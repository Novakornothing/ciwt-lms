"""Option B pass 3: every section in the LMS has a bespoke ladder (no same_as, no templated NETOPS sections),
and no item pool or ladder check has a key noticeably longer than its distractors."""
import importlib
import os
import re
import sys

from curriculum_v2 import ladder as L
from curriculum_v2.ladder.itsup import _p2
from curriculum_v2.ladder.sections import text_of

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))


def _secs():
    yield from (('ITSUP',) + k for k in importlib.import_module('curriculum_v2.ladder.itsup._p3c02').SECS)
    for n in range(1, 7):
        yield from (('NETOPS',) + k for k in importlib.import_module(f'curriculum_v2.ladder.netops._p3n{n}').SECS)


def test_539_sections_all_bespoke():
    lad = L.ladder()
    secs = [k for k, v in lad.items() if v.get('type') == 'section']
    assert len(secs) == 539
    assert [k for k, v in lad.items() if v.get('type') == 'same_as'] == []
    assert not os.path.exists(os.path.join(ROOT, 'curriculum_v2', 'ladder', 'netops', '_gen.py'))


def test_pass3_targets_are_bespoke_and_follow_the_rules():
    keys = list(_secs())
    assert len(keys) == len(set(keys)) == 125
    assert _p2.VIOLATIONS == []
    for c, label, sid in keys:
        e = L.entry(c, label, sid)
        assert e['type'] == 'section' and e.get('note') == _p2.P3_NOTE, (c, label, sid)
        r = e['rungs']
        assert [r[k]['kind'] for k in ('R1', 'R2', 'R3', 'R4')] == ['plain', 'analogy', 'visual', 'try']
        lens = [len(s.split()) for s in re.split(r'[.!?]+\s', text_of(r['R1']['html'])) if s.strip()]
        assert max(lens) <= 35 and sum(lens) / len(lens) <= 22, (label, sid)
        assert 'Analogy map' in r['R2']['html'] and 'Where the analogy breaks' in r['R2']['html']
        assert '<svg' in r['R3']['html'] and 'aria-label=' in r['R3']['html']
        assert r['R4'].get('widget') and 'style=' not in r['R3']['html']
        checks = e.get('checks', []) + [ch for g in r.values() for ch in g['checks']]
        assert len(checks) >= 5
        for ch in checks:
            assert ch['review'] == 'Pending SME review'
            assert set(ch['mc']) == set(ch['wrong'])
            assert len(ch['correct']) < 1.15 * max(map(len, ch['wrong']))


def test_no_templated_netops_sections():
    import sme_priority_review as S
    lad = L.ladder()
    gen = [k for k, v in lad.items() if k[0] == 'NETOPS' and k[2] in S.GEN_SECTIONS and v.get('type') == 'section'
           and not str(v.get('note') or '').startswith('Option B pass 3')]
    assert gen == []


def test_no_long_keys_in_any_pool():
    from curriculum_readiness import original_pools
    bad = []
    for name, pool in original_pools().items():
        for q in pool:
            if (q.get('type') or 'single') != 'single' or q.get('correct') not in (q.get('options') or []):
                continue
            longest = max(len(o) for o in q['options'] if o != q['correct'])
            if len(q['correct']) >= 1.15 * longest:
                bad.append((name, q.get('bank_id')))
    assert bad == []
