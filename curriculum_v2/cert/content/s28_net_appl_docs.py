"""Network+ 1.2 (appliances, applications and functions) — NETOPS 4.3; 3.1 (organizational processes and
documentation) — NETOPS 6.3.  Round 2 of pass 11."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_APP = figure(
    'fig-c-appliances', 'Where each appliance and function sits',
    ['Edge:\nrouter, firewall,\nIDS/IPS, VPN', 'Distribution:\nswitches,\nAP + controller', 'Servers:\nload balancer,\nproxy', 'Storage:\nNAS (files),\nSAN (blocks)', 'Internet:\nCDN edge caches', 'Everywhere:\nQoS, TTL'],
    'Six boxes. At the edge, the router forwards between networks, the firewall filters, an IPS sits inline to block attacks while an '
    'IDS watches a copy of traffic and alerts, and the VPN concentrator terminates tunnels. Switches connect hosts, and wireless access '
    'points are managed by a controller. In front of servers, a load balancer spreads requests and a proxy makes requests on behalf of '
    'clients. Storage is either network-attached storage, which shares files, or a storage area network, which presents block storage. '
    'On the internet, a content delivery network serves copies of content from caches near users. QoS and TTL apply across the path.',
    'Name what the box does to traffic: forward, filter, detect, block, spread, cache or store.', cols=3)

HTML_APP = f'''
<p>Network+ 1.2 compares networking appliances, applications and functions, physical or virtual.</p>
<ul>
<li><strong>Router</strong> (forwards between networks by IP), <strong>switch</strong> (forwards frames by MAC within a LAN), <strong>firewall</strong>
(permits or denies traffic by rule).</li>
<li><strong>IDS vs. IPS</strong> — an intrusion detection system watches a copy of traffic (for example from a SPAN port) and alerts; an
intrusion prevention system sits inline and can drop the traffic.</li>
<li><strong>Load balancer</strong> — spreads client requests across several servers and stops sending to a server that fails its health check.</li>
<li><strong>Proxy</strong> — makes requests on behalf of clients (forward proxy, for filtering and caching) or of servers (reverse proxy).</li>
<li><strong>NAS vs. SAN</strong> — network-attached storage shares <em>files</em> over SMB or NFS; a storage area network presents
<em>block</em> storage (LUNs) to servers over Fibre Channel or iSCSI, which the server formats as its own disk (SNIA definitions).</li>
<li><strong>Wireless access point and controller</strong> — APs give Wi-Fi access; a wireless LAN controller manages many APs centrally.</li>
<li><strong>CDN</strong> (content delivery network) — copies of web content cached at edge servers near users, for speed and to absorb load (RFC 7336).</li>
<li><strong>VPN</strong> — an encrypted tunnel across an untrusted network.</li>
<li><strong>QoS</strong> (quality of service) — classify and mark traffic (DSCP in the IP header, RFC 2474; voice is usually EF, DSCP 46), then queue
or shape so delay-sensitive traffic goes first when the link is busy.</li>
<li><strong>TTL</strong> (time to live) — the IPv4 TTL field (hop limit in IPv6) drops by one at each router; at zero the packet is discarded and an
ICMP Time Exceeded is returned, which stops loops and is how traceroute works. A DNS TTL is something else: how long a record may be cached.</li>
</ul>
{_FIG_APP}
{worked('slow file shares and choppy calls', '''<ol>
<li>Designers need a shared folder of large files: a NAS on the LAN, shared over SMB.</li>
<li>The virtual server cluster needs shared disks it can format: a SAN over iSCSI on its own VLAN.</li>
<li>Calls break up when backups run over the WAN: QoS marks voice EF and gives it priority on the WAN link.</li>
<li>The public website is slow for overseas visitors: a CDN serves images from edge caches near them.</li></ol>''')}
{scenario('the IDS that saw everything and stopped nothing', '''<p>An attack scan triggers hundreds of alerts on the company IDS, but the traffic still reaches the server. The IDS is
connected to a SPAN port, so it only sees a copy of traffic and can alert, not block. The team places an IPS inline at the firewall
for internet traffic, tunes its signatures to avoid blocking legitimate traffic, and keeps the IDS for internal monitoring.</p>''')}
{cfu(('What is the difference between NAS and SAN?', 'NAS shares files; a SAN presents block storage that the server formats.'),
     ('What happens when a packet’s TTL reaches zero?', 'The router discards it and sends back ICMP Time Exceeded.'),
     ('Why can an IPS block attacks when an IDS cannot?', 'The IPS sits inline in the traffic path; the IDS sees only a copy.'))}
'''

_FIG_DOC = figure(
    'fig-c-netdocs', 'The network documentation set',
    ['Diagrams:\nphysical, logical,\nrack, cable map', 'Inventory:\nassets, licences,\nwarranty', 'Addressing:\nIPAM', 'Agreements:\nSLA', 'Wireless:\nsurvey, heat map', 'Life cycle:\nEOL/EOS, patches,\ndecommission'],
    'Six boxes. Diagrams show the physical layout (where devices and cables are), the logical layout (subnets, VLANs and routing), '
    'rack elevations and cable maps, often split into layer 1, 2 and 3 diagrams. The asset inventory lists hardware, software, '
    'licences and warranty and support details. IP address management (IPAM) tracks subnets and assignments. Service-level agreements '
    'record what the provider promises. A wireless survey and heat map show coverage. Life-cycle records track end-of-life and '
    'end-of-support dates, patches and firmware, and decommissioning. Change and configuration management keep the set current.',
    'If it is not documented, the next technician has to rediscover it.', cols=3)

HTML_DOC = f'''
<p>Network+ 3.1 explains why organisations document networks and manage changes and configurations.</p>
<ul>
<li><strong>Physical vs. logical diagrams</strong> — physical shows real devices, ports, cable runs and locations; logical shows subnets,
VLANs, routing and traffic flow. <strong>Layer 1, 2 and 3 diagrams</strong> split these by OSI layer.</li>
<li><strong>Rack diagrams</strong> (rack elevations) show what is in each rack unit; <strong>cable maps</strong> record each cable’s ends and labels (ANSI/TIA-606).</li>
<li><strong>Asset inventory</strong> — hardware, software, licensing, and warranty and support contracts.</li>
<li><strong>IPAM</strong> (IP address management) — tracks subnets, DHCP scopes, reservations and static assignments, so addresses are not duplicated.</li>
<li><strong>SLA</strong> (service-level agreement) — the measurable service a provider commits to, such as uptime and response times.</li>
<li><strong>Wireless survey / heat map</strong> — measured signal strength and coverage across the site.</li>
<li><strong>Life-cycle management</strong> — <strong>EOL</strong> (end of life: no longer sold) and <strong>EOS</strong> (end of support: no more
fixes); software management for patches and bug fixes, operating system and firmware updates; <strong>decommissioning</strong>
(remove from service, wipe or destroy storage per NIST SP 800-88, update the inventory and diagrams).</li>
<li><strong>Change management</strong> — request tracking, approval and records for each change.</li>
<li><strong>Configuration management</strong> — the <em>production</em> configuration, a <em>backup</em> configuration, and a
<em>baseline/golden</em> configuration that new devices start from and running devices are compared to (NIST SP 800-128).</li>
</ul>
{_FIG_DOC}
{worked('replacing an end-of-support switch', '''<ol>
<li>The asset inventory shows the access switch reaches end of support next quarter: no more security fixes.</li>
<li>A change request is raised with scope, window and rollback; the new switch is configured from the golden config.</li>
<li>Cutover follows the cable map so every patch lead goes back to the same port; the rack diagram is updated.</li>
<li>The old switch is decommissioned: config wiped, removed from IPAM and the inventory, and disposed of per policy.</li></ol>''')}
{scenario('the address that already existed', '''<p>A technician gives a new printer a static address that “looked free”. Two days later the finance server drops off the
network: it had the same address. There was no IPAM and the logical diagram was two years old. The team adopts an IPAM tool, records
every static assignment and DHCP reservation in it, and makes updating IPAM and the diagram part of every change record.</p>''')}
{cfu(('What does a logical diagram show that a physical diagram does not?', 'Subnets, VLANs, routing and traffic flow rather than devices and cable runs.'),
     ('What is the difference between EOL and EOS?', 'End of life: no longer sold; end of support: no more fixes or patches.'),
     ('What is a golden configuration?', 'The approved baseline that new devices start from and running devices are compared to.'))}
'''

SUPPLEMENTS = [
    {'course': 'NETOPS', 'chapter': 4, 'lesson': 3, 'id': 'cert-net-appliances', 'title': 'Networking appliances, applications and functions',
     'cert': ['N:1.2'], 'html': sme_note('Networking appliances, applications and functions (Network+ 1.2).') + HTML_APP,
     'sources': ['snia-dict', 'rfc2474', 'rfc791', 'rfc7336']},
    {'course': 'NETOPS', 'chapter': 6, 'lesson': 3, 'id': 'cert-net-docs', 'title': 'Network documentation and life-cycle processes',
     'cert': ['N:3.1'], 'html': sme_note('Organisational processes, documentation and life-cycle management (Network+ 3.1).') + HTML_DOC,
     'sources': ['tia606', 'nist-800128', 'nist-80088']},
]

GLOSSARY = [
    ('IPS', 'Intrusion prevention system: sits inline and can block malicious traffic.'),
    ('NAS', 'Network-attached storage: shares files over SMB or NFS.'),
    ('SAN', 'Storage area network: presents block storage to servers over Fibre Channel or iSCSI.'),
    ('CDN', 'Content delivery network: serves cached content from edge servers near users.'),
    ('DSCP', 'Differentiated Services Code Point: QoS marking in the IP header.'),
    ('IPAM', 'IP address management: tracking subnets and address assignments.'),
    ('EOS', 'End of support: the vendor no longer issues fixes.'),
    ('Golden configuration', 'Approved baseline configuration for a device type.'),
]

MISCONCEPTIONS = {
    'MC-C-NO4-NAS-SAN': {'obj': 'NO-4.3', 'label': 'Mixing up NAS (file shares) and SAN (block storage)',
                         'fix': 'NAS shares files over SMB/NFS; a SAN presents blocks the server formats.', 'terms': ['nas', 'san', 'block', 'iscsi']},
    'MC-C-NO4-IDS-BLOCKS': {'obj': 'NO-4.3', 'label': 'Thinking an IDS on a SPAN port can block traffic',
                            'fix': 'An IDS sees a copy and alerts; an inline IPS can block.', 'terms': ['ids', 'ips', 'inline', 'span']},
    'MC-C-NO4-QOS-SPEED': {'obj': 'NO-4.3', 'label': 'Thinking QoS adds bandwidth rather than prioritising traffic',
                           'fix': 'QoS marks and queues traffic so important traffic goes first; it adds no capacity.', 'terms': ['qos', 'dscp', 'priority', 'queue']},
    'MC-C-NO4-TTL-TIME': {'obj': 'NO-4.3', 'label': 'Confusing the IP TTL hop count with a DNS cache TTL or a clock timer',
                          'fix': 'IP TTL drops by one per router; DNS TTL is how long a record may be cached.', 'terms': ['ttl', 'hop', 'time exceeded', 'traceroute']},
    'MC-C-NO4-APPLIANCE-ROLE': {'obj': 'NO-4.3', 'label': 'Choosing an appliance that does a different job (proxy vs. load balancer vs. CDN)',
                                'fix': 'Load balancers spread requests across servers; proxies act for clients; CDNs cache near users.', 'terms': ['load balancer', 'proxy', 'cdn']},
    'MC-C-NO6-DIAGRAM-TYPE': {'obj': 'NO-6.3', 'label': 'Mixing up physical, logical, rack and cable documentation',
                              'fix': 'Physical: devices and runs; logical: subnets and VLANs; rack: units; cable map: ends and labels.', 'terms': ['logical', 'physical', 'rack', 'cable map']},
    'MC-C-NO6-EOL-EOS': {'obj': 'NO-6.3', 'label': 'Thinking end of life (no longer sold) means no more security patches',
                         'fix': 'EOL: no longer sold; EOS: no more fixes. Plan replacement before EOS.', 'terms': ['eol', 'eos', 'end of support', 'patch']},
    'MC-C-NO6-NO-IPAM': {'obj': 'NO-6.3', 'label': 'Choosing addresses by ping or guesswork instead of IPAM records',
                         'fix': 'IPAM records every subnet, scope and static assignment.', 'terms': ['ipam', 'static', 'duplicate', 'address']},
    'MC-C-NO6-CONFIG-TYPE': {'obj': 'NO-6.3', 'label': 'Confusing the production, backup and golden (baseline) configurations',
                             'fix': 'Golden is the approved baseline; backup is a saved copy; production is what runs.', 'terms': ['golden', 'baseline', 'backup', 'configuration']},
}

ITEMS = [
    single('N:1.2', 'NO-4.3', 11, 'A virtualisation cluster needs shared storage that each host formats as its own disk. What fits?',
           'A SAN presenting iSCSI LUNs', ['A NAS sharing an SMB folder', 'A CDN edge cache', 'A forward proxy'],
           'A SAN presents block storage; a NAS shares files.', mc=['MC-C-NO4-NAS-SAN', None, None]),
    single('N:1.2', 'NO-4.3', 12, 'An attack reaches a web server even though the IDS raised alerts. Why?',
           'The IDS sees a copy of traffic and only alerts', ['The IDS was set to block only on weekends',
            'An IDS blocks only UDP traffic', 'The firewall overrides IDS blocking rules'],
           'An IDS is passive; an inline IPS can drop traffic.', mc=['MC-C-NO4-IDS-BLOCKS', 'MC-C-NO4-IDS-BLOCKS', 'MC-C-NO4-IDS-BLOCKS']),
    match('N:1.2', 'NO-4.3', 13, 'Match each requirement to the appliance or function.',
          [('Spread web requests over four servers', 'Load balancer'), ('Serve images from caches near overseas users', 'CDN'),
           ('Give voice traffic priority on a busy WAN link', 'QoS'), ('Filter staff web browsing on their behalf', 'Forward proxy'),
           ('Manage 60 access points centrally', 'Wireless LAN controller')],
          'Network+ 1.2 appliances, applications and functions.', decoys=['SAN']),
    single('N:1.2', 'NO-4.3', 14, 'What does a router do when it receives an IPv4 packet whose TTL is 1?',
           'Decrements it to 0, discards the packet and returns ICMP Time Exceeded',
           ['Forwards it and resets the TTL to 64', 'Caches it until the DNS record expires', 'Queues it for QoS priority handling'],
           'TTL drops by one per hop; at zero the packet is discarded (RFC 791, RFC 792).', mc=[None, 'MC-C-NO4-TTL-TIME', None]),
    multi('N:1.2', 'NO-4.3', 15, 'Which TWO statements about QoS are true? (Choose two.)',
          ['It marks traffic, for example with DSCP values', 'It gives priority to traffic such as voice when a link is congested'],
          ['It increases the bandwidth of the link', 'It encrypts traffic between sites', 'It replaces the need for a firewall'],
          'QoS classifies, marks and queues; it does not add capacity or security.', mc=['MC-C-NO4-QOS-SPEED', None, None]),
    single('N:3.1', 'NO-6.3', 11, 'Which document shows subnets, VLANs and routing between them?',
           'A logical network diagram', ['A rack elevation diagram', 'A cable map', 'An asset inventory'],
           'Logical diagrams show addressing and traffic flow; physical documents show devices and cables.',
           mc=['MC-C-NO6-DIAGRAM-TYPE', 'MC-C-NO6-DIAGRAM-TYPE', None]),
    single('N:3.1', 'NO-6.3', 12, 'A vendor announces end of support for a firewall model next quarter. What does that mean?',
           'No further patches or fixes will be released after that date', ['The model can no longer be bought, but patches continue',
            'The firewall will stop passing traffic on that date', 'The warranty is extended automatically'],
           'EOS ends fixes and support; EOL usually means it is no longer sold.',
           mc=['MC-C-NO6-EOL-EOS', None, None]),
    order('N:3.1', 'NO-6.3', 13, 'Put the steps for decommissioning a switch in order.',
          ['Raise and approve a change request', 'Move its links to the replacement using the cable map',
           'Wipe the configuration and storage per policy', 'Remove it from IPAM, inventory and diagrams'],
          'Approve, migrate, sanitise, update records (Network+ 3.1).'),
    match('N:3.1', 'NO-6.3', 14, 'Match each record to what it holds.',
          [('IPAM', 'Subnets and address assignments'), ('SLA', 'Uptime and response times a provider commits to'),
           ('Golden configuration', 'Approved baseline for a device type'), ('Heat map', 'Measured Wi-Fi signal across the floor'),
           ('Asset inventory', 'Hardware, licences and warranty details')],
          'Network+ 3.1 documentation.', decoys=['Running process list']),
    single('N:3.1', 'NO-6.3', 15, 'A technician needs a static address for a new printer. What should they check first?',
           'The IPAM record for that subnet', ['Ping a random address and use it if nothing replies',
            'Copy the address of a printer that is switched off', 'Pick the last address in the DHCP scope'],
           'IPAM records assignments; an unanswered ping or an off device does not prove an address is free.',
           mc=['MC-C-NO6-NO-IPAM', 'MC-C-NO6-NO-IPAM', 'MC-C-NO6-NO-IPAM']),
]
