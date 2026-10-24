"""Launch prep: campus SSO (OIDC + SAML), multi-tenant isolation and branding, outcomes reporting, /healthz."""
import base64
import hashlib
import json
import time
import zlib
from datetime import date
from urllib.parse import parse_qs, urlparse

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from institutional import map_role, on_color
from institutional import oidc as O
from institutional import saml as S

KEY, CERT = S.self_signed()
SP_ACS = 'http://localhost/sso/{slug}/saml/acs'
SP_ENTITY = 'http://localhost/sso/{slug}/saml/metadata.xml'
IDP = 'https://idp.example.edu'


@pytest.fixture(scope='module')
def tenants(app, mod):
    """Two extra institutions: 'saml-college' (SAML) and 'oidc-command' (OIDC), each with an instructor and a class."""
    I = mod.institutional_api.Institution
    with app.app_context():
        out = {}
        for slug, proto in (('saml-college', 'saml'), ('oidc-command', 'oidc')):
            inst = I.query.filter_by(slug=slug).first()
            if not inst:
                cfg = ({'protocol': 'saml', 'idp_entity_id': IDP, 'idp_sso_url': IDP + '/sso', 'idp_cert': CERT,
                        'role_map': {'instructor': ['faculty'], 'admin': ['lms-admins']}}
                       if proto == 'saml' else
                       {'protocol': 'oidc', 'issuer': 'https://login.example.mil', 'client_id': 'ciwt-client',
                        'authorization_endpoint': 'https://login.example.mil/authorize',
                        'token_endpoint': 'https://login.example.mil/token', 'jwks_uri': 'https://login.example.mil/jwks',
                        'role_map': {'instructor': ['instructors']}})
                inst = I(slug=slug, name=slug.replace('-', ' ').title(), domain='example.edu' if proto == 'saml' else 'example.mil',
                         primary_color='#7a0019', accent_color='#ffcc33', sso_config_json=json.dumps(cfg), active=True)
                mod.db.session.add(inst)
                mod.db.session.commit()
            email = f'teach@{inst.domain}'
            u = mod.User.query.filter_by(email=email).first()
            if not u:
                u = mod.User(email=email, first_name='Tenant', last_name='Teacher', role='instructor', institution_id=inst.id)
                u.set_password('teach123')
                mod.db.session.add(u)
                mod.db.session.flush()
                mod.db.session.add(mod.ClassSection(name=f'{slug} Section 1', course_id=mod.Course.query.first().id,
                                                    instructor_id=u.id, institution_id=inst.id,
                                                    start_date=date(2026, 9, 1), is_active=True))
                mod.db.session.commit()
            out[slug] = {'id': inst.id, 'teacher': email, 'section': mod.ClassSection.query.filter_by(instructor_id=u.id).first().id}
        return out


def _login(c, email, pw):
    r = c.post('/login', data={'email': email, 'password': pw})
    assert r.status_code in (302, 303), (email, r.status_code)
    return c


def _resp(slug, email, rid=None, attrs=None, **kw):
    return S.build_response(idp_entity_id=IDP, sp_entity_id=SP_ENTITY.format(slug=slug), acs_url=SP_ACS.format(slug=slug),
                            email=email, in_response_to=rid, attrs=attrs or {}, key_pem=KEY, cert_pem=CERT, **kw)


def _start_saml(c, slug):
    r = c.get(f'/sso/{slug}/login')
    assert r.status_code == 302 and r.location.startswith(IDP + '/sso?')
    q = parse_qs(urlparse(r.location).query)
    req = zlib.decompress(base64.b64decode(q['SAMLRequest'][0]), -15).decode()
    return req.split('ID="')[1].split('"')[0], q['RelayState'][0]


# ------------------------------------------------------------------ pure helpers
def test_role_mapping_and_contrast():
    cfg = {'role_map': {'instructor': ['faculty'], 'admin': ['lms-admins']}}
    assert map_role({'groups': ['Faculty']}, cfg) == 'instructor'
    assert map_role({'groups': ['lms-admins', 'faculty']}, cfg) == 'admin'
    assert map_role({'groups': ['students']}, cfg) == 'student'
    assert map_role({'eduPersonAffiliation': ['faculty']}, {}) == 'instructor'
    assert map_role({'groups': ['admin']}, {}) == 'student'          # admin is never granted by default
    assert on_color('#ffcc33') == '#000000' and on_color('#1f3a5f') == '#ffffff'


