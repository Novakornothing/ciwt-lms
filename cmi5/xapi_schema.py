"""Strict xAPI 1.0.3 statement checks used by the in-app LRS.

The ADL LRS conformance suite rejects a statement unless every property has the
specified type, case, and format. Null is allowed only inside extensions.
"""
import re

from .util import ApiError, is_iri, is_uuid

SIGNATURE_USAGE = 'http://adlnet.gov/expapi/attachments/signature'
INTERACTION_TYPES = (
    'true-false', 'choice', 'fill-in', 'long-fill-in', 'matching',
    'performance', 'sequencing', 'likert', 'numeric', 'other',
)
STATEMENT_KEYS = {
    'id', 'actor', 'verb', 'object', 'result', 'context', 'timestamp',
    'stored', 'authority', 'version', 'attachments',
}
SUB_KEYS = {'actor', 'verb', 'object', 'result', 'context', 'timestamp', 'attachments', 'objectType'}
AGENT_KEYS = {'objectType', 'name', 'mbox', 'mbox_sha1sum', 'openid', 'account', 'member'}
ACCOUNT_KEYS = {'homePage', 'name'}
VERB_KEYS = {'id', 'display'}
ACTIVITY_KEYS = {'objectType', 'id', 'definition'}
DEFINITION_KEYS = {
    'name', 'description', 'type', 'moreInfo', 'extensions', 'interactionType',
    'correctResponsesPattern', 'choices', 'scale', 'source', 'target', 'steps',
}
RESULT_KEYS = {'score', 'success', 'completion', 'response', 'duration', 'extensions'}
SCORE_KEYS = {'scaled', 'raw', 'min', 'max'}
CONTEXT_KEYS = {
    'registration', 'instructor', 'team', 'contextActivities', 'revision',
    'platform', 'language', 'statement', 'extensions',
}
CONTEXT_ACTIVITY_KEYS = {'parent', 'grouping', 'category', 'other'}
ATTACHMENT_KEYS = {'usageType', 'display', 'contentType', 'length', 'sha2', 'description', 'fileUrl'}
REF_KEYS = {'objectType', 'id'}

# RFC 5646 language tags, the practical form the conformance suite checks.
_LANG = re.compile(
    r'^('
    r'([A-Za-z]{2,3}(-[A-Za-z]{3}){0,3}|[A-Za-z]{4}|[A-Za-z]{5,8})'
    r'(-[A-Za-z]{4})?'
    r'(-([A-Za-z]{2}|\d{3}))?'
    r'(-([A-Za-z0-9]{5,8}|\d[A-Za-z0-9]{3}))*'
    r'(-[0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+)*'
    r'(-[Xx](-[A-Za-z0-9]{1,8})+)*'
    r')$'
)
_SHA1 = re.compile(r'^[0-9a-fA-F]{40}$')
_VERSION = re.compile(r'^1\.0(\.\d+)?$')
_NEG_ZERO_OFFSET = re.compile(r'-00(?::00|00)?$')
_SHA2 = re.compile(r'^[0-9a-fA-F]{64}$')
_DUR_WEEKS = re.compile(r'^P\d+W$')
_DUR = re.compile(
    r'^P((\d+Y)?(\d+M)?(\d+D)?)?(T(\d+H)?(\d+M)?(\d+(\.\d+)?S)?)?$'
)


def _bad(message):
    raise ApiError(400, message)


def _keys(node, allowed, label):
    if not isinstance(node, dict):
        _bad(label + ' must be an object')
    for key in node:
        if key not in allowed:
            _bad(label + ' property is not recognized: ' + str(key))


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _bad(label + ' must be a number')


def _string(value, label):
    if not isinstance(value, str):
        _bad(label + ' must be a string')


def _boolean(value, label):
    if not isinstance(value, bool):
        _bad(label + ' must be a boolean')


