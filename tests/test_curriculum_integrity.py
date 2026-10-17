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
    from curriculum_v2.exam_supplement import SUPPLEMENT
    from curriculum_v2.itsup_core import EXPANSION
    counts = collections.Counter(q['obj'] for q in all_items() + SUPPLEMENT + EXPANSION)
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


# ------------------------------------------------------------------------------------------- course package
import re  # noqa: E402

import lessons  # noqa: E402
from curriculum_v2 import course_package as CP  # noqa: E402
from curriculum_v2.exam_supplement import SUPPLEMENT  # noqa: E402

PACKS = {'ITSUP': lessons.APLUS, 'NETOPS': lessons.NETPLUS, 'CLIENT': lessons.CLIENT}


def test_supplement_items_are_keyed_and_mapped():
    ids = [q['bank_id'] for q in SUPPLEMENT]
    assert len(ids) == len(set(ids))
    for q in SUPPLEMENT:
        assert q['correct'] in q['options'] and len(set(q['options'])) == 4, q['bank_id']
        assert q['obj'] in OBJECTIVES and q['explanation'], q['bank_id']


@pytest.mark.parametrize('code', ['ITSUP', 'NETOPS', 'CLIENT'])
def test_every_chapter_has_a_complete_lesson_plan(code):
    for ch in PACKS[code]:
        plan = CP.lesson_plan(code, ch['order'])
        assert plan, (code, ch['order'])
        for field in ('warmup', 'guided', 'exit_ticket', 'discussion', 'misconceptions', 'support', 'extension', 'materials'):
            assert plan[field], (code, ch['order'], field)
        assert plan['objectives'], (code, ch['order'])
        assert plan['labs'] or plan['classroom_labs'], f'{code} ch{ch["order"]} has no lab'
        assert sum(t['minutes'] for t in plan['timing']) == 150


@pytest.mark.parametrize('code', ['ITSUP', 'NETOPS', 'CLIENT'])
def test_pacing_references_resolve(code):
    labs = {lab['id'] for lab in interactive_labs.LABS}
    for weeks in (16, 8, 10):
        rows = CP.pacing(code, weeks)
        assert [r['week'] for r in rows] == list(range(1, weeks + 1)), (code, weeks)
        for r in rows:
            for token in re.findall(r'\b(?:win|w11|gui|sw|rtr|hw|ticket)-[a-z0-9-]+', r['lab']):
                assert token in labs, (code, weeks, token)
            for cl in re.findall(r'CL-\d+', r['lab']):
                assert cl in CP.CLASSROOM_LABS, (code, weeks, cl)
        assert any('Final' in r['assessment'] for r in rows), (code, weeks)


def test_every_lab_has_standard_format():
    for lab in interactive_labs.LABS:
        f = CP.standard_lab(lab)
        for field in ('objective', 'steps', 'expected', 'equipment', 'low_cost', 'troubleshooting', 'reflection'):
            assert f[field], (lab['id'], field)
    for cl in CP.CLASSROOM_LABS.values():
        for field in ('objective', 'prerequisites', 'equipment', 'low_cost', 'steps', 'expected', 'troubleshooting', 'reflection', 'rubric'):
            assert cl[field], (cl['id'], field)
        assert cl['rubric'] in CP.RUBRICS
        assert set(cl['objectives']) <= set(OBJECTIVES)


@pytest.mark.parametrize('code', ['ITSUP', 'NETOPS', 'CLIENT'])
def test_blueprints_have_no_unassessed_objectives(code):
    for exam in ('midterm', 'final'):
        bp = CP.blueprint(code, exam)
        assert bp['gaps'] == [], (code, exam, bp['gaps'])
        assert 30 <= bp['n_items'] <= 50
        from curriculum_v2.itsup_core import EXPANSION
        known = {q.get('bank_id') for q in _test_items()} | {q['bank_id'] for q in SUPPLEMENT + EXPANSION}
        for row in bp['rows']:
            assert set(row['items']) <= known


def test_syllabus_has_institution_placeholders_and_gradebook_weights():
    s = CP.syllabus('ITSUP', section={'institution': 'Example College'})
    by = {f['key']: f for f in s['fields']}
    assert by['institution']['value'] == 'Example College'
    assert by['term']['value'] == '' and by['term']['placeholder'].startswith('[')
    keys = {p['key'] for p in s['policies']}
    assert {'attendance', 'late_work', 'academic_integrity', 'accessibility', 'ai_use'} <= keys
    assert [c['weight'] for c in s['grading']['categories']] == [70, 30, 0]
    custom = CP.syllabus('ITSUP', gb={'weight_tests': 50, 'weight_skills': 35, 'weight_quizzes': 15, 'pass_mark': 75})
    assert [c['weight'] for c in custom['grading']['categories']] == [50, 35, 15]
    assert custom['grading']['pass_mark'] == 75
    assert 'not affiliated' in s['disclaimer'].lower()


def test_answer_keys_cover_every_item_with_a_rationale():
    for code in ('ITSUP', 'NETOPS', 'CLIENT'):
        for key in CP.answer_keys(code):
            for row in key['rows']:
                assert row['key'] in 'ABCD' and row['rationale'], (code, key['title'], row['n'])
