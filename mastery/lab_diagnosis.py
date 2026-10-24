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
        if _get(e, 'kind') == 'check' and a.startswith('vm probe') and ': "t"' in a:
            a = ''   # a check the probe watchdog stopped (slow device) is not the student repeating themselves (labs r5)
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
    return any(p['id'] in ('trial_and_error', 'repeats_without_change', 'skipped_step', 'hint_reliance', 'change_before_diagnose',
                           'wrong_fix_repeated', 'elevation_missed', 'repeated_failed_checks')
               for p in (result or {}).get('patterns', []))


# ---------------------------------------------------------------------------------------------------------------
# Pass 20: Dynamic Lab Process Analysis — a timeline of what the student actually did, a "why" diagnosis with a
# link to the lesson section / ladder rung that teaches the missed habit, and a class roll-up. Pure, no database.
# Lesson references are resolved to URLs by the caller (lab_progress.lesson_links). Pending SME review.
CHANGE_RE = re.compile(
    r'^\s*(sudo\s+)?(ip\s+(-\d\s+)?(addr|address|a|route|r|link|l)\s+(add|del|delete|set|change|replace|flush)\b|'
    r'ifconfig\s+\S+\s+(\d|up|down)|route\s+(add|del|delete|change)\b|netsh\s|set-|new-|remove-|enable-|disable-|restart-|'
    r'ipconfig\s+/(release|renew|flushdns|registerdns)|resolvectl\s+(flush|dns|domain)|systemd-resolve\s+--flush|'
    r'(service|rc-service)\s+\S+\s+(start|stop|restart)|systemctl\s+(start|stop|restart|enable|disable|reload)|'
    r'chmod|chown|chgrp|useradd|usermod|userdel|groupadd|passwd|apk\s+(add|del)|apt(-get)?\s+(install|remove)|'
    r'echo\s.*>|sed\s+-i|tee\s|vi\s|nano\s|udhcpc|dhclient|'
    r'conf(igure)?(\s+t(erminal)?)?\s*$|interface\s|no\s+shut|shutdown\s*$|ip\s+address\s+\d|switchport|vlan\s+\d|'
    r'hostname\s+\S|reg\s+add|net\s+user\s+\S+\s+\S|gpupdate|sfc\s|dism\s|bcdedit\s+/set)', re.I)
FLUSH_RE = re.compile(r'(ipconfig\s+/flushdns|resolvectl\s+flush-caches|systemd-resolve\s+--flush-caches|nscd\s+-i|clear-dnsclientcache)', re.I)
ELEV_RE = re.compile(r'(permission denied|access is denied|operation not permitted|requires elevation|run as administrator|'
                     r'must be root|are you root|not permitted|% invalid input detected|privileged exec|need to be root)', re.I)
ELEV_CMD_RE = re.compile(r'^\s*(sudo\b|su\b|doas\b|enable\s*$|runas\b|start-process\b.*-verb\s+runas)', re.I)
ROUTE_WORDS = re.compile(r'(route|gateway|default\s+gw|next[- ]hop)', re.I)
DNS_WORDS = re.compile(r'(dns|resolv|name\s+resolution|nslookup|drill)', re.I)
PHASES = ('diagnose', 'change', 'verify', 'rejected', 'hint', 'context')
PHASE_LABEL = {'diagnose': 'Looked / diagnosed', 'change': 'Changed something', 'verify': 'Checked the result',
               'rejected': 'Rejected or not recognised', 'hint': 'Hint', 'context': 'Other'}

# Pattern -> the lesson section and rung that teaches the habit (course, lesson label, section id, rung, concept).
LESSON_REFS = {
    'trial_and_error': ('ITSUP', '1.3', '2-facts-versus-guesses', 'R2', 'Work from facts, not guesses'),
    'repeats_without_change': ('ITSUP', '1.3', 'action-result-until-it-is-boring', 'R2', 'Action → result: change one thing, then re-test'),
    'never_verifies': ('ITSUP', '1.3', 'action-result-until-it-is-boring', 'R3', 'Verify every change with a checking command'),
    'skipped_step': ('ITSUP', '1.3', '1-anatomy-of-a-usable-ticket', 'R3', 'Work the steps in order'),
    'hint_reliance': ('ITSUP', '1.5', 'after-the-lab', 'R1', 'Try your own idea before the hint'),
    'change_before_diagnose': ('ITSUP', '1.3', '3-change-awareness', 'R3', 'Diagnose before you change anything'),
    'wrong_fix_repeated': ('ITSUP', '1.3', '2-facts-versus-guesses', 'R3', 'Test the hunch before repeating a fix'),
    'elevation_missed': ('ITSUP', '10.3', 'workstation-security-options-and-hardening', 'R1', 'Privilege: elevate only when a task needs it'),
    'repeated_failed_checks': ('ITSUP', '1.3', '4-note-quality-bar-for-the-lab', 'R1', 'Read why a check failed before re-submitting'),
    'verified_before_submit': None,
    'efficient': None,
}
STRENGTHS = ('efficient', 'verified_before_submit', 'diagnosed_first')


