"""Option B pass 3 — NETOPS chapter 2 bespoke ladders (switching, VLANs, cabling, isolated-user capstone). Pending SME review."""
from curriculum_v2.ladder.netops._p3 import N, mc, src
from curriculum_v2.ladder.schema import order, reveal, sort

SECS = {}
TBL, ERRD, VGW, POE, OPT = ('MC-L-NO2-TABLE-FROM-DEST', 'MC-L-NO2-ERRDISABLE-JUST-RESET', 'MC-L-NO2-VLAN-NO-GATEWAY',
                            'MC-L-NO2-POE-BUDGET', 'MC-L-NO2-OPTIC-MISMATCH')
UNK, LOOP, DEVL, CLEN, TOOL, FMODE = ('MC-NO2-UNKNOWN-UNICAST', 'MC-NO2-LOOP-MISSED', 'MC-NO2-DEVICE-LAYER', 'MC-NO2-COPPER-LENGTH',
                                      'MC-NO2-WRONG-TOOL', 'MC-NO2-FIBRE-MODE')
WVF, TALL, NAT, PHYS, LAYER = ('MC-NO2-WRONG-VLAN-FIX', 'MC-NO2-TRUNK-ALLOWED', 'MC-NO2-NATIVE-VLAN', 'MC-C-NO2-PHYS-FAULT',
                               'MC-C-NO1-OSI-LAYER')
MACT = ('sw-mac-table', 'Run show mac address-table and match each MAC to the port it was learned on.')
VACC = ('sw-vlan-access', 'Compare the access VLAN on the user’s port with a working neighbour’s port.')
CAB = ('hw-cables', 'Pick the right cable and tester for each link on the bench and note the result.')


def _add(label, sid, title, *a):
    SECS[(label, sid)] = N(label, sid, src(label, title), *a)


# ================================================================== 2.1 Switching Basics
m = mc('2.1')
T = 'Switching Basics'
_add('2.1', 'core-concepts', T, [
    ('How does a switch decide which port gets a frame?', 'Destination MAC', 'The destination IP route', 'The user’s login name',
     'A switch forwards by looking up the destination MAC in its MAC table.', DEVL, TBL),
    ('Where does a switch learn MAC addresses from?', 'Source MACs', 'Destination MACs only', 'The DNS server records',
     'It learns each source MAC and the port it arrived on.', TBL, TBL),
    ('In the post-office story, the sorting rack is what?', 'The MAC table', 'The router’s route list', 'The parcel itself',
     'The town sorting rack maps names to pigeonholes, like MACs to ports.', TBL, DEVL),
    ('In the chart, an unknown destination MAC is…', 'Flooded', 'Dropped silently at once', 'Routed to the gateway',
     'Unknown unicast frames are flooded out all ports in the VLAN.', UNK, UNK),
    ('Two PCs on one switch cannot talk. First suspect?', 'Local switching', 'The internet router', 'The ISP circuit',
     'Hosts on one switch and VLAN talk without routing; look locally first.', DEVL, m('RECALL')),
], ([
    'A switch moves frames inside one local network.',
    'It reads the source MAC of each frame.',
    'It notes which port that MAC came from.',
    'That list is the MAC table.',
    'It sends frames to the port of the destination MAC.',
    'Unknown destinations are sent out every port.',
    'Not every fault is a routing fault.',
], 'Switching is local and MAC-based; check it before you blame routing.'), (
    'A small town post office sorts letters by house name into pigeonholes. When a new family sends their first letter, '
    'the clerk notes their pigeonhole. Letters for unknown names get copied to every pigeonhole until someone claims them.',
    [('Pigeonhole', 'switch port'), ('House name', 'MAC address'), ('Clerk’s notebook', 'MAC address table'),
     ('Copying to every pigeonhole', 'flooding unknown unicast')],
    'A clerk remembers for years. A switch forgets entries after a few minutes of silence, so the table changes all the time.'),
    ('flow', 'How a switch handles one frame', ['Frame arrives', 'Learn source MAC', 'Look up destination', 'Known: one port',
                                                'Unknown: flood']),
    'Follow the frame left to right. Learning happens from the source; forwarding decisions use the destination.',
    'Run show mac address-table in the lab. Pick two entries and write the MAC, VLAN and port for each.',
    order('Order the switch steps.', ['Frame arrives', 'Learn the source MAC', 'Look up the destination MAC', 'Forward or flood'],
          'Learn from source, forward by destination.'), MACT)

_add('2.1', 'incident-application', T, [
    ('One desk cannot reach a printer on the same switch. Scope?', 'Local, one switch', 'Whole company WAN', 'The ISP network',
     'Both devices share a switch, so the fault is local switching or the port.', DEVL, m('ESCALATE')),
    ('The printer MAC is missing from the table. Note it?', 'Yes, with time', 'No, skip it for now', 'Only if fixed later',
     'Missing MAC entries are evidence; record with the time.', m('NEG'), m('NEG')),
    ('In the hotel-reception story, the guest book is?', 'The MAC table', 'The hotel’s front door', 'The room key card',
     'Reception’s guest book maps guests to rooms like the MAC table maps MACs to ports.', TBL, DEVL),
    ('In the timeline, what proves the printer port is dead?', 'No MAC, no link', 'One failed print job', 'A user complaint',
     'No link light and no learned MAC on that port together point to the port or cable.', PHYS, m('NEG')),
    ('Good 15-minute status line?', 'Printer link down; checking', 'Network is broken', 'Fixed in two minutes, promise',
     'Accurate, calm, with the next step and no promises.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking switching incident.',
    'At 10:00 a desk cannot print. The printer is on the same switch.',
    'You check the MAC table. The printer’s MAC is missing.',
    'You check the port. No link light.',
    'You note each result with its time.',
    'You reseat the cable and the MAC returns.',
    'You tell users what happened in plain words.',
], 'A missing MAC plus no link points to the port; record both before you act.'), (
    'At a hotel, reception keeps a guest book of who is in which room. If a guest is not in the book, either they never '
    'checked in or they left. A printer missing from the MAC table is a guest who never arrived at the switch.',
    [('Guest book', 'MAC table'), ('Room number', 'switch port'), ('Guest never checked in', 'device has no link'),
     ('Calling the room', 'pinging the printer')],
    'A hotel guest can explain where they are. A printer cannot, so you read link lights and the table instead.'),
    ('flow', 'Printer on the same switch', ['10:00 print fails', '10:03 MAC missing', '10:05 port no link', '10:07 reseat cable',
                                            '10:09 MAC learned']),
    'The middle boxes are evidence written before the change. The last box is the proof after the change.',
    'Write a five-line timeline for a desk that cannot reach a local printer, including the MAC table result.',
    order('Order the incident.', ['Confirm the symptom', 'Check MAC table', 'Check link on the port', 'Make one fix', 'Verify the MAC returns'],
          'Evidence, one fix, verify.'), MACT)

