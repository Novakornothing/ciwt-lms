"""Accuracy spot-check round 3 (Oct 18 2026): the sampler's guarantees, the frozen record and the one stem fix."""
import json
from pathlib import Path

from curriculum_v2.itsup_core import EXPANSION
from tools import spot_check_sample as S

ROOT = Path(__file__).resolve().parents[1]


def _rec():
    return json.loads((ROOT / 'docs/readiness/spot-check-round3-sample.json').read_text())


def test_round3_sample_is_60_new_items_one_per_objective_every_chapter():
    r3 = S.sample_round3(15)
    ids = [x['bank_id'] for x in r3]
    assert len(r3) == 60 and len(set(ids)) == 60
    r2 = {x['bank_id'] for x in json.loads((ROOT / 'docs/readiness/spot-check-round2-sample.json').read_text())['items']}
    assert not (set(S.ROUND1_IDS) | r2) & set(ids)                 # nothing from rounds 1 or 2
    assert all(x['obj'] and x['correct'] in x['options'] for x in r3)
    chapters = {S._chapter(q['obj']) for P in S.pools().values() for q in P if q.get('obj')}
    assert {S._chapter(x['obj']) for x in r3} == chapters        # every chapter of both courses
    assert len({x['obj'] for x in r3}) == 60                     # one item per objective


def test_frozen_round3_record_is_the_drawn_sample():
    rec = _rec()
    assert [x['bank_id'] for x in rec['items']] == [x['bank_id'] for x in S.sample_round3(15)]
    assert len(S.ROUND1_IDS) == 40 and len(set(S.ROUND1_IDS)) == 40


def test_round3_stem_fix_applied_and_key_unchanged():
    q = next(x for x in EXPANSION if x['bank_id'] == 'X-IT-9.2.3')
    assert 'college-owned Mac they use' in q['text'] and 'from their Mac' not in q['text']
    assert q['correct'] == 'Decline and send the request to the device owner'
    assert 'the owner is the college' in q['explanation']
    assert 'Pending SME review' in q.get('review', '')
