"""Option B pass 1: stateful command fallbacks, packet-flow visualiser, hardware bench, Exam-Day Readiness Simulator."""
import copy
import json
import random
import re

import pytest

import interactive_labs as IL
import stateful_sim as SS
from curriculum_v2.cert import exam_sim as ES
from curriculum_v2.cert import practice as P
from mastery import lab_diagnosis as LDX


def _run(lab, cmds):
    state, done, r = None, [], None
    for c in cmds:
        r, state, done = IL.run_command(lab, state, done, c)
    return r, state, done


def _text(r):
    return '\n'.join(r.get('lines') or [])


# ------------------------------------------------------------------ 1. stateful command engine
def test_windows_fallbacks_use_live_state():
    r, st, _ = _run('win-ipconfig', ['whoami /priv'])
    assert 'SeShutdownPrivilege' in _text(r) or 'Privilege Name' in _text(r)
    r, st, _ = _run('win-ipconfig', ['Test-NetConnection 8.8.8.8'])
    assert 'PingSucceeded' in _text(r) and 'not recognized' not in _text(r)
    ok = (st.get('pingable_ips') or [None])[0]
    if ok:
        r, _s, _d = IL.run_command('win-ipconfig', st, [], f'tnc {ok}')
        assert 'PingSucceeded          : True' in _text(r)
    r, _s, _d = IL.run_command('win-ipconfig', st, [], 'tnc 8.8.8.8 -Port 443')
    assert 'TcpTestSucceeded' in _text(r)


@pytest.mark.parametrize('cmd', ['show ip route', 'show access-lists', 'show arp', 'show cdp neighbors',
                                 'show startup-config', 'traceroute 10.0.0.1'])
def test_switch_show_commands_answer(cmd):
    r, _s, _d = _run('sw-vlan-access', ['enable', cmd])
    assert '% Invalid' not in _text(r) and '% Unrecognized' not in _text(r)


def test_switch_startup_config_tracks_write_memory():
    r, st, d = _run('sw-hostname-write', ['enable', 'configure terminal', 'hostname EXAMSW', 'end', 'write memory',
                                         'show startup-config'])
    assert 'hostname EXAMSW' in _text(r)
    assert st.get('startup_cfg')


def test_router_cdp_and_every_ios_lab_answers_show_commands():
    for lab in IL.LABS:
        if lab.get('kind') not in ('switch', 'router'):
            continue
        r, _s, _d = _run(lab['id'], ['enable', 'show running-config'])
        assert '% Invalid' not in _text(r), lab['id']
        r, _s, _d = _run(lab['id'], ['enable', 'show cdp neighbors'])
        assert 'Device ID' in _text(r), lab['id']


@pytest.mark.parametrize('cmd,phase', [
    ('Test-NetConnection 10.0.0.1', 'diagnose'), ('tnc 8.8.8.8 -Port 443', 'diagnose'),
    ('whoami /priv', 'diagnose'), ('Resolve-DnsName example.com', 'diagnose'),
    ('netsh interface ip show config', 'diagnose'), ('show cdp neighbors', 'diagnose'), ('do show vlan brief', 'diagnose'),
    ('netsh interface ip set dns "Ethernet" static 8.8.8.8', 'change'),
])
def test_diagnostic_commands_are_look_check(cmd, phase):
    e = {'kind': 'cmd', 'action': cmd, 'outcome': 'ok'}
    assert LDX.phase_of(e) == phase


# ------------------------------------------------------------------ 2. packet-flow visualiser
def test_packet_flow_stops_at_failing_hop_for_every_lab():
    n = 0
    for lab in IL.LABS:
        if not SS.has_packet_flow(lab):
            continue
        for ptype in ('arp', 'icmp', 'dns', 'https'):
            r = SS.packet_flow(lab, copy.deepcopy(lab.get('initial_state') or {}), [], ptype)
            fails = [h for h in r['hops'] if not h['ok']]
            assert len(fails) <= 1 and r['ok'] == (not fails), (lab['id'], ptype)
            if fails:
                assert r['hops'][-1] is fails[0]        # the walk stops where the packet dies
            n += 1
    assert n > 100


