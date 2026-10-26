"""Option B pass 4: exam simulator auto-save/resume, server pause, timeout grading of saved answers, testing-centre
view, 90-question mode, simulation PBQs, whiteboard and eliminator, candidate score report + missed-objective drill,
and the port/protocol/acronym/command speed-drill."""
import json
import random
import re
from datetime import timedelta

import pytest

from curriculum_v2.cert import exam_sim as ES
from curriculum_v2.cert import practice as P
from curriculum_v2.cert import sim_pbq as SIM
from curriculum_v2.cert import speed_drill as SD

BASE = '/student/section/1/exam-sim'


def _start(client, exam='N', mode='sprint', timing='practice'):
    r = client.post(BASE + '/start', data={'exam': exam, 'mode': mode, 'timing': timing})
    assert r.status_code == 302
    return int(re.search(r'/exam-sim/(\d+)', r.headers['Location']).group(1))


def _att(app, mod, aid):
    with app.app_context():
        a = mod.db.session.get(mod.ExamSimAttempt, aid)
        return json.loads(a.items), a


def _right(iid):
    it = P.bank()[iid]
    return it['correct'] if it['type'] == 'single' else it['correct']


def _form_for(items, upto, flag=()):
    b, data = P.bank(), {}
    for i, (iid, _o) in enumerate(items[:upto]):
        it = b[iid]
        if it['type'] == 'single':
            data[f'q{i}'] = it['correct']
        elif it['type'] == 'multi':
            data[f'q{i}'] = list(it['correct'])
        else:
            for k, v in enumerate(it['correct']):
                data[f'q{i}_{k}'] = v
    for i in flag:
        data[f'flag{i}'] = '1'
    return data


# ------------------------------------------------------------------ modes and form building
def test_modes_and_pbq_types():
    assert ES.MODES['max'] == {'name': 'Official 90-question sitting', 'minutes': 90, 'questions': 90, 'pbqs': 5}
    assert ES.MODES['full']['questions'] == 45 and ES.MODES['full']['pbqs'] == 4
    assert ES.MODES['sprint']['minutes'] == 20 and ES.MODES['sprint']['questions'] == 15
    assert ES.PBQ_TYPES[0] == 'sim_pbq'


@pytest.mark.parametrize('exam', ['A1', 'A2', 'N'])
def test_max_mode_90_questions_opens_with_simulations(exam):
    items = ES.build_form(exam, 'max', random.Random(3))
    b = P.bank()
    assert len(items) == 90 and len({i for i, _ in items}) == 90
    types = [b[i]['type'] for i, _ in items]
    assert types[0] == 'sim_pbq' and all(t in ES.PBQ_TYPES for t in types[:5])
    assert not any(t in ES.PBQ_TYPES for t in types[5:])


def test_sim_pbq_bank_balanced_and_tagged():
    by = {}
    for s in SIM.SIMS:
        by.setdefault(s['oid'].split(':')[0], []).append(s)
        assert {t['kind'] for t in s['tabs']} & {'terminal', 'topology', 'inspector'}
        assert 3 <= len(s['parts']) <= 4
        for p in s['parts']:
            wrong = [o for o in p['options'] if o != p['correct']]
            assert p['correct'] in p['options'] and len(wrong) == 3
            assert len(p['correct']) < 1.15 * max(map(len, wrong)), (s['id'], p['prompt'])
    assert all(len(by[e]) >= 2 for e in ('A1', 'A2', 'N')) and sum(map(len, by.values())) >= 6
    it = P.bank()['SIM-N-1']
    assert it['raw']['review'] == 'Pending SME review'
    right = json.dumps(it['correct'])
    assert P.grade(it, right) and P.partial(it, right) == (3, 3)
    half = json.dumps(it['correct'][:2] + ['x'])
    assert not P.grade(it, half) and P.partial(it, half) == (2, 3)


# ------------------------------------------------------------------ take page UI
def test_take_page_testing_centre_chrome(student):
    aid = _start(student)
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    for s in ('id="esPrev"', 'id="esNext"', 'Question 1 of 15', 'id="esReviewBtn"', 'Review Screen',
              'Skip PBQs &amp; return later', 'id="esViewToggle"', 'All-questions scroll view', 'id="esWhiteboard"',
              'Whiteboard / Scratchpad', 'Insert CIDR / Binary Grid', 'class="es-strike"', 'es-sim', 'role="tablist"',
              'es-cmd', 'Simulation', '/autosave', '/pause'):
        assert s in html, s
    assert 'style=' not in html.split('id="examSim"')[1].split('{% block')[0].split('</form>')[0]
    js = open('static/js/exam_sim.js').read()
    for s in ('es-struck', 'altKey', 'contextmenu', 'sessionStorage', '128  64  32  16', '/30', 'es-off'):
        assert s in js, s


