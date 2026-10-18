"""Pass 11 extensions: misconceptions, spaced retrieval, struggle help, lab diagnosis, Who needs me, learning plan."""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from curriculum_v2 import misconceptions as MCS
from mastery import lab_diagnosis as LD
from mastery import memory as MEM
from mastery import model as M
from mastery import policy as P

T0 = datetime(2026, 9, 1, 9, 0)
FIX = json.loads((Path(__file__).parent / 'fixtures' / 'lab_events.json').read_text())


@pytest.fixture(scope='module', autouse=True)
def objective_tagged_checks(app, mod):
    with app.app_context():
        mod.sync_pilot_slice()
        mod.db.session.commit()


def _events(name):
    out = []
    for e in FIX[name]:
        e = dict(e)
        e['at'] = datetime.fromisoformat(e['at'])
        out.append(e)
    return out


# ------------------------------------------------------------------ 1. misconceptions
def _bank_items():
    from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload
    from pilot_slice import PILOT_CHECKS, quiz_payload
    import question_bank as QB
    items = {}
    for order in PILOT_CHECKS:
        for it in quiz_payload(order, ''):
            items.setdefault(it.get('bank_id'), []).append(it)
    for order in NETOPS_CHECKS:
        for it in netops_quiz_payload(order):
            items.setdefault(it.get('bank_id'), []).append(it)
    from curriculum_v2.cert.items import CERT_ITEMS          # content round 2: MC-C-* tags on cert items
    from curriculum_v2.exam_supplement import SUPPLEMENT     # content round 5: tags on the X-IT bank and supplement
    from curriculum_v2.itsup_core import EXPANSION
    for pool in (QB.A1, QB.A2, QB.A3, QB.N1, QB.N2, QB.N3, CERT_ITEMS, EXPANSION, SUPPLEMENT):
        for it in pool:
            items.setdefault(it.get('bank_id'), []).append(it)
    return items


def test_every_tag_is_a_real_distractor_of_its_item():
    items = _bank_items()
    assert len(MCS.TAGS) >= 100
    for (bank, distractor), mc in MCS.TAGS.items():
        assert mc in MCS.MISCONCEPTIONS
        cands = [it for it in items.get(bank, []) if it.get('obj') == MCS.MISCONCEPTIONS[mc]['obj']]
        assert cands, (bank, mc)
        for it in cands:
            opts = [MCS._norm(o) for o in it['options']]
            assert MCS._norm(distractor) in opts, (bank, distractor)
            keys = it['correct'] if isinstance(it['correct'], list) else [it['correct']]   # multi-select cert items
            assert MCS._norm(distractor) not in [MCS._norm(k) for k in keys], 'never tag the key'
        assert MCS.MISCONCEPTIONS[mc]['label'] and MCS.MISCONCEPTIONS[mc]['terms']


def test_tag_for():
    item = {'bank_id': 'Q5.1', 'obj': 'IT-5.1', 'correct': 'No usable lease (APIPA)'}
    assert MCS.tag_for(item, 'The DNS server is down') == 'MC-IT5-APIPA-AS-DNS'
    assert MCS.tag_for(item, 'No usable lease (APIPA)') is None
    assert MCS.tag_for(dict(item, obj='NO-1.2'), 'The DNS server is down') is None, 'objective must match'
    assert MCS.tag_for(item, None) is None


def test_apply_misconceptions_targets_the_review():
    low = M.estimate([dict(kind='test', correct=False, when=T0), dict(kind='test', correct=False, when=T0 + timedelta(1))])
    d = P.decide({'IT-5.1': low}, chapters={'IT-5.1': 5}, settings={'enabled': True}, describe=M.describe_counts)
    mcs = {'MC-IT5-APIPA-AS-DNS': {'obj': 'IT-5.1', 'hits': 2, 'last_hit': T0, 'active': True}}
    out = P.apply_misconceptions(d, mcs, settings={'enabled': True}, labels={'MC-IT5-APIPA-AS-DNS': 'X'})
    a = out['actions'][0]
    assert a['type'] == 'misconception' and a['mc'] == 'MC-IT5-APIPA-AS-DNS' and 'X' in a['reasons'][0]
    # repeated misconception on a developing objective -> optional correction; not when adaptivity is off
    dev = M.estimate([dict(kind='quiz', correct=True, when=T0)])
    d2 = P.decide({'IT-5.1': dev}, chapters={'IT-5.1': 5}, settings={'enabled': True}, describe=M.describe_counts)
    o2 = P.apply_misconceptions(d2, mcs, settings={'enabled': True})
    assert o2['actions'][0]['type'] == 'misconception' and not o2['actions'][0]['required']
    assert not P.apply_misconceptions(d2, mcs, settings={'enabled': False})['actions']
    assert not P.apply_misconceptions(d2, {'MC-IT5-APIPA-AS-DNS': dict(mcs['MC-IT5-APIPA-AS-DNS'], hits=1)},
                                      settings={'enabled': True})['actions']


