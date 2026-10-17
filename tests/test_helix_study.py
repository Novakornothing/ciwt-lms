"""Pass 10: accuracy study (consent, record API, privacy, aggregation honesty, admin-only),
re-check + hardening fields, per-device defaults and the instructor calibration view."""
import json
from types import SimpleNamespace

from helix import analytics as A
from helix.models import STUDY_VERSION


def _start(client, ids, uuid):
    client.post('/api/helix/consent', json={'agree': True, 'camera_ok': True, 'passive_ok': True})
    return client.post('/api/helix/session/start', json={'lesson_id': ids['lesson'], 'section_id': ids['section'],
                                                          'mode': 'gaze', 'device': 'desktop', 'client_uuid': uuid}).get_json()['session_id']


REC = {'context': 'study', 'kind': 'calibration', 'valid': True, 'score': 66, 'error_px': 120, 'error_deg': 3.4,
       'precision_px': 40, 'distance_cm': 55, 'calib_ms': 21000, 'engine': 'mediapipe', 'delegate': 'GPU',
       'camera_res': '1280x720', 'viewport_w': 1440, 'viewport_h': 900, 'dpr': 2, 'device': 'desktop',
       'browser': 'Chrome 141', 'arm_method': 'dots', 'arm_hires': False, 'calib_points': 9, 'pair_id': 'p1-abc',
       'points': [{'fx': 0.5, 'fy': 0.5, 'err': 90, 'n': 14}]}


def _cleanup(app, mod, uid):
    with app.app_context():
        from app import db
        from sqlalchemy import text
        db.session.execute(text('delete from helix_accuracy_record where user_id=:u'), {'u': uid})
        db.session.execute(text('delete from helix_study_consent where user_id=:u'), {'u': uid})
        db.session.commit()


def test_study_record_requires_study_consent(student, app, mod, ids):
    _cleanup(app, mod, ids['student1'])
    # lesson consent alone is not enough
    student.post('/api/helix/consent', json={'agree': True, 'camera_ok': True, 'passive_ok': True})
    r = student.post('/api/helix/study/record', json=REC)
    assert r.status_code == 403 and r.get_json()['error'] == 'study_consent_required'
    assert student.get('/api/helix/config').get_json()['study']['granted'] is False
    # joining needs the box ticked
    student.post('/helix/study', data={'action': 'join'})
    assert student.get('/api/helix/config').get_json()['study']['granted'] is False
    student.post('/helix/study', data={'action': 'join', 'agree': '1'})
    cfg = student.get('/api/helix/config').get_json()
    assert cfg['study'] == {'granted': True, 'version': STUDY_VERSION}
    r = student.post('/api/helix/study/record', json=REC)
    assert r.status_code == 200 and r.get_json()['ok']
    # back-to-back posts are rate limited
    assert student.post('/api/helix/study/record', json=REC).status_code == 429
    with app.app_context():
        from app import db
        from sqlalchemy import text
        row = db.session.execute(text('select * from helix_accuracy_record where id=:i'), {'i': r.get_json()['id']}).mappings().first()
    assert row['browser'] == 'Chrome 141' and row['camera_res'] == '1280x720' and row['error_deg'] == 3.4
    assert json.loads(row['points_json']) == [{'fx': 0.5, 'fy': 0.5, 'err': 90, 'n': 14}]
    _cleanup(app, mod, ids['student1'])


def test_study_record_refuses_media_and_sanitises(student, app, mod, ids):
    _cleanup(app, mod, ids['student1'])
    student.post('/helix/study', data={'action': 'join', 'agree': '1'})
    bad = dict(REC, points=[{'fx': 0.5, 'fy': 0.5, 'landmarks': [[0.1, 0.2]] * 10}])
    assert student.post('/api/helix/study/record', json=bad).get_json()['error'] == 'media_not_accepted'
    assert student.post('/api/helix/study/record', json=dict(REC, snapshot='data:image/png;base64,AAAA')).status_code == 400
    r = student.post('/api/helix/study/record', json=dict(REC, browser='Mozilla/5.0 (X11; Linux) full UA', camera_res='<b>',
                                                          device='fridge', arm_hires=True, error_deg=999, kind='evil'))
    rid = r.get_json()['id']
    with app.app_context():
        from app import db
        from sqlalchemy import text
        row = db.session.execute(text('select * from helix_accuracy_record where id=:i'), {'i': rid}).mappings().first()
    assert row['browser'] == 'Other' and row['camera_res'] == '' and row['device'] == 'desktop'
    assert row['error_deg'] == 90.0 and row['kind'] == 'calibration'
    _cleanup(app, mod, ids['student1'])


