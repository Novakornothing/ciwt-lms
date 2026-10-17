"""Published certification exam objectives used for the alignment map (content pass 11).

Source documents (downloaded 17 Oct 2026 from the links on comptia.org; the files are CompTIA's and are not
redistributed here, only their objective numbers, objective titles and domain weights are recorded so the
mapping can be checked):

* A+ Core 1 220-1201 (V15), Exam Objectives Document Version 4.0 — linked from
  https://www.comptia.org/en-us/certifications/a/core-1-v15/ ("A+ Core 1 exam (V15)").
* A+ Core 2 220-1202 (V15), Exam Objectives Document Version 4.0 — linked from
  https://www.comptia.org/en-us/certifications/a/core-2-v15/.
* Network+ N10-009 (V9), Exam Objectives Document Version 6.0 — on CompTIA's asset host (the same host the
  A+ pages link to); the comptia.org Network+ page lists exam series code N10-009.

The curriculum is *aligned to* these objectives. It is not CompTIA courseware, CompTIA has not reviewed or
endorsed it, and none of its items are CompTIA exam items. CompTIA does not publish weights below the domain
level, so any per-objective weight used here is the domain weight divided equally across the domain's
objectives — an assumption, labelled as such wherever it is shown.

``topics`` are this project's own short checklists of the technical terms each objective's bullet list
names. They drive an automatic, keyword-based coverage estimate (curriculum_v2/cert/mapping.py) and are
search aids, not a copy of the objectives document. Format: ``'Label'`` (searched as a whole word) or
``'Label=regex'`` (case-insensitive regex over lesson, lab and item plain text).
"""

DISCLAIMER = ('Aligned to the published CompTIA exam objectives listed below. Not affiliated with, reviewed or '
              'endorsed by CompTIA; no CompTIA exam items are used. CompTIA, A+ and Network+ are trademarks of CompTIA, Inc.')

EXAMS = {
    'A1': {
        'code': '220-1201', 'name': 'CompTIA A+ Core 1', 'short': 'A+ Core 1', 'version': 'V15',
        'doc_version': 'Exam Objectives Document Version 4.0',
        'url': 'https://lecbyo.files.cmp.optimizely.com/download/34be017cb73211ef8985a6f347fbf652',
        'page': 'https://www.comptia.org/en-us/certifications/a/core-1-v15/',
        'sha256': '9fb3471b397a863b1baa33912dffb6fa232b4631e2219f39188c5c109814648c',
        'official': {'questions': 'Maximum of 90', 'minutes': 90, 'passing': '675 (on a scale of 100–900)'},
        'course': 'ITSUP',
    },
    'A2': {
        'code': '220-1202', 'name': 'CompTIA A+ Core 2', 'short': 'A+ Core 2', 'version': 'V15',
        'doc_version': 'Exam Objectives Document Version 4.0',
        'url': 'https://lecbyo.files.cmp.optimizely.com/download/cefedfb2b8a511ef809306d06d323538',
        'page': 'https://www.comptia.org/en-us/certifications/a/core-2-v15/',
        'sha256': '1bc5195327296edd92948b5f3a950fee35ac6807cec9b244b0b2e54e72d11bd2',
        'official': {'questions': 'Maximum of 90', 'minutes': 90, 'passing': '700 (on a scale of 100–900)'},
        'course': 'ITSUP',
    },
    'N': {
        'code': 'N10-009', 'name': 'CompTIA Network+', 'short': 'Network+', 'version': 'V9',
        'doc_version': 'Exam Objectives Document Version 6.0',
        'url': 'https://lecbyo.files.cmp.optimizely.com/download/35a7403ab73211ef9dcda6f347fbf652',
        'page': 'https://www.comptia.org/en-us/certifications/network/',
        'sha256': 'cb0ca59be880c5ad9ee6905373f39443d040177968d5e36c93922c8622608c52',
        'official': {'questions': 'Maximum of 90', 'minutes': 90, 'passing': 'not stated in the objectives document'},
        'course': 'NETOPS',
    },
}

DOMAINS = {
    'A1': [('1.0', 'Mobile Devices', 13), ('2.0', 'Networking', 23), ('3.0', 'Hardware', 25),
           ('4.0', 'Virtualization and Cloud Computing', 11), ('5.0', 'Hardware and Network Troubleshooting', 28)],
    'A2': [('1.0', 'Operating Systems', 28), ('2.0', 'Security', 28), ('3.0', 'Software Troubleshooting', 23),
           ('4.0', 'Operational Procedures', 21)],
    'N': [('1.0', 'Networking Concepts', 23), ('2.0', 'Network Implementation', 20), ('3.0', 'Network Operations', 19),
          ('4.0', 'Network Security', 14), ('5.0', 'Network Troubleshooting', 24)],
}

