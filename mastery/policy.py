"""Adaptive decisions from mastery estimates, instructor overrides and (optionally) Helix (pass 11).

Pure functions. The rules, in the order they are applied to each objective:

1. **Waive** (instructor, on the objective or its chapter): nothing is inserted; shown as "Waived".
2. **Force review** (instructor): a review is inserted and required until the student completes one
   after the override was set. It applies even when adaptivity is off for the class (it is a person's
   decision, not the engine's).
3. **Engine** (only when adaptivity is on for the class): an objective whose estimate is "Needs review"
   gets a short targeted review; if the student already completed one and it is still low, an
   *alternate explanation*; after two completed reviews it is not inserted again and the objective
   is flagged as **stuck** for the instructor. A skipped review is not re-inserted until new evidence
   arrives. Engine reviews are optional ("Skip for now") unless the instructor set **Lock**;
   **Unlock** keeps them optional and opens the mastery check for that chapter.
4. **Helix** (only with current consent, Helix on for the class, adaptivity on): when the engine has
   nothing to insert and the objective is not mastered, a skimmed or re-read section produces an
   *optional* review offer. Helix never makes anything required, never changes an estimate or a status,
   never counts toward "stuck" and never touches a grade. No Helix data means this rule simply does not fire.

Overrides on an objective win over overrides on its chapter (target ``CH-<n>``), which win over the engine.
Test-out (mastery check) offers are made per chapter: Unlock on the chapter offers it, Lock on the
chapter blocks it, otherwise the engine offers it to students who are strong so far.
"""
from datetime import datetime

from .model import STATUS_LABEL

OVERRIDE_KINDS = {
    'lock': 'Lock (review required, no mastery check)',
    'unlock': 'Unlock (no required review, mastery check open)',
    'force_review': 'Force review',
    'waive': 'Waive',
}
MAX_ENGINE_REVIEWS = 2
STRONG_MIN_OBJECTIVES = 3
STRONG_SHARE = 0.8
MAX_TESTOUT_ATTEMPTS = 3

_MIN = datetime.min


def chapter_key(ch):
    return f'CH-{ch}'


def effective_override(overrides, obj, chapter):
    """Objective-level override, else chapter-level, else None. Returns (kind, row, scope)."""
    ov = (overrides or {}).get(obj)
    if ov:
        return ov.get('kind'), ov, 'objective'
    ov = (overrides or {}).get(chapter_key(chapter))
    if ov:
        return ov.get('kind'), ov, 'chapter'
    return None, None, None


def evidence_reason(est, describe):
    if not est or est.get('status') == 'not_started':
        return 'There is no answer evidence on this objective yet.'
    return f"Your estimate is {est['pct']}% ({est['confidence']} confidence): {describe(est)}."


