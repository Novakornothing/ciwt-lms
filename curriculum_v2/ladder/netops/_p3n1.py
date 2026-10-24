"""Option B pass 3 — NETOPS chapter 1 bespoke ladders (core concepts, practice blocks, depth, capstone). Pending SME review."""
from curriculum_v2.ladder.netops._p3 import N, mc, src
from curriculum_v2.ladder.schema import order, reveal, sort

SECS = {}
MISS, RAND, PINGP, SKIP, METHOD = ('MC-L-NO1-MISSING-PIECE', 'MC-L-NO1-RANDOM-STATIC', 'MC-L-NO1-PING-PROVES-PORT',
                                   'MC-L-NO1-SKIP-LAYER', 'MC-L-NO1-METHOD-MISMATCH')
APIPA, ONLINK, TCPU, PORTMAP, UDPP, LAYER, NAMEF = ('MC-C-NO1-SPECIAL-ADDR', 'MC-NO1-MASK-ONLINK', 'MC-C-NO1-TCP-UDP',
                                                    'MC-C-NO1-PORT-MAP', 'MC-NO1-UDP-PROPERTIES', 'MC-C-NO1-OSI-LAYER',
                                                    'MC-NO1-NAME-FAIL-LOW-LAYER')
IPC = ('win-ipconfig', 'Run ipconfig /all and label address, mask, gateway and DNS; name what is missing.')
PSN = ('w11-powershell-net', 'Use Test-NetConnection on a TCP port and note what ping could not tell you.')
DNSB = ('win-dns-break', 'Work up the layers and write the layer name next to every test.')


def _add(label, sid, title, *a):
    SECS[(label, sid)] = N(label, sid, src(label, title), *a)


# ================================================================== 1.2 Addressing Ideas
m = mc('1.2')
T = 'Addressing Ideas'
_add('1.2', 'core-concepts', T, [
    ('A PC shows 169.254.20.7. What does that tell you?', 'No DHCP answer came', 'The DNS server is wrong', 'The gateway is up and fine',
     '169.254 is APIPA: the PC gave itself an address because no DHCP server answered.', APIPA, MISS),
    ('A PC has an address and mask but no gateway. What fails?', 'Off-subnet traffic', 'Every local printer', 'Its own network card',
     'With no gateway the PC can reach its own subnet but has no road out to other networks.', MISS, ONLINK),
    ('In the neighbourhood story, the gateway is what?', 'The road out', 'Your house number', 'The street name sign',
     'The gateway is the road out of the neighbourhood to everywhere else.', MISS, MISS),
    ('In the chart, which setting pairs with “no road out”?', 'Gateway', 'IPv4 address', 'Subnet mask value',
     'A missing gateway leaves local traffic working and stops everything remote.', MISS, ONLINK),
    ('A user has APIPA. What do you not do?', 'Type a random IP', 'Check the cable and port', 'Renew the lease',
     'A guessed static address hides the DHCP fault and may clash; check link and DHCP instead.', RAND, m('CHECKLIST')),
], ([
    'Read the host settings before you guess.',
    'Each setting does one job.',
    'The address names the PC. The mask marks its street.',
    'The gateway is the road out. DNS turns names into numbers.',
    'A 169.254 address means DHCP did not answer.',
    'A missing gateway means local works but nothing beyond does.',
    'These two faults look different once you read ipconfig.',
], 'Classify what is missing first: no lease looks like 169.254, no gateway looks like “local only”.'), (
    'Think of a housing estate. Your house number is your address. The estate boundary is the mask. The one road out of '
    'the estate is the gateway. If the road is missing, you can visit neighbours but never reach the shops in town.',
    [('House number', 'IP address'), ('Estate boundary', 'subnet mask'), ('Road out of the estate', 'default gateway'),
     ('Town directory', 'DNS server')],
    'A real estate can have several roads. A simple PC uses one default gateway, so if that one is wrong, every remote trip fails.'),
    ('two', 'Two faults, two patterns', (('169.254 address (APIPA)', ['No lease from DHCP', 'Even local may fail', 'Check link, then DHCP']),
                                         ('Address OK, no gateway', ['Lease or static is fine', 'Local works', 'Remote fails']))),
    'Compare the two columns. The left fault starts before an address exists. The right fault starts after the address, at the road out.',
    'Run ipconfig /all in the lab. Label the address, mask, gateway and DNS lines, then write which one would be missing in each pattern.',
    sort('Sort each symptom.', {'APIPA (no lease)': ['169.254.x.x address', 'No gateway listed at all'],
                                'Missing gateway only': ['Valid address, blank gateway', 'Printer works, website fails']},
         'Address first, road out second.'), IPC)

