"""Rapid-fire Port, Protocol, Acronym & Command Speed-Drill with spaced repetition (Option B pass 4).

98 high-yield recall cards in four categories, each tagged with the exams it serves (A1 = 220-1201, A2 = 220-1202,
N = N10-009). Two modes: a 60-second timed Blitz (4 options, streak counter, instant feedback, missed-card retry queue)
and Flip-Card study (Got it / Review again). Results are stored per user and card (Leitner box 1-5); the deck is
ordered so low boxes and long-unseen cards come first. Blitz distractors come from the same category and are
length-balanced so the key is never >= 1.15x the longest distractor. Pending SME review.
"""
import json
import random

from flask import abort, render_template, request
from flask_login import current_user, login_required

REVIEW = 'Pending SME review'
CATEGORIES = {
    'ports': 'Ports & Protocols',
    'specs': 'IEEE / Wi-Fi / Cable & Hardware Specs',
    'cli': 'CLI Commands (Windows, Linux, Cisco IOS)',
    'acronyms': 'Acronyms & Security/Cloud Concepts',
}
EXAM_CODES = {'T': 'FC0-U71', 'A1': '220-1201', 'A2': '220-1202', 'N': 'N10-009'}
BLITZ_SECONDS = 60
BALANCE = 1.15

_P, _S, _C, _A = 'ports', 'specs', 'cli', 'acronyms'
_RAW = [
    # ---------------------------------------------------------------- ports & protocols
    (_P, 'A1 N', 'FTP', 'TCP 20/21'), (_P, 'A1 N', 'SSH / SFTP', 'TCP 22'), (_P, 'A1 N', 'Telnet', 'TCP 23'),
    (_P, 'A1 N', 'SMTP (relay / submission)', 'TCP 25 / 587'), (_P, 'A1 N', 'DNS', 'UDP/TCP 53'),
    (_P, 'A1 N', 'DHCP (server / client)', 'UDP 67 / 68'), (_P, 'A1 N', 'TFTP', 'UDP 69'), (_P, 'A1 N', 'HTTP', 'TCP 80'),
    (_P, 'A1 N', 'Kerberos', 'TCP/UDP 88'), (_P, 'A1 N', 'POP3 / POP3S', 'TCP 110 / 995'), (_P, 'N', 'NTP', 'UDP 123'),
    (_P, 'A1 N', 'NetBIOS', 'TCP/UDP 137-139'), (_P, 'A1 N', 'IMAP / IMAPS', 'TCP 143 / 993'),
    (_P, 'A1 N', 'SNMP (polls / traps)', 'UDP 161 / 162'), (_P, 'A1 N', 'LDAP', 'TCP 389'), (_P, 'A1 N', 'HTTPS', 'TCP 443'),
    (_P, 'A1 N', 'SMB / CIFS', 'TCP 445'), (_P, 'N', 'Syslog', 'UDP 514'), (_P, 'N', 'LDAPS', 'TCP 636'),
    (_P, 'N', 'SQL Server / MySQL', 'TCP 1433 / 3306'), (_P, 'A1 N', 'RDP', 'TCP 3389'),
    (_P, 'N', 'SIP (clear / TLS)', 'UDP/TCP 5060/5061'), (_P, 'N', 'Which protocol uses TCP 22 for file transfer?', 'SFTP'),
    (_P, 'N', 'Which protocol uses UDP 514?', 'Syslog'), (_P, 'A1 N', 'Which protocol uses TCP 3389?', 'RDP'),
    (_P, 'A1 N', 'Which protocol uses TCP 445?', 'SMB'), (_P, 'N', 'Which protocol uses UDP 123?', 'NTP'),
    (_P, 'A1 N', 'Which protocol uses UDP 69?', 'TFTP'),
    # ---------------------------------------------------------------- IEEE / Wi-Fi / cable / hardware
    (_S, 'N', '802.1Q', 'VLAN tagging on trunks'), (_S, 'A2 N', '802.1X', 'Port-based network access control'),
    (_S, 'N', '802.1D / 802.1w', 'Spanning Tree / Rapid STP'), (_S, 'A1 N', '802.3af PoE', 'Up to 15.4 W per port'),
    (_S, 'A1 N', '802.3at PoE+', 'Up to 30 W per port'), (_S, 'A1 N', '802.3bt PoE++', 'Up to 60-100 W per port'),
    (_S, 'A1 N', '802.11a', '5 GHz, up to 54 Mb/s'), (_S, 'A1 N', '802.11b', '2.4 GHz, up to 11 Mb/s'),
    (_S, 'A1 N', '802.11g', '2.4 GHz, up to 54 Mb/s'), (_S, 'A1 N', '802.11n (Wi-Fi 4)', '2.4/5 GHz, MIMO, 600 Mb/s'),
    (_S, 'A1 N', '802.11ac (Wi-Fi 5)', '5 GHz only, MU-MIMO'), (_S, 'A1 N', '802.11ax (Wi-Fi 6/6E)', '2.4/5/6 GHz, OFDMA'),
    (_S, 'A1 N', 'Cat 5e', '1 Gb/s to 100 m'), (_S, 'A1 N', 'Cat 6', '10 Gb/s to 55 m'), (_S, 'A1 N', 'Cat 6A', '10 Gb/s to 100 m'),
    (_S, 'A1 N', 'Cat 8', '25/40 Gb/s to 30 m'), (_S, 'A1 N', 'T568A pins 1-2', 'White/green, green'),
    (_S, 'A1 N', 'T568B pins 1-2', 'White/orange, orange'), (_S, 'A1 N', 'LC connector', 'Small form-factor fiber latch'),
    (_S, 'A1 N', 'SC connector', 'Square push-pull fiber'), (_S, 'A1 N', 'ST connector', 'Round bayonet twist fiber'),
    (_S, 'N', 'MPO connector', 'Multi-fiber ribbon connector'), (_S, 'A1', 'USB 3.2 Gen 2x2', '20 Gb/s over USB-C'),
    (_S, 'A1', 'USB4 / Thunderbolt 4', '40 Gb/s over USB-C'), (_S, 'A1', 'PCIe 4.0 x16', 'About 32 GB/s each way'),
    (_S, 'A1', 'M.2 NVMe', 'SSD over PCIe lanes, M key'),
    # ---------------------------------------------------------------- CLI
    (_C, 'A2 N', 'ipconfig /flushdns', 'Clear the DNS resolver cache'), (_C, 'A2 N', 'netstat -ano', 'Connections with owning PID'),
    (_C, 'A2', 'sfc /scannow', 'Repair protected system files'), (_C, 'A2', 'DISM /Online /Cleanup-Image /RestoreHealth', 'Repair the Windows image store'),
    (_C, 'A2', 'gpupdate /force', 'Reapply all Group Policy now'), (_C, 'A2', 'chmod 640 file', 'Set rw-r----- permissions'),
    (_C, 'A2', 'chown alice:staff file', 'Change file owner and group'), (_C, 'A2 N', 'ss -tulpn', 'Listening sockets with process'),
    (_C, 'A2', 'journalctl -u sshd', 'Read the systemd log of a unit'), (_C, 'N', 'dig example.com MX', 'Query DNS for mail exchangers'),
    (_C, 'N', 'show vlan brief', 'VLANs and their access ports'), (_C, 'N', 'show interfaces trunk', 'Trunk ports and allowed VLANs'),
    (_C, 'N', 'show ip route', 'The router\u2019s routing table'), (_C, 'A2 N', 'tracert / traceroute', 'List each hop to a host'),
    (_C, 'A2 N', 'nslookup', 'Query a DNS server by hand'), (_C, 'A2', 'chkdsk /r', 'Find bad sectors, recover data'),
    (_C, 'A2', 'diskpart', 'Manage disks and partitions'), (_C, 'A2', 'robocopy /MIR', 'Mirror a folder tree'),
    (_C, 'A2', 'sudo', 'Run one command as root'), (_C, 'N', 'show running-config', 'Active config in RAM'),
    (_C, 'N', 'copy run start', 'Save running config to NVRAM'), (_C, 'N', 'show mac address-table', 'Learned MACs per switchport'),
    (_C, 'A2 N', 'arp -a', 'IP-to-MAC cache entries'), (_C, 'A2', 'whoami /groups', 'Your account\u2019s group SIDs'),
    # ---------------------------------------------------------------- acronyms & concepts
    (_A, 'A2 N', 'AAA', 'Authentication, authorization, accounting'), (_A, 'A2 N', 'SAML', 'XML-based federated SSO'),
    (_A, 'A2 N', 'OIDC', 'Identity layer on top of OAuth 2.0'), (_A, 'A2 N', 'RADIUS', 'UDP AAA, encrypts only password'),
    (_A, 'A2 N', 'TACACS+', 'TCP 49 AAA, encrypts full body'), (_A, 'A2 N', 'WPA3-SAE', 'Dragonfly handshake, no offline guessing'),
    (_A, 'A2 N', 'MTBF', 'Mean time between failures'), (_A, 'A2 N', 'MTTR', 'Mean time to repair/restore'),
    (_A, 'A2 N', 'RTO', 'Max time to restore a service'), (_A, 'A2 N', 'RPO', 'Max data loss measured in time'),
    (_A, 'A1 N', 'IaaS', 'You manage OS and up; VMs rented'), (_A, 'A1 N', 'PaaS', 'You manage only apps and data'),
    (_A, 'A1 N', 'SaaS', 'Provider runs the whole app'), (_A, 'A2 N', 'SPF', 'DNS list of allowed mail senders'),
    (_A, 'A2 N', 'DKIM', 'Signs mail with a domain key'), (_A, 'A2 N', 'DMARC', 'Policy when SPF/DKIM checks fail'),
    (_A, 'N', 'VLAN', 'Logical layer-2 broadcast domain'), (_A, 'N', 'VXLAN', 'Layer-2 overlay over UDP 4789'),
    (_A, 'N', 'MPLS', 'Label switching across a WAN'), (_A, 'A2 N', 'MFA', 'Two or more factor types'),
    # ---------------------------------------------------------------- additional ports & protocols
    (_P, 'A1 N', 'FTP data transfer port', 'TCP 20'),
    (_P, 'A1 N', 'FTP control command port', 'TCP 21'),
    (_P, 'A1 A2 N', 'SCP / SFTP / SSH port', 'TCP 22'),
    (_P, 'A1 N', 'SMTPS (implicit TLS mail)', 'TCP 465'),
    (_P, 'A1 N', 'SMTP message submission', 'TCP 587'),
    (_P, 'A1 N', 'DNS zone transfer (AXFR)', 'TCP 53'),
    (_P, 'A1 N', 'DNS standard queries', 'UDP 53'),
    (_P, 'A1 N', 'DHCP server listening port', 'UDP 67'),
    (_P, 'A1 N', 'DHCP client listening port', 'UDP 68'),
    (_P, 'A1 N', 'POP3 cleartext mail port', 'TCP 110'),
    (_P, 'A1 N', 'POP3S TLS mail port', 'TCP 995'),
    (_P, 'A1 N', 'IMAP4 cleartext mail port', 'TCP 143'),
    (_P, 'A1 N', 'IMAPS TLS mail port', 'TCP 993'),
    (_P, 'A1 N', 'SNMP agent polling port', 'UDP 161'),
    (_P, 'A1 N', 'SNMP trap receiver port', 'UDP 162'),
    (_P, 'A1 N', 'NetBIOS Name Service', 'UDP 137'),
    (_P, 'A1 N', 'NetBIOS Datagram Service', 'UDP 138'),
    (_P, 'A1 N', 'NetBIOS Session Service', 'TCP 139'),
    (_P, 'A1 N', 'SLP (Service Location)', 'TCP/UDP 427'),
    (_P, 'A1', 'AFP (Apple Filing Protocol)', 'TCP 548'),
    (_P, 'N', 'BGP peering port', 'TCP 179'),
    (_P, 'N', 'RIPng / RIPv2 UDP port', 'UDP 520'),
    (_P, 'N', 'IKE / ISAKMP key exchange', 'UDP 500'),
    (_P, 'N', 'IPsec NAT-Traversal (NAT-T)', 'UDP 4500'),
    (_P, 'N', 'IPsec ESP IP protocol number', 'IP proto 50'),
    (_P, 'N', 'IPsec AH IP protocol number', 'IP proto 51'),
    (_P, 'N', 'GRE tunnel IP protocol number', 'IP proto 47'),
    (_P, 'N', 'OSPF IP protocol number', 'IP proto 89'),
    (_P, 'N', 'EIGRP IP protocol number', 'IP proto 88'),
    (_P, 'N', 'VRRP IP protocol number', 'IP proto 112'),
    (_P, 'N', 'HSRP UDP hello port', 'UDP 1985'),
    (_P, 'A2 N', 'RADIUS auth / acct (RFC)', 'UDP 1812 / 1813'),
    (_P, 'N', 'RADIUS legacy ports', 'UDP 1645 / 1646'),
    (_P, 'A2 N', 'TACACS+ AAA daemon port', 'TCP 49'),
    (_P, 'N', 'Syslog over TLS (RFC 5425)', 'TCP 6514'),
    (_P, 'N', 'Microsoft SQL Server port', 'TCP 1433'),
    (_P, 'N', 'Oracle SQL*Net listener', 'TCP 1521'),
    (_P, 'N', 'MySQL / MariaDB default port', 'TCP 3306'),
    (_P, 'N', 'PostgreSQL default port', 'TCP 5432'),
    (_P, 'A2 N', 'VNC remote framebuffer port', 'TCP 5900'),
    (_P, 'N', 'SIP cleartext signaling', 'UDP/TCP 5060'),
    (_P, 'N', 'SIPS TLS encrypted signaling', 'TCP 5061'),
    (_P, 'N', 'RTP / SRTP media stream ports', 'UDP 16384-32767'),
    (_P, 'A2 N', 'DNS over TLS (DoT) port', 'TCP 853'),
    (_P, 'A2 N', 'DNS over HTTPS (DoH) port', 'TCP 443'),
    (_P, 'N', 'VXLAN UDP encapsulation port', 'UDP 4789'),
    (_P, 'N', 'CAPWAP WLC control / data', 'UDP 5246 / 5247'),
    (_P, 'N', 'NetFlow / IPFIX collector', 'UDP 2055 / 4739'),
    (_P, 'N', 'PTP event / general messages', 'UDP 319 / 320'),
    (_P, 'A2', 'WinRM HTTP / HTTPS ports', 'TCP 5985 / 5986'),
    (_P, 'A1 N', 'IPP (Internet Printing)', 'TCP 631'),
    (_P, 'A1 N', 'Raw JetDirect network print', 'TCP 9100'),
    (_P, 'N', 'iSCSI target storage port', 'TCP 3260'),
    (_P, 'N', 'NFSv4 network file system', 'TCP 2049'),
    (_P, 'N', 'LDAP Global Catalog / SSL', 'TCP 3268 / 3269'),
    # ---------------------------------------------------------------- additional IEEE / Wi-Fi / cable / hardware
    (_S, 'N', '802.1D standard', 'Classic Spanning Tree (STP)'),
    (_S, 'N', '802.1w standard', 'Rapid Spanning Tree (RSTP)'),
    (_S, 'N', '802.1s standard', 'Multiple Spanning Tree (MSTP)'),
    (_S, 'N', '802.3ad / 802.1AX', 'LACP link aggregation'),
    (_S, 'N', '802.1AB standard', 'LLDP neighbor discovery'),
    (_S, 'N', '802.11h standard', 'DFS & TPC for 5 GHz radar'),
    (_S, 'N', '802.11r standard', 'Fast BSS transition roaming'),
    (_S, 'N', '802.11k / 802.11v', 'Neighbor reports & BSS steer'),
    (_S, 'N', '802.11w standard', 'Protected Management Frames'),
    (_S, 'A1 N', '802.11be (Wi-Fi 7)', '2.4/5/6 GHz, 320 MHz, MLO'),
    (_S, 'A1 N', '2.4 GHz non-overlapping (US)', 'Channels 1, 6, and 11'),
    (_S, 'A1 N', '5 GHz UNII-1 indoor channels', 'Channels 36, 40, 44, 48'),
    (_S, 'A1 N', 'Cat 5 cable specification', '100 Mb/s Fast Ethernet 100 m'),
    (_S, 'A1 N', 'Cat 7 shielded cable spec', '10 Gb/s to 100 m (GG45/TERA)'),
    (_S, 'A1 N', '1000BASE-T Ethernet spec', '1 Gb/s, 4 pairs Cat 5e, 100 m'),
    (_S, 'A1 N', '10GBASE-T Ethernet spec', '10 Gb/s, Cat 6A to 100 m'),
    (_S, 'N', '1000BASE-SX fiber spec', '850 nm MMF, up to 550 m'),
    (_S, 'N', '1000BASE-LX fiber spec', '1310 nm SMF, up to 5-10 km'),
    (_S, 'N', '10GBASE-SR fiber spec', '850 nm MMF, up to 400 m OM4'),
    (_S, 'N', '10GBASE-LR fiber spec', '1310 nm SMF, up to 10 km'),
    (_S, 'N', '10GBASE-ER fiber spec', '1550 nm SMF, up to 40 km'),
    (_S, 'N', '40GBASE-SR4 fiber spec', '850 nm OM4 MPO ribbon, 150 m'),
    (_S, 'N', 'DAC (Direct Attach Copper)', 'Twinax SFP+ passive/active'),
    (_S, 'A1 N', 'OM3 vs OM4 multimode core', '50/125 um aqua/erika violet'),
    (_S, 'A1 N', 'OS1 / OS2 single-mode core', '9/125 um yellow jacket SMF'),
    (_S, 'N', 'UPC vs APC fiber polish', 'Blue 0 deg vs Green 8 deg'),
    (_S, 'A1 N', 'Plenum cable jacket rating', 'CMP low-smoke fire-retardant'),
    (_S, 'A1 N', 'Riser cable jacket rating', 'CMR vertical shaft between floors'),
    (_S, 'A1 N', 'RG-6 coaxial cable use', '75-ohm DOCSIS cable broadband'),
    (_S, 'A1 N', 'F-type vs BNC coax connector', 'Threaded DOCSIS vs bayonet RF'),
    (_S, 'A1', 'USB 2.0 Hi-Speed rate', '480 Mb/s, 5 m max cable'),
    (_S, 'A1', 'USB 3.2 Gen 1 (SuperSpeed)', '5 Gb/s over 9-pin Type-A/C'),
    (_S, 'A1', 'USB 3.2 Gen 2 (SuperSpeed+)', '10 Gb/s over USB-A or USB-C'),
    (_S, 'A1', 'Thunderbolt 3 / 4 daisy chain', '40 Gb/s USB-C, PCIe + DP'),
    (_S, 'A1', 'SATA Revision 3.0 bandwidth', '6 Gb/s (about 600 MB/s max)'),
    (_S, 'A1', 'PCIe 3.0 x1 vs x16 bandwidth', '~1 GB/s per lane (~16 GB/s)'),
    (_S, 'A1', 'PCIe 5.0 x4 M.2 NVMe rate', '~16 GB/s over 4 PCIe 5 lanes'),
    (_S, 'A1', 'DDR4 vs DDR5 DIMM pins', '288-pin DIMM (different key)'),
    (_S, 'A1', 'DDR4 vs DDR5 SO-DIMM pins', '260-pin DDR4 vs 262-pin DDR5'),
    (_S, 'A1', 'ATX vs Mini-ITX board size', '305x244 mm vs 170x170 mm'),
    (_S, 'A1', '24-pin ATX + 8-pin EPS12V', 'Mainboard power + CPU 12 V'),
    (_S, 'A1', 'RAID 0 (striping only)', '2+ drives, 0 fault tolerance'),
    (_S, 'A1', 'RAID 1 (mirroring)', '2+ drives, 50% capacity usable'),
    (_S, 'A1', 'RAID 5 (distributed parity)', '3+ drives, 1-drive fault tol.'),
    (_S, 'A1', 'RAID 6 (dual parity)', '4+ drives, 2-drive fault tol.'),
    (_S, 'A1', 'RAID 10 (stripe of mirrors)', '4+ even drives, fast + 1/pair'),
    (_S, 'A1', 'LCD IPS vs TN panel traits', 'Wide viewing/color vs fast ms'),
    (_S, 'A1', 'OLED vs VA display traits', 'Self-lit per-pixel vs high contrast'),
    (_S, 'A1', 'Laser printing 7-step order', 'Proc,Charge,Expose,Dev,Tx,Fuse,Clean'),
    # ---------------------------------------------------------------- additional CLI commands
    (_C, 'A2 N', 'ipconfig /all', 'Full IP, MAC, DHCP, DNS info'),
    (_C, 'A2 N', 'ipconfig /release & /renew', 'Drop and request DHCP lease'),
    (_C, 'A2 N', 'ping -t <host>', 'Continuous ICMP echo in Win'),
    (_C, 'A2 N', 'pathping <host>', 'Per-hop packet loss & latency'),
    (_C, 'A2 N', 'route print', 'Display Windows routing table'),
    (_C, 'A2 N', 'net use Z: \\\\srv\\share', 'Map a Windows network drive'),
    (_C, 'A2', 'net user / net localgroup', 'Manage local users and groups'),
    (_C, 'A2', 'netstat -b', 'Show executable per socket'),
    (_C, 'A2', 'gpresult /r', 'RSOP summary of applied GPOs'),
    (_C, 'A2', 'gpresult /h report.html', 'HTML report of Group Policy'),
    (_C, 'A2', 'chkdsk C: /f', 'Fix filesystem errors on disk'),
    (_C, 'A2', 'format FS=NTFS QUICK', 'Quick-format volume as NTFS'),
    (_C, 'A2', 'bcdedit /enum', 'List Windows UEFI/BCD entries'),
    (_C, 'A2', 'bcdboot C:\\Windows /s S:', 'Rebuild EFI boot files on S:'),
    (_C, 'A2', 'manage-bde -status C:', 'Check BitLocker encryption'),
    (_C, 'A2', 'powercfg /batteryreport', 'Generate HTML battery health'),
    (_C, 'A2', 'tasklist / taskkill /PID', 'List or terminate Win process'),
    (_C, 'A2', 'shutdown /r /t 0', 'Reboot Windows immediately'),
    (_C, 'A2', 'winget install <pkg>', 'Install app via Win pkg mgr'),
    (_C, 'A2', 'Get-Service / Start-Service', 'Query or start Win services'),
    (_C, 'A2', 'Get-EventLog / Get-WinEvent', 'Query Windows Event Viewer'),
    (_C, 'A2 N', 'Test-NetConnection -Port', 'PowerShell TCP + ICMP test'),
    (_C, 'A2 N', 'Resolve-DnsName <name>', 'PowerShell DNS query cmdlet'),
    (_C, 'A2 N', 'ip addr show (ip a)', 'Linux interfaces & IPv4/IPv6'),
    (_C, 'A2 N', 'ip route show (ip r)', 'Linux kernel routing table'),
    (_C, 'A2 N', 'ip link set eth0 up', 'Bring Linux NIC link online'),
    (_C, 'A2 N', 'dig +short @8.8.8.8 host A', 'Direct DNS A-record lookup'),
    (_C, 'A2 N', 'dig -x 192.0.2.10', 'Reverse PTR lookup in DNS'),
    (_C, 'N', 'tcpdump -ni eth0 port 53', 'Capture DNS packets on eth0'),
    (_C, 'N', 'nmap -sS -p 1-1024 <ip>', 'TCP SYN stealth port scan'),
    (_C, 'N', 'iperf3 -c <srv> -t 10', 'Measure throughput & jitter'),
    (_C, 'A2', 'df -h', 'Filesystem free space in GB/MB'),
    (_C, 'A2', 'du -sh /var/log/*', 'Directory disk usage summary'),
    (_C, 'A2', 'free -h', 'Linux RAM and swap usage'),
    (_C, 'A2', 'ps aux | grep <proc>', 'Search running Linux processes'),
    (_C, 'A2', 'top / htop', 'Live CPU & memory process view'),
    (_C, 'A2', 'kill -9 <PID>', 'Send SIGKILL to a hung process'),
    (_C, 'A2', 'chmod 755 script.sh', 'Set rwxr-xr-x executable mode'),
    (_C, 'A2', 'chmod 600 ~/.ssh/id_ed25519', 'Restrict SSH key to owner rw'),
    (_C, 'A2', 'apt update && apt upgrade', 'Refresh & patch Debian/Ubuntu'),
    (_C, 'A2', 'dnf upgrade', 'Patch RHEL / Fedora packages'),
    (_C, 'A2', 'systemctl enable --now sshd', 'Start & enable systemd service'),
    (_C, 'A2', 'crontab -e', 'Edit scheduled user cron jobs'),
    (_C, 'A2', 'grep -rn "ERROR" /var/log/', 'Recursive line search in logs'),
    (_C, 'A2', 'find /etc -name "*.conf"', 'Locate config files by pattern'),
    (_C, 'A2', 'tar -czf backup.tar.gz /etc', 'Create gzipped tar archive'),
    (_C, 'A2', 'fsck -y /dev/sda2', 'Check and repair Linux ext4'),
    (_C, 'A2', 'lsblk / blkid', 'List block devices and UUIDs'),
    (_C, 'N', 'show ip interface brief', 'IOS ports, IPs, up/up status'),
    (_C, 'N', 'show ip ospf neighbor', 'OSPF adjacency state & peer'),
    (_C, 'N', 'show ip bgp summary', 'BGP neighbor ASN & prefixes'),
    (_C, 'N', 'show etherchannel summary', 'Port-channel LACP/PAgP state'),
    (_C, 'N', 'show spanning-tree', 'Root bridge & STP port states'),
    (_C, 'N', 'show ip arp', 'Router IPv4-to-MAC ARP table'),
    (_C, 'N', 'show cdp neighbors detail', 'Cisco neighbor IP & platform'),
    (_C, 'N', 'show lldp neighbors', 'IEEE vendor-neutral neighbors'),
    (_C, 'N', 'show access-lists', 'ACL rules and match counters'),
    (_C, 'N', 'show ip nat translations', 'Active inside/outside NAT/PAT'),
    (_C, 'N', 'show power inline', 'Per-port PoE draw and budget'),
    (_C, 'N', 'show interfaces status', 'Switchport VLAN, speed, err'),
    (_C, 'N', 'show interfaces transceiver', 'Fiber SFP DOM Tx/Rx dBm power'),
    (_C, 'N', 'switchport mode trunk', 'Configure 802.1Q trunk port'),
    (_C, 'N', 'ip helper-address <ip>', 'Relay DHCP broadcasts to srv'),
    # ---------------------------------------------------------------- additional acronyms & concepts
    (_A, 'A1 N', 'APIPA', '169.254.0.0/16 self-assigned'),
    (_A, 'A1 N', 'RFC 1918 private IPv4', '10/8, 172.16/12, 192.168/16'),
    (_A, 'N', 'IPv6 link-local prefix', 'fe80::/10 non-routable scope'),
    (_A, 'N', 'IPv6 Unique Local (ULA)', 'fc00::/7 (fd00::/8) private'),
    (_A, 'N', 'IPv6 Global Unicast (GUA)', '2000::/3 public internet'),
    (_A, 'N', 'SLAAC', 'Router Advertisement EUI/rand'),
    (_A, 'N', 'DHCP DORA sequence', 'Discover, Offer, Request, Ack'),
    (_A, 'N', 'OSI 7 layers (1 to 7)', 'Phys,Data,Net,Trans,Sess,Pres,App'),
    (_A, 'N', 'PDU names (L1 to L4)', 'Bit, Frame, Packet, Segment'),
    (_A, 'N', 'OSPF administrative distance', 'AD 110 (link-state Dijkstra)'),
    (_A, 'N', 'eBGP vs iBGP admin distance', 'AD 20 external, AD 200 internal'),
    (_A, 'N', 'EIGRP internal admin distance', 'AD 90 (dual distance-vector)'),
    (_A, 'N', 'Static route admin distance', 'AD 1 (or 0 connected interface)'),
    (_A, 'N', 'RIPv2 administrative distance', 'AD 120 (max 15 hops, metric 16)'),
    (_A, 'N', 'HSRP / VRRP / GLBP', 'First-hop default gateway VIP'),
    (_A, 'N', 'PAT (NAT Overload)', 'Many private IPs share 1 public'),
    (_A, 'N', 'DNAT / Port Forwarding', 'Map public port to inside host'),
    (_A, 'N', 'STP PortFast + BPDU Guard', 'Instant access up; err-disable'),
    (_A, 'N', 'DHCP Snooping + DAI', 'Drop rogue DHCP & forged ARP'),
    (_A, 'N', 'VLAN Hopping mitigation', 'Unused native VLAN, no DTP'),
    (_A, 'N', 'SD-WAN', 'App-aware overlay across WANs'),
    (_A, 'N', 'SASE (Secure Access Service)', 'SD-WAN + SSE Zero Trust edge'),
    (_A, 'N', 'Zero Trust (ZTA)', 'Verify explicitly, never trust'),
    (_A, 'N', 'IaC (Infrastructure as Code)', 'Versioned declarative net cfg'),
    (_A, 'N', 'NetFlow / IPFIX vs PCAP', '5-tuple metadata vs full frame'),
    (_A, 'N', 'SNMPv3 authPriv security', 'SHA/SHA-2 auth + AES encryption'),
    (_A, 'N', 'SPAN / Port Mirroring', 'Copy switch traffic to sensor'),
    (_A, 'N', 'Hot site vs Cold site DR', 'Live synced standby vs shell'),
    (_A, 'N', 'Warm site DR', 'Hardware ready, restore backup'),
    (_A, 'A1 A2', 'UEFI Secure Boot', 'Verify signed OS bootloaders'),
    (_A, 'A1 A2', 'TPM 2.0', 'Crypto module for BitLocker'),
    (_A, 'A2', 'BitLocker vs EFS', 'Full volume vs NTFS file/folder'),
    (_A, 'A2', 'FileVault 2', 'macOS XTS-AES full-disk crypto'),
    (_A, 'A2', 'LUKS / dm-crypt', 'Linux full-disk encryption'),
    (_A, 'A2', 'UAC (User Account Control)', 'Prompt before admin elevation'),
    (_A, 'A1 A2', 'MDM (Mobile Device Mgmt)', 'Enforce policies, wipe, certs'),
    (_A, 'A1 A2', 'MAM (Mobile App Management)', 'Containerize corporate apps'),
    (_A, 'A2', 'Sideloading / Jailbreaking', 'Bypass store & OS sandboxing'),
    (_A, 'A2 N', 'Phishing vs Spear Phishing', 'Bulk lure vs targeted victim'),
    (_A, 'A2 N', 'Whaling / BEC', 'Executive target / wire fraud'),
    (_A, 'A2 N', 'Vishing vs Smishing', 'Voice call scam vs SMS lure'),
    (_A, 'A2 N', 'Tailgating vs Piggybacking', 'Follow unawares vs with consent'),
    (_A, 'A2 N', 'Evil Twin AP attack', 'Rogue SSID mimicking corp Wi-Fi'),
    (_A, 'A2', 'Fileless Malware', 'Lives in RAM via PowerShell/WMI'),
    (_A, 'A2', 'Rootkit', 'Hides deep in kernel/bootloader'),
    (_A, 'A2', '3-2-1 Backup Rule', '3 copies, 2 media, 1 offsite'),
    (_A, 'A2', 'Incremental vs Differential', 'Since last any vs since last Full'),
    (_A, 'A2', 'Order of Volatility (RFC)', 'CPU/RAM -> Net -> Disk -> Backup'),
    (_A, 'A2', 'Chain of Custody', 'Signed log of evidence handling'),
    (_A, 'A2', 'GPT vs MBR partitioning', '128 parts >2 TB UEFI vs 4/2 TB'),
    (_A, 'A1 A2', '6-Step Troubleshooting Order', 'Identify,Theory,Test,Plan,Verify,Doc'),
    (_A, 'A2', '7-Step Malware Removal Order', 'ID,Quarantine,OffSR,Clean,Scan,OnSR,Edu'),
    (_A, 'A1 A2', 'ESD Prevention', 'Wrist strap + grounded mat'),
    (_A, 'A1 A2', 'SDS (Safety Data Sheet)', 'Hazmat handling & disposal doc'),
    (_A, 'A1 A2', 'UPS vs Surge Suppressor', 'Battery runtime vs joule clamp'),
    (_A, 'A2', 'PII vs PHI data privacy', 'Personal ID vs HIPAA health'),
    (_A, 'A2', 'DRM / EULA', 'Copy control / software license'),
    (_A, 'A1', 'VDI (Virtual Desktop Infra)', 'Centralized hosted desktop VMs'),
    (_A, 'A1', 'S.M.A.R.T. drive telemetry', 'Self-Monitoring drive health'),
    (_A, 'N', 'EUI-64 interface ID', '64-bit IPv6 host ID from MAC'),
]


