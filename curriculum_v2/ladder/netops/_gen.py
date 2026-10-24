"""Lesson-data driven builders for NETOPS practice sections (pass 21). Pending SME review. Not a chapter module.

ops() turns one compact lesson record into full ladders for the four practice sections every NETOPS lesson carries
(Incident application, Standard of work, Practice standard, Beyond the quiz); cap() does the same for the four capstone
sections (The scenario, scaffolded checklist, Common beginner mistakes, Check your understanding). The facts in each
ladder come from the lesson record, so every lesson gets its own worked case, checklist and scenario.
"""
from curriculum_v2.ladder.netops._kit import C as _C, beyond, incident, lad, ops_mcs, practice, standard
from curriculum_v2.ladder.schema import order, reveal, sort

R = 'Pending SME review'


def C(q, k, w, why, mc):
    if len(why.split()) < 14:
        why += ' The other options skip the habit this section teaches.'
    return _C(q, k, w, why, mc)


def _m(code, k):
    return f'MC-L-{code}-{k}'


def ops(code, obj, title, src, d):
    """d keys: an (analogy name), ab (analogy point), case, steps [(t, test, result)] x3-4, esc, status, who, neg, par,
    good [2], bad [2], plist [(action, good, fail)] x5, up, down, user, mist [2], escw, scen (sym, [3], disc, doc), lab (id, note)."""
    m = lambda k: _m(code, k)
    s = d['steps']
    an, ab = d['an'], d['ab']
    inc = incident('Incident application', obj, src, code, title, {
        'case': d['case'], 'steps': s, 'esc': d['esc'], 'status': d['status'], 'who': d.get('who', 'users'), 'lab': d['lab'],
        'ana': (f'<p>Think of a ship’s log. The officer on watch writes the time, what was checked and what was found, even when the answer is '
                f'“all normal.” When the captain is woken at 3 a.m., the log tells her in one glance what has been ruled out and what is still '
                f'open. The lesson’s own picture for {title} is {an}: {ab}. Your incident timeline is the log for that picture, one line per test, '
                f'so the next person never has to repeat a check.</p>'),
        'chk': [
            C(f'In the {title} incident, which test comes first?', s[0][1],
              [s[-1][1] + ' (straight away)', 'Restart every affected device and see'],
              'The first test rules out the most causes cheaply; later tests only make sense once it has a result.', [m('PARALLEL'), m('PARALLEL')]),
            C('What goes in the escalation package?', 'Impact, tests, results, access',
              ['The user’s complaint, copied word for word', 'A guess at the cause and a plea to fix it'],
              'The next team needs impact, what you tested, what each test showed and how to reach the system.', [m('ESCALATE'), m('ESCALATE')]),
            C('In the ship’s-log story, why write “all normal” lines?', 'They rule things out',
              ['Logs must look busy to the captain', 'The law requires a line every hour'],
              'A passed check is evidence: it tells the next person what not to repeat.', [m('NEG'), m('NEG')]),
            C(f'After “{s[0][1]}” gives “{s[0][2]}”, what is next?', s[1][1],
              ['Escalate at once with no other evidence', 'Change two settings and test both together'],
              'Each line in the trace builds on the result of the line before it.', [m('ESCALATE'), m('PARALLEL')]),
            C('What do you send at the 15-minute mark?', 'A calm, true status',
              ['Nothing at all until it is fixed', 'A promised fix time to keep users happy'],
              'Say what is affected, what is known and when the next update comes; never promise a time you do not control.', [m('STATUS'), m('STATUS')]),
        ]})
    std = standard('Standard of work', obj, src, code, title, {
        'neg': d['neg'], 'par': d['par'], 'good': d['good'], 'bad': d['bad'],
        'trace': [f'Test: {s[0][1]} → {s[0][2]}. Write it, even if it passed.', f'Change one thing only, with the time and how to undo it.',
                  'Retest and write the new result next to the old one.', 'If nothing improved, undo the change before trying the next.',
                  'Hand over a ticket where every line is a test or a change.'],
        'ana': (f'<p>A cook adjusting a soup adds one ingredient, tastes, and notes it. Throw in salt, lemon and chilli at once and, if the soup '
                f'is ruined, nobody can say which one did it. Tasting and writing “still bland” is useful too, because it stops the next cook '
                f'adding the same thing again. For {title}, the lesson’s picture is {an} ({ab}); the same two habits keep that picture honest.</p>'),
        'chk': [
            C(f'On a {title} ticket, a test passed. Do you write it down?', 'Yes, it rules a cause out',
              ['No, only failures are worth writing', 'Only if the supervisor asks for it later'],
              'A passed test is a negative result that saves the next technician repeating it.', [m('NEG'), m('NEG')]),
            C('Why change one thing at a time?', 'To know what worked',
              ['Because changes are slow to type in', 'Because tools allow only one at once'],
              'With several untracked changes, nobody can tell which one helped or caused a new outage.', [m('PARALLEL'), m('PARALLEL')]),
            C('In the soup story, what is three spices at once?', 'Parallel changes',
              ['A careful single test', 'A recorded negative result'],
              'Adding everything at once hides which change made the difference.', [m('PARALLEL'), m('NEG')]),
            C('Nothing improved after a change. Next step in the trace?', 'Undo it first',
              ['Add a second change on top of it', 'Leave it and close the ticket now'],
              'Undo before the next attempt so changes do not pile up unrecorded.', [m('PARALLEL'), m('PARALLEL')]),
            C('Which ticket line helps the next technician?', d['good'][0],
              [d['bad'][0], d['bad'][1]],
              'Specific results and recorded changes help; vague or hidden changes lose information.', [m('NEG'), m('PARALLEL')]),
        ]})
    pl = d['plist']
    pra = practice('Practice standard for this lesson', obj, src, code, title, {
        'steps': pl, 'lab': d['lab'],
        'ana': (f'<p>Pilots fly with a checklist even after thousands of flights. Each line says what to check and what “normal” looks like, and '
                f'if a line fails the checklist says what to do next. Nobody calls that weakness: it is how tired people stay safe. Your '
                f'{title} checklist works the same way, and the lesson’s picture of {an} ({ab}) is the aircraft it is written for.</p>'),
        'chk': [
            C(f'A good {title} checklist step has…', 'Action, good, fail note',
              ['Only the action to perform, nothing else', 'A long paragraph of background theory'],
              'Each step needs the action, what good looks like and what you write if it fails.', [m('CHECKLIST'), m('RECALL')]),
            C('How many steps should the checklist have?', 'Five to nine',
              ['One step that covers everything at once', 'At least thirty, to be thorough'],
              'Five to nine steps is short enough to use on a live ticket and long enough to be useful.', [m('CHECKLIST'), m('CHECKLIST')]),
            C('In the pilot story, why use a checklist?', 'Tired people stay safe',
              ['Pilots forget how to fly', 'Airlines like extra paperwork'],
              'Checklists make the routine reliable under pressure.', [m('CHECKLIST'), m('CHECKLIST')]),
            C(f'What is the first step of the worked list?', pl[0][0],
              [pl[-1][0] + ' first', 'Write the closing note'],
              'Good checklists start with cheap, broad checks and narrow down.', [m('CHECKLIST'), m('CHECKLIST')]),
            C('What should you do after running the list in the lab?', 'Note steps to change',
              ['Throw the list away', 'Memorise it word for word'],
              'Testing the list on a lab system shows which steps need fixing.', [m('CHECKLIST'), m('RECALL')]),
        ]})
    sym, causes, disc, doc = d['scen']
    bey = beyond('Beyond the quiz', obj, src, code, title, {
        'up': d['up'], 'down': d['down'], 'user': d['user'], 'mist': d['mist'], 'esc': d['escw'], 'scen': d['scen'],
        'ana': (f'<p>A mechanic who only memorised part names would struggle with a car that will not start. A good one thinks in chains: the '
                f'starter needs the battery, the engine needs the starter, and if the battery is flat everything after it looks broken too. '
                f'For {title}, think of {an} ({ab}) and ask what each piece needs upstream and what stops downstream when it fails.</p>'),
        'chk': [
            C(f'What does {title} need upstream?', d['up'].rstrip('.'),
              ['Nothing; it works on its own', 'Only a faster computer'],
              'Knowing the upstream dependency explains why failures elsewhere show up here.', [m('RECALL'), m('RECALL')]),
            C('Which is a common beginner mistake here?', d['mist'][0],
              ['Writing passed tests in the ticket', 'Explaining in plain words'],
              'The lesson lists the mistakes new technicians make most often.', [m('RECALL'), m('JARGON')]),
            C('In the mechanic story, why think in chains?', 'Failures cascade',
              ['Parts have long names', 'Cars are all identical'],
              'One upstream failure makes everything after it look broken.', [m('RECALL'), m('RECALL')]),
            C('Which check separates the three causes?', disc.rstrip('.'),
              ['Restart and hope it clears', 'Ask the user to wait longer'],
              'A discriminating check gives a different result for each cause.', [m('RECALL'), m('ESCALATE')]),
            C('How do you explain this to a user?', 'Plain words, next step, when',
              ['Technical terms so they trust you', 'Tell them it is their fault'],
              'Users need plain language about impact, next steps and timing.', [m('JARGON'), m('JARGON')]),
        ]})
    return {'incident-application': inc, 'standard-of-work': std, 'practice-standard-for-this-lesson': pra, 'beyond-the-quiz': bey}