_add('1.2', 'incident-application', T, [
    ('Five desks get 169.254 addresses at once. What scope is this?', 'A shared DHCP fault', 'Five broken network cards',
     'Five users typing wrong passwords', 'Many desks failing to lease at once points to the shared DHCP path, not each PC.', m('ESCALATE'), MISS),
    ('Ipconfig shows a valid address. What do you write?', 'Address OK, with time', 'Nothing, it passed', 'Only the failed tests later',
     'A passed test is evidence; record it with a time so nobody repeats it.', m('NEG'), m('NEG')),
    ('In the detective story, the clue log is what?', 'The ticket timeline', 'The user’s desk drawer', 'The detective’s hat',
     'A detective logs each clue with a time; the ticket timeline does the same for tests.', m('NEG'), m('RECALL')),
    ('In the flow, what comes after “gateway ping fails”?', 'Write it, then escalate', 'Reimage the PC straight away', 'Change DNS too',
     'Record the failure and pass evidence to the owner; do not add unrelated changes.', m('PARALLEL'), m('ESCALATE')),
    ('Fifteen minutes in. What is a good status line?', 'Impact, known, next', 'It is all fixed now', 'Network is broken',
     'A calm status says who is affected, what is known and the next update; it never promises.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking addressing incident.',
    'At 09:02 five desks lose the internet.',
    'You run ipconfig on one. It shows 169.254.',
    'You check a second desk. Same result.',
    'That is a shared DHCP problem, not five PCs.',
    'You write each test with its time and result.',
    'You tell users what is known and when you will update.',
], 'Test in order, record every result, and send a calm, accurate update.'), (
    'A detective at a crime scene writes each clue in a notebook with the time found, including the dead ends. When the '
    'case passes to a colleague, the notebook saves hours. Your ticket timeline is that notebook for an addressing outage.',
    [('Detective’s notebook', 'ticket timeline'), ('Dead-end clue', 'a test that passed'), ('Colleague taking over', 'DHCP or network team'),
     ('Press statement', 'stakeholder status update')],
    'A detective can revisit the scene later. A network changes by the minute, so a test without a time stamp loses its value fast.'),
    ('flow', 'Addressing incident, first 15 minutes', ['09:02 ipconfig: 169.254', '09:04 second desk: same', '09:06 link lights OK',
                                                       '09:08 escalate DHCP', '09:15 status update']),
    'The boxes are the timeline. Notice that the link check passed and is still written down, because it rules out cables.',
    'Write a five-line ticket timeline for an office where three PCs show 169.254. Add one calm status sentence for the manager.',
    order('Order the incident steps.', ['Check one PC’s address', 'Check a second PC', 'Check link lights', 'Escalate with evidence',
                                        'Send status'], 'Scope, prove, escalate, inform.'), IPC)

_add('1.2', 'standard-of-work', T, [
    ('You pinged the gateway and it worked. Do you note it?', 'Yes, with the time', 'No, nothing was found', 'Only if it failed',
     'A negative (passed) result rules out the gateway; leaving it out wastes the next person’s time.', m('NEG'), m('NEG')),
    ('You set a static IP and changed DNS together. Problem?', 'Cause is unclear', 'It saves time for everyone', 'Nothing at all',
     'Two untracked changes at once hide which one mattered and can create new outages.', m('PARALLEL'), m('PARALLEL')),
    ('In the cooking story, tasting and noting is like what?', 'Recording each test', 'Buying more salt for the pot', 'Cooking faster',
     'A cook who notes every tasting knows which change fixed the dish; same for tests.', m('NEG'), m('PARALLEL')),
    ('In the chart, which habit belongs on the “do” side?', 'One change at a time', 'Several fixes at once', 'Skip passed tests',
     'One recorded change at a time keeps cause and effect clear.', m('PARALLEL'), m('NEG')),
    ('Which ticket line meets the standard?', 'Gateway ping OK 09:06', 'Tried stuff, works now', 'Fixed it',
     'A good line names the test, the result and the time.', m('NEG'), m('CHECKLIST')),
], ([
    'Two habits protect addressing work.',
    'First, write down tests that passed.',
    'A good gateway ping rules the gateway out.',
    'If you skip it, someone will test it again.',
    'Second, make one change at a time.',
    'Changing IP and DNS together hides the cause.',
    'It can also break something new.',
], 'Write passed tests and change one thing at a time.'), (
    'A cook adjusting soup adds one pinch of salt, tastes and writes “salt +1, better”. If she adds salt, pepper and lemon '
    'together, she cannot tell which helped. If she forgets to note “tasted, fine”, her helper tastes again.',
    [('One pinch, then taste', 'one change, then test'), ('Note “tasted, fine”', 'record a passed test'),
     ('Salt, pepper and lemon at once', 'parallel untracked changes'), ('The helper', 'the next technician')],
    'Soup can be thrown out and restarted. A live network cannot, so a wrong double change hits real users straight away.'),
    ('two', 'Standard of work', (('Do', ['Note passed tests with time', 'One change, then retest', 'Write how to undo it']),
                                 ('Avoid', ['Skipping “nothing found”', 'IP and DNS changed together', 'Untracked edits']))),
    'Read across each row: the left habit is the cure for the right mistake beside it.',
    'Rewrite this ticket line to meet the standard: “Changed some settings, works now.” Name the test, the result and the time.',
    reveal('Rewrite: “Changed some settings, works now.”', '09:10 set DNS to 10.0.0.10 (was blank); nslookup OK 09:11. Undo: clear DNS.'), IPC)