_add('2.1', 'standard-of-work', T, [
    ('The MAC table shows the PC on port 7. Write it?', 'Yes, it is evidence', 'No, nothing was wrong', 'Only if it failed',
     'Passed checks rule things out; record them.', m('NEG'), m('NEG')),
    ('Clearing the MAC table and rebooting the switch together is…', 'Untracked parallel change', 'Good fast practice for outages',
     'Required by policy', 'Two big changes at once hide the cause and drop every user.', m('PARALLEL'), m('PARALLEL')),
    ('In the gardener story, one plant at a time means?', 'One change at a time', 'Water every plant at the same time', 'Skip the notes',
     'A gardener changes one thing per plant to see the effect.', m('PARALLEL'), m('NEG')),
    ('In the chart, which is on the “avoid” side?', 'Reboot the switch', 'Note the MAC entry', 'Retest after fix',
     'A switch reboot is a big change that hits everyone.', m('PARALLEL'), m('NEG')),
    ('Which ticket line meets the standard?', 'Port 7 MAC seen 10:12', 'Played with the switch for a while', 'Done',
     'Test, result and time make a trustworthy line.', m('NEG'), m('CHECKLIST')),
], ([
    'Switch work has two habits.',
    'Write down checks that passed.',
    'A MAC seen on the right port rules out the table.',
    'Make one change at a time.',
    'Never clear tables and reboot together.',
    'A reboot drops everyone on the switch.',
], 'Record passed switch checks and make single, tracked changes.'), (
    'A gardener testing why one rose wilts changes only its water first and writes the result. If she also moves it and '
    'adds feed, she will never know what worked. She also writes “soil fine”, so nobody digs it up again.',
    [('One rose', 'one switch port'), ('Changing only the water', 'one tracked change'), ('“Soil fine” note', 'passed MAC check'),
     ('Digging up the whole bed', 'rebooting the whole switch')],
    'A wilting rose affects one plant. A switch reboot affects every desk on it at once.'),
    ('two', 'Switching standard of work', (('Do', ['Note MAC and port seen', 'Change one port setting', 'Retest the one desk']),
                                           ('Avoid', ['Skipping passed checks', 'Clearing tables at random', 'Rebooting the switch']))),
    'Each row pairs a good habit with the mistake it replaces.',
    'Rewrite “messed with the switch, fixed” as a standard line with port, change, time and retest.',
    reveal('Rewrite: “messed with the switch, fixed”.', '10:12 Gi0/7 shut/no shut; link up 10:13; printer MAC learned 10:13.'), MACT)

_add('2.1', 'practice-standard-for-this-lesson', T, [
    ('First line of a switching checklist?', 'Check link light', 'Reboot the core switch first', 'Change the VLAN',
     'Start with physical link before table lookups.', m('CHECKLIST'), m('PARALLEL')),
    ('Pass sign for “MAC table” step?', 'MAC on expected port', 'Any MAC at all', 'A long table output on screen',
     'Good means the device’s MAC is learned on the port you expect.', TBL, m('CHECKLIST')),
    ('In the recipe story, the “done” test is?', 'The pass sign', 'The cooking pot', 'The shopping list',
     'A recipe says how to know a step is done; a checklist step does too.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “MAC on port”?', 'Ping the host', 'Reboot switch', 'Call the ISP',
     'Once the MAC is learned, test reachability to the host.', m('CHECKLIST'), m('PARALLEL')),
    ('How do you show mastery?', 'Teach it without notes', 'Read the slides to them', 'Copy the glossary out',
     'Walk a peer through switching with no notes, then run the checks.', m('RECALL'), m('JARGON')),
], ([
    'Explain switching to a peer without notes.',
    'Then run the checks in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start with the link light.',
    'Then check the MAC table for the right port.',
    'Give each step a pass sign and a fail note.',
], 'Each switching step needs a pass sign, like “MAC on the expected port”.'), (
    'A recipe says “bake until golden”, not just “bake”. That is the pass sign. It also says “if it browns too fast, cover '
    'with foil”: the fail note. A switching checklist line needs both, or it is only a list of chores.',
    [('Recipe step', 'checklist line'), ('“Until golden”', 'pass sign'), ('“Cover with foil”', 'fail note'),
     ('Another cook using the recipe', 'the next technician')],
    'Recipes rarely change. Switch ports get moved, so the “expected port” on your checklist must come from current records.'),
    ('flow', 'Switching checklist', ['Link light on', 'Speed/duplex OK', 'MAC on port', 'Ping host', 'User confirms']),
    'These five boxes are a full checklist outline. Under each one, add a pass sign and a fail note.',
    'Write your five-line switching checklist with a pass sign and fail note on each line.',
    order('Order the checklist.', ['Link light', 'Speed and duplex', 'MAC on port', 'Ping host', 'User confirms'],
          'Physical, then table, then reach.'), MACT)

_add('2.1', 'network-operations-depth', T, [
    ('At which layer do switches forward?', 'Data link', 'Network layer', 'Application layer',
     'Switches forward frames by MAC at layer 2.', DEVL, DEVL),
    ('Local works, remote fails. Switching or routing?', 'Routing', 'Switching', 'Cabling only',
     'If local hosts work, the switch is doing its job; look at the gateway and routes.', DEVL, m('RECALL')),
    ('In the town story, the post office does what?', 'Local delivery', 'Long-haul flights', 'Passport checks',
     'Local delivery is switching; leaving town is routing.', DEVL, DEVL),
    ('In the chart, ARP belongs to which side?', 'Local delivery', 'Remote routing', 'Firewall policy',
     'ARP finds the MAC of a local host for delivery on the same segment.', UNK, DEVL),
    ('Which comparison tests the switch’s role?', 'Two local hosts', 'Two websites', 'Two printers’ toner',
     'If two hosts on the same VLAN can talk, local switching works.', DEVL, m('RECALL')),
], ([
    'This depth note links layers to switching.',
    'Switches work at layer 2, the data link layer.',
    'ARP finds a local device’s MAC.',
    'Routing is for devices on other networks.',
    'If local works and remote fails, look at routing.',
    'If even local fails, look at the switch and port.',
], 'Compare local and remote to split switching faults from routing faults.'), (
    'A town has a post office for local letters and a sorting hub for letters leaving town. If letters across the street '
    'arrive but letters to the next city do not, the local office is fine. The fault is the route out.',
    [('Local post office', 'switch (layer 2)'), ('Asking the address of a neighbour', 'ARP'), ('Regional hub', 'router'),
     ('Letters to another city', 'remote traffic')],
    'A post office can redirect mail. A switch never changes the IP addresses; it only reads MACs.'),
    ('two', 'Local or remote?', (('Local (switching)', ['ARP finds the MAC', 'Same VLAN', 'MAC table decides']),
                                 ('Remote (routing)', ['Gateway needed', 'Other subnet', 'Route table decides']))),
    'Pick the column using one fact: is the destination on your subnet? Then test the parts in that column.',
    'In the lab, ping a local host and a remote host. Write which layer each result tests and what a failure would mean.',
    sort('Sort the facts.', {'Switching': ['MAC table lookup', 'ARP for a neighbour'], 'Routing': ['Default gateway', 'Route to another subnet']},
         'Local versus remote.'), MACT)

