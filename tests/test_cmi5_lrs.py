"""cmi5 launch, fetch, LaunchData, verb rules, moveOn, and the in-app xAPI LRS."""
import base64
import io
import json
import uuid
import zipfile
from urllib.parse import parse_qs, urlparse

import pytest
from lxml import etree

NS = 'https://w3id.org/xapi/profiles/cmi5/v1/CourseStructure.xsd'


def _basic(key, secret):
    token = base64.b64encode(f'{key}:{secret}'.encode()).decode()
    return {
        'Authorization': 'Basic ' + token,
        'X-Experience-API-Version': '1.0.3',
    }


def _credential(admin):
    page = admin.post('/admin/exports', data={'action': 'credential', 'name': 'Campus test'})
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    key = html.split('Key <code>')[1].split('</code>')[0]
    secret = html.split('Secret <code>')[1].split('</code>')[0]
    return key, secret


def _actor(name):
    return {'objectType': 'Agent', 'account': {'homePage': 'https://novakornothing.com', 'name': name}}


def _stmt(name, activity, verb='http://adlnet.gov/expapi/verbs/experienced', **extra):
    body = {
        'actor': _actor(name),
        'verb': {'id': verb},
        'object': {'id': activity, 'objectType': 'Activity'},
    }
    body.update(extra)
    return body


def _minimal_zip(move_on='CompletedAndPassed', second='NotApplicable'):
    def au(au_id, title, url, move, mastery=None):
        mastery_attr = f' masteryScore="{mastery}"' if mastery else ''
        return f'''<au id="{au_id}" moveOn="{move}" launchMethod="AnyWindow"{mastery_attr}>
          <title><langstring lang="en-US">{title}</langstring></title>
          <description><langstring lang="en-US">{title} description</langstring></description>
          <url>{url}</url>
        </au>'''
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<courseStructure xmlns="{NS}">
  <course id="https://novakornothing.com/cmi5/test/{uuid.uuid4()}">
    <title><langstring lang="en-US">Sample course</langstring></title>
    <description><langstring lang="en-US">A two-unit sample used to exercise launch and moveOn.</langstring></description>
  </course>
  <block id="https://novakornothing.com/cmi5/test/block/{uuid.uuid4()}">
    <title><langstring lang="en-US">Chapter</langstring></title>
    <description><langstring lang="en-US">One chapter.</langstring></description>
    {au("https://novakornothing.com/cmi5/test/au/one", "Unit one", "au/one.html", move_on, "0.8")}
    {au("https://novakornothing.com/cmi5/test/au/two", "Unit two", "au/two.html", second)}
  </block>
