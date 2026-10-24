"""Option B pass 3 — NETOPS chapter 5 bespoke ladders (monitoring, management hardening, segmentation, review capstone).
Pending SME review."""
from curriculum_v2.ladder.netops._p3 import N, mc, src
from curriculum_v2.ladder.schema import order, reveal, sort

SECS = {}
TRAP, NTP, AAA, NOLOC, INB, INSIDE, MACF = (
    'MC-L-NO5-TRAP-VS-POLL', 'MC-L-NO5-NO-NTP', 'MC-L-NO5-AAA-PROTOCOLS', 'MC-L-NO5-NO-LOCAL-ACCOUNT', 'MC-L-NO5-INBAND-ONLY',
    'MC-L-NO5-INSIDE-TRUSTED', 'MC-L-NO5-MAC-FILTER-STRONG')
SYSO, CRC, BASE, SINGLE, SNMPV, WEAK, SSIDSEG, PRIN = (
    'MC-NO5-SYSLOG-ORDER', 'MC-NO5-CRC-AS-LOAD', 'MC-NO5-BASELINE-PURPOSE', 'MC-NO5-SINGLE-SAMPLE', 'MC-NO5-SNMP-VERSIONS',
    'MC-NO5-WEAK-MGMT', 'MC-NO5-SSID-AS-SEGMENT', 'MC-NO5-PRINCIPLE-MIXUP')
LOGS = ('linux-vm-logs', 'Read the system log, find the first error by time and note its severity number.')
SSH = ('linux-vm-ssh', 'Log in with SSH, confirm Telnet is closed and note who may reach the management address.')
ACL = ('rtr-vlan-acl', 'Read the inter-VLAN ACL and say which user-to-server paths it allows and denies.')


def _add(label, sid, title, *a):
    SECS[(label, sid)] = N(label, sid, src(label, title), *a)


# ================================================================== 5.1 Monitoring Signals
m = mc('5.1')
T = 'Monitoring Signals'
_add('5.1', 'core-concepts', T, [
    ('Which syslog severity is most serious?', '0 (emergency)', '7 (debug messages)', '5 (notice level)',
     'Lower syslog numbers are more severe; 0 is emergency.', SYSO, SYSO),
    ('CRC errors climb on one port. Usually?', 'A physical fault', 'Heavy traffic load on the link', 'DNS',
     'CRC errors are damaged frames, usually cabling or optics.', CRC, CRC),
    ('In the camera story, knowing “normal” is?', 'A baseline', 'A brand new camera lens', 'An alarm',
     'You need a sense of normal to spot the odd, like a baseline.', BASE, SINGLE),
    ('In the chart, SNMP traps are sent by?', 'The device', 'The manager on a schedule', 'Users',
     'Traps are sent by the device when something happens; polls come from the manager.', TRAP, TRAP),
    ('Logs from three devices disagree on time. Fix?', 'Use NTP', 'Read them in any order you like', 'Ignore it',
     'A shared time source makes logs line up.', NTP, NTP),
], ([
    'Monitoring tells you where to look.',
    'Know three signals: errors, syslog and availability.',
    'Interface errors point to physical faults.',
    'Syslog gives events with a severity number.',
    'Lower numbers are more serious.',
    'Availability checks say if a device answers.',
    'You need a baseline to know what is normal.',
], 'Know where each signal lives and compare it with normal.'), (
    'A shop owner watching security cameras needs to know what a normal day looks like. Without that, a crowd at lunch '
    'looks like trouble. Network monitoring needs the same baseline before alerts mean anything.',
    [('Camera feed', 'monitoring dashboard'), ('Normal day', 'baseline'), ('Alarm bell', 'SNMP trap'), ('Clock on the footage', 'NTP time')],
    'Cameras show pictures. Network signals are numbers, so you must know the normal values.'),
    ('two', 'Three signals', (('Signal', ['Interface errors', 'Syslog', 'Availability']),
                              ('Tells you', ['Physical damage', 'Events and severity', 'Device answers or not']))),
    'Each row pairs a signal with what it reveals. Look in the right place for the question you have.',
    'In the logs lab, find the first error by time and write its severity number.',
    sort('Sort each finding.', {'Physical': ['CRC errors', 'Input errors'], 'Event': ['Syslog severity 3', 'Link down message']},
         'Different signals, different meanings.'), LOGS)

