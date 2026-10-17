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
        sec = mod.db.session.get(mod.ClassSection, section_id)
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


# ---------------------------------------------------------------- pass 3
def test_scale_late_and_window_helpers():
    from datetime import datetime, date
    sc = G.parse_scale('[[90, "A"], [75, "B"], [50, "C"]]')
    assert sc[-1] == (0, 'F') and G.letter(76, scale=sc) == 'B' and G.letter(10, scale=sc) == 'F'
    assert G.parse_scale('garbage') == G.DEFAULT_SCALE and G.parse_scale('[]') == G.DEFAULT_SCALE
    assert G.parse_scale([[100, 'TOOLONG'], [0, 'P']]) == [(100, 'TOOL'), (0, 'P')]
    due = datetime(2026, 10, 1, 17, 0)
    assert G.late_penalty(datetime(2026, 10, 1, 16, 0), due, 10, 30) == (0, 0.0)
    assert G.late_penalty(datetime(2026, 10, 1, 18, 0), due, 10, 30) == (1, 10.0)       # started day counts
    assert G.late_penalty(datetime(2026, 10, 6, 18, 0), due, 10, 30) == (6, 30.0)       # capped
    assert G.late_penalty(datetime(2026, 10, 1, 18, 0), due, 10, 0, grace_hours=2) == (0, 0.0)
    assert G.late_penalty(datetime(2026, 10, 9), due, 0, 0) == (0, 0.0)                 # rule off
    assert G.in_window(datetime(2026, 9, 2), datetime(2026, 9, 1), date(2026, 12, 1))
    assert not G.in_window(datetime(2026, 8, 1), datetime(2026, 9, 1), None)            # before enrolling
    assert not G.in_window(datetime(2027, 1, 5), datetime(2026, 9, 1), date(2026, 12, 1))  # after class ended


def test_quiz_attempts_scoped_to_section(app, mod, ids):
    """A quiz attempt recorded for another class (or before enrolling) must not count here."""
    from datetime import timedelta
    uid, qid = ids['student1'], ids['quiz']
    with app.app_context():
        enr = mod.Enrollment.query.filter_by(user_id=uid, section_id=1).first()
        other = mod.ClassSection.query.filter(mod.ClassSection.id != 1).first()
        mod.QuizAttempt.query.filter_by(user_id=uid, quiz_id=qid).delete()
        mod.db.session.add_all([
            mod.QuizAttempt(user_id=uid, quiz_id=qid, score=40, section_id=1, completed_at=enr.enrolled_at + timedelta(days=1)),
            mod.QuizAttempt(user_id=uid, quiz_id=qid, score=100, section_id=other.id if other else 999, completed_at=enr.enrolled_at + timedelta(days=2)),
            mod.QuizAttempt(user_id=uid, quiz_id=qid, score=95, section_id=None, completed_at=enr.enrolled_at - timedelta(days=30)),
        ])
        mod.db.session.commit()
    data = _compute(app, mod)
    row = next(r for r in data['rows'] if r['user'].id == uid)
    cell = next(c for c in row['cells'] if c['item']['type'] == 'quiz' and c['item']['id'] == qid)
    assert cell['score'] == 40 and cell['attempts'] == 1
    assert data['summary']['quiz_attempts_excluded'] >= 2


def test_take_quiz_records_section(student, app, mod, ids):
    with app.app_context():
        q = mod.db.session.get(mod.Quiz, ids['quiz'])
        n_q = len(q.questions) if hasattr(q, 'questions') else 0
    r = student.post(f"/student/quiz/{ids['section']}/{ids['quiz']}", data={}, follow_redirects=False)
    assert r.status_code in (200, 302)
    with app.app_context():
        a = mod.QuizAttempt.query.filter_by(user_id=ids['student1'], quiz_id=ids['quiz']).order_by(mod.QuizAttempt.id.desc()).first()
        assert a is not None and a.section_id == ids['section']


