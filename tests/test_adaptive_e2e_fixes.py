"""Fixes from the adaptive mastery end-to-end pass (Oct 18 2026, ADAPTIVE_E2E.md), plus engine paths the
earlier suites did not cover. Each test names the bug it guards."""
import json
from datetime import datetime, timedelta

import pytest

from curriculum_v2 import misconceptions as MCS
from mastery import model as M
from mastery import policy as P

T0 = datetime(2026, 9, 1, 9, 0)
MC = 'MC-IT5-APIPA-AS-DNS'
ON = {'enabled': True, 'testout': True}


def _low():
    return M.estimate([dict(kind='test', correct=False, when=T0), dict(kind='test', correct=False, when=T0 + timedelta(1))])


def _mcs(hits=2):
    return {MC: {'obj': 'IT-5.1', 'hits': hits, 'last_hit': T0 + timedelta(1), 'active': True}}


def _decide(history):
    d = P.decide({'IT-5.1': _low()}, chapters={'IT-5.1': 5}, settings=ON, history=history, describe=M.describe_counts)
    return P.apply_misconceptions(d, _mcs(), settings=ON, history=history, labels={MC: 'APIPA means DNS'})


# ------------------------------------------------------------------ pure policy
def test_first_review_with_a_mixup_is_the_correction():
    a = _decide({})['actions'][0]
    assert a['type'] == 'misconception' and a['mc'] == MC


def test_after_the_correction_is_done_the_next_review_is_the_alternate_explanation():
    """Bug: the second review said "explained another way (summary, analogy, worked example)" but served the
    same mix-up correction again, because every review/alt review with an active mix-up became a correction."""
    hist = {'IT-5.1': {'reviews_done': 1, 'last_review_at': T0 + timedelta(2), 'mc_done': {MC}}}
    out = _decide(hist)
    a = out['actions'][0]
    assert a['type'] == 'alt_review' and 'mc' not in a and a['mc_seen'] == MC
    assert 'APIPA means DNS' in a['reasons'][0] and 'not repeated' in a['reasons'][0]
    assert any('explained another way' in r for r in a['reasons'])
    assert out['rows']['IT-5.1']['action'] is a


def test_alternate_explanation_also_after_a_correction_of_a_different_mixup():
    # objectives often carry several mix-ups (IT-1.1 has four): one completed correction is enough
    hist = {'IT-5.1': {'reviews_done': 1, 'last_review_at': T0 + timedelta(2), 'mc_done': {'MC-OTHER'}}}
    a = _decide(hist)['actions'][0]
    assert a['type'] == 'alt_review' and a['mc_seen'] == MC


def test_alt_review_turned_into_a_correction_does_not_promise_the_alternate_explanation():
    # first review was a plain review (no mix-up known then); now a mix-up shows -> correction, honest reasons
    hist = {'IT-5.1': {'reviews_done': 1, 'last_review_at': T0 + timedelta(2)}}
    a = _decide(hist)['actions'][0]
    assert a['type'] == 'misconception' and a['mc'] == MC
    assert not any('explained another way' in r for r in a['reasons'])
    assert any('already did one review' in r for r in a['reasons'])


def test_stuck_objective_gets_no_third_insertion_from_a_repeated_mixup():
    """Bug: after two completed reviews (stuck), a repeated mix-up still inserted an optional correction,
    contradicting the rule and the student message that the instructor takes it from here."""
    hist = {'IT-5.1': {'reviews_done': 2, 'last_review_at': T0 + timedelta(3), 'mc_done': {MC}}}
    out = _decide(hist)
    assert out['stuck'] == ['IT-5.1'] and out['actions'] == []
    assert out['rows']['IT-5.1']['action'] is None


def test_standalone_mixup_offer_is_marked_optional():
    dev = M.estimate([dict(kind='quiz', correct=True, when=T0)])
    d = P.decide({'IT-5.1': dev}, chapters={'IT-5.1': 5}, settings=ON, describe=M.describe_counts)
    a = P.apply_misconceptions(d, _mcs(), settings=ON)['actions'][0]
    assert a['type'] == 'misconception' and a['offer'] is True and not a['required']
    # converted reviews are not "offers": they are inserted before the next lesson
    assert 'offer' not in _decide({})['actions'][0]


