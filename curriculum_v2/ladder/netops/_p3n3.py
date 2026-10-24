"""Option B pass 3 — NETOPS chapter 3 bespoke ladders (routing, WAN handoffs, enterprise WLAN, capacity capstone). Pending SME review."""
from curriculum_v2.ladder.netops._p3 import N, mc, src
from curriculum_v2.ladder.schema import order, reveal, sort

SECS = {}
CONN, DEMARC, RSSI, APID, POWER = ('MC-L-NO3-CONNECTED-STAYS', 'MC-L-NO3-DEMARC-SIDE', 'MC-L-NO3-RSSI-SIGN', 'MC-L-NO3-AP-IDS',
                                   'MC-L-NO3-MORE-POWER')
PREFIX, ADW, STARS, THIN, LANWAN, CHOV, SNR, SHKEY = (
    'MC-NO3-SHORTER-PREFIX', 'MC-NO3-AD-DYNAMIC-WINS', 'MC-NO3-TRACEROUTE-STARS', 'MC-NO3-THIN-EVIDENCE',
    'MC-NO3-LAN-FEATURE-AS-WAN', 'MC-NO3-CHANNEL-OVERLAP', 'MC-NO3-SNR-MATH', 'MC-NO3-SHARED-KEY-FOR-STAFF')
RTR = ('rtr-default-route', 'Read show ip route, find the default route and say where unknown traffic goes.')
WIFI = ('win-wifi-survey', 'Record SSID, band, channel and signal for each AP and note which channels overlap.')


def _add(label, sid, title, *a):
    SECS[(label, sid)] = N(label, sid, src(label, title), *a)


# ================================================================== 3.1 Routing Roles
m = mc('3.1')
T = 'Routing Roles'
_add('3.1', 'core-concepts', T, [
    ('What does a router join together?', 'Networks', 'Ports in one VLAN only', 'Users to their apps directly',
     'A router connects different networks (subnets) and forwards between them.', m('RECALL'), CONN),
    ('A packet’s destination is in no specific route. Where does it go?', 'Default route', 'Back to the sender at once',
     'Every interface at the same time', 'Unknown destinations follow the default route upstream, if one exists.', PREFIX, CONN),
    ('In the airport story, the flight plan is what?', 'The routing table', 'The passenger’s ticket stub', 'The terminal’s shops',
     'The flight plan lists where each destination goes, like the routing table.', PREFIX, m('RECALL')),
    ('In the chart, two routes match. Which wins?', 'The longest prefix', 'The route learned first', 'The broadest route there',
     'Routers prefer the most specific (longest-prefix) match.', PREFIX, ADW),
    ('A link goes down. Its connected route…', 'Leaves the table', 'Stays in the table forever', 'Turns into the default route',
     'Connected routes are removed when their interface goes down.', CONN, CONN),
], ([
    'A router connects different networks.',
    'It keeps a routing table of known networks.',
    'It picks the most specific match.',
    'Anything unknown goes to the default route.',
    'If there is no default route, unknown traffic is dropped.',
    'A down interface takes its connected route with it.',
], 'Routers join networks; the default route carries everything not listed.'), (
    'An airport hub has a flight plan for known destinations. Passengers for a city not on the plan are sent to the big '
    'international hub that knows more. The routing table is the plan; the default route is the flight to the big hub.',
    [('Airport hub', 'router'), ('Flight plan', 'routing table'), ('Flight to the big hub', 'default route'),
     ('Cancelled runway', 'interface down, route removed')],
    'Airports rebook stranded passengers. A router with no default route just drops the packet and may send an ICMP message.'),
    ('flow', 'How a router decides', ['Packet arrives', 'Read destination IP', 'Longest match?', 'Else default route', 'Forward out']),
    'Follow the packet. The third box is the decision; the fourth is the fallback that sends traffic upstream.',
    'In the lab, run show ip route. Find the default route and write its next hop and interface.',
    order('Order the router steps.', ['Read destination IP', 'Look for the longest match', 'Fall back to the default route', 'Forward out'],
          'Specific first, default last.'), RTR)

_add('3.1', 'incident-application', T, [
    ('A branch reaches its LAN but nothing outside. First check?', 'The default route', 'Every PC’s DNS settings first',
     'The Wi-Fi channel plan', 'Local works and remote fails, so check the route out.', PREFIX, m('PARALLEL')),
    ('show ip route has no 0.0.0.0/0 line. Record it?', 'Yes, with time', 'No, just add one quickly', 'Only if someone asks',
     'The missing default route is the key evidence; record it with time.', m('NEG'), m('PARALLEL')),
    ('In the ferry story, the missing route is…', 'No ferry off the island', 'A late bus across the town', 'A shop that closed',
     'Without a ferry, nobody leaves the island, like no default route.', PREFIX, m('RECALL')),
    ('In the timeline, what proved the cause?', 'No default route', 'A user’s complaint at 08:00', 'Rebooting the router',
     'The missing default route proves why remote traffic fails.', CONN, m('PARALLEL')),
    ('Good status line?', 'Branch route out missing; fixing', 'The internet is broken for everyone', 'Fixed, not sure how',
     'Accurate, calm, scoped and with the next step.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking routing incident.',
    'At 08:00 a branch can print but not reach the head office.',
    'Ping to the local gateway works.',
    'Ping beyond the router fails.',
    'show ip route has no default route.',
    'You record it and ask for the route to be restored.',
    'You verify head office is reachable.',
], 'Local OK, remote failing: read the route table and record what is missing.'), (
    'People on a small island can visit every house but cannot reach the mainland if the ferry stops. Nobody blames the '
    'island’s roads. A branch with no default route is that island: the LAN works, the way out is missing.',
    [('Island roads', 'branch LAN'), ('Ferry', 'default route'), ('Ferry timetable', 'routing table'), ('Harbour master', 'router owner')],
    'A missing ferry is obvious. A missing route is invisible until you read the table.'),
    ('flow', 'Branch timeline', ['08:00 remote fails', '08:03 gateway ping OK', '08:05 no default route', '08:08 route restored',
                                 '08:10 head office OK'], 2),
    'The red box is the proof. The passed gateway ping before it narrows the fault to routing.',
    'Write a five-line timeline for a branch that reaches its LAN but not head office.',
    order('Order the steps.', ['Confirm local works', 'Ping beyond the router', 'Read the route table', 'Restore one route', 'Verify'],
          'Local, remote, table, fix, verify.'), RTR)

