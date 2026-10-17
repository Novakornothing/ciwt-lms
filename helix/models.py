"""Helix storage models.

Defined through a factory so the flat ``app.py`` can keep owning the single
``SQLAlchemy`` instance (``python app.py`` runs it as ``__main__``, so a plain
``from app import db`` here would import the app twice).
"""
from datetime import datetime
from types import SimpleNamespace

POLICY_VERSION = '2026-10-17'
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
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class HelixGazeSession(db.Model):
        """One opt-in Helix run on a lesson page (camera gaze or passive signal)."""
        __tablename__ = 'helix_gaze_session'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
        lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
        engine = db.Column(db.String(40), default=ENGINE)
        consent_version = db.Column(db.String(20), default=POLICY_VERSION)
        started_at = db.Column(db.DateTime, default=datetime.utcnow)
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
        heat_json = db.Column(db.Text, default='{}')     # {"cols":20,"rows":60,"cells":{"x,y":ms}}
        layout_json = db.Column(db.Text, default='[]')   # [{key,label,order,y0,y1}] fractions of lesson body
        is_demo = db.Column(db.Boolean, default=False)

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
        updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    class HelixConsent(db.Model):
        """Explicit per-student consent record (versioned, revocable)."""
        __tablename__ = 'helix_consent'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        policy_version = db.Column(db.String(20), nullable=False)
        camera_ok = db.Column(db.Boolean, default=True)
        passive_ok = db.Column(db.Boolean, default=True)
        granted_at = db.Column(db.DateTime, default=datetime.utcnow)
        revoked_at = db.Column(db.DateTime)

    class HelixSectionSetting(db.Model):
        """Instructor switch: Helix offered on this section's lesson pages or not."""
        __tablename__ = 'helix_section_setting'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), unique=True, nullable=False)
        enabled = db.Column(db.Boolean, default=True)
        passive_enabled = db.Column(db.Boolean, default=True)
        min_accuracy = db.Column(db.Integer, default=45)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    models = SimpleNamespace(
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
