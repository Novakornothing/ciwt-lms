"""Per-objective mastery estimate: Bayesian Knowledge Tracing with weighted evidence (pass 11).

Pure functions, no Flask or database imports, so every number can be unit tested and explained.

The model
---------
Each objective has one hidden state, "mastered" or "not yet". ``p`` is the probability of
"mastered". It starts at ``p_init`` and is updated in time order by each piece of evidence:

1. **Item answers** (graded test, chapter check, review check, mastery check): Bayes' rule with a
   slip rate (a student who has mastered it still misses) and a guess rate (four options → 0.25)::

       correct: post = p(1-slip) / (p(1-slip) + (1-p)guess)
       wrong:   post = p*slip    / (p*slip    + (1-p)(1-guess))

   The update is *tempered* by the evidence weight ``w`` (``p ← p + w(post − p)``), so a practice
   question moves the estimate less than a graded test question. After each answer the standard BKT
   learning transition is applied (``p ← p + (1 − p)·learn·w``): answering is also practice.
2. **Lab outcomes** use the same rule with a low guess rate (a lab cannot be passed by guessing).
3. **Time on task** is a learning opportunity without an observation: reading a mapped lesson for at
   least half its estimated time applies one small learning transition (``read_learn``). It can only
   raise ``p``; too little time never lowers it (it is reported as a reason to offer a review).
4. **Helix reading signals are not an input.** They are used by the policy only to *offer* a review.

Confidence is the effective amount of evidence ``n_eff`` (sum of weights of answers and lab
outcomes): low < 2, medium < 6, high ≥ 6. Decisions that need evidence (inserting a review, calling
an objective mastered) check it, so one unlucky answer does not trigger anything on its own.
"""
from datetime import datetime

PARAMS = {
    'p_init': 0.30,    # prior: most objectives are new to most students
    'learn': 0.12,     # chance of moving to "mastered" at each practice opportunity
    'slip': 0.10,      # mastered but answered wrong
    'guess': 0.25,     # not mastered but answered right (four options)
    'lab_guess': 0.10,  # lab outcomes are hard to fake
    'read_learn': 0.05,  # learning credit for reading a mapped lesson for >= half its time
}

# Evidence weights (how much one observation counts). Graded and mastery-check items count fully.
WEIGHTS = {
    'test': 1.0,
    'testout': 1.0,
    'quiz': 0.8,
    'review_check': 0.6,
    'lab': 0.7,
}
KIND_LABEL = {
    'test': 'graded test question',
    'testout': 'mastery check question',
    'quiz': 'chapter check question',
    'review_check': 'review check question',
    'lab': 'lab outcome',
    'reading': 'lesson reading time',
}

MASTERED = 0.85     # p at or above → mastered (needs at least medium confidence)
LOW = 0.60          # p below → needs review (needs n_eff >= MIN_EVIDENCE)
MIN_EVIDENCE = 1.5  # weighted answers before the engine acts on a low estimate
CONF_MEDIUM = 2.0
CONF_HIGH = 6.0
READ_FULL = 0.5     # share of the lesson's estimated minutes that counts as "read"
READ_SHORT = 0.25   # under this share the reading time is reported as short

STATUS_LABEL = {
    'not_started': 'Not started',
    'developing': 'Developing',
    'review': 'Needs review',
    'mastered': 'Mastered',
    'waived': 'Waived',
}

_KIND_ORDER = {'reading': 0, 'lab': 1, 'quiz': 2, 'review_check': 3, 'test': 4, 'testout': 5}


def clamp(p, lo=0.001, hi=0.999):
    return max(lo, min(hi, p))


def bayes(p, correct, slip, guess):
    """Posterior P(mastered) after one right/wrong observation (BKT observation step)."""
    if correct:
        num, den = p * (1 - slip), p * (1 - slip) + (1 - p) * guess
    else:
        num, den = p * slip, p * slip + (1 - p) * (1 - guess)
    return num / den if den else p


def step(p, correct, weight=1.0, params=None, guess=None):
    """One weighted BKT update: tempered observation, then the learning transition."""
    P = params or PARAMS
    w = max(0.0, min(1.0, float(weight)))
    g = P['guess'] if guess is None else guess
    post = bayes(p, bool(correct), P['slip'], g)
    p1 = p + w * (post - p)
    p2 = p1 + (1 - p1) * P['learn'] * w
    return clamp(p2)


