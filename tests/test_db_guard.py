"""Pass 13: importing app without DATABASE_URL must not touch the real ciwt_lms.db."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import app as lms

ROOT = Path(__file__).resolve().parents[1]


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def test_guard_rules():
    ok = lms.real_db_allowed
    assert not ok({}) and not ok({'CIWT_ALLOW_REAL_DB': '0'}) and not ok({'CIWT_ALLOW_REAL_DB': 'yes'})
    assert ok({'DATABASE_URL': 'sqlite:////tmp/x.db'}) and ok({'CIWT_ALLOW_REAL_DB': '1'}) and ok({}, as_main=True)


def test_plain_import_without_database_url_is_refused_and_leaves_the_db_alone():
    real = ROOT / 'ciwt_lms.db'
    before = _sha(real)
    env = {k: v for k, v in os.environ.items() if k not in ('DATABASE_URL', 'CIWT_ALLOW_REAL_DB')}
    r = subprocess.run([sys.executable, '-c', 'import app'], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and 'Refusing to start against the real database' in r.stderr
    assert _sha(real) == before


def test_server_entry_points_set_the_flag():
    assert 'CIWT_ALLOW_REAL_DB=1' in (ROOT / 'Procfile').read_text()
    assert 'CIWT_ALLOW_REAL_DB' in (ROOT / 'render.yaml').read_text()
    assert 'CIWT_ALLOW_REAL_DB' in (ROOT / 'start_lms.sh').read_text()
