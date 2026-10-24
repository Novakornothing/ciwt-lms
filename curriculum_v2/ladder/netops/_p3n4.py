"""Option B pass 3 — NETOPS chapter 4 bespoke ladders (DHCP, DNS, NAT and firewall, internet-down capstone). Pending SME review."""
from curriculum_v2.ladder.netops._p3 import N, mc, src
from curriculum_v2.ladder.schema import order, reveal, sort

SECS = {}
SCOPE, LEASE, MISSO, RANDS, FLUSH, RESP, PORTP, RULE, TTLK = (
    'MC-L-NO4-SCOPE-SETTINGS', 'MC-L-NO4-LEASE-RENEW', 'MC-L-NO4-MISSING-OPTION', 'MC-L-NO4-RANDOM-STATIC',
    'MC-L-NO4-FLUSH-RESOLVER', 'MC-L-NO4-RESOLUTION-PATH', 'MC-L-NO4-PORT-IS-PROOF', 'MC-L-NO4-RULE-ORDER', 'MC-L-NO4-TTL-KINDS')
DORA, RELAY, NXD, TTLC, REC, NATT, SPEC, DHCPF = (
    'MC-NO4-DORA-ORDER', 'MC-NO4-NO-RELAY', 'MC-NO4-NXDOMAIN-AS-OUTAGE', 'MC-NO4-TTL-CACHE', 'MC-NO4-RECORD-TYPES',
    'MC-NO4-NAT-TYPES', 'MC-NO4-SPECIFIC-WINS', 'MC-C-NO4-DHCP-FAULT')
DH = ('win-dhcp-renew', 'Release and renew the lease, then read the server, lease time, gateway and DNS it handed out.')
NS = ('win-nslookup-ok', 'Resolve a name with nslookup and note which server answered and what it returned.')
NAT = ('linux-vm-nat', 'Read the NAT and firewall rules in order and say which rule matches a test connection.')
IPC = ('win-ipconfig', 'Run ipconfig /all and record address, gateway and DNS before any other test.')


def _add(label, sid, title, *a):
    SECS[(label, sid)] = N(label, sid, src(label, title), *a)


# ================================================================== 4.1 DHCP Deep Dive
m = mc('4.1')
T = 'DHCP Deep Dive'
_add('4.1', 'core-concepts', T, [
    ('New devices on one floor get 169.254 while old ones work. Likely?', 'Scope exhausted', 'Every new laptop is faulty',
     'The DNS server crashed', 'Old leases still work but no free addresses remain for new clients.', DHCPF, MISSO),
    ('What is in a DHCP lease besides the address?', 'Options like gateway', 'The user’s password and files', 'A website list',
     'Leases carry options such as gateway (3) and DNS servers (6).', MISSO, RANDS),
    ('In the badge-desk story, the badge expiry is?', 'Lease time', 'The visitor’s first name', 'The lobby door',
     'Badges expire like leases and must be renewed.', LEASE, SCOPE),
    ('In the chart, what is the DORA order?', 'Discover, Offer, Request, Ack', 'Offer, Discover, Ack, Request', 'Request first',
     'Discover, Offer, Request, Acknowledge.', DORA, DORA),
    ('Clients on another subnet need DHCP. What is needed?', 'A relay', 'A longer lease time for all', 'A static IP',
     'Broadcast Discovers need a relay (ip helper) to cross subnets.', RELAY, RELAY),
], ([
    'DHCP hands out addresses for a set time.',
    'That time is the lease.',
    'A lease also carries options like gateway and DNS.',
    'If the pool runs out, new clients get nothing.',
    'Clients on other subnets need a relay.',
    'Scope and relay faults hit many users at once.',
], 'DHCP faults are usually shared: many users, one scope or relay.'), (
    'A visitor desk gives out timed badges from a box. Each badge opens certain doors and expires at 5 pm. When the box is '
    'empty, new visitors wait, while people already inside are fine. That is a DHCP scope running out.',
    [('Badge desk', 'DHCP server'), ('Badge box', 'address pool (scope)'), ('Expiry time', 'lease time'),
     ('Doors the badge opens', 'options: gateway and DNS')],
    'Badge desks can print more badges. A scope is fixed by its range, so the fix is a bigger range or shorter leases.'),
    ('flow', 'DHCP DORA', ['Discover (broadcast)', 'Offer', 'Request', 'Acknowledge', 'Lease in use']),
    'Follow the four messages. If Discover cannot reach the server, nothing else happens, which is why relays matter.',
    'In the lab, release and renew. Record the DHCP server, lease time, gateway and DNS the client received.',
    order('Order DORA.', ['Discover', 'Offer', 'Request', 'Acknowledge'], 'Client asks, server offers, client requests, server confirms.'), DH)