def _reject_nulls(node, under_extensions=False):
    if node is None:
        if not under_extensions:
            _bad('null is not allowed outside extensions')
        return
    if isinstance(node, list):
        for item in node:
            _reject_nulls(item, under_extensions)
        return
    if not isinstance(node, dict):
        return
    for key, value in node.items():
        if key == 'extensions' and isinstance(value, dict) and not under_extensions:
            if value is None:
                _bad('null is not allowed outside extensions')
            for ext_value in value.values():
                _reject_nulls(ext_value, True)
        else:
            _reject_nulls(value, under_extensions)


def is_language(value):
    return isinstance(value, str) and _LANG.match(value) is not None


def is_duration(value):
    if not isinstance(value, str) or value in ('P', 'PT') or not value.startswith('P'):
        return False
    if _DUR_WEEKS.match(value):
        return True
    if 'W' in value or not _DUR.match(value):
        return False
    if value == 'P' or value.endswith('T') or 'T' in value and value.endswith('T'):
        return False
    # A time designator must introduce at least one component, and a date
    # designator must too. The regex already requires digits before T or after.
    body = value[1:]
    if body.startswith('T'):
        return len(body) > 1
    return any(ch.isdigit() for ch in body)


def _iso_timestamp(value, label):
    from .util import parse_iso
    _string(value, label)
    if _NEG_ZERO_OFFSET.search(value):
        _bad(label + ' cannot use a -00 offset')
    parse_iso(value)


def statement_version_ok(value):
    return isinstance(value, str) and _VERSION.match(value) is not None


def _language_map(value, label):
    if not isinstance(value, dict):
        _bad(label + ' must be a language map')
    for key, text in value.items():
        if not is_language(key):
            _bad(label + ' language tag is not valid')
        if not isinstance(text, str):
            _bad(label + ' values must be strings')


def _extensions(value, label):
    if not isinstance(value, dict):
        _bad(label + ' must be an object')
    for key in value:
        if not is_iri(key):
            _bad(label + ' keys must be IRIs')


def _mbox(value):
    _string(value, 'mbox')
    if not value.lower().startswith('mailto:') or not is_iri(value):
        _bad('mbox must be a mailto IRI')
    address = value.split(':', 1)[1]
    if '@' not in address or address.startswith('@') or address.endswith('@') or any(ch.isspace() for ch in value):
        _bad('mbox must be a mailto IRI')


def _account(value, label):
    _keys(value, ACCOUNT_KEYS, label + ' account')
    if 'homePage' not in value or 'name' not in value:
        _bad(label + ' account requires homePage and name')
    if not is_iri(value.get('homePage')):
        _bad(label + ' account homePage must be an IRI')
    _string(value.get('name'), label + ' account name')
    if value.get('name') == '':
        _bad(label + ' account name is empty')


def validate_agent(actor, label, allow_group=True):
    """Validate an Agent or Group. Returns the inverse-functional identifier count."""
    _keys(actor, AGENT_KEYS, label)
    if 'objectType' in actor:
        _string(actor.get('objectType'), label + ' objectType')
    kind = actor.get('objectType') or 'Agent'
    if kind == 'Agent':
        pass
    elif kind == 'Group' and allow_group:
        pass
    else:
        _bad(label + ' objectType must be Agent or Group')
    if 'name' in actor:
        _string(actor.get('name'), label + ' name')
    ifis = [key for key in ('mbox', 'mbox_sha1sum', 'openid', 'account') if key in actor]
    if 'mbox' in actor:
        _mbox(actor.get('mbox'))
    if 'mbox_sha1sum' in actor:
        _string(actor.get('mbox_sha1sum'), 'mbox_sha1sum')
        if not _SHA1.match(actor['mbox_sha1sum']):
            _bad('mbox_sha1sum must be a SHA-1 hex string')
    if 'openid' in actor:
        if not is_iri(actor.get('openid')):
            _bad('openid must be a URI')
    if 'account' in actor:
        _account(actor.get('account'), label)
    members = actor.get('member')
    if kind == 'Agent':
        if members is not None:
            _bad('An Agent cannot have members')
        if len(ifis) != 1:
            _bad(label + ' must have exactly one inverse functional identifier')
        return 1
    if members is not None and not isinstance(members, list):
        _bad('group member must be an array')
    if len(ifis) > 1:
        _bad('A group must have at most one inverse functional identifier')
    if not ifis and not members:
        _bad('An anonymous group must list its members')
    for member in members or []:
        validate_agent(member, 'group member', allow_group=False)
    if ifis:
        return 1
    return 0