</courseStructure>
'''
    page = b'<html><body><p id="cmi5-status"></p><button id="cmi5-complete">Mark complete</button></body></html>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr('cmi5.xml', xml)
        zf.writestr('au/one.html', page)
        zf.writestr('au/two.html', page)
    return buf.getvalue(), xml


def _import(admin, payload, name='sample-cmi5.zip'):
    response = admin.post('/admin/exports', data={
        'action': 'import',
        'package': (io.BytesIO(payload), name),
    }, content_type='multipart/form-data')
    assert response.status_code == 200, response.get_data(as_text=True)[:500]
    assert 'Imported' in response.get_data(as_text=True)
    return response


def _register_and_launch(admin, learner='Learner'):
    html = admin.get('/admin/exports').get_data(as_text=True)
    # The newest course is first. Its registration form posts course_id.
    marker = 'name="course_id" value="'
    course_id = html.split(marker)[1].split('"', 1)[0]
    created = admin.post('/admin/exports', data={'action': 'register', 'course_id': course_id, 'learner': learner},
                         follow_redirects=True)
    assert created.status_code == 200
    page = created.get_data(as_text=True)
    assert 'Assignable units' in page
    launched = admin.post(created.request.path, data={'action': 'launch', 'au_id': _first_au_id(page), 'launch_mode': 'Normal'})
    assert launched.status_code in (302, 303)
    return launched.headers['Location'], page


def _first_au_id(page):
    return page.split('name="au_id" value="')[1].split('"', 1)[0]


def _launch_params(location):
    query = parse_qs(urlparse(location).query)
    return {key: query[key][0] for key in ('endpoint', 'fetch', 'actor', 'registration', 'activityId')}


def _read_prefs(anon, params, headers):
    response = anon.get(params['endpoint'] + 'agents/profile', query_string={
        'agent': params['actor'],
        'profileId': 'cmi5LearnerPreferences',
    }, headers=headers)
    assert response.status_code == 200, response.get_data(as_text=True)
    return response


def _cmi5_statement(params, launch, verb, result=None):
    actor = json.loads(params['actor'])
    template = json.loads(json.dumps(launch['contextTemplate']))
    template['registration'] = params['registration']
    template.setdefault('contextActivities', {})
    categories = list(template['contextActivities'].get('category') or [])
    categories.append({'id': 'https://w3id.org/xapi/cmi5/context/categories/cmi5', 'objectType': 'Activity'})
    if result and ('success' in result or 'completion' in result):
        categories.append({'id': 'https://w3id.org/xapi/cmi5/context/categories/moveon', 'objectType': 'Activity'})
    template['contextActivities']['category'] = categories
    template.setdefault('extensions', {})
    if result and 'success' in result and launch.get('masteryScore') is not None:
        template['extensions']['https://w3id.org/xapi/cmi5/context/extensions/masteryscore'] = launch['masteryScore']
    body = {
        'id': str(uuid.uuid4()),
        'timestamp': '2026-10-30T12:00:00.000Z',
        'actor': actor,
        'verb': {'id': verb, 'display': {'en-US': verb.rsplit('/', 1)[-1]}},
        'object': {'objectType': 'Activity', 'id': params['activityId']},
        'context': template,
    }
    if result is not None:
        body['result'] = result
    # Give each call a later timestamp unless the caller set one.
    return body


def test_about_version_header_and_basic_auth(anon, admin):
    about = anon.get('/xAPI/about')
    assert about.status_code == 200
    assert about.headers['X-Experience-API-Version'] == '1.0.3'
    assert '1.0.3' in about.get_json()['version']

    missing = anon.post('/xAPI/statements', json=_stmt('nobody', 'https://novakornothing.com/xapi/activities/no-version'))
    assert missing.status_code == 400

    rejected = anon.post(
        '/xAPI/statements',
        json=_stmt('nobody', 'https://novakornothing.com/xapi/activities/bad-auth'),
        headers={'Authorization': 'Basic ' + base64.b64encode(b'no:one').decode(), 'X-Experience-API-Version': '1.0.3'},
    )
    assert rejected.status_code == 401
    assert 'Basic' in rejected.headers.get('WWW-Authenticate', '')

    key, secret = _credential(admin)
    headers = _basic(key, secret)
    bad_version = anon.post('/xAPI/statements', json=_stmt('x', 'https://example.com/a'),
                            headers={**headers, 'X-Experience-API-Version': '0.9.0'})
    assert bad_version.status_code == 400
    ok = anon.post('/xAPI/statements', json=_stmt('campus-reader', 'https://novakornothing.com/xapi/activities/auth-ok'),
                   headers=headers)
    assert ok.status_code == 200
    assert len(ok.get_json()) == 1


def test_statements_put_get_void_filters_and_more(anon, admin):
    key, secret = _credential(admin)
    headers = _basic(key, secret)
    reg = str(uuid.uuid4())
    activity = 'https://novakornothing.com/xapi/activities/paging-' + reg
    ids = []
    for index in range(3):
        body = _stmt('pager', activity, **{'context': {'registration': reg}})
        body['id'] = str(uuid.uuid4())
        body['timestamp'] = f'2026-10-30T15:00:0{index}.000Z'
        posted = anon.post('/xAPI/statements', json=body, headers=headers)
        assert posted.status_code == 200
        ids.append(posted.get_json()[0])

    again = anon.post('/xAPI/statements', json=body, headers=headers)
    assert again.status_code == 200
    clash = dict(body)
    clash['verb'] = {'id': 'http://adlnet.gov/expapi/verbs/answered'}
    conflict = anon.post('/xAPI/statements', json=clash, headers=headers)
    assert conflict.status_code == 409

    one = anon.get('/xAPI/statements', query_string={'statementId': ids[0]}, headers=headers)
    assert one.status_code == 200
    assert one.get_json()['id'] == ids[0]
    assert 'statements' not in one.get_json()

    page = anon.get('/xAPI/statements', query_string={'registration': reg, 'limit': 1}, headers=headers)
    payload = page.get_json()
    assert len(payload['statements']) == 1
    assert payload['more'].startswith('http')
    seen = list(payload['statements'])
    nxt = payload['more']
    while nxt:
        more = anon.get(nxt, headers=headers)
        body = more.get_json()
        seen.extend(body['statements'])
        nxt = body.get('more')
    assert len(seen) == 3

    void_id = ids[0]
    voided = anon.post('/xAPI/statements', json={
        'actor': _actor('pager'),
        'verb': {'id': 'http://adlnet.gov/expapi/verbs/voided'},
        'object': {'objectType': 'StatementRef', 'id': void_id},
    }, headers=headers)
    assert voided.status_code == 200
    listed = anon.get('/xAPI/statements', query_string={'registration': reg, 'limit': 10}, headers=headers)
    listed_ids = [item['id'] for item in listed.get_json()['statements']]
    assert void_id not in listed_ids
    fetched = anon.get('/xAPI/statements', query_string={'voidedStatementId': void_id}, headers=headers)
    assert fetched.status_code == 200
    assert fetched.get_json()['id'] == void_id

    put_id = str(uuid.uuid4())
    stored = _stmt('pager', activity, **{'id': put_id, 'context': {'registration': reg}})
    put = anon.put('/xAPI/statements', query_string={'statementId': put_id}, json=stored, headers=headers)
    assert put.status_code == 204
    mismatch = anon.put('/xAPI/statements', query_string={'statementId': put_id},
                        json=_stmt('other', activity, **{'id': put_id}), headers=headers)
    assert mismatch.status_code == 409


def test_state_activity_profile_and_agent_profile(anon, admin):
    key, secret = _credential(admin)
    headers = _basic(key, secret)
    agent = json.dumps(_actor('state-user'))
    activity = 'https://novakornothing.com/xapi/activities/state-' + uuid.uuid4().hex
    common = {'activityId': activity, 'agent': agent, 'stateId': 'bookmark'}
    first = anon.put('/xAPI/activities/state', query_string=common, data=b'{"place":1}',
                     headers={**headers, 'Content-Type': 'application/json', 'If-None-Match': '*'})
    assert first.status_code == 204
    etag = first.headers['ETag']
    blocked = anon.put('/xAPI/activities/state', query_string=common, data=b'{"place":9}',
                       headers={**headers, 'Content-Type': 'application/json', 'If-Match': '"nope"'})
    assert blocked.status_code == 412
    merged = anon.post('/xAPI/activities/state', query_string=common, data=b'{"page":2}',
                       headers={**headers, 'Content-Type': 'application/json', 'If-Match': etag})
    assert merged.status_code == 204
    got = anon.get('/xAPI/activities/state', query_string=common, headers=headers)
    assert got.get_json() == {'place': 1, 'page': 2}
    names = anon.get('/xAPI/activities/state', query_string={'activityId': activity, 'agent': agent}, headers=headers)
    assert 'bookmark' in names.get_json()

    profile = {'activityId': activity, 'profileId': 'cmi5'}
    assert anon.put('/xAPI/activities/profile', query_string=profile, data=b'{"n":1}',
                    headers={**headers, 'Content-Type': 'application/json', 'If-None-Match': '*'}).status_code == 204
    assert anon.get('/xAPI/activities/profile', query_string=profile, headers=headers).get_json()['n'] == 1

    agent_q = {'agent': agent, 'profileId': 'cmi5LearnerPreferences'}
    assert anon.put('/xAPI/agents/profile', query_string=agent_q, data=b'{"languagePreference":"en-US","audioPreference":"off"}',
                    headers={**headers, 'Content-Type': 'application/json', 'If-None-Match': '*'}).status_code == 204
    prefs = anon.get('/xAPI/agents/profile', query_string=agent_q, headers=headers)
    assert prefs.get_json()['audioPreference'] == 'off'


def test_fetch_is_single_use_and_launchdata_is_written(admin, anon):
    payload, _xml = _minimal_zip()
    _import(admin, payload)
    location, _page = _register_and_launch(admin, 'Fetch learner')
    params = _launch_params(location)
    for key in ('endpoint', 'fetch', 'actor', 'registration', 'activityId'):
        assert params[key]
    assert params['endpoint'].rstrip('/').endswith('/xAPI')
    assert params['activityId'] != 'https://novakornothing.com/cmi5/test/au/one'
    assert anon.get(params['fetch']).status_code == 405

    first = anon.post(params['fetch'])
    assert first.status_code == 200
    token = first.get_json()['auth-token']
    assert token and 'error-code' not in first.get_json()
    second = anon.post(params['fetch'])
    assert second.status_code == 200
    body = second.get_json()
    assert body['error-code'] == '1'
    assert 'auth-token' not in body

    headers = {
        'Authorization': 'Basic ' + token,
        'X-Experience-API-Version': '1.0.3',
    }
    state = anon.get(params['endpoint'] + 'activities/state', query_string={
        'stateId': 'LMS.LaunchData',
        'activityId': params['activityId'],
        'agent': params['actor'],
        'registration': params['registration'],
    }, headers=headers)
    assert state.status_code == 200
    launch = state.get_json()
    assert launch['launchMode'] == 'Normal'
    assert launch['launchMethod'] == 'AnyWindow'
    assert launch['moveOn'] == 'CompletedAndPassed'
    assert launch['masteryScore'] == 0.8
    assert launch['returnURL'].startswith('http')
    assert 'launchParameters' not in launch or isinstance(launch.get('launchParameters'), str)
    session_id = launch['contextTemplate']['extensions']['https://w3id.org/xapi/cmi5/context/extensions/sessionid']
    assert session_id
    grouping = [item['id'] for item in launch['contextTemplate']['contextActivities']['grouping']]
    assert 'https://novakornothing.com/cmi5/test/au/one' in grouping

    # The AU cannot replace LMS.LaunchData or void statements.
    denied = anon.put(params['endpoint'] + 'activities/state', query_string={
        'stateId': 'LMS.LaunchData', 'activityId': params['activityId'],
        'agent': params['actor'], 'registration': params['registration'],
    }, data=b'{}', headers={**headers, 'Content-Type': 'application/json'})
    assert denied.status_code == 403
    voided = anon.post(params['endpoint'] + 'statements', json={
        'actor': json.loads(params['actor']),
        'verb': {'id': 'http://adlnet.gov/expapi/verbs/voided'},
        'object': {'objectType': 'StatementRef', 'id': str(uuid.uuid4())},
    }, headers=headers)
    assert voided.status_code == 403

    # Launched was recorded before the assignable unit opened.
    listed = anon.get(params['endpoint'] + 'statements', query_string={
        'registration': params['registration'], 'limit': 20,
    }, headers=headers)
    verbs = [item['verb']['id'] for item in listed.get_json()['statements']]
    assert 'http://adlnet.gov/expapi/verbs/launched' in verbs


def test_verb_order_and_score_rules_reject_invalid_statements(admin, anon):
    _import(admin, _minimal_zip()[0])
    location, _page = _register_and_launch(admin, 'Rules learner')
    params = _launch_params(location)
    token = anon.post(params['fetch']).get_json()['auth-token']
    headers = {'Authorization': 'Basic ' + token, 'X-Experience-API-Version': '1.0.3'}
    _read_prefs(anon, params, headers)
    state = anon.get(params['endpoint'] + 'activities/state', query_string={
        'stateId': 'LMS.LaunchData', 'activityId': params['activityId'],
        'agent': params['actor'], 'registration': params['registration'],
    }, headers=headers).get_json()

    def post(verb, result=None, stamp='2026-10-30T12:00:00.000Z'):
        body = _cmi5_statement(params, state, verb, result)
        body['timestamp'] = stamp
        return anon.post(params['endpoint'] + 'statements', json=body, headers=headers)

    early = post('http://adlnet.gov/expapi/verbs/completed', {'completion': True, 'duration': 'PT1S'}, '2026-10-30T12:00:01.000Z')
    assert early.status_code == 403
    assert 'initialized' in early.get_data(as_text=True)

    init = post('http://adlnet.gov/expapi/verbs/initialized', None, '2026-10-30T12:00:02.000Z')
    assert init.status_code == 200, init.get_data(as_text=True)
    dup = post('http://adlnet.gov/expapi/verbs/initialized', None, '2026-10-30T12:00:03.000Z')
    assert dup.status_code == 403

    low = post('http://adlnet.gov/expapi/verbs/passed', {
        'success': True, 'duration': 'PT2S', 'score': {'scaled': 0.5, 'raw': 50, 'min': 0, 'max': 100},
    }, '2026-10-30T12:00:04.000Z')
    assert low.status_code == 403

    done = post('http://adlnet.gov/expapi/verbs/completed', {'completion': True, 'duration': 'PT3S'}, '2026-10-30T12:00:05.000Z')
    assert done.status_code == 200, done.get_data(as_text=True)
    passed = post('http://adlnet.gov/expapi/verbs/passed', {
        'success': True, 'duration': 'PT4S', 'score': {'scaled': 1, 'raw': 1, 'min': 0, 'max': 1},
    }, '2026-10-30T12:00:06.000Z')
    assert passed.status_code == 200, passed.get_data(as_text=True)
    failed = post('http://adlnet.gov/expapi/verbs/failed', {
        'success': False, 'duration': 'PT4S', 'score': {'scaled': 0, 'raw': 0, 'min': 0, 'max': 1},
    }, '2026-10-30T12:00:07.000Z')
    assert failed.status_code == 403

    end = post('http://adlnet.gov/expapi/verbs/terminated', {'duration': 'PT5S'}, '2026-10-30T12:00:08.000Z')
    assert end.status_code == 200, end.get_data(as_text=True)
    after = post('http://adlnet.gov/expapi/verbs/experienced', None, '2026-10-30T12:00:09.000Z')
    # experienced without the cmi5 category is an allowed statement, but the session is closed.
    assert after.status_code in (400, 403)


def test_moveon_satisfies_block_and_course_and_not_applicable_rolls_up(admin, anon):
    _import(admin, _minimal_zip()[0])
    location, page = _register_and_launch(admin, 'MoveOn learner')
    # Unit two is NotApplicable, so it does not by itself satisfy the block.
    assert 'Not yet' in page
    params = _launch_params(location)
    token = anon.post(params['fetch']).get_json()['auth-token']
    headers = {'Authorization': 'Basic ' + token, 'X-Experience-API-Version': '1.0.3'}
    _read_prefs(anon, params, headers)
    state = anon.get(params['endpoint'] + 'activities/state', query_string={
        'stateId': 'LMS.LaunchData', 'activityId': params['activityId'],
        'agent': params['actor'], 'registration': params['registration'],
    }, headers=headers).get_json()

    def post(verb, result, stamp):
        body = _cmi5_statement(params, state, verb, result)
        body['timestamp'] = stamp
        response = anon.post(params['endpoint'] + 'statements', json=body, headers=headers)
        assert response.status_code == 200, response.get_data(as_text=True)

    post('http://adlnet.gov/expapi/verbs/initialized', None, '2026-10-30T13:00:01.000Z')
    post('http://adlnet.gov/expapi/verbs/completed', {'completion': True, 'duration': 'PT1S'}, '2026-10-30T13:00:02.000Z')
    # Completed alone does not meet CompletedAndPassed.
    mid = anon.get('/xAPI/statements', query_string={'registration': params['registration'], 'verb': 'https://w3id.org/xapi/adl/verbs/satisfied', 'limit': 10},
                   headers={'X-Experience-API-Version': '1.0.3', 'Authorization': headers['Authorization']})
    assert mid.get_json()['statements'] == []
    post('http://adlnet.gov/expapi/verbs/passed', {
        'success': True, 'duration': 'PT2S', 'score': {'scaled': 1, 'raw': 1, 'min': 0, 'max': 1},
    }, '2026-10-30T13:00:03.000Z')
    satisfied = anon.get('/xAPI/statements', query_string={
        'registration': params['registration'],
        'verb': 'https://w3id.org/xapi/adl/verbs/satisfied',
        'limit': 10,
    }, headers=headers)
    types = []
    for item in satisfied.get_json()['statements']:
        types.append(((item.get('object') or {}).get('definition') or {}).get('type'))
        session_ext = item['context']['extensions']['https://w3id.org/xapi/cmi5/context/extensions/sessionid']
        assert session_ext == state['contextTemplate']['extensions']['https://w3id.org/xapi/cmi5/context/extensions/sessionid']
    assert 'https://w3id.org/xapi/cmi5/activitytype/block' in types
    assert 'https://w3id.org/xapi/cmi5/activitytype/course' in types


def test_package_export_validates_and_imports_and_lesson_player_launches(admin, anon, student, ids):
    from pathlib import Path
    xsd = etree.XMLSchema(etree.parse(str(Path(__file__).resolve().parents[1] / 'cmi5' / 'xsd' / 'CourseStructure.xsd')))
    downloaded = admin.get('/admin/exports/cmi5/CLIENT.zip')
    assert downloaded.status_code == 200
    assert downloaded.mimetype == 'application/zip'
    with zipfile.ZipFile(io.BytesIO(downloaded.data)) as zf:
        names = set(zf.namelist())
        assert 'cmi5.xml' in names
        xml = zf.read('cmi5.xml')
        xsd.assertValid(etree.fromstring(xml))
        root = etree.fromstring(xml)
        blocks = [el for el in root if etree.QName(el).localname == 'block']
        aus = root.findall(f'.//{{{NS}}}au')
        assert blocks and aus
        for au in aus:
            url = au.find(f'{{{NS}}}url').text
            assert not url.startswith('http')
            assert url in names
    _import(admin, downloaded.data, 'novak-client-cmi5.zip')
    location, _page = _register_and_launch(admin, 'Package learner')
    au_page = anon.get(location)
    assert au_page.status_code == 200
    html = au_page.get_data(as_text=True)
    assert 'initialized' in html and 'terminated' in html and 'passed' in html

    lesson = student.get(f"/student/module/{ids['section']}/{ids['module']}/lesson/{ids['lesson']}")
    assert 'cmi5-au.js' not in lesson.get_data(as_text=True)
    launched = student.get(
        f"/student/module/{ids['section']}/{ids['module']}/lesson/{ids['lesson']}"
        '?endpoint=http://localhost/xAPI/&fetch=http://localhost/cmi5/fetch/demo&actor=%7B%7D&registration='
        + str(uuid.uuid4()) + '&activityId=https://novakornothing.com/xapi/cmi5/au/demo'
    )
    text = launched.get_data(as_text=True)
    assert 'cmi5-au.js' in text
    script = (Path(__file__).resolve().parents[1] / 'static' / 'cmi5-au.js').read_text(encoding='utf-8')
    for verb in ('initialized', 'completed', 'passed', 'failed', 'terminated'):
        assert verb in script


def test_admin_exports_page_and_public_wording(admin, anon):
    page = admin.get('/admin/exports')
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    for text in ('Download cmi5 package', 'Import a cmi5 package', 'Learning record store', 'Registrations'):
        assert text in html
    assert anon.get('/admin/exports').status_code in (302, 401, 403)

    from tests.test_phase1_simplify import VERIFIED_PUBLIC_CLAIMS, _without_verified_claims
    for path in ('/landing', '/compliance', '/specs', '/compare', '/gaps', '/consult', '/llms.txt', '/llms-full.txt'):
        body = anon.get(path).get_data(as_text=True)
        scrubbed = _without_verified_claims(body)
        assert 'cmi5 compliant' not in scrubbed, path
        assert 'cmi5 conformant' not in scrubbed, path
        assert '(cmi5)' not in scrubbed, path
        assert '9274' not in scrubbed, path
    for path in ('/specs', '/compliance', '/compare', '/llms.txt'):
        lowered = anon.get(path).get_data(as_text=True).lower()
        for phrase in VERIFIED_PUBLIC_CLAIMS:
            assert phrase in lowered, (path, phrase)


def test_relaunch_abandons_the_open_session(admin, anon):
    _import(admin, _minimal_zip()[0])
    location, page = _register_and_launch(admin, 'Abandon learner')
    params = _launch_params(location)
    token = anon.post(params['fetch']).get_json()['auth-token']
    headers = {'Authorization': 'Basic ' + token, 'X-Experience-API-Version': '1.0.3'}
    _read_prefs(anon, params, headers)
    state = anon.get(params['endpoint'] + 'activities/state', query_string={
        'stateId': 'LMS.LaunchData', 'activityId': params['activityId'],
        'agent': params['actor'], 'registration': params['registration'],
    }, headers=headers).get_json()
    body = _cmi5_statement(params, state, 'http://adlnet.gov/expapi/verbs/initialized')
    body['timestamp'] = '2026-10-30T14:00:01.000Z'
    assert anon.post(params['endpoint'] + 'statements', json=body, headers=headers).status_code == 200

    listed = admin.get('/admin/exports')
    link = listed.get_data(as_text=True).split('Abandon learner')[0].rsplit('href="', 1)[-1].split('"', 1)[0]
    second = admin.post(link, data={'action': 'launch', 'au_id': _first_au_id(admin.get(link).get_data(as_text=True)), 'launch_mode': 'Normal'})
    assert second.status_code in (302, 303)
    closed = anon.post(params['endpoint'] + 'statements', json=body, headers=headers)
    assert closed.status_code in (401, 403)
    fresh = _launch_params(second.headers['Location'])
    fresh_headers = {
        'Authorization': 'Basic ' + anon.post(fresh['fetch']).get_json()['auth-token'],
        'X-Experience-API-Version': '1.0.3',
    }
    found = anon.get(fresh['endpoint'] + 'statements', query_string={
        'registration': fresh['registration'],
        'verb': 'https://w3id.org/xapi/adl/verbs/abandoned',
        'limit': 5,
    }, headers=fresh_headers)
    assert found.status_code == 200
    assert len(found.get_json()['statements']) >= 1
    assert found.get_json()['statements'][0]['result']['duration'].startswith('PT')
