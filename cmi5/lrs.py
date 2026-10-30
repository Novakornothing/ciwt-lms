"""xAPI 1.0.3 Learning Record Store resources, served by the Novak LMS web process.

Resources: /xAPI/about, /xAPI/statements, /xAPI/activities/state,
/xAPI/activities/profile, /xAPI/agents/profile.

Authentication is HTTP Basic: an organization client credential, or a one-time
cmi5 fetch token limited to that assignable-unit session.
"""
import base64
import hashlib
import json
import re
from types import SimpleNamespace
from urllib.parse import urlencode

from flask import Response, g, request
from werkzeug.security import check_password_hash

from .rules import check_au_statement
from .util import (
    SUPPORTED_VERSIONS, VOIDED, XAPI_VERSION, ApiError, agent_key, agents_match,
    canonical_statement, category_ids, grouping_ids, is_iri, is_uuid, iso,
    new_uuid, parse_iso, session_id_of, sha1_etag, utcnow,
)
from .xapi_schema import SIGNATURE_USAGE, statement_version_ok, validate_agent, validate_statement

_db = None
_m = None
_app = None
_after_store = None

LMS_AUTHORITY = {
    'objectType': 'Agent',
    'account': {'homePage': 'https://novakornothing.com', 'name': 'novak-lms'},
}


def init(app, db, models):
    global _db, _m, _app
    _db, _m, _app = db, models, app


def set_after_store(fn):
    global _after_store
    _after_store = fn


def M(name):
    return _m[name]


def _statement_row(sid):
    if not sid:
        return None
    row = _db.session.get(M('XapiStatement'), sid)
    if row is not None:
        return row
    return M('XapiStatement').query.filter(M('XapiStatement').id.ilike(sid)).first()


# -------------------------------------------------------------------------------------------- HTTP
def _cors(resp):
    resp.headers['X-Experience-API-Version'] = XAPI_VERSION
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Expose-Headers'] = (
        'ETag, Last-Modified, Location, Content-Length, '
        'X-Experience-API-Version, X-Experience-API-Consistent-Through'
    )
    return resp


def xapi_response(body=None, status=200, content_type='application/json; charset=utf-8', etag=None, extra=None):
    head = bool(getattr(g, 'xapi_head', False))
    if body is None:
        resp = Response(status=status)
    elif isinstance(body, (dict, list)):
        raw = json.dumps(body, ensure_ascii=False).encode('utf-8')
        resp = Response(b'' if head else raw, status=status, mimetype='application/json')
    elif isinstance(body, bytes):
        resp = Response(b'' if head else body, status=status)
        resp.headers['Content-Type'] = content_type
    else:
        raw = str(body).encode('utf-8')
        resp = Response(b'' if head else raw, status=status)
        resp.headers['Content-Type'] = content_type
    if etag:
        resp.headers['ETag'] = etag if str(etag).startswith('"') else f'"{etag}"'
    if status == 204:
        resp.headers.pop('Content-Type', None)
    if extra:
        for key, value in extra.items():
            resp.headers[key] = value
    return _cors(resp)


def xapi_error(status, message, www=False):
    resp = xapi_response(message, status=status, content_type='text/plain; charset=utf-8')
    if www:
        resp.headers['WWW-Authenticate'] = 'Basic realm="xAPI"'
    return resp


def _args():
    if getattr(g, 'xapi_args', None) is not None:
        return g.xapi_args
    return request.args


def _body_bytes():
    if getattr(g, 'xapi_body', None) is not None:
        return g.xapi_body
    return request.get_data(cache=True) or b''


def _content_type():
    if getattr(g, 'xapi_content_type', None):
        return g.xapi_content_type
    return request.content_type or ''


def _method():
    if getattr(g, 'xapi_method', None):
        return g.xapi_method
    if request.method == 'HEAD':
        g.xapi_head = True
        return 'GET'
    return request.method


_FORM_HEADERS = (
    'Authorization', 'X-Experience-API-Version', 'Content-Type',
    'If-Match', 'If-None-Match',
)


def _form_values():
    """Read an alternate-request form even when the client omits the form content type."""
    if request.form:
        return request.form
    raw = request.get_data(cache=True) or b''
    if not raw or raw[:1] in (b'{', b'['):
        return {}
    from urllib.parse import parse_qs
    try:
        parsed = parse_qs(raw.decode('utf-8'), keep_blank_values=True)
    except Exception as exc:
        raise ApiError(400, 'alternate request must be form-urlencoded') from exc
    return {key: values[0] for key, values in parsed.items() if values}


def _apply_form_header(name, value):
    headers = getattr(g, 'xapi_form_headers', None)
    if headers is None:
        headers = {}
        g.xapi_form_headers = headers
    headers[name.lower()] = value


def _header(name):
    headers = getattr(g, 'xapi_form_headers', None) or {}
    if name.lower() in headers:
        return headers[name.lower()]
    return request.headers.get(name)


def _prepare_alternate():
    """xAPI alternate request syntax: a POST whose form carries the real method."""
    if request.method != 'POST':
        if 'method' in request.args:
            raise ApiError(400, 'The alternate request syntax is only accepted as POST')
        return
    form = _form_values()
    if 'method' not in request.args and 'method' not in form:
        return
    extra = [key for key in request.args.keys() if key != 'method']
    if extra:
        raise ApiError(400, 'An alternate request cannot repeat parameters in the query string')
    ctype = (request.content_type or '').split(';')[0].strip().lower()
    raw = request.get_data(cache=True) or b''
    if raw[:1] in (b'{', b'['):
        raise ApiError(400, 'alternate request must be form-urlencoded')
    if ctype and ctype not in ('application/x-www-form-urlencoded', 'text/plain', 'application/octet-stream'):
        raise ApiError(400, 'alternate request must be form-urlencoded')
    method = (form.get('method') or request.args.get('method') or '').upper()
    if method not in ('GET', 'PUT', 'POST', 'DELETE'):
        raise ApiError(400, 'alternate method is not supported')
    for name in _FORM_HEADERS:
        if form.get(name):
            _apply_form_header(name, form.get(name))
    if method in ('PUT', 'POST') and 'content' not in form:
        raise ApiError(400, 'content is required')
    skip = {'method', 'content', * _FORM_HEADERS, 'contentType', 'Content-Length'}
    g.xapi_method = method
    g.xapi_args = {key: value for key, value in form.items() if key not in skip}
    g.xapi_body = (form.get('content') or '').encode('utf-8')
    g.xapi_content_type = form.get('Content-Type') or form.get('contentType') or 'application/json'


def _check_version():
    version = (_header('X-Experience-API-Version') or '').strip()
    if version not in SUPPORTED_VERSIONS:
        raise ApiError(400, 'X-Experience-API-Version must be 1.0.0, 1.0.1, 1.0.2, or 1.0.3')


