"""Live-labs end-to-end: complete every lab through the real UI as a student, at desktop and phone emulation
(optionally tablet), then check the records: lab_progress score 100 + completed_at, a lab_completion row,
reload resumes with every objective ticked, no horizontal overflow, and the instructor sees it (lab results,
per-student transcript, gradebook Labs column). Classroom labs (CL-*) are signed off by the instructor in the UI.

usage: python tools/labs_e2e.py [--base http://127.0.0.1:5191] [--db labs_dev.db] [--only regex]
                                [--views desktop,phone,tablet] [--shots DIR] [--json out.json] [--cpu 4] [--touch]
--touch (round 5): on the phone view, terminals are driven as a phone user would (see --help); per-lab boot time,
page-reported boot, probe time and layout measurements go into the JSON.
The DB must be the one the server at --base uses (it is read, never written, by this script).
"""
import argparse
import json
import re
import sqlite3
from types import SimpleNamespace
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import interactive_labs as IL  # noqa: E402
import lab_runtime as RT  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--base', default='http://127.0.0.1:5191')
ap.add_argument('--db', default=str(ROOT / 'labs_dev.db'))
ap.add_argument('--only', default='')
ap.add_argument('--views', default='desktop,phone')
ap.add_argument('--shots', default='')
ap.add_argument('--json', default='')
ap.add_argument('--cpu', type=float, default=0, help='CPU throttle for the student page (CDP; 4 = mid-range phone)')
ap.add_argument('--touch', action='store_true',
                help='round 5, phone view: drive terminals as a phone user (tap, type key by key, ↵ button, on-screen '
                     'keyboard simulated by shrinking the viewport to --kb-height), use the in-terminal Hint and Check '
                     'keys, and fail the lab on any layout problem (input/keys under the keyboard, tiny font, page scroll)')
ap.add_argument('--kb-height', type=int, default=420, help='viewport height while the on-screen keyboard is "open"')
a = ap.parse_args()

VIEWS = {  # name: (viewport, mobile/touch, student)
    'desktop': ({'width': 1280, 'height': 800}, False, 'student1@lms.local'),   # round 4: 1280x800 (was 1440x900)
    'phone': ({'width': 390, 'height': 844}, True, 'student2@lms.local'),
    'tablet': ({'width': 820, 'height': 1180}, True, 'student3@lms.local'),
}
PW = 'student123'
TERM_KINDS = {'windows', 'switch', 'router', 'ticket', 'linux'}
CUR_METRICS = {}
TOUCH = {'on': False}   # set per view: --touch and the phone view


def _tap(page, sel, **kw):
    """tap on the phone view with --touch (real touch events), click otherwise"""
    if TOUCH['on']:
        page.locator(sel).first.scroll_into_view_if_needed()
        return page.tap(sel, **kw)
    return page.click(sel, **kw)


def _lt(loc):
    return loc.tap() if TOUCH['on'] else loc.click()


