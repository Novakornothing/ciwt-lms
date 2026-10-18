"""First-run experience (pass 13).

Instructors see a "Set up your class" checklist on the class page until every item is reviewed or they hide it:
adaptivity, test-out, the Helix (attention) policy, certification practice items, releasing the first chapter
and, optionally, connecting an LMS over LTI 1.3. Each item shows the class's current setting, links to where it
is changed and can be marked reviewed. Students see a one-time introduction to their adaptive path and the daily
review on their class page; "Got it" hides it for good. Nothing here changes a setting by itself.
"""
from datetime import datetime, timezone

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

SETUP_ITEMS = ('adaptivity', 'helix', 'cert', 'release', 'lti')
STUDENT_INTRO = 'student_intro'


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def register(app, db, deps):
    from types import SimpleNamespace
    d = SimpleNamespace(**deps)

    class OnboardingFlag(db.Model):
        """One row per (user, class, key) the person has acknowledged. key: setup:<item>, setup:hidden, student_intro."""
        __tablename__ = 'onboarding_flag'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), index=True)
        key = db.Column(db.String(40), nullable=False)
        done_at = db.Column(db.DateTime, default=utcnow)
        __table_args__ = (db.UniqueConstraint('user_id', 'section_id', 'key', name='uq_onboarding_flag'),)

    def flags(user_id, section_id):
        return {f.key for f in OnboardingFlag.query.filter_by(user_id=user_id, section_id=section_id)}

    def set_flag(user_id, section_id, key):
        if not OnboardingFlag.query.filter_by(user_id=user_id, section_id=section_id, key=key).first():
            db.session.add(OnboardingFlag(user_id=user_id, section_id=section_id, key=key))

    def _lti_linked(section_id):
        try:
            return bool(db.session.execute(db.text('SELECT count(*) FROM lti_context WHERE section_id = :s'),
                                           {'s': section_id}).scalar())
        except Exception:
            db.session.rollback()
            return False

    def setup_checklist(section, user):
        """Items with the class's current state, for staff on the class page. None when hidden."""
        if not section or getattr(user, 'role', None) not in ('instructor', 'admin'):
            return None
        done = flags(user.id, section.id)
        if 'setup:hidden' in done:
            return None
        mx = d.mastery_settings(section.id)
        hx = d.HelixSectionSetting.query.filter_by(section_id=section.id).first()
        helix_on = hx.enabled if hx is not None else True
        mods = d.Module.query.filter_by(course_id=section.course_id).order_by(d.Module.order).all()
        released = [m for m in mods if d.ContentRelease.query.filter_by(section_id=section.id, content_type='module',
                                                                         content_id=m.id, user_id=None, is_active=True).first()]
        mastery = url_for('mastery_class', section_id=section.id) + '#mxSetH'
        items = [
            {'key': 'adaptivity', 'title': 'Adaptive path',
             'state': ('On' if mx['enabled'] else 'Off') + ' · mastery checks (test-out) ' + ('on' if mx['testout'] else 'off'),
             'help': 'Students get short reviews when an objective needs one, and strong students can test out of a chapter. '
                     'Reviews and mastery checks are never graded.', 'url': mastery, 'link': 'Mastery settings'},
            {'key': 'helix', 'title': 'Helix attention policy',
             'state': 'Offered to students (opt-in, with consent)' if helix_on else 'Not offered in this class',
             'help': 'Helix is optional webcam-based reading attention. Students must consent; it only adds optional review '
                     'offers and never affects grades.', 'url': url_for('helix.instructor_attention', section_id=section.id),
             'link': 'Attention settings'},
            {'key': 'cert', 'title': 'Certification practice items',
             'state': 'Included (pending SME review)' if mx['cert_items'] else 'Not used',
             'help': 'With this on, reviews and daily practice can also use certification practice items aligned to the same '
                     'objective. They have not yet been reviewed by a subject-matter expert.', 'url': mastery,
             'link': 'Mastery settings'},
            {'key': 'release', 'title': 'Release the first chapter',
             'state': f'{len(released)} of {len(mods)} chapters released',
             'help': 'Students see a chapter, its check and its labs once it is released.',
             'url': url_for('instructor_section', section_id=section.id) + '#content', 'link': 'Chapters', 'auto': bool(released)},
            {'key': 'lti', 'title': 'Connect your LMS (optional)',
             'state': 'Linked to an LMS course' if _lti_linked(section.id) else 'Not connected — optional',
             'help': 'If your college uses Canvas, Moodle, Blackboard or Brightspace, LTI 1.3 can launch lessons and send '
                     'scores back. Skip this if you use this site on its own.', 'url': url_for('instructor_lti', section_id=section.id),
             'link': 'LMS connection', 'optional': True},
        ]
        for it in items:
            it['done'] = f"setup:{it['key']}" in done or bool(it.get('auto'))
        n_done = sum(1 for it in items if it['done'])
        return {'items': items, 'done': n_done, 'total': len(items), 'complete': n_done == len(items)}

    def student_intro(section, user):
        if not section or getattr(user, 'role', None) != 'student':
            return None
        if STUDENT_INTRO in flags(user.id, None):
            return None
        mx = d.mastery_settings(section.id)
        return {'adaptive': mx['enabled'], 'testout': mx['testout'],
                'mastery_url': url_for('mastery_student', section_id=section.id),
                'daily_url': url_for('mastery_daily', section_id=section.id),
                'plan_url': url_for('mastery_plan', section_id=section.id)}

    @login_required
    def onboarding_setup(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role not in ('instructor', 'admin') or (
                current_user.role != 'admin' and not d.can_access_section(current_user, section)):
            abort(403)
        key = request.form.get('item', '')
        if key == 'hide':
            set_flag(current_user.id, section.id, 'setup:hidden')
            flash('Setup checklist hidden for this class. The settings stay where they are.', 'info')
        elif key == 'show':
            OnboardingFlag.query.filter_by(user_id=current_user.id, section_id=section.id, key='setup:hidden').delete()
        elif key in SETUP_ITEMS:
            set_flag(current_user.id, section.id, f'setup:{key}')
        else:
            abort(400)
        db.session.commit()
        return redirect(url_for('instructor_section', section_id=section.id) + '#setup', code=303)

    @login_required
    def onboarding_student_intro():
        if current_user.role != 'student':
            abort(403)
        set_flag(current_user.id, None, STUDENT_INTRO)
        db.session.commit()
        nxt = request.form.get('next') or ''
        if not (nxt.startswith('/student/') and '//' not in nxt):
            nxt = url_for('student_dashboard')
        return redirect(nxt, code=303)

    app.add_url_rule('/instructor/section/<int:section_id>/setup', 'onboarding_setup', onboarding_setup, methods=['POST'])
    app.add_url_rule('/student/intro/done', 'onboarding_student_intro', onboarding_student_intro, methods=['POST'])

    @app.context_processor
    def _onboarding_ctx():
        return {'onboarding_setup_checklist': setup_checklist, 'onboarding_student_intro': student_intro}

    return {'Flag': OnboardingFlag, 'setup_checklist': setup_checklist, 'student_intro': student_intro}
