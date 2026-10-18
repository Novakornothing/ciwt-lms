"""Pass 11 extensions on the mastery engine: daily spaced review, in-the-moment struggle help, the student's own
learning plan and the instructor's 'Who needs me' list. Registered from mastery.register()."""
import json
import math
from datetime import date, datetime, timedelta

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from curriculum_v2 import misconceptions as MCS

from . import content as C
from . import memory as MEM
from . import model as M
from .engine import DAILY_MAX, DAILY_MIN, SRC_RANK, short_text
from .models import utcnow

STRUGGLE_DWELL_MS = 45_000      # without Helix: 45 s on the section, then a miss, counts as struggling
SECONDS_PER_QUESTION = 30        # used for the honest "about N minutes" on the daily review
INACTIVE_DAYS = 7
REVIEW_OVERDUE_DAYS = 3
DROP_POINTS = 20                 # estimate fell by 20+ points in 7 days into "needs review"
REASON_ORDER = ['stuck', 'misconception', 'missed_review', 'drop', 'lab', 'inactive']


def register_features(app, db, ctx):
    eng, m, d = ctx.eng, ctx.m, ctx.d

    # ------------------------------------------------------------------ shared helpers
    def plan_row(section_id, user_id, create=False):
        p = m.LearningPlan.query.filter_by(section_id=section_id, user_id=user_id).first()
        if not p and create:
            p = m.LearningPlan(section_id=section_id, user_id=user_id)
            db.session.add(p)
        return p

    def today_key(now=None):
        return 'DAY-' + (now or utcnow()).date().isoformat()

    def eligible_objs(st):
        return {o for o, r in st['decision']['rows'].items() if r['state'] != 'waived'}

    def daily_plan(st, size=None):
        now = utcnow()
        size = max(DAILY_MIN, min(DAILY_MAX, size or DAILY_MAX))
        q = MEM.queue(st['memory'], now, minimum=DAILY_MIN, maximum=size, eligible=eligible_objs(st))
        items = []
        used = eng._answered(st['checks'])
        for obj, state, why in q:
            pool = eng.pool(st['cmap'], obj, st['settings']['testout_bank'], st['settings']['cert_items'])
            if not pool:
                continue
            pool.sort(key=lambda it: (used.get(it['bank_id'], 0), SRC_RANK.get(it['src'], 3), it['bank_id'] or ''))
            r = MEM.recall(state, now)
            it = dict(pool[0], why=why, recall=r, interval=state['interval'])
            items.append(it)
        return items

    def daily_summary(user, section):
        if not section or user.role != 'student':
            return None
        st = eng.student_state(section, user, log=False)
        done = (m.MasteryCheck.query.filter_by(section_id=section.id, user_id=user.id, kind='daily', target=today_key())
                .filter(m.MasteryCheck.completed_at.isnot(None)).first())
        pl = plan_row(section.id, user.id)
        items = [] if done else daily_plan(st, pl.daily_size if pl else None)
        due = sum(1 for it in items if it['why'] == 'due')
        upcoming = sorted([s['due'] for s in st['memory'].values() if s and s['due'] > utcnow()])
        return {'n': len(items), 'due': due, 'minutes': max(1, math.ceil(len(items) * SECONDS_PER_QUESTION / 60)),
                'done_today': bool(done), 'done': done, 'section': section,
                'url': url_for('mastery_daily', section_id=section.id),
                'next_due': upcoming[0] if upcoming else None,
                'learned': sum(1 for s in st['memory'].values() if s)}

    # ------------------------------------------------------------------ 2. daily spaced review
    @login_required
    def mastery_daily(section_id):
        section = ctx.enrolled_section(section_id)
        st = eng.student_state(section, current_user, log=False)
        key = today_key()
        done = (m.MasteryCheck.query.filter_by(section_id=section.id, user_id=current_user.id, kind='daily', target=key)
                .filter(m.MasteryCheck.completed_at.isnot(None)).order_by(m.MasteryCheck.completed_at.desc()).first())
        if request.method == 'POST':
            check = db.session.get(m.MasteryCheck, request.form.get('check_id', type=int) or 0)
            if (not check or check.user_id != current_user.id or check.section_id != section.id or check.kind != 'daily'
                    or check.completed_at):
                flash('That daily review was already submitted.', 'info')
                return redirect(url_for('mastery_daily', section_id=section.id), code=303)
            answers, correct, _per = ctx.grade(check, request.form)
            check.answers_json, check.correct, check.completed_at = json.dumps(answers), correct, utcnow()
            eng.log(section.id, current_user.id, key, 'daily_done', 'student',
                    [f'You answered {correct} of {check.total} daily review questions.',
                     'Each answer updates when that objective comes back (SM-2 schedule).'], actor_id=current_user.id)
            db.session.commit()
            return redirect(url_for('mastery_daily_result', section_id=section.id, check_id=check.id), code=303)
        if done:
            return redirect(url_for('mastery_daily_result', section_id=section.id, check_id=done.id))
        pl = plan_row(section.id, current_user.id)
        items = daily_plan(st, pl.daily_size if pl else None)
        check = None
        if items:
            open_c = (m.MasteryCheck.query.filter_by(section_id=section.id, user_id=current_user.id, kind='daily',
                                                     target=key, completed_at=None).first())
            check = open_c or ctx.open_check(section, current_user, 'daily', key, 'daily', [
                {k: it[k] for k in ('bank_id', 'obj', 'src', 'text', 'options', 'correct')} for it in items])
            served = json.loads(check.items_json or '[]')
            why = {it['obj']: it for it in items}
            items = [dict(it, why=why.get(it['obj'], {}).get('why', 'due'), recall=why.get(it['obj'], {}).get('recall'))
                     for it in served]
        return render_template('mastery/daily.html', section=section, items=items, check=check,
                               minutes=max(1, math.ceil(len(items) * SECONDS_PER_QUESTION / 60)),
                               objs=st['cmap']['objs'], learned=sum(1 for s in st['memory'].values() if s))

    @login_required
    def mastery_daily_result(section_id, check_id):
        section = ctx.enrolled_section(section_id)
        check = db.get_or_404(m.MasteryCheck, check_id)
        if check.user_id != current_user.id or check.section_id != section.id or check.kind != 'daily' or not check.completed_at:
            abort(404)
        st = eng.student_state(section, current_user, log=False)
        items = json.loads(check.items_json or '[]')
        answers = json.loads(check.answers_json or '{}')
        rows = []
        for i, it in enumerate(items):
            s = st['memory'].get(it['obj'])
            rows.append({'n': i + 1, 'obj': it['obj'], 'text': st['cmap']['objs'][it['obj']]['text'],
                         'ok': answers.get(str(i)) == it['correct'], 'answered': answers.get(str(i)) is not None,
                         'next': s['due'] if s else None, 'interval': s['interval'] if s else None})
        return render_template('mastery/daily_result.html', section=section, check=check, rows=rows,
                               path=eng.path(st, url_for))

    # ------------------------------------------------------------------ 3. in-the-moment struggle help
    def lesson_quickcheck(user, section, lesson):
        """Up to two quick-check questions for the objectives this lesson teaches (keys stay on the server)."""
        if not section or user.role != 'student':
            return []
        cmap = eng.course_map(section)
        out = []
        checks = eng.checks(section.id, user.id)
        settings = eng.settings(section.id)
        for obj in (cmap['lesson_objs'].get(lesson.id) or [])[:2]:
            items = eng.pick_items(cmap, [obj], 1, 1, checks, settings['testout_bank'], include_cert=settings['cert_items'])
            if not items:
                continue
            c = ctx.open_check(section, user, 'inline', obj, 'inline', items)
            it = json.loads(c.items_json or '[]')[0]
            heads = cmap['obj_sections'].get(obj) or []
            out.append({'check_id': c.id, 'obj': obj, 'text': it['text'], 'options': it['options'],
                        'heading': heads[0] if heads else '', 'url': url_for('mastery_quickcheck', section_id=section.id, check_id=c.id)})
        return out

    def struggle_offer(st, obj, heading, dwell_ms, mc):
        """Decide whether a miss right now should come with an inline alternate explanation."""
        cmap = st['cmap']
        reasons, source = [], None
        hx = (st['helix'] or {}).get(obj) if st['helix_status'] == 'ok' else None
        if hx and hx.get('reread') and (not heading or heading in hx['reread']):
            source = 'helix'
            reasons.append(f'Helix (with your consent) saw you go back to “{(heading or hx["reread"][0])}” several times, '
                           'and then this answer was not right.')
        elif dwell_ms >= STRUGGLE_DWELL_MS:
            source = 'time'
            reasons.append(f'You spent about {round(dwell_ms / 1000)} seconds on “{heading or "this section"}” and this answer '
                           'was not right, so a different explanation may help more than re-reading.')
        if mc:
            reasons.append(f'The answer you picked often means this mix-up: {MCS.MISCONCEPTIONS[mc]["label"]}.')
            source = source or 'answer'
        if not source:
            return None
        reasons.append('This is only an offer. Dismiss it if you prefer; nothing is recorded against you.')
        o = cmap['objs'][obj]
        info = cmap['obj_lesson'].get(obj)
        les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
        if mc:
            content = C.build_correction(obj, o['text'], MCS.MISCONCEPTIONS[mc], les,
                                         chapter_lessons=cmap['by_ch'].get(o['chapter'], []), glossary=d.glossary,
                                         marked=d.glossary_marked)
        else:
            content = C.build_review(obj, o['text'], les, variant='alt', chapter_lessons=cmap['by_ch'].get(o['chapter'], []),
                                     glossary=d.glossary, marked=d.glossary_marked)
        content['blocks'] = [b for b in content['blocks'] if b['label'] != heading][:2] or content['blocks'][:1]
        return {'source': source, 'reasons': reasons, 'content': content, 'mc': mc,
                'mc_label': MCS.MISCONCEPTIONS[mc]['label'] if mc else None,
                'review_url': url_for('mastery_review', section_id=st['section'].id, obj=obj, **({'mc': mc} if mc else {'variant': 'alt'}))}

    @login_required
    def mastery_quickcheck(section_id, check_id):
        section = ctx.enrolled_section(section_id)
        check = db.get_or_404(m.MasteryCheck, check_id)
        if check.user_id != current_user.id or check.section_id != section.id or check.kind != 'inline':
            abort(404)
        wants_json = request.is_json or 'application/json' in (request.headers.get('Accept') or '')
        data = request.get_json(silent=True) if request.is_json else request.form
        data = data or {}
        if check.completed_at:
            msg = 'You already answered this one.'
            return jsonify({'ok': False, 'html': f'<p class="mb-0">{msg}</p>'}) if wants_json else redirect(request.referrer or url_for('student_section', section_id=section.id))
        item = json.loads(check.items_json or '[]')[0]
        ans = data.get('answer')
        if ans not in item['options']:
            return (jsonify({'ok': False, 'html': '<p class="mb-0">Choose one of the answers first.</p>'}), 400) if wants_json \
                else redirect(request.referrer or url_for('student_section', section_id=section.id))
        try:
            dwell = max(0, min(int(data.get('dwell_ms') or 0), 3_600_000))
        except (TypeError, ValueError):
            dwell = 0
        heading = (data.get('heading') or '')[:200]
        ok = ans == item['correct']
        check.answers_json, check.correct, check.completed_at = json.dumps({'0': ans}), int(ok), utcnow()
        db.session.commit()
        st = eng.student_state(section, current_user, log=False)
        mc = MCS.tag_for(item, ans)
        offer = None if ok else struggle_offer(st, item['obj'], heading, dwell, mc)
        if offer:
            eng.log(section.id, current_user.id, item['obj'], 'struggle_offer', offer['source'] if offer['source'] != 'time' else 'engine',
                    offer['reasons'], st['states'][item['obj']], actor_id=None)
            db.session.commit()
        html = render_template('mastery/_struggle.html', ok=ok, offer=offer, check=check, section=section, obj=item['obj'],
                               heading=heading)
        if wants_json:
            return jsonify({'ok': True, 'correct': ok, 'offer': bool(offer), 'html': html})
        flash('Right.' if ok else 'Not quite. Open “Explain it another way” below the question for help.', 'info')
        return redirect(request.referrer or url_for('student_section', section_id=section.id))

    @login_required
    def mastery_quickcheck_dismiss(section_id, check_id):
        section = ctx.enrolled_section(section_id)
        check = db.get_or_404(m.MasteryCheck, check_id)
        if check.user_id != current_user.id or check.section_id != section.id or check.kind != 'inline':
            abort(404)
        eng.log(section.id, current_user.id, check.target, 'struggle_dismissed', 'student',
                ['You dismissed the alternate explanation. That is fine; nothing changes.'], actor_id=current_user.id)
        db.session.commit()
        return jsonify({'ok': True}) if request.is_json else redirect(request.referrer or url_for('student_section', section_id=section.id))

    # ------------------------------------------------------------------ 6. student-owned learning plan
    def build_plan(st, pl, today=None):
        today = today or utcnow().date()
        cmap = st['cmap']
        rows = st['decision']['rows']
        objs = [o for o in cmap['objs'] if rows[o]['state'] != 'waived']
        mastered = [o for o in objs if rows[o]['state'] == 'mastered']
        remaining = [o for o in objs if rows[o]['state'] != 'mastered']
        week_start = today - timedelta(days=today.weekday())
        two_weeks = datetime.combine(today - timedelta(days=14), datetime.min.time())
        recent = [o for o in mastered if (st['states'][o]['last_when'] or datetime.min) >= two_weeks]
        this_week = [o for o in mastered if (st['states'][o]['last_when'] or datetime.min) >= datetime.combine(week_start, datetime.min.time())]
        out = {'total': len(objs), 'mastered': len(mastered), 'remaining': remaining, 'recent': len(recent),
               'this_week': len(this_week), 'weeks': [], 'exam_date': pl.exam_date if pl else None, 'days_left': None,
               'per_week': None, 'status': None}
        if pl and pl.exam_date:
            days_left = (pl.exam_date - today).days
            out['days_left'] = days_left
            if days_left > 0:
                n_weeks = max(1, math.ceil(days_left / 7))
                per_week = math.ceil(len(remaining) / n_weeks) if remaining else 0
                out['per_week'] = per_week
                due_by_week = {}
                for s in st['memory'].values():
                    if s:
                        w = max(0, (s['due'].date() - today).days // 7)
                        due_by_week[w] = due_by_week.get(w, 0) + 1
                for w in range(n_weeks):
                    start = today + timedelta(days=7 * w)
                    targets = remaining[w * per_week:(w + 1) * per_week] if per_week else []
                    out['weeks'].append({'n': w + 1, 'start': start, 'end': min(pl.exam_date, start + timedelta(days=6)),
                                         'targets': targets, 'review_due': due_by_week.get(w, 0)})
                out['status'] = ('ahead' if out['this_week'] >= per_week and per_week else
                                 'on' if out['recent'] >= 2 * per_week else 'behind') if per_week else 'done'
        return out

    def plan_pref(section_id, user_id):
        p = plan_row(section_id, user_id)
        return p.review_pref if p and p.review_pref in ('review', 'alt', 'practice') else None

    @login_required
    def mastery_plan(section_id):
        section = ctx.enrolled_section(section_id)
        pl = plan_row(section.id, current_user.id)
        if request.method == 'POST':
            pl = plan_row(section.id, current_user.id, create=True)
            raw = (request.form.get('exam_date') or '').strip()
            if raw:
                try:
                    dt = date.fromisoformat(raw)
                except ValueError:
                    dt = None
                today = utcnow().date()
                if not dt or dt <= today or dt > today + timedelta(days=730):
                    flash('Pick an exam date after today and within two years.', 'warning')
                    return redirect(url_for('mastery_plan', section_id=section.id), code=303)
                pl.exam_date = dt
            elif request.form.get('clear_date') == '1':
                pl.exam_date = None
            pref = request.form.get('review_pref', '')
            pl.review_pref = pref if pref in ('', 'review', 'alt', 'practice') else ''
            size = request.form.get('daily_size', type=int) or 8
            pl.daily_size = max(DAILY_MIN, min(DAILY_MAX, size))
            pl.updated_at = utcnow()
            eng.log(section.id, current_user.id, 'PLAN', 'plan_updated', 'student',
                    [f'You set your plan: exam date {pl.exam_date.isoformat() if pl.exam_date else "none"}, '
                     f'review style {pl.review_pref or "engine picks"}, {pl.daily_size} daily questions.'], actor_id=current_user.id)
            db.session.commit()
            flash('Plan saved.', 'success')
            return redirect(url_for('mastery_plan', section_id=section.id), code=303)
        st = eng.student_state(section, current_user)
        plan = build_plan(st, pl)
        cmap = st['cmap']
        chapters = [{'chapter': ch, 'rows': [{'obj': o, 'text': cmap['objs'][o]['text'], 'row': st['decision']['rows'][o],
                                               'est': st['states'][o]} for o in cmap['chapter_objs'][ch]]}
                    for ch in cmap['chapters']]
        checkins = (m.MasteryCheckin.query.filter_by(section_id=section.id, user_id=current_user.id, done_at=None)
                    .filter(m.MasteryCheckin.on_date >= utcnow().date()).order_by(m.MasteryCheckin.on_date).all())
        return render_template('mastery/plan.html', section=section, st=st, plan=plan, pl=pl, chapters=chapters,
                               objs=cmap['objs'], daily=daily_summary(current_user, section), checkins=checkins,
                               min_date=(utcnow().date() + timedelta(days=1)).isoformat(),
                               max_date=(utcnow().date() + timedelta(days=730)).isoformat(),
                               daily_min=DAILY_MIN, daily_max=DAILY_MAX, short_text=short_text)

    # ------------------------------------------------------------------ 5. who needs me
    def last_activity(st, user):
        whens = [o.get('when') for obs in st['evidence'].values() for o in obs if o.get('when')]
        whens += [c.completed_at for c in st['checks'] if c.completed_at]
        t = (db.session.query(db.func.max(d.TimeLog.ended_at))
             .filter(d.TimeLog.user_id == user.id, d.TimeLog.kind == 'study').scalar())
        if t:
            whens.append(t)
        return max(whens) if whens else None

    def needs_me_reasons(st, user, now=None):
        now = now or utcnow()
        cmap = st['cmap']
        out = []
        for obj in st['decision']['stuck']:
            out.append({'kind': 'stuck', 'obj': obj, 'when': st['states'][obj]['last_when'],
                        'text': f'Still needs review on {obj} after two reviews: {short_text(cmap["objs"][obj]["text"], 60)}'})
        for mc, mm in st['misconceptions'].items():
            if mm['active'] and mm['hits'] >= 2:
                out.append({'kind': 'misconception', 'obj': mm['obj'], 'when': mm['last_hit'], 'mc': mc,
                            'text': f'Picked the same mix-up {mm["hits"]} times ({mm["obj"]}): {mm["label"]}'})
        week_ago = now - timedelta(days=7)
        for obj, est in st['states'].items():
            if st['decision']['rows'][obj]['state'] != 'review' or not est['trace']:
                continue
            before = [t for t in est['trace'] if t.get('when') and t['when'] < week_ago]
            if before:
                was = round(before[-1]['after'] * 100)
                if was - est['pct'] >= DROP_POINTS:
                    out.append({'kind': 'drop', 'obj': obj, 'when': est['last_when'],
                                'text': f'{obj} fell from {was}% to {est["pct"]}% in the last 7 days'})
        stale = (m.MasteryDecision.query.filter_by(section_id=st['section'].id, user_id=user.id, status='active')
                 .filter(m.MasteryDecision.action.in_(['review', 'alt_review', 'misconception']))
                 .filter(m.MasteryDecision.created_at < now - timedelta(days=REVIEW_OVERDUE_DAYS)).all())
        for r in stale:
            out.append({'kind': 'missed_review', 'obj': r.target, 'when': r.created_at,
                        'text': f'A review on {r.target} has waited {(now - r.created_at).days} days'
                                + (' (required)' if r.required else '')})
        skips = (m.MasteryDecision.query.filter_by(section_id=st['section'].id, user_id=user.id, action='review_skipped')
                 .filter(m.MasteryDecision.created_at >= now - timedelta(days=14)).count())
        if skips >= 2:
            out.append({'kind': 'missed_review', 'obj': None, 'when': now, 'text': f'Skipped {skips} reviews in the last 14 days'})
        lab_events = getattr(d, 'lab_events', None)
        diagnose = getattr(ctx, 'diagnose', None)
        if lab_events and diagnose:
            for r in ctx.lab_diagnoses(user, st['section']):
                if r['struggling']:
                    out.append({'kind': 'lab', 'obj': None, 'when': r['last_at'], 'lab': r,
                                'text': f"Lab “{r['title']}” (attempt {r['attempt']}): "
                                        + ', '.join(p['label'].lower() for p in r['concerns'])})
        last = last_activity(st, user)
        if not last:
            out.append({'kind': 'inactive', 'obj': None, 'when': None, 'text': 'No recorded activity in this class yet'})
        elif last < now - timedelta(days=INACTIVE_DAYS):
            out.append({'kind': 'inactive', 'obj': None, 'when': last, 'text': f'No activity for {(now - last).days} days'})
        out.sort(key=lambda r: REASON_ORDER.index(r['kind']))
        return out, last

    def needs_me(section):
        cmap, rows = ctx.class_rows(section)
        out = []
        for r in rows:
            reasons, last = needs_me_reasons(r['st'], r['user'])
            if not reasons:
                continue
            top_obj = next((x['obj'] for x in reasons if x.get('obj') and x['obj'] in cmap['objs']), None)
            out.append({'user': r['user'], 'reasons': reasons, 'last': last, 'top_obj': top_obj, 'st': r['st'],
                        'kinds': sorted({x['kind'] for x in reasons}, key=REASON_ORDER.index)})
        # ranked by how many different kinds of reason apply, then the most serious kind, then most recent activity
        out.sort(key=lambda x: (-len(x['kinds']), REASON_ORDER.index(x['kinds'][0]),
                                -(x['last'] or datetime.min).timestamp() if x['last'] else 0))
        return cmap, rows, out

    @login_required
    def mastery_today(section_id):
        section = ctx.staff_section(section_id)
        cmap, rows, people = needs_me(section)
        only_inactive = [p for p in people if p['kinds'] == ['inactive']]
        focus = [p for p in people if p['kinds'] != ['inactive']]
        checkins = (db.session.query(m.MasteryCheckin, d.User).join(d.User, d.User.id == m.MasteryCheckin.user_id)
                    .filter(m.MasteryCheckin.section_id == section.id, m.MasteryCheckin.done_at.is_(None))
                    .order_by(m.MasteryCheckin.on_date).limit(20).all())
        mc_counts = {}
        for r in rows:
            for mc, mm in r['st']['misconceptions'].items():
                c = mc_counts.setdefault(mc, {'mc': mc, 'label': mm['label'], 'obj': mm['obj'], 'students': 0, 'hits': 0, 'active': 0})
                c['students'] += 1
                c['hits'] += mm['hits']
                c['active'] += 1 if mm['active'] else 0
        return render_template('mastery/today.html', section=section, focus=focus, inactive=only_inactive, n_students=len(rows),
                               checkins=checkins, today=utcnow().date(), tomorrow=(utcnow().date() + timedelta(days=1)).isoformat(),
                               mc_counts=sorted(mc_counts.values(), key=lambda c: (-c['students'], -c['hits'])),
                               objs=cmap['objs'], demo=any(r['st']['demo'] for r in rows),
                               lab_wired=bool(getattr(d, 'lab_events', None)))

    @login_required
    def mastery_checkin(section_id):
        section = ctx.staff_section(section_id)
        uid = request.form.get('user_id', type=int)
        u = db.session.get(d.User, uid or 0)
        back = url_for('mastery_today', section_id=section.id)
        nxt = request.form.get('next') or ''
        if nxt.startswith(f'/instructor/section/{section.id}/') and '//' not in nxt:
            back = nxt
        if not u or u.role != 'student' or not d.Enrollment.query.filter_by(section_id=section.id, user_id=u.id).first():
            flash('That check-in could not be saved.', 'danger')
            return redirect(back, code=303)
        if request.form.get('done') == '1':
            ci = db.session.get(m.MasteryCheckin, request.form.get('checkin_id', type=int) or 0)
            if ci and ci.section_id == section.id and ci.user_id == u.id:
                ci.done_at = utcnow()
                db.session.commit()
                flash(f'Check-in with {u.full_name} marked done.', 'success')
            return redirect(back, code=303)
        try:
            on = date.fromisoformat(request.form.get('on_date') or '')
        except ValueError:
            on = None
        if not on or on < utcnow().date() or on > utcnow().date() + timedelta(days=60):
            flash('Pick a check-in date from today up to 60 days ahead.', 'warning')
            return redirect(back, code=303)
        note = (request.form.get('note') or '').strip()[:300]
        reasons, _last = needs_me_reasons(eng.student_state(section, u, log=False), u)
        db.session.add(m.MasteryCheckin(section_id=section.id, user_id=u.id, on_date=on, note=note,
                                        reasons_json=json.dumps([r['text'] for r in reasons]), created_by=current_user.id))
        eng.log(section.id, u.id, 'CHECKIN', 'checkin_scheduled', 'instructor',
                [f'Your instructor scheduled a check-in for {on.strftime("%a %d %b")}.'] + ([f'Note: {note}'] if note else []),
                actor_id=current_user.id)
        db.session.commit()
        d.audit('mastery_checkin', f'section={section.id} user={u.id} date={on.isoformat()}')
        flash(f'Check-in with {u.full_name} scheduled for {on.strftime("%a %d %b")}.', 'success')
        return redirect(back, code=303)

    for rule, ep, fn, methods in [
        ('/student/section/<int:section_id>/daily', 'mastery_daily', mastery_daily, ['GET', 'POST']),
        ('/student/section/<int:section_id>/daily/result/<int:check_id>', 'mastery_daily_result', mastery_daily_result, ['GET']),
        ('/student/section/<int:section_id>/quickcheck/<int:check_id>', 'mastery_quickcheck', mastery_quickcheck, ['POST']),
        ('/student/section/<int:section_id>/quickcheck/<int:check_id>/dismiss', 'mastery_quickcheck_dismiss', mastery_quickcheck_dismiss, ['POST']),
        ('/student/section/<int:section_id>/plan', 'mastery_plan', mastery_plan, ['GET', 'POST']),
        ('/instructor/section/<int:section_id>/mastery/today', 'mastery_today', mastery_today, ['GET']),
        ('/instructor/section/<int:section_id>/mastery/checkin', 'mastery_checkin', mastery_checkin, ['POST']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)
    return {'daily_summary': daily_summary, 'lesson_quickcheck': lesson_quickcheck, 'plan_pref': plan_pref,
            'build_plan': build_plan, 'needs_me': needs_me, 'needs_me_reasons': needs_me_reasons,
            'struggle_offer': struggle_offer, 'daily_plan': daily_plan}
