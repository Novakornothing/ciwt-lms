"""Option B pass 2 — ITSUP chapter 10 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

SHADM, PWREC, BROAD, DISP = 'MC-IT10-SHARED-ADMIN', 'MC-IT10-PASSWORD-RECORDED', 'MC-IT10-BROAD-PRIVILEGE', 'MC-IT10-DISABLE-PROTECTION'
COMPREQ, DISDEF, SOLO = 'MC-IT10-COMPROMISE-AS-REQUEST', 'MC-IT10-DISABLE-DEFENDER', 'MC-IT10-SOLO-RESPONDER'
UNDER, EVID, WEAK, MORDER = 'MC-R3-IT10-COMPROMISE-UNDERPLAYED', 'MC-R3-IT10-EVIDENCE-LATER', 'MC-R3-IT10-WEAKEN-CONTROLS', 'MC-C-IT10-MALWARE-ORDER'
TRUSTLAN, FWD = 'MC-C-IT10-TRUST-LAN', 'MC-L-IT10-FORWARD-PHISH'
LMW = ('sec-malware', 'Contain a suspected malware PC and write the incident note without disabling Defender.')
LACC = ('gui-accounts', 'Check who is signed in and whether that account needs admin rights.')
LUP = ('gui-update', 'Read the update state as part of describing the box.')
LINT = ('ticket-intake', 'Classify the phish report and write the note without any password.')


def _s(n, t):
    return f'Course lesson 10.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4 = _s(1, 'Security Controls'), _s(2, 'Malware Response'), _s(3, 'Endpoint Hygiene'), _s(4, 'Phishing Follow-up')
SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


_add('10.1', 'daily-controls', 'Daily controls', 'IT-10.1', S1, [
    ('What is wrong with a shared admin password on a monitor?', 'Nobody is accountable', 'It is too long to type', 'It fades in sunlight',
     'Shared, visible admin passwords give privilege nobody can trace.', SHADM, SHADM),
    ('What happens to the firewall profile?', 'It stays on', 'Off when busy', 'Off for admins',
     'The firewall profile stays on as a daily control.', DISP, DISP),
    ('In the office-key story, what is a personal key?', 'Your own sign-in', 'A shared admin code', 'An open front door',
     'A personal key records who entered, like your own account.', SHADM, TRUSTLAN),
    ('In the picture, which is a daily control?', 'Screen lock', 'Shared admin', 'Firewall off',
     'Screen lock is a daily control; the others weaken security.', SHADM, DISP),
    ('Least privilege means…', 'Only the rights needed', 'Admin for everyone', 'No passwords at all needed',
     'Give each account only what its job needs.', BROAD, BROAD),
],
    (['Wear your badge.', 'Lock your screen when you walk away.', 'Use only the rights you need.', 'Know who is signed in.', 'Keep the firewall on.',
      'A shared admin password on a sticky note is a problem.', 'Nobody can tell who used it.'],
     'Badge, screen lock, least privilege, known user, firewall on, and no shared admin passwords.'),
    ('In an office, everyone has their own key card, so the door log shows who came in. Doors close behind you. A master key taped to '
     'reception would open everything, and nobody could say who used it.',
     [('Own key card', 'Personal sign-in'), ('Door closing behind you', 'Screen lock'), ('Rooms you are allowed in', 'Least privilege'),
      ('Master key taped to reception', 'Shared admin password on a monitor'), ('Alarm left on', 'Firewall profile on')],
     'A taped key can be seen and removed; a shared password may already be copied, so it must also be changed.'),
    ('two', 'Daily controls versus bad habits', (('Daily controls', ['Badge and screen lock', 'Least privilege', 'Firewall on']),
                                                 ('Bad habits', ['Shared admin on a monitor', 'Admin for convenience', 'Firewall off']))),
     'Every item on the left has a twin on the right that undoes it. Spotting the right-column habit is part of every visit.',
    'Sort each habit, then check who is signed in using the accounts lab.',
    sort('Control or bad habit?', {'Control': ['Screen locks when away', 'Firewall profile on', 'User has only needed rights'],
                                   'Bad habit': ['Admin password on a sticky note', 'Everyone shares one admin account']}, 'Accountability matters.'), LACC)

_add('10.2', 'malware-is-an-incident', 'Malware is an incident', 'IT-10.2', S2, [
    ('Suspected malware. What do you follow?', 'Shop containment process', 'Any free cleaner', 'Your own instinct and tools',
     'Contain per shop process; random cleaners are not incident response.', SOLO, MORDER),
    ('A “tool” needs Defender off. What do you do?', 'Refuse, keep it on', 'Turn it off briefly', 'Turn it off for good',
     'Never disable Defender to let a tool run.', DISDEF, DISDEF),
    ('In the fire story, who is the fire service?', 'The IR owner', 'The first technician', 'The affected user',
     'You raise the alarm and hand over; the IR owner leads, like the fire service.', SOLO, SOLO),
    ('In the flow, what follows “write facts”?', 'Escalate to IR owner', 'Run a USB cleaner', 'Wipe the PC straight away',
     'After writing facts, escalate to the incident response owner.', SOLO, EVID),
    ('Who are you in an incident?', 'Support, not all of IR', 'The whole IR team', 'A bystander with no role',
     'You support and hand off; you are not the whole IR team.', SOLO, UNDER),
],
    (['Malware is an incident, not a chore.', 'Follow the shop’s plan to contain it.', 'Do not run random cleaners.', 'Do not turn Defender off for any tool.',
      'Write down the facts.', 'Pass it to the incident owner.', 'You are support, not the whole team.'],
     'Contain by process, write facts, hand off; never disable Defender or freelance with cleaners.'),
    ('If you smell smoke at work, you follow the fire plan, pull the alarm and tell the fire officer what you saw. You do not fight '
     'the fire with a bottle of cola or switch off the smoke detectors to stop the noise.',
     [('Fire plan', 'Shop containment process'), ('Telling the fire officer what you saw', 'Writing facts and escalating'),
      ('Bottle of cola', 'A random cleaner'), ('Switching off detectors', 'Disabling Defender'), ('Fire officer', 'IR owner')],
     'Smoke is obvious; malware may be quiet, so you raise the alarm on signs, not only on certainty.'),
    ('flow', 'Malware incident path', ['Contain per process', 'Defender stays on', 'Write facts', 'Escalate to IR owner']),
     'There is no cleaner box and no wipe box on this chart. Your part ends at the escalation, with good facts.',
    'Order the steps, then work the malware lab with Defender on.',
    order('Malware response', ['Contain per shop process', 'Keep Defender on', 'Write the facts', 'Escalate to the IR owner'],
          'You are support, not the whole IR team.'), LMW)

_add('10.2', 'containment-without-heroics', 'Containment without heroics', 'IT-10.2', S2, [
    ('When may you isolate on the wire?', 'If shop process says so', 'Whenever you like', 'Never, under any circumstances',
     'Isolation follows the shop process.', SOLO, SOLO),
    ('Is a USB cleaner incident response?', 'No', 'Yes', 'Sometimes',
     'A USB cleaner is not IR and can destroy evidence.', EVID, EVID),
    ('In the quarantine story, what is closing the ward door?', 'Isolating the PC', 'Curing the patient', 'Sending them home',
     'Closing the door stops spread without treating, like isolation.', SOLO, EVID),
    ('In the picture, what are the three jobs?', 'Isolate, document, hand off', 'Clean, wipe and close', 'Ignore, wait, then reboot it',
     'Your job is isolate, document, hand off.', SOLO, UNDER),
    ('Why no heroics?', 'They destroy evidence', 'They take too long', 'They look untidy in notes',
     'Heroic cleaning can wipe the evidence the IR team needs.', EVID, EVID),
],
    (['Your job has three parts.', 'Isolate the PC if the process says so.', 'Write down what you saw.', 'Hand it to the incident team.',
      'Do not play hero with a USB cleaner.', 'That can destroy the evidence.'],
     'Isolate, document, hand off; leave cleaning to the incident team.'),
    ('In a hospital, a nurse who suspects something catching closes the ward door and calls the infection team. The nurse does not '
     'try an untested cure from a pocket. The infection team needs to see the patient as they are.',
     [('Closing the ward door', 'Isolating on the wire'), ('Calling the infection team', 'Handing off to IR'), ('Untested pocket cure', 'USB cleaner'),
      ('Patient as they are', 'Evidence preserved')],
     'A ward door is physical; isolation may mean a cable pulled or a switch port disabled, and the shop process says which.'),
    ('flow', 'Three jobs, no heroics', ['Isolate (per process)', 'Document', 'Hand off']),
     'Three boxes only. A cleaner, a wipe or a reinstall would be a fourth box, and that box belongs to the incident team.',
    'Sort each action, then practise containment in the malware lab.',
    sort('Your job or theirs?', {'Your job': ['Isolate per process', 'Write what you saw', 'Hand off to IR'],
                                 'IR team’s job': ['Remove the malware', 'Decide on a reimage']}, 'Isolate, document, hand off.'), LMW)

_add('10.3', 'hygiene', 'Hygiene', 'IT-10.3', S3, [
    ('What should Defender show?', 'Running', 'Paused', 'Uninstalled',
     'Defender Running is part of hygiene.', DISP, DISP),
    ('Is patch state part of describing the box?', 'Yes, always', 'No, never', 'Only on servers',
     'Patch state describes the box like its name and address.', DISP, DISP),
    ('In the kitchen story, what is the fridge thermometer?', 'Defender status', 'The ticket form', 'A password note',
     'A quick look tells you protection is working, like the thermometer.', DISP, PWREC),
    ('In the picture, what must never be in a ticket?', 'Secrets', 'Update state', 'Defender state',
     'No passwords or secrets go in tickets.', PWREC, PWREC),
    ('Update history shows failures. Hygiene?', 'Record it', 'Ignore it', 'Turn Update off',
     'Reading and recording update state is hygiene.', DISP, DISP),
],
    (['Check that Defender is running.', 'Read the update state.', 'Keep secrets out of tickets.', 'Patch state describes the PC.',
      'Write it down like the name and address.', 'A missing patch is a fact, not a guess.'],
     'Defender running, updates read, no secrets in tickets, patch state recorded.'),
    ('A clean kitchen has a fridge at the right temperature, food rotated by date, and no keys left on the counter. A food inspector '
     'writes the fridge temperature on the report as part of describing the kitchen.',
     [('Fridge at the right temperature', 'Defender running'), ('Food rotated by date', 'Updates read and applied'),
      ('No keys on the counter', 'No secrets in tickets'), ('Temperature on the report', 'Patch state in the description')],
     'A fridge temperature is easy to read; update state may need the history page, so open it rather than assuming.'),
    ('two', 'Hygiene check', (('Check and record', ['Defender: Running', 'Update state read', 'Patch level noted']), ('Never record', ['Passwords', 'Recovery keys', 'Secrets']))),
     'The left column belongs in every description of the box. The right column never goes in a ticket.',
    'Sort each item, then read the update state in the lab.',
    sort('Record or never?', {'Record': ['Defender running', 'Last update result'], 'Never record': ['User password', 'BitLocker recovery key']},
         'Patch state is part of the description.'), LUP)

_add('10.4', 'phish-follow-up', 'Phish follow-up', 'IT-10.4', S4, [
    ('User reported a phish but did not open it. Response?', 'Record it, no shame', 'Scold the user', 'Ignore the report entirely',
     'Record, confirm no credentials, and thank them; no shame.', UNDER, UNDER),
    ('User typed their password into the page. What is it?', 'An incident and reset', 'Just a request', 'Nothing to worry about now',
     'Typed credentials mean an incident plus an approved reset.', COMPREQ, UNDER),
    ('In the lost-key story, what is changing the lock?', 'The approved reset', 'Writing down the key', 'Ignoring it for now',
     'If someone may have copied your key, you change the lock.', PWREC, UNDER),
    ('In the flow, what must never be in the ticket?', 'The password', 'The time', 'The sender’s name',
     'Never put the password in the ticket.', PWREC, PWREC),
    ('What do you confirm when nothing was opened?', 'No credentials typed', 'Their bank details', 'Their full home address',
     'Confirm no credentials were entered.', COMPREQ, COMPREQ),
],
    (['There are two common outcomes.', 'The user did not open it.', 'Then record it, thank them and confirm no password was typed.',
      'Or the user typed a password.', 'Then it is an incident.', 'Arrange an approved reset.', 'Never write the password in the ticket.'],
     'Not opened: record and reassure. Password typed: incident plus approved reset. Never record the password.'),
    ('If you see a stranger near your door, you note it and check the door is locked. If you think a stranger copied your key, you '
     'call the landlord and change the lock. You never write the key code on the report.',
     [('Stranger seen, door locked', 'Phish not opened'), ('Key may be copied', 'Password typed'), ('Changing the lock', 'Approved reset'),
      ('Key code on the report', 'Password in the ticket')],
     'A lock change is visible; a password reset must also end other sign-ins, so the approved process matters.'),
    ('two', 'Two outcomes', (('Not opened', ['Record, no shame', 'Confirm no credentials']), ('Password typed', ['Incident raised', 'Approved reset', 'Never record password']))),
     'Decide which column you are in from the user’s answer. Both columns keep the password out of the ticket.',
    'Sort each step, then write a phish note in the intake lab.',
    sort('Which outcome?', {'Not opened': ['Record the report', 'Confirm no password typed'], 'Password typed': ['Raise an incident', 'Arrange approved reset']},
         'The password never goes in the ticket.'), LINT)
