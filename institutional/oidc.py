"""OpenID Connect relying party: Authorization Code + PKCE (S256), ID token validated against the IdP JWKS
(signature, iss, aud, azp, exp/iat, nonce), optional UserInfo. Works with Okta, Entra ID, Google Workspace and
Shibboleth OIDC — each needs only issuer + client_id (+ client_secret for confidential clients).

All network calls go through `http(method, url, data=None, headers=None) -> dict` so tests inject a fake IdP.
"""
import base64
import hashlib
import json
import secrets
import urllib.parse
import urllib.request

import jwt

ALGS = ['RS256', 'RS384', 'RS512', 'PS256', 'ES256', 'ES384']


class OidcError(Exception):
    pass


def default_http(method, url, data=None, headers=None):
    if not (url.startswith('https://') or url.startswith('http://127.0.0.1') or url.startswith('http://localhost')):
        raise OidcError('IdP endpoints must use https')
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers=dict(headers or {}, Accept='application/json'))
    with urllib.request.urlopen(req, timeout=10) as r:   # noqa: S310 (scheme checked above)
        return json.loads(r.read().decode())


def pkce_pair():
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    return verifier, challenge


_disco = {}


def discover(cfg, http=default_http):
    """Merge /.well-known/openid-configuration into cfg (explicit endpoints in cfg win)."""
    if all(cfg.get(k) for k in ('authorization_endpoint', 'token_endpoint', 'jwks_uri')):
        return cfg
    iss = (cfg.get('issuer') or '').rstrip('/')
    if not iss:
        raise OidcError('OIDC issuer is not configured')
    if iss not in _disco:
        _disco[iss] = http('GET', iss + '/.well-known/openid-configuration')
    return dict(_disco[iss], **{k: v for k, v in cfg.items() if v})


def auth_url(cfg, redirect_uri, http=default_http):
    """Returns (url, state, nonce, verifier)."""
    cfg = discover(cfg, http)
    state, nonce = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    verifier, challenge = pkce_pair()
    q = {'response_type': 'code', 'client_id': cfg['client_id'], 'redirect_uri': redirect_uri,
         'scope': cfg.get('scopes') or 'openid email profile', 'state': state, 'nonce': nonce,
         'code_challenge': challenge, 'code_challenge_method': 'S256'}
    if cfg.get('domain_hint'):
        q['hd' if 'google' in cfg.get('issuer', '') else 'domain_hint'] = cfg['domain_hint']
    ep = cfg['authorization_endpoint']
    return ep + ('&' if '?' in ep else '?') + urllib.parse.urlencode(q), state, nonce, verifier


def _key_for(token, jwks):
    kid = jwt.get_unverified_header(token).get('kid')
    keys = [k for k in jwks.get('keys', []) if k.get('use', 'sig') == 'sig' and (kid is None or k.get('kid') == kid)]
    if not keys:
        raise OidcError('no JWKS key matches the ID token kid')
    return jwt.PyJWK(keys[0]).key


def validate_id_token(token, cfg, nonce, jwks):
    try:
        if jwt.get_unverified_header(token).get('alg') not in ALGS:
            raise OidcError('ID token algorithm not allowed')
        claims = jwt.decode(token, _key_for(token, jwks), algorithms=ALGS, audience=cfg['client_id'],
                            issuer=cfg.get('issuer') or None, leeway=120,
                            options={'require': ['exp', 'iat', 'iss', 'aud', 'sub'], 'verify_iss': bool(cfg.get('issuer'))})
    except OidcError:
        raise
    except jwt.PyJWTError as e:
        raise OidcError('ID token rejected: %s' % e) from e
    aud = claims['aud'] if isinstance(claims['aud'], list) else [claims['aud']]
    if len(aud) > 1 and claims.get('azp') != cfg['client_id']:
        raise OidcError('ID token azp does not match this client')
    if not nonce or not secrets.compare_digest(str(claims.get('nonce', '')), nonce):
        raise OidcError('ID token nonce mismatch (possible replay)')
    return claims


def complete(cfg, code, verifier, nonce, redirect_uri, http=default_http):
    """Exchange the code, validate the ID token, merge UserInfo. Returns a normalised identity dict."""
    cfg = discover(cfg, http)
    data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': redirect_uri,
            'client_id': cfg['client_id'], 'code_verifier': verifier}
    if cfg.get('client_secret'):
        data['client_secret'] = cfg['client_secret']
    try:
        tok = http('POST', cfg['token_endpoint'], data=data)
    except Exception as e:
        raise OidcError('token exchange failed (%s)' % e.__class__.__name__) from e
    if not tok.get('id_token'):
        raise OidcError('token endpoint returned no id_token')
    claims = validate_id_token(tok['id_token'], cfg, nonce, http('GET', cfg['jwks_uri']))
    if cfg.get('userinfo_endpoint') and tok.get('access_token'):
        try:
            ui = http('GET', cfg['userinfo_endpoint'], headers={'Authorization': 'Bearer ' + tok['access_token']})
            if ui.get('sub') == claims['sub']:
                claims = dict(ui, **claims)
        except Exception:
            pass
    if claims.get('email_verified') is False:
        raise OidcError('the IdP says this email address is not verified')
    email = (claims.get('email') or claims.get('preferred_username') or claims.get('upn') or '').lower()
    groups = claims.get(cfg.get('role_claim') or 'groups') or claims.get('roles') or []
    return {'sub': claims['sub'], 'email': email, 'first_name': claims.get('given_name', ''),
            'last_name': claims.get('family_name', ''),
            'attributes': {'groups': groups if isinstance(groups, list) else [groups]}, 'claims': claims}