def mcs(code, obj, src):
    return ops_mcs(code, obj, src)


def cap(code, obj, src, d):
    """Capstone sections. d: title, scen (one line), why (what it trains), steps [5 tests], layer [5 labels], items [3+] (checklist),
    mist [(mistake, fix)] x2, lab (id, note), an (analogy name), ab."""
    from curriculum_v2.ladder.itsup._lk import P, Q, V
    m = lambda k: _m(code, k)
    st, it, mi = d['steps'], d['items'], d['mist']
    q = lambda *a: Q(*a)

    def X(h, qs, p, a, v, t, w):
        return lad(h, obj, src, {'r0': q(*qs[0]), 'p': p, 'pc': q(*qs[1]), 'a': a, 'ac': q(*qs[2]), 'v': V(v), 'vc': q(*qs[3]),
                                 't': t, 'tc': q(*qs[4]), 'w': w, 'lab': d['lab']})
    sc = X('The scenario', [
        ('What is the capstone ticket?', d['short'], 'A quiz on definitions with no ticket', 'A free choice of any topic you like',
         'The capstone is one concrete ticket that you work from first symptom to verified fix.', m('RECALL')),
        ('What is the first test in the worked order?', st[0], st[-1] + ' before anything else', 'Close the ticket and wait',
         'Start broad and cheap, then narrow down one step at a time.', m('PARALLEL')),
        ('In the story, what is the first move?', 'Scope it', 'Fix the loudest part', 'Replace everything',
         f'Like {d["an"]}, you size the problem before acting on it.', m('PARALLEL')),
        ('Which test comes after the first one?', st[1], 'Escalate with no evidence at all', st[-1] + ' straight away',
         'Each test depends on the one before it.', m('ESCALATE')),
        ('What proves the ticket is done?', 'User verification', 'Green lights on one switch', 'A quiet helpdesk queue',
         'The fix is done when the affected user confirms it works.', m('STATUS')),
    ],
        P(f'The capstone gives you one realistic ticket: {d["scen"]} {d["why"]} You work it like a real shift: scope first, then tests in order, '
          f'one change at a time, a calm status update and a check with the user at the end.'),
        P(f'Think of {d["an"]}: {d["ab"]}. Nobody arriving at that scene starts by changing things at random. They look at how big the '
          f'problem is, decide what to check first, and tell people what is happening. The capstone ticket asks you to show exactly that '
          f'behaviour, step by step, with notes someone else could follow.'),
        [f'{a} <em>({b})</em>' for a, b in zip(st, d['layer'])],
        '<p>Put the tests for this capstone in the order you would run them, then work the ticket in the lab.</p>',
        order('Capstone order', st, 'Broad and cheap first, narrow and costly last.'))
    ck = X('Your turn — scaffolded checklist', [
        ('What must every checklist line have?', 'A written result', 'A coloured highlight for style', 'A signature from the user',
         'Each line is filled in with what you saw, so nothing is skipped silently.', m('CHECKLIST')),
        (f'Which line is on this capstone’s checklist?', it[0], 'Reboot everything to save time', 'Skip lines that seem obvious',
         'The scaffold lists exactly what a reviewer looks for.', m('CHECKLIST')),
        ('In the form story, why not skip a box?', 'Gaps hide problems', 'Forms are too long', 'Boxes are optional',
         'An empty box looks the same as a check you forgot.', m('CHECKLIST')),
        ('Which item comes last in the scaffold?', it[-1], it[0] + ' (repeat it)', 'Nothing; stop early',
         'The checklist ends with the evidence or verification the reviewer needs.', m('CHECKLIST')),
        ('Where do you fill the checklist in?', 'Paper or ticket notes', 'Only in your head', 'On the user’s screen',
         'Write it down, on paper or in the ticket.', m('CHECKLIST')),
    ],
        P(f'The checklist is the shape of a good answer to this capstone. Fill in every line, on paper or in the ticket notes, and do not skip any: '
          + '; '.join(it) + '. A line you cannot fill in is itself a finding; write what stopped you.'),
        P('A pre-flight form has a box for every check. A pilot who leaves one blank has not proved the check was done, even if it was. An '
          'inspector reading the form cannot tell a skipped check from a forgotten one. Your checklist is that form: every box filled, even '
          'when the answer is “not reachable” or “no access, escalated.”'),
        it + ['Read it back: could a colleague act on it?'],
        '<p>Sort each line into whether it belongs on the checklist.</p>',
        sort('On the checklist?', {'Belongs': it[:3], 'Does not belong': ['Reboot everything first', 'Guess the cause']},
             'Every line asks for evidence, not action.'))
    bm = X('Common beginner mistakes', [
        ('Which is a common beginner mistake here?', mi[0][0], 'Recording each test with its result', 'Checking scope before acting',
         'The capstone lists the mistakes new technicians make most often.', m('PARALLEL')),
        ('What fixes that mistake?', mi[0][1], 'Doing the same thing faster', 'Asking the user to restart',
         'Each mistake has a habit that prevents it.', m('PARALLEL')),
        ('In the story, what is the mistake like?', 'Acting before looking', 'Writing too many notes', 'Being too calm',
         'Beginners act before gathering evidence.', m('RECALL')),
        ('What is the second mistake listed?', mi[1][0], 'Writing passed tests down', 'Telling users the next update time',
         'Both mistakes skip evidence or verification.', m('ESCALATE')),
        ('What prevents the second mistake?', mi[1][1], 'Hoping it does not happen', 'Working faster',
         'The fix is a habit you can check on every ticket.', m('RECALL')),
    ],
        P(f'Two mistakes catch beginners on this capstone. First: {mi[0][0].lower()}; instead, {mi[0][1].lower()}. Second: {mi[1][0].lower()}; '
          f'instead, {mi[1][1].lower()}. Both come from acting before the evidence is in, and both are easy to spot in a ticket review.'),
        P('A new driver who hears a noise and immediately pulls over, jumps out and starts unscrewing the wheel has acted before looking. An '
          'experienced driver listens, checks the mirrors, notes when the noise happens and then decides. The capstone mistakes are the first '
          'driver’s habits; the fixes are the second driver’s.'),
        [f'Mistake: {a} → Habit: {b}' for a, b in mi] + ['Check your own ticket for both before you submit it.'],
        '<p>Sort each habit.</p>',
        sort('Mistake or habit?', {'Mistake': [mi[0][0], mi[1][0]], 'Habit': [mi[0][1], mi[1][1]]}, 'Every mistake has a matching habit.'))
    cu = X('Check your understanding', [
        ('How long should your explanation to a peer take?', 'Under two minutes', 'As long as it takes, an hour or more', 'No explanation; just the ticket number',
         'A short, ordered explanation proves you understood the ticket.', m('JARGON')),
        ('What four things does it cover?', 'Symptom, checks, cause, verify', 'Only the fix you applied', 'Your opinion of the user',
         'Symptom, first three checks, what proved the cause, how you verified.', m('RECALL')),
        ('In the story, why explain it aloud?', 'Gaps show up', 'Peers enjoy it', 'It saves typing',
         'Explaining aloud exposes the steps you cannot justify.', m('RECALL')),
        ('If you cannot explain it, what do you do?', 'Re-run the demo steps', 'Move on anyway', 'Guess the answer',
         'Repeat the live demonstration before moving on.', m('RECALL')),
        (f'For this capstone, what proved the fix?', 'User verification', 'A green light alone', 'No complaints yet',
         'The affected user confirming it works is the proof.', m('STATUS')),
    ],
        P(f'To check you really understood the {d["title"]} capstone, explain it to a classmate in under two minutes: the symptom, your first three '
          f'checks ({st[0].lower()}, {st[1].lower()}, {st[2].lower()}), what proved the cause, and how you confirmed it was fixed. If you stumble, '
          'go back and repeat the live demonstration before moving on.'),
        P('Teachers say you only know something when you can teach it. Telling a friend the plot of a film quickly shows which parts you missed: '
          'you reach a scene and realise you do not know why the character did that. Explaining the ticket aloud works the same way and shows '
          'which step you cannot yet justify.'),
        ['Symptom.', 'First three checks.', 'What proved the cause.', 'How you verified the fix.', 'Under two minutes.'],
        '<p>Guess first, then reveal.</p>',
        reveal('What is the one line that proves this ticket is finished?', 'The affected user confirmed the service works, and that confirmation is written in the ticket.'))
    return {'the-scenario': sc, 'your-turn-scaffolded-checklist': ck, 'common-beginner-mistakes': bm, 'check-your-understanding': cu}


