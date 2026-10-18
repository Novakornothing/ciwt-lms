"""Explanation ladder engine (pass 19): policy, progression through the routes, profile, instructor controls,
Who needs me / briefing hooks, and that grades are never touched."""
import re

import pytest

from curriculum_v2 import ladder as LD
from mastery import ladder_policy as P


# ---------------------------------------------------------------- policy (pure)
def test_progression_default_order_and_exhaustion():
    a = P.allowed_rungs(4)
    st = P.start(a)
    assert st['current'] == 'R0'
    seen = []
    for _ in range(4):
        st, nxt, ev = P.after_answer(st, False, P.order(a))
        seen.append(nxt)
        assert ev == 'escalated'
    assert seen == ['R1', 'R2', 'R3', 'R4']
    st, nxt, ev = P.after_answer(st, False, P.order(a))
    assert nxt is None and ev == 'exhausted' and st['exhausted']
    st, nxt, ev = P.after_answer(st, True, P.order(a))
    assert ev == 'resolved' and st['resolved'] == 'R4' and not st['exhausted']


def test_requests_escalate_without_a_miss_and_max_rungs():
    a = P.allowed_rungs(2)
    assert a == ['R1', 'R2']
    st = P.start(a)
    st, nxt, _ = P.after_request(st, P.order(a))
    assert nxt == 'R1' and st['misses'] == 0 and st['requests'] == 1
    st, nxt, _ = P.after_request(st, P.order(a))
    st, nxt, ev = P.after_request(st, P.order(a))
    assert nxt is None and ev == 'exhausted'
    assert P.allowed_rungs(4, {'off': True}) == []
    assert P.allowed_rungs(4, {'max': 1}) == ['R1']
    assert P.allowed_rungs(2, {'max': 3}) == ['R1', 'R2']


def test_resolved_section_stays_resolved_when_browsing():
    st = P.start(['R1', 'R2'])
    st, _, _ = P.after_answer(st, False, ['R1', 'R2'])
    st, _, _ = P.after_answer(st, True, ['R1', 'R2'])
    st2 = P.show(st, 'R0')
    assert st2['resolved'] == 'R1' and st2['current'] == 'R0'
    assert P.show(st, 'R2') == st      # not seen yet: ignored


def _sec(lesson, shown, resolved):
    return {'lesson': lesson, 'shown': set(shown), 'resolved': resolved}


def test_profile_threshold_is_conservative():
    assert P.profile([])['best'] is None
    three = [_sec('a', ['R1', 'R2'], 'R2'), _sec('a', ['R1', 'R2'], 'R2'), _sec('b', ['R1', 'R2'], 'R2')]
    assert P.profile(three)['best'] is None                                    # under 4 resolutions
    one_lesson = [_sec('a', ['R1', 'R2'], 'R2')] * 4
    assert P.profile(one_lesson)['best'] is None                               # one lesson only
    clear = [_sec('a', ['R1', 'R2'], 'R2'), _sec('a', ['R1', 'R2'], 'R2'), _sec('b', ['R1', 'R2'], 'R2'),
             _sec('b', ['R1'], 'R1')]
    p = P.profile(clear)
    assert p['best'] == 'analogy' and p['rates']['analogy'] == 1.0 and p['rates']['plain'] == 0.25
    with_orig = clear + [_sec('c', [], 'R0')] * 10                             # R0 resolutions are not rung evidence
    assert P.profile(with_orig)['best'] == 'analogy' and P.profile(with_orig)['original'] == 10
    # R1 comes first, so it is tried most: 4 of 8 for plain vs 4 of 4 for analogy -> analogy, by rate
    biased = [_sec(f'l{i}', ['R1'], 'R1') for i in range(4)] + [_sec(f'm{i}', ['R1', 'R2'], 'R2') for i in range(4)]
    assert P.profile(biased)['best'] == 'analogy'
    only_plain = [_sec(f'l{i}', ['R1'], 'R1') for i in range(3)] + [_sec(f'm{i}', ['R1', 'R2'], None) for i in range(3)]
    only_plain += [_sec('n', ['R1', 'R2', 'R3'], 'R3')]
    assert P.profile(only_plain)['best'] is None                               # plain 3/7 = 43% < 60%
    close = [_sec('a', ['R1', 'R2'], 'R2'), _sec('a', ['R1', 'R2'], 'R2'), _sec('b', ['R1', 'R2'], 'R2'),
             _sec('b', ['R1', 'R2'], 'R1'), _sec('c', ['R1', 'R2'], 'R1'), _sec('c', ['R1', 'R2'], 'R1')]
    assert P.profile(close)['best'] is None                                    # 50% vs 50%


