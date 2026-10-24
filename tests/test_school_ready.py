"""School-ready pass: comprehension gate, LTI, sections hub, outcomes, accessibility, FERPA, staff roles."""
import re

from tests.test_ladder_engine import _ans, _check_ids, _lesson, _reset, _section_for, lesson11  # noqa: F401


def _lesson_ids(html):
    return re.findall(r'id="ladder-sec-([^"]+)"', html)


# ---------------------------------------------------------------- 0. comprehension gate
def test_gate_banner_locks_and_advance_redirect(student, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    html = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    sids = _lesson_ids(html)
    assert sids and 'id="ladderGate"' in html and f'0 of {len(sids)}' in html
    assert 'Complete the quick check above to unlock this section' in html
    assert f'href="#ladder-sec-{sids[0]}"' in html and '/advance?' in html
    r = student.get(f'/student/section/{s}/lesson/{l}/advance?to=module')
    assert r.status_code == 303 and r.headers['Location'].endswith(f'#ladder-sec-{sids[0]}')
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert g['blocked'] and g['total'] == len(sids) and g['done'] == 0
    # verify every section correctly -> gate opens
    for sid in sids:
        html = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
        cid, _ = _check_ids(html, sid)
        if not cid:
            continue
        with app.app_context():
            right = _ans(cid, True)
        student.post(f'/student/section/{s}/ladder/{l}/{sid}/answer', data={'check_id': cid, 'answer': right})
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert not g['blocked'] and g['done'] == g['total']
    r = student.get(f'/student/section/{s}/lesson/{l}/advance?to=module')
    assert r.status_code == 303 and '#ladder-sec-' not in r.headers['Location']


def test_gate_setting_off_and_bypass(student, instructor, mod, app, lesson11):
    uid = _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'bypass', 'user_id': uid, 'lesson_id': l})
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert g['exempt'] and not g['blocked']
    assert 'id="ladderGate"' not in student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'bypass', 'action': 'remove', 'user_id': uid, 'lesson_id': l})
    assert student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()['blocked']
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'class', 'gate_form': '1', 'enabled': 'on', 'micro_checks': 'on'})
    g = student.get(f'/student/section/{s}/ladder/{l}/gate').get_json()
    assert not g['on'] and not g['blocked']
    _reset(mod, app, 'student1@lms.local')


def test_quiz_strict_gate_only_when_enabled(student, instructor, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    with app.app_context():
        q = mod.Quiz.query.filter_by(module_id=m).first()
    if not q:
        return
    assert student.get(f'/student/quiz/{s}/{q.id}').status_code == 200        # default: quiz not gated
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'class', 'gate_form': '1', 'enabled': 'on',
                                                             'micro_checks': 'on', 'require_check_to_advance': 'on',
                                                             'gate_quiz_on_ladder': 'on'})
    r = student.get(f'/student/quiz/{s}/{q.id}')
    assert r.status_code == 303 and '#ladder-sec-' in r.headers['Location']
    _reset(mod, app, 'student1@lms.local')
