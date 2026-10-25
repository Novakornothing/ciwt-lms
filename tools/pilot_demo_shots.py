"""Pilot demo screenshots (before/after, annotated). Usage:
   python tools/pilot_demo_shots.py OUT --base http://127.0.0.1:PORT
Needs a server on a COPY of the DB. Student1 is reset to R0 on lesson 1.1 by the caller."""
import argparse
import os
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curriculum_v2 import ladder as LD  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
B = a.base.rstrip('/')
LESSON = '/student/module/1/1/lesson/1'
SID = '2-three-kinds-of-work'


def key_for(cid):
    for (c, label, sid), _ in LD.ladder().items():
        pre = f'L-{c}-{label}-{sid}-'
        if cid.startswith(pre):
            ent = LD.entry(c, label, sid)
            rung = cid[len(pre):].split('-')[0]
            return next(x for x in LD.rung_checks(ent, rung) if x['id'] == cid)['correct']


def login(b, w, who, pw, theme='light'):
    c = b.new_context(viewport={'width': w, 'height': 900 if w > 500 else 844}, device_scale_factor=2 if w > 500 else 3,
                      is_mobile=w < 500, has_touch=w < 500)
    c.add_init_script(f"try{{localStorage.setItem('novak-theme','{theme}')}}catch(e){{}}")
    p = c.new_page()
    p.goto(B + '/login'); p.fill('input[name=email]', who); p.fill('input[name=password]', pw)
    p.click('form button[type=submit]'); p.wait_for_load_state('networkidle')
    return c, p


def answer(p, right):
    box = p.locator(f'#ladder-{SID}')
    cid = box.locator('input[name=check_id]').get_attribute('value')
    key = key_for(cid)
    opts = box.locator('input[name=answer]')
    for i in range(opts.count()):
        v = opts.nth(i).get_attribute('value')
        if (v == key) == right:
            opts.nth(i).check()
            break
    shown = box.get_attribute('data-shown')
    box.locator('.ladder-submit').click()
    p.wait_for_function(f"""() => {{ const b = document.getElementById('ladder-{SID}');
        return b && (b.getAttribute('data-shown') !== '{shown}' || b.querySelector('.ladder-ok')); }}""", timeout=10000)
    p.wait_for_timeout(700)


def shot(p, sel, path, pad=12):
    el = p.locator(sel).first
    el.scroll_into_view_if_needed()
    p.wait_for_timeout(300)
    bb = el.bounding_box()
    p.screenshot(path=path, clip={'x': max(bb['x'] - pad, 0), 'y': max(bb['y'] - pad, 0),
                                  'width': min(bb['width'] + 2 * pad, p.viewport_size['width']), 'height': bb['height'] + 2 * pad},
                 full_page=False) if bb['height'] < p.viewport_size['height'] else el.screenshot(path=path)


def composite(b, panels, out, title, stacked=False):
    figs = ''.join(f"<figure><figcaption><b>{i + 1}.</b> {cap}</figcaption><img src='file://{img}'></figure>"
                   for i, (img, cap) in enumerate(panels))
    lay = 'flex-direction:column' if stacked else 'flex-direction:row'
    html = (f"<html><body style='margin:0;background:#eef1f5;font:15px system-ui;color:#13202f'>"
            f"<h1 style='font-size:20px;margin:16px 16px 0'>{title}</h1>"
            f"<style>figure{{margin:0;flex:1;background:#fff;border:1px solid #c5ccd6;border-radius:8px;padding:8px}}"
            f"figcaption{{padding:2px 4px 8px;font-weight:600}}img{{width:100%;display:block}}</style>"
            f"<div style='display:flex;{lay};gap:14px;padding:16px;align-items:flex-start'>{figs}</div></body></html>")
    hp = out + '.html'
    open(hp, 'w').write(html)
    c = b.new_context(viewport={'width': 1280 if not stacked else 430, 'height': 300}, device_scale_factor=2)
    p = c.new_page(); p.goto('file://' + hp); p.wait_for_timeout(500)
    p.screenshot(path=out, full_page=True); c.close(); os.remove(hp)