_add('3.1', 'standard-of-work', T, [
    ('The gateway ping worked. Note it?', 'Yes, it narrows it', 'No, it found nothing wrong', 'Only if it had failed',
     'A passed gateway ping rules out the LAN and points to routing.', m('NEG'), m('NEG')),
    ('Adding three static routes at once to “try” is…', 'An untracked change', 'A very quick way to fix it', 'Normal for routers',
     'Several routes at once hide which one mattered and can misroute traffic.', m('PARALLEL'), m('PARALLEL')),
    ('In the map story, one road change at a time means?', 'One route per test', 'Redraw the whole map today', 'No notes needed',
     'Change one route, test, record.', m('PARALLEL'), m('NEG')),
    ('In the chart, which belongs under “avoid”?', 'Many routes at once', 'Note the route table', 'Retest after one change',
     'Bulk route changes lose cause and effect.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'Added 0.0.0.0/0 via .1 08:08', 'Messed with the routes a bit', 'Done',
     'Route, next hop and time make a trusted line.', m('NEG'), m('CHECKLIST')),
], ([
    'Routing work has two habits.',
    'Write down passed tests, like a good gateway ping.',
    'That rules out the LAN.',
    'Change one route at a time.',
    'Never add three routes to “try”.',
    'A wrong route can send traffic into a black hole.',
], 'Note passed tests and change one route at a time.'), (
    'A council changing road signs changes one junction, watches traffic and writes what happened. Changing every sign '
    'overnight causes chaos and nobody knows which sign helped. Routes are the network’s road signs.',
    [('Road sign', 'route'), ('One junction', 'one route change'), ('Traffic report', 'retest'), ('Council minutes', 'ticket notes')],
    'Drivers can read a bad sign and ignore it. Packets cannot; they follow a bad route straight into a black hole.'),
    ('two', 'Routing standard of work', (('Do', ['Note gateway ping OK', 'Add one route', 'Retest the path']),
                                         ('Avoid', ['Skipping passed tests', 'Adding many routes', 'No time on notes']))),
    'Each row pairs a good habit with the mistake it prevents.',
    'Rewrite “messed with routes, works” as a standard line with prefix, next hop, time and retest.',
    reveal('Rewrite: “messed with routes, works”.', '08:08 added 0.0.0.0/0 via 10.1.1.1; head office ping OK 08:10.'), RTR)

_add('3.1', 'practice-standard-for-this-lesson', T, [
    ('First line on a routing checklist?', 'Ping the gateway', 'Reload the core router now', 'Change every route',
     'Prove the first hop before reading tables.', m('CHECKLIST'), m('PARALLEL')),
    ('Pass sign for “read route table”?', 'Default route present', 'The output is very long', 'Any route at all is fine',
     'Good means a default route (or the needed route) is in the table.', PREFIX, m('CHECKLIST')),
    ('In the sat-nav story, “arrived” is what?', 'The pass sign', 'The car’s fuel level gauge', 'The radio station',
     '“Arrived” tells you the step worked, like a pass sign.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows the route table step?', 'Traceroute out', 'Reboot all the PCs', 'Change the VLAN',
     'Traceroute shows where the path stops after the table looks right.', STARS, m('PARALLEL')),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every routing protocol', 'Read the router manual',
     'Explain routing plainly to a peer, then do the checks.', m('RECALL'), m('JARGON')),
], ([
    'Explain routing to a peer without notes.',
    'Then run the checks in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start with a gateway ping.',
    'Read the route table for a default route.',
    'Give each step a pass sign and a fail note.',
], 'A routing checklist proves the first hop, then the table, then the path.'), (
    'A sat-nav says “arrived” only when you reach the address. If you are stuck, it says “recalculating”. A routing '
    'checklist line also needs a clear “arrived” sign and a clear “stuck here” note.',
    [('Sat-nav route', 'checklist'), ('“Arrived”', 'pass sign'), ('“Recalculating”', 'fail note'), ('Map data', 'routing table')],
    'A sat-nav fixes its own route. A router does not; a missing route stays missing until someone adds it.'),
    ('flow', 'Routing checklist', ['Ping gateway', 'Read route table', 'Default route?', 'Traceroute out', 'Verify app']),
    'These boxes outline the checklist. Under each, add what “good” looks like and the note for failure.',
    'Write a five-line routing checklist with a pass sign and fail note per line.',
    order('Order the checklist.', ['Ping gateway', 'Read route table', 'Check default route', 'Traceroute', 'Verify app'],
          'Hop, table, path, app.'), RTR)