def _authenticate():
    header = _header('Authorization') or ''
    if not header.startswith('Basic '):
        raise ApiError(401, 'Basic authentication is required')
    try:
        decoded = base64.b64decode(header[6:].strip(), validate=False).decode('utf-8')
    except Exception as exc:
        raise ApiError(401, 'Basic authentication is required') from exc
    user, sep, password = decoded.partition(':')
    if not sep:
        raise ApiError(401, 'Basic authentication is required')
    client = M('LrsClient').query.filter_by(key=user, active=True).first()
    if client and check_password_hash(client.secret_hash, password):
        return SimpleNamespace(kind='client', client=client, session=None)
    row = M('Cmi5Session').query.filter_by(auth_username=user).first()
    if row and row.auth_secret_hash and check_password_hash(row.auth_secret_hash, password):
        if row.terminated_at or row.abandoned_at:
            raise ApiError(403, 'This session is closed. No further requests are accepted.')
        return SimpleNamespace(kind='session', client=None, session=row)
    raise ApiError(401, 'Basic authentication is required')


def _authority(auth):
    if auth is None:
        return dict(LMS_AUTHORITY)
    if auth.kind == 'client':
        return {'objectType': 'Agent', 'account': {'homePage': 'https://novakornothing.com', 'name': auth.client.key}}
    return {'objectType': 'Agent', 'account': {'homePage': 'https://novakornothing.com', 'name': 'cmi5-session-' + auth.session.uuid}}


def _guard(fn, about=False):
    def wrapped(*args, **kwargs):
        try:
            if request.method == 'OPTIONS':
                resp = Response(status=200)
                resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, HEAD, OPTIONS'
                resp.headers['Access-Control-Allow-Headers'] = (
                    'Authorization, X-Experience-API-Version, Content-Type, Content-Length, '
                    'If-Match, If-None-Match, If-Modified-Since, Accept, Accept-Language'
                )
                resp.headers['Access-Control-Max-Age'] = '600'
                return _cors(resp)
            if request.method == 'HEAD':
                g.xapi_head = True
            if not about:
                _check_version()
                g.xapi_auth = _authenticate()
            _prepare_alternate()
            return fn(*args, **kwargs)
        except ApiError as exc:
            www = exc.status == 401
            _db.session.rollback()
            return xapi_error(exc.status, exc.message, www=www)
    wrapped.__name__ = fn.__name__
    return wrapped


# -------------------------------------------------------------------------------------------- agents
def _validate_actor(actor, label):
    if not isinstance(actor, dict):
        raise ApiError(400, f'{label} is required')
    validate_agent(actor, label)


def _validate_object(obj, allow_sub=True):
    if not isinstance(obj, dict):
        raise ApiError(400, 'object is required')
    kind = obj.get('objectType') or 'Activity'
    if kind == 'Activity':
        if not is_iri(obj.get('id')):
            raise ApiError(400, 'Activity id must be an IRI')
    elif kind in ('Agent', 'Group'):
        obj = dict(obj)
        if 'objectType' not in obj:
            obj['objectType'] = kind
        _validate_actor(obj, 'object')
    elif kind == 'StatementRef':
        if not is_uuid(str(obj.get('id') or '')):
            raise ApiError(400, 'StatementRef id must be a UUID')
    elif kind == 'SubStatement':
        if not allow_sub:
            raise ApiError(400, 'A SubStatement cannot contain another SubStatement')
        for banned in ('id', 'stored', 'authority', 'version'):
            if banned in obj:
                raise ApiError(400, 'A SubStatement cannot include ' + banned)
        _validate_actor(obj.get('actor'), 'substatement actor')
        verb = obj.get('verb')
        if not isinstance(verb, dict) or not is_iri(verb.get('id')):
            raise ApiError(400, 'substatement verb.id must be an IRI')
        _validate_object(obj.get('object'), allow_sub=False)
    else:
        raise ApiError(400, 'objectType is not supported')


def _b64url(segment):
    pad = '=' * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + pad)


def _check_signatures(stmt):
    """A signature attachment must be an RS256/384/512 JWS of the unsigned statement."""
    for attachment in stmt.get('attachments') or []:
        if not isinstance(attachment, dict) or attachment.get('usageType') != SIGNATURE_USAGE:
            continue
        row = _db.session.get(M('XapiAttachment'), attachment.get('sha2'))
        if row is None:
            raise ApiError(400, 'A statement signature attachment is missing')
        try:
            header_b, payload_b, sig_b = bytes(row.content).decode('ascii').split('.')
            header = json.loads(_b64url(header_b))
            payload = json.loads(_b64url(payload_b))
        except Exception as exc:
            raise ApiError(400, 'A statement signature must be a JWS') from exc
        if not header_b or not payload_b or not sig_b:
            raise ApiError(400, 'A statement signature must be a JWS')
        if not isinstance(header, dict) or header.get('alg') not in ('RS256', 'RS384', 'RS512'):
            raise ApiError(400, 'A statement signature must use RS256, RS384, or RS512')
        unsigned = {key: value for key, value in stmt.items() if key != 'attachments'}
        if payload != unsigned:
            raise ApiError(400, 'A statement signature does not match the statement')


def normalize_statement(stmt):
    if not isinstance(stmt, dict):
        raise ApiError(400, 'A statement must be a JSON object.')
    stmt = json.loads(json.dumps(stmt))
    _check_signatures(stmt)
    validate_statement(stmt)
    if not stmt.get('id'):
        stmt['id'] = new_uuid()
    actor = stmt.get('actor')
    if isinstance(actor, dict) and 'objectType' not in actor:
        actor['objectType'] = 'Agent'
    obj = stmt.get('object')
    if isinstance(obj, dict) and obj.get('objectType') is None:
        obj['objectType'] = 'Activity'
    if not stmt.get('timestamp'):
        stmt['timestamp'] = iso(utcnow())
    version = stmt.get('version') or XAPI_VERSION
    if not statement_version_ok(version):
        raise ApiError(400, 'statement version is not supported')
    stmt['version'] = version
    stmt.pop('stored', None)
    stmt.pop('authority', None)
    return stmt


# -------------------------------------------------------------------------------------------- store
def _parse_statements(body, content_type, bind_attachments=True):
    ctype = (content_type or '').split(';')[0].strip().lower()
    if ctype == 'multipart/mixed':
        return _parse_multipart(body, content_type)
    if ctype and ctype != 'application/json':
        raise ApiError(400, 'Content-Type must be application/json')
    try:
        data = json.loads(body.decode('utf-8') if isinstance(body, bytes) else body)
    except Exception as exc:
        raise ApiError(400, 'Statement body must be JSON.') from exc
    if isinstance(data, dict):
        statements = [data]
    elif isinstance(data, list):
        statements = data
    else:
        raise ApiError(400, 'Statement body must be a statement or an array.')
    if bind_attachments and ctype == 'application/json':
        _bind_attachments(statements, [])
    return statements


