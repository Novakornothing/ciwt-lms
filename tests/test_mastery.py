"""Pass 11 adaptive mastery: model math, override rules, consent fallback, Helix never penalizes, routes."""
import json
from datetime import datetime, timedelta

import pytest

from mastery import model as M
from mastery import policy as P

T0 = datetime(2026, 9, 1, 9, 0)


@pytest.fixture(scope='module', autouse=True)
def objective_tagged_checks(app, mod):
    """A fresh test DB is seeded but not yet re-synced; every later boot runs sync_pilot_slice(), which gives
    chapter-check items their objective codes and bank ids. Do the same here."""
    with app.app_context():
        mod.sync_pilot_slice()
        mod.db.session.commit()


def obs(kind, correct, i=0, **kw):
    return dict(kind=kind, correct=correct, when=T0 + timedelta(minutes=i), **kw)


def mod_db_get(app, model, pk):
    import app as lms
    return lms.db.session.get(model, pk)


# ------------------------------------------------------------------ model math
def test_bayes_matches_hand_calculation():
    # p=0.3, slip .1, guess .25: right -> .27/(.27+.175)=0.6067 ; wrong -> .03/(.03+.525)=0.0541
    assert abs(M.bayes(0.3, True, 0.1, 0.25) - 0.27 / 0.445) < 1e-9
    assert abs(M.bayes(0.3, False, 0.1, 0.25) - 0.03 / 0.555) < 1e-9


def test_step_is_tempered_and_learns():
    full = M.step(0.3, True, 1.0)
    post = 0.27 / 0.445
    assert abs(full - (post + (1 - post) * 0.12)) < 1e-9
    half = M.step(0.3, True, 0.5)
    assert 0.3 < half < full
    assert M.step(0.3, False, 1.0) < 0.3
    assert M.step(0.3, True, 0) == pytest.approx(0.3)


def test_estimate_status_confidence_and_thresholds():
    assert M.estimate([])['status'] == 'not_started'
    one_wrong = M.estimate([obs('test', False)])
    assert one_wrong['status'] == 'developing', 'one answer (n_eff 1 < 1.5) never triggers review'
    low = M.estimate([obs('test', False, 0), obs('test', False, 1)])
    assert low['status'] == 'review' and low['confidence'] == 'medium' and low['n_eff'] == 2
    high = M.estimate([obs('test', True, i) for i in range(6)])
    assert high['status'] == 'mastered' and high['confidence'] == 'high' and high['pct'] >= 85
    assert high['n_items'] == 6 and high['n_correct'] == 6


def test_unknown_kinds_and_helix_are_ignored():
    base = [obs('quiz', True, 0), obs('quiz', False, 1)]
    a = M.estimate(base)
    b = M.estimate(base + [{'kind': 'helix', 'when': T0, 'dwell_ms': 0, 'correct': False},
                           {'kind': 'gaze', 'when': T0, 'correct': False}])
    assert a['p'] == b['p'] and a['n_eff'] == b['n_eff']


def test_reading_only_raises():
    base = [obs('quiz', False, 0), obs('quiz', False, 1)]
    a = M.estimate(base)
    read = M.estimate(base + [{'kind': 'reading', 'seconds': 1800, 'expected': 1800, 'lesson': 'lesson 1.1', 'when': T0}])
    short = M.estimate(base + [{'kind': 'reading', 'seconds': 10, 'expected': 1800, 'lesson': 'lesson 1.1', 'when': T0}])
    assert read['p'] > a['p']
    assert short['p'] == a['p'] and short['short_reads']


def test_describe_counts_plain_language():
    est = M.estimate([obs('test', True, 0), obs('quiz', False, 1), obs('daily', True, 2)])
    s = M.describe_counts(est)
    assert s.startswith('2 of 3 questions right') and 'graded test questions 1/1' in s and 'daily review' in s


