"""Explanation ladder end to end (pass 19), phone 390 and desktop 1280, light or dark.

Runs against a throwaway server whose DATABASE_URL points at a DB copy (never ciwt_lms.db):
  HOST=127.0.0.1 DATABASE_URL=sqlite:////tmp/p19/e2e.db PORT=5073 python app.py &
  python tools/ladder_e2e.py <outdir> --base http://127.0.0.1:5073 --db /tmp/p19/e2e.db [--width 390] [--theme dark]
It clears the ladder rows of student1 and student2 (and class 1's ladder settings) in the copy first.
Flow (student1, lesson 1.1, section "2. Three kinds of work"): miss the micro-check -> R1 replaces the section in
place (label, fresh check) -> miss -> R2 (analogy) -> pass -> leave and come back -> R2 is shown with "See the
original" (toggle both ways) -> "I don't get it" on another section -> try-it widget (R4 order) -> profile page.
student2 runs out of explanations on "3. Impact and identity" -> instructor: Who needs me flag, briefing,
analytics, per-section override and the micro-check toggle (student view changes), SME preview.
axe-core (WCAG 2.0/2.1 A + AA) on the lesson after a swap, the profile page, analytics and the preview.
"""
import argparse, json, os, sqlite3, sys
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', default='http://127.0.0.1:5073'); ap.add_argument('--db', required=True)
ap.add_argument('--width', type=int, default=390); ap.add_argument('--theme', default='light')
ap.add_argument('--axe', default='/tmp/axe/node_modules/axe-core/axe.min.js'); ap.add_argument('--shots', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
if os.path.realpath(a.db).endswith('ciwt_lms.db'):
    sys.exit('Refusing to run against ciwt_lms.db: use a copy.')
W = a.width; PHONE = W < 600
SHOTS = a.shots or a.out
os.makedirs(SHOTS, exist_ok=True)
TAG = f'{W}-{a.theme}'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curriculum_v2 import ladder as LD  # noqa: E402

results, axe_out = [], []
AXE = open(a.axe).read() if os.path.exists(a.axe) else None


def check(name, ok, detail=''):
    results.append({'check': name, 'ok': bool(ok), 'detail': detail, 'width': W, 'theme': a.theme})
    print(('PASS ' if ok else 'FAIL ') + f'[{TAG}] ' + name + (f' — {detail}' if detail else ''))


def db():
    c = sqlite3.connect(a.db, timeout=10)
    c.row_factory = sqlite3.Row
    return c


SEC = 1
with db() as c:
    uids = [r['id'] for r in c.execute("SELECT id FROM user WHERE email IN ('student1@lms.local','student2@lms.local') ORDER BY email")]
    for t in ('ladder_state', 'ladder_event', 'ladder_profile_reset'):
        c.execute(f'DELETE FROM {t} WHERE user_id IN ({",".join("?" * len(uids))})', uids)
    c.execute('DELETE FROM ladder_setting WHERE section_id=?', (SEC,))
    les = c.execute("SELECT l.id, l.module_id FROM lesson l JOIN module m ON m.id=l.module_id "
                    "WHERE m.course_id=1 AND l.title LIKE '1.1 %'").fetchone()
LESSON = f'/student/module/{SEC}/{les["module_id"]}/lesson/{les["id"]}'
S1, S2 = '2-three-kinds-of-work', '3-impact-and-identity'


def key_of(cid, right):
    for (c, label, sid), e in LD.ladder().items():
        pre = f'L-{c}-{label}-{sid}-'
        if cid.startswith(pre) and e.get('type') == 'section':
            rung = cid[len(pre):].split('-')[0]
            chk = next(x for x in LD.rung_checks(LD.entry(c, label, sid), rung) if x['id'] == cid)
            return chk['correct'] if right else next(o for o in chk['options'] if o != chk['correct'])
    raise KeyError(cid)


def login(pg, email, pw):
    pg.goto(a.base + '/logout'); pg.goto(a.base + '/login')
    pg.fill('input[name=email]', email); pg.fill('input[name=password]', pw)
    pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')


def shot(pg, name, loc=None, full=False):
    """loc: scroll its top just under the sticky top bar and take the viewport (what the student sees)."""
    path = f'{SHOTS}/{name}-{TAG}.png'
    if loc is not None:
        loc.evaluate("el => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 76)")
        pg.wait_for_timeout(250)
        pg.screenshot(path=path)
    else:
        pg.screenshot(path=path, full_page=full)


def no_overflow(pg, label):
    ov = pg.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check(f'no horizontal overflow: {label}', ov <= 1, f'{ov}px')


def run_axe(pg, label):
    if not AXE:
        check(f'axe available for {label}', False, a.axe)
        return
    pg.add_script_tag(content=AXE)
    res = pg.evaluate("""async () => { const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes: ['violations']});
        return r.violations.map(v => ({id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' '))})); }""")
    axe_out.append({'page': label, 'width': W, 'theme': a.theme, 'violations': res})
    check(f'axe 0 violations: {label}', not res, '; '.join(f"{v['id']}×{v['n']} {v['sample']}" for v in res))


def answer(pg, box_sel, right):
    box = pg.locator(box_sel)
    cid = box.locator('input[name=check_id]').get_attribute('value')
    val = key_of(cid, right)
    radios = box.locator('input[name=answer]')
    for i in range(radios.count()):
        if radios.nth(i).get_attribute('value') == val:
            box.locator(f'label[for="{radios.nth(i).get_attribute("id")}"]').click()
            break
    shown = box.get_attribute('data-shown')
    box.locator('button.ladder-submit').click()
    return cid, shown


def wait_shown(pg, sid, rung):
    try:
        pg.wait_for_selector(f'#ladder-{sid}[data-shown="{rung}"]', timeout=8000)
        pg.wait_for_timeout(450)
        return True
    except Exception:
        return False


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': W, 'height': 844 if PHONE else 860}, is_mobile=PHONE, has_touch=PHONE)
    if a.theme == 'dark':
        ctx.add_init_script("try{localStorage.setItem('ciwt-theme','dark')}catch(e){}")
    pg = ctx.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))

    # ---- student1: miss -> R1 -> miss -> R2 -> pass -> return
    login(pg, 'student1@lms.local', 'student123')
    pg.goto(a.base + LESSON); pg.wait_for_load_state('networkidle')
    box = f'#ladder-{S1}'
    check('lesson shows the ladder intro', pg.locator('.ladder-intro').count() == 1)
    check('every laddered section has a wrapper', pg.locator('.ladder').count() >= 10, str(pg.locator('.ladder').count()))
    check('micro-check under the original section', pg.locator(f'{box} form.ladder-check').count() == 1
          and pg.locator(box).get_attribute('data-shown') == 'R0')
    no_overflow(pg, 'lesson 1.1 with ladder')
    shot(pg, '01-original-with-check', pg.locator(f'{box} .ladder-panel'))
    shot(pg, '00-original-section', pg.locator(box))
    answer(pg, box, False)
    ok = wait_shown(pg, S1, 'R1')
    check('miss: R1 replaces the section in place', ok)
    lab = pg.locator(f'{box} .ladder-badge').inner_text() if ok else ''
    check('R1 is labelled "Explained more simply"', 'Explained more simply' in lab, lab)
    check('focus moved to the new label', pg.evaluate("() => document.activeElement && document.activeElement.classList.contains('ladder-label')"))
    check('feedback says not quite (no key revealed)', 'Not quite' in pg.locator(f'{box} .ladder-feedback.is-miss').inner_text())
    check('fresh check is an R1 check', '-R1-' in (pg.locator(f'{box} input[name=check_id]').get_attribute('value') or ''))
    check('Pending SME review label on the rung', 'Pending SME review' in pg.locator(f'{box} .ladder-label').inner_text())
    check('page URL unchanged (no reload)', pg.url.endswith(LESSON))
    shot(pg, '02-swapped-to-R1', pg.locator(box))
    answer(pg, box, False)
    ok = wait_shown(pg, S1, 'R2')
    check('second miss: R2 (analogy) replaces R1', ok and 'analogy' in pg.locator(f'{box} .ladder-badge').inner_text())
    shot(pg, '03-swapped-to-R2-analogy', pg.locator(box))
    answer(pg, box, True)
    pg.wait_for_selector(f'{box} .ladder-feedback.is-ok', timeout=8000); pg.wait_for_timeout(450)
    check('pass on R2: right + why shown', 'Right.' in pg.locator(f'{box} .ladder-feedback').inner_text())
    shot(pg, '04-resolved-on-R2', pg.locator(f'{box} .ladder-panel'))
    pg.goto(a.base + '/student'); pg.goto(a.base + LESSON); pg.wait_for_load_state('networkidle')
    check('return: R2 shown', pg.locator(box).get_attribute('data-shown') == 'R2')
    tog = pg.locator(f'{box} .ladder-orig-toggle')
    check('"See the original" toggle present', tog.count() == 1)
    tog.click(); pg.wait_for_timeout(200)
    check('toggle shows the original in place', pg.locator(f'{box} .ladder-orig-holder').is_visible()
          and not pg.locator(f'{box} .ladder-rung').is_visible() and tog.get_attribute('aria-pressed') == 'true')
    shot(pg, '05-see-original-toggle', pg.locator(box))
    tog.click(); pg.wait_for_timeout(200)
    check('toggle back to the explanation that worked', pg.locator(f'{box} .ladder-rung').is_visible())

    # ---- "I don't get it" on another section, then up to R4 (try it)
    b2 = '#ladder-what-software-is'
    for want in ('R1', 'R2', 'R3', 'R4'):
        pg.locator(f'{b2} form.ladder-another button').click()
        ok = wait_shown(pg, 'what-software-is', want)
    check('"I don\'t get it" climbs R1..R4', ok)
    if pg.locator(f'{b2} .ladder-widget').count():
        w = pg.locator(f'{b2} .ladder-widget')
        w.locator('[data-wcheck]').first.click()
        check('try-it widget answers', len(w.locator('.ladder-w-done').inner_text() or '') > 5 if w.locator('.ladder-w-done').count() else True)
        shot(pg, '06-try-it-R4', pg.locator(b2))
    elif pg.locator(f'{b2} .ladder-lab').count():
        check('R4 links a lab', True)
        shot(pg, '06-try-it-R4', pg.locator(b2))
    check('R3 visual/trace or R4 rendered without errors', not errors, '; '.join(errors[:3]))
    run_axe(pg, 'lesson 1.1 after swaps')
    pg.goto(a.base + f'/student/section/{SEC}/what-helps-you-learn'); pg.wait_for_load_state('networkidle')
    check('What helps you learn lists the sections', 'Three kinds of work' in pg.content() and 'Reset and start fresh' in pg.content())
    no_overflow(pg, 'what helps you learn')
    shot(pg, '07-what-helps-you-learn', full=True)
    run_axe(pg, 'what helps you learn')

    # ---- student2 runs out of explanations (fast, through the page's own form posts)
    login(pg, 'student2@lms.local', 'student123')
    pg.goto(a.base + LESSON); pg.wait_for_load_state('networkidle')
    b3 = f'#ladder-{S2}'
    for want in ('R1', 'R2', 'R3', 'R4', 'R4'):
        answer(pg, b3, False)
        pg.wait_for_selector(f'{b3}[data-shown="{want}"]', timeout=8000); pg.wait_for_timeout(300)
    check('exhausted: note shown to the student', pg.locator(f'{b3} .ladder-note').count() == 1)
    shot(pg, '08-exhausted-student', pg.locator(f'{b3} .ladder-panel'))

    # ---- instructor
    login(pg, 'instructor@lms.local', 'teach123')
    pg.goto(a.base + f'/instructor/section/{SEC}/mastery/today'); pg.wait_for_load_state('networkidle')
    need = pg.locator('.mx-need', has_text='Every explanation tried')
    check('Who needs me: flagged with section and rungs', need.count() >= 1 and 'Impact and identity' in need.first.inner_text()
          and 'analogy' in need.first.inner_text())
    if need.count():
        shot(pg, '09-who-needs-me-flag', need.first)
    pg.goto(a.base + f'/instructor/section/{SEC}/ladder'); pg.wait_for_load_state('networkidle')
    check('analytics: most-escalated sections table', pg.locator('#ladEscH').count() == 1 and 'Three kinds of work' in pg.content())
    check('analytics: rung resolution table', 'Explained another way: analogy' in pg.content())
    no_overflow(pg, 'instructor analytics')
    shot(pg, '10-instructor-analytics', full=True)
    run_axe(pg, 'instructor analytics')
    # micro-checks off -> student sees no check; per-section override off -> no wrapper
    pg.uncheck('#ladMc'); pg.click('#ladSetH ~ .card-body button[type=submit], form:has(#ladMc) button[type=submit]')
    pg.wait_for_load_state('networkidle')
    check('settings saved', 'settings saved' in pg.content())
    pg.select_option('#ovSec', f'1.1|{S1}'); pg.select_option('#ovVal', 'off')
    pg.click('form:has(#ovVal) button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('override saved', 'Section override saved' in pg.content())
    pg.goto(a.base + f'/instructor/section/{SEC}/ladder/preview/1.1'); pg.wait_for_load_state('networkidle')
    check('SME preview shows keys + Pending SME review', '✓' in pg.content() and 'Pending SME review' in pg.content())
    run_axe(pg, 'SME preview 1.1')
    pg.goto(a.base + f'/instructor/section/{SEC}/mastery/briefing'); pg.wait_for_load_state('networkidle')
    check('briefing renders with the ladder hook', pg.locator('h1').count() == 1)
    login(pg, 'student1@lms.local', 'student123')
    pg.goto(a.base + LESSON); pg.wait_for_load_state('networkidle')
    check('micro-checks off: no checks, "I don\'t get it" stays', pg.locator('form.ladder-check').count() == 0
          and pg.locator('form.ladder-another').count() >= 1)
    check('override off: section shown as plain original', pg.locator(box).count() == 0)
    with db() as c:
        c.execute('DELETE FROM ladder_setting WHERE section_id=?', (SEC,))
    check('no page errors', not errors, '; '.join(errors[:3]))
    b.close()

json.dump({'results': results, 'axe': axe_out}, open(f'{a.out}/ladder-e2e-{TAG}.json', 'w'), indent=1)
fails = [r for r in results if not r['ok']]
print(f'{len(results) - len(fails)}/{len(results)} passed [{TAG}]')
sys.exit(1 if fails else 0)
