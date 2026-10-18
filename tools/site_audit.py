"""Full-site visual + UX audit: every page for every role at 390/820/1280, light and dark.

usage: python tools/site_audit.py <outdir> [--base http://127.0.0.1:5077] [--only regex] [--themes light,dark]
       [--widths 390,820,1280] [--prep]
Writes <outdir>/<role>-<page>-<width>-<theme>.png (full page) and <outdir>/audit.json with per-page
metrics: HTTP status, horizontal overflow, interactive elements under 44x44 px (visible, in <main>),
inline style attributes, <style> blocks, transferred bytes / request count, render-blocking assets,
console errors. --prep creates sample data (a message, a ticket, a quiz attempt) - point the server
at a throwaway DATABASE_URL when using it.
"""
import argparse, json, os, re, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', default='http://127.0.0.1:5077'); ap.add_argument('--only', default='')
ap.add_argument('--themes', default='light,dark'); ap.add_argument('--widths', default='390,820,1280'); ap.add_argument('--prep', action='store_true')
ap.add_argument('--no-shots', action='store_true')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
B = a.base
ROLES = {'student': ('student1@lms.local', 'student123'), 'instructor': ('instructor@lms.local', 'teach123'), 'admin': ('admin@lms.local', 'admin123')}
PAGES = {
  'anon': [('landing', '/'), ('login', '/login'), ('login-teach', '/login?as=teach'), ('policy', '/policy/attention'),
           ('try', '/helix/try'), ('404', '/no-such-page'), ('student-redirect', '/student')],
  'student': [('home', '/student'), ('class', '/student/section/1'), ('module', '/student/module/1/1'),
              ('lesson', '/student/module/1/1/lesson/1'), ('quiz', '/student/quiz/1/1'), ('test', '/student/test/1/1'),
              ('labs', '/labs'), ('lab', '/labs/win-ipconfig'), ('labs-verify', '/labs/verify'), ('class-labs', '/class/1/labs'),
              ('skills', '/class/1/skills'), ('curriculum', '/class/1/curriculum'), ('grades', '/student/grades'),
              ('grades-class', '/student/section/1/grades'), ('inbox', '/messages'), ('msg-new', '/messages/new'), ('msg-thread', '/messages/{msg}'),
              ('tickets', '/tickets'), ('ticket-new', '/tickets/new'), ('search', '/search?q=dns'), ('attention', '/student/attention'),
              ('consent', '/helix/consent'), ('account', '/account'),
              ('mastery', '/student/section/1/mastery'), ('mastery-review', '/student/section/1/review/IT-1.1'), ('mastery-plan', '/student/section/1/plan'),
              ('mastery-daily', '/student/section/1/daily'), ('mastery-testout', '/student/section/1/testout/2'), ('403', '/admin'), ('404', '/student/module/1/999'),
              ('practice', '/practice'), ('practice-take', '{ptake}'), ('practice-result', '{presult}'), ('cert-coverage-403', '/staff/cert-coverage')],
  'instructor': [('home', '/instructor'), ('section', '/instructor/section/1'), ('gradebook', '/instructor/section/1/gradebook'),
                 ('gradebook-student', '/instructor/section/1/gradebook/student/4'),
                 ('mastery', '/instructor/section/1/mastery'), ('mastery-student', '/instructor/section/1/mastery/student/4'), ('mastery-today', '/instructor/section/1/mastery/today'), ('test-perf', '/instructor/section/1/test/1/performance'),
                 ('quiz-preview', '/instructor/section/1/quiz/1/preview'), ('test-preview', '/instructor/section/1/test/1/preview'),
                 ('attempt', '/instructor/attempt/185'), ('analytics', '/instructor/analytics'), ('test-analytics', '/instructor/test-analytics'),
                 ('course-perf', '/instructor/course/1/performance'), ('item-analysis', '/analysis/test/1'), ('curriculum', '/class/1/curriculum'),
                 ('tqi', '/class/1/tqi'), ('tqi-report', '/class/1/tqi/report'), ('tqi-official', '/class/1/tqi/official'),
                 ('live-labs', '/live-labs'), ('class-labs', '/class/1/labs'), ('skills', '/class/1/skills'), ('inbox', '/messages'),
                 ('msg-thread', '/messages/{msg}'), ('msg-new', '/messages/new'), ('attention', '/instructor/section/1/attention'),
                 ('convening', '/convening'), ('pilot', '/pilot'), ('gaps', '/gaps'), ('aschool', '/aschool'), ('account', '/account'),
                 ('cert-coverage', '/staff/cert-coverage'), ('cert-coverage-filtered', '/staff/cert-coverage?exam=A2&status=partial'), ('practice', '/practice')],
  'admin': [('home', '/admin'), ('classes', '/admin/classes'), ('people', '/admin/people'), ('curriculum-admin', '/admin/curriculum'), ('audit', '/admin/audit'), ('curriculum-log', '/admin/curriculum-log'), ('readiness', '/admin/readiness'),
            ('teaching-time', '/admin/teaching-time'), ('test-analytics', '/admin/test-analytics'), ('tickets', '/admin/tickets'),
            ('ticket', '/admin/tickets/{ticket}'), ('tqi', '/admin/tqi'), ('curriculum', '/class/1/curriculum'), ('demo', '/demo'),
            ('search', '/search?q=raid'), ('account', '/account'), ('cert-coverage', '/staff/cert-coverage')],
}
SMALL_JS = """() => {
  const out = []; const main = document.querySelector('main') || document.body;
  main.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea, [role=button], summary, label.btn').forEach(e => {
    let r = e.getBoundingClientRect(); if (!r.width || !r.height) return;
    if (e.type === 'checkbox' || e.type === 'radio') { const l = e.closest('label') || (e.labels && e.labels[0]) || e.closest('.form-check'); if (l) { const lr = l.getBoundingClientRect(); if (lr.height >= r.height) r = lr; } }
    const st = getComputedStyle(e); if (st.visibility === 'hidden' || st.display === 'none') return;
    // inline text links inside paragraphs are exempt (WCAG 2.5.8 inline exception)
    if (e.tagName === 'A' && getComputedStyle(e).display === 'inline' && e.closest('p, li, td, dd') && !e.classList.contains('btn')) return;
    if (r.height < 44 || r.width < 44) out.push((e.tagName + '.' + [...e.classList].slice(0, 2).join('.') + ' ' + (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 24)).trim() + ` ${Math.round(r.width)}x${Math.round(r.height)}`);
  });
  const W = innerWidth; let mx = 0, who = '';
  document.querySelectorAll('main *').forEach(e => { const r = e.getBoundingClientRect(); if (r.right <= W + 2 || !r.width) return;
    let p = e.parentElement; while (p && p.tagName !== 'BODY') { const o = getComputedStyle(p).overflowX; if (o !== 'visible' && o !== 'clip') return; p = p.parentElement; }
    if (r.right > mx) { mx = r.right; who = e.tagName + '.' + [...e.classList].slice(0, 2).join('.'); } });
  return { small: out, overflow: mx > W + 2 ? Math.round(mx) + ' ' + who : null, inlineStyles: document.querySelectorAll('main [style]').length,
           styleBlocks: document.querySelectorAll('body style').length, h1: [...document.querySelectorAll('h1')].map(h => h.innerText.trim().slice(0, 60)),
           docH: document.documentElement.scrollHeight };
}"""

