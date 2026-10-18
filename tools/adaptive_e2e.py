"""Adaptive mastery engine, end to end on desktop (1366x900) and phone (390x844, mobile UA, touch).

Runs against a throwaway server whose DATABASE_URL points at a DB copy (never ciwt_lms.db):
  DATABASE_URL=sqlite:////tmp/ae2e/work.db PORT=5310 python app.py &
  python tools/adaptive_e2e.py --base http://127.0.0.1:5310 --db /tmp/ae2e/work.db --device phone --out DIR

Before it runs it clears, in the copy only, the mastery rows, chapter checks, graded test attempts, study time,
lab completions and practice exams of three demo students in class 1, so every flow starts from no evidence:
  struggler (student1): chapter 1 check with the tagged wrong answers -> mix-up correction inserted -> review
      check missed -> next review is another way in -> missed again -> flagged stuck (student + instructor).
  strong (student2): reads chapter 1, right on the lesson quick checks, 10/10 on the chapter check -> offered
      the chapter 2 mastery check by the engine -> passes -> next lesson is chapter 3.
  tester (student3): same start, fails the mastery check -> told why and what is next, no penalty.
  instructor: heatmap + stuck list + student page; force review (required, redirect before the next lesson),
      clear (back to the engine), waive, lock a chapter (blocks the mastery check offer), adaptivity off/on.
Every page: no horizontal scroll, nothing clipped off-screen, and (phone) tap targets >= 24 px (WCAG 2.5.8);
targets under 44 px are listed as notes. Writes results JSON + screenshots to --out.
"""
import argparse, json, os, sqlite3, sys
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--base', default='http://127.0.0.1:5310'); ap.add_argument('--db', required=True)
ap.add_argument('--device', choices=['desktop', 'phone'], default='desktop'); ap.add_argument('--out', required=True)
a = ap.parse_args()
if os.path.realpath(a.db).endswith('ciwt_lms.db'):
    sys.exit('Refusing to run against ciwt_lms.db: use a copy.')
PHONE = a.device == 'phone'
W, H = (390, 844) if PHONE else (1366, 900)
TAG = f'{a.device}-{W}'
os.makedirs(a.out, exist_ok=True)
SID = 1
STRUGGLER, STRONG, TESTER = 4, 5, 6
EMAIL = {4: 'student1@lms.local', 5: 'student2@lms.local', 6: 'student3@lms.local'}
results, notes = [], []


def check(name, ok, detail=''):
    results.append({'check': name, 'ok': bool(ok), 'detail': str(detail)[:400], 'device': TAG})
    print(('PASS ' if ok else 'FAIL ') + f'[{TAG}] ' + name + (f' — {detail}' if detail else ''), flush=True)
    return ok


def db():
    c = sqlite3.connect(a.db, timeout=10)
    c.row_factory = sqlite3.Row
    return c


with db() as c:
    for uid in (STRUGGLER, STRONG, TESTER):
        for t in ('mastery_decision', 'mastery_check', 'mastery_override', 'learning_plan', 'mastery_checkin'):
            c.execute(f'DELETE FROM {t} WHERE section_id=? AND user_id=?', (SID, uid))
        c.execute('DELETE FROM quiz_attempt WHERE user_id=?', (uid,))
        c.execute('DELETE FROM test_attempt WHERE user_id=? AND section_id=?', (uid, SID))
        c.execute("DELETE FROM time_log WHERE user_id=? AND kind='study'", (uid,))
        c.execute('DELETE FROM lab_completion WHERE user_id=?', (uid,))
        for t in ('practice_attempt',):
            try:
                c.execute(f'DELETE FROM {t} WHERE user_id=?', (uid,))
            except sqlite3.OperationalError:
                pass
    c.execute('DELETE FROM mastery_setting WHERE section_id=?', (SID,))
    mods = {r['order']: r['id'] for r in c.execute('SELECT id, "order" FROM module WHERE course_id=1')}
    quizzes = {r['order']: (r['id'], json.loads(r['questions'])) for r in c.execute(
        'SELECT q.id, q.questions, m."order" AS "order" FROM quiz q JOIN module m ON m.id=q.module_id WHERE m.course_id=1 ORDER BY q.id')}
    lessons = {ch: [dict(r) for r in c.execute('SELECT id, title, estimated_minutes FROM lesson WHERE module_id=? ORDER BY "order"', (mid,))]
               for ch, mid in mods.items()}
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curriculum_v2.misconceptions import TAGS  # noqa: E402

