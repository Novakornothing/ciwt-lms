"""Accessibility + responsive sweep: axe-core (WCAG 2.0/2.1 A+AA rules) on key pages for each role
at 390 / 820 / 1280 px, with screenshots and a horizontal-overflow check.

usage: python tools/a11y_sweep.py <outdir> [--base http://127.0.0.1:5050] [--axe /path/axe.min.js]
       [--only regex] [--no-shots] [--widths 390,820,1280]
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
ap.add_argument('--widths', default='390,820,1280')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
AXE = open(a.axe).read()
HEIGHT = {390: 844, 820: 1180, 1280: 800}
PAGES = {
    'anon': [('landing', '/'), ('login', '/login'), ('policy', '/policy/attention'), ('helix-try', '/helix/try')],
    'student1@lms.local:student123': [
        ('student-home', '/student'), ('student-class-goldpath', '/student/section/1'),
        ('lesson', '/student/module/1/1/lesson/1'), ('quiz', '/student/quiz/1/1'),
        ('labs', '/labs'), ('lab-detail', '/labs/gui-about'), ('grades', '/student/grades'),
        ('helix-mydata', '/student/attention'),
    ],
    'instructor@lms.local:teach123': [
        ('instr-home', '/instructor'), ('instr-section', '/instructor/section/1'),
        ('attention', '/instructor/section/1/attention'), ('attention-student', '/instructor/section/1/attention/student/4'),
        ('gradebook', '/instructor/section/1/gradebook'),
    ],
    'admin@lms.local:admin123': [('admin', '/admin'), ('admin-analytics', '/admin/test-analytics'),
                                 ('admin-tickets', '/admin/tickets')],
}
OVERFLOW_JS = """()=>{const W=innerWidth;let mx=0,who='';document.querySelectorAll('main, main *').forEach(e=>{const r=e.getBoundingClientRect(); if(r.right<=W+2||!r.width) return; let p=e.parentElement; while(p&&p.tagName!=='BODY'){const o=getComputedStyle(p).overflowX; if(o!=='visible'&&o!=='clip'&&p.tagName!=='HTML') return; p=p.parentElement} if(r.right>mx){mx=r.right;who=e.tagName+'.'+(e.className||'').toString().slice(0,40)}}); return mx?Math.round(mx)+' '+who:''}"""
report = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for who, pages in PAGES.items():
        for w in [int(x) for x in a.widths.split(',')]:
            mobile = w < 600
            ctx = b.new_context(viewport={'width': w, 'height': HEIGHT.get(w, 900)}, is_mobile=mobile, has_touch=w < 1000)
            pg = ctx.new_page()
            if who != 'anon':
                email, pw = who.split(':')
                pg.goto(a.base + '/login'); pg.fill('input[name=email]', email); pg.fill('input[name=password]', pw)
                pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
            for name, path in pages:
                if a.only and not re.search(a.only, name):
                    continue
                try:
                    r = pg.goto(a.base + path, wait_until='networkidle', timeout=25000)
                except Exception as e:
                    report.append({'page': name, 'width': w, 'error': str(e)[:200]}); continue
                pg.wait_for_timeout(350)
                pg.add_script_tag(content=AXE)
                res = pg.evaluate("""async () => { const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes: ['violations']});
                    return r.violations.map(v => ({id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.slice(0, 6).map(n => ({target: n.target.join(' '), summary: (n.failureSummary||'').slice(0, 220), html: n.html.slice(0, 160)})), count: v.nodes.length})); }""")
                ov = pg.evaluate(OVERFLOW_JS)
                report.append({'page': name, 'path': path, 'width': w, 'status': r.status if r else None, 'violations': res, 'overflow': ov})
                if not a.no_shots:
                    pg.screenshot(path=f'{a.out}/{name}-{w}.png', full_page=False)
            ctx.close()
    b.close()
json.dump(report, open(f'{a.out}/axe-report.json', 'w'), indent=1)
by_rule = defaultdict(lambda: {'n': 0, 'pages': set(), 'impact': ''})
for r in report:
    for v in r.get('violations', []):
        e = by_rule[v['id']]; e['n'] += v['count']; e['pages'].add(f"{r['page']}@{r['width']}"); e['impact'] = v['impact']
total = sum(e['n'] for e in by_rule.values())
print(f'pages checked: {len(report)}; violation nodes: {total}')
for k, e in sorted(by_rule.items(), key=lambda kv: -kv[1]['n']):
    print(f"  {k} [{e['impact']}] {e['n']} nodes on {len(e['pages'])} page/width: {', '.join(sorted(e['pages'])[:6])}")
for r in report:
    if r.get('overflow'):
        print(f"  overflow: {r['page']}@{r['width']} -> {r['overflow']}")
    if r.get('error') or (r.get('status') or 200) >= 400:
        print(f"  page problem: {r['page']}@{r['width']} {r.get('status')} {r.get('error', '')}")
