"""Adaptive mastery engine (pass 11): per-student, per-objective mastery with explainable actions.

model.py    Bayesian Knowledge Tracing with weighted evidence (pure)
policy.py   decision rules: reviews, alternate explanations, test-out offers, overrides, Helix advisory (pure)
content.py  finds and assembles existing lesson content for a review (pure)
engine.py   evidence gathering from the LMS tables + decision log
models.py   mastery_setting, mastery_override, mastery_decision, mastery_check (additive tables)

Registered from app.py with ``mastery.register(app, db, deps)`` (dependency injection, like gradebook).
Never writes to a grade table, and Helix data never lowers an estimate or makes anything required.
"""
import csv
import json
import re
from io import StringIO
from types import SimpleNamespace

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import content as C
from . import model as M
from . import policy as P
from .engine import (DEMO_DOMAIN, REVIEW_ITEMS, TESTOUT_MAX, TESTOUT_PASS, TESTOUT_PER_OBJ, Engine, short_text)
from .models import define_models, utcnow
from curriculum_v2 import misconceptions as MCS

OBJ_RE = re.compile(r'^(IT|NO)-\d{1,2}\.\d{1,2}$')
TARGET_RE = re.compile(r'^((IT|NO)-\d{1,2}\.\d{1,2}|CH-\d{1,2})$')
STATUS_ORDER = ['review', 'developing', 'mastered', 'not_started', 'waived']
ACTION_LABEL = {
    'review': 'Review inserted', 'alt_review': 'Alternate explanation inserted', 'helix_offer': 'Optional review offered (Helix)',
    'testout_offer': 'Mastery check offered', 'stuck_flag': 'Flagged as stuck', 'review_completed': 'Review completed',
    'review_skipped': 'Review skipped', 'testout_passed': 'Mastery check passed', 'testout_failed': 'Mastery check not passed',
    'override_lock': 'Instructor: lock', 'override_unlock': 'Instructor: unlock', 'override_force_review': 'Instructor: force review',
    'override_waive': 'Instructor: waive', 'override_clear': 'Instructor: override cleared',
    'misconception': 'Mix-up correction inserted', 'struggle_offer': 'Inline help offered',
    'struggle_dismissed': 'Inline help dismissed', 'daily_done': 'Daily review done', 'plan_updated': 'Learning plan updated',
    'checkin_scheduled': 'Check-in scheduled', 'checkin_done': 'Check-in done',
}


