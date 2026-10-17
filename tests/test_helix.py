"""Helix API lifecycle, consent, access control, dedupe, dashboards, analytics."""
import json
from types import SimpleNamespace

import pytest

from helix import analytics as A


def _start(client, ids, **kw):
    body = {'lesson_id': ids['lesson'], 'section_id': ids['section'], 'mode': 'gaze', 'device': 'desktop',
            'viewport_w': 1440, 'viewport_h': 900}
    body.update(kw)
    return client.post('/api/helix/session/start', json=body)


def test_config_reports_consent_state(student2, ids):
    r = student2.get(f"/api/helix/config?section_id={ids['section']}").get_json()
    assert r['ok'] and r['enabled'] and r['can_record']
    assert r['consent']['granted'] is False


def test_start_requires_consent(student2, ids):
    r = _start(student2, ids)
    assert r.status_code == 403 and r.get_json()['error'] == 'consent_required'


def test_consent_requires_agree(student2):
    assert student2.post('/api/helix/consent', json={'camera_ok': True}).status_code == 400


def test_full_lifecycle(student, instructor, mod, app, ids):
    assert student.post('/api/helix/consent', json={'agree': True, 'camera_ok': True, 'passive_ok': True}).get_json()['granted']
    r = _start(student, ids, client_uuid='uuid-test-1')
    assert r.status_code == 200
    sid = r.get_json()['session_id']
    # idempotent retry of start with the same client uuid
    again = _start(student, ids, client_uuid='uuid-test-1').get_json()
    assert again['session_id'] == sid and again['resumed']
    cal = student.post(f'/api/helix/session/{sid}/calibrated', json={
        'calibration_points': 9, 'calibration_score': 78, 'validation_error_px': 110, 'validation_precision_px': 40}).get_json()
    assert cal['band'] == 'Good'
    batch0 = {'seq': 0, 'segments': [{'t0': 0, 't1': 4000, 'aoi': 'h0-intro', 'label': 'Intro', 'n': 60, 'conf': .8},
                                     {'t0': 4000, 't1': 6000, 'aoi': '_face_lost', 'label': 'Face not detected'}],
              'buckets': [{'aoi_key': 'h0-intro', 'aoi_label': 'Intro', 'aoi_order': 0, 'dwell_ms': 4000, 'visits': 1},
                          {'aoi_key': '_face_lost', 'aoi_label': 'Face not detected', 'aoi_order': 996, 'dwell_ms': 2000, 'visits': 1}],
              'totals': {'total': 6000, 'attentive': 4000, 'face_lost': 2000},
              'heat': {'cols': 20, 'rows': 60, 'cells': {'5,3': 900, '99,99': 5, 'bad': 1}},
              'layout': [{'key': 'h0-intro', 'label': 'Intro', 'order': 0, 'y0': 0, 'y1': .3}], 'sample_count': 120}
    assert student.post(f'/api/helix/session/{sid}/batch', json=batch0).get_json()['ack'] == 0
    # duplicate (retried) batch is acknowledged but not re-applied
    dup = student.post(f'/api/helix/session/{sid}/batch', json=batch0).get_json()
    assert dup['duplicate'] is True
    # stale cumulative counters never move backwards
    batch1 = {'seq': 1, 'segments': [{'t0': 6000, 't1': 9000, 'aoi': 'h1-body', 'label': 'Body'}],
              'buckets': [{'aoi_key': 'h0-intro', 'aoi_label': 'Intro', 'dwell_ms': 100, 'visits': 1},
                          {'aoi_key': 'h1-body', 'aoi_label': 'Body', 'aoi_order': 1, 'dwell_ms': 3000, 'visits': 1}],
              'totals': {'total': 9000, 'attentive': 7000, 'face_lost': 2000}}
    student.post(f'/api/helix/session/{sid}/batch', json=batch1)
    # final batch via sendBeacon-style text/plain body
    end = student.post(f'/api/helix/session/{sid}/batch', data=json.dumps({'seq': 2, 'end': True, 'segments': []}),
                       content_type='text/plain')
    assert end.get_json()['status'] == 'ended'
    with app.app_context():
        s = mod.HelixGazeSession.query.get(sid)
        assert s.status == 'ended' and s.last_seq == 2 and s.calibration_score == 78
        tl = json.loads(s.timeline_json)
        assert len(tl) == 3, tl
        assert s.attentive_ms == 7000 and s.face_lost_ms == 2000
        heat = json.loads(s.heat_json)
        assert heat['cells'] == {'5,3': 900}
        b = mod.HelixAoiBucket.query.filter_by(session_id=sid, aoi_key='h0-intro').first()
        assert b.dwell_ms == 4000
        assert mod.HelixAoiBucket.query.filter_by(session_id=sid, aoi_key='_face_lost').first().aoi_kind == 'state'
    # instructor sees it
    summary = instructor.get(f"/api/helix/section/{ids['section']}/summary.json").get_json()
    me = [r for r in summary['students'] if r['user_id'] == ids['student1']]
    assert me and me[0]['sessions'] >= 1
    html = instructor.get(f"/instructor/section/{ids['section']}/attention/student/{ids['student1']}").get_data(as_text=True)
    assert 'Intro' in html and 'data-hx-lanes' in html
    lesson_html = instructor.get(f"/instructor/section/{ids['section']}/attention/lesson/{ids['lesson']}").get_data(as_text=True)
    assert 'data-hx-heat' in lesson_html
    # student self-review endpoint
    rv = student.get(f"/api/helix/lesson-summary/{ids['lesson']}").get_json()
    assert 'review' in rv


