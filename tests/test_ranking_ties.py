"""Pass 14: Who-needs-me and briefing tie-breaks — severity (weak before mixed), then most recent struggle, then name."""
from datetime import datetime, timedelta
from types import SimpleNamespace as NS

from mastery import briefing as BR
from mastery import features as F


def _p(uid, first, last, kinds, sev, ago_h):
    return {'user': NS(id=uid, first_name=first, last_name=last, full_name=f'{first} {last}'), 'kinds': kinds,
            'severity': sev, 'struggle_at': (datetime(2026, 10, 1) - timedelta(hours=ago_h)) if ago_h is not None else None}


def test_more_reason_kinds_and_more_serious_kind_still_come_first():
    a = _p(1, 'Ann', 'Zed', ['misconception'], 9, 1)
    b = _p(2, 'Bob', 'Young', ['stuck', 'misconception'], 1, 50)
    c = _p(3, 'Cy', 'Xu', ['stuck'], 1, 50)
    assert [x['user'].id for x in sorted([a, c, b], key=F.need_rank)] == [2, 3, 1]


def test_ties_break_by_severity_then_recency_then_name():
    weak = _p(1, 'Zoe', 'Zimmer', ['misconception'], 7, 30)          # many objectives need review
    mixed = _p(2, 'Amy', 'Adams', ['misconception'], 2, 1)           # alphabetically first, recent, but less severe
    mixed_recent = _p(3, 'Ben', 'Brown', ['misconception'], 2, 0)    # same severity, more recent struggle
    mixed_name_b = _p(4, 'Cal', 'Clark', ['misconception'], 2, 5)
    mixed_name_a = _p(5, 'Al', 'Clark', ['misconception'], 2, 5)    # same severity and time: name (last, first)
    got = [x['user'].id for x in sorted([mixed, mixed_name_b, weak, mixed_name_a, mixed_recent], key=F.need_rank)]
    assert got == [1, 3, 2, 5, 4]


def test_no_struggle_time_sorts_after_a_known_one():
    a = _p(1, 'A', 'A', ['inactive'], 0, None)
    b = _p(2, 'B', 'B', ['inactive'], 0, 3)
    assert [x['user'].id for x in sorted([a, b], key=F.need_rank)] == [2, 1]


def test_briefing_todo_breaks_student_ties_by_needs_me_order_not_alphabet():
    # Equal scores: the student ranked higher in Who needs me (tie (0,)) wins over the alphabetically earlier one.
    cands = [{'kind': 'student', 'score': 2, 'title': 'Check in with Amy Adams', 'tie': (1,)},
             {'kind': 'student', 'score': 2, 'title': 'Check in with Zoe Zimmer', 'tie': (0,)},
             {'kind': 'objective', 'score': 2, 'title': 'Review IT-1.1 with the class'}]
    top = BR.rank_todo(cands)
    assert [t['title'] for t in top] == ['Check in with Zoe Zimmer', 'Review IT-1.1 with the class', 'Check in with Amy Adams']
    assert BR.rank_todo(list(reversed(cands))) == top


def test_live_needs_me_list_is_sorted_by_the_documented_key(app, mod):
    api = app.extensions['ciwt_mastery']
    with app.test_request_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        _cmap, _rows, people = api.features['needs_me'](sec)
        assert people, 'demo class has students who need attention'
        assert all('severity' in p and 'struggle_at' in p for p in people)
        assert [p['user'].id for p in people] == [p['user'].id for p in sorted(people, key=F.need_rank)]
        b = api.briefing['build'](sec)
        studs = [t for t in b['todo'] if t['kind'] == 'student']
        order = [p['user'].id for p in people]
        assert [t['user'].id for t in studs] == sorted([t['user'].id for t in studs], key=order.index)
