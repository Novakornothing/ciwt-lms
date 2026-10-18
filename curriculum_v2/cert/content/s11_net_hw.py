"""A+ Core 1 2.5 (networking hardware) and 2.8 (networking tools) — ITSUP 5.3."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-soho-path', 'From the provider’s line to the desk',
    ['Provider line:\ncoax / DSL / fibre', 'Cable modem, DSL\nmodem or ONT', 'Router +\nfirewall', 'Switch (PoE)\n+ patch panel', 'Wall jack → NIC;\nAP on PoE'],
    'Five boxes in a chain. The provider’s line arrives as coaxial cable, a telephone pair for DSL, or fibre. It terminates '
    'on a cable modem, a DSL modem or an optical network terminal (ONT). The router and firewall connect to that and '
    'route between the internet and the LAN. A switch, often supplying Power over Ethernet, connects through a patch panel '
    'to the wall jacks. At the far end are the PCs’ network interface cards and PoE-powered access points.',
    'Know which box ends the provider’s line (modem or ONT) and which box routes (the router).', cols=5)

HTML = f'''
<h4>Networking hardware (Core 1 2.5)</h4>
<ul>
<li><strong>Cable modem</strong> (DOCSIS over coax), <strong>DSL modem</strong> (over telephone wiring) and <strong>ONT</strong>
(optical network terminal, where fibre ends) terminate the provider’s line.</li>
<li><strong>Router</strong> — moves traffic between networks (LAN and internet); a SOHO router usually also does NAT, DHCP,
firewall and Wi-Fi. <strong>Firewall</strong> — filters traffic by rules.</li>
<li><strong>Switch</strong> — forwards frames within the LAN by MAC address. An <strong>unmanaged</strong> switch is plug-and-play;
a <strong>managed</strong> switch adds VLANs, port security, monitoring and remote management.</li>
<li><strong>Access point</strong> — bridges Wi-Fi clients onto the wired LAN.</li>
<li><strong>Patch panel</strong> — the termination point for the building’s horizontal cabling; short patch cords connect it to the switch.</li>
<li><strong>Power over Ethernet (PoE)</strong> — power over the data cable for APs, phones and cameras, from a PoE switch or a
<strong>PoE injector</strong> placed between a non-PoE switch and the device. Standards (power at the source):
<strong>802.3af</strong> up to 15.4 W, <strong>802.3at</strong> (PoE+) up to 30 W, <strong>802.3bt</strong> up to 60 W (Type 3)
or 90 W (Type 4). The switch’s total PoE budget is a separate limit.</li>
<li><strong>NIC</strong> — the network interface card; its <strong>MAC address</strong> is a 48-bit hardware address (the first 24
bits identify the manufacturer).</li>
</ul>
{_FIG}
<h4>Networking tools (Core 1 2.8)</h4>
<table class="ref-table"><thead><tr><th scope="col">Tool</th><th scope="col">Use</th></tr></thead><tbody>
<tr><td>Cable stripper</td><td>Removes the outer jacket without nicking the pairs.</td></tr>
<tr><td>Crimper</td><td>Fixes an RJ45 (or RJ11) connector onto the cable end.</td></tr>
<tr><td>Punchdown tool</td><td>Seats wires into a patch panel or keystone jack (110 or Krone block) and trims them.</td></tr>
<tr><td>Cable tester</td><td>Checks continuity and the wire map (opens, shorts, crossed or split pairs).</td></tr>
<tr><td>Toner probe</td><td>The tone generator on one end, the probe finds that cable in a bundle or at the patch panel.</td></tr>
<tr><td>Loopback plug</td><td>Loops a port’s transmit to receive to test the port or NIC itself.</td></tr>
<tr><td>Wi-Fi analyzer</td><td>Shows networks, channels and signal strength to find interference and coverage gaps.</td></tr>
<tr><td>Network tap</td><td>Inline device that copies traffic to a monitoring tool without interrupting the link.</td></tr>
</tbody></table>
{worked('terminating and testing a new drop', '''<ol>
<li>Strip the jacket, untwist only as much as needed, and punch the pairs down on the patch panel in T568B order.</li>
<li>At the wall end, terminate the keystone the same way (both ends must use the same standard for a straight-through link).</li>
<li>Cable tester across the run: the wire map shows pins 3 and 6 open. Re-punch the green pair at the jack; retest — all eight pins pass.</li>
<li>Patch the port to the switch, connect a laptop, confirm link and an address, label both ends.</li></ol>''')}
{scenario('the AP that will not power up', '''<p>A new Wi-Fi 6E access point stays dark on a desk switch. The switch is unmanaged and has no PoE. You add a PoE
injector rated for the AP’s requirement (the datasheet says 802.3at), connecting switch → injector “data in” → injector
“PoE out” → AP. It boots. You note that the next switch purchase should be a managed PoE switch with enough budget for all
APs and phones.</p>''')}
{cfu(('Which device terminates a fibre-to-the-premises line?', 'An ONT (optical network terminal).'),
     ('What does a loopback plug test?', 'The port or NIC itself — transmit is looped back to receive.'),
     ('An AP needs 25 W. Which is the lowest PoE standard that supplies it?', '802.3at (PoE+), up to 30 W at the source.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 5, 'lesson': 3, 'id': 'cert-net-hw',
    'title': 'Networking hardware and networking tools',
    'cert': ['A1:2.5', 'A1:2.8'],
    'html': sme_note('Networking hardware and networking tools (Core 1 2.5 and 2.8).') + HTML,
    'sources': ['ieee-poe'],
}]

GLOSSARY = [
    ('ONT', 'Optical network terminal: the device where a provider’s fibre line terminates at the premises.'),
    ('PoE injector', 'Adds Power over Ethernet to a link from a switch that cannot supply power itself.'),
    ('Managed switch', 'A switch that can be configured (VLANs, port security, monitoring); an unmanaged switch cannot.'),
    ('Punchdown tool', 'Tool that seats and trims wires in a patch panel or keystone jack.'),
    ('Toner probe', 'Tone generator and probe used to trace and identify a cable.'),
    ('Network tap', 'Inline device that copies a link’s traffic to a monitoring tool.'),
]

ITEMS = [
    match('A1:2.8', 'IT-5.3', 1, 'Match each task to the right tool.',
          [('Find which unlabeled cable at the patch panel goes to office 214', 'Toner probe'),
           ('Seat wires into a keystone jack', 'Punchdown tool'),
           ('Confirm all eight pins are wired correctly end to end', 'Cable tester'),
           ('Attach an RJ45 connector to a patch cable', 'Crimper'),
           ('Test whether a NIC port itself works', 'Loopback plug')],
          'Each Core 1 2.8 tool has one main job.',
          decoys=['Wi-Fi analyzer']),
    single('A1:2.8', 'IT-5.3', 2, 'Users report Wi-Fi drops at one end of an office. Which tool best shows overlapping channels and weak signal in that area?',
           'A Wi-Fi analyzer',
           ['A toner probe', 'A loopback plug', 'A crimper'],
           'A Wi-Fi analyzer shows networks, channels and signal strength.'),
    order('A1:2.8', 'IT-5.3', 3, 'Put the steps for terminating a new cable run in order.',
          ['Strip the outer jacket', 'Arrange the pairs in T568B order', 'Punch the wires down on the patch panel', 'Test the run with a cable tester', 'Label both ends'],
          'Strip, order, terminate, test, label.'),
    single('A1:2.8', 'IT-5.3', 4, 'The security team needs a copy of all traffic on one link for a monitoring appliance without interrupting the link. What should be installed?',
           'A network tap',
           ['A PoE injector', 'An unmanaged switch', 'A loopback plug'],
           'A tap copies traffic inline to a monitoring port.'),
    single('A1:2.5', 'IT-5.4', 1, 'A camera needs 25 W of PoE. The switch supports only 802.3af. What is the most appropriate fix?',
           'Use an 802.3at (PoE+) injector or switch',
           ['Use a longer Cat 6 cable', 'Enable jumbo frames on the port', 'Replace the camera’s NIC'],
           '802.3af supplies up to 15.4 W at the source; 802.3at supplies up to 30 W.'),
    match('A1:2.5', 'IT-5.4', 2, 'Match each device to its role.',
          [('Terminates fibre at the customer premises', 'ONT'), ('Terminates a coax internet line', 'Cable modem'),
           ('Adds VLANs and port security to the LAN', 'Managed switch'), ('Bridges wireless clients onto the LAN', 'Access point')],
          'Know which box terminates the line, which switches and which bridges Wi-Fi.',
          decoys=['Patch panel']),
    multi('A1:2.5', 'IT-5.4', 3, 'Which TWO statements about MAC addresses are correct? (Choose two.)',
          ['They are 48-bit hardware addresses', 'The first half identifies the manufacturer'],
          ['They are assigned by the DHCP server', 'They are used to route between networks', 'They change each time the PC restarts'],
          'A MAC is a 48-bit address whose first 24 bits are the manufacturer’s OUI; routing uses IP addresses. (Randomised Wi-Fi MACs are a privacy feature, not a restart behaviour.)'),
    single('A1:2.5', 'IT-5.4', 4, 'A small office has fibre internet. Which device must be between the provider’s line and the office router?',
           'An optical network terminal (ONT)',
           ['A DSL modem', 'A PoE injector', 'A patch panel'],
           'The ONT terminates fibre; DSL modems terminate telephone pairs.'),
]
