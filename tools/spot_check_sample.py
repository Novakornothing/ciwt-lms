#!/usr/bin/env python3
"""Draw the seeded, stratified 40-item sample of ORIGINAL course items (no certification items) for the pass-13
accuracy spot-check. No app import, no DB. Usage: python tools/spot_check_sample.py [seed] > sample.json

Round 2 (pass 14): ``python tools/spot_check_sample.py --round2 [seed]`` draws 60 further items, none of them in the
round-1 sample, spread by objective: every chapter of both courses gets at least one item, then objectives are
covered one item each (objectives round 1 did not touch first), all from the same original pools.

Round 3 (content round 3): ``python tools/spot_check_sample.py --round3 [seed]`` draws 60 more, none from rounds 1-2
(round 1 ids frozen in ROUND1_IDS, round 2 read from docs/readiness/spot-check-round2-sample.json), least-checked
objectives first.

Round 4 (content round 4): ``python tools/spot_check_sample.py --round4 [seed]`` draws 60 more, none from rounds 1-3
(round 3 read from docs/readiness/spot-check-round3-sample.json), same method.

Round 5 (content round 5): ``python tools/spot_check_sample.py --round5 [seed]`` draws 60 more, none from rounds 1-4
(round 4 read from docs/readiness/spot-check-round4-sample.json), same method."""
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


def _row(name, q):
    return {'pool': name, 'bank_id': q.get('bank_id'), 'obj': q.get('obj'), 'text': q['text'],
            'options': q.get('options'), 'correct': q.get('correct'), 'explanation': q.get('explanation') or q.get('study_tip')}


def _chapter(obj):
    return (obj.split('-')[0], int(obj.split('-')[1].split('.')[0]))


def sample_round2(seed=14, n=60):
    rng, P = random.Random(seed), pools()
    r1 = sample(13)
    done_ids = {x['bank_id'] for x in r1}
    done_objs = {x['obj'] for x in r1}
    by_obj = {}
    for name in sorted(P):
        for q in P[name]:
            if q.get('bank_id') in done_ids or not q.get('obj'):
                continue
            by_obj.setdefault(q['obj'], []).append((name, q))
    objs = sorted(by_obj)
    rng.shuffle(objs)
    # untouched objectives first, then the rest (stable within each group after the shuffle)
    objs.sort(key=lambda o: o in done_objs)
    picked, used_obj, chapters = [], set(), set()
    for o in objs:                                   # pass 1: one item for every chapter
        if _chapter(o) not in chapters:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o); chapters.add(_chapter(o))
    for o in objs:                                   # pass 2: one item per further objective
        if len(picked) >= n:
            break
        if o not in used_obj:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o)
    picked = picked[:n]
    picked.sort(key=lambda t: (_chapter(t[1]['obj']), t[1]['obj'], t[1]['bank_id']))
    return [_row(name, q) for name, q in picked]


# Round 1 as checked (CURRICULUM_READINESS.md table). sample(13) no longer reproduces it exactly, because pass 14
# appended chapter-check items to the pools, so the ids are frozen here.
ROUND1_IDS = ['A1.16', 'A1.18', 'A1.43', 'A1.47', 'A1.11', 'A1.41', 'A2.7', 'A2.4', 'A2.19', 'A2.5', 'A3.2', 'A3.1', 'A3.3',
              'N1.23', 'N1.9', 'N1.0', 'N1.13', 'N1.4', 'N2.19', 'N2.0', 'N2.8', 'N2.4', 'N3.1', 'N3.4', 'N3.7', 'Q12.1',
              'Q4.5', 'Q7.5', 'Q10.1', 'Q6.9', 'Q13.4', 'NQ9.0', 'NQ5.3', 'NQ5.4', 'NQ4.3', 'S-IT-11.2.2', 'S-IT-7.1.2',
              'S-NO-9.2.1', 'X-IT-12.2.1', 'X-IT-9.4.1']
ROUND2_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'readiness',
                           'spot-check-round2-sample.json')


def sample_round3(seed=15, n=60):
    """Round 3 (content round 3, Oct 18 2026): n further original items, none checked in round 1 (ROUND1_IDS) or
    round 2 (the frozen round-2 JSON). Objectives checked least so far go first (shuffled within each level), every
    chapter of both courses gets at least one item, then one item per further objective."""
    rng, P = random.Random(seed), pools()
    with open(ROUND2_JSON, encoding='utf-8') as f:
        r2 = json.load(f)['items']
    done_ids = set(ROUND1_IDS) | {x['bank_id'] for x in r2}
    every = {q.get('bank_id'): q.get('obj') for name in P for q in P[name]}
    checked = {}
    for b in done_ids:
        if every.get(b):
            checked[every[b]] = checked.get(every[b], 0) + 1
    for x in r2:                                     # round-2 ids carry their objective even if a pool moved
        checked.setdefault(x['obj'], 1)
    by_obj = {}
    for name in sorted(P):
        for q in P[name]:
            if q.get('bank_id') in done_ids or not q.get('obj'):
                continue
            by_obj.setdefault(q['obj'], []).append((name, q))
    objs = sorted(by_obj)
    rng.shuffle(objs)
    objs.sort(key=lambda o: checked.get(o, 0))
    picked, used_obj, chapters = [], set(), set()
    for o in objs:                                   # pass 1: one item for every chapter
        if _chapter(o) not in chapters:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o); chapters.add(_chapter(o))
    for o in objs:                                   # pass 2: one item per further objective
        if len(picked) >= n:
            break
        if o not in used_obj:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o)
    picked = picked[:n]
    picked.sort(key=lambda t: (_chapter(t[1]['obj']), t[1]['obj'], t[1]['bank_id']))
    return [_row(name, q) for name, q in picked]


