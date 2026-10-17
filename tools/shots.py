"""Headless screenshots of key CIWT pages for each role at 3 widths.
usage: python shots.py <outdir> [base] [filter]"""
import sys, os, re
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; BASE = sys.argv[2] if len(sys.argv) > 2 else 'http://127.0.0.1:5050'
FILT = sys.argv[3] if len(sys.argv) > 3 else ''
os.makedirs(OUT, exist_ok=True)
SIZES = {'mobile': (390, 844), 'tablet': (820, 1180), 'desktop': (1440, 900)}
PAGES = {
  'anon': [('landing', '/'), ('login', '/login'), ('policy', '/policy/attention')],
  'student1@lms.local:student123': [
    ('student-home', '/student'), ('student-class', '/student/section/1'),
    ('lesson', '/student/module/1/1/lesson/1'), ('quiz', '/student/quiz/1/1'),
    ('labs', '/labs'), ('grades', '/student/grades'), ('grades-section', '/student/section/1/grades'),
  ],
  'instructor@lms.local:teach123': [
    ('instr-home', '/instructor'), ('instr-section', '/instructor/section/1'),
    ('attention', '/instructor/section/1/attention'), ('attention-student', '/instructor/section/1/attention/student/4'),
    ('attention-lesson', '/instructor/section/1/attention/lesson/1'),
    ('gradebook', '/instructor/section/1/gradebook'), ('item-analysis', '/analysis/test/1'),
  ],
  'admin@lms.local:admin123': [('admin', '/admin'), ('admin-analytics', '/admin/test-analytics')],
}
with sync_playwright() as p:
    b = p.chromium.launch()
    for who, pages in PAGES.items():
        for size, (w, h) in SIZES.items():
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1,
                                is_mobile=(size == 'mobile'), has_touch=(size != 'desktop'))
            pg = ctx.new_page()
            if who != 'anon':
                email, pw = who.split(':')
                pg.goto(BASE + '/login'); pg.fill('input[name=email]', email); pg.fill('input[name=password]', pw)
                pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
            for name, path in pages:
                if FILT and not re.search(FILT, name): continue
                try:
                    r = pg.goto(BASE + path, wait_until='networkidle', timeout=20000)
                    pg.wait_for_timeout(400)
                    sw = pg.evaluate("""()=>{const W=innerWidth;let mx=0;document.querySelectorAll('main, main *').forEach(e=>{const r=e.getBoundingClientRect(); if(r.right<=W+2||!r.width) return; let p=e.parentElement; while(p&&p.tagName!=='BODY'){const o=getComputedStyle(p).overflowX; if(o!=='visible'&&o!=='clip'&&p.tagName!=='HTML') return; p=p.parentElement} mx=Math.max(mx,r.right)}); return Math.round(mx)}""")
                    flag = ' OVERFLOW(%d)' % sw if sw > w + 2 else ''
                    pg.screenshot(path=f'{OUT}/{name}-{size}.png', full_page=False)
                    print(f'{r.status if r else "?"} {size:7} {name}{flag}')
                except Exception as e:
                    print('ERR', size, name, e)
            ctx.close()
    b.close()
