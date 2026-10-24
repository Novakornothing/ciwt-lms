"""Option B pass 3 — NETOPS chapter 6 bespoke ladders (pattern library, method under pressure, verification and
documentation, full capstone). Pending SME review."""
from curriculum_v2.ladder.netops._p3 import N, mc, src
from curriculum_v2.ladder.schema import order, reveal, sort

SECS = {}
PAT, IFS, ESCF, SIL = 'MC-L-NO6-PATTERN-MIX', 'MC-L-NO6-IF-STATE', 'MC-L-NO6-ESCALATE-FAIL', 'MC-L-NO6-SILENT-CHANGE'
SCOPEI, SHOT, PROM, ALERT, DOCS, PMTU, TBOX, ATTR = (
    'MC-NO6-SCOPE-IGNORED', 'MC-NO6-SHOTGUN', 'MC-NO6-STATUS-PROMISE', 'MC-NO6-ALERT-CLEARED', 'MC-NO6-DOCS-OPTIONAL',
    'MC-R3-NO6-PMTUD', 'MC-R3-NO6-TIMEBOX', 'MC-R3-NO6-ATTRIBUTION')
INT = ('sw-int-status', 'Read show interfaces status and match each port state to a known fault pattern.')
TM = ('ticket-method', 'Work the ticket in method order and write one line per step with a time.')
TRI = ('win-full-triage', 'Run the full triage, then verify with the user’s real task and write the root cause.')


def _add(label, sid, title, *a):
    SECS[(label, sid)] = N(label, sid, src(label, title), *a)


# ================================================================== 6.1 Pattern Library
m = mc('6.1')
T = 'Pattern Library'
_add('6.1', 'core-concepts', T, [
    ('One desk slow, late collisions on its port. Pattern?', 'Duplex mismatch', 'A DNS server outage for all', 'Full DHCP scope',
     'Late collisions on one link are the duplex mismatch signature.', PAT, IFS),
    ('Small pings work, large transfers hang. Pattern?', 'MTU black hole', 'A wrong VLAN on the port', 'DNS',
     'Small works, large fails is the PMTUD black-hole pattern.', PMTU, PAT),
    ('In the triage-card story, the card does what?', 'Matches signs to tests', 'Replaces the doctor fully', 'Nothing',
     'Triage cards map a pattern to first tests.', PAT, m('RECALL')),
    ('In the chart, “IP works, name fails” matches?', 'DNS', 'Duplex mismatch', 'Wi-Fi overlap',
     'That signature belongs to DNS.', PAT, PAT),
    ('Port shows err-disabled. What is it?', 'A protection shutdown', 'A cable that is broken', 'Admin down',
     'Err-disabled means a protection feature shut the port.', IFS, IFS),
], ([
    'Many faults have a signature.',
    'Duplex mismatch: one link slow with late collisions.',
    'VLAN: green light but isolated.',
    'DHCP: 169.254 addresses.',
    'DNS: IP works, names fail.',
    'Wi-Fi overlap: good signal, many retries.',
    'Matching the pattern speeds up your first tests.',
], 'Learn the signatures; they point to the first test.'), (
    'Emergency nurses use triage cards: “chest pain plus sweating” points to heart tests first. The cards do not replace '
    'diagnosis; they choose the first tests. A pattern library does the same for network faults.',
    [('Triage card', 'fault pattern'), ('Symptoms on the card', 'signature'), ('First tests listed', 'first checks'), ('Doctor’s diagnosis', 'proven root cause')],
    'Triage cards are tested on thousands of patients. Your patterns are a starting point; you still prove the cause.'),
    ('two', 'Signature to pattern', (('Signature', ['Late collisions', 'Green light, isolated', 'IP OK, name fails', 'Small OK, large hangs']),
                                     ('Pattern', ['Duplex mismatch', 'Wrong VLAN', 'DNS', 'MTU black hole']))),
    'Each row pairs a signature with its usual pattern. Use it to choose the first test, then prove it.',
    'In the interface lab, read show interfaces status and match each port state to a pattern.',
    sort('Sort each signature.', {'Layer 1–2': ['Late collisions', 'Err-disabled port'], 'Layer 3+': ['169.254 address', 'NXDOMAIN']},
         'Patterns point to layers.'), INT)

_add('6.1', 'incident-application', T, [
    ('A desk’s file copies crawl; its port shows late collisions. First test?', 'Compare duplex', 'Reimage the desk PC first',
     'Flush DNS', 'Check speed and duplex on both ends.', PAT, m('PARALLEL')),
    ('The switch side shows full duplex. Record it?', 'Yes, with time', 'No, only the PC side matters here', 'Skip',
     'Each side’s setting is evidence.', m('NEG'), m('NEG')),
    ('In the dance story, one partner out of step is?', 'Duplex mismatch', 'A broken dance floor', 'Music',
     'Two partners on different counts trip each other.', PAT, IFS),
    ('In the timeline, what proved the cause?', 'Half vs full', 'A user’s guess at 11:01', 'Reboot',
     'One side half, the other full, with late collisions.', PAT, m('PARALLEL')),
    ('Good status line?', 'Duplex mismatch; fixing', 'Network is broken all over', 'Fine',
     'Calm, specific, with action.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking pattern incident.',
    'At 11:00 one desk’s file copies crawl.',
    'The port shows late collisions.',
    'The switch side is full duplex.',
    'The PC side was forced to half.',
    'You set both to auto and retest.',
    'Copies run at full speed again.',
], 'Match the signature, prove both sides, make one change.'), (
    'Two dancers on different counts keep stepping on each other. The floor is fine; the timing is not. A duplex mismatch '
    'is two ends of a link on different timing rules.',
    [('Dancer A', 'switch port'), ('Dancer B', 'PC network card'), ('Different counts', 'half vs full duplex'), ('Stepped-on toes', 'late collisions')],
    'Dancers can talk and agree. Network cards only agree if both use auto-negotiation.'),
    ('flow', 'Duplex timeline', ['11:00 copies slow', '11:03 late collisions', '11:05 switch full', '11:06 PC half', '11:10 both auto'], 3),
    'The red box is the proof: the two sides disagree.',
    'Write a timeline for a slow desk with late collisions on its port.',
    order('Order the steps.', ['Spot the signature', 'Read switch side', 'Read PC side', 'Set both auto', 'Retest copy'], 'Both ends, then fix.'), INT)

