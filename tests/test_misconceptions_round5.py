"""Content round 5: misconception tags for the X-IT expansion bank and the exam supplement.

Every round-5 tag must point at a distractor the engine really serves for that objective (Engine.pool with
include_bank: exact option text, not the key, same objective, ``tag_for`` returns it); the new MC-R5-* entries carry a
primary source and 'Pending SME review' and find a lesson section for their correction; the measured coverage matches
what the round reports (bank 0/131 -> 110/131, supplement 0/30 -> 27/30)."""
import json
import pytest

from curriculum_v2 import misconceptions as MCS
from curriculum_v2 import misconceptions_round5 as R5
from curriculum_v2.exam_supplement import SUPPLEMENT
from curriculum_v2.itsup_core import EXPANSION
from tests.test_misconceptions_round3 import _maps

EMAIL = 'student13@lms.local'


@pytest.fixture(scope='module')
def maps(app, mod):
    return _maps(app, mod)


@pytest.fixture(scope='module')
def served(app, maps):
    """bank_id -> item, as Engine.pool serves the X-IT bank and supplement items (include_bank=True)."""
    eng = app.extensions['ciwt_mastery'].engine
    out = {}
    with app.app_context():
        for cmap in maps.values():
            for obj in cmap['objs']:
                for it in eng.pool(cmap, obj, include_bank=True, include_cert=False):
                    if it['src'] in ('bank', 'supplement'):
                        out[it['bank_id']] = it
    return out


def test_every_bank_and_supplement_item_is_served(served):
    assert set(served) == {q['bank_id'] for q in EXPANSION + SUPPLEMENT}
    assert len(served) == 161


def test_every_round5_tag_is_a_served_distractor_of_the_same_objective(served):
    assert len(R5._T) == len(R5.TAGS) == 348
    for b, d, mc in R5._T:
        it = served[b]
        assert d in it['options'] and d != it['correct'], (b, d)
        assert MCS.MISCONCEPTIONS[mc]['obj'] == it['obj'], (b, mc)
        assert MCS.tag_for(it, d) == mc, (b, d)
        assert MCS.tag_for(it, it['correct']) is None, b


def test_round5_does_not_retag_an_earlier_tag_or_redefine_an_earlier_id():
    from curriculum_v2 import misconceptions_pass13 as P13, misconceptions_round3 as R3, misconceptions_round4 as R4
    from curriculum_v2 import checks_pass14 as P14
    from curriculum_v2.cert import misconceptions as CERT
    earlier_tags = set(P13.TAGS) | set(P14.TAGS) | set(CERT.TAGS) | set(R3.TAGS) | set(R4.TAGS)
    assert not (set(R5.TAGS) & earlier_tags)
    earlier_ids = set(P13.MISCONCEPTIONS) | set(P14.MISCONCEPTIONS) | set(CERT.MISCONCEPTIONS) | set(R3.MISCONCEPTIONS) | set(R4.MISCONCEPTIONS)
    assert not (set(R5.MISCONCEPTIONS) & earlier_ids)


def test_new_misconceptions_are_used_sourced_and_pending():
    assert len(R5.MISCONCEPTIONS) == 66
    assert set(R5.MISCONCEPTIONS) <= set(R5.TAGS.values())
    for k, m in R5.MISCONCEPTIONS.items():
        assert k.startswith('MC-R5-') and m['status'] == 'Pending SME review' and len(m['source']) > 10, k
        assert m['label'] and m['fix'] and m['terms'], k
        assert MCS.MISCONCEPTIONS[k] is m


def test_reused_ids_are_existing_misconceptions_with_the_items_objective():
    reused = {mc for _b, _d, mc in R5._T if not mc.startswith('MC-R5-')}
    assert len(reused) == 71
    assert reused <= set(MCS.MISCONCEPTIONS)


def test_bank_and_supplement_coverage_matches_the_round(served):
    tagged = {}
    for b, it in served.items():
        tagged[b] = any(MCS.tag_for(it, d) for d in it['options'] if d != it['correct'])
    bank = [b for b in tagged if b.startswith('X-')]
    sup = [b for b in tagged if b.startswith('S-')]
    # measured with tools/misconception_coverage.py: bank 0/131 and supplement 0/30 before round 5
    assert (sum(tagged[b] for b in bank), len(bank)) == (110, 131)
    assert (sum(tagged[b] for b in sup), len(sup)) == (27, 30)
    assert sorted(b for b, t in tagged.items() if not t) == sorted(R5.UNTAGGED)


