"""Playwright + axe sweep of the school-ready pages at 390/1280 px, light/dark. Usage:
   python tools/school_ready_shots.py OUT --base http://127.0.0.1:PORT --axe /path/axe.min.js"""
import argparse
import os
import sys

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', required=True); ap.add_argument('--axe', default='')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
B, AXE = a.base.rstrip('/'), open(a.axe).read() if a.axe else None
WHO = {'student': ('student1@lms.local', 'student123'), 'instructor': ('instructor@lms.local', 'teach123'),
       'admin': ('admin@lms.local', 'admin123')}
PAGES = [('instructor', '/instructor/sections', 'hub'), ('instructor', '/instructor/section/1/roster', 'roster'),
         ('instructor', '/instructor/section/1/setup', 'setup'), ('instructor', '/instructor/section/1/outcomes', 'outcomes'),
         ('instructor', '/instructor/section/1/privacy', 'privacy'), ('instructor', '/instructor/section/1/lti', 'lti'),
         ('instructor', '/instructor/section/1/ladder', 'ladder-settings'),
         ('student', '/my-data', 'my-data'), ('student', '/join', 'join'), ('student', 'LESSON', 'lesson-gate'),
         ('instructor', '/instructor/section/1', 'class-why'), ('instructor', '/instructor/section/1/mastery/today', 'who-needs-me'),
         ('student', '/labs/win-dns-break/analysis', 'lab-analysis'), ('student', '/contact', 'contact'), ('student', '/landing', 'landing'), ('student', '/privacy', 'privacy-page'), ('instructor', '/instructor/section/1/ladder?scope=course', 'ladder-course'), ('instructor', '/instructor/section/1/who-needs-me', 'who-needs-me-alias'),
         ('admin', '/admin/ferpa', 'ferpa'), ('admin', '/admin/audit-log', 'audit-log'), ('admin', '/accessibility', 'accessibility')]
fails, n = [], 0
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for w in (390, 1280):
        for theme in ('light', 'dark'):
            for who in ('student', 'instructor', 'admin'):
                c = b.new_context(viewport={'width': w, 'height': 900 if w > 500 else 844}, is_mobile=w < 500, has_touch=w < 500)
                c.add_init_script(f"try{{localStorage.setItem('ciwt-theme','{theme}')}}catch(e){{}}")
                p = c.new_page()
                p.goto(B + '/login'); p.fill('input[name=email]', WHO[who][0]); p.fill('input[name=password]', WHO[who][1])
                p.click('form button[type=submit]'); p.wait_for_load_state('networkidle')
                for role, path, name in PAGES:
                    if role != who:
                        continue
                    if path == 'LESSON':
                        path = os.environ.get('LESSON_PATH', '/student/module/1/1/lesson/1')
                    r = p.goto(B + path, wait_until='networkidle')
                    n += 1
                    if not r or r.status != 200 or '/login' in p.url:
                        fails.append(f'{name} {w} {theme}: HTTP {r.status if r else "?"} {p.url}')
                        continue
                    over = p.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
                    if over > 1:
                        fails.append(f'{name} {w} {theme}: {over}px sideways overflow')
                    if AXE:
                        p.add_script_tag(content=AXE)
                        v = p.evaluate("""async () => (await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}}))
                            .violations.map(v => v.id + '×' + v.nodes.length + ' ' + v.nodes.slice(0,2).map(n => n.target.join(' ')).join(' | '))""")
                        if v:
                            fails.append(f'{name} {w} {theme}: axe ' + '; '.join(v))
                    p.screenshot(path=f'{a.out}/{name}-{w}-{theme}.png', full_page=False)
                c.close()
    b.close()
print(f'{n} page checks, {len(fails)} problems')
for f in fails:
    print(' -', f)
sys.exit(1 if fails else 0)