# (objective id, objective title as published, topics)
_A1 = [
    ('1.1', 'Given a scenario, monitor mobile device hardware and use appropriate replacement techniques.', [
        'Battery', 'Keyboard', 'RAM=\\bram\\b|so-?dimm|soldered', 'HDD/SSD=\\bssd\\b|\\bhdd\\b', 'Wireless card=wi-?fi card|wireless card|m\\.2 2230',
        'Biometrics=biometric|fingerprint (reader|sensor)', 'Near-field scanner=\\bnfc\\b|near-field', 'Wi-Fi antenna=antenna',
        'Camera/webcam=webcam|camera', 'Microphone']),
    ('1.2', 'Compare and contrast accessories and connectivity options for mobile devices.', [
        'USB-C/micro/mini USB=usb-c|micro-?usb|mini-?usb', 'Lightning=\\blightning\\b', 'NFC=\\bnfc\\b|near-field',
        'Bluetooth', 'Tethering/hotspot=tether|hotspot', 'Stylus', 'Headsets=headset', 'Speakers=speaker', 'Webcam',
        'Docking station=docking station|\\bdock\\b', 'Port replicator', 'Trackpad/drawing pad=trackpad|touchpad|drawing pad|track ?point']),
    ('1.3', 'Given a scenario, configure basic mobile device network connectivity and provide application support.', [
        'Cellular 3G/4G/5G=\\b(3g|4g|5g|lte)\\b|cellular', 'Hotspot', 'SIM/eSIM=\\besim\\b|\\bsim\\b', 'Bluetooth pairing=\\bpair(ing|ed)?\\b',
        'Location services/GPS=\\bgps\\b|location services', 'MDM=\\bmdm\\b|mobile device management', 'BYOD=\\bbyod\\b|bring your own device',
        'Policy enforcement=compliance policy|policy enforcement', 'Corporate applications=corporate app|managed app|work app',
        'Synchronization=synchroni[sz]|\\bsyncs?\\b', 'Data caps=data cap|data limit|metered', 'Mail/calendar/contacts=calendar|contacts']),
    ('2.1', 'Compare and contrast Transmission Control Protocol (TCP) and User Datagram Protocol (UDP) ports, protocols, and their purposes.', [
        'FTP 20-21=\\bftp\\b', 'SSH 22=\\bssh\\b', 'Telnet 23=telnet', 'SMTP 25=\\bsmtp\\b', 'DNS 53=\\b53\\b', 'DHCP 67/68=\\b67\\b',
        'HTTP 80=\\bhttp\\b', 'POP3 110=pop3', 'IMAP 143=\\bimap', 'NetBIOS 137-139=netbios', 'LDAP 389=\\bldap\\b', 'HTTPS 443=\\b443\\b',
        'SMB/CIFS 445=\\b445\\b', 'RDP 3389=3389', 'TCP vs. UDP=\\budp\\b']),
    ('2.2', 'Explain wireless networking technologies.', [
        '2.4GHz=2\\.4 ?ghz', '5GHz=\\b5 ?ghz', '6GHz=\\b6 ?ghz', 'Regulations=regulat|\\bdfs\\b', 'Channel widths=channel width|\\b(20|40|80|160|320) ?mhz',
        'Channel selection=non-overlapping|1, 6(,| and) 11|channel plan', 'Bluetooth', '802.11 standards=802\\.11|wi-?fi [4-7]', 'NFC=\\bnfc\\b', 'RFID=\\brfid\\b']),
    ('2.3', 'Summarize services provided by networked hosts.', [
        'DNS server=dns server', 'DHCP server=dhcp server', 'Fileshare=file (share|server)|fileshare', 'Print server', 'Mail server=mail server',
        'Syslog', 'Web server=web server', 'AAA=\\baaa\\b|radius|authentication, authorization', 'Database server=database', 'NTP=\\bntp\\b',
        'Spam gateway=spam', 'UTM=\\butm\\b|unified threat', 'Load balancer=load balanc', 'Proxy server=proxy', 'SCADA=scada', 'IoT=\\biot\\b|internet of things']),
    ('2.4', 'Explain common network configuration concepts.', [
        'A record=\\ba record|\\ba\\b and aaaa|\\ba/aaaa', 'AAAA=aaaa', 'CNAME=cname', 'MX=\\bmx\\b', 'TXT=\\btxt\\b', 'SPF=\\bspf\\b', 'DKIM=dkim', 'DMARC=dmarc',
        'DHCP lease=lease', 'Reservation=reservation', 'Scope=\\bscope\\b', 'Exclusions=exclusion', 'VLAN=\\bvlan', 'VPN=\\bvpn\\b']),
    ('2.5', 'Compare and contrast common networking hardware devices.', [
        'Router', 'Managed/unmanaged switch=managed switch|unmanaged', 'Access point=access point', 'Patch panel=patch panel', 'Firewall',
        'PoE=\\bpoe\\b|power over ethernet', 'PoE injector=injector', 'PoE standards=802\\.3a[ft]|802\\.3bt', 'Cable modem=cable modem|docsis',
        'DSL=\\bdsl\\b', 'ONT=\\bont\\b|optical network terminal', 'NIC=\\bnic\\b|network interface card', 'MAC address=mac address']),
    ('2.6', 'Given a scenario, configure basic wired/wireless small office/home office (SOHO) networks.', [
        'Private IPv4=private (range|address|ipv4)|rfc ?1918', 'Public addresses=public (ip|address|ipv4)', 'IPv6=ipv6', 'APIPA=apipa|169\\.254',
        'Static=static', 'Dynamic=dhcp|dynamic', 'Subnet mask=subnet mask|\\bmask\\b', 'Gateway=gateway']),
    ('2.7', 'Compare and contrast internet connection types, network types, and their characteristics.', [
        'Satellite', 'Fiber=fib(er|re)', 'Cable=cable (internet|modem|broadband)|docsis', 'DSL=\\bdsl\\b', 'Cellular=cellular|\\b5g\\b|\\blte\\b',
        'WISP=\\bwisp\\b|fixed wireless', 'LAN=\\blan\\b', 'WAN=\\bwan\\b', 'PAN=\\bpan\\b|personal area', 'MAN=metropolitan',
        'SAN=\\bsan\\b|storage area network', 'WLAN=\\bwlan\\b']),
    ('2.8', 'Explain networking tools and their purposes.', [
        'Crimper=crimp', 'Cable stripper=stripper', 'Wi-Fi analyzer=wi-?fi analy[sz]er|spectrum analy', 'Toner probe=toner probe|tone generator|toner and probe',
        'Punchdown tool=punch ?down', 'Cable tester=cable tester|certifier', 'Loopback plug=loopback plug|loopback adapter', 'Network tap=network tap']),
    ('3.1', 'Compare and contrast display components and attributes.', [
        'LCD=\\blcd\\b', 'IPS=\\bips\\b|in-plane', 'TN=\\btn\\b|twisted nematic', 'VA=\\bva\\b|vertical alignment', 'OLED=oled', 'Mini-LED=mini-?led',
        'Touch screen/digitizer=digitizer|touch ?screen', 'Inverter=inverter', 'Pixel density=pixel density|\\bppi\\b', 'Refresh rates=refresh rate',
        'Screen resolution=resolution', 'Color gamut=gamut|srgb|dci-p3']),
    ('3.2', 'Summarize basic cable types and their connectors, features, and purposes.', [
        'Copper categories=\\bcat ?[5-8]a?\\b|category [5-8]', 'T568A/T568B=t568', 'Coaxial=coax', 'Shielded twisted pair=shielded twisted|\\bstp\\b',
        'Unshielded twisted pair=unshielded|\\butp\\b', 'Direct burial=direct burial', 'Plenum-rated=plenum', 'Single-mode=single-?mode', 'Multimode=multi-?mode',
        'USB 2.0/3.0=usb (2|3)\\.[0-2]|usb 5 ?gbps', 'Serial=\\bserial\\b|db-?9|rs-?232', 'Thunderbolt', 'HDMI', 'DisplayPort', 'DVI=\\bdvi\\b', 'VGA=\\bvga\\b',
        'USB-C=usb-c', 'SATA=\\bsata\\b', 'eSATA=esata', 'RJ11=rj-?11', 'RJ45=rj-?45', 'F-type=f-type|f connector', 'ST/SC/LC=\\b(st|sc|lc)\\b',
        'Punchdown block=punch ?down block|110 block', 'MicroUSB/MiniUSB=micro-?usb|mini-?usb', 'Molex', 'Lightning', 'DB9=db-?9', 'Adapters=adapter|dongle']),
    ('3.3', 'Compare and contrast RAM characteristics.', [
        'SODIMM=so-?dimm', 'DIMM=\\bdimm', 'DDR iterations=ddr[3-5]', 'ECC vs. non-ECC=\\becc\\b', 'Channel configurations=dual[- ]channel|channel config|\\bchannels?\\b']),
    ('3.4', 'Compare and contrast storage devices.', [
        'Spindle speeds=rpm|spindle', '2.5/3.5-inch=(2\\.5|3\\.5)[- ]?(inch|in\\b|")', 'NVMe=nvme', 'SATA=\\bsata\\b', 'PCIe=pcie|pci express', 'SAS=\\bsas\\b|serial attached',
        'M.2=m\\.2', 'mSATA=msata', 'RAID 0/1/5/6/10=raid ?(0|1|5|6|10)\\b', 'Flash drives=flash drive|usb (stick|drive|flash)', 'Memory cards=sd card|memory card',
        'Optical drives=optical|dvd|blu-?ray']),
    ('3.5', 'Given a scenario, install and configure motherboards, central processing units (CPUs), and add-on cards.', [
        'ATX=\\batx\\b', 'microATX=micro-?atx', 'ITX=\\bitx\\b|mini-itx', 'PCI/PCIe=\\bpcie?\\b', 'Power connectors=24-pin|\\beps\\b|power connector', 'Headers=header',
        'M.2=m\\.2', 'CPU sockets=socket|\\bam[45]\\b|\\blga', 'Multisocket=multi-?socket|dual-socket', 'Boot options=boot order|boot option', 'USB permissions=usb permission|disable usb|usb port',
        'TPM=\\btpm\\b', 'Fan considerations=fan curve|\\bfans?\\b', 'Secure Boot=secure boot', 'Boot/BIOS password=(bios|uefi|boot|supervisor|setup) password',
        'Temperature monitoring=temperature', 'Virtualization support=vt-x|amd-v|\\bsvm\\b|virtuali[sz]ation (support|extensions)', 'HSM=\\bhsm\\b|hardware security module',
        'x86/x64=x86|x64', 'ARM=\\barm\\b', 'Core configurations=\\bcores\\b|core count|hyper-?thread|\\bsmt\\b|threads',
        'Expansion cards=expansion card|capture card|sound card|video card|graphics card', 'Cooling=heat ?sink|thermal paste|thermal pad|liquid cool']),
    ('3.6', 'Given a scenario, install the appropriate power supply.', [
        '110–120 vs. 220–240 VAC=(110|115|120|220|230|240) ?v(ac)?\\b', '3.3V/5V/12V=\\b(3\\.3|12) ?v\\b', '20+4 pin=24-pin|20\\+4', 'Redundant power supply=redundant (power|psu)',
        'Modular power supply=modular', 'Wattage rating=watt', 'Energy efficiency=80 plus|efficien']),
    ('3.7', 'Given a scenario, deploy and configure multifunction devices/printers and settings.', [
        'Set-up location=unbox|set-?up location|placement', 'PCL vs. PostScript=\\bpcl\\b|postscript', 'Firmware', 'Connectivity USB/Ethernet/wireless=(usb|ethernet|wireless|wi-?fi)[- ]connected|printer (port|connection)',
        'Printer share=printer shar|shared (printer|queue)', 'Print server=print server', 'Duplex', 'Orientation', 'Tray settings=\\btray', 'Quality=print quality|\\bdpi\\b',
        'User authentication/badging=badg|user authentication', 'Audit logs=audit log', 'Secured prints=secure(d)? (print|release)|pull print|pin release',
        'Scan services=scan to|scan-to', 'ADF/flatbed=\\badf\\b|automatic document feeder|flatbed']),
    ('3.8', 'Given a scenario, perform appropriate printer maintenance.', [
        'Laser maintenance kit=maintenance kit', 'Calibrate=calibrat', 'Clean=\\bclean', 'Inkjet cartridge/printhead=printhead|ink cartridge|nozzle',
        'Thermal=thermal (paper|printer)|heating element', 'Impact=\\bimpact printer|ribbon|multipart|dot matrix', 'Feed assembly/rollers=roller|feed assembly']),
    ('4.1', 'Explain virtualization concepts.', [
        'Sandbox', 'Test development=test (env|lab|development)', 'Application virtualization=application virtuali', 'Legacy software/OS=legacy',
        'Cross-platform virtualization=cross-platform', 'Requirements=requirement', 'VDI=\\bvdi\\b|virtual desktop', 'Containers=container', 'Type 1=type 1|bare-?metal', 'Type 2=type 2|hosted']),
    ('4.2', 'Summarize cloud computing concepts.', [
        'Private cloud', 'Public cloud', 'Hybrid cloud=hybrid', 'Community cloud', 'IaaS=iaas', 'SaaS=saas', 'PaaS=paas',
        'Shared vs. dedicated=shared resources|dedicated', 'Metered utilization=metered|egress|ingress|pay-as', 'Elasticity=elastic', 'Availability=availability|uptime',
        'File synchronization=file sync|synchroni', 'Multitenancy=multi-?tenan']),
    ('5.1', 'Given a scenario, troubleshoot motherboards, RAM, CPUs, and power.', [
        'POST beeps=beep|post code', 'Crash screens=bsod|stop (code|error)|crash screen|kernel panic', 'Blank screen=blank screen|no display|no video',
        'No power=no power|won.t power', 'Sluggish performance=sluggish|slow', 'Overheating=overheat|thermal throttl', 'Burning smell=burning|smell',
        'Random shutdown=random (shutdown|restart)|shuts? (itself )?(down|off)', 'Application crashes=crash', 'Unusual noise=noise|whine|grinding',
        'Capacitor swelling=capacitor', 'Inaccurate date/time=cmos|date and time|clock']),
    ('5.2', 'Given a scenario, troubleshoot drive and RAID issues.', [
        'LED status indicators=\\bled\\b|activity light', 'Grinding noises=grinding', 'Clicking sounds=click', 'Bootable device not found=bootable device|no boot device|boot device',
        'Data loss/corruption=corrupt|data loss', 'RAID failure=raid (failure|failed|degraded)|degraded', 'S.M.A.R.T. failure=s\\.m\\.a\\.r\\.t|smart (data|status|warning|attributes)',
        'Extended read/write times=latency|slow (read|write)|read/write', 'Low IOPS=iops', 'Missing drives in OS=missing drive|not (shown|detected|listed)|disk management',
        'Array missing=array (missing|not found)|foreign (config|disk)', 'Audible alarms=alarm|beep']),
    ('5.3', 'Given a scenario, troubleshoot video, projector, and display issues.', [
        'Incorrect input source=input (source|select)', 'Physical cabling issues=cable', 'Burnt-out bulb=bulb|projector lamp', 'Fuzzy image=fuzzy|blurr',
        'Display burn-in=burn-?in', 'Dead pixels=dead pixel|stuck pixel', 'Flashing screen=flicker|flashing', 'Incorrect color display=colou?r (cast|wrong|incorrect|tint)|tint',
        'Audio issues=audio|sound over hdmi', 'Dim image=\\bdim\\b|backlight', 'Intermittent projector shutdown=projector', 'Sizing issues=scaling|sizing|native resolution|aspect ratio',
        'Distorted image=distort']),
    ('5.4', 'Given a scenario, troubleshoot common mobile device issues.', [
        'Poor battery health=battery (health|wear)|full charge capacity', 'Swollen battery=swollen|swelling', 'Broken screen=(broken|cracked) (screen|display)',
        'Improper charging=not charging|charg(er|ing)', 'Poor/no connectivity=connectivity', 'Liquid damage=liquid|water damage', 'Overheating=overheat',
        'Digitizer issues=digitizer', 'Physically damaged ports=damaged port|port damage|charging port', 'Malware', 'Cursor drift/touch calibration=cursor drift|ghost touch|touch calibrat',
        'Unable to install apps=(unable|fails?) to install|storage (is )?full', 'Stylus does not work=stylus', 'Degraded performance=degraded|slow']),
    ('5.5', 'Given a scenario, troubleshoot network issues.', [
        'Intermittent wireless connectivity=intermittent', 'Slow network speeds=slow', 'Limited connectivity=limited connectivity|apipa|169\\.254', 'Jitter',
        'Poor VoIP quality=voip|voice quality', 'Port flapping=flap', 'High latency=latency', 'External interference=interference',
        'Authentication failures=authentication fail|802\\.1x|wrong (password|key)', 'Intermittent internet connectivity=internet']),
    ('5.6', 'Given a scenario, troubleshoot printer issues.', [
        'Lines down the page=vertical line|streak|lines down', 'Garbled print=garbled', 'Paper jams=jam', 'Faded prints=faded|faint', 'Paper not feeding=not feed|pickup roller',
        'Multipage misfeed=misfeed|double feed|multiple sheets', 'Multiple prints pending=queue', 'Speckling=speckl', 'Double/echo images=ghost|echo|double image',
        'Grinding noise=grinding', 'Finishing issues=staple|hole punch|finisher', 'Incorrect page orientation=orientation', 'Tray not recognized=\\btray',
        'Connectivity issues=offline|connectivity', 'Frozen print queue=stuck queue|frozen|spooler']),
]

