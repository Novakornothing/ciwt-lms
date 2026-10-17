"""Pass 8: the assessment player never ships the answer key, rationales or study tips to the browser."""
import json
import re

from test_prg import _release


def _player_items(body):
    m = re.search(r'<script type="application/json" id="assessQuestions">(.*?)</script>', body, re.S)
    assert m, 'assessment JSON missing'
    return json.loads(m.group(1))


def test_quiz_page_has_no_answer_key(student, app, mod, ids):
    with app.app_context():
        qs = json.loads(mod.db.session.get(mod.Quiz, ids['quiz']).questions)
    items = _player_items(student.get(f"/student/quiz/{ids['section']}/{ids['quiz']}").get_data(as_text=True))
    assert len(items) == len(qs)
    for it, q in zip(items, qs):
        assert set(it) <= {'text', 'options', 'lo', 'lo_code', 'lo_text'}
        assert it['text'] == (q.get('text') or q.get('q')) and it['options'] == q['options']


def test_test_page_has_no_answer_key(student, app, mod, ids):
    _release(app, mod, ids, ids['test'])
    body = student.get(f"/student/test/{ids['section']}/{ids['test']}").get_data(as_text=True)
    items = _player_items(body)
    assert items and all('correct' not in it and 'explanation' not in it and 'study_tip' not in it for it in items)
    assert '"correct"' not in body
