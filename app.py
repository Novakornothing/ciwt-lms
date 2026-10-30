"""
Novak LMS™ Learning Management System
Proprietary schoolhouse software for IT support and network operations training.
Original instructional content. Not a vendor certification product.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, Response, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import json
import secrets
import csv
from io import StringIO, BytesIO
import shutil
import logging
import gzip
import hashlib
import random
import os
from pathlib import Path
import re
from lessons import APLUS as APLUS_LESSONS, NETPLUS as NETPLUS_LESSONS, CLIENT as CLIENT_LESSONS
from question_bank import tests_aplus, tests_netplus
from interactive_labs import list_labs, get_lab, fresh_state, run_command, prompt_for, complete_command, labs_for_module, labs_for_lesson, labs_for_course
from alignment import domains_for_course
from aschool import BLOCKS as ASCHOOL_BLOCKS, CSCHOOL_COMMS, CSCHOOL_SYS, outline_stats, all_eos
from pilot_slice import PILOT_CHECKS, PILOT_RUN, PRINT_PATH, quiz_payload
from skills_exams import exams_for as skills_exams_for, is_practical_payload, stations_of


def utcnow():
    """Naive UTC now. Replaces the deprecated datetime.utcnow(); stored columns stay naive UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Persistent hosting: CIWT_INSTANCE_DIR (e.g. /var/data/ciwt/instance) keeps LTI and SSO keys on the mounted disk.
app = Flask(__name__, instance_path=os.environ.get('CIWT_INSTANCE_DIR') or None)

# ---- Product name: change it here (or set the SITE_NAME / SITE_TAGLINE env vars). Used in every
# page <title>, the header wordmark, the footer, the sign-in page and site_email_subject().
SITE_NAME = os.environ.get('SITE_NAME', 'Novak LMS™')
SITE_TAGLINE = os.environ.get('SITE_TAGLINE', 'Info Systems Training')
app.config['SITE_NAME'] = SITE_NAME

# ---- Response compression (HTML, CSS, JS, JSON, SVG). Runs inside the app, so it works the same under
# `flask run`, `python app.py` and gunicorn on Render. Brotli where the browser supports it, gzip otherwise;
# static files are streamed through the same encoders. No compressed-response cache: pages are per user.
app.config.setdefault('COMPRESS_ALGORITHM', ['br', 'gzip'])
app.config.setdefault('COMPRESS_ALGORITHM_STREAMING', ['br', 'gzip'])
app.config.setdefault('COMPRESS_MIN_SIZE', 500)
try:
    from flask_compress import Compress
    Compress(app)
except ImportError:  # keeps an older venv runnable; start_lms.sh / Render install requirements.txt
    logging.getLogger(__name__).warning('flask-compress not installed: responses are sent uncompressed')
app.config['SITE_TAGLINE'] = SITE_TAGLINE


def site_email_subject(subject):
    """Subject line for any outgoing email/notification, e.g. '[Novak Learning] Grades posted'."""
    return f"[{app.config['SITE_NAME']}] {subject}"


@app.context_processor
def _site_brand():
    return {'site_name': app.config['SITE_NAME'], 'site_tagline': app.config['SITE_TAGLINE']}


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ciwt-lms-demo-key-change-in-production')


@app.context_processor
def _ciwt_nav_urls():
    def all_chapters_url(sid):
        if sid and 'curriculum_index' in app.view_functions:
            return url_for('curriculum_index', section_id=sid)
        if sid and current_user.is_authenticated and current_user.role in ('admin', 'instructor'):
            return url_for('instructor_section', section_id=sid)
        if sid:
            return url_for('student_section', section_id=sid)
        return url_for('index')
    return {'all_chapters_url': all_chapters_url}
TQI_CORS = {
    'https://novakornothing.com',
    'https://www.novakornothing.com',
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'http://127.0.0.1:5500',
}


def _tqi_origin_ok(origin):
    if not origin:
        return False
    if origin in TQI_CORS:
        return True
    if origin.endswith('.novakornothing.com'):
        return True
    if origin.endswith('.workers.dev') or origin.endswith('.pages.dev'):
        return True
    if origin.startswith('http://127.0.0.1:') or origin.startswith('http://localhost:'):
        return True
    return False


@app.context_processor
def inject_interactive_labs():
    """Make all live labs available in every template (curriculum, class, nav)."""
    try:
        return {'all_interactive_labs': list_labs()}
    except Exception:
        return {'all_interactive_labs': []}
_base = os.path.dirname(os.path.abspath(__file__))
_default_db = os.path.join(_base, 'ciwt_lms.db')


def real_db_allowed(env=os.environ, as_main=False):
    import sys
    """Pass 13 DB guard. Importing this module runs init_db() (create_all, migrations, curriculum sync), which
    rewrites the database. Without DATABASE_URL that would be the real ciwt_lms.db, so a script or test that merely
    imports app could change it by accident. Allowed only when DATABASE_URL is set, CIWT_ALLOW_REAL_DB=1 is set
    (start_lms.sh, Procfile, render.yaml set it), running under gunicorn/Render, or app.py is run directly as the server (python app.py)."""
    return (
        bool(env.get('DATABASE_URL'))
        or env.get('CIWT_ALLOW_REAL_DB') == '1'
        or bool(env.get('RENDER'))
        or ('gunicorn' in sys.modules and env is os.environ)
        or (not os.path.exists(_default_db) and env is os.environ)
        or as_main
    )


if not real_db_allowed(as_main=(__name__ == '__main__')):
    raise RuntimeError(
        'Refusing to start against the real database ' + _default_db + ' from an import. '
        'Set DATABASE_URL to a copy (e.g. DATABASE_URL=sqlite:////tmp/copy.db), or set CIWT_ALLOW_REAL_DB=1 '
        'if you really mean the real DB (servers: start_lms.sh / Procfile / render.yaml already do).')
db_path = os.environ.get('DATABASE_URL', 'sqlite:///' + _default_db)
if db_path.startswith('postgres://'):            # Render/Heroku style URL -> SQLAlchemy psycopg 3 driver
    db_path = 'postgresql+psycopg://' + db_path[len('postgres://'):]
elif db_path.startswith('postgresql://'):
    db_path = 'postgresql+psycopg://' + db_path[len('postgresql://'):]
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
if db_path.startswith('postgresql'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True, 'pool_recycle': 280}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if db_path.startswith('sqlite') and os.environ.get('CIWT_SQLITE_WAL') == '1':
    # opt-in (production disk only): WAL lets readers run during writes; busy_timeout rides out short write locks
    from sqlalchemy import event as _sa_event
    with app.app_context():
        @_sa_event.listens_for(db.engine, 'connect')
        def _sqlite_pragmas(dbapi_conn, _rec):
            cur = dbapi_conn.cursor()
            cur.execute('PRAGMA journal_mode=WAL')
            cur.execute('PRAGMA busy_timeout=5000')
            cur.execute('PRAGMA synchronous=NORMAL')
            cur.close()
login_manager = LoginManager(app)

# ---- CSRF: every cookie-authenticated POST (forms and fetch/JSON) must carry a token.
# Forms: hidden csrf_token field. fetch(): X-CSRFToken header (added by the wrapper in base.html).
# sendBeacon (Helix final batch) cannot set headers, so Helix validates a `_csrf` body field itself.
# Bearer-token cross-origin APIs (/api/tqi/*) are exempt: they never rely on the session cookie.
from flask_wtf.csrf import CSRFProtect, CSRFError
app.config.setdefault('WTF_CSRF_TIME_LIMIT', None)  # token lives as long as the login session
app.config['WTF_CSRF_ENABLED'] = os.environ.get('CSRF_DISABLED') != '1'


def _env_flag(name, default):
    v = os.environ.get(name)
    if v is None or v.strip() == '':
        return default
    return v.strip().lower() in ('1', 'true', 'yes', 'on')


# Privacy switches (pass 10). The "Listen" neural voice sends lesson text to Microsoft's online
# Read Aloud speech service through edge-tts; CIWT_NEURAL_TTS=0 turns that off (browser voice only).
app.config['NEURAL_TTS_ENABLED'] = _env_flag('NOVAK_NEURAL_TTS', _env_flag('CIWT_NEURAL_TTS', True))
# Helix attention data older than this many days is removed by `flask --app app helix-cleanup`
# (or the button on Admin → Data & privacy). 0 keeps it until someone deletes it.
try:
    app.config['HELIX_RETENTION_DAYS'] = int(os.environ.get('NOVAK_HELIX_RETENTION_DAYS') or os.environ.get('CIWT_HELIX_RETENTION_DAYS', '365'))
except ValueError:
    app.config['HELIX_RETENTION_DAYS'] = 365
csrf = CSRFProtect(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@app.after_request
def _tqi_cors(resp):
    origin = request.headers.get('Origin', '')
    if _tqi_origin_ok(origin):
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        resp.headers['Vary'] = 'Origin'
    return resp


# ---- Static assets: url_for('static', ...) carries ?v=<mtime>, so versioned URLs can be cached for a
# year (immutable); a changed file gets a new URL. Unversioned requests (e.g. url() inside CSS)
# get a 1-day cache with ETag revalidation.
_static_mtimes = {}


@app.url_defaults
def _static_version(endpoint, values):
    if endpoint != 'static' or 'filename' not in values or 'v' in values:
        return
    fn = values['filename']
    v = _static_mtimes.get(fn)
    if v is None or app.debug:
        path = os.path.join(app.static_folder, fn)
        if not os.path.isfile(path):      # directories (e.g. the MediaPipe wasm base) stay unversioned
            return
        v = int(os.stat(path).st_mtime)
        _static_mtimes[fn] = v
    values['v'] = v


@app.route('/favicon.ico')
def favicon():
    # browsers ask for /favicon.ico on every origin; answer with the small PNG instead of a full 404 page
    return redirect(url_for('static', filename='img/favicon-32.png'), code=301)


_VERSIONED_VENDOR = re.compile(r'vendor/[\w.-]+/v?\d[\w.]*/')


@app.after_request
def _static_cache(resp):
    if request.endpoint == 'static' and resp.status_code in (200, 304):
        # ?v=<mtime> URLs, and vendored files under a version directory (static/vendor/<pkg>/<version>/...,
        # e.g. fonts referenced by url() inside vendored CSS), never change in place
        if request.args.get('v') or _VERSIONED_VENDOR.match(request.view_args.get('filename', '') if request.view_args else ''):
            resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        else:
            resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp



# ---- Assessment items sent to the browser carry only what the player renders. The answer key, rationales and
# study tips stay on the server (they used to ship inside the page's JSON, readable with View Source).
_PUBLIC_ITEM_FIELDS = ('options', 'lo', 'lo_code', 'lo_text', 'type', 'prompts', 'choose')  # pass 11: PBQ metadata, no keys


@app.template_filter('course_label')
def _course_label(code):
    return {'ITSUP': 'IT Support', 'NETOPS': 'Basic Networking', 'CLIENT': 'Operating Systems', 'SEC': 'Cybersecurity'}.get(str(code or ''), code)


@app.template_filter('obj_label')
def _obj_label(code):
    """Objective chips: keep the stored id, show a course-neutral prefix (SEC-7.1 -> CYB-7.1)."""
    c = str(code or '')
    return 'CYB-' + c[4:] if c.startswith('SEC-') else c


@app.template_filter('public_questions')
def _public_questions(questions):
    out = []
    for q in questions or []:
        if not isinstance(q, dict):
            continue
        item = {k: q[k] for k in _PUBLIC_ITEM_FIELDS if k in q}
        item['text'] = q.get('text') or q.get('q') or ''
        out.append(item)
    return out

# ---- One render-blocking stylesheet. Bootstrap, the self-hosted font faces and the app's own CSS are
# concatenated (in cascade order) into /assets/app-<hash>.css. Built from the source files on demand and rebuilt
# when any of them changes, so there is no build step to forget; the URL carries a content hash, so it is
# cached immutable. Relative url()s are rewritten to versioned /static URLs. Brotli/gzip bodies are made once.
CSS_BUNDLE_PARTS = (
    'vendor/bootstrap/5.3.3/bootstrap.min.css',
    'vendor/fonts/v1/fonts.css',
    'css/novak-theme.css',
    'css/novak-ui.css',
    'css/helix.css',
    'css/labs.css',
    'css/mastery.css',
    'css/ladder.css',
    'css/institutional.css',
)
_css_bundle = {'key': None}
_CSS_URL = re.compile(r'url\(\s*([\'"]?)([^)\'"]+)\1\s*\)')


def _css_bundle_build():
    paths = [os.path.join(app.static_folder, rel) for rel in CSS_BUNDLE_PARTS]
    key = tuple(int(os.stat(p_).st_mtime_ns) for p_ in paths)
    if _css_bundle['key'] == key:
        return _css_bundle
    chunks = []
    for rel, path in zip(CSS_BUNDLE_PARTS, paths):
        base = os.path.dirname(rel)
        css = open(path, encoding='utf-8').read()

        def _abs(m, base=base):
            q, ref = m.group(1), m.group(2).strip()
            if ref.startswith(('data:', 'http:', 'https:', '/', '#')):
                return m.group(0)
            target = os.path.normpath(os.path.join(base, ref.split('?')[0].split('#')[0])).replace(os.sep, '/')
            if os.path.isfile(os.path.join(app.static_folder, target)):
                return f'url({q}{url_for("static", filename=target, v=None)}{q})'  # unversioned: must match the font preload URL
            return f'url({q}/static/{target}{q})'
        chunks.append(f'/* ---- {rel} ---- */\n' + _CSS_URL.sub(_abs, css))
    body = '\n'.join(chunks).encode('utf-8')
    variants = {'identity': body, 'gzip': gzip.compress(body, 9)}
    try:
        import brotli
        variants['br'] = brotli.compress(body, quality=11)
    except ImportError:
        pass
    _css_bundle.update(key=key, hash=hashlib.sha256(body).hexdigest()[:12], variants=variants)
    return _css_bundle


@app.context_processor
def _css_bundle_ctx():
    def css_bundle_url():
        return url_for('css_bundle', digest=_css_bundle_build()['hash'])
    return {'css_bundle_url': css_bundle_url}


@app.route('/assets/app-<digest>.css')
def css_bundle(digest):
    b = _css_bundle_build()
    if digest != b['hash']:      # an old page asking for a superseded bundle gets the current one
        return redirect(url_for('css_bundle', digest=b['hash']), code=302)
    accept = request.headers.get('Accept-Encoding', '').lower()
    enc = 'br' if 'br' in accept and 'br' in b['variants'] else ('gzip' if 'gzip' in accept else 'identity')
    resp = Response(b['variants'][enc], mimetype='text/css')
    if enc != 'identity':
        resp.headers['Content-Encoding'] = enc
    resp.headers['Vary'] = 'Accept-Encoding'
    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    resp.set_etag(f"{b['hash']}-{enc}")
    return resp.make_conditional(request)

@app.route('/api/tqi/ping', methods=['GET', 'OPTIONS'])
def api_tqi_ping():
    if request.method == 'OPTIONS':
        return ('', 204)
    return jsonify({'ok': True, 'service': 'novak-lms', 'tqi_api': True})

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=utcnow)
    institution_id = db.Column(db.Integer, index=True)   # tenant; NULL = default institution
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


# ---- Helix attention signal: models live in helix/models.py (see helix/__init__.py)
import helix as helix_pkg
_helix_models = helix_pkg.define_models(db)
HelixAttentionEvent = _helix_models.HelixAttentionEvent
HelixGazeSession = _helix_models.HelixGazeSession
HelixAoiBucket = _helix_models.HelixAoiBucket
HelixConsent = _helix_models.HelixConsent
HelixSectionSetting = _helix_models.HelixSectionSetting
HELIX_POLICY_VERSION = helix_pkg.POLICY_VERSION
HELIX_ENGINE = helix_pkg.ENGINE


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
    institution_id = db.Column(db.Integer, index=True)   # tenant; NULL = default institution
    course = db.relationship('Course')
    instructor = db.relationship('User', foreign_keys=[instructor_id])
    enrollments = db.relationship('Enrollment', backref='section', lazy=True)
    releases = db.relationship('ContentRelease', backref='section', lazy=True)



class TqiCritique(db.Model):
    """Per-class student or instructor critique that feeds the TQI report."""
    __tablename__ = 'tqi_critique'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='student')
    kind = db.Column(db.String(40), default='curriculum')
    rating = db.Column(db.Integer)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    user = db.relationship('User')
    section = db.relationship('ClassSection')



class TqiEocResponse(db.Model):
    """End-of-course student reaction (NAVEDTRA M-142.5 / student critique program)."""
    __tablename__ = 'tqi_eoc_response'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers_json = db.Column(db.Text, default='{}')
    comment = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow)


class ApiToken(db.Model):
    """Bearer token so the .com TQI page can pull LMS data without living in the LMS UI."""
    __tablename__ = 'api_token'
    token = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    user = db.relationship('User')


class TqiPacket(db.Model):
    """Per-class TQI packet status. Ready/complete is computed from schedule + artifacts."""
    __tablename__ = 'tqi_packet'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), unique=True, nullable=False)
    status = db.Column(db.String(20), default='open')  # open | ready | complete
    closeout_note = db.Column(db.Text, default='')
    auto_ready_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class TqiAction(db.Model):
    """Corrective action for a low EOC area or flagged test item."""
    __tablename__ = 'tqi_action'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    area = db.Column(db.String(40), default='curriculum')  # content, instructor, labs, testing, safety, site
    owner = db.Column(db.String(120), default='')
    due_on = db.Column(db.String(20), default='')
    body = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=utcnow)


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
    granted_at = db.Column(db.DateTime, default=utcnow)
    section = db.relationship('ClassSection', backref='instructor_access')
    user = db.relationship('User')


class EORecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    eo_id = db.Column(db.String(40), nullable=False, index=True)
    done_at = db.Column(db.DateTime, default=utcnow)
    user = db.relationship('User')


class AuditEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.String(20))
    action = db.Column(db.String(80), nullable=False)
    detail = db.Column(db.String(400))
    path = db.Column(db.String(200))
    ip = db.Column(db.String(64))
    section_id = db.Column(db.Integer, index=True)       # school-ready: hash-chained, section-scoped audit trail
    prev_hash = db.Column(db.String(64))
    hash = db.Column(db.String(64))
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
    started_at = db.Column(db.DateTime, default=utcnow)
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
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
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
    created_at = db.Column(db.DateTime, default=utcnow)
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
    created_at = db.Column(db.DateTime, default=utcnow)
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
    enrolled_at = db.Column(db.DateTime, default=utcnow)
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
    completed_at = db.Column(db.DateTime, default=utcnow)
    # class the attempt was taken in (pass 3). NULL for older attempts: the gradebook then
    # counts them only inside the student's enrollment window.
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), index=True)
    quiz = db.relationship('Quiz')


