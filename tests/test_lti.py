"""Pass 12: LTI 1.3 + LTI Advantage (tool side) against the in-repo mock platform
(tools/lti_mock_platform.py). The mock is not a real LMS; these tests are not 1EdTech conformance tests."""
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import jwt
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from lti_mock_platform import create_mock  # noqa: E402

from lti import core  # noqa: E402
from lti.http import Response  # noqa: E402
from lti.keys import ToolKeys, generate_private_pem, public_pem  # noqa: E402

MOCK = 'http://127.0.0.1:5088'


@pytest.fixture(scope='module')
def env(app, mod, tmp_path_factory):
    api = app.extensions['ciwt_lti']
    m = api.models
    old_keys, old_t = api.state['keys'], api.state['transport']
    api.state['keys'] = ToolKeys(str(tmp_path_factory.mktemp('lti-instance')))
    app.config['LTI_ALLOW_LOOPBACK_HTTP'] = True
    tool = app.test_client()
    mock = create_mock(base=MOCK, tool_base='http://localhost', fetch_json=lambda url: tool.get(urlparse(url).path).get_json())
    mc = mock.test_client()
    st = mock.config['MOCK']

    def transport(method, url, headers=None, data=None):
        u = urlparse(url)
        assert u.netloc == '127.0.0.1:5088', url
        path = u.path + ('?' + u.query if u.query else '')
        headers = dict(headers or {})
        ctype = headers.pop('Content-Type', None)
        r = mc.open(path, method=method, headers=headers, data=data, content_type=ctype)
        return Response(r.status_code, dict(r.headers), r.data)

    api.state['transport'] = transport
    api.jwks_cache.clear(); api.token_cache.clear()
    with app.app_context():
        max_uid = mod.db.session.query(mod.db.func.max(mod.User.id)).scalar()
        p = m.LtiPlatform(name='Mock LMS (test)', kind='other', issuer=st['issuer'], client_id=st['client_id'],
                          auth_login_url=MOCK + '/auth', auth_token_url=MOCK + '/token', jwks_url=MOCK + '/jwks',
                          deployment_ids_json=json.dumps([st['deployment_id']]))
        mod.db.session.add(p); mod.db.session.flush()
        teacher = mod.User.query.filter_by(email='instructor@lms.local').first()
        mod.db.session.add(m.LtiUserLink(platform_id=p.id, sub='mock-teacher-1', user_id=teacher.id, how='manual'))
        mod.db.session.commit()
        pid = p.id
    yield {'api': api, 'm': m, 'mock': mock, 'mc': mc, 'st': st, 'pid': pid}
    api.state['keys'], api.state['transport'] = old_keys, old_t
    with app.app_context():
        new = [u.id for u in mod.User.query.filter(mod.User.id > max_uid)]
        for M in (m.LtiSyncLog, m.LtiDeepLink, m.LtiResourceLink, m.LtiContext, m.LtiUserLink, m.LtiLogin, m.LtiPlatform):
            M.query.delete()
        if new:
            mod.QuizAttempt.query.filter(mod.QuizAttempt.user_id.in_(new)).delete()
            mod.Enrollment.query.filter(mod.Enrollment.user_id.in_(new)).delete()
            mod.User.query.filter(mod.User.id.in_(new)).delete()
        mod.db.session.commit()


def browser_launch(env, client, user, kind='launch', target=None, rl='rl-1'):
    """What a browser does: LMS → tool login → LMS auth → auto-posted form → tool launch."""
    mc = env['mc']
    q = f'/start?user={user}&kind={kind}&rl={rl}' + (f'&target={target}' if target else '')
    r = mc.get(q)
    assert r.status_code == 302
    r = client.get(r.headers['Location'])
    assert r.status_code == 302, r.data[:300]
    loc = urlparse(r.headers['Location'])
    assert loc.netloc == '127.0.0.1:5088' and loc.path == '/auth'
    r = mc.get(loc.path + '?' + loc.query)
    assert r.status_code == 200, r.data
    h = r.data.decode()
    tok = re.search(r'name="id_token" value="([^"]+)"', h).group(1)
    state = re.search(r'name="state" value="([^"]+)"', h).group(1)
    return client.post('/lti/launch', data={'id_token': tok, 'state': state}), tok, state


# ---------------------------------------------------------------- pure checks
def _reg(st):
    return {'issuer': st['issuer'], 'client_id': st['client_id'], 'deployment_ids': [st['deployment_id']]}


