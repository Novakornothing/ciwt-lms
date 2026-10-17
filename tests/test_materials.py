"""Pass 8: course materials (instructor) and section syllabus/rubrics (students): access control,
exports, per-section syllabus fields and gradebook-linked grading."""
import pytest

DOCS = ['syllabus', 'pacing', 'lesson-plans', 'lab-manual', 'rubrics', 'blueprints', 'answer-key', 'glossary']
STAFF_ONLY = ['lesson-plans', 'lab-manual', 'blueprints', 'answer-key']


def _code(app, mod, section_id):
    from curriculum_v2.materials import package_code
    with app.app_context():
        return package_code(mod.db.session.get(mod.ClassSection, section_id).course)


def test_anonymous_is_sent_to_login(anon):
    r = anon.get('/instructor/materials')
    assert r.status_code in (302, 401)


@pytest.mark.parametrize('path', ['/instructor/materials', '/instructor/materials/ITSUP/answer-key',
                                  '/instructor/materials/ITSUP/answer-key.pdf', '/instructor/materials/NETOPS/blueprints.docx'])
def test_students_cannot_open_instructor_materials(student, path):
    assert student.get(path).status_code == 403


def test_instructor_index_lists_documents(instructor):
    body = instructor.get('/instructor/materials').get_data(as_text=True)
    assert 'Course materials' in body and 'Answer keys with rationales' in body and 'Instructors only' in body


@pytest.mark.parametrize('kind', DOCS)
def test_instructor_views_and_downloads_every_document(admin, kind):
    r = admin.get(f'/instructor/materials/ITSUP/{kind}')
    assert r.status_code == 200, kind
    docx = admin.get(f'/instructor/materials/ITSUP/{kind}.docx')
    assert docx.status_code == 200 and docx.data[:2] == b'PK'
    assert 'wordprocessingml' in docx.headers['Content-Type']
    pdf = admin.get(f'/instructor/materials/NETOPS/{kind}.pdf')
    assert pdf.status_code == 200 and pdf.data[:4] == b'%PDF'
    assert pdf.headers['Cache-Control'].startswith('private')


def test_unknown_document_or_format_is_404(admin):
    assert admin.get('/instructor/materials/ITSUP/secrets').status_code == 404
    assert admin.get('/instructor/materials/ITSUP/syllabus.exe').status_code == 404
    assert admin.get('/instructor/materials/NOPE/syllabus').status_code == 404


def test_answer_key_shows_rationales_to_staff(admin):
    body = admin.get('/instructor/materials/ITSUP/answer-key').get_data(as_text=True)
    assert 'Rationale' in body and 'Instructor-only document' in body


def test_enrolled_student_sees_section_syllabus_and_rubrics(student, app, mod, ids):
    sid = ids['section']
    r = student.get(f'/section/{sid}/materials/syllabus')
    body = r.get_data(as_text=True)
    assert r.status_code == 200 and 'Course learning outcomes' in body and 'Grading' in body
    assert 'Rationale' not in body
    assert student.get(f'/section/{sid}/materials/rubrics').status_code == 200
    pdf = student.get(f'/section/{sid}/materials/syllabus.pdf')
    assert pdf.status_code == 200 and pdf.data[:4] == b'%PDF'


@pytest.mark.parametrize('kind', STAFF_ONLY)
def test_student_cannot_reach_instructor_documents_through_section(student, ids, kind):
    assert student.get(f"/section/{ids['section']}/materials/{kind}").status_code == 404
    assert student.get(f"/section/{ids['section']}/materials/{kind}.pdf").status_code == 404


def test_student_outside_section_is_refused(outsider, ids):
    assert outsider.get(f"/section/{ids['section']}/materials/syllabus").status_code == 403


def test_student_class_page_links_syllabus(student, ids):
    body = student.get(f"/student/section/{ids['section']}").get_data(as_text=True)
    assert f"/section/{ids['section']}/materials/syllabus" in body