def _cards():
    out = []
    for n, (cat, exams, front, back) in enumerate(_RAW, 1):
        exs = exams.split()
        if ('A1' in exs or 'A2' in exs) and 'T' not in exs:
            exs = ['T'] + exs
        out.append({'id': f'SD-{n:03d}', 'cat': cat, 'exams': exs, 'front': front, 'back': back,
                    'codes': [EXAM_CODES[e] for e in exs], 'review': REVIEW})
    return out


CARDS = _cards()
BY_ID = {c['id']: c for c in CARDS}


def choices(card):
    """Key + 3 same-category distractors with the closest lengths; the key is never >= BALANCE x the longest one."""
    k = card['back']
    pool = sorted({c['back'] for c in CARDS if c['cat'] == card['cat'] and c['back'] != k},
                  key=lambda b: (abs(len(b) - len(k)), b))
    picks = pool[:3]
    if len(k) >= BALANCE * max(map(len, picks)):
        longer = [b for b in pool if len(b) * BALANCE > len(k)]
        picks = picks[:2] + longer[:1]
    opts = picks + [k]
    random.Random(card['id']).shuffle(opts)
    return opts


def balance_violations():
    out = []
    for c in CARDS:
        opts = choices(c)
        wrong = [o for o in opts if o != c['back']]
        if len(c['back']) >= BALANCE * max(map(len, wrong)):
            out.append(c['id'])
    return out


