"""Adaptive e2e round 2 (Oct 18 2026): the three small UI issues ADAPTIVE_E2E.md listed.

1. Stuck cells on the instructor heatmap get a visible marker (S flag + dashed outline) and screen-reader text.
2. The override dialog's status line follows the objective picked under "Applies to" (per-student status lines).
3. The review page shows the evidence once (it was both the last "Why" bullet and an "Evidence:" line).
"""
import json
import re
from pathlib import Path

import pytest
from flask import render_template_string

import mastery as MX
from curriculum_v2 import misconceptions as MCS
from mastery import model as M

ROOT = Path(__file__).resolve().parents[1]
EMAIL = 'student12@lms.local'


# ------------------------------------------------------------------ pure helpers
def _cmap():
    objs = {'IT-1.1': {'chapter': 1, 'text': 'a'}, 'IT-1.2': {'chapter': 1, 'text': 'b'}, 'IT-2.1': {'chapter': 2, 'text': 'c'}}
    return {'objs': objs, 'chapters': [1, 2], 'chapter_objs': {1: ['IT-1.1', 'IT-1.2'], 2: ['IT-2.1']}}


def _row(state, **kw):
    r = {'state': state, 'action': None, 'override': None, 'override_scope': None, 'stuck': False}
    r.update(kw)
    return r


def test_status_lines_cover_every_objective_and_chapter():
    st = {'decision': {'rows': {
        'IT-1.1': _row('review', stuck=True),
        'IT-1.2': _row('developing', action={'type': 'review'}),
        'IT-2.1': _row('not_started', override='lock', override_scope='chapter')}},
        'states': {'IT-1.1': {'pct': 31}, 'IT-1.2': {'pct': 55}, 'IT-2.1': {'pct': 20}}}
    out = MX.status_lines(_cmap(), st)
    assert set(out) == {'IT-1.1', 'IT-1.2', 'IT-2.1', 'CH-1', 'CH-2'}
    assert out['IT-1.1'] == 'IT-1.1: Needs review 31% · stuck after two reviews'
    assert out['IT-1.2'] == 'IT-1.2: Developing 55% · Review inserted'
    # no percentage for not started; the chapter-level override is named
    assert out['IT-2.1'] == 'IT-2.1: Not started · override: lock (chapter)'
    assert out['CH-1'] == 'Whole chapter 1: 1 needs review, 1 developing (of 2 objectives) · 1 stuck'
    assert out['CH-2'] == 'Whole chapter 2: 1 not started (of 1 objective) · chapter override: lock'


def test_why_macro_shows_the_evidence_once(app):
    tpl = ('{% from "mastery/_macros.html" import why with context %}'
           '{{ why(reasons, evidence=evidence) }}')
    ev = '2 of 5 questions right (chapter checks 2/5)'
    with app.test_request_context():
        dup = render_template_string(tpl, reasons=['A short review will help.', f'Your estimate is 40% (low confidence): {ev}.'], evidence=ev)
        own = render_template_string(tpl, reasons=['You opened this yourself.'], evidence=ev)
        none_yet = render_template_string(tpl, reasons=['There is no answer evidence on this objective yet.'],
                                          evidence='No questions answered yet')
    assert dup.count(ev) == 1 and 'Evidence:' not in dup
    assert own.count(ev) == 1 and 'Evidence:' in own        # still shown when no reason carries it
    assert 'Evidence:' not in none_yet


def test_override_dialog_script_follows_the_applies_to_choice():
    js = (ROOT / 'static/js/mastery.js').read_text()
    assert "getElementById('mxStates')" in js and "addEventListener('change', describe)" in js
    modal = (ROOT / 'templates/mastery/_override_modal.html').read_text()
    assert 'aria-live="polite"' in modal and 'aria-describedby="mxOverrideState"' in modal
    assert 'id="mxStates"' in modal


# ------------------------------------------------------------------ through the routes
@pytest.fixture(scope='module', autouse=True)
def objective_tagged_checks(app, mod):
    with app.app_context():
        mod.sync_pilot_slice()
        mod.db.session.commit()


def _clean(app, mod, uid):
    api = app.extensions['ciwt_mastery']
    with app.app_context():
        for t in (api.models.MasteryDecision, api.models.MasteryCheck, api.models.MasteryOverride):
            t.query.filter_by(section_id=1, user_id=uid).delete()
        mod.QuizAttempt.query.filter_by(user_id=uid).delete()
        mod.TestAttempt.query.filter_by(user_id=uid, section_id=1).delete()
        mod.TimeLog.query.filter_by(user_id=uid, kind='study').delete()
        mod.db.session.commit()