def test_synthetic_simulation_policy_properties():
    """SYNTHETIC (tools/ladder_sim.py): not student evidence, only a check that the policy behaves as designed."""
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location('ladder_sim', pathlib.Path(__file__).parents[1] / 'tools' / 'ladder_sim.py')
    sim = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim)
    r = sim.simulate(400, 19)
    assert r['label'].startswith('SYNTHETIC')
    g = r['groups']
    for k in ('plain', 'analogy', 'visual', 'try', 'None'):
        assert g[k]['profile_wrong_lead'] <= 0.10, (k, g[k])
        assert g[k]['exhausted_rate'] < 0.05
    for k in ('plain', 'analogy', 'visual'):
        assert g[k]['profile_right'] >= 0.6, (k, g[k])
    for k in ('analogy', 'visual', 'try'):
        assert g[k]['alt_rungs_after_profile'] < g[k]['alt_rungs_before_profile'], (k, g[k])


def test_profile_leads_but_never_replaces_the_original_by_default():
    a = P.allowed_rungs(4)
    assert P.order(a, 'visual') == ['R3', 'R1', 'R2', 'R4']
    assert P.start(a, 'visual')['current'] == 'R0'
    st = P.start(a, 'visual', adapt_first=True)
    assert st['current'] == 'R3' and st['tried'] == ['R3'] and st['adapted']
    assert P.order(P.allowed_rungs(2), 'visual') == ['R1', 'R2']    # best type not allowed in this class


# ---------------------------------------------------------------- routes
def _lesson(mod, label='1.1', code='ITSUP'):
    c = mod.Course.query.filter_by(code=code).first()
    for m in mod.Module.query.filter_by(course_id=c.id).order_by(mod.Module.order).all():
        for les in mod.Lesson.query.filter_by(module_id=m.id).all():
            if les.title.startswith(label + ' '):
                return m, les
    raise AssertionError(label)


def _section_for(mod, code='ITSUP'):
    c = mod.Course.query.filter_by(code=code).first()
    s = mod.ClassSection.query.filter_by(course_id=c.id).order_by(mod.ClassSection.id).first()
    return s


def _check_ids(html, sid):
    box = html.split(f'id="ladder-{sid}"', 1)[1].split('class="ladder-helix"', 1)[0]
    m = re.search(r'name="check_id" value="([^"]+)"', box)
    return m.group(1) if m else None, box


def _ans(cid, right=True):
    course, rest = cid[2:].split('-', 1)
    ent = None
    for (c, label, sid), e in LD.ladder().items():
        if c == course and cid.startswith(f'L-{c}-{label}-{sid}-'):
            ent = LD.entry(c, label, sid)
            rung = cid[len(f'L-{c}-{label}-{sid}-'):].split('-')[0]
            break
    chk = next(x for x in LD.rung_checks(ent, rung) if x['id'] == cid)
    return chk['correct'] if right else next(o for o in chk['options'] if o != chk['correct'])


@pytest.fixture
def lesson11(mod, app):
    with app.app_context():
        m, les = _lesson(mod)
        sec = _section_for(mod)
        return sec.id, m.id, les.id


def _reset(mod, app, uid_email):
    with app.app_context():
        u = mod.User.query.filter_by(email=uid_email).first()
        lm = mod.mastery_api.ladder.models
        lm.LadderState.query.filter_by(user_id=u.id).delete()
        lm.LadderEvent.query.filter_by(user_id=u.id).delete()
        lm.LadderSetting.query.delete()
        mod.db.session.commit()
        return u.id


SID = '2-three-kinds-of-work'