_add('2.1', 'beyond-the-quiz', T, [
    ('What does a switch need to learn a MAC?', 'Traffic from that device', 'A DNS entry for it', 'A static IP address on the device',
     'It learns from the source MAC of frames the device sends.', TBL, m('RECALL')),
    ('A loop forms. What breaks downstream?', 'The whole floor slows', 'Only the one printer near the door', 'Nothing at all',
     'A loop floods frames endlessly and can slow or stop the whole floor.', LOOP, m('RECALL')),
    ('In the echo story, the loop is like?', 'Endless echoes', 'One clear call', 'A locked door',
     'A loop repeats frames forever, like an echo that never fades.', LOOP, UNK),
    ('In the chart, which test splits “port” from “table”?', 'Link light check', 'Reboot all PCs', 'Ask the user again',
     'No link points to the port; link with no MAC points to the device or table.', PHYS, m('PARALLEL')),
    ('When do you escalate a switch fault?', 'No switch access', 'Never, keep trying', 'Before any test',
     'Escalate with evidence once you cannot see or change the switch.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot show every switching fault.',
    'Learn what a switch needs: traffic and link.',
    'Learn what breaks downstream: a loop slows a whole floor.',
    'Build a scenario: one symptom, three causes.',
    'Pick the test that tells them apart.',
    'Know when you need the network team.',
], 'Think in dependencies, design one deciding test, and escalate with evidence.'), (
    'In a canyon, one shout makes an echo that fades. Two facing walls make echoes bounce forever until nobody can hear. '
    'A switching loop is that canyon: frames bounce around, and every desk on the floor suffers.',
    [('Shout', 'broadcast frame'), ('Facing canyon walls', 'two switch links forming a loop'), ('Everyone deafened', 'floor-wide slowdown'),
     ('Park ranger', 'network team with STP control')],
    'An echo fades on its own. A switching loop does not fade; it grows until STP blocks it or someone pulls the cable.'),
    ('two', 'One desk offline: three causes', (('Cause', ['Cable or port', 'Wrong VLAN', 'Port err-disabled']),
                                               ('Deciding test', ['Link light', 'Compare access VLAN', 'show interfaces status']))),
    'Each cause pairs with the one test that proves it. Running all three takes minutes.',
    'Write your own switching scenario: symptom, three causes, the deciding test, and the note you would leave.',
    reveal('Whole floor slow after a cable was added. Suspect?', 'A switching loop; check STP and the new cable.'), MACT)

# ================================================================== 2.2 VLANs and Trunks
m = mc('2.2')
T = 'VLANs and Trunks'
_add('2.2', 'core-concepts', T, [
    ('An access port carries how many VLANs?', 'One', 'Two', 'All configured',
     'An access port belongs to one VLAN; a trunk carries many.', WVF, TALL),
    ('Green link light, but the PC is isolated. Likely?', 'Wrong access VLAN', 'A broken cable end', 'A dead power supply',
     'Link is up, so the cable works; a wrong VLAN isolates the desk.', WVF, PHYS),
    ('In the hotel story, a wrong floor is what?', 'A wrong VLAN', 'A broken lift', 'A lost key card',
     'The lift works (link up) but takes you to the wrong floor (VLAN).', WVF, PHYS),
    ('In the chart, a trunk link does what?', 'Carries many VLANs', 'Carries one VLAN', 'Blocks every VLAN on the switch',
     'Trunks tag frames so many VLANs share one link.', TALL, 'MC-R3-NO2-8021Q'),
    ('Two VLANs need to talk. What do they need?', 'A layer-3 gateway', 'A longer cable run', 'A second trunk link',
     'Different VLANs need routing (SVI or router) to talk.', VGW, VGW),
], ([
    'A VLAN splits one switch into separate networks.',
    'An access port is in one VLAN.',
    'A trunk carries many VLANs between switches.',
    'A green light only proves the cable works.',
    'A desk on the wrong VLAN is cut off.',
    'Two VLANs need a router to talk.',
], 'Green light plus wrong VLAN equals isolation; check the access VLAN early.'), (
    'A hotel has one lift and many floors. Each guest’s key card works on one floor. The lift may work perfectly, but if '
    'your card sends you to the wrong floor, you cannot reach your room. The staff lift that stops everywhere is the trunk.',
    [('Floor', 'VLAN'), ('Guest key card', 'access port VLAN setting'), ('Staff lift to all floors', 'trunk link'),
     ('Lift working', 'link light green')],
    'A guest can walk the stairs to the right floor. A PC on the wrong VLAN cannot reach other VLANs without a router.'),
    ('two', 'Access port versus trunk', (('Access port', ['One VLAN', 'To a PC or printer', 'Frames untagged']),
                                         ('Trunk', ['Many VLANs', 'Switch to switch', 'Frames tagged 802.1Q']))),
    'Each row compares one property. Mixing the two columns is the most common VLAN mistake.',
    'In the lab, compare the access VLAN on the user’s port with a working neighbour. Write both VLAN numbers.',
    sort('Sort each fact.', {'Access port': ['One VLAN', 'Plugs into a PC'], 'Trunk': ['802.1Q tags', 'Switch to switch']},
         'Know which kind of port you are looking at.'), VACC)

_add('2.2', 'incident-application', T, [
    ('One desk isolated, neighbours fine. First test?', 'Compare the VLAN', 'Reimage the PC first', 'Reboot the whole switch',
     'Compare the desk’s access VLAN with a neighbour’s.', WVF, m('PARALLEL')),
    ('Link light is green. Do you record it?', 'Yes, rules out cable', 'No, it is not useful', 'Only if red later',
     'A green link is evidence that the cable is fine.', m('NEG'), m('NEG')),
    ('In the courier story, the wrong depot is?', 'The wrong VLAN', 'A broken van', 'A bad street address',
     'Parcels reach the wrong depot even though the van works.', WVF, PHYS),
    ('In the timeline, what proved the cause?', 'VLAN 30 vs 20', 'A user email', 'A green light',
     'The VLAN mismatch with the neighbour proved the cause.', WVF, PHYS),
    ('Good status line?', 'One desk on wrong VLAN; fixing', 'The whole network is down for all', 'Fixed, no idea why',
     'Accurate and calm, with scope and next step.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking VLAN incident.',
    'At 11:00 one desk cannot reach the department server.',
    'Neighbours on the same switch are fine.',
    'The link light is green.',
    'The desk’s port is in VLAN 30. Neighbours are in VLAN 20.',
    'You record both and ask for the port change.',
    'You tell the user it is a setting, not their PC.',
], 'One desk isolated with a green light: compare VLANs and record the evidence.'), (
    'A courier delivers to the right street but the wrong depot sorted the parcel. The van and roads are fine; the label '
    'sent it elsewhere. A desk on VLAN 30 instead of 20 is that parcel: physically connected, logically lost.',
    [('Depot label', 'access VLAN'), ('Van and roads', 'cable and link'), ('Neighbour’s correct label', 'working neighbour’s VLAN'),
     ('Relabelling', 'changing the access VLAN')],
    'A courier can phone you. A PC on the wrong VLAN just gets an address from the wrong subnet or none at all.'),
    ('flow', 'Isolated desk timeline', ['11:00 desk isolated', '11:03 link green', '11:05 VLAN 30 vs 20', '11:08 port change',
                                        '11:10 user verified'], 2),
    'The red box marks the proof. The green-link test before it was still recorded because it rules out the cable.',
    'Write a timeline for one isolated desk with a green light, ending in user verification.',
    order('Order the steps.', ['Confirm one desk only', 'Check link light', 'Compare VLAN with neighbour', 'Change one port', 'Verify with user'],
          'Scope, physical, VLAN, fix, verify.'), VACC)

