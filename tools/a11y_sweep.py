"""Accessibility + responsive sweep: axe-core (WCAG 2.0/2.1 A+AA rules) on key pages for each role
at 390 / 820 / 1280 px, with screenshots and a horizontal-overflow check.

usage: python tools/a11y_sweep.py <outdir> [--base http://127.0.0.1:5050] [--axe /path/axe.min.js]
       [--only regex] [--no-shots] [--widths 390,820,1280] [--themes light,dark]
Dark mode is the stored theme (localStorage ciwt-theme=dark), set before every page loads.
Writes <outdir>/axe-report.json and prints a summary (violations by rule, impact, page).
axe-core: `npm install axe-core@4` anywhere and pass --axe <node_modules/axe-core/axe.min.js>.
"""
import argparse
import json
import os
import re
from collections import defaultdict

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', default='http://127.0.0.1:5050')
ap.add_argument('--axe', default='/tmp/axe/node_modules/axe-core/axe.min.js')
ap.add_argument('--only', default=''); ap.add_argument('--no-shots', action='store_true')
ap.add_argument('--widths', default='390,820,1280'); ap.add_argument('--themes', default='light')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
AXE = open(a.axe).read()
HEIGHT = {390: 844, 820: 1180, 1280: 800}
PAGES = {
    'anon': [('landing', '/'), ('login', '/login'), ('login-teach', '/login?as=teach'), ('policy', '/policy/attention'), ('helix-try', '/helix/try'), ('privacy', '/privacy')],
    'student1@lms.local:student123': [
        ('student-home', '/student'), ('student-class-goldpath', '/student/section/1'),
        ('lesson', '/student/module/1/1/lesson/1'), ('quiz', '/student/quiz/1/1'),
        ('labs', '/labs'), ('lab-detail', '/labs/gui-about'), ('grades', '/student/grades'),
        ('helix-mydata', '/student/attention'), ('class-labs', '/class/1/labs'), ('grades-class', '/student/section/1/grades'),
        ('inbox', '/messages'), ('account', '/account'),
        ('syllabus', '/section/1/materials/syllabus'), ('rubrics', '/section/1/materials/rubrics'), ('lab-cli', '/labs/win-ipconfig'),
        ('lab-ad', '/labs/win-ad-users'), ('lab-match', '/labs/hw-cables'), ('lab-config', '/labs/wifi-secure'),
        ('lab-build', '/labs/hw-pc-build'), ('lab-linux', '/labs/linux-shell'), ('lab-ios', '/labs/rtr-vlan-acl'),
        ('lab-vm', '/labs/linux-vm-perms'), ('lab-vm-net', '/labs/linux-vm-routing'), ('lab-ticket', '/labs/ticket-intake'), ('lab-classroom', '/labs/classroom/CL-7'),
        ('lab-ports', '/labs/win-laptop-ports'), ('lab-order', '/labs/ticket-method'),
        ('lesson-3.2', '/student/module/1/3/lesson/13'), ('lesson-4.3', '/student/module/1/4/lesson/19'), ('lesson-5.1', '/student/module/1/5/lesson/21'), ('lesson-6.3', '/student/module/1/6/lesson/28'),
        ('mastery-student', '/student/section/1/mastery'), ('mastery-review', '/student/section/1/review/IT-1.1'), ('mastery-review-alt', '/student/section/1/review/IT-1.1?variant=alt'),
        ('mastery-plan', '/student/section/1/plan'), ('mastery-daily', '/student/section/1/daily'), ('mastery-testout', '/student/section/1/testout/2'),
        ('helix-study', '/helix/study'), ('lesson-7.1', '/student/module/1/7/lesson/30'), ('lesson-10.1', '/student/module/1/10/lesson/42'), ('lesson-13.4', '/student/module/1/13/lesson/57'),
        ('lesson-cert-4.2', '/student/module/1/4/lesson/18'), ('lesson-cert-2.3', '/student/module/1/2/lesson/8'), ('lesson-cert-3.1', '/student/module/1/3/lesson/12'),
        ('lesson-cert-8.1', '/student/module/1/8/lesson/34'), ('lesson-cert-9.2', '/student/module/1/9/lesson/39'), ('lesson-cert-10.3', '/student/module/1/10/lesson/44'),
        ('lesson-cert-13.5', '/student/module/1/13/lesson/58'),
        ('lesson-cert-3.4', '/student/module/1/3/lesson/15'), ('lesson-cert-10.1', '/student/module/1/10/lesson/42'),
        ('lesson-cert-12.1', '/student/module/1/12/lesson/50'), ('lesson-cert-12.2', '/student/module/1/12/lesson/51'),
        ('lesson-cert-1.2', '/student/module/1/1/lesson/2'), ('lesson-cert-1.4', '/student/module/1/1/lesson/4'), ('practice', '/practice'), ('practice-take', '@practice-take'), ('practice-result', '@practice-result'),
    ],
    'instructor@lms.local:teach123': [
        ('instr-home', '/instructor'), ('instr-section', '/instructor/section/1'),
        ('attention', '/instructor/section/1/attention'), ('attention-student', '/instructor/section/1/attention/student/4'),
        ('gradebook', '/instructor/section/1/gradebook'),
        ('mastery-class', '/instructor/section/1/mastery'), ('mastery-class-ch1', '/instructor/section/1/mastery?ch=1'), ('mastery-class-student', '/instructor/section/1/mastery/student/4'), ('mastery-today', '/instructor/section/1/mastery/today'), ('briefing', '/instructor/section/1/briefing'),
        ('materials', '/instructor/materials'), ('materials-plans', '/instructor/materials/ITSUP/lesson-plans'),
        ('materials-key', '/instructor/materials/ITSUP/answer-key'), ('syllabus-settings', '/instructor/section/1/syllabus'),
        ('instr-lesson-13.1', '/student/module/1/13/lesson/54'), ('calibration', '/instructor/section/1/attention/calibration'), ('materials-labs', '/instructor/materials/ITSUP/lab-manual'),
        ('lab-results', '/instructor/section/1/labs/results'), ('lab-student', '/instructor/section/1/labs/student/4/win-ipconfig'),
        ('class-labs-instr', '/class/1/labs'),
        ('cert-coverage', '/staff/cert-coverage'), ('cert-coverage-filtered', '/staff/cert-coverage?exam=N&status=covered'),
    ],
    'admin@lms.local:admin123': [('admin', '/admin'), ('admin-classes', '/admin/classes'), ('admin-people', '/admin/people'),
                                 ('admin-curriculum', '/admin/curriculum'), ('admin-tqi', '/admin/tqi'),
                                 ('admin-analytics', '/admin/test-analytics'), ('admin-tickets', '/admin/tickets'),
                                 ('admin-privacy', '/admin/privacy?q=student1&user_id=4'), ('admin-accuracy', '/admin/helix/accuracy'),
                                 ('lesson-cert-netops-5.2', '/student/module/2/18/lesson/77'), ('lesson-cert-netops-5.3', '/student/module/2/18/lesson/78'),
                                 ('lesson-cert-netops-4.3', '/student/module/2/17/lesson/74'), ('lesson-cert-netops-6.3', '/student/module/2/19/lesson/82')],
}
OVERFLOW_JS = """()=>{const W=innerWidth;let mx=0,who='';document.querySelectorAll('main, main *').forEach(e=>{const r=e.getBoundingClientRect(); if(r.right<=W+2||!r.width) return; let p=e.parentElement; while(p&&p.tagName!=='BODY'){const o=getComputedStyle(p).overflowX; if(o!=='visible'&&o!=='clip'&&p.tagName!=='HTML') return; p=p.parentElement} if(r.right>mx){mx=r.right;who=e.tagName+'.'+(e.className||'').toString().slice(0,40)}}); return mx?Math.round(mx)+' '+who:''}"""
report = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for theme in a.themes.split(','):
     for who, pages in PAGES.items():
        for w in [int(x) for x in a.widths.split(',')]:
            mobile = w < 600
            ctx = b.new_context(viewport={'width': w, 'height': HEIGHT.get(w, 900)}, is_mobile=mobile, has_touch=w < 1000)
            if theme == 'dark':
                ctx.add_init_script("try{localStorage.setItem('ciwt-theme','dark')}catch(e){}")
            pg = ctx.new_page()
            if who != 'anon':
                email, pw = who.split(':')
                pg.goto(a.base + '/login'); pg.fill('input[name=email]', email); pg.fill('input[name=password]', pw)
                pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
            for name, path in pages:
                if a.only and not re.search(a.only, name):
                    continue
                try:
                    if path.startswith('@practice'):
                        # pass 11: start a practice drill through the real form (CSRF), optionally submit it
                        pg.goto(a.base + '/practice', wait_until='networkidle')
                        pg.locator('form:has(input[name=domain]) button').first.click(); pg.wait_for_url('**/practice/attempt/*')
                        if path == '@practice-result':
                            pg.evaluate("() => document.getElementById('testForm').submit()"); pg.wait_for_url('**/result')
                        r = pg.reload(wait_until='networkidle', timeout=25000)
                    else:
                        r = pg.goto(a.base + path, wait_until='networkidle', timeout=25000)
                except Exception as e:
                    report.append({'page': name, 'width': w, 'theme': theme, 'error': str(e)[:200]}); continue
                pg.wait_for_timeout(350)
                pg.add_script_tag(content=AXE)
                res = pg.evaluate("""async () => { const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes: ['violations']});
                    return r.violations.map(v => ({id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.slice(0, 6).map(n => ({target: n.target.join(' '), summary: (n.failureSummary||'').slice(0, 220), html: n.html.slice(0, 160)})), count: v.nodes.length})); }""")
                ov = pg.evaluate(OVERFLOW_JS)
                report.append({'page': name, 'path': path, 'width': w, 'theme': theme, 'status': r.status if r else None, 'violations': res, 'overflow': ov})
                if not a.no_shots:
                    pg.screenshot(path=f'{a.out}/{name}-{w}-{theme}.png', full_page=False)
            ctx.close()
    b.close()
