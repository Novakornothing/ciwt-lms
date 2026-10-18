"""Pass 13: smoke run of the synthetic semester simulation (tools/semester_sim.py) on its own fresh database.
Synthetic cohort, fixed answer probabilities: this checks engine behaviour, not learning gains."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_semester_simulation_smoke(tmp_path):
    out = tmp_path / 'sim.json'
    env = dict(os.environ, DATABASE_URL='sqlite:///' + str(tmp_path / 'sim.db'))
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'semester_sim.py'), str(out), '--days', '22'],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert out.exists(), p.stdout[-3000:] + p.stderr[-3000:]
    R = json.loads(out.read_text())
    assert R['synthetic'] is True and 'not learning gains' in R['note']
    failed = [c for c in R['checks'] if not c['ok']]
    assert not failed, failed
    assert R['events']['reviews'] > 0 and R['events']['daily_reviews'] > 0 and R['events']['testouts'] > 0
    assert R['daily_why'].get('due', 0) > 0


def test_sim_refuses_the_real_database():
    env = dict(os.environ, DATABASE_URL='sqlite:///' + os.path.join(ROOT, 'ciwt_lms.db'))
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'semester_sim.py'), '/dev/null'],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    assert p.returncode != 0 and 'COPY' in (p.stderr + p.stdout)


def test_reading_alone_does_not_block_a_mastery_check_offer():
    """Bug found by the simulation: objectives that were only read counted as 'worked but not mastered'."""
    sys.path.insert(0, ROOT)
    from mastery import policy as P
    mastered = [{'state': 'mastered', 'answered': True} for _ in range(4)]
    read_only = [{'state': 'developing', 'answered': False} for _ in range(6)]
    assert P.strong_so_far(mastered + read_only)[0] is True
    answered_dev = [{'state': 'developing', 'answered': True} for _ in range(6)]
    assert P.strong_so_far(mastered + answered_dev)[0] is False
