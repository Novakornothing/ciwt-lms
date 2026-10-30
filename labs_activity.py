"""Step graders for interactive (non-terminal) labs and for checkpoint questions inside terminal/GUI labs.

A lab may carry ``steps``: each step has an ``id``, a ``type`` and the ``objective`` it earns. Answers are
graded here, on the server; the page only ever receives :func:`public_step` (no keys, no rules).

Types
  choice  single or multiple choice, with per-option feedback
  order   put items in sequence (drag on desktop and touch, or move buttons / keyboard)
  match   drop each item on the right target (drag, tap-tap, or keyboard)
  fields  short answers; values may be generated per student (``gen``) and are checked by a function
  config  a settings form (e.g. a SOHO router page) checked rule by rule
  build   pick one part per slot from a catalog; a function checks compatibility and requirements
"""
import ipaddress
import random
import re

# ------------------------------------------------------------------ generators (per-student values)


def _rng(seed, step_id):
    return random.Random(f'{seed}:{step_id}')


def gen_subnet(seed, step_id):
    """A random private network for subnet questions. Prefix /24-/29 inside 10/8, 172.16/12 or 192.168/16."""
    r = _rng(seed, step_id)
    prefix = r.choice([25, 26, 27, 28, 29, 26, 27])
    base = r.choice(['10', '172', '192'])
    if base == '10':
        a, b, c = 10, r.randint(0, 255), r.randint(0, 255)
    elif base == '172':
        a, b, c = 172, r.randint(16, 31), r.randint(0, 255)
    else:
        a, b, c = 192, 168, r.randint(0, 255)
    size = 2 ** (32 - prefix)
    host_off = r.randint(1, 254)
    net = ipaddress.ip_network(f'{a}.{b}.{c}.{host_off}/{prefix}', strict=False)
    hosts = list(net.hosts())
    ip = hosts[r.randint(0, len(hosts) - 1)]
    need = r.choice([12, 20, 28, 45, 50, 60, 100, 110, 200])
    return {'ip': str(ip), 'prefix': prefix, 'size': size, 'need': need}


def gen_hosts_needed(seed, step_id):
    r = _rng(seed, step_id)
    need = r.choice([5, 9, 14, 25, 30, 33, 50, 62, 70, 120])
    return {'need': need}


def gen_ticket(seed, step_id):
    """A case id and a host the learner must read back. Nothing here is a command."""
    r = _rng(seed, step_id)
    return {
        'case': 'SR-%d' % r.randint(2400, 8900),
        'host': r.choice(['files-03', 'mail-11', 'badge-02', 'pay-07']),
    }


GENERATORS = {'subnet': gen_subnet, 'hosts_needed': gen_hosts_needed, 'ticket': gen_ticket}

# ------------------------------------------------------------------ helpers


def norm(v):
    return re.sub(r'\s+', ' ', str(v if v is not None else '')).strip().lower()


def _ip(v):
    try:
        return ipaddress.ip_address(str(v).strip())
    except ValueError:
        return None


def mask_from_any(v):
    """Accept '255.255.255.192', '/26' or '26'. Returns prefix length or None."""
    s = str(v or '').strip().lstrip('/')
    if s.isdigit() and 0 <= int(s) <= 32:
        return int(s)
    try:
        return ipaddress.ip_network(f'0.0.0.0/{s}').prefixlen
    except ValueError:
        return None


def shuffled(seed, step_id, items):
    out = list(items)
    _rng(seed, step_id + ':shuffle').shuffle(out)
    if len(out) > 2 and out == list(items):       # never show the answer order
        out = out[1:] + out[:1]
    return out


# ------------------------------------------------------------------ public view


