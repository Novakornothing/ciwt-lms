"""Pass 14: the phone quiz/test e2e is self-contained — it copies the DB, runs its own server and cleans up — so it
passes alone (pytest -k assess) or after any other suite. Skipped when Playwright's Chromium isn't installed."""
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _chromium():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            return os.path.exists(p.chromium.executable_path)
    except Exception:
        return False


@pytest.mark.skipif(not _chromium(), reason='Playwright Chromium not installed')
def test_assess_phone_e2e_runs_on_its_own_copy(tmp_path):
    src = tmp_path / 'src.db'
    # copy the baseline first (read-only); the tool then makes its own working copy of this one.
    # ciwt_lms.db is git-ignored, so a fresh clone or a second worktree has none: seed a brand-new DB instead.
    import shutil
    base = os.path.join(ROOT, 'ciwt_lms.db')
    if os.path.exists(base):
        shutil.copyfile(base, src)
    else:
        env = dict(os.environ, DATABASE_URL='sqlite:///' + str(src))
        seeded = subprocess.run([sys.executable, '-c', 'import app'], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        assert seeded.returncode == 0 and src.exists(), seeded.stdout[-2000:] + seeded.stderr[-2000:]
    env = {k: v for k, v in os.environ.items() if k not in ('DATABASE_URL', 'PORT', 'CIWT_ALLOW_REAL_DB')}
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'assess_phone_e2e.py'), str(tmp_path / 'out'),
                        '--src-db', str(src)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=240)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert 'checks passed' in r.stdout and 'FAIL' not in r.stdout
