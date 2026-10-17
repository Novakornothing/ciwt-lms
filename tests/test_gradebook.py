"""Gradebook computation, overrides, settings, exports, student views."""
import gradebook as G


def test_pure_helpers():
    assert G.letter(95) == 'A' and G.letter(81) == 'B-' and G.letter(None) == '—'
    assert G.weighted_grade({'tests': 80, 'skills': None, 'quizzes': 100}, {'tests': 70, 'skills': 30, 'quizzes': 0}) == 80
    assert G.weighted_grade({'tests': 80, 'skills': 90}, {'tests': 50, 'skills': 50}) == 85
    assert G.pick([(None, 60), (None, 90)], 'best') == 90
    from datetime import datetime
    assert G.pick([(datetime(2026, 1, 2), 60), (datetime(2026, 1, 1), 90)], 'latest') == 60
    h = G.histogram([55, 85, 86, 99])
    assert [b['n'] for b in h] == [1, 0, 0, 2, 1] and h[-1]['label'] == '90–100'


def _compute(app, mod, section_id=1, uid=None):
    with app.app_context():
        sec = mod.ClassSection.query.get(section_id)
        return app.extensions['ciwt_gradebook'].compute(sec, user_ids={uid} if uid else None)


def test_compute_matches_attempts(app, mod, ids):
    data = _compute(app, mod)
    assert data['rows'], 'seeded section has students'
    with app.app_context():
        r = data['rows'][0]
        u = r['user']
        tests = [c for c in r['cells'] if c['item']['type'] == 'test' and c['item']['category'] == 'tests']
        for c in tests:
            atts = mod.TestAttempt.query.filter_by(user_id=u.id, test_id=c['item']['id'], section_id=1).filter(
                mod.TestAttempt.completed_at.isnot(None)).all()
            best = max([a.score for a in atts], default=None)
            assert (c['score'] is None and best is None) or abs(c['score'] - round(best, 1)) < 0.06
    assert data['summary']['students'] == len(data['rows'])


def test_override_and_excuse_change_grade(instructor, app, mod, ids):
    uid = ids['student1']
    base = _compute(app, mod, uid=uid)['rows'][0]
    test_cell = next(c for c in base['cells'] if c['item']['category'] == 'tests')
    url = f"/instructor/section/{ids['section']}/gradebook/override"
    # note is required
    instructor.post(url, data={'user_id': uid, 'item_type': 'test', 'item_id': test_cell['item']['id'], 'score': '100'})
    assert _compute(app, mod, uid=uid)['rows'][0]['cells'][0]['status'] != 'override'
    instructor.post(url, data={'user_id': uid, 'item_type': 'test', 'item_id': test_cell['item']['id'], 'score': '100', 'note': 'regrade'})
    row = _compute(app, mod, uid=uid)['rows'][0]
    c = next(x for x in row['cells'] if x['item']['id'] == test_cell['item']['id'] and x['item']['type'] == 'test')
    assert c['status'] == 'override' and c['score'] == 100
    instructor.post(url, data={'user_id': uid, 'item_type': 'test', 'item_id': test_cell['item']['id'], 'excused': '1', 'note': 'medical'})
    row = _compute(app, mod, uid=uid)['rows'][0]
    c = next(x for x in row['cells'] if x['item']['id'] == test_cell['item']['id'] and x['item']['type'] == 'test')
    assert c['status'] == 'excused' and c['score'] is None
    instructor.post(url, data={'user_id': uid, 'item_type': 'test', 'item_id': test_cell['item']['id'], 'action': 'clear'})
    row = _compute(app, mod, uid=uid)['rows'][0]
    assert row['grade'] == base['grade']
    # out-of-range score rejected
    instructor.post(url, data={'user_id': uid, 'item_type': 'test', 'item_id': test_cell['item']['id'], 'score': '140', 'note': 'x'})
    assert _compute(app, mod, uid=uid)['rows'][0]['grade'] == base['grade']


def test_settings_change_policy_and_weights(instructor, app, mod, ids):
    url = f"/instructor/section/{ids['section']}/gradebook/settings"
    instructor.post(url, data={'weight_tests': 0, 'weight_skills': 0, 'weight_quizzes': 0})  # rejected
    assert _compute(app, mod)['weights']['tests'] == 70
    instructor.post(url, data={'weight_tests': 50, 'weight_skills': 50, 'weight_quizzes': 0, 'policy': 'latest', 'pass_mark': 75})
    d = _compute(app, mod)
    assert d['weights'] == {'tests': 50, 'skills': 50, 'quizzes': 0} and d['settings'].policy == 'latest'
    instructor.post(url, data={'weight_tests': 70, 'weight_skills': 30, 'weight_quizzes': 0, 'policy': 'best', 'pass_mark': 80})


def test_csv_has_every_student(instructor, app, mod, ids):
    text = instructor.get(f"/instructor/section/{ids['section']}/gradebook.csv").get_data(as_text=True)
    lines = [l for l in text.splitlines() if l.strip()]
    n = len(_compute(app, mod)['rows'])
    assert lines[0].startswith('last_name,first_name,email,course_grade')
    assert len(lines) == n + 2  # header + students + class mean


def test_student_sees_only_own_grades(student, ids):
    html = student.get(f"/student/section/{ids['section']}/grades").get_data(as_text=True)
    assert 'My grades' in html and 'Student2' not in html
    assert student.get('/student/grades').status_code == 200


def test_outsider_redirected_from_section_grades(outsider, ids):
    r = outsider.get(f"/student/section/{ids['section']}/grades")
    assert r.status_code == 302


def test_lesson_ids_stable_across_sync(app, mod):
    with app.app_context():
        before = sorted(l.id for l in mod.Lesson.query.all())
        mod.sync_curriculum()
        after = sorted(l.id for l in mod.Lesson.query.all())
    assert before == after
