#!/usr/bin/env python3
"""Lightweight smoke checks against a running CIWT LMS (default http://127.0.0.1:5050)."""
import json
import sys
import urllib.request
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5050'
ROOT = Path(__file__).resolve().parent
REQUIRED = [
    'templates/base.html', 'templates/login.html', 'templates/admin_tqi.html',
    'templates/tqi.html', 'templates/tqi_report.html', 'templates/tqi_official.html',
    'templates/staff_sidebar.html', 'app.py',
]
fail = 0
print('--- files ---')
for rel in REQUIRED:
    if (ROOT / rel).is_file():
        print(f'OK  file {rel}')
    else:
        print(f'MISS file {rel}')
        fail += 1

print('--- http ---')
paths = ['/', '/login', '/demo', '/gaps', '/healthz']
ok = 0
for p in paths:
    url = BASE.rstrip('/') + p
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            body = r.read()
            if p == '/healthz':
                data = json.loads(body.decode())
                if not data.get('ok'):
                    print(f'FAIL {p}: {data}')
                    fail += 1
                    continue
            print(f'OK  {r.status} {p}')
            ok += 1
    except Exception as e:
        print(f'FAIL {p}: {e}')
        fail += 1
print(f'{ok}/{len(paths)} public routes reachable')
sys.exit(1 if fail else 0)