_add('1.2', 'practice-standard-for-this-lesson', T, [
    ('What should a good checklist step include?', 'Pass sign and fail note', 'Just the command name to type', 'A screenshot only',
     'Each step needs what good looks like and what you write if it fails.', m('CHECKLIST'), m('CHECKLIST')),
    ('How many steps is a usable ticket checklist?', 'About 5 to 9', 'One big step', 'Forty detailed steps',
     'Five to nine steps is short enough to use and long enough to cover the path.', m('CHECKLIST'), m('RECALL')),
    ('In the pilot story, the pre-flight card is what?', 'Your checklist', 'The plane’s fuel', 'The control tower',
     'A pre-flight card lists checks with pass signs, like a ticket checklist.', m('CHECKLIST'), m('RECALL')),
    ('In the chart, what is the pass sign for “run ipconfig”?', 'Address, mask, gateway', 'The command window opens', 'A long output',
     'Pass means all the expected fields are present and valid.', MISS, m('CHECKLIST')),
    ('How do you show you can teach the topic?', 'Explain it with no notes', 'Read the slides aloud to them', 'Copy the glossary',
     'The standard is walking a peer through the topic without notes, then doing the checks.', m('RECALL'), m('JARGON')),
], ([
    'The standard is simple to say.',
    'Explain addressing to a peer without notes.',
    'Then run the checks on a lab PC.',
    'Build a short checklist of 5 to 9 steps.',
    'Each step has a pass sign.',
    'Each step has a note you write if it fails.',
    'Good work is judged by restored service and trusted notes.',
], 'A checklist step is only finished when it says what good looks like and what to write if it fails.'), (
    'Pilots use a pre-flight card. Each line says what to check and what “good” is: fuel full, flaps move. If a line fails, '
    'the card says what to do next. An addressing checklist works like that card for a PC with no network.',
    [('Pre-flight card', 'ticket checklist'), ('Fuel gauge reads full', 'ipconfig shows address, mask, gateway'),
     ('Abort note', 'failure note in the ticket'), ('Co-pilot', 'the peer you teach')],
    'A pilot’s card never changes between flights. Your checklist should be updated when a new failure teaches you a better step.'),
    ('flow', 'A five-step addressing checklist', ['Link light on', 'ipconfig: lease?', 'Ping gateway', 'Ping 8.8.8.8', 'Resolve a name']),
    'Each box is one checklist line. Under each, a real checklist would add the pass sign and the note to write if it fails.',
    'Write your own five-step addressing checklist. For each step add one pass sign and one failure note.',
    order('Order the checklist.', ['Link light', 'Lease (ipconfig)', 'Gateway ping', 'Outside IP ping', 'Name lookup'],
          'Bottom of the stack first.'), IPC)

_add('1.2', 'beyond-the-quiz', T, [
    ('What does DHCP need upstream to give a lease?', 'A path to the server', 'A working DNS zone and records', 'A browser open',
     'The client must reach a DHCP server (directly or via relay) before any lease exists.', m('RECALL'), MISS),
    ('Gateway down. What breaks downstream?', 'Every off-subnet trip', 'Only the local printer queue', 'The network card',
     'Without the gateway, all remote destinations fail while local ones work.', MISS, m('RECALL')),
    ('In the plumbing story, upstream is like what?', 'The water main', 'The tap handle', 'The sink colour',
     'The water main feeds the house; DHCP and gateway feed the PC’s connectivity.', m('RECALL'), m('RECALL')),
    ('In the chart, which cause matches “169.254 on one PC only”?', 'Its cable or port', 'The DHCP server for all floors', 'The ISP link',
     'One PC alone with APIPA points to its own link; many PCs point to DHCP.', m('ESCALATE'), MISS),
    ('When should a DHCP scope issue be escalated?', 'When you lack access', 'Never, just keep going', 'Before any test',
     'Escalate with evidence once the fault sits in a system you cannot change.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot show every addressing fault.',
    'Learn what each piece needs and what it feeds.',
    'DHCP needs a path to its server.',
    'The gateway feeds every trip off the subnet.',
    'Write your own scenario: one symptom, three causes.',
    'Pick the test that tells the causes apart.',
    'Explain it to a non-technical user in plain words.',
], 'Know the dependencies, invent a scenario, and know when to escalate.'), (
    'Plumbing in a house has an upstream and a downstream. The water main feeds everything. A blocked main leaves every '
    'tap dry; a broken tap only affects one sink. Addressing works the same: shared parts fail many users.',
    [('Water main', 'DHCP server and gateway'), ('One tap', 'one PC’s port or cable'), ('All taps dry', 'whole-office APIPA'),
     ('Calling the water company', 'escalating to the network team')],
    'Pipes leak visibly. Addressing faults are invisible, so you prove them with ipconfig and ping, not by looking.'),
    ('two', 'One symptom, three causes', (('Cause', ['Cable or port', 'DHCP server or scope', 'Relay on the router']),
                                          ('Test that tells them apart', ['Neighbour desk works?', 'Many desks 169.254?', 'Other VLANs lease?']))),
    'Each row pairs a cause with the one test that separates it. This is the scenario the original section asks you to build.',
    'Build your own scenario: symptom “PC shows 169.254”, three causes, the deciding test, and the note you would leave.',
    reveal('One PC has 169.254; its neighbour leases fine. Most likely?', 'Its cable, port or NIC — not the DHCP server.'), IPC)

