"""Lab process diagnosis (pass 11): how a student worked a lab, not only whether they finished.

Interface (pure, no database):

    diagnose(events, lab=None) -> {'attempt', 'patterns': [Pattern], 'summary': {...}}

``events`` is one attempt's ordered event list in the schema of ``lab_event`` on the ``labs`` branch
(lab_progress.LabEvent): dicts or objects with
    seq (int), at (datetime), kind ('cmd'|'event'|'check'|'hint'|'undo'|'reset'|'complete'|'vm'|'signoff'),
    action (str: the command / GUI event / step id), outcome ('ok'|'unknown'|'wrong'|'error'|'progress'|'repeat'),
    newly (JSON list or list of objective ids earned by this action, or None), score (float), detail (str).
``lab`` (optional) is the lab definition from interactive_labs: {'id', 'objectives': [{'id', 'text'}, ...]}.
Objective order in the definition is treated as the intended step order.

Each Pattern is {'id', 'label', 'evidence': [plain sentences citing seq numbers], 'tip'}. Patterns:
    trial_and_error   many unrecognised or rejected actions, or a run of them in a row
    repeats_without_change  the same action sent 3+ times in a row with no progress
    never_verifies    progress was made but no checking command followed the last change
    skipped_step      a later objective was earned while an earlier one never was
    hint_reliance     hints used for most objectives
    efficient         completed with few wasted actions, no hints and a verification at the end
How the live kinds map (pass 12, after the labs merge):
    cmd     simulated CLI command; ``unknown`` = not recognised (counts as rejected)
    event   GUI action (Windows 11 / activity labs); ``wrong``/``error`` count as rejected
    check   an answer check (guided labs: ``wrong`` = rejected answer) or, in real-VM labs, a ``vm probe``
            grading request: there ``wrong`` only means "not finished yet", so only ``error`` counts as rejected.
            A probe repeated with identical results and no progress is caught by repeats_without_change.
    vm      a command line the student typed into the real Linux VM. Its result is not graded per line,
            so it is never "rejected"; Linux read-only commands (ls, cat, stat, id, systemctl status, ...)
            count as verification. ``vm boot`` is not an action.
    hint (``ok`` = a counted hint, ``repeat`` = re-opened), undo, reset, complete and signoff are context, not actions.
Thresholds are constants below so they can be reviewed. Coaching tips are about process habits taught in
the course (verify after a change, change one thing at a time); they state no new technical facts.
"""
import json
import re

TRIAL_MIN = 4             # unrecognised/rejected actions needed for trial-and-error ...
TRIAL_SHARE = 0.4         # ... and at least this share of all actions,
TRIAL_RUN = 3             # or this many in a row
REPEAT_RUN = 3
HINT_SHARE = 0.5
EFFICIENT_SLACK = 3       # completed within objectives*2 + slack actions

VERIFY_RE = re.compile(
    r'^\s*(show|ping|tracert|traceroute|ipconfig|ifconfig|ip\s+(a|addr|route|r)\b|nslookup|dig|get-|test-|'
    r'gpresult|whoami|systeminfo|netstat|arp|route\s+print|display|cat|ls|dir|type|status|verify|'
    r'pathping|curl|wget|hostname|getmac|net\s+(user|share|use|localgroup)|sc\s+query|tasklist|'
    r'manage-bde\s+-status|bcdedit|chkdsk\s*$|'
    r'stat\b|id\b|getfacl|grep|head|tail|less|find|ps\b|df\b|du\b|uname|ss\b|systemctl\s+(status|is-)|journalctl|resolvectl)', re.I)
ACTION_KINDS = ('cmd', 'event', 'check', 'vm')


def _get(e, k, default=None):
    return e.get(k, default) if isinstance(e, dict) else getattr(e, k, default)


def _newly(e):
    v = _get(e, 'newly')
    if not v:
        return []
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except ValueError:
            return []
    return list(v or [])


def is_action(e):
    k = _get(e, 'kind')
    if k not in ACTION_KINDS:
        return False
    return not (k == 'vm' and (_get(e, 'action') or '').strip() == 'boot')


def is_rejected(e):
    o = _get(e, 'outcome')
    if _get(e, 'kind') == 'vm':
        return False
    if _get(e, 'kind') == 'check' and (_get(e, 'action') or '').startswith('vm probe'):
        return o == 'error'
    return o in ('unknown', 'wrong', 'error')


def is_verification(e):
    if _get(e, 'kind') == 'check':
        return False
    a = (_get(e, 'action') or '').strip()
    return bool(a) and bool(VERIFY_RE.match(a))