def login(pg, role):
    em, pw = ROLES[role]
    pg.goto(B + '/login'); pg.fill('input[name=email]', em); pg.fill('input[name=password]', pw)
    pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')

def practice_prep(pg):
    """Start a full A+ Core 2 practice (left open) and a Network+ drill that is submitted, so both pages can be audited."""
    pg.goto(B + '/practice'); pg.locator('form:has(input[name=exam][value=A2]):not(:has(input[name=domain])) button').click()
    pg.wait_for_url('**/practice/attempt/*'); take = pg.url.replace(B, '')
    pg.goto(B + '/practice'); pg.locator('form:has(input[name=exam][value=N]):has(input[name=domain]) button').first.click()
    pg.wait_for_url('**/practice/attempt/*')
    pg.evaluate("() => document.getElementById('testForm').submit()"); pg.wait_for_url('**/result')
    return take, pg.url.replace(B, '')

def prep(b):
    ids = {}
    ctx = b.new_context(); pg = ctx.new_page(); login(pg, 'student')
    pg.goto(B + '/messages/new')
    sel = pg.locator('select[name=recipient_id]').first
    opts = sel.locator('option').all(); val = next((o.get_attribute('value') for o in opts if o.get_attribute('value')), None)
    if val: sel.select_option(val)
    pg.fill('input[name=subject]', 'Question about the DNS lab'); pg.fill('textarea[name=body]', 'Hi, in step 3 of the DNS lab my nslookup times out. Is that expected?')
    pg.locator('#msgForm button[type=submit], #msgForm [type=submit]').first.click(); pg.wait_for_load_state('networkidle')
    m = re.search(r'/messages/(\d+)', pg.url); ids['msg'] = m.group(1) if m else '1'
    pg.goto(B + '/tickets/new'); pg.locator('select[name=category]').select_option(index=1)
    pg.fill('input[name=subject]', 'Typo in lesson 1.1'); pg.fill('textarea[name=body]', 'Paragraph 2 says "IPv4 has 64-bit addresses".')
    pg.locator('main form button.btn-brand').last.click(); pg.wait_for_load_state('networkidle')
    # practice exams (pass 11): one attempt left open to take, one submitted for the score report
    ids['ptake'], ids['presult'] = practice_prep(pg)
    ctx.close()
    ctx = b.new_context(); pg = ctx.new_page(); login(pg, 'admin'); pg.goto(B + '/admin/tickets')
    t = pg.locator('a[href*="/admin/tickets/"]').first
    ids['ticket'] = re.search(r'/admin/tickets/(\d+)', t.get_attribute('href')).group(1) if t.count() else '1'
    ctx.close()
    json.dump(ids, open(os.path.join(a.out, 'ids.json'), 'w')); return ids

