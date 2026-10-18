"""Pass 14: chapter-check items for IT-7.4 … IT-13.4 — appended without moving existing items, mapped to their
objective, tagged Pending SME review, with misconception tags that are real distractors and lesson-backed fixes."""
import pilot_slice as PS
from curriculum_v2 import checks_pass14 as P14
from curriculum_v2 import misconceptions as MCS
from curriculum_v2.item_review import MISMATCHES

TARGET = {f'IT-{c}.4' for c in range(7, 14)}


def _new():
    return [q for ch in range(7, 14) for q in PS.quiz_payload(ch, '') if q['bank_id'] in P14.REVIEW]


def test_every_x4_objective_now_has_two_chapter_check_items():
    qs = _new()
    assert len(qs) == 14 and not MISMATCHES
    by = {}
    for q in qs:
        by.setdefault(q['obj'], []).append(q['bank_id'])
    assert set(by) == TARGET and all(len(v) == 2 for v in by.values())
    all_checks = [q for o in sorted(PS.PILOT_CHECKS) for q in PS.quiz_payload(o, '')]
    assert TARGET <= {q['obj'] for q in all_checks}


def test_existing_items_keep_their_positions():
    for ch in range(7, 14):
        qs = PS.quiz_payload(ch, '')
        assert [q['bank_id'] for q in qs[:10]] == [f'Q{ch}.{i}' for i in range(10)]
        assert [q['bank_id'] for q in qs[10:]] == [f'Q{ch}.10', f'Q{ch}.11']


def test_items_are_well_formed_pending_sme_and_have_real_rationales():
    for q in _new():
        assert len(q['options']) == 4 and len(set(q['options'])) == 4 and q['correct'] in q['options']
        assert q['review'] == P14.PENDING and 'Pending SME review' in q['review']
        assert len(q['explanation']) > 120, q['bank_id']           # an explanation, not a section pointer
        assert P14.SOURCE[q['bank_id']]
    longest = sum(len(q['correct']) > max(len(o) for o in q['options'] if o != q['correct']) for q in _new())
    assert longest <= 5, longest                                     # no length giveaway


def test_stems_are_new():
    from curriculum_v2.itsup_core import ch07, ch08, ch09, ch10, ch11, ch12, ch13
    bank = {' '.join(i['text'].lower().split()) for m in (ch07, ch08, ch09, ch10, ch11, ch12, ch13) for i in m.ITEMS}
    old = {' '.join(q['text'].lower().split()) for ch in range(1, 14) for q in PS.quiz_payload(ch, '')[:10]}
    for q in _new():
        s = ' '.join(q['text'].lower().split())
        assert s not in bank and s not in old, q['bank_id']


def test_misconception_tags_are_real_distractors_on_the_right_objective():
    by = {q['bank_id']: q for q in _new()}
    from curriculum_v2.parity_pass15 import REWRITE  # pass 15: some distractors were rewritten for length parity
    for (b, d), mc in P14.TAGS.items():
        q = by[b]
        d = REWRITE.get(b, {}).get(d, d)
        assert d in q['options'] and d != q['correct'], (b, d)
        assert MCS.MISCONCEPTIONS[mc]['obj'] == q['obj']
        assert MCS.tag_for(q, d) == mc and MCS.tag_for(q, q['correct']) is None
    assert set(P14.TAGS.values()) == set(P14.MISCONCEPTIONS)
    assert {b for b, _d in P14.TAGS} == set(by)                      # every new item carries tags


def test_new_misconceptions_find_a_lesson_section_and_the_quiz_syncs(app, mod):
    from mastery import content as C
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        sec = mod.db.session.get(mod.ClassSection, 1)
        cmap = eng.course_map(sec)
        for mc_id, mc in P14.MISCONCEPTIONS.items():
            o = cmap['objs'][mc['obj']]
            info = cmap['obj_lesson'].get(mc['obj'])
            les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
            out = C.build_correction(mc['obj'], o['text'], mc, les, chapter_lessons=cmap['by_ch'].get(o['chapter'], []))
            assert out['blocks'], mc_id
        objs_with_checks = {i['obj'] for i in cmap['check_items'] if i.get('obj')}
        assert TARGET <= objs_with_checks, TARGET - objs_with_checks