def test_strict_mode_has_no_view_toggle_or_pause(student):
    aid = _start(student, 'A1', 'sprint', 'exam')
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    assert 'id="esViewToggle"' not in html and 'id="esPause"' not in html and 'id="esReviewBtn"' in html
    assert student.post(f'{BASE}/{aid}/pause', data={'action': 'pause'}).status_code == 403


# ------------------------------------------------------------------ auto-save and restore
def test_autosave_and_get_restores_answers_flags_whiteboard(student, app, mod):
    aid = _start(student, 'N', 'sprint')
    items, _a = _att(app, mod, aid)
    data = _form_for(items, 6, flag=(1, 4))
    data.update(all='1', whiteboard='/26 = 62 hosts')
    r = student.post(f'{BASE}/{aid}/autosave', data=data)
    assert r.status_code == 200 and r.get_json()['answered'] == 6 and r.get_json()['flagged'] == 2
    _i, att = _att(app, mod, aid)
    assert len(json.loads(att.answers)) == 6 and json.loads(att.flags) == [1, 4]
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    b = P.bank()
    for i, (iid, _o) in enumerate(items[:6]):
        it = b[iid]
        sec = html.split(f'id="esq{i}"')[1].split('</section>')[0]
        if it['type'] == 'single':
            assert re.search(r'value="[^"]*" checked', sec)
        elif it['type'] == 'multi':
            assert sec.count(' checked') >= len(it['correct'])
        else:
            assert sec.count(' selected') == len(it['correct'])
    assert html.count('class="es-flag-box" checked') == 2
    assert '/26 = 62 hosts' in html
    # final submit with an empty form keeps the auto-saved answers
    r = student.post(f'{BASE}/{aid}', data={})
    _i, att = _att(app, mod, aid)
    assert att.correct == 6 and json.loads(att.flags) == [1, 4]


# ------------------------------------------------------------------ server-side pause
def test_practice_pause_preserves_remaining(student, app, mod):
    aid = _start(student, 'A2', 'sprint')
    j = student.post(f'{BASE}/{aid}/pause', data={'action': 'pause'}).get_json()
    assert j['paused'] and 1100 <= j['remaining'] <= 1200
    frozen = j['remaining']
    with app.app_context():       # 30 minutes pass while paused: pretend the deadline is long gone
        a = mod.db.session.get(mod.ExamSimAttempt, aid)
        a.deadline = a.deadline - timedelta(minutes=30)
        mod.db.session.commit()
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    assert f'data-remaining="{frozen}"' in html and 'data-paused="1"' in html and 'Resume timer' in html
    j = student.post(f'{BASE}/{aid}/pause', data={'action': 'resume'}).get_json()
    assert not j['paused'] and frozen - 2 <= j['remaining'] <= frozen
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    assert 'data-paused="0"' in html


# ------------------------------------------------------------------ strict timeout grading
def test_strict_timeout_grades_autosaved_answers(student, app, mod):
    aid = _start(student, 'N', 'sprint', 'exam')
    items, _a = _att(app, mod, aid)
    assert student.post(f'{BASE}/{aid}/autosave', data=dict(_form_for(items, 5), all='1')).status_code == 200
    with app.app_context():
        a = mod.db.session.get(mod.ExamSimAttempt, aid)
        a.deadline = a.deadline - timedelta(minutes=25)     # clock ran out 5 min ago (well beyond grace)
        mod.db.session.commit()
    # late autosave is refused, late form answers are ignored, saved ones are graded
    assert student.post(f'{BASE}/{aid}/autosave', data=dict(_form_for(items, 10), all='1')).status_code == 409
    r = student.post(f'{BASE}/{aid}', data=dict(_form_for(items, 15), timed_out='1'))
    assert r.status_code == 302
    _i, att = _att(app, mod, aid)
    earned, possible = ES.earned_and_possible(items, json.loads(att.answers), P.bank())
    assert att.timed_out and att.correct == 5 and len(json.loads(att.answers)) == 5
    assert att.score == ES.scaled(earned, possible) and earned == sum(P.partial(P.bank()[i], json.dumps(P.bank()[i]['correct'])
                                                                                  if P.bank()[i]['type'] != 'single' else P.bank()[i]['correct'])[0]
                                                                      for i, _o in items[:5])