_add('6.1', 'standard-of-work', T, [
    ('Cable tested fine. Record it?', 'Yes, rules it out', 'No, nothing was found wrong', 'Skip',
     'It rules out a physical cause.', m('NEG'), m('NEG')),
    ('Changing duplex and swapping the cable together is…', 'Untracked change', 'A quick double fix for speed', 'Required',
     'Two changes hide which pattern was real.', m('PARALLEL'), SHOT),
    ('In the doctor story, one medicine at a time is?', 'One change per test', 'Every pill in the box at once', 'No notes',
     'One change, observe, note.', SHOT, m('NEG')),
    ('In the chart, which is “avoid”?', 'Two fixes at once', 'Note that the cable is OK', 'Retest',
     'Shotgun fixes hide cause.', SHOT, m('NEG')),
    ('Which line meets the standard?', 'Gi0/5 auto/auto 11:10', 'Fixed the speed thing', 'OK',
     'Port, setting, time.', m('NEG'), m('CHECKLIST')),
], ([
    'Pattern work has two habits.',
    'Write down tests that passed, like a good cable.',
    'That rules out other patterns.',
    'Make one change at a time.',
    'Do not change duplex and cable together.',
], 'Record ruled-out patterns and change one thing.'), (
    'A doctor treating a rash tries one cream, waits and notes the result. Three creams at once may help, but the doctor '
    'learns nothing. Fixing two patterns at once teaches nothing either.',
    [('Cream', 'one change'), ('Waiting to see', 'retest'), ('Three creams', 'shotgun fix'), ('Patient notes', 'ticket')],
    'Skin heals slowly. Networks change instantly, so the retest can be immediate.'),
    ('two', 'Pattern standard of work', (('Do', ['Note cable OK', 'One setting change', 'Retest']),
                                         ('Avoid', ['Skipping ruled-out tests', 'Two fixes at once', 'No retest']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “fixed the speed thing” as a standard line with port, setting, time and retest.',
    reveal('Rewrite: “fixed the speed thing”.', '11:10 Gi0/5 and PC NIC set auto/auto; copy 110 MB/s 11:12.'), INT)

_add('6.1', 'practice-standard-for-this-lesson', T, [
    ('First line on a pattern checklist?', 'Name the signature', 'Reboot everything in sight', 'Guess',
     'Name what you observe first.', PAT, SHOT),
    ('Pass sign for “pattern matched”?', 'Proof test agrees', 'It feels about right', 'Any',
     'A pattern is a guess until a test agrees.', PAT, m('CHECKLIST')),
    ('In the field-guide story, the fail note is?', 'What to write if it fails', 'The colour of the guide’s cover', 'Price',
     'Every step needs a failure note.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “pattern guess”?', 'Proof test', 'Close the ticket at once', 'Reboot',
     'Prove it before fixing.', PAT, ALERT),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every pattern name', 'Read',
     'Explain patterns plainly, then prove one.', m('RECALL'), m('JARGON')),
], ([
    'Explain fault patterns without notes.',
    'Then prove one in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start by naming the signature.',
    'Then run a test that proves the pattern.',
    'Each step has a pass sign and a fail note.',
], 'A pattern is a guess until a test proves it.'), (
    'A bird watcher uses a field guide: “red breast, small, garden” suggests a robin. She confirms with the song before '
    'writing it down. A pattern library is the field guide; the proof test is the song.',
    [('Field guide', 'pattern library'), ('Red breast', 'signature'), ('Song check', 'proof test'), ('Logbook', 'ticket')],
    'Birds do not change. Networks get new failure modes, so the library needs updates.'),
    ('flow', 'Pattern checklist', ['Name signature', 'Guess pattern', 'Proof test', 'One fix', 'Verify']),
    'These boxes outline the checklist from left to right. The proof test is what turns a guess into a cause.',
    'Write a five-line pattern checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Name signature', 'Guess pattern', 'Proof test', 'One fix', 'Verify'], 'Guess, prove, fix.'), INT)