_add('5.1', 'incident-application', T, [
    ('Users report slowness at 14:00. First signal?', 'Interface errors', 'Each user’s browser history', 'DNS',
     'Errors on the uplink show physical trouble quickly.', CRC, m('PARALLEL')),
    ('Syslog shows no new events. Record it?', 'Yes, it is evidence', 'No, nothing happened so skip it', 'Later',
     'A quiet log rules out config changes and reboots.', m('NEG'), m('NEG')),
    ('In the hospital story, the heart monitor is?', 'Monitoring', 'The hospital bed frame', 'Lunch',
     'It shows signals compared with normal.', BASE, m('RECALL')),
    ('In the timeline, what proved the cause?', 'CRC rising on uplink', 'One user’s guess at 14:01', 'Reboot',
     'CRC errors rising on the uplink match the slowness.', CRC, m('PARALLEL')),
    ('Good status line?', 'Uplink errors found; fixing', 'The network is dying slowly', 'Fine',
     'Calm, accurate, with next step.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking monitoring incident.',
    'At 14:00 users report slowness.',
    'Syslog shows nothing new.',
    'The uplink shows CRC errors rising.',
    'The baseline is zero errors.',
    'You record the numbers and times.',
    'You replace the uplink patch and recheck.',
], 'Compare live signals with the baseline and record the numbers.'), (
    'In a hospital, a heart monitor shows a pulse line. Nurses know a normal line, so a jagged one gets attention. CRC '
    'errors rising on an uplink are the jagged line.',
    [('Heart monitor', 'interface counters'), ('Normal pulse', 'baseline of zero errors'), ('Jagged line', 'rising CRC'), ('Nurse’s chart', 'ticket')],
    'Nurses see a line. You see counters, so you must read them twice to see a trend.'),
    ('flow', 'Slowness timeline', ['14:00 slowness', '14:03 syslog quiet', '14:05 CRC rising', '14:08 swap patch', '14:20 CRC flat'], 2),
    'The red box is the proof. The quiet log before it ruled out changes.',
    'Write a timeline for a slowness complaint where uplink errors are rising.',
    order('Order the steps.', ['Confirm slowness', 'Check syslog', 'Read counters twice', 'One change', 'Recheck counters'],
          'Signal, trend, change, verify.'), LOGS)

_add('5.1', 'standard-of-work', T, [
    ('Syslog was quiet. Record it?', 'Yes, it rules out changes', 'No, it showed nothing useful', 'Skip it',
     'A quiet log is evidence.', m('NEG'), m('NEG')),
    ('Clearing counters and swapping cables at once is…', 'Untracked change', 'A tidy quick reset for all', 'Required',
     'You lose the before reading and the cause.', m('PARALLEL'), m('PARALLEL')),
    ('In the thermometer story, two readings are?', 'A trend', 'A fact on its own', 'Noise',
     'One reading is a sample; two show a trend.', SINGLE, BASE),
    ('In the chart, which is “avoid”?', 'Clear counters first', 'Note the syslog result', 'Read twice',
     'Clearing first loses the evidence.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'Gi1/0/48 CRC 120→480 14:05', 'Errors seemed rather high earlier today', 'Bad',
     'Port, values and time.', m('NEG'), SINGLE),
], ([
    'Monitoring work has two habits.',
    'Write down quiet signals, like an empty log.',
    'Read counters twice to see a trend.',
    'Make one change at a time.',
    'Do not clear counters before you record them.',
], 'Record before and after, and change one thing.'), (
    'A nurse takes a temperature, waits, takes it again and writes both. One reading may be a fluke; two show a trend. '
    'Shaking the thermometer before reading it destroys the evidence, like clearing counters too soon.',
    [('Temperature reading', 'counter value'), ('Second reading', 'trend check'), ('Shaking the thermometer', 'clearing counters'),
     ('Patient chart', 'ticket')],
    'A thermometer resets itself. Counters do not, so clearing them is a deliberate choice you should record.'),
    ('two', 'Monitoring standard of work', (('Do', ['Note quiet syslog', 'Read counters twice', 'One change']),
                                            ('Avoid', ['Skipping quiet results', 'Clearing counters first', 'Two changes']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “errors seemed high” as a standard line with port, two values and times.',
    reveal('Rewrite: “errors seemed high”.', 'Gi1/0/48 CRC 120 at 14:05, 480 at 14:10; baseline 0.'), LOGS)

_add('5.1', 'practice-standard-for-this-lesson', T, [
    ('First line on a monitoring checklist?', 'Check the baseline', 'Clear all the counters now', 'Reboot',
     'Know normal before reading live values.', BASE, m('PARALLEL')),
    ('Pass sign for “errors”?', 'Flat at baseline', 'Any number is fine here', 'Large',
     'Good means no rise above the baseline.', SINGLE, m('CHECKLIST')),
    ('In the weather story, the normal range is?', 'The pass sign', 'The weather presenter', 'A cloud',
     'A normal range tells you what “good” looks like.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “errors rising”?', 'Check cabling', 'Restart the logging server', 'DNS',
     'Rising CRC sends you to the physical layer.', CRC, m('PARALLEL')),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every syslog level name', 'Read logs',
     'Explain the signals plainly, then read them.', m('RECALL'), m('JARGON')),
], ([
    'Explain monitoring signals without notes.',
    'Then read real logs in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start with the baseline.',
    'Read counters twice.',
    'Each step has a pass sign and a fail note.',
], 'A monitoring checklist compares live values with the baseline.'), (
    'A weather station records temperature against the normal for the month. “22 °C” means little; “8 degrees above '
    'normal” means a lot. Your monitoring checklist compares every reading with its normal.',
    [('Monthly normal', 'baseline'), ('Today’s reading', 'live counter'), ('Heatwave warning', 'alert'), ('Station log', 'ticket')],
    'Weather normals change slowly. Network baselines change after upgrades, so refresh them.'),
    ('flow', 'Monitoring checklist', ['Baseline', 'Read errors', 'Read again', 'Check syslog', 'Check availability']),
    'These boxes outline the checklist from left to right. Under each box, add the pass sign you expect and the note you will write if it fails.',
    'Write a five-line monitoring checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Baseline', 'Read errors', 'Read again', 'Syslog', 'Availability'], 'Normal first.'), LOGS)

