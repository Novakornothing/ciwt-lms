"""Helix blueprint: consent, session lifecycle API, dashboards, exports."""
import csv
import json
import re
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from io import StringIO

from flask import (Blueprint, Response, abort, current_app, flash, jsonify, make_response, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from . import analytics as A
from .models import ENGINE, NON_READING_KEYS, POLICY_VERSION, STATE_KEYS



PAYLOAD_MAX_BYTES = 256 * 1024
MEDIA_KEYS = {'frame', 'frames', 'image', 'images', 'img', 'video', 'snapshot', 'jpeg', 'jpg', 'png', 'webp',
              'pixels', 'imagedata', 'blob', 'landmarks', 'facelandmarks', 'mesh', 'iris'}
_B64 = re.compile(r'^[A-Za-z0-9+/=_-]{2000,}$')


def looks_like_media(obj, depth=0):
    """True if a JSON payload carries anything resembling camera frames or face geometry."""
    if depth > 6:
        return False
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower().replace('_', '').replace('-', '') in MEDIA_KEYS:
                return True
            if looks_like_media(v, depth + 1):
                return True
    elif isinstance(obj, list):
        return any(looks_like_media(v, depth + 1) for v in obj[:2000])
    elif isinstance(obj, str):
        low = obj[:16].lower()
        if low.startswith('data:image') or low.startswith('data:video') or low.startswith('blob:'):
            return True
        if len(obj) >= 2000 and _B64.match(obj[:5000]):
            return True
    return False

def utcnow():
    """Naive UTC now. Replaces the deprecated datetime.utcnow(); stored columns stay naive UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

STALE_AFTER = timedelta(minutes=10)

# Upload endpoints are exempt from CSRFProtect's header/form check because
# navigator.sendBeacon cannot set headers; they validate the token themselves
# from the X-CSRFToken header *or* a `_csrf` field in the JSON body.
BEACON_VIEWS = ('session_batch', 'session_timeline', 'session_end', 'beat')


def beacon_csrf_ok(data):
    if not current_app.config.get('WTF_CSRF_ENABLED', True) or 'csrf' not in current_app.extensions:
        return True
    from flask_wtf.csrf import validate_csrf
    from wtforms.validators import ValidationError
    token = request.headers.get('X-CSRFToken') or request.headers.get('X-CSRF-Token') or (data or {}).get('_csrf')
    try:
        validate_csrf(token)
        return True
    except ValidationError:
        return False


def create_blueprint(d, m):
    """d: app dependencies namespace; m: Helix models namespace."""
    bp = Blueprint('helix', __name__)

    @bp.app_template_global('hx_drift_svg')
    def hx_drift_svg(drift_json):
        return A.drift_svg(drift_json)
    db = d.db
    Session, Bucket, Consent, Setting, Event = (
        m.HelixGazeSession, m.HelixAoiBucket, m.HelixConsent, m.HelixSectionSetting, m.HelixAttentionEvent)

    # ------------------------------------------------------------ helpers
    def active_consent(user_id):
        return (Consent.query.filter_by(user_id=user_id, revoked_at=None)
                .order_by(Consent.granted_at.desc()).first())

    def consent_current(c):
        return bool(c and c.policy_version == POLICY_VERSION)

    def section_setting(section_id):
        if not section_id:
            return None
        return Setting.query.filter_by(section_id=section_id).first()

    def section_enabled(section_id):
        s = section_setting(section_id)
        return (True, True, 45) if s is None else (bool(s.enabled), bool(s.passive_enabled), s.min_accuracy or 45)

    def can_record(section_id):
        """Students: must be enrolled. Staff may preview (data kept, flagged by role)."""
        if not section_id:
            return current_user.role in ('admin', 'instructor')
        if current_user.role in ('admin', 'instructor'):
            return True
        return d.Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first() is not None

    def owned_session(session_id):
        sess = db.get_or_404(Session, session_id)
        if sess.user_id != current_user.id:
            abort(403)
        return sess

    def staff_section_or_403(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role == 'admin':
            return section
        if current_user.role != 'instructor' or not d.can_access_section(current_user, section):
            abort(403)
        return section

    @bp.before_request
    def _refuse_media_uploads():
        # runs before auth/session lookups so the refusal does not depend on route order
        if request.method in ('POST', 'PUT', 'PATCH') and request.path.startswith('/api/helix/'):
            if (request.content_length or 0) > PAYLOAD_MAX_BYTES:
                return jsonify(ok=False, error='payload_too_large'), 413
            if looks_like_media(request.get_json(force=True, silent=True) or {}):
                return jsonify(ok=False, error='media_not_accepted'), 400
        return None

    def payload():
        # sendBeacon posts with a Blob; accept JSON regardless of content-type.
        # Privacy guard: Helix only ever uploads gaze-derived numbers (AOI dwell, segments, a
        # coarse heat grid, quality stats). Anything that looks like camera data -- image/video
        # fields, data: URLs, long base64 blobs, raw landmarks -- is refused outright, even from
        # a modified client, and so are oversized bodies.
        if (request.content_length or 0) > PAYLOAD_MAX_BYTES:
            abort(make_response(jsonify(ok=False, error='payload_too_large'), 413))
        data = request.get_json(force=True, silent=True) or {}
        if looks_like_media(data):
            abort(make_response(jsonify(ok=False, error='media_not_accepted'), 400))
        return data

    def mark_stale(sessions):
        cutoff = utcnow() - STALE_AFTER
        changed = False
        for s in sessions:
            if s.status == 'running':
                seen = s.last_seen_at or s.started_at
                if seen and seen < cutoff:
                    s.status = 'abandoned'
                    s.ended_at = s.ended_at or seen
                    changed = True
        if changed:
            db.session.commit()

    def valid_lesson_ids(ids):
        ids = [i for i in ids if i]
        if not ids:
            return {}
        return {L.id: L for L in d.Lesson.query.filter(d.Lesson.id.in_(ids)).all()}

    def users_by_id(ids):
        ids = list(ids) or [0]
        return {u.id: u for u in d.User.query.filter(d.User.id.in_(ids)).all()}

    def enrolled_ids(section):
        return [e.user_id for e in d.Enrollment.query.filter_by(section_id=section.id).all()]

    # ------------------------------------------------------------ API: config + consent
    @bp.route('/api/helix/config')
    @login_required
    def api_config():
        section_id = request.args.get('section_id', type=int)
        enabled, passive, min_acc = section_enabled(section_id)
        c = active_consent(current_user.id)
        return jsonify({
            'ok': True,
            'enabled': enabled,
            'passive_enabled': passive,
            'min_accuracy': min_acc,
            'policy_version': POLICY_VERSION,
            'engine': ENGINE,
            'consent': {
                'granted': consent_current(c),
                'stale': bool(c) and not consent_current(c),
                'camera_ok': bool(c and c.camera_ok),
                'passive_ok': bool(c and c.passive_ok),
                'granted_at': c.granted_at.isoformat() + 'Z' if c else None,
            },
            'can_record': can_record(section_id),
        })

    def grant(camera_ok, passive_ok):
        for old in Consent.query.filter_by(user_id=current_user.id, revoked_at=None).all():
            old.revoked_at = utcnow()
        c = Consent(user_id=current_user.id, policy_version=POLICY_VERSION,
                    camera_ok=bool(camera_ok), passive_ok=bool(passive_ok))
        db.session.add(c)
        db.session.commit()
        d.audit('helix_consent_grant', f'camera={c.camera_ok} passive={c.passive_ok} v={POLICY_VERSION}')
        return c

    def revoke():
        n = 0
        for old in Consent.query.filter_by(user_id=current_user.id, revoked_at=None).all():
            old.revoked_at = utcnow()
            n += 1
        for s in Session.query.filter_by(user_id=current_user.id, status='running').all():
            s.status = 'ended'
            s.ended_at = utcnow()
        db.session.commit()
        d.audit('helix_consent_revoke', f'rows={n}')
        return n

    @bp.route('/api/helix/consent', methods=['POST', 'DELETE'])
    @login_required
    def api_consent():
        if request.method == 'DELETE':
            revoke()
            return jsonify({'ok': True, 'granted': False})
        data = payload()
        if not data.get('agree'):
            return jsonify({'ok': False, 'error': 'agree_required'}), 400
        c = grant(data.get('camera_ok', True), data.get('passive_ok', True))
        return jsonify({'ok': True, 'granted': True, 'policy_version': c.policy_version})

    # ------------------------------------------------------------ API: session lifecycle
    @bp.route('/api/helix/session/start', methods=['POST'])
    @login_required
    def session_start():
        data = payload()
        if not beacon_csrf_ok(data):
            return jsonify({'ok': False, 'error': 'csrf'}), 400
        lesson_id = data.get('lesson_id')
        if not lesson_id:
            return jsonify({'ok': False, 'error': 'lesson required'}), 400
        lesson = db.session.get(d.Lesson, A._int(lesson_id))
        if not lesson:
            return jsonify({'ok': False, 'error': 'lesson not found'}), 404
        section_id = A._int(data.get('section_id')) or None
        if section_id and not db.session.get(d.ClassSection, section_id):
            section_id = None
        if not can_record(section_id):
            return jsonify({'ok': False, 'error': 'not_enrolled'}), 403
        enabled, passive_enabled, _ = section_enabled(section_id)
        mode = 'passive' if data.get('mode') == 'passive' else 'gaze'
        if not enabled or (mode == 'passive' and not passive_enabled):
            return jsonify({'ok': False, 'error': 'disabled_for_section'}), 403
        c = active_consent(current_user.id)
        if not consent_current(c):
            return jsonify({'ok': False, 'error': 'consent_required', 'policy_version': POLICY_VERSION}), 403
        if (mode == 'gaze' and not c.camera_ok) or (mode == 'passive' and not c.passive_ok):
            return jsonify({'ok': False, 'error': 'consent_scope'}), 403
        uuid = str(data.get('client_uuid') or '')[:40] or None
        if uuid:
            existing = Session.query.filter_by(client_uuid=uuid, user_id=current_user.id).first()
            if existing:  # idempotent retry of a start call
                return jsonify({'ok': True, 'session_id': existing.id, 'resumed': True,
                                'last_seq': existing.last_seq, 'policy': POLICY_VERSION})
        device = str(data.get('device') or 'desktop')[:12]
        if device not in ('desktop', 'tablet', 'mobile'):
            device = 'desktop'
        sess = Session(
            user_id=current_user.id, section_id=section_id, lesson_id=lesson.id,
            engine=ENGINE if mode == 'gaze' else 'passive', consent_version=POLICY_VERSION,
            viewport_w=A._int(data.get('viewport_w'), hi=10000), viewport_h=A._int(data.get('viewport_h'), hi=10000),
            timeline_json='[]', heat_json='{}', layout_json='[]', status='running',
            client_uuid=uuid, mode=mode, device=device, last_seq=-1, last_seen_at=utcnow(),
        )
        db.session.add(sess)
        db.session.commit()
        d.audit('helix_session_start', f'lesson={lesson.id} session={sess.id} mode={mode} device={device}')
        return jsonify({'ok': True, 'session_id': sess.id, 'engine': sess.engine, 'policy': POLICY_VERSION,
                        'last_seq': -1})

    @bp.route('/api/helix/session/<int:session_id>/calibrated', methods=['POST'])
    @login_required
    def session_calibrated(session_id):
        sess = owned_session(session_id)
        data = payload()
        sess.calibration_points = A._int(data.get('calibration_points'), lo=0, hi=64)
        sess.calibration_score = A._int(data.get('calibration_score'), lo=0, hi=100)
        sess.validation_error_px = A._int(data.get('validation_error_px'), lo=0, hi=10000)
        sess.validation_precision_px = A._int(data.get('validation_precision_px'), lo=0, hi=10000)
        if data.get('recalibration'):
            sess.recalibrations = (sess.recalibrations or 0) + 1
        apply_engine_meta(sess, data)
        sess.last_seen_at = utcnow()
        db.session.commit()
        band = A.accuracy_band(sess.calibration_score)
        return jsonify({'ok': True, 'band': band['label']})

    def aggregated_buckets(section_id, lesson_id=None):
        """AOI dwell summed in SQL per (lesson, student, AOI); rows quack like Bucket for analytics."""
        from sqlalchemy import func
        q = (db.session.query(Bucket.lesson_id, Bucket.user_id, Bucket.aoi_key, Bucket.aoi_label, Bucket.aoi_kind,
                              func.min(Bucket.aoi_order), func.sum(Bucket.dwell_ms), func.sum(Bucket.visits))
             .filter(Bucket.section_id == section_id))
        if lesson_id is not None:
            q = q.filter(Bucket.lesson_id == lesson_id)
        q = q.group_by(Bucket.lesson_id, Bucket.user_id, Bucket.aoi_key, Bucket.aoi_label, Bucket.aoi_kind)
        return [SimpleNamespace(lesson_id=r[0], user_id=r[1], aoi_key=r[2], aoi_label=r[3], aoi_kind=r[4],
                                aoi_order=r[5] or 0, dwell_ms=int(r[6] or 0), visits=int(r[7] or 0))
                for r in q.all()]

    ENGINES = ('mediapipe', 'webgazer', 'passive')
    RESOLUTIONS = ('heading', 'paragraph', 'line')

    def apply_engine_meta(sess, data):
        """Camera-pipeline metadata sent with calibration results and batches (all optional, clamped)."""
        eng = str(data.get('engine') or '')
        if eng in ENGINES:
            sess.engine = eng
        if data.get('delegate'):
            sess.delegate = str(data.get('delegate'))[:40]
        if data.get('validation_error_deg') is not None:
            try:
                sess.validation_error_deg = round(max(0.0, min(90.0, float(data.get('validation_error_deg')))), 2)
            except (TypeError, ValueError):
                pass
        if data.get('distance_cm') is not None:
            sess.distance_cm = A._int(data.get('distance_cm'), lo=0, hi=300)
        if data.get('aoi_resolution') in RESOLUTIONS:
            sess.aoi_resolution = data.get('aoi_resolution')
        if data.get('orientation') in ('portrait', 'landscape'):
            sess.orientation = data.get('orientation')
        if data.get('implicit_samples') is not None:
            sess.implicit_samples = A._int(data.get('implicit_samples'), lo=0, hi=100000)
        drift = data.get('drift')
        if isinstance(drift, list):
            pts = []
            for d in drift[-120:]:
                if isinstance(d, dict) and d.get('src') == 'recal':
                    pts.append({'t': A._int(d.get('t'), lo=0, hi=24 * 3_600_000), 'src': 'recal'})
                elif isinstance(d, dict):
                    pts.append({'t': A._int(d.get('t'), lo=0, hi=24 * 3_600_000),
                                'err': A._int(d.get('err'), lo=0, hi=10000),
                                'med': A._int(d.get('med'), lo=0, hi=10000),
                                'src': str(d.get('src') or '')[:12]})
            sess.drift_json = json.dumps(pts)
        fine = data.get('fine')
        if isinstance(fine, list):
            rows = []
            for f in fine[:150]:
                if isinstance(f, dict) and f.get('key'):
                    rows.append({'key': str(f.get('key'))[:100], 'label': str(f.get('label') or '')[:160],
                                 'kind': 'line' if f.get('kind') == 'line' else 'paragraph',
                                 'dwell_ms': A._int(f.get('dwell_ms'), lo=0, hi=3_600_000)})
            sess.fine_json = json.dumps(rows)

    def apply_batch(sess, data, legacy=False):
        seq = data.get('seq')
        if seq is not None and not legacy:
            seq = A._int(seq, -1)
            if seq <= (sess.last_seq if sess.last_seq is not None else -1):
                return {'ok': True, 'duplicate': True, 'ack': sess.last_seq}
            sess.last_seq = seq
        if sess.status != 'running' and not legacy:
            # late batch after end/abandon: still accept data, keep ended state
            pass
        sess.timeline_json = A.merge_timeline(sess.timeline_json, data.get('segments') or [])
        sess.sample_count = max(sess.sample_count or 0, A._int(data.get('sample_count'), lo=0))
        sess.rejected_samples = max(sess.rejected_samples or 0, A._int(data.get('rejected'), lo=0))
        if data.get('viewport_w'):
            sess.viewport_w = A._int(data.get('viewport_w'), hi=10000)
            sess.viewport_h = A._int(data.get('viewport_h'), hi=10000)
        totals = data.get('totals')
        if isinstance(totals, dict):
            for field, key in (('total_ms', 'total'), ('attentive_ms', 'attentive'),
                               ('off_page_ms', 'off_page'), ('face_lost_ms', 'face_lost'),
                               ('hidden_ms', 'hidden'), ('low_conf_ms', 'low_conf')):
                setattr(sess, field, A._int(totals.get(key), lo=0, hi=24 * 3_600_000))
        apply_engine_meta(sess, data)
        heat = A.clean_heat(data.get('heat'))
        if heat is not None:
            sess.heat_json = json.dumps(heat)
        if data.get('layout'):
            sess.layout_json = json.dumps(A.clean_layout(data.get('layout')))
        for b in (data.get('buckets') or [])[:200]:
            if not isinstance(b, dict):
                continue
            key = str(b.get('aoi_key') or b.get('aoi') or '')[:80]
            if not key:
                continue
            row = Bucket.query.filter_by(session_id=sess.id, aoi_key=key).first()
            if not row:
                row = Bucket(session_id=sess.id, user_id=sess.user_id, section_id=sess.section_id,
                             lesson_id=sess.lesson_id, aoi_key=key)
                db.session.add(row)
            row.aoi_label = str(b.get('aoi_label') or b.get('label') or STATE_KEYS.get(key) or key)[:240]
            row.aoi_order = A._int(b.get('aoi_order'), lo=0, hi=999)
            row.aoi_kind = str(b.get('aoi_kind') or ('state' if key in NON_READING_KEYS else 'heading'))[:20]
            # cumulative counters: never let a stale retry move them backwards
            row.dwell_ms = max(row.dwell_ms or 0, A._int(b.get('dwell_ms'), lo=0, hi=3_600_000))
            row.visits = max(row.visits or 0, A._int(b.get('visits'), lo=0, hi=10_000))
            row.first_ms = A._int(b.get('first_ms'), lo=0)
            row.last_ms = A._int(b.get('last_ms'), lo=0)
            row.updated_at = utcnow()
        sess.last_seen_at = utcnow()
        if data.get('end'):
            sess.status = 'ended'
            sess.ended_at = utcnow()
        elif sess.status == 'abandoned':
            sess.status = 'running'  # client came back (e.g. laptop woke up)
        db.session.commit()
        return {'ok': True, 'ack': sess.last_seq, 'status': sess.status}

    @bp.route('/api/helix/session/<int:session_id>/batch', methods=['POST'])
    @login_required
    def session_batch(session_id):
        sess = owned_session(session_id)
        data = payload()
        if not beacon_csrf_ok(data):
            return jsonify({'ok': False, 'error': 'csrf'}), 400
        return jsonify(apply_batch(sess, data))

    @bp.route('/api/helix/session/<int:session_id>/timeline', methods=['POST'])
    @login_required
    def session_timeline(session_id):
        """Legacy (v1 client) endpoint: unsequenced timeline append."""
        sess = owned_session(session_id)
        data = payload()
        if not beacon_csrf_ok(data):
            return jsonify({'ok': False, 'error': 'csrf'}), 400
        return jsonify(apply_batch(sess, data, legacy=True))

    @bp.route('/api/helix/session/<int:session_id>/end', methods=['POST'])
    @login_required
    def session_end(session_id):
        sess = owned_session(session_id)
        data = payload()
        if not beacon_csrf_ok(data):
            return jsonify({'ok': False, 'error': 'csrf'}), 400
        data['end'] = True
        return jsonify(apply_batch(sess, data))

    @bp.route('/api/helix/beat', methods=['POST'])
    @login_required
    def beat():
        data = payload()
        lesson_id = data.get('lesson_id')
        if not lesson_id:
            return jsonify({'ok': False}), 400
        try:
            seconds = min(30.0, max(0.0, float(data.get('seconds') or 0)))
            focused = min(seconds, max(0.0, float(data.get('focused') or 0)))
        except (TypeError, ValueError):
            return jsonify({'ok': False}), 400
        db.session.add(Event(user_id=current_user.id, section_id=A._int(data.get('section_id')) or None,
                             lesson_id=A._int(lesson_id), heading=str(data.get('heading') or 'Lesson')[:240],
                             seconds=seconds, focused=focused))
        db.session.commit()
        return jsonify({'ok': True})

    @bp.route('/api/helix/lesson-summary/<int:lesson_id>')
    @login_required
    def lesson_summary(lesson_id):
        """Student self-review: headings with thin dwell on their own sessions."""
        buckets = Bucket.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).all()
        rows, total = A.aoi_rollup(buckets)
        review = [{'heading': r['label'], 'aoi_label': r['label'], 'seconds': r['seconds'],
                   'dwell_ms': r['dwell_ms'], 'focus': r['share'], 'key': r['key']}
                  for r in rows if r['thin']]
        review.sort(key=lambda x: x['dwell_ms'])
        sessions = Session.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).order_by(Session.id.desc()).limit(50).all()
        layout = next((A.loads(s.layout_json or '[]', []) for s in sessions if s.layout_json and s.layout_json != '[]'), [])
        n_sections = len([x for x in layout if isinstance(x, dict) and (x.get('kind') or 'heading') == 'heading']) or None
        recap = A.reading_recap(rows, total, n_sections, sessions)
        return jsonify({'review': review[:8], 'policy': POLICY_VERSION, 'total_ms': total, 'recap': recap})

    @bp.route('/api/helix/section/<int:section_id>/summary.json')
    @login_required
    def section_summary_json(section_id):
        section = staff_section_or_403(section_id)
        sessions = Session.query.filter_by(section_id=section.id).all()
        users = users_by_id({s.user_id for s in sessions})
        students, missing = A.student_summaries(sessions, users, enrolled_ids(section))
        buckets = Bucket.query.filter_by(section_id=section.id).all()
        aois, total = A.aoi_rollup(buckets)
        for s in students:
            s.pop('lessons', None)
            s['last'] = s['last'].isoformat() if s['last'] else None
        return jsonify({'ok': True, 'section_id': section.id, 'students': students,
                        'not_opted_in': len(missing), 'aois': aois[:50], 'total_ms': total})

    # ------------------------------------------------------------ pages: policy, consent, my data
    @bp.route('/helix/try')
    def try_page():
        """Local-only playground: calibrate, see the live gaze dot and diagnostics, measure accuracy.
        Nothing is uploaded or stored, so it needs no consent record and works signed out."""
        return render_template('helix/try.html', engine=request.args.get('engine', 'auto'))

    @bp.route('/policy/attention')
    def policy():
        return render_template('helix/policy.html', policy_version=POLICY_VERSION)

    @bp.route('/helix/consent', methods=['GET', 'POST'])
    @login_required
    def consent_page():
        nxt = request.values.get('next') or ''
        if not nxt.startswith('/'):
            nxt = url_for('helix.my_data')
        c = active_consent(current_user.id)
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'revoke':
                revoke()
                flash('Helix consent withdrawn. No new attention data will be recorded.', 'info')
                return redirect(nxt)
            if not request.form.get('agree'):
                flash('Tick the agreement box to turn Helix on, or choose "Not now".', 'warning')
                return redirect(url_for('helix.consent_page', next=nxt))
            grant(bool(request.form.get('camera_ok')), bool(request.form.get('passive_ok')))
            flash('Helix consent saved. You can withdraw it at any time from "My attention data".', 'success')
            return redirect(nxt)
        return render_template('helix/consent.html', consent=c, current=consent_current(c),
                               policy_version=POLICY_VERSION, next_url=nxt)

    @bp.route('/student/attention')
    @login_required
    def my_data():
        sessions = (Session.query.filter_by(user_id=current_user.id)
                    .order_by(Session.started_at.desc()).limit(200).all())
        mark_stale(sessions)
        lessons = valid_lesson_ids({s.lesson_id for s in sessions})
        rows = []
        for s in sessions:
            b = A.session_breakdown(s)
            rows.append({'s': s, 'lesson': lessons.get(s.lesson_id), 'b': b,
                         'band': A.accuracy_band(s.calibration_score, s.mode or 'gaze'),
                         'attentive_pct': A.pct(b['attentive'], b['total'])})
        c = active_consent(current_user.id)
        return render_template('helix/my_data.html', rows=rows, consent=c, current=consent_current(c),
                               policy_version=POLICY_VERSION)

    @bp.route('/student/attention/delete', methods=['POST'])
    @login_required
    def my_data_delete():
        sid = request.form.get('session_id', type=int)
        q = Session.query.filter_by(user_id=current_user.id)
        if sid:
            q = q.filter_by(id=sid)
        ids = [s.id for s in q.all()]
        if ids:
            Bucket.query.filter(Bucket.session_id.in_(ids)).delete(synchronize_session=False)
            Session.query.filter(Session.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
        d.audit('helix_self_delete', f'sessions={len(ids)}')
        flash(f'Deleted {len(ids)} attention session{"s" if len(ids) != 1 else ""}.', 'success')
        return redirect(url_for('helix.my_data'))

    # ------------------------------------------------------------ instructor dashboards
    @bp.route('/instructor/section/<int:section_id>/attention')
    @bp.route('/instructor/section/<int:section_id>/attention/report', endpoint='attention_report')
    @login_required
    def instructor_attention(section_id):
        section = staff_section_or_403(section_id)
        report = request.endpoint == 'helix.attention_report'
        # Large classes: never pull the big JSON blobs for the overview, and aggregate AOI dwell
        # in SQL (one row per lesson x student x AOI instead of one per session bucket).
        from sqlalchemy.orm import defer
        sessions = (Session.query.filter_by(section_id=section.id)
                    .options(defer(Session.heat_json), defer(Session.layout_json), defer(Session.drift_json),
                             defer(Session.fine_json), defer(Session.timeline_json))
                    .order_by(Session.started_at.desc()).all())
        mark_stale(sessions)
        lessons = valid_lesson_ids({s.lesson_id for s in sessions})
        sessions = [s for s in sessions if s.lesson_id in lessons]
        users = users_by_id({s.user_id for s in sessions})
        enrolled = enrolled_ids(section)
        students, missing = A.student_summaries(sessions, users, enrolled)
        buckets = [b for b in aggregated_buckets(section.id) if b.lesson_id in lessons]
        by_lesson = {}
        for b in buckets:
            by_lesson.setdefault(b.lesson_id, []).append(b)
        aois, total_ms = A.aoi_rollup(buckets)
        # paginate the per-student table (KPIs and charts still use everyone)
        per = request.args.get('per', type=int) or 50
        per = per if per in (25, 50, 100, 200) else 50
        if report:
            per = max(1, 10 ** 6)          # the printable report lists everyone
        spages = max(1, -(-len(students) // per))
        spage = min(max(1, request.args.get('spage', type=int) or 1), spages)
        students_all = students
        students = students_all[(spage - 1) * per: spage * per]
        spager = {'page': spage, 'pages': spages, 'per': per, 'total': len(students_all),
                  'first': (spage - 1) * per + 1 if students_all else 0, 'last': min(spage * per, len(students_all))}
        # lesson table
        per_lesson = {}
        for s in sessions:
            r = per_lesson.setdefault(s.lesson_id, {'sessions': 0, 'students': set(), 'acc': [], 'att': [0, 0]})
            r['sessions'] += 1
            r['students'].add(s.user_id)
            if s.calibration_score and (s.mode or 'gaze') == 'gaze':
                r['acc'].append(s.calibration_score)
            b = A.session_breakdown(s)
            r['att'][0] += b['attentive']
            r['att'][1] += b['total']
        lesson_rows = []
        for lid, r in per_lesson.items():
            L = lessons[lid]
            la, _ = A.aoi_rollup(by_lesson.get(lid, []))
            lesson_rows.append({
                'id': lid, 'title': L.title, 'module_id': L.module_id, 'sessions': r['sessions'],
                'students': len(r['students']),
                'accuracy': int(sum(r['acc']) / len(r['acc'])) if r['acc'] else 0,
                'attentive_pct': A.pct(r['att'][0], r['att'][1]),
                'thin': [a['label'] for a in la if a['thin']][:3],
            })
        lesson_rows.sort(key=lambda x: (lessons[x['id']].module_id, lessons[x['id']].order))
        focus_id = request.args.get('lesson', type=int)
        if focus_id not in per_lesson and lesson_rows:
            focus_id = max(lesson_rows, key=lambda r: r['sessions'])['id']
        matrix = A.aoi_matrix(by_lesson.get(focus_id, []), users) if focus_id else None
        if matrix:   # class means use everyone; rows follow the student-table page
            matrix['rows_total'] = len(matrix['rows'])
            matrix['rows'] = matrix['rows'][(spage - 1) * per: spage * per]
        gaze = [s for s in sessions if (s.mode or 'gaze') == 'gaze' and s.calibration_score]
        tot = {'attentive': 0, 'off_page': 0, 'face_lost': 0, 'hidden': 0, 'low_conf': 0, 'total': 0}
        for s in sessions:
            b = A.session_breakdown(s)
            for k in tot:
                tot[k] += b[k]
        kpi = {
            'sessions': len(sessions),
            'students': len(students_all),
            'enrolled': len(enrolled),
            'not_opted_in': len(missing),
            'avg_accuracy': int(sum(s.calibration_score for s in gaze) / len(gaze)) if gaze else 0,
            'gaze_sessions': len([s for s in sessions if (s.mode or 'gaze') == 'gaze']),
            'passive_sessions': len([s for s in sessions if s.mode == 'passive']),
            'running': len([s for s in sessions if s.status == 'running']),
            'attentive_pct': A.pct(tot['attentive'], tot['total']),
            'mix': {k: A.pct(v, tot['total']) for k, v in tot.items() if k != 'total'},
            'minutes': round(tot['total'] / 60000.0, 1),
            'mediapipe_sessions': len([s for s in gaze if s.engine == 'mediapipe']),
            'webgazer_sessions': len([s for s in gaze if s.engine != 'mediapipe']),
            'median_error_deg': A.median_or_none([s.validation_error_deg for s in gaze if s.validation_error_deg]),
            'fine_sessions': len([s for s in gaze if (s.aoi_resolution or 'heading') != 'heading']),
        }
        setting = section_setting(section.id)
        demo = any(getattr(s, 'is_demo', False) for s in sessions)
        not_opted = [users_by_id(missing).get(uid) for uid in missing]
        if report:
            d.audit('helix_report', f'section={section.id}')
            engines = {}
            for s_ in sessions:
                k = 'reading signal' if s_.mode == 'passive' else ({'mediapipe': 'MediaPipe'}.get(s_.engine) or 'WebGazer')
                engines[k] = engines.get(k, 0) + 1
            return render_template(
                'helix/report.html', section=section, students=students, aois=aois[:40], total_ms=total_ms,
                lessons=lesson_rows, kpi=kpi, setting=setting, demo=demo, not_opted=[u for u in not_opted if u],
                policy_version=POLICY_VERSION, band=A.accuracy_band(kpi['avg_accuracy']), engines=engines,
                generated=utcnow(), generated_by=current_user,
                date_range=(min((s_.started_at for s_ in sessions if s_.started_at), default=None),
                            max((s_.started_at for s_ in sessions if s_.started_at), default=None)))
        return render_template(
            'helix/dashboard.html', section=section, students=students, spager=spager, aois=aois[:24], total_ms=total_ms,
            lessons=lesson_rows, focus_id=focus_id, focus_lesson=lessons.get(focus_id), matrix=matrix,
            kpi=kpi, setting=setting, demo=demo, not_opted=[u for u in not_opted if u],
            policy_version=POLICY_VERSION, band=A.accuracy_band(kpi['avg_accuracy']),
        )

    @bp.route('/instructor/section/<int:section_id>/attention/settings', methods=['POST'])
    @login_required
    def instructor_attention_settings(section_id):
        section = staff_section_or_403(section_id)
        s = section_setting(section.id) or Setting(section_id=section.id)
        s.enabled = bool(request.form.get('enabled'))
        s.passive_enabled = bool(request.form.get('passive_enabled'))
        s.min_accuracy = A._int(request.form.get('min_accuracy'), 45, lo=20, hi=90)
        s.updated_at = utcnow()
        s.updated_by = current_user.id
        db.session.add(s)
        db.session.commit()
        d.audit('helix_settings', f'section={section.id} enabled={s.enabled} passive={s.passive_enabled}')
        flash('Helix settings saved for this class.', 'success')
        return redirect(url_for('helix.instructor_attention', section_id=section.id))

    @bp.route('/instructor/section/<int:section_id>/attention/student/<int:user_id>')
    @login_required
    def instructor_attention_student(section_id, user_id):
        section = staff_section_or_403(section_id)
        student = db.get_or_404(d.User, user_id)
        sessions = (Session.query.filter_by(section_id=section.id, user_id=user_id)
                    .order_by(Session.started_at.desc()).all())
        mark_stale(sessions)
        lessons = valid_lesson_ids({s.lesson_id for s in sessions})
        sessions = [s for s in sessions if s.lesson_id in lessons]
        summary, _ = A.student_summaries(sessions, {student.id: student})
        blocks = []
        by_lesson = {}
        for s in sessions:
            by_lesson.setdefault(s.lesson_id, []).append(s)
        for lid, sl in by_lesson.items():
            buckets = Bucket.query.filter_by(section_id=section.id, user_id=user_id, lesson_id=lid).all()
            aois, total = A.aoi_rollup(buckets)
            aois.sort(key=lambda a: a['order'])
            rows = []
            for s in sl:
                b = A.session_breakdown(s)
                rows.append({'s': s, 'b': b, 'band': A.accuracy_band(s.calibration_score, s.mode or 'gaze'),
                             'attentive_pct': A.pct(b['attentive'], b['total'])})
            blocks.append({'lesson': lessons[lid], 'sessions': rows, 'aois': aois[:20], 'total_ms': total,
                           'lanes': A.timeline_lanes(sl, {student.id: student}, max_lanes=6)})
        blocks.sort(key=lambda b: (b['lesson'].module_id, b['lesson'].order))
        return render_template('helix/student.html', section=section, student=student, blocks=blocks,
                               summary=summary[0] if summary else None,
                               demo=any(getattr(s, 'is_demo', False) for s in sessions))

    @bp.route('/instructor/section/<int:section_id>/attention/lesson/<int:lesson_id>')
    @login_required
    def instructor_attention_lesson(section_id, lesson_id):
        section = staff_section_or_403(section_id)
        lesson = db.get_or_404(d.Lesson, lesson_id)
        sessions = (Session.query.filter_by(section_id=section.id, lesson_id=lesson_id)
                    .order_by(Session.started_at.desc()).all())
        users = users_by_id({s.user_id for s in sessions})
        buckets = Bucket.query.filter_by(section_id=section.id, lesson_id=lesson_id).all()
        aois, total = A.aoi_rollup(buckets)
        aois.sort(key=lambda a: a['order'])
        heat = A.aggregate_heat(sessions)
        layout = A.merged_layout(sessions)
        lanes = A.timeline_lanes(sessions, users)
        matrix = A.aoi_matrix(buckets, users)
        students, _ = A.student_summaries(sessions, users)
        return render_template('helix/lesson.html', section=section, lesson=lesson, aois=aois, total_ms=total,
                               heat=heat, layout=layout, lanes=lanes, matrix=matrix, students=students,
                               n_sessions=len(sessions),
                               demo=any(getattr(s, 'is_demo', False) for s in sessions))

    @bp.route('/instructor/section/<int:section_id>/attention.csv')
    @login_required
    def attention_csv(section_id):
        section = staff_section_or_403(section_id)
        buckets = Bucket.query.filter_by(section_id=section.id).all()
        users = users_by_id({b.user_id for b in buckets})
        lessons = valid_lesson_ids({b.lesson_id for b in buckets})
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(['student', 'email', 'lesson', 'aoi_key', 'aoi', 'kind', 'dwell_ms', 'visits', 'session_id'])
        for b in buckets:
            u, L = users.get(b.user_id), lessons.get(b.lesson_id)
            w.writerow([u.full_name if u else b.user_id, u.email if u else '', L.title if L else b.lesson_id,
                        b.aoi_key, b.aoi_label, b.aoi_kind or '', b.dwell_ms or 0, b.visits or 0, b.session_id or ''])
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename=attention-section-{section_id}.csv'})

    @bp.route('/instructor/section/<int:section_id>/attention-sessions.csv')
    @login_required
    def attention_sessions_csv(section_id):
        section = staff_section_or_403(section_id)
        sessions = Session.query.filter_by(section_id=section.id).all()
        users = users_by_id({s.user_id for s in sessions})
        lessons = valid_lesson_ids({s.lesson_id for s in sessions})
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(['session_id', 'student', 'lesson', 'mode', 'device', 'status', 'started_utc', 'ended_utc',
                    'calibration_score', 'validation_error_px', 'recalibrations', 'total_ms', 'attentive_ms',
                    'off_page_ms', 'face_lost_ms', 'hidden_ms', 'low_conf_ms', 'samples', 'demo'])
        for s in sessions:
            b = A.session_breakdown(s)
            u, L = users.get(s.user_id), lessons.get(s.lesson_id)
            w.writerow([s.id, u.full_name if u else s.user_id, L.title if L else s.lesson_id, s.mode or 'gaze',
                        s.device or '', s.status, s.started_at, s.ended_at or '', s.calibration_score or 0,
                        s.validation_error_px or 0, s.recalibrations or 0, b['total'], b['attentive'],
                        b['off_page'], b['face_lost'], b['hidden'], b['low_conf'], s.sample_count or 0,
                        int(bool(s.is_demo))])
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename=attention-sessions-{section_id}.csv'})

    return bp
