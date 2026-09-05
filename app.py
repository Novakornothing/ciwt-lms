"""
CIWT Learning Management System
Demo-ready prototype — proprietary curriculum aligned to public exam domains
(original instructional content).
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, Response, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from collections import defaultdict
import json
import csv
from io import StringIO, BytesIO
import shutil
import random
import os
from pathlib import Path
import re
from lessons import APLUS as APLUS_LESSONS, NETPLUS as NETPLUS_LESSONS
from question_bank import tests_aplus, tests_netplus
from interactive_labs import list_labs, get_lab, fresh_state, run_command, prompt_for, complete_command, labs_for_module, labs_for_lesson, labs_for_course
from alignment import domains_for_course
from aschool import BLOCKS as ASCHOOL_BLOCKS, CSCHOOL_COMMS, CSCHOOL_SYS, outline_stats, all_eos

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ciwt-lms-demo-key-change-in-production')


@app.context_processor
def inject_interactive_labs():
    """Make all live labs available in every template (curriculum, class, nav)."""
    try:
        return {'all_interactive_labs': list_labs()}
    except Exception:
        return {'all_interactive_labs': []}
_base = os.path.dirname(os.path.abspath(__file__))
_default_db = os.path.join(_base, 'ciwt_lms.db')
db_path = os.environ.get('DATABASE_URL', 'sqlite:///' + _default_db)
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    test_attempts = db.relationship('TestAttempt', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    modules = db.relationship('Module', backref='course', lazy=True, order_by='Module.order')
    knowledge_tests = db.relationship('KnowledgeTest', backref='course', lazy=True)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)  # chapter overview
    estimated_minutes = db.Column(db.Integer, default=30)
    quizzes = db.relationship('Quiz', backref='module', lazy=True)
    lessons = db.relationship('Lesson', backref='module', lazy=True, order_by='Lesson.order')


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)
    estimated_minutes = db.Column(db.Integer, default=30)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    questions = db.Column(db.Text)
    is_ungraded = db.Column(db.Boolean, default=True)


class KnowledgeTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    questions = db.Column(db.Text)
    passing_score = db.Column(db.Integer, default=80)
    time_limit_minutes = db.Column(db.Integer, default=60)
    order = db.Column(db.Integer, default=1)


class ClassSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_students = db.Column(db.Integer, default=25)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    course = db.relationship('Course')
    instructor = db.relationship('User', foreign_keys=[instructor_id])
    enrollments = db.relationship('Enrollment', backref='section', lazy=True)
    releases = db.relationship('ContentRelease', backref='section', lazy=True)


class CourseInstructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course = db.relationship('Course', backref='instructor_links')
    user = db.relationship('User', backref='course_links')


class SectionInstructorAccess(db.Model):
    """Instructors who may open a class: primary lead plus any previous leads after reassignment."""
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    section = db.relationship('ClassSection', backref='instructor_access')
    user = db.relationship('User')


class EORecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    eo_id = db.Column(db.String(40), nullable=False, index=True)
    done_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User')


class AuditEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.String(20))
    action = db.Column(db.String(80), nullable=False)
    detail = db.Column(db.String(400))
    path = db.Column(db.String(200))
    ip = db.Column(db.String(64))
    user = db.relationship('User')


class TimeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    kind = db.Column(db.String(20), nullable=False)  # study | teaching
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('knowledge_test.id'))
    seconds = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    user = db.relationship('User')
    lesson = db.relationship('Lesson')
    quiz = db.relationship('Quiz')
    test = db.relationship('KnowledgeTest')


class CurriculumTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('knowledge_test.id'))
    category = db.Column(db.String(40), default='content')  # content | error | request | other
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    quoted_text = db.Column(db.Text)  # selected curriculum passage
    status = db.Column(db.String(20), default='open')  # open | in_progress | resolved | closed
    admin_notes = db.Column(db.Text)
    resolution = db.Column(db.String(40))  # fixed_content | declined | duplicate | other
    fixed_at = db.Column(db.DateTime)
    fixed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', foreign_keys=[user_id])
    fixed_by = db.relationship('User', foreign_keys=[fixed_by_id])
    course = db.relationship('Course')
    section = db.relationship('ClassSection')
    lesson = db.relationship('Lesson')
    quiz = db.relationship('Quiz')
    test = db.relationship('KnowledgeTest')


class CurriculumChangeLog(db.Model):
    """Shared curriculum edits push to every class on that course."""
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('curriculum_ticket.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    summary = db.Column(db.String(300), nullable=False)
    before_excerpt = db.Column(db.Text)
    after_excerpt = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ticket = db.relationship('CurriculumTicket', backref='change_logs')
    lesson = db.relationship('Lesson')
    admin = db.relationship('User')


class StaffMessage(db.Model):
    """Student ↔ instructor/admin messaging only (no student-to-student)."""
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('staff_message.id'))  # root id; null = root
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    section = db.relationship('ClassSection')
    replies = db.relationship(
        'StaffMessage',
        backref=db.backref('root', remote_side=[id]),
        foreign_keys=[thread_id],
    )


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress_percent = db.Column(db.Float, default=0.0)


class ContentRelease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # module | test | quiz
    content_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # None = whole class
    is_active = db.Column(db.Boolean, default=False)
    available_from = db.Column(db.DateTime)
    available_until = db.Column(db.DateTime)
    activated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    activated_at = db.Column(db.DateTime)


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answers = db.Column(db.Text)
    score = db.Column(db.Float)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    quiz = db.relationship('Quiz')


class TestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('knowledge_test.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    answers = db.Column(db.Text)
    score = db.Column(db.Float)
    passed = db.Column(db.Boolean)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    test = db.relationship('KnowledgeTest')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



def _section_course_id(section_id):
    sec = ClassSection.query.get(section_id) if section_id else None
    return sec.course_id if sec else None


def _student_in_course(course_id, within_seconds=180):
    """True if at least one student has study activity on this course recently."""
    if not course_id:
        return False
    cutoff = datetime.utcnow() - timedelta(seconds=within_seconds)
    section_ids = [s.id for s in ClassSection.query.filter_by(course_id=course_id).all()]
    if not section_ids:
        return False
    row = (
        TimeLog.query.filter(
            TimeLog.kind == 'study',
            TimeLog.section_id.in_(section_ids),
            TimeLog.ended_at.isnot(None),
            TimeLog.ended_at >= cutoff,
        ).first()
    )
    return row is not None


def _activity_rank():
    """course_id / section_id -> latest activity timestamp for sorting."""
    course_ts, section_ts = {}, {}
    for row in TimeLog.query.order_by(TimeLog.started_at.desc()).limit(400).all():
        when = row.ended_at or row.started_at
        if not when:
            continue
        if row.section_id:
            section_ts.setdefault(row.section_id, when)
            sec = ClassSection.query.get(row.section_id)
            if sec:
                course_ts.setdefault(sec.course_id, when)
    return course_ts, section_ts

def grant_section_instructor_access(section_id, user_id, primary=False):
    """Ensure an instructor can open this class. Primary = current lead instructor."""
    if not section_id or not user_id:
        return
    row = SectionInstructorAccess.query.filter_by(section_id=section_id, user_id=user_id).first()
    if not row:
        row = SectionInstructorAccess(section_id=section_id, user_id=user_id, is_primary=bool(primary))
        db.session.add(row)
    elif primary:
        row.is_primary = True
    if primary:
        # Only one primary lead at a time
        for other in SectionInstructorAccess.query.filter_by(section_id=section_id, is_primary=True).all():
            if other.user_id != user_id:
                other.is_primary = False


def instructor_course_ids(user_id):
    """Courses an instructor is assigned to, plus courses of sections they can access."""
    ids = {row.course_id for row in CourseInstructor.query.filter_by(user_id=user_id).all()}
    for sec in ClassSection.query.filter_by(instructor_id=user_id).all():
        ids.add(sec.course_id)
    access_sids = [
        r.section_id for r in SectionInstructorAccess.query.filter_by(user_id=user_id).all()
    ]
    if access_sids:
        for sec in ClassSection.query.filter(ClassSection.id.in_(access_sids)).all():
            ids.add(sec.course_id)
    return list(ids)


def instructor_can_access_section(user, section):
    if not user or not section:
        return False
    if user.role == 'admin':
        return True
    if user.role != 'instructor':
        return False
    if section.instructor_id == user.id:
        return True
    if SectionInstructorAccess.query.filter_by(section_id=section.id, user_id=user.id).first():
        return True
    return CourseInstructor.query.filter_by(course_id=section.course_id, user_id=user.id).first() is not None


def instructor_accessible_sections(user, course_id=None, active_only=True):
    """Sections the instructor may open (current lead or retained prior access)."""
    if not user:
        return []
    if user.role == 'admin':
        q = ClassSection.query
        if course_id:
            q = q.filter_by(course_id=course_id)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.order_by(ClassSection.name).all()
    access_ids = {
        r.section_id for r in SectionInstructorAccess.query.filter_by(user_id=user.id).all()
    }
    q = ClassSection.query.filter(
        db.or_(
            ClassSection.instructor_id == user.id,
            ClassSection.id.in_(access_ids or [0]),
        )
    )
    if course_id:
        q = q.filter_by(course_id=course_id)
    if active_only:
        q = q.filter_by(is_active=True)
    return q.order_by(ClassSection.name).all()


@app.context_processor
def inject_acting_role():
    role = ''
    if current_user.is_authenticated:
        role = current_user.role
        if current_user.role == 'admin':
            role = session.get('view_as') or 'admin'
    return {'acting_role': role}


@app.route('/admin/view-as/<role>')
@login_required
def admin_view_as(role):
    if current_user.role != 'admin':
        flash('Only an administrator can switch work mode.', 'danger')
        return redirect(url_for('index'))
    if role not in ('admin', 'instructor'):
        flash('Choose admin or instructor.', 'warning')
        return redirect(url_for('admin_dashboard'))
    session['view_as'] = role
    flash(f'Working as {role}. Your account is still an administrator.', 'success')
    if role == 'instructor':
        return redirect(url_for('instructor_dashboard'))
    return redirect(url_for('admin_dashboard'))


@app.context_processor
def inject_staff_nav():
    """Populate the left rail with classes for staff and enrolled sections for students."""
    empty = {'staff_nav_sections': [], 'staff_nav_courses': [], 'student_nav_sections': []}
    try:
        if not current_user.is_authenticated:
            return empty
        if current_user.role == 'student':
            sections = ClassSection.query.join(Enrollment).filter(
                Enrollment.user_id == current_user.id,
                ClassSection.is_active == True,
            ).order_by(ClassSection.name).all()
            return {
                'staff_nav_sections': [],
                'staff_nav_courses': [],
                'student_nav_sections': sections,
                'fmt_seconds': _fmt_seconds,
            }
        if current_user.role not in ('instructor', 'admin'):
            return empty
        if current_user.role == 'admin':
            sections = ClassSection.query.filter_by(is_active=True).order_by(ClassSection.name).all()
            courses = Course.query.order_by(Course.title).all()
        else:
            sections = instructor_accessible_sections(current_user, active_only=True)
            course_ids = instructor_course_ids(current_user.id)
            if course_ids:
                courses = Course.query.filter(Course.id.in_(course_ids)).order_by(Course.title).all()
            else:
                courses = []
        course_ts, section_ts = _activity_rank()
        sections = sorted(
            sections,
            key=lambda s: (section_ts.get(s.id) or datetime.min, s.name or ''),
            reverse=True,
        )
        courses = sorted(
            courses,
            key=lambda c: (course_ts.get(c.id) or datetime.min, c.title or ''),
            reverse=True,
        )
        return {
            'staff_nav_sections': sections,
            'staff_nav_courses': courses,
            'student_nav_sections': [],
            'fmt_seconds': _fmt_seconds,
        }
    except Exception:
        return empty


def _release_window_ok(release):
    if not release or not release.is_active:
        return False
    now = datetime.now()
    if release.available_from and now < release.available_from:
        return False
    if release.available_until and now > release.available_until:
        return False
    return True


def is_content_available(section_id, content_type, content_id, user_id=None):
    """Class-wide release OR a student-specific grant."""
    q = ContentRelease.query.filter_by(
        section_id=section_id, content_type=content_type, content_id=content_id, is_active=True
    )
    class_rel = q.filter(ContentRelease.user_id.is_(None)).first()
    if _release_window_ok(class_rel):
        return True
    if user_id:
        stu_rel = q.filter_by(user_id=user_id).first()
        if _release_window_ok(stu_rel):
            return True
    return False


def get_student_sections(user):
    return ClassSection.query.join(Enrollment).filter(
        Enrollment.user_id == user.id, ClassSection.is_active == True
    ).all()


def role_required(*roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return decorator



def _broad_category(q):
    """Map question metadata to a broad performance category."""
    if q.get('category'):
        return q['category']
    lo = (q.get('lo') or '') + ' ' + (q.get('lo_text') or '') + ' ' + (q.get('text') or '')
    s = lo.lower()
    if any(k in s for k in ('security', 'malware', 'mfa', 'phishing', 'encrypt', 'least privilege', 'ransomware')):
        return 'Security'
    if any(k in s for k in ('vlan', 'routing', 'dhcp', 'dns', 'tcp', 'udp', 'osi', 'subnet', 'wireless', 'wan', 'switch', 'gateway', 'ip address', 'network')):
        return 'Networking'
    if any(k in s for k in ('windows', 'linux', 'macos', 'install', 'sfc', 'dism', 'profile', 'software', 'application', 'cli')):
        return 'Operating Systems & Software'
    if any(k in s for k in ('ticket', 'document', 'change', 'policy', 'backup', 'checklist', 'professional', 'intake', 'escalat')):
        return 'Operations & Professionalism'
    if any(k in s for k in ('cpu', 'ram', 'memory', 'motherboard', 'storage', 'nvme', 'sata', 'psu', 'power', 'post', 'firmware', 'uefi', 'laptop', 'print', 'hardware')):
        return 'Hardware & Devices'
    return 'Core Knowledge'


def _terminal_objective(q):
    if q.get('to'):
        return q['to']
    lo = q.get('lo') or 'TO'
    lo_text = q.get('lo_text') or 'Curriculum terminal objective'
    return f"{lo}: {lo_text}"


def _category_breakdown(questions, answers):
    """Return list of {category, correct, total, pct} sorted by name."""
    buckets = {}
    for i, q in enumerate(questions):
        cat = _broad_category(q)
        buckets.setdefault(cat, {'correct': 0, 'total': 0})
        buckets[cat]['total'] += 1
        ans = answers.get(str(i))
        if ans == q.get('correct'):
            buckets[cat]['correct'] += 1
    out = []
    for cat, v in sorted(buckets.items()):
        pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
        out.append({'category': cat, 'correct': v['correct'], 'total': v['total'], 'pct': pct})
    return out


def _subcategory(q):
    """Finer topic under a broad category — prefer LO text, else infer from stem."""
    lo_text = (q.get('lo_text') or '').strip()
    # Skip ultra-generic labels so we get real topic splits
    generic = {
        'core technical knowledge', 'core knowledge', 'general', 'fundamentals',
        'chapter fundamentals', 'progress check',
    }
    if lo_text and lo_text.lower() not in generic:
        return lo_text[:100]
    focus = (q.get('focus') or '').strip()
    if focus and focus.lower() not in generic:
        return focus[:100]
    s = ((q.get('text') or '') + ' ' + (q.get('lo') or '')).lower()
    rules = [
        (('nvme', 'pcie', 'm.2', 'sata ssd', 'hdd', 'raid'), 'Storage & drives'),
        (('ddr', 'ram', 'memory', 'dual-channel'), 'Memory'),
        (('cpu', 'socket', 'lga', 'heatsink', 'thermal'), 'CPU & cooling'),
        (('motherboard', 'atx', 'form factor', 'chipset', 'uefi', 'bios', 'post'), 'Motherboard & firmware'),
        (('psu', 'watt', '24-pin', 'power supply'), 'Power'),
        (('print', 'toner', 'laser', 'inkjet'), 'Printers'),
        (('laptop', 'mobile', 'battery'), 'Laptops & mobile'),
        (('ipconfig', 'ping', 'tracert', 'nslookup', 'netstat'), 'Network tools'),
        (('dns', 'dhcp', 'gateway', 'apipa', 'subnet', 'ipv4', 'ipv6', 'nat'), 'IP addressing & services'),
        (('vlan', 'switch', 'router', 'ospf', 'bgp', 'routing'), 'Switching & routing'),
        (('wifi', 'wi-fi', 'wpa', 'ssid', 'wireless', '802.11'), 'Wireless'),
        (('tcp', 'udp', 'port', 'https', 'ssh', 'rdp', 'firewall'), 'Ports & transport'),
        (('cable', 'rj-45', 'fiber', 'cat6', 't568', 'crimp'), 'Cabling & media'),
        (('windows', 'linux', 'macos', 'ntfs', 'chmod', 'registry', 'group policy'), 'Operating systems'),
        (('malware', 'mfa', 'phishing', 'encrypt', 'bitlocker', 'password', 'antivirus'), 'Security controls'),
        (('ticket', 'change management', 'backup', 'documentation', 'escalate'), 'Operations & process'),
        (('driver', 'device manager', 'install', 'image', 'deployment'), 'Software & imaging'),
    ]
    for keys, label in rules:
        if any(k in s for k in keys):
            return label
    lo = (q.get('lo') or '').strip()
    if lo and lo not in ('LO-GEN',):
        return lo
    return 'General topics'


def _subcategory_breakdown(questions, answers, parent_category=None):
    """Subtopic rollup; optional filter to one broad category."""
    buckets = {}
    for i, q in enumerate(questions):
        cat = _broad_category(q)
        if parent_category and cat != parent_category:
            continue
        sub = _subcategory(q)
        buckets.setdefault(sub, {'correct': 0, 'total': 0, 'category': cat})
        buckets[sub]['total'] += 1
        ans = answers.get(str(i))
        if ans == q.get('correct'):
            buckets[sub]['correct'] += 1
    out = []
    for sub, v in sorted(buckets.items(), key=lambda x: x[1]['correct'] / x[1]['total'] if x[1]['total'] else 0):
        pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
        out.append({
            'subcategory': sub,
            'category': v['category'],
            'correct': v['correct'],
            'total': v['total'],
            'pct': pct,
        })
    return out


def _class_test_stats(test_id, section_id):
    attempts = TestAttempt.query.filter_by(
        test_id=test_id, section_id=section_id
    ).filter(TestAttempt.completed_at.isnot(None)).all()
    scores = [a.score for a in attempts if a.score is not None]
    if not scores:
        return {
            'n': 0, 'mean': None, 'median': None, 'high': None, 'low': None,
            'pass_rate': None, 'attempts': attempts, 'category_avg': [],
        }
    scores_sorted = sorted(scores)
    mid = len(scores_sorted) // 2
    if len(scores_sorted) % 2:
        median = scores_sorted[mid]
    else:
        median = round((scores_sorted[mid - 1] + scores_sorted[mid]) / 2, 1)
    test = KnowledgeTest.query.get(test_id)
    questions = json.loads(test.questions)
    # aggregate categories across attempts
    cat_totals = {}
    for att in attempts:
        ans = json.loads(att.answers or '{}')
        for row in _category_breakdown(questions, ans):
            cat_totals.setdefault(row['category'], {'correct': 0, 'total': 0})
            cat_totals[row['category']]['correct'] += row['correct']
            cat_totals[row['category']]['total'] += row['total']
    category_avg = []
    for cat, v in sorted(cat_totals.items()):
        pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
        category_avg.append({'category': cat, 'pct': pct, 'correct': v['correct'], 'total': v['total']})
    passed = sum(1 for a in attempts if a.passed)
    return {
        'n': len(scores),
        'mean': round(sum(scores) / len(scores), 1),
        'median': median,
        'high': max(scores),
        'low': min(scores),
        'pass_rate': round(passed / len(attempts) * 100, 1) if attempts else None,
        'attempts': attempts,
        'category_avg': category_avg,
    }


def _instructor_historical_average(instructor_id):
    """Mean score across all completed attempts in sections taught by this instructor."""
    sections = ClassSection.query.filter_by(instructor_id=instructor_id).all()
    sids = [s.id for s in sections]
    if not sids:
        return None, 0
    attempts = TestAttempt.query.filter(
        TestAttempt.section_id.in_(sids),
        TestAttempt.completed_at.isnot(None),
        TestAttempt.score.isnot(None),
    ).all()
    if not attempts:
        return None, 0
    return round(sum(a.score for a in attempts) / len(attempts), 1), len(attempts)


def compute_item_analysis(test_id, section_id=None, section_ids=None,
                           instructor_id=None, year=None, quarter=None):
    """NAVEDTRA-aligned test item analysis.

    Primary techniques (NETC / NAVEDTRA instructional testing guidance):
      - Difficulty index (P) = Nc / N
      - Discrimination index (d) using upper vs lower ~27% by total score
      - Effectiveness of alternatives (distractor analysis)

    For pass mark >= 80%, acceptable P band is treated as about 0.60–0.95
    (adjusted from the 0.50–0.90 band used when minimum pass is ~63%).
    Low throughput: full sample is used (entire N), matching low-volume guidance.
    """
    test = KnowledgeTest.query.get_or_404(test_id)
    questions = json.loads(test.questions or '[]')
    q = TestAttempt.query.filter_by(test_id=test_id)
    if section_id:
        q = q.filter_by(section_id=section_id)
    elif section_ids is not None:
        if not section_ids:
            attempts = []
            q = None
        else:
            q = q.filter(TestAttempt.section_id.in_(section_ids))
    if q is not None:
        attempts = q.filter(TestAttempt.completed_at.isnot(None)).all()
    else:
        attempts = []
    if attempts and (instructor_id or year or quarter):
        filtered = []
        for att in attempts:
            when = att.completed_at or att.started_at
            if year and when and when.year != int(year):
                continue
            if quarter and when:
                qlabel = f"Q{((when.month - 1) // 3) + 1}"
                if qlabel != str(quarter).upper():
                    continue
            if instructor_id:
                sec = ClassSection.query.get(att.section_id)
                if not sec or sec.instructor_id != int(instructor_id):
                    continue
            filtered.append(att)
        attempts = filtered

    n = len(attempts)
    # Upper / lower ~27% by total score (NAVEDTRA discrimination groups)
    scored = [(a, a.score if a.score is not None else 0) for a in attempts]
    scored.sort(key=lambda x: x[1])
    if n >= 4:
        k = max(1, int(round(n * 0.27)))
        low_group = scored[:k]
        high_group = scored[-k:]
    elif n >= 2:
        mid = n // 2
        low_group = scored[:mid]
        high_group = scored[mid:]
    else:
        low_group = high_group = scored
    low_set = {id(a) for a, _ in low_group}
    high_set = {id(a) for a, _ in high_group}
    # Avoid double-counting the same attempt in both groups when N is tiny
    if n >= 2 and low_set & high_set:
        high_set -= low_set

    pass_mark = int(test.passing_score or 80)
    # Acceptable difficulty band (P) adjusted for high pass scores
    if pass_mark >= 80:
        p_lo, p_hi = 0.60, 0.95
    elif pass_mark >= 70:
        p_lo, p_hi = 0.55, 0.93
    else:
        p_lo, p_hi = 0.50, 0.90

    analysis = []
    for i, qdata in enumerate(questions):
        correct_key = qdata.get('correct')
        options = list(qdata.get('options') or [])
        counts = {opt: 0 for opt in options}
        high_correct = low_correct = high_n = low_n = 0
        correct_count = 0
        answered = 0
        for att in attempts:
            ans = json.loads(att.answers or '{}')
            chosen = ans.get(str(i))
            if chosen is None:
                continue
            answered += 1
            if chosen in counts:
                counts[chosen] += 1
            is_right = chosen == correct_key
            if is_right:
                correct_count += 1
            if id(att) in high_set:
                high_n += 1
                if is_right:
                    high_correct += 1
            if id(att) in low_set:
                low_n += 1
                if is_right:
                    low_correct += 1

        # Difficulty index P = Nc / N (use full sample N per NAVEDTRA; omitters count as not correct)
        denom = n if n else answered
        P = (correct_count / denom) if denom else 0.0
        pct_correct = round(P * 100, 1)
        wrong_count = max(0, answered - correct_count)

        # Discrimination index d = Ph - Pl
        Ph = (high_correct / high_n) if high_n else 0.0
        Pl = (low_correct / low_n) if low_n else 0.0
        d = round(Ph - Pl, 3)

        if d >= 0.40:
            disc_label = 'Excellent'
        elif d >= 0.30:
            disc_label = 'Good'
        elif d >= 0.20:
            disc_label = 'Acceptable'
        elif d >= 0.10:
            disc_label = 'Marginal'
        elif d >= 0:
            disc_label = 'Poor'
        else:
            disc_label = 'Negative / reverse'

        # Difficulty label vs NAVEDTRA acceptable band
        if P > p_hi:
            diff_label = 'Too easy'
            p_status = 'Out of band (easy)'
        elif P < p_lo:
            diff_label = 'Too hard'
            p_status = 'Out of band (hard)'
        else:
            if P >= 0.85:
                diff_label = 'Easy (in band)'
            elif P >= 0.70:
                diff_label = 'Moderate (in band)'
            else:
                diff_label = 'Challenging (in band)'
            p_status = 'In band'

        # Effectiveness of alternatives
        option_stats = []
        for opt in options:
            c = counts.get(opt, 0)
            pct = (c / answered * 100) if answered else 0.0
            is_correct = opt == correct_key
            if is_correct:
                effectiveness = 'Answer key'
                note = 'Keyed correct response'
            else:
                pull = (c / wrong_count * 100) if wrong_count else 0.0
                if answered >= 5 and pct < 5:
                    effectiveness = 'Non-functional'
                    note = f'Chosen by {pct:.0f}% overall — ineffective alternative; revise or replace.'
                elif pull >= 40:
                    effectiveness = 'Strong distractor'
                    note = f'Selected by {pull:.0f}% of those who missed — highly attractive alternative.'
                elif pull >= 15:
                    effectiveness = 'Functional distractor'
                    note = f'Selected by {pull:.0f}% of those who missed — working alternative.'
                else:
                    effectiveness = 'Weak distractor'
                    note = f'Selected by only {pull:.0f}% of those who missed — weak alternative.'
            option_stats.append({
                'option': opt,
                'count': c,
                'pct': round(pct, 1),
                'is_correct': is_correct,
                'effectiveness': effectiveness,
                'note': note,
                'pct_of_wrong': round((c / wrong_count * 100) if (wrong_count and not is_correct) else 0, 1),
            })

        omit = n - answered
        flags = []
        if p_status.startswith('Out'):
            flags.append(f'P out of band ({P:.2f})')
        if d < 0:
            flags.append('Negative discrimination (d)')
        elif d < 0.10 and n >= 10:
            flags.append('Low discrimination (d)')
        if any(o['effectiveness'] == 'Non-functional' for o in option_stats):
            flags.append('Non-functional alternative')
        if any(o['effectiveness'] == 'Strong distractor' for o in option_stats):
            flags.append('Strong distractor present')
        # 50% missed rule for low throughput
        if n and n < 30 and P <= 0.50:
            flags.append('50% missed rule — review item')

        analysis.append({
            'index': i + 1,
            'text': qdata.get('text', ''),
            'lo': qdata.get('lo', ''),
            'lo_text': qdata.get('lo_text', ''),
            'to': qdata.get('to') or '',
            'category': qdata.get('category') or _broad_category(qdata),
            'domain': qdata.get('domain') or qdata.get('category') or '',
            'correct': correct_key,
            'answered': answered,
            'omit': omit,
            'omit_pct': round((omit / n * 100) if n else 0, 1),
            'correct_count': correct_count,
            'pct_correct': pct_correct,
            'P': round(P, 3),
            'difficulty_index': round(P, 3),
            'options': option_stats,
            'difficulty': diff_label,
            'p_status': p_status,
            'p_band': f'{p_lo:.2f}–{p_hi:.2f}',
            'discrimination': d,
            'disc_label': disc_label,
            'p_high': round(Ph * 100, 1),
            'p_low': round(Pl * 100, 1),
            'high_n': high_n,
            'low_n': low_n,
            'flags': flags,
        })

    scores = sorted(a.score for a in attempts if a.score is not None)

    def _median(vals):
        if not vals:
            return None
        m = len(vals) // 2
        if len(vals) % 2:
            return round(vals[m], 1)
        return round((vals[m - 1] + vals[m]) / 2, 1)

    mean = round(sum(scores) / len(scores), 1) if scores else None
    variance = (sum((s - mean) ** 2 for s in scores) / len(scores)) if scores and mean is not None else 0

    lo_map = {}
    for item in analysis:
        key = item.get('lo') or item.get('domain') or 'Unmapped'
        lo_map.setdefault(key, {'lo': key, 'text': item.get('lo_text') or '', 'n': 0, 'pct_sum': 0, 'hard': 0})
        lo_map[key]['n'] += 1
        lo_map[key]['pct_sum'] += item['pct_correct']
        if item['P'] < p_lo:
            lo_map[key]['hard'] += 1
    lo_rows = []
    for row in lo_map.values():
        lo_rows.append({
            'lo': row['lo'],
            'text': row['text'],
            'n': row['n'],
            'avg_pct': round(row['pct_sum'] / row['n'], 1) if row['n'] else 0,
            'hard': row['hard'],
        })
    lo_rows.sort(key=lambda x: x['avg_pct'])
    flagged = [it for it in analysis if it['flags']]
    in_band = sum(1 for it in analysis if it.get('p_status') == 'In band')
    summary = {
        'n_attempts': n,
        'mean_score': mean,
        'median_score': _median(scores),
        'high_score': max(scores) if scores else None,
        'low_score': min(scores) if scores else None,
        'stdev': round(variance ** 0.5, 1) if scores else None,
        'pass_rate': round(sum(1 for a in attempts if a.passed) / n * 100, 1) if n else None,
        'passing_score': test.passing_score,
        'n_items': len(analysis),
        'n_flagged': len(flagged),
        'lo_rows': lo_rows,
        'easy': sum(1 for it in analysis if 'easy' in (it.get('difficulty') or '').lower()),
        'medium': sum(1 for it in analysis if 'moderate' in (it.get('difficulty') or '').lower() or 'challenging' in (it.get('difficulty') or '').lower()),
        'hard': sum(1 for it in analysis if 'hard' in (it.get('difficulty') or '').lower()),
        'p_band': f'{p_lo:.2f}–{p_hi:.2f}',
        'items_in_band': in_band,
        'items_out_of_band': len(analysis) - in_band,
        'navedtra': True,
        'group_method': 'Upper/lower ~27% by total score' if n >= 4 else 'Split sample (small N)',
    }
    return test, analysis, summary


# ==================== ROUTES ====================

def _lms_host():
    """Apex/www of novakornothing.com = marketing page. Render and ciwt = LMS."""
    host = (request.host or "").split(":")[0].lower()
    if host in ("novakornothing.com", "www.novakornothing.com"):
        return False
    return True


@app.route('/')
def index():
    if not _lms_host():
        return render_template('landing.html')
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        if current_user.role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        return redirect(url_for('student_dashboard'))
    return render_template('index.html')


def audit(action, detail=''):
    try:
        ev = AuditEvent(
            user_id=current_user.id if getattr(current_user, 'is_authenticated', False) else None,
            role=getattr(current_user, 'role', None) if getattr(current_user, 'is_authenticated', False) else None,
            action=action[:80],
            detail=(detail or '')[:400],
            path=(request.path or '')[:200],
            ip=(request.headers.get('X-Forwarded-For') or request.remote_addr or '')[:64],
        )
        db.session.add(ev)
        db.session.commit()
    except Exception:
        db.session.rollback()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            audit('login', user.email)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    audit('logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/healthz')
def healthz():
    return jsonify({
        'ok': True,
        'service': 'ciwt-lms',
        'time': datetime.utcnow().isoformat() + 'Z',
    })


def _eo_done(user_id=None):
    uid = user_id or getattr(current_user, 'id', None)
    if not uid:
        return set()
    try:
        return {r.eo_id for r in EORecord.query.filter_by(user_id=uid).all()}
    except Exception:
        db.session.rollback()
        return set()


def _known_eo_ids():
    ids = set()
    for pack in (ASCHOOL_BLOCKS, CSCHOOL_COMMS, CSCHOOL_SYS):
        for b in pack:
            for e in b['eos']:
                ids.add(e['id'])
    return ids


@app.route('/convening')
@login_required
def convening_home():
    a = outline_stats(ASCHOOL_BLOCKS)
    c = outline_stats(CSCHOOL_COMMS)
    s = outline_stats(CSCHOOL_SYS)
    done = _eo_done()
    total_eos = a['eos'] + c['eos'] + s['eos']
    return render_template(
        'convening_home.html',
        a=a, c=c, s=s,
        done_n=len(done),
        total_eos=total_eos,
    )


@app.route('/aschool')
@login_required
def aschool_outline():
    return render_template(
        'aschool_outline.html',
        title='IT A-school outline',
        track='aschool',
        blocks=ASCHOOL_BLOCKS,
        stats=outline_stats(ASCHOOL_BLOCKS),
        done=_eo_done(),
    )


@app.route('/cschool/comms')
@login_required
def cschool_comms():
    return render_template(
        'aschool_outline.html',
        title='IT C-school — Communications',
        track='cschool_comms',
        blocks=CSCHOOL_COMMS,
        stats=outline_stats(CSCHOOL_COMMS),
        done=_eo_done(),
    )


@app.route('/cschool/sysadmin')
@login_required
def cschool_sysadmin():
    return render_template(
        'aschool_outline.html',
        title='IT C-school — Systems administrator',
        track='cschool_sys',
        blocks=CSCHOOL_SYS,
        stats=outline_stats(CSCHOOL_SYS),
        done=_eo_done(),
    )


@app.route('/aschool/eo/<eo_id>/toggle', methods=['POST'])
@login_required
def aschool_toggle_eo(eo_id):
    if eo_id not in _known_eo_ids():
        abort(404)
    rec = EORecord.query.filter_by(user_id=current_user.id, eo_id=eo_id).first()
    if rec:
        db.session.delete(rec)
    else:
        db.session.add(EORecord(user_id=current_user.id, eo_id=eo_id))
    db.session.commit()
    audit('eo_toggle', eo_id)
    nxt = request.form.get('next') or url_for('aschool_outline')
    return redirect(nxt + '#' + eo_id)


@app.route('/aschool/progress')
@login_required
def aschool_progress():
    if current_user.role not in ('admin', 'instructor'):
        flash('Progress roster is for instructors and admins.', 'warning')
        return redirect(url_for('aschool_outline'))
    eos = list(all_eos(ASCHOOL_BLOCKS)) + list(all_eos(CSCHOOL_COMMS)) + list(all_eos(CSCHOOL_SYS))
    students = User.query.filter_by(role='student').order_by(User.last_name).all()
    rows = []
    for s in students:
        done = _eo_done(s.id)
        rows.append({
            'user': s,
            'done': len(done),
            'total': len(eos),
            'pct': round(100 * len(done) / len(eos), 0) if eos else 0,
        })
    return render_template('aschool_progress.html', rows=rows, total=len(eos))


@app.route('/aschool/trainee-guide')
@login_required
def aschool_trainee_guide():
    stats = outline_stats()
    return render_template('aschool_guide.html', blocks=ASCHOOL_BLOCKS, stats=stats, generated=datetime.utcnow())


@app.route('/aschool/trainee-guide.txt')
@login_required
def aschool_trainee_guide_txt():
    lines = [
        'CIWT IT A-SCHOOL TRAINEE GUIDE',
        'Original CIWT material — not official NAVEDTRA / not CompTIA exam text.',
        f'Generated {datetime.utcnow().isoformat()}Z',
        '',
    ]
    stats = outline_stats()
    lines.append(f"{stats['blocks']} blocks · {stats['hours']} hours · {stats['eos']} EOs · {stats['with_lab']} with live labs")
    lines.append('')
    for b in ASCHOOL_BLOCKS:
        lines.append(f"{b['title']}  (weeks {b['week']}, {b['hours']} hrs)")
        lines.append(b['goal'])
        for e in b['eos']:
            tag = f"LAB {e['lab']}" if e.get('lab') else f"CHECK {e.get('check')}"
            lines.append(f"  - {e['text']}  [{tag}]")
        lines.append('')
    body = '\n'.join(lines)
    return Response(body, mimetype='text/plain', headers={
        'Content-Disposition': 'attachment; filename=CIWT-IT-A-School-Trainee-Guide.txt'
    })


def _accessible_course_ids():
    if current_user.role == 'admin':
        return [c.id for c in Course.query.all()]
    if current_user.role == 'instructor':
        secs = ClassSection.query.filter_by(instructor_id=current_user.id, is_active=True).all()
        ids = {s.course_id for s in secs}
        if not ids:
            return [c.id for c in Course.query.all()]
        return list(ids)
    secs = get_student_sections(current_user)
    return list({s.course_id for s in secs})


def _section_for_course(course_id):
    """Best section_id so search results can open curriculum."""
    if current_user.role == 'student':
        for s in get_student_sections(current_user):
            if s.course_id == course_id:
                return s
        return None
    if current_user.role == 'instructor':
        s = ClassSection.query.filter_by(
            course_id=course_id, instructor_id=current_user.id, is_active=True
        ).first()
        if not s and course_id in instructor_course_ids(current_user.id):
            s = ClassSection.query.filter_by(course_id=course_id, is_active=True).first()
        if s:
            return s
    return ClassSection.query.filter_by(course_id=course_id, is_active=True).first()


def _snippet(text, query, width=160):
    raw = re.sub(r'<[^>]+>', ' ', text or '')
    raw = re.sub(r'\s+', ' ', raw).strip()
    if not raw:
        return ''
    q = (query or '').lower()
    low = raw.lower()
    idx = low.find(q) if q else -1
    if idx < 0:
        return raw[:width] + ('…' if len(raw) > width else '')
    start = max(0, idx - 40)
    end = min(len(raw), idx + width)
    piece = raw[start:end]
    if start:
        piece = '…' + piece
    if end < len(raw):
        piece = piece + '…'
    return piece


@app.route('/search')
@login_required
def curriculum_search():
    q = (request.args.get('q') or '').strip()
    results = []
    course_ids = _accessible_course_ids()
    if q and course_ids:
        like = f'%{q}%'
        lessons = (
            Lesson.query.join(Module, Lesson.module_id == Module.id)
            .filter(Module.course_id.in_(course_ids))
            .filter(db.or_(Lesson.title.ilike(like), Lesson.content.ilike(like)))
            .order_by(Module.order, Lesson.order)
            .limit(40)
            .all()
        )
        seen = set()
        for lesson in lessons:
            module = lesson.module
            course = module.course
            section = _section_for_course(course.id)
            if not section:
                continue
            if current_user.role == 'student' and not is_content_available(section.id, 'module', module.id, current_user.id):
                # still list it but mark locked
                locked = True
            else:
                locked = False
            key = ('lesson', lesson.id)
            if key in seen:
                continue
            seen.add(key)
            results.append({
                'kind': 'Lesson',
                'title': lesson.title,
                'chapter': module.title,
                'course': course.title,
                'snippet': _snippet(lesson.content, q),
                'locked': locked,
                'url': url_for('view_lesson', section_id=section.id, module_id=module.id, lesson_id=lesson.id)
                if not locked else url_for('student_section', section_id=section.id),
            })
        modules = (
            Module.query.filter(Module.course_id.in_(course_ids))
            .filter(db.or_(Module.title.ilike(like), Module.content.ilike(like)))
            .order_by(Module.order)
            .limit(15)
            .all()
        )
        for module in modules:
            course = module.course
            section = _section_for_course(course.id)
            if not section:
                continue
            key = ('module', module.id)
            if key in seen:
                continue
            seen.add(key)
            locked = current_user.role == 'student' and not is_content_available(section.id, 'module', module.id, current_user.id)
            results.append({
                'kind': 'Chapter',
                'title': module.title,
                'chapter': course.title,
                'course': course.title,
                'snippet': _snippet(module.content, q),
                'locked': locked,
                'url': url_for('view_module', section_id=section.id, module_id=module.id)
                if not locked else url_for('student_section', section_id=section.id),
            })
        tests = (
            KnowledgeTest.query.filter(KnowledgeTest.course_id.in_(course_ids))
            .filter(KnowledgeTest.title.ilike(like))
            .order_by(KnowledgeTest.order)
            .limit(10)
            .all()
        )
        for test in tests:
            section = _section_for_course(test.course_id)
            if not section:
                continue
            if current_user.role in ('instructor', 'admin'):
                url = url_for('instructor_test_performance', section_id=section.id, test_id=test.id)
                locked = False
            else:
                locked = not is_content_available(section.id, 'test', test.id, current_user.id)
                url = url_for('take_test', section_id=section.id, test_id=test.id) if not locked else url_for('student_section', section_id=section.id)
            results.append({
                'kind': 'Test',
                'title': test.title,
                'chapter': test.course.title if test.course else '',
                'course': test.course.title if test.course else '',
                'snippet': test.description or 'Knowledge test',
                'locked': locked,
                'url': url,
            })
    return render_template('search.html', q=q, results=results)




@app.route('/messages')
@login_required
def messages_inbox():
    if current_user.role == 'student':
        threads = (
            StaffMessage.query.filter(
                StaffMessage.thread_id.is_(None),
                db.or_(
                    StaffMessage.sender_id == current_user.id,
                    StaffMessage.recipient_id == current_user.id,
                ),
            )
            .order_by(StaffMessage.created_at.desc())
            .all()
        )
        unread = StaffMessage.query.filter_by(recipient_id=current_user.id, is_read=False).count()
        return render_template('messages_inbox.html', threads=threads, unread=unread, mode='student')
    # instructor / admin
    if current_user.role == 'admin':
        threads = (
            StaffMessage.query.filter(StaffMessage.thread_id.is_(None))
            .order_by(StaffMessage.created_at.desc())
            .all()
        )
    else:
        threads = (
            StaffMessage.query.filter(
                StaffMessage.thread_id.is_(None),
                db.or_(
                    StaffMessage.sender_id == current_user.id,
                    StaffMessage.recipient_id == current_user.id,
                ),
            )
            .order_by(StaffMessage.created_at.desc())
            .all()
        )
    unread = StaffMessage.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    return render_template('messages_inbox.html', threads=threads, unread=unread, mode='staff')


@app.route('/messages/new', methods=['GET', 'POST'])
@login_required
def messages_new():
    if current_user.role == 'student':
        contacts = student_staff_contacts(current_user.id)
        enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
        sections = [ClassSection.query.get(e.section_id) for e in enrollments]
        sections = [s for s in sections if s]
    else:
        # staff composing to a student
        sections = ClassSection.query.filter_by(is_active=True).order_by(ClassSection.name).all()
        if current_user.role != 'admin':
            sections = [s for s in sections if instructor_can_access_section(current_user, s)]
        student_ids = set()
        for s in sections:
            for e in Enrollment.query.filter_by(section_id=s.id).all():
                student_ids.add(e.user_id)
        contacts = (
            User.query.filter(User.role == 'student', User.id.in_(student_ids or [0]))
            .order_by(User.last_name, User.first_name)
            .all()
        )
        if current_user.role == 'admin' and not contacts:
            contacts = User.query.filter_by(role='student').order_by(User.last_name, User.first_name).all()
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id', type=int)
        subject = (request.form.get('subject') or '').strip()
        body = (request.form.get('body') or '').strip()
        section_id = request.form.get('section_id') or None
        if not recipient_id or not can_message(current_user, recipient_id):
            flash('You can only message authorized instructors or admins.', 'danger')
            return redirect(url_for('messages_new'))
        if current_user.role == 'student':
            rec = User.query.get(recipient_id)
            if not rec or rec.role not in ('instructor', 'admin'):
                flash('Students cannot message other students.', 'danger')
                return redirect(url_for('messages_new'))
        if not subject or not body:
            flash('Subject and message are required.', 'warning')
            return redirect(url_for('messages_new'))
        msg = StaffMessage(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            section_id=int(section_id) if section_id else None,
            subject=subject[:200],
            body=body,
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent.', 'success')
        return redirect(url_for('messages_thread', msg_id=msg.id))
    rosters = {}
    if current_user.role != 'student':
        for s in sections:
            rows = []
            for e in Enrollment.query.filter_by(section_id=s.id).all():
                u = User.query.get(e.user_id)
                if u and u.role == 'student':
                    rows.append({
                        'id': u.id,
                        'name': u.full_name,
                        'email': u.email,
                    })
            rows.sort(key=lambda r: r['name'].lower())
            rosters[str(s.id)] = rows
        all_students = [
            {'id': u.id, 'name': u.full_name, 'email': u.email}
            for u in contacts
        ]
    else:
        all_students = [
            {'id': u.id, 'name': u.full_name, 'email': u.email, 'role': u.role}
            for u in contacts
        ]
    return render_template(
        'messages_new.html',
        contacts=contacts,
        sections=sections,
        rosters=rosters,
        all_students=all_students,
        pre_recipient=request.args.get('to', type=int),
        pre_section=request.args.get('section', type=int),
    )


@app.route('/messages/<int:msg_id>', methods=['GET', 'POST'])
@login_required
def messages_thread(msg_id):
    root = StaffMessage.query.get_or_404(msg_id)
    if root.thread_id:
        root = StaffMessage.query.get_or_404(root.thread_id)
    participants = {root.sender_id, root.recipient_id}
    allowed = current_user.id in participants or current_user.role == 'admin'
    if not allowed and current_user.role == 'instructor' and root.section_id:
        sec = ClassSection.query.get(root.section_id)
        if sec and instructor_can_access_section(current_user, sec):
            allowed = True
    if not allowed:
        flash('Access denied.', 'danger')
        return redirect(url_for('messages_inbox'))

    thread = [root] + (
        StaffMessage.query.filter_by(thread_id=root.id).order_by(StaffMessage.created_at).all()
    )
    # mark read for current user
    for m in thread:
        if m.recipient_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    if request.method == 'POST':
        body = (request.form.get('body') or '').strip()
        if not body:
            flash('Reply cannot be empty.', 'warning')
            return redirect(url_for('messages_thread', msg_id=root.id))
        # reply goes to the other party
        if current_user.id == root.sender_id:
            to_id = root.recipient_id
        else:
            to_id = root.sender_id
        # For admin viewing someone else's thread, reply as admin to the student
        if current_user.role == 'admin' and current_user.id not in participants:
            student = root.sender if root.sender.role == 'student' else root.recipient
            to_id = student.id
        if current_user.role == 'student' and User.query.get(to_id).role == 'student':
            flash('Students cannot message other students.', 'danger')
            return redirect(url_for('messages_thread', msg_id=root.id))
        if not can_message(current_user, to_id) and current_user.role not in ('admin', 'instructor'):
            flash('Not allowed.', 'danger')
            return redirect(url_for('messages_inbox'))
        reply = StaffMessage(
            thread_id=root.id,
            sender_id=current_user.id,
            recipient_id=to_id,
            section_id=root.section_id,
            subject=root.subject if root.subject.startswith('Re:') else f'Re: {root.subject}',
            body=body,
        )
        db.session.add(reply)
        db.session.commit()
        flash('Reply sent.', 'success')
        return redirect(url_for('messages_thread', msg_id=root.id))

    return render_template('messages_thread.html', root=root, thread=thread)



@app.route('/api/idle-challenge', methods=['GET', 'POST'])
@login_required
def idle_challenge():
    if current_user.role != 'student':
        return jsonify({'ok': True, 'skip': True})
    if request.method == 'GET':
        pool = []
        for qz in Quiz.query.all():
            try:
                items = json.loads(qz.questions or '[]')
            except Exception:
                continue
            for it in items:
                opts = it.get('options') or []
                text = it.get('text') or it.get('q')
                correct = it.get('correct')
                if text and opts and correct:
                    pool.append({'text': text, 'options': opts, 'correct': correct})
        if not pool:
            pool = [
                {'text': 'What is binary 00001010 in decimal?', 'options': ['8', '10', '12', '16'], 'correct': '10'},
                {'text': 'How many bits are in one byte?', 'options': ['4', '8', '16', '32'], 'correct': '8'},
                {'text': 'Which private IPv4 range is 192.168.0.0/16?', 'options': ['Loopback', 'APIPA', 'Private Class C space', 'Multicast'], 'correct': 'Private Class C space'},
            ]
        item = random.choice(pool)
        session['idle_answer'] = item['correct']
        return jsonify({
            'ok': True,
            'text': item['text'],
            'options': item['options'],
        })
    given = (request.get_json(silent=True) or {}).get('answer')
    expected = session.get('idle_answer')
    if expected is None:
        return jsonify({'ok': False, 'message': 'No challenge is open.'}), 400
    if given == expected:
        session.pop('idle_answer', None)
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'message': 'Incorrect. Try again or request a new question.'})



def student_staff_contacts(student_id):
    """Instructors and admins a student may message (never other students)."""
    contacts = {}
    for admin in User.query.filter_by(role='admin').all():
        contacts[admin.id] = admin
    enrs = Enrollment.query.filter_by(user_id=student_id).all()
    for e in enrs:
        sec = ClassSection.query.get(e.section_id)
        if not sec:
            continue
        if sec.instructor_id:
            u = User.query.get(sec.instructor_id)
            if u and u.role in ('instructor', 'admin'):
                contacts[u.id] = u
        for link in CourseInstructor.query.filter_by(course_id=sec.course_id).all():
            u = User.query.get(link.user_id)
            if u and u.role in ('instructor', 'admin'):
                contacts[u.id] = u
    return sorted(contacts.values(), key=lambda u: (u.last_name or '', u.first_name or ''))


def can_message(sender, recipient_id):
    """Enforce: students only to staff; staff to students (or other staff). Never student-student."""
    recipient = User.query.get(recipient_id)
    if not recipient:
        return False
    if sender.role == 'student':
        if recipient.role not in ('instructor', 'admin'):
            return False
        allowed = {u.id for u in student_staff_contacts(sender.id)}
        return recipient.id in allowed
    if sender.role in ('instructor', 'admin'):
        # staff may reply to students or message staff; not initiate random student-student
        return recipient.role in ('student', 'instructor', 'admin')
    return False


@app.route('/tickets')
@login_required
def tickets_list():
    tickets = (
        CurriculumTicket.query.filter_by(user_id=current_user.id)
        .order_by(CurriculumTicket.created_at.desc())
        .all()
    )
    courses = Course.query.order_by(Course.title).all()
    return render_template('tickets.html', tickets=tickets, courses=courses)


@app.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def tickets_new():
    courses = Course.query.order_by(Course.title).all()
    pre_course = request.args.get('course_id', type=int)
    pre_lesson = request.args.get('lesson_id', type=int)
    pre_section = request.args.get('section_id', type=int)
    pre_quiz = request.args.get('quiz_id', type=int)
    pre_test = request.args.get('test_id', type=int)
    pre_quote = (request.args.get('quote') or '').strip()
    lesson = Lesson.query.get(pre_lesson) if pre_lesson else None
    quiz = Quiz.query.get(pre_quiz) if pre_quiz else None
    test = KnowledgeTest.query.get(pre_test) if pre_test else None
    if quiz and not pre_course and quiz.module_id:
        mod = Module.query.get(quiz.module_id)
        if mod:
            pre_course = mod.course_id
    if test and not pre_course:
        pre_course = test.course_id
    if request.method == 'POST':
        subject = (request.form.get('subject') or '').strip()
        body = (request.form.get('body') or '').strip()
        quote = (request.form.get('quoted_text') or '').strip()
        category = request.form.get('category') or 'content'
        if category not in ('content', 'error', 'request', 'other'):
            category = 'content'
        if not subject:
            flash('Subject is required.', 'warning')
            return redirect(request.url)
        if not body and not quote:
            flash('Add a short note or keep the highlighted text.', 'warning')
            return redirect(request.url)
        if not body and quote:
            body = f'Highlighted passage needs review:\n\n"{quote}"'
        course_id = request.form.get('course_id') or None
        section_id = request.form.get('section_id') or None
        lesson_id = request.form.get('lesson_id') or None
        quiz_id = request.form.get('quiz_id') or None
        test_id = request.form.get('test_id') or None
        t = CurriculumTicket(
            user_id=current_user.id,
            course_id=int(course_id) if course_id else None,
            section_id=int(section_id) if section_id else None,
            lesson_id=int(lesson_id) if lesson_id else None,
            quiz_id=int(quiz_id) if quiz_id else None,
            test_id=int(test_id) if test_id else None,
            category=category,
            subject=subject[:200],
            body=body,
            quoted_text=quote or None,
            status='open',
        )
        db.session.add(t)
        db.session.commit()
        flash('Ticket submitted. An administrator will review it.', 'success')
        return redirect(url_for('tickets_list'))
    return render_template(
        'ticket_new.html',
        courses=courses,
        pre_course=pre_course,
        pre_lesson=pre_lesson,
        pre_section=pre_section,
        pre_quote=pre_quote,
        lesson=lesson,
        quiz=quiz,
        test=test,
        pre_quiz=pre_quiz,
        pre_test=pre_test,
    )


@app.route('/live-labs')
@app.route('/labs')
@login_required
def interactive_labs_index():
    """In-browser Windows / switch / router CLI simulators."""
    return render_template('interactive_labs_index.html', labs=list_labs())


@app.route('/labs/verify')
@login_required
def interactive_labs_verify():
    """Run built-in sequences for every lab (instructor/admin)."""
    if current_user.role not in ('admin', 'instructor'):
        flash('Lab verify is for instructors and admins.', 'warning')
        return redirect(url_for('interactive_labs_index'))
    from interactive_labs import verify_all_labs
    ok, report = verify_all_labs()
    return render_template('interactive_labs_verify.html', ok=ok, report=report)


@app.route('/labs/<lab_id>')
@login_required
def interactive_lab(lab_id):
    lab = get_lab(lab_id)
    if not lab:
        abort(404)
    key_s = f'lab_state_{lab_id}'
    key_d = f'lab_done_{lab_id}'
    if key_s not in session:
        session[key_s] = fresh_state(lab_id)
        session[key_d] = []
    state = session[key_s]
    audit('lab_open', lab_id)
    if lab.get('kind') == 'win11gui':
        return render_template('win11_gui_lab.html', lab=lab)
    return render_template(
        'interactive_lab.html',
        lab=lab,
        prompt=prompt_for(lab, state),
    )


@app.route('/labs/<lab_id>/complete', methods=['POST'])
@login_required
def interactive_lab_complete(lab_id):
    if not get_lab(lab_id):
        return jsonify({'error': 'unknown lab'}), 404
    payload = request.get_json(silent=True) or {}
    key_s = f'lab_state_{lab_id}'
    state = session.get(key_s) or {}
    mode = payload.get('mode') or state.get('mode') or 'user'
    return jsonify(complete_command(lab_id, payload.get('partial') or '', mode=mode))


@app.route('/labs/<lab_id>/cmd', methods=['POST'])
@login_required
def interactive_lab_cmd(lab_id):
    lab = get_lab(lab_id)
    if not lab:
        return jsonify({'error': 'unknown lab'}), 404
    key_s = f'lab_state_{lab_id}'
    key_d = f'lab_done_{lab_id}'
    state = session.get(key_s) or fresh_state(lab_id)
    done = session.get(key_d) or []
    payload = request.get_json(silent=True) or {}
    command = payload.get('command') or ''
    result, state, done = run_command(lab_id, state, done, command)
    session[key_s] = state
    session[key_d] = done
    session.modified = True
    return jsonify(result)


@app.route('/labs/<lab_id>/reset', methods=['POST'])
@login_required
def interactive_lab_reset(lab_id):
    if not get_lab(lab_id):
        return jsonify({'error': 'unknown lab'}), 404
    session[f'lab_state_{lab_id}'] = fresh_state(lab_id)
    session[f'lab_done_{lab_id}'] = []
    session.modified = True
    return jsonify({'ok': True})


@app.route('/admin/tickets')
@login_required
@role_required('admin')
def admin_tickets():
    status = request.args.get('status') or 'all'
    q = CurriculumTicket.query.order_by(CurriculumTicket.created_at.desc())
    if status != 'all':
        q = q.filter_by(status=status)
    tickets = q.limit(200).all()
    counts = {
        'open': CurriculumTicket.query.filter_by(status='open').count(),
        'in_progress': CurriculumTicket.query.filter_by(status='in_progress').count(),
        'resolved': CurriculumTicket.query.filter_by(status='resolved').count(),
        'closed': CurriculumTicket.query.filter_by(status='closed').count(),
        'all': CurriculumTicket.query.count(),
    }
    return render_template('admin_tickets.html', tickets=tickets, status=status, counts=counts)


@app.route('/admin/tickets/<int:ticket_id>')
@login_required
@role_required('admin')
def admin_ticket_detail(ticket_id):
    t = CurriculumTicket.query.get_or_404(ticket_id)
    lesson = t.lesson
    if not lesson and t.lesson_id:
        lesson = Lesson.query.get(t.lesson_id)
    modules = []
    if t.course_id:
        modules = Module.query.filter_by(course_id=t.course_id).order_by(Module.order).all()
    elif lesson and lesson.module:
        modules = Module.query.filter_by(course_id=lesson.module.course_id).order_by(Module.order).all()
    lessons_by_module = {
        m.id: Lesson.query.filter_by(module_id=m.id).order_by(Lesson.order).all()
        for m in modules
    }
    view_section = t.section
    course_id = t.course_id
    if lesson and lesson.module:
        course_id = lesson.module.course_id
    if not view_section and course_id:
        view_section = ClassSection.query.filter_by(course_id=course_id, is_active=True).first()
        if not view_section:
            view_section = ClassSection.query.filter_by(course_id=course_id).first()
    return render_template(
        'admin_ticket_detail.html',
        ticket=t,
        lesson=lesson,
        modules=modules,
        lessons_by_module=lessons_by_module,
        courses=Course.query.order_by(Course.title).all(),
        view_section=view_section,
    )


@app.route('/admin/tickets/<int:ticket_id>/update', methods=['POST'])
@login_required
@role_required('admin')
def admin_ticket_update(ticket_id):
    t = CurriculumTicket.query.get_or_404(ticket_id)
    status = request.form.get('status') or t.status
    if status in ('open', 'in_progress', 'resolved', 'closed'):
        t.status = status
        if status in ('resolved', 'closed') and not t.fixed_at:
            t.fixed_at = datetime.utcnow()
            t.fixed_by_id = current_user.id
            if not t.resolution:
                t.resolution = request.form.get('resolution') or 'other'
    notes = request.form.get('admin_notes')
    if notes is not None:
        t.admin_notes = notes
    # optional: link a different lesson while reviewing
    link_lesson = request.form.get('link_lesson_id')
    if link_lesson:
        t.lesson_id = int(link_lesson)
        les = Lesson.query.get(int(link_lesson))
        if les and les.module:
            t.course_id = les.module.course_id
    t.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'Ticket #{t.id} updated.', 'success')
    return redirect(url_for('admin_ticket_detail', ticket_id=t.id))


@app.route('/admin/tickets/<int:ticket_id>/fix-content', methods=['POST'])
@login_required
@role_required('admin')
def admin_ticket_fix_content(ticket_id):
    """Edit shared lesson content once; every class on that course sees the update."""
    t = CurriculumTicket.query.get_or_404(ticket_id)
    lesson_id = request.form.get('lesson_id') or t.lesson_id
    if not lesson_id:
        flash('Link a lesson before applying a content fix.', 'warning')
        return redirect(url_for('admin_ticket_detail', ticket_id=t.id))
    lesson = Lesson.query.get_or_404(int(lesson_id))
    new_content = request.form.get('content')
    if new_content is None:
        flash('No content submitted.', 'warning')
        return redirect(url_for('admin_ticket_detail', ticket_id=t.id))
    old = lesson.content or ''
    if old.strip() == new_content.strip():
        flash('Content unchanged. Ticket status not updated.', 'info')
        return redirect(url_for('admin_ticket_detail', ticket_id=t.id))
    lesson.content = new_content
    t.lesson_id = lesson.id
    if lesson.module:
        t.course_id = lesson.module.course_id
    summary = (request.form.get('change_summary') or '').strip() or f'Fixed curriculum from ticket #{t.id}: {t.subject}'
    log = CurriculumChangeLog(
        ticket_id=t.id,
        lesson_id=lesson.id,
        module_id=lesson.module_id,
        course_id=lesson.module.course_id if lesson.module else t.course_id,
        admin_id=current_user.id,
        summary=summary[:300],
        before_excerpt=old[:800],
        after_excerpt=new_content[:800],
    )
    t.status = 'resolved'
    t.resolution = 'fixed_content'
    t.fixed_at = datetime.utcnow()
    t.fixed_by_id = current_user.id
    t.admin_notes = (request.form.get('admin_notes') or t.admin_notes or '').strip() or (
        'Curriculum updated. Change applies to every class using this course.'
    )
    t.updated_at = datetime.utcnow()
    db.session.add(log)
    db.session.commit()
    flash(
        f'Lesson “{lesson.title}” updated for all classes. Ticket #{t.id} marked resolved (fixed).',
        'success',
    )
    return redirect(url_for('admin_ticket_detail', ticket_id=t.id))


@app.route('/admin/curriculum-log')
@login_required
@role_required('admin')
def admin_curriculum_log():
    logs = CurriculumChangeLog.query.order_by(CurriculumChangeLog.created_at.desc()).limit(200).all()
    closed = (
        CurriculumTicket.query.filter(CurriculumTicket.status.in_(('resolved', 'closed')))
        .order_by(CurriculumTicket.updated_at.desc())
        .limit(200)
        .all()
    )
    return render_template('admin_curriculum_log.html', logs=logs, closed_tickets=closed)


def _fmt_seconds(sec):
    sec = int(sec or 0)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f'{h}h {m:02d}m'
    return f'{m}m {s:02d}s'


@app.route('/time/study', methods=['POST'])
@login_required
def time_study_heartbeat():
    data = request.get_json(silent=True) or {}
    lesson_id = data.get('lesson_id')
    section_id = data.get('section_id')
    seconds = max(0, min(int(data.get('seconds') or 0), 120))
    if not lesson_id or seconds <= 0:
        return jsonify({'ok': False}), 400
    log = TimeLog(
        user_id=current_user.id,
        kind='study',
        section_id=int(section_id) if section_id else None,
        lesson_id=int(lesson_id),
        seconds=seconds,
        started_at=datetime.utcnow() - timedelta(seconds=seconds),
        ended_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'ok': True})


def _open_teaching_log(user_id):
    return TimeLog.query.filter_by(
        user_id=user_id, kind='teaching', ended_at=None
    ).order_by(TimeLog.started_at.desc()).first()


def _teaching_payload(log, extra=None):
    course_id = _section_course_id(log.section_id) if log else None
    present = _student_in_course(course_id) if course_id else False
    wall = 0
    if log and log.started_at:
        wall = int((datetime.utcnow() - log.started_at).total_seconds())
        wall = max(wall, int(log.seconds or 0))
    data = {
        'ok': True,
        'running': bool(log),
        'session_id': log.id if log else None,
        'section_id': log.section_id if log else None,
        'seconds': int(log.seconds or 0) if log else 0,
        'wall_seconds': wall,
        'students_present': present,
        'started_at': log.started_at.isoformat() + 'Z' if log and log.started_at else None,
        'label': _fmt_seconds(int(log.seconds or 0) if log else 0),
    }
    if extra:
        data.update(extra)
    return data


@app.route('/time/teaching/status')
@login_required
def time_teaching_status():
    if current_user.role not in ('instructor', 'admin'):
        return jsonify({'ok': False}), 403
    return jsonify(_teaching_payload(_open_teaching_log(current_user.id)))


@app.route('/time/teaching/start', methods=['POST'])
@login_required
def time_teaching_start():
    if current_user.role not in ('instructor', 'admin'):
        return jsonify({'ok': False}), 403
    data = request.get_json(silent=True) or {}
    section_id = data.get('section_id')
    section_id = int(section_id) if section_id else None
    if not section_id:
        return jsonify({'ok': False, 'error': 'Pick a class first.'}), 400
    section = ClassSection.query.get(section_id)
    if not section or (
        current_user.role != 'admin' and not instructor_can_access_section(current_user, section)
    ):
        return jsonify({'ok': False, 'error': 'No access to that class.'}), 403
    open_log = _open_teaching_log(current_user.id)
    if open_log:
        open_log.section_id = section_id
        db.session.commit()
        return jsonify(_teaching_payload(open_log))
    log = TimeLog(
        user_id=current_user.id, kind='teaching', seconds=0,
        section_id=section_id, started_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(_teaching_payload(log))


@app.route('/time/teaching/stop', methods=['POST'])
@login_required
def time_teaching_stop():
    if current_user.role not in ('instructor', 'admin'):
        return jsonify({'ok': False}), 403
    open_log = _open_teaching_log(current_user.id)
    if not open_log:
        return jsonify({'ok': True, 'running': False, 'seconds': 0, 'label': '0m'})
    data = request.get_json(silent=True) or {}
    client_sec = max(0, min(int(data.get('seconds') or 0), 12 * 3600))
    wall = int((datetime.utcnow() - (open_log.started_at or datetime.utcnow())).total_seconds())
    open_log.seconds = max(int(open_log.seconds or 0), client_sec, max(0, wall))
    open_log.ended_at = datetime.utcnow()
    db.session.commit()
    return jsonify({
        'ok': True,
        'running': False,
        'seconds': open_log.seconds,
        'label': _fmt_seconds(open_log.seconds),
    })


@app.route('/time/teaching/ping', methods=['POST'])
@login_required
def time_teaching_ping():
    if current_user.role not in ('instructor', 'admin'):
        return jsonify({'ok': False}), 403
    open_log = _open_teaching_log(current_user.id)
    if not open_log:
        return jsonify({'ok': False, 'error': 'No open session.', 'running': False}), 400
    data = request.get_json(silent=True) or {}
    elapsed = max(0, min(int(data.get('elapsed') or 15), 60))
    open_log.seconds = int(open_log.seconds or 0) + elapsed
    wall = int((datetime.utcnow() - (open_log.started_at or datetime.utcnow())).total_seconds())
    if wall > open_log.seconds:
        open_log.seconds = wall
    db.session.commit()
    present = _student_in_course(_section_course_id(open_log.section_id))
    return jsonify(_teaching_payload(open_log, {
        'credited': True,
        'students_present': present,
        'message': (
            'Students in course.' if present
            else 'Session running. No student heartbeat in this course right now.'
        ),
    }))


# ---------- Student ----------

@app.route('/student')
@login_required
def student_dashboard():
    if current_user.role not in ('student', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    sections = get_student_sections(current_user)
    progress = {}
    for s in sections:
        enr = Enrollment.query.filter_by(user_id=current_user.id, section_id=s.id).first()
        progress[s.id] = enr.progress_percent if enr else 0
    return render_template('student_dashboard.html', sections=sections, progress=progress)


@app.route('/student/section/<int:section_id>')
@login_required
def student_section(section_id):
    section = ClassSection.query.get_or_404(section_id)
    enr = Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first()
    if not enr and current_user.role != 'admin':
        flash('You are not enrolled in this section.', 'danger')
        return redirect(url_for('student_dashboard'))
    modules = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).all()
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    quizzes_by_module = {
        m.id: Quiz.query.filter_by(module_id=m.id).all()
        for m in modules
    }
    available_modules = []
    for m in modules:
        avail = is_content_available(section_id, 'module', m.id, current_user.id)
        quizzes = Quiz.query.filter_by(module_id=m.id).all()
        available_modules.append({
            'module': m,
            'available': avail,
            'quizzes': quizzes,
            'labs': labs_for_module(m),
        })
    available_tests = []
    for t in tests:
        avail = is_content_available(section_id, 'test', t.id, current_user.id)
        attempts = TestAttempt.query.filter_by(
            user_id=current_user.id, test_id=t.id, section_id=section_id
        ).order_by(TestAttempt.completed_at.desc()).all()
        available_tests.append({'test': t, 'available': avail, 'attempts': attempts})
    return render_template(
        'student_section.html',
        section=section,
        modules=available_modules,
        tests=available_tests,
        enrollment=enr,
        course_labs=labs_for_course(section.course),
    )


@app.route('/student/module/<int:section_id>/<int:module_id>')
@login_required
def view_module(section_id, module_id):
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'module', module_id, current_user.id):
        flash('This module is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    module = Module.query.get_or_404(module_id)
    lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
    quizzes = Quiz.query.filter_by(module_id=module_id).all()
    # If structured lessons exist, show chapter hub; else legacy single page
    chapter_labs = labs_for_module(module)
    if lessons:
        return render_template(
            'chapter.html', module=module, lessons=lessons,
            section_id=section_id, quizzes=quizzes, chapter_labs=chapter_labs
        )
    return render_template(
        'module.html', module=module, section_id=section_id, quizzes=quizzes,
        chapter_labs=chapter_labs,
    )


@app.route('/student/module/<int:section_id>/<int:module_id>/lesson/<int:lesson_id>')
@login_required
def view_lesson(section_id, module_id, lesson_id):
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'module', module_id, current_user.id):
        flash('This module is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    module = Module.query.get_or_404(module_id)
    lesson = Lesson.query.filter_by(id=lesson_id, module_id=module_id).first_or_404()
    lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
    # prev/next
    prev_l = next_l = None
    for i, L in enumerate(lessons):
        if L.id == lesson.id:
            if i > 0:
                prev_l = lessons[i - 1]
            if i + 1 < len(lessons):
                next_l = lessons[i + 1]
            break
    quizzes = Quiz.query.filter_by(module_id=module_id).all()
    return render_template(
        'lesson.html', module=module, lesson=lesson, lessons=lessons,
        prev_l=prev_l, next_l=next_l, section_id=section_id, quizzes=quizzes,
        chapter_labs=labs_for_module(module),
        lesson_labs=labs_for_lesson(module, lesson),
    )


@app.route('/student/quiz/<int:section_id>/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(section_id, quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    module = Module.query.get(quiz.module_id)
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'module', module.id, current_user.id):
        flash('This quiz is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    questions = json.loads(quiz.questions)
    if request.method == 'POST':
        answers = {}
        correct = 0
        # Aggregate by focus area — never expose item stems/keys to the student
        focus_map = {}
        for i, q in enumerate(questions):
            ans = request.form.get(f'q{i}')
            answers[str(i)] = ans
            is_ok = ans == q.get('correct')
            if is_ok:
                correct += 1
            focus = (
                q.get('focus')
                or q.get('lo_text')
                or q.get('category')
                or q.get('lo')
                or 'Core topics in this chapter'
            )
            tip = q.get('study_tip') or (
                'Revisit the related chapter lessons, practice the ordered checks, '
                'and be able to explain the idea to a peer without looking at notes.'
            )
            keywords = q.get('keywords') or []
            if isinstance(keywords, str):
                keywords = [k.strip() for k in keywords.split(',') if k.strip()]
            bucket = focus_map.setdefault(focus, {
                'focus': focus,
                'wrong': 0,
                'total': 0,
                'tips': [],
                'keywords': set(),
            })
            bucket['total'] += 1
            if not is_ok:
                bucket['wrong'] += 1
                if tip and tip not in bucket['tips']:
                    bucket['tips'].append(tip)
            for kw in keywords:
                bucket['keywords'].add(kw.lower())
            # derive keywords from focus text for lesson matching
            for token in re.findall(r'[a-z0-9]{4,}', focus.lower()):
                bucket['keywords'].add(token)

        score = (correct / len(questions)) * 100 if questions else 0
        attempt = QuizAttempt(
            user_id=current_user.id, quiz_id=quiz_id,
            answers=json.dumps(answers), score=score
        )
        db.session.add(attempt)
        enr = Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first()
        if enr:
            enr.progress_percent = min(100.0, enr.progress_percent + 5)
        db.session.commit()

        lessons = Lesson.query.filter_by(module_id=quiz.module_id).order_by(Lesson.order).all()
        # also pull neighboring modules in the same course for broader study links
        sibling_lessons = lessons
        if module and module.course_id:
            mod_ids = [m.id for m in Module.query.filter_by(course_id=module.course_id).all()]
            sibling_lessons = Lesson.query.filter(Lesson.module_id.in_(mod_ids)).order_by(Lesson.order).all()

        focus_areas = []
        for bucket in focus_map.values():
            if bucket['wrong'] == 0:
                continue
            matched = []
            kws = bucket['keywords']
            for les in sibling_lessons:
                title_l = (les.title or '').lower()
                content_snip = (les.content or '')[:400].lower()
                if any(kw in title_l or kw in content_snip for kw in kws):
                    matched.append(les)
            if not matched:
                matched = lessons[:3]  # fall back to this chapter's lessons
            focus_areas.append({
                'focus': bucket['focus'],
                'wrong': bucket['wrong'],
                'total': bucket['total'],
                'tips': bucket['tips'][:3],
                'lessons': matched[:5],
            })
        focus_areas.sort(key=lambda x: (-x['wrong'], x['focus']))

        return render_template(
            'quiz_results.html',
            quiz=quiz, section_id=section_id, module_id=quiz.module_id,
            score=score, correct=correct, total=len(questions),
            focus_areas=focus_areas, module=module,
        )
    mod = Module.query.get(quiz.module_id)
    return render_template('quiz.html', quiz=quiz, questions=questions, section_id=section_id, course_id=mod.course_id if mod else None)


@app.route('/student/test/<int:section_id>/<int:test_id>', methods=['GET', 'POST'])
@login_required
def take_test(section_id, test_id):
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'test', test_id, current_user.id):
        flash('This knowledge test is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    test = KnowledgeTest.query.get_or_404(test_id)
    questions = json.loads(test.questions or '[]')
    limit_min = int(test.time_limit_minutes or 75)

    # Open (in-progress) attempt for this student
    open_attempt = TestAttempt.query.filter_by(
        user_id=current_user.id, test_id=test_id, section_id=section_id,
    ).filter(TestAttempt.completed_at.is_(None)).order_by(TestAttempt.started_at.desc()).first()

    if request.method == 'POST':
        if not open_attempt:
            open_attempt = TestAttempt(
                user_id=current_user.id, test_id=test_id, section_id=section_id,
                started_at=datetime.utcnow(),
            )
            db.session.add(open_attempt)
            db.session.flush()
        # Enforce time limit server-side (small grace for network)
        elapsed = (datetime.utcnow() - (open_attempt.started_at or datetime.utcnow())).total_seconds()
        timed_out = request.form.get('timed_out') == '1'
        if elapsed > (limit_min * 60) + 90:
            timed_out = True
        answers = {}
        correct = 0
        for i, q in enumerate(questions):
            ans = request.form.get(f'q{i}')
            answers[str(i)] = ans
            if ans is not None and ans == q.get('correct'):
                correct += 1
        score = (correct / len(questions)) * 100 if questions else 0
        passed = score >= test.passing_score
        categories = _category_breakdown(questions, answers)
        open_attempt.answers = json.dumps(answers)
        open_attempt.score = score
        open_attempt.passed = passed
        open_attempt.completed_at = datetime.utcnow()
        db.session.commit()
        audit('test_submit', f'test={test_id} section={section_id} score={score:.0f}')
        if timed_out:
            flash('Time expired — your answers were submitted and graded automatically.', 'info')
        return render_template(
            'test_results.html',
            test=test, section_id=section_id, score=score, passed=passed,
            correct=correct, total=len(questions), categories=categories,
            attempt_id=open_attempt.id, timed_out=timed_out,
        )

    # GET — start or resume attempt; compute remaining seconds for timer
    if not open_attempt:
        open_attempt = TestAttempt(
            user_id=current_user.id, test_id=test_id, section_id=section_id,
            started_at=datetime.utcnow(),
        )
        db.session.add(open_attempt)
        db.session.commit()
    started = open_attempt.started_at or datetime.utcnow()
    remaining = max(0, int(limit_min * 60 - (datetime.utcnow() - started).total_seconds()))
    if remaining <= 0:
        # Time already over (e.g. left page open) — force grade empty/partial if they re-enter
        open_attempt.answers = open_attempt.answers or json.dumps({})
        open_attempt.score = open_attempt.score if open_attempt.score is not None else 0
        open_attempt.passed = False
        open_attempt.completed_at = datetime.utcnow()
        db.session.commit()
        flash('Time expired — this attempt was closed.', 'info')
        return redirect(url_for('student_section', section_id=section_id))
    return render_template(
        'test.html', test=test, questions=questions, section_id=section_id,
        course_id=test.course_id, remaining_seconds=remaining, attempt_id=open_attempt.id,
    )


# ---------- Instructor ----------

@app.route('/instructor')
@login_required
def instructor_dashboard():
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    if current_user.role == 'admin':
        sections = ClassSection.query.filter_by(is_active=True).order_by(ClassSection.name).all()
    else:
        cids = instructor_course_ids(current_user.id)
        sections = ClassSection.query.filter(
            ClassSection.is_active.is_(True),
            db.or_(
                ClassSection.instructor_id == current_user.id,
                ClassSection.course_id.in_(cids or [0]),
            ),
        ).order_by(ClassSection.name).all()
        courses = Course.query.filter(Course.id.in_(cids)).order_by(Course.title).all() if cids else []
    if current_user.role == 'admin':
        courses = Course.query.order_by(Course.title).all()
    sections = sorted(sections, key=lambda s: ((s.course.title if s.course else ''), s.name or ''))
    return render_template('instructor_dashboard.html', sections=sections, courses=courses)


@app.route('/instructor/section/<int:section_id>')
@login_required
def instructor_section(section_id):
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role != 'admin' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    modules = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).all()
    quizzes_by_module = {
        m.id: Quiz.query.filter_by(module_id=m.id).all()
        for m in modules
    }
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    enrollments = (
        Enrollment.query.filter_by(section_id=section_id)
        .join(User).order_by(User.last_name, User.first_name).all()
    )
    all_rels = ContentRelease.query.filter_by(section_id=section_id).all()
    releases = {}
    student_releases = {}
    for r in all_rels:
        if r.user_id is None:
            releases[(r.content_type, r.content_id)] = r
        else:
            student_releases.setdefault((r.content_type, r.content_id), []).append(r)
    # Students not yet enrolled (for add dropdown)
    enrolled_ids = {e.user_id for e in enrollments}
    available_students = User.query.filter_by(role='student').order_by(User.last_name).all()
    available_students = [s for s in available_students if s.id not in enrolled_ids]
    instructors = User.query.filter_by(role='instructor').order_by(User.last_name, User.first_name).all()
    course_instructor_links = CourseInstructor.query.filter_by(course_id=section.course_id).all()
    study_totals = defaultdict(int)
    for row in TimeLog.query.filter_by(kind='study', section_id=section.id).all():
        study_totals[row.user_id] += row.seconds or 0
    teach_totals = defaultdict(int)
    instructor_ids = {section.instructor_id}
    for link in course_instructor_links:
        instructor_ids.add(link.user_id)
    for row in TimeLog.query.filter(
        TimeLog.kind == 'teaching',
        TimeLog.user_id.in_(list(instructor_ids) or [0]),
    ).all():
        teach_totals[row.user_id] += row.seconds or 0
        if row.ended_at is None and row.started_at:
            teach_totals[row.user_id] += int((datetime.utcnow() - row.started_at).total_seconds())
    return render_template(
        'instructor_section.html',
        section=section,
        modules=modules,
        tests=tests,
        enrollments=enrollments,
        releases=releases,
        available_students=available_students,
        instructors=instructors,
        course_instructor_links=course_instructor_links,
        student_releases=student_releases,
        quizzes_by_module=quizzes_by_module,
        study_totals=study_totals,
        teach_totals=teach_totals,
        fmt_seconds=_fmt_seconds,
        course_labs=labs_for_course(section.course),
    )


@app.route('/class/<int:section_id>/labs')
@login_required
def course_labs(section_id):
    """All live labs that belong to this class's curriculum."""
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role == 'student':
        enr = Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first()
        if not enr:
            flash('You are not enrolled in this class.', 'danger')
            return redirect(url_for('student_dashboard'))
    elif current_user.role == 'instructor':
        if not instructor_can_access_section(current_user, section):
            flash('Access denied.', 'danger')
            return redirect(url_for('instructor_dashboard'))
    elif current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    modules = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).all()
    by_chapter = []
    seen = set()
    for m in modules:
        labs = labs_for_module(m)
        if labs:
            by_chapter.append({"module": m, "labs": labs})
            for lab in labs:
                seen.add(lab["id"])
    all_labs = labs_for_course(section.course)
    return render_template(
        'course_labs.html',
        section=section,
        labs=all_labs,
        by_chapter=by_chapter,
        domains=domains_for_course(section.course),
    )