_add('2.2', 'standard-of-work', T, [
    ('Why note “neighbour on VLAN 20, works”?', 'It is the reference', 'It wastes space', 'It is not needed in a ticket',
     'The working neighbour is the comparison that proves the fault.', m('NEG'), m('NEG')),
    ('Changing everyone’s VLAN to fix one desk is…', 'A risky parallel change', 'A neat and tidy fix for everyone', 'Normal practice',
     'It changes many ports at once and can break many users.', m('PARALLEL'), WVF),
    ('In the tailor story, one seam at a time means?', 'One port change', 'Recut the suit', 'Skip the fitting',
     'A tailor fixes one seam, then fits again.', m('PARALLEL'), m('NEG')),
    ('In the chart, which belongs under “avoid”?', 'Change all ports', 'Note VLAN seen', 'Retest the one desk only',
     'Bulk VLAN changes hit everyone.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'Gi0/12 VLAN 30→20 11:08', 'Fixed VLANs', 'Changed some VLAN stuff earlier',
     'Port, change, time: a trustworthy line.', m('NEG'), m('CHECKLIST')),
], ([
    'VLAN work has two habits.',
    'Write down what passed, like the neighbour’s VLAN.',
    'That is your reference.',
    'Change one port at a time.',
    'Never move everyone’s VLAN to fix one desk.',
    'That can cut off a whole team.',
], 'Keep the reference, change one port, and write port, change and time.'), (
    'A tailor fixing a suit unpicks one seam, fits it and notes the result. Recutting the whole suit for one loose seam '
    'risks ruining it. Moving every port’s VLAN for one desk is recutting the whole suit.',
    [('One seam', 'one access port'), ('Fitting', 'retest with the user'), ('Recutting the suit', 'changing every VLAN'),
     ('Tailor’s notes', 'ticket lines')],
    'A tailor’s client is one person. A switch serves many people, so a bulk change has many victims.'),
    ('two', 'VLAN standard of work', (('Do', ['Note neighbour’s VLAN', 'Change the one port', 'Retest the one desk']),
                                      ('Avoid', ['Skipping the reference', 'Changing all ports', 'No time on notes']))),
    'Each row is a habit and its opposite.',
    'Rewrite “fixed VLANs” as a standard line with the port, old and new VLAN, time and retest.',
    reveal('Rewrite: “fixed VLANs”.', 'Gi0/12 access VLAN 30→20 at 11:08; server reachable 11:10, user confirmed.'), VACC)

_add('2.2', 'practice-standard-for-this-lesson', T, [
    ('Key line on a VLAN checklist?', 'Compare with neighbour', 'Reboot the whole access switch', 'Reinstall the NIC',
     'Comparing with a working neighbour is the strongest VLAN test.', m('CHECKLIST'), m('PARALLEL')),
    ('Pass sign for “check VLAN”?', 'Matches the team’s VLAN', 'Any VLAN number', 'A long config dump from the switch',
     'Good means the port is in the VLAN the team uses.', WVF, m('CHECKLIST')),
    ('In the map story, the legend is like?', 'The pass sign', 'The road itself', 'The car colour',
     'A legend tells you what “good” looks like on the map.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what comes after the VLAN check?', 'Check the IP subnet', 'Reboot the PC and try again', 'Call the ISP',
     'The address should then match the VLAN’s subnet.', m('CHECKLIST'), m('PARALLEL')),
    ('Mastery shows how?', 'Teach it without notes', 'Recite VLAN numbers', 'Read the vendor guide to them',
     'Teach VLANs plainly to a peer, then run the checks.', m('RECALL'), m('JARGON')),
], ([
    'Explain VLANs and trunks without notes.',
    'Then run the checks in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Include a neighbour comparison.',
    'Each step gets a pass sign.',
    'Each step gets a note for when it fails.',
], 'A VLAN checklist must compare against a working neighbour.'), (
    'A map without a legend is hard to use; you do not know what the symbols mean. A checklist without pass signs is the '
    'same. “Check VLAN” means nothing until you write “matches VLAN 20 like the neighbour”.',
    [('Map', 'checklist'), ('Legend', 'pass signs'), ('Known landmark', 'working neighbour'), ('“You are lost” note', 'fail note')],
    'Maps are printed once. VLAN plans change, so your pass sign must come from the current VLAN plan.'),
    ('flow', 'VLAN checklist', ['Link light', 'Access VLAN', 'Neighbour VLAN', 'IP in VLAN subnet', 'Reach server']),
    'These boxes outline the checklist. The third box is the comparison that most beginners skip.',
    'Write a five-line VLAN checklist with a pass sign and fail note per line.',
    order('Order the checklist.', ['Link light', 'Access VLAN', 'Compare neighbour', 'IP subnet', 'Reach server'],
          'Physical, VLAN, address, reach.'), VACC)

