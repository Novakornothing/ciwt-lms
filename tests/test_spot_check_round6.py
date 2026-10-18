"""Accuracy spot-check round 6 (Oct 18 2026): the sampler's guarantees, the frozen record, and that no key, stem or
option was changed by the spot-check (0 clear errors found; three SME/editor notes and one outside-sample item are
documented)."""
import json
from pathlib import Path

from tools import spot_check_sample as S

ROOT = Path(__file__).resolve().parents[1]


def _rec(n):
    return json.loads((ROOT / f'docs/readiness/spot-check-round{n}-sample.json').read_text())


def test_round6_sample_is_60_new_items_one_per_objective_every_chapter():
    r6 = S.sample_round6(18)
    ids = [x['bank_id'] for x in r6]
    assert len(r6) == 60 and len(set(ids)) == 60
    earlier = set(S.ROUND1_IDS) | {x['bank_id'] for n in (2, 3, 4, 5) for x in _rec(n)['items']}
    assert len(earlier) == 280
    assert not earlier & set(ids)                                  # nothing from rounds 1-5
    assert 'X-IT-11.3.3' not in ids                              # edited this round, on the SME list instead
    assert all(x['obj'] and x['correct'] in x['options'] for x in r6)
    chapters = {S._chapter(q['obj']) for P in S.pools().values() for q in P if q.get('obj')}
    assert {S._chapter(x['obj']) for x in r6} == chapters        # every chapter of both courses
    assert len({x['obj'] for x in r6}) == 60                     # one item per objective
    assert not any(x['pool'] == 'cert' for x in r6)              # original items only


def test_frozen_round6_record_is_the_drawn_sample_and_nothing_changed():
    rec = _rec(6)
    drawn = S.sample_round6(18)
    assert [x['bank_id'] for x in rec['items']] == [x['bank_id'] for x in drawn]
    assert [(x['text'], x['options'], x['correct'], x['explanation']) for x in rec['items']] == \
           [(x['text'], x['options'], x['correct'], x['explanation']) for x in drawn]


def test_report_lists_every_sampled_item_with_a_source_and_verdict():
    doc = (ROOT / 'docs/readiness/SPOT_CHECK_ROUND6.md').read_text()
    rows = [line for line in doc.splitlines() if line.startswith('| ') and line.split('|')[1].strip().isdigit()]
    assert len(rows) == 60
    for x in _rec(6)['items']:
        row = next(r for r in rows if f"| {x['bank_id']} (" in r)
        assert len(row.split('|')[5].strip()) > 10, x['bank_id']    # primary source column filled
        assert row.split('|')[6].strip().startswith('Correct'), x['bank_id']
    assert '0 answer keys changed' in doc and 'not by an SME' in doc


def test_outside_sample_item_c_a1_3_5_3_is_recorded_and_left_as_is(app):
    from mastery.engine import cert_items_for
    from curriculum_v2 import misconceptions as MCS
    with app.app_context():
        q = next(x for x in cert_items_for('IT-2.1') if x.get('bank_id') == 'C-A1-3.5-3')
    assert q['correct'] == 'The app is built only for x86/x64 processors'
    assert not any(MCS.tag_for(dict(q, obj='IT-2.1'), d) for d in q['options'])
    assert 'C-A1-3.5-3' in (ROOT / 'docs/readiness/SPOT_CHECK_ROUND6.md').read_text()
