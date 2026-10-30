"""Tables for the in-app xAPI LRS and cmi5 courses, registrations, and sessions.

Created with the rest of the schema (db.create_all). No separate database.
"""
from datetime import datetime, timezone

_cache = {}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_models(db):
    if 'm' in _cache and _cache.get('db') is db:
        return _cache['m']

    class LrsClient(db.Model):
        """HTTP Basic credential for one organization or external client."""
        __tablename__ = 'lrs_client'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        key = db.Column(db.String(80), unique=True, nullable=False)
        secret_hash = db.Column(db.String(256), nullable=False)
        active = db.Column(db.Boolean, default=True, nullable=False)
        created_at = db.Column(db.DateTime, default=utcnow)

    class Cmi5Course(db.Model):
        __tablename__ = 'cmi5_course'
        id = db.Column(db.Integer, primary_key=True)
        publisher_id = db.Column(db.String(1000), nullable=False, index=True)
        lms_activity_id = db.Column(db.String(1000), nullable=False, unique=True)
        title = db.Column(db.String(400), nullable=False)
        description = db.Column(db.Text, default='')
        source = db.Column(db.String(20), default='import')
        novak_code = db.Column(db.String(20))
        created_at = db.Column(db.DateTime, default=utcnow)

    class Cmi5Block(db.Model):
        __tablename__ = 'cmi5_block'
        id = db.Column(db.Integer, primary_key=True)
        course_id = db.Column(db.Integer, db.ForeignKey('cmi5_course.id'), nullable=False, index=True)
        parent_id = db.Column(db.Integer, db.ForeignKey('cmi5_block.id'))
        publisher_id = db.Column(db.String(1000), nullable=False)
        lms_activity_id = db.Column(db.String(1000), nullable=False)
        title = db.Column(db.String(400), nullable=False)
        description = db.Column(db.Text, default='')
        sort_order = db.Column(db.Integer, default=0)

    class Cmi5AU(db.Model):
        __tablename__ = 'cmi5_au'
        id = db.Column(db.Integer, primary_key=True)
        course_id = db.Column(db.Integer, db.ForeignKey('cmi5_course.id'), nullable=False, index=True)
        block_id = db.Column(db.Integer, db.ForeignKey('cmi5_block.id'), index=True)
        publisher_id = db.Column(db.String(1000), nullable=False)
        lms_activity_id = db.Column(db.String(1000), nullable=False)
        title = db.Column(db.String(400), nullable=False)
        description = db.Column(db.Text, default='')
        url = db.Column(db.String(1000), nullable=False)
        launch_method = db.Column(db.String(20), default='AnyWindow')
        move_on = db.Column(db.String(40), default='NotApplicable')
        mastery_score = db.Column(db.String(16))
        launch_parameters = db.Column(db.Text)
        entitlement_key = db.Column(db.Text)
        activity_type = db.Column(db.String(500))
        sort_order = db.Column(db.Integer, default=0)

    class Cmi5Registration(db.Model):
        __tablename__ = 'cmi5_registration'
        id = db.Column(db.Integer, primary_key=True)
        uuid = db.Column(db.String(36), unique=True, nullable=False)
        course_id = db.Column(db.Integer, db.ForeignKey('cmi5_course.id'), nullable=False, index=True)
        actor_json = db.Column(db.Text, nullable=False)
        learner_label = db.Column(db.String(200), default='')
        created_at = db.Column(db.DateTime, default=utcnow)

    class Cmi5Session(db.Model):
        __tablename__ = 'cmi5_session'
        id = db.Column(db.Integer, primary_key=True)
        uuid = db.Column(db.String(36), unique=True, nullable=False)
        registration_id = db.Column(db.Integer, db.ForeignKey('cmi5_registration.id'), nullable=False, index=True)
        au_id = db.Column(db.Integer, db.ForeignKey('cmi5_au.id'), nullable=False, index=True)
        launch_mode = db.Column(db.String(20), default='Normal')
        fetch_secret = db.Column(db.String(80), unique=True)
        fetch_used_at = db.Column(db.DateTime)
        auth_username = db.Column(db.String(80), unique=True)
        auth_secret_hash = db.Column(db.String(256))
        launched_at = db.Column(db.DateTime)
        terminated_at = db.Column(db.DateTime)
        abandoned_at = db.Column(db.DateTime)
        return_url = db.Column(db.String(1000))
        launch_url = db.Column(db.String(1000))
        is_waive = db.Column(db.Boolean, default=False, nullable=False)
        prefs_read = db.Column(db.Boolean, default=False, nullable=False)

    class Cmi5File(db.Model):
        __tablename__ = 'cmi5_file'
        __table_args__ = (db.UniqueConstraint('course_id', 'path', name='uq_cmi5_file_path'),)
        id = db.Column(db.Integer, primary_key=True)
        course_id = db.Column(db.Integer, db.ForeignKey('cmi5_course.id'), nullable=False, index=True)
        path = db.Column(db.String(500), nullable=False)
        content_type = db.Column(db.String(120), default='application/octet-stream')
        content = db.Column(db.LargeBinary, nullable=False)

    class XapiStatement(db.Model):
        __tablename__ = 'xapi_statement'
        id = db.Column(db.String(36), primary_key=True)
        stored = db.Column(db.DateTime, nullable=False, index=True)
        statement_timestamp = db.Column(db.DateTime, index=True)
        actor_key = db.Column(db.String(1000), index=True)
        verb_id = db.Column(db.String(400), index=True)
        object_id = db.Column(db.String(1000), index=True)
        registration = db.Column(db.String(36), index=True)
        body = db.Column(db.Text, nullable=False)
        voided = db.Column(db.Boolean, default=False, nullable=False, index=True)
        is_voiding = db.Column(db.Boolean, default=False, nullable=False)
        void_target = db.Column(db.String(36), index=True)

    class XapiDocument(db.Model):
        __tablename__ = 'xapi_document'
        __table_args__ = (
            db.UniqueConstraint('kind', 'activity_id', 'agent_key', 'registration', 'doc_id', name='uq_xapi_document'),
        )
        id = db.Column(db.Integer, primary_key=True)
        kind = db.Column(db.String(32), nullable=False, index=True)
        activity_id = db.Column(db.String(1000), default='', nullable=False)
        agent_key = db.Column(db.String(1000), default='', nullable=False)
        registration = db.Column(db.String(36), default='', nullable=False)
        doc_id = db.Column(db.String(220), default='', nullable=False)
        content = db.Column(db.LargeBinary, nullable=False)
        content_type = db.Column(db.String(200), nullable=False)
        etag = db.Column(db.String(80), nullable=False)
        updated_at = db.Column(db.DateTime, nullable=False, index=True)

    class XapiAttachment(db.Model):
        __tablename__ = 'xapi_attachment'
        sha2 = db.Column(db.String(128), primary_key=True)
        content_type = db.Column(db.String(200), default='application/octet-stream')
        content = db.Column(db.LargeBinary, nullable=False)

    ns = {
        'LrsClient': LrsClient,
        'Cmi5Course': Cmi5Course,
        'Cmi5Block': Cmi5Block,
        'Cmi5AU': Cmi5AU,
        'Cmi5Registration': Cmi5Registration,
        'Cmi5Session': Cmi5Session,
        'Cmi5File': Cmi5File,
        'XapiStatement': XapiStatement,
        'XapiDocument': XapiDocument,
        'XapiAttachment': XapiAttachment,
    }
    _cache['db'] = db
    _cache['m'] = ns
    return ns
