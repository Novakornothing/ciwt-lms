"""Shared helpers for the in-app xAPI 1.0.3 LRS and cmi5 launch flow."""
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

XAPI_VERSION = '1.0.3'
SUPPORTED_VERSIONS = ('1.0.0', '1.0.1', '1.0.2', '1.0.3')

CMI5_CATEGORY = 'https://w3id.org/xapi/cmi5/context/categories/cmi5'
MOVEON_CATEGORY = 'https://w3id.org/xapi/cmi5/context/categories/moveon'
SESSION_EXT = 'https://w3id.org/xapi/cmi5/context/extensions/sessionid'
MASTERY_EXT = 'https://w3id.org/xapi/cmi5/context/extensions/masteryscore'
LAUNCHMODE_EXT = 'https://w3id.org/xapi/cmi5/context/extensions/launchmode'
LAUNCHURL_EXT = 'https://w3id.org/xapi/cmi5/context/extensions/launchurl'
MOVEON_EXT = 'https://w3id.org/xapi/cmi5/context/extensions/moveon'
LAUNCHPARAMS_EXT = 'https://w3id.org/xapi/cmi5/context/extensions/launchparameters'
REASON_EXT = 'https://w3id.org/xapi/cmi5/result/extensions/reason'
PROGRESS_EXT = 'https://w3id.org/xapi/cmi5/result/extensions/progress'
BLOCK_TYPE = 'https://w3id.org/xapi/cmi5/activitytype/block'
COURSE_TYPE = 'https://w3id.org/xapi/cmi5/activitytype/course'
VOIDED = 'http://adlnet.gov/expapi/verbs/voided'

VERBS = {
    'launched': 'http://adlnet.gov/expapi/verbs/launched',
    'initialized': 'http://adlnet.gov/expapi/verbs/initialized',
    'completed': 'http://adlnet.gov/expapi/verbs/completed',
    'passed': 'http://adlnet.gov/expapi/verbs/passed',
    'failed': 'http://adlnet.gov/expapi/verbs/failed',
    'terminated': 'http://adlnet.gov/expapi/verbs/terminated',
    'abandoned': 'https://w3id.org/xapi/adl/verbs/abandoned',
    'waived': 'https://w3id.org/xapi/adl/verbs/waived',
    'satisfied': 'https://w3id.org/xapi/adl/verbs/satisfied',
}
VERB_NAME = {v: k for k, v in VERBS.items()}
AU_VERBS = {'initialized', 'completed', 'passed', 'failed', 'terminated'}
LMS_VERBS = {'launched', 'abandoned', 'waived', 'satisfied'}
MOVE_ON_VALUES = ('Passed', 'Completed', 'CompletedAndPassed', 'CompletedOrPassed', 'NotApplicable')

UUID_RE = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
IRI_RE = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$')
DUR_RE = re.compile(
    r'^P(?!$)(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(?=\d)(\d+H)?(\d+M)?(\d+(\.\d+)?S)?)?$'
)
NS = 'https://w3id.org/xapi/profiles/cmi5/v1/CourseStructure.xsd'


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def parse_iso(value):
    if not isinstance(value, str) or not value.strip():
        raise ApiError(400, 'timestamp is not a valid ISO 8601 datetime')
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ApiError(400, 'timestamp is not a valid ISO 8601 datetime') from exc
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def new_uuid():
    return str(uuid.uuid4())


def is_uuid(value):
    return isinstance(value, str) and UUID_RE.match(value) is not None


def is_iri(value):
    return isinstance(value, str) and IRI_RE.match(value) is not None


def is_duration(value):
    return isinstance(value, str) and DUR_RE.match(value) is not None


def iso_duration(seconds):
    seconds = max(0, int(round(seconds)))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f'PT{hours}H{minutes}M{secs}S'
    if minutes:
        return f'PT{minutes}M{secs}S'
    return f'PT{secs}S'


def json_dumps(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'), sort_keys=True)


def canonical_statement(stmt):
    """Compare statements the client sent. Ignore fields the LRS assigns."""
    copy = json.loads(json.dumps(stmt))
    copy.pop('stored', None)
    copy.pop('authority', None)
    copy.setdefault('version', XAPI_VERSION)
    return json_dumps(copy)


def agent_ifis(agent):
    """Inverse functional identifiers. xAPI agents match when any IFI matches."""
    if not isinstance(agent, dict):
        return []
    keys = []
    mbox = agent.get('mbox')
    if isinstance(mbox, str) and mbox.strip():
        keys.append('mbox:' + mbox.strip().lower())
    sha = agent.get('mbox_sha1sum')
    if isinstance(sha, str) and sha.strip():
        keys.append('sha1:' + sha.strip().lower())
    openid = agent.get('openid')
    if isinstance(openid, str) and openid.strip():
        keys.append('openid:' + openid.strip())
    account = agent.get('account')
    if isinstance(account, dict) and account.get('homePage') and account.get('name') is not None:
        keys.append('account:' + str(account['homePage']).strip() + '|' + str(account['name']))
    return keys


def agent_key(agent):
    kind = (agent or {}).get('objectType') or 'Agent'
    if kind == 'Group' and not agent_ifis(agent):
        members = agent.get('member') or []
        parts = []
        for member in members:
            parts.append(','.join(sorted(agent_ifis(member))))
        return 'group:' + ';'.join(sorted(parts))
    return '|'.join(sorted(agent_ifis(agent)))


def agents_match(left, right):
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    li, ri = agent_ifis(left), agent_ifis(right)
    if li and ri and set(li) & set(ri):
        return True
    if (left.get('objectType') == 'Group' and right.get('objectType') == 'Group'
            and not li and not ri):
        return agent_key(left) == agent_key(right) and agent_key(left) != 'group:'
    return False


def as_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def sha256_etag(content):
    digest = hashlib.sha256(content).hexdigest()
    return digest


def sha1_etag(content):
    """Document concurrency tag. The 1.0.3 suite requires a 40-character SHA-1."""
    return hashlib.sha1(content).hexdigest()


def category_ids(stmt):
    ctx = (stmt or {}).get('context') or {}
    activities = (ctx.get('contextActivities') or {}).get('category') or []
    if isinstance(activities, dict):
        activities = [activities]
    ids = []
    for item in activities:
        if isinstance(item, dict) and item.get('id'):
            ids.append(item['id'])
    return ids


def grouping_ids(stmt):
    ctx = (stmt or {}).get('context') or {}
    activities = (ctx.get('contextActivities') or {}).get('grouping') or []
    if isinstance(activities, dict):
        activities = [activities]
    ids = []
    for item in activities:
        if isinstance(item, dict) and item.get('id'):
            ids.append(item['id'])
    return ids


def session_id_of(stmt):
    ext = ((stmt or {}).get('context') or {}).get('extensions') or {}
    return ext.get(SESSION_EXT)


def activity_object(activity_id, name=None, description=None, activity_type=None):
    obj = {'objectType': 'Activity', 'id': activity_id}
    definition = {}
    if name:
        definition['name'] = {'en-US': name}
    if description:
        definition['description'] = {'en-US': description}
    if activity_type:
        definition['type'] = activity_type
    if definition:
        obj['definition'] = definition
    return obj