@app.route('/class/<int:section_id>/pilot-pack.csv')
@login_required
def section_pilot_pack(section_id):
    """Convening data pack: scores, pass/fail, category percents."""
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role == 'student':
        flash('Pilot packs are for instructors and admins.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    if current_user.role == 'instructor' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    audit('pilot_pack', f'section={section_id}')
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    enrollments = Enrollment.query.filter_by(section_id=section_id).all()
    lines = ['last,first,email,test,score,passed,completed_utc,categories']
    scores = []
    for enr in enrollments:
        u = enr.student
        for t in tests:
            att = TestAttempt.query.filter_by(
                user_id=u.id, test_id=t.id, section_id=section_id,
            ).filter(TestAttempt.completed_at.isnot(None)).order_by(TestAttempt.completed_at.desc()).first()
            if not att:
                lines.append(f'{u.last_name},{u.first_name},{u.email},{t.title},,,not taken,')
                continue
            scores.append(att.score or 0)
            qs = json.loads(t.questions or '[]')
            ans = json.loads(att.answers or '{}')
            cats = _category_breakdown(qs, ans) if qs else []
            cat_s = ';'.join(f"{c['category']}:{c['pct']}" for c in cats)
            lines.append(
                f'{u.last_name},{u.first_name},{u.email},{t.title},'
                f'{att.score:.1f},{"pass" if att.passed else "fail"},{att.completed_at},{cat_s}'
            )
    if scores:
        lines.append('')
        lines.append(f'CLASS_AVG,,,{sum(scores)/len(scores):.1f},n={len(scores)},,')
        lines.append(f'CLASS_HIGH,,,{max(scores):.1f},,,')
        lines.append(f'CLASS_LOW,,,{min(scores):.1f},,,')
    body = '\n'.join(lines)
    return Response(body, mimetype='text/csv', headers={
        'Content-Disposition': f'attachment; filename=pilot-pack-section-{section_id}.csv'
    })


@app.route('/instructor/section/<int:section_id>/set-instructor', methods=['POST'])
@login_required
def section_set_instructor(section_id):
    if current_user.role != 'admin':
        flash('Only an administrator can change the class instructor.', 'warning')
        return redirect(url_for('instructor_section', section_id=section_id))
    section = ClassSection.query.get_or_404(section_id)
    instructor = User.query.filter_by(id=int(request.form.get('instructor_id') or 0), role='instructor').first()
    if not instructor:
        flash('Select a valid instructor.', 'warning')
        return redirect(url_for('instructor_section', section_id=section_id))
    section.instructor_id = instructor.id
    db.session.commit()
    flash(f'Primary instructor is now {instructor.full_name}.', 'success')
    return redirect(url_for('instructor_section', section_id=section_id) + '#staff')


@app.route('/instructor/section/<int:section_id>/add-course-instructor', methods=['POST'])
@login_required
def section_add_course_instructor(section_id):
    if current_user.role != 'admin':
        flash('Only an administrator can assign curriculum instructors.', 'warning')
        return redirect(url_for('instructor_section', section_id=section_id))
    section = ClassSection.query.get_or_404(section_id)
    user = User.query.filter_by(id=int(request.form.get('user_id') or 0), role='instructor').first()
    if not user:
        flash('Select a valid instructor.', 'warning')
        return redirect(url_for('instructor_section', section_id=section_id))
    exists = CourseInstructor.query.filter_by(course_id=section.course_id, user_id=user.id).first()
    if not exists:
        db.session.add(CourseInstructor(course_id=section.course_id, user_id=user.id))
        db.session.commit()
        flash(f'{user.full_name} can now access every class in {section.course.title}.', 'success')
    else:
        flash(f'{user.full_name} is already on this curriculum set.', 'info')
    return redirect(url_for('instructor_section', section_id=section_id) + '#staff')



@app.route('/instructor/section/<int:section_id>/quiz/<int:quiz_id>/preview')
@login_required
def instructor_quiz_preview(section_id, quiz_id):
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role not in ('admin', 'instructor') or (
        current_user.role != 'admin' and not instructor_can_access_section(current_user, section)
    ):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = json.loads(quiz.questions or '[]')
    module = Module.query.get(quiz.module_id)
    return render_template(
        'instructor_quiz_preview.html',
        section=section, quiz=quiz, questions=questions, module=module,
        course_id=module.course_id if module else section.course_id,
    )


@app.route('/instructor/section/<int:section_id>/test/<int:test_id>/preview')
@login_required
def instructor_test_preview(section_id, test_id):
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role not in ('admin', 'instructor') or (
        current_user.role != 'admin' and not instructor_can_access_section(current_user, section)
    ):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = KnowledgeTest.query.get_or_404(test_id)
    questions = json.loads(test.questions or '[]')
    return render_template(
        'instructor_test_preview.html',
        section=section, test=test, questions=questions,
        course_id=test.course_id,
    )


@app.route('/instructor/release', methods=['POST'])
@login_required
def toggle_release():
    if current_user.role not in ('instructor', 'admin'):
        return jsonify({'error': 'denied'}), 403
    section_id = int(request.form['section_id'])
    content_type = request.form['content_type']
    content_id = int(request.form['content_id'])
    action = request.form.get('action', 'activate')
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role != 'admin' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    audience = request.form.get('audience', 'class')
    raw_ids = request.form.getlist('student_ids')
    student_ids = []
    for raw in raw_ids:
        try:
            student_ids.append(int(raw))
        except (TypeError, ValueError):
            pass
    if audience == 'students' and not student_ids:
        flash('Select one or more students, or choose whole class.', 'warning')
        return redirect(url_for('instructor_section', section_id=section_id))

    def _get_or_create_release(uid):
        q = ContentRelease.query.filter_by(
            section_id=section_id, content_type=content_type, content_id=content_id
        )
        if uid is None:
            rel = q.filter(ContentRelease.user_id.is_(None)).first()
        else:
            rel = q.filter_by(user_id=uid).first()
        if not rel:
            rel = ContentRelease(
                section_id=section_id, content_type=content_type,
                content_id=content_id, user_id=uid,
            )
            db.session.add(rel)
        return rel

    targets = [None] if audience != 'students' else student_ids
    if action == 'activate':
        mode = request.form.get('schedule_mode', 'duration')
        start = end = None
        if mode == 'window':
            start_raw = (request.form.get('available_from') or '').strip()
            end_raw = (request.form.get('available_until') or '').strip()
            if not start_raw or not end_raw:
                flash('Schedule window requires both start and end date/time.', 'warning')
                return redirect(url_for('instructor_section', section_id=section_id))
            try:
                start = datetime.fromisoformat(start_raw)
                end = datetime.fromisoformat(end_raw)
            except ValueError:
                flash('Invalid date/time format.', 'danger')
                return redirect(url_for('instructor_section', section_id=section_id))
            if end <= start:
                flash('End must be after start.', 'warning')
                return redirect(url_for('instructor_section', section_id=section_id))
            msg = f'Scheduled {start.strftime("%Y-%m-%d %H:%M")} → {end.strftime("%Y-%m-%d %H:%M")}.'
        else:
            minutes = int(request.form.get('duration_minutes') or 0)
            hours = int(request.form.get('hours') or 0)
            if minutes <= 0 and hours > 0:
                minutes = hours * 60
            if minutes <= 0:
                minutes = 90
            start_raw = (request.form.get('available_from') or '').strip()
            if start_raw:
                try:
                    start = datetime.fromisoformat(start_raw)
                except ValueError:
                    start = datetime.now()
            else:
                start = datetime.now()
            end = start + timedelta(minutes=minutes)
            if minutes % 60 == 0:
                dur_label = f'{minutes // 60} hour(s)'
            else:
                dur_label = f'{minutes} minutes'
            msg = f'Open from {start.strftime("%Y-%m-%d %H:%M")} for {dur_label}.'
        for uid in targets:
            release = _get_or_create_release(uid)
            release.is_active = True
            release.activated_by = current_user.id
            release.activated_at = datetime.now()
            release.available_from = start
            release.available_until = end
        if audience == 'students':
            msg = f'{len(targets)} student(s): ' + msg
        else:
            msg = 'Whole class: ' + msg
    else:
        for uid in targets:
            release = _get_or_create_release(uid)
            release.is_active = False
            release.available_until = datetime.now()
        if audience == 'students':
            msg = f'Closed for {len(targets)} selected student(s).'
        else:
            msg = 'Closed for the whole class.'
    db.session.commit()
    flash(msg, 'success')
    return redirect(url_for('instructor_section', section_id=section_id))


@app.route('/instructor/enroll', methods=['POST'])
@login_required
def instructor_enroll():
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    section_id = int(request.form['section_id'])
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role != 'admin' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))

    user_id = request.form.get('user_id')
    email = (request.form.get('email') or '').strip().lower()
    student = None
    if user_id:
        student = User.query.filter_by(id=int(user_id), role='student').first()
    elif email:
        student = User.query.filter_by(email=email).first()
        if student and student.role != 'student':
            flash('That account is not a student.', 'warning')
            return redirect(url_for('instructor_section', section_id=section_id))
        if not student:
            # Create a new student on the fly
            first = request.form.get('first_name') or email.split('@')[0]
            last = request.form.get('last_name') or 'Student'
            student = User(email=email, first_name=first, last_name=last, role='student')
            student.set_password('student123')
            db.session.add(student)
            db.session.flush()
            flash(f'Created student account {email} (password: student123).', 'info')

    if not student:
        flash('Select or enter a student.', 'warning')
        return redirect(url_for('instructor_section', section_id=section_id))

    existing = Enrollment.query.filter_by(user_id=student.id, section_id=section_id).first()
    if existing:
        flash(f'{student.full_name} is already enrolled.', 'warning')
    else:
        count = Enrollment.query.filter_by(section_id=section_id).count()
        if count >= section.max_students:
            flash('Section is at capacity.', 'warning')
        else:
            db.session.add(Enrollment(user_id=student.id, section_id=section_id))
            db.session.commit()
            flash(f'Enrolled {student.full_name}.', 'success')
            return redirect(url_for('instructor_section', section_id=section_id))
    db.session.commit()
    return redirect(url_for('instructor_section', section_id=section_id))