_add('2.2', 'network-operations-depth', T, [
    ('What does a VLAN segment?', 'A broadcast domain', 'A power circuit in the building', 'A Wi-Fi channel',
     'Each VLAN is its own broadcast domain.', WVF, DEVL),
    ('One desk “network down” with a green light. Layer?', 'Data link (VLAN)', 'Physical cable', 'Application only',
     'Link is up, so look at layer 2: VLAN assignment.', WVF, DEVL),
    ('In the office story, separate floors are?', 'Separate VLANs', 'Separate cables', 'Separate users',
     'Each floor is its own space, like a VLAN broadcast domain.', WVF, DEVL),
    ('In the chart, which side is policy?', 'VLAN ACL', 'Bad cable', 'No link',
     'An ACL between VLANs is policy; a bad cable is reachability.', VGW, PHYS),
    ('Which test helps here?', 'Same-VLAN vs other', 'Morning vs evening', 'PC vs Mac',
     'Comparing same-VLAN and cross-VLAN reachability shows where the gateway or ACL steps in.', VGW, m('RECALL')),
], ([
    'This depth note links layers to VLANs.',
    'A VLAN is a separate broadcast domain.',
    'A wrong access port can look like “network down”.',
    'The link light can be green the whole time.',
    'Crossing VLANs needs a router or SVI.',
    'Test same-VLAN first, then cross-VLAN.',
], 'Name the layer: VLAN faults live at layer 2, even with a green light.'), (
    'An office building has floors with their own lobby announcements. You only hear your floor’s announcements. To '
    'reach another floor you take the lift through reception. VLANs are floors; the router is reception.',
    [('Floor announcements', 'broadcasts in a VLAN'), ('Your floor', 'your access VLAN'), ('Reception desk', 'router or SVI'),
     ('Security at reception', 'ACL between VLANs')],
    'Floors in a building are fixed. VLANs are software, so one typo moves a desk to another “floor” instantly.'),
    ('two', 'Same VLAN or across VLANs?', (('Same VLAN', ['ARP and switch', 'No gateway needed', 'Fails: port or VLAN']),
                                           ('Across VLANs', ['Router or SVI', 'Gateway needed', 'Fails: route or ACL']))),
    'Pick the column first; the bottom row then tells you where to look.',
    'In the lab, test a same-VLAN host and a cross-VLAN host. Label the layer and name policy or reachability.',
    sort('Sort the faults.', {'Layer 2': ['Wrong access VLAN', 'VLAN not on trunk'], 'Layer 3 or policy': ['Missing SVI', 'ACL between VLANs']},
         'Layer names guide the next test.'), VACC)

_add('2.2', 'beyond-the-quiz', T, [
    ('What does a VLAN need on a trunk to cross switches?', 'Be allowed on it', 'A brand new IP address scheme', 'A faster cable',
     'The VLAN must be in the trunk’s allowed list.', TALL, m('RECALL')),
    ('VLAN removed from a trunk. What breaks?', 'That VLAN beyond it', 'Every VLAN everywhere', 'Only one PC',
     'Only the removed VLAN stops crossing that trunk.', TALL, m('RECALL')),
    ('In the bridge story, the guest list is?', 'The allowed list', 'The bridge itself', 'The river',
     'Only listed cars cross, like allowed VLANs on a trunk.', TALL, NAT),
    ('In the chart, what splits “port” from “trunk” faults?', 'Scope of users', 'Desk colour', 'User’s job title',
     'One desk points to its port; a whole VLAN on far switches points to the trunk.', m('ESCALATE'), m('RECALL')),
    ('When do you escalate a trunk issue?', 'No access to core', 'Never escalate it', 'Before any check',
     'Escalate with evidence when the trunk is on a switch you cannot change.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every VLAN fault.',
    'Know what a VLAN needs: a port, a trunk, a gateway.',
    'Know what breaks when one is missing.',
    'Build a scenario with three causes.',
    'Find the test that splits them.',
    'Know when to call the core team.',
], 'Scope tells you port versus trunk; evidence gets the right team moving.'), (
    'A toll bridge has a list of approved vehicles. A car not on the list cannot cross, even though the bridge is open '
    'for everyone else. A trunk’s allowed VLAN list works like that list.',
    [('Toll bridge', 'trunk link'), ('Approved list', 'allowed VLANs'), ('Car not on the list', 'pruned VLAN'),
     ('Bridge authority', 'core network team')],
    'A driver can see the toll booth. Frames from a missing VLAN are dropped with no message.'),
    ('two', 'VLAN fault: three causes', (('Cause', ['Wrong access VLAN', 'VLAN not on trunk', 'No SVI or gateway']),
                                         ('Deciding test', ['Compare one neighbour', 'Same VLAN, far switch?', 'Ping the gateway']))),
    'Each cause has a test. Running them in this order narrows from one port to the whole VLAN.',
    'Write your own VLAN scenario: symptom, three causes, deciding test, and the note for the core team.',
    reveal('All VLAN 40 users on switch B fail; switch A fine. Suspect?', 'VLAN 40 not allowed on the A–B trunk.'), VACC)

# ================================================================== 2.3 Copper Fiber Cabling
m = mc('2.3')
T = 'Copper Fiber Cabling'
_add('2.3', 'core-concepts', T, [
    ('A link drops on and off. Common cause?', 'Bad termination', 'Wrong DNS server', 'A full DHCP scope',
     'Intermittent links are often poor terminations.', PHYS, m('RECALL')),
    ('What do you test before replacing a switch?', 'The cable', 'The browser', 'The user account',
     'Test cables first; they fail far more often than switches.', PHYS, TOOL),
    ('In the pipe story, a leak at a joint is?', 'A bad termination', 'A full water tank upstairs', 'A wrong tap',
     'Joints leak like badly crimped connectors.', PHYS, PHYS),
    ('In the chart, copper’s channel limit is?', '100 m', '500 m', '2 km',
     'Twisted-pair Ethernet is specified to 100 m.', CLEN, CLEN),
    ('A fibre optic “fits” but the link is dark. Likely?', 'Wrong optic type', 'Wrong VLAN set on the port', 'Bad DNS record',
     'Fibre type, wavelength and optic must match, not just the connector.', OPT, FMODE),
], ([
    'Test cables before you replace switches.',
    'Most intermittent faults are terminations.',
    'A termination is how the cable meets its plug.',
    'Copper Ethernet runs up to 100 metres.',
    'Fibre needs matching optics and fibre type.',
    'A connector that fits is not proof of a match.',
], 'Physical first: test the cable and its ends before blaming the switch.'), (
    'A house with damp walls usually has a leaking joint, not a broken boiler. A plumber checks joints first because they '
    'fail most. Network cables are pipes: the ends where they meet plugs fail most often.',
    [('Pipe', 'cable run'), ('Joint', 'termination (plug or jack)'), ('Boiler', 'switch'), ('Pressure test', 'cable tester')],
    'A leak drips where you can see it. A bad termination may pass at rest and fail when the cable moves.'),
    ('two', 'Copper versus fibre', (('Copper', ['Up to 100 m', 'Crimped RJ45 ends', 'Tester: wire map']),
                                    ('Fibre', ['Kilometres possible', 'Optics must match', 'Tester: light meter']))),
    'Each row shows the limit, the weak point and the right tool. Using the wrong tool proves nothing.',
    'In the cable bench lab, pick the right cable and tester for each link and write the result.',
    sort('Sort each fact.', {'Copper': ['100 m channel', 'RJ45 termination'], 'Fibre': ['Matching wavelength', 'Light meter test']},
         'Different media, different checks.'), CAB)