def _activity(obj, label):
    _keys(obj, ACTIVITY_KEYS, label)
    if 'objectType' in obj and obj.get('objectType') != 'Activity':
        _bad(label + ' objectType must be Activity')
    if not is_iri(obj.get('id')):
        _bad(label + ' id must be an IRI')
    definition = obj.get('definition')
    if definition is None:
        return
    _keys(definition, DEFINITION_KEYS, label + ' definition')
    if 'name' in definition:
        _language_map(definition.get('name'), label + ' name')
    if 'description' in definition:
        _language_map(definition.get('description'), label + ' description')
    if 'type' in definition and not is_iri(definition.get('type')):
        _bad(label + ' type must be an IRI')
    if 'moreInfo' in definition and not is_iri(definition.get('moreInfo')):
        _bad(label + ' moreInfo must be an IRI')
    if 'extensions' in definition:
        _extensions(definition.get('extensions'), label + ' extensions')
    interaction = definition.get('interactionType')
    component_keys = ('correctResponsesPattern', 'choices', 'scale', 'source', 'target', 'steps')
    uses_interaction = any(key in definition for key in component_keys)
    if uses_interaction and 'interactionType' not in definition:
        _bad(label + ' interactionType is required')
    if 'interactionType' in definition:
        _string(interaction, 'interactionType')
        if interaction not in INTERACTION_TYPES:
            _bad('interactionType is not a recognized value')
    if 'correctResponsesPattern' in definition:
        pattern = definition.get('correctResponsesPattern')
        if not isinstance(pattern, list) or not all(isinstance(item, str) for item in pattern):
            _bad('correctResponsesPattern must be an array of strings')
    for key in ('choices', 'scale', 'source', 'target', 'steps'):
        if key not in definition:
            continue
        items = definition.get(key)
        if not isinstance(items, list):
            _bad(key + ' must be an array')
        for item in items:
            _interaction_component(item, key)


def _interaction_component(item, label):
    if not isinstance(item, dict):
        _bad(label + ' must be an object')
    allowed = {'id', 'description'}
    for key in item:
        if key not in allowed:
            _bad(label + ' property is not recognized: ' + str(key))
    if 'id' not in item or not isinstance(item.get('id'), str) or item.get('id') == '':
        _bad(label + ' id must be a string')
    if 'description' in item:
        _language_map(item.get('description'), label + ' description')


def _score(score):
    _keys(score, SCORE_KEYS, 'score')
    for key in ('scaled', 'raw', 'min', 'max'):
        if key in score:
            _number(score[key], 'score ' + key)
    if 'scaled' in score and not -1 <= score['scaled'] <= 1:
        _bad('scaled score must be between -1 and 1')
    raw = score.get('raw')
    minimum = score.get('min')
    maximum = score.get('max')
    if minimum is not None and maximum is not None and minimum > maximum:
        _bad('score min cannot be greater than max')
    if raw is not None and minimum is not None and raw < minimum:
        _bad('score raw must be between min and max')
    if raw is not None and maximum is not None and raw > maximum:
        _bad('score raw must be between min and max')