def test_saml_validation_rejects_forgery_and_misuse():
    acs, sp = 'https://lms/acs', 'https://lms/sp'
    cfg = {'idp_entity_id': 'idp', 'idp_cert': CERT}
    mk = lambda **kw: S.build_response(**dict(dict(idp_entity_id='idp', sp_entity_id=sp, acs_url=acs, email='a@x.edu',   # noqa: E731
                                                   in_response_to='_r', key_pem=KEY, cert_pem=CERT), **kw))
    for what in ('assertion', 'response', 'both'):
        assert S.validate_response(mk(sign_what=what), cfg, sp, acs, '_r')['email'] == 'a@x.edu'
    b = mk()
    with pytest.raises(S.SamlError, match='digest'):
        S.validate_response(base64.b64encode(base64.b64decode(b).replace(b'a@x.edu', b'boss@x.edu')).decode(), cfg, sp, acs, '_r')
    ek, ec = S.self_signed('evil')
    with pytest.raises(S.SamlError, match='signature value'):
        S.validate_response(mk(key_pem=ek, cert_pem=ec), cfg, sp, acs, '_r')
    with pytest.raises(S.SamlError, match='Audience'):
        S.validate_response(b, cfg, 'https://someone-else/sp', acs, '_r')
    with pytest.raises(S.SamlError, match='InResponseTo'):
        S.validate_response(b, cfg, sp, acs, '_other')
    with pytest.raises(S.SamlError, match='no record'):
        S.validate_response(b, cfg, sp, acs, None)
    with pytest.raises(S.SamlError, match='signed'):
        S.validate_response(mk(sign_what='none'), cfg, sp, acs, '_r')
    with pytest.raises(S.SamlError, match='expired'):
        S.validate_response(mk(now=S._now().replace(year=2020)), cfg, sp, acs, '_r')
    with pytest.raises(S.SamlError, match='Destination'):
        S.validate_response(b, cfg, sp, 'https://lms/other-acs', '_r')
    xxe = base64.b64encode(b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>').decode()
    with pytest.raises(S.SamlError, match='DTD'):
        S.validate_response(xxe, cfg, sp, acs, '_r')


def test_oidc_pkce_and_id_token_checks():
    v, ch = O.pkce_pair()
    assert ch == base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b'=').decode()
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks = {'keys': [dict(json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key())), kid='k1', use='sig')]}
    cfg = {'issuer': 'https://idp', 'client_id': 'c'}
    now = int(time.time())
    good = dict(iss='https://idp', aud='c', sub='s1', iat=now, exp=now + 300, nonce='n1', email='x@y.mil')
    tok = lambda c, k=key: jwt.encode(c, k, algorithm='RS256', headers={'kid': 'k1'})   # noqa: E731
    assert O.validate_id_token(tok(good), cfg, 'n1', jwks)['sub'] == 's1'
    for bad, msg in ((dict(good, nonce='n2'), 'nonce'), (dict(good, aud='other'), 'rejected'),
                     (dict(good, iss='https://evil'), 'rejected'), (dict(good, exp=now - 3600), 'rejected')):
        with pytest.raises(O.OidcError, match=msg):
            O.validate_id_token(tok(bad), cfg, 'n1', jwks)
    with pytest.raises(O.OidcError):
        O.validate_id_token(tok(good, rsa.generate_private_key(public_exponent=65537, key_size=2048)), cfg, 'n1', jwks)
    with pytest.raises(O.OidcError, match='algorithm'):
        O.validate_id_token(jwt.encode(good, 'k' * 32, algorithm='HS256', headers={'kid': 'k1'}), cfg, 'n1', jwks)


# ------------------------------------------------------------------ SAML routes
def test_saml_metadata_login_acs_jit_and_replay(app, mod, tenants):
    slug = 'saml-college'
    c = app.test_client()
    md = c.get(f'/sso/{slug}/saml/metadata.xml')
    assert md.status_code == 200 and md.mimetype == 'application/samlmetadata+xml'
    assert b'AssertionConsumerService' in md.data and SP_ACS.format(slug=slug).encode() in md.data
    rid, relay = _start_saml(c, slug)
    resp = _resp(slug, 'prof.new@example.edu', rid, {'groups': ['faculty'], 'givenName': 'Pat', 'sn': 'Prof'})
    r = c.post(f'/sso/{slug}/saml/acs', data={'SAMLResponse': resp, 'RelayState': relay})
    assert r.status_code == 302 and '/login' not in r.location
    with app.app_context():
        u = mod.User.query.filter_by(email='prof.new@example.edu').first()
        assert u and u.role == 'instructor' and u.institution_id == tenants[slug]['id'] and u.first_name == 'Pat'
    r = app.test_client().post(f'/sso/{slug}/saml/acs', data={'SAMLResponse': resp, 'RelayState': relay}, follow_redirects=True)
    assert b'Campus sign-in failed' in r.data
    r = app.test_client().post(f'/sso/{slug}/saml/acs', data={'SAMLResponse': _resp(slug, 'x@example.edu')}, follow_redirects=True)
    assert b'IdP-initiated login is disabled' in r.data