_add('6.1', 'beyond-the-quiz', T, [
    ('What does a pattern library need to stay useful?', 'Updates after incidents', 'A thicker printed binder', 'Nothing',
     'New incidents add new signatures.', DOCS, m('RECALL')),
    ('Two patterns overlap. What can break?', 'Wrong first test', 'Every switch in the building', 'Nothing',
     'Similar signatures can send you to the wrong test.', PAT, m('RECALL')),
    ('In the lookalike story, twins are?', 'Overlapping patterns', 'Two broken cables in the wall', 'Mirrors',
     'Twins look alike; a second check tells them apart.', PAT, PAT),
    ('In the chart, which test splits MTU from DNS?', 'Large ping by IP', 'Reboot every PC first', 'Ask',
     'A large ping by IP fails for MTU but not for DNS.', PMTU, PAT),
    ('When do you escalate a pattern?', 'Time box passes', 'Never, keep going alone', 'At once',
     'Escalate when your time box runs out.', TBOX, ESCF),
], ([
    'A quiz cannot cover every pattern.',
    'Know what a library needs: updates after incidents.',
    'Know what breaks when patterns overlap.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Escalate when your time box runs out.',
], 'Patterns overlap; a deciding test keeps you honest.'), (
    'Identical twins look the same until you hear their voices. Some network faults are twins: MTU problems and DNS '
    'problems can both look like “the site will not load”. A deciding test is the voice.',
    [('Twins', 'overlapping patterns'), ('Voice', 'deciding test'), ('Family album', 'pattern library'), ('Name tag', 'proven cause')],
    'Twins stay twins. Network patterns can combine, so two faults may be present at once.'),
    ('two', 'Site will not load: three causes', (('Cause', ['DNS failure', 'MTU black hole', 'Firewall deny']),
                                                 ('Deciding test', ['nslookup', 'Large ping by IP', 'Port test']))),
    'Each cause has one test. Run them to split lookalikes.',
    'Write your own pattern scenario: symptom, three causes, deciding test, escalation note.',
    reveal('Small pings OK, large ping with DF set fails. Pattern?', 'MTU black hole (PMTUD blocked).'), INT)

# ================================================================== 6.2 Method Under Pressure
m = mc('6.2')
T = 'Method Under Pressure'
_add('6.2', 'core-concepts', T, [
    ('What comes first in the method?', 'Impact', 'Fix it immediately', 'Document',
     'Impact first: who and what is affected.', 'MC-C-NO6-METHOD-ORDER', SCOPEI),
    ('When do you communicate?', 'Before the fix', 'Only after it is fixed', 'Never',
     'Communicate after testing, before fixing.', PROM, 'MC-C-NO6-METHOD-ORDER'),
    ('In the pilot story, the checklist in turbulence is?', 'The method', 'The aircraft’s engine', 'Luck',
     'Pilots follow checklists when stressed.', 'MC-C-NO6-METHOD-ORDER', SHOT),
    ('In the chart, what comes after “fix”?', 'Verify', 'Close the ticket right away', 'Blame',
     'Verify, then document.', ALERT, DOCS),
    ('A VP demands an instant fix. You…', 'Keep the method', 'Reboot everything at once', 'Hide',
     'Pressure is when the method matters most.', SHOT, ESCF),
], ([
    'The method has seven steps.',
    'Impact, theory, test, communicate.',
    'Then fix, verify and document.',
    'Pressure makes people skip steps.',
    'Skipping steps causes new outages.',
    'Follow the order even when rushed.',
], 'Impact → theory → test → communicate → fix → verify → document, under any pressure.'), (
    'A calm pilot in turbulence still reads the checklist out loud. Panic makes people skip items; checklists stop that. '
    'Your seven-step method is the pilot’s checklist for an outage with a manager watching.',
    [('Turbulence', 'outage pressure'), ('Checklist', 'seven-step method'), ('Co-pilot reading aloud', 'ticket timeline'), ('Passengers', 'users')],
    'A pilot cannot pause the flight. You can take two minutes to plan, and it saves time.'),
    ('flow', 'The method', ['Impact', 'Theory', 'Test', 'Communicate', 'Fix', 'Verify', 'Document']),
    'Read the seven boxes from left to right. Communication sits before the fix, so stakeholders hear tested facts and a next update time, not promises.',
    'In the ticket lab, work a ticket in this order and write one line per step with a time.',
    order('Order the method.', ['Impact', 'Theory', 'Test', 'Communicate', 'Fix', 'Verify', 'Document'], 'Same order every time.'), TM)

