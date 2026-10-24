"""Final pre-pilot UX: landing privacy/FAQ/contact, /contact + footer, labels, lesson -> check -> lab flow."""
import re

from tests.test_ladder_engine import _ans, _check_ids, _reset, lesson11  # noqa: F401

MAIL = 'mailto:novakornothing@gmail.com'


def test_landing_host_privacy_faq_contact(app):
    for host in ('novakornothing.com', 'www.novakornothing.com'):
        h = app.test_client().get('/', base_url=f'http://{host}').get_data(as_text=True)
        assert 'navy-n-512.webp' in h and 'Privacy note' in h and 'FERPA' in h
        assert 'no video or images ever leave the device' in h and '/my-data' in h and 'tamper-evident' in h
        assert h.count('<details>') >= 5 and 'How do colleges or training commands run a pilot?' in h
        assert MAIL in h and 'href="/login"' in h
    c = app.test_client()
    assert 'Privacy note' in c.get('/landing').get_data(as_text=True)
    assert 'Privacy note' in c.get('/?landing=1').get_data(as_text=True)


def test_contact_page_footer_and_setup_card(anon, instructor, mod, app, lesson11):
    h = anon.get('/contact').get_data(as_text=True)
    assert MAIL in h and 'Instructors' in h and 'Students' in h
    assert '© 2026 Novak LMS™' in h and 'Contact: <a href="mailto:' in h and 'href="/contact"' in h   # footer
    s = lesson11[0]
    h = instructor.get(f'/instructor/section/{s}/setup').get_data(as_text=True)
    assert 'Pilot support' in h and MAIL in h


def test_gate_progression_lesson_to_check_and_lab(student, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    url = f'/student/module/{s}/{m}/lesson/{l}'
    html = student.get(url).get_data(as_text=True)
    sids = list(dict.fromkeys(re.findall(r'id="ladder-([^"]+)"[^>]*data-shown', html)))
    cnt = re.compile(r'(\d+) of (\d+)</span> sections verified')
    done, total = map(int, cnt.search(html).groups())
    assert sids and done == 0 and total > 0
    assert 'Check understanding' in html and 'Explain it another way (Plain language)' in html
    assert 'What to do next' in html
    for sid in sids:
        cid, _ = _check_ids(student.get(url).get_data(as_text=True), sid)
        if not cid:
            continue
        with app.app_context():
            right = _ans(cid, True)
        student.post(f'/student/section/{s}/ladder/{l}/{sid}/answer', data={'check_id': cid, 'answer': right})
    html = student.get(url).get_data(as_text=True)
    m2 = cnt.search(html)
    assert m2 is None or m2.group(1) == m2.group(2)        # strip disappears or shows all verified
    assert 'Next section' in html or 'All sections verified' in html or 'Continue to' in html or 'Next' in html
    # last lesson of the module ends with the chapter check and lab, never a dead end
    with app.app_context():
        last = mod.Lesson.query.filter_by(module_id=m).order_by(mod.Lesson.order.desc()).first().id
    h = student.get(f'/student/module/{s}/{m}/lesson/{last}').get_data(as_text=True)
    assert 'Continue to Adaptive Check' in h or 'Continue to Lab' in h
    _reset(mod, app, 'student1@lms.local')


def test_ladder_scope_course_and_csv(instructor, mod, app, lesson11):
    s = lesson11[0]
    h = instructor.get(f'/instructor/section/{s}/ladder').get_data(as_text=True)
    assert 'Scope:' in h and 'This class (' in h and 'scope=course' in h
    h = instructor.get(f'/instructor/section/{s}/ladder?scope=course').get_data(as_text=True)
    assert 'Curriculum average' in h and 'aria-current="page">All ' in h
    r = instructor.get(f'/instructor/section/{s}/ladder?scope=course&format=csv')
    assert r.status_code == 200 and r.mimetype == 'text/csv'
    assert 'explanations-course-' in r.headers['Content-Disposition']
    assert r.get_data(as_text=True).startswith('scope: all ')


def test_who_needs_me_empty_state_and_helix_note(instructor, mod, app):
    with app.app_context():
        sec = mod.ClassSection(name='Empty pilot class', course_id=mod.Course.query.first().id,
                               instructor_id=mod.User.query.filter_by(email='instructor@lms.local').first().id)
        mod.db.session.add(sec); mod.db.session.commit(); sid = sec.id
    h = instructor.get(f'/instructor/section/{sid}/who-needs-me').get_data(as_text=True)
    assert 'No students are struggling in this class right now.' in h
    assert 'Helix attention signals: 0 students opted in for this section' in h
    with app.app_context():
        mod.db.session.delete(mod.db.session.get(mod.ClassSection, sid)); mod.db.session.commit()


def test_privacy_page_and_brand_footer(app, anon, student):
    for c, kw in ((app.test_client(), {'base_url': 'http://novakornothing.com'}), (anon, {}), (student, {})):
        h = c.get('/privacy', **kw).get_data(as_text=True)
        assert 'never sold or shared with third-party advertisers' in h and 'never leave your device' in h
        assert 'FERPA' in h and '/my-data' in h and 'tamper-evident' in h and MAIL in h
        assert '© 2026 Novak LMS™' in h and 'href="/privacy"' in h
    h = app.test_client().get('/', base_url='http://novakornothing.com').get_data(as_text=True)
    assert '© 2026 Novak LMS™' in h and 'href="/privacy"' in h and MAIL in h and 'href="/contact"' in h
    h = student.get('/contact').get_data(as_text=True)
    assert '© 2026 Novak LMS™' in h and 'Novak LMS™</span>' in h and MAIL in h


def test_register_and_demo_enter(app, mod):
    c = app.test_client()
    # 1. Landing page has NOVAK LMS™, Eye Tracking, OPs, Demo, Create Account, FAQ, and Legal & Privacy note
    h = c.get("/landing").get_data(as_text=True)
    for expected in ("NOVAK LMS™", "Eye Tracking", "OPs", "Demo", "Create Account", "FAQ", "Legal Information &amp; Privacy note"):
        assert expected in h, f"Missing {expected} in /landing"

    # 2. 1-click demo enter for student, instructor, admin
    for role, target in (("student", "/student"), ("instructor", "/instructor"), ("admin", "/admin")):
        r = c.get(f"/demo/enter/{role}", follow_redirects=False)
        assert r.status_code in (302, 303)
        c.get("/logout")

    # 3. Self-service account creation (/register)
    r_get = c.get("/register")
    assert r_get.status_code == 200 and "Create your" in r_get.get_data(as_text=True)
    r_post = c.post("/register", data={
        "first_name": "Taylor",
        "last_name": "Sailor",
        "email": "taylor.sailor.new@lms.local",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!",
        "role": "student",
        "enroll_demo": "1",
    }, follow_redirects=True)
    assert r_post.status_code == 200
    body = r_post.get_data(as_text=True)
    assert "Welcome to Novak LMS™, Taylor!" in body
    with app.app_context():
        u = mod.User.query.filter_by(email="taylor.sailor.new@lms.local").first()
        assert u is not None and u.role == "student"
        enrolls = mod.Enrollment.query.filter_by(user_id=u.id).all()
        assert len(enrolls) >= 1
        for e in enrolls:
            mod.db.session.delete(e)
        mod.db.session.delete(u)
        mod.db.session.commit()