# ================================================================== 1.3 TCP versus UDP
m = mc('1.3')
T = 'TCP versus UDP'
_add('1.3', 'core-concepts', T, [
    ('Calls connect but have no audio. Which transport is suspect?', 'UDP media', 'TCP signalling', 'ICMP ping traffic',
     'Calls set up over signalling but carry audio over UDP; blocked UDP gives silent calls.', TCPU, PINGP),
    ('Which is true of TCP?', 'It tracks delivery', 'It drops order checks', 'It has no handshake',
     'TCP sets up a session and tracks and resends segments.', TCPU, UDPP),
    ('In the post story, UDP is like what?', 'An untracked postcard', 'A signed-for parcel', 'A courier with a receipt',
     'UDP sends and moves on, like a postcard with no tracking.', UDPP, TCPU),
    ('In the chart, a firewall rule must match which two things?', 'Protocol and port', 'Port and cable colour', 'Name and speed',
     'A rule allows a specific protocol (TCP or UDP) and port; one without the other fails.', PORTMAP, PINGP),
    ('Ping works to the server. What does it prove?', 'The host answers', 'The app port is open', 'UDP is allowed',
     'Ping is ICMP; it proves reachability, not that a TCP or UDP port is open.', PINGP, PINGP),
], ([
    'TCP and UDP both carry data.',
    'TCP sets up a session first.',
    'It tracks each piece and resends lost ones.',
    'UDP just sends and moves on.',
    'Voice and video often use UDP.',
    'A firewall must match the protocol and the port.',
    'Allowing TCP 5060 does not allow UDP audio.',
], 'Know which transport the app uses, then check the rule matches both protocol and port.'), (
    'Sending a signed-for parcel means a receipt at each step and a resend if lost. Dropping postcards in the box is '
    'faster, but nobody checks they arrive. TCP is the parcel; UDP is the postcard. A firewall is the post office rule '
    'about which kind of mail is accepted at which window.',
    [('Signed-for parcel', 'TCP segment'), ('Postcard', 'UDP datagram'), ('Window number', 'port number'),
     ('Post office rule', 'firewall rule')],
    'A late postcard still arrives eventually. Late UDP voice packets are useless and are simply skipped.'),
    ('two', 'TCP and UDP side by side', (('TCP', ['Handshake first', 'Tracks and resends', 'Web, email, SSH']),
                                         ('UDP', ['No handshake', 'No resend', 'Voice, video, DNS queries']))),
    'Each row compares the two. A firewall rule written for the left column will not let the right column through.',
    'In the lab, run Test-NetConnection to a TCP port. Write one sentence on why this cannot test a UDP media port.',
    sort('Sort by usual transport.', {'TCP': ['HTTPS web page', 'SSH login'], 'UDP': ['Voice audio stream', 'Streaming video']},
         'Transport decides the rule you need.'), PSN)

_add('1.3', 'incident-application', T, [
    ('Users report silent calls. What do you test first?', 'TCP signalling port', 'Reboot the phones', 'Their Wi-Fi password',
     'Prove the call sets up (TCP), then look at the UDP media rule.', TCPU, m('PARALLEL')),
    ('TCP 5060 connects at 14:05. Do you write it?', 'Yes, it rules out setup', 'No, because it simply passed', 'Only at the end',
     'A passed signalling test narrows the fault to media; write it with its time.', m('NEG'), m('NEG')),
    ('In the restaurant story, the order slip is like what?', 'Signalling', 'The meal itself', 'The bill',
     'The order slip (signalling) sets up the meal; the food (media) is a separate delivery.', TCPU, UDPP),
    ('In the timeline, where does the fault sit?', 'The UDP media rule', 'The phone handset itself', 'The TCP port',
     'Signalling passed, media failed: the UDP range in the rule is the fault.', PORTMAP, TCPU),
    ('Which status is calm and accurate?', 'Media blocked; fix soon', 'Every phone is dead for good', 'Hackers in the system',
     'Say what is affected and what is known without alarm or promises.', m('STATUS'), m('JARGON')),
], ([
    'Here is a real-looking transport incident.',
    'At 14:00 calls connect but nobody hears audio.',
    'You test TCP 5060. It connects at 14:05.',
    'So call setup works.',
    'You check the firewall rule. The UDP media range is missing.',
    'You record both results with times.',
    'You send the rule owner the evidence.',
], 'Split setup from media, test each, and hand the owner a precise rule gap.'), (
    'In a restaurant, you hand an order slip to the waiter, then the kitchen sends the food. If the slip arrives but the '
    'food never comes, the problem is the kitchen-to-table path, not your order. Calls work the same way.',
    [('Order slip', 'TCP signalling (5060)'), ('Food delivery', 'UDP audio stream'), ('Kitchen door locked', 'UDP range blocked'),
     ('Manager', 'firewall rule owner')],
    'A waiter will tell you the kitchen is closed. A firewall drops UDP silently, so you only learn it by testing.'),
    ('flow', 'Silent calls timeline', ['14:00 silent calls', '14:05 TCP 5060 OK', '14:08 rule check', '14:10 UDP range missing',
                                       '14:12 escalate'], 3),
    'The red box is where the evidence lands. The passed TCP test before it is what lets you point so precisely.',
    'Write a three-line escalation to the firewall team: symptom, tests with times, and the exact rule gap.',
    order('Order the call-fault tests.', ['Confirm silent calls', 'Test TCP signalling', 'Read the UDP rule', 'Escalate with times'],
          'Setup first, media second.'), PSN)

