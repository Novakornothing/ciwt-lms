"""Wave 1 SME Technical Depth Expansion for Novak LMS™ (NETOPS N10-009 lessons, 12-item NETOPS quizzes, 45-item Knowledge Tests A/B/C)."""
import json
from .svg_diagrams import LESSON_DIAGRAM_MAP, SVG_DIAGRAMS


def _tbl(headers, rows):
    th = ''.join(f'<th scope="col">{h}</th>' for h in headers)
    tb = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table class="port-table"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>'


def _cli(title, cmd_output, analysis):
    return (
        f'<div class="worked-example"><h4>CLI Verification &amp; Packet Walkthrough: {title}</h4>'
        f'<pre class="cli-block"><code>{cmd_output}</code></pre>'
        f'<p>{analysis}</p></div>'
    )


NETOPS_DEPTH_HTML = {
    (1, 1): (
        '<h3>N10-009 Deep Dive: Wire-Level Encapsulation, MTU / MSS Math &amp; Hop-by-Hop Header Rewrites</h3>'
        '<p>When an application payload leaves a workstation, each layer of the TCP/IP and ISO/IEC 7498-1 (OSI) stack prepends deterministic control metadata. '
        'At Layer 4, TCP (RFC 9293) adds a minimum 20-byte header (typically 32 bytes when RFC 7323 Timestamps and Window Scaling options are negotiated) containing 16-bit source and destination ports, a 32-bit sequence number, a 32-bit acknowledgment number, the 4-bit Data Offset, control flags (<code>SYN</code>, <code>ACK</code>, <code>FIN</code>, <code>RST</code>, <code>PSH</code>, <code>URG</code>), and a 16-bit receive window. '
        'UDP (RFC 768) prepends a fixed 8-byte header (16-bit source port, 16-bit destination port, 16-bit length, 16-bit checksum) with zero connection state. '
        'At Layer 3, IPv4 (RFC 791) adds a 20-byte base header including the 8-bit Time to Live (TTL), 8-bit Protocol field (<code>1</code> ICMP, <code>6</code> TCP, <code>17</code> UDP, <code>47</code> GRE, <code>50</code> ESP, <code>89</code> OSPF), 16-bit Total Length, 16-bit Identification, 3-bit Flags (<code>DF</code> Don\'t Fragment, <code>MF</code> More Fragments), 13-bit Fragment Offset, 16-bit Header Checksum, and 32-bit Source/Destination IPv4 addresses. '
        'IPv6 (RFC 8200) uses a fixed 40-byte header that eliminates the header checksum and hop-by-hop router fragmentation, replacing TTL with Hop Limit and Protocol with Next Header. '
        'At Layer 2, IEEE 802.3 Ethernet wraps the IP packet in a 14-byte header (6-byte Destination MAC, 6-byte Source MAC, 2-byte EtherType: <code>0x0800</code> IPv4, <code>0x0806</code> ARP, <code>0x86DD</code> IPv6, or <code>0x8100</code> IEEE 802.1Q tag) plus a 4-byte trailing Frame Check Sequence (FCS) computed via CRC-32.</p>'
        + _tbl(
            ['Encapsulation Scenario', 'L3 IP MTU', 'TCP Overhead', 'Max TCP MSS', 'Wire Frame Size (with L2)'],
            [
                ['Standard Untagged Ethernet (IEEE 802.3)', '1500 bytes', '20B IPv4 + 20B TCP', '1460 bytes', '1518 bytes (14B L2 + 4B FCS)'],
                ['IEEE 802.1Q Tagged Trunk (802.3ac)', '1500 bytes', '20B IPv4 + 20B TCP', '1460 bytes', '1522 bytes (+4B 802.1Q tag)'],
                ['GRE over IPsec Site-to-Site Tunnel', '1400 bytes', '24B GRE + 52–76B ESP/IP', '1360 bytes', '1514–1518 bytes on WAN egress'],
                ['VXLAN Overlay (UDP 4789, RFC 7348)', '1500 inner', '50B outer (VXLAN+UDP+IP+L2)', '1460 inner', '1550+ bytes (requires 1600–9000B underlay)'],
                ['Data Center Jumbo Frame (Storage/vMotion)', '9000 bytes', '20B IPv4 + 20B TCP', '8960 bytes', '9018 bytes untagged / 9022 bytes tagged'],
            ]
        )
        + _cli(
            'Inspecting Layer-2 MAC Rewrites, TTL Decrements &amp; PMTUD Black Holes with ip neigh and tcpdump',
            '$ ip -4 addr show dev eth0\n'
            '2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP qlen 1000\n'
            '    link/ether 00:50:56:9a:11:24 brd ff:ff:ff:ff:ff:ff\n'
            '    inet 10.20.30.45/24 brd 10.20.30.255 scope global dynamic eth0\n'
            '$ ip neigh show dev eth0\n'
            '10.20.30.1 lladdr 00:1c:73:00:0a:01 REACHABLE\n'
            '$ sudo tcpdump -enni eth0 "icmp or (tcp and port 443)" -c 3\n'
            '09:14:02.104 00:50:56:9a:11:24 > 00:1c:73:00:0a:01, ethertype IPv4 (0x0800), length 74: 10.20.30.45.51842 > 198.51.100.20.443: Flags [S], seq 2910441, win 64240, options [mss 1460,sackOK,TS,nop,wscale 7], length 0\n'
            '09:14:02.118 00:1c:73:00:0a:01 > 00:50:56:9a:11:24, ethertype IPv4 (0x0800), length 70: 172.16.254.2 > 10.20.30.45: ICMP 198.51.100.20 unreachable - need to frag (mtu 1400), length 36',
            'Notice how the outbound TCP SYN frame targets Destination MAC 00:1c:73:00:0a:01 (the local default gateway 10.20.30.1) while targeting Destination IP 198.51.100.20. '
            'At every Layer-3 hop, the router strips the ingress Ethernet header and FCS, decrements the IPv4 TTL by 1, recalculates the 16-bit IPv4 header checksum, looks up the egress next-hop MAC in its ARP/NDP cache, and writes a brand-new Layer-2 frame. '
            'The third line shows an ICMP Type 3 Code 4 ("Fragmentation Needed and DF Set", RFC 1191) returned by WAN router 172.16.254.2 advertising a 1400-byte tunnel MTU. '
            'If an overzealous firewall drops ICMP Type 3 Code 4 (or ICMPv6 Type 2 "Packet Too Big"), Path MTU Discovery (PMTUD) fails: small pings and TCP 3-way handshakes succeed, but TLS ServerHello certificates or bulk SMB transfers stall silently. '
            'Mitigate PMTUD black holes by permitting ICMP Unreachable/Packet-Too-Big messages and configuring TCP MSS clamping (<code>ip tcp adjust-mss 1360</code>) on VPN tunnel interfaces.'
        )
    ),
    (1, 2): (
        '<h3>N10-009 Deep Dive: Variable-Length Subnet Masking (VLSM), RFC Ranges &amp; IPv6 NDP / SLAAC Mechanics</h3>'
        '<p>Classless Inter-Domain Routing (CIDR, RFC 4632) and Variable-Length Subnet Masking (VLSM) allow network engineers to partition an address block without wasting IPv4 space. '
        'For any prefix length <code>/P</code> in IPv4, the number of host bits is <code>h = 32 - P</code>, the block size in the interesting octet is <code>2^(8 - (P mod 8))</code>, total addresses equal <code>2^h</code>, and usable host addresses equal <code>2^h - 2</code> (subtracting the all-zeros network ID and all-ones directed broadcast address). '
        'The sole exception is RFC 3021 <code>/31</code> point-to-point router links, which yield 2 usable addresses with no directed broadcast, and <code>/32</code> host loopback routes (1 address). '
        'When allocating VLSM subnets from a parent block such as <code>172.16.40.0/22</code> (1,024 addresses: <code>172.16.40.0</code>–<code>172.16.43.255</code>), always sort requirements from largest to smallest so every subnet aligns on an integral power-of-two boundary.</p>'
        + _tbl(
            ['CIDR Prefix', 'Dotted-Decimal Mask', 'Host Bits (h)', 'Block Size', 'Usable Hosts', 'Enterprise Architecture Role'],
            [
                ['/22', '255.255.252.0', '10 bits', '4 (3rd octet)', '1,022', 'Campus building supernet / wireless client pool'],
                ['/23', '255.255.254.0', '9 bits', '2 (3rd octet)', '510', 'Large floor user VLAN or voice segment'],
                ['/24', '255.255.255.0', '8 bits', '1 (3rd octet)', '254', 'Standard access VLAN (Data, Voice, IoT)'],
                ['/25', '255.255.255.128', '7 bits', '128 (4th octet)', '126', 'Medium branch office user segment'],
                ['/26', '255.255.255.192', '6 bits', '64 (4th octet)', '62', 'Small department or server cluster VLAN'],
                ['/27', '255.255.255.224', '5 bits', '32 (4th octet)', '30', 'Out-of-band management or printer VLAN'],
                ['/28', '255.255.255.240', '4 bits', '16 (4th octet)', '14', 'DMZ screened subnet or FHRP peering segment'],
                ['/29', '255.255.255.248', '3 bits', '8 (4th octet)', '6', 'Firewall HA cluster + dual ISP edge handoff'],
                ['/30', '255.255.255.252', '2 bits', '4 (4th octet)', '2', 'Traditional point-to-point WAN transit link'],
                ['/31', '255.255.255.254', '1 bit', '2 (4th octet)', '2 (RFC 3021)', 'Modern point-to-point router transit link'],
                ['/32', '255.255.255.255', '0 bits', '1 (4th octet)', '1 (Host route)', 'OSPF/BGP Loopback0 router ID &amp; VTEP source'],
            ]
        )
        + _cli(
            'Dual-Stack IPv6 SLAAC, EUI-64 vs Privacy Extensions &amp; ICMPv6 Neighbor Discovery (NDP)',
            '$ ip -6 addr show dev eth0\n'
            '2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 state UP qlen 1000\n'
            '    inet6 2001:db8:40:10:a8bb:ccff:fedd:ee11/64 scope global dynamic mngtmpaddr noprefixroute\n'
            '       valid_lft 86392sec preferred_lft 14392sec\n'
            '    inet6 fe80::a8bb:ccff:fedd:ee11/64 scope link\n'
            '$ ip -6 route show\n'
            '2001:db8:40:10::/64 dev eth0 proto kernel metric 256 expires 86392sec pref medium\n'
            'fe80::/64 dev eth0 proto kernel metric 256 pref medium\n'
            'default via fe80::21c:73ff:fe00:a01 dev eth0 proto ra metric 100 pref high\n'
            '$ ip -6 neigh show dev eth0\n'
            'fe80::21c:73ff:fe00:a01 lladdr 00:1c:73:00:0a:01 router REACHABLE',
            'IPv6 eliminates broadcast traffic entirely, replacing ARP with ICMPv6 Neighbor Discovery Protocol (NDP, RFC 4861) over multicast. '
            'When eth0 comes up, it forms its Link-Local address (<code>fe80::/10</code>) and sends an ICMPv6 Type 135 Neighbor Solicitation (NS) to the Solicited-Node multicast group <code>ff02::1:ffdd:ee11</code> for Duplicate Address Detection (DAD). '
            'Next, the host multicasts an ICMPv6 Type 133 Router Solicitation (RS) to <code>ff02::2</code> (All-Routers). '
            'The router replies from its link-local address <code>fe80::21c:73ff:fe00:a01</code> with an ICMPv6 Type 134 Router Advertisement (RA) to <code>ff02::1</code> (All-Nodes) carrying prefix <code>2001:db8:40:10::/64</code> and three control flags: '
            '<code>A=1</code> (Autonomous SLAAC enabled), <code>M=0, O=1</code> (Stateless DHCPv6—use SLAAC for the /64 address and query DHCPv6 on UDP 546/547 for DNS/NTP options), or <code>M=1</code> (Managed Stateful DHCPv6). '
            'Notice that in Modified EUI-64 addressing, the 48-bit MAC <code>aa:bb:cc:dd:ee:11</code> is split in half, <code>ff:fe</code> is inserted in the middle, and the 7th bit (Universal/Local bit) of the first byte is inverted (<code>0xaa</code> -> <code>0xa8</code>), producing <code>a8bb:ccff:fedd:ee11</code>.'
        )
    ),
    (1, 3): (
        '<h3>N10-009 Deep Dive: TCP State Machine, Flow Control, QUIC (HTTP/3) &amp; Enterprise Port Matrix</h3>'
        '<p>Transport-layer engineering balances delivery guarantees against latency and head-of-line blocking. '
        'TCP (RFC 9293) establishes full-duplex state via a 3-way handshake: (1) Client sends <code>SYN</code> with Initial Sequence Number <code>ISN=x</code>; (2) Server responds <code>SYN, ACK</code> with <code>SEQ=y, ACK=x+1</code>; (3) Client sends <code>ACK</code> with <code>SEQ=x+1, ACK=y+1</code>. '
        'During data transfer, TCP uses sliding receive windows (scaled up to 1 GiB via RFC 7323 window scale shift counts), Selective Acknowledgments (SACK, RFC 2018) to retransmit only missing segments rather than the entire window, and congestion control algorithms (CUBIC, BBR) to adapt to packet loss. '
        'By contrast, UDP (RFC 768) dispatches independent datagrams with zero handshake latency and no retransmission stalls—essential for real-time RTP voice/video (where a 200 ms retransmitted audio packet is worse than a concealed 20 ms drop), DNS queries (UDP 53), DHCP (UDP 67/68), NTP (UDP 123), SNMP (UDP 161/162), and QUIC / HTTP/3 (RFC 9000 / RFC 9114 over UDP 443, which integrates TLS 1.3 and independent multiplexed streams without TCP head-of-line blocking).</p>'
        + _tbl(
            ['Protocol / Service', 'Port &amp; Transport', 'Cleartext Legacy Counterpart', 'RFC / Security &amp; Operational Notes'],
            [
                ['SSH / SFTP / SCP', 'TCP 22', 'Telnet (TCP 23), FTP (TCP 20/21)', 'RFC 4251; use Ed25519/RSA keys and disable Telnet on all VTYs'],
                ['DNS (Queries / Zone Xfer)', 'UDP 53 / TCP 53', 'DoT (TCP 853), DoH (TCP 443)', 'UDP 53 for standard queries (EDNS0 up to 4096B); TCP 53 for AXFR/IXFR &amp; truncated TC=1 replies'],
                ['DHCPv4 / DHCPv6', 'UDP 67,68 / UDP 546,547', 'BootP (UDP 67/68)', 'Broadcast DORA in IPv4; multicast ff02::1:2 SARR in IPv6'],
                ['HTTP / HTTPS / HTTP/3', 'TCP 80 / TCP 443 / UDP 443', 'HTTP (TCP 80)', 'TLS 1.3 over TCP 443 or QUIC over UDP 443 (RFC 9114)'],
                ['Kerberos / LDAP / LDAPS', 'TCP/UDP 88, 389 / TCP 636', 'LDAP Cleartext (389)', 'Active Directory authentication (88) and directory queries (389 StartTLS / 636 LDAPS)'],
                ['NTP / SNMP / Syslog', 'UDP 123 / UDP 161,162 / UDP 514', 'Syslog over TLS (TCP 6514)', 'NTP stratum clock sync; SNMPv3 authPriv polling (161) &amp; traps (162); RFC 5424 Syslog'],
                ['SMTP Submission / IMAPS', 'TCP 587, 465 / TCP 993', 'SMTP (25), POP3 (110), IMAP (143)', 'RFC 8314: Client mail submission on TCP 587 (STARTTLS) or 465 (Implicit TLS); POP3S TCP 995'],
                ['SMB / RDP / SIP / RTP', 'TCP 445 / TCP+UDP 3389 / 5060,5061', 'NetBIOS 137–139, SIP 5060', 'SMB 3.1.1 encryption on TCP 445; SIP TLS signaling on 5061 with SRTP media on UDP 16384–32767'],
            ]
        )
        + _cli(
            'Diagnosing TCP Connection States (SYN_SENT vs CLOSE_WAIT) and Socket Listeners with ss -tulnp',
            '$ sudo ss -tulnp | egrep "Local|443|53|161"\n'
            'Netid State  Recv-Q Send-Q Local Address:Port  Peer Address:Port Process\n'
            'udp   UNCONN 0      0      10.20.30.10:53      0.0.0.0:*          users:(("named",pid=1142,fd=512))\n'
            'udp   UNCONN 0      0      10.20.30.10:161     0.0.0.0:*          users:(("snmpd",pid=988,fd=6))\n'
            'tcp   LISTEN 0      511    0.0.0.0:443         0.0.0.0:*          users:(("nginx",pid=1409,fd=8))\n'
            '$ ss -tan state syn-sent state close-wait\n'
            'State      Recv-Q Send-Q Local Address:Port   Peer Address:Port\n'
            'SYN-SENT   0      1      10.20.30.10:49218    10.40.50.25:636\n'
            'CLOSE-WAIT 38     0      10.20.30.10:443      10.20.30.112:54110',
            'Reading TCP socket states pinpoints whether a fault is network-side or application-side: '
            '<code>SYN-SENT</code> to <code>10.40.50.25:636</code> (LDAPS) proves the local host sent a TCP SYN that never received a SYN-ACK—indicating an intermediate firewall drop, routing black hole, or asymmetric return path. '
            'had the remote server been reachable with no daemon listening on TCP 636, it would have returned a TCP <code>RST, ACK</code> and closed immediately with "Connection refused". '
            'Conversely, a socket stuck in <code>CLOSE-WAIT</code> means the remote client already sent <code>FIN</code> and the local OS kernel acknowledged it, but the local server process (nginx PID 1409) has not yet closed its file descriptor.'
        )
    ),
    (1, 4): (
        '<h3>N10-009 Capstone Field Guide: Multi-Layer Packet Walk &amp; Fault Isolation Runbook</h3>'
        '<p>In production network operations, capstone layer mapping requires correlating user-facing symptoms with exact OSI/TCP-IP protocol headers before touching configuration. '
        'When a ticket states "Branch workstations can open internal web apps by IPv4 address <code>https://10.40.10.25:8443</code>, receive a TLS certificate hostname warning, and fail completely when browsing <code>https://erp.novak.internal:8443</code>," you can immediately exonerate Layers 1 through 4: physical optics/copper (L1), VLAN tagging and MAC switching (L2), IPv4 routing and inter-VLAN gateways (L3), and TCP port 8443 firewall rules (L4) are proven functional by the IP connection. '
        'The fault is strictly isolated to Layer 7 DNS name resolution (which in turn causes the Layer 6 TLS X.509 Subject Alternative Name mismatch when connecting via raw IP literal).</p>'
        + _cli(
            'End-to-End Divide-and-Conquer Triage Sequence (Linux / Windows PowerShell)',
            '$ ip -br link show eth0 && ip -br addr show eth0\n'
            'eth0             UP             00:50:56:9a:11:24 <BROADCAST,MULTICAST,UP,LOWER_UP>\n'
            'eth0             UP             10.20.30.45/24 fe80::250:56ff:fe9a:1124/64\n'
            '$ ping -c 2 -W 1 10.20.30.1 && ping -c 2 -W 1 10.40.10.25\n'
            '64 bytes from 10.20.30.1: icmp_seq=1 ttl=64 time=0.48 ms\n'
            '64 bytes from 10.40.10.25: icmp_seq=1 ttl=61 time=2.91 ms\n'
            '$ dig @10.20.30.10 erp.novak.internal +short\n'
            ';; connection timed out; no servers could be reached\n'
            '$ nc -zv -w 2 10.40.10.25 8443\n'
            'Connection to 10.40.10.25 8443 port [tcp/*] succeeded!',
            'Notice how four commands prove every layer in under 10 seconds: '
            '(1) <code>LOWER_UP</code> confirms Layer 1 carrier and Layer 2 interface state; '
            '(2) <code>ping 10.20.30.1</code> (TTL=64) confirms same-VLAN ARP and gateway reachability, while <code>ping 10.40.10.25</code> (TTL=61) proves Layer 3 routing across three router hops (64 - 61 = 3 hops); '
            '(3) <code>nc -zv 10.40.10.25 8443</code> proves Layer 4 TCP 3-way handshake completion; and '
            '(4) <code>dig @10.20.30.10</code> timing out isolates the outage to UDP/TCP 53 reachability or the `named` service on resolver 10.20.30.10.'
        )
    ),
}

NETOPS_DEPTH_HTML.update({
    (2, 1): (
        '<h3>N10-009 Deep Dive: CAM Table Learning, RSTP (802.1w) Convergence, BPDU Guard &amp; LACP (802.3ad)</h3>'
        '<p>Enterprise Layer-2 switches make wire-speed forwarding decisions in ASIC hardware by consulting the Content Addressable Memory (CAM) MAC address table. '
        'Every ingress frame triggers two independent operations: (1) <strong>Source MAC Learning</strong>—the switch records the frame\'s Source MAC, ingress port, and VLAN ID in the CAM table and resets its aging timer (default 300 seconds on Cisco IOS); '
        '(2) <strong>Destination MAC Lookup</strong>—if the Destination MAC is a known unicast entry in that VLAN, the frame is forwarded strictly out that single egress port (filtering); if the Destination MAC is unknown unicast, broadcast (<code>FF:FF:FF:FF:FF:FF</code>), or multicast (without IGMP snooping), the switch floods the frame out all ports in that VLAN except the ingress port. '
        'Because Ethernet frames have no Time-to-Live (TTL) field, a physical or logical Layer-2 loop causes flooded frames to circulate infinitely—creating a broadcast storm, constant MAC table thrashing (flapping between ports), and switch CPU exhaustion.</p>'
        + _tbl(
            ['Layer-2 Control Protocol', 'IEEE Standard', 'Port States / Modes', 'Timers &amp; Convergence', 'Production Hardening Best Practice'],
            [
                ['Classic STP', 'IEEE 802.1D', 'Disabled, Blocking, Listening, Learning, Forwarding', 'Hello 2s, Forward Delay 15sx2, MaxAge 20s (30–50s)', 'Legacy only; replace with Rapid PVST+ or MSTP (802.1s)'],
                ['Rapid STP (RSTP)', 'IEEE 802.1w', 'Discarding, Learning, Forwarding (Roles: Root, Designated, Alternate, Backup)', 'Proposal/Agreement handshake (<1–2s convergence)', 'Force root bridge via spanning-tree vlan X priority 4096'],
                ['PortFast + BPDU Guard', 'Cisco / 802.1w Edge', 'Edge port jumps immediately to Forwarding', '0s startup delay on end-host access ports', 'Enable spanning-tree bpduguard enable; err-disables if BPDU arrives'],
                ['Root Guard / Loop Guard', '802.1w Protection', 'Root-inconsistent / Loop-inconsistent state', 'Blocks superior BPDUs on downlinks / unidirectional fiber links', 'Apply Root Guard on distribution->access downlinks'],
                ['LACP EtherChannel', 'IEEE 802.3ad / 802.1AX', 'Active (initiates LACPDU) / Passive (responds)', 'Fast LACPDU 1s or Slow 30s; up to 8 active links', 'Use Active/Active or Active/Passive; never Passive/Passive'],
            ]
        )
        + _cli(
            'Inspecting RSTP Root Bridge Election, Err-Disabled BPDU Guard Events &amp; LACP EtherChannel',
            'SW-DIST-01# show spanning-tree vlan 10\n'
            'VLAN0010\n'
            '  Spanning tree enabled protocol rstp\n'
            '  Root ID    Priority    4106  (priority 4096 sys-id-ext 10)\n'
            '             Address     001c.7300.0a01\n'
            '             This bridge is the root\n'
            'Interface           Role Sts Cost      Prio.Nbr Type\n'
            '------------------- ---- --- --------- -------- --------------------------------\n'
            'Po1                 Desg FWD 3         128.65   P2p\n'
            'Gi0/12              Desg BKN*4         128.12   P2p Edge *BPDU_Inc\n'
            'SW-DIST-01# show etherchannel summary\n'
            'Group  Port-channel  Protocol    Ports\n'
            '------+-------------+-----------+-----------------------------------------------\n'
            '1      Po1(SU)         LACP      Gi0/1(P)   Gi0/2(P)',
            'In <code>show spanning-tree vlan 10</code>, the Bridge ID combines the 4-bit priority multiplier (4096), the 12-bit extended system ID (VLAN 10 = 4106), and the switch base MAC. '
            'Lowest Bridge ID wins Root Bridge election; never leave production core switches at default priority 32768 or an old closet switch with a lower MAC address will seize Root Bridge! '
            'In <code>show etherchannel summary</code>, flags <code>(SU)</code> verify a Layer-2 (<code>S</code>) Port-channel that is In-Use (<code>U</code>), and <code>(P)</code> confirms member links Gi0/1 and Gi0/2 are bundled in the LACP aggregation.'
        )
    ),
    (2, 2): (
        '<h3>N10-009 Deep Dive: IEEE 802.1Q Tagging, Native VLAN Security, Voice VLANs &amp; Inter-VLAN Routing</h3>'
        '<p>Virtual LANs (VLANs) partition a single physical switch fabric into isolated Layer-2 broadcast domains, where each VLAN maps 1-to-1 with a dedicated IPv4/IPv6 subnet. '
        'When a frame traverses an inter-switch trunk, IEEE 802.1Q inserts a 4-byte tag immediately after the 6-byte Source MAC address and before the 2-byte EtherType field: '
        'a 16-bit Tag Protocol Identifier (<code>TPID = 0x8100</code>), a 3-bit Priority Code Point (<code>PCP</code>, IEEE 802.1p Class of Service <code>0</code>–<code>7</code>, where VoIP RTP bearer traffic uses CoS <code>5</code> / DSCP <code>EF 46</code>), a 1-bit Drop Eligible Indicator (<code>DEI</code>), and a 12-bit VLAN Identifier (<code>VID</code> supporting values <code>1</code>–<code>4094</code>, with <code>0</code> and <code>4095</code> reserved). '
        'Because inserting those 4 bytes modifies the frame, the egress trunk switch recomputes the trailing 4-byte CRC-32 FCS, expanding maximum frame size from 1518 to 1522 bytes.</p>'
        + _cli(
            'Auditing 802.1Q Trunk Allowed/Active Lists, Voice VLANs &amp; SVI vs Router-on-a-Stick',
            'SW-ACC-02# show interfaces trunk\n'
            'Port        Mode             Encapsulation  Status        Native vlan\n'
            'Gi0/1       on               802.1q         trunking      99\n'
            'Port        Vlans allowed on trunk\n'
            'Gi0/1       10,20,30,99\n'
            'Port        Vlans allowed and active in management domain\n'
            'Gi0/1       10,20,99\n'
            'SW-ACC-02# show vlan brief | include 10|20|30\n'
            '10   CORP_DATA        active    Gi0/2, Gi0/3, Gi0/4\n'
            '20   VOICE_RTP        active    Gi0/2, Gi0/3, Gi0/4\n'
            '! Note: VLAN 30 is missing from local VLAN database!',
            'Look closely at the two tables in <code>show interfaces trunk</code>: VLAN 30 is listed under <em>Vlans allowed on trunk</em>, yet it is absent from <em>Vlans allowed and active in management domain</em>! '
            'That is a classic N10-009 troubleshooting trap: permitting a VLAN on a trunk (<code>switchport trunk allowed vlan add 30</code>) is necessary but not sufficient—if VLAN 30 does not exist in the local switch\'s VLAN database (or is in <code>shutdown</code> state), the switch cannot forward frames for VLAN 30. '
            'Notice also that ports Gi0/2–Gi0/4 appear in both VLAN 10 and VLAN 20 because an IP phone desk drop uses <code>switchport access vlan 10</code> (untagged PC data) plus <code>switchport voice vlan 20</code> (802.1Q-tagged VoIP frames advertised to the phone via CDP/LLDP-MED).'
        )
    ),
    (2, 3): (
        '<h3>N10-009 Deep Dive: TIA-568 Copper Categories, Single-Mode vs Multimode Fiber, Transceivers &amp; PoE Budgets</h3>'
        '<p>Physical layer engineering dictates maximum channel reach, EMI immunity, and inline power delivery. '
        'ANSI/TIA-568 specifies a 100-meter maximum horizontal copper channel: 90 meters of solid-core horizontal permanent link (terminated on 110 punchdown patch panels and keystone jacks using T568B pinouts) plus up to 10 meters of stranded patch cords. '
        'For inter-building or high-EMI environments, optical fiber eliminates electromagnetic interference and ground-potential differences entirely: Multimode Fiber (MMF, 50/125 µm laser-optimized OM3/OM4/OM5 with 850 nm VCSEL transceivers) serves short-reach data center interconnects, whereas Single-Mode Fiber (SMF, 9/125 µm OS1/OS2 with 1310 nm or 1550 nm DFB laser transceivers) spans kilometers across campus and metro links.</p>'
        + _tbl(
            ['Standard / Media', 'Core / Category', 'Wavelength / Pins', 'Max Distance', 'Data Rate &amp; Transceiver / Connector'],
            [
                ['1000BASE-T / 2.5G / 5GBASE-T', 'Cat5e / Cat6 UTP', '4 pairs (8P8C RJ-45)', '100 m (90m + 10m)', '1 Gbps (Cat5e/6); 2.5/5 Gbps (802.3bz)'],
                ['10GBASE-T (IEEE 802.3an)', 'Cat6 vs Cat6A (500 MHz)', '4 pairs (8P8C RJ-45)', '55 m (Cat6) / 100 m (Cat6A)', '10 Gbps copper; high transceiver power'],
                ['10GBASE-SR / 25GBASE-SR', 'OM3 / OM4 MMF (50/125 µm)', '850 nm VCSEL laser', '300 m (OM3) / 400 m (OM4)', '10G SFP+ / 25G SFP28 duplex LC'],
                ['10GBASE-LR / 100GBASE-LR4', 'OS2 SMF (9/125 µm)', '1310 nm DFB laser', '10 km', '10G SFP+ / 100G QSFP28 duplex LC (UPC/APC)'],
                ['10GBASE-ER / ZR', 'OS2 SMF (9/125 µm)', '1550 nm laser', '40 km (ER) / 80 km (ZR)', 'Long-haul metro dark fiber; requires attenuator on short bench runs'],
                ['40GBASE-SR4 / 100GBASE-SR4', 'OM4 MMF Parallel Ribbon', '850 nm (4x10G / 4x25G)', '100–150 m', 'QSFP+ / QSFP28 with 12-fiber MPO/MTP connector'],
            ]
        )
        + _cli(
            'Diagnosing Optical dBm Loss Budgets (DOM) &amp; IEEE 802.3af/at/bt PoE Power Exhaustion',
            'SW-ACC-03# show interfaces Gi0/24 transceiver detail\n'
            'ITU Channel not available (Wavelength 850 nm),\n'
            'Transceiver is internally calibrated.\n'
            'mA: milliamperes, dBm: decibels (milliwatts), NA or N/A: not applicable.\n'
            '                  Optical   Optical\n'
            '           Temp  Voltage  Tx Power  Rx Power\n'
            'Port       (Celsius) (Volts)  (dBm)     (dBm)\n'
            '---------  --------- -------  --------  --------\n'
            'Gi0/24       38.4     3.29      -2.1     -18.9   (Low Rx Alarm threshold: -14.0 dBm)\n'
            'SW-ACC-03# show power inline\n'
            'Module   Available     Used     Remaining\n'
            '          (Watts)     (Watts)    (Watts)\n'
            '------   ---------   --------   ---------\n'
            '1           370.0      358.4       11.6\n'
            'Interface Admin  Oper       Power   Device              Class Max\n'
            '                            (Watts)                            \n'
            '--------- ------ ---------- ------- ------------------- ----- ---\n'
            'Gi0/1     auto   on         28.4    AIR-AP3802I         4     30.0\n'
            'Gi0/2     auto   fault      0.0     n/a                 n/a   30.0',
            'Digital Optical Monitoring (DOM) on Gi0/24 shows normal Tx power (<code>-2.1 dBm</code>) but severely attenuated Rx power (<code>-18.9 dBm</code>, below the <code>-14.0 dBm</code> receiver sensitivity floor), causing FCS/CRC errors from a contaminated LC ferrule, tight macro-bend, or mismatched 50 µm/62.5 µm patch cord. '
            'Meanwhile, <code>show power inline</code> reveals why the new Wi-Fi 6E access point on Gi0/2 failed to boot (<code>Oper: fault</code>): only <code>11.6 W</code> remains in the switch\'s 370 W PoE budget, whereas an IEEE 802.3at (PoE+ Type 2 Class 4) AP requires up to 30 W at the PSE port (25.5 W at the PD), and IEEE 802.3bt (PoE++ Type 3/4) requires 60 W / 90 W.'
        )
    ),
    (2, 4): (
        '<h3>N10-009 Capstone Field Guide: Layer-1/Layer-2 Closet Isolation &amp; Port-Security Remediation</h3>'
        '<p>When a single workstation in a wiring closet is isolated while neighboring desks operate normally, follow a strict Layer-1-to-Layer-2 checklist before touching IP settings: '
        '(1) Check physical link status and err-disable reason (<code>show interfaces status err-disabled</code>); '
        '(2) Check IEEE 802.3af/at/bt PoE allocation if powering a VoIP phone, camera, or AP; '
        '(3) Verify speed/duplex negotiation (never pair hardcoded <code>speed 100 / duplex full</code> on one side with <code>auto</code> on the other, which forces the auto side to fall back to 100/Half and triggers late collisions and runts on the half-duplex end and FCS/CRC errors on the full-duplex end); '
        '(4) Verify access VLAN membership (<code>show vlan brief</code>) and MAC table learning (<code>show mac address-table interface Gi0/X</code>).</p>'
        + _cli(
            'Resolving a Port-Security Err-Disabled Violation &amp; Duplex Mismatch in One Sequence',
            'SW-ACC-01# show interfaces status err-disabled\n'
            'Port      Name               Status       Reason               Err-disabled Vlans\n'
            'Gi0/8     FINANCE_DESK_08    err-disabled psecure-violation\n'
            'SW-ACC-01# show port-security interface Gi0/8\n'
            'Port Security              : Enabled\n'
            'Port Status                : Secure-shutdown\n'
            'Violation Mode             : Shutdown\n'
            'Maximum MAC Addresses      : 1\n'
            'Sticky MAC Addresses       : 1\n'
            'Last Source Address:Vlan   : 0050.569a.8841:10\n'
            'Security Violation Count   : 1\n'
            'SW-ACC-01# configure terminal\n'
            'SW-ACC-01(config)# interface Gi0/8\n'
            'SW-ACC-01(config-if)# no switchport port-security mac-address sticky 0050.569a.0012\n'
            'SW-ACC-01(config-if)# shutdown\n'
            'SW-ACC-01(config-if)# no shutdown',
            'Port security offers three violation modes: <strong>Protect</strong> (silently drops frames from unauthorized MACs with no syslog/SNMP trap), <strong>Restrict</strong> (drops frames, increments the violation counter, and sends a syslog/SNMP trap while keeping the port up), and <strong>Shutdown</strong> (default; places the port in <code>err-disabled</code> state immediately). '
            'When a legitimate PC or USB-C dock is replaced on a sticky-MAC port, you must clear the old sticky MAC entry and bounce the interface with <code>shutdown</code> followed by <code>no shutdown</code>.'
        )
    ),
})

