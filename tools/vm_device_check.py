"""Real-VM labs on a throttled phone: boot time, save → reload → resume, and instant reset — through the real UI.

usage: python tools/vm_device_check.py [--base URL] [--cpu 4] [--labs linux-vm-shell,linux-vm-routing]
Uses Chrome DevTools CPU throttling (cpu=4 ≈ a mid-range phone, 6 ≈ an older one) at 390×844 with touch.
"""
import argparse
import json
import time

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--base', default='http://127.0.0.1:5191')
ap.add_argument('--cpu', type=float, default=4)
ap.add_argument('--labs', default='linux-vm-shell,linux-vm-routing')
ap.add_argument('--user', default='student3@lms.local')
ap.add_argument('--shots', default='')
ap.add_argument('--axe', default='', help='axe.min.js: run axe-core on the booted console (tabs, packets panel)')
a = ap.parse_args()
LAST = ("()=>{const s=document.querySelector('.vm-screen:not([hidden])');if(!s)return false;"
        "const l=[...s.querySelectorAll('.ln')];return l.length>0&&/[#%$] $/.test(l[l.length-1].textContent)}")
SCREEN = "()=>document.querySelector('.vm-screen:not([hidden])').textContent"
out = []


def unfocus(page):
    if page.locator('#termWrap.term-focus').count():
        page.click('#btnFocusExit')


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    page.on('dialog', lambda d: d.accept())
    page.goto(a.base + '/login')
    page.fill('input[name=email]', a.user)
    page.fill('input[name=password]', 'student123')
    page.click('button[type=submit]')
    page.wait_for_load_state()
    for lab in a.labs.split(','):
        r = {'lab': lab, 'cpu': a.cpu}
        page.goto(f'{a.base}/labs/{lab}')
        page.evaluate("()=>new Promise(r=>{const q=indexedDB.deleteDatabase('ciwt-vm');q.onsuccess=q.onerror=q.onblocked=()=>r()})")
        page.reload()
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': a.cpu})
        t = time.time()
        page.click('#vmBoot')
        page.wait_for_selector('#vmTools:not([hidden])', timeout=600000)
        r['boot_s'] = round(time.time() - t, 1)
        r['status'] = page.inner_text('#vmStatus')
        if a.axe:
            unfocus(page)
            if page.locator('#vmTab-_packets').count():
                page.click('#vmTab-_packets')
            page.add_script_tag(path=a.axe)
            v = page.evaluate("""async () => (await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes: ['violations']})).violations.map(x => x.id + ':' + x.nodes.map(n => n.target.join(' ')).join('|'))""")
            r['axe_booted'] = v
            if page.locator('#vmTab-_packets').count():
                page.click('.vm-tab >> nth=0')
        # type a marker, save, reload, resume, the marker must still be there (real VM state persisted)
        page.wait_for_function(LAST, timeout=60000)
        page.fill('#termInput', 'echo resumed-ok > /root/.marker; ls -l /root/.marker')
        page.press('#termInput', 'Enter')
        page.wait_for_function(LAST, timeout=60000)
        if page.locator('#termWrap.term-focus').count():
            page.click('#btnFocusExit')
        t = time.time()
        unfocus(page)
        page.click('#vmSave')
        page.wait_for_selector('.lab-toast:has-text("Saved on this device"), .toast:has-text("Saved on this device"), :text("Saved on this device")', timeout=120000)
        r['save_s'] = round(time.time() - t, 1)
        page.reload()
        page.wait_for_selector('#vmResume:not([hidden])', timeout=20000)
        t = time.time()
        page.click('#vmResume')
        page.wait_for_selector('#vmTools:not([hidden])', timeout=300000)
        r['resume_s'] = round(time.time() - t, 1)
        page.wait_for_function(LAST, timeout=60000)
        page.fill('#termInput', 'cat /root/.marker')
        page.press('#termInput', 'Enter')
        page.wait_for_function("()=>/resumed-ok\\n?[^\\n]*$/.test(document.querySelector('.vm-screen:not([hidden])').innerText) || document.querySelector('.vm-screen:not([hidden])').innerText.split('resumed-ok').length>2", timeout=60000)
        r['resume_ok'] = True
        if page.locator('#termWrap.term-focus').count():
            page.click('#btnFocusExit')
        # reset: after a resume there is no clean snapshot -> cold boot; do it, then reset again (instant, from the snapshot)
        t = time.time()
        unfocus(page)
        page.click('#vmRestart')
        page.wait_for_selector('#vmTools:not([hidden])', timeout=300000)
        page.wait_for_function(LAST, timeout=120000)
        r['reset_cold_s'] = round(time.time() - t, 1)
        page.wait_for_timeout(1500)
        t = time.time()
        unfocus(page)
        page.click('#vmRestart')
        page.wait_for_function(LAST, timeout=120000)
        r['reset_snapshot_s'] = round(time.time() - t, 1)
        page.fill('#termInput', 'ls /root/.marker 2>&1 | head -1')
        page.press('#termInput', 'Enter')
        try:
            page.wait_for_function("()=>/No such file/.test(document.querySelector('.vm-screen:not([hidden])').textContent)", timeout=20000)
            r['reset_clean'] = True
        except Exception:
            r['reset_clean'] = False
        if a.shots:
            page.screenshot(path=f'{a.shots}/{lab}-phone-throttled.png')
        if page.locator('#termWrap.term-focus').count():
            page.click('#btnFocusExit')
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
        out.append(r)
        print(json.dumps(r), flush=True)
    b.close()
