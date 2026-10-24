"""A+ Core 1 3.7/3.8/5.6 (printer configuration, maintenance and symptoms) — ITSUP 4.3; Core 1 5.2 (storage symptoms) — ITSUP 3.2."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-printdefect', 'Laser print defects: where on the page points to which part',
    ['Repeating mark at\nfixed interval', 'Vertical line\nor streak', 'Toner smears\nor rubs off', 'Ghost / echo\nimage', 'Speckling\nall over'],
    'Five boxes, each a defect and its usual cause. A mark that repeats at a fixed distance down the page comes from a roller '
    'or the drum whose circumference matches that distance. A vertical line or streak comes from a scratch or debris on the '
    'drum, or a dirty charging part. Toner that smears or rubs off was not fused, so suspect the fuser. A faint repeat of an '
    'earlier image (ghosting or echo) comes from toner left on the drum or a worn cleaning blade, or the fuser. Speckling across '
    'the page suggests leaking toner or a failing drum or toner cartridge.',
    'Measure the gap between repeating defects and compare with the roller sizes in the service manual.', cols=5)

HTML_PRINT = ('\n<h4>Deploying and configuring printers and MFDs (Core 1 3.7)</h4>\n<ul>\n<li><strong>Drivers and page-description languages:</strong> <strong>PCL</strong> (Printer Command Language) is fast and widely\nsupported for office printing; <strong>PostScript</strong> is device-independent and preferred for graphics and publishing.\nA driver for the wrong language produces <strong>garbled print</strong> — pages of symbols.</li>\n<li><strong>Connectivity and sharing:</strong> USB, Ethernet or wireless; shared from a PC or through a <strong>print server</strong>;\nkeep printer firmware current.</li>\n<li><strong>Configuration settings:</strong> <strong>duplex</strong> (two-sided), <strong>orientation</strong>, <strong>tray settings</strong>\n(paper size and type per tray) and <strong>quality</strong> (resolution in dpi, draft or best).</li>\n<li><strong>Security:</strong> <strong>user authentication / badging</strong> at the device, <strong>audit logs</strong> of who printed what,\nand <strong>secured prints</strong> (the job is held until the user releases it with a PIN or badge, so confidential pages are not\nleft in the tray).</li>\n<li><strong>Network scan services:</strong> scan to email, to a network folder (SMB) or to cloud storage; the document feeder\n(<strong>ADF</strong>) handles multi-page stacks, the <strong>flatbed</strong> handles books and fragile originals.</li>\n</ul>\n<h4>Maintenance (Core 1 3.8)</h4>\n<ul>\n<li><strong>Laser:</strong> replace the toner; apply the <strong>maintenance kit</strong> (typically fuser and rollers) at the page\ncount the vendor specifies and reset the counter; <strong>calibrate</strong>; clean with a toner-safe vacuum, never ordinary\ncompressed air indoors on loose toner.</li>\n<li><strong>Thermal:</strong> replace the heat-sensitive paper roll; clean the <strong>heating element</strong> (isopropyl alcohol on\nthe vendor-approved swab); remove debris.</li>\n<li><strong>Impact (dot matrix):</strong> replace the <strong>ribbon</strong>, the print head and multipart paper as needed.</li>\n<li><strong>Inkjet:</strong> clean and align the printhead (built-in utility), replace cartridges, calibrate.</li>\n</ul>\n' + str(_FIG) + '\n<h4>Printer symptoms (Core 1 5.6)</h4>\n<table class="ref-table"><thead><tr><th scope="col">Symptom</th><th scope="col">Usual cause</th></tr></thead><tbody>\n<tr><td>Lines down the page; speckling</td><td>Drum scratch or debris; leaking toner cartridge; on inkjets, clogged nozzles</td></tr>\n<tr><td>Garbled print</td><td>Wrong driver or PCL/PostScript mismatch; corrupted job in the queue</td></tr>\n<tr><td>Faded prints</td><td>Low toner; economy mode; on laser, a worn drum</td></tr>\n<tr><td>Double / echo images</td><td>Drum not cleaned between rotations; fuser problems</td></tr>\n<tr><td>Paper jams, paper not feeding, multipage misfeed</td><td>Worn pickup rollers or separation pad, wrong paper weight, damp paper, overfilled tray</td></tr>\n<tr><td>Grinding noise</td><td>Worn gears or a failing fuser drive; stop and inspect</td></tr>\n<tr><td>Finishing issues</td><td>Stapler or hole-punch unit out of staples, jammed, or not installed in the driver</td></tr>\n<tr><td>Incorrect page orientation</td><td>Application or driver orientation setting</td></tr>\n<tr><td>Tray not recognised</td><td>Tray not installed in the driver’s device settings, or a misseated tray</td></tr>\n<tr><td>Multiple prints pending, frozen queue</td><td>Stuck job: clear the queue and restart the Print Spooler service</td></tr>\n<tr><td>Connectivity issues</td><td>Printer IP changed (use a reservation), offline status, Wi-Fi drop</td></tr>\n</tbody></table>\n' + str(worked('pages of random symbols', '''<ol>
<li>A new MFD prints pages of symbols for one user; others print normally.</li>
<li>The user’s PC has a PostScript driver installed by hand; the shared queue uses PCL. The data and the printer’s language do not match.</li>
<li>Remove the manual driver, connect to the shared queue from the print server, delete the stuck jobs and print a test page.</li></ol>''')) + '\n' + str(scenario('the payslips in the tray', '''<p>HR prints payslips to the shared multifunction printer, and on two occasions someone else picked them up
from the output tray. The fix is secured print release: jobs are held on the device until the owner authenticates with a PIN
or badge. HR is also given its own print queue so the setting can be enforced for that department.</p>''')) + '\n' + str(cfu(('Why can the wrong driver produce garbled print?', 'The driver speaks a different page-description language (PCL vs PostScript) from the one the printer expects.'),
     ('What does a secured print (PIN release) prevent?', 'Confidential pages being left in the output tray — the job prints only when the user is there.'),
     ('Which consumable does an impact printer use instead of toner or ink?', 'A ribbon.'))) + '\n')

HTML_STORAGE = ('\n<h4>Storage symptoms (Core 1 5.2)</h4>\n<ul>\n<li><strong>Grinding or clicking</strong> from a hard drive is mechanical failure in progress: stop non-essential use and back up\n<em>first</em>; every extra hour of running risks the data.</li>\n<li><strong>Extended read/write times</strong> and <strong>low IOPS</strong> — a nearly full or failing drive, an HDD instead of an SSD\nfor the workload, a failing cable, or a RAID array rebuilding.</li>\n<li><strong>S.M.A.R.T. failure</strong> warnings and Windows “storage device” health warnings — replace the drive after backing up.</li>\n<li><strong>Array missing</strong> — the RAID controller or its configuration is not seen: check the controller in firmware, cables,\nand whether a drive failed; do <em>not</em> initialise or recreate the array, which can destroy the data.</li>\n<li><strong>Drive not recognised / boot failures / BSOD on access</strong> — check power and data cables, firmware detection and the\nstorage-controller mode (AHCI vs RAID/VMD) before replacing.</li>\n<li><strong>Status LEDs</strong> on drive bays — an amber or flashing LED usually marks the failed member; check the vendor’s legend.</li>\n</ul>\n' + str(figure('fig-c-storagetriage', 'Triage for a storage symptom',
    ['Symptom:\nnoise, S.M.A.R.T., slow', 'Protect the data:\nback up first', 'Check cables and\nfirmware detection', 'Check controller\nmode and array', 'Replace, then\nrestore or rebuild'],
    'Five boxes in a chain. A storage symptom — grinding or clicking, a S.M.A.R.T. warning, slow reads and writes or a missing '
    'array — comes first. Second, protect the data by backing it up before anything else. Third, check power and data cables '
    'and whether the firmware detects the drive. Fourth, check the storage-controller mode and the RAID array status without '
    'initialising anything. Fifth, replace the failed part, then restore from backup or let the array rebuild.',
    'Back up before you troubleshoot a failing drive; never initialise an array you are diagnosing.', cols=5)) + '\n' + str(worked('a degraded mirror', '''<ol>
<li>A small server with RAID 1 shows an amber LED on one bay, and the controller reports the array as degraded.</li>
<li>The data is still readable from the other member, so confirm a current backup first.</li>
<li>Identify the failed drive from the controller and the bay LED; check the vendor’s LED legend.</li>
<li>Replace it with a drive of the same or larger capacity and the same interface.</li>
<li>Start or confirm the rebuild, watch it complete, and record the drive serial numbers on the ticket.</li></ol>''')) + '\n' + str(scenario('no boot device after a firmware update', '''<p>After a firmware (BIOS/UEFI) update, a desktop reports that no boot device was found, although the SSD
appears in the firmware’s storage list. The update had reset the storage-controller mode to a different setting from the one
Windows was installed with. Putting the setting back lets Windows boot. Replacing the drive would have wasted a part and the
user’s time.</p>''')) + '\n' + str(cfu(('A hard drive starts clicking. What is the first priority?', 'Back up the data immediately, then replace the drive.'),
     ('The RAID controller reports “array missing”. What must you avoid?', 'Initialising or recreating the array before investigating — it can destroy the data.'))) + '\n')

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 4, 'lesson': 3, 'id': 'cert-printers', 'title': 'Printer configuration, maintenance and print-defect diagnosis',
     'cert': ['A1:3.7', 'A1:3.8', 'A1:5.6'], 'html': sme_note('Printer deployment, maintenance and troubleshooting (Core 1 3.7, 3.8 and 5.6).') + HTML_PRINT, 'sources': ['ms-print']},
    {'course': 'ITSUP', 'chapter': 3, 'lesson': 2, 'id': 'cert-storage-symptoms', 'title': 'Storage and RAID symptoms',
     'cert': ['A1:5.2'], 'html': sme_note('Storage-drive and RAID symptoms (Core 1 5.2).') + HTML_STORAGE, 'sources': ['ms-storage']},
]

GLOSSARY = [
    ('PCL', 'Printer Command Language: a common page-description language for office printers.'),
    ('PostScript', 'Device-independent page-description language preferred for graphics and publishing.'),
    ('Secured print', 'A job held at the printer until the user releases it with a PIN or badge.'),
    ('Maintenance kit (laser)', 'Vendor kit of wear parts — typically the fuser and rollers — replaced at a set page count.'),
    ('IOPS', 'Input/output operations per second: a measure of storage performance.'),
]

ITEMS = [
    single('A1:5.6', 'IT-4.3', 1, 'A laser printer prints a faint copy of the previous page’s image lower down each new page. What is this defect called?',
           'Ghosting (double / echo image)',
           ['Speckling', 'Garbled print', 'Multipage misfeed (several sheets pulled)'],
           'A faint repeat of an earlier image is ghosting, typically from the drum or fuser.'),
    order('A1:5.6', 'IT-4.3', 2, 'Jobs are stuck in a Windows print queue and nothing prints. Put the fix in order.',
          ['Confirm the printer is online and has paper', 'Cancel the stuck jobs in the queue', 'Restart the Print Spooler service', 'Print a test page'],
          'Check the obvious first, clear the queue, restart the spooler, verify.'),
    multi('A1:5.6', 'IT-4.3', 3, 'A printer often pulls several sheets at once. Which TWO are the most likely causes? (Choose two.)',
          ['Worn pickup rollers or separation pad', 'Damp or wrong-weight paper'],
          ['A PostScript driver', 'Low toner', 'Incorrect page orientation'],
          'Multipage misfeeds come from the feed mechanism or the paper itself.'),
    single('A1:3.7', 'IT-4.3', 1, 'HR wants confidential payslips never to sit in the output tray. Which MFD feature should be enabled?',
           'Secured print release with a PIN or badge',
           ['Duplex printing by default', 'Scan to a network folder with user authentication', 'Draft quality mode'],
           'Secured prints hold the job until the user authenticates at the device.'),
    match('A1:3.7', 'IT-4.3', 2, 'Match each setting or feature to its purpose.',
          [('Duplex', 'Print on both sides of the sheet'), ('ADF', 'Scan a stack of multi-page originals'),
           ('Audit logs', 'Record who printed what and when'), ('PostScript driver', 'Device-independent output for graphics work')],
          'Configuration terms from Core 1 3.7.',
          decoys=['Fuser']),
    single('A1:3.7', 'IT-4.3', 3, 'A user’s documents print as pages of random symbols on a new printer; everyone else prints correctly. What is the most likely cause?',
           'The user has the wrong driver for the printer',
           ['The fuser is overheating', 'The pickup rollers are worn and feeding pages twice', 'The toner is low'],
           'Garbled output is a driver/page-description-language mismatch.'),
    single('A1:3.8', 'IT-4.3', 1, 'A laser printer shows “Perform printer maintenance” at 200,000 pages. What should the technician do?',
           'Install the maintenance kit and reset the counter',
           ['Replace only the toner cartridge', 'Reinstall the printer driver', 'Clean the fuser’s heating element with isopropyl alcohol'],
           'The page-count message calls for the vendor maintenance kit (fuser and rollers) and a counter reset.'),
    match('A1:3.8', 'IT-4.3', 2, 'Match each printer type to its main maintenance task.',
          [('Thermal', 'Clean the heating element and replace the paper roll'), ('Impact', 'Replace the ribbon'),
           ('Laser', 'Apply the maintenance kit at the page count'), ('Inkjet', 'Clean and align the printhead')],
          'Each printer technology has its own consumables and maintenance.',
          decoys=['Replace the PCL driver']),
    single('A1:3.8', 'IT-4.3', 3, 'Receipts from a thermal printer are coming out faint and patchy. What should the technician try first?',
           'Clean the heating element as the vendor directs',
           ['Replace the ribbon', 'Install a laser maintenance kit', 'Switch the printer driver to PostScript emulation'],
           'Thermal printers have no toner or ribbon; residue on the heating element causes faint output.'),
    single('A1:5.2', 'IT-3.1', 1, 'A user’s laptop hard drive has started making a clicking noise. What should the technician do first?',
           'Back up the user’s data immediately',
           ['Defragment the drive', 'Run a full surface scan overnight', 'Update the drive firmware'],
           'Clicking is mechanical failure in progress; protect the data before anything else stresses the drive.'),
    single('A1:5.2', 'IT-3.2', 2, 'After a power cut the server’s RAID controller reports “array missing”. What should the technician avoid?',
           'Initialising or recreating the array',
           ['Checking the controller in firmware', 'Inspecting drive cables and LEDs', 'Reading the controller event log'],
           'Recreating or initialising an array can destroy the data; investigate first.'),
    multi('A1:5.2', 'IT-3.2', 3, 'Which TWO symptoms most strongly suggest a failing storage drive? (Choose two.)',
          ['A S.M.A.R.T. failure warning', 'Grinding noises from the drive'],
          ['Faded laser printouts', 'A flickering monitor', 'A Bluetooth pairing failure'],
          'S.M.A.R.T. warnings and mechanical noises are classic drive-failure indicators.'),
]
