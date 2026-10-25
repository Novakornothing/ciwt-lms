"""Institutional outcomes from recorded data only. Every figure carries its denominator; nothing is imputed.

Definitions (also shown on the report):
- Right first time: share of student x objective pairs whose FIRST answered item (quiz/test/check/lab) was correct.
- Mastered now: share of those pairs the mastery engine rates mastered today.
- Ladder: a struggle is a ladder state that left the original explanation (R0) or recorded a miss;
  "resolved by" is the rung on which the student then answered the micro-check correctly.
- Lab process: diagnose-first / verify-before-submit rates over completed labs whose event log could be analysed.
"""
from collections import Counter, defaultdict
from statistics import median

from curriculum_v2 import ladder as LD
from curriculum_v2.cert import exams as EX
from curriculum_v2.objectives import OBJECTIVES

_CERT = {}


def cert_map(obj):
    """Official exam objectives (A+ 220-1201/1202, Network+ N10-009) aligned to a course objective, via the cert item bank."""
    if not _CERT:
        from curriculum_v2.cert.items import CERT_ITEMS
        _CERT['_'] = set()
        for it in CERT_ITEMS:
            for c in it.get('cert') or []:
                if it.get('obj') and c in EX.OBJECTIVES:
                    _CERT.setdefault(it['obj'], set()).add(c)
    return [{'id': c, 'label': f"{EX.EXAMS[c.split(':')[0]]['code']} {c.split(':')[1]}",
             'title': EX.OBJECTIVES[c]['title']} for c in sorted(_CERT.get(obj, ()), key=EX.sort_key)]
from portfolio import build as PB

RUNGS = [('R0', 'Original explanation'), ('R1', 'Plain language'), ('R2', 'Analogy'), ('R3', 'Visual'), ('R4', 'Try it')]
DEMO_DOMAIN = '@lms.local'


def _pct(n, d):
    return round(100.0 * n / d) if d else None


def _answered(o):
    return o.get('kind') != 'reading' and o.get('correct') is not None


def exam_sim_summary(app, sids, students):
    """Exam-Day Simulator & voucher readiness (Option B pass 6): per exam and overall. Drill sittings excluded.
    voucher_ready = students whose best sitting reached VOUCHER READY; mean_score = mean of each student's latest."""
    from curriculum_v2.cert.exams import ALL_EXAMS as EXAMS
    es = app.extensions.get('ciwt_exam_sim')
    A = getattr(es, 'Attempt', None) if es else None
    rows = []
    if A is not None and students:
        rows = (A.query.filter(A.section_id.in_(sids), A.submitted_at.isnot(None), A.mode != 'drill')
                .order_by(A.submitted_at).all())
        rows = [r for r in rows if r.user_id in students]

    def summarise(rs, exam, code, name):
        latest, ready = {}, set()
        for r in rs:
            latest[(r.user_id, r.exam)] = r
            if r.badge == 'ready':
                ready.add(r.user_id)
        cands = {r.user_id for r in rs}
        scores = [r.score for r in latest.values() if r.score is not None]
        return {'exam': exam, 'code': code, 'name': name, 'attempts': len(rs), 'candidates': len(cands),
                'voucher_ready': len(ready), 'voucher_ready_pct': _pct(len(ready), len(cands)),
                'mean_score': round(sum(scores) / len(scores), 1) if scores else None,
                'basis': 'voucher_ready: best sitting per student; mean_score: latest sitting per student and exam; '
                         'submitted non-drill sittings of enrolled students only'}
    per = [summarise([r for r in rows if r.exam == ex], ex, m['code'], m['name']) for ex, m in EXAMS.items()]
    return {'exams': per, 'overall': summarise(rows, 'all', 'all', 'All exams')}


