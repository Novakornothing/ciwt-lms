"""Tables for the adaptive mastery engine (pass 11). Additive only: no existing table is changed."""
from datetime import datetime, timezone
from types import SimpleNamespace

_cache = {}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_models(db):
    if 'm' in _cache:
        return _cache['m']

    class MasterySetting(db.Model):
        """Per-class switches. No row = defaults (adaptivity on, mastery checks on, chapter checks only)."""
        __tablename__ = 'mastery_setting'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), unique=True, nullable=False)
        enabled = db.Column(db.Boolean, default=True)
        testout = db.Column(db.Boolean, default=True)
        testout_bank = db.Column(db.Boolean, default=False)   # also draw from the X-IT chapter item bank
        updated_at = db.Column(db.DateTime, default=utcnow)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    class MasteryOverride(db.Model):
        """Instructor decision for one student on one objective (``IT-5.1``) or chapter (``CH-5``)."""
        __tablename__ = 'mastery_override'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        target = db.Column(db.String(20), nullable=False)
        kind = db.Column(db.String(20), nullable=False)        # lock | unlock | force_review | waive
        note = db.Column(db.String(300), default='')
        active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=utcnow)
        created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
        cleared_at = db.Column(db.DateTime)
        cleared_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    class MasteryDecision(db.Model):
        """Log of every adaptive decision, with the reasons shown to the student and the evidence snapshot."""
        __tablename__ = 'mastery_decision'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        target = db.Column(db.String(20), nullable=False)
        action = db.Column(db.String(24), nullable=False)
        source = db.Column(db.String(12), default='engine')     # engine | instructor | helix | student
        required = db.Column(db.Boolean, default=False)
        status = db.Column(db.String(12), default='active')     # active | resolved | done | skipped | logged
        reasons_json = db.Column(db.Text, default='[]')
        evidence_json = db.Column(db.Text, default='{}')
        created_at = db.Column(db.DateTime, default=utcnow, index=True)
        resolved_at = db.Column(db.DateTime)
        actor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    class MasteryCheck(db.Model):
        """A review's practice questions or a chapter mastery check (test-out). Never graded."""
        __tablename__ = 'mastery_check'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        kind = db.Column(db.String(12), nullable=False)          # review | testout
        target = db.Column(db.String(20), nullable=False)        # objective or CH-<n>
        variant = db.Column(db.String(12), default='review')     # review | alt
        items_json = db.Column(db.Text, default='[]')            # served items, keys stay on the server
        answers_json = db.Column(db.Text, default='{}')
        correct = db.Column(db.Integer, default=0)
        total = db.Column(db.Integer, default=0)
        passed = db.Column(db.Boolean)
        skipped = db.Column(db.Boolean, default=False)
        started_at = db.Column(db.DateTime, default=utcnow)
        completed_at = db.Column(db.DateTime)

    _cache['m'] = SimpleNamespace(MasterySetting=MasterySetting, MasteryOverride=MasteryOverride,
                                  MasteryDecision=MasteryDecision, MasteryCheck=MasteryCheck)
    return _cache['m']
