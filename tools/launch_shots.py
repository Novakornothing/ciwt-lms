"""Launch screenshots + responsive/a11y check of the new pages (tutor, portfolio, institutions, outcomes, SSO).

  python tools/launch_shots.py OUT --base http://127.0.0.1:PORT [--axe /tmp/axe/node_modules/axe-core/axe.min.js]

Needs a running server on a throwaway DB (never the real ciwt_lms.db). Writes PNGs to OUT and prints a check summary;
exit status is non-zero if any page overflows sideways, returns an error, or has axe WCAG 2.1 AA violations."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.sync_api import sync_playwright  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--base', required=True); ap.add_argument('--axe', default='')
ap.add_argument('--lab', default='win-dns-break')
ap.add_argument('--skip-sweep', action='store_true', help='screenshots only')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
B = a.base.rstrip('/')
fails, n = [], 0
AXE = open(a.axe).read() if a.axe and os.path.exists(a.axe) else None
STU, INS, ADM = ('student1@lms.local', 'student123'), ('instructor@lms.local', 'teach123'), ('admin@lms.local', 'admin123')


def check(name, ok, detail=''):
    global n
    n += 1
    if not ok:
        fails.append(f'{name}: {detail}')


def ctx(b, w, theme, who=None):
    c = b.new_context(viewport={'width': w, 'height': 900 if w > 500 else 844}, device_scale_factor=2,
                      is_mobile=w < 500, has_touch=w < 500)
    c.add_init_script(f"try{{localStorage.setItem('novak-theme','{theme}')}}catch(e){{}}")
    p = c.new_page()
    if who:
        p.goto(B + '/login'); p.fill('input[name=email]', who[0]); p.fill('input[name=password]', who[1])
        p.click('form button[type=submit]'); p.wait_for_load_state('networkidle')
    return c, p


def audit(p, label):
    over = p.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check(f'no sideways overflow {label}', over <= 1, f'{over}px')
    if AXE:
        p.add_script_tag(content=AXE)
        v = p.evaluate("""async () => (await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}}))
                          .violations.map(v => v.id + '×' + v.nodes.length + ' ' + v.nodes.slice(0,2).map(n => n.target.join(' ')).join(' | '))""")
        check(f'axe {label}', not v, '; '.join(v))


def visit(p, path, label):
    r = p.goto(B + path, wait_until='networkidle')
    check(f'{label} loads', r and r.status == 200 and ('/login' not in p.url or path == '/login'), f'{r.status if r else "?"} {p.url}')
    return r


def composite(b, left, right, out, title_l, title_r):
    html = (f"<html><body style='margin:0;background:#e9edf2;font:600 18px system-ui'><div style='display:flex;gap:16px;padding:16px'>"
            f"<figure style='margin:0;flex:1'><figcaption style='padding:4px 0 8px'>{title_l}</figcaption><img src='file://{left}' style='width:100%;border:1px solid #c5ccd6'></figure>"
            f"<figure style='margin:0;flex:1'><figcaption style='padding:4px 0 8px'>{title_r}</figcaption><img src='file://{right}' style='width:100%;border:1px solid #c5ccd6'></figure></div></body></html>")
    hp = out + '.html'
    open(hp, 'w').write(html)
    c = b.new_context(viewport={'width': 1280, 'height': 200}, device_scale_factor=2)
    p = c.new_page(); p.goto('file://' + hp); p.wait_for_timeout(300)
    p.screenshot(path=out, full_page=True); c.close(); os.remove(hp)


with sync_playwright() as pw:
    b = pw.chromium.launch()
    # ---- demo institution with SAML (admin form, like a real admin would)
    c, p = ctx(b, 1280, 'light', ADM)
    p.goto(B + '/admin/institutions')
    if 'Coastal Community College' not in p.content():
        p.fill('#ni-name', 'Coastal Community College'); p.fill('#ni-slug', 'coastal'); p.fill('#ni-dom', 'coastal.edu')
        p.click('form button[type=submit]'); p.wait_for_load_state('networkidle')
        from institutional.saml import self_signed
        cfg = {'protocol': 'saml', 'idp_entity_id': 'https://idp.coastal.edu/idp/shibboleth',
               'idp_sso_url': 'https://idp.coastal.edu/idp/profile/SAML2/Redirect/SSO', 'idp_cert': self_signed('idp.coastal.edu')[1],
               'role_map': {'instructor': ['faculty'], 'admin': ['lms-admins']}}
        p.fill('#ie-sso', json.dumps(cfg, indent=2)); p.fill('#ie-logo', '/static/img/navy-n-128.png')
        p.eval_on_selector('#ie-p', "e => e.value = '#0b4f6c'"); p.eval_on_selector('#ie-a', "e => e.value = '#f2a541'")
        p.click('form.card button[type=submit]'); p.wait_for_load_state('networkidle')
    p.click('text=Coastal Community College'); p.wait_for_load_state('networkidle')
    check('demo institution saved', 'Give these to campus IT' in p.content() and 'idp.coastal.edu' in p.content(), p.url)
    c.close()

    # ---- responsive + a11y sweep of the new pages
    pages = [(STU, '/tutor', 'tutor'), (STU, '/portfolio', 'portfolio'), (INS, '/instructor/section/1/outcomes', 'outcomes-section'),
             (INS, '/instructor/section/1/tutor', 'tutor-instructor'), (ADM, '/admin/institutions', 'admin-institutions'),
             (ADM, '/admin/outcomes', 'admin-outcomes'), (None, '/t/coastal', 'tenant-landing'), (None, '/login', 'login-picker')]
    for w in (() if a.skip_sweep else (1280, 390)):
        for theme in ('light', 'dark'):
            for who in (STU, INS, ADM, None):
                c, p = ctx(b, w, theme, who)
                for who2, path, label in pages:
                    if who2 != who:
                        continue
                    visit(p, path, f'{label}-{w}-{theme}')
                    if label == 'tutor':
                        p.fill('#tutor-q', 'What does a 169.254 address mean?')
                        p.click('form:has(#tutor-q) button[type=submit]'); p.wait_for_load_state('networkidle')
                    audit(p, f'{label}-{w}-{theme}')
                c.close()

    # ---- 02 dynamic lab analysis: drive a simulated lab as the student, then open the analysis
    import interactive_labs as IL
    lab = IL.get_lab(a.lab)
    cmds = (lab.get('solution') or {}).get('commands') or IL.VERIFY_SEQUENCES.get(a.lab, [[]])[0]
    c, p = ctx(b, 1280, 'light', STU)
    visit(p, f'/labs/{a.lab}', 'lab')
    for cmd in cmds:
        p.fill('#termInput', cmd)
        with p.expect_response(lambda r: '/cmd' in r.url, timeout=15000):
            p.press('#termInput', 'Enter')
    p.wait_for_timeout(600)
    visit(p, f'/labs/{a.lab}/analysis', 'lab analysis')
    p.screenshot(path=f'{a.out}/02-dynamic-lab-analysis-1280.png', full_page=False)
    c.close()

    # ---- 03 helix attention, 04 gradebook (instructor)
    c, p = ctx(b, 1280, 'light', INS)
    visit(p, '/instructor/section/1/attention', 'attention'); p.screenshot(path=f'{a.out}/03-helix-attention-dashboard-1280.png')
    visit(p, '/instructor/section/1/gradebook', 'gradebook'); p.screenshot(path=f'{a.out}/04-gradebook-1280.png')
    visit(p, '/instructor/section/1/outcomes', 'outcomes'); p.screenshot(path=f'{a.out}/_outcomes.png')
    c.close()

    # ---- 05 mobile real-Linux lab, 06 student adaptive path
    c, p = ctx(b, 390, 'light', STU)
    visit(p, '/labs/linux-vm-shell', 'vm lab')
    p.click('#vmBoot')
    booted = False
    for i in range(120):     # keep the page "active" while v86 boots (an idle page triggers the attention check)
        p.mouse.move(40 + i % 7 * 30, 300 + i % 5 * 20)
        if p.locator('#vmTools:not([hidden])').count():
            booted = True
            break
        p.wait_for_timeout(2500)
    if booted:
        p.wait_for_timeout(1500)
        p.fill('#termInput', 'uname -sr; whoami; ls -la ~'); p.press('#termInput', 'Enter'); p.wait_for_timeout(5000)
        p.locator('#termInput').scroll_into_view_if_needed()
    check('real Linux VM booted on a phone viewport', booted)
    p.screenshot(path=f'{a.out}/05-mobile-linux-lab-390.png')
    visit(p, '/student/section/1/mastery', 'student path'); p.screenshot(path=f'{a.out}/06-student-path-390.png')
    c.close()

    # ---- 07 tutor + portfolio
    c, p = ctx(b, 1280, 'light', STU)
    visit(p, '/tutor', 'tutor'); p.fill('#tutor-q', 'Why would a PC get a 169.254 address?')
    p.click('form:has(#tutor-q) button[type=submit]'); p.wait_for_load_state('networkidle'); p.screenshot(path=f'{a.out}/_tutor.png')
    visit(p, '/portfolio', 'portfolio'); p.screenshot(path=f'{a.out}/_portfolio.png')
    c.close()
    composite(b, f'{a.out}/_tutor.png', f'{a.out}/_portfolio.png', f'{a.out}/07-ai-tutor-and-portfolio-1280.png',
              'AI tutor — answers cite lessons, rungs and glossary', 'Skills portfolio — verified competencies, lab badges, readiness')

    # ---- 08 outcomes + campus SSO
    c, p = ctx(b, 1280, 'light')
    visit(p, '/t/coastal', 'tenant'); p.goto(B + '/login'); p.wait_for_load_state('networkidle')
    p.screenshot(path=f'{a.out}/_sso.png'); c.close()
    composite(b, f'{a.out}/_outcomes.png', f'{a.out}/_sso.png', f'{a.out}/08-outcomes-and-sso-1280.png',
              'Institutional outcomes — real data, demo seed labelled', 'Campus SSO — branded sign-in with institution picker')
    for f in os.listdir(a.out):
        if f.startswith('_'):
            os.remove(os.path.join(a.out, f))
    b.close()

print(f'{n - len(fails)}/{n} checks passed')
for f in fails:
    print('FAIL', f)
sys.exit(1 if fails else 0)
