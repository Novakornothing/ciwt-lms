"""Accuracy spot-check round 5 (Oct 18 2026): the sampler's guarantees, the frozen record, and that no key, stem or
option was changed (0 clear errors found; two SME notes and one outside-sample dispute are documented)."""
import json
from pathlib import Path

from tools import spot_check_sample as S

ROOT = Path(__file__).resolve().parents[1]


def _rec(n):
    return json.loads((ROOT / f'docs/readiness/spot-check-round{n}-sample.json').read_text())


def test_round5_sample_is_60_new_items_one_per_objective_every_chapter():
    r5 = S.sample_round5(17)
    ids = [x['bank_id'] for x in r5]
    assert len(r5) == 60 and len(set(ids)) == 60
    earlier = set(S.ROUND1_IDS) | {x['bank_id'] for n in (2, 3, 4) for x in _rec(n)['items']}
    assert len(earlier) == 220
    assert not earlier & set(ids)                                  # nothing from rounds 1-4
    assert all(x['obj'] and x['correct'] in x['options'] for x in r5)
    chapters = {S._chapter(q['obj']) for P in S.pools().values() for q in P if q.get('obj')}
    assert {S._chapter(x['obj']) for x in r5} == chapters        # every chapter of both courses
    assert len({x['obj'] for x in r5}) == 60                     # one item per objective
    assert not any(x['pool'] == 'cert' for x in r5)              # original items only


def test_frozen_round5_record_is_the_drawn_sample_and_nothing_changed():
    rec = _rec(5)
    drawn = S.sample_round5(17)
    assert [x['bank_id'] for x in rec['items']] == [x['bank_id'] for x in drawn]
    assert [(x['text'], x['options'], x['correct'], x['explanation']) for x in rec['items']] == \
           [(x['text'], x['options'], x['correct'], x['explanation']) for x in drawn]


def test_report_lists_every_sampled_item_with_a_source_and_verdict():
    doc = (ROOT / 'docs/readiness/SPOT_CHECK_ROUND5.md').read_text()
    rows = [line for line in doc.splitlines() if line.startswith('| ') and line.split('|')[1].strip().isdigit()]
    assert len(rows) == 60
    for x in _rec(5)['items']:
        row = next(r for r in rows if f"| {x['bank_id']} (" in r)
        assert len(row.split('|')[5].strip()) > 10, x['bank_id']    # primary source column filled
        assert row.split('|')[6].strip().startswith('Correct'), x['bank_id']
    assert '0 answer keys changed' in doc and 'not by an SME' in doc


def test_outside_sample_dispute_is_recorded_and_the_item_left_as_is():
    from curriculum_v2.itsup_core import EXPANSION
    from curriculum_v2 import misconceptions_round5 as R5
    q = next(x for x in EXPANSION if x['bank_id'] == 'X-IT-11.3.3')
    assert q['correct'] == 'When there is no tested backup of the user’s data'
    assert 'When the fault has a known, documented vendor fix' in q['options']
    assert 'X-IT-11.3.3' in R5.UNTAGGED
    assert 'X-IT-11.3.3' in (ROOT / 'docs/readiness/SPOT_CHECK_ROUND5.md').read_text()