def test_packet_flow_tracks_the_live_fault():
    lab = IL.get_lab('sw-vlan-access')
    _r, st, done = _run('sw-vlan-access', ['enable'])
    before = SS.packet_flow(lab, st, done, 'icmp')
    st2 = copy.deepcopy(st)
    for ifc in (st2.get('interfaces') or {}).values():
        ifc['up'] = False
    after = SS.packet_flow(lab, st2, done, 'icmp')
    assert not after['ok'] and after['hops'][-1]['ok'] is False
    assert before != after


def test_packet_flow_route_and_panel(student):
    r = student.get('/labs/sw-vlan-access/packet-flow?type=arp')
    assert r.status_code == 200
    j = r.get_json()
    assert j['type'] == 'arp' and j['hops'] and 'summary' in j
    assert student.get('/labs/sw-vlan-access/packet-flow?type=bogus').status_code in (200, 400)
    html = student.get('/labs/sw-vlan-access').get_data(as_text=True)
    assert 'id="packetFlow"' in html and 'Trace Packet Flow' in html and 'packet_flow.js' in html
    for t in ('arp', 'icmp', 'dns', 'https'):
        assert f'value="{t}"' in html


# ------------------------------------------------------------------ 3. hardware / cable bench
@pytest.mark.parametrize('lab_id,mode', [('hw-board', 'board'), ('hw-pc-build', 'board'), ('hw-cables', 'cable')])
def test_hw_bench_on_hardware_labs(student, lab_id, mode):
    html = student.get(f'/labs/{lab_id}').get_data(as_text=True)
    assert 'id="hwBench"' in html and f'data-mode="{mode}"' in html and 'hw_bench.js' in html
    assert 'style=' not in html.split('id="hwBench"')[1].split('</section>')[0]


def test_hw_bench_assets():
    js = open('static/js/hw_bench.js').read()
    for word in ('T568A', 'T568B', 'crossover', 'straight', 'split'):
        assert word.lower() in js.lower()
    assert 'packet' in open('static/js/packet_flow.js').read().lower()


# ------------------------------------------------------------------ 4. Exam-Day Readiness Simulator
def test_scaling_and_badges():
    assert ES.scaled(0, 45) == 100 and ES.scaled(45, 45) == 900 and ES.scaled(0, 0) == 100
    assert ES.PASS_SCORE == {'A1': 675, 'A2': 700, 'N': 720, 'S': 750, 'T': 650}
    assert ES.readiness(800, 'N', [80, 90]) == 'ready'
    assert ES.readiness(800, 'N', [80, 40]) == 'borderline'
    assert ES.readiness(690, 'N', [70]) == 'borderline'
    assert ES.readiness(400, 'A1', [30]) == 'remediate'
    assert ES.BADGES['borderline'] == 'Borderline — review flagged domains'


@pytest.mark.parametrize('exam', ['A1', 'A2', 'N'])
@pytest.mark.parametrize('mode', ['full', 'sprint'])
def test_build_form_pbqs_first(exam, mode):
    items = ES.build_form(exam, mode, random.Random(7))
    m, b = ES.MODES[mode], P.bank()
    assert len(items) == m['questions'] and len({i for i, _o in items}) == len(items)
    types = [b[i]['type'] for i, _o in items]
    assert all(t in ES.PBQ_TYPES for t in types[:m['pbqs']])
    assert not any(t in ES.PBQ_TYPES for t in types[m['pbqs']:])
    assert all(o.startswith(exam + ':') for _i, o in items)


def _answer_form(att_items, right=True, flag=()):
    b, data = P.bank(), {}
    for i, (iid, _o) in enumerate(att_items):
        it = b[iid]
        if i in flag:
            data[f'flag{i}'] = '1'
        if not right:
            continue
        if it['type'] == 'single':
            data[f'q{i}'] = it['correct']
        elif it['type'] == 'multi':
            data[f'q{i}'] = list(it['correct'])
        else:
            for k, v in enumerate(it['correct']):
                data[f'q{i}_{k}'] = v
    return data