_add('3.1', 'network-operations-depth', T, [
    ('Routing works at which layer?', 'Network', 'Data link, like a switch', 'Physical, like a cable',
     'Routers forward packets by IP address at layer 3.', m('RECALL'), CONN),
    ('ARP works, remote ping fails. Which side?', 'Routing', 'Local switching and the MAC table', 'The cable',
     'Local delivery works; the remote path is the routing side.', PREFIX, m('RECALL')),
    ('In the hub story, the regional airport is?', 'The next hop', 'The passenger’s home', 'The luggage belt',
     'Unknown trips go to the next hop, like a regional hub.', PREFIX, m('RECALL')),
    ('In the chart, traceroute stars at one hop but later hops reply. Meaning?', 'Hop hides ICMP', 'Path is broken there',
     'DNS has failed', 'A silent hop with later replies is usually filtering, not a break.', STARS, STARS),
    ('Which comparison splits routing from policy?', 'Ping vs port test', 'Old vs new laptops', 'Morning vs evening',
     'If ping reaches but the port fails, policy is blocking; if ping fails, check routes.', m('RECALL'), THIN),
], ([
    'This depth note links layers to routing.',
    'Routers work at layer 3, the network layer.',
    'Subnet and mask say if a host is local or remote.',
    'Local uses ARP. Remote uses the gateway and routes.',
    'Firewalls and NAT can block a path that routes fine.',
    'Ask: is it a missing route or a rule?',
], 'Split local from remote, then routing from policy.'), (
    'A traveller flying to a small town goes to a hub, then a regional airport, then the town. Each stop only knows the '
    'next stop. A router is the same: it only knows the next hop. Passport control is policy, not the route.',
    [('Airport stop', 'router hop'), ('Next flight', 'next hop'), ('Passport control', 'firewall policy'), ('Boarding pass', 'packet header')],
    'Travellers can ask at each airport. Packets cannot ask; if a hop has no route, the trip simply ends.'),
    ('two', 'Route problem or policy problem?', (('Route problem', ['Ping fails beyond hop', 'Missing route', 'Fix: add route']),
                                                 ('Policy problem', ['Ping OK, port refused', 'Rule blocks', 'Fix: change rule']))),
    'Use the top row to pick a column; the rest of the column tells you the likely fix and owner.',
    'In the lab, compare the route table with a traceroute result. Label the layer and say route or policy.',
    sort('Sort each finding.', {'Routing': ['No default route', 'Traceroute stops'], 'Policy': ['Port refused, ping OK', 'ACL deny hit']},
         'Different fixes, different owners.'), RTR)

_add('3.1', 'beyond-the-quiz', T, [
    ('What does a default route need to work?', 'A reachable next hop', 'A DNS name for the router', 'A faster interface',
     'The next hop must be reachable on a connected network.', CONN, m('RECALL')),
    ('The upstream link drops. What breaks?', 'All remote traffic', 'Only one desk at the back', 'Nothing at all',
     'Everything using the default route loses its path.', m('RECALL'), CONN),
    ('In the bridge story, the only bridge is?', 'The default route', 'The town’s main square', 'The river bank',
     'Lose the only bridge and everyone outside is cut off.', PREFIX, m('RECALL')),
    ('In the chart, which test splits route from link?', 'Ping the next hop', 'Reboot every PC first', 'Ask the users',
     'If the next hop answers, the link is up and the route is the suspect.', CONN, m('PARALLEL')),
    ('When do you escalate a routing fault?', 'No router access', 'Never, keep trying alone', 'Before any test',
     'Escalate with evidence when you cannot change the router.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every routing fault.',
    'Know what a route needs: a reachable next hop.',
    'Know what breaks: all remote traffic.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Know when to hand over to the network team.',
], 'Dependencies, a deciding test, and timely escalation.'), (
    'A town with one bridge to the mainland depends on it for every trip out. If the bridge closes, the town still works '
    'inside but nothing leaves. The default route is that bridge; the next hop is the far bank.',
    [('Only bridge', 'default route'), ('Far bank', 'next hop'), ('Bridge closed', 'upstream link down'), ('Highways agency', 'network team')],
    'A town can build a second bridge in years. A router can learn a backup route in seconds if one is configured.'),
    ('two', 'Remote fails: three causes', (('Cause', ['No default route', 'Next hop down', 'Upstream filter']),
                                           ('Deciding test', ['show ip route', 'Ping next hop', 'Port test past hop']))),
    'Each cause has a test that proves it. Run them in order before escalating.',
    'Write your own routing scenario: symptom, three causes, deciding test, escalation note.',
    reveal('Next hop answers; default route present; traffic still fails. Next?', 'Check upstream filtering and the far-end route.'), RTR)

# ================================================================== 3.2 WAN Handoffs
m = mc('3.2')
T = 'WAN Handoffs'
_add('3.2', 'core-concepts', T, [
    ('Before an ISP ticket, what must you prove?', 'Your side is fine', 'The ISP is always at fault', 'The users are wrong',
     'Prove your edge first: link, router, counters.', DEMARC, THIN),
    ('What is the demarc?', 'Where ownership changes', 'The fastest router in the building', 'The office front door',
     'The demarcation point is where your responsibility ends and the provider’s begins.', DEMARC, DEMARC),
    ('In the city story, the city limits sign is?', 'The demarc', 'The mayor’s office', 'A traffic light',
     'At the city limits, a different authority owns the road.', DEMARC, DEMARC),
    ('In the chart, which belongs on “our side”?', 'Edge router', 'Provider’s core', 'Provider exchange',
     'The edge router is yours; the provider owns beyond the demarc.', DEMARC, DEMARC),
    ('What makes a strong provider ticket?', 'Times and counters', 'An angry tone and caps lock', 'Just “it’s down”',
     'Timestamps, counters and isolating tests get action.', THIN, THIN),
], ([
    'A WAN link joins your site to a provider.',
    'The demarc is where ownership changes.',
    'Prove your side before you open a ticket.',
    'Check the edge router and its counters.',
    'Bring times and test results.',
    'That evidence gets faster help.',
], 'Prove your side of the demarc and bring evidence.'), (
    'At a city boundary, the road changes owner. If a pothole is outside the city, the city council cannot fix it and the '
    'county must. You report it with the exact location and time. A WAN demarc is that boundary.',
    [('City limits sign', 'demarcation point'), ('City council', 'your team'), ('County roads team', 'the provider'),
     ('Exact location and time', 'timestamps and counters')],
    'Road signs are visible. A demarc may be a small box in a cupboard, so you need records showing where it is.'),
    ('two', 'Who owns what', (('Our side', ['LAN switch', 'Edge router', 'Patch to demarc']),
                              ('Provider side', ['Demarc box onward', 'Provider router', 'Provider core']))),
    'Faults in the left column are yours to fix. Faults in the right column need a ticket with evidence.',
    'In the lab, check the edge interface status and counters. Write what proves your side is fine.',
    sort('Sort each part.', {'Ours': ['Edge router', 'LAN switch'], 'Provider': ['Provider core', 'Their router past the demarc']},
         'Ownership decides who acts.'), RTR)