NETOPS_DEPTH_HTML.update({
    (3, 1): (
        '<h3>N10-009 Deep Dive: Longest-Prefix Match, Administrative Distance, OSPF Adjacencies &amp; FHRP High Availability</h3>'
        '<p>Every IP router separates its <strong>Routing Information Base (RIB)</strong>—where candidate routes from connected interfaces, static configuration, OSPF, EIGRP, and BGP compete—from its hardware-accelerated <strong>Forwarding Information Base (FIB / CEF table)</strong> used to forward packets at line rate. '
        'Two ironclad rules govern route installation versus packet forwarding: '
        '(1) <strong>Packet forwarding ALWAYS chooses Longest-Prefix Match (LPM)</strong> across installed FIB routes regardless of protocol or Administrative Distance (a <code>/27</code> OSPF route with AD 110 always beats a <code>/24</code> static route with AD 1 for a destination matching both); '
        '(2) <strong>Route installation into the RIB compares Administrative Distance (AD) ONLY when two protocols advertise the exact same prefix and mask</strong> (e.g., <code>10.20.30.0/24</code> via Static AD 1 vs OSPF AD 110), and compares protocol metric (OSPF cumulative cost, EIGRP composite metric, RIP hop count) only within the same routing protocol.</p>'
        + _tbl(
            ['Route Source / Protocol', 'Default AD (Cisco)', 'Metric / Algorithm', 'Transport &amp; Multicast / Port', 'Key Operational &amp; Failure Behavior'],
            [
                ['Connected Interface', '0', 'N/A (Direct L2)', 'Local interface UP/UP', 'Removed immediately when physical/line protocol goes down'],
                ['Static Route / Floating Static', '1 (or 1–254 custom)', '0 (Configured)', 'Manual next-hop or exit intf', 'Floating static sets AD > dynamic protocol (e.g., AD 200 backup to OSPF 110)'],
                ['eBGP (External BGP)', '20', 'Path Vector (AS_PATH, LOCAL_PREF, MED)', 'TCP Port 179 unicast', 'Inter-AS WAN/Internet peering; loop prevention via AS_PATH inspection'],
                ['EIGRP (Internal / External)', '90 / 170', 'DUAL Composite (BW + Delay)', 'IP Proto 88, Multicast 224.0.0.10', 'Maintains Successor &amp; Feasible Successor for sub-second failover'],
                ['OSPFv2 / OSPFv3', '110', 'Dijkstra SPF Cost = RefBW / BW', 'IP Proto 89, 224.0.0.5/.6 (ff02::5/6)', 'Requires matching Hello/Dead, Area ID, Subnet Mask, Stub flag, and MTU'],
                ['IS-IS / RIPv2 / iBGP', '115 / 120 / 200', 'Link-state / Hop count (max 15) / AS', 'L2 CLNS / UDP 520 / TCP 179', 'RIP metric 16 = unreachable; iBGP requires full mesh or route reflectors'],
            ]
        )
        + _cli(
            'Troubleshooting OSPF Stuck in EXSTART/INIT and Verifying HSRP / VRRP First-Hop Redundancy',
            'RTR-CORE-01# show ip ospf neighbor\n'
            'Neighbor ID     Pri   State           Dead Time   Address         Interface\n'
            '10.255.255.2      1   FULL/DR         00:00:36    10.10.12.2      GigabitEthernet0/0\n'
            '10.255.255.3      0   EXSTART/ -      00:00:33    10.10.13.2      GigabitEthernet0/1\n'
            'RTR-CORE-01# show standby brief\n'
            '                     P indicates configured to preempt.\n'
            '                     |\n'
            'Interface   Grp  Pri P State   Active          Standby         Virtual IP\n'
            'Gi0/0.10    10   110 P Active  local           10.10.10.3      10.10.10.1',
            'When <code>show ip ospf neighbor</code> shows a peer stuck in <code>EXSTART</code> or <code>EXCHANGE</code>, the Database Description (DBD) packets are failing due to an <strong>IP MTU mismatch</strong> between the two interfaces (e.g., 1500 bytes on RTR-CORE-01 vs 9000 bytes or 1400 bytes on 10.255.255.3). '
            'If a peer never appears at all or stays in <code>INIT</code>, check for mismatched Hello/Dead timers (default 10s/40s on broadcast/point-to-point), mismatched Area IDs, mismatched subnet masks, or a unidirectional ACL blocking IP protocol 89 / multicast <code>224.0.0.5</code>. '
            'In <code>show standby brief</code>, HSRP (or standard RFC 5798 VRRP on IP protocol 112) shares Virtual IP <code>10.10.10.1</code> and Virtual MAC <code>0000.0c07.ac0a</code> (HSRP v1 group 10) or <code>0000.5e00.010a</code> (VRRP v2/v3 group 10) so end hosts keep working seamlessly if a distribution router fails.'
        )
    ),
    (3, 2): (
        '<h3>N10-009 Deep Dive: WAN Handoffs, Demarc/NIU/Smartjack Isolation, MPLS, SD-WAN &amp; IPsec/GRE Tunnels</h3>'
        '<p>At the enterprise WAN edge, clear physical and operational boundaries separate customer responsibility from carrier responsibility. '
        'The <strong>Demarcation Point (Demarc)</strong>—housed in the building Minimum Point of Entry (MPOE) or Main Distribution Frame (MDF)—marks where the service provider\'s <strong>Local Loop</strong> terminates on a Network Interface Unit (NIU), Optical Network Terminal (ONT), or Smartjack, and hands off to the customer\'s Inside Wiring and <strong>Customer Premises Equipment (CPE)</strong> router or firewall. '
        'When a WAN circuit goes down, testing with a hardware or carrier-activated loopback at the Smartjack/NIU immediately isolates whether the fault lies on the carrier local loop/Central Office side or inside the customer CPE/patch cabling.</p>'
        + _tbl(
            ['WAN / Tunnel Technology', 'Layer / Encapsulation', 'Encryption &amp; Routing Support', 'Typical MTU / Overhead', 'Operational &amp; SLA Trade-offs'],
            [
                ['Metro Ethernet (E-Line / E-LAN)', 'IEEE 802.3 / 802.1ad Q-in-Q', 'None native (add MACsec 802.1AE or IPsec)', '1500–9100B per SLA', 'Low latency fiber handoff; single-provider footprint'],
                ['MPLS Layer-3 VPN', 'Shim Label (L2.5, 32-bit)', 'Private routing via MP-BGP VRFs; not encrypted', '1500B payload (provider MPLS MTU >=1508B)', 'Guaranteed QoS classes (EF/AF); expensive per-Mbps'],
                ['IPsec Site-to-Site VPN', 'IKEv2 (UDP 500/4500) + ESP (IP 50)', 'AES-256-GCM + SHA-256/384 + DH Group 19/20', '1400–1438B (52–76B overhead)', 'Encrypts unicast traffic over public broadband/DIA'],
                ['GRE over IPsec (mGRE / DMVPN)', 'GRE (IP 47, 24B) inside ESP (IP 50)', 'Carries multicast (OSPF/EIGRP) + AES-GCM', '1400B MTU / 1360B TCP MSS', 'Enables dynamic routing protocols across encrypted WANs'],
                ['SD-WAN Fabric', 'IPsec/BFD overlays over MPLS+DIA+5G', 'Zero-touch PKI + application-aware SLA steering', '1400–1420B auto-clamped', 'Sub-second path failover based on loss, latency, and MOS jitter'],
            ]
        )
        + _cli(
            'Verifying IKEv2 / IPsec Security Associations &amp; BFD Path SLA Telemetry on a Branch Edge',
            'BR-WAN-01# show crypto ikev2 sa\n'
            ' IPv4 Crypto IKEv2  SA\n'
            'Tunnel-id Local                 Remote                fvrf/ivrf            Status\n'
            '1         203.0.113.10/4500     198.51.100.1/4500     none/none            READY\n'
            '      Encr: AES-GCM, keysize: 256, PRF: SHA384, Hash: None, DH Grp:20, Auth sign: ECDSA\n'
            'BR-WAN-01# show crypto ipsec sa | include interface|pkts|esp\n'
            'interface: Tunnel10\n'
            '    #pkts encaps: 184920, #pkts encrypt: 184920, #pkts digest: 184920\n'
            '    #pkts decaps: 192411, #pkts decrypt: 192411, #pkts verify: 192411\n'
            '     inbound esp sas: spi: 0x9A412C0E(2587962382) transform: esp-256-gcm',
            'In <code>show crypto ikev2 sa</code>, status <code>READY</code> on UDP port <code>4500</code> indicates NAT-Traversal (NAT-T, RFC 3948) was automatically negotiated because one of the peers sits behind a NAT device (encapsulating ESP packets inside UDP 4500 so PAT routers can translate ports). '
            'In <code>show crypto ipsec sa</code>, both <code>#pkts encrypt</code> and <code>#pkts decrypt</code> are incrementing symmetrically. '
            'If <code>#pkts encrypt</code> climbs while <code>#pkts decrypt</code> remains <code>0</code>, the outbound tunnel traffic is leaving your CPE, but return ESP (IP protocol 50) or UDP 4500 packets are being blocked by the remote firewall or dropped by an asymmetrical ISP route.'
        )
    ),
    (3, 3): (
        '<h3>N10-009 Deep Dive: IEEE 802.11ax/be (Wi-Fi 6/6E/7), RF dBm/SNR Math, DFS &amp; WPA3-Enterprise</h3>'
        '<p>Enterprise wireless LAN (WLAN) architecture combines RF spectrum engineering with centralized controller orchestration (CAPWAP over UDP 5246 control and UDP 5247 data tunnels) and IEEE 802.1X identity security. '
        'In 2.4 GHz (2400–2483.5 MHz), each 20 MHz channel overlaps neighboring channels separated by 5 MHz; only Channels <strong>1, 6, and 11</strong> are non-overlapping in North America. '
        'Assigning an AP to Channel 3 or Channel 8 creates destructive <strong>Adjacent-Channel Interference (ACI)</strong> that bypasses normal 802.11 CSMA/CA Clear Channel Assessment and causes severe CRC corruptions. '
        'In 5 GHz (UNII-1, UNII-2/2e DFS, UNII-3) and 6 GHz (Wi-Fi 6E / Wi-Fi 7 IEEE 802.11be with 1,200 MHz of clean spectrum), non-overlapping 20 MHz channels can be bonded into 40 MHz, 80 MHz, 160 MHz, or 320 MHz channels, and OFDMA Resource Units (RUs) plus MU-MIMO schedule simultaneous multi-client transmissions.</p>'
        + _cli(
            'Calculating RF Link Budgets, SNR &amp; Debugging 802.1X / RADIUS Roaming on a Wireless Controller',
            'WLC-CORE-01# show ap auto-rf 802.11a AP-FL3-EAST\n'
            'Channel Assignment            : Channel 52 (5260 MHz, 40 MHz width, UNII-2 DFS)\n'
            'Last Radar Detected           : 10:41:12 UTC — Channel switched 52 -> 149 (30-min Non-Occupancy)\n'
            'Transmit Power                : 14 dBm (25 mW)\n'
            'Noise Floor                   : -94 dBm\n'
            'WLC-CORE-01# show client detail 6c:40:08:9a:22:10\n'
            'Client MAC Address            : 6c:40:08:9a:22:10\n'
            'RSSI / SNR                    : -62 dBm / 32 dB (Voice-grade target: RSSI >= -67 dBm, SNR >= 25 dB)\n'
            '802.11 Security Policy        : WPA3-Enterprise (802.1X SHA-256, PMF 802.11w Required)\n'
            'EAP Type / RADIUS VLAN        : EAP-TLS / VLAN 20 (Tunnel-Private-Group-Id = 20)',
            'Remember the logarithmic decibel rules for N10-009: <code>SNR (dB) = Signal (dBm) - Noise Floor (dBm)</code>, so <code>-62 dBm - (-94 dBm) = +32 dB SNR</code>. '
            'Every <code>+3 dB</code> doubles linear power (<code>14 dBm = 25 mW</code>; <code>17 dBm = 50 mW</code>; <code>20 dBm = 100 mW</code>), and every <code>+10 dB</code> multiplies power by 10. '
            'Notice that Channel 52 lies in the UNII-2 Dynamic Frequency Selection (DFS) band: when the AP detected weather/aviation radar at 10:41:12 UTC, regulatory rules forced it to vacate Channel 52 within 10 seconds and observe a 30-minute non-occupancy period on Channel 149.'
        )
    ),
    (3, 4): (
        '<h3>N10-009 Capstone Field Guide: High-Density Wireless Capacity &amp; Site Survey Remediation</h3>'
        '<p>When an auditorium or open-plan floor experiences Wi-Fi drops despite "full signal bars," the failure is almost never low transmit power—it is <strong>Co-Channel Interference (CCI)</strong>, excessive channel width, or asymmetric client transmit power. '
        'Cranking AP radios to maximum 2.4 GHz power (20–23 dBm) while mobile phones can only transmit back at 12–15 dBm creates a one-way "hidden node / loud speaker" problem where clients hear a distant AP they cannot talk back to, and neighboring APs on the same channel contend for airtime.</p>'
        + _cli(
            'High-Density WLAN Remediation Plan Verified via Ekahau / Controller Airtime Telemetry',
            'WLC-CORE-01# show ap wlan 802.11b summary\n'
            'WLAN 10 (CORP-ENTERPRISE): 2.4 GHz Radio Disabled (5 GHz / 6 GHz Band-Steered Only)\n'
            'WLC-CORE-01# show rf-profile summary "HIGH-DENSITY-AUDITORIUM"\n'
            '5 GHz Channel Width           : 20 MHz (Maximizes 24 independent channels; avoids 80 MHz CCI)\n'
            '5 GHz Tx Power Range          : Min 8 dBm / Max 14 dBm (Micro-cell footprint)\n'
            'Minimum Mandatory Data Rate   : 24 Mbps (1, 2, 5.5, 6, 9, 11, 12 Mbps disabled)\n'
            'Fast BSS Transition (802.11r) : Enabled (Over-the-DS FT with 802.11k &amp; 802.11v)',
            'Notice the four high-density engineering adjustments: (1) Reduce 5 GHz channel width from 80 MHz to 20 MHz so every AP in the room operates on a distinct frequency without CCI; '
            '(2) Lower AP transmit power to 8–14 dBm and disable low legacy data rates (1–12 Mbps) so management beacons consume <2% airtime and sticky clients roam cleanly at -67 dBm; '
            '(3) Enable 802.11r/k/v so WPA3-Enterprise clients roam in <15 ms without repeating a full EAP-TLS handshake.'
        )
    ),
    (4, 1): (
        '<h3>N10-009 Deep Dive: DHCPv4 DORA, Relay Agents (Option 82), DHCP Snooping &amp; IPv6 SLAAC/DHCPv6</h3>'
        '<p>Dynamic Host Configuration Protocol (DHCPv4, RFC 2131) operates over UDP port 68 (client) and UDP port 67 (server). '
        'Because a booting host lacks an IPv4 address, it transmits <strong>DHCPDISCOVER</strong> from <code>0.0.0.0:68</code> to limited broadcast <code>255.255.255.255:67</code> (Layer-2 destination <code>FF:FF:FF:FF:FF:FF</code>). '
        'Routers never forward Layer-3 limited broadcasts (<code>255.255.255.255</code>) across subnets. '
        'Therefore, when the enterprise DHCP server resides in a central data center VLAN, every remote VLAN router interface or Layer-3 switch SVI must be configured with a <strong>DHCP Relay Agent</strong> (<code>ip helper-address &lt;dhcp-server-ip&gt;</code>), which intercepts the broadcast on UDP 67, populates the <code>giaddr</code> (Gateway IP Address) field with the SVI\'s own IP address (so the DHCP server knows which scope to allocate from), and unicasts the packet to the DHCP server.</p>'
        + _tbl(
            ['DHCPv4 Option / Timer', 'Code / Value', 'Protocol Function &amp; Enterprise Troubleshooting Impact'],
            [
                ['Subnet Mask / Router', 'Option 1 / Option 3', 'Delivers prefix mask and default gateway IP; missing Option 3 isolates client to local VLAN'],
                ['DNS Servers / Domain Name', 'Option 6 / Option 15', 'Delivers recursive resolver IPs and search suffix (e.g., novak.internal)'],
                ['NTP Servers / Lease Time', 'Option 42 / Option 51', 'Clock sync for Kerberos/TLS; T1 renewal at 50% lease (unicast), T2 rebind at 87.5% (broadcast)'],
                ['TFTP / PXE Boot Server &amp; File', 'Option 66 / Option 67', 'Delivers VoIP phone configuration server or PXE network boot image path'],
                ['Relay Agent Information', 'Option 82 (RFC 3046)', 'Inserted by switch/relay (Circuit ID + Remote ID); untrusted downstream switch drops if unconfigured'],
                ['Captive Portal / WLC IP', 'Option 114 / Option 43', 'RFC 8910 captive portal URI; Option 43 gives lightweight APs the WLC management IP list'],
            ]
        )
        + _cli(
            'Verifying IP Helper Relay, DHCP Snooping Binding Database &amp; Untrusted Port Drops',
            'SW-CORE-01# show running-config interface Vlan30\n'
            'interface Vlan30\n'
            ' description ENGINEERING_WORKSTATIONS\n'
            ' ip address 10.30.0.1 255.255.254.0\n'
            ' ip helper-address 10.100.10.20\n'
            'SW-ACC-01# show ip dhcp snooping\n'
            'Switch DHCP snooping is enabled\n'
            'DHCP snooping is configured on following VLANs: 10,20,30\n'
            'Insertion of option 82 is enabled\n'
            'Interface                  Trusted    Allow option    Rate limit (pps)\n'
            '-----------------------    -------    ------------    ----------------\n'
            'GigabitEthernet0/1         yes        yes             unlimited\n'
            'GigabitEthernet0/5         no         no              15\n'
            'SW-ACC-01# show ip dhcp snooping binding\n'
            'MacAddress          IpAddress        Lease(sec)  Type           VLAN  Interface\n'
            '------------------  ---------------  ----------  -------------  ----  --------------------\n'
            '00:50:56:9A:11:24   10.30.0.45       86120       dhcp-snooping  30    GigabitEthernet0/5',
            '<strong>DHCP Snooping</strong> prevents rogue DHCP servers from handing out malicious default gateways or DNS servers (DHCP MitM): '
            'all client access ports (e.g., Gi0/5) are <strong>Untrusted</strong> and drop any ingress server messages (<code>DHCPOFFER</code>, <code>DHCPACK</code>, <code>DHCPNAK</code>), while only uplinks toward the legitimate DHCP server or relay (Gi0/1) are marked <code>ip dhcp snooping trust</code>. '
            'The switch also records every valid lease in the DHCP Snooping Binding Database (`MAC + IP + VLAN + Port`), which directly feeds <strong>Dynamic ARP Inspection (DAI)</strong> and <strong>IP Source Guard (IPSG)</strong> to block ARP poisoning and IP spoofing.'
        )
    ),
})

NETOPS_DEPTH_HTML.update({
    (4, 2): (
        '<h3>N10-009 Deep Dive: Recursive vs Iterative DNS Resolution, DNSSEC (RFC 4034), Split-Horizon &amp; DoH/DoT</h3>'
        '<p>Domain Name System (DNS, RFC 1035) translates human-readable Fully Qualified Domain Names (FQDNs) into IP addresses and service records. '
        'A stub resolver on a workstation sends a <strong>recursive query</strong> (`RD=1` Recursion Desired flag) to its configured enterprise DNS resolver (`10.100.10.53`). '
        'If the answer is not in cache, the recursive resolver performs <strong>iterative queries</strong> down the DNS hierarchy: querying a Root Server (`.`) to obtain the Top-Level Domain (`.com` or `.org`) NS/glue records, querying the TLD server to obtain the authoritative name servers for `novak.example`, and finally querying the authoritative server (`AA=1` Authoritative Answer flag) for the requested resource record. '
        'With <strong>Split-Horizon (Split-Brain) DNS</strong>, internal corporate resolvers answer internal queries (e.g., `erp.novak.example -> 10.40.10.25`) from a private zone while external public resolvers return only public-facing DMZ records (`203.0.113.25`).</p>'
        + _tbl(
            ['DNS Record Type', 'RFC Standard', 'Data Format &amp; Purpose', 'Operational &amp; Security Verification'],
            [
                ['A / AAAA', 'RFC 1035 / 3596', 'Maps hostname to 32-bit IPv4 (A) or 128-bit IPv6 (AAAA)', 'Verify forward resolution and TTL before IP migrations'],
                ['CNAME', 'RFC 1035', 'Canonical Name alias pointing one FQDN to another FQDN', 'Cannot coexist with SOA/NS/MX at the zone apex (@)'],
                ['MX', 'RFC 1035', 'Mail Exchanger priority (lower integer = higher preference) + FQDN', 'Must point to an A/AAAA host record, never to a CNAME'],
                ['PTR', 'RFC 1035', 'Reverse DNS in in-addr.arpa (IPv4) or ip6.arpa (IPv6)', 'Required for enterprise SMTP anti-spam &amp; troubleshooting'],
                ['SRV', 'RFC 2782', '_service._proto.name TTL IN SRV Priority Weight Port Target', 'Locates Active Directory LDAP/Kerberos (_ldap._tcp.dc._msdcs) &amp; SIP'],
                ['TXT (SPF/DKIM/DMARC)', 'RFC 7208 / 6376 / 7489', 'v=spf1, DKIM public key, and _dmarc policy (p=quarantine/reject)', 'Prevents domain email spoofing and phishing'],
                ['DNSKEY / DS / RRSIG', 'RFC 4034 (DNSSEC)', 'Public zone key, parent Delegation Signer hash, cryptographic signature', 'Authenticates DNS origin &amp; integrity; AD=1 Authenticated Data flag'],
            ]
        )
        + _cli(
            'Tracing Iterative Resolution &amp; DNSSEC RRSIG Validation with dig +trace and +dnssec',
            '$ dig @10.100.10.53 portal.novak.internal A +dnssec +multiline\n'
            ';; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 48219\n'
            ';; flags: qr rd ra ad; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1\n'
            ';; ANSWER SECTION:\n'
            'portal.novak.internal.  300 IN A 10.40.10.25\n'
            'portal.novak.internal.  300 IN RRSIG A 13 3 300 (\n'
            '                            20261125000000 20261025000000 41892 novak.internal.\n'
            '                            k9xP2mQ8vL1nR4tY7wZ0aB3cD6eF9gH2jK5lM8nP1qR4== )\n'
            '$ dig @10.100.10.53 _ldap._tcp.dc._msdcs.novak.internal SRV +short\n'
            '0 100 389 dc01.novak.internal.\n'
            '0 100 389 dc02.novak.internal.',
            'Distinguish DNS response codes (`RCODE`) immediately during triage: '
            '<code>NOERROR</code> means the query succeeded (even if `ANSWER: 0` when the name exists for another record type); '
            '<code>NXDOMAIN</code> is an authoritative guarantee that the domain name does not exist in the zone; '
            '<code>SERVFAIL</code> means the recursive resolver could not reach the authoritative servers or **DNSSEC cryptographic signature (`RRSIG` / `DS`) validation failed**; and '
            '<code>REFUSED</code> means the DNS server policy blocks recursion or zone transfers from your source IP.'
        )
    ),
    (4, 3): (
        '<h3>N10-009 Deep Dive: SNAT, DNAT, PAT (NAT Overload), Screened-Subnet DMZ &amp; Stateful Firewall ACLs</h3>'
        '<p>Network Address Translation (RFC 2663 / RFC 3022) and stateful inspection firewalls govern perimeter and internal zone transitions. '
        '<strong>Static NAT (1-to-1)</strong> maps one inside local RFC 1918 address to a dedicated inside global public IPv4 address. '
        '<strong>Dynamic PAT (Port Address Translation / NAT Overload)</strong> maps thousands of inside local hosts (`10.0.0.0/8`) onto a single public IPv4 address (`203.0.113.5`) by tracking each session via a unique 5-tuple (`Protocol, Inside IP:Port, Translated IP:Port, Outside IP:Port`) in the router\'s translation table. '
        'When an external client initiates an HTTPS request to a public service hosted in a **Screened Subnet (DMZ)**, **Destination NAT (DNAT / Port Forwarding)** rewrites the destination from `203.0.113.5:443` to the DMZ reverse proxy `172.16.10.5:443`, while stateful firewall policies strictly block any direct inbound connections from the untrusted Internet or DMZ into the internal corporate database VLAN.</p>'
        + _cli(
            'Inspecting Active PAT Translations &amp; Top-Down Extended ACL Hit Counters',
            'RTR-EDGE-01# show ip nat translations\n'
            'Pro Inside global         Inside local          Outside local         Outside global\n'
            'tcp 203.0.113.5:49210     10.20.30.45:49210     198.51.100.20:443     198.51.100.20:443\n'
            'tcp 203.0.113.5:443       172.16.10.5:443       192.0.2.88:55124      192.0.2.88:55124\n'
            'RTR-EDGE-01# show ip access-lists WAN_INBOUND\n'
            'Extended IP access list WAN_INBOUND\n'
            '    10 permit tcp any host 172.16.10.5 eq 443 (14820 matches)\n'
            '    20 deny ip 10.0.0.0 0.255.255.255 any log (42 matches)\n'
            '    30 deny ip 172.16.0.0 0.15.255.255 any log\n'
            '    40 deny ip 192.168.0.0 0.0.255.255 any log\n'
            '    50 deny ip any any log (914 matches)',
            'Notice three critical engineering details in `show ip access-lists WAN_INBOUND`: '
            '(1) Extended ACLs use **wildcard masks** (`0` = must match bit, `1` = ignore bit), so `0.15.255.255` matches the entire 12-bit RFC 1918 block `172.16.0.0/12` (`172.16.0.0`–`172.31.255.255`); '
            '(2) Sequence 20–40 implement **anti-spoofing (bogon/RFC 2827 ingress filtering)** at the WAN perimeter so external attackers cannot spoof internal RFC 1918 source addresses; and '
            '(3) ACLs evaluate top-down on a **first-match-wins** basis and end with an invisible **implicit `deny ip any any`** (which sequence 50 makes explicit with `log` so dropped packets generate syslog events).'
        )
    ),
    (4, 4): (
        '<h3>N10-009 Capstone Field Guide: "The Internet Is Down" — Separating DHCP, DNS, NAT &amp; Route Failures</h3>'
        '<p>When users report "The Internet is down," the ticket rarely means the ISP fiber was severed. '
        'A systematic 60-second isolation sequence separates the four classic culprits: '
        '(1) **DHCP exhaustion or missing relay** (`169.254.x.x` APIPA address -> Layer-2 VLAN or `ip helper-address` fault); '
        '(2) **Default gateway / FHRP failure** (valid IP lease, cannot ping default gateway -> SVI shutdown, wrong subnet mask, or HSRP/VRRP split-brain); '
        '(3) **NAT overload / WAN edge route failure** (can ping internal core `10.100.10.1`, cannot ping external IP `1.1.1.1` -> missing `0.0.0.0/0` default route, BGP peer down, or missing VLAN subnet in the NAT overload ACL); '
        '(4) **DNS resolution failure** (can ping `1.1.1.1` and `8.8.8.8`, cannot resolve `www.iana.org` -> UDP/TCP 53 blocked or recursive resolver down).</p>'
        + _cli(
            'Pinpointing a Missing Subnet in the Edge Router PAT ACL After Adding VLAN 40',
            'RTR-EDGE-01# show ip interface brief | include Gi0/0|Gi0/1\n'
            'GigabitEthernet0/0     10.255.0.1      YES NVRAM  up                    up\n'
            'GigabitEthernet0/1     203.0.113.5     YES NVRAM  up                    up\n'
            'RTR-EDGE-01# show running-config | include ip nat|access-list 10\n'
            'ip nat inside source list 10 interface GigabitEthernet0/1 overload\n'
            'access-list 10 permit 10.10.0.0 0.0.255.255\n'
            'access-list 10 permit 10.20.0.0 0.0.255.255\n'
            'access-list 10 permit 10.30.0.0 0.0.255.255\n'
            '! Fix: permit new VLAN 40 subnet (10.40.0.0/16) in NAT ACL 10:\n'
            'RTR-EDGE-01(config)# access-list 10 permit 10.40.0.0 0.0.255.255',
            'When a newly provisioned VLAN (`10.40.0.0/24`) can ping every internal server and even ping the edge router\'s inside interface (`10.255.0.1`), yet drops 100% of traffic to `8.8.8.8`, always check the NAT overload ACL (`access-list 10`): '
            'if `10.40.0.0` is missing from `access-list 10`, packets egress `Gi0/1` onto the public Internet with untranslated RFC 1918 source IP `10.40.0.45` and are immediately dropped by the ISP\'s anti-spoofing filters.'
        )
    ),
    (5, 1): (
        '<h3>N10-009 Deep Dive: Syslog (RFC 5424), SNMPv3 OIDs, NetFlow/IPFIX, SPAN/TAPs &amp; Interface Error Counters</h3>'
        '<p>Observability combines push telemetry (Syslog, SNMP Traps, NetFlow/IPFIX exports) with pull polling (SNMP GET/GETNEXT/GETBULK on UDP 161) and wire-level packet capture (SPAN port mirroring or passive optical/copper network TAPs). '
        'Syslog (UDP 514 or TLS TCP 6514, RFC 5424) classifies every event by 8 numeric severity levels from `0` ( most critical) to `7` (least critical) — remembered by the mnemonic **Every Awesome Cisco Engineer Will Need Icewater Daily**: '
        '`0 Emergency`, `1 Alert`, `2 Critical`, `3 Error`, `4 Warning`, `5 Notice`, `6 Informational`, `7 Debug`. '
        'While SNMP polls device health metrics (CPU, memory, interface octets, optical dBm) via hierarchical Management Information Base (MIB) Object Identifiers (OIDs), **NetFlow v9 / IPFIX (RFC 7011, UDP 2055/4739)** summarizes 5-tuple traffic flows (who talked to whom, on which port, for how many bytes/packets) without capturing full packet payloads.</p>'
        + _tbl(
            ['Interface Counter / Metric', 'Layer / Direction', 'Physical or Protocol Root Cause &amp; Remediation'],
            [
                ['CRC / FCS Errors &amp; Frame Alignment', 'Layer 1 / Ingress', 'Damaged copper pair, EMI, dirty fiber ferrule, or full/half duplex mismatch'],
                ['Runts (<64B) &amp; Late Collisions', 'Layer 1/2 / Half-Duplex', 'Runts from collisions; Late collisions (>64B into frame) mean cable >100m or duplex mismatch'],
                ['Giants (>1518B / >1522B)', 'Layer 2 / Ingress', 'Upstream host or switch sending 9000B jumbo frames into a 1500B MTU interface'],
                ['Output Drops / Queue Exhaustion', 'Layer 2/3 / Egress', 'Speed step-down (10G core bursting into 1G uplink); add QoS shaping/policing or LACP'],
                ['Input Queue Drops / Overruns', 'Layer 1/2 / Ingress', 'ASIC/CPU buffer overwhelmed by broadcast storm or microbursts'],
            ]
        )
        + _cli(
            'Correlating Rising CRC/Giant Counters and NetFlow Top-Talkers with iperf3 Bandwidth Validation',
            'SW-CORE-01# show interfaces Gi0/2 | include line protocol|MTU|input errors|output drops\n'
            'GigabitEthernet0/2 is up, line protocol is up (connected)\n'
            '  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec, \n'
            '  1482 input errors, 1410 CRC, 72 frame, 0 overrun, 0 ignored\n'
            '  Total output drops: 49210\n'
            '$ iperf3 -c 10.100.10.50 -P 4 -t 10\n'
            '[SUM]   0.00-10.00  sec  1.09 GBytes   938 Mbits/sec  1420             sender\n'
            '[SUM]   0.00-10.00  sec  1.09 GBytes   936 Mbits/sec                  receiver',
            'In `show interfaces Gi0/2`, `1410 CRC` errors paired with `49210 Total output drops` reveal two distinct physical/capacity issues: '
            'the ingress CRC errors indicate physical layer corruption (bad patch cord or dirty SFP transceiver), which in turn forces TCP endpoints (`iperf3 -P 4`) to record `1420` TCP retransmissions (`sender` column). '
            'Always run `clear counters Gi0/2` after replacing a patch cord or cleaning fiber so you can verify the CRC counter stays at `0` under an active `iperf3` load test.'
        )
    ),
    (5, 2): (
        '<h3>N10-009 Deep Dive: Management Plane Hardening, TACACS+ vs RADIUS, SNMPv3 authPriv &amp; Out-of-Band (OOB)</h3>'
        '<p>Hardening the network **Management Plane** ensures that administrative credentials, configuration files, and telemetry cannot be intercepted or hijacked from production user VLANs. '
        'Every enterprise switch, router, firewall, and wireless controller must enforce five baseline controls: '
        '(1) Disable cleartext protocols (`Telnet` TCP 23, `HTTP` TCP 80, `FTP` TCP 21, `TFTP` UDP 69, and `SNMPv1/v2c` community strings) in favor of `SSHv2` (TCP 22), `HTTPS` (TCP 443), `SCP/SFTP` (TCP 22), and **SNMPv3 `authPriv`** (SHA-256 HMAC authentication + AES-128/256 encryption); '
        '(2) Restrict VTY/HTTPS management access via an **Infrastructure Control-Plane ACL (`access-class`)** to a dedicated Management VLAN or **Out-of-Band (OOB)** terminal server network; '
        '(3) Authenticate administrators via centralized **AAA** with an offline local `enable secret` (Type 8 PBKDF2-SHA256 or Type 9 scrypt) break-glass account; '
        '(4) Synchronize clocks via authenticated **NTP (UDP 123)** so syslog and SIEM events correlate accurately; and '
        '(5) Back up running and startup configurations to version-controlled Git/NCM storage after every approved change.</p>'
        + _tbl(
            ['AAA Dimension', 'TACACS+ (RFC 8907)', 'RADIUS (RFC 2865 / 2866)', 'Enterprise Deployment Use Case'],
            [
                ['Transport &amp; Ports', 'TCP Port 49', 'UDP Ports 1812 (Auth) &amp; 1813 (Acct); TCP 2083 RadSec', 'TACACS+ for device CLI admin; RADIUS for 802.1X Wi-Fi/VPN'],
                ['Packet Encryption', 'Encrypts ENTIRE payload body', 'Encrypts password attribute only (RadSec TLS encrypts all)', 'TACACS+ hides command arguments and config strings on wire'],
                ['AAA Separation', 'Separates AuthN, AuthZ &amp; Acct', 'Combines Authentication + Authorization in Access-Accept', 'TACACS+ supports per-command authorization &amp; audit logging'],
            ]
        )
        + _cli(
            'Configuring SNMPv3 authPriv (SHA/AES), SSHv2-Only VTYs, TACACS+ &amp; Authenticated NTP',
            'SW-CORE-01(config)# ip ssh version 2\n'
            'SW-CORE-01(config)# ip access-list standard MGMT_JUMP_HOSTS\n'
            'SW-CORE-01(config-std-nacl)# permit 10.100.99.0 0.0.0.255\n'
            'SW-CORE-01(config-std-nacl)# deny any log\n'
            'SW-CORE-01(config)# line vty 0 15\n'
            'SW-CORE-01(config-line)# transport input ssh\n'
            'SW-CORE-01(config-line)# access-class MGMT_JUMP_HOSTS in\n'
            'SW-CORE-01(config-line)# exec-timeout 10 0\n'
            'SW-CORE-01(config)# snmp-server group NETOPS_V3 v3 priv\n'
            'SW-CORE-01(config)# snmp-server user poller01 NETOPS_V3 v3 auth sha S3cur3Auth!26 priv aes 128 S3cur3Priv!26 access MGMT_JUMP_HOSTS\n'
            'SW-CORE-01(config)# ntp authenticate\n'
            'SW-CORE-01(config)# ntp server 10.100.10.123 key 1',
            'Compare the three SNMPv3 security levels defined in RFC 3414: `noAuthNoPriv` (username only, no integrity or encryption), `authNoPriv` (HMAC-SHA authentication only, cleartext payload), and `authPriv` (`v3 priv` in IOS—requires both HMAC-SHA authentication and AES cipher encryption). '
            'Binding `access MGMT_JUMP_HOSTS` to both the VTY lines and the SNMPv3 user guarantees that even if a credential leaks on a user VLAN, the switch drops the management packet before authentication.'
        )
    ),
})