def test_student_sitting_end_to_end(student, instructor, app, mod):
    home = student.get('/student/section/1').get_data(as_text=True)
    assert '/student/section/1/exam-sim' in home
    html = student.get('/student/section/1/exam-sim').get_data(as_text=True)
    assert 'Practice Exams' in html and '220-1201' in html and '220-1202' in html and 'N10-009' in html
    r = student.post('/student/section/1/exam-sim/start', data={'exam': 'N', 'mode': 'sprint', 'timing': 'practice'})
    assert r.status_code == 302
    take_url = r.headers['Location']
    att_id = int(re.search(r'/exam-sim/(\d+)', take_url).group(1))
    page = student.get(take_url).get_data(as_text=True)
    assert 'Skip Hands-On Challenges &amp; return later' in page and 'id="esPause"' in page and 'Flag for review' in page
    assert 'Answered' in page and 'Unanswered' in page and 'Flagged' in page and 'exam_sim.js' in page
    assert page.count('class="card card-body mb-3 es-q') == 15 and page.count('es-q es-pbq') == 2
    assert page.index('es-pbq') < page.index('es-q"')
    with app.app_context():
        att = mod.db.session.get(mod.ExamSimAttempt, att_id)
        items = json.loads(att.items)
    data = _answer_form(items, right=True, flag=(0, 3))
    r = student.post(take_url, data=data)
    assert r.status_code == 302 and r.headers['Location'].endswith('/result')
    res = student.get(r.headers['Location']).get_data(as_text=True)
    assert '>900<' in res and 'Ready to sit' in res and 'pass bar 720' in res and 'Flagged' in res
    with app.app_context():
        att = mod.db.session.get(mod.ExamSimAttempt, att_id)
        assert att.score == 900 and att.badge == 'ready' and json.loads(att.flags) == [0, 3]
    # strict exam mode, nothing answered -> remediation with lesson + ladder rung links, no pause button
    r = student.post('/student/section/1/exam-sim/start', data={'exam': 'A1', 'mode': 'sprint', 'timing': 'exam'})
    take_url = r.headers['Location']
    page = student.get(take_url).get_data(as_text=True)
    assert 'id="esPause"' not in page and 'data-strict="1"' in page
    r = student.post(take_url, data={})
    res = student.get(r.headers['Location']).get_data(as_text=True)
    assert '>100<' in res and 'Needs remediation' in res and 'pass bar 675' in res
    assert re.search(r'href="/student/section/1/lesson/\d+\?', res) and 'rung=R1' in res and 'Ladder rung R1' in res
    # instructor visibility
    ih = instructor.get('/instructor/section/1/exam-sim')
    assert ih.status_code == 200
    ih = ih.get_data(as_text=True)
    assert 'Ready to sit: ' in ih and 'Needs remediation' in ih and 'Network+' in ih


def test_exam_sim_access_control(student, student2, anon, app, mod):
    r = student.post('/student/section/1/exam-sim/start', data={'exam': 'A2', 'mode': 'full', 'timing': 'practice'})
    url = r.headers['Location']
    page = student.get(url).get_data(as_text=True)
    assert page.count('es-q es-pbq') == 4 and page.count('class="card card-body mb-3 es-q') == 45
    assert student2.get(url).status_code in (403, 404)
    assert student.post('/student/section/1/exam-sim/start', data={'exam': 'X', 'mode': 'full'}).status_code == 400
    assert student.get('/instructor/section/1/exam-sim').status_code == 403
    assert anon.get('/student/section/1/exam-sim').status_code in (302, 401)


def test_strict_mode_rejects_late_answers(student, app, mod):
    r = student.post('/student/section/1/exam-sim/start', data={'exam': 'A2', 'mode': 'sprint', 'timing': 'exam'})
    url = r.headers['Location']
    att_id = int(re.search(r'/exam-sim/(\d+)', url).group(1))
    from datetime import timedelta
    with app.app_context():
        att = mod.db.session.get(mod.ExamSimAttempt, att_id)
        att.deadline = att.started_at - timedelta(minutes=5)
        items = json.loads(att.items)
        mod.db.session.commit()
    student.post(url, data=_answer_form(items))
    with app.app_context():
        att = mod.db.session.get(mod.ExamSimAttempt, att_id)
        assert att.timed_out and att.score == 100
