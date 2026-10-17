"""Pass 7: Post/Redirect/Get for quiz and test submissions.

Submitting answers a 303 to the attempt's own results URL, so reloading the results page is a plain GET
that never offers to resubmit. Results are rebuilt from the stored attempt."""
import json

import pytest


def _release(app, mod, ids, test_id):
    with app.app_context():
        if not mod.ContentRelease.query.filter_by(section_id=ids['section'], content_type='test', content_id=test_id,
                                                  user_id=ids['student1'], is_active=True).first():
            mod.db.session.add(mod.ContentRelease(section_id=ids['section'], content_type='test', content_id=test_id,
                                                  user_id=ids['student1'], is_active=True))
            mod.db.session.commit()


def test_quiz_submit_redirects_to_result(student, app, mod, ids):
    with app.app_context():
        qs = json.loads(mod.db.session.get(mod.Quiz, ids['quiz']).questions)
    data = {'q0': qs[0]['correct']}                      # one right, the rest blank
    r = student.post(f"/student/quiz/{ids['section']}/{ids['quiz']}", data=data)
    assert r.status_code == 303
    loc = r.headers['Location']
    assert f"/student/quiz/{ids['section']}/{ids['quiz']}/result/" in loc
    with app.app_context():
        n = mod.QuizAttempt.query.filter_by(user_id=ids['student1'], quiz_id=ids['quiz']).count()
    # the results page is a GET; loading it twice ("reload") creates no new attempt
    for _ in range(2):
        page = student.get(loc)
        assert page.status_code == 200
        body = page.get_data(as_text=True)
        assert f'1 of {len(qs)}' in body or f'1/{len(qs)}' in body or 'Focus' in body
    with app.app_context():
        assert mod.QuizAttempt.query.filter_by(user_id=ids['student1'], quiz_id=ids['quiz']).count() == n


def test_quiz_result_is_private(student, student2, anon, ids):
    loc = student.post(f"/student/quiz/{ids['section']}/{ids['quiz']}", data={}).headers['Location']
    assert student2.get(loc).status_code == 404
    r = anon.get(loc)
    assert r.status_code in (302, 303) and '/login' in r.headers['Location']
    # wrong quiz id in the URL
    other = loc.replace(f"/{ids['quiz']}/result/", f"/{ids['quiz'] + 999}/result/")
    assert student.get(other).status_code == 404


def test_test_submit_redirects_and_reload_is_safe(student, app, mod, ids):
    _release(app, mod, ids, ids['test'])
    url = f"/student/test/{ids['section']}/{ids['test']}"
    assert student.get(url).status_code == 200            # opens the attempt
    with app.app_context():
        qs = json.loads(mod.db.session.get(mod.KnowledgeTest, ids['test']).questions)
    r = student.post(url, data={f'q{i}': q['correct'] for i, q in enumerate(qs)})
    assert r.status_code == 303
    loc = r.headers['Location']
    assert '/result/' in loc and 'timed_out' not in loc
    with app.app_context():
        done = mod.TestAttempt.query.filter_by(user_id=ids['student1'], test_id=ids['test']).filter(
            mod.TestAttempt.completed_at.isnot(None)).count()
    for _ in range(2):
        page = student.get(loc)
        assert page.status_code == 200
        body = page.get_data(as_text=True)
        assert '100' in body and 'Submitted when time ran out' not in body
    with app.app_context():
        assert mod.TestAttempt.query.filter_by(user_id=ids['student1'], test_id=ids['test']).filter(
            mod.TestAttempt.completed_at.isnot(None)).count() == done


def test_test_timeout_flag_carries_through(student, app, mod, ids):
    _release(app, mod, ids, ids['test'])
    url = f"/student/test/{ids['section']}/{ids['test']}"
    student.get(url)
    r = student.post(url, data={'timed_out': '1'})
    assert r.status_code == 303 and 'timed_out=1' in r.headers['Location']
    body = student.get(r.headers['Location']).get_data(as_text=True)
    assert 'Submitted when time ran out' in body and 'Time expired' in body


def test_test_result_guards(student, student2, instructor, app, mod, ids):
    _release(app, mod, ids, ids['test'])
    url = f"/student/test/{ids['section']}/{ids['test']}"
    student.get(url)
    loc = student.post(url, data={}).headers['Location']
    assert student2.get(loc).status_code == 404
    assert instructor.get(loc).status_code == 200         # staff can open a student's result
    # an attempt that is still open sends you back to the test instead of showing a result
    student.get(url)
    with app.app_context():
        open_a = mod.TestAttempt.query.filter_by(user_id=ids['student1'], test_id=ids['test'], completed_at=None).first()
        assert open_a is not None
        aid = open_a.id
    r = student.get(f"{url}/result/{aid}")
    assert r.status_code == 302 and r.headers['Location'].endswith(url)


def test_practical_submit_redirects(student, app, mod, ids):
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, ids['section'])
        is_prac = lambda t: mod.is_practical_payload(json.loads(t.questions or '[]'))
        if not any(is_prac(t) for t in mod.KnowledgeTest.query.filter_by(course_id=sec.course_id)):
            mod.sync_skills_exams()      # a fresh seed has no skills exams until the startup sync runs
        prac = next((t for t in mod.KnowledgeTest.query.filter_by(course_id=sec.course_id).all()
                     if mod.is_practical_payload(json.loads(t.questions or '[]'))), None)
        if prac is None:
            pytest.skip('no skills practical in the seed data')
        pid = prac.id
    _release(app, mod, ids, pid)
    url = f"/student/test/{ids['section']}/{pid}"
    assert student.get(url).status_code == 200
    r = student.post(url, data={})
    assert r.status_code == 303 and '/result/' in r.headers['Location']
    page = student.get(r.headers['Location'])
    assert page.status_code == 200
    assert 'stations' in page.get_data(as_text=True).lower() or 'skill' in page.get_data(as_text=True).lower()