def apply(lessons, mcs_out, chapter, data, capd, cap_obj):
    """Replace every remaining skip in a NETOPS chapter: practice sections from data[label], capstone sections from capd,
    and the repeated 'Network operations depth' signpost as same_as the lesson's laddered core section."""
    from curriculum_v2.ladder.schema import same_as
    for label, secs in lessons.items():
        skips = {sid for sid, e in secs.items() if e.get('type') == 'skip'}
        if not skips:
            continue
        code = 'NO' + label.replace('.', '')
        src = f'Course lesson {label} (the original section), re-explained'
        if label in data:
            obj = f'NO-{label}'
            mcs_out.update(mcs(code, obj, src))
            built = ops(code, obj, data[label]['title'], src, data[label])
        else:
            mcs_out.update(mcs(code, cap_obj, src))
            built = cap(code, cap_obj, src, capd)
        for sid in sorted(skips):
            if sid in built:
                secs[sid] = built[sid]
            elif sid == 'network-operations-depth':
                core = 'core-content' if secs.get('core-content', {}).get('type') == 'section' else next(
                    k for k, e in secs.items() if e.get('type') == 'section')
                secs[sid] = same_as(core, 'Network operations depth',
                                    'The course-wide depth signpost repeated in several lessons; the core section of this lesson ladders it.')