def test_miss_miss_pass_return(student, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    url = f'/student/module/{s}/{m}/lesson/{l}'
    html = student.get(url).get_data(as_text=True)
    assert 'id="ladder-' + SID + '"' in html and 'Quick check · not graded' in html
    cid, box = _check_ids(html, SID)
    assert cid.endswith('-R0-1') and 'See the original' not in box
    with app.app_context():
        wrong = _ans(cid, False)
    r = student.post(f'/student/section/{s}/ladder/{l}/{SID}/answer', data={'check_id': cid, 'answer': wrong},
                     headers={'X-Requested-With': 'fetch'})
    j = r.get_json()
    assert j['shown'] == 'R1' and j['label'] == 'Explained more simply' and 'Not quite' in j['feedback']['text']
    assert 'See the original explanation' in j['html'] and 'Pending SME review' in j['html']
    cid = re.search(r'name="check_id" value="([^"]+)"', j['html']).group(1)
    assert '-R1-' in cid
    with app.app_context():
        wrong = _ans(cid, False)
    j = student.post(f'/student/section/{s}/ladder/{l}/{SID}/answer', data={'check_id': cid, 'answer': wrong},
                     headers={'X-Requested-With': 'fetch'}).get_json()
    assert j['shown'] == 'R2' and j['label'] == 'Explained another way: analogy'
    cid = re.search(r'name="check_id" value="([^"]+)"', j['html']).group(1)
    with app.app_context():
        right = _ans(cid, True)
    j = student.post(f'/student/section/{s}/ladder/{l}/{SID}/answer', data={'check_id': cid, 'answer': right},
                     headers={'X-Requested-With': 'fetch'}).get_json()
    assert j['event'] == 'resolved' and j['feedback']['ok']
    html = student.get(url).get_data(as_text=True)
    _cid, box = _check_ids(html, SID)
    assert 'data-shown="R2"' in box and 'Explained another way: analogy' in box and 'See the original explanation' in box
    assert 'You got the check on this section with this explanation' in box
    # the original is still in the page for the toggle, and the no-JS link shows it
    assert '<template class="ladder-original-tpl">' in box
    html = student.get(url + f'?ladder_original={SID}').get_data(as_text=True)
    assert 'data-shown="R0"' in _check_ids(html, SID)[1]


def test_keys_never_in_student_page(student, mod, app, lesson11):
    s, m, l = lesson11
    html = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    assert '<div class="instructor-note">' not in html
    with app.app_context():
        ent = LD.entry('ITSUP', '1.1', SID)
        why = LD.rung_checks(ent, 'R0')[0]['why']
    assert why not in html


def test_exhaustion_flags_who_needs_me_and_profile(student2, instructor, mod, app, lesson11):
    uid = _reset(mod, app, 'student2@lms.local')
    s, m, l = lesson11
    sid = '3-impact-and-identity'
    html = student2.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    cid, _ = _check_ids(html, sid)
    for _ in range(5):
        with app.app_context():
            wrong = _ans(cid, False)
        j = student2.post(f'/student/section/{s}/ladder/{l}/{sid}/answer', data={'check_id': cid, 'answer': wrong},
                          headers={'X-Requested-With': 'fetch'}).get_json()
        m2 = re.search(r'name="check_id" value="([^"]+)"', j['html'])
        cid = m2.group(1) if m2 else cid
    assert j['event'] in ('exhausted', 'no_more') and 'every explanation' in j['feedback']['text']
    page = instructor.get(f'/instructor/section/{s}/mastery/today').get_data(as_text=True)
    assert 'Every explanation tried' in page and 'Impact and identity' in page.replace('3. ', '')
    prof = instructor.get(f'/instructor/section/{s}/ladder/student/{uid}').get_data(as_text=True)
    assert 'every explanation seen' in prof
    an = instructor.get(f'/instructor/section/{s}/ladder').get_data(as_text=True)
    assert 'Sections students most often needed explained another way' in an and 'Includes demo seed data' in an
    pv = instructor.get(f'/instructor/section/{s}/ladder/preview/1.1').get_data(as_text=True)
    assert '✓' in pv and 'Pending SME review' in pv


def test_instructor_controls(student, instructor, mod, app, lesson11):
    _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    url = f'/student/module/{s}/{m}/lesson/{l}'
    r = instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'class', 'enabled': 'on', 'max_rung': '4'})
    assert r.status_code == 303
    assert 'Quick check · not graded' not in student.get(url).get_data(as_text=True)     # micro-checks off
    assert "explain it another way" in student.get(url).get_data(as_text=True)
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'override', 'label': '1.1', 'sid': SID, 'value': 'off'})
    assert f'id="ladder-{SID}"' not in student.get(url).get_data(as_text=True)
    assert student.post(f'/student/section/{s}/ladder/{l}/{SID}/another').status_code == 404
    instructor.post(f'/instructor/section/{s}/ladder/settings', data={'form': 'class', 'max_rung': '4'})   # all off
    assert 'class="ladder' not in student.get(url).get_data(as_text=True)
    with app.app_context():
        mod.mastery_api.ladder.models.LadderSetting.query.delete()
        mod.db.session.commit()
    assert f'id="ladder-{SID}"' in student.get(url).get_data(as_text=True)


def test_profile_page_and_reset(student, mod, app, lesson11):
    s, _m, _l = lesson11
    page = student.get(f'/student/section/{s}/what-helps-you-learn').get_data(as_text=True)
    assert 'What helps you learn' in page and 'How this is decided' in page
    r = student.post(f'/student/section/{s}/what-helps-you-learn')
    assert r.status_code == 303
    assert 'Started fresh on' in student.get(f'/student/section/{s}/what-helps-you-learn').get_data(as_text=True)


