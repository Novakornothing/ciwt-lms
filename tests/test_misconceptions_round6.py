"""Content round 6: misconception tags for the objectives with the lowest tagged share (mostly certification items)
and four round-5 bank/supplement leftovers; X-IT-11.3.3 stem/rationale tightened (key and options unchanged).

Every round-6 tag must point at a distractor the engine really serves for that objective (exact option text, not the
key, same objective, ``tag_for`` returns it); the new MC-R6-* entries carry a primary source and 'Pending SME review'
and find a lesson section for their correction; the measured coverage matches what the round reports
(1543/2349 -> 1726/2349 tagged distractors, measured with tools/misconception_coverage.py)."""
import pytest

from curriculum_v2 import misconceptions as MCS
from curriculum_v2 import misconceptions_round5 as R5
from curriculum_v2 import misconceptions_round6 as R6
from curriculum_v2.exam_supplement import SUPPLEMENT
from curriculum_v2.itsup_core import EXPANSION
from tests.test_misconceptions_round3 import _maps

EMAIL = 'student13@lms.local'


@pytest.fixture(scope='module')
def maps(app, mod):
    return _maps(app, mod)


@pytest.fixture(scope='module')
def served(app, maps):
    """(bank_id, obj) -> item as Engine.pool serves it with the bank and cert items included."""
    eng = app.extensions['ciwt_mastery'].engine
    out = {}
    with app.app_context():
        for cmap in maps.values():
            for obj in cmap['objs']:
                for it in eng.pool(cmap, obj, include_bank=True, include_cert=True):
                    if it.get('bank_id'):
                        out[(it['bank_id'], obj)] = it
    return out


def test_every_round6_tag_is_a_served_distractor_of_the_same_objective(served):
    assert len(R6._T) == len(R6.TAGS) == 183
    for b, d, mc in R6._T:
        obj = MCS.MISCONCEPTIONS[mc]['obj']
        it = served.get((b, obj))
        assert it, (b, obj)
        assert d in it['options'] and d != it['correct'], (b, d)
        assert MCS.tag_for(it, d) == mc, (b, d)
        assert MCS.tag_for(it, it['correct']) is None, b


def test_round6_does_not_retag_an_earlier_tag_or_redefine_an_earlier_id():
    from curriculum_v2 import misconceptions_pass13 as P13, misconceptions_round3 as R3, misconceptions_round4 as R4
    from curriculum_v2 import checks_pass14 as P14
    from curriculum_v2.cert import misconceptions as CERT
    earlier_tags = set(P13.TAGS) | set(P14.TAGS) | set(CERT.TAGS) | set(R3.TAGS) | set(R4.TAGS) | set(R5.TAGS)
    assert not (set(R6.TAGS) & earlier_tags)
    earlier_ids = (set(P13.MISCONCEPTIONS) | set(P14.MISCONCEPTIONS) | set(CERT.MISCONCEPTIONS) | set(R3.MISCONCEPTIONS)
                   | set(R4.MISCONCEPTIONS) | set(R5.MISCONCEPTIONS))
    assert not (set(R6.MISCONCEPTIONS) & earlier_ids)


def test_new_misconceptions_are_used_sourced_and_pending():
    assert len(R6.MISCONCEPTIONS) == 39
    assert set(R6.MISCONCEPTIONS) <= set(R6.TAGS.values())
    for k, m in R6.MISCONCEPTIONS.items():
        assert k.startswith('MC-R6-') and m['status'] == 'Pending SME review' and len(m['source']) > 10, k
        assert m['label'] and m['fix'] and m['terms'], k
        assert MCS.MISCONCEPTIONS[k] is m


def test_reused_ids_are_existing_misconceptions():
    reused = {mc for _b, _d, mc in R6._T if not mc.startswith('MC-R6-')}
    assert len(reused) == 34
    assert reused <= set(MCS.MISCONCEPTIONS) - set(R6.MISCONCEPTIONS)


def test_every_round6_misconception_finds_a_lesson_section(maps):
    from mastery import content as C
    empty = []
    for mc_id in sorted(R6.MISCONCEPTIONS):
        mc = MCS.MISCONCEPTIONS[mc_id]
        cmap = maps['IT' if mc['obj'].startswith('IT-') else 'NO']
        o = cmap['objs'][mc['obj']]
        info = cmap['obj_lesson'].get(mc['obj'])
        les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
        if not C.build_correction(mc['obj'], o['text'], mc, les, chapter_lessons=cmap['by_ch'].get(o['chapter'], []))['blocks']:
            empty.append(mc_id)
    assert not empty, empty


def test_measured_coverage_after_round6(app, mod):
    from tools import misconception_coverage as T
    cov = T.measure(app, mod)
    s = T.summary(cov)
    # before round 6 (content after the pass16-merge merge, 1f752f4): 1543/2349, items 634/783, cert 168/293,
    # bank 110/131, supplement 27/30 (docs/readiness/misconception-coverage-round6-before.txt)
    assert (s['tagged_distractors'], s['distractors']) == (1726, 2349)
    assert (s['items_tagged'], s['items']) == (698, 783)
    assert s['items_by_source']['cert'] == [293, 228]
    assert s['items_by_source']['bank'] == [131, 113] and s['items_by_source']['supplement'] == [30, 28]
    assert s['covered'] == s['objectives'] == 70
    r6 = T.r6_report(cov)
    assert r6 == {'r6_tags': 183, 'r6_mcs': 39, 'r6_with_status': 39, 'r6_with_source': 39, 'r6_with_correction': 39}


def test_round5_leftovers_tagged_this_round_were_on_the_round5_list():
    assert set(R6.NEWLY_TAGGED_BANK) <= set(R5.UNTAGGED)
    assert 'X-IT-11.3.3' not in R6.NEWLY_TAGGED_BANK
    tagged_bank = {b for b, _d, _mc in R6._T if b[:2] in ('X-', 'S-')}
    assert tagged_bank == set(R6.NEWLY_TAGGED_BANK)


def test_x_it_11_3_3_key_and_options_unchanged_stem_and_rationale_tightened():
    q = next(x for x in EXPANSION if x['bank_id'] == 'X-IT-11.3.3')
    assert q['correct'] == 'When there is no tested backup of the user’s data'
    assert sorted(q['options']) == sorted(['When there is no tested backup of the user’s data',
                                           'When the device is already on the standard image',
                                           'When the fault has a known, documented vendor fix',
                                           'When the user agrees to a time after 16:00'])
    assert 'no documented fix exists' in q['text']          # the stem now rules the vendor-fix option out
    assert 'would also favour repair' not in q['explanation']
    assert 'stem rules that out' in q['explanation']
    assert q['review'] == 'Pending SME review'


def test_bank_items_other_than_x_it_11_3_3_unchanged():
    x = {q['bank_id']: q for q in EXPANSION + SUPPLEMENT}
    assert x['X-IT-9.2.2']['correct'] == 'Energy' and x['S-IT-9.2.1']['correct'] == 'Activity Monitor'
    assert x['X-IT-4.1.2']['correct'] == 'powercfg /batteryreport'
    assert all(q['correct'] in q['options'] and len(q['options']) == 4 for q in x.values())


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


def test_correction_page_shows_label_and_pending_status_for_a_round6_misconception(s13):
    mc = 'MC-R6-IT4-JAILBREAK-TRUST'
    page = s13.get(f'/student/section/1/review/IT-4.2?mc={mc}').data.decode()
    assert 'Thinking a jailbroken or rooted phone can be trusted again' in page
    assert 'Status of this mix-up description: Pending SME review.' in page