# ------------------------------------------------------------------ result page: report + drill
def test_candidate_score_report_and_missed_objective_drill(student, app, mod):
    aid = _start(student, 'A1', 'sprint')
    items, _a = _att(app, mod, aid)
    student.post(f'{BASE}/{aid}', data=_form_for(items, 7))
    html = student.get(f'{BASE}/{aid}/result').get_data(as_text=True)
    for s in ('Candidate Score Report', 'Candidate Name', 'Exam Code &amp; Version', '220-1201', 'Practice mode',
              'Simulated Scaled Score', 'Pass Bar', 'Voucher Readiness Status', '<meter', 'Print / Save Candidate Score Report',
              'Drill My Missed Objectives Now (10 questions)', '/remediate-drill', 'Core 1 '):
        assert s in html, s
    assert any(x in html for x in ('VOUCHER READY', 'BORDERLINE', 'REMEDIATION REQUIRED'))
    css = open('static/css/cert.css').read()
    assert '@media print' in css
    r = student.post(f'{BASE}/{aid}/remediate-drill')
    assert r.status_code == 302
    did = int(re.search(r'/exam-sim/(\d+)', r.headers['Location']).group(1))
    d_items, d = _att(app, mod, did)
    _x, src = _att(app, mod, aid)
    missed = {o for i, (iid, o) in enumerate(items)
              if not P.grade(P.bank()[iid], json.loads(src.answers).get(str(i)))}
    assert d.mode == 'drill' and 1 <= len(d_items) <= 15 and {o for _i, o in d_items} <= missed
    assert student.post(BASE + '/start', data={'exam': 'A1', 'mode': 'drill'}).status_code == 400


def test_drill_falls_back_to_weakest_domain():
    missed = sorted(P.pool('N', '1.0'))
    out = ES.drill_form('N', missed, random.Random(1))
    assert len(out) == 10 and all(o in missed for _i, o in out)


# ------------------------------------------------------------------ speed drill
def test_speed_drill_deck_content():
    assert len(SD.CARDS) >= 90 and set(SD.CATEGORIES) == {c['cat'] for c in SD.CARDS}
    fronts = ' '.join(c['front'] for c in SD.CARDS)
    for s in ('FTP', 'Kerberos', 'LDAPS', 'SIP', '802.1Q', '802.3bt', 'Cat 6A', 'MPO', 'USB4', 'ipconfig /flushdns',
              'ss -tulpn', 'show interfaces trunk', 'TACACS+', 'WPA3-SAE', 'RPO', 'DMARC', 'VXLAN'):
        assert s in fronts, s
    assert SD.balance_violations() == []
    for c in SD.CARDS:
        assert len(set(SD.choices(c))) == 4 and c['back'] in SD.choices(c)


def test_speed_drill_route_filter_and_record(student, app, mod):
    html = student.get('/student/section/1/speed-drill').get_data(as_text=True)
    assert '60-Second Timed Blitz' in html and 'Flip-Card Study Mode' in html and 'id="sdData"' in html
    assert 'speed_drill.js' in html
    html = student.get('/student/section/1/speed-drill?exam=N&cat=cli').get_data(as_text=True)
    data = json.loads(html.split('id="sdData">')[1].split('</script>')[0])
    assert data and all(c['cat'] == SD.CATEGORIES['cli'] and 'N10-009' in c['codes'] for c in data)
    j = student.post('/student/section/1/speed-drill/record', json={'card': 'SD-001', 'result': 'right', 'streak': 4}).get_json()
    assert j['ok'] and j['box'] >= 2
    j2 = student.post('/student/section/1/speed-drill/record', json={'card': 'SD-001', 'result': 'again'}).get_json()
    assert j2['box'] == 1 and j2['seen'] == j['seen'] + 1
    assert student.post('/student/section/1/speed-drill/record', json={'card': 'nope', 'result': 'right'}).status_code == 400
    assert 'speed-drill' in student.get('/student/section/1').get_data(as_text=True)
    assert 'speed-drill' in student.get(BASE).get_data(as_text=True)


