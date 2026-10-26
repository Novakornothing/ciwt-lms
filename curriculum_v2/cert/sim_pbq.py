"""Interactive simulation PBQs for the Exam-Day Readiness Simulator (Option B pass 4). Pending SME review.

Each item is a small testing-centre style simulation: one or more read-only tabs (diagnostic terminal, topology,
configuration inspector) the candidate explores, then 3-4 remediation sub-fields. ``practice.grade`` scores a
sim_pbq all-or-nothing (as the scaled score does) and ``practice.partial`` reports parts right for feedback.
Options inside every part are length-balanced (the key is never >= 1.15x the longest distractor).
"""
REVIEW = 'Pending SME review'


def _t(name, kind, **kw):
    return dict(name=name, kind=kind, **kw)


def _p(prompt, correct, wrong):
    opts = sorted([correct] + list(wrong), key=lambda s: (len(s), s))
    return {'prompt': prompt, 'options': opts, 'correct': correct}


SIMS = [
    # ------------------------------------------------------------------ Network+ N10-009
    dict(id='SIM-N-1', obj='NO-2.2', oid='N:2.2', text='Users on PC-B (VLAN 20) cannot reach the file server in VLAN 10, but PC-A '
         '(VLAN 10) can. Inspect the switch, then fix the fault.',
         tabs=[_t('Topology', 'topology', nodes=[
             ('PC-A', 'Gi0/2 · VLAN 10 · 10.10.10.21/24 · gateway 10.10.10.1'),
             ('PC-B', 'Gi0/3 · VLAN 20 · 10.10.20.30/24 · gateway 10.10.20.1'),
             ('SW1', 'Access switch · uplink Gi0/1 to R1 (router-on-a-stick)'),
             ('R1', 'Gi0/0.10 10.10.10.1 dot1Q 10 · Gi0/0.20 10.10.20.1 dot1Q 20'),
             ('FS1', 'File server 10.10.10.5/24 in VLAN 10')]),
               _t('SW1 terminal', 'terminal', commands={
                   'show vlan brief': 'VLAN Name     Status  Ports\n1    default  active  Gi0/4-24\n10   USERS-A  active  Gi0/2\n20   USERS-B  active  Gi0/3',
                   'show interfaces trunk': 'Port   Mode  Encapsulation  Status    Native vlan\nGi0/1  on    802.1q         trunking  1\n\nPort   Vlans allowed on trunk\nGi0/1  1,10',
                   'show interfaces gi0/3 switchport': 'Name: Gi0/3\nAdministrative Mode: static access\nAccess Mode VLAN: 20 (USERS-B)'})],
         parts=[_p('Faulty device / port', 'SW1 Gi0/1 (trunk uplink)', ['SW1 Gi0/3 (PC-B access)', 'R1 Gi0/0.10 subinterface', 'FS1 network adapter NIC']),
                _p('Root cause', 'VLAN 20 not allowed on trunk', ['PC-B port is in VLAN 10', 'Native VLAN mismatch on R1', 'Wrong gateway set on PC-B']),
                _p('Corrective command', 'switchport trunk allowed vlan add 20',
                   ['switchport access vlan 20 on Gi0/1', 'switchport trunk native vlan 20', 'no switchport on interface Gi0/1'])],
         explanation='show interfaces trunk lists only VLANs 1,10 as allowed on Gi0/1, so VLAN 20 frames never reach the '
                     'router subinterface. Adding VLAN 20 to the allowed list fixes inter-VLAN routing for PC-B.'),
    dict(id='SIM-N-2', obj='NO-9.2', oid='N:5.5', text='A branch PC (192.168.50.20) cannot browse https://intranet (10.1.1.80). Ping '
         'works. Use the router tabs to find and fix the fault.',
         tabs=[_t('R-BR terminal', 'terminal', commands={
             'show ip route': 'Gateway of last resort is 203.0.113.1\nC 192.168.50.0/24 is directly connected, Gi0/1\nS 10.1.1.0/24 [1/0] via 172.16.0.2\nS* 0.0.0.0/0 [1/0] via 203.0.113.1',
             'show access-lists': 'Extended IP access list BRANCH-OUT\n 10 permit icmp 192.168.50.0 0.0.0.255 any\n 20 permit udp 192.168.50.0 0.0.0.255 any eq 53\n 30 deny ip any any (41 matches)',
             'show ip interface gi0/1': 'GigabitEthernet0/1 is up, line protocol is up\n Internet address is 192.168.50.1/24\n Inbound access list is BRANCH-OUT'}),
               _t('Config inspector', 'inspector', text='interface Gi0/1\n ip address 192.168.50.1 255.255.255.0\n ip access-group BRANCH-OUT in\n!\nip route 10.1.1.0 255.255.255.0 172.16.0.2')],
         parts=[_p('Where the traffic stops', 'R-BR Gi0/1 inbound ACL', ['Static route to 10.1.1.0', 'Default route to the ISP', 'DNS server for the branch']),
                _p('ACL action to add', 'permit tcp ... any eq 443', ['permit udp ... any eq 443', 'deny icmp ... any echo', 'permit tcp ... any eq 23']),
                _p('Placement of the new line', 'Before line 30 (deny ip any)', ['After line 30 (deny ip any)', 'Applied outbound on Gi0/0', 'In a new standard access list'])],
         explanation='ICMP and DNS are permitted but HTTPS hits the explicit deny on line 30. A permit for TCP 443 placed '
                     'above the deny (ACLs are processed top-down) fixes it; the routes are fine because ping works.'),
    dict(id='SIM-N-3', obj='IT-5.1', oid='N:1.7', text='A new hire\'s laptop shows 169.254.x.x while every other host on the same '
         'subnet works. Inspect the host, then correct its settings.',
         tabs=[_t('Laptop terminal', 'terminal', commands={
             'ipconfig /all': 'Ethernet adapter Ethernet:\n   DHCP Enabled. . . . . . : No\n   IPv4 Address. . . . . . : 192.168.10.300(Duplicate)\n   Subnet Mask . . . . . . : 255.255.255.0\n   Autoconfiguration IPv4 . : 169.254.12.7(Preferred)\n   Default Gateway . . . . : 192.168.1.1',
             'ping 192.168.10.1': 'PING: transmit failed. General failure.'}),
               _t('Topology', 'topology', nodes=[('Laptop', 'Port 14 · VLAN 10 · static settings typed by hand'),
                                                ('SW2', 'All ports VLAN 10 · DHCP snooping off'),
                                                ('R2', 'Gi0/0 192.168.10.1/24 · DHCP pool 192.168.10.50-200')])],
         parts=[_p('Addressing method to use', 'Enable DHCP on the adapter', ['Keep the static address set', 'Set APIPA as preferred IP', 'Use IPv6 link-local only']),
                _p('What was wrong with the IP', 'Octet 300 is out of range', ['/24 mask is far too small', 'It sits in the DHCP pool', 'It is a broadcast address']),
                _p('Correct default gateway', '192.168.10.1', ['192.168.1.1', '192.168.10.255', '169.254.0.1'])],
         explanation='The hand-typed address 192.168.10.300 is invalid, so Windows fell back to APIPA, and the gateway '
                     '192.168.1.1 is on a different subnet. Enabling DHCP gets 192.168.10.x with gateway 192.168.10.1.'),
    # ------------------------------------------------------------------ Additional Network+ N10-009 (SIM-N-4 .. SIM-N-10)
    dict(id='SIM-N-4', obj='NO-2.2', oid='N:2.2', text='Switches SW-CORE and SW-ACC1 have two redundant gigabit links bundled into Port-channel 1, but the bundle is down and spanning tree blocks both ports as err-disabled/suspended. Inspect both switches and fix the LACP trunk.',
         tabs=[_t('SW-CORE terminal', 'terminal', commands={
             'show etherchannel summary': 'Group  Port-channel  Protocol  Ports\n1      Po1(SD)       LACP      Gi0/1(s) Gi0/2(s)',
             'show running-config interface range gi0/1-2': 'interface Gi0/1\n switchport mode trunk\n channel-group 1 mode passive\ninterface Gi0/2\n switchport mode trunk\n channel-group 1 mode passive'}),
               _t('SW-ACC1 terminal', 'terminal', commands={
             'show etherchannel summary': 'Group  Port-channel  Protocol  Ports\n1      Po1(SD)       LACP      Gi0/1(I) Gi0/2(I)',
             'show running-config interface range gi0/1-2': 'interface Gi0/1\n switchport mode access\n switchport access vlan 10\n channel-group 1 mode passive\ninterface Gi0/2\n switchport mode access\n switchport access vlan 10\n channel-group 1 mode passive'})],
         parts=[_p('Why LACP fails to negotiate', 'Both ends are in passive mode', ['PAgP is enabled on SW-CORE', 'Port-channel ID must be 10', 'STP PortFast is enabled']),
                _p('Why SW-CORE suspends Gi0/1-2', 'SW-ACC1 ports are access mode', ['Duplex is set to half-duplex', 'VLAN 10 does not exist', 'MTU is set to 9000 bytes']),
                _p('Fix on SW-ACC1 Gi0/1-2', 'switchport mode trunk + mode active', ['channel-group 1 mode on only', 'switchport trunk native vlan 99', 'spanning-tree bpduguard enable'])],
         explanation='Two LACP passive endpoints never initiate negotiation, and EtherChannel member ports must match trunk/access mode on both ends. Setting SW-ACC1 Gi0/1-2 to trunk mode and LACP active brings Po1 up.'),
    dict(id='SIM-N-5', obj='NO-3.1', oid='N:2.1', text='Router R1 and R2 share a point-to-point subnet (10.0.12.0/30) in OSPF Area 0, but the adjacency never forms. Inspect the OSPF outputs and resolve the mismatch.',
         tabs=[_t('R1 terminal', 'terminal', commands={
             'show ip ospf interface gi0/0': 'GigabitEthernet0/0 is up, line protocol is up\n  Internet Address 10.0.12.1/30, Area 0\n  Timer intervals configured, Hello 10, Dead 40, Wait 40\n  IP MTU 1500 bytes',
             'show ip ospf neighbor': '(no neighbors shown)'}),
               _t('R2 terminal', 'terminal', commands={
             'show ip ospf interface gi0/0': 'GigabitEthernet0/0 is up, line protocol is up\n  Internet Address 10.0.12.2/30, Area 0\n  Timer intervals configured, Hello 30, Dead 120, Wait 120\n  IP MTU 1500 bytes',
             'show running-config interface gi0/0': 'interface GigabitEthernet0/0\n ip address 10.0.12.2 255.255.255.252\n ip ospf hello-interval 30'})],
         parts=[_p('Parameter preventing adjacency', 'OSPF Hello/Dead timer mismatch', ['OSPF Area ID mismatch on link', 'Subnet mask mismatch (/30 vs /24)', 'IP MTU mismatch across Gi0/0']),
                _p('Current timers on R2 Gi0/0', 'Hello 30 s / Dead 120 s', ['Hello 10 s / Dead 40 s', 'Hello 5 s / Dead 15 s', 'Hello 60 s / Dead 180 s']),
                _p('Command on R2 Gi0/0 to fix', 'no ip ospf hello-interval 30', ['ip ospf mtu-ignore on Gi0/0', 'ip ospf network broadcast', 'passive-interface Gi0/0'])],
         explanation='OSPF neighbors must agree on Hello and Dead intervals, Area ID, and subnet mask. R2 Gi0/0 has a custom 30/120 timer while R1 uses default 10/40; removing the custom hello-interval on R2 restores the adjacency.'),
    dict(id='SIM-N-6', obj='NO-4.1', oid='N:3.4', text='Workstations in VLAN 30 (10.30.0.0/24) obtain 169.254.x.x addresses even though the central DHCP server (10.100.0.50) has an active scope for 10.30.0.0/24. Inspect the distribution router and fix DHCP relay.',
         tabs=[_t('R-DIST terminal', 'terminal', commands={
             'show ip interface gi0/0.30': 'GigabitEthernet0/0.30 is up, line protocol is up\n  Internet address is 10.30.0.1/24\n  Helper address is 10.100.0.5',
             'ping 10.100.0.50': 'Type escape sequence to abort.\n!!!!! (100 percent)',
             'ping 10.100.0.5': 'Type escape sequence to abort.\n..... (0 percent)'}),
               _t('DHCP server inspector', 'inspector', text='Server IP: 10.100.0.50/24\nScope VLAN30: 10.30.0.20 - 10.30.0.200 /24\nRouter (Option 003): 10.30.0.1\nDNS (Option 006): 10.100.0.10\nStatus: Active (0 leases in use)')],
         parts=[_p('Root cause of APIPA on VLAN 30', 'Wrong ip helper-address IP', ['DHCP scope is deactivated', 'Option 003 gateway is wrong', 'VLAN 30 subinterface is down']),
                _p('Current helper address configured', '10.100.0.5 (unreachable)', ['10.100.0.50 (DHCP server)', '10.30.0.1 (subinterface)', '10.100.0.10 (DNS server)']),
                _p('Corrective command on Gi0/0.30', 'ip helper-address 10.100.0.50', ['ip helper-address 10.30.0.1', 'ip dhcp pool VLAN30-LOCAL', 'no ip directed-broadcast'])],
         explanation='DHCP broadcasts do not cross routers unless an IP helper relays UDP 67/68 to the DHCP server. Gi0/0.30 points to 10.100.0.5 instead of 10.100.0.50.'),
    dict(id='SIM-N-7', obj='NO-3.3', oid='N:2.3', text='Clients on the 2nd floor experience frequent drops and high retries on 2.4 GHz Wi-Fi. Inspect the wireless controller survey and fix the channel and security config.',
         tabs=[_t('WLC RF survey', 'terminal', commands={
             'show ap channel 2.4ghz': 'AP Name   Channel   Width   TxPower   Avg Retry%\nAP-2F-W   1         20 MHz  14 dBm    4%\nAP-2F-C   4         40 MHz  20 dBm    38%\nAP-2F-E   6         20 MHz  14 dBm    31%',
             'show wlan summary': 'WLAN 10 Corp-WiFi · Security: WPA2/WPA3 · VLAN 20'}),
               _t('Floor plan', 'topology', nodes=[
             ('AP-2F-W', 'West wing · Channel 1 · 20 MHz'),
             ('AP-2F-C', 'Center hall · Channel 4 · 40 MHz (overlaps Ch 1 and Ch 6)'),
             ('AP-2F-E', 'East wing · Channel 6 · 20 MHz')])],
         parts=[_p('AP causing adjacent-channel interference', 'AP-2F-C on Ch 4 (40 MHz)', ['AP-2F-W on Channel 1 (20 MHz)', 'AP-2F-E on Channel 6 (20 MHz)', 'WLC management VLAN 20']),
                _p('Correct 2.4 GHz channel for AP-2F-C', 'Channel 11 at 20 MHz width', ['Channel 3 at 40 MHz width', 'Channel 9 at 40 MHz width', 'Channel 14 at 80 MHz width']),
                _p('Power adjustment on AP-2F-C', 'Reduce Tx power to 14 dBm', ['Boost Tx power to 30 dBm', 'Disable 5 GHz radio band', 'Enable TKIP encryption'])],
         explanation='In 2.4 GHz, only channels 1, 6, and 11 are non-overlapping at 20 MHz. Channel 4 at 40 MHz overlaps both 1 and 6, causing severe adjacent-channel interference.'),
    dict(id='SIM-N-8', obj='NO-5.3', oid='N:4.3', text='An unauthorized hub was plugged into access port Gi0/12 on SW-IDF3, and a rogue DHCP server began handing out leases. Inspect the switch config and harden the access edge.',
         tabs=[_t('SW-IDF3 terminal', 'terminal', commands={
             'show mac address-table interface gi0/12': 'Vlan  Mac Address       Type     Ports\n10    0050.7966.6801    DYNAMIC  Gi0/12\n10    0050.7966.6802    DYNAMIC  Gi0/12\n10    0050.7966.6803    DYNAMIC  Gi0/12',
             'show ip dhcp snooping': 'Switch DHCP snooping is disabled\nTrusted ports: none'}),
               _t('Config inspector', 'inspector', text='interface Gi0/1 (Uplink to Core + legitimate DHCP server)\n switchport mode trunk\n!\ninterface Gi0/12 (Cubicle wall jack)\n switchport mode access\n switchport access vlan 10')],
         parts=[_p('Feature to block rogue DHCP offers', 'Enable DHCP snooping on VLAN 10', ['Enable STP Root Guard on VLAN 10', 'Enable PortFast on uplink Gi0/1', 'Disable CDP globally on SW-IDF3']),
                _p('Port that needs ip dhcp snooping trust', 'Gi0/1 (trunk uplink to core)', ['Gi0/12 (cubicle wall jack)', 'All access ports Gi0/2-24', 'VLAN 1 management SVI']),
                _p('Limit Gi0/12 to one workstation MAC', 'switchport port-security maximum 1', ['switchport mode dynamic desirable', 'spanning-tree guard loop', 'ip arp inspection trust'])],
         explanation='DHCP snooping drops DHCPOFFER/DHCPACK messages on untrusted access ports while permitting them on the trusted uplink (Gi0/1), and port-security limits Gi0/12 to a single MAC.'),
    dict(id='SIM-N-9', obj='NO-2.3', oid='N:5.2', text='A newly patched 10GBASE-SR fiber link between SW-MDF and SW-IDF4 stays down/down. Inspect the transceiver DOM readings and patch panel notes to fix the link.',
         tabs=[_t('SW-MDF terminal', 'terminal', commands={
             'show interfaces te0/1 transceiver': 'ITU Channel: 850 nm (MMF 10GBASE-SR)\nTx Power: -2.1 dBm   Rx Power: -39.8 dBm (LOS alarm)',
             'show interfaces te0/1 status': 'Port   Name     Status      Vlan   Duplex  Speed  Type\nTe0/1  To-IDF4  notconnect  trunk  full    10G    SFP-10GB-SR'}),
               _t('Patch panel inspector', 'inspector', text='SW-MDF Te0/1: 850 nm 10GBASE-SR SFP+ · OM4 LC duplex jumper (Tx->A, Rx->B)\nSW-IDF4 Te0/1: 850 nm 10GBASE-SR SFP+ · OM4 LC duplex jumper (Tx->A, Rx->B)\nHorizontal run: 90 m OM4 straight-through patch (A->A, B->B)')],
         parts=[_p('Why both SFP+ ports show Rx LOS (-39.8 dBm)', 'Tx/Rx fiber strands uncrossed', ['850 nm optics require OS2 SMF fiber', '90 m exceeds OM4 10GBASE-SR limit', 'Duplex mismatch on 10GbE fiber']),
                _p('Maximum reach of 10GBASE-SR on OM4', '400 meters over OM4 multimode', ['25 meters over OM4 multimode', '10 kilometers over OM4 fiber', '55 meters over OM4 multimode']),
                _p('Corrective action at SW-IDF4 patch panel', 'Roll LC A/B polarity at one end', ['Swap the LC polarity at BOTH ends', 'Replace both SFP+ with 10GBASE-LR', 'Set speed 1000 and half-duplex'])],
         explanation='With straight-through A->A/B->B horizontal fiber and identical jumper polarity on both ends, Tx talks into Tx and Rx listens to Rx. Rolling the duplex LC clip at one end crosses Tx to Rx.'),
    dict(id='SIM-N-10', obj='NO-5.1', oid='N:3.2', text='The NOC SIEM is not receiving syslog alerts from router R-EDGE, and SNMPv3 polling from the NMS (10.100.5.20) times out. Inspect R-EDGE and fix both monitoring feeds.',
         tabs=[_t('R-EDGE terminal', 'terminal', commands={
             'show logging': 'Syslog logging: enabled\n    Trap logging: level notifications, 142 message lines logged\n    Logging to 10.100.5.99 (udp port 514, audit disabled)',
             'show snmp user': 'User name: noc-poller\nEngine ID: 800000090300001\nAuthentication Protocol: SHA\nPrivacy Protocol: None (noPriv)'}),
               _t('NOC collector sheet', 'inspector', text='SIEM syslog receiver: 10.100.5.25 (UDP 514)\nNMS poller: 10.100.5.20 · SNMPv3 group NOC-GRP requires authPriv (SHA + AES-128)')],
         parts=[_p('Why syslog messages miss the SIEM', 'Logging host set to .99 not .25', ['Syslog uses TCP 162 by default', 'Trap level notifications is off', 'Syslog logging is disabled']),
                _p('Why SNMPv3 polls from NMS fail', 'noc-poller is set to noPriv', ['SNMPv3 uses TCP port 514 only', 'Authentication uses SHA instead of MD5', 'Engine ID is missing on R-EDGE']),
                _p('Commands to restore both feeds', 'logging host .25 + priv aes 128', ['logging trap debugging + snmp-server community public', 'logging console warnings + snmpv2c noAuthNoPriv', 'no logging on + snmp-server host 10.100.5.99'])],
         explanation='R-EDGE sends syslog to 10.100.5.99 instead of the SIEM at 10.100.5.25, and the SNMPv3 user is configured without encryption (noPriv) while NOC-GRP requires authPriv (SHA + AES-128).'),
    # ------------------------------------------------------------------ A+ Core 1 220-1201
    dict(id='SIM-A1-1', obj='IT-5.2', oid='A1:2.1', text='Terminate a straight-through patch cable to the T568B standard. Inspect the '
         'pinout card, then choose the colour for each pin.',
         tabs=[_t('Pinout card', 'inspector', text='T568A: 1 W/Grn 2 Grn 3 W/Org 4 Blu 5 W/Blu 6 Org 7 W/Brn 8 Brn\n'
                                                      'Rule: a straight-through cable uses the SAME standard at both ends.'),
               _t('Cable tester', 'terminal', commands={
                   'test cable': 'Wiremap: 1-3 2-6 3-1 6-2 (crossed pairs)\nResult: FAIL - crossover detected, expected straight-through'})],
         parts=[_p('Pin 1', 'White/orange', ['White/green', 'White/blue', 'White/brown']),
                _p('Pin 2', 'Orange', ['Green', 'Blue', 'Brown/white']),
                _p('Pin 3', 'White/green', ['White/orange', 'White/blue', 'White/brown']),
                _p('Pin 6', 'Green', ['Orange', 'Blue', 'Brown'])],
         explanation='T568B swaps the orange and green pairs of T568A: 1 W/Org, 2 Org, 3 W/Grn, 6 Grn. The tester shows '
                     'one end was punched as T568A, which made an unintended crossover.'),
    dict(id='SIM-A1-2', obj='IT-3.1', oid='A1:3.4', text='A technician installs an M.2 NVMe SSD and a second RAM kit, but the new SSD '
         'does not appear as a boot option. Inspect the board, then fix the build.',
         tabs=[_t('Board diagram', 'topology', nodes=[
             ('M2_1', 'M.2 slot · PCIe 4.0 x4 · shares lanes with SATA6 when used'),
             ('M2_2', 'M.2 slot · SATA only (no NVMe) · new SSD is installed here'),
             ('DIMM A2/B2', 'Populate first for dual channel'), ('DIMM A1/B1', 'Second kit installed here'),
             ('SATA6', 'Old SATA SSD (Windows) connected')]),
               _t('UEFI inspector', 'inspector', text='Boot mode: UEFI\nSecure Boot: Enabled\nCSM: Disabled\nBoot #1: Windows Boot Manager (SATA6)\nNVMe devices: none detected')],
         parts=[_p('Move the NVMe SSD to', 'M2_1 (PCIe 4.0 x4)', ['M2_2 (SATA only)', 'SATA6 with an adapter', 'PCIe x1 slot']),
                _p('Side effect to plan for', 'SATA6 port is disabled', ['Dual channel turns off', 'Secure Boot turns off', 'CSM is re-enabled']),
                _p('UEFI boot order after cloning', 'NVMe Boot Manager first', ['SATA6 Boot Manager first', 'Legacy CSM boot first', 'Network PXE boot first'])],
         explanation='An NVMe drive needs a slot wired for PCIe/NVMe; M2_2 is SATA-only so the drive is never detected. '
                     'M2_1 shares lanes with SATA6, so the old SSD port goes dark: clone first, then boot the NVMe entry.'),
    dict(id='SIM-A1-3', obj='IT-3.4', oid='A1:5.3', text='A laptop shows "Limited" Wi-Fi in a hotel. Run the read-only checks, then '
         'pick the fix.',
         tabs=[_t('Laptop terminal', 'terminal', commands={
             'netsh wlan show interfaces': 'State : connected\nSSID : HOTEL-GUEST\nRadio type : 802.11ax\nAuthentication : Open\nSignal : 92%',
             'ipconfig': 'Wireless LAN adapter Wi-Fi:\n   IPv4 Address : 10.40.12.88\n   Default Gateway : 10.40.0.1',
             'nslookup example.com': 'Server: 10.40.0.1\nName: example.com\nAddress: 10.40.0.1  (redirected)'})],
         parts=[_p('Most likely cause', 'Captive portal not completed', ['Weak 2.4 GHz radio signal', 'APIPA address on adapter', 'WPA3 handshake mismatch']),
                _p('Evidence that points to it', 'DNS answers with the gateway', ['Signal strength is 92 percent', 'Radio type is 802.11ax', 'Authentication is Open']),
                _p('Next step', 'Open a browser to sign in', ['Reset the TCP/IP stack', 'Replace the Wi-Fi card', 'Forget all saved networks'])],
         explanation='The laptop has a valid lease and strong signal, but DNS returns the gateway for every name: the '
                     'portal is redirecting until the guest signs in. Opening a browser completes it.'),
    dict(id='SIM-A1-4', obj='IT-4.3', oid='A1:5.6', text='Accounting users report that every page from the departmental laser printer has loose toner that smears when touched and faint ghost images down the page. Inspect the printer status and service it.',
         tabs=[_t('Printer web console', 'terminal', commands={
             'status': 'Model: LaserJet Enterprise M611\nPage count: 224,810 (Maintenance kit interval: 225,000)\nAlerts: 50.2 Fuser Low Temp Warning',
             'supplies': 'Black Toner: 68%\nMaintenance Kit (Fuser + Rollers): 1% remaining'}),
               _t('Test page inspector', 'inspector', text='Symptom 1: Toner rubs off the paper with finger pressure.\nSymptom 2: Faint repeat of the top header appears 94 mm lower on the same sheet.')],
         parts=[_p('Failed component causing unmelted toner', 'Fuser assembly not reaching heat', ['Laser scanner mirror assembly', 'Transfer belt charging roller', 'Pickup and feed rollers in Tray 2']),
                _p('Corrective maintenance action', 'Install the maintenance kit', ['Replace the 68% black toner cart', 'Switch driver from PCL6 to PS', 'Calibrate color registration']),
                _p('Follow-up step after replacement', 'Reset the maintenance page counter', ['Enable duplex printing on Tray 1', 'Power-cycle the print server VM', 'Refill the waste toner bottle'])],
         explanation='Toner that smears off the sheet and a 50.2 fuser low-temperature warning indicate the fuser assembly is failing at the 225,000-page maintenance interval. Installing the maintenance kit and resetting the counter fixes it.'),
    dict(id='SIM-A1-5', obj='IT-2.3', oid='A1:5.1', text='A newly assembled CAD workstation powers on, fans spin at 100%, and the motherboard emits 1 long and 2 short beeps with a blank monitor. Inspect the build and resolve the POST fault.',
         tabs=[_t('Motherboard layout', 'topology', nodes=[
             ('CPU + 8-pin EPS', 'Ryzen 9 7900X · 8-pin EPS12V connected · 24-pin ATX connected'),
             ('PCIe_1 (x16)', 'RTX 4070 workstation GPU seated · 16-pin 12VHPWR power cable UNPLUGGED'),
             ('DIMM_A2 / B2', '2x 32 GB DDR5-5600 seated in primary dual-channel slots'),
             ('Monitor cable', 'DisplayPort plugged into motherboard rear I/O instead of discrete GPU')]),
               _t('POST code table', 'inspector', text='AMI UEFI Beep / LED Codes:\n1 long, 2 short (VGA LED solid): Video card initialization failure / no graphics output detected')],
         parts=[_p('Meaning of 1 long, 2 short POST beeps', 'Graphics card failed to initialize', ['System RAM not detected in A2/B2', 'CPU overheating thermal shutdown', 'CMOS battery voltage below 2.5 V']),
                _p('Hardware power fix required', 'Connect PCIe power to the GPU', ['Move DDR5 modules to A1 and B1', 'Unplug the 8-pin EPS12V CPU cable', 'Replace the 850 W power supply']),
                _p('Display cable fix required', 'Plug DisplayPort into GPU port', ['Switch motherboard to VGA adapter', 'Enable Legacy CSM in UEFI setup', 'Reseat the M.2 NVMe boot drive'])],
         explanation='1 long and 2 short AMI beeps (with VGA LED) indicate video initialization failure because the RTX 4070 lacks its auxiliary PCIe power connector, and the monitor is plugged into the motherboard instead of the discrete GPU.'),
    dict(id='SIM-A1-6', obj='IT-3.2', oid='A1:5.2', text='A small file server running a 4-disk RAID 5 array beeps and reports degraded performance. Inspect the storage controller and recover redundancy without losing data.',
         tabs=[_t('RAID CLI', 'terminal', commands={
             'megacli -LDInfo': 'Virtual Drive: 0 (RAID-5, 4 drives, 12 TB usable)\nState: Degraded\nStrip Size: 64 KB',
             'megacli -PDList': 'Slot 0: Online (4 TB SAS) · 0 media errors\nSlot 1: Online (4 TB SAS) · 0 media errors\nSlot 2: Failed (4 TB SAS) · 418 media errors, S.M.A.R.T. tripped\nSlot 3: Online (4 TB SAS) · 0 media errors'}),
               _t('Server bay notes', 'inspector', text='Hot-swap 3.5" SAS backplane · Slot 2 amber fault LED solid.\nSpare on shelf: 4 TB 12Gb/s SAS 7200 RPM enterprise drive.')],
         parts=[_p('Current fault tolerance of the array', 'Zero more drive failures allowed', ['One more drive can fail safely', 'Two more drives can fail safely', 'Data is already permanently lost']),
                _p('Correct drive replacement action', 'Hot-swap Slot 2 with SAS spare', ['Power down and run RAID 0 init', 'Pull Slot 0 and Slot 1 together', 'Format the virtual drive in OS']),
                _p('What happens after inserting the spare', 'Controller rebuilds parity on 2', ['Array converts to RAID 10 live', 'All shares must be recreated', 'OS partition table is wiped'])],
         explanation='RAID 5 tolerates exactly one drive failure; while degraded, a second failure destroys the array. Hot-swapping the failed Slot 2 drive with the matching 4 TB SAS spare triggers an online parity rebuild.'),
    dict(id='SIM-A1-7', obj='IT-4.2', oid='A1:1.3', text='A travelling executive cannot receive corporate email on an iPhone after a password rotation, and MDM shows the device out of compliance. Inspect the MDM console and restore access.',
         tabs=[_t('MDM device console', 'inspector', text='Device: iPhone 15 Pro (iOS 18.1) · Enrollment: Supervised BYOD\nCompliance status: Non-compliant (Passcode age > 90 days; cached Exchange token expired)\nCorporate Wi-Fi profile: EAP-TLS certificate valid'),
               _t('Mail client log', 'terminal', commands={
             'mail-diag': 'Server: outlook.office365.com (TCP 443)\nAuth method: OAuth2 modern auth\nResult: 401 Unauthorized - token revoked after AD password reset',
             'network-test': '5G Cellular: Connected · DNS: ok · HTTPS 443: reachable'})],
         parts=[_p('Why corporate mail fails with 401', 'OAuth token expired after reset', ['TCP port 443 is blocked on 5G', 'EAP-TLS Wi-Fi cert is expired', 'SIM card eSIM profile is corrupt']),
                _p('Why MDM flags the phone non-compliant', 'Passcode exceeded 90-day policy', ['iOS version is below minimum', 'Phone is jailbroken / rooted', 'Location services are turned off']),
                _p('Steps to restore compliant mail sync', 'Update passcode & re-auth OAuth', ['Factory-reset and wipe the eSIM', 'Switch mail account to POP3 110', 'Remove the MDM management profile'])],
         explanation='Resetting the AD password revoked the OAuth2 refresh token, and the expired device passcode tripped MDM compliance. Updating the passcode and signing in to refresh the OAuth token restores compliance and mail sync.'),
    dict(id='SIM-A1-8', obj='IT-6.1', oid='A1:4.1', text='A developer tries to start two 64-bit Linux VMs in Hyper-V on a workstation, but the hypervisor refuses to start the VMs and the second VM fails with an out-of-memory error. Inspect the host and fix both issues.',
         tabs=[_t('Host PowerShell', 'terminal', commands={
             'systeminfo | findstr /i "hyper-v memory"': 'Total Physical Memory: 16,384 MB\nAvailable Physical Memory: 3,900 MB\nHyper-V Requirements: Virtualization Enabled In Firmware: No',
             'Get-VM': 'Name     State  MemoryAssigned  StartupMemory\nDev-DB   Off    0M              8192M\nDev-App  Off    0M              8192M'}),
               _t('UEFI CPU settings', 'inspector', text='Processor: Intel Core i7-13700\nIntel VT-x (Virtualization Technology): Disabled\nVT-d (IOMMU): Disabled')],
         parts=[_p('Firmware setting needed to start 64-bit VMs', 'Enable Intel VT-x in UEFI', ['Disable Secure Boot in UEFI', 'Enable Legacy CSM boot mode', 'Turn off CPU hyper-threading']),
                _p('Why both 8 GB VMs cannot start on a 16 GB host', '16 GB host RAM overcommitted', ['Hyper-V only supports 32-bit guests', 'VT-d blocks dual VM startup', 'Virtual switch lacks a VLAN ID']),
                _p('Memory adjustment to run both VMs concurrently', 'Set 4-6 GB per VM or add RAM', ['Set both VMs to 16 GB static RAM', 'Disable host Windows pagefile', 'Switch virtual disk to IDE bus'])],
         explanation='64-bit guests require hardware virtualization (Intel VT-x / AMD-V) enabled in UEFI, and two VMs requesting 8 GB each leave zero RAM for the host OS on a 16 GB workstation.'),
    dict(id='SIM-A1-9', obj='IT-5.4', oid='A1:2.5', text='Two new PoE+ PTZ security cameras (24 W each) connected to an 8-port PoE switch keep rebooting whenever their pan/tilt motors engage. Inspect the switch PoE budget and fix the installation.',
         tabs=[_t('SW-CAM terminal', 'terminal', commands={
             'show power inline': 'Available: 65.0(w)  Used: 61.2(w)  Remaining: 3.8(w)\nInterface  Admin  Oper  Power(W)  Class  Device\nGi0/1-4    auto   on    15.3      3      Access-Point (x4 = 61.2 W)\nGi0/5      auto   off   0.0       4      PTZ-Cam-1 (denied: power budget)\nGi0/6      auto   off   0.0       4      PTZ-Cam-2 (denied: power budget)'}),
               _t('Equipment spec sheet', 'inspector', text='SW-CAM: 802.3af/at switch · Total PoE budget: 65 W\nPTZ Camera spec: IEEE 802.3at (PoE+ Class 4, up to 25.5 W peak per camera)')],
         parts=[_p('IEEE standard required by each 24 W PTZ camera', '802.3at PoE+ (up to 30 W)', ['802.3af PoE (up to 15.4 W per port)', '802.1Q VLAN tagging on trunks', '802.1X port-based access control']),
                _p('Why Gi0/5 and Gi0/6 shut off under load', '65 W PoE budget is exhausted', ['Cat 6A cable cannot carry PoE+', 'Cameras require crossover cables', 'Switch ports are in half-duplex']),
                _p('Best hardware remediation', 'Use PoE+ injectors or bigger switch', ['Force ports to 802.3af 15.4 W mode', 'Replace Cat 6 runs with fiber', 'Lower the switch MTU to 1400'])],
         explanation='Four APs already draw 61.2 W of the switch’s 65 W total PoE budget, leaving only 3.8 W for two 24 W Class 4 (802.3at PoE+) PTZ cameras. Adding midspan 802.3at PoE+ injectors or a higher-wattage PoE+ switch resolves it.'),
    dict(id='SIM-A1-10', obj='IT-4.1', oid='A1:5.4', text='A field technician’s tablet trackpad cursor jumps erratically and the bottom bezel is lifting away from the aluminum frame. Inspect the device diagnostics and choose the safe procedure.',
         tabs=[_t('Tablet hardware log', 'terminal', commands={
             'battery-diag': 'Cycle count: 890\nDesign capacity: 6,800 mAh\nCurrent full capacity: 3,120 mAh (45%)\nPack temperature: 48 C · Internal gas pressure warning'}),
               _t('Physical inspection', 'inspector', text='Visual check: Lower chassis seam pushed open 4 mm directly beneath the trackpad assembly.\nSweet metallic odor near the vent slot.')],
         parts=[_p('Root cause of the lifted bezel and erratic trackpad', 'Swollen Li-ion battery pack', ['Corrupt HID trackpad driver in OS', 'Loose Wi-Fi antenna coax lead', 'Cracked LCD backlight inverter']),
                _p('Immediate safety action', 'Power off unplug & isolate unit', ['Puncture the pack to release gas', 'Clamp the bezel shut with tape', 'Run a full charge/discharge cycle']),
                _p('Proper disposal and repair path', 'Replace & use hazmat recycling', ['Throw old battery in office trash', 'Reflow battery cells with heat gun', 'Reinstall OS and recalibrate touch'])],
         explanation='A bulging chassis beneath the trackpad pushes against the touchpad sensor and indicates a swollen lithium-ion pouch cell. It must be powered down immediately, never punctured or compressed, and recycled through certified hazardous battery disposal.'),
    # ------------------------------------------------------------------ A+ Core 2 220-1202
    dict(id='SIM-A2-1', obj='IT-8.2', oid='A2:1.6', text='Remote Desktop to PC-FIN07 fails from the help desk. Inspect the services and '
         'firewall, then configure the PC.',
         tabs=[_t('PowerShell', 'terminal', commands={
             'Get-Service TermService': 'Status   Name         DisplayName\nStopped  TermService  Remote Desktop Services',
             'Get-NetFirewallRule -DisplayGroup "Remote Desktop"': 'DisplayName: Remote Desktop - User Mode (TCP-In)\nEnabled: False\nProfile: Domain',
             'Get-NetConnectionProfile': 'Name: corp.local\nNetworkCategory: DomainAuthenticated'}),
               _t('Settings inspector', 'inspector', text='System > Remote Desktop: Off\nNetwork Level Authentication: Required\nEdition: Windows 11 Pro')],
         parts=[_p('Setting to change first', 'Turn Remote Desktop on', ['Turn NLA requirement off', 'Upgrade to Enterprise', 'Set network to Public']),
                _p('Firewall rule state', 'Enable RDP rule (Domain)', ['Disable RDP rule (Domain)', 'Enable RDP rule (Public)', 'Open all inbound ports']),
                _p('Port the rule allows', 'TCP 3389', ['TCP 3398', 'UDP 3388', 'TCP 5900'])],
         explanation='Remote Desktop is off (so TermService is stopped) and the inbound rule is disabled. Turning RDP on '
                     'enables the service and, with the Domain-profile rule enabled, TCP 3389 is allowed. NLA can stay on.'),
    dict(id='SIM-A2-2', obj='IT-11.1', oid='A2:3.1', text='A user reports pop-ups and a browser homepage that keeps changing. Inspect '
         'the PC and order your response like the malware-removal process.',
         tabs=[_t('Task Manager', 'inspector', text='Startup apps:\n  SearchHelperPro  Enabled  High impact\n  OneDrive         Enabled  Low impact\nBrowser extension: "Coupon Wizard" (installed today)'),
               _t('Command prompt', 'terminal', commands={
                   'netstat -ano': 'TCP 10.0.0.44:51022  185.199.110.9:443  ESTABLISHED  6120\nTCP 10.0.0.44:51040  13.107.42.14:443  ESTABLISHED  3304',
                   'tasklist /fi "pid eq 6120"': 'Image Name: SearchHelperPro.exe   PID 6120'})],
         parts=[_p('Step 1 after confirming symptoms', 'Quarantine the infected PC', ['Disable System Restore now', 'Reimage the PC right away', 'Email the user the logs']),
                _p('Step 2', 'Disable System Restore', ['Re-enable System Restore', 'Schedule weekly scans', 'Educate the end user']),
                _p('Item to remove', 'SearchHelperPro + extension', ['OneDrive startup app entry', 'TCP 3304 connection', 'Windows Defender files']),
                _p('Final step', 'Educate the end user', ['Quarantine the system', 'Disable System Restore', 'Identify the symptoms'])],
         explanation='CompTIA order: investigate symptoms, quarantine, disable System Restore (Windows), remediate, '
                     'schedule scans, re-enable System Restore and make a restore point, then educate the user. '
                     'SearchHelperPro (PID 6120) and the new extension are the adware.'),
    dict(id='SIM-A2-3', obj='IT-10.2', oid='A2:2.6', text='A shared folder must give the Finance group change access and everyone '
         'else no access. Inspect the effective permissions, then set them.',
         tabs=[_t('icacls', 'terminal', commands={
             'icacls D:\\Finance': 'D:\\Finance BUILTIN\\Users:(OI)(CI)(RX)\n            CORP\\Finance:(OI)(CI)(RX)\n            BUILTIN\\Administrators:(OI)(CI)(F)',
             'net share Finance': 'Share name  Finance\nPath        D:\\Finance\nPermission  Everyone, READ'})],
         parts=[_p('Share permission for Everyone', 'Change (or Full)', ['Read only share', 'Deny full control', 'No share entry']),
                _p('NTFS entry for CORP\\Finance', 'Modify', ['Read & execute', 'List', 'Write']),
                _p('NTFS entry for BUILTIN\\Users', 'Remove the entry', ['Set it to Modify', 'Add Deny Read', 'Leave it as RX'])],
         explanation='The most restrictive of share and NTFS permissions wins. Share Change/Full lets NTFS decide; Finance '
                     'gets Modify, and removing Users (rather than a Deny that could hit Finance members) blocks everyone else.'),
    dict(id='SIM-A2-4', obj='IT-8.3', oid='A2:3.1', text='After a power outage, a Windows 11 workstation displays "BOOTMGR is missing / No bootable device" even though UEFI detects the NVMe SSD. Inspect the WinRE command prompt and repair the boot configuration.',
         tabs=[_t('WinRE diskpart & bcdedit', 'terminal', commands={
             'diskpart -> list vol': 'Volume 0  C   Windows   NTFS   Partition  475 GB  Healthy\nVolume 1  S   SYSTEM    FAT32  Partition  100 MB  Healthy (EFI System)',
             'bcdedit /enum': 'The boot configuration data store could not be opened.\nThe system cannot find the file specified.',
             'sfc /scannow': 'Windows Resource Protection did not find any integrity violations.'}),
               _t('System configuration', 'inspector', text='Partition style: GPT · Firmware mode: UEFI native (CSM off)\nWindows installation present at C:\\Windows')],
         parts=[_p('Why the system fails to boot into Windows', 'UEFI BCD store is corrupted', ['C:\\Windows OS files are deleted', 'NVMe SSD has a physical failure', 'Drive is formatted as ext4 Linux']),
                _p('WinRE command to rebuild the UEFI BCD store', 'bcdboot C:\\Windows /s S: /f UEFI', ['fdisk /mbr on Disk 0 partition', 'chkdsk C: /f /r from desktop', 'gpupdate /force /boot in WinRE']),
                _p('Partition that holds the UEFI boot loader', 'FAT32 EFI System Partition (S:)', ['475 GB NTFS Windows volume (C:)', '16 MB Microsoft Reserved (MSR)', 'USB WinRE installer thumb drive'])],
         explanation='On a UEFI/GPT system, the boot loader and BCD store live on the FAT32 EFI System Partition (Volume S:). Running bcdboot C:\\Windows /s S: /f UEFI copies fresh UEFI boot files and rebuilds the BCD store.'),
    dict(id='SIM-A2-5', obj='IT-9.1', oid='A2:1.9', text='A Linux web developer updated /etc/nginx/sites-enabled/app.conf, but the web server still serves the old config and a backup script /opt/scripts/backup.sh fails with "Permission denied". Fix both issues.',
         tabs=[_t('Linux bash terminal', 'terminal', commands={
             'ls -l /opt/scripts/backup.sh': '-rw-r--r-- 1 root devops 1840 Oct 26 09:12 /opt/scripts/backup.sh',
             'systemctl status nginx': 'Active: active (running) since Mon 08:00 UTC; config not reloaded',
             'nginx -t': 'nginx: the configuration file /etc/nginx/nginx.conf syntax is ok\nnginx: configuration file test is successful'}),
               _t('Cron / user inspector', 'inspector', text='Current user: deploy (member of group devops)\nTask 1: Make /opt/scripts/backup.sh executable by owner and group only.\nTask 2: Apply the tested nginx config via systemd.')],
         parts=[_p('Why /opt/scripts/backup.sh fails to run', 'Missing execute (x) bit (644)', ['Script is owned by root user', 'Disk /opt is mounted read-only', 'Bash shell is not installed']),
                _p('Command to grant rwxr-x--- permissions', 'sudo chmod 750 /opt/scripts/backup.sh', ['sudo chmod 666 /opt/scripts/backup.sh', 'sudo chown nobody /opt/scripts/backup.sh', 'sudo chmod 400 /opt/scripts/backup.sh']),
                _p('Command to apply the verified nginx config', 'sudo systemctl reload nginx', ['sudo apt remove nginx-common', 'sudo kill -9 1 (systemd init)', 'sudo echo reload > /etc/hosts'])],
         explanation='Mode 644 (-rw-r--r--) lacks execute bits; chmod 750 sets rwxr-x--- so owner root and group devops can execute it. Running sudo systemctl reload nginx applies the verified configuration cleanly.'),
    dict(id='SIM-A2-6', obj='IT-13.2', oid='A2:1.5', text='Domain workstations in the Accounting OU can ping servers by IP (10.20.1.10) but fail to resolve internal hostnames after a DNS migration, and a new logon banner GPO has not yet applied. Inspect the client and fix it.',
         tabs=[_t('Client Command Prompt', 'terminal', commands={
             'ipconfig /all': 'DNS Servers . . . . . . . . . . . : 10.20.1.10\nPrimary Dns Suffix  . . . . . . . : corp.example.com',
             'nslookup files01.corp.example.com': 'Server: dc01.corp.example.com\nAddress: 10.20.1.10\nName: files01.corp.example.com\nAddress: 10.20.1.55 (new IP)',
             'ping files01.corp.example.com': 'Pinging files01.corp.example.com [10.20.1.199] with 32 bytes of data:\nRequest timed out. (stale cached record)'}),
               _t('GPO inspector', 'inspector', text='Linked GPO: Accounting-Logon-Banner (linked 10 minutes ago)\nLocal DNS resolver cache still holds old IP 10.20.1.199 (TTL 86400 s).')],
         parts=[_p('Why ping uses 10.20.1.199 while nslookup returns .55', 'Stale local DNS resolver cache', ['DNS server 10.20.1.10 is offline', 'Default gateway is misconfigured', 'TCP/IPv4 stack is uninstalled']),
                _p('Command to clear the stale DNS cache', 'ipconfig /flushdns', ['ipconfig /release', 'netstat -r', 'arp -d *']),
                _p('Command to pull the new GPO immediately', 'gpupdate /force', ['gpresult /r', 'sfc /scannow', 'net use * /delete'])],
         explanation='nslookup queries the DNS server directly (.55), whereas ping uses the Windows DNS client resolver cache (.199). Running ipconfig /flushdns purges the stale cache, and gpupdate /force refreshes Group Policy immediately.'),
    dict(id='SIM-A2-7', obj='IT-10.1', oid='A2:2.7', text='A lost corporate laptop was recovered, and an audit revealed that a shared local Administrator account with no lockout policy and an unencrypted SSD were in use. Harden the workstation to policy.',
         tabs=[_t('Security audit output', 'terminal', commands={
             'manage-bde -status C:': 'Volume C: [Windows]\n    Conversion Status: Fully Decrypted\n    Protection Status: Protection Off',
             'net accounts': 'Lockout threshold: Never\nMinimum password length: 6\nMaximum password age (days): Unlimited',
             'net localgroup Administrators': 'Members: Administrator, Guest, CORP\\Domain Admins'}),
               _t('Hardening baseline', 'inspector', text='1. Full-disk encryption with TPM + PIN required on C:\n2. Account lockout after 5 invalid attempts; Guest disabled\n3. Standard domain accounts for daily work; UAC at default')],
         parts=[_p('Protect data at rest on Volume C:', 'Enable BitLocker with TPM', ['Run Disk Defragmenter on C:', 'Share C:\\ with Everyone Read', 'Convert NTFS volume to FAT32']),
                _p('Remediate the local account findings', 'Disable Guest & set lockout 5', ['Add Everyone to Administrators', 'Set minimum password length 0', 'Turn off User Account Control']),
                _p('Daily user privilege best practice', 'Use standard user + UAC prompt', ['Use shared local Administrator', 'Disable Windows Defender service', 'Store admin password in .bat'])],
         explanation='Workstation hardening requires full-disk encryption (BitLocker with TPM), disabling the built-in Guest account, configuring an account lockout threshold (5 attempts), and enforcing least privilege with standard accounts and UAC.'),
    dict(id='SIM-A2-8', obj='IT-12.1', oid='A2:4.2', text='An administrator pushed a registry script directly to 400 production call-center PCs at 10:30 AM without testing or approval, breaking the softphone app. Review the change record and enforce change management.',
         tabs=[_t('Incident timeline', 'inspector', text='10:30 AM: Unannounced registry script pushed to 400 production PCs.\n10:34 AM: All 400 call-center softphones fail to launch (DLL path overwritten).\nChange ticket: None · Sandbox test: None · Backout script: Available on admin desktop'),
               _t('Endpoint console', 'terminal', commands={
             'reg query HKLM\\Software\\SoftPhone': 'InstallPath    REG_SZ    C:\\Program Files (x86)\\TypoPath\\  (broken)',
             'status': '388 agents offline from call queue · SLA breach imminent'})],
         parts=[_p('Immediate action to restore call-center service', 'Run rollback script immediately', ['Format all 400 PCs from USB', 'Wait for next month patch window', 'Delete the softphone executable']),
                _p('Steps skipped before the 10:30 AM push', 'Sandbox test + CAB + window', ['Disabling Windows Firewall first', 'Giving call agents local Admin', 'Turning off system restore points']),
                _p('Final step after service is verified restored', 'Document incident in the ticket', ['Erase the deployment server logs', 'Push another untested script live', 'Disable change board reviews'])],
         explanation='When an unapproved production change causes an outage, executing the rollback plan restores service fastest. Proper change management requires sandbox testing, risk analysis, CAB approval, a scheduled window, and post-incident documentation.'),
    dict(id='SIM-A2-9', obj='IT-9.2', oid='A2:1.8', text='A graphic designer’s MacBook Pro (macOS Sonoma) becomes unresponsive while exporting a project, and Time Machine reports that backups have not completed in 42 days. Inspect the Mac and resolve both issues.',
         tabs=[_t('macOS Terminal', 'terminal', commands={
             'ps aux | head -n 5': 'USER   PID  %CPU %MEM COMMAND\nava   3912 198.4 62.1 /Applications/VectorRender.app (Not Responding)',
             'tmutil status': 'BackupPhase = MountFailed; Destination = smb://nas01.local/TimeMachine (credentials expired)',
             'diskutil apfs list': 'APFS Container disk3: 1.0 TB capacity · 412 GB free · FileVault: Yes (Unlocked)'}),
               _t('System Settings inspector', 'inspector', text='Force Quit Applications window: VectorRender (Not Responding)\nTime Machine: NAS share smb://nas01.local/TimeMachine requires updated Keychain password')],
         parts=[_p('Stop the hung VectorRender application cleanly', 'Force Quit or kill PID 3912', ['Run diskutil eraseVolume APFS', 'Disable FileVault encryption', 'Delete /System/Library folder']),
                _p('Why Time Machine backups have failed for 42 days', 'Expired SMB login in Keychain', ['APFS container has 0 bytes free', 'FileVault blocks Time Machine', 'Spotlight index is rebuilding']),
                _p('Restore automated macOS backups', 'Update Keychain & run backup', ['Format the Mac startup volume', 'Uninstall XProtect definitions', 'Boot into Single-User recovery'])],
         explanation='A hung macOS app is terminated with Force Quit (Cmd+Opt+Esc) or kill/killall in Terminal. tmutil status shows MountFailed due to expired SMB credentials in Keychain; updating the credential resumes Time Machine backups.'),
    dict(id='SIM-A2-10', obj='IT-10.2', oid='A2:2.11', text='A remote bookkeeper reports certificate warnings on every banking site and unexpected search redirects in Chrome. Inspect the browser and Windows proxy settings to clean up the hijacker.',
         tabs=[_t('Browser & Proxy inspector', 'inspector', text='Installed Extensions: "PDF-Free-Search-Bar" (ID: xk99, sideloaded, reads all site data)\nSystem Proxy: Manual proxy enabled -> 127.0.0.1:8888 (local MITM ad-injector)\nDNS over HTTPS (Secure DNS): Disabled'),
               _t('PowerShell terminal', 'terminal', commands={
             'Get-ItemProperty "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"': 'ProxyEnable : 1\nProxyServer : 127.0.0.1:8888',
             'netstat -ano | findstr 8888': 'TCP 127.0.0.1:8888 0.0.0.0:0 LISTENING 7420 (adproxy.exe)'})],
         parts=[_p('Why banking sites show TLS certificate warnings', 'Local proxy intercepts HTTPS', ['Bank servers use TCP port 80', 'Secure DNS (DoH) is turned off', 'Chrome pop-up blocker is active']),
                _p('Browser & proxy remediation steps', 'Remove extension & proxy setting', ['Install self-signed root cert', 'Lower TLS version to SSL 3.0', 'Allow pop-ups for all websites']),
                _p('Post-cleanup browser hardening', 'Clear cache & enable Secure DNS', ['Save banking passwords in plain text', 'Turn off automatic browser updates', 'Enable third-party sideloading'])],
         explanation='The rogue proxy on 127.0.0.1:8888 intercepts TLS traffic (triggering certificate warnings) and the sideloaded extension hijacks searches. Killing/removing the proxy and extension, clearing site data, and enabling Secure DNS fixes it.'),
    # ------------------------------------------------------------------ Tech+ FC0-U71
    dict(id='SIM-T-1', obj='IT-8.1', oid='T:3.1', text='A user on a shared Windows 11 workstation reports their system is sluggish and '
         'cannot save files to the D: data volume. Inspect the workstation and choose the remediation steps.',
         tabs=[_t('Workstation terminal', 'terminal', commands={
             'systeminfo': 'OS Name: Microsoft Windows 11 Education\nTotal Physical Memory: 16,384 MB\nAvailable Physical Memory: 410 MB',
             'tasklist': 'Image Name          PID   Mem Usage\nrender_preview.exe  4812  12,480,000 K\nexplorer.exe        2104     118,000 K',
             'fsutil volume diskfree D:': 'Total free bytes        : 0 (0.0 MB)\nTotal bytes             : 34,359,738,368 (32.0 GB)'}),
               _t('Disk & Startup inspector', 'inspector', text='Volume D: (NTFS) — 100% full (C:\\Temp_Captures redirected to D:\\Scratch)\nStartup impact: render_preview.exe (High, runaway background loop)')],
         parts=[_p('Runaway memory process to stop', 'render_preview.exe (PID 4812)', ['explorer.exe shell (PID 2104)', 'Windows Boot Manager service', 'NTFS volume shadow service']),
                _p('Why saves to D: fail', 'Volume D: has 0 bytes free', ['Volume D: is formatted ext4', 'RAM is below 64 GB minimum', 'User lacks read permission']),
                _p('Preventive fix', 'Disable runaway app & clear D:\\Scratch', ['Reformat C: system volume as FAT32', 'Disable Windows Defender real-time', 'Set system paging file to 0 MB max'])],
         explanation='tasklist shows render_preview.exe consuming over 12 GB of RAM, and fsutil shows 0 bytes free on D:. '
                     'Stopping/disabling the runaway startup process and clearing D:\\Scratch restores both performance and saves.'),
    dict(id='SIM-T-2', obj='IT-10.2', oid='T:6.1', text='An office manager needs a secure wireless network for staff laptops and a '
         'separate guest network that cannot reach internal accounting servers. Review the router settings and complete the setup.',
         tabs=[_t('Router Wi-Fi inspector', 'inspector', text='SSID 1: Novak-Staff · Security: Open (none) · VLAN 10 (10.10.10.0/24)\n'
                                                             'SSID 2: Novak-Guest · Security: WPA2-PSK · VLAN 10 (bridged to internal LAN)\n'
                                                             'Admin portal: http://10.10.10.1 (default password: admin)'),
               _t('Security policy', 'topology', nodes=[
                   ('Staff Wi-Fi', 'Must use modern personal encryption + strong passphrase on internal VLAN 10'),
                   ('Guest Wi-Fi', 'Must be isolated from VLAN 10 accounting servers (client isolation / guest VLAN)'),
                   ('Router Admin', 'Must require a unique strong admin password and MFA where supported')])],
         parts=[_p('Encryption for Novak-Staff', 'WPA3-Personal (SAE)', ['Open with MAC filter', 'WEP 64-bit shared key', 'Disable SSID broadcast']),
                _p('Isolation for Novak-Guest', 'Enable guest VLAN + client isolation', ['Bridge guest clients onto VLAN 10', 'Assign static IPs on staff VLAN 10', 'Turn off DHCP server on VLAN 10']),
                _p('Router management hardening', 'Change default admin password', ['Leave admin/admin on internal LAN', 'Enable WAN Telnet access on TCP 23', 'Share admin login with guest users'])],
         explanation='Staff Wi-Fi requires WPA3-Personal (or WPA2/WPA3), guest Wi-Fi must be segmented on an isolated VLAN '
                     'with client isolation so guests cannot reach internal servers, and default router credentials must be changed.'),
    dict(id='SIM-T-3', obj='IT-7.1', oid='T:1.2', text='All 18 desktop PCs in Training Room B lost internet access at 9:00 AM, while Wi-Fi laptops in the hallway still work. Inspect the room switch and apply the CompTIA troubleshooting methodology.',
         tabs=[_t('Room B checks', 'terminal', commands={
             'ipconfig (Room B PC)': 'IPv4 Address: 10.20.4.31/24 · Default Gateway: 10.20.4.1',
             'ping 10.20.4.1': 'Request timed out. (4/4 lost)',
             'SW-ROOMB status': 'Port Gi0/24 (Uplink to MDF router): unplugged / link down (cleaning crew bumped patch cord)'}),
               _t('Methodology notes', 'inspector', text='Step 1: Identify the problem (gather info, check scope: all 18 wired PCs in Room B).\nStep 2: Establish a theory of probable cause (question the obvious: physical uplink).\nStep 3: Test the theory -> Step 4: Plan & implement -> Step 5: Verify -> Step 6: Document.')],
         parts=[_p('Why checking the Room B switch uplink comes first', 'All 18 wired PCs failed at once', ['Each PC has a bad NIC driver', 'Every monitor cable is loose', 'The internet ISP is down citywide']),
                _p('Corrective action after testing the theory', 'Reconnect Gi0/24 uplink cable', ['Reinstall Windows on all 18 PCs', 'Replace all 18 desktop PSUs', 'Assign APIPA addresses by hand']),
                _p('Final two steps of the methodology', 'Verify functionality & document', ['Establish a new theory and reboot', 'Skip verification and close ticket', 'Escalate directly to ISP tier 3'])],
         explanation='When an entire room of wired PCs fails simultaneously, questioning the obvious points to the shared switch uplink (Gi0/24). Reconnecting the cable, verifying internet access on the PCs, and documenting the fix completes the methodology.'),
    dict(id='SIM-T-4', obj='IT-13.1', oid='T:4.1', text='An IT intern wrote a nightly PowerShell script to check free disk space and archive old log files, but the script never triggers the warning branch even when free space is 2 GB. Inspect the script and fix the logic bug.',
         tabs=[_t('PowerShell script', 'inspector', text='1: $thresholdGB = 10\n2: $freeGB = (Get-PSDrive C).Free / 1GB   # returns 2.4\n3: if ($freeGB -gt $thresholdGB) {\n4:     Write-Output "ALERT: Low disk space on C:"\n5: } else {\n6:     Write-Output "OK: Sufficient space"\n7: }'),
               _t('Script test run', 'terminal', commands={
             'pwsh ./check_disk.ps1': 'Current $freeGB = 2.4\nOutput: OK: Sufficient space\nExit code: 0'})],
         parts=[_p('Programming construct on lines 3-7', 'Conditional branching (if / else)', ['Infinite while loop iteration', 'Relational database foreign key', 'Compiled machine-code binary']),
                _p('Logic bug on line 3', 'Uses -gt instead of -lt operator', ['$thresholdGB is a string literal', 'Get-PSDrive deletes Volume C:', 'Write-Output requires TCP 443']),
                _p('Corrected line 3 condition', 'if ($freeGB -lt $thresholdGB)', ['if ($freeGB -eq 999999)', 'while ($thresholdGB -gt 0)', 'for ($freeGB = 0; $freeGB++)'])],
         explanation='The script checks if $freeGB -gt $thresholdGB (2.4 > 10), which is false when disk space is low. Changing the comparison operator to -lt (less than) triggers the low-space alert whenever free space drops below 10 GB.'),
    dict(id='SIM-T-5', obj='IT-12.3', oid='T:5.1', text='A dental clinic’s patient scheduling database server suffered a drive failure on Wednesday at 2:00 PM. Review the backup schedule and SQL log to restore the database with minimal data loss.',
         tabs=[_t('Backup catalog', 'inspector', text='Sunday 02:00 AM: Full backup (verified) -> Onsite NAS + Offsite Cloud\nMon / Tue 02:00 AM: Incremental backups (verified)\nHourly 00:00..13:00 Wed: Transaction log backups (verified)\nTarget RPO: <= 1 hour · Target RTO: <= 2 hours'),
               _t('Database restore console', 'terminal', commands={
             'db-verify-backups': 'Sun-Full.bak: OK · Mon-Inc.bak: OK · Tue-Inc.bak: OK · Wed-Logs-01..13.trn: OK',
             'storage-status': 'Replacement NVMe mirror online and ready for restore'})],
         parts=[_p('Correct restore sequence for incremental backups', 'Sun Full + Mon/Tue Inc + logs', ['Sunday Full + Tuesday Inc only', 'Wednesday 13:00 log file alone', 'Monday Inc without Sunday Full']),
                _p('Why the clinic meets the 3-2-1 backup rule', '3 copies: prod, NAS & cloud', ['Three full backups on one USB', 'Backups run only once a month', 'Database has three SQL tables']),
                _p('Maximum data loss (actual RPO) achieved', 'Up to 1 hour (1 PM log backup)', ['3 full days since Sunday 2 AM', 'Zero backups exist off-server', '7 full days of appointments'])],
         explanation='Restoring an incremental chain requires the last Full backup plus every subsequent Incremental backup in order (Mon and Tue), followed by Wednesday’s hourly transaction logs, achieving the 1-hour RPO.'),
    dict(id='SIM-T-6', obj='IT-10.4', oid='T:6.2', text='An employee received an urgent email claiming to be from "IT Helpdesk <support@micros0ft-login-verify.com>" asking them to scan a QR code and enter their corporate password and MFA code. Analyze the incident and respond.',
         tabs=[_t('Email header inspector', 'inspector', text='From: IT Helpdesk <support@micros0ft-login-verify.com>\nSPF: fail · DKIM: none · DMARC: reject (quarantine bypassed via personal webmail)\nBody: "Scan this QR code with your phone within 15 minutes or your account will be deleted!"'),
               _t('Sign-in audit log', 'terminal', commands={
             'auth-log --user jsmith': '11:04 UTC: QR link opened -> https://micros0ft-login-verify.com/login\n11:05 UTC: Password submitted + MFA push approved from IP 198.51.100.77 (unfamiliar country)\n11:06 UTC: Inbox forwarding rule created to external address'})],
         parts=[_p('Social engineering attack vector used', 'QR phishing + look-alike domain', ['Physical tailgating at badge door', 'USB drop keylogger in parking lot', 'On-path ARP poisoning on LAN']),
                _p('Immediate containment actions for jsmith', 'Revoke sessions & reset password', ['Reply to the sender to unsubscribe', 'Disable SPF and DMARC on domain', 'Grant jsmith Domain Admin rights']),
                _p('Stronger MFA control that blocks domain spoofing', 'FIDO2 / WebAuthn security key', ['SMS 6-digit text message codes', 'Security questions (mother maiden)', 'Shorter 6-character passwords'])],
         explanation='The attacker used a look-alike domain (micros0ft-login-verify.com) and a QR code (quishing) to steal credentials and an MFA approval. Revoking sessions, resetting credentials, removing the rogue inbox rule, and moving to FIDO2/WebAuthn prevents replay on spoofed domains.'),
]


def items():
    """Bank-format items (practice.bank() merges these). obj = the CIWT course objective (mapping.CURATED maps it
    to the exam objective oid), so mastery evidence and ladder remediation land on the exact lesson section."""
    out = []
    for s in SIMS:
        exam = s['oid'].split(':')[0]
        raw = dict(s, type='sim_pbq', exam=exam, review=REVIEW, bank_id=s['id'],
                   prompts=[p['prompt'] for p in s['parts']])
        out.append({'id': s['id'], 'source': 'sim', 'obj': s['obj'], 'text': s['text'], 'options': [],
                    'correct': [p['correct'] for p in s['parts']], 'explanation': s['explanation'],
                    'type': 'sim_pbq', 'cert': [s['oid']], 'raw': raw})
    return out


def by_exam(exam):
    return [(s['id'], s['oid']) for s in SIMS if s['oid'].startswith(exam + ':')]