_add('2.3', 'incident-application', T, [
    ('A desk drops off when the chair moves. First test?', 'Test the cable', 'Replace the switch', 'Reinstall Windows',
     'Movement-linked drops point to the cable or its ends.', PHYS, m('PARALLEL')),
    ('Tester shows pair 3 open. Do you write it?', 'Yes, with time', 'No, just fix it', 'Only if asked',
     'The tester result is the proof; record it.', m('NEG'), m('NEG')),
    ('In the hose story, the kink is?', 'The cable fault', 'The tap', 'The whole garden outside',
     'A kinked hose drops flow when moved, like a damaged cable.', PHYS, PHYS),
    ('In the timeline, what proved the cause?', 'Tester: pair 3 open', 'The user’s first complaint email', 'Switch reboot',
     'The tester result on pair 3 proved the termination fault.', PHYS, m('PARALLEL')),
    ('Good status line?', 'Cable fault; patching now', 'The switch is slowly dying', 'Who knows',
     'Accurate and calm with the next step.', m('STATUS'), m('STATUS')),
], ([
    'Here is a real-looking cabling incident.',
    'At 13:00 a desk drops when the chair moves.',
    'Link lights flicker.',
    'You test the patch cable. Pair 3 is open.',
    'You record the result with the time.',
    'You swap the patch cable and retest.',
    'You tell the user it was a cable.',
], 'Test the cable, record the tester result, then make one swap.'), (
    'A garden hose kinks behind a chair leg. Water stops whenever someone moves the chair. Replacing the tap would not '
    'help. A desk cable trapped under a chair leg drops the link in exactly the same way.',
    [('Hose', 'patch cable'), ('Kink', 'damaged pair or end'), ('Tap', 'switch port'), ('Moving the chair', 'trigger for the drop')],
    'You can see a kinked hose. A damaged pair can look perfect, so you need the tester.'),
    ('flow', 'Cabling timeline', ['13:00 drops reported', '13:04 lights flicker', '13:06 tester: pair 3', '13:08 swap patch',
                                  '13:10 stable link'], 2),
    'The red box is the proof. Only after it does the swap happen, so the fix is explained.',
    'Write a five-line timeline for a link that drops when a cable moves.',
    order('Order the steps.', ['Confirm the trigger', 'Check link lights', 'Test the cable', 'Swap one cable', 'Verify stable'],
          'Prove, then swap.'), CAB)

_add('2.3', 'standard-of-work', T, [
    ('Tester passed on the wall run. Record it?', 'Yes, rules it out', 'No, nothing found', 'Only on failure',
     'A passed wall run moves suspicion to the patch lead or port.', m('NEG'), m('NEG')),
    ('Swapping patch lead, port and NIC together is…', 'Untracked change', 'Very efficient troubleshooting', 'Best practice',
     'Three swaps at once hide which part was bad.', m('PARALLEL'), m('PARALLEL')),
    ('In the electrician story, one fuse at a time means?', 'One swap at a time', 'Pull every fuse in the box', 'Skip the notes',
     'An electrician tests one circuit at a time.', m('PARALLEL'), m('NEG')),
    ('In the chart, what goes under “avoid”?', 'Swap three parts', 'Note tester result', 'Retest after swap',
     'Multiple swaps at once lose the cause.', m('PARALLEL'), m('NEG')),
    ('Which line meets the standard?', 'Patch swapped 13:08, stable', 'Changed some stuff, all good now', 'Done',
     'Change, time and result.', m('NEG'), m('CHECKLIST')),
], ([
    'Cabling work has two habits.',
    'Write down passed tests, like a good wall run.',
    'That moves attention to the next part.',
    'Swap one part at a time.',
    'Never swap lead, port and NIC together.',
    'You would never know which one was bad.',
], 'Note passed cable tests and swap one part at a time.'), (
    'An electrician chasing a tripping circuit tests one fuse and one socket at a time and notes each. Pulling every fuse '
    'and swapping every socket might fix it, but the cause stays hidden and returns later.',
    [('One fuse', 'one cable part'), ('Socket test passed', 'wall run passed'), ('Pulling every fuse', 'swapping everything'),
     ('Electrician’s log', 'ticket notes')],
    'An electrician’s fault can start a fire. A network fault is less dangerous, but hidden causes still come back.'),
    ('two', 'Cabling standard of work', (('Do', ['Note wall run passed', 'Swap the patch lead only', 'Retest the link']),
                                         ('Avoid', ['Skipping passed tests', 'Swapping three parts', 'No retest']))),
    'Each row is a habit and the mistake it prevents.',
    'Rewrite “changed stuff, works” as a standard line naming the part, the time and the retest.',
    reveal('Rewrite: “changed stuff, works”.', '13:08 replaced desk patch lead (pair 3 open); link stable 13:10–13:25.'), CAB)

_add('2.3', 'practice-standard-for-this-lesson', T, [
    ('First line of a cabling checklist?', 'Look at link lights', 'Order a new switch straight away', 'Reimage the PC',
     'Start with what the lights say, then test.', m('CHECKLIST'), m('PARALLEL')),
    ('Pass sign for “wire map test”?', 'All 8 pins correct', 'The tester beeps once at the end', 'Cable looks new',
     'Good means every pin maps correctly with no opens or shorts.', TOOL, m('CHECKLIST')),
    ('In the doctor story, a normal reading is?', 'The pass sign', 'The doctor’s coat', 'The waiting room',
     'A normal reading is a pass sign; an abnormal one gets a note.', m('CHECKLIST'), m('RECALL')),
    ('In the flow, what follows “wire map OK”?', 'Check length', 'Call the ISP', 'Change VLAN',
     'After wire map, check length against the 100 m limit.', CLEN, m('PARALLEL')),
    ('Mastery shows how?', 'Teach it without notes', 'Recite all the cable colours', 'Read the spec sheet',
     'Explain cabling plainly, then test a real run.', m('RECALL'), m('JARGON')),
], ([
    'Explain cabling to a peer without notes.',
    'Then test a real cable in the lab.',
    'Write a checklist of 5 to 9 steps.',
    'Start with the link lights.',
    'Each step gets a pass sign, like “all 8 pins correct”.',
    'Each step gets a note for when it fails.',
], 'A cabling checklist names the tool and the pass sign for each step.'), (
    'A doctor’s check-up has a list: blood pressure, pulse, temperature. Each has a normal range. A reading outside it gets '
    'written down. Your cabling checklist has normal ranges too: pins correct, length under 100 m.',
    [('Check-up list', 'cabling checklist'), ('Normal range', 'pass sign'), ('Abnormal reading note', 'fail note'),
     ('Right instrument', 'right tester for the medium')],
    'A doctor uses the same instruments on everyone. Copper and fibre need different testers.'),
    ('flow', 'Cabling checklist', ['Link lights', 'Wire map', 'Length < 100 m', 'Swap one part', 'Retest link']),
    'These boxes outline a full checklist. Add a pass sign and fail note under each.',
    'Write a five-line cabling checklist with the tool, pass sign and fail note per line.',
    order('Order the checklist.', ['Link lights', 'Wire map', 'Length check', 'Swap one part', 'Retest'],
          'Look, test, measure, change, verify.'), CAB)