_add('4.1', 'incident-application', T, [
    ('At 09:00 new laptops on floor 3 get 169.254. First check?', 'Scope usage', 'Each laptop’s network driver version',
     'DNS records', 'Many new clients failing points to the shared scope.', DHCPF, m('PARALLEL')),
    ('Scope shows 254 of 254 used. Record it?', 'Yes, it is proof', 'No, just extend the scope now', 'Only later on',
     'The full scope is the key evidence; record it with time.', m('NEG'), m('PARALLEL')),
    ('In the car-park story, a full car park means?', 'No new spaces', 'Faster parking for everyone', 'Free parking',
     'Cars already in are fine; new ones cannot enter.', DHCPF, SCOPE),
    ('In the timeline, what proved the cause?', 'Scope 100% used', 'A user’s email at 09:01', 'A reboot',
     'A full pool explains new-client failures.', DHCPF, m('PARALLEL')),
    ('Good status line?', 'Floor 3 pool full; adding', 'The whole network has gone', 'Fixed somehow',
     'Calm, accurate, scoped, with next step.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking DHCP incident.',
    'At 09:00 new laptops on floor 3 get 169.254.',
    'Old desktops on the floor still work.',
    'The scope shows 254 of 254 addresses used.',
    'Many leases belong to old guest devices.',
    'You record the numbers and propose a fix.',
    'You tell users new devices will connect soon.',
], 'New clients failing while old ones work: check the scope, record the numbers.'), (
    'A car park with 254 spaces is full by 9 am. Cars already inside are fine; new arrivals circle. Some spaces hold cars '
    'that left days ago but still show a ticket. A DHCP scope full of stale leases is that car park.',
    [('Car park', 'DHCP scope'), ('Parking ticket', 'lease'), ('Abandoned car', 'stale guest lease'), ('Attendant', 'DHCP admin')],
    'An attendant can tow abandoned cars. Stale leases expire on their own, but only after the lease time runs out.'),
    ('flow', 'Floor 3 timeline', ['09:00 169.254 on new', '09:03 old PCs fine', '09:05 scope 254/254', '09:08 shorter guest lease',
                                  '09:20 new PCs lease'], 2),
    'The red box is the proof. The old PCs working before it shows the fault is the pool, not the network.',
    'Write a timeline for a floor where new devices fail to lease while old ones work.',
    order('Order the steps.', ['Confirm new clients only', 'Check old clients', 'Read scope usage', 'Make one change', 'Verify new leases'],
          'Scope, prove, change, verify.'), DH)