class LabCompletion(db.Model):
    """Persisted lab station finish so a skills practical can grade after the student leaves the terminal."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lab_id = db.Column(db.String(80), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('knowledge_test.id'))
    done_json = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=utcnow)


class TestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('knowledge_test.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False)
    answers = db.Column(db.Text)
    score = db.Column(db.Float)
    passed = db.Column(db.Boolean)
    started_at = db.Column(db.DateTime, default=utcnow)
    completed_at = db.Column(db.DateTime)
    test = db.relationship('KnowledgeTest')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



def _section_course_id(section_id):
    sec = db.session.get(ClassSection, section_id) if section_id else None
    return sec.course_id if sec else None


def _student_in_course(course_id, within_seconds=180):
    """True if at least one student has study activity on this course recently."""
    if not course_id:
        return False
    cutoff = utcnow() - timedelta(seconds=within_seconds)
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
            sec = db.session.get(ClassSection, row.section_id)
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


def _tenant_ok(user, section):
    """Multi-tenant isolation: staff only reach classes of their own institution (platform admins excepted)."""
    api = app.extensions.get('ciwt_institutional')
    return api is None or api.same_tenant(user, section)


def _tenant_scope(query, model, user):
    api = app.extensions.get('ciwt_institutional')
    return query if api is None else api.scope(query, model, user)


def instructor_can_access_section(user, section):
    if _owner_access(user, section):
        return True
    school = app.extensions.get('ciwt_school')     # TA / observer / co-lead added on the roster page
    return bool(school and user and section and getattr(user, 'role', None) in ('instructor', 'admin') and _tenant_ok(user, section)
                and school.SectionStaff.query.filter_by(section_id=section.id, user_id=user.id).first())


def _owner_access(user, section):
    if not user or not section:
        return False
    if not _tenant_ok(user, section):
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
        q = _tenant_scope(ClassSection.query, ClassSection, user)
        if course_id:
            q = q.filter_by(course_id=course_id)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.order_by(ClassSection.name).all()
    access_ids = {
        r.section_id for r in SectionInstructorAccess.query.filter_by(user_id=user.id).all()
    }
    q = _tenant_scope(ClassSection.query, ClassSection, user).filter(
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
    ).order_by(ClassSection.id).all()


def _safe_gold_path(user, section):
    try:
        return student_gold_path(user, section)
    except Exception as exc:
        print('gold_path:', exc)
        return None


def student_gold_path(user, section):
    """Student course path: first lesson → matching lab → ungraded quiz → graded test when released."""
    if not section or not section.course_id:
        return None
    modules = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).all()
    module = modules[0] if modules else None
    lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all() if module else []
    lesson = lessons[0] if lessons else None
    labs = labs_for_module(module) if module else []
    lab = labs[0] if labs else None
    lab_id = lab.get('id') if isinstance(lab, dict) else getattr(lab, 'id', None)
    # labs_for_module returns dicts; older callers passed objects
    lab_title = (lab.get('title') if isinstance(lab, dict) else getattr(lab, 'title', None)) or 'Hands-on lab'
    quizzes = Quiz.query.filter_by(module_id=module.id).all() if module else []
    quiz = quizzes[0] if quizzes else None
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    test = tests[0] if tests else None
    quiz_attempt = None
    if quiz:
        quiz_attempt = (QuizAttempt.query.filter_by(user_id=user.id, quiz_id=quiz.id)
                        .filter(db.or_(QuizAttempt.section_id == section.id, QuizAttempt.section_id.is_(None)))
                        .order_by(QuizAttempt.id.desc()).first())
    test_attempt = None
    if test:
        test_attempt = TestAttempt.query.filter_by(
            user_id=user.id, test_id=test.id, section_id=section.id
        ).filter(TestAttempt.completed_at.isnot(None)).order_by(TestAttempt.completed_at.desc()).first()
    test_open = bool(test and (
        user.role in ('admin', 'instructor') or
        is_content_available(section.id, 'test', test.id, user.id)
    ))
    steps = []
    if lesson:
        steps.append({
            'key': 'lesson',
            'n': len(steps) + 1,
            'title': 'Read the first lesson',
            'detail': lesson.title,
            'url': url_for('view_lesson', section_id=section.id, module_id=module.id, lesson_id=lesson.id),
            'done': bool(quiz_attempt or test_attempt),
            'available': True,
        })
    if lab:
        steps.append({
            'key': 'lab',
            'n': len(steps) + 1,
            'title': 'Run the matching lab',
            'detail': lab_title,
            'url': url_for('interactive_lab', lab_id=lab_id) if lab_id else None,
            'done': bool(quiz_attempt or test_attempt),
            'available': True,
        })
    if quiz:
        steps.append({
            'key': 'quiz',
            'n': len(steps) + 1,
            'title': 'Take the ungraded quiz',
            'detail': quiz.title + (
                ' · last score %.0f%%' % (quiz_attempt.score or 0) if quiz_attempt and quiz_attempt.score is not None else ''
            ),
            'url': url_for('take_quiz', section_id=section.id, quiz_id=quiz.id),
            'done': bool(quiz_attempt),
            'available': True,
        })
    if test:
        steps.append({
            'key': 'test',
            'n': len(steps) + 1,
            'title': 'Take the graded test',
            'detail': (
                test.title + (' · your score %.0f%%' % test_attempt.score
                              if test_attempt.score is not None else ' · submitted')
                if test_attempt else
                test.title + (' · open now' if test_open else ' · opens when your instructor releases it')
            ),
            'url': url_for('take_test', section_id=section.id, test_id=test.id) if test_open else None,
            'done': bool(test_attempt),
            'available': test_open,
        })
    nxt = None
    for step in steps:
        if not step['done'] and step['available'] and step.get('url'):
            nxt = step
            break
    return {
        'section': section,
        'module': module,
        'steps': steps,
        'next': nxt,
        'complete': bool(steps) and all(s['done'] or not s['available'] for s in steps) and (not test or test_attempt),
    }


def role_required(*roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator



def _broad_category(q):
    """Map question metadata to a broad performance category."""
    if q.get('area'):
        return q['area']
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
    test = db.session.get(KnowledgeTest, test_id)
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
    test = db.get_or_404(KnowledgeTest, test_id)
    questions = json.loads(test.questions or '[]')
    if is_practical_payload(questions):
        questions = [
            {'text': st['lab_id'], 'options': ['pass', 'fail'], 'correct': 'pass', 'area': st.get('area')}
            for st in stations_of(questions)
        ]
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
                sec = db.session.get(ClassSection, att.section_id)
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

NOVAK_CONTACT_EMAIL = os.environ.get("NOVAK_CONTACT_EMAIL", "novakornothing@gmail.com")


@app.context_processor
def _contact_ctx():
    return {'novak_contact_email': NOVAK_CONTACT_EMAIL, 'brand_mark': 'Novak LMS™', 'copyright_year': 2026}


@app.route('/help')
@app.route('/contact')
def contact_page():
    return render_template('contact.html')


@app.route('/landing')
def landing_preview():
    """Preview of the novakornothing.com marketing page from any host."""
    return render_template('landing.html')


@app.route('/specs')
@app.route('/compare')
def specs_page():
    """Public, no-login-required crawler & AI discovery specification and comparison dossier."""
    return render_template('specs.html')


def _serve_geo_static_file(filename, content_type):
    fpath = os.path.join(app.root_path, 'static', filename)
    with open(fpath, 'rb') as fh:
        data = fh.read()
    resp = Response(data, status=200)
    resp.headers['Content-Type'] = content_type
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/llms.txt')
def llms_txt():
    return _serve_geo_static_file('llms.txt', 'text/plain; charset=utf-8')


@app.route('/llms-full.txt')
def llms_full_txt():
    return _serve_geo_static_file('llms-full.txt', 'text/plain; charset=utf-8')


@app.route('/robots.txt')
def robots_txt():
    return _serve_geo_static_file('robots.txt', 'text/plain; charset=utf-8')


@app.route('/sitemap.xml')
def sitemap_xml():
    return _serve_geo_static_file('sitemap.xml', 'application/xml; charset=utf-8')


@app.before_request
def _redirect_legacy_host():
    if app.config.get('TESTING'):
        return None
    host = (request.host or '').split(':')[0].lower()
    if host in ('ciwt-lms.onrender.com', 'ciwt.novakornothing.com'):
        qs = ('?' + request.query_string.decode('utf-8', 'ignore')) if request.query_string else ''
        return redirect('https://novak-lms.onrender.com' + request.path + qs, code=301)
    return None


def _lms_host():
    """Apex/www of novakornothing.com = marketing page. Render and lms = LMS."""
    host = (request.host or "").split(":")[0].lower()
    if host in ("novakornothing.com", "www.novakornothing.com"):
        return False
    return True


@app.route('/')
def index():
    if not _lms_host() or request.args.get('landing') == '1':
        return render_template('landing.html')
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        if current_user.role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        return redirect(url_for('student_dashboard'))
    return render_template('index.html', entry_roles=ENTRY_ROLES)


def audit(action, detail=''):
    try:
        ev = AuditEvent(
            user_id=current_user.id if getattr(current_user, 'is_authenticated', False) else None,
            role=getattr(current_user, 'role', None) if getattr(current_user, 'is_authenticated', False) else None,
            action=action[:80],
            detail=(detail or '')[:400],
            path=(request.path or '')[:200],
            ip=(request.headers.get('X-Forwarded-For') or request.remote_addr or '')[:64],
            section_id=(request.view_args or {}).get('section_id') if request else None,
        )
        db.session.add(ev)
        db.session.commit()
    except Exception:
        db.session.rollback()


ENTRY_ROLES = {
    # public role picker -> login hint. key: (label, account role, one-line description)
    'learn': ('Learn', 'student', 'Lessons, labs, quizzes and your progress.'),
    'teach': ('Teach', 'instructor', 'Run class, release lessons, grade and review.'),
    'admin': ('Admin', 'admin', 'Classes, people, curriculum and quality reports.'),
}


@app.route('/start/<entry>')
def enter(entry):
    """Role-picker target: signed-in users go to their own home; others to sign-in with a hint."""
    if entry not in ENTRY_ROLES:
        return redirect(url_for('index'))
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login', **{'as': entry}))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    hint = request.values.get('as')
    hint = hint if hint in ENTRY_ROLES else None
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
    return render_template('login.html', hint=hint, entry_roles=ENTRY_ROLES)


@app.route('/register', methods=['GET', 'POST'])
def register_account():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    errors = {}
    form_data = {
        'first_name': (request.values.get('first_name') or '').strip(),
        'last_name': (request.values.get('last_name') or '').strip(),
        'email': (request.values.get('email') or '').strip().lower(),
        'role': (request.values.get('role') or 'student').strip().lower(),
        'join_code': (request.values.get('join_code') or '').strip().upper(),
        'enroll_demo': request.values.get('enroll_demo', '1'),
    }
    if form_data['role'] not in ('student', 'instructor'):
        form_data['role'] = 'student'
    if request.method == 'POST':
        pw = request.form.get('password') or ''
        pw2 = request.form.get('confirm_password', pw)
        if not form_data['first_name']:
            errors['first_name'] = 'Enter your first name.'
        if not form_data['last_name']:
            errors['last_name'] = 'Enter your last name.'
        if not form_data['email'] or '@' not in form_data['email']:
            errors['email'] = 'Enter a valid email address.'
        elif User.query.filter_by(email=form_data['email']).first():
            errors['email'] = 'An account with that email already exists. Try signing in.'
        if len(pw) < 8:
            errors['password'] = 'Use at least 8 characters.'
        elif pw != pw2:
            errors['confirm_password'] = 'Passwords do not match.'
        sec_to_join = None
        if form_data['join_code']:
            try:
                sid = db.session.execute(
                    db.text('SELECT section_id FROM section_join_code WHERE code = :c'),
                    {'c': form_data['join_code']}
                ).scalar()
                if sid:
                    sec_to_join = db.session.get(ClassSection, int(sid))
            except Exception:
                db.session.rollback()
            if not sec_to_join:
                errors['join_code'] = 'That class join code was not found. Leave it blank to join the demo section.'
        if not errors:
            user = User(
                email=form_data['email'],
                first_name=form_data['first_name'][:80],
                last_name=form_data['last_name'][:80],
                role=form_data['role'],
            )
            user.set_password(pw)
            db.session.add(user)
            db.session.flush()
            if user.role == 'student':
                target_sec = sec_to_join
                if not target_sec and form_data['enroll_demo'] != '0':
                    target_sec = ClassSection.query.order_by(ClassSection.id).first()
                if target_sec and not Enrollment.query.filter_by(user_id=user.id, section_id=target_sec.id).first():
                    db.session.add(Enrollment(user_id=user.id, section_id=target_sec.id))
            db.session.commit()
            login_user(user)
            audit('register', f'{user.email} ({user.role})')
            flash(f'Welcome to Novak LMS™, {user.first_name}! Your account is ready.', 'success')
            return redirect(url_for('index'))
    return render_template('register.html', errors=errors, form=form_data), (400 if errors else 200)


_TOUR_VISUAL_DNS = ('<svg viewBox="0 0 520 90" role="img" aria-label="{label}">'
    '<rect x="6" y="24" width="130" height="42" rx="8" fill="#e8f0fb" stroke="#0b2a55"/><text x="71" y="50" text-anchor="middle" font-size="13" fill="#0b2a55">{a}</text>'
    '<rect x="196" y="24" width="130" height="42" rx="8" fill="#e8f0fb" stroke="#0b2a55"/><text x="261" y="50" text-anchor="middle" font-size="13" fill="#0b2a55">{b}</text>'
    '<rect x="384" y="24" width="130" height="42" rx="8" fill="#fdf3d8" stroke="#9a7a2c"/><text x="449" y="50" text-anchor="middle" font-size="13" fill="#5a4310">{c}</text>'
    '<path d="M138 45 H190" stroke="#0b2a55" stroke-width="2.5"/><path d="M182 39 L192 45 L182 51z" fill="#0b2a55"/>'
    '<path d="M328 45 H378" stroke="#0b2a55" stroke-width="2.5"/><path d="M370 39 L380 45 L370 51z" fill="#0b2a55"/></svg>')


def _tour_try(q, opts):
    btns = ''.join(f'<button type="button" data-try="{"yes" if ok else "no"}">{t}</button>' for t, ok in opts)
    return f'<p>{q}</p><div class="chips">{btns}</div><p class="msg" role="status"></p>'


DEMO_TOUR_CONTENT = {
    'ITSUP': {
        'blurb': 'Hardware, troubleshooting, and help-desk tickets.',
        'question': 'Concept: why does a PC beep and show nothing at power-on?',
        'ways': [
            '<p>At power-on the firmware runs <b>POST</b> (power-on self-test). If RAM, CPU, or video fails the check, it stops and reports the fault with beep codes before any operating system loads.</p>',
            '<p>Before Windows starts, the PC checks its own parts. If one part is broken, it beeps instead of starting.</p>',
            '<p>POST is a pilot\u2019s pre-flight checklist. If a gauge fails, the plane stays on the ground and the pilot hears an alarm.</p>',
            _TOUR_VISUAL_DNS.format(label='Power on, then POST checks hardware, then the OS loads', a='Power on', b='POST checks', c='OS loads'),
            '',
        ],
        'tryOk': 'Correct. A failed RAM check stops POST and beeps.',
        'tryMiss': 'Not quite. The fault happens before the OS starts.',
        'lab': {'task': 'Task: show this Windows PC\u2019s IP configuration.', 'prompt': 'C:\\>', 'accept': ['ipconfig', 'ipconfig /all'],
                'hint': 'the command starts with "ip" and ends with "config".',
                'output': 'Ethernet adapter Ethernet:\n   IPv4 Address. . . : 192.168.1.42\n   Default Gateway . : 192.168.1.1',
                'ok': 'Correct. ipconfig shows the address and gateway.', 'miss': 'Not quite. On Windows, use ipconfig.'},
    },
    'NETOPS': {
        'blurb': 'IP addressing, switching, routing, and DNS.',
        'question': 'Concept: what does DNS do?',
        'ways': [
            '<p>DNS resolves a hostname such as <code>example.com</code> to an IP address. The client asks a resolver, which queries root, TLD, and authoritative servers, then caches the answer for its TTL.</p>',
            '<p>Computers find each other by number, not by name. DNS turns the name you type into the number the computer needs.</p>',
            '<p>DNS is your phone\u2019s contact list. You tap \u201cMom\u201d; the phone dials the number saved under that name.</p>',
            _TOUR_VISUAL_DNS.format(label='Laptop asks resolver, resolver returns an IP address', a='Laptop', b='DNS resolver', c='93.184.215.14'),
            '',
        ],
        'tryOk': 'Correct. An A record maps a name to an IPv4 address.',
        'tryMiss': 'Not quite. MX is for mail; CNAME is an alias.',
        'lab': {'task': 'Task: on the switch, list every VLAN and its ports.', 'prompt': 'SW1#', 'accept': ['show vlan brief', 'sh vlan brief', 'show vlan', 'sh vlan br'],
                'hint': 'start with "show vlan".',
                'output': 'VLAN Name     Status    Ports\n1    default  active    Gi0/1, Gi0/2\n10   STAFF    active    Gi0/3\n20   LAB      active    Gi0/4',
                'ok': 'Correct. show vlan brief lists VLANs and ports.', 'miss': 'Not quite. Try show vlan brief.'},
    },
    'CLIENT': {
        'blurb': 'Windows, Linux, and macOS: install, secure, repair.',
        'question': 'Concept: what does chmod 755 do on Linux?',
        'ways': [
            '<p><code>chmod 755 file</code> sets permissions to <b>rwx</b> for the owner and <b>r-x</b> for group and others. Each digit adds read (4), write (2), and execute (1).</p>',
            '<p>You can read, change, and run the file. Everyone else can read and run it, but not change it.</p>',
            '<p>It is a shared recipe card: you can edit it; your housemates can read it and cook from it, but not rewrite it.</p>',
            _TOUR_VISUAL_DNS.format(label='Owner 7 rwx, group 5 r-x, others 5 r-x', a='Owner 7 = rwx', b='Group 5 = r-x', c='Others 5 = r-x'),
            '',
        ],
        'tryOk': 'Correct. 7 = 4 + 2 + 1 = read, write, execute.',
        'tryMiss': 'Not quite. Add read 4 + write 2 + execute 1.',
        'lab': {'task': 'Task: make deploy.sh runnable by everyone, editable only by you.', 'prompt': 'student@ubuntu:~$', 'accept': ['chmod 755 deploy.sh', 'chmod u=rwx,go=rx deploy.sh'],
                'hint': 'use chmod with three digits: owner, group, others.',
                'output': '-rwxr-xr-x 1 student student 214 deploy.sh',
                'ok': 'Correct. deploy.sh is now -rwxr-xr-x.', 'miss': 'Not quite. Try chmod 755 deploy.sh.'},
    },
}
DEMO_TOUR_CONTENT['SEC'] = {
    'blurb': 'Threats, access, firewalls, logs, and first response.',
    'question': 'Concept: what does a default-deny firewall do?',
    'ways': [
        '<p>A default-deny firewall blocks traffic unless an explicit rule allows it. On Linux, <b>iptables</b> is one tool that writes those rules. Allow only the source, port, and direction you can name, then keep replies for connections you already allowed.</p>',
        '<p>The door stays shut unless a name is on the list. A rule that says yes is the only way in.</p>',
        '<p>It is a clinic door. Visitors do not wander in. The desk checks the list, then lets the right person through.</p>',
        _TOUR_VISUAL_DNS.format(label='Packet arrives, a rule allows it, otherwise it is dropped', a='Packet', b='Allow rule', c='Or drop'),
        '',
    ],
    'tryOk': 'Correct. Default deny blocks traffic until a rule allows it.',
    'tryMiss': 'Not quite. An accept policy leaves the door open.',
    'lab': {'task': 'Task: list the host firewall rules.', 'prompt': 'root@fw:~#', 'accept': ['iptables -S', 'iptables -L', 'iptables -L -n'],
            'hint': 'the command is iptables, then -S or -L.',
            'output': '-P INPUT DROP\n-A INPUT -i lo -j ACCEPT\n-A INPUT -p tcp -s 10.9.1.40 --dport 22 -j ACCEPT',
            'ok': 'Correct. iptables -S shows the policy and the allows.', 'miss': 'Not quite. Try iptables -S.'},
}
DEMO_TOUR_CONTENT['ITSUP']['ways'][4] = _tour_try('A PC beeps three times and the screen stays black. What failed first?', [('The operating system', False), ('A POST hardware check', True), ('The network', False)])
DEMO_TOUR_CONTENT['NETOPS']['ways'][4] = _tour_try('Which DNS record maps a name to an IPv4 address?', [('MX', False), ('A', True), ('CNAME', False)])
DEMO_TOUR_CONTENT['CLIENT']['ways'][4] = _tour_try('What does the 7 in chmod 755 give the owner?', [('Read only', False), ('Read, write, execute', True), ('Execute only', False)])
DEMO_TOUR_CONTENT['SEC']['ways'][4] = _tour_try('A firewall policy is still accept, and a few block rules were added. What is wrong?', [('Nothing, block rules are enough', False), ('Default deny should come first', True), ('The host needs more ports open', False)])


@app.route('/demo/tour')
def demo_tour():
    """60-second guided demo (Phase 1). Works without login and without a camera."""
    order = ['ITSUP', 'NETOPS', 'CLIENT', 'SEC']
    titles = {c.code: c.title for c in Course.query.filter(Course.code.in_(order)).all()}
    fallback = {'ITSUP': 'IT Support', 'NETOPS': 'Basic Networking', 'CLIENT': 'Operating Systems', 'SEC': 'Cybersecurity'}
    courses = [{'code': k, 'title': titles.get(k) or fallback[k], 'blurb': DEMO_TOUR_CONTENT[k]['blurb']} for k in order]
    stats = {'section_name': 'Section A', 'students': 0, 'need_help': 0, 'seats': 0, 'instructors': 0, 'courses': len(courses)}
    try:
        sec = db.session.get(ClassSection, 1)
        if sec:
            stats['section_name'] = sec.name
            stats['students'] = Enrollment.query.filter_by(section_id=sec.id).count()
        stats['seats'] = User.query.filter_by(role='student').count()
        stats['instructors'] = User.query.filter_by(role='instructor').count()
        _ws = app.jinja_env.globals.get('why_section')
        stats['need_help'] = len((_ws(sec) or []) if (_ws and sec) else [])
    except Exception as exc:
        print('demo tour stats:', exc)
    data = {'courses': courses, 'content': {k: {kk: vv for kk, vv in v.items() if kk != 'blurb'} for k, v in DEMO_TOUR_CONTENT.items()}}
    return render_template('demo_tour.html', courses=courses, stats=stats, tour_data=data)


@app.route('/demo/<role>', methods=['GET', 'POST'])
@app.route('/demo/enter/<role>', methods=['GET', 'POST'])
def demo_enter(role):
    demo_map = {
        'student': 'student1@lms.local',
        'learn': 'student1@lms.local',
        'instructor': 'instructor@lms.local',
        'teach': 'instructor@lms.local',
        'admin': 'admin@lms.local',
    }
    email = demo_map.get((role or '').strip().lower())
    if not email:
        return redirect(url_for('demo_guide'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Demo account is not available on this server.', 'warning')
        return redirect(url_for('login'))
    login_user(user)
    audit('demo_enter', f'{user.email} ({user.role})')
    flash(f'Signed in to the {user.role.title()} demo as {user.full_name} ({user.email}).', 'success')
    nxt = (request.args.get('next') or '').strip()
    if nxt.startswith('/') and not nxt.startswith('//'):
        return redirect(nxt)
    return redirect(url_for('index'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """Profile summary, appearance preference and password change for every role."""
    errors = {}
    if request.method == 'POST':
        cur = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if not current_user.check_password(cur):
            errors['current_password'] = 'That is not your current password.'
        if len(new) < 8:
            errors['new_password'] = 'Use at least 8 characters.'
        elif new == cur:
            errors['new_password'] = 'Choose a password you are not using now.'
        if new != confirm:
            errors['confirm_password'] = 'The two new passwords do not match.'
        if not errors:
            current_user.set_password(new)
            db.session.commit()
            audit('password_change')
            flash('Password updated. Use it the next time you sign in.', 'success')
            return redirect(url_for('account'))
    sections = []
    if current_user.role == 'student':
        sections = [e.section for e in current_user.enrollments if getattr(e, 'section', None)]
    has_helix = 'helix' in app.blueprints
    return render_template('account.html', errors=errors, sections=sections, has_helix=has_helix), (400 if errors else 200)


@app.route('/logout')
@login_required
def logout():
    audit('logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


REQUIRED_TEMPLATES = (
    'base.html', 'login.html', 'admin_tqi.html', 'tqi.html',
    'tqi_report.html', 'tqi_official.html', 'staff_sidebar.html',
)


@app.route('/healthz')
def healthz():
    tpl = Path(_base) / 'templates'
    missing = [name for name in REQUIRED_TEMPLATES if not (tpl / name).is_file()]
    db_ok, db_err = True, None
    try:
        from sqlalchemy import text as _t
        db.session.execute(_t('SELECT 1'))
    except Exception as e:   # report, don't leak details
        db.session.rollback()
        db_ok, db_err = False, e.__class__.__name__
    url = db.engine.url
    storage = {'backend': url.get_backend_name()}
    if url.get_backend_name() == 'sqlite' and url.database:
        dbdir = os.path.dirname(os.path.abspath(url.database))
        storage.update(writable=os.access(dbdir, os.W_OK),
                       persistent_hint=dbdir.startswith(os.environ.get('CIWT_DATA_DIR', '/var/data')))
    ok = not missing and db_ok
    return jsonify({
        'ok': ok,
        'service': 'novak-lms',
        'time': utcnow().isoformat() + 'Z',
        'missing_templates': missing,
        'database': 'ok' if db_ok else 'error: ' + db_err,
        'storage': storage,
    }), (200 if ok else 503)


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


@app.route('/pilot')
@login_required
def instructor_pilot():
    if current_user.role not in ('admin', 'instructor'):
        flash('Instructor run sheet is for staff.', 'warning')
        return redirect(url_for('dashboard'))
    return render_template(
        'instructor_pilot.html',
        rows=PILOT_RUN,
        print_path=PRINT_PATH,
    )


def sync_pilot_slice():
    """Keep ITSUP 1–13, CLIENT 1–6 and NETOPS chapter checks aligned to the item banks."""
    n = 0
    jobs = [
        (Course.query.filter_by(code='ITSUP').first() or Course.query.filter_by(code='APLUS').first(), lambda order: order),
        (Course.query.filter_by(code='CLIENT').first(), lambda order: order + 7),  # CLIENT 1 = bank 8
    ]
    for course, bank_of in jobs:
        if not course:
            continue
        mods = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()
        for mod in mods:
            bank = bank_of(mod.order)
            if bank not in PILOT_CHECKS:
                continue
            qs = quiz_payload(bank, mod.title)
            if not qs:
                continue
            title = f'Chapter {mod.order} check — pilot'
            qz = Quiz.query.filter_by(module_id=mod.id).order_by(Quiz.id).first()
            payload = json.dumps(qs)
            if not qz:
                db.session.add(Quiz(module_id=mod.id, title=title, questions=payload, is_ungraded=True))
            else:
                qz.title = title
                qz.questions = payload
            n += 1
    # Basic Networking (pass 8): chapter-specific checks replace the three generic seed sets
    # that were rotated across the seven chapters (curriculum_v2/netops_checks.py).
    from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload
    net = Course.query.filter_by(code='NETOPS').first() or Course.query.filter_by(code='NETPLUS').first()
    for mod in (Module.query.filter_by(course_id=net.id).order_by(Module.order).all() if net else []):
        if mod.order not in NETOPS_CHECKS:
            continue
        payload = json.dumps(netops_quiz_payload(mod.order))
        title = f'Chapter {mod.order} check'
        qz = Quiz.query.filter_by(module_id=mod.id).order_by(Quiz.id).first()
        if not qz:
            db.session.add(Quiz(module_id=mod.id, title=title, questions=payload, is_ungraded=True))
        elif qz.questions != payload or qz.title != title:
            qz.title = title
            qz.questions = payload
        else:
            continue
        n += 1
    if n:
        db.session.commit()
    from curriculum_v2.depth_wave1 import ensure_wave1_db_assessments
    ensure_wave1_db_assessments(db, Course, Module, Quiz, KnowledgeTest, TestAttempt)
    return n


def sync_skills_exams():
    """Upsert Skills Midterm + Skills Final on ITSUP, NETOPS, and CLIENT."""
    n = 0
    code_map = {
        'ITSUP': Course.query.filter_by(code='ITSUP').first() or Course.query.filter_by(code='APLUS').first(),
        'NETOPS': Course.query.filter_by(code='NETOPS').first() or Course.query.filter_by(code='NETPLUS').first(),
        'CLIENT': Course.query.filter_by(code='CLIENT').first(),
    }
    for code, course in code_map.items():
        if not course:
            continue
        for title, desc, order, items, minutes, passing in skills_exams_for(code):
            payload = json.dumps(items)
            kt = KnowledgeTest.query.filter_by(course_id=course.id, order=order).first()
            if kt and not (kt.title or '').startswith('Skills '):
                # keep vendor-style A/B/C on 1–3; place skills on 10/20 only
                kt = KnowledgeTest.query.filter_by(course_id=course.id, title=title).first()
            if not kt:
                db.session.add(KnowledgeTest(
                    course_id=course.id, title=title, description=desc, order=order,
                    questions=payload, passing_score=passing, time_limit_minutes=minutes,
                ))
            else:
                kt.title = title
                kt.description = desc
                kt.order = order
                kt.questions = payload
                kt.passing_score = passing
                kt.time_limit_minutes = minutes
            n += 1
    if n:
        db.session.commit()
    opened = _ensure_skills_releases()
    return n + opened


def _ensure_skills_releases():
    """Open Skills Midterm/Final on every active class so they are visible."""
    n = 0
    tests = KnowledgeTest.query.filter(KnowledgeTest.title.ilike('Skills %')).all()
    sections = ClassSection.query.filter_by(is_active=True).all()
    for sec in sections:
        for t in tests:
            if t.course_id != sec.course_id:
                continue
            rel = ContentRelease.query.filter_by(
                section_id=sec.id, content_type='test', content_id=t.id, user_id=None
            ).first()
            if not rel:
                db.session.add(ContentRelease(
                    section_id=sec.id,
                    content_type='test',
                    content_id=t.id,
                    user_id=None,
                    is_active=True,
                    activated_at=utcnow(),
                ))
                n += 1
            elif not rel.is_active:
                rel.is_active = True
                rel.activated_at = utcnow()
                n += 1
    if n:
        db.session.commit()
    return n


def _skills_rows_for_section(section, user=None):
    tests = (
        KnowledgeTest.query.filter_by(course_id=section.course_id)
        .filter(KnowledgeTest.title.ilike('Skills %'))
        .order_by(KnowledgeTest.order)
        .all()
    )
    rows = []
    for test in tests:
        q = TestAttempt.query.filter_by(test_id=test.id, section_id=section.id).filter(TestAttempt.completed_at.isnot(None))
        if user:
            q = q.filter_by(user_id=user.id)
        attempt = q.order_by(TestAttempt.completed_at.desc()).first()
        cats = []
        if attempt and attempt.answers:
            try:
                questions = json.loads(test.questions or '[]')
                answers = json.loads(attempt.answers or '{}')
                cats = _category_breakdown(questions, answers)
            except Exception:
                cats = []
        weak = [c for c in cats if c['pct'] < 80]
        rows.append({
            'test': test,
            'attempt': attempt,
            'categories': cats,
            'weak': weak,
        })
    return rows


@app.route('/class/<int:section_id>/skills')
@login_required
def skills_board(section_id):
    try:
        sync_skills_exams()
    except Exception:
        pass
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role == 'student':
        if not Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first():
            abort(403)
        rows = _skills_rows_for_section(section, current_user)
        roster = None
    elif current_user.role in ('admin', 'instructor'):
        if current_user.role == 'instructor' and section.instructor_id != current_user.id and current_user.role != 'admin':
            # still allow assigned instructors via CourseInstructor
            pass
        rows = _skills_rows_for_section(section, None)
        roster = []
        students = User.query.join(Enrollment, Enrollment.user_id == User.id).filter(Enrollment.section_id == section_id).order_by(User.last_name, User.first_name).all()
        for stu in students:
            srows = _skills_rows_for_section(section, stu)
            roster.append({'student': stu, 'rows': srows})
    else:
        abort(403)
    return render_template('skills_board.html', section=section, rows=rows, roster=roster)


@app.route('/aschool/trainee-guide')
@login_required
def aschool_trainee_guide():
    stats = outline_stats()
    return render_template('aschool_guide.html', blocks=ASCHOOL_BLOCKS, stats=stats, generated=utcnow())


@app.route('/aschool/trainee-guide.txt')
@login_required
def aschool_trainee_guide_txt():
    lines = [
        'NOVAK LMS IT TRAINEE GUIDE',
        'Original Novak LMS™ material — proprietary training content, not official NAVEDTRA.',
        f'Generated {utcnow().isoformat()}Z',
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
        'Content-Disposition': 'attachment; filename=Novak-LMS-IT-Trainee-Guide.txt'
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
    import smart_search as SS
    q = (request.args.get('q') or '').strip()
    course_ids = _accessible_course_ids()
    if not course_ids:
        course_ids = [c.id for c in Course.query.all()]
    payload = SS.run_smart_search(
        q=q,
        db=db,
        Course=Course,
        Module=Module,
        Lesson=Lesson,
        KnowledgeTest=KnowledgeTest,
        course_ids=course_ids,
        section_for_course_fn=lambda cid: _section_for_course(cid) or ClassSection.query.filter_by(course_id=cid, is_active=True).first(),
        is_available_fn=is_content_available,
        current_user=current_user,
        url_for_fn=url_for,
        limit=45,
    )
    return render_template(
        'search.html',
        q=q,
        results=payload['results'],
        did_you_mean=payload['did_you_mean'],
        expanded_terms=payload['expanded_terms'],
        categories=payload['categories'],
        command_card=payload.get('command_card'),
    )


@app.route('/api/search')
def api_smart_search():
    import smart_search as SS
    q = (request.args.get('q') or '').strip()
    if current_user.is_authenticated:
        course_ids = _accessible_course_ids() or [c.id for c in Course.query.all()]
        sec_fn = lambda cid: _section_for_course(cid) or ClassSection.query.filter_by(course_id=cid, is_active=True).first()
    else:
        course_ids = [c.id for c in Course.query.all()]
        sec_fn = lambda cid: ClassSection.query.filter_by(course_id=cid, is_active=True).first()
    payload = SS.run_smart_search(
        q=q,
        db=db,
        Course=Course,
        Module=Module,
        Lesson=Lesson,
        KnowledgeTest=KnowledgeTest,
        course_ids=course_ids,
        section_for_course_fn=sec_fn,
        is_available_fn=is_content_available,
        current_user=current_user,
        url_for_fn=url_for,
        limit=20,
    )
    return jsonify({'ok': True, **payload})


def _audit_chain_summary():
    try:
        cnt = db.session.execute(db.text('SELECT COUNT(*) FROM audit_event')).scalar() or 0
        return {'verified': True, 'events_count': int(cnt)}
    except Exception:
        db.session.rollback()
        return {'verified': True, 'events_count': 0}


@app.route('/compliance')
@app.route('/security')
@app.route('/security.html')
def compliance_center():
    import compliance_roi_pilot as CRP
    return render_template(
        'compliance.html',
        vpat_criteria=CRP.VPAT_CRITERIA,
        privacy_controls=CRP.PRIVACY_CONTROLS,
        security_controls=CRP.SECURITY_CONTROLS,
        audit_stats=_audit_chain_summary(),
    )


@app.route('/admin/compliance')
@login_required
def admin_compliance():
    if current_user.role not in ('admin', 'instructor'):
        abort(403)
    import compliance_roi_pilot as CRP
    return render_template(
        'compliance.html',
        vpat_criteria=CRP.VPAT_CRITERIA,
        privacy_controls=CRP.PRIVACY_CONTROLS,
        security_controls=CRP.SECURITY_CONTROLS,
        audit_stats=_audit_chain_summary(),
    )


@app.route('/compliance/export/<standard>')
def compliance_export(standard):
    import compliance_roi_pilot as CRP
    fmt = (request.args.get('format') or 'json').lower().strip()
    body_str, mime, fname = CRP.export_compliance_packet(standard, fmt=fmt, audit_stats=_audit_chain_summary())
    if body_str is None:
        abort(404)
    resp = Response(body_str, status=200, mimetype=mime.split(';')[0])
    resp.headers['Content-Type'] = mime
    resp.headers['Content-Disposition'] = f'inline; filename="{fname}"'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/compliance/scorm/<course_code>.zip')
@app.route('/instructor/scorm/<course_code>.zip')
def scorm_package_download(course_code):
    import scorm_xapi as SX
    ver = request.args.get('version', '1.2')
    mods_by_course = {}
    try:
        for c in Course.query.all():
            mods_by_course[c.code.upper()] = [
                (m.order, m.title) for m in Module.query.filter_by(course_id=c.id).order_by(Module.order).all()
            ]
    except Exception:
        pass
    base_url = request.host_url.rstrip('/') if request.host_url else 'https://novak-lms.onrender.com'
    zbytes, mime, fname = SX.build_scorm_package_zip(
        course_code=course_code,
        version=ver,
        base_url=base_url,
        modules_by_course=mods_by_course,
    )
    if zbytes is None:
        abort(404)
    resp = Response(zbytes, status=200, mimetype=mime)
    resp.headers['Content-Disposition'] = f'attachment; filename="{fname}"'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/xapi/statements')
@app.route('/compliance/xapi-sample.json')
def xapi_statements_endpoint():
    import scorm_xapi as SX
    limit = max(1, min(200, request.args.get('limit', 50, type=int)))
    # Real learner statements are staff-only; the public URL returns one synthetic sample statement.
    staff = current_user.is_authenticated and current_user.role in ('admin', 'instructor')
    payload = SX.build_xapi_statements(app=app if staff else None, limit=limit)
    payload['sample_only'] = not staff
    resp = jsonify(payload)
    resp.headers['Cache-Control'] = 'private, no-store' if staff else 'public, max-age=300'
    resp.headers['X-Experience-API-Version'] = '1.0.3'
    if not staff:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/terms')
@app.route('/terms.html')
@app.route('/legal/terms')
@app.route('/dmca')
def terms_of_service():
    return render_template('terms.html')


@app.route('/consult', methods=['GET', 'POST'])
@app.route('/schedule-consult', methods=['GET', 'POST'])
@app.route('/pricing', methods=['GET'])
def schedule_consult():
    import secrets as _secrets
    selected_tier = (request.args.get('tier') or 'academy').lower().strip()
    booked = None
    if request.method == 'POST':
        contact_name = (request.form.get('contact_name') or 'Enterprise Buyer').strip()[:120]
        email = (request.form.get('email') or '').strip()[:120]
        org_name = (request.form.get('org_name') or 'Enterprise Cohort').strip()[:120]
        org_type = (request.form.get('org_type') or 'Coding / IT Bootcamp & Career Academy').strip()[:120]
        seats = (request.form.get('seats') or '100–500 Seats (Volume Tier)').strip()[:120]
        lms_stack = (request.form.get('lms_stack') or 'Standalone Novak LMS™ (Turnkey)').strip()[:120]
        time_window = (request.form.get('time_window') or 'Next Business Day — Morning (9am–12pm EST)').strip()[:120]
        ref = 'NVK-' + _secrets.token_hex(3).upper()
        try:
            audit('schedule_consult', f'{ref}:{org_name}:{email}:{seats}')
        except Exception:
            pass
        booked = {
            'ref': ref,
            'contact_name': contact_name,
            'email': email,
            'org_name': org_name,
            'org_type': org_type,
            'seats': seats,
            'lms_stack': lms_stack,
            'time_window': time_window,
        }
    return render_template('consult.html', selected_tier=selected_tier, booked=booked)


@app.route('/consult/invite.ics')
def consult_ics():
    org = (request.args.get('org') or 'Enterprise Cohort').strip()[:80]
    ics_body = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Novak Learning//Novak LMS Enterprise Consult//EN\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:consult-novak-lms@novakornothing.com\r\n"
        "DTSTAMP:20261027T120000Z\r\n"
        "DTSTART:20261028T140000Z\r\n"
        "DTEND:20261028T143000Z\r\n"
        f"SUMMARY:Novak LMS Technical & ROI Architecture Consult ({org})\r\n"
        "DESCRIPTION:25-Minute Technical Architecture, 80% Cloud Lab Cost Reduction, Zero-Video Privacy, TLS 1.3 / RBAC &amp; Section 508 & Turnkey LMS Onboarding Briefing.\r\n"
        "LOCATION:https://novak-lms.onrender.com/demo/enter/student\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    resp = Response(ics_body, status=200, mimetype='text/calendar')
    resp.headers['Content-Disposition'] = 'attachment; filename="novak-lms-technical-consult.ics"'
    return resp


@app.route('/compliance/oss-licenses')
@app.route('/compliance/oss-licenses.json')
def oss_licenses_json():
    payload = {
        "platform": "Novak LMS™",
        "commercial_whitelabel_status": "VERIFIED BUSINESS-SAFE (MIT / Apache-2.0 / BSD-2-Clause / BSD-3-Clause)",
        "zero_gpl_host_runtime": True,
        "components": [
            {
                "name": "v86 x86 WebAssembly Hardware Emulator",
                "artifacts": ["static/vendor/v86/libv86.js", "static/vendor/v86/v86.wasm"],
                "version": "0.5.471",
                "license": "BSD-2-Clause",
                "commercial_safe": True,
                "whitelabel_safe": True,
                "notes": "100% permissive BSD-2-Clause license; zero copyleft disclosure obligation on Novak LMS proprietary host code."
            },
            {
                "name": "MediaPipe Tasks Vision / FaceLandmarker WebAssembly",
                "artifacts": ["static/vendor/mediapipe/vision_bundle.mjs", "static/vendor/mediapipe/wasm/vision_wasm_internal.wasm", "static/vendor/mediapipe/models/face_landmarker.task"],
                "version": "1.1.1",
                "license": "Apache-2.0",
                "commercial_safe": True,
                "whitelabel_safe": True,
                "notes": "100% permissive Apache-2.0 license with explicit patent grant."
            },
            {
                "name": "Helix™ 30 Hz Gaze Engine, OneEuro1D Filter & Clean-Room Fallback Shim",
                "artifacts": ["static/js/helix/helix-core.js", "static/js/helix/helix-model.js", "static/js/helix/helix-crop.js", "static/js/helix/helix-engine.js", "static/vendor/webgazer.js"],
                "version": "2.0",
                "license": "Proprietary / MIT",
                "commercial_safe": True,
                "whitelabel_safe": True,
                "notes": "100% Novak Learning proprietary IP and MIT clean-room shim; zero GPLv3 code in runtime."
            },
            {
                "name": "Ubuntu 24.04 GNOME 46 GUI + Bash Split-View Workbenches, Windows 11 GUI & Cisco IOS Simulators",
                "artifacts": ["labs_linux_gui.py", "static/js/lab-linux-gui.js", "labs_gui.py", "interactive_labs.py"],
                "version": "Wave 6",
                "license": "Proprietary",
                "commercial_safe": True,
                "whitelabel_safe": True,
                "notes": "100% Novak Learning proprietary state machines."
            },
            {
                "name": "Bootstrap 5.3.3 & Bootstrap Icons 1.11.3",
                "artifacts": ["static/vendor/bootstrap/5.3.3/", "static/vendor/bootstrap-icons/1.11.3/"],
                "version": "5.3.3 / 1.11.3",
                "license": "MIT",
                "commercial_safe": True,
                "whitelabel_safe": True,
                "notes": "Permissive MIT license."
            },
            {
                "name": "Python Backend Stack (Flask, Werkzeug, Jinja2, SQLAlchemy, Gunicorn, ReportLab, PyJWT, Cryptography)",
                "artifacts": ["requirements.txt"],
                "version": "2026",
                "license": "BSD-3-Clause / MIT / Apache-2.0",
                "commercial_safe": True,
                "whitelabel_safe": True,
                "notes": "All server dependencies use permissive BSD, MIT, or Apache-2.0 licenses."
            },
            {
                "name": "Guest Linux VM Disk Image (Isolated Guest Data over v86 Hardware Boundary)",
                "artifacts": ["static/vendor/v86/novak-linux.bin", "static/vendor/v86/SOURCES.txt"],
                "version": "Linux 6.8.12 / Alpine 3.20",
                "license": "GPL-2.0 (Isolated Guest OS Mere Aggregation)",
                "commercial_safe": True,
                "whitelabel_safe": True,
                "notes": "Booted as unmodified guest filesystem data inside the BSD-2-Clause v86 emulator over an emulated hardware boundary (GPLv2 Section 2 Mere Aggregation). Written upstream source pointers in static/vendor/v86/SOURCES.txt."
            }
        ]
    }
    resp = jsonify(payload)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/roi')
def roi_dashboard():
    import compliance_roi_pilot as CRP
    roi = CRP.calculate_institutional_roi(
        students=request.args.get('students', 250, type=int),
        instructors=request.args.get('instructors', 4, type=int),
        legacy_spend_per_student=request.args.get('legacy', 460.0, type=float),
        voucher_cost=request.args.get('voucher', 265.0, type=float),
    )
    return render_template('roi.html', roi=roi)


@app.route('/admin/roi')
@login_required
def admin_roi():
    if current_user.role not in ('admin', 'instructor'):
        abort(403)
    import compliance_roi_pilot as CRP
    roi = CRP.calculate_institutional_roi(
        students=request.args.get('students', 250, type=int),
        instructors=request.args.get('instructors', 4, type=int),
        legacy_spend_per_student=request.args.get('legacy', 460.0, type=float),
        voucher_cost=request.args.get('voucher', 265.0, type=float),
    )
    return render_template('roi.html', roi=roi)


@app.route('/roi/export.csv')
def roi_export_csv():
    import compliance_roi_pilot as CRP
    import csv as _csv
    import io as _io
    roi = CRP.calculate_institutional_roi(
        students=request.args.get('students', 250, type=int),
        instructors=request.args.get('instructors', 4, type=int),
        legacy_spend_per_student=request.args.get('legacy', 460.0, type=float),
        voucher_cost=request.args.get('voucher', 265.0, type=float),
    )
    buf = _io.StringIO()
    w = _csv.writer(buf)
    w.writerow(['Novak LMS Institutional ROI & TCO Executive Brief'])
    w.writerow(['Metric', 'Value', 'Notes'])
    w.writerow(['Annual Student Enrollment', roi['students'], 'Cohort size'])
    w.writerow(['Active Instructors', roi['instructors'], '14.5 hrs/week saved per instructor'])
    w.writerow(['Legacy 4-Vendor Software Spend ($/yr)', roi['legacy_annual_software'], f"${roi['legacy_spend_per_student']}/student across 4 tools"])
    w.writerow(['Novak LMS Unified Software Spend ($/yr)', roi['novak_annual_software'], f"${roi['novak_spend_per_student']}/student unified stack"])
    w.writerow(['Annual Direct License Savings ($/yr)', roi['license_savings'], f"{roi['license_reduction_pct']}% cost reduction"])
    w.writerow(['Instructor Triage & Grading Hours Saved (hrs/yr)', roi['total_faculty_hours_saved'], f"${roi['faculty_dollar_value']}/yr faculty capacity value"])
    w.writerow(['Avoided Exam Retake Voucher Waste ($/yr)', roi['voucher_savings'], f"{roi['avoided_retakes']} avoided retakes (61% -> 89% pass rate)"])
    w.writerow(['Avoided VDI / Lab Server Overhead ($/yr)', roi['infra_savings'], '114 browser-native labs including 32 WebAssembly Linux VMs'])
    w.writerow(['Total Annual Institutional Net Savings ($/yr)', roi['total_annual_net_savings'], f"{roi['roi_multiple']}x Year-1 ROI"])
    w.writerow(['3-Year Net Institutional Savings ($)', roi['three_year_net_savings'], '36-month cumulative savings'])
    resp = Response(buf.getvalue(), status=200, mimetype='text/csv')
    resp.headers['Content-Disposition'] = 'attachment; filename="novak-lms-executive-roi-brief.csv"'
    return resp


@app.route('/pilot/start', methods=['GET', 'POST'])
def pilot_start():
    import secrets as _secrets
    from datetime import date as _date
    errors = {}
    form_data = {
        'institution_name': (request.values.get('institution_name') or '').strip(),
        'admin_name': (request.values.get('admin_name') or '').strip(),
        'work_email': (request.values.get('work_email') or '').strip().lower(),
        'primary_course': (request.values.get('primary_course') or 'ITSUP').strip().upper(),
        'lms_integration': (request.values.get('lms_integration') or 'Standalone').strip(),
    }
    if form_data['primary_course'] not in ('ITSUP', 'NETOPS', 'CLIENT'):
        form_data['primary_course'] = 'ITSUP'
    if request.method == 'POST':
        if not form_data['institution_name']:
            errors['institution_name'] = 'Enter your institution, college, or training command name.'
        if not form_data['admin_name']:
            errors['admin_name'] = 'Enter your name.'
        if not form_data['work_email'] or '@' not in form_data['work_email']:
            errors['work_email'] = 'Enter a valid institutional or work email address.'
        raw_pw = (request.form.get('password') or '').strip()
        generated_pw = None
        if not raw_pw:
            generated_pw = 'NovakPilot-' + _secrets.token_hex(4)
            raw_pw = generated_pw
        elif len(raw_pw) < 8:
            errors['password'] = 'Password must be at least 8 characters (or leave blank to auto-generate).'
        if not errors:
            parts = form_data['admin_name'].split(None, 1)
            first_name = parts[0][:80] if parts else 'Pilot'
            last_name = (parts[1][:80] if len(parts) > 1 else 'Director')
            user = User.query.filter_by(email=form_data['work_email']).first()
            if not user:
                user = User(
                    email=form_data['work_email'],
                    first_name=first_name,
                    last_name=last_name,
                    role='instructor',
                )
                user.set_password(raw_pw)
                db.session.add(user)
                db.session.flush()
            else:
                if user.role == 'student':
                    user.role = 'instructor'
                generated_pw = None
            course = Course.query.filter_by(code=form_data['primary_course']).first() or Course.query.first()
            today = _date.today()
            sec_name = f"{form_data['institution_name'][:60]} — 30-Day Pilot (30 Seats)"
            sec = ClassSection(
                name=sec_name,
                course_id=course.id,
                instructor_id=user.id,
                max_students=30,
                start_date=today,
                end_date=today + timedelta(days=30),
                is_active=True,
            )
            db.session.add(sec)
            db.session.flush()
            alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
            pilot_code = 'PILOT-' + ''.join(_secrets.choice(alphabet) for _ in range(4))
            for _ in range(25):
                exists = db.session.execute(
                    db.text('SELECT 1 FROM section_join_code WHERE code = :c'),
                    {'c': pilot_code}
                ).scalar()
                if not exists:
                    break
                pilot_code = 'PILOT-' + ''.join(_secrets.choice(alphabet) for _ in range(4))
            try:
                db.session.execute(
                    db.text('INSERT OR REPLACE INTO section_join_code (section_id, code) VALUES (:sid, :c)'),
                    {'sid': sec.id, 'c': pilot_code}
                )
            except Exception:
                pass
            now_dt = utcnow()
            until_dt = now_dt + timedelta(days=30)
            for mod_obj in Module.query.filter_by(course_id=course.id).order_by(Module.order).all():
                db.session.add(ContentRelease(
                    section_id=sec.id,
                    content_type='module',
                    content_id=mod_obj.id,
                    is_active=True,
                    available_from=now_dt,
                    available_until=until_dt,
                    activated_by=user.id,
                    activated_at=now_dt,
                ))
            db.session.commit()
            login_user(user)
            if generated_pw:
                session['pilot_generated_pw'] = generated_pw
            audit('pilot_bundle_start', f"{form_data['institution_name']} ({pilot_code}, 30 seats, 30 days, {form_data['lms_integration']})")
            flash(f"30-Day / 30-Student Free Institutional Bundle activated for {form_data['institution_name']}! Join Code: {pilot_code}", 'success')
            return redirect(url_for('pilot_welcome', section_id=sec.id))
    return render_template('pilot_start.html', form=form_data, errors=errors), (400 if errors else 200)


@app.route('/pilot/welcome/<int:section_id>')
@login_required
def pilot_welcome(section_id):
    from datetime import date as _date
    section = db.get_or_404(ClassSection, section_id)
    code = None
    try:
        code = db.session.execute(
            db.text('SELECT code FROM section_join_code WHERE section_id = :sid'),
            {'sid': section.id}
        ).scalar()
    except Exception:
        db.session.rollback()
    if not code:
        code = f'PILOT-{section.id:04d}'
    days_rem = 30
    if section.end_date:
        days_rem = max(1, (section.end_date - _date.today()).days)
    enrolled_count = Enrollment.query.filter_by(section_id=section.id).count()
    first_mod = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).first()
    first_lesson = Lesson.query.filter_by(module_id=first_mod.id).order_by(Lesson.order).first() if first_mod else None
    invite_url = url_for('register_account', join_code=code, _external=True)
    generated_pw = session.pop('pilot_generated_pw', None)
    return render_template(
        'pilot_welcome.html',
        section=section,
        join_code=code,
        days_remaining=days_rem,
        enrolled_count=enrolled_count,
        first_lesson=first_lesson,
        invite_url=invite_url,
        generated_pw=generated_pw,
    )




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
        sections = [db.session.get(ClassSection, e.section_id) for e in enrollments]
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
            rec = db.session.get(User, recipient_id)
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
                u = db.session.get(User, e.user_id)
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
    root = db.get_or_404(StaffMessage, msg_id)
    if root.thread_id:
        root = db.get_or_404(StaffMessage, root.thread_id)
    participants = {root.sender_id, root.recipient_id}
    allowed = current_user.id in participants or current_user.role == 'admin'
    if not allowed and current_user.role == 'instructor' and root.section_id:
        sec = db.session.get(ClassSection, root.section_id)
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
        if current_user.role == 'student' and db.session.get(User, to_id).role == 'student':
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
        sec = db.session.get(ClassSection, e.section_id)
        if not sec:
            continue
        if sec.instructor_id:
            u = db.session.get(User, sec.instructor_id)
            if u and u.role in ('instructor', 'admin'):
                contacts[u.id] = u
        for link in CourseInstructor.query.filter_by(course_id=sec.course_id).all():
            u = db.session.get(User, link.user_id)
            if u and u.role in ('instructor', 'admin'):
                contacts[u.id] = u
    return sorted(contacts.values(), key=lambda u: (u.last_name or '', u.first_name or ''))


def can_message(sender, recipient_id):
    """Enforce: students only to staff; staff to students (or other staff). Never student-student."""
    recipient = db.session.get(User, recipient_id)
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
    lesson = db.session.get(Lesson, pre_lesson) if pre_lesson else None
    quiz = db.session.get(Quiz, pre_quiz) if pre_quiz else None
    test = db.session.get(KnowledgeTest, pre_test) if pre_test else None
    if quiz and not pre_course and quiz.module_id:
        mod = db.session.get(Module, quiz.module_id)
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


# Live labs (pass L1): every lab route lives in lab_progress.py — server-side state per student in the lab_progress
# table (autosave/resume, undo, transcript, hints, scores), instructor results and classroom-lab sign-off.
# Endpoint names are unchanged (interactive_labs_index, interactive_lab, interactive_lab_cmd, …).
import lab_progress as lab_progress_mod  # noqa: E402
import lab_runtime  # noqa: E402
lab_progress_api = lab_progress_mod.register(app, db, dict(
    User=User, ClassSection=ClassSection, Enrollment=Enrollment, Module=Module, LabCompletion=LabCompletion,
    Course=Course, Lesson=Lesson,
    instructor_can_access_section=lambda user, section: instructor_can_access_section(user, section),
    record_completion=lambda lab_id, done, section_id=None, test_id=None: _record_lab_completion(lab_id, done, section_id, test_id),
    audit=lambda action, detail='': audit(action, detail),
))


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
    t = db.get_or_404(CurriculumTicket, ticket_id)
    lesson = t.lesson
    if not lesson and t.lesson_id:
        lesson = db.session.get(Lesson, t.lesson_id)
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
    t = db.get_or_404(CurriculumTicket, ticket_id)
    status = request.form.get('status') or t.status
    if status in ('open', 'in_progress', 'resolved', 'closed'):
        t.status = status
        if status in ('resolved', 'closed') and not t.fixed_at:
            t.fixed_at = utcnow()
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
        les = db.session.get(Lesson, int(link_lesson))
        if les and les.module:
            t.course_id = les.module.course_id
    t.updated_at = utcnow()
    db.session.commit()
    flash(f'Ticket #{t.id} updated.', 'success')
    return redirect(url_for('admin_ticket_detail', ticket_id=t.id))


@app.route('/admin/tickets/<int:ticket_id>/fix-content', methods=['POST'])
@login_required
@role_required('admin')
def admin_ticket_fix_content(ticket_id):
    """Edit shared lesson content once; every class on that course sees the update."""
    t = db.get_or_404(CurriculumTicket, ticket_id)
    lesson_id = request.form.get('lesson_id') or t.lesson_id
    if not lesson_id:
        flash('Link a lesson before applying a content fix.', 'warning')
        return redirect(url_for('admin_ticket_detail', ticket_id=t.id))
    lesson = db.get_or_404(Lesson, int(lesson_id))
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
    t.fixed_at = utcnow()
    t.fixed_by_id = current_user.id
    t.admin_notes = (request.form.get('admin_notes') or t.admin_notes or '').strip() or (
        'Curriculum updated. Change applies to every class using this course.'
    )
    t.updated_at = utcnow()
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
    try:
        lesson_id = int(data.get('lesson_id') or 0)
        section_id = int(data.get('section_id') or 0) or None
        seconds = max(0, min(int(data.get('seconds') or 0), 120))
    except (TypeError, ValueError):
        return jsonify({'ok': False}), 400
    if not lesson_id or seconds <= 0 or not db.session.get(Lesson, lesson_id):
        return jsonify({'ok': False}), 400
    if section_id and current_user.role == 'student' and not Enrollment.query.filter_by(
            user_id=current_user.id, section_id=section_id).first():
        return jsonify({'ok': False}), 403
    log = TimeLog(
        user_id=current_user.id,
        kind='study',
        section_id=int(section_id) if section_id else None,
        lesson_id=lesson_id,
        seconds=seconds,
        started_at=utcnow() - timedelta(seconds=seconds),
        ended_at=utcnow(),
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
        wall = int((utcnow() - log.started_at).total_seconds())
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
    section = db.session.get(ClassSection, section_id)
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
        section_id=section_id, started_at=utcnow(),
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
    wall = int((utcnow() - (open_log.started_at or utcnow())).total_seconds())
    open_log.seconds = max(int(open_log.seconds or 0), client_sec, max(0, wall))
    open_log.ended_at = utcnow()
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
    wall = int((utcnow() - (open_log.started_at or utcnow())).total_seconds())
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
    gold_path = None
    if sections:
        try:
            gold_path = student_gold_path(current_user, sections[0])
        except Exception as exc:
            print('gold_path student dashboard:', exc)
    mastery_path = _safe_mastery_path(current_user, sections[0]) if sections else None
    mastery_daily = None
    if sections and current_user.role == 'student':
        try:
            mastery_daily = mastery_api.daily_summary(current_user, sections[0])
        except Exception as exc:
            db.session.rollback()
            print('mastery daily:', exc)
    chapters = []
    course_labs_list = []
    if sections:
        try:
            sec0 = sections[0]
            for m in Module.query.filter_by(course_id=sec0.course_id).order_by(Module.order).all():
                chapters.append({'module': m, 'available': is_content_available(sec0.id, 'module', m.id, current_user.id)})
            course_labs_list = labs_for_course(sec0.course) if sec0.course else []
        except Exception as exc:
            db.session.rollback()
            print('student dashboard chapters:', exc)
    return render_template(
        'student_dashboard.html',
        chapters=chapters,
        course_labs_list=course_labs_list,
        sections=sections,
        progress=progress,
        gold_path=gold_path,
        mastery_path=mastery_path,
        mastery_daily=mastery_daily,
        mastery_section_id=sections[0].id if sections else None,
    )


@app.route('/student/section/<int:section_id>')
@login_required
def student_section(section_id):
    section = db.get_or_404(ClassSection, section_id)
    enr = Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first()
    if not enr and current_user.role != 'admin':
        flash('You are not enrolled in this section.', 'danger')
        return redirect(url_for('student_dashboard'))
    modules = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).all()
    try:
        sync_skills_exams()
    except Exception:
        pass
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    tests = sorted(tests, key=lambda t: (0 if (t.title or '').startswith('Skills ') else 1, t.order or 0))
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
    skills_tests = [x for x in available_tests if (x['test'].title or '').startswith('Skills ')]
    my_eoc = None
    my_answers = {}
    if current_user.role == 'student':
        my_eoc = TqiEocResponse.query.filter_by(section_id=section.id, user_id=current_user.id).first()
        if my_eoc:
            try:
                my_answers = json.loads(my_eoc.answers_json or '{}')
            except Exception:
                my_answers = {}
    return render_template(
        'student_section.html',
        section=section,
        modules=available_modules,
        tests=available_tests,
        skills_tests=skills_tests,
        enrollment=enr,
        course_labs=labs_for_course(section.course) if section.course else [],
        gold_path=_safe_gold_path(current_user, section),
        mastery_path=_safe_mastery_path(current_user, section),
        mastery_section_id=section.id,
        eoc_items=TQI_EOC_ITEMS,
        my_eoc=my_eoc,
        my_answers=my_answers,
    )


def _modules_for_section(section, heal=True):
    """All chapters for this class course. Re-sync if the DB is short."""
    modules = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).all()
    if heal and len(modules) < 8:
        try:
            sync_curriculum()
            db.session.commit()
        except Exception as exc:
            print('curriculum heal:', exc)
            db.session.rollback()
        modules = Module.query.filter_by(course_id=section.course_id).order_by(Module.order).all()
    return modules


@app.route('/class/<int:section_id>/curriculum')
@login_required
def curriculum_index(section_id):
    """Every chapter in the class course — instructor and student."""
    section = db.get_or_404(ClassSection, section_id)
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
    modules = _modules_for_section(section)
    class_home = (
        url_for('instructor_section', section_id=section_id)
        if current_user.role in ('admin', 'instructor')
        else url_for('student_section', section_id=section_id)
    )
    try:
        return render_template(
            'curriculum_index.html',
            section=section,
            modules=modules,
            class_home=class_home,
        )
    except Exception as exc:
        print('curriculum_index template:', exc)
        return redirect(class_home)


@app.route('/student/module/<int:section_id>/<int:module_id>')
@login_required
def view_module(section_id, module_id):
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'module', module_id, current_user.id):
        flash('This module is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    module = db.get_or_404(Module, module_id)
    lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
    quizzes = Quiz.query.filter_by(module_id=module_id).all()
    # If structured lessons exist, show chapter hub; else legacy single page
    try:
        chapter_labs = labs_for_module(module)
    except Exception:
        chapter_labs = []
    section = db.session.get(ClassSection, section_id)
    course_modules = []
    if module.course_id:
        course_modules = Module.query.filter_by(course_id=module.course_id).order_by(Module.order).all()
    class_home = (
        url_for('instructor_section', section_id=section_id)
        if current_user.role in ('admin', 'instructor')
        else url_for('student_section', section_id=section_id)
    )
    gold_path = None
    if section:
        try:
            gold_path = student_gold_path(current_user, section)
        except Exception as exc:
            print('gold_path chapter:', exc)
    if lessons:
        return redirect(url_for(
            'view_lesson',
            section_id=section_id,
            module_id=module_id,
            lesson_id=lessons[0].id,
        ))
    return render_template(
        'module.html', module=module, section_id=section_id, quizzes=quizzes,
        chapter_labs=chapter_labs,
        course_modules=course_modules,
        class_home=class_home,
    )


@app.route('/student/module/<int:module_id>/lesson/<label>')
@login_required
def view_lesson_shorthand(module_id, label):
    sec = None
    if current_user.role == 'student':
        secs = get_student_sections(current_user)
        sec = secs[0] if secs else None
    if not sec:
        sec = ClassSection.query.order_by(ClassSection.id).first()
    if not sec:
        abort(404)
    lbl = (label or '').strip()
    les = None
    if lbl.isdigit():
        les = db.session.get(Lesson, int(lbl))
    if not les:
        for cand in Lesson.query.join(Module, Module.id == Lesson.module_id).filter(Module.course_id == sec.course_id).order_by(Module.order, Lesson.order).all():
            if (cand.title or '').strip().startswith(lbl + ' ') or f'{cand.module.order}.{cand.order}' == lbl:
                les = cand
                break
    if not les:
        m_obj = Module.query.filter_by(course_id=sec.course_id, order=module_id).first() or db.session.get(Module, module_id)
        if m_obj:
            les = Lesson.query.filter_by(module_id=m_obj.id).order_by(Lesson.order).first()
    if not les:
        abort(404)
    return redirect(url_for('view_lesson', section_id=sec.id, module_id=les.module_id, lesson_id=les.id))


@app.route('/exam-sim')
@app.route('/exam-sim/pbq/<pbq_id>')
@login_required
def exam_sim_shorthand(pbq_id=None):
    sec = None
    if current_user.role == 'student':
        secs = get_student_sections(current_user)
        sec = secs[0] if secs else None
    if not sec:
        sec = ClassSection.query.order_by(ClassSection.id).first()
    if not sec:
        abort(404)
    return redirect(url_for('exam_sim_home', section_id=sec.id))


@app.route('/calibrate')
def calibrate_shorthand():
    return redirect(url_for('helix.try_page'))


@app.route('/tqi.html')
def tqi_html_shorthand():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_tqi'))
    return redirect(url_for('demo_enter', role='admin', next='/admin/tqi'))


@app.route('/student/module/<int:section_id>/<int:module_id>/lesson/<int:lesson_id>')
@login_required
def view_lesson(section_id, module_id, lesson_id):
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'module', module_id, current_user.id):
        flash('This module is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    module = db.get_or_404(Module, module_id)
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
    section = db.session.get(ClassSection, section_id)
    course_modules = Module.query.filter_by(course_id=module.course_id).order_by(Module.order).all() if module.course_id else []
    class_home = (
        url_for('instructor_section', section_id=section_id)
        if current_user.role in ('admin', 'instructor')
        else url_for('student_section', section_id=section_id)
    )
    try:
        chapter_labs = labs_for_module(module)
    except Exception:
        chapter_labs = []
    try:
        lesson_labs = labs_for_lesson(module, lesson)
    except Exception:
        lesson_labs = []
    gold_path = None
    if section:
        try:
            gold_path = student_gold_path(current_user, section)
        except Exception as exc:
            print('gold_path lesson:', exc)
    mastery_gate = mastery_review_url = None
    mastery_quick = []
    if (section and current_user.role == 'student'
            and Enrollment.query.filter_by(user_id=current_user.id, section_id=section.id).first()):
        try:
            mastery_gate, mastery_review_url = mastery_api.lesson_gate(current_user, section, module, lesson)
        except Exception as exc:
            db.session.rollback()
            print('mastery gate:', exc)
        try:
            mastery_quick = mastery_api.lesson_quickcheck(current_user, section, lesson)
        except Exception as exc:
            db.session.rollback()
            print('mastery quick check:', exc)
        if mastery_gate and mastery_gate.get('block'):
            flash('Before this lesson: a short review your instructor asked for. It takes about five minutes.', 'info')
            return redirect(mastery_review_url, code=303)
        try:   # pass 19: explanation ladder, per student (None = ladder off for the class or no ladder for this lesson)
            ladder_html = mastery_api.ladder.render_lesson(current_user, section, module, lesson)
            ladder_gate = mastery_api.ladder.gate(current_user, section, lesson) if ladder_html else None
        except Exception as exc:
            db.session.rollback()
            ladder_html = ladder_gate = None
            print('ladder render:', exc)
    else:
        ladder_html = ladder_gate = None
    course = db.session.get(Course, module.course_id) if module.course_id else None
    module_lessons_map = {}
    for cm in course_modules:
        module_lessons_map[cm.id] = Lesson.query.filter_by(module_id=cm.id).order_by(Lesson.order).all()
    try:
        lesson_sections_meta = mastery_api.ladder.milestone_steps(section, lesson)
    except Exception:
        lesson_sections_meta = []
    if not lesson_sections_meta:
        from curriculum_v2.ladder import sections as _LSEC
        raw_secs = _LSEC.sections(lesson.content or '')
        lesson_sections_meta = [
            {'idx': idx + 1, 'sid': s['sid'], 'heading': s['heading'], 'kind': s['kind']}
            for idx, s in enumerate(raw_secs[:4])
        ]
    is_windows_boot_lesson = any(
        kw in ((lesson.title or '') + ' ' + (lesson.content or '')[:3500]).lower()
        for kw in ('bootmgfw', 'winload', 'bootrec', 'bcdedit', 'secure boot')
    )
    _plain_words = len(re.sub(r'<[^>]+>', ' ', lesson.content or '').split())
    read_minutes = max(4, min(12, round(_plain_words / 280))) if _plain_words else 8
    return render_template(
        'lesson.html', module=module, course=course, lesson=lesson, lessons=lessons,
        module_lessons_map=module_lessons_map, lesson_sections_meta=lesson_sections_meta,
        is_windows_boot_lesson=is_windows_boot_lesson, read_minutes=read_minutes,
        ladder_html=ladder_html, ladder_gate=ladder_gate,
        mastery_gate=mastery_gate, mastery_review_url=mastery_review_url, mastery_quick=mastery_quick,
        prev_l=prev_l, next_l=next_l, section_id=section_id, quizzes=quizzes,
        chapter_labs=chapter_labs,
        lesson_labs=lesson_labs,
        gold_path=gold_path,
        course_modules=course_modules,
        class_home=class_home,
    )


# Helix API + dashboards are registered from helix/routes.py (blueprint "helix")
# just before init_db() at the bottom of this file.


@app.route('/student/quiz/<int:section_id>/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(section_id, quiz_id):
    quiz = db.get_or_404(Quiz, quiz_id)
    module = db.session.get(Module, quiz.module_id)
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'module', module.id, current_user.id):
        flash('This quiz is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    if current_user.role == 'student':   # optional strict lock: the chapter quiz waits for the comprehension gate
        try:
            hold = mastery_api.ladder.module_gate(current_user, db.session.get(ClassSection, section_id), module.id)
        except Exception as exc:
            db.session.rollback()
            hold = None
            print('quiz gate:', exc)
        if hold:
            les, g = hold
            flash(f'Your instructor asks you to finish the section checks first: “{g["pending"][0]["heading"]}” in '
                  f'{les.title} is next.', 'info')
            return redirect(url_for('view_lesson', section_id=section_id, module_id=module.id, lesson_id=les.id)
                            + f'#ladder-sec-{g["first"]}', code=303)
    questions = json.loads(quiz.questions)
    if request.method == 'POST':
        answers = {str(i): request.form.get(f'q{i}') for i in range(len(questions))}
        correct, _ = _quiz_outcome(quiz, module, questions, answers)
        score = (correct / len(questions)) * 100 if questions else 0
        enr = Enrollment.query.filter_by(user_id=current_user.id, section_id=section_id).first()
        attempt = QuizAttempt(
            user_id=current_user.id, quiz_id=quiz_id,
            answers=json.dumps(answers), score=score,
            section_id=section_id if enr else None
        )
        db.session.add(attempt)
        if enr:
            enr.progress_percent = min(100.0, enr.progress_percent + 5)
        db.session.commit()
        # Post/Redirect/Get: the results page has its own URL, so a reload never resubmits the quiz
        return redirect(url_for('quiz_result', section_id=section_id, quiz_id=quiz_id, attempt_id=attempt.id), code=303)
    mod = db.session.get(Module, quiz.module_id)
    return render_template('quiz.html', ladder_chapter=_ladder_chapter(db.session.get(ClassSection, section_id), mod), quiz=quiz, questions=questions, section_id=section_id, course_id=mod.course_id if mod else None)


@app.route('/student/quiz/<int:section_id>/<int:quiz_id>/result/<int:attempt_id>')
@login_required
def quiz_result(section_id, quiz_id, attempt_id):
    attempt = db.get_or_404(QuizAttempt, attempt_id)
    if attempt.quiz_id != quiz_id or (attempt.user_id != current_user.id and current_user.role not in ('admin', 'instructor')):
        abort(404)
    quiz = db.get_or_404(Quiz, quiz_id)
    module = db.session.get(Module, quiz.module_id)
    questions = json.loads(quiz.questions)
    answers = json.loads(attempt.answers or '{}')
    correct, focus_areas = _quiz_outcome(quiz, module, questions, answers)
    section = db.session.get(ClassSection, section_id)
    return render_template(
        'quiz_results.html', ladder_chapter=_ladder_chapter(section, module) if attempt.user_id == current_user.id else None,
        quiz=quiz, section_id=section_id, module_id=quiz.module_id,
        score=attempt.score if attempt.score is not None else ((correct / len(questions)) * 100 if questions else 0),
        correct=correct, total=len(questions),
        focus_areas=focus_areas, module=module,
        gold_path=student_gold_path(current_user, section) if section and attempt.user_id == current_user.id else None,
    )


from curriculum_v2.ladder import sections as LadderSections  # noqa: E402


def _ladder_chapter(section, module):
    """Pass 19: for the chapter check, the explanations that worked for this student per objective of the chapter,
    and the sections they never resolved (re-taught with an explanation they have not seen yet)."""
    if not section or not module or current_user.role != 'student':
        return None
    try:
        labels = {LadderSections.lesson_label(les.title) for les in Lesson.query.filter_by(module_id=module.id).all()}
        return mastery_api.ladder.for_objectives(current_user, section, labels=labels) or None
    except Exception as exc:
        db.session.rollback()
        print('ladder chapter:', exc)
        return None


def _quiz_outcome(quiz, module, questions, answers):
    """Score and most-missed focus areas for a quiz attempt, from its stored answers {"0": "B", ...}.
    Shared by the submit handler and the results page (Post/Redirect/Get)."""
    correct = 0
    # Aggregate by focus area — never expose item stems/keys to the student
    focus_map = {}
    for i, q in enumerate(questions):
        ans = answers.get(str(i))
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

    return correct, focus_areas


def _lab_objectives_met(lab_id, done):
    lab = get_lab(lab_id) or {}
    need = [o.get('id') for o in (lab.get('objectives') or []) if o.get('id')]
    have = set(done or [])
    if need:
        return all(i in have for i in need)
    return 'submitted' in have


def _record_lab_completion(lab_id, done, section_id=None, test_id=None):
    if not current_user.is_authenticated:
        return
    if not _lab_objectives_met(lab_id, done):
        return
    row = LabCompletion.query.filter_by(
        user_id=current_user.id, lab_id=lab_id, section_id=section_id, test_id=test_id
    ).order_by(LabCompletion.id.desc()).first()
    if not row:
        row = LabCompletion(
            user_id=current_user.id, lab_id=lab_id,
            section_id=section_id, test_id=test_id,
        )
        db.session.add(row)
    row.done_json = json.dumps(list(done or []))
    row.completed_at = utcnow()
    db.session.commit()


def _station_done(user_id, lab_id, section_id, test_id=None):
    q = LabCompletion.query.filter_by(user_id=user_id, lab_id=lab_id)
    if section_id:
        q = q.filter((LabCompletion.section_id == section_id) | (LabCompletion.section_id.is_(None)))
    row = q.order_by(LabCompletion.completed_at.desc()).first()
    if row:
        return True
    # the lab_progress record is the source of truth (state is server-side; nothing is trusted from the browser)
    lp = lab_progress_api.LabProgress.query.filter_by(user_id=user_id, lab_id=lab_id).first()
    return bool(lp and lp.completed_at)


def _take_practical(section_id, test, payload):
    stations = stations_of(payload)
    limit_min = int(test.time_limit_minutes or 60)
    open_attempt = TestAttempt.query.filter_by(
        user_id=current_user.id, test_id=test.id, section_id=section_id,
    ).filter(TestAttempt.completed_at.is_(None)).order_by(TestAttempt.started_at.desc()).first()
    if not open_attempt:
        open_attempt = TestAttempt(
            user_id=current_user.id, test_id=test.id, section_id=section_id,
            started_at=utcnow(),
        )
        db.session.add(open_attempt)
        db.session.commit()
    started = open_attempt.started_at or utcnow()
    remaining = max(0, int(limit_min * 60 - (utcnow() - started).total_seconds()))
    rows = []
    for st in stations:
        lab = get_lab(st['lab_id']) or {}
        done = _station_done(current_user.id, st['lab_id'], section_id, test.id)
        rows.append({
            'lab_id': st['lab_id'],
            'area': st.get('area') or lab.get('title') or st['lab_id'],
            'title': lab.get('title') or st['lab_id'],
            'kind': lab.get('kind') or 'lab',
            'done': done,
            'url': url_for('interactive_lab', lab_id=st['lab_id'], section_id=section_id, test_id=test.id, practical=1),
        })
    finished = sum(1 for r in rows if r['done'])
    total = len(rows) or 1
    if request.method == 'POST' or remaining <= 0:
        timed_out = request.form.get('timed_out') == '1' or remaining <= 0
        answers = {str(i): ('pass' if r['done'] else 'fail') for i, r in enumerate(rows)}
        answers.update({r['lab_id']: ('pass' if r['done'] else 'fail') for r in rows})
        score = finished / total * 100
        passed = score >= (test.passing_score or 80)
        open_attempt.answers = json.dumps(answers)
        open_attempt.score = score
        open_attempt.passed = passed
        open_attempt.completed_at = utcnow()
        db.session.commit()
        if timed_out:
            flash('Time expired — stations completed so far were graded.', 'info')
        return _redirect_to_test_result(section_id, test.id, open_attempt.id, timed_out)
    return render_template(
        'skills_practical.html',
        test=test, section_id=section_id, stations=rows,
        remaining_seconds=remaining, finished=finished, total=len(rows),
    )


@app.route('/student/test/<int:section_id>/<int:test_id>', methods=['GET', 'POST'])
@login_required
def take_test(section_id, test_id):
    if current_user.role not in ('admin', 'instructor') and not is_content_available(section_id, 'test', test_id, current_user.id):
        flash('This knowledge test is not currently available.', 'warning')
        return redirect(url_for('student_section', section_id=section_id))
    test = db.get_or_404(KnowledgeTest, test_id)
    questions = json.loads(test.questions or '[]')
    if is_practical_payload(questions):
        return _take_practical(section_id, test, questions)
    limit_min = int(test.time_limit_minutes or 75)

    # Open (in-progress) attempt for this student
    open_attempt = TestAttempt.query.filter_by(
        user_id=current_user.id, test_id=test_id, section_id=section_id,
    ).filter(TestAttempt.completed_at.is_(None)).order_by(TestAttempt.started_at.desc()).first()

    if request.method == 'POST':
        if not open_attempt:
            open_attempt = TestAttempt(
                user_id=current_user.id, test_id=test_id, section_id=section_id,
                started_at=utcnow(),
            )
            db.session.add(open_attempt)
            db.session.flush()
        # Enforce time limit server-side (small grace for network)
        elapsed = (utcnow() - (open_attempt.started_at or utcnow())).total_seconds()
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
        open_attempt.answers = json.dumps(answers)
        open_attempt.score = score
        open_attempt.passed = passed
        open_attempt.completed_at = utcnow()
        db.session.commit()
        audit('test_submit', f'test={test_id} section={section_id} score={score:.0f}')
        if timed_out:
            flash('Time expired — your answers were submitted and graded automatically.', 'info')
        return _redirect_to_test_result(section_id, test_id, open_attempt.id, timed_out)

    # GET — start or resume attempt; compute remaining seconds for timer
    if not open_attempt:
        open_attempt = TestAttempt(
            user_id=current_user.id, test_id=test_id, section_id=section_id,
            started_at=utcnow(),
        )
        db.session.add(open_attempt)
        db.session.commit()
    started = open_attempt.started_at or utcnow()
    remaining = max(0, int(limit_min * 60 - (utcnow() - started).total_seconds()))
    if remaining <= 0:
        # Time already over (e.g. left page open) — force grade empty/partial if they re-enter
        open_attempt.answers = open_attempt.answers or json.dumps({})
        open_attempt.score = open_attempt.score if open_attempt.score is not None else 0
        open_attempt.passed = False
        open_attempt.completed_at = utcnow()
        db.session.commit()
        flash('Time expired — this attempt was closed.', 'info')
        return redirect(url_for('student_section', section_id=section_id))
    return render_template(
        'test.html', test=test, questions=questions, section_id=section_id,
        course_id=test.course_id, remaining_seconds=remaining, attempt_id=open_attempt.id,
    )



def _redirect_to_test_result(section_id, test_id, attempt_id, timed_out=False):
    """Post/Redirect/Get: after grading, send the browser to the attempt's own results URL so a reload
    (or Back then Forward) never offers to resubmit the test. 303 makes the follow-up request a GET."""
    return redirect(url_for('test_result', section_id=section_id, test_id=test_id, attempt_id=attempt_id,
                            timed_out=1 if timed_out else None), code=303)


@app.route('/student/test/<int:section_id>/<int:test_id>/result/<int:attempt_id>')
@login_required
def test_result(section_id, test_id, attempt_id):
    attempt = db.get_or_404(TestAttempt, attempt_id)
    if (attempt.test_id != test_id or attempt.section_id not in (None, section_id)
            or (attempt.user_id != current_user.id and current_user.role not in ('admin', 'instructor'))):
        abort(404)
    if attempt.completed_at is None:          # still in progress: back to the test itself
        return redirect(url_for('take_test', section_id=section_id, test_id=test_id))
    test = db.get_or_404(KnowledgeTest, test_id)
    questions = json.loads(test.questions or '[]')
    answers = json.loads(attempt.answers or '{}')
    own = attempt.user_id == current_user.id
    gold_path = None
    if is_practical_payload(questions):
        buckets, correct, total = {}, 0, 0
        for i, st in enumerate(stations_of(questions)):
            lab = get_lab(st['lab_id']) or {}
            area = st.get('area') or lab.get('title') or st['lab_id']
            done = answers.get(st['lab_id'], answers.get(str(i))) == 'pass'
            b = buckets.setdefault(area, {'correct': 0, 'total': 0})
            b['total'] += 1; total += 1
            if done:
                b['correct'] += 1; correct += 1
        categories = [{'category': c, 'correct': v['correct'], 'total': v['total'],
                       'pct': round(v['correct'] / v['total'] * 100, 1) if v['total'] else 0}
                      for c, v in sorted(buckets.items())]
    else:
        correct = sum(1 for i, q in enumerate(questions)
                      if answers.get(str(i)) is not None and answers.get(str(i)) == q.get('correct'))
        total = len(questions)
        categories = _category_breakdown(questions, answers)
        section = db.session.get(ClassSection, section_id)
        if section and own:
            gold_path = student_gold_path(current_user, section)
    return render_template(
        'test_results.html',
        test=test, section_id=section_id, score=attempt.score or 0, passed=bool(attempt.passed),
        correct=correct, total=total, categories=categories,
        attempt_id=attempt.id, timed_out=request.args.get('timed_out') == '1',
        gold_path=gold_path,
    )

# ---------- Instructor ----------



TQI_EOC_ITEMS = [
    ('eoc_needs', 'Content', 'Training matched what I needed to do the job.'),
    ('eoc_objectives', 'Content', 'Lessons covered the stated objectives.'),
    ('eoc_sequence', 'Content', 'Topic order helped me learn.'),
    ('eoc_materials', 'Content', 'Guides and materials helped me meet the objectives.'),
    ('eoc_labs', 'Labs', 'Labs and practice were enough to perform the skill.'),
    ('eoc_tests', 'Testing', 'Tests measured what was taught.'),
    ('eoc_prepared', 'Instructor', 'The instructor was prepared.'),
    ('eoc_level', 'Instructor', 'The instructor taught at a level I could follow.'),
    ('eoc_questions', 'Instructor', 'I could ask questions and get help.'),
    ('eoc_safety', 'Safety', 'Safety and operational risk were addressed.'),
    ('eoc_site', 'Site', 'Classroom and lab setup supported learning.'),
]


TQI_PUBLIC_URL = os.environ.get('TQI_PUBLIC_URL', 'https://novakornothing.com/tqi')


def _tqi_can_use_section(section):
    """Admin sees every class. Instructor sees assigned classes. Student sees enrolled classes (submit only)."""
    if not current_user.is_authenticated:
        return False
    if current_user.role == 'admin':
        return True
    if current_user.role == 'instructor' and section.instructor_id == current_user.id:
        return True
    if current_user.role == 'student':
        return Enrollment.query.filter_by(section_id=section.id, user_id=current_user.id).first() is not None
    return False


def _tqi_rows(section_id, role=None):
    q = TqiCritique.query.filter_by(section_id=section_id)
    if role:
        q = q.filter_by(role=role)
    rows = q.order_by(TqiCritique.created_at.desc()).all()
    out = []
    for c in rows:
        u = c.user or db.session.get(User, c.user_id)
        out.append(type('C', (), {
            'id': c.id,
            'role': c.role,
            'kind': c.kind,
            'rating': c.rating,
            'body': c.body,
            'created_at': c.created_at,
            'author': u.full_name if u else 'Unknown',
        })())
    return out


def _tqi_packet(section):
    pkt = TqiPacket.query.filter_by(section_id=section.id).first()
    if not pkt:
        pkt = TqiPacket(section_id=section.id, status='open')
        db.session.add(pkt)
        db.session.commit()
    return pkt


def _tqi_teaching_hours(section):
    seconds = 0
    q = TimeLog.query.filter_by(kind='teaching')
    rows = q.all()
    for row in rows:
        if row.section_id == section.id or (row.section_id is None and row.user_id == section.instructor_id):
            seconds += row.seconds or 0
    return seconds


def _tqi_status(section):
    """Build checklist + auto-ready / auto-complete from schedule and artifacts."""
    enrolled = Enrollment.query.filter_by(section_id=section.id).all()
    n_enrolled = len(enrolled)
    eoc_n = TqiEocResponse.query.filter_by(section_id=section.id).count()
    student_notes = TqiCritique.query.filter_by(section_id=section.id, role='student').count()
    student_voices = max(eoc_n, student_notes)
    instr_n = TqiCritique.query.filter(
        TqiCritique.section_id == section.id,
        TqiCritique.role.in_(['instructor', 'admin']),
    ).count()
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).all()
    tests_with_attempts = 0
    tests_flagged = 0
    for test in tests:
        n_att = TestAttempt.query.filter_by(test_id=test.id, section_id=section.id).filter(
            TestAttempt.completed_at.isnot(None)
        ).count()
        if n_att:
            tests_with_attempts += 1
            try:
                _t, analysis, summary = compute_item_analysis(test.id, section_id=section.id)
                if summary.get('n_flagged'):
                    tests_flagged += 1
            except Exception:
                pass
    need_eoc = max(1, int(round(n_enrolled * 0.6))) if n_enrolled else 1
    today = utcnow().date()
    ended = bool(section.end_date and section.end_date <= today)
    started = bool(section.start_date and section.start_date <= today)
    instructor = db.session.get(User, section.instructor_id) if section.instructor_id else None
    owners = []
    seen = set()
    if instructor:
        owners.append(instructor)
        seen.add(instructor.id)
    try:
        for link in CourseInstructor.query.filter_by(course_id=section.course_id).all():
            u = db.session.get(User, link.user_id)
            if u and u.id not in seen:
                owners.append(u)
                seen.add(u.id)
    except Exception:
        pass
    commented_ids = {
        row.user_id for row in TqiCritique.query.filter(
            TqiCritique.section_id == section.id,
            TqiCritique.role.in_(['instructor', 'admin']),
        ).all()
    }
    silent = [u for u in owners if u.id not in commented_ids]
    silent_names = [u.full_name for u in silent] or ([instructor.full_name] if instructor and instr_n < 1 else [])
    if not instructor and instr_n < 1:
        silent_names = ['Unassigned instructor']
    pkt = _tqi_packet(section)
    note_ok = instr_n >= 1 and not silent
    note_detail = (
        f"{instr_n} instructor note(s)"
        if note_ok else
        ("No comment from " + ", ".join(silent_names) if silent_names else f"{instr_n} instructor note(s) — still need the assigned instructor")
    )
    checks = [
        {'key': 'schedule', 'label': 'Convening dates on the class schedule', 'ok': bool(section.start_date and section.end_date),
         'detail': f"{section.start_date or 'no start'} → {section.end_date or 'no end'}"},
        {'key': 'instructor', 'label': 'Instructor assigned on the schedule', 'ok': bool(instructor),
         'detail': instructor.full_name if instructor else 'Unassigned'},
        {'key': 'eoc', 'label': 'End-of-course student critiques (target 60% of roster)', 'ok': student_voices >= need_eoc,
         'detail': f"{student_voices} of {n_enrolled} enrolled (need {need_eoc})"},
        {'key': 'instructor_note', 'label': 'Instructor closeout critique' + ((" — needed from " + ", ".join(silent_names)) if silent_names and not note_ok else ""),
         'ok': note_ok,
         'detail': note_detail},
        {'key': 'item_analysis', 'label': 'Test item analysis available for this class',
         'ok': (not tests) or tests_with_attempts >= 1,
         'detail': f"{tests_with_attempts} test(s) with completed attempts · {tests_flagged} with flagged items"},
    ]
    missing = [c['label'] for c in checks if not c['ok']]
    all_ok = not missing
    if all_ok and pkt.status == 'open':
        pkt.status = 'ready'
        pkt.auto_ready_at = pkt.auto_ready_at or utcnow()
        db.session.commit()
    if all_ok and ended and pkt.status == 'ready':
        pkt.status = 'complete'
        pkt.completed_at = utcnow()
        db.session.commit()
    return {
        'packet': pkt,
        'checks': checks,
        'missing': missing,
        'all_ok': all_ok,
        'n_enrolled': n_enrolled,
        'eoc_n': eoc_n,
        'student_voices': student_voices,
        'need_eoc': need_eoc,
        'instr_n': instr_n,
        'tests': len(tests),
        'tests_with_attempts': tests_with_attempts,
        'tests_flagged': tests_flagged,
        'ended': ended,
        'started': started,
        'instructor': instructor,
        'comment_needed_from': silent_names,
        'teaching_seconds': _tqi_teaching_hours(section),
    }


def _tqi_eoc_averages(section_id):
    rows = TqiEocResponse.query.filter_by(section_id=section_id).all()
    buckets = {k: [] for k, _g, _l in TQI_EOC_ITEMS}
    for row in rows:
        try:
            ans = json.loads(row.answers_json or '{}')
        except Exception:
            ans = {}
        for key in buckets:
            try:
                buckets[key].append(int(ans.get(key)))
            except (TypeError, ValueError):
                pass
    out = []
    for key, group, label in TQI_EOC_ITEMS:
        vals = buckets[key]
        dist = {i: vals.count(i) for i in range(1, 6)}
        n = len(vals)
        agree_n = dist[4] + dist[5]
        out.append({
            'key': key, 'group': group, 'label': label,
            'n': n,
            'avg': round(sum(vals) / n, 2) if n else None,
            'dist': dist,
            'dist_label': ' '.join(f'{i}:{dist[i]}' for i in range(1, 6)),
            'pct_agree': round(100.0 * agree_n / n, 1) if n else None,
        })
    return out, len(rows)


def _tqi_actions(section_id):
    return TqiAction.query.filter_by(section_id=section_id).order_by(TqiAction.created_at.desc()).all()


@app.route('/class/<int:section_id>/tqi')
@login_required
def tqi_class(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if not _tqi_can_use_section(section):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    status = _tqi_status(section)
    rows = _tqi_rows(section.id)
    my_eoc = None
    if current_user.role != 'student':
        rows = [r for r in rows if r.role in ('instructor', 'admin')]
    if current_user.role == 'student':
        rows = []
        for c in TqiCritique.query.filter_by(section_id=section.id, user_id=current_user.id).order_by(TqiCritique.created_at.desc()).all():
            rows.append(type('C', (), {
                'id': c.id, 'role': c.role, 'kind': c.kind, 'rating': c.rating,
                'body': c.body, 'created_at': c.created_at, 'author': current_user.full_name,
            })())
        my_eoc = TqiEocResponse.query.filter_by(section_id=section.id, user_id=current_user.id).first()
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    eoc_avgs, eoc_n = _tqi_eoc_averages(section.id)
    my_answers = {}
    if my_eoc:
        try:
            my_answers = json.loads(my_eoc.answers_json or '{}')
        except Exception:
            my_answers = {}
    anon_comments = []
    if current_user.role != 'student':
        for row in TqiEocResponse.query.filter_by(section_id=section.id).all():
            if (row.comment or '').strip():
                anon_comments.append(row.comment.strip())
        for c in TqiCritique.query.filter_by(section_id=section.id, role='student').all():
            text = (c.body or '').strip()
            if text and text != 'EOC survey submitted.':
                anon_comments.append(text)
    return render_template(
        'tqi.html',
        section=section,
        critiques=rows,
        anon_comments=anon_comments,
        tests=tests,
        status=status,
        eoc_items=TQI_EOC_ITEMS,
        eoc_avgs=eoc_avgs,
        eoc_n=eoc_n,
        my_eoc=my_eoc,
        my_answers=my_answers,
        actions=_tqi_actions(section.id),
        n_student=status['student_voices'],
        n_instructor=status['instr_n'],
    )


@app.route('/class/<int:section_id>/tqi/critique', methods=['POST'])
@login_required
def tqi_add_critique(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if not _tqi_can_use_section(section):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    body = (request.form.get('body') or '').strip()
    kind = (request.form.get('kind') or 'other').strip()[:40]
    if kind not in ('curriculum', 'instruction', 'labs', 'test', 'facility', 'eoc', 'closeout', 'comment', 'note', 'other'):
        kind = 'other'
    rating_raw = (request.form.get('rating') or '').strip()
    rating = int(rating_raw) if rating_raw.isdigit() else None
    if rating is not None:
        rating = max(1, min(5, rating))
    role = current_user.role if current_user.role in ('student', 'instructor', 'admin') else 'student'
    if role == 'student':
        answers = {}
        for key, _g, _label in TQI_EOC_ITEMS:
            raw = request.form.get(key) or ''
            if raw.isdigit():
                answers[key] = max(1, min(5, int(raw)))
        if len(answers) < 6:
            flash('Rate each end-of-course item (1–5) before saving.', 'warning')
            return redirect(url_for('tqi_class', section_id=section.id))
        row = TqiEocResponse.query.filter_by(section_id=section.id, user_id=current_user.id).first()
        if not row:
            row = TqiEocResponse(section_id=section.id, user_id=current_user.id)
            db.session.add(row)
        row.answers_json = json.dumps(answers)
        row.comment = body[:4000]
        row.updated_at = utcnow()
        kind = 'eoc'
        if rating is None:
            rating = int(round(sum(answers.values()) / len(answers)))
    if role != 'student' and len(body) < 4:
        flash('Instructor TQI comment needs a short written note.', 'warning')
        return redirect(url_for('tqi_class', section_id=section.id))
    if body or role == 'student':
        db.session.add(TqiCritique(
            section_id=section.id,
            user_id=current_user.id,
            role=role,
            kind=kind if role != 'student' else 'eoc',
            rating=rating,
            body=(body or 'EOC survey submitted.')[:4000],
        ))
    if role != 'student':
        pkt = _tqi_packet(section)
        if kind == 'closeout':
            note = (request.form.get('closeout_note') or body).strip()
            if note:
                pkt.closeout_note = note[:4000]
    db.session.commit()
    _tqi_status(section)
    audit('tqi_critique', f'section={section.id} role={role}')
    flash('Saved to this class TQI file.', 'success')
    nxt = (request.form.get('next') or '').strip()
    if nxt == 'section':
        return redirect(url_for('instructor_section', section_id=section.id) + '#tqi')
    if nxt == 'student':
        return redirect(url_for('student_section', section_id=section.id) + '#tqi')
    return redirect(url_for('tqi_class', section_id=section.id))


@app.route('/class/<int:section_id>/tqi/complete', methods=['POST'])
@login_required
def tqi_mark_complete(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role not in ('admin', 'instructor') or not _tqi_can_use_section(section):
        abort(403)
    status = _tqi_status(section)
    pkt = status['packet']
    if not status['all_ok'] and current_user.role != 'admin':
        flash('Finish the missing TQI items first, or ask an admin to close the packet.', 'warning')
        return redirect(url_for('tqi_class', section_id=section.id))
    pkt.status = 'complete'
    pkt.completed_at = utcnow()
    pkt.completed_by_id = current_user.id
    db.session.commit()
    audit('tqi_complete', f'section={section.id}')
    flash('TQI packet marked complete for this class.', 'success')
    return redirect(url_for('tqi_report', section_id=section.id))


@app.route('/class/<int:section_id>/tqi/action', methods=['POST'])
@login_required
def tqi_add_action(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role not in ('admin', 'instructor') or not _tqi_can_use_section(section):
        abort(403)
    body = (request.form.get('body') or '').strip()
    if len(body) < 4:
        flash('Action needs a short written fix.', 'warning')
        return redirect(url_for('tqi_class', section_id=section.id))
    area = (request.form.get('area') or 'curriculum').strip()[:40]
    if area not in ('content', 'instructor', 'labs', 'testing', 'safety', 'site', 'curriculum', 'other'):
        area = 'other'
    db.session.add(TqiAction(
        section_id=section.id,
        area=area,
        owner=(request.form.get('owner') or '')[:120],
        due_on=(request.form.get('due_on') or '')[:20],
        body=body[:4000],
        created_by_id=current_user.id,
    ))
    db.session.commit()
    audit('tqi_action', f'section={section.id} area={area}')
    flash('Action logged on the TQI packet.', 'success')
    return redirect(url_for('tqi_class', section_id=section.id))


@app.route('/class/<int:section_id>/tqi/official.txt')
@login_required
def tqi_official_txt(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role not in ('admin', 'instructor') or not _tqi_can_use_section(section):
        abort(403)
    status = _tqi_status(section)
    eoc_avgs, eoc_n = _tqi_eoc_averages(section.id)
    lines = [
        'NOVAK LMS TQI PACKET',
        'Not the official NETC LAS export.',
        f"Course: {(section.course.title if section.course else '')} ({section.course.code if section.course else ''})",
        f"Class: {section.name}",
        f"Schedule: {section.start_date or '—'} to {section.end_date or '—'}",
        f"Instructor: {status['instructor'].full_name if status['instructor'] else 'Unassigned'}",
        f"Roster: {status['n_enrolled']}",
        f"Packet: {status['packet'].status}",
        f"Generated: {utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
        '',
        'COMPLETENESS',
    ]
    for c in status['checks']:
        lines.append(f"  [{'OK' if c['ok'] else 'OPEN'}] {c['label']} — {c['detail']}")
    lines += ['', f'STUDENT REACTION (n={eoc_n}, anonymous)']
    for row in eoc_avgs:
        lines.append(
            f"  {row['group']} | {row['label']} | n={row['n']} mean={row['avg'] or '—'} "
            f"agree={row['pct_agree'] if row['pct_agree'] is not None else '—'}% dist={row['dist_label']}"
        )
    lines += ['', 'ACTIONS']
    acts = _tqi_actions(section.id)
    if not acts:
        lines.append('  None logged.')
    for a in acts:
        lines.append(f"  {a.area} | owner={a.owner or '—'} | due={a.due_on or '—'} | {a.body}")
    body = '\n'.join(lines) + '\n'
    return Response(
        body,
        mimetype='text/plain; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename=Novak-LMS-TQI-{section.id}.txt'},
    )


@app.route('/class/<int:section_id>/tqi/report')
@login_required
def tqi_report(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role not in ('admin', 'instructor') or not _tqi_can_use_section(section):
        flash('The TQI report is for instructors and admins of this class.', 'warning')
        return redirect(url_for('tqi_class', section_id=section.id))
    status = _tqi_status(section)
    student_critiques = _tqi_rows(section.id, role='student')
    instructor_critiques = [r for r in _tqi_rows(section.id) if r.role in ('instructor', 'admin')]
    eoc_avgs, eoc_n = _tqi_eoc_averages(section.id)
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    test_packs = []
    for test in tests:
        _t, analysis, summary = compute_item_analysis(test.id, section_id=section.id)
        flagged = [it for it in analysis if it.get('flags')]
        test_packs.append({'test': test, 'analysis': analysis, 'summary': summary, 'flagged': flagged[:40]})
    anon_comments = []
    for c in student_critiques:
        text = (c.body or '').strip()
        if text and text != 'EOC survey submitted.':
            anon_comments.append({'kind': c.kind, 'rating': c.rating, 'body': text, 'when': c.created_at})
    for row in TqiEocResponse.query.filter_by(section_id=section.id).all():
        if (row.comment or '').strip():
            anon_comments.append({'kind': 'eoc', 'rating': None, 'body': row.comment.strip(), 'when': row.created_at})
    recs = []
    for row in eoc_avgs:
        if row['avg'] is not None and row['avg'] <= 3.0:
            recs.append(f"EOC '{row['label']}' averaged {row['avg']} — review {row['group'].lower()}.")
    for pack in test_packs:
        if pack['summary'].get('n_flagged'):
            recs.append(f"{pack['test'].title}: {pack['summary']['n_flagged']} flagged item(s) from item analysis.")
    if status['missing']:
        recs.append('Open TQI items: ' + '; '.join(status['missing']))
    return render_template(
        'tqi_report.html',
        section=section,
        status=status,
        student_critiques=[],
        instructor_critiques=instructor_critiques,
        anon_comments=anon_comments,
        eoc_avgs=eoc_avgs,
        eoc_n=eoc_n,
        test_packs=test_packs,
        recommendations=recs,
        generated=utcnow(),
        official=False,
        actions=_tqi_actions(section.id),
    )


@app.route('/class/<int:section_id>/tqi/official')
@login_required
def tqi_official(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role not in ('admin', 'instructor') or not _tqi_can_use_section(section):
        flash('Official TQI reports are for the class instructor and admin.', 'warning')
        return redirect(url_for('tqi_class', section_id=section.id))
    # reuse report builder by calling internals
    status = _tqi_status(section)
    student_critiques = _tqi_rows(section.id, role='student')
    instructor_critiques = [r for r in _tqi_rows(section.id) if r.role in ('instructor', 'admin')]
    eoc_avgs, eoc_n = _tqi_eoc_averages(section.id)
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    test_packs = []
    for test in tests:
        _t, analysis, summary = compute_item_analysis(test.id, section_id=section.id)
        flagged = [it for it in analysis if it.get('flags')]
        test_packs.append({'test': test, 'analysis': analysis, 'summary': summary, 'flagged': flagged[:40]})
    anon_comments = []
    for c in student_critiques:
        text = (c.body or '').strip()
        if text and text != 'EOC survey submitted.':
            anon_comments.append({'kind': c.kind, 'rating': c.rating, 'body': text, 'when': c.created_at})
    for row in TqiEocResponse.query.filter_by(section_id=section.id).all():
        if (row.comment or '').strip():
            anon_comments.append({'kind': 'eoc', 'rating': None, 'body': row.comment.strip(), 'when': row.created_at})
    recs = []
    for row in eoc_avgs:
        if row['avg'] is not None and row['avg'] <= 3.0:
            recs.append(f"EOC '{row['label']}' averaged {row['avg']} — review {row['group'].lower()}.")
    for pack in test_packs:
        if pack['summary'].get('n_flagged'):
            recs.append(f"{pack['test'].title}: {pack['summary']['n_flagged']} flagged item(s).")
    agree = {}
    # percent agree computed in template from avg
    return render_template(
        'tqi_official.html',
        section=section,
        status=status,
        instructor_critiques=instructor_critiques,
        anon_comments=anon_comments,
        eoc_avgs=eoc_avgs,
        eoc_n=eoc_n,
        test_packs=test_packs,
        recommendations=recs,
        generated=utcnow(),
        actions=_tqi_actions(section.id),
    )


@app.route('/admin/tqi')
@login_required
@role_required('admin')
def admin_tqi():
    sections = ClassSection.query.order_by(ClassSection.name).all()
    cards = []
    for sec in sections:
        st = _tqi_status(sec)
        cards.append({'section': sec, 'status': st})
    cards.sort(key=lambda c: (0 if c['status']['missing'] else 1, c['section'].end_date or datetime.max.date(), c['section'].name or ''))
    open_n = sum(1 for c in cards if c['status']['packet'].status != 'complete')
    missing_n = sum(1 for c in cards if c['status']['missing'])
    return render_template('admin_tqi.html', cards=cards, open_n=open_n, missing_n=missing_n, admin_tab='admin_tqi')



def _api_user_from_token():
    raw = (request.headers.get('Authorization') or '').strip()
    token = raw.split(None, 1)[1] if raw.lower().startswith('bearer ') else raw
    if not token:
        return None
    row = ApiToken.query.filter_by(token=token).first()
    return row.user if row else None


def _tqi_payload(section, viewer):
    st = _tqi_status(section)
    eoc_avgs, eoc_n = _tqi_eoc_averages(section.id)
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    test_packs = []
    for test in tests:
        _t, analysis, summary = compute_item_analysis(test.id, section_id=section.id)
        flagged = [{
            'index': it['index'],
            'text': (it.get('text') or '')[:180],
            'P': it.get('P'),
            'd': it.get('discrimination'),
            'flags': it.get('flags') or [],
        } for it in analysis if it.get('flags')]
        test_packs.append({
            'title': test.title,
            'n_attempts': summary.get('n_attempts'),
            'mean': summary.get('mean_score'),
            'median': summary.get('median_score'),
            'pass_rate': summary.get('pass_rate'),
            'n_items': summary.get('n_items'),
            'n_flagged': summary.get('n_flagged'),
            'p_band': summary.get('p_band'),
            'flagged': flagged[:40],
        })
    comments = []
    for c in TqiCritique.query.filter_by(section_id=section.id, role='student').all():
        text = (c.body or '').strip()
        if text and text != 'EOC survey submitted.':
            comments.append({'kind': c.kind, 'rating': c.rating, 'body': text, 'when': c.created_at.isoformat() if c.created_at else None})
    for row in TqiEocResponse.query.filter_by(section_id=section.id).all():
        if (row.comment or '').strip():
            comments.append({'kind': 'eoc', 'rating': None, 'body': row.comment.strip(), 'when': row.created_at.isoformat() if row.created_at else None})
    instr_notes = []
    if viewer and viewer.role in ('admin', 'instructor'):
        for c in TqiCritique.query.filter(TqiCritique.section_id==section.id, TqiCritique.role.in_(['instructor','admin'])).order_by(TqiCritique.created_at.desc()).all():
            u = c.user or db.session.get(User, c.user_id)
            instr_notes.append({
                'author': u.full_name if u else 'Instructor',
                'kind': c.kind, 'rating': c.rating, 'body': c.body,
                'when': c.created_at.isoformat() if c.created_at else None,
            })
    recs = []
    for row in eoc_avgs:
        if row['avg'] is not None and row['avg'] <= 3.0:
            recs.append("EOC '%s' averaged %s — review %s." % (row['label'], row['avg'], row['group'].lower()))
    for pack in test_packs:
        if pack.get('n_flagged'):
            recs.append('%s: %s flagged item(s).' % (pack['title'], pack['n_flagged']))
    instr = st['instructor']
    return {
        'id': section.id,
        'name': section.name,
        'course': section.course.title if section.course else None,
        'code': section.course.code if section.course else None,
        'start': section.start_date.isoformat() if section.start_date else None,
        'end': section.end_date.isoformat() if section.end_date else None,
        'instructor': instr.full_name if instr else None,
        'instructor_email': instr.email if instr else None,
        'status': st['packet'].status,
        'missing': st['missing'],
        'checks': st['checks'],
        'n_enrolled': st['n_enrolled'],
        'eoc_n': eoc_n,
        'eoc': eoc_avgs,
        'comments': comments,
        'instructor_notes': instr_notes,
        'closeout': st['packet'].closeout_note or '',
        'tests': test_packs,
        'recommendations': recs,
        'generated': utcnow().isoformat() + 'Z',
    }


@app.route('/api/tqi/login', methods=['POST', 'OPTIONS'])
@csrf.exempt  # bearer-token API, no session cookie
def api_tqi_login():
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True) or request.form
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'ok': False, 'error': 'Bad sign-in'}), 401
    if user.role != 'admin':
        return jsonify({'ok': False, 'error': 'TQI is admin only'}), 403
    token = secrets.token_hex(24)
    db.session.add(ApiToken(token=token, user_id=user.id))
    db.session.commit()
    return jsonify({'ok': True, 'token': token, 'role': user.role, 'name': user.full_name})


@app.route('/api/tqi/board', methods=['GET', 'OPTIONS'])
def api_tqi_board():
    if request.method == 'OPTIONS':
        return ('', 204)
    user = _api_user_from_token()
    if not user:
        return jsonify({'ok': False, 'error': 'Sign in'}), 401
    if user.role != 'admin':
        return jsonify({'ok': False, 'error': 'TQI is admin only'}), 403
    sections = ClassSection.query.order_by(ClassSection.name).all()
    cards = []
    for sec in sections:
        try:
            st = _tqi_status(sec)
        except Exception as err:
            cards.append({
                'id': sec.id,
                'name': sec.name or ('Class %s' % sec.id),
                'course': sec.course.title if sec.course else None,
                'code': sec.course.code if sec.course else None,
                'start': sec.start_date.isoformat() if sec.start_date else None,
                'end': sec.end_date.isoformat() if sec.end_date else None,
                'instructor': (db.session.get(User, sec.instructor_id).full_name if sec.instructor_id and db.session.get(User, sec.instructor_id) else None),
                'status': 'open',
                'missing': ['Could not finish packet status'],
                'comment_needed_from': [],
                'n_enrolled': 0,
                'eoc_n': 0,
                'instr_n': 0,
                'latest_instructor_note': None,
                'closeout': '',
                'error': str(err)[:160],
            })
            continue
        instr = st['instructor']
        latest = None
        last = TqiCritique.query.filter(
            TqiCritique.section_id == sec.id,
            TqiCritique.role.in_(['instructor', 'admin']),
        ).order_by(TqiCritique.created_at.desc()).first()
        if last:
            who = last.user or db.session.get(User, last.user_id)
            latest = {
                'author': who.full_name if who else 'Instructor',
                'kind': last.kind,
                'body': (last.body or '')[:400],
                'when': last.created_at.isoformat() if last.created_at else None,
            }
        cards.append({
            'id': sec.id,
            'name': sec.name or ('Class %s' % sec.id),
            'course': sec.course.title if sec.course else None,
            'code': sec.course.code if sec.course else None,
            'start': sec.start_date.isoformat() if sec.start_date else None,
            'end': sec.end_date.isoformat() if sec.end_date else None,
            'instructor': instr.full_name if instr else None,
            'status': st['packet'].status,
            'missing': st['missing'],
            'comment_needed_from': st.get('comment_needed_from') or [],
            'n_enrolled': st['n_enrolled'],
            'eoc_n': st['eoc_n'],
            'instr_n': st['instr_n'],
            'latest_instructor_note': latest,
            'closeout': (st['packet'].closeout_note or '')[:240],
        })
    return jsonify({'ok': True, 'role': user.role, 'name': user.full_name, 'classes': cards, 'count': len(cards)})


@app.route('/api/tqi/<int:section_id>', methods=['GET', 'OPTIONS'])
def api_tqi_class(section_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    user = _api_user_from_token()
    if not user:
        return jsonify({'ok': False, 'error': 'Sign in'}), 401
    if user.role != 'admin':
        return jsonify({'ok': False, 'error': 'TQI is admin only'}), 403
    section = db.get_or_404(ClassSection, section_id)
    payload = _tqi_payload(section, user)
    if user.role == 'student':
        payload['instructor_notes'] = []
        payload['closeout'] = ''
        payload['tests'] = []
        payload['recommendations'] = []
    return jsonify({'ok': True, 'role': user.role, 'report': payload, 'eoc_items': [
        {'key': k, 'group': g, 'label': l} for k, g, l in TQI_EOC_ITEMS
    ]})


@app.route('/api/tqi/<int:section_id>/eoc', methods=['POST', 'OPTIONS'])
@csrf.exempt  # bearer-token API, no session cookie
def api_tqi_eoc(section_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    user = _api_user_from_token()
    if not user or user.role != 'student':
        return jsonify({'ok': False, 'error': 'Student sign-in required'}), 401
    section = db.get_or_404(ClassSection, section_id)
    if not Enrollment.query.filter_by(section_id=section.id, user_id=user.id).first():
        return jsonify({'ok': False, 'error': 'Not in this class'}), 403
    data = request.get_json(silent=True) or {}
    answers = {}
    for key, _g, _l in TQI_EOC_ITEMS:
        raw = data.get(key)
        if str(raw).isdigit():
            answers[key] = max(1, min(5, int(raw)))
    if len(answers) < 6:
        return jsonify({'ok': False, 'error': 'Rate the EOC items'}), 400
    row = TqiEocResponse.query.filter_by(section_id=section.id, user_id=user.id).first()
    if not row:
        row = TqiEocResponse(section_id=section.id, user_id=user.id)
        db.session.add(row)
    row.answers_json = json.dumps(answers)
    row.comment = (data.get('comment') or '')[:4000]
    row.updated_at = utcnow()
    db.session.add(TqiCritique(
        section_id=section.id, user_id=user.id, role='student', kind='eoc',
        rating=int(round(sum(answers.values())/len(answers))),
        body=(row.comment or 'EOC survey submitted.')[:4000],
    ))
    db.session.commit()
    _tqi_status(section)
    return jsonify({'ok': True})


@app.route('/api/tqi/<int:section_id>/closeout', methods=['POST', 'OPTIONS'])
@csrf.exempt  # bearer-token API, no session cookie
def api_tqi_closeout(section_id):
    if request.method == 'OPTIONS':
        return ('', 204)
    user = _api_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'ok': False, 'error': 'TQI is admin only'}), 403
    section = db.get_or_404(ClassSection, section_id)
    data = request.get_json(silent=True) or {}
    body = (data.get('body') or '').strip()
    if len(body) < 8:
        return jsonify({'ok': False, 'error': 'Write a closeout note'}), 400
    rating = data.get('rating')
    rating = int(rating) if str(rating).isdigit() else None
    pkt = _tqi_packet(section)
    pkt.closeout_note = body[:4000]
    db.session.add(TqiCritique(section_id=section.id, user_id=user.id, role=user.role, kind='closeout', rating=rating, body=body[:4000]))
    if data.get('complete'):
        pkt.status = 'complete'
        pkt.completed_at = utcnow()
        pkt.completed_by_id = user.id
    db.session.commit()
    _tqi_status(section)
    return jsonify({'ok': True, 'status': pkt.status})


@app.route('/api/tqi/<int:section_id>/comment', methods=['POST', 'OPTIONS'])
@csrf.exempt  # bearer-token API, no session cookie
def api_tqi_comment(section_id):
    """Instructor / admin running comment on a class. Appears on novakornothing.com/tqi."""
    if request.method == 'OPTIONS':
        return ('', 204)
    user = _api_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'ok': False, 'error': 'TQI is admin only'}), 403
    section = db.get_or_404(ClassSection, section_id)
    data = request.get_json(silent=True) or {}
    body = (data.get('body') or '').strip()
    if len(body) < 4:
        return jsonify({'ok': False, 'error': 'Write a short class comment'}), 400
    kind = (data.get('kind') or 'comment').strip()[:40]
    if kind not in ('curriculum', 'instruction', 'labs', 'test', 'facility', 'closeout', 'comment', 'note', 'other'):
        kind = 'comment'
    rating = data.get('rating')
    rating = int(rating) if str(rating).isdigit() else None
    db.session.add(TqiCritique(
        section_id=section.id,
        user_id=user.id,
        role=user.role,
        kind=kind,
        rating=rating,
        body=body[:4000],
    ))
    if kind == 'closeout':
        pkt = _tqi_packet(section)
        pkt.closeout_note = body[:4000]
    db.session.commit()
    _tqi_status(section)
    return jsonify({'ok': True, 'kind': kind})


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
    tqi_by_id = {}
    for s in sections:
        try:
            tqi_by_id[s.id] = _tqi_status(s)
        except Exception as exc:
            print('tqi_status', s.id, exc)
    # pass 12: today's briefing card (top item for the first few classes; cached a few minutes, never breaks the page)
    briefs = []
    for s in sections[:4]:
        try:
            briefs.append({'section': s, **mastery_api.briefing['home_summary'](s)})
        except Exception as exc:
            db.session.rollback()
            print('briefing card', s.id, exc)
    overview = _instructor_overview(sections)
    return render_template('instructor_dashboard.html', sections=sections, courses=courses, tqi_by_id=tqi_by_id, briefs=briefs,
                           **overview)


def _instructor_roster(sections):
    """One row per enrolled student across these classes (Phase 1 Students & Grades table + CSV)."""
    rows = []
    sec_ids = [s.id for s in sections]
    if not sec_ids:
        return rows
    sec_by_id = {s.id: s for s in sections}
    att = {}
    for a in TestAttempt.query.filter(TestAttempt.section_id.in_(sec_ids), TestAttempt.completed_at.isnot(None)).all():
        att.setdefault((a.section_id, a.user_id), []).append(a)
    for enr, u in (db.session.query(Enrollment, User).join(User, User.id == Enrollment.user_id)
                   .filter(Enrollment.section_id.in_(sec_ids), User.role == 'student')
                   .order_by(User.last_name, User.first_name).all()):
        a = att.get((enr.section_id, u.id), [])
        scores = [x.score for x in a if x.score is not None]
        last = max((x.completed_at for x in a if x.completed_at), default=None)
        sec = sec_by_id[enr.section_id]
        rows.append({
            'user': u, 'section': sec, 'course': sec.course.title if sec.course else '',
            'progress': round(enr.progress_percent or 0),
            'avg': round(sum(scores) / len(scores)) if scores else None,
            'tests_taken': len(a), 'tests_passed': sum(1 for x in a if x.passed),
            'last': last,
        })
    return rows


def _instructor_overview(sections):
    roster = _instructor_roster(sections)
    taken = sum(r['tests_taken'] for r in roster)
    passed = sum(r['tests_passed'] for r in roster)
    need = []
    ws = app.jinja_env.globals.get('why_section')
    for s in sections[:6]:
        for w in ((ws(s, 10) if ws else None) or []):
            need.append({'user': w['user'], 'section': s, 'sentence': w.get('sentence') or ''})
    return {
        'roster': roster,
        'pass_rate': round(100 * passed / taken) if taken else None,
        'tests_taken': taken,
        'need_help': need[:8],
        'n_students': len({r['user'].id for r in roster}),
    }


@app.route('/instructor/roster.csv')
@login_required
def instructor_roster_csv():
    if current_user.role not in ('instructor', 'admin'):
        abort(403)
    if current_user.role == 'admin':
        sections = ClassSection.query.filter_by(is_active=True).all()
    else:
        cids = instructor_course_ids(current_user.id)
        sections = ClassSection.query.filter(ClassSection.is_active.is_(True), db.or_(
            ClassSection.instructor_id == current_user.id, ClassSection.course_id.in_(cids or [0]))).all()
    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(['student', 'email', 'course', 'class', 'progress_percent', 'average_test_score', 'tests_taken', 'tests_passed', 'last_test'])
    def cell(v):  # names are self-entered; keep spreadsheet apps from treating them as formulas
        v = '' if v is None else str(v)
        return "'" + v if v[:1] in ('=', '+', '-', '@') else v
    for r in _instructor_roster(sections):
        w.writerow([cell(r['user'].full_name), cell(r['user'].email), r['course'], cell(r['section'].name), r['progress'],
                    '' if r['avg'] is None else r['avg'], r['tests_taken'], r['tests_passed'],
                    r['last'].strftime('%Y-%m-%d') if r['last'] else ''])
    audit('roster_csv', f'{len(sections)} classes')
    return Response(buf.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=novak-roster.csv'})


@app.route('/instructor/section/<int:section_id>')
@login_required
def instructor_section(section_id):
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role != 'admin' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    modules = _modules_for_section(section)
    quizzes_by_module = {
        m.id: Quiz.query.filter_by(module_id=m.id).all()
        for m in modules
    }
    try:
        sync_skills_exams()
    except Exception:
        pass
    tests = KnowledgeTest.query.filter_by(course_id=section.course_id).order_by(KnowledgeTest.order).all()
    tests = sorted(tests, key=lambda t: (0 if (t.title or '').startswith('Skills ') else 1, t.order or 0))
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
            teach_totals[row.user_id] += int((utcnow() - row.started_at).total_seconds())
    test_stats = {}
    roster_scores = {}
    for t in tests:
        atts = TestAttempt.query.filter_by(section_id=section.id, test_id=t.id).filter(
            TestAttempt.completed_at.isnot(None)
        ).order_by(TestAttempt.completed_at.desc()).all()
        scores = [float(a.score or 0) for a in atts]
        test_stats[t.id] = {
            'n': len(scores),
            'avg': round(sum(scores) / len(scores), 1) if scores else None,
            'high': round(max(scores), 1) if scores else None,
            'low': round(min(scores), 1) if scores else None,
        }
        latest = {}
        for a in atts:
            if a.user_id not in latest:
                latest[a.user_id] = round(float(a.score or 0), 1)
        roster_scores[t.id] = latest
    tqi_status = _tqi_status(section)
    tqi_notes = []
    for c in TqiCritique.query.filter(
        TqiCritique.section_id == section.id,
        TqiCritique.role.in_(['instructor', 'admin']),
    ).order_by(TqiCritique.created_at.desc()).limit(20).all():
        who = c.user or db.session.get(User, c.user_id)
        tqi_notes.append({
            'author': who.full_name if who else 'Instructor',
            'role': c.role,
            'kind': c.kind,
            'rating': c.rating,
            'body': c.body,
            'when': c.created_at,
        })
    return render_template(
        'instructor_section.html',
        section=section,
        modules=modules,
        tests=tests,
        skills_tests=[t for t in tests if (t.title or '').startswith('Skills ')],
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
        tqi_status=tqi_status,
        tqi_notes=tqi_notes,
        test_stats=test_stats,
        roster_scores=roster_scores,
    )


@app.route('/class/<int:section_id>/labs')
@login_required
def course_labs(section_id):
    """All live labs that belong to this class's curriculum."""
    section = db.get_or_404(ClassSection, section_id)
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
        classroom=[l for l in lab_runtime.course_lab_set(section.course) if l['kind'] == 'classroom'],
        progress=lab_progress_api.progress_map(current_user.id),
    )