_add('5.1', 'beyond-the-quiz', T, [
    ('What do correlated logs need?', 'Common time (NTP)', 'The same device brand everywhere', 'Big disks',
     'Without NTP, timestamps cannot be lined up.', NTP, m('RECALL')),
    ('The log server fills up. What breaks?', 'New log storage', 'Every switch port at once', 'DNS',
     'New events are lost; devices keep running.', m('RECALL'), 'MC-R3-NO5-LOCAL-LOGS'),
    ('In the diary story, an undated entry is?', 'A log without NTP', 'A very long diary entry', 'A pen',
     'Without a date, you cannot order events.', NTP, NTP),
    ('In the chart, which test splits device from link?', 'Ping the device', 'Reboot the log server', 'Ask',
     'If the device answers, the link is fine and the device is the focus.', m('RECALL'), m('PARALLEL')),
    ('When do you escalate a monitoring alert?', 'Impact confirmed', 'Never, ignore alerts', 'Instantly',
     'Confirm impact with evidence, then escalate.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every monitoring case.',
    'Know what logs need: NTP time and storage.',
    'Know what breaks: lost events if storage fills.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Escalate when impact is confirmed.',
], 'Signals depend on time and storage; plan for both.'), (
    'A diary with no dates is useless for working out what happened first. Three diaries with different clocks are '
    'worse. NTP gives every device the same clock so logs line up.',
    [('Diary', 'device log'), ('Date on each entry', 'timestamp'), ('Shared calendar', 'NTP'), ('Full diary', 'full log server')],
    'You can guess the order of diary entries from the story. You cannot guess packet timing to the second.'),
    ('two', 'Alert: three causes', (('Cause', ['Real outage', 'Monitoring server fault', 'Threshold too low']),
                                    ('Deciding test', ['Users affected?', 'Other alerts OK?', 'Compare baseline']))),
    'Each cause has one test. This stops alert fatigue.',
    'Write your own monitoring scenario: alert, three causes, deciding test, escalation note.',
    reveal('Three switch logs disagree by minutes. Fix?', 'Point all devices at the same NTP server.'), LOGS)

# ================================================================== 5.2 Management Plane Hardening
m = mc('5.2')
T = 'Management Plane Hardening'
_add('5.2', 'core-concepts', T, [
    ('Which protocol should manage devices?', 'SSH', 'Telnet with a longer password', 'HTTP',
     'SSH encrypts management sessions; Telnet sends cleartext.', WEAK, WEAK),
    ('What does a management ACL do?', 'Limits who connects', 'Speeds up the user traffic', 'Assigns IPs',
     'It restricts management access to approved hosts.', WEAK, INSIDE),
    ('In the utility-room story, the locked door is?', 'Management controls', 'The public hallway on the ground floor', 'The lift',
     'Controls live behind a locked door, not in the public hall.', INSIDE, WEAK),
    ('In the chart, which SNMP version encrypts?', 'v3', 'v2c with a long community', 'v1',
     'Only SNMPv3 adds authentication and encryption.', SNMPV, SNMPV),
    ('After AAA, keep a local admin account?', 'Yes, for break-glass', 'No, delete every local one', 'Only on Fridays',
     'A local break-glass account helps if AAA is down.', NOLOC, NOLOC),
], ([
    'The management plane is how you control devices.',
    'Use SSH, not Telnet.',
    'Limit who can connect with a management ACL.',
    'Keep devices patched.',
    'Use strong, individual logins.',
    'Turn off services you do not use.',
], 'Lock the control room: SSH, ACLs, patches, strong auth, fewer services.'), (
    'A building’s utility room holds the power and water controls. It is locked and only staff have keys. It is not '
    'on the public corridor. Device management should be treated the same way.',
    [('Utility room', 'management plane'), ('Lock and keys', 'SSH and strong auth'), ('Staff-only list', 'management ACL'),
     ('Spare key in a safe', 'break-glass local account')],
    'A locked room is physical. Management access is reachable from far away, so the “door” must be checked on every device.'),
    ('two', 'Weak versus hardened', (('Weak', ['Telnet', 'Shared admin login', 'SNMP v2c public']),
                                     ('Hardened', ['SSH', 'Individual AAA logins', 'SNMPv3']))),
    'Each row swaps a weak habit for a hardened one.',
    'In the SSH lab, confirm SSH works and Telnet is closed. Note which hosts may reach the management address.',
    sort('Sort each setting.', {'Weak': ['Telnet enabled', 'Community “public”'], 'Hardened': ['SSH only', 'Management ACL']},
         'Close the easy doors.'), SSH)

_add('5.2', 'incident-application', T, [
    ('An audit finds Telnet open on a switch. First step?', 'Confirm and record', 'Wipe the whole switch config', 'Ignore',
     'Confirm the finding with evidence before changing anything.', WEAK, m('PARALLEL')),
    ('SSH works. Record it?', 'Yes, before changes', 'No, it is obvious to all', 'Skip',
     'It proves you will not lock yourself out.', m('NEG'), INB),
    ('In the house story, changing locks with keys inside is?', 'Lockout risk', 'A great security move', 'Fine',
     'Check your way back in before changing access.', INB, m('PARALLEL')),
    ('In the timeline, what proved the fix?', 'Telnet refused', 'An email saying “done”', 'A reboot',
     'A refused Telnet connection proves it is off.', WEAK, m('NEG')),
    ('Good status line?', 'Telnet disabled; SSH verified', 'Hackers are inside all the switches', 'OK',
     'Accurate, calm, specific.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking hardening task.',
    'An audit finds Telnet open on one switch.',
    'You confirm it and record the time.',
    'You check that SSH works first.',
    'You disable Telnet in a change window.',
    'You test that Telnet is refused.',
    'You note the result in the ticket.',
], 'Prove the way back in, change one thing, prove the result.'), (
    'Before changing the locks on a house, you make sure you have the new key in hand. Otherwise you lock yourself out. '
    'Disabling Telnet before testing SSH is changing the locks with the key inside.',
    [('Old lock', 'Telnet'), ('New key', 'SSH'), ('Testing the key', 'SSH login test'), ('Locksmith’s note', 'change record')],
    'A locksmith can break in. If you lock out remote access, someone may have to drive to the console.'),
    ('flow', 'Hardening timeline', ['09:00 audit finding', '09:05 SSH tested', '09:10 Telnet off', '09:12 Telnet refused', '09:15 ticket note'], 3),
    'The red box is the proof the change worked. SSH tested first prevents a lockout.',
    'Write a timeline for disabling Telnet safely on one switch.',
    order('Order the steps.', ['Confirm finding', 'Test SSH', 'Disable Telnet', 'Test Telnet refused', 'Record'], 'Safe order.'), SSH)