def test_section_syllabus_fields_round_trip_and_escape(instructor, student, app, mod, ids):
    sid = ids['section']
    assert instructor.get(f'/instructor/section/{sid}/syllabus').status_code == 200
    r = instructor.post(f'/instructor/section/{sid}/syllabus', data={
        'institution': 'Example Community College', 'term': 'Spring 2027',
        'ai_use': 'AI tools allowed for practice <script>alert(1)</script>', 'pacing_weeks': '10', 'bogus': 'x'})
    assert r.status_code in (302, 303)
    try:
        body = student.get(f'/section/{sid}/materials/syllabus').get_data(as_text=True)
        assert 'Example Community College' in body and 'Spring 2027' in body
        assert '<script>alert(1)</script>' not in body and '&lt;script&gt;' in body
        assert '10-week schedule' in body
        assert '[Meeting' in body or '[Days, times' in body   # unfilled fields keep their placeholder
    finally:
        with app.app_context():
            SyllabusSettings = app.extensions['ciwt_materials']['SyllabusSettings']
            SyllabusSettings.query.filter_by(section_id=sid).delete()
            mod.db.session.commit()


def test_students_cannot_edit_syllabus(student, ids):
    assert student.get(f"/instructor/section/{ids['section']}/syllabus").status_code == 403
    assert student.post(f"/instructor/section/{ids['section']}/syllabus", data={'term': 'x'}).status_code == 403


def test_instructor_without_access_cannot_edit_other_section(instructor2, app, mod, ids):
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, ids['section'])
        allowed = mod.instructor_can_access_section(mod.User.query.filter_by(email='instructor2@lms.local').first(), sec)
    if allowed:
        pytest.skip('instructor2 shares this course in the seed data')
    assert instructor2.post(f"/instructor/section/{ids['section']}/syllabus", data={'term': 'x'}).status_code == 403
    assert instructor2.get(f"/instructor/materials/{_code(app, mod, ids['section'])}/syllabus?section={ids['section']}").status_code in (403, 404)


def test_syllabus_grading_follows_section_gradebook(admin, app, mod, ids):
    sid = ids['section']
    gb = app.extensions['ciwt_gradebook'].models.GradebookSetting
    with app.app_context():
        existing = gb.query.filter_by(section_id=sid).first()
        saved = (existing.weight_tests, existing.weight_skills, existing.weight_quizzes, existing.pass_mark) if existing else None
        row = existing or gb(section_id=sid)
        row.weight_tests, row.weight_skills, row.weight_quizzes, row.pass_mark = 55, 35, 10, 75
        mod.db.session.add(row)
        mod.db.session.commit()
    try:
        code = _code(app, mod, sid)
        body = admin.get(f'/instructor/materials/{code}/syllabus?section={sid}').get_data(as_text=True)
        assert '55%' in body and '35%' in body and '10%' in body and 'Pass mark: 75%' in body
    finally:
        with app.app_context():
            row = gb.query.filter_by(section_id=sid).first()
            if saved:
                row.weight_tests, row.weight_skills, row.weight_quizzes, row.pass_mark = saved
            else:
                mod.db.session.delete(row)
            mod.db.session.commit()


def test_lab_pages_show_rubric_before_starting(student):
    for lab in ('win-ipconfig', 'gui-about', 'sw-vlan-access'):
        body = student.get(f'/labs/{lab}').get_data(as_text=True)
        assert 'How this lab is assessed' in body and 'Reflection questions' in body, lab


def test_staff_rail_links_course_materials(instructor):
    assert '/instructor/materials' in instructor.get('/instructor').get_data(as_text=True)


def test_instructor_notes_hidden_from_students_shown_to_staff(app, mod):
    with app.test_request_context():
        from flask_login import login_user, logout_user
        html = '<p>Lesson</p><div class="instructor-note"><h4>Instructor — 50 minutes</h4><p>Pace.</p></div><p>More</p>'
        stu = mod.User.query.filter_by(email='student1@lms.local').first()
        ins = mod.User.query.filter_by(email='instructor@lms.local').first()
        login_user(stu)
        out = mod.render_lesson_filter(html)
        assert 'Instructor — 50 minutes' not in out and '<p>More</p>' in out
        logout_user()
        login_user(ins)
        assert 'Instructor — 50 minutes' in mod.render_lesson_filter(html)


def test_student_lesson_page_has_no_instructor_note(student, ids):
    body = student.get(f"/student/module/{ids['section']}/{ids['module']}", follow_redirects=True).get_data(as_text=True)
    assert 'class="instructor-note"' not in body


def test_placeholder_helper():
    from curriculum_v2 import documents as D
    assert D.has_placeholders({'blocks': [('p', 'Room [TBD]')]})
    assert not D.has_placeholders({'blocks': [('table', ['A', 'B'], [['x', 'y']])]})
