"""Explanation ladder — NETOPS chapter 3 (Routing, WAN, Cloud and Wireless). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Facts follow the lesson and the primary sources named in each rung.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 3

L = 'Course lesson {} (the original section), re-explained'
RT = 'RFC 1812 (IPv4 router requirements, longest match); RFC 2328 (OSPFv2); RFC 4271 (BGP-4); RFC 5798 (VRRPv3); Cisco IOS administrative distance documentation'
WAN = 'CableLabs DOCSIS 3.1 specifications; ITU-T G.992/G.993 (ADSL/VDSL); RFC 4301 (IPsec architecture); MEF Carrier Ethernet definitions'
CLOUD = 'NIST SP 800-145 (cloud definition); Amazon VPC User Guide (security groups, network ACLs, internet and NAT gateways); RFC 7348 (VXLAN); NIST SP 800-207 (zero trust); CompTIA Network+ N10-009 objectives 1.3 and 1.8'
WIFI = 'IEEE Std 802.11-2020 and amendments 802.11h/ax/be; Wi-Fi Alliance WPA3 and Wi-Fi 6E specifications; CompTIA Network+ N10-009 objective 2.3'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO3-CONNECTED-STAYS': {
        'obj': 'NO-3.1', 'label': 'Thinking a connected route stays in the table when its interface goes down',
        'fix': 'Connected routes exist only while the interface is up with an address; down interface, route gone.',
        'terms': ['connected route', 'interface down', 'routing table'], 'source': L.format('3.1') + '; RFC 1812', 'review': R},
    'MC-L-NO3-DEMARC-SIDE': {
        'obj': 'NO-3.2', 'label': 'Opening an ISP ticket before proving your own side of the demarcation point',
        'fix': 'Check your edge interface, addressing and cabling to the demarc first, then give the ISP that evidence.',
        'terms': ['demarc', 'isp ticket', 'circuit id', 'cpe'], 'source': L.format('3.2'), 'review': R},
    'MC-L-NO3-SAT-LATENCY': {
        'obj': 'NO-3.2', 'label': 'Thinking satellite latency comes from low bandwidth rather than the distance to orbit',
        'fix': 'GEO satellites are about 36,000 km up, so the round trip alone adds hundreds of milliseconds; LEO is far lower.',
        'terms': ['satellite', 'geo', 'leo', 'latency'], 'source': L.format('3.2'), 'review': R},
    'MC-L-NO3-CLOUD-BLOCKS': {
        'obj': 'NO-3.2', 'label': 'Mixing up internet gateway, NAT gateway, security group and network ACL roles in a VPC',
        'fix': 'Internet gateway: public subnets in and out. NAT gateway: private subnets out only. SG: per instance. NACL: per subnet.',
        'terms': ['vpc', 'nat gateway', 'internet gateway', 'security group', 'network acl'], 'source': L.format('3.2') + '; ' + CLOUD, 'review': R},
    'MC-L-NO3-VXLAN-SCALE': {
        'obj': 'NO-3.2', 'label': 'Not knowing why VXLAN scales beyond VLANs, or thinking it is a security or WAN feature',
        'fix': 'VXLAN carries layer-2 frames in UDP 4789 with a 24-bit ID (about 16 million segments) versus 4,094 VLANs.',
        'terms': ['vxlan', 'vni', 'vlan', '24-bit'], 'source': L.format('3.2') + '; RFC 7348', 'review': R},
    'MC-L-NO3-PERIMETER-TRUST': {
        'obj': 'NO-3.2', 'label': 'Thinking zero trust means trusting anything already inside the network perimeter',
        'fix': 'Zero trust gives no implicit trust from location; every request is authenticated and authorised (NIST SP 800-207).',
        'terms': ['zero trust', 'perimeter', 'least privilege'], 'source': L.format('3.2') + '; NIST SP 800-207', 'review': R},
    'MC-L-NO3-RSSI-SIGN': {
        'obj': 'NO-3.3', 'label': 'Reading a more negative RSSI (e.g. −75 dBm) as a stronger signal than −55 dBm',
        'fix': 'RSSI in dBm is negative; closer to zero is stronger.',
        'terms': ['rssi', 'dbm', 'signal'], 'source': L.format('3.3'), 'review': R},
    'MC-L-NO3-AP-IDS': {
        'obj': 'NO-3.3', 'label': 'Mixing up SSID, BSSID and ESSID, or autonomous and lightweight APs',
        'fix': 'SSID: network name. BSSID: one AP radio’s MAC. ESSID: one SSID across many APs. Lightweight APs are controller-managed.',
        'terms': ['ssid', 'bssid', 'essid', 'lightweight', 'controller'], 'source': L.format('3.3') + '; ' + WIFI, 'review': R},
    'MC-L-NO3-MORE-POWER': {
        'obj': 'NO-3.3', 'label': 'Fixing weak or noisy Wi-Fi by turning transmit power up instead of fixing placement, antennas or channels',
        'fix': 'More power raises co-channel contention and does not help the client’s weaker transmit back; re-plan and re-survey.',
        'terms': ['transmit power', 'antenna', 'survey', 'coverage'], 'source': L.format('3.3'), 'review': R},
}

SP, AD, STARS, FHRP, CONN = 'MC-NO3-SHORTER-PREFIX', 'MC-NO3-AD-DYNAMIC-WINS', 'MC-NO3-TRACEROUTE-STARS', 'MC-NO3-FHRP-PURPOSE', 'MC-L-NO3-CONNECTED-STAYS'
THIN, LANW, DEM, SAT, CB, VX = ('MC-NO3-THIN-EVIDENCE', 'MC-NO3-LAN-FEATURE-AS-WAN', 'MC-L-NO3-DEMARC-SIDE', 'MC-L-NO3-SAT-LATENCY',
                                'MC-L-NO3-CLOUD-BLOCKS', 'MC-L-NO3-VXLAN-SCALE')
OVL, SNR, PSK, RSSI, IDS, PWR = ('MC-NO3-CHANNEL-OVERLAP', 'MC-NO3-SNR-MATH', 'MC-NO3-SHARED-KEY-FOR-STAFF', 'MC-L-NO3-RSSI-SIGN',
                                 'MC-L-NO3-AP-IDS', 'MC-L-NO3-MORE-POWER')

_TXT = {
    'core-concepts': None,
    'incident-application': ('activity', 'A practice drill (write a ticket timeline and a status sentence); it applies the lesson rather than explaining a concept.'),
    'standard-of-work': ('reference', 'A two-line list of work-habit reminders (record negative results; no untracked parallel changes) repeated in every lesson.'),
    'practice-standard-for-this-lesson': ('activity', 'A self-study instruction to build a 5–9 step checklist; it is an exercise, not an explanation.'),
    'network-operations-depth': ('orientation', 'A course-wide signpost paragraph repeated in every lesson; each topic it names is laddered in its own lesson.'),
    'beyond-the-quiz': ('activity', 'A study-skills prompt (write your own scenario, explain to a non-technical user); an exercise, not a concept.'),
}
_HEAD = {'incident-application': 'Incident application', 'standard-of-work': 'Standard of work',
         'practice-standard-for-this-lesson': 'Practice standard for this lesson',
         'network-operations-depth': 'Network operations depth', 'beyond-the-quiz': 'Beyond the quiz'}


def _filler(keys, summary):
    out = {'core-concepts': same_as('core-content', 'Core concepts', summary)}
    for k in keys:
        out[k] = skip(_HEAD[k], *_TXT[k])
    return out


_STD5 = ['incident-application', 'standard-of-work', 'practice-standard-for-this-lesson', 'beyond-the-quiz']

LESSONS = {
    '3.1': {
        'core-content': section(
            'Core content', 'NO-3.1',
            [check('A router has routes for 172.16.0.0/12 and 172.16.5.0/24. Which one carries a packet to 172.16.5.20?',
                   'The /24', ['The /12, because it was configured first', 'Both in turn, sharing the load between them'],
                   'Routers use longest-prefix match: the /24 is more specific, so it wins. Order of configuration does not '
                   'matter, and two different prefixes are not load-shared.', mc=[SP, AD])],
            plain('''<p>A router keeps a list of networks it can reach. That list is the <strong>routing table</strong>.</p>
<ul><li><strong>Connected</strong> routes appear by themselves for each working interface.</li>
<li><strong>Static</strong> routes are typed in by a person.</li>
<li><strong>OSPF</strong> learns routes from other routers in the same company. <strong>BGP</strong> swaps routes between companies on the Internet.</li>
<li>The <strong>default route</strong> (0.0.0.0/0) is used when nothing else matches. It usually points to the ISP.</li></ul>
<p>When several routes match, the most specific one (the longest prefix) wins.</p>
<p>VRRP or HSRP let two routers share one gateway address, so hosts keep working if one fails.</p>''',
                  L.format('3.1') + '; ' + RT,
                  [check('What happens to a connected route when its interface goes down?', 'It is removed from the table',
                         ['It stays, but with a higher metric', 'It turns into the default route'],
                         'Connected routes exist only while the interface is up with an address. They are not kept with a worse '
                         'metric, and they never become a default route.', mc=[CONN, CONN])]),
            analogy('''<p>Think of a parcel depot sorting by postcode.</p>
<p>The sorter has bins labelled at different levels of detail: “SW” for a whole region, “SW1” for a district, “SW1A 1AA” for one street.
A parcel for SW1A 1AA could go in all three, but it goes in the <strong>most detailed bin that fits</strong>: that is longest-prefix match.
A big “everything else” bin at the end goes to the national hub: the <strong>default route</strong>.</p>
<p>Bins come from different places. Some exist because a van is parked at that door today (<strong>connected</strong>: van leaves, bin
goes). Some were set up by the manager (<strong>static</strong>). Others are learned from phone calls with nearby depots (<strong>OSPF</strong>) or
other companies (<strong>BGP</strong>). If two sources offer the same bin, the sorter believes the source it trusts more.</p>''',
                    L.format('3.1') + ' (postcode analogy written for this rung); ' + RT,
                    [check('In the depot story, two sources both offer the same “SW1” bin. How does a Cisco router choose between them?',
                           'Lower administrative distance first, then lower metric', ['Whichever route it learned most recently',
                            'The dynamic one, because it adapts to failures'],
                           'Same prefix means the router prefers the more trusted source (connected 0, static 1, OSPF 110), then '
                           'the better metric. Being dynamic or recent does not win on its own.', mc=[AD, AD])]),
            visual(svg(560, 150, 'Longest-prefix match: 10.20.30.9 matches 10.0.0.0/8, 10.20.0.0/16 and 10.20.30.0/24; the /24 wins',
                       text(280, 18, 'Destination 10.20.30.9', 13, bold=True)
                       + box(20, 35, 160, 46, '10.0.0.0/8', 'matches 8 bits') + box(200, 35, 160, 46, '10.20.0.0/16', 'matches 16 bits')
                       + box(380, 35, 160, 46, '10.20.30.0/24', 'matches 24 bits: WINS') + box(380, 95, 160, 40, '0.0.0.0/0', 'default: only if none match'))
                   + '''<ol class="ladder-trace"><li>Packet arrives for 10.20.30.9.</li>
<li>The router lists every route whose prefix contains that address: /8, /16 and /24 (and the default /0).</li>
<li>It picks the longest prefix: the /24.</li>
<li>If two sources gave the same /24, it would pick the lower administrative distance, then the lower metric.</li>
<li>It sends the packet to that route’s next hop or exit interface.</li>
<li>Stars (* * *) at one traceroute hop with later hops answering just mean that router does not reply to probes.</li></ol>''',
                   L.format('3.1') + '; ' + RT,
                   [check('A traceroute shows * * * at hop 4, but hops 5 to 9 answer and the destination replies. What does hop 4 show?',
                          'That router does not answer probes but forwards', ['The path is broken at hop 4 and must be escalated', 'The destination host is down or firewalled'],
                          'Later hops answering proves packets passed hop 4; it just does not send time-exceeded replies. Only a '
                          'trace that stops for good shows a break.', mc=[STARS, STARS])]),
            tryit('<p>Read the routing table on the lab router and say which route each test address will use.</p>', L.format('3.1') + '; RFC 1812',
                  [check('What do VRRP and HSRP give hosts?', 'A shared virtual gateway that survives a router failure',
                         ['More bandwidth by bonding two uplinks together', 'Loop prevention between two access switches'],
                         'First-hop redundancy lets two routers share a virtual gateway IP so the standby takes over. Bonding '
                         'links is aggregation, and loop prevention is Spanning Tree.', mc=[FHRP, FHRP])],
                  widget=reveal('Routes: 10.0.0.0/8 via A, 10.20.0.0/16 via B, 0.0.0.0/0 via ISP. Where do 10.20.7.1, 10.9.9.9 and 8.8.8.8 go?',
                                '10.20.7.1 → B (/16 is longest); 10.9.9.9 → A (/8); 8.8.8.8 → ISP (only the default matches).'),
                  lab={'id': 'rtr-default-route', 'note': 'Add a default route and verify with show ip route which route a packet uses.'})),
        **_filler(_STD5 + ['network-operations-depth'], 'A short summary (routers connect networks; the default route sends unknowns upstream) of the core section.'),
    },
    '3.2': {
        'core-content': section(
            'Core content', 'NO-3.2',
            [check('Your edge router’s WAN interface is up but cannot ping the provider gateway. What do you do first?',
                   'Prove your side to the demarc, then ticket with that evidence', ['Open the ISP ticket at once and wait for their reply',
                    'Swap the edge router for a spare and see if it helps'],
                   'The lesson says to check your interface errors, addressing and cabling up to the demarc first. A bare ticket '
                   'wastes time, and swapping hardware skips the evidence.', mc=[DEM, THIN])],
            plain('''<p>A WAN joins your site to the Internet or to other sites.</p>
<ul><li><strong>Fibre</strong> is fast both ways. <strong>Cable</strong> is fast down, slower up. <strong>DSL</strong> slows with distance.</li>
<li><strong>5G or fixed wireless</strong> is quick to set up and a good backup. <strong>Satellite</strong> reaches remote places but adds delay.</li>
<li>The <strong>demarc</strong> is where the provider’s part ends.</li>
<li>To join sites: a private line, <strong>MPLS</strong>, an <strong>IPsec VPN</strong> over the Internet, or <strong>SD-WAN</strong>, which picks the best link per app.</li></ul>
<p>Before you call the ISP, check your side and write down the circuit ID, the times, and your tests.</p>''',
                  L.format('3.2') + '; ' + WAN,
                  [check('Why is geostationary satellite latency high?', 'The signal travels about 36,000 km up and back',
                         ['Satellites have very little bandwidth to share', 'Satellite links always use slow encryption'],
                         'GEO satellites orbit far above the equator, so distance alone adds hundreds of milliseconds per round trip. '
                         'Bandwidth and encryption do not explain that delay.', mc=[SAT, SAT])]),
            analogy('''<p>Think of renting a flat.</p>
<p>The landlord is responsible up to your front door: the <strong>demarc</strong>. Inside, the wiring and the lamps are yours. If the lights
fail, you check your own fuses and bulbs first, then call the landlord with the facts: “power went at 08:10, the neighbours have it too,
I reset the breaker”. That call gets fixed; “nothing works” does not.</p>
<p>Joining two flats is like choosing transport between them: a private car (a dedicated line), a taxi firm with priority lanes (MPLS),
a sealed van on public roads (IPsec VPN), or an app that picks the fastest route each trip from car, bus or bike (SD-WAN).</p>''',
                    L.format('3.2') + ' (rental analogy written for this rung); ' + WAN,
                    [check('In the transport picture, which option matches “an app that picks the fastest route each trip”?',
                           'SD-WAN choosing a link per application', ['MPLS with its fixed traffic classes', 'A single IPsec tunnel over one link'],
                           'SD-WAN steers each application across several links by measured link health. MPLS is one provider network, '
                           'and a single tunnel has only one path.', mc=[LANW, LANW])]),
            visual('''<ol class="ladder-trace"><li><strong>Scope</strong>: total outage or intermittent? One site or many? Note the start time.</li>
<li><strong>Your edge</strong>: WAN interface status and errors, and light levels on fibre.</li>
<li><strong>Your addressing</strong>: static or DHCP, as the ISP requires; correct gateway.</li>
<li><strong>To the demarc</strong>: patch cord swapped, CPE power-cycled, no recent changes.</li>
<li><strong>Tests</strong>: ping and traceroute from the edge to the provider gateway and beyond.</li>
<li><strong>Ticket</strong>: circuit ID, site address, start time, and every result above, including what you ruled out.</li></ol>''',
                   L.format('3.2'),
                   [check('Which item from the trace makes an ISP ticket actionable for the provider?', 'The circuit ID with the tests you ran',
                          ['The user’s description that “the internet is slow”', 'The make and model of the office PCs'],
                          'The circuit ID tells the provider which line, and your test results show where it breaks. User adjectives '
                          'and PC models do not locate a WAN fault.', mc=[THIN, THIN])]),
            tryit('<p>Sort the WAN facts by access type.</p>', L.format('3.2') + '; ' + WAN,
                  [check('What does SD-WAN add over a single site-to-site VPN tunnel?', 'Per-app path choice across several links',
                         ['Encryption, which a VPN tunnel does not have', 'A provider-run private network with SLAs'],
                         'SD-WAN measures several transports and steers each application over the best one. IPsec already encrypts, '
                         'and a provider-run private WAN describes MPLS.', mc=[LANW, LANW])],
                  widget=sort('Which access type?',
                              {'Fibre Ethernet': ['Symmetric, low latency', 'Watch light levels and construction cuts'],
                               'Cable / DSL': ['Fast download, slower upload', 'Speed falls with distance from the exchange'],
                               '5G / satellite': ['Quick to deploy as a backup', 'GEO adds hundreds of ms of delay']},
                              'Notice which ones make good backups.'))),
        **_filler(_STD5, 'A short summary (demarc ownership, circuit IDs and evidence for the ISP) of the core section.'),
        'cloud-networking-and-modern-network-environments': section(
            'Cloud networking and modern network environments', 'NO-3.2',
            [check('What lets instances in a private subnet download updates without being reachable from the internet?',
                   'A NAT gateway', ['An internet gateway on the private subnet', 'A security group that allows all inbound traffic'],
                   'A NAT gateway allows outbound connections only. An internet gateway route would make the subnet public, and '
                   'allowing all inbound traffic is the opposite of the goal.', mc=[CB, CB])],
            plain('''<p>In the cloud you build networks in software.</p>
<ul><li>A <strong>VPC</strong> is your own private network in the cloud, split into subnets.</li>
<li>An <strong>internet gateway</strong> lets a public subnet reach and be reached from the Internet.</li>
<li>A <strong>NAT gateway</strong> lets a private subnet go out, but nothing can come in.</li>
<li><strong>Security groups</strong> filter each server. <strong>Network ACLs</strong> filter each subnet.</li>
<li>Your office joins by VPN or a private direct link.</li></ul>
<p>Newer ideas: <strong>SD-WAN</strong> picks links by app. <strong>VXLAN</strong> stretches layer-2 networks over routed ones. <strong>Zero trust</strong> checks every request. <strong>Infrastructure as code</strong> keeps configs in version control.</p>''',
                  L.format('3.2') + '; ' + CLOUD,
                  [check('Which control filters traffic for one instance rather than a whole subnet?', 'A security group',
                         ['A network ACL (security list)', 'The internet gateway'],
                         'Security groups attach to instances; network ACLs apply at the subnet boundary. An internet gateway routes '
                         'traffic and does not filter it.', mc=[CB, CB])]),
            analogy('''<p>Think of a shopping centre.</p>
<p>The centre is the <strong>VPC</strong>. Shops on the high street side face the public road: the <strong>public subnet</strong>, with the main
entrance as the <strong>internet gateway</strong>. Stockrooms at the back are the <strong>private subnet</strong>: staff can leave by a one-way
exit door to fetch supplies (the <strong>NAT gateway</strong>) but no customer can walk in that way. Each shop has its own door guard
(<strong>security group</strong>) and each corridor has a barrier (<strong>network ACL</strong>). Head office uses a private service road
(VPN or direct connect).</p>
<p>Zero trust is a centre where every door checks your badge each time, even if you are already inside.</p>''',
                    L.format('3.2') + ' (shopping-centre analogy written for this rung); ' + CLOUD,
                    [check('In the shopping-centre story, what is “zero trust”?', 'Every door checks your badge every time',
                           ['Staff inside the centre are trusted everywhere', 'Only the main entrance checks badges'],
                           'Zero trust removes implicit trust from location, so each request is authenticated and authorised '
                           '(NIST SP 800-207). Trusting anyone already inside is the old perimeter model.', mc=['MC-L-NO3-PERIMETER-TRUST', 'MC-L-NO3-PERIMETER-TRUST'])]),
            visual(svg(560, 120, 'Cloud VPC: internet, internet gateway, public subnet with web server and NAT gateway, private subnet with app and database, on-premises link',
                       box(5, 30, 80, 50, 'Internet') + box(100, 30, 90, 50, 'Internet', 'gateway') + box(205, 30, 115, 50, 'Public subnet', 'web, NAT gw')
                       + box(335, 30, 115, 50, 'Private subnet', 'app, database') + box(465, 30, 90, 50, 'On-prem', 'VPN / direct')
                       + arrow(85, 55, 100, 55) + arrow(190, 55, 205, 55) + arrow(335, 55, 320, 55) + arrow(465, 55, 450, 55)
                       + text(280, 105, 'private subnet reaches out only via the NAT gateway'))
                   + '''<ol class="ladder-trace"><li>Web server in the public subnet; its route goes to the internet gateway.</li>
<li>Its security group allows only TCP 443 inbound.</li>
<li>Database in the private subnet; its security group allows the database port only from the web tier’s group.</li>
<li>The private subnet’s default route points at the NAT gateway: patches out, nothing in.</li>
<li>Admins come in over the site-to-site VPN, never through admin ports open to the internet.</li></ol>''',
                   L.format('3.2') + '; ' + CLOUD,
                   [check('Why does VXLAN scale further than VLANs?', 'Its 24-bit ID gives about 16 million segments',
                          ['It encrypts each frame so segments cannot overlap', 'It replaces IP routing with switching'],
                          'VXLAN’s 24-bit network identifier allows about 16 million segments versus 4,094 usable VLAN IDs. It does '
                          'not encrypt, and it runs over a routed IP fabric (UDP 4789).', mc=[VX, VX])]),
            tryit('<p>Sort each cloud building block by what it does.</p>', L.format('3.2') + '; ' + CLOUD,
                  [check('A new shop’s SD-WAN box downloads its configuration when staff plug it in. What is that called?',
                         'Zero-touch provisioning', ['Infrastructure drift', 'Transport-agnostic routing'],
                         'Zero-touch provisioning means the device calls home and pulls central policy. Drift is configuration changing '
                         'from the standard, and transport agnostic means using any link type.', mc=[LANW, LANW])],
                  widget=sort('What does it do?',
                              {'Lets traffic in or out': ['Internet gateway (public subnets)', 'NAT gateway (private, outbound only)'],
                               'Filters traffic': ['Security group (per instance)', 'Network ACL (per subnet)'],
                               'Connects sites or segments': ['Site-to-site VPN or direct connect', 'VXLAN over a routed fabric']},
                              'Notice that gateways route and groups or ACLs filter.'))),
    },
    '3.3': {
        'core-content': section(
            'Core content', 'NO-3.3',
            [check('An office uses 2.4 GHz channels 1, 3, 6, 9 and 11. What is wrong?', 'Channels 3 and 9 overlap their neighbours',
                   ['Nothing, five channels give more capacity', 'Channel 11 is not allowed in North America'],
                   'Only 1, 6 and 11 do not overlap in North America, so 3 and 9 interfere with both neighbours. Channel 11 is '
                   'allowed there, and more overlapping channels reduce capacity.', mc=[OVL, OVL])],
            plain('''<p>Wi-Fi has generations. Wi-Fi 6 (802.11ax) handles crowds better. Wi-Fi 6E adds the 6 GHz band. Wi-Fi 7 adds wider channels and multi-link.</p>
<ul><li><strong>2.4 GHz</strong> has only three channels that do not overlap: 1, 6 and 11 (North America).</li>
<li><strong>5 and 6 GHz</strong> have many more. Narrow channels (20 or 40 MHz) let more APs fit.</li>
<li><strong>Security</strong>: staff use WPA3-Enterprise (own login). Small sites use WPA3-Personal. Guests can use OWE. Never WEP or TKIP.</li>
<li><strong>Signal</strong>: −55 dBm is stronger than −75 dBm. SNR is signal minus noise; bigger is better.</li></ul>''',
                  L.format('3.3') + '; ' + WIFI,
                  [check('Which reading is the stronger signal?', '−55 dBm', ['−75 dBm', '−90 dBm'],
                         'RSSI in dBm is negative and closer to zero is stronger, so −55 beats −75 and −90. Reading the bigger '
                         'number as stronger flips the scale.', mc=[RSSI, RSSI])]),
            analogy('''<p>Think of conversations in a busy café.</p>
<p>Each AP is a table, and its channel is the language spoken there. In the small 2.4 GHz café there are only three languages that do not
blur together (1, 6, 11); seat neighbouring tables with the same or a blended language and everyone talks over each other. The 5 and
6 GHz cafés are much bigger, with many more languages.</p>
<p>How loud the speaker is, is <strong>RSSI</strong>; how loud the speaker is <em>compared with the background clatter</em> is <strong>SNR</strong>.
A loud voice in a noisy room still gets misheard. Security is the door: one shared door code (WPA3-Personal) or a personal badge for each
staff member (WPA3-Enterprise).</p>''',
                    L.format('3.3') + ' (café analogy written for this rung); ' + WIFI,
                    [check('In the café story, which security mode gives each staff member their own badge?', 'WPA3-Enterprise with 802.1X',
                           ['WPA3-Personal with one passphrase', 'OWE for the open guest network'],
                           'Enterprise mode authenticates each user or device through 802.1X. Personal mode shares one secret, and OWE '
                           'encrypts an open network without any login.', mc=[PSK, PSK])]),
            visual(svg(560, 110, 'Four APs along a floor on 2.4 GHz channels 1, 6, 11 and 1; the fourth reuses 1 because it is far from the first',
                       box(10, 30, 120, 50, 'AP-1', 'channel 1') + box(150, 30, 120, 50, 'AP-2', 'channel 6')
                       + box(290, 30, 120, 50, 'AP-3', 'channel 11') + box(430, 30, 120, 50, 'AP-4', 'channel 1')
                       + text(280, 100, 'neighbours never share a channel; reuse only where cells do not overlap'))
                   + '''<ol class="ladder-trace"><li>Survey: three APs audible on 2.4 GHz in the meeting room, two on channel 6.</li>
<li>Re-plan 2.4 GHz neighbours onto 1, 6 and 11 in turn.</li>
<li>5 GHz radios on 80 MHz overlap: drop to 40 MHz so neighbours get separate channels.</li>
<li>Enable band steering to move dual-band clients off 2.4 GHz.</li>
<li>Retest during a real meeting and check retries; aim for about −67 dBm and 25 dB SNR for voice.</li>
<li>Record the channel plan.</li></ol>''',
                   L.format('3.3') + '; ' + WIFI,
                   [check('A client shows signal −60 dBm and noise −80 dBm. What is the SNR?', '20 dB', ['140 dB', '−20 dB'],
                          'SNR is signal minus noise: −60 − (−80) = 20 dB. Adding the magnitudes gives 140, and subtracting the '
                          'wrong way gives a negative value.', mc=[SNR, SNR])]),
            tryit('<p>Run a Wi-Fi survey in the lab and decide whether each problem is coverage, contention or security.</p>', L.format('3.3') + '; ' + WIFI,
                  [check('Strong signal but poor throughput in a crowded hall usually points to what?', 'Contention or interference',
                         ['Weak coverage from a far-away AP', 'The wrong WPA3 password'],
                         'Strong RSSI rules out coverage, so many clients or overlapping APs sharing airtime is likely. A wrong '
                         'password would stop the connection, not slow it.', mc=[OVL, PSK])],
                  widget=sort('Coverage or contention?',
                              {'Coverage': ['−80 dBm at the far desk', 'Signal drops halfway down an aisle'],
                               'Contention / interference': ['−55 dBm but slow in a full lecture hall', 'Two neighbouring APs both on channel 6']},
                              'Notice that signal strength alone separates them.'),
                  lab={'id': 'win-wifi-survey', 'note': 'Survey the nearby networks and note channel, band and signal for each.'})),
        **_filler(_STD5, 'A short summary (channel planning, coverage and WPA3) of the core section.'),
        'wireless-channels-identifiers-antennas-and-ap-types': section(
            'Wireless channels, identifiers, antennas and AP types', 'NO-3.3',
            [check('What does a BSSID identify?', 'One AP radio, by its MAC address', ['The network name shared by every AP', 'The controller that manages the APs'],
                   'The BSSID is the MAC address of one radio. The SSID or ESSID is the network name across many APs, and the '
                   'controller has its own address.', mc=[IDS, IDS])],
            plain('''<p>Words you need for Wi-Fi design:</p>
<ul><li><strong>SSID</strong>: the network name. <strong>BSSID</strong>: one AP radio. <strong>ESSID</strong>: one name across many APs, so you can roam.</li>
<li><strong>Omni</strong> antennas send in all directions. <strong>Directional</strong> ones (patch, Yagi, dish) aim one way.</li>
<li><strong>Autonomous</strong> APs are set up one by one. <strong>Lightweight</strong> APs get their settings from a controller.</li>
<li><strong>DFS</strong>: some 5 GHz channels must move away if radar appears.</li>
<li><strong>Band steering</strong> pushes clients off 2.4 GHz.</li></ul>
<p>Use 802.1X (Enterprise) for staff and a separate guest network.</p>''',
                  L.format('3.3') + '; ' + WIFI,
                  [check('Which kind of AP is managed by a wireless LAN controller?', 'Lightweight', ['Autonomous', 'Ad hoc'],
                         'Lightweight APs take their configuration from a controller, often over CAPWAP. Autonomous APs are set up '
                         'one by one, and ad hoc is a peer-to-peer mode with no AP.', mc=[IDS, IDS])]),
            analogy('''<p>Think of lighting a warehouse.</p>
<p>A bare bulb on the ceiling lights the whole room evenly: an <strong>omnidirectional</strong> antenna. In long aisles between tall metal
racks that light gets blocked halfway down. A torch aimed along the aisle reaches the end: a <strong>directional</strong> antenna. Turning
every bulb brighter just adds glare and does not fix the shadows.</p>
<p>The lights all have the same switch label, “Warehouse”: the <strong>ESSID</strong>. Each bulb has its own serial number: the
<strong>BSSID</strong>. A building manager who sets every bulb from one panel is the <strong>controller</strong> with lightweight APs.</p>''',
                    L.format('3.3') + ' (warehouse-lighting analogy written for this rung); ' + WIFI,
                    [check('In the warehouse story, the aisles are still dark. What does the survey recommend?',
                           'Directional antennas along the aisles, then re-survey', ['Raise every AP to maximum transmit power and wait',
                            'Switch the APs from 5 GHz to 2.4 GHz only, for range'],
                           'Directional antennas put energy where the racks block omni coverage, and a re-survey proves it. More power '
                           'adds contention and does not fix the shadows.', mc=[PWR, PWR])]),
            visual('''<ol class="ladder-trace"><li>Find the problem area with a survey: weak signal halfway down each aisle.</li>
<li>Note the cause: metal racks absorb and reflect the signal from ceiling omni antennas.</li>
<li>Choose antennas: directional (patch or Yagi) aimed along each aisle.</li>
<li>Plan channels: 2.4 GHz neighbours on 1, 6, 11; 5 GHz on non-DFS or DFS channels as the site allows.</li>
<li>Configure once on the controller so all lightweight APs match.</li>
<li>Re-survey and record the channel plan and antenna types.</li></ol>''',
                   L.format('3.3') + '; ' + WIFI,
                   [check('What must a 5 GHz AP do on a DFS channel when it detects radar?', 'Move off that channel',
                          ['Raise its transmit power to drown out the radar', 'Switch every client to WEP'],
                          'DFS (802.11h) requires the AP to vacate a channel where radar is detected. Raising power breaks the rule, '
                          'and WEP is a broken security mode unrelated to radar.', mc=[PWR, PSK])]),
            tryit('<p>Sort the identifiers and hardware terms.</p>', L.format('3.3') + '; ' + WIFI,
                  [check('Which Wi-Fi mode lets APs relay traffic to each other wirelessly?', 'Mesh', ['Infrastructure', 'Ad hoc'],
                         'In mesh, APs forward traffic between themselves over the air. Infrastructure clients talk through an AP to '
                         'the wired network, and ad hoc devices talk directly with no AP.', mc=[IDS, IDS])],
                  widget=sort('Identifier or hardware?',
                              {'Identifier': ['SSID: the network name', 'BSSID: one radio’s MAC', 'ESSID: one name across many APs'],
                               'Hardware / management': ['Omni antenna on a ceiling AP', 'Yagi antenna for a long link', 'Lightweight AP on a controller']},
                              'Notice that BSSID and ESSID differ in scope: one radio versus a whole network.'),
                  lab={'id': 'w11-wlan', 'note': 'Read the SSID, BSSID, channel and band of the connected network with netsh wlan show interfaces.'})),
    },
    '3.4': {
        'the-scenario': skip('The scenario', 'activity', 'The capstone ticket the student works; it sets up practice, not a concept.'),
        'your-turn-scaffolded-checklist': skip('Your turn — scaffolded checklist', 'activity', 'The checklist the student fills in during the capstone drill.'),
        'common-beginner-mistakes': skip('Common beginner mistakes', 'reference', 'Short list of capstone pitfalls; the wireless ideas behind them are laddered in 3.3.'),
        'check-your-understanding': skip('Check your understanding', 'activity', 'A self-check prompt for the capstone; it is practice, not an explanation.'),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '3.1': {'core-content': '2c48e4b4633b'},
    '3.2': {'core-content': '3854950ac122', 'cloud-networking-and-modern-network-environments': '320725a45bc5'},
    '3.3': {'core-content': '31629e98894d', 'wireless-channels-identifiers-antennas-and-ap-types': '2ca82e4ee57f'},
}