def read_step(p, params=None):
    P = params or PARAMS
    return clamp(p + (1 - p) * P['read_learn'])


def confidence(n_eff):
    if n_eff >= CONF_HIGH:
        return 'high'
    if n_eff >= CONF_MEDIUM:
        return 'medium'
    return 'low'


def _sort_key(o):
    when = o.get('when') or datetime.min
    return (when, _KIND_ORDER.get(o.get('kind'), 9), o.get('ref') or '')


def estimate(observations, params=None):
    """Run the model over one objective's evidence.

    observations: dicts with ``kind`` (test | quiz | review_check | testout | lab | reading),
    ``when`` (datetime), and for answers/labs ``correct`` (bool) and optional ``weight``; for
    reading ``seconds`` and ``expected`` (seconds) and ``lesson`` (label). Anything else (e.g. a
    Helix signal) is ignored on purpose.

    Returns p, n_eff, counts per kind, confidence, status and a step-by-step trace.
    """
    P = params or PARAMS
    p = P['p_init']
    n_eff = 0.0
    counts = {}
    trace = []
    read_lessons = set()
    short_reads = []
    for o in sorted(observations or [], key=_sort_key):
        kind = o.get('kind')
        if kind == 'reading':
            seconds, expected = float(o.get('seconds') or 0), float(o.get('expected') or 0)
            label = o.get('lesson') or ''
            share = (seconds / expected) if expected else 0.0
            if expected and share < READ_SHORT:
                short_reads.append({'lesson': label, 'seconds': int(seconds), 'expected': int(expected)})
            if expected and share >= READ_FULL and label not in read_lessons:
                read_lessons.add(label)
                before = p
                p = read_step(p, P)
                trace.append({'kind': kind, 'when': o.get('when'), 'before': before, 'after': p, 'ref': label})
            continue
        if kind not in WEIGHTS:
            continue                      # unknown kinds (and Helix) never move the estimate
        w = float(o.get('weight', WEIGHTS[kind]))
        before = p
        p = step(p, o.get('correct'), w, P, guess=P['lab_guess'] if kind == 'lab' else None)
        n_eff += w
        c = counts.setdefault(kind, {'n': 0, 'correct': 0})
        c['n'] += 1
        c['correct'] += 1 if o.get('correct') else 0
        trace.append({'kind': kind, 'when': o.get('when'), 'correct': bool(o.get('correct')), 'weight': w,
                      'before': before, 'after': p, 'ref': o.get('ref') or '', 'source': o.get('source') or ''})
    n_items = sum(c['n'] for k, c in counts.items() if k != 'lab')
    n_correct = sum(c['correct'] for k, c in counts.items() if k != 'lab')
    conf = confidence(n_eff)
    return {
        'p': round(p, 4),
        'pct': int(round(p * 100)),
        'n_eff': round(n_eff, 2),
        'n_items': n_items,
        'n_correct': n_correct,
        'counts': counts,
        'confidence': conf,
        'status': status_for(p, n_eff, any_evidence=bool(counts) or bool(read_lessons)),
        'read_lessons': sorted(read_lessons),
        'short_reads': short_reads,
        'trace': trace,
        'last_when': max([t['when'] for t in trace if t.get('when')] or [None]) if trace else None,
    }


def status_for(p, n_eff, any_evidence=True):
    if not any_evidence or n_eff <= 0:
        return 'not_started'
    if p >= MASTERED and n_eff >= CONF_MEDIUM:
        return 'mastered'
    if p < LOW and n_eff >= MIN_EVIDENCE:
        return 'review'
    return 'developing'


def describe_counts(est):
    """Plain-language evidence summary, e.g. '3 of 5 questions right (chapter check 1/2, graded test 2/3)'."""
    parts = []
    for kind in ('test', 'quiz', 'review_check', 'testout'):
        c = est['counts'].get(kind)
        if c:
            parts.append(f"{KIND_LABEL[kind]}s {c['correct']}/{c['n']}")
    lab = est['counts'].get('lab')
    head = (f"{est['n_correct']} of {est['n_items']} questions right" if est['n_items'] else 'No questions answered yet')
    if lab:
        head += f"; {lab['correct']} of {lab['n']} lab outcomes passed"
    return head + (f" ({', '.join(parts)})" if parts else '')