# ------------------------------------------------------------------ policy / overrides
SET_ON = {'enabled': True, 'testout': True, 'testout_bank': False}
SET_OFF = {'enabled': False, 'testout': True, 'testout_bank': False}
LOW = M.estimate([obs('test', False, 0), obs('test', False, 1)])
GOOD = M.estimate([obs('test', True, i) for i in range(6)])


def dec(est, settings=SET_ON, overrides=None, history=None, helix=None, obj='IT-5.1', chapter=5):
    return P.decide_objective(obj, est, chapter=chapter, settings=settings, overrides=overrides or {},
                              history=history, helix=helix, describe=M.describe_counts)


def test_engine_review_then_alt_then_stuck():
    r = dec(LOW)
    assert r['action']['type'] == 'review' and not r['action']['required']
    assert dec(LOW, history={'reviews_done': 1})['action']['type'] == 'alt_review'
    s = dec(LOW, history={'reviews_done': 2})
    assert s['action'] is None and s['stuck']


def test_skip_respected_until_new_evidence():
    est = dict(LOW, last_when=T0)
    assert dec(est, history={'skipped_at': T0 + timedelta(hours=1)})['action'] is None
    assert dec(est, history={'skipped_at': T0 - timedelta(hours=1)})['action']['type'] == 'review'


def test_overrides():
    at = T0
    waived = dec(LOW, overrides={'IT-5.1': {'kind': 'waive', 'at': at}})
    assert waived['state'] == 'waived' and waived['action'] is None
    forced = dec(GOOD, settings=SET_OFF, overrides={'IT-5.1': {'kind': 'force_review', 'at': at, 'note': 'see me'}})
    assert forced['action']['required'] and forced['action']['source'] == 'instructor', 'force review applies with adaptivity off'
    done = dec(GOOD, overrides={'IT-5.1': {'kind': 'force_review', 'at': at}}, history={'last_review_at': at + timedelta(minutes=5), 'reviews_done': 1})
    assert done['action'] is None
    locked = dec(LOW, overrides={'CH-5': {'kind': 'lock', 'at': at}})
    assert locked['action']['required'] and locked['override_scope'] == 'chapter'
    # objective-level beats chapter-level
    both = dec(LOW, overrides={'CH-5': {'kind': 'lock', 'at': at}, 'IT-5.1': {'kind': 'waive', 'at': at}})
    assert both['state'] == 'waived'
    assert dec(LOW, settings=SET_OFF)['action'] is None, 'adaptivity off: no engine action'


def test_testout_offer_rules():
    rows = [{'state': 'mastered'}] * 4
    assert P.testout_offer(6, rows=rows, settings=SET_ON, overrides={}, testout_history={})
    assert not P.testout_offer(6, rows=rows, settings=SET_ON, overrides={'CH-6': {'kind': 'lock'}}, testout_history={})
    assert P.testout_offer(6, rows=[], settings=SET_OFF, overrides={'CH-6': {'kind': 'unlock'}}, testout_history={})['source'] == 'instructor'
    assert not P.testout_offer(6, rows=rows, settings=SET_ON, overrides={}, testout_history={6: {'passed': True}})
    assert not P.testout_offer(6, rows=rows + [{'state': 'review'}], settings=SET_ON, overrides={}, testout_history={})


def test_gate_only_for_current_or_earlier_chapters():
    d = P.decide({'IT-5.1': LOW, 'IT-8.1': LOW}, chapters={'IT-5.1': 5, 'IT-8.1': 8}, settings=SET_ON,
                 describe=M.describe_counts)
    assert P.gate(d, {'IT-5.1': 5, 'IT-8.1': 8}, 3) is None
    assert P.gate(d, {'IT-5.1': 5, 'IT-8.1': 8}, 6)['obj'] == 'IT-5.1'
    assert [a['obj'] for a in d['actions']] == ['IT-5.1', 'IT-8.1'], 'earlier chapter first'


