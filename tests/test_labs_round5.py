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
