"""cmi5 LMS runtime: registrations, launch, fetch, LMS statements, and moveOn."""
import base64
import json
import secrets
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from werkzeug.security import generate_password_hash

from . import lrs
from .util import (
    BLOCK_TYPE, CMI5_CATEGORY, COURSE_TYPE, LAUNCHMODE_EXT, LAUNCHPARAMS_EXT,
    LAUNCHURL_EXT, MASTERY_EXT, MOVEON_CATEGORY, MOVEON_EXT, REASON_EXT,
    SESSION_EXT, VERBS, VERB_NAME, activity_object, agent_key, as_decimal,
    category_ids, iso, iso_duration, new_uuid, utcnow,
)

_db = None
_m = None
_app = None


def init(app, db, models):
    global _db, _m, _app
    _db, _m, _app = db, models, app
    lrs.set_after_store(on_statements_stored)


def M(name):
    return _m[name]


def _with_query(url, params):
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    for key, value in params.items():
        query.append((key, value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def absolute_au_url(au, host_url):
    url = au.url or ''
    if url.startswith('http://') or url.startswith('https://'):
        return url
    base = host_url.rstrip('/')
    if url.startswith('/'):
        return base + url
    return base + f'/cmi5/content/{au.course_id}/{url.lstrip("/")}'


def grouping_activities(au):
    ids = []
    if au.publisher_id:
        ids.append(au.publisher_id)
    block_id = au.block_id
    seen = set(ids)
    while block_id:
        block = _db.session.get(M('Cmi5Block'), block_id)
        if block is None or block.publisher_id in seen:
            break
        ids.append(block.publisher_id)
        seen.add(block.publisher_id)
        block_id = block.parent_id
    course = _db.session.get(M('Cmi5Course'), au.course_id)
    if course and course.publisher_id not in seen:
        ids.append(course.publisher_id)
    return [{'objectType': 'Activity', 'id': item} for item in ids]


def _actor(registration):
    return json.loads(registration.actor_json)


def _defined_names(activity_id, registration_uuid):
    rows = M('XapiStatement').query.filter_by(
        object_id=activity_id, registration=registration_uuid, voided=False, is_voiding=False,
    ).all()
    names = []
    for row in rows:
        stmt = json.loads(row.body)
        if CMI5_CATEGORY not in category_ids(stmt):
            continue
        name = VERB_NAME.get(row.verb_id)
        if name:
            names.append(name)
    return names


def au_moveon_met(au, registration):
    names = _defined_names(au.lms_activity_id, registration.uuid)
    if 'waived' in names:
        return True
    move = au.move_on or 'NotApplicable'
    if move == 'NotApplicable':
        return True
    if move == 'Passed':
        return 'passed' in names
    if move == 'Completed':
        return 'completed' in names
    if move == 'CompletedAndPassed':
        return 'passed' in names and 'completed' in names
    if move == 'CompletedOrPassed':
        return 'passed' in names or 'completed' in names
    return False


def _base_context(registration, session_id, grouping, extra_extensions=None, moveon_category=False):
    extensions = {SESSION_EXT: session_id}
    if extra_extensions:
        extensions.update(extra_extensions)
    categories = [{'id': CMI5_CATEGORY, 'objectType': 'Activity'}]
    if moveon_category:
        categories.append({'id': MOVEON_CATEGORY, 'objectType': 'Activity'})
    return {
        'registration': registration.uuid,
        'contextActivities': {'grouping': grouping, 'category': categories},
        'extensions': extensions,
    }


def _statement(registration, verb, obj, context, result=None):
    stmt = {
        'id': new_uuid(),
        'timestamp': iso(utcnow()),
        'actor': _actor(registration),
        'verb': {'id': VERBS[verb], 'display': {'en-US': verb}},
        'object': obj,
        'context': context,
    }
    if result is not None:
        stmt['result'] = result
    return stmt


def _session_statements(registration, session_id):
    rows = M('XapiStatement').query.filter_by(registration=registration.uuid, voided=False, is_voiding=False).all()
    out = []
    for row in rows:
        stmt = json.loads(row.body)
        if ((stmt.get('context') or {}).get('extensions') or {}).get(SESSION_EXT) == session_id:
            out.append(stmt)
    return out


def _issue_abandoned(session_row, registration, au):
    stmts = _session_statements(registration, session_row.uuid)
    launched = next((item for item in stmts if (item.get('verb') or {}).get('id') == VERBS['launched']), None)
    au_verbs = {VERBS[name] for name in ('initialized', 'completed', 'passed', 'failed', 'terminated')}
    au_stmts = [item for item in stmts if (item.get('verb') or {}).get('id') in au_verbs]
    start = launched.get('timestamp') if launched else iso(session_row.launched_at or utcnow())
    end = au_stmts[-1]['timestamp'] if au_stmts else iso(utcnow())
    try:
        from .util import parse_iso
        seconds = (parse_iso(end) - parse_iso(start)).total_seconds()
    except Exception:
        seconds = 0
    if not au_stmts:
        try:
            from .util import parse_iso
            seconds = (utcnow() - parse_iso(start)).total_seconds()
        except Exception:
            seconds = 0
    grouping = grouping_activities(au)
    context = _base_context(registration, session_row.uuid, grouping)
    obj = activity_object(au.lms_activity_id, au.title, au.description, au.activity_type)
    stmt = _statement(registration, 'abandoned', obj, context, {'duration': iso_duration(seconds)})
    lrs.store_lms_statement(stmt)
    session_row.abandoned_at = utcnow()


def _launch_data(session_row, registration, au, return_url):
    mastery = as_decimal(au.mastery_score) if au.mastery_score not in (None, '') else None
    document = {
        'contextTemplate': {
            'contextActivities': {'grouping': grouping_activities(au)},
            'extensions': {SESSION_EXT: session_row.uuid},
        },
        'launchMode': session_row.launch_mode,
        'launchMethod': au.launch_method or 'AnyWindow',
        'moveOn': au.move_on or 'NotApplicable',
        'returnURL': return_url,
    }
    if mastery is not None:
        document['masteryScore'] = float(mastery)
    if au.launch_parameters:
        document['launchParameters'] = au.launch_parameters
    if au.entitlement_key:
        document['entitlementKey'] = {'courseStructure': au.entitlement_key}
    return document


def _write_launch_data(session_row, registration, au, document):
    actor = _actor(registration)
    payload = json.dumps(document, ensure_ascii=False).encode('utf-8')
    lrs._write_doc(
        'state', au.lms_activity_id, agent_key(actor), registration.uuid,
        'LMS.LaunchData', payload, 'application/json',
    )


def _seed_preferences(registration):
    actor = _actor(registration)
    key = agent_key(actor)
    existing = M('XapiDocument').query.filter_by(
        kind='agent', activity_id='', agent_key=key, registration='', doc_id='cmi5LearnerPreferences',
    ).first()
    if existing:
        return
    payload = json.dumps({'languagePreference': 'en-US', 'audioPreference': 'off'}).encode('utf-8')
    lrs._write_doc('agent', '', key, '', 'cmi5LearnerPreferences', payload, 'application/json')


def _launched_statement(session_row, registration, au, launch_url):
    mastery = as_decimal(au.mastery_score) if au.mastery_score not in (None, '') else None
    extra = {
        LAUNCHMODE_EXT: session_row.launch_mode,
        MOVEON_EXT: au.move_on or 'NotApplicable',
        LAUNCHURL_EXT: launch_url,
    }
    if mastery is not None:
        extra[MASTERY_EXT] = float(mastery)
    if au.launch_parameters:
        extra[LAUNCHPARAMS_EXT] = au.launch_parameters
    context = _base_context(registration, session_row.uuid, grouping_activities(au), extra)
    obj = activity_object(au.lms_activity_id, au.title, au.description, au.activity_type)
    return _statement(registration, 'launched', obj, context)


def launch_session(registration, au, host_url, launch_mode='Normal'):
    if launch_mode not in ('Normal', 'Browse', 'Review'):
        launch_mode = 'Normal'
    for old in M('Cmi5Session').query.filter_by(
        registration_id=registration.id, au_id=au.id, is_waive=False,
    ).filter(M('Cmi5Session').terminated_at.is_(None), M('Cmi5Session').abandoned_at.is_(None)).all():
        _issue_abandoned(old, registration, au)
    _db.session.commit()
    session_row = M('Cmi5Session')(
        uuid=new_uuid(),
        registration_id=registration.id,
        au_id=au.id,
        launch_mode=launch_mode,
        fetch_secret=secrets.token_urlsafe(24),
        launched_at=utcnow(),
    )
    _db.session.add(session_row)
    _db.session.flush()
    launch_url = absolute_au_url(au, host_url)
    return_url = host_url.rstrip('/') + '/cmi5/return/' + session_row.uuid
    session_row.return_url = return_url
    session_row.launch_url = launch_url
    document = _launch_data(session_row, registration, au, return_url)
    _write_launch_data(session_row, registration, au, document)
    lrs.store_lms_statement(_launched_statement(session_row, registration, au, launch_url))
    endpoint = host_url.rstrip('/') + '/xAPI/'
    fetch = host_url.rstrip('/') + '/cmi5/fetch/' + session_row.fetch_secret
    actor = json.dumps(_actor(registration), separators=(',', ':'))
    target = _with_query(launch_url, {
        'endpoint': endpoint,
        'fetch': fetch,
        'actor': actor,
        'registration': registration.uuid,
        'activityId': au.lms_activity_id,
    })
    return session_row, target


def fetch_auth(secret):
    row = M('Cmi5Session').query.filter_by(fetch_secret=secret).first()
    if row is None:
        return {'error-code': '2', 'error-text': 'Unknown fetch URL.'}
    if row.fetch_used_at or row.terminated_at or row.abandoned_at:
        return {'error-code': '1', 'error-text': 'The authorization token has already been returned.'}
    username = 'cmi5' + row.uuid.replace('-', '')[:20]
    password = secrets.token_urlsafe(24)
    row.auth_username = username
    row.auth_secret_hash = generate_password_hash(password)
    row.fetch_used_at = utcnow()
    _db.session.commit()
    token = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('ascii')
    return {'auth-token': token}


def create_registration(course, learner_label, actor=None, registration_uuid=None):
    label = (learner_label or 'Learner').strip()[:200] or 'Learner'
    if actor is None:
        slug = ''.join(ch if ch.isalnum() else '-' for ch in label).strip('-') or 'learner'
        actor = {
            'objectType': 'Agent',
            'account': {
                'homePage': 'https://novakornothing.com',
                'name': f'{slug}-{secrets.token_hex(3)}',
            },
        }
    if isinstance(actor, dict) and 'objectType' not in actor:
        actor = {'objectType': 'Agent', **actor}
    if not isinstance(actor, dict) or actor.get('objectType') not in ('Agent', 'Group'):
        raise ValueError('The actor must be an xAPI agent.')
    reg_uuid = registration_uuid or new_uuid()
    from .util import is_uuid
    if not is_uuid(reg_uuid):
        raise ValueError('registration must be a UUID')
    existing = M('Cmi5Registration').query.filter_by(uuid=reg_uuid).first()
    if existing:
        return existing
    registration = M('Cmi5Registration')(
        uuid=reg_uuid.lower(),
        course_id=course.id,
        actor_json=json.dumps(actor, ensure_ascii=False),
        learner_label=label,
    )
    _db.session.add(registration)
    _db.session.commit()
    _seed_preferences(registration)
    evaluate_moveon(registration, None)
    return registration


def abandon_session(session_uuid):
    row = M('Cmi5Session').query.filter_by(uuid=session_uuid).first()
    if row is None or row.is_waive or row.terminated_at or row.abandoned_at:
        return False
    registration = _db.session.get(M('Cmi5Registration'), row.registration_id)
    au = _db.session.get(M('Cmi5AU'), row.au_id)
    _issue_abandoned(row, registration, au)
    _db.session.commit()
    return True


def waive_au(registration, au, reason='Administrative'):
    names = _defined_names(au.lms_activity_id, registration.uuid)
    if 'waived' in names:
        raise ValueError('This assignable unit is already waived for this registration.')
    session_id = new_uuid()
    row = M('Cmi5Session')(
        uuid=session_id,
        registration_id=registration.id,
        au_id=au.id,
        launch_mode='Normal',
        is_waive=True,
        terminated_at=utcnow(),
        launched_at=utcnow(),
    )
    _db.session.add(row)
    _db.session.commit()
    context = _base_context(registration, session_id, grouping_activities(au), moveon_category=True)
    obj = activity_object(au.lms_activity_id, au.title, au.description, au.activity_type)
    stmt = _statement(registration, 'waived', obj, context, {
        'success': True,
        'completion': True,
        'extensions': {REASON_EXT: reason},
    })
    lrs.store_lms_statement(stmt)
    evaluate_moveon(registration, session_id)


def _already_satisfied(activity_id, registration_uuid):
    return M('XapiStatement').query.filter_by(
        verb_id=VERBS['satisfied'], object_id=activity_id, registration=registration_uuid,
        voided=False, is_voiding=False,
    ).first() is not None


def _satisfy(registration, activity_id, title, activity_type, publisher_id, session_id):
    if _already_satisfied(activity_id, registration.uuid):
        return
    sid = session_id or new_uuid()
    grouping = [{'objectType': 'Activity', 'id': publisher_id}] if publisher_id else []
    context = _base_context(registration, sid, grouping)
    obj = activity_object(activity_id, title, title, activity_type)
    lrs.store_lms_statement(_statement(registration, 'satisfied', obj, context))


def evaluate_moveon(registration, trigger_session_id):
    course = _db.session.get(M('Cmi5Course'), registration.course_id)
    blocks = M('Cmi5Block').query.filter_by(course_id=course.id).all()
    aus = M('Cmi5AU').query.filter_by(course_id=course.id).order_by(M('Cmi5AU').sort_order).all()
    children = {}
    for block in blocks:
        children.setdefault(block.parent_id, []).append(block)
    aus_by_block = {}
    root_aus = []
    for au in aus:
        if au.block_id:
            aus_by_block.setdefault(au.block_id, []).append(au)
        else:
            root_aus.append(au)

    def block_met(block):
        for au in aus_by_block.get(block.id, []):
            if not au_moveon_met(au, registration):
                return False
        for child in children.get(block.id, []):
            if not block_met(child):
                return False
        return True

    def walk(block):
        for child in children.get(block.id, []):
            walk(child)
        if block_met(block):
            _satisfy(registration, block.lms_activity_id, block.title, BLOCK_TYPE, block.publisher_id, trigger_session_id)

    for block in children.get(None, []):
        walk(block)
    top = children.get(None, [])
    if not root_aus and not top:
        return
    if all(au_moveon_met(au, registration) for au in root_aus) and all(block_met(block) for block in top):
        _satisfy(registration, course.lms_activity_id, course.title, COURSE_TYPE, course.publisher_id, trigger_session_id)


def on_statements_stored(pairs):
    seen = set()
    for session_row, stmt in pairs:
        name = VERB_NAME.get((stmt.get('verb') or {}).get('id'))
        if name not in ('completed', 'passed', 'terminated') or session_row.id in seen:
            continue
        registration = _db.session.get(M('Cmi5Registration'), session_row.registration_id)
        if registration is None:
            continue
        seen.add(session_row.id)
        evaluate_moveon(registration, session_row.uuid)


def registration_rows(registration):
    aus = M('Cmi5AU').query.filter_by(course_id=registration.course_id).order_by(M('Cmi5AU').sort_order).all()
    blocks = {block.id: block for block in M('Cmi5Block').query.filter_by(course_id=registration.course_id).all()}
    rows = []
    for au in aus:
        block = blocks.get(au.block_id)
        names = _defined_names(au.lms_activity_id, registration.uuid)
        rows.append({
            'au': au,
            'block': block,
            'met': au_moveon_met(au, registration),
            'waived': 'waived' in names,
            'verbs': names,
        })
    return rows
