"""End-to-end check of the MediaPipe camera pipeline with a REAL face video as the camera.

Chromium's fake capture device plays a y4m file as the webcam. The face video has no ground truth
for where the person looks, so this proves the pipeline runs (model loads, delegate, landmarks,
features, calibration, validation, live estimates that move) - it does not measure accuracy.

usage: python tools/helix_mp_e2e.py <base_url> <face.y4m> <outdir> [--viewport 1280x800] [--mobile]
       [--record fixture.json] [--engine auto|mediapipe|webgazer]
"""
import argparse
import json
import statistics
import time

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('base'); ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--viewport', default='1280x800'); ap.add_argument('--mobile', action='store_true')
ap.add_argument('--record'); ap.add_argument('--engine', default='auto'); ap.add_argument('--tag', default='desktop'); ap.add_argument('--delegate', default='')
a = ap.parse_args()
W, H = map(int, a.viewport.split('x'))
log = {'console': []}

RECORD_JS = """() => {
  const keep = [33,133,159,145,468,469,471,362,263,386,374,473,474,476,234,454,10,152,1];
  window.__rec = [];
  window.HelixTry.engine.on(ev => {
    if (window.__rec.length > 400) return;
    const f = ev.feat;
    if (!f || !f.landmarks) { window.__rec.push({t: ev.t, face: false}); return; }
    const lm = {}; keep.forEach(i => { const p = f.landmarks[i]; lm[i] = [+p.x.toFixed(5), +p.y.toFixed(5)]; });
    window.__rec.push({t: ev.t, face: true, lm, pose: f.pose, dist: f.distanceCm, open: f.open,
      look: f.vec.slice(19, 23), lookDown: f.lookDown, blinkScore: f.blinkScore, blink: f.blink, infer: ev.inferMs, pred: ev.pred});
  });
}"""

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
                                '--use-file-for-fake-video-capture=' + a.video, '--enable-unsafe-swiftshader'])
    ctx = b.new_context(viewport={'width': W, 'height': H}, permissions=['camera'],
                        is_mobile=a.mobile, has_touch=a.mobile, device_scale_factor=2 if a.mobile else 1)
    pg = ctx.new_page()
    pg.on('console', lambda m: log['console'].append(m.type + ': ' + m.text[:300]) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: log['console'].append('PAGEERROR: ' + str(e)[:300]))
    pg.goto(a.base + '/helix/try?engine=' + a.engine + ('&delegate=' + a.delegate if a.delegate else ''))
    pg.select_option('#hxTryEngine', a.engine)
    t0 = time.time()
    pg.click('#hxTryStart')
    pg.wait_for_selector('#helixCalib', timeout=90000)
    log['engine_load_s'] = round(time.time() - t0, 1)
    if pg.locator('#hxPosChecks').count():
        pg.wait_for_timeout(2500)
        pg.screenshot(path=f'{a.out}/mp-positioning-{a.tag}.png')
        log['positioning_checks'] = pg.locator('#hxPosChecks').inner_text()
        if a.record:
            pg.evaluate(RECORD_JS)
        # press Start as soon as guidance is satisfied, else "Continue anyway" (shown after 5 s)
        for _ in range(40):
            if pg.locator('#hxPosGo').is_enabled():
                log['positioning'] = 'guidance satisfied'; pg.click('#hxPosGo'); break
            if pg.locator('#hxPosSkip').is_visible():
                log['positioning'] = 'continued anyway'; pg.click('#hxPosSkip'); break
            pg.wait_for_timeout(250)
    pg.wait_for_selector('.hx-cal-pt', timeout=20000)
    pg.wait_for_timeout(400)
    pg.screenshot(path=f'{a.out}/mp-calibration-{a.tag}.png')
    retries = 0
    for _ in range(40):
        pending = pg.locator('.hx-cal-pt:not(.done)')
        if pending.count() == 0:
            break
        (pending.first.tap() if a.mobile else pending.first.click())
        pg.wait_for_timeout(1350)
        retries += 1
    log['dot_presses'] = retries
    log['dots_done'] = pg.locator('.hx-cal-pt.done').count()
    try:
        pg.wait_for_selector('.hx-cal-help.is-result', timeout=45000)
    except Exception:
        pg.screenshot(path=f'{a.out}/mp-FAIL-{a.tag}.png')
        log['fail_help'] = pg.locator('.hx-cal-help').inner_text()[:300]
        log['fail_stats'] = pg.evaluate('window.HelixTry.engine && window.HelixTry.engine.stats()')
        print(json.dumps(log, indent=1)); raise SystemExit(1)
    pg.wait_for_timeout(300)
    pg.screenshot(path=f'{a.out}/mp-validation-{a.tag}.png')
    log['validation_text'] = pg.locator('.hx-cal-help').inner_text()[:500]
    log['score'] = pg.evaluate('window.HelixTry.score')
    btn = pg.locator('#hxGo, #hxGoAnyway').first
    btn.click()
    pg.wait_for_timeout(9000)
    pg.screenshot(path=f'{a.out}/mp-live-{a.tag}.png')
    # pass 5: diagnostics card with the live eye crops (Try page only)
    if pg.locator('#hxTryCropsWrap:not([hidden])').count():
        card = pg.locator('#hxTryHud').locator('xpath=ancestor::div[contains(@class,"card")][1]')
        card.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
        card.screenshot(path=f'{a.out}/mp-hud-crops-{a.tag}.png')
        log['crop_hud'] = True
    st = pg.evaluate("""() => ({stats: window.HelixTry.engine.stats(), preds: window.HelixTry.preds,
                               frames: window.HelixTry.frames, hist: window.HelixTry.history.slice(-200)})""")
    hist = st.pop('hist')
    log.update(st)
    if hist:
        xs = [h['x'] for h in hist]; ys = [h['y'] for h in hist]
        log['live_estimates'] = {'n': len(hist), 'x_range': [min(xs), max(xs)], 'y_range': [min(ys), max(ys)],
                                 'x_sd': round(statistics.pstdev(xs), 1), 'y_sd': round(statistics.pstdev(ys), 1)}
    if a.record:
        rec = pg.evaluate('window.__rec')
        meta = {'source': 'Wikimedia Commons "Interview with Zara Kay about Faithless Hijabi.webm" (CC0), 2:00-2:24, right half cropped to 640x480 @15 fps',
                'captured_with': 'MediaPipe Face Landmarker (tasks-vision 1.1.1) in Chromium fake camera, delegate ' + str(st['stats'].get('delegate')),
                'frames': len(rec)}
        json.dump({'meta': meta, 'frames': rec}, open(a.record, 'w'))
        log['recorded_frames'] = len(rec)
    b.close()
print(json.dumps(log, indent=1))
