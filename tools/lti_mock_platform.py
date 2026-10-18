"""A small mock LTI 1.3 platform ("Mock LMS") for tests and local demos. NOT a real LMS and not a
conformance suite; it does just enough of the platform side to exercise this tool:
OIDC auth redirect + signed id_token (resource link and deep linking), platform JWKS, OAuth2
client-credentials token (verifies the tool's client assertion against the tool JWKS), AGS line items
and scores, NRPS memberships with paging, and the deep-linking return (verifies the tool's JWT).

  python tools/lti_mock_platform.py --tool http://127.0.0.1:5078 --port 5088
then register it in the tool (Admin → LMS (LTI)) with the values printed at start-up and open
http://127.0.0.1:5088/ to launch. Everything lives in memory. Demo people are fictional.
"""
import argparse
import html
import json
import secrets
import time
import urllib.parse
import urllib.request
import uuid

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, Response, jsonify, request
from jwt.algorithms import RSAAlgorithm

C = 'https://purl.imsglobal.org/spec/lti/claim/'
R = 'http://purl.imsglobal.org/vocab/lis/v2/membership#'
AGS = 'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint'
NRPS = 'https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice'
DLS = 'https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings'
SC = 'https://purl.imsglobal.org/spec/lti-ags/scope/'
NRPS_SCOPE = 'https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly'

DEMO_PEOPLE = {   # fictional demo people (mock platform only)
    'mock-teacher-1': {'name': 'Demo Teacher (mock LMS)', 'given_name': 'Demo', 'family_name': 'Teacher',
                       'email': 'mock.teacher@mock-lms.invalid', 'roles': [R + 'Instructor']},
    'mock-student-1': {'name': 'Demo Learner One (mock LMS)', 'given_name': 'Demo', 'family_name': 'Learner One',
                       'email': 'mock.learner1@mock-lms.invalid', 'roles': [R + 'Learner']},
    'mock-student-2': {'name': 'Demo Learner Two (mock LMS)', 'given_name': 'Demo', 'family_name': 'Learner Two',
                       'email': 'mock.learner2@mock-lms.invalid', 'roles': [R + 'Learner']},
    'mock-student-3': {'name': 'Demo Learner Three (mock LMS)', 'given_name': 'Demo', 'family_name': 'Learner Three',
                       'email': 'mock.learner3@mock-lms.invalid', 'roles': [R + 'Learner'], 'status': 'Inactive'},
}


def _pem_pair():
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    pub = k.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return priv, pub


def _urlopen_get_json(url):
    with urllib.request.urlopen(url, timeout=10) as r:  # noqa: S310 (local mock only)
        return json.loads(r.read().decode())


