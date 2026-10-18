"""Content round 3 (Oct 18 2026): misconception tags for the Tests A/B/C and chapter-check items that had none.

Checks that every round-3 tag points at a distractor the engine really serves (exact option text, not the key, same
objective), that every new misconception carries a primary source and 'Pending SME review', that each one finds a
lesson section for its correction, and that the coverage the round reports is what the engine now sees."""
import pytest

from curriculum_v2 import misconceptions as MCS
from curriculum_v2 import misconceptions_round3 as R3

EMAIL = 'student13@lms.local'


def _maps(app, mod):
    out = {}
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        for code in ('ITSUP', 'NETOPS'):
            course = mod.Course.query.filter_by(code=code).first()
            sec = mod.ClassSection.query.filter_by(course_id=course.id).first()
            out['IT' if code == 'ITSUP' else 'NO'] = eng.course_map(sec)
    return out


def _served(maps):
    """bank_id -> (item, source) for every single-answer chapter-check and Tests A/B/C item the engine scores."""
    by = {}
    for cmap in maps.values():
        for it in cmap['check_items']:
            by[it['bank_id']] = (it, 'check')
        for t in cmap['tests'].values():
            for q in t['qs'] if isinstance(t['qs'], list) else []:
                if isinstance(q, dict) and q.get('obj') in cmap['objs'] and q.get('bank_id'):
                    by[q['bank_id']] = (q, 'test')
    return {b: v for b, v in by.items()
            if (v[0].get('type') or 'single') == 'single' and v[0].get('options') and v[0].get('correct') in v[0]['options']}


@pytest.fixture(scope='module')
def served(app, mod):
    return _served(_maps(app, mod))


def test_every_round3_tag_is_a_served_distractor_of_the_same_objective(served):
    assert len(R3._T) == len(R3.TAGS)                                # no duplicate (item, distractor) pairs
    for b, d, mc in R3._T:
        assert b in served, b
        it, _src = served[b]
        assert d in it['options'] and d != it['correct'], (b, d)
        assert MCS.MISCONCEPTIONS[mc]['obj'] == it['obj'], (b, mc)
        assert MCS.tag_for(it, d) == mc, (b, d)
        assert MCS.tag_for(it, it['correct']) is None


def test_round3_does_not_retag_a_distractor_earlier_rounds_tagged():
    from curriculum_v2 import misconceptions_pass13 as P13
    from curriculum_v2 import checks_pass14 as P14
    from curriculum_v2.cert import misconceptions as CERT
    earlier = set(P13.TAGS) | set(P14.TAGS) | set(CERT.TAGS)
    import importlib
    base = importlib.import_module('curriculum_v2.misconceptions')
    assert not (set(R3.TAGS) & earlier)
    assert all(base.TAGS[k] == v for k, v in R3.TAGS.items())


def test_new_misconceptions_have_a_source_and_are_pending_sme_review():
    used = set(R3.TAGS.values())
    assert set(R3.MISCONCEPTIONS) <= used                              # nothing defined and left unused
    for mc_id, m in R3.MISCONCEPTIONS.items():
        assert mc_id.startswith('MC-R3-'), mc_id
        assert m['status'] == 'Pending SME review', mc_id
        assert m['source'] and len(m['source']) > 10, mc_id
        assert m['label'] and m['fix'] and m['terms'], mc_id
        assert MCS.MISCONCEPTIONS[mc_id] is m
    # reused ids (no R3 prefix) are earlier rounds' ids, not new definitions
    for mc in used - set(R3.MISCONCEPTIONS):
        assert not mc.startswith('MC-R3-') and mc in MCS.MISCONCEPTIONS, mc


def test_every_round3_misconception_finds_a_lesson_section(app, mod):
    from mastery import content as C
    maps = _maps(app, mod)
    empty = []
    for mc_id in sorted(set(R3.TAGS.values())):
        mc = MCS.MISCONCEPTIONS[mc_id]
        cmap = maps['IT' if mc['obj'].startswith('IT-') else 'NO']
        o = cmap['objs'][mc['obj']]
        info = cmap['obj_lesson'].get(mc['obj'])
        les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
        out = C.build_correction(mc['obj'], o['text'], mc, les, chapter_lessons=cmap['by_ch'].get(o['chapter'], []))
        if not out['blocks']:
            empty.append(mc_id)
    assert not empty, empty


def test_tests_abc_and_chapter_checks_now_carry_tags(served):
    untagged = {'test': [], 'check': []}
    for b, (it, src) in served.items():
        if not any(MCS.tag_for(it, d) for d in it['options'] if d != it['correct']):
            untagged[src].append(b)
    # measured with tools/misconception_coverage.py: Tests A/B/C 30/129 -> 129/129 tagged, checks 183/200 -> 198/200
    assert untagged['test'] == []
    assert sorted(untagged['check']) == ['NQ5.5', 'Q13.6']             # throw-away distractors only, left untagged


@pytest.fixture
def s13(app, mod):
    api = app.extensions['ciwt_mastery']

    def clean(uid):
        with app.app_context():
            for t in (api.models.MasteryDecision, api.models.MasteryCheck, api.models.MasteryOverride):
                t.query.filter_by(section_id=1, user_id=uid).delete()
            mod.db.session.commit()
    with app.app_context():
        uid = mod.User.query.filter_by(email=EMAIL).first().id
    clean(uid)
    c = app.test_client()
    assert c.post('/login', data={'email': EMAIL, 'password': 'student123'}).status_code in (302, 303)
    yield c
    clean(uid)


def test_correction_page_marks_round3_wording_pending_sme_review(s13):
    mc = 'MC-R3-IT2-PCIE-LANES'
    page = s13.get(f'/student/section/1/review/IT-2.1?mc={mc}').data.decode()
    assert MCS.MISCONCEPTIONS[mc]['label'].split(',')[0] in page
    assert 'Status of this mix-up description: Pending SME review.' in page