def test_forced_review_after_a_done_correction_is_the_alternate_explanation_and_stays_required():
    hist = {'IT-5.1': {'reviews_done': 1, 'last_review_at': T0 + timedelta(2), 'mc_done': {MC}}}
    ov = {'IT-5.1': {'kind': 'force_review', 'at': T0 + timedelta(5), 'note': 'again please'}}
    d = P.decide({'IT-5.1': _low()}, chapters={'IT-5.1': 5}, settings=ON, overrides=ov, history=hist, describe=M.describe_counts)
    a = P.apply_misconceptions(d, _mcs(), settings=ON, history=hist)['actions'][0]
    assert a['type'] == 'alt_review' and a['required'] and a['source'] == 'instructor'


def test_clear_override_returns_to_the_engine_and_chapter_lock_blocks_testout():
    strong = M.estimate([dict(kind='testout', correct=True, when=T0 + timedelta(minutes=i)) for i in range(4)])
    rows = [{'state': 'mastered', 'answered': True}] * 3
    assert P.testout_offer(4, rows=rows, settings=ON, overrides={}, testout_history={})['source'] == 'engine'
    assert P.testout_offer(4, rows=rows, settings=ON, overrides={'CH-4': {'kind': 'lock'}}, testout_history={}) is None
    # an objective lock does not make an engine review required unless the estimate needs review
    d = P.decide({'IT-5.1': strong}, chapters={'IT-5.1': 5}, settings=ON, overrides={'IT-5.1': {'kind': 'lock'}})
    assert d['actions'] == [] and d['rows']['IT-5.1']['state'] == 'mastered'


def test_failed_testouts_stop_the_engine_offer_after_three_attempts_but_unlock_reopens():
    rows = [{'state': 'mastered', 'answered': True}] * 3
    th = {4: {'attempts': 3, 'passed': False}}
    assert P.testout_offer(4, rows=rows, settings=ON, overrides={}, testout_history=th) is None
    assert P.testout_offer(4, rows=rows, settings=ON, overrides={'CH-4': {'kind': 'unlock'}}, testout_history=th)
    assert P.testout_offer(4, rows=rows, settings=ON, overrides={'CH-4': {'kind': 'unlock'}},
                           testout_history={4: {'attempts': 1, 'passed': True}}) is None


# ------------------------------------------------------------------ through the routes
@pytest.fixture(scope='module', autouse=True)
def objective_tagged_checks(app, mod):
    with app.app_context():
        mod.sync_pilot_slice()
        mod.db.session.commit()


EMAIL = 'student12@lms.local'


def _clean(app, mod, uid):
    api = app.extensions['ciwt_mastery']
    with app.app_context():
        for t in (api.models.MasteryDecision, api.models.MasteryCheck, api.models.MasteryOverride):
            t.query.filter_by(section_id=1, user_id=uid).delete()
        mod.QuizAttempt.query.filter_by(user_id=uid).delete()
        mod.TestAttempt.query.filter_by(user_id=uid, section_id=1).delete()
        mod.TimeLog.query.filter_by(user_id=uid, kind='study').delete()
        mod.db.session.commit()


@pytest.fixture
def s12(app, mod):
    """student12 from a clean slate in class 1. The session DB is shared, so the graded-test attempts this
    clears are restored afterwards and the rows these tests add are removed (other suites count class results)."""
    with app.app_context():
        u = mod.User.query.filter_by(email=EMAIL).first()
        assert mod.Enrollment.query.filter_by(user_id=u.id, section_id=1).first()
        uid = u.id
        cols = [c.name for c in mod.TestAttempt.__table__.columns]
        saved = [{k: getattr(t, k) for k in cols} for t in mod.TestAttempt.query.filter_by(user_id=uid, section_id=1)]
    _clean(app, mod, uid)
    c = app.test_client()
    r = c.post('/login', data={'email': EMAIL, 'password': 'student123'})
    assert r.status_code in (302, 303)
    c.uid = uid
    yield c
    _clean(app, mod, uid)
    with app.app_context():
        for row in saved:
            mod.db.session.add(mod.TestAttempt(**row))
        mod.db.session.commit()


