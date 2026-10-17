"""Pass 6: error pages, role guard, static caching, account page."""


def test_404_is_friendly_html(anon):
    r = anon.get('/no-such-page')
    assert r.status_code == 404
    body = r.get_data(as_text=True)
    assert 'find that page' in body and 'error-page' in body
    assert 'Werkzeug' not in body


def test_404_api_is_json(anon):
    r = anon.get('/api/does-not-exist')
    assert r.status_code == 404
    assert r.is_json and r.get_json()['error']


def test_wrong_role_gets_403_page(student):
    r = student.get('/admin')
    assert r.status_code == 403
    assert 'have access to this page' in r.get_data(as_text=True)


def test_anonymous_staff_page_redirects_to_login(anon):
    r = anon.get('/admin')
    assert r.status_code in (302, 303) and '/login' in r.headers['Location']


def test_versioned_static_is_immutable(app, anon):
    with app.test_request_context():
        from flask import url_for
        u = url_for('static', filename='css/ciwt-ui.css')
    assert '?v=' in u
    r = anon.get(u)
    assert r.status_code == 200
    assert 'immutable' in r.headers.get('Cache-Control', '')
    r2 = anon.get('/static/css/ciwt-ui.css')
    assert 'max-age=86400' in r2.headers.get('Cache-Control', '')


def test_account_page_every_role(student, instructor, admin):
    for c in (student, instructor, admin):
        r = c.get('/account')
        assert r.status_code == 200
        assert 'Change password' in r.get_data(as_text=True)


def test_account_requires_login(anon):
    r = anon.get('/account')
    assert r.status_code in (302, 303)


def test_password_change_validation_and_success(app, student2):
    r = student2.post('/account', data={'current_password': 'wrong', 'new_password': 'short', 'confirm_password': 'x'})
    assert r.status_code == 400
    body = r.get_data(as_text=True)
    assert 'not your current password' in body and 'at least 8' in body and 'do not match' in body
    r = student2.post('/account', data={'current_password': 'student123', 'new_password': 'longer-pass-1',
                                        'confirm_password': 'longer-pass-1'})
    assert r.status_code in (302, 303)
    fresh = app.test_client()
    assert fresh.post('/login', data={'email': 'student2@lms.local', 'password': 'longer-pass-1'}).status_code in (302, 303)
    # restore for other tests
    r = student2.post('/account', data={'current_password': 'longer-pass-1', 'new_password': 'student123',
                                        'confirm_password': 'student123'})
    assert r.status_code in (302, 303)


def test_favicon_redirects_to_small_png(anon):
    r = anon.get('/favicon.ico')
    assert r.status_code == 301 and 'favicon-32.png' in r.headers['Location']


def test_base_loads_icons_without_blocking(student):
    body = student.get('/student').get_data(as_text=True)
    assert 'rel="preload" as="style" href="https://cdn.jsdelivr.net/npm/bootstrap-icons' in body
    assert 'onsubmit="return confirm' not in body
