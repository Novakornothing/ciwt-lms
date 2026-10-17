"""Phone end-to-end for the quiz and knowledge-test runner (pass 6).

Runs against a throwaway server (DATABASE_URL pointing at a DB copy). Usage:
  python tools/assess_phone_e2e.py <outdir> [--base URL] [--quiz /student/quiz/1/1] [--test /student/test/1/2] [--theme dark]
Checks: no horizontal overflow, tab bar hidden in focus mode, sticky action bar and timer stay on screen,
answer/flag/reload-restore, review modal jump chips, submit -> results, and timer auto-submit.
"""
import argparse, json, os, sys, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', default='http://127.0.0.1:5077')
ap.add_argument('--quiz', default='/student/quiz/1/1'); ap.add_argument('--test', default='/student/test/1/2')
ap.add_argument('--theme', default='light'); ap.add_argument('--db', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
results = []

def check(name, ok, detail=''):
    results.append({'check': name, 'ok': bool(ok), 'detail': detail})
    print(('PASS ' if ok else 'FAIL ') + name + (f' — {detail}' if detail else ''))

GEOM = """() => { const W = document.documentElement.clientWidth, H = innerHeight;
  const vis = s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); const st = getComputedStyle(e);
    return {top: Math.round(r.top), bottom: Math.round(r.bottom), shown: st.display !== 'none' && st.visibility !== 'hidden' && r.height > 0}; };
  return { W, H, sw: document.documentElement.scrollWidth, tabbar: vis('.mobile-tabbar'), actions: vis('.assess-actions'),
           toolbar: vis('.test-toolbar'), timer: vis('#testTimer') }; }"""

def run_flow(pg, kind, path, shot):
    pg.goto(a.base + path); pg.wait_for_selector('#qText')
    g = pg.evaluate(GEOM)
    check(f'{kind}: no horizontal overflow', g['sw'] <= g['W'] + 1, f"scrollWidth {g['sw']} vs {g['W']}")
    check(f'{kind}: tab bar hidden in focus mode', not (g['tabbar'] and g['tabbar']['shown']))
    check(f'{kind}: action bar on screen', g['actions']['shown'] and g['actions']['bottom'] <= g['H'] + 1, json.dumps(g['actions']))
    pg.screenshot(path=shot('01-start'))
    n = pg.locator('#qNav button').count()
    # answer Q1 by tapping the second option
    pg.locator('.q-option').nth(1).tap()
    check(f'{kind}: tap selects option', pg.locator('.q-option.selected').count() == 1)
    check(f'{kind}: navigator marks answered', 'answered' in (pg.locator('#qNav button').nth(0).get_attribute('class') or ''))
    pg.locator('#nextBtn').tap(); pg.wait_for_timeout(150)
    check(f'{kind}: next moves to Q2', pg.locator('#qText').inner_text().startswith('2.'))
    pg.locator('.q-option').nth(0).tap(); pg.locator('#flagBtn').tap()
    check(f'{kind}: flag toggles', pg.locator('#flagBtn').get_attribute('aria-pressed') == 'true')
    # scroll to the bottom: toolbar (and timer) must stay visible
    pg.mouse.wheel(0, 2000); pg.wait_for_timeout(250)
    g = pg.evaluate(GEOM)
    check(f'{kind}: toolbar sticky after scroll', g['toolbar']['top'] >= 0 and g['toolbar']['top'] < 120, json.dumps(g['toolbar']))
    if kind == 'test':
        check('test: timer visible after scroll', g['timer'] and g['timer']['shown'] and 0 <= g['timer']['top'] < g['H'])
        t1 = pg.locator('#timerDisplay').inner_text(); pg.wait_for_timeout(1300); t2 = pg.locator('#timerDisplay').inner_text()
        check('test: timer counts down', t1 != t2 and ':' in t2, f'{t1} -> {t2}')
    pg.screenshot(path=shot('02-answered-flagged'))
    # reload: answers and flags restored (sessionStorage); beforeunload is bypassed in automation
    pg.reload(); pg.wait_for_selector('#qText')
    restored = pg.evaluate("() => [...document.querySelectorAll('#qNav button')].slice(0,2).map(b => b.className)")
    check(f'{kind}: answers + flag restored after reload', 'answered' in restored[0] and 'answered' in restored[1] and 'flagged' in restored[1], str(restored))
    # jump to last via navigator, open submit review
    pg.locator('#qNav button').nth(n - 1).tap(); pg.wait_for_timeout(150)
    check(f'{kind}: submit button on last question', pg.locator('#submitBtn').is_visible())
    pg.locator('#submitBtn').tap(); pg.wait_for_selector('#reviewModal.show'); pg.wait_for_timeout(350)
    chips = pg.locator('#reviewBody .review-chips .btn')
    check(f'{kind}: review lists unanswered + flagged chips', chips.count() >= 2, f'{chips.count()} chips')
    pg.screenshot(path=shot('03-review'))
    chips.nth(0).tap(); pg.wait_for_timeout(500)
    check(f'{kind}: chip jumps to that question', pg.locator('#qText').inner_text().startswith('3.') and not pg.locator('#reviewModal.show').count())
    # answer everything quickly, then submit
    for i in range(n):
        pg.evaluate(f"document.querySelectorAll('#qNav button')[{i}].click()")
        pg.locator('.q-option').nth(0).tap()
    pg.locator('#submitBtn').tap(); pg.wait_for_selector('#reviewModal.show'); pg.wait_for_timeout(350)
    check(f'{kind}: review says all answered', 'Every question has an answer' in pg.locator('#reviewBody').inner_text())
    with pg.expect_navigation():
        pg.locator('#confirmSubmit').tap()
    pg.wait_for_load_state('networkidle')
    body = pg.locator('main').inner_text()
    check(f'{kind}: results page after submit', ('%' in body) and ('Score' in body or 'score' in body or 'correct' in body), pg.url)
    g = pg.evaluate(GEOM)
    check(f'{kind}: results fit phone width', g['sw'] <= g['W'] + 1, f"{g['sw']}")
    check(f'{kind}: tab bar back after submit', g['tabbar'] and g['tabbar']['shown'])
    left = pg.evaluate("() => Object.keys(sessionStorage).filter(k => k.startsWith('ciwt-assess:')).length")
    check(f'{kind}: saved answers cleared after submit', left == 0, f'{left} keys')
    pg.screenshot(path=shot('04-results'), full_page=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True,
                        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
    if a.theme == 'dark':
        ctx.add_init_script("try{localStorage.setItem('ciwt-theme','dark')}catch(e){}")
    pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(a.base + '/login'); pg.fill('[name=email]', 'student1@lms.local'); pg.fill('[name=password]', 'student123')
    with pg.expect_navigation(): pg.locator('main form button[type=submit], main form .btn-brand').first.click()
    for kind, path in (('quiz', a.quiz), ('test', a.test)):
        run_flow(pg, kind, path, lambda s, k=kind: os.path.join(a.out, f'phone-{k}-{s}-{a.theme}.png'))
    # timer auto-submit: start a fresh attempt, then age it in the DB copy so ~4s remain
    if a.db:
        import sqlite3
        pg.goto(a.base + a.test); pg.wait_for_selector('#qText')
        con = sqlite3.connect(a.db)
        sec, tid = a.test.rstrip('/').split('/')[-2:]
        lim = con.execute('select time_limit_minutes from knowledge_test where id=?', (tid,)).fetchone()[0] or 75
        con.execute("update test_attempt set started_at=datetime('now', ?) where user_id=4 and test_id=? and section_id=? and completed_at is null",
                    (f'-{lim * 60 - 4} seconds', tid, sec)); con.commit(); con.close()
        pg.reload(); pg.wait_for_selector('#qText')
        pg.locator('.q-option').nth(0).tap()
        cls = pg.locator('#testTimer').get_attribute('class')
        check('test: last-minute timer turns red', 'danger' in (cls or ''), cls)
        pg.screenshot(path=os.path.join(a.out, f'phone-test-05-last-seconds-{a.theme}.png'))
        try:
            pg.wait_for_url('**/student/test/**', timeout=1)  # same URL after POST; wait for results text instead
        except Exception:
            pass
        pg.wait_for_function("() => document.body.innerText.includes('Time expired')", timeout=15000)
        check('test: auto-submits at zero with a notice', 'Time expired' in pg.locator('main').inner_text())
    check('no page JS errors', not errs, '; '.join(errs[:3]))
    b.close()
json.dump(results, open(os.path.join(a.out, f'phone-e2e-{a.theme}.json'), 'w'), indent=1)
fails = [r for r in results if not r['ok']]
print(f"{len(results) - len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