def _chapter1(app, mod):
    with app.app_context():
        m1 = mod.Module.query.filter_by(course_id=1, order=1).first()
        q = mod.Quiz.query.filter_by(module_id=m1.id).first()
        return q.id, json.loads(q.questions)


def _open_review(app, uid, obj):
    with app.app_context():
        MC_ = app.extensions['ciwt_mastery'].models.MasteryCheck
        c = (MC_.query.filter_by(section_id=1, user_id=uid, kind='review', target=obj, completed_at=None)
             .order_by(MC_.id.desc()).first())
        return c.id, json.loads(c.items_json), c.variant


def _miss_review(app, client, obj):
    cid, items, variant = _open_review(app, client.uid, obj)
    data = {'check_id': cid}
    for i, it in enumerate(items):
        data[f'q{i}'] = next(o for o in it['options'] if o != it['correct'])
    assert client.post(f'/student/section/1/review/{obj}', data=data).status_code == 303
    return variant


def test_route_mixup_then_alternate_explanation_then_stuck(app, mod, s12):
    qid, qs = _chapter1(app, mod)
    data = {}
    for i, it in enumerate(qs):
        tagged = [d for (b, d) in MCS.TAGS if b == it.get('bank_id') and d in it['options']]
        data[f'q{i}'] = tagged[0] if tagged else next(o for o in it['options'] if o != it['correct'])
    assert s12.post(f'/student/quiz/1/{qid}', data=data).status_code in (302, 303)
    home = s12.get('/student/section/1').data.decode()
    assert 'Fix a mix-up' in home
    # the inserted correction carries the same badge as other inserted reviews, and the same time as its page
    step = home.split('Fix a mix-up', 1)[1].split('</li>', 1)[0]
    assert 'Inserted before your next lesson' in step and 'about 2 min' in step
    obj = 'IT-1.1'
    page = s12.get(f'/student/section/1/review/{obj}').data.decode()
    assert 'The mix-up' in page and 'about 2 minutes' in page
    assert _miss_review(app, s12, obj).startswith('mc:')
    # second time: the alternate explanation it promises, with the mix-up still named
    page = s12.get(f'/student/section/1/review/{obj}').data.decode()
    assert 'Another way to see it' in page and 'different angle' in page
    assert 'You already worked through a mix-up correction' in page and 'explained another way' in page
    assert 'Fix: ' in page          # the other mix-ups on this objective stay one tap away
    assert _miss_review(app, s12, obj) == 'alt'
    # third time: nothing inserted for that objective (stuck), the student is told and the instructor sees it
    api = app.extensions['ciwt_mastery']
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        u = mod.db.session.get(mod.User, s12.uid)
        st = api.engine.student_state(sec, u, log=False)
    assert obj in st['decision']['stuck']
    assert not [a for a in st['decision']['actions'] if a['obj'] == obj]
    assert 'two reviews' in s12.get('/student/section/1').data.decode()


def test_dashboard_hero_falls_back_to_the_adaptive_path(app, mod, s12):
    """Bug: once the getting-started path had no next step (chapter check done, graded test not released) the
    dashboard hero showed "3 of 4 steps done" and no Continue button, although the adaptive path had a next step."""
    qid, qs = _chapter1(app, mod)
    assert s12.post(f'/student/quiz/1/{qid}', data={f'q{i}': it['correct'] for i, it in enumerate(qs)}).status_code in (302, 303)
    api = app.extensions['ciwt_mastery']
    with app.test_request_context('/student'):
        sec = mod.db.session.get(mod.ClassSection, 1)
        u = mod.db.session.get(mod.User, s12.uid)
        gold = mod.student_gold_path(u, sec)
        path = api.student_path(u, sec)
    page = s12.get('/student').data.decode()
    hero = page.split('home-hero', 1)[1].split('</div>\n\n', 1)[0]
    assert path and path['next']
    assert gold and gold['steps'] and not gold['next'], 'precondition: the getting-started path has no next step'
    assert f'href="{path["next"]["url"]}"' in hero and 'Continue:' in hero