_A2 = [
    ('1.1', 'Explain common operating system (OS) types and their purposes.', [
        'Windows', 'Linux', 'macOS', 'ChromeOS=chrome ?os|chromebook', 'iPadOS=ipados', 'iOS=\\bios\\b|iphone', 'Android', 'NTFS', 'ReFS', 'FAT32', 'ext4', 'XFS',
        'APFS', 'exFAT', 'End-of-life=end of (life|support)|\\beol\\b', 'Update limitations=update limit|no longer receives?|security updates',
        'Compatibility between OSs=compatib']),
    ('1.2', 'Given a scenario, perform OS installations and upgrades in a diverse environment.', [
        'USB boot=bootable usb|usb (installer|install media|boot)', 'Network boot=\\bpxe\\b|network boot', 'Internet-based install=cloud download|internet-based',
        'External/hot-swappable drive=external drive|hot-swap', 'Internal partition=partition', 'Multiboot=multi-?boot|dual-?boot', 'Clean install=clean install',
        'Upgrade=in-place|upgrade', 'Image deployment=image deploy|imaging|\\bimage\\b', 'Remote network installation=remote (network )?install|\\bwds\\b',
        'Zero-touch deployment=zero-?touch|autopilot', 'Recovery partition=recovery partition|winre', 'Repair installation=repair install|reinstall (the )?current version|fix problems using windows update',
        'Third-party drivers=(third-party|storage|raid|vendor) driver', 'GPT=\\bgpt\\b', 'MBR=\\bmbr\\b', 'Drive format=\\bformat', 'Backup files/preferences=back ?up|user data',
        'App/driver compatibility=driver (support|compatib)|app(lication)? compatib', 'Hardware compatibility=hardware (compatib|requirement)|pc health check',
        'Feature updates=feature update|2[45]h2', 'Product life cycle=lifecycle|life cycle|servicing']),
    ('1.3', 'Compare and contrast basic features of Microsoft Windows editions.', [
        'Home=\\bhome\\b', 'Pro=\\bpro\\b', 'Pro for Workstations=pro for workstations', 'Enterprise=enterprise', 'N versions=\\bn editions?|\\bn versions?',
        'Domain vs. workgroup=domain|workgroup', 'Desktop styles/UI=start menu|taskbar|desktop style', 'RDP availability=remote desktop|\\brdp\\b',
        'RAM support limitations=(ram|memory) (limit|support)|maximum (ram|memory)', 'BitLocker', 'gpedit.msc=gpedit', 'In-place upgrade=in-place',
        'Clean install=clean install', 'TPM=\\btpm\\b', 'UEFI=uefi']),
    ('1.4', 'Given a scenario, use Microsoft Windows operating system features and tools.', [
        'Task Manager', 'Services=services\\.msc|\\bservices\\b', 'Startup=\\bstartup\\b', 'Performance=\\bperformance\\b', 'Processes=process', 'Users tab=users tab',
        'Event Viewer=event viewer|eventvwr', 'Disk Management=disk management|diskmgmt', 'Task Scheduler=task scheduler|taskschd', 'Device Manager=device manager|devmgmt',
        'Certificate Manager=certmgr|certificate manager', 'Local Users and Groups=lusrmgr|local users and groups', 'Performance Monitor=perfmon|performance monitor',
        'Group Policy Editor=gpedit|group policy editor', 'System Information=msinfo32|system information', 'Resource Monitor=resmon|resource monitor',
        'System Configuration=msconfig|system configuration', 'Disk Cleanup=cleanmgr|disk cleanup', 'Disk Defragment=dfrgui|defrag|optimi[sz]e drives',
        'Registry Editor=regedit|registry editor']),
    ('1.5', 'Given a scenario, use the appropriate Microsoft command-line tools.', [
        'cd=\\bcd\\b', 'dir=\\bdir\\b', 'ipconfig', 'ping=\\bping\\b', 'netstat', 'nslookup', 'net use=net use', 'tracert', 'pathping', 'chkdsk', 'format=\\bformat\\b',
        'diskpart', 'md=\\bmd\\b|\\bmkdir\\b', 'rmdir', 'robocopy', 'hostname', 'net user=net user', 'winver', 'whoami', '[command] /?=/\\?', 'gpupdate', 'gpresult', 'sfc=\\bsfc\\b']),
    ('1.6', 'Given a scenario, configure Microsoft Windows settings.', [
        'Internet Options=internet options', 'Devices and Printers=devices and printers|printers (&|and) scanners', 'Programs and Features=programs and features|installed apps',
        'Network and Sharing Center=sharing center', 'Windows Defender Firewall=defender firewall|windows firewall', 'Mail=mail (control panel|profile|app)',
        'Sound=\\bsound\\b', 'User Accounts=user accounts', 'Device Manager=device manager', 'Indexing Options=indexing', 'Administrative Tools=administrative tools|windows tools',
        'File Explorer Options=hidden (files|items)|file name extensions|hide extensions|file explorer options', 'Power plans=power (options|plan|mode)',
        'Hibernate/sleep/standby=hibernat|\\bsleep\\b|standby', 'Lid close action=\\blid\\b', 'Fast startup=fast startup', 'USB selective suspend=selective suspend',
        'Ease of Access/Accessibility=ease of access|accessibility', 'Time and Language=time (&|and) language|time zone', 'Update and Security=windows update',
        'Personalization=personali[sz]ation', 'Apps=\\bapps\\b', 'Privacy=privacy', 'System=\\bsystem\\b', 'Devices=bluetooth (&|and) devices|\\bdevices\\b',
        'Network and Internet=network (&|and) internet', 'Gaming', 'Accounts=\\baccounts\\b']),
    ('1.7', 'Given a scenario, configure Microsoft Windows networking features on a client/desktop.', [
        'Domain joined vs. workgroup=domain|workgroup', 'Shared printers=shared printer|printer shar', 'File servers=file server', 'Mapped drives=mapped drive|map (a )?(network )?drive|net use',
        'Firewall settings=firewall', 'Application exceptions=allow (an )?app|exception|inbound rule', 'IP addressing/DNS settings=dns server|dns settings',
        'Subnet mask=subnet mask', 'Gateway=gateway', 'Static vs. dynamic=static', 'VPN=\\bvpn\\b', 'Wireless=wi-?fi|wireless', 'Wired=ethernet|wired',
        'WWAN/cellular=wwan|cellular', 'Proxy settings=proxy', 'Public vs. private network=public network|private network|network profile',
        'Network paths=unc path|network path|\\\\\\\\[a-z]', 'Metered connections=metered']),
    ('1.8', 'Explain common features and tools of the macOS/desktop operating system.', [
        '.dmg/.pkg/.app=\\.dmg|\\.pkg|\\.app\\b', 'App Store=app store', 'Uninstallation=uninstall', 'System folders=/applications|/library|/users|/system',
        'Apple ID and corporate restrictions=apple (id|account)', 'System Settings=system (settings|preferences)', 'Time Machine=time machine', 'Backups=backup',
        'Antivirus=antivirus|xprotect|anti-?malware', 'Updates/RSR=rapid security response|software update', 'Multiple desktops/Mission Control=mission control|multiple desktops|spaces',
        'Keychain', 'Spotlight', 'iCloud=icloud', 'Gestures=gesture', 'Finder', 'Dock=\\bdock\\b', 'Continuity=continuity|handoff|airdrop', 'Disk Utility=disk utility',
        'FileVault=filevault', 'Terminal=\\bterminal\\b', 'Force Quit=force quit']),
    ('1.9', 'Identify common features and tools of the Linux client/desktop operating system.', [
        'ls=\\bls\\b', 'pwd=\\bpwd\\b', 'mv=\\bmv\\b', 'cp=\\bcp\\b', 'rm=\\brm\\b', 'chmod', 'chown', 'grep', 'find=\\bfind\\b', 'fsck', 'mount=\\bmount\\b', 'su=\\bsu\\b',
        'sudo', 'apt=\\bapt\\b', 'dnf=\\bdnf\\b', 'ip=\\bip (a|addr|address|route|link)\\b', 'ping=\\bping\\b', 'curl', 'dig=\\bdig\\b', 'traceroute', 'man=\\bman\\b',
        'cat=\\bcat\\b', 'top=\\btop\\b', 'ps=\\bps\\b', 'du=\\bdu\\b', 'df=\\bdf\\b', 'nano', '/etc/passwd=/etc/passwd', '/etc/shadow=/etc/shadow', '/etc/hosts=/etc/hosts',
        '/etc/fstab=/etc/fstab', '/etc/resolv.conf=resolv\\.conf', 'systemd', 'kernel', 'bootloader=bootloader|grub', 'Root account=\\broot\\b']),
    ('1.10', 'Given a scenario, install applications according to requirements.', [
        '32-bit vs. 64-bit=32-bit|64-bit', 'Dedicated vs. integrated graphics=dedicated|integrated graphics|discrete', 'VRAM=vram', 'RAM requirements=(ram|memory) requirement|gb of ram',
        'CPU requirements=(cpu|processor) requirement', 'External hardware tokens=hardware token|dongle|security key', 'Storage requirements=disk space|storage requirement',
        'Application to OS compatibility=compatib', 'Physical media vs. ISO=\\biso\\b|mount', 'Downloadable package=installer|\\.msi|package',
        'Image deployment=image deploy|imaging', 'Impact considerations=impact']),
    ('1.11', 'Given a scenario, install and configure cloud-based productivity tools.', [
        'Email systems=exchange online|email system|mail service|microsoft 365|google workspace', 'Storage/sync settings=onedrive|known folder|sync (folder|settings)|\\bsync\\b',
        'Collaboration tools=teams|videoconferenc|spreadsheet|instant messag|collaborat|presentation', 'Identity synchronization=identity sync|entra connect|directory sync',
        'Licensing assignment=licen[cs]e assign|assign(ed|ing)? (a )?licen']),
    ('2.1', 'Summarize various security measures and their purposes.', [
        'Bollards=bollard', 'Access control vestibule=vestibule|mantrap', 'Badge reader=badge', 'Video surveillance=cctv|surveillance|camera', 'Alarm systems/motion sensors=alarm|motion sensor',
        'Door/equipment locks=\\block', 'Security guards=guard', 'Fences=fence', 'Key fobs=\\bfob', 'Smart cards=smart card', 'Mobile digital key=digital key',
        'Biometrics=biometric|fingerprint|facial', 'Lighting=lighting', 'Magnetometers=magnetometer', 'Least privilege=least privilege', 'Zero Trust=zero trust', 'ACLs=\\bacls?\\b',
        'MFA=\\bmfa\\b|multifactor|multi-factor', 'Hardware token=hardware token|security key|fido', 'Authenticator application=authenticator', 'SMS/voice call=\\bsms\\b|voice call',
        'TOTP/OTP=totp|one-time', 'SAML=saml', 'SSO=\\bsso\\b|single sign-on', 'Just-in-time/PAM=just-in-time|\\bpam\\b|privileged access', 'MDM=\\bmdm\\b',
        'DLP=\\bdlp\\b|data loss prevention', 'IAM=\\biam\\b|identity and access', 'Directory services=directory']),
    ('2.2', 'Given a scenario, configure and apply basic Microsoft Windows OS security settings.', [
        'Defender Antivirus=defender antivirus|microsoft defender', 'Update definitions=definition|security intelligence', 'Firewall', 'Local vs. Microsoft account=microsoft account|local account',
        'Standard/Administrator/Guest=standard (user|account)|administrator|\\bguest\\b', 'PIN=\\bpin\\b', 'Fingerprint/facial=fingerprint|facial',
        'Windows Hello/passwordless=windows hello|passwordless|passkey', 'SSO=single sign-on|\\bsso\\b', 'NTFS vs. share permissions=share permission|ntfs permission',
        'Attributes/inheritance=inherit|attribute', 'Run as administrator=run as admin', 'UAC=\\buac\\b|user account control', 'BitLocker', 'BitLocker To Go=to go',
        'EFS=\\befs\\b|encrypting file system', 'Joining domain=join(ing)? (a |the )?domain|domain join', 'Log-in script=log(o|i)n script',
        'Organizational units=organizational unit|\\bous?\\b', 'Home folders=home folder', 'Group Policy=group policy|\\bgpo', 'Security groups=security group',
        'Folder redirection=folder redirection']),
    ('2.3', 'Compare and contrast wireless security protocols and authentication methods.', [
        'WPA2=wpa2', 'WPA3=wpa3', 'TKIP=tkip', 'AES=\\baes\\b|ccmp', 'RADIUS=radius', 'TACACS+=tacacs', 'Kerberos', 'Multifactor=\\bmfa\\b|multifactor|multi-factor']),
    ('2.4', 'Summarize types of malware and tools/methods for detection, removal, and prevention.', [
        'Trojan', 'Rootkit', 'Virus', 'Spyware', 'Ransomware', 'Keylogger=keylog', 'Boot sector virus=boot sector', 'Cryptominer=cryptomin|cryptojack', 'Stalkerware',
        'Fileless=fileless', 'Adware/PUP=adware|\\bpups?\\b|potentially unwanted', 'Recovery console=recovery (console|environment)|winre', 'EDR/MDR/XDR=\\bedr\\b|\\bmdr\\b|\\bxdr\\b',
        'Antivirus/anti-malware=anti-?malware|antivirus', 'Email security gateway=email (security )?gateway', 'Software firewalls=firewall',
        'User education/antiphishing=phishing (training|simulation|awareness)|awareness training|educat', 'OS reinstallation=reinstall|reimage']),
    ('2.5', 'Compare and contrast common social engineering attacks, threats, and vulnerabilities.', [
        'Phishing=phish', 'Vishing=vish', 'Smishing=smish', 'QR code phishing=\\bqr\\b', 'Spear phishing/whaling=spear|whal', 'Shoulder surfing=shoulder surf', 'Tailgating=tailgat|piggyback',
        'Impersonation=impersonat|pretext', 'Dumpster diving=dumpster', 'DoS/DDoS=\\bd?dos\\b|denial of service', 'Evil twin=evil twin', 'Zero-day=zero-?day', 'Spoofing=spoof',
        'On-path=on-path|man-in-the-middle', 'Brute-force=brute', 'Dictionary attack=dictionary', 'Insider threat=insider', 'SQL injection=sql injection',
        'XSS=\\bxss\\b|cross-site', 'BEC=business email compromise|\\bbec\\b', 'Supply chain=supply chain', 'Unpatched/non-compliant systems=unpatched|non-compliant',
        'Unprotected systems=missing (antivirus|firewall)|unprotected', 'EOL=end of (life|support)|\\beol\\b', 'BYOD=\\bbyod\\b']),
    ('2.6', 'Given a scenario, implement procedures for basic small office/home office (SOHO) malware removal.', [
        'Investigate/verify symptoms=verify (the )?(malware )?symptom|investigate', 'Quarantine=quarantin|isolat', 'Disable System Restore=disable system restore|turn off system protection',
        'Remediate=remediat', 'Update anti-malware=update (the )?(anti-?malware|definitions|security intelligence)', 'Scan in safe mode/PE=safe mode|offline scan|defender offline|preinstallation|winpe',
        'Reimage/reinstall=reimage|reinstall', 'Schedule scans and updates=schedul', 'Enable System Restore/restore point=restore point', 'Educate the end user=educat']),
    ('2.7', 'Given a scenario, apply workstation security options and hardening techniques.', [
        'Data-at-rest encryption=encrypt', 'Password considerations=password (length|complexity)|composition|15 characters|passphrase', 'BIOS/UEFI passwords=(bios|uefi|firmware|setup) password',
        'Screensaver lock/timeout=screen ?lock|lock (the|your) (screen|pc)|win\\s?\\+\\s?l|screen saver|timeout', 'Log off=log ?off|sign out', 'Secure critical hardware=cable lock|lock (the )?laptop',
        'Password managers=password manager', 'Restrict user permissions=least privilege|restrict (user )?permission|standard user', 'Restrict log-in times=log ?(in|on) (hours|times)',
        'Disable guest account=guest account', 'Failed attempts lockout=lockout|failed (log ?in |sign-in )?attempt', 'Account expiration=account expir|expiration date',
        'Change default admin=default (admin|administrator|password|credential)', 'Disable AutoRun=autorun|autoplay', 'Disable unused services=unused services|disable (unnecessary|unused)']),
    ('2.8', 'Given a scenario, apply common methods for securing mobile devices.', [
        'Device encryption=device encryption|encrypt', 'Screen locks=screen lock|passcode|face id|pattern', 'Configuration profiles=configuration profile|management profile',
        'OS/app updates=(os|app|application|ios|android) update', 'Endpoint security software=content filter|antivirus|anti-malware|mobile threat', 'Locator applications=find my|locator|locate',
        'Remote wipes=remote wipe|\\bwipe\\b', 'Remote backup=icloud backup|remote backup|google (one )?backup', 'Failed log-in restrictions=failed (attempts|passcode)|erase data after',
        'MDM=\\bmdm\\b', 'BYOD vs. corporate-owned=\\bbyod\\b|company-owned|corporate-owned', 'Profile security requirements=compliance (policy|requirement)']),
    ('2.9', 'Compare and contrast common data destruction and disposal methods.', [
        'Drilling=drill', 'Shredding=shred', 'Degaussing=degauss', 'Incineration=incinerat', 'Erasing/wiping=\\bwip(e|ing)\\b|erase', 'Low-level formatting=low-level',
        'Standard formatting=quick format|standard format', 'Third-party vendor=third-party|vendor', 'Certification of destruction=certificate of (destruction|sanitization)|certificate',
        'Regulatory and environmental requirements=regulat|environment']),
    ('2.10', 'Given a scenario, apply security settings on SOHO wireless and wired networks.', [
        'Change default passwords=default (password|credential)|admin password', 'IP filtering=ip filter|mac filter|allow ?list', 'Firmware updates=firmware', 'Content filtering=content filter|dns filter',
        'Physical placement=placement|secure location', 'UPnP=upnp|universal plug', 'Screened subnet=screened subnet|\\bdmz\\b', 'Secure management access=remote (administration|management)|management access',
        'Change SSID=\\bssid', 'Disable SSID broadcast=ssid broadcast|hid(e|ing|den) (the )?(ssid|network)', 'Encryption settings=wpa[23]', 'Guest access=guest (network|wi-?fi|access|ssid)',
        'Disable unused ports=unused ports|disable (the )?(unused )?ports?', 'Port forwarding=port forward|port mapping']),
    ('2.11', 'Given a scenario, configure relevant security settings in a browser.', [
        'Trusted sources/hashing=\\bhash|checksum|sha-?256', 'Untrusted sources=untrusted|unofficial', 'Browser patching=browser (update|patch)|update the browser',
        'Extensions/plug-ins=extension|plug-?in|add-?on', 'Password managers=password manager', 'Valid certificates=certificate|padlock', 'Pop-up blocker=pop-?up',
        'Clearing data/cache=clear(ing)? (browsing data|cache|cookies)|\\bcache\\b', 'Private browsing=private (browsing|window)|incognito|inprivate',
        'Sign-in/data sync=browser sync|sync (passwords|browsing|data)|signed-in browser', 'Ad blockers=ad ?block', 'Proxy=proxy', 'Secure DNS=secure dns|dns over https|\\bdoh\\b',
        'Feature management=(enable|disable|turn off) (the )?(extension|plug-?in|feature)']),
    ('3.1', 'Given a scenario, troubleshoot common Windows OS issues.', [
        'BSOD=bsod|blue screen|stop (code|error)', 'Degraded performance=slow|degraded', 'Boot issues=boot (issue|problem|loop|fail)|won.t boot|startup repair',
        'Frequent shutdowns=frequent (shutdown|restart)|restarts? (unexpectedly|itself|on its own)|unexpected shutdown', 'Services not starting=service(s)? (not|won.t|fail(s|ed)? to) start',
        'Applications crashing=crash|event id 1000', 'Low memory warnings=low memory|out of memory|memory leak', 'USB controller resource warnings=usb (controller|resource)',
        'System instability=instab|unstable', 'No OS found=no (os|operating system) found|bootable device|bootmgr', 'Slow profile load=slow (logon|profile|sign-?in)|profile load|temporary profile',
        'Time drift=time drift|clock (skew|drift)|w32tm|time sync']),
    ('3.2', 'Given a scenario, troubleshoot common mobile OS and application issues.', [
        'App fails to launch=(fails? to|won.t|doesn.t) (launch|open)', 'App fails to close/crashes=crash|force (stop|close|quit)', 'App fails to update=(fails? to|won.t) update|app update',
        'App fails to install=(fails? to|won.t|unable to) install', 'Slow to respond=slow', 'OS fails to update=(os|ios|ipados|android|software) update', 'Battery life issues=battery (life|drain|usage)',
        'Random reboots=reboot|restarts? (randomly|itself)', 'Bluetooth', 'Wi-Fi=wi-?fi', 'NFC=\\bnfc\\b', 'Screen does not autorotate=rotat']),
    ('3.3', 'Given a scenario, troubleshoot common mobile OS and application security issues.', [
        'Unofficial app stores=sideload|unofficial|third-party (app )?store', 'Developer mode=developer (mode|options)|usb debugging', 'Root access/jailbreak=jailbr|\\broot(ed|ing)\\b',
        'Malicious apps/spoofing=malicious app|fake app|spoof', 'High network traffic=(high|unusual) (network|data) (traffic|use|usage)', 'Degraded response time=degraded|slow',
        'Data-usage limit notification=data(-| )usage|data limit|data cap', 'Limited/no internet connectivity=connectivity', 'High number of ads=\\bads\\b|adware',
        'Fake security warnings=fake (security|virus) (warning|alert)|scareware', 'Unexpected application behavior=unexpected', 'Leaked personal files/data=leak']),
    ('3.4', 'Given a scenario, troubleshoot common personal computer (PC) security issues.', [
        'Unable to access the network=(unable|can.t|cannot) (to )?(access|reach) (the )?network', 'Desktop alerts=desktop alert|alert', 'False antivirus alerts=fake (antivirus|security)|false alert|scareware|rogue (antivirus|security)',
        'Missing/renamed files=renamed|missing files|extension changed', 'Inability to access files=(can.t|cannot|unable to) (open|access) (the |their )?files', 'Unwanted OS notifications=unwanted notification|notification',
        'OS update failures=update(s)? (fail|error)|fails? to update', 'Random/frequent pop-ups=pop-?up', 'Certificate warnings=certificate (warning|error)', 'Redirection=redirect|hijack',
        'Degraded browser performance=browser (is )?(slow|performance)']),
    ('4.1', 'Given a scenario, implement best practices associated with documentation and support systems information management.', [
        'Ticketing systems=ticket', 'Categories/severity=categor|severity|priority', 'Escalation levels=escalat', 'Clear written communication=progress note|action . result|resolution note',
        'Inventory lists=inventory', 'CMDB=cmdb|configuration management database', 'Asset tags and IDs=asset (tag|id|record)', 'Procurement life cycle=procure',
        'Warranty and licensing=warranty', 'Assigned users=assigned (user|to)', 'Incident reports=incident report', 'SOPs=standard operating procedure|\\bsops?\\b|runbook',
        'Custom installation procedure=install(ation)? procedure|software package', 'Onboarding checklist=onboard|new (user|starter|hire)', 'Off-boarding checklist=off-?board|leaver',
        'SLAs=\\bslas?\\b|service-level', 'Knowledge base=knowledge(-| )base|kb article']),
    ('4.2', 'Given a scenario, apply change management procedures.', [
        'Documented business processes=business process', 'Rollback plan=rollback|roll back|back-?out', 'Backup plan=backup plan', 'Sandbox testing=sandbox|test (environment|lab)',
        'Responsible staff=responsible|change owner|implementer', 'Request forms=change request|request form', 'Purpose of the change=purpose|reason for (the )?change', 'Scope of the change=\\bscope\\b',
        'Change types=standard change|normal change|emergency change', 'Date/time/freeze/windows=maintenance window|change window|freeze', 'Affected systems/impact=affected|impact',
        'Risk analysis=risk', 'Change board approvals=\\bcab\\b|change (advisory )?board|approv', 'Implementation=implement', 'Peer review=peer review', 'End-user acceptance=acceptance|sign-?off']),
    ('4.3', 'Given a scenario, implement workstation backup and recovery methods.', [
        'Full=full backup', 'Incremental=incremental', 'Differential=differential', 'Synthetic full=synthetic', 'In-place/overwrite=in-place|overwrite',
        'Alternative location=alternate location|alternative location|different location|another location', 'Backup testing/frequency=test (the )?restore|restore test|test(ing)? (your |the )?backups?',
        'Onsite vs. offsite=off-?site|on-?site', 'GFS=grandfather|\\bgfs\\b', '3-2-1 rule=3-2-1']),
    ('4.4', 'Given a scenario, use common safety procedures.', [
        'ESD straps=wrist strap|esd strap', 'ESD mats=esd mat|anti-?static mat', 'Equipment grounding=ground', 'Component handling/storage=by the edges|handling', 'Antistatic bags=anti-?static bag',
        'Cable management=cable management|trip hazard', 'Government regulations=osha|regulation', 'Disconnect power=(unplug|disconnect) (the )?power|power (off|down)|unplug',
        'Lifting techniques=\\blift', 'Fire safety=fire|extinguisher', 'Safety goggles=goggle|eye protection|safety glasses', 'Air filter mask=mask|respirator']),
    ('4.5', 'Summarize environmental impacts and local environment controls.', [
        'MSDS/SDS=\\bm?sds\\b|safety data sheet', 'Battery disposal=batter(y|ies) (disposal|recycl|collection)|lithium-ion batter', 'Toner disposal=toner (disposal|recycl|return)',
        'Other device/asset disposal=e-?waste|electronic waste|recycl', 'Temperature/humidity=humidity|temperature', 'Ventilation/placement=ventilat|airflow',
        'Dust cleanup=\\bdust', 'Compressed air/vacuums=compressed air|vacuum', 'Surges/brownouts/blackouts=surge|brownout|blackout', 'UPS=\\bups\\b|uninterruptible', 'Surge suppressor=surge (suppressor|protector)']),
    ('4.6', 'Explain the importance of prohibited content/activity and privacy, licensing, and policy concepts.', [
        'Chain of custody=chain of custody', 'Inform management/law enforcement=law enforcement|inform (management|your manager)', 'Copy of drive=forensic (image|copy)|copy of (the )?drive|write.?block',
        'Incident documentation=incident (documentation|record|report)', 'Order of volatility=order of volatility|volatil', 'Licensing/DRM/EULA=\\beula\\b|\\bdrm\\b|licens',
        'Perpetual license=perpetual|subscription', 'Personal vs. corporate license=personal[- ]use|commercial use|corporate[- ]use', 'Open-source license=open[- ]source',
        'NDA/MNDA=\\bm?nda\\b|non-disclosure', 'Credit card data=credit card|payment card', 'Government-issued information=government-issued|passport|social security', 'PII=\\bpii\\b|personally identifiable',
        'Healthcare data=health(care)? (data|record|information)|\\bphi\\b|hipaa', 'Data retention=retention', 'AUP=acceptable use|\\baup\\b', 'Splash screens=splash screen|logon banner|login banner']),
    ('4.7', 'Given a scenario, use proper communication techniques and professionalism.', [
        'Professional appearance/attire=attire|dress code|appearance', 'Avoid jargon=jargon|plain language', 'Positive attitude=positive|confiden', 'Active listening=listen',
        'Cultural sensitivity=cultur', 'Be on time=on time|running late|punctual', 'Avoid distractions=distraction|personal call', 'Difficult customers=difficult (customer|user|situation)|angry|frustrated|upset',
        'Do not argue/dismiss/judge=argu|defensive|dismiss|judg', 'Clarify/open-ended questions=open-ended|clarif|restate', 'Discretion=discret', 'Set and meet expectations=expectation|timeline|status update',
        'Offer repair/replacement options=replacement option|repair or replace', 'Document services=document', 'Follow up=follow[- ]up', 'Confidential materials=confidential']),
    ('4.8', 'Explain the basics of scripting.', [
        '.bat=\\.bat\\b|batch file', '.ps1=\\.ps1\\b|powershell script', '.vbs=\\.vbs\\b|vbscript', '.sh=\\.sh\\b|bash script|shell script', '.js=\\.js\\b|javascript',
        '.py=\\.py\\b|python', 'Basic automation=automat', 'Restarting machines=restart-computer|restart(ing)? (machines|computers)|scheduled restart',
        'Remapping network drives=(re)?map(ping)? (a )?(network )?drive|new-psdrive', 'Installing applications=winget|msiexec|install(ing)? (apps|applications|software) (with|by|from) (a )?script',
        'Automated backups=automated backup', 'Gathering information=get-ciminstance|gather(ing)? (information|data|inventory)', 'Initiating updates=(initiat|trigger)(e|es|ing) updates|usoclient',
        'Script risks=execution policy|unintentional|untrusted script|test (the |a )?script']),
    ('4.9', 'Given a scenario, use remote access technologies.', [
        'RDP=\\brdp\\b|remote desktop', 'VPN=\\bvpn\\b', 'VNC=\\bvnc\\b', 'SSH=\\bssh\\b', 'RMM=\\brmm\\b|remote monitoring', 'SPICE=\\bspice\\b',
        'WinRM=winrm|enter-pssession|powershell remoting', 'Screen-sharing/videoconferencing=screen[- ]shar|quick assist|remote assistance', 'File transfer software=file transfer|\\bsftp\\b|\\bscp\\b',
        'Desktop management software=desktop management|intune|configuration manager', 'Security considerations=network level authentication|\\bnla\\b|(security|risk) of remote']),
    ('4.10', 'Explain basic concepts related to artificial intelligence (AI).', [
        'Application integration=copilot|ai (assistant|integration|feature)', 'Appropriate use policy=ai (use )?policy|appropriate use', 'Plagiarism=plagiar', 'Bias=\\bbias',
        'Hallucinations=hallucinat', 'Accuracy=accura', 'Private vs. public=(public|private|enterprise) (ai|model|chatbot|llm)', 'Data security/source/privacy=training data|prompt']),
]