_add('1.3', 'standard-of-work', T, [
    ('Why record that ping to the call server worked?', 'It rules out reachability', 'It proves the UDP ports are open', 'It is not needed',
     'A passed ping rules out a dead host; it says nothing about UDP ports.', m('NEG'), PINGP),
    ('Opening all UDP ports and restarting phones at once is…', 'Two untracked changes', 'A tidy and quick fix for all', 'The standard',
     'Parallel changes hide the cause and can open new risk.', m('PARALLEL'), m('PARALLEL')),
    ('In the lab-science story, one variable means what?', 'One change per test', 'Many fixes at once to save time', 'No notes kept',
     'A scientist changes one variable at a time; so does a technician.', m('PARALLEL'), m('NEG')),
    ('In the chart, which belongs under “avoid”?', 'Open every port', 'Note TCP result', 'Retest after change',
     'Opening every port is a big untracked change and a security hole.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'UDP 10000-20000 added 14:20', 'Opened some ports, all OK now', 'Tweaked the firewall a bit',
     'A good line names the change, the range and the time.', m('NEG'), m('CHECKLIST')),
], ([
    'Two habits matter for transport faults.',
    'Write down tests that passed, like a good ping.',
    'That stops the next person repeating it.',
    'Make one change at a time.',
    'Never open every port and restart phones together.',
    'You would not know which step helped.',
    'You might also open a security hole.',
], 'Passed tests go in the ticket; changes go in one at a time.'), (
    'A science student testing plant growth changes only the water, not the light and soil too. She notes every '
    'measurement, even “no change”. A firewall fix needs the same discipline, or the results mean nothing.',
    [('One variable', 'one firewall change'), ('“No change” measurement', 'passed test in the ticket'),
     ('Changing light, soil and water', 'opening ports and rebooting at once'), ('Lab notebook', 'ticket notes')],
    'A plant experiment harms nobody if it fails. An “open all ports” change can expose the company to attack.'),
    ('two', 'Transport standard of work', (('Do', ['Note ping OK with time', 'Add only the UDP range needed', 'Retest one call']),
                                           ('Avoid', ['Skipping passed results', 'Opening every port', 'Rebooting phones too']))),
    'Each row pairs the habit with the mistake it prevents. The middle row is the security reason for one change at a time.',
    'Rewrite “opened ports and rebooted, works” as a standard line with the exact range, the time and the retest.',
    reveal('Rewrite: “opened ports and rebooted, works”.', '14:20 allowed UDP 10000–20000 to call server; test call has audio 14:22.'), PSN)

_add('1.3', 'practice-standard-for-this-lesson', T, [
    ('First line of a call-fault checklist?', 'Name app protocol', 'Reboot the server', 'Open all ports',
     'Start by knowing which protocol and port the app uses.', m('CHECKLIST'), m('PARALLEL')),
    ('Pass sign for “test TCP port”?', 'TcpTestSucceeded True', 'Ping replies', 'The test window closes cleanly',
     'Test-NetConnection reports TcpTestSucceeded True when the port answers.', PINGP, m('CHECKLIST')),
    ('In the checklist story, what is the fail note?', 'What you write if it fails', 'What the app licence costs', 'Who sits nearby',
     'Every step needs a note to write on failure, like a flight card abort line.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, which step can ping not cover?', 'Test the TCP port', 'Ping the server', 'Name the protocol',
     'Ping cannot tell you whether a TCP or UDP port is open.', PINGP, PINGP),
    ('Peer test: what shows you know TCP vs UDP?', 'Explain it with no notes', 'Recite long lists of ports', 'Show a long trace',
     'Teach it plainly, without notes, then run the checks.', m('RECALL'), m('JARGON')),
], ([
    'Teach TCP and UDP to a peer without notes.',
    'Then run the checks on a lab PC.',
    'Build a checklist of 5 to 9 steps.',
    'Start by naming the app’s protocol and port.',
    'Each step has a pass sign, like TcpTestSucceeded True.',
    'Each step has a note to write if it fails.',
    'Notes must be ones another technician can trust.',
], 'A transport checklist starts with the protocol and port, and every step has a pass sign.'), (
    'A security guard’s round sheet lists each door, what “locked” looks like and who to call if one is open. The sheet '
    'is short and in order. Your transport checklist is that sheet for an app that will not connect.',
    [('Round sheet', 'ticket checklist'), ('Door number', 'port number'), ('“Locked” sign', 'pass sign'),
     ('Who to call', 'failure note and escalation')],
    'Doors stay put. Apps change ports after upgrades, so the first step is always to confirm the protocol and port again.'),
    ('flow', 'Transport checklist', ['Name protocol and port', 'Ping server', 'Test TCP port', 'Check UDP rule', 'Verify with user']),
    'Five boxes, five checklist lines. The third and fourth boxes are where ping stops being useful.',
    'Write a five-line transport checklist with a pass sign and a fail note on each line, using the boxes as your outline.',
    order('Order the checklist.', ['Name protocol and port', 'Ping the server', 'Test TCP port', 'Check UDP rule', 'Verify with user'],
          'Identity, reach, port, rule, user.'), PSN)