def test_bank_items_are_unchanged_by_round5():
    """Round 5 adds tags only: no bank or supplement key, stem or option was edited (frozen counts and a spot value)."""
    x = {q['bank_id']: q for q in EXPANSION + SUPPLEMENT}
    assert x['X-IT-3.2.1']['correct'] == '12 TB' and x['S-NO-9.2.1']['correct'] == 'encapsulation dot1Q 20'
    assert all(q['correct'] in q['options'] and len(q['options']) == 4 for q in x.values())


def test_every_round5_misconception_finds_a_lesson_section(maps):
    from mastery import content as C
    empty = []
    for mc_id in sorted(R5.MISCONCEPTIONS):
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


def test_correction_page_shows_label_and_pending_status_for_a_round5_misconception(s13):
    mc = 'MC-R5-IT5-DORA'
    page = s13.get(f'/student/section/1/review/IT-5.2?mc={mc}').data.decode()
    assert 'Mixing up the order of the DHCP exchange' in page
    assert 'Status of this mix-up description: Pending SME review.' in page


def _bank_setting(app, mod, on):
    """Set "Also use the chapter item bank" for section 1; returns the previous row state to restore."""
    MS = app.extensions['ciwt_mastery'].models.MasterySetting
    with app.app_context():
        row = MS.query.filter_by(section_id=1).first()
        prev = None if row is None else (row.enabled, row.testout, row.testout_bank, row.cert_items)
        if row is None:
            row = MS(section_id=1, enabled=True, testout=True, cert_items=True)
            mod.db.session.add(row)
        row.testout_bank = on
        mod.db.session.commit()
    return prev


def _restore_setting(app, mod, prev):
    MS = app.extensions['ciwt_mastery'].models.MasterySetting
    with app.app_context():
        row = MS.query.filter_by(section_id=1).first()
        if prev is None:
            mod.db.session.delete(row)
        else:
            row.enabled, row.testout, row.testout_bank, row.cert_items = prev
        mod.db.session.commit()


def _open_review(app, client, uid, obj, mc):
    api = app.extensions['ciwt_mastery']
    assert client.get(f'/student/section/1/review/{obj}?mc={mc}').status_code == 200
    with app.app_context():
        c = (api.models.MasteryCheck.query.filter_by(section_id=1, user_id=uid, kind='review', target=obj, completed_at=None)
             .order_by(api.models.MasteryCheck.id.desc()).first())
        return c.id, json.loads(c.items_json)


def test_with_the_bank_on_a_round5_correction_serves_its_bank_item_and_records_the_mixup(app, mod, s13):
    """Round 5 e2e finding made permanent: the round-5 tags only reach students when the class turns the bank on;
    then the correction check for a round-5 mix-up leads with the X-IT item carrying it, and the tagged wrong
    answer is recorded as that mix-up. With the bank off, no X-IT/S- item is served."""
    api = app.extensions['ciwt_mastery']
    mc, obj, item, wrong = 'MC-R5-IT5-DORA', 'IT-5.2', 'X-IT-5.2.2', 'Discover'
    assert MCS.TAGS[(item, wrong)] == mc
    with app.app_context():
        uid = mod.User.query.filter_by(email=EMAIL).first().id
    prev = _bank_setting(app, mod, True)
    try:
        cid, items = _open_review(app, s13, uid, obj, mc)
        assert items[0]['bank_id'] == item and wrong in items[0]['options']
        data = {'check_id': cid}
        data.update({f'q{i}': (wrong if it['bank_id'] == item else it['correct']) for i, it in enumerate(items)})
        assert s13.post(f'/student/section/1/review/{obj}', data=data).status_code == 303
        with app.app_context():
            st = api.engine.student_state(mod.db.session.get(mod.ClassSection, 1), mod.db.session.get(mod.User, uid), log=False)
        assert mc in st['misconceptions'] and st['misconceptions'][mc]['active']
        assert st['misconceptions'][mc]['label'] == 'Mixing up the order of the DHCP exchange'
        _bank_setting(app, mod, False)
        _cid, items = _open_review(app, s13, uid, obj, mc)
        assert items and not [it['bank_id'] for it in items if str(it.get('bank_id') or '').startswith(('X-', 'S-'))]
    finally:
        _restore_setting(app, mod, prev)
