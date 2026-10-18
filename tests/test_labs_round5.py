"""Labs round 5: phone terminals (real-VM and simulated) stay usable with the on-screen keyboard open.

Regressions covered:
- focus mode at 390 px inherited the phone `.term-body` min-height 240px / max-height 50vh (ciwt-ui.css), so with the
  keyboard open the keys row (and Check) were squashed or pushed under the keyboard, and with it closed ~160 px sat
  unused; now the output area flexes and the chips row drops while the keyboard is open
- the Check key sat past the right edge of the keys row (8th key); Check and Hint are now in the first six
- hints and check results only reached the side panel / a 3.5 s toast while the terminal covered the screen; they now
  show inside the terminal (#termNote) with every message
- tapping ↵ took focus from the input, which closes a phone keyboard after every command
- the empty, "hidden" toast peeked out at the top of the full-screen terminal; the toast was capped at 50vw wide
The browser checks run on a live server over the throwaway test DB and need no VM boot."""
import re
import socket
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'static/css/labs.css').read_text()


def _keys(html):
    m = re.search(r'<div class="term-keys"[^>]*>(.*?)</div>', html, re.S)
    return re.findall(r'data-key-act="(\w+)"', m.group(1))


def test_vm_page_has_in_terminal_note_and_onscreen_check_and_hint(student):
    html = student.get('/labs/linux-vm-routing').get_data(as_text=True)
    assert html.index('id="termNote"') < html.index('id="termForm"')
    keys = _keys(html)
    assert 'check' in keys[:6] and 'hint' in keys[:6], keys


def test_sim_terminal_page_has_hint_key_and_note(student):
    html = student.get('/labs/win-dns-break').get_data(as_text=True)
    assert 'id="termNote"' in html and 'hint' in _keys(html)


def test_css_focus_mode_overrides_the_phone_min_and_max_height():
    rule = re.search(r'\.term-wrap\.term-focus \.term-body \{([^}]*)\}', CSS).group(1)
    assert 'min-height: 0' in rule and 'max-height: none' in rule
    assert re.search(r'\.term-wrap\.term-focus\.term-short \.term-chips \{ display: none', CSS)
    assert re.search(r'\.lab-toast:not\(\.show\) \{ visibility: hidden', CSS)
    assert 'width: max-content' in re.search(r'\.lab-toast \{([^}]*)\}', CSS).group(1)


def _chromium():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            return Path(p.chromium.executable_path).exists()
    except Exception:
        return False


@pytest.fixture(scope='module')
def live(app):
    from werkzeug.serving import make_server
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    srv = make_server('127.0.0.1', port, app, threaded=True)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f'http://127.0.0.1:{port}'
    srv.shutdown()


GEOM = """()=>{const v=visualViewport.height,W=document.documentElement.clientWidth;
  const r=s=>{const n=document.querySelector(s);if(!n)return null;const b=n.getBoundingClientRect();return b.height>0&&b.top>=-1&&b.bottom<=v+1&&b.left>=-1&&b.right<=W+1};
  const body=document.querySelector('.vm-screen:not([hidden])')||document.getElementById('termBody');
  return {focus:document.getElementById('termWrap').classList.contains('term-focus'),form:r('#termForm'),send:r('#termForm .term-send'),
    hint:r('[data-key-act=hint]'),check:document.querySelector('[data-key-act=check]')?r('[data-key-act=check]'):true,
    body:Math.round(body.getBoundingClientRect().height),chips:getComputedStyle(document.querySelector('.term-chips')).display,
    toastVisible:getComputedStyle(document.getElementById('labToast')).visibility}}"""


@pytest.mark.skipif(not _chromium(), reason='Playwright Chromium not installed')
@pytest.mark.parametrize('lab_id', ['win-dns-break', 'linux-vm-routing'])
def test_phone_terminal_with_keyboard_open(live, lab_id):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        pg.goto(live + '/login')
        pg.fill('input[name=email]', 'student3@lms.local')
        pg.fill('input[name=password]', 'student123')
        pg.click('button[type=submit]')
        pg.wait_for_load_state()
        pg.goto(f'{live}/labs/{lab_id}')
        if lab_id.startswith('linux-vm'):   # layout only: show the console without booting v86
            assert not pg.is_visible('#vmCheck'), 'Check my work is shown before the VM has booted'
            pg.evaluate("document.getElementById('termWrap').hidden=false")
        pg.tap('#termInput')
        g = pg.evaluate(GEOM)
        assert g['focus'] and g['body'] > 500, g                # keyboard closed: the output fills the screen
        assert g['toastVisible'] == 'hidden', g                 # no empty toast peeking out
        for h in (470, 420, 380):                               # on-screen keyboard open (iPhone with accessory bar ≈ 420)
            pg.set_viewport_size({'width': 390, 'height': h})
            pg.wait_for_timeout(150)
            g = pg.evaluate(GEOM)
            assert g['form'] and g['send'] and g['hint'] and g['check'], (h, g)
            assert g['body'] >= 120 and g['chips'] == 'none', (h, g)
        pg.tap('[data-key-act=hint]')
        pg.wait_for_selector('#termNote:not([hidden])')
        assert 'Hint' in pg.inner_text('#termNote')
        pg.tap('#termNoteX')
        assert pg.locator('#termNote:not([hidden])').count() == 0
        assert pg.evaluate("document.activeElement.id") == 'termInput'
        if lab_id == 'win-dns-break':                           # ↵ keeps the keyboard (focus) and runs the command
            pg.keyboard.type('ipconfig')
            with pg.expect_response(lambda r: '/cmd' in r.url):
                pg.tap('#termForm .term-send')
            assert pg.evaluate("document.activeElement.id") == 'termInput'
            assert 'ipconfig' in pg.inner_text('#termBody')
        b.close()


