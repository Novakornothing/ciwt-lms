"""Pass 13: every chapter-check objective (ITSUP and NETOPS) has misconception tags on its own check items, the new
tags follow the pass-11 rules, and every new misconception finds a lesson section to explain it."""
import pilot_slice as PS
from curriculum_v2 import misconceptions as MCS
from curriculum_v2 import misconceptions_pass13 as P13
from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload


def _checks():
    return ([q for o in sorted(PS.PILOT_CHECKS) for q in PS.quiz_payload(o, '')]
            + [q for o in sorted(NETOPS_CHECKS) for q in netops_quiz_payload(o)])


def test_every_chapter_check_objective_has_tags_on_its_check_items():
    checks = _checks()
    ids = {q['bank_id'] for q in checks}
    covered = {MCS.MISCONCEPTIONS[mc]['obj'] for (b, _d), mc in MCS.TAGS.items() if b in ids}
    assert {q['obj'] for q in checks} <= covered


def test_new_tags_are_real_distractors_with_matching_objectives():
    by = {q['bank_id']: q for q in _checks()}
    for (b, d), mc in P13.TAGS.items():
        q = by[b]
        assert d in q['options'] and d != q['correct'], (b, d)
        assert P13.MISCONCEPTIONS[mc]['obj'] == q['obj'], (b, mc)
        assert MCS.tag_for(q, d) == mc
        assert MCS.tag_for(q, q['correct']) is None
    assert set(P13.TAGS.values()) == set(P13.MISCONCEPTIONS)


def test_every_new_misconception_finds_a_lesson_section(app, mod):
    from mastery import content as C
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        maps = {}
        for code in ('ITSUP', 'NETOPS'):
            course = mod.Course.query.filter_by(code=code).first()
            sec = mod.ClassSection.query.filter_by(course_id=course.id).first()
            maps[code[:2] if code == 'ITSUP' else 'NO'] = eng.course_map(sec)
        empty = []
        for mc_id, mc in P13.MISCONCEPTIONS.items():
            cmap = maps['IT' if mc['obj'].startswith('IT-') else 'NO']
            o = cmap['objs'][mc['obj']]
            info = cmap['obj_lesson'].get(mc['obj'])
            les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
            out = C.build_correction(mc['obj'], o['text'], mc, les, chapter_lessons=cmap['by_ch'].get(o['chapter'], []))
            if not out['blocks']:
                empty.append(mc_id)
        assert not empty, empty