_add('1.3', 'network-operations-depth', T, [
    ('At which layer do TCP and UDP live?', 'Transport', 'Data link', 'Physical layer',
     'TCP and UDP are transport-layer protocols (layer 4).', LAYER, LAYER),
    ('Ping works, the app port fails. Policy or reachability?', 'Policy', 'Reachability', 'Cabling fault',
     'The host answers, so the path exists; a rule is blocking the port.', PINGP, SKIP),
    ('In the building story, the floor is what?', 'The layer you test', 'The tool you happen to own', 'The user’s desk',
     'Naming the floor you are on keeps tests organised by layer.', LAYER, SKIP),
    ('In the chart, a firewall deny sits at which kind of fault?', 'Policy', 'Physical', 'Addressing',
     'A deny rule is policy: the path exists but is not allowed.', PINGP, LAYER),
    ('Which comparison helps most here?', 'On-net vs off-net', 'Old PCs versus new PCs', 'Morning vs night',
     'Comparing on-net and off-net behaviour shows where a rule or route steps in.', METHOD, m('RECALL')),
], ([
    'This depth note links layers to TCP and UDP.',
    'TCP and UDP live at the transport layer.',
    'Say which layer each test checks.',
    'Ping checks the network layer only.',
    'A port test checks transport.',
    'Firewalls and NAT change which paths exist.',
    'Ask: is this policy, or is it reachability?',
], 'Name the layer, then decide if the failure is a rule (policy) or a missing path.'), (
    'A large office building has floors. A lift engineer says “I am testing floor 4” before starting. If floor 3 works and '
    'floor 4 does not, the fault is on floor 4. A badge reader on a floor door is like a firewall: the floor exists, but '
    'you are not let in.',
    [('Floor', 'layer'), ('Lift reaches the floor', 'reachability (ping)'), ('Badge reader refuses', 'policy (firewall deny)'),
     ('Engineer naming the floor', 'labelling each test with a layer')],
    'Buildings have one door per floor. A host has thousands of ports, so “the floor works” says little about one port.'),
    ('two', 'Policy or reachability?', (('Reachability fault', ['Ping fails', 'No route or no link', 'Fix path']),
                                        ('Policy fault', ['Ping OK, port refused', 'Rule or NAT blocks', 'Fix rule']))),
    'Use the top row to choose a column. Each column then tells you which team and which change is likely.',
    'In the lab, ping a host, then test a TCP port on it. Label each result with its layer and say policy or reachability.',
    sort('Sort each finding.', {'Reachability': ['Ping times out', 'No route to host'], 'Policy': ['Ping OK, port blocked',
                                                                                                  'Rule denies UDP range']},
         'Layer names make the split obvious.'), PSN)

_add('1.3', 'beyond-the-quiz', T, [
    ('What does a voice app need upstream for audio?', 'UDP allowed end to end', 'A faster CPU and nothing else', 'A bigger monitor',
     'Audio depends on UDP media reaching both ends through every rule.', m('RECALL'), UDPP),
    ('UDP blocked. What breaks downstream?', 'Audio, not setup', 'Call setup and nothing else', 'Nothing visible',
     'Signalling (TCP) still works, so calls connect silently.', TCPU, m('RECALL')),
    ('In the courier story, the depot rules are what?', 'Firewall rules', 'The parcels on the shelves', 'The van',
     'Depot rules decide what passes, like firewall rules for protocols and ports.', PORTMAP, m('RECALL')),
    ('In the chart, which test tells the causes apart?', 'TCP then UDP test', 'Reboot all phones', 'Ask the user',
     'Testing setup then media separates a dead server from a blocked UDP range.', m('PARALLEL'), m('JARGON')),
    ('When do you escalate a firewall rule issue?', 'When another team owns it', 'Never escalate, keep trying', 'Before testing',
     'Escalate with evidence once the fault is in a rule you do not own.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every transport fault.',
    'Know what an app needs upstream.',
    'A call needs TCP for setup and UDP for audio.',
    'Know what breaks downstream when UDP is blocked.',
    'Build your own scenario with three causes.',
    'Pick the test that tells them apart.',
    'Explain it to a user without jargon.',
], 'Map the dependencies, design a deciding test, and escalate rules you do not own.'), (
    'A courier depot has rules: parcels pass, loose letters do not. A shop whose orders are parcels is fine; a shop that '
    'sends letters finds nothing arrives. Apps are the same: the depot (firewall) rules decide which transport gets through.',
    [('Depot rules', 'firewall rules'), ('Parcel', 'TCP traffic'), ('Loose letter', 'UDP traffic'), ('Shop owner', 'app owner')],
    'A courier tells the sender a letter was refused. Firewalls often drop silently, so you prove it by testing.'),
    ('two', 'Silent calls: three causes', (('Cause', ['Server down', 'Wrong TCP port', 'UDP media blocked']),
                                           ('Deciding test', ['Ping server', 'Test TCP 5060', 'Check UDP rule']))),
    'Each cause has one test that confirms or rules it out. Run them in this order and write each result.',
    'Build your own transport scenario: symptom, three causes, deciding test, and a plain sentence for the user.',
    reveal('Calls connect, no audio. Plain sentence for the user?', 'Calls connect but a security setting blocks the sound; the owner is fixing it now.'), PSN)

