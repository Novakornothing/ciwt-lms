"""Content round 4: misconception tags for the pass-15 certification gap items and the last two untagged chapter checks.

Every round-4 tag must point at a distractor the engine really serves (exact option text, not the key, same
objective, ``tag_for`` returns it); the pass-15 misconceptions now carry a source and 'Pending SME review'; every
chapter-check item has at least one tagged distractor; the measured coverage matches what the round reports."""
import pytest

from curriculum_v2 import misconceptions as MCS
from curriculum_v2 import misconceptions_round4 as R4
from curriculum_v2.cert.content import i05_gaps_p15 as P15
from tests.test_misconceptions_round3 import _maps, _served

EMAIL = 'student13@lms.local'


@pytest.fixture(scope='module')
def maps(app, mod):
    return _maps(app, mod)


def _cert_served(app):
    from mastery.engine import cert_items_for
    with app.app_context():
        return {x['bank_id']: x for q in P15.ITEMS for x in cert_items_for(q['obj']) if x.get('bank_id') == q['bank_id']}


def test_every_round4_tag_is_a_served_distractor_of_the_same_objective(app, maps):
    served = {b: it for b, (it, _s) in _served(maps).items()}
    served.update(_cert_served(app))
    assert len(R4._T) == len(R4.TAGS) == 7
    for b, d, mc in R4._T:
        it = served[b]
        assert d in it['options'] and d != it['correct'], (b, d)
        assert MCS.MISCONCEPTIONS[mc]['obj'] == it['obj'], (b, mc)
        assert MCS.tag_for(it, d) == mc, (b, d)
        assert MCS.tag_for(it, it['correct']) is None


def test_round4_does_not_retag_an_earlier_tag():
    from curriculum_v2 import misconceptions_pass13 as P13, misconceptions_round3 as R3, checks_pass14 as P14
    from curriculum_v2.cert import misconceptions as CERT
    earlier = set(P13.TAGS) | set(P14.TAGS) | set(CERT.TAGS) | set(R3.TAGS)
    assert not (set(R4.TAGS) & earlier)


def test_new_misconceptions_are_used_sourced_and_pending():
    assert set(R4.MISCONCEPTIONS) <= set(R4.TAGS.values())
    for k, m in R4.MISCONCEPTIONS.items():
        assert k.startswith('MC-R4-') and m['status'] == 'Pending SME review' and len(m['source']) > 10, k
        assert MCS.MISCONCEPTIONS[k] is m


def test_pass15_misconceptions_now_show_source_and_pending_status():
    assert len(P15.MISCONCEPTIONS) == 47
    for k in P15.MISCONCEPTIONS:
        m = MCS.MISCONCEPTIONS[k]
        assert m['status'] == 'Pending SME review', k
        assert m['source'] and m['source'] in R4.p15_annotations()[k]['source'], k
        for part in m['source'].split('; '):                   # every source is one pass 15 recorded for an item
            assert any(part in s for s in P15.SOURCE.values()), (k, part)


def test_pass15_single_items_coverage_is_160_of_165(app):
    served = _cert_served(app)
    singles = [q for q in P15.ITEMS if q['type'] == 'single']
    assert len(singles) == 55 and all(q['bank_id'] in served for q in singles)
    tagged = untagged = 0
    for q in singles:
        it = served[q['bank_id']]
        hits = [MCS.tag_for(it, d) for d in it['options'] if d != it['correct']]
        assert any(hits), q['bank_id']
        tagged += sum(1 for h in hits if h)
        untagged += sum(1 for h in hits if not h)
    # measured with tools/misconception_coverage.py: 155/165 before round 4, 160/165 after (5 throw-aways left)
    assert (tagged, tagged + untagged) == (160, 165)


def test_every_chapter_check_item_now_has_a_tagged_distractor(maps):
    served = _served(maps)
    checks = {b: it for b, (it, src) in served.items() if src == 'check'}
    assert len(checks) == 200
    assert [b for b, it in checks.items() if not any(MCS.tag_for(it, d) for d in it['options'] if d != it['correct'])] == []


def test_every_round4_misconception_finds_a_lesson_section(maps):
    from mastery import content as C
    empty = []
    for mc_id in sorted(set(R4.TAGS.values())):
        mc = MCS.MISCONCEPTIONS[mc_id]
        cmap = maps['IT' if mc['obj'].startswith('IT-') else 'NO']
        o = cmap['objs'][mc['obj']]
        info = cmap['obj_lesson'].get(mc['obj'])
        les = cmap['lesson_by_id'].get(info['lesson_id']) if info else None
        if not C.build_correction(mc['obj'], o['text'], mc, les, chapter_lessons=cmap['by_ch'].get(o['chapter'], []))['blocks']:
            empty.append(mc_id)
    assert not empty, empty


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


def test_correction_page_shows_pending_status_for_a_pass15_misconception(s13):
    mc = 'MC-C-IT1-REQ-VS-INC'
    page = s13.get(f'/student/section/1/review/IT-1.1?mc={mc}').data.decode()
    assert page and 'Status of this mix-up description: Pending SME review.' in page
