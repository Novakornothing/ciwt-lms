"""Pass 10 e2e: session hardening + re-check on a real lesson page with the MediaPipe pipeline and a
real face video as the fake webcam (Chromium fake capture).

What is simulated, and how (each is the browser event the runtime listens for):
  re-check     the real "Re-check accuracy" button (5 look-only dots), then "Back to reading"
  sleep        HelixRuntime.state.lastTickAt moved 20 s into the past (what a suspended page sees on resume)
  other tab    a second real tab of the same browser context posts the runtime's claim message on the
               'ciwt-helix' BroadcastChannel; tab 1 must release the camera, then reclaim on click
  track ended  'ended' dispatched on the live MediaStreamTrack (unplug / another app took it)
  permission   navigator.permissions.query('camera') wrapped before load; its status flips to 'denied'
               and fires 'change' (Chromium's fake-UI flag cannot revoke for real)
  unplugged    enumerateDevices() made to return no cameras, then 'devicechange' fired
After each loss it presses Reconnect (the fake device is still there, so it reconnects to the same id).
Finally it stops and reads the stored session counters from the DB.

usage: python tools/helix_hardening_e2e.py <base> <face.y4m> <outdir> --db <db> [--email ...]
"""
import argparse
import json
import sqlite3
import sys

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('base'); ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--db', default=''); ap.add_argument('--email', default='student14@lms.local')
ap.add_argument('--lesson', default='/student/module/1/1/lesson/1')
a = ap.parse_args()
res = {'steps': {}, 'console': []}

PERM_HOOK = """
(() => {
  if (!navigator.permissions) return;
  const orig = navigator.permissions.query.bind(navigator.permissions);
  navigator.permissions.query = (d) => {
    if (d && d.name === 'camera') {
      const st = new EventTarget(); st.state = 'granted'; st.onchange = null;
      window.__camPerm = st; return Promise.resolve(st);
    }
    return orig(d);
  };
})();
"""


def state(pg, expr):
    return pg.evaluate('() => { const S = window.HelixRuntime.state; return ' + expr + '; }')


def wait_live(pg, timeout=15000):
    pg.wait_for_function("() => { const S = window.HelixRuntime && window.HelixRuntime.state; return S && S.timeline && !S.cameraLost && !S.yielded && document.getElementById('hxCheck'); }", timeout=timeout)


def cur_state(pg):
    return state(pg, 'S.timeline && S.timeline.cur ? S.timeline.cur.key : null')


