"""A+ Core 1 3.4 (storage devices), 3.5 (motherboards, CPUs, add-on cards) and 3.6 (power supplies) — ITSUP 3.1, 2.3, 3.3."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_RAID = figure(
    'fig-c-raid', 'RAID levels with four 4 TB drives',
    ['RAID 0:\n16 TB, no redundancy', 'RAID 1:\nmirror pairs', 'RAID 5:\n12 TB, 1 drive may fail', 'RAID 6:\n8 TB, 2 drives may fail', 'RAID 10:\n8 TB, 1 per mirror may fail'],
    'Five boxes. RAID 0 stripes data across all four drives: 16 TB usable, fastest, but any one failure loses everything. RAID 1 '
    'mirrors one drive onto another (usually used with two drives): half the raw capacity. RAID 5 stripes with one drive’s worth of '
    'parity: 12 TB usable, survives one failure, needs at least three drives. RAID 6 uses two drives’ worth of parity: 8 TB usable, '
    'survives two failures, needs at least four. RAID 10 stripes across mirrored pairs: 8 TB usable, survives one failure in each pair.',
    'RAID trades capacity for redundancy; none of these levels is a backup.', cols=5)

HTML_STORAGE = ('\n<p>Core 1 3.4 compares storage devices.</p>\n<ul>\n<li><strong>Hard disk drives</strong> — spindle speeds of 5,400 and 7,200 rpm on desktops and laptops, 10,000 and 15,000 rpm on older\nenterprise drives; 2.5-inch (laptop) and 3.5-inch (desktop, NAS) form factors.</li>\n<li><strong>Interfaces</strong> — <strong>SATA</strong> (desktop drives and SSDs); <strong>SAS</strong> (Serial Attached SCSI, enterprise drives:\na SAS controller can also run SATA drives, but a SATA controller cannot run SAS drives); <strong>NVMe</strong> SSDs on\n<strong>PCIe</strong> lanes, far faster than SATA.</li>\n<li><strong>SSD form factors</strong> — 2.5-inch SATA, <strong>M.2</strong> (SATA or NVMe — check which the slot supports),\n<strong>mSATA</strong> (an older small form factor replaced by M.2) and PCIe add-in cards.</li>\n<li><strong>RAID</strong> — 0 (striping), 1 (mirroring), 5 (striping with parity, minimum three drives), 6 (double parity, minimum four)\nand 10 (a stripe of mirrors, minimum four).</li>\n<li><strong>Removable storage</strong> — USB <strong>flash drives</strong>, <strong>memory cards</strong> (SD, microSD) and\n<strong>optical drives</strong> (CD about 700 MB, single-layer DVD 4.7 GB, single-layer Blu-ray 25 GB).</li>\n</ul>\n' + str(_FIG_RAID) + '\n' + str(worked('sizing a small office NAS', '''<ol>
<li>The office has 7 TB of files and wants to survive a drive failure. The NAS holds four 4 TB drives.</li>
<li>RAID 0 gives 16 TB but no redundancy — ruled out.</li>
<li>RAID 5 gives (4 − 1) × 4 = 12 TB and survives one failure. RAID 6 gives (4 − 2) × 4 = 8 TB and survives two. RAID 10 gives 8 TB and survives one per mirror pair.</li>
<li>All three redundant options fit 7 TB today. RAID 6 is chosen: large drives take a long time to rebuild, and it survives a second failure during that rebuild.</li>
<li>Back up the NAS to another location as well — RAID does not protect against deletion, ransomware or fire.</li></ol>''')) + '\n' + str(scenario('the M.2 drive the PC could not see', '''<p>A technician fits a new M.2 NVMe SSD in a small PC, but the firmware does not detect it. The motherboard manual
shows that this M.2 slot supports only SATA M.2 drives; the NVMe slot is on the back of the board. Moving the drive to the
correct slot fixes it. Checking the slot type in the manual before buying would have saved the trip.</p>''')) + '\n' + str(cfu(('What is the minimum number of drives for RAID 5, and how many can fail?', 'Three drives; one can fail.'),
     ('Can a SATA drive be connected to a SAS controller?', 'Yes — SAS controllers accept SATA drives, but SATA controllers cannot run SAS drives.'),
     ('Is RAID a backup?', 'No. It keeps running through a drive failure but does not protect against deletion, ransomware or disaster.'))) + '\n')

_FIG_MB = figure(
    'fig-c-mobo', 'Matching a motherboard to the job',
    ['Form factor:\nATX, microATX, ITX', 'CPU: socket, cores,\nx64 or ARM', 'Firmware: TPM,\nSecure Boot, VT-x', 'Security: BIOS password,\nUSB port control', 'Expansion: PCIe\nslots, M.2, headers'],
    'Five boxes. Choose the form factor to fit the case: ATX (full size), microATX (smaller, fewer slots) or mini-ITX (very small, '
    'usually one slot). Match the CPU to the socket and the workload: more cores and threads for parallel work; x86-64 for most '
    'Windows PCs, ARM in phones, Apple silicon Macs and some Windows laptops. In firmware, enable TPM, Secure Boot and '
    'virtualization support as needed. Set a firmware (BIOS/UEFI) password and disable unused USB ports where policy requires. '
    'Check PCIe slots, M.2 sockets and headers for the cards and front-panel connectors.',
    'The board decides what fits, what the CPU can be, and which security features are available.', cols=5)

HTML_MB = ('\n<p>Core 1 3.5 covers installing and configuring motherboards, CPUs and add-on cards.</p>\n<ul>\n<li><strong>Form factors</strong>: ATX (305 × 244 mm), microATX (244 × 244 mm), mini-ITX (170 × 170 mm).</li>\n<li><strong>CPU architecture</strong>: <strong>x86/x64</strong> (Intel and AMD; 64-bit x86 is called x64 or x86-64) and <strong>ARM</strong>\n(phones, tablets, Apple silicon Macs, some Windows laptops). Software must be built for the architecture or run under emulation.</li>\n<li><strong>Core configurations</strong>: multiple <strong>cores</strong> per CPU; simultaneous multithreading (Intel Hyper-Threading)\nruns two threads per core. <strong>Multisocket</strong> boards (servers and workstations) hold two or more CPUs.</li>\n<li><strong>Virtualization support</strong>: Intel VT-x or AMD-V, enabled in firmware, is required by hypervisors such as Hyper-V.</li>\n<li><strong>Firmware security</strong>: <strong>TPM</strong> (Trusted Platform Module — stores keys for BitLocker and measured boot;\nWindows 11 requires TPM 2.0, often a firmware TPM in the CPU), <strong>Secure Boot</strong>, <strong>boot options</strong> (boot order),\na <strong>boot/BIOS password</strong> (supervisor password for settings, user password to start), and <strong>USB permissions</strong>\n(disable ports or USB booting).</li>\n<li><strong>HSM</strong> — a hardware security module is a separate device or card that generates and protects keys, often validated to NIST FIPS 140-3; used by servers and certificate authorities rather than desktops.</li>\n<li><strong>Expansion</strong>: PCIe slots for video, sound, capture and network cards; M.2 sockets; headers for front-panel switches, USB, audio and fans.</li>\n<li><strong>Cooling</strong>: heat sink, thermal paste or pad, fans, and liquid cooling; monitor <strong>temperature</strong> in firmware or vendor tools.</li>\n</ul>\n' + str(_FIG_MB) + '\n' + str(worked('a lab PC that will not run virtual machines', '''<ol>
<li>Hyper-V will not install: “virtualization support is disabled in the firmware”.</li>
<li>Check the CPU model’s specifications: it supports Intel VT-x.</li>
<li>Restart into UEFI setup (supervisor password needed), enable Intel Virtualization Technology, save and exit.</li>
<li>Task Manager → Performance → CPU now shows “Virtualization: Enabled”. Install Hyper-V and test a VM.</li></ol>''')) + '\n' + str(scenario('the student who booted Linux from a stick', '''<p>In a public computer lab, a student booted a live Linux USB stick and bypassed the Windows sign-in. The lab
PCs had no firmware password and USB was first in the boot order. The fix: internal disk first in the boot order, USB booting
disabled, a supervisor password on the firmware, Secure Boot on, and BitLocker with the TPM so the disk is unreadable from
another OS.</p>''')) + '\n' + str(cfu(('Which firmware setting must be on for a hypervisor to run VMs?', 'CPU virtualization support (Intel VT-x or AMD-V).'),
     ('What does a TPM store, and which Windows feature uses it?', 'Keys and boot measurements; BitLocker (and Windows 11 requires TPM 2.0).'),
     ('Why might an app fail on an ARM laptop?', 'It was built only for x86/x64 and is not available for, or does not run well under emulation on, ARM.'))) + '\n')

_FIG_PSU = figure(
    'fig-c-psu', 'Choosing a power supply',
    ['Input: 110–120 or\n220–240 VAC', 'Outputs: 3.3, 5\nand 12 V rails', 'Connectors:\n24-pin, EPS, PCIe', 'Wattage with\nheadroom', 'Modular or\nredundant'],
    'Five boxes. Check the input voltage the PSU accepts: 110–120 VAC in North America, 220–240 VAC in the UK and much of Europe and '
    'Asia; most modern units are auto-ranging. The PSU supplies 3.3 V, 5 V and 12 V outputs, with most power on 12 V. It needs the '
    'right connectors: the 24-pin (20+4) motherboard connector, the CPU EPS connector and PCIe power for graphics cards. Size the '
    'wattage for the parts plus headroom, and prefer an efficient (80 PLUS rated) unit. Modular PSUs have detachable cables; '
    'servers use redundant hot-swappable PSUs.',
    'Voltage, rails, connectors, wattage and form decide whether a PSU fits.', cols=5)

HTML_PSU = ('\n<p>Core 1 3.6 asks you to install the appropriate power supply.</p>\n<ul>\n<li><strong>Input voltage</strong>: 110–120 VAC (North America, Japan) or 220–240 VAC (UK, most of Europe). Most current PSUs are\n<em>auto-ranging</em>; older ones have a voltage selector switch, and setting it to 115 V on a 230 V supply can destroy the PSU.</li>\n<li><strong>Outputs</strong>: +3.3 V, +5 V and +12 V DC; modern CPUs and graphics cards draw mostly from 12 V.</li>\n<li><strong>Connectors</strong>: 24-pin ATX (the older 20-pin plus a 4-pin section, “20+4”), 4/8-pin EPS for the CPU, PCIe power for graphics cards, SATA power for drives.</li>\n<li><strong>Wattage rating</strong>: add up the components and leave headroom; a PSU near its limit runs hot and less efficiently.</li>\n<li><strong>Energy efficiency</strong>: the 80 PLUS ratings certify efficiency at set loads.</li>\n<li><strong>Modular power supply</strong>: cables detach, so only the needed ones are fitted — better airflow and tidier builds. Semi-modular units fix the main cables.</li>\n<li><strong>Redundant power supply</strong>: two or more PSUs in a server, each able to run it alone and hot-swappable, ideally fed from separate circuits.</li>\n</ul>\n' + str(_FIG_PSU) + '\n' + str(worked('a graphics upgrade that reboots under load', '''<ol>
<li>After fitting a new graphics card, the PC restarts during games but is fine on the desktop.</li>
<li>The card maker recommends a larger total PSU rating than the 450 W unit fitted, and the card needs two 8-pin PCIe connectors; one is fed by an adapter from SATA power.</li>
<li>Fit a PSU that meets the card maker’s recommendation, with native PCIe connectors, from an 80 PLUS rated range.</li>
<li>Test under load for an hour while watching temperatures; no restarts. Record the PSU model on the asset.</li></ol>''')) + '\n' + str(scenario('the server that stayed up', '''<p>A small server has two redundant power supplies, both plugged into the same power strip. When the strip
fails, the server goes down anyway. The technician moves one PSU to a second circuit through a different UPS, so a single
strip, circuit or UPS failure no longer stops the server — and replaces the failed strip while the server keeps running.</p>''')) + '\n' + str(cfu(('What does an auto-ranging PSU do?', 'Accepts any input from about 100 to 240 VAC without a selector switch.'),
     ('Why choose a modular power supply?', 'Only the cables you need are fitted, improving airflow and cable management.'),
     ('What makes a redundant PSU setup actually redundant?', 'Each PSU can run the system alone, is hot-swappable, and is fed from a separate power source.'))) + '\n')

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 3, 'lesson': 1, 'id': 'cert-storage-devices', 'title': 'Storage devices: interfaces, form factors, RAID and removable media',
     'cert': ['A1:3.4'], 'html': sme_note('Storage devices compared (Core 1 3.4).') + HTML_STORAGE, 'sources': ['snia-ddf', 'ms-storage']},
    {'course': 'ITSUP', 'chapter': 2, 'lesson': 3, 'id': 'cert-mobo-cpu', 'title': 'Motherboards, CPU architectures, firmware security and add-on cards',
     'cert': ['A1:3.5'], 'html': sme_note('Motherboards, CPUs and add-on cards (Core 1 3.5).') + HTML_MB, 'sources': ['tcg-tpm', 'nist-fips1403', 'ms-hyperv-req']},
    {'course': 'ITSUP', 'chapter': 3, 'lesson': 3, 'id': 'cert-psu', 'title': 'Choosing and installing a power supply',
     'cert': ['A1:3.6'], 'html': sme_note('Power supplies (Core 1 3.6).') + HTML_PSU, 'sources': ['intel-atx3']},
]

GLOSSARY = [
    ('SAS', 'Serial Attached SCSI: enterprise drive interface; SAS controllers also accept SATA drives.'),
    ('mSATA', 'Older small SSD form factor using SATA, replaced by M.2.'),
    ('RAID 6', 'Striping with double parity: survives two drive failures; minimum four drives.'),
    ('RAID 10', 'A stripe across mirrored pairs; minimum four drives.'),
    ('ARM', 'Processor architecture used in phones, tablets, Apple silicon Macs and some Windows laptops.'),
    ('Multisocket', 'Motherboard that holds two or more physical CPUs.'),
    ('HSM', 'Hardware security module: dedicated device that generates and protects cryptographic keys.'),
    ('Auto-ranging PSU', 'Power supply that accepts any mains input from about 100 to 240 VAC.'),
    ('Modular power supply', 'PSU with detachable cables so only those needed are fitted.'),
    ('Redundant power supply', 'Two or more hot-swappable PSUs, each able to power the system alone.'),
]

ITEMS = [
    single('A1:3.4', 'IT-3.1', 1, 'A NAS has four 4 TB drives in RAID 5. About how much usable space is there?',
           '12 TB', ['16 TB', '8 TB', '4 TB'], 'RAID 5 loses one drive’s worth to parity: (4 − 1) × 4 TB.'),
    match('A1:3.4', 'IT-3.1', 2, 'Match each RAID level to its description.',
          [('RAID 0', 'Striping, no redundancy'), ('RAID 1', 'Mirroring'), ('RAID 5', 'Striping with single parity'), ('RAID 6', 'Striping with double parity')],
          'Know the levels named in Core 1 3.4.', decoys=['Mirrors of parity sets']),
    single('A1:3.4', 'IT-3.1', 3, 'An M.2 SSD is not detected after installation; the board manual says that slot is “SATA only”. What is the most likely cause?',
           'The drive is an NVMe M.2 SSD in a SATA-only slot',
           ['The slot needs a RAID 1 partner drive before it works', 'The SSD has to be formatted as exFAT first', 'mSATA drives must be fitted in M.2 slots instead'],
           'M.2 is a form factor; the slot may support SATA, NVMe or both.'),
    multi('A1:3.4', 'IT-3.1', 4, 'Which TWO RAID levels need at least four drives? (Choose two.)',
          ['RAID 6', 'RAID 10'], ['RAID 0', 'RAID 1', 'RAID 5'],
          'RAID 6 needs four for double parity; RAID 10 needs two mirrored pairs.'),
    single('A1:3.5', 'IT-2.2', 1, 'Hyper-V reports that virtualization support is disabled. What should the technician enable in firmware?',
           'Intel VT-x or AMD-V', ['Secure Boot', 'The TPM', 'USB legacy support'],
           'Hypervisors need the CPU’s hardware virtualization extensions.'),
    match('A1:3.5', 'IT-2.1', 2, 'Match each item to its purpose.',
          [('TPM', 'Stores keys for disk encryption on the board'), ('HSM', 'Separate device protecting keys for servers or CAs'),
           ('Supervisor password', 'Stops changes to firmware settings'), ('Multisocket board', 'Holds two or more physical CPUs')],
          'Core 1 3.5 security and configuration terms.', decoys=['mini-ITX']),
    single('A1:3.5', 'IT-2.1', 3, 'A user’s new laptop has an ARM processor and an old accounting app will not install. What is the most likely reason?',
           'The app is built only for x86/x64 processors',
           ['The laptop has its TPM 2.0 chip turned off', 'The laptop has too many processor cores', 'Secure Boot blocks every app that is unsigned'],
           'Software must be built for the CPU architecture or run under emulation.'),
    single('A1:3.6', 'IT-3.3', 3, 'An older PSU has a voltage switch set to 115 V and is moved to a country with 230 V mains. What is the risk?',
           'The PSU can be damaged when it is powered on',
           ['The PC will run at half speed', 'The 3.3 V rail will be disabled', 'The PSU will switch to modular mode'],
           'Fixed-range PSUs must be set to the local mains voltage; auto-ranging units avoid this.'),
    multi('A1:3.6', 'IT-3.3', 4, 'Which TWO make a server’s redundant power supplies effective? (Choose two.)',
          ['Each PSU can run the server alone', 'Each PSU is fed from a separate circuit'],
          ['Both PSUs share one power strip', 'Each PSU has a lower wattage than needed', 'The PSUs are non-modular', 'The PSUs use 20-pin connectors'],
          'Redundancy needs independent capacity and independent supply.'),
]