@pytest.fixture
def s12(app, mod):
    with app.app_context():
        u = mod.User.query.filter_by(email=EMAIL).first()
        uid = u.id
        cols = [c.name for c in mod.TestAttempt.__table__.columns]
        saved = [{k: getattr(t, k) for k in cols} for t in mod.TestAttempt.query.filter_by(user_id=uid, section_id=1)]
    _clean(app, mod, uid)
    c = app.test_client()
    assert c.post('/login', data={'email': EMAIL, 'password': 'student123'}).status_code in (302, 303)
    c.uid = uid
    yield c
    _clean(app, mod, uid)
    with app.app_context():
        for row in saved:
            mod.db.session.add(mod.TestAttempt(**row))
        mod.db.session.commit()


def _miss_chapter1(app, mod, client):
    with app.app_context():
        m1 = mod.Module.query.filter_by(course_id=1, order=1).first()
        q = mod.Quiz.query.filter_by(module_id=m1.id).first()
        qid, qs = q.id, json.loads(q.questions)
    data = {}
    for i, it in enumerate(qs):
        tagged = [d for (b, d) in MCS.TAGS if b == it.get('bank_id') and d in it['options']]
        data[f'q{i}'] = tagged[0] if tagged else next(o for o in it['options'] if o != it['correct'])
    assert client.post(f'/student/quiz/1/{qid}', data=data).status_code in (302, 303)


def _miss_review(app, client, obj):
    with app.app_context():
        MC_ = app.extensions['ciwt_mastery'].models.MasteryCheck
        c = (MC_.query.filter_by(section_id=1, user_id=client.uid, kind='review', target=obj, completed_at=None)
             .order_by(MC_.id.desc()).first())
        cid, items = c.id, json.loads(c.items_json)
    data = {'check_id': cid}
    for i, it in enumerate(items):
        data[f'q{i}'] = next(o for o in it['options'] if o != it['correct'])
    assert client.post(f'/student/section/1/review/{obj}', data=data).status_code == 303


def _cell(html, uid, obj):
    m = re.search(r'<button type="button" class="(mx-cell[^"]*)"[^>]*data-mx-user="%d"[^>]*data-mx-target="%s">(.*?)</button>'
                  % (uid, re.escape(obj)), html, re.S)
    assert m, obj
    return m.group(1), m.group(2)


def _states(html):
    m = re.search(r'<script type="application/json" id="mxStates">(.*?)</script>', html, re.S)
    assert m
    return json.loads(m.group(1))


def test_review_page_shows_the_evidence_once(app, mod, s12):
    _miss_chapter1(app, mod, s12)
    page = s12.get('/student/section/1/review/IT-1.1').data.decode()
    with app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        u = mod.db.session.get(mod.User, s12.uid)
        est = app.extensions['ciwt_mastery'].engine.student_state(sec, u, log=False)['states']['IT-1.1']
    ev = M.describe_counts(est)
    assert page.count(ev) == 1, ev
    # a self-opened review (no engine reasons) still shows its evidence exactly once
    page = s12.get('/student/section/1/review/IT-1.3?variant=practice').data.decode()
    with app.app_context():
        est = app.extensions['ciwt_mastery'].engine.student_state(sec, u, log=False)['states']['IT-1.3']
    assert page.count(M.describe_counts(est)) == 1


def test_stuck_cell_has_a_visible_marker_and_text_and_dialog_lines(app, mod, s12, instructor):
    obj = 'IT-1.1'
    _miss_chapter1(app, mod, s12)
    s12.get(f'/student/section/1/review/{obj}')
    _miss_review(app, s12, obj)
    s12.get(f'/student/section/1/review/{obj}')
    _miss_review(app, s12, obj)
    html = instructor.get('/instructor/section/1/mastery?ch=1').data.decode()
    cls, inner = _cell(html, s12.uid, obj)
    assert 'mx-cell-stuck' in cls
    assert '<span class="mx-flag mx-flag-stuck">S</span>' in inner       # visible, inside aria-hidden
    assert 'stuck after two reviews' in inner.split('mx-cell-sr', 1)[1]  # screen-reader text
    assert 'stuck (two reviews done, nothing more inserted)' in html     # legend
    # a cell that is not stuck has no marker
    cls2, inner2 = _cell(html, s12.uid, 'IT-1.2')
    assert 'mx-cell-stuck' not in cls2 and 'mx-flag-stuck' not in inner2
    # the dialog has a status line for every target this student can be given, incl. other chapters
    lines = _states(html)[str(s12.uid)]
    assert lines[obj].startswith(f'{obj}: Needs review') and 'stuck after two reviews' in lines[obj]
    assert lines['IT-1.2'].startswith('IT-1.2: ') and 'stuck' not in lines['IT-1.2']
    assert 'IT-5.1' in lines and lines['CH-1'].startswith('Whole chapter 1: ') and '1 stuck' in lines['CH-1']
    assert 'CH-13' in lines
    # the per-student page carries the same lines for its "New override" dialog
    page = instructor.get(f'/instructor/section/1/mastery/student/{s12.uid}').data.decode()
    assert _states(page) == {str(s12.uid): lines}