NETOPS_DEPTH_HTML.update({
    (5, 3): (
        '<h3>N10-009 Deep Dive: Zero-Trust Architecture (NIST SP 800-207), Micro-Segmentation, PVLANs &amp; 802.1X NAC</h3>'
        '<p>Traditional perimeter security assumed that any host inside the corporate LAN VLAN could be implicitly trusted—allowing a single compromised workstation or IoT sensor to move laterally via SMB (TCP 445), RDP (TCP 3389), or WinRM (TCP 5985/5986). '
        '<strong>Zero-Trust Architecture (NIST SP 800-207)</strong> eliminates implicit trust based on network location: every connection request is authenticated, authorized, and encrypted dynamically by a **Policy Decision Point (PDP = Policy Engine + Policy Administrator)** and enforced by a **Policy Enforcement Point (PEP)** based on user identity, MFA token, endpoint posture (EDR active, OS patch level, BitLocker/FileVault status), and least-privilege application scope. '
        'At Layer 2 and Layer 3, network engineers reinforce Zero Trust using **North-South zone firewalls**, **East-West micro-segmentation** (VXLAN Group-Based Policy / SGTs / hypervisor distributed firewalls), **Private VLANs (PVLANs, RFC 5517)**, and **IEEE 802.1X Network Access Control (NAC)** with RADIUS Change of Authorization (CoA, RFC 5176 on UDP 3799).</p>'
        + _tbl(
            ['Segmentation Control', 'Enforcement Layer', 'Traffic Direction Controlled', 'Operational Mechanics &amp; Use Case'],
            [
                ['VLANs + Inter-VLAN Firewall ACLs', 'Layer 2 / Layer 3', 'North-South between subnets', 'Separates Corp, Voice, Guest, IoT, PCI-DSS, and Management zones'],
                ['Private VLAN (PVLAN) Isolated Port', 'Layer 2 within 1 subnet', 'Blocks East-West host-to-host L2', 'Isolated ports talk ONLY to the Promiscuous port (default gateway)'],
                ['Private VLAN Community Port', 'Layer 2 within 1 subnet', 'Permits intra-community L2 only', 'Servers in same community talk to each other &amp; Promiscuous gateway'],
                ['Micro-Segmentation / SGT / NSX', 'Layer 3/4/7 vNIC / Fabric', 'East-West inside same VLAN/subnet', 'Blocks workstation-to-workstation SMB/RDP even on same /24 subnet'],
                ['802.1X NAC + Dynamic VLAN / dACL', 'Layer 2 Access Port / WLAN', 'Pre-admission port quarantine', 'Assigns remediation VLAN or guest VLAN until posture check passes'],
            ]
        )
        + _cli(
            'Auditing 802.1X Port Authentication, RADIUS CoA Quarantine &amp; East-West Deny ACLs',
            'SW-ACC-04# show authentication sessions interface Gi0/10 details\n'
            '            Interface:  GigabitEthernet0/10\n'
            '          MAC Address:  0050.569a.4419\n'
            '         IPv4 Address:  10.10.20.88\n'
            '            User-Name:  corp\\jdoe\n'
            '               Status:  Authorized\n'
            '               Domain:  DATA\n'
            '       Oper host mode:  multi-auth\n'
            '      Vlan Policy:      20\n'
            '      ACS ACL:          xACSACLx-IP-PERMIT_CORP_EGRESS-65a1b2c\n'
            'SW-ACC-04# show ip access-lists xACSACLx-IP-PERMIT_CORP_EGRESS-65a1b2c\n'
            'Extended IP access list xACSACLx-IP-PERMIT_CORP_EGRESS-65a1b2c\n'
            '    10 permit udp any host 10.100.10.53 eq domain\n'
            '    20 permit tcp any host 10.100.10.88 eq 88\n'
            '    30 deny tcp any 10.10.20.0 0.0.0.255 eq 445 log\n'
            '    40 deny tcp any 10.10.20.0 0.0.0.255 eq 3389 log\n'
            '    50 permit ip any any',
            'Look at how the RADIUS server pushed a downloadable ACL (`dACL`) upon 802.1X authorization on `Gi0/10`: lines 30 and 40 explicitly block lateral workstation-to-workstation SMB (`eq 445`) and RDP (`eq 3389`) across `10.10.20.0/24` at the ingress switch port itself, stopping ransomware lateral movement cold even within the same subnet.'
        )
    ),
    (5, 4): (
        '<h3>N10-009 Capstone Field Guide: Complete Switch &amp; Router Hardening Audit Checklist</h3>'
        '<p>During a security compliance audit (CIS Benchmark / DISA STIG / PCI-DSS 4.0), an unhardened access switch can expose the entire enterprise fabric through Layer-2 control-plane attacks: '
        '**VLAN Hopping** (via Dynamic Trunking Protocol `DTP` auto-negotiation or double-tagging on Native VLAN 1), **STP Root Hijacking** (plugging in a rogue bridge with Priority 0), **CAM Table Overflow** (flooding thousands of spoofed source MACs until the switch fails open like a hub), **DHCP Starvation / Rogue DHCP**, and **ARP Cache Poisoning**. '
        'Every production access port and management plane must be audited against the complete Layer-2/Layer-3 hardening baseline below.</p>'
        + _cli(
            'Production Access-Port &amp; Control-Plane Hardening Template (Cisco IOS XE)',
            '! 1. Global Layer-2 Control-Plane Protection\n'
            'ip dhcp snooping\n'
            'ip dhcp snooping vlan 10,20,30\n'
            'no ip dhcp snooping information option\n'
            'ip arp inspection vlan 10,20,30\n'
            'spanning-tree mode rapid-pvst\n'
            'spanning-tree portfast bpduguard default\n'
            '!\n'
            '! 2. Hardened End-Host Access Port Template\n'
            'interface range GigabitEthernet0/2 - 23\n'
            ' switchport mode access\n'
            ' switchport access vlan 10\n'
            ' switchport nonegotiate\n'
            ' switchport port-security\n'
            ' switchport port-security maximum 2\n'
            ' switchport port-security violation restrict\n'
            ' switchport port-security mac-address sticky\n'
            ' ip verify source\n'
            ' ip dhcp snooping limit rate 15\n'
            ' ip arp inspection limit rate 15\n'
            ' spanning-tree portfast\n'
            ' spanning-tree bpduguard enable\n'
            ' no cdp enable\n'
            '!\n'
            '! 3. Quarantine Unused Ports\n'
            'interface range GigabitEthernet0/24 - 47\n'
            ' switchport mode access\n'
            ' switchport access vlan 999\n'
            ' switchport nonegotiate\n'
            ' shutdown',
            'Every line in this template counters a specific N10-009 attack vector: `switchport mode access` + `switchport nonegotiate` disables DTP to prevent VLAN hopping; `spanning-tree bpduguard enable` blocks rogue switches; `switchport port-security` prevents CAM overflow; `ip dhcp snooping` blocks rogue DHCP servers; `ip arp inspection` validates ARP replies against the DHCP snooping binding table; `ip verify source` (IP Source Guard) blocks spoofed source IPs; and `no cdp enable` stops reconnaissance of switch IOS versions and management IPs.'
        )
    ),
    (6, 1): (
        '<h3>N10-009 Deep Dive: Enterprise Failure Pattern Library — Blast-Radius Matrix &amp; Telemetry Signatures</h3>'
        '<p>Rapid fault isolation depends on matching the **blast radius** (single host, single port, single VLAN, single closet/building, or multi-site WAN) and the **protocol symptom** against known failure signatures. '
        'Before running intrusive commands, classify the incident along two axes: **Scope** (who is affected and what shared infrastructure sits at their lowest common denominator) and **Layer** (which OSI layer first fails a deterministic test).</p>'
        + _tbl(
            ['Symptom Pattern', 'Blast Radius', 'Primary Root Cause', 'Definitive CLI / Tool Proof'],
            [
                ['169.254.x.x (APIPA) on 1 new VLAN; other VLANs get leases', 'Single VLAN', 'Missing ip helper-address on SVI or exhausted DHCP scope', 'show ip interface VlanX | include Helper'],
                ['Can ping 8.8.8.8; cannot open any https://hostname URL', 'VLAN or Enterprise', 'DNS UDP/TCP 53 blocked or recursive resolver service down', 'dig @10.100.10.53 example.com; Test-NetConnection -Port 53'],
                ['Pings &amp; SSH login work; TLS pages &amp; bulk transfers hang', 'VPN / WAN Tunnel', 'PMTUD black hole (MTU < 1500 + ICMP Type 3 Code 4 blocked)', 'ping -M do -s 1472 (Linux) / ping -f -l 1472 (Windows)'],
                ['Intermittent packet loss to default gateway; MAC flips in ARP', 'Single Subnet/VLAN', 'Duplicate IP address or FHRP (HSRP/VRRP) active/active split-brain', 'arp -a / ip neigh show; show ip arp | include 10.10.10.1'],
                ['All users on 1 switch drop after patch cord plugged into 2 jacks', 'Single Closet/VLAN', 'Layer-2 switching loop (STP disabled or missing BPDU Guard)', 'show processes cpu; show mac address-table count'],
                ['100 Mbps link has high CRC errors on 1 side &amp; late collisions on other', 'Single Point-to-Point Link', 'Duplex mismatch (one side hardcoded 100/Full, other Auto -> 100/Half)', 'show interfaces Gi0/X; ethtool eth0'],
            ]
        )
        + _cli(
            'Isolating a PMTUD Black Hole Across an IPsec VPN Using Don\'t-Fragment (DF) Probe Sweeps',
            '$ ping -c 2 -M do -s 1472 10.50.10.25\n'
            'PING 10.50.10.25 (10.50.10.25) 1472(1500) bytes of data.\n'
            'ping: local error: message too long, mtu=1400\n'
            '$ ping -c 2 -M do -s 1372 10.50.10.25\n'
            'PING 10.50.10.25 (10.50.10.25) 1372(1400) bytes of data.\n'
            '1380 bytes from 10.50.10.25: icmp_seq=1 ttl=61 time=14.2 ms\n'
            'RTR-WAN-01(config)# interface Tunnel10\n'
            'RTR-WAN-01(config-if)# ip mtu 1400\n'
            'RTR-WAN-01(config-if)# ip tcp adjust-mss 1360',
            'Remember the exact ICMP payload math for N10-009: an IPv4 header is `20 bytes` and an ICMP Echo header is `8 bytes` (`28 bytes` total). '
            'Therefore, `ping -M do -s 1472` (Linux) or `ping -f -l 1472` (Windows) sends an unfragmented `1472 + 28 = 1500-byte` IPv4 packet. '
            'When the tunnel MTU is `1400 bytes`, the maximum unfragmented ICMP payload is `1400 - 28 = 1372 bytes`, and the optimal TCP MSS clamp is `1400 - 20 (IPv4) - 20 (TCP) = 1360 bytes`.'
        )
    ),
    (6, 2): (
        '<h3>N10-009 Deep Dive: CompTIA 7-Step Troubleshooting Methodology Under Production Incident Pressure</h3>'
        '<p>Under major incident pressure (Severity-1 outage), ad-hoc guessing ("reboot the core switch," "disable the firewall," or changing three parameters simultaneously) destroys forensic evidence and compounds downtime. '
        'The CompTIA N10-009 7-step methodology enforces disciplined engineering control at every stage:</p>'
        '<ol>'
        '<li><strong>Identify the problem</strong> — Gather information, question users, identify symptoms, determine if anything changed (correlate with the Change Advisory Board / NCM config diff log), duplicate the problem if possible, and approach multiple problems individually.</li>'
        '<li><strong>Establish a theory of probable cause</strong> — Question the obvious and consider multiple approaches: top-down, bottom-up, or divide-and-conquer across the OSI layers.</li>'
        '<li><strong>Test the theory to determine Cause</strong> — Run one non-destructive diagnostic or single-variable test. If the theory is confirmed, determine the next steps to resolve the problem. If the theory is disproved, establish a new theory or escalate to Tier 3 / vendor TAC.</li>'
        '<li><strong>Establish a plan of action to resolve the problem and identify potential effects</strong> — Evaluate blast radius, maintenance window requirements, and always write a tested **rollback plan** before executing any change.</li>'
        '<li><strong>Implement the solution or escalate as necessary</strong> — Apply a single controlled change (or execute the approved emergency change request).</li>'
        '<li><strong>Verify full system functionality and, if applicable, implement preventive measures</strong> — Re-run the exact failing test from Step 1, confirm with affected end users that business workflows are restored, and add monitoring alerts or configuration guardrails.</li>'
        '<li><strong>Document findings, actions, outcomes, and lessons learned</strong> — Update network diagrams, IPAM, runbooks, and the incident ticket record.</li>'
        '</ol>'
        + _cli(
            'Auditing Configuration Drift &amp; Executing an Atomic Rollback During a Change Window',
            'RTR-CORE-01# show archive config differences nvram:startup-config system:running-config\n'
            '!Contextual Config Diffs:\n'
            '+router ospf 1\n'
            '+ passive-interface GigabitEthernet0/1\n'
            'RTR-CORE-01# configure replace nvram:startup-config force\n'
            'Total number of passes: 1\n'
            'Rollback Done',
            'Notice how `show archive config differences` immediately exposes that an engineer accidentally configured `passive-interface GigabitEthernet0/1` under `router ospf 1`, tearing down the OSPF neighbor adjacency to the distribution block. '
            'Rather than manually guessing inverse commands under pressure, `configure replace nvram:startup-config force` (or `commit confirmed 5` in JUNOS/IOS-XR) performs an atomic configuration rollback.'
        )
    ),
    (6, 3): (
        '<h3>N10-009 Deep Dive: Post-Change Verification, IPAM / Diagram Governance &amp; Configuration Management</h3>'
        '<p>A network repair is incomplete until **full system functionality** is verified from the user perspective, **startup configuration** is persisted to non-volatile memory (`copy running-config startup-config`), and **authoritative documentation** (physical/logical diagrams, rack elevations, cable matrices, IP Address Management `IPAM`, and Network Configuration Management `NCM` baselines) is updated. '
        'Leaving running configuration unsaved means the next power outage or maintenance reload silently reintroduces the original outage months later.</p>'
        + _tbl(
            ['Artifact / Record', 'Core Contents &amp; Schema', 'Operational Role During Incidents &amp; Audits'],
            [
                ['Physical Network Diagram', 'Rack/RU locations, patch panel ports, fiber strands, transceiver types, cable labels', 'Isolates Layer-1 closet runs, MPOE demarcs, and single points of failure'],
                ['Logical Network Diagram', 'VLAN IDs, IPv4/IPv6 CIDR subnets, OSPF areas, BGP ASNs, FHRP VIPs, Firewall zones', 'Guides Layer-3 traceroute analysis, ACL placement, and routing design'],
                ['IPAM (IP Address Management)', 'Subnet allocations, static server/VIP reservations, DHCP scope utilization, DNS A/PTR sync', 'Prevents overlapping subnets and duplicate IP conflicts during deployments'],
                ['Golden Config / Git NCM', 'Versioned startup-config diffs, AAA/SNMPv3 compliance templates, automated nightly backups', 'Detects unauthorized config drift and enables 1-click disaster recovery'],
            ]
        )
        + _cli(
            'Post-Maintenance Verification Checklist &amp; NVRAM Persistence Proof',
            'RTR-CORE-01# show ip ospf neighbor\n'
            'Neighbor ID     Pri   State           Dead Time   Address         Interface\n'
            '10.255.255.2      1   FULL/DR         00:00:38    10.10.12.2      GigabitEthernet0/0\n'
            '10.255.255.3      1   FULL/BDR        00:00:35    10.10.13.2      GigabitEthernet0/1\n'
            'RTR-CORE-01# ping 10.30.0.45 source 10.10.10.1 repeat 5\n'
            'Type escape sequence to abort.\n'
            'Sending 5, 100-byte ICMP Echos to 10.30.0.45, timeout is 2 seconds:\n'
            'Packet sent with a source address of 10.10.10.1\n'
            '!!!!!\n'
            'Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/3 ms\n'
            'RTR-CORE-01# copy running-config startup-config\n'
            'Destination filename [startup-config]? \n'
            'Building configuration...\n'
            '[OK]',
            'Using an **extended ping (`ping <dest> source <src-interface>`)** from the router\'s VLAN 10 gateway (`10.10.10.1`) to a host in VLAN 30 (`10.30.0.45`) proves bidirectional inter-VLAN routing and ACL permit rules without needing to walk to a workstation.'
        )
    ),
    (6, 4): (
        '<h3>N10-009 Capstone Field Guide: Multi-Layer Enterprise Outage Triage &amp; Post-Mortem Walkthrough</h3>'
        '<p>In a full-scale enterprise capstone incident, multiple symptoms often stem from a single underlying change—or two independent faults mask each other (for example, a corrected VLAN trunk still fails to pass HTTPS traffic because a new firewall ACL or NAT rule is missing). '
        'Work methodically from the shared infrastructure outward, verify each layer with read-only `show` commands before editing configuration, and record timestamps and before/after diffs for the post-incident review.</p>'
        + _cli(
            'Full Multi-Hop Verification Sequence Across Access Switch, Core Router &amp; Perimeter Firewall',
            'SW-ACC-01# show interfaces trunk | include Gi0/1\n'
            'Gi0/1       on               802.1q         trunking      99\n'
            'Gi0/1       10,20,30,40,99\n'
            'RTR-CORE-01# show ip route 10.40.0.0\n'
            'Routing entry for 10.40.0.0/24\n'
            '  Known via "ospf 1", distance 110, metric 2, type intra area\n'
            '  Last update from 10.10.12.2 on GigabitEthernet0/0, 00:14:22 ago\n'
            '  Routing Descriptor Blocks:\n'
            '  * 10.10.12.2, from 10.255.255.2, 00:14:22 ago, via GigabitEthernet0/0\n'
            '      Route metric is 2, traffic share count is 1\n'
            'FW-EDGE-01# show conn address 10.40.0.45\n'
            'TCP OUT 203.0.113.5:51892 INSIDE 10.40.0.45:51892 -> 198.51.100.20:443, idle 0:00:02, bytes 48210, flags UIO',
            'This three-device verification chain proves the entire packet path end-to-end: (1) `SW-ACC-01` confirms VLAN 40 is allowed and active on trunk `Gi0/1`; (2) `RTR-CORE-01` confirms intra-area OSPF route `10.40.0.0/24` (AD 110, metric 2) is installed in the RIB/FIB; and (3) `FW-EDGE-01` state table flags `UIO` (`Up`, `Inbound data`, `Outbound data`) confirm bidirectional TCP 443 payload flow through PAT address `203.0.113.5`.'
        )
    ),
})

NETOPS_DEPTH_HTML.update({
    (9, 1): (
        '<h3>N10-009 CLI Lab Reference: Out-of-Band Console Serial Parameters, IOS Privilege Modes &amp; LLDP/CDP Discovery</h3>'
        '<p>Before configuring IP routing or VLAN trunks on a bare-metal switch or router, an engineer connects via an Out-of-Band (OOB) RJ-45 RS-232 rollover console cable or USB Type-C console port using standard serial terminal parameters: **9600 baud, 8 data bits, no parity, 1 stop bit, and no flow control (`9600-8-N-1`)**. '
        'Cisco IOS XE separates command execution into hierarchical privilege modes to prevent accidental outages: '
        '**User EXEC (`Switch>`)** (Privilege Level 1, read-only basic status), **Privileged EXEC (`Switch#`)** (Privilege Level 15, entered via `enable`, unlocks full `show`, `debug`, `copy`, and `reload` commands), **Global Configuration (`Switch(config)#`)** (entered via `configure terminal`, modifies system-wide running-config), and sub-modes including **Interface (`Switch(config-if)#`)**, **Subinterface (`Router(config-subif)#`)**, **VLAN (`Switch(config-vlan)#`)**, **Router (`Router(config-router)#`)**, and **Line (`Switch(config-line)#`)**. '
        'Before making any topological change, run **IEEE 802.1AB Link Layer Discovery Protocol (`show lldp neighbors detail`)** or **Cisco Discovery Protocol (`show cdp neighbors detail`)** to verify physical port-to-port wiring across switches, routers, IP phones, and access points.</p>'
        + _cli(
            'Mapping Unknown Wiring Closet Neighbors with CDP and Vendor-Neutral IEEE 802.1AB LLDP',
            'SW1# show cdp neighbors detail | include Device ID|IP address|Platform|Interface\n'
            'Device ID: RTR1.novak.internal\n'
            '  IP address: 10.10.10.1\n'
            'Platform: Cisco ISR4331/K9,  Capabilities: Router Switch IGMP \n'
            'Interface: GigabitEthernet0/1,  Port ID (outgoing port): GigabitEthernet0/0\n'
            'SW1# show lldp neighbors\n'
            'Capability codes: (R) Router, (B) Bridge, (T) Telephone, (W) WLAN Access Point\n'
            'Device ID           Local Intf     Hold-time  Capability      Port ID\n'
            'RTR1                Gi0/1          120        R               Gi0/0\n'
            'AP-FL1-WEST         Gi0/10         120        B,W             eth0',
            'While CDP is Cisco-proprietary (multicast MAC `01:00:0c:cc:cc:cc`, default timer 60s, holdtime 180s), **LLDP (IEEE 802.1AB)** is vendor-neutral (multicast MAC `01:80:c2:00:00:0e`, default timer 30s, holdtime 120s) and includes **LLDP-MED** extensions that negotiate voice VLAN IDs and exact PoE wattage with VoIP phones and wireless access points.'
        )
    ),
    (9, 2): (
        '<h3>N10-009 CLI Lab Reference: Creating VLANs, Assigning Access Ports &amp; Verifying CAM / Trunk State</h3>'
        '<p>On a Layer-2 switch, creating a VLAN in the VLAN database (`vlan 10` / `name USERS`) and assigning an interface to that VLAN (`switchport mode access` / `switchport access vlan 10`) are two distinct configuration steps. '
        'If an engineer assigns `switchport access vlan 20` on `Fa0/2` when VLAN 20 has not yet been created, modern IOS automatically creates VLAN 20 in `vlan.dat`, whereas assigning a trunk allowed list (`switchport trunk allowed vlan 10,20,30`) NEVER auto-creates missing VLANs. '
        'Always verify access port membership with `show vlan brief` and verify per-port operational mode and trunk negotiation status with `show interfaces <id> switchport`.</p>'
        + _cli(
            'Configuring Access VLANs 10 &amp; 20, Disabling DTP &amp; Auditing Switchport Operational Status',
            'SW1# configure terminal\n'
            'SW1(config)# vlan 10\n'
            'SW1(config-vlan)# name USERS\n'
            'SW1(config-vlan)# vlan 20\n'
            'SW1(config-vlan)# name SERVERS\n'
            'SW1(config-vlan)# exit\n'
            'SW1(config)# interface FastEthernet0/1\n'
            'SW1(config-if)# description WORKSTATION_VLAN10\n'
            'SW1(config-if)# switchport mode access\n'
            'SW1(config-if)# switchport access vlan 10\n'
            'SW1(config-if)# switchport nonegotiate\n'
            'SW1(config-if)# spanning-tree portfast\n'
            'SW1(config-if)# spanning-tree bpduguard enable\n'
            'SW1(config-if)# end\n'
            'SW1# show interfaces FastEthernet0/1 switchport | include Name|Mode|Access Mode VLAN|Negotiation\n'
            'Name: Fa0/1\n'
            'Administrative Mode: static access\n'
            'Operational Mode: static access\n'
            'Negotiation of Trunking: Off\n'
            'Access Mode VLAN: 10 (USERS)',
            'Inspecting `show interfaces FastEthernet0/1 switchport` confirms both the **Administrative Mode** (what you configured) and the **Operational Mode** (what the port is currently doing on the wire), and proves that Dynamic Trunking Protocol (`Negotiation of Trunking: Off`) is disabled.'
        )
    ),
    (9, 3): (
        '<h3>N10-009 CLI Lab Reference: Router Interface Bring-Up, Status/Protocol Pairs &amp; Connected/Local RIB Entries</h3>'
        '<p>Unlike Layer-2 switch ports (which default to `no shutdown` in VLAN 1), Cisco router physical interfaces ship **administratively down (`shutdown`)** by default to prevent accidental routing loops or duplicate IP conflicts when cabling a new chassis. '
        'When reading `show ip interface brief`, the two status columns (**Status** = Layer 1 physical carrier; **Protocol** = Layer 2 data-link framing/keepalives) provide an instant OSI Layer-1 vs Layer-2 diagnosis.</p>'
        + _tbl(
            ['Status (Layer 1)', 'Protocol (Layer 2)', 'Root Cause &amp; Immediate Remediation Step'],
            [
                ['administratively down', 'down', 'Interface has shutdown configured; enter interface mode and run no shutdown'],
                ['down', 'down', 'No Layer-1 carrier: unplugged cable, dead SFP, wrong fiber Tx/Rx polarity, or remote port shut'],
                ['up', 'down', 'Layer-1 carrier present, Layer-2 failing: encapsulation mismatch, clock rate missing, keepalive failure, or LACP mismatch'],
                ['up', 'up', 'Layer 1 and Layer 2 operational; installs Connected (C) subnet route and Local (L) /32 host route in RIB'],
            ]
        )
        + _cli(
            'Bringing Up Router Interfaces and Distinguishing Connected (C) vs Local (L) Routes in IOS XE',
            'RTR1# configure terminal\n'
            'RTR1(config)# interface GigabitEthernet0/0\n'
            'RTR1(config-if)# description LAN_GATEWAY_VLAN10\n'
            'RTR1(config-if)# ip address 10.10.10.1 255.255.255.0\n'
            'RTR1(config-if)# no shutdown\n'
            'RTR1(config-if)# end\n'
            'RTR1# show ip route connected\n'
            'C        10.10.10.0/24 is directly connected, GigabitEthernet0/0\n'
            'L        10.10.10.1/32 is directly connected, GigabitEthernet0/0',
            'Since IOS 15 / IOS XE, every active IPv4 interface installs two RIB entries: a **Connected (`C`)** route for the entire subnet prefix (`10.10.10.0/24`, AD 0) and a **Local (`L`)** `/32` host route (`10.10.10.1/32`, AD 0) for Packets destined to the router\'s own interface IP.'
        )
    ),
    (9, 4): (
        '<h3>N10-009 CLI Lab Reference: Router-on-a-Stick (802.1Q Subinterfaces) vs Multilayer Switch SVIs</h3>'
        '<p>Inter-VLAN routing can be implemented either via **Router-on-a-Stick (RoaS)**—where a single physical router interface (`Gi0/0`) connects over an 802.1Q trunk to a Layer-2 switch and terminates logical subinterfaces (`Gi0/0.10`, `Gi0/0.20`)—or on a **Layer-3 Multilayer Switch using Switched Virtual Interfaces (`interface Vlan10`, `interface Vlan20`)** with global `ip routing` enabled. '
        'On Router-on-a-Stick, three rules are mandatory: (1) the physical parent interface (`Gi0/0`) must have **no IP address** and be enabled with `no shutdown`; (2) each subinterface MUST configure `encapsulation dot1Q <vlan-id>` **before** IOS will accept the `ip address` command; and (3) the connected switch port (`Gi0/1`) must be configured as an 802.1Q trunk (`switchport mode trunk`) allowing all routed VLANs.</p>'
        + _cli(
            'Complete Router-on-a-Stick Configuration &amp; Multilayer Switch SVI Comparison',
            '! Router-on-a-Stick (RTR1):\n'
            'RTR1(config)# interface GigabitEthernet0/0\n'
            'RTR1(config-if)# no ip address\n'
            'RTR1(config-if)# no shutdown\n'
            'RTR1(config-if)# interface GigabitEthernet0/0.10\n'
            'RTR1(config-subif)# description DEFAULT_GW_USERS_VLAN10\n'
            'RTR1(config-subif)# encapsulation dot1Q 10\n'
            'RTR1(config-subif)# ip address 10.10.10.1 255.255.255.0\n'
            'RTR1(config-subif)# interface GigabitEthernet0/0.20\n'
            'RTR1(config-subif)# description DEFAULT_GW_SERVERS_VLAN20\n'
            'RTR1(config-subif)# encapsulation dot1Q 20\n'
            'RTR1(config-subif)# ip address 10.10.20.1 255.255.255.0\n'
            '!\n'
            '! Equivalent Layer-3 Switch SVI Configuration (SW-CORE):\n'
            'SW-CORE(config)# ip routing\n'
            'SW-CORE(config)# interface Vlan10\n'
            'SW-CORE(config-if)# ip address 10.10.10.1 255.255.255.0\n'
            'SW-CORE(config-if)# no shutdown',
            'Note why an SVI (`interface Vlan10`) on a Layer-3 switch sometimes shows `Vlan10 is up, line protocol is down`: '
            'an SVI\'s line protocol only comes `up` when (1) VLAN 10 exists and is active in the local VLAN database, AND (2) at least one Layer-2 access or trunk port on that switch is actively forwarding (`STP FWD`) in VLAN 10!'
        )
    ),
    (9, 5): (
        '<h3>N10-009 CLI Lab Reference: End-to-End Closet Drop Turn-Up &amp; Next-Hop Static Routing</h3>'
        '<p>When turning up a new wiring closet drop that must reach both local servers and remote branch subnets, you must verify the entire Layer-1-to-Layer-3 chain: '
        'access port VLAN assignment on the switch, 802.1Q trunk allowance between switch and router, router subinterface gateway IP, and static or dynamic routes (`ip route <prefix> <mask> <next-hop-ip>`) in both forward and return directions. '
        'Remember that routing is unidirectional per hop: if Router A has a static route to Router B\'s LAN (`10.50.0.0/24`), but Router B lacks a return route back to Router A\'s VLAN 10 (`10.10.10.0/24`), ICMP Echo Requests reach the destination host, and the replies are dropped at Router B.</p>'
        + _cli(
            'Adding Bidirectional Static &amp; Default Routes and Verifying the Forwarding Path',
            'RTR1(config)# ip route 10.50.0.0 255.255.255.0 172.16.12.2\n'
            'RTR1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1\n'
            'RTR1# show ip route static\n'
            'S*    0.0.0.0/0 [1/0] via 203.0.113.1\n'
            'S     10.50.0.0/24 [1/0] via 172.16.12.2\n'
            'RTR1# traceroute 10.50.0.25 source 10.10.10.1 numeric\n'
            'Type escape sequence to abort.\n'
            'Tracing the route to 10.50.0.25\n'
            '  1 172.16.12.2 1 msec 1 msec 1 msec\n'
            '  2 10.50.0.25 2 msec *  2 msec',
            'In `show ip route static`, `S*` marks the candidate default route (`0.0.0.0/0`), and `[1/0]` indicates Administrative Distance `1` and metric `0`. '
            'To configure a **Floating Static Route** that remains dormant unless an OSPF route (AD 110) fails, append an administrative distance greater than 110: `ip route 10.50.0.0 255.255.255.0 172.16.99.2 200`.'
        )
    ),
    (9, 6): (
        '<h3>N10-009 CLI Lab Reference: Device Identity, Configuration Memory Architecture (RAM vs NVRAM) &amp; Config Diffs</h3>'
        '<p>Every enterprise network device maintains distinct memory partitions with different volatility characteristics: '
        '**RAM / DRAM** holds the active operating system tables (ARP cache, CAM MAC table, OSPF LSDB, RIB/FIB) and the **`running-config`** (every command typed in `configure terminal` takes effect immediately in `running-config` but is lost on power loss or `reload`); '
        '**NVRAM (Non-Volatile RAM)** stores the persistent **`startup-config`** loaded at boot; '
        '**Flash** stores the Cisco IOS XE system image (`.bin` / `packages.conf`) and VLAN database (`vlan.dat`); and '
        '**ROM** holds the bootstrap program and ROMMON recovery firmware.</p>'
        + _cli(
            'Setting Device Identity, Auditing Unsaved Changes &amp; Persisting Running-Config to NVRAM',
            'SW1(config)# hostname SW-BLDG4-IDF2\n'
            'SW-BLDG4-IDF2(config)# ip domain-name novak.internal\n'
            'SW-BLDG4-IDF2(config)# banner motd ^Authorized Novak Enterprise Personnel Only. All sessions logged.^\n'
            'SW-BLDG4-IDF2(config)# end\n'
            'SW-BLDG4-IDF2# show running-config | include hostname|domain-name\n'
            'hostname SW-BLDG4-IDF2\n'
            'ip domain-name novak.internal\n'
            'SW-BLDG4-IDF2# copy running-config startup-config\n'
            'Destination filename [startup-config]? \n'
            'Building configuration...\n'
            '[OK]',
            'Always set a deterministic `hostname` (encoding site, building, and wiring closet role) and `ip domain-name` (required to generate RSA/Ed25519 SSH host keys via `crypto key generate rsa modulus 2048`), and immediately run `copy running-config startup-config` (or `write memory`) after verifying your change so an unexpected power cycle never rolls the closet back to an unconfigured state.'
        )
    ),
})

