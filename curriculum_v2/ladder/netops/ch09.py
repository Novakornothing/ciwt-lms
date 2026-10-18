"""Explanation ladder — NETOPS chapter 9 (CLI labs: switch, router, inter-VLAN routing). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Commands follow Cisco IOS conventions used in the course labs.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 9

L = 'Course lesson {} (the original section), re-explained'
IOS = 'Cisco IOS configuration fundamentals and command references (CLI modes, show running-config, copy running-config startup-config)'
SW = 'Cisco Catalyst VLAN and interface configuration guides (switchport access vlan, show vlan brief, show interfaces trunk); IEEE Std 802.1Q'
RTR = 'Cisco IOS IP routing configuration guides (connected routes, show ip route, show ip interface brief, router-on-a-stick subinterfaces)'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO9-MODE-MIX': {
        'obj': 'NO-9.1', 'label': 'Mixing up user EXEC, privileged EXEC and global configuration modes',
        'fix': 'User EXEC (>) is limited; enable gives privileged EXEC (#) for full show commands; configure terminal changes the device.',
        'terms': ['user exec', 'privileged exec', 'enable', 'configure terminal'], 'source': L.format('9.1') + '; ' + IOS, 'review': R},
    'MC-L-NO9-CONFIG-IS-PROOF': {
        'obj': 'NO-9.1', 'label': 'Treating a typed configuration as proof that it works, without verifying',
        'fix': 'Verify port state, VLAN membership and the client’s address after every change: configuration without verification is hope.',
        'terms': ['verify', 'show vlan brief', 'ipconfig'], 'source': L.format('9.2') + '; ' + SW, 'review': R},
    'MC-L-NO9-ISOLATION-ORDER': {
        'obj': 'NO-9.2', 'label': 'Testing inter-VLAN routing from the far end first instead of building up from the same VLAN',
        'fix': 'Same-VLAN ping, then each PC to its own gateway, then both networks in the table, then the trunk allows both VLANs.',
        'terms': ['inter-vlan', 'isolation', 'gateway', 'trunk'], 'source': L.format('9.4') + '; ' + RTR, 'review': R},
}

WSHOW, VCO, MODE, CIP = 'MC-NO9-WRONG-SHOW', 'MC-NO9-VLAN-CREATE-ONLY', 'MC-L-NO9-MODE-MIX', 'MC-L-NO9-CONFIG-IS-PROOF'
ADMIN, SAS, SAVE, ISO, CONN = 'MC-NO9-ADMIN-DOWN-AS-PHYSICAL', 'MC-NO9-SHOW-AS-SAVE', 'MC-C-NO9-SAVE-CONFIG', 'MC-L-NO9-ISOLATION-ORDER', 'MC-L-NO9-ISOLATION-ORDER'

LESSONS = {
    '9.1': {
        'modes': section(
            'Modes', 'NO-9.1',
            [check('The prompt shows Switch>. Which command gets you to privileged mode?', 'enable', ['configure terminal', 'exit'],
                   'User EXEC (>) moves to privileged EXEC (#) with enable. configure terminal only works from privileged mode, '
                   'and exit leaves the session or mode.', mc=[MODE, MODE])],
            plain('''<p>A switch or router has three main modes.</p>
<ul><li><strong>User mode</strong> (prompt ends in <code>&gt;</code>): you can look at a little.</li>
<li><strong>Privileged mode</strong> (<code>#</code>, after <code>enable</code>): you can see everything with <code>show</code>.</li>
<li><strong>Configuration mode</strong> (<code>(config)#</code>, after <code>configure terminal</code>): you change the device.</li></ul>
<p>Changes take effect at once, but are not saved until you save them.</p>
<p>Before you change anything, know how to back out, and when to save.</p>''',
                  L.format('9.1') + '; ' + IOS,
                  [check('Which prompt means you are in global configuration mode?', 'Switch(config)#', ['Switch(config-if)#', 'Switch#'],
                         'The plain (config) tag marks global configuration mode. (config-if) is interface configuration, entered '
                         'from global mode, and Switch# is privileged EXEC, where show works.', mc=[MODE, MODE])]),
            analogy('''<p>Think of a museum.</p>
<p>As a visitor (<strong>user mode</strong>) you can walk the public rooms and look at the labels. With a staff badge (<strong>enable</strong>,
privileged mode) you can enter the archive and read every file, but you still cannot change the displays. The workshop (<strong>configuration
mode</strong>) is where exhibits are actually rebuilt.</p>
<p>A rebuilt exhibit is on show at once, but if the night cleaner resets the room (a <strong>reload</strong>) it goes back to the last approved
plan unless you filed the new plan (<strong>saved the config</strong>). A careful curator knows how to undo a change before starting.</p>''',
                    L.format('9.1') + ' (museum analogy written for this rung); ' + IOS,
                    [check('In the museum story, which mode is the archive where you read every file but change nothing?', 'Privileged EXEC (#)',
                           ['User EXEC (>)', 'Global configuration (config)#'],
                           'Privileged EXEC gives full show access without changing settings. User EXEC is the public rooms, and '
                           'configuration mode is the workshop that changes the device.', mc=[MODE, MODE])]),
            visual('''<ol class="ladder-trace"><li><code>Switch&gt;</code> type <code>enable</code>.</li>
<li><code>Switch#</code> type <code>show running-config</code> and copy it into your lab notes.</li>
<li><code>Switch#</code> type <code>configure terminal</code>.</li>
<li><code>Switch(config)#</code> type <code>hostname SW1</code>; the prompt changes to <code>SW1(config)#</code> at once.</li>
<li>Type <code>end</code> to go back to <code>SW1#</code>.</li>
<li>Decide: save with <code>copy running-config startup-config</code>, or leave it unsaved so a reload undoes it.</li></ol>''',
                   L.format('9.1') + '; ' + IOS,
                   [check('After step 4, the hostname shows in the prompt. Is it saved for the next reload?', 'No, not until you copy it to startup-config',
                          ['Yes, a prompt change means it was saved', 'Yes, leaving configuration mode saves it'],
                          'Changes live in running-config until copied to startup-config. Neither the new prompt nor typing end '
                          'writes NVRAM.', mc=[SAVE, SAS])]),
            tryit('<p>Set the hostname on the lab switch, check the prompt, then save it.</p>', L.format('9.1') + '; ' + IOS,
                  [check('Which command shows the configuration the device is using right now?', 'show running-config',
                         ['show startup-config', 'show version'],
                         'running-config is the live configuration in memory. startup-config is what loads at the next boot, and show '
                         'version reports software and hardware.', mc=[WSHOW, SAS])],
                  widget=order('Order the steps', ['enable', 'configure terminal', 'hostname SW1', 'end', 'copy running-config startup-config'],
                               'Each command only works in the mode the one before it put you in.'),
                  lab={'id': 'sw-hostname-write', 'note': 'Set the switch hostname and save it so it survives a reload.'})),
    },
    '9.2': {
        'verification-mindset': section(
            'Verification mindset', 'NO-9.1',
            [check('You created VLAN 20 and named it USERS, but PC-A still is not in it. What is missing?', 'switchport access vlan 20 on PC-A’s port',
                   ['A name for VLAN 20 that matches the diagram exactly', 'A trunk on PC-A’s port allowing VLAN 20'],
                   'Creating or naming a VLAN does not move any port into it; the access port needs switchport access vlan 20. A '
                   'PC port should be an access port, not a trunk.', mc=[VCO, VCO])],
            plain('''<p>Typing a command is not the same as proving it works.</p>
<p>After every change, check three things:</p>
<ol><li>The <strong>port is up</strong>.</li>
<li>The port is in the <strong>right VLAN</strong>.</li>
<li>The PC got an <strong>address in the right subnet</strong>.</li></ol>
<p>Two VLANs on one switch do not talk to each other. A broadcast in VLAN 20 never reaches VLAN 30. They need a router to connect them.</p>''',
                  L.format('9.2') + '; ' + SW,
                  [check('Which command shows which ports are in which VLAN?', 'show vlan brief', ['show ip route', 'show mac address-table count'],
                         'show vlan brief lists each VLAN and its access ports. show ip route shows routes, and the MAC table count '
                         'shows how many addresses were learned, not VLAN membership.', mc=[WSHOW, WSHOW])]),
            analogy('''<p>Think of a teacher handing out room changes.</p>
<p>Writing “Room 20” on the board does not move any student there; each student must be told which room they belong to. That is creating a
VLAN versus putting a port in it. A good teacher then checks: is the student in the building (<strong>port up</strong>), in the right room
(<strong>VLAN membership</strong>), and do they have the right timetable for that room (<strong>an address in that subnet</strong>)?</p>
<p>Students in room 20 cannot hear announcements in room 30. That is two broadcast domains, until someone builds a corridor between them (a
router).</p>''',
                    L.format('9.2') + ' (classroom analogy written for this rung); ' + SW,
                    [check('In the classroom story, the student is in room 20 but has room 30’s timetable. What is the network equivalent?',
                           'Right VLAN, but an address in the wrong subnet', ['The port is shut down', 'The VLAN does not exist on the switch'],
                           'The port and VLAN are right, but the PC’s address does not match that VLAN’s subnet, so check its DHCP or '
                           'static settings. A shut port or missing VLAN would fail earlier checks.', mc=[CIP, VCO])]),
            visual(svg(560, 120, 'Switch with VLAN 20 holding PC-A and VLAN 30 holding a printer; broadcasts stay inside each VLAN',
                       box(170, 10, 220, 40, 'SW1') + box(40, 70, 200, 40, 'VLAN 20 users', 'PC-A 10.20.0.10') + box(320, 70, 200, 40, 'VLAN 30 printers', 'PRN 10.30.0.20')
                       + arrow(240, 50, 140, 70) + arrow(320, 50, 420, 70) + text(280, 100, 'no path', 11))
                   + '''<ol class="ladder-trace"><li><code>vlan 20</code>, <code>name USERS</code>; <code>vlan 30</code>, <code>name PRINTERS</code>.</li>
<li>PC-A’s port: <code>switchport mode access</code>, <code>switchport access vlan 20</code>. Printer’s port: VLAN 30.</li>
<li><code>show interfaces status</code>: both ports connected.</li>
<li><code>show vlan brief</code>: each port listed under its VLAN.</li>
<li>PC-A’s <code>ipconfig</code>: an address in VLAN 20’s subnet.</li>
<li>Ping PC-A to the printer: fails, as expected, until routing exists.</li></ol>''',
                   L.format('9.2') + '; ' + SW,
                   [check('At step 6 the ping from PC-A to the printer fails. What does that show?', 'The VLANs are separate, as designed',
                          ['The printer port is broken and needs a new cable', 'VLAN 30 was never created on the switch'],
                          'Different VLANs are separate broadcast domains with no route between them yet, so the failure is the expected '
                          'result. Steps 3 and 4 already proved the port and VLAN.', mc=[CIP, VCO])]),
            tryit('<p>Build the two VLANs in the lab, then prove each of the three checks.</p>', L.format('9.2') + '; ' + SW,
                  [check('After assigning the port, what proves the PC is really on VLAN 20?', 'Its address sits in VLAN 20’s subnet',
                         ['The command was accepted with no error', 'The port light is green'],
                         'An accepted command and a green light do not prove membership or addressing. The PC getting an address in the '
                         'expected subnet, plus show vlan brief, does.', mc=[CIP, CIP])],
                  widget=order('Order the checks', ['Port is up (show interfaces status)', 'Port is in VLAN 20 (show vlan brief)',
                                                    'PC has an address in VLAN 20’s subnet', 'Ping to another VLAN fails until routing exists'],
                               'Each check builds on the one before.'),
                  lab={'id': 'sw-vlan-multi', 'note': 'Create two VLANs, assign ports, and verify membership with show vlan brief.'})),
    },
    '9.3': {
        'reading-the-table': section(
            'Reading the table', 'NO-9.2',
            [check('PC-A cannot ping its gateway 10.20.0.1. What do you check before chasing “the internet”?', 'Cable, VLAN, PC settings and the router interface',
                   ['The ISP circuit and the provider’s status page', 'The DNS servers configured on PC-A'],
                   'If the gateway does not answer, the fault is local: link, VLAN, the PC’s address and mask, or the router '
                   'interface. The ISP and DNS sit beyond a step that already fails.', mc=[ADMIN, ADMIN])],
            plain('''<p>A router adds a <strong>connected route</strong> by itself when an interface is up and has an address.</p>
<p>If the interface is down, the route disappears.</p>
<p>If a PC cannot ping its gateway, check these first:</p>
<ul><li>the cable, port and VLAN;</li>
<li>the PC’s address and mask;</li>
<li>the router interface: is it up? Is it <code>administratively down</code>, which means it needs <code>no shutdown</code>?</li></ul>
<p>Test both ways: PC to router, and router to PC.</p>''',
                  L.format('9.3') + '; ' + RTR,
                  [check('show ip interface brief lists G0/1 as administratively down. What fixes it?', 'no shutdown on G0/1',
                         ['Replacing the cable on G0/1', 'Reloading the router'],
                         'Administratively down means the interface is shut in configuration, so no shutdown brings it up. A cable '
                         'fault shows as down/down, and a reload keeps the saved shutdown.', mc=[ADMIN, ADMIN])]),
            analogy('''<p>Think of a shop’s list of delivery areas.</p>
<p>The shop can deliver to a street only while its own door onto that street is open: an interface that is <strong>up with an address</strong>
creates a <strong>connected route</strong>. If the manager locks the door (<code>shutdown</code>), that street vanishes from the list until someone
unlocks it (<code>no shutdown</code>).</p>
<p>If a customer next door cannot reach the shop, you check the front step, the customer’s own address and the shop door before blaming the
national road network. And you test both ways: customer to shop, and shop to customer.</p>''',
                    L.format('9.3') + ' (shop-door analogy written for this rung); ' + RTR,
                    [check('In the shop story, why test both ways (PC to router and router to PC)?', 'One-way success can hide a fault on the other side',
                           ['Routers ignore pings from PCs on the same subnet', 'Testing twice is only needed for the logbook'],
                           'Asymmetric failures happen, for example a wrong mask or host firewall on one side, so both directions are '
                           'evidence. Routers do answer pings from their subnets.', mc=['MC-NO9-ROUTE-EVIDENCE', 'MC-NO9-ROUTE-EVIDENCE'])]),
            visual('''<ol class="ladder-trace"><li>Configure <code>interface G0/0</code>, <code>ip address 10.20.0.1 255.255.255.0</code>, <code>no shutdown</code>.</li>
<li><code>show ip interface brief</code>: G0/0 up/up with 10.20.0.1.</li>
<li><code>show ip route</code>: <code>C 10.20.0.0/24 is directly connected, G0/0</code> and <code>L 10.20.0.1/32</code>.</li>
<li>Set PC-A to 10.20.0.10/24, gateway 10.20.0.1.</li>
<li>Ping PC-A → 10.20.0.1, then router → 10.20.0.10. Record both.</li>
<li>Shut G0/0 and look again: the C route is gone.</li></ol>''',
                   L.format('9.3') + '; ' + RTR,
                   [check('At step 6 you shut G0/0. What happens to the C 10.20.0.0/24 route?', 'It leaves the routing table',
                          ['It stays but is marked as backup', 'It turns into a static route'],
                          'Connected routes exist only while the interface is up with an address, so shutting it removes the route. IOS '
                          'does not keep it as a backup or convert it.', mc=[ADMIN, ADMIN])]),
            tryit('<p>Bring up a router interface in the lab and read the connected route it creates.</p>', L.format('9.3') + '; ' + RTR,
                  [check('Which line in show ip route marks a connected network?', 'A line starting with C', ['A line starting with S', 'A line starting with O'],
                         'C marks a directly connected network (L marks the router’s own address). S is static and O is OSPF-learned.',
                         mc=['MC-NO9-ROUTE-EVIDENCE', 'MC-NO9-ROUTE-EVIDENCE'])],
                  widget=reveal('show ip interface brief: G0/1 10.30.0.1 administratively down down. What do you type, and what then appears in show ip route?',
                                'interface G0/1, then no shutdown. Once up/up, show ip route lists C 10.30.0.0/24 directly connected, G0/1.'),
                  lab={'id': 'rtr-two-interfaces', 'note': 'Bring up two router interfaces and read both connected routes.'})),
    },
    '9.4': {
        'isolation-order': section(
            'Isolation order', 'NO-9.2',
            [check('VLAN 20 cannot reach VLAN 30 through router-on-a-stick. Both PCs ping their own gateways. What do you check next?',
                   'That both networks are in the router’s table', ['That each PC can ping a host in its own VLAN', 'That the cable to PC-A is good'],
                   'Pinging their gateways already proves the PCs, cables and same-VLAN path, so the next step up is the routing '
                   'table and then the trunk. Going back to cables repeats proven steps.', mc=[ISO, ISO])],
            plain('''<p>When two VLANs cannot talk, check in this order.</p>
<ol><li>Can two PCs in the <strong>same VLAN</strong> ping each other?</li>
<li>Can each PC ping its <strong>own gateway</strong>?</li>
<li>Does the router have <strong>both networks</strong> in its table?</li>
<li>If a trunk links the switch and router, does it <strong>allow both VLANs</strong>?</li></ol>
<p>Stop at the first “no”. That is where the problem is.</p>
<p>Common causes: a port in the wrong VLAN, a wrong mask, or a subinterface that is down.</p>''',
                  L.format('9.4') + '; ' + RTR,
                  [check('PC-A cannot ping its gateway 10.20.0.1, though a neighbour in VLAN 20 can. What is a likely cause?', 'PC-A’s port is in the wrong VLAN',
                         ['The trunk does not allow VLAN 30', 'The router lacks a route to VLAN 30'],
                         'A neighbour in the same VLAN reaches the gateway, so the trunk and router are fine for VLAN 20; PC-A’s own port '
                         'or settings are wrong. VLAN 30 issues would not stop PC-A reaching its own gateway.', mc=[ISO, VCO])]),
            analogy('''<p>Think of checking why a letter between two towns never arrived.</p>
<p>First: can people on the same street pass notes? (<strong>same VLAN</strong>). Then: can each person reach their own post office?
(<strong>own gateway</strong>). Then: does the sorting centre know both towns? (<strong>both networks in the table</strong>). Finally: does
the van between the post office and sorting centre carry post for both towns? (<strong>the trunk allows both VLANs</strong>).</p>
<p>The first “no” tells you where to dig. Starting at the van when the person cannot even reach their post office wastes the afternoon.</p>''',
                    L.format('9.4') + ' (letter analogy written for this rung); ' + RTR,
                    [check('In the letter story, what is “the van that must carry post for both towns”?', 'The trunk allowing both VLANs',
                           ['The routing table on the router', 'The access port of each PC'],
                           'On router-on-a-stick, one trunk carries every VLAN to the router, so both must be allowed. The routing table is '
                           'the sorting centre, and access ports are the streets.', mc=[ISO, ISO])]),
            visual(svg(560, 130, 'Router-on-a-stick: PC-A in VLAN 20 and printer in VLAN 30 on a switch, trunk to router subinterfaces G0/0.20 and G0/0.30',
                       box(210, 5, 140, 44, 'Router', 'G0/0.20 · G0/0.30') + box(210, 80, 140, 40, 'Switch')
                       + box(20, 80, 150, 40, 'PC-A', 'VLAN 20') + box(390, 80, 150, 40, 'Printer', 'VLAN 30')
                       + arrow(280, 80, 280, 49, '') + text(330, 68, 'trunk: 20, 30', 11) + arrow(170, 100, 210, 100) + arrow(390, 100, 350, 100))
                   + '''<ol class="ladder-trace"><li>Same-VLAN ping: PC-A to another VLAN 20 host. Pass.</li>
<li>PC-A to 10.20.0.1 and printer to 10.30.0.1. Printer fails.</li>
<li><code>show ip interface brief</code>: G0/0.30 up; <code>show ip route</code>: C 10.30.0.0/24 present.</li>
<li><code>show interfaces trunk</code>: allowed VLANs 1, 20. VLAN 30 missing.</li>
<li>Fix: <code>switchport trunk allowed vlan add 30</code>.</li>
<li>Retest step 2, then PC-A to the printer. Record the misconfig and fix.</li></ol>''',
                   L.format('9.4') + '; ' + SW,
                   [check('In the trace, which show command found the fault?', 'show interfaces trunk', ['show vlan brief', 'show running-config | include hostname'],
                          'The allowed-VLAN list is shown by show interfaces trunk, where VLAN 30 was missing. show vlan brief lists access '
                          'ports, and the hostname line is unrelated.', mc=[WSHOW, WSHOW])]),
            tryit('<p>Make VLAN 20 reach VLAN 30 in the lab, then break one thing on purpose and fix it with the isolation order.</p>', L.format('9.4') + '; ' + RTR,
                  [check('Which mistake makes a PC reach some local hosts but treat others as remote?', 'A wrong subnet mask on the PC',
                         ['A trunk that allows every VLAN', 'A subinterface that is up'],
                         'A wrong mask changes what the PC thinks is local, so some same-subnet hosts get sent to the gateway. An open '
                         'trunk and an up subinterface are working conditions.', mc=[ISO, ISO])],
                  widget=order('Order the isolation checks', ['Same-VLAN ping', 'Each PC to its own gateway', 'Both networks in the routing table',
                                                              'Trunk allows both VLANs', 'PC-A to the printer'],
                               'Stop at the first failure.'),
                  lab={'id': 'sw-vlan-and-trunk', 'note': 'Build VLANs and a trunk to the router, then verify routing between them.'})),
    },
    '9.5': {
        'ordered-checks': section(
            'Ordered checks', 'NO-9.2',
            [check('A new closet drop has no network. Which check comes first in the lesson’s order?', 'Link lights and show interfaces status',
                   ['The DHCP pool or relay for the VLAN', 'The router subinterface for the subnet'],
                   'The order starts at the physical link, because nothing above it can work until the link is up. DHCP and the '
                   'router subinterface come later in the list.', mc=[ISO, ISO])],
            plain('''<p>For a new network drop, check from the bottom up.</p>
<ol><li><strong>Link lights</strong> and <code>show interfaces status</code>.</li>
<li>The switch port’s <strong>access VLAN</strong>.</li>
<li>The <strong>trunk</strong> to the router, if there is one.</li>
<li>The router <strong>subinterface or SVI</strong>: up, with the right subnet.</li>
<li><strong>DHCP</strong> pool or relay, and the PC’s settings.</li></ol>
<p>Then hand over an evidence pack: commands, outputs, the cause, the fix, a ping test, and proof the user can open the intranet.</p>''',
                  L.format('9.5') + '; ' + SW + '; ' + RTR,
                  [check('What final proof belongs in the evidence pack besides a ping?', 'The user opening the intranet', ['The switch’s serial number', 'A screenshot of the login banner'],
                         'Verification from the user’s side shows the service works, not only the path. Serial numbers and banners do '
                         'not show the fix worked.', mc=[CIP, CIP])]),
            analogy('''<p>Think of moving into a new flat.</p>
<p>First, is the electricity on at the meter? (<strong>link</strong>). Is your flat on the right circuit? (<strong>access VLAN</strong>). Does the
building’s riser carry your circuit up? (<strong>trunk</strong>). Is the building’s main panel switched on for your floor? (<strong>subinterface
or SVI</strong>). Finally, did you get your key and post box number? (<strong>DHCP</strong>).</p>
<p>When it all works, you do not just say “power’s on”: you show the electrician’s readings and switch on the kettle (<strong>the user opens the
intranet</strong>).</p>''',
                    L.format('9.5') + ' (new-flat analogy written for this rung)',
                    [check('In the flat story, “the riser carries your circuit up” matches which check?', 'The trunk to the router',
                           ['The access VLAN on the switch port', 'The DHCP pool for the VLAN'],
                           'The trunk carries the VLAN from the access switch to the router. The access VLAN is the flat’s own circuit, '
                           'and DHCP is the key and post box.', mc=[ISO, ISO])]),
            visual('''<ol class="ladder-trace"><li><code>show interfaces status</code>: Gi1/0/7 connected. Pass.</li>
<li><code>show vlan brief</code>: Gi1/0/7 in VLAN 1, should be 40. Fix: <code>switchport access vlan 40</code>.</li>
<li><code>show interfaces trunk</code>: VLAN 40 allowed. Pass.</li>
<li><code>show ip interface brief</code> on the router: G0/0.40 up, 10.20.40.1/24. Pass.</li>
<li>PC: <code>ipconfig /renew</code> gives 10.20.40.57. Ping 10.20.40.1: pass.</li>
<li>User opens the intranet. Evidence pack: commands, outputs, cause (wrong VLAN), fix, verification.</li></ol>''',
                   L.format('9.5') + '; ' + SW,
                   [check('In the trace, the port was in VLAN 1 instead of 40. Why did the link check at step 1 still pass?',
                          'Link state does not depend on the VLAN', ['VLAN 1 always shows as disconnected', 'The trunk hid the wrong VLAN'],
                          'A port can be connected with a green light in any VLAN, so a wrong VLAN only shows at step 2. VLAN 1 ports '
                          'connect normally, and the trunk does not affect access-port state.', mc=[VCO, CIP])]),
            tryit('<p>Work the closet scenario in the lab and build the evidence pack as you go.</p>', L.format('9.5'),
                  [check('Which order is right for the first three checks?', 'Link, access VLAN, trunk', ['Trunk, access VLAN, link', 'DHCP, link, trunk'],
                         'The lesson goes bottom-up: link first, then the port’s VLAN, then the trunk. Starting at the trunk or DHCP skips '
                         'the cheapest, most common faults.', mc=[ISO, ISO])],
                  widget=order('Order the closet checks', ['Link lights / show interfaces status', 'Access VLAN on the port', 'Trunk to the router',
                                                           'Router subinterface or SVI', 'DHCP pool or relay and PC settings'],
                               'Bottom-up: each layer depends on the one below.'),
                  lab={'id': 'scn-lan2-fix', 'note': 'Fix the new-closet scenario and record each check’s evidence.'})),
    },
    '9.6': {
        'check': section(
            'Check', 'NO-9.2',
            [check('After saving, which two commands should both show the new hostname?', 'show running-config and show startup-config',
                   ['show version and show clock', 'show ip route and show vlan brief'],
                   'running-config is the live configuration and startup-config is what loads at boot; both should match after a '
                   'save. The other commands do not show the hostname setting.', mc=[SAVE, WSHOW])],
            plain('''<p>Saving copies your live settings so they load again after a restart.</p>
<ul><li><strong>running-config</strong> is what the device uses now.</li>
<li><strong>startup-config</strong> is what it loads when it restarts.</li>
<li><code>copy running-config startup-config</code> (or <code>write memory</code>) saves one into the other.</li></ul>
<p>To check it worked, look at both. Each should show the new hostname.</p>
<p>A <code>show</code> command only looks. It never saves anything.</p>''',
                  L.format('9.6') + '; ' + IOS,
                  [check('Which command saves the configuration so it survives a reload?', 'copy running-config startup-config',
                         ['show startup-config | include hostname', 'reload'],
                         'Copying running to startup writes the configuration to NVRAM. show only displays a config, and reload without saving '
                         'throws unsaved changes away.', mc=[SAS, SAS])]),
            analogy('''<p>Think of editing a document on a shared computer that wipes itself every night.</p>
<p>What is on the screen is <strong>running-config</strong>. The copy in your cloud folder is <strong>startup-config</strong>: that is what you
get back tomorrow. Pressing <strong>Save</strong> (<code>copy running-config startup-config</code>) is the only thing that updates the cloud copy.
Scrolling through the document (<code>show</code>) does not save it.</p>
<p>To be sure, you open the cloud copy and check your latest edit is there, just like comparing running and startup configs.</p>''',
                    L.format('9.6') + ' (shared-computer analogy written for this rung); ' + IOS,
                    [check('In the shared-computer story, what happens to unsaved edits at night?', 'They are lost when the device reloads',
                           ['They are saved automatically at shutdown', 'They move into startup-config by themselves'],
                           'Unsaved running-config changes are gone after a reload; IOS does not save them automatically. Only '
                           'copying to startup-config keeps them.', mc=[SAVE, SAVE])]),
            visual('''<ol class="ladder-trace"><li><code>configure terminal</code>, <code>hostname SW1</code>, <code>end</code>.</li>
<li><code>show running-config | include hostname</code>: <code>hostname SW1</code>.</li>
<li><code>show startup-config | include hostname</code>: still the old name.</li>
<li><code>copy running-config startup-config</code>.</li>
<li><code>show startup-config | include hostname</code>: now <code>hostname SW1</code>.</li>
<li>Optional: <code>reload</code>; the prompt still shows SW1.</li></ol>''',
                   L.format('9.6') + '; ' + IOS,
                   [check('At step 3, startup-config still has the old name. What does that mean?', 'The change has not been saved yet',
                          ['The hostname command failed', 'startup-config cannot store hostnames'],
                          'Step 2 proves the change is live, but startup-config updates only when you copy it there. The command worked, '
                          'and hostnames are stored in startup-config.', mc=[SAVE, SAVE])]),
            tryit('<p>Set and save the hostname on the lab router, then prove it with both show commands.</p>', L.format('9.6') + '; ' + IOS,
                  [check('A colleague says “I ran show running-config, so it’s saved.” What is wrong?', 'show only displays; it does not save',
                         ['Nothing, show running-config saves the file', 'show running-config erases the startup copy'],
                         'show commands only read. Saving needs copy running-config startup-config or write memory, and show never '
                         'erases anything.', mc=[SAS, SAS])],
                  widget=order('Order the save-and-prove steps', ['Change the hostname', 'Check running-config', 'copy running-config startup-config',
                                                                  'Check startup-config shows the new name'],
                               'Proof is the last step, not an extra.'),
                  lab={'id': 'rtr-hostname-write', 'note': 'Set the router hostname, save it, and compare running and startup configs.'})),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '9.1': {'modes': '93f09cdb9b92'},
    '9.2': {'verification-mindset': 'a9d58cc7358b'},
    '9.3': {'reading-the-table': 'c6e51894b0a2'},
    '9.4': {'isolation-order': '9d967c1ff489'},
    '9.5': {'ordered-checks': '9d84c1680d2e'},
    '9.6': {'check': 'efa80090b8ce'},
}