# ------------------------------------------------------------------ Helix never penalizes / consent fallback
def test_helix_offer_is_optional_and_never_changes_state():
    hx = {'IT-5.1': {'skimmed': ['Address, door, name'], 'reread': []}}
    for est in (M.estimate([]), M.estimate([obs('quiz', True, 0)])):
        with_h = dec(est, helix=hx)
        without = dec(est, helix=None)
        assert with_h['state'] == without['state']
        assert with_h['action']['type'] == 'helix_offer' and not with_h['action']['required']
        assert with_h['action']['source'] == 'helix' and not with_h['stuck']
    assert dec(GOOD, helix=hx)['action'] is None, 'no offer once mastered'
    assert dec(M.estimate([]), helix=hx, settings=SET_OFF)['action'] is None
    assert dec(M.estimate([]), helix={})['action'] is None, 'no Helix data: rule does not fire'
    # Helix never upgrades an engine review into something required
    lr = dec(LOW, helix=hx)
    assert lr['action']['type'] == 'review' and not lr['action']['required']


def test_engine_helix_requires_current_consent(app, mod):
    api = app.extensions['ciwt_mastery']
    with app.test_request_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        u = mod.User.query.filter_by(email='student2@lms.local').first()
        mod.HelixConsent.query.filter_by(user_id=u.id).delete()
        mod.db.session.commit()
        st = api.engine.student_state(sec, u, log=False)
        assert st['helix_status'] == 'no_consent' and st['helix'] is None
        c = mod.HelixConsent(user_id=u.id, policy_version='old-version', granted_at=datetime(2026, 9, 1))
        mod.db.session.add(c)
        mod.db.session.commit()
        assert api.engine.student_state(sec, u, log=False)['helix_status'] == 'no_consent', 'stale policy version'
        c.policy_version = mod.HELIX_POLICY_VERSION
        mod.db.session.commit()
        st2 = api.engine.student_state(sec, u, log=False)
        assert st2['helix_status'] in ('ok', 'disabled')
        assert {k: v['p'] for k, v in st2['states'].items()} == {k: v['p'] for k, v in st['states'].items()}
        mod.db.session.delete(c)
        mod.db.session.commit()


def test_mastery_never_touches_gradebook(app, mod, student, ids):
    gb = app.extensions['ciwt_gradebook']
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        before = gb.compute(sec, user_ids={ids['student1']})['rows'][0]['grade']
    student.get('/student/section/1/mastery')
    r = student.get('/student/section/1/review/IT-1.1')
    assert r.status_code == 200
    with app.app_context():
        api = app.extensions['ciwt_mastery']
        c = api.models.MasteryCheck.query.filter_by(user_id=ids['student1'], kind='review', completed_at=None).first()
    student.post('/student/section/1/review/IT-1.1', data={'check_id': c.id})
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        assert gb.compute(sec, user_ids={ids['student1']})['rows'][0]['grade'] == before


# ------------------------------------------------------------------ routes / access
STUDENT_PAGES = ['/student/section/1/mastery', '/student/section/1/review/IT-1.1', '/student/section/1/plan',
                 '/student/section/1/daily']
STAFF_PAGES = ['/instructor/section/1/mastery', '/instructor/section/1/mastery?ch=5',
               '/instructor/section/1/mastery/student/{s1}', '/instructor/section/1/mastery.csv',
               '/instructor/section/1/mastery/today']


def test_student_pages(student):
    for u in STUDENT_PAGES:
        assert student.get(u).status_code in ((200, 302) if u.endswith('/daily') else (200,)), u   # done today -> result
    assert student.get('/student/section/1/review/XX-9.9').status_code == 404
    assert student.get('/instructor/section/1/mastery').status_code == 403


def test_staff_pages_and_access(instructor, instructor2, outsider, ids):
    for u in STAFF_PAGES:
        assert instructor.get(u.format(s1=ids['student1'])).status_code == 200, u
    assert instructor2.get('/instructor/section/1/mastery').status_code == 403
    assert outsider.get('/student/section/1/mastery').status_code == 404