def test_other_user_cannot_write_session(student, student2, ids):
    student.post('/api/helix/consent', json={'agree': True})
    sid = _start(student, ids).get_json()['session_id']
    assert student2.post(f'/api/helix/session/{sid}/batch', json={'seq': 0}).status_code == 403
    assert student2.post(f'/api/helix/session/{sid}/calibrated', json={}).status_code == 403


def test_not_enrolled_student_refused(outsider, ids):
    outsider.post('/api/helix/consent', json={'agree': True})
    r = _start(outsider, ids)
    assert r.status_code == 403 and r.get_json()['error'] == 'not_enrolled'


def test_consent_scope_respected(student2, ids):
    student2.post('/api/helix/consent', json={'agree': True, 'camera_ok': False, 'passive_ok': True})
    assert _start(student2, ids, mode='gaze').get_json()['error'] == 'consent_scope'
    r = _start(student2, ids, mode='passive', device='mobile')
    assert r.status_code == 200
    student2.delete('/api/helix/consent')
    assert _start(student2, ids, mode='passive').status_code == 403


def test_section_switch_disables_helix(instructor, student, ids):
    s = ids['section']
    instructor.post(f'/instructor/section/{s}/attention/settings', data={'passive_enabled': '1', 'min_accuracy': '50'})
    assert student.get(f'/api/helix/config?section_id={s}').get_json()['enabled'] is False
    student.post('/api/helix/consent', json={'agree': True})
    assert _start(student, ids).get_json()['error'] == 'disabled_for_section'
    instructor.post(f'/instructor/section/{s}/attention/settings', data={'enabled': '1', 'passive_enabled': '1', 'min_accuracy': '45'})
    assert student.get(f'/api/helix/config?section_id={s}').get_json()['enabled'] is True


def test_student_can_delete_own_data(student, app, mod, ids):
    student.post('/api/helix/consent', json={'agree': True})
    sid = _start(student, ids).get_json()['session_id']
    student.post('/student/attention/delete', data={'session_id': sid})
    with app.app_context():
        assert mod.HelixGazeSession.query.get(sid) is None


def test_dashboard_marks_demo_data(instructor, ids):
    html = instructor.get(f"/instructor/section/{ids['section']}/attention").get_data(as_text=True)
    assert 'Includes demo seed data' in html
    assert 'Student × heading heatmap' in html


# ---------------------------------------------------------------- pure analytics
def _sess(**kw):
    base = dict(user_id=1, lesson_id=1, mode='gaze', calibration_score=80, recalibrations=0, started_at=None,
                total_ms=0, attentive_ms=0, off_page_ms=0, face_lost_ms=0, hidden_ms=0, low_conf_ms=0,
                timeline_json='[]', heat_json='{}', layout_json='[]', is_demo=False, id=1)
    base.update(kw)
    return SimpleNamespace(**base)


def test_breakdown_falls_back_to_timeline():
    s = _sess(timeline_json=json.dumps([{'t0': 0, 't1': 1000, 'aoi': 'h0'}, {'t0': 1000, 't1': 1500, 'aoi': '_hidden'},
                                        {'t0': 1500, 't1': 2000, 'aoi': 'off_page'}]))
    b = A.session_breakdown(s)
    assert b == {'attentive': 1000, 'off_page': 500, 'face_lost': 0, 'hidden': 500, 'low_conf': 0, 'total': 2000}


def test_student_summary_flags():
    users = {1: SimpleNamespace(full_name='Ana', email='a@x')}
    rows, missing = A.student_summaries([_sess(total_ms=1000, attentive_ms=500, face_lost_ms=400, hidden_ms=100,
                                               calibration_score=30)], users, enrolled_ids=[1, 2])
    r = rows[0]
    assert r['attentive_pct'] == 50 and r['face_lost_pct'] == 40
    assert 'Camera often lost the face' in r['flags'] and 'Low calibration accuracy' in r['flags']
    assert missing == [2]


def test_aoi_rollup_thin_and_excludes_states():
    B = lambda k, l, ms, u=1, o=0: SimpleNamespace(aoi_key=k, aoi_label=l, dwell_ms=ms, visits=1, user_id=u, aoi_order=o, aoi_kind='heading')
    rows, total = A.aoi_rollup([B('a', 'A', 10000), B('b', 'B', 9000), B('c', 'C', 1000), B('_hidden', 'Tab hidden / app switched', 50000)])
    assert total == 20000
    thin = {r['label']: r['thin'] for r in rows}
    assert thin == {'A': False, 'B': False, 'C': True}


