"""Pass 7: the admin dashboard is split into an overview plus Classes, People, Curriculum and Quality/TQI."""
import pytest

PAGES = ['/admin', '/admin/classes', '/admin/people', '/admin/curriculum', '/admin/tqi']


@pytest.mark.parametrize('path', PAGES)
def test_admin_subpages_render_with_shared_nav(admin, path):
    r = admin.get(path)
    assert r.status_code == 200, path
    body = r.get_data(as_text=True)
    assert 'class="admin-tabs' in body
    for href in PAGES:
        assert f'href="{href}"' in body, (path, href)
    assert body.count('aria-current="page"') >= 1
    assert '<style>' not in body.split('<main', 1)[-1]          # no page-level style blocks


@pytest.mark.parametrize('path', PAGES[1:4])
def test_admin_subpages_are_admin_only(student, instructor, anon, path):
    assert student.get(path).status_code == 403
    assert instructor.get(path).status_code == 403
    r = anon.get(path)
    assert r.status_code in (302, 303) and '/login' in r.headers['Location']


def test_old_anchor_bookmarks_are_forwarded(admin):
    body = admin.get('/admin').get_data(as_text=True)
    for anchor, page in (('admin-class', '/admin/classes'), ('admin-sections', '/admin/classes'),
                         ('admin-course-instr', '/admin/curriculum'), ('admin-people', '/admin/people'),
                         ('admin-staff', '/admin/people')):
        assert f"'{anchor}': \"{page}#{anchor}\"" in body
    # and each target id exists on its new page
    for page, ids in (('/admin/classes', ('admin-class', 'admin-sections')), ('/admin/curriculum', ('admin-course-instr',)),
                      ('/admin/people', ('admin-people', 'admin-staff'))):
        html = admin.get(page).get_data(as_text=True)
        for i in ids:
            assert f'id="{i}"' in html, (page, i)


def test_overview_is_short_and_links_out(admin):
    body = admin.get('/admin').get_data(as_text=True)
    assert 'kpi-grid' in body and 'admin-hub' in body
    # the long forms now live on their own pages
    assert 'Create class section' not in body and 'Add instructor or admin' not in body


def test_forms_return_to_their_subpage(admin, app, mod):
    with app.app_context():
        course = mod.Course.query.first(); instr = mod.User.query.filter_by(role='instructor').first()
        cid, iid = course.id, instr.id
        sec = mod.ClassSection.query.first(); sid = sec.id
    r = admin.post('/admin/section/create', data={'name': 'Pass 7 Test Section', 'course_id': cid, 'instructor_id': iid, 'max_students': 20})
    assert r.status_code in (302, 303) and r.headers['Location'].split('#')[0].endswith('/admin/classes')
    r = admin.post('/admin/section/toggle', data={'section_id': sid})
    assert r.headers['Location'].split('#')[0].endswith('/admin/classes')
    admin.post('/admin/section/toggle', data={'section_id': sid})       # back to how it was
    r = admin.post('/admin/user/create', data={'first_name': 'Pat', 'last_name': 'Seven', 'email': 'pat.seven@lms.local', 'role': 'student'})
    assert r.headers['Location'].split('#')[0].endswith('/admin/people')
    r = admin.post('/admin/course/add-instructor', data={'course_id': cid, 'user_id': iid})
    assert r.headers['Location'].split('#')[0].endswith('/admin/curriculum')


def test_people_filter_and_search(admin):
    body = admin.get('/admin/people?role=admin').get_data(as_text=True)
    assert 'admin@lms.local' in body and 'student1@lms.local' not in body
    body = admin.get('/admin/people?q=student1%40').get_data(as_text=True)
    assert 'student1@lms.local' in body and 'student2@lms.local' not in body
    body = admin.get('/admin/people?q=zzzz-nobody').get_data(as_text=True)
    assert 'Nobody matches' in body


def test_instructor_mode_hides_admin_subpages(admin):
    admin.get('/admin/view-as/instructor')
    try:
        for path in PAGES[:4]:
            r = admin.get(path)
            assert r.status_code in (302, 303) and '/instructor' in r.headers['Location'], path
    finally:
        admin.get('/admin/view-as/admin')


def test_people_list_is_paginated_and_keeps_filters(admin, mod, monkeypatch):
    import re
    monkeypatch.setattr(mod, 'PEOPLE_PAGE_SIZE', 5)
    with mod.app.app_context():
        n_students = mod.User.query.filter_by(role='student').count()
        n_all = mod.User.query.count()
    assert n_students > 10
    emails = lambda b: re.findall(r'<td class="small text-break">([^<]+)</td>', b)
    p1 = admin.get('/admin/people?role=student').get_data(as_text=True)
    assert len(emails(p1)) == 5
    assert f'Showing 1–5 of {n_students}' in p1 and f'Everyone <span class="chip-count">{n_students}</span>' in p1
    assert 'aria-label="People list pages"' in p1 and 'href="/admin/people?role=student&amp;page=2#admin-users"' in p1
    p2 = admin.get('/admin/people?role=student&page=2').get_data(as_text=True)
    assert len(emails(p2)) == 5 and not set(emails(p1)) & set(emails(p2))
    assert 'rel="prev"' in p2 and 'aria-current="page">2<' in p2
    last = -(-n_students // 5)
    pl = admin.get(f'/admin/people?role=student&page={last + 7}').get_data(as_text=True)   # out of range clamps to last page
    assert f'of {n_students}' in pl and 'rel="next"' not in pl and f'aria-current="page">{last}<' in pl
    for b in (p1, p2, pl):
        assert b.count('role-badge role-student') == len(emails(b)) and 'role-badge role-admin' not in b
    allp = admin.get('/admin/people?page=0').get_data(as_text=True)                        # below range clamps to 1
    assert f'Showing 1–5 of {n_all}' in allp
    q = admin.get('/admin/people?q=student1%40').get_data(as_text=True)
    assert 'Showing 1–1 of 1' in q and 'People list pages' not in q                     # a single page needs no pager
