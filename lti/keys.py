"""Tool signing keys. Never stored in git:
  1. LTI_PRIVATE_KEY      env var holding the PEM text, or
  2. LTI_PRIVATE_KEY_FILE env var naming a PEM file, or
  3. <instance folder>/lti/tool_private.pem, generated (RSA 2048, mode 0600) on first use.
instance/ is in .gitignore. Rotation: put old public keys in <instance>/lti/previous/*.pem; they stay in
the JWKS so platforms can still verify messages signed before the switch."""
import base64
import glob
import hashlib
import json
import os
import threading

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .core import jwk_from_public_pem

_lock = threading.Lock()


def _b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


def thumbprint(jwk):
    """RFC 7638 JWK thumbprint, used as the kid."""
    canon = json.dumps({'e': jwk['e'], 'kty': 'RSA', 'n': jwk['n']}, separators=(',', ':'), sort_keys=True)
    return _b64(hashlib.sha256(canon.encode()).digest())


def public_pem(private_pem):
    k = serialization.load_pem_private_key(private_pem.encode() if isinstance(private_pem, str) else private_pem, None)
    return k.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()


def generate_private_pem():
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                           serialization.NoEncryption()).decode()


class ToolKeys:
    def __init__(self, instance_path, env=os.environ):
        self.dir = os.path.join(instance_path, 'lti')
        self.env = env
        self._cache = None

    def source(self):
        if self.env.get('LTI_PRIVATE_KEY'):
            return 'env LTI_PRIVATE_KEY'
        if self.env.get('LTI_PRIVATE_KEY_FILE'):
            return 'file ' + self.env['LTI_PRIVATE_KEY_FILE']
        return 'instance file ' + os.path.join(self.dir, 'tool_private.pem')

    def _load(self):
        if self._cache:
            return self._cache
        with _lock:
            if self.env.get('LTI_PRIVATE_KEY'):
                pem = self.env['LTI_PRIVATE_KEY'].replace('\\n', '\n')
            elif self.env.get('LTI_PRIVATE_KEY_FILE'):
                with open(self.env['LTI_PRIVATE_KEY_FILE']) as f:
                    pem = f.read()
            else:
                path = os.path.join(self.dir, 'tool_private.pem')
                if not os.path.exists(path):
                    os.makedirs(self.dir, exist_ok=True)
                    pem = generate_private_pem()
                    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, 'w') as f:
                        f.write(pem)
                with open(path) as f:
                    pem = f.read()
            pub = public_pem(pem)
            jwk = jwk_from_public_pem(pub, 'tmp')
            kid = thumbprint(jwk)
            jwk['kid'] = kid
            self._cache = (pem, kid, jwk)
            return self._cache

    @property
    def private_pem(self):
        return self._load()[0]

    @property
    def kid(self):
        return self._load()[1]

    def jwks(self):
        keys = [self._load()[2]]
        for p in sorted(glob.glob(os.path.join(self.dir, 'previous', '*.pem'))):
            try:
                with open(p) as f:
                    pem = f.read()
                if 'PRIVATE' in pem:
                    pem = public_pem(pem)
                j = jwk_from_public_pem(pem, 'tmp')
                j['kid'] = thumbprint(j)
                if j['kid'] != keys[0]['kid']:
                    keys.append(j)
            except (OSError, ValueError):
                continue
        return {'keys': keys}