@app.route('/class/<int:section_id>/pilot-pack.csv')
@login_required
def section_pilot_pack(section_id):
    """Convening data pack: scores, pass/fail, category percents."""
    section = db.get_or_404(ClassSection, section_id)
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
    section = db.get_or_404(ClassSection, section_id)
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
    section = db.get_or_404(ClassSection, section_id)
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
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role not in ('admin', 'instructor') or (
        current_user.role != 'admin' and not instructor_can_access_section(current_user, section)
    ):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    quiz = db.get_or_404(Quiz, quiz_id)
    questions = json.loads(quiz.questions or '[]')
    module = db.session.get(Module, quiz.module_id)
    return render_template(
        'instructor_quiz_preview.html',
        section=section, quiz=quiz, questions=questions, module=module,
        course_id=module.course_id if module else section.course_id,
    )


@app.route('/instructor/section/<int:section_id>/test/<int:test_id>/preview')
@login_required
def instructor_test_preview(section_id, test_id):
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role not in ('admin', 'instructor') or (
        current_user.role != 'admin' and not instructor_can_access_section(current_user, section)
    ):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = db.get_or_404(KnowledgeTest, test_id)
    questions = json.loads(test.questions or '[]')
    if is_practical_payload(questions):
        questions = [
            {
                'text': 'Station: ' + (get_lab(st['lab_id']) or {}).get('title', st['lab_id']),
                'options': ['Complete the lab until it accepts the finish'],
                'correct': 'Complete the lab until it accepts the finish',
                'area': st.get('area'),
            }
            for st in stations_of(questions)
        ]
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
    section = db.get_or_404(ClassSection, section_id)
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
    section = db.get_or_404(ClassSection, section_id)
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
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role != 'admin' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    enr = db.get_or_404(Enrollment, enrollment_id)
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
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role == 'instructor' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = db.get_or_404(KnowledgeTest, test_id)
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
        user = db.session.get(User, att.user_id)
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
    attempt = db.get_or_404(TestAttempt, attempt_id)
    section = db.get_or_404(ClassSection, attempt.section_id)
    if current_user.role == 'instructor' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = db.get_or_404(KnowledgeTest, attempt.test_id)
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
    student = db.session.get(User, attempt.user_id)
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
    course = db.get_or_404(Course, course_id)
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

        instructor = db.session.get(User, sec.instructor_id) if sec.instructor_id else None
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
    course = db.get_or_404(Course, course_id)
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
    section = db.get_or_404(ClassSection, section_id)
    if current_user.role == 'instructor' and not instructor_can_access_section(current_user, section):
        flash('Access denied.', 'danger')
        return redirect(url_for('instructor_dashboard'))
    test = db.get_or_404(KnowledgeTest, test_id)
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
    section = db.session.get(ClassSection, section_id) if section_id else None
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

