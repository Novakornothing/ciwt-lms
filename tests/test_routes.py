"""Every key page returns 200 for the roles that should see it (and never 500)."""
import pytest

PUBLIC = ['/', '/login', '/demo', '/gaps', '/healthz', '/policy/attention']


def student_pages(i):
    return ['/student', f"/student/section/{i['section']}",             f"/student/module/{i['section']}/{i['module']}/lesson/{i['lesson']}", f"/student/quiz/{i['section']}/{i['quiz']}",
            '/labs', f"/class/{i['section']}/labs", f"/class/{i['section']}/curriculum", '/student/grades',
            f"/student/section/{i['section']}/grades", '/student/attention', '/helix/consent', '/messages', '/tickets',
            '/search?q=cpu', '/policy/attention', '/convening', '/aschool']


def instructor_pages(i):
    s = i['section']
    return ['/instructor', f'/instructor/section/{s}', f'/instructor/section/{s}/attention',
            f"/instructor/section/{s}/attention/student/{i['student1']}", f"/instructor/section/{s}/attention/lesson/{i['lesson']}",
            f'/instructor/section/{s}/gradebook', f"/instructor/section/{s}/gradebook/student/{i['student1']}",
            f"/analysis/test/{i['test']}", f"/instructor/section/{s}/test/{i['test']}/performance", '/instructor/analytics',
            f"/student/module/{s}/{i['module']}/lesson/{i['lesson']}", f'/class/{s}/tqi', f'/class/{s}/skills', '/pilot']


ADMIN = ['/admin', '/admin/classes', '/admin/people', '/admin/curriculum', '/admin/tqi', '/admin/test-analytics', '/admin/teaching-time', '/admin/audit', '/admin/readiness', '/admin/tickets']


@pytest.mark.parametrize('path', PUBLIC)
def test_public(anon, path):
    assert anon.get(path).status_code == 200


def test_student_pages(student, ids):
    bad = {p: student.get(p).status_code for p in student_pages(ids)}
    assert all(v == 200 for v in bad.values()), {k: v for k, v in bad.items() if v != 200}


def test_module_hub_opens_first_lesson(student, ids):
    r = student.get(f"/student/module/{ids['section']}/{ids['module']}", follow_redirects=True)
    assert r.status_code == 200


def test_instructor_pages(instructor, ids):
    bad = {p: instructor.get(p).status_code for p in instructor_pages(ids)}
    assert all(v == 200 for v in bad.values()), {k: v for k, v in bad.items() if v != 200}


def test_admin_pages(admin, ids):
    paths = ADMIN + instructor_pages(ids)
    bad = {p: admin.get(p).status_code for p in paths}
    assert all(v == 200 for v in bad.values()), {k: v for k, v in bad.items() if v != 200}


def test_csv_exports(instructor, ids):
    s = ids['section']
    for path in (f'/instructor/section/{s}/attention.csv', f'/instructor/section/{s}/attention-sessions.csv',
                 f'/instructor/section/{s}/gradebook.csv'):
        r = instructor.get(path)
        assert r.status_code == 200 and r.mimetype == 'text/csv', path
        assert len(r.data.splitlines()) > 2


def test_students_blocked_from_staff_pages(student, ids):
    s = ids['section']
    for path in (f'/instructor/section/{s}/attention', f'/instructor/section/{s}/gradebook',
                 f'/instructor/section/{s}/gradebook.csv', f'/api/helix/section/{s}/summary.json'):
        assert student.get(path).status_code == 403, path


def test_instructor_without_access_blocked(instructor2, ids):
    s = ids['section']
    assert instructor2.get(f'/instructor/section/{s}/attention').status_code == 403
    assert instructor2.get(f'/instructor/section/{s}/gradebook').status_code == 403


def test_anonymous_redirected(anon, ids):
    r = anon.get(f"/instructor/section/{ids['section']}/gradebook")
    assert r.status_code in (302, 401)
    assert anon.post('/api/helix/session/start', json={}).status_code in (302, 401)


def test_mobile_shell_markup(student):
    html = student.get('/student').get_data(as_text=True)
    assert 'mobile-tabbar' in html and 'rail-scrim' in html and 'ciwt-ui.css' in html
    assert 'aria-controls="staffRail"' in html