_add('5.2', 'standard-of-work', T, [
    ('SSH login tested OK. Record it?', 'Yes, it is evidence', 'No, nothing went wrong there', 'Skip',
     'It proves your way back in.', m('NEG'), INB),
    ('Changing ACL, AAA and SNMP in one go is…', 'Untracked change', 'An efficient hardening sweep', 'Required',
     'Three changes risk lockout and hide the cause.', m('PARALLEL'), m('PARALLEL')),
    ('In the climber story, one hold at a time is?', 'One change', 'Jump to the top fast', 'No rope',
     'One move, check, then the next.', m('PARALLEL'), INB),
    ('In the chart, which is “avoid”?', 'Three edits at once', 'Test SSH', 'Note the result each time',
     'Bulk edits risk lockout.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'VTY ACL 10 applied 09:20', 'Hardened the switch today', 'OK',
     'Change, time, specific.', m('NEG'), m('CHECKLIST')),
], ([
    'Hardening work has two habits.',
    'Write down passed tests, like SSH login.',
    'Make one change at a time.',
    'Never change ACL, AAA and SNMP together.',
    'You could lock everyone out.',
    'Keep an out-of-band path ready.',
], 'Prove access, change one thing, keep a way back.'), (
    'A rock climber moves one hand or foot at a time and keeps three points of contact. Moving everything at once is how '
    'climbers fall. Hardening changes need the same three points: tested SSH, out-of-band access, rollback.',
    [('Hold', 'one config change'), ('Three points of contact', 'SSH, console, rollback'), ('Fall', 'lockout'), ('Climbing log', 'ticket')],
    'A climber feels a slip. A lockout may only show when you next try to log in.'),
    ('two', 'Hardening standard of work', (('Do', ['Test SSH first', 'One change', 'Keep console access']),
                                           ('Avoid', ['Skipping the SSH test', 'Three edits at once', 'In-band only']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “hardened the switch” as a standard line with change, time and test.',
    reveal('Rewrite: “hardened the switch”.', '09:20 applied VTY ACL 10 (mgmt subnet only); SSH from jump host OK 09:21.'), SSH)

_add('5.2', 'practice-standard-for-this-lesson', T, [
    ('First line on a hardening checklist?', 'Confirm console path', 'Disable everything at once', 'Reboot',
     'Have out-of-band access before changes.', INB, m('PARALLEL')),
    ('Pass sign for “Telnet disabled”?', 'Connection refused', 'No users complained today', 'Silence',
     'A refused connection proves it.', WEAK, m('CHECKLIST')),
    ('In the pre-flight story, the fail note is?', 'What to write if it fails', 'The pilot’s name and rank', 'Fuel price',
     'Every step needs a failure note.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “ACL applied”?', 'Test from jump host', 'Delete local accounts', 'Reboot',
     'Prove allowed hosts still connect.', WEAK, NOLOC),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every crypto cipher', 'Read RFCs',
     'Explain hardening plainly, then do it.', m('RECALL'), m('JARGON')),
], ([
    'Explain management hardening without notes.',
    'Then harden a lab device.',
    'Write a checklist of 5 to 9 steps.',
    'Start by confirming a console path.',
    'Each step has a pass sign, like “Telnet refused”.',
    'Each step has a fail note.',
], 'A hardening checklist proves access before and after each change.'), (
    'A pilot’s pre-flight checklist includes “emergency exits armed” before take-off. Hardening needs its own emergency '
    'exit: a console or out-of-band path tested before any change.',
    [('Emergency exit', 'console or out-of-band path'), ('Pre-flight check', 'hardening checklist'), ('“Armed”', 'pass sign'),
     ('Abort note', 'fail note')],
    'Pilots rarely use the exits. You may need the console the first time an ACL is wrong.'),
    ('flow', 'Hardening checklist', ['Console path', 'Test SSH', 'Disable Telnet', 'Apply ACL', 'Test jump host']),
    'These boxes outline the checklist from left to right. Under each box, add the pass sign you expect and the note you will write if it fails.',
    'Write a five-line hardening checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Console path', 'Test SSH', 'Disable Telnet', 'Apply ACL', 'Test jump host'], 'Exit first.'), SSH)

