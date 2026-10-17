"""Pass 10 e2e: the accuracy-study page end to end with a real face video as the fake webcam.
Joins the study, runs both rounds (server-assigned arms that differ in one factor), and checks the
DB holds exactly two numeric records for this visit, with no image-like fields in any upload.
The fake camera has no ground-truth gaze: the stored error is NOT an accuracy measurement, so the
script deletes its own records at the end (pass --keep to inspect them).

usage: python tools/helix_study_e2e.py <base> <face.y4m> <outdir> --db <db> [--email ...] [--keep]
"""
import argparse
import json
import re
import sqlite3
import sys

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('base'); ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--db', required=True); ap.add_argument('--email', default='student16@lms.local'); ap.add_argument('--keep', action='store_true')
a = ap.parse_args()
res = {'rounds': [], 'console': []}
uploads = []
MEDIA = re.compile(r'"(frame|frames|image|images|video|snapshot|jpeg|png|webp|pixels|landmarks|faceLandmarks|mesh|iris)"\s*:|data:image|data:video|[A-Za-z0-9+/=]{2000,}', re.I)


def do_round(pg, n):
    pg.click('#hxStudyStart')
    pg.wait_for_selector('#helixCalib', timeout=90000)
    for _ in range(80):
        if pg.locator('#hxPosGo').count() and pg.locator('#hxPosGo').is_enabled():
            pg.click('#hxPosGo'); break
        if pg.locator('#hxPosSkip').count() and pg.locator('#hxPosSkip').is_visible():
            pg.click('#hxPosSkip'); break
        pg.wait_for_timeout(250)
    for _ in range(120):
        if pg.locator('.hx-cal-help.is-result').count():
            break
        pending = pg.locator('.hx-cal-pt:not(.done)')
        if pending.count():
            try:
                pending.first.click(timeout=4000)
            except Exception:
                pass
        pg.wait_for_timeout(1000)
    pg.wait_for_selector('.hx-cal-help.is-result', timeout=120000)
    pg.screenshot(path=f'{a.out}/study-round{n}-result.png')
    pg.locator('#hxGo, #hxGoAnyway').first.click()
    pg.wait_for_function(f"() => document.querySelectorAll('#hxStudyOut li').length >= {n}", timeout=30000)
    res['rounds'].append(pg.locator('#hxStudyOut li').nth(n - 1).inner_text())


with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
                                '--use-file-for-fake-video-capture=' + a.video])
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}, permissions=['camera'])
    pg = ctx.new_page(); pg.set_default_timeout(60000)
    pg.on('pageerror', lambda e: res['console'].append('PAGEERROR: ' + str(e)[:240]))
    pg.on('request', lambda r: uploads.append({'url': r.url, 'body': (r.post_data_buffer or b'').decode('utf-8', 'replace')}) if r.method == 'POST' else None)
    pg.goto(a.base + '/login'); pg.fill('input[name=email]', a.email); pg.fill('input[name=password]', 'student123')
    pg.click('button[type=submit]'); pg.wait_for_load_state('networkidle')
    pg.goto(a.base + '/helix/study?delegate=CPU')
    if pg.locator('#hxStudyAgree').count():
        pg.check('#hxStudyAgree'); pg.click('form button.btn-brand'); pg.wait_for_load_state('networkidle')
    do_round(pg, 1)
    do_round(pg, 2)
    pg.wait_for_timeout(800)
    res['final_state'] = pg.locator('#hxStudyState').inner_text()
    pg.screenshot(path=f'{a.out}/study-done.png', full_page=True)
    b.close()

con = sqlite3.connect(a.db); con.row_factory = sqlite3.Row
uid = con.execute('select id from user where email=?', (a.email,)).fetchone()[0]
rows = [dict(r) for r in con.execute('select id, context, kind, pair_id, arm_method, arm_hires, device, browser, camera_res, valid, '
                                     'error_px, error_deg, calib_ms, points_json from helix_accuracy_record where user_id=? order by id', (uid,))]
res['records'] = rows
rec_posts = [u for u in uploads if '/api/helix/study/record' in u['url']]
res['privacy'] = {'record_posts': len(rec_posts), 'media_like': [u['url'] for u in uploads if MEDIA.search(u['body'])]}
two = len(rows) == 2 and rows[0]['pair_id'] == rows[1]['pair_id'] and all(r['context'] == 'study' for r in rows)
if two:
    arms = [((r['arm_method'] or '').startswith('follow'), bool(r['arm_hires'])) for r in rows]
    res['one_factor_differs'] = (arms[0][0] != arms[1][0]) != (arms[0][1] != arms[1][1])
res['pass'] = bool(two and res.get('one_factor_differs') and not res['privacy']['media_like'] and len(rec_posts) == 2
                   and not [c for c in res['console'] if 'PAGEERROR' in c])
if not a.keep:
    con.execute('delete from helix_accuracy_record where user_id=?', (uid,))
    con.execute('delete from helix_study_consent where user_id=?', (uid,))
    con.commit()
    res['cleaned_up'] = True
print(json.dumps(res, indent=1))
sys.exit(0 if res['pass'] else 1)
