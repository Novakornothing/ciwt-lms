"""Course materials in the LMS (pass 8).

Instructors: /instructor/materials — syllabus, pacing, lesson plans, lab manual, rubrics, blueprints and
answer keys per course, viewable/printable and downloadable as DOCX or PDF; per-section syllabus fields
(institution, term, meeting times, policies) at /instructor/section/<id>/syllabus.
Students: /section/<id>/materials/<doc> for the student-safe documents (syllabus, pacing, rubrics, glossary)
of a section they are enrolled in. Answer keys, blueprints and lesson plans are instructor-only.
"""
import json
import re
from datetime import datetime, timezone

from flask import abort, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from curriculum_v2 import course_package as CP
from curriculum_v2 import documents as D

CODE_ALIASES = {'ITSUP': 'ITSUP', 'APLUS': 'ITSUP', 'NETOPS': 'NETOPS', 'NETPLUS': 'NETOPS', 'CLIENT': 'CLIENT'}
FIELD_KEYS = [k for k, _l, _p in CP.SECTION_FIELDS] + [k for k, _l, _p in CP.POLICY_FIELDS]
MAX_FIELD = 4000


def package_code(course):
    return CODE_ALIASES.get((getattr(course, 'code', '') or '').upper())


def _slug(text):
    return re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')[:60] or 'document'