def test_csv_has_no_answer_keys(instructor):
    body = instructor.get('/instructor/section/1/mastery.csv').data.decode()
    assert body.splitlines()[0].startswith('student,email,objective')
    assert 'correct' not in body.splitlines()[0]


def test_override_flow_and_validation(app, instructor, student, ids):
    api = app.extensions['ciwt_mastery']
    url = '/instructor/section/1/mastery/override'
    uid = ids['student1']
    instructor.post(url, data={'user_id': uid, 'target': 'IT-1.2', 'kind': 'force_review'})   # no note
    with app.app_context():
        assert not api.models.MasteryOverride.query.filter_by(user_id=uid, target='IT-1.2', active=True).first()
    instructor.post(url, data={'user_id': uid, 'target': 'BAD', 'kind': 'force_review', 'note': 'x'})
    instructor.post(url, data={'user_id': uid, 'target': 'IT-1.2', 'kind': 'nuke', 'note': 'x'})
    r = instructor.post(url, data={'user_id': uid, 'target': 'IT-1.2', 'kind': 'force_review', 'note': 'please review',
                                   'next': 'https://evil.example/'})
    assert r.status_code == 303 and r.headers['Location'].endswith('/instructor/section/1/mastery')
    with app.app_context():
        assert api.models.MasteryOverride.query.filter_by(user_id=uid, target='IT-1.2', active=True).count() == 1
    # the required review blocks lessons in chapter 1 (except the review's own lesson), and cannot be skipped
    h = student.get('/student/section/1/review/IT-1.2').data.decode()
    assert 'required by your instructor' in h and 'Skip for now' not in h
    r = student.post('/student/section/1/review/IT-1.2/skip')
    assert r.status_code == 303 and '/review/IT-1.2' in r.headers['Location']
    instructor.post(url, data={'user_id': uid, 'target': 'IT-1.2', 'kind': 'clear', 'note': 'done'})
    with app.app_context():
        assert not api.models.MasteryOverride.query.filter_by(user_id=uid, target='IT-1.2', active=True).first()
        assert api.models.MasteryDecision.query.filter_by(user_id=uid, action='override_force_review').count() >= 1


def test_review_answers_are_graded_server_side_and_keys_not_shown(app, student, ids):
    api = app.extensions['ciwt_mastery']
    h = student.get('/student/section/1/review/IT-1.3').data.decode()
    with app.app_context():
        c = api.models.MasteryCheck.query.filter_by(user_id=ids['student1'], kind='review', target='IT-1.3',
                                                    completed_at=None).first()
        items = json.loads(c.items_json)
    assert items and '"correct"' not in h
    data = {'check_id': c.id}
    data.update({f'q{i}': it['correct'] for i, it in enumerate(items)})
    r = student.post('/student/section/1/review/IT-1.3', data=data)
    assert r.status_code == 303
    done = student.get(r.headers['Location']).data.decode()
    with app.app_context():
        c2 = mod_db_get(app, api.models.MasteryCheck, c.id)
        assert c2.correct == len(items) and c2.completed_at
    assert 'Correct answer' not in done


def test_settings_toggle(app, instructor, mod):
    api = app.extensions['ciwt_mastery']
    instructor.post('/instructor/section/1/mastery/settings', data={'testout': '1'})
    with app.app_context():
        assert api.engine.settings(1)['enabled'] is False
    instructor.post('/instructor/section/1/mastery/settings', data={'enabled': '1', 'testout': '1'})
    with app.app_context():
        assert api.engine.settings(1)['enabled'] is True


def test_study_heartbeat_validates(student, ids):
    assert student.post('/time/study', json={'lesson_id': 'abc', 'seconds': 10}).status_code == 400
    assert student.post('/time/study', json={'lesson_id': 999999, 'seconds': 10}).status_code == 400
    assert student.post('/time/study', json={'lesson_id': ids['lesson'], 'section_id': 2, 'seconds': 10}).status_code == 403
    assert student.post('/time/study', json={'lesson_id': ids['lesson'], 'section_id': 1, 'seconds': 30}).status_code == 200
