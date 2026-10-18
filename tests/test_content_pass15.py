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


def test_every_course_objective_now_has_certification_items():
    from collections import Counter
    from curriculum_v2.cert.items import CERT_ITEMS
    from curriculum_v2.objectives import OBJECTIVES
    n = Counter(q['obj'] for q in CERT_ITEMS)
    missing = [o for o, v in OBJECTIVES.items() if v['course'] in ('ITSUP', 'NETOPS') and n.get(o, 0) < 2]
    assert missing == []


def test_gap_items_are_pending_review_sourced_aligned_and_tagged():
    from curriculum_v2.cert import misconceptions as CM
    from curriculum_v2.cert.content import i05_gaps_p15 as G
    from curriculum_v2.cert.exams import OBJECTIVES as EXAM_OBJ
    from curriculum_v2.cert.items import BY_ID
    from curriculum_v2.cert.mapping import CURATED
    assert len(G.ITEMS) == 59 and set(G.SOURCE) == {q['bank_id'] for q in G.ITEMS}
    objs = {q['obj'] for q in G.ITEMS}
    assert len(objs) == 26
    for raw in G.ITEMS:
        q = BY_ID[raw['bank_id']]
        assert 'Pending SME review' in q['review']
        assert all(c in EXAM_OBJ and c in CURATED[q['obj']] for c in q['cert']), q['bank_id']
        assert G.SOURCE[q['bank_id']].strip()
        for d, mc in (q.get('mc') or {}).items():
            assert d in q['options'] and d != q['correct'] and CM.MISCONCEPTIONS[mc]['obj'] == q['obj']
    tagged = {q['obj'] for q in G.ITEMS if q.get('mc')}
    assert tagged == objs                                             # every gap objective gets misconception tags
    singles = [BY_ID[q['bank_id']] for q in G.ITEMS if q['type'] == 'single']
    uniq = [q for q in singles if len(q['correct']) > max(len(o) for o in q['options'] if o != q['correct'])]
    assert len(uniq) / len(singles) <= 0.30
