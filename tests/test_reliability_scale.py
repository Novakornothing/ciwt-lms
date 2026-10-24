"""Reliability at pilot scale: 60 students in 3 sections with ladder states, gates, lab events, LTI passback + NRPS,
then timing of the busiest instructor/student pages; plus hosting config vs docs/PRODUCTION_HOSTING.md."""
import json
import os
import pathlib
import random
import subprocess
import sys
import time

import pytest

from tests.test_lti import ensure_learner_launched, env  # noqa: F401

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIMIT = 1.5


@pytest.fixture(scope='module')
def big(app, mod):
    rnd = random.Random(7)
    lm = mod.mastery_api.ladder.models
    labs = app.extensions['ciwt_lab_progress']
    with app.app_context():
        c = mod.Course.query.filter_by(code='ITSUP').first()
        teacher = mod.User.query.filter_by(email='instructor@lms.local').first()
        les = next(l for mm in mod.Module.query.filter_by(course_id=c.id, order=1) for l in mod.Lesson.query.filter_by(module_id=mm.id) if l.title.startswith('1.1 '))
        secs, users = [], []
        for k in range(3):
            s = mod.ClassSection(name=f'Scale pilot {k + 1}', course_id=c.id, instructor_id=teacher.id, is_active=True)
            mod.db.session.add(s); mod.db.session.flush(); secs.append(s.id)
            mod.db.session.add(mod.ContentRelease(section_id=s.id, content_type='module', content_id=les.module_id, user_id=None, is_active=True))
            for i in range(20):
                u = mod.User(email=f'scale{k}-{i}@pilot.test', first_name=f'P{k}{i}', last_name='Scale', role='student')
                u.set_password('pw-scale-123'); mod.db.session.add(u); mod.db.session.flush()
                mod.db.session.add(mod.Enrollment(user_id=u.id, section_id=s.id)); users.append((s.id, u.id))
                for j, sid in enumerate(('1-what-a-computer-is-in-one-picture', '2-three-kinds-of-work', '3-impact-and-identity')):
                    roll = rnd.random()
                    tried = ['R0'] + (['R1', 'R2'][:rnd.randint(0, 2)] if roll < .5 else [])
                    mod.db.session.add(lm.LadderState(user_id=u.id, section_id=s.id, course='ITSUP', label='1.1', sid=sid, lesson_id=les.id,
                                                      current=tried[-1], tried_json=json.dumps(tried), misses=len(tried) - 1, requests=0,
                                                      resolved=tried[-1] if roll < .8 else None,
                                                      exhausted_at=mod.utcnow() if roll > .95 else None))
                mod.db.session.add(labs.LabProgress(user_id=u.id, lab_id='win-dns-break', actions=8, score=80, best_score=80,
                                                    completed_at=mod.utcnow() if rnd.random() < .6 else None))
        lid, mid = les.id, les.module_id
        mod.db.session.commit()
    yield {'sections': secs, 'users': users, 'lesson': lid, 'module': mid}
    with app.app_context():
        ids = [u for _, u in users]
        lm.LadderState.query.filter(lm.LadderState.user_id.in_(ids)).delete(synchronize_session=False)
        labs.LabProgress.query.filter(labs.LabProgress.user_id.in_(ids)).delete(synchronize_session=False)
        mod.Enrollment.query.filter(mod.Enrollment.user_id.in_(ids)).delete(synchronize_session=False)
        mod.db.session.commit()


def timed(client, url, method='get', **kw):
    t = time.perf_counter()
    r = getattr(client, method)(url, **kw)
    return r, time.perf_counter() - t


def test_scale_pages_stay_fast(app, mod, big, instructor):
    s1 = big['sections'][0]
    for url in ('/instructor/sections', f'/instructor/section/{s1}', f'/instructor/section/{s1}/mastery/today',
                f'/instructor/section/{s1}/roster', f'/instructor/section/{s1}/ladder', f'/instructor/section/{s1}/outcomes?format=csv',
                f'/instructor/section/{s1}/outcomes?format=json', f'/instructor/section/{s1}/setup'):
        r, dt = timed(instructor, url)
        assert r.status_code == 200, url
        assert dt < LIMIT, f'{url} took {dt:.2f}s'
    h = instructor.get('/instructor/sections').get_data(as_text=True)
    assert all(f'Scale pilot {k}' in h for k in (1, 2, 3))
    j = instructor.get(f'/instructor/section/{s1}/outcomes?format=json').get_json()
    assert j['students'] == 20


