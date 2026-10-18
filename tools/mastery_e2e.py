"""Adaptive mastery end to end (pass 11), desktop 1280 and phone 390.

Runs against a throwaway server whose DATABASE_URL points at a DB copy (never ciwt_lms.db). Usage:
  HOST=127.0.0.1 DATABASE_URL=sqlite:////tmp/p11/e2e.db PORT=5078 python app.py &
  python tools/mastery_e2e.py <outdir> --base http://127.0.0.1:5078 --db /tmp/p11/e2e.db [--width 390] [--theme dark]
The script resets student1's mastery rows, chapter-check attempts and study time in the copy before it runs.
Flow: chapter check with tagged wrong answers -> review inserted on the path (+ "why am I seeing this") ->
lesson banner -> misconception correction -> lesson quick check with inline offer + dismiss -> daily review ->
learning plan -> instructor heatmap + override dialog (force review, then waive) -> who needs me ->
instructor unlock + student test-out pass.
"""
import argparse, json, os, sqlite3, sys
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', default='http://127.0.0.1:5078'); ap.add_argument('--db', required=True)
ap.add_argument('--width', type=int, default=1280); ap.add_argument('--theme', default='light'); ap.add_argument('--shots', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
if os.path.realpath(a.db).endswith('ciwt_lms.db'):
    sys.exit('Refusing to run against ciwt_lms.db: use a copy.')
W = a.width; PHONE = W < 600
SHOTS = a.shots or a.out
os.makedirs(SHOTS, exist_ok=True)
results = []


def check(name, ok, detail=''):
    results.append({'check': name, 'ok': bool(ok), 'detail': detail, 'width': W})
    print(('PASS ' if ok else 'FAIL ') + f'[{W}] ' + name + (f' — {detail}' if detail else ''))


def db():
    c = sqlite3.connect(a.db, timeout=10)
    c.row_factory = sqlite3.Row
    return c


SID, UID = 1, 4
with db() as c:
    for t in ('mastery_decision', 'mastery_check', 'mastery_override', 'learning_plan', 'mastery_checkin'):
        c.execute(f'DELETE FROM {t} WHERE section_id=? AND user_id=?', (SID, UID))
    c.execute('DELETE FROM mastery_setting WHERE section_id=?', (SID,))
    c.execute('DELETE FROM quiz_attempt WHERE user_id=?', (UID,))
    c.execute("DELETE FROM time_log WHERE user_id=? AND kind='study'", (UID,))
    quiz = c.execute('SELECT q.id, q.questions, m.id AS mid FROM quiz q JOIN module m ON m.id=q.module_id '
                     'WHERE m.course_id=1 AND m."order"=1 ORDER BY q.id LIMIT 1').fetchone()
    lessons = [r['id'] for r in c.execute('SELECT id FROM lesson WHERE module_id=? ORDER BY "order"', (quiz['mid'],))]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curriculum_v2.misconceptions import TAGS  # noqa: E402
items = json.loads(quiz['questions'])
answers = {}
for i, it in enumerate(items):
    tagged = [d for (b, d) in TAGS if b == it.get('bank_id')]
    answers[f'q{i}'] = tagged[0] if tagged else next(o for o in it['options'] if o != it['correct'])


def open_check(kind, target=None):
    with db() as c:
        q = 'SELECT id, items_json FROM mastery_check WHERE section_id=? AND user_id=? AND kind=? AND completed_at IS NULL'
        args = [SID, UID, kind]
        if target:
            q += ' AND target=?'; args.append(target)
        r = c.execute(q + ' ORDER BY id DESC', args).fetchone()
    return (r['id'], json.loads(r['items_json'])) if r else (None, [])


OVERFLOW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"


def login(pg, email, pw):
    pg.goto(a.base + '/logout'); pg.goto(a.base + '/login')
    pg.fill('input[name=email]', email); pg.fill('input[name=password]', pw)
    pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')


def shot(pg, name, full=False):
    if (PHONE and name.endswith('-390')) or (not PHONE and name.endswith('-1280')):
        pg.screenshot(path=f'{SHOTS}/{name}.png', full_page=full)


def no_overflow(pg, label):
    ov = pg.evaluate(OVERFLOW)
    check(f'no horizontal overflow: {label}', ov <= 1, f'{ov}px')


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': W, 'height': 844 if PHONE else 800}, is_mobile=PHONE, has_touch=PHONE)
    if a.theme == 'dark':
        ctx.add_init_script("try{localStorage.setItem('ciwt-theme','dark')}catch(e){}")
    pg = ctx.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))

    # ---- student: a chapter check with tagged wrong answers
    login(pg, 'student1@lms.local', 'student123')
    pg.goto(a.base + '/student')
    tok = pg.get_attribute('meta[name="csrf-token"]', 'content')
    r = pg.request.post(a.base + f'/student/quiz/{SID}/{quiz["id"]}', form=dict(answers, csrf_token=tok), max_redirects=0)
    check('chapter check submitted', r.status in (302, 303), str(r.status))
    pg.goto(a.base + '/student'); pg.wait_for_load_state('networkidle')
    path = pg.locator('.mx-path')
    check('path card shows recommended next', path.count() == 1 and 'Recommended next for you' in path.inner_text())
    first = pg.locator('.mx-step').first
    check('review inserted as first step', first.count() and ('Fix a mix-up' in first.inner_text() or 'Short review' in first.inner_text()),
          first.inner_text()[:80] if first.count() else '')
    check('hero continue goes to the review', '/review/' in (pg.locator('.home-hero a.btn-brand').first.get_attribute('href') or ''))
    no_overflow(pg, 'student home')
    path.scroll_into_view_if_needed()
    shot(pg, 'student-path-review-inserted-390')
    why = first.locator('details.mx-why')
    why.locator('summary').click()
    check('why panel opens with plain reasons', why.get_attribute('open') is not None and 'not a grade' in why.inner_text())
    why.scroll_into_view_if_needed()
    shot(pg, 'why-am-i-seeing-this-390')
    shot(pg, 'why-am-i-seeing-this-1280')
    daily = pg.locator('.mx-daily-card')
    check('daily review card on home', daily.count() == 1 and 'question' in daily.inner_text())

    # ---- lesson banner before a chapter-1 lesson
    pg.goto(a.base + f'/student/module/{SID}/{quiz["mid"]}/lesson/{lessons[1]}')
    check('lesson banner shows the inserted review', pg.locator('.mx-gate').count() == 1)
    no_overflow(pg, 'lesson with banner')

    # ---- misconception correction (the inserted review)
    pg.goto(a.base + '/student')
    pg.locator('.mx-step').first.locator('a.mx-step-go').click(); pg.wait_for_load_state('networkidle')
    check('correction names the mix-up', pg.locator('.mx-mc').count() == 1 and 'What the course teaches instead' in pg.content())
    obj = pg.url.split('/review/')[1].split('?')[0]
    no_overflow(pg, 'misconception correction')
    shot(pg, 'misconception-correction-390')
    cid, its = open_check('review', obj)
    for i, it in enumerate(its):
        idx = it['options'].index(it['correct'])
        pg.locator(f'#q{i}o{idx}').check()
    pg.click('#mxReviewForm button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('review completed', 'done' in pg.url)

    # ---- quick check in a lesson: tagged distractor -> inline offer, dismiss
    pg.goto(a.base + f'/student/module/{SID}/{quiz["mid"]}/lesson/{lessons[0]}'); pg.wait_for_load_state('networkidle')
    forms = pg.locator('.mx-quick-form')
    check('lesson quick check present', forms.count() >= 1)
    offered = False
    for k in range(forms.count()):
        f = forms.nth(k)
        cidq = int(f.get_attribute('action').rstrip('/').split('/')[-1])
        with db() as c:
            it = json.loads(c.execute('SELECT items_json FROM mastery_check WHERE id=?', (cidq,)).fetchone()[0])[0]
        tagged = [d for (bk, d) in TAGS if bk == it.get('bank_id')]
        wrong = tagged[0] if tagged else next(o for o in it['options'] if o != it['correct'])
        f.locator(f'input[value="{wrong}"]').check()
        f.locator('button[type=submit]').click()
        f.locator('.mx-quick-result > *').first.wait_for(timeout=8000)
        if f.locator('.mx-struggle').count():
            offered = True
            f.scroll_into_view_if_needed()
            shot(pg, 'inline-struggle-offer-390')
            check('inline offer comes from the lessons and has Dismiss', 'lessons' in f.inner_text() and f.locator('[data-mx-dismiss]').count() == 1)
            f.locator('[data-mx-dismiss]').click()
            check('dismiss removes the offer', f.locator('.mx-struggle').count() == 0)
            break
    check('a missed quick check with a tagged distractor offered help inline', offered)

    # ---- daily review
    pg.goto(a.base + '/student/section/1/daily'); pg.wait_for_load_state('networkidle')
    did, dits = open_check('daily')
    check('daily review has 1-10 questions and an honest time', 1 <= len(dits) <= 10 and 'min' in pg.locator('h1').inner_text(), str(len(dits)))
    no_overflow(pg, 'daily review')
    shot(pg, 'daily-review-390')
    for i, it in enumerate(dits):
        pg.locator(f'#d{i}o{it["options"].index(it["correct"])}').check()
    pg.click('#mxDailyForm button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('daily review result', 'Done for today' in pg.content())

    # ---- learning plan
    pg.goto(a.base + '/student/section/1/plan')
    pg.fill('#mxExam', (date.today() + timedelta(days=35)).isoformat())
    pg.locator('#mxPref3').check()
    pg.click('form[action$="/plan"] button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('plan saved with weekly targets', pg.locator('.mx-week').count() >= 5 and 'not' in pg.locator('.mx-frame').inner_text())
    no_overflow(pg, 'learning plan')
    shot(pg, 'learning-plan-390')

    # ---- instructor: heatmap, override dialog (force review), then waive
    login(pg, 'instructor@lms.local', 'teach123')
    pg.goto(a.base + '/instructor/section/1/mastery?ch=1'); pg.wait_for_load_state('networkidle')
    check('heatmap rendered', pg.locator('.mx-heat .mx-cell').count() > 10)
    check('inserted reviews counted', pg.locator('.kpi-card').nth(1).locator('.kpi-value').inner_text().strip() != '0')
    no_overflow(pg, 'instructor mastery')
    pg.evaluate("document.getElementById('mxHeatH').closest('section,.card').scrollIntoView({block: 'start', behavior: 'instant'})")
    shot(pg, 'instructor-mastery-heatmap-1280')
    cell = pg.locator(f'.mx-cell[data-mx-user="{UID}"][data-mx-target="IT-1.4"]')
    cell.scroll_into_view_if_needed(); cell.click()
    pg.locator('#mxOverride.show').wait_for(timeout=5000); pg.wait_for_timeout(500)
    check('override dialog filled from the cell', 'IT-1.4' == pg.input_value('#mxTarget') and pg.input_value('#mxOverride [data-mx="user"]') == str(UID))
    pg.locator('#mxKind-force_review').check()
    pg.fill('#mxNote', 'Please go over protecting identity and privacy before the next lesson')
    shot(pg, 'override-dialog-1280')
    shot(pg, 'override-dialog-390')
    pg.click('#mxOverrideForm button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('override saved', 'Saved: Force review' in pg.content())

    login(pg, 'student1@lms.local', 'student123')
    pg.goto(a.base + '/student')
    step = pg.locator('.mx-step').first
    check('forced review is first and required', 'Required' in step.inner_text() and 'IT-1.4' in step.inner_text())
    redirected = False
    for lid in lessons:
        pg.goto(a.base + f'/student/module/{SID}/{quiz["mid"]}/lesson/{lid}')
        if '/review/IT-1.4' in pg.url:
            redirected = True
            break
    check('a required review is inserted before the next lesson', redirected)
    check('required review cannot be skipped', 'Skip for now' not in pg.content())

    login(pg, 'instructor@lms.local', 'teach123')
    pg.goto(a.base + f'/instructor/section/1/mastery/student/{UID}')
    btn = pg.locator('button[data-mx-target="IT-1.4"]').first
    btn.scroll_into_view_if_needed(); btn.click(); pg.locator('#mxOverride.show').wait_for(timeout=5000)
    pg.locator('#mxKind-waive').check(); pg.fill('#mxNote', 'Covered in class')
    pg.click('#mxOverrideForm button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('waive saved', 'Saved: Waive' in pg.content())
    # unlock the chapter-2 mastery check for this student
    pg.goto(a.base + '/instructor/section/1/mastery')
    pg.locator(f'.mx-cell[data-mx-user="{UID}"]').first.click(); pg.locator('#mxOverride.show').wait_for(timeout=5000)
    pg.select_option('#mxTarget', 'CH-2'); pg.locator('#mxKind-unlock').check(); pg.fill('#mxNote', 'Prior experience: try the check')
    pg.click('#mxOverrideForm button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('chapter unlock saved', 'Saved: Unlock' in pg.content())
    pg.goto(a.base + '/instructor/section/1/mastery/today'); pg.wait_for_load_state('networkidle')
    check('who needs me lists reasons, no score', pg.locator('.mx-need').count() >= 1 and 'No risk score' in pg.content())
    no_overflow(pg, 'who needs me')
    shot(pg, 'who-needs-me-1280')

    # ---- student: waived objective gone, test-out chapter 2
    login(pg, 'student1@lms.local', 'student123')
    pg.goto(a.base + '/student')
    check('waived review no longer required', 'IT-1.4' not in (pg.locator('.mx-step').first.inner_text() if pg.locator('.mx-step').count() else ''))
    pg.goto(a.base + '/student/section/1/testout/2'); pg.wait_for_load_state('networkidle')
    tid, tits = open_check('testout', 'CH-2')
    check('test-out offered after unlock', tid is not None and len(tits) >= 2, str(len(tits)))
    no_overflow(pg, 'test-out')
    for i, it in enumerate(tits):
        pg.locator(f'input[name="q{i}"][value="{it["correct"]}"]').check()
    pg.click('#mxTestoutForm button[type=submit]'); pg.wait_for_load_state('networkidle')
    check('test-out passed', '/result/' in pg.url and 'you tested out' in pg.content())
    shot(pg, 'testout-passed-390')
    check('no page JavaScript errors', not errors, '; '.join(errors)[:200])
    b.close()

ok = all(r['ok'] for r in results)
json.dump(results, open(f'{a.out}/mastery-e2e-{W}-{a.theme}.json', 'w'), indent=1)
print(f'{sum(r["ok"] for r in results)}/{len(results)} checks passed at {W}px ({a.theme})')
sys.exit(0 if ok else 1)