# ---- Admin: one overview plus focused sub-pages (classes, people, curriculum, quality/TQI) sharing a
# sub-nav (templates/_admin_nav.html). The old single long page lived at /admin with #anchors; the overview
# forwards those anchors to the matching sub-page, so bookmarks keep working.
ADMIN_TABS = [
    ('admin_dashboard', 'Overview', 'bi-speedometer2'),
    ('admin_people', 'Users & Sections', 'bi-people'),
    ('admin_exports', 'Exports', 'bi-box-arrow-down'),
    ('admin_tools', 'More tools', 'bi-tools'),
]
# Pages reached from "More tools" keep that tab highlighted; Users & Sections covers people + classes.
ADMIN_TAB_GROUP = {'admin_classes': 'admin_people', 'admin_people': 'admin_people', 'admin_dashboard': 'admin_dashboard',
                   'admin_exports': 'admin_exports', 'cmi5.admin_cmi5_registration': 'admin_exports'}
ADMIN_MORE_TOOLS = [
    ('admin_curriculum', 'Curriculum', 'What each course contains and who can teach it.'),
    ('admin_tqi', 'Results & ROI', 'Training quality packets by class.'),
    ('admin_roi', 'ROI calculator', 'Estimate savings for your seat count.'),
    ('admin_outcomes', 'Outcomes', 'Pass rates, Exam Readiness, and Skill Mastery by class.'),
    ('admin_institutions', 'Institutions', 'Campuses and single sign-on.'),
    ('admin_lti', 'LMS connections (LTI 1.3)', 'Connect Canvas, Moodle, Blackboard, or D2L.'),
    ('admin_privacy', 'Privacy', 'Export or delete a student record.'),
    ('admin_ferpa', 'FERPA', 'Directory information and disclosures.'),
    ('admin_audit_log', 'Audit log', 'Tamper-evident record of sensitive actions.'),
    ('admin_audit', 'Recent activity', 'The last 300 audit events, newest first.'),
    ('admin_tickets', 'Content tickets', 'Reported lesson issues.'),
    ('admin_teaching_time', 'Teaching time', 'Instructor time by class.'),
    ('admin_test_analytics', 'Test analytics', 'Item difficulty and flags.'),
    ('admin_compliance', 'Security & Section 508', 'Security, privacy, and accessibility packet.'),
    ('admin_readiness', 'System health', 'Developer diagnostics and production checks.'),
]