def test_grades_untouched(student, mod, app, lesson11):
    s, m, l = lesson11
    with app.app_context():
        u = mod.User.query.filter_by(email='student1@lms.local').first()
        before = (mod.QuizAttempt.query.filter_by(user_id=u.id).count(), mod.TestAttempt.query.filter_by(user_id=u.id).count(),
                  mod.mastery_api.models.MasteryCheck.query.filter_by(user_id=u.id).count())
    html = student.get(f'/student/module/{s}/{m}/lesson/{l}').get_data(as_text=True)
    cid, _ = _check_ids(html, 'what-software-is')
    with app.app_context():
        wrong = _ans(cid, False)
    student.post(f'/student/section/{s}/ladder/{l}/what-software-is/answer', data={'check_id': cid, 'answer': wrong})
    with app.app_context():
        after = (mod.QuizAttempt.query.filter_by(user_id=u.id).count(), mod.TestAttempt.query.filter_by(user_id=u.id).count(),
                 mod.mastery_api.models.MasteryCheck.query.filter_by(user_id=u.id).count())
    assert before == after


def test_access_rules(outsider, instructor, anon, lesson11):
    s, _m, l = lesson11
    assert outsider.post(f'/student/section/{s}/ladder/{l}/{SID}/another').status_code in (403, 404)
    assert instructor.post(f'/student/section/{s}/ladder/{l}/{SID}/another').status_code == 403
    assert anon.post(f'/student/section/{s}/ladder/{l}/{SID}/another').status_code in (302, 401)
    assert outsider.get(f'/instructor/section/{s}/ladder').status_code == 403


def test_helix_offer_needs_consent(student, mod, app, lesson11):
    s, _m, l = lesson11
    r = student.post(f'/student/section/{s}/ladder/{l}/{SID}/event', data={'kind': 'helix_offer'})
    assert r.status_code in (200, 403)
    with app.app_context():
        u = mod.User.query.filter_by(email='student1@lms.local').first()
        sec = mod.db.session.get(mod.ClassSection, s)
        ok = mod.mastery_api.engine.helix_state(sec, u) == 'ok'
    assert (r.status_code == 200) == ok


def test_every_laddered_lesson_renders_for_a_student(app, mod):
    """All merged ladder files (every course): each lesson with ladder entries renders for an enrolled student,
    with one wrapper per laddered or same_as section, and no server error."""
    from curriculum_v2.ladder import sections as LSEC
    with app.app_context():
        todo = []
        for code in ('ITSUP', 'NETOPS', 'CLIENT'):
            c = mod.Course.query.filter_by(code=code).first()
            sec = mod.ClassSection.query.filter_by(course_id=c.id).order_by(mod.ClassSection.id).first() if c else None
            if not sec:
                continue
            enr = mod.Enrollment.query.filter_by(section_id=sec.id).join(mod.User, mod.User.id == mod.Enrollment.user_id) \
                .filter(mod.User.role == 'student').first()
            if not enr:
                continue
            email = mod.db.session.get(mod.User, enr.user_id).email
            for m in mod.Module.query.filter_by(course_id=c.id).all():
                for les in mod.Lesson.query.filter_by(module_id=m.id).all():
                    label = LSEC.lesson_label(les.title)
                    want = [s['sid'] for s in LSEC.sections(les.content or '') if LD.entry(code, label, s['sid'])]
                    if want:
                        todo.append((email, sec.id, m.id, les.id, want))
    assert todo
    clients = {}
    n = 0
    for email, s, m, l, want in todo:
        cl = clients.get(email)
        if not cl:
            cl = clients[email] = app.test_client()
            cl.post('/login', data={'email': email, 'password': 'student123'})
        r = cl.get(f'/student/module/{s}/{m}/lesson/{l}')
        if r.status_code != 200:          # module not released to students in this class: not a ladder failure
            continue
        html = r.get_data(as_text=True)
        got = re.findall(r'data-ladder-sid="([^"]+)"', html)
        assert got == want, (email, l, set(want) - set(got))
        n += 1
    assert n >= 5


