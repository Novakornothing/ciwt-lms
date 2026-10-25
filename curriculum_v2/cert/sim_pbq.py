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
