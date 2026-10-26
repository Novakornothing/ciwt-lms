"""Ten annotated, interactive SVG technical architecture diagrams for Novak LMS™ (ITSUP, NETOPS, CLIENT)."""


def _fig(fig_id, title, caption, inner_svg, view_box="0 0 860 280"):
    return (
        f'<figure class="novak-tech-diagram" id="{fig_id}" role="group" aria-labelledby="{fig_id}-cap">'
        f'<div class="novak-svg-hdr"><strong>Interactive Architecture Diagram:</strong> {title}</div>'
        f'<svg viewBox="{view_box}" xmlns="http://www.w3.org/2000/svg" class="novak-svg-canvas" role="img" aria-label="{title}">'
        '<defs><style>'
        '.nd-bg{fill:#0f172a;rx:10px}.nd-box{fill:#1e293b;stroke:#38bdf8;stroke-width:1.6;rx:6px}'
        '.nd-box-alt{fill:#172554;stroke:#818cf8;stroke-width:1.6;rx:6px}'
        '.nd-box-warn{fill:#3b1725;stroke:#f43f5e;stroke-width:1.6;rx:6px}'
        '.nd-box-ok{fill:#052e16;stroke:#22c55e;stroke-width:1.6;rx:6px}'
        '.nd-t{fill:#f8fafc;font:600 12px system-ui,sans-serif}.nd-s{fill:#cbd5e1;font:10.5px ui-monospace,monospace}'
        '.nd-k{fill:#38bdf8;font:700 11px ui-monospace,monospace}.nd-line{stroke:#64748b;stroke-width:2;fill:none}'
        '.nd-bus{stroke:#22d3ee;stroke-width:2.5;stroke-dasharray:5,3;fill:none}'
        '</style></defs>'
        '<rect width="100%" height="100%" class="nd-bg"/>'
        f'{inner_svg}</svg>'
        f'<figcaption id="{fig_id}-cap" class="novak-svg-cap">{caption}</figcaption></figure>'
    )