_add('6.2', 'incident-application', T, [
    ('At 09:00 the CRM is down and a VP calls. First?', 'State the impact', 'Reboot the CRM server now', 'Hang up',
     'Impact first: who, what, since when.', SCOPEI, SHOT),
    ('Your first theory is wrong. Record it?', 'Yes, as ruled out', 'No, it is embarrassing to note', 'Skip',
     'Ruled-out theories save others time.', m('NEG'), m('NEG')),
    ('In the firefighter story, sizing up first is?', 'Impact', 'Spraying everywhere', 'Leaving',
     'Firefighters size up before acting.', SCOPEI, SHOT),
    ('In the timeline, what came before the fix?', 'Status update', 'A quiet, unlogged reboot', 'Nothing',
     'Communicate before fixing.', PROM, SIL),
    ('Good VP update?', 'Impact, known, next 09:30', 'Fixed in five minutes, promise', 'Unknown',
     'Facts and next update time, no promises.', PROM, PROM),
], ([
    'Here is a real-looking pressure incident.',
    'At 09:00 the CRM is down for sales.',
    'A VP calls every five minutes.',
    'You state impact: 40 users, since 08:50.',
    'You test two theories and rule one out.',
    'You send a status with the next update time.',
    'You fix, verify with sales, and document.',
], 'Under pressure, run the same steps and keep updates factual.'), (
    'Firefighters arriving at a fire size it up first: who is inside, where it is spreading. Spraying water everywhere '
    'wastes it. The VP’s calls are the crowd shouting; the size-up still comes first.',
    [('Size-up', 'impact'), ('Spraying everywhere', 'shotgun fixes'), ('Crowd shouting', 'VP pressure'), ('Incident report', 'documentation')],
    'Fires grow by the second. Most outages do not get worse while you spend two minutes planning.'),
    ('flow', 'CRM outage timeline', ['09:00 impact 40 users', '09:05 theory 1 ruled out', '09:10 theory 2 proven', '09:12 status', '09:20 fix and verify']),
    'Each box is a method step with a time. The status comes before the fix.',
    'Write a timeline for an outage with a VP calling, including two theories.',
    order('Order the steps.', ['Impact', 'Theory 1 ruled out', 'Theory 2 proven', 'Status update', 'Fix and verify'], 'Method order.'), TM)

_add('6.2', 'standard-of-work', T, [
    ('A theory was ruled out. Record it?', 'Yes, with the test', 'No, only the winner matters', 'Skip',
     'Ruled-out theories are evidence.', m('NEG'), m('NEG')),
    ('Trying three fixes because the VP is shouting is…', 'Shotgun fixing', 'Responsive leadership in action', 'Fine',
     'Several fixes at once hide cause and can add outages.', SHOT, ATTR),
    ('In the chess story, one move at a time is?', 'One change', 'Move every piece at once', 'Quit',
     'One move, then observe.', SHOT, m('NEG')),
    ('In the chart, which is “avoid”?', 'Three fixes at once', 'Note the ruled-out theory', 'Status update',
     'Shotgun fixes lose attribution.', SHOT, m('NEG')),
    ('Which line meets the standard?', '09:05 DB up; app pool down', 'Tried a few things, works now', 'OK',
     'Test, result, time.', m('NEG'), m('CHECKLIST')),
], ([
    'Pressure work has two habits.',
    'Write down ruled-out theories with their tests.',
    'Make one change at a time.',
    'Shouting does not justify shotgun fixes.',
    'Shotgun fixes hide the cause.',
], 'Write every result, and change only one thing at a time, even under pressure.'), (
    'A chess player under time pressure still moves one piece at a time. Moving several would be illegal and chaotic. '
    'Shotgun fixes are illegal chess moves: you cannot tell which one mattered.',
    [('One move', 'one change'), ('Chess clock', 'outage pressure'), ('Scoresheet', 'ticket timeline'), ('Illegal moves', 'shotgun fixes')],
    'Chess has rules that stop you. Networks let you make every mistake at once.'),
    ('two', 'Pressure standard of work', (('Do', ['Note ruled-out theories', 'One change', 'Status before fix']),
                                          ('Avoid', ['Only noting the winner', 'Three fixes at once', 'Promised times']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “tried things, works now” as a standard line with tests, results and times.',
    reveal('Rewrite: “tried things, works now”.', '09:05 DB ping OK; 09:10 app pool stopped; restarted 09:15; sales login OK 09:17.'), TM)

_add('6.2', 'practice-standard-for-this-lesson', T, [
    ('First line on a method checklist?', 'Impact', 'Reboot the main server', 'Guess',
     'Impact comes first.', SCOPEI, SHOT),
    ('Pass sign for “communicate”?', 'Next update time set', 'Said “it’ll be fixed soon”', 'None',
     'A good update sets the next update time.', PROM, m('CHECKLIST')),
    ('In the recipe story, the fail note is?', 'What to write if it fails', 'The colour of the kitchen walls', 'Salt',
     'Each step needs a failure note.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “verify”?', 'Document', 'Leave at once for lunch', 'Blame',
     'Document after verifying.', DOCS, ALERT),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite seven words fast', 'Read',
     'Explain the method plainly, then run it.', m('RECALL'), m('JARGON')),
], ([
    'Explain the method without notes.',
    'Then run it on a lab ticket.',
    'Write a checklist of 5 to 9 steps.',
    'Start with impact.',
    'Each step gets a pass sign, like “next update time set”.',
    'Each step gets a fail note.',
], 'The method checklist is the seven steps with pass signs.'), (
    'A recipe card for a dinner party lists each course with “done when”. Under pressure, the card keeps you calm. Your '
    'method checklist is that card for a busy outage.',
    [('Course', 'method step'), ('“Done when”', 'pass sign'), ('Burnt note', 'fail note'), ('Guests waiting', 'users waiting')],
    'Dinner can be late. Some outages have a business deadline, so time boxes matter.'),
    ('flow', 'Method checklist', ['Impact', 'Theory and test', 'Status with time', 'Fix and verify', 'Document']),
    'These boxes compress the seven steps into a five-line checklist. Each needs a pass sign and a fail note.',
    'Write a five-line method checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Impact', 'Theory and test', 'Status', 'Fix and verify', 'Document'], 'Method order.'), TM)

