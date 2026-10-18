"""SYNTHETIC simulation of the explanation-ladder policy (pass 19). Not student evidence.

Synthetic learners walk 40 synthetic sections (8 lessons x 5) through mastery/ladder_policy.py exactly as the
routes do (answer -> escalate / resolve, profile from resolutions, profile leads the order). Each learner has a
hidden "what helps" kind (plain / analogy / visual / try) or none. Chance of a right answer: original 0.55, the
learner's helpful kind 0.85, any other rung 0.45 (made-up numbers chosen only to exercise the policy).
It reports, per group: how often the profile settles on the right kind, how often it settles on a wrong one
(false lead), rungs per section before vs after the profile settles, and the exhaustion rate.
usage: python tools/ladder_sim.py [--learners 400] [--seed 19] [--json]
"""
import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mastery import ladder_policy as P  # noqa: E402

P_R0, P_HELP, P_OTHER = 0.55, 0.85, 0.45
KINDS = ['plain', 'analogy', 'visual', 'try', None]


def learner_run(rng, helps, n_lessons=8, per_lesson=5, max_rung=4):
    allowed = P.allowed_rungs(max_rung)
    res, log = [], []
    first_best_at = None
    for li in range(n_lessons):
        for si in range(per_lesson):
            prof = P.profile(res)
            best = prof['best']
            if best and first_best_at is None:
                first_best_at = li * per_lesson + si
            st = P.start(allowed, best, False)
            seq = P.order(allowed, best)
            sec = {'lesson': f'L{li}', 'shown': set(), 'resolved': None}
            while True:
                rung = st['current']
                kind = P.KIND[rung]
                p = P_R0 if rung == 'R0' else (P_HELP if kind == helps else P_OTHER)
                ok = rng.random() < p
                sec['shown'].add(rung)
                st, nxt, ev = P.after_answer(st, ok, seq)
                if ev == 'resolved':
                    sec['resolved'] = st['resolved']
                    break
                if ev in ('exhausted', 'no_more'):
                    break
            res.append(sec)
            log.append({'alt_rungs': len(st['tried']) - 1, 'exhausted': st['exhausted'], 'had_best': bool(best),
                        'best': best})
    return {'helps': helps, 'first_best_at': first_best_at, 'final_best': P.profile(res)['best'], 'log': log}


def simulate(learners=400, seed=19):
    rng = random.Random(seed)
    runs = [learner_run(rng, KINDS[i % len(KINDS)]) for i in range(learners)]
    out = {'label': 'SYNTHETIC simulation, not student evidence', 'learners': learners, 'seed': seed,
           'p': {'original': P_R0, 'helpful kind': P_HELP, 'other rung': P_OTHER}, 'groups': {}}
    for k in KINDS:
        rs = [r for r in runs if r['helps'] == k]
        settled = [r for r in rs if r['final_best']]
        right = [r for r in settled if r['final_best'] == k]
        wrong = [r for r in settled if r['final_best'] != k]
        before = [x['alt_rungs'] for r in rs for x in r['log'] if not x['had_best'] and x['alt_rungs']]
        after = [x['alt_rungs'] for r in rs for x in r['log'] if x['had_best'] and x['alt_rungs']]
        sections = [x for r in rs for x in r['log']]
        out['groups'][str(k)] = {
            'learners': len(rs),
            'profile_right': round(len(right) / len(rs), 3),
            'profile_wrong_lead': round(len(wrong) / len(rs), 3),
            'median_section_when_settled': sorted(r['first_best_at'] for r in rs if r['first_best_at'] is not None)[
                len([r for r in rs if r['first_best_at'] is not None]) // 2] if any(r['first_best_at'] is not None for r in rs) else None,
            'alt_rungs_before_profile': round(sum(before) / len(before), 2) if before else None,
            'alt_rungs_after_profile': round(sum(after) / len(after), 2) if after else None,
            'exhausted_rate': round(sum(1 for x in sections if x['exhausted']) / len(sections), 3),
        }
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--learners', type=int, default=400); ap.add_argument('--seed', type=int, default=19)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    r = simulate(a.learners, a.seed)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        print(r['label'], f"({r['learners']} learners, seed {r['seed']}; p = {r['p']})")
        for k, g in r['groups'].items():
            print(f"  helps={k:8s} profile right {g['profile_right']:.0%}  wrong lead {g['profile_wrong_lead']:.0%}  "
                  f"settles at section {g['median_section_when_settled']}  alt rungs before/after "
                  f"{g['alt_rungs_before_profile']}/{g['alt_rungs_after_profile']}  exhausted {g['exhausted_rate']:.1%}")
