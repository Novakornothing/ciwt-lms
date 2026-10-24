"""Authoring kit for the content-branch ladder files (NETOPS and ITSUP). Pending SME review.

Builders turn short, section-specific data into full R1-R4 ladders so every activity-style section (incident drills,
practice checklists, standards of work, capstones) gets its own concrete walk-through. Not a chapter module.
"""
import copy

from curriculum_v2.ladder.schema import analogy, check, order, plain, reveal, section, sort, tryit, visual

R = 'Pending SME review'


def C(q, key, wrong, why, mc):
    """Shorthand for schema.check with a misconception list aligned to the distractors."""
    return check(q, key, wrong, why, mc=mc)


def ol(steps):
    return '<ol class="ladder-trace">' + ''.join(f'<li>{s}</li>' for s in steps) + '</ol>'


def ul(items):
    return '<ul>' + ''.join(f'<li>{s}</li>' for s in items) + '</ul>'


def lad(heading, obj, src, d):
    """Generic ladder. d: r0, p, pc, a, ac, v (html or list of steps), vc, t, tc, w (widget), lab (id, note)."""
    v = d['v'] if isinstance(d['v'], str) else ol(d['v'])
    lab = {'id': d['lab'][0], 'note': d['lab'][1]} if d.get('lab') else None
    return section(heading, obj, [d['r0']],
                   plain(d['p'], src, [d['pc']]),
                   analogy(d['a'], d.get('asrc', src + ' (analogy written for this rung)'), [d['ac']]),
                   visual(v, src, [d['vc']]),
                   tryit(d['t'], src, [d['tc']], widget=d.get('w'), lab=lab))


def ops_mcs(code, obj, src):
    """Process misconceptions for one lesson (ids are unique per lesson code, e.g. 'NO21')."""
    m = {
        'NEG': ('Leaving passed (negative) test results out of the ticket because “nothing was found”',
                'A passed test rules something out; write it down so nobody repeats it.', ['negative result', 'ticket', 'evidence']),
        'PARALLEL': ('Making several untracked changes at once during a fault',
                     'One change at a time, each recorded with a time and a way back, so cause and effect stay clear.', ['change', 'rollback', 'one at a time']),
        'STATUS': ('Giving stakeholders a vague, alarming or over-promising status update',
                   'Say what is affected, since when, what is known, the next step and the next update time; never promise a fix time you do not control.', ['status', 'stakeholder', 'update']),
        'ESCALATE': ('Escalating with no evidence, or too late, or treating escalation as failure',
                     'Escalate on time with impact, tests run, results and access details.', ['escalate', 'evidence', 'time box']),
        'CHECKLIST': ('Writing a checklist of actions with no pass condition or failure note',
                      'Each step needs what “good” looks like and what you write if it fails.', ['checklist', 'pass', 'ticket note']),
        'RECALL': ('Studying definitions only, without the dependencies that explain failures',
                   'Know what the component needs upstream and what breaks downstream when it fails.', ['dependency', 'upstream', 'downstream']),
        'JARGON': ('Explaining the problem to a user in jargon, or blaming them',
                   'Use plain words about what they can and cannot do, what happens next and when.', ['user', 'plain language']),
    }
    return {f'MC-L-{code}-{k}': {'obj': obj, 'label': v[0], 'fix': v[1], 'terms': v[2], 'source': src, 'review': R}
            for k, v in m.items()}


def incident(heading, obj, src, code, title, d):
    """'Incident application' drill. d: case, steps [(time, test, result)], esc, status, ana, chk[5], lab."""
    m = lambda k: f'MC-L-{code}-{k}'
    p = (f'<p>This part is practice: you run one real-looking incident using what {title} taught. Here is a worked one.</p>'
         f'<p><strong>The case:</strong> {d["case"]}</p>'
         + ul(['<strong>Ordered tests</strong>: start with the test that rules out the most causes, then move up or down one step.',
               '<strong>Recorded results</strong>: write every result with its time, including tests that passed.',
               f'<strong>Escalation package</strong>: {d["esc"]}',
               f'<strong>At the 15-minute mark</strong>, tell people something calm and true: “{d["status"]}”']))
    v = ol([f'<strong>{t}</strong> {x} → <em>{r}</em>' for t, x, r in d['steps']]
           + ['<strong>+15 min</strong> Send the status sentence; if the time box is used up, hand over the package above.'])
    t = (f'<p>Put the tests for this case in the order you would run them. Then open the lab, reproduce the case, and write '
         f'your own timeline line by line plus one status sentence for the {d.get("who", "users")}.</p>')
    return section(heading, obj, [d['chk'][0]],
                   plain(p, src, [d['chk'][1]]),
                   analogy(d['ana'], src + ' (analogy written for this rung)', [d['chk'][2]]),
                   visual(v, src, [d['chk'][3]]),
                   tryit(t, src, [d['chk'][4]],
                         widget=order('Order the tests for this case', [x for _, x, _ in d['steps']],
                                      'Each test only makes sense once the one before it has passed or failed.'),
                         lab={'id': d['lab'][0], 'note': d['lab'][1]}))


