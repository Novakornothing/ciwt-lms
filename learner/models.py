"""Additive tables for placement, the help desk queue, and the daily review deck."""
from datetime import datetime, timezone
from types import SimpleNamespace

_cache = {}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def define_models(db):
    if 'm' in _cache:
        return _cache['m']

    class PlacementAttempt(db.Model):
        """One placement per student per course. Reset deletes the row so they can take it again."""
        __tablename__ = 'placement_attempt'
        __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='uq_placement_user_course'),)
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        status = db.Column(db.String(12), nullable=False, default='active')  # active | complete
        state_json = db.Column(db.Text, default='{}')
        used_json = db.Column(db.Text, default='[]')
        current_id = db.Column(db.String(40))
        stop_reason = db.Column(db.String(20), default='')
        plan_json = db.Column(db.Text, default='{}')
        n_asked = db.Column(db.Integer, default=0)
        started_at = db.Column(db.DateTime, default=utcnow)
        completed_at = db.Column(db.DateTime)

    class PlacementOverride(db.Model):
        """Instructor replaces one chapter's placement result. Active row wins."""
        __tablename__ = 'placement_override'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, index=True)
        chapter = db.Column(db.Integer, nullable=False)
        kind = db.Column(db.String(20), nullable=False)  # tested_out | review
        note = db.Column(db.String(300), default='')
        active = db.Column(db.Boolean, default=True)
        created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
        created_at = db.Column(db.DateTime, default=utcnow)

    class HelpdeskAttempt(db.Model):
        """One working or finished ticket for a student."""
        __tablename__ = 'helpdesk_attempt'
        __table_args__ = (db.UniqueConstraint('user_id', 'ticket_id', name='uq_helpdesk_user_ticket'),)
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        course_code = db.Column(db.String(20), nullable=False, default='')
        ticket_id = db.Column(db.String(40), nullable=False, index=True)
        phase = db.Column(db.String(12), nullable=False, default='triage')  # triage|clarify|diagnose|close|done
        priority = db.Column(db.String(12), default='')
        asked_json = db.Column(db.Text, default='[]')
        steps_json = db.Column(db.Text, default='[]')
        note = db.Column(db.Text, default='')
        score_json = db.Column(db.Text, default='{}')
        total = db.Column(db.Integer)
        started_at = db.Column(db.DateTime, default=utcnow)
        finished_at = db.Column(db.DateTime)

    class DeckState(db.Model):
        """SM-2 state for one card and one user."""
        __tablename__ = 'deck_state'
        __table_args__ = (db.UniqueConstraint('user_id', 'card_id', name='uq_deck_user_card'),)
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        card_id = db.Column(db.String(40), nullable=False)
        ease = db.Column(db.Float, nullable=False, default=2.5)
        interval_days = db.Column(db.Integer, nullable=False, default=0)
        reps = db.Column(db.Integer, nullable=False, default=0)
        lapses = db.Column(db.Integer, nullable=False, default=0)
        due_on = db.Column(db.Date, nullable=False)
        last_on = db.Column(db.Date)

    class DeckProgress(db.Model):
        """Streak and today's sitting. One row per user."""
        __tablename__ = 'deck_progress'
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
        streak = db.Column(db.Integer, nullable=False, default=0)
        last_completed = db.Column(db.Date)
        session_day = db.Column(db.Date)
        session_json = db.Column(db.Text, default='[]')
        done_json = db.Column(db.Text, default='[]')

    _cache['m'] = SimpleNamespace(
        PlacementAttempt=PlacementAttempt,
        PlacementOverride=PlacementOverride,
        HelpdeskAttempt=HelpdeskAttempt,
        DeckState=DeckState,
        DeckProgress=DeckProgress,
    )
    return _cache['m']