def public_step(step, state):
    seed = state.get('seed', 0)
    s = {k: step[k] for k in ('id', 'type', 'objective', 'title', 'prompt', 'multi', 'help', 'submit_label', 'scenario',
                              'image', 'note') if k in step}
    s['prompt'] = render_prompt(step, state)
    t = step['type']
    if t == 'choice':
        s['options'] = list(step['options'])
    elif t == 'order':
        s['items'] = shuffled(seed, step['id'], step['items'])
    elif t == 'match':
        s['targets'] = [{k: v for k, v in tg.items() if k in ('id', 'label', 'svg', 'sub')} for tg in step['targets']]
        s['items'] = shuffled(seed, step['id'], [{k: v for k, v in it.items() if k in ('id', 'label', 'svg', 'sub')}
                                                  for it in step['items']])
    elif t == 'fields':
        s['fields'] = [{k: v for k, v in f.items() if k in ('name', 'label', 'placeholder', 'inputmode', 'size', 'multiline')}
                       for f in step['fields']]
    elif t == 'config':
        s['fields'] = [{k: v for k, v in f.items() if k in ('name', 'label', 'kind', 'options', 'default', 'help', 'group')}
                       for f in step['fields']]
    elif t == 'build':
        s['slots'] = [{'name': sl['name'], 'label': sl['label'],
                       'options': [{k: v for k, v in o.items() if k in ('id', 'label', 'specs', 'price')} for o in sl['options']]}
                      for sl in step['slots']]
        s['budget'] = step.get('budget')
    saved = (state.get('answers') or {}).get(step['id'])
    if saved is not None:
        s['saved'] = saved
    fb = (state.get('feedback') or {}).get(step['id'])
    if fb is not None:
        s['last'] = fb
    return s


def render_prompt(step, state):
    vals = (state.get('gen') or {}).get(step['id']) or {}
    try:
        return (step.get('prompt') or '').format(**vals)
    except (KeyError, IndexError, ValueError):
        return step.get('prompt') or ''


def ensure_generated(steps, state):
    gen = state.setdefault('gen', {})
    for st in steps:
        g = st.get('gen')
        if g and st['id'] not in gen:
            gen[st['id']] = GENERATORS[g](state.get('seed', 0), st['id'])
    return state


# ------------------------------------------------------------------ graders


def grade(step, answer, state):
    """Returns dict(correct, message, per={key: bool}, detail=[...])."""
    t = step['type']
    fn = {'choice': _g_choice, 'order': _g_order, 'match': _g_match, 'fields': _g_fields,
          'config': _g_config, 'build': _g_build}[t]
    return fn(step, answer, state)


def _g_choice(step, answer, state):
    key = step['answer']
    if step.get('multi'):
        try:
            got = sorted({int(x) for x in (answer or [])})
        except (TypeError, ValueError):
            got = []
        want = sorted(key)
        ok = got == want
        per = {str(i): ((i in want) == (i in got)) for i in range(len(step['options']))}
        msgs = []
        expl = step.get('explain') or {}
        for i in got:
            if i not in want and str(i) in expl:
                msgs.append(expl[str(i)])
        if not ok and not msgs:
            missing = len([i for i in want if i not in got])
            extra = len([i for i in got if i not in want])
            msgs.append(f"Not yet: {missing} correct choice(s) missing, {extra} incorrect choice(s) selected.")
        return {'correct': ok, 'message': step.get('right', 'Correct.') if ok else ' '.join(msgs), 'per': per}
    try:
        got = int(answer)
    except (TypeError, ValueError):
        return {'correct': False, 'message': 'Choose an answer first.', 'per': {}}
    ok = got == key
    expl = step.get('explain') or {}
    msg = step.get('right', 'Correct.') if ok else expl.get(str(got), step.get('wrong', 'Not quite. Re-read the scenario and try again.'))
    return {'correct': ok, 'message': msg, 'per': {str(got): ok}}