def test_speed_drill_access(anon, outsider):
    assert anon.get('/student/section/1/speed-drill').status_code in (302, 401)
    assert outsider.get('/student/section/1/speed-drill').status_code == 403


# ------------------------------------------------------------------ pass 5: partial credit, ADA time, agreement
def test_partial_credit_scaled_scoring():
    b = P.bank()
    sim = b['SIM-N-1']
    chosen = [['SIM-N-1', 'N:2.2'], [next(k for k, v in b.items() if v['type'] == 'single'), 'N:1.1']]
    answers = {'0': json.dumps(sim['correct'][:2] + ['wrong'])}          # 2 of 3 parts, MCQ blank
    assert ES.earned_and_possible(chosen, answers, b) == (2, 4)
    assert ES.scaled(2, 4) == 500 and ES.scaled(45, 45) == 900 and ES.scaled(0, 0) == 100


def test_partial_credit_in_a_real_sitting(student, app, mod):
    aid = _start(student, 'N', 'sprint')
    items, _a = _att(app, mod, aid)
    assert P.bank()[items[0][0]]['type'] == 'sim_pbq'
    data = _form_for(items, 15)
    data[f'q0_0'] = 'not the key'                                          # one sub-part wrong on the first sim PBQ
    student.post(f'{BASE}/{aid}', data=data)
    _i, att = _att(app, mod, aid)
    parts = len(P.bank()[items[0][0]]['correct'])
    earned, possible = ES.earned_and_possible(items, json.loads(att.answers), P.bank())
    assert att.correct == 14 and earned == possible - 1 and att.score == ES.scaled(possible - 1, possible) > ES.scaled(14, 15) - 1
    assert parts >= 3
    html = student.get(f'{BASE}/{aid}/result').get_data(as_text=True)
    assert f'{parts - 1}/{parts} parts right' in html


def test_pre_clock_agreement_and_begin(student, app, mod):
    aid = _start(student, 'A1', 'sprint', 'exam')
    _i, att = _att(app, mod, aid)
    assert json.loads(att.domains)['_pre'] == 20 * 60
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    for s in ('id="esAgreement"', 'Candidate Agreement &amp; Exam Instructions', 'I Agree — Start Exam Clock', '220-1201',
              'data-pre="1"', '20 minutes', 'Passing score', '675', 'class="es-pre"'):
        assert s in html, s
    with app.app_context():       # time spent reading the rules does not count
        a = mod.db.session.get(mod.ExamSimAttempt, aid)
        a.started_at, a.deadline = a.started_at - timedelta(minutes=19), a.deadline - timedelta(minutes=19)
        mod.db.session.commit()
    j = student.post(f'{BASE}/{aid}/begin', headers={'Accept': 'application/json'}).get_json()
    assert 1190 <= j['remaining'] <= 1200
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    assert 'id="esAgreement"' not in html and 'data-pre="0"' in html


def test_direct_post_without_begin_starts_the_clock(student, app, mod):
    aid = _start(student, 'N', 'sprint', 'exam')
    items, _a = _att(app, mod, aid)
    student.post(f'{BASE}/{aid}', data=_form_for(items, 15))
    _i, att = _att(app, mod, aid)
    assert att.correct == 15 and att.score == 900 and not att.timed_out and '_pre' not in (att.domains or '')


def _user_id(app, mod, email):
    with app.app_context():
        return mod.User.query.filter_by(email=email).first().id


def test_ada_extended_time_accommodation(student, instructor, app, mod):
    uid = _user_id(app, mod, 'student1@lms.local')
    page = instructor.get('/instructor/section/1/exam-sim').get_data(as_text=True)
    assert 'Time Accommodations (ADA / Section 504)' in page and '1.5× Time-and-a-half' in page and '2.0× Double time' in page
    r = instructor.post('/instructor/section/1/exam-sim/accommodation', data={'user_id': uid, 'multiplier': '1.5'})
    assert r.status_code == 302
    assert student.post('/instructor/section/1/exam-sim/accommodation', data={'user_id': uid, 'multiplier': '2.0'}).status_code == 403
    assert instructor.post('/instructor/section/1/exam-sim/accommodation', data={'user_id': uid, 'multiplier': '3'}).status_code == 400
    home = student.get(BASE).get_data(as_text=True)
    assert '1.5× time accommodation applied — 135 min' in home
    aid = _start(student, 'N', 'full')
    _i, att = _att(app, mod, aid)
    assert json.loads(att.domains)['_pre'] == 135 * 60
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    assert '1.5× time accommodation applied — 135 min' in html and '135 minutes' in html
    instructor.post('/instructor/section/1/exam-sim/accommodation', data={'user_id': uid, 'multiplier': '1.0'})
    assert 'time accommodation applied' not in student.get(BASE).get_data(as_text=True)
    from privacy_tools import plan
    with app.app_context():
        _doomed, _null, tables = plan(mod.db, uid)
    assert 'exam_sim_accommodation' in str(tables) and 'exam_sim_grade' in str(tables)