_add('3.2', 'incident-application', T, [
    ('The site loses the WAN at 07:30. First check?', 'Edge interface', 'Everyone’s DNS cache first', 'Each user’s browser',
     'Check your edge interface status before blaming the provider.', DEMARC, m('PARALLEL')),
    ('Edge interface up, counters clean. Note it?', 'Yes, it is proof', 'No, it found nothing at all', 'Only at the end',
     'Clean counters prove your side and strengthen the ticket.', m('NEG'), THIN),
    ('In the parcel story, the depot receipt is?', 'Your evidence', 'The parcel’s wrapping', 'The van colour',
     'A receipt proves the parcel left your hands, like clean edge counters.', THIN, m('RECALL')),
    ('In the timeline, what proves it is past the demarc?', 'Next hop silent', 'A user complaint', 'A reboot',
     'Your edge is up but the provider’s next hop is silent: past the demarc.', DEMARC, THIN),
    ('Good status line?', 'Provider link down; ticket open', 'The internet is dead forever, sorry', 'No idea',
     'Clear, calm, with owner and next step.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking WAN incident.',
    'At 07:30 the site loses its WAN link.',
    'Your edge interface is up. Counters are clean.',
    'The provider’s next hop does not answer.',
    'You record times and counters.',
    'You open a provider ticket with that evidence.',
    'You update the site manager.',
], 'Prove your edge, then hand the provider exact evidence.'), (
    'When a parcel goes missing, the shop shows the depot receipt: handed over at 07:10, sealed, labelled. The courier '
    'cannot argue. Clean edge counters and a silent next hop are your depot receipt.',
    [('Depot receipt', 'edge counters and status'), ('Courier', 'WAN provider'), ('Tracking time', 'timestamps'),
     ('Complaint form', 'provider ticket')],
    'A courier can find the parcel. A provider may need you to test with them, so stay available.'),
    ('flow', 'WAN outage timeline', ['07:30 WAN down', '07:33 edge up', '07:35 counters clean', '07:37 next hop silent', '07:40 ticket'], 3),
    'The red box shows where your side ends. Everything before it is evidence for the ticket.',
    'Write a provider ticket for a WAN outage: times, your edge results and the failing test.',
    order('Order the steps.', ['Check edge status', 'Read counters', 'Ping next hop', 'Open provider ticket', 'Update site'],
          'Prove ours, then theirs.'), RTR)

_add('3.2', 'standard-of-work', T, [
    ('Edge counters were clean. Record it?', 'Yes, it is evidence', 'No, nothing was found there', 'Only if they ask',
     'Clean counters are what the provider needs to see.', m('NEG'), THIN),
    ('Rebooting the edge and changing its config together is…', 'Untracked change', 'A quick sensible first step', 'Required',
     'Two changes hide the cause and can extend the outage.', m('PARALLEL'), m('PARALLEL')),
    ('In the witness story, a calm statement is?', 'Clear evidence', 'A loud rumour in the street', 'A guess',
     'A witness gives times and facts, not guesses.', THIN, m('JARGON')),
    ('In the chart, which belongs under “avoid”?', 'Reboot and reconfigure', 'Note the counters first', 'Record times',
     'Doing both at once hides cause.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'Gi0/0 up, 0 CRC 07:35', 'Router seems fine to me', 'OK',
     'Interface, counter and time make a trusted line.', m('NEG'), m('CHECKLIST')),
], ([
    'WAN work has two habits.',
    'Write down passed checks, like clean counters.',
    'The provider will ask for them.',
    'Change one thing at a time.',
    'Do not reboot and reconfigure the edge together.',
    'You may lose the evidence you need.',
], 'Keep the edge evidence and make one change at a time.'), (
    'A witness to a car crash gives the time, the cars and what they saw. A witness who also moves the cars before the '
    'police arrive destroys the evidence. Rebooting the edge mid-incident can wipe the counters you needed.',
    [('Witness statement', 'ticket notes'), ('Moving the cars', 'rebooting the edge'), ('Police', 'provider support'),
     ('Skid marks', 'interface counters')],
    'Skid marks stay for days. Counters reset on reboot, so record them first.'),
    ('two', 'WAN standard of work', (('Do', ['Record counters first', 'One change only', 'Note every time']),
                                     ('Avoid', ['Rebooting before notes', 'Reboot plus config', 'Vague lines']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “router seems fine” as a standard line with interface, counters and time.',
    reveal('Rewrite: “router seems fine”.', 'Gi0/0 up/up, 0 input errors, 0 CRC at 07:35; next hop 203.0.113.1 no reply.'), RTR)

_add('3.2', 'practice-standard-for-this-lesson', T, [
    ('First line on a WAN checklist?', 'Edge link status', 'Call the provider straight away', 'Reboot all PCs',
     'Check your own edge first.', DEMARC, m('PARALLEL')),
    ('Pass sign for “counters”?', 'No rising errors', 'Lots of output text on screen', 'Any number',
     'Good means error counters are not increasing.', THIN, m('CHECKLIST')),
    ('In the checklist story, the fail note is?', 'What you write if it fails', 'The weather', 'The office address and postcode',
     'Every step needs a note for failure.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “ping next hop”?', 'Open ticket', 'Reimage the laptops', 'Change VLAN',
     'If the next hop is silent after your checks, open the ticket.', DEMARC, m('PARALLEL')),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every WAN acronym', 'Read the contract',
     'Explain the handoff plainly, then run the checks.', m('RECALL'), m('JARGON')),
], ([
    'Explain WAN handoffs to a peer without notes.',
    'Then run the checks in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start with your edge link.',
    'Check counters and the next hop.',
    'Each step has a pass sign and a fail note.',
], 'A WAN checklist proves your side before the provider ticket.'), (
    'Before a car goes to the garage under warranty, the owner checks the fuel, the lights and the tyres. If those pass, '
    'the warranty claim is strong. A WAN checklist is that pre-garage list.',
    [('Fuel and tyres', 'edge link and counters'), ('Warranty claim', 'provider ticket'), ('Garage', 'provider'),
     ('Service book', 'ticket notes')],
    'A car owner can see the tyres. You see counters, so you must know what normal looks like.'),
    ('flow', 'WAN checklist', ['Edge link up', 'Counters clean', 'Ping next hop', 'Open ticket', 'Verify restore']),
    'These boxes outline the checklist. Under each, write the pass sign and the fail note.',
    'Write a five-line WAN checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Edge link', 'Counters', 'Next hop', 'Provider ticket', 'Verify'],
          'Ours, then theirs, then verify.'), RTR)