def deck(exam=None, cat=None):
    return [c for c in CARDS if (not exam or exam in c['exams']) and (not cat or c['cat'] == cat)]


def register(app, db, deps):
    """deps: ClassSection, Enrollment, utcnow."""
    ClassSection, Enrollment, utcnow = deps['ClassSection'], deps['Enrollment'], deps['utcnow']

    class SpeedDrillStat(db.Model):
        __tablename__ = 'speed_drill_stat'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        card_id = db.Column(db.String(12), nullable=False)
        box = db.Column(db.Integer, default=1)          # Leitner box 1 (review soon) .. 5 (known)
        seen = db.Column(db.Integer, default=0)
        right = db.Column(db.Integer, default=0)
        best_streak = db.Column(db.Integer, default=0)
        updated_at = db.Column(db.DateTime)
        __table_args__ = (db.UniqueConstraint('user_id', 'card_id', name='uq_speed_drill_user_card'),)

    with app.app_context():
        SpeedDrillStat.__table__.create(db.engine, checkfirst=True)

    def section(section_id):
        sec = db.get_or_404(ClassSection, section_id)
        if current_user.role in ('admin', 'instructor'):
            return sec
        if not Enrollment.query.filter_by(user_id=current_user.id, section_id=sec.id).first():
            abort(403)
        return sec

    @login_required
    def speed_drill(section_id):
        sec = section(section_id)
        exam = request.args.get('exam') if request.args.get('exam') in EXAM_CODES else ''
        cat = request.args.get('cat') if request.args.get('cat') in CATEGORIES else ''
        stats = {s.card_id: s for s in SpeedDrillStat.query.filter_by(user_id=current_user.id).all()}
        cards = deck(exam, cat)
        # spaced repetition: lowest box first, then fewest seen; shuffled within ties
        rng = random.Random()
        cards = sorted(cards, key=lambda c: ((stats[c['id']].box if c['id'] in stats else 0),
                                             (stats[c['id']].seen if c['id'] in stats else 0), rng.random()))
        payload = [{'id': c['id'], 'cat': CATEGORIES[c['cat']], 'front': c['front'], 'back': c['back'],
                    'codes': c['codes'], 'choices': choices(c),
                    'box': stats[c['id']].box if c['id'] in stats else 0} for c in cards]
        known = sum(1 for s in stats.values() if s.box >= 4)
        return render_template('exam_sim/speed_drill.html', section=sec, cards=payload, exam=exam, cat=cat,
                               categories=CATEGORIES, exams=EXAM_CODES, seconds=BLITZ_SECONDS, review=REVIEW,
                               known=known, seen=len(stats), total=len(CARDS),
                               best=max((s.best_streak or 0 for s in stats.values()), default=0))

    @login_required
    def speed_drill_record(section_id):
        section(section_id)
        data = request.get_json(silent=True) or request.form
        card = BY_ID.get(data.get('card'))
        result = data.get('result')
        if not card or result not in ('right', 'wrong', 'got', 'again'):
            abort(400)
        s = SpeedDrillStat.query.filter_by(user_id=current_user.id, card_id=card['id']).first()
        if not s:
            s = SpeedDrillStat(user_id=current_user.id, card_id=card['id'], box=1, seen=0, right=0, best_streak=0)
            db.session.add(s)
        ok = result in ('right', 'got')
        s.seen = (s.seen or 0) + 1
        s.right = (s.right or 0) + int(ok)
        s.box = min(5, (s.box or 1) + 1) if ok else 1
        try:
            streak = int(data.get('streak') or 0)
        except (TypeError, ValueError):
            streak = 0
        s.best_streak = max(s.best_streak or 0, min(streak, 999))
        s.updated_at = utcnow()
        db.session.commit()
        return {'ok': True, 'card': card['id'], 'box': s.box, 'seen': s.seen, 'right': s.right}

    app.add_url_rule('/student/section/<int:section_id>/speed-drill', 'speed_drill', speed_drill, methods=['GET'])
    app.add_url_rule('/student/section/<int:section_id>/speed-drill/record', 'speed_drill_record', speed_drill_record,
                     methods=['POST'])
    return SpeedDrillStat
