"""Network+ 4.2 (attacks and their impact) and 4.1 (basic network security concepts) — NETOPS 5.3."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-l2attack', 'Layer 2 attacks and the switch feature that stops each',
    ['MAC flooding\n→ port security', 'Rogue DHCP\n→ DHCP snooping', 'ARP poisoning\n→ dynamic ARP insp.', 'VLAN hopping\n→ no DTP, unused native'],
    'Four boxes, each pairing an attack with its control. MAC flooding fills the switch’s MAC address table so it floods '
    'frames to every port; port security limits the number of MAC addresses per port. A rogue DHCP server hands out a '
    'malicious gateway; DHCP snooping allows DHCP offers only from trusted ports. ARP poisoning maps the gateway’s IP to '
    'the attacker’s MAC; dynamic ARP inspection checks ARP replies against the DHCP snooping bindings. VLAN hopping by '
    'switch spoofing or double tagging is stopped by turning off trunk negotiation on access ports and setting the trunk '
    'native VLAN to an unused VLAN.',
    'DHCP snooping is the foundation: dynamic ARP inspection uses its binding table.', cols=4)

HTML = f'''
<h4>Attacks and their impact (Network+ 4.2)</h4>
<table class="ref-table"><thead><tr><th scope="col">Attack</th><th scope="col">How it works</th><th scope="col">Impact / defence</th></tr></thead><tbody>
<tr><td><strong>DoS / DDoS</strong></td><td>Exhausts a service, link or device — from one source, or many (a botnet). A TCP SYN flood fills a server’s half-open connection table.</td><td>Outage. Upstream filtering, rate limiting, SYN cookies (RFC 4987), DDoS protection services.</td></tr>
<tr><td><strong>VLAN hopping</strong></td><td><em>Switch spoofing</em> (the attacker negotiates a trunk) or <em>double tagging</em> (an outer tag for the native VLAN, an inner tag for the target).</td><td>Reaches a VLAN it should not. Disable trunk negotiation on access ports; use an unused native VLAN on trunks.</td></tr>
<tr><td><strong>MAC flooding</strong></td><td>Floods fake source MACs until the switch’s MAC table is full, so it floods frames out of every port.</td><td>Eavesdropping. Port security (maximum MACs per port).</td></tr>
<tr><td><strong>ARP poisoning / spoofing</strong></td><td>Unsolicited (gratuitous) ARP replies map the gateway’s IP to the attacker’s MAC — ARP has no authentication (RFC 826).</td><td>On-path interception. Dynamic ARP inspection; static entries for critical hosts.</td></tr>
<tr><td><strong>DNS poisoning / spoofing</strong></td><td>False records are injected into a resolver’s cache, or forged answers are sent.</td><td>Users are sent to attacker sites. DNSSEC validation; secured resolvers.</td></tr>
<tr><td><strong>Rogue DHCP</strong></td><td>An unauthorised server answers first with a malicious gateway or DNS server.</td><td>On-path or outage. DHCP snooping (trusted ports only).</td></tr>
<tr><td><strong>Rogue AP / evil twin</strong></td><td>A rogue AP is an unauthorised access point on the LAN; an evil twin copies a trusted SSID to lure clients.</td><td>Backdoor into the LAN, credential theft. Wireless intrusion detection, 802.1X/EAP with server-certificate validation.</td></tr>
<tr><td><strong>On-path attack</strong></td><td>Any position between two parties — via ARP, DHCP, DNS or a rogue AP — to read or alter traffic.</td><td>Data theft or tampering. Encryption in transit (TLS, IPsec) plus the controls above.</td></tr>
<tr><td><strong>Social engineering</strong></td><td>Phishing, dumpster diving, shoulder surfing, tailgating.</td><td>Credentials and access. Training, verification, physical controls.</td></tr>
<tr><td><strong>Malware</strong></td><td>Worms and ransomware spread across flat networks.</td><td>Segmentation limits the blast radius.</td></tr>
</tbody></table>
{_FIG}
<h4>Basic security concepts (Network+ 4.1) in one table</h4>
<table class="ref-table"><thead><tr><th scope="col">Area</th><th scope="col">Terms</th></tr></thead><tbody>
<tr><td>Confidentiality, integrity, availability (CIA)</td><td>The three goals; encryption serves confidentiality, hashing and signatures integrity, redundancy availability.</td></tr>
<tr><td>Encryption</td><td>In transit (TLS, IPsec, SSH) and at rest (disk or database encryption).</td></tr>
<tr><td>Certificates and PKI</td><td>A certificate authority signs certificates; a self-signed certificate is not trusted by clients unless installed manually.</td></tr>
<tr><td>Identity and access management (IAM)</td><td>Authentication: MFA, SSO, SAML (web SSO), LDAP (directory queries), RADIUS (UDP, network access) and TACACS+ (TCP 49, device administration, encrypts the whole payload), time-based restrictions. Authorization: least privilege, role-based access control.</td></tr>
<tr><td>Location and physical</td><td>Geofencing, cameras, locks.</td></tr>
<tr><td>Deception</td><td>Honeypot (a decoy system) and honeynet (a decoy network) to detect and study attackers.</td></tr>
<tr><td>Risk terms</td><td>Threat (what could cause harm), vulnerability (a weakness), exploit (the way it is used), risk (likelihood × impact).</td></tr>
<tr><td>Compliance</td><td>Data locality (where data may be stored), PCI DSS (card data), GDPR (EU personal data).</td></tr>
<tr><td>Segmentation enforcement</td><td>Separate IoT/IIoT, SCADA/ICS/OT, guest and BYOD networks from corporate systems.</td></tr>
</tbody></table>
{worked('a user’s gateway is “wrong”', '''<ol>
<li>Several PCs on one floor have default gateway 192.168.50.1; the correct gateway for that VLAN is 10.20.30.1.</li>
<li><code>ipconfig /all</code> shows the DHCP server as 192.168.50.1 — not the corporate DHCP server. A rogue DHCP server is answering.</li>
<li>Switch MAC table locates the source port: a consumer router plugged in under a desk. Shut the port, remove the device.</li>
<li>Prevent recurrence: enable DHCP snooping with only the uplinks trusted, and add dynamic ARP inspection on the same VLAN.</li>
<li>Release and renew leases on affected PCs; verify the correct gateway; document.</li></ol>''')}
{scenario('the coffee-shop Wi-Fi', '''<p>A travelling employee connects to “CoffeeShop_Free” and gets a certificate warning when opening the company
portal. Two networks with that name are visible. This is consistent with an evil twin performing an on-path attack. The
warning is the defence working: she should not click through, should disconnect, and should use the company VPN or her phone’s
hotspot. The help desk reports it to security in case credentials were entered.</p>''')}
{cfu(('Which switch feature limits the number of MAC addresses on a port?', 'Port security.'),
     ('What feature does dynamic ARP inspection rely on?', 'The DHCP snooping binding table.'),
     ('RADIUS or TACACS+: which uses TCP and encrypts the whole payload?', 'TACACS+.'))}
'''

SUPPLEMENTS = [{
    'course': 'NETOPS', 'chapter': 5, 'lesson': 3, 'id': 'cert-net-attacks',
    'title': 'Network attacks, their impact and basic security concepts',
    'cert': ['N:4.2', 'N:4.1'],
    'html': sme_note('Network attacks and defences (Network+ 4.2) and basic network security concepts (Network+ 4.1).') + HTML,
    'sources': ['rfc4987', 'rfc826', 'ieee-8021q', 'cisa-dos', 'nist-800207'],
}]

GLOSSARY = [
    ('MAC flooding', 'Filling a switch’s MAC address table with fake entries so it floods frames to every port.'),
    ('ARP poisoning', 'Sending forged ARP replies so traffic for one IP address goes to the attacker’s MAC address.'),
    ('DHCP snooping', 'Switch feature that allows DHCP server messages only on trusted ports and records IP-to-MAC bindings.'),
    ('Dynamic ARP inspection', 'Switch feature that drops ARP packets that do not match the DHCP snooping bindings.'),
    ('VLAN hopping', 'Reaching another VLAN without routing, by switch spoofing or double tagging.'),
    ('Honeypot', 'A decoy system that attracts attackers so their activity can be detected and studied.'),
    ('TACACS+', 'AAA protocol over TCP 49 used for device administration; encrypts the entire payload.'),
]

ITEMS = [
    match('N:4.2', 'NO-5.3', 1, 'Match each attack to the switch feature that best mitigates it.',
          [('MAC flooding', 'Port security'), ('Rogue DHCP server', 'DHCP snooping'),
           ('ARP poisoning', 'Dynamic ARP inspection'), ('Double-tagging VLAN hopping', 'Unused native VLAN on trunks')],
          'Each Layer 2 attack has a matching control; dynamic ARP inspection relies on DHCP snooping’s binding table.',
          decoys=['Spanning Tree PortFast']),
    single('N:4.2', 'NO-5.3', 2, 'Users on one VLAN suddenly receive an unfamiliar default gateway and DNS server from DHCP. What is the most likely cause?',
           'A rogue DHCP server on the VLAN',
           ['A MAC flooding attack on the switch', 'A DNS cache poisoning attack', 'A duplex mismatch on the uplink'],
           'Wrong gateway and DNS from DHCP is the signature of a rogue DHCP server; DHCP snooping prevents it.'),
    single('N:4.2', 'NO-5.3', 3, 'A switch begins sending unicast frames out of every port after an attacker’s laptop is connected. What attack is under way?',
           'MAC flooding',
           ['ARP poisoning', 'Evil twin', 'DNS spoofing'],
           'A full MAC table makes the switch flood frames like a hub.'),
    multi('N:4.2', 'NO-5.2', 4, 'Which TWO configurations reduce the risk of VLAN hopping? (Choose two.)',
          ['Disable trunk negotiation on access ports', 'Set the trunk native VLAN to an unused VLAN'],
          ['Enable PortFast on all trunks', 'Use VLAN 1 for user traffic', 'Allow all VLANs on every trunk'],
          'Switch spoofing needs trunk negotiation; double tagging needs the attacker’s VLAN to be the native VLAN.'),
    single('N:4.2', 'NO-5.3', 5, 'Clients connect to an access point broadcasting the corporate SSID that is not on the company’s AP inventory, outside the building. What is this?',
           'An evil twin',
           ['A honeynet', 'A captive portal', 'A wireless bridge'],
           'An evil twin impersonates a trusted SSID to lure clients for an on-path attack.'),
    match('N:4.1', 'NO-5.3', 1, 'Match each security term to its meaning.',
          [('Vulnerability', 'A weakness that could be used'), ('Exploit', 'The method that takes advantage of a weakness'),
           ('Threat', 'Something that could cause harm'), ('Honeypot', 'A decoy system to detect attackers')],
          'Standard risk vocabulary from Network+ 4.1.',
          decoys=['Geofencing']),
    single('N:4.1', 'NO-5.2', 2, 'Network administrators’ logins to switches must be authenticated centrally, with each command authorized and the whole session payload encrypted. Which protocol fits best?',
           'TACACS+',
           ['RADIUS', 'LDAP', 'SAML'],
           'TACACS+ (TCP 49) separates AAA functions and encrypts the entire payload, which suits device administration.'),
    single('N:4.1', 'NO-5.3', 3, 'An internal web server’s certificate triggers browser warnings on every client, but the traffic is encrypted. What is the most likely reason?',
           'The certificate is self-signed',
           ['The server uses TLS 1.3', 'The certificate uses a 2048-bit key', 'The site is on the intranet zone'],
           'Clients do not trust a self-signed certificate unless it is installed or issued by a trusted internal CA.'),
]