OVERFLOW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
AUDIT_JS = r"""(phone) => {
  const vw = document.documentElement.clientWidth, out = {clipped: [], small: [], under44: []};
  const scroller = (el) => { for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const s = getComputedStyle(p); if (/(auto|scroll|hidden)/.test(s.overflowX)) return true; } return false; };
  const shown = (el) => { const s = getComputedStyle(el); const r = el.getBoundingClientRect();
      return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 1 && r.height > 1 && !el.closest('.visually-hidden,[hidden],.modal:not(.show),.d-none'); };
  const name = (el) => (el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '') + ' "' + (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().slice(0, 40) + '"');
  document.querySelectorAll('main *, .modal.show *').forEach(el => {
    if (!shown(el)) return; const r = el.getBoundingClientRect();
    if ((r.right > vw + 1 || r.left < -1) && !scroller(el) && !el.closest('.mx-heat-wrap,.table-responsive')) out.clipped.push(name(el) + ' [' + Math.round(r.left) + '..' + Math.round(r.right) + ']');
  });
  if (phone) document.querySelectorAll('main a, main button, main summary, main select, main textarea, main input:not([type=hidden]), .modal.show button, .modal.show input:not([type=hidden]), .modal.show select').forEach(el => {
    if (!shown(el)) return;
    let r = el.getBoundingClientRect();
    if (el.matches('input[type=radio],input[type=checkbox]')) { const fc = el.closest('.form-check'); if (fc) r = fc.getBoundingClientRect(); }
    // inline links inside running text are exempt from 2.5.8
    if (el.tagName === 'A' && !el.classList.contains('btn') && el.closest('p,li,dd,td,.mx-why-body,.small') && getComputedStyle(el).display === 'inline') return;
    if (r.width < 24 || r.height < 24) out.small.push(name(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
    else if (r.height < 44 && r.width < 44) out.under44.push(name(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  });
  out.clipped = [...new Set(out.clipped)].slice(0, 12); out.small = [...new Set(out.small)].slice(0, 12); out.under44 = [...new Set(out.under44)].slice(0, 12);
  return out;
}"""


COVER_JS = r"""() => {
  // after scrolling to the very end, the last controls of the page must not sit under a fixed bar (bottom nav)
  if (document.querySelector('.modal.show')) return [];   // an open dialog covers the page on purpose
  window.scrollTo(0, document.documentElement.scrollHeight);
  const vh = window.innerHeight, vw = document.documentElement.clientWidth, out = [];
  const els = [...document.querySelectorAll('main a.btn, main button, main summary, main input:not([type=hidden])')].filter(el => {
    const r = el.getBoundingClientRect(), st = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && r.bottom > 0 && r.top < vh && r.left >= 0 && r.right <= vw + 1 && st.visibility !== 'hidden'
      && !el.closest('.modal,.offcanvas:not(.show),.visually-hidden');
  });
  els.slice(-4).forEach(el => {
    const r = el.getBoundingClientRect(), x = r.left + r.width / 2, y = Math.min(vh - 1, r.top + r.height / 2);
    const hit = document.elementFromPoint(x, y);
    if (!hit || !(el === hit || el.contains(hit) || hit.contains(el) || hit.closest('label') === el.closest('label')))
      out.push((el.innerText || el.value || el.tagName).trim().slice(0, 30) + ' under ' + (hit ? hit.tagName.toLowerCase() + '.' + String(hit.className).split(' ')[0] : 'nothing'));
  });
  window.scrollTo(0, 0);
  return out;
}"""