NETOPS_CASE_STUDIES = {
    (1, 1): (
        '<h4>Production Case Study 1.1: Asymmetric Routing, Stateful Firewall Drops &amp; Overlay VXLAN Encapsulation</h4>'
        '<p>Consider a multi-tier hospital PACS imaging deployment where radiologists in Building A (`10.11.20.0/24`) experience TCP resets (`RST`) exactly 30 seconds into downloading 400 MB DICOM studies from the core imaging cluster (`10.80.10.50/24`), whereas ICMP pings (`ping -c 20 10.80.10.50`) succeed with 0% loss and 1.2 ms RTT. '
        'A novice technician might blame the PACS application or swap the workstation patch cord. An N10-009 engineer inspects the packet path layer by layer: '
        'at Layer 3, traceroute from `10.11.20.44` to `10.80.10.50` crosses Core Router A (`10.255.1.1`) -> Stateful Firewall FW-01 (`10.255.1.2`) -> PACS Server (`10.80.10.50`). '
        'However, on the PACS Server VLAN, the default gateway points to Core Switch B (`10.80.10.2`), which has a lower-cost OSPF route back to `10.11.20.0/24` directly over a bypass fiber link—completely skipping `FW-01`! '
        'Because `FW-01` sees only the client-to-server `SYN` and `ACK` segments and never sees the server-to-client `SYN-ACK` (asymmetric routing), the stateful firewall marks the TCP session half-open, drops subsequent PSH/ACK segments after its 30-second embryonic timeout, and emits a TCP reset. '
        'Correcting the OSPF interface cost (`ip ospf cost 50` on the bypass link) restores symmetric Layer-3 forwarding through `FW-01`.</p>'
        '<p>In modern spine-leaf data centers (clos fabric), engineers also encounter **double encapsulation** via **VXLAN (RFC 7348)**. '
        'A virtual machine sends an inner Layer-2 Ethernet frame (`1514 bytes`) to its hypervisor Virtual Tunnel Endpoint (**VTEP**). '
        'The VTEP wraps that entire inner Ethernet frame inside an 8-byte VXLAN header containing a 24-bit **VXLAN Network Identifier (VNI)** (supporting 16.7 million segments compared with 4,094 IEEE 802.1Q VLANs), encapsulates it in an outer **UDP header (destination port 4789, source port hashed from the inner flow for ECMP load balancing)**, an outer IPv4/IPv6 underlay header, and an outer IEEE 802.3 Ethernet header. '
        'This adds 50 bytes (or 54 bytes with an outer 802.1Q tag) to every frame, requiring all spine and leaf underlay interfaces to be configured for at least `1554` bytes (typically `9000`–`9216` bytes Jumbo MTU) so VTEP-to-VTEP traffic never fragments.</p>'
    ),
    (1, 2): (
        '<h4>Production Case Study 1.2: Campus VLSM Allocation, Route Summarization &amp; IPv6 RA Guard Troubleshooting</h4>'
        '<p>Suppose you are handed the parent block `10.48.0.0/21` (which spans `10.48.0.0` through `10.48.7.255`, providing `2^11 = 2,048` total IPv4 addresses) to design a new manufacturing facility with five distinct segments: '
        '(A) Automated Assembly IoT Sensors requiring 460 hosts; (B) Engineering Workstations requiring 210 hosts; (C) VoIP Desk Phones requiring 110 hosts; (D) Out-of-Band BMS Controllers requiring 26 hosts; and (E) Four point-to-point router links requiring 2 hosts each. '
        'Following strict largest-first VLSM allocation prevents address overlap: '
        'First, allocate **Segment A (460 hosts)** using a `/23` (`2^9 - 2 = 510` usable hosts): `10.48.0.0/23` (network `10.48.0.0`, first usable `10.48.0.1`, last usable `10.48.1.254`, broadcast `10.48.1.255`). '
        'Second, allocate **Segment B (210 hosts)** at the next free boundary (`10.48.2.0`) using a `/24` (`254` usable hosts): `10.48.2.0/24` (`10.48.2.1`–`10.48.2.254`, broadcast `10.48.2.255`). '
        'Third, allocate **Segment C (110 hosts)** at `10.48.3.0` using a `/25` (`126` usable hosts): `10.48.3.0/25` (`10.48.3.1`–`10.48.3.126`, broadcast `10.48.3.127`). '
        'Fourth, allocate **Segment D (26 hosts)** at `10.48.3.128` using a `/27` (`30` usable hosts): `10.48.3.128/27` (`10.48.3.129`–`10.48.3.158`, broadcast `10.48.3.159`). '
        'Fifth, carve the four point-to-point links from `10.48.3.160` using `/30` blocks (`10.48.3.160/30`, `10.48.3.164/30`, `10.48.3.168/30`, `10.48.3.172/30`) or RFC 3021 `/31` blocks, leaving `10.48.4.0/22` (`1,024` addresses) completely free for future growth—while the core router advertises a single **summary route `10.48.0.0/21`** upstream to keep the enterprise OSPF routing table compact.</p>'
        '<p>On the IPv6 side of the same VLANs, suppose workstations suddenly acquire an unexpected `fd00:dead:beef::/64` Unique Local Address and lose IPv6 Internet connectivity. '
        'Running `rdisc6 eth0` or `tcpdump -enni eth0 icmp6` reveals ICMPv6 Type 134 Router Advertisements originating from a developer laptop running Windows Internet Connection Sharing or a rogue Linux `radvd` container on access port `Gi0/14`. '
        'Enabling **IPv6 RA Guard (RFC 6105)** on all host access ports (`ipv6 nd raguard attach-policy HOST_PORT_POLICY`) instructs the switch ASIC to drop any ICMPv6 Type 134 Router Advertisement or Type 137 Redirect arriving on non-uplink ports.</p>'
    ),
    (1, 3): (
        '<h4>Production Case Study 1.3: Ephemeral Port Exhaustion, TCP Keepalives &amp; UDP Application Timeouts</h4>'
        '<p>Every TCP or UDP client connection requires an ephemeral source port chosen from the operating system\'s dynamic port range (IANA RFC 6335 range `49152`–`65535`, giving `16,384` ports on Windows Server; Linux `net.ipv4.ip_local_port_range` defaults to `32768`–`60999`). '
        'When an reverse proxy or PAT firewall opens thousands of short-lived TCP connections to a single backend database IP and port (`10.80.20.10:5432`), closed sockets remain in the **`TIME_WAIT`** state for `2 x MSL` (60–120 seconds) to ensure stray duplicate segments from the old connection cannot corrupt a new connection reusing the same 5-tuple. '
        'If connection churn exceeds ~270 connections/second to a single backend IP:Port from a single source IP, all 16,384 ephemeral ports fill with `TIME_WAIT` entries and new outbound `connect()` calls fail immediately with `EADDRNOTAVAIL`. '
        'Engineers resolve this by enabling connection pooling/multiplexing, adding secondary source IPs to the PAT pool, or switching to persistent HTTP/2 or HTTP/3 (QUIC over UDP 443) sessions.</p>'
        '<p>In voice and video conferencing over RTP/SRTP (UDP ports `16384`–`32767` controlled by SIP TLS on TCP `5061`), transport troubleshooting focuses on **one-way audio** and **jitter buffer underruns**. '
        'When SIP call setup succeeds (phones ring and answer) but one party hears silence, the TCP 5061 signaling path worked, while the unidirectional UDP RTP media stream was blocked by an asymmetric firewall ACL or symmetric NAT rule that failed to open the negotiated SDP media port.</p>'
    ),
    (1, 4): (
        '<h4>Production Case Study 1.4: Multi-Symptom Ticket Triage — Separating Proxy, TLS SAN, DNS &amp; Routing</h4>'
        '<p>During shift turnover, three tickets arrive simultaneously: '
        '**Ticket A**: "Accounting PC-04 cannot reach `\\10.40.10.12/payroll`, but `ping 10.40.10.12` succeeds in 0.8 ms." Because `ping` proves Layers 1–3 (`ICMP Echo`), the block is at Layer 4 (`TCP 445 SMB` filtered by Windows Defender Firewall or an inter-VLAN ACL) or Layer 7 (`NTFS/SMB share permissions`). Running `Test-NetConnection 10.40.10.12 -Port 445` returns `TcpTestSucceeded: False`, proving a Layer-4 port block in one command. '
        '**Ticket B**: "Every laptop in Conference Room B loses Wi-Fi and wired access simultaneously, while the rest of Floor 2 works." Because both the conference room AP and the table RJ-45 jacks patch back to a compact 8-port PoE switch (`SW-CONF-B`), the shared fault domain is the uplink fiber or power supply of `SW-CONF-B` (Layer 1/2). '
        '**Ticket C**: "Remote VPN users can SSH to `10.100.20.15` (`22/tcp`) and query SQL (`1433/tcp`), but opening the internal GitLab web UI (`https://10.100.20.15`) hangs after `ClientHello`." Because small SSH packets work while large TLS `ServerHello` certificate chains hang across the IPsec tunnel, the symptom matches a Layer-3 **MTU / TCP MSS black hole** (`1400-byte` VPN tunnel dropping `1500-byte` DF-set packets).</p>'
    ),
    (2, 1): (
        '<h4>Production Case Study 2.1: Unidirectional Fiber Failure, STP Bridge Assurance &amp; LACP Load-Balance Hashing</h4>'
        '<p>Suppose a pair of distribution switches (`SW-DIST-1` and `SW-DIST-2`) are linked by a 10GBASE-SR multimode fiber pair where the Tx strand from `SW-DIST-1` (Root Bridge) is partially fractured inside a splice tray, while the Rx strand remains intact. '
        'Without protection, `SW-DIST-2` stops receiving BPDUs on its Alternate (blocking) port after `MaxAge` (20 seconds), assumes the Root Bridge is dead, transitions its blocking port to `Forwarding`, and creates a catastrophic Layer-2 bridging loop across the distribution block! '
        'To prevent unidirectional fiber loops, enterprise engineers enable **UDLD (Unidirectional Link Detection) Aggressive Mode** alongside **STP Loop Guard (`spanning-tree guard loop`)** or **Bridge Assurance**. '
        'When Loop Guard is enabled on a non-designated port and BPDUs stop arriving while the physical link stays `UP`, the switch places the port into **`loop-inconsistent` blocking state** instead of forwarding.</p>'
        '<p>Similarly, when engineers bundle four 10 Gbps links into a 40 Gbps **LACP (IEEE 802.3ad) Port-Channel** between a core switch and a backup server, they are often surprised when a single `scp` or `iperf3` stream never exceeds `10 Gbps`. '
        'LACP never round-robins individual packets of the same TCP flow across multiple physical member links (doing so would cause out-of-order TCP arrivals and severe SACK retransmission storms). '
        'Instead, the switch ASIC computes a deterministic XOR/CRC hash of the packet headers (**`src-dst-ip`** or **`src-dst-mixed-ip-port`**) and pins each 5-tuple flow to a single member link. '
        'Upgrading the switch load-balancing algorithm from `src-mac` to `src-dst-mixed-ip-port` (`port-channel load-balance src-dst-mixed-ip-port`) ensures multi-session traffic distributes evenly across all four 10G member links.</p>'
    ),
    (2, 2): (
        '<h4>Production Case Study 2.2: Native VLAN Hopping (Double Tagging), DTP Spoofing &amp; VTP Revision Bombs</h4>'
        '<p>Why do security frameworks require changing the 802.1Q **Native VLAN** from VLAN 1 to an unused quarantine VLAN (e.g., VLAN 999) and pruning it from user-facing trunks? '
        'If an attacker sits on an access port assigned to VLAN 1 while the upstream inter-switch trunk also uses VLAN 1 as its untagged Native VLAN, the attacker can craft a **double-tagged 802.1Q frame**: outer tag `VID = 1` (the Native VLAN) and inner tag `VID = 20` (the restricted Server VLAN). '
        'When the first switch receives the frame on the access port and forwards it out the trunk port, it sees outer `VID = 1` matches the trunk\'s Native VLAN, strips the outer 4-byte tag to send the frame "untagged," and inadvertently exposes the inner `VID = 20` tag on the wire! '
        'When the downstream switch receives that frame on its trunk port, it reads the exposed inner `VID = 20` tag and delivers the packet directly into the restricted Server VLAN (unidirectional VLAN hopping). '
        'Moving all access ports off VLAN 1, setting `switchport trunk native vlan 999` (with no hosts in VLAN 999), or forcing `vlan dot1q tag native` eliminates double-tagging completely.</p>'
        '<p>A second infamous Layer-2 outage is the **VLAN Trunking Protocol (VTP) Configuration Revision Bomb**. '
        'In VTP Server/Client mode, switches in the same VTP domain overwrite their entire `vlan.dat` database whenever they receive a VTP summary advertisement with a higher 32-bit Configuration Revision number—even from a lab switch pulled out of a storage closet whose revision number is `412` while the production core is at revision `85`! '
        'If that lab switch only has default VLAN 1 in its database, every production switch in the building immediately deletes VLANs 10, 20, 30, and 40, stranding every access port in an inactive VLAN. '
        'Best practice on N10-009 is to set **`vtp mode transparent`** (or `vtp mode off`), which forces switches to maintain independent local VLAN databases and sets the VTP revision number permanently to `0`.</p>'
    ),
    (2, 3): (
        '<h4>Production Case Study 2.3: NEXT/FEXT Crosstalk, Single-Mode vs Multimode Mismatch &amp; APC vs UPC Ferrules</h4>'
        '<p>When certifying newly pulled horizontal Cat6A runs with a Fluke DSX cable certifier, four physical metrics determine pass/fail: '
        '(1) **Wiremap** (detects opens, shorts, reversed pairs, crossed pairs, and **split pairs**—where one wire of Pair 1 is twisted with one wire of Pair 2, passing a cheap DC continuity tester while failing at 1 Gbps due to severe crosstalk); '
        '(2) **Insertion Loss (Attenuation)** (signal loss in dB over distance, worsened by excessive length >100 m or high ambient heat in plenum ceilings); '
        '(3) **Near-End Crosstalk (NEXT) and Alien Crosstalk (ANEXT)** (electromagnetic coupling between adjacent twisted pairs when a technician untwists more than 12.7 mm / 0.5 inch of jacket at the RJ-45 keystone termination); and '
        '(4) **Time-Domain Reflectometry (TDR)** length and distance-to-fault measurement (computed from the cable\'s Nominal Velocity of Propagation, `NVP ~ 0.65c`–`0.72c`).</p>'
        '<p>On optical fiber links, two physical mismatches cause immediate attenuation or back-reflection damage: '
        'First, patching a `9/125 µm` **Single-Mode (OS2, yellow jacket)** 1310 nm SFP+ into a `50/125 µm` **Multimode (OM4, aqua jacket)** plant—or vice versa—causes massive core-diameter coupling loss (>15 dB) or Differential Mode Delay. '
        'Second, mating a **Green APC (Angled Physical Contact, 8-degree angled ferrule)** connector with a **Blue UPC (Ultra Physical Contact, flat polished ferrule)** connector creates an air gap and crushes the glass ferrule tip, spiking **Optical Return Loss (ORL)** and insertion loss. Always match Blue-to-Blue (UPC) and Green-to-Green (APC), and inspect/clean every ferrule with an IEC 61300-3-35 fiber scope before insertion.</p>'
    ),
    (2, 4): (
        '<h4>Production Case Study 2.4: VoIP Desk Phone + PC Daisy-Chain Failure in a Wiring Closet</h4>'
        '<p>A user reports that after moving their desk, their PoE IP phone boots and registers to the call manager (`10.20.0.10` in Voice VLAN 20), yet the desktop PC plugged into the `PC` pass-through port on the back of the phone shows `Unidentified network (169.254.88.14)` and cannot reach the corporate network. '
        'Walking through the closet configuration on port `Gi0/15` exposes why the phone works while the PC fails: '
        'the switch port has `switchport voice vlan 20` and `power inline auto` configured, so the phone receives 802.3af power and learns via CDP/LLDP-MED to tag its own VoIP frames with `802.1Q VID 20`. '
        'However, the phone\'s internal 3-port switch bridges the desktop PC\'s frames **untagged** onto `Gi0/15`, and someone previously left `Gi0/15` configured with `switchport access vlan 999` (the quarantine VLAN) instead of `switchport access vlan 10`! '
        'Updating `switchport access vlan 10` on `Gi0/15` immediately places the untagged PC traffic into the Corporate Data VLAN without interrupting the active VoIP call on tagged VLAN 20.</p>'
    ),
}

NETOPS_CASE_STUDIES.update({
    (3, 1): (
        '<h4>Production Case Study 3.1: OSPF Reference Bandwidth on 10G/40G Links &amp; Floating Static Failover</h4>'
        '<p>By default, OSPFv2 (RFC 2328) calculates interface metric cost using the formula `Cost = Reference_Bandwidth / Interface_Bandwidth`, where the default `Reference_Bandwidth` is **100 Mbps (`10^8 bps`)** and integer division rounds any result below `1` up to `1`. '
        'Consequently, unless modified, OSPF assigns the exact same cost (`Cost = 1`) to a 100 Mbps FastEthernet link, a 1 Gbps GigabitEthernet link, a 10 Gbps SFP+ trunk, and a 100 Gbps QSFP28 spine link! '
        'In a campus where a legacy 100 Mbps microwave backup link parallels a 2-hop 10 Gbps fiber ring, default OSPF chooses the 1-hop 100 Mbps link (`Cost = 1`) over the 2-hop 10 Gbps fiber path (`Cost = 1 + 1 = 2`), saturating the microwave link and dropping traffic. '
        'To fix this across an enterprise OSPF domain, configure **`auto-cost reference-bandwidth 100000`** (100 Gbps in Mbps) under `router ospf 1` on EVERY router in the OSPF autonomous system, so a 100G link costs `1`, a 10G link costs `10`, a 1G link costs `100`, and a 100M link costs `1000`.</p>'
        '<p>When pairing OSPF with a backup LTE/5G cellular router at a retail branch, engineers configure a **Floating Static Default Route**: `ip route 0.0.0.0 0.0.0.0 192.0.2.1 210`. '
        'While the primary MPLS/IPsec OSPF adjacency is `FULL`, the OSPF default route (`O*E2 0.0.0.0/0`, AD `110`) wins RIB installation because `110 < 210`. '
        'The instant the primary tunnel drops and OSPF withdraws its `0.0.0.0/0` route, the router promotes the floating static route (AD `210`) into the FIB in milliseconds, and automatically reverts to OSPF as soon as the primary adjacency returns to `FULL`.</p>'
    ),
    (3, 2): (
        '<h4>Production Case Study 3.2: Dual-Homed eBGP Multihoming, Local Preference vs AS_PATH Prepending &amp; BFD</h4>'
        '<p>When an enterprise headquarters dual-homes to two independent Tier-1 Internet Service Providers (`ISP-A AS 65101` on a 10 Gbps fiber circuit and `ISP-B AS 65202` on a 1 Gbps backup circuit) using **eBGP (TCP 179, AD 20)**, engineers must control both **outbound traffic** (leaving the enterprise toward the Internet) and **inbound traffic** (returning from the Internet toward the enterprise\'s public `/24` prefix `203.0.113.0/24`). '
        'To steer **outbound traffic** onto `ISP-A`, set a higher BGP **Local Preference (`LOCAL_PREF`, default 100)** on routes learned from `ISP-A` (e.g., `set local-preference 200` inbound on the `ISP-A` peer). Because BGP evaluates `Weight` (Cisco local) and `LOCAL_PREF` (AS-wide) before `AS_PATH` length, all internal routers prefer `ISP-A` for outbound traffic. '
        'To steer **inbound return traffic** onto `ISP-A`, advertise `203.0.113.0/24` normally to `ISP-A` while applying **AS_PATH Prepending** outbound toward `ISP-B` (`set as-path prepend 65001 65001 65001`), making the path through `ISP-B` look three autonomous-system hops longer to the global Internet routing table.</p>'
        '<p>Because standard BGP Hold Timers default to `180 seconds` (`3 x 60s Keepalive`), a dark-fiber cut inside a metro carrier ring that does not drop the local electrical SFP link status (`up/up`) would black-hole traffic for up to 3 minutes. '
        'Binding **Bidirectional Forwarding Detection (BFD, RFC 5880, UDP 3784/3785)** to both eBGP and OSPF neighbors (`neighbor 198.51.100.1 fall-over bfd`) exchanges lightweight control packets every `50 ms` (`3 x 50 ms = 150 ms` detection multiplier), triggering BGP/OSPF failover in under 200 milliseconds.</p>'
    ),
    (3, 3): (
        '<h4>Production Case Study 3.3: 802.1X EAP-TLS Certificate Validation Failure &amp; Captive Portal DNS Hijacking</h4>'
        '<p>After an enterprise rotates the Intermediate CA certificate on its Microsoft NPS / FreeRADIUS cluster, Windows 11 and macOS laptops fail to connect to the `CORP-8021X` SSID, logging `EAP-TLS handshake failed: untrusted server root/intermediate certificate` while existing connected clients stay online until they roam. '
        'In **IEEE 802.1X (WPA2/WPA3-Enterprise)**, the wireless client (**Supplicant**) communicates over Layer-2 **EAPOL (EAP over LAN, EtherType `0x888E`)** with the Wireless LAN Controller (**Authenticator**), which encapsulates the EAP frames inside **RADIUS (`UDP 1812` or RadSec `TCP 2083`)** packets to the **Authentication Server**. '
        'During the TLS handshake inside EAP-TLS or PEAP, the client validates the RADIUS server\'s X.509 certificate chain against the **Trusted Root Certification Authorities** configured in its MDM/GPO 802.1X profile—and because the client has no IP address yet during Layer-2 802.1X authentication, it **cannot fetch missing intermediate certificates via AIA HTTP URLs or check online CRLs**! '
        'Therefore, the RADIUS server must present the complete certificate chain (Server Leaf + Issuing Intermediate CA), and the new Root/Intermediate thumbprints must be pushed via GPO/MDM *before* activating the new RADIUS certificate.</p>'
    ),
    (3, 4): (
        '<h4>Production Case Study 3.4: Warehouse VoIP Roaming Drops, Hidden Nodes &amp; Antenna Polarity</h4>'
        '<p>In a high-ceiling logistics warehouse with steel racking stacked 12 meters high, barcode scanners and VoIP handsets drop calls every time a forklift drives down an aisle. '
        'A post-deployment Ekahau heat-map survey reveals two flaws: first, ceiling-mounted omnidirectional APs were installed 14 meters above the floor (radiating horizontally into the top of steel racks rather than down the narrow aisles where directional patch/yagi aisle antennas belong); '
        'second, 5 GHz UNII-2 DFS channels (`52`–`144`) were enabled near a regional airport Doppler weather radar, causing APs to abruptly abandon their channel without client coordination whenever radar pulses hit. '
        'Replacing the ceiling omnis with directional aisle-aligned antennas, restricting voice SSIDs to non-DFS UNII-1 (`36, 40, 44, 48`) and UNII-3 (`149, 153, 157, 161`) 20 MHz channels, and enabling **802.11r Fast BSS Transition** with **802.11k Neighbor Reports** eliminated the roaming drops completely.</p>'
    ),
    (4, 1): (
        '<h4>Production Case Study 4.1: DHCP Starvation, Rogue DHCP MitM &amp; Option 82 Relay Drop</h4>'
        '<p>At 08:30 on Monday, 120 incoming employees in Building C receive `169.254.x.x` APIPA addresses, while a handful of laptops receive `192.168.1.x` leases with gateway `192.168.1.1` and lose access to all internal corporate servers. '
        'Investigating the closet switch reveals two simultaneous issues: an employee plugged the LAN port of a consumer home router into wall jack `Gi0/19` (acting as a rogue DHCP server answering `DHCPDISCOVER` broadcasts faster than the central Windows DHCP server two router hops away), AND a misconfigured test script on another port exhausted the `/24` corporate scope by sending spoofed random `chaddr` client MAC addresses (a **DHCP starvation attack**). '
        'Enabling `ip dhcp snooping` on VLAN 10 with only the distribution uplink (`Gi0/1`) marked `ip dhcp snooping trust` immediately drops all `DHCPOFFER`/`DHCPACK` packets from `Gi0/19`, while `switchport port-security maximum 2` and `ip dhcp snooping limit rate 15` stop the starvation script. '
        'Note one subtle interaction when enabling `ip dhcp snooping` on a Layer-2 access switch upstream of a Cisco IOS router `ip helper-address`: by default, IOS DHCP snooping inserts **DHCP Option 82 (Relay Agent Information)** with a `giaddr` of `0.0.0.0`, which causes an upstream IOS router relay to drop the packet unless you either run **`no ip dhcp snooping information option`** on the access switch or configure **`ip dhcp relay information trust-all`** on the router SVI.</p>'
    ),
    (4, 2): (
        '<h4>Production Case Study 4.2: Negative DNS Caching (SOA Minimum TTL), CNAME at Zone Apex &amp; Stale Active Directory SRV Records</h4>'
        '<p>An engineer deploys a new internal microservice at `api-v2.novak.internal` (`10.40.30.88`) and tests it from a jump box *before* creating the DNS `A` record. '
        'Two minutes later, the engineer adds `api-v2 IN A 10.40.30.88` to the authoritative zone, verifies it resolves on a second server, yet the first jump box continues returning `NXDOMAIN` for the next 15 minutes! '
        'Why? According to **RFC 2308 (DNS NCACHE)**, recursive resolvers cache `NXDOMAIN` and `NODATA` responses for the duration specified by the **Negative Caching TTL** (the last field of the zone\'s **SOA (Start of Authority)** record, often set to 900–3600 seconds). '
        'Until you flush the local stub cache (`ipconfig /flushdns` on Windows; `resolvectl flush-caches` on systemd Linux) and flush the recursive resolver cache (`rndc flushname api-v2.novak.internal`), the cached negative answer persists.</p>'
        '<p>Another frequent DNS outage occurs when a marketing team asks to place a **`CNAME` record at the zone apex (`@` / `novak.example`)** pointing to a cloud CDN hostname. '
        '**RFC 1034 / RFC 2181** strictly forbid a `CNAME` from coexisting with any other record type at the same owner name—and because the zone apex `@` *must* contain `SOA` and `NS` records (plus usually `MX` and `TXT` records), adding an apex `CNAME` breaks either zone authority or mail delivery! '
        'Use synthetic **`ALIAS` / `ANAME`** records or `HTTPS` / `SVCB` records (RFC 9460) at the zone apex instead.</p>'
    ),
    (4, 3): (
        '<h4>Production Case Study 4.3: Hairpin NAT (NAT Loopback), Overlapping Partner VPN Subnets &amp; Stateless vs Stateful ACLs</h4>'
        '<p>Suppose an enterprise hosts a customer portal in its DMZ (`172.16.10.25`) published to the Internet via static DNAT on public IP `203.0.113.25`. '
        'External customers connect to `https://portal.novak.example` (`203.0.113.25`) without issue, but when internal employees on VLAN 10 (`10.10.10.0/24`) resolve `portal.novak.example` via public DNS to `203.0.113.25`, their browser connections time out! '
        'When `10.10.10.45` sends a packet to `203.0.113.25`, the edge firewall translates the destination to `172.16.10.25` and forwards it to the DMZ server; however, if the source IP remains `10.10.10.45`, the DMZ server sees an internal RFC 1918 route and replies directly to `10.10.10.45:49200` from source IP `172.16.10.25:443`—bypassing the edge firewall! '
        'The client workstation (`10.10.10.45`) receives a `SYN-ACK` from `172.16.10.25` when it sent its `SYN` to `203.0.113.25`, so the client OS kernel drops the packet and sends a TCP `RST`. '
        'Cleanly solve this by deploying **Split-Horizon DNS** (so internal clients resolve `portal.novak.example` directly to `172.16.10.25`) or configuring **Hairpin NAT (U-Turn NAT)** on the firewall.</p>'
    ),
    (4, 4): (
        '<h4>Production Case Study 4.4: Post-Cutover Branch Outage — Tracing DHCP Option 3, DNS Option 6 &amp; NAT Pool Exhaustion</h4>'
        '<p>Following a weekend router replacement at Branch 12 (`10.12.0.0/23`), users report that half the office can browse internal and external sites normally, while the other half can reach internal printers (`10.12.0.50`) but cannot reach any other VLAN or the Internet. '
        'Inspecting `ipconfig /all` on an affected PC shows `IPv4 Address: 10.12.1.44`, `Subnet Mask: 255.255.255.0 (/24)`, `Default Gateway: 10.12.0.1`! '
        'Because the DHCP scope Option 1 (`Subnet Mask`) was accidentally typed as `255.255.255.0 (/24)` instead of `255.255.254.0 (/23)`, any client assigned an address in the upper half of the `/23` (`10.12.1.1`–`10.12.1.254`) believes its default gateway `10.12.0.1` sits on a *foreign* subnet and refuses to ARP for `10.12.0.1`! '
        'Correcting the DHCP scope mask to `255.255.254.0` and running `ipconfig /renew` immediately restores gateway reachability for all 510 usable hosts.</p>'
    ),
    (5, 1): (
        '<h4>Production Case Study 5.1: SPAN Port Oversubscription vs Network TAPs &amp; SNMPv3 Counter64 Wrap</h4>'
        '<p>To investigate intermittent microburst drops on two 10 Gbps distribution uplinks (`Gi1/0/1` and `Gi1/0/2`, each carrying 6 Gbps bidirectional traffic), a junior technician configures a local **SPAN (Switched Port Analyzer)** session mirroring `both` (Rx + Tx) of both 10G uplinks onto a single 10G IDS sensor port (`Gi1/0/48`: `monitor session 1 source interface Gi1/0/1 - 2 both` / `monitor session 1 destination interface Gi1/0/48`). '
        'Why does the IDS sensor report 60% packet loss while production users see none? '
        'Mirroring `Rx + Tx` across two 10 Gbps links running at 6 Gbps each attempts to funnel `24 Gbps` of mirrored frames into a single `10 Gbps` SPAN destination port (`Gi1/0/48`), causing massive SPAN egress queue drops—and furthermore, standard hardware switches strip corrupted CRC/FCS frames *before* copying them to a SPAN port! '
        'To capture wire-accurate timing and physical Layer-1 CRC errors at line rate without oversubscription, deploy a passive **Optical Network TAP** (which splits light 50/50 or 70/30 onto separate Rx and Tx capture fibers with zero delay and fails open on power loss) feeding a Packet Broker with hardware deduplication and header slicing.</p>'
    ),
    (5, 2): (
        '<h4>Production Case Study 5.2: AAA Lockout Prevention, Break-Glass Local Accounts &amp; NTP Stratum Drift</h4>'
        '<p>When migrating a campus switch fleet from local VTY passwords to centralized **TACACS+ (`TCP 49`)**, a single syntax mistake in `aaa authentication login default group tacacs+` (omitting the trailing **`local`** keyword) can lock administrators out of every switch in the enterprise the moment the WAN link to the TACACS+ server goes down! '
        'Always configure **`aaa authentication login default group tacacs+ local`** and **`aaa authentication enable default group tacacs+ enable`** so the switch falls back to the local `username netadmin privilege 15 algorithm-type scrypt secret ...` account only when the TACACS+ servers are unreachable (`DEAD` timeout, not when a user types a wrong password against a live TACACS+ server). '
        'Equally critical is **NTP Stratum hierarchy**: Stratum `0` is the atomic/GPS reference clock; Stratum `1` is the primary network time server directly attached to the GPS receiver via PPS serial; Stratum `2` servers sync from Stratum `1` over UDP 123; and Stratum `16` indicates an unsynchronized clock. '
        'If a switch\'s clock drifts by more than 5 minutes (default Kerberos `MaxTicketAge` skew tolerance) or outside an X.509 certificate\'s `notBefore`/`notAfter` validity window, both RadSec/TLS and AD-backed authentication fail immediately.</p>'
    ),
    (5, 3): (
        '<h4>Production Case Study 5.3: PCI-DSS Cardholder Data Environment (CDE) Isolation &amp; Jump-Box Bastion Controls</h4>'
        '<p>In a retail enterprise subject to PCI-DSS 4.0 compliance, point-of-sale (POS) terminals and payment processors must reside in a strictly isolated **Cardholder Data Environment (CDE) VLAN** where every inbound and outbound flow is default-denied by a stateful zone firewall, East-West terminal-to-terminal traffic is blocked via **Private VLAN (PVLAN) Isolated ports** (`switchport mode private-vlan host`), and administrative access is permitted solely through a hardened, MFA-enforced **Bastion Host / Jump Box** using ephemeral session certificates. '
        'Without PVLAN isolation or micro-segmentation, a single compromised POS terminal in VLAN 50 can ARP-scan and attack every other POS terminal in `10.50.0.0/24` without ever crossing the Layer-3 firewall gateway (`10.50.0.1`).</p>'
    ),
    (5, 4): (
        '<h4>Production Case Study 5.4: Remedying a Live ARP Poisoning / Responder Attack with Dynamic ARP Inspection (DAI)</h4>'
        '<p>A penetration tester on guest/contractor port `Gi0/18` launches an ARP spoofing (`ettercap` / `arpspoof`) and LLMNR/NBT-NS poisoning (`Responder`) attack, sending gratuitous ARP replies claiming that `10.10.10.1` (the VLAN 10 default gateway) is at the attacker\'s MAC address `00:11:22:33:44:55`. '
        'Why did `switchport port-security` alone fail to stop this attack? Because `port-security` only inspects the **Layer-2 Ethernet header Source MAC** (which matched the attacker\'s own legitimate NIC `00:11:22:33:44:55`); it does not inspect the **ARP payload (`Sender IP = 10.10.10.1`)**! '
        'Enabling **Dynamic ARP Inspection (`ip arp inspection vlan 10`)** intercepts every ARP packet on untrusted access ports, compares the ARP payload\'s `(Sender MAC, Sender IP)` pair against the trusted **DHCP Snooping Binding Database**, drops the forged ARP reply claiming `10.10.10.1`, logs `%SW_DAI-4-DHCP_SNOOPING_DENY`, and rate-limits the port (`ip arp inspection limit rate 15`) before the poisoning can reach a single victim cache.</p>'
    ),
})