ROUND3_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'readiness',
                           'spot-check-round3-sample.json')


def sample_round4(seed=16, n=60):
    """Round 4 (content round 4, Oct 18 2026): n further original items, none checked in rounds 1-3 (ROUND1_IDS and
    the frozen round-2 and round-3 JSON). Same method as round 3: objectives checked least so far go first (shuffled
    within each level), every chapter of both courses gets at least one item, then one item per further objective."""
    rng, P = random.Random(seed), pools()
    prev = []
    for path in (ROUND2_JSON, ROUND3_JSON):
        with open(path, encoding='utf-8') as f:
            prev += json.load(f)['items']
    done_ids = set(ROUND1_IDS) | {x['bank_id'] for x in prev}
    every = {q.get('bank_id'): q.get('obj') for name in P for q in P[name]}
    checked = {}
    for b in set(ROUND1_IDS):
        if every.get(b):
            checked[every[b]] = checked.get(every[b], 0) + 1
    for x in prev:                                   # rounds 2-3 carry their objective even if a pool moved
        checked[x['obj']] = checked.get(x['obj'], 0) + 1
    by_obj = {}
    for name in sorted(P):
        for q in P[name]:
            if q.get('bank_id') in done_ids or not q.get('obj'):
                continue
            by_obj.setdefault(q['obj'], []).append((name, q))
    objs = sorted(by_obj)
    rng.shuffle(objs)
    objs.sort(key=lambda o: checked.get(o, 0))
    picked, used_obj, chapters = [], set(), set()
    for o in objs:                                   # pass 1: one item for every chapter
        if _chapter(o) not in chapters:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o); chapters.add(_chapter(o))
    for o in objs:                                   # pass 2: one item per further objective
        if len(picked) >= n:
            break
        if o not in used_obj:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o)
    picked = picked[:n]
    picked.sort(key=lambda t: (_chapter(t[1]['obj']), t[1]['obj'], t[1]['bank_id']))
    return [_row(name, q) for name, q in picked]


ROUND4_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'readiness',
                           'spot-check-round4-sample.json')


def sample_round5(seed=17, n=60):
    """Round 5 (content round 5, Oct 18 2026): n further original items, none checked in rounds 1-4 (ROUND1_IDS and
    the frozen round-2, round-3 and round-4 JSON). Same method as rounds 3-4: objectives checked least so far go first
    (shuffled within each level), every chapter of both courses gets at least one item, then one item per further
    objective."""
    rng, P = random.Random(seed), pools()
    prev = []
    for path in (ROUND2_JSON, ROUND3_JSON, ROUND4_JSON):
        with open(path, encoding='utf-8') as f:
            prev += json.load(f)['items']
    done_ids = set(ROUND1_IDS) | {x['bank_id'] for x in prev}
    every = {q.get('bank_id'): q.get('obj') for name in P for q in P[name]}
    checked = {}
    for b in set(ROUND1_IDS):
        if every.get(b):
            checked[every[b]] = checked.get(every[b], 0) + 1
    for x in prev:
        checked[x['obj']] = checked.get(x['obj'], 0) + 1
    by_obj = {}
    for name in sorted(P):
        for q in P[name]:
            if q.get('bank_id') in done_ids or not q.get('obj'):
                continue
            by_obj.setdefault(q['obj'], []).append((name, q))
    objs = sorted(by_obj)
    rng.shuffle(objs)
    objs.sort(key=lambda o: checked.get(o, 0))
    picked, used_obj, chapters = [], set(), set()
    for o in objs:                                   # pass 1: one item for every chapter
        if _chapter(o) not in chapters:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o); chapters.add(_chapter(o))
    for o in objs:                                   # pass 2: one item per further objective
        if len(picked) >= n:
            break
        if o not in used_obj:
            picked.append(rng.choice(by_obj[o])); used_obj.add(o)
    picked = picked[:n]
    picked.sort(key=lambda t: (_chapter(t[1]['obj']), t[1]['obj'], t[1]['bank_id']))
    return [_row(name, q) for name, q in picked]


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--round5':
        print(json.dumps(sample_round5(int(args[1]) if len(args) > 1 else 17), indent=1, ensure_ascii=False))
    elif args and args[0] == '--round4':
        print(json.dumps(sample_round4(int(args[1]) if len(args) > 1 else 16), indent=1, ensure_ascii=False))
    elif args and args[0] == '--round3':
        print(json.dumps(sample_round3(int(args[1]) if len(args) > 1 else 15), indent=1, ensure_ascii=False))
    elif args and args[0] == '--round2':
        print(json.dumps(sample_round2(int(args[1]) if len(args) > 1 else 14), indent=1, ensure_ascii=False))
    else:
        print(json.dumps(sample(int(args[0]) if args else 13), indent=1, ensure_ascii=False))
