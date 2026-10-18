#!/usr/bin/env python3
"""Adaptive end-to-end semester simulation (pass 13) — a SYNTHETIC check, not evidence of learning gains.

    DATABASE_URL=sqlite:////tmp/sim.db ./venv/bin/python tools/semester_sim.py out.json [--days 28] [--seed 13]

Creates a clearly labelled synthetic class ("SYNTHETIC SIMULATION — not real students") on ITSUP with 20
synthetic accounts (simNN@synthetic.invalid) whose answers are drawn from fixed per-objective probabilities.
They work through chapters 1–4 for four simulated weeks through the real HTTP routes (lessons, study-time
heartbeats, chapter checks, daily review, reviews, mastery checks, one graded knowledge test). Lab completions
are written directly (the lab simulator itself is covered by the lab e2e suites).

Time: after each simulated day every timestamp belonging to the synthetic accounts is moved back one day, so the
engine (which compares stored times with the real clock) sees the history age exactly as it would.

It verifies: (1) reviews are inserted for objectives a student is weak on; (2) strong students are offered and
pass mastery checks (test-outs) and their path skips the chapter; (3) spaced review comes due; (4) "Who needs me"
and the briefing rank the students who need help; (5) no adaptive action changes a grade (gradebook CSV is
identical before and after each day's adaptive actions, and no adaptive route writes graded rows).
Refuses to run against ciwt_lms.db.
"""
import argparse
import csv
import io
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
URL = os.environ.get('DATABASE_URL', '')
if not URL or os.path.realpath(URL.split('sqlite:///')[-1]) == os.path.realpath(os.path.join(ROOT, 'ciwt_lms.db')):
    raise SystemExit('Set DATABASE_URL to a COPY of the database; this tool writes synthetic accounts and activity.')

SECTION_NAME = 'SYNTHETIC SIMULATION — not real students'
EMAIL = 'sim{:02d}@synthetic.invalid'
PASSWORD = 'synthetic-not-real'
PROFILES = (['strong'] * 4 + ['good'] * 5 + ['mixed'] * 5 + ['weak'] * 4 + ['disengaged'] * 2)
P_BASE = {'strong': 0.95, 'good': 0.82, 'mixed': 0.8, 'weak': 0.35, 'disengaged': 0.6}
MC_PRONE = {'weak': 0.85, 'mixed': 0.6}        # chance a wrong answer is the tagged misconception distractor
DISENGAGE_DAY = 9
GRADED_TEST_DAY = 10                           # week 2, Thursday-ish


