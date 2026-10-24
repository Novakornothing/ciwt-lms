"""Exam-Day Readiness Simulator (Option B pass 1).

A timed rehearsal of a CompTIA exam sitting for one class section: A+ Core 1 (220-1201), A+ Core 2 (220-1202) or
Network+ (N10-009). Two lengths: Full (90 min, 45 questions, 4 performance-based items first) and Sprint
(20 min, 15 questions, 2 PBQs first). Practice mode lets the student pause the clock; exam mode does not and the
server refuses late answers beyond a short grace. The student can flag questions for review, skip the PBQs and come
back, and sees a review grid (answered / unanswered / flagged) before submitting.

Scoring: a *simulated* scaled score, 100 + 800 x fraction correct, compared with CompTIA's published passing score
(675 Core 1, 700 Core 2; Network+ 720 as commonly cited — CompTIA's objectives document does not state it). CompTIA
does not publish its scaling, so the number is an estimate and is labelled as one everywhere it is shown.
Every missed objective links to the matching lesson and the explanation-ladder rung (R1, plain language) of the
lesson section that teaches the same course objective. Pending SME review.
"""
import json
import random
from datetime import timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import practice as P
from .exams import DISCLAIMER, DOMAINS, EXAMS, OBJECTIVES, label, sort_key

REVIEW = 'Pending SME review'
PASS_SCORE = {'A1': 675, 'A2': 700, 'N': 720}
MODES = {
    'full': {'name': 'Full exam', 'minutes': 90, 'questions': 45, 'pbqs': 4},
    'sprint': {'name': 'Sprint', 'minutes': 20, 'questions': 15, 'pbqs': 2},
}
PBQ_TYPES = ('order', 'match')
GRACE_SECONDS = 30
BORDERLINE_BAND = 50      # scaled points below the pass bar that still count as "borderline"
DOMAIN_FLOOR = 60         # % — a passing score with any domain under this is "borderline", not "ready"
BADGES = {
    'ready': 'Ready to sit',
    'borderline': 'Borderline — review flagged domains',
    'remediate': 'Needs remediation',
}


def scaled(correct, total):
    """Simulated CompTIA-style scaled score on 100–900 (linear; CompTIA's real scaling is not published)."""
    if not total:
        return 100
    return int(round(100 + 800 * correct / total))


def readiness(score, exam, domain_pcts):
    bar = PASS_SCORE[exam]
    if score >= bar and all(p >= DOMAIN_FLOOR for p in domain_pcts):
        return 'ready'
    if score >= bar - BORDERLINE_BAND:
        return 'borderline'
    return 'remediate'


def build_form(exam, mode, rng=None):
    """[[item_id, objective_id], ...] with the mode's PBQs (ordering / matching items) first."""
    rng = rng or random.Random()
    m = MODES[mode]
    b = P.bank()
    pbq_pool = [(i, o) for o, ids in sorted(P.pool(exam).items()) for i in ids if b[i]['type'] in PBQ_TYPES]
    rng.shuffle(pbq_pool)
    pbqs, used, doms = [], set(), set()
    for iid, oid in pbq_pool:         # spread the PBQs over domains first
        if len(pbqs) >= m['pbqs']:
            break
        d = OBJECTIVES[oid]['domain']
        if iid not in used and d not in doms:
            pbqs.append((iid, oid)); used.add(iid); doms.add(d)
    for iid, oid in pbq_pool:
        if len(pbqs) >= m['pbqs']:
            break
        if iid not in used:
            pbqs.append((iid, oid)); used.add(iid)
    rest = [(i, o) for i, o in P.draw(exam, n=m['questions'] + len(pbqs), rng=rng)
            if i not in used and b[i]['type'] not in PBQ_TYPES]
    if len(rest) < m['questions'] - len(pbqs):    # top up from anything left in the pool
        extra = [(i, o) for o, ids in sorted(P.pool(exam).items()) for i in ids
                 if i not in used and i not in {x for x, _ in rest} and b[i]['type'] not in PBQ_TYPES]
        rng.shuffle(extra)
        rest += extra
    return [list(x) for x in pbqs + rest[:m['questions'] - len(pbqs)]]