def test_misconception_summary_resolves_on_later_right_answer():
    from mastery.engine import misconception_summary
    ev = {'IT-5.1': [
        {'kind': 'quiz', 'correct': False, 'when': T0, 'mc': 'MC-IT5-APIPA-AS-DNS', 'bank_id': 'Q5.1'},
        {'kind': 'test', 'correct': False, 'when': T0 + timedelta(hours=1), 'mc': 'MC-IT5-APIPA-AS-DNS', 'bank_id': 'Q5.1'},
    ]}
    s = misconception_summary(ev)['MC-IT5-APIPA-AS-DNS']
    assert s['hits'] == 2 and s['active']
    ev['IT-5.1'].append({'kind': 'review_check', 'correct': True, 'when': T0 + timedelta(hours=2), 'bank_id': 'Q5.1'})
    assert not misconception_summary(ev)['MC-IT5-APIPA-AS-DNS']['active']


def test_misconception_correction_flow(app, mod, student, instructor, ids):
    with app.app_context():
        m1 = mod.Module.query.filter_by(course_id=1, order=1).first()
        q = mod.Quiz.query.filter_by(module_id=m1.id).first()
        qs = json.loads(q.questions)
    data = {}
    for i, it in enumerate(qs):
        tagged = [d for (b, d) in MCS.TAGS if b == it.get('bank_id')]
        data[f'q{i}'] = tagged[0] if tagged else it['correct']
    assert student.post(f'/student/quiz/1/{q.id}', data=data).status_code in (302, 303)
    h = student.get('/student/section/1/mastery').data.decode()
    assert student.get('/student').status_code == 200
    page = student.get('/student/section/1/review/IT-1.1').data.decode()
    assert 'The mix-up' in page and 'What the course teaches instead' in page
    t = instructor.get('/instructor/section/1/mastery/today').data.decode()
    assert 'Mix-ups in this class' in t and MCS.MISCONCEPTIONS['MC-IT1-REQ-AS-INC']['label'] in t


# ------------------------------------------------------------------ 2. spaced retrieval
def test_sm2_schedule_math():
    assert MEM.schedule([]) is None
    day = lambda n, ok: {'kind': 'quiz', 'correct': ok, 'when': T0 + timedelta(days=n)}
    s1 = MEM.schedule([day(0, True)])
    assert s1['interval'] == 1 and s1['due'] == T0 + timedelta(days=1)
    s3 = MEM.schedule([day(0, True), day(1, True), day(4, True)])
    assert s3['interval'] == pytest.approx(3 * 2.6) and s3['reps'] == 3
    lapse = MEM.schedule([day(0, True), day(1, True), day(4, False)])
    assert lapse['interval'] == 1 and lapse['lapses'] == 1 and lapse['ease'] == pytest.approx(2.4)
    # forgetting curve: recall is 90% exactly at the due moment
    assert MEM.recall(s1, s1['due']) == pytest.approx(0.9)
    assert MEM.recall(s1, s1['last']) == 1.0
    # same-day answers aggregate (2/3 right = recalled)
    same = MEM.schedule([day(0, True), day(0, True), dict(day(0, False))])
    assert same['reps'] == 1
    # helix and reading never count as retrieval
    assert MEM.schedule([{'kind': 'reading', 'when': T0}, {'kind': 'helix', 'when': T0}]) is None


def test_queue_prefers_overdue_and_tops_up():
    now = T0 + timedelta(days=10)
    st = {f'O{i}': {'last': T0 + timedelta(days=i), 'interval': 1.0, 'due': T0 + timedelta(days=i + 1)} for i in range(12)}
    q = MEM.queue(st, now, minimum=5, maximum=10)
    assert len(q) == 10 and q[0][0] == 'O0' and all(r == 'due' for _o, _s, r in q[:9])
    few = {k: v for k, v in st.items() if k in ('O11', 'O10', 'O9')}
    q2 = MEM.queue(few, now, minimum=5)
    assert [o for o, _s, _r in q2] == ['O9', 'O10', 'O11'] and q2[-1][2] == 'soon'


