"""Pass 12: lab process diagnosis wired to the live lab_event log (after the labs merge).

Events below are hand-written test rows (not real student data) inserted into the throwaway test DB and removed again.
"""
from datetime import datetime, timedelta

import pytest

from mastery import lab_diagnosis as LD

T0 = datetime(2026, 10, 1, 9, 0)


def ev(seq, kind, action, outcome='ok', newly=None, attempt=1):
    return {'seq': seq, 'attempt': attempt, 'at': T0 + timedelta(seconds=20 * seq), 'kind': kind,
            'action': action, 'outcome': outcome, 'newly': newly}


VM_LAB = {'id': 'linux-vm-x', 'objectives': [{'id': 'boot', 'text': 'Boot'}, {'id': 'mkdir', 'text': 'Make the dir'},
                                              {'id': 'perm', 'text': 'Set permissions'}]}


# ---------------------------------------------------------------- kind mapping (pure)
def test_vm_lines_are_never_rejected_and_boot_is_not_an_action():
    evs = [ev(1, 'vm', 'boot', newly=['boot']), ev(2, 'vm', 'mkdir -p /root/x'), ev(3, 'vm', 'chmod 750 /root/x'),
           ev(4, 'check', 'vm probe {"a": 1}', 'progress', ['mkdir', 'perm']), ev(5, 'vm', 'ls -l /root'),
           ev(6, 'complete', 'linux-vm-x')]
    r = LD.diagnose(evs, lab=VM_LAB)
    assert r['summary']['actions'] == 4 and r['summary']['rejected'] == 0
    assert not LD.is_action(evs[0]) and LD.is_action(evs[1])
    ids = {p['id'] for p in r['patterns']}
    assert 'never_verifies' not in ids and 'trial_and_error' not in ids
    assert 'efficient' in ids


def test_vm_probe_not_finished_is_not_a_rejection_but_repeating_it_unchanged_is_flagged():
    evs = [ev(1, 'vm', 'boot', newly=['boot'])] + [ev(i, 'check', 'vm probe {"c": "same"}', 'wrong') for i in range(2, 6)]
    r = LD.diagnose(evs, lab=VM_LAB)
    assert r['summary']['rejected'] == 0
    ids = {p['id'] for p in r['patterns']}
    assert 'repeats_without_change' in ids and 'trial_and_error' not in ids
    assert LD.is_rejected(ev(9, 'check', 'vm probe {}', 'error'))


def test_vm_change_without_a_check_command_is_never_verifies():
    evs = [ev(1, 'vm', 'boot', newly=['boot']), ev(2, 'vm', 'mkdir -p /root/x'),
           ev(3, 'check', 'vm probe {"a": 1}', 'progress', ['mkdir'])]
    ids = {p['id'] for p in LD.diagnose(evs, lab=VM_LAB)['patterns']}
    assert 'never_verifies' in ids


def test_guided_answer_checks_that_are_wrong_count_as_rejected():
    evs = [ev(i, 'check', f'step1 "{i}"', 'wrong') for i in range(1, 5)]
    r = LD.diagnose(evs)
    assert r['summary']['rejected'] == 4 and 'trial_and_error' in {p['id'] for p in r['patterns']}


def test_hint_repeat_views_do_not_count_as_hints():
    evs = [ev(1, 'hint', 'o1 tier 1', 'ok'), ev(2, 'hint', 'o1 tier 1', 'repeat'), ev(3, 'hint', 'o1 tier 1', 'repeat')]
    assert LD.diagnose(evs)['summary']['hints'] == 1


# ---------------------------------------------------------------- live wiring (DB)
@pytest.fixture
def lab_rows(app, mod):
    """student1 (section 1): win-ipconfig attempt 1 was clean, attempt 2 (latest) is guessing.
    The same student's linux lab row belongs to another class (section 2) and must not appear."""
    api = mod.lab_progress_api
    LP, LE = api.LabProgress, api.LabEvent
    with app.app_context():
        u = mod.User.query.filter_by(email='student1@lms.local').first()
        uid = u.id
        LE.query.filter_by(user_id=uid).delete(); LP.query.filter_by(user_id=uid).delete()
        mod.db.session.add(LP(user_id=uid, lab_id='win-ipconfig', section_id=1, resets=1, updated_at=T0))
        mod.db.session.add(LP(user_id=uid, lab_id='linux-vm-perms', section_id=2, updated_at=T0))
        rows = [ev(1, 'cmd', 'hostname', 'progress', '["run_hostname"]', attempt=1)]
        rows += [ev(i, 'cmd', f'ipconfg /{i}', 'unknown', attempt=2) for i in range(1, 6)]
        rows += [ev(1, 'vm', 'rm -rf /', 'ok')]
        for i, r in enumerate(rows):
            lab = 'linux-vm-perms' if i == len(rows) - 1 else 'win-ipconfig'
            mod.db.session.add(LE(user_id=uid, lab_id=lab, **r))
        mod.db.session.commit()
    yield uid
    with app.app_context():
        LE.query.filter_by(user_id=uid).delete(); LP.query.filter_by(user_id=uid).delete()
        mod.db.session.commit()


def test_lab_diagnoses_use_latest_attempt_and_this_class_only(app, mod, lab_rows):
    with app.app_context():
        api = app.extensions['ciwt_mastery']
        u = mod.db.session.get(mod.User, lab_rows)
        sec = mod.db.session.get(mod.ClassSection, 1)
        res = api.lab_diagnoses(u, sec)
    assert [r['lab_id'] for r in res] == ['win-ipconfig']
    r = res[0]
    assert r['attempt'] == 2 and r['summary']['actions'] == 5 and r['struggling']
    assert r['title'] and r['title'] != 'win-ipconfig'           # title from interactive_labs.get_lab
    assert 'trial_and_error' in {p['id'] for p in r['patterns']}


def test_who_needs_me_and_student_page_show_the_lab_reason(instructor, lab_rows):
    t = instructor.get('/instructor/section/1/mastery/today').data.decode()
    assert 'Lab “' in t and 'trial-and-error' in t
    assert 'appear once the lab event log' not in t
    h = instructor.get(f'/instructor/section/1/mastery/student/{lab_rows}').data.decode()
    assert 'How Student1 Demo works the labs' in h and 'Coaching tip' in h and 'attempt 2' in h
    assert f'/instructor/section/1/labs/student/{lab_rows}/win-ipconfig' in h


def test_lab_diagnosis_never_changes_a_lab_score(app, mod, instructor, lab_rows):
    with app.app_context():
        before = [(r.lab_id, r.score, r.best_score) for r in mod.lab_progress_api.LabProgress.query.filter_by(user_id=lab_rows)]
    instructor.get(f'/instructor/section/1/mastery/student/{lab_rows}')
    instructor.get('/instructor/section/1/mastery/today')
    with app.app_context():
        after = [(r.lab_id, r.score, r.best_score) for r in mod.lab_progress_api.LabProgress.query.filter_by(user_id=lab_rows)]
    assert before == after