_add('5.2', 'beyond-the-quiz', T, [
    ('What does AAA login need upstream?', 'Reachable AAA server', 'A bigger switch CPU and RAM', 'DNS only',
     'Devices must reach the TACACS+ or RADIUS server.', AAA, m('RECALL')),
    ('AAA server down, no local account. What breaks?', 'All admin logins', 'Only user web traffic', 'Nothing',
     'Without a fallback, nobody can log in.', NOLOC, m('RECALL')),
    ('In the bank story, the spare key in the safe is?', 'Break-glass account', 'The bank’s logo on the door', 'A queue',
     'A sealed spare key for emergencies.', NOLOC, NOLOC),
    ('In the chart, TACACS+ is used for?', 'Device admin', 'Wi-Fi user logins only', 'DNS',
     'TACACS+ suits device administration with per-command authorisation.', AAA, AAA),
    ('When do you escalate a hardening gap?', 'Needs a change window', 'Never, just fix it live', 'Before tests',
     'Escalate for approval and a window.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every hardening case.',
    'Know what AAA needs: a reachable server.',
    'Know what breaks if it fails: admin logins.',
    'Keep a break-glass local account.',
    'Build a scenario with three causes.',
    'Know when changes need approval.',
], 'Plan for AAA failure with a safe fallback.'), (
    'A bank vault opens with staff cards checked by a central system. If that system fails, a sealed spare key in a safe '
    'lets a manager in. A break-glass local account is that sealed key.',
    [('Staff card system', 'AAA server'), ('Sealed spare key', 'break-glass local account'), ('Manager', 'senior admin'),
     ('Key log', 'audit record of use')],
    'A spare key is physical. A local account can be guessed, so it needs a long password and audit.'),
    ('two', 'Cannot log in: three causes', (('Cause', ['AAA server down', 'ACL blocks you', 'Wrong credentials']),
                                            ('Deciding test', ['Ping AAA server', 'Try from jump host', 'Test break-glass']))),
    'Each cause has one test. Run them before asking for console access.',
    'Write your own hardening scenario: symptom, three causes, deciding test, escalation note.',
    reveal('AAA is down and nobody can log in to the core switch. Next?', 'Use the break-glass account or console; log its use.'), SSH)

# ================================================================== 5.3 Segmentation
m = mc('5.3')
T = 'Segmentation'
_add('5.3', 'core-concepts', T, [
    ('Why separate user, lab and server paths?', 'To limit spread', 'To make the network faster', 'To save IPs',
     'Segmentation limits how far a compromise spreads.', INSIDE, PRIN),
    ('Is a hidden SSID a segment?', 'No', 'Yes, hiding it isolates', 'Only at night',
     'A name is not a boundary; VLANs and rules are.', SSIDSEG, SSIDSEG),
    ('In the fire-door story, the doors do what?', 'Slow the spread', 'Make the building warmer', 'Decorate',
     'Fire doors slow a fire, like segments slow an attack.', INSIDE, PRIN),
    ('In the chart, what enforces segments?', 'VLANs plus ACLs', 'SSID names and colours', 'DNS',
     'VLANs separate; ACLs or firewalls control what crosses.', SSIDSEG, MACF),
    ('Is MAC filtering a strong control alone?', 'No', 'Yes, MACs are secret', 'Always',
     'MACs are easy to spoof.', MACF, MACF),
], ([
    'Segmentation splits a network into zones.',
    'Users, labs and servers get separate paths.',
    'A flat network lets an attack spread fast.',
    'VLANs separate the zones.',
    'ACLs or firewalls control what crosses.',
    'A hidden SSID is not a segment.',
], 'Separate zones and control what crosses; names are not boundaries.'), (
    'A large building has fire doors between wings. A fire in one wing is slowed at the doors, giving people time. A flat '
    'network is a building with no fire doors.',
    [('Wing', 'segment or VLAN'), ('Fire door', 'ACL or firewall'), ('Fire', 'attack or malware'), ('Fire plan', 'segmentation design')],
    'Fire doors stop heat. ACLs only stop what their rules name, so a lazy “permit any” is a propped-open door.'),
    ('two', 'Flat versus segmented', (('Flat', ['One big VLAN', 'Anything reaches anything', 'Fast spread']),
                                      ('Segmented', ['User, lab, server VLANs', 'ACLs between them', 'Slowed spread']))),
    'Each row compares the two designs.',
    'In the ACL lab, read the inter-VLAN ACL and list which user-to-server paths it allows.',
    sort('Sort each control.', {'Real boundary': ['VLAN plus ACL', 'Firewall zone'], 'Not a boundary': ['Hidden SSID', 'MAC filter alone']},
         'Boundaries need enforcement.'), ACL)

