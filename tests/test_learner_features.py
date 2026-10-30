"""Skip What You Know, Help Desk Queue, and Daily Review."""
import json
from datetime import date, timedelta

from learner.deck import (NEW_PER_DAY, apply_review, cards, due_queue, score_card, session_cards, sm2_step,
                          streak_after, typed_quality)
from learner.placement import MAX_ITEMS, blank, next_item, observe, pick_item, plan, status_of
from learner.placement_bank import items_for
from learner.tickets import PRIORITIES, TICKETS, get_ticket, grade, replay


def test_deck_has_commands_and_concepts():
    deck = cards()
    assert len(deck) >= 400
    kinds = {c['kind'] for c in deck}
    assert kinds == {'command', 'concept'}
    assert sum(1 for c in deck if c['kind'] == 'command') >= 40
    assert all(len(c['options']) == 4 for c in deck if c['kind'] == 'concept')
    assert len({c['id'] for c in deck}) == len(deck)


def test_sm2_intervals_lapse_and_queue():
    ease, interval, reps = sm2_step(2.5, 0, 0, 5)
    assert (interval, reps) == (1, 1)
    ease, interval, reps = sm2_step(ease, interval, reps, 5)
    assert (interval, reps) == (6, 2) and ease > 2.5
    ease2, interval2, reps2 = sm2_step(ease, interval, reps, 1)
    assert reps2 == 0 and interval2 == 1 and ease2 < ease
    today = date(2026, 10, 30)
    state = apply_review(None, 5, today)
    assert state['due'] == today + timedelta(days=1) and state['reps'] == 1
    state = apply_review(state, 0, state['due'])
    assert state['reps'] == 0 and state['lapses'] == 1
    deck = cards()
    queue = due_queue(deck, {}, today, 'ITSUP')
    assert len(queue) == NEW_PER_DAY
    topics = [c['topic'] for c in queue]
    assert 'command' in topics and 'command' != topics[0]
    sitting = session_cards(queue)
    assert len(sitting) == NEW_PER_DAY
    cmd = next(c for c in deck if c['kind'] == 'command')
    assert typed_quality(cmd['answer'].upper(), cmd['accept']) == 5
    assert typed_quality('', cmd['accept']) == 0
    assert typed_quality('not a command', cmd['accept']) == 1
    assert score_card(cmd, cmd['answer']) == 5
    streak, last = streak_after(3, today - timedelta(days=1), today, True)
    assert streak == 4 and last == today
    streak, last = streak_after(4, today, today, True)
    assert streak == 4 and last == today
    assert streak_after(4, today - timedelta(days=3), today, True) == (1, today)


def test_placement_stops_early_and_builds_a_plan():
    chapters = [1, 2, 3, 4]
    items = []
    for ch in chapters:
        for letter in 'abc':
            items.append({'id': f'c{ch}{letter}', 'chapter': ch, 'correct': 'yes', 'options': ['yes', 'no']})
    state = blank(chapters)
    used = []
    while True:
        item, why = next_item(state, items, used, len(used), max_items=20, min_items=4)
        if item is None:
            break
        observe(state, item['chapter'], False)
        used.append(item['id'])
    assert why == 'confident' and len(used) == 4 and len(used) < 20
    built = plan(state)
    assert built['skip'] == [] and built['review'] == [1, 2, 3, 4] and built['start'] == 1
    # two correct answers test out; one correct does not; uncertainty returns to that chapter
    state = blank([1, 2])
    pool = [it for it in items if it['chapter'] in (1, 2)]
    first = pick_item(state, pool, [])
    observe(state, first['chapter'], True)
    assert status_of(state[first['chapter']]) == 'uncertain'
    second = pick_item(state, pool, [first['id']])
    assert second['chapter'] == first['chapter']
    observe(state, second['chapter'], True)
    assert status_of(state[1]) == 'tested_out'
    observe(state, 2, False)
    built = plan(state, overrides={1: 'review'})
    assert 1 not in built['skip'] and built['start'] == 1
    built = plan(state)
    assert built['skip'] == [1] and built['review'] == [2] and built['start'] == 2
    # a strong student still stops before the item cap
    state = blank(chapters)
    used = []
    while True:
        item, why = next_item(state, items, used, len(used), max_items=MAX_ITEMS, min_items=4)
        if item is None:
            break
        observe(state, item['chapter'], True)
        used.append(item['id'])
    assert why == 'confident' and len(used) < MAX_ITEMS
    assert plan(state)['skip'] == chapters


def test_ticket_grade_is_deterministic_and_rubric_based():
    assert len(TICKETS) >= 40
    courses = {t['course'] for t in TICKETS}
    assert courses == {'ITSUP', 'NETOPS', 'CLIENT', 'SEC'}
    import interactive_labs as labs
    for ticket in TICKETS:
        if ticket['lab_id']:
            assert ticket['lab_id'] in labs.LABS_BY_ID
        lines, _node = replay(ticket, [ticket['tree']['start']['asks'][0]['id']])
        assert lines == replay(ticket, [ticket['tree']['start']['asks'][0]['id']])[0]
        assert lines[0]['who'] == 'them' and lines[1]['who'] == 'you' and lines[2]['text']
    ticket = get_ticket('hd-it-01')
    note = 'Swapped the known-good adapter. The laptop powers on and the user confirmed it.'
    perfect = grade(ticket, priority='high', steps=['swap', 'confirm'], note=note, seconds=60)
    again = grade(ticket, priority='high', steps=['swap', 'confirm'], note=note, seconds=60)
    assert perfect == again and perfect['total'] == 100
    off = grade(ticket, priority='medium', steps=['swap', 'confirm'], note=note, seconds=60)
    assert off['triage'] == 10 and off['total'] == 85
    missed = grade(ticket, priority='low', steps=['reimage'], note='idk', seconds=9999)
    assert missed['triage'] == 0 and missed['steps'] < 20 and missed['time'] == 0 and missed['closing'] == 0
    assert set(PRIORITIES) == {'low', 'medium', 'high', 'critical'}