def _cmd(e):
    return re.sub(r'^\s*\[[^\]]{1,20}\]\s*', '', (_get(e, 'action') or '')).strip()


def phase_of(e, changed=False):
    k = _get(e, 'kind')
    if k == 'hint':
        return 'hint'
    if not is_action(e):
        return 'context'
    if is_rejected(e):
        return 'rejected'
    a = _cmd(e)
    if k in ('cmd', 'vm'):
        if CHANGE_RE.match(a):
            return 'change'
        if VERIFY_RE.match(a) or ELEV_CMD_RE.match(a) and VERIFY_RE.match(ELEV_CMD_RE.sub('', a).strip()):
            return 'verify' if changed else 'diagnose'
        return 'change' if _newly(e) else 'diagnose'
    if k == 'check':
        return 'verify'
    return 'change' if _newly(e) or _get(e, 'outcome') == 'progress' else 'diagnose'


def timeline(events):
    """Ordered steps with phase, seconds since the previous step, objectives earned, plus per-phase totals."""
    evs = sorted(list(events or []), key=lambda e: (_get(e, 'attempt', 1) or 1, _get(e, 'seq', 0) or 0))
    changed = False
    steps, totals, prev_at = [], {p: {'n': 0, 'seconds': 0} for p in PHASES}, None
    for e in evs:
        if _get(e, 'kind') == 'vm' and _cmd(e) == 'boot':
            continue
        ph = phase_of(e, changed)
        changed = changed or ph == 'change'
        at = _get(e, 'at')
        dt = int((at - prev_at).total_seconds()) if at and prev_at else 0
        dt = max(0, min(dt, 1800))           # a long pause (lunch, closed tab) is capped, not counted as work
        prev_at = at or prev_at
        totals[ph]['n'] += 1
        totals[ph]['seconds'] += dt
        steps.append({'seq': _get(e, 'seq'), 'kind': _get(e, 'kind'), 'action': (_get(e, 'action') or '')[:120],
                      'outcome': _get(e, 'outcome'), 'phase': ph, 'phase_label': PHASE_LABEL[ph], 'dt': dt,
                      'newly': _newly(e), 'detail': (_get(e, 'detail') or '')[:160]})
    return steps, totals


def _extra_patterns(evs, steps, lab):
    acts = [s for s in steps if s['phase'] not in ('context', 'hint')]
    out, objtext = [], ' '.join(o.get('text', '') for o in (lab or {}).get('objectives', []))
    cli = [s for s in acts if s['kind'] in ('cmd', 'vm')]
    first_change = next((s for s in cli if s['phase'] == 'change'), None)
    looked = [s for s in cli if s['phase'] == 'diagnose' and first_change and (s['seq'] or 0) < (first_change['seq'] or 0)]
    if first_change and not looked:
        out.append({'id': 'change_before_diagnose', 'label': 'Changed configuration before running any diagnostic command',
                    'evidence': [f'The first command, step {first_change["seq"]} (“{first_change["action"][:50]}”), changed something; '
                                 'no read-only command (ip a, ipconfig, show, cat, ping…) came before it.'],
                    'tip': 'Look first: read the current state and write down what is wrong before you change anything.'})
    elif first_change and looked:
        out.append({'id': 'diagnosed_first', 'label': 'Diagnosed before changing',
                    'evidence': [f'{len(looked)} read-only command(s) before the first change at step {first_change["seq"]}.'],
                    'tip': 'Good habit: keep reading the state before every change.'})
    flushes = [s for s in cli if FLUSH_RE.search(s['action']) and not s['newly']]
    if len(flushes) >= 2:
        ev = [f'DNS cache flushed {len(flushes)} times (steps {", ".join(str(s["seq"]) for s in flushes[:5])}) with no progress.']
        if ROUTE_WORDS.search(objtext) and not DNS_WORDS.search(objtext):
            ev.append('The fault in this lab is a routing / gateway problem, not name resolution.')
        out.append({'id': 'wrong_fix_repeated', 'label': 'Repeatedly flushed DNS when the fault was elsewhere', 'evidence': ev,
                    'tip': 'If a fix did not help once, test the next layer (ping the gateway by IP, check the route) instead of repeating it.'})
    denied = [s for s in acts if ELEV_RE.search(s['detail'] or '') or (s['outcome'] in ('error', 'wrong') and ELEV_RE.search(s['action']))]
    if denied:
        elevated_after = any(ELEV_CMD_RE.match(re.sub(r'^\s*\[[^\]]+\]\s*', '', s['action'])) and (s['seq'] or 0) > (denied[0]['seq'] or 0)
                             for s in acts)
        out.append({'id': 'elevation_missed', 'label': 'Skipped privilege elevation',
                    'evidence': [f'{len(denied)} command(s) refused for lack of privilege, first at step {denied[0]["seq"]} '
                                 f'(“{denied[0]["action"][:50]}”).'] + ([] if elevated_after else ['The student never elevated (sudo / enable / Run as administrator) afterwards.']),
                    'tip': 'Read “permission denied” as a signal: elevate for that one command (sudo, enable, admin prompt), then drop back.'})
    fails = [s for s in acts if s['kind'] == 'check' and s['outcome'] in ('wrong', 'error') and not s['newly']]
    run = best = 0
    for s in acts:
        if s['kind'] == 'check':
            run = run + 1 if s['outcome'] in ('wrong', 'error') and not s['newly'] else 0
            best = max(best, run)
        elif s['phase'] == 'change':
            run = 0
    if best >= 3:
        out.append({'id': 'repeated_failed_checks', 'label': 'Re-submitted failing checks without changing anything',
                    'evidence': [f'{len(fails)} failed checks; {best} in a row with no change in between.'],
                    'tip': 'Read what the failed check says is missing, change one thing, then check again.'})
    complete = next((s for s in steps if s['kind'] == 'complete'), None)
    if complete:
        changes = [s for s in acts if s['phase'] == 'change' and (s['seq'] or 0) < (complete['seq'] or 0)]
        if changes and any(s['phase'] == 'verify' and s['kind'] != 'check' and (s['seq'] or 0) > (changes[-1]['seq'] or 0)
                           and (s['seq'] or 0) < (complete['seq'] or 0) for s in acts):
            out.append({'id': 'verified_before_submit', 'label': 'Verified the fix before submitting',
                        'evidence': [f'A checking command followed the last change (step {changes[-1]["seq"]}) before the lab was completed.'],
                        'tip': 'Exactly the habit tickets need: action → result.'})
    return out