NETOPS_CASE_STUDIES.update({
    (6, 1): (
        '<h4>Production Case Study 6.1: Intermittent Packet Loss — HSRP Active/Active Split-Brain vs Flapping SFP</h4>'
        '<p>Users on Floor 4 (`10.40.0.0/24`) report that every 3 to 5 seconds their SSH sessions freeze and ping to default gateway `10.40.0.1` drops 40% of packets, while pings between two workstations on Floor 4 (`10.40.0.21` to `10.40.0.22`) show 0.2 ms and 0% loss. '
        'Running `show standby brief` on both core distribution switches (`CORE-A` and `CORE-B`) reveals that **both switches list themselves as `Active` for HSRP Group 40 (`10.40.0.1`)**! '
        'Why did both switches become HSRP Active simultaneously? Because VLAN 40 was accidentally pruned from the inter-switch peer trunk connecting `CORE-A` and `CORE-B` (`switchport trunk allowed vlan` omitted `40`), preventing HSRP UDP 1985 multicast Hellos (`224.0.0.2` for HSRPv1 or `224.0.0.102` for HSRPv2) from crossing between the two cores! '
        'As a result, both switches continually advertise Virtual MAC `0000.0c9f.f028`, causing the access switch CAM table to flap Virtual MAC `0000.0c9f.f028` between Uplink 1 and Uplink 2 every few milliseconds. '
        'Adding VLAN 40 back to the inter-core trunk (`switchport trunk allowed vlan add 40`) immediately restores HSRP hello visibility and returns `CORE-B` to `Standby`.</p>'
    ),
    (6, 2): (
        '<h4>Production Case Study 6.2: Avoiding Multi-Variable Changes &amp; Managing Maintenance Window Risk</h4>'
        '<p>During a midnight outage where a branch site loses access to an cloud ERP application after a firewall upgrade, an stressed technician simultaneously (1) disables the WAN IPS signature engine, (2) lowers the tunnel MTU to 1350, (3) changes the branch DNS forwarder to `8.8.8.8`, and (4) reboots the branch router. '
        'Although the ERP site comes back online 4 minutes later, the team now faces three severe operational hazards: they do not know which of the four actions fixed the outage; disabling the IPS left the perimeter exposed; and pointing corporate clients to public DNS `8.8.8.8` broke internal Split-Horizon Active Directory resolution (`_ldap._tcp.dc._msdcs`) the next morning! '
        'Testing **one hypothesis at a time**, recording the exact metric before and after each single change, and reverting any test that does not resolve the symptom is the difference between engineering and guesswork.</p>'
    ),
    (6, 3): (
        '<h4>Production Case Study 6.3: Closing the Loop — CMDB, Rack Elevation, Cable Matrix &amp; Post-Incident Review</h4>'
        '<p>After resolving a fiber uplink failure by moving the closet trunk from damaged strand pair `F-01/02` on Patch Panel `MDF-LIU-A` to spare strand pair `F-05/06` and reconfiguring the core trunk port from `Te1/1/1` to `Te1/1/3`, the incident is NOT finished when pings succeed. '
        'If the engineer closes the ticket without updating the **Fiber Patch Matrix**, **Logical Topology Diagram**, **Port Description (`description UPLINK_TO_IDF3_SW1_GI0/1`)**, **Monitoring/SNMP Interface Thresholds**, and **NVRAM (`copy running-config startup-config`)**, the next technician servicing `MDF-LIU-A` will see `F-05/06` listed as "Spare/Unused" in the spreadsheet and unplug it during routine cable cleanup—causing a repeat outage! '
        'Always attach the `show archive config differences` output and updated cable/IPAM row IDs directly to the closure notes of the change or incident ticket.</p>'
    ),
    (6, 4): (
        '<h4>Production Case Study 6.4: End-to-End Multi-Site Outage — Correlating Syslog, NetFlow, OSPF &amp; Firewall State</h4>'
        '<p>In a company-wide severity-1 drill, users across three branch offices report that voice calls drop after 32 seconds and internal web apps time out, while local printing works. '
        'Correlating NTP-synchronized syslog messages across the WAN core reveals `%OSPF-5-ADJCHG: Process 1, Nbr 10.255.0.2 on Tunnel10 from FULL to DOWN, Neighbor Down: Dead timer expired` occurring every 3 minutes because a newly applied QoS policy-map starved OSPF IP Protocol 89 and BFD control packets during backup replication bursts! '
        'Adding a dedicated priority/control-plane class (`class-map match-any NETWORK_CONTROL` matching `protocol ospf`, `dscp cs6`, and `bfd`) with guaranteed bandwidth reservation immediately stabilized OSPF adjacencies and eliminated the 32-second SIP call drops.</p>'
    ),
    (9, 1): (
        '<h4>Hands-On CLI Deep Dive 9.1: Terminal Length, Pipe Filters (`include`, `section`, `begin`), and ROMMON Recovery</h4>'
        '<p>When inspecting multi-thousand-line enterprise configurations over a 9600-baud serial console or SSH session, mastering IOS output modifiers saves critical minutes during an outage: '
        '`show running-config | section router ospf` prints the entire OSPF configuration block; `show ip interface brief | exclude unassigned` hides unused ports; `show interfaces | include line protocol|CRC|drops` extracts physical health counters across all ports at once; and `terminal length 0` disables `--More--` pagination when capturing a full session log for a ticket attachment. '
        'If a switch or router boots to the `rommon 1>` or `switch:` recovery prompt (either because the Flash IOS image was corrupted or the configuration register was set to `0x2142` to bypass `startup-config` during password recovery), verify the image in flash (`dir flash:`), set `confreg 0x2102` so the router loads `startup-config` normally on boot, and issue `reset`.</p>'
    ),
    (9, 2): (
        '<h4>Hands-On CLI Deep Dive 9.2: Interface Range Macros, Voice + Data Access Ports &amp; VLAN Deletion Hazards</h4>'
        '<p>When provisioning 24 access ports in a closet, never configure ports one by one—use `interface range FastEthernet0/1 - 24` to apply identical `switchport mode access`, `switchport access vlan 10`, and `spanning-tree portfast` commands atomically. '
        'Beware of what happens when you delete a VLAN (`no vlan 20`) while access ports (`Fa0/5`–`Fa0/8`) are still assigned to VLAN 20: '
        'those ports do NOT automatically fall back to VLAN 1! Instead, they become **orphaned (`inactive`) ports** displayed under `show interfaces status` as `inactive` (amber LED), dropping all traffic until you either recreate `vlan 20` or reassign those interfaces to an active VLAN with `switchport access vlan 10`.</p>'
    ),
    (9, 3): (
        '<h4>Hands-On CLI Deep Dive 9.3: Diagnosing Secondary IP Addresses, Loopback0 Interfaces &amp; ARP Timeout Tuning</h4>'
        '<p>In addition to physical routed interfaces (`Gi0/0`, `Gi0/1`), enterprise routers always configure at least one logical **`interface Loopback0`** with a `/32` host mask (`ip address 10.255.255.1 255.255.255.255`). '
        'Why? Because a physical interface goes `down/down` if its single cable or SFP fails, whereas a Loopback interface is pure software and remains **`up/up` as long as the router chassis has power**! '
        'Using `Loopback0` as the **OSPF Router-ID (`router-id 10.255.255.1`)**, the **iBGP update-source (`neighbor X update-source Loopback0`)**, the **SNMP trap source**, and the **SSH/TACACS+ source interface** ensures that management sessions and BGP peerings survive any single physical link failure as long as an alternate OSPF path exists.</p>'
    ),
    (9, 4): (
        '<h4>Hands-On CLI Deep Dive 9.4: Subinterface Native VLAN Alignment &amp; Troubleshooting One-Way Inter-VLAN Routing</h4>'
        '<p>When a host in VLAN 10 (`10.10.10.25/24`, gateway `10.10.10.1`) can ping its own router subinterface `10.10.10.1` AND can even ping the router\'s VLAN 20 subinterface `10.10.20.1`, yet **cannot ping Server `10.10.20.50` in VLAN 20**, why does pinging `10.10.20.1` succeed while pinging `10.10.20.50` fails? '
        'Because `10.10.20.1` is an IP address owned by the router itself—the router answers that ping in its own control plane without ever transmitting a frame out onto VLAN 20! '
        'When the router tries to forward a packet to `10.10.20.50`, three things can still fail downstream: (1) VLAN 20 might be missing from the switch trunk or access port for `10.10.20.50`; (2) Server `10.10.20.50` might have a missing or wrong default gateway (`10.10.20.254` instead of `10.10.20.1`), so it receives the Echo Request from `10.10.10.25` and cannot route the Echo Reply back; or (3) Windows Firewall on `10.10.20.50` allows ICMP Echo only from `LocalSubnet` (`10.10.20.0/24`) and drops pings from remote subnet `10.10.10.0/24`.</p>'
    ),
    (9, 5): (
        '<h4>Hands-On CLI Deep Dive 9.5: Recursive Static Routes vs Exit-Interface Static Routes &amp; Proxy ARP</h4>'
        '<p>On multi-access Ethernet segments, always configure static routes using an explicit **next-hop IP address (`ip route 10.50.0.0 255.255.255.0 172.16.12.2`)** or a **fully specified static route (`ip route 10.50.0.0 255.255.255.0 GigabitEthernet0/1 172.16.12.2`)** rather than pointing solely to an Ethernet exit interface (`ip route 10.50.0.0 255.255.255.0 GigabitEthernet0/1`). '
        'Why? Pointing a static route solely to a broadcast Ethernet interface makes the router believe the entire remote subnet (`10.50.0.0/24`) is directly attached to `Gi0/1`, forcing the router to send an ARP broadcast for every single destination host IP in `10.50.0.0/24` (relying on the downstream router having Proxy ARP enabled and bloating the ARP table). '
        'Using a fully specified static route (`Gi0/1 172.16.12.2`) resolves the next-hop MAC once for `172.16.12.2` and avoids recursive RIB lookups.</p>'
    ),
    (9, 6): (
        '<h4>Hands-On CLI Deep Dive 9.6: Automated Configuration Archival, Rollback Timers &amp; Pre-Reload Sanity Checks</h4>'
        '<p>Before issuing `reload` on a remote router or switch, always run a three-step pre-flight verification: '
        '(1) `show archive config differences nvram:startup-config system:running-config` to verify zero unsaved lines remain between RAM and NVRAM; '
        '(2) `show boot` and `dir flash:` to confirm the boot variable points to an existing, non-corrupted IOS image file in Flash; and '
        '(3) `show version | include Configuration register` to confirm the configuration register is set to **`0x2102`** (not `0x2142`, which would wipe the active configuration on reboot by ignoring `startup-config`). '
        'When making risky remote ACL or routing changes over an in-band WAN link without OOB console access, schedule a fail-safe reload first (`reload in 10 reason "WAN ACL cutover safety net"`), apply the change, verify connectivity, save configuration, and cancel the timer (`reload cancel`).</p>'
    ),
})

NETOPS_FIELD_DRILLS = {
    (1, 1): (
        '<h4>N10-009 Packet Dissection &amp; Multi-Vendor CLI Comparison Drill (Lesson 1.1)</h4>'
        '<p>When examining a packet capture in Wireshark or `tcpdump`, every byte of the frame header maps to a deterministic operational behavior across Cisco IOS XE, Linux `iproute2`, and Windows PowerShell:</p>'
        + _tbl(
            ['Header / Field', 'Bit/Byte Offset', 'Normal Value / State', 'Failure Signature in Wireshark / CLI', 'Exact Diagnostic Command'],
            [
                ['Ethernet Preamble &amp; SFD', '7B + 1B (0xAB)', 'Alternating 10101010 + 10101011', 'Frame alignment / symbol error on NIC PHY', 'ethtool -S eth0 | egrep "align|symbol|crc"'],
                ['Destination / Source MAC', 'Bytes 0–5 / 6–11', '6-byte OUI (first 24b) + 24b NIC ID', 'Source MAC flapping or broadcast FF:FF:FF:FF:FF:FF storm', 'show mac address-table dynamic vlan 10'],
                ['EtherType / 802.1Q TPID', 'Bytes 12–13', '0x0800 IPv4, 0x86DD IPv6, 0x8100 VLAN', 'Unknown protocol drop or native VLAN mismatch', 'tcpdump -enni eth0 -vvv -c 5'],
                ['IPv4 DSCP / ECN (ToS)', 'IPv4 Byte 1', 'EF (46) Voice, AF41 (34) Video, CS0 (0)', 'QoS remarking stripped at WAN edge -> VoIP jitter', 'ping -Q 0xb8 10.20.30.1 (EF DSCP 46 = ToS 0xb8)'],
                ['IPv4 TTL / IPv6 Hop Limit', 'IPv4 Byte 8 / IPv6 Byte 7', '64 (Linux/macOS), 128 (Windows), 255 (IOS)', 'ICMP Time Exceeded (Type 11 Code 0) in routing loop', 'traceroute -n -q 1 10.40.10.25'],
                ['TCP Flags Byte', 'TCP Byte 13', 'SYN(0x02), ACK(0x10), FIN(0x01), RST(0x04)', 'Repeated SYN retransmissions or immediate RST/ACK', 'tcpdump -ni eth0 "tcp[tcpflags] & (tcp-syn|tcp-rst) != 0"'],
            ]
        )
        + '<p><strong>Field Verification Exercise:</strong> On a Linux jump host, run `ip -s link show dev eth0` to inspect Layer-1/Layer-2 `RX: bytes packets errors dropped Missed` and `TX: bytes packets errors dropped carrier collsns`; then run `ip route get 10.40.10.25` to verify the exact egress interface, source IP, and next-hop gateway selected by the kernel FIB before transmitting a single packet.</p>'
    ),
    (1, 2): (
        '<h4>N10-009 Subnet Binary Conversion &amp; IPv6 Multicast Scope Drill (Lesson 1.2)</h4>'
        '<p>Mastering rapid binary-to-decimal positional weights (`128, 64, 32, 16, 8, 4, 2, 1`) and prefix mask sums (`128, 192, 224, 240, 248, 252, 254, 255`) lets you solve any subnetting or ACL wildcard question in under 15 seconds without a calculator:</p>'
        + _tbl(
            ['IPv6 Address / Multicast Group', 'Prefix / Scope', 'IPv4 Equivalent Concept', 'Protocol Consumer &amp; Operational Purpose'],
            [
                ['::/128 &amp; ::1/128', 'Unspecified &amp; Loopback', '0.0.0.0 &amp; 127.0.0.1', 'Source address during DAD (::) and local host TCP/IP stack test (::1)'],
                ['2000::/3 (e.g., 2001:db8::/32)', 'Global Unicast (GUA)', 'Public routable IPv4 (2001:db8 = RFC 3849 doc)', 'End-to-end Internet routable addressing without NAT'],
                ['fe80::/10 (interface fe80::/64)', 'Link-Local Unicast', '169.254.0.0/16 APIPA (but mandatory in IPv6)', 'Used as next-hop address for OSPFv3, BGP, and ICMPv6 RA default gateway'],
                ['fc00::/7 (fd00::/8 locally assigned)', 'Unique Local (ULA)', 'RFC 1918 (10/8, 172.16/12, 192.168/16)', 'Internal multi-site private IPv6 addressing with 40-bit random Global ID'],
                ['ff02::1 &amp; ff02::2', 'Link-Local Multicast', '224.0.0.1 (All Hosts) &amp; 224.0.0.2 (All Routers)', 'Replaces broadcast: RA targets ff02::1; Host RS targets ff02::2'],
                ['ff02::5, ff02::6, ff02::1:2', 'Link-Local Multicast', '224.0.0.5/.6 (OSPF) &amp; UDP 67 Broadcast (DHCP)', 'OSPFv3 All-SPF-Routers (::5), DR/BDR (::6), and DHCPv6 Relay/Servers (::1:2)'],
                ['ff02::1:ff00:0/104', 'Solicited-Node Multicast', 'ARP Broadcast FF:FF:FF:FF:FF:FF', 'Appends low 24 bits of unicast IPv6 for targeted NDP MAC resolution &amp; DAD'],
            ]
        )
        + '<p><strong>Field Verification Exercise:</strong> Given host `10.144.219.100/20`, identify the network ID, first usable host, last usable host, and directed broadcast: `/20` lies in the 3rd octet (`20 = 16 + 4` bits, so mask is `255.255.240.0` and block size in the 3rd octet is `2^(8-4) = 16`). Multiples of 16 in the 3rd octet are `192, 208, 224`. Because `219` falls between `208` and `224`, the network address is `10.144.208.0/20`, first usable host is `10.144.208.1`, last usable host is `10.144.223.254`, and broadcast address is `10.144.223.255` (`4,094` usable hosts).</p>'
    ),
    (1, 3): (
        '<h4>N10-009 Transport Protocol Header &amp; Service Port Verification Drill (Lesson 1.3)</h4>'
        '<p>When auditing firewall rules or diagnosing service failures, engineers must distinguish connection-oriented TCP handshakes from connectionless UDP datagrams and know which diagnostic flag tests each transport mode (`nc -zv` vs `nc -zvu`, `nmap -sT/-sS` vs `nmap -sU`, `Test-NetConnection`):</p>'
        + _tbl(
            ['Service Category', 'Unencrypted Port (Legacy)', 'Encrypted Port (Modern Baseline)', 'Verification Command &amp; Expected Response'],
            [
                ['Remote CLI / File Transfer', 'Telnet TCP 23 / FTP TCP 20,21 / TFTP UDP 69', 'SSH / SCP / SFTP TCP 22; FTPS TCP 989/990', 'ssh -vvv admin@10.10.10.1 (Server banner SSH-2.0-Cisco)'],
                ['Directory &amp; Identity AAA', 'LDAP TCP/UDP 389; RADIUS UDP 1812/1813', 'LDAPS TCP 636; Kerberos TCP/UDP 88; TACACS+ TCP 49; RadSec TCP 2083', 'openssl s_client -connect dc01.novak.internal:636'],
                ['Mail Transfer &amp; Retrieval', 'SMTP TCP 25; POP3 TCP 110; IMAP4 TCP 143', 'SMTP Submission TCP 587 (STARTTLS) / 465; IMAPS TCP 993; POP3S TCP 995', 'openssl s_client -starttls smtp -connect mail.novak.internal:587'],
                ['Web, VoIP &amp; Remote Desktop', 'HTTP TCP 80; SIP UDP/TCP 5060', 'HTTPS TCP 443; HTTP/3 UDP 443; SIPS TCP 5061; RDP TCP/UDP 3389', 'curl -Iv --http2 https://portal.novak.internal:443'],
                ['Network Infrastructure', 'NTP UDP 123; SNMPv1/v2c UDP 161/162; Syslog UDP 514', 'NTS (RFC 8915); SNMPv3 authPriv UDP 161/162; Syslog-TLS TCP 6514', 'snmpwalk -v3 -l authPriv -u poller01 -a SHA -APass1 -x AES -XPass2 10.10.10.1'],
            ]
        )
    ),
    (1, 4): (
        '<h4>N10-009 Capstone Layer-Isolation Command Reference Matrix (Lesson 1.4)</h4>'
        '<p>Use this cross-platform command matrix during timed N10-009 troubleshooting scenarios to prove or exonerate each layer without guesswork:</p>'
        + _tbl(
            ['OSI Layer', 'Linux (iproute2 / bind9 / netcat)', 'Windows 11 / Server PowerShell', 'Cisco IOS XE Switch / Router CLI'],
            [
                ['L1 Physical', 'ethtool eth0; ip -s link show dev eth0', 'Get-NetAdapter | Select Name,Status,LinkSpeed,FullDuplex', 'show interfaces status; show interfaces Gi0/1 transceiver detail'],
                ['L2 Data Link', 'ip neigh show; bridge fdb show', 'Get-NetNeighbor; arp -a', 'show mac address-table; show vlan brief; show interfaces trunk'],
                ['L3 Network', 'ip -4 addr; ip -6 route; ping -M do -s 1472; mtr -n', 'Get-NetIPConfiguration; Get-NetRoute; Test-Connection', 'show ip interface brief; show ip route; show ip ospf neighbor'],
                ['L4 Transport', 'ss -tulnp; nc -zv 10.20.30.10 443; tcpdump -ni eth0', 'Get-NetTCPConnection; Test-NetConnection -Port 443', 'show ip access-lists; show ip nat translations; show tcp brief'],
                ['L7 Application', 'dig @10.100.10.53 host A +trace; curl -Iv https://host', 'Resolve-DnsName host -Server 10.100.10.53; Invoke-WebRequest', 'show ntp status; show logging; show dhcp lease'],
            ]
        )
    ),
    (2, 1): (
        '<h4>N10-009 Switching, STP Path Cost &amp; EtherChannel Negotiation Matrix (Lesson 2.1)</h4>'
        '<p>When auditing multi-switch topologies, verify IEEE 802.1D vs 802.1w port costs and channel bundling modes so redundant links never form a bridging loop or fail to bundle due to mismatched EtherChannel protocols:</p>'
        + _tbl(
            ['Link Speed', '802.1D Short Path Cost', '802.1w Long Path Cost', 'LACP (802.3ad) Mode Matrix', 'PAgP (Cisco Proprietary) Mode Matrix'],
            [
                ['10 Mbps', '100', '2,000,000', 'Active + Active = BUNDLES (LACP)', 'Desirable + Desirable = BUNDLES (PAgP)'],
                ['100 Mbps', '19', '200,000', 'Active + Passive = BUNDLES (LACP)', 'Desirable + Auto = BUNDLES (PAgP)'],
                ['1 Gbps', '4', '20,000', 'Passive + Passive = NO BUNDLE (Both wait)', 'Auto + Auto = NO BUNDLE (Both wait)'],
                ['10 Gbps', '2', '2,000', 'On + On = Static (No LACPDU health check)', 'On + Active/Desirable = NO BUNDLE (Loop/Err-disable)'],
                ['40G / 100 Gbps', '1', '500 / 200', 'Match Speed, Duplex, Native/Allowed VLANs, STP', 'Never mix LACP and PAgP across ends of a link'],
            ]
        )
    ),
    (2, 2): (
        '<h4>N10-009 802.1Q Trunking, DTP Negotiation &amp; Inter-VLAN Diagnostic Matrix (Lesson 2.2)</h4>'
        '<p>Before closing any VLAN or trunk ticket, verify that both ends of every inter-switch link agree on trunking mode, Native VLAN ID, Allowed VLAN list, and local active VLAN state:</p>'
        + _tbl(
            ['Switch A Mode', 'Switch B Mode', 'Resulting Operational State', 'Security &amp; Production Recommendation'],
            [
                ['Trunk (on)', 'Trunk (on) + switchport nonegotiate', 'Unconditional 802.1Q Trunk (No DTP frames)', 'BEST PRACTICE for all enterprise inter-switch/router trunks'],
                ['Dynamic Desirable', 'Dynamic Desirable or Dynamic Auto', 'Negotiates Trunk via DTP (01:00:0c:cc:cc:cc)', 'AVOID in production; vulnerable to DTP trunk spoofing'],
                ['Dynamic Auto', 'Dynamic Auto', 'Remains Static Access Port (Neither side initiates)', 'Common misconfiguration when admins leave defaults'],
                ['Access (on)', 'Trunk (on)', 'Mismatched mode: traffic drops / native VLAN leak', 'Immediate outage; verify with show interfaces switchport'],
            ]
        )
    ),
    (2, 3): (
        '<h4>N10-009 Structured Cabling, TIA-568A/B Pinouts, PoE Classes &amp; Fiber Connector Reference (Lesson 2.3)</h4>'
        '<p>Technician exams and field installations test exact TIA-568A vs TIA-568B RJ-45 pin positions, IEEE 802.3 PoE power budgets, and optical transceiver form factors:</p>'
        + _tbl(
            ['Pin / Standard', 'TIA-568A Wire Color', 'TIA-568B Wire Color', 'PoE Standard &amp; IEEE Class', 'Max Power at PSE Port / PD Device'],
            [
                ['Pin 1 / Pin 2', 'White/Green / Green (Pair 3)', 'White/Orange / Orange (Pair 2)', 'IEEE 802.3af (PoE Type 1, Class 0–3)', '15.4 W at PSE / 12.95 W at PD (VoIP Phone)'],
                ['Pin 3 / Pin 6', 'White/Orange / Orange (Pair 2)', 'White/Green / Green (Pair 3)', 'IEEE 802.3at (PoE+ Type 2, Class 4)', '30.0 W at PSE / 25.5 W at PD (Dual-band AP, PTZ Cam)'],
                ['Pin 4 / Pin 5', 'Blue / White/Blue (Pair 1)', 'Blue / White/Blue (Pair 1)', 'IEEE 802.3bt (PoE++ Type 3, Class 5–6)', '60.0 W at PSE / 51.0 W at PD (Wi-Fi 6E/7 AP, Thin Client)'],
                ['Pin 7 / Pin 8', 'White/Brown / Brown (Pair 4)', 'White/Brown / Brown (Pair 4)', 'IEEE 802.3bt (PoE++ Type 4, Class 7–8)', '90–100 W at PSE / 71.3 W at PD (LED lighting, Pan-Tilt-Zoom)'],
            ]
        )
    ),
    (2, 4): (
        '<h4>N10-009 Closet Isolation Step-by-Step Field Checklist (Lesson 2.4)</h4>'
        '<p>When dispatched to an IDF wiring closet for a single-user or single-room outage, execute these six deterministic checks in order:</p>'
        '<ol>'
        '<li><strong>Verify Physical Patch &amp; Toning:</strong> Match wall faceplate label (`IDF2-B14`) to patch panel port `14` and trace the patch cord to switch port `Gi1/0/14`. If unlabelled, attach a tone generator at the desk jack and sweep the 110 patch panel with an inductive amplifier probe (for copper) or inject a 650 nm red Visual Fault Locator (VFL) laser (for fiber).</li>'
        '<li><strong>Check Err-Disable &amp; Link State:</strong> Run `show interfaces Gi1/0/14 status` and `show interfaces status err-disabled`. Identify whether the port is `notconnect`, `disabled` (`shutdown`), or `err-disabled` (`bpduguard`, `psecure-violation`, `arp-inspection`, `dhcp-rate-limit`, `udld`).</li>'
        '<li><strong>Inspect Cable Diagnostics (Hardware TDR):</strong> Run `test cable-diagnostics tdr interface Gi1/0/14` followed by `show cable-diagnostics tdr interface Gi1/0/14` to confirm all four twisted pairs (`Pair A, B, C, D`) show `Normal` termination at matching meter length (`+/- 2 m`).</li>'
        '<li><strong>Verify PoE Allocation:</strong> Run `show power inline Gi1/0/14` to confirm powered devices receive requested class wattage without `Imax` or budget fault.</li>'
        '<li><strong>Audit VLAN &amp; MAC Learning:</strong> Run `show interfaces Gi1/0/14 switchport` and `show mac address-table interface Gi1/0/14` to verify the client MAC is learned in the expected Data/Voice VLAN.</li>'
        '<li><strong>Verify Trunk Path to Default Gateway:</strong> Run `show interfaces trunk` to confirm the user\'s VLAN is `allowed and active` on the closet uplink to the distribution core.</li>'
        '</ol>'
    ),
    (3, 1): (
        '<h4>N10-009 Dynamic Routing Protocol Comparison &amp; OSPF Area Types Reference (Lesson 3.1)</h4>'
        '<p>Enterprise network architects scale OSPF and BGP by partitioning topologies into hierarchical areas and autonomous systems:</p>'
        + _tbl(
            ['OSPF Router Role / Area Type', 'LSA Types Permitted', 'Routing Table Behavior &amp; Architectural Purpose'],
            [
                ['Internal Router / Area 0 (Backbone)', 'LSA 1 (Router), LSA 2 (Network), LSA 3 (Summary), LSA 5 (External)', 'Carries full inter-area and autonomous-system external topology; all areas must connect to Area 0'],
                ['Area Border Router (ABR)', 'Originates LSA 3 Summary routes between Area 0 and non-backbone areas', 'Summarizes prefixes (area X range) and isolates SPF recalculations to a single area'],
                ['Autonomous System Boundary Router (ASBR)', 'Originates LSA 5 (or LSA 7 in NSSA) for redistributed external routes', 'Redistributes eBGP, EIGRP, or static WAN routes into OSPF (E1 adds internal cost; E2 keeps fixed metric)'],
                ['Stub Area / Totally Stubby Area', 'Blocks LSA 5 External (Totally Stubby also blocks LSA 3 Inter-Area)', 'ABR injects a single 0.0.0.0/0 default summary route into branch routers with small memory'],
                ['Not-So-Stubby Area (NSSA)', 'Blocks LSA 5 but allows local ASBR via Type 7 LSAs (converted to LSA 5 at ABR)', 'Used when a stub branch also has a local partner or ISP connection needing redistribution'],
            ]
        )
    ),
    (3, 2): (
        '<h4>N10-009 Enterprise WAN Architecture, Cloud Direct Connect &amp; SD-WAN Underlay Matrix (Lesson 3.2)</h4>'
        '<p>Modern hybrid-cloud WANs combine private carrier circuits (MPLS, Metro-E, Wavelength DWDM), public broadband/DIA, cellular 5G/LTE, and LEO satellite (Starlink) under a unified SD-WAN control plane:</p>'
        + _tbl(
            ['Transport / Handoff', 'Typical Latency &amp; Jitter', 'Primary Enterprise Role &amp; Redundancy Pairing'],
            [
                ['Dedicated Dark Fiber / DWDM Wavelength', '<1–3 ms metro / <0.2 ms jitter', 'Data center interconnect (DCI), synchronous storage replication, 10G–400G optical'],
                ['MPLS Layer-3 VPN / Metro Ethernet', '5–25 ms regional / <2 ms jitter', 'Mission-critical voice/video (DSCP EF honored end-to-end by provider PE routers)'],
                ['Dedicated Internet Access (DIA Fiber)', '5–35 ms / SLA backed', 'Primary SD-WAN IPsec transport &amp; direct-to-cloud SaaS/SSE breakout'],
                ['5G Fixed Wireless / LTE WWAN', '18–45 ms / variable jitter', 'Diverse physical-path failover (survives backhoe trench cut that severs conduit fiber)'],
                ['Cloud Direct Connect / ExpressRoute', '1–10 ms from colocation cage', 'Private BGP peering (VLAN 802.1Q + BGP + BFD) into AWS VPC / Azure VNet'],
            ]
        )
    ),
    (3, 3): (
        '<h4>N10-009 IEEE 802.11 Standards Evolution, Frequency Bands &amp; WPA3 Security Matrix (Lesson 3.3)</h4>'
        '<p>Compare the physical-layer modulation, channel widths, spatial streams, and cryptographic suites across Wi-Fi generations:</p>'
        + _tbl(
            ['IEEE Standard', 'Wi-Fi Generation', 'Frequency Bands', 'Max Channel Width &amp; MIMO/Modulation', 'Security Suite &amp; Management Frame Protection'],
            [
                ['802.11n', 'Wi-Fi 4', '2.4 GHz &amp; 5 GHz', '20 / 40 MHz; up to 4x4 MIMO (64-QAM, 600 Mbps)', 'WPA2-PSK / Enterprise (AES-CCMP); 802.11w PMF optional'],
                ['802.11ac', 'Wi-Fi 5', '5 GHz only', '20/40/80/160 MHz; 8x8 Downlink MU-MIMO (256-QAM)', 'WPA2-AES-CCMP; beamforming via explicit sounding'],
                ['802.11ax', 'Wi-Fi 6 / Wi-Fi 6E', '2.4, 5 &amp; 6 GHz (6E)', '20–160 MHz; UL/DL OFDMA + 8x8 MU-MIMO (1024-QAM)', 'WPA3-Personal (SAE Dragonfly) / WPA3-Enterprise; 802.11w PMF mandatory on 6 GHz'],
                ['802.11be', 'Wi-Fi 7', '2.4, 5 &amp; 6 GHz', 'Up to 320 MHz + Multi-Link Operation (MLO, 4096-QAM)', 'WPA3 + GCMP-256; OWE (Opportunistic Wireless Encryption) for open guest networks'],
            ]
        )
    ),
    (3, 4): (
        '<h4>N10-009 RF Math, Antenna Radiation Patterns &amp; Site Survey Checklist (Lesson 3.4)</h4>'
        '<p>When designing or troubleshooting outdoor point-to-point bridges and indoor high-density venues, calculate **Effective Isotropic Radiated Power (`EIRP`)** accurately: `EIRP (dBm) = Tx Power (dBm) - Cable/Connector Loss (dB) + Antenna Gain (dBi)`. '
        'For example, a `17 dBm` (`50 mW`) radio feeding `3 dB` of coaxial pigtail loss into a `12 dBi` directional patch antenna produces `EIRP = 17 - 3 + 12 = 26 dBm` (`400 mW`). '
        'On long outdoor point-to-point wireless bridges, ensure at least **60% of the first Fresnel Zone** (the elliptical RF volume between transmitter and receiver antennas) remains clear of trees, rooftops, and metal structures to prevent phase-canceling multipath reflections.</p>'
    ),
}

