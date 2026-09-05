#!/usr/bin/env python3
"""Lightweight smoke checks against a running CIWT LMS (default http://127.0.0.1:5050)."""
import sys
import urllib.request
import urllib.error

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5050'
paths = ['/', '/login', '/demo', '/gaps']
ok = 0
for p in paths:
    url = BASE.rstrip('/') + p
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            code = r.status
            body = r.read(200)
            print(f'OK  {code} {p}')
            ok += 1
    except Exception as e:
        print(f'FAIL {p}: {e}')
print(f'{ok}/{len(paths)} public routes reachable')
sys.exit(0 if ok == len(paths) else 1)