def test_csv_export_and_gradebook_sync(student, instructor, app, mod):
    aid = _start(student, 'A2', 'sprint')
    items, _a = _att(app, mod, aid)
    student.post(f'{BASE}/{aid}', data=_form_for(items, 15))
    r = instructor.get('/instructor/section/1/exam-sim/export.csv')
    assert r.status_code == 200 and r.mimetype == 'text/csv'
    body = r.get_data(as_text=True)
    assert body.splitlines()[0].startswith('student,email,exam,exam_code') and '220-1202' in body and 'VOUCHER READY' in body
    assert student.get('/instructor/section/1/exam-sim/export.csv').status_code == 403
    page = instructor.get('/instructor/section/1/exam-sim').get_data(as_text=True)
    assert 'Export Scores CSV' in page and 'Sync Latest Exam-Sim Scores to Gradebook / LTI' in page
    r = instructor.post('/instructor/section/1/exam-sim/sync-gradebook')
    assert r.status_code == 302
    G = app.extensions['ciwt_exam_sim'].Grade
    with app.app_context():
        g = G.query.filter_by(section_id=1, user_id=_user_id(app, mod, 'student1@lms.local'), exam='A2').first()
        assert g and g.score == 900 and g.pct == 100.0 and g.status == 'VOUCHER READY'
    assert 'Last synced' in instructor.get('/instructor/section/1/exam-sim').get_data(as_text=True)


def test_mastery_why_and_portfolio_integration(student, instructor, app, mod):
    uid = _user_id(app, mod, 'student1@lms.local')
    aid = _start(student, 'A1', 'sprint')
    items, _a = _att(app, mod, aid)
    student.post(f'{BASE}/{aid}', data={})                     # nothing answered → remediation, every domain weak
    # mastery engine counts exam-sim answers (weight 0.85) — answer a second sitting fully
    from mastery.model import WEIGHTS
    assert WEIGHTS['exam_sim'] == 0.85
    aid2 = _start(student, 'A1', 'sprint')
    items2, _a = _att(app, mod, aid2)
    student.post(f'{BASE}/{aid2}', data=_form_for(items2, 15))
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        user = mod.db.session.get(mod.User, uid)
        st = app.extensions['ciwt_mastery'].engine.student_state(sec, user, log=False)
    assert st['sources'].get('exam_sim', 0) >= 1
    assert any(o.get('kind') == 'exam_sim' for evs in st['evidence'].values() for o in evs)
    # why: latest sitting is ready (aid2); make the failing one latest to check the remediation signal
    with app.app_context():
        a = mod.db.session.get(mod.ExamSimAttempt, aid)
        a.submitted_at = a.submitted_at + timedelta(days=1)
        mod.db.session.commit()
        from mastery.why import why
        with app.test_request_context():
            w = why(app, mod.db, mod.db.session.get(mod.ClassSection, 1), mod.db.session.get(mod.User, uid))
    assert any('Exam Sim (220-1201): 100/900 · Needs remediation (weak:' in p for p in w['pills']['exam_sim'])
    assert any(s['text'].startswith('Exam Sim 220-1201') for s in w['stuck'])
    assert any(a['kind'] == 'exam_sim' and f'/exam-sim/{aid}/result' in a['url'] for a in w['actions'])
    assert w['severity'] >= 3
    r = instructor.get(f'{BASE}/{aid}/result')
    assert r.status_code == 200 and 'Candidate Score Report' in r.get_data(as_text=True)
    # portfolio: best ready sitting per exam + OpenBadges assertion
    html = student.get('/portfolio').get_data(as_text=True)
    assert 'Exam-Day Simulator sittings' in html and 'VOUCHER READY' in html and '220-1201' in html
    j = json.loads(student.get('/portfolio/export.json').get_data(as_text=True))
    assert any(a['badge']['name'].startswith('VOUCHER READY: CompTIA A+ Core 1') for a in j['assertions'])
    assert j['portfolio']['exam_sittings']