def decide_objective(obj, est, *, chapter, settings, overrides, history, helix, describe, obj_text=''):
    """Decision for one objective. Returns dict(state, label, action, override, stuck, notes)."""
    enabled = bool(settings.get('enabled'))
    h = history or {}
    done = int(h.get('reviews_done') or 0)
    last_review = h.get('last_review_at')
    skipped_at = h.get('skipped_at')
    kind, ov, scope = effective_override(overrides, obj, chapter)
    status = est['status'] if est else 'not_started'
    out = {'obj': obj, 'state': status, 'label': STATUS_LABEL.get(status, status), 'action': None,
           'override': kind, 'override_scope': scope, 'override_row': ov, 'stuck': False, 'notes': []}
    if kind == 'waive':
        out['state'], out['label'] = 'waived', STATUS_LABEL['waived']
        out['notes'].append('Your instructor waived this objective for you.')
        return out
    ev = evidence_reason(est, describe)
    if kind == 'force_review':
        satisfied = bool(last_review and ov.get('at') and last_review >= ov['at'])
        if not satisfied:
            out['action'] = {
                'type': 'alt_review' if done >= 1 else 'review', 'obj': obj, 'required': True,
                'source': 'instructor',
                'reasons': ['Your instructor asked you to review this objective before you move on.'
                            + (f" Note: “{ov.get('note')}”" if ov.get('note') else ''), ev],
            }
            return out
        out['notes'].append('You completed the review your instructor asked for.')
    if enabled and status == 'review':
        if done >= MAX_ENGINE_REVIEWS:
            out['stuck'] = True
            out['notes'].append('You have done two reviews on this objective. Your instructor can see that and '
                                'may suggest another way in; you can also message them.')
        elif skipped_at and skipped_at >= ((est or {}).get('last_when') or _MIN):
            out['notes'].append('You skipped the review for now. It comes back only if new answers show it would help.')
        else:
            alt = done >= 1
            reasons = [ev]
            if alt:
                reasons.insert(0, 'You already did one review and the estimate is still low, so this time the '
                                  'same objective is explained another way (plain-English summary, analogy and a worked example).')
            else:
                reasons.insert(0, 'Your recent answers on this objective suggest a short review will help before the next lesson.')
            for sr in (est or {}).get('short_reads') or []:
                reasons.append(f"Time on task: about {max(1, sr['seconds'] // 60)} min recorded on {sr['lesson']} "
                               f"(estimated {max(1, sr['expected'] // 60)} min). Short reading time never lowers your estimate.")
                break
            out['action'] = {'type': 'alt_review' if alt else 'review', 'obj': obj, 'required': kind == 'lock',
                             'source': 'engine', 'reasons': reasons}
            if kind == 'lock':
                out['action']['reasons'].append('Your instructor locked this objective, so the review is required.')
    if (out['action'] is None and enabled and helix and obj in helix and status not in ('mastered',)):
        sig = helix[obj]
        reasons = []
        if sig.get('skimmed'):
            reasons.append('Optional: the reading signal shows only a quick pass over “' + '”, “'.join(sig['skimmed'][:2]) + '”.')
        if sig.get('reread'):
            reasons.append('Optional: the reading signal shows you came back to “' + '”, “'.join(sig['reread'][:2]) + '” several times.')
        if reasons:
            reasons.append('This comes from Helix, which you turned on. It is not an assessment: it never changes '
                           'your estimate, never makes anything required and never affects a grade.')
            out['action'] = {'type': 'helix_offer', 'obj': obj, 'required': False, 'source': 'helix', 'reasons': reasons}
    return out


def strong_so_far(rows):
    worked = [r for r in rows if r['state'] not in ('not_started', 'waived')]
    mastered = [r for r in worked if r['state'] == 'mastered']
    review = [r for r in worked if r['state'] == 'review']
    ok = len(worked) >= STRONG_MIN_OBJECTIVES and not review and len(mastered) >= STRONG_SHARE * len(worked)
    return ok, len(mastered), len(worked)


def testout_offer(chapter, *, rows, settings, overrides, testout_history):
    """Offer a chapter mastery check? Returns dict(chapter, source, reasons) or None."""
    th = (testout_history or {}).get(chapter) or {}
    if th.get('passed'):
        return None
    ov = (overrides or {}).get(chapter_key(chapter))
    kind = ov.get('kind') if ov else None
    if kind == 'lock':
        return None
    if kind == 'unlock':
        return {'chapter': chapter, 'source': 'instructor',
                'reasons': ['Your instructor opened the mastery check for this chapter.']}
    if not (settings.get('enabled') and settings.get('testout')):
        return None
    if int(th.get('attempts') or 0) >= MAX_TESTOUT_ATTEMPTS:
        return None
    ok, m, n = strong_so_far(rows)
    if not ok:
        return None
    return {'chapter': chapter, 'source': 'engine',
            'reasons': [f'You have mastered {m} of the {n} objectives you have worked on so far, and none needs review.',
                        'If you pass the mastery check you can skip ahead; the lessons stay open if you want them.',
                        'The mastery check is never graded and does not change your gradebook.']}


def priority(action, est, chapter=0):
    """Required first, then reviews before optional Helix offers, earlier chapters first, lowest estimate first."""
    order = {'review': 1, 'alt_review': 1, 'helix_offer': 3}
    return (0 if action.get('required') else 1, order.get(action['type'], 5), chapter, (est or {}).get('p', 1))