def test_id_token_validation_accepts_good_and_refuses_each_bad_claim(env):
    st = env['st']
    jwks = {'keys': [json.loads(env['mc'].get('/jwks').data)['keys'][0]]}
    good = st['id_token']('mock-student-1', nonce='n1')
    assert core.validate_id_token(st['sign'](good), _reg(st), jwks, 'n1')['sub'] == 'mock-student-1'
    other = generate_private_pem()
    cases = {
        'jwt_sig': (good, {'key': other}),
        'jwt_aud': (dict(good, aud='someone-else'), {}),
        'jwt_iss': (dict(good, iss='https://evil.example'), {}),
        'jwt_expired': (dict(good, exp=int(time.time()) - 600), {}),
        'nonce': (good, {'nonce': 'different'}),
        'deployment': (dict(good, **{core.CLAIM['deployment_id']: 'not-registered'}), {}),
        'version': (dict(good, **{core.CLAIM['version']: '1.1'}), {}),
        'message_type': (dict(good, **{core.CLAIM['message_type']: 'LtiSubmissionReviewRequest'}), {}),
        'jwt_azp': (dict(good, aud=[st['client_id'], 'x'], azp='x'), {}),
        'jwks_kid': (good, {'kid': 'unknown-kid'}),
    }
    for code, (claims, kw) in cases.items():
        tok = st['sign'](claims, key=kw.get('key'), kid_=kw.get('kid'))
        with pytest.raises(core.LtiError) as e:
            core.validate_id_token(tok, _reg(st), jwks, kw.get('nonce', 'n1'))
        assert e.value.code == code, (code, e.value.code)
    no_rl = dict(good); no_rl.pop(core.CLAIM['resource_link'])
    with pytest.raises(core.LtiError) as e:
        core.validate_id_token(st['sign'](no_rl), _reg(st), jwks, 'n1')
    assert e.value.code == 'resource_link'
    hs = jwt.encode(good, 'x' * 40, algorithm='HS256', headers={'kid': st['kid']})
    with pytest.raises(core.LtiError) as e:
        core.validate_id_token(hs, _reg(st), jwks, 'n1')
    assert e.value.code == 'jwt_alg'


def test_roles_map_to_instructor_or_student_and_never_admin():
    R = 'http://purl.imsglobal.org/vocab/lis/v2/'
    assert core.map_role([R + 'membership#Instructor']) == 'instructor'
    assert core.map_role([R + 'institution/person#Administrator']) == 'instructor'
    assert core.map_role([R + 'membership/Instructor#TeachingAssistant']) == 'instructor'
    assert core.map_role(['Instructor']) == 'instructor'                      # LTI 1.1-style short name
    assert core.map_role([R + 'membership#Learner']) == 'student'
    assert core.map_role([]) is None
    assert 'admin' not in {core.map_role([r]) for r in (R + 'system/person#Administrator', 'Administrator')}


def test_tool_jwks_is_public_only_and_key_lives_outside_git(env, anon):
    ks = anon.get('/lti/jwks').get_json()['keys']
    assert len(ks) == 1 and ks[0]['kid'] == env['api'].keys().kid and ks[0]['kty'] == 'RSA'
    assert not {'d', 'p', 'q', 'dp', 'dq', 'qi'} & set(ks[0])
    root = Path(__file__).resolve().parents[1]
    assert 'instance/' in (root / '.gitignore').read_text().split()


def test_env_key_takes_precedence_and_rotation_keeps_old_key_published(tmp_path):
    pem = generate_private_pem()
    k = ToolKeys(str(tmp_path), env={'LTI_PRIVATE_KEY': pem})
    assert k.private_pem == pem and k.source() == 'env LTI_PRIVATE_KEY' and not (tmp_path / 'lti').exists()
    k2 = ToolKeys(str(tmp_path), env={})
    (tmp_path / 'lti').mkdir(exist_ok=True); (tmp_path / 'lti' / 'previous').mkdir()
    (tmp_path / 'lti' / 'previous' / 'old.pem').write_text(public_pem(pem))
    kids = [x['kid'] for x in k2.jwks()['keys']]
    assert len(kids) == 2 and kids[1] == k.kid
    assert oct((tmp_path / 'lti' / 'tool_private.pem').stat().st_mode & 0o777) == '0o600'