def _g_order(step, answer, state):
    want = list(step['items'])
    got = [str(x) for x in (answer or [])]
    if sorted(got) != sorted(want):
        return {'correct': False, 'message': 'Place every item before checking.', 'per': {}}
    per = {it: (got[i] == want[i]) for i, it in enumerate(got)}
    right = sum(per.values())
    if right == len(want):
        return {'correct': True, 'message': step.get('right', 'Correct order.'), 'per': per}
    first_bad = next(i for i in range(len(want)) if got[i] != want[i])
    tip = (step.get('tips') or {}).get(want[first_bad]) or f"Position {first_bad + 1} is the first one out of place."
    return {'correct': False, 'message': f"{right} of {len(want)} in the right position. {tip}", 'per': per}


def _g_match(step, answer, state):
    answer = answer or {}
    want = {it['id']: it['answer'] for it in step['items']}
    per = {}
    for iid, tgt in want.items():
        got = answer.get(iid)
        per[iid] = (got == tgt) if not isinstance(tgt, (list, tuple)) else (got in tgt)
    unplaced = [i for i in want if not answer.get(i)]
    right = sum(per.values())
    if unplaced:
        return {'correct': False, 'message': f"Place all items first ({len(unplaced)} left). {right} placed correctly so far.", 'per': per}
    if right == len(want):
        return {'correct': True, 'message': step.get('right', 'All matched correctly.'), 'per': per}
    wrong = [it for it in step['items'] if not per[it['id']]]
    tip = wrong[0].get('tip') or ''
    return {'correct': False, 'message': f"{right} of {len(want)} correct. Items marked ✗ are on the wrong target. {tip}".strip(), 'per': per}


def _g_fields(step, answer, state):
    answer = answer or {}
    vals = (state.get('gen') or {}).get(step['id']) or {}
    per, msgs = {}, []
    for f in step['fields']:
        got = answer.get(f['name'], '')
        chk = f.get('check')
        if callable(chk):
            res = chk(got, vals, answer)
            ok, why = (res if isinstance(res, tuple) else (bool(res), ''))
        else:
            accept = [norm(a) for a in (f.get('accept') or [])]
            ok, why = norm(got) in accept, ''
        per[f['name']] = ok
        if not ok and str(got).strip():
            msgs.append(f"{f['label']}: {why or 'not correct yet.'}")
        elif not ok:
            msgs.append(f"{f['label']}: missing.")
    ok = all(per.values())
    return {'correct': ok, 'message': step.get('right', 'All correct.') if ok else ' '.join(msgs[:4]), 'per': per}


def _g_config(step, answer, state):
    answer = answer or {}
    per, msgs = {}, []
    for f in step['fields']:
        per[f['name']] = True
    for rule in step['rules']:
        fieldname, check, message = rule
        try:
            ok = bool(check(answer))
        except Exception:
            ok = False
        if not ok:
            per[fieldname] = False
            msgs.append(message)
    ok = not msgs
    return {'correct': ok, 'message': step.get('right', 'Configuration meets the policy.') if ok else ' '.join(msgs[:3]) +
            (f' (+{len(msgs) - 3} more)' if len(msgs) > 3 else ''), 'per': per, 'issues': len(msgs)}


def _g_build(step, answer, state):
    answer = answer or {}
    parts = {}
    for sl in step['slots']:
        oid = answer.get(sl['name'])
        opt = next((o for o in sl['options'] if o['id'] == oid), None)
        if opt is None:
            return {'correct': False, 'message': f"Choose a part for {sl['label']}.", 'per': {sl['name']: False}}
        parts[sl['name']] = opt
    issues = step['validate'](parts)          # list of (slot, message)
    per = {sl['name']: True for sl in step['slots']}
    for slot, _ in issues:
        per[slot] = False
    total = sum(p.get('price', 0) for p in parts.values())
    budget = step.get('budget')
    if budget and total > budget:
        issues.append(('_budget', f"Total ${total} is over the ${budget} budget."))
    ok = not issues
    msg = step.get('right', 'Compatible build that meets the requirements.') if ok else ' '.join(m for _, m in issues[:3])
    return {'correct': ok, 'message': msg + f" (Total ${total}.)", 'per': per, 'total': total}
