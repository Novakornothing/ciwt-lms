"""Spaced retrieval memory model (pass 11): SM-2-style intervals with an explicit forgetting curve.

Model (per objective, pure and documented):
* Every graded answer on the objective is a retrieval. Answers on the same calendar day are one review;
  the day counts as recalled when at least 60% of that day's answers were right.
* SM-2 schedule: ease starts at 2.5. A recalled review grows the interval 1 day -> 3 days -> previous x ease
  and nudges ease up (+0.05, max 2.8); a lapse resets the interval to 1 day and lowers ease by 0.2 (min 1.3).
* Forgetting curve: predicted recall R(t) = 0.9 ** (t / interval), so the interval is the point where recall is
  predicted to fall to 90%. An objective is due when that moment is reached: just before predicted
  forgetting, not after. This is a prediction for scheduling only; it never changes an estimate or a grade.
"""
import math
from datetime import datetime, timedelta

EASE_START = 2.5
EASE_MIN = 1.3
EASE_MAX = 2.8
DAY_PASS = 0.6
FIRST, SECOND = 1.0, 3.0
TARGET_R = 0.9
RETRIEVAL_KINDS = ('test', 'testout', 'quiz', 'review_check', 'daily', 'inline')


def _day(when):
    return when.date() if isinstance(when, datetime) else None


def schedule(observations):
    """Replay answers into an SM-2 state. Returns None when the objective has never been answered."""
    days = {}
    for o in observations or []:
        if o.get('kind') not in RETRIEVAL_KINDS or not o.get('when'):
            continue
        d = days.setdefault(_day(o['when']), [0, 0, o['when']])
        d[0] += 1 if o.get('correct') else 0
        d[1] += 1
        d[2] = max(d[2], o['when'])
    if not days:
        return None
    ease, interval, reps, lapses, history = EASE_START, 0.0, 0, 0, []
    last = None
    for day in sorted(days):
        right, n, when = days[day]
        ok = right / n >= DAY_PASS
        if ok:
            reps += 1
            interval = FIRST if reps == 1 else SECOND if reps == 2 else round(interval * ease, 2)
            ease = min(EASE_MAX, ease + 0.05)
        else:
            lapses += 1
            reps = 0
            interval = FIRST
            ease = max(EASE_MIN, ease - 0.2)
        last = when
        history.append({'day': day.isoformat(), 'right': right, 'n': n, 'recalled': ok, 'interval': interval})
    due = last + timedelta(days=interval)
    return {'ease': round(ease, 2), 'interval': interval, 'reps': reps, 'lapses': lapses, 'last': last,
            'due': due, 'history': history}


def recall(state, now):
    """Predicted probability of recall now (0..1) under R(t) = 0.9 ** (t / interval)."""
    if not state:
        return None
    t = max(0.0, (now - state['last']).total_seconds() / 86400.0)
    return round(TARGET_R ** (t / max(state['interval'], 0.01)), 3)


def is_due(state, now):
    return bool(state) and now >= state['due']


def days_until_due(state, now):
    if not state:
        return None
    return math.ceil((state['due'] - now).total_seconds() / 86400.0)


def queue(states, now, minimum=5, maximum=10, eligible=None):
    """Objectives for today's review: every due one (most overdue first), topped up with the soonest-due
    ones to reach ``minimum`` when enough have been learned, capped at ``maximum``. Returns
    [(obj, state, reason)]."""
    learned = [(o, s) for o, s in states.items() if s and (eligible is None or o in eligible)]
    due = sorted([x for x in learned if is_due(x[1], now)], key=lambda x: recall(x[1], now))
    soon = sorted([x for x in learned if not is_due(x[1], now)], key=lambda x: x[1]['due'])
    out = [(o, s, 'due') for o, s in due[:maximum]]
    for o, s in soon:
        if len(out) >= minimum:
            break
        out.append((o, s, 'soon'))
    return out[:maximum]