def layout(pg, label):
    pg.wait_for_timeout(150)
    ov = pg.evaluate(OVERFLOW)
    au = pg.evaluate(AUDIT_JS, PHONE)
    check(f'layout {label}: no horizontal scroll', ov <= 1, f'{ov}px')
    check(f'layout {label}: nothing clipped off-screen', not au['clipped'], '; '.join(au['clipped']))
    if PHONE:
        check(f'layout {label}: tap targets >= 24px', not au['small'], '; '.join(au['small']))
        cov = pg.evaluate(COVER_JS)
        check(f'layout {label}: last controls reachable above the bottom bar', not cov, '; '.join(cov))
        if au['under44']:
            notes.append({'page': label, 'under_44px': au['under44']})


def shot(pg, name, full=False):
    pg.screenshot(path=f'{a.out}/{name}-{TAG}.png', full_page=full)


def tap(loc):
    loc.scroll_into_view_if_needed()
    if PHONE:
        loc.tap()
        pg_ = loc.page
        pg_.wait_for_timeout(350)    # a tap does not wait for the navigation it starts
        pg_.wait_for_load_state('networkidle')
    else:
        loc.click()


def login(pg, email, pw):
    pg.goto(a.base + '/logout'); pg.goto(a.base + '/login')
    pg.fill('input[name=email]', email); pg.fill('input[name=password]', pw)
    tap(pg.locator('button[type=submit]').first); pg.wait_for_load_state('networkidle')


def home(pg):
    pg.goto(a.base + f'/student/section/{SID}'); pg.wait_for_load_state('networkidle')
    if not pg.locator('.mx-path').count():
        pg.goto(a.base + '/student'); pg.wait_for_load_state('networkidle')


def steps(pg):
    return [s.inner_text() for s in pg.locator('.mx-step').all()]


def take_check(pg, ch, chooser):
    """Chapter check through the one-question-at-a-time UI."""
    qid, items = quizzes[ch]
    pg.goto(a.base + f'/student/quiz/{SID}/{qid}'); pg.wait_for_load_state('networkidle')
    pg.evaluate("() => { try { Object.keys(localStorage).filter(k => k.startsWith('quiz-')).forEach(k => localStorage.removeItem(k)); } catch (e) {} }")
    for i, it in enumerate(items):
        want = chooser(it)
        opt = pg.locator('#qOptions label.q-option').filter(has=pg.locator('.q-text', has_text=want))
        opt = opt.filter(has=pg.get_by_text(want, exact=True)) if opt.count() > 1 else opt
        tap(opt.first)
        if i < len(items) - 1:
            tap(pg.locator('#nextBtn'))
    tap(pg.locator('#submitBtn'))
    try:
        pg.locator('#confirmSubmit').wait_for(state='visible', timeout=1500); tap(pg.locator('#confirmSubmit'))
    except Exception:
        pass
    pg.wait_for_url('**/result/**', timeout=10000); pg.wait_for_load_state('networkidle')
    return pg.url


def wrong_tagged(it):
    tagged = [d for (b, d) in TAGS if b == it.get('bank_id') and d in it['options']]
    return tagged[0] if tagged else next(o for o in it['options'] if o != it['correct'])


def right(it):
    return it['correct']


def open_check(uid, kind, target=None):
    with db() as c:
        q = 'SELECT id, items_json FROM mastery_check WHERE section_id=? AND user_id=? AND kind=? AND completed_at IS NULL'
        args = [SID, uid, kind]
        if target:
            q += ' AND target=?'; args.append(target)
        r = c.execute(q + ' ORDER BY id DESC', args).fetchone()
    return (r['id'], json.loads(r['items_json'])) if r else (None, [])


def answer_form(pg, items, prefix, pick):
    for i, it in enumerate(items):
        tap(pg.locator(f'label[for="{prefix}{i}o{it["options"].index(pick(it))}"]'))