def register(app, db, deps):
    m = define_models(db)
    d = SimpleNamespace(**deps)
    eng = Engine(db, d, m)

    # ------------------------------------------------------------------ helpers
    plan_pref_ref = {}

    def plan_pref(section_id, user_id):
        fn = plan_pref_ref.get('fn')
        return fn(section_id, user_id) if fn else None

    def enrolled_section(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role != 'student':
            abort(403)
        if not d.Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first():
            abort(404)
        return section

    def staff_section(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role == 'admin':
            return section
        if current_user.role != 'instructor' or not d.can_access_section(current_user, section):
            abort(403)
        return section

    def students_of(section):
        rows = (d.User.query.join(d.Enrollment, d.Enrollment.user_id == d.User.id)
                .filter(d.Enrollment.section_id == section.id, d.User.role == 'student')
                .order_by(d.User.last_name, d.User.first_name).all())
        return rows

    def reasons_of(row):
        try:
            return json.loads(row.reasons_json or '[]')
        except ValueError:
            return []

    def evidence_of(row):
        try:
            return json.loads(row.evidence_json or '{}')
        except ValueError:
            return {}

    def obj_or_404(cmap, obj):
        if not OBJ_RE.match(obj or '') or obj not in cmap['objs']:
            abort(404)
        return cmap['objs'][obj]

    def lesson_url(section, les):
        return url_for('view_lesson', section_id=section.id, module_id=les['module_id'], lesson_id=les['id'])

    def continue_url(st):
        nl = st['next_lesson']
        return lesson_url(st['section'], nl) if nl else url_for('student_section', section_id=st['section'].id)

    @app.template_filter('mastery_reasons')
    def _reasons_filter(row):
        return reasons_of(row)

    @app.context_processor
    def _mastery_ctx():
        return {'mastery_status_label': M.STATUS_LABEL, 'mastery_action_label': ACTION_LABEL,
                'mastery_kind_label': M.KIND_LABEL, 'mastery_override_kinds': P.OVERRIDE_KINDS}

    # ------------------------------------------------------------------ API used by app.py
    def student_path(user, section):
        if not section or user.role != 'student':
            return None
        st = eng.student_state(section, user)
        return eng.path(st, url_for)

    def lesson_gate(user, section, module, lesson):
        """For a student opening a lesson: (action, review_url) to show before it, or (None, None)."""
        if not section or user.role != 'student':
            return None, None
        st = eng.student_state(section, user)
        a = eng.gate(st, module.order)
        if not a:
            return None, None
        mapped = (st['cmap']['obj_lesson'].get(a['obj']) or {}).get('lesson_id')
        # a required review blocks the lesson (redirect), except the very lesson the review is built from
        block = bool(a['required']) and lesson.id != mapped
        return (dict(a, text=st['cmap']['objs'][a['obj']]['text'], block=block),
                url_for('mastery_review', section_id=section.id, obj=a['obj']))

    # ------------------------------------------------------------------ student pages
    @login_required
    def mastery_student(section_id):
        section = enrolled_section(section_id)
        st = eng.student_state(section, current_user)
        cmap = st['cmap']
        chapters = []
        for ch in cmap['chapters']:
            rows = []
            for obj in cmap['chapter_objs'][ch]:
                r = st['decision']['rows'][obj]
                rows.append({'obj': obj, 'text': cmap['objs'][obj]['text'], 'est': st['states'][obj], 'row': r,
                             'evidence': M.describe_counts(st['states'][obj]), 'lesson': cmap['obj_lesson'].get(obj)})
            chapters.append({'chapter': ch, 'rows': rows, 'tested_out': st['testout_history'].get(ch, {}).get('passed')})
        log = (m.MasteryDecision.query.filter_by(section_id=section.id, user_id=current_user.id)
               .order_by(m.MasteryDecision.created_at.desc(), m.MasteryDecision.id.desc()).limit(25).all())
        return render_template('mastery/student.html', section=section, st=st, chapters=chapters, log=log,
                               path=eng.path(st, url_for), reasons_of=reasons_of, objs=cmap['objs'],
                               model_params=M.PARAMS, weights=M.WEIGHTS)

    def _open_check(section, user, kind, target, variant, items):
        c = (m.MasteryCheck.query.filter_by(section_id=section.id, user_id=user.id, kind=kind, target=target,
                                            completed_at=None, skipped=False)
             .order_by(m.MasteryCheck.started_at.desc()).first())
        if c and c.variant == variant:
            return c
        c = m.MasteryCheck(section_id=section.id, user_id=user.id, kind=kind, target=target, variant=variant,
                           items_json=json.dumps(items), total=len(items), started_at=utcnow())
        db.session.add(c)
        db.session.commit()
        return c

    def _grade(check, form):
        items = json.loads(check.items_json or '[]')
        answers, correct, per = {}, 0, []
        for i, it in enumerate(items):
            ans = form.get(f'q{i}')
            if ans is not None and ans not in it['options']:
                ans = None
            answers[str(i)] = ans
            ok = ans is not None and ans == it['correct']
            correct += 1 if ok else 0
            per.append({'obj': it['obj'], 'ok': ok, 'answered': ans is not None})
        return answers, correct, per

    @login_required
    def mastery_review(section_id, obj):
        section = enrolled_section(section_id)
        st = eng.student_state(section, current_user)
        cmap = st['cmap']
        o = obj_or_404(cmap, obj)
        row = st['decision']['rows'][obj]
        action = row['action']
        asked, mc = request.args.get('variant'), request.args.get('mc')
        if mc and (mc not in MCS.MISCONCEPTIONS or MCS.MISCONCEPTIONS[mc]['obj'] != obj):
            mc = None
        if asked in ('alt', 'review', 'practice'):
            variant, mc = asked, None                       # the student's explicit choice
        elif mc:
            variant = 'mc'
        elif action and action['type'] == 'misconception':
            variant, mc = 'mc', action['mc']
        else:
            pref = plan_pref(section.id, current_user.id)
            variant = pref or ('alt' if action and action['type'] == 'alt_review' else 'review')
        required = bool(action and action['required'])
        if request.method == 'POST':
            check = db.session.get(m.MasteryCheck, request.form.get('check_id', type=int) or 0)
            if (not check or check.user_id != current_user.id or check.section_id != section.id or check.kind != 'review'
                    or check.target != obj or check.completed_at):
                flash('That review was already finished or has expired. Here is a fresh one.', 'info')
                return redirect(url_for('mastery_review', section_id=section.id, obj=obj), code=303)
            before = st['states'][obj]
            answers, correct, _per = _grade(check, request.form)
            check.answers_json, check.correct, check.completed_at = json.dumps(answers), correct, utcnow()
            for r in m.MasteryDecision.query.filter_by(section_id=section.id, user_id=current_user.id, target=obj,
                                                       status='active').all():
                if r.action in ('review', 'alt_review', 'misconception', 'helix_offer'):
                    r.status, r.resolved_at = 'done', utcnow()
            eng.log(section.id, current_user.id, obj, 'review_completed', 'student',
                    [f'You finished the {"alternate explanation" if check.variant == "alt" else "review"} and answered '
                     f'{correct} of {check.total} check questions.'], before, actor_id=current_user.id, status='logged')
            db.session.commit()
            return redirect(url_for('mastery_review_done', section_id=section.id, obj=obj, check_id=check.id), code=303)
        info = cmap['obj_lesson'].get(obj)
        les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
        chapter_lessons = cmap['by_ch'].get(o['chapter'], [])
        mcinfo = None
        if variant == 'mc':
            mcinfo = dict(MCS.MISCONCEPTIONS[mc], id=mc, seen=(st['misconceptions'].get(mc) or {}).get('hits', 0))
            review = C.build_correction(obj, o['text'], mcinfo, les, chapter_lessons=chapter_lessons,
                                        glossary=d.glossary, marked=d.glossary_marked)
        elif variant == 'practice':
            review = {'obj': obj, 'variant': 'practice', 'blocks': [], 'glossary': [], 'lesson': les}
        else:
            review = C.build_review(obj, o['text'], les, variant=variant, chapter_lessons=chapter_lessons,
                                    glossary=d.glossary, marked=d.glossary_marked)
        prefer = {b for (b, _d), m in MCS.TAGS.items() if m == mc} if mc else None
        n_items = 5 if variant == 'practice' else REVIEW_ITEMS
        items = eng.pick_items(cmap, [obj], n_items, n_items, st['checks'], st['settings']['testout_bank'], prefer=prefer)
        check = _open_check(section, current_user, 'review', obj, variant if not mc else f'mc:{mc}', items)
        reasons = action['reasons'] if action and (variant != 'mc' or action.get('mc') == mc) else [
            'You opened this review yourself. It is optional.', P.evidence_reason(st['states'][obj], M.describe_counts)]
        mc_opts = [dict(MCS.MISCONCEPTIONS[k], id=k, hits=v['hits']) for k, v in st['misconceptions'].items()
                   if v['obj'] == obj and v['active']]
        return render_template('mastery/review.html', section=section, obj=obj, o=o, review=review, check=check,
                               mcinfo=mcinfo, mc_opts=mc_opts,
                               items=json.loads(check.items_json or '[]'), action=action, required=required,
                               reasons=reasons, est=st['states'][obj], lesson=les, map_info=info, st=st,
                               lesson_link=lesson_url(section, les) if les else None, variant=variant,
                               evidence=M.describe_counts(st['states'][obj]))

    @login_required
    def mastery_review_skip(section_id, obj):
        section = enrolled_section(section_id)
        st = eng.student_state(section, current_user, log=False)
        obj_or_404(st['cmap'], obj)
        action = st['decision']['rows'][obj]['action']
        if action and action['required']:
            flash('Your instructor made this review required, so it cannot be skipped. It takes about five minutes.', 'warning')
            return redirect(url_for('mastery_review', section_id=section.id, obj=obj), code=303)
        for r in m.MasteryDecision.query.filter_by(section_id=section.id, user_id=current_user.id, target=obj,
                                                   status='active').all():
            if r.action in ('review', 'alt_review', 'misconception', 'helix_offer'):
                r.status, r.resolved_at = 'skipped', utcnow()
        eng.log(section.id, current_user.id, obj, 'review_skipped', 'student',
                ['You chose “Skip for now”. The review comes back only if new answers suggest it would help.'],
                st['states'][obj], actor_id=current_user.id)
        db.session.commit()
        flash('Review skipped for now. You can open it any time from “My mastery”.', 'info')
        return redirect(continue_url(st), code=303)

    @login_required
    def mastery_review_done(section_id, obj, check_id):
        section = enrolled_section(section_id)
        check = db.get_or_404(m.MasteryCheck, check_id)
        if check.user_id != current_user.id or check.section_id != section.id or check.target != obj or not check.completed_at:
            abort(404)
        st = eng.student_state(section, current_user)
        o = obj_or_404(st['cmap'], obj)
        items = json.loads(check.items_json or '[]')
        answers = json.loads(check.answers_json or '{}')
        per = [{'n': i + 1, 'text': it['text'], 'ok': answers.get(str(i)) == it['correct'],
                'answered': answers.get(str(i)) is not None} for i, it in enumerate(items)]
        return render_template('mastery/review_done.html', section=section, obj=obj, o=o, check=check, per=per,
                               est=st['states'][obj], row=st['decision']['rows'][obj],
                               path=eng.path(st, url_for), continue_url=continue_url(st))

    def _testout_allowed(st, chapter):
        if chapter not in st['cmap']['chapter_objs']:
            return None
        rows = list(st['decision']['rows'].values())
        return P.testout_offer(chapter, rows=rows, settings=st['settings'], overrides=st['overrides'],
                               testout_history=st['testout_history'])

    @login_required
    def mastery_testout(section_id, chapter):
        section = enrolled_section(section_id)
        st = eng.student_state(section, current_user)
        cmap = st['cmap']
        target = P.chapter_key(chapter)
        open_c = (m.MasteryCheck.query.filter_by(section_id=section.id, user_id=current_user.id, kind='testout',
                                                 target=target, completed_at=None).first())
        offer = _testout_allowed(st, chapter)
        if request.method == 'POST':
            check = db.session.get(m.MasteryCheck, request.form.get('check_id', type=int) or 0)
            if (not check or check.user_id != current_user.id or check.section_id != section.id or check.kind != 'testout'
                    or check.target != target or check.completed_at):
                flash('That mastery check was already submitted.', 'info')
                return redirect(url_for('mastery_student', section_id=section.id), code=303)
            answers, correct, per = _grade(check, request.form)
            by_obj = {}
            for p_ in per:
                b = by_obj.setdefault(p_['obj'], [0, 0])
                b[0] += 1 if p_['ok'] else 0
                b[1] += 1
            pct = 100.0 * correct / check.total if check.total else 0
            passed = pct >= TESTOUT_PASS and all(c >= 1 for c, _n in by_obj.values())
            check.answers_json, check.correct, check.passed, check.completed_at = json.dumps(answers), correct, passed, utcnow()
            reasons = [f'You answered {correct} of {check.total} questions right ({pct:.0f}%).',
                       f'Passing needs {TESTOUT_PASS}% and at least one right answer on every objective in the chapter.']
            eng.log(section.id, current_user.id, target, 'testout_passed' if passed else 'testout_failed', 'student',
                    reasons, None, actor_id=current_user.id)
            for r in m.MasteryDecision.query.filter_by(section_id=section.id, user_id=current_user.id, target=target,
                                                       action='testout_offer', status='active').all():
                r.status, r.resolved_at = 'done', utcnow()
            db.session.commit()
            return redirect(url_for('mastery_testout_result', section_id=section.id, chapter=chapter, check_id=check.id), code=303)
        if not offer and not open_c:
            flash('The mastery check for that chapter is not open for you right now.', 'info')
            return redirect(url_for('mastery_student', section_id=section.id))
        if open_c:
            check = open_c
        else:
            items = eng.pick_items(cmap, cmap['chapter_objs'][chapter], TESTOUT_PER_OBJ, TESTOUT_MAX, st['checks'],
                                   st['settings']['testout_bank'])
            if not items:
                flash('There are no check questions for that chapter yet.', 'info')
                return redirect(url_for('mastery_student', section_id=section.id))
            check = _open_check(section, current_user, 'testout', target, 'review', items)
        mod = next((les for les in cmap['lessons'] if les['chapter'] == chapter), None)
        return render_template('mastery/testout.html', section=section, chapter=chapter, check=check,
                               items=json.loads(check.items_json or '[]'), offer=offer, objs=cmap['objs'],
                               chapter_objs=cmap['chapter_objs'][chapter], pass_pct=TESTOUT_PASS, first_lesson=mod)

    @login_required
    def mastery_testout_result(section_id, chapter, check_id):
        section = enrolled_section(section_id)
        check = db.get_or_404(m.MasteryCheck, check_id)
        if (check.user_id != current_user.id or check.section_id != section.id or check.target != P.chapter_key(chapter)
                or not check.completed_at):
            abort(404)
        st = eng.student_state(section, current_user)
        items = json.loads(check.items_json or '[]')
        answers = json.loads(check.answers_json or '{}')
        by_obj = {}
        for i, it in enumerate(items):
            b = by_obj.setdefault(it['obj'], {'obj': it['obj'], 'text': st['cmap']['objs'][it['obj']]['text'], 'ok': 0, 'n': 0})
            b['n'] += 1
            b['ok'] += 1 if answers.get(str(i)) == it['correct'] else 0
        return render_template('mastery/testout_result.html', section=section, chapter=chapter, check=check,
                               rows=list(by_obj.values()), pass_pct=TESTOUT_PASS, path=eng.path(st, url_for),
                               continue_url=continue_url(st))

    # ------------------------------------------------------------------ instructor pages
    def class_rows(section):
        cmap = eng.course_map(section)
        out = []
        for u in students_of(section):
            st = eng.student_state(section, u, cmap=cmap)
            out.append({'user': u, 'st': st})
        return cmap, out

    @login_required
    def mastery_class(section_id):
        section = staff_section(section_id)
        cmap, rows = class_rows(section)
        ch = request.args.get('ch', 'all')
        chapters = cmap['chapters']
        if ch != 'all':
            try:
                ch = int(ch)
            except ValueError:
                ch = 'all'
            if ch not in chapters:
                ch = 'all'
        cols = [o for o in cmap['objs'] if ch == 'all' or cmap['objs'][o]['chapter'] == ch]
        stuck, need = [], []
        counts = {k: 0 for k in STATUS_ORDER}
        active_reviews = 0
        for r in rows:
            dec = r['st']['decision']
            for obj, row in dec['rows'].items():
                counts[row['state']] = counts.get(row['state'], 0) + 1
                if row['stuck']:
                    stuck.append({'user': r['user'], 'obj': obj, 'row': row, 'est': r['st']['states'][obj],
                                  'why': M.describe_counts(r['st']['states'][obj]), 'kind': 'stuck'})
            for a in dec['actions']:
                if a['type'] in ('review', 'alt_review', 'misconception'):
                    active_reviews += 1
                    need.append({'user': r['user'], 'obj': a['obj'], 'action': a, 'est': r['st']['states'][a['obj']],
                                 'why': M.describe_counts(r['st']['states'][a['obj']])})
        need.sort(key=lambda x: x['est']['p'])
        passed_to = sum(1 for r in rows for t in r['st']['testout_history'].values() if t.get('passed'))
        log = (db.session.query(m.MasteryDecision, d.User).join(d.User, d.User.id == m.MasteryDecision.user_id)
               .filter(m.MasteryDecision.section_id == section.id)
               .order_by(m.MasteryDecision.created_at.desc(), m.MasteryDecision.id.desc()).limit(30).all())
        settings = eng.settings(section.id)
        demo = any(r['st']['demo'] for r in rows)
        helix_n = sum(1 for r in rows if r['st']['helix_status'] == 'ok')
        return render_template('mastery/instructor.html', section=section, cmap=cmap, rows=rows, cols=cols, ch=ch,
                               chapters=chapters, stuck=stuck, need=need[:15], need_total=len(need), counts=counts,
                               active_reviews=active_reviews, passed_to=passed_to, log=log, settings=settings,
                               demo=demo, helix_n=helix_n, reasons_of=reasons_of, model_params=M.PARAMS,
                               weights=M.WEIGHTS, thresholds={'mastered': M.MASTERED, 'low': M.LOW,
                                                              'min_evidence': M.MIN_EVIDENCE})

    @login_required
    def mastery_class_student(section_id, user_id):
        section = staff_section(section_id)
        u = db.get_or_404(d.User, user_id)
        if not d.Enrollment.query.filter_by(section_id=section.id, user_id=u.id).first() or u.role != 'student':
            abort(404)
        st = eng.student_state(section, u)
        cmap = st['cmap']
        rows = []
        for obj, o in cmap['objs'].items():
            est = st['states'][obj]
            reading = [t for t in est['trace'] if t['kind'] == 'reading']
            rows.append({'obj': obj, 'o': o, 'est': est, 'row': st['decision']['rows'][obj], 'lesson': cmap['obj_lesson'].get(obj),
                         'helix': (st['helix'] or {}).get(obj), 'reading_n': len(reading),
                         'evidence': M.describe_counts(est)})
        log = (m.MasteryDecision.query.filter_by(section_id=section.id, user_id=u.id)
               .order_by(m.MasteryDecision.created_at.desc(), m.MasteryDecision.id.desc()).limit(60).all())
        ovs = (m.MasteryOverride.query.filter_by(section_id=section.id, user_id=u.id)
               .order_by(m.MasteryOverride.created_at.desc()).limit(40).all())
        return render_template('mastery/instructor_student.html', section=section, u=u, st=st, rows=rows, log=log,
                               overrides=ovs, reasons_of=reasons_of, evidence_of=evidence_of, chapters=cmap['chapters'])

    @login_required
    def mastery_override(section_id):
        section = staff_section(section_id)
        cmap = eng.course_map(section)
        uid = request.form.get('user_id', type=int)
        target = (request.form.get('target') or '').strip()
        kind = (request.form.get('kind') or '').strip()
        note = (request.form.get('note') or '').strip()[:300]
        back = request.form.get('next') or ''
        if not back.startswith(f'/instructor/section/{section.id}/mastery'):
            back = url_for('mastery_class', section_id=section.id)
        u = db.session.get(d.User, uid or 0)
        valid_target = TARGET_RE.match(target) and (target in cmap['objs'] or
                                                     (target.startswith('CH-') and int(target[3:]) in cmap['chapters']))
        if (not u or u.role != 'student' or not d.Enrollment.query.filter_by(section_id=section.id, user_id=u.id).first()
                or not valid_target or kind not in list(P.OVERRIDE_KINDS) + ['clear']):
            flash('That override could not be saved: check the student, objective and action.', 'danger')
            return redirect(back, code=303)
        if not note:
            flash('Add a short note so the student and other instructors know why.', 'warning')
            return redirect(back, code=303)
        now = utcnow()
        for o in m.MasteryOverride.query.filter_by(section_id=section.id, user_id=u.id, target=target, active=True).all():
            o.active, o.cleared_at, o.cleared_by = False, now, current_user.id
        if kind != 'clear':
            db.session.add(m.MasteryOverride(section_id=section.id, user_id=u.id, target=target, kind=kind, note=note,
                                             created_by=current_user.id, created_at=now))
        label = P.OVERRIDE_KINDS.get(kind, 'Clear override')
        eng.log(section.id, u.id, target, f'override_{kind}', 'instructor',
                [f'Your instructor set “{label}” on {target}.', f'Note: {note}'], actor_id=current_user.id)
        db.session.commit()
        d.audit('mastery_override', f'section={section.id} user={u.id} target={target} kind={kind}')
        flash(f'Saved: {label} for {u.full_name} on {target}.', 'success')
        return redirect(back, code=303)

    @login_required
    def mastery_settings(section_id):
        section = staff_section(section_id)
        s = m.MasterySetting.query.filter_by(section_id=section.id).first()
        if not s:
            s = m.MasterySetting(section_id=section.id)
            db.session.add(s)
        s.enabled = request.form.get('enabled') == '1'
        s.testout = request.form.get('testout') == '1'
        s.testout_bank = request.form.get('testout_bank') == '1'
        s.updated_at, s.updated_by = utcnow(), current_user.id
        db.session.commit()
        d.audit('mastery_settings', f'section={section.id} enabled={s.enabled} testout={s.testout} bank={s.testout_bank}')
        flash('Adaptivity ' + ('on' if s.enabled else 'off') + ' for this class.', 'success')
        return redirect(url_for('mastery_class', section_id=section.id), code=303)

    @login_required
    def mastery_csv(section_id):
        section = staff_section(section_id)
        cmap, rows = class_rows(section)
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(['student', 'email', 'objective', 'chapter', 'estimate_pct', 'confidence', 'status', 'questions',
                    'right', 'evidence_weight', 'override', 'action', 'stuck', 'demo_account'])
        for r in rows:
            st = r['st']
            for obj, row in st['decision']['rows'].items():
                est = st['states'][obj]
                w.writerow([r['user'].full_name, r['user'].email, obj, cmap['objs'][obj]['chapter'], est['pct'],
                            est['confidence'], row['state'], est['n_items'], est['n_correct'], est['n_eff'],
                            row['override'] or '', (row['action'] or {}).get('type', ''), int(row['stuck']),
                            int((r['user'].email or '').endswith(DEMO_DOMAIN))])
        d.audit('mastery_export', f'section={section.id}')
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename=mastery-section-{section.id}.csv'})

    from . import lab_diagnosis
    from .features import register_features
    feats = register_features(app, db, SimpleNamespace(
        eng=eng, m=m, d=d, enrolled_section=enrolled_section, staff_section=staff_section, grade=_grade,
        open_check=_open_check, class_rows=class_rows, diagnose=lab_diagnosis.diagnose))
    plan_pref_ref['fn'] = feats['plan_pref']

    for rule, ep, fn, methods in [
        ('/student/section/<int:section_id>/mastery', 'mastery_student', mastery_student, ['GET']),
        ('/student/section/<int:section_id>/review/<obj>', 'mastery_review', mastery_review, ['GET', 'POST']),
        ('/student/section/<int:section_id>/review/<obj>/skip', 'mastery_review_skip', mastery_review_skip, ['POST']),
        ('/student/section/<int:section_id>/review/<obj>/done/<int:check_id>', 'mastery_review_done', mastery_review_done, ['GET']),
        ('/student/section/<int:section_id>/testout/<int:chapter>', 'mastery_testout', mastery_testout, ['GET', 'POST']),
        ('/student/section/<int:section_id>/testout/<int:chapter>/result/<int:check_id>', 'mastery_testout_result', mastery_testout_result, ['GET']),
        ('/instructor/section/<int:section_id>/mastery', 'mastery_class', mastery_class, ['GET']),
        ('/instructor/section/<int:section_id>/mastery/student/<int:user_id>', 'mastery_class_student', mastery_class_student, ['GET']),
        ('/instructor/section/<int:section_id>/mastery/override', 'mastery_override', mastery_override, ['POST']),
        ('/instructor/section/<int:section_id>/mastery/settings', 'mastery_settings', mastery_settings, ['POST']),
        ('/instructor/section/<int:section_id>/mastery.csv', 'mastery_csv', mastery_csv, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)
    api = SimpleNamespace(engine=eng, models=m, student_path=student_path, lesson_gate=lesson_gate,
                          daily_summary=feats['daily_summary'], lesson_quickcheck=feats['lesson_quickcheck'],
                          features=feats, diagnose=lab_diagnosis.diagnose)
    app.extensions['ciwt_mastery'] = api
    return api