_N = [
    ('1.1', 'Explain concepts related to the Open Systems Interconnection (OSI) reference model.', [
        'Layer 1 Physical=physical layer|layer 1\\b', 'Layer 2 Data link=data link|layer 2\\b', 'Layer 3 Network=network layer|layer 3\\b', 'Layer 4 Transport=transport layer|layer 4\\b',
        'Layer 5 Session=session layer|layer 5\\b', 'Layer 6 Presentation=presentation layer|layer 6\\b', 'Layer 7 Application=application layer|layer 7\\b']),
    ('1.2', 'Compare and contrast networking appliances, applications, and functions.', [
        'Router', 'Switch', 'Firewall', 'IDS/IPS=\\bids\\b|\\bips\\b|intrusion (detection|prevention)', 'Load balancer=load balanc', 'Proxy=proxy', 'NAS=\\bnas\\b|network-attached storage',
        'SAN=\\bsan\\b|storage area network', 'AP/controller=access point|wireless (lan )?controller|\\bwlc\\b', 'CDN=\\bcdn\\b|content delivery', 'VPN=\\bvpn\\b',
        'QoS=\\bqos\\b|quality of service', 'TTL=\\bttl\\b|time to live']),
    ('1.3', 'Summarize cloud concepts and connectivity options.', [
        'NFV=\\bnfv\\b|network functions virtual', 'VPC=\\bvpc\\b|virtual private cloud|\\bvnet\\b', 'Security groups/lists=security group|security list|\\bnsg\\b',
        'Internet gateway=internet gateway', 'NAT gateway=nat gateway', 'Cloud VPN=vpn gateway|site-to-site vpn', 'Direct Connect=direct connect|expressroute|dedicated (link|interconnect)',
        'Public/private/hybrid=(public|private|hybrid) cloud', 'SaaS/IaaS/PaaS=saas|iaas|paas', 'Scalability=scalab', 'Elasticity=elastic', 'Multitenancy=multi-?tenan']),
    ('1.4', 'Explain common networking ports, protocols, services, and traffic types.', [
        'FTP 20/21=\\bftp\\b', 'SFTP 22=sftp', 'SSH 22=\\bssh\\b', 'Telnet 23=telnet', 'SMTP 25=\\bsmtp\\b', 'DNS 53=\\b53\\b', 'DHCP 67/68=\\b67\\b', 'TFTP 69=tftp',
        'HTTP 80=\\bhttp\\b', 'NTP 123=\\bntp\\b', 'SNMP 161/162=snmp', 'LDAP 389=\\bldap\\b', 'HTTPS 443=\\b443\\b', 'SMB 445=\\b445\\b', 'Syslog 514=syslog',
        'SMTPS 587=\\b587\\b', 'LDAPS 636=ldaps|\\b636\\b', 'SQL Server 1433=1433', 'RDP 3389=3389', 'SIP 5060/5061=\\bsip\\b|506[01]', 'ICMP=icmp', 'TCP=\\btcp\\b',
        'UDP=\\budp\\b', 'GRE=\\bgre\\b', 'IPsec AH/ESP/IKE=ipsec|\\besp\\b|\\bike(v2)?\\b', 'Unicast=unicast', 'Multicast=multicast', 'Anycast=anycast', 'Broadcast=broadcast']),
    ('1.5', 'Compare and contrast transmission media and transceivers.', [
        '802.11 standards=802\\.11|wi-?fi [4-7]', 'Cellular=cellular|\\blte\\b|\\b5g\\b', 'Satellite', '802.3 standards=802\\.3|base-?t\\b|base-?[sl]r',
        'Single-mode vs. multimode=single-?mode|multi-?mode', 'DAC/twinax=\\bdac\\b|direct attach|twinax', 'Coaxial=coax', 'Cable speeds=gbps|10gbase|1000base',
        'Plenum=plenum', 'Transceivers (Ethernet/FC)=transceiver|fibre channel|fiber channel', 'SFP=\\bsfp', 'QSFP=qsfp', 'SC=\\bsc\\b', 'LC=\\blc\\b', 'ST=\\bst\\b',
        'MPO=\\bmpo\\b', 'RJ11=rj-?11', 'RJ45=rj-?45', 'F-type=f-type', 'BNC=\\bbnc\\b']),
    ('1.6', 'Compare and contrast network topologies, architectures, and types.', [
        'Mesh', 'Hybrid', 'Star/hub and spoke=\\bstar\\b|hub[- ]and[- ]spoke', 'Spine and leaf=spine', 'Point to point=point-to-point|point to point',
        'Three-tier hierarchical=three-tier|distribution layer|core layer|access layer', 'Collapsed core=collapsed core', 'North-south=north-south', 'East-west=east-west']),
    ('1.7', 'Given a scenario, use appropriate IPv4 network addressing.', [
        'Public vs. private=public (ip|address|ipv4)|private (ip|address|range)', 'APIPA=apipa|169\\.254', 'RFC1918=1918', 'Loopback/localhost=loopback|127\\.0\\.0\\.1|localhost',
        'VLSM=vlsm|variable[- ]length', 'CIDR=cidr|/2[0-9]\\b', 'IPv4 classes=class [a-e]\\b|classful']),
    ('1.8', 'Summarize evolving use cases for modern network environments.', [
        'SDN/SD-WAN=\\bsdn\\b|sd-wan|software-defined', 'Application aware=application[- ]aware', 'Zero-touch provisioning=zero-?touch', 'Transport agnostic=transport[- ]agnostic',
        'Central policy management=central(ised|ized)? (policy|management)', 'VXLAN=vxlan', 'DCI=data cent(er|re) interconnect|\\bdci\\b', 'Layer 2 encapsulation=layer 2 (encapsulation|overlay)|overlay',
        'ZTA=zero trust', 'Policy-based authentication=policy-based', 'Least privilege=least privilege', 'SASE/SSE=\\bsase\\b|\\bsse\\b|security service edge',
        'IaC=infrastructure as code|\\biac\\b', 'Playbooks/templates=playbook|template', 'Configuration drift=drift', 'Dynamic inventories=dynamic inventor',
        'Source/version control=version control|\\bgit\\b|repository', 'IPv6 exhaustion mitigation=exhaust', 'Dual stack=dual[- ]stack', 'Tunneling=tunnel', 'NAT64=nat64']),
    ('2.1', 'Explain characteristics of routing technologies.', [
        'Static routing=static route|ip route', 'Dynamic routing=dynamic routing|routing protocol', 'BGP=\\bbgp\\b', 'EIGRP=eigrp', 'OSPF=ospf',
        'Administrative distance=administrative distance', 'Prefix length=longest (prefix )?match|prefix length', 'Metric=metric|\\bcost\\b', 'NAT=\\bnat\\b',
        'PAT=\\bpat\\b|overload|port address translation', 'FHRP=fhrp|hsrp|vrrp|first hop redundancy', 'VIP=virtual ip|\\bvip\\b', 'Subinterfaces=subinterface|router-on-a-stick|dot1q']),
    ('2.2', 'Given a scenario, configure switching technologies and features.', [
        'VLAN=\\bvlan', 'VLAN database=vlan database|show vlan', 'SVI=\\bsvi\\b|interface vlan|switch virtual interface', 'Native VLAN=native vlan', 'Voice VLAN=voice vlan',
        '802.1Q tagging=802\\.1q|dot1q|\\btag(ged|ging)?\\b', 'Link aggregation=link aggregation|lacp|etherchannel|port[- ]channel', 'Speed=\\bspeed\\b', 'Duplex=duplex',
        'Spanning tree=spanning tree|\\bstp\\b|\\brstp\\b', 'MTU=\\bmtu\\b', 'Jumbo frames=jumbo']),
    ('2.3', 'Given a scenario, select and configure wireless devices and technologies.', [
        'Channel width=channel width|\\b(20|40|80|160) ?mhz', 'Non-overlapping channels=non-overlapping|1, 6(,| and) 11', 'Regulatory impacts/802.11h=802\\.11h|\\bdfs\\b|\\btpc\\b|regulat',
        '2.4/5/6GHz=ghz', 'Band steering=band steering', 'SSID/BSSID/ESSID=\\bssid|bssid|essid', 'Mesh networks=mesh', 'Ad hoc=ad hoc', 'Point to point=point-to-point|bridge link',
        'Infrastructure mode=infrastructure', 'Antennas=omni|directional|antenna', 'Autonomous vs. lightweight AP=autonomous|lightweight|controller-based|capwap',
        'WPA2/WPA3=wpa[23]', 'Guest networks/captive portals=captive portal|guest (network|ssid)', 'PSK vs. Enterprise=\\bpsk\\b|802\\.1x|enterprise']),
    ('2.4', 'Explain important factors of physical installations.', [
        'IDF/MDF=\\bidf\\b|\\bmdf\\b|distribution frame|wiring closet', 'Rack size=\\brack', 'Port-side exhaust/intake=exhaust|intake|airflow|hot aisle|cold aisle',
        'Patch panel=patch panel', 'Fiber distribution panel=fib(er|re) (distribution|patch) panel', 'Lockable=lockable|locked (rack|cabinet|room)', 'UPS=\\bups\\b|uninterruptible',
        'PDU=\\bpdu\\b|power distribution unit', 'Power load/voltage=power (load|budget)|voltage', 'Humidity=humidity', 'Fire suppression=fire suppression|clean agent|sprinkler',
        'Temperature=temperature']),
    ('3.1', 'Explain the purpose of organizational processes and procedures.', [
        'Physical vs. logical diagrams=logical (diagram|topology)|physical (diagram|topology)', 'Rack diagrams=rack (diagram|elevation)', 'Cable maps=cable (map|label|schedule)',
        'Layer 1/2/3 diagrams=diagram', 'Asset inventory=asset|inventory', 'IPAM=ipam|ip address management', 'SLA=\\bsla\\b|service-level', 'Wireless survey/heat map=site survey|heat ?map|wireless survey',
        'EOL/EOS=end of (life|support)|\\beo[ls]\\b', 'Patches/OS/firmware=patch|firmware', 'Decommissioning=decommission', 'Change management=change (management|request|control|record)',
        'Configuration management=(golden|baseline) config|running-config|startup-config|config(uration)? backup']),
    ('3.2', 'Given a scenario, use network monitoring technologies.', [
        'SNMP traps/MIB/versions=snmp|\\bmib\\b|\\btraps?\\b|snmpv3|community string', 'Flow data=netflow|ipfix|sflow|flow (data|record)', 'Packet capture=packet capture|wireshark|tcpdump|pcap',
        'Baseline metrics/anomaly alerting=baseline|anomal|threshold', 'Log aggregation/syslog/SIEM=syslog|\\bsiem\\b', 'API integration=\\bapi\\b', 'Port mirroring=port mirror|\\bspan\\b',
        'Network discovery=discovery|lldp|\\bcdp\\b', 'Traffic analysis=traffic analysis|top talkers', 'Performance/availability/configuration monitoring=availability|uptime|performance monitor']),
    ('3.3', 'Explain disaster recovery (DR) concepts.', [
        'RPO=\\brpo\\b|recovery point', 'RTO=\\brto\\b|recovery time', 'MTTR=mttr|mean time to repair', 'MTBF=mtbf|mean time between', 'Cold/warm/hot sites=(cold|warm|hot) site',
        'Active-active=active-active|active/active', 'Active-passive=active-passive|active/passive|active/standby', 'Tabletop exercises=tabletop', 'Validation tests=(failover|restore|validation) test']),
    ('3.4', 'Given a scenario, implement IPv4 and IPv6 network services.', [
        'DHCP reservations=reservation', 'DHCP scope=\\bscope', 'Lease time=lease', 'DHCP options=dhcp option|option (3|6|15)', 'Relay/IP helper=relay|ip helper|helper-address',
        'Exclusions=exclusion', 'SLAAC=slaac|stateless address', 'DNSSEC=dnssec', 'DoH/DoT=dns over (https|tls)|\\bdoh\\b|\\bdot\\b', 'A=\\ba record|\\ba\\b and aaaa|\\ba/aaaa',
        'AAAA=aaaa', 'CNAME=cname', 'MX=\\bmx\\b', 'TXT=\\btxt\\b', 'NS=\\bns\\b record|\\bns records?', 'PTR=\\bptr\\b', 'Forward/reverse zones=reverse (lookup|zone)|forward (lookup|zone)|in-addr\\.arpa',
        'Authoritative vs. non-authoritative=authoritative', 'Primary vs. secondary=(primary|secondary) (dns|server|zone)|zone transfer', 'Recursive=recursi', 'Hosts file=hosts file',
        'NTP=\\bntp\\b', 'PTP=\\bptp\\b|precision time', 'NTS=\\bnts\\b|network time security']),
    ('3.5', 'Compare and contrast network access and management methods.', [
        'Site-to-site VPN=site-to-site', 'Client-to-site VPN=client-to-site|remote[- ]access vpn', 'Clientless VPN=clientless', 'Split vs. full tunnel=split[- ]tunnel|full[- ]tunnel',
        'SSH=\\bssh\\b', 'GUI=\\bgui\\b|web (interface|ui)', 'API=\\bapi\\b', 'Console=console', 'Jump box/host=jump (box|host)|bastion', 'In-band vs. out-of-band=out-of-band|in-band|\\boob\\b']),
    ('4.1', 'Explain the importance of basic network security concepts.', [
        'Encryption in transit/at rest=in transit|at rest', 'Certificates/PKI/self-signed=\\bpki\\b|certificate|self-signed', 'IAM=\\biam\\b|identity and access',
        'MFA=\\bmfa\\b|multifactor|multi-factor', 'SSO=\\bsso\\b|single sign-on', 'RADIUS=radius', 'LDAP=\\bldap', 'SAML=saml', 'TACACS+=tacacs', 'Time-based authentication=time-based',
        'Least privilege=least privilege', 'Role-based access control=role-based|\\brbac\\b', 'Geofencing=geofenc', 'Camera/locks=camera|\\blocks?\\b', 'Honeypot/honeynet=honey(pot|net)',
        'Risk/vulnerability/exploit/threat=vulnerab|exploit', 'CIA triad=confidentiality|cia triad', 'Data locality=data (locality|residency|sovereignty)', 'PCI DSS=pci', 'GDPR=gdpr',
        'Segmentation enforcement=segment']),
    ('4.2', 'Summarize various types of attacks and their impact to the network.', [
        'DoS/DDoS=\\bd?dos\\b|denial of service', 'VLAN hopping=vlan hopping|double[- ]tag|switch spoofing', 'MAC flooding=mac flood|cam table (overflow|flood)',
        'ARP poisoning/spoofing=arp (poison|spoof)|gratuitous arp', 'DNS poisoning/spoofing=dns (poison|spoof)|cache poison', 'Rogue DHCP=rogue dhcp|dhcp snooping',
        'Rogue AP=rogue (ap|access point)', 'Evil twin=evil twin', 'On-path attack=on-path|man-in-the-middle|\\bmitm\\b', 'Social engineering=phish|dumpster|shoulder surf|tailgat',
        'Malware=malware|ransomware']),
    ('4.3', 'Given a scenario, apply network security features, defense techniques, and solutions.', [
        'Disable unused ports/services=unused (ports|services)|shutdown unused|disable unused', 'Change default passwords=default (password|credential)', 'NAC=\\bnac\\b|network access control',
        'Port security=port[- ]security', '802.1X=802\\.1x', 'MAC filtering=mac filter|allow-?list', 'Key management=key (management|rotation)|rotate (the )?keys', 'ACL=\\bacls?\\b|access-list',
        'URL filtering=url filter', 'Content filtering=content filter', 'Trusted vs. untrusted zones=untrusted|trusted zone|\\bzones?\\b', 'Screened subnet=screened subnet|\\bdmz\\b']),
    ('5.1', 'Explain the troubleshooting methodology.', [
        'Identify the problem=identify the problem|gather information|question (the )?users|what changed|reproduce|duplicate the problem', 'Theory/question the obvious=theory|question the obvious',
        'Top-to-bottom/bottom-to-top/divide and conquer=top-down|bottom-up|top-to-bottom|bottom-to-top|divide and conquer|half-?split', 'Test the theory=test the theory|test (a|the) theory',
        'Plan of action and potential effects=plan of action|potential effects', 'Implement or escalate=escalat', 'Verify and preventive measures=verify (full )?(system )?functionality|preventive',
        'Document findings=document|lessons learned']),
    ('5.2', 'Given a scenario, troubleshoot common cabling and physical interface issues.', [
        'Single mode vs. multimode=single-?mode|multi-?mode', 'Category 5/6/7/8=\\bcat ?[5-8]', 'STP vs. UTP=\\bstp\\b|\\butp\\b|shielded', 'Crosstalk=crosstalk', 'Interference=interference|\\bemi\\b',
        'Attenuation=attenuat|signal loss', 'Improper termination=terminat|pinout|wire ?map', 'TX/RX transposed=tx/rx|transposed|swapped (strands|pair)|polarity', 'CRC=\\bcrc\\b|\\bfcs\\b',
        'Runts=runt', 'Giants=giant', 'Drops=\\bdrops\\b|discard', 'Error disabled=err-?disabled|error[- ]disabled', 'Administratively down=administratively down|admin down', 'Suspended=suspended',
        'PoE power budget/standard=power budget|poe (budget|standard|class)|802\\.3(af|at|bt)', 'Transceiver mismatch/signal strength=transceiver|\\boptic|dbm|light level']),
    ('5.3', 'Given a scenario, troubleshoot common issues with network services.', [
        'STP loops/root bridge/port roles/states=network loop|broadcast storm|root bridge|port (role|state)|bpdu', 'Incorrect VLAN assignment=(wrong|incorrect) vlan|access vlan',
        'ACLs=\\bacls?\\b|access-list', 'Routing table=routing table|show ip route', 'Default routes=default route|0\\.0\\.0\\.0/0', 'Address pool exhaustion=exhaust|pool (is )?full|no free (addresses|leases)',
        'Incorrect default gateway=(wrong|incorrect|missing) (default )?gateway', 'Incorrect/duplicate IP=duplicate (ip|address)|address conflict', 'Incorrect subnet mask=(wrong|incorrect) (subnet )?mask']),
    ('5.4', 'Given a scenario, troubleshoot common performance issues.', [
        'Congestion/contention=congest|contention', 'Bottlenecking=bottleneck', 'Bandwidth/throughput=bandwidth|throughput', 'Latency=latency', 'Packet loss=packet loss',
        'Jitter=jitter', 'Interference/channel overlap=channel overlap|co-?channel|adjacent[- ]channel|interference', 'Signal degradation=signal (degrad|loss|strength)|rssi|\\bsnr\\b',
        'Insufficient coverage=coverage|dead (spot|zone)', 'Client disassociation=disassociat|deauth', 'Roaming misconfiguration=roam']),
    ('5.5', 'Given a scenario, use the appropriate tool or protocol to solve networking issues.', [
        'Protocol analyzer=protocol analy[sz]er|wireshark', 'ping=\\bping\\b', 'traceroute/tracert=tracert|traceroute', 'nslookup', 'tcpdump', 'dig=\\bdig\\b', 'netstat',
        'ip/ifconfig/ipconfig=ipconfig|ifconfig|\\bip (a|addr|route)\\b', 'arp=\\barp\\b', 'Nmap=nmap', 'LLDP/CDP=lldp|\\bcdp\\b', 'Speed tester=speed ?test|iperf', 'Toner=toner|tone generator',
        'Cable tester=cable tester|certifier', 'Taps=\\btaps?\\b', 'Wi-Fi analyzer=wi-?fi analy[sz]er|spectrum analy', 'Visual fault locator=visual fault|\\bvfl\\b',
        'show mac-address-table=mac[- ]address[- ]table', 'show route=show (ip )?route', 'show interface=show (ip )?interface', 'show config=show (running|startup|config)',
        'show arp=show (ip )?arp', 'show vlan=show vlan', 'show power=show power']),
]