@app.route('/instructor/unenroll', methods=['POST'])
@login_required
def instructor_unenroll():
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    section_id = int(request.form['section_id'])
    enrollment_id = int(request.form['enrollment_id'])
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role != 'admin' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    enr = Enrollment.query.get_or_404(enrollment_id)
    if enr.section_id != section_id:
        abort(400)
    name = enr.user.full_name
    db.session.delete(enr)
    db.session.commit()
    flash(f'Removed {name} from the section.', 'info')
    return redirect(url_for('instructor_section', section_id=section_id))


# ---------- Item analysis (visible to all authenticated roles with access) ----------


@app.route('/instructor/section/<int:section_id>/test/<int:test_id>/performance')
@login_required
def instructor_test_performance(section_id, test_id):
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role == 'instructor' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = KnowledgeTest.query.get_or_404(test_id)
    stats = _class_test_stats(test_id, section_id)
    hist_avg, hist_n = _instructor_historical_average(
        section.instructor_id if section.instructor_id else current_user.id
    )
    # Nested subcategories under each broad category (same page expand)
    qs = json.loads(test.questions or '[]')
    sub_by_cat = {}
    for att in stats.get('attempts') or []:
        ans = json.loads(att.answers or '{}')
        for row in _subcategory_breakdown(qs, ans, parent_category=None):
            cat = row['category']
            sub_by_cat.setdefault(cat, {})
            sub_by_cat[cat].setdefault(row['subcategory'], {'correct': 0, 'total': 0})
            sub_by_cat[cat][row['subcategory']]['correct'] += row['correct']
            sub_by_cat[cat][row['subcategory']]['total'] += row['total']
    category_subs = {}
    for cat, subs in sub_by_cat.items():
        rows_sub = []
        for sub, v in sorted(subs.items(), key=lambda x: x[0]):
            pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
            rows_sub.append({
                'subcategory': sub,
                'pct': pct,
                'correct': v['correct'],
                'total': v['total'],
            })
        category_subs[cat] = rows_sub
    # per-student rows + filters (All / multiple / None checkboxes)
    filter_student_ids = [int(x) for x in request.args.getlist('student_id') if str(x).isdigit()]
    result_filter = (request.args.get('result') or '').strip().lower()  # pass | fail | ''
    all_rows = []
    for att in stats['attempts']:
        user = User.query.get(att.user_id)
        all_rows.append({
            'attempt': att,
            'user': user,
            'name': f"{user.first_name} {user.last_name}" if user else 'Unknown',
            'user_id': att.user_id,
        })
    # unique students for filter panel (from this class's attempts)
    student_options = sorted(
        {r['user_id']: r['name'] for r in all_rows if r.get('user_id')}.items(),
        key=lambda x: x[1].lower()
    )
    rows = all_rows
    if filter_student_ids:
        want = set(filter_student_ids)
        rows = [r for r in rows if r.get('user_id') in want]
    if result_filter == 'pass':
        rows = [r for r in rows if r['attempt'].passed]
    elif result_filter == 'fail':
        rows = [r for r in rows if not r['attempt'].passed]
    rows.sort(key=lambda r: (r['attempt'].score is None, -(r['attempt'].score or 0)))
    return render_template(
        'instructor_test_performance.html',
        section=section, test=test, stats=stats, rows=rows,
        hist_avg=hist_avg, hist_n=hist_n,
        category_subs=category_subs,
        student_options=student_options,
        filter_student_ids=filter_student_ids,
        result_filter=result_filter,
        all_attempt_count=len(all_rows),
    )