_add('6.2', 'beyond-the-quiz', T, [
    ('What does the method need from others?', 'Approvals and access', 'A faster laptop for you', 'Nothing',
     'Fixes may need approval or access you do not have.', ESCF, m('RECALL')),
    ('You skip “communicate”. What breaks?', 'Stakeholder trust', 'Every network link at once', 'Nothing',
     'People fill the silence with worry and calls.', PROM, m('RECALL')),
    ('In the relay story, passing the baton is?', 'Escalation', 'Dropping out of the race', 'Rest',
     'A clean handover keeps the race going.', ESCF, ESCF),
    ('In the chart, a time box does what?', 'Triggers escalation', 'Cuts the length of the ticket', 'Nothing',
     'When time runs out, escalate.', TBOX, TBOX),
    ('When do you escalate under pressure?', 'Time box expires', 'Never, it looks weak', 'At once',
     'Escalation is a step, not a failure.', ESCF, ESCF),
], ([
    'A quiz cannot cover every pressure case.',
    'Know what the method needs: approvals and access.',
    'Know what breaks if you skip updates: trust.',
    'Set a time box for each theory.',
    'Escalate when it runs out.',
    'Escalation is part of the method.',
], 'Time boxes and escalation keep pressure from stalling the work.'), (
    'In a relay race, each runner has a set distance before passing the baton. Holding on longer slows the team. A time '
    'box is your leg of the race; escalation is the baton pass.',
    [('Leg of the race', 'time box'), ('Baton', 'evidence package'), ('Next runner', 'next-tier team'), ('Coach', 'incident lead')],
    'Runners know the distance. Time boxes must be set at the start, or nobody knows when to pass.'),
    ('two', 'Stuck: three causes', (('Cause', ['No access', 'No approval', 'Theory exhausted']),
                                    ('Deciding check', ['Can I log in?', 'Is a change needed?', 'Time box expired?']))),
    'Each cause points to a different escalation.',
    'Write your own pressure scenario: symptom, time box, escalation trigger, handover note.',
    reveal('Thirty minutes in, no theory proven, time box was 20. Next?', 'Escalate with impact, tests run and results.'), TM)

# ================================================================== 6.3 Verification and Documentation
m = mc('6.3')
T = 'Verification and Documentation'
_add('6.3', 'core-concepts', T, [
    ('The alert cleared. Is the fix verified?', 'No, test the workflow', 'Yes, green means done', 'Maybe',
     'A cleared alert is not proof; the user’s task must work.', ALERT, ALERT),
    ('What belongs in the final note?', 'Root cause and ruled-outs', 'Only the word “fixed” at the end', 'Nothing',
     'Root cause plus what was ruled out.', DOCS, m('NEG')),
    ('In the court story, evidence is?', 'Required', 'Optional for experts', 'Ignored',
     'Claims need evidence, like root-cause notes.', DOCS, ALERT),
    ('In the chart, who verifies?', 'The user', 'The monitoring alert only', 'Nobody',
     'The user confirms their workflow works.', ALERT, ALERT),
    ('Docs after a fix are…', 'Required', 'Optional once it works', 'Never',
     'Docs must be updated even after service is restored.', DOCS, DOCS),
], ([
    'Verify the user’s workflow, not just lights.',
    'A cleared alert is not proof.',
    'Write the root cause.',
    'Write what you ruled out.',
    'Update the documentation.',
    'The next person will rely on it.',
], 'Verify with the user’s real task; write cause and ruled-outs.'), (
    'In court, a claim without evidence is thrown out. A ticket that says “fixed” without what was tested and why is the '
    'same. The court record is your documentation.',
    [('Court record', 'ticket'), ('Evidence', 'tests and results'), ('Verdict', 'root cause'), ('Witness confirms', 'user verifies')],
    'Courts take months. Tickets should be written while the facts are fresh.'),
    ('flow', 'Close a ticket properly', ['Fix applied', 'User workflow tested', 'Root cause written', 'Ruled-outs written', 'Docs updated']),
    'Each box must be done before closing. The second box is verification, not the alert.',
    'In the triage lab, verify with the user’s real task and write the root cause and ruled-outs.',
    order('Order the close-out.', ['Fix applied', 'User workflow tested', 'Root cause', 'Ruled-outs', 'Docs updated'], 'Verify, then write.'), TRI)

_add('6.3', 'incident-application', T, [
    ('Printer alert cleared at 15:00. Next?', 'Print a test page', 'Close the ticket right now', 'Leave',
     'Verify the real workflow.', ALERT, ALERT),
    ('Driver theory ruled out. Record it?', 'Yes, as a ruled-out', 'No, it was not the cause', 'Skip',
     'Ruled-outs are part of the record.', m('NEG'), DOCS),
    ('In the receipt story, the receipt is?', 'Verification', 'The shop’s window', 'Bag',
     'A receipt proves the purchase like a test page proves the fix.', ALERT, m('RECALL')),
    ('In the timeline, what proved the fix?', 'User printed a page', 'The alert turned green', 'Reboot',
     'The user’s task working is proof.', ALERT, ALERT),
    ('Good closing note?', 'Cause, ruled-outs, verify', 'Fixed, closing ticket now', 'Done',
     'Complete and specific.', DOCS, DOCS),
], ([
    'Here is a real-looking verification case.',
    'A print queue fails at 14:30.',
    'You rule out the driver.',
    'You find the spooler stopped and restart it.',
    'The alert clears at 15:00.',
    'You ask the user to print a page. It works.',
    'You write cause, ruled-outs and verification.',
], 'The user’s page printing is the proof; the alert is not.'), (
    'At a shop, the receipt proves the sale, not the till beeping. The till might beep for a failed card. A cleared alert '
    'is a beep; the user printing a page is the receipt.',
    [('Till beep', 'cleared alert'), ('Receipt', 'user test'), ('Shop’s ledger', 'ticket'), ('Returned item', 'reopened ticket')],
    'A receipt is printed for you. You must ask the user to test.'),
    ('flow', 'Printer timeline', ['14:30 print fails', '14:35 driver ruled out', '14:40 spooler restarted', '15:00 alert clear', '15:02 user prints'], 4),
    'The red box marks the real proof. The alert clearing before it is a hint, not verification.',
    'Write a timeline for a print fault that ends with user verification.',
    order('Order the steps.', ['Symptom', 'Rule out driver', 'Fix spooler', 'User prints', 'Write record'], 'Verify with the user.'), TRI)

