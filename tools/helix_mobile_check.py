"""Mobile code-path check (emulated phone + real-face fake camera) on the Try page:
front-camera constraints, playsinline video, touch tap calibration, portrait mapping,
rotation -> per-orientation model (quick 5-dot calibration, then switch back), fps cap.
Emulation only: real iOS Safari / Android Chrome behaviour is NOT covered by this.
usage: python tools/helix_mobile_check.py <base> <face.y4m> <outdir>"""
import json
import sys

from playwright.sync_api import sync_playwright

base, video, out = sys.argv[1:4]
log = {'console': []}
UA = ('Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0 Mobile Safari/537.36')


def tap_all(pg):
    n = 0
    for _ in range(40):
        pend = pg.locator('.hx-cal-pt:not(.done)')
        if pend.count() == 0:
            break
        pend.first.tap(); pg.wait_for_timeout(1350); n += 1
    return n


def go_positioning(pg):
    if pg.locator('#hxPosChecks').count():
        for _ in range(40):
            if pg.locator('#hxPosGo').is_enabled():
                pg.click('#hxPosGo'); return 'guidance satisfied'
            if pg.locator('#hxPosSkip').is_visible():
                pg.click('#hxPosSkip'); return 'continued anyway'
            pg.wait_for_timeout(250)
    return 'skipped'


with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
                                '--use-file-for-fake-video-capture=' + video])
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True,
                        device_scale_factor=3, user_agent=UA, permissions=['camera'])
    pg = ctx.new_page()
    pg.on('console', lambda m: log['console'].append(m.text[:200]) if m.type == 'error' and 'XNNPACK' not in m.text else None)
    pg.on('pageerror', lambda e: log['console'].append('PAGEERROR ' + str(e)[:200]))
    pg.goto(base + '/helix/try?delegate=CPU')
    pg.tap('#hxTryStart')
    pg.wait_for_selector('#helixCalib', timeout=60000)
    pg.wait_for_timeout(1500)
    log['camera'] = pg.evaluate("""() => { const e = window.HelixTry.engine, v = e.video, t = e.stream && e.stream.getVideoTracks()[0];
        return {engine: e.kind, isMobile: HelixEngine.isMobile(), orientation: HelixEngine.orientationKey(),
                playsinline: v.hasAttribute('playsinline'), webkitPlaysinline: v.hasAttribute('webkit-playsinline'), muted: v.muted,
                facingMode: t && t.getConstraints().facingMode, settings: t && (({width, height, frameRate}) => ({width, height, frameRate}))(t.getSettings()),
                maxFps: e.maxFps || (e.opts && e.opts.maxFps)} }""")
    pg.screenshot(path=f'{out}/mobile-positioning-390.png')
    log['positioning'] = go_positioning(pg)
    pg.wait_for_selector('.hx-cal-pt', timeout=20000)
    log['dot_type'] = pg.evaluate("document.querySelector('.hx-cal-pt').className")
    log['portrait_taps'] = tap_all(pg)
    pg.wait_for_selector('.hx-cal-help.is-result', timeout=45000); pg.wait_for_timeout(300)
    pg.screenshot(path=f'{out}/mobile-validation-390.png')
    log['portrait_score'] = pg.evaluate('window.HelixTry.score')
    pg.locator('#hxGo, #hxGoAnyway').first.tap()
    pg.wait_for_timeout(6000)
    pg.screenshot(path=f'{out}/mobile-try-live-dot-390.png')
    log['portrait_live'] = pg.evaluate("({preds: HelixTry.preds, last: HelixTry.lastPred, stats: HelixTry.engine.stats()})")
    # rotate to landscape: no landscape model yet -> quick 5-point calibration
    pg.set_viewport_size({'width': 844, 'height': 390}); pg.wait_for_timeout(900)
    log['after_rotate_state'] = pg.inner_text('#hxTryState')
    log['rotate_opened_calibration'] = pg.locator('#helixCalib').count() > 0
    if log['rotate_opened_calibration']:
        pg.wait_for_selector('.hx-cal-pt', timeout=20000)
        log['landscape_dots'] = pg.locator('.hx-cal-pt').count()
        tap_all(pg)
        pg.wait_for_selector('.hx-cal-help.is-result', timeout=45000)
        log['landscape_score'] = pg.evaluate('window.HelixTry.score')
        pg.locator('#hxGo, #hxGoAnyway').first.tap(); pg.wait_for_timeout(2500)
        pg.screenshot(path=f'{out}/mobile-landscape-844.png')
    n0 = pg.evaluate('HelixTry.preds')
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(2500)
    log['back_to_portrait_state'] = pg.inner_text('#hxTryState')
    log['back_to_portrait_recalibration'] = pg.locator('#helixCalib').count() > 0
    log['preds_after_return'] = pg.evaluate('HelixTry.preds') - n0
    log['orientation_now'] = pg.evaluate('HelixTry.engine.stats().orientation')
    b.close()
print(json.dumps(log, indent=1, default=str))