_add('3.2', 'beyond-the-quiz', T, [
    ('What does the edge router need upstream?', 'The provider’s link', 'A local DNS server only', 'A bigger switch',
     'The provider’s circuit and next hop carry all off-site traffic.', DEMARC, m('RECALL')),
    ('The WAN drops. What breaks downstream?', 'All off-site traffic', 'Only the printer by reception', 'Nothing',
     'Everything leaving the site depends on the WAN.', m('RECALL'), DEMARC),
    ('In the pipeline story, the meter is?', 'The demarc', 'The kitchen tap', 'The bath',
     'The water meter marks where the utility’s pipe meets yours.', DEMARC, DEMARC),
    ('In the chart, which test splits ours from theirs?', 'Ping the next hop', 'Reboot all the PCs', 'Ask users',
     'Your edge up and next hop silent places the fault past the demarc.', DEMARC, m('PARALLEL')),
    ('Can a LAN trunk link two sites over the Internet?', 'No, use a VPN', 'Yes, trunks work anywhere', 'Only on Fridays',
     'Trunks are LAN features; sites connect with WAN or VPN.', LANWAN, LANWAN),
], ([
    'A quiz cannot cover every WAN fault.',
    'Know what the edge needs: the provider link.',
    'Know what breaks: all off-site traffic.',
    'Build a scenario with three causes.',
    'Pick the test that splits ours from theirs.',
    'Know when to escalate to the provider.',
], 'Map the handoff, design a deciding test, escalate with evidence.'), (
    'A house water meter marks where the utility’s pipe meets yours. A leak before the meter is theirs; after it, yours. '
    'You check your pipes first, then phone them with readings. The WAN demarc works the same way.',
    [('Water meter', 'demarc'), ('Your pipes', 'LAN and edge'), ('Utility main', 'provider network'), ('Meter readings', 'counters and times')],
    'Water leaks are visible. Packet loss is not, so readings and tests are your only proof.'),
    ('two', 'WAN down: three causes', (('Cause', ['Our edge port down', 'Provider circuit down', 'Routing past edge']),
                                       ('Deciding test', ['Edge status', 'Next hop ping', 'Traceroute past edge']))),
    'Each cause has a test. The middle row is where the provider ticket starts.',
    'Write your own WAN scenario: symptom, three causes, deciding test, and the ticket text.',
    reveal('Edge up, next hop silent, counters clean. Who acts?', 'The provider; open a ticket with times and counters.'), RTR)

# ================================================================== 3.3 Enterprise WLAN
m = mc('3.3')
T = 'Enterprise WLAN'
_add('3.3', 'core-concepts', T, [
    ('Users have full bars but slow Wi-Fi in a busy room. Likely?', 'Capacity limits', 'A broken cable on one PC', 'A DNS fault',
     'Many clients on shared airtime show as slowness and retries.', POWER, m('RECALL')),
    ('Which RSSI is stronger?', '−55 dBm', '−75 dBm', '−90 dBm',
     'A less negative number is a stronger signal.', RSSI, RSSI),
    ('In the radio story, crowded channels mean?', 'Retries', 'Faster speed for all', 'Better security',
     'Many talkers on one channel collide and retry.', CHOV, POWER),
    ('In the chart, which 2.4 GHz channels do not overlap?', '1, 6, 11', '1, 2, 3 and 4', '5, 6, 7',
     'In 2.4 GHz, 1, 6 and 11 are the usual non-overlapping set.', CHOV, CHOV),
    ('Staff need per-user Wi-Fi access. Which?', '802.1X', 'One shared password', 'A hidden SSID',
     'Enterprise auth (802.1X) gives each user their own login.', SHKEY, SHKEY),
], ([
    'Enterprise Wi-Fi has four parts to check.',
    'Authentication: who may join.',
    'SSID design: which networks exist.',
    'Channels: who shares airtime.',
    'Roaming: moving between APs.',
    'Too many users shows as slowness and retries.',
], 'Strong signal is not enough; capacity and channels decide speed.'), (
    'Picture a room of radio users on walkie-talkies. If everyone uses one channel, they talk over each other and repeat '
    'themselves. Spreading them over separate channels lets more people talk at once.',
    [('Walkie-talkie user', 'Wi-Fi client'), ('Channel', 'Wi-Fi channel'), ('Talking over each other', 'collisions and retries'),
     ('Radio licence', '802.1X login')],
    'People can wait politely. Wi-Fi clients retry blindly, which makes a busy channel even busier.'),
    ('two', 'Signal versus capacity', (('Signal problem', ['RSSI below −70 dBm', 'Far from AP', 'Fix: placement']),
                                       ('Capacity problem', ['Good RSSI, slow', 'Many clients', 'Fix: channels and APs']))),
    'Pick the column with RSSI. Good signal with poor speed points to the right-hand column.',
    'In the Wi-Fi survey lab, record SSID, band, channel and RSSI for each AP and mark overlaps.',
    sort('Sort the signs.', {'Signal': ['RSSI −82 dBm', 'Far corner'], 'Capacity': ['40 clients on one AP', 'Many retries, good RSSI']},
         'Different causes, different fixes.'), WIFI)

