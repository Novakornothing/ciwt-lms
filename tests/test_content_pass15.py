"""Pass 15: full rationales for the last one-line chapter-check rationales, and option-length parity."""
import re

import pilot_slice as PS
from curriculum_v2 import misconceptions as MCS
from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload
from curriculum_v2.parity_pass15 import REWRITE
from curriculum_v2.rationales_pass15 import RATIONALE


def _itsup():
    return [q for ch in sorted(PS.PILOT_CHECKS) for q in PS.quiz_payload(ch, '')]


def _all():
    return _itsup() + [q for ch in sorted(NETOPS_CHECKS) for q in netops_quiz_payload(ch)]


def _words(e):
    return len(re.sub(r'^\[Pending SME review\]\s*', '', (e or '').strip()).split())


def test_every_chapter_check_rationale_explains_the_answer():
    thin = [q['bank_id'] for q in _all() if _words(q['explanation']) < 10]
    assert thin == []


def test_pass15_rationales_are_served_keep_the_pointer_and_explain_both_sides():
    by = {q['bank_id']: q for q in _itsup()}
    assert len(RATIONALE) == 39
    for k, why in RATIONALE.items():
        assert by[k]['explanation'] == why, k                       # applied (no other review rationale existed)
        assert re.search(r'See \d+\.\d+( / \d+\.\d+)*\.$', why), k   # section pointer kept at the end
        assert len(why.split()) >= 30, k


def test_parity_rewrites_apply_and_keep_the_key():
    by = {q['bank_id']: q for q in _all()}
    for b, rw in REWRITE.items():
        q = by[b]
        for old, new in rw.items():
            assert new in q['options'] and old not in q['options'], (b, old)
            assert new != q['correct'], b                            # only distractors were rewritten
        assert len(set(q['options'])) == 4 and q['correct'] in q['options']


def test_key_is_rarely_the_uniquely_longest_option():
    items = _all()
    uniq = [q['bank_id'] for q in items if len(q['correct']) > max(len(o) for o in q['options'] if o != q['correct'])]
    clear = [q['bank_id'] for q in items if len(q['correct']) >= 1.15 * max(len(o) for o in q['options'] if o != q['correct'])]
    assert len(uniq) / len(items) <= 0.30, (len(uniq), len(items))
    assert len(clear) <= 4, clear                                    # only one-word protocol/record names remain
    for b in ('Q12.11', 'Q13.11'):                                   # the two pass-14 items flagged in pass 14
        assert b not in uniq


def test_misconception_tags_follow_rewritten_distractors():
    by = {q['bank_id']: q for q in _all()}
    moved = 0
    for b, rw in REWRITE.items():
        for old, new in rw.items():
            assert (b, old) not in MCS.TAGS
            if (b, new) in MCS.TAGS:
                moved += 1
                assert MCS.tag_for(by[b], new) == MCS.TAGS[(b, new)]
    assert moved >= 60
