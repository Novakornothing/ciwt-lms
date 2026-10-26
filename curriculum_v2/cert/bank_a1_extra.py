"""Expanded CompTIA A+ Core 1 (220-1201) scenario item bank for the Exam-Day Readiness Simulator.

195 concrete, scenario-driven items across all 27 Core 1 objectives (Domains 1.0–5.0). Pending SME review.
"""
REVIEW = 'Pending SME review'


def _s(idx, bid, obj, oid, text, correct, wrong, explanation):
    w = sorted(list(wrong), key=lambda s: (len(s), s))
    pos = idx % 4
    opts = w[:pos] + [correct] + w[pos:]
    d = {'id': bid, 'bank_id': bid, 'source': 'extra', 'obj': obj, 'cert': [oid], 'type': 'single',
         'text': text, 'options': opts, 'correct': correct, 'explanation': explanation, 'review': REVIEW}
    d['raw'] = d
    return d


RAW_A1 = [('A1X-101',
  'IT-4.1',
  'A1:1.1',
  'A technician replaces the LCD panel on a corporate Ultrabook, and after reassembly the Windows 11 desktop works '
  'normally but Wi-Fi signal strength drops from -48 dBm to -86 dBm at 2 meters from the AP. Which internal step was '
  'missed?',
  'Snapping coax antenna leads to the Wi-Fi card',
  ['Applying fresh thermal paste to the CPU heat pipe',
   'Enabling the SO-DIMM dual-channel mode in UEFI',
   'Calibrating the capacitive touch digitizer ribbon'],
  'Laptop Wi-Fi antennas route through the display hinge and attach to the M.2 2230 wireless card via miniature '
  'coaxial connectors (MHF4/U.FL); leaving them unclipped drops RSSI by 30+ dB.'),
 ('A1X-102',
  'IT-4.1',
  'A1:1.1',
  'A compact thin-and-light laptop requires a memory upgrade from 8 GB to 32 GB for local data analysis, but the '
  'service manual lists LPDDR5X memory. What should the technician inform the user?',
  'LPDDR5X is soldered and not field-upgradable',
  ['A single 32 GB DDR5 SO-DIMM can be installed in Slot B',
   'Two 16 GB 288-pin desktop DIMMs are required for dual channel',
   'Upgrading the M.2 2280 NVMe SSD automatically adds LPDDR5X'],
  'LPDDR5/LPDDR5X packages are BGA-soldered directly to the motherboard for low profile and signal integrity, so RAM '
  'capacity is fixed at manufacture.'),
 ('A1X-103',
  'IT-4.1',
  'A1:1.1',
  'After replacing a cracked smartphone OLED assembly, the screen does not turn off when the user holds the phone to '
  'their ear during voice calls, causing accidental mute presses. Which component was misaligned during reassembly?',
  'The IR proximity sensor window near the earpiece',
  ['The NFC coil adhesive pad on the rear battery cover',
   'The Hall-effect lid-close magnet in the lower bezel',
   'The piezoelectric fingerprint reader under the home button'],
  'The IR proximity sensor near the top bezel detects when the user’s face is close during a call and blanks the touch '
  'digitizer.'),
 ('A1X-104',
  'IT-4.1',
  'A1:1.1',
  'A field laptop fails to wake from sleep when the lid is opened and does not enter sleep when the lid is closed, '
  'even though Windows power settings specify Sleep on lid close. Which component is most likely faulty?',
  'The Hall-effect magnetic lid switch or palm-rest magnet',
  ['The CMOS CR2032 coin-cell battery on the mainboard',
   'The PCIe 4.0 x4 M.2 NVMe solid-state boot drive',
   'The liquid-crystal backlight inverter board'],
  'Modern laptops detect lid position using a small permanent magnet in the display bezel paired with a Hall-effect '
  'sensor on the system board.'),
 ('A1X-105',
  'IT-4.1',
  'A1:1.1',
  'A user wants to upgrade the internal storage of a handheld gaming PC that uses a single-sided M.2 2230 NVMe slot. '
  'Which replacement drive physically fits and functions in that bay?',
  'A 22 mm wide by 30 mm long PCIe NVMe M-key SSD',
  ['A 22 mm wide by 80 mm long SATA III B+M-key SSD',
   'A 2.5-inch 7 mm SATA III solid-state drive',
   'An mSATA full-size 51 mm mini-PCIe card'],
  'M.2 form-factor numbers denote width and length in millimeters: 2230 is 22 mm wide and 30 mm long.'),
 ('A1X-106',
  'IT-4.1',
  'A1:1.1',
  'During a laptop keyboard replacement, the technician disconnects a narrow flat-flex ZIF ribbon cable under the '
  'spacebar area. How should a ZIF (Zero Insertion Force) connector be released safely?',
  'Flip up the hinged actuator latch and slide out',
  ['Pull the ribbon straight out with needle-nose pliers under tension',
   'Unscrew the two Torx T8 standoffs holding the socket to the PCB',
   'Heat the connector with a rework station to soften the adhesive'],
  'ZIF connectors clamp flat-flex cables with a tiny hinged bail or slider; lifting the latch releases clamping '
  'pressure so the ribbon slides out undamaged.'),
 ('A1X-107',
  'IT-4.1',
  'A1:1.1',
  'A retail POS tablet fails to read contactless tap-to-pay cards after a battery swap, although Wi-Fi and Bluetooth '
  'headsets work normally. What should the technician inspect first?',
  'The flat NFC loop antenna pad on the back cover',
  ['The 5 GHz MIMO auxiliary antenna lead inside the LCD lid',
   'The microSDXC card reader spring mechanism on the side edge',
   'The ambient light sensor window beside the front camera'],
  'Contactless payments use NFC (13.56 MHz) via a flat inductive loop antenna adhered to the battery pack or rear '
  'housing.'),
 ('A1X-108',
  'IT-4.1',
  'A1:1.2',
  'An architect needs a tablet stylus that supports 4,096 levels of pressure sensitivity, tilt shading, and palm '
  'rejection for CAD markups. Which accessory technology meets these requirements?',
  'An active digitizer stylus using Wacom EMR or AES/MPP',
  ['A passive capacitive rubber-dome stylus pen',
   'A resistive plastic stylus designed for warehouse PDAs',
   'An optical infrared trackball USB-A receiver'],
  'Active styluses communicate pressure, tilt, and hover coordinates to a dedicated digitizer grid, enabling hardware '
  'palm rejection.'),
 ('A1X-109',
  'IT-4.1',
  'A1:1.2',
  'A salesperson wants to connect a corporate laptop to dual 4K@60Hz DisplayPort monitors, Gigabit Ethernet, and 100 W '
  'USB Power Delivery charging over a single USB-C cable, plus PCIe tunneling for an external NVMe scratch array. '
  'Which station should be ordered?',
  'A Thunderbolt 4 docking station with USB-PD 100 W',
  ['A USB 3.0 Type-A port replicator with DisplayLink software',
   'A passive USB-C to HDMI 1.4 travel dongle without power pass-through',
   'A Bluetooth 5.2 wireless audio and HID multi-device hub'],
  'Thunderbolt 4 over USB-C provides 40 Gb/s bandwidth with native PCIe tunneling, dual 4K@60Hz DisplayPort streams, '
  'and up to 100 W USB-PD charging.'),
 ('A1X-110',
  'IT-4.2',
  'A1:1.2',
  'A field engineer in an area with no Wi-Fi connects a laptop to a company smartphone over a USB-C cable to share the '
  'phone’s 5G cellular data connection while charging the phone. What is this configuration called?',
  'USB tethering',
  ['NFC tap pairing', 'Ad-hoc Wi-Fi Direct bridging', 'Infrared IrDA beaming'],
  'Sharing a mobile device’s cellular internet connection with a PC over a physical USB cable is USB tethering.'),
 ('A1X-111',
  'IT-4.1',
  'A1:1.2',
  'An older iPhone 14 uses an 8-pin reversible proprietary Apple connector for charging and wired CarPlay, whereas an '
  'iPhone 15 Pro uses a 24-pin reversible industry-standard connector. Which two connectors are these?',
  'Lightning on the iPhone 14 and USB-C on the iPhone 15 Pro',
  ['Micro-USB on the iPhone 14 and Mini-USB on the iPhone 15 Pro',
   'Mini-DisplayPort on the iPhone 14 and Thunderbolt 2 on the 15 Pro',
   '30-pin dock connector on the iPhone 14 and USB-A on the 15 Pro'],
  'Apple used the 8-pin reversible Lightning connector through the iPhone 14 series before transitioning to the 24-pin '
  'reversible USB-C connector.'),
 ('A1X-112',
  'IT-4.2',
  'A1:1.2',
  'A warehouse worker pairs a Bluetooth barcode scanner with a rugged Android tablet. During the pairing handshake, '
  'both screens display the same 6-digit numeric code and ask the user to confirm they match. Which Bluetooth Secure '
  'Simple Pairing method is in use?',
  'Numeric Comparison',
  ['Just Works (no user prompt)', 'Out of Band (OOB) via Ethernet cable', 'Static 0000 PIN legacy pairing'],
  'Numeric Comparison displays a 6-digit code on both devices for the user to verify, protecting against '
  'man-in-the-middle attacks during Bluetooth pairing.'),
 ('A1X-113',
  'IT-4.1',
  'A1:1.2',
  'Which device provides additional USB-A and audio jacks via a standard USB cable without onboard video controller '
  'chips or PCIe expansion lanes?',
  'A basic USB port replicator or hub',
  ['A Thunderbolt 4 PCIe docking station', 'A proprietary mechanical chassis dock', 'An ExpressCard/34 expansion cage'],
  'A port replicator (or USB hub) simply extends existing USB/audio interfaces without adding independent PCIe '
  'controllers or full docking video paths.'),
 ('A1X-114',
  'IT-4.1',
  'A1:1.2',
  'A technician taps a smartphone against a conference-room speakerphone’s logo, and the phone immediately completes '
  'Bluetooth pairing without searching through a device list. Which short-range (<4 cm) technology bootstrapped the '
  'pairing?',
  'NFC (Near-Field Communication)',
  ['802.11ax 6 GHz Wi-Fi', 'GPS satellite trilateration', 'UHF passive RFID at 900 MHz'],
  'NFC operates at 13.56 MHz within ~4 cm and is commonly used for Out-of-Band (OOB) tap-to-pair Bluetooth '
  'bootstrapping.'),
 ('A1X-115',
  'IT-4.2',
  'A1:1.3',
  'A multinational company issues smartphones that must switch between a domestic carrier and two European carriers '
  'remotely via MDM without shipping physical plastic cards. Which cellular technology enables this?',
  'eSIM profile download via MDM provisioning',
  ['Swapping a full-size 1FF SIM card into a PCMCIA slot',
   'Flashing the baseband CDMA PRL over an RS-232 serial cable',
   'Enabling Airplane Mode and static IPv4 ARP entries'],
  'An eSIM (embedded UICC) soldered to the phone logic board allows carrier profiles to be downloaded and switched '
  'over the air via MDM or QR code.'),
 ('A1X-116',
  'IT-4.2',
  'A1:1.3',
  'Under a company’s BYOD policy, employees use personal phones for work email, and the security team must be able to '
  'erase corporate mail, contacts, and OneDrive files when an employee leaves without touching personal photos or text '
  'messages. What should be configured in MDM/MAM?',
  'Containerized work profile with selective wipe',
  ['Full factory reset remote wipe of the entire NAND flash',
   'Physical confiscation and shredding of the employee phone',
   'Disabling screen lock passcodes on personal devices'],
  'MAM / Android Work Profile / iOS User Enrollment isolates corporate apps and data in an encrypted container so an '
  'administrator can issue a selective wipe of work data only.'),
 ('A1X-117',
  'IT-4.2',
  'A1:1.3',
  'A logistics driver’s rugged tablet fails to record delivery coordinates in the fleet app even though 5G cellular '
  'data works. In Android Settings, "Use location" is on, but accuracy in urban canyons is off by 400 meters. Which '
  'setting improves precision to within a few meters?',
  'Enable High Accuracy mode (GPS + Wi-Fi + cell)',
  ['Disable GPS and rely solely on carrier cell-tower triangulation',
   'Turn on Airplane Mode while the fleet app is recording',
   'Set the DNS server to 127.0.0.1 in the APN settings'],
  'Assisted GPS / High Accuracy combines GNSS satellites with nearby Wi-Fi BSSIDs, Bluetooth beacons, and cell towers '
  'to achieve meter-level positioning in dense cities.'),
 ('A1X-118',
  'IT-4.2',
  'A1:1.3',
  'An executive’s corporate laptop tethered to a mobile hotspot consumes 12 GB of cellular data in two hours because '
  'Windows downloaded a feature update and synced large OneDrive archives in the background. Which Windows Wi-Fi '
  'setting prevents background bulk transfers on a hotspot?',
  'Set the hotspot Wi-Fi profile as Metered',
  ['Change the Wi-Fi adapter MAC address to all zeros',
   'Disable WPA3 encryption on the mobile hotspot',
   'Configure a static 169.254.1.1 IPv4 address'],
  'Marking a network connection as Metered pauses non-critical Windows Updates, app store downloads, and background '
  'cloud sync over capped cellular links.'),
 ('A1X-119',
  'IT-4.2',
  'A1:1.3',
  'A hospital deploys 300 company-owned iPads that must automatically enroll in Intune MDM out of the shrink-wrap, '
  'prevent users from removing the management profile, and lock into a single patient check-in app. Which deployment '
  'model is required?',
  'Apple Business Manager supervised Single App Mode',
  ['Personal Apple ID sign-in with manual .dmg sideloading',
   'Unmanaged guest Wi-Fi with browser pop-up blockers disabled',
   'Jailbreaking each iPad to install an SSH daemon'],
  'Automated Device Enrollment (ADE, formerly DEP) via Apple Business Manager places corporate iPads into Supervised '
  'mode with non-removable MDM profiles and kiosk/Single App Mode.'),
 ('A1X-120',
  'IT-4.2',
  'A1:1.3',
  'A user configures corporate Exchange contacts and calendar on a smartphone using Microsoft Entra / Exchange '
  'ActiveSync over HTTPS. Which TCP port must be reachable from the mobile network for Exchange ActiveSync / modern '
  'OAuth mail sync?',
  'TCP 443',
  ['TCP 25', 'TCP 110', 'UDP 69'],
  'Exchange ActiveSync (EAS) and modern OAuth2/REST mail, calendar, and contact synchronization encapsulate all '
  'traffic over HTTPS on TCP port 443.'),
 ('A1X-121',
  'IT-4.2',
  'A1:1.3',
  'Which MDM capability prevents a user from copying text from a corporate email app and pasting it into a personal '
  'consumer social-media app on the same smartphone?',
  'MDM clipboard DLP restriction between apps',
  ['Port forwarding on the SOHO home router',
   '802.1Q VLAN tagging on the cellular baseband',
   'Enabling Developer Options and USB debugging'],
  'MDM/MAM Data Loss Prevention (DLP) policies restrict clipboard sharing, "Open In", and screenshots between managed '
  'corporate apps and unmanaged personal apps.'),
 ('A1X-122',
  'IT-5.2',
  'A1:2.1',
  'A network technician is configuring an IP phone that must download its firmware and XML configuration file from a '
  'provisioning server with minimal header overhead and no session setup. Which protocol and transport port does the '
  'phone use?',
  'TFTP over UDP port 69',
  ['FTP over TCP port 21', 'HTTPS over TCP port 443', 'SMB over TCP port 445'],
  'VoIP phones and PXE boot clients commonly pull small boot/config files via Trivial File Transfer Protocol (TFTP), '
  'which runs connectionlessly over UDP port 69.'),
 ('A1X-123',
  'IT-5.2',
  'A1:2.1',
  'A legacy industrial controller only supports unencrypted command-line logins over TCP port 23, exposing credentials '
  'in cleartext on the wire. Which protocol and port should replace it for encrypted remote CLI management?',
  'SSH over TCP port 22',
  ['RDP over TCP port 3389', 'SNMP over UDP port 161', 'Telnet over TCP port 2323'],
  'SSH (Secure Shell) on TCP port 22 provides strong encryption and authentication for remote CLI administration, '
  'replacing cleartext Telnet (TCP 23).'),
 ('A1X-124',
  'IT-5.2',
  'A1:2.1',
  'When a user opens a mailbox on a laptop AND a smartphone and wants folder changes and read/unread flags to stay '
  'synchronized on the mail server across both devices, which encrypted protocol and port should the mail client use?',
  'IMAPS over TCP port 993',
  ['POP3 over TCP port 110', 'POP3S over TCP port 995', 'SMTP over TCP port 25'],
  'IMAP keeps messages and folder state synchronized on the server across multiple clients, and IMAPS encrypts the '
  'session over TLS on TCP port 993.'),
 ('A1X-125',
  'IT-5.2',
  'A1:2.1',
  'A Windows workstation maps a drive letter (`\\filesrv01\\projects`) directly over TCP/IP without legacy NetBIOS. '
  'Which port must the firewall allow between the client and the file server?',
  'TCP 445 (SMB/CIFS direct host)',
  ['UDP 137 (NetBIOS Name Service)', 'TCP 21 (FTP control channel)', 'TCP 389 (LDAP directory query)'],
  'Modern Server Message Block (SMB/CIFS) file sharing runs directly over TCP port 445.'),
 ('A1X-126',
  'IT-5.2',
  'A1:2.1',
  'A printer appliance needs to query an Active Directory domain controller to look up employee email addresses for '
  'its "Scan to Email" address book. Which default cleartext and TLS ports does LDAP use?',
  'TCP 389 for LDAP and TCP 636 for LDAPS',
  ['TCP 80 (HTTP) and TCP 443 (HTTPS)', 'UDP 67 (DHCP) and UDP 68 (DHCP)', 'UDP 161 (SNMP) and UDP 162 (SNMPtrap)'],
  'Lightweight Directory Access Protocol (LDAP) queries directory services on TCP/UDP 389, while LDAPS (LDAP over '
  'TLS/SSL) uses TCP 636.'),
 ('A1X-127',
  'IT-5.2',
  'A1:2.1',
  'Why do real-time VoIP audio streams and live video conferences use UDP rather than TCP at the transport layer?',
  'UDP avoids handshake and retransmission delays',
  ['UDP automatically encrypts every voice payload with AES-256',
   'UDP guarantees in-order delivery via sequence acknowledgments',
   'UDP dynamically assigns IPv4 addresses to VoIP handsets'],
  'Retransmitting a late audio packet in TCP stalls playback and worsens jitter; UDP sends datagrams immediately with '
  'minimal 8-byte header overhead.'),
 ('A1X-128',
  'IT-5.2',
  'A1:2.1',
  'A network monitoring server polls managed switches every 60 seconds for interface byte counters and listens for '
  'asynchronous link-down alerts from those switches. Which two UDP ports are used?',
  'UDP 161 for polling and UDP 162 for traps',
  ['UDP 53 for polling and TCP 53 for zone transfers',
   'UDP 67 for polling and UDP 68 for trap alerts',
   'TCP 143 for polling and TCP 993 for trap alerts'],
  'SNMP agents listen for manager GET/NEXT/WALK requests on UDP 161, while the NMS trap receiver listens for '
  'unsolicited traps/informs on UDP 162.'),
 ('A1X-129',
  'NO-1.3',
  'A1:2.1',
  'Which protocol dynamically assigns an IPv4 address, subnet mask, default gateway, and DNS server to a client via a '
  'four-step broadcast/unicast exchange on UDP ports 67 and 68?',
  'DHCP (Dynamic Host Configuration Protocol)',
  ['DNS (Domain Name System)', 'ARP (Address Resolution Protocol)', 'ICMP (Internet Control Message Protocol)'],
  'DHCP servers listen on UDP port 67 and clients listen on UDP port 68 during the DORA (Discover, Offer, Request, '
  'Acknowledge) lease process.'),
 ('A1X-130',
  'IT-5.4',
  'A1:2.2',
  'An office located 2 kilometers from a Doppler weather radar station notices that its 5 GHz Wi-Fi access points '
  'occasionally move clients from Channel 100 to Channel 36 automatically. Which regulatory mechanism caused the '
  'channel change?',
  'DFS (Dynamic Frequency Selection, 802.11h)',
  ['OFDMA sub-carrier allocation under IEEE 802.11ax',
   'CSMA/CD collision detection on half-duplex coax',
   'WPA3 Simultaneous Authentication of Equals (SAE)'],
  'In the 5 GHz UNII-2/2e bands (channels 52–144), DFS requires APs to monitor for military/weather radar pulses and '
  'vacate the channel immediately if radar is detected.'),
 ('A1X-131',
  'IT-5.4',
  'A1:2.2',
  'Which Wi-Fi generation introduced operation in the 6 GHz spectrum (up to 1,200 MHz of clean spectrum in North '
  'America) alongside 2.4 GHz and 5 GHz using OFDMA and 1024-QAM?',
  'Wi-Fi 6E (IEEE 802.11ax in 6 GHz)',
  ['Wi-Fi 4 (IEEE 802.11n on 2.4/5 GHz)',
   'Wi-Fi 5 (IEEE 802.11ac on 5 GHz only)',
   'IEEE 802.11g (2.4 GHz 54 Mb/s OFDM)'],
  'Wi-Fi 6E extends IEEE 802.11ax features (OFDMA, MU-MIMO, TWT, 1024-QAM) into the newly unlicensed 6 GHz band.'),
 ('A1X-132',
  'IT-5.4',
  'A1:2.2',
  'When designing a high-density 2.4 GHz wireless plan for a 30-classroom building in North America, why should the '
  'administrator restrict APs to 20 MHz channels on 1, 6, and 11 rather than using 40 MHz channel bonding?',
  'A 40 MHz channel overlaps and causes interference in 2.4 GHz',
  ['40 MHz channels are legally restricted to military satellites in 2.4 GHz',
   '2.4 GHz antennas physically melt when transmitting above 20 MHz width',
   'Client laptops only support 40 MHz channels when connected via Ethernet'],
  'Because 2.4 GHz has only three non-overlapping 20 MHz channels (1, 6, 11), bonding to 40 MHz consumes two-thirds of '
  'the entire band and creates co-/adjacent-channel interference.'),
 ('A1X-133',
  'NO-3.3',
  'A1:2.2',
  'A warehouse inventory system reads passive tags attached to pallets from 6 meters away as a forklift drives through '
  'a dock doorway without line-of-sight scanning. Which wireless technology is used?',
  'UHF RFID passive tags and portal readers',
  ['NFC (Near-Field Communication at 13.56 MHz)',
   'IrDA infrared line-of-sight optical transceivers',
   '802.11ad 60 GHz WiGig millimeter-wave'],
  'UHF RFID (860–960 MHz) powers passive tags via reader RF energy and reads dozens of tags simultaneously at '
  'distances of several meters.'),
 ('A1X-134',
  'IT-5.4',
  'A1:2.2',
  'What is the key difference between 802.11ac (Wi-Fi 5) and 802.11ax (Wi-Fi 6) when serving dozens of small-packet '
  'IoT and voice clients simultaneously?',
  '802.11ax uses OFDMA to subdivide channels into Resource Units',
  ['802.11ac operates only in 2.4 GHz whereas 802.11ax operates only in 900 MHz',
   '802.11ac uses WEP encryption whereas 802.11ax requires open authentication',
   '802.11ax removes MIMO antennas and limits every AP to a single spatial stream'],
  'OFDMA (Orthogonal Frequency-Division Multiple Access) in 802.11ax divides a channel into smaller sub-carriers '
  '(Resource Units) so an AP can transmit to or receive from multiple clients simultaneously.'),
 ('A1X-135',
  'IT-5.4',
  'A1:2.2',
  'A technician compares 2.4 GHz and 5 GHz Wi-Fi propagation inside an older brick-and-plaster building. Which '
  'statement accurately contrasts the two bands?',
  '2.4 GHz reaches farther; 5 GHz has more clean channels and speed',
  ['5 GHz penetrates concrete walls twice as far as 2.4 GHz due to shorter wavelength',
   '2.4 GHz provides 24 non-overlapping 20 MHz channels while 5 GHz has only 3',
   '5 GHz suffers interference from Bluetooth headsets and 2.4 GHz cordless phones'],
  'Lower frequencies (2.4 GHz, longer wavelength) diffract and attenuate less through walls, whereas 5 GHz attenuates '
  'faster but provides far more clean, non-overlapping spectrum.'),
 ('A1X-136',
  'IT-5.4',
  'A1:2.2',
  'Which IEEE 802.11 amendment introduced Wi-Fi 7 features including Multi-Link Operation (MLO), 320 MHz channels in 6 '
  'GHz, and 4096-QAM modulation?',
  'IEEE 802.11be',
  ['IEEE 802.11b', 'IEEE 802.11g', 'IEEE 802.11a'],
  'IEEE 802.11be (Extremely High Throughput / Wi-Fi 7) adds Multi-Link Operation across 2.4/5/6 GHz, 320 MHz channel '
  'width, and 4096-QAM.'),
 ('A1X-137',
  'IT-5.2',
  'A1:2.3',
  'A small manufacturing firm wants a single perimeter appliance that combines a stateful firewall, intrusion '
  'prevention (IPS), gateway anti-malware, web content filtering, and VPN termination. Which device category describes '
  'this appliance?',
  'UTM (Unified Threat Management) appliance',
  ['Unmanaged Layer 2 workgroup switch', 'Authoritative recursive DNS resolver', 'Stratum 1 NTP time appliance'],
  'A UTM appliance consolidates multiple security functions—stateful firewall, IDS/IPS, anti-malware, URL filtering, '
  'and VPN—into a single platform.'),
 ('A1X-138',
  'IT-5.2',
  'A1:2.3',
  'In a water treatment plant, ruggedized PLCs (Programmable Logic Controllers) monitor valve pressure and pump speed '
  'and report telemetry to a central human-machine interface (HMI). What type of operational environment is this?',
  'SCADA / ICS industrial control network',
  ['VDI (Virtual Desktop Infrastructure) pool',
   'Public SaaS multi-tenant webmail cluster',
   'Peer-to-peer workgroup print queue'],
  'SCADA / ICS networks manage industrial physical equipment (pumps, valves, power grids) using PLCs, RTUs, and HMIs '
  'and require strict network segmentation.'),
 ('A1X-139',
  'IT-5.2',
  'A1:2.3',
  'Why is it critical that all domain controllers, servers, and workstations on an Active Directory network '
  'synchronize their clocks to a common NTP server within 5 minutes?',
  'Kerberos tickets fail if clock skew exceeds 5 minutes',
  ['DHCP leases immediately expire if a client clock is off by more than 2 seconds',
   'Ethernet switches drop 802.1Q VLAN tags when system clocks are in different time zones',
   'SATA and NVMe drives refuse to mount NTFS volumes without an NTP stratum-1 pulse'],
  'Kerberos v5 defaults to a maximum 5-minute clock-skew tolerance to block ticket replay attacks; NTP (UDP 123) keeps '
  'all domain members synchronized.'),
 ('A1X-140',
  'IT-5.2',
  'A1:2.3',
  'An e-commerce company runs four identical web servers behind a single virtual IP address (`203.0.113.10`). Which '
  'infrastructure service distributes incoming HTTPS requests across the healthy servers and removes any server that '
  'fails a health check?',
  'Load balancer',
  ['Syslog collector', 'Print spooler server', 'DHCP relay agent'],
  'A load balancer terminates or distributes client requests across a pool of backend servers and performs continuous '
  'health checks to bypass failed nodes.'),
 ('A1X-141',
  'IT-5.2',
  'A1:2.3',
  'A school district routes all student web browsing through an intermediary server that caches frequently requested '
  'educational assets, enforces URL category blocks, and hides internal client IPv4 addresses. Which server role is '
  'performing this function?',
  'Forward proxy server',
  ['Authoritative MX mail exchanger', 'Fibre Channel SAN fabric switch', 'RADIUS AAA accounting server'],
  'A forward proxy acts on behalf of internal clients to filter outbound web requests, inspect content, and cache '
  'static responses.'),
 ('A1X-142',
  'IT-5.2',
  'A1:2.3',
  'After a security breach on a Linux web server, the attacker deletes `/var/log/auth.log` locally to hide their SSH '
  'brute-force attempts. Which network service ensures the security team still has an intact copy of those '
  'authentication events?',
  'Centralized Syslog / SIEM server receiving real-time logs',
  ['Local BIOS/UEFI hardware monitoring log on the web server motherboard',
   'A secondary DNS server performing AXFR zone transfers',
   'An unmanaged PoE switch powering the server rack fans'],
  'Forwarding logs in real time to a remote Syslog or SIEM server preserves an immutable audit trail even if an '
  'attacker compromises and wipes local logs on the host.'),
 ('A1X-143',
  'IT-5.2',
  'A1:2.3',
  'An organization wants incoming internet email scanned for phishing links, spoofed sender headers, and malicious '
  'macro attachments before messages ever reach the internal Exchange server. Which host service sits in the mail path '
  '(MX record) to perform this?',
  'Secure Email Gateway (spam gateway)',
  ['Print server with PCL6 drivers', 'TFTP provisioning server', 'NetBIOS WINS name server'],
  'A Secure Email Gateway (spam gateway) receives inbound SMTP mail via the domain’s MX record, checks SPF/DKIM/DMARC, '
  'sandboxes attachments, and forwards clean mail internally.'),
 ('A1X-144',
  'IT-5.3',
  'A1:2.4',
  'A company wants email receivers worldwide to know which outbound mail servers are authorized to send mail for '
  '`@novaklabs.example`, and further wants receivers to reject any message that fails SPF and DKIM alignment and send '
  'a forensic report. Which three DNS TXT records work together to accomplish this?',
  'SPF, DKIM, and DMARC TXT records',
  ['A (IPv4 host), AAAA (IPv6 host), and CNAME (canonical alias)',
   'MX (mail exchanger), PTR (reverse lookup), and NS (name server)',
   'SRV (service locator), SOA (start of authority), and CAA (cert authority)'],
  'SPF lists allowed sending IPs in a TXT record, DKIM publishes the public key to verify signed mail headers, and '
  'DMARC specifies the policy (none/quarantine/reject) and reporting URI when SPF/DKIM fail.'),
 ('A1X-145',
  'IT-5.3',
  'A1:2.4',
  'A networked laser printer in the Finance department must always receive IPv4 address `10.10.20.45` so client print '
  'queues never break, but the admin wants to manage all IP settings centrally from the DHCP server rather than typing '
  'static IPs on the printer LCD. What should the admin configure?',
  'DHCP reservation for the printer MAC at .45',
  ['An APIPA 169.254.20.45 address on the printer NIC',
   'A DNS CNAME record pointing 10.10.20.45 to localhost',
   'A 15-minute DHCP lease time with no exclusions'],
  'A DHCP reservation maps a specific client MAC address (DUID/client-identifier) to a fixed IP address within the '
  'DHCP scope.'),
 ('A1X-146',
  'IT-5.3',
  'A1:2.4',
  'A web team hosts their marketing site on a cloud CDN at `prod-cdn-442.cloudhost.net` and wants '
  '`www.novaklabs.example` to alias that hostname even if the CDN rotates its underlying IPv4 and IPv6 addresses. '
  'Which DNS record should be created for `www`?',
  'CNAME aliasing www to prod-cdn-442.cloudhost.net',
  ['AAAA record pointing www.novaklabs.example to 192.0.2.44',
   'MX record with priority 10 pointing to 2001:db8::44',
   'PTR record in the in-addr.arpa reverse lookup zone'],
  'A CNAME (Canonical Name) record aliases one domain name (`www`) to another canonical hostname, following any IP '
  'changes of the target automatically.'),
 ('A1X-147',
  'NO-4.2',
  'A1:2.4',
  'A DHCP scope is configured for `192.168.10.1` to `192.168.10.254` (`/24`), and the subnet router (`192.168.10.1`) '
  'plus ten static switches (`192.168.10.2`–`192.168.10.11`) have hard-coded static IPs. What must be configured on '
  'the DHCP server to prevent duplicate IP conflicts?',
  'DHCP exclusion range for 192.168.10.1–.11',
  ['A DNS MX record for 192.168.10.1 through 192.168.10.11',
   'An 802.1Q native VLAN tag of 254 on the router port',
   'A split-tunnel VPN profile for the ten switches'],
  'An exclusion range tells the DHCP server never to hand out addresses from that range (`192.168.10.1–.11`) because '
  'they are statically assigned to infrastructure devices.'),
 ('A1X-148',
  'IT-5.3',
  'A1:2.4',
  'Which DNS record maps a hostname to a 128-bit IPv6 address such as `2001:db8:85a3::8a2e:370:7334`?',
  'AAAA record',
  ['A record', 'CNAME record', 'MX record'],
  'An A record maps a hostname to a 32-bit IPv4 address, whereas an AAAA (quad-A) record maps a hostname to a 128-bit '
  'IPv6 address.'),
 ('A1X-149',
  'IT-5.3',
  'A1:2.4',
  'A coffee shop offers free public Wi-Fi with 200 visitors passing through each day, while a corporate desktop LAN '
  'has 80 fixed PCs that stay plugged in all week. How should DHCP lease durations be tuned for these two networks?',
  'Short lease (1–2 hr) on guest Wi-Fi; longer lease on LAN',
  ['30-day lease time on the coffee shop Wi-Fi so the pool never reclaims transient IPs',
   '60-second lease time on the fixed corporate LAN to maximize broadcast traffic',
   'Infinite lease time on the coffee shop Wi-Fi with DHCP disabled'],
  'High-churn guest networks need short DHCP leases so addresses from departed visitors are reclaimed quickly before '
  'the scope exhausts.'),
 ('A1X-150',
  'IT-5.3',
  'A1:2.4',
  'A physical 48-port switch serves both Accounting PCs and Engineering lab machines, and security policy requires '
  'separating their Layer 2 broadcast domains without buying a second switch. What feature accomplishes this?',
  'Separate VLANs on the managed switch',
  ['Installing an unmanaged 8-port hub between the two departments',
   'Changing the DNS suffix on the Accounting PCs',
   'Crimping crossover RJ45 cables for the Engineering PCs'],
  'VLANs logically partition a single physical switch into separate Layer 2 broadcast domains; traffic between VLANs '
  'must pass through a Layer 3 router or firewall.'),
 ('A1X-151',
  'IT-5.3',
  'A1:2.4',
  'A remote worker in a hotel needs an encrypted tunnel back to the corporate headquarters firewall so their laptop '
  'can access internal ERP servers over the public internet as if on the office LAN. Which technology provides this?',
  'Client-to-site VPN (Virtual Private Network)',
  ['VLAN trunking (IEEE 802.1Q)', 'APIPA link-local addressing', 'UPnP port forwarding on the hotel router'],
  'A client-to-site (remote-access) VPN establishes an authenticated, encrypted tunnel (IPsec or TLS/WireGuard) over '
  'untrusted public networks.'),
 ('A1X-152',
  'IT-5.4',
  'A1:2.5',
  'A fiber-to-the-premises (FTTP) ISP brings a single-mode optical fiber to the exterior wall of a small office and '
  'hands off a copper RJ45 Gigabit Ethernet jack to the customer’s router. Which device performs this '
  'optical-to-electrical conversion at the demarcation point?',
  'ONT (Optical Network Terminal)',
  ['DOCSIS 3.1 cable modem', 'DSL microfilter splitter', '110 punchdown patch panel'],
  'In passive optical networks (GPON/XGS-PON), the Optical Network Terminal (ONT) terminates the ISP fiber optic line '
  'and converts it to copper Ethernet.'),
 ('A1X-153',
  'IT-5.4',
  'A1:2.5',
  'An office has a 24-port non-PoE managed switch in the wiring closet and needs to install a single ceiling-mounted '
  '802.3at wireless access point 40 meters away where no AC power outlet exists. What is the most cost-effective '
  'hardware addition?',
  'An inline 802.3at PoE+ midspan injector',
  ['Replacing the entire 24-port switch with a chassis core switch',
   'Splicing 120 V AC building power onto the blue Cat 6 wire pair',
   'Installing a passive RJ45 splitter at the access point'],
  'A PoE injector (midspan) sits between a non-PoE switch port and the horizontal Cat 6 run, injecting DC power onto '
  'the Ethernet cable for a single powered device.'),
 ('A1X-154',
  'IT-5.4',
  'A1:2.5',
  'Why are solid-conductor horizontal Cat 6 cables from wall jacks terminated onto a patch panel in the telecom closet '
  'rather than crimped directly with RJ45 plugs and plugged into the switch?',
  'Solid horizontal wire breaks if flexed; patch panels use fixed IDCs',
  ['A patch panel amplifies Ethernet signals to extend Cat 6 runs to 500 meters',
   'A patch panel performs Layer 3 NAT and stateful packet inspection for each wall jack',
   'Switch RJ45 ports only accept fiber-optic LC connectors without a patch panel'],
  'Horizontal in-wall cable uses solid copper conductors punched down once to a fixed patch panel (110/Krone IDC), '
  'while flexible stranded patch cords connect the panel to the switch.'),
 ('A1X-155',
  'IT-5.4',
  'A1:2.5',
  'What capabilities distinguish a managed Layer 2 switch from an unmanaged switch in a small business network?',
  'VLANs, 802.1Q trunking, STP, SNMP, and port mirroring',
  ['Automatic plug-and-play MAC learning with zero configuration interface or VLAN support',
   'Converting coaxial DOCSIS RF signals into analog telephone dial tone',
   'Generating 48-bit burned-in MAC addresses for attached desktop NICs'],
  'Managed switches provide CLI/web/SNMP management, VLANs, trunking, Spanning Tree, QoS, 802.1X, and port mirroring, '
  'whereas unmanaged switches only forward frames in a single flat broadcast domain.'),
 ('A1X-156',
  'IT-5.4',
  'A1:2.5',
  'A technician is ordering a PoE switch to power high-wattage dual-radio Wi-Fi 7 access points and pan-tilt-zoom '
  'heated outdoor cameras that draw 51 W each. Which IEEE PoE standard must the switch ports support?',
  'IEEE 802.3bt (PoE++ Type 3/4, 60–100 W)',
  ['IEEE 802.3af (PoE Type 1, supplying up to 15.4 W at the PSE)',
   'IEEE 802.3at (PoE+ Type 2, supplying up to 30 W at the PSE)',
   'IEEE 802.1D (Classic Spanning Tree Protocol)'],
  'IEEE 802.3bt (PoE++) delivers up to 60 W (Type 3) or 90–100 W (Type 4) over all four twisted pairs.'),
 ('A1X-157',
  'IT-5.4',
  'A1:2.5',
  'A home office subscriber receives broadband internet over the existing hybrid fiber-coaxial (HFC) television line '
  'using an F-type connector. Which device demodulates the RF channels into Ethernet?',
  'Cable modem (DOCSIS)',
  ['DSL modem (ADSL2+/VDSL2 over RJ11)', 'Optical Network Terminal (GPON over SC/APC)', 'PoE midspan power injector'],
  'A cable modem terminates coaxial cable via an F-type connector and uses DOCSIS to modulate/demodulate IP traffic '
  'over hybrid fiber-coax.'),
 ('A1X-158',
  'IT-5.4',
  'A1:2.5',
  'Which 48-bit hardware identifier is burned into a Network Interface Card (NIC) ROM and used by Layer 2 switches to '
  'build their forwarding table?',
  '48-bit MAC hardware address',
  ['IPv4 default gateway address', 'TCP ephemeral source port number', 'DNS Fully Qualified Domain Name (FQDN)'],
  'Every Ethernet/Wi-Fi NIC has a 48-bit (6-byte, 12-hex-digit) MAC address consisting of a 24-bit OUI and a 24-bit '
  'device identifier.'),
 ('A1X-159',
  'IT-5.1',
  'A1:2.6',
  'A technician inspects a desktop PC that cannot reach the internet and sees IPv4 address `169.254.88.14` with subnet '
  'mask `255.255.0.0` and a blank default gateway. What does this address indicate?',
  'DHCP failed and the PC self-assigned an APIPA address',
  ['The ISP assigned a routable public Class B IPv4 address directly to the PC',
   'The user manually configured a valid RFC 1918 private address for VLAN 88',
   'The PC is using a loopback diagnostic address reserved for local NIC testing'],
  'When a DHCP client fails to receive a DHCPOFFER, it assigns itself an Automatic Private IP Addressing (APIPA) '
  'address in `169.254.0.0/16`, which is non-routable and has no default gateway.'),
 ('A1X-160',
  'IT-5.1',
  'A1:2.6',
  'Which three IPv4 address blocks are reserved by RFC 1918 for private internal networks and require NAT to '
  'communicate on the public internet?',
  '10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16',
  ['127.0.0.0/8, 169.254.0.0/16, and 224.0.0.0/4',
   '8.8.8.0/24, 1.1.1.0/24, and 208.67.222.0/24',
   '172.32.0.0/16, 192.0.2.0/24, and 198.51.100.0/24'],
  'RFC 1918 defines `10.0.0.0/8`, `172.16.0.0/12` (`172.16.0.0–172.31.255.255`), and `192.168.0.0/16` as private IPv4 '
  'ranges.'),
 ('A1X-161',
  'IT-5.1',
  'A1:2.6',
  'On a SOHO subnet using `192.168.1.0/24` (mask `255.255.255.0`) where the router LAN interface is `192.168.1.1` and '
  'the DHCP pool is `.100` to `.200`, which static IPv4 configuration is valid for a local NAS appliance?',
  'IP 192.168.1.25 /24, gateway and DNS 192.168.1.1',
  ['IP 192.168.1.255, mask 255.255.255.0, gateway 192.168.1.1, DNS 8.8.8.8',
   'IP 192.168.2.25, mask 255.255.255.0, gateway 192.168.1.1, DNS 192.168.1.1',
   'IP 192.168.1.150, mask 255.255.255.252, gateway 192.168.1.0, DNS 1.1.1.1'],
  '`192.168.1.25` is in the `192.168.1.0/24` subnet, outside the `.100–.200` DHCP pool, and not the network (`.0`), '
  'gateway (`.1`), or broadcast (`.255`) address.'),
 ('A1X-162',
  'IT-5.4',
  'A1:2.6',
  'A small law firm sets up a new SOHO wireless router. Which combination of wireless and management settings provides '
  'the strongest baseline security for staff laptops and client visitors?',
  'Change admin password, disable UPnP/WAN admin, use WPA3 + Guest VLAN',
  ['Keep the default admin login, hide the SSID broadcast with Open authentication, and enable UPnP for all LAN hosts',
   'Enable WEP-128 encryption, allow WAN HTTP administration on port 80, and bridge guest devices onto the server LAN',
   'Use MAC address filtering with no encryption and set the router DMZ host to the firm’s file server'],
  'Hiding an SSID or filtering MAC addresses provides no encryption; real SOHO hardening requires strong admin '
  'credentials, WPA3 (or WPA2/WPA3), disabling UPnP/WAN admin, and isolating guests.'),
 ('A1X-163',
  'NO-1.2',
  'A1:2.6',
  'An IPv6-enabled workstation displays two addresses on its Ethernet interface: `fe80::21a:2bff:fe3c:4d5e/64` and '
  '`2001:db8:400:10::55/64`. What is the purpose of the `fe80::/10` address?',
  'IPv6 link-local address for NDP and local router discovery',
  ['It is a globally routable public IPv6 address assigned by IANA for internet web hosting',
   'It is an IPv4-mapped broadcast address that forwards packets to every subnet in the autonomous system',
   'It is a multicast group address reserved exclusively for OSPFv3 designated routers'],
  'Every IPv6 interface automatically generates a link-local address in `fe80::/10` used for Neighbor Discovery '
  'Protocol (NDP), router advertisements, and next-hop routing on the local link.'),
 ('A1X-164',
  'IT-5.1',
  'A1:2.6',
  'A user on `10.10.5.42/24` can ping other workstations in `10.10.5.0/24` and can print to the local printer at '
  '`10.10.5.15`, but cannot reach `10.10.20.10` or any internet IP address. Which TCP/IP parameter is misconfigured on '
  'the user’s PC?',
  'Default gateway',
  ['NIC MAC address', 'Localhost loopback (127.0.0.1)', 'Workgroup name'],
  'When a host can communicate with every device on its own local subnet (`/24`) but cannot reach any remote subnet or '
  'internet IP, its default gateway is missing or incorrect.'),
 ('A1X-165',
  'IT-5.4',
  'A1:2.6',
  'A small studio connects Smart TVs and IoT smart plugs to the SOHO router and wants to prevent those IoT devices '
  'from initiating connections to the owner’s accounting workstation while still giving them internet access. What '
  'should be configured?',
  'Place IoT devices on an isolated VLAN or Guest SSID',
  ['Configure port forwarding on the router WAN port to the accounting workstation',
   'Assign the IoT devices static IPv4 addresses in the same /24 subnet as the workstation',
   'Disable the stateful firewall on the SOHO router'],
  'Placing untrusted IoT devices on a segmented VLAN or isolated Guest SSID blocks east-west traffic to internal '
  'workstations while permitting outbound internet access.'),
 ('A1X-166',
  'NO-3.2',
  'A1:2.7',
  'A remote geological research camp in northern Alaska has no fiber, cable, or cellular towers within 100 km. Staff '
  'noticed that traditional geostationary satellite links had ~600 ms round-trip latency that broke interactive SSH '
  'and VoIP calls. Which connection type provides broadband with ~25–50 ms latency at that site?',
  'Low-Earth Orbit (LEO) satellite internet',
  ['Geostationary (GEO) satellite at 35,786 km altitude',
   'ADSL2+ over dry copper twisted pair beyond 18 km',
   '10GBASE-SR multimode OM4 fiber patch cord'],
  'LEO satellites orbit at ~500–1,200 km rather than 35,786 km (GEO), cutting propagation latency from ~600 ms down to '
  '~25–50 ms.'),
 ('A1X-167',
  'NO-3.2',
  'A1:2.7',
  'A rural grain elevator 12 km from town has unobstructed line-of-sight to a water tower where a regional provider '
  'mounts directional 5 GHz / 60 GHz sector antennas. Which internet access technology uses a rooftop subscriber CPE '
  'radio pointed at that tower?',
  'WISP fixed wireless rooftop CPE radio',
  ['DOCSIS 3.1 hybrid fiber-coaxial cable broadband',
   'Synchronous Optical Network (SONET) OC-192 ring',
   'Bluetooth Personal Area Network (PAN) piconet'],
  'A WISP delivers fixed wireless broadband from a central tower or high point to directional rooftop '
  'customer-premises equipment (CPE) radios.'),
 ('A1X-168',
  'NO-3.2',
  'A1:2.7',
  'Why does a residential ADSL (Asymmetric Digital Subscriber Line) connection experience noticeably lower download '
  'and upload speeds when the home is 4.5 km from the telephone company central office (DSLAM) compared to a neighbor '
  '800 m away?',
  'DSL signals attenuate rapidly over long copper loops',
  ['ADSL shares coaxial RF bandwidth with every television set on the street',
   'Rain fade absorbs DSL signals in the atmosphere during storms',
   'Single-mode fiber modal dispersion limits ADSL to 300 meters'],
  'DSL runs over voice-grade copper telephone lines (RJ11); signal attenuation increases steeply with loop length from '
  'the DSLAM.'),
 ('A1X-169',
  'NO-3.2',
  'A1:2.7',
  'A university connects four campus buildings spread across a single city using high-speed dark fiber links leased '
  'from the municipal utility. Which network scope classification describes this city-wide interconnect?',
  'MAN (Metropolitan Area Network)',
  ['PAN (Personal Area Network)', 'SAN (Storage Area Network)', 'WLAN (Wireless Local Area Network)'],
  'A Metropolitan Area Network (MAN) spans a city or large campus cluster, sitting between a single-building LAN and a '
  'cross-country WAN.'),
 ('A1X-170',
  'NO-3.2',
  'A1:2.7',
  'In a data center, database servers connect to a dedicated, low-latency Fibre Channel and iSCSI fabric that provides '
  'block-level disk LUNs rather than file-level SMB/NFS shares. What type of network is this?',
  'SAN (Storage Area Network) block fabric',
  ['PAN (Personal Area Network)', 'MAN (Metropolitan Area Network)', 'WISP (Wireless ISP)'],
  'A Storage Area Network (SAN) presents high-speed block-level storage (via Fibre Channel, FCoE, or iSCSI) directly '
  'to servers as if the disks were locally attached.'),
 ('A1X-171',
  'NO-3.2',
  'A1:2.7',
  'Which broadband technology delivers symmetrical multi-gigabit upload and download speeds immune to electromagnetic '
  'interference (EMI) and lightning surges along the outside plant?',
  'FTTH / FTTP optical fiber broadband',
  ['DOCSIS coaxial cable internet', 'VDSL2 copper telephone line', '5G sub-6 GHz cellular hotspot'],
  'Optical fiber transmits light pulses through glass rather than electrical current over copper, offering symmetrical '
  'multi-gigabit speeds and complete immunity to EMI/RFI.'),
 ('A1X-172',
  'NO-3.2',
  'A1:2.7',
  'A smartwatch, wireless earbuds, and continuous glucose monitor communicate with a user’s smartphone over a range of '
  'a few meters. Which network category describes this personal device group?',
  'PAN (Personal Area Network)',
  ['WAN (Wide Area Network)', 'MAN (Metropolitan Area Network)', 'SAN (Storage Area Network)'],
  'A Personal Area Network (PAN) interconnects wearable and personal peripherals within a few meters of an individual, '
  'typically over Bluetooth, BLE, or NFC.'),
 ('A1X-173',
  'IT-5.3',
  'A1:2.8',
  'A technician finds an unlabeled bundle of 24 Cat 6 cables in the wiring closet and needs to identify which specific '
  'cable goes to the receptionist’s wall jack on the first floor. Which tool pair should the technician use?',
  'Tone generator at the jack and inductive probe in the closet',
  ['Optical time-domain reflectometer (OTDR) and a fusion splicer',
   'RJ45 modular crimper and a coaxial cable stripper',
   'Hardware loopback plug and a spectrum Wi-Fi analyzer'],
  'A tone generator places an audible modulated signal onto the copper pair at the wall jack, and the inductive probe '
  'detects that tone when touched to the matching cable in the closet.'),
 ('A1X-174',
  'IT-5.3',
  'A1:2.8',
  'When terminating solid-conductor Cat 6A horizontal cable onto the rear IDC slots of a 110 patch panel or keystone '
  'jack, which tool seats the wire and trims the excess conductor flush in one motion?',
  '110 impact punchdown tool with cut blade',
  ['RJ45 modular ratcheting crimper', 'Visual fault locator (VFL) laser pen', 'Rotary coaxial insulation stripper'],
  'An impact punchdown tool pushes each insulated wire into the Insulation Displacement Connector (IDC) slot and '
  'shears off the tail on the cut side of the 110 blade.'),
 ('A1X-175',
  'IT-5.3',
  'A1:2.8',
  'A user reports that a newly made Cat 6 patch cord links at only 100 Mb/s instead of 1000BASE-T. Which tool quickly '
  'reveals that pin 4 and pin 5 have an open circuit and pins 3 and 6 are reversed?',
  'Continuity / wiremap cable tester',
  ['Inductive toner probe wand', 'Passive network tap appliance', 'Punchdown impact tool'],
  'A continuity/wiremap cable tester checks all 8 pins end-to-end for opens, shorts, crossed pairs, and split pairs.'),
 ('A1X-176',
  'NO-2.3',
  'A1:2.8',
  'A network engineer needs to verify Whether a server’s physical Gigabit Ethernet NIC transceiver and OS driver can '
  'transmit and receive frames locally without connecting the server to a switch. Which small plug-in tool '
  'accomplishes this?',
  'RJ45 hardware loopback plug',
  ['T568B straight-through patch cord with one end left unplugged',
   'Tone generator alligator clip set',
   '110 keystone punchdown block'],
  'A hardware loopback plug loops the NIC’s transmit pairs back into its own receive pairs so self-diagnostics can '
  'test the physical port hardware.'),
 ('A1X-177',
  'IT-5.3',
  'A1:2.8',
  'Users in a medical clinic report that Wi-Fi drops every afternoon even though no neighbor SSIDs appear in Windows '
  'Wi-Fi lists. Which tool detects both 802.11 channel utilization AND non-Wi-Fi RF interference in 2.4 GHz and 5 GHz?',
  'Wi-Fi / RF spectrum analyzer',
  ['Copper TDR cable certifier', 'RJ45 ratcheting crimper', 'Optical power meter'],
  'A Wi-Fi / RF spectrum analyzer visualizes channel overlap, RSSI, noise floor, and non-802.11 interferers across the '
  'radio spectrum.'),
 ('A1X-178',
  'NO-2.3',
  'A1:2.8',
  'An incident responder needs to capture a bit-for-bit copy of full-duplex traffic on an inline trunk link to an IDS '
  'sensor without introducing switch CPU load or dropping packets if the monitoring appliance loses power. Which '
  'hardware device is designed for this?',
  'Passive optical or copper network TAP',
  ['Unmanaged 10/100 Mb/s half-duplex repeater hub',
   'Inductive tone-and-probe cable locator kit',
   'RJ11 DSL microfilter inline splitter'],
  'A network TAP passively splits or duplicates Tx and Rx traffic streams to a monitoring port without altering packet '
  'timing or introducing a single point of failure.'),
 ('A1X-179',
  'IT-5.3',
  'A1:2.8',
  'Before sliding an 8P8C (RJ45) modular plug onto the end of a stranded Cat 6 patch cable and crimping the gold '
  'contact pins into the conductors, which tool removes the outer PVC jacket cleanly without nicking the twisted pairs '
  'inside?',
  'Adjustable UTP cable stripper',
  ['110/66 impact punchdown tool', 'Loopback diagnostic adapter', 'Wi-Fi heat-map survey scanner'],
  'A UTP cable stripper scores only the outer jacket to a preset depth so the inner conductor insulation remains '
  'intact before untwisting and crimping.'),
 ('A1X-180',
  'IT-3.4',
  'A1:3.1',
  'A print photo retoucher requires a 27-inch monitor that maintains accurate sRGB/DCI-P3 colors and consistent '
  'contrast even when viewed at wide off-center angles by clients sitting beside the desk. Which LCD panel technology '
  'best fits this use case?',
  'IPS (In-Plane Switching)',
  ['TN (Twisted Nematic)', 'Monochrome passive STN', 'Reflective e-ink display'],
  'IPS aligns liquid crystals parallel to the glass substrate, delivering the widest viewing angles (178°) and most '
  'accurate color reproduction among LCD panel types.'),
 ('A1X-181',
  'IT-3.4',
  'A1:3.1',
  'Which display technology uses self-emissive organic compounds for every individual sub-pixel—requiring no backlight '
  'layer at all—to achieve true black levels (infinite contrast ratio) and near-instantaneous pixel response, at the '
  'risk of static-image burn-in?',
  'OLED self-emissive organic display panel',
  ['TN (Twisted Nematic) LCD with edge LED backlight',
   'VA (Vertical Alignment) LCD with CCFL inverter',
   'DLP projector with a spinning color wheel'],
  'OLED pixels emit their own light when current passes through an organic film and turn completely off for black, '
  'eliminating the LCD backlight.'),
 ('A1X-182',
  'IT-3.4',
  'A1:3.1',
  'An older ruggedized industrial laptop uses a Cold Cathode Fluorescent Lamp (CCFL) backlight rather than an LED '
  'backlight. If the LCD image is faintly visible under a flashlight but the backlight stays dark, which high-voltage '
  'board between the DC system board and the CCFL tube has likely failed?',
  'DC-to-AC high-voltage backlight inverter',
  ['The capacitive touch digitizer controller',
   'The discrete PCIe graphics card VRAM',
   'The Hall-effect lid-close switch'],
  'CCFL backlights require high-voltage AC supplied by an inverter board that converts low-voltage DC from the '
  'motherboard; LED-backlit panels do not use an AC inverter.'),
 ('A1X-183',
  'IT-3.4',
  'A1:3.1',
  'A user replaces a 24-inch 1920x1080 (Full HD) monitor with a 24-inch 3840x2160 (4K UHD) monitor of the exact same '
  'physical diagonal size. How does this affect pixel density (PPI) and native sharpness?',
  'Pixel density doubles (~92 to ~184 PPI) with 4x total pixels',
  ['Pixel density drops in half because 4K pixels are physically larger than 1080p pixels',
   'Refresh rate automatically increases from 60 Hz to 240 Hz at the same pixel density',
   'Aspect ratio changes from 16:9 widescreen to 4:3 standard square'],
  '3840×2160 has twice the horizontal and twice the vertical resolution of 1920×1080 (8.29M vs 2.07M pixels), doubling '
  'pixels per inch (PPI) on the same 24-inch diagonal.'),
 ('A1X-184',
  'IT-3.4',
  'A1:3.1',
  'A home-theater enthusiast wants an LCD monitor for dark-room movie watching that offers deeper native contrast '
  '(3000:1 to 5000:1) than IPS while costing less than OLED, even if off-axis viewing angles and dark-transition '
  'response times are slightly slower than IPS/TN. Which LCD panel type provides this?',
  'VA (Vertical Alignment)',
  ['TN (Twisted Nematic)', 'CRT (Cathode Ray Tube)', 'Plasma gas discharge'],
  'VA (Vertical Alignment) panels block backlight bleed much more effectively than IPS or TN when pixels are off, '
  'yielding 3000:1+ native contrast ratios.'),
 ('A1X-185',
  'IT-3.4',
  'A1:3.1',
  'What is the advantage of a Mini-LED backlight over a conventional edge-lit LED backlight in an HDR LCD monitor?',
  'Hundreds of Mini-LED local dimming zones boost HDR contrast',
  ['Mini-LED eliminates the liquid-crystal layer and polarizers completely like OLED',
   'Mini-LED requires a high-voltage AC fluorescent inverter board in the bezel',
   'Mini-LED limits the monitor refresh rate to 30 Hz interlaced'],
  'Mini-LED backlights use thousands of sub-millimeter LEDs across hundreds or thousands of local dimming zones behind '
  'the LCD layer for high HDR peak luminance and deep local contrast.'),
 ('A1X-186',
  'IT-3.4',
  'A1:3.1',
  'A tablet screen displays a crisp image without cracks, but touching icons anywhere on the left half of the glass '
  'produces no response. Which layer of the display assembly is faulty?',
  'Capacitive touch digitizer sensor',
  ['The LED backlight array', 'The IPS liquid-crystal matrix', 'The GPU HDMI output controller'],
  'The digitizer is the transparent capacitive sensor layer bonded over the display panel that translates finger or '
  'stylus touch into X/Y coordinates.'),
 ('A1X-187',
  'IT-3.4',
  'A1:3.2',
  'A facility manager is running horizontal Cat 6A network cables through the return-air drop ceiling space (used '
  'directly for HVAC air circulation without enclosed metal ducts). Which cable jacket fire rating is required by '
  'building code?',
  'Plenum-rated (CMP) low-smoke jacket',
  ['Riser-rated (CMR) standard PVC jacket',
   'General-purpose (CM/CMG) PVC patch cord jacket',
   'Direct-burial gel-filled PE outdoor jacket'],
  'Spaces used for environmental air return (plenums) require CMP (plenum-rated) cable whose fluoropolymer jacket '
  'resists flame spread and emits minimal toxic smoke.'),
 ('A1X-188',
  'IT-3.4',
  'A1:3.2',
  'A workstation GPU has only three DisplayPort 1.4 outputs and one HDMI 2.1 output, and it must drive a legacy analog '
  'projector that only has a 15-pin 3-row DE-15 (DB-15) blue input jack. What is needed to connect them?',
  'Active DisplayPort/HDMI-to-VGA DAC adapter',
  ['A passive DVI-D single-link to HDMI pin-to-pin adapter',
   'A passive USB-A 2.0 to RS-232 DB-9 serial null-modem cable',
   'An S/PDIF optical Toslink audio patch cord'],
  'DisplayPort and HDMI output purely digital signals, whereas 15-pin VGA carries analog RGBHV video, requiring an '
  'active DAC (digital-to-analog converter) chip.'),
 ('A1X-189',
  'NO-2.3',
  'A1:3.2',
  'A technician is patching a 10GBASE-LR SFP+ transceiver (1310 nm laser) to a cross-campus patch panel that reaches a '
  'building 4 kilometers away. Which fiber cable type and connector style matches a standard SFP+ transceiver?',
  'Single-mode OS2 fiber with duplex LC plugs',
  ['Multimode fiber (OM1, 62.5/125 µm orange jacket) with bayonet ST connectors',
   'Multimode fiber (OM3, 50/125 µm aqua jacket) with 12-fiber MPO ribbon connectors',
   'Shielded Cat 8 copper twinax with RJ11 modular plugs'],
  'SFP/SFP+ transceivers use small form-factor duplex LC connectors, and a 4 km 1310 nm 10GBASE-LR link requires 9/125 '
  'µm OS1/OS2 single-mode fiber.'),
 ('A1X-190',
  'IT-3.4',
  'A1:3.2',
  'A technician needs to connect a laptop to the RS-232 serial console port of a rackmount UPS that uses a 9-pin male '
  'D-sub connector. Which connector name refers to that 9-pin serial interface?',
  'DB-9 (DE-9) serial connector',
  ['RJ45 (8P8C) modular connector', 'F-type threaded coaxial connector', 'Molex 4-pin LP4 power connector'],
  'RS-232 serial console connections traditionally use a 9-pin D-subminiature connector commonly called DB-9 '
  '(technically DE-9), often paired with a USB-to-serial adapter or RJ45 rollover cable.'),
 ('A1X-191',
  'IT-3.4',
  'A1:3.2',
  'Which video interface supports Multi-Stream Transport (MST)—allowing a single port on a PC to daisy-chain two or '
  'three independent 1080p/1440p monitors in series—and features a 20-pin asymmetrical latching connector?',
  'DisplayPort (DP) with Multi-Stream Transport',
  ['VGA (DE-15)', 'DVI-I Dual Link', 'Composite RCA'],
  'DisplayPort natively supports packetized Multi-Stream Transport (MST) for daisy-chaining multiple independent '
  'displays from one port and uses a 20-pin latching connector.'),
 ('A1X-192',
  'IT-3.4',
  'A1:3.2',
  'When installing an internal 2.5-inch SATA III SSD into a desktop PC, which two cables must be connected to the '
  'drive?',
  '7-pin SATA data cable and 15-pin SATA power cable',
  ['A 40-pin PATA IDE ribbon cable and a 4-pin Berg floppy power connector',
   'A 6+2-pin PCIe auxiliary power cable and an M.2 M-key standoff screw',
   'An 8-pin EPS12V cable and a USB 3.0 19-pin internal front-panel header'],
  '2.5-inch and 3.5-inch SATA drives use an L-keyed 7-pin SATA data cable (6 Gb/s) and a wider L-keyed 15-pin SATA '
  'power plug from the power supply.'),
 ('A1X-193',
  'IT-3.4',
  'A1:3.2',
  'A factory floor runs Ethernet cabling alongside 480 V three-phase variable-frequency motor drives that generate '
  'intense electromagnetic interference (EMI). Which twisted-pair cabling prevents EMI from corrupting Ethernet frames '
  'when properly grounded?',
  'Shielded Twisted Pair (STP) with grounded jacks',
  ['Unshielded Cat 3 UTP voice-grade station wire',
   'Flat untwisted silver-satin 6P2C RJ11 telephone cord',
   'CCA (Copper-Clad Aluminum) unshielded patch cable'],
  'Shielded Twisted Pair (STP/F/UTP/S/FTP) wraps the pairs in metallic foil and/or braid shielding that drains induced '
  'electromagnetic noise to ground.'),
 ('A1X-194',
  'IT-3.4',
  'A1:3.2',
  'What is the maximum certified distance for 10GBASE-T (10 Gb/s Ethernet) over unshielded Cat 6 versus Cat 6A '
  'horizontal copper cabling?',
  '55 meters on Cat 6 and 100 meters on Cat 6A',
  ['Up to 100 meters on Cat 6 and up to 500 meters on Cat 6A',
   'Up to 10 meters on Cat 6 and up to 30 meters on Cat 6A',
   'Up to 30 meters on Cat 6 and up to 55 meters on Cat 6A'],
  'Cat 6 supports 10GBASE-T up to 55 m depending on alien crosstalk, while Cat 6A (500 MHz bandwidth, tighter '
  'twists/spline) supports 10GBASE-T to the full 100 m channel length.'),
 ('A1X-195',
  'IT-2.1',
  'A1:3.3',
  'A technician is populating two identical 16 GB DDR5-6000 DIMMs onto an ATX motherboard that has four memory slots '
  'labeled `A1, A2, B1, B2` (where Channel A is `A1/A2` and Channel B is `B1/B2`, and the board silkscreen marks `A2` '
  'and `B2` as "FIRST"). Which slots should be populated?',
  'Slots A2 and B2 for dual-channel interleaving',
  ['Slots A1 and A2 so both modules share Channel A while Channel B stays empty',
   'Slots B1 and B2 so Channel A is reserved for the PCIe graphics card',
   'Slot A1 only, leaving the second 16 GB module in its antistatic bag'],
  'Installing one matched DIMM per memory channel in the primary daisy-chain end slots (`A2` and `B2`) enables '
  'dual-channel mode, doubling memory bus width.'),
 ('A1X-196',
  'IT-2.1',
  'A1:3.3',
  'A financial database server must detect and automatically correct single-bit memory flips caused by cosmic rays or '
  'electrical noise without crashing the OS, and halt cleanly on double-bit errors. Which RAM type is required?',
  'ECC RAM with a supported CPU and chipset',
  ['Non-ECC unbuffered gaming DDR4 RAM with RGB heat spreaders',
   'Virtual memory pagefile stored on a consumer USB 2.0 flash drive',
   'LPDDR4X mobile memory with XMP overclocking profiles'],
  'ECC memory stores extra parity/syndrome bits (Hamming/SECDED code) to correct single-bit errors on the fly and '
  'detect double-bit errors.'),
 ('A1X-197',
  'IT-2.3',
  'A1:3.3',
  'Why can a DDR5 desktop DIMM never be accidentally seated into a DDR4 motherboard slot even though both DDR4 and '
  'DDR5 desktop DIMMs have 288 pins?',
  'Different bottom key notch position and 1.1 V on-DIMM PMIC',
  ['DDR5 DIMMs are 2 inches longer than DDR4 DIMMs and use 400 pins',
   'DDR4 slots require 12 V DC whereas DDR5 slots require 24 V AC',
   'DDR5 modules only fit into 260-pin laptop SO-DIMM sockets'],
  'Every DDR generation relocates the physical key notch on the module edge to prevent cross-insertion between '
  'incompatible voltages and signaling architectures.'),
 ('A1X-198',
  'IT-2.1',
  'A1:3.3',
  'What is the architectural difference between DDR4 and DDR5 regarding memory sub-channels on a single DIMM?',
  'Dual 32-bit sub-channels per DIMM plus an on-module PMIC',
  ['A single DDR5 DIMM uses a single 16-bit serial bus and moves the voltage regulator back to the power supply',
   'DDR4 runs at 1.1 V with on-die ECC whereas DDR5 runs at 1.5 V with no burst length',
   'DDR5 eliminates dual-channel motherboards and allows only one DIMM per system'],
  'Each DDR5 DIMM provides two independent 32-bit addressable sub-channels (with 16n prefetch burst length) plus '
  'on-die ECC and an on-module Power Management IC (PMIC) at 1.1 V.'),
 ('A1X-199',
  'IT-2.1',
  'A1:3.3',
  'A technician is upgrading an All-in-One (AiO) desktop PC and a compact Mini-PC NUC. Upon opening the chassis, the '
  'memory slots are roughly half the length of a standard 5.25-inch desktop DIMM. Which memory form factor do these '
  'systems use?',
  'SO-DIMM small-outline memory module',
  ['Full-length 288-pin Registered RDIMM', 'M.2 2280 Key-M NVMe module', '30-pin SIMM legacy module'],
  'Laptops, Mini-PCs, and many All-in-One desktops use compact SO-DIMM modules (260-pin for DDR4, 262-pin for DDR5).'),
 ('A1X-200',
  'IT-2.1',
  'A1:3.3',
  'A user mixes one 8 GB DDR4-2666 DIMM and one 8 GB DDR4-3200 DIMM of the same voltage in a desktop motherboard. '
  'Assuming the system POSTs cleanly, at what speed will the memory controller run both modules?',
  'Both modules run at the slower DDR4-2666 speed',
  ['Both modules overclock automatically to DDR4-3200',
   'The memory controller averages the two speeds to DDR4-2933',
   'Each channel runs at its own independent clock frequency asynchronously'],
  'All populated memory channels share a common memory controller clock, so the BIOS/UEFI trains all DIMMs at the '
  'speed and timings of the slowest installed module.'),
 ('A1X-201',
  'IT-2.3',
  'A1:3.3',
  'After installing 64 GB of DDR5-6000 RAM, a user notices in Task Manager that the memory is running at the base '
  'JEDEC speed of 4800 MT/s instead of the advertised 6000 MT/s. Which UEFI setting loads the factory-tested '
  'high-speed timing profile stored on the DIMM’s SPD chip?',
  'Intel XMP or AMD EXPO memory profile',
  ['UEFI Secure Boot and Trusted Platform Module (TPM)',
   'Legacy CSM (Compatibility Support Module)',
   'S.M.A.R.T. acoustic management'],
  'RAM boots at conservative JEDEC base speeds (e.g., DDR5-4800) until Intel XMP or AMD EXPO is enabled in UEFI to '
  'apply the rated speed, timings, and voltage profile.'),
 ('A1X-202',
  'IT-3.1',
  'A1:3.4',
  'A video editing workstation requires a scratch storage array built from four 2 TB NVMe SSDs that provides both '
  'striped multi-drive read/write speed AND fault tolerance if one drive fails, with fast rebuilds that do not require '
  'parity calculations. Which RAID level meets these requirements and what is its usable capacity?',
  'RAID 10 (stripe of mirrors) with 4 TB usable',
  ['RAID 0 (stripe only), yielding 8 TB usable capacity with 1-drive fault tolerance',
   'RAID 1 (single mirror), yielding 6 TB usable capacity across 4 drives',
   'RAID 5 (distributed parity), yielding 8 TB usable capacity with zero parity overhead'],
  'RAID 10 combines mirroring (RAID 1) and striping (RAID 0) across at least 4 drives, delivering high IOPS without '
  'parity write penalties and surviving at least 1 drive failure (up to 1 per mirrored pair) at 50% capacity.'),
 ('A1X-203',
  'IT-3.1',
  'A1:3.4',
  'A storage engineer builds a 6-drive array using 4 TB SAS hard drives and selects RAID 6 because large-capacity HDD '
  'rebuilds take over 24 hours and the array must survive two simultaneous drive failures. How much usable storage '
  'capacity does this 6-drive RAID 6 array provide?',
  '16 TB usable (N - 2 drives with dual parity)',
  ['24 TB usable (100% of all 6 drives)',
   '20 TB usable (N - 1 drives = 5 × 4 TB)',
   '12 TB usable (50% of all 6 drives)'],
  'RAID 6 requires at least 4 drives and dedicates the equivalent of 2 drives to dual distributed parity ($N - 2$), '
  'allowing any 2 drives to fail without data loss.'),
 ('A1X-204',
  'IT-3.1',
  'A1:3.4',
  'Why does an M.2 PCIe 4.0 x4 NVMe SSD achieve sequential read speeds above 7,000 MB/s while a 2.5-inch SATA III SSD '
  'tops out around 550–600 MB/s?',
  'NVMe uses 4 parallel PCIe lanes vs SATA III 6 Gb/s bus limit',
  ['2.5-inch SATA SSDs use spinning magnetic platters at 7,200 RPM inside the casing',
   'M.2 NVMe SSDs store all files in volatile DRAM rather than non-volatile NAND flash',
   'SATA III cables operate in half-duplex coaxial mode at 100 MHz'],
  'The SATA III physical interface maxes out at 6 Gb/s (600 MB/s after 8b/10b encoding) with 1 command queue of 32 '
  'commands; NVMe over PCIe 4.0 x4 provides ~8 GB/s of full-duplex bandwidth and 64K queues.'),
 ('A1X-205',
  'IT-3.2',
  'A1:3.4',
  'A technician examines two M.2 2280 SSDs on the bench: Drive A has a single notch on the right side (M-key) and '
  'states "PCIe 4.0 x4 NVMe", while Drive B has two notches (B+M key) and states "M.2 SATA 6 Gb/s". What happens if '
  'Drive A (NVMe) is installed into an M.2 slot wired only for the SATA controller?',
  'The drive is not detected because NVMe requires PCIe lanes',
  ['Drive A will automatically fall back to SATA III 600 MB/s compatibility mode',
   'Drive A will short-circuit the 12 V ATX rail and trip the power supply OCP',
   'Drive A will format itself as a RAID 0 array with the optical drive'],
  'M.2 is a physical form factor that can carry PCIe (NVMe) lanes, a SATA port, or both; an NVMe-only SSD cannot '
  'communicate over a SATA-only M.2 port.'),
 ('A1X-206',
  'IT-3.1',
  'A1:3.4',
  'Which storage medium is best suited for cold, offline archival storage of 10 TB video masters on a shelf for 10+ '
  'years without periodic power-on refresh cycles (which NAND flash SSDs need to prevent charge leakage)?',
  'LTO magnetic tape or enterprise 3.5-inch HDD',
  ['Consumer QLC NAND M.2 NVMe SSD left unpowered in a warm cabinet',
   'Volatile DDR5 RDIMM modules stored in an antistatic bag',
   'RAM disk virtual volume configured in Windows'],
  'Unpowered NAND flash cells gradually leak trapped electrons over months/years (especially worn TLC/QLC at warm '
  'temperatures), whereas magnetic tape, archival optical media, and magnetic platters retain cold data much longer.'),
 ('A1X-207',
  'IT-3.1',
  'A1:3.4',
  'A user builds a 2-drive RAID 0 array from two 1 TB SSDs to maximize game loading speeds. One of the two SSDs '
  'suffers a controller failure. What percent of the user’s files on the RAID 0 volume can be read from the surviving '
  'drive?',
  '0% — losing one RAID 0 member destroys the volume',
  ['50% — half of the files are stored intact on the surviving 1 TB SSD',
   '100% — RAID 0 automatically rebuilds missing blocks from distributed parity',
   '75% — the NTFS Master File Table mirrors all user documents on both disks'],
  'RAID 0 splits every file into stripe blocks across all member disks without redundancy; the loss of any single '
  'member drive renders the entire filesystem unrecoverable.'),
 ('A1X-208',
  'IT-3.1',
  'A1:3.4',
  'An enterprise storage shelf requires dual-ported 12 Gb/s full-duplex serial disks that can connect to two redundant '
  'storage controllers simultaneously for multipath failover. Which drive interface supports this natively?',
  'SAS (Serial Attached SCSI)',
  ['SATA III (Serial ATA)', 'PATA / IDE 40-pin ribbon', 'eSATA external port'],
  'SAS (Serial Attached SCSI) operates at 12–24 Gb/s full-duplex and features dual ports on the connector so a single '
  'drive can attach to two redundant backplane expanders/controllers.'),
 ('A1X-209',
  'IT-3.1',
  'A1:3.4',
  'A photographer’s mirrorless camera records 8K RAW burst video to a removable flash card and requires sustained '
  'minimum write speeds of 90 MB/s. Which SD card speed class rating guarantees at least 90 MB/s sustained video write '
  'performance?',
  'V90 Video Speed Class (90 MB/s minimum)',
  ['Class 4 (4 MB/s minimum write)', 'U1 (UHS Speed Class 1, 10 MB/s minimum write)', 'V10 (10 MB/s minimum write)'],
  'SD Video Speed Class ratings (V10, V30, V60, V90) denote the guaranteed minimum sustained sequential write speed in '
  'megabytes per second.'),
 ('A1X-210',
  'IT-2.1',
  'A1:3.5',
  'A technician is building a compact living-room workstation inside a small-form-factor case that only has four rear '
  'expansion slots and measures 244 mm × 244 mm (9.6 in × 9.6 in) maximum board footprint. Which motherboard form '
  'factor fits this case while still offering up to four DIMM slots?',
  'microATX (244 × 244 mm, 4 slots)',
  ['Standard ATX (305 mm × 244 mm, 7 expansion slots)',
   'Extended ATX / E-ATX (305 mm × 330 mm)',
   'WTX server Dual-Socket board'],
  'microATX measures up to 244 × 244 mm (9.6 × 9.6 in), shares the top mounting standoff holes with ATX, supports up '
  'to 4 expansion slots, and typically includes 2 or 4 DIMM slots.'),
 ('A1X-211',
  'IT-2.1',
  'A1:3.5',
  'What is the physical difference between an Intel LGA (Land Grid Array) socket (such as LGA 1700/1851) or AMD AM5 '
  'socket and an older PGA (Pin Grid Array) socket (such as AMD AM4)?',
  'LGA puts pins in the motherboard socket; PGA puts pins on the CPU',
  ['In LGA, the CPU is permanently BGA-soldered at the factory and has no socket lever',
   'In PGA, the CPU slots vertically into a 288-pin edge connector like a RAM module',
   'LGA sockets require no heatsink or thermal paste because the pins dissipate all heat'],
  'Land Grid Array (LGA) places the delicate spring contacts in the motherboard socket (protected by a plastic cover '
  'until installation), whereas Pin Grid Array (PGA) places the pins on the CPU package.'),
 ('A1X-212',
  'IT-2.2',
  'A1:3.5',
  'During a CPU cooler upgrade, the technician cleans off the old dried thermal paste from the CPU integrated heat '
  'spreader (IHS) and cooler cold plate with 99% isopropyl alcohol. What is the exact purpose of applying a thin, even '
  'layer (pea-sized dot) of new thermal paste before clamping the heatsink?',
  'Fill microscopic air gaps between the CPU IHS and cooler base',
  ['To act as an electrical insulator between the CPU pins and the motherboard socket',
   'To permanently glue the heatsink to the motherboard so mounting screws are unnecessary',
   'To lower the CPU core voltage from 12 V down to 1.2 V'],
  'Air is a poor thermal conductor; thermal interface material (paste/pad) displaces microscopic air pockets between '
  'the two machined metal surfaces.'),
 ('A1X-213',
  'IT-2.4',
  'A1:3.5',
  'A Windows 11 upgrade readiness check reports that the PC meets CPU and RAM requirements, but fails because "TPM 2.0 '
  'must be supported and enabled" and "Secure Boot must be capable". On a modern AMD Ryzen or Intel Core motherboard '
  'without a discrete plug-in TPM header module, what should the technician enable in UEFI?',
  'Enable firmware TPM (fTPM/PTT) and UEFI Secure Boot',
  ['Enable Legacy CSM (Compatibility Support Module) and MBR boot order',
   'Disable CPU virtualization extensions (SVM / Intel VT-x)',
   'Clear the CMOS jumper and remove the CR2032 battery permanently'],
  'Modern CPUs integrate a firmware-based TPM 2.0 (Intel Platform Trust Technology / AMD fTPM) inside the '
  'processor/SoC that can be enabled in UEFI alongside UEFI Secure Boot.'),
 ('A1X-214',
  'IT-2.1',
  'A1:3.5',
  'An enterprise PKI root certificate authority server requires a dedicated, tamper-resistant PCIe or network '
  'appliance that generates, stores, and performs cryptographic signing with private keys inside a FIPS 140-3 '
  'validated physical boundary that wipes keys if opened. Which hardware component is this?',
  'HSM (Hardware Security Module)',
  ['USB 2.0 flash thumb drive', 'Audio sound card DAC', 'HDMI video capture card'],
  'A Hardware Security Module (HSM) is a dedicated, tamper-responsive cryptographic processor appliance or PCIe card '
  'used in servers/CAs to protect high-value private keys.'),
 ('A1X-215',
  'IT-2.1',
  'A1:3.5',
  'A mobile workstation laptop achieves 18 hours of battery life using a processor whose instruction set uses '
  'fixed-length, simplified instructions rather than complex variable-length x86/x64 instructions. Which CPU '
  'architecture does this processor use?',
  'ARM 64-bit RISC processor architecture',
  ['x86-32 IA-32 CISC with 4 GB RAM limit', 'x86-64 / AMD64 CISC desktop server socket', '8-bit microcontroller Z80'],
  'ARM processors use a Reduced Instruction Set Computing (RISC) architecture optimized for high performance-per-watt '
  'in smartphones, tablets, Apple Silicon Macs, and Snapdragon laptops.'),
 ('A1X-216',
  'IT-2.1',
  'A1:3.5',
  'A technician installs a PCIe x4 10GbE network card, but the motherboard’s only open PCIe x4 slot is blocked by a '
  'thick graphics card cooler. However, a full-length PCIe x16 mechanical slot at the bottom of the board is open. Can '
  'the PCIe x4 card be installed into the PCIe x16 slot?',
  'Yes — an x4 PCIe card up-plugs into an x16 slot at x4 speed',
  ['No — plugging an x4 card into an x16 slot shorts out the motherboard chipset',
   'Only if the technician saws off the rear 12 lanes of the motherboard x16 slot',
   'Only if the system is booted in 32-bit Legacy BIOS mode'],
  'PCI Express slots are backward/upward compatible: any narrower PCIe card (x1, x4, x8) seats into the front section '
  'of a wider x16 slot and auto-negotiates the shared lane width.'),
 ('A1X-217',
  'IT-3.3',
  'A1:3.5',
  'When a liquid-cooled AIO (All-in-One) workstation suddenly hits 100 °C CPU temperatures within 30 seconds of '
  'booting while the radiator exhaust air remains completely cool to the touch, even though the radiator fans are '
  'spinning, what component has failed?',
  'Failed or unplugged AIO liquid-cooler water pump',
  ['The chassis rear exhaust dust filter',
   'The DDR5 memory XMP timing profile',
   'The PSU 80 Plus Gold efficiency circuit'],
  'When the CPU overheats almost immediately while the radiator fins stay cold, coolant is not circulating from the '
  'CPU water block to the radiator because the pump has failed or lost power.'),
 ('A1X-218',
  'IT-3.3',
  'A1:3.6',
  'Which voltage rail on a modern ATX power supply delivers the bulk of the power consumed by high-wattage components '
  'such as the CPU voltage regulator (via the 8-pin EPS connector) and PCIe graphics cards?',
  '+12 V rail',
  ['+3.3 V rail', '+5 V standby (+5VSB) rail', '-12 V legacy serial rail'],
  'The +12 V rail powers the heaviest loads in a modern PC—CPU VRMs, discrete GPUs, cooling fans, and 3.5-inch drive '
  'motors—while +3.3 V and +5 V supply logic, M.2/SATA SSDs, and USB ports.'),
 ('A1X-219',
  'IT-3.3',
  'A1:3.6',
  'A technician is building a workstation in a compact Mini-ITX case with tight airflow and wants to attach only the '
  'exact power cables needed (24-pin ATX, 8-pin EPS, and one 16-pin GPU cable), leaving unused SATA and Molex leads in '
  'the box. Which PSU design allows every cable to detach from the power supply housing?',
  'Fully modular power supply',
  ['Non-modular (fixed-cable) power supply',
   'Redundant hot-swap 1U server power cage',
   'Passive inline PoE++ power injector'],
  'A fully modular PSU uses detachable connectors on the PSU chassis for all cables, minimizing cable clutter and '
  'improving case airflow.'),
 ('A1X-220',
  'IT-3.3',
  'A1:3.6',
  'An engineering workstation’s components draw 500 W of DC power under full rendering load. If the power supply is '
  'rated 80 Plus Gold and operates at 90% efficiency at that load, how much AC power does the PSU draw from the wall '
  'outlet, and what happens to the difference?',
  '~556 W AC from the wall, with ~56 W lost as heat',
  ['Exactly 450 W AC from the wall because 90% efficiency reduces component draw by 10%',
   '800 W AC from the wall at all times regardless of whether the PC is idle or loaded',
   '500 W AC from the wall, with the extra 10% stored in the CMOS battery'],
  'PSU wattage ratings specify maximum DC output; at 90% efficiency, delivering 500 W DC requires $500 / 0.90 '
  '\x07pprox 556\text{ W}$ AC input, with the 56 W loss converted into heat.'),
 ('A1X-221',
  'IT-3.3',
  'A1:3.6',
  'A rackmount virtualization host in a hospital data center must remain powered on even if one internal power supply '
  'fails or if a technician unplugs one power cord to move it to a different PDU circuit. Which power architecture is '
  'used?',
  'Dual hot-swap redundant PSUs on separate A/B PDUs',
  ['A single 1600 W ATX desktop power supply with a Y-splitter power cord',
   'A passive surge protector power strip plugged into a wall dimmer switch',
   'Switching the PSU voltage selector slide switch from 115 V to 230 V'],
  'Enterprise servers use dual (or N+1) hot-swappable power supply modules wired to independent A and B power '
  'distribution units so either PSU or circuit can fail with zero downtime.'),
 ('A1X-222',
  'IT-3.3',
  'A1:3.6',
  'A user builds a PC with a CPU rated at 170 W peak power, a GPU rated at 320 W TGP (with brief transient spikes), '
  'and 60 W for motherboard, RAM, NVMe drives, and fans (~550 W total continuous load). Why do PSU manufacturers and '
  'CompTIA best practices recommend sizing a quality 750 W–850 W PSU rather than a bare-minimum 550 W unit?',
  'Peak efficiency at 50–75% load plus headroom for GPU spikes',
  ['A 550 W PSU only outputs 275 W DC unless connected to a 240 V dryer outlet',
   'Windows 11 refuses to boot if the PSU wattage sticker is below 850 W',
   'Oversizing a PSU forces it to push 850 W continuously into the motherboard even at idle'],
  'A PSU only draws what the components demand, and sizing 25%–40% headroom keeps the unit in its optimal 50%–75% '
  'efficiency curve while absorbing GPU transient spikes.'),
 ('A1X-223',
  'IT-3.3',
  'A1:3.6',
  'An older bench PSU has a manual red slide switch on the rear panel labeled `115V / 230V` instead of active PFC '
  'auto-switching. What happens if that switch is accidentally set to `230V` while plugged into a standard North '
  'American `120V` AC wall outlet?',
  'Undervoltage prevents power-on or causes brownout resets',
  ['The PSU voltage doubler explodes immediately from overvoltage',
   'The PC runs twice as fast because current doubles automatically',
   'The motherboard 24-pin connector outputs 230 V DC to the CPU'],
  'Setting a manual-switching PSU to 230 V on a 115/120 V circuit disables the input voltage doubler, starving the '
  'primary side of voltage (whereas setting 115 V on a 230 V outlet destroys the PSU).'),
 ('A1X-224',
  'IT-3.3',
  'A1:3.6',
  'While upgrading an older motherboard that has a 20-pin ATX main power header with a modern power supply that has a '
  '24-pin (20+4) main connector, how should the technician connect the cable?',
  'Detach the 4-pin block from the 20+4-pin ATX plug',
  ['Force all 24 pins onto the 20-pin header so 4 pins overhang into the RAM slot',
   'Plug the 8-pin EPS12V CPU connector into the 20-pin mainboard socket',
   'Cut off the four extra wires with diagonal cutters'],
  'The 20+4-pin ATX main connector has a slide-off 4-pin block (+12V, +5V, +3.3V, COM) for backward compatibility with '
  'older 20-pin motherboards.'),
 ('A1X-225',
  'IT-4.3',
  'A1:3.7',
  'A graphic design agency prints vector illustrations and needs page layout output to look identical across macOS, '
  'Linux, and Windows workstations and commercial prepress RIPs. Which page description language (PDL) driver should '
  'be selected?',
  'PostScript (Adobe PS) driver',
  ['PCL 5e text-mode office driver', 'Raw ASCII line-printer driver', 'ESC/P dot-matrix control codes'],
  'PostScript describes pages mathematically as device-independent vector graphics and fonts, whereas PCL is optimized '
  'for fast office document rendering.'),
 ('A1X-226',
  'IT-4.3',
  'A1:3.7',
  'Human Resources shares a hallway multifunction printer (MFP) with four departments and needs to ensure payroll '
  'print jobs do not sit in the output bin unattended. Which MFP feature holds the job until the sender stands at the '
  'printer?',
  'Secured print with PIN or badge release at the MFD',
  ['Automatic duplex printing on Tray 2 with landscape orientation',
   'Direct Wi-Fi Peer-to-Peer printing with open authentication',
   'Enabling SNMPv1 public community read/write strings'],
  'Secured print (pull printing) queues the job until the user authenticates at the MFD via a badge reader or PIN '
  'pad.'),
 ('A1X-227',
  'IT-4.3',
  'A1:3.7',
  'A paralegal needs to scan a 60-page double-sided contract into a searchable PDF stored directly in the firm’s '
  '`\\filesrv\\scans` SMB share without flipping each page by hand. Which MFD hardware and workflow feature are used?',
  'Duplexing ADF (DADF) with Scan-to-SMB network folder',
  ['Flatbed platen glass with manual single-sheet placement and Scan-to-USB',
   'Tractor-feed pin platen with multipart carbon paper ribbon',
   'Thermal direct printhead with wax-resin transfer roll'],
  'An Automatic Document Feeder (ADF) with duplex scanning feeds multi-page stacks automatically, and Scan-to-SMB '
  'writes the PDF directly to a UNC share.'),
 ('A1X-228',
  'IT-4.3',
  'A1:3.7',
  'When loading heavy 200 gsm glossy cardstock into Tray 1 (bypass) on a departmental laser printer, why must the '
  'paper type and weight be set accurately in the tray configuration?',
  'It slows feed speed and raises fuser heat for thick media',
  ['Paper weight settings change the IPv4 subnet mask of the JetDirect card',
   'Setting heavy cardstock disables the laser diode and activates an impact ribbon',
   'Tray paper weight controls whether the printer uses TCP port 9100 or UDP 514'],
  'Heavy or glossy media requires a slower paper path speed and higher fuser heat to melt toner completely onto the '
  'thicker substrate.'),
 ('A1X-229',
  'IT-4.3',
  'A1:3.7',
  'Why should a corporate office deploy shared printers through a centralized print server rather than having 150 '
  'workstations connect directly to each printer’s IP address?',
  'Centralized driver deployment, queueing, and job auditing',
  ['Direct IP printing is limited by RFC to a maximum of three workstations per subnet',
   'A print server eliminates the need for toner cartridges or fuser assemblies',
   'Workstations cannot send PCL or PostScript jobs over Ethernet without a print server'],
  'A central print server manages driver updates for all clients automatically, spools jobs when a printer is busy, '
  'and maintains a unified audit log.'),
 ('A1X-230',
  'IT-4.3',
  'A1:3.7',
  'A user prints a 40-page manual and wants pages printed on both sides of each sheet, flipping along the long '
  'vertical edge like a standard book. Which two print driver settings accomplish this?',
  'Portrait orientation + Duplex flip on long edge',
  ['Landscape orientation + Simplex (single-sided)',
   'Portrait orientation + Duplex (flip on short edge)',
   'Poster 2x2 tiling + Reverse page order'],
  'Long-edge binding in Portrait orientation turns pages like a standard left-bound book; short-edge binding flips '
  'pages vertically like a top-bound calendar.'),
 ('A1X-231',
  'IT-4.3',
  'A1:3.7',
  'A retail popup kiosk has no wired Ethernet or office Wi-Fi router, and an associate needs to print receipts from a '
  'tablet directly to a wireless printer over a peer-to-peer Wi-Fi link created by the printer itself. Which '
  'technology enables this?',
  'Wi-Fi Direct (or AirPrint peer-to-peer)',
  ['802.1X RADIUS Enterprise authentication',
   'LPR/LPD over a WAN MPLS pseudowire',
   'Parallel IEEE 1284 Centronics 36-pin cable'],
  'Wi-Fi Direct allows a wireless printer to act as its own soft AP so a mobile device or laptop can print directly '
  'without an infrastructure router.'),
 ('A1X-232',
  'IT-4.3',
  'A1:3.8',
  'A shipping warehouse prints 4-part carbonless (NCR) bill-of-lading forms where four physical copies are produced in '
  'a single pass. Which printer technology physically strikes through multiple layers of paper?',
  'Impact dot-matrix printer with fabric ribbon',
  ['Direct thermal printer using heat-sensitive chemically coated paper',
   'Monochrome laser printer using a photosensitive OPC drum and fuser',
   'Piezoelectric inkjet printer using aqueous dye cartridges'],
  'Only impact printers (dot-matrix / daisy-wheel) physically strike an inked ribbon against the page to transfer '
  'impressions through multi-part forms.'),
 ('A1X-233',
  'IT-4.3',
  'A1:3.8',
  'How should a technician clean adhesive residue off a direct thermal receipt printer’s heating element and platen '
  'roller?',
  'Power off, cool, and wipe printhead with IPA swab',
  ['Vacuum the heating element with an ungrounded shop vac while powered on',
   'Scrape the ceramic heating element with a steel flathead screwdriver blade',
   'Run a laser printer fuser maintenance kit through the receipt slot'],
  'Direct thermal printheads are cleaned with anhydrous isopropyl alcohol swabs or cleaning cards to dissolve adhesive '
  'buildup without scratching the heating elements.'),
 ('A1X-234',
  'IT-4.3',
  'A1:3.8',
  'An office inkjet printer sits unused for six weeks, and now printed charts have missing horizontal bands of cyan '
  'and magenta even though the ink tanks are 80% full. What maintenance procedure should be run first?',
  'Run printhead nozzle check and automated head cleaning',
  ['Replace the high-voltage corona wire and transfer belt assembly',
   'Install a new 225,000-page fuser and separation pad kit',
   'Sand the rubber paper-pickup rollers with coarse grit sandpaper'],
  'Liquid inkjet nozzles dry out and clog when idle; running a nozzle check pattern followed by an automated '
  'head-cleaning cycle purges dried ink from the microscopic jets.'),
 ('A1X-235',
  'IT-4.3',
  'A1:3.8',
  'When loose toner spills inside a laser printer cavity, why must a technician NEVER use a standard office vacuum '
  'cleaner to clean it up?',
  'Fine toner passes standard bags, melts, and risks static/ESD sparks',
  ['Toner powder is strongly magnetic and welds the vacuum cleaner metal wand to the floor',
   'Standard vacuums spin in reverse when exposed to cyan and yellow pigments',
   'Vacuum suction erases the printer’s NVRAM IP address configuration'],
  'Laser toner requires an ESD-safe, grounded HEPA/ULPA toner vacuum with conductive attachments and ultra-fine '
  'filtration.'),
 ('A1X-236',
  'IT-4.3',
  'A1:3.8',
  'In the 7-step laser printing process (Processing, Charging, Exposing, Developing, Transferring, Fusing, Cleaning), '
  'what happens during the Exposing and Transferring steps?',
  'Laser writes latent image on drum; positive charge pulls toner to paper',
  ['Exposing: the fuser melts toner into the paper at 200 °C; Transferring: the wiper blade scrapes leftover toner '
   'into the waste bottle',
   'Exposing: the pickup roller pulls paper from Tray 2; Transferring: the RIP converts PCL commands into a bitmap in '
   'RAM',
   'Exposing: the primary charge roller applies +1000 V to the paper; Transferring: the laser vaporizes excess ink off '
   'the page'],
  'During Exposing, the laser neutralizes exposed areas of the negatively charged OPC drum so toner adheres there '
  'during Developing; during Transferring, a positive charge beneath the paper attracts the negatively charged toner '
  'off the drum.'),
 ('A1X-237',
  'IT-4.3',
  'A1:3.8',
  'A color laser printer produces pages where the cyan, magenta, yellow, and black layers are slightly offset, '
  'creating colored fringes around text. Which maintenance routine aligns the four color planes?',
  'Color registration / calibration cycle',
  ['Fuser thermal fuse replacement', 'ADF separation pad rotation', 'DHCP lease renewal on the NIC'],
  'Color laser printers use four separate toner passes onto a transfer belt; running color calibration/registration '
  'aligns all four color planes.'),
 ('A1X-238',
  'IT-4.3',
  'A1:3.8',
  'What three high-wear components are bundled together inside a scheduled laser printer Maintenance Kit?',
  'Fuser assembly, transfer roller, and pickup/separation rollers',
  ['Laser scanner polygon mirror, motherboard formatter PCB, and Ethernet NIC',
   'Four CMYK toner cartridges, a ream of 20 lb bond paper, and a USB cable',
   'Printhead ink carriage belt, waste ink sponge pad, and ribbon stepper motor'],
  'Laser maintenance kits replace the high-wear mechanical and thermal parts: the fuser unit, transfer roller, and '
  'rubber pickup/feed/separation rollers.'),
 ('A1X-239',
  'IT-6.1',
  'A1:4.1',
  'What distinguishes a Type 1 hypervisor (VMware ESXi, Microsoft Hyper-V Server, KVM/Proxmox) from a Type 2 '
  'hypervisor (VMware Workstation, VirtualBox, Parallels)?',
  'Type 1 runs on bare metal; Type 2 runs atop a host OS',
  ['Type 1 can only run 32-bit containers, whereas Type 2 runs bare-metal mainframes',
   'Type 1 requires no CPU or RAM, whereas Type 2 requires dual CPU sockets',
   'Type 2 boots before UEFI firmware, whereas Type 1 runs inside a web browser'],
  'Type 1 (bare-metal) hypervisors schedule hardware directly on the server, while Type 2 (hosted) hypervisors rely on '
  'a host OS for device drivers and scheduling.'),
 ('A1X-240',
  'IT-6.1',
  'A1:4.1',
  'A security analyst detonates a suspicious email attachment inside an isolated VM with no shared folders, no '
  'clipboard sharing, and a disconnected virtual NIC, then reverts to a clean snapshot. What is this isolated '
  'environment called?',
  'A sandbox environment',
  ['A production cluster node', 'A bridged VLAN trunk port', 'A domain controller FSMO role'],
  'A sandbox is a tightly isolated VM or container environment used to test untrusted code or software changes without '
  'risking the host or production LAN.'),
 ('A1X-241',
  'IT-6.3',
  'A1:4.1',
  'How do OS-level containers (such as Docker / containerd) differ from full virtual machines running on a hypervisor?',
  'Containers share the host kernel; VMs run a full guest OS',
  ['Each Docker container emulates a separate UEFI BIOS, virtual PCIe bus, and 60 GB guest kernel image',
   'Containers require a separate physical server per container and cannot share CPU cores',
   'Full virtual machines cannot be snapshotted, whereas containers require VT-x disabled'],
  'Because containers share the host OS kernel via namespaces and cgroups rather than booting a full guest OS per '
  'instance, they start in milliseconds with minimal overhead.'),
 ('A1X-242',
  'IT-6.1',
  'A1:4.1',
  'A hospital replaces 500 nurses’ station PCs with low-power thin clients that stream full Windows 11 desktops hosted '
  'centrally on data-center servers. Which architecture is this?',
  'VDI (Virtual Desktop Infrastructure)',
  ['BYOD local fat client', 'Edge peer-to-peer workgroup', 'Standalone air-gapped BIOS terminal'],
  'Virtual Desktop Infrastructure (VDI) runs user desktop VMs centrally on data-center hypervisors and streams '
  'display/input over RDP, Blast, or PCoIP to thin clients.'),
 ('A1X-243',
  'IT-6.1',
  'A1:4.1',
  'An engineering firm relies on a custom 32-bit calibration program written for Windows 7 that fails on 64-bit '
  'Windows 11. What is the safest way to keep running that legacy application on a modern Windows 11 workstation?',
  'Run the legacy OS and app in an isolated Virtual Machine',
  ['Overwrite the Windows 11 system32 folder with Windows 7 DLLs',
   'Disable UEFI Secure Boot and delete the NTFS partition table',
   'Overclock the CPU until 32-bit drivers execute in kernel ring 0'],
  'Virtualization encapsulates a legacy operating system and application inside a guest VM on modern hardware while '
  'isolating the outdated OS from internet exposure.'),
 ('A1X-244',
  'IT-6.3',
  'A1:4.1',
  'A VM on a workstation needs its own IPv4 address from the physical office DHCP server (`10.10.1.0/24`) so other LAN '
  'PCs can reach a service inside the VM directly. Which virtual switch mode should be configured on the VM’s vNIC?',
  'Bridged networking mode bound to the physical NIC',
  ['Host-only networking mode (isolated private switch between host and VMs only)',
   'NAT mode with no port forwarding rules configured',
   'Disconnected virtual cable state'],
  'In Bridged mode, the VM’s virtual NIC bridges directly onto the physical LAN with its own MAC address and requests '
  'its own DHCP lease from the LAN router.'),
 ('A1X-245',
  'IT-6.1',
  'A1:4.1',
  'Which security risk occurs when a vulnerability in a guest VM’s virtualized hardware driver allows an attacker '
  'inside the guest VM to break out and execute code on the underlying hypervisor?',
  'VM escape',
  ['VM sprawl', 'ARP cache poisoning', 'VLAN double-tagging'],
  'VM escape is a critical vulnerability where code inside a guest VM breaks out of the hypervisor isolation boundary '
  'to compromise the host or neighboring VMs.'),
 ('A1X-246',
  'IT-6.2',
  'A1:4.2',
  'A startup rents virtual machines, block disks, and a VPC subnet from a cloud provider while its own engineers '
  'install Ubuntu Linux, patch the kernel, and manage PostgreSQL. Which cloud service model is this?',
  'IaaS (Infrastructure as a Service)',
  ['SaaS (Software as a Service)', 'PaaS (Platform as a Service)', 'On-premises bare-metal colocation'],
  'In IaaS, the cloud provider manages the physical data center, storage, and hypervisor, while the customer manages '
  'the guest OS, database, runtime, and applications.'),
 ('A1X-247',
  'IT-6.2',
  'A1:4.2',
  'A software team pushes Node.js code directly to a managed cloud app runtime and connects it to a managed cloud SQL '
  'service without provisioning VMs or patching OS kernels. Which cloud service model is this?',
  'PaaS (Platform as a Service)',
  ['IaaS (Infrastructure as a Service)', 'SaaS (Software as a Service)', 'DaaS (Desktop as a Service)'],
  'In PaaS, the provider manages the underlying VMs, OS patching, and runtime environment so developers manage only '
  'their application code and data.'),
 ('A1X-248',
  'IT-6.2',
  'A1:4.2',
  'A retailer keeps its latency-sensitive POS database on private servers in its own data center, but bursts seasonal '
  'holiday web-storefront traffic into public cloud VMs over an encrypted link. Which cloud deployment model is this?',
  'Hybrid cloud deployment model',
  ['Public cloud only', 'Community cloud only', 'Air-gapped private cloud'],
  'A hybrid cloud combines private (on-premises or dedicated) infrastructure with public cloud services across an '
  'encrypted interconnect.'),
 ('A1X-249',
  'IT-6.2',
  'A1:4.2',
  'Twelve regional hospitals share a dedicated, HIPAA-compliant cloud infrastructure built specifically for their '
  'healthcare consortium while excluding the general public. Which cloud deployment model describes this?',
  'Community cloud',
  ['Public consumer cloud', 'Single-tenant personal NAS', 'Unmanaged peer-to-peer LAN'],
  'A community cloud is shared by several organizations that share common regulatory, security, or mission '
  'requirements.'),
 ('A1X-250',
  'IT-6.2',
  'A1:4.2',
  'During a product launch, a cloud web cluster automatically adds 30 instances as CPU crosses 70% and terminates them '
  'two hours later when traffic drops, billing only for those two hours. Which two cloud characteristics are '
  'demonstrated?',
  'Rapid elasticity and metered pay-as-you-go billing',
  ['Fixed capital expenditure (CapEx) over-provisioning and manual rack mounting',
   'Single-tenancy dedicated mainframes and unmetered flat-rate colocation',
   'Offline magnetic tape vaulting and manual BIOS overclocking'],
  'Rapid elasticity scales resources outward and inward on demand, and metered utilization bills strictly for the '
  'compute/storage/egress consumed.'),
 ('A1X-251',
  'IT-6.2',
  'A1:4.2',
  'In a public cloud environment, multiple unrelated corporate customers run workloads on the same physical host '
  'servers and storage arrays, separated logically by hypervisor isolation. What is this concept called?',
  'Multitenancy (shared hardware with logical isolation)',
  ['Dedicated single-tenant bare-metal hosting', 'Air-gapped physical separation', 'Localhost loopback multiplexing'],
  'Multitenancy shares underlying physical compute, network, and storage hardware across multiple customers while '
  'isolating each tenant’s data and VMs logically.'),
 ('A1X-252',
  'IT-6.2',
  'A1:4.2',
  'Users edit files in their local `OneDrive` or `Google Drive` folder while offline on a flight, and as soon as the '
  'laptop connects to hotel Wi-Fi, modified blocks upload and sync to their tablet and web portal. What cloud feature '
  'is this?',
  'Cloud file synchronization with offline caching',
  ['Block-level Fibre Channel SAN zoning', 'Stateless PXE network boot', 'Authoritative DNS zone transfer (AXFR)'],
  'Cloud file synchronization clients maintain a local cached folder and synchronize delta changes bidirectionally '
  'over HTTPS whenever connectivity is available.'),
 ('A1X-253',
  'IT-2.3',
  'A1:5.1',
  'An older office desktop PC loses its BIOS settings and resets the date to `01/01/2020 00:00` every time the AC '
  'power strip is switched off overnight, prompting `CMOS Checksum Error` on boot. What is the fix?',
  'Replace the CR2032 3V CMOS coin-cell battery',
  ['Reformat the NVMe boot drive and reinstall Windows 11',
   'Replace the 24-pin ATX power supply with a 1000 W unit',
   'Reflash the GPU vBIOS and replace the DisplayPort cable'],
  'When AC standby power (+5VSB) is removed, the motherboard relies on the CR2032 coin-cell battery to maintain the '
  'Real-Time Clock (RTC) and CMOS settings.'),
 ('A1X-254',
  'IT-3.3',
  'A1:5.1',
  'A workstation runs for 10 minutes, then the CPU fan hits maximum RPM, clock speeds drop from 5.0 GHz to 800 MHz, '
  'and the PC abruptly powers off during rendering. The technician finds the plastic protective film was left on the '
  'bottom of the new CPU heatsink. What caused the shutdown?',
  'CPU thermal throttling and emergency thermal shutdown',
  ['RAM single-bit parity error corrected by ECC modules',
   'CMOS battery depletion resetting the NTP time server',
   'Hard drive S.M.A.R.T. reallocated sector warning'],
  'Leaving the plastic peel film on the cooler cold plate insulates the CPU IHS, causing rapid overheating, thermal '
  'throttling, and an automatic thermal protection shutdown.'),
 ('A1X-255',
  'IT-2.3',
  'A1:5.1',
  'A technician presses the front-panel power button on a newly built PC and nothing happens—no fans spin and no '
  'motherboard LEDs light—even though the wall outlet has 120 V AC and the PSU rear switch is On. What should be '
  'checked first?',
  'Check the 24-pin ATX plug and 2-pin PWR_SW header lead',
  ['Boot into Windows Safe Mode and run `sfc /scannow`',
   'Update the graphics card driver in Device Manager',
   'Change the boot order in UEFI from SATA to NVMe'],
  'Complete lack of power response when pressing the front button is most commonly an unseated 24-pin ATX cable or the '
  '`PWR_SW` front-panel switch lead connected to the wrong header pins.'),
 ('A1X-256',
  'IT-3.3',
  'A1:5.1',
  'A 7-year-old desktop PC randomly freezes under load, and visual inspection around the CPU socket reveals '
  'cylindrical components with bulging, domed tops and brown crust leaking from their vents. What failed?',
  'Bulging/leaking electrolytic capacitors on the VRM',
  ['Blown glass tube fuses inside the M.2 NVMe SSD',
   'Melted optical fibers inside the SATA data cable',
   'Shattered quartz crystals inside the CPU die'],
  'Electrolytic capacitors filter voltage ripples in the CPU voltage regulator module (VRM); when they bulge or leak '
  'electrolyte, voltage stability collapses.'),
 ('A1X-257',
  'IT-2.3',
  'A1:5.1',
  'After adding two new RAM sticks, a desktop PC experiences random Blue Screen crashes (`MEMORY_MANAGEMENT` and '
  '`IRQL_NOT_LESS_OR_EQUAL`). Which bootable diagnostic tool tests physical RAM addresses outside the OS?',
  'MemTest86+ / Windows Memory Diagnostic',
  ['CrystalDiskInfo S.M.A.R.T. utility', 'Wireshark packet analyzer', 'Display Driver Uninstaller (DDU)'],
  'Memory diagnostic utilities (`mdsched.exe` or MemTest86+) write and read walking-bit patterns across physical RAM '
  'rows/columns to isolate defective DIMMs.'),
 ('A1X-258',
  'IT-3.3',
  'A1:5.1',
  'A user reports an acrid electrical burning smell coming from the rear of a desktop PC immediately before it clicked '
  'off and refused to power back on. What is the safest action?',
  'Unplug AC cord immediately and replace the sealed PSU',
  ['Bypass the PSU protection with a paperclip on the green PS_ON wire and keep running',
   'Open the PSU metal casing with a screwdriver to solder the primary 400 V capacitor',
   'Spray water into the rear PSU exhaust fan grille to cool the transformer'],
  'Power supplies contain high-voltage primary capacitors that hold hazardous charge even after unplugging; a failed '
  'PSU must be replaced as a sealed unit.'),
 ('A1X-259',
  'IT-2.3',
  'A1:5.1',
  'A PC powers on, case fans spin, the motherboard DRAM diagnostic LED stays solid amber (with repeating long beeps), '
  'and no video reaches the monitor. Which step isolates the fault fastest?',
  'Reseat RAM and test one DIMM at a time in slot A2',
  ['Reformat the hard drive from a Linux live USB stick',
   'Replace the monitor HDMI cable with a VGA adapter',
   'Resolder the CPU socket pins with a heat gun'],
  'A solid DRAM POST LED or memory beep code indicates failed memory training; reseating DIMMs and testing one stick '
  'at a time in the primary slot isolates a loose or dead module.'),
 ('A1X-260',
  'IT-3.3',
  'A1:5.1',
  'A designer installs a 320 W discrete GPU into an office PC that has a 300 W PSU. The PC boots to the Windows '
  'desktop fine, but the instant a 3D render starts, the PC clicks off abruptly. Why?',
  'The 3D load trips the 300 W PSU over-power protection',
  ['The monitor refresh rate is set to 60 Hz instead of 144 Hz',
   'Windows 11 Home does not support discrete PCIe graphics cards',
   'The CMOS battery only supplies power during 2D desktop work'],
  'At idle a GPU draws only ~20 W, allowing the PC to boot; when a 3D workload starts, the GPU spikes to 300+ W, '
  'tripping the undersized PSU’s protection shutdown.'),
 ('A1X-261',
  'IT-3.1',
  'A1:5.2',
  'A user reports that their 3.5-inch mechanical hard drive is making rhythmic metallic clicking sounds and files take '
  '30 seconds to open. What is the first priority action?',
  'Back up or image critical user data onto a healthy drive first',
  ['Run a 5-pass zero-fill surface wipe to quiet the actuator arm',
   'Open the sealed HDD cover plate at the desk to realign the heads by hand',
   'Run Disk Defragmenter 10 times in a row to move files away from the clicking head'],
  'Rhythmic clicking indicates mechanical head/media failure; every additional spin-up or heavy defrag pass risks '
  'total platter failure, so rescuing data comes first.'),
 ('A1X-262',
  'IT-3.2',
  'A1:5.2',
  'A workstation displays `S.M.A.R.T. Status BAD, Backup and Replace — Press F1 to Resume` during POST, even though '
  'Windows still boots. What does this warning mean?',
  'Internal drive S.M.A.R.T. telemetry predicts imminent failure',
  ['The drive has a virus in the Master Boot Record that `ipconfig /flushdns` can remove',
   'The SATA data cable is plugged into Port 2 instead of Port 1 on the motherboard',
   'The Windows Recycle Bin contains more than 10 GB of deleted files'],
  'S.M.A.R.T. tracks internal drive health metrics and alerts the user before catastrophic failure so data can be '
  'backed up and the disk replaced.'),
 ('A1X-263',
  'IT-3.1',
  'A1:5.2',
  'A technician installs a brand-new secondary 2 TB M.2 NVMe SSD into a Windows 11 PC. The drive appears in UEFI setup '
  'and Device Manager, but does NOT appear with a drive letter in File Explorer. Why?',
  'Initialize (GPT), partition, and format it in Disk Management',
  ['The NVMe drive is defective and must be returned under RMA',
   'Windows 11 only supports one storage drive per motherboard',
   'The user must enable RAID 5 in the printer spooler service'],
  'Raw factory drives have no partition table or filesystem; opening `diskmgmt.msc` to initialize as GPT, create a '
  'volume, format as NTFS, and assign a drive letter makes it visible.'),
 ('A1X-264',
  'IT-3.2',
  'A1:5.2',
  'After a technician hot-swaps a replacement SAS drive (pulled from an old lab server) into a degraded RAID 10 array, '
  'the controller reports `Foreign Configuration Detected` instead of rebuilding. What should the technician do?',
  'Clear the foreign config on the spare so it rebuilds cleanly',
  ['Import the foreign configuration from the old disk to overwrite the live production array',
   'Format the entire RAID 10 virtual disk from the UEFI setup menu',
   'Unplug all surviving drives while the server is running'],
  'A reused disk carrying old RAID metadata is flagged as `Foreign`; clearing the foreign metadata on the replacement '
  'disk allows the controller to rebuild onto it cleanly.'),
 ('A1X-265',
  'IT-3.1',
  'A1:5.2',
  'A user leaves a non-bootable USB thumb drive plugged into a PC overnight, and the next morning the PC stops on a '
  'black screen saying `No bootable device found`. What happened?',
  'USB removable media is ahead of the SSD in UEFI boot order',
  ['The USB thumb drive erased the internal NVMe SSD firmware over the PCIe bus',
   'The power supply +3.3 V rail failed when the USB drive entered sleep mode',
   'The monitor DisplayPort cable became unplugged from the graphics card'],
  'When removable USB media precedes the internal OS drive in the boot order, the firmware attempts to boot from the '
  'non-bootable thumb drive.'),
 ('A1X-266',
  'IT-3.2',
  'A1:5.2',
  'Why does an SSD that is 99% full with TRIM disabled experience severe write latency spikes and low IOPS whenever '
  'saving large files?',
  'Without free TRIM blocks, writes trigger slow read-erase-modify cycles',
  ['The SSD spindle motor slows down from 7,200 RPM to 5,400 RPM when capacity exceeds 90%',
   'NAND flash cells switch from PCIe x4 to USB 1.1 mode when free space drops below 5%',
   'The SATA cable develops high electrical resistance when carrying large files'],
  'SSD flash writes in pages (4–16 KB) but can only erase entire blocks (megabytes); freeing space and enabling TRIM '
  'allows background garbage collection to pre-erase blocks.'),
 ('A1X-267',
  'IT-3.2',
  'A1:5.2',
  'In a 3-drive RAID 5 array, Drive 1 fails on Friday night (Degraded), and before Drive 1 is replaced, Drive 2 fails '
  'on Saturday morning (Offline). How can the company recover its data?',
  'Replace both failed drives, recreate RAID 5, and restore backup',
  ['Hot-swap Drive 1 only and let Drive 3 rebuild both missing drives from single parity',
   'Run `chkdsk /r` on the offline RAID controller BIOS screen',
   'Swap the SATA cables between Drive 1 and Drive 2 to invert the parity XOR math'],
  'Single-parity RAID 5 can reconstruct at most one missing disk ($N-1$); losing two disks simultaneously exceeds '
  'fault tolerance and requires restoring from backup.'),
 ('A1X-268',
  'IT-3.4',
  'A1:5.3',
  'A ceiling projector powers on, the cooling fans run for 90 seconds, and then the `TEMP` warning LED flashes red and '
  'the projector shuts off its lamp automatically. What is the most likely cause?',
  'Clogged dust filter or failed fan tripping the thermal cutoff',
  ['An incorrect HDMI input source selected on the remote control',
   'A wrong screen resolution set on the presenter’s laptop',
   'A dead CMOS battery on the room’s Wi-Fi access point'],
  'Projector lamps generate intense heat; if the intake air filter is clogged with dust or a cooling fan fails, the '
  'thermal cutoff shuts down the unit.'),
 ('A1X-269',
  'IT-3.4',
  'A1:5.3',
  'A lobby information monitor has displayed the same static company logo and stock ticker banner 24/7 for two years, '
  'and now a permanent ghostly outline of the banner remains visible even when playing full-screen video. What is this '
  'defect called?',
  'Display burn-in (permanent sub-pixel image retention)',
  ['Chromatic aberration of the HDMI cable',
   'Loose VGA thumbscrews missing the red channel',
   'GPU artifacting from an unstable VRAM overclock'],
  'Static high-contrast UI elements displayed continuously cause uneven aging of OLED organic sub-pixels (or '
  'persistent LCD image retention), known as burn-in.'),
 ('A1X-270',
  'IT-3.4',
  'A1:5.3',
  'A monitor connected via a legacy 15-pin analog VGA cable displays the entire Windows desktop with a heavy '
  'magenta/purple tint (missing all green color). What is the most likely cause?',
  'Bent or loose Green video pin on the analog VGA plug',
  ['The monitor refresh rate is set to 75 Hz instead of 60 Hz',
   'The Windows Night Light blue-light filter is enabled',
   'The DisplayPort Multi-Stream Transport (MST) hub is full'],
  'Analog VGA carries Red, Green, and Blue on separate physical pins; if the Green pin is bent or loose at the '
  'connector, only Red + Blue reach the monitor, producing a magenta cast.'),
 ('A1X-271',
  'IT-3.4',
  'A1:5.3',
  'A user connects a 27-inch 2560×1440 (QHD) LCD monitor to a laptop, but text looks blurry, stretched, and fuzzy '
  'across the entire screen. Checking Windows Display Settings shows the resolution is set to `1280×720`. What fixes '
  'the blurry text?',
  'Set Windows display resolution to native 2560×1440',
  ['Degauss the LCD panel using an external electromagnetic coil',
   'Replace the LCD backlight inverter board',
   'Lower the refresh rate from 60 Hz to 24 Hz interlaced'],
  'LCD/OLED panels have a fixed physical grid of pixels; running any non-native resolution forces interpolation across '
  'fractional pixels, making text appear blurry.'),
 ('A1X-272',
  'IT-3.4',
  'A1:5.3',
  'A user connects a laptop to a conference room TV with an HDMI cable. The video picture on the TV is sharp, but '
  'sound still plays out of the tiny laptop speakers instead of the TV soundbar. What should the technician check '
  'first?',
  'Select the HDMI/TV device as default Sound Output',
  ['Replace the HDMI cable with a 15-pin analog VGA cable',
   'Update the laptop’s SATA AHCI storage controller driver',
   'Enable Sticky Keys in Windows Accessibility settings'],
  'HDMI carries both digital video and multi-channel digital audio, but if the OS audio output device remains set to '
  'Internal Speakers, audio will not route over the HDMI sink.'),
 ('A1X-273',
  'IT-3.4',
  'A1:5.3',
  'On a brand-new LCD monitor, a single tiny dot near the corner stays permanently bright red on a black background, '
  'while another dot near the center stays permanently black on a white background. How are these two pixel defects '
  'classified?',
  'Red dot = stuck sub-pixel; black dot = dead pixel',
  ['Both dots are caused by a corrupt DNS resolver cache on the PC',
   'The red dot is a burnt-out projector bulb and the black dot is display burn-in',
   'Both dots indicate the monitor is set to the wrong HDMI input source'],
  'A stuck pixel/sub-pixel has a transistor locked in the on state (glowing red, green, blue, or white), whereas a '
  'dead pixel receives no power and remains permanently black.'),
 ('A1X-274',
  'IT-3.4',
  'A1:5.3',
  'A dual-monitor workstation works on Monitor 1, but Monitor 2 says `No Signal — Going to Sleep` even though its '
  'power LED is amber, the DisplayPort cable is plugged into the GPU, and Windows detects only one display. The user '
  'mentions they cleaned behind the desk this morning. What should the technician check on Monitor 2’s OSD menu and '
  'cabling?',
  'Set Monitor 2 input source to DisplayPort and reseat the cable',
  ['Reinstall Windows 11 from a bootable USB flash drive',
   'Replace the workstation CPU and apply fresh thermal paste',
   'Enable Airplane Mode in Windows Network settings'],
  'When a powered monitor reports `No Signal` after desk cleaning, either the cable was bumped loose or the monitor’s '
  'On-Screen Display (OSD) input source button was switched to an unused port.'),
 ('A1X-275',
  'IT-4.1',
  'A1:5.4',
  'A user’s smartphone charges intermittently only when the USB-C cable is held at a sharp upward angle, and the plug '
  'does not click all the way into the bottom port even with a brand-new charger and cable. What is the most common '
  'non-destructive cause to inspect first?',
  'Compacted lint in the USB-C port stopping the plug from seating',
  ['A corrupted eSIM carrier profile requiring an MDM factory wipe',
   'An outdated Bluetooth 5.3 firmware driver in the OS',
   'Too many browser tabs open in mobile Safari/Chrome'],
  'Compacted lint at the base of a USB-C or Lightning port stops the connector from latching and making solid pin '
  'contact; removing it with a non-conductive pick often restores charging without board repair.'),
 ('A1X-276',
  'IT-4.1',
  'A1:5.4',
  'A field technician drops a smartphone into a puddle of water. The phone is retrieved within 5 seconds. What is the '
  'correct immediate response to minimize corrosion and short-circuit damage?',
  'Power off immediately, unplug cables, dry, and do not charge',
  ['Plug the wet phone into a 65 W USB-PD fast charger immediately to see if the battery still charges',
   'Bake the smartphone in a kitchen oven at 180 °C (350 °F) for 20 minutes',
   'Submerge the phone in salt water to neutralize the puddle minerals'],
  'Applying electrical current while moisture bridges PCB pads causes rapid galvanic corrosion and short circuits; '
  'powering off immediately and avoiding charging is critical.'),
 ('A1X-277',
  'IT-4.1',
  'A1:5.4',
  'A tablet screen registers phantom taps and erratic "ghost touches" in the upper-right corner even when no one is '
  'touching the glass, after a cheap third-party ungrounded charger was plugged in and the screen protector cracked. '
  'What steps isolate and fix the issue?',
  'Unplug noisy charger, remove cracked protector, or replace digitizer',
  ['Turn off Wi-Fi and Bluetooth permanently and set the DNS server to 8.8.8.8',
   'Replace the rear camera lens cover and recalibrate the barometer',
   'Delete all user contacts and calendar appointments from iCloud'],
  'Capacitive digitizers rely on a uniform electrostatic field; unshielded third-party chargers inject common-mode '
  'noise onto the touch grid, and cracked digitizer glass causes permanent ghost inputs.'),
 ('A1X-278',
  'IT-4.1',
  'A1:5.4',
  'A user complains that their smartphone screen no longer rotates from portrait to landscape when turning the phone '
  'sideways to watch a video, even though the Orientation Lock icon in the control center is turned OFF. Which '
  'internal MEMS sensor (or app state) is responsible for detecting device tilt?',
  'Internal 3-axis accelerometer / gyroscope MEMS sensor',
  ['The NFC 13.56 MHz inductive payment coil',
   'The ultrasonic fingerprint reader under the glass',
   'The LiDAR time-of-flight rear camera autofocus laser'],
  'Screen auto-rotation relies on the internal MEMS accelerometer (and gyroscope) to detect gravity vector '
  'orientation.'),
 ('A1X-279',
  'IT-4.1',
  'A1:5.4',
  'An employee’s Android phone battery drains from 100% to 15% in three hours while sitting idle in a pocket, and the '
  'back of the phone feels noticeably warm (`43 °C`). What should the technician check first in Settings before '
  'replacing the battery?',
  'Check Battery Usage by app for a runaway background task',
  ['Puncture the rear housing to vent heat from the processor',
   'Disable the SIM PIN and turn off device encryption',
   'Format the corporate network’s DHCP server scope'],
  'Rapid battery drain paired with a warm chassis is frequently caused by a hung background app holding a CPU/GPS wake '
  'lock or the cellular modem transmitting at maximum power in a low-signal zone.'),
 ('A1X-280',
  'IT-4.1',
  'A1:5.4',
  'A user tries to install a required 1.8 GB corporate inspection app from the Managed Play Store / App Store, but the '
  'download fails repeatedly even on fast office Wi-Fi. Checking Device Storage shows `63.6 GB used of 64.0 GB`. What '
  'is the cause?',
  'Insufficient free flash storage to download and unpack the app',
  ['The office Wi-Fi router is using WPA3 instead of WPA2',
   'The phone’s Bluetooth radio is paired to a wireless headset',
   'The user’s Active Directory password is more than 14 characters long'],
  'Mobile operating systems require free storage well above the compressed download size to unpack the installer '
  'archive and maintain OS cache headroom.'),
 ('A1X-281',
  'IT-4.1',
  'A1:5.4',
  'An active Bluetooth stylus stops drawing on a tablet even though finger touch works across the entire screen. What '
  'should the technician check first?',
  'Recharge the active stylus battery and check Bluetooth pairing',
  ['Replace the tablet’s IPS LCD panel and backlight assembly',
   'Reset the office wireless LAN controller (WLC)',
   'Install a PostScript printer driver on the tablet'],
  'When capacitive finger touch works normally but an active stylus does not respond, the stylus battery is depleted '
  'or its Bluetooth/digitizer pairing was lost.'),
 ('A1X-282',
  'IT-5.3',
  'A1:5.5',
  'Users on a VoIP call report that words sound robotic, clipped, and out of order whenever a backup job saturates the '
  'branch WAN link, even though average bandwidth is 100 Mb/s. Which two network metrics degrade real-time voice '
  'packets during congestion, and what switch/router feature prioritizes voice?',
  'High latency and jitter; fix with QoS (DSCP EF / Voice VLAN)',
  ['High DHCP lease time and large DNS TTLs; mitigated by disabling Spanning Tree Protocol',
   'Low MAC address table aging and T568B pinouts; mitigated by switching from UDP to TCP port 21',
   'Excessive PoE wattage budget and Cat 6A shielding; mitigated by enabling APIPA'],
  'Real-time RTP audio is sensitive to one-way latency (<150 ms), jitter (<30 ms variation), and packet loss (<1%); '
  'QoS queues voice traffic (DSCP 46 EF / 802.1p CoS 5) ahead of bulk backups.'),
 ('A1X-283',
  'IT-5.3',
  'A1:5.5',
  'A switch log shows `Gi0/14 changed state to down` followed 3 seconds later by `Gi0/14 changed state to up` over and '
  'over 40 times in ten minutes. What is this symptom called, and what are its common physical causes?',
  'Port flapping from a bad patch cord, loose jack, EMI, or bad SFP',
  ['VLAN hopping — caused by an attacker sending double-tagged 802.1Q frames',
   'DNS cache poisoning — caused by an expired SOA serial number',
   'Split-horizon routing — caused by RIPv2 advertisement suppression'],
  'Rapidly alternating link-up / link-down transitions on a switchport is called port flapping and usually points to '
  'Layer 1 physical instability or speed/duplex auto-negotiation failure.'),
 ('A1X-284',
  'IT-7.2',
  'A1:5.5',
  'Employees in the breakroom report that 2.4 GHz Wi-Fi disconnects every day at 12:15 PM for two minutes whenever '
  'someone heats lunch, while laptops connected on 5 GHz Wi-Fi stay connected without a hitch. Why?',
  'Leaky microwave oven RF interference near 2.45 GHz',
  ['Microwave ovens consume all available DHCP leases from the router scope',
   'The 5 GHz band travels through metal microwave doors to boost signal strength',
   'Heating food triggers Dynamic Frequency Selection (DFS) radar avoidance on 2.4 GHz'],
  'Magnetrons in microwave ovens operate at ~2.45 GHz; leaky door seals flood the 2.4 GHz ISM band (especially '
  'channels 6–11) with high-amplitude RF noise while leaving 5 GHz and 6 GHz unaffected.'),
 ('A1X-285',
  'IT-5.3',
  'A1:5.5',
  'A workstation on a Gigabit switch transfers files from the local NAS at only 9–11 MB/s (~90 Mb/s) and experiences '
  'thousands of late collisions and CRC errors. Inspecting `show interfaces gi0/8` shows the switchport is hard-coded '
  'to `100 Mbps / Full-duplex` while the PC NIC is set to `Auto-negotiate`. Why are CRC/collision errors occurring?',
  'Duplex mismatch (100/Full hard-coded vs 100/Half fallback)',
  ['Both ends automatically negotiate 10 Gb/s Full-duplex over Cat 3 cable',
   'The switchport disables Ethernet and switches to Token Ring arbitration',
   'The PC NIC changes its IPv4 subnet mask from /24 to /30'],
  'Per IEEE 802.3u/ab, if one link partner disables auto-negotiation (hard-coded 100/Full), the auto-negotiating '
  'partner detects 100BASE-TX parallel carrier without negotiation pulses and defaults to Half-duplex, causing late '
  'collisions and FCS/CRC errors. Setting both sides to Auto fixes it.'),
 ('A1X-286',
  'IT-5.3',
  'A1:5.5',
  'A user can `ping 8.8.8.8` with 14 ms response times, but typing `https://www.comptia.org` in a browser fails with '
  '`DNS_PROBE_FINISHED_NXDOMAIN / Server Not Found`. What does this isolate?',
  'IP routing works; DNS name resolution is failing',
  ['The physical Ethernet patch cable is unplugged from the wall jack',
   'The default gateway router interface is administratively shut down',
   'The workstation NIC has a 169.254.x.x APIPA address'],
  'A successful ping to an external public IP (`8.8.8.8`) proves Layer 1–3 LAN and WAN routing work; failure to open '
  'websites by hostname isolates the problem to DNS resolution.'),
 ('A1X-287',
  'IT-13.2',
  'A1:5.5',
  'A newly joined laptop fails to connect to the `Corp-Secure` 802.1X (WPA3-Enterprise) Wi-Fi network with '
  '`Authentication Failed`, while neighboring laptops connect normally. What should the technician verify on the new '
  'laptop?',
  'Verify the 802.1X client/CA certificates, credentials, and clock',
  ['Verify the user typed the 10-digit hexadecimal WEP key into the SSID name field',
   'Disable the laptop’s wireless NIC in UEFI and plug into an RJ11 phone jack',
   'Enable WPS (Wi-Fi Protected Setup) push-button mode on the enterprise WLC'],
  'WPA2/WPA3-Enterprise (802.1X/EAP-TLS or PEAP) authenticates via a RADIUS server and requires valid '
  'credentials/certificates and a trusted root CA.'),
 ('A1X-288',
  'IT-5.3',
  'A1:5.5',
  'Two desktop PCs on the same subnet (`10.1.1.50`) display a pop-up warning of an `IP address conflict detected` and '
  'intermittently lose network sessions as switches update their ARP/MAC tables. How is this caused and resolved?',
  'Duplicate IP conflict; move to DHCP or exclude static IPs',
  ['Both PCs are using the same DNS server IP (`10.1.1.10`) in their TCP/IP settings',
   'Both PCs are connected to the same VLAN ID on the access switch',
   'Both PCs have IPv6 enabled alongside IPv4 dual-stack'],
  'Every host on a subnet shares the same gateway and DNS server IP, but each host must have a unique IP address; '
  'duplicate IPs cause gratuitous ARP battles and dropped TCP sessions.'),
 ('A1X-289',
  'IT-4.3',
  'A1:5.6',
  'Every page printed or copied using the top Automatic Document Feeder (ADF) on an office MFD has a crisp, straight '
  'vertical black line running from the very top edge to the very bottom edge of the page, whereas pages copied from '
  'the flatbed glass or printed from a PC have no line at all. What is the cause?',
  'Debris stuck on the narrow ADF slit-scan glass strip',
  ['A deep scratch around the circumference of the photosensitive imaging drum',
   'A worn pickup roller in Paper Tray 2',
   'A corrupted PCL6 print driver on the print server'],
  'During ADF scanning, the CCD/CIS sensor stays stationary beneath a narrow slit glass while rollers move the paper '
  'past it; a single stationary speck on that slit glass gets scanned continuously as a vertical line down the entire '
  'page.'),
 ('A1X-290',
  'IT-4.3',
  'A1:5.6',
  'A laser printer begins outputting dozens of pages filled with random ASCII symbols, hearts, and wingdings '
  '(`%!PS-Adobe-3.0 ...`) instead of a 2-page PDF report. What caused the garbled output?',
  'Corrupted or mismatched print driver (PS vs PCL)',
  ['A depleted black toner cartridge in the imaging unit',
   'A worn rubber separation pad in the paper tray',
   'A dirty primary corona wire inside the toner cartridge'],
  'When a workstation sends PostScript commands to a printer expecting PCL (or raw binary to a wrong driver), the '
  'printer interprets the control stream as literal printable characters across dozens of pages.'),
 ('A1X-291',
  'IT-4.3',
  'A1:5.6',
  'A laser printer clicks its solenoid three times when a job is sent, the paper in Tray 2 barely twitches forward by '
  '2 mm, and the control panel displays `Paper Jam in Tray 2 — Load Paper`, even though the tray is half full and no '
  'torn paper is inside the path. What component needs service?',
  'Worn or dusty rubber paper pickup rollers in Tray 2',
  ['A burned-out fuser halogen heating lamp at the rear exit',
   'A full waste-toner collection bottle',
   'An IP address conflict on the printer’s Ethernet port'],
  'As rubber pickup rollers age and accumulate paper dust, they lose friction and slip against the top sheet; if the '
  'paper fails to reach the registration sensor in time, the printer reports a false Tray 2 jam.'),
 ('A1X-292',
  'IT-4.3',
  'A1:5.6',
  'Conversely, when a laser printer pulls three or four sheets of paper glued together out of Tray 2 at the same time '
  'on every print job—causing accordion jams inside the paper path—which part in the tray feed assembly is worn out '
  '(besides fanning the paper stack)?',
  'Worn separation pad failing to hold back lower sheets',
  ['The laser scanner mirror motor', 'The high-voltage transfer corona wire', 'The duplexer exit diverter gate'],
  'The pickup roller advances the top sheet while the high-friction separation pad holds back the second sheet; a worn '
  'separation pad lets multiple sheets feed simultaneously (multipage misfeed).'),
 ('A1X-293',
  'IT-4.3',
  'A1:5.6',
  'Eight users send documents to a shared Windows print queue, and all eight jobs sit in the queue with the first job '
  'stuck at `Printing - Deleting` for an hour even after the physical printer is rebooted. Which Windows service on '
  'the print server/PC must be stopped, its `C:\\Windows\\System32\\spool\\PRINTERS` folder cleared, and restarted?',
  'Print Spooler (`Spooler` service and `spool\\PRINTERS` folder)',
  ['Server (`LanmanServer` service)',
   'Background Intelligent Transfer Service (`BITS`)',
   'Windows Search Indexing (`WSearch` service)'],
  'A corrupt `.SPL`/`.SHD` spool file in `C:\\Windows\\System32\\spool\\PRINTERS` freezes the Print Spooler queue; '
  'stopping `Spooler`, deleting the stuck spool files, and starting `Spooler` clears the jam.'),
 ('A1X-294',
  'IT-4.3',
  'A1:5.6',
  'Pages from a monochrome laser printer become progressively fainter down the right side of the page, even after '
  'installing a brand-new OEM toner cartridge and shaking it gently. If toner is full, which high-voltage component '
  'inside the printer chassis is failing to pull toner evenly from the drum onto the paper?',
  'Failing high-voltage transfer roller in the printer',
  ['The ADF document feeder glass', 'The RJ45 Ethernet network interface card', 'The paper output bin full sensor'],
  'If a known-good toner/drum cartridge still produces faded print, the high-voltage transfer roller (or HVPS) is '
  'failing to apply sufficient positive charge beneath the paper to pull toner off the drum.'),
 ('A1X-295',
  'IT-4.3',
  'A1:5.6',
  'Every printed page from a laser printer shows tiny random gray dots and toner speckles scattered across the white '
  'background. Which two components are the primary suspects?',
  'Damaged OPC drum or worn drum cleaning blade',
  ['A misconfigured default gateway or wrong DNS server on the printer NIC',
   'Landscape page orientation or long-edge duplexing selected in the driver',
   'A disconnected stapler finisher cable or empty hole-punch bin'],
  'Speckling across the page background happens when the drum cleaning blade fails to wipe leftover toner off the OPC '
  'drum during step 7 (Cleaning) or when stray toner leaks from a damaged cartridge seal.')]


def items():
    return [_s(i, *row) for i, row in enumerate(RAW_A1)]


ITEMS = items()
