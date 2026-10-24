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
    assert att.timed_out and att.correct == 5 and att.score == ES.scaled(5, 15)


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
