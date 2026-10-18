"""Network+ 3.5 (access and management methods) and 4.3 (security features and defences) — NETOPS 5.2 and 5.3."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_VPN = figure(
    'fig-c-vpn', 'VPN types and tunnel modes',
    ['Site-to-site:\ngateway to gateway', 'Client-to-site:\nlaptop to gateway', 'Clientless:\nbrowser portal', 'Split tunnel:\nonly company traffic', 'Full tunnel:\nall traffic'],
    'Five boxes. A site-to-site VPN joins two networks through their gateways, usually with IPsec, so users notice nothing. A '
    'client-to-site (remote-access) VPN runs a client on the laptop that connects to the company gateway. A clientless VPN gives '
    'access to selected web applications through a TLS portal in the browser, with no client installed. With a split tunnel, only '
    'traffic for company networks goes through the VPN and internet traffic goes direct; with a full tunnel, all traffic goes '
    'through the VPN so company security controls inspect it.',
    'Pick the VPN type by who connects, and the tunnel mode by how much traffic the company needs to see.', cols=5)

HTML_ACCESS = f'''
<p>Network+ 3.5 compares ways to reach and manage a network.</p>
<h4>VPNs</h4>
<ul>
<li><strong>Site-to-site</strong> — permanent tunnel between two sites’ gateways (IPsec; NIST SP 800-77 Rev. 1).</li>
<li><strong>Client-to-site</strong> (remote access) — a VPN client on each user device.</li>
<li><strong>Clientless</strong> — a TLS (SSL VPN) portal reached in a browser, for selected web apps (NIST SP 800-113).</li>
<li><strong>Split tunnel vs. full tunnel</strong> — split sends only company-bound traffic through the VPN (less load, but internet traffic
bypasses company filtering); full sends everything through it (more control, more bandwidth at the head office).</li>
</ul>
<h4>Connection and management methods</h4>
<ul>
<li><strong>SSH</strong> — encrypted command-line management (TCP 22); replaces Telnet.</li>
<li><strong>GUI</strong> — a device’s web interface (HTTPS only).</li>
<li><strong>API</strong> — programmatic access for automation and monitoring tools.</li>
<li><strong>Console</strong> — a direct serial or USB console cable to the device; works when the network does not.</li>
<li><strong>Jump box / jump host</strong> — a hardened server that administrators connect to first, and the only host allowed to reach management interfaces.</li>
<li><strong>In-band vs. out-of-band</strong> — in-band management uses the production network; out-of-band uses a separate path
(a management network, console server or cellular modem) so devices can be fixed when the production network is down.</li>
</ul>
{_FIG_VPN}
{worked('remote access for a new branch', '''<ol>
<li>The branch needs printers and file servers at head office all day: a site-to-site IPsec VPN between the two firewalls.</li>
<li>Field staff need the same servers from hotels: client-to-site VPN with MFA.</li>
<li>Contractors need only the ticketing web app: clientless portal access, no client on their own devices.</li>
<li>Policy requires web filtering on company laptops everywhere, so the client VPN uses a full tunnel.</li>
<li>Switches at the branch are managed over SSH from the jump host, with a console server on a cellular link for out-of-band access.</li></ol>''')}
{scenario('the switch nobody could reach', '''<p>A configuration change on a core switch blocks the management VLAN, and every SSH session drops. Because
management was in-band only, a technician has to drive to the site and connect a console cable. After the fix, the team adds an
out-of-band console server reachable over a separate link and moves all management through a jump host, so the next mistake can
be undone remotely and every session is logged.</p>''')}
{cfu(('What is the difference between a split tunnel and a full tunnel?', 'Split sends only company traffic through the VPN; full sends all traffic through it.'),
     ('When is out-of-band management needed?', 'When the production network is down or misconfigured, so in-band access is lost.'),
     ('Which VPN type needs no installed client?', 'A clientless (browser-based TLS) VPN.'))}
'''

_FIG_DEF = figure(
    'fig-c-netdef', 'Network defences from the port outwards',
    ['Port: disable unused,\nport security', 'Admission: 802.1X,\nNAC', 'Traffic: ACLs,\nzones, screened subnet', 'Content: URL and\ncontent filtering', 'Keys and defaults:\nrotate, change'],
    'Five layers from left to right. At the switch port, disable unused ports and use port security to limit MAC addresses. Before '
    'a device joins, 802.1X authenticates it and network access control checks its health. Access control lists and firewall zones '
    'separate trusted from untrusted networks, with public servers in a screened subnet. URL and content filtering block harmful '
    'sites and file types. Throughout, change default passwords and manage and rotate keys.',
    'Each layer limits who joins, what they can reach, and what they can fetch.', cols=5)

HTML_DEF = f'''
<p>Network+ 4.3 asks you to apply network security features and defences.</p>
<ul>
<li><strong>Device hardening</strong> — disable unused ports and services; change default passwords; manage and rotate keys
(SSH keys, Wi-Fi pre-shared keys, certificates — NIST SP 800-57 covers key management).</li>
<li><strong>Network access control (NAC)</strong> — checks a device’s identity and posture before it joins.</li>
<li><strong>Port security</strong> — limits the MAC addresses allowed on a switch port.</li>
<li><strong>802.1X</strong> — port-based authentication through a RADIUS server (IEEE 802.1X-2020).</li>
<li><strong>MAC filtering</strong> — an allow-list of MAC addresses. Weak on its own: MAC addresses are easy to spoof.</li>
<li><strong>Access control lists (ACLs)</strong> — permit or deny traffic by address, protocol and port.</li>
<li><strong>URL filtering</strong> — allow or block sites by address or category. <strong>Content filtering</strong> — inspects what is fetched, such as file types or malware.</li>
<li><strong>Trusted vs. untrusted zones</strong> — firewall policy between internal, guest and internet zones, and a
<strong>screened subnet</strong> (DMZ) for servers the internet must reach (NIST SP 800-41 Rev. 1).</li>
</ul>
{_FIG_DEF}
{worked('locking down a conference-room port', '''<ol>
<li>A wall port in a public meeting room connects straight to the staff VLAN.</li>
<li>Enable 802.1X on the port: company laptops authenticate with certificates; anything else is placed in the guest VLAN.</li>
<li>Add port security limiting the port to two MAC addresses (a phone and a PC), with violations logged.</li>
<li>ACL on the guest VLAN: internet only, no internal subnets.</li>
<li>Disable the unused ports in the room, and record the change.</li></ol>''')}
{scenario('the Wi-Fi key everyone knew', '''<p>A small company’s Wi-Fi uses one pre-shared key, unchanged for years and known to former staff. MAC filtering was
added as a “fix”, but a visitor joined by copying an allowed MAC address. The company moves staff to WPA3-Enterprise with 802.1X,
puts visitors on a separate guest network, rotates the remaining keys on a schedule, and keeps the key change in the
off-boarding checklist.</p>''')}
{cfu(('Why is MAC filtering weak on its own?', 'MAC addresses can be spoofed easily.'),
     ('What is the difference between URL filtering and content filtering?', 'URL filtering blocks by site or category; content filtering inspects what is fetched, such as file types or malware.'),
     ('Where should an internet-facing web server sit?', 'In a screened subnet (DMZ), separated from the internal network.'))}
'''

SUPPLEMENTS = [
    {'course': 'NETOPS', 'chapter': 5, 'lesson': 2, 'id': 'cert-net-access', 'title': 'VPN types and network management access',
     'cert': ['N:3.5'], 'html': sme_note('Network access and management methods (Network+ 3.5).') + HTML_ACCESS, 'sources': ['nist-80077r1', 'nist-800113']},
    {'course': 'NETOPS', 'chapter': 5, 'lesson': 3, 'id': 'cert-net-defences', 'title': 'Network security features and defences',
     'cert': ['N:4.3'], 'html': sme_note('Network security features, defence techniques and solutions (Network+ 4.3).') + HTML_DEF,
     'sources': ['ieee-8021x', 'nist-80041r1', 'nist-80057p1']},
]

GLOSSARY = [
    ('Site-to-site VPN', 'Permanent tunnel joining two networks through their gateways.'),
    ('Clientless VPN', 'Browser-based TLS portal giving access to selected web applications without a VPN client.'),
    ('Split tunnel', 'VPN mode sending only company-bound traffic through the tunnel.'),
    ('Jump host', 'Hardened server administrators connect through to reach management interfaces.'),
    ('Out-of-band management', 'Managing devices over a path separate from the production network.'),
    ('MAC filtering', 'Allow-listing devices by MAC address; weak because MACs can be spoofed.'),
    ('URL filtering', 'Allowing or blocking web access by site address or category.'),
    ('Content filtering', 'Inspecting fetched content, such as file types or malware, and blocking it by policy.'),
]

ITEMS = [
    match('N:3.5', 'NO-5.2', 1, 'Match each requirement to the access method.',
          [('Join two offices’ networks permanently', 'Site-to-site VPN'), ('Contractor reaches one web app with no client installed', 'Clientless VPN'),
           ('Fix a switch when the production network is down', 'Out-of-band management'), ('Only route company traffic through the VPN', 'Split tunnel')],
          'Network+ 3.5 access and management methods.', decoys=['Full tunnel']),
    single('N:3.5', 'NO-5.2', 2, 'Security policy says web filtering must apply to company laptops even on hotel Wi-Fi. Which VPN setting meets this?',
           'A full tunnel', ['A split tunnel', 'A clientless portal', 'In-band management'],
           'A full tunnel sends all traffic through company controls.'),
    single('N:3.5', 'NO-5.2', 3, 'Administrators must reach switch management only through one logged, hardened server. What is that server called?',
           'A jump host', ['A screened subnet', 'A console cable', 'A NAT gateway'],
           'A jump host (jump box) is the controlled entry point to management interfaces.'),
    multi('N:3.5', 'NO-5.2', 4, 'Which TWO are out-of-band management methods? (Choose two.)',
          ['A console server on a separate link', 'A cellular modem for remote console access'],
          ['SSH over the production VLAN', 'The device’s web GUI on the user LAN', 'An API call over the production network'],
          'Out-of-band uses a path separate from the production network.'),
    single('N:4.3', 'NO-5.3', 1, 'A company relies on MAC filtering to keep unknown devices off Wi-Fi. Why is that weak?',
           'MAC addresses can be copied and spoofed easily',
           ['MAC filtering only works on 2.4 GHz networks', 'MAC addresses change every time a device reboots', 'MAC filtering blocks every WPA3 client'],
           'MAC addresses are sent in the clear and can be changed in software.'),
    match('N:4.3', 'NO-5.3', 2, 'Match each control to what it does.',
          [('802.1X', 'Authenticates a device before the port opens'), ('ACL', 'Permits or denies traffic by address and port'),
           ('URL filtering', 'Blocks sites by address or category'), ('Screened subnet', 'Holds internet-facing servers apart from the LAN')],
          'Network+ 4.3 defences.', decoys=['Split tunnel']),
    order('N:4.3', 'NO-5.3', 3, 'Put the steps for hardening a new switch before it goes live in order.',
          ['Change the default admin password', 'Disable unused ports and services', 'Enable 802.1X or port security on access ports',
           'Apply management ACLs allowing only the jump host', 'Back up and document the configuration'],
          'Remove defaults first, then reduce exposure, control access, and record the result.'),
    multi('N:4.3', 'NO-5.3', 4, 'Which TWO are key-management practices? (Choose two.)',
          ['Rotating a Wi-Fi pre-shared key on a schedule', 'Revoking a departed administrator’s SSH key'],
          ['Disabling unused switch ports', 'Placing web servers in a screened subnet', 'Blocking sites by category', 'Using a split tunnel'],
          'Key management covers creating, rotating and revoking keys.'),
]