_add('3.3', 'incident-application', T, [
    ('Meeting room Wi-Fi slows at 10:00 daily. First data?', 'Clients per AP', 'Each laptop’s antivirus scan', 'DNS logs',
     'Count clients and channel use at the busy time.', POWER, m('PARALLEL')),
    ('RSSI is −52 dBm on a slow laptop. Record it?', 'Yes, rules out signal', 'No, signal is not useful here', 'Skip it',
     'Good signal rules out coverage and points to capacity.', m('NEG'), RSSI),
    ('In the café story, too many orders means?', 'A queue', 'Better coffee for all', 'A faster till',
     'A crowded counter queues orders like crowded airtime.', POWER, m('RECALL')),
    ('In the timeline, what proved capacity?', '45 clients, one AP', 'The user said it was slow', 'A reboot',
     'Many clients on one AP at busy time proves capacity.', POWER, m('PARALLEL')),
    ('Good status line?', 'Room AP overloaded; plan made', 'The Wi-Fi is broken everywhere now', 'Fixed',
     'Accurate, calm, with the plan.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking Wi-Fi incident.',
    'At 10:00 the meeting room Wi-Fi becomes slow.',
    'A laptop shows −52 dBm. Signal is fine.',
    '45 clients are on one AP.',
    'The neighbour AP uses the same channel.',
    'You record counts, channels and times.',
    'You escalate a capacity plan.',
], 'Good signal plus many clients means capacity; record numbers.'), (
    'A café with one till is fine at 8 customers and chaos at 40. The coffee is good, the till works, but the queue grows. '
    'A meeting-room AP serving 45 laptops is that till.',
    [('Till', 'access point'), ('Customers', 'clients'), ('Queue', 'airtime contention'), ('Second till', 'second AP on another channel')],
    'A café can ask people to wait. Wi-Fi clients keep retrying, which slows everyone further.'),
    ('flow', 'Meeting room timeline', ['10:00 slow reported', '10:03 RSSI −52', '10:05 45 clients', '10:07 same channel', '10:10 escalate plan'], 2),
    'The red box is the capacity proof. The strong RSSI before it rules out coverage.',
    'Write a timeline for a busy room with good signal and poor speed.',
    order('Order the steps.', ['Confirm busy-time slowness', 'Measure RSSI', 'Count clients', 'Check channels', 'Escalate plan'],
          'Signal, load, channel, plan.'), WIFI)

