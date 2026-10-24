"""Explanation ladder — NETOPS chapter 4 (DHCP, DNS, NAT and Firewalls). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Facts follow the lesson and the primary sources named in each rung.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 4

L = 'Course lesson {} (the original section), re-explained'
DHCP = 'RFC 2131 (DHCP, DORA, T1/T2 timers); RFC 2132 (DHCP options 3, 6, 15); RFC 1542 (relay agents); RFC 3927 (IPv4 link-local)'
DNS = 'RFC 1034 and RFC 1035 (DNS concepts and record types); RFC 8499 (DNS terminology); RFC 2782 (SRV); RFC 2308 (negative caching)'
NAT = 'RFC 3022 (traditional NAT and NAPT); RFC 4787 (NAT behaviour); RFC 6598 (shared address space); NIST SP 800-41r1 (firewall policy)'
APP = ('SNIA Dictionary (NAS, SAN); RFC 2474 (DSCP); RFC 3246 (Expedited Forwarding); RFC 791 and RFC 8200 (TTL / hop limit); '
       'RFC 7336 (CDN interconnection); NIST SP 800-94 (IDS/IPS); CompTIA Network+ N10-009 objective 1.2')
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO4-SCOPE-SETTINGS': {
        'obj': 'NO-4.1', 'label': 'Mixing up DHCP exclusions, reservations and the pool range',
        'fix': 'Pool: what may be leased. Exclusion: inside the pool but never leased. Reservation: one MAC always gets one IP.',
        'terms': ['exclusion', 'reservation', 'pool', 'scope'], 'source': L.format('4.1') + '; RFC 2131', 'review': R},
    'MC-L-NO4-LEASE-RENEW': {
        'obj': 'NO-4.1', 'label': 'Thinking a client waits until its lease expires before trying to renew',
        'fix': 'Clients renew with their server at 50% of the lease (T1) and with any server at 87.5% (T2).',
        'terms': ['lease', 't1', 't2', 'renew'], 'source': L.format('4.1') + '; RFC 2131', 'review': R},
    'MC-L-NO4-MISSING-OPTION': {
        'obj': 'NO-4.1', 'label': 'Not matching a missing DHCP-supplied setting (address, gateway, DNS) to its symptom',
        'fix': 'No gateway (option 3): local only. No DNS (option 6): names fail, IPs work. No lease: APIPA and nothing works.',
        'terms': ['option 3', 'option 6', 'gateway', 'dns'], 'source': L.format('4.1') + '; RFC 2132', 'review': R},
    'MC-L-NO4-RANDOM-STATIC': {
        'obj': 'NO-4.1', 'label': 'Fixing an APIPA client by typing a guessed static address',
        'fix': 'Find why DHCP failed (link, VLAN, relay, scope); a guessed address may collide and hides the fault.',
        'terms': ['apipa', 'static', 'collision'], 'source': L.format('4.1') + '; RFC 3927', 'review': R},
    'MC-L-NO4-FLUSH-RESOLVER': {
        'obj': 'NO-4.2', 'label': 'Thinking ipconfig /flushdns clears the DNS server’s cache too',
        'fix': '/flushdns clears only the client’s cache; the recursive resolver keeps its copy until the record’s TTL ends.',
        'terms': ['flushdns', 'cache', 'resolver', 'ttl'], 'source': L.format('4.2') + '; RFC 1035', 'review': R},
    'MC-L-NO4-RESOLUTION-PATH': {
        'obj': 'NO-4.2', 'label': 'Getting the order of a recursive lookup wrong (asking the authoritative server first, or the root last)',
        'fix': 'Stub → recursive resolver → root → TLD → authoritative; the resolver caches the answer for the TTL.',
        'terms': ['resolver', 'root', 'tld', 'authoritative'], 'source': L.format('4.2') + '; RFC 1034', 'review': R},
    'MC-L-NO4-PORT-IS-PROOF': {
        'obj': 'NO-4.2', 'label': 'Treating a well-known port number as proof of which service is running or why it fails',
        'fix': 'A port is a hypothesis; test name, TCP reachability, TLS and authentication separately.',
        'terms': ['port', 'listening', 'filtered', 'tls'], 'source': L.format('4.2'), 'review': R},
    'MC-L-NO4-RULE-ORDER': {
        'obj': 'NO-4.3', 'label': 'Thinking a firewall evaluates every rule and applies the most permissive or most specific one',
        'fix': 'Rules are read top to bottom and the first match wins; unmatched traffic hits the implicit deny.',
        'terms': ['rule order', 'first match', 'implicit deny'], 'source': L.format('4.3') + '; NIST SP 800-41r1', 'review': R},
    'MC-L-NO4-APPLIANCE-ROLE': {
        'obj': 'NO-4.3', 'label': 'Mixing up IDS and IPS, NAS and SAN, or proxy, load balancer and CDN roles',
        'fix': 'IDS watches a copy and alerts; IPS is inline and blocks. NAS shares files; SAN presents blocks. LB spreads; CDN caches.',
        'terms': ['ids', 'ips', 'nas', 'san', 'load balancer', 'cdn', 'proxy'], 'source': L.format('4.3') + '; ' + APP, 'review': R},
    'MC-L-NO4-TTL-KINDS': {
        'obj': 'NO-4.3', 'label': 'Confusing the IP TTL (hop count) with a DNS TTL (cache time)',
        'fix': 'IP TTL drops by one per router and stops loops; a DNS TTL says how long a record may be cached.',
        'terms': ['ttl', 'hop limit', 'time exceeded'], 'source': L.format('4.3') + '; RFC 791', 'review': R},
}

DORA, RELAY, OPT, FAULT, ROGUE = 'MC-NO4-DORA-ORDER', 'MC-NO4-NO-RELAY', 'MC-NO4-OPTION-MIXUP', 'MC-C-NO4-DHCP-FAULT', 'MC-R3-NO4-ROGUE-DHCP'
SCOPE, LEASE, MISS, RSTAT = 'MC-L-NO4-SCOPE-SETTINGS', 'MC-L-NO4-LEASE-RENEW', 'MC-L-NO4-MISSING-OPTION', 'MC-L-NO4-RANDOM-STATIC'
NXO, TTLC, REC, FLUSH, PATH, PORTP = ('MC-NO4-NXDOMAIN-AS-OUTAGE', 'MC-NO4-TTL-CACHE', 'MC-NO4-RECORD-TYPES', 'MC-L-NO4-FLUSH-RESOLVER',
                                      'MC-L-NO4-RESOLUTION-PATH', 'MC-L-NO4-PORT-IS-PROOF')
NATT, DMZ, PATT, STATE, ORD, APPL, TTLK = ('MC-NO4-NAT-TYPES', 'MC-R3-NO4-DMZ', 'MC-R3-NO4-PAT-TRADEOFF', 'MC-R3-NO4-STATEFUL-NEW',
                                          'MC-L-NO4-RULE-ORDER', 'MC-L-NO4-APPLIANCE-ROLE', 'MC-L-NO4-TTL-KINDS')

_TXT = {
    'incident-application': ('Incident application', 'activity', 'A practice drill (write a ticket timeline and a status sentence); it applies the lesson rather than explaining a concept.'),
    'standard-of-work': ('Standard of work', 'reference', 'A two-line list of work-habit reminders (record negative results; no untracked parallel changes) repeated in every lesson.'),
    'practice-standard-for-this-lesson': ('Practice standard for this lesson', 'activity', 'A self-study instruction to build a 5–9 step checklist; it is an exercise, not an explanation.'),
    'network-operations-depth': ('Network operations depth', 'orientation', 'A course-wide signpost paragraph repeated in every lesson; each topic it names is laddered in its own lesson.'),
    'beyond-the-quiz': ('Beyond the quiz', 'activity', 'A study-skills prompt (write your own scenario, explain to a non-technical user); an exercise, not a concept.'),
}


def _filler(keys, summary):
    out = {'core-concepts': same_as('core-content', 'Core concepts', summary)}
    out.update({k: skip(*_TXT[k]) for k in keys})
    return out


_STD = ['incident-application', 'standard-of-work', 'practice-standard-for-this-lesson', 'beyond-the-quiz']

LESSONS = {
    '4.1': {
        'core-content': section(
            'Core content', 'NO-4.1',
            [check('A new VLAN’s clients all get 169.254 addresses, though the DHCP server has a scope for that VLAN. What is likely missing?',
                   'A DHCP relay on the VLAN gateway', ['A DNS server option in the scope settings',
                    'A reservation for every client MAC address'],
                   'Discover is a broadcast that routers do not forward, so without a relay on the gateway the server never '
                   'hears it. Missing DNS options or reservations would not stop leases.', mc=[RELAY, SCOPE])],
            plain('''<p>DHCP hands out addresses in four steps: <strong>DORA</strong>.</p>
<ol><li><strong>Discover</strong>: the PC shouts “any DHCP servers?” to everyone.</li>
<li><strong>Offer</strong>: a server offers an address.</li>
<li><strong>Request</strong>: the PC says “I’ll take that one”.</li>
<li><strong>Acknowledge</strong>: the server says “it’s yours” and the lease starts.</li></ol>
<p>Half way through the lease, the PC asks to keep it.</p>
<p>The server also gives the gateway (option 3) and DNS servers (option 6).</p>
<p>Routers do not pass on broadcasts. So a <strong>relay</strong> on the router passes DHCP requests to a server on another subnet.</p>''',
                  L.format('4.1') + '; ' + DHCP,
                  [check('Which DHCP option tells clients their DNS servers?', 'Option 6', ['Option 3', 'Option 15'],
                         'Option 6 lists DNS servers. Option 3 is the default gateway (router) and option 15 is the DNS domain name, '
                         'not the server addresses.', mc=[OPT, OPT])]),
            analogy('''<p>Think of arriving at a busy hotel without a booking.</p>
<p>You stand in the lobby and call out “is there a receptionist?”: <strong>Discover</strong>. A receptionist answers “room 214 is free”:
<strong>Offer</strong>. You say, loud enough for the other desks to hear, “I’ll take 214”: <strong>Request</strong>. She hands you the key card,
valid for three nights: <strong>Acknowledge</strong> and the lease. The welcome pack lists the exit (gateway) and the information desk (DNS).</p>
<p>If reception is in another building, your shout never reaches it. A porter in your lobby (the <strong>relay</strong>) walks your request
over and says which wing you are in. A fake receptionist handing out wrong keys and wrong directions is a <strong>rogue DHCP server</strong>.</p>''',
                    L.format('4.1') + ' (hotel-arrival analogy written for this rung); ' + DHCP,
                    [check('In the hotel story, guests get keys but the welcome pack sends them to the wrong exit. What is the network cause?',
                           'A rogue DHCP server handing out a wrong gateway', ['A missing relay on the VLAN gateway', 'An exhausted pool on the real DHCP server'],
                           'Getting an address with wrong gateway or DNS points to an unauthorised server; compare the DHCP server in '
                           'ipconfig /all and enable snooping. A missing relay or full pool gives no lease at all.', mc=[ROGUE, FAULT])]),
            visual(svg(560, 210, 'DHCP DORA sequence: client Discover broadcast, server Offer, client Request broadcast, server Acknowledge',
                       text(80, 20, 'Client (UDP 68)', 13, bold=True) + text(450, 20, 'Server (UDP 67)', 13, bold=True)
                       + '<line x1="80" y1="30" x2="80" y2="200" stroke="currentColor" stroke-width="2"/>'
                       + '<line x1="450" y1="30" x2="450" y2="200" stroke="currentColor" stroke-width="2"/>'
                       + arrow(80, 55, 450, 55, '1. Discover (broadcast)') + arrow(450, 95, 80, 95, '2. Offer: 10.20.40.57, options')
                       + arrow(80, 135, 450, 135, '3. Request (broadcast)') + arrow(450, 175, 80, 175, '4. Ack: lease starts'))
                   + '''<ol class="ladder-trace"><li>Discover from UDP 68 to UDP 67, as a broadcast. A relay on the gateway forwards it as unicast and adds the subnet.</li>
<li>The server picks a free address from the pool (not an exclusion) and sends an Offer with options 3, 6 and 15.</li>
<li>The client broadcasts its Request so any other servers know which offer it took.</li>
<li>The server sends Ack and the lease starts.</li>
<li>At 50% (T1) the client renews with that server; at 87.5% (T2) with any server.</li></ol>''',
                   L.format('4.1') + '; ' + DHCP,
                   [check('From the trace, when does a client first try to renew an 8-hour lease?', 'After about 4 hours',
                          ['After 8 hours, when it expires', 'After about 7 hours'],
                          'T1 is half the lease, so renewal starts around 4 hours. About 7 hours is T2 (87.5%), when it asks any '
                          'server, and waiting for expiry would drop the address.', mc=[LEASE, LEASE])]),
            tryit('<p>Sort each symptom by its DHCP failure pattern, then release and renew a lease in the lab.</p>', L.format('4.1') + '; ' + DHCP,
                  [check('A printer must always get 10.20.40.20 from DHCP. Which scope setting does that?', 'A reservation for its MAC',
                         ['An exclusion for 10.20.40.20', 'A shorter lease time'],
                         'A reservation ties one MAC to one address. An exclusion stops the server leasing that address to anyone, '
                         'including the printer, and lease time does not pin an address.', mc=[SCOPE, SCOPE])],
                  widget=sort('Which failure pattern?',
                              {'One client': ['APIPA on one PC; neighbours fine', 'Cable reseated, still no lease on that PC'],
                               'Whole VLAN': ['All new devices get APIPA; old leases still work', 'Problem began after a gateway change'],
                               'Rogue server': ['Clients get addresses with the wrong gateway', 'DHCP server in ipconfig is unknown']},
                              'Notice that existing leases keep working when the pool or relay breaks.'),
                  lab={'id': 'win-dhcp-renew', 'note': 'Release and renew, then read the lease times and DHCP server in ipconfig /all.'})),
        **_filler(_STD, 'A short summary (DORA, scopes and relays) of the core section.'),
        'client-addressing-in-the-real-world': section(
            'Client addressing in the real world', 'NO-4.1',
            [check('A PC reaches local file shares but nothing outside its subnet. Which DHCP-supplied setting do you check first?',
                   'Option 3, the default gateway', ['Option 6, the DNS server list', 'Option 15, the DNS domain name'],
                   'Local-only access means traffic cannot leave the subnet, which is the gateway’s job. Missing DNS servers '
                   'or domain name would break names, not off-subnet IP traffic.', mc=[MISS, OPT])],
            plain('''<p>DHCP is supposed to give every PC four things.</p>
<ul><li>An <strong>address</strong> and <strong>mask</strong>: who it is and what is local.</li>
<li>A <strong>gateway</strong> (option 3): the way out.</li>
<li><strong>DNS</strong> servers (option 6): how names become addresses.</li></ul>
<p>Each missing piece looks different to the user. No gateway: only local things work. No DNS: names fail. No address: nothing works.</p>
<p>A 169.254 address means no DHCP answer came back. Find out why. Do not just type an address in.</p>
<p>Read <code>ipconfig /all</code> and say your next test out loud first.</p>''',
                  L.format('4.1') + '; ' + DHCP,
                  [check('Which ipconfig /all line tells you the PC never got a DHCP answer?', 'An address in 169.254.0.0/16',
                         ['A DNS suffix of corp.local', 'A lease that expires tomorrow'],
                         'APIPA addresses are self-assigned when DHCP fails. A DNS suffix and a future lease expiry both show a '
                         'working lease.', mc=[FAULT, LEASE])]),
            analogy('''<p>Think of a new phone with a SIM card.</p>
<p>The phone number is the <strong>address</strong>. The area code tells it which numbers are local calls: the <strong>mask</strong>. To ring
abroad, it needs the international exchange: the <strong>gateway</strong>. The contacts app turns “Mum” into a number: <strong>DNS</strong>.</p>
<p>The network normally sets all four when the SIM registers, the way DHCP does. If registration fails, the phone shows “emergency calls
only”, a bit like a 169.254 address. Typing in someone else’s number would not fix it; you would just get their calls.</p>''',
                    L.format('4.1') + ' (phone analogy written for this rung); RFC 3927',
                    [check('In the phone story, calls to saved contacts fail but typing the full number works. Which setting is missing?',
                           'DNS servers (option 6)', ['The default gateway (option 3)', 'The IP address itself'],
                           'Numbers work but names do not, which is DNS. No gateway would stop calls abroad whether dialled by name '
                           'or number, and no address would stop everything.', mc=[MISS, MISS])]),
            visual('''<ol class="ladder-trace"><li>Run <code>ipconfig /all</code>.</li>
<li>169.254 address? DHCP did not answer: check link and VLAN, then the relay and scope. Stop here.</li>
<li>Real address: note the DHCP server. Is it the expected one? If not, suspect a rogue server.</li>
<li>Gateway listed? If blank, check the scope’s option 3.</li>
<li>DNS servers listed? If blank or wrong, check option 6.</li>
<li>Say the next test (ping gateway, nslookup a name) before you change anything.</li></ol>''',
                   L.format('4.1'),
                   [check('At step 3 the DHCP server shown is 192.168.0.1, a home router, not the company server. What do you suspect?',
                          'A rogue DHCP server on the VLAN', ['An exhausted pool on the real server', 'A missing relay on the gateway'],
                          'An unexpected server handing out leases is the rogue pattern; find its port and enable DHCP snooping. An '
                          'exhausted pool or missing relay gives APIPA, not a foreign lease.', mc=[ROGUE, RELAY])]),
            tryit('<p>Predict the user’s complaint from each ipconfig line, then check it in the lab.</p>', L.format('4.1'),
                  [check('A help-desk colleague fixes a 169.254 PC by typing 10.20.40.99. What is the risk?', 'It may collide with a leased address',
                         ['The PC will be faster than its neighbours', 'DHCP will then lease it a second address'],
                         'A guessed static address can duplicate one the server already leased and hides the real DHCP fault. It does '
                         'not speed anything up or add a second lease.', mc=[RSTAT, RSTAT])],
                  widget=reveal('ipconfig: 10.20.40.57/24, gateway 10.20.40.1, DNS blank. What does the user say?',
                                '“Websites by name don’t work, but IP addresses do.” DNS (option 6) is missing.'),
                  lab={'id': 'win-ipconfig', 'note': 'Read each DHCP-supplied setting in ipconfig /all and name the symptom if it were missing.'})),
    },
    '4.2': {
        'core-content': section(
            'Core content', 'NO-4.2',
            [check('A record was changed 10 minutes ago with a TTL of 3600. Why do some users still get the old address?',
                   'Caches may keep the old answer for up to an hour', ['The change failed and must be made again',
                    'DNS servers only update once a day at midnight'],
                   'Resolvers and clients may cache an answer until its TTL runs out, here one hour. The change can be correct; '
                   'there is no daily update schedule.', mc=[TTLC, TTLC])],
            plain('''<p>DNS turns names into addresses.</p>
<ul><li>Your PC asks its DNS server (the <strong>resolver</strong>).</li>
<li>If the resolver does not know, it asks a <strong>root</strong> server, then the <strong>.com</strong> servers, then the domain’s own server.</li>
<li>It keeps the answer for a time called the <strong>TTL</strong>.</li></ul>
<p>Record types: <strong>A</strong> (IPv4), <strong>AAAA</strong> (IPv6), <strong>CNAME</strong> (alias), <strong>MX</strong> (mail), <strong>PTR</strong> (IP to name), <strong>TXT</strong> (text, e.g. SPF).</p>
<p>Results: <strong>NXDOMAIN</strong> means the name does not exist. <strong>SERVFAIL</strong> means the resolver could not get an answer. A timeout means no reply at all.</p>''',
                  L.format('4.2') + '; ' + DNS,
                  [check('Which record type tells other mail servers where to deliver mail for a domain?', 'MX', ['PTR', 'CNAME'],
                         'MX records list a domain’s mail servers with preference values. PTR maps an address back to a name, and '
                         'CNAME makes one name an alias of another.', mc=[REC, REC])]),
            analogy('''<p>Think of asking a librarian for a book you only know by title.</p>
<p>You ask the front desk (your <strong>resolver</strong>). If it is not on the recent-requests shelf (the <strong>cache</strong>), the librarian
checks the master index (the <strong>root</strong>), which points to the right floor (<strong>TLD</strong>, like .com), whose catalogue points to
the exact shelf (the <strong>authoritative</strong> server). The librarian writes the answer on a sticky note valid for an hour (the
<strong>TTL</strong>). Moving the book does not update the sticky notes; they expire on their own.</p>
<p>“No such book exists” is <strong>NXDOMAIN</strong>. “The catalogue system is down” is <strong>SERVFAIL</strong>. The librarian not answering at all
is a <strong>timeout</strong>.</p>''',
                    L.format('4.2') + ' (library analogy written for this rung); ' + DNS,
                    [check('In the library story, the librarian says “no such book exists”. Which DNS result is that?', 'NXDOMAIN',
                           ['SERVFAIL', 'A timeout'],
                           'NXDOMAIN is an authoritative “this name does not exist”, so check spelling and suffix. SERVFAIL means '
                           'the resolver could not get a valid answer, and a timeout means no reply.', mc=[NXO, NXO])]),
            visual(svg(560, 140, 'DNS recursive lookup: client asks resolver, resolver asks root, then TLD, then authoritative server, then caches the answer',
                       box(5, 50, 85, 46, 'Client', 'stub') + box(120, 50, 95, 46, 'Resolver', 'cache') + box(250, 5, 95, 40, 'Root')
                       + box(250, 55, 95, 40, 'TLD .com') + box(250, 105, 95, 34, 'Authoritative') + arrow(90, 73, 120, 73, '1')
                       + arrow(215, 60, 250, 25) + arrow(215, 73, 250, 75) + arrow(215, 86, 250, 120)
                       + text(460, 60, 'answer cached for the TTL', 12) + text(460, 80, 'then returned to the client', 12))
                   + '''<ol class="ladder-trace"><li>The client checks its own cache and hosts file, then asks the resolver from DHCP option 6.</li>
<li>Resolver cache empty: it asks a root server, which refers it to the .com TLD servers.</li>
<li>The TLD servers refer it to the domain’s authoritative servers (its NS records).</li>
<li>The authoritative server answers, e.g. an A record.</li>
<li>The resolver caches it for the TTL and returns it. <code>ipconfig /flushdns</code> clears only step 1’s cache.</li></ol>''',
                   L.format('4.2') + '; ' + DNS,
                   [check('After a record change, you run ipconfig /flushdns but still get the old address. Why?',
                          'The resolver still caches it until the TTL ends', ['flushdns also needs a reboot to take effect',
                           'The authoritative server has not been asked yet'],
                          'flushdns clears only the client cache; the recursive resolver keeps its copy for the TTL. No reboot is '
                          'needed, and the resolver will not ask the authoritative server again until its cache expires.', mc=[FLUSH, PATH])]),
            tryit('<p>Use nslookup or Resolve-DnsName in the lab to look up different record types and read each result.</p>', L.format('4.2') + '; ' + DNS,
                  [check('nslookup returns NXDOMAIN for intranet.corp, but a colleague resolves it. What do you check first?',
                         'Which DNS server and suffix each of you uses', ['Whether the intranet web server is powered on',
                          'Whether the colleague’s browser is newer'],
                         'NXDOMAIN on one PC but not another points to a different resolver (internal vs public) or suffix, as with '
                         'split-horizon DNS. The web server and browser do not affect a lookup.', mc=[NXO, NXO])],
                  widget=sort('Which result?',
                              {'NXDOMAIN': ['Name misspelled', 'Missing DNS suffix for a short name'],
                               'SERVFAIL': ['DNSSEC validation failed upstream', 'Resolver cannot reach the authoritative servers'],
                               'Timed out': ['UDP/TCP 53 to the DNS server is blocked', 'DNS server is down']},
                              'Notice that only a timeout points to layers 3–4.'),
                  lab={'id': 'win-nslookup-ok', 'note': 'Look up A, MX and PTR records and read each answer and its server.'})),
        **_filler(_STD, 'A short summary (resolution path, caching and record types) of the core section.'),
        'ports-as-clues-not-magic-numbers': section(
            'Ports as clues, not magic numbers', 'NO-4.2',
            [check('A web app fails. The name resolves and TCP 443 connects. What does the lesson say to test next?',
                   'The certificate (TLS), then sign-in', ['DNS again, with a different resolver', 'The cable, starting with layer 1'],
                   'Name and TCP reachability are already proven, so the next layer is TLS and then the application’s authentication. '
                   'Re-testing DNS or cabling repeats proven steps.', mc=[PORTP, NXO])],
            plain('''<p>Port numbers give you a first guess. They do not prove anything.</p>
<ul><li>443 suggests HTTPS. 3389 suggests remote desktop. But the service may be <strong>stopped</strong>, <strong>blocked</strong>, or <strong>refusing the login</strong>.</li>
<li>For a web app, test in this order: the <strong>name</strong>, the <strong>TCP connection</strong>, the <strong>certificate</strong>, the <strong>login</strong>.</li>
<li>Ask: is it one PC, or everyone at the site?</li></ul>
<p>Write down the exact URL, where the user was (office, VPN or home), and whether the IP works when the name fails.</p>''',
                  L.format('4.2'),
                  [check('Which detail should the ticket record about the user’s location?', 'Office, VPN or home',
                         ['Their desk phone extension', 'The colour of their laptop'],
                         'Network location changes which DNS server, path and firewall rules apply, so it is key evidence. Phone '
                         'extensions and laptop colour do not affect the path.', mc=[PORTP, PORTP])]),
            analogy('''<p>Think of door numbers in a big office building.</p>
<p>Room 443 is “usually the web team”. That is a good guess about who you will find, but the door could be locked (filtered), the room empty
(service not listening), or the person inside may not let you in without a badge (authentication). Knocking on the right room number proves
none of that.</p>
<p>A detective uses the room number to decide where to look first, then checks each thing in turn: is the building address right (DNS), does
the door open (TCP), is it really the web team (certificate), will they serve you (login).</p>''',
                    L.format('4.2') + ' (office-door analogy written for this rung)',
                    [check('In the office-door story, the door opens but the person inside asks for a badge you do not have. Which layer failed?',
                           'Application authentication', ['TCP reachability to the port', 'DNS name resolution'],
                           'An open door is a completed TCP connection, and finding the building is DNS, so both passed. Being refused '
                           'without a badge is the application’s sign-in.', mc=[PORTP, NXO])]),
            visual('''<ol class="ladder-trace"><li><strong>Name</strong>: <code>Resolve-DnsName app.corp.example</code>. Fails? DNS.</li>
<li><strong>IP</strong>: does the resolved address answer from this network?</li>
<li><strong>TCP</strong>: <code>Test-NetConnection app.corp.example -Port 443</code>. False? Firewall or service.</li>
<li><strong>TLS</strong>: does the browser trust the certificate and name?</li>
<li><strong>Login</strong>: does the app accept the user?</li>
<li><strong>Scope</strong>: same result for a colleague, on VPN, at home?</li></ol>''',
                   L.format('4.2') + '; RFC 9293',
                   [check('Step 3 shows TcpTestSucceeded: True, but the browser shows a certificate name warning. Where is the fault?',
                          'TLS: the certificate does not match the name', ['TCP: the port is filtered by a firewall', 'DNS: the name resolves to the wrong place'],
                          'A successful TCP test means the port is reachable, and resolving the name was step 1. A name mismatch in '
                          'the certificate is a TLS problem.', mc=[PORTP, PORTP])]),
            tryit('<p>Put the web-app tests in order, from name to login.</p>', L.format('4.2'),
                  [check('Why is “port 3389 is open, so remote desktop works” a weak conclusion?', 'Open does not prove the login will work',
                         ['Port 3389 is not used by remote desktop', 'An open port means the firewall is broken'],
                         'An open port only proves something accepts TCP there; the service may still refuse sign-in or be a different '
                         'program. RDP does use 3389, and an open port can be intended.', mc=[PORTP, PORTP])],
                  widget=order('Order the web-app tests', ['Resolve the name', 'Test TCP to the port', 'Check the certificate', 'Sign in',
                                                           'Compare with a colleague or another network'],
                               'Each test is only meaningful once the one before it has passed.'),
                  lab={'id': 'scn-dns-evidence', 'note': 'Gather name, IP and port evidence for a failing app before proposing a fix.'})),
    },
    '4.3': {
        'core-content': section(
            'Core content', 'NO-4.3',
            [check('A permit rule for HTTPS sits below a broader deny for the same destination. What happens to HTTPS?',
                   'It is blocked, because the deny matches first', ['It is allowed, because permits always win',
                    'It is allowed, because the HTTPS rule is more specific'],
                   'Firewalls evaluate rules top to bottom and stop at the first match, so the deny wins. Specificity and '
                   'permit-versus-deny do not reorder rules.', mc=[ORD, ORD])],
            plain('''<p><strong>NAT</strong> swaps private addresses for public ones at the edge.</p>
<ul><li><strong>PAT</strong> (NAT overload): many PCs share one public address. Outbound just works.</li>
<li>Inbound connections have nothing to match, so they need a <strong>port forward</strong> and a firewall rule.</li>
<li><strong>Static NAT</strong> maps one private address to one public address, e.g. for a server.</li></ul>
<p>A <strong>stateful firewall</strong> remembers each connection. Replies to allowed traffic come back by themselves. New traffic needs a rule.</p>
<p>Rules are read from the top. The first match wins. Anything left over is denied.</p>
<p>A <strong>DMZ</strong> holds public servers, away from internal ones.</p>''',
                  L.format('4.3') + '; ' + NAT,
                  [check('Does a stateful firewall need a rule for replies to an allowed outbound connection?', 'No, replies match the connection table',
                         ['Yes, every reply needs its own rule', 'Only when the reply is UDP'],
                         'The firewall records the outbound flow, and replies matching that entry are allowed. New inbound flows still '
                         'need a rule; UDP replies are tracked too.', mc=[STATE, STATE])]),
            analogy('''<p>Think of a company switchboard.</p>
<p>Staff all call out through one main number: that is <strong>PAT</strong>. The operator writes down who called whom, so when the other side
calls back, she knows which desk to put them through to. A stranger ringing in cold has no note to match, so they get nowhere, unless
reception has a standing instruction like “calls for sales go to extension 443”: a <strong>port forward</strong>.</p>
<p>The security guard reads a list of rules from the top and acts on the first one that fits, even if a better rule is further down. The
<strong>DMZ</strong> is the visitor lounge: guests can meet public-facing staff there without walking into the main office.</p>''',
                    L.format('4.3') + ' (switchboard analogy written for this rung); ' + NAT,
                    [check('In the switchboard story, why can a stranger not reach an internal web server behind PAT?',
                           'No translation exists for an unsolicited call', ['The public number has run out of lines',
                            'Web servers cannot use private addresses'],
                           'PAT only has entries for connections started from inside, so inbound needs a port forward. Private '
                           'addresses are fine for servers; running out of ports is a separate PAT limit.', mc=[NATT, PATT])]),
            visual('''<ol class="ladder-trace"><li>User at 10.0.5.20 browses to 203.0.113.10:443.</li>
<li>Rule 1: <code>deny inside → 203.0.113.0/24 any</code>. Matches. Blocked. No more rules are read.</li>
<li>Rule 2: <code>allow inside → any TCP 443</code>. Never reached for that destination.</li>
<li>Implicit deny at the end catches anything that matched nothing.</li>
<li>Fix: move a specific allow for 203.0.113.10:443 above rule 1, under change control, and log denies.</li>
<li>Return traffic from the server is allowed by the state table, not by a rule.</li></ol>''',
                   L.format('4.3') + '; NIST SP 800-41r1',
                   [check('In the trace, where should the specific allow rule go?', 'Above the broad deny', ['Below the allow-all-443 rule', 'After the implicit deny'],
                          'First match wins, so a specific exception must sit above the broader deny. Rules after the deny, or after '
                          'the implicit deny, are never reached for that traffic.', mc=[ORD, ORD])]),
            tryit('<p>Sort each need into the NAT type that fits, then build a rule set in the lab VM.</p>', L.format('4.3') + '; ' + NAT,
                  [check('Which servers belong in a DMZ?', 'Internet-facing ones, like a public web server',
                         ['Domain controllers, to make logins faster', 'Every internal file server, for backups'],
                         'The DMZ holds services exposed to the internet so a compromise there does not land on the internal network. '
                         'Domain controllers and file servers stay inside.', mc=[DMZ, DMZ])],
                  widget=sort('Which NAT fits?',
                              {'PAT / overload': ['Fifty PCs browsing through one public IP', 'Home router for a family'],
                               'Static NAT': ['One public IP always maps to the mail server', 'Publishing one server one-to-one'],
                               'Port forward': ['Public :443 to an internal web server behind PAT', 'Inbound access through a shared IP']},
                              'Notice that only static NAT and port forwards allow unsolicited inbound traffic.'),
                  lab={'id': 'linux-vm-nat', 'note': 'Configure NAT on the Linux VM and confirm outbound works while inbound needs a forward.'})),
        **_filler(_STD + ['network-operations-depth'], 'A short summary (NAT types, stateful rules and zones) of the core section.'),
        'networking-appliances-applications-and-functions': section(
            'Networking appliances, applications and functions', 'NO-4.3',
            [check('Hundreds of IDS alerts fire, but the attack still reaches the server. Why?', 'An IDS sees a copy and can only alert',
                   ['The IDS signatures are switched off', 'The firewall has crashed under the load'],
                   'An IDS on a SPAN port watches mirrored traffic, so it alerts but cannot drop packets; an inline IPS can. The '
                   'alerts prove signatures are working.', mc=[APPL, APPL])],
            plain('''<p>Each box does one job to traffic.</p>
<ul><li><strong>Router</strong>: forwards between networks. <strong>Switch</strong>: forwards inside a LAN. <strong>Firewall</strong>: allows or blocks.</li>
<li><strong>IDS</strong>: watches and alerts. <strong>IPS</strong>: sits in the path and blocks.</li>
<li><strong>Load balancer</strong>: shares requests across servers. <strong>Proxy</strong>: asks on someone else’s behalf. <strong>CDN</strong>: copies content near users.</li>
<li><strong>NAS</strong>: shares files. <strong>SAN</strong>: gives servers raw disks.</li>
<li><strong>QoS</strong>: lets voice go first when the link is busy.</li>
<li>IP <strong>TTL</strong> drops by one at each router. At zero, the packet is thrown away.</li></ul>''',
                  L.format('4.3') + '; ' + APP,
                  [check('What is the difference between NAS and SAN?', 'NAS shares files; a SAN presents block storage',
                         ['NAS is faster; a SAN is always cloud-based', 'NAS uses fibre; a SAN uses only Wi-Fi'],
                         'NAS serves files over SMB or NFS, while a SAN gives servers block devices (LUNs) over Fibre Channel or iSCSI. '
                         'Speed, cloud and media are not the defining difference.', mc=[APPL, APPL])]),
            analogy('''<p>Think of the staff at a large concert venue.</p>
<p>The <strong>router</strong> is the road signage between car parks; the <strong>switch</strong> is the ushers inside one hall. The
<strong>firewall</strong> checks tickets at the gate. The <strong>IDS</strong> is a CCTV operator who sees trouble and radios for help; the
<strong>IPS</strong> is a steward standing in the doorway who can stop someone. The <strong>load balancer</strong> sends queues to whichever bar is
open; the <strong>CDN</strong> is merchandise stalls placed near every entrance so nobody walks to the main shop.</p>
<p><strong>NAS</strong> is a cloakroom handing back coats (files). A <strong>SAN</strong> rents out empty lockers the guest arranges themselves (blocks).
<strong>QoS</strong> is the priority lane for ambulances when the roads are full.</p>''',
                    L.format('4.3') + ' (concert-venue analogy written for this rung); ' + APP,
                    [check('In the concert story, what is the difference between the CCTV operator and the steward in the doorway?',
                           'The steward is inline and can stop people', ['The CCTV operator blocks people, like an IPS',
                            'Both only watch and report, like two IDSs'],
                           'An IPS sits in the traffic path and can drop it; an IDS watches a copy and alerts. Only the doorway steward '
                           'can physically stop someone.', mc=[APPL, APPL])]),
            visual(svg(560, 150, 'Where appliances sit: edge with router, firewall, IDS/IPS and VPN; switches and APs; servers behind load balancer and proxy; NAS and SAN storage; CDN on the internet',
                       box(5, 10, 170, 50, 'Internet', 'CDN edge caches') + box(195, 10, 170, 50, 'Edge', 'router, firewall, IPS, VPN')
                       + box(385, 10, 170, 50, 'Distribution', 'switches, AP + controller') + box(105, 85, 170, 50, 'Servers', 'load balancer, proxy')
                       + box(295, 85, 170, 50, 'Storage', 'NAS files · SAN blocks') + arrow(175, 35, 195, 35) + arrow(365, 35, 385, 35)
                       + text(480, 145, 'QoS and TTL apply on every hop', 11))
                   + '''<ol class="ladder-trace"><li>Designers need a shared folder: a NAS over SMB.</li>
<li>The VM cluster needs shared disks it can format: a SAN over iSCSI on its own VLAN.</li>
<li>Calls break up during backups: QoS marks voice EF (DSCP 46) and queues it first on the WAN.</li>
<li>Overseas visitors find the site slow: a CDN serves images from caches near them.</li>
<li>Attacks get through despite alerts: add an inline IPS at the firewall.</li></ol>''',
                   L.format('4.3') + '; ' + APP,
                   [check('What happens when an IPv4 packet’s TTL reaches zero at a router?', 'It is discarded and ICMP Time Exceeded is sent',
                          ['It is cached until the DNS record TTL ends', 'It is forwarded to the default route instead'],
                          'The IP TTL is a hop counter that stops loops; at zero the router drops it and replies with Time Exceeded, '
                          'which traceroute uses. A DNS TTL is a cache time, a different thing.', mc=[TTLK, TTLK])]),
            tryit('<p>Match each requirement to the appliance or function that solves it.</p>', L.format('4.3') + '; ' + APP,
                  [check('Voice calls break up only while backups run over the WAN. Which function helps most?', 'QoS marking and priority queuing',
                         ['A CDN for the voice server', 'A NAS for the call recordings'],
                         'QoS classifies voice (EF) and serves it first when the link is busy. A CDN caches web content, and a NAS '
                         'stores files; neither prioritises live traffic.', mc=[APPL, APPL])],
                  widget=sort('Which box or function?',
                              {'Security': ['Block attack traffic inline: IPS', 'Alert from a SPAN copy: IDS'],
                               'Performance': ['Spread requests over servers: load balancer', 'Serve images near users: CDN', 'Voice first on a busy WAN: QoS'],
                               'Storage': ['Shared folder over SMB: NAS', 'Raw disks over iSCSI: SAN']},
                              'Notice that each box is named by what it does to traffic.'))),
    },
    '4.4': {
        'the-scenario': skip('The scenario', 'activity', 'The capstone ticket the student works; it sets up practice, not a concept.'),
        'your-turn-scaffolded-checklist': skip('Your turn — scaffolded checklist', 'activity', 'The checklist the student fills in during the capstone drill.'),
        'common-beginner-mistakes': skip('Common beginner mistakes', 'reference', 'Short list of capstone pitfalls; the ideas behind them are laddered in 4.1–4.3.'),
        'check-your-understanding': skip('Check your understanding', 'activity', 'A self-check prompt for the capstone; it is practice, not an explanation.'),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '4.1': {'core-content': 'f08e71b8591c', 'incident-application': 'db207ea562c8', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': 'ec08e2a0f067', 'client-addressing-in-the-real-world': 'be040c5e9ac0', 'beyond-the-quiz': '593477debeaf'},
    '4.2': {'core-content': '518ad9fffc8b', 'incident-application': 'e0e61ccedcab', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '44599507dbad', 'ports-as-clues-not-magic-numbers': '061f8ea7b03c', 'beyond-the-quiz': '55e742c3b869'},
    '4.3': {'core-content': 'f3668cd04a12', 'incident-application': '990d80cec504', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '8ae57f3d5a6a', 'beyond-the-quiz': '674b404a67bd', 'networking-appliances-applications-and-functions': '6b59091e19a6'},
    '4.4': {'the-scenario': '16429d05880a', 'your-turn-scaffolded-checklist': '3029ce383f1b', 'common-beginner-mistakes': '4279a7f93ee2', 'check-your-understanding': 'cdda2cb3f068'},
}

# Option B pass 3: the practice/capstone blocks, core-concepts and depth signposts are bespoke ladders (_p3n4.py).
from curriculum_v2.ladder.netops._p3 import wire as _wire  # noqa: E402
from curriculum_v2.ladder.netops._p3n4 import SECS as _P3  # noqa: E402

_wire(LESSONS, MISCONCEPTIONS, _P3, 'NO-4.3')