def test_route_strong_student_is_offered_the_next_chapter_check_and_passing_skips_it(app, mod, s12):
    """Engine path not covered by a route test before: read chapter 1, right on its quick checks and its
    chapter check -> the engine (not an instructor unlock) offers the chapter 2 mastery check -> passing moves
    the next lesson to chapter 3, chapter 2 lessons stay open, and nothing reaches the gradebook."""
    api = app.extensions['ciwt_mastery']
    MCk = api.models.MasteryCheck
    with app.app_context():
        mods = {m.order: m.id for m in mod.Module.query.filter_by(course_id=1)}
        ch1 = [(l.id, l.estimated_minutes or 30) for l in mod.Lesson.query.filter_by(module_id=mods[1]).order_by(mod.Lesson.order)]
        ch2_first = mod.Lesson.query.filter_by(module_id=mods[2]).order_by(mod.Lesson.order).first().id
        grades_before = mod.TestAttempt.query.filter_by(user_id=s12.uid).count()
    for lid, minutes in ch1:
        assert s12.get(f'/student/module/1/{mods[1]}/lesson/{lid}').status_code == 200
        for _ in range((minutes * 60) // 120):
            assert s12.post('/time/study', json={'lesson_id': lid, 'section_id': 1, 'seconds': 120}).status_code == 200
        with app.app_context():
            open_inline = [(c.id, json.loads(c.items_json)[0]['correct']) for c in
                           MCk.query.filter_by(section_id=1, user_id=s12.uid, kind='inline', completed_at=None)]
        for cid, key in open_inline:
            r = s12.post(f'/student/section/1/quickcheck/{cid}', json={'answer': key, 'dwell_ms': 0})
            assert r.status_code == 200 and r.get_json()['correct']
    qid, qs = _chapter1(app, mod)
    assert s12.post(f'/student/quiz/1/{qid}', data={f'q{i}': it['correct'] for i, it in enumerate(qs)}).status_code in (302, 303)
    with app.test_request_context('/student'):
        u = mod.db.session.get(mod.User, s12.uid)
        path = api.student_path(u, mod.db.session.get(mod.ClassSection, 1))
    offer = [s for s in path['steps'] if s['kind'] == 'testout']
    assert offer and 'chapter 2' in offer[0]['title'] and offer[0]['source'] == 'engine'
    assert any('never graded' in r for r in offer[0]['why'])
    lesson_step = [s for s in path['steps'] if s['kind'] == 'lesson'][0]
    assert f'/module/1/{mods[2]}/' in lesson_step['url']
    assert s12.get('/student/section/1/testout/2').status_code == 200
    with app.app_context():
        c = MCk.query.filter_by(section_id=1, user_id=s12.uid, kind='testout', target='CH-2', completed_at=None).first()
        cid, items = c.id, json.loads(c.items_json)
    assert len({it['obj'] for it in items}) >= 3 and all(it['obj'].startswith('IT-2.') for it in items)
    data = {'check_id': cid, **{f'q{i}': it['correct'] for i, it in enumerate(items)}}
    r = s12.post('/student/section/1/testout/2', data=data)
    assert r.status_code == 303 and '/result/' in r.headers['Location']
    assert 'you tested out' in s12.get(r.headers['Location']).data.decode()
    with app.test_request_context('/student'):
        u = mod.db.session.get(mod.User, s12.uid)
        path = api.student_path(u, mod.db.session.get(mod.ClassSection, 1))
        assert mod.TestAttempt.query.filter_by(user_id=s12.uid).count() == grades_before
    lesson_step = [s for s in path['steps'] if s['kind'] == 'lesson'][0]
    assert f'/module/1/{mods[3]}/' in lesson_step['url']
    assert not [s for s in path['steps'] if s['kind'] == 'testout' and 'chapter 2' in s['title']]
    assert s12.get(f'/student/module/1/{mods[2]}/lesson/{ch2_first}').status_code == 200
