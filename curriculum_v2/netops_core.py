"""Network Operations Fundamentals — core teaching content for chapters 1–6 (pass 8).

The original NETOPS lessons were mostly a shared template around two or three lines of topic text.
Each entry below gives a teaching lesson measurable objectives, a specific plain-English summary and a
core-content section. Technical facts follow the published standards they name (IEEE 802.x, IETF RFCs,
TIA-568) or vendor-neutral practice; values marked "typical" or "common default" vary by vendor.
"""

T = '<table class="port-table">'


def table(head, rows):
    h = ''.join(f'<th scope="col">{c}</th>' for c in head)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'{T}<thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def check(*qa):
    items = ''.join(f'<li><strong>{q}</strong> <span class="answer">{a}</span></li>' for q, a in qa)
    return f'<div class="callout check-yourself"><h4>Check yourself</h4><ol>{items}</ol></div>'


NETOPS_CORE = {
    # ------------------------------------------------------------------ Chapter 1
    (1, 1): {
        'objectives': [
            'Name the seven OSI layers and the four TCP/IP layers, and map each to a common protocol or device',
            'Describe encapsulation: how data becomes segments, packets, frames and bits on the way down the stack',
            'Classify a reported symptom by the lowest layer that could explain it',
            'Choose a bottom-up, top-down or divide-and-conquer approach and justify the choice for a given ticket',
        ],
        'plain': 'A layered model is a checklist for where a network can break. The OSI model has seven layers and is '
                 'used for teaching and talking; the TCP/IP model has four and is what hosts actually run. '
                 'Naming the layer you are testing keeps you from reinstalling an application when the cable is unplugged.',
        'html': '<h3>The two models side by side</h3>'
                + table(['OSI layer', 'TCP/IP layer', 'Unit of data (PDU)', 'Examples', 'A first test'], [
                    ['7 Application', 'Application', 'Data', 'HTTP, DNS, SMTP, SSH', 'Does the app or a browser get a response?'],
                    ['6 Presentation', 'Application', 'Data', 'TLS encryption, character encoding', 'Certificate or encoding errors?'],
                    ['5 Session', 'Application', 'Data', 'Session setup and teardown', 'Does the session stay up?'],
                    ['4 Transport', 'Transport', 'Segment (TCP) / datagram (UDP)', 'TCP, UDP, port numbers', 'Is the port reachable (Test-NetConnection, nc)?'],
                    ['3 Network', 'Internet', 'Packet', 'IPv4, IPv6, ICMP, routers', 'ping the gateway, then a remote IP; traceroute'],
                    ['2 Data link', 'Link', 'Frame', 'Ethernet, Wi-Fi (802.11), MAC addresses, switches, ARP', 'MAC/ARP table, VLAN on the port, Wi-Fi association'],
                    ['1 Physical', 'Link', 'Bits', 'Copper, fibre, radio, connectors, NIC', 'Link light, cable test, signal strength'],
                ])
                + '<p><strong>Encapsulation.</strong> On the way out, each layer wraps the data from the layer above with its own header: '
                  'the transport layer adds port numbers (a segment), the network layer adds source and destination IP addresses (a packet), '
                  'and the data-link layer adds source and destination MAC addresses plus a frame check sequence (a frame). '
                  'The receiver removes the headers in reverse order. A router rewrites the layer-2 frame on every hop but keeps the '
                  'layer-3 addresses (NAT is the exception, covered in Chapter 4).</p>'
                  '<h3>Three ways to work a problem</h3><ul>'
                  '<li><strong>Bottom-up</strong> — start at the cable and climb. Best when the symptom is “nothing works” on one device.</li>'
                  '<li><strong>Top-down</strong> — start at the application. Best when other apps work and one fails.</li>'
                  '<li><strong>Divide and conquer</strong> — start in the middle (usually <code>ping</code> to an IP). A success rules out layers 1–3 on that path; a failure rules out the application.</li></ul>'
                  '<p>Whichever you pick, write the layer next to each test in the ticket. “Layer 3: ping 10.20.30.1 — 4/4 replies” tells the next technician what is already proven.</p>'
                + check(('A user can reach websites by IP address but not by name. Lowest layer to investigate?', 'Application-layer name resolution (DNS) — layers 1–3 are already proven by the IP test.'),
                        ('Which device works mainly at layer 2?', 'A switch (it forwards frames by MAC address).'),
                        ('What does a router change in every frame it forwards?', 'The layer-2 source and destination MAC addresses (and it decrements the IP TTL).')),
    },
    (1, 2): {
        'objectives': [
            'Identify the network address, broadcast address and usable host range for an IPv4 prefix up to /30',
            'Distinguish private (RFC 1918), APIPA/link-local, loopback and public IPv4 addresses',
            'Calculate the number of usable hosts for a prefix length (2^h − 2)',
            'Recognise IPv6 global unicast, link-local and unique local addresses and explain why LAN subnets are /64',
        ],
        'plain': 'An IPv4 address is 32 bits written as four numbers. The prefix (or mask) says how many bits name the network; '
                 'the rest name the host. Two addresses in every IPv4 subnet are reserved, which is why a /24 has 254 usable hosts, not 256.',
        'html': '<h3>Reading a prefix</h3>'
                + table(['Prefix', 'Mask', 'Addresses', 'Usable hosts', 'Typical use'], [
                    ['/24', '255.255.255.0', '256', '254', 'A user VLAN'],
                    ['/25', '255.255.255.128', '128', '126', 'Half a /24'],
                    ['/26', '255.255.255.192', '64', '62', 'Small department'],
                    ['/27', '255.255.255.224', '32', '30', 'Printers, small server segment'],
                    ['/28', '255.255.255.240', '16', '14', 'Management segment'],
                    ['/30', '255.255.255.252', '4', '2', 'Point-to-point router link'],
                ])
                + '<p><strong>Worked example.</strong> 192.168.10.77/26: a /26 block is 64 addresses, so blocks start at .0, .64, .128 and .192. '
                  '.77 falls in the .64 block. Network address 192.168.10.64, broadcast 192.168.10.127, usable hosts .65–.126 (62 hosts), '
                  'and the gateway is usually the first or last usable address by local convention.</p>'
                  '<h3>Special IPv4 ranges</h3>'
                + table(['Range', 'Meaning'], [
                    ['10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16', 'Private (RFC 1918). Not routed on the public Internet; reaches it through NAT.'],
                    ['169.254.0.0/16', 'Link-local / APIPA. The host gave itself an address because DHCP did not answer.'],
                    ['127.0.0.0/8', 'Loopback. 127.0.0.1 is “this host”.'],
                    ['100.64.0.0/10', 'Shared address space for carrier-grade NAT (RFC 6598) — seen on some ISP WAN links.'],
                ])
                + '<h3>IPv6 in one screen</h3><p>IPv6 addresses are 128 bits written in hexadecimal, eight groups separated by colons; '
                  'leading zeros can be dropped and one run of all-zero groups can be written as <code>::</code>. '
                  'LAN subnets are /64: the first 64 bits name the network, the last 64 the interface, which is what lets SLAAC (stateless address autoconfiguration) work.</p>'
                + table(['Prefix', 'Type'], [
                    ['2000::/3', 'Global unicast — routable on the Internet'],
                    ['fe80::/10', 'Link-local — every IPv6 interface has one; not routed'],
                    ['fc00::/7 (in practice fd00::/8)', 'Unique local — private, like RFC 1918'],
                    ['::1', 'Loopback'],
                ])
                + '<p>A host that shows only an <code>fe80::</code> address has no global IPv6 configuration: check router advertisements or DHCPv6 on that segment.</p>'
                + check(('How many usable hosts does a /28 provide?', '14 (16 addresses minus network and broadcast).'),
                        ('Is 192.168.11.50 inside 192.168.10.0/23?', 'Yes — a /23 covers 192.168.10.0 to 192.168.11.255.'),
                        ('A laptop shows 169.254.3.9. What failed?', 'It did not get a DHCP lease; check link, VLAN and DHCP before DNS.')),
    },
    (1, 3): {
        'objectives': [
            'Compare TCP and UDP on connection setup, reliability, ordering and overhead',
            'Describe the TCP three-way handshake and how sequence numbers, acknowledgements and windows provide reliability',
            'Match common services to their port numbers and transport protocol',
            'Use a port test (Test-NetConnection or nc) to tell a closed port from an unreachable host',
        ],
        'plain': 'TCP is a phone call: it sets up a connection, numbers everything and resends what is lost. UDP is a postcard: '
                 'it just sends. Port numbers tell the receiving host which service a segment is for.',
        'html': table(['', 'TCP', 'UDP'], [
                    ['Connection', 'Three-way handshake: SYN → SYN-ACK → ACK', 'None'],
                    ['Reliability', 'Acknowledgements and retransmission', 'None at the transport layer (the app may add its own)'],
                    ['Ordering', 'Sequence numbers put data back in order', 'Not guaranteed'],
                    ['Flow control', 'Window size limits unacknowledged data', 'None'],
                    ['Typical uses', 'Web (HTTP/1.1, HTTP/2), mail, file transfer, SSH, RDP', 'DNS queries, DHCP, NTP, SNMP, VoIP media, QUIC (HTTP/3)'],
                ])
                + '<p>Ports 0–1023 are “well-known”, 1024–49151 are registered, and 49152–65535 are the dynamic (ephemeral) range IANA recommends for client source ports. '
                  'A connection is identified by five values: protocol, source IP, source port, destination IP and destination port.</p>'
                  '<h3>Ports a network technician says out loud</h3>'
                + table(['Port', 'Transport', 'Service'], [
                    ['20/21', 'TCP', 'FTP (data/control) — cleartext; prefer SFTP'],
                    ['22', 'TCP', 'SSH and SFTP'],
                    ['23', 'TCP', 'Telnet — cleartext; do not use for management'],
                    ['25 / 587', 'TCP', 'SMTP relay / mail submission'],
                    ['53', 'UDP and TCP', 'DNS (TCP for large responses and zone transfers)'],
                    ['67/68', 'UDP', 'DHCP server/client'],
                    ['80 / 443', 'TCP (443 also UDP for HTTP/3)', 'HTTP / HTTPS'],
                    ['110 / 995, 143 / 993', 'TCP', 'POP3 / POP3S, IMAP / IMAPS'],
                    ['123', 'UDP', 'NTP time'],
                    ['161 / 162', 'UDP', 'SNMP polling / traps'],
                    ['389 / 636', 'TCP', 'LDAP / LDAPS'],
                    ['445', 'TCP', 'SMB file sharing'],
                    ['514', 'UDP (TCP/TLS options exist)', 'Syslog'],
                    ['3389', 'TCP (and UDP)', 'Remote Desktop'],
                ])
                + '<h3>Testing a port, not just a host</h3><p><code>ping</code> uses ICMP and proves only that the host answers ICMP. '
                  'To test a service, connect to its port: on Windows <code>Test-NetConnection mail.example.com -Port 587</code>; on Linux/macOS <code>nc -vz mail.example.com 587</code>. '
                  '“TcpTestSucceeded: False” with a successful ping points at a firewall rule or a stopped service, not at routing.</p>'
                + check(('Which transport does DHCP use?', 'UDP (server port 67, client port 68).'),
                        ('A packet capture shows SYN, then RST from the server. What does that mean?', 'The host is reachable but nothing is listening on that port (or a device actively refused it).'),
                        ('Why does voice media usually use UDP?', 'A late retransmitted packet is useless for live audio; low delay matters more than recovering every packet.')),
    },
    # ------------------------------------------------------------------ Chapter 2
    (2, 1): {
        'objectives': [
            'Explain how a switch learns source MAC addresses, forwards known unicast frames and floods broadcasts and unknown unicasts',
            'Distinguish a collision domain from a broadcast domain',
            'Read a MAC address table to find the port a device is on',
            'Explain why a layer-2 loop causes a broadcast storm and how Spanning Tree (STP/RSTP) and BPDU Guard prevent it',
        ],
        'plain': 'A switch keeps a table of which MAC address lives on which port. It learns from the source address of every frame '
                 'and forwards by the destination. Loops are the big danger at layer 2, so switches run Spanning Tree to block redundant paths.',
        'html': '<h3>Learn, forward, flood</h3><ol>'
                '<li><strong>Learn:</strong> a frame arrives on port 5 from MAC aa:bb:cc:00:00:01, so the switch records “…:01 is on port 5”.</li>'
                '<li><strong>Forward:</strong> if the destination MAC is in the table, the frame goes out that one port only.</li>'
                '<li><strong>Flood:</strong> broadcasts (ff:ff:ff:ff:ff:ff), and unicasts to unknown MACs, go out every port in the VLAN except the one they came in on.</li>'
                '<li><strong>Age:</strong> entries that are not refreshed expire (300 seconds is a common default), so moved devices are relearned.</li></ol>'
                + table(['Term', 'Boundary', 'Why it matters'], [
                    ['Collision domain', 'Each switch port (full duplex has no collisions)', 'Hubs shared one collision domain; switches ended that'],
                    ['Broadcast domain', 'The VLAN — stopped by a router or layer-3 interface', 'Every host in it processes every broadcast (ARP, DHCP Discover)'],
                ])
                + '<p><strong>Finding a device.</strong> On many switches <code>show mac address-table address aabb.cc00.0001</code> returns the VLAN and port. '
                  'If the port is an uplink to another switch, follow it and repeat until you reach an access port.</p>'
                  '<h3>Loops and Spanning Tree</h3><p>Ethernet frames have no hop limit. If two switches are cabled together twice, a broadcast circulates for ever, '
                  'multiplying until links saturate and CPUs peg: a <strong>broadcast storm</strong>. Spanning Tree Protocol (IEEE 802.1D; Rapid STP is 802.1w, now part of 802.1Q) '
                  'elects a root bridge and puts redundant ports into a blocking/discarding state, so there is one active path and a standby path if a link fails.</p>'
                  '<ul><li><strong>PortFast / edge port</strong> lets an access port forward immediately because it should only ever see an end device.</li>'
                  '<li><strong>BPDU Guard</strong> shuts (err-disables) an edge port that receives STP BPDUs, which usually means someone plugged in a switch or made a loop.</li>'
                  '<li>An err-disabled port is a protection that worked: find the cause, fix it, then re-enable the port under change control.</li></ul>'
                + check(('A switch receives a frame for a MAC it has never seen. What does it do?', 'Floods it out all ports in that VLAN except the ingress port.'),
                        ('Which device ends a broadcast domain?', 'A router (or layer-3 switch interface).'),
                        ('Users report the whole floor is slow and switch CPU is at 100% right after someone patched a cable between two wall jacks. Likely cause?', 'A layer-2 loop causing a broadcast storm — look for the new cable and STP/BPDU Guard events.')),
    },
    (2, 2): {
        'objectives': [
            'Explain how a VLAN creates a separate broadcast domain on shared switch hardware',
            'Compare access ports and 802.1Q trunk ports, including the native VLAN and allowed-VLAN list',
            'Explain why traffic between VLANs needs a router or layer-3 switch (SVI or router-on-a-stick)',
            'Diagnose a wrong-VLAN symptom from a host’s address and the switchport configuration',
        ],
        'plain': 'A VLAN is a separate network that happens to share switches with other networks. Access ports belong to one VLAN; '
                 'trunks carry many VLANs between switches by tagging each frame. A device on the wrong VLAN has a link light and still cannot reach its servers.',
        'html': table(['', 'Access port', 'Trunk port'], [
                    ['Carries', 'One data VLAN (optionally one voice VLAN)', 'Many VLANs'],
                    ['Tagging', 'Frames untagged to the end device', 'IEEE 802.1Q tag added (4 bytes, 12-bit VLAN ID 1–4094); the native VLAN is sent untagged'],
                    ['Connects to', 'PCs, printers, phones, APs in local mode', 'Other switches, routers, hypervisor hosts, some APs'],
                    ['Common faults', 'Port in the wrong VLAN', 'VLAN missing from the allowed list; native VLAN mismatch between ends'],
                ])
                + '<h3>Moving between VLANs</h3><p>Hosts in different VLANs are in different IP subnets, so they talk through their default gateway. '
                  'The gateway is either a <strong>switch virtual interface (SVI)</strong> on a layer-3 switch (for example interface Vlan40 with 10.20.40.1/24) '
                  'or a router subinterface per VLAN on one trunk link (“router-on-a-stick”). Without one, two VLANs on the same switch cannot communicate at all.</p>'
                  '<h3>The wrong-VLAN ticket</h3><ol>'
                  '<li>Compare the user’s IP with a working neighbour. 10.20.30.x versus everyone else on 10.20.40.x is the classic sign.</li>'
                  '<li>Trace the wall jack to the switchport (patch-panel labels or the MAC table).</li>'
                  '<li>Read the port: <code>show interfaces status</code> or <code>show running-config interface Gi1/0/12</code>.</li>'
                  '<li>If you have rights and a change ticket, set the access VLAN; otherwise escalate with the evidence.</li>'
                  '<li>Verify: renew the lease, ping the gateway and the server, and record before/after addresses.</li></ol>'
                + check(('How many bits identify the VLAN in an 802.1Q tag?', '12 bits (VLAN IDs 1–4094 are usable).'),
                        ('Two PCs on the same switch, VLAN 10 and VLAN 20, cannot ping each other. Is the switch broken?', 'No — that is the design. Traffic between VLANs needs a layer-3 gateway.'),
                        ('A new VLAN works on the core but not on an access switch across a trunk. First check?', 'Whether the VLAN exists on the access switch and is in the trunk’s allowed-VLAN list.')),
    },
    (2, 3): {
        'objectives': [
            'Select a copper category or fibre type for a given speed and distance',
            'Apply the 100-metre twisted-pair channel limit and the T568A/T568B wiring standards',
            'Match PoE standards (802.3af/at/bt) to device power needs',
            'Choose the right test tool (continuity tester, certifier, toner, OTDR, optical power meter) for a physical-layer symptom',
        ],
        'plain': 'Most “the network is flaky” tickets that affect one desk are physical. Copper Ethernet runs up to 100 metres; fibre goes much further and ignores electrical noise. '
                 'Pick the right test tool before you replace any switch.',
        'html': '<h3>Twisted-pair copper (TIA-568)</h3>'
                + table(['Category', 'Common Ethernet use', 'Distance'], [
                    ['Cat 5e', '1000BASE-T (1 Gb/s)', '100 m channel'],
                    ['Cat 6', '1 Gb/s at 100 m; 10GBASE-T up to about 55 m', '100 m / ~55 m for 10G'],
                    ['Cat 6A', '10GBASE-T', '100 m channel'],
                    ['Cat 8', '25G/40GBASE-T in data centres', 'Up to 30 m'],
                ])
                + '<p>The 100 m channel is typically 90 m of permanent horizontal cable plus up to 10 m of patch cords. '
                  'T568A and T568B differ only in swapping the orange and green pairs; use one standard consistently at both ends. '
                  'Modern ports auto-negotiate crossover (Auto-MDIX), so crossover cables are rarely needed.</p>'
                  '<h3>Power over Ethernet</h3>'
                + table(['Standard', 'Power at the switch port (PSE)', 'Power available to the device (PD)'], [
                    ['IEEE 802.3af (PoE)', '15.4 W', '12.95 W'],
                    ['IEEE 802.3at (PoE+)', '30 W', '25.5 W'],
                    ['IEEE 802.3bt Type 3', '60 W', '51 W'],
                    ['IEEE 802.3bt Type 4', '90 W', '71.3 W'],
                ])
                + '<p>A switch also has a total PoE budget. APs or phones that reboot when more devices are added often point to an exhausted budget, not faulty devices.</p>'
                  '<h3>Fibre</h3>'
                + table(['Type', 'Light source / wavelength', 'Typical reach'], [
                    ['Multimode (OM3/OM4)', 'VCSEL lasers, usually 850 nm', 'Hundreds of metres (inside a building or campus)'],
                    ['Single-mode (OS2)', 'Lasers at 1310/1550 nm', 'Kilometres (between buildings and to providers)'],
                ])
                + '<p>Common connectors are LC (small, most common on SFP optics) and SC. The optic (SFP, SFP+, QSFP) and the fibre type must match at both ends. '
                  'Dirty end faces are a leading cause of fibre faults: inspect and clean before replacing optics.</p>'
                  '<h3>Pick the tool</h3>'
                + table(['Symptom', 'Tool'], [
                    ['Which wall jack goes to which panel port?', 'Tone generator and probe'],
                    ['Is each conductor connected to the right pin?', 'Continuity / wire-map tester'],
                    ['Link works at 100 Mb/s but not 1 Gb/s, or fails certification', 'Cable certifier (NEXT, return loss, split pairs, length)'],
                    ['Is there light, and how strong?', 'Optical power meter and light source'],
                    ['Where along a long fibre is the break or bad splice?', 'OTDR (optical time-domain reflectometer)'],
                ])
                + check(('A 10GBASE-T link must run 85 m. Cat 6 or Cat 6A?', 'Cat 6A — Cat 6 supports 10GBASE-T only to about 55 m.'),
                        ('A wire-map test passes but the cable fails certification with split pairs. What is wrong?', 'Conductors are on the right pins but from different twisted pairs, so crosstalk is high; re-terminate to the standard.'),
                        ('A PoE+ camera needs 22 W. Is an 802.3af port enough?', 'No — 802.3af delivers 12.95 W at the device; it needs PoE+ (802.3at) or better.')),
    },
    # ------------------------------------------------------------------ Chapter 3
    (3, 1): {
        'objectives': [
            'Explain how a router selects a route using longest-prefix match',
            'Read a routing table and identify connected, static, dynamic and default routes',
            'Compare static routing, interior dynamic routing (OSPF) and exterior routing (BGP) at a conceptual level',
            'Explain how first-hop redundancy (VRRP/HSRP) keeps a default gateway available',
        ],
        'plain': 'A router forwards packets between networks by looking up the destination IP address in its routing table. '
                 'The most specific matching route wins. If nothing more specific matches, the default route (0.0.0.0/0) is used.',
        'html': '<h3>Where routes come from</h3>'
                + table(['Source', 'How it appears', 'Notes'], [
                    ['Connected', 'Automatically, for every interface that is up with an address', 'Interface down = route gone'],
                    ['Static', 'Typed by an administrator', 'Predictable; does not adapt to failures unless tracked'],
                    ['Dynamic — OSPF', 'Learned from neighbours inside one organisation', 'Link-state; converges quickly; uses cost'],
                    ['Dynamic — BGP', 'Exchanged between organisations (autonomous systems)', 'Path-vector; policy-driven; the routing protocol of the Internet'],
                    ['Default (0.0.0.0/0)', 'Static or learned', 'The route of last resort — usually toward the ISP'],
                ])
                + '<p><strong>Longest-prefix match.</strong> A router holding 10.0.0.0/8, 10.20.0.0/16 and 10.20.30.0/24 sends a packet for 10.20.30.9 '
                  'using the /24, because it is the most specific match. If two sources offer the same prefix, the router prefers the source it trusts more '
                  '(on Cisco IOS this is administrative distance: connected 0, static 1, OSPF 110 by default), then the lower metric.</p>'
                  '<h3>Reading a table</h3><p>Look for three things: is there a route to the destination prefix, which next hop or exit interface it uses, '
                  'and is there a default route? “No route to host” and a missing default route are routing problems; a route that points out a down interface is a layer-1/2 problem.</p>'
                  '<h3>Keeping the gateway up</h3><p>Hosts usually have one default gateway address. VRRP (an IETF standard) and HSRP (Cisco) let two routers share a virtual gateway IP, '
                  'so if the active router fails the standby takes over the same address and hosts never notice.</p>'
                  '<h3>traceroute</h3><p><code>tracert</code>/<code>traceroute</code> lists each router hop by provoking ICMP “time exceeded” replies. '
                  'A row of <code>* * *</code> followed by later hops that answer means that router does not reply to the probes; it is still forwarding. Only a trace that stops for good is evidence of a break.</p>'
                + check(('Routes exist for 172.16.0.0/12 and 172.16.5.0/24. Which carries a packet to 172.16.5.20?', 'The /24 — longest-prefix match.'),
                        ('What does 0.0.0.0/0 mean in a routing table?', 'The default route: used when no more specific route matches.'),
                        ('A router interface goes down. What happens to its connected route?', 'It is removed from the routing table.')),
    },
    (3, 2): {
        'objectives': [
            'Identify the demarcation point and which party owns each device on a WAN path',
            'Compare common access technologies (fibre Ethernet, cable, DSL, fixed wireless/5G, satellite) on speed, latency and failure modes',
            'Describe site-to-site connectivity options: dedicated circuits, MPLS, SD-WAN and IPsec VPN',
            'Assemble the evidence an ISP needs to accept a fault ticket',
        ],
        'plain': 'The WAN is where your network meets someone else’s. Know exactly where the hand-off (demarc) is, what you own on each side, '
                 'and what proof the provider needs before they will dispatch.',
        'html': table(['Access type', 'Strengths', 'Watch for'], [
                    ['Fibre Ethernet', 'High, symmetric bandwidth; low latency', 'Optic or light-level faults; construction cuts'],
                    ['Cable (DOCSIS)', 'Widely available, high download speed', 'Shared segment congestion; asymmetric upload'],
                    ['DSL', 'Uses existing phone copper', 'Speed falls with distance from the exchange'],
                    ['Fixed wireless / 5G', 'Fast to deploy; good backup link', 'Signal varies with weather, obstacles and load'],
                    ['Satellite (GEO and LEO)', 'Reaches remote sites', 'GEO adds hundreds of ms of latency; LEO is much lower but still variable'],
                ])
                + '<h3>Who owns what</h3><p>The <strong>demarcation point</strong> is where the provider’s responsibility ends: often a modem, an optical terminal or a smart jack in a comms room. '
                  'Record for every site: circuit ID, demarc location, provider support number, and whether the edge router is yours or managed by the provider.</p>'
                  '<h3>Joining sites</h3><ul>'
                  '<li><strong>Dedicated circuit / Ethernet private line</strong> — predictable, more expensive.</li>'
                  '<li><strong>MPLS</strong> — provider-run private WAN with traffic classes.</li>'
                  '<li><strong>Site-to-site IPsec VPN</strong> — encrypted tunnels over ordinary Internet links. Tunnel mode encapsulates the whole original packet.</li>'
                  '<li><strong>SD-WAN</strong> — software that steers traffic across several links (for example fibre plus 5G) by application and link health.</li></ul>'
                  '<h3>Opening an ISP ticket</h3><ol>'
                  '<li>Circuit ID and site address.</li><li>Time the fault began and whether it is total or intermittent.</li>'
                  '<li>Edge interface status and, for fibre, light levels.</li><li>Ping and traceroute results from the edge router to the provider gateway and beyond.</li>'
                  '<li>What you already ruled out (power-cycled CPE, swapped patch cord, no recent changes).</li></ol>'
                + check(('Your edge router’s WAN interface is up but it cannot ping the provider gateway. Whose side do you prove first?', 'Your own — interface errors, addressing (static vs DHCP as the ISP requires) and cabling to the demarc — then open the ISP ticket with that evidence.'),
                        ('Why is satellite latency higher than fibre?', 'Signals travel to orbit and back; geostationary satellites are about 36,000 km up.'),
                        ('What does SD-WAN add over a single VPN tunnel?', 'Path selection across several links by application and measured link quality.')),
    },
    (3, 3): {
        'objectives': [
            'Compare Wi-Fi generations (Wi-Fi 4 to Wi-Fi 7) by IEEE standard, frequency bands and key features',
            'Plan non-overlapping channels and channel widths to limit co-channel interference',
            'Select an appropriate WLAN security mode (WPA3-Personal, WPA3-Enterprise/802.1X, OWE) and reject obsolete ones (WEP, TKIP)',
            'Interpret signal strength (RSSI) and signal-to-noise ratio when troubleshooting coverage and capacity',
        ],
        'plain': 'Enterprise Wi-Fi is a shared radio channel, not a cable. Capacity depends on how many devices share each channel, '
                 'how strong and clean the signal is, and which standards the clients support. Security is now WPA3, or WPA2 where older devices still require it.',
        'html': table(['Name', 'IEEE standard', 'Bands', 'Notes'], [
                    ['Wi-Fi 4', '802.11n', '2.4 and 5 GHz', 'MIMO; up to 40 MHz channels'],
                    ['Wi-Fi 5', '802.11ac', '5 GHz', 'Up to 160 MHz channels; downlink MU-MIMO'],
                    ['Wi-Fi 6', '802.11ax', '2.4 and 5 GHz', 'OFDMA and target wake time — better in dense areas'],
                    ['Wi-Fi 6E', '802.11ax', 'adds 6 GHz', 'Much more clean spectrum; WPA3 or OWE required on 6 GHz'],
                    ['Wi-Fi 7', '802.11be', '2.4, 5 and 6 GHz', '320 MHz channels (6 GHz only), multi-link operation (MLO), 4096-QAM'],
                ])
                + '<h3>Channels</h3><p>In the 2.4 GHz band only three 20 MHz channels do not overlap in most regulatory domains (1, 6 and 11 in North America), '
                  'so dense 2.4 GHz deployments fight themselves. 5 GHz and 6 GHz offer many more channels. Wider channels raise peak speed but reduce the number of '
                  'separate channels available, so dense offices usually use 20 or 40 MHz at 5 GHz. Neighbouring APs on the same channel share airtime (co-channel contention).</p>'
                  '<h3>Security modes</h3>'
                + table(['Mode', 'Use it?', 'Why'], [
                    ['WPA3-Enterprise (802.1X/EAP)', 'Yes — staff', 'Per-user or per-device credentials; EAP-TLS uses certificates for mutual authentication'],
                    ['WPA3-Personal (SAE)', 'Yes — small sites', 'Resists offline guessing of the passphrase; still one shared secret'],
                    ['OWE (Wi-Fi Enhanced Open)', 'Yes — open guest networks', 'Encrypts open networks without a password'],
                    ['WPA2 (AES/CCMP)', 'Only for legacy clients', 'Use WPA3 transition mode where needed, never on 6 GHz'],
                    ['WEP, WPA/TKIP', 'No', 'Broken and removed from current certification'],
                ])
                + '<h3>Reading the numbers</h3><p>RSSI is received signal strength in dBm; closer to zero is stronger (−55 dBm is stronger than −75 dBm). '
                  'SNR is signal minus noise in dB; higher is better. Many enterprise design guides target about −67 dBm or stronger with an SNR of 25 dB or more for voice-grade coverage; follow your vendor’s design guide. '
                  'Strong signal with poor throughput suggests contention or interference; weak signal suggests coverage, AP placement or a client roaming poorly.</p>'
                + check(('Which Wi-Fi generation first added the 6 GHz band?', 'Wi-Fi 6E (802.11ax in 6 GHz).'),
                        ('An office uses 2.4 GHz channels 1, 3, 6, 9 and 11. What is wrong?', 'Channels 3 and 9 overlap their neighbours; use only 1, 6 and 11.'),
                        ('Which security mode gives each employee their own credentials?', 'WPA3-Enterprise (or WPA2-Enterprise) with 802.1X.')),
    },
}