json.dump(report, open(f'{a.out}/axe-report.json', 'w'), indent=1)
by_rule = defaultdict(lambda: {'n': 0, 'pages': set(), 'impact': ''})
for r in report:
    for v in r.get('violations', []):
        e = by_rule[v['id']]; e['n'] += v['count']; e['pages'].add(f"{r['page']}@{r['width']}/{r['theme']}"); e['impact'] = v['impact']
total = sum(e['n'] for e in by_rule.values())
for th in a.themes.split(','):
    n = sum(v['count'] for r in report if r.get('theme') == th for v in r.get('violations', []))
    print(f"  {th}: {sum(1 for r in report if r.get('theme') == th)} page/width checks, {n} violation nodes")
print(f'pages checked: {len(report)}; violation nodes: {total}')
for k, e in sorted(by_rule.items(), key=lambda kv: -kv[1]['n']):
    print(f"  {k} [{e['impact']}] {e['n']} nodes on {len(e['pages'])} page/width: {', '.join(sorted(e['pages'])[:6])}")
for r in report:
    if r.get('overflow'):
        print(f"  overflow: {r['page']}@{r['width']}/{r['theme']} -> {r['overflow']}")
    if r.get('error') or (r.get('status') or 200) >= 400:
        print(f"  page problem: {r['page']}@{r['width']}/{r['theme']} {r.get('status')} {r.get('error', '')}")
