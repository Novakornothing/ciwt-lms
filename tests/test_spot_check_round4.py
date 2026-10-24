"""Accuracy spot-check round 4 (Oct 18 2026): the sampler's guarantees, the frozen record, no key changed, and the
lesson and citation corrections the round made."""
import json
from pathlib import Path

from tools import spot_check_sample as S

ROOT = Path(__file__).resolve().parents[1]


def _rec(n):
    return json.loads((ROOT / f'docs/readiness/spot-check-round{n}-sample.json').read_text())


def test_round4_sample_is_60_new_items_one_per_objective_every_chapter():
    r4 = S.sample_round4(16)
    ids = [x['bank_id'] for x in r4]
    assert len(r4) == 60 and len(set(ids)) == 60
    earlier = set(S.ROUND1_IDS) | {x['bank_id'] for n in (2, 3) for x in _rec(n)['items']}
    assert not earlier & set(ids)                                  # nothing from rounds 1-3
    assert all(x['obj'] and x['correct'] in x['options'] for x in r4)
    chapters = {S._chapter(q['obj']) for P in S.pools().values() for q in P if q.get('obj')}
    assert {S._chapter(x['obj']) for x in r4} == chapters        # every chapter of both courses
    assert len({x['obj'] for x in r4}) == 60                     # one item per objective
    assert not any(x['pool'] in ('cert',) for x in r4)           # original items only


def test_frozen_round4_record_is_the_drawn_sample_and_keys_are_unchanged():
    rec = _rec(4)
    drawn = S.sample_round4(16)
    assert [x['bank_id'] for x in rec['items']] == [x['bank_id'] for x in drawn]
    # no answer key, stem or option was changed by round 4 (Q9.11 is disputed but left as is)
    # Q9.11 was rewritten in content round 7 (Oct 24) to resolve that dispute, so it is excluded here
    assert [(x['text'], x['options'], x['correct']) for x in rec['items'] if x['bank_id'] != 'Q9.11'] == \
           [(x['text'], x['options'], x['correct']) for x in drawn if x['bank_id'] != 'Q9.11']
    q911 = next(x for x in drawn if x['bank_id'] == 'Q9.11')
    assert q911['correct'].startswith('ext4 names are case-sensitive')


def test_report_lists_every_sampled_item_with_a_source():
    doc = (ROOT / 'docs/readiness/SPOT_CHECK_ROUND4.md').read_text()
    rows = [line for line in doc.splitlines() if line.startswith('| ') and line.split('|')[1].strip().isdigit()]
    assert len(rows) == 60
    for x in _rec(4)['items']:
        row = next(r for r in rows if f"| {x['bank_id']} (" in r)
        assert len(row.split('|')[5].strip()) > 10, x['bank_id']    # primary source column filled
    assert 'Key disputed' in doc and 'Q9.11' in doc


def test_am5_lesson_fact_corrected():
    src = (ROOT / 'block2_hardware.py').read_text()
    assert 'AM4/AM5: pins on the' not in src
    assert 'AM5 is an LGA socket too' in src and 'AM5 is LGA, like Intel' in src


def test_aplus_methodology_is_not_cited_as_a_220_1201_objective():
    for p in ('curriculum_v2/misconceptions_round3.py', 'curriculum_v2/rationales_round4.py'):
        t = (ROOT / p).read_text()
        assert '(220-1201) objective 5.1, troubleshooting methodology' not in t, p
        assert '220-1201) objective 5.1 (verify' not in t, p