SVG_DIAGRAMS = {
    'motherboard_bus': _fig(
        'novak-svg-motherboard-bus',
        'Motherboard Architecture & PCIe 5.0 / DDR5 / NVMe Bus Topology (ITSUP Ch 2–3)',
        'CPU root complex drives dual-channel DDR5 (2x32-bit + ECC subchannels per DIMM, Slots A2/B2 primary) and direct PCIe 5.0 x16/x4 NVMe lanes; DMI 4.0 x8 links the PCH chipset for USB 3.2, SATA 6 Gb/s (AHCI), and SPI UEFI flash.',
        '<rect x="310" y="22" width="240" height="90" class="nd-box"/><text x="330" y="45" class="nd-t">CPU Socket (LGA1700 / AM5)</text>'
        '<text x="330" y="65" class="nd-s">Integrated Memory Controller (IMC)</text><text x="330" y="83" class="nd-s">PCIe 5.0 Root Complex (20-28 lanes)</text>'
        '<rect x="30" y="25" width="215" height="82" class="nd-box-alt"/><text x="44" y="47" class="nd-t">PCIe 5.0 x16 Graphics Slot</text>'
        '<text x="44" y="66" class="nd-s">32 GT/s per lane (~64 GB/s x16)</text><text x="44" y="84" class="nd-s">12VHPWR / PCIe 8-pin aux</text>'
        '<rect x="615" y="25" width="215" height="82" class="nd-box-ok"/><text x="630" y="47" class="nd-t">Dual-Channel DDR5 DIMMs</text>'
        '<text x="630" y="66" class="nd-s">Populate A2 &amp; B2 first (288-pin)</text><text x="630" y="84" class="nd-s">On-die PMIC (1.1V) + 2x32b subch</text>'
        '<rect x="40" y="165" width="225" height="85" class="nd-box"/><text x="55" y="188" class="nd-t">M.2_1 NVMe (CPU-Attached)</text>'
        '<text x="55" y="207" class="nd-s">PCIe 4.0/5.0 x4 (Key M, 2280)</text><text x="55" y="225" class="nd-s">64K queues x 64K cmds (~7.4 GB/s)</text>'
        '<rect x="310" y="165" width="240" height="85" class="nd-box-alt"/><text x="326" y="188" class="nd-t">PCH / Chipset Southbridge</text>'
        '<text x="326" y="207" class="nd-s">SATA 3.0 (6 Gb/s) | USB 3.2 Gen2x2</text><text x="326" y="225" class="nd-s">Intel I226-V 2.5GbE | PCIe 4.0 x4</text>'
        '<rect x="605" y="165" width="225" height="85" class="nd-box-warn"/><text x="620" y="188" class="nd-t">SPI Flash / TPM 2.0 / Super I/O</text>'
        '<text x="620" y="207" class="nd-s">UEFI + Secure Boot db/dbx + CMOS</text><text x="620" y="225" class="nd-s">CPU_FAN PWM tach + 24-pin ATX</text>'
        '<line x1="245" y1="65" x2="310" y2="65" class="nd-bus"/><line x1="550" y1="65" x2="615" y2="65" class="nd-bus"/>'
        '<line x1="360" y1="112" x2="170" y2="165" class="nd-bus"/><line x1="430" y1="112" x2="430" y2="165" class="nd-bus"/>'
        '<line x1="550" y1="208" x2="605" y2="208" class="nd-line"/><text x="438" y="143" class="nd-k">DMI 4.0 x8</text>'
    ),
    'raid_architecture': _fig(
        'novak-svg-raid-architecture',
        'Storage & RAID 0 / 1 / 5 / 10 Striping, Mirroring & Distributed Parity (ITSUP Ch 3)',
        'Comparison of block-level striping (RAID 0), mirroring (RAID 1), distributed XOR parity (RAID 5, N-1 capacity, URE risk during rebuild), and nested stripe-of-mirrors (RAID 10, minimum 4 drives).',
        '<rect x="20" y="22" width="195" height="230" class="nd-box-warn"/><text x="32" y="45" class="nd-t">RAID 0 (Stripe Only)</text>'
        '<text x="32" y="68" class="nd-s">Disk 0: [A1] [A3] [A5]</text><text x="32" y="88" class="nd-s">Disk 1: [A2] [A4] [A6]</text>'
        '<text x="32" y="122" class="nd-k">Min Disks: 2 | Cap: 100%</text><text x="32" y="145" class="nd-s">Fault Tolerance: 0 drives</text>'
        '<text x="32" y="168" class="nd-s">Any 1 drive failure = 100%</text><text x="32" y="186" class="nd-s">volume loss (scratch only)</text>'
        '<rect x="228" y="22" width="195" height="230" class="nd-box"/><text x="240" y="45" class="nd-t">RAID 1 (Mirror)</text>'
        '<text x="240" y="68" class="nd-s">Disk 0: [A1] [A2] [A3]</text><text x="240" y="88" class="nd-s">Disk 1: [A1] [A2] [A3]</text>'
        '<text x="240" y="122" class="nd-k">Min Disks: 2 | Cap: 50%</text><text x="240" y="145" class="nd-s">Fault Tolerance: 1 drive</text>'
        '<text x="240" y="168" class="nd-s">Fast rebuild copy; used for</text><text x="240" y="186" class="nd-s">OS boot volumes</text>'
        '<rect x="436" y="22" width="195" height="230" class="nd-box-alt"/><text x="448" y="45" class="nd-t">RAID 5 (Distributed Parity)</text>'
        '<text x="448" y="68" class="nd-s">D0:[A1][B1][Bp] D1:[A2][Ap][B2]</text><text x="448" y="88" class="nd-s">D2:[Ap][B2][C1] (XOR Parity)</text>'
        '<text x="448" y="122" class="nd-k">Min Disks: 3 | Cap: (N-1)/N</text><text x="448" y="145" class="nd-s">Fault Tolerance: 1 drive</text>'
        '<text x="448" y="168" class="nd-s">2nd drive failure during XOR</text><text x="448" y="186" class="nd-s">rebuild destroys array</text>'
        '<rect x="644" y="22" width="196" height="230" class="nd-box-ok"/><text x="656" y="45" class="nd-t">RAID 10 (1+0 Nested)</text>'
        '<text x="656" y="68" class="nd-s">Mirror A (D0,D1): [A1][A3]</text><text x="656" y="88" class="nd-s">Mirror B (D2,D3): [A2][A4]</text>'
        '<text x="656" y="122" class="nd-k">Min Disks: 4 | Cap: 50%</text><text x="656" y="145" class="nd-s">Survives 1 per mirror pair</text>'
        '<text x="656" y="168" class="nd-s">High IOPS + no parity XOR</text><text x="656" y="186" class="nd-s">penalty; RAID != Backup!</text>'
    ),
    'osi_encapsulation': _fig(
        'novak-svg-osi-encapsulation',
        'OSI 7-Layer & TCP/IP Encapsulation / Decapsulation Pipeline (ITSUP Ch 5 & NETOPS Ch 1)',
        'Downward encapsulation wraps Application Data into a Layer-4 Segment/Datagram (ports), Layer-3 Packet (IP + TTL), and Layer-2 Frame (MACs + 802.1Q + FCS). Routers rewrite L2 MACs and decrement TTL at every hop while preserving end-to-end IPs (absent NAT).',
        '<rect x="20" y="22" width="390" height="235" class="nd-box"/><text x="36" y="45" class="nd-t">OSI 7-Layer Stack &amp; TCP/IP Mapping</text>'
        '<text x="36" y="70" class="nd-s">L7 Application  | HTTP/443, DNS/53, SSH/22   [Data]</text>'
        '<text x="36" y="92" class="nd-s">L6 Presentation | TLS 1.3 (RFC 8446), UTF-8  [Data]</text>'
        '<text x="36" y="114" class="nd-s">L5 Session      | RPC / NetBIOS / TLS Sess   [Data]</text>'
        '<text x="36" y="138" class="nd-k">L4 Transport    | TCP (SYN/ACK) / UDP        [Segment/Datagram]</text>'
        '<text x="36" y="162" class="nd-k">L3 Network      | IPv4 / IPv6 / ICMP / OSPF  [Packet]</text>'
        '<text x="36" y="186" class="nd-k">L2 Data Link    | Ethernet 802.3 / 802.1Q    [Frame]</text>'
        '<text x="36" y="210" class="nd-s">L1 Physical     | 1000BASE-T / 10GBASE-SR    [Bits / Symbols]</text>'
        '<rect x="435" y="22" width="405" height="235" class="nd-box-alt"/><text x="450" y="45" class="nd-t">Wire-Level Ethernet Frame Encapsulation</text>'
        '<rect x="450" y="65" width="72" height="50" class="nd-box-ok"/><text x="456" y="88" class="nd-s">L2 Hdr</text><text x="456" y="103" class="nd-s">DMAC/SMAC</text>'
        '<rect x="526" y="65" width="72" height="50" class="nd-box"/><text x="532" y="88" class="nd-s">L3 IP Hdr</text><text x="532" y="103" class="nd-s">SIP/DIP/TTL</text>'
        '<rect x="602" y="65" width="72" height="50" class="nd-box-alt"/><text x="608" y="88" class="nd-s">L4 TCP</text><text x="608" y="103" class="nd-s">SPort/DPort</text>'
        '<rect x="678" y="65" width="82" height="50" class="nd-box"/><text x="686" y="88" class="nd-s">L7 Payload</text><text x="686" y="103" class="nd-s">TLS/HTTP</text>'
        '<rect x="764" y="65" width="60" height="50" class="nd-box-warn"/><text x="772" y="88" class="nd-s">L2 FCS</text><text x="772" y="103" class="nd-s">CRC-32</text>'
        '<text x="450" y="145" class="nd-k">Hop-by-Hop vs End-to-End Invariants:</text>'
        '<text x="450" y="168" class="nd-s">• Switch (L2): Reads DMAC, learns SMAC in CAM, keeps TTL</text>'
        '<text x="450" y="190" class="nd-s">• Router (L3): Strips L2 frame, decrements IP TTL by 1,</text>'
        '<text x="450" y="210" class="nd-s">  recomputes IPv4 header checksum, writes new L2 DMAC/SMAC</text>'
        '<text x="450" y="232" class="nd-s">• Standard Ethernet payload MTU = 1500B (1518B untagged frame)</text>'
    ),
    'vlan_trunking_roas': _fig(
        'novak-svg-vlan-roas',
        'IEEE 802.1Q VLAN Trunking, Native VLANs & Router-on-a-Stick (NETOPS Ch 2 & Ch 9)',
        'Access ports belong to a single untagged VLAN; 802.1Q trunks insert a 4-byte tag (TPID 0x8100 + 12-bit VID) for all non-native VLANs. Router-on-a-Stick routes inter-VLAN traffic over Gi0/0.10 and Gi0/0.20 subinterfaces.',
        '<rect x="20" y="30" width="185" height="90" class="nd-box"/><text x="32" y="55" class="nd-t">Access Ports (SW1)</text>'
        '<text x="32" y="76" class="nd-s">Fa0/1: VLAN 10 (10.10.10.21)</text><text x="32" y="96" class="nd-s">Fa0/2: VLAN 20 (10.10.20.22)</text>'
        '<rect x="240" y="30" width="335" height="90" class="nd-box-alt"/><text x="255" y="55" class="nd-t">802.1Q Trunk Link (Gi0/1 &lt;-&gt; RTR Gi0/0)</text>'
        '<text x="255" y="76" class="nd-k">4-Byte Tag: TPID 0x8100 | PCP(3b) | DEI(1b) | VID(12b)</text>'
        '<text x="255" y="96" class="nd-s">switchport trunk allowed vlan 10,20,99 | native 99</text>'
        '<rect x="610" y="30" width="230" height="90" class="nd-box-ok"/><text x="624" y="55" class="nd-t">Router-on-a-Stick (RTR1)</text>'
        '<text x="624" y="76" class="nd-s">Gi0/0.10: dot1Q 10 | 10.10.10.1/24</text><text x="624" y="96" class="nd-s">Gi0/0.20: dot1Q 20 | 10.10.20.1/24</text>'
        '<line x1="205" y1="75" x2="240" y2="75" class="nd-bus"/><line x1="575" y1="75" x2="610" y2="75" class="nd-bus"/>'
        '<rect x="20" y="145" width="820" height="110" class="nd-box"/><text x="36" y="170" class="nd-t">802.1Q Frame Insertion &amp; Verification Workflow</text>'
        '<text x="36" y="193" class="nd-s">[DMAC 6B][SMAC 6B] + [802.1Q Tag 4B: 0x8100 | VID 10/20] + [EtherType 0x0800] + [IPv4 Packet] + [New FCS 4B (1522B max)]</text>'
        '<text x="36" y="216" class="nd-k">Verify: show interfaces trunk (Allowed + Active + Not Pruned) | show vlan brief | show ip interface brief</text>'
        '<text x="36" y="238" class="nd-s">Native VLAN mismatch (CDP %CDP-4-NATIVE_VLAN_MISMATCH) leaks untagged frames across VLANs; set unused native VLAN 99.</text>'
    ),
    'cidr_ipv6_ndp': _fig(
        'novak-svg-cidr-ipv6-ndp',
        'IPv4 CIDR Bit-Boundary Math & IPv6 SLAAC / NDP Neighbor Discovery Flow (NETOPS Ch 1 & Ch 3)',
        'Left: IPv4 /26 splits the 4th octet at bit value 64 (4 subnets of 64 addresses, 62 usable hosts). Right: IPv6 ICMPv6 Neighbor Discovery Protocol (NDP) replaces ARP and configures SLAAC /64 addresses via RS/RA (Types 133/134) and NS/NA DAD (Types 135/136).',
        '<rect x="20" y="22" width="400" height="235" class="nd-box"/><text x="35" y="45" class="nd-t">IPv4 CIDR Octet Boundary (e.g., 192.168.10.77/26)</text>'
        '<text x="35" y="70" class="nd-k">Bit Value:  128  64 |  32  16   8   4   2   1</text>'
        '<text x="35" y="92" class="nd-s">/26 Mask:     1   1 |   0   0   0   0   0   0  (.192, block=64)</text>'
        '<text x="35" y="118" class="nd-s">Subnets:    .0/26 (.1-.62, bcast .63)</text>'
        '<text x="35" y="138" class="nd-k">Active:     .64/26 (Net .64 | Hosts .65-.126 | Bcast .127)</text>'
        '<text x="35" y="158" class="nd-s">Next:       .128/26 (.129-.190) | .192/26 (.193-.254)</text>'
        '<text x="35" y="188" class="nd-s">Usable Formula: 2^h - 2 = 2^6 - 2 = 62 hosts (/30 = 2, /31 = 2 PtP)</text>'
        '<text x="35" y="212" class="nd-s">RFC 1918 Private: 10/8, 172.16/12, 192.168/16 | APIPA: 169.254/16</text>'
        '<text x="35" y="234" class="nd-s">CGNAT Shared WAN: 100.64.0.0/10 (RFC 6598)</text>'
        '<rect x="440" y="22" width="400" height="235" class="nd-box-alt"/><text x="455" y="45" class="nd-t">IPv6 SLAAC &amp; ICMPv6 NDP (RFC 4861 / 4862)</text>'
        '<text x="455" y="70" class="nd-s">1. Link-Local Init: fe80::/10 + 64-bit IID (EUI-64 or RFC 7217)</text>'
        '<text x="455" y="94" class="nd-k">2. RS (ICMPv6 Type 133): Host -&gt; ff02::2 (All-Routers Multicast)</text>'
        '<text x="455" y="118" class="nd-k">3. RA (ICMPv6 Type 134): Router -&gt; ff02::1 (Prefix 2001:db8:1::/64)</text>'
        '<text x="455" y="142" class="nd-s">   Flags: A=1 (SLAAC), M=0/1 (Managed DHCPv6), O=1 (Other DNS)</text>'
        '<text x="455" y="166" class="nd-k">4. NS (Type 135): Solicited-Node ff02::1:ffXX:XXXX (DAD &amp; MAC res)</text>'
        '<text x="455" y="190" class="nd-k">5. NA (Type 136): Unicast reply with Target Link-Layer MAC Address</text>'
        '<text x="455" y="216" class="nd-s">Verify: ip -6 neigh show | ip -6 route show | show ipv6 neighbors</text>'
        '<text x="455" y="236" class="nd-s">Security: Enable RA Guard (RFC 6105) on switch access ports</text>'
    ),
}

