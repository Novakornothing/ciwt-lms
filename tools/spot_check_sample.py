#!/usr/bin/env python3
"""Draw the seeded, stratified 40-item sample of ORIGINAL course items (no certification items) for the pass-13
accuracy spot-check. No app import, no DB. Usage: python tools/spot_check_sample.py [seed] > sample.json"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pilot_slice as PS  # noqa: E402
import question_bank as QB  # noqa: E402
from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload  # noqa: E402
from curriculum_v2.exam_supplement import SUPPLEMENT  # noqa: E402
from curriculum_v2.itsup_core import EXPANSION  # noqa: E402

PLAN = [('question_bank.A1', 6), ('question_bank.A2', 4), ('question_bank.A3', 3), ('question_bank.N1', 5),
        ('question_bank.N2', 4), ('question_bank.N3', 3), ('ITSUP chapter checks', 6), ('NETOPS chapter checks', 4),
        ('exam_supplement', 3), ('itsup_core.EXPANSION', 2)]


def pools():
    p = {f'question_bank.{n}': getattr(QB, n) for n in ('A1', 'A2', 'A3', 'N1', 'N2', 'N3')}
    p['ITSUP chapter checks'] = [q for o in sorted(PS.PILOT_CHECKS) for q in PS.quiz_payload(o, '')]
    p['NETOPS chapter checks'] = [q for o in sorted(NETOPS_CHECKS) for q in netops_quiz_payload(o)]
    p['exam_supplement'] = SUPPLEMENT
    p['itsup_core.EXPANSION'] = EXPANSION
    return p


def sample(seed=13):
    rng, P, out = random.Random(seed), pools(), []
    for name, n in PLAN:
        for q in rng.sample(P[name], n):
            out.append({'pool': name, 'bank_id': q.get('bank_id'), 'obj': q.get('obj'), 'text': q['text'],
                        'options': q.get('options'), 'correct': q.get('correct'), 'explanation': q.get('explanation') or q.get('study_tip')})
    return out


if __name__ == '__main__':
    print(json.dumps(sample(int(sys.argv[1]) if len(sys.argv) > 1 else 13), indent=1, ensure_ascii=False))