def test_letter_scale_editor_and_late_rules(instructor, app, mod, ids):
    sid = ids['section']
    r = instructor.post(f'/instructor/section/{sid}/gradebook/scale', data={
        'scale_min': ['90', '70', 'x', ''], 'scale_label': ['H', 'P', 'Q', '']})
    assert r.status_code == 302
    with app.app_context():
        assert mod.db.session.query(mod.app.extensions['ciwt_gradebook'].models.GradebookSetting).filter_by(section_id=sid).first().letter_scale is None, 'invalid rows reject the save'
    r = instructor.post(f'/instructor/section/{sid}/gradebook/scale', data={'scale_min': ['90', '70'], 'scale_label': ['H', 'P']})
    data = _compute(app, mod)
    assert data['settings'].scale == [(90, 'H'), (70, 'P'), (0, 'F')]
    assert {r['letter'] for r in data['rows'] if r['grade'] is not None} <= {'H', 'P', 'F'}
    page = instructor.get(f'/instructor/section/{sid}/gradebook').get_data(as_text=True)
    assert 'Letter scale' in page and 'custom' in page
    # late rule: due date in the distant past -> scored test cells get the capped deduction
    instructor.post(f'/instructor/section/{sid}/gradebook/settings', data={
        'weight_tests': 70, 'weight_skills': 30, 'weight_quizzes': 0, 'policy': 'best', 'pass_mark': 80,
        'late_per_day': 5, 'late_max': 20, 'late_grace_hours': 0})
    before = _compute(app, mod)
    col = next(i for i, c in enumerate(before['columns']) if c['type'] == 'test' and c['id'] == ids['test'])
    raw = {r['user'].id: r['cells'][col]['score'] for r in before['rows']}
    instructor.post(f'/instructor/section/{sid}/gradebook/due', data={f"due_test_{ids['test']}": '2000-01-01T09:00'})
    after = _compute(app, mod)
    assert not after['cached'], 'due-date change invalidates the cache'
    hit = 0
    for r in after['rows']:
        c = r['cells'][col]
        if c['status'] == 'scored' and raw[r['user'].id] is not None:
            assert c['late_off'] == 20 and abs(c['score'] - max(0, raw[r['user'].id] - 20)) < 0.11
            hit += 1
    assert hit, 'some seeded attempts were penalised'
    assert after['summary']['late_cells'] == hit
    # clearing the due date removes the penalty; reset scale
    instructor.post(f'/instructor/section/{sid}/gradebook/due', data={f"due_test_{ids['test']}": ''})
    instructor.post(f'/instructor/section/{sid}/gradebook/scale', data={'action': 'reset'})
    instructor.post(f'/instructor/section/{sid}/gradebook/settings', data={
        'weight_tests': 70, 'weight_skills': 30, 'weight_quizzes': 0, 'policy': 'best', 'pass_mark': 80, 'late_per_day': 0})
    final = _compute(app, mod)
    assert final['summary']['late_cells'] == 0 and final['settings'].scale == G.DEFAULT_SCALE


def test_cache_hits_and_invalidates_on_new_attempt(app, mod, ids):
    first = _compute(app, mod)
    second = _compute(app, mod)
    assert second['cached'] and second['rows'] is first['rows'] or second['cached']
    with app.app_context():
        mod.db.session.add(mod.QuizAttempt(user_id=ids['student1'], quiz_id=ids['quiz'], score=77, section_id=1))
        mod.db.session.commit()
    assert not _compute(app, mod)['cached']


def test_gradebook_pagination_and_server_filter(instructor, ids):
    sid = ids['section']
    page = instructor.get(f'/instructor/section/{sid}/gradebook?per=25').get_data(as_text=True)
    assert 'Students per page' in page
    p2 = instructor.get(f'/instructor/section/{sid}/gradebook?per=25&page=999')
    assert p2.status_code == 200           # clamps to the last page
    one = instructor.get(f'/instructor/section/{sid}/gradebook?q=student1%40').get_data(as_text=True)
    assert 'filtered from' in one and one.count('data-risk=') == 1
