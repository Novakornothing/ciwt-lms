"""Round 5: direct keys (vi, less, top) on a phone — 390×844, touch, typed through the on-screen keyboard's input.

Before round 5, "Keys: direct" focused the console <div>, which opens no on-screen keyboard, so phones could not use
vi. Now the input stays and forwards every key. This boots one real VM, then in direct mode: echo with a Backspace
correction, edits a file in BusyBox vi (i, text, the Esc key from the keys bar, :wq), checks the line was logged,
and back in line mode reads the file.
usage: python tools/vm_keys_e2e.py [--base URL] [--lab linux-vm-perms] [--cpu 4]
"""
import argparse
import json
import sys
import time

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--base', default='http://127.0.0.1:5191')
ap.add_argument('--lab', default='linux-vm-perms')
ap.add_argument('--user', default='student3@lms.local')
ap.add_argument('--cpu', type=float, default=4)
a = ap.parse_args()
SCREEN = "()=>document.querySelector('.vm-screen:not([hidden])').innerText"
IDLE = ("()=>{const l=[...document.querySelectorAll('.vm-screen:not([hidden]) .ln')];return l.length>0&&/[#%$] $/.test(l[l.length-1].textContent)}")
out = {'lab': a.lab, 'cpu': a.cpu, 'steps': {}}
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    pg = ctx.new_page()
    logged = []
    pg.on('request', lambda r: logged.append(r.post_data or '') if r.method == 'POST' and 'vm-log' in r.url else None)
    pg.goto(a.base + '/login')
    pg.fill('input[name=email]', a.user)
    pg.fill('input[name=password]', 'student123')
    pg.click('button[type=submit]')
    pg.wait_for_load_state()
    pg.goto(f'{a.base}/labs/{a.lab}')
    ctx.new_cdp_session(pg).send('Emulation.setCPUThrottlingRate', {'rate': a.cpu})
    t = time.time()
    pg.tap('#vmBoot')
    pg.wait_for_selector('#vmTools:not([hidden])', timeout=600000)
    out['boot_s'] = round(time.time() - t, 1)
    pg.tap('#termInput')
    pg.tap('#vmRaw')
    ok = True

    def step(name, fn):
        global ok
        try:
            fn()
            out['steps'][name] = 'ok'
        except Exception as e:
            ok = False
            out['steps'][name] = 'FAIL ' + str(e)[:160]
        print(name, out['steps'][name], flush=True)

    def direct_echo():
        assert pg.is_visible('#termForm'), 'input hidden in direct mode'
        assert pg.evaluate("document.activeElement.id") == 'termInput'
        pg.keyboard.type('echo abX')
        pg.keyboard.press('Backspace')
        pg.keyboard.type('c-direct')
        pg.keyboard.press('Enter')
        pg.wait_for_function("()=>/\\nabc-direct\\n/.test(document.querySelector('.vm-screen:not([hidden])').innerText)", timeout=30000)

    def direct_vi():
        pg.wait_for_function(IDLE, timeout=30000)
        pg.keyboard.type('vi /tmp/r5-phone.txt')
        pg.keyboard.press('Enter')
        pg.wait_for_timeout(1500)
        pg.keyboard.type('ihello from a phone')
        pg.wait_for_timeout(300)
        pg.tap('[data-key-act=esc]')
        pg.wait_for_timeout(700)           # vi reads ESC followed at once by ':' as an Alt-key sequence (a person pauses)
        pg.keyboard.type(':wq')
        pg.tap('#termForm .term-send')     # ↵ button sends Enter in direct mode
        pg.wait_for_function(IDLE, timeout=30000)

    def logged_line():
        pg.wait_for_timeout(600)
        assert any('echo abc-direct' in x for x in logged), 'direct-mode line not logged: ' + json.dumps(logged)[:200]

    def back_to_line():
        pg.tap('#vmRaw')
        assert pg.inner_text('#termPrompt') != 'keys'
        pg.keyboard.type('cat /tmp/r5-phone.txt')
        pg.keyboard.press('Enter')
        pg.wait_for_function("()=>/\\nhello from a phone\\n/.test(document.querySelector('.vm-screen:not([hidden])').innerText)", timeout=30000)

    step('direct echo + backspace', direct_echo)
    step('direct vi edit (i, Esc key, :wq)', direct_vi)
    step('direct line logged', logged_line)
    step('line mode reads the file', back_to_line)
    pg.screenshot(path='/tmp/vm_keys_e2e.png')
    b.close()
print(json.dumps(out))
sys.exit(0 if ok else 1)