def standard(heading, obj, src, code, title, d):
    """'Standard of work' (record negative results; no parallel untracked changes). d: neg, par, ana, good, bad, chk[5]."""
    p = (f'<p>Two habits keep {title} tickets trustworthy.</p>'
         + ul([f'<strong>Write down tests that passed.</strong> Example: {d["neg"]} That result rules a cause out, so the next person does not repeat it.',
               f'<strong>Change one thing at a time, and record it.</strong> Example of what not to do: {d["par"]} If it gets better or worse, nobody knows why.']))
    v = ol(d['trace'])
    t = '<p>Sort these ticket lines: which ones help the next technician, and which ones lose information or hide what changed?</p>'
    return section(heading, obj, [d['chk'][0]],
                   plain(p, src, [d['chk'][1]]),
                   analogy(d['ana'], src + ' (analogy written for this rung)', [d['chk'][2]]),
                   visual(v, src, [d['chk'][3]]),
                   tryit(t, src, [d['chk'][4]],
                         widget=sort('Helpful or harmful ticket line?', {'Helps the next technician': d['good'],
                                                                         'Loses information or hides a change': d['bad']},
                                     'Notice that “passed” results are just as useful as failures.')))


def practice(heading, obj, src, code, title, d):
    """'Practice standard' checklist. d: steps [(step, good, fail)], ana, chk[5], lab."""
    s1, s2 = d['steps'][0], d['steps'][1]
    p = (f'<p>The goal: explain {title} to a classmate without notes, then do the checks on a real or lab system.</p>'
         f'<p>Build a checklist of 5–9 steps. Each step has three parts:</p>'
         + ul(['<strong>the action</strong>,', '<strong>what “good” looks like</strong>,', '<strong>what you write in the ticket if it fails</strong>.'])
         + f'<p>Example first step: {s1[0]}. Good looks like: {s1[1]}. If not, write: “{s1[2]}”.</p>')
    v = ol([f'<strong>{a}</strong>. Good: {g}. If not, write: “{f}”' for a, g, f in d['steps']])
    t = '<p>Put these checklist steps into a sensible order, then try the whole list on the lab system and note any step you would change.</p>'
    return section(heading, obj, [d['chk'][0]],
                   plain(p, src, [d['chk'][1]]),
                   analogy(d['ana'], src + ' (analogy written for this rung)', [d['chk'][2]]),
                   visual(v, src, [d['chk'][3]]),
                   tryit(t, src, [d['chk'][4]],
                         widget=order('Order the checklist', [a for a, _, _ in d['steps']],
                                      'A good checklist goes from cheap, broad checks to narrow ones.'),
                         lab={'id': d['lab'][0], 'note': d['lab'][1]}))


def beyond(heading, obj, src, code, title, d):
    """'Beyond the quiz'. d: up, down, user, mist[2], esc, scen (symptom, [3 causes], disc, doc), ana, chk[5]."""
    sym, causes, disc, doc = d['scen']
    p = (f'<p>Quizzes only sample {title}. Real faults make more sense once you know the <strong>dependencies</strong>.</p>'
         + ul([f'<strong>Needs upstream:</strong> {d["up"]}', f'<strong>Breaks downstream when it fails:</strong> {d["down"]}',
               f'<strong>Say it to a user:</strong> “{d["user"]}”',
               f'<strong>Two common beginner mistakes:</strong> {d["mist"][0]}; {d["mist"][1]}.',
               f'<strong>Escalate instead of forcing it when:</strong> {d["esc"]}']))
    v = ol([f'<strong>Starting symptom:</strong> {sym}'] + [f'<strong>Possible cause {i}:</strong> {c}' for i, c in enumerate(causes, 1)]
           + [f'<strong>The check that tells them apart:</strong> {disc}', f'<strong>What you leave in the ticket:</strong> {doc}'])
    t = ('<p>Write your own scenario in the same shape: one symptom, three possible causes, and one check that separates them. '
         'Compare with the worked one below before you open it.</p>')
    return section(heading, obj, [d['chk'][0]],
                   plain(p, src, [d['chk'][1]]),
                   analogy(d['ana'], src + ' (analogy written for this rung)', [d['chk'][2]]),
                   visual(v, src, [d['chk'][3]]),
                   tryit(t, src, [d['chk'][4]], widget=reveal(f'Symptom: {sym} Which single check separates the three causes?', disc)))


def shared(entry):
    """A fresh copy of one shared ladder (for a signpost paragraph that is identical in several lessons)."""
    return copy.deepcopy(entry)
