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

* Evidence, per section since the student last reset their profile: which alternative rungs (R1..R4) the student
  was shown AND responded to (answered its check, or asked for another way while on it), and which one resolved
  the section. Resolutions on the original (R0) are counted and shown but are not evidence for a rung type.
* Rates, not counts: R1 is always offered first, so it resolves the most sections even when it is not what helps
  (the synthetic simulation, tools/ladder_sim.py, showed a count rule picking "plain" for most learners). A kind's
  rate = sections it resolved / sections where it was shown and responded to.
* A best rung type is used only when ALL hold: at least PROFILE_MIN_RESOLVED (4) sections resolved by an
  alternative, from at least PROFILE_MIN_LESSONS (2) lessons; the best kind was responded to in at least
  PROFILE_MIN_SHOWN (3) sections and resolved at least PROFILE_MIN_BEST (3); its rate is at least
  PROFILE_MIN_RATE (60%); and it beats the rate of every other kind with at least PROFILE_MIN_SHOWN sections by
  at least PROFILE_MIN_RATE_LEAD (25 points). Ties are never broken by guessing: no best type.
"""
from collections import Counter

RUNGS = ('R1', 'R2', 'R3', 'R4')
KIND = {'R0': 'original', 'R1': 'plain', 'R2': 'analogy', 'R3': 'visual', 'R4': 'try'}
RUNG_OF_KIND = {v: k for k, v in KIND.items()}
KIND_LABEL = {'original': 'The original explanation', 'plain': 'Plain language', 'analogy': 'An analogy or story',
              'visual': 'A picture or step-by-step trace', 'try': 'Trying it hands-on'}
PROFILE_MIN_RESOLVED = 4
PROFILE_MIN_LESSONS = 2
PROFILE_MIN_SHOWN = 3
PROFILE_MIN_BEST = 3
PROFILE_MIN_RATE = 0.6
PROFILE_MIN_RATE_LEAD = 0.25
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


def profile(sections):
    """sections: [{'lesson': key, 'shown': rungs responded to, 'resolved': rung or None}] since the last reset.
    -> {'counts': {kind: resolved}, 'shown': {kind: n}, 'rates': {kind: rate}, 'original': n, 'alt': n,
        'lessons': n, 'best': kind | None, 'why': text}"""
    shown, counts = Counter(), Counter()
    alt_lessons, alt, original = set(), 0, 0
    for s in sections:
        r = s.get('resolved')
        for x in set(s.get('shown') or ()) | ({r} if r in RUNGS else set()):
            if x in RUNGS:
                shown[KIND[x]] += 1
        if r == 'R0':
            original += 1
        elif r in RUNGS:
            counts[KIND[r]] += 1
            alt += 1
            alt_lessons.add(s.get('lesson'))
    rates = {k: round(counts[k] / n, 3) for k, n in shown.items() if n}
    out = {'counts': dict(counts), 'shown': dict(shown), 'rates': rates, 'original': original, 'alt': alt,
           'lessons': len(alt_lessons), 'best': None}
    if alt < PROFILE_MIN_RESOLVED:
        out['why'] = f'Not enough evidence yet: {alt} of {PROFILE_MIN_RESOLVED} sections cleared by another explanation.'
        return out
    if len(alt_lessons) < PROFILE_MIN_LESSONS:
        out['why'] = f'Not enough evidence yet: all of it comes from one lesson (needs {PROFILE_MIN_LESSONS}).'
        return out
    known = {k: rates[k] for k in rates if shown[k] >= PROFILE_MIN_SHOWN}
    cands = sorted((k for k in known if counts[k] >= PROFILE_MIN_BEST), key=lambda k: (-known[k], k))
    if not cands:
        out['why'] = 'No clear pattern yet: no kind of explanation has been tried and has worked often enough.'
        return out
    best = cands[0]
    others = [v for k, v in known.items() if k != best]
    if known[best] < PROFILE_MIN_RATE or any(known[best] - v < PROFILE_MIN_RATE_LEAD for v in others):
        out['why'] = 'No clear pattern yet: no single kind of explanation has worked clearly more often than the others.'
        return out
    out['best'] = best
    out['why'] = (f'{KIND_LABEL[best]} cleared {counts[best]} of the {shown[best]} sections where you tried it '
                  f'({round(known[best] * 100)}%), clearly more than the other kinds, across {len(alt_lessons)} lessons.')
    return out