_add('2.3', 'network-operations-depth', T, [
    ('Cabling faults live at which layer?', 'Physical', 'Network layer', 'Application layer',
     'Cables, connectors and light levels are layer 1.', PHYS, DEVL),
    ('Rising CRC errors on a port point to what?', 'A physical fault', 'Congestion on the uplink only', 'A DNS problem',
     'CRC errors are damaged frames, usually physical.', PHYS, TOOL),
    ('In the road story, potholes are?', 'Physical faults', 'The traffic rules in town', 'Route signs',
     'Potholes damage what passes over them, like bad cable damages frames.', PHYS, DEVL),
    ('In the chart, PoE budget faults cause?', 'Random reboots', 'Wrong VLANs', 'DNS lookup failures on clients',
     'Devices exceeding the PoE budget lose power and reboot.', POE, PHYS),
    ('Which test splits cable from switch?', 'Known-good cable', 'Reboot the whole switch stack', 'New VLAN',
     'A known-good cable swap separates cable faults from the port.', TOOL, m('PARALLEL')),
], ([
    'This depth note links layers to cabling.',
    'Cables live at layer 1, the physical layer.',
    'CRC errors usually mean a physical problem.',
    'PoE budgets can make phones and APs reboot.',
    'Test with a known-good cable to split cable from port.',
    'Name the layer for each test.',
], 'Physical-layer evidence comes from testers, counters and a known-good swap.'), (
    'A road with potholes damages every car that drives over it, however good the driver. Frames crossing a damaged '
    'cable are the cars; CRC errors are the dents. Fixing the traffic lights will not fill the potholes.',
    [('Potholes', 'damaged cable or ends'), ('Dented cars', 'CRC errors'), ('Traffic lights', 'logical settings'),
     ('Road crew', 'cable test and repair')],
    'A road crew can see potholes. CRC counters are your only view, so you must read them before and after.'),
    ('two', 'Physical faults and their signs', (('Fault', ['Bad termination', 'Over 100 m', 'PoE over budget']),
                                                ('Sign', ['CRC errors, flaps', 'Errors, low speed', 'Device reboots']))),
    'Each row pairs a physical fault with what you see. None of these is fixed by a VLAN or DNS change.',
    'In the cable bench lab, note the tester you used for each link and the layer it tests.',
    sort('Sort the signs.', {'Physical': ['CRC errors', 'Link flaps'], 'Not physical': ['Wrong VLAN', 'DNS fails']},
         'Layer 1 first.'), CAB)

_add('2.3', 'beyond-the-quiz', T, [
    ('What does a fibre link need besides a fitting plug?', 'Matching optics', 'A DNS name', 'A static IP on both ends',
     'Fibre mode and wavelength must match on both ends.', OPT, FMODE),
    ('A trunk cable fails. What breaks downstream?', 'All VLANs on it', 'Only the one desk at the end', 'Nothing much',
     'A trunk carries many VLANs, so all of them lose that path.', TALL, m('RECALL')),
    ('In the bridge story, a cracked span affects?', 'Every crossing car', 'Only one car on the far side', 'The river',
     'A shared path failing hits everyone who uses it.', m('RECALL'), m('RECALL')),
    ('In the chart, which test splits pins from length?', 'Certifier report', 'A user survey about the speed', 'Reboot',
     'A certifier reports wire map and length separately.', TOOL, m('PARALLEL')),
    ('When do you escalate a cabling fault?', 'Run is in the wall', 'Never escalate, just keep trying', 'Before testing',
     'In-wall runs need facilities or cabling contractors.', m('ESCALATE'), m('ESCALATE')),
], ([
    'A quiz cannot cover every cable fault.',
    'Know what a link needs: good ends, length, matched optics.',
    'Know what breaks downstream: a trunk cable takes many VLANs.',
    'Build a scenario with three causes.',
    'Pick the test that splits them.',
    'Know when to call cabling contractors.',
], 'Map dependencies, test to split causes, escalate in-wall faults.'), (
    'A bridge carries every car into town. A crack in one span stops all traffic, while a pothole on a side street only '
    'bothers one house. A trunk cable is that bridge; a desk patch lead is the side street.',
    [('Bridge span', 'trunk or uplink cable'), ('Side street', 'desk patch lead'), ('All traffic stopped', 'many VLANs down'),
     ('Bridge engineers', 'cabling contractor')],
    'A bridge crack is visible. A failing fibre may show only rising errors until it dies.'),
    ('two', 'Link down: three causes', (('Cause', ['Bad patch lead', 'Run over 100 m', 'Optic mismatch']),
                                        ('Deciding test', ['Known-good swap', 'Certifier length', 'Check optic type']))),
    'Each cause has a test that proves it. Run them before calling anyone.',
    'Write your own cabling scenario: symptom, three causes, deciding test, and who you would escalate to.',
    reveal('New fibre fits but stays dark. First check?', 'Optic type and fibre mode match on both ends.'), CAB)

# ================================================================== 2.4 Capstone — Isolated User
m = mc('2.4')
T = 'Capstone — Isolated User'
_add('2.4', 'the-scenario', T, [
    ('One user cannot see the server; neighbours can. Scope?', 'One port or PC', 'The whole server', 'The internet link',
     'Neighbours work, so shared parts are fine.', m('ESCALATE'), DEVL),
    ('First comparison to make?', 'With a neighbour', 'With another site', 'With last year',
     'A working neighbour is the best reference.', WVF, m('RECALL')),
    ('In the apartment story, one dark flat means?', 'A local fault', 'A city blackout', 'A storm',
     'One dark flat with lit neighbours points to that flat’s fuse.', m('ESCALATE'), DEVL),
    ('In the chart, which check comes after link?', 'IP and VLAN', 'Reimage the PC from scratch', 'Call ISP',
     'With link up, compare IP and VLAN with the neighbour.', WVF, m('PARALLEL')),
    ('No switch access. What do you send?', 'Evidence package', 'An angry email to the switch team', 'Nothing',
     'Send link, IP and VLAN results to the switch team.', m('ESCALATE'), m('JARGON')),
], ([
    'One user cannot see the department server.',
    'The neighbours can.',
    'So the server and switch mostly work.',
    'Compare the user with a neighbour.',
    'Check link, then IP and VLAN.',
    'Escalate with evidence if you cannot see the switch.',
], 'One isolated user is a local problem: compare with a neighbour.'), (
    'In an apartment block, one flat goes dark while the rest have power. Nobody calls the power company. You check that '
    'flat’s fuse box and compare it with the neighbour’s.',
    [('Dark flat', 'isolated user'), ('Lit neighbours', 'working desks'), ('Fuse box', 'port, IP and VLAN'),
     ('Building manager', 'switch team')],
    'Flats share wiring you can see. Desks share a switch you may not have access to, so you collect evidence first.'),
    ('flow', 'Isolated user path', ['Peer works', 'Link OK', 'IP compared', 'VLAN compared', 'Escalate or fix']),
    'Each box narrows the fault. The comparisons in the middle are what the capstone checks.',
    'In the lab, compare the user’s access VLAN with a neighbour’s and write both.',
    order('Order the checks.', ['Confirm peer works', 'Check link', 'Compare IP', 'Compare VLAN', 'Fix or escalate'],
          'Narrow before you act.'), VACC)