def test_daily_review_route(app, student, ids):
    api = app.extensions['ciwt_mastery']
    h = student.get('/student/section/1/daily').data.decode()
    assert 'Daily review' in h
    with app.app_context():
        c = api.models.MasteryCheck.query.filter_by(user_id=ids['student1'], kind='daily', completed_at=None).first()
    assert c, 'student1 has answered chapter 1 items, so a daily review exists'
    items = json.loads(c.items_json)
    assert 5 <= len(items) <= 10 or len(items) == len({i['obj'] for i in items})
    assert '"correct"' not in h
    r = student.post('/student/section/1/daily', data={'check_id': c.id, **{f'q{i}': it['correct'] for i, it in enumerate(items)}})
    assert r.status_code == 303
    res = student.get(r.headers['Location']).data.decode()
    assert 'Done for today' in res and 'next review' in res
    # once done, the page goes to the result; home card says done
    assert student.get('/student/section/1/daily').status_code == 302
    assert 'Done for today' in student.get('/student').data.decode()


# ------------------------------------------------------------------ 3. struggle detection
def test_quickcheck_offer_on_time_and_miss_never_reveals_key(app, mod, student, ids):
    api = app.extensions['ciwt_mastery']
    with app.app_context():
        m1 = mod.Module.query.filter_by(course_id=1, order=1).first()
        les = mod.Lesson.query.filter_by(module_id=m1.id).order_by(mod.Lesson.order).first()
    h = student.get(f'/student/module/1/{m1.id}/lesson/{les.id}').data.decode()
    assert 'Quick check (not graded)' in h
    with app.app_context():
        cks = api.models.MasteryCheck.query.filter_by(user_id=ids['student1'], kind='inline', completed_at=None).all()
        pending = [(c.id, json.loads(c.items_json)[0]) for c in cks]
    assert pending
    cid, it = pending[0]
    wrong = next(o for o in it['options'] if o != it['correct'] and not MCS.tag_for(it, o)) if any(
        o != it['correct'] and not MCS.tag_for(it, o) for o in it['options']) else next(o for o in it['options'] if o != it['correct'])
    r = student.post(f'/student/section/1/quickcheck/{cid}', json={'answer': wrong, 'heading': 'Some section', 'dwell_ms': 60000},
                     headers={'Accept': 'application/json'})
    j = r.get_json()
    assert r.status_code == 200 and j['correct'] is False and j['offer'] is True
    assert 'Dismiss' in j['html'] and 'only an offer' in j['html']
    assert student.post(f'/student/section/1/quickcheck/{cid}/dismiss', json={}).get_json()['ok']
    if len(pending) > 1:
        cid2, it2 = pending[1]
        wrong2 = next((o for o in it2['options'] if o != it2['correct'] and not MCS.tag_for(it2, o)), None)
        if wrong2:
            j2 = student.post(f'/student/section/1/quickcheck/{cid2}', json={'answer': wrong2, 'dwell_ms': 2000},
                              headers={'Accept': 'application/json'}).get_json()
            assert j2['offer'] is False, 'a quick miss without a long stay (and no Helix) gets no offer'
    with app.app_context():
        assert api.models.MasteryDecision.query.filter_by(user_id=ids['student1'], action='struggle_offer').count() >= 1
        assert api.models.MasteryDecision.query.filter_by(user_id=ids['student1'], action='struggle_dismissed').count() == 1


def test_struggle_offer_helix_reread_and_never_required(app, mod):
    feats = app.extensions['ciwt_mastery'].features
    with app.test_request_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        u = mod.User.query.filter_by(email='student3@lms.local').first()
        st = app.extensions['ciwt_mastery'].engine.student_state(sec, u, log=False)
        obj = next(o for o in st['cmap']['obj_lesson'])
        assert feats['struggle_offer'](st, obj, 'H', 1000, None) is None
        st2 = dict(st, helix_status='ok', helix={obj: {'reread': ['H'], 'skimmed': []}})
        o = feats['struggle_offer'](st2, obj, 'H', 1000, None)
        assert o and o['source'] == 'helix' and 'only an offer' in ' '.join(o['reasons'])
        st3 = dict(st, helix_status='no_consent', helix={obj: {'reread': ['H'], 'skimmed': []}})
        assert feats['struggle_offer'](st3, obj, 'H', 1000, None) is None, 'Helix data without consent is not used'


# ------------------------------------------------------------------ 4. lab process diagnosis
def _ids(res):
    return {p['id'] for p in res['patterns']}


def test_lab_diagnosis_patterns():
    lab = FIX['lab']
    eff = LD.diagnose(_events('efficient'), lab)
    assert _ids(eff) == {'efficient'} and eff['summary']['completed']
    g = LD.diagnose(_events('guessing'), lab)
    assert 'trial_and_error' in _ids(g)
    tae = next(p for p in g['patterns'] if p['id'] == 'trial_and_error')
    assert '4 of 6 actions' in tae['evidence'][0] and tae['tip']
    nv = LD.diagnose(_events('no_verify'))
    assert 'never_verifies' in _ids(nv)
    sk = LD.diagnose(_events('skipped'), lab)
    assert {'skipped_step', 'hint_reliance'} <= _ids(sk)
    assert 'Renew the lease' in next(p for p in sk['patterns'] if p['id'] == 'skipped_step')['evidence'][0]
    rp = LD.diagnose(_events('repeats'))
    assert 'repeats_without_change' in _ids(rp)
    assert LD.diagnose([], lab)['patterns'] == []
    assert LD.struggling(g) and not LD.struggling(eff)