_add('5.3', 'incident-application', T, [
    ('A lab PC can reach the payroll server. First step?', 'Confirm and record', 'Unplug the whole server room', 'Ignore',
     'Confirm the path with a test before changing rules.', INSIDE, m('PARALLEL')),
    ('Users still reach the file server. Record it?', 'Yes, before changes', 'No, that part is obvious', 'Skip',
     'It shows what must keep working after the fix.', m('NEG'), m('NEG')),
    ('In the hotel story, a guest key opening the safe room is?', 'A segment gap', 'Great service', 'Normal',
     'A guest should never reach the safe room.', INSIDE, PRIN),
    ('In the timeline, what proved the gap?', 'Lab → payroll allowed', 'A rumour in the office', 'Reboot',
     'A successful test and the permitting rule prove it.', INSIDE, m('PARALLEL')),
    ('Good status line?', 'Lab path closed; users OK', 'We were hacked badly over the weekend', 'Fine',
     'Accurate, calm, specific.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking segmentation finding.',
    'A lab PC can reach the payroll server.',
    'You confirm it with a port test.',
    'You note that users reach the file server too.',
    'You find a “permit any” rule.',
    'You propose one deny for lab to server.',
    'You retest both paths after the change.',
], 'Prove the gap, protect what must work, change one rule.'), (
    'A hotel finds that guest keys open the safe room. The fix is to recode one door, not lock every guest out of their '
    'rooms. A segmentation gap is fixed with one precise rule, then both paths are tested.',
    [('Guest key', 'lab PC'), ('Safe room', 'payroll server'), ('Recoding one door', 'one deny rule'), ('Guest rooms still open', 'user paths still work')],
    'Hotels can see who opened a door. You need ACL hit counts or logs to see it.'),
    ('flow', 'Segmentation finding', ['Lab → payroll OK', 'Users → files OK', 'Permit any found', 'Deny lab → servers', 'Retest both'], 2),
    'The red box is the cause. Testing user paths before and after protects what must keep working.',
    'Write a timeline for closing a lab-to-server path without breaking users.',
    order('Order the steps.', ['Test the gap', 'Test user paths', 'Find the rule', 'One deny', 'Retest both'], 'Prove, protect, change, verify.'), ACL)

_add('5.3', 'standard-of-work', T, [
    ('User path tested OK. Record it?', 'Yes, it is a baseline', 'No, nothing was wrong there', 'Skip',
     'It proves the fix will not break users.', m('NEG'), m('NEG')),
    ('Rewriting the whole ACL to close one gap is…', 'A risky change', 'A clean, tidy improvement', 'Required',
     'A full rewrite risks many paths at once.', m('PARALLEL'), m('PARALLEL')),
    ('In the gardener story, one fence panel at a time is?', 'One rule change', 'Rebuild the whole fence', 'No notes',
     'Fix one panel, check, note.', m('PARALLEL'), m('NEG')),
    ('In the chart, which is “avoid”?', 'Rewrite the ACL', 'Test the user paths', 'Note rule',
     'Rewrites hide which line broke things.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'ACL 120 line 15 deny lab 10:30', 'Tidied up the ACL a bit this morning', 'OK',
     'Rule, line, time.', m('NEG'), m('CHECKLIST')),
], ([
    'Segmentation work has two habits.',
    'Write down paths that must keep working.',
    'Test them before and after.',
    'Change one rule at a time.',
    'Never rewrite the whole ACL for one gap.',
], 'Baseline the good paths and change one rule.'), (
    'A gardener with a gap in a fence replaces one panel and checks the dog cannot get out. Rebuilding the whole fence '
    'might leave new gaps. ACL fixes are the same: one panel at a time.',
    [('Fence panel', 'ACL line'), ('Dog getting out', 'unwanted path'), ('Rebuilding the fence', 'rewriting the ACL'), ('Garden notes', 'ticket')],
    'A fence gap is visible. An ACL gap is not, so you test both the gap and the good paths.'),
    ('two', 'Segmentation standard of work', (('Do', ['Test user paths', 'Add one deny', 'Retest both']),
                                              ('Avoid', ['Skipping the baseline', 'Rewriting the ACL', 'No retest']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “tidied up the ACL” as a standard line with ACL, line, action, time and retest.',
    reveal('Rewrite: “tidied up the ACL”.', '10:30 ACL 120 line 15: deny 10.30.0.0/24 → 10.50.0.0/24; users→files OK 10:32.'), ACL)

_add('5.3', 'practice-standard-for-this-lesson', T, [
    ('First line on a segmentation checklist?', 'Draw the zones', 'Delete all the existing rules', 'Reboot',
     'Know the zones before testing paths.', PRIN, m('PARALLEL')),
    ('Pass sign for “lab → server blocked”?', 'Port test fails', 'No complaints from users', 'Silence',
     'A failed test from lab to server proves the block.', INSIDE, m('CHECKLIST')),
    ('In the map story, the legend is?', 'The pass sign', 'The paper the map uses', 'Ink',
     'It tells you what “good” looks like.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “deny added”?', 'Retest both paths', 'Remove the user VLAN', 'Reboot',
     'Retest the blocked path and the allowed path.', m('CHECKLIST'), m('PARALLEL')),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every ACL syntax form', 'Read docs',
     'Explain segmentation plainly, then test it.', m('RECALL'), m('JARGON')),
], ([
    'Explain segmentation without notes.',
    'Then test zones in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start by drawing the zones.',
    'Test what should pass and what should fail.',
    'Each step has a pass sign and a fail note.',
], 'A segmentation checklist tests both allowed and blocked paths.'), (
    'A map with a legend shows which roads are open and which are closed. A segmentation checklist is that map: each '
    'zone, each path, and whether it should be open.',
    [('Map legend', 'pass signs'), ('Open road', 'allowed path'), ('Closed road', 'denied path'), ('Survey notes', 'ticket')],
    'Maps rarely change. Networks gain new servers, so the zone map needs updates.'),
    ('flow', 'Segmentation checklist', ['Draw zones', 'Test allowed', 'Test denied', 'Read rule hits', 'Record']),
    'These boxes outline the checklist from left to right. Under each box, add the pass sign you expect and the note you will write if it fails.',
    'Write a five-line segmentation checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Draw zones', 'Test allowed', 'Test denied', 'Rule hits', 'Record'], 'Map, test, prove.'), ACL)