_add('6.3', 'standard-of-work', T, [
    ('Network ruled out. Record it?', 'Yes, as a ruled-out', 'No, it was fine so skip', 'Skip',
     'Ruled-outs are documentation.', m('NEG'), DOCS),
    ('Closing on a green alert and editing docs later is…', 'Weak practice', 'An efficient way to work', 'Required',
     'Docs often never get written later.', DOCS, ALERT),
    ('In the lab-notebook story, writing as you go is?', 'Live notes', 'Writing it from memory', 'Skip',
     'Write while it is fresh.', DOCS, m('NEG')),
    ('In the chart, which is “avoid”?', 'Close on alert', 'Note ruled-outs', 'Ask user',
     'An alert is not verification.', ALERT, m('NEG')),
    ('Which line meets the standard?', 'Spooler restart; user OK 15:02', 'Fixed the printer thing this afternoon', 'OK',
     'Action, verification and time.', m('NEG'), DOCS),
], ([
    'Documentation has two habits.',
    'Write ruled-outs as you go.',
    'Verify with the user before closing.',
    'Do not close on a green alert.',
    'Do not leave docs for “later”.',
    'Later usually means never.',
], 'Write notes as you go, and verify with the user before closing.'), (
    'A scientist writes in a lab notebook during the experiment, not from memory a week later. Memory drops the failed '
    'attempts, which are often the most useful. Tickets are lab notebooks.',
    [('Lab notebook', 'ticket'), ('Failed attempt', 'ruled-out theory'), ('Writing later', 'doc debt'), ('Peer review', 'next technician reading')],
    'Scientists publish. Your notes are read in the middle of the next outage, so clarity matters more.'),
    ('two', 'Documentation standard of work', (('Do', ['Write ruled-outs live', 'User verifies', 'Update docs now']),
                                               ('Avoid', ['Only the winner', 'Close on alert', 'Docs later']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “fixed the printer thing” as a standard closing line.',
    reveal('Rewrite: “fixed the printer thing”.', 'Cause: spooler stopped. Ruled out: driver, network. Verified: user printed 15:02.'), TRI)

_add('6.3', 'practice-standard-for-this-lesson', T, [
    ('First line on a close-out checklist?', 'User verifies', 'Close the ticket straight away', 'Leave',
     'Verification comes before any closing note.', ALERT, DOCS),
    ('Pass sign for “root cause”?', 'Cause plus evidence', 'The word “fixed” alone', 'Blank',
     'A cause needs the evidence that proved it.', DOCS, m('CHECKLIST')),
    ('In the map story, the fail note is?', 'What to write if it fails', 'The colour of the compass case', 'Ink',
     'Every step needs a failure note.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “ruled-outs”?', 'Update docs', 'Delete the old ticket notes', 'Reboot',
     'Docs come last.', DOCS, DOCS),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every ticket field', 'Read',
     'Explain close-out plainly, then do it.', m('RECALL'), m('JARGON')),
], ([
    'Explain verification and documentation without notes.',
    'Then close a lab ticket properly.',
    'Write a checklist of 5 to 9 steps.',
    'Start with user verification.',
    'Each step has a pass sign, like “cause plus evidence”.',
    'Each step has a fail note.',
], 'A close-out checklist verifies first and writes evidence-backed notes.'), (
    'A map-maker checks each road by walking it before printing. The legend explains every symbol. A close-out checklist '
    'is the walk and the legend: each item verified, each note clear.',
    [('Walking the road', 'user verification'), ('Legend', 'clear notes'), ('Correction slip', 'fail note'), ('Printed map', 'closed ticket')],
    'Maps last years. Ticket notes may be read tomorrow in a crisis, so write for a tired reader.'),
    ('flow', 'Close-out checklist', ['User verifies', 'Root cause', 'Ruled-outs', 'Docs updated', 'Close']),
    'These boxes outline the checklist from left to right. Closing the ticket is the last box, never the first, and each box needs evidence.',
    'Write a five-line close-out checklist with pass signs and fail notes.',
    order('Order the checklist.', ['User verifies', 'Root cause', 'Ruled-outs', 'Docs updated', 'Close'], 'Close last.'), TRI)

_add('6.3', 'beyond-the-quiz', T, [
    ('What does good documentation need?', 'A reader in mind', 'Lots of long screenshots', 'Nothing',
     'Write for the next technician.', DOCS, m('RECALL')),
    ('Docs are not updated. What breaks?', 'The next incident', 'Nothing, service is up', 'DNS',
     'The next person works from wrong information.', DOCS, DOCS),
    ('In the recipe story, a missing step is?', 'Doc gap', 'A brand new dish idea', 'Salt',
     'A missing step ruins the next cook’s dish.', DOCS, m('RECALL')),
    ('In the chart, which check splits “fixed” from “hidden”?', 'User retest later', 'Alert still green', 'Ask',
     'A later retest shows if the fault returns.', ALERT, ALERT),
    ('When do you escalate a doc gap?', 'Owner unknown', 'Never, docs are optional', 'At once',
     'If no one owns the doc, raise it.', m('ESCALATE'), DOCS),
], ([
    'A quiz cannot cover every documentation case.',
    'Know what docs need: a reader in mind.',
    'Know what breaks without them: the next incident.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Raise doc gaps with an owner.',
], 'Documentation is a tool for the next incident.'), (
    'A family recipe passed down without the oven temperature leads to burnt cakes for years. Missing documentation does '
    'the same: every future technician repeats the mistake.',
    [('Family recipe', 'runbook'), ('Missing oven temperature', 'missing config detail'), ('Burnt cake', 'repeat incident'), ('Grandmother', 'original technician')],
    'Recipes rarely change. Networks change monthly, so docs must be updated after every change.'),
    ('two', 'Fault came back: three causes', (('Cause', ['Root cause missed', 'Fix not saved', 'Docs wrong']),
                                              ('Deciding check', ['Re-read evidence', 'Running vs startup config', 'Compare docs to device']))),
    'Each cause has one check. This is why ruled-outs and configs are written down.',
    'Write your own documentation scenario: repeat fault, three causes, deciding check, owner.',
    reveal('Fix worked, then failed after a reload. Likely?', 'The change was not saved to startup config.'), TRI)

# ================================================================== 6.4 Full Capstone Scenario
m = mc('6.4')
T = 'Full Capstone Scenario'
_add('6.4', 'the-scenario', T, [
    ('Weekend firewall change; Monday half can’t reach the app. First?', 'Scope the impact', 'Roll back everything at once',
     'Reboot', 'Who and how many, then correlate with the change.', SCOPEI, SHOT),
    ('What links the outage to the change?', 'Timing and rule hits', 'A hunch from the VP this morning', 'Nothing',
     'Change time plus rule hits correlate cause.', SIL, m('RECALL')),
    ('In the orchestra story, the conductor is?', 'You, coordinating', 'The audience in seats', 'Nobody',
     'You coordinate checks across teams.', ESCF, m('RECALL')),
    ('In the chart, what needs approval?', 'The rollback', 'Reading the change log', 'Pinging',
     'Production actions need approval.', SIL, 'MC-C-NO6-NO-ROLLBACK'),
    ('Last step?', 'User verification', 'Close the ticket at once', 'Blame',
     'Users confirm the app works.', ALERT, DOCS),
], ([
    'A firewall change happened at the weekend.',
    'On Monday, half the users cannot reach the main web app.',
    'You coordinate the checks.',
    'Scope the impact first.',
    'Correlate with the change.',
    'Get approval before acting.',
    'Verify with users.',
], 'Scope, correlate, approve, act, verify.'), (
    'A conductor does not play every instrument. She keeps time, cues each section and stops the piece if something goes '
    'wrong. In this capstone you conduct: the firewall team, the app team and the users each play their part.',
    [('Conductor', 'you'), ('Sections', 'teams'), ('Score', 'change log and timeline'), ('Applause', 'user verification')],
    'Orchestras rehearse. Outages do not, so your timeline is written live.'),
    ('flow', 'Full capstone', ['Scope', 'Change correlation', 'Tests', 'Approval', 'Action', 'User verification']),
    'These six boxes are the whole capstone, from left to right. Approval sits before action, so every production change stays controlled and recorded.',
    'In the ticket lab, write the capstone timeline in this order with times.',
    order('Order the capstone.', ['Scope', 'Change correlation', 'Tests', 'Approval', 'Action', 'User verification'], 'Method under pressure.'), TM)

_add('6.4', 'your-turn-scaffolded-checklist', T, [
    ('“Scope” needs what?', 'Who and how many', 'Your personal guess', 'Nothing',
     'Name the affected users and count.', SCOPEI, m('CHECKLIST')),
    ('“Change correlation” needs?', 'Change time vs outage', 'The VP’s strong opinion', 'Nothing',
     'Line up the change time with the start of the outage.', SIL, m('RECALL')),
    ('In the form story, a blank line means?', 'Unfinished', 'Optional for today', 'Done',
     'Do not skip lines.', m('CHECKLIST'), m('CHECKLIST')),
    ('In the chart, “approval for action” needs?', 'A named approver', 'Nobody at all, just do it', 'A guess',
     'Record who approved and when.', SIL, m('CHECKLIST')),
    ('Which entry fills “timeline notes”?', '08:10 rule 22 hits', 'Stuff happened earlier', 'OK',
     'Time, item, result.', m('NEG'), DOCS),
], ([
    'This capstone has six lines to complete.',
    'Write who is affected and how many.',
    'Line up the change time with the first failure.',
    'List each test with its result.',
    'Name the person who approved the action.',
    'Record what the users said when they tested.',
    'Keep a timeline with a time on every entry.',
], 'Six lines, each with names, values and times.'), (
    'An accident report form asks: who was involved, when, what tests were done, who authorised the response, and whether '
    'the people are okay. Missing one box makes the report useless for next time.',
    [('Who was involved', 'scope'), ('When', 'change correlation'), ('Tests done', 'tests'), ('Authorised by', 'approval'), ('People okay', 'user verification')],
    'Accident forms are filed later. Your timeline must be written as it happens.'),
    ('two', 'Checklist filled in', (('Line', ['Scope', 'Correlation', 'Approval', 'Verification']),
                                    ('Example', ['120 of 240 users, VLAN 30', 'Change Sat 22:00; fail Mon 08:00', 'J. Lee 08:25', 'Sales lead OK 08:40']))),
    'The right column shows good entries with names and times.',
    'Fill the six lines for your lab capstone.',
    reveal('Fill “approval for action”.', 'Rollback of rule 22 approved by J. Lee (change manager) 08:25.'), TM)

_add('6.4', 'common-beginner-mistakes', T, [
    ('What is “forward-fix without evidence”?', 'Changing on a hunch', 'Reading the change log first', 'Testing',
     'Acting without proving the cause.', SHOT, SIL),
    ('Why verify with users after green lights?', 'Lights are not tasks', 'It is far too quick to bother', 'It is not needed',
     'Green lights do not prove the app works for users.', ALERT, ALERT),
    ('In the builder story, building on a guess is?', 'Forward-fix', 'Checking the plan', 'Measuring',
     'Acting without a survey.', SHOT, SIL),
    ('In the chart, the fix for “no verification” is?', 'Ask users to test', 'Watch the alert go green', 'Wait',
     'Users confirm the real workflow.', ALERT, ALERT),
    ('Which entry avoids both mistakes?', 'Rule 22 hits; rollback; user OK', 'Changed a rule, the lights went green', 'Done',
     'Evidence, action, verification.', SHOT, ALERT),
], ([
    'Two mistakes are common here.',
    'First, forward-fixing without evidence.',
    'Second, no user verification after green lights.',
    'Prove the cause before you change anything.',
    'Ask users to test their real task.',
], 'Get evidence before any action, and get users to confirm before closing.'), (
    'A builder who adds a new wall because “it feels weak” without a survey may make things worse. A builder who signs '
    'off because the lights work, without asking if the doors open, has not finished.',
    [('Wall on a hunch', 'forward-fix without evidence'), ('Survey', 'tests and rule hits'), ('Lights work', 'green alerts'),
     ('Doors open', 'user workflow works')],
    'Buildings are inspected by law. Network fixes are only inspected if you ask users.'),
    ('two', 'Mistake and fix', (('Mistake', ['Forward-fix on a hunch', 'Close on green lights']), ('Fix', ['Prove cause first', 'User tests the app']))),
    'Each row is a mistake and the habit that replaces it.',
    'Rewrite “changed a rule, lights green, closed” as a proper capstone close.',
    sort('Sort each action.', {'Mistake': ['Change on a hunch', 'Close on green'], 'Good': ['Prove with rule hits', 'User verifies']},
         'Evidence and users.'), TM)

_add('6.4', 'check-your-understanding', T, [
    ('First beat in the explanation?', 'Symptom and scope', 'The rollback you did', 'Blame',
     'Start with what was seen and who was hit.', SCOPEI, m('JARGON')),
    ('What proved the cause?', 'Change plus rule hits', 'The VP’s strong guess', 'Reboot',
     'Timing and hits together prove it.', SIL, m('PARALLEL')),
    ('In the match story, the final whistle is?', 'User verification', 'The kick-off at the start', 'Half time',
     'The match is over when users confirm.', ALERT, m('RECALL')),
    ('In the chart, the last box is?', 'Users confirm', 'Close the ticket right now', 'Blame',
     'Users confirming closes the loop.', ALERT, DOCS),
    ('Cannot explain it? Next?', 'Re-run the demo', 'Skip to the next one', 'Guess',
     'Re-run the steps.', m('RECALL'), m('RECALL')),
], ([
    'Explain the capstone in two minutes.',
    'Symptom and scope: half the users, main app, Monday.',
    'Checks: change log, rule hits, port test.',
    'Cause: weekend rule 22 blocked one VLAN.',
    'Verification: users in that VLAN reach the app.',
    'If you cannot, re-run the demo.',
], 'Scope, checks, cause, verification, in two minutes.'), (
    'A football commentator sums up a match: the situation, three key plays, why one team won, and the final whistle. '
    'Your capstone explanation has the same four parts.',
    [('Situation', 'symptom and scope'), ('Key plays', 'checks'), ('Why they won', 'cause'), ('Final whistle', 'users confirm')],
    'A match ends at a set time. Your incident ends only when users confirm.'),
    ('flow', 'Two-minute explanation', ['Symptom and scope', 'Three checks', 'Cause proved', 'Users confirm']),
    'Four boxes, four beats, read from left to right. If one box is blank when you practise, re-run that part of the capstone before you explain it again.',
    'Explain your capstone to a peer in two minutes using the boxes.',
    order('Order the explanation.', ['Symptom and scope', 'Three checks', 'Cause proved', 'Users confirm'], 'Story order.'), TM)
