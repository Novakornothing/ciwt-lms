"""Outbound HTTP for LTI services (JWKS, OAuth2 token, AGS, NRPS). One function so tests can swap in
the mock platform. HTTPS only, except loopback hosts when LTI_ALLOW_LOOPBACK_HTTP is on (dev/tests)."""
import json
import urllib.error
import urllib.parse
import urllib.request

LOOPBACK = {'127.0.0.1', 'localhost', '::1'}
MAX_BYTES = 2 * 1024 * 1024


class Response:
    def __init__(self, status, headers, body):
        self.status, self.headers, self.body = status, {k.lower(): v for k, v in (headers or {}).items()}, body

    def json(self):
        return json.loads(self.body.decode('utf-8') or 'null')

    @property
    def ok(self):
        return 200 <= self.status < 300


def url_allowed(url, allow_loopback_http=False):
    u = urllib.parse.urlparse(url or '')
    if u.scheme == 'https' and u.hostname:
        return True
    return bool(allow_loopback_http and u.scheme == 'http' and u.hostname in LOOPBACK)


class Transport:
    def __init__(self, allow_loopback_http=False, timeout=10):
        self.allow_loopback_http, self.timeout = allow_loopback_http, timeout

    def __call__(self, method, url, headers=None, data=None):
        if not url_allowed(url, self.allow_loopback_http):
            raise ValueError(f'Refusing non-HTTPS service URL: {url}')
        body = data
        if isinstance(data, dict):
            body = urllib.parse.urlencode(data).encode()
            headers = dict(headers or {}, **{'Content-Type': 'application/x-www-form-urlencoded'})
        elif isinstance(data, str):
            body = data.encode()
        req = urllib.request.Request(url, data=body, method=method, headers=dict(headers or {}))
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:  # noqa: S310 (scheme checked above)
                return Response(r.status, dict(r.headers), r.read(MAX_BYTES))
        except urllib.error.HTTPError as e:
            return Response(e.code, dict(e.headers or {}), e.read(MAX_BYTES) if e.fp else b'')