def analyze(events, lab=None):
    """diagnose() plus the dynamic process analysis: timeline, phase times, why-diagnosis with lesson refs."""
    res = diagnose(events, lab=lab)
    steps, totals = timeline(events)
    extra = _extra_patterns(events, steps, lab)
    have = {p['id'] for p in res['patterns']}
    pats = res['patterns'] + [p for p in extra if p['id'] not in have]
    if any(p['id'] not in STRENGTHS for p in pats):
        pats = [p for p in pats if p['id'] != 'efficient']
    for p in pats:
        p['strength'] = p['id'] in STRENGTHS
        ref = LESSON_REFS.get(p['id'])
        p['ref'] = ({'course': ref[0], 'label': ref[1], 'sid': ref[2], 'rung': ref[3], 'concept': ref[4]} if ref else None)
    pats.sort(key=lambda p: p['strength'])
    order = [s['phase'] for s in steps if s['phase'] in ('diagnose', 'change', 'verify')]
    seqline = []
    for ph in order:
        if not seqline or seqline[-1] != ph:
            seqline.append(ph)
    res.update(patterns=pats, timeline=steps, phases=totals, sequence=seqline,
               concerns=[p for p in pats if not p['strength']], strengths=[p for p in pats if p['strength']],
               minutes=round(sum(t['seconds'] for t in totals.values()) / 60, 1))
    return res


def class_summary(analyses):
    """Roll-up across students: how often each pattern appears, common rejected commands, phase-order habits."""
    from collections import Counter
    pat, rej, starts, n = Counter(), Counter(), Counter(), 0
    labels, refs = {}, {}
    for a in analyses or []:
        if not a:
            continue
        n += 1
        for p in a.get('patterns', []):
            pat[p['id']] += 1
            labels[p['id']] = p['label']
            refs[p['id']] = p.get('ref')
        for s in a.get('timeline', []):
            if s['phase'] == 'rejected' and s['action']:
                rej[re.sub(r'\s+', ' ', s['action'].strip().lower())[:40]] += 1
        seq = a.get('sequence') or []
        if seq:
            starts['Started by ' + PHASE_LABEL[seq[0]].lower()] += 1
    return {'students': n,
            'patterns': [{'id': k, 'label': labels[k], 'count': v, 'share': round(100 * v / n) if n else 0, 'ref': refs[k],
                          'strength': k in STRENGTHS} for k, v in pat.most_common()],
            'wrong_turns': [{'action': k, 'count': v} for k, v in rej.most_common(8)],
            'openings': [{'label': k, 'count': v} for k, v in starts.most_common()]}
