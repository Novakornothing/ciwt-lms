"""Pass 20: Dynamic Lab Process Analysis — timeline, why-diagnosis with lesson links, class roll-up, and the
student / instructor views. Events are hand-written test rows (not real student data) in the throwaway test DB."""
from datetime import datetime, timedelta

import pytest

from mastery import lab_diagnosis as LD

T0 = datetime(2026, 10, 1, 9, 0)
ROUTE_LAB = {'id': 'net-route', 'objectives': [{'id': 'look', 'text': 'Read the routing table'},
                                               {'id': 'fix', 'text': 'Restore the default gateway route'}]}


def ev(seq, kind, action, outcome='ok', newly=None, detail=None, attempt=1):
    return {'seq': seq, 'attempt': attempt, 'at': T0 + timedelta(seconds=30 * seq), 'kind': kind, 'action': action,
            'outcome': outcome, 'newly': newly, 'detail': detail}


def ids(res):
    return {p['id'] for p in res['patterns']}


# ---------------------------------------------------------------- pure analysis
def test_timeline_phases_and_time_per_phase():
    res = LD.analyze([ev(1, 'vm', 'boot'), ev(2, 'vm', 'ip route', newly=['look']), ev(3, 'vm', 'ip route add default via 10.0.0.1', newly=['fix']),
                      ev(4, 'vm', 'ping -c1 10.0.0.1'), ev(5, 'complete', '')], lab=ROUTE_LAB)
    assert [s['phase'] for s in res['timeline'][:3]] == ['diagnose', 'change', 'verify']
    assert res['sequence'] == ['diagnose', 'change', 'verify']
    assert res['phases']['change']['n'] == 1 and res['phases']['verify']['seconds'] == 30
    assert {'diagnosed_first', 'verified_before_submit'} <= {p['id'] for p in res['strengths']}
    assert not res['concerns']


def test_change_before_diagnose_links_the_lesson_rung():
    res = LD.analyze([ev(1, 'cmd', 'ipconfig /release'), ev(2, 'cmd', 'ipconfig /renew')])
    p = next(p for p in res['concerns'] if p['id'] == 'change_before_diagnose')
    assert p['ref']['sid'] == '3-change-awareness' and p['ref']['rung'] == 'R3'


def test_flushing_dns_when_the_fault_is_a_route():
    res = LD.analyze([ev(1, 'cmd', 'ipconfig /all'), ev(2, 'cmd', 'ipconfig /flushdns'), ev(3, 'cmd', 'ipconfig /flushdns'),
                      ev(4, 'cmd', 'ipconfig /flushdns')], lab=ROUTE_LAB)
    p = next(p for p in res['patterns'] if p['id'] == 'wrong_fix_repeated')
    assert 'routing' in ' '.join(p['evidence']) and LD.struggling(res)


def test_skipped_elevation_and_repeated_failed_checks():
    res = LD.analyze([ev(1, 'vm', 'cat /etc/hosts'), ev(2, 'vm', 'useradd bob', detail='useradd: Permission denied.'),
                      ev(3, 'check', 'vm probe', 'error'), ev(4, 'check', 'vm probe', 'error'), ev(5, 'check', 'vm probe', 'error')])
    assert {'elevation_missed', 'repeated_failed_checks'} <= ids(res)
    el = next(p for p in res['patterns'] if p['id'] == 'elevation_missed')
    assert 'never elevated' in ' '.join(el['evidence']) and el['ref']['course'] == 'ITSUP'


def test_cisco_enable_missing_is_elevation():
    res = LD.analyze([ev(1, 'cmd', 'show ip int brief'), ev(2, 'cmd', 'configure terminal', 'error', detail='% Invalid input detected')])
    assert 'elevation_missed' in ids(res)


def test_class_summary_counts_common_wrong_turns():
    a = LD.analyze([ev(1, 'cmd', 'ipconfg', 'unknown'), ev(2, 'cmd', 'ipconfig /flushdns'), ev(3, 'cmd', 'ipconfig /flushdns')])
    b = LD.analyze([ev(1, 'cmd', 'ipconfg', 'unknown'), ev(2, 'cmd', 'ipconfig /all')])
    cls = LD.class_summary([a, b])
    assert cls['students'] == 2 and cls['wrong_turns'][0] == {'action': 'ipconfg', 'count': 2}
    assert any(p['id'] == 'wrong_fix_repeated' and p['count'] == 1 and p['share'] == 50 for p in cls['patterns'])


# ---------------------------------------------------------------- views
@pytest.fixture
def rows(app, mod):
    api = mod.lab_progress_api
    LP, LE = api.LabProgress, api.LabEvent
    with app.app_context():
        uid = mod.User.query.filter_by(email='student1@lms.local').first().id
        LE.query.filter_by(user_id=uid).delete(); LP.query.filter_by(user_id=uid).delete()
        mod.db.session.add(LP(user_id=uid, lab_id='win-ipconfig', section_id=1, updated_at=T0))
        for r in [ev(1, 'cmd', 'ipconfig /flushdns'), ev(2, 'cmd', 'ipconfig /flushdns'), ev(3, 'cmd', 'ipconfig /flushdns'),
                  ev(4, 'cmd', 'ipconfg', 'unknown'), ev(5, 'cmd', 'ipconfg', 'unknown'), ev(6, 'cmd', 'ipconfg', 'unknown'),
                  ev(7, 'hint', 'h1')]:
            mod.db.session.add(LE(user_id=uid, lab_id='win-ipconfig', **r))
        mod.db.session.commit()
    yield uid
    with app.app_context():
        LE.query.filter_by(user_id=uid).delete(); LP.query.filter_by(user_id=uid).delete()
        mod.db.session.commit()


def test_student_sees_own_process_analysis(student, rows):
    student.get('/labs/win-ipconfig?section_id=1')
    h = student.get('/labs/win-ipconfig/analysis').data.decode()
    assert 'Dynamic Lab Process Analysis' in h and 'Where it went wrong' in h
    assert 'Repeatedly flushed DNS' in h and 'Step-by-step timeline' in h and 'Learn it:' in h
    j = student.get('/labs/win-ipconfig/analysis?format=json').get_json()
    assert j['summary']['actions'] == 6 and any(c['id'] == 'wrong_fix_repeated' for c in j['concerns'])
    assert 'My process analysis' in student.get('/labs/win-ipconfig').data.decode()


def test_student_analysis_is_empty_without_events(student2):
    h = student2.get('/labs/win-ipconfig/analysis').data.decode()
    assert 'No actions recorded' in h


def test_instructor_detail_class_view_and_who_needs_me(instructor, rows):
    h = instructor.get(f'/instructor/section/1/labs/student/{rows}/win-ipconfig').data.decode()
    assert 'Dynamic Lab Process Analysis' in h and 'Why they struggled' in h and 'Trial-and-error' in h
    c = instructor.get('/instructor/section/1/labs/results?lab=win-ipconfig').data.decode()
    assert 'Class lab process: common wrong turns' in c and '<code>ipconfg</code> × 3' in c
    t = instructor.get('/instructor/section/1/mastery/today').data.decode()
    assert 'reteach' in t and f'/instructor/section/1/labs/student/{rows}/win-ipconfig' in t


def test_other_students_cannot_see_the_instructor_detail(student, rows):
    assert student.get(f'/instructor/section/1/labs/student/{rows}/win-ipconfig').status_code in (302, 403, 404)