NETOPS_CORE.update({
    # ------------------------------------------------------------------ Chapter 4
    (4, 1): {
        'objectives': [
            'Sequence the DHCP DORA exchange (Discover, Offer, Request, Acknowledge) and name the ports it uses',
            'Configure the parts of a scope: range, exclusions, reservations, lease time and options (router, DNS, domain name)',
            'Explain why a DHCP relay (helper address) is needed when clients and server are on different subnets',
            'Distinguish client-side, scope and rogue-server DHCP failures from their symptoms',
        ],
        'plain': 'DHCP hands out addresses so nobody types them by hand. The client shouts for a server, takes an offer, and renews before the lease runs out. '
                 'When DHCP fails, clients fall back to 169.254.x.x and nothing beyond the local link works.',
        'html': '<h3>DORA</h3><ol>'
                '<li><strong>Discover</strong> — the client broadcasts from UDP 68 to UDP 67: “any DHCP servers?”</li>'
                '<li><strong>Offer</strong> — a server offers an address and options.</li>'
                '<li><strong>Request</strong> — the client asks for the offered address (broadcast, so other servers know it chose).</li>'
                '<li><strong>Acknowledge</strong> — the server confirms; the lease starts.</li></ol>'
                '<p>Clients try to renew with the same server at half the lease time (T1) and with any server at 87.5% (T2). '
                '<code>ipconfig /release</code> and <code>/renew</code> on Windows, or <code>dhclient</code>/<code>NetworkManager</code> on Linux, force the cycle.</p>'
                + table(['Scope setting', 'Purpose'], [
                    ['Range / pool', 'Addresses the server may lease'],
                    ['Exclusions', 'Addresses inside the range kept for static devices'],
                    ['Reservations', 'Always give one MAC address the same IP (printers, APs)'],
                    ['Lease time', 'Short for guest Wi-Fi with many transient devices; longer for fixed desktops'],
                    ['Option 3', 'Default gateway (router)'],
                    ['Option 6', 'DNS servers'],
                    ['Option 15', 'DNS domain name'],
                ])
                + '<h3>Across subnets</h3><p>DHCP Discover is a broadcast, and routers do not forward broadcasts. A <strong>relay agent</strong> on the client VLAN’s gateway '
                  '(for example <code>ip helper-address 10.0.0.10</code> on Cisco, or “DHCP relay” on other platforms) converts the broadcast into a unicast to the server and tells it which subnet the client is on.</p>'
                  '<h3>Three failure patterns</h3>'
                + table(['Pattern', 'Symptom', 'First check'], [
                    ['One client', 'APIPA on one device; neighbours fine', 'Link, VLAN, DHCP Client service, release/renew'],
                    ['Whole VLAN', 'Everyone new gets APIPA; existing leases still work', 'Scope exhausted or relay missing after a change'],
                    ['Rogue server', 'Clients get addresses but the wrong gateway/DNS', 'Compare the DHCP server address in ipconfig /all; enable DHCP snooping on switches'],
                ])
                + check(('Which DHCP message does the client send first, and is it unicast or broadcast?', 'Discover, broadcast.'),
                        ('A new VLAN’s clients all get 169.254 addresses; the DHCP server has a scope for it. What is likely missing?', 'The DHCP relay (helper address) on the VLAN’s gateway interface.'),
                        ('Which option tells clients their DNS servers?', 'Option 6.')),
    },
    (4, 2): {
        'objectives': [
            'Trace a DNS lookup from the stub resolver through the recursive resolver to root, TLD and authoritative servers',
            'Identify the purpose of A, AAAA, CNAME, MX, NS, PTR, TXT, SRV and SOA records',
            'Explain how TTL and caching delay the visibility of DNS changes',
            'Interpret nslookup / dig / Resolve-DnsName results: NOERROR, NXDOMAIN, SERVFAIL and timeout',
        ],
        'plain': 'DNS turns names into addresses. Your PC asks a resolver; the resolver finds the answer by asking the root, the top-level domain and finally the server that owns the name, '
                 'then caches it for as long as the record’s TTL allows. Most “DNS changes aren’t working” tickets are caches doing their job.',
        'html': '<h3>One lookup</h3><ol>'
                '<li>The client’s stub resolver checks its own cache and hosts file, then asks its configured DNS server (from DHCP option 6).</li>'
                '<li>That <strong>recursive resolver</strong> checks its cache; if empty, it asks a root server, which refers it to the TLD servers (for example .com).</li>'
                '<li>The TLD servers refer it to the domain’s <strong>authoritative</strong> name servers (the NS records).</li>'
                '<li>The authoritative server answers; the resolver caches the answer for the TTL and returns it to the client.</li></ol>'
                + table(['Record', 'Maps'], [
                    ['A / AAAA', 'Name → IPv4 / IPv6 address'],
                    ['CNAME', 'Alias → canonical name'],
                    ['MX', 'Domain → mail servers, with preference values'],
                    ['NS', 'Zone → its authoritative name servers'],
                    ['PTR', 'IP address → name (reverse lookup)'],
                    ['TXT', 'Free text — used for SPF, DKIM and DMARC email authentication and domain verification'],
                    ['SRV', 'Service → host and port (used by Active Directory, SIP and others)'],
                    ['SOA', 'Zone metadata: primary server, serial number, timers'],
                ])
                + '<h3>Reading results</h3>'
                + table(['Result', 'Meaning', 'Next step'], [
                    ['NOERROR with an answer', 'The name resolved', 'If the app still fails, test the port (Chapter 1.3)'],
                    ['NXDOMAIN', 'The name does not exist (authoritatively)', 'Check spelling and DNS suffix; ask the zone owner'],
                    ['SERVFAIL', 'The resolver could not get a valid answer', 'Try another resolver; check DNSSEC or upstream reachability'],
                    ['Timed out', 'No reply from the DNS server', 'Layer 3/4: can you reach the server on UDP/TCP 53?'],
                ])
                + '<p>Useful commands: <code>nslookup name server</code>, <code>Resolve-DnsName name -Type MX</code> (PowerShell), <code>dig name AAAA</code>, '
                  '<code>ipconfig /displaydns</code> and <code>ipconfig /flushdns</code> (client cache only — it does not clear the resolver’s cache). '
                  '<strong>Split-horizon DNS</strong> returns different answers to internal and external clients for the same name; test from the same side as the user.</p>'
                + check(('A record was changed 10 minutes ago with a TTL of 3600. Why do some users still get the old address?', 'Resolvers and clients may cache the old answer for up to an hour.'),
                        ('Which record type tells other mail servers where to deliver mail for a domain?', 'MX.'),
                        ('nslookup returns NXDOMAIN for intranet.corp but a colleague resolves it. First check?', 'Which DNS server each of you is using (internal versus public resolver) and the DNS suffix.')),
    },
    (4, 3): {
        'objectives': [
            'Compare static NAT, dynamic NAT and PAT (overload), and explain why inbound connections need port forwarding',
            'Explain how a stateful firewall uses a connection table to allow return traffic',
            'Evaluate an ordered rule list using first-match and the implicit deny',
            'Place services in zones (inside, DMZ, outside) and justify the placement',
        ],
        'plain': 'NAT rewrites addresses at the edge so many private hosts can share public ones. A firewall decides which flows are allowed. '
                 'They are separate jobs that often live on the same box, and each can be the reason “the Internet works but my server is unreachable”.',
        'html': table(['Type', 'Mapping', 'Use'], [
                    ['Static NAT', 'One private ↔ one public address', 'Publishing a server'],
                    ['Dynamic NAT', 'Private → address from a public pool', 'Rare today'],
                    ['PAT / NAT overload', 'Many private → one public, distinguished by source port', 'Almost every home and office Internet edge'],
                    ['Port forwarding', 'Public IP:port → private IP:port', 'Allowing an inbound connection through PAT'],
                ])
                + '<p>With PAT, outbound connections work automatically because the edge records each translation. Unsolicited inbound connections have no translation to match, '
                  'so they need an explicit port-forward (and a firewall rule). Some ISPs place customers behind carrier-grade NAT (100.64.0.0/10), which makes inbound hosting impossible without the ISP’s help.</p>'
                  '<h3>Stateful filtering</h3><p>A stateful firewall tracks each connection (addresses, ports, protocol, state). Once an outbound flow is allowed, '
                  'replies are permitted automatically because they match the table entry. New flows still need a rule.</p>'
                  '<h3>Rule order</h3><p>Rules are evaluated top to bottom and the <strong>first match wins</strong>. Anything that matches no rule hits the <strong>implicit deny</strong> at the end. '
                  'Put specific rules above general ones and log denies you care about.</p>'
                + table(['#', 'Rule', 'Effect on a user browsing to 203.0.113.10:443'], [
                    ['1', 'Deny inside → 203.0.113.0/24 any', 'Matches first: blocked'],
                    ['2', 'Allow inside → any TCP 443', 'Never reached for that destination'],
                    ['—', 'Implicit deny all', ''],
                ])
                + '<h3>Zones</h3><p>A <strong>DMZ</strong> holds Internet-facing services (public web, mail relay) so that a compromise there does not land the attacker on the internal network. '
                  'Internal systems such as domain controllers never sit in the DMZ.</p>'
                + check(('Why does an internal web server need a port-forward to be reachable from the Internet behind PAT?', 'Unsolicited inbound traffic has no existing translation to match.'),
                        ('A permit rule for HTTPS sits below a broader deny for the same destination. Result?', 'The deny matches first; HTTPS is blocked.'),
                        ('Does a stateful firewall need a rule for reply traffic to an allowed outbound connection?', 'No — replies match the connection table.')),
    },
    # ------------------------------------------------------------------ Chapter 5
    (5, 1): {
        'objectives': [
            'Compare SNMP versions and explain polling (UDP 161) versus traps/informs (UDP 162)',
            'Rank syslog severities 0–7 and choose which to forward and alert on',
            'Interpret interface counters (utilisation, errors, CRC, discards) against a baseline',
            'Explain why synchronised time (NTP) and central log collection matter for troubleshooting and incident response',
        ],
        'plain': 'Monitoring tells you something is wrong before users do, and gives you evidence when they call. You need a baseline of “normal”, '
                 'devices that report to a central place, and clocks that agree so events line up.',
        'html': table(['Signal', 'What it tells you', 'Tool'], [
                    ['SNMP polling', 'Counters and status on a schedule (UDP 161)', 'NMS / monitoring platform'],
                    ['SNMP traps / informs', 'Device-initiated alerts (UDP 162)', 'NMS'],
                    ['Syslog', 'Event messages with severities', 'Central syslog server or SIEM'],
                    ['Flow data (NetFlow / IPFIX / sFlow)', 'Who talked to whom, how much, on which ports', 'Flow collector'],
                    ['Synthetic tests', 'Latency, loss and jitter to key services', 'Ping/HTTP probes'],
                ])
                + '<p><strong>SNMP versions.</strong> v1 and v2c authenticate with a community string sent in cleartext; v3 adds user authentication and encryption (authPriv). '
                  'Use v3 for anything you can, and never leave default communities such as “public” or “private” enabled with write access.</p>'
                  '<h3>Syslog severities</h3>'
                + table(['Level', 'Name', 'Level', 'Name'], [
                    ['0', 'Emergency', '4', 'Warning'],
                    ['1', 'Alert', '5', 'Notice'],
                    ['2', 'Critical', '6', 'Informational'],
                    ['3', 'Error', '7', 'Debug'],
                ])
                + '<p>Lower numbers are more severe. Debug (7) on a busy device can flood a collector; forward levels 0–5 or 0–6 by default and alert on the lowest few.</p>'
                  '<h3>Counters that matter</h3><ul>'
                  '<li><strong>Utilisation</strong> over time (not one sample) — sustained high utilisation with output drops means congestion.</li>'
                  '<li><strong>CRC / input errors</strong> — physical layer: cable, optic, or duplex mismatch.</li>'
                  '<li><strong>Discards / drops</strong> — buffers or QoS policy.</li>'
                  '<li><strong>Latency, loss, jitter</strong> — jitter (variation in delay) hurts voice and video even when average latency is fine.</li></ul>'
                  '<p>A <strong>baseline</strong> is a record of normal values at normal times. Without it, “the WAN is at 70%” is not evidence of anything. '
                  'Point every device at the same NTP sources so that logs from switches, firewalls and servers can be correlated by timestamp.</p>'
                + check(('Which SNMP version supports encryption?', 'SNMPv3 (authPriv).'),
                        ('Is syslog severity 2 more or less severe than 5?', 'More severe (2 = Critical, 5 = Notice).'),
                        ('An interface shows rising CRC errors but low utilisation. First suspect?', 'The physical layer — cable, optic/connector, or a duplex mismatch.')),
    },
    (5, 2): {
        'objectives': [
            'Replace insecure management protocols (Telnet, HTTP, SNMPv1/v2c, TFTP) with secure equivalents',
            'Configure centralised AAA (RADIUS or TACACS+) with a documented local fallback account',
            'Restrict management access by source network, out-of-band path or management VLAN',
            'Maintain device hygiene: default credentials changed, unused services and ports disabled, firmware current, configuration backed up',
        ],
        'plain': 'The management plane is how administrators reach a device. If it is weak, everything behind the device is weak. '
                 'Encrypt it, control who can use it and from where, and keep a record of every change.',
        'html': table(['Instead of', 'Use', 'Why'], [
                    ['Telnet (TCP 23)', 'SSH v2 (TCP 22)', 'Telnet sends credentials in cleartext'],
                    ['HTTP management', 'HTTPS with a valid certificate', 'Same reason'],
                    ['SNMPv1/v2c communities', 'SNMPv3 authPriv', 'Authentication and encryption'],
                    ['TFTP/FTP for configs', 'SCP/SFTP', 'Encrypted transfer'],
                    ['Shared admin login', 'Individual accounts via RADIUS/TACACS+', 'Accountability and easy revocation'],
                ])
                + '<h3>AAA</h3><p><strong>Authentication</strong> (who are you), <strong>authorisation</strong> (what may you do) and <strong>accounting</strong> (what did you do). '
                  'TACACS+ separates the three and can authorise individual commands, which is why it is common for network devices; RADIUS is common for network access (802.1X, VPN). '
                  'Keep one local emergency account with a strong, vaulted password for when the AAA servers are unreachable.</p>'
                  '<h3>Where management comes from</h3><ul>'
                  '<li>An access list on the VTY/SSH lines and web UI allowing only the management subnet.</li>'
                  '<li>A dedicated management VLAN, or an out-of-band network/console server that still works when production is down.</li>'
                  '<li>Login banners stating authorised use, per your organisation’s legal guidance.</li></ul>'
                  '<h3>Hygiene checklist</h3><ol>'
                  '<li>Default usernames and passwords changed before the device is connected.</li>'
                  '<li>Unused services (HTTP server, CDP/LLDP on untrusted edges where policy says so) and unused switch ports disabled or placed in an unused VLAN.</li>'
                  '<li>Firmware on a supported, patched release; vendor security advisories reviewed.</li>'
                  '<li>Running configuration saved and backed up off the device after every approved change.</li>'
                  '<li>Logging to the central server and NTP configured.</li></ol>'
                + check(('Why is Telnet unacceptable for device management?', 'It sends usernames, passwords and commands in cleartext.'),
                        ('Which AAA protocol can authorise individual CLI commands?', 'TACACS+.'),
                        ('Why keep a local admin account if you use TACACS+?', 'Emergency access when the AAA servers or the path to them is down.')),
    },
    (5, 3): {
        'objectives': [
            'Design network zones (users, servers, guest, IoT, management, DMZ) and the allowed flows between them',
            'Explain how segmentation limits the blast radius of a compromise and of broadcast or misconfiguration faults',
            'Compare enforcement tools: VLANs with ACLs, firewalls between zones, 802.1X/NAC with dynamic VLAN assignment, and microsegmentation',
            'Apply least privilege and zero-trust principles to inter-zone access',
        ],
        'plain': 'Segmentation means not putting everything on one flat network. Group devices by trust and purpose, allow only the traffic each group needs, '
                 'and a problem in one segment stays in that segment.',
        'html': table(['Zone', 'Typical members', 'Typical allowed flows'], [
                    ['Users', 'Staff laptops and desktops', 'To servers on business ports; to the Internet via proxy/firewall'],
                    ['Servers', 'File, app and directory servers', 'From users on specific ports; to backup and management'],
                    ['Guest', 'Visitor devices', 'Internet only; client isolation; nothing internal'],
                    ['IoT / OT', 'Cameras, sensors, building systems', 'Only to their controllers; no general Internet unless required'],
                    ['Management', 'Device management interfaces, jump hosts', 'From administrator workstations only'],
                    ['DMZ', 'Public-facing services', 'From the Internet on published ports; tightly limited to internal'],
                ])
                + '<h3>How it is enforced</h3><ul>'
                  '<li><strong>VLANs + ACLs</strong> — VLANs separate layer 2; ACLs on the layer-3 gateway limit what crosses between them.</li>'
                  '<li><strong>Firewalls between zones</strong> — stateful inspection and logging for important boundaries.</li>'
                  '<li><strong>802.1X / NAC</strong> — authenticate the device or user at the switchport or Wi-Fi, then place it in the right VLAN or apply a policy automatically.</li>'
                  '<li><strong>Microsegmentation</strong> — policy per workload (often in hypervisors or cloud security groups) to control east-west traffic inside a zone.</li></ul>'
                  '<h3>Zero trust in one sentence</h3><p>Do not grant access because a device is “inside”; verify identity and device health for each request and allow only what is needed (least privilege).</p>'
                  '<h3>Blast radius</h3><p>On a flat network, ransomware on one laptop can reach every server, and one looping cable affects every device. '
                  'With zones, the same events are contained to one segment and the rules between zones give you logs showing what was attempted.</p>'
                + check(('Which zone should a visitor’s phone land in, and what should it reach?', 'Guest — Internet only, with client isolation.'),
                        ('What does 802.1X add to VLAN segmentation?', 'It authenticates the user/device before granting network access and can assign the VLAN dynamically.'),
                        ('Name one benefit of segmentation besides security.', 'Smaller broadcast domains and fault containment (for example a loop or broadcast storm stays local).')),
    },
    # ------------------------------------------------------------------ Chapter 6
    (6, 1): {
        'objectives': [
            'Match common network symptoms to their most likely cause and first discriminating test',
            'Use scope (one user, one VLAN, one site, everyone) to narrow the fault domain before testing',
            'Distinguish look-alike faults (DNS versus routing, wrong VLAN versus DHCP failure, congestion versus duplex mismatch)',
        ],
        'plain': 'Most network faults are repeats. A pattern library is a table of symptoms you have seen before, the usual cause, and the one test that tells the look-alikes apart.',
        'html': table(['Symptom', 'Likely cause', 'Test that discriminates'], [
                    ['One host has 169.254.x.x', 'No DHCP lease: link, VLAN, client service', 'Link light; compare the switchport VLAN with a neighbour’s; release/renew'],
                    ['Many new clients get 169.254 on one VLAN', 'Scope exhausted or relay missing', 'Scope statistics; helper address on the gateway'],
                    ['Address and gateway look right but wrong subnet', 'Wrong access VLAN', 'Compare IP/subnet with neighbours; read the port config'],
                    ['Ping by IP works, by name fails', 'DNS', 'nslookup against the configured server and a known-good server'],
                    ['Gateway pings; Internet IPs do not', 'Upstream routing, NAT or firewall', 'traceroute; edge interface and NAT/firewall logs'],
                    ['Small packets work, large transfers stall', 'MTU / path-MTU discovery black hole (often over VPNs)', 'ping with “don’t fragment” and increasing size'],
                    ['Link up, slow, rising CRC or late-collision counters', 'Duplex mismatch or bad cable', 'Compare speed/duplex at both ends; cable test'],
                    ['Whole switch slow, CPU high, after a cabling change', 'Layer-2 loop / broadcast storm', 'STP topology changes; BPDU Guard err-disable logs'],
                    ['Clients get addresses with the wrong gateway', 'Rogue DHCP server', 'DHCP server field in ipconfig /all; DHCP snooping logs'],
                    ['Two devices drop off intermittently', 'Duplicate IP address', 'ARP table / “address conflict” event; arp -a from a neighbour'],
                    ['APs or phones reboot when more are added', 'PoE budget exceeded', 'Switch PoE power usage versus budget'],
                    ['Wi-Fi strong signal, poor throughput', 'Channel contention or interference', 'Channel utilisation; neighbouring APs on the same channel'],
                ])
                + '<h3>Scope first</h3><p>Before any test, ask how far the problem reaches. One user points at that device, its cable or its port; one VLAN at the gateway, DHCP scope or trunk; '
                  'one site at the WAN or edge; everyone at a shared service (DNS, identity, SaaS provider). Each answer removes most of the table.</p>'
                + check(('Users can reach file shares but every large download over the VPN stalls. Which pattern?', 'MTU / path-MTU black hole.'),
                        ('Half the clients on a VLAN suddenly have the wrong gateway. Which pattern and test?', 'Rogue DHCP — check the DHCP server address clients received.'),
                        ('Why ask about scope before testing?', 'It narrows the fault domain, so the first test can discriminate between few causes instead of many.')),
    },
    (6, 2): {
        'objectives': [
            'Apply a structured troubleshooting method: identify, theorise, test, plan, implement, verify, document',
            'Time-box each theory and escalate with evidence when the time box expires or the fix is outside your authority',
            'Communicate status during an incident on a predictable cadence with facts, impact, next step and next update time',
            'Decide when to roll back instead of pushing a fix forward',
        ],
        'plain': 'Pressure makes people skip steps. A written method, short time boxes and regular status updates keep an outage from turning into two outages.',
        'html': '<h3>A seven-step method</h3><ol>'
                '<li><strong>Identify the problem</strong> — gather symptoms, scope, recent changes; reproduce if safe.</li>'
                '<li><strong>Establish a theory</strong> of probable cause — start with the simple and the recently changed.</li>'
                '<li><strong>Test the theory</strong> — one discriminating test. If it is disproved, form a new theory or escalate.</li>'
                '<li><strong>Plan the fix</strong> — impact, rollback, approval (an emergency change is still a change).</li>'
                '<li><strong>Implement</strong> — one change at a time.</li>'
                '<li><strong>Verify full functionality</strong> — from the user’s side; add preventive measures if appropriate.</li>'
                '<li><strong>Document</strong> — findings, actions, outcome, and lessons.</li></ol>'
                '<h3>Time boxes and escalation</h3><p>Give each theory a fixed time (for example 15 minutes in a priority-1 outage). When it expires, escalate with what you tested and the results, '
                'even if you are “close”. Escalation is a hand-off of evidence, not an admission of failure.</p>'
                '<h3>Status updates</h3>'
                + table(['Element', 'Example'], [
                    ['What is affected', 'Staff at the north site cannot reach the Internet'],
                    ['Since when', 'Since 09:40'],
                    ['What we know', 'The ISP circuit is up; our edge firewall is dropping outbound traffic after a 09:35 rule change'],
                    ['Next step', 'Rolling back the 09:35 change'],
                    ['Next update', '10:15, or sooner if resolved'],
                ])
                + '<h3>Roll back or push forward?</h3><p>If the outage started with a change and you cannot fix forward within the time box, roll back to the last known good state, restore service, and investigate afterwards. '
                  'Making several untracked changes under pressure is how one incident becomes two.</p>'
                + check(('Your first theory is disproved. What are your two options?', 'Form a new theory and test it, or escalate with evidence.'),
                        ('What five things belong in an incident status update?', 'What is affected, since when, what is known, the next step, and when the next update will come.'),
                        ('A change at 09:35 preceded a 09:40 outage. What should be tested first?', 'The change — and rolling it back is often the fastest way to restore service.')),
    },
    (6, 3): {
        'objectives': [
            'Verify a fix from the user’s perspective and with before/after evidence',
            'Update the documentation a network depends on: diagrams, IP address records, configuration backups and the change record',
            'Write a knowledge-base article and a blameless post-incident review that another technician can act on',
        ],
        'plain': 'A ticket is not done when the light turns green. It is done when the user confirms it works, the evidence is attached, and the documentation matches the network you left behind.',
        'html': '<h3>Verify</h3><ul>'
                '<li>Ask the user to perform the task that failed — not just “can you ping”.</li>'
                '<li>Capture the same test before and after (for example traceroute, interface counters, DHCP lease) and attach both.</li>'
                '<li>Watch long enough to catch intermittent faults: an error counter that keeps rising means the fix did not hold.</li></ul>'
                '<h3>Keep documentation true</h3>'
                + table(['Document', 'Update when'], [
                    ['Physical diagram (layer 1)', 'Cables, patch panels, devices or rack positions change'],
                    ['Logical diagram (layers 2–3)', 'VLANs, subnets, routing or firewall zones change'],
                    ['IP address management (IPAM) records', 'Addresses, reservations or scopes change'],
                    ['Configuration backup', 'After every approved change — and compare (diff) with the previous version'],
                    ['Change record', 'Every change, including emergency ones, with the outcome'],
                ])
                + '<h3>Knowledge-base article</h3><p>Title by symptom (“New VLAN clients get 169.254 addresses”), then environment, cause, fix steps, verification, and when to escalate. '
                  'Write it for the technician who has never seen this before.</p>'
                  '<h3>Blameless post-incident review</h3><p>For significant incidents: timeline, impact, root cause and contributing factors, what went well, what to change (with an owner and due date). '
                  'Focus on how the system and process allowed the error, not on who made it; people report problems honestly when they are not punished for doing so.</p>'
                + check(('Why attach before-and-after evidence?', 'It proves what changed and lets the next technician trust the conclusion.'),
                        ('After changing a trunk’s allowed VLAN list, which documents need updating?', 'The configuration backup, the change record and the logical (layer 2) diagram.'),
                        ('What makes a post-incident review “blameless”?', 'It examines the process and system conditions that allowed the fault, not individual blame.')),
    },
})

CAPSTONE_OBJECTIVES = {
    1: ['Map each step of a guided ticket to the OSI layer it tests', 'Write test results as action → result pairs a peer can verify'],
    2: ['Isolate a single-user fault to port, cable, VLAN or host using comparison with a working neighbour', 'Document the jack, switchport and before/after addressing'],
    3: ['Assess a wireless capacity complaint using signal, channel and client-count evidence', 'Recommend a channel or band change and state how you would verify it'],
    4: ['Isolate an “Internet down” report across DHCP, DNS, NAT and firewall in a fixed order', 'Escalate with the evidence an ISP or firewall owner needs'],
    5: ['Audit a device configuration against a hardening checklist', 'Rank findings by risk and propose changes through change control'],
    6: ['Work a multi-fault scenario with the structured method and time boxes', 'Deliver a status update and a final ticket note with verification evidence'],
}
