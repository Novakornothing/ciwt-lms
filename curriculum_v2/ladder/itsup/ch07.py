"""Explanation ladder — ITSUP chapter 7 (Troubleshooting Methodology). Pending SME review.

Author B (labs branch, pass 19). Every concept section of lessons 7.1-7.4 is laddered (Option B pass 2 replaced every same_as with a bespoke ladder, _p2cNN.py), or
skipped with a reason. Rungs re-explain what the lesson teaches; they add no new course rules. The method follows
the CompTIA A+ best-practice troubleshooting methodology the lesson is built on; escalation and problem records
follow ITIL 4 incident and problem management.
"""
from curriculum_v2.ladder.itsup._p2c07 import SECS as _P2
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, section, skip, sort,
                                         tryit, visual)

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 7

L71 = 'Course lesson 7.1 “Structured Process” (the original section), re-explained'
L72 = 'Course lesson 7.2 “Fault Domains” (the original section), re-explained'
L73 = 'Course lesson 7.3 “Verification and Handoff” (the original section), re-explained'
L74 = 'Course lesson 7.4 “Capstone Drills” (the original section), re-explained'
APLUS = ('CompTIA A+ Core 1 (220-1201) exam objectives: best-practice troubleshooting methodology (identify the problem, '
         'establish a theory, test it, plan and implement, verify full functionality, document)')
ITIL = 'AXELOS, ITIL 4 Foundation (2019): incident management, problem management and service desk practices'
RFC3927 = 'IETF RFC 3927, Dynamic Configuration of IPv4 Link-Local Addresses (169.254.0.0/16)'

MISCONCEPTIONS = {
    'MC-L-IT7-TEST-CONFIRMS-ONLY': {
        'obj': 'IT-7.1', 'label': 'Choosing a test that can only confirm what you already believe, so no result could change your mind',
        'fix': 'Pick a test that is cheap, safe and decisive: either result tells you something and can kill a theory.',
        'terms': ['test', 'theory', 'decisive', 'cheap'], 'source': L71 + '; ' + APLUS, 'review': 'Pending SME review'},
    'MC-L-IT7-END-TO-END-WALK': {
        'obj': 'IT-7.1', 'label': 'Testing a long path one hop at a time from one end instead of splitting it in the middle',
        'fix': 'Test the middle of the path first (half-splitting); each result removes half of the places the fault can be.',
        'terms': ['half-splitting', 'divide and conquer', 'path'], 'source': L71, 'review': 'Pending SME review'},
    'MC-L-IT7-TOOL-FIRST': {
        'obj': 'IT-7.2', 'label': 'Picking a familiar tool first and working out what part of the system it tests afterwards',
        'fix': 'Name the fault domain from the symptom and scope first; the domain chooses the tool and the owner.',
        'terms': ['fault domain', 'scope', 'tool', 'owner'], 'source': L72, 'review': 'Pending SME review'},
    'MC-L-IT7-NO-UPDATE-PLAN': {
        'obj': 'IT-7.4', 'label': 'Keeping working past the time box or outside your domain instead of escalating with evidence',
        'fix': 'Stop and escalate when access, ownership, the time box or growing impact says so, with the evidence attached.',
        'terms': ['time box', 'escalate', 'stop', 'impact'], 'source': L74, 'review': 'Pending SME review'},
}

# reused course misconceptions (curriculum_v2/misconceptions.py)
FIXFIRST, TRUSTUSER, MANY = 'MC-IT7-FIX-BEFORE-IDENTIFY', 'MC-IT7-TRUST-USER-DIAGNOSIS', 'MC-IT7-MANY-CHANGES'
CROSS, CLOSED, GUESS = 'MC-IT7-CROSS-DOMAIN', 'MC-IT7-CLOSED-AS-VERIFIED', 'MC-IT7-GUESS-AS-FACT'
PARTS, SILENT, ORDER = 'MC-IT7-PACKAGE-PARTS', 'MC-IT7-SILENT-ESCALATION', 'MC-C-IT7-METHOD-ORDER'
DSCOPE, NOVERIFY, THIN = 'MC-C-IT7-DOMAIN-SCOPE', 'MC-C-IT7-NO-VERIFY', 'MC-C-IT7-THIN-ESCALATION'
DELAY, VAGUE, PREVENT = 'MC-C-IT7-SILENT-DELAY', 'MC-R5-IT7-VAGUE-EVIDENCE', 'MC-R5-IT7-PREVENT-WORKAROUND'
CONFIRMS, ENDWALK = 'MC-L-IT7-TEST-CONFIRMS-ONLY', 'MC-L-IT7-END-TO-END-WALK'
TOOLFIRST, NOSTOP = 'MC-L-IT7-TOOL-FIRST', 'MC-L-IT7-NO-UPDATE-PLAN'

SVG = 'viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" aria-label="{label}" class="ladder-svg"'


def svg(w, h, label, body):
    return f'<svg {SVG.format(w=w, h=h, label=label)}><title>{label}</title>{body}</svg>'


def box(x, y, w, h, text, sub=''):
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>'
    t += (f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 7)}" text-anchor="middle" dominant-baseline="middle" '
          f'fill="currentColor" font-size="13" font-weight="700">{text}</text>')
    if sub:
        t += (f'<text x="{x + w / 2}" y="{y + h / 2 + 10}" text-anchor="middle" dominant-baseline="middle" '
              f'fill="currentColor" font-size="11">{sub}</text>')
    return t


