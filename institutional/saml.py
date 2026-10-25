"""SAML 2.0 Service Provider helpers (no xmlsec dependency).

Supports HTTP-Redirect AuthnRequest and HTTP-POST Response with an enveloped XML-DSig signature using
exclusive c14n, SHA-256 digest and RSA-SHA256, verified against the IdP certificate pinned in the tenant config
(KeyInfo in the message is ignored). Defends against signature wrapping by only trusting the element the verified
Reference points at, and against XXE by parsing with entity resolution and network access off.
"""
import base64
import hashlib
import uuid
import zlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from lxml import etree

NS = {'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol', 'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
      'ds': 'http://www.w3.org/2000/09/xmldsig#', 'md': 'urn:oasis:names:tc:SAML:2.0:metadata'}
C14N = 'http://www.w3.org/2001/10/xml-exc-c14n#'
ENV = 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'
RSA256 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
SHA256 = 'http://www.w3.org/2001/04/xmlenc#sha256'
SKEW = timedelta(minutes=3)


class SamlError(Exception):
    pass


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _ts(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def _parse_ts(s):
    s = (s or '').strip().replace('Z', '')
    return datetime.fromisoformat(s.split('.')[0]) if s else None


def parse(xml_bytes):
    if b'<!DOCTYPE' in xml_bytes or b'<!ENTITY' in xml_bytes:
        raise SamlError('DTDs are not allowed')
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_comments=True, huge_tree=False, load_dtd=False)
    return etree.fromstring(xml_bytes, parser)


def _c14n(el):
    return etree.tostring(el, method='c14n', exclusive=True, with_comments=False)


def _load_cert(pem):
    pem = (pem or '').strip()
    if pem and 'BEGIN CERTIFICATE' not in pem:
        pem = '-----BEGIN CERTIFICATE-----\n' + pem + '\n-----END CERTIFICATE-----'
    try:
        return x509.load_pem_x509_certificate(pem.encode())
    except Exception as e:
        raise SamlError('IdP certificate is not valid PEM') from e


def cert_body(pem):
    return ''.join(l for l in (pem or '').splitlines() if l and 'CERTIFICATE' not in l)


