"""Pass 10 steering: debug-off run settings, the neural-TTS switch, the /privacy notice, and the admin
student-record export / delete tool with Helix retention cleanup. Uses a throwaway student so the
seeded accounts other tests rely on are never touched."""
import json
from datetime import timedelta

import pytest
from sqlalchemy import inspect, text

import privacy_tools as P


# ---- run settings -------------------------------------------------------------------------------
def test_run_settings_debug_off_by_default(mod):
    assert mod.run_settings({}) == ('0.0.0.0', 5050, False, '')
    assert mod.run_settings({'FLASK_DEBUG': '0', 'PORT': '6000'})[1:3] == (6000, False)


def test_run_settings_debug_binds_loopback(mod):
    host, _p, debug, note = mod.run_settings({'FLASK_DEBUG': '1'})
    assert (host, debug, note) == ('127.0.0.1', True, '')
    host, _p, debug, note = mod.run_settings({'FLASK_DEBUG': 'true', 'HOST': '0.0.0.0'})
    assert host == '127.0.0.1' and debug and 'CIWT_ALLOW_DEBUG_ON_NETWORK' in note
    assert mod.run_settings({'FLASK_DEBUG': '1', 'HOST': '0.0.0.0', 'CIWT_ALLOW_DEBUG_ON_NETWORK': '1'})[0] == '0.0.0.0'
    assert mod.run_settings({'HOST': '10.0.0.5'})[0] == '10.0.0.5'


def test_start_script_does_not_force_debug():
    from pathlib import Path
    s = (Path(__file__).resolve().parents[1] / 'start_lms.sh').read_text()
    assert 'FLASK_DEBUG=1' not in s.replace('"${FLASK_DEBUG:-0}" = "1"', '').split('echo')[0]


# ---- neural TTS switch --------------------------------------------------------------------------
@pytest.fixture
def tts_off(app):
    old = app.config.get('NEURAL_TTS_ENABLED', True)
    app.config['NEURAL_TTS_ENABLED'] = False
    yield
    app.config['NEURAL_TTS_ENABLED'] = old


def test_narrate_disabled_returns_403(student, tts_off):
    r = student.post('/api/narrate', json={'text': 'Hello there', 'voice': 'en-US-JennyNeural'})
    assert r.status_code == 403
    assert r.get_json() == {'fallback': True, 'disabled': True} or r.get_json().get('disabled') is True


def test_lesson_hides_neural_voice_when_off(student, ids, tts_off):
    html = student.get(f"/student/module/{ids['section']}/{ids['module']}/lesson/{ids['lesson']}").get_data(as_text=True)
    assert 'const NEURAL_TTS = false' in html and 'JennyNeural" selected' not in html


def test_privacy_page_describes_tts(anon, app, tts_off):
    html = anon.get('/privacy').get_data(as_text=True)
    assert 'turned off' in html and 'CIWT_NEURAL_TTS=0' in html


def test_privacy_page_on(anon):
    r = anon.get('/privacy')
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'edge-tts' in html and 'sends the lesson text' in html and 'Helix' in html


# ---- admin tool ---------------------------------------------------------------------------------
@pytest.fixture
def temp_student(app, mod, ids):
    """A throwaway student with an enrolment, Helix consent + session and an audit trail."""
    with app.app_context():
        u = mod.User(email='privacy-temp@lms.local', first_name='Pri', last_name='Vacy', role='student')
        u.set_password('temp12345')
        mod.db.session.add(u)
        mod.db.session.flush()
        mod.db.session.add(mod.Enrollment(user_id=u.id, section_id=ids['section']))
        mod.db.session.commit()
        uid = u.id
    c = app.test_client()
    assert c.post('/login', data={'email': 'privacy-temp@lms.local', 'password': 'temp12345'}).status_code in (302, 303)
    c.post('/api/helix/consent', json={'agree': True, 'camera_ok': True, 'passive_ok': True})
    sid = c.post('/api/helix/session/start', json={'lesson_id': ids['lesson'], 'section_id': ids['section'], 'mode': 'gaze',
                                                    'device': 'desktop', 'client_uuid': 'privacy-temp-1'}).get_json()['session_id']
    yield {'id': uid, 'session': sid, 'client': c}
    with app.app_context():   # belt and braces if a test failed before deleting
        u = mod.db.session.get(mod.User, uid)
        if u:
            P.delete_record(mod.db, uid)