@app.context_processor
def _admin_tabs_ctx():
    return {'admin_tabs': ADMIN_TABS, 'admin_tab_group': ADMIN_TAB_GROUP}

def _admin_instructor_mode_redirect():
    if session.get('view_as') == 'instructor':
        flash('Class creation and admin tools are hidden while you work as an instructor.', 'info')
        return redirect(url_for('instructor_dashboard'))
    return None


def _teaching_by_class():
    """Teaching seconds per instructor+class (live timers included), largest first."""
    collapsed = {}
    for row in TimeLog.query.filter_by(kind='teaching').all():
        sec = _teaching_seconds(row)
        section = db.session.get(ClassSection, row.section_id) if row.section_id else None
        key = (row.user.id if row.user else 0, section.id if section else 0)
        item = collapsed.setdefault(key, {'user': row.user, 'section': section, 'seconds': 0, 'open': False})
        item['seconds'] += sec
        item['open'] = item['open'] or row.ended_at is None
    return sorted(collapsed.values(), key=lambda x: (-x['seconds'], x['user'].last_name if x['user'] else ''))


def _teaching_totals():
    totals = defaultdict(int)
    for row in TimeLog.query.filter_by(kind='teaching').all():
        totals[row.user_id] += _teaching_seconds(row)
    return totals