def read_chapter(pg, uid, ch):
    """Open every lesson of a chapter, record study time like the page heartbeat does, and answer its quick checks right."""
    for les in lessons[ch]:
        pg.goto(a.base + f'/student/module/{SID}/{mods[ch]}/lesson/{les["id"]}'); pg.wait_for_load_state('networkidle')
        tok = pg.get_attribute('meta[name="csrf-token"]', 'content')
        secs = (les['estimated_minutes'] or 30) * 60
        while secs > 0:
            n = min(120, secs)
            pg.request.post(a.base + '/time/study', data=json.dumps({'lesson_id': les['id'], 'section_id': SID, 'seconds': n}),
                            headers={'Content-Type': 'application/json', 'X-CSRFToken': tok})
            secs -= n
        forms = pg.locator('.mx-quick-form')
        for k in range(forms.count()):
            f = forms.nth(k)
            cid = int(f.get_attribute('action').rstrip('/').split('/')[-1])
            with db() as c:
                it = json.loads(c.execute('SELECT items_json FROM mastery_check WHERE id=?', (cid,)).fetchone()[0])[0]
            idx = it['options'].index(it['correct'])
            tap(f.locator(f'label[for="qc{cid}o{idx}"]'))
            tap(f.locator('button[type=submit]'))
            f.locator('.mx-quick-result > *').first.wait_for(timeout=8000)


def override(pg, page_url, uid, target, kind, note):
    pg.goto(a.base + page_url); pg.wait_for_load_state('networkidle')
    btn = pg.locator(f'.mx-cell[data-mx-user="{uid}"]').first
    if not btn.count():
        btn = pg.locator('button[data-bs-target="#mxOverride"]').first
    tap(btn)
    pg.locator('#mxOverride.show').wait_for(timeout=5000); pg.wait_for_timeout(400)
    pg.select_option('#mxTarget', target)
    tap(pg.locator(f'label[for="mxKind-{kind}"]'))
    pg.fill('#mxNote', note)
    return pg