_add('2.4', 'your-turn-scaffolded-checklist', T, [
    ('What does “peer works” prove?', 'Shared parts OK', 'User is wrong', 'The server itself is down',
     'A working peer clears the server and core.', m('NEG'), m('JARGON')),
    ('“Link OK” rules out what?', 'Cable and port', 'The DNS server settings', 'The VLAN',
     'Link up clears the physical path, not VLAN.', PHYS, WVF),
    ('In the forms story, a blank box means?', 'Unfinished work', 'Not needed for this ticket', 'Done',
     'Do not skip lines: a blank box is unfinished.', m('CHECKLIST'), m('CHECKLIST')),
    ('In the chart, the last line needs what?', 'Escalation evidence', 'A written apology to the user', 'A reboot',
     'Without switch access, the last line is the evidence you hand over.', m('ESCALATE'), m('PARALLEL')),
    ('Which entry fills “IP/VLAN compared”?', '10.20.30.x vs 10.20.20.x', 'Looks fine to me, same as the rest', 'Same',
     'Write both values so the difference is visible.', WVF, m('NEG')),
], ([
    'Fill in each line on paper or in the ticket.',
    'Do not skip lines.',
    'Peer works.',
    'Link OK.',
    'IP and VLAN compared with the peer.',
    'Escalation evidence if you have no switch access.',
], 'Four lines, all filled, with real values.'), (
    'A passport form has a box for every detail. Leave one blank and it comes back. The checklist is that form: every line '
    'filled with a value, or the next person must start again.',
    [('Form box', 'checklist line'), ('Blank box', 'skipped test'), ('Real value written', 'IP and VLAN shown'),
     ('Form sent to office', 'escalation package')],
    'A form office tells you what is missing. A colleague may not notice, so you check your own blanks.'),
    ('two', 'Checklist lines filled in', (('Line', ['Peer works', 'Link OK', 'IP/VLAN compared', 'Escalation evidence']),
                                          ('Example', ['Desk 14 OK 11:02', 'Green, 1 Gb 11:03', 'VLAN 30 vs 20', 'Port Gi0/12, VLAN 30']))),
    'The right column shows good entries. Each one has a value, not just a tick.',
    'Fill the four lines for your lab run with real values and times.',
    reveal('Fill “IP/VLAN compared” for a mismatch.', 'User 10.20.30.15 VLAN 30; peer 10.20.20.22 VLAN 20 — mismatch.'), VACC)

_add('2.4', 'common-beginner-mistakes', T, [
    ('Why not reimage the PC first?', 'It skips network tests', 'It is too quick', 'It is always the right first move',
     'Reimaging wastes hours when the fault is a port VLAN.', m('PARALLEL'), m('RECALL')),
    ('Why not change everyone’s VLAN?', 'It breaks others', 'It is too small a change to matter', 'It is policy',
     'A bulk VLAN change cuts off working users.', m('PARALLEL'), WVF),
    ('In the car story, a new engine for a flat tyre is?', 'Reimaging first', 'Checking the tyre', 'Reading the manual',
     'Big work for a small, local fault.', m('PARALLEL'), m('RECALL')),
    ('In the chart, the fix for “reimage first” is?', 'Compare with peer', 'Reboot the department server', 'Call ISP',
     'A peer comparison finds the real difference fast.', WVF, m('PARALLEL')),
    ('Which entry avoids both mistakes?', 'Gi0/12 30→20 only', 'Reimaged PC', 'All ports VLAN 20',
     'One port changed, nothing else.', m('PARALLEL'), WVF),
], ([
    'Two mistakes are common here.',
    'First, reimaging the PC before testing the network.',
    'Second, changing everyone’s VLAN to fix one desk.',
    'Both are big changes for a small fault.',
    'Compare with a neighbour instead.',
    'Change only the one port.',
], 'Small fault, small fix: compare first, change one port.'), (
    'Buying a new engine for a flat tyre is expensive and does not help. Repainting every car in the street because one '
    'is scratched is worse. Reimaging or bulk VLAN changes are those mistakes.',
    [('Flat tyre', 'wrong access VLAN'), ('New engine', 'reimaging the PC'), ('Repainting the street', 'changing every VLAN'),
     ('Pump up the tyre', 'fix one port')],
    'A mechanic sees the flat tyre. You must prove the VLAN mismatch with a comparison.'),
    ('two', 'Mistake and fix', (('Mistake', ['Reimage the PC first', 'Change everyone’s VLAN']),
                                ('Fix', ['Compare with a neighbour', 'Change the one port']))),
    'Each row pairs a beginner mistake with the habit that replaces it.',
    'Rewrite “reimaged PC, still broken” into a better first step with a comparison.',
    sort('Sort each action.', {'Mistake': ['Reimage first', 'Bulk VLAN change'], 'Good': ['Compare neighbour', 'One port change']},
         'Smallest change that fixes it.'), VACC)

_add('2.4', 'check-your-understanding', T, [
    ('What starts the two-minute explanation?', 'The symptom', 'The fix', 'Your opinion',
     'Symptom first, then checks, cause and verification.', m('RECALL'), m('JARGON')),
    ('What proved the cause here?', 'VLAN mismatch', 'The user’s own guess about it', 'A reboot',
     'The VLAN comparison with a neighbour proved it.', WVF, m('PARALLEL')),
    ('In the weather story, the forecast check is?', 'Verification', 'The original symptom report', 'The guess',
     'Checking the forecast came true is like verifying the fix.', m('CHECKLIST'), m('RECALL')),
    ('In the chart, the last box is?', 'User verified', 'Ticket closed', 'Blame assigned',
     'The user reaching the server is the verification.', m('CHECKLIST'), m('NEG')),
    ('Can’t explain it in two minutes. Next?', 'Re-run the demo', 'Skip ahead to the next ticket', 'Guess',
     'Re-run the live steps before moving on.', m('RECALL'), m('RECALL')),
], ([
    'Explain the ticket to a peer in two minutes.',
    'Symptom: one user cannot reach the server.',
    'Checks: peer, link, VLAN.',
    'Cause: wrong access VLAN on the port.',
    'Verification: user reaches the server.',
    'If you cannot say this, re-run the demo.',
], 'Symptom, three checks, cause, verification: in two minutes.'), (
    'A weather presenter explains a storm: what was seen, three readings, why it formed, and whether the forecast came '
    'true. If they cannot, they review the charts. Your ticket explanation follows the same four beats.',
    [('What was seen', 'symptom'), ('Three readings', 'first three checks'), ('Why it formed', 'cause'),
     ('Forecast came true', 'user verified')],
    'Weather cannot be re-run. Your demo can, so if you stumble, run it again.'),
    ('flow', 'Two-minute explanation', ['Symptom', 'Three checks', 'Cause proved', 'User verified']),
    'Four boxes, four beats, read from left to right. If any box is blank when you practise, re-run that part of the demonstration before you explain it again.',
    'Explain your isolated-user ticket to a peer in two minutes using the four boxes.',
    order('Order the explanation.', ['Symptom', 'Three checks', 'Cause proved', 'User verified'], 'Story order.'), VACC)