def test_study_leave_and_delete(student, app, mod, ids):
    _cleanup(app, mod, ids['student1'])
    student.post('/helix/study', data={'action': 'join', 'agree': '1'})
    assert student.post('/api/helix/study/record', json=REC).status_code == 200
    page = student.get('/helix/study').get_data(as_text=True)
    assert 'Your records (1)' in page and 'Never recorded' in page
    student.post('/helix/study', data={'action': 'delete'})
    assert student.get('/api/helix/config').get_json()['study']['granted'] is False
    with app.app_context():
        from app import db
        from sqlalchemy import text
        n = db.session.execute(text('select count(*) from helix_accuracy_record where user_id=:u'), {'u': ids['student1']}).scalar()
    assert n == 0


def test_admin_accuracy_is_admin_only_and_honest_when_empty(admin, instructor, student):
    assert instructor.get('/admin/helix/accuracy').status_code == 403
    assert student.get('/admin/helix/accuracy').status_code == 403
    assert student.get('/admin/helix/accuracy.csv').status_code == 403
    html = admin.get('/admin/helix/accuracy').get_data(as_text=True)
    assert 'Eye-tracking accuracy' in html and 'Not enough paired data' in html
    csv = admin.get('/admin/helix/accuracy.csv').get_data(as_text=True)
    assert csv.splitlines()[0].startswith('device,browser_family,camera_res,users')
    assert 'student1' not in csv and '@' not in csv            # aggregates only


def test_admin_sets_defaults_served_in_config(admin, student):
    assert student.get('/api/helix/config').get_json()['calib_defaults']['desktop'] == {
        'method': 'dots', 'hires': False, 'basis': 'built-in default (no study evidence yet)'}
    assert student.post('/admin/helix/defaults', data={'device': 'mobile', 'method': 'follow'}).status_code == 403
    admin.post('/admin/helix/defaults', data={'device': 'mobile', 'method': 'follow', 'hires': '1', 'basis': 'test'})
    d = student.get('/api/helix/config').get_json()['calib_defaults']['mobile']
    assert d['method'] == 'follow' and d['hires'] is False      # never 1080p on phones
    admin.post('/admin/helix/defaults', data={'device': 'mobile', 'method': 'dots', 'basis': 'reset after test'})


def test_study_arm_is_balanced_and_pairs_change_one_factor(student):
    a1 = student.get('/api/helix/study/arm?device=desktop&hires_capable=1&pair=zz1').get_json()
    assert a1['ok'] and a1['method'] in ('dots', 'follow') and a1['hires'] in (True, False)
    a = student.get('/api/helix/study/arm?device=mobile&hires_capable=1').get_json()
    assert a['hires'] is False                                     # phones never get the 1080p arm


def _r(uid, deg, device='desktop', method='dots', hires=False, browser='Chrome 141', res='1280x720', valid=True, kind='calibration', ms=20000):
    return SimpleNamespace(user_id=uid, error_deg=deg, error_px=None if deg is None else int(deg * 40), valid=valid, device=device,
                           arm_method=method, arm_hires=hires, browser=browser, camera_res=res, engine='mediapipe',
                           kind=kind, calib_ms=ms)


def test_groups_count_each_person_once_and_flag_small_n():
    recs = [_r(1, 2.0)] * 30 + [_r(2, 6.0), _r(3, 6.0)]           # one keen participant must not dominate
    g = A.study_groups(recs)[0]
    assert g['users'] == 3 and g['records'] == 32 and g['median_deg'] == 6.0 and g['enough'] is False
    recs = [_r(u, 3.0 + u * 0.1) for u in range(1, 7)]
    g = A.study_groups(recs)[0]
    assert g['enough'] is True and g['key'] == {'device': 'desktop', 'browser_family': 'Chrome', 'res': '720p'}
    assert A.res_bucket('1920x1080') == '1080p' and A.res_bucket('480x640') == '480p' and A.res_bucket('x') == 'unknown'
    assert A.browser_tag('Chrome iOS 120') == 'Chrome iOS 120' and A.browser_tag('Mozilla/5.0') == 'Other'