# ---------------------------------------------------------------- launches
def test_login_refuses_unknown_platform_and_foreign_target(env, anon):
    assert anon.get('/lti/login?iss=https://nope.example&login_hint=x').status_code == 400
    r = anon.get(f'/lti/login?iss={env["st"]["issuer"]}&login_hint=x&target_link_uri=https://evil.example/lti/launch')
    assert r.status_code == 400 and b'target_link_uri' in r.data


def test_instructor_launch_maps_course_then_learner_launch_enrolls(app, mod, env):
    t = app.test_client()
    r, _, _ = browser_launch(env, t, 'mock-teacher-1', target='course')
    assert r.status_code == 302 and '/lti/context/' in r.headers['Location']          # unmapped: pick a class
    cid = int(re.search(r'/lti/context/(\d+)/map', r.headers['Location']).group(1))
    assert b'Connect' in t.get(f'/lti/context/{cid}/map').data
    assert t.post(f'/lti/context/{cid}/map', data={'section_id': 1}).status_code == 302
    s = app.test_client()
    r, tok, state = browser_launch(env, s, 'mock-student-1', target='quiz:1', rl='rl-quiz-1')
    with app.test_request_context():
        assert r.status_code == 302 and r.headers['Location'] == mod.url_for('take_quiz', section_id=1, quiz_id=1)
    with app.app_context():
        link = env['m'].LtiUserLink.query.filter_by(sub='mock-student-1').first()
        u = mod.db.session.get(mod.User, link.user_id)
        assert u.role == 'student' and link.how == 'created' and u.email == 'mock.learner1@mock-lms.invalid'
        assert mod.Enrollment.query.filter_by(user_id=u.id, section_id=1).count() == 1
        rl = env['m'].LtiResourceLink.query.filter_by(resource_link_id='rl-quiz-1').first()
        assert rl.target == 'quiz:1'
    # replaying the same state + id_token is refused (state is single-use)
    again = s.post('/lti/launch', data={'id_token': tok, 'state': state})
    assert again.status_code == 400 and b'already used' in again.data


def test_launch_without_the_state_cookie_is_refused(app, env):
    c = app.test_client()
    r = env['mc'].get('/start?user=mock-student-2&kind=launch')
    r = c.get(r.headers['Location'])
    loc = urlparse(r.headers['Location'])
    h = env['mc'].get(loc.path + '?' + loc.query).data.decode()
    tok = re.search(r'name="id_token" value="([^"]+)"', h).group(1)
    state = re.search(r'name="state" value="([^"]+)"', h).group(1)
    other = app.test_client()                                # a different browser
    r = other.post('/lti/launch', data={'id_token': tok, 'state': state})
    assert r.status_code == 400 and b'state_cookie' in r.data


def test_email_linking_is_opt_in_and_never_links_admins(app, mod, env):
    st, m = env['st'], env['m']
    st['people']['mock-admin-like'] = {'name': 'Mock Admin', 'given_name': 'Mock', 'family_name': 'Admin',
                                      'email': 'admin@lms.local', 'roles': ['http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator']}
    st['people']['mock-s1-email'] = {'name': 'S One', 'given_name': 'S', 'family_name': 'One', 'email': 'student1@lms.local',
                                    'roles': ['http://purl.imsglobal.org/vocab/lis/v2/membership#Learner']}
    with app.app_context():
        mod.db.session.get(m.LtiPlatform, env['pid']).link_by_email = True; mod.db.session.commit()
    try:
        browser_launch(env, app.test_client(), 'mock-admin-like', target='course')
        browser_launch(env, app.test_client(), 'mock-s1-email', target='course')
        with app.app_context():
            a = m.LtiUserLink.query.filter_by(sub='mock-admin-like').first()
            ua = mod.db.session.get(mod.User, a.user_id)
            assert ua.email != 'admin@lms.local' and ua.role == 'instructor' and a.how == 'created'
            s1 = m.LtiUserLink.query.filter_by(sub='mock-s1-email').first()
            assert s1.how == 'email' and mod.db.session.get(mod.User, s1.user_id).email == 'student1@lms.local'
            mod.db.session.delete(s1); mod.db.session.commit()   # leave student1 unlinked for later tests
    finally:
        with app.app_context():
            mod.db.session.get(m.LtiPlatform, env['pid']).link_by_email = False; mod.db.session.commit()
        st['people'].pop('mock-admin-like'); st['people'].pop('mock-s1-email')