def test_adapt_first_and_profile_order_through_routes(student, instructor, mod, app, lesson11):
    uid = _reset(mod, app, 'student1@lms.local')
    s, m, l = lesson11
    with app.app_context():
        lm = mod.mastery_api.ladder.models
        for i, lab in enumerate(['1.2', '1.2', '1.3', '1.3']):           # 4 sections in 2 lessons cleared by R3
            for k, rung in (('check', 'R1'), ('check', 'R3'), ('resolved', 'R3')):
                mod.db.session.add(lm.LadderEvent(user_id=uid, section_id=s, course='ITSUP', label=lab, sid=f'x{i}',
                                                  kind=k, rung=rung, correct=(k == 'resolved') or None))
        mod.db.session.commit()
        assert mod.mastery_api.ladder.profile(uid)['best'] == 'visual'
    url = f'/student/module/{s}/{m}/lesson/{l}'
    assert 'data-shown="R0"' in _check_ids(student.get(url).get_data(as_text=True), SID)[1]   # default: original first
    j = student.post(f'/student/section/{s}/ladder/{l}/{SID}/another', headers={'X-Requested-With': 'fetch'}).get_json()
    assert j['shown'] == 'R3'                                             # the profile leads with what helped
    instructor.post(f'/instructor/section/{s}/ladder/settings',
                    data={'form': 'class', 'enabled': 'on', 'micro_checks': 'on', 'adapt_first': 'on', 'max_rung': '4'})
    box = _check_ids(student.get(url).get_data(as_text=True), 'what-software-is')[1]
    assert 'data-shown="R3"' in box and 'See the original explanation' in box and 'ladder-original-tpl' in box
    page = student.get(f'/student/section/{s}/what-helps-you-learn').get_data(as_text=True)
    assert 'Leads when a section does not click' in page and 'adapt the first presentation' in page
    _reset(mod, app, 'student1@lms.local')


def test_analytics_csv_chapter_filter_and_review_queue(instructor, lesson11):
    s, _m, _l = lesson11
    page = instructor.get(f'/instructor/section/{s}/ladder?chapter=1').get_data(as_text=True)
    assert 'Review the explanations (Pending SME review)' in page and 'Read every explanation' in page
    r = instructor.get(f'/instructor/section/{s}/ladder?format=csv')
    assert r.status_code == 200 and r.mimetype == 'text/csv'
    assert r.get_data(as_text=True).splitlines()[0].startswith('lesson,section,students')


def test_who_needs_me_links_and_message_draft_is_not_sent(student2, instructor, mod, app, lesson11):
    _reset(mod, app, 'student2@lms.local')
    s, m, l = lesson11
    sid = '3-impact-and-identity'
    for _ in range(5):                       # R1..R4, then a fifth request finds nothing new: exhausted
        student2.post(f'/student/section/{s}/ladder/{l}/{sid}/another')
    with app.app_context():
        n_msgs = mod.StaffMessage.query.count()
    page = instructor.get(f'/instructor/section/{s}/mastery/today').get_data(as_text=True)
    assert 'Draft a message about this section' in page and 'Read the explanations they saw' in page
    href = re.search(r'href="([^"]*/messages/new[^"]*subject=[^"]+)"', page).group(1).replace('&amp;', '&')
    draft = instructor.get(href).get_data(as_text=True)
    assert 'Let us go through' in draft
    with app.app_context():
        assert mod.StaffMessage.query.count() == n_msgs                   # a draft only: nothing is sent


def test_lessons_without_ladder_content_are_unchanged(student, instructor, mod, app, lesson11):
    """No ladder entries for the lesson (or staff viewing, or the ladder off): the lesson body is exactly the classic
    render_lesson output, no ladder markup or script."""
    from curriculum_v2.ladder import sections as LSEC
    s, m11, l11 = lesson11
    with app.app_context():
        c = mod.Course.query.filter_by(code='ITSUP').first()
        plain = None
        for m in mod.Module.query.filter_by(course_id=c.id).order_by(mod.Module.order).all():
            for les in mod.Lesson.query.filter_by(module_id=m.id).order_by(mod.Lesson.order).all():
                label = LSEC.lesson_label(les.title)
                if not any(k[0] == 'ITSUP' and k[1] == label for k in LD.ladder()):
                    plain = (m.id, les.id, les.content)
                    break
            if plain:
                break
        expected = mod._INSTRUCTOR_NOTE_RE.sub('', mod.render_lesson_html(plain[2]))
    html = student.get(f'/student/module/{s}/{plain[0]}/lesson/{plain[1]}').get_data(as_text=True)
    assert 'class="ladder' not in html and 'js/ladder.js' not in html and expected in html
    staff = instructor.get(f'/student/module/{s}/{m11}/lesson/{l11}').get_data(as_text=True)
    assert 'data-ladder-sid' not in staff and 'js/ladder.js' not in staff
