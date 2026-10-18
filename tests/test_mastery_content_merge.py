"""Pass 12: the mastery engine after the content merge — typed items (multi-select, ordering, matching),
practice-exam evidence (weight 0.8) and the new cert-supplement lesson sections.
Practice attempts below are test rows in the throwaway DB (removed afterwards), not real student data."""
import json
from datetime import datetime

import pytest

from mastery import content as C
from mastery import model as M
from mastery.engine import judge


@pytest.fixture(scope='module', autouse=True)
def objective_tagged_checks(app, mod):
    with app.app_context():
        mod.sync_pilot_slice()
        mod.db.session.commit()


MULTI = {'type': 'multi', 'options': ['a', 'b', 'c', 'd'], 'correct': ['a', 'c']}
ORDER = {'type': 'order', 'options': ['x', 'y', 'z'], 'correct': ['y', 'x', 'z']}
MATCH = {'type': 'match', 'options': ['1', '2', '3', '9'], 'correct': ['2', '1', '3']}
SINGLE = {'options': ['p', 'q'], 'correct': 'q'}


def test_judge_typed_items_all_or_nothing():
    assert judge(MULTI, json.dumps(['c', 'a'])) == (True, True)
    assert judge(MULTI, json.dumps(['a'])) == (True, False)
    assert judge(ORDER, json.dumps(['y', 'x', 'z'])) == (True, True)
    assert judge(ORDER, json.dumps(['x', 'y', 'z'])) == (True, False)
    assert judge(MATCH, json.dumps(['2', '1', '3'])) == (True, True)
    assert judge(MATCH, json.dumps(['2', '1', '9'])) == (True, False)


def test_judge_cannot_judge_stale_or_malformed_answers():
    assert judge(MULTI, json.dumps(['a', 'old wording'])) == (False, False)
    assert judge(ORDER, 'not json') == (False, False)
    assert judge(SINGLE, 'old option') == (False, False)
    assert judge(SINGLE, 'q') == (True, True) and judge(SINGLE, None) == (True, False)


def test_practice_weight_and_label():
    assert M.WEIGHTS['practice'] == 0.8 and 'practice' in M.KIND_LABEL


def test_review_pools_only_use_single_answer_items(app):
    with app.app_context():
        api = app.extensions['ciwt_mastery']
        from mastery.engine import Engine  # noqa: F401
        import app as lms
        cmap = api.engine.course_map(lms.db.session.get(lms.ClassSection, 1))
        for obj in list(cmap['objs'])[:50]:
            for it in api.engine.pool(cmap, obj, include_bank=True):
                assert isinstance(it['correct'], str) and it['correct'] in it['options']


def test_cert_supplement_sections_are_segmented_without_instructor_notes():
    from curriculum_v2.cert import supplements as S
    sup = list(S.SUPPLEMENTS.values())[0] if isinstance(S.SUPPLEMENTS, dict) else S.SUPPLEMENTS[0]
    html = '<h3>Intro</h3><p>' + 'word ' * 60 + '</p>' + S.section_html(sup)
    secs = C.sections(html)
    assert [s['heading'] for s in secs][-1] == sup['title']
    assert 'Pending SME review' not in C.clean(secs[-1]['html'])
    lesson = {'id': 1, 'label': '9.9', 'title': 'T', 'html': html}
    r = C.build_review('IT-9.9', sup['title'], lesson)
    blob = json.dumps(r['blocks'], default=str)
    assert sup['title'] in blob and 'Pending SME review' not in blob      # what the student is shown


@pytest.fixture
def practice_rows(app, mod):
    from curriculum_v2.cert.practice import bank
    with app.app_context():
        u = mod.User.query.filter_by(email='student2@lms.local').first()
        b = bank()
        picks = [it for it in b.values() if it.get('obj') == 'IT-1.2'][:3]
        multi = next(it for it in b.values() if it.get('type') == 'multi' and it.get('obj', '').startswith('IT-'))
        chosen = [[it['id'], 'A2:4.4'] for it in picks] + [[multi['id'], 'A1:2.1']]
        answers = {'0': json.dumps(picks[0]['correct']) if picks[0]['type'] != 'single' else picks[0]['correct'],
                   '1': '',                                            # blank: skipped, never counted as wrong
                   '3': json.dumps(list(multi['correct']))}
        now = datetime(2026, 10, 10, 9, 0)
        att = mod.PracticeAttempt(user_id=u.id, exam='A2', items=json.dumps(chosen), started_at=now, deadline=now,
                                  submitted_at=now, answers=json.dumps(answers), correct=2, total=4)
        mod.db.session.add(att); mod.db.session.commit()
        aid, uid = att.id, u.id
    yield uid, picks, multi
    with app.app_context():
        mod.db.session.delete(mod.db.session.get(mod.PracticeAttempt, aid)); mod.db.session.commit()


def test_practice_exam_answers_become_mastery_evidence(app, mod, practice_rows):
    uid, picks, multi = practice_rows
    with app.app_context():
        api = app.extensions['ciwt_mastery']
        st = api.engine.student_state(mod.db.session.get(mod.ClassSection, 1), mod.db.session.get(mod.User, uid), log=False)
        prac = [o for obj, obs in st['evidence'].items() for o in obs if o.get('kind') == 'practice']
    assert st['sources'].get('practice') == 2               # item 0 and the multi-select; blank and unanswered skipped
    assert {o['ref'] for o in prac} == {picks[0]['id'], multi['id']}
    assert all(o['correct'] for o in prac)
    est = st['states']['IT-1.2']
    assert est['n_eff'] >= 0.8 - 1e-9


def test_practice_evidence_never_touches_the_gradebook(app, mod, instructor):
    import re
    from curriculum_v2.cert.practice import bank
    def page():
        h = instructor.get('/instructor/section/1/gradebook').data.decode()
        return re.findall(r'<table\b.*?</table>', h, re.S)        # the grade tables themselves
    page()
    before = page()
    assert before
    with app.app_context():
        u = mod.User.query.filter_by(email='student3@lms.local').first()
        it = next(i for i in bank().values() if i.get('obj') == 'IT-1.2' and i['type'] == 'single')
        now = datetime(2026, 10, 10, 9, 0)
        att = mod.PracticeAttempt(user_id=u.id, exam='A2', items=json.dumps([[it['id'], 'A2:4.4']]), started_at=now,
                                  deadline=now, submitted_at=now, answers=json.dumps({'0': it['correct']}), correct=1, total=1)
        mod.db.session.add(att); mod.db.session.commit(); aid = att.id
    try:
        assert page() == before
    finally:
        with app.app_context():
            mod.db.session.delete(mod.db.session.get(mod.PracticeAttempt, aid)); mod.db.session.commit()
