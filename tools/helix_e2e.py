"""Browser end-to-end check of the Helix runtime (passive mobile + camera calibration UI).
Usage: python helix_e2e.py <base> <outdir>"""
import json, sys, time
from playwright.sync_api import sync_playwright

base, out = sys.argv[1], sys.argv[2]
LESSON = '/student/module/1/1/lesson/1'
log = []


def login(pg, email):
    pg.goto(base + '/login'); pg.fill('input[name=email]', email); pg.fill('input[name=password]', 'student123'); pg.click('button[type=submit]')


with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'])
    # ---- passive / mobile
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    pg = ctx.new_page()
    reqs = []
    pg.on('request', lambda r: reqs.append((r.method, r.url.replace(base, ''))) if '/api/helix' in r.url else None)
    pg.on('console', lambda m: log.append('console:' + m.type + ':' + m.text) if m.type in ('error', 'warning') else None)
    login(pg, 'student12@lms.local')
    pg.request.delete(base + '/api/helix/consent')  # start from a clean, un-consented state
    pg.goto(base + LESSON); pg.wait_for_timeout(1200)
    pg.locator('#hxPill').is_visible() and pg.click('#hxPill'); pg.wait_for_timeout(300)
    pg.screenshot(path=out + '/helix-offer-mobile.png')
    assert pg.locator('#hxCam').count() == 0, 'phones should only get passive'
    pg.click('#hxPassive'); pg.wait_for_timeout(300)
    pg.check('#hxAgree'); pg.screenshot(path=out + '/helix-consent-mobile.png')
    pg.click('#hxConsent button[type=submit]'); pg.wait_for_timeout(1500)
    for y in range(0, 4000, 400):
        pg.mouse.wheel(0, 400); pg.wait_for_timeout(500)
    pg.wait_for_timeout(5500)
    pg.screenshot(path=out + '/helix-live-mobile.png')
    status = pg.evaluate("document.getElementById('hxNow') && document.getElementById('hxNow').textContent")
    pg.click('#hxStop'); pg.wait_for_timeout(1500)
    pg.screenshot(path=out + '/helix-review-mobile.png')
    log.append('passive now-text: %r' % status)
    log.append('passive requests: %s' % json.dumps(reqs))
    ctx.close()

    # ---- camera / desktop: calibration + validation UI
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, permissions=['camera'])
    pg = ctx.new_page(); reqs2 = []
    pg.on('request', lambda r: reqs2.append((r.method, r.url.replace(base, ''))) if '/api/helix' in r.url else None)
    pg.on('console', lambda m: log.append('console2:' + m.type + ':' + m.text[:200]) if m.type == 'error' else None)
    login(pg, 'student13@lms.local')
    pg.request.delete(base + '/api/helix/consent')  # start from a clean, un-consented state
    pg.goto(base + LESSON); pg.wait_for_timeout(1200)
    pg.locator('#hxPill').is_visible() and pg.click('#hxPill'); pg.click('#hxCam'); pg.check('#hxAgree'); pg.click('#hxConsent button[type=submit]')
    try:
        pg.wait_for_selector('.hx-cal-pt', timeout=60000)
        pg.wait_for_timeout(1500)
        pg.screenshot(path=out + '/helix-calibration-desktop.png')
        n = pg.locator('.hx-cal-pt').count()
        for i in range(n):
            pt = pg.locator('.hx-cal-pt').nth(i)
            for _ in range(5):
                if pt.is_visible(): pt.click(); pg.wait_for_timeout(60)
        pg.wait_for_timeout(9000)
        pg.screenshot(path=out + '/helix-validation-desktop.png')
        txt = pg.evaluate("(document.querySelector('.hx-cal-overlay, .hx-cal')||document.body).innerText.slice(0,400)")
        log.append('validation text: %r' % txt)
    except Exception as e:
        log.append('camera path: %s' % e)
        pg.screenshot(path=out + '/helix-camera-desktop.png')
    log.append('camera requests: %s' % json.dumps(reqs2))
    ctx.close(); b.close()
print('\n'.join(log))
