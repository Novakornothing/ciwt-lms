"""Exam-Day Readiness Simulator (Option B pass 1).

A timed rehearsal of a CompTIA exam sitting for one class section: A+ Core 1 (220-1201), A+ Core 2 (220-1202) or
Network+ (N10-009). Three lengths: Official (90 min, 90 questions, 5 PBQs), Standard (90 min, 45 questions, 4 PBQs)
and Sprint (20 min, 15 questions, 2 PBQs); interactive simulation PBQs (sim_pbq) come first. Pass 4 adds server-side
auto-save/resume, a server-side practice pause, timeout grading of auto-saved answers, a one-question testing-centre
view, a whiteboard, option strikethrough, a printable candidate score report and a missed-objective drill. Practice mode lets the student pause the clock; exam mode does not and the
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
from . import sim_pbq
from .exams import ALL_DOMAINS as DOMAINS, ALL_EXAMS as EXAMS, ALL_OBJECTIVES as OBJECTIVES, DISCLAIMER, label, sort_key

REVIEW = 'Pending SME review'
PASS_SCORE = {'A1': 675, 'A2': 700, 'N': 720}
MODES = {
    'max': {'name': 'Official 90-question sitting', 'minutes': 90, 'questions': 90, 'pbqs': 5},
    'full': {'name': 'Standard 45-question sitting', 'minutes': 90, 'questions': 45, 'pbqs': 4},
    'sprint': {'name': 'Sprint (15 questions)', 'minutes': 20, 'questions': 15, 'pbqs': 2},
    # created only from a result page ("Drill My Missed Objectives Now"); not offered on the start form
    'drill': {'name': 'Missed-objective drill', 'minutes': 15, 'questions': 10, 'pbqs': 0, 'hidden': True},
}
PBQ_TYPES = ('sim_pbq', 'order', 'match')      # sim_pbq first: every sitting opens with interactive simulations
DRILL_QUESTIONS = 10
VOUCHER_STATUS = {'ready': 'VOUCHER READY', 'borderline': 'BORDERLINE', 'remediate': 'REMEDIATION REQUIRED'}
# ADA / Section 504 extended-time accommodations an instructor can set per student and class
ACCOMMODATIONS = {1.0: '1.0× Standard', 1.25: '1.25× Time + 25%', 1.5: '1.5× Time-and-a-half', 2.0: '2.0× Double time'}
CANDIDATE_RULES = (
    'The exam clock starts only when you select “I Agree — Start Exam Clock”.',
    'Work alone. No notes, phones, other browser tabs or outside help; use only the on-screen whiteboard.',
    'Performance-based questions come first; you may skip them and return before you submit.',
    'You can flag any question and use the Review Screen before you submit.',
    'In exam mode the timer cannot be paused and the sitting submits itself at 0:00; answers are auto-saved as you go.',
    'Scores are simulated (100–900); this is not an official CompTIA exam.',
)
AUTOSAVE_FIELDS = ('_pause', '_wb')            # kept in att.domains (JSON) while the sitting is unsubmitted
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
    bar = PASS_SCORE.get(exam, 650)
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
    sims = [(i, o) for i, o in sim_pbq.by_exam(exam) if i in b]
    core_sims, extra_sims = sims[:3], sims[3:]
    rng.shuffle(core_sims)
    rng.shuffle(extra_sims)
    sims = core_sims + extra_sims
    pbqs, used, doms = [], set(), set()
    for iid, oid in sims[:m['pbqs']]:
        pbqs.append((iid, oid)); used.add(iid); doms.add(OBJECTIVES[oid]['domain'])
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
    n = len(it['raw'].get('prompts') or []) if t in ('match', 'sim_pbq') else len(it['options'])
    vals = [(form.get(f'q{i}_{k}') or '')[:500] for k in range(n)]
    return json.dumps(vals) if any(vals) else None


def earned_and_possible(chosen, answers, b):
    """Points earned / possible with partial credit: a k-part PBQ is worth k points (one per sub-part right);
    single and multi items are worth 1 point, all or nothing."""
    earned = possible = 0
    for i, (iid, _oid) in enumerate(chosen):
        it = b.get(iid)
        if it is None:
            continue
        got, parts = P.partial(it, answers.get(str(i)))
        earned += got
        possible += parts
    return earned, possible


def minutes_for(mode, mult=1.0):
    return int(round(MODES[mode]['minutes'] * (mult or 1.0)))


def drill_form(exam, missed, rng=None, n=DRILL_QUESTIONS):
    """Up to n single/multi items drawn round-robin from the missed objectives (no PBQs)."""
    rng = rng or random.Random()
    b, pools = P.bank(), P.pool(exam)
    queues = {o: rng.sample([i for i in pools.get(o, []) if b[i]['type'] in ('single', 'multi')],
                            len([i for i in pools.get(o, []) if b[i]['type'] in ('single', 'multi')])) for o in missed}
    out = []
    while len(out) < n and any(queues.values()):
        for o in missed:
            if queues[o] and len(out) < n:
                out.append([queues[o].pop(), o])
    return out


def saved_value(it, val):
    """Auto-saved answer as the template needs it: str for single, list otherwise."""
    if val in (None, ''):
        return None
    if it['type'] == 'single':
        return val
    try:
        v = json.loads(val)
    except ValueError:
        return None
    return [str(x) for x in v] if isinstance(v, list) else None


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

    class ExamSimAccommodation(db.Model):
        """ADA / Section 504 extended time for one student in one class (Option B pass 5)."""
        __tablename__ = 'exam_sim_accommodation'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        multiplier = db.Column(db.Float, nullable=False, default=1.0)
        set_by = db.Column(db.Integer)                           # staff user id (plain int: not personal data)
        updated_at = db.Column(db.DateTime)
        __table_args__ = (db.UniqueConstraint('section_id', 'user_id', name='uq_exam_sim_accommodation'),)

    class ExamSimGrade(db.Model):
        """Gradebook line item: latest Exam-Day Simulator sitting per student and exam, synced by an instructor."""
        __tablename__ = 'exam_sim_grade'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        exam = db.Column(db.String(4), nullable=False)
        attempt_id = db.Column(db.Integer)
        score = db.Column(db.Integer)                            # simulated scaled 100-900
        pct = db.Column(db.Float)                                # (score - 100) / 8 → 0-100 for gradebook columns
        status = db.Column(db.String(24))
        synced_at = db.Column(db.DateTime)
        __table_args__ = (db.UniqueConstraint('section_id', 'user_id', 'exam', name='uq_exam_sim_grade'),)

    with app.app_context():
        for t in (ExamSimAccommodation.__table__, ExamSimGrade.__table__):
            t.create(db.engine, checkfirst=True)

    def multiplier(section_id, user_id):
        row = ExamSimAccommodation.query.filter_by(section_id=section_id, user_id=user_id).first()
        return row.multiplier if row and row.multiplier in ACCOMMODATIONS else 1.0

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
        refs = list((P.alignment()['objectives'].get(oid) or OBJECTIVES.get(oid) or {}).get('lessons', []))
        if course_obj:
            # the lesson whose ladder actually teaches the mapped course objective goes first, even when the
            # alignment's lesson list for this exam objective does not name it (pass 7 audit: SIM-N-2, SIM-A2-1)
            own = sorted({(k[0], k[1]) for k, v in lad.items() if v.get('obj') == course_obj},
                         key=lambda t: (t[0], *[int(x) for x in t[1].split('.')]))
            for code, lbl in own:
                ref = f'{code} {lbl}'
                if ref in refs:
                    refs.remove(ref)
                refs.insert(0, ref)
                break
            # then prefer alignment lessons that have a section for the objective over ones that would fall back
            refs = refs[:1] + sorted(refs[1:], key=lambda r: not any(
                v.get('obj') == course_obj and f'{k[0]} {k[1]}' == r for k, v in lad.items()))
        for ref in refs:
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

    def question_view(it, oid, i, answers=None, flags=(), attempt_id=None):
        q = P.public_item(it, oid)
        if attempt_id is not None and it['type'] in ('single', 'multi'):
            # deterministic per sitting: a retake shows a fresh order, a reload of the same sitting the same one
            opts = list(q['options'])
            random.Random(f'{attempt_id}:{i}:{it["id"]}').shuffle(opts)
            q['options'] = opts
        q.update(n=i, type=it['type'], pbq=it['type'] in PBQ_TYPES, flagged=i in flags,
                 saved=saved_value(it, (answers or {}).get(str(i))))
        if it['type'] == 'order':
            q['slots'] = len(it['options'])
        if it['type'] == 'sim_pbq':
            raw = it['raw']
            q['tabs'] = raw['tabs']
            q['parts'] = [{'prompt': p['prompt'], 'options': p['options']} for p in raw['parts']]
            q['review'] = raw['review']
        return q

    def meta(att):
        """Unsubmitted-sitting metadata kept in att.domains: pause state and whiteboard text."""
        if att.submitted_at:
            return {}
        try:
            m = json.loads(att.domains or '{}')
        except ValueError:
            m = {}
        return m if isinstance(m, dict) else {}

    def remaining_of(att, now):
        m = meta(att)
        if m.get('_pre') is not None:
            return int(m['_pre'])
        p = m.get('_pause')
        if p is not None and not att.strict:
            return int(p)
        return max(0, int((_naive(att.deadline) - now).total_seconds()))

    def begin(att, now):
        """Start the clock: the candidate agreed (or a direct POST/auto-save arrived before /begin)."""
        m = meta(att)
        if m.get('_pre') is None:
            return False
        pre = int(m.pop('_pre'))
        # the stored deadline is provisional (started_at + allowance) until the candidate agrees; a deadline that was
        # changed by an administrator or a test fixture is respected as-is
        if abs((_naive(att.deadline) - (_naive(att.started_at) + timedelta(seconds=pre))).total_seconds()) <= 2:
            att.deadline = now + timedelta(seconds=pre)
        att.domains = json.dumps(m) if m else None
        return True

    def collect(att, form, chosen, b):
        answers, flags = {}, []
        for i, (iid, _oid) in enumerate(chosen):
            it = b.get(iid)
            if it is None:
                continue
            if form.get(f'flag{i}') == '1':
                flags.append(i)
            val = compose(it, form, i)
            if val is not None:
                answers[str(i)] = val
        return answers, flags

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
            d = by_dom.setdefault(dom, {'correct': 0, 'total': 0, 'earned': 0, 'possible': 0, 'missed': {}})
            d['total'] += 1
            d['correct'] += int(ok)
            got, parts = P.partial(it, answers.get(str(i)))
            d['earned'] += got
            d['possible'] += parts
            if not ok:
                d['missed'].setdefault(oid, it['raw'].get('obj'))
            review.append({'n': i + 1, 'ok': ok, 'parts': parts, 'parts_right': got, 'sim': it['type'] == 'sim_pbq', 'flagged': i in flags, 'answered': str(i) in answers,
                           'text': it['text'], 'lo': label(oid), 'pbq': it['type'] in PBQ_TYPES,
                           'yours': P.display_answer(it, answers.get(str(i))), 'key': P.display_key(it),
                           'why': it['explanation']})
        domains = []
        for dom in sorted(by_dom, key=float):
            d = by_dom[dom]
            pct = round(100 * d['earned'] / d['possible']) if d['possible'] else 0     # partial credit on PBQs
            missed = [{'oid': o, 'label': label(o), 'title': OBJECTIVES[o]['title'],
                       'links': remediation(o, cobj, att.section_id)}
                      for o, cobj in sorted(d['missed'].items(), key=lambda kv: sort_key(kv[0]))]
            domains.append({'id': dom, 'name': names[dom], 'pct': pct, 'correct': d['correct'], 'total': d['total'],
                            'earned': d['earned'], 'possible': d['possible'],
                            'weak': pct < DOMAIN_FLOOR, 'missed': missed})
        return domains, review

    # ------------------------------------------------------------------ student
    @login_required
    def exam_sim_home(section_id):
        sec = student_section(section_id)
        past = (ExamSimAttempt.query.filter_by(user_id=current_user.id, section_id=sec.id)
                .order_by(ExamSimAttempt.id.desc()).limit(10).all())
        mult = multiplier(sec.id, current_user.id)
        return render_template('exam_sim/home.html', section=sec, exams=EXAMS, modes=MODES, pass_score=dict(PASS_SCORE, T=650, S=750),
                               mult=mult, mult_label=ACCOMMODATIONS.get(mult), minutes_for=minutes_for,
                               default_exam=default_exam(sec), past=past, badges=BADGES, disclaimer=DISCLAIMER,
                               review=REVIEW)

    @login_required
    def exam_sim_start(section_id):
        sec = student_section(section_id)
        exam, mode = request.form.get('exam'), request.form.get('mode')
        if exam not in EXAMS or mode not in MODES or MODES[mode].get('hidden'):
            abort(400)
        chosen = build_form(exam, mode)
        if not chosen:
            flash('No questions are available for that exam yet.', 'warning')
            return redirect(url_for('exam_sim_home', section_id=sec.id))
        now = _naive(utcnow())
        mins = minutes_for(mode, multiplier(sec.id, current_user.id))
        att = ExamSimAttempt(user_id=current_user.id, section_id=sec.id, exam=exam, mode=mode,
                             strict=request.form.get('timing') == 'exam', items=json.dumps(chosen), started_at=now,
                             deadline=now + timedelta(minutes=mins), total=len(chosen),
                             domains=json.dumps({'_pre': mins * 60}))     # clock waits for the candidate agreement
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
            begin(att, now)
            late = att.strict and now > _naive(att.deadline) + timedelta(seconds=GRACE_SECONDS)
            # start from what auto-save already stored (saved before deadline + grace in exam mode)
            answers = json.loads(att.answers or '{}')
            flags = json.loads(att.flags or '[]')
            if not late:
                form_answers, form_flags = collect(att, request.form, chosen, b)
                answers.update(form_answers)
                if any(k.startswith('flag') for k in request.form) or request.form.get('flags_sent') == '1':
                    flags = form_flags
            att.answers, att.flags = json.dumps(answers), json.dumps(sorted(set(flags)))
            att.submitted_at = now
            att.timed_out = late or request.form.get('timed_out') == '1'
            att.correct = sum(1 for i, (iid, _o) in enumerate(chosen) if iid in b and P.grade(b[iid], answers.get(str(i))))
            earned, possible = earned_and_possible(chosen, answers, b)
            att.score = scaled(earned, possible)          # multi-part PBQs: one point per sub-part (partial credit)
            att.domains = None
            domains, _r = summarise(att)
            att.domains = json.dumps({d['id']: [d['correct'], d['total']] for d in domains})
            att.badge = readiness(att.score, att.exam, [d['pct'] for d in domains])
            db.session.commit()
            audit('exam_sim_submit', f'{att.exam}/{att.mode}/{att.id}: {att.score} {att.badge}')
            return redirect(url_for('exam_sim_result', section_id=sec.id, attempt_id=att.id))
        answers, flags = json.loads(att.answers or '{}'), set(json.loads(att.flags or '[]'))
        questions = [question_view(b[iid], oid, i, answers, flags, attempt_id=att.id) for i, (iid, oid) in enumerate(chosen) if iid in b]
        m = meta(att)
        mult = multiplier(sec.id, att.user_id)
        return render_template('exam_sim/take.html', section=sec, att=att, questions=questions,
                               pre='_pre' in m, mult=mult, minutes=minutes_for(att.mode, mult),
                               mult_label=ACCOMMODATIONS.get(mult), rules=CANDIDATE_RULES, bar=PASS_SCORE.get(att.exam, 650),
                               remaining=remaining_of(att, now), paused='_pause' in m and not att.strict,
                               whiteboard=m.get('_wb', ''), exam=EXAMS[att.exam], mode=MODES[att.mode],
                               n_pbq=sum(1 for q in questions if q['pbq']))

    @login_required
    def exam_sim_autosave(section_id, attempt_id):
        sec = student_section(section_id)
        att = _own(sec.id, attempt_id)
        now = _naive(utcnow())
        if att.submitted_at:
            return {'ok': False, 'error': 'submitted'}, 409
        if begin(att, now):
            db.session.commit()
        if att.strict and now > _naive(att.deadline) + timedelta(seconds=GRACE_SECONDS):
            return {'ok': False, 'error': 'time expired'}, 409
        b = P.bank()
        answers, flags = collect(att, request.form, json.loads(att.items), b)
        saved = json.loads(att.answers or '{}')
        for i in range(len(json.loads(att.items))):     # the form carries every question: replace, including clears
            if str(i) in answers:
                saved[str(i)] = answers[str(i)]
            elif request.form.get('all') == '1':
                saved.pop(str(i), None)
        att.answers, att.flags = json.dumps(saved), json.dumps(flags)
        if 'whiteboard' in request.form:
            m = meta(att)
            m['_wb'] = request.form.get('whiteboard', '')[:20000]
            att.domains = json.dumps(m)
        db.session.commit()
        return {'ok': True, 'answered': len(saved), 'flagged': len(flags), 'remaining': remaining_of(att, now)}

    @login_required
    def exam_sim_begin(section_id, attempt_id):
        sec = student_section(section_id)
        att = _own(sec.id, attempt_id)
        if att.submitted_at:
            return {'ok': False, 'error': 'submitted'}, 409
        now = _naive(utcnow())
        started = begin(att, now)
        db.session.commit()
        if started:
            audit('exam_sim_begin', f'{att.exam}/{att.mode}/{att.id}')
        if request.accept_mimetypes.best == 'application/json' or request.is_json or request.headers.get('X-Requested-With'):
            return {'ok': True, 'remaining': remaining_of(att, now)}
        return redirect(url_for('exam_sim_take', section_id=sec.id, attempt_id=att.id))

    @login_required
    def exam_sim_pause(section_id, attempt_id):
        sec = student_section(section_id)
        att = _own(sec.id, attempt_id)
        if att.strict or att.submitted_at:
            abort(403 if att.strict else 409)
        now = _naive(utcnow())
        begin(att, now)
        m = meta(att)
        action = request.form.get('action') or ('resume' if '_pause' in m else 'pause')
        if action == 'pause' and '_pause' not in m:
            m['_pause'] = max(0, int((_naive(att.deadline) - now).total_seconds()))
        elif action == 'resume' and '_pause' in m:
            att.deadline = now + timedelta(seconds=int(m.pop('_pause')))
        att.domains = json.dumps(m)
        db.session.commit()
        return {'ok': True, 'paused': '_pause' in m, 'remaining': remaining_of(att, now)}

    @login_required
    def exam_sim_remediate(section_id, attempt_id):
        sec = student_section(section_id)
        att = _own(sec.id, attempt_id)
        if not att.submitted_at:
            abort(409)
        domains, _r = summarise(att)
        missed = [m['oid'] for d in domains for m in d['missed']]
        if not missed:      # perfect sitting: drill the weakest domain's objectives
            weakest = min(domains, key=lambda d: d['pct'])['id'] if domains else None
            missed = sorted(P.pool(att.exam, weakest), key=sort_key) if weakest else []
        chosen = drill_form(att.exam, missed)
        if not chosen and domains:     # missed objectives with no single/multi items: fall back to the weakest domain
            weakest = min(domains, key=lambda d: d['pct'])['id']
            chosen = drill_form(att.exam, sorted(P.pool(att.exam, weakest), key=sort_key))
        if not chosen:
            flash('No drill questions are available for those objectives yet.', 'warning')
            return redirect(url_for('exam_sim_result', section_id=sec.id, attempt_id=att.id))
        now = _naive(utcnow())
        mins = minutes_for('drill', multiplier(sec.id, current_user.id))
        new = ExamSimAttempt(user_id=current_user.id, section_id=sec.id, exam=att.exam, mode='drill', strict=False,
                             items=json.dumps(chosen), started_at=now, deadline=now + timedelta(minutes=mins),
                             total=len(chosen), domains=json.dumps({'_pre': mins * 60}))
        db.session.add(new)
        db.session.commit()
        audit('exam_sim_drill', f'{att.exam}/{att.id}->{new.id}: {len(chosen)} items')
        return redirect(url_for('exam_sim_take', section_id=sec.id, attempt_id=new.id))

    @login_required
    def exam_sim_result(section_id, attempt_id):
        if current_user.role in ('instructor', 'admin'):
            # staff read-only view (linked from "Why this student is struggling")
            sec = db.get_or_404(ClassSection, section_id)
            if not can_access(current_user, sec) and current_user.role != 'admin':
                abort(403)
            att = db.get_or_404(ExamSimAttempt, attempt_id)
            if att.section_id != sec.id:
                abort(404)
        else:
            sec = student_section(section_id)
            att = _own(sec.id, attempt_id)
        if not att.submitted_at and att.user_id != current_user.id:
            abort(404)
        if not att.submitted_at:
            return redirect(url_for('exam_sim_take', section_id=sec.id, attempt_id=att.id))
        domains, review = summarise(att)
        codes = [m['label'] for d in domains for m in d['missed']]
        status = VOUCHER_STATUS.get(att.badge, 'REMEDIATION REQUIRED')
        return render_template('exam_sim/result.html', section=sec, att=att, domains=domains, review=review,
                               candidate=db.session.get(User, att.user_id), codes=codes, status=status,
                               staff_view=att.user_id != current_user.id,
                               exam=EXAMS[att.exam], mode=MODES[att.mode], bar=PASS_SCORE.get(att.exam, 650),
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
        students = sorted((u for u in User.query.join(Enrollment, Enrollment.user_id == User.id)
                           .filter(Enrollment.section_id == sec.id).all()), key=lambda u: (u.last_name or '', u.first_name or ''))
        acc = {a.user_id: a.multiplier for a in ExamSimAccommodation.query.filter_by(section_id=sec.id).all()}
        synced = ExamSimGrade.query.filter_by(section_id=sec.id).order_by(ExamSimGrade.synced_at.desc()).first()
        return render_template('exam_sim/instructor.html', section=sec, rows=rows, users=users, latest=latest,
                               students=students, acc=acc, accommodations=ACCOMMODATIONS, can_grade=can_grade(sec),
                               last_sync=synced.synced_at if synced else None, minutes_for=minutes_for,
                               exams=EXAMS, modes=MODES, badges=BADGES, counts=counts, weak=weak_rows,
                               pass_score=dict(PASS_SCORE, T=650, S=750), disclaimer=DISCLAIMER)

    def staff_section(section_id):
        sec = db.get_or_404(ClassSection, section_id)
        if current_user.role not in ('instructor', 'admin') or not can_access(current_user, sec):
            abort(403)
        return sec

    def can_grade(sec):
        school = app.extensions.get('ciwt_school')
        fn = getattr(school, 'can_edit_grades', None) if school else None
        return True if fn is None else bool(fn(current_user, sec))

    def latest_rows(sec):
        rows = ExamSimAttempt.query.filter_by(section_id=sec.id).filter(ExamSimAttempt.submitted_at.isnot(None)) \
            .filter(ExamSimAttempt.mode != 'drill').order_by(ExamSimAttempt.submitted_at.desc()).all()
        latest = {}
        for r in rows:
            latest.setdefault((r.user_id, r.exam), r)
        return rows, latest

    @login_required
    def instructor_exam_sim_csv(section_id):
        import csv
        import io
        sec = staff_section(section_id)
        rows, latest = latest_rows(sec)
        users = {u.id: u for u in User.query.filter(User.id.in_({r.user_id for r in rows} or {0})).all()}
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['student', 'email', 'exam', 'exam_code', 'mode', 'timing', 'scaled_score', 'pass_bar', 'status',
                    'correct', 'total', 'submitted_utc', 'latest', 'time_multiplier'])
        acc = {a.user_id: a.multiplier for a in ExamSimAccommodation.query.filter_by(section_id=sec.id).all()}
        for r in rows:
            u = users.get(r.user_id)
            w.writerow([u.full_name if u else r.user_id, u.email if u else '', EXAMS[r.exam]['short'], EXAMS[r.exam]['code'],
                        MODES.get(r.mode, {}).get('name', r.mode), 'exam' if r.strict else 'practice', r.score,
                        PASS_SCORE.get(r.exam, 650), VOUCHER_STATUS.get(r.badge, ''), r.correct, r.total,
                        r.submitted_at.strftime('%Y-%m-%d %H:%M'), 'yes' if latest.get((r.user_id, r.exam)) is r else '',
                        acc.get(r.user_id, 1.0)])
        audit('exam_sim_export', f'section {sec.id}: {len(rows)} rows')
        return app.response_class(buf.getvalue(), mimetype='text/csv', headers={
            'Content-Disposition': f'attachment; filename=exam-sim-section-{sec.id}.csv'})

    @login_required
    def instructor_exam_sim_sync(section_id):
        sec = staff_section(section_id)
        if not can_grade(sec):
            abort(403)
        _rows, latest = latest_rows(sec)
        enrolled = {e.user_id for e in Enrollment.query.filter_by(section_id=sec.id).all()}
        latest = {k: r for k, r in latest.items() if k[0] in enrolled}     # dropped students are not synced
        now = _naive(utcnow())
        by_exam = {}
        for (uid, ex), r in latest.items():
            g = ExamSimGrade.query.filter_by(section_id=sec.id, user_id=uid, exam=ex).first() or \
                ExamSimGrade(section_id=sec.id, user_id=uid, exam=ex)
            g.attempt_id, g.score, g.status, g.synced_at = r.id, r.score, VOUCHER_STATUS.get(r.badge, ''), now
            g.pct = round(max(0, (r.score or 100) - 100) / 8, 1)
            db.session.add(g)
            by_exam.setdefault(ex, {})[uid] = (r.score, f'{VOUCHER_STATUS.get(r.badge, "")} · pass bar {PASS_SCORE.get(ex, 650)} (simulated)')
        db.session.commit()
        msg = f'Synced {len(latest)} latest sitting(s) to the gradebook line items.'
        lti = app.extensions.get('ciwt_lti')
        if lti is not None and getattr(lti, 'send_line_scores', None):
            sent = failed = 0
            for ex, scores in by_exam.items():
                s_, f_, _n = lti.send_line_scores(sec, current_user, f'Exam-Day Simulator — {EXAMS[ex]["code"]}',
                                                  f'novak-exam-sim-{ex}', scores)
                sent, failed = sent + s_, failed + f_
            if sent or failed:
                msg += f' LTI: {sent} score(s) sent, {failed} failed.'
        audit('exam_sim_sync', f'section {sec.id}: {len(latest)} rows')
        flash(msg, 'success')
        return redirect(url_for('instructor_exam_sim', section_id=sec.id))

    @login_required
    def instructor_exam_sim_accommodation(section_id):
        sec = staff_section(section_id)
        if not can_grade(sec):
            abort(403)
        try:
            uid, mult = int(request.form.get('user_id')), float(request.form.get('multiplier'))
        except (TypeError, ValueError):
            abort(400)
        if mult not in ACCOMMODATIONS or not Enrollment.query.filter_by(user_id=uid, section_id=sec.id).first():
            abort(400)
        row = ExamSimAccommodation.query.filter_by(section_id=sec.id, user_id=uid).first()
        if mult == 1.0:
            if row:
                db.session.delete(row)
        else:
            row = row or ExamSimAccommodation(section_id=sec.id, user_id=uid)
            row.multiplier, row.set_by, row.updated_at = mult, current_user.id, _naive(utcnow())
            db.session.add(row)
        db.session.commit()
        audit('exam_sim_accommodation', f'section {sec.id} user {uid}: {mult}x')
        flash(f'Time accommodation saved: {ACCOMMODATIONS[mult]}.', 'success')
        return redirect(url_for('instructor_exam_sim', section_id=sec.id) + '#esAccommodations')

    app.extensions['ciwt_exam_sim'] = type('ExamSimApi', (), {})()
    app.extensions['ciwt_exam_sim'].Attempt = ExamSimAttempt
    app.extensions['ciwt_exam_sim'].Accommodation = ExamSimAccommodation
    app.extensions['ciwt_exam_sim'].Grade = ExamSimGrade
    app.extensions['ciwt_exam_sim'].multiplier = multiplier
    app.extensions['ciwt_exam_sim'].remediation = remediation
    app.extensions['ciwt_exam_sim'].question_view = question_view

    for rule, ep, fn, methods in (
        ('/student/section/<int:section_id>/exam-sim', 'exam_sim_home', exam_sim_home, ['GET']),
        ('/student/section/<int:section_id>/exam-sim/start', 'exam_sim_start', exam_sim_start, ['POST']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>', 'exam_sim_take', exam_sim_take, ['GET', 'POST']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>/result', 'exam_sim_result', exam_sim_result, ['GET']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>/autosave', 'exam_sim_autosave', exam_sim_autosave, ['POST']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>/pause', 'exam_sim_pause', exam_sim_pause, ['POST']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>/remediate-drill', 'exam_sim_remediate', exam_sim_remediate, ['POST']),
        ('/instructor/section/<int:section_id>/exam-sim', 'instructor_exam_sim', instructor_exam_sim, ['GET']),
        ('/instructor/section/<int:section_id>/exam-sim/export.csv', 'instructor_exam_sim_csv', instructor_exam_sim_csv, ['GET']),
        ('/instructor/section/<int:section_id>/exam-sim/sync-gradebook', 'instructor_exam_sim_sync', instructor_exam_sim_sync, ['POST']),
        ('/instructor/section/<int:section_id>/exam-sim/accommodation', 'instructor_exam_sim_accommodation',
         instructor_exam_sim_accommodation, ['POST']),
        ('/student/section/<int:section_id>/exam-sim/<int:attempt_id>/begin', 'exam_sim_begin', exam_sim_begin, ['POST']),
    ):
        app.add_url_rule(rule, ep, fn, methods=methods)
    return ExamSimAttempt
