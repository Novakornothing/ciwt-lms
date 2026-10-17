"""End-to-end: a student lesson page with the MediaPipe camera pipeline, using a REAL face video
as the webcam (Chromium fake capture). Walks consent -> positioning -> tap/click calibration ->
validation -> live reading -> stop, then reports what the server stored for the session.

The video has no ground-truth gaze, so validation error here is NOT an accuracy measurement;
this proves the pipeline runs on the real page and uploads engine/accuracy metadata.

Privacy audit: every request the page makes during the session is recorded with its body. The
run fails if any upload carries image/video data, data: URLs, long base64 blobs, face-landmark
fields, or a body over 64 KB, and it checks the server refuses a forged frame upload.

usage: python tools/helix_lesson_e2e.py <base> <face.y4m> <outdir> [--mobile] [--viewport WxH]
       [--email student13@lms.local] [--delegate CPU] [--tag desktop] [--db instance/lms.db]
       [--method dots|follow]
"""
import re
import argparse
import json
import sqlite3

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('base'); ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--viewport', default='1280x800'); ap.add_argument('--mobile', action='store_true')
ap.add_argument('--email', default='student13@lms.local'); ap.add_argument('--delegate', default='CPU')
ap.add_argument('--tag', default='desktop'); ap.add_argument('--db', default='')
ap.add_argument('--lesson', default='/student/module/1/1/lesson/1')
ap.add_argument('--method', default='dots', choices=['dots', 'follow'])
a = ap.parse_args()
W, H = map(int, a.viewport.split('x'))
log = {'console': [], 'requests': []}

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
                                '--use-file-for-fake-video-capture=' + a.video])
    ctx = b.new_context(viewport={'width': W, 'height': H}, permissions=['camera'],
                        is_mobile=a.mobile, has_touch=a.mobile, device_scale_factor=2 if a.mobile else 1)
    pg = ctx.new_page()
    pg.on('console', lambda m: log['console'].append(m.type + ': ' + m.text[:240]) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: log['console'].append('PAGEERROR: ' + str(e)[:240]))
    uploads = []
    def on_req(r):
        if r.method in ('POST', 'PUT', 'PATCH'):
            body = r.post_data_buffer or b''
            uploads.append({'url': r.url.replace(a.base, '').split('?')[0], 'bytes': len(body), 'body': body[:300000].decode('utf-8', 'replace')})
        elif r.method == 'GET' and r.resource_type in ('image', 'media') and a.base not in r.url and not r.url.startswith('data:'):
            uploads.append({'url': r.url, 'bytes': 0, 'body': '', 'external_media': True})
    pg.on('request', on_req)
    pg.on('response', lambda r: log['requests'].append(f"{r.request.method} {r.url.replace(a.base, '').split('?')[0]} {r.status}") if '/api/helix' in r.url else None)
    pg.goto(a.base + '/login'); pg.fill('input[name=email]', a.email); pg.fill('input[name=password]', 'student123')
    pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
    pg.goto(a.base + a.lesson); pg.wait_for_load_state('networkidle')
    tok = pg.evaluate("document.querySelector('meta[name=csrf-token]').content")
    pg.request.delete(a.base + '/api/helix/consent', headers={'X-CSRFToken': tok})   # start un-consented
    pg.goto(a.base + a.lesson + '?delegate=' + a.delegate); pg.wait_for_timeout(1200)
    if pg.locator('#hxPill').is_visible():
        pg.click('#hxPill')
    pg.wait_for_selector('#hxCam', timeout=5000)
    pg.screenshot(path=f'{a.out}/lesson-offer-{a.tag}.png')
    pg.click('#hxCam'); pg.check('#hxAgree'); pg.click('#hxConsent button[type=submit]')
    pg.wait_for_selector('#helixCalib', timeout=60000)
    if pg.locator('#hxPosChecks').count():
        pg.wait_for_timeout(2000)
        pg.screenshot(path=f'{a.out}/lesson-positioning-{a.tag}.png')
        for _ in range(40):
            if pg.locator(f'input[name=hxMethod][value={a.method}]').count():
                pg.check(f'input[name=hxMethod][value={a.method}]')
            if pg.locator('#hxPosGo').is_enabled():
                log['positioning'] = 'guidance satisfied'; pg.click('#hxPosGo'); break
            if pg.locator('#hxPosSkip').is_visible():
                log['positioning'] = 'continued anyway'; pg.click('#hxPosSkip'); break
            pg.wait_for_timeout(250)
    if a.method == 'follow':
        pg.wait_for_selector('.hx-pursuit-dot', timeout=20000); pg.wait_for_timeout(4000)
        pg.screenshot(path=f'{a.out}/lesson-follow-{a.tag}.png')
    pg.wait_for_selector('.hx-cal-pt', timeout=30000); pg.wait_for_timeout(300)
    pg.screenshot(path=f'{a.out}/lesson-calibration-{a.tag}.png')
    for _ in range(40):
        pending = pg.locator('.hx-cal-pt:not(.done)')
        if pending.count() == 0:
            break
        (pending.first.tap() if a.mobile else pending.first.click())
        pg.wait_for_timeout(1350)
    pg.wait_for_selector('.hx-cal-help.is-result', timeout=45000); pg.wait_for_timeout(300)
    pg.screenshot(path=f'{a.out}/lesson-validation-{a.tag}.png')
    log['validation'] = pg.locator('.hx-cal-help').inner_text()[:300]
    pg.locator('#hxGo, #hxGoAnyway').first.click()
    pg.wait_for_timeout(1500)
    if pg.locator('#hxDotBtn').count():
        pg.click('#hxDotBtn')
    if pg.locator('#hxDbgBtn').count():
        pg.click('#hxDbgBtn')
    # read, scroll, and click a couple of in-lesson controls (implicit samples)
    for i in range(6):
        pg.mouse.wheel(0, 250); pg.wait_for_timeout(900)
    links = pg.locator('#lessonBody a, #lessonBody button')
    for i in range(min(3, links.count())):
        try:
            box = links.nth(i).bounding_box()
            if box and 0 < box['y'] < H:
                pg.mouse.move(box['x'] + 3, box['y'] + 3)
                pg.evaluate("([x,y]) => document.elementFromPoint(x,y)?.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:y,bubbles:true,isPrimary:true,pointerType:'mouse'}))", [box['x'] + 3, box['y'] + 3])
        except Exception:
            pass
    pg.wait_for_timeout(6000)
    pg.screenshot(path=f'{a.out}/lesson-live-{a.tag}.png')
    log['now'] = pg.evaluate("document.getElementById('hxNow') && document.getElementById('hxNow').textContent")
    log['debug_hud'] = pg.evaluate("document.getElementById('hxDbg') && document.getElementById('hxDbg').innerText")
    pg.click('#hxStop'); pg.wait_for_timeout(2500)
    pg.screenshot(path=f'{a.out}/lesson-ended-{a.tag}.png')
    # forged upload: the server must refuse frame-like data even from a modified client
    sid = pg.evaluate("window.HelixRuntime && window.HelixRuntime.state.lastSessionId || null")
    forged = pg.evaluate('''async () => {
      const tok = document.querySelector('meta[name=csrf-token]').content;
      const r = await fetch('/api/helix/session/999999/batch', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': tok},
        body: JSON.stringify({segments: [], frame: 'data:image/jpeg;base64,' + 'A'.repeat(4000)})});
      return r.status; }''')
    log['forged_frame_upload_status'] = forged
    MEDIA = re.compile(r'"(frame|frames|image|images|video|snapshot|jpeg|png|webp|pixels|landmarks|faceLandmarks|mesh|iris)"\s*:|data:image|data:video|[A-Za-z0-9+/=]{2000,}', re.I)
    helix_up = [u for u in uploads if '/api/helix' in u['url'] and 'batch' in u['url'] or '/api/helix/session' in u['url']]
    helix_up = [u for u in helix_up if '999999' not in u['url']]
    bad = [u['url'] for u in helix_up if MEDIA.search(u['body'])]
    big = [(u['url'], u['bytes']) for u in uploads if u['bytes'] > 64 * 1024]
    ext = [u['url'] for u in uploads if u.get('external_media') or (u['bytes'] and a.base not in a.base + u['url'] and u['url'].startswith('http'))]
    log['privacy_audit'] = {'uploads': len(uploads), 'helix_uploads': len(helix_up),
                            'helix_bytes_total': sum(u['bytes'] for u in helix_up),
                            'largest_upload_bytes': max([u['bytes'] for u in uploads] or [0]),
                            'media_like_uploads': bad, 'oversized': big, 'offsite_posts': ext,
                            'pass': not bad and not big and not ext and forged == 400}
    log['calibration_score'] = pg.evaluate("window.HelixRuntime && window.HelixRuntime.state.calibration")
    b.close()

if a.db:
    con = sqlite3.connect(a.db); con.row_factory = sqlite3.Row
    r = con.execute("""select s.id, s.engine, s.delegate, s.mode, s.device, s.status, s.calibration_score,
        s.validation_error_px, s.validation_error_deg, s.distance_cm, s.aoi_resolution, s.orientation,
        s.implicit_samples, s.sample_count, s.total_ms, s.attentive_ms, length(s.drift_json) drift_len,
        (select count(*) from helix_aoi_bucket bk where bk.session_id = s.id) buckets
        from helix_gaze_session s join user u on u.id = s.user_id where u.email = ? order by s.id desc limit 1""", (a.email,)).fetchone()
    log['stored_session'] = dict(r) if r else None
log['requests'] = sorted(set(log['requests']))
print(json.dumps(log, indent=1))