def decide(states, *, chapters, settings, overrides=None, history=None, helix=None, describe=None,
           testout_history=None, upcoming=None):
    """All decisions for one student in one class.

    states: {obj: estimate}; chapters: {obj: chapter}; upcoming: chapter numbers the student has not
    started, in order (the first is offered a mastery check when the rules allow).
    """
    describe = describe or (lambda est: '')
    rows = {}
    for obj in chapters:
        rows[obj] = decide_objective(obj, states.get(obj), chapter=chapters[obj], settings=settings,
                                     overrides=overrides, history=(history or {}).get(obj), helix=helix,
                                     describe=describe)
    actions = [r['action'] for r in rows.values() if r['action']]
    actions.sort(key=lambda a: priority(a, states.get(a['obj']), chapters.get(a['obj'], 0)))
    offers = []
    for ch in upcoming or []:
        o = testout_offer(ch, rows=list(rows.values()), settings=settings, overrides=overrides,
                          testout_history=testout_history)
        if o:
            offers.append(o)
            break
    return {'rows': rows, 'actions': actions, 'testout': offers,
            'stuck': [o for o, r in rows.items() if r['stuck']]}


def gate(decision, chapter_of, lesson_chapter):
    """The action to show before a lesson in ``lesson_chapter``: reviews for objectives in this or an
    earlier chapter, required ones first. Returns the action or None."""
    for a in decision['actions']:
        if chapter_of.get(a['obj'], 0) <= lesson_chapter:
            return a
    return None


MC_REPEAT = 2   # the same misconception this many times (unresolved) earns an optional correction on its own


def apply_misconceptions(decision, misconceptions, *, settings, history=None, labels=None):
    """Turn reviews into targeted corrections where the student's wrong answers signal a known misconception.

    misconceptions: {mc_id: {'obj', 'hits', 'last_hit', 'resolved_at', 'active'}}; labels: {mc_id: label}.
    * an inserted review/alt review on an objective with an active misconception becomes a 'misconception'
      action (same required flag, same source), aimed at the most frequent one;
    * with adaptivity on, an unresolved misconception seen MC_REPEAT+ times on an objective with no other
      action gets an optional correction (respecting a skip made after the last hit).
    Pure: returns a new decision dict."""
    labels = labels or {}
    history = history or {}
    by_obj = {}
    for mc, m in (misconceptions or {}).items():
        if m.get('active'):
            by_obj.setdefault(m['obj'], []).append((m['hits'], m['last_hit'], mc))
    for v in by_obj.values():
        v.sort(key=lambda x: (x[0], x[1]), reverse=True)
    actions = []
    rows = {k: dict(r) for k, r in decision['rows'].items()}
    have = set()
    for a in decision['actions']:
        a = dict(a)
        cands = by_obj.get(a['obj'])
        if a['type'] in ('review', 'alt_review') and cands:
            hits, _last, mc = cands[0]
            a['type'], a['mc'] = 'misconception', mc
            a['reasons'] = ([f'Your answers suggest this mix-up: {labels.get(mc, mc)} (seen {hits} time{"s" if hits != 1 else ""}).',
                             'So this review goes straight at that idea instead of re-reading the whole lesson.'] + list(a['reasons']))
            rows[a['obj']]['action'] = a
        actions.append(a)
        have.add(a['obj'])
    if settings.get('enabled'):
        for obj, cands in by_obj.items():
            hits, last, mc = cands[0]
            row = rows.get(obj)
            if obj in have or not row or row['state'] in ('waived', 'mastered') or hits < MC_REPEAT:
                continue
            sk = (history.get(obj) or {}).get('skipped_at')
            if sk and last and sk >= last:
                continue
            a = {'type': 'misconception', 'obj': obj, 'mc': mc, 'required': False, 'source': 'engine',
                 'reasons': [f'Your answers suggest this mix-up: {labels.get(mc, mc)} (seen {hits} times).',
                             'A two-minute correction is offered. It is optional and never graded.']}
            rows[obj]['action'] = a
            actions.append(a)
    order = {'review': 1, 'alt_review': 1, 'misconception': 1, 'helix_offer': 3}
    actions.sort(key=lambda a: (0 if a.get('required') else 1, order.get(a['type'], 5)))
    return dict(decision, rows=rows, actions=actions)