def create_mock(base='http://127.0.0.1:5088', tool_base='http://127.0.0.1:5078', client_id='mock-client-1',
                deployment_id='mock-deployment-1', issuer=None, fetch_json=None):
    """fetch_json(url) → dict, used to read the tool JWKS (tests pass the tool's test client)."""
    app = Flask('lti_mock_platform')
    priv, pub = _pem_pair()
    kid = 'mock-key-' + uuid.uuid4().hex[:8]
    st = {'base': base.rstrip('/'), 'tool': tool_base.rstrip('/'), 'client_id': client_id, 'deployment_id': deployment_id,
          'issuer': issuer or base.rstrip('/'), 'priv': priv, 'kid': kid, 'pub': pub, 'pending': {}, 'tokens': {},
          'lineitems': {}, 'scores': [], 'deep_links': [], 'people': dict(DEMO_PEOPLE), 'page_size': 2,
          'context': {'id': 'mock-course-101', 'label': 'MOCK101', 'title': 'Mock LMS course 101 (demo)',
                      'type': ['http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering']},
          'fetch_json': fetch_json or _urlopen_get_json, 'used_jti': set(), 'next_iat_offset': 0}
    app.config['MOCK'] = st

    def jwk():
        k = json.loads(RSAAlgorithm.to_jwk(RSAAlgorithm(RSAAlgorithm.SHA256).prepare_key(st['pub'])))
        k.update({'kid': st['kid'], 'alg': 'RS256', 'use': 'sig'})
        return k

    def b(path):
        return st['base'] + path

    def id_token(user, kind='launch', target=None, rl_id='rl-1', nonce=None, extra=None):
        p = st['people'][user]
        now = int(time.time()) + st['next_iat_offset']
        claims = {'iss': st['issuer'], 'aud': st['client_id'], 'azp': st['client_id'], 'sub': user,
                  'iat': now, 'exp': now + 300, 'nonce': nonce or secrets.token_urlsafe(8),
                  'name': p['name'], 'given_name': p['given_name'], 'family_name': p['family_name'], 'email': p['email'],
                  C + 'version': '1.3.0', C + 'deployment_id': st['deployment_id'], C + 'roles': p['roles'],
                  C + 'context': st['context'], C + 'target_link_uri': st['tool'] + '/lti/launch',
                  C + 'tool_platform': {'guid': 'mock-lms', 'name': 'Mock LMS', 'product_family_code': 'mock'},
                  NRPS: {'context_memberships_url': b('/api/memberships'), 'service_versions': ['2.0']},
                  AGS: {'scope': [SC + 'lineitem', SC + 'result.readonly', SC + 'score'], 'lineitems': b('/api/lineitems')}}
        if kind == 'deeplink':
            claims[C + 'message_type'] = 'LtiDeepLinkingRequest'
            claims[DLS] = {'deep_link_return_url': b('/deep_link_return'), 'accept_types': ['ltiResourceLink'],
                           'accept_presentation_document_targets': ['iframe', 'window'], 'accept_multiple': True,
                           'auto_create': True, 'data': 'mock-dl-' + uuid.uuid4().hex[:6]}
        else:
            claims[C + 'message_type'] = 'LtiResourceLinkRequest'
            claims[C + 'resource_link'] = {'id': rl_id, 'title': f'Mock link {rl_id}'}
            if target:
                claims[C + 'custom'] = {'ciwt_target': target}
            li = next((k for k, v in st['lineitems'].items() if v.get('resourceLinkId') == rl_id), None)
            if li:
                claims[AGS]['lineitem'] = b(f'/api/lineitems/{li}')
        claims.update(extra or {})
        return claims

    def sign(claims, key=None, kid_=None, alg='RS256'):
        return jwt.encode(claims, key or st['priv'], algorithm=alg, headers={'kid': kid_ or st['kid']})

    st['id_token'], st['sign'] = id_token, sign

    def tool_key(kid_):
        ks = st['fetch_json'](st['tool'] + '/lti/jwks')
        k = next((x for x in ks.get('keys', []) if x.get('kid') == kid_), None)
        if not k:
            raise ValueError('tool kid not in tool JWKS')
        return RSAAlgorithm.from_jwk(json.dumps(k))

    def bearer(scope):
        tok = (request.headers.get('Authorization') or '').removeprefix('Bearer ').strip()
        t = st['tokens'].get(tok)
        return bool(t and t['exp'] > time.time() and scope in t['scopes'])

    @app.get('/')
    def home():
        links = ''.join(f'<li>{html.escape(u)}: <a href="/start?user={u}&kind=launch&target=course">Open the class</a> · '
                        f'<a href="/start?user={u}&kind=launch&target=quiz:1&rl=rl-quiz-1">Chapter 1 check</a>'
                        + (f' · <a href="/start?user={u}&kind=deeplink">Add content (deep linking)</a>' if 'Instructor' in v['roles'][0] else '')
                        + '</li>' for u, v in st['people'].items() if v.get('status', 'Active') == 'Active')
        return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Mock LMS</title></head><body>'
                f'<main><h1>Mock LMS (demo, not a real LMS)</h1><p>Issuer <code>{html.escape(st["issuer"])}</code>, client ID '
                f'<code>{html.escape(st["client_id"])}</code>, deployment <code>{html.escape(st["deployment_id"])}</code>.</p>'
                f'<ul>{links}</ul><h2>Scores received</h2><pre id="scores">{html.escape(json.dumps(st["scores"], indent=1))}</pre>'
                f'</main></body></html>')

    @app.get('/start')
    def start():
        """Platform-initiated OIDC login: send the browser to the tool's login URL."""
        hint = uuid.uuid4().hex
        st['pending'][hint] = {'user': request.args.get('user', 'mock-student-1'), 'kind': request.args.get('kind', 'launch'),
                               'target': request.args.get('target'), 'rl': request.args.get('rl', 'rl-1')}
        q = {'iss': st['issuer'], 'login_hint': request.args.get('user', 'mock-student-1'), 'lti_message_hint': hint,
             'target_link_uri': st['tool'] + '/lti/launch', 'client_id': st['client_id'], 'lti_deployment_id': st['deployment_id']}
        return Response(status=302, headers={'Location': st['tool'] + '/lti/login?' + urllib.parse.urlencode(q)})

    @app.get('/auth')
    def auth():
        a = request.args
        if a.get('client_id') != st['client_id'] or a.get('redirect_uri') != st['tool'] + '/lti/launch':
            return 'bad client_id or redirect_uri', 400
        if a.get('response_type') != 'id_token' or a.get('scope') != 'openid' or a.get('response_mode') != 'form_post':
            return 'bad OIDC parameters', 400
        pend = st['pending'].pop(a.get('lti_message_hint', ''), None)
        if not pend or pend['user'] != a.get('login_hint'):
            return 'unknown login', 400
        tok = sign(id_token(pend['user'], pend['kind'], pend['target'], pend['rl'], nonce=a.get('nonce')))
        return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Mock LMS launch</title></head><body>'
                f'<form id="f" method="post" action="{html.escape(a["redirect_uri"])}">'
                f'<input type="hidden" name="id_token" value="{tok}"><input type="hidden" name="state" value="{html.escape(a.get("state", ""))}">'
                f'<button>Continue</button></form><script>document.getElementById("f").submit()</script></body></html>')

    @app.get('/jwks')
    def jwks():
        return jsonify({'keys': [jwk()]})

    @app.post('/token')
    def token():
        f = request.form
        if f.get('grant_type') != 'client_credentials' or f.get('client_assertion_type') != 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer':
            return jsonify({'error': 'unsupported_grant_type'}), 400
        try:
            h = jwt.get_unverified_header(f.get('client_assertion', ''))
            c = jwt.decode(f['client_assertion'], tool_key(h.get('kid')), algorithms=['RS256'], audience=b('/token'))
        except Exception as e:  # noqa: BLE001
            return jsonify({'error': 'invalid_client', 'error_description': str(e)}), 401
        if c.get('iss') != st['client_id'] or c.get('sub') != st['client_id'] or c.get('jti') in st['used_jti']:
            return jsonify({'error': 'invalid_client'}), 401
        st['used_jti'].add(c['jti'])
        tok = secrets.token_urlsafe(16)
        st['tokens'][tok] = {'scopes': set((f.get('scope') or '').split()), 'exp': time.time() + 3600}
        return jsonify({'access_token': tok, 'token_type': 'Bearer', 'expires_in': 3600, 'scope': f.get('scope')})

    @app.route('/api/lineitems', methods=['GET', 'POST'])
    def lineitems():
        if request.method == 'GET':
            if not (bearer(SC + 'lineitem') or bearer(SC + 'lineitem.readonly')):
                return '', 401
            rl = request.args.get('resource_link_id')
            out = [dict(v, id=b(f'/api/lineitems/{k}')) for k, v in st['lineitems'].items() if not rl or v.get('resourceLinkId') == rl]
            return Response(json.dumps(out), mimetype='application/vnd.ims.lis.v2.lineitemcontainer+json')
        if not bearer(SC + 'lineitem'):
            return '', 401
        body = json.loads(request.data or b'{}')
        if 'scoreMaximum' not in body or 'label' not in body:
            return 'scoreMaximum and label required', 400
        k = str(len(st['lineitems']) + 1)
        st['lineitems'][k] = body
        return Response(json.dumps(dict(body, id=b(f'/api/lineitems/{k}'))), status=201, mimetype='application/vnd.ims.lis.v2.lineitem+json')

    @app.post('/api/lineitems/<k>/scores')
    def scores(k):
        if not bearer(SC + 'score'):
            return '', 401
        if k not in st['lineitems']:
            return '', 404
        if request.mimetype != 'application/vnd.ims.lis.v1.score+json':
            return 'wrong content type', 415
        s = json.loads(request.data or b'{}')
        for need in ('userId', 'activityProgress', 'gradingProgress', 'timestamp'):
            if need not in s:
                return f'{need} required', 400
        if s['userId'] not in st['people']:
            return 'unknown user', 422
        st['scores'].append(dict(s, lineitem=k))
        return '', 204

    @app.get('/api/memberships')
    def memberships():
        if not bearer(NRPS_SCOPE):
            return '', 401
        people = list(st['people'].items())
        page = int(request.args.get('page', '1'))
        n = st['page_size']
        chunk = people[(page - 1) * n: page * n]
        members = [{'user_id': u, 'name': p['name'], 'given_name': p['given_name'], 'family_name': p['family_name'],
                    'email': p['email'], 'roles': p['roles'], 'status': p.get('status', 'Active')} for u, p in chunk]
        r = Response(json.dumps({'id': b('/api/memberships'), 'context': st['context'], 'members': members}),
                     mimetype='application/vnd.ims.lti-nrps.v2.membershipcontainer+json')
        if page * n < len(people):
            r.headers['Link'] = f'<{b("/api/memberships")}?page={page + 1}>; rel="next"'
        return r

    @app.post('/deep_link_return')
    def deep_link_return():
        tok = request.form.get('JWT', '')
        try:
            h = jwt.get_unverified_header(tok)
            c = jwt.decode(tok, tool_key(h.get('kid')), algorithms=['RS256'], audience=st['issuer'])
        except Exception as e:  # noqa: BLE001
            return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Rejected</title></head><body><main><h1>Rejected</h1><p>{html.escape(str(e))}</p></main></body></html>', 400
        ok = (c.get('iss') == st['client_id'] and c.get(C + 'message_type') == 'LtiDeepLinkingResponse'
              and c.get(C + 'deployment_id') == st['deployment_id'])
        items = c.get('https://purl.imsglobal.org/spec/lti-dl/claim/content_items') or []
        if ok:
            st['deep_links'].append(c)
            for i, it in enumerate(items):        # auto_create: placed links get resource link ids (+ line items)
                rl = f'rl-dl-{len(st["deep_links"])}-{i}'
                it['_rl'] = rl
                if it.get('lineItem'):
                    k = str(len(st['lineitems']) + 1)
                    st['lineitems'][k] = dict(it['lineItem'], resourceLinkId=rl)
        lis = ''.join(f'<li>{html.escape(it.get("title", ""))} → <code>{html.escape(json.dumps(it.get("custom", {})))}</code>'
                      f'{" (gradebook column)" if it.get("lineItem") else ""}</li>' for it in items)
        return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Mock LMS: content added</title></head><body><main>'
                f'<h1>{"Content added" if ok else "Rejected"}</h1><p id="dlmsg">{html.escape(str(c.get("https://purl.imsglobal.org/spec/lti-dl/claim/msg", "")))}</p>'
                f'<ul id="dlitems">{lis}</ul><p><a href="/">Back to the mock LMS</a></p></main></body></html>'), (200 if ok else 400)

    return app


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tool', default='http://127.0.0.1:5078')
    ap.add_argument('--port', type=int, default=5088)
    ap.add_argument('--teacher-email', help='email the mock teacher launches with (to try link-by-email)')
    a = ap.parse_args()
    base = f'http://127.0.0.1:{a.port}'
    app = create_mock(base=base, tool_base=a.tool)
    st = app.config['MOCK']
    if a.teacher_email:
        st['people']['mock-teacher-1'] = dict(st['people']['mock-teacher-1'], email=a.teacher_email)
    print(json.dumps({'issuer': st['issuer'], 'client_id': st['client_id'], 'deployment_id': st['deployment_id'],
                      'auth_login_url': base + '/auth', 'auth_token_url': base + '/token', 'jwks_url': base + '/jwks'}, indent=1), flush=True)
    app.run(host='127.0.0.1', port=a.port, debug=False)


if __name__ == '__main__':
    main()