def compose(it, form, i):
    """The submitted value for question i as practice.grade() expects it (str for single, JSON list otherwise)."""
    t = it['type']
    if t == 'single':
        v = form.get(f'q{i}')
        return v[:2000] if v else None
    if t == 'multi':
        vals = [v[:500] for v in form.getlist(f'q{i}') if v]
        return json.dumps(vals) if vals else None
    n = len(it['raw'].get('prompts') or []) if t == 'match' else len(it['options'])
    vals = [(form.get(f'q{i}_{k}') or '')[:500] for k in range(n)]
    return json.dumps(vals) if any(vals) else None


def register(app, db, deps):
    """deps: User, Course, Module, Lesson, ClassSection, Enrollment, utcnow, can_access_section, audit."""
    Course, Module, Lesson = deps['Course'], deps['Module'], deps['Lesson']
    ClassSection, Enrollment = deps['ClassSection'], deps['Enrollment']
    utcnow, can_access, User = deps['utcnow'], deps['can_access_section'], deps['User']
    audit = deps.get('audit') or (lambda *a, **k: None)

    class ExamSimAttempt(db.Model):
        __tablename__ = 'exam_sim_attempt'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        exam = db.Column(db.String(4), nullable=False)
        mode = db.Column(db.String(10), nullable=False)          # full | sprint
        strict = db.Column(db.Boolean, default=False)            # exam mode (no pause) vs practice mode
        items = db.Column(db.Text, nullable=False)               # JSON [[item_id, objective_id], ...], PBQs first
        started_at = db.Column(db.DateTime, nullable=False)
        deadline = db.Column(db.DateTime, nullable=False)
        submitted_at = db.Column(db.DateTime)
        answers = db.Column(db.Text)                             # JSON {index: submitted value}
        flags = db.Column(db.Text)                               # JSON [index, ...]
        correct = db.Column(db.Integer)
        total = db.Column(db.Integer)
        score = db.Column(db.Integer)                            # simulated scaled score 100-900
        badge = db.Column(db.String(12))
        domains = db.Column(db.Text)                             # JSON {domain: [correct, total]}
        timed_out = db.Column(db.Boolean, default=False)

    def _naive(dt):
        return dt.replace(tzinfo=None) if dt is not None and dt.tzinfo else dt

    def student_section(section_id):
        sec = db.get_or_404(ClassSection, section_id)
        if current_user.role == 'admin':
            return sec
        if not Enrollment.query.filter_by(user_id=current_user.id, section_id=sec.id).first():
            abort(403)
        return sec

    def default_exam(sec):
        code = sec.course.code if getattr(sec, 'course', None) else None
        for ex, meta in EXAMS.items():
            if meta['course'] == code:
                return ex
        return 'A1'

    def _lesson(code, ch, lo):
        course = Course.query.filter_by(code=code).first()
        mod = Module.query.filter_by(course_id=course.id, order=ch).first() if course else None
        return Lesson.query.filter_by(module_id=mod.id, order=lo).first() if mod else None

    def remediation(oid, course_obj, section_id):
        """Lesson section + ladder rung links for one missed objective (max 2)."""
        from curriculum_v2 import ladder as LD
        lad = LD.ladder()
        out = []
        for ref in P.alignment()['objectives'].get(oid, {}).get('lessons', []):
            if len(out) >= 2:
                break
            try:
                code, ch, lo = P.lesson_ref(ref)
            except ValueError:
                continue
            les = _lesson(code, ch, lo)
            if not les:
                continue
            lbl = f'{ch}.{lo}'
            secs = [(k[2], v) for k, v in lad.items() if k[0] == code and k[1] == lbl]
            pick = next((s for s in secs if course_obj and s[1].get('obj') == course_obj), secs[0] if secs else None)
            link = {'ref': ref, 'title': les.title,
                    'lesson_url': url_for('lesson_shortcut', section_id=section_id, lesson_id=les.id)}
            if pick:
                link['heading'] = pick[1].get('heading') or pick[0]
                link['rung_url'] = url_for('lesson_shortcut', section_id=section_id, lesson_id=les.id,
                                           rung='R1', sid=pick[0]) + f'#ladder-{pick[0]}'
            out.append(link)
        return out

    def question_view(it, oid, i):
        q = P.public_item(it, oid)
        q.update(n=i, type=it['type'], pbq=it['type'] in PBQ_TYPES)
        if it['type'] == 'order':
            q['slots'] = len(it['options'])
        return q

    def summarise(att):
        chosen = json.loads(att.items)
        answers = json.loads(att.answers or '{}')
        flags = set(json.loads(att.flags or '[]'))
        b = P.bank()
        names = {d: n for d, n, _w in DOMAINS[att.exam]}
        by_dom, review = {}, []
        for i, (iid, oid) in enumerate(chosen):
            it = b.get(iid)
            if not it:
                continue
            ok = P.grade(it, answers.get(str(i)))
            dom = OBJECTIVES[oid]['domain']
            d = by_dom.setdefault(dom, {'correct': 0, 'total': 0, 'missed': {}})
            d['total'] += 1
            d['correct'] += int(ok)
            if not ok:
                d['missed'].setdefault(oid, it['raw'].get('obj'))
            review.append({'n': i + 1, 'ok': ok, 'flagged': i in flags, 'answered': str(i) in answers,
                           'text': it['text'], 'lo': label(oid), 'pbq': it['type'] in PBQ_TYPES,
                           'yours': P.display_answer(it, answers.get(str(i))), 'key': P.display_key(it),
                           'why': it['explanation']})
        domains = []
        for dom in sorted(by_dom, key=float):
            d = by_dom[dom]
            pct = round(100 * d['correct'] / d['total']) if d['total'] else 0
            missed = [{'oid': o, 'label': label(o), 'title': OBJECTIVES[o]['title'],
                       'links': remediation(o, cobj, att.section_id)}
                      for o, cobj in sorted(d['missed'].items(), key=lambda kv: sort_key(kv[0]))]
            domains.append({'id': dom, 'name': names[dom], 'pct': pct, 'correct': d['correct'], 'total': d['total'],
                            'weak': pct < DOMAIN_FLOOR, 'missed': missed})
        return domains, review

    # ------------------------------------------------------------------ student
    @login_required
    def exam_sim_home(section_id):
        sec = student_section(section_id)
        past = (ExamSimAttempt.query.filter_by(user_id=current_user.id, section_id=sec.id)
                .order_by(ExamSimAttempt.id.desc()).limit(10).all())
        return render_template('exam_sim/home.html', section=sec, exams=EXAMS, modes=MODES, pass_score=PASS_SCORE,
                               default_exam=default_exam(sec), past=past, badges=BADGES, disclaimer=DISCLAIMER,
                               review=REVIEW)

    @login_required
    def exam_sim_start(section_id):
        sec = student_section(section_id)
        exam, mode = request.form.get('exam'), request.form.get('mode')
        if exam not in EXAMS or mode not in MODES:
            abort(400)
        chosen = build_form(exam, mode)
        if not chosen:
            flash('No questions are available for that exam yet.', 'warning')
            return redirect(url_for('exam_sim_home', section_id=sec.id))
        now = _naive(utcnow())
        att = ExamSimAttempt(user_id=current_user.id, section_id=sec.id, exam=exam, mode=mode,
                             strict=request.form.get('timing') == 'exam', items=json.dumps(chosen), started_at=now,
                             deadline=now + timedelta(minutes=MODES[mode]['minutes']), total=len(chosen))
        db.session.add(att)
        db.session.commit()
        audit('exam_sim_start', f'{exam}/{mode}/{"exam" if att.strict else "practice"}/{att.id}')
        return redirect(url_for('exam_sim_take', section_id=sec.id, attempt_id=att.id))

    def _own(section_id, attempt_id):
        att = db.get_or_404(ExamSimAttempt, attempt_id)
        if att.user_id != current_user.id or att.section_id != section_id:
            abort(404)
        return att

    @login_required
    def exam_sim_take(section_id, attempt_id):
        sec = student_section(section_id)
        att = _own(sec.id, attempt_id)
        if att.submitted_at:
            return redirect(url_for('exam_sim_result', section_id=sec.id, attempt_id=att.id))
        chosen = json.loads(att.items)
        b = P.bank()
        now = _naive(utcnow())
        if request.method == 'POST':
            late = att.strict and now > _naive(att.deadline) + timedelta(seconds=GRACE_SECONDS)
            answers, flags = {}, []
            for i, (iid, _oid) in enumerate(chosen):
                it = b.get(iid)
                if it is None:
                    continue
                if request.form.get(f'flag{i}') == '1':
                    flags.append(i)
                if late:
                    continue        # strict exam mode: nothing after the clock (plus grace) counts
                val = compose(it, request.form, i)
                if val is not None:
                    answers[str(i)] = val
            att.answers, att.flags = json.dumps(answers), json.dumps(flags)
            att.submitted_at = now
            att.timed_out = late or request.form.get('timed_out') == '1'
            att.correct = sum(1 for i, (iid, _o) in enumerate(chosen) if iid in b and P.grade(b[iid], answers.get(str(i))))
            att.score = scaled(att.correct, att.total)
            domains, _r = summarise(att)
            att.domains = json.dumps({d['id']: [d['correct'], d['total']] for d in domains})
            att.badge = readiness(att.score, att.exam, [d['pct'] for d in domains])
            db.session.commit()
            audit('exam_sim_submit', f'{att.exam}/{att.mode}/{att.id}: {att.score} {att.badge}')
            return redirect(url_for('exam_sim_result', section_id=sec.id, attempt_id=att.id))
        questions = [question_view(b[iid], oid, i) for i, (iid, oid) in enumerate(chosen) if iid in b]
        remaining = max(0, int((_naive(att.deadline) - now).total_seconds()))
        return render_template('exam_sim/take.html', section=sec, att=att, questions=questions, remaining=remaining,
                               exam=EXAMS[att.exam], mode=MODES[att.mode],
                               n_pbq=sum(1 for q in questions if q['pbq']))

    @login_required
    def exam_sim_result(section_id, attempt_id):
        sec = student_section(section_id)
        att = _own(sec.id, attempt_id)
        if not att.submitted_at:
            return redirect(url_for('exam_sim_take', section_id=sec.id, attempt_id=att.id))
        domains, review = summarise(att)
        return render_template('exam_sim/result.html', section=sec, att=att, domains=domains, review=review,
                               exam=EXAMS[att.exam], mode=MODES[att.mode], bar=PASS_SCORE[att.exam],
                               badge=BADGES[att.badge or 'remediate'], disclaimer=DISCLAIMER, review_tag=REVIEW)

    # ------------------------------------------------------------------ instructor
    @login_required
    def instructor_exam_sim(section_id):
        sec = db.get_or_404(ClassSection, section_id)
        if current_user.role not in ('instructor', 'admin') or not can_access(current_user, sec):
            abort(403)
        rows = ExamSimAttempt.query.filter_by(section_id=sec.id).filter(ExamSimAttempt.submitted_at.isnot(None)) \
            .order_by(ExamSimAttempt.submitted_at.desc()).all()
        users = {u.id: u for u in User.query.filter(User.id.in_({r.user_id for r in rows} or {0})).all()}
        latest, weak = {}, {}
        for r in rows:
            latest.setdefault((r.user_id, r.exam), r)
        for r in latest.values():
            for dom, (c, t) in json.loads(r.domains or '{}').items():
                if t and 100 * c / t < DOMAIN_FLOOR:
                    weak.setdefault((r.exam, dom), 0)
                    weak[(r.exam, dom)] += 1
        names = {(ex, d): n for ex in DOMAINS for d, n, _w in DOMAINS[ex]}
        weak_rows = sorted(({'exam': EXAMS[ex]['short'], 'domain': d, 'name': names.get((ex, d), d), 'n': n}
                            for (ex, d), n in weak.items()), key=lambda x: -x['n'])
        counts = {k: sum(1 for r in latest.values() if r.badge == k) for k in BADGES}
        return render_template('exam_sim/instructor.html', section=sec, rows=rows, users=users, latest=latest,
                               exams=EXAMS, modes=MODES, badges=BADGES, counts=counts, weak=weak_rows,
                               pass_score=PASS_SCORE, disclaimer=DISCLAIMER)

    for rule, ep, fn, methods in (
        ('/student/section/<int:section_id>/exam-sim', 'exam_sim_home', exam_sim_home, ['GET']),
        ('/student/section/<int:section_id>/exam-sim/start', 'exam_sim_start', exam_sim_start, ['POST']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>', 'exam_sim_take', exam_sim_take, ['GET', 'POST']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>/result', 'exam_sim_result', exam_sim_result, ['GET']),
        ('/instructor/section/<int:section_id>/exam-sim', 'instructor_exam_sim', instructor_exam_sim, ['GET']),
    ):
        app.add_url_rule(rule, ep, fn, methods=methods)
    return ExamSimAttempt