_add('5.3', 'beyond-the-quiz', T, [
    ('What does a segment need to be real?', 'Enforced rules', 'A clever and secret name', 'A colour',
     'Without enforcement, a segment is a label.', SSIDSEG, MACF),
    ('The inter-VLAN ACL is removed. What breaks?', 'The boundary', 'All user internet access', 'DNS',
     'Zones can reach each other freely.', INSIDE, m('RECALL')),
    ('In the ship story, bulkheads are?', 'Segments', 'The ship’s paint', 'Sails',
     'Bulkheads keep a leak in one compartment.', INSIDE, PRIN),
    ('In the chart, which test splits rule from routing?', 'Rule hit counts', 'Reboot every switch', 'Ask',
     'Hits show the rule matched.', m('RECALL'), m('PARALLEL')),
    ('When do you escalate a segmentation gap?', 'Needs approval', 'Never, fix it live now', 'Before tests',
     'Escalate for approval and a change window.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every segmentation case.',
    'Know what a segment needs: enforced rules.',
    'Know what breaks without them: the boundary.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Know when changes need approval.',
], 'A boundary is only real if something enforces it.'), (
    'A ship has watertight bulkheads. A leak in one compartment stays there. A ship with open bulkhead doors sinks from a '
    'single leak. Segments with “permit any” rules are open bulkhead doors.',
    [('Compartment', 'segment'), ('Bulkhead door', 'ACL'), ('Leak', 'compromise'), ('Captain’s order', 'change approval')],
    'Water obeys physics. Attackers adapt, so segments must be tested, not assumed.'),
    ('two', 'Gap found: three causes', (('Cause', ['Permit any rule', 'ACL not applied', 'Wrong direction']),
                                        ('Deciding test', ['Read rule lines', 'Check interface', 'Check in/out']))),
    'Each cause has one test. Run them before proposing a fix.',
    'Write your own segmentation scenario: gap, three causes, deciding test, escalation note.',
    reveal('ACL exists but shows zero hits. Suspect?', 'Not applied, or applied in the wrong direction.'), ACL)

# ================================================================== 5.4 Capstone — Hardening Review
m = mc('5.4')
T = 'Capstone — Hardening Review'
_add('5.4', 'the-scenario', T, [
    ('What kind of exercise is this?', 'A paper review', 'A live production change', 'A pen test',
     'It is a review on a diagram, not a change.', m('PARALLEL'), m('RECALL')),
    ('What three zones are on the diagram?', 'User, server, firewall', 'Lab, cloud and guest Wi-Fi', 'None',
     'User VLAN, server VLAN and firewall.', PRIN, m('RECALL')),
    ('In the inspector story, the inspector does what?', 'Lists gaps', 'Fixes every gap', 'Nothing',
     'A review lists gaps; fixes come later with approval.', m('PARALLEL'), m('RECALL')),
    ('In the chart, the first step is?', 'Draw the path', 'Rank the risks first', 'Fix',
     'Draw how traffic flows before listing gaps.', PRIN, m('CHECKLIST')),
    ('Each gap needs?', 'Severity and owner', 'A quick silent fix', 'Nothing',
     'Severity and owner make it actionable.', m('ESCALATE'), m('PARALLEL')),
], ([
    'This is a paper review.',
    'The diagram has a user VLAN, a server VLAN and a firewall.',
    'Draw the paths traffic takes.',
    'List the gaps you find.',
    'Give each gap a severity and an owner.',
    'Do not change anything live.',
], 'Review on paper: paths, gaps, severity, owner.'), (
    'A building inspector walks through with a clipboard. She lists missing fire doors and blocked exits, rates them, and '
    'names who must fix each. She does not start rebuilding walls during the visit.',
    [('Inspector', 'reviewer'), ('Clipboard list', 'gap list'), ('Rating', 'severity'), ('Who must fix', 'owner')],
    'An inspector can see walls. You see a diagram, so you must trace paths carefully.'),
    ('flow', 'Hardening review', ['Draw paths', 'List gaps', 'Rate severity', 'Name owner', 'Report']),
    'These boxes are the review steps, from left to right. Nothing in any of them changes production; the report goes to the owners.',
    'In the ACL lab, trace the user-to-server path and list one gap with severity and owner.',
    order('Order the review.', ['Draw paths', 'List gaps', 'Rate severity', 'Name owner', 'Report'], 'Paper first.'), ACL)