def arrow(x1, y1, x2, y2):
    """Horizontal (y1 == y2) or vertical-down arrow."""
    rot = 0 if y1 == y2 else 90
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="2"/>'
            f'<polygon points="{x2},{y2} {x2 - 7},{y2 - 5} {x2 - 7},{y2 + 5}" fill="currentColor" transform="rotate({rot} {x2} {y2})"/>')


def label(x, y, text, size=11, anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="currentColor" font-size="{size}">{text}</text>'


# ---------------------------------------------------------------- diagrams
_LOOP = svg(640, 210, 'The theory and test loop: identify, list theories, test the top one; a disproved theory sends you back to the list; only a confirmed cause moves on to plan, one change, verify and document',
            box(10, 20, 110, 50, 'Identify', 'outcome, scope') + arrow(120, 45, 150, 45)
            + box(150, 20, 120, 50, 'Theories', 'two or three') + arrow(270, 45, 300, 45)
            + box(300, 20, 120, 50, 'Test', 'cheapest first') + arrow(420, 45, 450, 45)
            + box(450, 20, 180, 50, 'Cause confirmed', 'now you may change')
            + '<path d="M360 70 C360 115 210 115 210 72" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/>'
            + '<polygon points="210,72 205,82 215,82" fill="currentColor"/>'
            + label(285, 120, 'disproved → back to the list (nothing changed yet)')
            + arrow(540, 70, 540, 140)
            + box(10, 145, 140, 50, 'Plan + undo') + arrow(150, 170, 180, 170)
            + box(180, 145, 140, 50, 'Change ONE thing') + arrow(320, 170, 350, 170)
            + box(350, 145, 140, 50, 'User verifies') + arrow(490, 170, 520, 170)
            + box(520, 145, 110, 50, 'Document'))

_SPLIT = svg(640, 170, 'Half-splitting a path from a PC to an app server: test the middle by IP first; success clears the network half, failure clears the name and app half',
             box(10, 20, 100, 44, 'User PC') + arrow(110, 42, 150, 42) + box(150, 20, 100, 44, 'Switch')
             + arrow(250, 42, 290, 42) + box(290, 20, 100, 44, 'Router') + arrow(390, 42, 430, 42)
             + box(430, 20, 100, 44, 'App server') + arrow(530, 42, 560, 42) + box(560, 20, 70, 44, 'Name')
             + '<line x1="410" y1="10" x2="410" y2="80" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/>'
             + label(410, 98, 'Test 1: reach the server by IP address')
             + label(200, 128, 'reply → this half works', 12) + label(520, 128, 'no reply → look here first', 12)
             + label(320, 156, 'one test removes half the suspects; the next test splits the half that is left'))

_DOMAINS = svg(640, 200, 'Three scope questions point at a fault domain: does it follow the user, stay with the device, or hit everyone using one app',
               box(10, 75, 120, 50, 'Symptom') + arrow(130, 100, 170, 100)
               + box(170, 10, 200, 50, 'Same user, other PC?', 'fails too → account') + box(170, 75, 200, 50, 'Other user, this PC?', 'fails too → device')
               + box(170, 140, 200, 50, 'Same app, other users?', 'fails too → service') + arrow(370, 35, 420, 35) + arrow(370, 100, 420, 100)
               + arrow(370, 165, 420, 165) + box(420, 10, 210, 50, 'Identity team', 'account / profile')
               + box(420, 75, 210, 50, 'Desk-side', 'device, OS, its network') + box(420, 140, 210, 50, 'App owner / provider', 'service or SaaS'))

_HANDOFF = svg(640, 150, 'Fixed versus verified, then the handoff: your test passing is supporting evidence; the user doing their own task is verification; the notes let the next person start at the test step',
               box(10, 20, 180, 54, 'Your test passes', 'supporting evidence') + arrow(190, 47, 230, 47)
               + box(230, 20, 180, 54, 'User does the task', 'verification') + arrow(410, 47, 450, 47)
               + box(450, 20, 180, 54, 'Notes: cause, fix,', 'verified, prevention')
               + label(320, 100, 'Escalating instead? the package carries: impact · scope · evidence ·', 12)
               + label(320, 120, 'actions → results · current state · request', 12)
               + label(320, 142, 'so the next tier starts at “test”, not at “identify”', 11))

_STOP = svg(640, 190, 'A time-boxed drill: work the method inside the box; any one stop signal sends the ticket up with evidence and a status message to the user',
            box(10, 20, 250, 150, 'Inside the time box') + label(135, 75, 'identify · theories · cheap tests', 12)
            + label(135, 95, 'one change with rollback', 12) + label(135, 115, 'user verifies · notes', 12)
            + arrow(260, 95, 320, 95)
            + box(320, 20, 310, 150, 'Stop signals (any one)') + label(475, 70, 'need access or approval you lack', 12)
            + label(475, 90, 'evidence points to another team’s domain', 12) + label(475, 110, 'time box expired, no confirmed cause', 12)
            + label(475, 130, 'impact grew: more users, safety, data', 12) + label(475, 155, '→ escalate with evidence; tell the user who and when', 11))

LESSONS = {
    '7.1': {
        'start-here-why-a-method-exists': skip(
            'Start here — why a method exists', 'orientation',
            'A short start-here summary of the method; the core section that follows teaches it and carries the ladder.'),

        'core-content': section(
            'Core content', 'IT-7.1',
            [check('A user says “it’s the Wi-Fi”. You note her words, then record that two colleagues on the same Wi-Fi '
                   'are fine and the fault began at 09:10. Which step are you doing?',
                   'Identify: outcome, scope and start time',
                   ['Test: proving the Wi-Fi theory she gave you', 'Plan: deciding which change to make first'],
                   'Identify collects the missing outcome, who is affected and since when. Accepting the user’s cause and '
                   'testing it, or planning a change, comes later and would skip the evidence.', mc=[TRUSTUSER, FIXFIRST]),
             check('Your first test disproves your top theory. What does the method say happens next?',
                   'Go back to the theory list and test the next theory',
                   ['Make a change anyway, since the test is already done', 'Close the ticket, as the test showed no fault'],
                   'A failed test sends you back to the list of theories; nothing is changed until a test confirms a cause. '
                   'Changing anyway is guessing, and closing ignores that the outcome is still missing.', mc=[ORDER, NOVERIFY])],
            plain('''<p>Fixing things goes better with a fixed order.</p>
<ol><li>Find out what the person cannot do. Find out who else has the problem, and since when.</li>
<li>Write down two or three likely causes.</li>
<li>Test the most likely one with the quickest safe check.</li>
<li>If the check says “not this”, go back to your list. Do not change anything yet.</li>
<li>When a check points to the cause, plan the fix. Know how to undo it.</li>
<li>Change one thing only. Then see if it worked.</li>
<li>Ask the user to try their task again.</li>
<li>Write down the cause, the fix and the proof.</li></ol>
<p>Why one thing at a time? If you change four things, you never learn which one helped.</p>''',
                  L71 + '; ' + APLUS,
                  [check('Why does the method say to change only one thing at a time?',
                         'So you know which change brought the outcome back',
                         ['Because each change must be approved by a manager first', 'Because several changes make the PC run more slowly'],
                         'One change per test means the result belongs to that change. With several changes at once a fix '
                         'cannot be explained or repeated; approval and speed are not the reason the method gives.', mc=[MANY, None])]),
            analogy('''<p>A doctor with a patient who has a fever does not start with surgery.</p>
<p>First the doctor asks what is wrong, since when, and whether anyone at home is ill too. That is <strong>identify</strong>.
Then the doctor thinks of a few likely causes (a virus, an infection) — the <strong>theories</strong>. A cheap test comes
next, like a throat swab, and not a full-body scan. If the swab is clear, the doctor crosses that cause off and tests
the next one. Only with a confirmed cause does the doctor <strong>plan</strong> treatment, start <strong>one</strong>
medicine so its effect is clear, and later ask the patient how they feel — that is <strong>verify</strong>. The chart
notes record what was found and what worked, so the next doctor does not start from zero.</p>
<p>Where the comparison stops: a PC rarely gets better on its own, so “wait and see” is not a test.</p>''',
                    L71 + ' (doctor analogy written for this rung); ' + APLUS,
                    [check('In the doctor story, the swab comes back clear. What matches that in troubleshooting?',
                           'A test disproved one theory, so you test the next',
                           ['The fault is fixed, because the test came back clear', 'The user was wrong, so the ticket can be closed'],
                           'A clear swab rules out one cause; the patient is still ill. In the same way a disproved theory sends '
                           'you back to the list while the user’s outcome is still missing.', mc=[NOVERIFY, TRUSTUSER])]),
            visual(_LOOP + '''
<ol class="ladder-trace">
<li><strong>Identify</strong>: “Mail stays in the Outbox, one user, since 08:30, webmail sends.”</li>
<li><strong>Theories</strong>: stale sign-in · security tool blocking Outlook · mail service down (last, since webmail works).</li>
<li><strong>Test</strong> stale sign-in: sign out and back in → same error. Back to the list.</li>
<li><strong>Test</strong> security tool: its log shows Outlook blocked at 08:27 → cause confirmed.</li>
<li><strong>Plan</strong>: the security team owns the tool; report it rather than turn protection off.</li>
<li><strong>One change</strong>: the security team releases the rule.</li>
<li><strong>Verify</strong>: the user sends a message and a colleague receives it.</li>
<li><strong>Document</strong>: cause, fix, verification, prevention.</li></ol>''',
                   L71 + ' (worked example “Outlook won’t send”, drawn as a loop)',
                   [check('In the loop picture, where does the dashed arrow from “Test” lead, and why?',
                          'Back to the theories, because a disproved theory means nothing gets changed yet',
                          ['Forward to “Plan”, because every test result, pass or fail, should become a change', 'Straight to “Document”, because a failed test ends the job'],
                          'The dashed arrow returns to the theory list: a test that kills a theory gives you the next theory to '
                          'test, not permission to change something or to stop working.', mc=[ORDER, FIXFIRST])]),
            tryit('''<p>Put the method in order for a real ticket, then work one end to end in the methodology lab. The lab
records every action, so you can see whether you changed anything before a test confirmed the cause.</p>''',
                  L71 + '; ' + APLUS,
                  [check('A technician reinstalls a driver, swaps a cable and edits a setting, and the fault clears. What can they write as the cause?',
                         'Nothing they can prove: three changes hide which one helped',
                         ['The driver, because a reinstall is usually what fixes it', 'The cable, because physical faults are the most common'],
                         'With three changes at once, the result cannot be tied to any single one, so the cause is unknown. '
                         'Naming the driver or the cable would be a guess written as fact.', mc=[MANY, GUESS])],
                  widget=order('Order the steps for “the shared drive is gone” (one user, since this morning).',
                               ['Note who, what outcome, how many and since when',
                                'List two or three likely causes',
                                'Run the cheapest test that could kill the top cause',
                                'Plan the fix and how to undo it',
                                'Make one change',
                                'Have the user open the drive themselves',
                                'Write cause, fix, verification and prevention'],
                               'Nothing is changed until a test has pointed at a cause, and the job ends with the user’s own check and the notes.'),
                  lab={'id': 'ticket-method', 'note': 'Work the ticket end to end; the lab scores the order of your steps.'})),

        '1-the-order': _P2[('7.1', '1-the-order')],
        'the-seven-words': _P2[('7.1', 'the-seven-words')],

        'cheap-tests-first': section(
            'Cheap tests first', 'IT-7.1',
            [check('Which is the better first test for “this PC has no network”?',
                   'Ping the default gateway',
                   ['Reinstall the network adapter driver', 'Reimage the PC to rule out the operating system'],
                   'Pinging the gateway takes seconds, changes nothing and either result is useful. A driver reinstall or '
                   'reimage takes long, changes the system and would not tell you what was wrong.', mc=[FIXFIRST, None])],
            plain('''<p>Some tests are cheap. They take a minute. They change nothing. Ping is one. Trying a second app is
another. So is trying the next desk, or a cable you know works.</p>
<p>Some tests are costly. Reimaging is one. Swapping a part is another. They take a long time. They change the PC.</p>
<p>Start with the cheap ones. A good test also gives you an answer either way. A reply tells you something. No reply
tells you something too.</p>
<p>Long path? Test in the middle first. Then you know which half to look at.</p>''',
                  L71,
                  [check('A test can only ever say “yes”. Why is it a poor test?',
                         'No result could change your mind, so it teaches you nothing',
                         ['It takes too long to run on a busy help desk with a queue of other tickets', 'It needs admin rights that the help desk lacks'],
                         'A useful test is decisive: one result supports the theory and the other kills it. A test that can only '
                         'agree with you gives no new information; speed and rights are not the problem.', mc=[CONFIRMS, None])]),
            analogy('''<p>You are looking for a fault in a long string of fairy lights that will not light.</p>
<p>You could start at the plug and check each bulb in turn — slow, if the dead bulb is near the far end. Or you could
check the <strong>middle</strong> of the string first: if the first half lights from there, the fault is in the second
half, and you have ruled out half the bulbs with one check. Check the middle of the half that is left, and so on.
Ten checks can find one bad bulb in a string of a thousand.</p>
<p>A network path is the same. User PC → switch → router → server → name lookup. Reaching the server by IP is the
“middle bulb”: if it works, the network half is fine and you look at names and the app.</p>''',
                    L71 + ' (fairy-light analogy written for this rung)',
                    [check('In the fairy-light story, why check the middle of the string first?',
                           'One check removes half of the bulbs that could be at fault',
                           ['The middle bulbs are the ones most likely to fail, since they run the hottest', 'Starting at the plug end could damage the string'],
                           'Half-splitting works because each check halves the suspects, whatever the result. The middle is not '
                           'more likely to fail; it is simply the point that divides the possibilities evenly.', mc=[ENDWALK, None])]),
            visual(_SPLIT + '''
<ol class="ladder-trace">
<li>Symptom: one user cannot open an internal web app by its name.</li>
<li>Test the middle: reach the app server by its IP address.</li>
<li>It answers → the PC, switch and router are fine. Look at name resolution or the app.</li>
<li>It does not answer → names are not the problem yet. Look between the PC and the server.</li>
<li>Split the remaining half again with the next cheap test.</li></ol>''',
                   L71 + ' (half-splitting example from the core section, drawn)',
                   [check('The app server answers by IP address but the user’s browser still fails by name. Which half is cleared?',
                          'The network path from the PC to the server',
                          ['Name resolution, because the IP test reached the server', 'The application, because the server itself answered'],
                          'An answer by IP proves the PC-to-server path. Names were not used in that test, so name resolution '
                          'and the app are still suspects and are the half you test next.', mc=[ENDWALK, CROSS])]),
            tryit('''<p>Sort the tests by cost before you touch a real ticket. Then try the name-resolution lab: it gives you a
PC that fails by name, and the cheapest decisive test splits the path at once.</p>''',
                  L71,
                  [check('Which of these is cheap, safe and decisive for “the PC can’t reach the file server”?',
                         'Reach the file server by IP address',
                         ['Replace the network card with a new spare', 'Reset the whole network stack and restart the PC'],
                         'An IP test takes seconds, changes nothing, and success or failure narrows the fault. A card swap or '
                         'network reset is slow, changes the system and destroys the evidence.', mc=[FIXFIRST, None])],
                  widget=sort('Sort each first test: cheap and safe, or expensive and changes the system.',
                              {'Cheap and safe': ['Ping the default gateway', 'Try a second app', 'Try the user at the next desk',
                                                  'Swap in a known-good cable'],
                               'Expensive or changes things': ['Reimage the PC', 'Replace the motherboard',
                                                               'Reinstall the network driver', 'Reset all network settings']},
                              'The cheap tests take a minute and leave the evidence in place; save the expensive ones for when a test points to them.'),
                  lab={'id': 'win-net-cli', 'note': 'Isolate the name-resolution fault with the cheapest test that splits the path.'})),

        'teach-block-process-on-a-live-sentence': skip(
            'Teach block — process on a live sentence', 'plan',
            'An instructor teaching block with a timing; the concept is laddered in the core section.'),
    },

    '7.2': {
        'core-content': section(
            'Core content', 'IT-7.2',
            [check('A user gets a temporary profile on every PC she signs in to. Which fault domain fits best?',
                   'Account or profile, since it follows her',
                   ['Local network, since profiles load over the LAN', 'Hardware, since each PC may have a failing disk'],
                   'The problem follows the user to every device, so the devices and their networks are ruled out. That '
                   'pattern points to the account or profile, owned by the identity or endpoint team.', mc=[DSCOPE, CROSS])],
            plain('''<p>A fault domain is the part of the system that could cause the problem. Examples are power, the PC
itself, the account, the network, the name lookup, or an online service.</p>
<p>Pick the domain first. Then pick the tool. A network tool cannot help a PC that will not turn on. A DNS change cannot
help a user whose password ran out.</p>
<p>To find the domain, ask about scope. Is it one user? One PC? One app? One building? Everyone?</p>
<p>One test can answer two questions. If the user tries a colleague’s PC and still fails, the PC is fine. The account is
now the suspect.</p>''',
                  L72,
                  [check('Why name the fault domain before you choose a tool?',
                         'The domain decides which tool and which team can prove it',
                         ['Tools only run once a domain is logged in the ticket', 'Every domain uses the same first tool anyway'],
                         'Naming the domain keeps you from using a network command on a power fault or editing DNS for a password '
                         'problem. Tools do not depend on the ticket field, and domains have different first tests.', mc=[TOOLFIRST, None])]),
            analogy('''<p>Your kitchen tap gives no water. Before you call anyone, you ask a few questions.</p>
<p>Does the bathroom tap work? If yes, the house supply is fine and the fault is in the kitchen tap — call a plumber for
that one tap. Do the neighbours have water? If no one on the street does, it is the water company, and nothing in your
house will fix it. Only the kitchen, only your house, or the whole street: each answer names a different
<strong>domain</strong> and a different person to call.</p>
<p>Help-desk tickets work the same way. “Same user on another PC?”, “another user on this PC?”, “same app for other
people?” tell you whether to look at the account, the device or the service before you pick up a tool.</p>''',
                    L72 + ' (household-water analogy written for this rung)',
                    [check('In the water story, the whole street has no water. What is the help-desk match?',
                           'Many users fail on one service: the provider’s domain',
                           ['One user’s PC has a fault, because the kitchen tap failed first', 'The user’s account is locked, because only one tap was tested'],
                           'When everyone using the same supply fails, the fault is upstream, at the provider. A PC or account '
                           'fault would affect one user, not the whole street.', mc=[DSCOPE, None])]),
            visual(_DOMAINS + '''
<ol class="ladder-trace">
<li>“Teams shows a spinning circle.”</li>
<li>Teams in a browser on the same PC works → the network path and the account are fine.</li>
<li>Colleagues are fine → it is not a service outage.</li>
<li>Domain: the desktop app on this one PC. First test: the app’s own repair or cache reset.</li>
<li>Untouched: DNS, the network adapter, the password — the scope ruled them out.</li></ol>''',
                   L72 + ' (scoping diagram and “Teams won’t load” example, redrawn)',
                   [check('Twelve users on one floor cannot print; other floors print fine. What should come before reinstalling any driver?',
                          'Scope it: what do the twelve share that other floors do not?',
                          ['Reinstall the print driver on every PC on that floor, one by one', 'Replace the printer with a spare and test again'],
                          'Scoping finds the shared part — in the lesson, one queue and a printer IP that now conflicts. '
                          'Driver reinstalls or a printer swap act before the domain is known.', mc=[CROSS, FIXFIRST])]),
            tryit('''<p>Match each symptom to its domain before you open any tool. Then do the full-triage lab, where the
first job is to say which domain you are in.</p>''',
                  L72,
                  [check('Many users at one office lose a cloud app, but colleagues at home can still use it. Which domain comes first?',
                         'The office’s Internet path, proxy or DNS',
                         ['The cloud provider, because the app is the thing failing', 'Each user’s account, because they all sign in to the app'],
                         'The service works from another network, so the provider and the accounts are fine. What the failing '
                         'users share is the office network path.', mc=[DSCOPE, None])],
                  widget=sort('Put each symptom in its fault domain.',
                              {'Account / profile': ['Locked out after a password change', 'Temporary profile on every PC'],
                               'Local network': ['Address starts 169.254', 'No network icon on one PC'],
                               'Name resolution': ['Works by IP, fails by name', 'Wrong website loads for a name'],
                               'Service / SaaS': ['Every user of one app fails', 'Provider status page shows an incident']},
                              'The scope and the symptom name the domain; the domain then names the tool and the owner.'),
                  lab={'id': 'win-full-triage', 'note': 'Decide the domain from the first evidence before you change anything.'})),

        '1-domains-you-already-know': _P2[('7.2', '1-domains-you-already-know')],
        'fault-domains-you-already-know': _P2[('7.2', 'fault-domains-you-already-know')],
    },

    '7.3': {
        'core-content': section(
            'Core content', 'IT-7.3',
            [check('A test page prints after your fix. What still has to happen before the ticket counts as verified?',
                   'The user does their own print job and confirms it',
                   ['The print queue should be clear for one full hour', 'Your manager should approve the closure notes'],
                   'Verification is the user’s lost outcome back and confirmed by them. A test page and an empty queue '
                   'are supporting evidence; approval is not the verification step.', mc=[CLOSED, NOVERIFY]),
             check('Which escalation lets the network team start at the test step instead of starting over?',
                   'Floor 3 APIPA since 07:50, floor 2 fine, Gi1/0/24 err-disabled',
                   ['Escalated to network, user cannot work, very urgent please call', 'Network issue on floor 3, tried everything, no luck'],
                   'The useful note carries scope, a start time and the evidence. The other two give no comparison and no '
                   'results, so the next team must repeat the first-tier tests.', mc=[THIN, VAGUE])],
            plain('''<p>“Fixed” is what you think. “Verified” is what the user shows you.</p>
<p>After a fix, run the same test that failed. Then ask the user to do the task they could not do. A green icon is not
enough. A test page is not enough. They help, but the user’s own task is the proof.</p>
<p>Then ask: can this happen again? If so, note how to stop it. If not, say so.</p>
<p>Sometimes you pass the ticket on. Then write what the next person needs: who is hit, what works and what does not,
the error and times, what you tried and what happened, what you changed, and what you need from them.</p>''',
                  L73 + '; ' + ITIL,
                  [check('Which is the strongest closure note?',
                         'Cause: duplicate IP. Fix: moved camera. User printed 09:40',
                         ['Fixed printer, all good now, user happy, ticket closed by me', 'Printer working again after restart'],
                         'A strong note records the cause, the fix and the user’s verification so another technician can repeat '
                         'it. “All good” and “working again” are impressions with no cause or proof.', mc=[VAGUE, CLOSED])]),
            analogy('''<p>Think of a car repair.</p>
<p>The mechanic says the brakes are fixed. That is a claim. You are only sure when you drive the car and it stops
properly — that is <strong>verification</strong>, and it is the driver who does it, not the mechanic’s gauge. A good
garage also hands you a job sheet: what was wrong, what was replaced, and when to come back. That is the
<strong>closure note</strong>.</p>
<p>If the garage sends the car to a specialist, it sends the job sheet too — the noise, when it started, what they tried
and what they found — so the specialist does not take the car apart again from scratch. That is the
<strong>escalation package</strong>.</p>''',
                    L73 + ' (car-repair analogy written for this rung)',
                    [check('In the car story, why does the garage send its job sheet to the specialist?',
                           'So the specialist can skip the tests already done',
                           ['So the specialist can bill the customer directly', 'So the garage is not blamed if the repair fails'],
                           'The job sheet is the escalation package: symptoms, times, actions and results. It lets the next person '
                           'start where the first stopped. Billing and blame are not why the package exists.', mc=[THIN, None])]),
            visual(_HANDOFF + '''
<ol class="ladder-trace">
<li>Your test passes → write it down as supporting evidence.</li>
<li>The user prints the real booking receipt at 09:40 → <strong>verified</strong>.</li>
<li>Ask “can it recur?” → reserve the printer’s IP in DHCP and label it (prevention).</li>
<li>Close with cause, fix, verification and prevention.</li>
<li>Or, if escalating: impact · scope · evidence · actions → results · current state · request, plus the next update time for the user.</li></ol>''',
                   L73 + ' (closure-note and escalation-package examples, drawn)',
                   [check('In the picture, which box is the actual verification?',
                          'The user doing the task they could not do',
                          ['Your own test passing after the change', 'The notes recording the cause and the fix'],
                          'Your test is supporting evidence and the notes record the result; only the user’s own task, back and '
                          'confirmed, verifies the fix.', mc=[CLOSED, None])]),
            tryit('''<p>Sort the notes into strong and weak, then rewrite a weak escalation in your head before you reveal the
lesson’s version.</p>''',
                  L73,
                  [check('Which part of an escalation package is “I reseated the uplink and it is still reseated”?',
                         'Current state: what you changed and whether it still is',
                         ['Impact: who cannot do what, how many people, and any deadline', 'Request: what you need the next team to do'],
                         'Current state tells the next team what is different from normal right now. Impact describes the people '
                         'affected, and the request says what you need.', mc=[PARTS, None])],
                  widget=reveal('Rewrite: “User can’t get on VPN, tried everything, please help.” What would you add before revealing?',
                                'P3, one remote user since 07:30, colleagues fine; the exact error text; tried a client restart (no change), '
                                'home Internet works, PC clock correct, same on a mobile hotspot; nothing changed on the PC; request: check '
                                'the user’s VPN certificate or group.'),
                  lab={'id': 'ticket-method', 'note': 'Finish a ticket with a verification line and a closure note.'})),

        'handoff': _P2[('7.3', 'handoff')],
    },

    '7.4': {
        'core-content': section(
            'Core content', 'IT-7.4',
            [check('You are ten minutes into a fifteen-minute drill and the evidence points to the identity team’s system. What now?',
                   'Escalate to identity with the evidence and tell the user',
                   ['Keep testing until the fifteen-minute time box has fully run out', 'Change the user’s group yourself to save time'],
                   'Evidence pointing at another team’s domain is a stop signal, even with time left. Using up the box or '
                   'changing a system you do not own skips the escalation the method requires.', mc=[NOSTOP, THIN])],
            plain('''<p>The drills check how you work, not how fast you guess.</p>
<p>Each drill has a time limit. Inside it you use the method: find out the problem, list causes, run cheap tests, make
one change, have the user check, write notes.</p>
<p>Stop and pass the ticket on when any of these is true. You need access you do not have. The problem is in another
team’s area. Time ran out and you still do not know the cause. More people are now affected, or there is a risk.</p>
<p>Tell the user who has the ticket now, what you need from them, and when they will hear next.</p>''',
                  L74 + '; ' + ITIL,
                  [check('After you escalate, what should the user be told?',
                         'Who has the ticket now and when they will hear next',
                         ['Nothing until the other team has the fix', 'The cause you suspect, so they can plan their day around it'],
                         'The user needs the owner, anything needed from them, and the next update time. Silence leaves them '
                         'without status, and a guessed cause can be wrong.', mc=[SILENT, DELAY])]),
            analogy('''<p>Think of a lifeguard at a pool.</p>
<p>The lifeguard handles what the job covers: a swimmer with cramp, a child who strays into the deep end. But some things
are beyond that post — a spinal injury, a chemical leak in the plant room. The lifeguard does not keep trying alone
until it is too late. The rule is clear: when it is outside your training or your equipment, or it is getting worse,
you call the ambulance or the plant engineer <em>early</em>, tell them exactly what you have seen, and tell the
people at the pool what is happening.</p>
<p>A help-desk drill works the same way. The time box and the stop signals are your “call for help now” rules.</p>''',
                    L74 + ' (lifeguard analogy written for this rung)',
                    [check('In the lifeguard story, which stop signal matches “the impact has grown”?',
                           'The situation is getting worse while you watch',
                           ['The swimmer is asking you lots of questions', 'Your shift is nearly over for the day'],
                           'Growing impact — more people, safety or data at risk — is a reason to escalate at once. Questions from '
                           'the swimmer and the end of a shift are not stop signals.', mc=[NOSTOP, None])]),
            visual(_STOP + '''
<ol class="ladder-trace">
<li>Drill A, “Internet is down”: one PC shows 169.254.x.x → a lease failure.</li>
<li>Check the link and adapter state; renew the lease.</li>
<li>Still failing → stop: the switch port belongs to the network team.</li>
<li>Escalate with the port and the MAC address.</li>
<li>Tell the user who has it and when the next update comes.</li></ol>''',
                   L74 + ' (drill A from the core section, drawn); ' + RFC3927,
                   [check('Drill B: the shared drive also fails when the user signs in on another PC. What do you stop doing?',
                          'Testing the first PC’s hardware, OS and network',
                          ['Talking to the user until the cause is found', 'Recording the tests you have already run'],
                          'The fault follows the user, so the device is ruled out and the account is the domain. You keep '
                          'recording and keep the user informed.', mc=[CROSS, SILENT])]),
            tryit('''<p>Sort the situations into “keep working” and “stop and escalate”, then run the methodology VM lab
with a time box of your own.</p>''',
                  L74,
                  [check('A student ran two resets and a reboot with no tests in between, and the fault remained. What did the rubric miss most?',
                         'Identify notes, scope, and a test between changes',
                         ['A faster reboot and one more reset of the network stack', 'A reimage once the resets did not help'],
                         'The lesson’s rubric marks the attempt down for no identify notes, no scope and two untested changes; the '
                         'cause was visible in the first ipconfig. More changes would repeat the mistake.', mc=[MANY, FIXFIRST])],
                  widget=sort('Keep working inside the time box, or stop and escalate?',
                              {'Keep working': ['Cheap tests are still narrowing the cause', 'The fix is in your domain and you have access'],
                               'Stop and escalate': ['The fix needs approval you do not have', 'Evidence points to another team’s system',
                                                     'Time box over, no confirmed cause', 'More users are now affected']},
                              'Any single stop signal is enough; escalate with the evidence and tell the user what happens next.'),
                  lab={'id': 'linux-vm-method', 'note': 'Work the broken time-clock service with the method; note when you would escalate.'})),

        'two-drills': skip('Two drills', 'activity', 'Pointers to practice drills (hw-board, win-dns-break); the drills are the practice.'),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '7.1': {'core-content': '8bf5d2f53eba', 'cheap-tests-first': '05b0b4fae80b'},
    '7.2': {'core-content': '788c7e9d4ffb'},
    '7.3': {'core-content': 'db998f156c90'},
    '7.4': {'core-content': 'f95487361aee'},
}

# ---------------------------------------------------------------- refinement pass 20: former skips, now laddered
from curriculum_v2.ladder.itsup._lk import P as _P, X as _X  # noqa: E402

_LDNS = ('win-dns-break', 'Name fails after the IP path works: prove it, look it up, make one change, verify.')
LESSONS['7.1'].update({
    'start-here-why-a-method-exists': _X('Start here — why a method exists', 'IT-7.1', L71, [
        ('A beginner changes four settings and the fault clears. What is the problem?', 'Nobody knows which change worked', 'Nothing, the user is happy again', 'Four changes is too few to matter',
         'Several changes at once hide cause and effect, so the fix cannot be explained, repeated or safely undone.', MANY, FIXFIRST),
        ('Which step comes first in the method?', 'Name the outcome and scope', 'Reimage the PC to be safe', 'Change the likeliest setting',
         'You first say what is broken and for whom, then pick a cheap test, then change one thing.', FIXFIRST, TOOLFIRST),
        ('In the recipe-tasting story, why add one spice at a time?', 'So you know which one helped', 'Spices are very expensive', 'Chefs like slow cooking',
         'One change at a time is the only way to know which change mattered.', MANY, None),
        ('Trace step 2 picks the cheapest test that…', 'Can rule a theory out', 'Takes the longest time', 'Proves the user wrong',
         'Cheap tests that can kill a theory narrow the search fast.', CONFIRMS, GUESS),
        ('Where does “reimage” sit in the method?', 'An expensive last move', 'The first thing to try', 'Part of every ticket',
         'Reimaging destroys evidence and time; it is not a method, it is a last resort.', TOOLFIRST, FIXFIRST),
    ],
        _P('Without a fixed way of working, beginners change lots of things at once and then cannot say which one helped. The method is short. Say what is broken and for how many people. Choose the cheapest test that could prove your idea wrong. Change one thing. Check whether the problem is gone. Write it down. Wiping and reinstalling is not a method; it is a costly final step.'),
        _P('A cook whose soup tastes flat could throw in salt, lemon, pepper and herbs all at once. It might taste better, but next time they will '
           'not know which ingredient fixed it, and if it is now too salty they cannot tell what to take out. A careful cook adds one thing, tastes, '
           'and notes it. Troubleshooting is tasting the soup. One change, one taste, one note.'),
        ['Name the outcome and scope.', 'Pick the cheapest test that can kill a theory.', 'Change one thing.', 'Is the outcome back?', 'Write it down.'],
        '<p>Order the method, then try it in the lab on a name-resolution fault.</p>',
        order('The method', ['Name outcome and scope', 'Cheapest killing test', 'One change', 'Check the outcome', 'Write it down'],
              'Each step depends on the one before.'), _LDNS),
    'teach-block-process-on-a-live-sentence': _X('Teach block — process on a live sentence', 'IT-7.1', L71, [
        ('A user says “the internet is down.” What do you identify first?', 'One person or many', 'Which router to replace', 'Whether to reimage',
         'Scope (one versus many) decides where the fault can be.', DSCOPE, TOOLFIRST),
        ('Why does the block spend forty minutes on one sentence?', 'Practice beats a slide', 'The sentence is very long', 'There is nothing else to teach',
         'Walking the process on a real sentence builds the habit far better than memorising seven words.', ORDER, None),
        ('In the driving-lesson story, why drive real streets?', 'Practice beats reading rules', 'Roads are quieter at noon', 'The car needs running in',
         'Doing the process on live examples makes it stick.', ORDER, None),
        ('After the cheap test, what comes next in the trace?', 'One change', 'Three changes together', 'Close the ticket',
         'One change keeps cause and effect clear.', MANY, CLOSED),
        ('Which cheap test fits “the internet is down” for one PC?', 'ipconfig /all on that PC', 'Replacing the core switch', 'Calling the ISP first',
         'Start with the cheapest look at the one affected PC.', TOOLFIRST, DSCOPE),
    ],
        _P('In this teaching block the class takes one real complaint, “the internet is down,” and works through it together. First decide whether '
           'it is one person or many. Then pick a cheap test. Then make one change. Spending forty minutes doing this teaches far more than a slide '
           'with seven words on it.'),
        _P('You cannot learn to drive by reading the Highway Code. At some point the instructor takes you out on real streets, with real '
           'roundabouts and real cyclists, and makes you do the mirror-signal-manoeuvre routine again and again. This teach block is the driving '
           'lesson for troubleshooting: one live sentence, worked slowly, until the routine happens without thinking.'),
        ['Hear: “the internet is down.”', 'Identify: one PC or many?', 'Cheap test: ipconfig /all, ping the gateway.', 'One change.', 'Verify and record.'],
        '<p>Walk the sentence yourself in the lab.</p>',
        order('Live sentence', ['Identify scope', 'Cheap test', 'One change', 'Verify'], 'Scope, test, change, verify.'), _LDNS),
})
LESSONS['7.4'].update({
    'two-drills': _X('Two drills', 'IT-7.4', L74, [
        ('A PC gives a memory beep. Where does the work stay?', 'In POST, at the hardware', 'In Windows Device Manager', 'In the network adapter',
         'A beep at power-on happens before the OS, so the fault domain is hardware.', CROSS, CROSS),
        ('Names fail after the IP path works. Which drill?', 'win-dns-break or full triage', 'The hw-board memory drill', 'A diskpart exercise',
         'Name failure after IP works is a name-resolution fault.', CROSS, CROSS),
        ('In the fire-and-flood story, why different crews?', 'Each fault has its own domain', 'Each crew takes a turn', 'Flood crews cost less to send',
         'Matching the drill to the fault domain avoids wrong-domain fixes.', CROSS, None),
        ('Why does diskpart on a SaaS outage fail on purpose?', 'It is a wrong-domain, destructive fix', 'diskpart cannot reach the cloud', 'SaaS disks need tenant admin rights',
         'A tenant outage is not a disk problem; wiping a disk is destructive and wrong-domain.', CROSS, TOOLFIRST),
        ('Which pair is matched correctly?', 'MEM beep → hw-board', 'MEM beep → win-dns-break', 'Name fail → hw-board',
         'Beeps go to hardware; name failures go to DNS drills.', CROSS, None),
    ],
        _P('There are two practice drills. A memory beep at power-on means stay at the hardware stage and use the hw-board lab. A name that fails '
           'after the address path works means use win-dns-break or the full triage lab. Running diskpart during a cloud-service outage fails the '
           'pass bar on purpose, because it is the wrong fix in the wrong place.'),
        _P('A town has a fire crew and a flood crew. If the river bursts its banks, sending the fire engine to hose the street makes things worse. '
           'If a house is burning, the pumps that drain water are no help. The skill is matching the crew to the emergency. The two drills train '
           'that match: hardware beeps go to the hardware crew, name failures to the DNS crew, and nobody brings diskpart to a cloud outage.'),
        ['Hear the symptom.', 'Beep at power-on → hw-board (POST).', 'Name fails, IP works → win-dns-break or full triage.', 'Never use a destructive fix in the wrong domain.'],
        '<p>Sort each symptom into its drill.</p>',
        sort('Which drill?', {'hw-board': ['Memory beep at power-on', 'No POST, fans spin'], 'win-dns-break': ['Name fails, IP works', 'nslookup times out']},
             'Match the drill to the fault domain.'), ('hw-board', 'Diagnose a memory beep without leaving POST.')),
})

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '7.1': {'start-here-why-a-method-exists': '4162bcc5b0e6', 'core-content': '8bf5d2f53eba', 'cheap-tests-first': '05b0b4fae80b', 'teach-block-process-on-a-live-sentence': 'aa4fe500b0b2'},
    '7.2': {'core-content': '788c7e9d4ffb'},
    '7.3': {'core-content': 'db998f156c90'},
    '7.4': {'core-content': 'f95487361aee', 'two-drills': '40c320f8e917'},
}
