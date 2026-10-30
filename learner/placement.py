"""Adaptive placement for Skip What You Know.

Chapter-level Bayesian Knowledge Tracing via ``mastery.model.step``. Pure functions:
no Flask and no database. The next item is the unused question in the least-decided
chapter (binary entropy, then fewer answers, then chapter number). A chapter is
tested out only after enough evidence that the estimate is high. One lucky correct
answer cannot skip a chapter. The test stops early once every chapter is decided,
and always stops at the item cap (about 20 minutes).
"""
import math

from mastery import model as M

SKIP_P = M.MASTERED
SKIP_N = M.CONF_MEDIUM
REVIEW_P = M.LOW
REVIEW_N = 1.0
MAX_ITEMS = 24
MIN_ITEMS = 6
SECONDS_PER_ITEM = 50
WEIGHT = M.WEIGHTS['test']


def entropy(p):
    p = min(max(float(p), 1e-6), 1.0 - 1e-6)
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def blank(chapters):
    return {int(ch): {'p': M.PARAMS['p_init'], 'n_eff': 0.0, 'n': 0, 'correct': 0} for ch in chapters}


def observe(state, chapter, correct, weight=WEIGHT):
    s = state[int(chapter)]
    w = float(weight)
    s['p'] = M.step(s['p'], bool(correct), w)
    s['n_eff'] = round(s['n_eff'] + w, 4)
    s['n'] += 1
    s['correct'] += 1 if correct else 0
    return state


def status_of(row):
    """tested_out, review, uncertain, or untested."""
    if row['n_eff'] >= SKIP_N and row['p'] >= SKIP_P:
        return 'tested_out'
    if row['n_eff'] >= REVIEW_N and row['p'] < REVIEW_P:
        return 'review'
    if row['n_eff'] >= SKIP_N:
        return 'review'
    if row['n'] == 0:
        return 'untested'
    return 'uncertain'


def decided(row):
    return status_of(row) in ('tested_out', 'review')


def pick_item(state, items, used, allow_decided=False):
    """Next item, or None. Deterministic."""
    used = set(used or [])
    by_ch = {}
    for it in items:
        if it['id'] in used or it['chapter'] not in state:
            continue
        by_ch.setdefault(it['chapter'], []).append(it)
    candidates = [ch for ch, row in state.items() if by_ch.get(ch) and (allow_decided or not decided(row))]
    if not candidates:
        return None
    chapter = sorted(candidates, key=lambda c: (-entropy(state[c]['p']), state[c]['n'], c))[0]
    return sorted(by_ch[chapter], key=lambda it: it['id'])[0]


def should_stop(state, n_asked, max_items=MAX_ITEMS, min_items=MIN_ITEMS):
    if n_asked >= max_items:
        return True, 'max_items'
    if state and all(decided(row) for row in state.values()) and n_asked >= min_items:
        return True, 'confident'
    return False, ''


def next_item(state, items, used, n_asked, max_items=MAX_ITEMS, min_items=MIN_ITEMS):
    """(item or None, stop_reason). Padding items fill up to min_items after a confident stop would be early."""
    stop, why = should_stop(state, n_asked, max_items, min_items)
    if stop:
        return None, why
    allow = bool(state) and all(decided(row) for row in state.values())
    item = pick_item(state, items, used, allow_decided=allow)
    if item is None:
        return None, 'no_items'
    return item, ''


def plan(state, overrides=None):
    """Personalized plan. Instructor overrides replace the placement status for that chapter."""
    overrides = overrides or {}
    rows = []
    for chapter in sorted(state):
        row = state[chapter]
        base = status_of(row)
        ov = overrides.get(chapter)
        if ov is None:
            ov = overrides.get(str(chapter))
        if ov in ('tested_out', 'review'):
            status, source = ov, 'instructor'
        else:
            status, source = base, 'placement'
        rows.append({
            'chapter': chapter,
            'status': status,
            'base': base,
            'source': source,
            'p': round(row['p'], 4),
            'pct': int(round(row['p'] * 100)),
            'n_eff': row['n_eff'],
            'n': row['n'],
            'correct': row['correct'],
        })
    skip = [r['chapter'] for r in rows if r['status'] == 'tested_out']
    review = [r['chapter'] for r in rows if r['status'] == 'review']
    start = next((r['chapter'] for r in rows if r['status'] != 'tested_out'), None)
    return {'skip': skip, 'review': review, 'start': start, 'rows': rows}


def minutes_for(n_items):
    return max(1, round(n_items * SECONDS_PER_ITEM / 60))
