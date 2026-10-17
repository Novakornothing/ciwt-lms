"""Content integrity for the curriculum and assessments (pass 8).

Every assessed objective has items, every item has a key among its options and an instructor
rationale, every item maps to a known objective, review entries still point at the item they were
written for, and labs referenced by lessons exist.
"""
import collections

import pytest

import interactive_labs
import pilot_slice
import question_bank
from curriculum_v2 import item_review
from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload
from curriculum_v2.objectives import CLOS, OBJECTIVES


def _test_items():
    seen = {}
    for _title, _desc, _order, items in question_bank.tests_aplus() + question_bank.tests_netplus():
        for q in items:
            seen.setdefault(q.get('bank_id') or q['text'], q)
    return list(seen.values())


def _quiz_items():
    out = [q for order in pilot_slice.PILOT_CHECKS for q in pilot_slice.quiz_payload(order, '')]
    out += [q for order in NETOPS_CHECKS for q in netops_quiz_payload(order)]
    return out


ALL = None


def all_items():
    global ALL
    if ALL is None:
        ALL = _test_items() + _quiz_items()
    return ALL


def test_review_entries_still_point_at_their_items():
    all_items()  # applying the review records any stem-guard failure
    assert item_review.MISMATCHES == []
    banks = {'A1': question_bank.A1, 'A2': question_bank.A2, 'A3': question_bank.A3,
             'N1': question_bank.N1, 'N2': question_bank.N2, 'N3': question_bank.N3}
    for key in item_review.REVIEW:
        name, idx = key.split('.')
        if name.startswith('Q'):
            assert int(idx) < len(pilot_slice.PILOT_CHECKS[int(name[1:])]), key
        else:
            assert int(idx) < len(banks[name]), key


def test_every_bank_item_is_reviewed():
    expected = {f'{n}.{i}' for n, pool in (('A1', question_bank.A1), ('A2', question_bank.A2), ('A3', question_bank.A3),
                                           ('N1', question_bank.N1), ('N2', question_bank.N2), ('N3', question_bank.N3))
                for i in range(len(pool))}
    expected |= {f'Q{o}.{i}' for o, items in pilot_slice.PILOT_CHECKS.items() for i in range(len(items))}
    assert expected - set(item_review.REVIEW) == set()


@pytest.mark.parametrize('kind', ['tests', 'quizzes'])
def test_every_item_has_key_rationale_and_objective(kind):
    items = _test_items() if kind == 'tests' else _quiz_items()
    assert items
    for q in items:
        tag = q.get('bank_id') or q['text'][:50]
        assert len(q['options']) == 4 and len(set(q['options'])) == 4, tag
        assert q['correct'] in q['options'], tag
        assert (q.get('explanation') or '').strip(), f'{tag}: no rationale'
        assert q.get('obj') in OBJECTIVES, f'{tag}: unknown objective {q.get("obj")}'


def test_every_objective_is_assessed():
    counts = collections.Counter(q['obj'] for q in all_items())
    thin = {k: counts[k] for k in OBJECTIVES if counts[k] < 2}
    assert thin == {}, f'objectives with fewer than 2 items: {thin}'


def test_course_outcomes_cover_all_objectives():
    for course in ('ITSUP', 'NETOPS'):
        prefixes = [p for _code, _text, refs in CLOS[course] for p in refs]
        own = {k for k, v in OBJECTIVES.items() if v['course'] == course}
        unmapped = {k for k in own if not any(k == p or k.startswith(p + '.') for p in prefixes)}
        assert unmapped == set(), course


def test_no_answer_length_giveaway():
    def ratio(q):
        return len(q['correct']) / max(len(o) for o in q['options'] if o != q['correct'])
    items = all_items()
    giveaway = [q.get('bank_id') for q in items if ratio(q) > 2.0]
    assert len(giveaway) <= len(items) * 0.02, giveaway


def test_key_positions_are_balanced():
    pos = collections.Counter(q['options'].index(q['correct']) for q in all_items())
    total = sum(pos.values())
    assert all(pos[i] / total > 0.15 for i in range(4)), pos


def test_no_vendor_exam_claims_in_items():
    for q in all_items():
        blob = ' '.join([q['text']] + q['options']).lower()
        assert 'comptia' not in blob, q.get('bank_id')


def test_netops_checks_are_chapter_specific():
    stems = [q['q'] for items in NETOPS_CHECKS.values() for q in items]
    assert len(stems) == len(set(stems))
    for order, items in NETOPS_CHECKS.items():
        for q in items:
            assert OBJECTIVES[q['obj']]['chapter'] == order, (order, q['q'][:40])


def test_lab_references_resolve():
    labs = {lab['id'] for lab in interactive_labs.LABS}
    for ch, ids in interactive_labs.CHAPTER_LABS.items():
        assert set(ids) <= labs, ch
    for key, ids in interactive_labs.LESSON_LABS.items():
        assert set(ids if isinstance(ids, (list, tuple)) else [ids]) <= labs, key


def test_known_factual_fixes_stay_fixed():
    by = {q.get('bank_id'): q for q in all_items()}
    # N1.2: 192.168.10.255 is a valid host in 192.168.10.0/23 and must not be a distractor
    assert '192.168.10.255' not in by['N1.2']['options']
    # N1.4: inbound ACLs are evaluated before the routing decision
    assert 'before the routing decision' in by['N1.4']['correct']
    # A1.13: stem no longer gives away the mask
    assert '/27' not in by['A1.13']['text']
