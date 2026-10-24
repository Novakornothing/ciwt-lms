"""Explanation ladder — NETOPS chapter 2 (Switching, VLANs and Cabling). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Facts follow the lesson and the primary sources named in each rung.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 2

L = 'Course lesson {} (the original section), re-explained'
BR = 'IEEE Std 802.1Q-2022 (bridging, VLAN tagging, RSTP, formerly 802.1D/802.1w)'
CAB = 'ANSI/TIA-568.2-D (balanced twisted-pair cabling, 100 m channel); IEEE Std 802.3 (1000BASE-T, 10GBASE-T, PoE clauses 33/145)'
FIB = 'ANSI/TIA-568.3-D (optical fibre cabling); IEEE Std 802.3 (10GBASE-SR/LR); SFF-8431 (SFP+)'
TOPO = 'Cisco, “Data Center Spine-and-Leaf Architecture: Design Overview” white paper; Cisco campus hierarchical design guides; CompTIA Network+ N10-009 objective 1.6'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO2-TABLE-FROM-DEST': {
        'obj': 'NO-2.1', 'label': 'Thinking a switch learns MAC addresses from the destination field rather than the source',
        'fix': 'The switch records the source MAC against the port a frame arrived on; it looks up the destination to forward.',
        'terms': ['mac table', 'source mac', 'learn'], 'source': L.format('2.1') + '; ' + BR, 'review': R},
    'MC-L-NO2-ERRDISABLE-JUST-RESET': {
        'obj': 'NO-2.1', 'label': 'Re-enabling an err-disabled port without finding what tripped it',
        'fix': 'Err-disable is a protection that worked; remove the cause (a loop or rogue switch) and re-enable under change control.',
        'terms': ['err-disabled', 'bpdu guard', 'shutdown'], 'source': L.format('2.1'), 'review': R},
    'MC-L-NO2-TOPOLOGY-MIX': {
        'obj': 'NO-2.1', 'label': 'Mixing up star, mesh, three-tier and spine-and-leaf designs or north-south with east-west traffic',
        'fix': 'Spine and leaf connects every leaf to every spine for east-west server traffic; north-south enters or leaves the data centre.',
        'terms': ['spine', 'leaf', 'east-west', 'north-south', 'collapsed core', 'mesh'], 'source': L.format('2.1') + '; ' + TOPO, 'review': R},
    'MC-L-NO2-VLAN-NO-GATEWAY': {
        'obj': 'NO-2.2', 'label': 'Expecting two VLANs on one switch to talk without a layer-3 gateway (SVI or router)',
        'fix': 'Each VLAN is its own subnet and broadcast domain; traffic between them must be routed.',
        'terms': ['vlan', 'svi', 'inter-vlan', 'router-on-a-stick'], 'source': L.format('2.2'), 'review': R},
    'MC-L-NO2-POE-BUDGET': {
        'obj': 'NO-2.3', 'label': 'Blaming devices when PoE devices reboot because the switch power budget or class is too small',
        'fix': 'Check the port’s PoE standard (af/at/bt) against the device’s draw, and the switch’s total budget.',
        'terms': ['poe', '802.3af', '802.3at', 'budget'], 'source': L.format('2.3') + '; ' + CAB, 'review': R},
    'MC-L-NO2-OPTIC-MISMATCH': {
        'obj': 'NO-2.3', 'label': 'Thinking any optic works if the connector fits, ignoring fibre type, wavelength and speed',
        'fix': 'Both transceivers must match each other and the fibre (e.g. two 10GBASE-LR on single-mode), not just plug in.',
        'terms': ['transceiver', 'sfp', 'lc', 'single-mode', 'multimode'], 'source': L.format('2.3') + '; ' + FIB, 'review': R},
}

UNK, LOOP, STPP, DEVL = 'MC-NO2-UNKNOWN-UNICAST', 'MC-NO2-LOOP-MISSED', 'MC-NO2-STP-PURPOSE', 'MC-NO2-DEVICE-LAYER'
ERR, BPG, LEARN, ERRR, TOP = 'MC-R3-NO2-ERRDISABLE', 'MC-R3-NO2-BPDUGUARD', 'MC-L-NO2-TABLE-FROM-DEST', 'MC-L-NO2-ERRDISABLE-JUST-RESET', 'MC-L-NO2-TOPOLOGY-MIX'
WVF, TAL, NAT_V, Q, GW = 'MC-NO2-WRONG-VLAN-FIX', 'MC-NO2-TRUNK-ALLOWED', 'MC-NO2-NATIVE-VLAN', 'MC-R3-NO2-8021Q', 'MC-L-NO2-VLAN-NO-GATEWAY'
CLEN, TOOL, FMODE, NEXT, POE, OPT = ('MC-NO2-COPPER-LENGTH', 'MC-NO2-WRONG-TOOL', 'MC-NO2-FIBRE-MODE', 'MC-R3-NO2-NEXT',
                                     'MC-L-NO2-POE-BUDGET', 'MC-L-NO2-OPTIC-MISMATCH')

_ACT = 'A practice drill (write a ticket timeline and a status sentence); it applies the lesson rather than explaining a concept.'
_STD = 'A two-line list of work-habit reminders (record negative results; no untracked parallel changes) repeated in every lesson.'
_PRA = 'A self-study instruction to build a 5–9 step checklist; it is an exercise, not an explanation.'
_BEY = 'A study-skills prompt (write your own scenario, explain to a non-technical user); an exercise, not a concept.'
_DEP = 'A course-wide signpost paragraph repeated in every lesson; each topic it names is laddered in its own lesson.'


def _filler(l):
    return {'incident-application': skip('Incident application', 'activity', _ACT),
            'standard-of-work': skip('Standard of work', 'reference', _STD),
            'practice-standard-for-this-lesson': skip('Practice standard for this lesson', 'activity', _PRA),
            'network-operations-depth': skip('Network operations depth', 'orientation', _DEP),
            'beyond-the-quiz': skip('Beyond the quiz', 'activity', _BEY)}


LESSONS = {
    '2.1': {
        'core-content': section(
            'Core content', 'NO-2.1',
            [check('A switch receives a frame for a MAC address that is not in its table. What does it do?',
                   'Floods it out every other port in that VLAN',
                   ['Drops it and waits for the sender to try again later', 'Sends it to the default gateway to be routed'],
                   'Unknown unicast is flooded within the VLAN, and the switch learns the destination when it replies. '
                   'Switches do not route or drop it at layer 2.', mc=[UNK, UNK])],
            plain('''<p>A switch learns where devices are, then sends frames only where they need to go.</p>
<ul><li><strong>Learn</strong>: when a frame comes in, the switch notes the sender’s MAC and the port.</li>
<li><strong>Forward</strong>: if it knows the destination MAC, it sends the frame out that one port.</li>
<li><strong>Flood</strong>: if it does not know it, or the frame is a broadcast, it sends it out every port in the VLAN.</li>
<li><strong>Age</strong>: entries it does not see for a while (often 300 seconds) are forgotten.</li></ul>
<p>If two switches are joined by two cables, broadcasts go round for ever. That is a loop. <strong>Spanning Tree</strong> stops it by turning off the spare path until it is needed.</p>
<p><strong>BPDU Guard</strong> shuts a user port if a switch is plugged into it.</p>''',
                  L.format('2.1') + '; ' + BR,
                  [check('Which field does a switch use to fill in its MAC address table?', 'The source MAC of frames arriving on a port',
                         ['The destination MAC of frames it sends out', 'The source IP address of each packet it sees'],
                         'Learning uses the source address: “this MAC lives behind this port”. The destination is only looked up '
                         'to forward, and IP addresses are not read by a layer-2 switch.', mc=[LEARN, DEVL])]),
            analogy('''<p>Think of a new receptionist in an office building.</p>
<p>On day one she does not know who sits where. When a visitor asks for Sam, she announces “Sam, visitor at reception” on every floor’s
speaker: that is <strong>flooding</strong>. When Sam calls back from floor 3, she writes down “Sam: floor 3”: she <strong>learned</strong> from
who called, not who was asked for. Next time she just phones floor 3. If Sam has not called for weeks, she rubs the note out in case
he moved: that is <strong>ageing</strong>.</p>
<p>Now imagine two intercoms wired in a ring, so every announcement plays again and again, louder each time, until nobody can work.
That is a <strong>broadcast storm</strong>, and Spanning Tree is the caretaker who unplugs the extra wire and keeps it as a spare.</p>''',
                    L.format('2.1') + ' (receptionist analogy written for this rung); ' + BR,
                    [check('In the receptionist story, what matches Spanning Tree?', 'The caretaker unplugging the spare intercom wire',
                           ['The receptionist writing down which floor Sam is on', 'Sharing callers across both intercoms for speed'],
                           'STP blocks a redundant path so there is one active path, keeping the other as standby. Writing notes '
                           'is MAC learning, and STP does not load-balance.', mc=[STPP, STPP])]),
            visual(svg(560, 150, 'Switch learns PC A on port 1 from its source MAC, floods the unknown destination, then learns PC B on port 3 from the reply',
                       box(220, 20, 120, 50, 'Switch', 'MAC table') + box(10, 95, 110, 40, 'PC A', 'port 1') + box(225, 95, 110, 40, 'PC C', 'port 2')
                       + box(440, 95, 110, 40, 'PC B', 'port 3') + arrow(65, 95, 230, 70, '') + arrow(330, 70, 495, 95, '')
                       + arrow(280, 70, 280, 95, '') + text(280, 145, '1st frame A→B is flooded to ports 2 and 3; B’s reply is sent to port 1 only'))
                   + '''<ol class="ladder-trace"><li>PC A (port 1) sends a frame to PC B. The switch records “A is on port 1”.</li>
<li>B is unknown, so the frame is flooded to ports 2 and 3. PC C ignores it; PC B keeps it.</li>
<li>PC B replies. The switch records “B is on port 3”.</li>
<li>A is known, so the reply leaves port 1 only.</li>
<li>From now on A and B talk privately until an entry ages out.</li>
<li>To find a device: <code>show mac address-table address &lt;mac&gt;</code>, then follow uplinks until you reach an access port.</li></ol>''',
                   L.format('2.1') + '; ' + BR,
                   [check('After step 3 of the trace, which ports does a new frame from A to B leave by?', 'Port 3 only',
                          ['Ports 2 and 3, the same as the first frame', 'Every port, including port 1 where it arrived'],
                          'Step 3 taught the switch that B is on port 3, so known unicast goes out that one port. Flooding was '
                          'only for the first frame, and a switch never floods back out the ingress port.', mc=[UNK, UNK])]),
            tryit('<p>On the lab switch, read the MAC table, then find which access port a given device is on.</p>',
                  L.format('2.1'),
                  [check('A user port shows err-disabled after someone plugged a small switch into the wall jack. What should you do?',
                         'Remove the cause, then re-enable it under change control', ['Re-enable the port immediately so the user can work',
                          'Turn off BPDU Guard on that port permanently'],
                         'BPDU Guard did its job by shutting the port when a switch appeared. Re-enabling without removing the '
                         'cause, or disabling the guard, invites a loop.', mc=[ERRR, BPG])],
                  widget=reveal('Floor slow, switch CPU 100%, right after a cable was patched between two wall jacks. Cause?',
                                'A layer-2 loop and broadcast storm. Find the new cable; check STP and BPDU Guard events.'),
                  lab={'id': 'sw-mac-table', 'note': 'Read the MAC address table and follow a MAC to its access port.'})),
        'core-concepts': same_as('core-content', 'Core concepts', 'A short summary (switches forward on MACs within a broadcast domain) of the core section.'),
        **_filler('2.1'),
        'topologies-architectures-and-traffic-flows': section(
            'Topologies, architectures and traffic flows', 'NO-2.1',
            [check('Server-to-server traffic inside one data centre is called what?', 'East-west traffic', ['North-south traffic', 'Hub-and-spoke traffic'],
                   'East-west flows stay inside the data centre between servers. North-south enters or leaves it, and hub and '
                   'spoke is a topology, not a flow.', mc=[TOP, TOP])],
            plain('''<p>A topology is the shape of a network.</p>
<ul><li><strong>Star</strong>: everything connects to one centre. Simple, but if the centre fails, all fail.</li>
<li><strong>Mesh</strong>: devices connect to many others. Strong, but needs lots of links.</li>
<li><strong>Point to point</strong>: one link between two places.</li>
<li><strong>Three-tier</strong>: access (users), distribution (rules and routing) and core (fast). Small sites merge the top two: a <strong>collapsed core</strong>.</li>
<li><strong>Spine and leaf</strong>: every leaf switch connects to every spine. Used in data centres.</li></ul>
<p>Traffic in and out of a data centre is <strong>north-south</strong>. Traffic between servers inside is <strong>east-west</strong>.</p>''',
                  L.format('2.1') + '; ' + TOPO,
                  [check('What does a collapsed core combine?', 'The core and distribution layers',
                         ['The access and distribution layers', 'The spine and leaf layers of a data centre'],
                         'A collapsed core merges core and distribution for smaller sites, leaving access below. Spine and leaf '
                         'is a separate two-layer data-centre design.', mc=[TOP, TOP])]),
            analogy('''<p>Compare a city’s transport.</p>
<p>A <strong>star</strong> is a town where every bus goes through one central station: easy to plan, but a fire at the station stops everything.
That is what happened to six branches when the head-office hub failed. A <strong>mesh</strong> is lots of direct roads between towns:
costly, but a closed road has a detour.</p>
<p><strong>Spine and leaf</strong> is a metro where every local line (leaf) meets every express line (spine). Any two local stops are always
local → express → local, the same number of hops wherever you start. Commuters crossing town (east-west) love it. The motorway in and
out of the city is <strong>north-south</strong>.</p>''',
                    L.format('2.1') + ' (transport analogy written for this rung); ' + TOPO,
                    [check('In the metro picture, why does spine and leaf suit server-to-server traffic?',
                           'Any two leaves are always the same two hops apart', ['Every server plugs straight into the core motorway',
                            'All traffic passes through one central station'],
                           'Each leaf links to every spine, so leaf, spine, leaf is the path for any pair, giving predictable latency. '
                           'One central station describes a star with a single point of failure.', mc=[TOP, TOP])]),
            visual(svg(560, 190, 'Three-tier stack of core, distribution and access beside spine and leaf with every leaf linked to every spine',
                       box(30, 10, 170, 40, 'Core') + box(30, 75, 170, 40, 'Distribution') + box(30, 140, 170, 40, 'Access', 'users')
                       + arrow(115, 75, 115, 50) + arrow(115, 140, 115, 115)
                       + box(300, 20, 110, 40, 'Spine 1') + box(430, 20, 110, 40, 'Spine 2')
                       + box(290, 130, 80, 40, 'Leaf 1') + box(380, 130, 80, 40, 'Leaf 2') + box(470, 130, 80, 40, 'Leaf 3')
                       + ''.join(f'<line x1="{lx}" y1="130" x2="{sx}" y2="60" stroke="currentColor" stroke-width="1.5"/>'
                                 for lx in (330, 420, 510) for sx in (355, 485)))
                   + '''<ol class="ladder-trace"><li>Requirement: twelve racks, mostly VM-to-VM and app-to-database traffic: east-west.</li>
<li>Three-tier: a flow between racks may climb to distribution or core and back, so path length varies.</li>
<li>Spine and leaf: a leaf (top-of-rack) switch in every rack, each linked to every spine.</li>
<li>Any two servers in different racks: leaf → spine → leaf, always.</li>
<li>Growth: add spines for bandwidth between racks, leaves for more server ports.</li>
<li>Decision: spine and leaf in the data centre; office floors keep a collapsed core (mostly north-south).</li></ol>''',
                   L.format('2.1') + '; ' + TOPO,
                   [check('Following the design trace, the data centre needs more bandwidth between racks. What do you add?',
                          'More spine switches', ['More leaf switches in each rack', 'A second distribution layer above the core'],
                          'Every leaf links to every spine, so extra spines add parallel paths between racks. Extra leaves add '
                          'server ports, and a distribution layer belongs to three-tier.', mc=[TOP, TOP])]),
            tryit('<p>Sort each description to the topology or flow it describes.</p>', L.format('2.1') + '; ' + TOPO,
                  [check('Six branches connect only to head office, and lose each other when its router fails. Which topology is that?',
                         'Hub and spoke (star)', ['Full mesh between all branches', 'Spine and leaf across the sites'],
                         'All branch-to-branch traffic passing through one hub is a star, whose centre is a single point of failure. '
                         'A mesh would have kept direct branch links.', mc=[TOP, TOP])],
                  widget=sort('Which design or flow?',
                              {'Spine and leaf': ['Every leaf links to every spine', 'Two hops between any two racks'],
                               'Star / hub and spoke': ['Branches only link to head office', 'Centre is a single point of failure'],
                               'Traffic flow': ['North-south: users to servers', 'East-west: VM to database']},
                              'Notice that spine and leaf is chosen for the east-west flow.'))),
    },
    '2.2': {
        'core-content': section(
            'Core content', 'NO-2.2',
            [check('A new VLAN works on the core switch but not on an access switch across a trunk. What do you check first?',
                   'That the VLAN exists there and the trunk allows it', ['That the PCs have the right DNS server set',
                    'That the access switch’s power supply is working'],
                   'A trunk only carries VLANs in its allowed list, and the VLAN must exist on the far switch. DNS and power '
                   'would affect every VLAN, not just the new one.', mc=[TAL, TAL])],
            plain('''<p>A VLAN splits one switch into separate networks.</p>
<ul><li>An <strong>access port</strong> belongs to one VLAN. PCs and printers plug in here. Their frames have no tag.</li>
<li>A <strong>trunk port</strong> carries many VLANs between switches. Each frame gets a small tag with its VLAN number (802.1Q).</li>
<li>Each VLAN is its own IP subnet. To get from one VLAN to another, traffic must go through a <strong>router</strong> or a layer-3 switch.</li></ul>
<p>A common ticket: one PC is on the wrong VLAN. Its address looks different from its neighbours’. Fix the port’s VLAN with a change ticket, then renew and test.</p>''',
                  L.format('2.2') + '; ' + BR,
                  [check('Two PCs on the same switch are in VLAN 10 and VLAN 20 and cannot ping each other. Is the switch broken?',
                         'No, VLANs need a layer-3 gateway to talk', ['Yes, ports on one switch can always talk', 'Yes, the trunk tag must be missing'],
                         'Separate VLANs are separate subnets and broadcast domains by design, so they need an SVI or router '
                         'between them. Trunk tags are not involved between two access ports.', mc=[GW, Q])]),
            analogy('''<p>Think of a hotel with several floors and one lift.</p>
<p>Each floor is a <strong>VLAN</strong>: guests on floor 3 share a corridor and hear each other’s announcements, but not floor 4’s. A room’s
door only opens onto one corridor: that is an <strong>access port</strong>. The lift carries guests for every floor, and each guest wears a
badge saying which floor they belong to: that is the <strong>trunk</strong> with its 802.1Q tag.</p>
<p>To visit a friend on another floor you must go through reception (the <strong>router</strong> or SVI). The classic ticket is a guest given a
key for the wrong floor: the lift works, the light is green, but they end up in the wrong corridor.</p>''',
                    L.format('2.2') + ' (hotel analogy written for this rung); ' + BR,
                    [check('In the hotel story, a guest’s key opens the wrong floor’s corridor. What is the network fix?',
                           'Set the right access VLAN on the switchport', ['Replace the PC’s network card with a new one', 'Add a second default gateway on the PC'],
                           'The link is fine; the port is just in the wrong VLAN, so the port assignment is the fix. A new NIC or '
                           'extra gateway does not move the PC to the right VLAN.', mc=[WVF, WVF])]),
            visual(svg(560, 130, '802.1Q tag inserted into an Ethernet frame after the source MAC, carrying a 12-bit VLAN ID',
                       box(10, 30, 90, 46, 'Dest MAC') + box(100, 30, 90, 46, 'Src MAC') + box(190, 30, 110, 46, '802.1Q tag', '4 bytes')
                       + box(300, 30, 80, 46, 'Type') + box(380, 30, 110, 46, 'Payload') + box(490, 30, 60, 46, 'FCS')
                       + text(245, 100, 'VLAN ID: 12 bits (1–4094)') + text(245, 118, 'native VLAN frames are sent untagged'))
                   + '''<ol class="ladder-trace"><li>PC on access port Gi1/0/12 (VLAN 40) sends an untagged frame.</li>
<li>The switch sends it up the trunk with an 802.1Q tag: VLAN 40.</li>
<li>The far switch reads the tag and delivers it only to VLAN 40 ports, untagged again.</li>
<li>To reach VLAN 30, the frame goes to the gateway (SVI Vlan40, 10.20.40.1), which routes it.</li>
<li>Wrong-VLAN check: user on 10.20.30.x, neighbours on 10.20.40.x; read <code>show interfaces status</code>.</li></ol>''',
                   L.format('2.2') + '; ' + BR,
                   [check('How many bits of the 802.1Q tag identify the VLAN?', '12 bits', ['8 bits', '16 bits'],
                          'The VLAN ID field is 12 bits, giving IDs 0–4095 with 1–4094 usable. The whole tag is 4 bytes, which '
                          'is where the 16-bit and 32-bit guesses come from.', mc=[Q, Q])]),
            tryit('<p>Put the wrong-VLAN ticket steps in order, then do them on the lab switch.</p>', L.format('2.2'),
                  [check('A trunk works for most VLANs, but CDP warns of a native VLAN mismatch. What is wrong?',
                         'Each end uses a different untagged VLAN', ['The trunk is missing an IP address', 'The two switches run different VTP passwords'],
                         'The native VLAN is the one sent untagged, and it must match at both ends or untagged traffic leaks '
                         'between VLANs. Trunks do not need IP addresses.', mc=[NAT_V, NAT_V])],
                  widget=order('Order the wrong-VLAN steps', ['Compare the user’s IP with a working neighbour', 'Trace the jack to the switchport',
                                                              'Read the port’s VLAN', 'Set the access VLAN under a change ticket',
                                                              'Renew the lease and ping gateway and server'],
                               'Evidence first, change second, verify last.'),
                  lab={'id': 'sw-vlan-access', 'note': 'Put a port in the right access VLAN and verify with show vlan brief.'})),
        'core-concepts': same_as('core-content', 'Core concepts', 'A short summary (access one VLAN, trunk many, wrong VLAN isolates) of the core section.'),
        **_filler('2.2'),
    },
    '2.3': {
        'core-content': section(
            'Core content', 'NO-2.3',
            [check('A 10GBASE-T link must run 85 m. Which cable category does the lesson say to use?', 'Cat 6A',
                   ['Cat 6, which reaches 100 m at 10 Gb/s', 'Cat 5e with a good patch lead'],
                   'Cat 6 supports 10GBASE-T only to about 55 m, and Cat 5e is rated for 1 Gb/s. Cat 6A supports 10GBASE-T '
                   'across the full 100 m channel.', mc=[CLEN, CLEN])],
            plain('''<p>Pick the cable, the power and the test tool to fit the job.</p>
<ul><li><strong>Copper</strong> Ethernet works up to 100 m. For 10 Gb/s over the full 100 m, use Cat 6A.</li>
<li><strong>PoE</strong> sends power over the cable. 802.3af gives a device about 13 W, 802.3at (PoE+) about 25 W, 802.3bt more.</li>
<li><strong>Multimode fibre</strong> is for shorter runs in a building. <strong>Single-mode</strong> goes kilometres.</li>
<li>Optics at both ends must match, and dirty fibre ends cause many faults. Clean first.</li></ul>
<p>Tools: a toner finds a cable, a wire-map tester checks the pins, a certifier checks quality, a light meter checks fibre, an OTDR finds a break.</p>''',
                  L.format('2.3') + '; ' + CAB + '; ' + FIB,
                  [check('A PoE+ camera needs 22 W. Is an 802.3af port enough?', 'No, it delivers about 13 W to the device',
                         ['Yes, any PoE port gives at least 30 W', 'Yes, as long as the cable is Cat 6A or better'],
                         '802.3af delivers 12.95 W at the device, so a 22 W camera needs 802.3at or better. Cable category does '
                         'not raise the power a port supplies.', mc=[POE, POE])]),
            analogy('''<p>Think of plumbing.</p>
<p>Copper cable is a garden hose: fine across a garden (100 m), but the pressure fades if you go further. Single-mode fibre is a water main
that carries water between towns; multimode is a building’s internal pipes. PoE is sending hot water down the same pipe as the cold: handy,
but the boiler (the switch’s <strong>PoE budget</strong>) can run out if too many taps open at once, which is why phones reboot when more are added.</p>
<p>A plumber picks the right gauge: a tracer to find which pipe goes where (toner), a pressure test for each joint (wire map), and a camera down
the pipe to find the crack (OTDR). Most leaks are at the joints, just as most intermittent faults are bad terminations.</p>''',
                    L.format('2.3') + ' (plumbing analogy written for this rung); ' + CAB,
                    [check('In the plumbing story, phones reboot every time more are added. What does the boiler stand for?',
                           'The switch’s total PoE power budget', ['The length limit of the copper cable', 'A dirty fibre connector end face'],
                           'More devices drawing power can exhaust the switch’s PoE budget, so the newest or lowest-priority ports '
                           'lose power. Cable length and fibre cleanliness do not change with device count.', mc=[POE, OPT])]),
            visual('''<ol class="ladder-trace"><li><strong>Which wall jack goes to which panel port?</strong> Tone generator and probe.</li>
<li><strong>Is each conductor on the right pin?</strong> Continuity or wire-map tester.</li>
<li><strong>Link works at 100 Mb/s but not 1 Gb/s, or fails acceptance?</strong> Cable certifier (NEXT, return loss, split pairs, length).</li>
<li><strong>Is there light on the fibre, and how strong?</strong> Optical power meter and light source.</li>
<li><strong>Where along a long fibre is the break?</strong> OTDR.</li>
<li>Note: wire map can pass while certification fails on split pairs; re-terminate to T568A or T568B, the same at both ends.</li></ol>''',
                   L.format('2.3') + '; ' + CAB + '; ' + FIB,
                   [check('Using the tool list, a cable passes wire map but fails certification with split pairs. Why?',
                          'Right pins, wrong pairs, so crosstalk is high', ['The cable run is longer than the 100 m channel', 'The fibre end faces are dirty and need cleaning'],
                          'Split pairs put the conductors on the right pins but break the twists, so NEXT fails. Length would show '
                          'as a length fault, and fibre cleanliness is not a copper issue.', mc=[NEXT, TOOL])]),
            tryit('<p>Match each symptom to the tool you would reach for first.</p>', L.format('2.3') + '; ' + CAB,
                  [check('Which tool tells you how far along a long fibre the break is?', 'An OTDR', ['A tone generator and probe', 'A wire-map tester'],
                         'An OTDR sends pulses and times the reflections to locate breaks and bad splices. Toners trace copper '
                         'runs, and wire-map testers check copper pinning.', mc=[TOOL, TOOL])],
                  widget=sort('Which tool?',
                              {'Tone generator': ['Find which panel port a wall jack uses', 'Trace an unlabelled cable in a ceiling'],
                               'Cable certifier': ['Link stuck at 100 Mb/s on a new run', 'Acceptance test for a new install'],
                               'Optical power meter / OTDR': ['No light at the far fibre end', 'Locate a break in a 2 km fibre']},
                              'Notice that copper and fibre faults need different tools.'),
                  lab={'id': 'hw-cables', 'note': 'Identify the cable types and pick the test tool for each fault.'})),
        'core-concepts': same_as('core-content', 'Core concepts', 'A short summary (test cables before switches; intermittents are terminations) of the core section.'),
        **_filler('2.3'),
        'transmission-media-transceivers-and-connectors': section(
            'Transmission media, transceivers and connectors', 'NO-2.3',
            [check('A new fibre link stays down. One end has a multimode SR optic and the other a single-mode LR optic. What is the fix?',
                   'Fit a matching pair of transceivers', ['Swap the LC connectors for SC ones', 'Use a longer patch lead between the ends'],
                   'Optics must match each other and the fibre type and wavelength. The connector already fits; changing '
                   'connectors or lead length does not fix a mismatched pair.', mc=[OPT, OPT])],
            plain('''<p>Pick the medium by distance and place.</p>
<ul><li><strong>DAC (twinax)</strong>: short copper cable with optics built in. Good inside a rack.</li>
<li><strong>Twisted pair</strong>: up to 100 m. Good from desk to closet.</li>
<li><strong>Fibre</strong>: longer runs and between buildings. Single-mode for kilometres.</li>
<li><strong>Wireless</strong>, cellular and satellite for places cables cannot reach.</li></ul>
<p>Optics come as SFP/SFP+ (up to 25 Gb/s) or QSFP (four lanes, 40 Gb/s and up). Both ends must match.</p>
<p>Connectors: LC (most SFPs), SC, ST, MPO for fibre; RJ45 for Ethernet; RJ11 for phone; F-type for cable TV.</p>
<p>Cable in an air-return ceiling must be <strong>plenum</strong>-rated.</p>''',
                  L.format('2.3') + '; ' + FIB,
                  [check('Why must cable in a ceiling air-return space be plenum-rated?', 'Less toxic smoke in a fire',
                         ['It carries data further than normal cable', 'It blocks interference from air handlers'],
                         'Plenum jackets are made to produce less smoke and toxic gas, and building codes require them where air '
                         'circulates. They do not change reach or shielding.', mc=[CLEN, NEXT])]),
            analogy('''<p>Think about how you would move people between places.</p>
<p>Across a room you walk: that is a <strong>DAC</strong> cable between a server and the switch two metres away. Across a building you take
the corridor: <strong>twisted-pair</strong> copper, good to 100 m. Between towns you take the train: <strong>single-mode fibre</strong>. Where
there is no track, you fly: wireless, cellular or satellite.</p>
<p>The train only runs if the platforms match the train: a long-distance train cannot stop at a tram platform. A long-range LR optic will not
talk to a short-range SR optic, even if both plugs (LC) fit the socket.</p>''',
                    L.format('2.3') + ' (travel analogy written for this rung); ' + FIB,
                    [check('In the travel story, which medium is “walking across a room” for a server two metres from its switch?',
                           'A direct attach copper (DAC) cable', ['Single-mode fibre with LR optics', 'A cellular 5G link'],
                           'DAC is cheap and needs no separate optics for very short rack links. Single-mode fibre is for long runs, '
                           'and cellular is for places without cabling.', mc=[FMODE, FMODE])]),
            visual(svg(560, 110, 'Fibre link: switch A SFP+ port, 10GBASE-LR optic, single-mode LC duplex fibre, 10GBASE-LR optic, switch B SFP+ port',
                       box(5, 30, 90, 46, 'Switch A', 'SFP+') + box(115, 30, 95, 46, 'Optic', '10GBASE-LR') + box(230, 30, 100, 46, 'Fibre', 'SMF LC–LC')
                       + box(350, 30, 95, 46, 'Optic', '10GBASE-LR') + box(465, 30, 90, 46, 'Switch B', 'SFP+')
                       + arrow(95, 53, 115, 53) + arrow(210, 53, 230, 53) + arrow(330, 53, 350, 53) + arrow(445, 53, 465, 53)
                       + text(280, 100, 'speed, fibre type, wavelength and connector must match end to end'))
                   + '''<ol class="ladder-trace"><li>Check both ports take the same form factor and speed (SFP+, 10 Gb/s).</li>
<li>Check both optics are the same type (here 10GBASE-LR, single-mode, 1310 nm).</li>
<li>Check the fibre is the type the optics need (single-mode) and the connectors fit (LC duplex).</li>
<li>Inspect and clean the end faces.</li>
<li>Bring the link up and record both optics’ part numbers in the change record.</li></ol>''',
                   L.format('2.3') + '; ' + FIB,
                   [check('Which connector do most SFP fibre transceivers use?', 'LC duplex', ['RJ45 (copper)', 'F-type (coax)'],
                          'SFP optics use the small LC duplex connector. RJ45 is for twisted-pair Ethernet and F-type is for coax '
                          'cable broadband.', mc=[OPT, OPT])]),
            tryit('<p>Pick the medium for each link before you open the answer.</p>', L.format('2.3') + '; ' + FIB,
                  [check('Two buildings are 5 km apart. Which medium fits?', 'Single-mode fibre', ['Multimode fibre', 'Cat 6A twisted pair'],
                         'Single-mode fibre with laser optics reaches kilometres. Multimode is for hundreds of metres, and copper '
                         'stops at 100 m and brings ground-potential problems outdoors.', mc=[FMODE, CLEN])],
                  widget=sort('Which medium?',
                              {'DAC / twinax': ['Server to top-of-rack switch, 2 m', 'Switch to switch in the same rack'],
                               'Twisted-pair copper': ['Desk to wiring closet, 60 m', 'Wall jack to a PoE phone'],
                               'Fibre': ['Building to building, 800 m', 'Campus core to a site 5 km away']},
                              'Notice that distance decides most of these.'))),
    },
    '2.4': {
        'the-scenario': skip('The scenario', 'activity', 'The capstone ticket the student works; it sets up practice, not a concept.'),
        'your-turn-scaffolded-checklist': skip('Your turn — scaffolded checklist', 'activity', 'The checklist the student fills in during the capstone drill.'),
        'common-beginner-mistakes': skip('Common beginner mistakes', 'reference', 'Short list of capstone pitfalls; the ideas behind them are laddered in lessons 2.1–2.3.'),
        'check-your-understanding': skip('Check your understanding', 'activity', 'A self-check prompt for the capstone; it is practice, not an explanation.'),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '2.1': {'core-content': 'e6180897cc05', 'incident-application': '6fa836dd7510', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '443b884c7c33', 'beyond-the-quiz': '82511ac789c6', 'topologies-architectures-and-traffic-flows': '54848c566f7f'},
    '2.2': {'core-content': '3f15ab1e0b00', 'incident-application': 'b5595f8c0269', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '97a010071d97', 'beyond-the-quiz': 'e7442395d925'},
    '2.3': {'core-content': '14b493260ca6', 'incident-application': '859e9aae531a', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '1a0d5144dc08', 'beyond-the-quiz': '374a3e2398b6', 'transmission-media-transceivers-and-connectors': 'e98e798e8279'},
    '2.4': {'the-scenario': '7da5ef5850a4', 'your-turn-scaffolded-checklist': '336f0cb966c8', 'common-beginner-mistakes': '173cc49fb69b', 'check-your-understanding': 'cdda2cb3f068'},
}

# Option B pass 3: the practice/capstone blocks, core-concepts and depth signposts are bespoke ladders (_p3n2.py).
from curriculum_v2.ladder.netops._p3 import wire as _wire  # noqa: E402
from curriculum_v2.ladder.netops._p3n2 import SECS as _P3  # noqa: E402

_wire(LESSONS, MISCONCEPTIONS, _P3, 'NO-2.2')