NETOPS_FIELD_DRILLS.update({
    (4, 1): (
        '<h4>N10-009 DHCPv4 vs DHCPv6 Packet Exchange &amp; Lease Renewal Timeline Reference (Lesson 4.1)</h4>'
        '<p>Compare IPv4 broadcast lease lifecycle mechanics with IPv6 multicast SLAAC and Stateful/Stateless DHCPv6:</p>'
        + _tbl(
            ['Lifecycle Stage', 'DHCPv4 (UDP 67/68)', 'DHCPv6 (UDP 546/547, RFC 8415)', 'Address / Scope &amp; Relay Behavior'],
            [
                [' Step 1 Solicitation', 'DHCPDISCOVER (0.0.0.0 -> 255.255.255.255)', 'SOLICIT (fe80::client -> ff02::1:2)', 'Relay sets giaddr (IPv4) or wraps Relay-Forward (IPv6)'],
                ['Step 2 Offer / Adv', 'DHCPOFFER (Server offers IP + Options)', 'ADVERTISE (Server offers IA_NA + DNS)', 'Client may receive multiple offers; selects first/best'],
                ['Step 3 Request', 'DHCPREQUEST (Broadcasts chosen Server ID)', 'REQUEST (Requests offered lease/options)', 'Broadcast in IPv4 notifies unchosen servers to release offer'],
                ['Step 4 Commit / Ack', 'DHCPACK (or DHCPNAK if scope changed)', 'REPLY (Confirms lease + T1/T2 timers)', 'Client runs gratuitous ARP (IPv4) or ICMPv6 DAD NS (IPv6)'],
                ['T1 (50%) / T2 (87.5%)', 'Unicast DHCPREQUEST at T1; Broadcast at T2', 'RENEW at T1 (50%); REBIND at T2 (80%)', 'If server unreachable past 100% lease, client drops IP -> APIPA'],
            ]
        )
    ),
    (4, 2): (
        '<h4>N10-009 Enterprise DNS Architecture, SOA Serial Timers &amp; Query Diagnostic Drill (Lesson 4.2)</h4>'
        '<p>Every authoritative DNS zone begins with an **SOA (Start of Authority)** record containing seven operational fields that govern zone transfers (`AXFR` / `IXFR` over TCP 53) and negative caching:</p>'
        + _tbl(
            ['SOA Field / DNS Flag', 'Example Value', 'Operational Meaning &amp; Troubleshooting Significance'],
            [
                ['MNAME &amp; RNAME', 'ns1.novak.internal. hostmaster.novak.internal.', 'Primary authoritative server FQDN and admin email (@ replaced by .)'],
                ['Serial Number', '2026102601 (YYYYMMDDnn)', 'MUST be incremented after manual zone file edits or secondary NS ignores update!'],
                ['Refresh / Retry', '3600s (1 hr) / 600s (10 min)', 'How often secondary NS polls primary SOA serial, and retry interval on failure'],
                ['Expire', '604800s (7 days)', 'When secondary NS stops answering authoritatively if primary remains unreachable'],
                ['Minimum (Negative TTL)', '900s (15 min, RFC 2308)', 'How long recursive resolvers cache NXDOMAIN / NODATA negative responses'],
            ]
        )
    ),
    (4, 3): (
        '<h4>N10-009 NAT Terminology Matrix &amp; Wildcard Mask Calculation Drill (Lesson 4.3)</h4>'
        '<p>Master the four Cisco/CompTIA NAT perspective definitions and rapid wildcard mask inversion (`255.255.255.255 - Subnet_Mask = Wildcard_Mask`):</p>'
        + _tbl(
            ['NAT Address Term', 'Location of Host', 'Address Space Perspective', 'Example in Enterprise PAT / DMZ Topology'],
            [
                ['Inside Local', 'Inside corporate network', 'Private RFC 1918 IP before translation', 'Workstation 10.20.30.45 or DMZ server 172.16.10.5'],
                ['Inside Global', 'Inside corporate network', 'Public routable IP seen by outside world', 'Enterprise WAN PAT IP 203.0.113.5'],
                ['Outside Global', 'Outside (Internet / Partner)', 'Public routable IP assigned to remote host', 'Cloud server 198.51.100.20'],
                ['Outside Local', 'Outside (Internet / Partner)', 'How inside hosts see remote IP (usually = Outside Global)', '198.51.100.20 (or translated RFC 1918 in overlapping VPN NAT)'],
            ]
        )
    ),
    (4, 4): (
        '<h4>N10-009 Core Network Services Triage Decision Tree (Lesson 4.4)</h4>'
        '<p>When triaging multi-service outages across DHCP, DNS, NTP, and NAT, verify dependencies in strict bottom-up service order: '
        '**Step 1 (IP Configuration):** Check `ipconfig /all` or `ip addr`—if `169.254.x.x` is present, stop and fix VLAN/DHCP/Helper before touching DNS or NAT. '
        '**Step 2 (Local Gateway):** Ping the configured Default Gateway IP—if unreachable or experiencing 50% packet loss, check ARP (`arp -a`), VLAN tagging, or FHRP (HSRP/VRRP) state. '
        '**Step 3 (Remote IP &amp; NAT):** Ping an external IP literal (`1.1.1.1`) and trace the route (`traceroute -n 1.1.1.1`)—if hops stop at the perimeter router, inspect the default route (`show ip route 0.0.0.0`) and PAT translation table (`show ip nat translations`). '
        '**Step 4 (Name Resolution):** Query the configured DNS server directly (`dig @10.100.10.53 www.example.com`)—if it times out, check UDP/TCP 53 ACLs; if it returns `SERVFAIL`, check DNSSEC validation and upstream forwarders; if it returns `NXDOMAIN`, verify the zone record and Split-Horizon view.</p>'
    ),
    (5, 1): (
        '<h4>N10-009 Syslog Severity Table, SNMP OID Tree &amp; Telemetry Protocol Reference (Lesson 5.1)</h4>'
        '<p>Commit all eight RFC 5424 Syslog severity levels (`0`–`7`) and core monitoring protocols to memory for N10-009:</p>'
        + _tbl(
            ['Severity Code &amp; Name', 'Keyword', 'Operational Condition &amp; SIEM Alerting Action'],
            [
                ['0 — Emergency', 'emerg', 'System is unusable (kernel panic, total power/backplane failure) — Immediate PagerDuty P1'],
                ['1 — Alert', 'alert', 'Immediate action required (dual PSU failure, chassis temp critical) — Immediate P1'],
                ['2 — Critical', 'crit', 'Critical condition (core fiber transceiver fault, OSPF backbone down) — High-priority ticket'],
                ['3 — Error', 'err', 'Error condition (interface err-disabled by BPDU guard or port-security) — NOC investigation'],
                ['4 — Warning', 'warning', 'Warning condition (PoE budget >85%, native VLAN mismatch, DAI drop) — Proactive remediation'],
                ['5 — Notice', 'notice', 'Normal but significant event (LINEPROTO-5-UPDOWN, OSPF-5-ADJCHG, config change) — Audit log'],
                ['6 — Informational', 'info', 'Informational operational messages (SSH login success, DHCP ACK) — SIEM retention'],
                ['7 — Debug', 'debug', 'Packet-level debug trace — Disable in production after capture to protect CPU'],
            ]
        )
    ),
    (5, 2): (
        '<h4>N10-009 Infrastructure Plane Separation &amp; Hardening Verification Matrix (Lesson 5.2)</h4>'
        '<p>Network architectures divide device operations into three logical planes, each secured by dedicated controls:</p>'
        + _tbl(
            ['Architectural Plane', 'Core Traffic &amp; Protocols', 'Primary Threat Vector', 'Mandatory Hardening Controls'],
            [
                ['Management Plane', 'SSH (22), HTTPS (443), SNMPv3 (161/162), Syslog (514/6514), TACACS+ (49), NTP (123)', 'Credential sniffing, brute-force login, unauthorized config changes', 'Disable Telnet/HTTP/SNMPv1-2c; OOB Mgmt VLAN; VTY access-class; TACACS+ AAA; RBAC'],
                ['Control Plane', 'ARP, STP BPDUs, OSPF (89), BGP (179), EIGRP (88), LACP, HSRP/VRRP, ICMPv6 NDP', 'Route table poisoning, STP root hijack, CPU exhaustion DoS', 'Control Plane Policing (CoPP); OSPF/BGP cryptographic auth; BPDU Guard; RA Guard'],
                ['Data (Forwarding) Plane', 'End-user IPv4/IPv6 transit packets switched in CAM/CEF ASIC hardware', 'VLAN hopping, ARP spoofing, DHCP starvation, lateral malware spread', '802.1X NAC; DHCP Snooping; Dynamic ARP Inspection (DAI); IP Source Guard; Zone ACLs'],
            ]
        )
    ),
    (5, 3): (
        '<h4>N10-009 Zero-Trust, SASE / SSE &amp; Defense-in-Depth Control Matrix (Lesson 5.3)</h4>'
        '<p>Modern enterprise security combines on-premises Layer-2/Layer-3 segmentation with cloud-delivered **Secure Access Service Edge (SASE)** and **Security Service Edge (SSE)** controls: '
        '**Zero Trust Network Access (ZTNA)** replaces split-tunnel/full-tunnel legacy VPNs with identity- and posture-verified per-application micro-tunnels; '
        '**Secure Web Gateway (SWG)** inspects outbound TLS traffic and blocks malicious domains; '
        '**Cloud Access Security Broker (CASB)** enforces data loss prevention (DLP) across SaaS APIs; and '
        '**Firewall-as-a-Service (FWaaS)** applies uniform Layer-7 threat prevention across branch and remote users.</p>'
    ),
    (5, 4): (
        '<h4>N10-009 Layer-2 Attack Vector &amp; Countermeasure Mapping Table (Lesson 5.4)</h4>'
        '<p>Use this rapid-reference matrix to match every Layer-2 threat on N10-009 to its exact switchport mitigation command:</p>'
        + _tbl(
            ['Layer-2 Attack Vector', 'Attacker Mechanism', 'Exact Switch Countermeasure &amp; CLI Command'],
            [
                ['MAC Flooding / CAM Overflow', 'Floods frames with thousands of bogus Source MACs to fill CAM table', 'Port Security: switchport port-security maximum 2 + violation restrict/shutdown'],
                ['DTP Trunk Negotiation Spoofing', 'Sends forged DTP desirable frames to turn access port into 802.1Q trunk', 'Hardcode access mode &amp; disable DTP: switchport mode access + switchport nonegotiate'],
                ['802.1Q Double-Tag VLAN Hopping', 'Sends double-tagged frame whose outer VID matches trunk Native VLAN', 'Move Native VLAN to unused ID (switchport trunk native vlan 999) or tag native VLAN'],
                ['Rogue Switch / STP Root Hijack', 'Plugs in bridge with Priority 0 BPDUs to seize Root Bridge &amp; intercept traffic', 'Enable PortFast + BPDU Guard (spanning-tree bpduguard enable) &amp; Root Guard on downlinks'],
                ['Rogue DHCP Server / Starvation', 'Hands out fake gateway/DNS or exhausts DHCP pool with spoofed chaddr', 'Enable ip dhcp snooping; mark only uplinks ip dhcp snooping trust; rate-limit 15 pps'],
                ['ARP Cache Poisoning (MitM)', 'Broadcasts gratuitous ARP replies binding gateway IP to attacker MAC', 'Enable Dynamic ARP Inspection: ip arp inspection vlan 10,20 (validates via snooping DB)'],
            ]
        )
    ),
    (6, 1): (
        '<h4>N10-009 Physical &amp; Hardware Diagnostic Tool Selection Reference (Lesson 6.1)</h4>'
        '<p>Select the exact physical or software diagnostic instrument that matches the layer and media under test:</p>'
        + _tbl(
            ['Diagnostic Tool', 'Media / Layer', 'What It Measures &amp; When to Select It on N10-009'],
            [
                ['Tone Generator &amp; Inductive Probe', 'Copper UTP (L1)', 'Traces an unlabelled wall jack to its 110 patch panel port via audible warble tone'],
                ['Cable Continuity / Wiremap Tester', 'Copper RJ-45 (L1)', 'Detects open pins, shorts, crossed pairs, reversed pairs, and split pairs across pins 1–8'],
                ['Time-Domain Reflectometer (TDR)', 'Copper Metallic (L1)', 'Measures cable length and exact distance in meters to an impedance fault, crimp, or cut'],
                ['Optical Power Meter &amp; Light Source', 'SMF / MMF Fiber (L1)', 'Measures end-to-end optical insertion loss in dB and received power in dBm'],
                ['Optical Time-Domain Reflectometer (OTDR)', 'Long-Haul Fiber (L1)', 'Graphs backscatter/Fresnel reflections to pinpoint splice loss, micro-bends, and fiber breaks'],
                ['Visual Fault Locator (VFL)', 'Fiber Patch / Tray (L1)', 'Injects visible 650 nm red laser light that glows through jacket at sharp bends or breaks'],
                ['Wi-Fi Analyzer / RF Spectrum Analyzer', '802.11 RF (L1/L2)', 'Wi-Fi analyzer reads SSIDs, channels, RSSI; Spectrum analyzer sees non-802.11 RF interferers'],
            ]
        )
    ),
    (6, 2): (
        '<h4>N10-009 Change Management, Maintenance Windows &amp; Escalation Governance (Lesson 6.2)</h4>'
        '<p>Every production network modification follows formal **Change Management** governance to prevent self-inflicted outages: '
        '**Standard Changes** (pre-authorized, low-risk repeatable tasks like assigning an access port VLAN), **Normal Changes** (peer-reviewed by the Change Advisory Board `CAB` with a scheduled maintenance window, impact analysis, test plan, and backout procedure), and **Emergency Changes** (expedited approval to restore service during a live Severity-1 outage or patch an actively exploited zero-day vulnerability, followed by retrospective CAB documentation).</p>'
    ),
    (6, 3): (
        '<h4>N10-009 High Availability Metrics (MTBF, MTTR, RPO, RTO) &amp; DR Testing Reference (Lesson 6.3)</h4>'
        '<p>Network verification and continuity planning rely on four quantitative availability metrics: '
        '**MTBF (Mean Time Between Failures)** measures reliability (average operating time between hardware/circuit faults); '
        '**MTTR (Mean Time To Repair / Restore)** measures maintainability (average time to diagnose, fix, and verify service restoration); '
        '**RPO (Recovery Point Objective)** defines the maximum acceptable age of lost data (governed by backup/replication frequency—e.g., synchronous SAN replication achieves `RPO = 0`); and '
        '**RTO (Recovery Time Objective)** defines the maximum acceptable downtime before business operations are restored (`Five Nines = 99.999%` availability permits only **5.26 minutes** of unplanned downtime per year).</p>'
    ),
    (6, 4): (
        '<h4>N10-009 Master Command &amp; Protocol Synthesis Review (Lesson 6.4)</h4>'
        '<p>Before sitting the Knowledge Test or Practical Skills Exam, confirm you can trace a packet from an end-user browser (`HTTPS TCP 443`) through local DNS resolution (`UDP/TCP 53`), ARP/NDP neighbor resolution (`EtherType 0x0806` / `ICMPv6 Type 135/136`), 802.1Q access-to-trunk VLAN switching (`TPID 0x8100`), FHRP default gateway redundancy (`HSRP UDP 1985` / `VRRP IP 112`), OSPF/BGP longest-prefix routing (`AD 110` / `AD 20`), stateful zone firewall inspection, and outbound PAT (`inside local -> inside global`)—and state the exact CLI command that proves each hop.</p>'
    ),
    (9, 1): (
        '<h4>N10-009 Lab 9.1 Verification Checklist: Physical Console, Privilege Levels &amp; Neighbor Discovery</h4>'
        '<p>In Lab 9.1, always confirm three items before advancing: (1) serial settings `9600-8-N-1` with flow control `None`; (2) privilege level transition from `Switch>` (`Level 1`) to `Switch#` (`Level 15`) via `enable`; and (3) neighbor port mapping via `show cdp neighbors detail` and `show lldp neighbors` so you never configure the wrong trunk interface.</p>'
    ),
    (9, 2): (
        '<h4>N10-009 Lab 9.2 Verification Checklist: VLAN Creation, Access Port Binding &amp; Trunk Allowed Lists</h4>'
        '<p>In Lab 9.2, verify that every created VLAN shows `active` in `show vlan brief`, every workstation port shows `static access` in `show interfaces switchport`, and every inter-switch link lists the new VLAN under both `Vlans allowed on trunk` and `Vlans allowed and active in management domain` in `show interfaces trunk`.</p>'
    ),
    (9, 3): (
        '<h4>N10-009 Lab 9.3 Verification Checklist: Router Interface IP Addressing &amp; RIB Code Inspection</h4>'
        '<p>In Lab 9.3, verify that every configured router interface shows `up / up` in `show ip interface brief` and installs both a `C` (`Connected` subnet) and an `L` (`Local` `/32` host) entry in `show ip route`.</p>'
    ),
    (9, 4): (
        '<h4>N10-009 Lab 9.4 Verification Checklist: 802.1Q Subinterfaces &amp; Inter-VLAN Ping Proof</h4>'
        '<p>In Lab 9.4, verify that each subinterface (`Gi0/0.10`, `Gi0/0.20`) applies `encapsulation dot1Q <vlan>` prior to `ip address`, that the parent physical interface `Gi0/0` is `no shutdown`, and that end-to-end pings between hosts in VLAN 10 and VLAN 20 succeed after the initial ARP resolution packet.</p>'
    ),
    (9, 5): (
        '<h4>N10-009 Lab 9.5 Verification Checklist: Full Closet Turn-Up &amp; Bidirectional Static Routing</h4>'
        '<p>In Lab 9.5, verify that both forward and return static routes (`S` in `show ip route`) or default routes (`S* 0.0.0.0/0`) are installed on every router along the path, and confirm hop-by-hop reachability with `traceroute`.</p>'
    ),
    (9, 6): (
        '<h4>N10-009 Lab 9.6 Verification Checklist: NVRAM Persistence &amp; Zero-Diff Audit</h4>'
        '<p>In Lab 9.6, confirm that `show running-config` and `show startup-config` match identically after executing `copy running-config startup-config`, ensuring your hostname, VLANs, subinterfaces, and routes survive a chassis reload.</p>'
    ),
})

NETOPS_ARCHITECTURE_LABS = {
    (1, 1): (
        '<h4>Enterprise Architecture Note 1.1: Spine-Leaf Clos Topologies vs Three-Tier Hierarchical Campus Design</h4>'
        '<p>Compare traditional **Three-Tier Campus Hierarchy (Core, Distribution, Access)** with modern **Data Center Spine-Leaf (Clos) Architecture**: '
        'in a Three-Tier campus, Access switches aggregate end-user endpoints and PoE devices, Distribution switches enforce Layer-3 SVIs, ACLs, and FHRP gateways while blocking redundant Layer-2 paths via Rapid PVST+, and Core switches provide high-speed Layer-3 backbone switching across buildings. '
        'In a Data Center Spine-Leaf fabric, every **Leaf (Top-of-Rack)** switch connects to every **Spine** switch via Layer-3 routed ECMP links (OSPF or BGP unnumbered) with zero Spine-to-Spine or Leaf-to-Leaf links. '
        'Because every server-to-server East-West flow crosses exactly `Leaf -> Spine -> Leaf` (a deterministic 2-hop latency path) and uses **VXLAN BGP EVPN** overlays across all active uplinks without STP blocking half the bandwidth, Spine-Leaf fabrics scale predictably for virtualization, Kubernetes, and NVMe-oF storage clusters.</p>'
    ),
    (1, 2): (
        '<h4>Enterprise Architecture Note 1.2: Dual-Stack Transition Mechanisms, NAT64/DNS64 &amp; RFC 6877 464XLAT</h4>'
        '<p>When migrating enterprise networks from IPv4 to IPv6, engineers choose among three transition architectures: '
        '(1) **Dual-Stack (RFC 4213)**, where every router, switch SVI, firewall, and host runs both IPv4 and IPv6 stacks natively and applications prefer IPv6 via **Happy Eyeballs (RFC 8305)** (attempting AAAA connections first and falling back to IPv4 within 250 ms if IPv6 fails); '
        '(2) **6in4 / GRE / IPsec Tunneling**, where isolated IPv6 islands encapsulate IPv6 packets (IP protocol `41` for 6in4 or `47` for GRE) across a legacy IPv4 WAN; and '
        '(3) **NAT64 + DNS64 (RFC 6146 / RFC 6147)** on IPv6-only mobile and IoT networks, where the DNS64 resolver synthesizes an `AAAA` record using the well-known prefix **`64:ff9b::/96`** concatenated with the remote server\'s 32-bit IPv4 address (`203.0.113.20` -> `64:ff9b::cb00:7114`), and the stateful NAT64 gateway translates the IPv6 packet into IPv4 on egress.</p>'
    ),
    (1, 3): (
        '<h4>Enterprise Architecture Note 1.3: Quality of Service (QoS) Marking, DSCP Per-Hop Behaviors &amp; Policing vs Shaping</h4>'
        '<p>When voice, video, and bulk backup traffic contend for a congested WAN uplink, **Quality of Service (QoS)** classifies packets at the access edge (**Trust Boundary**), marks their Layer-2 **IEEE 802.1p CoS (3-bit PCP)** and Layer-3 **DiffServ DSCP (6-bit field in IPv4 ToS / IPv6 Traffic Class, RFC 2474)**, and schedules queues at egress: '
        '**Expedited Forwarding (`DSCP EF = 46`, CoS `5`)** feeds the **Low-Latency Queue (LLQ / Strict Priority Queue)** for interactive VoIP RTP audio (policed to ~30% of link capacity so voice can never starve routing protocols); '
        '**Assured Forwarding (`DSCP AF41 = 34`, CoS `4`)** serves interactive video conferencing; '
        '**Class Selector 6 (`DSCP CS6 = 48`)** reserves bandwidth for OSPF, BGP, and BFD control-plane packets; and '
        '**Default (`DSCP DF / CS0 = 0`)** handles best-effort HTTP/SMB transfers. '
        'At the WAN edge, **Traffic Shaping** buffers excess bursts in memory to smooth egress traffic to the carrier\'s Committed Information Rate (CIR) without dropping TCP segments, whereas **Traffic Policing** enforces a hard rate limit by immediately dropping or remarking excess bursts without buffering.</p>'
    ),
    (1, 4): (
        '<h4>Enterprise Architecture Note 1.4: Automated Network Verification &amp; Synthetic SLA Probes (IP SLA / TWAMP)</h4>'
        '<p>Rather than waiting for users to report outages, enterprise networks run continuous synthetic **Cisco IP SLA** or **TWAMP (Two-Way Active Measurement Protocol, RFC 5357)** probes between branch routers and core services. '
        'An IP SLA `udp-jitter` probe transmits synthetic RTP-sized packets every 20 ms to measure one-way latency (target `< 150 ms`), jitter (`< 30 ms`), packet loss (`< 1%`), and **Mean Opinion Score (`MOS`, scale `1.0` bad to `5.0` ideal, voice target `>= 4.0`)**, automatically triggering an **Object Tracking (`track 1 ip sla 10 reachability`)** failover for HSRP or floating static routes when carrier brownouts degrade link quality without dropping physical carrier.</p>'
    ),
    (2, 1): (
        '<h4>Enterprise Architecture Note 2.1: Multi-Chassis EtherChannel (vPC / MLAG / StackWise) &amp; Split-Brain Prevention</h4>'
        '<p>Standard IEEE 802.3ad LACP terminates all member links of a Port-Channel on a single physical switch—leaving the switch chassis itself as a Single Point of Failure (SPOF). '
        'To achieve active-active Layer-2 forwarding across two separate distribution switches with **zero STP blocked links**, enterprise networks deploy **Multi-Chassis Link Aggregation (MLAG / Cisco vPC / Arista MLAG)** or **Switch Stacking (StackWise / VSF)**. '
        'An access switch or dual-homed hypervisor bundles one link to Core Switch A and one link to Core Switch B into a single logical LACP Port-Channel, while a dedicated **Peer-Link** and out-of-band **Peer-Keepalive heartbeat** synchronize MAC tables and IGMP state between the two cores.</p>'
    ),
    (2, 2): (
        '<h4>Enterprise Architecture Note 2.2: IEEE 802.1ad Q-in-Q Provider Bridging &amp; VRF-Lite Multi-Tenancy</h4>'
        '<p>When a Metro Ethernet service provider or multi-tenant campus carries multiple customer 802.1Q trunks across a shared optical metro backbone, **IEEE 802.1ad Provider Bridging (Q-in-Q)** prepends an outer **Service VLAN tag (`S-TAG`, EtherType `0x88A8`)** outside the customer\'s inner **Customer VLAN tag (`C-TAG`, EtherType `0x8100`)**, allowing each tenant to keep their own VLAN 10–4094 numbering without collision. '
        'At Layer 3, **VRF-Lite (Virtual Routing and Forwarding)** partitions a single physical router or multilayer switch into multiple independent virtual routing tables (`ip vrf FINANCE`, `ip vrf GUEST_WIFI`), each with its own isolated RIB, FIB, ARP table, and OSPF process, so overlapping RFC 1918 subnets never leak between tenants unless explicitly route-leaked through a firewall.</p>'
    ),
    (2, 3): (
        '<h4>Enterprise Architecture Note 2.3: Data Center Rack Thermal Airflow (Hot-Aisle / Cold-Aisle) &amp; Twinax DAC / AOC</h4>'
        '<p>Inside the MDF/Data Center, physical reliability depends on thermal containment and short-reach interconnect selection: '
        'server and switch racks are arranged in alternating **Cold Aisles** (perforated raised-floor tiles supplying `18–27 °C` chilled air into front equipment intakes) and **Hot Aisles** (rear exhaust ducts returning heated air to CRAC/CRAH HVAC units); every front-to-back or side-to-back switch fan tray must match the rack\'s airflow direction, and empty rack units must be sealed with **blanking panels** to prevent hot exhaust recirculation. '
        'For short Top-of-Rack connections (`1–5 meters`), **Passive Copper Twinax Direct Attach Cables (DAC)** provide the lowest cost and latency (`< 0.1 µs`), **Active Optical Cables (AOC)** span `5–30 meters` inside a row, and modular **SFP28/QSFP28 optical transceivers** on structured OM4/OS2 patch panels serve cross-row runs.</p>'
    ),
    (2, 4): (
        '<h4>Enterprise Architecture Note 2.4: Out-of-Band Power Redundancy — Dual PSUs, A/B PDUs, UPS Topologies &amp; Generators</h4>'
        '<p>A core switch with dual hot-swappable Power Supply Units (`PSU-1` and `PSU-2`) still suffers a total outage if both power cords are plugged into the same rack Power Distribution Unit (PDU) or the same Uninterruptible Power Supply (UPS) branch circuit! '
        'True Tier-III/IV power high availability wires `PSU-1` to **A-Side PDU -> Online Double-Conversion UPS A -> Utility Feed A** and wires `PSU-2` to **B-Side PDU -> Online Double-Conversion UPS B -> Utility Feed B / Automatic Transfer Switch (ATS) + Diesel Generator**, ensuring zero-millisecond cutover during utility blackouts, brownouts (sags), or single-PDU maintenance.</p>'
    ),
    (3, 1): (
        '<h4>Enterprise Architecture Note 3.1: OSPFv2 vs OSPFv3 (IPv6 RFC 5340) &amp; Equal-Cost Multi-Path (ECMP)</h4>'
        '<p>While **OSPFv2 (RFC 2328)** runs exclusively for IPv4, **OSPFv3 (RFC 5340)** was redesigned for IPv6 (and supports both IPv6 and IPv4 address families via RFC 5838): '
        'OSPFv3 forms neighbor adjacencies using **IPv6 Link-Local addresses (`fe80::/10`)** regardless of global subnet prefixes, authenticates packets using IPv6 IPsec/ESP or RFC 7166 Auth Trailer, moves prefix topology out of Router/Network LSAs into dedicated **Intra-Area-Prefix LSAs (Type 9)** so a prefix change does not force a full SPF tree recalculation, and is enabled directly per interface (`ipv6 ospf 1 area 0`) rather than using `network` wildcard statements.</p>'
    ),
    (3, 2): (
        '<h4>Enterprise Architecture Note 3.2: BGP Route Reflectors, Confederation &amp; Internet Exchange Peering</h4>'
        '<p>Why does **Internal BGP (iBGP, AD 200)** require either a full mesh (`N * (N - 1) / 2` TCP 179 sessions) or a **Route Reflector (RFC 4456)**? '
        'Because iBGP operates within a single Autonomous System (`AS_PATH` does not change on iBGP updates), loop prevention cannot rely on `AS_PATH` inspection. '
        'Therefore, RFC 4271 enforces the **iBGP Split-Horizon Rule**: an iBGP speaker NEVER advertises a route learned from one iBGP peer to another iBGP peer! '
        'Deploying a pair of redundant **BGP Route Reflectors** with `CLUSTER_ID` and `ORIGINATOR_ID` attributes allows edge routers (`Route Reflector Clients`) to peer only with the Route Reflectors instead of maintaining `O(N^2)` full-mesh TCP sessions.</p>'
    ),
    (3, 3): (
        '<h4>Enterprise Architecture Note 3.3: CAPWAP Split-MAC vs FlexConnect (Local Switching) &amp; WPA3-SAE</h4>'
        '<p>In an enterprise Wireless LAN Controller (WLC) architecture using **CAPWAP (RFC 5415, UDP 5246 control / UDP 5247 data)**, engineers select between two forwarding modes: '
        '**Central Switching (Local Mode)** tunnels 100% of client 802.11 traffic back to the central WLC in the data center (ideal for campus headquarters roaming across subnets), whereas **FlexConnect (Local Switching)** keeps the CAPWAP control plane on the central WLC over the WAN while switching authenticated client VLAN traffic locally at the branch switch—preventing branch office traffic from hair-pinning across a slow WAN circuit and allowing existing clients to stay connected if the WAN link to the WLC drops. '
        'On WPA3-Personal networks, **Simultaneous Authentication of Equals (SAE / Dragonfly handshake)** replaces the legacy WPA2 4-way PSK handshake, providing forward secrecy and immunity against offline dictionary capture attacks.</p>'
    ),
    (3, 4): (
        '<h4>Enterprise Architecture Note 3.4: Wireless Location Services, BLE Beacons &amp; Rogue AP Containment</h4>'
        '<p>Enterprise APs equipped with dedicated scanning radios perform continuous **Wireless Intrusion Detection and Prevention (WIDS/WIPS)**: comparing observed BSSIDs and SSIDs against the wired switch CAM/LLDP tables to distinguish an external neighbor\'s Wi-Fi from a dangerous **Rogue AP** (an unauthorized AP physically plugged into an internal corporate switch port) or an **Evil Twin AP** (an attacker broadcasting the corporate SSID to harvest credentials). '
        'When a Rogue AP is confirmed on an internal switch port via MAC correlation, the controller automatically shuts the switch port via SNMPv3/NETCONF rather than relying solely on over-the-air deauthentication frames (which are blocked when IEEE 802.11w Protected Management Frames are active).</p>'
    ),
    (4, 1): (
        '<h4>Enterprise Architecture Note 4.1: High-Availability DHCP Failover Clustering (RFC 8156) &amp; Split-Scope 80/20</h4>'
        '<p>Because DHCP is a critical foundation service, a single failed DHCP server halts network onboarding once T1/T2 lease timers expire. '
        'Enterprise architects deploy DHCP High Availability using either **Active/Passive or Load-Balanced DHCP Failover Protocol** (where two servers replicate lease state over a heartbeat TCP peer link and hold a Maximum Client Lead Time `MCLT`), or the classic **80/20 Split-Scope Design** (where Primary Server A holds 80% of the subnet pool with a `0 ms` offer delay and Secondary Server B in another data center holds the remaining non-overlapping 20% of the pool with a `50–100 ms` `Offer Delay`, plus both servers appear as `ip helper-address` entries on every router SVI).</p>'
    ),
    (4, 2): (
        '<h4>Enterprise Architecture Note 4.2: Anycast DNS Resolution, Response Policy Zones (RPZ) &amp; DNS Sinkholing</h4>'
        '<p>How do global public resolvers (`1.1.1.1`, `8.8.8.8`, `9.9.9.9`) and large enterprise DNS clusters achieve 100% uptime and sub-5 ms latency without requiring clients to change their configured DNS server IP? '
        'They deploy **IP Anycast**: multiple geographically distributed DNS servers configure the exact same `/32` loopback IP address (`10.100.53.53/32`) and advertise it into OSPF/BGP alongside a local health-check script. '
        'Every client query is automatically routed to the topologically nearest healthy resolver, and if one resolver daemon crashes, its local BGP/OSPF health daemon withdraws the `/32` advertisement within 1 second so traffic shifts seamlessly to the next nearest Anycast node. '
        'On those resolvers, **DNS Response Policy Zones (RPZ) / DNS Sinkholing** intercept queries for known command-and-control (`C2`) malware domains and return `NXDOMAIN` or a forensic sinkhole IP (`10.100.99.99`), immediately identifying infected internal endpoints by their source IP in the DNS query log.</p>'
    ),
    (4, 3): (
        '<h4>Enterprise Architecture Note 4.3: Next-Generation Firewalls (NGFW), Web Application Firewalls (WAF) &amp; Load Balancers</h4>'
        '<p>Distinguish the three perimeter and application-delivery appliances tested on N10-009: '
        '(1) A **Stateful Layer-4 Firewall** tracks TCP/UDP/ICMP connection state tables and enforces IP/port ACLs; '
        '(2) A **Next-Generation Firewall (NGFW)** adds **Deep Packet Inspection (DPI)**, **Application-ID** (recognizing SSH or BitTorrent running over non-standard port TCP 443), integrated **Intrusion Prevention System (IPS)** signature/anomaly blocking, **User-ID** (Active Directory mapping), and TLS decryption inspection; and '
        '(3) A **Reverse Proxy / Application Delivery Controller (ADC / Load Balancer)** with an integrated **Web Application Firewall (WAF)** terminates public HTTPS connections on a **Virtual IP (VIP)**, offloads TLS certificates, inspects HTTP payloads against OWASP Top 10 attacks (SQL injection, XSS), and distributes requests across backend server pools using **Round-Robin**, **Least Connections**, **Weighted**, or **Source-IP Hash** scheduling with active HTTP `/healthz` probes.</p>'
    ),
    (4, 4): (
        '<h4>Enterprise Architecture Note 4.4: NTP Stratum Security, PTP (IEEE 1588) &amp; IPAM-Driven Automation</h4>'
        '<p>While **NTPv4 (RFC 5905, UDP 123)** synchronizes enterprise switches, servers, and Active Directory domain controllers within `1–10 milliseconds`, high-frequency trading, 5G cellular base stations, and broadcast video studios require sub-microsecond clock accuracy provided by **Precision Time Protocol (PTP, IEEE 1588v2)** using hardware timestamping in switch PHY silicon (`Grandmaster Clock -> Boundary Clock -> Ordinary Clock`). '
        'In modern NetDevOps pipelines, **IPAM (NetBox / Infoblox)** acts as the single **Source of Truth (SoT)**: assigning an IP and VLAN in IPAM automatically triggers Ansible/Terraform webhooks to render the DNS `A`/`PTR` records, DHCP reservations, and switchport configurations without manual copy-paste errors.</p>'
    ),
}