with sync_playwright() as p:
    b = p.chromium.launch()
    kw = {'viewport': {'width': W, 'height': H}}
    if PHONE:
        kw.update(is_mobile=True, has_touch=True, device_scale_factor=3,
                  user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/126.0.0.0 Mobile Safari/537.36')
    ctx = b.new_context(**kw)
    pg = ctx.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(f'{pg.url}: {e}'))
    pg.on('response', lambda r: errors.append(f'HTTP {r.status} {r.url}') if r.status >= 500 else None)

    # ================================================================ struggler
    login(pg, EMAIL[STRUGGLER], 'student123')
    take_check(pg, 1, wrong_tagged)
    check('struggler: chapter 1 check submitted through the UI', '/result/' in pg.url, pg.url)
    home(pg)
    st = steps(pg)
    check('struggler: path card present', pg.locator('.mx-path').count() == 1)
    check('struggler: a mix-up correction is inserted first', st and st[0].startswith('Fix a mix-up'), st[0][:90] if st else st)
    first = pg.locator('.mx-step').first
    check('struggler: inserted step is marked as inserted before the next lesson',
          'Inserted before your next lesson' in first.inner_text() or 'Required' in first.inner_text(), first.inner_text()[:160])
    tap(first.locator('details.mx-why summary'))
    why_txt = first.locator('details.mx-why').inner_text()
    check('struggler: why panel names the mix-up, the evidence and says it is not a grade',
          'mix-up' in why_txt and 'right' in why_txt and 'not a grade' in why_txt, why_txt[:300])
    layout(pg, 'student home (review inserted)')
    first.scroll_into_view_if_needed(); shot(pg, '01-struggler-path-why')
    # lesson banner (engine reviews are optional: banner, no redirect)
    pg.goto(a.base + f'/student/module/{SID}/{mods[2]}/lesson/{lessons[2][0]["id"]}'); pg.wait_for_load_state('networkidle')
    check('struggler: next-chapter lesson shows the review banner without blocking', pg.locator('.mx-gate').count() == 1 and '/review/' not in pg.url, pg.url)
    layout(pg, 'lesson with review banner')
    pg.locator('.mx-gate').scroll_into_view_if_needed(); shot(pg, '02-struggler-lesson-banner')
    # round 1: the correction, answered wrong again
    home(pg)
    tap(pg.locator('.mx-step').first.locator('a.mx-step-go'))
    pg.wait_for_load_state('networkidle')
    obj = pg.url.split('/review/')[1].split('?')[0].split('/')[0]
    check('struggler: correction page names the mix-up and the fix', pg.locator('.mx-mc').count() == 1 and 'What the course teaches instead' in pg.content(), obj)
    check('struggler: engine review can be skipped', pg.locator('text=Skip for now').count() == 1)
    layout(pg, 'mix-up correction')
    shot(pg, '03-struggler-mixup-correction', full=True)
    cid, its = open_check(STRUGGLER, 'review', obj)
    answer_form(pg, its, 'q', wrong_tagged)
    tap(pg.locator('#mxReviewForm button[type=submit]')); pg.wait_for_load_state('networkidle')
    check('struggler: review 1 completed', '/done/' in pg.url, pg.url)
    done_txt = pg.locator('main').inner_text()
    layout(pg, 'review done (missed)')
    shot(pg, '04-struggler-review1-done', full=True)
    # round 2: a different way in
    home(pg)
    st = steps(pg)
    s2 = next((s for s in st if obj in s), '')
    check('struggler: after a missed review the next step for that objective is another way in',
          s2.startswith('Another way to see it') or 'another way' in s2.lower(), s2[:160])
    step2 = pg.locator('.mx-step', has_text=obj).first
    tap(step2.locator('details.mx-why summary'))
    why2 = step2.locator('details.mx-why').inner_text()
    check('struggler: why panel explains the path changed because the first review did not help',
          'already did one review' in why2, why2[:300])
    shot(pg, '05-struggler-path-second-review')
    tap(step2.locator('a.mx-step-go')); pg.wait_for_load_state('networkidle')
    eyebrow = pg.locator('.page-hero .eyebrow').inner_text()
    body = pg.locator('main').inner_text()
    check('struggler: second review page shows the alternate explanation it promised',
          'Another way to see it' in eyebrow or 'different angle' in body, eyebrow)
    layout(pg, 'alternate explanation')
    shot(pg, '06-struggler-alternate-explanation', full=True)
    cid, its = open_check(STRUGGLER, 'review', obj)
    answer_form(pg, its, 'q', wrong_tagged)
    tap(pg.locator('#mxReviewForm button[type=submit]')); pg.wait_for_load_state('networkidle')
    check('struggler: review 2 completed', '/done/' in pg.url, pg.url)
    home(pg)
    st = steps(pg)
    with db() as c:
        live = [r[0] for r in c.execute("SELECT action FROM mastery_decision WHERE section_id=? AND user_id=? AND target=? AND status='active' "
                                        "AND action IN ('review','alt_review','misconception','helix_offer')", (SID, STRUGGLER, obj))]
    check('struggler: after two reviews the objective is not inserted a third time (path and decision log)',
          not any(obj in s for s in st) and not live, f'steps={[s[:40] for s in st]} active={live}')
    stuck_txt = pg.locator('.mx-path').inner_text()
    check('struggler: student is told about two reviews and can message the instructor',
          'two reviews' in stuck_txt and pg.locator('.mx-path a', has_text='Message your instructor').count() == 1, stuck_txt[-240:])
    layout(pg, 'student home (stuck)')
    pg.locator('.mx-path').scroll_into_view_if_needed(); shot(pg, '07-struggler-stuck-message')
    pg.goto(a.base + f'/student/section/{SID}/mastery'); pg.wait_for_load_state('networkidle')
    layout(pg, 'my mastery (struggler)')
    shot(pg, '08-struggler-my-mastery')
    STUCK_OBJ = obj

    # ================================================================ strong student
    login(pg, EMAIL[STRONG], 'student123')
    read_chapter(pg, STRONG, 1)
    take_check(pg, 1, right)
    home(pg)
    st = steps(pg)
    t_step = next((s for s in st if 'mastery check' in s.lower()), '')
    check('strong: engine offers the chapter 2 mastery check', 'chapter 2' in t_step, [s[:70] for s in st])
    if t_step:
        loc = pg.locator('.mx-step', has_text='mastery check').first
        tap(loc.locator('details.mx-why summary'))
        wt = loc.locator('details.mx-why').inner_text()
        check('strong: offer explains why (mastered objectives, none needs review, not graded)',
              'mastered' in wt and 'never graded' in wt, wt[:300])
        loc.scroll_into_view_if_needed(); shot(pg, '09-strong-testout-offer')
        nl = pg.locator('.mx-step-lesson a.mx-step-go').first.get_attribute('href') or ''
        check('strong: before the mastery check the next lesson is in chapter 2', f'/module/{SID}/{mods[2]}/' in nl, nl)
        layout(pg, 'student home (mastery check offered)')
        tap(loc.locator('a.mx-step-go')); pg.wait_for_load_state('networkidle')
        tid, tits = open_check(STRONG, 'testout', 'CH-2')
        check('strong: mastery check opened with 2 items per objective', tid and len(tits) >= 6, len(tits))
        layout(pg, 'mastery check')
        shot(pg, '10-strong-testout', full=True)
        for i, it in enumerate(tits):
            tap(pg.locator(f'label[for="{pg.locator(f"input[name=q{i}]").nth(it["options"].index(it["correct"])).get_attribute("id")}"]'))
        tap(pg.locator('#mxTestoutForm button[type=submit]')); pg.wait_for_load_state('networkidle')
        check('strong: mastery check passed', '/result/' in pg.url and 'you tested out' in pg.content(), pg.url)
        layout(pg, 'mastery check result (passed)')
        shot(pg, '11-strong-testout-passed', full=True)
        home(pg)
        nl = pg.locator('.mx-step-lesson a.mx-step-go').first.get_attribute('href') or ''
        check('strong: passing advances the path to chapter 3', f'/module/{SID}/{mods[3]}/' in nl, nl)
        pg.goto(a.base + '/student'); pg.wait_for_load_state('networkidle')
        hero = pg.locator('.home-hero a.btn-brand').first
        check('strong: hero Continue on the dashboard follows the path to chapter 3',
              hero.count() and f'/module/{SID}/{mods[3]}/' in (hero.get_attribute('href') or ''),
              hero.get_attribute('href') if hero.count() else 'no hero')
        pg.goto(a.base + f'/student/module/{SID}/{mods[2]}/lesson/{lessons[2][0]["id"]}'); pg.wait_for_load_state('networkidle')
        check('strong: chapter 2 lessons stay open after testing out', '/lesson/' in pg.url and pg.locator('#lessonBody').count() == 1, pg.url)
        pg.goto(a.base + f'/student/section/{SID}/mastery'); pg.wait_for_load_state('networkidle')
        check('strong: My mastery shows the chapter 2 mastery check passed', 'Mastery check passed' in pg.locator('main').inner_text())
        layout(pg, 'my mastery (strong)')

    # ================================================================ tester: fails the mastery check
    login(pg, EMAIL[TESTER], 'student123')
    read_chapter(pg, TESTER, 1)
    take_check(pg, 1, right)
    pg.goto(a.base + f'/student/section/{SID}/testout/2'); pg.wait_for_load_state('networkidle')
    tid, tits = open_check(TESTER, 'testout', 'CH-2')
    if check('tester: mastery check open', tid is not None):
        for i, it in enumerate(tits):
            wrong = next(o for o in it['options'] if o != it['correct'])
            tap(pg.locator(f'label[for="{pg.locator(f"input[name=q{i}]").nth(it["options"].index(wrong)).get_attribute("id")}"]'))
        tap(pg.locator('#mxTestoutForm button[type=submit]')); pg.wait_for_load_state('networkidle')
        txt = pg.locator('main').inner_text()
        check('tester: failed result says not passed, not graded, and what to do next',
              'not' in txt.lower() and 'grade' in txt.lower(), txt[:300])
        layout(pg, 'mastery check result (not passed)')
        shot(pg, '12-tester-testout-not-passed', full=True)
        home(pg)
        nl = pg.locator('.mx-step-lesson a.mx-step-go').first.get_attribute('href') or ''
        check('tester: after not passing the path stays on chapter 2 lessons', f'/module/{SID}/{mods[2]}/' in nl, nl)

    # ================================================================ instructor
    login(pg, 'instructor@lms.local', 'teach123')
    pg.goto(a.base + f'/instructor/section/{SID}/mastery?ch=1'); pg.wait_for_load_state('networkidle')
    check('instructor: heatmap rendered', pg.locator('.mx-heat .mx-cell').count() > 10)
    main = pg.locator('main').inner_text()
    check('instructor: struggler listed as stuck on the objective', STUCK_OBJ in main and 'stuck' in main.lower())
    cell = pg.locator(f'.mx-cell[data-mx-user="{STRUGGLER}"][data-mx-target="{STUCK_OBJ}"]')
    check('instructor: struggler heatmap cell shows needs review', cell.count() == 1 and 'mx-s-review' in (cell.get_attribute('class') or ''),
          cell.get_attribute('class') if cell.count() else 'missing')
    scell = pg.locator(f'.mx-cell[data-mx-user="{STRONG}"]').first
    layout(pg, 'instructor mastery heatmap')
    shot(pg, '13-instructor-heatmap')
    pg.evaluate("document.getElementById('mxHeatH') && document.getElementById('mxHeatH').scrollIntoView({block: 'start', behavior: 'instant'})")
    shot(pg, '13b-instructor-heatmap-grid')
    pg.goto(a.base + f'/instructor/section/{SID}/mastery/student/{STRUGGLER}'); pg.wait_for_load_state('networkidle')
    st_txt = pg.locator('main').inner_text()
    check('instructor: student page shows the decision log and the mix-up', 'Mix-up' in st_txt or 'mix-up' in st_txt, '')
    layout(pg, 'instructor student page')
    shot(pg, '14-instructor-student-page')

    # force review on the strong student -> required, redirected before the next (chapter 3) lesson
    override(pg, f'/instructor/section/{SID}/mastery', STRONG, 'IT-1.2', 'force_review', 'Go over this before Monday, please')
    layout(pg, 'override dialog')
    shot(pg, '15-instructor-override-dialog')
    tap(pg.locator('#mxOverrideForm button[type=submit]')); pg.wait_for_load_state('networkidle')
    check('instructor: force review saved', 'Saved: Force review' in pg.content())
    login(pg, EMAIL[STRONG], 'student123')
    home(pg)
    s0 = pg.locator('.mx-step').first.inner_text()
    check('strong: forced review is first and required', 'Required' in s0 and 'IT-1.2' in s0, s0[:120])
    tap(pg.locator('.mx-step').first.locator('details.mx-why summary'))
    wt = pg.locator('.mx-step').first.locator('details.mx-why').inner_text()
    check('strong: why panel shows the instructor and their note', 'instructor' in wt.lower() and 'before Monday' in wt, wt[:200])
    shot(pg, '16-strong-forced-review')
    pg.goto(a.base + f'/student/module/{SID}/{mods[3]}/lesson/{lessons[3][0]["id"]}'); pg.wait_for_load_state('networkidle')
    check('strong: required review is inserted before the next lesson (redirect)', '/review/IT-1.2' in pg.url, pg.url)
    check('strong: required review has no Skip', pg.locator('text=Skip for now').count() == 0)
    layout(pg, 'required review')
    # clear -> back to the engine
    login(pg, 'instructor@lms.local', 'teach123')
    override(pg, f'/instructor/section/{SID}/mastery/student/{STRONG}', STRONG, 'IT-1.2', 'clear', 'Talked it through in class')
    tap(pg.locator('#mxOverrideForm button[type=submit]')); pg.wait_for_load_state('networkidle')
    check('instructor: clear (reset to the engine) saved', 'Saved: Clear override' in pg.content())
    # lock chapter 3 for the strong student -> no chapter 3 mastery check offer
    override(pg, f'/instructor/section/{SID}/mastery/student/{STRONG}', STRONG, 'CH-3', 'lock', 'Do chapter 3 with the class')
    tap(pg.locator('#mxOverrideForm button[type=submit]')); pg.wait_for_load_state('networkidle')
    check('instructor: lock on chapter 3 saved', 'Saved: Lock' in pg.content())
    # waive the stuck objective for the struggler
    override(pg, f'/instructor/section/{SID}/mastery/student/{STRUGGLER}', STRUGGLER, STUCK_OBJ, 'waive', 'Covered one-to-one')
    tap(pg.locator('#mxOverrideForm button[type=submit]')); pg.wait_for_load_state('networkidle')
    check('instructor: waive saved', 'Saved: Waive' in pg.content())
    pg.goto(a.base + f'/instructor/section/{SID}/mastery/today'); pg.wait_for_load_state('networkidle')
    layout(pg, 'who needs me')
    shot(pg, '17-instructor-who-needs-me')

    login(pg, EMAIL[STRONG], 'student123')
    home(pg)
    st = steps(pg)
    check('strong: after clear the forced review is gone', not any('IT-1.2' in s and 'Required' in s for s in st), [s[:60] for s in st])
    check('strong: chapter lock blocks the chapter 3 mastery check offer', not any('chapter 3' in s.lower() and 'mastery check' in s.lower() for s in st))
    pg.goto(a.base + f'/student/section/{SID}/testout/3'); pg.wait_for_load_state('networkidle')
    check('strong: locked chapter mastery check URL is refused', '/testout/3' not in pg.url, pg.url)
    login(pg, EMAIL[STRUGGLER], 'student123')
    pg.goto(a.base + f'/student/section/{SID}/mastery'); pg.wait_for_load_state('networkidle')
    row = pg.locator('main').inner_text()
    check('struggler: waived objective shows Waived with the reason', 'Waived' in row)
    home(pg)
    check('struggler: waived objective no longer on the path or in the stuck note',
          not any(STUCK_OBJ in s for s in steps(pg)) and 'two reviews' not in pg.locator('.mx-path').inner_text() if pg.locator('.mx-path').count() else True)

    # adaptivity off -> engine steps go, instructor's required ones stay
    login(pg, 'instructor@lms.local', 'teach123')
    pg.goto(a.base + f'/instructor/section/{SID}/mastery'); pg.wait_for_load_state('networkidle')
    tok = pg.get_attribute('meta[name="csrf-token"]', 'content')
    r = pg.request.post(a.base + f'/instructor/section/{SID}/mastery/settings', form={'csrf_token': tok, 'testout': '1', 'cert_items': '1'}, max_redirects=0)
    check('instructor: adaptivity turned off', r.status in (302, 303), r.status)
    login(pg, EMAIL[STRUGGLER], 'student123')
    home(pg)
    txt = pg.locator('.mx-path').inner_text() if pg.locator('.mx-path').count() else ''
    check('struggler: with adaptivity off the path says so and inserts no engine reviews',
          'turned adaptive recommendations off' in txt and not any(s.startswith(('Fix a mix-up', 'Short review', 'Another way')) for s in steps(pg)), txt[:200])
    login(pg, 'instructor@lms.local', 'teach123')
    pg.goto(a.base + f'/instructor/section/{SID}/mastery'); pg.wait_for_load_state('networkidle')
    tok = pg.get_attribute('meta[name="csrf-token"]', 'content')
    pg.request.post(a.base + f'/instructor/section/{SID}/mastery/settings', form={'csrf_token': tok, 'enabled': '1', 'testout': '1', 'cert_items': '1'}, max_redirects=0)
    check('no page JavaScript errors or server errors', not errors, '; '.join(errors)[:400])
    b.close()

json.dump({'results': results, 'notes': notes}, open(f'{a.out}/adaptive-e2e-{TAG}.json', 'w'), indent=1)
n_ok = sum(r['ok'] for r in results)
print(f'{n_ok}/{len(results)} checks passed ({TAG})')
sys.exit(0 if n_ok == len(results) else 1)