def _result(result, label):
    _keys(result, RESULT_KEYS, label)
    if 'score' in result:
        _score(result.get('score'))
    if 'success' in result:
        _boolean(result.get('success'), 'success')
    if 'completion' in result:
        _boolean(result.get('completion'), 'completion')
    if 'response' in result:
        _string(result.get('response'), 'response')
    if 'duration' in result and not is_duration(result.get('duration')):
        _bad('duration must be an ISO 8601 duration')
    if 'extensions' in result:
        _extensions(result.get('extensions'), 'result extensions')


def _context_activities(value, label):
    _keys(value, CONTEXT_ACTIVITY_KEYS, label)
    for key in CONTEXT_ACTIVITY_KEYS:
        if key not in value:
            continue
        item = value[key]
        if isinstance(item, dict):
            items = [item]
        elif isinstance(item, list):
            items = item
        else:
            _bad(label + ' ' + key + ' must be an activity or an array')
        if not items:
            _bad(label + ' ' + key + ' is empty')
        for activity in items:
            _activity(activity, label + ' ' + key)
        value[key] = items


def _context(ctx, label, object_kind):
    _keys(ctx, CONTEXT_KEYS, label)
    if 'registration' in ctx and not is_uuid(str(ctx.get('registration') or '')):
        _bad('registration must be a UUID')
    if 'instructor' in ctx:
        validate_agent(ctx.get('instructor'), 'instructor')
    if 'team' in ctx:
        team = ctx.get('team')
        if not isinstance(team, dict) or team.get('objectType') != 'Group':
            _bad('team must be a Group')
        validate_agent(team, 'team')
    if 'contextActivities' in ctx:
        _context_activities(ctx.get('contextActivities'), 'contextActivities')
    if 'revision' in ctx:
        _string(ctx.get('revision'), 'revision')
        if object_kind != 'Activity':
            _bad('revision is only valid when the object is an Activity')
    if 'platform' in ctx:
        _string(ctx.get('platform'), 'platform')
        if object_kind != 'Activity':
            _bad('platform is only valid when the object is an Activity')
    if 'language' in ctx and not is_language(ctx.get('language')):
        _bad('language must be an RFC 5646 tag')
    if 'statement' in ctx:
        ref = ctx.get('statement')
        _keys(ref, REF_KEYS, 'statement reference')
        if ref.get('objectType') != 'StatementRef' or not is_uuid(str(ref.get('id') or '')):
            _bad('context statement must be a StatementRef')
    if 'extensions' in ctx:
        _extensions(ctx.get('extensions'), 'context extensions')


def _validate_authority(auth):
    """Authority is an Agent, or an anonymous Group of exactly two Agents."""
    validate_agent(auth, 'authority')
    if (auth.get('objectType') or 'Agent') != 'Group':
        return
    if any(key in auth for key in ('mbox', 'mbox_sha1sum', 'openid', 'account')):
        _bad('An authority group must be anonymous')
    members = auth.get('member') or []
    if len(members) != 2:
        _bad('An authority group must contain exactly two agents')


def _attachment(item):
    _keys(item, ATTACHMENT_KEYS, 'attachment')
    for required in ('usageType', 'display', 'contentType', 'length', 'sha2'):
        if required not in item:
            _bad('attachment ' + required + ' is required')
    if not is_iri(item.get('usageType')):
        _bad('attachment usageType must be an IRI')
    _language_map(item.get('display'), 'attachment display')
    _string(item.get('contentType'), 'attachment contentType')
    if item.get('contentType') == '':
        _bad('attachment contentType is empty')
    if isinstance(item.get('length'), bool) or not isinstance(item.get('length'), int) or item.get('length') < 0:
        _bad('attachment length must be an integer')
    _string(item.get('sha2'), 'attachment sha2')
    if not _SHA2.match(item['sha2']):
        _bad('attachment sha2 must be a SHA-256 hex string')
    if 'description' in item:
        _language_map(item.get('description'), 'attachment description')
    if 'fileUrl' in item and not is_iri(item.get('fileUrl')):
        _bad('attachment fileUrl must be an IRI')
    if item.get('usageType') == SIGNATURE_USAGE and item.get('contentType') != 'application/octet-stream':
        _bad('A statement signature must have content type application/octet-stream')


