"""LTI 1.3 / LTI Advantage message logic, tool side. Pure functions (no Flask, no DB) so the
security checks can be tested on their own. Built on PyJWT + cryptography.

Not 1EdTech-certified; tested against the in-repo mock platform (tools/lti_mock_platform.py) only.
"""
import json
import time
import uuid

import jwt
from jwt.algorithms import RSAAlgorithm

LTI_VERSION = '1.3.0'
C = 'https://purl.imsglobal.org/spec/lti/claim/'
CLAIM = {
    'message_type': C + 'message_type', 'version': C + 'version', 'deployment_id': C + 'deployment_id',
    'target_link_uri': C + 'target_link_uri', 'resource_link': C + 'resource_link', 'roles': C + 'roles',
    'context': C + 'context', 'custom': C + 'custom', 'launch_presentation': C + 'launch_presentation', 'tool_platform': C + 'tool_platform', 'lis': C + 'lis',
    'ags': 'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint',
    'nrps': 'https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice',
    'dl_settings': 'https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings',
    'dl_items': 'https://purl.imsglobal.org/spec/lti-dl/claim/content_items',
    'dl_data': 'https://purl.imsglobal.org/spec/lti-dl/claim/data',
    'dl_msg': 'https://purl.imsglobal.org/spec/lti-dl/claim/msg',
}
MSG_LAUNCH, MSG_DL, MSG_DL_RESP = 'LtiResourceLinkRequest', 'LtiDeepLinkingRequest', 'LtiDeepLinkingResponse'
SCOPE = {
    'lineitem': 'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
    'lineitem_ro': 'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly',
    'result_ro': 'https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly',
    'score': 'https://purl.imsglobal.org/spec/lti-ags/scope/score',
    'nrps': 'https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly',
}
MT_SCORE = 'application/vnd.ims.lis.v1.score+json'
MT_LINEITEM = 'application/vnd.ims.lis.v2.lineitem+json'
MT_LINEITEMS = 'application/vnd.ims.lis.v2.lineitemcontainer+json'
MT_NRPS = 'application/vnd.ims.lti-nrps.v2.membershipcontainer+json'
ALGS = ('RS256', 'RS384', 'RS512')
LEEWAY = 60            # seconds of clock skew allowed on exp / iat
MAX_AGE = 3600         # an id_token issued more than this long ago is refused even if exp says otherwise


class LtiError(Exception):
    """A launch or service call that must be refused. `code` is stable for tests and logs."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------- roles
R = 'http://purl.imsglobal.org/vocab/lis/v2/'
STAFF_ROLES = {R + 'membership#Instructor', R + 'membership#ContentDeveloper', R + 'membership#Administrator',
               R + 'membership/Instructor#TeachingAssistant', R + 'institution/person#Administrator',
               R + 'institution/person#Instructor', R + 'institution/person#Faculty', R + 'system/person#Administrator',
               R + 'membership#Mentor'}
LEARNER_ROLES = {R + 'membership#Learner', R + 'institution/person#Student', R + 'institution/person#Learner',
                 R + 'membership/Learner#Learner'}
SHORT = {'Instructor', 'Learner', 'ContentDeveloper', 'TeachingAssistant', 'Administrator', 'Student', 'Mentor'}


def norm_role(r):
    """Expand the LTI 1.1-style short names some platforms still send ('Instructor') to full URIs."""
    r = (r or '').strip()
    if r in SHORT:
        return R + ('membership/Instructor#TeachingAssistant' if r == 'TeachingAssistant' else
                    'membership#Learner' if r == 'Student' else 'membership#' + r)
    return r


def map_role(roles):
    """LTI roles → this LMS's role. Staff roles → 'instructor'; learner roles → 'student'.
    Never 'admin': LMS administrators get admin here only by a local admin's decision."""
    roles = {norm_role(r) for r in (roles or [])}
    if roles & STAFF_ROLES:
        return 'instructor'
    if roles & LEARNER_ROLES:
        return 'student'
    return 'student' if roles else None


def is_staff(roles):
    return map_role(roles) == 'instructor'


