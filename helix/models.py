"""Helix storage models.

Defined through a factory so the flat ``app.py`` can keep owning the single
``SQLAlchemy`` instance (``python app.py`` runs it as ``__main__``, so a plain
``from app import db`` here would import the app twice).
"""
from datetime import datetime, timezone
from types import SimpleNamespace


def utcnow():
    """Naive UTC now. Replaces the deprecated datetime.utcnow(); stored columns stay naive UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

STUDY_VERSION = '2026-10-17.s1'  # accuracy-study consent text (separate from the lesson policy)
POLICY_VERSION = '2026-10-17.3'  # .3: calibration time/method, re-checks, interruption counts, camera size, browser family.
# .2: camera on phones, paragraph/line dwell when accuracy allows
ENGINE = 'webgazer'

# Special AOI keys produced by the client state machine. They are stored in the
# timeline so instructors can see *why* there is no reading dwell, but they are
# never counted as reading attention.
STATE_KEYS = {
    'off_page': 'Looking away from page',
    'chrome': 'Page chrome / navigation',
    '_face_lost': 'Face not detected',
    '_hidden': 'Tab hidden / app switched',
    '_low_conf': 'Low-confidence estimate',
    '_idle': 'No activity (passive mode)',
    '_paused': 'Paused by student',
    '_camera_off': 'Camera disconnected or blocked',   # pass 10 session hardening
    '_other_tab': 'Helix active in another tab',
    '_asleep': 'Device asleep / page suspended',
}
NON_READING_KEYS = set(STATE_KEYS)
NON_READING_LABELS = set(STATE_KEYS.values()) | {'Off page', 'Page chrome'}

_cache = {}


def define_models(db):
    if 'models' in _cache:
        return _cache['models']

    class HelixAttentionEvent(db.Model):
        """Legacy heading beat. Prefer HelixGazeSession + HelixAoiBucket."""
        __tablename__ = 'helix_attention_event'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
        lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
        heading = db.Column(db.String(240), default='')
        seconds = db.Column(db.Float, default=0)
        focused = db.Column(db.Float, default=0)
        created_at = db.Column(db.DateTime, default=utcnow)

    class HelixGazeSession(db.Model):
        """One opt-in Helix run on a lesson page (camera gaze or passive signal)."""
        __tablename__ = 'helix_gaze_session'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
        lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
        engine = db.Column(db.String(40), default=ENGINE)
        consent_version = db.Column(db.String(20), default=POLICY_VERSION)
        started_at = db.Column(db.DateTime, default=utcnow)
        ended_at = db.Column(db.DateTime)
        calibration_points = db.Column(db.Integer, default=0)
        calibration_score = db.Column(db.Integer, default=0)
        viewport_w = db.Column(db.Integer, default=0)
        viewport_h = db.Column(db.Integer, default=0)
        sample_count = db.Column(db.Integer, default=0)
        timeline_json = db.Column(db.Text, default='[]')
        status = db.Column(db.String(20), default='running')
        # --- added in the refinement pass (auto-migrated by ensure_schema) ---
        client_uuid = db.Column(db.String(40), index=True)
        mode = db.Column(db.String(12), default='gaze')        # gaze | passive
        device = db.Column(db.String(12), default='desktop')   # desktop | tablet | mobile
        validation_error_px = db.Column(db.Integer, default=0)
        validation_precision_px = db.Column(db.Integer, default=0)
        recalibrations = db.Column(db.Integer, default=0)
        total_ms = db.Column(db.Integer, default=0)
        attentive_ms = db.Column(db.Integer, default=0)
        off_page_ms = db.Column(db.Integer, default=0)
        face_lost_ms = db.Column(db.Integer, default=0)
        hidden_ms = db.Column(db.Integer, default=0)
        low_conf_ms = db.Column(db.Integer, default=0)
        rejected_samples = db.Column(db.Integer, default=0)
        last_seq = db.Column(db.Integer, default=-1)
        last_seen_at = db.Column(db.DateTime)
        # --- pass 3: camera pipeline metadata (auto-migrated) ---
        delegate = db.Column(db.String(40), default='')            # GPU | CPU | WebGazer (TF.js)
        validation_error_deg = db.Column(db.Float)                 # median validation error, visual degrees
        distance_cm = db.Column(db.Integer)                        # estimated eye-to-screen distance
        aoi_resolution = db.Column(db.String(12), default='heading')  # heading | paragraph | line
        orientation = db.Column(db.String(12), default='')
        drift_json = db.Column(db.Text, default='[]')              # implicit-sample error over time
        implicit_samples = db.Column(db.Integer, default=0)
        fine_json = db.Column(db.Text, default='[]')               # paragraph/line dwell (only if accuracy allowed)
        heat_json = db.Column(db.Text, default='{}')     # {"cols":20,"rows":60,"cells":{"x,y":ms}}
        layout_json = db.Column(db.Text, default='[]')   # [{key,label,order,y0,y1}] fractions of lesson body
        is_demo = db.Column(db.Boolean, default=False)
        # pass 10: calibration time/quality and session-hardening counters (all gaze-derived numbers)
        calib_ms = db.Column(db.Integer)                           # first calibration dot -> end of check
        calib_mode = db.Column(db.String(16), default='')          # dots | follow | follow+dots
        rechecks = db.Column(db.Integer, default=0)
        recheck_error_px = db.Column(db.Integer)
        recheck_error_deg = db.Column(db.Float)
        camera_losses = db.Column(db.Integer, default=0)
        sleeps = db.Column(db.Integer, default=0)
        tab_yields = db.Column(db.Integer, default=0)
        camera_res = db.Column(db.String(20), default='')
        hires = db.Column(db.Boolean, default=False)
        browser = db.Column(db.String(30), default='')

    class HelixAoiBucket(db.Model):
        """Queryable dwell per student / lesson / AOI. Not a grade."""
        __tablename__ = 'helix_aoi_bucket'
        id = db.Column(db.Integer, primary_key=True)
        session_id = db.Column(db.Integer, db.ForeignKey('helix_gaze_session.id'))
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
        lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
        aoi_key = db.Column(db.String(80), default='')
        aoi_label = db.Column(db.String(240), default='')
        aoi_order = db.Column(db.Integer, default=0)
        aoi_kind = db.Column(db.String(20), default='heading')
        dwell_ms = db.Column(db.Integer, default=0)
        visits = db.Column(db.Integer, default=0)
        first_ms = db.Column(db.Integer, default=0)
        last_ms = db.Column(db.Integer, default=0)
        updated_at = db.Column(db.DateTime, default=utcnow)

    class HelixConsent(db.Model):
        """Explicit per-student consent record (versioned, revocable)."""
        __tablename__ = 'helix_consent'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        policy_version = db.Column(db.String(20), nullable=False)
        camera_ok = db.Column(db.Boolean, default=True)
        passive_ok = db.Column(db.Boolean, default=True)
        granted_at = db.Column(db.DateTime, default=utcnow)
        revoked_at = db.Column(db.DateTime)

    class HelixSectionSetting(db.Model):
        """Instructor switch: Helix offered on this section's lesson pages or not."""
        __tablename__ = 'helix_section_setting'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), unique=True, nullable=False)
        enabled = db.Column(db.Boolean, default=True)
        passive_enabled = db.Column(db.Boolean, default=True)
        min_accuracy = db.Column(db.Integer, default=45)
        updated_at = db.Column(db.DateTime, default=utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    class HelixStudyConsent(db.Model):
        """Separate, opt-in consent for the accuracy study (pass 10). Independent of lesson consent."""
        __tablename__ = 'helix_study_consent'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        version = db.Column(db.String(20), nullable=False)
        granted_at = db.Column(db.DateTime, default=utcnow)
        revoked_at = db.Column(db.DateTime)

    class HelixAccuracyRecord(db.Model):
        """One accuracy check: known validation targets vs the tracker's estimates. Numbers only:
        no images, landmarks or raw gaze samples. Never seeded or simulated."""
        __tablename__ = 'helix_accuracy_record'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        created_at = db.Column(db.DateTime, default=utcnow, index=True)
        study_version = db.Column(db.String(20), default='')
        context = db.Column(db.String(12), default='lesson')       # lesson | study
        kind = db.Column(db.String(16), default='calibration')     # calibration | recal | quick | recheck
        pair_id = db.Column(db.String(40), default='')             # study page: both arms of one visit
        arm_method = db.Column(db.String(16), default='')          # dots | follow | follow+dots | recheck
        arm_hires = db.Column(db.Boolean, default=False)           # 1080p requested
        device = db.Column(db.String(12), default='desktop')
        browser = db.Column(db.String(30), default='')
        camera_res = db.Column(db.String(20), default='')          # actual video size, e.g. 1280x720
        viewport_w = db.Column(db.Integer, default=0)
        viewport_h = db.Column(db.Integer, default=0)
        dpr = db.Column(db.Float)
        engine = db.Column(db.String(20), default='')
        delegate = db.Column(db.String(40), default='')
        calib_points = db.Column(db.Integer, default=0)
        calib_ms = db.Column(db.Integer)
        valid = db.Column(db.Boolean, default=False)
        score = db.Column(db.Integer, default=0)
        error_px = db.Column(db.Integer)
        error_deg = db.Column(db.Float)
        precision_px = db.Column(db.Integer)
        distance_cm = db.Column(db.Integer)
        points_json = db.Column(db.Text, default='[]')             # per target: fx, fy, err_px, n

    class HelixCalibDefault(db.Model):
        """Calibration defaults per device class, changed only by an admin after reviewing study data."""
        __tablename__ = 'helix_calib_default'
        id = db.Column(db.Integer, primary_key=True)
        device = db.Column(db.String(12), unique=True, nullable=False)
        method = db.Column(db.String(16), default='dots')
        hires = db.Column(db.Boolean, default=False)
        basis = db.Column(db.Text, default='')
        decided_at = db.Column(db.DateTime, default=utcnow)
        decided_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    models = SimpleNamespace(
        HelixStudyConsent=HelixStudyConsent, HelixAccuracyRecord=HelixAccuracyRecord, HelixCalibDefault=HelixCalibDefault,
        HelixAttentionEvent=HelixAttentionEvent,
        HelixGazeSession=HelixGazeSession,
        HelixAoiBucket=HelixAoiBucket,
        HelixConsent=HelixConsent,
        HelixSectionSetting=HelixSectionSetting,
    )
    _cache['models'] = models
    return models


# Columns added after the first public release: (table, column, DDL type)
MIGRATIONS = [
    ('helix_gaze_session', 'client_uuid', 'VARCHAR(40)'),
    ('helix_gaze_session', 'mode', "VARCHAR(12) DEFAULT 'gaze'"),
    ('helix_gaze_session', 'device', "VARCHAR(12) DEFAULT 'desktop'"),
    ('helix_gaze_session', 'validation_error_px', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'validation_precision_px', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'recalibrations', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'total_ms', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'attentive_ms', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'off_page_ms', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'face_lost_ms', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'hidden_ms', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'low_conf_ms', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'rejected_samples', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'last_seq', 'INTEGER DEFAULT -1'),
    ('helix_gaze_session', 'last_seen_at', 'DATETIME'),
    ('helix_gaze_session', 'heat_json', "TEXT DEFAULT '{}'"),
    ('helix_gaze_session', 'layout_json', "TEXT DEFAULT '[]'"),
    ('helix_gaze_session', 'is_demo', 'BOOLEAN DEFAULT 0'),
    ('helix_aoi_bucket', 'aoi_kind', "VARCHAR(20) DEFAULT 'heading'"),
    ('helix_gaze_session', 'delegate', "VARCHAR(40) DEFAULT ''"),
    ('helix_gaze_session', 'validation_error_deg', 'FLOAT'),
    ('helix_gaze_session', 'distance_cm', 'INTEGER'),
    ('helix_gaze_session', 'aoi_resolution', "VARCHAR(12) DEFAULT 'heading'"),
    ('helix_gaze_session', 'orientation', "VARCHAR(12) DEFAULT ''"),
    ('helix_gaze_session', 'drift_json', "TEXT DEFAULT '[]'"),
    ('helix_gaze_session', 'implicit_samples', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'fine_json', "TEXT DEFAULT '[]'"),
    # pass 10
    ('helix_gaze_session', 'calib_ms', 'INTEGER'),
    ('helix_gaze_session', 'calib_mode', "VARCHAR(16) DEFAULT ''"),
    ('helix_gaze_session', 'rechecks', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'recheck_error_px', 'INTEGER'),
    ('helix_gaze_session', 'recheck_error_deg', 'FLOAT'),
    ('helix_gaze_session', 'camera_losses', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'sleeps', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'tab_yields', 'INTEGER DEFAULT 0'),
    ('helix_gaze_session', 'camera_res', "VARCHAR(20) DEFAULT ''"),
    ('helix_gaze_session', 'hires', 'BOOLEAN DEFAULT 0'),
    ('helix_gaze_session', 'browser', "VARCHAR(30) DEFAULT ''"),
]


def ensure_schema(db):
    """Add new columns to an existing SQLite/Postgres DB without dropping data."""
    from sqlalchemy import inspect, text
    try:
        insp = inspect(db.engine)
        tables = set(insp.get_table_names())
        with db.engine.begin() as conn:
            for table, col, ddl in MIGRATIONS:
                if table not in tables:
                    continue
                cols = {c['name'] for c in insp.get_columns(table)}
                if col not in cols:
                    conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {col} {ddl}'))
    except Exception as exc:  # pragma: no cover - defensive on exotic DBs
        print('Helix schema note:', exc)