# ------------------------------------------------------------------ Option B pass 6
def test_sim_pbqs_map_to_curated_course_objectives():
    from curriculum_v2.cert.mapping import CURATED
    from curriculum_v2.cert.tech_plus import TECH_OBJECTIVES
    assert len(SIM.SIMS) == 36
    for s in SIM.SIMS:
        if s['oid'].startswith('T:'):
            assert s['obj'] in TECH_OBJECTIVES[s['oid']]['course_objs'], s['id']
        else:
            assert s['oid'] in CURATED.get(s['obj'], ()), s['id']
    for it in SIM.items():
        assert it['obj'] in CURATED and it['raw']['obj'] == it['obj']


def test_sim_pbq_remediation_links_exact_r1_ladder_section(app):
    from curriculum_v2 import ladder as LD
    lad = LD.ladder()
    api = app.extensions['ciwt_exam_sim']
    hit = 0
    with app.test_request_context():
        for s in SIM.SIMS:
            links = api.remediation(s['oid'], s['obj'], 1)
            assert links, s['id']
            for ln in links:
                if 'rung_url' not in ln:
                    continue
                assert 'rung=R1' in ln['rung_url']
                sid = ln['rung_url'].rsplit('#ladder-', 1)[1]
                objs = [v.get('obj') for k, v in lad.items() if k[2] == sid]
                if s['obj'] in objs:
                    hit += 1
    assert hit >= 1


def test_sim_pbq_answers_record_mastery_on_mapped_objective(student, app, mod):
    aid = _start(student, 'N', 'max')
    items, _a = _att(app, mod, aid)
    sims = [(i, iid) for i, (iid, _o) in enumerate(items) if P.bank()[iid]['type'] == 'sim_pbq']
    assert sims
    student.post(f'{BASE}/{aid}', data=_form_for(items, len(items)))
    uid = _user_id(app, mod, 'student1@lms.local')
    with app.app_context():
        st = app.extensions['ciwt_mastery'].engine.student_state(
            mod.db.session.get(mod.ClassSection, 1), mod.db.session.get(mod.User, uid), log=False)
    want = {P.bank()[iid]['obj'] for _i, iid in sims}
    got = {o for o, evs in st['evidence'].items() if any(e.get('kind') == 'exam_sim' for e in evs)}
    assert want & got


def test_gradebook_shows_synced_exam_sim_without_changing_grade(student, instructor, app, mod):
    before = instructor.get('/instructor/section/1/gradebook.csv').get_data(as_text=True)
    aid = _start(student, 'A2', 'sprint')
    items, _a = _att(app, mod, aid)
    student.post(f'{BASE}/{aid}', data=_form_for(items, 15))
    instructor.post('/instructor/section/1/exam-sim/sync-gradebook')
    html = instructor.get('/instructor/section/1/gradebook').get_data(as_text=True)
    assert 'Exam Sim' in html and '220-1202: 900/900 (VOUCHER READY)' in html
    csv_after = instructor.get('/instructor/section/1/gradebook.csv').get_data(as_text=True)
    head = csv_after.splitlines()[0]
    assert 'Exam-Day Simulator 220-1202' in head and '900/900 100% VOUCHER READY' in csv_after
    # weighted course grade unchanged: first columns of each row identical
    strip = lambda t: [ln.split(',')[:4] for ln in t.splitlines()[1:]]
    assert strip(before) == strip(csv_after)
    page = student.get('/student/section/1/grades').get_data(as_text=True)
    assert 'Exam-Day Simulator' in page and '900/900 (VOUCHER READY)' in page