# ------------------------------------------------------------------ SP side
def sp_metadata(entity_id, acs_url, cert_pem=None, org='Novak LMS'):
    md = NS['md']
    xl = '{http://www.w3.org/XML/1998/namespace}lang'
    root = etree.Element(f'{{{md}}}EntityDescriptor', nsmap={'md': md, 'ds': NS['ds']}, entityID=entity_id)
    sp = etree.SubElement(root, f'{{{md}}}SPSSODescriptor', AuthnRequestsSigned='false', WantAssertionsSigned='true',
                          protocolSupportEnumeration='urn:oasis:names:tc:SAML:2.0:protocol')
    if cert_pem:
        kd = etree.SubElement(sp, f'{{{md}}}KeyDescriptor', use='signing')
        ki = etree.SubElement(kd, f'{{{NS["ds"]}}}KeyInfo')
        etree.SubElement(etree.SubElement(ki, f'{{{NS["ds"]}}}X509Data'), f'{{{NS["ds"]}}}X509Certificate').text = cert_body(cert_pem)
    etree.SubElement(sp, f'{{{md}}}NameIDFormat').text = 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress'
    etree.SubElement(sp, f'{{{md}}}AssertionConsumerService', Binding='urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                     Location=acs_url, index='0', isDefault='true')
    o = etree.SubElement(root, f'{{{md}}}Organization')
    for tag in ('OrganizationName', 'OrganizationDisplayName'):
        etree.SubElement(o, f'{{{md}}}{tag}', {xl: 'en'}).text = org
    etree.SubElement(o, f'{{{md}}}OrganizationURL', {xl: 'en'}).text = entity_id
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8')


def authn_request(sp_entity_id, acs_url, idp_sso_url, relay_state=''):
    """Returns (request_id, redirect_url) for the HTTP-Redirect binding."""
    from xml.sax.saxutils import quoteattr, escape
    rid = '_' + uuid.uuid4().hex
    xml = (f'<samlp:AuthnRequest xmlns:samlp="{NS["samlp"]}" xmlns:saml="{NS["saml"]}" ID="{rid}" Version="2.0" '
           f'IssueInstant="{_ts(_now())}" Destination={quoteattr(idp_sso_url)} AssertionConsumerServiceURL={quoteattr(acs_url)} '
           f'ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"><saml:Issuer>{escape(sp_entity_id)}</saml:Issuer>'
           f'<samlp:NameIDPolicy AllowCreate="true" Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"/>'
           f'</samlp:AuthnRequest>')
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    payload = base64.b64encode(co.compress(xml.encode()) + co.flush()).decode()
    q = {'SAMLRequest': payload}
    if relay_state:
        q['RelayState'] = relay_state
    return rid, idp_sso_url + ('&' if '?' in idp_sso_url else '?') + urlencode(q)


# ------------------------------------------------------------------ signatures
def sign(el, key_pem, cert_pem):
    """Enveloped-sign element `el` in place (used by tests and the mock IdP). The element must carry an ID."""
    key = serialization.load_pem_private_key(key_pem.encode() if isinstance(key_pem, str) else key_pem, None)
    ds = NS['ds']
    for old in el.findall('ds:Signature', NS):
        el.remove(old)
    digest = base64.b64encode(hashlib.sha256(_c14n(el)).digest()).decode()
    sig = etree.Element(f'{{{ds}}}Signature', nsmap={'ds': ds})
    si = etree.SubElement(sig, f'{{{ds}}}SignedInfo')
    etree.SubElement(si, f'{{{ds}}}CanonicalizationMethod', Algorithm=C14N)
    etree.SubElement(si, f'{{{ds}}}SignatureMethod', Algorithm=RSA256)
    ref = etree.SubElement(si, f'{{{ds}}}Reference', URI='#' + el.get('ID'))
    tr = etree.SubElement(ref, f'{{{ds}}}Transforms')
    etree.SubElement(tr, f'{{{ds}}}Transform', Algorithm=ENV)
    etree.SubElement(tr, f'{{{ds}}}Transform', Algorithm=C14N)
    etree.SubElement(ref, f'{{{ds}}}DigestMethod', Algorithm=SHA256)
    etree.SubElement(ref, f'{{{ds}}}DigestValue').text = digest
    sv = etree.SubElement(sig, f'{{{ds}}}SignatureValue')
    ki = etree.SubElement(sig, f'{{{ds}}}KeyInfo')
    etree.SubElement(etree.SubElement(ki, f'{{{ds}}}X509Data'), f'{{{ds}}}X509Certificate').text = cert_body(cert_pem)
    issuer = el.find('saml:Issuer', NS)
    (issuer.addnext(sig) if issuer is not None else el.insert(0, sig))
    sv.text = base64.b64encode(key.sign(_c14n(si), padding.PKCS1v15(), hashes.SHA256())).decode()
    return el


def _verify_signed(el, cert):
    """True when `el` carries a valid enveloped signature over itself made by `cert`; raises on a bad one."""
    sig = el.find('ds:Signature', NS)
    if sig is None:
        return False
    si = sig.find('ds:SignedInfo', NS)
    refs = si.findall('ds:Reference', NS) if si is not None else []
    if len(refs) != 1 or refs[0].get('URI') != '#' + (el.get('ID') or '\0'):
        raise SamlError('signature does not reference the signed element')
    cm, sm = si.find('ds:CanonicalizationMethod', NS), si.find('ds:SignatureMethod', NS)
    if cm is None or sm is None or cm.get('Algorithm') != C14N or sm.get('Algorithm') != RSA256:
        raise SamlError('unsupported signature algorithm (need exc-c14n + rsa-sha256)')
    algs = [t.get('Algorithm') for t in refs[0].findall('ds:Transforms/ds:Transform', NS)]
    dm = refs[0].find('ds:DigestMethod', NS)
    if any(a not in (ENV, C14N) for a in algs) or dm is None or dm.get('Algorithm') != SHA256:
        raise SamlError('unsupported transform or digest')
    clone = etree.fromstring(etree.tostring(el))
    for s in clone.findall('ds:Signature', NS):
        clone.remove(s)
    digest = base64.b64encode(hashlib.sha256(_c14n(clone)).digest()).decode()
    if digest != (refs[0].findtext('ds:DigestValue', namespaces=NS) or '').strip():
        raise SamlError('digest mismatch: the signed content was altered')
    try:
        cert.public_key().verify(base64.b64decode(sig.findtext('ds:SignatureValue', namespaces=NS) or ''), _c14n(si),
                                 padding.PKCS1v15(), hashes.SHA256())
    except Exception as e:
        raise SamlError('signature value does not verify against the IdP certificate') from e
    return True


# ------------------------------------------------------------------ ACS
def _first(attrs, keys):
    return next((attrs[k][0] for k in keys if attrs.get(k)), '')


def validate_response(b64, cfg, sp_entity_id, acs_url, request_id=None, now=None):
    """Validate a base64 SAMLResponse. Returns name_id, email, names, attributes and assertion_id.

    cfg: idp_entity_id, idp_cert (PEM), allow_idp_initiated. The Response or the Assertion must be signed by the IdP.
    """
    now = now or _now()
    try:
        root = parse(base64.b64decode(b64 or '', validate=False))
    except SamlError:
        raise
    except Exception as e:
        raise SamlError('SAMLResponse is not valid base64 XML') from e
    if root.tag != f'{{{NS["samlp"]}}}Response':
        raise SamlError('not a SAML Response')
    sc_el = root.find('samlp:Status/samlp:StatusCode', NS)
    if sc_el is None or sc_el.get('Value') != 'urn:oasis:names:tc:SAML:2.0:status:Success':
        raise SamlError('IdP reported a failed login')
    if root.get('Destination') and root.get('Destination') != acs_url:
        raise SamlError('Destination does not match this ACS URL')
    cert = _load_cert(cfg.get('idp_cert'))
    assertions = root.findall('saml:Assertion', NS)
    if len(assertions) != 1 or root.findall('.//saml:EncryptedAssertion', NS) or len(root.findall('.//saml:Assertion', NS)) != 1:
        raise SamlError('expected exactly one unencrypted Assertion')
    a = assertions[0]
    signed = _verify_signed(root, cert)
    signed = _verify_signed(a, cert) or signed
    if not signed:
        raise SamlError('neither the Response nor the Assertion is signed')
    want_issuer = cfg.get('idp_entity_id')
    if want_issuer and (a.findtext('saml:Issuer', namespaces=NS) or '').strip() != want_issuer:
        raise SamlError('Assertion Issuer is not the configured IdP')
    irt = root.get('InResponseTo')
    if request_id and irt and irt != request_id:
        raise SamlError('InResponseTo does not match the login request')
    if not request_id:
        if irt:
            raise SamlError('response answers a request this server has no record of (expired or replayed)')
        if not cfg.get('allow_idp_initiated'):
            raise SamlError('IdP-initiated login is disabled for this institution')
    cond = a.find('saml:Conditions', NS)
    if cond is not None:
        nb, na = _parse_ts(cond.get('NotBefore')), _parse_ts(cond.get('NotOnOrAfter'))
        if nb and now + SKEW < nb:
            raise SamlError('assertion is not valid yet')
        if na and now - SKEW >= na:
            raise SamlError('assertion has expired')
        auds = [x.text for x in cond.findall('saml:AudienceRestriction/saml:Audience', NS)]
        if auds and sp_entity_id not in auds:
            raise SamlError('assertion is for a different service provider (Audience)')
    sc_ok = False
    for sc in a.findall('saml:Subject/saml:SubjectConfirmation', NS):
        scd = sc.find('saml:SubjectConfirmationData', NS)
        if sc.get('Method') != 'urn:oasis:names:tc:SAML:2.0:cm:bearer' or scd is None:
            continue
        na = _parse_ts(scd.get('NotOnOrAfter'))
        if scd.get('Recipient') in (None, acs_url) and (not na or now - SKEW < na) and \
                (not request_id or scd.get('InResponseTo') in (None, request_id)):
            sc_ok = True
    if not sc_ok:
        raise SamlError('no valid bearer SubjectConfirmation for this ACS')
    attrs = {}
    for at in a.findall('saml:AttributeStatement/saml:Attribute', NS):
        vals = [(v.text or '').strip() for v in at.findall('saml:AttributeValue', NS)]
        attrs.setdefault(at.get('Name'), []).extend(vals)
        if at.get('FriendlyName'):
            attrs.setdefault(at.get('FriendlyName'), []).extend(vals)
    name_id = (a.findtext('saml:Subject/saml:NameID', namespaces=NS) or '').strip()
    email = _first(attrs, ('email', 'mail', 'urn:oid:0.9.2342.19200300.100.1.3',
                           'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'))
    if not email and '@' in name_id:
        email = name_id
    return {'name_id': name_id, 'email': (email or '').lower(), 'attributes': attrs, 'assertion_id': a.get('ID'),
            'first_name': _first(attrs, ('givenName', 'given_name', 'urn:oid:2.5.4.42',
                                         'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname')),
            'last_name': _first(attrs, ('sn', 'surname', 'family_name', 'urn:oid:2.5.4.4',
                                        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'))}


def build_response(*, idp_entity_id, sp_entity_id, acs_url, email, attrs=None, in_response_to=None, key_pem, cert_pem,
                   sign_what='assertion', now=None, lifetime=300):
    """Mock-IdP helper (tests, local demo): a signed SAMLResponse, base64-encoded."""
    now = now or _now()
    p, s = NS['samlp'], NS['saml']
    r = etree.Element(f'{{{p}}}Response', nsmap={'samlp': p, 'saml': s}, ID='_' + uuid.uuid4().hex, Version='2.0',
                      IssueInstant=_ts(now), Destination=acs_url)
    if in_response_to:
        r.set('InResponseTo', in_response_to)
    etree.SubElement(r, f'{{{s}}}Issuer').text = idp_entity_id
    etree.SubElement(etree.SubElement(r, f'{{{p}}}Status'), f'{{{p}}}StatusCode', Value='urn:oasis:names:tc:SAML:2.0:status:Success')
    a = etree.SubElement(r, f'{{{s}}}Assertion', ID='_' + uuid.uuid4().hex, Version='2.0', IssueInstant=_ts(now))
    etree.SubElement(a, f'{{{s}}}Issuer').text = idp_entity_id
    sub = etree.SubElement(a, f'{{{s}}}Subject')
    etree.SubElement(sub, f'{{{s}}}NameID', Format='urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress').text = email
    sc = etree.SubElement(sub, f'{{{s}}}SubjectConfirmation', Method='urn:oasis:names:tc:SAML:2.0:cm:bearer')
    scd = etree.SubElement(sc, f'{{{s}}}SubjectConfirmationData', Recipient=acs_url, NotOnOrAfter=_ts(now + timedelta(seconds=lifetime)))
    if in_response_to:
        scd.set('InResponseTo', in_response_to)
    c = etree.SubElement(a, f'{{{s}}}Conditions', NotBefore=_ts(now - timedelta(seconds=30)), NotOnOrAfter=_ts(now + timedelta(seconds=lifetime)))
    etree.SubElement(etree.SubElement(c, f'{{{s}}}AudienceRestriction'), f'{{{s}}}Audience').text = sp_entity_id
    st = etree.SubElement(a, f'{{{s}}}AttributeStatement')
    for k, vals in (attrs or {}).items():
        at = etree.SubElement(st, f'{{{s}}}Attribute', Name=k)
        for v in (vals if isinstance(vals, (list, tuple)) else [vals]):
            etree.SubElement(at, f'{{{s}}}AttributeValue').text = v
    if sign_what in ('assertion', 'both'):
        sign(a, key_pem, cert_pem)
    if sign_what in ('response', 'both'):
        sign(r, key_pem, cert_pem)
    return base64.b64encode(etree.tostring(r)).decode()


def self_signed(cn='ciwt-test-idp'):
    """(key_pem, cert_pem) for tests, the mock IdP and SP metadata."""
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(_now() - timedelta(days=1))
            .not_valid_after(_now() + timedelta(days=3650)).sign(key, hashes.SHA256()))
    return (key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode(),
            cert.public_bytes(serialization.Encoding.PEM).decode())