def test_arm_comparison_requires_pairs_and_significance():
    # 6 pairs all favouring follow: not enough pairs, so no suggestion
    recs = []
    for u in range(6):
        recs += [_r(u, 6.0, method='dots'), _r(u, 4.0, method='follow')]
    c = A.arm_comparison(recs, 'desktop', 'method')
    assert c['pairs'] == 6 and c['suggest'] is None and 'Not enough paired data' in c['verdict']
    # 12 pairs, 11 better by 2 deg: suggest follow
    recs = []
    for u in range(12):
        recs += [_r(u, 6.0, method='dots'), _r(u, 4.0 if u < 11 else 7.0, method='follow+dots' if u == 0 else 'follow')]
    c = A.arm_comparison(recs, 'desktop', 'method')
    assert c['pairs'] == 12 and c['suggest'] == 'follow' and c['p'] < 0.05
    # 12 pairs, mixed: no suggestion
    recs = []
    for u in range(12):
        recs += [_r(u, 5.0, hires=False), _r(u, 5.0 + (0.6 if u % 2 else -0.6), hires=True)]
    c = A.arm_comparison(recs, 'desktop', 'hires')
    assert c['suggest'] is None and 'No clear difference' in c['verdict']
    # re-checks and invalid checks never count
    assert A.arm_comparison([_r(1, 3.0, kind='recheck'), _r(1, 2.0, valid=False, method='follow')], 'desktop', 'method')['pairs'] == 0
    assert A.sign_test_p(9, 1) == 0.0215 and A.sign_test_p(0, 0) == 1.0


def test_recheck_and_hardening_counters_stored(student, instructor, app, ids):
    sid = _start(student, ids, 'uuid-p10-1')
    student.post(f'/api/helix/session/{sid}/calibrated', json={
        'calibration_points': 9, 'calibration_score': 70, 'validation_error_px': 80, 'validation_error_deg': 2.1,
        'calib_ms': 24000, 'calib_mode': 'follow', 'camera_res': '1280x720', 'browser': 'Firefox 131', 'hires': False})
    r = student.post(f'/api/helix/session/{sid}/calibrated', json={
        'recheck': True, 'recheck_error_px': 140, 'recheck_error_deg': 3.9, 'recheck_score': 52,
        'validation_error_deg': 9.9, 'camera_losses': 1, 'sleeps': 2, 'tab_yields': 1, 'rechecks': 1})
    assert r.get_json()['band'] == 'Fair'
    # a stale batch with lower counters must not lower them
    student.post(f'/api/helix/session/{sid}/batch', json={'seq': 0, 'segments': [], 'buckets': [], 'camera_losses': 0, 'sleeps': 3})
    with app.app_context():
        from app import db
        from sqlalchemy import text
        row = db.session.execute(text('select * from helix_gaze_session where id=:i'), {'i': sid}).mappings().first()
    assert row['calibration_score'] == 70 and row['validation_error_deg'] == 2.1     # recheck leaves calibration alone
    assert row['rechecks'] == 1 and row['recheck_error_px'] == 140 and row['recheck_error_deg'] == 3.9
    assert row['calib_ms'] == 24000 and row['calib_mode'] == 'follow' and row['browser'] == 'Firefox 131'
    assert row['camera_losses'] == 1 and row['sleeps'] == 3 and row['tab_yields'] == 1
    page = instructor.get(f"/instructor/section/{ids['section']}/attention/calibration").get_data(as_text=True)
    assert 'Calibration quality' in page or 'calibration quality' in page
    assert '24.0 s' in page and '~140 px' in page
    assert instructor.get(f"/instructor/section/{ids['section']}/attention").get_data(as_text=True).count('/attention/calibration') >= 1


def test_calibration_view_forbidden_for_students_and_other_instructors(student, instructor2, ids):
    assert student.get(f"/instructor/section/{ids['section']}/attention/calibration").status_code == 403
    assert instructor2.get(f"/instructor/section/{ids['section']}/attention/calibration").status_code == 403


def test_new_states_are_not_reading_time():
    s = SimpleNamespace(total_ms=0, attentive_ms=0, off_page_ms=0, face_lost_ms=0, hidden_ms=0, low_conf_ms=0, timeline_json=json.dumps([
        {'aoi': '_camera_off', 't0': 0, 't1': 5000}, {'aoi': '_other_tab', 't0': 5000, 't1': 8000},
        {'aoi': '_asleep', 't0': 8000, 't1': 20000}, {'aoi': 'h0', 't0': 20000, 't1': 21000}]))
    b = A.session_breakdown(s)
    assert b['attentive'] == 1000 and b['face_lost'] == 5000 and b['hidden'] == 15000