def test_outcomes_exam_sim_metrics(student, instructor, admin, app, mod):
    from institutional import outcomes as OC
    aid = _start(student, 'A2', 'sprint')
    items, _a = _att(app, mod, aid)
    student.post(f'{BASE}/{aid}', data=_form_for(items, 15))
    with app.app_context():
        es = OC.exam_sim_summary(app, [1], {_user_id(app, mod, 'student1@lms.local')})
    a2 = next(x for x in es['exams'] if x['exam'] == 'A2')
    assert a2['attempts'] >= 1 and a2['candidates'] == 1 and a2['voucher_ready'] == 1
    assert a2['voucher_ready_pct'] == 100.0 and a2['mean_score'] == 900
    assert {'A1', 'A2', 'N'} <= {x['exam'] for x in es['exams']} and es['overall']['attempts'] >= 1
    html = instructor.get('/instructor/section/1/outcomes').get_data(as_text=True)
    assert 'Exam-Day Simulator &amp; Voucher Readiness' in html and 'id="ocExamSim"' in html
    assert admin.get('/admin/outcomes').status_code == 200
    body = instructor.get('/instructor/section/1/outcomes?format=csv').get_data(as_text=True)
    assert 'exam_sim_voucher_ready_pct,220-1202' in body and 'exam_sim_mean_scaled_score' in body
    j = json.loads(instructor.get('/instructor/section/1/outcomes?format=json').get_data(as_text=True))
    assert j['exam_sim']['overall']['voucher_ready'] >= 1


def test_option_shuffle_deterministic_per_attempt(app):
    qv = app.extensions['ciwt_exam_sim'].question_view
    b = P.bank()
    iid, it = next((k, v) for k, v in b.items() if v['type'] == 'single' and len(v['options']) >= 4)
    from curriculum_v2.cert.exams import OBJECTIVES
    oid = next(iter(OBJECTIVES))
    with app.test_request_context():
        a1 = qv(it, oid, 0, attempt_id=7)['options']
        a2 = qv(it, oid, 0, attempt_id=7)['options']
        orders = {tuple(qv(it, oid, 0, attempt_id=n)['options']) for n in range(1, 30)}
        base = qv(it, oid, 0)['options']
    assert a1 == a2 and sorted(a1) == sorted(base) and len(orders) > 1


def test_keyboard_shortcut_hint_and_script(student):
    aid = _start(student, 'N', 'sprint')
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    assert 'id="esKeys"' in html and 'Prev/Next' in html and 'Whiteboard' in html
    js = open('static/js/exam_sim.js').read()
    assert "'ArrowRight'" in js and "tag === 'textarea'" in js and '[1-6]' in js


def test_landing_page_pillars(anon):
    html = anon.get('/landing').get_data(as_text=True)
    assert 'What Sets Novak LMS™ Apart' in html
    for s in ('539 bespoke', '90 labs', 'Diagnose → Fix → Verify', 'VOUCHER READY', '98-card Speed-Drill',
              'Who Needs Me', 'LTI 1.3 Advantage', 'SAML 2.0', 'WCAG 2.1 AA', 'FERPA', 'novakornothing@gmail.com'):
        assert s in html, s


# ------------------------------------------------------------------ pass 7 audit fixes
def test_every_sim_pbq_first_remediation_link_is_its_own_ladder_section(app):
    from curriculum_v2 import ladder as LD
    lad = LD.ladder()
    api = app.extensions['ciwt_exam_sim']
    with app.test_request_context():
        for s in SIM.SIMS:
            links = api.remediation(s['oid'], s['obj'], 1)
            assert links and 'rung=R1' in links[0]['rung_url'], s['id']
            code, ch, lo = P.lesson_ref(links[0]['ref'])
            sid = links[0]['rung_url'].rsplit('#ladder-', 1)[1]
            assert lad[(code, f'{ch}.{lo}', sid)].get('obj') == s['obj'], (s['id'], links[0])