# ---------------------------------------------------------------- deep linking
def ensure_course_mapped(app, env, section_id=1):
    """Pass 14: make the deep-link tests self-contained (they pass alone or under -k): map the mock LMS course to a
    class unless an earlier test already did, through the same instructor launch a teacher would use."""
    t = app.test_client()
    r, _, _ = browser_launch(env, t, 'mock-teacher-1', target='course', rl='rl-map-fixture')
    if r.status_code == 302 and '/lti/context/' in r.headers['Location'] and r.headers['Location'].endswith('/map'):
        cid = int(re.search(r'/lti/context/(\d+)/map', r.headers['Location']).group(1))
        assert t.post(f'/lti/context/{cid}/map', data={'section_id': section_id}).status_code == 302


def ensure_learner_launched(app, env):
    """Course mapped and mock-student-1 launched into quiz 1 (resource link rl-quiz-1), as the launch test does."""
    ensure_course_mapped(app, env)
    with app.app_context():
        have = (env['m'].LtiUserLink.query.filter_by(sub='mock-student-1').first() is not None and
                env['m'].LtiResourceLink.query.filter_by(resource_link_id='rl-quiz-1').first() is not None)
    if not have:
        r, _, _ = browser_launch(env, app.test_client(), 'mock-student-1', target='quiz:1', rl='rl-quiz-1')
        assert r.status_code == 302


def test_deep_linking_returns_signed_items_with_line_items_for_graded_ones(app, mod, env, ids):
    ensure_course_mapped(app, env)
    t = app.test_client()
    r, _, _ = browser_launch(env, t, 'mock-teacher-1', kind='deeplink')
    assert r.status_code == 302 and '/lti/deep-link/' in r.headers['Location']
    page = t.get(r.headers['Location'])
    h = page.data.decode()
    assert page.status_code == 200 and 'Add to “Mock LMS course 101 (demo)”' in h and f'value="lesson:{ids["lesson"]}"' in h
    lab = re.search(r'value="(lab:[^"]+)"', h).group(1)
    targets = [f'lesson:{ids["lesson"]}', 'quiz:1', lab, 'quiz:999999']
    dl_path = urlparse(r.headers['Location']).path
    r = t.post(dl_path, data={'target': targets, 'line_items': '1'})
    h = r.data.decode()
    assert r.status_code == 200 and 'action="http://127.0.0.1:5088/deep_link_return"' in h
    jwt_out = re.search(r'name="JWT" value="([^"]+)"', h).group(1)
    back = env['mc'].post('/deep_link_return', data={'JWT': jwt_out})
    assert back.status_code == 200 and b'Content added' in back.data
    c = env['st']['deep_links'][-1]
    items = c[core.CLAIM['dl_items']]
    assert [i['custom']['ciwt_target'] for i in items] == targets[:3]               # unknown target dropped
    assert [bool(i.get('lineItem')) for i in items] == [False, True, True]
    assert c[core.CLAIM['dl_data']].startswith('mock-dl-') and c['aud'] == [env['st']['issuer']]
    again = t.post(dl_path, data={'target': targets[:1]})
    assert again.status_code == 400 and b'expired' in again.data                      # the picker is single-use
    assert t.get('/lti/deep-link/not-a-token').status_code == 404


def test_learners_cannot_deep_link(app, env):
    r, _, _ = browser_launch(env, app.test_client(), 'mock-student-2', kind='deeplink')
    assert r.status_code == 403


# ---------------------------------------------------------------- AGS + NRPS
def test_scores_go_to_the_lms_from_the_gradebook(app, mod, env, instructor):
    ensure_learner_launched(app, env)
    m = env['m']
    with app.app_context():
        uid = m.LtiUserLink.query.filter_by(sub='mock-student-1').first().user_id
        a = mod.QuizAttempt(user_id=uid, quiz_id=1, answers='{}', score=85.0, completed_at=mod.utcnow(), section_id=1)
        mod.db.session.add(a); mod.db.session.commit()
    r = instructor.post('/instructor/section/1/lti/scores')
    assert r.status_code == 303
    sent = [s for s in env['st']['scores'] if s['userId'] == 'mock-student-1']
    assert sent and sent[-1]['scoreGiven'] == 85.0 and sent[-1]['scoreMaximum'] == 100.0
    assert sent[-1]['activityProgress'] == 'Completed' and sent[-1]['gradingProgress'] == 'FullyGraded'
    with app.app_context():
        rl = m.LtiResourceLink.query.filter_by(resource_link_id='rl-quiz-1').first()
        assert rl.lineitem_url and rl.lineitem_url.startswith(MOCK + '/api/lineitems/')   # created via AGS
        log = m.LtiSyncLog.query.filter_by(kind='scores').order_by(m.LtiSyncLog.id.desc()).first()
        assert log.ok >= 1 and log.failed == 0
    h = instructor.get('/instructor/section/1/lti').data.decode()
    assert 'Mock LMS course 101 (demo)' in h and 'Send scores to the LMS' in h


