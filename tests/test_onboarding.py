"""Pass 13: first-run experience — instructor "Set up your class" checklist and the one-time student intro."""
import re


def _section_for(mod, email):
    u = mod.User.query.filter_by(email=email).first()
    enr = mod.Enrollment.query.filter_by(user_id=u.id).first()
    return u, enr.section_id


def test_instructor_checklist_lists_every_setting_and_can_be_reviewed_and_hidden(app, mod, instructor):
    with app.app_context():
        sec = mod.ClassSection.query.filter_by(instructor_id=mod.User.query.filter_by(email='instructor@lms.local').first().id).first()
        sid = sec.id
        mod.onboarding_api['Flag'].query.filter_by(section_id=sid).delete()
        mod.db.session.commit()
    h = instructor.get(f'/instructor/section/{sid}').get_data(as_text=True)
    assert 'Set up your class' in h
    for title in ('Adaptive path', 'Helix attention policy', 'Certification practice items', 'Release the first chapter',
                  'Connect your LMS (optional)'):
        assert title in h, title
    assert 'Included (pending SME review)' in h or 'Not used' in h
    before = int(re.search(r'id="setupProgress">(\d+) of', h).group(1))
    r = instructor.post(f'/instructor/section/{sid}/setup', data={'item': 'helix'})
    assert r.status_code == 303 and r.headers['Location'].endswith('#setup')
    h = instructor.get(f'/instructor/section/{sid}').get_data(as_text=True)
    assert int(re.search(r'id="setupProgress">(\d+) of', h).group(1)) == before + 1
    assert instructor.post(f'/instructor/section/{sid}/setup', data={'item': 'bogus'}).status_code == 400
    instructor.post(f'/instructor/section/{sid}/setup', data={'item': 'hide'})
    assert 'Set up your class' not in instructor.get(f'/instructor/section/{sid}').get_data(as_text=True)
    instructor.post(f'/instructor/section/{sid}/setup', data={'item': 'show'})
    assert 'Set up your class' in instructor.get(f'/instructor/section/{sid}').get_data(as_text=True)
    with app.app_context():
        mod.onboarding_api['Flag'].query.filter_by(section_id=sid).delete()
        mod.db.session.commit()


def test_checklist_changes_no_setting(app, mod, instructor):
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        sid = mod.ClassSection.query.first().id
        before = {k: v for k, v in eng.settings(sid).items() if k != 'row'}
    for item in ('adaptivity', 'cert', 'lti', 'release'):
        instructor.post(f'/instructor/section/{sid}/setup', data={'item': item})
    with app.app_context():
        assert {k: v for k, v in app.extensions['ciwt_mastery'].engine.settings(sid).items() if k != 'row'} == before
        mod.onboarding_api['Flag'].query.filter_by(section_id=sid).delete()
        mod.db.session.commit()


def test_students_cannot_use_the_setup_route_and_do_not_see_it(app, mod, student):
    with app.app_context():
        _u, sid = _section_for(mod, 'student1@lms.local')
    assert student.post(f'/instructor/section/{sid}/setup', data={'item': 'helix'}).status_code == 403
    assert 'Set up your class' not in student.get(f'/student/section/{sid}').get_data(as_text=True)


def test_student_intro_shows_once_then_never_again(app, mod, student, instructor):
    with app.app_context():
        u, sid = _section_for(mod, 'student1@lms.local')
        mod.onboarding_api['Flag'].query.filter_by(user_id=u.id).delete()
        mod.db.session.commit()
    h = student.get(f'/student/section/{sid}').get_data(as_text=True)
    assert 'How your path works' in h and 'None of this changes your grade' in h and 'Daily review' in h
    r = student.post('/student/intro/done', data={'next': f'/student/section/{sid}'})
    assert r.status_code == 303 and r.headers['Location'].endswith(f'/student/section/{sid}')
    assert 'How your path works' not in student.get(f'/student/section/{sid}').get_data(as_text=True)
    # an off-site "next" is ignored
    r = student.post('/student/intro/done', data={'next': 'https://evil.example/'})
    assert 'evil' not in r.headers['Location']
    assert instructor.post('/student/intro/done').status_code == 403
