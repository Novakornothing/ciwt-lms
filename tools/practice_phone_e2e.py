"""Phone end-to-end for practice exams and the PBQ-style item types (pass 11).

Runs against a throwaway server (DATABASE_URL pointing at a DB copy). Usage:
  python tools/practice_phone_e2e.py <outdir> [--base URL] [--db /path/to/copy.db] [--theme dark] [--axe axe.min.js]
Starts a full A+ Core 2 practice at 390 px and answers every question through the UI (single, multi-select,
ordering with Move up/down, matching selects). Checks: practice label shown, no horizontal overflow on any
question, focus kept on the moved step, typed items count as answered, review says all answered, score
report by domain with lesson links, axe WCAG 2.1 AA on each item type, and timer auto-submit (with --db).
"""
import argparse, json, os, re, sys
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', default='http://127.0.0.1:5079')
ap.add_argument('--db', default=''); ap.add_argument('--theme', default='light')
ap.add_argument('--axe', default='/tmp/axe/node_modules/axe-core/axe.min.js')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
AXE = open(a.axe).read() if os.path.exists(a.axe) else ''
results = []

def check(name, ok, detail=''):
    results.append({'check': name, 'ok': bool(ok), 'detail': str(detail)[:300]})
    print(('PASS ' if ok else 'FAIL ') + name + (f' — {detail}' if detail and not ok else ''))

def overflow(pg):
    return pg.evaluate('() => document.documentElement.scrollWidth - document.documentElement.clientWidth')

def axe(pg):
    if not AXE:
        return None
    pg.wait_for_timeout(400)   # let colour transitions finish before measuring contrast
    pg.add_script_tag(content=AXE)
    return pg.evaluate("""async () => (await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}}))
        .violations.map(v => v.id + ' x' + v.nodes.length + ' ' + v.nodes[0].target.join(' ') + ' ' + (v.nodes[0].failureSummary || '').slice(0, 160))""")

