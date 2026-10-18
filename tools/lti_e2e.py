"""Browser e2e for LTI 1.3 against the local mock platform (not a real LMS).

Needs the tool running with LTI_ALLOW_LOOPBACK_HTTP=1 on a throwaway DB copy, e.g.
  HOST=127.0.0.1 LTI_ALLOW_LOOPBACK_HTTP=1 DATABASE_URL=sqlite:////tmp/x.db PORT=5078 python app.py
Then: python tools/lti_e2e.py [--tool http://127.0.0.1:5078] [--shots DIR]
Starts the mock on 5088 (stopped at the end), registers it through the admin UI, then:
teacher deep-links content (maps the LMS course to section 1), a learner launches a chapter check,
the teacher sends scores and syncs the roster. Exits non-zero on any failed check."""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--tool', default='http://127.0.0.1:5078')
ap.add_argument('--mock-port', type=int, default=5088)
ap.add_argument('--shots', default='')
a = ap.parse_args()
T, M = a.tool.rstrip('/'), f'http://127.0.0.1:{a.mock_port}'
results = []


def check(name, ok, detail=''):
    results.append((name, bool(ok)))
    print(('PASS ' if ok else 'FAIL ') + name + (f' — {detail}' if detail and not ok else ''), flush=True)


def shot(pg, name):
    if a.shots:
        os.makedirs(a.shots, exist_ok=True)
        pg.screenshot(path=os.path.join(a.shots, name + '.png'), full_page=True)


mock = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), 'lti_mock_platform.py'), '--tool', T,
                         '--port', str(a.mock_port), '--teacher-email', 'instructor@lms.local'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    buf = ''
    while '}' not in buf:
        line = mock.stdout.readline()
        if not line:
            raise SystemExit('mock platform did not start')
        buf += line
    reg = json.loads(buf[buf.index('{'):buf.index('}') + 1])
    for _ in range(50):
        try:
            urllib.request.urlopen(M + '/jwks', timeout=1)
            break
        except OSError:
            time.sleep(0.2)
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 1280, 'height': 900})
        pg = ctx.new_page()
        pg.goto(T + '/login'); pg.fill('input[name=email]', 'admin@lms.local'); pg.fill('input[name=password]', 'admin123')
        pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
        pg.goto(T + '/admin/lti/new?kind=other')
        pg.fill('#f-name', 'Mock LMS (local demo)'); pg.fill('#f-issuer', reg['issuer']); pg.fill('#f-client_id', reg['client_id'])
        pg.fill('#f-auth_login_url', reg['auth_login_url']); pg.fill('#f-auth_token_url', reg['auth_token_url'])
        pg.fill('#f-jwks_url', reg['jwks_url']); pg.fill('#f-deps', reg['deployment_id'])
        pg.check('#f-le')
        shot(pg, 'lti-admin-new')
        pg.click('form.card button[type=submit]'); pg.wait_for_load_state('networkidle')
        check('admin saves the registration', 'Mock LMS (local demo)' in pg.content())
        shot(pg, 'lti-admin-list')
        ctx.close()

        # teacher: deep linking from the mock LMS
        ctx = br.new_context(viewport={'width': 1280, 'height': 900})
        pg = ctx.new_page()
        pg.goto(M + '/start?user=mock-teacher-1&kind=deeplink'); pg.wait_for_load_state('networkidle')
        check('deep-link launch lands on the picker', '/lti/deep-link/' in pg.url, pg.url)
        if pg.locator('input[name=section_id]').count():
            pg.check('input[name=section_id][value="1"]')
            pg.click('button[name=pick_only]'); pg.wait_for_load_state('networkidle')
        check('picker lists course content', pg.locator('input[name=target]').count() > 5)
        pg.check('input[name=target][value="course"]')
        pg.check('input[name=target][value="quiz:1"]')
        lab = pg.locator('input[name=target][value^="lab:"]').first
        lab.check()
        shot(pg, 'lti-deep-link-picker')
        pg.click('.mx-dl-bar button[type=submit]'); pg.wait_for_load_state('networkidle')
        check('signed deep-link response accepted by the mock', 'Content added' in pg.content(), pg.content()[:300])
        check('three items returned', pg.locator('#dlitems li').count() == 3)
        shot(pg, 'lti-deep-link-return')
        ctx.close()

        # learner: resource link launch of the chapter check
        ctx = br.new_context(viewport={'width': 390, 'height': 844})
        pg = ctx.new_page()
        pg.goto(M + '/start?user=mock-student-1&kind=launch&target=quiz:1&rl=rl-quiz-1'); pg.wait_for_load_state('networkidle')
        check('learner launch opens the chapter check', re.search(r'/quiz/1', pg.url) is not None, pg.url)
        shot(pg, 'lti-learner-launch-390')
        ctx.close()

        # teacher: class LMS page, send scores, sync roster
        ctx = br.new_context(viewport={'width': 1280, 'height': 900})
        pg = ctx.new_page()
        pg.goto(T + '/login'); pg.fill('input[name=email]', 'instructor@lms.local'); pg.fill('input[name=password]', 'teach123')
        pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
        pg.goto(T + '/instructor/section/1/lti')
        check('class LMS page shows the mock course', 'Mock LMS course 101 (demo)' in pg.content())
        pg.click('text=Sync roster from the LMS'); pg.wait_for_load_state('networkidle')
        check('roster sync reports', 'Roster from the LMS' in pg.content())
        pg.click('text=Send scores to the LMS'); pg.wait_for_load_state('networkidle')
        check('score send reports', 'Scores to the LMS' in pg.content())
        shot(pg, 'lti-section-page')
        ctx.close()
        br.close()
finally:
    mock.terminate()
    try:
        mock.wait(5)
    except subprocess.TimeoutExpired:
        mock.kill()
n_fail = len([r for r in results if not r[1]])
print(f'{len(results) - n_fail}/{len(results)} checks passed')
sys.exit(1 if n_fail else 0)
