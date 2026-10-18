"""Browser end-to-end check of the Helix runtime (passive mobile + camera calibration UI).
Usage: python helix_e2e.py <base> <outdir>
Pass 12: walks the "Get into position" step (Chromium's fake camera has no face, so it takes
"Continue anyway" once offered) and exits non-zero when a check fails."""
import json, sys, time
from playwright.sync_api import sync_playwright

base, out = sys.argv[1], sys.argv[2]
LESSON = '/student/module/1/1/lesson/1'
log = []
checks = []


def check(name, ok, detail=''):
    checks.append((name, bool(ok)))
    log.append(('PASS ' if ok else 'FAIL ') + name + (f' — {detail}' if detail else ''))


def clear_consent(pg):
    """Start from an un-consented state (the API needs the CSRF token, so a rerun is clean too)."""
    tok = pg.get_attribute('meta[name="csrf-token"]', 'content')
    r = pg.request.delete(base + '/api/helix/consent', headers={'X-CSRFToken': tok or ''})
    log.append('consent cleared: %s' % r.status)


def login(pg, email):
    pg.goto(base + '/login'); pg.fill('input[name=email]', email); pg.fill('input[name=password]', 'student123'); pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')


with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'])
    # ---- passive / mobile
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    pg = ctx.new_page()
    reqs = []
    pg.on('request', lambda r: reqs.append((r.method, r.url.replace(base, ''))) if '/api/helix' in r.url else None)
    pg.on('console', lambda m: log.append('console:' + m.type + ':' + m.text) if m.type in ('error', 'warning') else None)
    login(pg, 'student12@lms.local')
    clear_consent(pg)  # start from a clean, un-consented state
    pg.goto(base + LESSON); pg.wait_for_timeout(1200)
    pg.locator('#hxPill').is_visible() and pg.click('#hxPill'); pg.wait_for_timeout(300)
    pg.screenshot(path=out + '/helix-offer-mobile.png')
    log.append('mobile offers camera: %s' % (pg.locator('#hxCam').count() == 1))
    check('phone is offered the camera option', pg.locator('#hxCam').count() == 1)  # camera on phones since pass 3
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
    check('passive session streamed batches', any('/batch' in u for _, u in reqs))
    check('passive session summary loaded after stop', any('lesson-summary' in u for _, u in reqs))
    log.append('passive requests: %s' % json.dumps(reqs))
    ctx.close()

    # ---- camera / desktop: calibration + validation UI
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, permissions=['camera'])
    pg = ctx.new_page(); reqs2 = []
    pg.on('request', lambda r: reqs2.append((r.method, r.url.replace(base, ''))) if '/api/helix' in r.url else None)
    pg.on('console', lambda m: log.append('console2:' + m.type + ':' + m.text[:200]) if m.type == 'error' else None)
    login(pg, 'student13@lms.local')
    clear_consent(pg)  # start from a clean, un-consented state
    pg.goto(base + LESSON); pg.wait_for_timeout(1200)
    pg.locator('#hxPill').is_visible() and pg.click('#hxPill'); pg.click('#hxCam'); pg.check('#hxAgree'); pg.click('#hxConsent button[type=submit]')
    try:
        pg.wait_for_selector('#helixCalib', timeout=60000)
        if pg.locator('#hxPosChecks').count():
            pg.wait_for_timeout(1500)
            pg.screenshot(path=out + '/helix-positioning-desktop.png')
            positioned = ''
            for _ in range(80):
                if pg.locator('input[name=hxMethod][value=dots]').count():
                    pg.check('input[name=hxMethod][value=dots]')
                if pg.locator('#hxPosGo').is_enabled():
                    positioned = 'guidance satisfied'; pg.click('#hxPosGo'); break
                if pg.locator('#hxPosSkip').is_visible():
                    positioned = 'continued anyway'; pg.click('#hxPosSkip'); break
                pg.wait_for_timeout(250)
            log.append('positioning: %s' % (positioned or 'no way forward'))
            check('positioning step can be passed', positioned)
        pg.wait_for_selector('.hx-cal-pt', timeout=60000)
        check('calibration dots shown', True)
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
        # Chromium's synthetic camera shows no face, so calibration must refuse the clicks and say why.
        # (A full calibration + validation run with a real face video is tools/helix_lesson_e2e.py.)
        cal = pg.evaluate("(document.querySelector('#helixCalib')||{innerText:''}).innerText")
        check('no face: clicks are not accepted and the overlay says why', 'face not found' in cal.lower() and '0 / 9' in cal, cal[:90].replace('\n', ' '))
    except Exception as e:
        log.append('camera path: %s' % e)
        check('camera calibration path', False, str(e)[:120])
        pg.screenshot(path=out + '/helix-camera-desktop.png')
    log.append('camera requests: %s' % json.dumps(reqs2))
    ctx.close(); b.close()
print('\n'.join(log))
print(f'{sum(ok for _, ok in checks)}/{len(checks)} checks passed')
sys.exit(0 if checks and all(ok for _, ok in checks) else 1)