NETOPS_ARCHITECTURE_LABS.update({
    (5, 1): (
        '<h4>Enterprise Architecture Note 5.1: Streaming Telemetry (gNMI / NETCONF YANG) vs Legacy SNMP Polling</h4>'
        '<p>Why are modern cloud and campus fabrics supplementing SNMPv3 (`UDP 161` pull polling every 1–5 minutes) with **Model-Driven Streaming Telemetry (`gNMI / gRPC` over HTTP/2 TLS and `NETCONF` RFC 6241 over SSH TCP 830 / `RESTCONF` RFC 8040 over HTTPS)**? '
        'SNMP polling suffers from two architectural limits: polling thousands of interface OIDs sequentially using `snmpwalk` spikes switch control-plane CPU, and a 5-minute polling interval completely misses a 400-millisecond microburst queue drop! '
        'With **YANG data models (RFC 7950)** and **gNMI Streaming Telemetry**, switches push structured JSON/Protobuf state changes (`on-change` for BGP/OSPF/interface state or `sample` every 1–5 seconds for queue counters) over a persistent encrypted gRPC stream directly into Prometheus/Time-Series databases with sub-second visibility and minimal CPU overhead.</p>'
    ),
    (5, 2): (
        '<h4>Enterprise Architecture Note 5.2: Control Plane Policing (CoPP), uRPF Anti-Spoofing &amp; MACsec (802.1AE)</h4>'
        '<p>Even when the Management Plane (`SSH`, `SNMPv3`) is locked down, an attacker or misconfigured host can cripple a router or Layer-3 switch by flooding packets that punt from the hardware forwarding ASIC to the route processor CPU—such as ARP requests, TTL=1 packets, IP options, or spoofed OSPF/BGP packets. '
        'Configuring **Control Plane Policing (CoPP, `control-plane` service-policy)** applies modular QoS rate-limiters directly in front of the route processor CPU: guaranteeing bandwidth for critical OSPF/BGP/LACP peers while rate-limiting or dropping excessive ARP, ICMP Unreachable, and TTL-expired punts. '
        'At the WAN/ISP edge, **Unicast Reverse Path Forwarding (`ip verify unicast source reachable-via rx`)** automatically drops any ingress packet whose source IP address is not reachable back out the exact interface on which it arrived. '
        'For point-to-point campus fiber links crossing public utility conduits, **IEEE 802.1AE MACsec** encrypts the entire Layer-2 Ethernet frame at line rate (`10G/40G/100G` AES-GCM-128/256 in PHY hardware) using MKA (MACsec Key Agreement) over 802.1X.</p>'
    ),
    (5, 3): (
        '<h4>Enterprise Architecture Note 5.3: Industrial ICS / SCADA Purdue Model Zones &amp; Honeypots / Deception</h4>'
        '<p>In manufacturing, power grid, and water treatment Operational Technology (**OT / ICS / SCADA**) networks running protocols like Modbus/TCP (`TCP 502`), DNP3 (`TCP 20000`), and BACnet (`UDP 47808`), engineers enforce the **Purdue Enterprise Reference Architecture**: '
        'strictly separating **Enterprise IT (Levels 4–5)** from the **Industrial DMZ (Level 3.5)** and **OT Supervisory / PLC / Sensor Zones (Levels 0–3)** via dual-homed industrial firewalls or hardware **Unidirectional Security Gateways (Data Diodes)** that physically permit telemetry to flow outward from OT to IT while making inbound packet injection physically impossible. '
        'Inside the corporate and OT DMZ segments, deploying **Deception Systems / Honeypots** (decoy SMB/SSH/PLC listeners that no legitimate host ever contacts) provides a zero-false-positive tripwire: a single TCP `SYN` to a honeypot IP immediately triggers a SIEM high-severity alert and NAC port quarantine.</p>'
    ),
    (5, 4): (
        '<h4>Enterprise Architecture Note 5.4: Automated Compliance Auditing (Ansible, Batfish &amp; Golden Config Drift)</h4>'
        '<p>Rather than manually logging into 200 switches via SSH to check whether `no ip http server`, `ip ssh version 2`, `vtp mode transparent`, and `spanning-tree portfast bpduguard default` are present, enterprise NetSecOps teams run **automated pre-deployment validation (Batfish / pyATS)** and **idempotent Ansible (`cisco.ios.ios_config`) / NCM compliance scans**. '
        'Every night, the NCM server pulls the `running-config` via SSH/NETCONF, normalizes volatile lines (such as `ntp clock-period`), diffs it against the approved **CIS Benchmark Golden Template**, and opens an automated remediation ticket or pushes a signed configuration patch if any port or ACL drifts out of compliance.</p>'
    ),
    (6, 1): (
        '<h4>Enterprise Architecture Note 6.1: TCP Throughput Math — Bandwidth-Delay Product (BDP) &amp; Bufferbloat</h4>'
        '<p>Why does a 10 Gbps long-haul transcontinental fiber circuit with `0%` packet loss and `80 ms` round-trip latency (`RTT`) sometimes transfer a single-stream backup at only `6.5 Mbps` when using a legacy unscaled 64 KB TCP receive window? '
        'Because of the **Bandwidth-Delay Product (`BDP = Bandwidth x RTT`)**, which defines the volume of unacknowledged data that must be "in flight" on the wire to fill the pipe: '
        '`Max Throughput = TCP_Receive_Window_Bits / RTT_Seconds`. With a `64 KB` (`524,288-bit`) window and `0.080 s` RTT, a single TCP stream can never exceed `524,288 / 0.080 = 6.55 Mbps` regardless of whether the link is 100 Mbps or 100 Gbps! '
        'Filling a 1 Gbps path at 80 ms RTT requires `10^9 bps * 0.080 s = 80 Mbits = 10 MB` of in-flight window (`TCP Window Scaling` RFC 7323 shift count `>= 8`). '
        'Conversely, oversized unmanaged FIFO queues on consumer/branch WAN routers cause **Bufferbloat** (latency spiking from 15 ms to 800+ ms under upload load), which is cured by enabling **Active Queue Management (`FQ-CoDel` or `PIE`)** and shaping at 95% of line rate.</p>'
    ),
    (6, 2): (
        '<h4>Enterprise Architecture Note 6.2: Major Incident Command Roles, Blameless Post-Mortems &amp; Runbook Maturity</h4>'
        '<p>During a Severity-1 enterprise outage, high-reliability NOCs separate technical keyboard execution from stakeholder communication using the **Incident Command System (ICS)**: '
        'the **Incident Commander (IC)** owns the timeline, enforces 15-minute time-boxes on hypotheses, and decides when to execute a rollback; the **Subject Matter Expert (SME / Scribe)** executes single-variable CLI diagnostics and captures terminal logs; and the **Communications Lead** publishes structured stakeholder updates (`Impact`, `Current Action`, `Next Update Time`). '
        'Within 48 hours of resolution, the team conducts a **Blameless Post-Incident Review (Post-Mortem)** focused on systemic guardrails (e.g., "Why did our CI/CD pipeline allow a trunk VLAN list to be overwritten with `switchport trunk allowed vlan 40` instead of `add 40`?") rather than individual blame.</p>'
    ),
    (6, 3): (
        '<h4>Enterprise Architecture Note 6.3: Backup Verification Rules (3-2-1-1-0), Config Encryption &amp; Sanitization</h4>'
        '<p>Infrastructure resilience requires applying the **3-2-1-1-0 Backup Rule** to both server data and network appliance configurations/PKI keys (`3` copies of data, on `2` different media types, with `1` copy offsite, `1` copy air-gapped/immutable via WORM object lock against ransomware, and `0` unverified recovery errors in automated restore drills). '
        'Before exporting router or firewall configurations to an external ticket or vendor TAC case, ensure **`service password-encryption`** (or Type 8/9 hashing) is active and redact any cleartext PSKs, SNMP strings, or private keys; and when decommissioning hardware for disposal or RMA, follow **NIST SP 800-88 Rev 1 Media Sanitization** (`write erase` + `delete /force /recursive flash:vlan.dat` + cryptographic erase or physical shredding of NVRAM/SSD media).</p>'
    ),
    (6, 4): (
        '<h4>Enterprise Architecture Note 6.4: End-to-End Packet Walk Synthesis — Workstation Boot to Cloud HTTPS Response</h4>'
        '<p>Trace the complete life of a workstation connecting to a corporate network from power-on: '
        '(1) **Layer 1:** RJ-45 patch cord negotiates `1000BASE-T Full-Duplex` via Fast Link Pulses (`FLP`) and PoE classification if applicable; '
        '(2) **Layer 2 Admission:** Port passes **802.1X EAP-TLS** via RADIUS (`UDP 1812`), receives dynamic `VLAN 10`, and transitions via **RSTP PortFast + BPDU Guard** directly to `Forwarding`; '
        '(3) **DHCPv4 DORA:** Host broadcasts `DHCPDISCOVER`; switch `DHCP Snooping` permits it out the trusted uplink; router SVI `ip helper-address` relays it (`giaddr = 10.10.10.1`) to the DHCP cluster, which returns `10.10.10.45/24`, Option 3 Gateway `10.10.10.1`, and Option 6 DNS `10.100.10.53`; '
        '(4) **DNS &amp; ARP:** Host ARPs for `10.10.10.1` (`DAI` validates the reply against the snooping DB), receives the **HSRP/VRRP Virtual MAC (`0000.0c07.ac0a`)**, queries DNS `UDP 53` for `app.novak.example`, and receives `198.51.100.20` with a validated **DNSSEC `RRSIG`**; '
        '(5) **Routing, NAT &amp; TLS 1.3:** Packet routes via **OSPF Area 0 (`AD 110`)** to the perimeter NGFW, undergoes **PAT (`10.10.10.45:51420 -> 203.0.113.5:51420`)**, exits via **eBGP (`AD 20`)**, and completes a **1-RTT TLS 1.3 ECDHE** handshake on `TCP 443`.</p>'
    ),
    (9, 1): (
        '<h4>Enterprise CLI Troubleshooting Note 9.1: Resolving Bad Console Baud Rates, Stuck SSH Sessions &amp; DNS Lookup Delays</h4>'
        '<p>Two classic lab and field annoyances have instant CLI fixes: '
        'first, if your serial console prints garbled hieroglyphics (`x~?@#`), the previous technician left the router\'s console baud rate set to `115200` in the configuration register instead of default `9600` (`9600-8-N-1`); '
        'second, if mistyping a command at the `Switch#` prompt freezes your terminal for 30 seconds while printing `Translating "shwo"... domain server (255.255.255.255)`, IOS is treating your typo as a Telnet hostname and broadcasting a DNS lookup! '
        'Configure **`no ip domain-lookup`** in global configuration mode (or press `Ctrl+Shift+6` to abort) and add **`logging synchronous`** under `line con 0` and `line vty 0 15` so unsolicited syslog messages never split the command line you are currently typing.</p>'
    ),
    (9, 2): (
        '<h4>Enterprise CLI Troubleshooting Note 9.2: Verifying Spanning-Tree Port States After Assigning Access VLANs</h4>'
        '<p>When you move a workstation port from VLAN 1 to VLAN 10 (`switchport access vlan 10`) without `spanning-tree portfast`, classic STP/PVST+ holds the port in `Listening` (15 seconds) and `Learning` (15 seconds) before transitioning to `Forwarding`. '
        'During those 30 seconds, the workstation OS often times out its initial `DHCPDISCOVER` bursts and falls back to an `169.254.x.x` APIPA address even though the VLAN configuration is 100% correct! '
        'Enabling `spanning-tree portfast` (paired with `spanning-tree bpduguard enable`) on all end-host access ports transitions the port to `Forwarding` in `0 seconds` so DHCP succeeds immediately on link-up.</p>'
    ),
    (9, 3): (
        '<h4>Enterprise CLI Troubleshooting Note 9.3: Overlapping Subnet Errors (`% 10.10.10.0 overlaps with GigabitEthernet0/0`)</h4>'
        '<p>Unlike Layer-2 switches (where multiple access ports belong to the same VLAN/subnet), **every routed Layer-3 interface or subinterface on a router MUST belong to a distinct, non-overlapping IP subnet**. '
        'If a router complains `% 10.10.10.0 overlaps with GigabitEthernet0/0` when you configure `Gi0/1`, check the subnet masks on both interfaces (`show ip interface brief` and `show running-config interface Gi0/0`): a typo such as `255.255.0.0 (/16)` instead of `255.255.255.0 (/24)` on `Gi0/0` causes `10.10.10.1/16` to swallow the entire `10.10.0.0`–`10.10.255.255` range and overlap with `10.10.20.1/24` on `Gi0/1`.</p>'
    ),
    (9, 4): (
        '<h4>Enterprise CLI Troubleshooting Note 9.4: Diagnosing `% Configuring IP routing on a LAN subinterface is only allowed if...`</h4>'
        '<p>On Cisco IOS routers, if you enter `interface GigabitEthernet0/0.10` and immediately type `ip address 10.10.10.1 255.255.255.0`, IOS rejects the command with: '
        '`% Configuring IP routing on a LAN subinterface is only allowed if that subinterface is already configured as part of an IEEE 802.10, IEEE 802.1Q, or ISL vLAN.` '
        'Always configure **`encapsulation dot1Q 10`** FIRST on the subinterface (or `encapsulation dot1Q 99 native` if the subinterface matches the trunk\'s untagged Native VLAN), and then apply the `ip address` command.</p>'
    ),
    (9, 5): (
        '<h4>Enterprise CLI Troubleshooting Note 9.5: Why a Static Route Disappears From `show ip route`</h4>'
        '<p>If you configure `ip route 10.50.0.0 255.255.255.0 172.16.12.2` in global configuration mode and confirm the line exists in `show running-config`, yet `show ip route static` is completely empty, why did IOS refuse to install your static route into the RIB? '
        'A router only installs a static route in `show ip route` if **the next-hop IP (`172.16.12.2`) is resolvable through an active (`up/up`) local exit interface**! '
        'If the WAN interface (`Gi0/1` with `172.16.12.1/30`) is still `administratively down` (`shutdown`) or its cable is unplugged (`down/down`), the static route remains dormant in `running-config` and immediately appears in `show ip route` the instant `Gi0/1` reaches `up/up`.</p>'
    ),
    (9, 6): (
        '<h4>Enterprise CLI Troubleshooting Note 9.6: Recovering From an Accidental Config Change Without Rebooting</h4>'
        '<p>What is the difference between `copy startup-config running-config` and `configure replace nvram:startup-config force`? '
        '`copy startup-config running-config` performs an **additive merge** in RAM (it does NOT remove extra lines you added to `running-config` since boot), whereas **`configure replace nvram:startup-config force`** performs a **true atomic replacement** that diffs `running-config` against `startup-config` and automatically issues the `no ...` commands needed to return `running-config` to the exact saved NVRAM state without rebooting the switch or router!</p>'
    ),
})

NETOPS_TROUBLESHOOTING_TRANSCRIPTS = {
    (1, 1): (
        '<h4>Field Packet-Capture Transcript 1.1: Comparing Layer-2 Broadcast ARP vs Layer-3 Routed Unicast</h4>'
        '<p>When a workstation at `10.10.10.25/24` pings a local peer `10.10.10.90/24` on the same subnet, the bitwise AND `(10.10.10.25 & 255.255.255.0) == (10.10.10.90 & 255.255.255.0)` evaluates to `True`, so the host ARPs directly for `10.10.10.90` (`Who has 10.10.10.90? Tell 10.10.10.25`, EtherType `0x0806`) and places `10.10.10.90`\'s MAC in the Ethernet Destination MAC field. '
        'When the same host pings remote server `10.20.20.90/24`, the bitwise AND evaluates to `False`, so the host never ARPs for `10.20.20.90`; instead, it consults its routing table (`0.0.0.0/0 via 10.10.10.1`), ARPs for default gateway `10.10.10.1`, and places the gateway\'s MAC in the Ethernet Destination MAC field while keeping `10.20.20.90` in the IPv4 Destination IP field.</p>'
    ),
    (1, 2): (
        '<h4>Field Packet-Capture Transcript 1.2: Diagnosing Duplicate IPv4 (RFC 5227 ACD) &amp; IPv6 DAD Conflicts</h4>'
        '<p>When a technician statically assigns `10.10.10.50/24` to a printer without checking IPAM while DHCP already leased `10.10.10.50` to a laptop, the booting host transmits an **ARP Probe** (`Sender IP = 0.0.0.0`, `Target IP = 10.10.10.50`, RFC 5227 IPv4 Address Conflict Detection) followed by a **Gratuitous ARP Announcement** (`Sender IP = Target IP = 10.10.10.50`). '
        'When the existing owner replies with its own MAC address, Windows logs `System Event ID 4198 (Tcpip)` and falls back to `169.254.x.x`, while Linux `arping -D -I eth0 10.10.10.50` returns exit code `1` with the conflicting hardware MAC address so you can locate the port via `show mac address-table address <mac>`.</p>'
    ),
    (1, 3): (
        '<h4>Field Packet-Capture Transcript 1.3: TCP Zero-Window Stalls vs Network Packet Loss</h4>'
        '<p>Not every slow file transfer is caused by the network! If `tcpdump` on a slow SMB (`TCP 445`) transfer shows **`[TCP ZeroWindow]`** advertised by the receiving storage server followed by periodic **`[TCP WindowProbe]`** packets from the sender, the network path has zero packet loss—instead, the receiving server\'s application/disk I/O subsystem is saturated and its kernel socket receive buffer (`SO_RCVBUF`) is completely full, instructing the sender to pause transmission until a **`[TCP WindowUpdate]`** arrives.</p>'
    ),
    (1, 4): (
        '<h4>Field Packet-Capture Transcript 1.4: Interpreting Traceroute ICMP Time Exceeded &amp; Asymmetric MPLS Hops</h4>'
        '<p>Remember how `traceroute` works under the hood: Linux `traceroute` sends UDP datagrams to high ports (`33434`–`33534`) by default (or ICMP Echo with `-I`, or TCP SYN with `-T -p 443`), while Windows `tracert` sends ICMP Echo Requests, starting with **`TTL = 1`** and incrementing TTL by 1 per round. '
        'Each transit router decrements TTL to `0`, drops the packet, and generates an **ICMP Type 11 Code 0 (`Time to Live Exceeded in Transit`)** from its ingress interface IP. '
        'If Hop 4 shows `100%` packet loss (`* * *`) while Hop 5 and the final destination Hop 6 show `0%` packet loss and `4 ms` RTT, Hop 4 is NOT dropping transit traffic—Hop 4 is simply rate-limiting control-plane ICMP TTL-exceeded generation (`ip icmp rate-limit unreachable`)!</p>'
    ),
    (2, 1): (
        '<h4>Field Packet-Capture Transcript 2.1: STP Topology Change Notification (TCN) CAM Aging Storms</h4>'
        '<p>Why does enabling `spanning-tree portfast` on all user access ports improve performance across the entire VLAN? '
        'Without `portfast`, every time a desktop PC boots, reboots, or enters sleep mode, the switch treats the link transition on `Gi0/5` as a **Spanning Tree Topology Change**, generates a **TCN BPDU** toward the Root Bridge, and forces every switch in that VLAN to reduce its CAM MAC aging timer from `300 seconds` down to `Forward_Delay` (`15 seconds`)—causing periodic unknown-unicast flooding across the building whenever workstations power-cycle!</p>'
    ),
    (2, 2): (
        '<h4>Field Packet-Capture Transcript 2.2: Pruning Unused VLANs vs VTP Pruning Pitfalls</h4>'
        '<p>Manual trunk pruning (`switchport trunk allowed vlan 10,20,30`) is strongly preferred over automatic VTP pruning in enterprise networks because manual allowed lists are deterministic in `show running-config`, prevent broadcast/unknown-unicast flooding of non-local VLANs onto closet uplinks, and strictly limit the blast radius of a Layer-2 broadcast storm to switches that actually host ports in that VLAN.</p>'
    ),
    (2, 3): (
        '<h4>Field Packet-Capture Transcript 2.3: Copper Cable Shielding Ratings (UTP, F/UTP, S/FTP) &amp; Fire Codes (Plenum CMP vs Riser CMR)</h4>'
        '<p>When pulling twisted-pair cabling above drop ceilings that serve as HVAC air-handling return plenums, building fire codes (NFPA 90A / NEC Article 800) mandate **Plenum-rated (`CMP`, fluorinated ethylene propylene `FEP` low-smoke jacket)** cable rather than **Riser-rated (`CMR`, vertical shaft between floors)** or **PVC (`CM`)** cable, which releases toxic halogen smoke when burned. '
        'In high-EMI factory floors near VFDs and arc welders, replace unshielded **`UTP`** with **`F/UTP` (overall foil shield)** or **`S/FTP` (overall braid screen + individual foil per twisted pair)** terminated on grounded metallic keystone jacks so induced common-mode noise drains safely to the telecommunications main grounding busbar (`TMGB`).</p>'
    ),
    (2, 4): (
        '<h4>Field Packet-Capture Transcript 2.4: Diagnosing PoE Power Negotiation — IEEE 802.3 Classification vs LLDP-MED</h4>'
        '<p>IEEE 802.3af/at/bt Power over Ethernet negotiates power in two phases: first, **Physical Layer Classification** applies a low-voltage DC probe across the twisted pairs to detect the Powered Device\'s (`PD`) `25 kOhm` signature resistor and read its hardware current class (`Class 0`–`8`); second, once the PD boots its OS, **Layer-2 LLDP-MED (`TLV Type 127`)** negotiates fine-grained power in `0.1 Watt` increments (for example, an AP requesting `21.4 W` instead of locking an entire `30.0 W` Class 4 reservation), reclaiming unused PoE budget across the switch.</p>'
    ),
    (3, 1): (
        '<h4>Field Packet-Capture Transcript 3.1: OSPF DR/BDR Election on Broadcast Segments vs Point-to-Point Links</h4>'
        '<p>On multi-access broadcast segments (Ethernet VLANs), OSPF elects a **Designated Router (DR)** and **Backup Designated Router (BDR)** based on highest `ip ospf priority` (`1` default, `0` never becomes DR/BDR) and highest **Router-ID** (configured `router-id`, else highest Loopback IP, else highest active physical IP). '
        'Because the DR/BDR election is **non-preemptive**, adding a new router with Priority `255` will NOT unseat an existing DR until the current DR/BDR reloads or `clear ip ospf process` is executed during a maintenance window. '
        'On a 2-router point-to-point Ethernet link (`/30` or `/31`), configure **`ip ospf network point-to-point`** on both interfaces to skip the 40-second DR/BDR wait timer and converge to `FULL/-` in under 1 second.</p>'
    ),
    (3, 2): (
        '<h4>Field Packet-Capture Transcript 3.2: Diagnosing Split-Tunnel vs Full-Tunnel Remote-Access VPNs</h4>'
        '<p>On remote-access client VPNs (**IPsec IKEv2** or **TLS/DTLS OpenVPN/AnyConnect**), a **Full-Tunnel** configuration pushes default route `0.0.0.0/0` and `::/0` into the virtual tunnel adapter so 100% of employee Internet and corporate traffic passes through enterprise NGFW/SWG inspection, whereas a **Split-Tunnel** configuration pushes only specific corporate RFC 1918 routes (`10.0.0.0/8`, `172.16.0.0/12`) into the tunnel while letting high-bandwidth Zoom/Teams media egress directly out the user\'s home ISP (or uses **Split-Exclude / Dynamic FQDN Split-Tunneling** to send only verified SaaS media direct).</p>'
    ),
    (3, 3): (
        '<h4>Field Packet-Capture Transcript 3.3: 802.11 CSMA/CA, RTS/CTS Protection &amp; Airtime Fairness</h4>'
        '<p>Unlike full-duplex switched Ethernet (which uses CSMA/CD only on legacy half-duplex hubs and runs collision-free on modern full-duplex switch ports), wireless 802.11 RF is a **half-duplex shared medium** governed by **CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance)**. '
        'Before transmitting, every station performs physical energy detection and reads the **NAV (Network Allocation Vector)** duration timer in frame headers; when hidden nodes cannot hear each other across a concrete pillar, enabling **RTS/CTS (Request to Send / Clear to Send)** reserves the channel via the AP.</p>'
    ),
    (3, 4): (
        '<h4>Field Packet-Capture Transcript 3.4: Validating Post-Installation Wireless Roaming with Continuous Ping &amp; PCAP</h4>'
        '<p>When walking a floor during a post-validation survey while running a `20 ms` interval VoIP-sized ping (`ping -i 0.02 -s 160 10.20.0.10`), a properly tuned **802.11r/k/v** WPA3-Enterprise network completes an inter-AP Layer-2 roam in `< 20 ms` (`0` to `1` dropped packet) by caching the Pairwise Master Key (`PMK-R0` / `PMK-R1`) across the controller mobility group.</p>'
    ),
    (4, 1): (
        '<h4>Field Packet-Capture Transcript 4.1: Resolving PXE Network Boot Failures — DHCP Options 60, 66, 67 &amp; UEFI HTTP Boot</h4>'
        '<p>When imaging bare-metal workstations over the network via **PXE (Preboot Execution Environment)** or **UEFI HTTP Boot**, the NIC firmware completes a standard DHCPv4 DORA exchange and inspects **Option 66 (`TFTP Boot Server Host Name/IP`)** and **Option 67 (`Bootfile Name`, e.g., `boot\\x64\\wdsmgfw.efi`)**. '
        'If the PXE/WDS imaging server runs on a different subnet from the DHCP server, prefer configuring a second **`ip helper-address <pxe-server-ip>`** on the router SVI rather than hardcoding static Options 66/67 so the PXE server can dynamically respond to both Legacy BIOS and UEFI x64/ARM64 client architecture tags (`Option 93`).</p>'
    ),
    (4, 2): (
        '<h4>Field Packet-Capture Transcript 4.2: Diagnosing EDNS0 UDP Payload Size Drops &amp; TCP 53 Fallback</h4>'
        '<p>Classic DNS (RFC 1035) limited UDP DNS packets to `512 bytes`. Modern DNSSEC-signed responses (`RRSIG` + `DNSKEY`) and multi-record answers use **EDNS0 (RFC 6891)** to advertise a `1232-byte` or `4096-byte` UDP payload buffer. '
        'If a legacy perimeter firewall inspects UDP 53 and drops DNS packets larger than 512 bytes *and* blocks **TCP Port 53**, any query whose reply sets the **`TC=1` (Truncated)** flag fails completely when the resolver attempts to retry over TCP 53! Always permit both **UDP 53 and TCP 53** to authoritative and recursive DNS servers.</p>'
    ),
    (4, 3): (
        '<h4>Field Packet-Capture Transcript 4.3: Carrier-Grade NAT (CGNAT 100.64.0.0/10) &amp; Why Inbound Port Forwarding Fails</h4>'
        '<p>When a branch office orders a low-cost cellular 5G or broadband circuit and configures an IPsec VPN responder or inbound HTTPS port forward on the router\'s WAN interface, why do inbound connections never reach the WAN interface when the WAN IP reads **`100.84.12.99`**? '
        'Because **`100.64.0.0/10` (`100.64.0.0`–`100.127.255.255`, RFC 6598)** is **Shared Address Space for Carrier-Grade NAT (CGNAT)**: the ISP is performing a second layer of PAT upstream in the carrier core! '
        'To host inbound IPsec or HTTPS services on that circuit, either request a static public IPv4/IPv6 address from the carrier or have the CGNAT branch router initiate outbound IKEv2 NAT-T (`UDP 4500`) connections to a hub with a public IP.</p>'
    ),
    (4, 4): (
        '<h4>Field Packet-Capture Transcript 4.4: Resolving Split-Horizon DNS vs Hairpin NAT After a Cloud Migration</h4>'
        '<p>Whenever an internal server is migrated to a cloud VPC or DMZ behind a public DNS hostname, always verify both the **External Public DNS View** and the **Internal Split-Horizon Active Directory DNS Zone**! '
        'If the public DNS zone is updated to the new IP while the internal AD-integrated zone still holds the old RFC 1918 `A` record, external users succeed while internal headquarters users remain pointed at the decommissioned server.</p>'
    ),
    (5, 1): (
        '<h4>Field Packet-Capture Transcript 5.1: Distinguishing RSPAN vs ERSPAN for Remote Packet Analysis</h4>'
        '<p>When a network engineer needs to capture packets from an access switch in Building 4 without walking to the closet: '
        '**Local SPAN** mirrors frames from source ports to a destination port on the *same* physical switch; '
        '**RSPAN (Remote SPAN)** carries mirrored frames across Layer-2 inter-switch trunks inside a dedicated `remote-span` VLAN; and '
        '**ERSPAN (Encapsulated Remote SPAN)** wraps the mirrored Ethernet frames inside a **GRE (IP Protocol 47)** tunnel and routes them across any Layer-3 IPv4/IPv6 network directly to a central Wireshark analysis VM or IDS appliance.</p>'
    ),
    (5, 2): (
        '<h4>Field Packet-Capture Transcript 5.2: Role-Based Access Control (RBAC), Privilege Levels &amp; Parser Views</h4>'
        '<p>Instead of sharing Privilege Level 15 (`enable`) root access with Tier-1 help-desk technicians, Cisco IOS **Role-Based CLI Access (Parser Views)** and **TACACS+ Command Authorization** enforce **Least Privilege** and **Separation of Duties**: '
        'a `TIER1_HELPDESK` view grants only `show interfaces`, `show vlan brief`, `show mac address-table`, and `ping`, while blocking `configure terminal`, `write erase`, and `reload`.</p>'
    ),
    (5, 3): (
        '<h4>Field Packet-Capture Transcript 5.3: East-West Lateral Movement Detection via NetFlow &amp; SIEM Correlation</h4>'
        '<p>Because East-West traffic between two hosts in the same `/24` VLAN is switched at Layer 2 without crossing the perimeter Layer-3 firewall, blinding the SOC to same-VLAN lateral movement is a major security gap. '
        'Exporting **Flexible NetFlow / IPFIX** directly from access-switch ASICs (`ip flow monitor EAST_WEST_MON input`) and enforcing **802.1X dACLs / PVLAN isolation** gives the SIEM immediate visibility into any workstation scanning TCP 445 or TCP 3389 across the closet switch.</p>'
    ),
    (5, 4): (
        '<h4>Field Packet-Capture Transcript 5.4: Verifying Dynamic ARP Inspection (DAI) &amp; Static ARP ACLs for Non-DHCP Servers</h4>'
        '<p>When you enable **Dynamic ARP Inspection (`ip arp inspection vlan 20`)** on a server VLAN where database servers use **static IPv4 addresses** instead of DHCP leases, why do those static servers suddenly lose network connectivity? '
        'Because DAI validates ARP packets against the **DHCP Snooping Binding Database**, and a statically addressed server has no DHCP snooping lease entry! '
        'Before enabling DAI on a VLAN with static IPs, either create a static **`arp access-list STATIC_SERVERS`** (`permit ip host 10.20.20.50 mac host 0050.569a.0050`) applied via `ip arp inspection filter STATIC_SERVERS vlan 20`, or convert those servers to **DHCP Reservations** so they populate the snooping table automatically.</p>'
    ),
    (6, 1): (
        '<h4>Field Packet-Capture Transcript 6.1: Optical Power Budget Math — Calculating Link Margin in dB</h4>'
        '<p>On N10-009, calculate optical link margin by subtracting total passive plant loss from available transmitter-to-receiver dynamic range: '
        'if a `10GBASE-LR` (1310 nm Single-Mode) SFP+ transmits at **`-1.0 dBm`** and its receiver sensitivity floor is **`-14.0 dBm`** (a `13.0 dB` gross link budget), and the 10 km fiber span includes `10 km * 0.35 dB/km = 3.5 dB` fiber attenuation, `4` mated LC patch panel connectors (`4 * 0.50 dB = 2.0 dB`), and `2` fusion splices (`2 * 0.10 dB = 0.2 dB`) for a total insertion loss of **`5.7 dB`**, the expected received power at the far-end SFP+ is `-1.0 dBm - 5.7 dB = -6.7 dBm`, leaving a healthy **`7.3 dB` operating margin** above `-14.0 dBm`.</p>'
    ),
    (6, 2): (
        '<h4>Field Packet-Capture Transcript 6.2: Escalation Hand-Off Packet — What Tier 3 &amp; Carrier TAC Require</h4>'
        '<p>When escalating a circuit or routing fault after exhausting local theories, package five artifacts in the escalation ticket: '
        '(1) Exact UTC timestamps (NTP-synced) of fault onset; (2) Circuit ID / Demarc NIU loop status and optical DOM readings (`Tx/Rx dBm`); (3) Bidirectional `mtr`/`traceroute` and `ping` loss percentages; (4) `show interfaces` error counters and `show logging` excerpt; and (5) Exact list of tests already executed so Tier 3 never repeats Tier 1 steps.</p>'
    ),
    (6, 3): (
        '<h4>Field Packet-Capture Transcript 6.3: Auditing Cable Plant Labels (TIA-606-C) &amp; Rack Unit (RU) Elevations</h4>'
        '<p>Following **ANSI/TIA-606-C** administration standards, every horizontal cable, patch panel port, fiber cassette, and switch uplink label encodes both ends of the link (`1A-IDF2-B04 <-> 1A-R214-D04`), and rack elevation diagrams track standard **19-inch EIA-310 rack units (`1 RU = 1.75 inches / 44.45 mm`, typically 42U or 48U per cabinet)** along with weight load and Watt/BTU thermal dissipation (`1 Watt = 3.412 BTU/hr`).</p>'
    ),
    (6, 4): (
        '<h4>Field Packet-Capture Transcript 6.4: Final Pre-Exam N10-009 Rapid-Fire Diagnostic Checklist</h4>'
        '<p>Keep four golden rules front-of-mind across every scenario: (1) Longest-prefix match (`/27` over `/24`) ALWAYS governs packet forwarding before Administrative Distance (`Static 1` over `OSPF 110`); (2) Routers rewrite Layer-2 MACs and decrement TTL at every hop while preserving end-to-end IPs unless NAT translates them; (3) Inbound ACLs run *before* routing, outbound ACLs run *after* routing, and first-match wins above an implicit `deny ip any any`; and (4) Verification repeats the original failing user test and updates diagrams/NVRAM before ticket closure.</p>'
    ),
    (9, 1): '<p><strong>CLI Quick-Ref 9.1:</strong> `enable` -> `show version` -> `show cdp neighbors detail` -> `show lldp neighbors detail` -> `show ip interface brief`.</p>',
    (9, 2): '<p><strong>CLI Quick-Ref 9.2:</strong> `configure terminal` -> `vlan 10` -> `name USERS` -> `interface Fa0/1` -> `switchport mode access` -> `switchport access vlan 10` -> `show vlan brief`.</p>',
    (9, 3): '<p><strong>CLI Quick-Ref 9.3:</strong> `interface Gi0/0` -> `ip address 10.10.10.1 255.255.255.0` -> `no shutdown` -> `show ip interface brief` -> `show ip route connected`.</p>',
    (9, 4): '<p><strong>CLI Quick-Ref 9.4:</strong> `interface Gi0/0` -> `no shutdown` -> `interface Gi0/0.10` -> `encapsulation dot1Q 10` -> `ip address 10.10.10.1 255.255.255.0` -> `show interfaces trunk`.</p>',
    (9, 5): '<p><strong>CLI Quick-Ref 9.5:</strong> `ip route 10.50.0.0 255.255.255.0 172.16.12.2` -> `ip route 0.0.0.0 0.0.0.0 203.0.113.1` -> `show ip route static` -> `ping` / `traceroute`.</p>',
    (9, 6): '<p><strong>CLI Quick-Ref 9.6:</strong> `hostname RTR-CORE-01` -> `copy running-config startup-config` -> `show archive config differences nvram:startup-config system:running-config`.</p>',
}

