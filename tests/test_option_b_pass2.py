"""Option B pass 2: ITSUP ch3-10 sections that were same_as now carry bespoke R1-R4 ladders."""
import importlib
import re

from curriculum_v2 import ladder as L
from curriculum_v2.ladder.itsup import _p2
from curriculum_v2.ladder.sections import text_of


def _secs():
    for c in range(3, 11):
        yield from importlib.import_module(f'curriculum_v2.ladder.itsup._p2c{c:02d}').SECS.items()


def test_no_same_as_left_in_itsup_ch3_to_10():
    lad = L.ladder()
    left = [k for k, e in lad.items() if k[0] == 'ITSUP' and 3 <= int(k[1].split('.')[0]) <= 10 and e.get('type') == 'same_as']
    assert left == []
    assert len(dict(_secs())) == 63


def test_bespoke_rungs_meet_the_authoring_rules():
    assert _p2.VIOLATIONS == []
    for (label, sid), e in _secs():
        assert L.entry('ITSUP', label, sid)['type'] == 'section'
        r = e['rungs']
        assert [r[k]['kind'] for k in ('R1', 'R2', 'R3', 'R4')] == ['plain', 'analogy', 'visual', 'try']
        sents = [s for s in re.split(r'[.!?]+\s', text_of(r['R1']['html'])) if s.strip()]
        lens = [len(s.split()) for s in sents]
        assert max(lens) <= 35 and sum(lens) / len(lens) <= 22, (label, sid)
        assert 'Takeaway:' in r['R1']['html']
        assert 'Analogy map' in r['R2']['html'] and 'Where the analogy breaks' in r['R2']['html']
        assert '<svg' in r['R3']['html'] and 'aria-label=' in r['R3']['html']
        assert r['R4'].get('widget')
        for ch in e['checks'] + [c for g in r.values() for c in g['checks']]:
            assert ch['review'] == 'Pending SME review'
            assert set(ch['mc']) == set(ch['wrong'])          # every distractor carries a misconception tag
            mean = sum(map(len, ch['wrong'])) / len(ch['wrong'])
            assert len(ch['correct']) <= max(map(len, ch['wrong'])) and len(ch['correct']) < 1.4 * mean