def test_privacy_admin_only(anon, student, instructor, admin, temp_student):
    uid = temp_student['id']
    for c in (student, instructor):
        assert c.get('/admin/privacy').status_code in (302, 403)
        assert c.get(f'/admin/privacy/student/{uid}/export.json').status_code in (302, 403)
        assert c.post(f'/admin/privacy/student/{uid}/delete', data={'confirm_email': 'privacy-temp@lms.local'}).status_code in (302, 403)
        assert c.post('/admin/privacy/helix-cleanup').status_code in (302, 403)
    assert anon.get('/admin/privacy').status_code in (302, 401)
    r = admin.get(f'/admin/privacy?q=privacy-temp&user_id={uid}')
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and 'privacy-temp@lms.local' in html and 'helix_gaze_session' in html


def test_privacy_tool_refuses_staff(admin, app, mod):
    with app.app_context():
        inst = mod.User.query.filter_by(email='instructor@lms.local').first().id
    assert admin.get(f'/admin/privacy/student/{inst}/export.json').status_code == 404
    assert admin.post(f'/admin/privacy/student/{inst}/delete', data={'confirm_email': 'instructor@lms.local'}).status_code == 404


def test_export_full_record(admin, app, mod, temp_student):
    uid = temp_student['id']
    r = admin.get(f'/admin/privacy/student/{uid}/export.json')
    assert r.status_code == 200 and 'attachment' in r.headers['Content-Disposition']
    body = r.get_data(as_text=True)
    data = json.loads(body)
    assert 'password_hash' not in body and 'temp12345' not in body
    assert data['tables']['user'][0]['email'] == 'privacy-temp@lms.local'
    assert data['counts']['helix_gaze_session'] >= 1 and data['counts']['helix_consent'] >= 1
    assert data['counts']['enrollment'] == 1
    with app.app_context():
        ev = mod.AuditEvent.query.filter_by(action='student_record_export').order_by(mod.AuditEvent.id.desc()).first()
        assert ev and f'user={uid}' in ev.detail


def test_delete_requires_matching_email(admin, app, mod, temp_student):
    uid = temp_student['id']
    admin.post(f'/admin/privacy/student/{uid}/delete', data={'confirm_email': 'wrong@lms.local'})
    with app.app_context():
        assert mod.db.session.get(mod.User, uid) is not None


def test_delete_removes_everything(admin, app, mod, temp_student):
    uid = temp_student['id']
    r = admin.post(f'/admin/privacy/student/{uid}/delete', data={'confirm_email': 'Privacy-Temp@lms.local'})
    assert r.status_code in (302, 303)
    with app.app_context():
        assert mod.db.session.get(mod.User, uid) is None
        insp = inspect(mod.db.engine)
        left = []
        for t in insp.get_table_names():
            for fk in insp.get_foreign_keys(t):
                if fk['referred_table'] == 'user':
                    for col in fk['constrained_columns']:
                        n = mod.db.session.execute(text(f'select count(*) from "{t}" where "{col}"=:u'), {'u': uid}).scalar()
                        if n:
                            left.append((t, col, n))
        assert left == []
        assert mod.db.session.execute(text('select count(*) from helix_gaze_session where id=:s'), {'s': temp_student['session']}).scalar() == 0
        ev = mod.AuditEvent.query.filter_by(action='student_record_delete').order_by(mod.AuditEvent.id.desc()).first()
        assert ev and f'user={uid}' in ev.detail and 'privacy-temp' not in (ev.detail or '')


def test_retention_cleanup(app, mod, admin, temp_student):
    sid = temp_student['session']
    with app.app_context():
        mod.db.session.execute(text('update helix_gaze_session set started_at=:t where id=:s'),
                               {'t': (P._utcnow() - timedelta(days=400)).strftime('%Y-%m-%d %H:%M:%S.%f'), 's': sid})
        mod.db.session.commit()
        dry = P.helix_cleanup(mod.db, mod._helix_models, 365, dry_run=True)
        assert dry['sessions'] >= 1 and dry['dry_run']
        assert mod.db.session.execute(text('select count(*) from helix_gaze_session where id=:s'), {'s': sid}).scalar() == 1
        assert P.helix_cleanup(mod.db, mod._helix_models, 0)['sessions'] == 0   # 0 = keep
    r = admin.post('/admin/privacy/helix-cleanup')
    assert r.status_code in (302, 303)
    with app.app_context():
        assert mod.db.session.execute(text('select count(*) from helix_gaze_session where id=:s'), {'s': sid}).scalar() == 0
        # consent is kept as the record of what was agreed
        assert mod.db.session.execute(text('select count(*) from helix_consent where user_id=:u'), {'u': temp_student['id']}).scalar() >= 1
        assert mod.AuditEvent.query.filter_by(action='helix_retention_cleanup').count() >= 1


def test_cleanup_cli(app):
    r = app.test_cli_runner().invoke(args=['helix-cleanup', '--dry-run'])
    assert r.exit_code == 0 and 'dry' in r.output.lower()