for _ch9_les in range(1, 7):
    NETOPS_TROUBLESHOOTING_TRANSCRIPTS[(9, _ch9_les)] += (
        f' <p>In enterprise Closet Lab 9.{_ch9_les}, always capture pre-change and post-change state using '
        '<code>show ip interface brief</code>, <code>show vlan brief</code>, <code>show interfaces trunk</code>, '
        '<code>show spanning-tree summary</code>, and <code>show ip route</code> so every Layer-1 physical carrier, '
        'Layer-2 802.1Q VLAN tag, and Layer-3 next-hop RIB entry is documented with concrete CLI evidence before ticket closure.</p>'
    )


def _wq(ch, idx, q, correct, w1, w2, w3, w_obj, why):
    opts = [w1, w2, w3, correct]
    s = (ch + idx) % 4
    opts = opts[s:] + opts[:s]
    return {
        'text': q,
        'options': opts,
        'correct': correct,
        'lo': f'LO-NET-{ch}',
        'lo_text': f'Network Operations Chapter {ch} Scenario Mastery',
        'focus': f'Chapter {ch} N10-009 scenario analysis ({w_obj})',
        'keywords': [],
        'study_tip': why,
        'explanation': why,
        'wave1_id': f'WNQ{ch}.{idx}',
        'wave1_obj': w_obj,
    }


NETOPS_EXTRA_QUIZ_ITEMS = {
    1: [
        _wq(1, 8,
            'An IPsec GRE tunnel interface has IP MTU 1400 bytes. When an internal firewall blocks ICMP Type 3 Code 4 (Fragmentation Needed and DF Set), which failure symptom occurs for remote branch users?',
            'Small pings and SSH handshakes succeed, but TLS certificate exchanges and bulk file transfers stall silently',
            'All ICMP Echo Requests fail while large HTTPS downloads complete at full line rate',
            'The branch switch places the tunnel interface into err-disabled state due to BPDU Guard',
            'Workstations immediately release their DHCPv4 leases and fall back to 169.254.0.0/16 APIPA addresses',
            'NO-1.1',
            'Blocking ICMP Type 3 Code 4 breaks Path MTU Discovery (PMTUD, RFC 1191): small packets under 1400 bytes pass, while 1500-byte DF-set TLS/SMB segments are dropped without notifying the sender to clamp TCP MSS.'),
        _wq(1, 9,
            'An architect subnets 172.16.40.0/22 to create a point-to-point router transit link using RFC 3021 (/31) and a management segment using /28. How many usable host addresses does the /28 subnet provide?',
            '14 usable host addresses (block size 16 minus network and broadcast)',
            '16 usable host addresses because /28 suppresses the broadcast address',
            '30 usable host addresses across a 32-address fourth-octet block',
            '6 usable host addresses across an 8-address fourth-octet block',
            'NO-1.2',
            'A /28 leaves 4 host bits (32 - 28 = 4): 2^4 = 16 total addresses minus the network ID and directed broadcast address yields 14 usable hosts.'),
        _wq(1, 10,
            'On a dual-stack IPv6 VLAN, a Linux host transmits an ICMPv6 Type 133 Router Solicitation to ff02::2 and receives a Type 134 Router Advertisement with flags A=1, M=0, O=1. How does the host configure its networking?',
            'It generates its own /64 global IPv6 address via SLAAC and queries Stateless DHCPv6 on UDP 546/547 for DNS options',
            'It ignores the prefix in the Router Advertisement and waits for a Stateful DHCPv6 server to assign its IPv6 address',
            'It uses ARP broadcasts on FF:FF:FF:FF:FF:FF to resolve the default gateway MAC address',
            'It assigns itself an IPv4 100.64.0.0/10 CGNAT address and disables IPv6 neighbor discovery',
            'NO-1.2',
            'In ICMPv6 NDP (RFC 4861/4862), A=1 enables autonomous SLAAC address generation, M=0 disables stateful DHCPv6 address leasing, and O=1 directs the client to fetch Other configuration (DNS/domain) via Stateless DHCPv6.'),
        _wq(1, 11,
            'Running ss -tan on an application server shows dozens of outbound connections to 10.80.10.25:636 stuck in SYN-SENT state. What does SYN-SENT prove?',
            'The local kernel transmitted TCP SYN packets to TCP port 636, but no SYN-ACK or RST response returned across the path',
            'The remote LDAPS server completed the 3-way handshake and is waiting for the local application to close its file descriptor',
            'UDP port 636 is open, but the local DNS stub resolver returned NXDOMAIN for the hostname',
            'The physical NIC link partner negotiated 100 Mbps half-duplex and dropped Layer-2 framing',
            'NO-1.3',
            'SYN-SENT means the outbound TCP SYN left the socket, but neither a SYN-ACK nor a TCP RST returned—pointing to a silent firewall drop, routing black hole, or asymmetric return path on TCP 636.'),
    ],
    2: [
        _wq(2, 8,
            'Two distribution switches are linked via two 10GBASE-SR fiber pairs configured with channel-group 1 mode passive on BOTH switches. What is the operational result in show etherchannel summary?',
            'The LACP port-channel fails to bundle because both sides wait passively for the peer to initiate LACPDUs',
            'Both links bundle immediately into an active 20 Gbps IEEE 802.3ad LACP trunk',
            'Spanning Tree Protocol disables both switches permanently with a VTP revision mismatch',
            'The switches automatically convert the fiber links into a Layer-3 OSPF point-to-point subnet',
            'NO-2.1',
            'In IEEE 802.3ad LACP, Passive/Passive never transmits an initial LACPDU; at least one side must be set to Active (Active/Active or Active/Passive) to negotiate the bundle.'),
        _wq(2, 9,
            'An engineer runs show interfaces trunk on SW-ACC-02 and sees VLAN 40 listed under "Vlans allowed on trunk" for Gi0/1, but VLAN 40 is missing from "Vlans allowed and active in management domain." What is the root cause?',
            'VLAN 40 has not been created in the local switch VLAN database (vlan.dat) or is currently in shutdown state',
            'The native VLAN on Gi0/1 is encrypting VLAN 40 frames with WPA3-Enterprise',
            'The router subinterface Gi0/0.40 has an administrative distance higher than 110',
            'PortFast was enabled on the access ports in VLAN 10',
            'NO-2.2',
            'Permitting a VLAN on a trunk allowed list does not create the VLAN; if VLAN 40 is absent from show vlan brief (or shut down), it will not appear in the active trunk forwarding list.'),
        _wq(2, 10,
            'A new Wi-Fi 6E access point requiring 28 W (IEEE 802.3at Class 4) fails to power up when patched into Gi0/18. Running show power inline shows Module 1 Available: 370.0 W, Used: 356.0 W, Remaining: 14.0 W. What is the cause?',
            'The switch PoE power budget is exhausted (only 14.0 W remains, below the 30.0 W PSE allocation required for Class 4)',
            'Cat6A copper cabling cannot carry DC phantom power beyond 15 meters',
            'The access port is missing the switchport nonegotiate command',
            'The switch CAM table has aged out the access point MAC address after 300 seconds',
            'NO-2.3',
            'An IEEE 802.3at (PoE+) Class 4 device requires up to 30 W at the switch PSE port (25.5 W at the PD); with only 14 W remaining in the 370 W PoE budget, the switch denies power.'),
        _wq(2, 11,
            'An access port Gi0/12 configured with spanning-tree portfast and spanning-tree bpduguard enable suddenly changes to err-disabled (bpduguard) status. What happened at the wall jack?',
            'Someone connected a switch or bridge that transmitted an IEEE 802.1D/802.1w BPDU into port Gi0/12',
            'A desktop PC sent a DHCPDISCOVER broadcast packet with source IP 0.0.0.0',
            'A user opened an HTTPS website whose TLS certificate had expired',
            'The horizontal Cat6 run between the patch panel and wall jack is 65 meters long',
            'NO-2.1',
            'BPDU Guard immediately places a PortFast edge port into err-disabled state if any Spanning Tree Bridge Protocol Data Unit (BPDU) arrives on that port.'),
    ],
    3: [
        _wq(3, 8,
            'A core router has three routes in its routing table: 10.40.0.0/16 via Static (AD 1), 10.40.20.0/24 via EIGRP (AD 90), and 10.40.20.128/26 via OSPF (AD 110). Which path does the router choose for a packet destined to 10.40.20.150?',
            'The OSPF route 10.40.20.128/26 because Longest-Prefix Match (/26) always wins before Administrative Distance',
            'The Static route 10.40.0.0/16 because Administrative Distance 1 beats EIGRP 90 and OSPF 110',
            'The EIGRP route 10.40.20.0/24 because DUAL composite metric overrides prefix length',
            'The router drops the packet and returns ICMP Type 11 Time Exceeded',
            'NO-3.1',
            'Host IP 10.40.20.150 falls inside 10.40.20.128/26 (.128–.191); routers always forward using the Longest-Prefix Match (/26 > /24 > /16) regardless of Administrative Distance.'),
        _wq(3, 9,
            'Two routers connected over GigabitEthernet0/1 remain stuck in OSPF state EXSTART/- in show ip ospf neighbor. Pings of 64 bytes between their interface IPs succeed. What is the most likely cause?',
            'An IP MTU mismatch between the two router interfaces prevents large OSPF Database Description (DBD) packets from passing',
            'Both routers are configured with the exact same DNS server IP in DHCP Option 6',
            'A static default route 0.0.0.0/0 is missing from the local routing table',
            'Port 443 is blocked on the perimeter firewall',
            'NO-3.1',
            'OSPF Database Description (DBD) packets exchanged during EXSTART/EXCHANGE check interface MTU and carry full LSA headers; a mismatched MTU causes neighbors to stall in EXSTART/EXCHANGE.'),
        _wq(3, 10,
            'An enterprise branch needs dynamic OSPF routing across an encrypted VPN tunnel over the public Internet. Which tunnel architecture supports both multicast OSPF Hellos (224.0.0.5) and payload encryption?',
            'GRE over IPsec (encapsulating multicast/unicast inside GRE IP Protocol 47, then encrypting with IPsec ESP IP Protocol 50)',
            'An unencrypted VLAN 802.1Q trunk patched directly into the ISP broadband modem',
            'SNMPv2c trap forwarding over UDP port 162',
            'Static Port Address Translation (PAT) on UDP port 53',
            'NO-3.2',
            'GRE (IP Protocol 47) encapsulates multicast routing protocols (OSPF 224.0.0.5) inside point-to-point tunnel packets, and IPsec (IKEv2 + ESP) encrypts the GRE tunnel over the public Internet.'),
        _wq(3, 11,
            'During an auditorium Wi-Fi upgrade, 5 GHz access points on Channel 52 (UNII-2) abruptly switch to Channel 149 for 30 minutes whenever nearby airport weather radar operates. Which mechanism caused this channel change?',
            'Dynamic Frequency Selection (DFS), which vacates UNII-2/2e channels upon detecting incumbent radar pulses',
            'WPA3 Simultaneous Authentication of Equals (SAE) key rotation',
            'Spanning Tree Root Guard blocking superior BPDUs on the wired switch',
            'DHCP Snooping rate-limiting untrusted ports at 15 packets per second',
            'NO-3.3',
            'Channels 52–144 lie in the 5 GHz UNII-2/2e DFS spectrum; regulatory rules mandate that APs detect radar and vacate the channel within 10 seconds for a 30-minute non-occupancy period.'),
    ],
}

NETOPS_EXTRA_QUIZ_ITEMS.update({
    4: [
        _wq(4, 8,
            'After enabling ip dhcp snooping on VLAN 20, clients on access ports Fa0/2–Fa0/24 stop receiving DHCP leases even though the central DHCP server is online and reachable via Gi0/1. What was missed on uplink port Gi0/1?',
            'Configuring ip dhcp snooping trust on the uplink port Gi0/1 toward the DHCP server/relay',
            'Setting switchport port-security violation shutdown on the uplink trunk',
            'Configuring an MX record for the DHCP server in the reverse DNS zone',
            'Changing the DHCP server port from UDP 67 to TCP 443',
            'NO-4.1',
            'DHCP Snooping sets all ports to untrusted by default (dropping ingress DHCPOFFER/DHCPACK packets); the uplink toward the legitimate DHCP server or relay must be configured with ip dhcp snooping trust.'),
        _wq(4, 9,
            'Running dig @10.100.10.53 payroll.novak.internal returns status: SERVFAIL when DNSSEC validation is enabled, but succeeds when +cd (Checking Disabled) is passed. What does this prove?',
            'DNSSEC cryptographic signature validation (RRSIG / DS / DNSKEY chain) failed or expired for that zone',
            'The workstation lacks a default gateway in DHCP Option 3',
            'The physical Ethernet cable on the DNS server is unplugged',
            'The query name does not exist in the zone (NXDOMAIN)',
            'NO-4.2',
            'When a query fails with SERVFAIL normally but succeeds with +cd (Checking Disabled), the recursive resolver reached the server, but DNSSEC validation of the RRSIG/DNSKEY/DS chain failed.'),
        _wq(4, 10,
            'A newly added VLAN 40 (10.40.0.0/24) can ping all internal VLANs and the perimeter router inside IP (10.255.0.1), but cannot ping 8.8.8.8. VLANs 10, 20, and 30 reach 8.8.8.8 normally. What is the most likely omission on the perimeter router?',
            'The 10.40.0.0/24 subnet was not added to the standard ACL referenced by the ip nat inside source list overload command',
            'VLAN 40 hosts are using TCP port 443 instead of TCP port 80',
            'The perimeter router has ip routing enabled globally',
            'Spanning Tree PortFast is enabled on VLAN 40 workstation ports',
            'NO-4.3',
            'If a new internal subnet routes to the edge router but is omitted from the NAT overload (PAT) ACL, its packets egress onto the WAN with untranslated RFC 1918 source IPs and are dropped by the ISP.'),
        _wq(4, 11,
            'An external customer connects to https://203.0.113.25:443, and the perimeter firewall translates the destination IP to DMZ web server 172.16.10.25:443. Which NAT type is performing this inbound translation?',
            'Destination NAT (DNAT / Static Port Forwarding) into a Screened Subnet (DMZ)',
            'Dynamic APIPA link-local autoconfiguration on the WAN interface',
            'IPv6 Stateless Address Autoconfiguration (SLAAC) with EUI-64',
            'Outbound Port Address Translation (PAT) for internal workstations',
            'NO-4.3',
            'Rewriting a public VIP/port (203.0.113.25:443) to an internal DMZ server private IP/port (172.16.10.25:443) for inbound requests is Destination NAT (DNAT / port forwarding).'),
    ],
    5: [
        _wq(5, 8,
            'A 10 Gbps core switch uplink stepping down to a 1 Gbps branch circuit shows 0 CRC errors and 0 input errors, but rapidly climbing Total output drops during backup windows. What does this indicate?',
            'Egress queue congestion caused by a 10 Gbps-to-1 Gbps speed step-down exceeding interface buffer capacity',
            'A cracked multimode fiber core or dirty LC optical ferrule on the ingress strand',
            'An IPv4 duplicate address conflict on the management loopback interface',
            'A missing TACACS+ shared secret on the VTY lines',
            'NO-5.1',
            'Zero input/CRC errors prove the physical medium is clean; rising output drops occur when bursty traffic from a faster link (10G) overflows the egress queue buffers of a slower link (1G).'),
        _wq(5, 9,
            'Which AAA protocol encrypts the ENTIRE packet payload (including command arguments) over TCP port 49 and separates Authentication, Authorization, and Accounting for network device CLI administration?',
            'TACACS+ (RFC 8907)',
            'SNMPv2c over UDP port 161',
            'Plaintext Telnet over TCP port 23',
            'Syslog over UDP port 514',
            'NO-5.2',
            'TACACS+ uses TCP port 49, encrypts the entire AAA packet body, and provides granular per-command authorization and audit accounting for router/switch CLI administration.'),
        _wq(5, 10,
            'In a data center VLAN where 40 payment servers share subnet 10.50.0.0/24, security policy requires that servers communicate ONLY with the default gateway firewall (10.50.0.1) and never directly with each other at Layer 2. Which feature enforces this?',
            'Private VLAN (PVLAN) Isolated ports bound to a Promiscuous gateway port',
            'Enabling CDP and LLDP on all server switchports',
            'Setting VTP mode to server with a shared domain password',
            'Increasing the CAM MAC aging timer from 300 seconds to 3600 seconds',
            'NO-5.3',
            'PVLAN Isolated ports (RFC 5517) block all Layer-2 East-West communication between hosts in the same subnet while allowing traffic to and from the Promiscuous default gateway port.'),
        _wq(5, 11,
            'An attacker on access port Gi0/11 sends gratuitous ARP replies claiming that default gateway 10.10.10.1 is at the attacker’s own NIC MAC address. Why does Dynamic ARP Inspection (DAI) block this attack when Port Security alone does not?',
            'DAI inspects the ARP payload (Sender IP + Sender MAC) against the trusted DHCP Snooping Binding Database and drops mismatched claims',
            'DAI encrypts all Ethernet frames with WPA3-Personal SAE',
            'DAI disables IPv4 routing across the entire autonomous system',
            'DAI changes the physical cable category from Cat5e to OS2 single-mode fiber',
            'NO-5.2',
            'Port security checks only the Layer-2 Ethernet Source MAC header (which matches the attacker’s valid NIC); DAI inspects the ARP packet body and drops any ARP reply whose Sender IP does not match the DHCP Snooping lease table.'),
    ],
    6: [
        _wq(6, 8,
            'Workstations on VLAN 40 experience 45% packet loss when pinging default gateway 10.40.0.1, while pings between workstations on VLAN 40 have 0% loss. Running show standby brief on both core switches shows BOTH switches in State: Active for Group 40. What caused this split-brain?',
            'VLAN 40 is blocked or missing on the Layer-2 trunk between the two core switches, preventing HSRP multicast Hellos from being heard',
            'The workstation DNS cache contains an expired CNAME record',
            'The ISP BGP peer prepended its AS_PATH three times',
            'SNMPv3 authPriv encryption was enabled on the management VLAN',
            'NO-6.1',
            'When HSRP/VRRP peers cannot hear each other’s Layer-2 multicast Hellos across the inter-switch trunk, the Standby router promotes itself to Active—causing dual Active virtual MAC flapping.'),
        _wq(6, 9,
            'A 100 Mbps copper link between a router (configured with speed 100 and duplex full) and an access switch (configured with speed auto and duplex auto) suffers severe throughput degradation. What duplex state did the switch port select, and what counters increment?',
            'The auto switch port fell back to 100 Mbps Half-Duplex (parallel detection without FLP autonegotiation), causing late collisions on the switch and FCS/CRC errors on the router',
            'The switch port negotiated 10 Gbps Full-Duplex and enabled LACP automatically',
            'Both ports shut down into err-disabled psecure-violation state',
            'The router automatically converted the copper port into an 850 nm multimode fiber link',
            'NO-6.1',
            'Hardcoding speed/duplex disables Fast Link Pulse (FLP) autonegotiation; per IEEE 802.3u parallel detection, the auto peer detects 100 Mbps carrier without autonegotiation and defaults to Half-Duplex.'),
        _wq(6, 10,
            'During a scheduled maintenance window, an OSPF change on RTR-CORE-01 unexpectedly drops branch routes. Which command atomically reverts running-config in RAM back to the saved startup-config in NVRAM without rebooting the router?',
            'configure replace nvram:startup-config force',
            'copy startup-config running-config',
            'erase startup-config',
            'show archive config differences',
            'NO-6.2',
            'Unlike copy startup-config running-config (which only merges lines additively), configure replace nvram:startup-config force diffs the configurations and removes any lines added since boot.'),
        _wq(6, 11,
            'A mission-critical hospital network SLA requires "Five Nines" (99.999%) annual availability. Approximately how much total unplanned downtime per year does 99.999% availability permit?',
            'About 5.26 minutes per year',
            'About 8.76 hours per year (which corresponds to 99.9% Three Nines)',
            'About 3.65 days per year (which corresponds to 99.0% Two Nines)',
            'Zero milliseconds over a 10-year hardware lifecycle',
            'NO-6.3',
            '365.25 days x 1,440 minutes/day = 525,960 minutes/year; 0.001% (1 - 0.99999) of 525,960 minutes is 5.26 minutes per year.'),
    ],
    9: [
        _wq(9, 8,
            'An engineer connects a laptop to a switch RJ-45 console port using a rollover cable, opens a terminal emulator, and sees garbled characters on screen. Which standard serial parameters should be verified first?',
            '9600 baud, 8 data bits, no parity, 1 stop bit, no flow control (9600-8-N-1)',
            'UDP port 161 with SNMPv3 SHA-256 and AES-128 encryption',
            'IEEE 802.1Q TPID 0x8100 with Native VLAN 99',
            'OSPF Area 0 with Hello timer 10 seconds and Dead timer 40 seconds',
            'NO-9.1',
            'Standard Cisco IOS RS-232/USB serial console ports default to 9600 bps, 8 data bits, no parity, 1 stop bit, and no flow control (9600-8-N-1); a mismatched baud rate produces garbled text.'),
        _wq(9, 9,
            'On switch SW1, an engineer runs no vlan 20 in global configuration mode while FastEthernet0/5 is still configured with switchport access vlan 20. How does FastEthernet0/5 behave until reconfigured?',
            'FastEthernet0/5 becomes an orphaned (inactive) port and drops all traffic until VLAN 20 is recreated or the port is reassigned to an active VLAN',
            'FastEthernet0/5 automatically converts into an 802.1Q trunk port allowing all VLANs',
            'FastEthernet0/5 automatically moves itself into VLAN 1 and begins routing OSPF',
            'The switch erases its NVRAM startup-config and reboots into ROMMON',
            'NO-9.1',
            'Deleting a VLAN while access ports remain assigned to it leaves those ports in an inactive (amber) state; they do not revert to VLAN 1 automatically.'),
        _wq(9, 10,
            'When configuring Router-on-a-Stick on GigabitEthernet0/0.10, typing ip address 10.10.10.1 255.255.255.0 is rejected with "% Configuring IP routing on a LAN subinterface is only allowed if that subinterface is already configured as part of an IEEE 802.1Q... vLAN." What must be entered first?',
            'encapsulation dot1Q 10 on subinterface GigabitEthernet0/0.10',
            'switchport mode access on physical interface GigabitEthernet0/0',
            'ip helper-address 10.10.10.1 in global configuration mode',
            'spanning-tree portfast on subinterface GigabitEthernet0/0.10',
            'NO-9.2',
            'IOS requires encapsulation dot1Q <vlan-id> on a router subinterface before it will accept an IPv4 address assignment.'),
        _wq(9, 11,
            'An engineer configures ip route 10.50.0.0 255.255.255.0 172.16.12.2 on RTR1 and confirms the command appears in show running-config, yet show ip route static is completely empty. What is the cause?',
            'The local exit interface toward 172.16.12.2 (subnet 172.16.12.0/30) is currently down or administratively shut down, so the next hop is unresolvable',
            'Static routes have an Administrative Distance of 255 by default',
            'The router hostname has not been changed from the default Router prompt',
            'copy running-config startup-config must be run before routes enter the RIB',
            'NO-9.2',
            'A static route is only installed into the active Routing Information Base (show ip route) when its next-hop IP address is reachable through an active (up/up) local interface.'),
    ],
})


def apply_depth_wave1(pack, course='NETOPS'):
    """Inject SVG technical architecture diagrams (ITSUP, NETOPS, CLIENT) and Wave-1 N10-009 depth sections (NETOPS).
    Uses <div class="novak-depth-wave1"> outside <section class="sublesson ..."> and before #cert-supplement-* so
    explanation-ladder section SHAs (curriculum_v2/ladder/sections.py) and test_cert_alignment.py stay 100% intact.
    """
    for ch in pack:
        ch_order = int(ch.get('order') or 0)
        for les in ch.get('lessons', []):
            les_order = int(les.get('order') or 0)
            html = les.get('html') or ''
            if 'class="novak-depth-wave1"' in html:
                continue
            blocks = []
            diag_key = LESSON_DIAGRAM_MAP.get((course, ch_order, les_order))
            if diag_key and diag_key in SVG_DIAGRAMS:
                fig_html = SVG_DIAGRAMS[diag_key]
                fig_id = f'novak-svg-{diag_key.replace("_", "-")}'
                if fig_id not in html:
                    blocks.append(fig_html)
            if course == 'NETOPS':
                key = (ch_order, les_order)
                for dct in (
                    NETOPS_DEPTH_HTML,
                    NETOPS_CASE_STUDIES,
                    NETOPS_FIELD_DRILLS,
                    NETOPS_ARCHITECTURE_LABS,
                    NETOPS_TROUBLESHOOTING_TRANSCRIPTS,
                ):
                    if key in dct:
                        blocks.append(dct[key])
            if not blocks:
                continue
            wrapper = f'\n<div class="novak-depth-wave1" data-wave="1">{"".join(blocks)}</div>\n'
            cert_idx = html.find('<section id="cert-supplement-')
            if cert_idx != -1:
                les['html'] = html[:cert_idx] + wrapper + html[cert_idx:]
            else:
                les['html'] = html + wrapper


def netops_quiz_12_payload(order):
    """Return the 12-item NETOPS chapter quiz payload (8 core NETOPS_CHECKS + 4 Wave-1 scenario items) for DB seeding."""
    from .netops_checks import netops_quiz_payload
    base = list(netops_quiz_payload(order))
    extra = [dict(q) for q in NETOPS_EXTRA_QUIZ_ITEMS.get(order, [])]
    return (base + extra)[:12]


def _build_wave1_test_padding():
    """Build deterministic, non-overlapping 45-question padding pools for ITSUP and NETOPS Knowledge Tests B & C."""
    from .itsup_core import EXPANSION
    from .exam_supplement import SUPPLEMENT
    from .cert.items import CERT_ITEMS
    it_pool, no_pool = [], []
    for src in (EXPANSION, SUPPLEMENT, CERT_ITEMS):
        for q in src:
            if (q.get('type') or 'single') != 'single':
                continue
            opts = list(q.get('options') or [])
            correct = q.get('correct')
            if len(opts) != 4 or correct not in opts:
                continue
            obj = str(q.get('obj') or '')
            item = {
                'text': q.get('text') or q.get('q') or '',
                'options': opts,
                'correct': correct,
                'lo': f'LO-{obj}' if obj else 'LO-GEN',
                'lo_text': f'CompTIA Aligned Scenario ({obj})',
                'to': f'LO-{obj}: CompTIA Aligned Scenario ({obj})',
                'category': 'Networking' if obj.startswith('NO-') else 'Core Knowledge',
                'explanation': q.get('explanation') or q.get('why') or '',
                'study_tip': q.get('explanation') or q.get('why') or '',
                'wave1_id': q.get('bank_id') or '',
                'wave1_obj': obj,
            }
            if obj.startswith('IT-'):
                it_pool.append(item)
            elif obj.startswith('NO-'):
                no_pool.append(item)
    return it_pool, no_pool


def ensure_wave1_db_assessments(db, Course, Module, Quiz, KnowledgeTest, TestAttempt=None):
    """Ensure all 7 NETOPS chapter quizzes have 12 questions (84 total) and ITSUP/NETOPS Knowledge Tests A/B/C
    each have 45 questions (135 per course), without altering static module lists or misconception coverage counts."""
    import re

    def _stem_key(s):
        return ' '.join(re.findall(r'[a-z0-9]+', (s or '').lower()))

    net = Course.query.filter_by(code='NETOPS').first() or Course.query.filter_by(code='NETPLUS').first()
    aplus = Course.query.filter_by(code='ITSUP').first() or Course.query.filter_by(code='APLUS').first()

    # 1. Expand all 7 NETOPS chapter quizzes to 12 questions per chapter (84 total)
    if net:
        for mod in Module.query.filter_by(course_id=net.id).order_by(Module.order).all():
            if mod.order not in NETOPS_EXTRA_QUIZ_ITEMS:
                continue
            qz = Quiz.query.filter_by(module_id=mod.id).order_by(Quiz.id).first()
            if qz:
                qs = netops_quiz_12_payload(mod.order)
                qz.questions = json.dumps(qs)

    # Collect all quiz stems so KnowledgeTest items never overlap a quiz stem
    quiz_stems = set()
    for qz in Quiz.query.all():
        for it in json.loads(qz.questions or '[]'):
            quiz_stems.add(_stem_key(it.get('text') or it.get('q') or ''))

    it_pool, no_pool = _build_wave1_test_padding()

    # 2. Expand ITSUP Knowledge Tests A, B, C (orders 1, 2, 3) to 45 questions each (135 total)
    if aplus:
        kts_it = {
            kt.order: kt
            for kt in KnowledgeTest.query.filter_by(course_id=aplus.id).filter(KnowledgeTest.order.in_([1, 2, 3])).all()
        }
        used_it = set(quiz_stems)
        for o in (1, 2, 3):
            if o in kts_it:
                for q in json.loads(kts_it[o].questions or '[]'):
                    used_it.add(_stem_key(q.get('text') or ''))
        it_cursor = 0
        for o in (1, 2, 3):
            kt = kts_it.get(o)
            if not kt:
                continue
            qs = json.loads(kt.questions or '[]')
            if len(qs) > 45:
                qs = qs[:45]
            while len(qs) < 45 and it_cursor < len(it_pool):
                cand = it_pool[it_cursor]
                it_cursor += 1
                sk = _stem_key(cand['text'])
                if sk in used_it:
                    continue
                used_it.add(sk)
                qs.append(cand)
            kt.questions = json.dumps(qs)
            kt.description = (kt.description or '').replace('50 questions', '45 questions')

    # 3. Expand NETOPS Knowledge Tests A, B, C (orders 1, 2, 3) to 45 questions each (135 total)
    if net:
        kts_no = {
            kt.order: kt
            for kt in KnowledgeTest.query.filter_by(course_id=net.id).filter(KnowledgeTest.order.in_([1, 2, 3])).all()
        }
        # If Form A has 47 items (e.g. N2.9 and N2.13 at indices 45, 46), move overflow items with bank_id to Form B
        overflow = []
        if 1 in kts_no:
            qs_a = json.loads(kts_no[1].questions or '[]')
            if len(qs_a) > 45:
                overflow = qs_a[45:]
                kts_no[1].questions = json.dumps(qs_a[:45])
        if 2 in kts_no and overflow:
            qs_b = json.loads(kts_no[2].questions or '[]')
            existing_bids = {q.get('bank_id') for q in qs_b if q.get('bank_id')}
            added_indices = []
            for ov in overflow:
                if ov.get('bank_id') not in existing_bids:
                    added_indices.append((len(qs_b), ov.get('correct')))
                    qs_b.append(ov)
            kts_no[2].questions = json.dumps(qs_b)
            if TestAttempt is not None and added_indices:
                for ta in TestAttempt.query.filter_by(test_id=kts_no[2].id).all():
                    try:
                        ans = json.loads(ta.answers or '{}')
                    except Exception:
                        ans = {}
                    for idx_pos, corr_val in added_indices:
                        ans.setdefault(str(idx_pos), corr_val)
                    ta.answers = json.dumps(ans)

        used_no = set(quiz_stems)
        for o in (1, 2, 3):
            if o in kts_no:
                for q in json.loads(kts_no[o].questions or '[]'):
                    used_no.add(_stem_key(q.get('text') or ''))
        no_cursor = 0
        for o in (1, 2, 3):
            kt = kts_no.get(o)
            if not kt:
                continue
            qs = json.loads(kt.questions or '[]')
            while len(qs) < 45 and no_cursor < len(no_pool):
                cand = no_pool[no_cursor]
                no_cursor += 1
                sk = _stem_key(cand['text'])
                if sk in used_no:
                    continue
                used_no.add(sk)
                qs.append(cand)
            kt.questions = json.dumps(qs)
            kt.description = (kt.description or '').replace('50 questions', '45 questions')

    db.session.commit()