def test_lab_diagnosis_accepts_objects():
    from types import SimpleNamespace
    evs = [SimpleNamespace(attempt=1, **e) for e in _events('no_verify')]
    assert 'never_verifies' in _ids(LD.diagnose(evs))


# ------------------------------------------------------------------ 5. who needs me
def test_who_needs_me_reasons_and_actions(app, mod, instructor, instructor2, student, ids):
    h = instructor.get('/instructor/section/1/mastery/today').data.decode()
    assert 'Who needs me' in h and 'No risk score' in h
    assert 'risk score' not in h.replace('No risk score', '')
    assert instructor2.get('/instructor/section/1/mastery/today').status_code == 403
    assert student.get('/instructor/section/1/mastery/today').status_code == 403
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    r = instructor.post('/instructor/section/1/mastery/checkin', data={'user_id': ids['student1'], 'on_date': tomorrow, 'note': 'subnetting'})
    assert r.status_code == 303
    assert instructor.post('/instructor/section/1/mastery/checkin', data={'user_id': ids['student1'], 'on_date': '2001-01-01'}).status_code == 303
    api = app.extensions['ciwt_mastery']
    with app.app_context():
        rows = api.models.MasteryCheckin.query.filter_by(user_id=ids['student1']).all()
        assert len(rows) == 1 and rows[0].note == 'subnetting'
    assert 'Check-in with your instructor' in student.get('/student/section/1/plan').data.decode()


def test_needs_me_reason_rules(app, mod):
    feats = app.extensions['ciwt_mastery'].features
    with app.test_request_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        u = mod.User.query.filter_by(email='student5@lms.local').first()
        st = app.extensions['ciwt_mastery'].engine.student_state(sec, u, log=False)
        reasons, _last = feats['needs_me_reasons'](st, u)
        kinds = [r['kind'] for r in reasons]
        assert kinds == sorted(kinds, key=['stuck', 'misconception', 'missed_review', 'drop', 'lab', 'inactive'].index)
        assert all(r['text'] for r in reasons)


# ------------------------------------------------------------------ 6. learning plan
def test_learning_plan_backward_plan(app, mod, student, ids):
    exam = (date.today() + timedelta(days=28)).isoformat()
    assert student.post('/student/section/1/plan', data={'exam_date': '2000-01-01'}).status_code == 303
    r = student.post('/student/section/1/plan', data={'exam_date': exam, 'review_pref': 'practice', 'daily_size': '6'})
    assert r.status_code == 303
    h = student.get('/student/section/1/plan').data.decode()
    assert 'not</strong> a prediction' in h and 'Week 4' in h and 'objectives a week' in h
    assert 'likely to pass' not in h.lower() and 'chance of passing' not in h.lower()
    # the chosen review style is used when the student opens a review themselves
    page = student.get('/student/section/1/review/IT-1.4').data.decode()
    assert 'Practice questions only, as you chose' in page or 'Fix a mix-up' in page
    feats = app.extensions['ciwt_mastery'].features
    with app.test_request_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        u = mod.db.session.get(mod.User, ids['student1'])
        st = app.extensions['ciwt_mastery'].engine.student_state(sec, u, log=False)
        pl = app.extensions['ciwt_mastery'].models.LearningPlan.query.filter_by(user_id=u.id).first()
        plan = feats['build_plan'](st, pl)
        assert plan['total'] == len(st['cmap']['objs'])
        assert len(plan['weeks']) == 4
        assert sum(len(w['targets']) for w in plan['weeks']) == len(plan['remaining'])


def test_every_logged_action_has_a_plain_label():
    """The instructor log shows a readable label for every decision kind the engine or features write."""
    import re, pathlib
    import mastery
    root = pathlib.Path(mastery.__file__).parent
    src = ''.join((root / f).read_text() for f in ('features.py', '__init__.py'))
    kinds = set(re.findall(r"eng\.log\([^\n]*?, '([a-z_]+)', '(?:student|instructor|engine)'", src))
    kinds |= {'misconception', 'review', 'alt_review', 'helix_offer', 'testout_offer', 'stuck_flag',
              'checkin_scheduled', 'struggle_offer'}
    missing = sorted(k for k in kinds if k not in mastery.ACTION_LABEL)
    assert not missing, missing