SVG_DIAGRAMS.update({
    'ospf_bgp_routing': _fig(
        'novak-svg-ospf-bgp',
        'OSPF Multi-Area (Area 0 Backbone, ABR, ASBR) & BGP (eBGP vs iBGP) Routing (NETOPS Ch 3)',
        'Longest-prefix match always wins (/26 beats /24 beats /16). For identical prefixes, lowest Administrative Distance wins (Connected 0, Static 1, eBGP 20, OSPF 110, RIP 120, iBGP 200). OSPF Area 0 connects non-backbone areas via ABRs; eBGP peers across autonomous systems over TCP 179.',
        '<rect x="20" y="22" width="255" height="235" class="nd-box"/><text x="34" y="45" class="nd-t">OSPFv2/v3 Area 0 (Backbone)</text>'
        '<text x="34" y="68" class="nd-s">IP Proto 89 | Multicast 224.0.0.5/.6</text>'
        '<text x="34" y="90" class="nd-k">States: Down-&gt;Init-&gt;2-Way-&gt;ExStart</text>'
        '<text x="34" y="108" class="nd-k">        -&gt;Exchange-&gt;Loading-&gt;Full</text>'
        '<text x="34" y="132" class="nd-s">Cost = Ref BW / Intf BW (SPF Dijkstra)</text>'
        '<text x="34" y="154" class="nd-s">Match reqs: Hello/Dead, Area ID, MTU,</text>'
        '<text x="34" y="172" class="nd-s">Subnet mask, Auth, Stub flags</text>'
        '<text x="34" y="198" class="nd-k">CLI: show ip ospf neighbor</text>'
        '<text x="34" y="218" class="nd-s">ABR joins Area 1/2 to Area 0</text>'
        '<rect x="295" y="22" width="265" height="235" class="nd-box-alt"/><text x="310" y="45" class="nd-t">ASBR &amp; BGP Autonomous Systems</text>'
        '<text x="310" y="68" class="nd-s">AS 65001 (Enterprise) &lt;-&gt; AS 65100 (ISP)</text>'
        '<text x="310" y="92" class="nd-k">eBGP (AD 20, TCP 179) vs iBGP (AD 200)</text>'
        '<text x="310" y="116" class="nd-s">Path Vector: AS_PATH, LOCAL_PREF,</text>'
        '<text x="310" y="134" class="nd-s">MED, NEXT_HOP, Weight</text>'
        '<text x="310" y="160" class="nd-s">FHRP LAN Gateway Redundancy:</text>'
        '<text x="310" y="180" class="nd-k">VRRP (RFC 5798, IP 112) / HSRP (UDP 1985)</text>'
        '<text x="310" y="202" class="nd-s">Virtual IP + Virtual MAC + Preempt</text>'
        '<text x="310" y="224" class="nd-s">CLI: show ip bgp summary | show standby</text>'
        '<rect x="580" y="22" width="260" height="235" class="nd-box-ok"/><text x="595" y="45" class="nd-t">Route Selection Order of Operations</text>'
        '<text x="595" y="70" class="nd-k">1. Longest Prefix Match (LPM) FIRST</text>'
        '<text x="595" y="90" class="nd-s">   10.1.2.0/26 beats 10.1.0.0/16</text>'
        '<text x="595" y="116" class="nd-k">2. Administrative Distance (Equal Mask)</text>'
        '<text x="595" y="136" class="nd-s">   Connected=0 | Static=1 | eBGP=20</text>'
        '<text x="595" y="154" class="nd-s">   EIGRP=90 | OSPF=110 | IS-IS=115</text>'
        '<text x="595" y="172" class="nd-s">   RIP=120 | iBGP=200</text>'
        '<text x="595" y="198" class="nd-k">3. Protocol Metric (Equal Mask &amp; AD)</text>'
        '<text x="595" y="218" class="nd-s">   Equal-Cost Multi-Path (ECMP) load</text>'
        '<text x="595" y="236" class="nd-s">   balances across equal-metric paths</text>'
    ),
    'wireless_8021x_channels': _fig(
        'novak-svg-wireless-8021x',
        'Enterprise Wireless 802.1X / RADIUS / EAP-TLS & 2.4 / 5 / 6 GHz Channel Plan (NETOPS Ch 3 & Ch 5)',
        'Left: Non-overlapping RF channel allocations across 2.4 GHz (Ch 1, 6, 11 at 20 MHz), 5 GHz (UNII-1/2/3 + DFS), and 6 GHz (Wi-Fi 6E/7 PSC). Right: IEEE 802.1X port-based authentication between Supplicant, WLC/Switch Authenticator, and RADIUS Server.',
        '<rect x="20" y="22" width="400" height="235" class="nd-box"/><text x="35" y="45" class="nd-t">RF Spectrum &amp; Non-Overlapping Channel Plan</text>'
        '<text x="35" y="70" class="nd-k">2.4 GHz (802.11b/g/n/ax): Ch 1 (2412), Ch 6 (2437), Ch 11 (2462)</text>'
        '<text x="35" y="90" class="nd-s">  Use 20 MHz only; Ch 2-5/7-10 cause adjacent-channel interference</text>'
        '<text x="35" y="116" class="nd-k">5 GHz (802.11a/n/ac/ax/be): 20/40/80 MHz channels</text>'
        '<text x="35" y="136" class="nd-s">  UNII-1 (36,40,44,48) | UNII-2/2e DFS (52-144, radar avoidance)</text>'
        '<text x="35" y="154" class="nd-s">  UNII-3 (149,153,157,161,165)</text>'
        '<text x="35" y="180" class="nd-k">6 GHz (Wi-Fi 6E / Wi-Fi 7 802.11be): 1200 MHz clean spectrum</text>'
        '<text x="35" y="200" class="nd-s">  WPA3 / OWE mandatory; 80/160/320 MHz + MLO</text>'
        '<text x="35" y="226" class="nd-s">Target Voice/Video Roaming: RSSI &gt;= -67 dBm, SNR &gt;= 25 dB, 15-20% overlap</text>'
        '<rect x="440" y="22" width="400" height="235" class="nd-box-alt"/><text x="455" y="45" class="nd-t">IEEE 802.1X / WPA3-Enterprise Authentication</text>'
        '<text x="455" y="70" class="nd-k">[Supplicant (Client)] &lt;--EAPOL--&gt; [Authenticator (WLC/Switch)]</text>'
        '<text x="455" y="92" class="nd-k">                      &lt;--RADIUS (UDP 1812/1813 or TLS 2083)--&gt; [AAA/PKI]</text>'
        '<text x="455" y="120" class="nd-s">• EAP-TLS (RFC 5216): Mutual X.509 certificates (client + server);</text>'
        '<text x="455" y="138" class="nd-s">  strongest zero-password authentication</text>'
        '<text x="455" y="160" class="nd-s">• PEAP-MSCHAPv2 / EAP-TTLS: Server cert TLS tunnel + inner AD auth</text>'
        '<text x="455" y="182" class="nd-s">• RADIUS Access-Accept returns per-session PMK + Dynamic VLAN</text>'
        '<text x="455" y="200" class="nd-s">  (Tunnel-Private-Group-Id) + dACL + CoA (UDP 3799)</text>'
        '<text x="455" y="226" class="nd-s">• Fast Roaming: 802.11r (FT), 802.11k (Neighbor Rep), 802.11v (BSS Trans)</text>'
    ),
    'ztna_sdwan_dmz': _fig(
        'novak-svg-ztna-sdwan-dmz',
        'Zero-Trust Architecture (NIST SP 800-207), SD-WAN Planes & Screened-Subnet DMZ ACL Flow (NETOPS Ch 4 & Ch 5)',
        'Left: NIST SP 800-207 Zero-Trust Policy Engine (PDP) and Policy Enforcement Point (PEP) separated from SD-WAN Management, Control, and Data planes. Right: Screened-subnet (DMZ) stateful firewall zone policies and top-down ACL processing.',
        '<rect x="20" y="22" width="400" height="235" class="nd-box"/><text x="35" y="45" class="nd-t">Zero-Trust (NIST 800-207) &amp; SD-WAN Planes</text>'
        '<text x="35" y="70" class="nd-k">Control Plane (PDP): Policy Engine + Policy Administrator</text>'
        '<text x="35" y="90" class="nd-s">  Evaluates User IdP + Device Posture + Threat Intel per request</text>'
        '<text x="35" y="114" class="nd-k">Data Plane (PEP): ZTNA Gateway / Micro-Segmentation</text>'
        '<text x="35" y="134" class="nd-s">  Establishes mTLS session to single app (no flat VPN LAN access)</text>'
        '<text x="35" y="162" class="nd-k">SD-WAN Plane Separation:</text>'
        '<text x="35" y="182" class="nd-s">  • Management Plane: Central GUI/API/Zero-Touch Provisioning</text>'
        '<text x="35" y="202" class="nd-s">  • Control Plane: OMP/BGP route &amp; IPsec key distribution</text>'
        '<text x="35" y="222" class="nd-s">  • Data Plane: IPsec/GRE BFD SLA probes (jitter, loss, latency)</text>'
        '<rect x="440" y="22" width="400" height="235" class="nd-box-ok"/><text x="455" y="45" class="nd-t">Screened-Subnet (DMZ) &amp; Top-Down Stateful ACLs</text>'
        '<text x="455" y="70" class="nd-s">[Untrusted WAN] --&gt; (TCP 443 DNAT) --&gt; [DMZ Reverse Proxy 172.16.10.5]</text>'
        '<text x="455" y="92" class="nd-s">[DMZ 172.16.10.5] --&gt; (TCP 8443/5432 Only) --&gt; [Internal App/DB VLAN]</text>'
        '<text x="455" y="114" class="nd-k">[Untrusted WAN] --X (DENY Direct) X--&gt; [Internal Corp &amp; DB VLANs]</text>'
        '<text x="455" y="144" class="nd-k">ACL Evaluation Rules (First-Match Wins + Implicit Deny):</text>'
        '<text x="455" y="166" class="nd-s">10 permit tcp any host 172.16.10.5 eq 443   [MATCHES HTTPS]</text>'
        '<text x="455" y="186" class="nd-s">20 permit udp host 10.10.20.50 any eq 53    [MATCHES DNS]</text>'
        '<text x="455" y="206" class="nd-s">99 deny ip any any log                      [IMPLICIT DENY ALL]</text>'
        '<text x="455" y="230" class="nd-s">Inbound ACLs run BEFORE routing decision; Outbound ACLs run AFTER</text>'
    ),
    'uefi_gpt_ntfs': _fig(
        'novak-svg-uefi-gpt-ntfs',
        'Windows UEFI / GPT Secure Boot Pipeline & NTFS Permission Inheritance Matrix (CLIENT Ch 1 & Ch 2)',
        'Left: UEFI 64-bit Secure Boot chain from SPI flash through EFI System Partition (FAT32) bootmgfw.efi, winload.efi, and BitLocker TPM 2.0 PCR validation. Right: NTFS explicit vs inherited ACE precedence and SMB Share x NTFS effective permission intersection.',
        '<rect x="20" y="22" width="400" height="235" class="nd-box"/><text x="35" y="45" class="nd-t">UEFI + GPT + Secure Boot + TPM 2.0 Chain</text>'
        '<text x="35" y="70" class="nd-k">1. UEFI Firmware (SPI Flash) -&gt; POST &amp; Secure Boot Verification</text>'
        '<text x="35" y="90" class="nd-s">   Checks KEK / db signatures and dbx revocation list</text>'
        '<text x="35" y="114" class="nd-k">2. GPT Disk (128 partitions, 64-bit LBAs, Backup GPT Header)</text>'
        '<text x="35" y="134" class="nd-s">   FAT32 EFI System Partition: \\EFI\\Microsoft\\Boot\\bootmgfw.efi</text>'
        '<text x="35" y="158" class="nd-k">3. BCD Store -&gt; winload.efi (TPM 2.0 PCRs 0,2,4,7,11 unseal)</text>'
        '<text x="35" y="180" class="nd-s">4. ntoskrnl.exe -&gt; smss.exe -&gt; wininit.exe -&gt; services.exe -&gt; lsass.exe</text>'
        '<text x="35" y="206" class="nd-s">Repair: bcdedit /enum | reagentc /info | DISM /RestoreHealth | sfc /scannow</text>'
        '<text x="35" y="228" class="nd-s">BitLocker status: manage-bde -status C: | Confirm-SecureBootUEFI</text>'
        '<rect x="440" y="22" width="400" height="235" class="nd-box-alt"/><text x="455" y="45" class="nd-t">NTFS Inheritance &amp; SMB Share Intersection</text>'
        '<text x="455" y="70" class="nd-k">ACE Precedence Order (Evaluated Before Inherited):</text>'
        '<text x="455" y="92" class="nd-s">  1. Explicit Deny  &gt;  2. Explicit Allow</text>'
        '<text x="455" y="112" class="nd-s">  3. Inherited Deny &gt;  4. Inherited Allow (from parent folder)</text>'
        '<text x="455" y="140" class="nd-k">Network Access = MOST RESTRICTIVE of (SMB Share n NTFS):</text>'
        '<text x="455" y="162" class="nd-s">  User User1 in GroupA (NTFS Read) + GroupB (NTFS Modify)</text>'
        '<text x="455" y="180" class="nd-s">  -&gt; Cumulative NTFS = Modify; if SMB Share = Read -&gt; Effective = Read!</text>'
        '<text x="455" y="206" class="nd-k">Move vs Copy Rule:</text>'
        '<text x="455" y="226" class="nd-s">  Same-volume Move keeps ACLs; Cross-volume Move or Copy inherits dest ACLs</text>'
    ),
    'pki_tls13_handshake': _fig(
        'novak-svg-pki-tls13',
        'PKI X.509 Certificate Chain of Trust & TLS 1.3 / Mutual Auth Handshake (CLIENT Ch 3 & Ch 4)',
        'Left: 3-tier PKI hierarchy (Offline Root CA -> Issuing Intermediate CA -> End-Entity SAN Certificate) and revocation checking (CRL, OCSP Stapling). Right: 1-RTT TLS 1.3 handshake (RFC 8446) with ephemeral ECDHE forward secrecy and mTLS client authentication.',
        '<rect x="20" y="22" width="400" height="235" class="nd-box"/><text x="35" y="45" class="nd-t">PKI 3-Tier X.509v3 Hierarchy &amp; Revocation</text>'
        '<text x="35" y="70" class="nd-k">[Offline Root CA] (Self-Signed, HSM Air-Gapped, 10-20 yr)</text>'
        '<text x="35" y="92" class="nd-s">       |  signs Intermediate CA Certificate</text>'
        '<text x="35" y="114" class="nd-k">[Issuing / Intermediate CA] (Online Enterprise CA, 3-5 yr)</text>'
        '<text x="35" y="136" class="nd-s">       |  signs Leaf End-Entity Certificate (SAN = DNS/IP)</text>'
        '<text x="35" y="158" class="nd-k">[Leaf Server / Client Cert] (Valid &lt;= 398 days, EKU Server/Client)</text>'
        '<text x="35" y="186" class="nd-s">Revocation &amp; Validation:</text>'
        '<text x="35" y="206" class="nd-s">• CRL (Certificate Revocation List) vs OCSP (RFC 6960) &amp; OCSP Stapling</text>'
        '<text x="35" y="226" class="nd-s">• Hostname mismatch if URL != Subject Alternative Name (SAN)</text>'
        '<rect x="440" y="22" width="400" height="235" class="nd-box-ok"/><text x="455" y="45" class="nd-t">TLS 1.3 (RFC 8446) 1-RTT &amp; mTLS Handshake</text>'
        '<text x="455" y="70" class="nd-k">Client                                     Server (TCP 443)</text>'
        '<text x="455" y="92" class="nd-s">1. ClientHello + SNI + CipherSuites + ECDHE key_share ---&gt;</text>'
        '<text x="455" y="116" class="nd-s">2. &lt;--- ServerHello + key_share + {EncryptedExtensions}</text>'
        '<text x="455" y="136" class="nd-s">        + {Certificate} + {CertificateVerify} + {Finished}</text>'
        '<text x="455" y="160" class="nd-k">3. [Optional mTLS: Client {Certificate} + {CertificateVerify}]</text>'
        '<text x="455" y="182" class="nd-s">4. Client {Finished} + AEAD Application Data (AES-256-GCM) ---&gt;</text>'
        '<text x="455" y="210" class="nd-s">• Ephemeral ECDHE guarantees Perfect Forward Secrecy (PFS)</text>'
        '<text x="455" y="230" class="nd-s">• Static RSA key exchange removed in TLS 1.3</text>'
    ),
})

LESSON_DIAGRAM_MAP = {
    ('ITSUP', 2, 1): 'motherboard_bus',
    ('ITSUP', 3, 1): 'motherboard_bus',
    ('ITSUP', 3, 2): 'raid_architecture',
    ('ITSUP', 5, 1): 'osi_encapsulation',
    ('NETOPS', 1, 1): 'osi_encapsulation',
    ('NETOPS', 1, 2): 'cidr_ipv6_ndp',
    ('NETOPS', 2, 2): 'vlan_trunking_roas',
    ('NETOPS', 3, 1): 'ospf_bgp_routing',
    ('NETOPS', 3, 3): 'wireless_8021x_channels',
    ('NETOPS', 4, 3): 'ztna_sdwan_dmz',
    ('NETOPS', 5, 3): 'ztna_sdwan_dmz',
    ('NETOPS', 9, 4): 'vlan_trunking_roas',
    ('ITSUP', 8, 1): 'uefi_gpt_ntfs',
    ('ITSUP', 8, 2): 'uefi_gpt_ntfs',
    ('ITSUP', 10, 1): 'pki_tls13_handshake',
    ('ITSUP', 11, 1): 'pki_tls13_handshake',
}