def test_saml_refuses_other_domains_and_cross_tenant_accounts(app, mod, tenants):
    for email, msg in (('someone@gmail.com', b'is not an address at'), ('teach@example.mil', b'is not an address at')):
        c = app.test_client()
        rid, relay = _start_saml(c, 'saml-college')
        r = c.post('/sso/saml-college/saml/acs', data={'SAMLResponse': _resp('saml-college', email, rid), 'RelayState': relay},
                   follow_redirects=True)
        assert msg in r.data
    # an address on the college's domain that already belongs to another tenant is not taken over
    with app.app_context():
        if not mod.User.query.filter_by(email='moved@example.edu').first():
            u = mod.User(email='moved@example.edu', first_name='M', last_name='V', role='student',
                         institution_id=tenants['oidc-command']['id'])
            u.set_password('x' * 12)
            mod.db.session.add(u)
            mod.db.session.commit()
    c = app.test_client()
    rid, relay = _start_saml(c, 'saml-college')
    r = c.post('/sso/saml-college/saml/acs', data={'SAMLResponse': _resp('saml-college', 'moved@example.edu', rid),
                                                    'RelayState': relay}, follow_redirects=True)
    assert b'different institution' in r.data


# ------------------------------------------------------------------ OIDC route flow with a fake IdP
def test_oidc_login_flow_with_fake_idp(app, mod, tenants, monkeypatch):
    slug = 'oidc-command'
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks = {'keys': [dict(json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key())), kid='k', use='sig')]}
    state = {}

    def fake_http(method, url, data=None, headers=None):
        if url.endswith('/token'):
            assert data['code'] == 'abc' and len(data['code_verifier']) >= 43 and data['grant_type'] == 'authorization_code'
            now = int(time.time())
            claims = dict(iss='https://login.example.mil', aud='ciwt-client', sub='mil-123', iat=now, exp=now + 300,
                          nonce=state['nonce'], email='Sailor.One@example.mil', given_name='Sailor', family_name='One',
                          groups=['students'])
            return {'id_token': jwt.encode(claims, key, algorithm='RS256', headers={'kid': 'k'}), 'access_token': 'at'}
        if url.endswith('/jwks'):
            return jwks
        raise AssertionError(url)

    monkeypatch.setattr(mod.institutional_api, 'http', fake_http)
    c = app.test_client()
    q = parse_qs(urlparse(c.get(f'/sso/{slug}/login?next=/portfolio').location).query)
    assert q['code_challenge_method'] == ['S256'] and q['client_id'] == ['ciwt-client'] and q['nonce'] and q['state']
    assert b'did not match this browser' in c.get(f'/sso/{slug}/oidc/callback?code=abc&state=wrong', follow_redirects=True).data
    q = parse_qs(urlparse(c.get(f'/sso/{slug}/login?next=/portfolio').location).query)
    state['nonce'] = q['nonce'][0]
    r = c.get(f'/sso/{slug}/oidc/callback?code=abc&state={q["state"][0]}')
    assert r.status_code == 302 and r.location.endswith('/portfolio')
    with app.app_context():
        u = mod.User.query.filter_by(email='sailor.one@example.mil').first()
        assert u.role == 'student' and u.institution_id == tenants[slug]['id']
        assert mod.institutional_api.SsoIdentity.query.filter_by(user_id=u.id, subject='mil-123').count() == 1
    page = c.get('/portfolio').get_data(as_text=True)
    assert 'tenant-banner' in page and 'Oidc Command' in page


# ------------------------------------------------------------------ isolation + branding
def test_tenant_isolation_for_instructors(app, tenants, instructor):
    a, b = tenants['saml-college'], tenants['oidc-command']
    other = _login(app.test_client(), a['teacher'], 'teach123')
    for url in (f'/instructor/section/{b["section"]}', f'/instructor/section/{b["section"]}/gradebook',
                f'/instructor/section/{b["section"]}/mastery', f'/instructor/section/{b["section"]}/outcomes',
                '/instructor/section/1/gradebook', '/instructor/section/1/mastery', '/instructor/section/1/outcomes'):
        assert other.get(url).status_code in (302, 403, 404), url
    assert other.get(f'/instructor/section/{a["section"]}/outcomes').status_code == 200
    for url in (f'/instructor/section/{a["section"]}/gradebook', f'/instructor/section/{a["section"]}/outcomes'):
        assert instructor.get(url).status_code in (302, 403, 404), url