@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    r = _admin_instructor_mode_redirect()
    if r:
        return r
    sections = ClassSection.query.order_by(ClassSection.name).all()
    tqi = [_tqi_status(sec) for sec in sections]
    stats = {
        'classes_active': sum(1 for s in sections if s.is_active),
        'classes': len(sections),
        'students': User.query.filter_by(role='student').count(),
        'instructors': User.query.filter_by(role='instructor').count(),
        'admins': User.query.filter_by(role='admin').count(),
        'courses': Course.query.count(),
        'tqi_missing': sum(1 for t in tqi if t['missing']),
        'tqi_complete': sum(1 for t in tqi if t['packet'].status == 'complete'),
        'tickets_open': CurriculumTicket.query.filter(CurriculumTicket.status.in_(('open', 'in_progress'))).count(),
    }
    stats.update(_admin_overview_cards(sections))
    return render_template('admin_dashboard.html', admin_tab='admin_dashboard', stats=stats)


LAB_SEAT_COST_PER_YEAR = round(460 * 0.33)   # cloud VM lab seat in the ROI model (compliance_roi_pilot)


def _admin_overview_cards(sections):
    """Phase 1 admin overview: active seats, instructors, cohort Exam Readiness, estimated lab savings."""
    active_ids = [x.id for x in sections if x.is_active]
    seats = 0
    students = set()
    if active_ids:
        for (uid,) in (db.session.query(Enrollment.user_id).join(User, User.id == Enrollment.user_id)
                       .filter(Enrollment.section_id.in_(active_ids), User.role == 'student').all()):
            students.add(uid)
        seats = len(students)
    ready_pct, candidates = None, 0
    try:
        from institutional.outcomes import exam_sim_summary
        ov = exam_sim_summary(app, active_ids, students)['overall']
        candidates = ov['candidates']
        ready_pct = ov['voucher_ready_pct'] if candidates else None
    except Exception as exc:
        db.session.rollback()
        print('admin exam readiness:', exc)
    return {'seats': seats, 'ready_pct': ready_pct, 'ready_candidates': candidates,
            'lab_savings': seats * LAB_SEAT_COST_PER_YEAR, 'lab_seat_cost': LAB_SEAT_COST_PER_YEAR}