def run(days=28, seed=13, chapters=(1, 2, 3, 4), log=print):
    import app as A
    from curriculum_v2 import misconceptions as MCS
    import interactive_labs as IL
    app, db = A.app, A.db
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    api = app.extensions['ciwt_mastery']
    eng, MM = api.engine, api.models
    rng = random.Random(seed)
    R = {'synthetic': True, 'note': 'Synthetic cohort with fixed answer probabilities; checks engine behaviour only, '
         'not learning gains.', 'seed': seed, 'days': days, 'checks': [], 'events': Counter(), 'daily_why': Counter()}

    def check(name, ok, detail=None):
        R['checks'].append({'check': name, 'ok': bool(ok), 'detail': detail})
        log(('PASS ' if ok else 'FAIL ') + name + ('' if ok or detail is None else f' — {str(detail)[:400]}'))

    with app.app_context():
        course = A.Course.query.filter_by(code='ITSUP').first()
        instructor = A.User.query.filter_by(email='instructor@lms.local').first()
        sec = A.ClassSection(name=SECTION_NAME, course_id=course.id, instructor_id=instructor.id, max_students=40, is_active=True)
        db.session.add(sec)
        db.session.flush()
        users = []
        for n, prof in enumerate(PROFILES, 1):
            u = A.User.query.filter_by(email=EMAIL.format(n)).first()
            if not u:
                u = A.User(email=EMAIL.format(n), first_name='Synthetic', last_name=f'student {n:02d} ({prof})', role='student')
                u.set_password(PASSWORD)
                db.session.add(u)
                db.session.flush()
            db.session.add(A.Enrollment(user_id=u.id, section_id=sec.id))
            users.append((u.id, prof))
        mods = {m.order: m for m in A.Module.query.filter_by(course_id=course.id) if m.order in chapters}
        for m in mods.values():
            db.session.add(A.ContentRelease(section_id=sec.id, content_type='module', content_id=m.id, is_active=True,
                                            activated_by=instructor.id, activated_at=A.utcnow()))
        test1 = A.KnowledgeTest.query.filter_by(course_id=course.id).order_by(A.KnowledgeTest.order).first()
        db.session.add(A.ContentRelease(section_id=sec.id, content_type='test', content_id=test1.id, is_active=True,
                                        activated_by=instructor.id, activated_at=A.utcnow()))
        db.session.commit()
        sid = sec.id
        cmap = eng.course_map(sec)
        objs = [o for o in cmap['objs'] if cmap['objs'][o]['chapter'] in chapters]
        with_checks = sorted({i['obj'] for i in cmap['check_items'] if i['obj'] in objs})
        ability, weak_objs = {}, {}
        for uid, prof in users:
            p = {o: P_BASE[prof] for o in objs}
            if prof == 'mixed':
                weak_objs[uid] = rng.sample([o for o in with_checks if cmap['objs'][o]['chapter'] <= 2], 2)
                for o in weak_objs[uid]:
                    p[o] = 0.15
            ability[uid] = p
        quiz_by_ch = {q['chapter']: q for q in cmap['quizzes'].values() if q['chapter'] in chapters}
        sim_ids = [u for u, _ in users]
        R['cohort'] = {prof: n for prof, n in Counter(PROFILES).items()}
        R['weak_objectives'] = {str(k): v for k, v in weak_objs.items()}

    # ---------------------------------------------------------------- helpers
    def client(uid):
        c = app.test_client()
        with app.app_context():
            email = db.session.get(A.User, uid).email
        r = c.post('/login', data={'email': email, 'password': PASSWORD})
        assert r.status_code in (302, 303)
        return c

    clients = {uid: client(uid) for uid in sim_ids}
    staff = app.test_client()
    staff.post('/login', data={'email': 'instructor@lms.local', 'password': 'teach123'})
    prof_of = dict(users)

    def answer(uid, it):
        """Pick an answer from the synthetic ability; wrong answers favour a tagged misconception distractor."""
        opts, key = it['options'], it['correct']
        p = ability[uid].get(it.get('obj'), P_BASE[prof_of[uid]])
        if rng.random() < p:
            return key
        tagged = [o for o in opts if o != key and MCS.TAGS.get((it.get('bank_id'), o))]
        if tagged and rng.random() < MC_PRONE.get(prof_of[uid], 0.3):
            return tagged[0]
        return rng.choice([o for o in opts if o != key])

    def served_items(check_id):
        with app.app_context():
            c = db.session.get(MM.MasteryCheck, check_id)
            return json.loads(c.items_json or '[]')

    def post_check(uid, url, check_id):
        items = served_items(check_id)
        form = {'check_id': str(check_id)}
        for i, it in enumerate(items):
            form[f'q{i}'] = answer(uid, it)
        r = clients[uid].post(url, data=form)
        assert r.status_code in (302, 303), (url, r.status_code)
        return r

    def check_id_from(html):
        m = re.search(r'name="check_id" value="(\d+)"', html)
        return int(m.group(1)) if m else None

    def state(uid):
        with app.test_request_context():
            s = db.session.get(A.ClassSection, sid)
            return eng.student_state(s, db.session.get(A.User, uid), log=True)

    def grades_csv():
        r = staff.get(f'/instructor/section/{sid}/gradebook.csv')
        assert r.status_code == 200
        return r.get_data(as_text=True)

    def graded_rows():
        with app.app_context():
            ta = sorted((a.id, a.user_id, a.score, str(a.completed_at)[:16]) for a in
                        A.TestAttempt.query.filter(A.TestAttempt.user_id.in_(sim_ids)))
            GO = getattr(A, 'GradeOverride', None)
            n_ov = db.session.execute(db.text('SELECT count(*) FROM grade_override WHERE section_id=:s'), {'s': sid}).scalar()
            return ta, n_ov

    def age_one_day():
        """Move every timestamp owned by the synthetic accounts back one day (the class's releases too)."""
        ids = ','.join(str(i) for i in sim_ids)
        with app.app_context():
            for t in db.metadata.sorted_tables:
                cols = {c.name: c for c in t.columns}
                dt = [c for c, col in cols.items() if col.type.__class__.__name__ in ('DateTime',)]
                if not dt:
                    continue
                if 'user_id' in cols:
                    where = f'user_id IN ({ids})'
                elif t.name == 'class_section':
                    continue
                elif 'section_id' in cols:
                    where = f'section_id = {sid}'
                else:
                    continue
                for c in dt:
                    db.session.execute(db.text(f'UPDATE "{t.name}" SET "{c}" = datetime("{c}", \'-1 day\') '
                                               f'WHERE "{c}" IS NOT NULL AND {where}'))
            # the daily review is keyed by calendar day ("DAY-YYYY-MM-DD"); age that key with the timestamps
            for t in ('mastery_check', 'mastery_decision'):
                db.session.execute(db.text(f"UPDATE {t} SET target = 'DAY-' || date(substr(target, 5), '-1 day') "
                                           f"WHERE target LIKE 'DAY-____-__-__' AND user_id IN ({ids})"))
            db.session.commit()

    # ---------------------------------------------------------------- the semester
    tested_out = defaultdict(set)
    testout_offered = defaultdict(set)
    grade_changes = []
    reviews_done = Counter()
    due_seen = defaultdict(int)
    for day in range(days):
        week, wd = day // 7, day % 7
        ch = chapters[min(week, len(chapters) - 1)]
        active = [u for u in sim_ids if not (prof_of[u] == 'disengaged' and day >= DISENGAGE_DAY)]
        if wd >= 5:
            age_one_day()
            continue
        # ---- adaptive, before the week's reading: a strong student offered the chapter's mastery check takes it
        pre_csv, pre_rows = grades_csv(), graded_rows()
        for uid in active:
            if wd != 0 or ch in tested_out[uid]:
                continue
            st = state(uid)
            for o in st['decision']['testout']:
                testout_offered[uid].add(o['chapter'])
            if prof_of[uid] == 'strong':
                rows_ = list(st['decision']['rows'].values())
                R.setdefault('strong_mondays', []).append({
                    'day': day, 'user': uid, 'upcoming': st['upcoming'], 'offers': [o['chapter'] for o in st['decision']['testout']],
                    'states': dict(Counter(r['state'] for r in rows_))})
                offer = next((o for o in st['decision']['testout'] if o['chapter'] == ch), None)
                if offer:
                    c = clients[uid]
                    r = c.get(f'/student/section/{sid}/testout/{ch}')
                    cid = check_id_from(r.get_data(as_text=True))
                    if cid:
                        post_check(uid, f'/student/section/{sid}/testout/{ch}', cid)
                        R['events']['testouts'] += 1
                        with app.app_context():
                            if db.session.get(MM.MasteryCheck, cid).passed:
                                tested_out[uid].add(ch)
        if (pre_csv, pre_rows) != (grades_csv(), graded_rows()):
            grade_changes.append((day, 'test-out'))
        # ---- non-adaptive work (lessons, check, lab, graded test)
        for uid in active:
            c = clients[uid]
            if wd == 0 and ch not in tested_out[uid]:
                for les in cmap['by_ch'][ch]:
                    r = c.get(f'/student/module/{sid}/{les["module_id"]}/lesson/{les["id"]}')
                    assert r.status_code in (200, 302), r.status_code
                    beats = 3 if prof_of[uid] != 'weak' else 6
                    for _ in range(beats):
                        c.post('/time/study', json={'lesson_id': les['id'], 'section_id': sid, 'seconds': 120})
                R['events']['lesson_reads'] += len(cmap['by_ch'][ch])
            if wd == 1 and ch not in tested_out[uid]:
                qz = quiz_by_ch[ch]
                form = {f'q{i}': answer(uid, it) for i, it in enumerate(qz['items'])}
                r = c.post(f'/student/quiz/{sid}/{qz["id"]}', data=form)
                assert r.status_code in (302, 303), r.status_code
                R['events']['chapter_checks'] += 1
            if wd == 2:
                lab = (IL.CHAPTER_LABS.get(('ITSUP', ch)) or [None])[0]
                if lab and rng.random() < (0.5 if prof_of[uid] == 'weak' else 0.9):
                    with app.app_context():
                        db.session.add(A.LabCompletion(user_id=uid, lab_id=lab, section_id=sid,
                                                       done_json=json.dumps(['submitted']), completed_at=A.utcnow()))
                        db.session.commit()
                    R['events']['labs'] += 1
            if day == GRADED_TEST_DAY:
                c.get(f'/student/test/{sid}/{test1.id}')
                with app.app_context():
                    qs = json.loads(db.session.get(A.KnowledgeTest, test1.id).questions or '[]')
                form = {f'q{i}': answer(uid, q) if q.get('options') else '' for i, q in enumerate(qs)}
                r = c.post(f'/student/test/{sid}/{test1.id}', data=form)
                assert r.status_code in (200, 302, 303), r.status_code
                R['events']['graded_tests'] += 1
        before_csv, before_rows = grades_csv(), graded_rows()
        # ---- adaptive work (mastery checks, daily review, reviews)
        for uid in active:
            c = clients[uid]
            st = state(uid)
            for o in st['decision']['testout']:
                testout_offered[uid].add(o['chapter'])
            if wd in (0, 1, 2, 3, 4) and day >= 1:
                with app.test_request_context():
                    s = db.session.get(A.ClassSection, sid)
                    plan = api.features['daily_plan'](eng.student_state(s, db.session.get(A.User, uid), log=False))
                for it in plan:
                    R['daily_why'][it['why']] += 1
                    if it['why'] == 'due':
                        due_seen[uid] += 1
                r = c.get(f'/student/section/{sid}/daily')
                cid = check_id_from(r.get_data(as_text=True))
                if cid:
                    post_check(uid, f'/student/section/{sid}/daily', cid)
                    R['events']['daily_reviews'] += 1
            if wd in (1, 3):
                st = state(uid)
                acts = [a for a in st['decision']['actions'] if a['type'] in ('review', 'alt_review', 'misconception')]
                for a in acts[:2]:
                    r = c.get(f'/student/section/{sid}/review/{a["obj"]}')
                    cid = check_id_from(r.get_data(as_text=True))
                    if cid:
                        post_check(uid, f'/student/section/{sid}/review/{a["obj"]}', cid)
                        reviews_done[(uid, a['obj'])] += 1
                        R['events']['reviews'] += 1
        after_csv, after_rows = grades_csv(), graded_rows()
        if before_csv != after_csv or before_rows != after_rows:
            grade_changes.append(day)
        age_one_day()

    # ---------------------------------------------------------------- verification
    with app.test_request_context():
        s = db.session.get(A.ClassSection, sid)
        D = MM.MasteryDecision
        rev_actions = ('review', 'alt_review', 'misconception')
        missing = []
        for uid, wobjs in weak_objs.items():
            for o in wobjs:
                if not D.query.filter(D.section_id == sid, D.user_id == uid, D.target == o, D.action.in_(rev_actions)).count():
                    missing.append((uid, o))
        check('reviews were inserted for every objective a "mixed" student is weak on '
              f'({sum(len(v) for v in weak_objs.values())} weak objective/student pairs)', not missing, missing)
        strong = [u for u in sim_ids if prof_of[u] == 'strong']
        weak = [u for u in sim_ids if prof_of[u] == 'weak']
        check('every strong student was offered a mastery check and passed at least one (test-out)',
              all(tested_out[u] for u in strong), {u: sorted(tested_out[u]) for u in strong})
        skip_ok = []
        for u in strong:
            st = eng.student_state(s, db.session.get(A.User, u), log=False)
            nl = st['next_lesson']
            skip_ok.append(not nl or nl['chapter'] not in tested_out[u])
        check('after a test-out the student path no longer sends the student into that chapter', all(skip_ok))
        check('no weak student passed a mastery check', not any(tested_out[u] for u in weak),
              {u: sorted(tested_out[u]) for u in weak if tested_out[u]})
        check('spaced review came due: daily review served items marked "due" to every engaged student',
              all(due_seen[u] > 0 for u in sim_ids if prof_of[u] != 'disengaged'),
              {u: due_seen[u] for u in sim_ids if prof_of[u] != 'disengaged' and not due_seen[u]})
        _cmap, _rows, people = api.features['needs_me'](s)
        need_ids = [p['user'].id for p in people]
        focus_ids = [p['user'].id for p in people if p['kinds'] != ['inactive']]
        disengaged = [u for u in sim_ids if prof_of[u] == 'disengaged']
        R['needs_me'] = [{'user': p['user'].id, 'profile': prof_of[p['user'].id], 'kinds': p['kinds']} for p in people]
        check('"Who needs me" lists every weak student with a non-inactivity reason', all(u in focus_ids for u in weak),
              [u for u in weak if u not in focus_ids])
        check('"Who needs me" flags both disengaged students as inactive',
              all(any(p['user'].id == u and 'inactive' in p['kinds'] for p in people) for u in disengaged), R['needs_me'])
        top = need_ids[:len(weak) + len(disengaged)]
        check('the top of "Who needs me" is weak, mixed or disengaged students — never a strong one',
              not [u for u in top if prof_of[u] in ('strong',)], [(u, prof_of[u]) for u in top])
        check('no strong student is in "Who needs me"', not [u for u in strong if u in need_ids],
              [(p['user'].id, p['kinds']) for p in people if p['user'].id in strong])
        b = api.briefing['build'](s)
        studs = [t for t in b['todo'] if t['kind'] == 'student']
        R['briefing_todo'] = [{'kind': t['kind'], 'title': t['title'], 'score': t['score']} for t in b['todo']]
        check('the briefing to-do names only students who need help (weak, mixed or disengaged)',
              all(prof_of[t['user'].id] in ('weak', 'mixed', 'disengaged') for t in studs) and bool(b['todo']),
              R['briefing_todo'])
        bfocus = [p['user'].id for p in b['focus']]
        check('the briefing\'s focus list includes every weak student and no strong one',
              all(u in bfocus for u in weak) and not [u for u in strong if u in bfocus], [(u, prof_of[u]) for u in bfocus])
        check('no adaptive action changed a grade (gradebook CSV and graded rows identical before/after on every day)',
              not grade_changes, grade_changes)
        n_mastery_rows = MM.MasteryCheck.query.filter_by(section_id=sid).count()
        R['events'] = dict(R['events'])
        R['events']['mastery_check_rows'] = n_mastery_rows
        R['daily_why'] = dict(R['daily_why'])
        by_prof = defaultdict(list)
        for u in sim_ids:
            st = eng.student_state(s, db.session.get(A.User, u), log=False)
            rows = st['decision']['rows']
            by_prof[prof_of[u]].append(sum(1 for o in objs if rows[o]['state'] == 'mastered'))
        R['mastered_objectives_by_profile'] = {k: sorted(v) for k, v in by_prof.items()}
        R['section_id'] = sid
        R['testouts_passed'] = {str(u): sorted(v) for u, v in tested_out.items() if v}
        R['testout_offered'] = {str(u): sorted(v) for u, v in testout_offered.items() if v}
    R['summary'] = {'passed': sum(c['ok'] for c in R['checks']), 'total': len(R['checks'])}
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--days', type=int, default=28)
    ap.add_argument('--seed', type=int, default=13)
    a = ap.parse_args()
    R = run(a.days, a.seed)
    with open(a.out, 'w') as f:
        json.dump(R, f, indent=1, default=str)
    print(f"{R['summary']['passed']}/{R['summary']['total']} checks passed — synthetic simulation, not evidence of learning")
    return 0 if R['summary']['passed'] == R['summary']['total'] else 1


if __name__ == '__main__':
    sys.exit(main())