def report(app, db, d, sections):
    from gradebook import histogram
    from mastery import lab_diagnosis as LDX
    from mastery.ladder import define_ladder_models
    mastery = app.extensions.get('ciwt_mastery')
    labs = app.extensions.get('ciwt_lab_progress')
    gb = app.extensions.get('ciwt_gradebook')
    LS = define_ladder_models(db).LadderState
    Enrollment, User, TimeLog = d['Enrollment'], d['User'], d['TimeLog']

    obj_pairs = defaultdict(lambda: {'pairs': 0, 'pre': 0, 'cur': 0, 'attempts': 0, 'lab_n': 0, 'lab_ok': 0})
    p_by_obj = defaultdict(list)
    students, demo_users, section_rows, grades = set(), set(), [], []
    for section in sections:
        uids = [e.user_id for e in Enrollment.query.filter_by(section_id=section.id).all()]
        users = [u for u in (db.session.get(User, i) for i in uids) if u and u.role == 'student']
        students |= {u.id for u in users}
        demo_users |= {u.id for u in users if (u.email or '').endswith(DEMO_DOMAIN)}
        mastered_here = pairs_here = 0
        for u in users:
            try:
                st = mastery.engine.student_state(section, u, log=False)
            except Exception:
                db.session.rollback()
                continue
            for obj, est in st['states'].items():
                obs = sorted((o for o in st['evidence'].get(obj, []) if _answered(o)), key=lambda o: str(o.get('when') or ''))
                if not obs:
                    continue
                mastered = est.get('status') == 'mastered'
                row = obj_pairs[obj]
                row['pairs'] += 1
                row['pre'] += 1 if obs[0].get('correct') else 0
                row['cur'] += 1 if mastered else 0
                row['attempts'] += len(obs)
                labs_obs = [o for o in obs if o.get('kind') == 'lab']
                row['lab_n'] += len(labs_obs)
                row['lab_ok'] += sum(1 for o in labs_obs if o.get('correct'))
                p_by_obj[obj].append(est.get('p', 0))
                pairs_here += 1
                mastered_here += 1 if mastered else 0
        g = []
        if gb:
            try:
                g = [r['grade'] for r in gb.compute(section)['rows'] if r['grade'] is not None]
            except Exception:
                db.session.rollback()
        grades += g
        section_rows.append({'section': section, 'students': len(users), 'pairs': pairs_here,
                             'mastered_pct': _pct(mastered_here, pairs_here),
                             'mean_grade': round(sum(g) / len(g), 1) if g else None})

    sids = [s.id for s in sections] or [0]
    struggles = resolved = exhausted = 0
    by_rung = Counter()
    obj_rungs = defaultdict(Counter)
    for row in LS.query.filter(LS.section_id.in_(sids)).all():
        if row.user_id not in students:
            continue
        ent = LD.entry(row.course, row.label, row.sid) or {}
        if ent.get('obj') and (row.resolved or row.exhausted_at):
            obj_rungs[ent['obj']][row.resolved or 'EX'] += 1
        if (row.misses or 0) > 0 or (row.current or 'R0') != 'R0' or (row.tried_json or '').count('R') > 1:
            struggles += 1
            if row.resolved:
                resolved += 1
                by_rung[row.resolved] += 1
            elif row.exhausted_at:
                exhausted += 1
    ladder = {'struggles': struggles, 'resolved': resolved, 'resolved_pct': _pct(resolved, struggles), 'exhausted': exhausted,
              'rungs': [{'rung': r, 'name': n, 'n': by_rung.get(r, 0), 'pct': _pct(by_rung.get(r, 0), resolved)} for r, n in RUNGS]}

    lab = {'completed': 0, 'vm_completed': 0, 'vm_students': 0, 'analysed': 0, 'diagnosed_first': 0, 'verified': 0}
    if labs and students:
        LP = labs.LabProgress
        vm_students = set()
        for r in LP.query.filter(LP.user_id.in_(list(students)), LP.completed_at.isnot(None)).all():
            lab['completed'] += 1
            if r.lab_id.startswith('linux-vm'):
                lab['vm_completed'] += 1
                vm_students.add(r.user_id)
            try:
                ana = LDX.analyze(labs.events_for(r.user_id, r.lab_id), lab=d['get_lab'](r.lab_id) or {})
            except Exception:
                continue
            ids = {s.get('id') for s in ana.get('strengths', [])}
            lab['analysed'] += 1
            lab['diagnosed_first'] += 'diagnosed_first' in ids
            lab['verified'] += 'verified_before_submit' in ids
        lab['vm_students'] = len(vm_students)
    lab['diagnosed_first_pct'] = _pct(lab['diagnosed_first'], lab['analysed'])
    lab['verified_pct'] = _pct(lab['verified'], lab['analysed'])
    lab['vm_student_pct'] = _pct(lab['vm_students'], len(students))

    cert = PB.cert_readiness({o: {'p': sum(v) / len(v)} for o, v in p_by_obj.items() if v})

    per_student = defaultdict(int)
    if students:
        for t in TimeLog.query.filter(TimeLog.kind == 'study', TimeLog.section_id.in_(sids)).all():
            if t.user_id in students:
                per_student[t.user_id] += t.seconds or 0
    hours = [v / 3600 for v in per_student.values()]

    helix_demo = False
    try:
        from helix.models import define_models  # noqa: F401  (models are already bound on app import)
    except Exception:
        pass
    try:
        HGS = next(m.class_ for m in db.Model.registry.mappers if m.class_.__name__ == 'HelixGazeSession')
        helix_demo = HGS.query.filter(HGS.section_id.in_(sids), HGS.is_demo.is_(True)).count() > 0
    except Exception:
        db.session.rollback()

    objectives = sorted(({'id': o, 'text': OBJECTIVES.get(o, {}).get('text', o), 'pairs': r['pairs'],
                          'pre_pct': _pct(r['pre'], r['pairs']), 'cur_pct': _pct(r['cur'], r['pairs']),
                          'cert': cert_map(o), 'attempts': r['attempts'], 'lab_n': r['lab_n'],
                          'lab_pct': _pct(r['lab_ok'], r['lab_n']),
                          'rungs': {k: obj_rungs[o].get(k, 0) for k in ('R0', 'R1', 'R2', 'R3', 'R4', 'EX')}}
                         for o, r in obj_pairs.items()), key=lambda x: x['id'])
    pairs = sum(r['pairs'] for r in obj_pairs.values())
    return {
        'sections': section_rows, 'students': len(students), 'demo_students': len(demo_users), 'helix_demo': helix_demo,
        'demo': bool(demo_users) or helix_demo,
        'mastery': {'pairs': pairs, 'pre_pct': _pct(sum(r['pre'] for r in obj_pairs.values()), pairs),
                    'cur_pct': _pct(sum(r['cur'] for r in obj_pairs.values()), pairs), 'objectives': objectives},
        'ladder': ladder, 'labs': lab, 'cert': cert, 'exam_sim': exam_sim_summary(app, sids, students),
        'grades': {'n': len(grades), 'mean': round(sum(grades) / len(grades), 1) if grades else None,
                   'median': round(median(grades), 1) if grades else None, 'histogram': histogram(grades) if grades else []},
        'time': {'students': len(hours), 'total_hours': round(sum(hours), 1),
                 'median_hours': round(median(hours), 1) if hours else None},
    }