def test_matrix_rows_normalised():
    B = lambda u, l, ms, o: SimpleNamespace(aoi_key=l, aoi_label=l, dwell_ms=ms, visits=1, user_id=u, aoi_order=o)
    m = A.aoi_matrix([B(1, 'A', 300, 0), B(1, 'B', 100, 1), B(2, 'A', 100, 0), B(2, 'B', 100, 1)],
                     {1: SimpleNamespace(full_name='X'), 2: SimpleNamespace(full_name='Y')})
    assert m['labels'] == ['A', 'B']
    assert [c['share'] for c in m['rows'][0]['cells']] == [75, 25]
    assert m['means'] == [62, 38]


def test_clean_segments_caps_and_sanitises():
    segs = A.clean_segments([{'t0': -5, 't1': 999999, 'aoi': 'x' * 200, 'conf': 7}, 'junk', {'t0': 'a'}])
    assert segs[0]['t0'] == 0 and segs[0]['t1'] == A.MAX_SEGMENT_MS and len(segs[0]['aoi']) == 80 and segs[0]['conf'] == 1.0
    assert len(segs) == 2


def test_accuracy_bands():
    assert A.accuracy_band(75)['label'] == 'Good'
    assert A.accuracy_band(50)['label'] == 'Fair'
    assert A.accuracy_band(20)['label'] == 'Poor'
    assert A.accuracy_band(0, 'passive')['label'] == 'Passive'


def test_try_page_is_public_and_self_hosted(app):
    r = app.test_client().get('/helix/try')
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'vendor/mediapipe/vision_bundle.mjs' in html and 'face_landmarker.task' in html
    assert 'helix-engine.js' in html and 'helix-calib.js' in html
    assert 'Nothing is uploaded' in html


def test_mediapipe_assets_are_vendored(app):
    import os
    root = os.path.join(app.root_path, 'static', 'vendor', 'mediapipe')
    for rel in ('vision_bundle.mjs', 'wasm/vision_wasm_internal.wasm', 'wasm/vision_wasm_internal.js',
                'wasm/vision_wasm_nosimd_internal.wasm', 'models/face_landmarker.task'):
        assert os.path.getsize(os.path.join(root, rel)) > 1000, rel


def test_engine_metadata_stored_and_clamped(student, instructor, app, ids):
    student.post('/api/helix/consent', json={'agree': True, 'camera_ok': True, 'passive_ok': True})
    sid = _start(student, ids, client_uuid='uuid-mp-1').get_json()['session_id']
    r = student.post(f'/api/helix/session/{sid}/calibrated', json={
        'calibration_points': 9, 'calibration_score': 71, 'validation_error_px': 64, 'validation_precision_px': 30,
        'engine': 'mediapipe', 'delegate': 'GPU', 'validation_error_deg': 1.7, 'distance_cm': 52,
        'aoi_resolution': 'paragraph', 'orientation': 'landscape'})
    assert r.get_json()['ok']
    drift = [{'t': 1000 * i, 'err': 40 + i, 'med': 45, 'src': 'click'} for i in range(5)] + [{'t': 9000, 'src': 'recal'}]
    r = student.post(f'/api/helix/session/{sid}/batch', json={
        'seq': 0, 'segments': [], 'buckets': [], 'implicit_samples': 5, 'drift': drift,
        'aoi_resolution': 'bogus', 'validation_error_deg': 500, 'engine': 'evil<script>',
        'fine': [{'key': 'h0-intro~p1', 'label': 'Intro > first para', 'kind': 'paragraph', 'dwell_ms': 3200}]})
    assert r.get_json()['ok']
    with app.app_context():
        from app import db
        from sqlalchemy import text
        row = db.session.execute(text('select engine, delegate, validation_error_deg, distance_cm, aoi_resolution, '
                                      'implicit_samples, drift_json, fine_json from helix_gaze_session where id=:i'), {'i': sid}).mappings().first()
    assert row['engine'] == 'mediapipe' and row['delegate'] == 'GPU'
    assert row['validation_error_deg'] == 90.0          # clamped
    assert row['distance_cm'] == 52 and row['aoi_resolution'] == 'paragraph'   # bogus value ignored
    assert row['implicit_samples'] == 5
    assert json.loads(row['drift_json'])[-1] == {'t': 9000, 'src': 'recal'}
    assert json.loads(row['fine_json'])[0]['dwell_ms'] == 3200


def test_drift_svg_renders_and_escapes():
    pts = [{'t': i, 'err': 50 + 10 * i, 'med': 60, 'src': 'tap'} for i in range(6)] + [{'t': 7, 'src': 'recal'}, {'t': 8, 'err': 30, 'med': 30, 'src': '<b>'}]
    svg = str(A.drift_svg(json.dumps(pts)))
    assert svg.startswith('<svg') and 'stroke-dasharray' in svg and '<b>' not in svg
    assert A.drift_svg('[]') == '' and A.drift_svg('not json') == ''
    assert A.median_or_none([3, None, 1, 2]) == 2 and A.median_or_none([]) is None