# ------------------------------------------------------------------ round 5 lab: troubleshooting methodology (ITSUP 7)
import json  # noqa: E402

import interactive_labs as IL  # noqa: E402
import lab_runtime as RT  # noqa: E402
import labs_vm as V  # noqa: E402
from curriculum_v2.objectives import OBJECTIVES  # noqa: E402

METHOD = 'linux-vm-method'


def _grade(lab, cmds):
    st = V.fresh(lab, 7)
    V.record_commands(st, cmds)
    _, _, done = V.grade(lab, st, [], V.solved_probes(st, lab), booted=True)
    return done


def test_method_lab_registered_mapped_tagged_and_has_fallbacks():
    lab = RT.get_lab(METHOD)
    assert lab and lab['kind'] == 'vm' and METHOD in V.VM_BY_ID
    assert lab.get('review') == IL.SME_PENDING
    assert all(o in OBJECTIVES for o in lab['course_objectives']) and 'IT-7.1' in lab['course_objectives']
    assert METHOD in IL.CHAPTER_LABS.get(('ITSUP', 7), []), 'mapped to the thin chapter ITSUP 7'
    assert set(lab['obj_hints']) == {o['id'] for o in lab['objectives']}
    assert all(len(h) == 2 and all(x.strip() for x in h) for h in lab['obj_hints'].values())
    assert lab['fallback'] and all(RT.get_lab(f) and RT.get_lab(f)['kind'] != 'vm' for f in lab['fallback'])
    json.dumps(lab['vm']), json.dumps(lab['vm_checks'])


def test_method_solution_earns_everything_and_empty_only_boot():
    lab = V.VM_BY_ID[METHOD]
    assert sorted(_grade(lab, lab['solution']['vm_commands'])) == sorted(o['id'] for o in lab['objectives'])
    _, _, done = V.grade(lab, V.fresh(lab, 7), [], {}, booted=True)
    assert done in ([], ['boot'])


def test_method_order_is_graded():
    lab = V.VM_BY_ID[METHOD]
    sol = lab['solution']['vm_commands']
    edit = next(c for c in sol if c.startswith('sed -i'))
    # fixing first, then going through the motions: identify / domain / theory / test are not earned
    done = _grade(lab, [edit] + [c for c in sol if c != edit])
    assert not {'identify', 'domain', 'theory', 'test'} & set(done), done
    assert {'fix', 'document'} <= set(done)
    # testing before writing the theory does not count as testing the theory
    th = next(c for c in sol if 'theory=' in c)
    tests_first = [c for c in sol if c != th]
    i = tests_first.index(edit)
    done = _grade(lab, tests_first[:i] + [th] + tests_first[i:])
    assert 'theory' in done and 'test' not in done
    # copying the settings to the backup is not an edit (identify still counts); writing into the live file is
    assert 'identify' in _grade(lab, ['cp /etc/default/timeclock /etc/default/timeclock.bak'] + sol)
    assert 'identify' not in _grade(lab, ["echo DOCROOT=/srv/timeclock >> /etc/default/timeclock"] + sol)
    # verify needs a page load after the restart
    no_curl_after = [c for c in sol if not c.startswith('curl -s -o') and 'grep -o' not in c]
    assert 'verify' not in _grade(lab, no_curl_after)


def test_method_answers_hashed_not_in_probe():
    lab = V.VM_BY_ID[METHOD]
    probe = V.probe_script(V.fresh(lab, 1), lab)
    assert 'domain=service' not in probe and 'cause=docroot' not in probe.lower()


def test_method_page_and_http_flow(student, instructor):
    lab = RT.get_lab(METHOD)
    page = student.get(f'/labs/{METHOD}').data.decode()
    assert 'Pending SME review' not in page and all(f'/labs/{f}' in page for f in lab['fallback'])
    assert 'Pending SME review' in instructor.get(f'/labs/{METHOD}').data.decode()
    assert f'/labs/{METHOD}' in student.get('/labs/ticket-method').data.decode()   # the simulator links its real twin
    student.post(f'/labs/{METHOD}/reset')
    import app as lms
    api = lms.app.extensions['ciwt_lab_progress']
    with lms.app.app_context():
        u = lms.User.query.filter_by(email='student1@lms.local').first()
        st = json.loads(api.LabProgress.query.filter_by(user_id=u.id, lab_id=METHOD).first().state_json)
    student.post(f'/labs/{METHOD}/vm-log', json={'lines': [], 'booted': True, 'boot_ms': 1})
    student.post(f'/labs/{METHOD}/vm-log', json={'lines': lab['solution']['vm_commands']})
    r = student.post(f'/labs/{METHOD}/vm-check', json={'probes': V.solved_probes(st, lab)}).get_json()
    assert r['complete'] and r['score'] == 100, r