# ================================================================== 1.4 Capstone — Layer Mapping
m = mc('1.4')
T = 'Capstone — Layer Mapping'
_add('1.4', 'the-scenario', T, [
    ('A user cannot reach a website. What must each test carry?', 'A layer name', 'A colour code', 'A user rating',
     'The capstone asks you to say which layer every tool tests.', LAYER, SKIP),
    ('Which test checks the physical layer?', 'Link light', 'nslookup', 'Opening the site',
     'The link light is physical; nslookup is DNS (application).', LAYER, LAYER),
    ('In the doctor story, checking breathing first is like?', 'Testing low layers first', 'Asking which site they wanted', 'Skipping notes',
     'Triage checks basics first, like starting at the lower layers.', SKIP, METHOD),
    ('In the chart, nslookup tests which layer?', 'Application (DNS)', 'Physical (the cable)', 'Data link (switch)',
     'nslookup tests name resolution, an application-layer service.', LAYER, NAMEF),
    ('Ping to gateway fails. What next?', 'Stop and record it', 'Test the website again', 'Clear the browser',
     'Stop at the first hard failure; higher-layer tests cannot pass.', SKIP, SKIP),
], ([
    'A user cannot reach a website.',
    'You must test layer by layer.',
    'Say the layer for each tool you use.',
    'Link light is physical. Ping is network.',
    'nslookup is DNS. A port test is transport.',
    'Stop at the first hard failure.',
], 'Every test gets a layer label, and the first failure is where you stop.'), (
    'A doctor at triage checks breathing before a broken finger. She says out loud what she is checking. A website fault '
    'gets the same order: physical first, application last, and every check is named.',
    [('Breathing', 'link light (physical)'), ('Pulse', 'ping (network)'), ('Asking the patient', 'nslookup (DNS)'),
     ('Treating the finger', 'opening the site')],
    'A doctor can see a patient. You cannot see a packet, so you need tools and you must name what each proves.'),
    ('flow', 'Website unreachable: layer by layer', ['Link light', 'ipconfig', 'Ping gateway', 'nslookup', 'Open site port']),
    'Read from left to right. Each box is a layer step. The capstone answer is this order with a layer name on each box.',
    'Open the DNS lab. Run the steps in the chart and write the layer name next to every result.',
    order('Order the layered tests.', ['Link light', 'ipconfig', 'Ping gateway', 'nslookup', 'Open site port'],
          'Low layers before high.'), DNSB)

_add('1.4', 'your-turn-scaffolded-checklist', T, [
    ('What does “stop at first hard failure” mean?', 'Fix that layer first', 'Run all tests anyway', 'Skip to the website',
     'Higher tests cannot pass while a lower layer is down.', SKIP, SKIP),
    ('What makes notes readable?', 'Test, layer, result, time', 'Long raw output pasted in', 'Only “fixed”',
     'Short lines with test, layer, result and time can be trusted.', m('CHECKLIST'), m('NEG')),
    ('In the ladder story, a broken rung means what?', 'Stop climbing there', 'Jump two rungs', 'Use the top rung only',
     'You cannot skip a broken rung; fix it first.', SKIP, METHOD),
    ('In the chart, which line is filled for ping?', 'Network layer', 'Physical layer', 'Application layer',
     'Ping (ICMP) tests the network layer.', LAYER, LAYER),
    ('A line is blank. What do you do?', 'Fill it in', 'Skip it', 'Guess later',
     'The checklist says do not skip lines.', m('CHECKLIST'), m('CHECKLIST')),
], ([
    'Fill in the checklist on paper or in the ticket.',
    'Do not skip lines.',
    'Label each test with its layer.',
    'Stop at the first hard failure.',
    'Write short, readable notes.',
    'Each note has the test, layer, result and time.',
], 'Label, stop at the first failure, and keep every line readable.'), (
    'Climbing a ladder, you test each rung before standing on it. If one cracks, you stop and fix it; you do not leap to '
    'the top. The checklist is that ladder for a website fault, one rung per layer.',
    [('Rung', 'one layered test'), ('Cracked rung', 'first hard failure'), ('Stopping to fix', 'working that layer'),
     ('Tag on the rung', 'layer label on the note')],
    'A ladder is the same every day. Network layers can fail in odd ways, so a passing rung today is still worth noting.'),
    ('two', 'Checklist lines', (('Line', ['Each test labelled with a layer', 'Stop at first hard failure', 'Notes readable']),
                                ('Example', ['Ping GW — network — OK 10:02', 'nslookup fails — stop here', 'Test, layer, result, time']))),
    'Each row shows a checklist line and an example of it filled in well.',
    'Copy the three checklist lines into a ticket note and fill them with your own lab results.',
    reveal('Fill: “ping 10.0.0.1 failed”. Add layer and action.', 'Network layer — failed 10:03 — stop; check gateway before DNS.'), DNSB)

