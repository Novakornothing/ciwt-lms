"""Network+ 5.2 (cabling and physical interface issues) and 5.5 (tools and protocols) — NETOPS 6.1."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-ifcounters', 'Reading an interface: status line first, then counters',
    ['Status: up/up?\nadmin down? err-disabled?', 'Speed and duplex\nmatch both ends?', 'Counters: CRC,\nrunts, giants, drops', 'Optics / PoE:\nlight level, power budget'],
    'Four boxes in order. First read the status line: up and up is healthy; administratively down means someone shut the '
    'port; err-disabled means the switch shut it after a violation such as port security or BPDU guard. Second, check that '
    'speed and duplex match on both ends. Third, read the error counters: CRC errors point at cabling or interference, runts '
    'at collisions or a duplex mismatch, giants at an MTU mismatch, drops at congestion. Fourth, for fibre check the received '
    'light level, and for PoE check the power budget.',
    'show interfaces answers most physical-layer questions before you touch a cable.', cols=4)

HTML = f'''
<h4>Cabling and interface issues (Network+ 5.2)</h4>
<table class="ref-table"><thead><tr><th scope="col">Finding</th><th scope="col">Meaning</th><th scope="col">Next step</th></tr></thead><tbody>
<tr><td>Administratively down</td><td>The port was shut in configuration</td><td>Confirm it should be live, then <code>no shutdown</code></td></tr>
<tr><td>Error disabled (err-disabled)</td><td>The switch shut the port after a violation (port security, BPDU guard)</td><td>Find and fix the cause, then reset the port</td></tr>
<tr><td>Suspended</td><td>A link-aggregation member whose settings do not match the bundle</td><td>Match speed, duplex, VLANs and LACP mode on the member</td></tr>
<tr><td>CRC errors</td><td>Frames corrupted in transit: damaged cable, bad termination, interference (EMI), crosstalk</td><td>Test or replace the cable; reroute away from interference</td></tr>
<tr><td>Runts</td><td>Frames shorter than 64 bytes — collisions, often a duplex mismatch</td><td>Match duplex (auto on both ends)</td></tr>
<tr><td>Giants</td><td>Frames larger than the configured MTU</td><td>Make MTU / jumbo-frame settings consistent along the path</td></tr>
<tr><td>Attenuation; low received light (dBm)</td><td>Signal loss from distance, dirty or damaged fibre ends, too many joints</td><td>Clean and inspect connectors; check run length against the standard</td></tr>
<tr><td>TX/RX transposed</td><td>Fibre strands crossed so transmit meets transmit</td><td>Swap the strands at one end (polarity)</td></tr>
<tr><td>PoE device not powering</td><td>Power budget exhausted or the wrong PoE standard</td><td><code>show power inline</code>; move or reduce load</td></tr>
</tbody></table>
{_FIG}
<h4>Tools and protocols (Network+ 5.5)</h4>
<ul>
<li><strong>Software:</strong> <strong>protocol analyzer</strong> (Wireshark) and <strong>tcpdump</strong> capture packets;
<code>ping</code> and <code>traceroute</code>/<code>tracert</code> test reachability and path; <code>nslookup</code> and
<code>dig</code> query DNS; <code>netstat</code> shows connections and listening ports; <code>ip</code>/<code>ifconfig</code>/
<code>ipconfig</code> show addressing; <code>arp</code> shows IP-to-MAC mappings; <strong>Nmap</strong> discovers hosts and open
ports (only with authorisation); <strong>LLDP/CDP</strong> identify the neighbouring device and port; speed testers measure throughput.</li>
<li><strong>Hardware:</strong> toner, cable tester, <strong>taps</strong>, Wi-Fi analyzer and the <strong>visual fault locator</strong> (a
red laser that shows breaks and bad joints in fibre).</li>
<li><strong>Device commands:</strong> <code>show mac address-table</code>, <code>show ip route</code>, <code>show interfaces</code>,
<code>show running-config</code>, <code>show arp</code>, <code>show vlan</code> and <code>show power inline</code>.</li>
</ul>
{worked('“slow network” on one port', '''<ol>
<li>One user’s file copies crawl; neighbours are fine. <code>show interfaces</code> on the user’s port: up/up, 100 Mb/s full duplex (hard-set), runts and CRC errors rising.</li>
<li>The switch port is hard-set to 100 Mb/s full duplex. The PC auto-negotiates, gets no negotiation from a hard-set port, detects the speed and falls back to half duplex: a duplex mismatch.</li>
<li>Set the port to auto speed/duplex, re-patch with a tested cable; link comes up at 1000/full and counters stop increasing.</li>
<li>Clear counters, monitor for a day, document the change.</li></ol>''')}
{scenario('the errors that followed the cable', '''<p>A user reports a slow, unreliable connection. The switch port shows CRC errors climbing. Moving the PC to a
different switch port does not help — the errors move with it. Replacing the user’s patch cable stops the errors; the
technician clears the counters and checks again the next day to confirm they stay at zero.</p>''')}
{cfu(('A port shows “err-disabled”. What does that mean?', 'The switch shut the port itself after a violation such as port security or BPDU guard.'),
     ('Rising CRC errors on one port usually point at…?', 'The physical layer — cable, termination or interference.'),
     ('Which tool shows the neighbouring switch’s name and port?', 'LLDP or CDP (show lldp/cdp neighbors).'))}
'''

SUPPLEMENTS = [{
    'course': 'NETOPS', 'chapter': 6, 'lesson': 1, 'id': 'cert-net-trouble', 'title': 'Interface states, error counters and the troubleshooting toolkit',
    'cert': ['N:5.2', 'N:5.5'], 'html': sme_note('Cabling and interface issues and network troubleshooting tools (Network+ 5.2 and 5.5).') + HTML,
    'sources': ['cisco-ifaces', 'tcpdump-man'],
}]

GLOSSARY = [
    ('Runt', 'An Ethernet frame shorter than 64 bytes, usually from collisions or a duplex mismatch.'),
    ('Giant', 'A frame larger than the configured MTU.'),
    ('Err-disabled', 'Port state in which the switch has shut the port after a violation.'),
    ('Visual fault locator', 'Red-laser tool that shows breaks and bad joints in fibre.'),
    ('LLDP', 'Link Layer Discovery Protocol: devices advertise their identity and port to neighbours (CDP is Cisco’s equivalent).'),
]

ITEMS = [
    match('N:5.2', 'NO-6.1', 1, 'Match each interface finding to its most likely cause.',
          [('Rising CRC errors', 'Damaged cable or interference'), ('Runts and late collisions', 'Duplex mismatch'),
           ('Giants', 'MTU mismatch along the path'), ('Administratively down', 'Port shut in configuration')],
          'Read show interfaces counters to locate physical faults.',
          decoys=['DNS server unreachable']),
    single('N:5.2', 'NO-6.1', 2, 'A newly patched fibre link stays down. Light is visible at both ends, and swapping the two strands at one end brings it up. What was the fault?',
           'TX/RX transposed (polarity)',
           ['Attenuation from a long run', 'An MTU mismatch', 'An exhausted PoE budget'],
           'Transmit must meet receive; swapping strands fixes reversed polarity.'),
    single('N:5.2', 'NO-6.1', 3, 'An access port shows err-disabled after a user connected a small switch under their desk. What is the most likely reason?',
           'A port-security or BPDU-guard violation',
           ['Attenuation on the long copper cable run', 'A giant-frame error', 'An incorrect DNS suffix'],
           'Err-disabled means the switch shut the port after a security or loop-protection violation.'),
    order('N:5.2', 'NO-6.1', 4, 'Put these physical-layer checks in an efficient order for a port that is “down”.',
          ['Read the interface status line', 'Check speed and duplex on both ends', 'Read CRC, runt and giant counters', 'Test or replace the cable'],
          'Status and configuration are read in seconds; cable tests come once the counters point at the physical layer.'),
    match('N:5.5', 'NO-9.1', 1, 'Match each task to the best tool.',
          [('Find which switch port a server is plugged into', 'show mac address-table'), ('Identify the neighbouring switch and its port', 'LLDP/CDP'),
           ('Locate a break in a fibre patch lead', 'Visual fault locator'), ('Query an MX record from Linux', 'dig')],
          'Each Network+ 5.5 tool has a characteristic use.',
          decoys=['Crimper']),
    single('N:5.5', 'NO-9.1', 2, 'A technician needs to capture packets on a headless Linux server to send to the security team. Which tool fits?',
           'tcpdump',
           ['nslookup', 'tracert', 'ipconfig'],
           'tcpdump captures packets from the command line and can write a capture file.'),
    single('N:5.5', 'NO-9.2', 3, 'A PoE phone will not power up on a switch that powers other phones. Which command best shows whether the power budget is the problem?',
           'show power inline',
           ['show vlan', 'show ip route', 'show running-config | include hostname'],
           'show power inline lists available and used PoE power per port.'),
    multi('N:5.5', 'NO-9.1', 4, 'Which TWO tools would best show which services are listening on a server? (Choose two.)',
          ['netstat on the server', 'An authorised Nmap scan'],
          ['A toner probe', 'A visual fault locator', 'show vlan on the switch'],
          'netstat shows listening ports locally; Nmap discovers open ports remotely (only with authorisation).'),
]