def test_roster_sync_pages_enrolls_learners_and_removes_nobody(app, mod, env, instructor):
    ensure_learner_launched(app, env)
    with app.app_context():
        before = mod.Enrollment.query.filter_by(section_id=1).count()
    r = instructor.post('/instructor/section/1/lti/roster')
    assert r.status_code == 303
    m = env['m']
    with app.app_context():
        log = m.LtiSyncLog.query.filter_by(kind='roster').order_by(m.LtiSyncLog.id.desc()).first()
        assert log.skipped == 1 and log.failed == 0                       # mock-student-3 is Inactive
        two = m.LtiUserLink.query.filter_by(sub='mock-student-2').first()
        assert two and mod.Enrollment.query.filter_by(user_id=two.user_id, section_id=1).count() == 1
        assert m.LtiUserLink.query.filter_by(sub='mock-student-3').first() is None
        after = mod.Enrollment.query.filter_by(section_id=1).count()
        assert after >= before
        assert 'staff (not enrolled)' in log.detail


def test_lti_pages_access(admin, instructor, instructor2, student):
    assert admin.get('/admin/lti').status_code == 200
    assert b'Not yet 1EdTech-certified' in admin.get('/admin/lti').data
    assert instructor.get('/admin/lti').status_code == 403
    assert student.get('/instructor/section/1/lti').status_code == 403
    assert instructor2.get('/instructor/section/1/lti').status_code == 403
    assert instructor2.post('/instructor/section/1/lti/scores').status_code == 403


def test_admin_registration_form_validates_and_saves(app, admin, env):
    r = admin.post('/admin/lti/new?kind=canvas', data={'kind': 'canvas', 'name': 'Canvas test', 'issuer': 'https://canvas.instructure.com',
                                                       'client_id': '10000000000001', 'auth_login_url': 'http://insecure.example/auth',
                                                       'auth_token_url': 'https://sso.canvaslms.com/login/oauth2/token',
                                                       'jwks_url': 'https://sso.canvaslms.com/api/lti/security/jwks', 'deployment_ids': ''})
    assert r.status_code == 200 and b'must be a full https://' in r.data and b'Add at least one deployment ID' in r.data
    r = admin.post('/admin/lti/new', data={'kind': 'canvas', 'name': 'Canvas test', 'issuer': 'https://canvas.instructure.com',
                                           'client_id': '10000000000001', 'auth_login_url': 'https://sso.canvaslms.com/api/lti/authorize_redirect',
                                           'auth_token_url': 'https://sso.canvaslms.com/login/oauth2/token',
                                           'jwks_url': 'https://sso.canvaslms.com/api/lti/security/jwks',
                                           'deployment_ids': '1:abc\n2:def', 'create_accounts': '1', 'active': '1'})
    assert r.status_code == 303
    with app.app_context():
        p = env['m'].LtiPlatform.query.filter_by(client_id='10000000000001').first()
        assert p.deployment_ids == ['1:abc', '2:def'] and p.active and not p.link_by_email
    cfg = admin.get('/lti/config/canvas.json').get_json()
    assert cfg['oidc_initiation_url'].endswith('/lti/login') and cfg['public_jwk_url'].endswith('/lti/jwks')


def test_service_urls_must_be_https_outside_loopback():
    from lti.http import url_allowed
    assert url_allowed('https://lms.example/api') and not url_allowed('http://lms.example/api')
    assert not url_allowed('http://127.0.0.1:5088/x') and url_allowed('http://127.0.0.1:5088/x', allow_loopback_http=True)
    assert not url_allowed('file:///etc/passwd', True)
    assert core.scores_url('https://m.example/mod/lti/services.php/2/lineitems/7/lineitem?type_id=3') == \
        'https://m.example/mod/lti/services.php/2/lineitems/7/lineitem/scores?type_id=3'