def write_csv(rep, w):
    w.writerow(['metric', 'scope', 'value', 'denominator', 'note'])
    w.writerow(['data_source', 'all', 'contains demo seed data' if rep['demo'] else 'recorded activity only',
                rep['students'], f"{rep['demo_students']} demo accounts (@lms.local)"])
    m = rep['mastery']
    w.writerow(['objective_right_first_time_pct', 'all', m['pre_pct'], m['pairs'], 'student-objective pairs'])
    w.writerow(['objective_mastered_now_pct', 'all', m['cur_pct'], m['pairs'], 'engine status mastered'])
    for o in m['objectives']:
        w.writerow(['objective_right_first_time_pct', o['id'], o['pre_pct'], o['pairs'], o['text']])
        w.writerow(['objective_mastered_now_pct', o['id'], o['cur_pct'], o['pairs'], o['text']])

    L = rep['ladder']
    w.writerow(['ladder_struggles_resolved_pct', 'all', L['resolved_pct'], L['struggles'], ''])
    for r in L['rungs']:
        w.writerow(['ladder_resolved_by', r['rung'], r['n'], L['resolved'], r['name']])
    lb = rep['labs']
    w.writerow(['lab_diagnosed_first_pct', 'all', lb['diagnosed_first_pct'], lb['analysed'], 'completed labs analysed'])
    w.writerow(['lab_verified_before_submit_pct', 'all', lb['verified_pct'], lb['analysed'], ''])
    w.writerow(['real_vm_lab_completions', 'all', lb['vm_completed'], lb['completed'], 'of all completed labs'])
    w.writerow(['real_vm_students_pct', 'all', lb['vm_student_pct'], rep['students'], ''])
    for e in rep['cert']:
        for dm in e['domains']:
            w.writerow(['cert_domain_readiness_pct', f"{e['exam']} {dm['domain']}", dm['pct'], dm['objectives'], dm['name']])
    g = rep['grades']
    w.writerow(['grade_mean', 'all', g['mean'], g['n'], ''])
    w.writerow(['grade_median', 'all', g['median'], g['n'], ''])
    for h in g['histogram']:
        w.writerow(['grade_band', h['label'], h['n'], g['n'], ''])
    for x in rep['exam_sim']['exams'] + [rep['exam_sim']['overall']]:
        w.writerow(['exam_sim_attempts', x['code'], x['attempts'], x['candidates'], x['name']])
        w.writerow(['exam_sim_voucher_ready_pct', x['code'], x['voucher_ready_pct'], x['candidates'],
                    f"{x['voucher_ready']} candidates VOUCHER READY (simulated)"])
        w.writerow(['exam_sim_mean_scaled_score', x['code'], x['mean_score'], x['candidates'], 'latest sitting, 100-900'])
    t = rep['time']
    w.writerow(['study_hours_total', 'all', t['total_hours'], t['students'], 'logged study time'])
    w.writerow(['study_hours_median', 'all', t['median_hours'], t['students'], 'per student'])


OBJ_COLS = ['course_objective_id', 'course_objective', 'cert_objectives', 'students', 'initial_mastery_pct',
            'current_mastery_pct', 'R0', 'R1', 'R2', 'R3', 'R4', 'exhausted', 'lab_process_pct', 'lab_attempts', 'attempts']


def objective_rows(rep):
    """One row per course objective (the school-ready per-objective export)."""
    for o in rep['mastery']['objectives']:
        yield [o['id'], o['text'], '; '.join(c['label'] for c in o['cert']), o['pairs'], o['pre_pct'], o['cur_pct'],
               *[o['rungs'][k] for k in ('R0', 'R1', 'R2', 'R3', 'R4', 'EX')], o['lab_pct'], o['lab_n'], o['attempts']]


def to_json(rep):
    keep = {k: rep[k] for k in ('students', 'demo', 'demo_students', 'mastery', 'ladder', 'labs', 'grades', 'time', 'exam_sim')}
    keep['sections'] = [{**{k: v for k, v in s.items() if k != 'section'}, 'id': s['section'].id, 'name': s['section'].name}
                        for s in rep['sections']]
    keep['status'] = 'Pending SME review (curriculum mapping)'
    return keep