def _section(mod, code='ITSUP'):
    course = mod.Course.query.filter_by(code=code).first()
    section = mod.ClassSection.query.filter_by(course_id=course.id).order_by(mod.ClassSection.id).first()
    return course, section


def test_placement_route_stops_and_instructor_can_override(app, mod, student, instructor):
    with app.app_context():
        _course, section = _section(mod)
        sid = section.id
        student_row = mod.User.query.filter_by(email='student1@lms.local').first()
        uid = student_row.id
    url = f'/student/section/{sid}/placement'
    page = student.get(url).get_data(as_text=True)
    assert 'Skip What You Know' in page and 'Start' in page
    assert student.post(url, data={'action': 'start'}, follow_redirects=True).status_code == 200
    for _ in range(30):
        body = student.get(url).get_data(as_text=True)
        if 'Your plan' in body:
            break
        posted = student.post(url, data={'action': 'answer', 'choice': 'not-an-option'}, follow_redirects=True)
        assert posted.status_code == 200
    body = student.get(url).get_data(as_text=True)
    assert 'Your plan' in body and 'Where to start' in body and 'No chapter tested out' in body
    again = student.post(url, data={'action': 'start'}, follow_redirects=True).get_data(as_text=True)
    assert 'already took' in again
    staff = instructor.get(f'/instructor/section/{sid}/placement').get_data(as_text=True)
    assert 'Skip What You Know' in staff and 'Student1' in staff
    assert student.get(f'/instructor/section/{sid}/placement').status_code == 403
    saved = instructor.post(f'/instructor/section/{sid}/placement/{uid}', data={
        'action': 'save', 'note': 'Counts chapter 1 from a prior course.', 'kind-1': 'tested_out',
    }, follow_redirects=True)
    assert saved.status_code == 200
    plan = student.get(url).get_data(as_text=True)
    assert 'tested out' in plan and 'Chapter 1' in plan
    home = student.get('/student').get_data(as_text=True)
    assert 'tested out' in home
    reset = instructor.post(f'/instructor/section/{sid}/placement/{uid}', data={'action': 'reset'}, follow_redirects=True)
    assert reset.status_code == 200
    fresh = student.get(url).get_data(as_text=True)
    assert 'Start' in fresh and 'Your plan' not in fresh


def test_helpdesk_route_grades_and_lists_for_instructor(app, mod, student, instructor):
    with app.app_context():
        _course, section = _section(mod)
        sid = section.id
    queue = student.get(f'/student/section/{sid}/helpdesk').get_data(as_text=True)
    assert 'Help Desk Queue' in queue and 'Laptop will not power on' in queue
    url = f'/student/section/{sid}/helpdesk/hd-it-01'
    page = student.get(url).get_data(as_text=True)
    assert 'How urgent' in page
    assert 'Priya N..' not in page and 'Priya N.</strong>' in page
    student.post(url, data={'action': 'priority', 'priority': 'high'})
    asked = student.post(url, data={'action': 'ask', 'qid': 'brick'}, follow_redirects=True).get_data(as_text=True)
    assert 'brick stays dark' in asked
    student.post(url, data={'action': 'diagnose'})
    student.post(url, data={'action': 'step', 'step': 'swap'})
    student.post(url, data={'action': 'step', 'step': 'confirm'})
    student.post(url, data={'action': 'close'})
    note = 'Swapped the known-good adapter. The laptop powers on and the user confirmed it.'
    result = student.post(url, data={'action': 'resolve', 'note': note}, follow_redirects=True).get_data(as_text=True)
    assert '100 / 100' in result
    staff = instructor.get(f'/instructor/section/{sid}/helpdesk').get_data(as_text=True)
    assert 'Student1' in staff and '>1</td>' in staff and 'Average' in staff


def test_daily_review_route_sync_and_search(app, mod, student, instructor):
    with app.app_context():
        _course, section = _section(mod)
        sid = section.id
    home = student.get('/student').get_data(as_text=True)
    assert 'Daily Review ·' in home and 'due' in home
    assert 'Skip What You Know' in home and 'Help Desk Queue' in home
    from pathlib import Path
    import re
    page = student.get(f'/student/section/{sid}/daily-review')
    body = page.get_data(as_text=True)
    assert 'Daily Review' in body
    assert 'indexedDB' in Path('static/js/daily-review.js').read_text()
    sync = student.get(f'/student/section/{sid}/daily-review/sync').get_json()
    assert sync['due'] >= 1 and sync['session'] and 'answer' not in sync['session'][0]
    card_id = re.search(r'name="card_id" value="([^"]+)"', body).group(1)
    first = next(c for c in cards() if c['id'] == card_id)
    if first['kind'] == 'command':
        assert first['answer'] not in body
    posted = student.post(f'/student/section/{sid}/daily-review', data={'card_id': first['id'], 'answer': first['answer']},
                          follow_redirects=True)
    assert posted.status_code == 200
    staff = instructor.get(f'/instructor/section/{sid}/daily-review').get_data(as_text=True)
    assert 'Cards learned' in staff and 'Streak' in staff
    found = student.get('/api/search?q=help%20desk').get_json()
    assert any(r['title'] == 'Help Desk Queue' for r in found['results'])
    inst = instructor.get('/instructor').get_data(as_text=True)
    assert 'id="itab-practice"' in inst and 'Skip What You Know' in inst
    assert student.get(f'/instructor/section/{sid}/daily-review').status_code == 403
