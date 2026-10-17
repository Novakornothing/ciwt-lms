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
