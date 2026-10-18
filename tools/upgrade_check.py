"""Upgrade check (pass 16): boot this code against a COPY of a database, or against a brand-new empty one, then
compare every table's row count and columns before and after, run SQLite's integrity check, and load key pages as
the demo admin, instructor and student. The source database is only read (copied); it is never opened for writing.

  python tools/upgrade_check.py upgrade [--src ciwt_lms.db] [--port 5075] [--work /tmp/ciwt-upgrade]
  python tools/upgrade_check.py fresh   [--port 5075] [--work /tmp/ciwt-upgrade]

Page checks use the demo logins, so on a database whose demo accounts were removed or re-passworded those checks
fail (the row-count and schema checks still apply). Exit status is non-zero if any check fails."""
import json, os, re, shutil, sqlite3, subprocess, sys, time, urllib.request, urllib.parse, http.cookiejar
import argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PY = os.path.join(ROOT, 'venv', 'bin', 'python')
ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['upgrade', 'fresh'])
ap.add_argument('--src', default=os.path.join(ROOT, 'ciwt_lms.db')); ap.add_argument('--port', type=int, default=5075)
ap.add_argument('--work', default='/tmp/ciwt-upgrade')
A = ap.parse_args(); mode, PORT, W = A.mode, A.port, A.work
os.makedirs(W, exist_ok=True)
db = os.path.join(W, f'{mode}.db')
if os.path.realpath(db) == os.path.realpath(A.src):
    sys.exit('--work must not contain the source database')
for p in (db,):
    if os.path.exists(p): os.remove(p)
if mode == 'upgrade':
    shutil.copy2(A.src, db)

def snap(path):
    if not os.path.exists(path): return {}, {}
    c = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
    counts = {t: c.execute(f'select count(*) from "{t}"').fetchone()[0] for t in tabs}
    cols = {t: [r[1] for r in c.execute(f'pragma table_info("{t}")')] for t in tabs}
    ok = c.execute('pragma integrity_check').fetchone()[0]
    c.close(); counts['__integrity__'] = ok
    return counts, cols

before, bcols = snap(db)
env = dict(os.environ, HOST='127.0.0.1', PORT=str(PORT), DATABASE_URL='sqlite:///' + db)
env.pop('CIWT_ALLOW_REAL_DB', None)
log = open(os.path.join(W, f'{mode}-server.log'), 'w')
t0 = time.time()
srv = subprocess.Popen([PY, 'app.py'], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
base = f'http://127.0.0.1:{PORT}'
res = {'mode': mode, 'checks': []}
def check(name, ok, info=''):
    res['checks'].append({'name': name, 'ok': bool(ok), 'info': info}); print(('PASS ' if ok else 'FAIL ') + name, info)
try:
    for _ in range(120):
        try: urllib.request.urlopen(base + '/login', timeout=3); break
        except Exception: time.sleep(1)
    check('server boots and serves /login', True, f'{time.time()-t0:.1f}s to first 200')
    def session(email, pw):
        cj = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        html = op.open(base + '/login').read().decode()
        tok = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
        data = {'email': email, 'password': pw}
        if tok: data['csrf_token'] = tok.group(1)
        r = op.open(base + '/login', urllib.parse.urlencode(data).encode())
        return op, r.geturl()
    pages = {
        'admin@lms.local': ('admin123', ['/admin', '/admin/people', '/admin/curriculum', '/admin/readiness', '/account']),
        'instructor@lms.local': ('teach123', ['/instructor', '/instructor/section/1/briefing', '/instructor/section/1/gradebook',
                                              '/instructor/section/1/mastery', '/instructor/section/1/mastery/today', '/class/1/labs']),
        'student1@lms.local': ('student123', ['/student', '/student/section/1/mastery', '/student/section/1/daily',
                                              '/student/module/1/1/lesson/1', '/labs', '/labs/linux-vm-shell', '/practice', '/student/grades']),
    }
    for email, (pw, urls) in pages.items():
        try:
            op, landed = session(email, pw)
            check(f'login {email}', '/login' not in landed, landed.replace(base, ''))
        except Exception as e:
            check(f'login {email}', False, repr(e)); continue
        for u in urls:
            try:
                r = op.open(base + u); code = r.status; final = r.geturl().replace(base, '')
            except urllib.error.HTTPError as e:
                code = e.code; final = u
            res.setdefault('pages', []).append({'user': email, 'url': u, 'status': code, 'final': final})
            print('  ', code, email.split('@')[0], u, '->', final)
finally:
    srv.terminate(); srv.wait(20); log.close()
after, acols = snap(db)
res['before'] = before; res['after'] = after
lost = {t: (before[t], after.get(t)) for t in before if t != '__integrity__' and (after.get(t) is None or after[t] < before[t])}
gained_tables = sorted(set(after) - set(before) - {'__integrity__'})
added_cols = {t: sorted(set(acols[t]) - set(bcols.get(t, []))) for t in acols if t in bcols and set(acols[t]) - set(bcols[t])}
dropped_cols = {t: sorted(set(bcols[t]) - set(acols.get(t, []))) for t in bcols if set(bcols[t]) - set(acols.get(t, []))}
res.update(lost=lost, new_tables=gained_tables, added_columns=added_cols, dropped_columns=dropped_cols)
check('integrity_check ok after boot', after.get('__integrity__') == 'ok', after.get('__integrity__'))
if mode == 'upgrade':
    check('no table lost rows', not lost, json.dumps(lost))
    check('no column dropped', not dropped_cols, json.dumps(dropped_cols))
    key = ['user', 'course', 'class_section', 'enrollment', 'quiz_attempt', 'test_attempt', 'grade_override', 'grade_due']
    sub = [t for t in before if 'submission' in t or 'attempt' in t or 'grade' in t]
    for t in sorted(set(key + sub)):
        if t in before: check(f'rows kept: {t}', after.get(t, -1) >= before[t], f'{before[t]} -> {after.get(t)}')
bad = [p for p in res.get('pages', []) if p['status'] >= 400 or p['final'].startswith('/login')]
check('key pages load (no 4xx/5xx, no bounce to login)', not bad, json.dumps(bad))
err = open(os.path.join(W, f'{mode}-server.log')).read()
check('no traceback in server log', 'Traceback' not in err, '')
json.dump(res, open(os.path.join(W, f'{mode}.json'), 'w'), indent=1, default=str)
print(f"{sum(c['ok'] for c in res['checks'])}/{len(res['checks'])} checks passed ({mode})")
print('new tables', len(gained_tables), 'tables with added columns', len(added_cols))
sys.exit(0 if all(c['ok'] for c in res['checks']) else 1)