with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
                                '--use-file-for-fake-video-capture=' + a.video])
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}, permissions=['camera'])
    ctx.add_init_script(PERM_HOOK)
    pg = ctx.new_page()
    pg.set_default_timeout(60000)
    pg.on('pageerror', lambda e: res['console'].append('PAGEERROR: ' + str(e)[:240]))
    pg.on('console', lambda m: res['console'].append(m.type + ': ' + m.text[:200]) if m.type == 'error' else None)
    pg.goto(a.base + '/login'); pg.fill('input[name=email]', a.email); pg.fill('input[name=password]', 'student123')
    pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
    pg.goto(a.base + a.lesson + '?delegate=CPU'); pg.wait_for_timeout(1200)
    if pg.locator('#hxPill').is_visible():
        pg.click('#hxPill')
    pg.wait_for_selector('#hxCam', timeout=8000)
    pg.click('#hxCam')
    if pg.locator('#hxAgree').count():
        pg.check('#hxAgree'); pg.click('#hxConsent button[type=submit]')
    pg.wait_for_selector('#helixCalib', timeout=60000)
    for _ in range(60):
        if pg.locator('#hxPosGo').count() and pg.locator('#hxPosGo').is_enabled():
            pg.click('#hxPosGo'); break
        if pg.locator('#hxPosSkip').count() and pg.locator('#hxPosSkip').is_visible():
            pg.click('#hxPosSkip'); break
        if pg.locator('.hx-cal-pt').count():
            break
        pg.wait_for_timeout(250)
    pg.wait_for_selector('.hx-cal-pt', timeout=30000)
    for _ in range(80):   # a dot only counts while the face is tracked; under load that can take a few tries
        pending = pg.locator('.hx-cal-pt:not(.done)')
        if pending.count() == 0:
            break
        try:
            pending.first.click(timeout=5000)
        except Exception:
            pass
        pg.wait_for_timeout(1300)
    try:
        pg.wait_for_selector('.hx-cal-help.is-result', timeout=120000)
    except Exception:
        pg.screenshot(path=f'{a.out}/debug-calib.png')
        print('DEBUG', pg.evaluate("() => [document.querySelectorAll('.hx-cal-pt').length, document.querySelectorAll('.hx-cal-pt.done').length, (document.querySelector('.hx-cal-help')||{}).innerText]"))
        raise
    pg.locator('#hxGo, #hxGoAnyway').first.click()
    wait_live(pg)
    pg.wait_for_timeout(2500)
    res['session_id'] = state(pg, 'S.sessionId')
    # record every state the timeline enters (read-only spy, the runtime's behaviour is unchanged)
    pg.evaluate("() => { const T = window.HelixRuntime.state.timeline, orig = T.enter; window.__entered = []; T.enter = function (a, t) { window.__entered.push(a.key); return orig.call(this, a, t); }; }")

    # 1. re-check accuracy
    try:
        pg.click('#hxCheck', timeout=5000)
    except Exception:
        pg.screenshot(path=f'{a.out}/debug-check.png')
        print('DEBUG', pg.evaluate("() => { const b = document.getElementById('hxCheck'); const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2); return [r.x, r.y, r.width, r.height, e && (e.id || e.className), innerWidth, innerHeight]; }"))
        raise
    pg.wait_for_selector('.hx-cal-help.is-result', timeout=30000)
    res['steps']['recheck'] = {'overlay_text': pg.locator('.hx-cal-help').inner_text()[:200]}
    pg.screenshot(path=f'{a.out}/hardening-recheck.png')
    pg.click('#hxChkDone'); wait_live(pg)
    res['steps']['recheck'].update(rechecks=state(pg, 'S.rechecks'), last=state(pg, 'S.lastCheck'),
                                   live_note=pg.locator('#helixDock').inner_text()[:400])
    res['steps']['recheck']['pass'] = res['steps']['recheck']['rechecks'] == 1 and 'Last check' in res['steps']['recheck']['live_note']

    # 2. sleep / resume
    before = state(pg, 'S.sleeps')
    pg.evaluate('() => { window.__entered = []; window.HelixRuntime.state.lastTickAt = Date.now() - 20000; }')
    pg.wait_for_timeout(1600)
    segs = pg.evaluate('() => window.__entered.slice(0, 6)')
    res['steps']['sleep'] = {'sleeps_before': before, 'sleeps': state(pg, 'S.sleeps'), 'entered': segs,
                             'note': 'sleeps_before can be >0: under heavy box load a real >8 s timer gap also counts as a suspension'}
    res['steps']['sleep']['pass'] = res['steps']['sleep']['sleeps'] == before + 1 and segs[:1] == ['_asleep']

    # 3. a second tab takes over
    pg2 = ctx.new_page()
    pg2.goto(a.base + a.lesson); pg2.wait_for_timeout(800)
    pg2.evaluate("() => new BroadcastChannel('ciwt-helix').postMessage({type: 'claim', tab: 'e2e-tab2', lesson: window.HELIX.lessonId, t: Date.now()})")
    pg.wait_for_selector('#hxUseHere', timeout=5000)
    pg.wait_for_timeout(1300)
    tracks = pg.evaluate("() => { const e = window.HelixRuntime.state.engine; return e && e.stream ? e.stream.getTracks().map(t => t.readyState) : []; }")
    res['steps']['other_tab'] = {'yielded': state(pg, 'S.yielded'), 'tracks': tracks, 'state': cur_state(pg), 'tab_yields': state(pg, 'S.tabYields')}
    pg.screenshot(path=f'{a.out}/hardening-other-tab.png')
    pg2.close()
    pg.click('#hxUseHere'); wait_live(pg); pg.wait_for_timeout(1500)
    res['steps']['other_tab']['reclaimed'] = not state(pg, 'S.yielded') and state(pg, '!!S.engine.ready()')
    res['steps']['other_tab']['pass'] = (res['steps']['other_tab']['yielded'] and all(t == 'ended' for t in tracks)
                                         and res['steps']['other_tab']['state'] == '_other_tab' and res['steps']['other_tab']['reclaimed'])

    def loss(name, js):
        pg.evaluate(js)
        pg.wait_for_selector('#hxReconnect', timeout=8000)
        pg.wait_for_timeout(1300)
        r = {'reason': state(pg, 'S.cameraLost'), 'state': cur_state(pg), 'losses': state(pg, 'S.cameraLosses'),
             'panel': pg.locator('#helixDock').inner_text()[:700]}
        pg.screenshot(path=f'{a.out}/hardening-{name}.png')
        pg.click('#hxReconnect')
        wait_live(pg, 20000); pg.wait_for_timeout(1500)
        r['reconnected'] = state(pg, '!S.cameraLost && S.engine.ready()')
        r['frames_after'] = pg.evaluate("() => new Promise(res => { let n = 0; const e = window.HelixRuntime.state.engine; const l = e.on(ev => { if (ev.pred || ev.feat) n++; }); setTimeout(() => { e.off(l); res(n); }, 1500); })")
        return r

    # 4. track ended
    r = loss('track-ended', "() => window.HelixRuntime.state.engine.track.dispatchEvent(new Event('ended'))")
    r['pass'] = r['reason'] == 'ended' and r['state'] == '_camera_off' and r['reconnected'] and r['frames_after'] > 0
    res['steps']['track_ended'] = r
    # 5. permission revoked
    r = loss('permission', "() => { const s = window.__camPerm; s.state = 'denied'; s.dispatchEvent(new Event('change')); }")
    r['pass'] = r['reason'] == 'permission' and 'site settings' in r['panel'] and r['reconnected']
    res['steps']['permission'] = r
    pg.evaluate("() => { window.__camPerm.state = 'granted'; }")
    # 6. camera unplugged
    r = loss('unplugged', """() => {
        const md = navigator.mediaDevices, orig = md.enumerateDevices.bind(md);
        md.enumerateDevices = () => Promise.resolve([]);
        md.dispatchEvent(new Event('devicechange'));
        setTimeout(() => { md.enumerateDevices = orig; }, 400);
    }""")
    r['pass'] = r['reason'] == 'unplugged' and r['reconnected']
    res['steps']['unplugged'] = r

    pg.wait_for_timeout(2000)
    pg.click('#hxStop'); pg.wait_for_timeout(2500)
    b.close()

if a.db and res.get('session_id'):
    con = sqlite3.connect(a.db); con.row_factory = sqlite3.Row
    row = con.execute('select status, rechecks, recheck_error_px, camera_losses, sleeps, tab_yields, calib_ms, calib_mode, '
                      'camera_res, browser, face_lost_ms, hidden_ms, attentive_ms, total_ms from helix_gaze_session where id=?',
                      (res['session_id'],)).fetchone()
    res['stored'] = dict(row) if row else None
    s = res['stored'] or {}
    res['stored_pass'] = bool(s) and s['rechecks'] == 1 and s['camera_losses'] >= 3 and s['sleeps'] >= 1 and s['tab_yields'] >= 1 and bool(s['calib_ms'])
res['pass'] = all(v.get('pass') for v in res['steps'].values()) and res.get('stored_pass', True) and not [c for c in res['console'] if 'PAGEERROR' in c]
print(json.dumps(res, indent=1))
sys.exit(0 if res['pass'] else 1)