OBJECTIVES = {}       # 'A1:2.1' -> {...}
for _ex, _rows in (('A1', _A1), ('A2', _A2), ('N', _N)):
    _doms = {d: (name, w) for d, name, w in DOMAINS[_ex]}
    _count = {}
    for _oid, _t, _tp in _rows:
        _count[_oid.split('.')[0]] = _count.get(_oid.split('.')[0], 0) + 1
    for _oid, _title, _topics in _rows:
        _d = _oid.split('.')[0] + '.0'
        OBJECTIVES[f'{_ex}:{_oid}'] = {
            'exam': _ex, 'id': _oid, 'domain': _d, 'domain_name': _doms[_d][0], 'title': _title, 'topics': list(_topics),
            # assumption: the domain weight is shared equally by its objectives (CompTIA publishes domain weights only)
            'weight': round(_doms[_d][1] / _count[_oid.split('.')[0]], 2),
        }


def objectives_for(exam):
    return [(k, v) for k, v in OBJECTIVES.items() if v['exam'] == exam]


def sort_key(oid):
    ex, num = oid.split(':')
    a, b = num.split('.')
    return (list(EXAMS).index(ex), int(a), int(b))


def label(oid):
    ex, num = oid.split(':')
    return f'{EXAMS[ex]["short"]} {num}'
