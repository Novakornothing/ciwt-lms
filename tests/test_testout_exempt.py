"""Pass 14: a passed chapter mastery check (test-out) marks that chapter's check 'Exempt (test-out)' in the
gradebook. No score is invented; the item drops out of completion like an excused item."""
from datetime import datetime

import pytest


def _gb(app):
    return app.extensions['ciwt_gradebook']


def _row(app, mod, sid, uid):
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, sid)
        return _gb(app).compute(sec, user_ids={uid})['rows'][0]


@pytest.fixture
def setup(app, mod):
    """Section 1, a student with no attempt on some chapter check, quiz weight > 0. Restores everything afterwards."""
    MC = app.extensions['ciwt_mastery'].models.MasteryCheck
    GS = _gb(app).models.GradebookSetting
    with app.app_context():
        sid = 1
        uid = mod.User.query.filter_by(email='student1@lms.local').first().id
        row = _row(app, mod, sid, uid)
        cell = next(c for c in row['cells'] if c['item']['type'] == 'quiz' and c['status'] == 'missing')
        ch = cell['item']['module_order']
        gs = GS.query.filter_by(section_id=sid).first()
        created = gs is None
        if created:
            gs = GS(section_id=sid)
            mod.db.session.add(gs)
        saved = (gs.weight_tests, gs.weight_skills, gs.weight_quizzes, getattr(gs, 'weight_labs', None))
        gs.weight_tests, gs.weight_skills, gs.weight_quizzes = 50, 20, 30
        gs.updated_at = datetime.utcnow()
        mod.db.session.commit()
    made = []

    def add_check(passed, target=None):
        with app.app_context():
            c = MC(section_id=sid, user_id=uid, kind='testout', target=target or f'CH-{ch}', variant='testout',
                   correct=5 if passed else 1, total=5, passed=passed, completed_at=datetime.utcnow())
            mod.db.session.add(c)
            mod.db.session.commit()
            made.append(c.id)

    yield dict(sid=sid, uid=uid, ch=ch, quiz_id=cell['item']['id'], add_check=add_check, before=row)
    with app.app_context():
        for i in made:
            mod.db.session.delete(mod.db.session.get(MC, i))
        gs = GS.query.filter_by(section_id=sid).first()
        if created:
            mod.db.session.delete(gs)
        else:
            gs.weight_tests, gs.weight_skills, gs.weight_quizzes = saved[:3]
        gs and setattr(gs, 'updated_at', datetime.utcnow())
        mod.db.session.commit()
        _gb(app).invalidate(sid)


def _cell(row, quiz_id):
    return next(c for c in row['cells'] if c['item']['type'] == 'quiz' and c['item']['id'] == quiz_id)


def test_passed_testout_marks_chapter_check_exempt_and_lifts_completion(app, mod, setup):
    base = _row(app, mod, setup['sid'], setup['uid'])
    assert _cell(base, setup['quiz_id'])['status'] == 'missing'
    setup['add_check'](True)
    row = _row(app, mod, setup['sid'], setup['uid'])
    c = _cell(row, setup['quiz_id'])
    assert c['status'] == 'exempt' and c['score'] is None and c['raw'] is None   # no fabricated score
    assert row['completion'] > base['completion'], (base['completion'], row['completion'])
    assert row['grade'] == base['grade'] and row['cat_avgs'] == base['cat_avgs']   # averages untouched


def test_failed_testout_or_other_chapter_does_not_exempt(app, mod, setup):
    setup['add_check'](False)
    setup['add_check'](True, target='CH-999')
    assert _cell(_row(app, mod, setup['sid'], setup['uid']), setup['quiz_id'])['status'] == 'missing'


def test_real_attempt_wins_over_exemption(app, mod, setup):
    setup['add_check'](True)
    with app.app_context():
        a = mod.QuizAttempt(user_id=setup['uid'], quiz_id=setup['quiz_id'], score=60.0, completed_at=datetime.utcnow(),
                            **({'section_id': setup['sid']} if hasattr(mod.QuizAttempt, 'section_id') else {}))
        mod.db.session.add(a)
        mod.db.session.commit()
        aid = a.id
    try:
        c = _cell(_row(app, mod, setup['sid'], setup['uid']), setup['quiz_id'])
        assert c['status'] == 'scored' and c['score'] == 60.0
    finally:
        with app.app_context():
            mod.db.session.delete(mod.db.session.get(mod.QuizAttempt, aid))
            mod.db.session.commit()
            _gb(app).invalidate(setup['sid'])


def test_instructor_sees_exempt_label_in_grid_detail_and_csv(app, mod, setup, instructor):
    setup['add_check'](True)
    sid, uid = setup['sid'], setup['uid']
    grid = instructor.get(f'/instructor/section/{sid}/gradebook').get_data(as_text=True)
    assert 'Exempt (test-out)' in grid
    det = instructor.get(f'/instructor/section/{sid}/gradebook/student/{uid}').get_data(as_text=True)
    assert 'Exempt (test-out)' in det
    csv_text = instructor.get(f'/instructor/section/{sid}/gradebook.csv').get_data(as_text=True)
    assert 'Exempt (test-out)' in csv_text


def test_student_sees_exempt_status(app, mod, setup, student):
    setup['add_check'](True)
    h = student.get(f"/student/section/{setup['sid']}/grades").get_data(as_text=True)
    assert 'Exempt (test-out)' in h
