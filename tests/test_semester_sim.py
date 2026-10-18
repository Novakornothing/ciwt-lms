"""Pass 13: smoke run of the synthetic semester simulation (tools/semester_sim.py) on its own fresh database.
Synthetic cohort, fixed answer probabilities: this checks engine behaviour, not learning gains."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_semester_simulation_smoke(tmp_path):
    # Pass 14: run the documented 28-day window (default). At 22 days a strong student has a single
    # mastery-check offer (day 21); with the fixed answer probability and the larger pass-14 check pools
    # one of them can fail that single attempt, which tells us nothing about the engine.
    out = tmp_path / 'sim.json'
    env = dict(os.environ, DATABASE_URL='sqlite:///' + str(tmp_path / 'sim.db'))
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'semester_sim.py'), str(out), '--days', '28'],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert out.exists(), p.stdout[-3000:] + p.stderr[-3000:]
    R = json.loads(out.read_text())
    assert R['synthetic'] is True and 'not learning gains' in R['note']
    failed = [c for c in R['checks'] if not c['ok']]
    assert not failed, failed
    assert R['events']['reviews'] > 0 and R['events']['daily_reviews'] > 0 and R['events']['testouts'] > 0
    assert R['daily_why'].get('due', 0) > 0
    assert R['bank'] is False and R['bank_items_served']['times'] == 0   # content round 5: the default leaves the bank off


def test_semester_simulation_with_the_bank_on(tmp_path):
    """Content round 5: with "Also use the chapter item bank" on, review/mastery checks draw X-IT bank and S-
    supplement items, and every tagged wrong answer on them is recorded as that mix-up. 14 days is enough for the
    bank checks; the other checks are written for the documented 28-day window and are covered above."""
    out = tmp_path / 'sim.json'
    env = dict(os.environ, DATABASE_URL='sqlite:///' + str(tmp_path / 'sim.db'))
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'semester_sim.py'), str(out), '--days', '14', '--bank'],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert out.exists(), p.stdout[-3000:] + p.stderr[-3000:]
    R = json.loads(out.read_text())
    assert R['bank'] is True
    bank_checks = [c for c in R['checks'] if 'bank' in c['check']]
    assert len(bank_checks) == 3 and all(c['ok'] for c in bank_checks), bank_checks
    assert R['bank_items_served']['times'] > 0 and R['bank_items_served']['tagged_wrong_answers'] > 0


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


def test_strong_rank_check_uses_the_ranked_list_round6():
    """Content round 6: replay of the failing full-suite order (strong 32 listed for a repeated mix-up below every weak,
    mixed and disengaged student in the ranked list, but above inactive-only disengaged 47, whom the page lists
    separately). The check passes; a strong student above a mixed one, or listed for another reason, still fails."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('semester_sim_mod', os.path.join(ROOT, 'tools', 'semester_sim.py'))
    src = open(spec.origin).read()
    ns = {}
    exec(compile(src[src.index('def strong_rank_ok'):src.index('\n\n\n', src.index('def strong_rank_ok'))], spec.origin, 'exec'), ns)
    ok = ns['strong_rank_ok']
    prof = {45: 'weak', 48: 'disengaged', 40: 'mixed', 38: 'mixed', 35: 'good', 32: 'strong', 47: 'disengaged'}
    order = [(45, ['stuck', 'misconception']), (48, ['stuck', 'misconception', 'inactive']), (40, ['stuck', 'misconception']),
             (38, ['stuck', 'misconception']), (35, ['misconception']), (32, ['misconception']), (47, ['inactive'])]
    assert ok(order, prof, {32})
    above_mixed = order[:3] + [(32, ['misconception'])] + [x for x in order[3:] if x[0] != 32]
    assert not ok(above_mixed, prof, {32})
    assert not ok([x if x[0] != 32 else (32, ['misconception', 'missed_review']) for x in order], prof, {32})
