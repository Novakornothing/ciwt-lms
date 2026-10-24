"""Final pre-pilot UX: landing privacy/FAQ/contact, /contact + footer, labels, lesson -> check -> lab flow."""
import re

from tests.test_ladder_engine import _ans, _check_ids, _reset, lesson11  # noqa: F401

MAIL = 'mailto:contact@novakornothing.com'


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
    assert 'Contact &amp; Support:' in h and 'href="/contact"' in h          # footer
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