def diagnose(events, lab=None):
    evs = sorted(list(events or []), key=lambda e: (_get(e, 'attempt', 1) or 1, _get(e, 'seq', 0) or 0))
    acts = [e for e in evs if is_action(e)]
    bad = [e for e in acts if is_rejected(e)]
    hints = [e for e in evs if _get(e, 'kind') == 'hint' and _get(e, 'outcome') == 'ok']
    complete = next((e for e in evs if _get(e, 'kind') == 'complete'), None)
    earned, earned_at = [], {}
    for e in evs:
        for o in _newly(e):
            if o not in earned_at:
                earned_at[o] = _get(e, 'seq')
                earned.append(o)
    objs = [o['id'] for o in (lab or {}).get('objectives', [])] if lab else []
    patterns = []

    # trial and error
    run, best_run, run_start, best_start = 0, 0, None, None
    for e in acts:
        if is_rejected(e):
            run += 1
            run_start = run_start if run > 1 else _get(e, 'seq')
            if run > best_run:
                best_run, best_start = run, run_start
        else:
            run = 0
    if acts and ((len(bad) >= TRIAL_MIN and len(bad) / len(acts) >= TRIAL_SHARE) or best_run >= TRIAL_RUN):
        ev = [f'{len(bad)} of {len(acts)} actions were not recognised or were rejected.']
        if best_run >= TRIAL_RUN:
            ev.append(f'{best_run} in a row starting at step {best_start}.')
        sample = [(_get(e, 'action') or '')[:40] for e in bad[:3]]
        if sample:
            ev.append('For example: ' + '; '.join(f'“{s}”' for s in sample if s) + '.')
        patterns.append({'id': 'trial_and_error', 'label': 'Trial-and-error command guessing', 'evidence': ev,
                         'tip': 'Before typing, say what you expect the command to show. If it is rejected, read the '
                                'message and check the syntax in the lesson or with a hint instead of trying variations.'})

    # same action repeated without progress
    run, prev, start, worst = 0, None, None, (0, None, '')
    for e in acts:
        a = (_get(e, 'action') or '').strip().lower()
        if a and a == prev and not _newly(e):
            run += 1
        else:
            run, start = 1, _get(e, 'seq')
        prev = a
        if run > worst[0]:
            worst = (run, start, a)
    if worst[0] >= REPEAT_RUN:
        patterns.append({'id': 'repeats_without_change', 'label': 'Repeating the same action without changing anything',
                         'evidence': [f'“{worst[2][:40]}” was sent {worst[0]} times in a row from step {worst[1]} with no new progress.'],
                         'tip': 'If an action did not work, change one thing (a setting, a value, the order) and then test again.'})

    # never verifies after the last change
    progress = [e for e in evs if _newly(e) or _get(e, 'outcome') == 'progress']
    if progress and any(_get(e, 'kind') in ('cmd', 'vm') for e in acts):
        # the change is the last command typed at or before the last credited progress (in VM labs credit
        # arrives with the grader's probe, after the command that made the change)
        pseq = _get(progress[-1], 'seq') or 0
        changes = [e for e in acts if _get(e, 'kind') in ('cmd', 'vm') and (_get(e, 'seq') or 0) <= pseq
                   and not is_verification(e)]
        last_change = changes[-1] if changes else progress[-1]
        after = [e for e in acts if (_get(e, 'seq') or 0) > (_get(last_change, 'seq') or 0)]
        verified_ever = any(is_verification(e) for e in acts)
        if not any(is_verification(e) for e in after) and not is_verification(last_change):
            ev = [f'The last change was step {_get(last_change, "seq")} (“{(_get(last_change, "action") or "")[:40]}”) '
                  f'and no checking command (show, ping, ipconfig, Get-…) followed it.']
            if not verified_ever:
                ev.append('No checking command was used at any point in this attempt.')
            patterns.append({'id': 'never_verifies', 'label': 'Never verifies the result', 'evidence': ev,
                             'tip': 'After every change, run the command that proves it worked and read the output, '
                                    'the same “action → result” habit the tickets use.'})

    # skipped a required step (needs the lab definition)
    if objs:
        missing = [o for o in objs if o not in earned_at]
        later = [o for i, o in enumerate(objs) if o in earned_at and any(m in objs[:i] for m in missing)]
        if missing and later:
            names = {o['id']: o.get('text', o['id']) for o in lab['objectives']}
            patterns.append({'id': 'skipped_step', 'label': 'Skipped a required step',
                             'evidence': [f'Not done: {", ".join(names[m] for m in missing[:3])}.',
                                          f'Later step{"s" if len(later) > 1 else ""} done anyway: {", ".join(names[o] for o in later[:3])}.'],
                             'tip': 'Work the steps in order; later steps usually depend on the earlier ones being true.'})

    # hint reliance
    n_obj = len(objs) or len(earned) or 0
    if n_obj and len(hints) >= max(2, HINT_SHARE * n_obj):
        patterns.append({'id': 'hint_reliance', 'label': 'Relying on hints', 'evidence': [f'{len(hints)} hints for {n_obj} objectives.'],
                         'tip': 'Try one more idea of your own before each hint, then compare it with the hint.'})

    flagged = {p['id'] for p in patterns}
    if complete and not hints and not flagged and acts:
        budget = 2 * (n_obj or 1) + EFFICIENT_SLACK
        if len(acts) <= budget and len(bad) <= 1:
            patterns.append({'id': 'efficient', 'label': 'Efficient',
                             'evidence': [f'Completed in {len(acts)} actions for {n_obj or "the"} objectives, '
                                          f'{len(bad)} rejected, no hints.'],
                             'tip': 'Good process. Next time, try it without notes or explain each step to a partner.'})
    return {'attempt': _get(evs[0], 'attempt', 1) if evs else None, 'patterns': patterns,
            'summary': {'actions': len(acts), 'rejected': len(bad), 'hints': len(hints), 'earned': earned,
                        'completed': bool(complete)}}


def struggling(result):
    """True when a diagnosis shows a pattern an instructor may want to look at (used by 'Who needs me')."""
    return any(p['id'] in ('trial_and_error', 'repeats_without_change', 'skipped_step', 'hint_reliance')
               for p in (result or {}).get('patterns', []))
