"""Explanation ladder policy (pass 19). Pure functions, no database: the routes in mastery/ladder.py call these.

Progression, per student and per concept section:

* The student first sees the original section (R0), unless the class has "adapt first presentation" on AND the
  learner profile has a confident best rung type (see PROFILE_* below); then the first presentation is that rung,
  labelled, with "See the original" always one tap away.
* A micro-check sits after the section (no grade impact). A right answer marks the rung currently shown as the one
  that worked (``resolved``). A wrong answer, or "Explain it another way", replaces the section with the next rung
  the student has not seen yet. The order is R1 plain -> R2 analogy -> R3 visual / step by step -> R4 try it,
  cut to the class's max rungs and any per-section override; when the profile is confident, its best rung type
  moves to the front ("lead with what helps you").
* When no unseen rung is left and the student has not passed a check on this section, the section is
  ``exhausted``: the instructor sees it in Who needs me and the briefing. The student can still browse every rung.

Learner profile (conservative on purpose: a wrong lead costs the student a rung, a late lead costs nothing):

* Evidence = sections resolved on an alternative rung (R1..R4) since the student last reset their profile.
  Resolutions on the original (R0) are counted and shown but are not evidence for a rung type.
* A best rung type is used only when ALL hold: at least PROFILE_MIN_RESOLVED (4) alternative resolutions, from at
  least PROFILE_MIN_LESSONS (2) different lessons; the best type has at least PROFILE_MIN_BEST (3) of them and at
  least PROFILE_MIN_SHARE (50%) of them; and it leads the runner-up by at least PROFILE_MIN_LEAD (2).
  Ties are never broken by guessing: no best type.
"""
from collections import Counter

RUNGS = ('R1', 'R2', 'R3', 'R4')
KIND = {'R0': 'original', 'R1': 'plain', 'R2': 'analogy', 'R3': 'visual', 'R4': 'try'}
RUNG_OF_KIND = {v: k for k, v in KIND.items()}
KIND_LABEL = {'original': 'The original explanation', 'plain': 'Plain language', 'analogy': 'An analogy or story',
              'visual': 'A picture or step-by-step trace', 'try': 'Trying it hands-on'}
PROFILE_MIN_RESOLVED = 4
PROFILE_MIN_LESSONS = 2
PROFILE_MIN_BEST = 3
PROFILE_MIN_SHARE = 0.5
PROFILE_MIN_LEAD = 2
DEFAULT_MAX_RUNG = 4


def new_state():
    return {'current': 'R0', 'tried': ['R0'], 'resolved': None, 'misses': 0, 'requests': 0, 'exhausted': False}


def allowed_rungs(max_rung=DEFAULT_MAX_RUNG, override=None):
    """Rungs this class/section may use, in default order. override: {'off': bool, 'max': int} or None."""
    o = override or {}
    if o.get('off'):
        return []
    n = max(0, min(4, int(o.get('max') or max_rung or 0)))
    n = min(n, max(0, min(4, int(max_rung or 0))))
    return list(RUNGS[:n])


def order(allowed, best_kind=None):
    """Escalation order: the profile's best rung type first (when allowed), then the rest in default order."""
    best = RUNG_OF_KIND.get(best_kind)
    if best in allowed and best != 'R0':
        return [best] + [r for r in allowed if r != best]
    return list(allowed)


def first_presentation(allowed, best_kind=None, adapt_first=False):
    best = RUNG_OF_KIND.get(best_kind)
    if adapt_first and best in allowed and best != 'R0':
        return best
    return 'R0'


def start(allowed, best_kind=None, adapt_first=False):
    st = new_state()
    first = first_presentation(allowed, best_kind, adapt_first)
    if first != 'R0':
        st['current'] = first
        st['tried'] = [first]
        st['adapted'] = True
    return st


def next_rung(state, seq):
    for r in seq:
        if r not in state['tried']:
            return r
    return None


def _escalate(state, seq):
    st = dict(state, tried=list(state['tried']))
    nxt = next_rung(st, seq)
    if nxt:
        st['current'] = nxt
        st['tried'].append(nxt)
    elif not st['resolved']:
        st['exhausted'] = True
    return st, nxt


def after_answer(state, correct, seq):
    """(new state, rung now shown or None when nothing changed, event) for a micro-check answer on state['current']."""
    if correct:
        st = dict(state, tried=list(state['tried']), resolved=state['current'], exhausted=False)
        return st, None, 'resolved'
    st = dict(state, misses=state['misses'] + 1)
    st, nxt = _escalate(st, seq)
    return st, nxt, ('escalated' if nxt else ('exhausted' if st['exhausted'] else 'no_more'))


def after_request(state, seq):
    """'Explain it another way' / 'I don't get it' (or an accepted Helix offer): next unseen rung."""
    st = dict(state, requests=state['requests'] + 1)
    st, nxt = _escalate(st, seq)
    return st, nxt, ('escalated' if nxt else ('exhausted' if st['exhausted'] else 'no_more'))


def show(state, rung):
    """Browse a rung the student has already seen (or R0, the original). Never changes resolved/exhausted."""
    if rung != 'R0' and rung not in state['tried']:
        return state
    return dict(state, current=rung)


def profile(resolutions):
    """resolutions: [(lesson key, rung resolved)] since the last reset.
    -> {'counts': {kind: n}, 'original': n, 'alt': n, 'lessons': n, 'best': kind | None, 'why': text}"""
    alt = [(les, r) for les, r in resolutions if r in RUNGS]
    counts = Counter(KIND[r] for _l, r in alt)
    lessons = len({les for les, _r in alt})
    out = {'counts': dict(counts), 'original': sum(1 for _l, r in resolutions if r == 'R0'), 'alt': len(alt),
           'lessons': lessons, 'best': None}
    if len(alt) < PROFILE_MIN_RESOLVED:
        out['why'] = (f'Not enough evidence yet: {len(alt)} of {PROFILE_MIN_RESOLVED} sections resolved by another '
                      'explanation.')
        return out
    if lessons < PROFILE_MIN_LESSONS:
        out['why'] = f'Not enough evidence yet: all of it comes from one lesson (needs {PROFILE_MIN_LESSONS}).'
        return out
    ranked = counts.most_common()
    best, n = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0
    if n < PROFILE_MIN_BEST or n / len(alt) < PROFILE_MIN_SHARE or n - second < PROFILE_MIN_LEAD:
        out['why'] = ('No clear pattern yet: no single kind of explanation has worked clearly more often than the '
                      'others.')
        return out
    out['best'] = best
    out['why'] = (f'{KIND_LABEL[best]} resolved {n} of the {len(alt)} sections where another explanation helped, '
                  f'across {lessons} lessons.')
    return out