# ---------------------------------------------------------------- keys
def jwk_from_public_pem(pem, kid):
    k = json.loads(RSAAlgorithm.to_jwk(RSAAlgorithm(RSAAlgorithm.SHA256).prepare_key(pem)))
    k.update({'kid': kid, 'alg': 'RS256', 'use': 'sig'})
    return k


def key_from_jwks(jwks, kid, alg):
    keys = (jwks or {}).get('keys') or []
    cand = [k for k in keys if k.get('kid') == kid] if kid else (keys if len(keys) == 1 else [])
    if not cand:
        raise LtiError('jwks_kid', f'No platform key with kid {kid!r} in the platform key set.')
    k = cand[0]
    if k.get('kty') != 'RSA':
        raise LtiError('jwks_kty', 'Platform key is not an RSA key.')
    if k.get('use') not in (None, 'sig'):
        raise LtiError('jwks_use', 'Platform key is not a signing key.')
    return RSAAlgorithm.from_jwk(json.dumps(k))


# ---------------------------------------------------------------- id_token
def peek_header(token):
    try:
        h = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise LtiError('jwt_malformed', f'id_token is not a JWT: {exc}')
    if h.get('alg') not in ALGS:
        raise LtiError('jwt_alg', f'Signing algorithm {h.get("alg")!r} is not accepted (RS256/384/512 only).')
    return h


def peek_claims(token):
    """Unverified claims, only to find which registration to verify against."""
    try:
        return jwt.decode(token, options={'verify_signature': False})
    except jwt.PyJWTError as exc:
        raise LtiError('jwt_malformed', f'id_token is not a JWT: {exc}')


def validate_id_token(token, reg, jwks, expected_nonce, now=None):
    """Verify an id_token from the platform. `reg` needs issuer, client_id, deployment_ids.
    Returns the claims. Raises LtiError on any failure (signature, iss, aud, azp, exp, iat, nonce,
    version, message type, deployment)."""
    h = peek_header(token)
    key = key_from_jwks(jwks, h.get('kid'), h['alg'])
    now = int(now or time.time())
    try:
        claims = jwt.decode(token, key=key, algorithms=[h['alg']], audience=reg['client_id'], issuer=reg['issuer'],
                            leeway=LEEWAY, options={'require': ['exp', 'iat', 'iss', 'aud', 'sub', 'nonce'],
                                                    'verify_iat': True})
    except jwt.ExpiredSignatureError:
        raise LtiError('jwt_expired', 'id_token has expired.')
    except jwt.InvalidAudienceError:
        raise LtiError('jwt_aud', 'id_token is not addressed to this tool (aud).')
    except jwt.InvalidIssuerError:
        raise LtiError('jwt_iss', 'id_token issuer does not match the registration.')
    except jwt.MissingRequiredClaimError as exc:
        raise LtiError('jwt_claim', f'id_token is missing a required claim: {exc}')
    except jwt.InvalidSignatureError:
        raise LtiError('jwt_sig', 'id_token signature does not verify against the platform key set.')
    except jwt.PyJWTError as exc:
        raise LtiError('jwt_invalid', f'id_token rejected: {exc}')
    if claims['iat'] < now - MAX_AGE - LEEWAY:
        raise LtiError('jwt_old', 'id_token was issued too long ago.')
    aud = claims['aud'] if isinstance(claims['aud'], list) else [claims['aud']]
    if len(aud) > 1 and claims.get('azp') != reg['client_id']:
        raise LtiError('jwt_azp', 'id_token has several audiences and azp is not this tool.')
    if 'azp' in claims and claims['azp'] != reg['client_id']:
        raise LtiError('jwt_azp', 'id_token azp is not this tool.')
    if not expected_nonce or claims.get('nonce') != expected_nonce:
        raise LtiError('nonce', 'id_token nonce does not match the login request (replay or a different browser).')
    if claims.get(CLAIM['version']) != LTI_VERSION:
        raise LtiError('version', 'Only LTI 1.3.0 launches are accepted.')
    mt = claims.get(CLAIM['message_type'])
    if mt not in (MSG_LAUNCH, MSG_DL):
        raise LtiError('message_type', f'Unsupported LTI message type {mt!r}.')
    dep = claims.get(CLAIM['deployment_id'])
    if not dep or dep not in (reg.get('deployment_ids') or []):
        raise LtiError('deployment', f'Deployment {dep!r} is not registered for this platform.')
    if mt == MSG_LAUNCH and not (claims.get(CLAIM['resource_link']) or {}).get('id'):
        raise LtiError('resource_link', 'Resource link launch without a resource_link id.')
    if mt == MSG_DL and not (claims.get(CLAIM['dl_settings']) or {}).get('deep_link_return_url'):
        raise LtiError('dl_settings', 'Deep linking request without a deep_link_return_url.')
    if not claims.get('sub'):
        raise LtiError('sub', 'Anonymous launches (no sub) are not supported.')
    return claims