def test_gate_for_every_student_is_fast(app, mod, big):
    lad = mod.mastery_api.ladder
    with app.test_request_context():
        les = mod.db.session.get(mod.Lesson, big['lesson'])
        t = time.perf_counter()
        n_blocked = 0
        for sid, uid in big['users']:
            g = lad.gate(mod.db.session.get(mod.User, uid), mod.db.session.get(mod.ClassSection, sid), les)
            n_blocked += g['blocked']
        dt = time.perf_counter() - t
    assert 0 < n_blocked <= 60 and dt < LIMIT * 2, f'60 gates {dt:.2f}s'


def test_student_gate_route_and_advance(app, mod, big):
    sid, uid = big['users'][0]
    c = app.test_client()
    with app.app_context():
        email = mod.db.session.get(mod.User, uid).email
    c.post('/login', data={'email': email, 'password': 'pw-scale-123'})
    r, dt = timed(c, f'/student/section/{sid}/ladder/{big["lesson"]}/gate')
    assert r.status_code == 200 and dt < LIMIT
    r, dt = timed(c, f'/student/module/{sid}/{big["module"]}/lesson/{big["lesson"]}')
    assert r.status_code == 200 and dt < LIMIT


def test_transfer_between_scale_sections(app, mod, big, instructor):
    a, b = big['sections'][:2]
    sid, uid = next(x for x in big['users'] if x[0] == a)
    r, dt = timed(instructor, f'/instructor/section/{a}/roster', 'post', data={'action': 'transfer', 'user_id': uid, 'to': b})
    assert r.status_code == 303 and dt < LIMIT
    with app.app_context():
        assert mod.Enrollment.query.filter_by(user_id=uid, section_id=b).first()


def test_lti_passback_and_roster_at_scale(app, mod, env, instructor):
    ensure_learner_launched(app, env)
    r, dt = timed(instructor, '/instructor/section/1/lti/scores', 'post')
    assert r.status_code == 303 and dt < LIMIT * 2
    r, dt = timed(instructor, '/instructor/section/1/lti/roster', 'post')
    assert r.status_code == 303 and dt < LIMIT * 2
    with app.app_context():
        logs = env['m'].LtiSyncLog.query.order_by(env['m'].LtiSyncLog.id.desc()).limit(2).all()
        assert all(lg.failed == 0 for lg in logs)


# ---------------------------------------------------------------- hosting config matches docs
def test_hosting_config_matches_docs(anon, tmp_path):
    doc = (ROOT / 'docs' / 'PRODUCTION_HOSTING.md').read_text()
    render, docker, compose = ((ROOT / f).read_text() for f in ('render.yaml', 'Dockerfile', 'docker-compose.yml'))
    for s in ('/var/data/ciwt/ciwt_lms.db', 'CIWT_INSTANCE_DIR', '/healthz', 'tools/backup_db.py', '--restore-check'):
        assert s in doc
    assert 'healthCheckPath: /healthz' in render and 'mountPath: /var/data' in render and 'sqlite:////var/data/ciwt/ciwt_lms.db' in render
    assert 'CIWT_SQLITE_WAL' in render and 'CIWT_INSTANCE_DIR' in render and 'SECRET_KEY' in render
    assert '/healthz' in docker and 'EXPOSE 8000' in docker and '/var/data/ciwt' in docker
    assert 'ciwt-data' in compose and '/var/data/ciwt' in compose and '8000' in compose
    j = anon.get('/healthz')
    assert j.status_code == 200 and j.get_json()['database'] == 'ok'


def test_backup_and_restore_check(tmp_path):
    url = os.environ['DATABASE_URL']
    out = subprocess.run([sys.executable, str(ROOT / 'tools' / 'backup_db.py'), '--url', url, '--dest', str(tmp_path)],
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    gz = sorted(tmp_path.glob('*.db.gz'))
    assert gz
    chk = subprocess.run([sys.executable, str(ROOT / 'tools' / 'backup_db.py'), '--restore-check', str(gz[-1])],
                         capture_output=True, text=True, timeout=120)
    assert chk.returncode == 0, chk.stderr