def _object(obj, allow_sub):
    if not isinstance(obj, dict):
        _bad('object is required')
    if 'objectType' in obj and not isinstance(obj.get('objectType'), str):
        _bad('objectType must be a string')
    kind = obj.get('objectType') or 'Activity'
    if kind == 'Activity':
        _activity(obj, 'activity')
    elif kind in ('Agent', 'Group'):
        validate_agent(obj, 'object')
    elif kind == 'StatementRef':
        _keys(obj, REF_KEYS, 'StatementRef')
        if not is_uuid(str(obj.get('id') or '')):
            _bad('StatementRef id must be a UUID')
    elif kind == 'SubStatement':
        if not allow_sub:
            _bad('A SubStatement cannot contain another SubStatement')
        _substatement(obj)
    else:
        _bad('objectType is not supported')
    return kind


def _substatement(obj):
    _keys(obj, SUB_KEYS, 'SubStatement')
    if obj.get('objectType') != 'SubStatement':
        _bad('SubStatement objectType is required')
    for banned in ('id', 'stored', 'authority', 'version'):
        if banned in obj:
            _bad('A SubStatement cannot include ' + banned)
    validate_agent(obj.get('actor'), 'substatement actor')
    verb = obj.get('verb')
    _keys(verb, VERB_KEYS, 'substatement verb')
    if not is_iri((verb or {}).get('id')):
        _bad('substatement verb.id must be an IRI')
    if 'display' in verb:
        _language_map(verb.get('display'), 'substatement verb display')
    kind = _object(obj.get('object'), allow_sub=False)
    if 'result' in obj:
        _result(obj.get('result'), 'substatement result')
    if 'context' in obj:
        _context(obj.get('context'), 'substatement context', kind)
    if 'timestamp' in obj:
        _iso_timestamp(obj.get('timestamp'), 'timestamp')
    if 'attachments' in obj:
        items = obj.get('attachments')
        if not isinstance(items, list):
            _bad('attachments must be an array')
        for item in items:
            _attachment(item)


def validate_statement(stmt):
    """Raise ApiError 400 when a statement violates the xAPI 1.0.3 data rules."""
    if not isinstance(stmt, dict):
        _bad('A statement must be a JSON object.')
    _reject_nulls(stmt)
    _keys(stmt, STATEMENT_KEYS, 'statement')
    if 'actor' not in stmt:
        _bad('actor is required')
    if 'verb' not in stmt:
        _bad('verb is required')
    if 'object' not in stmt:
        _bad('object is required')
    if 'id' in stmt and not is_uuid(stmt.get('id')):
        _bad('statement id must be a UUID')
    validate_agent(stmt.get('actor'), 'actor')
    verb = stmt.get('verb')
    _keys(verb, VERB_KEYS, 'verb')
    if not is_iri((verb or {}).get('id')):
        _bad('verb.id must be an IRI')
    if isinstance(verb, dict) and 'display' in verb:
        _language_map(verb.get('display'), 'verb display')
    kind = _object(stmt.get('object'), allow_sub=True)
    if 'result' in stmt:
        _result(stmt.get('result'), 'result')
    if 'context' in stmt:
        _context(stmt.get('context'), 'context', kind)
    if 'timestamp' in stmt:
        _iso_timestamp(stmt.get('timestamp'), 'timestamp')
    if 'stored' in stmt:
        _iso_timestamp(stmt.get('stored'), 'stored')
    if 'authority' in stmt:
        _validate_authority(stmt.get('authority'))
    if 'version' in stmt and not statement_version_ok(stmt.get('version')):
        _bad('statement version is not supported')
    if 'attachments' in stmt:
        items = stmt.get('attachments')
        if not isinstance(items, list):
            _bad('attachments must be an array')
        for item in items:
            _attachment(item)