@app.route('/instructor/attempt/<int:attempt_id>')
@login_required
def instructor_attempt_detail(attempt_id):
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    attempt = TestAttempt.query.get_or_404(attempt_id)
    section = ClassSection.query.get_or_404(attempt.section_id)
    if current_user.role == 'instructor' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = KnowledgeTest.query.get_or_404(attempt.test_id)
    questions = json.loads(test.questions)
    answers = json.loads(attempt.answers or '{}')
    items = []
    for i, q in enumerate(questions):
        ans = answers.get(str(i))
        ok = ans == q.get('correct')
        items.append({
            'index': i + 1,
            'text': q.get('text'),
            'yours': ans,
            'correct': q.get('correct'),
            'ok': ok,
            'to': _terminal_objective(q),
            'category': _broad_category(q),
            'lo': q.get('lo', ''),
            'lo_text': q.get('lo_text', ''),
        })
    categories = _category_breakdown(questions, answers)
    student = User.query.get(attempt.user_id)
    return render_template(
        'instructor_attempt_detail.html',
        section=section, test=test, attempt=attempt, student=student,
        items=items, categories=categories
    )




@app.route('/instructor/course/<int:course_id>/performance')
@login_required
def course_performance(course_id):
    """Compare all class sections for one curriculum set (course)."""
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    course = Course.query.get_or_404(course_id)
    tests = KnowledgeTest.query.filter_by(course_id=course_id).order_by(KnowledgeTest.order).all()
    if current_user.role == 'admin':
        sections = ClassSection.query.filter_by(course_id=course_id, is_active=True).order_by(ClassSection.name).all()
    else:
        sections = instructor_accessible_sections(current_user, course_id=course_id, active_only=True)
        if not sections:
            flash('You only see analytics for classes you can access.', 'warning')
            return redirect(url_for('instructor_analytics_hub'))

    # Build matrix: for each section, overall + per-test + category rollup
    section_rows = []
    category_names = set()
    for sec in sections:
        attempts = TestAttempt.query.filter(
            TestAttempt.section_id == sec.id,
            TestAttempt.completed_at.isnot(None),
            TestAttempt.score.isnot(None),
        ).all()
        scores = [a.score for a in attempts]
        overall = round(sum(scores) / len(scores), 1) if scores else None
        pass_n = sum(1 for a in attempts if a.passed)
        pass_rate = round(pass_n / len(attempts) * 100, 1) if attempts else None

        per_test = []
        for test in tests:
            st = _class_test_stats(test.id, sec.id)
            per_test.append({
                'test': test,
                'stats': st,
            })
            for c in st.get('category_avg') or []:
                category_names.add(c['category'])

        # section-level category blend across all tests
        cat_totals = {}
        for test in tests:
            qs = json.loads(test.questions)
            for att in TestAttempt.query.filter_by(test_id=test.id, section_id=sec.id).filter(
                TestAttempt.completed_at.isnot(None)
            ).all():
                ans = json.loads(att.answers or '{}')
                for row in _category_breakdown(qs, ans):
                    cat_totals.setdefault(row['category'], {'correct': 0, 'total': 0})
                    cat_totals[row['category']]['correct'] += row['correct']
                    cat_totals[row['category']]['total'] += row['total']
                    category_names.add(row['category'])
        cat_avg = []
        for cat, v in sorted(cat_totals.items()):
            pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
            cat_avg.append({'category': cat, 'pct': pct})

        # Nested subcategory totals under each broad category
        sub_by_cat = {}
        for test in tests:
            qs = json.loads(test.questions or '[]')
            for att in TestAttempt.query.filter_by(section_id=sec.id, test_id=test.id).filter(
                TestAttempt.completed_at.isnot(None)
            ).all():
                ans = json.loads(att.answers or '{}')
                for row in _subcategory_breakdown(qs, ans, parent_category=None):
                    cat = row['category']
                    sub_by_cat.setdefault(cat, {})
                    sub_by_cat[cat].setdefault(row['subcategory'], {'correct': 0, 'total': 0})
                    sub_by_cat[cat][row['subcategory']]['correct'] += row['correct']
                    sub_by_cat[cat][row['subcategory']]['total'] += row['total']
        nested = {}
        for cat, subs in sub_by_cat.items():
            rows = []
            for sub, v in sorted(subs.items(), key=lambda x: x[0]):
                pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
                rows.append({'subcategory': sub, 'pct': pct, 'correct': v['correct'], 'total': v['total']})
            nested[cat] = rows

        instructor = User.query.get(sec.instructor_id) if sec.instructor_id else None
        section_rows.append({
            'section': sec,
            'instructor': instructor,
            'n_attempts': len(attempts),
            'overall': overall,
            'pass_rate': pass_rate,
            'high': max(scores) if scores else None,
            'low': min(scores) if scores else None,
            'median': (sorted(scores)[len(scores)//2] if scores else None),
            'per_test': per_test,
            'categories': cat_avg,
            'subs_by_category': nested,
        })

    # Curriculum-wide averages
    all_scores = []
    for row in section_rows:
        if row['overall'] is not None:
            all_scores.append(row['overall'])
    curriculum_mean = round(sum(all_scores) / len(all_scores), 1) if all_scores else None

    hist_avg, hist_n = (None, 0)
    if current_user.role == 'instructor':
        hist_avg, hist_n = _instructor_historical_average(current_user.id)

    return render_template(
        'course_performance.html',
        course=course,
        tests=tests,
        section_rows=section_rows,
        category_names=sorted(category_names),
        curriculum_mean=curriculum_mean,
        hist_avg=hist_avg,
        hist_n=hist_n,
    )


@app.route('/instructor/course/<int:course_id>/category/<path:category>')
@login_required
def course_category_performance(course_id, category):
    """Drill from a broad category into learning-objective subcategories by class."""
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    course = Course.query.get_or_404(course_id)
    category = category.replace('+', ' ')
    tests = KnowledgeTest.query.filter_by(course_id=course_id).order_by(KnowledgeTest.order).all()
    if current_user.role == 'admin':
        sections = ClassSection.query.filter_by(course_id=course_id, is_active=True).order_by(ClassSection.name).all()
    else:
        sections = ClassSection.query.filter_by(
            course_id=course_id, instructor_id=current_user.id, is_active=True
        ).order_by(ClassSection.name).all()
        if not sections:
            flash('You only see analytics for classes you teach.', 'warning')
            return redirect(url_for('instructor_analytics_hub'))

    sub_names = set()
    section_rows = []
    for sec in sections:
        sub_totals = {}
        n_attempts = 0
        for test in tests:
            qs = json.loads(test.questions or '[]')
            atts = TestAttempt.query.filter_by(test_id=test.id, section_id=sec.id).filter(
                TestAttempt.completed_at.isnot(None)
            ).all()
            n_attempts += len(atts)
            for att in atts:
                ans = json.loads(att.answers or '{}')
                for row in _subcategory_breakdown(qs, ans, parent_category=category):
                    sub_totals.setdefault(row['subcategory'], {'correct': 0, 'total': 0})
                    sub_totals[row['subcategory']]['correct'] += row['correct']
                    sub_totals[row['subcategory']]['total'] += row['total']
                    sub_names.add(row['subcategory'])
        subs = []
        for sub, v in sorted(sub_totals.items()):
            pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
            subs.append({'subcategory': sub, 'pct': pct, 'correct': v['correct'], 'total': v['total']})
        overall = None
        if sub_totals:
            c = sum(v['correct'] for v in sub_totals.values())
            tot = sum(v['total'] for v in sub_totals.values())
            overall = round(c / tot * 100, 1) if tot else None
        section_rows.append({
            'section': sec,
            'n_attempts': n_attempts,
            'overall': overall,
            'subs': subs,
        })

    return render_template(
        'course_category_performance.html',
        course=course,
        category=category,
        section_rows=section_rows,
        sub_names=sorted(sub_names),
    )


@app.route('/instructor/section/<int:section_id>/test/<int:test_id>/category/<path:category>')
@login_required
def section_test_category(section_id, test_id, category):
    """Subcategory breakdown for one class + one test under a broad category."""
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    section = ClassSection.query.get_or_404(section_id)
    if current_user.role == 'instructor' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = KnowledgeTest.query.get_or_404(test_id)
    category = category.replace('+', ' ')
    qs = json.loads(test.questions or '[]')
    atts = TestAttempt.query.filter_by(test_id=test_id, section_id=section_id).filter(
        TestAttempt.completed_at.isnot(None)
    ).all()
    sub_totals = {}
    for att in atts:
        ans = json.loads(att.answers or '{}')
        for row in _subcategory_breakdown(qs, ans, parent_category=category):
            sub_totals.setdefault(row['subcategory'], {'correct': 0, 'total': 0})
            sub_totals[row['subcategory']]['correct'] += row['correct']
            sub_totals[row['subcategory']]['total'] += row['total']
    subs = []
    for sub, v in sorted(sub_totals.items(), key=lambda x: (x[1]['correct'] / x[1]['total']) if x[1]['total'] else 0):
        pct = round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0
        subs.append({'subcategory': sub, 'pct': pct, 'correct': v['correct'], 'total': v['total']})
    return render_template(
        'section_test_category.html',
        section=section,
        test=test,
        category=category,
        subs=subs,
        n_attempts=len(atts),
    )



@app.route('/instructor/analytics')
@login_required
def instructor_analytics_hub():
    """Hub: curriculum sets and links to class comparison + section management."""
    if current_user.role not in ('instructor', 'admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    courses = Course.query.order_by(Course.title).all()
    cards = []
    for course in courses:
        if current_user.role == 'admin':
            sections = ClassSection.query.filter_by(course_id=course.id, is_active=True).all()
        else:
            # Current lead + retained access after reassignment
            sections = instructor_accessible_sections(current_user, course_id=course.id, active_only=True)
        if current_user.role != 'admin' and not sections:
            continue
        tests = KnowledgeTest.query.filter_by(course_id=course.id).order_by(KnowledgeTest.order).all()
        sids = [s.id for s in sections]
        attempts = []
        if sids:
            attempts = TestAttempt.query.filter(
                TestAttempt.section_id.in_(sids),
                TestAttempt.completed_at.isnot(None),
                TestAttempt.score.isnot(None),
            ).all()
        mean = round(sum(a.score for a in attempts) / len(attempts), 1) if attempts else None
        cards.append({
            'course': course,
            'sections': sections,
            'tests': tests,
            'n_sections': len(sections),
            'n_attempts': len(attempts),
            'mean': mean,
        })
    return render_template('analytics_hub.html', cards=cards)


@app.route('/analysis/test/<int:test_id>')
@login_required
def test_item_analysis(test_id):
    section_id = request.args.get('section_id', type=int)
    test, analysis, summary = compute_item_analysis(test_id, section_id)
    section = ClassSection.query.get(section_id) if section_id else None
    # Access: admin always; instructor if owns section or any section of course; student if enrolled in section
    allowed = False
    if current_user.role == 'admin':
        allowed = True
    elif current_user.role == 'instructor':
        if section and section.instructor_id == current_user.id:
            allowed = True
        elif not section:
            # course-level view for instructors teaching that course
            allowed = test.course_id in instructor_course_ids(current_user.id)
    # Students never see item-level keys / correct answers — only score + categories on results
    elif current_user.role == 'student':
        allowed = False
    if not allowed:
        flash('Item analysis is available to instructors and administrators only. Students see overall score and category performance after completing a test.', 'warning')
        if current_user.role == 'student' and section_id:
            return redirect(url_for('student_section', section_id=section_id))
        return redirect(url_for('index'))
    return render_template(
        'item_analysis.html',
        test=test,
        analysis=analysis,
        summary=summary,
        section=section,
    )



@app.route('/admin/test-analytics')
@app.route('/instructor/test-analytics')
@login_required
def admin_test_analytics():
    """Distractor / alternative effectiveness with multi-select filters (admin + instructor)."""
    if current_user.role not in ('admin', 'instructor'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    is_admin = current_user.role == 'admin'

    def _ints(name):
        vals = request.args.getlist(name)
        out = []
        for v in vals:
            try:
                out.append(int(v))
            except (TypeError, ValueError):
                pass
        return out

    course_ids = _ints('course_id')
    test_ids = _ints('test_id')
    section_ids = _ints('section_id')
    instructor_ids = _ints('instructor_id')
    if not course_ids and request.args.get('course_id'):
        try:
            course_ids = [int(request.args.get('course_id'))]
        except ValueError:
            pass
    if not test_ids and request.args.get('test_id'):
        try:
            test_ids = [int(request.args.get('test_id'))]
        except ValueError:
            pass
    if not section_ids and request.args.get('section_id'):
        try:
            section_ids = [int(request.args.get('section_id'))]
        except ValueError:
            pass
    if not instructor_ids and request.args.get('instructor_id'):
        try:
            instructor_ids = [int(request.args.get('instructor_id'))]
        except ValueError:
            pass

    # Instructors are locked to their own classes
    if not is_admin:
        instructor_ids = [current_user.id]

    year = request.args.get('year', type=int)
    quarter = (request.args.get('quarter') or '').strip().upper() or None
    if quarter and quarter not in ('Q1', 'Q2', 'Q3', 'Q4'):
        quarter = None
    only_flagged = request.args.get('only_flagged') == '1'
    min_diff = (request.args.get('difficulty') or '').strip()

    if is_admin:
        courses = Course.query.order_by(Course.title).all()
        instructors = User.query.filter(User.role.in_(('instructor', 'admin'))).order_by(User.last_name).all()
        sections = ClassSection.query.order_by(ClassSection.name).all()
    else:
        my_sections = ClassSection.query.filter_by(instructor_id=current_user.id, is_active=True).all()
        my_course_ids = {s.course_id for s in my_sections}
        courses = Course.query.filter(Course.id.in_(my_course_ids or [-1])).order_by(Course.title).all()
        instructors = [current_user]
        sections = my_sections

    if course_ids:
        sections = [s for s in sections if s.course_id in course_ids]
    if instructor_ids and is_admin:
        sections = [s for s in sections if s.instructor_id in instructor_ids]
    elif not is_admin:
        sections = [s for s in sections if s.instructor_id == current_user.id]

    tests = KnowledgeTest.query.order_by(KnowledgeTest.course_id, KnowledgeTest.order).all()
    if course_ids:
        tests = [x for x in tests if x.course_id in course_ids]
    elif not is_admin:
        allowed_c = {s.course_id for s in sections} or my_course_ids
        tests = [x for x in tests if x.course_id in allowed_c]

    # Scope section filter to only allowed ids for instructors
    if not is_admin and section_ids:
        allowed_s = {s.id for s in sections}
        section_ids = [sid for sid in section_ids if sid in allowed_s]

    years = sorted({
        (a.completed_at or a.started_at).year
        for a in TestAttempt.query.filter(TestAttempt.completed_at.isnot(None)).all()
        if (a.completed_at or a.started_at)
    }, reverse=True)

    analysis = summary = test = section = None
    distractor_roll = {'Answer key': 0, 'Strong distractor': 0, 'Functional distractor': 0,
                       'Weak distractor': 0, 'Non-functional': 0}
    test_cards = []

    scope_section_ids = None
    if section_ids:
        scope_section_ids = section_ids
    elif course_ids or instructor_ids or not is_admin:
        scope_section_ids = [s.id for s in sections] if sections else [-1]

    if len(test_ids) == 1:
        tid = test_ids[0]
        test, analysis, summary = compute_item_analysis(
            tid,
            section_ids=scope_section_ids,
            instructor_id=instructor_ids[0] if len(instructor_ids) == 1 else None,
            year=year,
            quarter=quarter,
        )
        if only_flagged:
            analysis = [it for it in analysis if it.get('flags')]
        if min_diff in ('Easy', 'Medium', 'Hard'):
            analysis = [it for it in analysis if it.get('difficulty') == min_diff]
        for it in analysis:
            for opt in it.get('options') or []:
                label = opt.get('effectiveness') or ''
                if label in distractor_roll:
                    distractor_roll[label] += 1
    elif course_ids or test_ids:
        kt_list = tests
        if test_ids:
            kt_list = [x for x in tests if x.id in test_ids]
        for kt in kt_list:
            _t, _a, _s = compute_item_analysis(
                kt.id,
                section_ids=scope_section_ids,
                instructor_id=instructor_ids[0] if len(instructor_ids) == 1 else None,
                year=year,
                quarter=quarter,
            )
            strong = sum(1 for it in _a for o in it.get('options') or [] if o.get('effectiveness') == 'Strong distractor')
            dead = sum(1 for it in _a for o in it.get('options') or [] if o.get('effectiveness') == 'Non-functional')
            test_cards.append({
                'test': kt,
                'summary': _s,
                'strong_distractors': strong,
                'dead_distractors': dead,
                'flagged': _s.get('n_flagged') or 0,
            })

    return render_template(
        'admin_test_analytics.html',
        courses=courses,
        tests=tests,
        sections=sections,
        instructors=instructors,
        years=years,
        filter_course_ids=course_ids,
        filter_test_ids=test_ids,
        filter_section_ids=section_ids,
        filter_instructor_ids=instructor_ids,
        filter_year=year,
        filter_quarter=quarter or '',
        only_flagged=only_flagged,
        min_diff=min_diff,
        test=test,
        analysis=analysis,
        summary=summary,
        section=section,
        distractor_roll=distractor_roll,
        test_cards=test_cards,
        is_admin=is_admin,
    )


# ---------- Admin ----------

@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    if session.get('view_as') == 'instructor':
        flash('Class creation and admin tools are hidden while you work as an instructor.', 'info')
        return redirect(url_for('instructor_dashboard'))
    users = User.query.order_by(User.role, User.last_name).all()
    sections = ClassSection.query.order_by(ClassSection.name).all()
    courses = Course.query.all()
    instructors = User.query.filter_by(role='instructor').order_by(User.last_name, User.first_name).all()
    admins = User.query.filter_by(role='admin').order_by(User.last_name, User.first_name).all()
    course_instructors = {}
    for link in CourseInstructor.query.all():
        course_instructors.setdefault(link.course_id, []).append(link)
    teach_totals = defaultdict(int)
    for row in TimeLog.query.filter_by(kind='teaching').all():
        teach_totals[row.user_id] += row.seconds or 0
        if row.ended_at is None and row.started_at:
            teach_totals[row.user_id] += max(0, int((datetime.utcnow() - row.started_at).total_seconds()))
    study_all = defaultdict(int)
    for row in TimeLog.query.filter_by(kind='study').all():
        study_all[row.user_id] += row.seconds or 0
    teach_by_class = []
    for row in TimeLog.query.filter_by(kind='teaching').all():
        sec = row.seconds or 0
        if row.ended_at is None and row.started_at:
            sec += max(0, int((datetime.utcnow() - row.started_at).total_seconds()))
        teach_by_class.append({
            'user': row.user,
            'section': ClassSection.query.get(row.section_id) if row.section_id else None,
            'seconds': sec,
            'open': row.ended_at is None,
        })
    # collapse by instructor+class
    collapsed = {}
    for item in teach_by_class:
        key = (item['user'].id if item['user'] else 0, item['section'].id if item['section'] else 0)
        collapsed.setdefault(key, {'user': item['user'], 'section': item['section'], 'seconds': 0, 'open': False})
        collapsed[key]['seconds'] += item['seconds']
        collapsed[key]['open'] = collapsed[key]['open'] or item['open']
    teach_by_class = sorted(collapsed.values(), key=lambda x: (-x['seconds'], x['user'].last_name if x['user'] else ''))
    report = _teaching_time_report()
    return render_template(
        'admin_dashboard.html',
        users=users,
        sections=sections,
        courses=courses,
        instructors=instructors,
        admins=admins,
        course_instructors=course_instructors,
        teach_totals=teach_totals,
        study_all=study_all,
        teach_by_class=teach_by_class,
        teach_by_course=report['by_course'],
        teach_by_quarter=report['by_quarter'],
        teach_by_year=report['by_year'],
        fmt_seconds=_fmt_seconds,
    )


def _teaching_seconds(row):
    sec = row.seconds or 0
    if row.ended_at is None and row.started_at:
        sec += max(0, int((datetime.utcnow() - row.started_at).total_seconds()))
    return sec


def _teaching_time_report():
    rows = TimeLog.query.filter_by(kind='teaching').all()
    by_class, by_course, by_quarter, by_year = {}, {}, {}, {}
    # per-class seconds list for course averages (unique instructor-class pairs)
    course_class_totals = defaultdict(list)  # course_id -> [seconds per class]
    course_instr_totals = defaultdict(list)  # course_id -> [seconds per instructor]
    for row in rows:
        user = row.user
        section = ClassSection.query.get(row.section_id) if row.section_id else None
        course = section.course if section and section.course else None
        when = row.started_at or datetime.utcnow()
        year = when.year
        quarter = f'Q{((when.month - 1) // 3) + 1}'
        sec = _teaching_seconds(row)
        uid = user.id if user else 0
        cid = course.id if course else 0
        sid = section.id if section else 0
        sk = (uid, sid)
        by_class.setdefault(sk, {
            'user': user, 'section': section, 'course': course, 'seconds': 0, 'sessions': 0,
        })
        by_class[sk]['seconds'] += sec
        by_class[sk]['sessions'] += 1
        ck = (uid, cid)
        by_course.setdefault(ck, {
            'user': user, 'course': course, 'seconds': 0, 'class_ids': set(),
        })
        by_course[ck]['seconds'] += sec
        if sid:
            by_course[ck]['class_ids'].add(sid)
        qk = (uid, year, quarter, sid if sid else cid)
        by_quarter.setdefault(qk, {
            'user': user, 'year': year, 'quarter': quarter,
            'section': section, 'course': course, 'seconds': 0,
        })
        by_quarter[qk]['seconds'] += sec
        yk = (uid, year)
        by_year.setdefault(yk, {'user': user, 'year': year, 'seconds': 0})
        by_year[yk]['seconds'] += sec

    # Course averages: mean seconds across classes that have teaching time
    class_only = {}
    for key, item in by_class.items():
        if not item['section'] or not item['course']:
            continue
        cid = item['course'].id
        sid = item['section'].id
        class_only.setdefault((cid, sid), 0)
        class_only[(cid, sid)] += item['seconds']
    course_avg_by_class = {}
    for (cid, sid), secs in class_only.items():
        course_avg_by_class.setdefault(cid, []).append(secs)
    # instructor totals per course for mean
    instr_per_course = defaultdict(list)
    for item in by_course.values():
        if item['course']:
            instr_per_course[item['course'].id].append(item['seconds'])

    course_averages = []
    courses = {c.id: c for c in Course.query.all()}
    for cid, class_secs in course_avg_by_class.items():
        course = courses.get(cid)
        avg_class = round(sum(class_secs) / len(class_secs)) if class_secs else 0
        instr_secs = instr_per_course.get(cid, [])
        avg_instr = round(sum(instr_secs) / len(instr_secs)) if instr_secs else 0
        course_averages.append({
            'course': course,
            'total_seconds': sum(class_secs),
            'n_classes': len(class_secs),
            'avg_per_class': avg_class,
            'n_instructors': len(instr_secs),
            'avg_per_instructor': avg_instr,
        })
    course_averages.sort(key=lambda x: (x['course'].title if x['course'] else ''))

    by_course_list = []
    for item in by_course.values():
        by_course_list.append({
            'user': item['user'],
            'course': item['course'],
            'seconds': item['seconds'],
            'n_classes': len(item['class_ids']),
            'avg_per_class': round(item['seconds'] / len(item['class_ids'])) if item['class_ids'] else item['seconds'],
        })
    by_course_list.sort(key=lambda x: (
        x['user'].last_name if x['user'] else '', x['course'].title if x['course'] else ''))

    return {
        'by_class': sorted(by_class.values(), key=lambda x: (
            x['user'].last_name if x['user'] else '',
            x['course'].title if x['course'] else '',
            x['section'].name if x['section'] else '')),
        'by_course': by_course_list,
        'course_averages': course_averages,
        'by_quarter': sorted(by_quarter.values(), key=lambda x: (
            -x['year'], x['quarter'], x['user'].last_name if x['user'] else '')),
        'by_year': sorted(by_year.values(), key=lambda x: (-x['year'], x['user'].last_name if x['user'] else '')),
    }


@app.route('/admin/teaching-time')
@login_required
@role_required('admin')
def admin_teaching_time():
    report = _teaching_time_report()
    instructor_id = request.args.get('instructor_id', type=int)
    course_id = request.args.get('course_id', type=int)
    section_id = request.args.get('section_id', type=int)
    year = request.args.get('year', type=int)
    quarter = (request.args.get('quarter') or '').strip().upper()
    sort = (request.args.get('sort') or 'instructor').strip()
    q = (request.args.get('q') or '').strip().lower()

    def _match_person(user):
        if not instructor_id:
            return True
        return user and user.id == instructor_id

    def _match_course(course):
        if not course_id:
            return True
        return course and course.id == course_id

    def _match_section(section):
        if not section_id:
            return True
        return section and section.id == section_id

    def _text_ok(*parts):
        if not q:
            return True
        blob = ' '.join(str(p or '') for p in parts).lower()
        return q in blob

    by_class = [
        row for row in report['by_class']
        if _match_person(row.get('user'))
        and _match_course(row.get('course'))
        and _match_section(row.get('section'))
        and _text_ok(
            row.get('user').full_name if row.get('user') else '',
            row.get('section').name if row.get('section') else '',
            row.get('course').title if row.get('course') else '',
            row.get('course').code if row.get('course') else '',
        )
    ]
    by_course = [
        row for row in report['by_course']
        if _match_person(row.get('user')) and _match_course(row.get('course'))
        and _text_ok(
            row.get('user').full_name if row.get('user') else '',
            row.get('course').title if row.get('course') else '',
        )
    ]
    course_averages = [
        row for row in report['course_averages']
        if _match_course(row.get('course'))
        and _text_ok(row.get('course').title if row.get('course') else '')
    ]
    def _match_year(row_year):
        if not year:
            return True
        return row_year == year

    def _match_quarter(row_q):
        if not quarter:
            return True
        return (row_q or '').upper() == quarter

    by_quarter = [
        row for row in report['by_quarter']
        if _match_person(row.get('user'))
        and _match_course(row.get('course'))
        and _match_section(row.get('section'))
        and _match_year(row.get('year'))
        and _match_quarter(row.get('quarter'))
        and _text_ok(
            row.get('user').full_name if row.get('user') else '',
            row.get('section').name if row.get('section') else '',
            row.get('course').code if row.get('course') else '',
        )
    ]
    by_year = [
        row for row in report['by_year']
        if _match_person(row.get('user')) and _match_year(row.get('year'))
        and _text_ok(row.get('user').full_name if row.get('user') else '')
    ]

    def _iname(row):
        return (row.get('user').last_name if row.get('user') else 'zzz').lower()
    def _cname(row):
        sec = row.get('section')
        return (sec.name if sec else '').lower()
    def _course(row):
        c = row.get('course')
        return ((c.code if c else '') + ' ' + (c.title if c else '')).lower()
    def _secs(row):
        return int(row.get('seconds') or 0)

    reverse_time = sort in ('time', '-time', 'time_desc')
    if sort in ('time', '-time', 'time_desc'):
        by_class.sort(key=_secs, reverse=True)
        by_course.sort(key=_secs, reverse=True)
        by_quarter.sort(key=_secs, reverse=True)
        by_year.sort(key=_secs, reverse=True)
        course_averages.sort(key=lambda r: int(r.get('total_seconds') or 0), reverse=True)
    elif sort == 'class':
        by_class.sort(key=_cname)
        by_quarter.sort(key=_cname)
    elif sort == 'course':
        by_class.sort(key=_course)
        by_course.sort(key=_course)
        by_quarter.sort(key=_course)
        course_averages.sort(key=lambda r: (r.get('course').title if r.get('course') else ''))
    elif sort == 'year':
        by_quarter.sort(key=lambda r: (-int(r.get('year') or 0), r.get('quarter') or ''))
        by_year.sort(key=lambda r: -int(r.get('year') or 0))
    else:
        by_class.sort(key=_iname)
        by_course.sort(key=_iname)
        by_quarter.sort(key=_iname)
        by_year.sort(key=_iname)

    years = sorted({r.get('year') for r in report['by_year'] if r.get('year')}, reverse=True)
    instructors = User.query.filter(User.role.in_(('instructor', 'admin'))).order_by(User.last_name).all()
    courses = Course.query.order_by(Course.title).all()
    sections = ClassSection.query.order_by(ClassSection.name).all()
    if course_id:
        sections = [s for s in sections if s.course_id == course_id]
    return render_template(
        'admin_teaching_time.html',
        teach_by_class=by_class,
        teach_by_course=by_course,
        course_averages=course_averages,
        teach_by_quarter=by_quarter,
        teach_by_year=by_year,
        fmt_seconds=_fmt_seconds,
        instructors=instructors,
        courses=courses,
        sections=sections,
        filter_instructor_id=instructor_id,
        filter_course_id=course_id,
        filter_section_id=section_id,
        filter_year=year,
        filter_quarter=quarter,
        filter_sort=sort,
        filter_q=q,
        years=years,
    )


@app.route('/admin/section/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_section():
    if session.get('view_as') == 'instructor':
        flash('Only an administrator working as admin can create classes.', 'warning')
        return redirect(url_for('instructor_dashboard'))
    name = request.form.get('name', '').strip()
    course_id = int(request.form['course_id'])
    instructor_id = int(request.form['instructor_id'])
    max_students = int(request.form.get('max_students') or 25)
    start = request.form.get('start_date') or None
    end = request.form.get('end_date') or None
    if not name:
        flash('Section name is required.', 'warning')
        return redirect(url_for('admin_dashboard'))
    section = ClassSection(
        name=name,
        course_id=course_id,
        instructor_id=instructor_id,
        max_students=max_students,
        start_date=datetime.strptime(start, '%Y-%m-%d').date() if start else None,
        end_date=datetime.strptime(end, '%Y-%m-%d').date() if end else None,
        is_active=True,
    )
    db.session.add(section)
    db.session.flush()
    grant_section_instructor_access(section.id, instructor_id, primary=True)
    db.session.commit()
    flash(f'Created section “{name}”.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/section/toggle', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_section():
    section = ClassSection.query.get_or_404(int(request.form['section_id']))
    section.is_active = not section.is_active
    db.session.commit()
    flash(f'Section “{section.name}” is now {"active" if section.is_active else "inactive"}.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/user/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_user():
    email = request.form.get('email', '').strip().lower()
    first = request.form.get('first_name', '').strip()
    last = request.form.get('last_name', '').strip()
    role = request.form.get('role', 'student')
    password = request.form.get('password') or 'changeme123'
    if not email or not first or not last:
        flash('Email and name are required.', 'warning')
        return redirect(url_for('admin_dashboard'))
    if User.query.filter_by(email=email).first():
        flash('Email already exists.', 'warning')
        return redirect(url_for('admin_dashboard'))
    if role not in ('admin', 'instructor', 'student'):
        role = 'student'
    u = User(email=email, first_name=first, last_name=last, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash(f'Created {role} {first} {last} ({email}). Sign-in password: {password}', 'success')
    return redirect(url_for('admin_dashboard') + '#admin-staff')


@app.route('/admin/instructor/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_instructor():
    email = request.form.get('email', '').strip().lower()
    first = request.form.get('first_name', '').strip()
    last = request.form.get('last_name', '').strip()
    password = request.form.get('password') or 'changeme123'
    role = request.form.get('role') or 'instructor'
    if role not in ('instructor', 'admin'):
        role = 'instructor'
    if not email or not first or not last:
        flash('First name, last name, and email are required.', 'warning')
        return redirect(url_for('admin_dashboard') + '#admin-people')
    existing = User.query.filter_by(email=email).first()
    if existing:
        if existing.role == 'instructor':
            flash('That account is already an instructor.', 'info')
        elif existing.id == current_user.id:
            flash('You cannot change your own role here.', 'warning')
        else:
            existing.role = role
            existing.first_name = first or existing.first_name
            existing.last_name = last or existing.last_name
            db.session.commit()
            flash(f'Updated {existing.full_name} to {role}.', 'success')
        return redirect(url_for('admin_dashboard'))
    u = User(email=email, first_name=first, last_name=last, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash(f'Added {role} {first} {last} ({email}). Temporary password: {password}', 'success')
    return redirect(url_for('admin_dashboard') + '#admin-staff')


@app.route('/admin/instructor/make-admin', methods=['POST'])
@login_required
@role_required('admin')
def admin_make_admin():
    user = User.query.get_or_404(int(request.form.get('user_id') or 0))
    if user.id == current_user.id:
        flash('You are already an administrator.', 'info')
        return redirect(url_for('admin_dashboard'))
    if user.role != 'instructor':
        flash('Only an instructor account can be promoted to admin from this button.', 'warning')
        return redirect(url_for('admin_dashboard'))
    user.role = 'admin'
    db.session.commit()
    flash(f'{user.full_name} is now an administrator.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/admin/demote', methods=['POST'])
@login_required
@role_required('admin')
def admin_demote_admin():
    user = User.query.get_or_404(int(request.form.get('user_id') or 0))
    if user.id == current_user.id:
        flash('You cannot remove your own admin access from this screen.', 'warning')
        return redirect(url_for('admin_dashboard') + '#admin-staff')
    if user.role != 'admin':
        flash('That account is not an administrator.', 'warning')
        return redirect(url_for('admin_dashboard') + '#admin-staff')
    remaining = User.query.filter_by(role='admin').count()
    if remaining <= 1:
        flash('Keep at least one administrator.', 'warning')
        return redirect(url_for('admin_dashboard') + '#admin-staff')
    user.role = 'instructor'
    db.session.commit()
    flash(f'{user.full_name} is now an instructor (admin access removed).', 'success')
    return redirect(url_for('admin_dashboard') + '#admin-staff')


@app.route('/admin/instructor/remove', methods=['POST'])
@login_required
@role_required('admin')
def admin_remove_instructor():
    user_id = int(request.form.get('user_id') or 0)
    reassign_to = request.form.get('reassign_to') or ''
    instructor = User.query.get_or_404(user_id)
    if instructor.role != 'instructor':
        flash('That user is not an instructor.', 'warning')
        return redirect(url_for('admin_dashboard'))
    if instructor.id == current_user.id:
        flash('You cannot remove your own account from this screen.', 'warning')
        return redirect(url_for('admin_dashboard'))
    sections = ClassSection.query.filter_by(instructor_id=instructor.id).all()
    if sections:
        if not reassign_to:
            flash(
                f'{instructor.full_name} is assigned to {len(sections)} class(es). '
                'Choose another instructor to reassign those classes, then remove.',
                'warning',
            )
            return redirect(url_for('admin_dashboard'))
        replacement = User.query.filter_by(id=int(reassign_to), role='instructor').first()
        if not replacement or replacement.id == instructor.id:
            flash('Select a different active instructor to take those classes.', 'warning')
            return redirect(url_for('admin_dashboard'))
        for sec in sections:
            prev_id = sec.instructor_id
            sec.instructor_id = replacement.id
            # Previous instructor keeps access; new lead is primary
            if prev_id:
                grant_section_instructor_access(sec.id, prev_id, primary=False)
            grant_section_instructor_access(sec.id, replacement.id, primary=True)
    instructor.role = 'student'
    db.session.commit()
    extra = f' Classes moved to {replacement.full_name} (previous instructor keeps view access).' if sections else ''
    flash(f'Removed instructor access for {instructor.full_name}.{extra}', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/section/assign-instructor', methods=['POST'])
@login_required
@role_required('admin')
def admin_assign_instructor():
    section = ClassSection.query.get_or_404(int(request.form['section_id']))
    instructor = User.query.filter_by(id=int(request.form['instructor_id']), role='instructor').first()
    if not instructor:
        flash('Select a valid instructor.', 'warning')
        return redirect(url_for('admin_dashboard'))
    prev_id = section.instructor_id
    section.instructor_id = instructor.id
    if prev_id and prev_id != instructor.id:
        grant_section_instructor_access(section.id, prev_id, primary=False)
    grant_section_instructor_access(section.id, instructor.id, primary=True)
    db.session.commit()
    if prev_id and prev_id != instructor.id:
        prev = User.query.get(prev_id)
        prev_name = prev.full_name if prev else 'previous instructor'
        flash(
            f'{section.name} is now led by {instructor.full_name}. '
            f'{prev_name} still has access to this class.',
            'success',
        )
    else:
        flash(f'{section.name} is now assigned to {instructor.full_name}.', 'success')
    return redirect(url_for('admin_dashboard'))



@app.route('/admin/course/add-instructor', methods=['POST'])
@login_required
@role_required('admin')
def admin_add_course_instructor():
    course = Course.query.get_or_404(int(request.form.get('course_id') or 0))
    user = User.query.get_or_404(int(request.form.get('user_id') or 0))
    if user.role != 'instructor':
        flash('Select an instructor account.', 'warning')
        return redirect(url_for('admin_dashboard'))
    exists = CourseInstructor.query.filter_by(course_id=course.id, user_id=user.id).first()
    if exists:
        flash(f'{user.full_name} is already assigned to {course.title}.', 'info')
        return redirect(url_for('admin_dashboard'))
    db.session.add(CourseInstructor(course_id=course.id, user_id=user.id))
    db.session.commit()
    flash(f'Added {user.full_name} to curriculum set {course.title}.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/course/remove-instructor', methods=['POST'])
@login_required
@role_required('admin')
def admin_remove_course_instructor():
    link = CourseInstructor.query.get_or_404(int(request.form.get('link_id') or 0))
    name = link.user.full_name if link.user else 'Instructor'
    title = link.course.title if link.course else 'course'
    db.session.delete(link)
    db.session.commit()
    flash(f'Removed {name} from {title}.', 'success')
    return redirect(url_for('admin_dashboard'))




@app.route('/demo')
def demo_guide():
    return render_template('demo_guide.html')


@app.route('/gaps')
def gaps():
    return render_template('gaps.html')


@app.route('/admin/backup-db')
@login_required
@role_required('admin')
def admin_backup_db():
    """Download a copy of the SQLite database file."""
    db_path = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///ciwt.db')
    if db_path.startswith('sqlite:///'):
        path = db_path.replace('sqlite:///', '', 1)
        if not path.startswith('/'):
            path = str(Path(app.root_path) / path)
    else:
        flash('Backup is only implemented for SQLite demos.', 'warning')
        return redirect(url_for('admin_dashboard'))
    p = Path(path)
    if not p.exists():
        # common relative instance path
        for cand in (Path(app.root_path) / 'ciwt.db', Path(app.root_path) / 'instance' / 'ciwt.db',
                     Path('ciwt.db'), Path('instance/ciwt.db')):
            if cand.exists():
                p = cand
                break
    if not p.exists():
        flash('Could not find SQLite file to back up.', 'danger')
        return redirect(url_for('admin_dashboard'))
    audit('backup_db')
    return send_file(p, as_attachment=True, download_name=f'ciwt-backup-{datetime.utcnow().strftime("%Y%m%d-%H%M")}.db')


@app.route('/admin/audit')
@login_required
@role_required('admin')
def admin_audit():
    rows = AuditEvent.query.order_by(AuditEvent.created_at.desc()).limit(300).all()
    return render_template('admin_audit.html', rows=rows)


@app.route('/admin/readiness')
@login_required
@role_required('admin')
def admin_readiness():
    from interactive_labs import list_labs
    labs = list_labs()
    by_kind = {}
    for lab in labs:
        by_kind[lab['kind']] = by_kind.get(lab['kind'], 0) + 1
    secret_default = app.config.get('SECRET_KEY') == 'ciwt-lms-demo-key-change-in-production'
    debug = bool(app.debug)
    sqlite = str(app.config.get('SQLALCHEMY_DATABASE_URI') or '').startswith('sqlite')
    checks = [
        {'name': 'Live labs catalog', 'ok': len(labs) >= 20, 'detail': f'{len(labs)} labs'},
        {'name': 'SECRET_KEY set from environment', 'ok': not secret_default, 'detail': 'Required before any real users'},
        {'name': 'Not running Flask debug', 'ok': not debug, 'detail': 'Debug leaks traces'},
        {'name': 'Database is not demo SQLite', 'ok': not sqlite, 'detail': 'Postgres/MySQL for production'},
        {'name': 'Audit log table', 'ok': True, 'detail': 'Logins and admin backups are recorded'},
        {'name': 'SQLite backup download', 'ok': True, 'detail': '/admin/backup-db'},
        {'name': 'Health endpoint', 'ok': True, 'detail': '/healthz'},
    ]
    return render_template(
        'admin_readiness.html',
        checks=checks,
        labs=labs,
        by_kind=by_kind,
        domains_itsup=domains_for_course(type('C', (), {'code': 'ITSUP'})()),
        domains_netops=domains_for_course(type('C', (), {'code': 'NETOPS'})()),
    )


@app.route('/admin/export/analytics.csv')
@login_required
def export_analytics_csv():
    """CSV: class / test scores and category rollups for admin or instructor scope."""
    if current_user.role not in ('admin', 'instructor'):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    if current_user.role == 'admin':
        sections = ClassSection.query.order_by(ClassSection.name).all()
    else:
        sections = instructor_accessible_sections(current_user, active_only=False)

    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(['class', 'course', 'instructor', 'test', 'attempts', 'average', 'median', 'high', 'low', 'pass_rate', 'category', 'category_pct'])
    for sec in sections:
        course = Course.query.get(sec.course_id)
        instr = User.query.get(sec.instructor_id) if sec.instructor_id else None
        instr_name = instr.full_name if instr else ''
        tests = KnowledgeTest.query.filter_by(course_id=sec.course_id).order_by(KnowledgeTest.order).all()
        for test in tests:
            st = _class_test_stats(test.id, sec.id)
            cats = st.get('category_avg') or [{'category': '', 'pct': ''}]
            for c in cats:
                w.writerow([
                    sec.name,
                    course.title if course else '',
                    instr_name,
                    test.title,
                    st.get('n') or 0,
                    st.get('mean') if st.get('mean') is not None else '',
                    st.get('median') if st.get('median') is not None else '',
                    st.get('high') if st.get('high') is not None else '',
                    st.get('low') if st.get('low') is not None else '',
                    st.get('pass_rate') if st.get('pass_rate') is not None else '',
                    c.get('category') or '',
                    c.get('pct') if c.get('pct') is not None else '',
                ])
    data = buf.getvalue()
    return Response(
        data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=ciwt-analytics-export.csv'},
    )


@app.route('/admin/export/item-flags.csv')
@login_required
@role_required('admin')
def export_item_flags_csv():
    """CSV of flagged items across tests (admin)."""
    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(['course', 'test', 'item_index', 'P', 'pct_correct', 'p_status', 'difficulty', 'd', 'disc_label', 'flags', 'stem'])
    for test in KnowledgeTest.query.order_by(KnowledgeTest.course_id, KnowledgeTest.order).all():
        course = Course.query.get(test.course_id)
        _t, analysis, _s = compute_item_analysis(test.id)
        for it in analysis:
            if not it.get('flags'):
                continue
            w.writerow([
                course.title if course else '',
                test.title,
                it.get('index'),
                it.get('P'),
                it.get('pct_correct'),
                it.get('p_status'),
                it.get('difficulty'),
                it.get('discrimination'),
                it.get('disc_label'),
                '; '.join(it.get('flags') or []),
                (it.get('text') or '')[:200],
            ])
    return Response(
        buf.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=ciwt-item-flags.csv'},
    )



@app.route('/admin/seed', methods=['POST'])
@login_required
@role_required('admin')
def seed_data_route():
    seed_database()
    flash('Database re-seeded with sample curriculum, users, and classes.', 'success')
    return redirect(url_for('admin_dashboard'))



def _question_stem_key(text):
    """Normalize stems so quiz items are not reused on graded tests."""
    if not text:
        return ''
    words = re.findall(r"[a-z0-9]+", text.lower())
    stop = {
        'the','a','an','of','to','and','or','for','in','on','is','which','what','when','with',
        'does','do','are','most','best','likely','common','typically','following','should',
        'would','could','from','that','this','into','after','before','only','used','using',
    }
    words = [w for w in words if w not in stop and len(w) > 1]
    return ' '.join(words[:18])


def _stems_overlap(a, b, threshold=0.55):
    """True if two normalized stems share enough significant tokens (near-duplicate)."""
    if not a or not b:
        return False
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return False
    inter = len(sa & sb)
    return inter / min(len(sa), len(sb)) >= threshold


def _filter_unused_questions(question_list, used_keys, min_keep=40):
    """Drop any item whose stem matches or strongly overlaps a quiz stem. Never re-add quiz items."""
    out = []
    used_list = list(used_keys)
    for q in question_list:
        key = _question_stem_key(q.get('text') or q.get('q') or '')
        if not key:
            continue
        if key in used_keys:
            continue
        if any(_stems_overlap(key, uk) for uk in used_list):
            continue
        out.append(q)
        used_keys.add(key)
        used_list.append(key)
    # Do NOT fall back to quiz-overlapping items. Pad only from non-overlapping remainder.
    if len(out) < min_keep:
        for q in question_list:
            if q in out:
                continue
            key = _question_stem_key(q.get('text') or q.get('q') or '')
            if not key or key in used_keys:
                continue
            if any(_stems_overlap(key, uk) for uk in used_list):
                continue
            out.append(q)
            used_keys.add(key)
            used_list.append(key)
            if len(out) >= min_keep:
                break
    return out


def seed_database():
    db.drop_all()
    db.create_all()

    admin = User(email='admin@lms.local', first_name='System', last_name='Admin', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    instr1 = User(email='instructor@lms.local', first_name='Jordan', last_name='Lee', role='instructor')
    instr1.set_password('teach123')
    db.session.add(instr1)

    instr2 = User(email='instructor2@lms.local', first_name='Sam', last_name='Rivera', role='instructor')
    instr2.set_password('teach123')
    db.session.add(instr2)

    students = []
    for i in range(1, 26):
        s = User(
            email=f'student{i}@lms.local',
            first_name=f'Student{i}',
            last_name='Demo',
            role='student',
        )
        s.set_password('student123')
        students.append(s)
        db.session.add(s)
    db.session.commit()

    aplus = Course(
        code='ITSUP',
        title='IT Support Technician Fundamentals',
        description='Hardware, software, networking, security, and operational procedures for IT support technicians.',
    )
    netplus = Course(
        code='NETOPS',
        title='Network Operations Fundamentals',
        description='Networking concepts, infrastructure, operations, security, and troubleshooting.',
    )
    db.session.add_all([aplus, netplus])
    db.session.commit()
    db.session.add_all([
        CourseInstructor(course_id=aplus.id, user_id=instr1.id),
        CourseInstructor(course_id=netplus.id, user_id=instr2.id),
    ])
    db.session.commit()

    def _seed_course_modules(course, pack):
        for ch in pack:
            # support both legacy tuples and new dict chapters
            if isinstance(ch, dict):
                order = ch['order']
                title = ch['title']
                mins = ch.get('minutes', 60)
                overview = ch.get('overview', '')
                lesson_list = ch.get('lessons', [])
            else:
                order, title, mins, html = ch
                overview = html
                lesson_list = []
            mod = Module(
                course_id=course.id, title=title, order=order,
                content=overview, estimated_minutes=mins
            )
            db.session.add(mod)
            db.session.flush()
            for les in lesson_list:
                db.session.add(Lesson(
                    module_id=mod.id,
                    title=les['title'],
                    order=les['order'],
                    content=les['html'],
                    estimated_minutes=les.get('minutes', 30),
                ))
        db.session.commit()

    _seed_course_modules(aplus, APLUS_LESSONS)
    _seed_course_modules(netplus, NETPLUS_LESSONS)

    aplus_mods = Module.query.filter_by(course_id=aplus.id).order_by(Module.order).all()
    # Formative progress-check banks (must NOT overlap graded test scenario stems)
    quiz_data = [
        [  # Hardware formative
            {"q": "In plain terms, what does a motherboard primarily do?",
             "options": ["Store long-term user files only", "Connect CPU, memory, storage, and expansion so they work as one system", "Replace the need for an operating system", "Provide only Wi-Fi"], "correct": "Connect CPU, memory, storage, and expansion so they work as one system"},
            {"q": "Why do technicians match RAM generation (for example DDR4 vs DDR5) to the board?",
             "options": ["Any stick fits any board electrically", "Slots and memory controllers support specific generations and keying", "RAM generation only changes the color of the PCB", "DDR number only describes the heatsink brand"], "correct": "Slots and memory controllers support specific generations and keying"},
            {"q": "What is the main practical difference between a SATA SSD and an NVMe SSD for a student lab PC?",
             "options": ["NVMe cannot store an OS", "NVMe typically uses a PCIe path for higher throughput; SATA uses the SATA interface", "SATA is always faster than NVMe", "Both only work on servers"], "correct": "NVMe typically uses a PCIe path for higher throughput; SATA uses the SATA interface"},
            {"q": "What does RAID protect against when used correctly?",
             "options": ["User error and ransomware by itself", "Certain drive failures depending on the RAID level—not a full backup strategy", "Only power outages", "Only DNS failures"], "correct": "Certain drive failures depending on the RAID level—not a full backup strategy"},
            {"q": "Where is thermal paste supposed to go?",
             "options": ["Between the CPU heat spreader and the cooler base", "On top of RAM sticks", "Inside the PSU", "On the SATA data pins"], "correct": "Between the CPU heat spreader and the cooler base"},
            {"q": "What is UEFI relative to legacy BIOS for modern PCs?",
             "options": ["A type of hard drive", "Modern firmware interface that initializes hardware and starts the boot process", "A Windows user account", "A network cable standard"], "correct": "Modern firmware interface that initializes hardware and starts the boot process"},
            {"q": "Why might a small form-factor PC limit GPU choices?",
             "options": ["Because Ethernet cannot run at 1 Gbps", "Because case clearance, slot count, and power delivery are constrained", "Because Windows refuses GPUs under 100W always", "Because CPUs cannot use PCIe"], "correct": "Because case clearance, slot count, and power delivery are constrained"},
            {"q": "What does a PSU wattage rating mainly tell you?",
             "options": ["CPU clock speed", "How much power the supply can deliver to the system under load", "Hard drive RPM", "Monitor refresh rate"], "correct": "How much power the supply can deliver to the system under load"},
            {"q": "What is a practical reason to prefer ECC memory in some workstations/servers?",
             "options": ["It always doubles clock speed", "It can detect/correct certain memory errors for higher reliability", "It removes the need for cooling", "It replaces the need for backups"], "correct": "It can detect/correct certain memory errors for higher reliability"},
            {"q": "What does a POST beep or code generally indicate?",
             "options": ["Successful user login", "Firmware/hardware initialization status during early boot", "DHCP lease time", "Printer toner level"], "correct": "Firmware/hardware initialization status during early boot"},
        ],
        [  # Networking formative
            {"q": "What problem does a default gateway solve for a PC?",
             "options": ["It stores all DNS records locally", "It is the hop used to leave the local network toward other networks", "It assigns MAC addresses", "It compresses files"], "correct": "It is the hop used to leave the local network toward other networks"},
            {"q": "What is the main job of DNS for end users?",
             "options": ["Assign IP addresses automatically", "Translate names people use into addresses systems route to", "Encrypt every packet on the LAN", "Create VLANs"], "correct": "Translate names people use into addresses systems route to"},
            {"q": "What does DHCP mainly automate?",
             "options": ["Certificate issuance only", "Handing out IP settings such as address, mask, gateway, and DNS to clients", "RAID rebuilds", "UEFI updates"], "correct": "Handing out IP settings such as address, mask, gateway, and DNS to clients"},
            {"q": "Why do we care about TCP port numbers in troubleshooting?",
             "options": ["They identify which service/process is intended on a host", "They replace IP addresses", "They measure cable length", "They set fan speed"], "correct": "They identify which service/process is intended on a host"},
            {"q": "What is an APIPA address a clue about on Windows?",
             "options": ["Perfect DHCP operation", "The client likely failed to obtain a DHCP lease and self-assigned a link-local address", "The CPU is overheating", "The disk is GPT"], "correct": "The client likely failed to obtain a DHCP lease and self-assigned a link-local address"},
            {"q": "What is the difference between a switch and a basic hub in modern LANs?",
             "options": ["A switch forwards based on MAC learning; hubs are shared repeaters rarely used today", "A hub routes between VLANs", "A switch only works with fiber", "Hubs encrypt traffic by default"], "correct": "A switch forwards based on MAC learning; hubs are shared repeaters rarely used today"},
            {"q": "What does a subnet mask tell a host?",
             "options": ["Which part of the address is network vs host for on-link decisions", "The DNS server password", "The printer model", "The BIOS version"], "correct": "Which part of the address is network vs host for on-link decisions"},
            {"q": "Why is ping a useful first test?",
             "options": ["It verifies basic IP reachability (when ICMP is allowed)", "It repairs the OS image", "It creates user accounts", "It measures toner density"], "correct": "It verifies basic IP reachability (when ICMP is allowed)"},
            {"q": "On a home or small-office gateway, why do many private PCs share one public address toward the Internet?",
             "options": ["Sharing a public address among private LAN clients for Internet access", "Formatting disks", "Assigning domain SIDs", "Updating UEFI"], "correct": "Sharing a public address among private LAN clients for Internet access"},
            {"q": "Why prefer modern WPA2/WPA3 settings over legacy weak Wi-Fi security?",
             "options": ["Stronger protection for traffic on the wireless medium", "Faster spinning hard drives", "Automatic VLAN creation", "Removal of the need for passwords"], "correct": "Stronger protection for traffic on the wireless medium"},
        ],
        [  # OS formative
            {"q": "Why should a standard staff account not be given full administrator rights on every PC?",
             "options": ["Give everyone administrator rights", "Grant only the access needed to do the job, reducing impact of mistakes and compromise", "Disable all logging", "Share one password"], "correct": "Grant only the access needed to do the job, reducing impact of mistakes and compromise"},
            {"q": "Which built-in Windows command checks protected system files and tries to repair them when they are corrupt?",
             "options": ["Scan and repair protected system files", "Create a new VLAN", "Flash the BIOS", "Measure network latency"], "correct": "Scan and repair protected system files"},
            {"q": "Why might a technician use DISM after SFC fails?",
             "options": ["To repair the Windows component store that SFC relies on", "To set the default gateway", "To crimp Ethernet ends", "To enable WEP"], "correct": "To repair the Windows component store that SFC relies on"},
            {"q": "What is a practical difference between MBR and GPT for modern OS installs?",
             "options": ["GPT supports larger disks and more partitions and is typical for UEFI systems", "MBR is required for all NVMe drives", "GPT only works on Linux", "MBR encrypts the disk automatically"], "correct": "GPT supports larger disks and more partitions and is typical for UEFI systems"},
            {"q": "What does the Linux chmod command change?",
             "options": ["File mode/permissions bits", "The default route", "The CPU socket type", "The Wi-Fi channel"], "correct": "File mode/permissions bits"},
            {"q": "Why does accurate time matter on domain-joined Windows PCs?",
             "options": ["Authentication protocols like Kerberos are sensitive to clock skew", "It changes the color depth", "It sets the RAID level", "It assigns MAC addresses"], "correct": "Authentication protocols like Kerberos are sensitive to clock skew"},
            {"q": "What is a user profile on Windows primarily responsible for?",
             "options": ["Per-user settings and data under that account", "The physical RAM generation", "The switch VLAN database", "The PSU efficiency rating"], "correct": "Per-user settings and data under that account"},
            {"q": "What is Group Policy used for in many Windows environments?",
             "options": ["Centrally applying configuration and security settings to users/computers", "Replacing Ethernet cables", "Measuring optical power", "Formatting USB sticks only"], "correct": "Centrally applying configuration and security settings to users/computers"},
            {"q": "Why document steps during troubleshooting?",
             "options": ["So others can continue the work and so you can reverse changes safely", "Documentation is optional and never helps", "To hide root cause", "To avoid testing"], "correct": "So others can continue the work and so you can reverse changes safely"},
            {"q": "What is a safe first mindset when a volume will not mount after a crash?",
             "options": ["Prefer recovery/repair paths and backups before destructive wipe commands", "Always diskpart clean immediately", "Delete System32", "Disable the firewall only"], "correct": "Prefer recovery/repair paths and backups before destructive wipe commands"},
        ],
        [  # Security & professionalism formative
            {"q": "What is multi-factor authentication trying to ensure?",
             "options": ["That more than one independent factor is required to prove identity", "That passwords are never used", "That antivirus is disabled", "That all ports are open"], "correct": "That more than one independent factor is required to prove identity"},
            {"q": "What is the best immediate response when a user reports a suspicious email they did not open?",
             "options": ["Report/record it per process and verify no credentials were entered", "Ignore all phishing forever", "Reimage the mail server first", "Reply with your password"], "correct": "Report/record it per process and verify no credentials were entered"},
            {"q": "Why is change management used before risky production changes?",
             "options": ["To coordinate approval, timing, and recovery plans", "To slow work with no benefit", "To avoid documentation", "To disable monitoring"], "correct": "To coordinate approval, timing, and recovery plans"},
            {"q": "What does an anti-static wrist strap help prevent?",
             "options": ["Electrostatic discharge damage to components", "DNS cache poisoning", "VLAN hopping", "Weak Wi-Fi passwords"], "correct": "Electrostatic discharge damage to components"},
            {"q": "What should secure disposal of a retired hard drive include conceptually?",
             "options": ["Approved wipe or destruction so data cannot be recovered casually", "Only deleting the desktop icons", "Shipping it with labels showing customer data", "Formatting is never needed"], "correct": "Approved wipe or destruction so data cannot be recovered casually"},
            {"q": "What is a privacy screen an example of?",
             "options": ["A physical control reducing shoulder-surfing risk", "A network ACL", "A RAID level", "A subnet mask"], "correct": "A physical control reducing shoulder-surfing risk"},
            {"q": "When escalating a ticket, what should you provide?",
             "options": ["Clear symptoms, steps already tried, and impact", "Only the user password", "No context", "A demand to reimage without details"], "correct": "Clear symptoms, steps already tried, and impact"},
            {"q": "What is BitLocker primarily designed to protect?",
             "options": ["Data at rest on a volume through encryption", "Only DNS queries", "Only printer queues", "Only fan curves"], "correct": "Data at rest on a volume through encryption"},
            {"q": "Why avoid shared administrator passwords written on monitors?",
             "options": ["They enable unaccountable privileged access and are easy to abuse", "They improve MFA", "They encrypt traffic", "They replace backups"], "correct": "They enable unaccountable privileged access and are easy to abuse"},
            {"q": "What is a professional way to talk with a frustrated user?",
             "options": ["Listen, stay calm, explain in plain language, and set expectations", "Interrupt with jargon only", "Blame them immediately", "Share unrelated credentials"], "correct": "Listen, stay calm, explain in plain language, and set expectations"},
        ],
    ]

    for i, mod in enumerate(aplus_mods):
        bank = quiz_data[i % len(quiz_data)]
        # attach focus metadata if missing
        enriched = []
        for item in bank:
            it = dict(item)
            if not it.get('focus'):
                ql = (it.get('q') or '').lower()
                meta = None
                for key, triple in {
                    'form factor': ('Motherboard form factors', ['motherboard','form','atx'], 'Compare board sizes and expansion tradeoffs on real hardware.'),
                    'ddr5': ('Memory standards', ['memory','ddr','ram'], 'Relate DDR generation to slots, channels, and failure symptoms.'),
                    'nvme': ('Storage interfaces', ['storage','nvme','pcie','ssd'], 'Map media to bus and expected performance characteristics.'),
                    'raid 1': ('RAID and data protection', ['raid','mirror'], 'Separate mirroring from backup policy.'),
                    'raid 5': ('RAID and data protection', ['raid','parity'], 'Know minimum disks and rebuild impact.'),
                    'socket': ('CPU packaging and cooling', ['cpu','socket','lga'], 'Connect socket, cooler, and thermal interface into one install path.'),
                    'dual-channel': ('Memory channels', ['memory','channel'], 'Practice correct slot population for channel mode.'),
                    '24-pin': ('Power delivery', ['psu','power'], 'Identify major PSU connectors and symptoms of a missing rail.'),
                    'uefi': ('Firmware and boot', ['uefi','bios','boot'], 'Change boot order and Secure Boot with a clear rollback plan.'),
                    'thermal paste': ('CPU packaging and cooling', ['thermal','cpu'], 'Apply paste and seat coolers safely.'),
                    'https': ('Ports and services', ['https','443'], 'Link services users request to default ports.'),
                    'private': ('IPv4 addressing', ['ipv4','private'], 'Read client IP config and spot private vs APIPA addresses.'),
                    'ping': ('Connectivity testing', ['ping','connectivity'], 'Place ping inside a wider isolation order.'),
                    'rj-45': ('Physical Ethernet', ['ethernet','cable'], 'Check physical layer before blaming the OS.'),
                    'apipa': ('IPv4 addressing', ['apipa','dhcp'], 'Treat APIPA as DHCP path failure and continue ordered checks.'),
                    'rdp': ('Ports and services', ['rdp','3389'], 'Tie remote access ports to policy and exposure risk.'),
                    'dns primarily': ('Name resolution', ['dns','hostname'], 'Separate “IP works / name fails” from total outage.'),
                    'dhcp': ('DHCP and client config', ['dhcp','lease'], 'Explain what a complete lease must include.'),
                    'ssh': ('Ports and services', ['ssh','22'], 'Prefer encrypted admin protocols and know their ports.'),
                    'gateway': ('Routing basics', ['gateway','routing'], 'Predict on-link vs remote destinations.'),
                    'sfc': ('Windows repair tools', ['sfc','windows'], 'Use integrity tools before opportunistic reinstalls.'),
                    'gpt': ('Disk partitioning', ['gpt','mbr'], 'Choose disk style for capacity and platform needs.'),
                    'ntfs': ('Windows filesystems', ['ntfs','permissions'], 'Apply NTFS features to real permission and recovery tasks.'),
                    'chmod': ('Linux permissions', ['linux','chmod'], 'Read and set modes deliberately.'),
                    'directory contents': ('Linux CLI', ['linux','ls'], 'Grow a reliable CLI checklist for support.'),
                    'dism': ('Windows repair tools', ['dism','image'], 'Repair the component store with intent, not guesswork.'),
                    'mbr is limited': ('Disk partitioning', ['mbr','gpt'], 'State MBR limits that drive GPT adoption.'),
                    'startup': ('Windows client config', ['startup'], 'Manage startup impact without breaking required agents.'),
                    'ext4': ('Linux storage', ['linux','ext4'], 'Recognize common Linux filesystems in the field.'),
                    'least privilege': ('Access control', ['privilege','security'], 'Grant only what the role needs.'),
                    'mfa': ('Authentication', ['mfa','authentication'], 'Describe multi-factor design without reducing it to a product name.'),
                    'esd': ('Workplace safety', ['esd','safety'], 'Control static before internal component work.'),
                    'malware': ('Malware response', ['malware','security'], 'Follow a disciplined incident sequence.'),
                    'privacy screen': ('Physical security', ['physical','privacy'], 'Use physical controls for exposed workstations.'),
                    'change management': ('Change control', ['change','documentation'], 'Document changes with rollback in mind.'),
                    'escalat': ('Ticketing and escalation', ['escalation','ticket'], 'Escalate with evidence and impact.'),
                    'anti-static': ('Workplace safety', ['esd','safety'], 'Use ESD gear correctly.'),
                    'bitlocker': ('Endpoint encryption', ['bitlocker','encryption'], 'Handle recovery keys as controlled secrets.'),
                    'communication': ('Professional communication', ['communication'], 'Update users in plain language.'),
                    'disposal': ('Media sanitization', ['disposal','wipe'], 'Match destruction method to data classification.'),
                    'osi': ('OSI and routing', ['osi','layer'], 'Map symptoms to the layer under test.'),
                    'udp': ('Transport protocols', ['tcp','udp'], 'Match transport choice to application needs.'),
                    'cidr': ('Subnetting', ['cidr','subnet'], 'Convert prefix length to host capacity with confidence.'),
                    'dns primarily uses': ('DNS services', ['dns','53'], 'Trace name resolution failures that affect many users.'),
                    'topology': ('Topologies', ['topology','switch'], 'Spot single points of failure in common layouts.'),
                    'ipv6': ('IPv6 addressing', ['ipv6'], 'Read basic IPv6 notation without avoiding the topic.'),
                    'ospf': ('Dynamic routing', ['ospf','routing'], 'Contrast static and dynamic routing at a support level.'),
                    'arp': ('Local delivery', ['arp','mac'], 'Use ARP to explain local delivery problems.'),
                    'layer 3 switch': ('Switching and inter-VLAN routing', ['vlan','switch','routing'], 'Explain when a L3 switch routes between VLANs.'),
                    '802.11': ('Wireless standards', ['wireless','wifi'], 'Relate Wi-Fi generation to expected capability.'),
                    'poe': ('Power over Ethernet', ['poe','power'], 'Match PoE budget to device draw.'),
                    'fiber': ('Optical media', ['fiber','single-mode'], 'Choose media for distance and environment.'),
                    'wpa3': ('Wireless security', ['wpa','wireless','security'], 'Prefer modern WLAN security modes.'),
                }.items():
                    if key in ql:
                        meta = triple
                        break
                if meta:
                    it['focus'], it['keywords'], it['study_tip'] = meta
                else:
                    it['focus'] = f'Chapter {mod.order} fundamentals'
                    it['keywords'] = []
                    it['study_tip'] = 'Revisit this chapter end-to-end and practice the workflow on a sample ticket.'
            enriched.append(it)
        bank = enriched
        qs = [{
            "text": item["q"],
            "options": item["options"],
            "correct": item["correct"],
            "lo": f"LO-CH-{mod.order}",
            "lo_text": item.get("focus") or f"Progress check for chapter {mod.order}",
            "focus": item.get("focus") or f"Progress check for chapter {mod.order}",
            "keywords": item.get("keywords") or [],
            "study_tip": item.get("study_tip") or "Revisit this chapter's lessons and practice the workflow, not a single fact.",
        } for item in bank]
        db.session.add(Quiz(module_id=mod.id, title=f'Progress Check: {mod.title}', questions=json.dumps(qs)))

    net_mods = Module.query.filter_by(course_id=netplus.id).order_by(Module.order).all()
    net_quiz_data = [
        [
            {"q": "What is the simplest description of the OSI model for a beginner?",
             "options": ["A rigid law that forbids TCP", "A layered way to talk about network functions from media to applications", "A brand of switch", "A type of fiber connector"], "correct": "A layered way to talk about network functions from media to applications"},
            {"q": "What does a router primarily do that a pure Layer-2 switch does not?",
             "options": ["Forward between different IP networks using routing information", "Learn only MAC addresses", "Assign printer drivers", "Generate thermal paste"], "correct": "Forward between different IP networks using routing information"},
            {"q": "Why do we subnet networks?",
             "options": ["To size address spaces and control broadcast domains according to design", "To increase toner density", "To remove the need for switches", "To disable ARP"], "correct": "To size address spaces and control broadcast domains according to design"},
            {"q": "How do switches separate groups of ports into different broadcast domains without separate physical switches?",
             "options": ["Logical segmentation of traffic on switches", "Encrypting hard drives", "Cooling CPUs", "Assigning UEFI passwords"], "correct": "Logical segmentation of traffic on switches"},
            {"q": "What does TCP provide that UDP does not emphasize the same way?",
             "options": ["Connection-oriented reliable ordered delivery mechanisms", "Always lower latency for video", "Automatic VLAN tags", "Optical amplification"], "correct": "Connection-oriented reliable ordered delivery mechanisms"},
            {"q": "What is a common reason to use fiber between buildings?",
             "options": ["Distance and immunity to electrical interference compared with copper Ethernet limits", "Cheaper than Cat6 for 1 meter desk runs always", "It replaces DNS", "It powers PoE phones without copper"], "correct": "Distance and immunity to electrical interference compared with copper Ethernet limits"},
            {"q": "What is the purpose of a network ACL on a router/firewall?",
             "options": ["Permit or deny traffic according to policy", "Format disks", "Assign hostnames automatically without DNS", "Measure fan RPM"], "correct": "Permit or deny traffic according to policy"},
            {"q": "What is a DMZ commonly for?",
             "options": ["Hosting services that need controlled exposure separate from the internal LAN", "Storing domain admin passwords", "Disabling logging", "Replacing backups"], "correct": "Hosting services that need controlled exposure separate from the internal LAN"},
            {"q": "Why use SSH instead of Telnet for device management?",
             "options": ["SSH encrypts the management session", "Telnet is faster for passwords", "SSH disables all authentication", "Telnet supports MFA natively"], "correct": "SSH encrypts the management session"},
            {"q": "What should you change when troubleshooting so you can tell what fixed the issue?",
             "options": ["One clear variable at a time when practical, and document results", "Everything at once always", "Nothing—only reboot forever", "Only the desktop wallpaper"], "correct": "One clear variable at a time when practical, and document results"},
        ],
        [
            {"q": "What does ARP do on an Ethernet LAN?",
             "options": ["Maps IPv4 addresses to MAC addresses", "Encrypts TLS", "Creates OSPF areas", "Assigns BGP AS numbers"], "correct": "Maps IPv4 addresses to MAC addresses"},
            {"q": "What is a default route used for?",
             "options": ["Forwarding traffic toward destinations not matched by more specific routes", "Storing email", "Building RAID arrays", "Flashing BIOS"], "correct": "Forwarding traffic toward destinations not matched by more specific routes"},
            {"q": "What is port security or 802.1X trying to reduce?",
             "options": ["Unauthorized devices attaching to the network edge", "CPU heat", "DNS TTL", "Cable category"], "correct": "Unauthorized devices attaching to the network edge"},
            {"q": "When logs are unclear, what kind of tool lets you inspect protocol messages on the wire for diagnosis?",
             "options": ["Seeing protocol exchanges when diagnosing complex issues", "Increasing link speed beyond physics", "Replacing fiber splices", "Powering APs"], "correct": "Seeing protocol exchanges when diagnosing complex issues"},
            {"q": "What addressing detail inside a private LAN is often not visible to hosts on the public Internet when a gateway translates traffic?",
             "options": ["Private internal addresses behind a shared public mapping", "All DNS names forever", "Switch MAC tables from the switch itself", "Optical power readings"], "correct": "Private internal addresses behind a shared public mapping"},
            {"q": "Why monitor interface errors and utilization?",
             "options": ["To detect saturation, faults, and capacity problems early", "To set desktop themes", "To choose toner color", "To update UEFI automatically"], "correct": "To detect saturation, faults, and capacity problems early"},
            {"q": "What is a wireless survey helping you decide?",
             "options": ["Coverage, capacity, and interference for AP placement", "RAID stripe size", "PSU wattage only", "Domain functional level"], "correct": "Coverage, capacity, and interference for AP placement"},
            {"q": "What is syslog commonly used for?",
             "options": ["Centralizing device event messages for operations and IR", "Crimping RJ-45 ends", "Cooling GPUs", "Assigning VLANs via DHCP option only"], "correct": "Centralizing device event messages for operations and IR"},
            {"q": "What is a trunk port carrying between switches?",
             "options": ["Multiple VLANs with tagging (such as 802.1Q)", "Only power", "Only console serial", "Only printer jobs"], "correct": "Multiple VLANs with tagging (such as 802.1Q)"},
            {"q": "What is a professional escalation package?",
             "options": ["Timeline, impact, evidence, and steps already tried", "Only the user password", "A demand with no data", "A screenshot of the desktop background only"], "correct": "Timeline, impact, evidence, and steps already tried"},
        ],
        [
            {"q": "What does “interesting traffic” mean for many site-to-site VPNs?",
             "options": ["The traffic selectors that should enter the tunnel", "Any broadcast on the LAN", "Only social media", "Only printer discovery"], "correct": "The traffic selectors that should enter the tunnel"},
            {"q": "What is a benefit of network segmentation?",
             "options": ["Limits blast radius and can enforce different security policies", "Removes the need for authentication", "Makes all hosts administrators", "Disables monitoring"], "correct": "Limits blast radius and can enforce different security policies"},
            {"q": "What does an optical power meter help verify?",
             "options": ["Light levels on fiber links", "RAM timings", "Domain lockout policy", "Toner type"], "correct": "Light levels on fiber links"},
            {"q": "What is a practical first step when one VLAN has Internet and another does not?",
             "options": ["Compare routing and policy differences between the VLANs", "Replace all patch cords with USB", "Disable STP globally immediately", "Format the core switch"], "correct": "Compare routing and policy differences between the VLANs"},
            {"q": "Why keep network device firmware updated under change control?",
             "options": ["Security fixes and stability improvements with a tested process", "To randomly break configs without tickets", "Because firmware updates replace fiber", "Because it assigns DNS"], "correct": "Security fixes and stability improvements with a tested process"},
            {"q": "What is a loop in Layer 2 without STP protection likely to cause?",
             "options": ["Broadcast storms and outage risk", "Faster DNS only", "Automatic encryption", "Higher toner yield"], "correct": "Broadcast storms and outage risk"},
            {"q": "What is a runbook useful for in operations?",
             "options": ["Consistent steps for common incidents and changes", "Hiding credentials in chat", "Avoiding documentation", "Skipping verification"], "correct": "Consistent steps for common incidents and changes"},
            {"q": "What does capacity planning look at?",
             "options": ["Whether links and devices can handle expected load", "Only the color of patch panels", "Only the number of fonts on diagrams", "Only the office coffee stock"], "correct": "Whether links and devices can handle expected load"},
            {"q": "What is an indicator that a WAN link is saturated?",
             "options": ["High utilization with latency/loss symptoms under load", "Idle interface at 0%", "Perfect voice quality always", "No SNMP counters"], "correct": "High utilization with latency/loss symptoms under load"},
            {"q": "What should you do after implementing a network fix?",
             "options": ["Verify services with the user/stakeholder and document the outcome", "Leave without testing", "Delete the logs", "Disable monitoring"], "correct": "Verify services with the user/stakeholder and document the outcome"},
        ],
    ]

    for i, mod in enumerate(net_mods):
        bank = net_quiz_data[i % len(net_quiz_data)]
        enriched = []
        for item in bank:
            it = dict(item)
            if not it.get("focus"):
                it["focus"] = f"Network chapter {mod.order} fundamentals"
                it["keywords"] = []
                it["study_tip"] = "Study the full chapter workflows—addressing, paths, and verification—not a single fact."
            enriched.append(it)
        bank = enriched
        qs = [{
            "text": item["q"],
            "options": item["options"],
            "correct": item["correct"],
            "lo": f"LO-NET-{mod.order}",
            "lo_text": item.get("focus") or f"Progress check for network chapter {mod.order}",
            "focus": item.get("focus") or f"Progress check for network chapter {mod.order}",
            "keywords": item.get("keywords") or [],
            "study_tip": item.get("study_tip") or "Study the full chapter workflows—not a single fact.",
        } for item in bank]
        db.session.add(Quiz(module_id=mod.id, title=f'Progress Check: {mod.title}', questions=json.dumps(qs)))
    db.session.commit()

    used_stems = set()
    for mod in Module.query.all():
        for qz in Quiz.query.filter_by(module_id=mod.id).all():
            for item in json.loads(qz.questions or '[]'):
                used_stems.add(_question_stem_key(item.get('text') or item.get('q') or ''))

    aplus_tests = []
    for title, desc, order, qs in tests_aplus():
        filtered = _filter_unused_questions(list(qs), used_stems, min_keep=45)
        aplus_tests.append((title, desc, order, filtered))
    for title, desc, order, qs in aplus_tests:
        db.session.add(KnowledgeTest(
            course_id=aplus.id, title=title, description=desc, order=order,
            questions=json.dumps(qs), passing_score=80, time_limit_minutes=75
        ))

    net_tests = []
    for title, desc, order, qs in tests_netplus():
        filtered = _filter_unused_questions(list(qs), used_stems, min_keep=45)
        net_tests.append((title, desc, order, filtered))
    for title, desc, order, qs in net_tests:
        db.session.add(KnowledgeTest(
            course_id=netplus.id, title=title, description=desc, order=order,
            questions=json.dumps(qs), passing_score=80, time_limit_minutes=75
        ))
    db.session.commit()

    # Integrity: graded tests must not reuse progress-check stems
    quiz_keys = set()
    for qz in Quiz.query.all():
        for item in json.loads(qz.questions or '[]'):
            quiz_keys.add(_question_stem_key(item.get('text') or item.get('q') or ''))
    leaked = []
    for kt in KnowledgeTest.query.all():
        for item in json.loads(kt.questions or '[]'):
            key = _question_stem_key(item.get('text') or '')
            if key and key in quiz_keys:
                leaked.append((kt.title, item.get('text', '')[:80]))
            else:
                for qk in quiz_keys:
                    if _stems_overlap(key, qk):
                        leaked.append((kt.title, item.get('text', '')[:80]))
                        break
    if leaked:
        # Strip leaks rather than ship overlapping forms
        for kt in KnowledgeTest.query.all():
            kept = []
            for item in json.loads(kt.questions or '[]'):
                key = _question_stem_key(item.get('text') or '')
                if key in quiz_keys or any(_stems_overlap(key, qk) for qk in quiz_keys):
                    continue
                kept.append(item)
            kt.questions = json.dumps(kept)
        db.session.commit()

    section_a = ClassSection(
        name='IT Support Spring 2026 — Section A',
        course_id=aplus.id,
        instructor_id=instr1.id,
        max_students=25,
        start_date=datetime(2026, 1, 15).date(),
        end_date=datetime(2026, 5, 15).date(),
    )
    section_b = ClassSection(
        name='Networking Spring 2026 — Section B',
        course_id=netplus.id,
        instructor_id=instr1.id,
        max_students=25,
        start_date=datetime(2026, 1, 15).date(),
        end_date=datetime(2026, 5, 15).date(),
    )
    section_c = ClassSection(
        name='IT Support Spring 2026 — Section C',
        course_id=aplus.id,
        instructor_id=instr2.id,
        max_students=20,
        start_date=datetime(2026, 2, 1).date(),
        end_date=datetime(2026, 6, 1).date(),
    )
    db.session.add_all([section_a, section_b, section_c])
    db.session.flush()
    grant_section_instructor_access(section_a.id, instr1.id, primary=True)
    grant_section_instructor_access(section_b.id, instr1.id, primary=True)
    grant_section_instructor_access(section_c.id, instr2.id, primary=True)
    db.session.commit()

    for s in students[:22]:
        db.session.add(Enrollment(user_id=s.id, section_id=section_a.id, progress_percent=0))
    for s in students[3:25]:
        db.session.add(Enrollment(user_id=s.id, section_id=section_b.id, progress_percent=0))
    for s in students[10:18]:
        db.session.add(Enrollment(user_id=s.id, section_id=section_c.id, progress_percent=0))
    db.session.commit()

    # Pre-activate ALL modules for demo sections so students can open full curriculum
    for sec in (section_a, section_b, section_c):
        mods = Module.query.filter_by(course_id=sec.course_id).all()
        for mod in mods:
            db.session.add(ContentRelease(
                section_id=sec.id,
                content_type='module',
                content_id=mod.id,
                is_active=True,
                available_from=datetime.utcnow() - timedelta(days=1),
                available_until=datetime.utcnow() + timedelta(days=90),
                activated_by=sec.instructor_id,
                activated_at=datetime.utcnow(),
            ))
    db.session.commit()

    # Extra class for richer admin comparison
    section_d = ClassSection(
        name='Networking Spring 2026 — Section D',
        course_id=netplus.id,
        instructor_id=instr2.id,
        max_students=22,
        start_date=datetime(2026, 2, 10).date(),
        end_date=datetime(2026, 6, 10).date(),
    )
    db.session.add(section_d)
    db.session.commit()
    for s in students[5:20]:
        db.session.add(Enrollment(user_id=s.id, section_id=section_d.id, progress_percent=random.randint(20, 95)))
    for mod in Module.query.filter_by(course_id=netplus.id).all():
        db.session.add(ContentRelease(
            section_id=section_d.id, content_type='module', content_id=mod.id,
            is_active=True,
            available_from=datetime.utcnow() - timedelta(days=1),
            available_until=datetime.utcnow() + timedelta(days=90),
            activated_by=instr2.id, activated_at=datetime.utcnow(),
        ))
    db.session.commit()

    # Demo completed knowledge tests — varied class strength for heat maps
    import random as _rnd
    _rnd.seed(42)
    demo_sections = [section_a, section_b, section_c, section_d]
    strength = {
        section_a.id: 0.86,  # strong
        section_b.id: 0.74,
        section_c.id: 0.58,  # needs support
        section_d.id: 0.79,
    }
    for sec in demo_sections:
        tests = KnowledgeTest.query.filter_by(course_id=sec.course_id).all()
        enrolled = Enrollment.query.filter_by(section_id=sec.id).all()
        base = strength.get(sec.id, 0.7)
        for enr in enrolled:
            for ti, test in enumerate(tests):
                # Not every student took every test
                if _rnd.random() < 0.12:
                    continue
                qs = json.loads(test.questions or '[]')
                if not qs:
                    continue
                answers = {}
                correct_n = 0
                for i, q in enumerate(qs):
                    opts = list(q.get('options') or [])
                    correct = q.get('correct')
                    cat = _broad_category(q)
                    p = base + _rnd.uniform(-0.1, 0.1)
                    if cat == 'Security':
                        p -= 0.07
                    if cat == 'Networking' and sec.id in (section_c.id,):
                        p -= 0.14
                    if cat == 'Hardware & Devices' and sec.id == section_a.id:
                        p += 0.06
                    if cat == 'Operating Systems & Software' and sec.id == section_c.id:
                        p -= 0.05
                    p = max(0.22, min(0.96, p))
                    if correct is not None and _rnd.random() < p:
                        answers[str(i)] = correct
                        correct_n += 1
                    else:
                        wrong = [o for o in opts if o != correct]
                        answers[str(i)] = _rnd.choice(wrong) if wrong else (correct or '')
                score = round(100.0 * correct_n / len(qs), 1)
                day_ago = _rnd.randint(1, 45)
                db.session.add(TestAttempt(
                    user_id=enr.user_id,
                    test_id=test.id,
                    section_id=sec.id,
                    answers=json.dumps(answers),
                    score=score,
                    passed=score >= 80,
                    started_at=datetime.utcnow() - timedelta(days=day_ago, hours=2),
                    completed_at=datetime.utcnow() - timedelta(days=day_ago),
                ))
        # light progress marks
        for enr in enrolled:
            enr.progress_percent = _rnd.randint(15, 100)
    db.session.commit()
    print('Database seeded successfully (with demo test analytics).')


def render_lesson_html(text):
    """Turn stored lesson text into real HTML (never show # or raw <br>)."""
    if not text:
        return '<p class="text-muted">No lesson content.</p>'
    raw = text.replace('\r\n', '\n').replace('\r', '\n')
    # Already HTML from lessons.py
    if '<h2' in raw or '<h3' in raw or '<p>' in raw:
        return raw
    import re
    import html as html_mod
    t = html_mod.escape(raw)
    t = re.sub(r'^###\s+(.+)$', r'<h5 class="mt-3">\1</h5>', t, flags=re.M)
    t = re.sub(r'^##\s+(.+)$', r'<h4 class="mt-4">\1</h4>', t, flags=re.M)
    t = re.sub(r'^#\s+(.+)$', r'<h3 class="mt-2">\1</h3>', t, flags=re.M)
    t = re.sub(r'^[-*]\s+(.+)$', r'<li>\1</li>', t, flags=re.M)
    t = re.sub(r'(?:<li>.*</li>\n?)+', lambda m: '<ul class="mb-3">' + m.group(0) + '</ul>', t)
    blocks = re.split(r'\n{2,}', t)
    out = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith('<h') or b.startswith('<ul'):
            out.append(b)
        else:
            out.append('<p class="mb-3">' + b.replace('\n', ' ') + '</p>')
    return '\n'.join(out)


@app.template_filter('simple_md')
def simple_md(text):
    return render_lesson_html(text)


@app.template_filter('render_lesson')
def render_lesson_filter(text):
    return render_lesson_html(text)


def sync_curriculum():
    """Overwrite lesson HTML in an existing DB so students see real pages."""
    aplus = Course.query.filter_by(code='ITSUP').first() or Course.query.filter_by(code='APLUS').first()
    netplus = Course.query.filter_by(code='NETOPS').first() or Course.query.filter_by(code='NETPLUS').first()
    if not aplus or not netplus:
        return False
    aplus.code, aplus.title = 'ITSUP', 'IT Support Technician Fundamentals'
    aplus.description = 'Hardware, software, networking, security, and operational procedures for IT support technicians.'
    netplus.code, netplus.title = 'NETOPS', 'Network Operations Fundamentals'
    netplus.description = 'Networking concepts, infrastructure, operations, security, and troubleshooting.'

    for course, pack in ((aplus, APLUS_LESSONS), (netplus, NETPLUS_LESSONS)):
        for ch in pack:
            if isinstance(ch, dict):
                order, title, mins = ch['order'], ch['title'], ch.get('minutes', 60)
                overview = ch.get('overview', '')
                lesson_list = ch.get('lessons', [])
            else:
                order, title, mins, html = ch
                overview, lesson_list = html, []
            m = Module.query.filter_by(course_id=course.id, order=order).first()
            if not m:
                m = Module(course_id=course.id, order=order, title=title, content=overview, estimated_minutes=mins)
                db.session.add(m)
                db.session.flush()
            else:
                m.title = title
                m.content = overview
                m.estimated_minutes = mins
                db.session.flush()
            # replace lessons for module
            Lesson.query.filter_by(module_id=m.id).delete()
            for les in lesson_list:
                db.session.add(Lesson(
                    module_id=m.id, title=les['title'], order=les['order'],
                    content=les['html'], estimated_minutes=les.get('minutes', 30)
                ))
    used_stems = set()
    for mod in Module.query.all():
        for qz in Quiz.query.filter_by(module_id=mod.id).all():
            for item in json.loads(qz.questions or '[]'):
                used_stems.add(_question_stem_key(item.get('text') or item.get('q') or ''))
    for course, tests in ((aplus, tests_aplus()), (netplus, tests_netplus())):
        for title, desc, order, qs in tests:
            qs = _filter_unused_questions(list(qs), used_stems, min_keep=45)
            kt = KnowledgeTest.query.filter_by(course_id=course.id, order=order).first()
            payload = json.dumps(qs)
            if not kt:
                db.session.add(KnowledgeTest(
                    course_id=course.id, title=title, description=desc, order=order,
                    questions=payload, passing_score=80, time_limit_minutes=75
                ))
            else:
                kt.title = title
                kt.description = desc
                kt.questions = payload
                kt.time_limit_minutes = 75
    # Ensure progress quizzes carry focus metadata for study-plan results
    for qz in Quiz.query.all():
        try:
            items = json.loads(qz.questions or '[]')
        except Exception:
            continue
        changed = False
        for it in items:
            if it.get('focus') and it.get('study_tip'):
                continue
            ql = (it.get('text') or it.get('q') or '').lower()
            it.setdefault('focus', 'Chapter fundamentals')
            it.setdefault('keywords', [])
            it.setdefault(
                'study_tip',
                'Revisit the related lessons and practice the workflow end to end—not a single definition.',
            )
            # light keyword tagging from stem
            for token in re.findall(r'[a-z]{4,}', ql):
                if token not in it['keywords']:
                    it['keywords'].append(token)
            changed = True
        if changed:
            qz.questions = json.dumps(items)
    db.session.commit()
    return True


def _curriculum_outdated():
    if User.query.count() == 0:
        return True
    if Lesson.query.count() < 50:
        return True
    sample = Lesson.query.first()
    if sample and len(sample.content or '') < 3000:
        return True
    if sample and 'In plain English' not in (sample.content or ''):
        return True
    cap = Lesson.query.filter(Lesson.title.ilike('%capstone%')).first()
    if cap and 'Live demonstration' not in (cap.content or ''):
        return True
    if sample and 'Builds on:' not in (sample.content or '') and Lesson.query.count() > 1:
        # first lesson may use "Where this fits"; second should bridge
        second = Lesson.query.order_by(Lesson.id).offset(1).first()
        if second and 'Builds on:' not in (second.content or '') and 'Where this fits' not in (second.content or ''):
            return True
    qz = Quiz.query.first()
    if not qz:
        return True
    try:
        nq = len(json.loads(qz.questions))
    except Exception:
        nq = 0
    kt = KnowledgeTest.query.first()
    nt = 0
    if kt:
        try:
            nt = len(json.loads(kt.questions))
        except Exception:
            nt = 0
    mod = Module.query.first()
    html_lessons = bool(Lesson.query.first() and 'analogy-box' in (Lesson.query.first().content or ''))
    c0 = Course.query.first()
    old_brand = bool(c0 and ('CompTIA' in (c0.title or '') or c0.code in ('APLUS', 'NETPLUS')))
    return nq < 8 or nt < 40 or not html_lessons or old_brand


def _ensure_schema():
    """Add columns/tables introduced after first install (SQLite-friendly)."""
    try:
        from sqlalchemy import text, inspect
        insp = inspect(db.engine)
        tables = set(insp.get_table_names())
        if 'curriculum_ticket' in tables:
            cols = {c['name'] for c in insp.get_columns('curriculum_ticket')}
            with db.engine.begin() as conn:
                if 'resolution' not in cols:
                    conn.execute(text('ALTER TABLE curriculum_ticket ADD COLUMN resolution VARCHAR(40)'))
                if 'fixed_at' not in cols:
                    conn.execute(text('ALTER TABLE curriculum_ticket ADD COLUMN fixed_at DATETIME'))
                if 'fixed_by_id' not in cols:
                    conn.execute(text('ALTER TABLE curriculum_ticket ADD COLUMN fixed_by_id INTEGER'))
                if 'quoted_text' not in cols:
                    conn.execute(text('ALTER TABLE curriculum_ticket ADD COLUMN quoted_text TEXT'))
                if 'quiz_id' not in cols:
                    conn.execute(text('ALTER TABLE curriculum_ticket ADD COLUMN quiz_id INTEGER'))
                if 'test_id' not in cols:
                    conn.execute(text('ALTER TABLE curriculum_ticket ADD COLUMN test_id INTEGER'))
        if 'content_release' in tables:
            rcols = {c['name'] for c in insp.get_columns('content_release')}
            if 'user_id' not in rcols:
                with db.engine.begin() as conn:
                    conn.execute(text('ALTER TABLE content_release ADD COLUMN user_id INTEGER'))
    except Exception as e:
        print('Schema ensure note:', e)


def init_db():
    db.create_all()
    _ensure_schema()
    if User.query.count() == 0:
        print('Seeding database...')
        seed_database()
        return
    # Do not drop_all on an existing schoolhouse DB — that hangs startup
    # and looks like the site is down. Sync lesson text only.
    try:
        sync_curriculum()
    except Exception as e:
        print('Curriculum sync note:', e)


with app.app_context():
    init_db()




# ---------- Premium free narration (edge-tts neural + file URL) ----------
@app.route('/api/narrate', methods=['POST'])
@login_required
def api_narrate():
    """Synthesize neural speech; return a playable URL (not giant base64)."""
    import hashlib
    import json
    import re
    import tempfile
    import threading
    from pathlib import Path as _Path

    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'No text'}), 400
    # Keep first chunk snappy so Play "just works"
    max_chars = 3500
    truncated = False
    if len(text) > max_chars:
        cut = text.rfind('. ', 0, max_chars)
        if cut < max_chars // 2:
            cut = max_chars
        text = text[:cut + 1].strip()
        truncated = True

    voice = (data.get('voice') or 'en-US-JennyNeural').strip()
    if voice not in ('en-US-JennyNeural', 'en-US-GuyNeural'):
        voice = 'en-US-JennyNeural'

    cache_dir = _Path(tempfile.gettempdir()) / 'ciwt_tts'
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256((voice + '|' + text).encode('utf-8')).hexdigest()[:40]
    mp3_path = cache_dir / f'{key}.mp3'
    meta_path = cache_dir / f'{key}.json'

    def _estimate_words(txt, duration_sec):
        tokens = re.findall(r'\S+', txt)
        if not tokens or duration_sec <= 0:
            return []
        weights = [max(1, len(re.sub(r'[^\w]', '', w))) for w in tokens]
        total_w = sum(weights) or 1
        t0 = 0.05
        usable = max(0.2, duration_sec - 0.2)
        out = []
        for tok, w in zip(tokens, weights):
            dur = usable * (w / total_w)
            out.append({'text': tok, 'start': round(t0, 3), 'end': round(t0 + dur, 3)})
            t0 += dur
        return out

    def _run_tts():
        import edge_tts
        import asyncio
        async def _save():
            await edge_tts.Communicate(text, voice, rate='-4%').save(str(mp3_path))
        try:
            asyncio.run(_save())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_save())
            finally:
                loop.close()

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        return jsonify({'error': 'edge-tts not installed. Run: pip install edge-tts', 'fallback': True}), 503

    if not mp3_path.exists() or mp3_path.stat().st_size < 400:
        err_box = {}
        def worker():
            try:
                _run_tts()
            except Exception as e:
                err_box['e'] = f'{type(e).__name__}: {e}'
        th = threading.Thread(target=worker)
        th.start()
        th.join(timeout=120)
        if th.is_alive():
            return jsonify({'error': 'TTS timed out', 'fallback': True}), 504
        if err_box.get('e'):
            return jsonify({'error': err_box['e'], 'fallback': True}), 500
        if not mp3_path.exists() or mp3_path.stat().st_size < 400:
            return jsonify({'error': 'No audio produced', 'fallback': True}), 500

    duration = max(1.0, len(text) / 12.2)
    words = _estimate_words(text, duration)
    meta_path.write_text(json.dumps({'words': words, 'voice': voice}))

    return jsonify({
        'url': url_for('api_narrate_file', key=key),
        'words': words,
        'voice': voice,
        'truncated': truncated,
        'duration_est': duration,
    })


@app.route('/api/narrate/file/<key>')
@login_required
def api_narrate_file(key):
    """Serve cached neural MP3."""
    import re
    import tempfile
    from pathlib import Path as _Path
    if not re.fullmatch(r'[0-9a-f]{20,64}', key or ''):
        abort(404)
    path = _Path(tempfile.gettempdir()) / 'ciwt_tts' / f'{key}.mp3'
    if not path.exists():
        abort(404)
    return send_file(path, mimetype='audio/mpeg', conditional=True, download_name='narration.mp3')


@app.route('/api/narrate/voices')
@login_required
def api_narrate_voices():
    return jsonify({
        'voices': [
            {'id': 'en-US-JennyNeural', 'label': 'Jenny — neural instructor'},
            {'id': 'en-US-GuyNeural', 'label': 'Guy — neural instructor'},
        ],
        'default': 'en-US-JennyNeural',
    })


def _ensure_section_access_table():
    """Create access table if missing and backfill primary instructors."""
    with app.app_context():
        db.create_all()
        for sec in ClassSection.query.all():
            if sec.instructor_id:
                existing = SectionInstructorAccess.query.filter_by(
                    section_id=sec.id, user_id=sec.instructor_id
                ).first()
                if not existing:
                    db.session.add(SectionInstructorAccess(
                        section_id=sec.id,
                        user_id=sec.instructor_id,
                        is_primary=True,
                    ))
        db.session.commit()


_ensure_section_access_table()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=True)