_add('5.4', 'your-turn-scaffolded-checklist', T, [
    ('“Path drawn” means what?', 'Traffic flow shown', 'A nice picture of the office', 'Nothing',
     'Show how traffic goes from users to servers.', PRIN, m('CHECKLIST')),
    ('“Gaps listed” needs?', 'Specific gaps', 'A general feeling of risk', 'Nothing',
     'Name each gap clearly.', m('CHECKLIST'), m('CHECKLIST')),
    ('In the form story, a blank line means?', 'Unfinished', 'Optional for today', 'Done',
     'Do not skip lines.', m('CHECKLIST'), m('CHECKLIST')),
    ('In the chart, “severity + owner” needs?', 'Both fields', 'Only a severity number', 'Neither',
     'Severity without an owner goes nowhere.', m('ESCALATE'), m('CHECKLIST')),
    ('Which entry fills “gaps listed”?', 'Telnet open on FW mgmt', 'Some things on it look quite bad', 'OK',
     'A specific, checkable gap.', WEAK, m('CHECKLIST')),
], ([
    'Fill in each line on paper or in the ticket.',
    'Do not skip lines.',
    'Path drawn.',
    'Gaps listed.',
    'Severity and owner for each gap.',
    'Each line has specific details.',
    'Write the gap so the owner can find it.',
], 'Path, gaps, severity and owner, all specific.'), (
    'A home survey report lists each defect, how serious it is and which trade should fix it. “Some damp” helps nobody; '
    '“damp under kitchen window, medium, roofer” does. Your review needs that level.',
    [('Defect', 'gap'), ('How serious', 'severity'), ('Trade', 'owner'), ('Survey report', 'review checklist')],
    'A surveyor sees damp. You read configs and diagrams, so quote the exact setting.'),
    ('two', 'Checklist filled in', (('Line', ['Path drawn', 'Gaps listed', 'Severity + owner']),
                                    ('Example', ['Users → FW → servers', 'Telnet on FW mgmt', 'High, network team']))),
    'The right column shows good entries.',
    'Fill the three lines for your lab diagram.',
    reveal('Fill one gap with severity and owner.', 'Permit any user→server on FW rule 9 — High — security team.'), ACL)

_add('5.4', 'common-beginner-mistakes', T, [
    ('Why not fix gaps live during the review?', 'Unapproved change', 'It is far too quick', 'It is fine',
     'Silent fixes on production break change control.', m('PARALLEL'), m('ESCALATE')),
    ('What should you do instead?', 'Report with owner', 'Fix it quietly tonight', 'Ignore',
     'Report the gap with severity and owner.', m('ESCALATE'), m('PARALLEL')),
    ('In the inspector story, rebuilding during the visit is?', 'A silent fix', 'Good service', 'Normal',
     'Inspectors report; builders fix with approval.', m('PARALLEL'), m('RECALL')),
    ('In the chart, the fix for the mistake is?', 'Change request', 'Quiet edit at night', 'Wait',
     'Raise a change request.', m('PARALLEL'), m('ESCALATE')),
    ('Which entry avoids the mistake?', 'CR-123 raised for FW', 'Fixed it live, no notes', 'Done',
     'A change request, not a silent fix.', m('PARALLEL'), m('NEG')),
], ([
    'One mistake is common here.',
    'Making silent fixes on production during a review.',
    'A review is paper only.',
    'Fixes need a change request and approval.',
    'Report the gap with severity and owner.',
], 'Review means report; changes go through change control.'), (
    'A home inspector who starts knocking down walls during the inspection causes chaos. The owner did not approve it and '
    'nobody planned it. Silent production fixes during a review are that.',
    [('Inspector', 'reviewer'), ('Knocking down walls', 'silent production fix'), ('Owner’s approval', 'change approval'), ('Builder’s plan', 'change request')],
    'Walls do not come back. Config changes can, but only if someone recorded the before state.'),
    ('two', 'Mistake and fix', (('Mistake', ['Silent live fix', 'No record kept']), ('Fix', ['Raise a change request', 'Report with owner']))),
    'Each row is a mistake and the habit that replaces it.',
    'Rewrite “fixed it live during the review” as a proper report line.',
    sort('Sort each action.', {'Mistake': ['Silent live fix', 'Undocumented edit'], 'Good': ['Change request', 'Report with owner']},
         'Report, then change with approval.'), ACL)

_add('5.4', 'check-your-understanding', T, [
    ('First beat in the explanation?', 'The diagram', 'The fixes you made', 'Blame',
     'Start with what you reviewed.', m('RECALL'), m('JARGON')),
    ('What proves a gap?', 'Rule or setting cited', 'A general bad feeling', 'Reboot',
     'Quote the setting that causes the gap.', m('NEG'), m('PARALLEL')),
    ('In the auditor story, the signed report is?', 'Verification', 'The coffee break after', 'Lunch',
     'A signed report confirms the review.', m('CHECKLIST'), m('RECALL')),
    ('In the chart, the last box is?', 'Owners accept', 'Close the ticket at once', 'Blame',
     'Owners accepting gaps closes the loop.', m('ESCALATE'), m('NEG')),
    ('Cannot explain it? Next?', 'Re-run the demo', 'Skip to the next one', 'Guess',
     'Re-run the steps.', m('RECALL'), m('RECALL')),
], ([
    'Explain the review in two minutes.',
    'Say what diagram you reviewed.',
    'Say the paths you drew.',
    'Say the gaps, with the setting that proves each.',
    'Say the severity and owner, and that owners accepted them.',
    'If you cannot, re-run the demo.',
], 'Diagram, paths, gaps with proof, owners accepted.'), (
    'An auditor presents findings: what was audited, how, what was found with evidence, and who accepted each finding. '
    'Your review explanation follows the same shape.',
    [('What was audited', 'diagram'), ('How', 'paths drawn'), ('Findings with evidence', 'gaps with settings cited'),
     ('Sign-off', 'owners accept')],
    'Auditors have formal sign-off. In a small team, a ticket comment from the owner can serve.'),
    ('flow', 'Two-minute explanation', ['Diagram', 'Paths', 'Gaps with proof', 'Owners accept']),
    'Four boxes, four beats, read from left to right. If one box is blank when you practise, re-run that part of the review before you explain it again.',
    'Explain your review to a peer in two minutes using the boxes.',
    order('Order the explanation.', ['Diagram', 'Paths', 'Gaps with proof', 'Owners accept'], 'Story order.'), ACL)