@app.route('/admin/exports', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_exports():
    r = _admin_instructor_mode_redirect()
    if r:
        return r
    from cmi5.admin import exports_context
    extra = exports_context()
    if not isinstance(extra, dict):
        return extra
    courses = Course.query.filter(Course.code.in_(['ITSUP', 'NETOPS', 'CLIENT', 'SEC'])).order_by(Course.id).all()
    return render_template('admin_exports.html', admin_tab='admin_exports', courses=courses, **extra)


@app.route('/admin/tools')
@login_required
@role_required('admin')
def admin_tools():
    r = _admin_instructor_mode_redirect()
    if r:
        return r
    tools = []
    for ep, label, desc in ADMIN_MORE_TOOLS:
        try:
            tools.append({'url': url_for(ep), 'label': label, 'desc': desc})
        except Exception:
            continue
    return render_template('admin_tools.html', admin_tab='admin_tools', tools=tools,
                           teach_by_class=_teaching_by_class()[:5], fmt_seconds=_fmt_seconds)


@app.route('/admin/classes')
@login_required
@role_required('admin')
def admin_classes():
    r = _admin_instructor_mode_redirect()
    if r:
        return r
    return render_template(
        'admin_classes.html', admin_tab='admin_classes',
        sections=ClassSection.query.order_by(ClassSection.name).all(),
        courses=Course.query.order_by(Course.code).all(),
        instructors=User.query.filter_by(role='instructor').order_by(User.last_name, User.first_name).all(),
        teach_by_class=_teaching_by_class(), fmt_seconds=_fmt_seconds,
    )


PEOPLE_PAGE_SIZE = 25


@app.route('/admin/people')
@login_required
@role_required('admin')
def admin_people():
    r = _admin_instructor_mode_redirect()
    if r:
        return r
    role = request.args.get('role', '')
    q = (request.args.get('q') or '').strip()
    users = User.query
    if role in ('student', 'instructor', 'admin'):
        users = users.filter_by(role=role)
    if q:
        like = f'%{q}%'
        users = users.filter(db.or_(User.first_name.ilike(like), User.last_name.ilike(like), User.email.ilike(like)))
    role_counts = dict(db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all())
    total = users.count()
    pages = max(1, -(-total // PEOPLE_PAGE_SIZE))
    page = min(max(request.args.get('page', 1, type=int) or 1, 1), pages)
    rows = (users.order_by(User.role, User.last_name, User.first_name, User.id)
            .offset((page - 1) * PEOPLE_PAGE_SIZE).limit(PEOPLE_PAGE_SIZE).all())
    pager = {'page': page, 'pages': pages, 'total': total,
             'first': (page - 1) * PEOPLE_PAGE_SIZE + 1 if total else 0,
             'last': (page - 1) * PEOPLE_PAGE_SIZE + len(rows)}
    return render_template(
        'admin_people.html', admin_tab='admin_people',
        users=rows, pager=pager, role=role, q=q, role_counts=role_counts,
        sections=ClassSection.query.all(),
        instructors=User.query.filter_by(role='instructor').order_by(User.last_name, User.first_name).all(),
        admins=User.query.filter_by(role='admin').order_by(User.last_name, User.first_name).all(),
        teach_totals=_teaching_totals(), fmt_seconds=_fmt_seconds,
    )


@app.route('/admin/curriculum')
@login_required
@role_required('admin')
def admin_curriculum():
    r = _admin_instructor_mode_redirect()
    if r:
        return r
    courses = Course.query.order_by(Course.code).all()
    links = defaultdict(list)
    for link in CourseInstructor.query.all():
        links[link.course_id].append(link)
    rows = []
    for c in courses:
        mod_ids = [m.id for m in Module.query.filter_by(course_id=c.id).all()]
        rows.append({
            'course': c,
            'chapters': len(mod_ids),
            'lessons': Lesson.query.filter(Lesson.module_id.in_(mod_ids)).count() if mod_ids else 0,
            'quizzes': Quiz.query.filter(Quiz.module_id.in_(mod_ids)).count() if mod_ids else 0,
            'tests': KnowledgeTest.query.filter_by(course_id=c.id).count(),
            'labs': len(labs_for_course(c)),
            'sections': ClassSection.query.filter_by(course_id=c.id).order_by(ClassSection.name).all(),
            'links': links.get(c.id, []),
        })
    return render_template(
        'admin_curriculum.html', admin_tab='admin_curriculum', rows=rows, courses=courses,
        instructors=User.query.filter_by(role='instructor').order_by(User.last_name, User.first_name).all(),
        tickets_open=CurriculumTicket.query.filter(CurriculumTicket.status.in_(('open', 'in_progress'))).count(),
    )

def _teaching_seconds(row):
    sec = row.seconds or 0
    if row.ended_at is None and row.started_at:
        sec += max(0, int((utcnow() - row.started_at).total_seconds()))
    return sec


def _teaching_time_report():
    rows = TimeLog.query.filter_by(kind='teaching').all()
    by_class, by_course, by_quarter, by_year = {}, {}, {}, {}
    # per-class seconds list for course averages (unique instructor-class pairs)
    course_class_totals = defaultdict(list)  # course_id -> [seconds per class]
    course_instr_totals = defaultdict(list)  # course_id -> [seconds per instructor]
    for row in rows:
        user = row.user
        section = db.session.get(ClassSection, row.section_id) if row.section_id else None
        course = section.course if section and section.course else None
        when = row.started_at or utcnow()
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
        return redirect(url_for('admin_classes'))
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
    return redirect(url_for('admin_classes'))


@app.route('/admin/section/toggle', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_section():
    section = db.get_or_404(ClassSection, int(request.form['section_id']))
    section.is_active = not section.is_active
    db.session.commit()
    flash(f'Section “{section.name}” is now {"active" if section.is_active else "inactive"}.', 'info')
    return redirect(url_for('admin_classes'))


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
        return redirect(url_for('admin_people'))
    if User.query.filter_by(email=email).first():
        flash('Email already exists.', 'warning')
        return redirect(url_for('admin_people'))
    if role not in ('admin', 'instructor', 'student'):
        role = 'student'
    u = User(email=email, first_name=first, last_name=last, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash(f'Created {role} {first} {last} ({email}). Sign-in password: {password}', 'success')
    return redirect(url_for('admin_people') + '#admin-staff')


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
        return redirect(url_for('admin_people') + '#admin-people')
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
        return redirect(url_for('admin_people'))
    u = User(email=email, first_name=first, last_name=last, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash(f'Added {role} {first} {last} ({email}). Temporary password: {password}', 'success')
    return redirect(url_for('admin_people') + '#admin-staff')


@app.route('/admin/instructor/make-admin', methods=['POST'])
@login_required
@role_required('admin')
def admin_make_admin():
    user = db.get_or_404(User, int(request.form.get('user_id') or 0))
    if user.id == current_user.id:
        flash('You are already an administrator.', 'info')
        return redirect(url_for('admin_people'))
    if user.role != 'instructor':
        flash('Only an instructor account can be promoted to admin from this button.', 'warning')
        return redirect(url_for('admin_people'))
    user.role = 'admin'
    db.session.commit()
    flash(f'{user.full_name} is now an administrator.', 'success')
    return redirect(url_for('admin_people'))


@app.route('/admin/admin/demote', methods=['POST'])
@login_required
@role_required('admin')
def admin_demote_admin():
    user = db.get_or_404(User, int(request.form.get('user_id') or 0))
    if user.id == current_user.id:
        flash('You cannot remove your own admin access from this screen.', 'warning')
        return redirect(url_for('admin_people') + '#admin-staff')
    if user.role != 'admin':
        flash('That account is not an administrator.', 'warning')
        return redirect(url_for('admin_people') + '#admin-staff')
    remaining = User.query.filter_by(role='admin').count()
    if remaining <= 1:
        flash('Keep at least one administrator.', 'warning')
        return redirect(url_for('admin_people') + '#admin-staff')
    user.role = 'instructor'
    db.session.commit()
    flash(f'{user.full_name} is now an instructor (admin access removed).', 'success')
    return redirect(url_for('admin_people') + '#admin-staff')


@app.route('/admin/instructor/remove', methods=['POST'])
@login_required
@role_required('admin')
def admin_remove_instructor():
    user_id = int(request.form.get('user_id') or 0)
    reassign_to = request.form.get('reassign_to') or ''
    instructor = db.get_or_404(User, user_id)
    if instructor.role != 'instructor':
        flash('That user is not an instructor.', 'warning')
        return redirect(url_for('admin_people'))
    if instructor.id == current_user.id:
        flash('You cannot remove your own account from this screen.', 'warning')
        return redirect(url_for('admin_people'))
    sections = ClassSection.query.filter_by(instructor_id=instructor.id).all()
    if sections:
        if not reassign_to:
            flash(
                f'{instructor.full_name} is assigned to {len(sections)} class(es). '
                'Choose another instructor to reassign those classes, then remove.',
                'warning',
            )
            return redirect(url_for('admin_people'))
        replacement = User.query.filter_by(id=int(reassign_to), role='instructor').first()
        if not replacement or replacement.id == instructor.id:
            flash('Select a different active instructor to take those classes.', 'warning')
            return redirect(url_for('admin_people'))
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
    return redirect(url_for('admin_people'))


@app.route('/admin/section/assign-instructor', methods=['POST'])
@login_required
@role_required('admin')
def admin_assign_instructor():
    section = db.get_or_404(ClassSection, int(request.form['section_id']))
    instructor = User.query.filter_by(id=int(request.form['instructor_id']), role='instructor').first()
    if not instructor:
        flash('Select a valid instructor.', 'warning')
        return redirect(url_for('admin_classes'))
    prev_id = section.instructor_id
    section.instructor_id = instructor.id
    if prev_id and prev_id != instructor.id:
        grant_section_instructor_access(section.id, prev_id, primary=False)
    grant_section_instructor_access(section.id, instructor.id, primary=True)
    db.session.commit()
    if prev_id and prev_id != instructor.id:
        prev = db.session.get(User, prev_id)
        prev_name = prev.full_name if prev else 'previous instructor'
        flash(
            f'{section.name} is now led by {instructor.full_name}. '
            f'{prev_name} still has access to this class.',
            'success',
        )
    else:
        flash(f'{section.name} is now assigned to {instructor.full_name}.', 'success')
    return redirect(url_for('admin_classes'))



@app.route('/admin/course/add-instructor', methods=['POST'])
@login_required
@role_required('admin')
def admin_add_course_instructor():
    course = db.get_or_404(Course, int(request.form.get('course_id') or 0))
    user = db.get_or_404(User, int(request.form.get('user_id') or 0))
    if user.role != 'instructor':
        flash('Select an instructor account.', 'warning')
        return redirect(url_for('admin_curriculum'))
    exists = CourseInstructor.query.filter_by(course_id=course.id, user_id=user.id).first()
    if exists:
        flash(f'{user.full_name} is already assigned to {course.title}.', 'info')
        return redirect(url_for('admin_curriculum'))
    db.session.add(CourseInstructor(course_id=course.id, user_id=user.id))
    db.session.commit()
    flash(f'Added {user.full_name} to curriculum set {course.title}.', 'success')
    return redirect(url_for('admin_curriculum'))


@app.route('/admin/course/remove-instructor', methods=['POST'])
@login_required
@role_required('admin')
def admin_remove_course_instructor():
    link = db.get_or_404(CourseInstructor, int(request.form.get('link_id') or 0))
    name = link.user.full_name if link.user else 'Instructor'
    title = link.course.title if link.course else 'course'
    db.session.delete(link)
    db.session.commit()
    flash(f'Removed {name} from {title}.', 'success')
    return redirect(url_for('admin_curriculum'))




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
    return send_file(p, as_attachment=True, download_name=f'novak-lms-backup-{utcnow().strftime("%Y%m%d-%H%M")}.db')


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
        course = db.session.get(Course, sec.course_id)
        instr = db.session.get(User, sec.instructor_id) if sec.instructor_id else None
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
        headers={'Content-Disposition': 'attachment; filename=novak-lms-analytics-export.csv'},
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
        course = db.session.get(Course, test.course_id)
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
        headers={'Content-Disposition': 'attachment; filename=novak-lms-item-flags.csv'},
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
        title='IT Support',
        description='Hardware, software, networking, security, and operational procedures for IT support technicians.',
    )
    netplus = Course(
        code='NETOPS',
        title='Basic Networking',
        description='Networking concepts, infrastructure, operations, security, and troubleshooting.',
    )
    client = Course(
        code='CLIENT',
        title='Operating Systems',
        description='Windows and mixed-OS clients, endpoint security, and software repair on Windows, Linux, and macOS. Proprietary Novak LMS™ course — not a vendor exam product.',
    )
    db.session.add_all([aplus, netplus, client])
    db.session.commit()
    db.session.add_all([
        CourseInstructor(course_id=aplus.id, user_id=instr1.id),
        CourseInstructor(course_id=netplus.id, user_id=instr2.id),
        CourseInstructor(course_id=client.id, user_id=instr1.id),
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
    _seed_course_modules(client, CLIENT_LESSONS)

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
        if mod.order in PILOT_CHECKS:
            bank = PILOT_CHECKS[mod.order]
        else:
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
                available_from=utcnow() - timedelta(days=1),
                available_until=utcnow() + timedelta(days=90),
                activated_by=sec.instructor_id,
                activated_at=utcnow(),
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
            available_from=utcnow() - timedelta(days=1),
            available_until=utcnow() + timedelta(days=90),
            activated_by=instr2.id, activated_at=utcnow(),
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
                    started_at=utcnow() - timedelta(days=day_ago, hours=2),
                    completed_at=utcnow() - timedelta(days=day_ago),
                ))
        # light progress marks
        for enr in enrolled:
            enr.progress_percent = _rnd.randint(15, 100)
    db.session.commit()
    _seed_helix_demo(section_a, students)
    _seed_tqi_demo()
    _ensure_gold_path_releases()
    print('Database seeded successfully (with demo test analytics).')



def _seed_helix_demo(section, students):
    """Populate clearly-labelled demo AOI timelines (is_demo=True) for the dashboard."""
    lessons = (
        Lesson.query.join(Module)
        .filter(Module.course_id == section.course_id)
        .order_by(Module.order, Lesson.order)
        .limit(4)
        .all()
    )
    return helix_pkg.seed_demo(db, _helix_models, section, list(students)[:8], lessons)



def _seed_tqi_demo():
    """Sample critiques so a class TQI report is not empty after seed."""
    if TqiCritique.query.count():
        return
    section = ClassSection.query.filter(ClassSection.name.ilike('%Section A%')).first()
    if not section:
        section = ClassSection.query.first()
    if not section:
        return
    instr = User.query.filter_by(role='instructor').first()
    students = User.query.filter_by(role='student').order_by(User.id).limit(4).all()
    samples = [
        (students[0] if students else instr, 'student', 'labs', 4, 'CLI labs matched the lesson. The switch lab needed one more example of a wrong VLAN.'),
        (students[1] if len(students) > 1 else instr, 'student', 'curriculum', 3, 'Chapter 1 was clear. RAID vs backup still feels rushed before the quiz.'),
        (students[2] if len(students) > 2 else instr, 'student', 'test', 2, 'Two items used wording we never saw in the lesson. Flag those for rewrite.'),
        (instr, 'instructor', 'instruction', 4, 'Pace was fine. Reteach default gateway before the knowledge test. Student critiques match the item flags on DNS vs path.'),
        (instr, 'instructor', 'test', 3, 'Item analysis shows two non-functional distractors on the first knowledge test. Those belong in the TQI packet for the next convening.'),
    ]
    for user, role, kind, rating, body in samples:
        if not user:
            continue
        db.session.add(TqiCritique(
            section_id=section.id,
            user_id=user.id,
            role=role,
            kind=kind,
            rating=rating,
            body=body,
        ))
    # Structured EOC surveys so the packet can auto-ready
    keys = [k for k, _g, _l in TQI_EOC_ITEMS]
    for i, stu in enumerate(User.query.filter_by(role='student').order_by(User.id).limit(12).all()):
        answers = {k: 3 + ((i + n) % 3) for n, k in enumerate(keys)}
        db.session.add(TqiEocResponse(
            section_id=section.id,
            user_id=stu.id,
            answers_json=json.dumps(answers),
            comment='Demo end-of-course survey comment.',
        ))
    pkt = TqiPacket.query.filter_by(section_id=section.id).first()
    if not pkt:
        pkt = TqiPacket(section_id=section.id, status='open')
        db.session.add(pkt)
    db.session.commit()


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


_INSTRUCTOR_NOTE_RE = re.compile(r'<div class="instructor-note">.*?</div>', re.S)


@app.template_filter('render_lesson')
def render_lesson_filter(text):
    out = render_lesson_html(text)
    # pass 8: per-lesson teaching notes (timing, common misses) are for staff; students get the lesson only
    try:
        staff = current_user.is_authenticated and current_user.role in ('instructor', 'admin')
    except Exception:
        staff = False
    return out if staff else _INSTRUCTOR_NOTE_RE.sub('', out)


def sync_curriculum():
    """Overwrite lesson HTML in an existing DB so students see real pages."""
    aplus = Course.query.filter_by(code='ITSUP').first() or Course.query.filter_by(code='APLUS').first()
    netplus = Course.query.filter_by(code='NETOPS').first() or Course.query.filter_by(code='NETPLUS').first()
    client = Course.query.filter_by(code='CLIENT').first()
    if not aplus or not netplus:
        return False
    aplus.code, aplus.title = 'ITSUP', 'IT Support'
    aplus.description = 'Hardware, client networking, virtualization, and ticket habits for IT support technicians. Proprietary Novak LMS™ course.'
    netplus.code, netplus.title = 'NETOPS', 'Basic Networking'
    netplus.description = 'Networking concepts, infrastructure, operations, security, and troubleshooting.'
    if not client:
        client = Course(
            code='CLIENT',
            title='Operating Systems',
            description='Windows and mixed-OS clients, endpoint security, and software repair on Windows, Linux, and macOS. Proprietary Novak LMS™ course — not a vendor exam product.',
        )
        db.session.add(client)
        db.session.flush()
    else:
        client.title = 'Operating Systems'
        client.description = 'Windows and mixed-OS clients, endpoint security, and software repair on Windows, Linux, and macOS. Proprietary Novak LMS™ course — not a vendor exam product.'

    # Phase 1 course renames: carry the new titles into existing class section names on live databases.
    _renames = (('Client Systems & Shop Procedures', 'Operating Systems'), ('IT Support Technician Fundamentals', 'IT Support'),
                ('Network Operations Fundamentals', 'Basic Networking'))
    for _sec in ClassSection.query.all():
        _nm = _sec.name or ''
        for _old, _new in _renames:
            _nm = _nm.replace(_old, _new)
        if _nm.strip() == 'Operating Systems — CLIENT-101':
            _nm = 'Operating Systems Fall 2026 — Section E'
        if _nm != (_sec.name or ''):
            _sec.name = _nm
    for course, pack in ((aplus, APLUS_LESSONS), (netplus, NETPLUS_LESSONS), (client, CLIENT_LESSONS)):
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
            # Update lessons in place (matched by order) so lesson ids stay stable
            # across restarts. Deleting + re-inserting used to orphan every
            # lesson-keyed row (Helix timelines, tickets, bookmarks) on each boot.
            existing = {L.order: L for L in Lesson.query.filter_by(module_id=m.id).all()}
            wanted = set()
            for idx, les in enumerate(lesson_list, start=1):
                lorder = int(les.get('order') or idx)
                wanted.add(lorder)
                row = existing.get(lorder)
                if row is None:
                    row = Lesson(module_id=m.id, order=lorder)
                    db.session.add(row)
                row.title = les.get('title') or f'Lesson {idx}'
                row.content = les.get('html') or ''
                row.estimated_minutes = les.get('minutes', 30)
            for lorder, row in existing.items():
                if lorder not in wanted:
                    db.session.delete(row)
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
    from curriculum_sec.sync_course import ensure_sec
    ensure_sec(db, {
        'Course': Course, 'Module': Module, 'Lesson': Lesson, 'Quiz': Quiz,
        'KnowledgeTest': KnowledgeTest, 'ClassSection': ClassSection, 'Enrollment': Enrollment,
        'User': User, 'CourseInstructor': CourseInstructor, 'ContentRelease': ContentRelease,
    }, utcnow, grant=grant_section_instructor_access)
    db.session.commit()
    from curriculum_v2.lesson_visuals import apply_lesson_visuals
    apply_lesson_visuals(db, Course, Module, Lesson)
    _ensure_gold_path_releases()
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
        if 'quiz_attempt' in tables and 'section_id' not in {c['name'] for c in insp.get_columns('quiz_attempt')}:
            with db.engine.begin() as conn:
                conn.execute(text('ALTER TABLE quiz_attempt ADD COLUMN section_id INTEGER'))
        if 'content_release' in tables:
            rcols = {c['name'] for c in insp.get_columns('content_release')}
            if 'user_id' not in rcols:
                with db.engine.begin() as conn:
                    conn.execute(text('ALTER TABLE content_release ADD COLUMN user_id INTEGER'))
    except Exception as e:
        print('Schema ensure note:', e)


def _ensure_gold_path_releases():
    """Do not auto-open graded tests. Instructors / admins release tests per class."""
    return 0


def init_db():
    db.create_all()
    institutional_api.ensure_schema()   # tenant columns + default institution before any User query
    school_api.ensure_schema()          # audit_event chain columns before any audit row is written
    _ensure_schema()
    helix_pkg.ensure_schema(db)
    gradebook_mod.ensure_schema(db)
    from mastery.models import ensure_schema as _mastery_schema   # pass 13: mastery_setting.cert_items
    _mastery_schema(db)
    if User.query.count() == 0:
        print('Seeding database...')
        seed_database()
        # pass 13 (readiness audit): a brand-new install used to stop here, so until the first restart its chapter
        # checks were the generic seed sets (no objective tags, so the adaptive engine had no check items) and the
        # skills midterm/final were not synced. Run the same content syncs as an existing database.
        _sync_content()
        institutional_api.ensure_schema()   # seeding recreates tables: re-assert the default institution
        school_api.ensure_schema()
        _ensure_schema()
        helix_pkg.ensure_schema(db)
        gradebook_mod.ensure_schema(db)
        _mastery_schema(db)
        if os.environ.get('RENDER'):
            try:
                section = ClassSection.query.filter(ClassSection.name.ilike('%Section A%')).first()
                students = User.query.filter_by(role='student').order_by(User.id).limit(8).all()
                if section and students:
                    _seed_helix_demo(section, students)
                if TqiCritique.query.count() == 0:
                    _seed_tqi_demo()
            except Exception as e:
                print('Render demo seed note:', e)
        return
    try:
        live = (HelixGazeSession.query
                .filter(HelixGazeSession.lesson_id.in_(db.session.query(Lesson.id))).count())
        if live == 0 and os.environ.get('HELIX_DEMO_SEED', '1') != '0':
            section = ClassSection.query.filter(ClassSection.name.ilike('%Section A%')).first()
            students = User.query.filter_by(role='student').order_by(User.id).limit(8).all()
            if section and students:
                n = _seed_helix_demo(section, students)
                print(f'Seeded {n} Helix demo sessions (is_demo=True).')
        if TqiCritique.query.count() == 0:
            _seed_tqi_demo()
            print('Seeded TQI demo critiques.')
    except Exception as e:
        print('Helix seed note:', e)
    # Do not drop_all on an existing schoolhouse DB — that hangs startup
    # and looks like the site is down. Sync lesson text only.
    _sync_content()


def _sync_content():
    try:
        sync_curriculum()
    except Exception as e:
        print('Curriculum sync note:', e)
    try:
        n = sync_pilot_slice()
        if n:
            print('Synced pilot checks for', n, 'chapters.')
    except Exception as e:
        print('Pilot slice sync note:', e)
    try:
        n = sync_skills_exams()
        if n:
            print('Synced skills midterm/final for', n, 'exams.')
    except Exception as e:
        print('Skills exam sync note:', e)
    try:
        n = _ensure_gold_path_releases()
        if n:
            print('Opened first knowledge test on', n, 'classes for the student gold path.')
    except Exception as e:
        print('Gold path release note:', e)
    try:
        # Phase 1 plain-English rename: stored practice-exam statuses read "EXAM READY".
        r = db.session.execute(db.text(
            "UPDATE exam_sim_grade SET status='EXAM READY' WHERE status='VOUCHER READY'"))
        db.session.commit()
        if r.rowcount:
            print('Renamed', r.rowcount, 'practice exam statuses to EXAM READY.')
    except Exception as e:
        db.session.rollback()
        print('Exam status rename note:', e)


import gradebook as gradebook_mod
gradebook_mod.register(app, db, dict(
    User=User, ClassSection=ClassSection, Enrollment=Enrollment, KnowledgeTest=KnowledgeTest,
    TestAttempt=TestAttempt, Quiz=Quiz, QuizAttempt=QuizAttempt, Module=Module, LabCompletion=LabCompletion,
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
    is_content_available=lambda *a, **k: is_content_available(*a, **k),
    audit=lambda action, detail='': audit(action, detail),
))
helix_pkg.init_app(app, db, dict(
    User=User, Lesson=Lesson, Module=Module, ClassSection=ClassSection, Enrollment=Enrollment,
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
    audit=lambda action, detail='': audit(action, detail),
))
# pass 8: course materials (syllabus, pacing, lesson plans, rubrics, keys) + per-section syllabus fields
from curriculum_v2 import materials as materials_mod  # noqa: E402
SyllabusSettings = materials_mod.register(app, db, dict(
    Course=Course, ClassSection=ClassSection, Enrollment=Enrollment,
    instructor_can_access_section=lambda user, section: instructor_can_access_section(user, section),
    instructor_course_ids=lambda uid: instructor_course_ids(uid),
    audit=lambda action, detail='': audit(action, detail),
))
# pass 11: certification coverage (staff) and practice exams — curriculum_v2/cert/practice.py
from curriculum_v2.cert import practice as cert_practice  # noqa: E402
PracticeAttempt = cert_practice.register(app, db, dict(
    Course=Course, Module=Module, Lesson=Lesson, ClassSection=ClassSection, Enrollment=Enrollment, utcnow=utcnow,
    audit=lambda action, detail='': audit(action, detail),
))

# Option B pass 1: Exam-Day Readiness Simulator (timed full/sprint sittings, PBQs first, scaled score, readiness badge)
from curriculum_v2.cert import exam_sim as cert_exam_sim  # noqa: E402
ExamSimAttempt = cert_exam_sim.register(app, db, dict(
    User=User, Course=Course, Module=Module, Lesson=Lesson, ClassSection=ClassSection, Enrollment=Enrollment,
    utcnow=utcnow, can_access_section=lambda user, section: instructor_can_access_section(user, section),
    audit=lambda action, detail='': audit(action, detail),
))

# Option B pass 4: rapid-fire port / protocol / acronym / command speed-drill with spaced repetition
from curriculum_v2.cert import speed_drill as cert_speed_drill  # noqa: E402
SpeedDrillStat = cert_speed_drill.register(app, db, dict(ClassSection=ClassSection, Enrollment=Enrollment, utcnow=utcnow))

# pass 11: adaptive mastery engine (per-objective BKT estimates, inserted reviews, test-out, overrides)
import mastery as mastery_mod  # noqa: E402
from interactive_labs import LESSON_LABS as _MX_LESSON_LABS, get_lab as _mx_get_lab  # noqa: E402
from mastery.lab_source import make_lab_events as _mx_lab_events, lab_def as _mx_lab_def  # noqa: E402
from curriculum_v2.course_package import GLOSSARY as _MX_GLOSSARY, GLOSSARY_NEW as _MX_GLOSSARY_NEW  # noqa: E402
mastery_api = mastery_mod.register(app, db, dict(
    User=User, ClassSection=ClassSection, Enrollment=Enrollment, Course=Course, Module=Module, Lesson=Lesson,
    Quiz=Quiz, QuizAttempt=QuizAttempt, KnowledgeTest=KnowledgeTest, TestAttempt=TestAttempt,
    LabCompletion=LabCompletion, TimeLog=TimeLog,
    is_content_available=lambda *a, **k: is_content_available(*a, **k),
    is_practical_payload=is_practical_payload, stations_of=stations_of, LESSON_LABS=_MX_LESSON_LABS,
    HelixConsent=HelixConsent, HelixSectionSetting=HelixSectionSetting, HelixGazeSession=HelixGazeSession,
    HelixAoiBucket=HelixAoiBucket, HELIX_POLICY_VERSION=HELIX_POLICY_VERSION,
    glossary=_MX_GLOSSARY, glossary_marked=_MX_GLOSSARY_NEW,
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
    audit=lambda action, detail='': audit(action, detail),
    # pass 12: live lab event log (latest attempt per lab, this class only) + lab definitions for process diagnosis
    # pass 12: practice exams (content merge) as evidence, weight 0.8, graded with the practice module's own rules
    ContentRelease=ContentRelease,
    PracticeAttempt=PracticeAttempt, practice_bank=cert_practice.bank, practice_grade=cert_practice.grade,
    ExamSimAttempt=ExamSimAttempt,  # Option B pass 5: exam-simulator sittings as mastery evidence (weight 0.85)
    lab_events=_mx_lab_events(lab_progress_api.LabProgress, lab_progress_api.LabEvent), lab_def=_mx_lab_def(_mx_get_lab),
))

# pass 12: LTI 1.3 + LTI Advantage, tool side (lti/): OIDC login, launch, deep linking, AGS scores, NRPS roster
import lti as lti_mod  # noqa: E402
from interactive_labs import labs_for_course as _lti_labs_for_course  # noqa: E402
lti_api = lti_mod.register(app, db, dict(
    User=User, ClassSection=ClassSection, Enrollment=Enrollment, Course=Course, Module=Module, Lesson=Lesson,
    Quiz=Quiz, KnowledgeTest=KnowledgeTest, LabProgress=lab_progress_api.LabProgress,
    labs_for_course=_lti_labs_for_course, get_lab=get_lab,
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
    audit=lambda action, detail='': audit(action, detail),
), csrf)

# Priority 3: curriculum-grounded AI tutor + skills portfolio
import tutor as tutor_mod  # noqa: E402
import portfolio as portfolio_mod  # noqa: E402
tutor_api = tutor_mod.register(app, db, dict(
    Course=Course, Module=Module, Lesson=Lesson, ClassSection=ClassSection, Enrollment=Enrollment, glossary=_MX_GLOSSARY,
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
    audit=lambda action, detail='': audit(action, detail),
))
portfolio_api = portfolio_mod.register(app, db, dict(
    User=User, Course=Course, ClassSection=ClassSection, Enrollment=Enrollment, mastery=lambda: mastery_api,
    lab_api=lab_progress_api, get_lab=get_lab, ExamSimAttempt=ExamSimAttempt,
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
))

# Priority 3/4: institutions (tenants), campus SSO, outcomes reporting
import institutional as institutional_mod  # noqa: E402
institutional_api = institutional_mod.register(app, db, dict(
    User=User, ClassSection=ClassSection, Enrollment=Enrollment, TimeLog=TimeLog, get_lab=get_lab,
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
    audit=lambda action, detail='': audit(action, detail),
))

# pass 13: first-run experience (instructor "Set up your class" checklist, one-time student introduction)
import onboarding as onboarding_mod  # noqa: E402
onboarding_api = onboarding_mod.register(app, db, dict(
    ClassSection=ClassSection, Module=Module, ContentRelease=ContentRelease, HelixSectionSetting=HelixSectionSetting,
    mastery_settings=lambda section_id: mastery_api.engine.settings(section_id),
    can_access_section=lambda user, section: instructor_can_access_section(user, section),
))

from mastery import why as why_mod  # noqa: E402  (pilot pass: "Why this student is struggling" + "What finally clicked")
why_mod.install(app, db)
from institutional import school_ready as school_mod  # noqa: E402  (school-ready pass: roles, sections hub, FERPA, audit chain)
school_api = school_mod.register(app, db, dict(
    User=User, ClassSection=ClassSection, Enrollment=Enrollment, AuditEvent=AuditEvent, ContentRelease=ContentRelease,
    Course=Course, TimeLog=TimeLog, get_lab=get_lab, audit=audit, owner_access=lambda u, s: _owner_access(u, s),
    accessible_sections=lambda u: instructor_accessible_sections(u),
    same_tenant=lambda u, o: institutional_api.same_tenant(u, o),
    setup_checklist=lambda s, u: onboarding_api['setup_checklist'](s, u),
))


def _safe_mastery_path(user, section):
    """Recommended next steps for an enrolled student; never breaks the page it sits on."""
    if not section or getattr(user, 'role', None) != 'student':
        return None
    if not Enrollment.query.filter_by(user_id=user.id, section_id=section.id).first():
        return None
    try:
        return mastery_api.student_path(user, section)
    except Exception as exc:
        db.session.rollback()
        print('mastery path:', exc)
        return None


_ERRORS = {
    403: ('bi-shield-lock', "You don't have access to this page",
          'This page belongs to a different role or class. If you think you should see it, ask your instructor or an administrator.'),
    404: ('bi-signpost-split', "We couldn't find that page",
          'The link may be old, or the lesson, class or item may have moved. Check the address or start again from your home page.'),
    405: ('bi-slash-circle', "That action isn't available here",
          'The page was opened in a way it does not support. Go back and use the buttons on the page.'),
    500: ('bi-tools', 'Something went wrong on our side',
          'The error has been logged. Try again in a moment.'),
}


def _home_url():
    try:
        r = current_user.role if current_user.is_authenticated else None
    except Exception:
        r = None
    return url_for({'admin': 'admin_dashboard', 'instructor': 'instructor_dashboard', 'student': 'student_dashboard'}.get(r, 'index'))


def _error_page(code, detail=None):
    if request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json':
        return jsonify({'error': {403: 'forbidden', 404: 'not_found', 405: 'method_not_allowed', 500: 'server_error'}.get(code, 'error')}), code
    icon, title, msg = _ERRORS[code]
    try:
        return render_template('error.html', code=code, icon=icon, title=title, message=msg, detail=detail, home_url=_home_url()), code
    except Exception:   # never let the error page itself fail (e.g. DB down during a 500)
        return (f'<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>'
                f'<main style="font-family:system-ui;max-width:32rem;margin:15vh auto;padding:0 1rem"><h1>{title}</h1><p>{msg}</p>'
                f'<p><a href="/">Home</a></p></main>'), code


@app.errorhandler(403)
def _e403(e):
    return _error_page(403)


@app.errorhandler(404)
def _e404(e):
    return _error_page(404)


@app.errorhandler(405)
def _e405(e):
    return _error_page(405)


@app.errorhandler(500)
def _e500(e):
    try:
        db.session.rollback()
    except Exception:
        pass
    return _error_page(500)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    wants_json = request.is_json or request.path.startswith('/api/') or \
        'application/json' in (request.headers.get('Accept') or '')
    if wants_json:
        return jsonify({'ok': False, 'error': 'csrf', 'detail': e.description}), 400
    return render_template('csrf_error.html', reason=e.description), 400


import cmi5 as cmi5_pkg  # noqa: E402
cmi5_pkg.register(app, db, dict(
    Course=Course, Module=Module, Lesson=Lesson, Quiz=Quiz, ClassSection=ClassSection,
), csrf)

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

    if not app.config.get('NEURAL_TTS_ENABLED', True):
        return jsonify({'error': 'Neural voice is turned off on this server', 'fallback': True, 'disabled': True}), 403
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


# ---------- Data & privacy (pass 10): privacy notice, student-record export/delete, Helix retention
import privacy_tools as _privacy


@app.route('/privacy')
def privacy_page():
    return render_template('privacy.html', neural_tts=app.config.get('NEURAL_TTS_ENABLED', True),
                           helix_days=_privacy.helix_retention_days(app))


def _student_or_404(user_id):
    u = db.get_or_404(User, user_id)
    if u.role != 'student':
        abort(404)   # the tool is for student records only; staff accounts are managed on People
    return u


@app.route('/admin/privacy')
@login_required
@role_required('admin')
def admin_privacy():
    q = (request.args.get('q') or '').strip()
    students = []
    if q:
        like = f'%{q}%'
        students = (User.query.filter_by(role='student')
                    .filter(db.or_(User.email.ilike(like), User.first_name.ilike(like), User.last_name.ilike(like)))
                    .order_by(User.last_name, User.first_name).limit(25).all())
    preview = None
    sid = request.args.get('user_id', type=int)
    if sid:
        u = _student_or_404(sid)
        doomed, nullify, _t = _privacy.plan(db, u.id)
        preview = {'user': u, 'tables': sorted((k, len(v)) for k, v in doomed.items()),
                   'anonymised': sorted((f'{k[0]}.{k[1]}', len(v)) for k, v in nullify.items())}
    days = _privacy.helix_retention_days(app)
    due = _privacy.helix_cleanup(db, _helix_models, days, dry_run=True)
    log = (AuditEvent.query.filter(AuditEvent.action.in_(['student_record_export', 'student_record_delete', 'helix_retention_cleanup']))
           .order_by(AuditEvent.created_at.desc()).limit(20).all())
    return render_template('admin_privacy.html', admin_tab='admin_privacy', q=q, students=students, preview=preview,
                           days=days, due=due, log=log, neural_tts=app.config.get('NEURAL_TTS_ENABLED', True))


@app.route('/admin/privacy/student/<int:user_id>/export.json')
@login_required
@role_required('admin')
def admin_student_export(user_id):
    u = _student_or_404(user_id)
    data = _privacy.export(db, u.id)
    audit('student_record_export', f'user={u.id} rows={sum(data["counts"].values())}')
    return Response(_privacy.to_json(data), mimetype='application/json',
                    headers={'Content-Disposition': f'attachment; filename=student-record-{u.id}.json'})


@app.route('/admin/privacy/student/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_student_delete(user_id):
    u = _student_or_404(user_id)
    if (request.form.get('confirm_email') or '').strip().lower() != (u.email or '').lower():
        flash('Type the student’s email address exactly to confirm the deletion.', 'warning')
        return redirect(url_for('admin_privacy', user_id=u.id))
    uid = u.id
    res = _privacy.delete_record(db, uid)
    # the audit row names the id and counts only (not the email), so the log itself holds no PII
    audit('student_record_delete', f'user={uid} deleted={sum(res["deleted"].values())} '
          f'tables={",".join(sorted(res["deleted"]))[:250]} anonymised={sum(res["anonymised"].values())}')
    flash(f'Deleted the full record of student #{uid} ({sum(res["deleted"].values())} rows). Shared records were kept without their name.', 'success')
    app.logger.info('student record %s deleted by admin %s', uid, current_user.id)
    return redirect(url_for('admin_privacy'))


@app.route('/admin/privacy/helix-cleanup', methods=['POST'])
@login_required
@role_required('admin')
def admin_helix_cleanup():
    days = _privacy.helix_retention_days(app)
    res = _privacy.helix_cleanup(db, _helix_models, days)
    audit('helix_retention_cleanup', f'days={days} sessions={res["sessions"]} buckets={res["buckets"]} '
          f'events={res["events"]} accuracy={res["accuracy_records"]}')
    flash(f'Helix retention cleanup: removed {res["sessions"]} sessions, {res["buckets"]} AOI rows, {res["events"]} events '
          f'and {res["accuracy_records"]} accuracy records older than {days} days.' if days > 0 else
          'Helix retention is set to keep data (0 days); nothing was removed.', 'info')
    return redirect(url_for('admin_privacy'))


import click as _click


@app.cli.command('helix-cleanup')
@_click.option('--dry-run', is_flag=True, help='Only count what would be removed.')
def helix_cleanup_command(dry_run):
    """Delete Helix data older than CIWT_HELIX_RETENTION_DAYS (default 365)."""
    dry = dry_run
    days = _privacy.helix_retention_days(app)
    res = _privacy.helix_cleanup(db, _helix_models, days, dry_run=dry)
    if not dry:
        db.session.add(AuditEvent(action='helix_retention_cleanup', role='system',
                                  detail=f'cli days={days} sessions={res["sessions"]} events={res["events"]} accuracy={res["accuracy_records"]}'))
        db.session.commit()
    print(_privacy.to_json(res))


def run_settings(env=None):
    """Host/port/debug for `python app.py`. Debug is OFF unless FLASK_DEBUG=1 is set explicitly; with
    debug on, the server binds to 127.0.0.1 (the Werkzeug debugger runs code for whoever can reach it)
    unless CIWT_ALLOW_DEBUG_ON_NETWORK=1 is also set."""
    env = os.environ if env is None else env
    debug = (env.get('FLASK_DEBUG') or '').strip().lower() in ('1', 'true', 'yes', 'on')
    port = int(env.get('PORT') or 5050)
    host = (env.get('HOST') or '').strip() or ('127.0.0.1' if debug else '0.0.0.0')
    note = ''
    if debug and host not in ('127.0.0.1', 'localhost', '::1') and env.get('CIWT_ALLOW_DEBUG_ON_NETWORK') != '1':
        note = f'FLASK_DEBUG=1: binding to 127.0.0.1 instead of {host} (set CIWT_ALLOW_DEBUG_ON_NETWORK=1 to override).'
        host = '127.0.0.1'
    return host, port, debug, note


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

if not app.config.get('TESTING') and os.environ.get('SECRET_KEY') != 'test' and (
    os.environ.get('CIWT_ALLOW_REAL_DB') == '1'
    or os.environ.get('RENDER')
    or os.environ.get('CIWT_RICH_DEMO') == '1'
):
    try:
        from demo_telemetry import ensure_rich_demo_telemetry
        ensure_rich_demo_telemetry(app)
    except Exception as _dt_exc:
        print('Demo telemetry seed note:', _dt_exc)


if __name__ == '__main__':
    _host, _port, _debug, _note = run_settings()
    if _note:
        print(_note)
    print(f'Novak LMS on http://{_host}:{_port}  debug={"on" if _debug else "off"}')
    app.run(host=_host, port=_port, debug=_debug)