_add('3.3', 'standard-of-work', T, [
    ('RSSI was strong. Record it?', 'Yes, rules out coverage', 'No, it found nothing wrong at all', 'Only if bad',
     'A strong reading moves the focus to capacity.', m('NEG'), RSSI),
    ('Raising AP power and changing channels together is…', 'Untracked change', 'The fastest fix for slow rooms', 'Policy',
     'Two radio changes at once hide the cause and may add interference.', m('PARALLEL'), POWER),
    ('In the orchestra story, tuning one instrument at a time is?', 'One radio change', 'Tune all at once loudly', 'Skip notes',
     'One change, listen, note.', m('PARALLEL'), m('NEG')),
    ('In the chart, which belongs under “avoid”?', 'Max out AP power', 'Note RSSI', 'Count the clients per AP',
     'More power often adds interference.', POWER, m('NEG')),
    ('Which line meets the standard?', 'AP3 ch 6→11 10:20', 'Tweaked the Wi-Fi a little bit', 'OK',
     'AP, change and time.', m('NEG'), m('CHECKLIST')),
], ([
    'Wi-Fi work has two habits.',
    'Write down good readings, like strong RSSI.',
    'That rules out coverage.',
    'Make one radio change at a time.',
    'Do not raise power and change channels together.',
    'More power often makes things worse.',
], 'Note passed readings; change one radio setting at a time.'), (
    'An orchestra tunes one instrument at a time. If everyone retunes together, the hall is noise and nobody knows who is '
    'flat. Wi-Fi radios share the air the same way.',
    [('Instrument', 'AP radio'), ('Tuning one at a time', 'one channel or power change'), ('Hall noise', 'interference'),
     ('Conductor’s notes', 'ticket notes')],
    'Musicians hear each other. APs only partly coordinate, so you must measure after each change.'),
    ('two', 'Wi-Fi standard of work', (('Do', ['Note RSSI and clients', 'One channel change', 'Measure again']),
                                       ('Avoid', ['Skipping good readings', 'Power to max', 'Several radio changes']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “tweaked Wi-Fi” as a standard line with AP, change, time and new measurement.',
    reveal('Rewrite: “tweaked Wi-Fi”.', '10:20 AP3 channel 6→11; retries 18%→6% at 10:35.'), WIFI)

_add('3.3', 'practice-standard-for-this-lesson', T, [
    ('First line on a Wi-Fi checklist?', 'Record SSID and band', 'Turn security off to test speed', 'Reboot APs',
     'Start by recording what the client is connected to.', m('CHECKLIST'), SHKEY),
    ('Pass sign for “signal”?', 'RSSI above −67 dBm', 'Bars look full on the phone', 'Any value',
     'A typical data target is better than about −67 dBm.', RSSI, m('CHECKLIST')),
    ('In the doctor story, the normal range is?', 'The pass sign', 'The waiting room chairs', 'The clipboard',
     'A normal range is the pass sign for a reading.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “channel check”?', 'Clients per AP', 'Change the user’s password', 'DNS',
     'After channels, check load per AP.', POWER, m('PARALLEL')),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite all 802.11 versions', 'Read a datasheet',
     'Explain Wi-Fi plainly, then survey a room.', m('RECALL'), m('JARGON')),
], ([
    'Explain enterprise Wi-Fi to a peer without notes.',
    'Then survey a room in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Record SSID, band, channel and RSSI.',
    'Count clients per AP.',
    'Each step gets a pass sign and a fail note.',
], 'A Wi-Fi checklist measures signal, channel and load with clear targets.'), (
    'A nurse’s check-up has normal ranges: pulse, temperature, blood pressure. A reading outside the range gets a note. '
    'Wi-Fi checks have ranges too: RSSI, channel overlap, clients per AP.',
    [('Pulse', 'RSSI'), ('Normal range', 'pass sign'), ('Note on the chart', 'fail note'), ('Patient file', 'ticket')],
    'Human ranges are stable. Wi-Fi targets depend on the use: voice needs stronger signal than email.'),
    ('flow', 'Wi-Fi checklist', ['SSID and band', 'RSSI', 'Channel overlap', 'Clients per AP', 'Retest speed']),
    'These boxes outline the checklist from left to right. Under each one, add a numeric target and the note you write when it fails.',
    'Write a five-line Wi-Fi checklist with a target and fail note per line.',
    order('Order the checklist.', ['SSID and band', 'RSSI', 'Channel overlap', 'Clients per AP', 'Retest'],
          'Identity, signal, channel, load, verify.'), WIFI)

_add('3.3', 'beyond-the-quiz', T, [
    ('What does 802.1X Wi-Fi need upstream?', 'A RADIUS server', 'A brighter screen on laptops', 'A printer',
     'Enterprise auth depends on RADIUS reaching the identity store.', SHKEY, m('RECALL')),
    ('RADIUS goes down. What breaks?', 'New Wi-Fi logins', 'Every wired desk in the building', 'Nothing',
     'Clients cannot authenticate to join the staff SSID.', m('RECALL'), SHKEY),
    ('In the gate story, the guard’s phone line is?', 'The RADIUS link', 'The paint on the gate posts', 'The car park',
     'The guard checks badges by phone, like an AP asking RADIUS.', SHKEY, m('RECALL')),
    ('In the chart, which test splits auth from radio?', 'Join the guest SSID', 'Reboot every laptop', 'Ask HR',
     'If guest works and staff fails, auth is the suspect.', SHKEY, m('PARALLEL')),
    ('When do you escalate a Wi-Fi fault?', 'Needs controller access', 'Never, just keep trying', 'Before tests',
     'Escalate with data when the fix needs the controller or RADIUS.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every Wi-Fi fault.',
    'Know what Wi-Fi needs: radio, channels and auth.',
    'Know what breaks if RADIUS fails: logins.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Know when to call the wireless team.',
], 'Radio, capacity and auth are separate; test to tell them apart.'), (
    'A security guard at a gate phones the office to check each badge. If the phone line fails, the gate still opens for '
    'nobody, though the road is fine. 802.1X Wi-Fi is that gate: radio fine, auth broken.',
    [('Gate', 'access point'), ('Guard’s phone', 'link to RADIUS'), ('Badge', 'user credentials'), ('Road', 'radio signal')],
    'A guard might wave a familiar face through. RADIUS never does; no answer means no access.'),
    ('two', 'Staff cannot join: three causes', (('Cause', ['Weak signal', 'RADIUS down', 'Wrong SSID chosen']),
                                                ('Deciding test', ['RSSI reading', 'Guest SSID works?', 'Check SSID name']))),
    'Each cause has one test. Run them before calling the wireless team.',
    'Write your own Wi-Fi scenario: symptom, three causes, deciding test and escalation note.',
    reveal('Guest SSID works; staff SSID rejects everyone. Suspect?', 'RADIUS or the 802.1X policy, not the radio.'), WIFI)

# ================================================================== 3.4 Capstone — Wireless Capacity
m = mc('3.4')
T = 'Capstone — Wireless Capacity'
_add('3.4', 'the-scenario', T, [
    ('Fine at 8 people, unusable at 40. Likely cause?', 'Capacity', 'A bad cable on one chair', 'DNS',
     'Same room, more people: capacity, not coverage.', POWER, m('RECALL')),
    ('First data to collect?', 'Client counts', 'The room’s paint colour', 'User names',
     'Counts per AP and band at busy time.', POWER, m('RECALL')),
    ('In the lift story, a full lift means?', 'Waiting', 'Faster rides for all', 'A broken lift',
     'A full lift makes people wait, like full airtime.', POWER, POWER),
    ('In the chart, which band adds the most room?', '5 GHz', '2.4 GHz only', 'None',
     '5 GHz has many more non-overlapping channels.', CHOV, CHOV),
    ('What does “escalate with metrics” need?', 'Counts and retries', 'A strongly worded complaint', 'Nothing',
     'Numbers make the capacity case.', THIN, m('ESCALATE')),
], ([
    'A conference room has Wi-Fi.',
    'It works for 8 people.',
    'It is unusable for 40.',
    'Signal did not change. Load did.',
    'Collect client counts and bands.',
    'Escalate with metrics.',
    'Do not change settings during the meeting.',
], 'Same room, more users: measure capacity before you change anything.'), (
    'A lift is quick with three people and slow at rush hour. The lift is not broken; it is full. The fix is more lifts '
    'or spreading people out, not a faster motor.',
    [('Lift', 'access point'), ('Rush hour', '40 users'), ('More lifts', 'more APs or channels'), ('Faster motor', 'more transmit power')],
    'A lift has a fixed size. Wi-Fi capacity also depends on each client’s speed, so one slow client can slow the rest.'),
    ('flow', 'Capacity scenario', ['8 users OK', '40 users slow', 'Count clients', 'Check bands', 'Escalate metrics']),
    'Read left to right. The scenario is only solved when the last box has real numbers.',
    'In the Wi-Fi survey lab, count clients and record each band for the room’s APs.',
    order('Order the work.', ['Confirm load trigger', 'Count clients', 'Record bands', 'Check channels', 'Escalate with numbers'],
          'Measure, then escalate.'), WIFI)

_add('3.4', 'your-turn-scaffolded-checklist', T, [
    ('What goes in “counts and bands recorded”?', 'Clients per band', 'The guest list', 'Room temperature',
     'Clients per AP and band at the busy time.', POWER, m('CHECKLIST')),
    ('What goes in “channel note”?', 'Channels and overlap', 'The user’s favourite channel', 'TV channel',
     'Which channels each AP uses and any overlap.', CHOV, CHOV),
    ('In the form story, a blank line means?', 'Unfinished', 'Optional for this one', 'Done',
     'Do not skip lines.', m('CHECKLIST'), m('CHECKLIST')),
    ('In the chart, the escalation line needs?', 'Numbers', 'Feelings about the room', 'Nothing',
     'Metrics make the escalation useful.', THIN, m('ESCALATE')),
    ('Which entry fills “counts and bands”?', '38 on 2.4, 4 on 5', 'Lots and lots of users today', 'Busy',
     'Real numbers by band.', POWER, m('NEG')),
], ([
    'Fill in each line on paper or in the ticket.',
    'Do not skip lines.',
    'Counts and bands recorded.',
    'Channel note.',
    'Escalation with metrics.',
    'Each line needs a real number, not a tick.',
    'Write the time you measured each one.',
], 'Three lines, all with numbers and times.'), (
    'A traffic survey records cars per lane at rush hour. “Busy” is useless to planners; “900 cars in lane 1, 40 in lane '
    '2” shows the fix. Your checklist needs numbers in the same way.',
    [('Lanes', 'bands'), ('Cars per lane', 'clients per band'), ('Planner', 'wireless team'), ('Survey sheet', 'checklist')],
    'Roads cannot steer cars between lanes. Wi-Fi can steer clients to 5 GHz with band steering.'),
    ('two', 'Checklist filled in', (('Line', ['Counts and bands', 'Channel note', 'Escalation metrics']),
                                    ('Example', ['38 on 2.4, 4 on 5', 'Two APs on ch 6', 'Retries 22% at 10:05']))),
    'The right column shows good entries with numbers.',
    'Fill the three lines with real values from your lab survey.',
    reveal('Fill “channel note” for two APs both on 6.', 'AP1 ch 6, AP2 ch 6 — overlap; propose AP2 ch 11.'), WIFI)

_add('3.4', 'common-beginner-mistakes', T, [
    ('Why not turn off security “to make it faster”?', 'It exposes the network', 'It is too fast for older laptops', 'It is policy',
     'Removing security risks data and barely helps capacity.', SHKEY, POWER),
    ('What helps capacity more?', 'More channels or APs', 'Turning security off for now', 'A new SSID name',
     'Spread clients over more airtime.', POWER, SHKEY),
    ('In the bank story, removing the door lock is?', 'Disabling security', 'Hiring more tellers', 'Longer hours',
     'Speed is not worth an open vault.', SHKEY, POWER),
    ('In the chart, the fix for the mistake is?', 'Add capacity', 'Remove security', 'Reboot',
     'Capacity problems need capacity fixes.', POWER, SHKEY),
    ('Which entry avoids the mistake?', 'Added AP on ch 11', 'Disabled WPA3 for speed', 'Open SSID',
     'It adds capacity and keeps security.', SHKEY, SHKEY),
], ([
    'One mistake is very common here.',
    'Turning off security “to make it faster”.',
    'It exposes the network.',
    'It does not fix a crowded channel.',
    'Add capacity instead: channels, APs, 5 GHz.',
], 'Keep security on, and fix a capacity problem with more capacity.'), (
    'A bank with long queues does not remove the vault lock to speed things up. It opens more tellers. Wi-Fi security '
    'is the vault lock; extra APs and channels are more tellers.',
    [('Vault lock', 'WPA2/WPA3 security'), ('Long queue', 'crowded airtime'), ('More tellers', 'more APs or channels'),
     ('Robbery risk', 'data exposure')],
    'A bank lock adds no queue time. Wi-Fi encryption adds almost none either, so removing it gains nothing.'),
    ('two', 'Mistake and fix', (('Mistake', ['Turn security off', 'Raise power to max']), ('Fix', ['Add APs or channels', 'Move clients to 5 GHz']))),
    'Each row is a tempting shortcut and the real fix.',
    'Rewrite “turned off security, faster now” as a proper capacity action.',
    sort('Sort each action.', {'Mistake': ['Disable security', 'Max power'], 'Good': ['Add an AP', 'Use 5 GHz']},
         'Capacity, not shortcuts.'), WIFI)

_add('3.4', 'check-your-understanding', T, [
    ('First thing in your two-minute explanation?', 'The symptom', 'The final fix you chose', 'A joke',
     'Symptom, checks, cause, verification.', m('RECALL'), m('JARGON')),
    ('What proved capacity here?', 'Client counts', 'A user’s strong opinion', 'Reboot',
     'Counts per AP at busy time proved it.', POWER, m('PARALLEL')),
    ('In the sports story, the replay is?', 'Verification', 'The opening whistle', 'Kit',
     'Replay confirms what happened, like verifying the fix.', m('CHECKLIST'), m('RECALL')),
    ('In the chart, the last box is?', 'Re-measure at 40', 'Close the ticket at once', 'Blame',
     'Verify under the same load.', m('CHECKLIST'), m('NEG')),
    ('Cannot explain it? Next step?', 'Re-run the demo', 'Skip to the next lesson', 'Guess',
     'Re-run the steps first.', m('RECALL'), m('RECALL')),
], ([
    'Explain the ticket in two minutes.',
    'Symptom: room slow at 40 people.',
    'Checks: RSSI, counts, channels.',
    'Cause: too many clients on one channel.',
    'Verification: re-measure with 40 people.',
    'If you cannot, re-run the demo.',
], 'Verify under the same load that caused the problem.'), (
    'A coach explains a match: what happened, three key moments, why it went that way, and the replay that confirms it. '
    'Your Wi-Fi explanation has the same four beats.',
    [('What happened', 'symptom'), ('Key moments', 'RSSI, counts, channels'), ('Why', 'capacity cause'), ('Replay', 're-measure at 40')],
    'A replay is exact. A busy room varies, so you verify at a similar time and load.'),
    ('flow', 'Two-minute explanation', ['Symptom', 'Three checks', 'Cause', 'Verify at load']),
    'Four boxes, four beats. Testing with 8 people would not verify a 40-person problem, so the last box needs real load.',
    'Explain your capacity ticket to a peer in two minutes using the four boxes.',
    order('Order the explanation.', ['Symptom', 'Three checks', 'Cause', 'Verify at load'], 'Story order.'), WIFI)
