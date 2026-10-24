"""Option B pass 2 — ITSUP chapter 7 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

FIXF, TRUST, MANY, CROSS = 'MC-IT7-FIX-BEFORE-IDENTIFY', 'MC-IT7-TRUST-USER-DIAGNOSIS', 'MC-IT7-MANY-CHANGES', 'MC-IT7-CROSS-DOMAIN'
CLOSED, GUESS, ORDER, DSCOPE = 'MC-IT7-CLOSED-AS-VERIFIED', 'MC-IT7-GUESS-AS-FACT', 'MC-C-IT7-METHOD-ORDER', 'MC-C-IT7-DOMAIN-SCOPE'
NOVER, THIN, CONTEXT, CONFIRMS = 'MC-C-IT7-NO-VERIFY', 'MC-C-IT7-THIN-ESCALATION', 'MC-R3-IT7-CONTEXT-OPTIONAL', 'MC-L-IT7-TEST-CONFIRMS-ONLY'
TOOLF = 'MC-L-IT7-TOOL-FIRST'
METH = ('ticket-method', 'Work one ticket through all seven steps and write action → result at each.')
TRI = ('win-full-triage', 'Stay in one fault domain until a test result moves you to the next.')
INT = ('ticket-intake', 'Write a hand-off whose last line names a person or a command.')


def _s(n, t):
    return f'Course lesson 7.{n} “{t}” (the original section), re-explained'


S1, S2, S3 = _s(1, 'Troubleshooting Method'), _s(2, 'Fault Domains'), _s(3, 'Notes and Hand-offs')
SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


_add('7.1', '1-the-order', '1. The order', 'IT-7.1', S1, [
    ('Which step includes a safety stop?', 'Identify', 'Document', 'Verify the outcome',
     'Identify covers who, what outcome, how many, and any safety stop.', ORDER, FIXF),
    ('What makes a good test?', 'It can kill a theory', 'It confirms your hunch', 'It changes several things',
     'The cheapest test that could prove a theory wrong is the one to run.', CONFIRMS, MANY),
    ('In the recipe story, what is “taste before serving”?', 'Verify', 'Plan', 'Probable cause',
     'Tasting checks the real outcome, like verifying with the user.', NOVER, ORDER),
    ('In the flow, what comes right after Plan?', 'Change one thing', 'Document it', 'Identify the user',
     'Plan includes the undo; then you change exactly one thing.', MANY, ORDER),
    ('What does Verify check?', 'The user’s outcome', 'A green icon only', 'That the timer expired',
     'A green icon is not the user outcome; check that the user can do the task.', CLOSED, CLOSED),
],
    (['There are seven steps.', 'Identify who, what, how many, and any danger.', 'List a few likely causes.', 'Run the cheapest test that could rule one out.',
      'Plan the fix and how to undo it.', 'Change one thing.', 'Check the user can work again.', 'Write action and result.'],
     'Walk all seven steps in order, and verify with the user, not an icon.'),
    ('A cook with a flat cake reads the order slip, lists likely causes, does a quick test such as checking the baking powder date, '
     'plans one change, bakes once, tastes, and writes it in the kitchen book.',
     [('Reading the order slip', 'Identify'), ('Likely causes', 'Probable cause'), ('Checking the powder date', 'Cheapest test'),
      ('Plan one change', 'Plan with undo'), ('Bake once', 'Change one thing'), ('Taste', 'Verify the user outcome'), ('Kitchen book', 'Document')],
     'A cook can bake another cake; some IT changes cannot be undone, which is why the plan must include the way back.'),
    ('flow', 'The seven steps', ['Identify', 'Probable cause', 'Test', 'Plan + undo', 'Change one', 'Verify', 'Document']),
     'Never skip a box. The test box is about killing a theory, and the verify box is about the user, not a status light.',
    'Order the seven steps, then work one ticket in the method lab.',
    order('The method', ['Identify', 'Probable cause', 'Test', 'Plan with undo', 'Change one thing', 'Verify the user outcome', 'Document'],
          'Each step depends on the one before.'), METH)

_add('7.1', 'the-seven-words', 'The seven words', 'IT-7.1', S1, [
    ('The user says “it’s DNS”. Is that Identify?', 'No, it is a claim', 'Yes, it is complete', 'Yes, users know best',
     'Identify is your own who, what, how many and safety check.', TRUST, TRUST),
    ('Which test should come first?', 'The cheapest killer test', 'The longest full scan', 'The test you like the most',
     'Pick the cheapest test that can rule out a theory.', CONFIRMS, TOOLF),
    ('In the detective story, what is the suspect’s alibi check?', 'A test', 'A plan', 'The document',
     'Checking an alibi can clear a suspect, like a test kills a theory.', CONFIRMS, ORDER),
    ('In the arrow chain, what is the last word?', 'Document', 'Verify', 'Change one thing',
     'The chain ends with documenting action → result.', ORDER, ORDER),
    ('Which word means “one at a time”?', 'Change one thing', 'Probable cause', 'Identify the user',
     'Change one thing keeps cause and effect clear.', MANY, MANY),
],
    (['Remember seven words.', 'Identify.', 'Cause.', 'Test.', 'Plan.', 'Change one thing.', 'Verify.', 'Document.',
      'A user who says “it’s DNS” has not identified anything.', 'You still ask who, what, how many and is it safe.'],
     'The user’s guess is a clue, not the Identify step.'),
    ('A detective hears a witness say “the butler did it”. That is a lead, not a finding. The detective still notes who was there and '
     'what happened, lists suspects, and checks the quickest alibi first. One alibi check can clear a suspect in minutes.',
     [('Witness says the butler did it', 'User says “it’s DNS”'), ('Noting who and what', 'Identify'), ('List of suspects', 'Probable causes'),
      ('Quick alibi check', 'Cheapest test that kills a theory')],
     'Detectives can interview suspects; your theories cannot talk, so the test must be one that could clearly fail.'),
    ('flow', 'Seven words', ['Identify', 'Cause', 'Test', 'Plan', 'Change one', 'Verify', 'Document']),
     'The words are short so you can say them under pressure. The user’s own diagnosis is not a box on this chain.',
    'Reveal the answer after you decide what Identify should contain.',
    reveal('A user rings: “Teams is broken, it’s DNS.” Write the Identify line.',
           '“Who: J. Doe, CIWT-W11-07. Outcome: cannot join Teams calls since 09:10. How many: one user so far. Safety: none.”'), METH)

_add('7.2', '1-domains-you-already-know', '1. Domains you already know', 'IT-7.2', S2, [
    ('Shock, heat or smell. Which domain?', 'Safety: stop', 'Display after POST', 'Name resolution',
     'Safety comes first and means stop.', CROSS, DSCOPE),
    ('Ping IP works, name fails. Which domain?', 'Name', 'Address', 'Power / POST',
     'An IP that works with a name that fails is a name problem.', CROSS, CROSS),
    ('In the hospital story, what is the ward?', 'A fault domain', 'A test command', 'The user’s desk',
     'Each ward handles one kind of problem, as each domain has its own first tests.', DSCOPE, DSCOPE),
    ('In the table, what is the first test for Address?', 'ipconfig, not 169.254', 'Wall, cables, beeps', 'About and then list disk',
     'Address starts with ipconfig and checking for APIPA.', CROSS, TOOLF),
    ('LAN fine, the whole tenant is down. Which domain?', 'Vendor / SaaS', 'OS / disk', 'Display after POST',
     'A tenant-wide outage with a healthy LAN is the vendor’s domain.', DSCOPE, CROSS),
],
    (['Most problems belong to one of seven areas you have met before.', 'If someone feels a shock or smells burning, everyone stops.',
      'If nothing lights up, think power first.', 'If the screen is dark after a good start, think screen path.',
      'If Windows or a drive is the issue, read the system page.', 'If the PC has no proper address, think addressing.',
      'If numbers work but names do not, think names.', 'If the whole company app is down, think supplier.'],
     'Name the domain first, then use that domain’s first test.'),
    ('A hospital has wards: emergency, heart, bones, eyes. A patient with a broken arm goes to bones, not eyes. Each ward has its own '
     'first checks. Anyone in danger goes to emergency first.',
     [('Wards', 'Fault domains'), ('Emergency ward', 'Safety: stop'), ('Ward’s first checks', 'Domain’s first tests'),
      ('Sending an arm to the eye ward', 'Using a tool from the wrong domain')],
     'Patients can have two injuries at once; tickets can too, but you still work one domain at a time.'),
    ('two', 'Domains and first tests', (('Domain', ['Safety', 'Power / POST', 'Display', 'OS / disk', 'Address', 'Name', 'Vendor']),
                                         ('First test', ['Stop', 'Wall, cables, beeps', 'Cable/input after POST', 'About, list disk', 'ipconfig', 'Ping IP vs name', 'Status page']))),
     'Read each row across. Picking the wrong row means running tests that cannot answer your question.',
    'Sort each symptom into its domain, then work the triage lab inside one domain.',
    sort('Which domain?', {'Safety': ['Burning smell from the PSU'], 'Address': ['ipconfig shows 169.254'], 'Name': ['Ping IP works, name fails'],
                           'Vendor / SaaS': ['Whole tenant mail down, LAN fine']}, 'The domain picks the first test.'), TRI)

_add('7.2', 'fault-domains-you-already-know', 'Fault domains you already know', 'IT-7.2', S2, [
    ('Tenant mail is down. Should you format a disk?', 'No, wrong domain', 'Yes, start with one', 'Yes, it often helps',
     'Formatting a disk for a tenant outage is crossing domains.', CROSS, CROSS),
    ('When do you leave a domain?', 'When evidence moves you', 'After ten minutes', 'When you start to feel stuck',
     'Stay until a test result points to another domain.', DSCOPE, NOVER),
    ('In the neighbourhood story, what is the street you search?', 'One fault domain', 'The whole city', 'The user’s own home',
     'Search one street fully before moving, like one domain at a time.', DSCOPE, CROSS),
    ('In the picture, which arrow is the mistake?', 'Tenant down → format', 'APIPA → check DHCP', 'Beeps → check the RAM',
     'Formatting for a tenant outage jumps domains.', CROSS, CROSS),
    ('Which domain list is complete?', 'Safety to Vendor, seven', 'Only Address and Name', 'Power and Display, nothing else',
     'The seven domains run from Safety to Vendor/SaaS.', DSCOPE, DSCOPE),
],
    (['Think of the seven areas as neighbourhoods.', 'Work inside one at a time.', 'Move only when a test result sends you.',
      'A mail outage for the whole tenant is the vendor area.', 'Formatting a disk is the OS area.', 'Doing that for mail is crossing areas.', 'It fixes nothing.'],
     'Stay in one domain until evidence moves you; never jump to a fix in another.'),
    ('Looking for a lost cat, you search one street thoroughly before moving to the next. You do not dig up the park because a '
     'neighbour three streets away heard a meow. You move when you find a real sign.',
     [('Street', 'Fault domain'), ('Searching thoroughly', 'Running that domain’s tests'), ('A real sign', 'Evidence that moves you'),
      ('Digging up the park', 'Formatting a disk for a tenant outage')],
     'Cats wander between streets; faults do not, so a clean test result really does clear a domain for now.'),
    ('flow', 'Move only on evidence', ['Pick a domain', 'Run its tests', 'Result points elsewhere?', 'Move one domain', 'Repeat']),
     'Leaving a domain needs a result. A hunch or a long wait is not on this chart.',
    'Sort each move as allowed or not, then try it in the triage lab.',
    sort('Good move?', {'Allowed': ['APIPA found → work DHCP', 'Name fails, IP works → check DNS'],
                        'Crossing domains': ['Tenant mail down → format disk', 'Beep codes → reinstall Windows']}, 'Evidence moves you.'), TRI)

_add('7.3', 'handoff', 'Handoff', 'IT-7.3', S3, [
    ('A hand-off leaves out the tests. What happens?', 'The next person restarts', 'Nothing, it saves time', 'The ticket closes itself',
     'Without tests, the next technician starts from zero.', CONTEXT, THIN),
    ('What should the last line name?', 'A person or command', '“Look into it”', 'Your lunch break time',
     'The last line says exactly who acts next or which command to run.', THIN, CONTEXT),
    ('In the relay story, what is the baton?', 'The hand-off note', 'The finish line', 'The stadium itself',
     'The baton carries everything to the next runner.', CONTEXT, CONTEXT),
    ('In the note picture, how is a guess marked?', 'Labelled “guess”', 'Written as a fact', 'Left out entirely',
     'Guesses stay labelled so nobody acts on them as facts.', GUESS, GUESS),
    ('Which last line passes?', 'Next: DNS owner, ticket 4471', 'Next: look into it', 'Next: maybe check some more stuff',
     'It names a person and a reference, not a vague task.', THIN, THIN),
],
    (['A hand-off passes the ticket to someone else.', 'List the tests you ran.', 'Give their results.', 'Mark guesses as guesses.',
      'End with a person or a command.', 'Never end with “look into it”.'],
     'Tests, results, labelled guesses, and a last line that names who or what is next.'),
    ('In a relay race, a runner hands over the baton cleanly and shouts “go”. Dropping it means the next runner starts from the back. '
     'The coach labels any guess about the other teams as a guess.',
     [('Baton', 'Hand-off note'), ('Clean handover', 'Tests and results included'), ('Shouting “go”', 'Last line names a person or command'),
      ('Coach’s guess', 'Labelled guess, not a fact')],
     'A dropped baton is seen by everyone; a thin note looks fine until the next person tries to use it at 0200.'),
    ('flow', 'A hand-off that works', ['Tests run', 'Results', 'Guesses labelled', 'Next: person or command']),
     'Every box is required. Missing the first one sends the next person back to zero.',
    'Order the note parts, then write a hand-off in the intake lab.',
    order('Hand-off note', ['Tests run', 'Results with values', 'Guesses labelled', 'Next: a named person or command'],
          'The last line is never “look into it”.'), INT)