def shot(name, pg, full=False):
    pg.screenshot(path=os.path.join(a.out, f'{name}-{a.theme}.png'), full_page=full)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    if a.theme == 'dark':
        ctx.add_init_script("try{localStorage.setItem('ciwt-theme','dark')}catch(e){}")
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(a.base + '/login'); pg.fill('[name=email]', 'student1@lms.local'); pg.fill('[name=password]', 'student123')
    with pg.expect_navigation(): pg.locator('main form button[type=submit], main form .btn-brand').first.click()

    pg.goto(a.base + '/practice'); pg.wait_for_load_state('networkidle')
    check('index: practice label shown', 'not an official CompTIA exam' in pg.locator('main').inner_text())
    check('index: no horizontal overflow', overflow(pg) <= 1, overflow(pg))
    shot('practice-index-390', pg, True)

    pg.locator('form:has(input[name=exam][value=A2]):not(:has(input[name=domain])) button').tap()
    pg.wait_for_url('**/practice/attempt/*'); pg.wait_for_selector('#qText')
    take_url = pg.url
    check('take: practice label shown', 'not an official CompTIA exam' in pg.locator('main').inner_text())
    check('take: timer shown', pg.locator('#testTimer').is_visible())
    n = pg.locator('#qNav button').count()
    check('take: 45 questions', n == 45, n)
    seen, axed, ov = {}, {}, []
    for i in range(n):
        pg.evaluate(f"document.querySelectorAll('#qNav button')[{i}].click()"); pg.wait_for_timeout(60)
        if pg.locator('.pbq-order').count():
            t = 'order'
            mv = pg.locator('.pbq-move:not([disabled])').first
            label = mv.get_attribute('aria-label'); mv.tap(); pg.wait_for_timeout(60)
            if t not in seen:
                check('order: focus stays on a move button after moving', pg.evaluate("() => document.activeElement.classList.contains('pbq-move')"), label)
                check('order: live region announces the move', pg.locator('#assessLive').inner_text().strip() != '')
            pg.locator('.pbq-confirm').tap()
        elif pg.locator('.pbq-check').count():
            t = 'multi'
            k = int(re.search(r'\d+', pg.locator('#pbqHint').inner_text()).group(0))
            for j in range(k):
                pg.locator('.pbq-check').nth(j).tap()
            if t not in seen:
                check('multi: chosen boxes are checked', pg.locator('.pbq-check input:checked').count() == k)
        elif pg.locator('.pbq-select').count():
            t = 'match'
            for j in range(pg.locator('.pbq-select').count()):
                pg.locator('.pbq-select').nth(j).select_option(index=1)
        else:
            t = 'single'
            pg.locator('.q-option').nth(0).tap()
        answered = 'answered' in (pg.locator('#qNav button').nth(i).get_attribute('class') or '')
        if t not in seen:
            check(f'{t}: counts as answered', answered)
            shot(f'practice-take-390-{t}', pg)
            v = axe(pg)
            if v is not None:
                check(f'{t}: axe WCAG 2.1 AA clean', not v, v)
        seen[t] = seen.get(t, 0) + 1
        o = overflow(pg)
        if o > 1:
            ov.append((i + 1, t, o))
    check('take: every item type appeared', set(seen) == {'single', 'multi', 'order', 'match'}, seen)
    check('take: no question overflows 390 px', not ov, ov)
    pg.locator('#submitBtn').tap(); pg.wait_for_selector('#reviewModal.show'); pg.wait_for_timeout(350)
    check('review: all answered', 'Every question has an answer' in pg.locator('#reviewBody').inner_text())
    with pg.expect_navigation():
        pg.locator('#confirmSubmit').tap()
    pg.wait_for_load_state('networkidle')
    body = pg.locator('main').inner_text()
    check('result: own URL', pg.url.endswith('/result'), pg.url)
    check('result: practice label and scaled-score caveat', 'not an official CompTIA exam' in body and 'does not convert' in body and 'scaled scores' in body)
    check('result: domain breakdown', body.count('% of the exam') == 4, body.count('% of the exam'))
    check('result: lesson links for missed objectives', pg.locator('main a[href*="/lesson/"]').count() > 0 or 'Every question in this domain was correct' in body)
    check('result: fits 390 px', overflow(pg) <= 1, overflow(pg))
    v = axe(pg)
    if v is not None:
        check('result: axe WCAG 2.1 AA clean', not v, v)
    shot('practice-result-390', pg, True); shot('practice-result-390-top', pg)
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.evaluate('window.scrollTo(0,0)')
    check('result: sessionStorage cleared', pg.evaluate("() => Object.keys(sessionStorage).filter(k => k.startsWith('ciwt-assess:')).length") == 0)

    if a.db:
        import sqlite3
        pg.goto(a.base + '/practice'); pg.locator('form:has(input[name=domain]) button').first.tap()
        pg.wait_for_url('**/practice/attempt/*'); aid = int(pg.url.rstrip('/').split('/')[-1])
        con = sqlite3.connect(a.db)
        con.execute("update practice_attempt set deadline=datetime('now', '+4 seconds') where id=?", (aid,)); con.commit(); con.close()
        pg.reload(); pg.wait_for_selector('#qText')
        pg.wait_for_url('**/result', timeout=20000); pg.wait_for_load_state('networkidle')
        con = sqlite3.connect(a.db); to = con.execute('select timed_out, submitted_at from practice_attempt where id=?', (aid,)).fetchone(); con.close()
        check('timer: auto-submits at zero, marked timed out', to and to[0] == 1 and to[1], to)
        check('timer: report says time ran out', 'time ran out' in pg.locator('main').inner_text())
    check('no page JS errors', not errs, '; '.join(errs[:3]))
    b.close()
json.dump(results, open(os.path.join(a.out, f'practice-phone-e2e-{a.theme}.json'), 'w'), indent=1)
fails = [r for r in results if not r['ok']]
print(f"{len(results) - len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
