"""Pilot polish: swap badge + rung pill + continue chip, deep link to a rung, What finally clicked, Why struggling."""
from tests.test_ladder_engine import SID, _ans, _check_ids, _reset, lesson11  # noqa: F401


def test_swap_badge_pill_and_continue_chip(student, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    html = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    cid, _ = _check_ids(html, SID)
    with app.app_context():
        wrong = _ans(cid, False)
    j = student.post(f'/student/section/{s}/ladder/{l}/{SID}/answer', data={'check_id': cid, 'answer': wrong},
                     headers={'X-Requested-With': 'fetch'}).get_json()
    assert 'Swapped to R1: Plain language — step 1 of' in j['html'] and 'class="ladder-steps"' in j['html']
    assert 'aria-current="step"' in j['html']
    cid2, _ = _check_ids(j['html'], SID)
    with app.app_context():
        right = _ans(cid2, True)
    j = student.post(f'/student/section/{s}/ladder/{l}/{SID}/answer', data={'check_id': cid2, 'answer': right},
                     headers={'X-Requested-With': 'fetch'}).get_json()
    assert f'data-continue="{SID}"' in j['html'] and 'Next section' in j['html'] and 'ls-resolved' in j['html']
    page = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    assert 'js/ladder_gate.js' in page


def test_deep_link_opens_section_on_rung(student, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    r = student.get(f'/student/section/{s}/lesson/{l}?rung=R2&sid={SID}')
    assert r.status_code == 302 and 'rung=R2' in r.headers['Location'] and f'sid={SID}' in r.headers['Location']
    html = student.get(r.headers['Location']).get_data(as_text=True)
    box = html.split(f'id="ladder-{SID}"', 1)[1][:3000]
    assert 'data-shown="R2"' in html.split(f'id="ladder-{SID}"', 1)[1][:200] and 'Swapped to R2: Analogy' in box
    _reset(mod, app, 'student1@lms.local')


def test_what_clicked_and_why_struggling(student2, instructor, mod, app, lesson11):
    _reset(mod, app, 'student2@lms.local')
    s, m, l = lesson11
    html = student2.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    cid, _ = _check_ids(html, SID)
    with app.app_context():
        wrong = _ans(cid, False)
    j = student2.post(f'/student/section/{s}/ladder/{l}/{SID}/answer', data={'check_id': cid, 'answer': wrong},
                      headers={'X-Requested-With': 'fetch'}).get_json()
    cid2, _ = _check_ids(j['html'], SID)
    with app.app_context():
        right = _ans(cid2, True)
        uid = mod.User.query.filter_by(email='student2@lms.local').first().id
    student2.post(f'/student/section/{s}/ladder/{l}/{SID}/answer', data={'check_id': cid2, 'answer': right})
    with app.app_context():
        c = mod.mastery_api.ladder.clicked(uid, s)
        assert c['best'] == 'R1' and c['best_text'].startswith('Best style: Plain language (resolved 1/')
        assert any(x['text'].startswith('Clicked on R1: Plain language after 1 miss') for x in c['sections'])
    h = instructor.get(f'/instructor/section/{s}/ladder/student/{uid}').get_data(as_text=True)
    assert 'What finally clicked' in h and 'Clicked on R1' in h
    assert 'What finally clicked for this class' in instructor.get(f'/instructor/section/{s}/ladder').get_data(as_text=True)
    h = instructor.get(f'/instructor/section/{s}').get_data(as_text=True)
    assert 'Why these students are struggling' in h and 'Draft message' in h and 'Where stuck' in h
    assert 'Helix:' in h
    _reset(mod, app, 'student2@lms.local')
