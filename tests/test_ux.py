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
    assert 'rel="preload" as="style" href="/static/vendor/bootstrap-icons/1.11.3/bootstrap-icons-subset.css' in body
    assert 'onsubmit="return confirm' not in body


def test_no_third_party_assets(anon, student):
    """Pass 7: CSS, JS and fonts are self-hosted, so no page waits on a CDN."""
    import re
    for client, path in ((anon, '/login'), (student, '/student'), (anon, '/')):
        body = client.get(path).get_data(as_text=True)
        ext = re.findall(r'<(?:link|script)[^>]+(?:href|src)="(https?://[^"]+)"', body)
        assert ext == [], (path, ext)
        assert 'fonts.googleapis' not in body and 'cdn.jsdelivr' not in body


def test_vendor_assets_served_and_cached(anon):
    for path in ('/static/vendor/bootstrap/5.3.3/bootstrap.min.css', '/static/vendor/bootstrap/5.3.3/bootstrap.bundle.min.js',
                 '/static/vendor/bootstrap-icons/1.11.3/bootstrap-icons-subset.css',
                 '/static/vendor/fonts/v1/fonts.css', '/static/vendor/fonts/v1/ibm-plex-sans-400-700-latin.woff2'):
        r = anon.get(path)
        assert r.status_code == 200, path
        # versioned directory => immutable even without ?v= (fonts are referenced by url() inside CSS)
        assert 'immutable' in r.headers.get('Cache-Control', ''), path
        r.close()


def test_responses_are_compressed(anon):
    r = anon.get('/login', headers={'Accept-Encoding': 'gzip'})
    assert r.headers.get('Content-Encoding') == 'gzip'
    assert 'Accept-Encoding' in r.headers.get('Vary', '')
    r = anon.get('/login', headers={'Accept-Encoding': 'br, gzip'})
    assert r.headers.get('Content-Encoding') == 'br'
    r = anon.get('/static/vendor/bootstrap/5.3.3/bootstrap.min.css', headers={'Accept-Encoding': 'br'})
    assert r.headers.get('Content-Encoding') == 'br'
    assert len(r.get_data()) < 60_000          # ~230 KB raw
    r.close()
    # images and fonts are already compressed: untouched
    r = anon.get('/static/vendor/fonts/v1/ibm-plex-sans-400-700-latin.woff2', headers={'Accept-Encoding': 'br, gzip'})
    assert 'Content-Encoding' not in r.headers
    r.close()


def test_icon_subset_covers_every_icon_used():
    """The icon font is subset to the icons the app uses; a new icon needs tools/build_icon_subset.py."""
    import pathlib, re, sys
    root = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tools'))
    import build_icon_subset as b
    css = (b.ICONS / 'bootstrap-icons-subset.css').read_text()
    have = set(re.findall(r'\.bi-([a-z0-9-]+)::before', css))
    defined = set(re.findall(r'\.bi-([a-z0-9-]+)::before', b.FULL_CSS.read_text()))
    used = b.used_icons()
    assert used - defined == set(), f'not Bootstrap Icons names: {sorted(used - defined)}'
    assert used - have == set(), f'run tools/build_icon_subset.py; missing: {sorted(used - have)}'
    font = re.search(r'url\("fonts/([^"]+)"\)', css).group(1)
    assert (b.ICONS / 'fonts' / font).is_file()


def test_single_blocking_css_bundle(anon):
    import re
    html = anon.get('/login').get_data(as_text=True)
    blocking = re.findall(r'<link[^>]+rel="stylesheet"[^>]*>', re.sub(r'<noscript>.*?</noscript>', '', html, flags=re.S))
    assert len(blocking) == 1 and '/assets/app-' in blocking[0]
    url = re.search(r'/assets/app-[0-9a-f]{12}\.css', blocking[0]).group(0)
    r = anon.get(url, headers={'Accept-Encoding': 'identity'})
    css = r.get_data(as_text=True)
    assert r.status_code == 200 and r.mimetype == 'text/css'
    assert 'immutable' in r.headers['Cache-Control']
    # cascade order: Bootstrap first, app CSS after it
    assert css.index('bootstrap.min.css') < css.index('novak-theme.css') < css.index('novak-ui.css') < css.index('helix.css')
    assert '.mobile-tabbar' in css and '@font-face' in css
    assert '../img/' not in css and 'url(/static/vendor/fonts/v1/ibm-plex-sans-400-700-latin.woff2)' in css
    # the font preload uses the same URL, so the font is fetched once
    assert 'href="/static/vendor/fonts/v1/ibm-plex-sans-400-700-latin.woff2"' in html
    br = anon.get(url, headers={'Accept-Encoding': 'br, gzip'})
    assert br.headers.get('Content-Encoding') in ('br', 'gzip') and len(br.data) < len(r.data) / 3
    stale = anon.get('/assets/app-000000000000.css')
    assert stale.status_code == 302 and stale.headers['Location'].endswith(url)
