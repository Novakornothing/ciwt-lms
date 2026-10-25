"""ITSUP Chapter 5 — Networking for Support Technicians (pass 10 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 5
SOURCES_USED = ['ietf-rfc1918', 'ietf-rfc4291', 'ietf-rfc2131', 'iana-ports', 'cisa-wireless', 'ms-netsh-wlan']

_NOTE = 'Core content added in pass 10.'

LESSONS = {
    (5, 1): {
        'objectives': [
            'Interpret an ipconfig /all output: address, prefix, gateway, DNS, DHCP and lease times',
            'Calculate the network, broadcast and usable host range for an IPv4 prefix from /24 to /30',
            'Recognise private, link-local (APIPA) and shared (carrier-grade NAT) IPv4 ranges',
            'Identify IPv6 link-local, global and unique-local addresses on a Windows client',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Prefix length and the mask are the same fact</h3>
<p>An IPv4 address is 32 bits. The <strong>prefix length</strong> (the “/26” in CIDR notation) says how many of those bits name the
network; the rest name the host. The subnet mask writes the same thing as four numbers. Each step down in prefix halves the network.</p>
''' + table(['Prefix', 'Mask', 'Addresses', 'Usable hosts', 'Block size in the last octet'], [
            ['/24', '255.255.255.0', '256', '254', '256 (whole octet)'],
            ['/25', '255.255.255.128', '128', '126', '128'],
            ['/26', '255.255.255.192', '64', '62', '64'],
            ['/27', '255.255.255.224', '32', '30', '32'],
            ['/28', '255.255.255.240', '16', '14', '16'],
            ['/29', '255.255.255.248', '8', '6', '8'],
            ['/30', '255.255.255.252', '4', '2', '4'],
        ]) + '''
<p>Usable hosts are the addresses minus two: the first address names the network and the last is the broadcast address. (Point-to-point
links may use /31, a special case defined for exactly two hosts; you will meet it on routers, not on client tickets.)</p>
''' + worked('is the gateway on the same subnet?', '''
<p>A PC shows <code>192.168.10.77</code> with mask <code>255.255.255.192</code> (/26) and default gateway <code>192.168.10.1</code>, and
nothing beyond the LAN works. The block size for /26 is 64, so the networks start at .0, .64, .128 and .192. 77 falls in the block that
starts at 64: network <code>192.168.10.64</code>, broadcast <code>192.168.10.127</code>, hosts <code>.65</code>–<code>.126</code>. The gateway
<code>.1</code> is in a <em>different</em> subnet, so the PC cannot reach it directly. Either the mask or the gateway on this PC is wrong —
compare with a working PC on the same switch port VLAN before changing anything. Note: “192.168.10.77/26, gw .1 outside .64–.127; working
neighbour has /24. Static mask typo suspected; changed to /24 per neighbour and DHCP scope → gateway reachable.”</p>''') + '''
<h3>Ranges that tell a story</h3>
''' + table(['Range', 'Meaning', 'What it suggests on a ticket'], [
            ['10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16', 'Private addresses (RFC 1918), not routed on the internet', 'Normal for a LAN; NAT at the edge translates them'],
            ['169.254.0.0/16', 'IPv4 link-local, which Windows calls APIPA (RFC 3927)', 'No DHCP lease: check link and DHCP, not DNS'],
            ['100.64.0.0/10', 'Shared address space for carrier-grade NAT (RFC 6598)', 'The upstream “public” address is itself behind the ISP’s NAT; inbound connections will not reach you'],
            ['127.0.0.0/8', 'Loopback — the PC itself', 'ping 127.0.0.1 tests the TCP/IP stack, nothing more'],
        ]) + '''
<h3>IPv6 on the same screen</h3>
<p>Windows clients run IPv6 alongside IPv4. In <code>ipconfig /all</code> you will usually see a <strong>link-local</strong> address
beginning <code>fe80::</code> (from <code>fe80::/10</code>), often followed by <code>%</code> and an interface number; every IPv6 interface
has one, and it only works on the local link. A <strong>global unicast</strong> address (currently allocated from <code>2000::/3</code>,
so it starts with 2 or 3) means the network hands out routable IPv6. <strong>Unique local</strong> addresses (<code>fc00::/7</code>, in
practice <code>fd</code>…) are IPv6’s private range. Hosts can configure their own addresses from the router’s advertisements
(<strong>SLAAC</strong>) or get them from DHCPv6. A client with only <code>fe80::</code> addresses has no routed IPv6, which is normal on
many LANs — it is not, on its own, a fault.</p>
''' + cfu(
            ('How many usable hosts does a /27 give?',
             '30: 32 addresses minus the network and broadcast addresses.'),
            ('A PC has 192.168.10.77/26. What are its network and broadcast addresses?',
             'Network 192.168.10.64 and broadcast 192.168.10.127 (hosts .65 to .126).'),
            ('ipconfig shows 169.254.x.x. Which two things do you check first?',
             'The link (cable, Wi-Fi association) and whether a DHCP server answered — not DNS.')),
        'sources': ['ietf-rfc1918', 'ietf-rfc4291'],
    },
    (5, 2): {
        'objectives': [
            'Map a user’s symptom to the service, port and transport protocol it implies',
            'Choose the right test for a service: ping for reachability, Test-NetConnection for a port, nslookup for a name',
            'Explain the DHCP lease process (DORA) and what renewal at T1 and T2 means for a client',
            'Interpret common DNS record types (A, AAAA, CNAME, MX, TXT, PTR) in a lookup result',
        ],
        'html': sme_note(_NOTE) + '''
<h3>A port is a service promise</h3>
<p>An address gets a packet to the host; the <strong>port</strong> picks the service on that host, and the transport (TCP or UDP) says how
it is carried. Ping uses ICMP and has no port at all, so a successful ping proves only that the host answers ping. The ports in the
reference table in this lesson are the ones whose number changes your first test.</p>
''' + table(['User says', 'Service and port', 'Test that proves it'], [
            ['“Websites don’t load, but Teams chat works”', 'HTTPS, TCP 443 (and proxy settings)', 'Test-NetConnection site -Port 443; check proxy'],
            ['“The shared drive is gone”', 'SMB, TCP 445', 'Test-NetConnection fileserver -Port 445'],
            ['“I can’t remote into my desktop”', 'RDP, TCP/UDP 3389', 'Test-NetConnection pc -Port 3389 (and whether RDP is allowed)'],
            ['“Names don’t resolve”', 'DNS, UDP/TCP 53', 'nslookup name; repeat against the shop’s second DNS server'],
            ['“No network after I plug in”', 'DHCP, UDP 67 (server) / 68 (client)', 'ipconfig /all: lease obtained? 169.254?'],
            ['“The clock is wrong and sign-in fails”', 'NTP, UDP 123', 'w32tm /query /status'],
        ]) + '''
<p><code>Test-NetConnection</code> (PowerShell) with <code>-Port</code> reports <code>TcpTestSucceeded : True</code> when something accepted
the TCP connection. It says nothing about UDP services and nothing about whether the application then works, but it separates “the path
or a firewall blocks this port” from “the service answers”.</p>
<h3>How a client gets its address: DORA</h3>
''' + figure('f5-2', 'DHCP lease exchange (DORA)', ['Discover\n(client\nbroadcast)', 'Offer\n(server)', 'Request\n(client)', 'Ack\n(server)', 'Renew at T1\n(50 % of lease)', 'Rebind at T2\n(87.5 %)'],
             'Six boxes. The client broadcasts a Discover; a DHCP server replies with an Offer; the client sends a Request for that offer; the server '
             'confirms with an Ack and the client uses the address. Halfway through the lease (T1, 50 per cent) the client asks the same server to '
             'renew; if it gets no answer by T2 (87.5 per cent) it asks any server. If the lease expires without renewal, the address is given up.',
             'Discover, Offer, Request, Ack — then renewal at T1 and rebinding at T2 keep the lease alive.', cols=3) + '''
<p>Because the first message is a broadcast, DHCP only crosses routers when a <strong>relay</strong> (an “IP helper”) forwards it. If one
VLAN gets APIPA addresses and others do not, a missing or broken relay is a better guess than a dead server. On Windows,
<code>ipconfig /release</code> and <code>ipconfig /renew</code> repeat the exchange; <code>ipconfig /all</code> shows
<em>Lease Obtained</em> and <em>Lease Expires</em>.</p>
<h3>Reading a DNS answer</h3>
''' + table(['Record', 'Holds', 'Ticket relevance'], [
            ['A / AAAA', 'IPv4 / IPv6 address for a name', 'Wrong or stale address after a server move'],
            ['CNAME', 'An alias to another name', 'The alias resolves only if its target does'],
            ['MX', 'The mail servers for a domain', 'Mail not arriving at a domain'],
            ['TXT', 'Free text — SPF, DKIM and DMARC policies, domain verification', 'Outgoing mail marked as spam; SaaS domain verification'],
            ['PTR', 'Reverse lookup: address to name', 'Logs showing addresses; some mail servers check it'],
            ['NS / SOA', 'Which servers are authoritative for a zone', 'Owner of the zone — who to escalate to'],
        ]) + '''
<p><code>nslookup app.training.local</code> shows which server answered and what it returned. <code>NXDOMAIN</code> (“Non-existent
domain”) means that server says the name does not exist; a time-out means no server answered. Those are different tickets: the first goes
to the owner of the zone, the second is a path or resolver problem.</p>
''' + cfu(
            ('Ping to the file server works but the mapped drive fails. Which test is next?',
             'Test-NetConnection fileserver -Port 445: ping does not test SMB.'),
            ('A client sent a DHCP Discover and got no Offer. What address will Windows use?',
             'A 169.254.x.x (APIPA) link-local address.'),
            ('Which DNS record type lists the mail servers for a domain?',
             'MX.')),
        'sources': ['iana-ports', 'ietf-rfc2131'],
    },
    (5, 3): {
        'objectives': [
            'Isolate a client connectivity fault in the fixed order: link, lease, local IP, gateway, remote IP, name, service',
            'Interpret the result of each test and name the layer it rules in or out',
            'Document each test as action → result so the next technician can continue',
        ],
        'html': sme_note(_NOTE) + '''
<h3>The order, and why it does not change</h3>
<p>Each test depends on the one before. Testing a name before you have a lease, or a service before you can reach the gateway, gives a
failure that tells you nothing. Work down this list and stop at the first failure.</p>
''' + figure('f5-3', 'Client connectivity isolation order', ['Link\n(cable / Wi-Fi)', 'Lease\n(ipconfig)', 'Ping\ngateway', 'Ping remote\nIP', 'Resolve\nname', 'Test the\nservice port'],
             'Six boxes in order. Check the physical or wireless link; check ipconfig for a real lease rather than 169.254; ping the default gateway; '
             'ping a known remote address; resolve the name with nslookup; then test the service port with Test-NetConnection. Stop at the first '
             'step that fails: that is the layer to work on.',
             'Stop at the first failing step; everything after it is untested, not broken.', cols=3) + table(['Step', 'Command / check', 'If it fails'], [
            ['Link', 'Adapter status, link lights; netsh wlan show interfaces (State, SSID, Signal)', 'Cable, port, switch port, Wi-Fi association or wrong SSID'],
            ['Lease', 'ipconfig /all — address, mask, gateway, DNS; not 169.254', 'DHCP server, relay, scope full, or the VLAN on the switch port'],
            ['Gateway', 'ping the default gateway', 'Local LAN problem, wrong mask/gateway, or the gateway is down'],
            ['Remote IP', 'ping (or tracert) a known external or data-centre address', 'Upstream routing, NAT or a firewall beyond the gateway'],
            ['Name', 'nslookup name; compare with the shop’s second resolver', 'DNS server, the record, or the client’s DNS settings'],
            ['Service', 'Test-NetConnection host -Port n; open the app', 'Firewall rule, stopped service, account or the application'],
        ]) + '''
<p>Some gateways and many internet hosts drop ping by policy, so a failed ping to a remote host is weaker evidence than a successful
one; confirm with a second target or a port test before you call the upstream down. <code>tracert</code> shows where along the route
replies stop; the last hop that answers is where to look, not necessarily what is broken.</p>
''' + worked('name problem, proved', '''
<p>Ticket: “The training portal is down.” Link up, <code>ipconfig</code> 10.20.30.47/24 gw 10.20.30.1 DNS 10.20.30.10, ping gateway 4/4,
ping 10.20.30.50 (the portal server) 4/4, <code>nslookup portal.training.local</code> → NXDOMAIN from 10.20.30.10. The path and the server
are fine; the name is missing. <code>ipconfig /flushdns</code> changes nothing (as expected — the server says the name does not exist).
Note: “Link/lease/gw/IP OK (10.20.30.50 replies). nslookup portal.training.local NXDOMAIN from 10.20.30.10. Escalated to DNS owner: record
missing. Users can reach https://10.20.30.50 meanwhile if certificate policy allows — not advised.”</p>''') + scenario('one VLAN without leases', '''
<p>On Monday morning every PC in one training room shows 169.254 addresses; the next room is fine. The technician does not touch DNS or
reimage anything. Link lights are on; a laptop with a static address on the same port pings the gateway, so the switch and VLAN work. The
problem is the lease step, for one VLAN only: the network owner finds that a weekend router change removed the DHCP relay (IP helper) for
that VLAN. With the relay restored, <code>ipconfig /renew</code> on each PC brings real addresses. The note lists the scope, the evidence
and the change that fixed it.</p>''') + cfu(
            ('Ping to the gateway fails and ipconfig shows a good address. Which layer is next?',
             'The local LAN or the gateway itself (also check the mask and gateway are correct), not DNS.'),
            ('nslookup returns NXDOMAIN. Will ipconfig /flushdns fix it?',
             'No. The server says the name does not exist; the record must be fixed by the zone owner.')),
        'sources': ['ietf-rfc2131', 'iana-ports'],
    },
    (5, 4): {
        'objectives': [
            'Configure a SOHO router and access point to a current security baseline',
            'Choose WPA3-Personal, WPA2/WPA3 transition or Enhanced Open for a stated situation',
            'Select 2.4, 5 or 6 GHz and a channel plan for a small office',
            'Use netsh wlan to read a Windows client’s association, signal and authentication',
        ],
        'html': sme_note(_NOTE) + '''
<h3>The baseline, in order of impact</h3>
<ol>
<li><strong>Admin credentials:</strong> change the default administrator password (and username, if the device allows). This is the
single biggest hole on small routers.</li>
<li><strong>Remote administration off:</strong> disable WAN-side management unless a documented need exists.</li>
<li><strong>Encryption:</strong> WPA3-Personal, or WPA2/WPA3 transition mode while older devices remain. Never WEP or WPA with TKIP.</li>
<li><strong>WPS off:</strong> the PIN method of Wi-Fi Protected Setup can be brute-forced.</li>
<li><strong>Guest network</strong> for visitors and personal devices, with client isolation.</li>
<li><strong>Firmware</strong> updated; replace equipment that no longer receives updates.</li>
</ol>
<p>CISA’s home-network guidance gives the same list. Hiding the SSID and MAC filtering are not on it: the network name still appears in
client probes, and MAC addresses are sent unencrypted and can be copied.</p>
''' + table(['Mode', 'How it protects', 'Use when'], [
            ['WPA3-Personal (SAE)', 'Simultaneous Authentication of Equals resists offline password guessing from a captured handshake', 'All clients support WPA3; required on 6 GHz'],
            ['WPA2/WPA3 transition', 'WPA3 clients use SAE, older clients use WPA2-PSK with AES', 'A mix of old and new devices — plan to retire the old ones'],
            ['WPA2/WPA3-Enterprise (802.1X)', 'Each user signs in; keys are per user', 'Offices with a RADIUS/identity service'],
            ['Enhanced Open (OWE)', 'Encrypts traffic on an open network without a password; no authentication', 'Café-style guest Wi-Fi'],
        ]) + '''
<h3>Bands and channels</h3>
<p><strong>2.4 GHz</strong> reaches further and passes walls better but is crowded; in North America only channels <strong>1, 6 and 11</strong>
do not overlap, so neighbouring access points should use different ones of those three. <strong>5 GHz</strong> has many more channels and
higher speeds at shorter range. <strong>6 GHz</strong> (Wi-Fi 6E and Wi-Fi 7) adds wide, clean channels, requires WPA3, and only newer
clients can see it. A client that “can’t find the network” may simply not support the band the SSID was moved to.</p>
<h3>Reading the client side</h3>
<p><code>netsh wlan show interfaces</code> shows the SSID, BSSID (which access point), radio type, authentication, channel, receive and
transmit rates and signal percentage. <code>netsh wlan show wlanreport</code> (as administrator) writes an HTML report of recent
connections, disconnections and their reasons to <code>C:\\ProgramData\\Microsoft\\Windows\\WlanReport\\</code>. Record the signal,
channel and authentication before you blame the access point.</p>
''' + worked('the printer that left the Wi-Fi', '''
<p>After the router was switched to WPA3-only, a small office’s 2016 label printer drops off the network; laptops are fine. The printer’s
spec sheet lists WPA2-PSK only. The technician proposes, as a change: set the SSID to WPA2/WPA3 transition mode so laptops keep WPA3, or
put the printer on Ethernet; record the printer as a replacement candidate. The owner approves Ethernet. Note: “Printer supports WPA2 only;
SSID now WPA3-only. Moved printer to wired port 7 (approved). WPA3-only retained.”</p>''') + cfu(
            ('Which baseline change closes the most common SOHO hole?',
             'Changing the default administrator password (and disabling remote administration).'),
            ('Why is hiding the SSID not a security control?',
             'Clients still send the name in probes and the radio is visible; it only inconveniences legitimate users.'),
            ('Which three 2.4 GHz channels do not overlap in North America?',
             '1, 6 and 11.')),
        'sources': ['cisa-wireless', 'ms-netsh-wlan'],
    },
    (5, 5): {
        'objectives': [
            'Run a full client triage from identity through service test without skipping a layer',
            'Write a note in which every line is a test and its result',
            'Decide when to stop and escalate with evidence instead of changing shared network equipment',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Capstone: “the internet is down”</h3>
<p>This is the most common network ticket, and the sentence is never the diagnosis. Work the order from Lesson 5.3, write one line per
test, and stop at the layer that fails. Changes to shared equipment (switches, the router, DHCP scopes, DNS zones) belong to their owners;
your evidence is what lets them act quickly.</p>
''' + table(['Line', 'Example', 'What a reviewer checks'], [
            ['Identity', 'NOVAK-W11-07, user jdoe, Ethernet, room 2', 'Which device, which path'],
            ['Lease', 'ipconfig: 10.20.30.47/24, gw 10.20.30.1, DNS 10.20.30.10, DHCP yes', 'Not 169.254; mask and gateway consistent'],
            ['Gateway', 'ping 10.20.30.1: 4/4', 'Local LAN works'],
            ['Remote IP', 'ping 10.20.30.50: 4/4', 'The server answers'],
            ['Name', 'nslookup app.training.local: NXDOMAIN from 10.20.30.10', 'The failing layer, with the server that said so'],
            ['Action / next', 'flushdns: no change (expected). Escalated to DNS owner', 'Who owns the next step'],
        ]) + worked('a note that would survive 02:00', '''
<p>“NOVAK-W11-07 (jdoe), wired. Lease 10.20.30.47/24 gw .1 DNS .10. Ping gw 4/4; ping 10.20.30.50 4/4. nslookup app.training.local →
NXDOMAIN from 10.20.30.10; same from secondary .11. Flushdns no change. Not a client fault. Escalated to DNS owner (ticket 4471) for
missing A record. Firewall unchanged.”</p>
<p>Notice what it does not contain: no “rebooted to see”, no “reset network settings”, no firewall disabled “to test”. Each of those
changes something without testing anything.</p>''') + '''
<h3>Pass bar</h3>
<ul>
<li>The lab note has every step in order, each with its result, and stops at the first failing layer.</li>
<li>The firewall stays on, and nothing on shared equipment was changed without its owner.</li>
<li>A peer can say from the note alone which team receives the ticket.</li>
</ul>
''' + cfu(
            ('Why does the note include the secondary DNS server’s answer?',
             'It shows the missing record is not one server’s fault, which points at the zone, not the resolver.'),
            ('What is wrong with “disabled the firewall to test”?',
             'It changes security without isolating anything, and the result proves little; test the port with Test-NetConnection instead.')),
        'sources': ['iana-ports', 'ietf-rfc1918'],
    },
}

GLOSSARY = [
    ('CIDR', 'Classless Inter-Domain Routing notation: an address followed by /n, the number of network bits (for example 192.168.10.0/26).'),
    ('Broadcast address', 'The last address in an IPv4 subnet, used to reach every host on it; it cannot be assigned to a host.'),
    ('Carrier-grade NAT', 'ISP-level address translation using the 100.64.0.0/10 shared range, so the customer’s “public” address is itself translated.'),
    ('Link-local address', 'An address valid only on the local link: 169.254.0.0/16 (APIPA) in IPv4 and fe80::/10 in IPv6.'),
    ('Unique local address', 'An IPv6 private address from fc00::/7 (in practice fd00::/8), not routed on the internet.'),
    ('SLAAC', 'Stateless Address Autoconfiguration: an IPv6 host builds its own address from the prefix a router advertises.'),
    ('DORA', 'The DHCP lease exchange: Discover, Offer, Request, Acknowledge.'),
    ('DHCP relay', 'A router function (an IP helper) that forwards DHCP broadcasts from one subnet to a DHCP server on another.'),
    ('NXDOMAIN', 'A DNS response meaning the queried name does not exist on the server that answered.'),
    ('MX record', 'A DNS record listing the mail servers that accept email for a domain, with priorities.'),
    ('SAE', 'Simultaneous Authentication of Equals: the WPA3-Personal handshake that resists offline password guessing.'),
    ('Enhanced Open', 'Opportunistic Wireless Encryption (OWE): encryption for open Wi-Fi networks without a password.'),
    ('WPS', 'Wi-Fi Protected Setup: a convenience pairing method whose PIN mode is weak and should be disabled.'),
    ('Default gateway', 'The router address a host sends traffic to when the destination is outside its own subnet; it must be inside that subnet.'),
]

PLAN = {
    'warmup': 'Project an ipconfig /all with a /26 mask and a gateway outside the subnet. Pairs find the problem without a calculator.',
    'guided': 'Fill the prefix table on the board and do three subnet calculations (5.1); match six user sentences to ports and tests (5.2); run the isolation order with win-ipconfig and win-dns-break (5.3); read netsh wlan show interfaces on w11-wlan (5.4).',
    'worked_example': 'Lesson 5.1 gateway outside the subnet; 5.3 name problem, proved; 5.5 the 02:00 note.',
    'cfu': ['Usable hosts in a /27?',
            '192.168.10.77/26: network and broadcast?',
            'Ping works, mapped drive fails: next test?',
            'NXDOMAIN: will flushdns help?'],
    'exit_ticket': 'Write the six-line note for a PC whose ping to the gateway fails while its address is good.',
    'misconceptions_add': ['“Ping works, so the service works.” Ping uses ICMP; test the port.',
                           '“Flush DNS” as a first step. It cannot fix a missing lease or a missing record.',
                           '“Hidden SSID and MAC filtering secure the Wi-Fi.” Admin password, WPA3 and WPS off do.'],
    'classroom_lab': '',
    'materials_add': 'Printed ipconfig /all outputs (good, APIPA, wrong mask); a subnet worksheet from /24 to /30; a SOHO router or its emulator page for the baseline walk-through.',
}

ITEMS = [
    item('IT-5.1', 1, 'How many usable host addresses does a /27 IPv4 subnet provide?',
         '30', ['32', '62', '126'],
         'A /27 has 32 addresses; the network and broadcast addresses leave 30 usable.'),
    item('IT-5.1', 2, 'A PC has 192.168.10.77/26. What is its subnet’s network address?',
         '192.168.10.64', ['192.168.10.128', '192.168.10.0', '192.168.10.32'],
         '/26 blocks are 64 wide (.0, .64, .128, .192); .77 is in .64–.127, so the network address is .64.'),
    item('IT-5.1', 3, 'ipconfig shows 169.254.40.12. What does this address indicate?',
         'No DHCP lease was obtained', ['A DNS server is unreachable', 'The PC is behind carrier NAT', 'IPv6 is turned off on the PC'],
         '169.254.0.0/16 is link-local (APIPA): Windows assigned it because no DHCP server answered.'),
    item('IT-5.1', 4, 'Which IPv6 address is link-local and valid only on the local network segment?',
         'fe80::3aff:fe4d:12', ['2001:db8:10:4a2::25:1c', 'fd12:3456:789a:1::1:20', '::ffff:192.168.100.25'],
         'Link-local IPv6 addresses come from fe80::/10; fd… is unique local and 2001:db8 is the documentation prefix.'),
    item('IT-5.2', 1, 'Ping to the file server works, but the mapped drive fails. Which port should be tested?',
         'TCP 445', ['UDP 123', 'TCP 3389', 'UDP 67'],
         'Mapped drives use SMB on TCP 445; Test-NetConnection server -Port 445 tests it.'),
    item('IT-5.2', 2, 'In the DHCP exchange, which message does the client send after receiving an Offer?',
         'Request', ['Discover', 'Acknowledge', 'Release'],
         'The order is Discover, Offer, Request, Acknowledge (DORA).'),
    item('IT-5.2', 3, 'Which DNS record type identifies the mail servers for a domain?',
         'MX record', ['PTR record', 'CNAME record', 'AAAA record'],
         'MX records list a domain’s mail servers; PTR is reverse lookup and CNAME is an alias.'),
    item('IT-5.3', 1, 'A PC has a valid lease but cannot ping its default gateway. Which layer is next to check?',
         'The local LAN and the gateway', ['The DNS server and its records', 'The web proxy configuration', 'The application’s service port'],
         'Stop at the first failing step: the gateway is unreachable, so name and service tests would prove nothing yet.'),
    item('IT-5.3', 2, 'Ping to the server’s IP works; nslookup of its name returns NXDOMAIN. What is the next action?',
         'Escalate the missing record to the DNS owner', ['Release and renew the client’s DHCP lease now', 'Replace the PC’s network adapter with a new one', 'Disable the firewall and then test again'],
         'The path works and the server says the name does not exist; the zone owner must add or fix the record.'),
    item('IT-5.3', 3, 'Every PC in one room gets 169.254 addresses; other rooms are fine. What is the most likely cause?',
         'DHCP relay missing for that VLAN', ['A DNS zone record was deleted overnight', 'All of the room’s PCs need reimaging', 'The internet provider has an outage'],
         'Only one subnet fails the lease step, which points at the relay (IP helper) or scope for that VLAN.'),
    item('IT-5.4', 1, 'Which change most improves a new SOHO router’s security?',
         'Change the default admin password', ['Hide the SSID broadcast on the router', 'Turn on MAC address filtering', 'Move the router to channel 6'],
         'Default credentials are the biggest hole; hiding the SSID and MAC filtering are not security controls.'),
    item('IT-5.4', 2, 'Old and new devices must share one SSID securely. Which mode fits best?',
         'WPA2/WPA3 transition mode', ['WEP with a long passphrase', 'Open network with WPS on', 'WPA with TKIP encryption'],
         'Transition mode lets WPA3 clients use SAE and older clients WPA2-AES; WEP and TKIP are broken.'),
    item('IT-5.4', 3, 'Which command shows a Windows client’s SSID, signal and authentication type?',
         'netsh wlan show interfaces', ['ipconfig /displaydns', 'Get-NetIPConfiguration', 'netsh interface show interface'],
         'netsh wlan show interfaces reports the association, signal, channel and authentication.'),
]
