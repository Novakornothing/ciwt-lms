"""ITSUP Chapter 3 — Storage, Power, Ports & Peripherals (pass 10 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 3
SOURCES_USED = ['nvme-spec', 'ms-storage', 'cisa-backup', 'cisa-ransomware', 'pcisig-cem', 'usbif-naming', 'ms-display']

_NOTE = 'Core content added in pass 10.'

LESSONS = {
    (3, 1): {
        'objectives': [
            'Compare HDD, SATA SSD and NVMe SSD by interface, form factor and the kind of work each is good at',
            'Identify an M.2 drive’s keying, length and protocol before ordering a replacement',
            'Read a drive’s health in Windows (Drive health, Get-PhysicalDisk) and record it before imaging or replacing the disk',
            'Choose storage for a stated scenario and justify the choice in one sentence',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Three questions that pick a drive</h3>
<p>Every storage choice answers three separate questions, and most ordering mistakes come from mixing them up:</p>
<ol>
<li><strong>Form factor</strong> — the physical shape: 3.5-inch (desktop hard drives), 2.5-inch (laptop hard drives and most SATA SSDs) or
<strong>M.2</strong>, a small circuit-board “stick” 22 mm wide whose length is part of its name (2230, 2242, 2280 = 30, 42 or 80 mm long).</li>
<li><strong>Interface / protocol</strong> — how the drive talks to the board. <strong>SATA</strong> (Serial ATA, 6 Gb/s in its current
revision, a little under 600 MB/s in practice) or <strong>NVMe</strong> over PCIe lanes. NVMe was designed for flash and uses up to four
PCIe lanes, so a PCIe 4.0 ×4 NVMe drive can move several gigabytes per second.</li>
<li><strong>Media</strong> — spinning platters (HDD) or flash memory (SSD).</li>
</ol>
<p>An M.2 slot can accept SATA M.2 drives, NVMe drives or only one of them, depending on how the board is wired. The notch in the
connector (the <strong>key</strong>) is a clue, not proof: NVMe drives are usually <strong>M-keyed</strong>, many SATA M.2 drives are
<strong>B+M-keyed</strong> so they fit both kinds of slot. The board’s manual or the vendor’s parts list for that service tag is the
authority.</p>
''' + table(['Drive', 'Strength', 'Weakness', 'Typical ticket use'], [
            ['HDD (3.5" / 2.5")', 'Lowest cost per terabyte', 'Slow random access; moving parts; can click when failing', 'Bulk data, backup targets, archives'],
            ['SATA SSD (2.5" or M.2)', 'Fast random access; uses existing SATA ports', 'Capped by the SATA link', 'Upgrading an older PC that has no NVMe slot'],
            ['NVMe SSD (M.2)', 'Fastest common option; no cables', 'Must match slot keying, length and PCIe support', 'OS disk in current laptops and desktops'],
        ]) + '''
<h3>Health before hands</h3>
<p>Before anyone images, clones or replaces a disk, record its health. Drives report <strong>S.M.A.R.T.</strong> data
(Self-Monitoring, Analysis and Reporting Technology); NVMe drives report a standard health log that includes the percentage of rated life
used, available spare blocks and temperature. In Windows 11 the same facts appear for NVMe drives under <em>Settings → System → Storage →
Advanced storage settings → Disks &amp; volumes → Properties → Drive health</em>. In PowerShell, <code>Get-PhysicalDisk</code> lists each
disk’s <code>MediaType</code>, <code>BusType</code> and <code>HealthStatus</code>, and <code>Get-PhysicalDisk | Get-StorageReliabilityCounter</code>
adds wear, temperature and error counters where the drive provides them.</p>
<p>SSDs need no defragmenting: Windows’ <em>Optimize Drives</em> sends <strong>TRIM</strong> (“retrim”) to SSDs instead, telling the
drive which blocks are free. A failing HDD that clicks or shows reallocated sectors is copied <em>first</em> — every extra hour of
spinning can cost data.</p>
''' + worked('choosing the replacement drive', '''
<p>Ticket: “Laptop says ‘no bootable device’.” <code>Get-PhysicalDisk</code> from a recovery USB shows no NVMe disk at all, and the
firmware setup page lists no drive. The service-tag parts list shows an M.2 2280 NVMe (PCIe) drive. The technician orders an M.2 2280
<strong>NVMe</strong> drive of equal or larger capacity — not “an M.2 SSD”, which could arrive as a SATA M.2 drive that this slot may not
accept — and writes: “Firmware sees no disk; Get-PhysicalDisk lists none; parts list: M.2 2280 NVMe. Ordered like-for-like; user data
restore depends on the last OneDrive/backup sync (confirmed 2 days old).”</p>''') + cfu(
            ('A user wants “the fastest drive” for an older desktop with SATA ports and no M.2 slot. What do you offer?',
             'A 2.5-inch SATA SSD: it uses the existing SATA data and power cables. NVMe needs an M.2 slot or a PCIe adapter card.'),
            ('Why is “M.2 SSD” not enough information to order a part?',
             'M.2 is only the shape. You also need the length (for example 2280), the key and the protocol (SATA or NVMe) the slot supports.'),
            ('What do you record before imaging a disk that might be failing?',
             'Its health: S.M.A.R.T./Drive health values or Get-PhysicalDisk HealthStatus, plus the model and capacity. A failing disk is copied first.')),
        'sources': ['nvme-spec', 'ms-storage'],
    },
    (3, 2): {
        'objectives': [
            'Calculate usable capacity and fault tolerance for RAID 0, 1, 5, 6 and 10',
            'Explain why RAID, snapshots and sync are not backups, using the 3-2-1 rule',
            'Compare full, incremental and differential backups by what a restore needs',
            'Decide what to do first when an array reports degraded',
        ],
        'html': sme_note(_NOTE) + '''
<h3>RAID in numbers</h3>
<p><strong>RAID</strong> combines disks so that the operating system sees one volume. It protects against <em>a disk failing</em> — and
nothing else. It does not undo a deletion, a bad update, ransomware or a fire, because every one of those changes the data on all
disks at once.</p>
''' + table(['Level', 'Minimum disks', 'Usable capacity (n disks of size s)', 'Survives'], [
            ['RAID 0 (stripe)', '2', 'n × s', 'No disk failure — one failure loses the volume'],
            ['RAID 1 (mirror)', '2', 's (half of two disks)', 'One disk of the pair'],
            ['RAID 5 (stripe + parity)', '3', '(n − 1) × s', 'One disk; the array is at risk until the rebuild finishes'],
            ['RAID 6 (double parity)', '4', '(n − 2) × s', 'Any two disks'],
            ['RAID 10 (mirrored stripes)', '4', '(n ÷ 2) × s', 'One disk per mirror pair'],
        ]) + '''
<p>Example: four 4 TB disks give 16 TB in RAID 0, 12 TB in RAID 5, 8 TB in RAID 6 and 8 TB in RAID 10. A <strong>hot spare</strong> is an
idle disk the controller uses to start a rebuild automatically.</p>
<h3>What a backup is</h3>
<p>A backup is a <strong>separate copy you have restored from at least once</strong>. CISA’s guidance for small organisations is the
<strong>3-2-1 rule</strong>: three copies of the data, on two different kinds of storage, with one copy off site; for ransomware it also
recommends keeping backups offline (or otherwise unreachable from the network) and testing restores. Sync services such as OneDrive
copy deletions and encryption too, and a VM snapshot sits on the same storage as the VM — useful, but not a backup on its own.</p>
''' + table(['Backup type', 'Copies', 'A restore needs'], [
            ['Full', 'Everything selected', 'That one full backup'],
            ['Incremental', 'Changes since the last backup of any type', 'The last full plus every incremental since, in order'],
            ['Differential', 'Changes since the last full backup', 'The last full plus the newest differential'],
        ]) + figure('f3-2', 'Disk failure versus data loss', ['Disk fails', 'RAID keeps\nvolume online', 'Replace disk,\nrebuild', 'Data deleted\nor encrypted', 'RAID copies\nthe damage', 'Restore from\nbackup'],
             'Two rows of three boxes. Top row: a disk fails, RAID keeps the volume online, you replace the disk and rebuild. Bottom row: data is '
             'deleted or encrypted, RAID copies the damage to every disk, and the only fix is a restore from a separate, tested backup.',
             'RAID answers a disk failure; only a separate, tested backup answers deletion, corruption or ransomware.', cols=3) + scenario('the degraded array on a Friday', '''
<p>The office NAS emails “RAID 5 degraded — disk 3 failed” at 16:30. The tempting move is to pull disk 3 and slot in a spare before the
weekend. The right order: (1) treat it as an incident — the volume now has <em>no</em> redundancy; (2) confirm the most recent backup
finished and can be read (open a file from it); (3) note which bay failed and the exact model; (4) replace <em>that</em> bay’s disk with a
compatible one and let the rebuild run, with users warned that the share may be slow. Pulling the wrong disk from a degraded RAID 5
destroys the volume.</p>''') + cfu(
            ('Six 2 TB disks are configured as RAID 6. What is the usable capacity, and how many disks can fail?',
             '(6 − 2) × 2 TB = 8 TB; any two disks can fail.'),
            ('A user deletes a folder on a RAID 1 share. Does the mirror help?',
             'No. The deletion is written to both disks. Restore from a backup or from the share’s previous versions if they exist.'),
            ('Incremental backups ran Monday to Thursday after Sunday’s full. What does a Thursday restore need?',
             'Sunday’s full plus the Monday, Tuesday, Wednesday and Thursday incrementals, applied in order.')),
        'sources': ['cisa-backup', 'cisa-ransomware'],
    },
    (3, 3): {
        'objectives': [
            'Identify ATX power connectors (24-pin, CPU 8-pin, PCIe 6/8-pin, 12V-2x6) and the device each feeds',
            'Estimate a power budget and choose a replacement PSU of adequate rating and the same connectors',
            'Distinguish a surge protector from a UPS and select the right one for a scenario',
            'Diagnose overheating and thermal throttling from symptoms before replacing parts',
        ],
        'html': sme_note(_NOTE + ' Connector power limits checked against the PCIe CEM specification summaries.') + '''
<h3>What the power supply feeds</h3>
<p>A desktop <strong>power supply unit (PSU)</strong> converts mains AC into the DC rails the components use. It is a sealed,
field-replaceable unit: you test it from the outside and replace it whole — this course never opens one, because its capacitors can hold
a dangerous charge after it is unplugged.</p>
''' + table(['Connector', 'Feeds', 'Notes'], [
            ['24-pin ATX', 'Motherboard', 'Main board power; partly seated = random resets or no power'],
            ['8-pin (4+4) EPS / “CPU”', 'CPU voltage regulators', 'Missing = fans spin, no POST on many boards'],
            ['PCIe 6-pin / 8-pin', 'Graphics card', 'Up to 75 W / 150 W each, on top of the 75 W the slot provides'],
            ['12V-2x6 (successor to 12VHPWR)', 'Current high-power graphics cards', 'Up to 600 W through one connector; must be fully seated'],
            ['SATA power', 'SATA drives and some fans', 'Flat 15-pin; never mix up with the SATA data cable'],
        ]) + '''
<h3>Sizing a replacement</h3>
<p>Add up the main loads — CPU and graphics card (from their specification sheets), plus a modest allowance for board, drives and fans —
and choose a PSU whose rating leaves clear headroom above that total, with the <em>same connectors</em> the system uses. The
<strong>80 PLUS</strong> badge (Bronze to Titanium) is about efficiency — how little power is wasted as heat — not about how much the PSU
can deliver. A PSU that is too small often shows up as the PC turning off under load (a game, a render), not at idle.</p>
<h3>Mains problems: surge protector or UPS</h3>
<p>A <strong>surge protector</strong> clamps short voltage spikes; it does nothing when the power drops. A <strong>UPS</strong>
(uninterruptible power supply) runs the equipment from a battery during an outage or brown-out, long enough to save work and shut down
cleanly. Standby and line-interactive UPSs switch to battery when needed; online (double-conversion) UPSs run the load from the inverter
all the time. A server or NAS that must shut down cleanly needs a UPS with a data cable or network card that tells it to shut down.</p>
<h3>Heat</h3>
<p>CPUs and GPUs slow themselves down when they get too hot (<strong>thermal throttling</strong>) and switch off if that is not enough.
Symptoms: the PC is fast for a minute, then slow; fans roar; it shuts off under load. Check the firmware hardware monitor for temperatures,
look for blocked vents, dust in heatsinks and stopped fans, and only then consider re-pasting a cooler (a bench task with the vendor’s
procedure, not a hallway fix).</p>
''' + worked('random reboots under load', '''
<p>A design workstation reboots when rendering. The note reads: “Event Viewer: Kernel-Power 41 (unexpected shutdown) at each reboot, no
bugcheck. Firmware temps at idle: CPU 41 °C. Render test: reboot after 3 min; CPU 78 °C at the moment of reboot (not critical). GPU is a 300 W
card on a 450 W PSU (label). Plan: replace PSU with a 750 W unit, same 24-pin, 8-pin CPU and two PCIe 8-pin connectors. Verify: three
back-to-back renders without a reboot.” The temperature reading ruled out heat before the power budget was blamed.</p>''') + cfu(
            ('The board LEDs light and the fans spin, but there is no POST and no beep. Which power connector do you check first?',
             'The 8-pin CPU (EPS) connector: without it many boards power the fans but cannot start the CPU.'),
            ('Does an 80 PLUS Gold badge mean a PSU is powerful enough for a new graphics card?',
             'No. 80 PLUS rates efficiency. Check the wattage rating and that it has the card’s connectors.'),
            ('A NAS must survive a 2-minute outage and shut down cleanly in a longer one. Surge protector or UPS?',
             'A UPS with a USB/network signal to the NAS so it shuts down before the battery runs out.')),
        'sources': ['pcisig-cem'],
    },
    (3, 4): {
        'objectives': [
            'Identify USB-C capabilities (data rate, DisplayPort Alt Mode, Power Delivery) from port markings and documentation',
            'Isolate a display fault in order: power and input, cable and adapter, known-good display, output and driver',
            'Use Windows display tools (Win+P, Display settings, the graphics-driver reset shortcut) to recover a missing image',
            'Choose a cable or adapter that supports the required resolution and refresh rate',
        ],
        'html': sme_note(_NOTE + ' USB names follow the current USB-IF naming guidelines.') + '''
<h3>USB-C is a connector, not a capability</h3>
<p>The oval <strong>USB-C</strong> connector can carry very different things depending on the port and the cable:</p>
<ul>
<li><strong>Data</strong> — from USB 2.0 (480 Mb/s) to USB 10Gbps, USB 20Gbps, USB4 (up to 40 Gb/s) and USB4 Version 2.0 (up to 80 Gb/s).
Thunderbolt 3 and 4 run at 40 Gb/s; Thunderbolt 5 at 80 Gb/s.</li>
<li><strong>Video</strong> — through <strong>DisplayPort Alternate Mode</strong> (or tunnelled over USB4/Thunderbolt), only on ports wired
for it. Laptop makers mark these ports with a DisplayPort or Thunderbolt symbol, or list them in the specifications.</li>
<li><strong>Power</strong> — <strong>USB Power Delivery (USB PD)</strong> negotiates voltage and current. Standard USB PD reaches 100 W
(20 V at 5 A, which needs a 5 A cable with an electronic marker); USB PD 3.1 Extended Power Range goes up to 240 W with EPR cables.</li>
</ul>
<p>So “my monitor doesn’t work over USB-C” can be a port without video, a charge-only or USB 2.0 cable, or a dock that needs its own
power. The cable matters as much as the port.</p>
<h3>Display isolation order</h3>
''' + figure('f3-4', 'Display isolation after a good POST', ['Power + input\nselected', 'Cable and\nadapter', 'Known-good\ndisplay', 'Output port /\ngraphics', 'Driver and\nsettings'],
             'Five boxes in order. First check the display has power and the correct input is selected. Then swap the cable and any adapter for '
             'known-good ones. Then try a known-good display. Then try another output port or the onboard graphics. Last, check the graphics driver '
             'and Windows display settings.',
             'Work from the cheapest and most likely layer towards the graphics hardware, one swap at a time.', cols=5) + '''
<p>This order only starts once the PC has passed POST (Chapter 2.5); memory beep codes are not a cable problem. Windows tools help at the
last step: <kbd>Win</kbd>+<kbd>P</kbd> switches between PC screen only, Duplicate, Extend and Second screen only (a projector left in
“Second screen only” leaves the laptop panel black); <em>Settings → System → Display → Detect</em> re-scans for monitors; and
<kbd>Win</kbd>+<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd> restarts the graphics driver (the screen blinks and the PC beeps once).</p>
''' + table(['Link', 'Typical maximum bandwidth', 'Note'], [
            ['HDMI 2.0', '18 Gb/s', '4K at 60 Hz'],
            ['HDMI 2.1', '48 Gb/s', 'Higher refresh rates and resolutions; needs an Ultra High Speed cable'],
            ['DisplayPort 1.4', '32.4 Gb/s', 'Common on monitors and docks'],
            ['DisplayPort 2.1', 'Up to 80 Gb/s (UHBR20)', 'Needs a certified cable for the top rates'],
        ]) + scenario('the docking station that only charges', '''
<p>A new hire’s laptop charges from the desk dock but neither monitor lights. The technician checks the laptop’s specification: one
USB-C port supports DisplayPort Alt Mode and Thunderbolt, the other is data and charging only. The dock is plugged into the second port.
Moving it to the marked port brings up both monitors. The note records the port, the dock model and that the user was shown the
Thunderbolt symbol — and no driver was reinstalled.</p>''') + cfu(
            ('A laptop panel is black after a presentation, but the projector worked. What do you try first?',
             'Win+P and choose PC screen only or Duplicate; the laptop was probably left in Second screen only.'),
            ('A USB-C cable charges a phone fine but the monitor stays dark. Name two likely causes.',
             'The cable is charge-only or USB 2.0 (no video lanes), or the laptop port does not support DisplayPort Alt Mode.'),
            ('Long beeps and a MEM LED, no image. Do you start the display isolation order?',
             'No. That is a POST memory fault (Chapter 2.5). The display order starts after POST completes.')),
        'sources': ['usbif-naming', 'ms-display'],
    },
    (3, 5): {
        'objectives': [
            'Apply the hardware order (safety, POST, inventory, storage, power and heat, display) to one unstable workstation',
            'Record each test as action and result, changing one component at a time',
            'Decide when the evidence calls for a part, a backup first, or escalation',
        ],
        'html': sme_note(_NOTE) + '''
<h3>One ticket, several domains</h3>
<p>An unstable PC tempts you to change everything at once: new RAM, new PSU, fresh Windows. If it then works, nobody knows which change
fixed it, and the other two cost money and risked data for nothing. The capstone asks for the opposite: one domain at a time, one change
at a time, and a note that a colleague could follow.</p>
''' + table(['Step', 'Question', 'Evidence that answers it'], [
            ['Safety', 'Any smell, heat, swelling or shock report?', 'If yes: stop, isolate, report (Chapter 1.2)'],
            ['POST', 'Does firmware complete POST every time?', 'Beep/LED codes; firmware event log'],
            ['Inventory', 'What is in the box, and does Windows see all of it?', 'System → About, Device Manager, list disk'],
            ['Storage', 'Is the OS disk healthy?', 'Drive health / Get-PhysicalDisk; backup status'],
            ['Power and heat', 'Does it fail under load, and how hot does it get?', 'Kernel-Power 41 events; firmware temperatures; PSU label vs load'],
            ['Display', 'When the image goes, does the PC keep running?', 'Sound or remote access continues; isolation order from 3.4'],
        ]) + worked('the capstone note', '''
<p>“NOVAK-W11-07, intermittent reboots, ‘sometimes no video’. Safety: no smell/heat. POST: completes, no codes (3 cold starts). Inventory:
16 GB seen of 16 GB; Disk 0 = 512 GB NVMe, Drive health OK, 4% life used. Backup: OneDrive synced today. Event Viewer: Kernel-Power 41 at each
reboot, no bugcheck. Load test: reboot in 4 min; temps normal. ‘No video’ events coincide with the reboots (not a display fault). PSU label 300
W; GPU added last month draws up to 220 W. Change: none yet — request a 550 W PSU with matching connectors. Next: verify with 3 load tests.”
Every line is a test with a result; the display was ruled out by evidence, not skipped.</p>''') + cfu(
            ('Why change only one component at a time on an intermittent fault?',
             'So the result of each change is known. Several changes at once hide the real cause and may add new faults.'),
            ('The OS disk reports a warning while you investigate reboots. What comes before any other change?',
             'Make sure the user’s data is backed up (or copy it now), then continue; a failing disk can lose data with every hour.')),
        'sources': ['ms-storage'],
    },
}

GLOSSARY = [
    ('M.2 keying', 'The notch pattern on an M.2 card edge (commonly M or B+M) that shows which slots it fits; it does not prove SATA or NVMe.'),
    ('SATA', 'Serial ATA: the drive interface used by hard drives and many SSDs; the current revision signals at 6 Gb/s.'),
    ('S.M.A.R.T.', 'Self-Monitoring, Analysis and Reporting Technology: health counters a drive reports, such as reallocated sectors or life used.'),
    ('TRIM', 'A command that tells an SSD which blocks are no longer in use; Windows Optimize Drives sends it (“retrim”) instead of defragmenting SSDs.'),
    ('Hot spare', 'An idle disk in an array that the controller uses to start a rebuild automatically when a member disk fails.'),
    ('Degraded array', 'A RAID volume that is still online after a disk failure but has lost some or all of its redundancy until rebuilt.'),
    ('Full backup', 'A backup of everything selected; the base that incremental and differential backups build on.'),
    ('80 PLUS', 'An efficiency certification for power supplies (Bronze to Titanium); it says nothing about the wattage rating.'),
    ('UPS', 'Uninterruptible power supply: battery-backed power that keeps equipment running through an outage long enough to shut down cleanly.'),
    ('Surge protector', 'A power strip that clamps short voltage spikes; it provides no power during an outage.'),
    ('Thermal throttling', 'A CPU or GPU lowering its speed to stay within safe temperature; a common cause of “fast, then slow”.'),
    ('DisplayPort Alt Mode', 'A USB-C mode in which some of the cable’s lanes carry DisplayPort video; only ports wired for it support it.'),
    ('USB Power Delivery (USB PD)', 'The USB-C charging standard that negotiates voltage and current: up to 100 W standard, 240 W with Extended Power Range.'),
]

PLAN = {
    'warmup': 'Hold up a 2.5-inch SATA SSD, an M.2 SATA stick and an M.2 NVMe stick. Pairs write shape, key and protocol for each.',
    'guided': 'Read Drive health and Get-PhysicalDisk together (3.1), calculate RAID capacities on the board (3.2), size a PSU from two spec sheets (3.3), then walk the display isolation order with a deliberately wrong input (3.4).',
    'worked_example': 'Lesson 3.1 replacement drive; 3.3 random reboots under load; 3.5 the capstone note.',
    'cfu': ['What three facts do you need to order an M.2 drive?',
            'Four 4 TB disks in RAID 5: usable capacity?',
            'Surge protector or UPS for a NAS?',
            'USB-C monitor stays dark: two causes?'],
    'exit_ticket': 'Write the first three lines of a note for “PC reboots when I render”, each as test → result.',
    'misconceptions_add': ['“RAID 5 means we are backed up.” RAID covers one disk failure; deletion and ransomware hit every disk.',
                           '“80 PLUS Gold is a powerful PSU.” It is an efficiency grade, not a wattage.',
                           '“Every USB-C port does video and fast charging.” Port wiring and the cable decide.'],
    'classroom_lab': '',
    'materials_add': 'Sample SATA and M.2 drives; two GPU/CPU spec sheets for the power budget; a USB-C dock and a charge-only cable for the display drill.',
}

ITEMS = [
    item('IT-3.1', 1, 'A desktop has SATA ports but no M.2 slot. Which upgrade gives the biggest speed gain without extra parts?',
         'A 2.5-inch SATA solid-state drive', ['A 7,200 rpm 3.5-inch hard drive', 'An M.2 2280 NVMe solid-state drive', 'A second identical hard drive in RAID 1'],
         'A SATA SSD uses the existing SATA data and power cables and removes the hard drive’s seek time; NVMe needs an M.2 slot or a PCIe adapter (an extra part), and RAID 1 mirrors for redundancy, with at most a modest read gain.'),
    item('IT-3.1', 2, 'A parts list shows “M.2 2280 NVMe”. What does 2280 tell you?',
         'The card is 22 mm wide and 80 mm long', ['The drive’s capacity is 2,280 gigabytes', 'The drive uses PCIe generation 2.2', 'The drive reads at 2,280 megabytes per second'],
         'M.2 size codes give width and length in millimetres; 2280 is 22 × 80 mm.'),
    item('IT-3.1', 3, 'Before imaging a disk that might be failing, what should you record first?',
         'Its health status and model', ['The user’s Windows password', 'The disk’s defragmentation level', 'The BIOS boot-order password'],
         'Drive health or Get-PhysicalDisk HealthStatus, with model and capacity, decides whether to copy data first and what to order.'),
    item('IT-3.2', 1, 'Four 4 TB disks are configured as RAID 5. What is the usable capacity?',
         '12 TB', ['16 TB', '8 TB', '4 TB'],
         'RAID 5 uses one disk’s worth of space for parity: (4 − 1) × 4 TB = 12 TB.'),
    item('IT-3.2', 2, 'Ransomware encrypts files on a RAID 1 file share. What recovers the data?',
         'A restore from a separate backup', ['Rebuilding the mirror from disk two', 'Replacing both disks in the mirror', 'Switching the array to RAID 5'],
         'RAID writes the encrypted files to both disks; only a separate, tested backup holds clean copies.'),
    item('IT-3.2', 3, 'Incrementals ran Monday to Wednesday after Sunday’s full backup. What does a Wednesday restore need?',
         'Sunday’s full and all three incrementals', ['Only Wednesday’s incremental backup', 'Sunday’s full and Wednesday’s backup only', 'Monday’s incremental and the full backup'],
         'Each incremental holds changes since the previous backup, so all of them are applied in order after the full.'),
    item('IT-3.2', 4, 'A NAS reports “RAID 5 degraded”. What should happen before the failed disk is replaced?',
         'Confirm a recent backup can be restored', ['Pull a second disk to test the array', 'Reinitialise the array to clear the error', 'Update the NAS firmware to the latest'],
         'A degraded RAID 5 has no redundancy left; a verified backup must exist before any hands-on work.'),
    item('IT-3.3', 1, 'Fans spin and LEDs light, but the board never posts. Which connector should you check first?',
         'The 8-pin CPU (EPS) power plug', ['The SATA power plug on the drive', 'The front-panel USB header', 'The PCIe 6-pin plug on the GPU'],
         'Without CPU power many boards run fans but cannot start the processor.'),
    item('IT-3.3', 2, 'What does an 80 PLUS Gold label on a power supply describe?',
         'How efficiently it converts power', ['The maximum wattage it can deliver', 'Which connectors it provides', 'How long its warranty lasts'],
         '80 PLUS is an efficiency certification; wattage and connectors are separate specifications.'),
    item('IT-3.3', 3, 'A NAS must ride through short outages and shut down cleanly in long ones. What should be installed?',
         'A UPS that signals the NAS to shut down', ['A surge protector with a high joule rating', 'A larger power supply inside the NAS', 'A second NAS that mirrors the first one'],
         'Only a UPS supplies power during an outage, and its signal lets the NAS shut down before the battery runs out.'),
    item('IT-3.3', 4, 'A PC is fast for a minute, then slows down while the fans get louder. What is the most likely cause?',
         'Thermal throttling from poor cooling', ['A failing SATA data cable in the case', 'An expired Windows licence key', 'A misconfigured DNS server address'],
         'Rising heat makes the CPU or GPU lower its speed; check vents, dust, fans and temperatures.'),
    item('IT-3.4', 1, 'A monitor stays dark on a laptop’s USB-C port while charging works. What is a likely cause?',
         'The port does not support DisplayPort Alt Mode', ['The monitor needs a new external power supply', 'The laptop’s memory module is loose', 'The Windows display language is wrong'],
         'Not every USB-C port carries video; it must support DisplayPort Alt Mode or USB4/Thunderbolt video.'),
    item('IT-3.4', 2, 'After a presentation the laptop panel is black but the PC is running. What should you try first?',
         'Press Win+P and choose a screen mode', ['Reseat both of the laptop’s memory modules', 'Replace the laptop display panel', 'Reinstall Windows from recovery'],
         'The projection mode was probably left on Second screen only; Win+P switches it back.'),
    item('IT-3.4', 3, 'POST completed and the display is dark. After checking power and input, what is the next step?',
         'Swap the cable and adapter for known-good ones', ['Replace the graphics card with a brand-new one', 'Reinstall the graphics driver at once', 'Reset the firmware to factory defaults'],
         'The isolation order moves from the cheapest likely layer (cable, adapter) towards the graphics hardware.'),
]