with sync_playwright() as p:
    b = p.chromium.launch()
    ids = prep(b) if a.prep else (json.load(open(os.path.join(a.out, 'ids.json'))) if os.path.exists(os.path.join(a.out, 'ids.json')) else {'msg': '1', 'ticket': '1', 'ptake': '/practice', 'presult': '/practice'})
    report = []
    for role, pages in PAGES.items():
        for theme in a.themes.split(','):
            for w in map(int, a.widths.split(',')):
                mob = w < 600
                ctx = b.new_context(viewport={'width': w, 'height': 844 if mob else (1180 if w < 1000 else 860)}, is_mobile=mob, has_touch=w < 1000)
                if theme == 'dark': ctx.add_init_script("try{localStorage.setItem('ciwt-theme','dark')}catch(e){}")
                pg = ctx.new_page(); errs = []; reqs = []
                pg.on('requestfinished', lambda r: reqs.append(r))
                pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
                pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)[:200]))
                if role != 'anon': login(pg, role)
                for name, path in pages:
                    if a.only and not re.search(a.only, f'{role}-{name}'): continue
                    path = path.format(**ids); errs.clear(); reqs.clear()
                    try:
                        r = pg.goto(B + path, wait_until='networkidle', timeout=30000); pg.wait_for_timeout(250)
                        m = pg.evaluate(SMALL_JS)
                        size = 0
                        for q in reqs:
                            try: s = q.sizes(); size += s.get('responseBodySize', 0) + s.get('responseHeadersSize', 0)
                            except Exception: pass
                        rec = dict(role=role, page=name, path=path, width=w, theme=theme, status=r.status if r else None, url=pg.url.replace(B, ''),
                                   bytes=size, requests=len(reqs), errors=list(errs), **m)
                        report.append(rec)
                        if not a.no_shots: pg.screenshot(path=f'{a.out}/{role}-{name}-{w}-{theme}.png', full_page=True)
                        print(f"{rec['status']} {role:10} {name:18} {w:4} {theme:5} small={len(m['small']):3} ovf={m['overflow'] or '-'} inl={m['inlineStyles']} kb={size//1024} err={len(errs)}", flush=True)
                    except Exception as e:
                        print('ERR', role, name, w, theme, str(e)[:120], flush=True)
                ctx.close()
    json.dump(report, open(os.path.join(a.out, 'audit.json'), 'w'), indent=1)
    b.close()
