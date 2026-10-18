"""Live-labs end-to-end: complete every lab through the real UI as a student, at desktop and phone emulation
(optionally tablet), then check the records: lab_progress score 100 + completed_at, a lab_completion row,
reload resumes with every objective ticked, no horizontal overflow, and the instructor sees it (lab results,
per-student transcript, gradebook Labs column). Classroom labs (CL-*) are signed off by the instructor in the UI.

usage: python tools/labs_e2e.py [--base http://127.0.0.1:5191] [--db labs_dev.db] [--only regex]
                                [--views desktop,phone,tablet] [--shots DIR] [--json out.json]
The DB must be the one the server at --base uses (it is read, never written, by this script).
"""
import argparse
import json
import re
import sqlite3
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
a = ap.parse_args()

VIEWS = {  # name: (viewport, mobile/touch, student)
    'desktop': ({'width': 1440, 'height': 900}, False, 'student1@lms.local'),
    'phone': ({'width': 390, 'height': 844}, True, 'student2@lms.local'),
    'tablet': ({'width': 820, 'height': 1180}, True, 'student3@lms.local'),
}
PW = 'student123'
TERM_KINDS = {'windows', 'switch', 'router', 'ticket', 'linux'}


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
    page.click('#w11StartBtn')
    page.fill('#w11Search', key)
    wait_post(page, '/event', lambda: page.click(f'#w11StartList [data-start="{app}"]'))


def gui_user(page, ad_users, sam):
    ou = next((u['ou'] for u in ad_users if u['sam'] == sam), None)
    for _ in range(10):   # the state fetch can race the previous event's save
        if ou:
            break
        page.wait_for_timeout(300)
        st = page.evaluate("()=>fetch(LabKit.config().urls.state).then(r=>r.json())")
        ou = next((u['ou'] for u in st['gui']['ad']['users'] if u['sam'] == sam), None)
    assert ou, f'AD user {sam} not found in the lab state'
    page.click(f'[data-ou="{ou}"]')
    page.click(f'[data-user="{sam}"]')


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
                wait_post(page, '/event', lambda: row.first.click())
            else:
                lbl = {'home': 'Home', 'system': 'System', 'network': 'Network & internet', 'accounts': 'Accounts', 'update': 'Windows Update'}[ev[5:]]
                wait_post(page, '/event', lambda: page.locator('.w11-nav-item', has_text=lbl).first.click())
        elif ev.startswith('adapter:'):
            if page.locator('#w11AdapterToggle').count():
                wait_post(page, '/event', lambda: page.click('#w11AdapterToggle'))
            else:
                if view == 'desktop':
                    page.click('#w11Adapter', button='right')
                else:
                    touch_long_press(page, '#w11Adapter')
                lbl = 'Disable' if ev.endswith('disable') else 'Enable'
                wait_post(page, '/event', lambda: page.locator('#w11Ctx .w11-ctx-item', has_text=lbl).click())
        elif ev.startswith('svc:'):
            wait_post(page, '/event', lambda: page.click(f'[data-svc="{ev[4:]}"]'))
        elif ev.startswith('dev:'):
            wait_post(page, '/event', lambda: page.click(f'[data-dev="{ev[4:]}"]'))
        elif ev == 'update:check':
            wait_post(page, '/event', lambda: page.click('#w11CheckUpdates'))
        elif ev == 'ad:create':
            page.click(f'[data-ou="{data["ou"]}"]')
            page.click('#adNewUser')
            page.fill('#nuFirst', data['first']); page.fill('#nuLast', data['last']); page.fill('#nuSam', data['sam'])
            page.fill('#nuPw', data['password']); page.fill('#nuPw2', data['confirm'])
            page.set_checked('#nuMust', bool(data.get('must_change')))
            wait_post(page, '/event', lambda: page.click('#dlgOk'))
        elif ev == 'ad:addgroup':
            gui_user(page, users, data['sam'])
            page.click('[data-act="group"]')
            page.select_option('#grpSel', data['group'])
            wait_post(page, '/event', lambda: page.click('#dlgOk'))
        elif ev in ('ad:unlock', 'ad:disable', 'ad:enable'):
            gui_user(page, users, data['sam'])
            act = ev[3:]
            if view != 'desktop':
                touch_long_press(page, f'[data-user="{data["sam"]}"]')
                lbl = {'unlock': 'Unlock account', 'disable': 'Disable account', 'enable': 'Enable account'}[act]
                wait_post(page, '/event', lambda: page.locator('#w11Ctx .w11-ctx-item', has_text=lbl).click())
            else:
                wait_post(page, '/event', lambda: page.click(f'[data-act="{act}"]'))
        elif ev == 'ad:reset':
            gui_user(page, users, data['sam'])
            page.click('[data-act="reset"]')
            page.fill('#rpPw', data['password']); page.fill('#rpPw2', data['confirm'])
            page.set_checked('#rpMust', bool(data.get('must_change')))
            wait_post(page, '/event', lambda: page.click('#dlgOk'))
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
               "const l=[...s.querySelectorAll('.ln')];return l.length>0&&/[#%$] $/.test(l[l.length-1].textContent)}")
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
        page.wait_for_function(last_ln, timeout=60000)
    if lab['vm'].get('net'):
        page.click('#vmTab-_packets')
        n = page.locator('#vmPackets .pk').count()
        notes.append(f'{n} packets')
        if not n:
            raise AssertionError('Packets panel is empty')
        page.click(f'#vmTab-{first}')
    page.wait_for_timeout(400)   # let the batched command log post
    sel = '[data-key-act="check"]' if page.locator('#termWrap.term-focus').count() else '#vmCheck'
    r = wait_post(page, '/vm-check', lambda: page.click(sel), timeout=60000)
    if not r['complete']:
        raise AssertionError('VM check not complete: ' + '; '.join(r['result'].get('messages') or [r['result'].get('error') or '']))
    if page.locator('#termWrap.term-focus').count():
        page.click('#btnFocusExit')


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
                page.click(f'label[for="ch-{sid}-{i}"]')
        elif t == 'order':
            for i, want in enumerate(ans):
                cur = page.eval_on_selector_all(f'{card} .lab-order-item', 'ns=>ns.map(n=>n.getAttribute("data-key"))')
                j = cur.index(want)
                for _ in range(j - i):
                    page.locator(f'{card} .lab-order-item[data-key="{want}"] .lab-mv').first.click()
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
                page.click(f'{card} .lab-pool [data-item="{item}"], {card} .lab-zone [data-item="{item}"]')
                page.click(f'{card} [data-zone="{zone}"] .lab-zone-btn')
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
        r = wait_post(page, '/check', lambda: page.click(f'#chk-{sid}'))
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
    if k in TERM_KINDS:
        drive_terminal(page, lab, view, notes)
    elif k == 'win11gui':
        drive_gui(page, lab, view, notes)
    elif k == 'vm':
        drive_vm(page, lab, view, notes)
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
    return {'lab': lab['id'], 'kind': k, 'view': view, 'ok': True, 'secs': round(time.time() - t0, 1), 'notes': notes}


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
    out.append(('csv', resp.status == 200 and all(l in csvt for l in labs_done[:5]), ''))
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
            page = ctx.new_page()
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
                         'error': (str(e) or type(e).__name__ + ' ' + traceback.format_exc().splitlines()[-3].strip())[:300], 'notes': []}
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