# ---------------------------------------------------------------- tool-signed messages
def sign(payload, private_pem, kid):
    return jwt.encode(payload, private_pem, algorithm='RS256', headers={'kid': kid, 'typ': 'JWT'})


def deep_link_response(reg, request_claims, items, private_pem, kid, msg=None, now=None):
    """JWT the tool posts back to deep_link_return_url (Deep Linking 2.0, section 4.2)."""
    now = int(now or time.time())
    settings = request_claims.get(CLAIM['dl_settings']) or {}
    p = {'iss': reg['client_id'], 'aud': [request_claims['iss']], 'iat': now, 'exp': now + 600,
         'nonce': uuid.uuid4().hex, 'azp': reg['client_id'],
         CLAIM['message_type']: MSG_DL_RESP, CLAIM['version']: LTI_VERSION,
         CLAIM['deployment_id']: request_claims[CLAIM['deployment_id']], CLAIM['dl_items']: items}
    if settings.get('data') is not None:
        p[CLAIM['dl_data']] = settings['data']
    if msg:
        p[CLAIM['dl_msg']] = msg
    return sign(p, private_pem, kid)


def resource_link_item(title, url, target, text=None, line_item=None):
    it = {'type': 'ltiResourceLink', 'title': title, 'url': url, 'custom': {'ciwt_target': target}}
    if text:
        it['text'] = text
    if line_item:
        it['lineItem'] = line_item
    return it


def client_assertion(reg, private_pem, kid, now=None):
    """JWT for the OAuth2 client-credentials grant (1EdTech Security Framework 4.1)."""
    now = int(now or time.time())
    return sign({'iss': reg['client_id'], 'sub': reg['client_id'], 'aud': reg.get('token_audience') or reg['auth_token_url'],
                 'iat': now, 'exp': now + 300, 'jti': uuid.uuid4().hex}, private_pem, kid)


def token_request_body(reg, scopes, private_pem, kid):
    return {'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': client_assertion(reg, private_pem, kid), 'scope': ' '.join(scopes)}


def score_payload(user_sub, score, maximum=100.0, comment=None, when=None):
    """AGS score. `score` None → no grade yet (still reports progress)."""
    p = {'userId': user_sub, 'activityProgress': 'Completed' if score is not None else 'Initialized',
         'gradingProgress': 'FullyGraded' if score is not None else 'NotReady',
         'timestamp': (when or time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime()))}
    if score is not None:
        p['scoreGiven'] = round(float(score), 2)
        p['scoreMaximum'] = float(maximum)
    if comment:
        p['comment'] = comment
    return p


def scores_url(lineitem_url):
    """Lineitem URL + '/scores', keeping any query string (Moodle uses ?type_id=…)."""
    base, sep, q = lineitem_url.partition('?')
    return base.rstrip('/') + '/scores' + (sep + q if sep else '')


def parse_link_next(header):
    for part in (header or '').split(','):
        seg = [s.strip() for s in part.split(';')]
        if len(seg) > 1 and any(s.replace(' ', '') in ('rel="next"', "rel=next") for s in seg[1:]):
            return seg[0].strip('<>')
    return None