def _bind_attachments(statements, hashes):
    """Every non-fileUrl attachment needs a part. A part must match some attachment."""
    needed = []
    declared = []
    for stmt in statements:
        if not isinstance(stmt, dict):
            continue
        for attachment in stmt.get('attachments') or []:
            if not isinstance(attachment, dict):
                continue
            declared.append(attachment.get('sha2'))
            if not attachment.get('fileUrl'):
                needed.append(attachment.get('sha2'))
    if any(sha not in hashes for sha in needed):
        raise ApiError(400, 'attachment content is missing')
    if any(sha not in declared for sha in hashes):
        raise ApiError(400, 'multipart section is not an attachment of the statement')


def _parse_multipart(body, content_type):
    match = re.search(r'boundary=("[^"]+"|[^;]+)', content_type, re.I)
    if not match:
        raise ApiError(400, 'multipart boundary is missing')
    boundary = match.group(1).strip().strip('"').encode('utf-8')
    raw = body.lstrip()
    if not raw.startswith(b'--' + boundary):
        raise ApiError(400, 'multipart body must start with the boundary')
    json_part = None
    hashes = []
    for part in body.split(b'--' + boundary):
        if not part or part.strip() in (b'', b'--'):
            continue
        if part.startswith(b'\r\n'):
            part = part[2:]
        head, sep, data = part.partition(b'\r\n\r\n')
        if not sep:
            continue
        if data.endswith(b'\r\n'):
            data = data[:-2]
        headers = {}
        for line in head.decode('utf-8', 'replace').split('\r\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        if json_part is None and 'json' in headers.get('content-type', ''):
            json_part = data
            continue
        if 'json' in headers.get('content-type', ''):
            raise ApiError(400, 'multipart request has more than one statement part')
        sha = headers.get('x-experience-api-hash')
        if not sha:
            raise ApiError(400, 'attachment part is missing X-Experience-API-Hash')
        if headers.get('content-transfer-encoding', '').lower() != 'binary':
            raise ApiError(400, 'attachment transfer encoding must be binary')
        digest = hashlib.sha256(data).hexdigest()
        if digest != sha:
            raise ApiError(400, 'Attachment hash does not match the content.')
        hashes.append(sha)
        if _db.session.get(M('XapiAttachment'), sha) is None:
            _db.session.add(M('XapiAttachment')(
                sha2=sha, content_type=headers.get('content-type') or 'application/octet-stream', content=data,
            ))
    if json_part is None:
        raise ApiError(400, 'multipart statement is missing the JSON part')
    statements = _parse_statements(json_part, 'application/json', bind_attachments=False)
    _bind_attachments(statements, hashes)
    return statements


def _template_grouping(au, actor, registration):
    doc = M('XapiDocument').query.filter_by(
        kind='state', activity_id=au.lms_activity_id, agent_key=agent_key(actor),
        registration=registration.uuid, doc_id='LMS.LaunchData',
    ).first()
    if doc:
        try:
            payload = json.loads(doc.content)
            ids = [item.get('id') for item in
                   (((payload.get('contextTemplate') or {}).get('contextActivities') or {}).get('grouping') or [])
                   if isinstance(item, dict) and item.get('id')]
            if ids:
                return ids
        except Exception:
            pass
    return [au.publisher_id]


def _registration_statements(registration_uuid):
    rows = M('XapiStatement').query.filter_by(registration=registration_uuid, voided=False, is_voiding=False).all()
    return [json.loads(row.body) for row in rows]


def _enforce_cmi5(stmt, auth, batch_prior):
    sid = session_id_of(stmt)
    session_row = auth.session if auth and auth.kind == 'session' else None
    if session_row is not None and sid and sid != session_row.uuid:
        raise ApiError(403, 'This token can only write its own session.')
    if session_row is None and sid:
        session_row = M('Cmi5Session').query.filter_by(uuid=str(sid)).first()
    if auth and auth.kind == 'session' and session_row is None:
        raise ApiError(403, 'This token is not an active session.')
    if session_row is None:
        return None
    if session_row.is_waive:
        raise ApiError(400, 'A waived session does not accept assignable-unit statements.')
    registration = _db.session.get(M('Cmi5Registration'), session_row.registration_id)
    au = _db.session.get(M('Cmi5AU'), session_row.au_id)
    actor = json.loads(registration.actor_json)
    prior = [item for item in _registration_statements(registration.uuid) if session_id_of(item) == session_row.uuid]
    prior.extend(item for item in batch_prior if session_id_of(item) == session_row.uuid)
    reg_prior = [item for item in _registration_statements(registration.uuid)
                 if (item.get('object') or {}).get('id') == au.lms_activity_id]
    reg_prior.extend(item for item in batch_prior if (item.get('object') or {}).get('id') == au.lms_activity_id)
    check_au_statement(
        stmt, session_row, registration, au, actor,
        _template_grouping(au, actor, registration), prior, reg_prior,
    )
    return session_row


def store_statements(raw_statements, auth, bypass_cmi5=False):
    """Validate and store statements. Returns the ids in request order."""
    authority = _authority(auth)
    if auth is not None and auth.kind == 'session':
        for raw in raw_statements:
            if not isinstance(raw, dict):
                continue
            if not raw.get('id'):
                raise ApiError(403, 'A cmi5 statement must include an id.')
            stamp = raw.get('timestamp')
            if not stamp:
                raise ApiError(403, 'A cmi5 statement must include a timestamp.')
            if not str(stamp).endswith('Z'):
                raise ApiError(403, 'A cmi5 timestamp must be UTC.')
    normalized = [normalize_statement(item) for item in raw_statements]
    ids = []
    touched_sessions = []
    batch = []
    for stmt in normalized:
        existing = _statement_row(stmt['id'])
        if existing:
            if canonical_statement(json.loads(existing.body)) != canonical_statement(stmt):
                raise ApiError(409, 'A different statement is already stored with this id.')
            ids.append(stmt['id'])
            continue
        verb_id = stmt['verb']['id']
        is_voiding = verb_id == VOIDED
        void_target = None
        if is_voiding:
            if auth and auth.kind == 'session':
                raise ApiError(403, 'The assignable unit is not allowed to void statements.')
            obj = stmt.get('object') or {}
            if obj.get('objectType') != 'StatementRef':
                raise ApiError(400, 'A voiding statement object must be a StatementRef.')
            void_target = str(obj.get('id') or '')
            target = _statement_row(void_target)
            if target is not None and target.is_voiding:
                raise ApiError(400, 'A voiding statement cannot be voided.')
        session_row = None
        if not bypass_cmi5:
            session_row = _enforce_cmi5(stmt, auth, batch)
        now = utcnow()
        stmt['stored'] = iso(now)
        stmt['authority'] = authority
        voided = False
        if not is_voiding and M('XapiStatement').query.filter(
                M('XapiStatement').is_voiding.is_(True),
                M('XapiStatement').void_target.ilike(stmt['id'])).first():
            voided = True
        if is_voiding and void_target:
            target = _statement_row(void_target)
            if target is not None:
                target.voided = True
        row = M('XapiStatement')(
            id=stmt['id'],
            stored=now,
            statement_timestamp=parse_iso(stmt['timestamp']),
            actor_key=agent_key(stmt.get('actor') or {})[:1000],
            verb_id=verb_id[:400],
            object_id=((stmt.get('object') or {}).get('id') or '')[:1000],
            registration=((stmt.get('context') or {}).get('registration') or None),
            body=json.dumps(stmt, ensure_ascii=False),
            voided=voided,
            is_voiding=is_voiding,
            void_target=void_target,
        )
        _db.session.add(row)
        ids.append(stmt['id'])
        batch.append(stmt)
        if session_row is not None:
            if VERB_NAME_OF(stmt) == 'terminated':
                session_row.terminated_at = now
            touched_sessions.append((session_row, stmt))
    _db.session.commit()
    if _after_store and touched_sessions and not bypass_cmi5:
        _after_store(touched_sessions)
    return ids


def VERB_NAME_OF(stmt):
    from .util import VERB_NAME
    return VERB_NAME.get(((stmt.get('verb') or {}).get('id')))


def store_lms_statement(stmt):
    """Store one LMS-issued statement. cmi5 session rules are not applied."""
    ids = store_statements([stmt], auth=None, bypass_cmi5=True)
    return ids[0]


# -------------------------------------------------------------------------------------------- query
def _bool_arg(name, default=False):
    raw = _args().get(name)
    if raw is None or raw == '':
        return default
    if str(raw).lower() == 'true':
        return True
    if str(raw).lower() == 'false':
        return False
    raise ApiError(400, name + ' must be true or false')


def _limit_arg(raw):
    if raw is None or raw == '':
        return 100
    try:
        number = int(raw)
    except (TypeError, ValueError) as exc:
        raise ApiError(400, 'limit must be an integer') from exc
    if number < 0:
        raise ApiError(400, 'limit must be zero or greater')
    if number == 0:
        return 1000
    return min(number, 1000)


def _activity_ids(stmt, related):
    found = set()
    if not isinstance(stmt, dict):
        return found
    obj = stmt.get('object') if isinstance(stmt.get('object'), dict) else {}
    kind = obj.get('objectType') or 'Activity'
    if kind == 'Activity' and isinstance(obj.get('id'), str):
        found.add(obj['id'])
    if kind == 'SubStatement':
        found |= _activity_ids(obj, True)
    if related:
        ctx = stmt.get('context') if isinstance(stmt.get('context'), dict) else {}
        groups = ctx.get('contextActivities') if isinstance(ctx.get('contextActivities'), dict) else {}
        for key in ('parent', 'grouping', 'category', 'other'):
            items = groups.get(key) or []
            if isinstance(items, dict):
                items = [items]
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and isinstance(item.get('id'), str):
                    found.add(item['id'])
    return found


def _stmt_matches(stmt, params, agent, related_activities, related_agents):
    if not isinstance(stmt, dict):
        return False
    verb = stmt.get('verb') if isinstance(stmt.get('verb'), dict) else {}
    if params.get('verb') and verb.get('id') != params['verb']:
        return False
    if params.get('registration'):
        ctx = stmt.get('context') if isinstance(stmt.get('context'), dict) else {}
        if str(ctx.get('registration') or '').lower() != str(params['registration']).lower():
            return False
    if params.get('activity') and params['activity'] not in _activity_ids(stmt, related_activities):
        return False
    if agent is not None and not any(agents_match(agent, item) for item in _collect_agents(stmt, related_agents)):
        return False
    return True


def _collect_agents(stmt, related):
    found = []
    actor = stmt.get('actor')
    if isinstance(actor, dict):
        found.append(actor)
        if related and actor.get('objectType') == 'Group':
            found.extend(actor.get('member') or [])
    if not related:
        return found
    obj = stmt.get('object') or {}
    if obj.get('objectType') in ('Agent', 'Group'):
        found.append(obj)
        found.extend(obj.get('member') or [])
    if obj.get('objectType') == 'SubStatement':
        found.extend(_collect_agents(obj, True))
    ctx = stmt.get('context') or {}
    if isinstance(ctx.get('instructor'), dict):
        found.append(ctx['instructor'])
    team = ctx.get('team')
    if isinstance(team, dict):
        found.append(team)
        found.extend(team.get('member') or [])
    return found


def _format_statement(stmt, fmt):
    if fmt == 'ids':
        return _ids_format(stmt)
    if fmt == 'canonical':
        return _canonical_format(stmt, request.headers.get('Accept-Language') or '')
    return stmt


def _ids_agent(agent):
    if not isinstance(agent, dict):
        return agent
    kind = agent.get('objectType') or 'Agent'
    out = {'objectType': kind}
    for key in ('mbox', 'mbox_sha1sum', 'openid', 'account'):
        if agent.get(key):
            out[key] = agent[key]
            break
    if kind == 'Group' and agent.get('member'):
        out['member'] = [_ids_agent(member) for member in agent['member']]
    return out


def _ids_object(obj):
    if not isinstance(obj, dict):
        return obj
    kind = obj.get('objectType') or 'Activity'
    if kind == 'Activity':
        return {'id': obj.get('id')}
    if kind in ('Agent', 'Group'):
        return _ids_agent(obj)
    if kind == 'StatementRef':
        return {'objectType': 'StatementRef', 'id': obj.get('id')}
    if kind == 'SubStatement':
        copy = {
            'objectType': 'SubStatement',
            'actor': _ids_agent(obj.get('actor')),
            'verb': {'id': (obj.get('verb') or {}).get('id')},
            'object': _ids_object(obj.get('object')),
        }
        return copy
    return {'objectType': kind, 'id': obj.get('id')}


def _ids_format(stmt):
    out = {}
    for key in ('id', 'timestamp', 'stored', 'version', 'result', 'context', 'authority'):
        if key in stmt:
            out[key] = stmt[key]
    out['actor'] = _ids_agent(stmt.get('actor'))
    out['verb'] = {'id': (stmt.get('verb') or {}).get('id')}
    out['object'] = _ids_object(stmt.get('object'))
    return out


def _pick_lang(langmap, accept):
    if not isinstance(langmap, dict) or not langmap:
        return langmap
    prefs = [part.split(';')[0].strip() for part in accept.split(',') if part.strip()]
    for pref in prefs:
        if pref in langmap:
            return {pref: langmap[pref]}
        for key, value in langmap.items():
            if key.lower().startswith(pref.lower()) or pref.lower().startswith(key.lower().split('-')[0]):
                return {key: value}
    key = next(iter(langmap))
    return {key: langmap[key]}


def _canonical_format(stmt, accept):
    def walk(node):
        if isinstance(node, dict):
            out = {}
            for key, value in node.items():
                if key in ('display', 'name', 'description') and isinstance(value, dict):
                    out[key] = _pick_lang(value, accept)
                else:
                    out[key] = walk(value)
            return out
        if isinstance(node, list):
            return [walk(item) for item in node]
        return node
    return walk(stmt)


def _more_token(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    secret = _app.secret_key
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    sig = hashlib.sha256(secret + b'.' + raw).hexdigest()
    token = base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')
    return token + '.' + sig


def _read_more(token):
    try:
        encoded, sig = token.rsplit('.', 1)
        pad = '=' * (-len(encoded) % 4)
        raw = base64.urlsafe_b64decode(encoded + pad)
    except Exception as exc:
        raise ApiError(400, 'more is not a valid continuation') from exc
    secret = _app.secret_key
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    if hashlib.sha256(secret + b'.' + raw).hexdigest() != sig:
        raise ApiError(400, 'more is not a valid continuation')
    return json.loads(raw.decode('utf-8'))


def _query_statements(params):
    fmt = params.get('format') or 'exact'
    if fmt not in ('exact', 'ids', 'canonical'):
        raise ApiError(400, 'format must be exact, ids, or canonical')
    ascending = str(params.get('ascending') or 'false').lower() == 'true'
    if str(params.get('ascending') or 'false').lower() not in ('true', 'false'):
        raise ApiError(400, 'ascending must be true or false')
    related_activities = str(params.get('related_activities') or 'false').lower() == 'true'
    related_agents = str(params.get('related_agents') or 'false').lower() == 'true'
    for name in ('related_activities', 'related_agents', 'attachments'):
        raw = params.get(name)
        if raw not in (None, '', 'true', 'false', True, False):
            if str(raw).lower() not in ('true', 'false'):
                raise ApiError(400, name + ' must be true or false')
    attachments = str(params.get('attachments') or 'false').lower() == 'true'
    limit = _limit_arg(params.get('limit'))
    offset = int(params.get('offset') or 0)
    agent = None
    if params.get('agent'):
        try:
            agent = json.loads(params['agent']) if isinstance(params['agent'], str) else params['agent']
        except Exception as exc:
            raise ApiError(400, 'agent must be a JSON agent') from exc
        _validate_actor(agent, 'agent')
    if params.get('verb') and not is_iri(params['verb']):
        raise ApiError(400, 'verb must be an IRI')
    if params.get('activity') and not is_iri(params['activity']):
        raise ApiError(400, 'activity must be an IRI')
    if params.get('registration') and not is_uuid(params['registration']):
        raise ApiError(400, 'registration must be a UUID')
    since = parse_iso(params['since']) if params.get('since') else None
    until = parse_iso(params['until']) if params.get('until') else None

    query = M('XapiStatement').query
    if params.get('verb'):
        query = query.filter_by(verb_id=params['verb'])
    if params.get('registration'):
        query = query.filter_by(registration=params['registration'])
    if params.get('activity') and not related_activities:
        query = query.filter_by(object_id=params['activity'])
    if agent is not None and not related_agents:
        query = query.filter_by(actor_key=agent_key(agent)[:1000])
    if since is not None:
        query = query.filter(M('XapiStatement').stored > since)
    if until is not None:
        query = query.filter(M('XapiStatement').stored <= until)
    rows = query.all()
    matched = []
    voided_hits = set()
    for row in rows:
        stmt = json.loads(row.body)
        if not _stmt_matches(stmt, params, agent, related_activities, related_agents):
            continue
        if row.voided:
            voided_hits.add((row.id or '').lower())
        else:
            matched.append((row, stmt))
    if voided_hits:
        seen = {row.id for row, _stmt in matched}
        voiding = M('XapiStatement').query.filter_by(is_voiding=True, voided=False)
        if since is not None:
            voiding = voiding.filter(M('XapiStatement').stored > since)
        if until is not None:
            voiding = voiding.filter(M('XapiStatement').stored <= until)
        for row in voiding.all():
            target = (row.void_target or '').lower()
            if target in voided_hits and row.id not in seen:
                matched.append((row, json.loads(row.body)))
                seen.add(row.id)
    matched.sort(key=lambda pair: (pair[0].stored, pair[0].id), reverse=not ascending)
    statements = [stmt for _row, stmt in matched]
    page = statements[offset:offset + limit]
    result = {'statements': [_format_statement(item, fmt) for item in page]}
    if offset + limit < len(statements):
        nxt = dict(params)
        nxt['offset'] = offset + limit
        nxt['limit'] = limit
        nxt['format'] = fmt
        nxt['ascending'] = 'true' if ascending else 'false'
        token = _more_token(nxt)
        result['more'] = request.host_url.rstrip('/') + '/xAPI/statements?' + urlencode({'more': token})
    else:
        result['more'] = ''
    extra = {'X-Experience-API-Consistent-Through': iso(utcnow())}
    if attachments:
        payload, ctype = _multipart_result(result, page)
        return xapi_response(payload, content_type=ctype, extra=extra)
    return xapi_response(result, extra=extra)


def _multipart_result(result, statements):
    boundary = 'novak' + new_uuid().replace('-', '')
    chunks = []
    body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    chunks.append(f'--{boundary}\r\nContent-Type: application/json\r\n\r\n'.encode('utf-8') + body + b'\r\n')
    seen = set()
    for stmt in statements:
        for attachment in stmt.get('attachments') or []:
            sha = attachment.get('sha2')
            if not sha or sha in seen:
                continue
            row = _db.session.get(M('XapiAttachment'), sha)
            if row is None:
                continue
            seen.add(sha)
            ctype = attachment.get('contentType') or row.content_type or 'application/octet-stream'
            chunks.append(
                f'--{boundary}\r\nContent-Type: {ctype}\r\nContent-Transfer-Encoding: binary\r\n'
                f'X-Experience-API-Hash: {sha}\r\n\r\n'.encode('utf-8') + bytes(row.content) + b'\r\n'
            )
    chunks.append(f'--{boundary}--\r\n'.encode('utf-8'))
    return b''.join(chunks), 'multipart/mixed; boundary=' + boundary


# -------------------------------------------------------------------------------------------- documents
def _etag_values(header):
    if not header:
        return []
    values = []
    for part in header.split(','):
        token = part.strip()
        if token.startswith('W/'):
            token = token[2:].strip()
        values.append(token.strip('"'))
    return values


def _precondition(doc, write=True):
    if_match = _header('If-Match')
    if_none = _header('If-None-Match')
    if if_match is not None:
        tags = _etag_values(if_match)
        if doc is None or ('*' not in tags and doc.etag not in tags):
            raise ApiError(412, 'If-Match precondition failed')
    if if_none is not None and write:
        tags = _etag_values(if_none)
        if doc is not None and ('*' in tags or doc.etag in tags):
            raise ApiError(412, 'If-None-Match precondition failed')


def _find_doc(kind, activity_id, agent, registration, doc_id):
    return M('XapiDocument').query.filter_by(
        kind=kind, activity_id=activity_id or '', agent_key=agent or '',
        registration=registration or '', doc_id=doc_id or '',
    ).first()


def _write_doc(kind, activity_id, agent, registration, doc_id, content, content_type):
    now = utcnow()
    etag = sha1_etag(content)
    row = _find_doc(kind, activity_id, agent, registration, doc_id)
    if row is None:
        row = M('XapiDocument')(
            kind=kind, activity_id=activity_id or '', agent_key=agent or '',
            registration=registration or '', doc_id=doc_id or '',
            content=content, content_type=content_type, etag=etag, updated_at=now,
        )
        _db.session.add(row)
    else:
        row.content = content
        row.content_type = content_type
        row.etag = etag
        row.updated_at = now
    _db.session.commit()
    return row


def _doc_response(row):
    if_none = _header('If-None-Match')
    if if_none:
        tags = _etag_values(if_none)
        if '*' in tags or row.etag in tags:
            return xapi_response(None, status=304, etag=row.etag)
    return xapi_response(
        bytes(row.content), content_type=row.content_type, etag=row.etag,
        extra={'Last-Modified': iso(row.updated_at)},
    )


def _require_agent():
    raw = _args().get('agent')
    if not raw:
        raise ApiError(400, 'agent is required')
    try:
        agent = json.loads(raw)
    except Exception as exc:
        raise ApiError(400, 'agent must be a JSON agent') from exc
    _validate_actor(agent, 'agent')
    return agent_key(agent)


def _registration_arg():
    raw = _args().get('registration') or ''
    if raw and not is_uuid(raw):
        raise ApiError(400, 'registration must be a UUID')
    return raw


def _session_may_document(auth, activity_id, agent, registration, doc_id, method):
    if not auth or auth.kind != 'session':
        return
    session_row = auth.session
    au = _db.session.get(M('Cmi5AU'), session_row.au_id)
    reg = _db.session.get(M('Cmi5Registration'), session_row.registration_id)
    actor = json.loads(reg.actor_json)
    if activity_id and activity_id != au.lms_activity_id:
        raise ApiError(403, 'This token can only use its assignable unit.')
    if agent and agent != agent_key(actor):
        raise ApiError(403, 'This token can only use its learner.')
    if registration and registration != reg.uuid:
        raise ApiError(403, 'This token can only use its registration.')
    if method in ('PUT', 'POST', 'DELETE') and doc_id == 'LMS.LaunchData':
        raise ApiError(403, 'The assignable unit cannot change LMS.LaunchData.')
    if method == 'DELETE' and not doc_id:
        raise ApiError(403, 'The assignable unit cannot delete every state document.')


def _state_or_profile(kind):
    method = _method()
    activity_id = _args().get('activityId') or ''
    agent = ''
    registration = ''
    if kind == 'state':
        if not activity_id or not is_iri(activity_id):
            raise ApiError(400, 'activityId is required')
        agent = _require_agent()
        registration = _registration_arg()
        doc_name = 'stateId'
    elif kind == 'activity':
        if not activity_id or not is_iri(activity_id):
            raise ApiError(400, 'activityId is required')
        doc_name = 'profileId'
    else:
        agent = _require_agent()
        doc_name = 'profileId'
    doc_id = _args().get(doc_name) or ''
    _session_may_document(getattr(g, 'xapi_auth', None), activity_id, agent, registration, doc_id, method)
    if kind == 'agent' and doc_id == 'cmi5LearnerPreferences' and method == 'GET':
        auth = getattr(g, 'xapi_auth', None)
        if auth is not None and auth.kind == 'session' and not auth.session.prefs_read:
            auth.session.prefs_read = True
            _db.session.commit()
    if kind == 'agent' and doc_id == 'cmi5LearnerPreferences' and method in ('PUT', 'POST'):
        _validate_learner_prefs(_content_type(), _body_bytes())
    if method == 'GET' and not doc_id:
        since_raw = _args().get('since')
        query = M('XapiDocument').query.filter_by(
            kind=kind, activity_id=activity_id, agent_key=agent, registration=registration,
        )
        if since_raw:
            query = query.filter(M('XapiDocument').updated_at > parse_iso(since_raw))
        ids = [row.doc_id for row in query.order_by(M('XapiDocument').doc_id.asc()).all() if row.doc_id]
        return xapi_response(ids)
    if not doc_id:
        raise ApiError(400, doc_name + ' is required')
    row = _find_doc(kind, activity_id, agent, registration, doc_id)
    if method == 'GET':
        if row is None:
            raise ApiError(404, 'Document not found')
        return _doc_response(row)
    if method == 'DELETE':
        if row is not None:
            _db.session.delete(row)
            _db.session.commit()
        return xapi_response(None, status=204)
    content_type = (_content_type() or '').split(';')[0].strip() or 'application/octet-stream'
    if 'application/json' in content_type:
        try:
            json.loads(_body_bytes().decode('utf-8') if _body_bytes() else '')
        except Exception as exc:
            raise ApiError(400, 'JSON document is invalid') from exc
    if method == 'PUT':
        if_match = _header('If-Match')
        if_none = _header('If-None-Match')
        # State documents are created with a plain PUT. Profile resources require a precondition.
        if kind != 'state' and if_match is None and if_none is None:
            if row is None:
                raise ApiError(400, 'If-Match or If-None-Match is required')
            raise ApiError(409, 'The document already exists. Send If-Match or If-None-Match.')
        _precondition(row, write=True)
        if not _content_type():
            raise ApiError(400, 'Content-Type is required')
        _write_doc(kind, activity_id, agent, registration, doc_id, _body_bytes(), content_type)
        saved = _find_doc(kind, activity_id, agent, registration, doc_id)
        return xapi_response(None, status=204, etag=saved.etag)
    if method == 'POST':
        _precondition(row, write=True)
        incoming = _body_bytes()
        if row is None:
            if not _content_type():
                raise ApiError(400, 'Content-Type is required')
            _write_doc(kind, activity_id, agent, registration, doc_id, incoming, content_type)
        else:
            if 'application/json' not in (content_type or '') or 'json' not in (row.content_type or ''):
                raise ApiError(400, 'POST merges JSON documents. Use PUT to replace other content.')
            try:
                merged = json.loads(row.content.decode('utf-8') or '{}')
                posted = json.loads(incoming.decode('utf-8') or '{}')
            except Exception as exc:
                raise ApiError(400, 'POST merge requires JSON objects') from exc
            if not isinstance(merged, dict) or not isinstance(posted, dict):
                raise ApiError(400, 'POST merge requires JSON objects')
            merged.update(posted)
            _write_doc(kind, activity_id, agent, registration, doc_id,
                       json.dumps(merged, ensure_ascii=False).encode('utf-8'), 'application/json')
        saved = _find_doc(kind, activity_id, agent, registration, doc_id)
        return xapi_response(None, status=204, etag=saved.etag)
    raise ApiError(405, 'Method not allowed')


def delete_state_many():
    """DELETE activities/state with no stateId removes every document in scope."""
    activity_id = _args().get('activityId') or ''
    if not activity_id or not is_iri(activity_id):
        raise ApiError(400, 'activityId is required')
    agent = _require_agent()
    registration = _registration_arg()
    _session_may_document(getattr(g, 'xapi_auth', None), activity_id, agent, registration, '', 'DELETE')
    M('XapiDocument').query.filter_by(
        kind='state', activity_id=activity_id, agent_key=agent, registration=registration,
    ).delete()
    _db.session.commit()
    return xapi_response(None, status=204)


# -------------------------------------------------------------------------------------------- routes
def _agent_person():
    raw = _args().get('agent')
    if not raw:
        raise ApiError(400, 'agent is required')
    try:
        agent = json.loads(raw)
    except Exception as exc:
        raise ApiError(400, 'agent must be a JSON agent') from exc
    _validate_actor(agent, 'agent')
    person = {'objectType': 'Person'}
    for key in ('name', 'mbox', 'mbox_sha1sum', 'openid'):
        if agent.get(key):
            person[key] = [agent[key]] if key != 'name' or isinstance(agent[key], str) else agent[key]
            if key == 'name' and isinstance(agent[key], str):
                person['name'] = [agent[key]]
    if isinstance(agent.get('account'), dict):
        person['account'] = [agent['account']]
    return xapi_response(person)


def _merge_definition(base, extra):
    if not isinstance(extra, dict):
        return base
    if not isinstance(base, dict):
        return json.loads(json.dumps(extra))
    out = dict(base)
    for key, value in extra.items():
        if key in ('name', 'description') and isinstance(value, dict):
            merged = dict(out.get(key) or {})
            for lang, text in value.items():
                merged.setdefault(lang, text)
            out[key] = merged
        elif key == 'extensions' and isinstance(value, dict):
            merged = dict(out.get('extensions') or {})
            for ext_key, ext_value in value.items():
                merged.setdefault(ext_key, ext_value)
            out['extensions'] = merged
        elif key not in out:
            out[key] = value
    return out


def _activity_definition():
    activity_id = _args().get('activityId')
    if not activity_id or not is_iri(activity_id):
        raise ApiError(400, 'activityId is required')
    found = {'objectType': 'Activity', 'id': activity_id}
    rows = M('XapiStatement').query.filter_by(object_id=activity_id).order_by(
        M('XapiStatement').stored.asc()).all()
    definition = None
    for row in rows:
        body = json.loads(row.body)
        obj = body.get('object') if isinstance(body.get('object'), dict) else {}
        if obj.get('id') != activity_id:
            continue
        definition = _merge_definition(definition, obj.get('definition'))
    if definition:
        found['definition'] = definition
    return xapi_response(found)


def mount(bp, csrf):
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']

    @bp.route('/xAPI/about', methods=['GET', 'HEAD', 'OPTIONS'])
    @csrf.exempt
    def xapi_about():
        # The About resource is readable without a credential (xAPI 1.0.3).
        try:
            if request.method == 'OPTIONS':
                resp = Response(status=200)
                resp.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
                resp.headers['Access-Control-Allow-Headers'] = (
                    'Authorization, X-Experience-API-Version, Content-Type, If-Match, If-None-Match'
                )
                return _cors(resp)
            if request.method == 'HEAD':
                g.xapi_head = True
            return xapi_response({'version': list(SUPPORTED_VERSIONS)})
        except ApiError as exc:
            return xapi_error(exc.status, exc.message)

    @bp.route('/xAPI/statements', methods=methods)
    @csrf.exempt
    def xapi_statements():
        try:
            if request.method == 'OPTIONS':
                return _guard(lambda: None)()
            if request.method == 'HEAD':
                g.xapi_head = True
            _prepare_alternate()
            _check_version()
            g.xapi_auth = _authenticate()
            method = _method()
            if method == 'GET':
                _check_params({
                    'statementId', 'voidedStatementId', 'agent', 'verb', 'activity', 'registration',
                    'related_activities', 'related_agents', 'since', 'until', 'limit', 'ascending',
                    'format', 'attachments', 'more',
                })
            elif method == 'PUT':
                _check_params({'statementId'})
            elif method == 'POST':
                _check_params(set())
            if method in ('POST', 'PUT'):
                _require_prefs(g.xapi_auth)
            if method == 'PUT':
                return _put_statement()
            if method == 'POST':
                ids = store_statements(_parse_statements(_body_bytes(), _content_type()), g.xapi_auth)
                return xapi_response(ids)
            if method == 'GET':
                return _get_statements()
            raise ApiError(405, 'Method not allowed')
        except ApiError as exc:
            _db.session.rollback()
            resp = xapi_error(exc.status, exc.message, www=exc.status == 401)
            resp.headers['X-Experience-API-Consistent-Through'] = iso(utcnow())
            return resp

    @bp.route('/xAPI/activities/state', methods=methods)
    @csrf.exempt
    def xapi_state():
        try:
            if request.method == 'OPTIONS':
                return _guard(lambda: None)()
            if request.method == 'HEAD':
                g.xapi_head = True
            _prepare_alternate()
            _check_version()
            g.xapi_auth = _authenticate()
            _check_params({'activityId', 'agent', 'registration', 'stateId', 'since'})
            if _method() == 'DELETE' and not _args().get('stateId'):
                return delete_state_many()
            return _state_or_profile('state')
        except ApiError as exc:
            _db.session.rollback()
            return xapi_error(exc.status, exc.message, www=exc.status == 401)

    @bp.route('/xAPI/activities/profile', methods=methods)
    @csrf.exempt
    def xapi_activity_profile():
        try:
            if request.method == 'OPTIONS':
                return _guard(lambda: None)()
            if request.method == 'HEAD':
                g.xapi_head = True
            _prepare_alternate()
            _check_version()
            g.xapi_auth = _authenticate()
            _check_params({'activityId', 'profileId', 'since'})
            return _state_or_profile('activity')
        except ApiError as exc:
            _db.session.rollback()
            return xapi_error(exc.status, exc.message, www=exc.status == 401)

    @bp.route('/xAPI/agents', methods=['GET', 'HEAD', 'OPTIONS'])
    @csrf.exempt
    def xapi_agents():
        try:
            if request.method == 'OPTIONS':
                return _guard(lambda: None)()
            if request.method == 'HEAD':
                g.xapi_head = True
            _prepare_alternate()
            _check_version()
            g.xapi_auth = _authenticate()
            _check_params({'agent'})
            return _agent_person()
        except ApiError as exc:
            _db.session.rollback()
            return xapi_error(exc.status, exc.message, www=exc.status == 401)

    @bp.route('/xAPI/activities', methods=['GET', 'HEAD', 'OPTIONS'])
    @csrf.exempt
    def xapi_activities():
        try:
            if request.method == 'OPTIONS':
                return _guard(lambda: None)()
            if request.method == 'HEAD':
                g.xapi_head = True
            _prepare_alternate()
            _check_version()
            g.xapi_auth = _authenticate()
            _check_params({'activityId'})
            return _activity_definition()
        except ApiError as exc:
            _db.session.rollback()
            return xapi_error(exc.status, exc.message, www=exc.status == 401)

    @bp.route('/xAPI/agents/profile', methods=methods)
    @csrf.exempt
    def xapi_agent_profile():
        try:
            if request.method == 'OPTIONS':
                return _guard(lambda: None)()
            if request.method == 'HEAD':
                g.xapi_head = True
            _prepare_alternate()
            _check_version()
            g.xapi_auth = _authenticate()
            _check_params({'agent', 'profileId', 'since'})
            return _state_or_profile('agent')
        except ApiError as exc:
            _db.session.rollback()
            return xapi_error(exc.status, exc.message, www=exc.status == 401)



def _validate_learner_prefs(content_type, body):
    """cmi5 learner preferences must be a JSON object with both properties (section 11)."""
    ctype = (content_type or '').split(';')[0].strip().lower()
    if ctype != 'application/json':
        raise ApiError(403, 'cmi5LearnerPreferences must be a JSON object.')
    try:
        data = json.loads(body.decode('utf-8') if isinstance(body, (bytes, bytearray)) else body or '{}')
    except Exception as exc:
        raise ApiError(403, 'cmi5LearnerPreferences must be a JSON object.') from exc
    if not isinstance(data, dict) or 'languagePreference' not in data or 'audioPreference' not in data:
        raise ApiError(403, 'cmi5LearnerPreferences must include languagePreference and audioPreference.')
    langs = data.get('languagePreference')
    tag = re.compile(r'^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$')
    parts = langs.split(',') if isinstance(langs, str) else []
    if not parts or any(not tag.match(part.strip()) or part != part.strip() for part in parts):
        raise ApiError(403, 'languagePreference must be a comma-separated list of language tags.')
    if data.get('audioPreference') not in ('on', 'off'):
        raise ApiError(403, 'audioPreference must be on or off.')


def _require_prefs(auth):
    if auth is None or auth.kind != 'session':
        return
    row = auth.session
    if row.launch_mode in ('Browse', 'Review') or row.prefs_read:
        return
    earlier = M('Cmi5Session').query.filter_by(registration_id=row.registration_id, prefs_read=True).first()
    if earlier is not None:
        return
    raise ApiError(403, 'Retrieve cmi5LearnerPreferences before sending statements.')


def _put_statement():
    statement_id = _args().get('statementId')
    if not statement_id or not is_uuid(statement_id):
        raise ApiError(400, 'statementId must be a UUID')
    stmts = _parse_statements(_body_bytes(), _content_type())
    if len(stmts) != 1:
        raise ApiError(400, 'PUT stores one statement.')
    stmt = stmts[0]
    if stmt.get('id') and stmt['id'].lower() != statement_id.lower():
        raise ApiError(400, 'statement id does not match statementId')
    stmt['id'] = statement_id
    store_statements([stmt], g.xapi_auth)
    return xapi_response(None, status=204)


def _check_params(allowed):
    for key in _args().keys():
        if key not in allowed:
            raise ApiError(400, 'unrecognized parameter')


def _get_statements():
    args = _args()
    if args.get('more'):
        if set(args.keys()) != {'more'}:
            raise ApiError(400, 'more cannot be combined with other parameters')
        params = _read_more(args.get('more'))
        return _query_statements(params)
    statement_id = args.get('statementId')
    voided_id = args.get('voidedStatementId')
    if statement_id and voided_id:
        raise ApiError(400, 'Use either statementId or voidedStatementId')
    if statement_id or voided_id:
        extra = {k for k in args.keys() if k not in ('statementId', 'voidedStatementId', 'format', 'attachments')}
        if extra:
            raise ApiError(400, 'statementId cannot be combined with other filters')
        target = statement_id or voided_id
        if not is_uuid(target):
            raise ApiError(400, 'statement id must be a UUID')
        row = _statement_row(target)
        if row is None or (statement_id and row.voided) or (voided_id and not row.voided):
            raise ApiError(404, 'Statement not found')
        fmt = args.get('format') or 'exact'
        if fmt not in ('exact', 'ids', 'canonical'):
            raise ApiError(400, 'format must be exact, ids, or canonical')
        stmt = _format_statement(json.loads(row.body), fmt)
        extra_headers = {'X-Experience-API-Consistent-Through': iso(utcnow())}
        if str(args.get('attachments') or 'false').lower() == 'true':
            payload, ctype = _multipart_result({'statements': [stmt]}, [json.loads(row.body)])
            # A single-statement GET with attachments is still multipart, but the first
            # part is the statement object itself (not a statements wrapper).
            boundary = ctype.split('boundary=')[1]
            raw = json.dumps(stmt, ensure_ascii=False).encode('utf-8')
            body = (
                f'--{boundary}\r\nContent-Type: application/json\r\n\r\n'.encode('utf-8') + raw + b'\r\n'
                + payload.split(b'\r\n', 1)[-1]
            )
            # Simpler: rebuild from the statement only.
            payload, ctype = _multipart_single(stmt, json.loads(row.body))
            return xapi_response(payload, content_type=ctype, extra=extra_headers)
        return xapi_response(stmt, extra=extra_headers)
    params = {k: args.get(k) for k in (
        'agent', 'verb', 'activity', 'registration', 'related_activities', 'related_agents',
        'since', 'until', 'limit', 'ascending', 'format', 'attachments',
    ) if args.get(k) is not None}
    return _query_statements(params)


def _multipart_single(stmt, original):
    wrapped, ctype = _multipart_result({'statements': [original]}, [original])
    # Replace the JSON part with the single statement while keeping attachment parts.
    boundary = ctype.split('boundary=', 1)[1]
    marker = b'\r\n\r\n'
    head, _, rest = wrapped.partition(marker)
    _, _, tail = rest.partition(b'\r\n--' + boundary.encode('utf-8'))
    raw = json.dumps(stmt, ensure_ascii=False).encode('utf-8')
    body = head + marker + raw + b'\r\n--' + boundary.encode('utf-8') + tail
    return body, ctype
