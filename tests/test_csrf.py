"""CSRF protection: forms, fetch/JSON (header), Helix sendBeacon (body token), exempt bearer APIs."""
import glob
import json
import re

import pytest


@pytest.fixture
def csrf_on(app):
    app.config['WTF_CSRF_ENABLED'] = True
    yield
    app.config['WTF_CSRF_ENABLED'] = False


def token_from(html):
    m = re.search(r'name="csrf-token" content="([^"]+)"', html) or re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, 'page has no csrf token'
    return m.group(1)


def login(client, email='student1@lms.local', pw='student123'):
    tok = token_from(client.get('/login').get_data(as_text=True))
    r = client.post('/login', data={'email': email, 'password': pw, 'csrf_token': tok})
    assert r.status_code == 302
    return client


def test_every_post_form_has_token():
    missing = []
    for f in glob.glob('templates/**/*.html', recursive=True):
        for m in re.finditer(r'<form\b[^>]*method=["\']post["\'][^>]*>(.{0,120})', open(f).read(), re.I | re.S):
            # forms that post to another site (the LMS deep-link return) must NOT carry our token
            if 'csrf_token' not in m.group(1) and 'data-external-post' not in m.group(0):
                missing.append(f)
    assert not missing, missing


def test_form_post_without_token_rejected(app, csrf_on):
    c = app.test_client()
    r = c.post('/login', data={'email': 'student1@lms.local', 'password': 'student123'})
    assert r.status_code == 400 and b'could not be verified' in r.data
    login(c)  # with token works


def test_json_post_needs_header(app, csrf_on):
    c = login(app.test_client())
    assert c.post('/api/helix/consent', json={'agree': True}).get_json()['error'] == 'csrf'
    tok = token_from(c.get('/student').get_data(as_text=True))
    r = c.post('/api/helix/consent', json={'agree': True}, headers={'X-CSRFToken': tok})
    assert r.status_code == 200 and r.get_json()['granted']


def test_beacon_body_token(app, csrf_on, ids):
    c = login(app.test_client())
    tok = token_from(c.get('/student').get_data(as_text=True))
    h = {'X-CSRFToken': tok}
    c.post('/api/helix/consent', json={'agree': True}, headers=h)
    sid = c.post('/api/helix/session/start', json={'lesson_id': ids['lesson'], 'section_id': ids['section']}, headers=h).get_json()['session_id']
    # sendBeacon: text/plain-ish body, no headers -> token must be in the body
    bad = c.post(f'/api/helix/session/{sid}/batch', data=json.dumps({'seq': 0}), content_type='application/json')
    assert bad.status_code == 400 and bad.get_json()['error'] == 'csrf'
    ok = c.post(f'/api/helix/session/{sid}/batch', data=json.dumps({'seq': 0, '_csrf': tok, 'end': True}), content_type='application/json')
    assert ok.status_code == 200 and ok.get_json()['status'] == 'ended'


def test_token_from_other_session_rejected(app, csrf_on):
    a = login(app.test_client())
    b = login(app.test_client(), 'student2@lms.local')
    tok_a = token_from(a.get('/student').get_data(as_text=True))
    assert b.post('/api/helix/consent', json={'agree': True}, headers={'X-CSRFToken': tok_a}).status_code == 400


def test_bearer_api_exempt(app, csrf_on):
    r = app.test_client().post('/api/tqi/login', json={'email': 'nobody@x', 'password': 'x'})
    assert r.status_code == 401  # reached the view: not blocked by CSRF