with sync_playwright() as pw:
    b = pw.chromium.launch()
    tmp = os.path.join(a.out, '_tmp'); os.makedirs(tmp, exist_ok=True)
    for w, name in ((1280, '01-before-after-explanation-swap-1280.png'), (390, '02-before-after-explanation-swap-390.png')):
        c, p = login(b, w, 'student1@lms.local', 'student123')
        if w == 390:   # second run: reset this section by starting from its original via a fresh student
            c.close(); c, p = login(b, w, 'student2@lms.local', 'student123')
        p.goto(B + LESSON, wait_until='networkidle')
        shot(p, f'#ladder-{SID}', f'{tmp}/a{w}.png')
        answer(p, False); answer(p, False)
        shot(p, f'#ladder-{SID}', f'{tmp}/b{w}.png')
        answer(p, True)
        shot(p, f'#ladder-{SID} .ladder-panel', f'{tmp}/c{w}.png')
        p.goto(B + LESSON + '#ladderGate', wait_until='networkidle')
        shot(p, '#ladderGate', f'{tmp}/d{w}.png')
        composite(b, [(f'{tmp}/a{w}.png', 'Before: the original explanation (R0) with its quick check'),
                      (f'{tmp}/b{w}.png', 'Two misses: the section swaps in place to R2 Analogy — badge + R0→R4 pill show where they are'),
                      (f'{tmp}/c{w}.png', 'Pass: the section is verified and a one-tap “Next section ↓” chip appears'),
                      (f'{tmp}/d{w}.png', 'The gate counts it (“X of Y sections verified”, top and bottom) and says what to do next')],
                  os.path.join(a.out, name), 'Adaptive difference: the explanation changes for this student, in place', stacked=(w == 390))
        c.close()
    # lab flags for student1: change before diagnosing, then repeat without change
    c, p = login(b, 1280, 'student1@lms.local', 'student123')
    p.goto(B + '/labs/win-dns-break', wait_until='networkidle')
    tok = p.evaluate("(document.querySelector('meta[name=csrf-token]')||{}).content||''")
    for cmd in ('ipconfig /flushdns', 'ipconfig /flushdns', 'ipconfig /flushdns', 'ping app.training.local', 'ipconfig /all'):
        p.request.post(B + '/labs/win-dns-break/cmd', data={'command': cmd}, headers={'X-CSRFToken': tok})
    p.goto(B + '/labs/win-dns-break/analysis', wait_until='networkidle')
    shot(p, '.lpa-why', f'{tmp}/e.png')
    cta = p.locator('.lpa-cta').first
    href = cta.get_attribute('href') if cta.count() else None
    if href:
        p.goto(B + href if href.startswith('/') else href, wait_until='networkidle')
        sid = href.split('#ladder-sec-')[-1]
        shot(p, f'#ladder-{sid}', f'{tmp}/f.png')
        composite(b, [(f'{tmp}/e.png', 'Lab process analysis: each flagged habit has a re-teach button'),
                      (f'{tmp}/f.png', 'One click opens that lesson section directly on the recommended explanation rung')],
                  os.path.join(a.out, '04-lab-analysis-to-ladder-rung-1280.png'), 'From a lab mistake to the explanation that re-teaches it')
    c.close()
    c, p = login(b, 1280, 'instructor@lms.local', 'teach123')
    p.goto(B + '/instructor/section/1', wait_until='networkidle')
    shot(p, 'section[aria-labelledby=whyH]', f'{tmp}/g.png')
    p.goto(B + '/instructor/section/1/ladder', wait_until='networkidle')
    shot(p, '.page-hero', f'{tmp}/h.png')
    composite(b, [(f'{tmp}/g.png', 'Why this student is struggling: Where stuck · What clicked badge · Lab/Helix tags · one-click next actions'),
                  (f'{tmp}/h.png', 'What finally clicked for the class (explanation style that resolved struggles)')],
              os.path.join(a.out, '03-why-student-is-struggling-1280.png'), 'Instructor view: why a student struggles, and what works')
    c.close()
    c = b.new_context(viewport={'width': 1280, 'height': 800}); p = c.new_page()
    p.goto(B + '/landing', wait_until='networkidle')
    p.evaluate("document.querySelectorAll('details').forEach((d, i) => { if (i < 2) d.open = true })")
    p.screenshot(path=os.path.join(a.out, '05-novakornothing-landing-privacy-faq-1280.png'), full_page=True)
    c.close()
    b.close()
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
print('ok')
