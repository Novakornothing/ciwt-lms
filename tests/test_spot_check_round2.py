"""Accuracy spot-check round 2 (Oct 18 2026): the sampler's guarantees and the six wording fixes it led to."""
import json
from pathlib import Path

import question_bank as QB
from curriculum_v2.netops_checks import netops_quiz_payload
from curriculum_v2.itsup_core import EXPANSION
from tools import spot_check_sample as S

ROOT = Path(__file__).resolve().parents[1]


def test_round2_sample_is_60_new_items_covering_every_chapter():
    r1 = {x['bank_id'] for x in S.sample(13)}
    r2 = S.sample_round2(14)
    ids = [x['bank_id'] for x in r2]
    assert len(r2) == 60 and len(set(ids)) == 60
    assert not r1 & set(ids)                                   # nothing from round 1
    assert all(x['obj'] and x['correct'] in x['options'] for x in r2)
    chapters = {S._chapter(q['obj']) for P in S.pools().values() for q in P if q.get('obj')}
    assert {S._chapter(x['obj']) for x in r2} == chapters      # every chapter of both courses
    assert len({x['obj'] for x in r2}) == 60                   # one item per objective


def test_frozen_round2_record_matches_the_items_checked():
    rec = json.loads((ROOT / 'docs/readiness/spot-check-round2-sample.json').read_text())
    assert len(rec['items']) == 60 and len({x['bank_id'] for x in rec['items']}) == 60


def _qb(bank_id):
    name, i = bank_id.split('.')
    return getattr(QB, name)[int(i)]


def test_round2_fixes_are_applied_and_keys_unchanged():
    a217 = _qb('A2.17')
    assert 'requires online MFA' not in a217['text'] and 'authenticator-app approval' in a217['text']
    assert a217['correct'] == 'The elevation policy needs an online MFA check'
    n120 = _qb('N1.20')
    assert 'shrinking windows' not in n120['text'] and 'bytes in flight' in n120['text']
    assert n120['correct'] == 'Congestion or loss on the path'
    ch1 = {q['bank_id']: q for q in netops_quiz_payload(1)}
    assert ch1['NQ1.1']['text'].startswith('As a packet crosses routers') and ch1['NQ1.1']['correct'] == 'Destination IP address'
    ch4 = {q['bank_id']: q for q in netops_quiz_payload(4)}
    assert 'alias' in ch4['NQ4.5']['text'] and ch4['NQ4.5']['correct'] == 'CNAME'
    ex = {q['bank_id']: q for q in EXPANSION}
    assert 'seek time' in ex['X-IT-3.1.1']['explanation'] and ex['X-IT-3.1.1']['correct'] == 'A 2.5-inch SATA solid-state drive'
    assert 'gateway' not in ex['X-IT-13.2.1']['explanation'] and ex['X-IT-13.2.1']['correct'] == 'In name resolution on that path'