_add('4.1', 'standard-of-work', T, [
    ('The relay was configured correctly. Record it?', 'Yes, rules it out', 'No, nothing was wrong with it', 'Only if asked',
     'A correct relay rules out the path and narrows to the scope.', m('NEG'), RELAY),
    ('Widening the scope and cutting lease time at once is…', 'Untracked change', 'The best quick fix for pools', 'Required',
     'Two changes at once hide which one fixed it.', m('PARALLEL'), SCOPE),
    ('In the bakery story, one recipe change means?', 'One change per test', 'Change all the ingredients', 'No notes',
     'Change one thing, then test.', m('PARALLEL'), m('NEG')),
    ('In the chart, which belongs under “avoid”?', 'Two scope edits', 'Note that the relay is OK', 'Retest lease',
     'Bulk scope edits hide cause.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'Guest lease 8d→1d 09:08', 'Fiddled with DHCP a bit', 'Done',
     'Setting, change and time.', m('NEG'), m('CHECKLIST')),
], ([
    'DHCP work has two habits.',
    'Write down passed checks, like a correct relay.',
    'That rules out the path.',
    'Make one scope change at a time.',
    'Do not widen the scope and cut leases together.',
    'You would not know which one helped.',
], 'Record passed checks and make one scope change at a time.'), (
    'A baker fixing flat bread changes only the yeast first and notes the result. Changing yeast, flour and oven heat '
    'together might work, but next time she will not know why. DHCP scope changes need the same care.',
    [('Yeast', 'lease time'), ('Flour', 'scope range'), ('Oven heat', 'relay or server'), ('Recipe notes', 'ticket notes')],
    'Bread fails in an hour. A lease change shows its effect only as old leases expire.'),
    ('two', 'DHCP standard of work', (('Do', ['Note relay OK', 'One scope edit', 'Retest a new client']),
                                      ('Avoid', ['Skipping passed checks', 'Two scope edits', 'No time on notes']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “fiddled with DHCP” as a standard line with setting, change, time and retest.',
    reveal('Rewrite: “fiddled with DHCP”.', '09:08 guest scope lease 8 days→1 day; new laptop leased 10.3.0.77 at 09:20.'), DH)

_add('4.1', 'practice-standard-for-this-lesson', T, [
    ('First line on a DHCP checklist?', 'Read ipconfig', 'Rebuild the DHCP server', 'Set static IPs',
     'Start with what the client actually has.', m('CHECKLIST'), RANDS),
    ('Pass sign for “renew”?', 'Lease with gateway, DNS', 'The command window closed cleanly', 'Any address',
     'Good means a lease with the expected options.', MISSO, m('CHECKLIST')),
    ('In the recipe story, the fail note is?', 'What to write if it fails', 'The brand of the oven used', 'Shopping list',
     'Every step needs a failure note.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “renew fails”?', 'Check scope', 'Type a random static IP', 'Reboot PC',
     'A failed renew sends you to the scope and relay.', DHCPF, RANDS),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite every DHCP option number', 'Read RFCs aloud',
     'Explain DHCP plainly, then run the checks.', m('RECALL'), m('JARGON')),
], ([
    'Explain DHCP to a peer without notes.',
    'Then run the checks in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start with ipconfig.',
    'Renew and read the lease options.',
    'Each step has a pass sign and a fail note.',
], 'A DHCP checklist checks the lease and its options, not just an address.'), (
    'A hotel check-in list says: key card works, Wi-Fi code given, breakfast time told. A guest with a key but no Wi-Fi '
    'code is half checked in. A lease with an address but no DNS is half a lease.',
    [('Key card', 'IP address'), ('Wi-Fi code', 'DNS option'), ('Breakfast time', 'lease time'), ('Check-in list', 'DHCP checklist')],
    'A guest can ask reception later. A client without a DNS option just fails names until it renews.'),
    ('flow', 'DHCP checklist', ['ipconfig /all', 'Renew lease', 'Gateway option', 'DNS option', 'Reach a site']),
    'These boxes outline the checklist. Under each, add a pass sign and a fail note.',
    'Write a five-line DHCP checklist with a pass sign and fail note per line.',
    order('Order the checklist.', ['ipconfig', 'Renew', 'Check gateway', 'Check DNS', 'Reach a site'], 'Lease, options, use.'), DH)

_add('4.1', 'beyond-the-quiz', T, [
    ('What does DHCP on another subnet need?', 'A relay', 'A bigger switch in the rack', 'A new DNS zone',
     'Broadcasts stop at the router unless a relay forwards them.', RELAY, m('RECALL')),
    ('The DHCP server dies. What breaks first?', 'New leases', 'Every current session instantly', 'Nothing ever',
     'Existing leases keep working until they expire; new clients fail.', LEASE, m('RECALL')),
    ('In the library story, the returns desk is?', 'Lease renewal', 'The building’s front door', 'The café',
     'Borrowers renew books before they are due, like lease renewal at 50%.', LEASE, LEASE),
    ('In the chart, which test splits scope from relay?', 'Same-subnet client', 'Reboot all the PCs', 'Ask users',
     'A client on the server’s subnet leasing fine points to the relay.', RELAY, m('PARALLEL')),
    ('A rogue DHCP server appears. Symptom?', 'Wrong gateway', 'No link light at all', 'Bad cables',
     'Clients get leases with the rogue’s gateway and DNS.', 'MC-R3-NO4-ROGUE-DHCP', MISSO),
], ([
    'A quiz cannot cover every DHCP fault.',
    'Know what DHCP needs: a server, a scope, maybe a relay.',
    'Know what breaks: new leases first.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Know when to call the server team.',
], 'Know the DHCP chain and test to find the broken link.'), (
    'A library lets you renew a book halfway through the loan. If the library closes for a week, people with books keep '
    'reading, but nobody new can borrow. A DHCP outage behaves exactly like that closed library.',
    [('Library', 'DHCP server'), ('Loan period', 'lease time'), ('Renewing halfway', 'renew at 50% of lease'),
     ('Branch van', 'DHCP relay')],
    'A library posts a closed sign. A DHCP server just stops answering; clients notice only when they need a lease.'),
    ('two', 'No lease: three causes', (('Cause', ['Scope full', 'Relay missing', 'Server down']),
                                       ('Deciding test', ['Scope usage', 'Same-subnet client OK?', 'Server reachable?']))),
    'Each cause has one test. Running all three takes a few minutes.',
    'Write your own DHCP scenario: symptom, three causes, deciding test, escalation note.',
    reveal('Clients get a gateway of 192.168.0.1 that nobody configured. Suspect?', 'A rogue DHCP server on the LAN.'), DH)

# ================================================================== 4.2 DNS Deep Dive
m = mc('4.2')
T = 'DNS Deep Dive'
_add('4.2', 'core-concepts', T, [
    ('Ping by IP works, by name fails. Which service?', 'DNS', 'The cable and the switch port', 'DHCP',
     'If the IP works and the name fails, look at name resolution.', 'MC-R4-NO4-DHCP-RESOLVES', NXD),
    ('A record changed but users still reach the old IP. Why?', 'Caching (TTL)', 'The mask is set wrong on PCs', 'DHCP',
     'Caches keep old answers until their TTL expires.', TTLC, TTLK),
    ('In the phone-book story, a wrong entry means?', 'Wrong destination', 'A dead telephone line', 'A long call',
     'A wrong entry sends you to the wrong place, like a bad DNS record.', REC, NXD),
    ('In the chart, which record maps a name to IPv4?', 'A', 'MX for mail', 'CNAME alias',
     'An A record maps a name to an IPv4 address.', REC, REC),
    ('Does ipconfig /flushdns clear the server cache?', 'No, only local', 'Yes, it clears every cache', 'Only on Fridays',
     'It clears the client resolver cache only.', FLUSH, FLUSH),
], ([
    'DNS turns names into addresses.',
    'If the IP works but the name fails, suspect DNS.',
    'Answers are cached for a time called TTL.',
    'Caching delays breakage and also delays fixes.',
    'Flushing your PC does not flush the server.',
    'Wrong records send users to wrong places.',
], 'IP works, name fails: DNS. Remember caches keep old answers.'), (
    'A phone book lists names and numbers. If an entry is wrong, you ring the wrong house. If you copied the number onto a '
    'sticky note, you keep ringing the old number even after the book is fixed. DNS caches are those sticky notes.',
    [('Phone book', 'DNS server'), ('Entry', 'DNS record'), ('Sticky note copy', 'cached answer'), ('How long you keep the note', 'TTL')],
    'You can throw away a sticky note. Server caches you do not control, so you wait for the TTL.'),
    ('two', 'Name problem or not?', (('DNS problem', ['IP works, name fails', 'NXDOMAIN or wrong IP', 'Check records and cache']),
                                     ('Not DNS', ['IP also fails', 'No route or link', 'Check lower layers']))),
    'Use the top row to choose a column. Only the left column is a DNS ticket.',
    'In the lab, run nslookup for a name. Write the server that answered and the address returned.',
    sort('Sort the signs.', {'DNS': ['Name fails, IP works', 'NXDOMAIN'], 'Not DNS': ['Ping by IP fails', 'No link light']},
         'Test the IP before blaming DNS.'), NS)

_add('4.2', 'incident-application', T, [
    ('After a server move, half the users reach the old IP. Why?', 'Cached records', 'Half the cables are broken now',
     'DHCP is full', 'Clients with cached answers keep the old IP until TTL expires.', TTLC, DHCPF),
    ('nslookup on the DNS server shows the new IP. Note it?', 'Yes, record it', 'No, it looks fine so skip it', 'Only later',
     'It proves the record is right; the problem is caching.', m('NEG'), TTLC),
    ('In the moving-house story, old address cards are?', 'Cached answers', 'The new house keys', 'The removal van',
     'Friends with old cards still visit the old house.', TTLC, REC),
    ('In the timeline, what proved caching?', 'Server new, PC old', 'A user’s guess about it', 'A reboot',
     'The server has the new IP while the PC still has the old one.', TTLC, m('PARALLEL')),
    ('Good status line?', 'Old address cached; clearing', 'Everything is broken today for all', 'Fixed?',
     'Accurate, calm, with what is happening.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking DNS incident.',
    'At 10:00 the app server moved to a new IP.',
    'Half the users still reach the old IP.',
    'nslookup on the DNS server shows the new IP.',
    'nslookup on a failing PC shows the old one.',
    'You note the TTL and flush affected clients.',
    'You tell users when it will clear.',
], 'Compare server and client answers; caching explains the split.'), (
    'After moving house, some friends still visit your old address because they kept your old card. The post office has '
    'your new address, but the cards last until people replace them. DNS caches work the same way.',
    [('Old address card', 'cached DNS answer'), ('Post office records', 'authoritative DNS'), ('Card replacement time', 'TTL'),
     ('Ringing friends', 'flushing client caches')],
    'You can phone friends. You cannot reach every cache, so you lower TTL before planned moves.'),
    ('flow', 'Server move timeline', ['10:00 move done', '10:05 half fail', '10:07 server: new IP', '10:08 PC: old IP', '10:10 flush clients'], 3),
    'The red box is the proof: server and client disagree. That is caching, not a broken record.',
    'Write a timeline for a server move where some users reach the old address.',
    order('Order the steps.', ['Confirm the split', 'Query the server', 'Query a failing PC', 'Flush one client', 'Verify'],
          'Compare, then act.'), NS)

_add('4.2', 'standard-of-work', T, [
    ('The record on the server is correct. Record it?', 'Yes, it rules it out', 'No, nothing was wrong with it', 'Skip it',
     'A correct record narrows the fault to caching.', m('NEG'), REC),
    ('Changing the record and the TTL and restarting DNS together is…', 'Untracked change', 'A very quick tidy fix for all',
     'Policy', 'Three changes hide the cause.', m('PARALLEL'), m('PARALLEL')),
    ('In the letter story, one correction at a time means?', 'One DNS change', 'Rewrite every letter now', 'No notes',
     'One change, retest, note.', m('PARALLEL'), m('NEG')),
    ('In the chart, which is “avoid”?', 'Restart DNS service', 'Note the record as it is now', 'Retest one PC',
     'Restarting DNS hits everyone.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'app A 10.0.5.20 OK 10:07', 'Fixed the DNS somehow earlier today', 'Done',
     'Record, value and time.', m('NEG'), m('CHECKLIST')),
], ([
    'DNS work has two habits.',
    'Write down checks that passed, like a correct record.',
    'That moves focus to caches.',
    'Make one DNS change at a time.',
    'Do not change record, TTL and service together.',
    'Restarting DNS affects everyone.',
], 'Note correct records and make single DNS changes.'), (
    'An editor correcting a printed directory fixes one entry, checks the proof, and notes it. Reprinting the whole book '
    'for one typo wastes time and risks new typos. DNS changes need the same single-step care.',
    [('Directory entry', 'DNS record'), ('Proof check', 'nslookup retest'), ('Reprinting the book', 'restarting the DNS service'),
     ('Editor’s log', 'ticket notes')],
    'A book is reprinted rarely. DNS changes take effect in seconds, so a mistake spreads fast.'),
    ('two', 'DNS standard of work', (('Do', ['Note record is correct', 'One change', 'Retest one client']),
                                     ('Avoid', ['Skipping passed checks', 'Restarting DNS', 'Several edits']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “fixed DNS somehow” as a standard line with record, value, time and retest.',
    reveal('Rewrite: “fixed DNS somehow”.', '10:07 app A record = 10.0.5.20 on server; flushed PC-14 10:10; app opens 10:11.'), NS)

_add('4.2', 'practice-standard-for-this-lesson', T, [
    ('First line on a DNS checklist?', 'Ping by IP', 'Restart the DNS server now', 'Flush every PC',
     'Prove the IP path before blaming names.', m('CHECKLIST'), m('PARALLEL')),
    ('Pass sign for “nslookup”?', 'Expected IP returned', 'The command printed text', 'Any answer',
     'Good means the right address from the expected server.', REC, m('CHECKLIST')),
    ('In the quiz story, the answer key is?', 'The pass sign', 'The exam room’s clock', 'The pen',
     'An answer key tells you what correct looks like.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “nslookup wrong IP”?', 'Check TTL', 'Reboot the router first', 'DHCP',
     'A wrong answer leads to records and cache TTL.', TTLC, DHCPF),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite all record types in order', 'Read RFCs',
     'Explain DNS plainly, then run checks.', m('RECALL'), m('JARGON')),
], ([
    'Explain DNS to a peer without notes.',
    'Then run the checks in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start by pinging the IP.',
    'Then run nslookup and compare answers.',
    'Each step has a pass sign and a fail note.',
], 'A DNS checklist proves IP first, then compares answers.'), (
    'A teacher marking a quiz uses an answer key. Without it, “looks right” is a guess. Your DNS checklist needs its own '
    'answer key: the address the name should return, and from which server.',
    [('Answer key', 'expected IP'), ('Marked paper', 'nslookup result'), ('Wrong answer note', 'fail note'), ('Teacher', 'technician')],
    'Answer keys are fixed. DNS answers change after moves, so update the key with each change.'),
    ('flow', 'DNS checklist', ['Ping by IP', 'nslookup name', 'Compare servers', 'Check TTL', 'Flush and retest']),
    'These boxes outline the checklist. Under each, add a pass sign and fail note.',
    'Write a five-line DNS checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Ping by IP', 'nslookup', 'Compare servers', 'Check TTL', 'Flush and retest'], 'IP, name, cache.'), NS)

_add('4.2', 'beyond-the-quiz', T, [
    ('What does a client need to resolve names?', 'A reachable DNS server', 'A static IP set by hand', 'A web browser',
     'The resolver must reach a DNS server, usually given by DHCP.', MISSO, m('RECALL')),
    ('Internal DNS fails. What breaks?', 'Name lookups', 'Every link light on the switch', 'Nothing',
     'Anything using names fails; IP-only traffic may still work.', m('RECALL'), NXD),
    ('In the directory story, a recursive lookup is?', 'Asking in steps', 'Guessing the number', 'Reading a map',
     'The resolver asks root, then TLD, then the authoritative server.', RESP, RESP),
    ('In the chart, NXDOMAIN means?', 'Name does not exist', 'The server is slow or down', 'Network down',
     'NXDOMAIN is a definite “no such name”, not an outage.', NXD, NXD),
    ('When do you escalate DNS?', 'Zone you cannot edit', 'Never, keep trying alone', 'Before tests',
     'Escalate with evidence to the zone owner.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every DNS fault.',
    'Know what DNS needs: a reachable server.',
    'Know what breaks: every name lookup.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Know who owns each zone.',
], 'Map the DNS chain, test to split causes, escalate to the zone owner.'), (
    'Finding a number for a stranger, you ask the operator, who asks the city exchange, who asks the street office. Each '
    'step knows a little more. A recursive DNS lookup works through root, TLD and authoritative servers the same way.',
    [('Operator', 'local resolver'), ('City exchange', 'TLD server'), ('Street office', 'authoritative server'), ('“No such person”', 'NXDOMAIN')],
    'Operators remember callers. Resolvers remember answers only for the TTL.'),
    ('two', 'Name fails: three causes', (('Cause', ['Wrong record', 'Stale cache', 'Server unreachable']),
                                         ('Deciding test', ['Query authoritative', 'Compare client vs server', 'Ping DNS server']))),
    'Each cause has one test. Run them in order to find the broken link.',
    'Write your own DNS scenario: symptom, three causes, deciding test, escalation note.',
    reveal('nslookup returns NXDOMAIN for a new name. Outage?', 'No — the record does not exist yet; ask the zone owner.'), NS)

# ================================================================== 4.3 NAT and Firewall
m = mc('4.3')
T = 'NAT and Firewall'
_add('4.3', 'core-concepts', T, [
    ('An app stopped after a firewall change. First question?', 'What changed?', 'Which user is at fault here?', 'Is DNS up?',
     'Firewall denies look like app outages; start with the change.', RULE, m('JARGON')),
    ('What does NAT do at the edge?', 'Rewrites addresses', 'Encrypts all the traffic', 'Assigns leases',
     'NAT rewrites private addresses to public ones (and back).', NATT, SCOPE),
    ('In the mailroom story, rewriting the return address is?', 'NAT', 'Firewall policy', 'DNS',
     'The mailroom rewrites the address; security decides what passes.', NATT, RULE),
    ('In the chart, a firewall evaluates rules how?', 'Top down, first match', 'All rules, most permissive', 'Randomly',
     'Most firewalls stop at the first matching rule.', RULE, SPEC),
    ('A port number is open. Does that prove the service?', 'No', 'Yes, always', 'Only for TCP',
     'A port number is a convention; check what actually answers.', PORTP, PORTP),
], ([
    'NAT rewrites addresses at the edge.',
    'Firewalls decide which traffic may pass.',
    'Rules are read top down; the first match wins.',
    'A firewall deny can look like an app outage.',
    'Always ask what changed recently.',
], 'NAT changes addresses; firewalls change what is allowed. Ask what changed.'), (
    'A company mailroom rewrites every outgoing letter with the company’s address, and remembers who sent it so replies '
    'return. A security guard at the door checks a list of what may enter or leave. NAT is the mailroom; the firewall is the guard.',
    [('Mailroom rewrite', 'NAT'), ('Sender list', 'NAT translation table'), ('Security guard', 'firewall'), ('Guard’s list, read top down', 'rule order')],
    'A guard can use judgement. A firewall applies the first matching rule exactly, even if a later rule seems better.'),
    ('two', 'NAT versus firewall', (('NAT', ['Rewrites addresses', 'Private to public', 'Keeps a table']),
                                    ('Firewall', ['Allows or denies', 'Rules top down', 'First match wins']))),
    'Each row compares the two jobs. A fault in the left column changes addresses; in the right, it changes what passes.',
    'In the NAT lab, read the rules in order and say which rule matches a test connection.',
    sort('Sort each job.', {'NAT': ['Rewrite source IP', 'Port translation'], 'Firewall': ['Deny a port', 'First-match rule']},
         'Different jobs, different fixes.'), NAT)

_add('4.3', 'incident-application', T, [
    ('Monday, the web app fails after a weekend rule change. First?', 'Review the change', 'Reboot every server in the room',
     'Flush DNS', 'Correlate the outage with the change before anything else.', RULE, m('PARALLEL')),
    ('Ping to the server works. Record it?', 'Yes, it is evidence', 'No, ping proves the app works', 'Skip',
     'It proves reachability and points to policy.', m('NEG'), PORTP),
    ('In the door story, a new “staff only” sign is?', 'A new deny rule', 'A broken door hinge', 'A lost key',
     'The door works; a new rule keeps people out.', RULE, m('RECALL')),
    ('In the timeline, what proved the cause?', 'Deny rule hit count', 'A user complaint at 08:05', 'A reboot',
     'Hit counts on the new deny rule show it is blocking traffic.', RULE, m('PARALLEL')),
    ('Good status line?', 'Rule change blocking app; rollback', 'Hackers attacked all of us overnight', 'No idea',
     'Clear, calm, with the action.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking firewall incident.',
    'On Monday at 08:00 the web app fails.',
    'A firewall change was made on Saturday.',
    'Ping to the server works.',
    'The port test fails.',
    'A new deny rule shows hits.',
    'You request a rollback with the evidence.',
], 'Reachable but refused after a change: check the new rule first.'), (
    'An office door works fine, but over the weekend someone put up a “staff only” sign and locked visitors out. Visitors '
    'think the office is closed. A new firewall deny rule makes an app look “down” the same way.',
    [('Door', 'network path'), ('“Staff only” sign', 'new deny rule'), ('Visitors', 'app users'), ('Facilities ticket', 'change record')],
    'A sign is visible. A rule is not, so you check hit counts and the change log.'),
    ('flow', 'Monday timeline', ['08:00 app fails', '08:03 ping OK', '08:05 port fails', '08:07 deny rule hits', '08:10 rollback'], 3),
    'The red box is the proof. Ping working earlier narrowed the fault to policy.',
    'Write a timeline for an app outage after a weekend firewall change.',
    order('Order the steps.', ['Check recent changes', 'Ping the server', 'Test the port', 'Read rule hits', 'Rollback with approval'],
          'Change, reach, port, rule, act.'), NAT)

_add('4.3', 'standard-of-work', T, [
    ('The NAT table looked correct. Record it?', 'Yes, it rules it out', 'No, nothing was wrong in it', 'Only if bad',
     'A correct NAT entry narrows the fault to rules.', m('NEG'), NATT),
    ('Disabling the firewall “to test” is…', 'A risky change', 'A quick sensible first check', 'Normal',
     'Turning protection off is a big untracked change and a security risk.', m('PARALLEL'), m('PARALLEL')),
    ('In the lock story, changing one lock at a time is?', 'One rule change', 'Remove every lock now', 'No notes',
     'One rule, retest, note.', m('PARALLEL'), m('NEG')),
    ('In the chart, which is “avoid”?', 'Disable firewall', 'Note that NAT looks OK', 'Retest port',
     'Disabling protection hides the cause and adds risk.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'Rule 14 reverted 08:12', 'Played with firewall rules', 'OK',
     'Rule, action and time.', m('NEG'), m('CHECKLIST')),
], ([
    'Firewall work has two habits.',
    'Write down passed checks, like a correct NAT entry.',
    'Make one rule change at a time.',
    'Never disable the firewall “to test”.',
    'That opens the network to attack.',
    'It also hides which rule was wrong.',
], 'Note passed checks; change one rule; never switch protection off.'), (
    'A building manager with a stuck door does not remove every lock in the building to test. She checks one lock, changes '
    'it, and notes it. Turning off the firewall is removing every lock.',
    [('One lock', 'one rule'), ('Removing every lock', 'disabling the firewall'), ('Manager’s log', 'change record'), ('Stuck door', 'blocked app')],
    'An unlocked building may be safe for an hour. An unprotected network can be scanned within minutes.'),
    ('two', 'Firewall standard of work', (('Do', ['Note NAT is correct', 'Revert one rule', 'Retest the port']),
                                          ('Avoid', ['Skipping passed checks', 'Disabling the firewall', 'Many rule edits']))),
    'Each row pairs a habit with the mistake it prevents.',
    'Rewrite “played with firewall rules” as a standard line with rule, action, time and retest.',
    reveal('Rewrite: “played with firewall rules”.', '08:12 reverted rule 14 (deny TCP 443 to web01); app loads 08:13.'), NAT)

_add('4.3', 'practice-standard-for-this-lesson', T, [
    ('First line on a firewall checklist?', 'What changed?', 'Disable the firewall to test', 'Reboot',
     'Start with recent changes.', RULE, m('PARALLEL')),
    ('Pass sign for “port test”?', 'Port connects', 'Ping replies from host', 'Window opens',
     'Good means the actual port answers, not just ping.', PORTP, m('CHECKLIST')),
    ('In the ledger story, the fail note is?', 'What you write if it fails', 'The colour of the ink used', 'Page count',
     'Every step needs a failure note.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “port fails”?', 'Read rule hits', 'Turn off the firewall', 'Flush DNS',
     'Rule hits show which rule matched.', RULE, m('PARALLEL')),
    ('Mastery shows how?', 'Teach it, no notes', 'Recite all port numbers', 'Read the manual',
     'Explain NAT and firewalls plainly, then run checks.', m('RECALL'), m('JARGON')),
], ([
    'Explain NAT and firewalls without notes.',
    'Then run the checks in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start with recent changes.',
    'Test the real port, not just ping.',
    'Each step has a pass sign and a fail note.',
], 'A firewall checklist tests the port and reads the rule that matched.'), (
    'An accountant’s ledger shows every entry with a date and a balance check. If a check fails, she notes it before '
    'moving on. Your firewall checklist is the ledger: each test, its expected result and a failure note.',
    [('Ledger line', 'checklist step'), ('Balance check', 'pass sign'), ('Error note', 'fail note'), ('Audit', 'change review')],
    'Ledgers balance or not. Firewalls can partly allow traffic, so test the exact port and direction.'),
    ('flow', 'Firewall checklist', ['Recent changes', 'Ping host', 'Test the port', 'Read rule hits', 'Verify app']),
    'These boxes outline the checklist. Under each, add a pass sign and fail note.',
    'Write a five-line firewall checklist with pass signs and fail notes.',
    order('Order the checklist.', ['Recent changes', 'Ping host', 'Test the port', 'Rule hits', 'Verify'], 'Change, reach, port, rule.'), NAT)

_add('4.3', 'network-operations-depth', T, [
    ('Ping works, port refused. Policy or reachability?', 'Policy', 'Reachability, a missing route', 'Cabling',
     'The host answers; a rule blocks the port.', PORTP, m('RECALL')),
    ('Which changes what paths exist?', 'Firewalls and NAT', 'Monitor brightness settings', 'Keyboards',
     'Firewalls and NAT decide which paths are allowed and how addresses look.', NATT, RULE),
    ('In the border story, customs is?', 'Policy', 'The road surface', 'The map',
     'Customs decides what may pass, like firewall policy.', RULE, m('RECALL')),
    ('In the chart, which comparison helps most?', 'On-net vs off-net', 'Morning vs evening shift', 'PC vs Mac',
     'Comparing inside and outside the edge shows where NAT or rules step in.', NATT, m('RECALL')),
    ('Which layer does a port rule act on?', 'Transport', 'Physical, at the cable', 'Data link',
     'Port rules match transport-layer ports.', PORTP, PORTP),
], ([
    'This depth note links layers to NAT and firewalls.',
    'Firewalls and NAT change which paths exist.',
    'Port rules act at the transport layer.',
    'Compare on-net with off-net behaviour.',
    'Ask whether the failure is policy or reachability.',
], 'Inside versus outside, and policy versus reachability.'), (
    'At a national border, the road continues, but customs decides what passes and passports get stamped. NAT is the '
    'stamp; the firewall is customs. A car turned back at customs did not hit a broken road.',
    [('Road', 'route'), ('Customs', 'firewall policy'), ('Passport stamp', 'NAT translation'), ('Inside the country', 'on-net')],
    'Customs explains why it refuses. Firewalls usually drop silently.'),
    ('two', 'Inside or outside the edge?', (('On-net works', ['App OK inside', 'Fails from outside', 'Check NAT and rules']),
                                            ('On-net fails too', ['App fails inside', 'Server or app fault', 'Check host']))),
    'Pick the column by testing inside first.',
    'In the NAT lab, test a connection from inside and outside. Label the layer and say policy or reachability.',
    sort('Sort each finding.', {'Policy': ['Port refused, ping OK', 'Deny rule hits'], 'Reachability': ['No route', 'Host down']},
         'Different owners.'), NAT)

_add('4.3', 'beyond-the-quiz', T, [
    ('What does port forwarding need to work?', 'NAT and an allow rule', 'Only a DNS record for it', 'A bigger router',
     'Inbound access needs a NAT mapping and a firewall allow rule.', NATT, m('RECALL')),
    ('A deny rule is placed above an allow. What breaks?', 'The allowed traffic', 'Nothing, specific always wins', 'DNS',
     'First match wins, so the deny blocks it.', RULE, SPEC),
    ('In the queue story, first in line is?', 'First rule matched', 'The most important person', 'Last',
     'Rules are read top down like a queue.', RULE, SPEC),
    ('In the chart, which test splits NAT from rule?', 'Inside vs outside test', 'Reboot every server in the rack', 'Ask users',
     'Inside OK and outside failing points at NAT or edge rules.', NATT, m('PARALLEL')),
    ('When do you escalate a firewall fault?', 'Rule owned elsewhere', 'Never, just keep trying', 'Before tests',
     'Escalate with evidence to the rule owner.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every firewall fault.',
    'Know what inbound access needs: NAT plus a rule.',
    'Know what breaks when rule order is wrong.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Know who owns each rule.',
], 'Rule order matters; first match wins.'), (
    'A queue at a club door is checked in order. If the first rule says “no trainers”, it does not matter that a later '
    'rule says “VIPs welcome”. A firewall reads its rules top down in the same way.',
    [('Queue order', 'rule order'), ('“No trainers”', 'deny rule'), ('“VIPs welcome”', 'later allow rule'), ('Bouncer', 'firewall')],
    'A bouncer may bend rules. A firewall never does; the first match is final.'),
    ('two', 'Inbound fails: three causes', (('Cause', ['No NAT mapping', 'Deny above allow', 'Service down']),
                                            ('Deciding test', ['NAT table entry', 'Rule hit counts', 'Test from inside']))),
    'Each cause has one test. Run them to find the broken link.',
    'Write your own firewall scenario: symptom, three causes, deciding test, escalation note.',
    reveal('Allow rule exists but has zero hits; a deny above it has many. Fix?', 'Move the allow above the deny (with approval).'), NAT)

# ================================================================== 4.4 Capstone — Internet Down
m = mc('4.4')
T = 'Capstone — Internet Down'
_add('4.4', 'the-scenario', T, [
    ('Whole office down, phones on cellular fine. Scope?', 'Site edge', 'Every PC is broken at once', 'The internet',
     'Cellular works, so the internet is up; the site edge is the suspect.', m('ESCALATE'), DHCPF),
    ('First test?', 'Ping the gateway', 'Reboot every PC one by one', 'Call vendors',
     'Test the gateway before touching PCs.', m('PARALLEL'), m('RECALL')),
    ('In the street story, one dark house among lit ones is?', 'A local fault', 'A national blackout', 'Weather',
     'If others have power, the fault is local.', m('ESCALATE'), m('RECALL')),
    ('In the chart, how many tests before escalating?', 'Four', 'One quick one', 'None at all',
     'The checklist asks for four recorded tests.', m('CHECKLIST'), m('CHECKLIST')),
    ('Who do you engage?', 'The right team', 'Everyone at the same time', 'Nobody',
     'Evidence tells you which team owns the fault.', m('ESCALATE'), m('ESCALATE')),
], ([
    'The whole office says “internet is down”.',
    'Phones on cellular still work.',
    'So the internet itself is fine.',
    'The fault is at your site.',
    'Test the gateway, DNS and the WAN.',
    'Then engage the right team.',
], 'Cellular works: the problem is your site, so test the edge.'), (
    'When one street goes dark but the next street is lit, you call about your street, not the national grid. Cellular '
    'phones working are the lit street next door.',
    [('Dark street', 'office network'), ('Lit street', 'cellular network'), ('Street transformer', 'site edge'), ('Power company', 'the right team')],
    'A street outage is visible. A network outage needs tests to show which part is dark.'),
    ('flow', 'Internet down path', ['Scope: site', 'Ping gateway', 'Ping outside IP', 'Resolve a name', 'Engage team']),
    'These boxes are the four tests plus escalation. Each needs a recorded result.',
    'In the ipconfig lab, record address, gateway and DNS, then plan the four tests.',
    order('Order the work.', ['Scope the site', 'Ping gateway', 'Ping outside IP', 'Resolve a name', 'Engage team'], 'Scope, test, engage.'), IPC)

_add('4.4', 'your-turn-scaffolded-checklist', T, [
    ('“Scope site vs single PC” needs what?', 'Several desks tested', 'One user’s opinion only', 'Nothing',
     'Check more than one desk to set the scope.', m('ESCALATE'), m('CHECKLIST')),
    ('How many tests must be recorded?', 'Four', 'Just one quick one', 'Ten',
     'The checklist asks for four tests.', m('CHECKLIST'), m('CHECKLIST')),
    ('In the form story, a blank line means?', 'Unfinished', 'Optional for today', 'Done',
     'Do not skip lines.', m('CHECKLIST'), m('CHECKLIST')),
    ('In the chart, “right team engaged” needs?', 'Evidence', 'A loud complaint', 'Nothing',
     'Evidence picks the team.', m('ESCALATE'), m('JARGON')),
    ('Which entry fills “four tests”?', 'GW OK, 8.8.8.8 fail…', 'Did some tests earlier', 'OK',
     'Real tests with results.', m('NEG'), m('CHECKLIST')),
], ([
    'Fill in each line on paper or in the ticket.',
    'Do not skip lines.',
    'Scope: site or single PC.',
    'Four tests recorded.',
    'Right team engaged.',
    'Each line has real values and times.',
], 'Scope, four tests and the right team, each with a value and a time.'), (
    'An insurance claim form asks: what happened, four pieces of evidence, which department. Leave a box empty and it '
    'returns. Your internet-down checklist works the same way.',
    [('What happened', 'scope'), ('Four pieces of evidence', 'four tests'), ('Department', 'right team'), ('Returned form', 'reopened ticket')],
    'An insurer checks every box. A colleague may not, so you check your own.'),
    ('two', 'Checklist filled in', (('Line', ['Scope', 'Four tests', 'Team']),
                                    ('Example', ['All 30 desks, 08:02', 'GW ok, WAN fail, DNS n/a', 'ISP ticket 08:15']))),
    'The right column shows good entries with values.',
    'Fill the three lines with your own lab values and times.',
    reveal('Fill “four tests” for a dead WAN.', 'GW ping OK; 8.8.8.8 fail; edge Gi0/0 up; next hop silent.'), IPC)

_add('4.4', 'common-beginner-mistakes', T, [
    ('Why not reboot every PC first?', 'It skips the gateway', 'It is far too quick to be useful', 'It is policy',
     'The gateway test finds site faults in seconds.', m('PARALLEL'), m('RECALL')),
    ('Better first move?', 'Test the gateway', 'Reboot every PC in turn', 'Reimage',
     'Gateway first.', m('PARALLEL'), m('RECALL')),
    ('In the car story, washing every car for one flat tyre is?', 'Rebooting all PCs', 'Checking the tyre', 'Reading',
     'Big effort, wrong target.', m('PARALLEL'), m('RECALL')),
    ('In the chart, the fix for the mistake is?', 'Gateway test', 'More reboots', 'Wait',
     'Test the shared path first.', m('PARALLEL'), m('RECALL')),
    ('Which entry avoids the mistake?', 'GW ping 08:03 OK', 'Rebooted 30 PCs one at a time', 'Waited',
     'A test before changes.', m('PARALLEL'), m('NEG')),
], ([
    'One mistake is very common here.',
    'Rebooting every PC before testing the gateway.',
    'It takes an hour and proves nothing.',
    'One gateway ping takes seconds.',
    'Test the shared path first.',
], 'Test the gateway before you touch a single PC.'), (
    'If every car on a street has no fuel deliveries, you do not service each car. You check the petrol station. Rebooting '
    'every PC when the gateway is the problem is servicing every car.',
    [('Each car', 'each PC'), ('Petrol station', 'gateway and WAN'), ('Servicing every car', 'rebooting every PC'), ('Checking the station', 'gateway ping')],
    'Cars can be serviced in parallel by many mechanics. PC reboots still waste everyone’s time.'),
    ('two', 'Mistake and fix', (('Mistake', ['Reboot every PC', 'No tests recorded']), ('Fix', ['Ping the gateway', 'Record four tests']))),
    'Each row is a mistake and the habit that replaces it.',
    'Rewrite “rebooted all PCs, still down” as a better first step.',
    sort('Sort each action.', {'Mistake': ['Reboot all PCs', 'Guess the cause'], 'Good': ['Ping gateway', 'Ping outside IP']},
         'Shared path first.'), IPC)

_add('4.4', 'check-your-understanding', T, [
    ('First beat in the explanation?', 'Symptom', 'The fix you made', 'Blame',
     'Symptom first.', m('RECALL'), m('JARGON')),
    ('What proved the cause here?', 'Next hop silent', 'A user’s strong guess', 'Reboot',
     'Edge up, next hop silent: WAN.', m('NEG'), m('PARALLEL')),
    ('In the news story, the follow-up report is?', 'Verification', 'The headline only', 'Ads',
     'A follow-up confirms what happened.', m('CHECKLIST'), m('RECALL')),
    ('In the chart, the last box is?', 'Users online', 'Ticket closed at once', 'Blame',
     'Users confirm they are online.', m('CHECKLIST'), m('NEG')),
    ('Cannot explain it? Next?', 'Re-run the demo', 'Skip to the next one', 'Guess',
     'Re-run the steps.', m('RECALL'), m('RECALL')),
], ([
    'Explain the ticket in two minutes.',
    'Symptom: whole office offline, cellular fine.',
    'Checks: gateway, outside IP, edge status.',
    'Cause: provider next hop silent.',
    'Verification: users back online.',
    'If you cannot, re-run the demo.',
], 'Symptom, checks, cause, verification, in two minutes.'), (
    'A news reporter covers a story: what happened, three facts checked, the cause, and a follow-up confirming it. Your '
    'internet-down explanation has the same four parts.',
    [('What happened', 'symptom'), ('Three facts', 'gateway, outside IP, edge'), ('Cause', 'provider fault'), ('Follow-up', 'users online')],
    'News can be corrected later. A ticket explanation should be right the first time.'),
    ('flow', 'Two-minute explanation', ['Symptom', 'Three checks', 'Cause', 'Users online']),
    'Four boxes, four beats, read from left to right. If one box is blank when you practise, re-run that step of the demonstration before you try again.',
    'Explain your internet-down ticket to a peer in two minutes using the boxes.',
    order('Order the explanation.', ['Symptom', 'Three checks', 'Cause', 'Users online'], 'Story order.'), IPC)