_add('1.4', 'common-beginner-mistakes', T, [
    ('A user says “network down”. Best first reply?', 'Which layer fails?', 'Reboot the router right now', 'Reinstall Windows',
     'Name the failing layer instead of a vague “network down”.', SKIP, m('PARALLEL')),
    ('Why is testing only the URL weak?', 'It skips lower layers', 'It is too fast to read', 'URLs are fake',
     'Testing only the website hides where the stack breaks.', SKIP, METHOD),
    ('In the car story, “car broken” is like what?', '“Network down”', 'A layer label on a note', 'A test result',
     'A vague complaint like “car broken” tells the mechanic nothing; name the part.', SKIP, LAYER),
    ('In the chart, the fix for “only the URL” is?', 'Test lower layers', 'Clear the browser cache', 'Try another site',
     'Start lower: link, address, gateway, DNS.', SKIP, SKIP),
    ('Which ticket line avoids both mistakes?', 'DNS fails; gateway OK', 'Network is down, call the ISP', 'Site broken',
     'It names the failing layer and records the passed lower test.', m('NEG'), SKIP),
], ([
    'Two mistakes are very common.',
    'First, calling everything “network down”.',
    'Instead, name the layer that failed.',
    'Second, testing only the website URL.',
    'Instead, test the lower layers first.',
    'A named layer tells the next person where to look.',
], 'Swap “network down” for a named layer, and test from the bottom.'), (
    'Telling a mechanic “the car is broken” wastes time. Saying “it starts, but the brakes squeal” sends them straight to '
    'the brakes. Testing only the website is like only turning the key and never checking the fuel.',
    [('“Car is broken”', '“network down”'), ('“Brakes squeal”', '“DNS fails, gateway OK”'), ('Only turning the key', 'only opening the URL'),
     ('Checking fuel and battery', 'testing lower layers')],
    'A mechanic can hear the noise. You must create the evidence with tests, so a vague report gives you nothing at all.'),
    ('two', 'Mistake and fix', (('Mistake', ['Calling it “network down”', 'Testing only the URL']),
                                ('Fix', ['Name the failing layer', 'Test lower layers first']))),
    'Each row is one beginner mistake and the habit that replaces it.',
    'Rewrite “network down, site broken” as a ticket line that names the failing layer and a passed lower test.',
    sort('Sort each note.', {'Weak': ['Network down', 'Site broken'], 'Strong': ['DNS fails, gateway ping OK',
                                                                               'Link OK, no lease']},
         'Strong notes name a layer.'), DNSB)

_add('1.4', 'check-your-understanding', T, [
    ('What four things go in a two-minute explanation?', 'Symptom, checks, cause, fix', 'Name, desk, phone and their boss', 'Tools I own',
     'The check asks for symptom, first three checks, what proved the cause and how you verified.', m('RECALL'), m('JARGON')),
    ('You cannot explain it in two minutes. What next?', 'Re-run the demo steps', 'Move on to the next one', 'Skip the capstone',
     'Re-run the live demonstration before moving on.', m('RECALL'), m('RECALL')),
    ('In the sports story, the replay is like what?', 'Re-running the demo', 'Ending the game early', 'Buying a new pair of boots',
     'A coach replays the clip until the move makes sense, like re-running the steps.', m('RECALL'), m('RECALL')),
    ('In the chart, what comes after “what proved the cause”?', 'How you verified', 'Who you blamed for it', 'Which tool cost',
     'Verification with the user ends the explanation.', m('JARGON'), m('RECALL')),
    ('Which shows you understood the fix?', 'User confirms it works', 'A green light on the switch', 'Nobody has complained yet',
     'The user confirming the site loads is real verification.', m('CHECKLIST'), m('NEG')),
], ([
    'Explain the ticket to a peer in two minutes.',
    'Say the symptom first.',
    'Say your first three checks.',
    'Say what proved the cause.',
    'Say how you checked the fix.',
    'If you cannot, re-run the demo steps.',
], 'If you can explain symptom, checks, cause and verification in two minutes, you are ready.'), (
    'A football coach asks a player to explain a goal: where the ball started, three passes, the shot and the replay '
    'that confirmed it. If the player cannot, they watch the clip again. Your ticket explanation follows the same shape.',
    [('Where the ball started', 'symptom'), ('Three passes', 'first three checks'), ('The shot', 'what proved the cause'),
     ('The replay', 'verification with the user')],
    'A replay never changes. A real fault can change while you test, so your times matter in the explanation.'),
    ('flow', 'Two-minute explanation', ['Symptom', 'First three checks', 'What proved it', 'How verified']),
    'The four boxes are the shape of the explanation. If one box is empty, re-run that part of the demonstration.',
    'Explain your layer-mapping ticket aloud to a peer in two minutes using the four boxes. Time yourself.',
    order('Order the explanation.', ['Symptom', 'First three checks', 'What proved the cause', 'How you verified'],
          'Story order makes it easy to follow.'), DNSB)
