"""Explanation ladder — NETOPS chapter 1 (Network Models & Addressing). Pending SME review.

Author: content branch (pass 19). Each laddered section has R1 plain, R2 analogy, R3 visual/trace and R4 try-it,
each with its own check that asks the idea in a new form. Facts are re-explanations of the lesson, checked against
the primary sources named in each rung's source.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 1

L = 'Course lesson {} (the original section), re-explained'
OSI = 'ISO/IEC 7498-1 (OSI basic reference model); RFC 1122 (Internet host requirements: link, internet, transport, application layers)'
ADDR = 'RFC 1918 (private IPv4), RFC 3927 (IPv4 link-local), RFC 6598 (shared address space), RFC 4632 (CIDR)'
V6 = 'RFC 4291 (IPv6 addressing architecture), RFC 4193 (unique local addresses), RFC 4862 (SLAAC)'
TCPUDP = 'RFC 9293 (TCP), RFC 768 (UDP), RFC 6335 and the IANA service name and port number registry'
JEDEC = 'JEDEC DDR4/DDR5 SDRAM standards (JESD79-4, JESD79-5); motherboard vendor memory population guides'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO1-SKIP-LAYER': {
        'obj': 'NO-1.1', 'label': 'Working on a higher layer (DNS, browser, app) while a lower layer is still failing',
        'fix': 'Prove the lowest failing layer first; nothing above it can work until it is fixed.',
        'terms': ['layer', 'apipa', 'dns', 'bottom-up'], 'source': L.format('1.1'), 'review': R},
    'MC-L-NO1-ENCAP-ORDER': {
        'obj': 'NO-1.1', 'label': 'Thinking headers are added in the wrong order, or that the receiver keeps every header',
        'fix': 'Going out, transport then network then data link wrap the data; the receiver unwraps in reverse.',
        'terms': ['encapsulation', 'header', 'segment', 'packet', 'frame'], 'source': L.format('1.1') + '; ' + OSI, 'review': R},
    'MC-L-NO1-METHOD-MISMATCH': {
        'obj': 'NO-1.1', 'label': 'Picking a troubleshooting direction that does not fit the symptom (top-down for a dead link)',
        'fix': 'Bottom-up when nothing works on one device, top-down when one app fails, divide and conquer from a ping to an IP.',
        'terms': ['bottom-up', 'top-down', 'divide and conquer'], 'source': L.format('1.1'), 'review': R},
    'MC-L-NO1-MISSING-PIECE': {
        'obj': 'NO-1.2', 'label': 'Not matching each missing host setting (address, mask, gateway, DNS) to its own symptom',
        'fix': 'No gateway: local only. No DNS: names fail. No address: nothing works. Wrong mask: some local hosts look remote.',
        'terms': ['gateway', 'dns', 'mask', 'address'], 'source': L.format('1.2'), 'review': R},
    'MC-L-NO1-RANDOM-STATIC': {
        'obj': 'NO-1.2', 'label': 'Fixing an APIPA address by typing in a random static address',
        'fix': 'APIPA means DHCP failed; find out why (link, VLAN, DHCP) instead of guessing an address that may collide.',
        'terms': ['apipa', 'static', 'dhcp', 'collision'], 'source': L.format('1.2') + '; RFC 3927', 'review': R},
    'MC-L-NO1-RAM-SIZE-ONLY': {
        'obj': 'NO-1.2', 'label': 'Thinking memory capacity is the only thing that matters when replacing or adding RAM',
        'fix': 'Generation, speed, channel population, ECC and registered/unbuffered type all have to match the board.',
        'terms': ['memory', 'ecc', 'channel', 'part number'], 'source': L.format('1.2') + '; ' + JEDEC, 'review': R},
    'MC-L-NO1-PING-PROVES-PORT': {
        'obj': 'NO-1.3', 'label': 'Thinking a successful ping proves a service port is open',
        'fix': 'Ping uses ICMP; test the service by connecting to its TCP or UDP port.',
        'terms': ['ping', 'icmp', 'port', 'test-netconnection'], 'source': L.format('1.3') + '; ' + TCPUDP, 'review': R},
}

LAYER, ROUTER, NAMEFAIL, ARP = 'MC-C-NO1-OSI-LAYER', 'MC-NO1-ROUTER-REWRITES-IP', 'MC-NO1-NAME-FAIL-LOW-LAYER', 'MC-R3-NO1-ARP'
ENC, METH = 'MC-L-NO1-ENCAP-ORDER', 'MC-L-NO1-METHOD-MISMATCH'
HOSTS, BLOCK, V6T, PRIV, MASK = 'MC-NO1-HOSTS-NO-SUBTRACT', 'MC-NO1-WRONG-BLOCK', 'MC-NO1-IPV6-TYPES', 'MC-NO1-PRIVATE-RANGES', 'MC-NO1-MASK-ONLINK'
SPECIAL, MISS, RSTATIC, RAMSZ = 'MC-C-NO1-SPECIAL-ADDR', 'MC-L-NO1-MISSING-PIECE', 'MC-L-NO1-RANDOM-STATIC', 'MC-L-NO1-RAM-SIZE-ONLY'
PORT, UDPP, TU, HS, PINGP = 'MC-NO1-PORT-MIXUP', 'MC-NO1-UDP-PROPERTIES', 'MC-C-NO1-TCP-UDP', 'MC-R3-NO1-HANDSHAKE', 'MC-L-NO1-PING-PROVES-PORT'

_ACT = 'A practice drill (write a ticket timeline and a status sentence); it applies the lesson rather than explaining a concept.'
_STD = 'A two-line list of work-habit reminders (record negative results; no untracked parallel changes) repeated in every lesson.'
_PRA = 'A self-study instruction to build a 5–9 step checklist; it is an exercise, not an explanation.'
_BEY = 'A study-skills prompt (write your own scenario, explain to a non-technical user); an exercise, not a concept.'

LESSONS = {
    '1.1': {
        'core-content': section(
            'Core content', 'NO-1.1',
            [check('A laptop reaches 8.8.8.8 by ping but cannot open any website by name. Which layers has the ping already proven on that path?',
                   'Layers 1 to 3', ['Only layer 1, because ping tests the cable', 'Layers 1 to 7, because a reply means everything works'],
                   'A ping to a remote IP needs a working link, frames and IP routing, so layers 1-3 are proven. It does '
                   'not test names or applications, so it cannot prove layer 7.', mc=[LAYER, NAMEFAIL])],
            plain('''<p>Networks are easier to fix when you split them into layers.</p>
<ul><li><strong>Layer 1</strong> is the signal: cable, fibre or radio.</li>
<li><strong>Layer 2</strong> moves frames between devices on the same local network, using MAC addresses. Switches live here.</li>
<li><strong>Layer 3</strong> moves packets between networks, using IP addresses. Routers live here.</li>
<li><strong>Layer 4</strong> picks the program on the host, using port numbers (TCP or UDP).</li>
<li><strong>Layers 5–7</strong> are the application: web, mail, names (DNS), encryption.</li></ul>
<p>Sending works like nesting. Each layer adds its own label on the outside. The receiver takes the labels off again, outside first.</p>
<p>Write the layer next to every test. Then the next person knows what is already proven.</p>''',
                  L.format('1.1') + '; ' + OSI,
                  [check('Which address does a switch read to decide where a frame goes?',
                         'The destination MAC address', ['The destination IP address in the packet', 'The destination port number of the service'],
                         'Switches work at layer 2 and forward frames by MAC address. IP addresses are read by routers at '
                         'layer 3, and ports belong to layer 4 on the hosts.', mc=[LAYER, LAYER])]),
            analogy('''<p>Think of posting a gift to a friend in another city.</p>
<p>You put the gift (the <strong>data</strong>) in a box and write the friend’s flat number on it: that is the <strong>port</strong>, which
says which person in the building gets it. You put the box in a mail bag addressed to the friend’s street address: the
<strong>IP address</strong>. Each van that carries the bag gets a new label for its next depot only: the <strong>MAC address</strong>,
rewritten at every stop. The road or rail under the van is the <strong>physical layer</strong>.</p>
<p>The friend opens the bag, then the box, in reverse order. The street address never changes on the way, but every van
label does, just as a router rewrites the frame on every hop and keeps the IP addresses (NAT, in Chapter 4, is the exception).</p>
<p>Where the story stops working: real data is cut into many small boxes, not sent as one parcel.</p>''',
                    L.format('1.1') + ' (postal analogy written for this rung); ' + OSI,
                    [check('In the parcel story, which label is replaced at every depot, the way a router replaces it on every hop?',
                           'The van label for the next stop: the MAC address',
                           ['The street address on the mail bag: the IP address', 'The flat number on the box: the port number'],
                           'Routers rewrite the layer-2 frame, so source and destination MAC addresses change hop by hop. '
                           'The IP addresses stay the same end to end unless NAT is used.', mc=[ROUTER, ENC])]),
            visual(svg(560, 200, 'Encapsulation: data gets a TCP or UDP header, then an IP header, then an Ethernet header and trailer',
                       box(200, 10, 160, 34, 'Data') + text(470, 32, 'application (7–5)')
                       + box(150, 56, 50, 34, 'TCP') + box(200, 56, 160, 34, 'Data') + text(470, 78, 'segment (4): ports')
                       + box(100, 102, 50, 34, 'IP') + box(150, 102, 210, 34, 'TCP + Data') + text(470, 124, 'packet (3): IP addresses')
                       + box(40, 148, 60, 34, 'Eth') + box(100, 148, 260, 34, 'IP + TCP + Data') + box(360, 148, 46, 34, 'FCS')
                       + text(490, 170, 'frame (2): MACs'))
                   + '''<ol class="ladder-trace"><li>The browser hands its request (data) down.</li>
<li>TCP adds source and destination <strong>ports</strong>: now it is a segment.</li>
<li>IP adds source and destination <strong>IP addresses</strong>: now it is a packet.</li>
<li>Ethernet adds source and destination <strong>MAC addresses</strong> and a frame check sequence: now it is a frame.</li>
<li>The NIC sends it as <strong>bits</strong> on the wire or radio.</li>
<li>At the far end each header is checked and removed, outside first, until the web server gets the request.</li></ol>''',
                   L.format('1.1') + '; ' + OSI,
                   [check('Following the trace, what is the unit called right after IP adds its header?',
                          'A packet', ['A frame', 'A segment'],
                          'IP is layer 3 and its unit is the packet. A segment is what TCP makes one step earlier, and the '
                          'frame comes one step later when Ethernet adds MAC addresses.', mc=[ENC, ENC])]),
            tryit('''<p>Pick a troubleshooting direction before you touch anything. Sort each symptom by where you would start, then
check your sorting against the rule: nothing works on one device, start at the bottom; one app fails while others
work, start at the top; unsure, start in the middle with a ping to an IP.</p>''',
                  L.format('1.1'),
                  [check('Outlook fails but Teams and the web work on the same PC. Which method fits best?',
                         'Top-down, starting at the application', ['Bottom-up, starting at the cable', 'Replace the NIC, then test from layer 1 up'],
                         'Other applications work, so layers 1-4 on this PC are fine; start at the failing application. '
                         'Starting at the cable wastes time on layers that are already proven.', mc=[METH, METH])],
                  widget=sort('Where would you start?',
                              {'Bottom-up (cable first)': ['No link light on the only PC in the room', 'Laptop shows “No network” after a desk move'],
                               'Top-down (application first)': ['Only the payroll app fails; web and email work', 'One website shows a certificate error'],
                               'Middle (ping an IP first)': ['“The internet is slow” with no other detail', 'Some sites load, others time out']},
                              'Notice that the symptom, not habit, picks the starting layer.'),
                  lab={'id': 'win-ipconfig', 'note': 'Read the PC’s layer-2 (MAC) and layer-3 (IP, gateway) identity and label each line with its layer.'})),
        'layer-thinking-for-tickets': section(
            'Layer thinking for tickets', 'NO-1.1',
            [check('A user’s PC has an APIPA address and cannot ping the gateway. Where does the lesson say to start?',
                   'Host IP, DHCP and the local segment', ['DNS, because names are not resolving', 'The application, by reinstalling the browser'],
                   'An APIPA address means no DHCP lease, so the host’s IP configuration and local segment come first. DNS '
                   'and the browser sit above a layer that is already failing.', mc=['MC-L-NO1-SKIP-LAYER', NAMEFAIL])],
            plain('''<p>Match the symptom to a starting point.</p>
<ul><li>No link light, or it drops when the cable moves: start with the <strong>cable and port</strong>.</li>
<li>A 169.254 address, or no reply from the gateway: start with <strong>the PC’s IP settings and DHCP</strong>.</li>
<li>An IP address works but the name does not: start with <strong>DNS</strong>.</li>
<li>The name works but the page errors or the login fails: start with <strong>the application or the account</strong>.</li></ul>
<p>Do not fix a higher layer while a lower one is broken. It cannot help yet.</p>''',
                  L.format('1.1'),
                  [check('Ping to 10.1.1.20 works, but ping to fileserver.corp.local says it cannot find the host. Where do you start?',
                         'DNS name resolution', ['The cable and switch port', 'The DHCP lease on the PC'],
                         'The IP test passed, so link, lease and routing work on that path. Only the name failed, which points '
                         'at DNS, not at the cable or the lease.', mc=[NAMEFAIL, NAMEFAIL])]),
            analogy('''<p>Imagine a pizza delivery that never arrives.</p>
<p>If the scooter will not start, it does not matter whether the address is right: that is the <strong>physical</strong> problem. If the
scooter runs but the rider has no map of the town, he cannot leave the street: that is <strong>no IP or gateway</strong>. If he has a map
but the order slip has a misspelled street name, he cannot find the house: that is <strong>DNS</strong>. If he reaches the door and the
customer says “that is not what I ordered”, the trip worked and the <strong>application</strong> is wrong.</p>
<p>A good dispatcher asks how far the rider got before calling anyone. A technician does the same with layers.</p>''',
                    L.format('1.1') + ' (delivery analogy written for this rung)',
                    [check('In the delivery story, the rider reached the right door but the wrong pizza was in the box. Which kind of ticket is that?',
                           'An application or identity problem', ['A physical-layer fault on the road', 'A DNS failure with a misspelled street'],
                           'Arriving at the right door proves the path and the name worked, so what is left is the application '
                           'layer. Physical and DNS faults would have stopped the rider earlier.', mc=[LAYER, NAMEFAIL])]),
            visual('''<ol class="ladder-trace"><li><strong>Link light on, stays on when the cable is moved?</strong> No: cable, port or Wi-Fi association. Stop and fix.</li>
<li><strong>Real address (not 169.254) and the gateway answers a ping?</strong> No: IP settings, DHCP, VLAN. Stop and fix.</li>
<li><strong>A remote IP answers?</strong> No: routing or the gateway beyond the LAN.</li>
<li><strong>The name resolves (nslookup)?</strong> No: DNS.</li>
<li><strong>The page or login works?</strong> No: the application or the account.</li>
<li>Write each line in the ticket with its result, e.g. “Layer 3: ping 10.20.30.1, 4/4 replies”.</li></ol>''',
                   L.format('1.1'),
                   [check('Following the trace, the link light is on and steady but the PC has 169.254.10.4. At which step do you stop?',
                          'Step 2: IP settings, DHCP or VLAN', ['Step 1: replace the cable and reseat it at both ends', 'Step 4: flush the DNS cache and retry the name'],
                          'Step 1 passed because the link is steady. Step 2 fails on the APIPA address, so DHCP and VLAN come next; '
                          'DNS work at step 4 cannot help yet.', mc=['MC-L-NO1-SKIP-LAYER', 'MC-L-NO1-SKIP-LAYER'])]),
            tryit('<p>Put these first tests in the order the trace uses, from the lowest layer up. Then say what a failure at each step would mean.</p>',
                  L.format('1.1'),
                  [check('Why is reinstalling the browser the wrong first move for a DHCP failure?',
                         'The PC has no lease, so no app can reach the network', ['The browser must be updated before DHCP can work',
                          'Reinstalling the browser resets the network adapter'],
                         'A DHCP failure is below the application, so the browser is not the cause. Reinstalling it neither '
                         'renews a lease nor resets the adapter.', mc=['MC-L-NO1-SKIP-LAYER', None])],
                  widget=order('Order the first tests', ['Check the link light and cable', 'Read ipconfig: real address and gateway',
                                                         'Ping the gateway, then a remote IP', 'nslookup the name', 'Open the page and sign in'],
                               'Each step only makes sense once the one before it passed.'),
                  lab={'id': 'win-dns-break', 'note': 'Prove layers 1–3 with ping, then show that only the name path fails.'})),
    },
    '1.2': {
        'core-content': section(
            'Core content', 'NO-1.2',
            [check('A host is 10.4.4.200/27. What is the broadcast address of its subnet?',
                   '10.4.4.223', ['10.4.4.255', '10.4.4.207'],
                   'A /27 block is 32 addresses, so blocks start at .192 and .224; .200 is in .192–.223 and the last address, '
                   '.223, is the broadcast. .255 would be the answer for a /24.', mc=[BLOCK, BLOCK])],
            plain('''<p>An IPv4 address has two parts. The <strong>prefix</strong> (like /24) says how many bits name the network. The rest
names the host.</p>
<ul><li>A shorter prefix means a bigger network. /24 has 256 addresses. /26 has 64. /30 has 4.</li>
<li>The first address is the network’s own name. The last is the broadcast. Hosts get the ones in between.</li>
<li>So usable hosts = addresses minus 2. A /28 has 16 addresses and 14 hosts.</li></ul>
<p>Some ranges are special. 10.x, 172.16–31.x and 192.168.x are private. 169.254.x means the PC gave itself an address because DHCP
did not answer. 127.0.0.1 is the PC itself.</p>
<p>IPv6 addresses are longer and written in hex. A LAN is a /64. An address starting fe80 works only on the local link.</p>''',
                  L.format('1.2') + '; ' + ADDR + '; ' + V6,
                  [check('How many hosts can use a /29 subnet?', '6', ['8', '7'],
                         'A /29 has 8 addresses; the first is the network address and the last is the broadcast, leaving 6 '
                         'for hosts. Counting all 8 forgets to subtract those two.', mc=[HOSTS, HOSTS])]),
            analogy('''<p>Think of a street of houses.</p>
<p>The prefix is how long the street is. A /26 street has 64 plots, numbered in blocks: plots .0–.63, then .64–.127, and so on.
The first plot on each street holds the street sign (the <strong>network address</strong>) and the last holds the community notice
board that everyone reads (the <strong>broadcast</strong>). People can live only on the plots in between.</p>
<p>Private ranges are like gated estates: the same house numbers exist in many towns, so the postman outside will not deliver there
without the gate (NAT) relabelling the post. A 169.254 address is someone who could not get a key from the estate office (DHCP)
and pitched a tent on the verge.</p>
<p>Where the story stops working: real blocks always start at multiples of the block size, which streets do not.</p>''',
                    L.format('1.2') + ' (street analogy written for this rung); ' + ADDR,
                    [check('In the street picture, someone “pitched a tent on the verge”. What would ipconfig show?',
                           'A 169.254.x.x address', ['A 10.x.x.x address from the private estate', 'A 100.64.x.x carrier-grade NAT address'],
                           '169.254.0.0/16 is link-local (APIPA): the host gave itself an address because DHCP did not answer. '
                           '10.x is a normal private lease and 100.64.x is ISP shared space.', mc=[PRIV, SPECIAL])]),
            visual(svg(560, 120, 'A /24 split into four /26 blocks: .0 to .63, .64 to .127, .128 to .191, .192 to .255; .77 falls in the .64 block',
                       box(10, 30, 130, 50, '.0 – .63', 'block 1') + box(145, 30, 130, 50, '.64 – .127', 'holds .77')
                       + box(280, 30, 130, 50, '.128 – .191', 'block 3') + box(415, 30, 130, 50, '.192 – .255', 'block 4')
                       + text(280, 18, '192.168.10.0/24 cut into /26 blocks of 64') + text(210, 104, 'network .64 · hosts .65–.126 · broadcast .127'))
                   + '''<ol class="ladder-trace"><li>Prefix to block size: /26 leaves 6 host bits, 2<sup>6</sup> = 64 addresses.</li>
<li>List the block starts: .0, .64, .128, .192.</li>
<li>Find the block that holds the host: .77 is between .64 and .127.</li>
<li>Network = block start (.64). Broadcast = next start minus 1 (.127).</li>
<li>Usable hosts = .65 to .126, which is 64 − 2 = 62.</li></ol>''',
                   L.format('1.2') + '; RFC 4632',
                   [check('Using the same steps, what is the network address of 172.16.5.130/25?',
                          '172.16.5.128', ['172.16.5.0', '172.16.5.129'],
                          'A /25 is a block of 128, so blocks start at .0 and .128; .130 is in the .128 block, whose first address '
                          'is the network. .129 is the first usable host, not the network address.', mc=[BLOCK, HOSTS])]),
            tryit('<p>Work two subnets on the workbench before you look at the answer: 10.0.0.50/28 and 192.168.1.200/26. For each, write the block size, network, broadcast and usable range.</p>',
                  L.format('1.2') + '; RFC 4632',
                  [check('Is 192.168.11.50 inside 192.168.10.0/23?', 'Yes, a /23 covers .10.0 to .11.255', ['No, it only covers 192.168.10.0 to .10.255', 'No, a /23 is smaller than a /24'],
                         'A /23 has 512 addresses, two /24s, so 192.168.10.0/23 runs from 10.0 to 11.255. A shorter prefix is a '
                         'bigger network, not a smaller one.', mc=[BLOCK, BLOCK])],
                  widget=reveal('192.168.1.200/26: block size, network, broadcast, hosts?',
                                'Block 64; blocks start .0/.64/.128/.192, so network 192.168.1.192, broadcast .255, hosts .193–.254 (62).'),
                  lab={'id': 'net-subnet', 'note': 'Use the subnetting workbench to check your network, broadcast and host range.'})),
        'core-concepts': same_as('core-content', 'Core concepts',
                                 'A short summary (host config, APIPA and missing gateway) of the addressing ideas laddered in the core section.'),
        'incident-application': skip('Incident application', 'activity', _ACT),
        'standard-of-work': skip('Standard of work', 'reference', _STD),
        'practice-standard-for-this-lesson': skip('Practice standard for this lesson', 'activity', _PRA),
        'memory-as-a-system-not-a-stick': section(
            'Memory as a system, not a stick', 'NO-1.2',
            [check('A workstation needs a replacement memory module. Which record lets you order the right one?',
                   'The exact kit part number in the asset record', ['“8 GB RAM, two sticks” written in the asset record', 'The PC’s IP address and hostname from the ticket'],
                   'Capacity alone does not say generation, speed, ECC or registered type, so the lesson asks for the exact '
                   'part number. The IP address says nothing about memory.', mc=[RAMSZ, None])],
            plain('''<p>Memory is more than a size in GB.</p>
<ul><li>The <strong>generation</strong> (such as DDR4 or DDR5) must match the board.</li>
<li><strong>Speed</strong> and how the slots are filled (<strong>channels</strong>) change performance.</li>
<li>Server and workstation boards may need <strong>ECC</strong> or <strong>registered</strong> modules.</li>
<li>One module may work but run slower. A mixed set may not start, or may crash.</li></ul>
<p>To test a fault, reseat the modules, try a known-good one, and test one slot at a time. Write down the exact part number.</p>''',
                  L.format('1.2') + '; ' + JEDEC,
                  [check('A PC will not start after a new module was added. What is the lesson’s first kind of test?',
                         'Reseat, then try a known-good module one slot at a time', ['Buy a larger module of any type and fit it instead',
                          'Replace the motherboard straight away to be safe'],
                         'Reseating and testing known-good modules in single slots isolates a bad module or slot cheaply. Buying '
                         'bigger memory ignores compatibility, and a board swap skips isolation.', mc=[RAMSZ, None])]),
            analogy('''<p>Think of memory modules as rowers in a team boat.</p>
<p>One strong rower can move the boat, but slowly: that is one module in a board built for two channels. Rowers must also fit the
boat’s seats and rhythm: a DDR5 module will not even fit a DDR4 seat, and rowers pulling at different speeds make the boat lurch,
which is the instability mixed kits cause. Some boats, like server boards, only take a special kind of rower (ECC or registered).</p>
<p>When the boat will not move, the coach swaps one rower at a time to find the problem, which is what testing slots one by one does.</p>''',
                    L.format('1.2') + ' (rowing analogy written for this rung); ' + JEDEC,
                    [check('In the rowing picture, “one strong rower in a two-seat boat” means what?',
                           'One module on a dual-channel board: it works but runs slower',
                           ['A failed module that stops the PC from starting at all', 'An ECC module fitted to a desktop board by mistake'],
                           'The boat still moves, so the PC still works; it just loses dual-channel speed. A failed module would '
                           'stop it, and ECC is a different compatibility point.', mc=[RAMSZ, None])]),
            visual('''<ol class="ladder-trace"><li>Read the board’s memory spec: generation, maximum speed, ECC or not, registered or unbuffered.</li>
<li>Read the installed modules’ labels and part numbers.</li>
<li>Check the slot plan in the manual: which slots make a channel pair.</li>
<li>For a no-POST or random crash: reseat all modules.</li>
<li>Still failing: one known-good module in the first slot, then move it slot by slot.</li>
<li>Record the exact part numbers in the asset record.</li></ol>''',
                   L.format('1.2') + '; ' + JEDEC,
                   [check('At step 5, the known-good module works in every slot but the original module fails in all of them. What does that show?',
                          'The original module is faulty', ['One of the slots is faulty', 'The board needs ECC memory'],
                          'The good module passing in every slot clears the slots, and the original failing everywhere isolates it. '
                          'A bad slot would fail with the good module too.', mc=[RAMSZ, None])]),
            tryit('<p>Sort these facts into what must match the board and what only changes performance.</p>',
                  L.format('1.2') + '; ' + JEDEC,
                  [check('Which detail must match the board for a module to work at all?', 'Its generation, such as DDR5',
                         ['Its colour of heat spreader', 'Its capacity being the same as the old module'],
                         'Generations are keyed differently and are not interchangeable. Heat-spreader colour is cosmetic, and '
                         'capacity can usually differ.', mc=[RAMSZ, RAMSZ])],
                  widget=sort('Must match, or affects performance?',
                              {'Must match the board': ['Generation (DDR4 vs DDR5)', 'ECC or registered when the board requires it'],
                               'Affects performance': ['Filling both channels', 'Module speed within the board’s range']},
                              'Notice that a size in GB appears in neither list on its own.'))),
        'client-addressing-in-the-real-world': section(
            'Client addressing in the real world', 'NO-1.2',
            [check('A PC can print to a local printer but cannot reach any website, by name or by IP. Which setting is most likely missing?',
                   'The default gateway', ['The DNS server address', 'The subnet mask'],
                   'Local traffic works, so address and mask are usable; nothing leaves the subnet, which is the gateway’s job. '
                   'A missing DNS server would still let websites load by IP.', mc=[MISS, MISS])],
            plain('''<p>A PC needs four settings to work normally on IPv4.</p>
<ul><li><strong>Address</strong>: who it is. Without one, nothing works.</li>
<li><strong>Mask</strong>: which other addresses are local.</li>
<li><strong>Gateway</strong>: the way off the local network. Without it, only local things work.</li>
<li><strong>DNS</strong>: turns names into addresses. Without it, names fail but IP addresses work.</li></ul>
<p>Private ranges are normal inside a company. A 169.254 address means DHCP failed. Do not type a random address to “fix” it. Find out why DHCP failed.</p>''',
                  L.format('1.2') + '; ' + ADDR,
                  [check('Which symptom matches a missing DNS server, with everything else correct?',
                         'Websites open by IP address but not by name', ['Only devices on the same subnet answer', 'Nothing answers at all, even the gateway'],
                         'DNS only turns names into addresses, so IP access still works. Local-only access points to the gateway, '
                         'and no replies at all to the address or link.', mc=[MISS, MISS])]),
            analogy('''<p>Think of a new employee’s first day.</p>
<p>The <strong>address</strong> is their desk number: without it, nobody can find them. The <strong>mask</strong> is the floor plan that says
which desks are on their own floor. The <strong>gateway</strong> is the lift: without it they can talk to their floor but cannot reach
any other. <strong>DNS</strong> is the staff directory: without it they can still visit room 4.12 if they know the number, but “the
finance office” means nothing.</p>
<p>A 169.254 address is like sitting at a desk you picked yourself because reception was closed. Picking someone else’s desk
(a random static address) just causes a collision; the fix is to find out why reception (DHCP) did not answer.</p>''',
                    L.format('1.2') + ' (first-day analogy written for this rung); RFC 3927',
                    [check('In the first-day story, the employee can reach “room 4.12” but not “the finance office”. Which setting is missing?',
                           'DNS', ['The gateway', 'The address'],
                           'Reaching a room by number but not by name is names failing while addresses work, which is DNS. A '
                           'missing gateway would stop every other floor, number or name.', mc=[MISS, MISS])]),
            visual('''<ol class="ladder-trace"><li>Run <code>ipconfig /all</code> (Windows) or <code>ip addr</code> and <code>ip route</code> (Linux).</li>
<li>Is the address 169.254.x.x? Then DHCP failed: check link, VLAN and DHCP. Stop.</li>
<li>Is there a default gateway? If not: only local traffic can work.</li>
<li>Is the mask right for the VLAN? A wrong mask makes some local hosts look remote.</li>
<li>Are DNS servers listed? If not: names will fail while IPs work.</li>
<li>Say the next test out loud before you change anything.</li></ol>''',
                   L.format('1.2'),
                   [check('At step 2 the address is 169.254.33.8. A colleague suggests typing 10.1.1.50 in. Why does the trace stop you?',
                          'DHCP failed; a guessed static address may collide', ['APIPA addresses only need a reboot to fix themselves',
                           'A 169.254 address is a valid company lease'],
                          'APIPA means no lease, so the fix is the DHCP path (link, VLAN, server). A random static address hides '
                          'the fault and may duplicate another device’s address.', mc=[RSTATIC, PRIV])]),
            tryit('<p>Read the host settings in the lab VM and predict the user’s complaint before you test it.</p>',
                  L.format('1.2'),
                  [check('A PC has address, mask and DNS but no gateway. What will the user say?',
                         '“I can reach the printer but not the internet”', ['“Websites work when I type the IP, but not by name”', '“Nothing works at all, not even the printer”'],
                         'Without a gateway only local traffic works, so the local printer answers and the internet does not. '
                         'Names-only failure is DNS, and total failure is no address or link.', mc=[MISS, MISS])],
                  widget=reveal('A PC shows 192.168.5.40/24, gateway blank, DNS 192.168.5.10. What works and what fails?',
                                'Local hosts on 192.168.5.0/24 work (including the DNS server, so local names resolve); anything off the subnet fails.'),
                  lab={'id': 'win-ipconfig', 'note': 'Read address, mask, gateway and DNS from ipconfig /all and say which piece each symptom needs.'})),
        'beyond-the-quiz': skip('Beyond the quiz', 'activity', _BEY),
    },
    '1.3': {
        'core-content': section(
            'Core content', 'NO-1.3',
            [check('Ping to the mail server works, but Test-NetConnection to port 587 reports TcpTestSucceeded: False. What does that point to?',
                   'A firewall rule or a stopped service', ['A routing problem between the sites', 'A DNS failure for the server’s name'],
                   'The ping proves the path and the name, so routing and DNS are fine. A failed port test on a reachable host '
                   'means nothing is accepting on that port.', mc=[PINGP, NAMEFAIL])],
            plain('''<p>TCP and UDP both carry data between programs. They do it in different ways.</p>
<ul><li><strong>TCP</strong> sets up a connection first (SYN, SYN-ACK, ACK). It numbers the data, checks it arrived, and resends what was lost.</li>
<li><strong>UDP</strong> just sends. No setup, no resending. The application deals with any loss.</li></ul>
<p>Use TCP when every byte matters: web pages, email, SSH. Use UDP when speed matters more: DNS queries, DHCP, voice.</p>
<p>A <strong>port</strong> number picks the program, like 22 for SSH or 53 for DNS. Ping does not test ports. To test a service, connect to its port.</p>''',
                  L.format('1.3') + '; ' + TCPUDP,
                  [check('Which feature does UDP have at the transport layer?', 'None of setup, acknowledgement or resending',
                         ['Encryption of every datagram it sends', 'Sequence numbers that put data back in order'],
                         'UDP is connectionless and adds only ports, length and a checksum. Sequencing belongs to TCP, and '
                         'encryption comes from protocols above it, such as TLS or DTLS.', mc=[UDPP, UDPP])]),
            analogy('''<p>Compare a phone call with a radio broadcast.</p>
<p><strong>TCP</strong> is a phone call. You dial, the other person answers, you both say hello (the handshake). If a sentence is
garbled, they say “sorry, again?” and you repeat it. Every sentence is heard, in order.</p>
<p><strong>UDP</strong> is a radio presenter. They just talk. If your car goes under a bridge, the presenter does not repeat the
sentence, and that is fine for live news, where a late sentence is useless anyway, just like late voice packets.</p>
<p>The <strong>port</strong> is the extension number or the station frequency: it picks which conversation you mean on that host.</p>''',
                    L.format('1.3') + ' (phone and radio analogy written for this rung); ' + TCPUDP,
                    [check('Voice calls usually carry their audio over UDP. Which part of the radio story explains why?',
                           'A late repeat of a sentence is useless live', ['Radio is encrypted so nobody can listen in',
                            'The presenter waits for every listener to confirm'],
                           'Live audio needs low delay, and a retransmitted packet arrives too late to play. UDP does not encrypt, '
                           'and waiting for confirmations is TCP behaviour.', mc=[UDPP, TU])]),
            visual(svg(520, 210, 'TCP three-way handshake: client sends SYN, server replies SYN-ACK, client sends ACK, then data flows',
                       text(80, 20, 'Client', 13, bold=True) + text(440, 20, 'Server :443', 13, bold=True)
                       + '<line x1="80" y1="30" x2="80" y2="200" stroke="currentColor" stroke-width="2"/>'
                       + '<line x1="440" y1="30" x2="440" y2="200" stroke="currentColor" stroke-width="2"/>'
                       + arrow(80, 55, 440, 55, '1. SYN') + arrow(440, 95, 80, 95, '2. SYN-ACK') + arrow(80, 135, 440, 135, '3. ACK')
                       + arrow(80, 175, 440, 175, '4. data (numbered, acknowledged)'))
                   + '''<ol class="ladder-trace"><li>The client picks a high (ephemeral) source port and sends SYN to port 443.</li>
<li>If something listens on 443, the server replies SYN-ACK. If nothing listens, it replies RST.</li>
<li>The client sends ACK: the connection is open.</li>
<li>Data flows with sequence numbers; lost segments are resent.</li>
<li>With UDP, step 4 happens straight away with no steps 1–3 and no resends.</li></ol>''',
                   L.format('1.3') + '; RFC 9293',
                   [check('A capture shows the client’s SYN followed by RST from the server. What does that mean?',
                          'The host is up but nothing is listening on that port', ['The connection opened and then finished normally',
                           'The server is down, so no packet came back'],
                          'An RST in reply to a SYN means the host answered and refused the port. A finished connection would '
                          'show a handshake first, and a down host sends nothing.', mc=[HS, HS])]),
            tryit('<p>Sort each service by its normal transport, then test one real port in the lab.</p>',
                  L.format('1.3') + '; ' + TCPUDP,
                  [check('Which service uses UDP ports 67 and 68?', 'DHCP', ['SSH', 'SMTP submission'],
                         'DHCP uses UDP 67 (server) and 68 (client). SSH is TCP 22 and mail submission is TCP 587, both '
                         'connection-oriented.', mc=[PORT, PORT])],
                  widget=sort('TCP or UDP?', {'TCP': ['SSH (22)', 'HTTPS on HTTP/1.1 or HTTP/2 (443)', 'SMB file sharing (445)'],
                                              'UDP': ['DHCP (67/68)', 'NTP (123)', 'SNMP polling (161)']},
                              'Notice the pattern: reliability-hungry services use TCP; small, fast or live ones use UDP.'),
                  lab={'id': 'w11-powershell-net', 'note': 'Use Test-NetConnection with -Port to test a service port, then compare it with a plain ping.'})),
        'core-concepts': same_as('core-content', 'Core concepts',
                                 'A short summary (TCP reliability, UDP lightness, firewall must match protocol and port) of the core section.'),
        'incident-application': skip('Incident application', 'activity', _ACT),
        'standard-of-work': skip('Standard of work', 'reference', _STD),
        'practice-standard-for-this-lesson': skip('Practice standard for this lesson', 'activity', _PRA),
        'network-operations-depth': skip('Network operations depth', 'orientation',
                                         'A course-wide signpost that lists every later topic (subnetting, ARP, VLANs, wireless, PoE, NAT) in one paragraph; each is laddered in its own lesson.'),
        'beyond-the-quiz': skip('Beyond the quiz', 'activity', _BEY),
    },
    '1.4': {
        'the-scenario': skip('The scenario', 'activity', 'The capstone ticket the student works; it sets up practice, not a concept.'),
        'your-turn-scaffolded-checklist': skip('Your turn — scaffolded checklist', 'activity', 'The checklist the student fills in during the capstone drill.'),
        'common-beginner-mistakes': skip('Common beginner mistakes', 'reference',
                                         'Two-line list of capstone pitfalls; the layer ideas behind them are laddered in lesson 1.1.'),
        'check-your-understanding': skip('Check your understanding', 'activity', 'A self-check prompt (explain the ticket to a peer); it is practice, not an explanation.'),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '1.1': {'core-content': '1974c29db0b7', 'layer-thinking-for-tickets': 'eed1f095dd51'},
    '1.2': {'core-content': '11475a8149fc', 'memory-as-a-system-not-a-stick': '784c1675e7f7', 'client-addressing-in-the-real-world': 'be040c5e9ac0'},
    '1.3': {'core-content': '290ed663d569'},
}