def test_institution_admin_is_fenced(app, mod, tenants, admin):
    with app.app_context():
        if not mod.User.query.filter_by(email='it.admin@example.edu').first():
            u = mod.User(email='it.admin@example.edu', first_name='IT', last_name='Admin', role='admin',
                         institution_id=tenants['saml-college']['id'])
            u.set_password('admin123')
            mod.db.session.add(u)
            mod.db.session.commit()
    ta = _login(app.test_client(), 'it.admin@example.edu', 'admin123')
    assert ta.get('/admin/people').status_code == 403 and ta.get('/admin').status_code == 403
    page = ta.get('/admin/institutions').get_data(as_text=True)
    assert 'Saml College' in page and 'Oidc Command' not in page
    assert ta.get(f'/admin/institutions/{tenants["oidc-command"]["id"]}').status_code == 404
    assert ta.get(f'/instructor/section/{tenants["oidc-command"]["section"]}/gradebook').status_code in (302, 403, 404)
    assert ta.get(f'/instructor/section/{tenants["saml-college"]["section"]}/outcomes').status_code == 200
    assert ta.get('/admin/outcomes').status_code == 200
    page = admin.get('/admin/institutions').get_data(as_text=True)
    assert 'Saml College' in page and 'Oidc Command' in page
    assert admin.post('/admin/institutions', data={'name': 'Bad', 'slug': 'NO SPACES', 'sso_config_json': '{}'}).status_code == 400
    r = admin.post(f'/admin/institutions/{tenants["saml-college"]["id"]}',
                   data={'name': 'Saml College', 'slug': 'saml-college', 'active': '1', 'primary_color': '#7a0019',
                         'accent_color': '#ffcc33', 'domain': 'example.edu', 'sso_config_json': '{"protocol": "ldap"}'})
    assert r.status_code == 400


def test_branding_and_login_picker(app, tenants):
    c = app.test_client()
    page = c.get('/t/saml-college').get_data(as_text=True)
    assert 'Sign in with your campus ID' in page and 'tenant-banner' in page and '/t/saml-college/theme.css' in page
    css = c.get('/t/saml-college/theme.css').get_data(as_text=True)
    assert '--tenant-primary:#7a0019' in css and '--tenant-on-primary:#ffffff' in css
    login = c.get('/login').get_data(as_text=True)
    assert 'Sign in with your campus ID' in login and 'value="saml-college" selected' in login
    assert c.get('/t/no-such-college').status_code == 404
    assert c.get('/sso/start?tenant=saml-college').location.endswith('/sso/saml-college/login')


# ------------------------------------------------------------------ outcomes + healthz
def test_outcomes_report_is_real_and_labelled(app, instructor, admin, student):
    page = instructor.get('/instructor/section/1/outcomes').get_data(as_text=True)
    for s in ('Contains demo seed data', 'Right first time', 'Which explanation resolved the struggle',
              'Lab process proficiency', 'Certification domain readiness', 'Study time logged'):
        assert s in page, s
    r = instructor.get('/instructor/section/1/outcomes?format=csv')
    assert r.status_code == 200 and r.mimetype == 'text/csv'
    rows = r.get_data(as_text=True).splitlines()
    assert rows[0] == 'metric,scope,value,denominator,note' and 'contains demo seed data' in rows[1]
    assert any(x.startswith('ladder_resolved_by,R2') for x in rows) and any(x.startswith('lab_diagnosed_first_pct') for x in rows)
    assert student.get('/instructor/section/1/outcomes').status_code in (302, 403)
    assert admin.get('/admin/outcomes').status_code == 200 and admin.get('/admin/outcomes?format=csv').status_code == 200


def test_outcomes_empty_class_reports_no_data_not_zero(app, tenants):
    t = _login(app.test_client(), tenants['oidc-command']['teacher'], 'teach123')
    rows = t.get(f'/instructor/section/{tenants["oidc-command"]["section"]}/outcomes?format=csv').get_data(as_text=True).splitlines()
    assert 'objective_right_first_time_pct,all,,0,student-objective pairs' in rows
    assert 'recorded activity only' in rows[1]


def test_healthz(anon):
    r = anon.get('/healthz')
    body = r.get_json()
    assert r.status_code == 200 and body['ok'] and body['database'] == 'ok' and body['storage']['backend'] == 'sqlite'