def test_outcomes_exam_sim_ignores_drill_unsubmitted_and_empty(student, app, mod):
    from institutional import outcomes as OC
    uid = _user_id(app, mod, 'student1@lms.local')
    with app.app_context():
        empty = OC.exam_sim_summary(app, [1], set())
    assert empty['overall'] == {**empty['overall'], 'attempts': 0, 'candidates': 0, 'voucher_ready': 0,
                                'voucher_ready_pct': None, 'mean_score': None}
    aid = _start(student, 'N', 'sprint')                       # left unsubmitted
    aid2 = _start(student, 'N', 'sprint')
    items, _a = _att(app, mod, aid2)
    student.post(f'{BASE}/{aid2}', data=_form_for(items, 15))  # 900, ready
    aid3 = _start(student, 'N', 'sprint')
    student.post(f'{BASE}/{aid3}', data={})                    # latest: 100, not ready
    r = student.post(f'{BASE}/{aid3}/remediate-drill')
    did = int(re.search(r'/exam-sim/(\d+)', r.headers['Location']).group(1))
    student.post(f'{BASE}/{did}', data={})                     # drill sitting excluded
    with app.app_context():
        n = next(x for x in OC.exam_sim_summary(app, [1], {uid})['exams'] if x['exam'] == 'N')
        A = app.extensions['ciwt_exam_sim'].Attempt
        subs = A.query.filter(A.section_id == 1, A.user_id == uid, A.exam == 'N', A.mode != 'drill',
                              A.submitted_at.isnot(None)).count()
    assert n['attempts'] == subs and n['voucher_ready'] == 1 and n['mean_score'] == 100   # best → ready; latest → mean
    assert aid not in () and 'best sitting' in n['basis']


def test_drill_from_sim_only_misses_still_builds(student, app, mod):
    aid = _start(student, 'A2', 'max')
    items, _a = _att(app, mod, aid)
    b = P.bank()
    data = _form_for(items, len(items))
    for i, (iid, _o) in enumerate(items):                       # miss only the simulation PBQs
        if b[iid]['type'] == 'sim_pbq':
            for k in [k for k in data if k == f'q{i}' or k.startswith(f'q{i}_')]:
                data.pop(k)
    student.post(f'{BASE}/{aid}', data=data)
    r = student.post(f'{BASE}/{aid}/remediate-drill')
    assert r.status_code == 302 and '/exam-sim/' in r.headers['Location'] and 'result' not in r.headers['Location']
    did = int(re.search(r'/exam-sim/(\d+)', r.headers['Location']).group(1))
    ditems, d = _att(app, mod, did)
    sim_oids = {o for iid, o in items if b[iid]['type'] == 'sim_pbq'}
    assert d.mode == 'drill' and ditems and {o for _i, o in ditems} <= sim_oids
    assert all(b[i]['type'] in ('single', 'multi') for i, _o in ditems)
    html = student.get(f'{BASE}/{did}').get_data(as_text=True)
    assert 'data-pre="1"' in html and 'id="esKeys"' in html     # drill also waits for the agreement, shortcuts present


def test_speed_drill_keyboard_and_live_regions(student):
    html = student.get('/student/section/1/speed-drill').get_data(as_text=True)
    assert 'id="sdKeys"' in html and 'id="sdFeedback" role="status" aria-live="polite"' in html
    assert 'id="speedDrill" data-seconds' in html and html.count('aria-live') == 2
    js = open('static/js/speed_drill.js').read()
    assert "if (!running) return;      // the Blitz clock" in js and "'keydown'" in js
    assert 'speed-drill' in student.get('/student/section/1').get_data(as_text=True)


# ------------------------------------------------------------------ pre-push fixes
def test_sync_skips_students_no_longer_enrolled(student, instructor, app, mod):
    aid = _start(student, 'N', 'sprint')
    items, _a = _att(app, mod, aid)
    student.post(f'{BASE}/{aid}', data=_form_for(items, 15))
    uid = _user_id(app, mod, 'student1@lms.local')
    G = app.extensions['ciwt_exam_sim'].Grade
    with app.app_context():
        e = mod.Enrollment.query.filter_by(section_id=1, user_id=uid).first()
        G.query.filter_by(section_id=1, user_id=uid).delete()
        mod.db.session.delete(e)
        mod.db.session.commit()
    try:
        instructor.post('/instructor/section/1/exam-sim/sync-gradebook')
        with app.app_context():
            assert G.query.filter_by(section_id=1, user_id=uid).count() == 0
    finally:
        with app.app_context():
            mod.db.session.add(mod.Enrollment(section_id=1, user_id=uid))
            mod.db.session.commit()


def test_strikeouts_persist_by_option_text_and_hint_matches_keys(student):
    js = open('static/js/exam_sim.js').read()
    assert "'esStrike:' + root.dataset.attempt" in js and "inp.name + '|' + inp.value" in js
    aid = _start(student, 'N', 'sprint')
    html = student.get(f'{BASE}/{aid}').get_data(as_text=True)
    assert '<kbd>1</kbd>–<kbd>6</kbd> Select' in html