def register(app, db, deps):
    """deps: Course, ClassSection, Enrollment, instructor_can_access_section, instructor_course_ids, audit."""
    Course, ClassSection, Enrollment = deps['Course'], deps['ClassSection'], deps['Enrollment']
    can_access = deps['instructor_can_access_section']
    course_ids_for = deps['instructor_course_ids']
    audit = deps.get('audit') or (lambda *a, **k: None)

    class SyllabusSettings(db.Model):
        __tablename__ = 'syllabus_settings'
        id = db.Column(db.Integer, primary_key=True)
        section_id = db.Column(db.Integer, db.ForeignKey('class_section.id'), unique=True, nullable=False, index=True)
        fields = db.Column(db.Text)           # JSON {key: value} for SECTION_FIELDS + POLICY_FIELDS
        pacing_weeks = db.Column(db.Integer)  # 16, 8 or 10; NULL = course default
        updated_at = db.Column(db.DateTime)
        updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def is_staff():
        return current_user.is_authenticated and current_user.role in ('instructor', 'admin')

    def section_fields(section):
        row = SyllabusSettings.query.filter_by(section_id=section.id).first() if section else None
        data = {}
        if row and row.fields:
            try:
                data = {k: v for k, v in json.loads(row.fields).items() if k in FIELD_KEYS and isinstance(v, str)}
            except ValueError:
                data = {}
        if section is not None:
            data.setdefault('course_number', '')
            if row and row.pacing_weeks:
                data['pacing_weeks'] = str(row.pacing_weeks)
        return data, row

    def gb_settings(section):
        gb = app.extensions.get('ciwt_gradebook')
        if not gb or not section:
            return None
        s = gb.models.GradebookSetting.query.filter_by(section_id=section.id).first()
        return s

    def staff_courses():
        if current_user.role == 'admin':
            courses = Course.query.order_by(Course.title).all()
        else:
            ids = set(course_ids_for(current_user.id) or [])
            ids |= {s.course_id for s in ClassSection.query.filter_by(instructor_id=current_user.id).all()}
            courses = Course.query.filter(Course.id.in_(ids or [0])).order_by(Course.title).all()
        return [c for c in courses if package_code(c)]

    def staff_sections(course):
        q = ClassSection.query.filter_by(course_id=course.id, is_active=True).order_by(ClassSection.name)
        return [s for s in q.all() if can_access(current_user, s)]

    def course_for_code(code):
        for c in staff_courses():
            if package_code(c) == code:
                return c
        return None

    def resolve_section(code):
        sid = request.args.get('section', type=int)
        if not sid:
            return None
        s = db.session.get(ClassSection, sid)
        if not s or package_code(s.course) != code or not can_access(current_user, s):
            abort(404)
        return s

    def build(kind, code, section):
        fields, _row = section_fields(section)
        return D.build(kind, code, fields if section else None, gb_settings(section))

    def send(doc, fmt, filename):
        try:
            if fmt == 'docx':
                body, mime = D.to_docx(doc), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                body, mime = D.to_pdf(doc), 'application/pdf'
        except ImportError:
            # python-docx / reportlab missing (older install): the HTML view still works and prints to PDF
            flash('DOCX/PDF export needs python-docx and reportlab (pip install -r requirements.txt). '
                  'Use Print on this page meanwhile.', 'warning')
            return redirect(request.path.rsplit('.', 1)[0] + (('?' + request.query_string.decode()) if request.query_string else ''))
        resp = make_response(body)
        resp.headers['Content-Type'] = mime
        resp.headers['Content-Disposition'] = f'attachment; filename="{filename}.{fmt}"'
        resp.headers['Cache-Control'] = 'private, no-store'
        return resp

    # ------------------------------------------------------------------------------ instructor
    @login_required
    def materials_index():
        if not is_staff():
            abort(403)
        rows = []
        for c in staff_courses():
            rows.append({'course': c, 'code': package_code(c), 'sections': staff_sections(c)})
        return render_template('materials_index.html', rows=rows, docs=D.DOCS, disclaimer=CP.DISCLAIMER)

    @login_required
    def materials_view(code, kind):
        if not is_staff():
            abort(403)
        code = CODE_ALIASES.get(code.upper())
        if not code or kind not in D.BUILDERS or not course_for_code(code):
            abort(404)
        section = resolve_section(code)
        doc = build(kind, code, section)
        audit('materials_view', f'{code}/{kind}')
        return render_template('materials_view.html', doc=doc, code=code, kind=kind, section=section,
                               instructor_only=kind not in D.STUDENT_DOCS, staff=True,
                               download=lambda fmt: url_for('materials_download', code=code, kind=kind, fmt=fmt,
                                                            **({'section': section.id} if section else {})))

    @login_required
    def materials_download(code, kind, fmt):
        if not is_staff():
            abort(403)
        code = CODE_ALIASES.get(code.upper())
        if not code or kind not in D.BUILDERS or fmt not in ('docx', 'pdf') or not course_for_code(code):
            abort(404)
        section = resolve_section(code)
        doc = build(kind, code, section)
        audit('materials_download', f'{code}/{kind}.{fmt}')
        return send(doc, fmt, f'{_slug(CP.COURSES[code]["title"])}-{kind}')

    @login_required
    def syllabus_settings(section_id):
        section = db.get_or_404(ClassSection, section_id)
        if not is_staff() or not can_access(current_user, section):
            abort(403)
        code = package_code(section.course)
        if not code:
            abort(404)
        fields, row = section_fields(section)
        if request.method == 'POST':
            data = {}
            for k in FIELD_KEYS:
                v = (request.form.get(k) or '').strip()
                if v:
                    data[k] = v[:MAX_FIELD]
            weeks = request.form.get('pacing_weeks', type=int)
            if row is None:
                row = SyllabusSettings(section_id=section.id)
                db.session.add(row)
            row.fields = json.dumps(data)
            row.pacing_weeks = weeks if weeks in (16, 8, 10) else None
            row.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            row.updated_by = current_user.id
            db.session.commit()
            audit('syllabus_settings', f'section {section.id}')
            flash('Syllabus details saved.', 'success')
            return redirect(url_for('syllabus_settings', section_id=section.id))
        return render_template('syllabus_settings.html', section=section, code=code, fields=fields,
                               section_fields=CP.SECTION_FIELDS, policy_fields=CP.POLICY_FIELDS, row=row,
                               weeks=int(fields.get('pacing_weeks') or (8 if code == 'CLIENT' else 16)))

    # ------------------------------------------------------------------------------ students
    def student_section_or_404(section_id):
        section = db.get_or_404(ClassSection, section_id)
        if is_staff():
            if not can_access(current_user, section):
                abort(403)
        elif not Enrollment.query.filter_by(user_id=current_user.id, section_id=section.id).first():
            abort(403)
        code = package_code(section.course)
        if not code:
            abort(404)
        return section, code

    @login_required
    def section_material(section_id, kind):
        section, code = student_section_or_404(section_id)
        if kind not in D.STUDENT_DOCS:
            abort(404)
        doc = build(kind, code, section)
        return render_template('materials_view.html', doc=doc, code=code, kind=kind, section=section,
                               instructor_only=False, staff=is_staff(),
                               student_docs=[(k, t) for k, t, a in D.DOCS if a == 'all'],
                               download=lambda fmt: url_for('section_material_download', section_id=section.id,
                                                            kind=kind, fmt=fmt))

    @login_required
    def section_material_download(section_id, kind, fmt):
        section, code = student_section_or_404(section_id)
        if kind not in D.STUDENT_DOCS or fmt not in ('docx', 'pdf'):
            abort(404)
        return send(build(kind, code, section), fmt, f'{_slug(CP.COURSES[code]["title"])}-{kind}')

    for rule, ep, fn, methods in [
        ('/instructor/materials', 'materials_index', materials_index, ['GET']),
        ('/instructor/materials/<code>/<kind>', 'materials_view', materials_view, ['GET']),
        ('/instructor/materials/<code>/<kind>.<fmt>', 'materials_download', materials_download, ['GET']),
        ('/instructor/section/<int:section_id>/syllabus', 'syllabus_settings', syllabus_settings, ['GET', 'POST']),
        ('/section/<int:section_id>/materials/<kind>', 'section_material', section_material, ['GET']),
        ('/section/<int:section_id>/materials/<kind>.<fmt>', 'section_material_download', section_material_download, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)

    @app.context_processor
    def _materials_ctx():
        def lab_assessment(lab):
            """Standard-format summary shown with a lab before students start it."""
            if not lab or not lab.get('id'):
                return None
            f = CP.standard_lab(lab)
            r = CP.RUBRICS['lab']
            return {'reflection': f['reflection'], 'low_cost': f['low_cost'], 'minutes': f['minutes'],
                    'rubric': r, 'proficient': [(name, levels[1]) for name, levels in r['criteria']]}
        return {'lab_assessment': lab_assessment}

    app.extensions['ciwt_materials'] = {'SyllabusSettings': SyllabusSettings, 'package_code': package_code}
    return SyllabusSettings