def db():
    c = sqlite3.connect(a.db, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def uid_of(email):
    with db() as c:
        return c.execute('select id from user where email=?', (email,)).fetchone()['id']


def progress(uid, lab_id):
    with db() as c:
        return c.execute('select * from lab_progress where user_id=? and lab_id=?', (uid, lab_id)).fetchone()


def completion(uid, lab_id):
    with db() as c:
        return c.execute('select * from lab_completion where user_id=? and lab_id=?', (uid, lab_id)).fetchone()


def login(page, email, pw):
    page.goto(a.base + '/login')
    page.fill('input[name=email]', email)
    page.fill('input[name=password]', pw)
    page.click('button[type=submit]')
    page.wait_for_load_state()


OVERFLOW = "()=>{const W=document.documentElement.clientWidth;return document.documentElement.scrollWidth>W+1?document.documentElement.scrollWidth-W:0}"


def wait_post(page, path_part, fn, timeout=15000):
    with page.expect_response(lambda r: path_part in r.url and r.request.method == 'POST', timeout=timeout) as info:
        fn()
    r = info.value
    assert r.status == 200, (path_part, r.status)
    page.wait_for_timeout(60)
    return r.json()


def touch_long_press(page, sel):
    page.eval_on_selector(sel, """(n)=>{const r=n.getBoundingClientRect();const o={pointerType:'touch',clientX:r.left+r.width/2,clientY:r.top+r.height/2,bubbles:true,pointerId:7};
      n.dispatchEvent(new PointerEvent('pointerdown',o));}""")
    page.wait_for_timeout(700)
    page.eval_on_selector(sel, "(n)=>n.dispatchEvent(new PointerEvent('pointerup',{pointerType:'touch',bubbles:true,pointerId:7}))")
    page.wait_for_selector('#w11Ctx:not([hidden])', timeout=3000)


def touch_drag(page, src, dst):
    page.evaluate("""([s,d])=>{const a=document.querySelector(s),b=document.querySelector(d);const ra=a.getBoundingClientRect(),rb=b.getBoundingClientRect();
      const p=(t,x,y,n)=>n.dispatchEvent(new PointerEvent(t,{pointerType:'touch',clientX:x,clientY:y,bubbles:true,pointerId:9,cancelable:true}));
      const ax=ra.left+ra.width/2,ay=ra.top+ra.height/2,bx=rb.left+rb.width/2,by=rb.top+rb.height/2;
      p('pointerdown',ax,ay,a);for(let i=1;i<=6;i++)p('pointermove',ax+(bx-ax)*i/6,ay+(by-ay)*i/6,document);p('pointerup',bx,by,document);}""", [src, dst])
    page.wait_for_timeout(120)


# ---------------------------------------------------------------- per-kind drivers
def drive_terminal(page, lab, view, notes):
    sol = lab.get('solution') or {}
    cmds = sol.get('commands')
    if cmds is None and lab['id'] in IL.VERIFY_SEQUENCES:
        cmds = IL.VERIFY_SEQUENCES[lab['id']][0]
    inp = page.locator('#termInput')
    fs = float(inp.evaluate("n=>parseFloat(getComputedStyle(n).fontSize)"))
    if view != 'desktop' and fs < 16:
        notes.append(f'input font {fs}px < 16 (iOS zoom)')
    for i, c in enumerate(cmds or []):
        inp.click()
        inp.fill(c)
        if view == 'phone' and i == 0:
            # submit the first command with the on-screen ↵ button (keys bar path), the rest with Enter
            wait_post(page, '/cmd', lambda: page.click('#termForm button[type=submit]'))
            if not page.evaluate("document.getElementById('termWrap').classList.contains('term-focus')"):
                notes.append('focus mode did not engage on phone')
        else:
            wait_post(page, '/cmd', lambda: inp.press('Enter'))


def gui_open(page, app, view):
    if view == 'desktop':
        ic = page.locator(f'#w11Desk [data-app="{app}"]')
        try:
            wait_post(page, '/event', lambda: ic.click(timeout=2000))
            return
        except Exception:
            pass
    key = {'settings': 'settings', 'services': 'services', 'devmgr': 'devmgmt', 'ncpa': 'ncpa', 'aduc': 'dsa'}[app]
    _tap(page, '#w11StartBtn')
    page.fill('#w11Search', key)
    wait_post(page, '/event', lambda: _tap(page, f'#w11StartList [data-start="{app}"]'))


def gui_user(page, ad_users, sam):
    ou = next((u['ou'] for u in ad_users if u['sam'] == sam), None)
    for _ in range(10):   # the state fetch can race the previous event's save
        if ou:
            break
        page.wait_for_timeout(300)
        st = page.evaluate("()=>fetch(LabKit.config().urls.state).then(r=>r.json())")
        ou = next((u['ou'] for u in st['gui']['ad']['users'] if u['sam'] == sam), None)
    assert ou, f'AD user {sam} not found in the lab state'
    _tap(page, f'[data-ou="{ou}"]')
    _tap(page, f'[data-user="{sam}"]')


def drive_gui(page, lab, view, notes):
    events = (lab.get('solution') or {}).get('events') or RT._default_events(lab)
    for ev, data in events:
        st = page.evaluate("()=>fetch(LabKit.config().urls.state).then(r=>r.json())")
        users = ((st.get('gui') or {}).get('ad') or {}).get('users') or []
        if ev.startswith('open:'):
            gui_open(page, ev[5:], view)
        elif ev.startswith('pane:'):
            row = page.locator(f'.w11-row[data-ev="{ev}"]')
            if row.count() and row.first.is_visible():
                wait_post(page, '/event', lambda: _lt(row.first))
            else:
                lbl = {'home': 'Home', 'system': 'System', 'network': 'Network & internet', 'accounts': 'Accounts', 'update': 'Windows Update'}[ev[5:]]
                wait_post(page, '/event', lambda: _lt(page.locator('.w11-nav-item', has_text=lbl).first))
        elif ev.startswith('adapter:'):
            if page.locator('#w11AdapterToggle').count():
                wait_post(page, '/event', lambda: _tap(page, '#w11AdapterToggle'))
            else:
                if view == 'desktop':
                    page.click('#w11Adapter', button='right')
                else:
                    touch_long_press(page, '#w11Adapter')
                lbl = 'Disable' if ev.endswith('disable') else 'Enable'
                wait_post(page, '/event', lambda: _lt(page.locator('#w11Ctx .w11-ctx-item', has_text=lbl)))
        elif ev.startswith('svc:'):
            wait_post(page, '/event', lambda: _tap(page, f'[data-svc="{ev[4:]}"]'))
        elif ev.startswith('dev:'):
            wait_post(page, '/event', lambda: _tap(page, f'[data-dev="{ev[4:]}"]'))
        elif ev == 'update:check':
            wait_post(page, '/event', lambda: _tap(page, '#w11CheckUpdates'))
        elif ev == 'ad:create':
            _tap(page, f'[data-ou="{data["ou"]}"]')
            _tap(page, '#adNewUser')
            page.fill('#nuFirst', data['first']); page.fill('#nuLast', data['last']); page.fill('#nuSam', data['sam'])
            page.fill('#nuPw', data['password']); page.fill('#nuPw2', data['confirm'])
            page.set_checked('#nuMust', bool(data.get('must_change')))
            wait_post(page, '/event', lambda: _tap(page, '#dlgOk'))
        elif ev == 'ad:addgroup':
            gui_user(page, users, data['sam'])
            _tap(page, '[data-act="group"]')
            page.select_option('#grpSel', data['group'])
            wait_post(page, '/event', lambda: _tap(page, '#dlgOk'))
        elif ev in ('ad:unlock', 'ad:disable', 'ad:enable'):
            gui_user(page, users, data['sam'])
            act = ev[3:]
            if view != 'desktop':
                touch_long_press(page, f'[data-user="{data["sam"]}"]')
                lbl = {'unlock': 'Unlock account', 'disable': 'Disable account', 'enable': 'Enable account'}[act]
                wait_post(page, '/event', lambda: _lt(page.locator('#w11Ctx .w11-ctx-item', has_text=lbl)))
            else:
                wait_post(page, '/event', lambda: _tap(page, f'[data-act="{act}"]'))
        elif ev == 'ad:reset':
            gui_user(page, users, data['sam'])
            _tap(page, '[data-act="reset"]')
            page.fill('#rpPw', data['password']); page.fill('#rpPw2', data['confirm'])
            page.set_checked('#rpMust', bool(data.get('must_change')))
            wait_post(page, '/event', lambda: _tap(page, '#dlgOk'))
        else:
            raise AssertionError('no UI driver for event ' + ev)
        if page.locator('.w11-window .w11-status').count():
            err = page.locator('.w11-window .w11-status').first.inner_text().strip()
            if err and 'error' in err.lower():
                notes.append(f'{ev}: {err}')


def drive_vm(page, lab, view, notes):
    """Real VM(s): boot v86 in the page, type the commands into the real shells (switching machine tabs), Check my work."""
    import re as _re
    t = time.time()
    page.click('#vmBoot')
    page.wait_for_selector('#vmTools:not([hidden])', timeout=300000)
    notes.append(f'VM boot {time.time() - t:.1f}s' + (f" ×{len(lab['vm']['machines'])}" if len(lab['vm']['machines']) > 1 else ''))
    last_ln = ("()=>{const s=document.querySelector('.vm-screen:not([hidden])');if(!s)return false;"
               "const l=[...s.querySelectorAll('.ln')];return l.length>0&&/([#%$] |assword: ?|\\(yes\\/no[^)]*\\)\\? ?)$/.test(l[l.length-1].textContent)}")
    first = lab['vm']['machines'][0]['name']
    cur = first
    for c in lab['solution']['vm_commands']:
        m = _re.match(r'^\[(\w+)\] (.*)$', c)
        mach, cmd = (m.group(1), m.group(2)) if m else (first, c)
        if mach != cur:
            tab = page.locator(f'#vmTab-{mach}')
            if page.locator('#termWrap.term-focus').count():
                tab.scroll_into_view_if_needed()
            tab.click()
            cur = mach
        page.wait_for_function(last_ln, timeout=60000)
        page.fill('#termInput', cmd)
        page.press('#termInput', 'Enter')
        page.wait_for_timeout(80)
        page.wait_for_function(last_ln, timeout=180000)   # some steps really wait (cron: sleep 75)
    if lab['vm'].get('net'):
        page.click('#vmTab-_packets')
        n = page.locator('#vmPackets .pk').count()
        notes.append(f'{n} packets')
        if not n:
            raise AssertionError('Packets panel is empty')
        if a.shots:
            page.screenshot(path=f"{a.shots}/{lab['id']}-{view}-packets.png", full_page=False)
        page.click(f'#vmTab-{first}')
    page.wait_for_timeout(400)   # let the batched command log post
    sel = '[data-key-act="check"]' if page.locator('#termWrap.term-focus').count() else '#vmCheck'
    r = wait_post(page, '/vm-check', lambda: page.click(sel), timeout=60000)
    if not r['complete']:
        raise AssertionError('VM check not complete: ' + '; '.join(r['result'].get('messages') or [r['result'].get('error') or '']))
    if page.locator('#termWrap.term-focus').count():
        page.click('#btnFocusExit')



# ---------------------------------------------------------------- round 5: phone-realistic terminal driving (--touch)
LAYOUT = """(kbh)=>{const r=s=>{const n=document.querySelector(s);if(!n||!n.offsetParent&&getComputedStyle(n).position!=='fixed')return null;const b=n.getBoundingClientRect();return {l:b.left,r:b.right,t:b.top,b:b.bottom,h:b.height}};
  const W=document.documentElement.clientWidth,H=window.visualViewport?visualViewport.height:innerHeight,p=[];
  const wrap=document.getElementById('termWrap');const focus=wrap&&wrap.classList.contains('term-focus');
  const body=document.querySelector('.vm-screen:not([hidden])')||document.getElementById('termBody');
  const bb=body&&body.getBoundingClientRect();const fs=body?parseFloat(getComputedStyle(body).fontSize):0;
  const inp=document.getElementById('termInput');const ifs=inp?parseFloat(getComputedStyle(inp).fontSize):0;
  const within=(x,name)=>{if(!x){p.push(name+' not visible');return}if(x.b>H+1||x.t<-1||x.r>W+1||x.l<-1)p.push(name+' off screen ('+Math.round(x.l)+','+Math.round(x.t)+'-'+Math.round(x.r)+','+Math.round(x.b)+' in '+W+'x'+Math.round(H)+')')};
  if(!focus)p.push('focus mode not engaged');
  within(r('#termForm'),'input row');within(r('#termForm .term-send'),'send button');
  if(document.querySelector('[data-key-act=check]'))within(r('[data-key-act=check]'),'Check key');
  if(document.querySelector('[data-key-act=hint]'))within(r('[data-key-act=hint]'),'Hint key');
  if(bb&&bb.height<120)p.push('terminal output only '+Math.round(bb.height)+'px tall');
  if(fs<13)p.push('terminal font '+fs+'px');if(ifs<16)p.push('input font '+ifs+'px (iOS zooms)');
  if(document.documentElement.scrollWidth>W+1)p.push('page scrolls sideways '+(document.documentElement.scrollWidth-W)+'px');
  return {problems:p,vvh:Math.round(H),body_h:bb?Math.round(bb.height):0,font:fs,input_font:ifs}}"""


def kb_open(page, view, notes, metrics):
    """the input is focused: shrink the viewport to the keyboard-open height and measure the full-screen terminal"""
    if view != 'phone':
        return
    page.set_viewport_size({'width': VIEWS[view][0]['width'], 'height': a.kb_height})
    page.wait_for_timeout(250)
    m = page.evaluate(LAYOUT, a.kb_height)
    metrics['layout_kb'] = m
    for pr in m['problems']:
        notes.append('LAYOUT ' + pr)


def kb_close(page, view):
    if view == 'phone':
        page.set_viewport_size(VIEWS[view][0])
        page.wait_for_timeout(150)


def touch_hint(page, notes):
    """the Hint key in the terminal: the hint must appear inside the full-screen terminal, then close with ×"""
    if not page.locator('[data-key-act=hint]').count():
        notes.append('LAYOUT no Hint key in the terminal')
        return
    wait_post(page, '/hint', lambda: page.tap('[data-key-act=hint]'))
    try:
        page.wait_for_selector('#termNote:not([hidden])', timeout=3000)
        txt = page.inner_text('#termNote').strip()
        if 'Hint' not in txt or len(txt) < 12:
            notes.append('LAYOUT hint note empty: ' + txt[:60])
    except Exception:
        notes.append('LAYOUT hint not shown inside the terminal')
        return
    page.tap('#termNoteX')
    if page.locator('#termNote:not([hidden])').count():
        notes.append('LAYOUT hint note did not close')
    if page.evaluate("document.activeElement && document.activeElement.id") != 'termInput':
        notes.append('LAYOUT input lost focus after closing the hint (keyboard would close)')


def type_line(page, text, i):
    """type key by key into the focused input; submit with the ↵ button (odd lines) or Enter (even lines)"""
    page.keyboard.type(text)
    if i % 2:
        page.tap('#termForm .term-send')
    else:
        page.keyboard.press('Enter')


def drive_terminal_touch(page, lab, view, notes, metrics):
    sol = lab.get('solution') or {}
    cmds = sol.get('commands')
    if cmds is None and lab['id'] in IL.VERIFY_SEQUENCES:
        cmds = IL.VERIFY_SEQUENCES[lab['id']][0]
    page.tap('#termInput')
    kb_open(page, view, notes, metrics)
    touch_hint(page, notes)
    for i, c in enumerate(cmds or []):
        if page.evaluate("document.activeElement && document.activeElement.id") != 'termInput':
            notes.append(f'LAYOUT input not focused before command {i + 1} (keyboard closed)')
            page.tap('#termInput')
        wait_post(page, '/cmd', lambda: type_line(page, c, i))
    kb_close(page, view)
    if page.locator('#termWrap.term-focus').count():
        page.tap('#btnFocusExit')


def drive_vm_touch(page, lab, view, notes, metrics):
    import re as _re
    page.evaluate("()=>new Promise(r=>{const q=indexedDB.deleteDatabase('ciwt-vm');q.onsuccess=q.onerror=q.onblocked=()=>r()})")
    t = time.time()
    page.tap('#vmBoot')
    page.wait_for_selector('#vmTools:not([hidden])', timeout=600000)
    metrics['boot_s'] = round(time.time() - t, 1)
    pr = re.search(r'boot ([\d.]+) s', page.inner_text('#vmPerf'))
    metrics['boot_page_s'] = float(pr.group(1)) if pr else None
    notes.append(f"VM boot {metrics['boot_s']}s (page {metrics['boot_page_s']}s)" + (f" ×{len(lab['vm']['machines'])}" if len(lab['vm']['machines']) > 1 else ''))
    last_ln = ("()=>{const s=document.querySelector('.vm-screen:not([hidden])');if(!s)return false;"
               "const l=[...s.querySelectorAll('.ln')];return l.length>0&&/([#%$] |assword: ?|\\(yes\\/no[^)]*\\)\\? ?)$/.test(l[l.length-1].textContent)}")
    page.tap('#termInput')
    kb_open(page, view, notes, metrics)
    touch_hint(page, notes)
    first = lab['vm']['machines'][0]['name']
    cur = first
    for i, c in enumerate(lab['solution']['vm_commands']):
        m = _re.match(r'^\[(\w+)\] (.*)$', c)
        mach, cmd = (m.group(1), m.group(2)) if m else (first, c)
        if mach != cur:
            tab = page.locator(f'#vmTab-{mach}')
            tab.scroll_into_view_if_needed()
            tab.tap()
            cur = mach
        page.wait_for_function(last_ln, timeout=60000)
        if page.evaluate("document.activeElement && document.activeElement.id") != 'termInput':
            page.tap('#termInput')
        type_line(page, cmd, i)
        page.wait_for_timeout(80)
        page.wait_for_function(last_ln, timeout=240000)
    if lab['vm'].get('net'):
        page.locator('#vmTab-_packets').tap()
        n = page.locator('#vmPackets .pk').count()
        notes.append(f'{n} packets')
        if not n:
            raise AssertionError('Packets panel is empty')
        page.locator(f'#vmTab-{first}').tap()
    page.wait_for_timeout(400)
    t1 = time.time()
    r = wait_post(page, '/vm-check', lambda: page.tap('[data-key-act="check"]'), timeout=120000)
    metrics['check_s'] = round(time.time() - t1, 1)
    if not r['complete']:
        raise AssertionError('VM check not complete: ' + '; '.join(r['result'].get('messages') or [r['result'].get('error') or '']))
    try:
        page.wait_for_selector('#termNote.ok:not([hidden])', timeout=3000)
    except Exception:
        notes.append('LAYOUT check result not shown inside the terminal')
    kb_close(page, view)
    page.tap('#btnFocusExit')

def server_state(uid, lab_id):
    row = progress(uid, lab_id)
    return json.loads(row['state_json']) if row and row['state_json'] else {}


def drive_steps(page, lab, view, uid, notes):
    sol = (lab.get('solution') or {}).get('answers') or {}
    st = server_state(uid, lab['id'])
    if callable(sol):
        sol = sol(st)
    dragged = False
    for step in lab.get('steps') or []:
        ans = sol.get(step['id'])
        if callable(ans):
            ans = ans(st)
        sid = step['id']
        card = f'[data-step="{sid}"]'
        page.locator(card).scroll_into_view_if_needed()
        t = step['type']
        if t == 'choice':
            for i in (ans if isinstance(ans, list) else [ans]):
                _tap(page, f'label[for="ch-{sid}-{i}"]')
        elif t == 'order':
            for i, want in enumerate(ans):
                cur = page.eval_on_selector_all(f'{card} .lab-order-item', 'ns=>ns.map(n=>n.getAttribute("data-key"))')
                j = cur.index(want)
                for _ in range(j - i):
                    _lt(page.locator(f'{card} .lab-order-item[data-key="{want}"] .lab-mv').first)
            got = page.eval_on_selector_all(f'{card} .lab-order-item', 'ns=>ns.map(n=>n.getAttribute("data-key"))')
            assert got == list(ans), ('order', got, ans)
        elif t == 'match':
            for item, zone in ans.items():
                if view != 'desktop' and not dragged:
                    touch_drag(page, f'{card} [data-item="{item}"]', f'{card} [data-zone="{zone}"] .lab-zone-btn')
                    dragged = True
                    if not page.locator(f'{card} [data-zone="{zone}"] [data-item="{item}"]').count():
                        notes.append('touch drag did not place the item; used tap')
                    else:
                        continue
                _tap(page, f'{card} .lab-pool [data-item="{item}"], {card} .lab-zone [data-item="{item}"]')
                _tap(page, f'{card} [data-zone="{zone}"] .lab-zone-btn')
        elif t == 'fields':
            for k, v in ans.items():
                page.fill(f'#f-{sid}-{k}', str(v))
        elif t == 'config':
            for f in step['fields']:
                k = f['name']
                if k not in ans:
                    continue
                v = ans[k]
                sel = f'#c-{sid}-{k}'
                if f.get('kind') == 'select':
                    page.select_option(sel, str(v))
                elif f.get('kind') == 'toggle':
                    page.set_checked(sel, v == 'on')
                else:
                    page.fill(sel, str(v))
        elif t == 'build':
            for k, v in ans.items():
                page.select_option(f'#b-{sid}-{k}', v)
        else:
            raise AssertionError('no UI driver for step type ' + t)
        r = wait_post(page, '/check', lambda: _tap(page, f'#chk-{sid}'))
        if not r['result']['correct']:
            raise AssertionError(f'step {sid} rejected: {r["result"].get("message")}')


# ---------------------------------------------------------------- one lab at one view
def run_lab(page, lab, view, email, shots):
    uid = uid_of(email)
    notes = []
    t0 = time.time()
    page.goto(f"{a.base}/labs/{lab['id']}")
    page.wait_for_selector('#labObjectives')
    # start clean through the UI: Start over (confirm) reloads the page
    page.once('dialog', lambda d: d.accept())
    with page.expect_navigation(timeout=15000):
        page.click('#btnReset')
    page.wait_for_selector('#labObjectives')
    row = progress(uid, lab['id'])
    assert row and (row['score'] or 0) == 0, 'reset did not clear score'
    k = lab['kind']
    metrics = CUR_METRICS
    metrics.clear()
    touch = a.touch and view == 'phone'
    if k in TERM_KINDS:
        (drive_terminal_touch if touch else drive_terminal)(*((page, lab, view, notes, metrics) if touch else (page, lab, view, notes)))
    elif k == 'win11gui':
        drive_gui(page, lab, view, notes)
    elif k == 'vm':
        (drive_vm_touch if touch else drive_vm)(*((page, lab, view, notes, metrics) if touch else (page, lab, view, notes)))
    if lab.get('steps'):
        drive_steps(page, lab, view, uid, notes)
    page.wait_for_selector('#labSuccess:not([hidden])', timeout=5000)
    ov = page.evaluate(OVERFLOW)
    if ov:
        notes.append(f'horizontal overflow {ov}px')
    if shots:
        page.screenshot(path=f"{shots}/{lab['id']}-{view}.png", full_page=False)
    row = progress(uid, lab['id'])
    assert row['score'] == 100 and row['completed_at'], ('progress', row['score'], row['completed_at'])
    assert completion(uid, lab['id']) is not None, 'no lab_completion row'
    page.reload()
    page.wait_for_selector('#labObjectives')
    n_done = page.locator('#labObjectives [data-oid].done').count()
    total = page.locator('#labObjectives [data-oid]').count()
    assert n_done == total, f'resume: {n_done}/{total} ticked after reload'
    assert page.locator('#labSuccess:not([hidden])').count() == 1, 'resume: success banner missing'
    if k in TERM_KINDS and page.locator('#termBody .ln').count() == 0 and page.locator('#termBody').inner_text().strip() == '':
        notes.append('transcript not restored')
    bad = [n for n in notes if n.startswith('LAYOUT')]
    if touch and bad:
        raise AssertionError('; '.join(bad))
    return {'lab': lab['id'], 'kind': k, 'view': view, 'ok': True, 'secs': round(time.time() - t0, 1), 'notes': notes, **metrics}


def run_classroom(inst_page, stu_page, cl, view, email):
    uid = uid_of(email)
    inst_page.goto(f'{a.base}/instructor/section/1/labs/results?lab={cl}#signoff')
    inst_page.select_option('#soLab', cl)
    inst_page.select_option('#soUser', str(uid))
    for ci, lv in enumerate([4, 4, 3, 4]):
        inst_page.check(f'#soc{ci}l{lv}')
    inst_page.fill('#soFb', f'e2e sign-off {view}')
    with inst_page.expect_navigation():
        inst_page.click('#soSave')
    row = progress(uid, cl)
    assert row and row['score'] == 93.8 or abs((row['score'] or 0) - 93.75) < 0.1, ('classroom score', row and row['score'])
    assert row['completed_at'] and row['graded_by']
    stu_page.goto(f'{a.base}/labs/classroom/{cl}')
    body = stu_page.locator('main').inner_text()
    assert '15/16' in body and f'e2e sign-off {view}' in body, 'student does not see sign-off'
    ov = stu_page.evaluate(OVERFLOW)
    return {'lab': cl, 'kind': 'classroom', 'view': view, 'ok': True, 'secs': 0, 'notes': [f'horizontal overflow {ov}px'] if ov else []}


def instructor_checks(page, emails, labs_done):
    out = []
    page.goto(f'{a.base}/instructor/section/1/labs/results')
    html = page.content()
    for e in emails:
        uid = uid_of(e)
        for lid in labs_done[:3]:
            page.goto(f'{a.base}/instructor/section/1/labs/student/{uid}/{lid}')
            ok = page.locator('main').inner_text().count('100') > 0
            out.append(('detail', e, lid, ok))
    page.goto(f'{a.base}/instructor/section/1/gradebook')
    gb = page.content()
    out.append(('gradebook-labs-column', 'Labs' in gb, ''))
    resp = page.request.get(f'{a.base}/instructor/section/1/labs/results.csv')
    csvt = resp.text()
    with db() as c:   # the CSV lists the labs of section 1's course only
        code = c.execute('select c.code from class_section s join course c on c.id=s.course_id where s.id=1').fetchone()['code']
    in_course = {l['id'] for l in RT.course_lab_set(SimpleNamespace(code=code))}
    want = [l for l in labs_done if l in in_course][:5]
    out.append(('csv', resp.status == 200 and all(l in csvt for l in want), ''))
    out.append(('results-page', 'Lab results' in html, ''))
    return out


def main():
    labs = [l for l in IL.LABS if not a.only or re.search(a.only, l['id'])]
    cls = [c for c in RT.classroom_ids() if not a.only or re.search(a.only, c)]
    if a.shots:
        Path(a.shots).mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        ictx = b.new_context(viewport={'width': 1280, 'height': 900})
        ipage = ictx.new_page()
        login(ipage, 'instructor@lms.local', 'teach123')
        for view in a.views.split(','):
            vp, mobile, email = VIEWS[view]
            ctx = b.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, device_scale_factor=2 if mobile else 1)
            TOUCH['on'] = a.touch and view == 'phone'
            page = ctx.new_page()
            if a.cpu:
                ctx.new_cdp_session(page).send('Emulation.setCPUThrottlingRate', {'rate': a.cpu})
            errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            login(page, email, PW)
            for lab in labs:
                errs.clear()
                try:
                    r = run_lab(page, lab, view, email, a.shots)
                except Exception as e:  # keep going: report every lab
                    import traceback
                    r = {'lab': lab['id'], 'kind': lab['kind'], 'view': view, 'ok': False,
                         'error': (str(e) or type(e).__name__ + ' ' + traceback.format_exc().splitlines()[-3].strip())[:300], 'notes': [], **CUR_METRICS}
                    if a.shots:
                        page.screenshot(path=f"{a.shots}/FAIL-{lab['id']}-{view}.png")
                if errs:
                    r['ok'] = False
                    r.setdefault('error', 'JS error: ' + errs[0][:200])
                results.append(r)
                print(('PASS' if r['ok'] else 'FAIL'), view, lab['id'], r.get('error', ''), '; '.join(r['notes']), flush=True)
            for cl in cls:
                try:
                    r = run_classroom(ipage, page, cl, view, email)
                except Exception as e:
                    r = {'lab': cl, 'kind': 'classroom', 'view': view, 'ok': False, 'error': str(e)[:300], 'notes': []}
                results.append(r)
                print(('PASS' if r['ok'] else 'FAIL'), view, cl, r.get('error', ''), '; '.join(r['notes']), flush=True)
            ctx.close()
        done = [r['lab'] for r in results if r['ok'] and r['kind'] != 'classroom']
        emails = [VIEWS[v][2] for v in a.views.split(',')]
        for chk in instructor_checks(ipage, emails, done):
            ok = chk[-1] if chk[0] == 'detail' else chk[1]
            print(('PASS' if ok else 'FAIL'), 'instructor', *[str(x) for x in chk[:-1] if not isinstance(x, bool)], flush=True)
            results.append({'lab': 'instructor:' + chk[0], 'view': 'instructor', 'ok': bool(ok), 'notes': []})
        b.close()
    bad = [r for r in results if not r['ok']]
    print(f'\n{len(results) - len(bad)}/{len(results)} passed')
    if a.json:
        Path(a.json).write_text(json.dumps(results, indent=1))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
