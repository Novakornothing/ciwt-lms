"""School-ready pass: section staff roles, multi-section hub + rosters, FERPA export/delete + hash-chained audit log,
accessibility statement and the one-page section setup checklist. All new copy is Pending SME review."""
import csv
import hashlib
import io
import json
import secrets
import string
import time as _time
import zipfile
from datetime import datetime, timezone

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import event, inspect, text


ROLES = {'lead': 'Lead instructor', 'ta': 'Teaching assistant', 'observer': 'Observer (read-only)'}
TA_DENY = ('lti', 'privacy', 'roster', 'setup', 'clone', 'delete', 'ferpa', 'staff', 'reassign')
SECRET = ('password', 'hash', 'token', 'secret', 'private', 'key_pem', 'otp')
KEEP_ON_DELETE = {'audit_event', 'data_request'}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def register(app, db, d):
    User, ClassSection, Enrollment, AuditEvent = d['User'], d['ClassSection'], d['Enrollment'], d['AuditEvent']

    class SectionStaff(db.Model):
        __tablename__ = 'section_staff'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        role = db.Column(db.String(12), nullable=False, default='ta')
        added_by = db.Column(db.Integer)
        added_at = db.Column(db.DateTime, default=utcnow)
        __table_args__ = (db.UniqueConstraint('section_id', 'user_id', name='uq_section_staff'),)

    class SectionJoinCode(db.Model):
        __tablename__ = 'section_join_code'
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), primary_key=True)
        code = db.Column(db.String(20), unique=True, nullable=False)

    class DataRequest(db.Model):
        """FERPA request: a student (or staff on their behalf) asks for an export, a correction or deletion."""
        __tablename__ = 'data_request'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False, index=True)
        kind = db.Column(db.String(12), nullable=False)          # export | correct | delete
        note = db.Column(db.String(1000), default='')
        status = db.Column(db.String(12), default='open')        # open | done | denied
        created_by = db.Column(db.Integer)
        created_at = db.Column(db.DateTime, default=utcnow)
        handled_by = db.Column(db.Integer)
        handled_at = db.Column(db.DateTime)
        outcome = db.Column(db.String(400), default='')

    # ------------------------------------------------------------------ tamper-evident audit chain
    def _digest(prev, ev):
        raw = '|'.join(str(x if x is not None else '') for x in (
            prev, ev.created_at.isoformat() if ev.created_at else '', ev.user_id, ev.role, ev.action, ev.detail,
            ev.path, ev.ip, getattr(ev, 'section_id', None)))
        return hashlib.sha256(raw.encode()).hexdigest()

    @event.listens_for(AuditEvent, 'before_insert')
    def _chain(mapper, conn, ev):
        ev.created_at = (ev.created_at or utcnow()).replace(microsecond=0)
        prev = conn.info.get('audit_tail')
        if prev is None:
            prev = conn.execute(text('SELECT hash FROM audit_event WHERE hash IS NOT NULL ORDER BY id DESC LIMIT 1')).scalar() or ''
        ev.prev_hash = prev
        ev.hash = _digest(prev, ev)
        conn.info['audit_tail'] = ev.hash

    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, 'commit')
    @event.listens_for(Engine, 'rollback')
    def _reset_tail(conn):   # the tail cache only chains rows within one transaction; re-read it afterwards
        conn.info.pop('audit_tail', None)

    def verify_chain():
        prev, n, bad = None, 0, None
        for ev in AuditEvent.query.filter(AuditEvent.hash.isnot(None)).order_by(AuditEvent.id).all():
            if prev is not None and ev.prev_hash != prev or _digest(ev.prev_hash, ev) != ev.hash:
                bad = ev.id
                break
            prev, n = ev.hash, n + 1
        legacy = AuditEvent.query.filter(AuditEvent.hash.is_(None)).count()
        return {'ok': bad is None, 'checked': n, 'broken_at': bad, 'legacy': legacy}

    def ensure_schema():
        insp = inspect(db.engine)
        cols = {c['name'] for c in insp.get_columns('audit_event')}
        with db.engine.begin() as conn:
            for c, t in (('section_id', 'INTEGER'), ('prev_hash', 'VARCHAR(64)'), ('hash', 'VARCHAR(64)')):
                if c not in cols:
                    conn.execute(text(f'ALTER TABLE audit_event ADD COLUMN {c} {t}'))
        db.create_all()

    # ------------------------------------------------------------------ roles
    def staff_role(user, section):
        """'lead' | 'ta' | 'observer' | None for one class."""
        if not getattr(user, 'is_authenticated', False) or section is None or user.role not in ('instructor', 'admin'):
            return None
        row = SectionStaff.query.filter_by(section_id=section.id, user_id=user.id).first()
        if user.role == 'admin' or section.instructor_id == user.id:
            return 'lead'
        if row:
            return row.role
        return 'lead' if d['owner_access'](user, section) else None

    def can_manage_section(user, section):
        return staff_role(user, section) == 'lead'

    def can_edit_grades(user, section):
        return staff_role(user, section) in ('lead', 'ta')

    can_edit_settings = can_manage_section

    @app.before_request
    def _staff_guard():
        va = request.view_args or {}
        sid = va.get('section_id')
        if not isinstance(sid, int) or not request.path.startswith('/instructor/') or not current_user.is_authenticated:
            return None
        if current_user.role not in ('instructor', 'admin'):
            return None
        sec = db.session.get(ClassSection, sid)
        role = staff_role(current_user, sec)
        if role == 'observer' and request.method != 'GET':
            abort(403)
        if role in ('ta', 'observer') and (request.method != 'GET' or '/privacy' in request.path) and \
                any(w in (request.endpoint or '') or f'/{w}' in request.path for w in TA_DENY):
            abort(403)
        return None

    def section_or_403(section_id, need='view'):
        sec = db.get_or_404(ClassSection, section_id)
        role = staff_role(current_user, sec)
        if role is None or (need == 'lead' and role != 'lead') or (need == 'grade' and role == 'observer'):
            abort(403)
        return sec, role

    def my_sections(user):
        secs = {s.id: s for s in d['accessible_sections'](user)}
        for r in SectionStaff.query.filter_by(user_id=user.id).all():
            s = db.session.get(ClassSection, r.section_id)
            if s:
                secs[s.id] = s
        return sorted(secs.values(), key=lambda s: (s.course_id, s.name))

    @app.context_processor
    def _school_ctx():
        def switcher():
            if not current_user.is_authenticated or current_user.role not in ('instructor', 'admin'):
                return []
            try:
                return my_sections(current_user)[:30]
            except Exception:
                db.session.rollback()
                return []
        return {'school_sections': switcher}

    # ------------------------------------------------------------------ join codes, clone, roster
    def join_code(section, fresh=False):
        row = db.session.get(SectionJoinCode, section.id)
        alphabet = ''.join(c for c in string.ascii_uppercase + string.digits if c not in 'O0I1')
        if row and not fresh:
            return row.code
        code = ''.join(secrets.choice(alphabet) for _ in range(8))
        if row:
            row.code = code
        else:
            db.session.add(SectionJoinCode(section_id=section.id, code=code))
        db.session.commit()
        return code

    def _section_models():
        """Per-class settings tables (one row per class): adaptive, ladder, Helix, grading weights, LTI policy..."""
        for mp in db.Model.registry.mappers:
            t = mp.local_table
            col = t.c.get('section_id') if hasattr(t, 'c') else None
            if col is not None and (col.unique or col.primary_key) and t.name not in ('tqi_packet', 'section_join_code'):
                yield mp.class_

    def clone_section(src, actor):
        new = ClassSection(name=f'{src.name} (copy)'[:100], course_id=src.course_id, instructor_id=actor.id
                           if actor.role == 'instructor' else src.instructor_id, max_students=src.max_students,
                           start_date=src.start_date, end_date=src.end_date, is_active=True,
                           institution_id=getattr(src, 'institution_id', None))
        db.session.add(new)
        db.session.flush()
        for M in _section_models():
            row = M.query.filter_by(section_id=src.id).first()
            if row is None:
                continue
            cols = [c.key for c in inspect(M).column_attrs if c.key not in ('id', 'section_id')]
            db.session.add(M(section_id=new.id, **{k: getattr(row, k) for k in cols}))
        CR = d['ContentRelease']
        for r in CR.query.filter_by(section_id=src.id, user_id=None).all():
            cols = [c.key for c in inspect(CR).column_attrs if c.key not in ('id', 'section_id')]
            db.session.add(CR(section_id=new.id, **{k: getattr(r, k) for k in cols}))
        db.session.commit()
        join_code(new, fresh=True)
        d['audit']('section_clone', f'section {src.id} → {new.id}')
        return new

    def _user_by(ident):
        ident = (ident or '').strip().lower()
        return User.query.filter(db.func.lower(User.email) == ident).first() if ident else None

    def import_csv(section, raw, actor):
        """CSV columns: username/email, full_name, role (student | ta | observer | lead). Creates missing accounts."""
        made = enrolled = staffed = 0
        errors = []
        for i, row in enumerate(csv.reader(io.StringIO(raw)), 1):
            if not row or not row[0].strip() or row[0].strip().lower() in ('email', 'username', 'username/email'):
                continue
            email = row[0].strip().lower()
            name = (row[1] if len(row) > 1 else '').strip()
            role = ((row[2] if len(row) > 2 else '') or 'student').strip().lower()
            if '@' not in email or role not in ('student', *ROLES):
                errors.append(f'Line {i}: need an email and a role of student, ta, observer or lead.')
                continue
            u = _user_by(email)
            if u is None:
                first, _, last = (name or email.split('@')[0]).partition(' ')
                u = User(email=email, first_name=first[:80] or 'Student', last_name=last[:80] or '-',
                         role='student' if role == 'student' else 'instructor',
                         institution_id=getattr(section, 'institution_id', None))
                u.set_password(secrets.token_urlsafe(16))
                db.session.add(u)
                db.session.flush()
                made += 1
            if role == 'student':
                if not Enrollment.query.filter_by(user_id=u.id, section_id=section.id).first():
                    db.session.add(Enrollment(user_id=u.id, section_id=section.id))
                    enrolled += 1
            elif u.role in ('instructor', 'admin'):
                set_staff(section, u, role, actor, commit=False)
                staffed += 1
            else:
                errors.append(f'Line {i}: {email} is a student account and cannot be class staff.')
        db.session.commit()
        d['audit']('roster_import', f'section {section.id}: {made} new accounts, {enrolled} enrolled, {staffed} staff')
        return made, enrolled, staffed, errors

    def set_staff(section, user, role, actor, commit=True):
        row = SectionStaff.query.filter_by(section_id=section.id, user_id=user.id).first()
        if role is None:
            if row:
                db.session.delete(row)
        elif row:
            row.role = role
        else:
            db.session.add(SectionStaff(section_id=section.id, user_id=user.id, role=role, added_by=actor.id))
        if commit:
            db.session.commit()
            d['audit']('permission_change', f'section {section.id}: {user.email} → {role or "removed"}')

    def students_of(section):
        return (User.query.join(Enrollment, Enrollment.user_id == User.id)
                .filter(Enrollment.section_id == section.id, User.role == 'student').order_by(User.last_name).all())

    _stats_cache = {}

    def section_stats(section, deadline=None):
        """Hub comparison row: cheap ladder counts from the state table; mastery % via the engine, cached for 2 minutes."""
        LS = app.extensions['ciwt_mastery'].ladder.models.LadderState
        uids = [u.id for u in students_of(section)]
        struggles = resolved = exhausted = 0
        for r in LS.query.filter(LS.section_id == section.id, LS.user_id.in_(uids or [0])).all():
            if (r.misses or 0) or (r.requests or 0) or (r.tried_json or '').count('R') > 1:
                struggles += 1
                resolved += 1 if r.resolved else 0
                exhausted += 1 if (r.exhausted_at and not r.resolved) else 0
        hit = _stats_cache.get(section.id)
        stale = not hit or (utcnow() - hit[0]).total_seconds() > 600
        if stale and deadline and _time.monotonic() > deadline:   # page budget used: show cached or "pending"
            hit = hit or (utcnow(), 'pending')
        elif stale:
            eng = app.extensions['ciwt_mastery'].engine
            pairs = mastered = 0
            for uid in uids:
                try:
                    st = eng.student_state(section, db.session.get(User, uid), log=False)
                except Exception:
                    db.session.rollback()
                    continue
                for obj, est in st['states'].items():
                    if st['evidence'].get(obj):
                        pairs += 1
                        mastered += est.get('status') == 'mastered'
            hit = _stats_cache[section.id] = (utcnow(), round(100 * mastered / pairs) if pairs else None)
        return {'section': section, 'students': len(uids), 'mastery': hit[1],
                'resolved': round(100 * resolved / struggles) if struggles else None,
                'struggles': struggles - resolved, 'exhausted': exhausted}

    @login_required
    def sections_hub():
        if current_user.role not in ('instructor', 'admin'):
            abort(403)
        secs = my_sections(current_user)
        by_course = {}
        deadline = _time.monotonic() + 0.8      # mastery % is the costly column; fill the rest on the next visit
        for s in secs:
            by_course.setdefault(s.course_id, []).append(section_stats(s, deadline))
        courses = {c.id: c for c in d['Course'].query.filter(d['Course'].id.in_(list(by_course) or [0])).all()}
        roles = {s.id: staff_role(current_user, s) for s in secs}
        return render_template('school/hub.html', groups=[(courses.get(c), rows) for c, rows in by_course.items()],
                               roles=roles, ROLES=ROLES)

    @login_required
    def section_clone(section_id):
        src, _ = section_or_403(section_id, 'lead')
        new = clone_section(src, current_user)
        flash(f'Created “{new.name}” with the same settings and an empty roster. Join code: {join_code(new)}.', 'success')
        return redirect(url_for('section_roster', section_id=new.id), code=303)

    @login_required
    def section_roster(section_id):
        sec, role = section_or_403(section_id)
        if request.method == 'POST':
            if role != 'lead':
                abort(403)
            f, act = request.form, request.form.get('action')
            if act == 'import':
                up = request.files.get('file')
                raw = (up.read().decode('utf-8-sig', 'replace') if up and up.filename else '') or f.get('csv', '')
                made, enr, st, errs = import_csv(sec, raw, current_user)
                flash(f'Imported: {enr} enrolled, {st} staff, {made} new accounts.' + (' ' + ' '.join(errs[:5]) if errs else ''),
                      'warning' if errs else 'success')
            elif act in ('drop', 'transfer'):
                e = Enrollment.query.filter_by(section_id=sec.id, user_id=f.get('user_id', type=int)).first_or_404()
                if act == 'drop':
                    db.session.delete(e)
                    d['audit']('roster_drop', f'section {sec.id}: user {e.user_id}')
                    flash('Student dropped from this class. Their records are kept.', 'success')
                else:
                    to = db.get_or_404(ClassSection, f.get('to', type=int))
                    if to.course_id != sec.course_id or staff_role(current_user, to) != 'lead':
                        abort(400)
                    if Enrollment.query.filter_by(section_id=to.id, user_id=e.user_id).first():
                        db.session.delete(e)
                    else:
                        e.section_id = to.id
                    d['audit']('roster_transfer', f'user {e.user_id}: section {sec.id} → {to.id}')
                    flash(f'Student moved to {to.name}.', 'success')
                db.session.commit()
            elif act == 'regen':
                join_code(sec, fresh=True)
                d['audit']('join_code_regen', f'section {sec.id}')
                flash('New join code created; the old one no longer works.', 'success')
            elif act == 'staff':
                u = _user_by(f.get('email'))
                r = f.get('role') if f.get('role') in ROLES else None
                if not u or u.role not in ('instructor', 'admin') or u.id == sec.instructor_id:
                    flash('Staff must be an existing instructor account (not the class owner).', 'warning')
                else:
                    set_staff(sec, u, r, current_user)
                    flash('Staff updated.', 'success')
            return redirect(url_for('section_roster', section_id=sec.id), code=303)
        siblings = [s for s in my_sections(current_user) if s.course_id == sec.course_id and s.id != sec.id]
        staff = [(r, db.session.get(User, r.user_id)) for r in SectionStaff.query.filter_by(section_id=sec.id).all()]
        return render_template('school/roster.html', section=sec, role=role, students=students_of(sec), siblings=siblings,
                               staff=staff, code=join_code(sec), ROLES=ROLES)

    @login_required
    def join_section():
        if request.method == 'POST':
            row = SectionJoinCode.query.filter_by(code=(request.form.get('code') or '').strip().upper()).first()
            sec = db.session.get(ClassSection, row.section_id) if row else None
            if not sec or current_user.role != 'student' or not d['same_tenant'](current_user, sec):
                flash('That join code is not valid.', 'warning')
                return redirect(url_for('join_section'))
            if not Enrollment.query.filter_by(user_id=current_user.id, section_id=sec.id).first():
                db.session.add(Enrollment(user_id=current_user.id, section_id=sec.id))
                db.session.commit()
                d['audit']('roster_join', f'section {sec.id} by code')
            flash(f'You joined {sec.name}.', 'success')
            return redirect(url_for('student_dashboard'))
        return render_template('school/join.html')

    # ------------------------------------------------------------------ FERPA
    def _user_tables():
        for t in db.metadata.sorted_tables:
            if 'user_id' in t.c and t.name not in ('user',):
                yield t

    def record_of(user):
        """Everything stored about one person, table by table (secrets removed)."""
        out = {'generated_at': utcnow().isoformat() + 'Z', 'notice': 'Your education record export (FERPA).',
               'profile': {k: getattr(user, k, None) for k in ('id', 'email', 'first_name', 'last_name', 'role', 'created_at')}}
        tables = {}
        with db.engine.connect() as conn:
            for t in _user_tables():
                cols = [c for c in t.c if not any(s in c.name.lower() for s in SECRET)]
                rows = conn.execute(t.select().with_only_columns(*cols).where(t.c.user_id == user.id)).mappings().all()
                if rows:
                    tables[t.name] = [dict(r) for r in rows]
        out['tables'] = tables
        return out

    def export_response(user, fmt):
        rec = record_of(user)
        d['audit']('ferpa_export', f'user {user.id} ({fmt})')
        body = json.dumps(rec, default=str, indent=1)
        if fmt != 'zip':
            return Response(body, mimetype='application/json',
                            headers={'Content-Disposition': f'attachment; filename=record-{user.id}.json'})
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('record.json', body)
            for name, rows in rec['tables'].items():
                s = io.StringIO()
                w = csv.DictWriter(s, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
                z.writestr(f'{name}.csv', s.getvalue())
        return Response(buf.getvalue(), mimetype='application/zip',
                        headers={'Content-Disposition': f'attachment; filename=record-{user.id}.zip'})

    def anonymize(user, actor, delete=False):
        """De-identify the account; with delete=True also remove activity rows. The audit trail is kept."""
        n = 0
        if delete:
            with db.engine.begin() as conn:
                for t in reversed(list(_user_tables())):
                    if t.name not in KEEP_ON_DELETE:
                        n += conn.execute(t.delete().where(t.c.user_id == user.id)).rowcount or 0
        user.first_name, user.last_name = 'Removed', f'Student {user.id}'
        user.email = f'removed-{user.id}@anonymized.invalid'
        user.set_password(secrets.token_urlsafe(24))
        db.session.commit()
        d['audit']('ferpa_delete' if delete else 'ferpa_anonymize', f'user {user.id} by {actor.id}: {n} rows removed')
        return n

    @login_required
    def my_data():
        fmt = request.args.get('format')
        if fmt in ('json', 'zip'):
            return export_response(current_user, fmt)
        if request.method == 'POST':
            kind = request.form.get('kind')
            if kind not in ('export', 'correct', 'delete'):
                abort(400)
            db.session.add(DataRequest(user_id=current_user.id, kind=kind, note=(request.form.get('note') or '')[:1000],
                                       created_by=current_user.id))
            db.session.commit()
            d['audit']('ferpa_request', f'{kind} by user {current_user.id}')
            flash('Request sent to your school’s records administrator.', 'success')
            return redirect(url_for('my_data'), code=303)
        reqs = DataRequest.query.filter_by(user_id=current_user.id).order_by(DataRequest.id.desc()).all()
        return render_template('school/my_data.html', reqs=reqs)

    def _admin():
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)

    @login_required
    def admin_ferpa():
        _admin()
        f = request.form
        if request.args.get('user_id') and request.args.get('format') in ('json', 'zip'):
            u = db.get_or_404(User, request.args.get('user_id', type=int))
            if not d['same_tenant'](current_user, u):
                abort(404)
            return export_response(u, request.args['format'])
        if request.method == 'POST':
            r = db.get_or_404(DataRequest, f.get('request_id', type=int))
            u = db.session.get(User, r.user_id)
            if not u or not d['same_tenant'](current_user, u):
                abort(404)
            act = f.get('action')
            if act in ('anonymize', 'delete'):
                if f.get('confirm') != u.email:
                    flash('Type the student’s email exactly to confirm.', 'warning')
                    return redirect(url_for('admin_ferpa'), code=303)
                n = anonymize(u, current_user, delete=act == 'delete')
                r.outcome = f'{act}d ({n} activity rows removed)'
            else:
                r.outcome = (f.get('outcome') or act or '')[:400]
            r.status = 'denied' if act == 'deny' else 'done'
            r.handled_by, r.handled_at = current_user.id, utcnow()
            db.session.commit()
            d['audit']('ferpa_request_handled', f'request {r.id}: {r.status} {r.outcome}')
            flash('Request updated.', 'success')
            return redirect(url_for('admin_ferpa'), code=303)
        rows = [(r, db.session.get(User, r.user_id)) for r in DataRequest.query.order_by(DataRequest.status != 'open',
                                                                                         DataRequest.id.desc()).limit(200)]
        rows = [(r, u) for r, u in rows if u and d['same_tenant'](current_user, u)]
        return render_template('school/ferpa.html', rows=rows, chain=verify_chain(), admin_tab='admin_ferpa')

    @login_required
    def section_privacy(section_id):
        sec, role = section_or_403(section_id, 'lead')
        if request.args.get('user_id') and request.args.get('format') in ('json', 'zip'):
            u = db.get_or_404(User, request.args.get('user_id', type=int))
            if not Enrollment.query.filter_by(section_id=sec.id, user_id=u.id).first():
                abort(404)
            return export_response(u, request.args['format'])
        if request.method == 'POST':
            u = db.get_or_404(User, request.form.get('user_id', type=int))
            kind = request.form.get('kind')
            if kind not in ('export', 'correct', 'delete') or not Enrollment.query.filter_by(section_id=sec.id, user_id=u.id).first():
                abort(400)
            db.session.add(DataRequest(user_id=u.id, kind=kind, created_by=current_user.id,
                                       note=f'Filed by instructor for {sec.name}. ' + (request.form.get('note') or '')[:800]))
            db.session.commit()
            d['audit']('ferpa_request', f'{kind} for user {u.id} filed by staff')
            flash('Request filed with the records administrator.', 'success')
            return redirect(url_for('section_privacy', section_id=sec.id), code=303)
        uids = [u.id for u in students_of(sec)]
        reqs = DataRequest.query.filter(DataRequest.user_id.in_(uids or [0])).order_by(DataRequest.id.desc()).limit(50).all()
        return render_template('school/privacy.html', section=sec, students=students_of(sec), reqs=reqs)

    @login_required
    def admin_audit_log():
        _admin()
        q = AuditEvent.query
        a = request.args
        if a.get('action'):
            q = q.filter(AuditEvent.action.like(f"%{a['action']}%"))
        if a.get('user_id', type=int):
            q = q.filter(AuditEvent.user_id == a.get('user_id', type=int))
        if a.get('section_id', type=int):
            q = q.filter(AuditEvent.section_id == a.get('section_id', type=int))
        for k, op in (('since', '__ge__'), ('until', '__le__')):
            if a.get(k):
                try:
                    q = q.filter(getattr(AuditEvent.created_at, op)(datetime.fromisoformat(a[k])))
                except ValueError:
                    pass
        rows = q.order_by(AuditEvent.id.desc()).limit(5000 if a.get('format') == 'csv' else 300).all()
        if a.get('format') == 'csv':
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(['id', 'utc', 'actor_id', 'role', 'action', 'detail', 'path', 'ip', 'section_id', 'prev_hash', 'hash'])
            for e in rows:
                w.writerow([e.id, e.created_at, e.user_id, e.role, e.action, e.detail, e.path, e.ip, e.section_id, e.prev_hash, e.hash])
            d['audit']('audit_export', f'{len(rows)} rows')
            return Response(buf.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=audit-log.csv'})
        return render_template('school/audit_log.html', rows=rows, chain=verify_chain(), f=a, admin_tab='admin_audit_log')

    # ------------------------------------------------------------------ accessibility + setup
    def accessibility():
        return render_template('school/accessibility.html')

    @login_required
    def section_setup(section_id):
        sec, role = section_or_403(section_id)
        chk = d['setup_checklist'](sec, current_user) or {'items': []}
        base = {i['key']: i for i in chk['items']}
        lad = app.extensions['ciwt_mastery'].ladder.settings(sec.id)
        lti = app.extensions['ciwt_lti']
        lcfg = lti.section_setting(sec.id)
        n_staff = SectionStaff.query.filter_by(section_id=sec.id).count()
        n_stu = len(students_of(sec))
        linked = lti.models.LtiContext.query.filter_by(section_id=sec.id).count()
        areas = [
            ('roster', 'Roster & multi-section', f'{n_stu} students · join code {join_code(sec)}', n_stu > 0,
             url_for('section_roster', section_id=sec.id), 'Manage roster'),
            ('adaptive', 'Adaptive path & comprehension gate',
             (base.get('adaptivity', {}).get('state', '') + ' · gate ' + ('on' if lad.get('require_check') else 'off')).strip(' ·'),
             True, url_for('mastery_class', section_id=sec.id), 'Mastery settings'),
            ('ladder', 'Explanation ladder', ('On' if lad['enabled'] else 'Off') + f" · up to {lad.get('max_rung', 4)} explanations",
             lad['enabled'], url_for('ladder_class', section_id=sec.id), 'Ladder settings'),
            ('helix', 'Helix attention policy', base.get('helix', {}).get('state', 'Opt-in, never graded'), True,
             url_for('helix.instructor_attention', section_id=sec.id), 'Attention settings'),
            ('staff', 'Staff roles', f'{n_staff} TA/observer/co-lead' + ('' if n_staff == 1 else 's'), True,
             url_for('section_roster', section_id=sec.id) + '#staff', 'Staff roles'),
            ('lti', 'LTI 1.3 (optional)', ('Connected' if linked else 'Not connected') +
             f" · auto-passback {'on' if lcfg.auto_passback else 'off'}", True,
             url_for('instructor_lti', section_id=sec.id), 'LMS connection'),
            ('a11y', 'Accessibility & FERPA', 'WCAG 2.1 AA statement · student export/delete requests', True,
             url_for('section_privacy', section_id=sec.id), 'Privacy tools'),
        ]
        return render_template('school/setup.html', section=sec, role=role, areas=areas, ROLES=ROLES)

    for rule, ep, fn, methods in [
        ('/instructor/sections', 'sections_hub', sections_hub, ['GET']),
        ('/instructor/section/<int:section_id>/clone', 'section_clone', section_clone, ['POST']),
        ('/instructor/section/<int:section_id>/roster', 'section_roster', section_roster, ['GET', 'POST']),
        ('/instructor/section/<int:section_id>/privacy', 'section_privacy', section_privacy, ['GET', 'POST']),
        ('/instructor/section/<int:section_id>/setup', 'section_setup', section_setup, ['GET']),
        ('/join', 'join_section', join_section, ['GET', 'POST']),
        ('/my-data', 'my_data', my_data, ['GET', 'POST']),
        ('/admin/ferpa', 'admin_ferpa', admin_ferpa, ['GET', 'POST']),
        ('/admin/audit-log', 'admin_audit_log', admin_audit_log, ['GET']),
        ('/accessibility', 'accessibility', accessibility, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)

    from types import SimpleNamespace
    api = SimpleNamespace(SectionStaff=SectionStaff, SectionJoinCode=SectionJoinCode, DataRequest=DataRequest,
                          ensure_schema=ensure_schema, staff_role=staff_role, can_manage_section=can_manage_section,
                          can_edit_grades=can_edit_grades, can_edit_settings=can_edit_settings, join_code=join_code,
                          clone_section=clone_section, record_of=record_of, anonymize=anonymize, verify_chain=verify_chain)
    app.extensions['ciwt_school'] = api
    return api
