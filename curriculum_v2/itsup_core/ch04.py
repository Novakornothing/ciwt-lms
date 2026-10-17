"""ITSUP Chapter 4 — Mobile Devices & Printing (pass 10 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 4
SOURCES_USED = ['usbif-naming', 'epa-liion', 'ms-intune-actions', 'apple-deploy', 'ms-print', 'ietf-ipp']

_NOTE = 'Core content added in pass 10.'

LESSONS = {
    (4, 1): {
        'objectives': [
            'Identify a laptop’s field-replaceable units from the service manual and service tag before ordering parts',
            'Apply the power-down sequence and the stop rules for swollen, hot or damaged lithium-ion batteries',
            'Read a Windows battery report and compare design capacity with full-charge capacity',
            'Verify that a replacement charger and cable can deliver the wattage the laptop expects',
        ],
        'html': sme_note(_NOTE) + '''
<h3>What “field-replaceable” really means</h3>
<p>A <strong>field-replaceable unit (FRU)</strong> is a part the manufacturer expects a trained technician to swap on site with
ordinary tools. Which parts count depends on the model, not on how the laptop looks. Before you open anything, look up the
<strong>service manual</strong> for that exact model and the parts list for its <strong>service tag</strong> (or serial number):
the same product name can ship with different panels, keyboards and batteries in different years.</p>
''' + table(['Part', 'Often a FRU?', 'What to check before ordering'], [
            ['M.2 SSD', 'Usually, behind a door or the bottom cover', 'Length (2230/2242/2280), key and SATA or NVMe — Chapter 3.1'],
            ['Memory (RAM)', 'Sometimes; many thin laptops solder it to the board', 'Whether there is a SO-DIMM slot at all, type (DDR4/DDR5) and speed'],
            ['Battery', 'Internal on most current models; screwed or glued in', 'Exact part number; whether the manual allows field replacement'],
            ['Keyboard', 'Varies: a separate part or riveted to the palm rest', 'Layout (country) and whether the whole top cover is the FRU'],
            ['Display panel', 'Yes, but by panel code', 'Resolution, touch or non-touch, connector — never “a 15-inch screen”'],
            ['AC adapter / USB-C charger', 'Yes', 'Wattage, connector, and for USB-C the Power Delivery profile'],
            ['Wi-Fi card', 'On some models (M.2 2230); soldered on others', 'Antenna connectors, and whether firmware allows other cards'],
        ]) + '''
<h3>Power-down sequence</h3>
<ol>
<li>Back up or confirm the user’s data is synced, and record the service tag, symptoms and BitLocker recovery status (Chapter 2).</li>
<li>Shut down fully (not sleep). Unplug the charger and any dock.</li>
<li>Remove a removable battery if the model has one; on internal-battery models, follow the manual’s step to disconnect the battery
cable <em>first</em> after opening the cover. Some manuals add a “battery disconnect” or “ship mode” step in firmware.</li>
<li>Use ESD precautions (Chapter 1.2), keep screws in order — laptop screws are often different lengths, and a long screw in the wrong
hole can punch through the board.</li>
</ol>
<h3>Lithium-ion batteries: when to stop</h3>
<p>A lithium-ion battery that is <strong>swollen</strong> (trackpad lifted, bottom cover bulging, keyboard pushed up), <strong>hot</strong>
when the laptop is off, <strong>punctured</strong> or <strong>smells</strong> sweet or chemical is a safety incident, not a repair.
Stop using and charging the device, do not press, pry or puncture the pack, move it away from anything flammable if you can do so
safely, and follow your shop’s battery procedure. Used and damaged lithium-ion batteries do <strong>not</strong> go in household
trash or ordinary recycling: the U.S. EPA advises taking them to a battery or household-hazardous-waste collection point, with the
terminals taped or the battery in its own plastic bag.</p>
<h3>Battery wear and chargers</h3>
<p>“The battery dies by lunch” is often wear, not a fault. In Windows, <code>powercfg /batteryreport</code> writes an HTML report
(by default <code>battery-report.html</code> in the current folder) that lists <strong>design capacity</strong> and <strong>full charge
capacity</strong> and the history of each. A battery whose full-charge capacity is far below design capacity holds proportionally less.
Record both numbers in the ticket.</p>
<p>USB-C laptops charge with <strong>USB Power Delivery (PD)</strong>: the charger and laptop negotiate a voltage and current. Standard
PD reaches 100 W (20 V at 5 A); <strong>Extended Power Range</strong> reaches 240 W (48 V at 5 A) and needs a cable rated for it.
Currents above 3 A need a cable marked for 5 A. A 45 W phone charger can keep a 100 W laptop alive when idle and still let the battery
drain under load — the symptom is “slow and not charging”, and the charger label is the evidence.</p>
''' + worked('the battery that “stopped charging”', '''
<p>Ticket: “Laptop says plugged in, not charging.” The technician reads the charger label (USB-C, 45 W) and the laptop’s specification
(65 W adapter supplied). <code>powercfg /batteryreport</code> shows design capacity 54,000 mWh, full charge 51,300 mWh — healthy. Swapping in
the 65 W adapter from stock, the battery charges. The note: “Charger 45 W (not original); laptop expects 65 W. Battery 95 % of design. Swapped to
65 W adapter → charging. User’s 45 W phone charger returned to user.”</p>''') + scenario('the raised trackpad', '''
<p>A user drops off a laptop because “the trackpad clicks by itself”. The trackpad sits visibly higher at the front and the bottom
cover rocks on the desk. The technician does not open the case or charge it. They tell the user it may be a swollen battery and must
not be used, place it on a non-flammable surface in the designated area, tag it “Swollen battery — do not charge”, and open a ticket
under the battery procedure with the service tag so the depot or vendor can replace it. The user gets a loaner the same hour.</p>''') + cfu(
            ('Why is “a 15-inch screen for a Dell Latitude” not enough to order a panel?',
             'Panels differ by resolution, touch, connector and year. You need the panel code or the parts list for that service tag.'),
            ('A laptop’s trackpad is lifted and the case bulges. What do you do first?',
             'Stop: do not use, charge, press or open it. Treat it as a swollen battery and follow the battery procedure.'),
            ('Which two numbers from the battery report show wear?',
             'Design capacity and full charge capacity; the closer full charge is to design, the healthier the battery.')),
        'sources': ['epa-liion', 'usbif-naming'],
    },
    (4, 2): {
        'objectives': [
            'Isolate a phone or tablet connectivity fault to Wi-Fi, cellular data, VPN or the account',
            'Distinguish an Intune retire from a wipe and decide which one a ticket actually asks for',
            'Explain why Activation Lock and Factory Reset Protection make an unauthorised reset useless',
            'Route a non-compliant managed device to the policy owner instead of bypassing the policy',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Which path is failing?</h3>
<p>A phone has three ways out: <strong>Wi-Fi</strong>, <strong>cellular data</strong> and, on top of either, a <strong>VPN</strong> or
per-app tunnel. “Mail doesn’t work” is a symptom; the first test is which path the device is using and whether the other path works.</p>
''' + table(['Check', 'What it tells you', 'Next step if it fails'], [
            ['Toggle Wi-Fi off: does mail sync on cellular?', 'Whether the device and account work at all', 'If yes, the building Wi-Fi path is the suspect (captive portal, proxy, filtering)'],
            ['Settings → Wi-Fi → the network’s details', 'IP address, router, DNS — the same fields as ipconfig (Chapter 5)', '169.254 or no address: DHCP/association, not the app'],
            ['Cellular: SIM or eSIM present, data on, roaming as policy allows', 'Whether the carrier path is up', 'Carrier outage or plan; the APN setting if your carrier requires a custom one'],
            ['VPN status / per-app VPN profile', 'Whether work apps are forced through a tunnel', 'VPN service owner, with the error text'],
            ['Account banner in the work app or Company Portal', 'Sign-in, MFA or compliance problems', 'Identity or MDM owner'],
        ]) + '''
<p>Two settings regularly confuse technicians. An <strong>eSIM</strong> is a carrier profile downloaded into the phone instead of a
plastic card; deleting it in Settings can mean asking the carrier for a new one. The <strong>APN</strong> (Access Point Name) tells the
phone how to reach the carrier’s data network; most carriers set it automatically, and changing it by hand without the carrier’s values
breaks data. Phones also use a <strong>private (randomised) Wi-Fi address</strong> per network by default; that can defeat a DHCP
reservation or a MAC allow-list, and on corporate networks your shop decides whether it should be turned off for that SSID.</p>
<h3>Managed devices: retire, wipe, lock</h3>
<p>A device enrolled in <strong>mobile device management (MDM)</strong>, such as Microsoft Intune, belongs to a policy, and only the
policy owner changes it. Know what the remote actions do, because the wrong one destroys someone’s data:</p>
''' + table(['Action', 'What it removes', 'Typical use'], [
            ['Retire', 'Company data, managed apps, email and Wi-Fi/VPN profiles the MDM pushed; personal data stays', 'A personal phone leaving the program; an employee leaving'],
            ['Wipe', 'Everything — a factory reset (some platforms can keep enrolment)', 'A company-owned device that is lost, stolen or being reissued'],
            ['Remote lock / passcode reset', 'Nothing; it locks the device or resets the passcode', 'Lost device; user locked out'],
        ]) + '''
<p>A <strong>compliance policy</strong> decides whether a device may reach company resources: for example a minimum OS version, a
passcode, encryption, or “not jailbroken/rooted”. A non-compliant device is blocked by design. The fix is to bring the device into line
(update the OS, set a passcode) or ask the policy owner for an exception — never to remove the profile so “Outlook just works”.</p>
<h3>Why resetting a phone is not a fix</h3>
<p>Apple’s <strong>Activation Lock</strong> ties an iPhone or iPad to the owner’s Apple Account when Find My is on: after an erase, the
device asks for that account before it can be used. Organisations that supervise their devices can clear it through their MDM. Android’s
<strong>Factory Reset Protection</strong> does the same with the Google account. A technician who factory-resets a device without the
owner or the MDM has not fixed anything — they have produced a locked brick and erased the user’s data.</p>
''' + figure('f4-2', 'Managed phone: which action fits the ticket', ['Ticket\nreceived', 'Company- or\nuser-owned?', 'Lost or\nstolen?', 'Retire\n(user-owned)', 'Wipe\n(company, lost)', 'Fix compliance\nor escalate'],
             'Six boxes. Start from the ticket and ask whether the device is company-owned or user-owned, and whether it is lost or stolen. '
             'A user-owned device leaving the program is retired, which removes only company data. A lost company-owned device is wiped by the '
             'MDM owner. A device that is merely blocked as non-compliant is fixed (update, passcode) or escalated, not reset.',
             'Pick the remote action by ownership and situation; a compliance block is fixed, not wiped.', cols=3) + worked('mail fails only in the office', '''
<p>Ticket: “Outlook on my phone stopped syncing.” The technician asks the user to turn Wi-Fi off: mail syncs on cellular within a
minute. On the office SSID the phone shows an address from the guest range, not the staff range — it joined the guest network, which
blocks the mail service. Rejoining the staff SSID fixes it. Note: “Phone on guest SSID (10.50.x). Mail OK on cellular. Moved to staff
SSID → syncs. No reset, no profile change.”</p>''') + cfu(
            ('A user’s personal phone is leaving the BYOD program. Retire or wipe?',
             'Retire: it removes company apps, data and profiles and leaves personal data. Wipe would erase the user’s phone.'),
            ('A phone is blocked because its OS is out of date. Should you remove the management profile?',
             'No. Update the OS (or ask the policy owner about an exception). Removing the profile bypasses policy and loses access anyway.'),
            ('Why does factory-resetting a found iPhone not let you reissue it?',
             'Activation Lock still asks for the owner’s Apple Account after the erase, unless the organisation’s MDM clears it.')),
        'sources': ['ms-intune-actions', 'apple-deploy'],
    },
    (4, 3): {
        'objectives': [
            'Isolate a printing fault to the application, spooler, driver, port, network or device by scope',
            'Resolve a stuck Windows print queue by stopping the Print Spooler, clearing it and restarting it',
            'Identify the port and protocol a network printer uses (IPP 631, raw 9100, LPD 515)',
            'Diagnose common laser-printer output defects from the symptom on the page',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Scope first, then the path</h3>
<p>The print path is: <strong>application → Windows print system (spooler and queue) → driver → port (USB or network) → device</strong>.
Scope tells you where to start (Chapter 1’s one-or-many question): one app on one PC points at the app or its print dialog; every app on
one PC points at the spooler, queue or driver on that PC; every PC points at the printer, the print server or the network path to it.</p>
''' + figure('f4-3', 'The print path and where scope points', ['Application', 'Spooler and\nqueue', 'Driver', 'Port: USB\nor network', 'Printer\n(panel)'],
             'Five boxes in a row: the application hands the job to the Windows spooler and its queue, the driver turns it into the printer’s '
             'language, the port carries it over USB or the network, and the printer prints it. One app failing points at the first box; one PC '
             'with every app failing points at the middle boxes; every PC failing points at the last two boxes or the print server.',
             'Work along the path from the end the scope points at; the next desk that prints fine is your control.', cols=5) + '''
<h3>The stuck queue</h3>
<p>A job that will not delete, and blocks everything behind it, usually means the spooler is holding a damaged spool file. The
supported fix on the affected PC (as an administrator):</p>
<ol>
<li>Stop the <strong>Print Spooler</strong> service (Services, or <code>net stop spooler</code>).</li>
<li>Delete the files in <code>C:\\Windows\\System32\\spool\\PRINTERS</code> — the folder, not the folder above it. These are the
queued jobs, so tell the user their pending prints will be gone.</li>
<li>Start the service again (<code>net start spooler</code>) and print a test page.</li>
</ol>
<p>Windows’ own troubleshooter (Settings → Bluetooth &amp; devices → Printers &amp; scanners → the printer → <em>Run the troubleshooter</em>)
performs similar checks. If the queue fills again immediately, the driver or the job is the cause; reinstall the driver from the printer
vendor or use the built-in class driver.</p>
<h3>How the PC reaches a network printer</h3>
''' + table(['Port / protocol', 'Number', 'Notes'], [
            ['IPP / IPPS (Internet Printing Protocol)', 'TCP 631', 'Modern standard; used by driverless (Mopria / AirPrint-style) printing and by Windows protected print mode'],
            ['Raw / AppSocket (often called JetDirect)', 'TCP 9100', 'Common “Standard TCP/IP port” in Windows; sends the job straight to the printer'],
            ['LPD/LPR', 'TCP 515', 'Older Unix-style protocol, still offered by many printers'],
            ['SMB to a print server', 'TCP 445', 'Shared queues on a Windows print server (\\\\server\\queue)'],
        ]) + '''
<p>With the scope known, test the layer: can the PC reach the printer’s address (<code>ping</code>, the printer’s web page,
<code>Test-NetConnection printer -Port 9100</code>)? Has the printer’s address changed because it lost a DHCP reservation? Windows 11 also offers
<strong>Windows protected print mode</strong>, which uses only the built-in IPP-based print stack and blocks third-party drivers; with it
on, an old printer that needs a vendor driver will not install, by design.</p>
<h3>Reading the page (laser printers)</h3>
<p>A laser printer charges a drum, writes the image on it with a laser, develops it with toner, transfers the toner to the paper and
<strong>fuses</strong> it with heat and pressure, then cleans the drum. Output defects point at a stage:</p>
''' + table(['Symptom on the page', 'Likely stage', 'First action'], [
            ['Toner smears or rubs off with a finger', 'Fusing', 'Fuser unit (often a maintenance-kit part); check the paper type setting'],
            ['Repeating mark at a regular interval down the page', 'A roller or the drum — the interval matches its circumference', 'Measure the interval; compare with the vendor’s defect ruler'],
            ['Faint image of an earlier part of the page (ghosting)', 'Drum or cleaning', 'Replace the toner/drum unit as the vendor directs'],
            ['Vertical line or streak in the same place', 'Drum scratch or dirty corona/laser window', 'Replace drum/toner cartridge; clean as the manual allows'],
            ['Blank page', 'No toner, a sealing tape left on, or transfer failure', 'Check the cartridge first'],
        ]) + '''
<p>Fusers run hot: let the printer cool before reaching in, and follow the manual’s jam-clearing steps. For inkjets, the equivalents are
clogged nozzles (missing lines — run the cleaning cycle) and misalignment (run alignment).</p>
''' + scenario('the floor that cannot print', '''
<p>At 09:10, three tickets arrive from the same floor: “printer offline.” The technician does not touch the first PC. The printer’s panel is
lit and shows no error, but its network page will not load and <code>ping</code> to its address fails; a colleague’s PC on the same switch
reaches other devices. At the printer, the panel shows a new IP address — the printer lost its DHCP reservation after a router change. The
technician restores the reservation through the network owner, the printer returns to its old address, and every queue recovers without a
single driver reinstall. The note records the address change and asks the network owner to confirm the reservation is permanent.</p>''') + cfu(
            ('Every app on one PC fails to print while the next desk prints fine. Where do you start?',
             'That PC’s spooler, queue and driver. The next desk proves the printer and network path work.'),
            ('What must you do before deleting files in the spool PRINTERS folder?',
             'Stop the Print Spooler service (and warn the user that queued jobs will be lost); start it again afterwards.'),
            ('Toner rubs off the page with a finger. Which stage do you suspect?',
             'Fusing: the toner was not melted onto the paper. Check the fuser and the paper-type setting.')),
        'sources': ['ms-print', 'ietf-ipp'],
    },
    (4, 4): {
        'objectives': [
            'Classify a portable-device or print ticket and decide whether it is a safety stop',
            'Write an intake note that names the FRU, the managed-device action or the print-path link to touch next',
            'Route a managed-device or shared-printer change to its owner with evidence',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Capstone: three portable tickets</h3>
<p>Use the Chapter 1 intake structure (classify → impact → escalate → note) on each ticket. Every note must let a colleague pick it up
without asking you a question.</p>
''' + table(['Ticket', 'Classify', 'First evidence', 'Owner of the change'], [
            ['“My laptop’s case is bulging and it’s warm when off.”', 'Safety stop (swollen battery)', 'Photo, service tag, “do not charge” tag', 'Battery procedure / depot'],
            ['“My phone won’t get work email since the update.”', 'Managed device — compliance or account', 'Company Portal / compliance message; does mail work on cellular?', 'User (update), MDM owner (policy)'],
            ['“Nobody on floor 2 can print.”', 'Shared device, many users', 'Printer panel state, ping/web page, one PC’s queue status', 'Print server or network owner'],
        ]) + worked('three notes that pass', '''
<p><strong>Battery:</strong> “Latitude, tag 7XQ2…; trackpad lifted ~2 mm, warm when off. Not opened, not charged. Isolated on the battery
shelf, tagged. Loaner issued. Next: depot battery replacement under the battery procedure.”</p>
<p><strong>Phone:</strong> “iPhone, company-owned. Company Portal: ‘OS version below minimum’. Mail fails on Wi-Fi and cellular. User updated
iOS 17 → current at desk; device re-checked compliant after ~15 min; mail syncs. No profile removed.”</p>
<p><strong>Printer:</strong> “Floor 2 MFP: panel OK, no jam; ping 10.20.40.25 fails from three PCs; panel shows 10.20.40.131. Reservation
missing. Escalated to network owner to restore reservation 10.20.40.25; queues left untouched.”</p>''') + '''
<h3>Pass bar</h3>
<ul>
<li>The battery ticket stops work and never includes “opened to check”.</li>
<li>The phone note names the compliance message and the remote action (if any) and who approved it; nobody wiped or removed a profile
to make it work.</li>
<li>The print note names the link in the print path, the evidence, and the owner — and does not reinstall a driver on a floor-wide
outage.</li>
</ul>
''' + cfu(
            ('What makes the battery ticket different from the other two?',
             'It is a safety stop: the device is isolated and not used, charged or opened, before any troubleshooting.'),
            ('Why does the printer note leave the PCs’ queues untouched?',
             'Scope (a whole floor) points at the shared device or network path; changing each PC would add changes without fixing the cause.')),
        'sources': ['epa-liion', 'ms-intune-actions', 'ms-print'],
    },
}

GLOSSARY = [
    ('Field-replaceable unit (FRU)', 'A part the manufacturer expects a trained technician to replace on site, identified by the service manual and the service tag.'),
    ('Battery report', 'The HTML report from powercfg /batteryreport listing a laptop battery’s design capacity, full charge capacity and usage history.'),
    ('Extended Power Range (EPR)', 'The USB Power Delivery range above 100 W, up to 240 W at 48 V, which needs an EPR-rated 5 A cable.'),
    ('eSIM', 'A carrier profile downloaded into a phone’s embedded SIM instead of a removable card.'),
    ('APN', 'Access Point Name: the setting a phone uses to reach its carrier’s data network; normally provided by the carrier.'),
    ('Private Wi-Fi address', 'A randomised hardware (MAC) address a device uses per network to limit tracking; it can defeat DHCP reservations and MAC allow-lists.'),
    ('Retire (MDM)', 'A remote action that removes company apps, data and profiles from an enrolled device and leaves personal data in place.'),
    ('Compliance policy', 'MDM rules (OS version, passcode, encryption, not jailbroken) that decide whether a device may reach company resources.'),
    ('Activation Lock', 'Apple’s Find My protection that requires the owner’s Apple Account after an erase; supervised devices can have it cleared through MDM.'),
    ('Factory Reset Protection', 'Android’s protection that asks for the previous Google account after an unauthorised factory reset.'),
    ('Print Spooler', 'The Windows service that queues print jobs; stopping it allows stuck jobs to be cleared from the spool PRINTERS folder.'),
    ('IPP', 'Internet Printing Protocol (TCP 631, IPPS over TLS): the modern network printing standard used by driverless printing.'),
    ('Fuser', 'The heated laser-printer assembly that melts toner onto paper; toner that rubs off points at it.'),
    ('Windows protected print mode', 'A Windows 11 setting that allows only the built-in IPP-based print stack and blocks third-party print drivers.'),
]

PLAN = {
    'warmup': 'Show two photos of the same laptop model from different years with different panel codes. Pairs list what they would need to order a screen.',
    'guided': 'Read a battery report and a charger label together (4.1); walk the retire/wipe table with three ownership stories (4.2); trace the print path on the board, then clear a stuck queue on a bench PC (4.3).',
    'worked_example': 'Lesson 4.1 “not charging”; 4.2 mail fails only in the office; 4.4 the three passing notes.',
    'cfu': ['Swollen battery: first three actions?',
            'BYOD phone leaving: retire or wipe?',
            'One PC, every app fails to print: where do you start?',
            'Toner rubs off: which stage?'],
    'exit_ticket': 'Write the one-line note for “nobody on floor 2 can print” after finding the printer on a new IP address.',
    'misconceptions_add': ['“Factory reset fixes a managed phone.” It erases data and leaves Activation Lock or FRP in place; the MDM owner decides.',
                           '“Any USB-C charger works.” Wattage and the PD profile decide; a low-watt charger drains under load.',
                           '“Reinstall the driver” on a floor-wide print outage. Scope points at the shared printer or path.'],
    'classroom_lab': '',
    'materials_add': 'A training laptop with its service manual; a 45 W and a 65 W USB-C charger; printed defect samples (smear, repeating mark, ghost); a bench PC with a test printer queue.',
}

ITEMS = [
    item('IT-4.1', 1, 'A laptop’s trackpad is lifted and the case bulges. What should the technician do first?',
         'Stop using and charging it and isolate it', ['Open the case to check the battery connector', 'Run a full battery report in Windows first', 'Press the trackpad back down firmly'],
         'Swelling is a lithium-ion safety stop: no use, charging, pressing or opening; follow the battery procedure.'),
    item('IT-4.1', 2, 'Which command shows a laptop battery’s design capacity and full charge capacity?',
         'powercfg /batteryreport', ['ipconfig /batteryinfo /all', 'chkdsk C: /battery', 'msinfo32 /report power'],
         'powercfg /batteryreport writes an HTML report with both capacities and their history.'),
    item('IT-4.1', 3, 'A 100 W USB-C laptop drains under load while plugged in. What is the most likely cause?',
         'The charger supplies too little power', ['The M.2 SSD is the wrong length for it', 'The Wi-Fi card is not supported', 'The display panel code does not match'],
         'A low-wattage USB-C charger can keep an idle laptop alive but not supply full load; read the charger label.'),
    item('IT-4.2', 1, 'A user-owned phone is leaving the company’s BYOD program. Which MDM action fits?',
         'Retire, keeping personal data', ['Full wipe to factory settings', 'Remote lock with a new passcode', 'Reset the phone’s APN values'],
         'Retire removes company apps, data and profiles but leaves personal data; wipe would erase the user’s phone.'),
    item('IT-4.2', 2, 'A managed phone is blocked because its OS is below the minimum version. What is the right fix?',
         'Update the OS and recheck compliance', ['Remove the management profile first', 'Factory reset the phone and re-enrol it', 'Disable the compliance policy for now'],
         'Bring the device into compliance or ask the policy owner; bypassing the policy is not the technician’s change to make.'),
    item('IT-4.2', 3, 'Mail syncs on cellular but not on the office Wi-Fi. What should you check next?',
         'Which SSID and address it has', ['The phone’s eSIM carrier profile', 'The battery report on the phone', 'The Activation Lock status'],
         'The device and account work; the building Wi-Fi path (wrong SSID, guest network, proxy) is the suspect.'),
    item('IT-4.3', 1, 'Every app on one PC fails to print while the next desk prints fine. Where do you start?',
         'That PC’s spooler, queue and driver', ['The printer’s fuser and drum units', 'The print server queue for the floor', 'The network switch serving the floor'],
         'The next desk proves the printer and path work, so the fault is on the failing PC.'),
    item('IT-4.3', 2, 'What must happen before deleting files in the spool PRINTERS folder?',
         'Stop the Print Spooler service', ['Uninstall every printer driver', 'Restart the printer at its panel', 'Turn off the Windows Firewall'],
         'The spooler holds the files open; stop it, delete the queued jobs, then start it again.'),
    item('IT-4.3', 3, 'Toner rubs off a laser printout with a finger. Which part is most likely at fault?',
         'The fuser assembly', ['The toner chip', 'The paper tray roller', 'The network port'],
         'The fuser melts toner onto the paper; loose toner means fusing failed (or the wrong paper type is set).'),
    item('IT-4.3', 4, 'Which TCP port does the Internet Printing Protocol use by default?',
         '631', ['9100', '515', '445'],
         'IPP uses TCP 631; 9100 is raw/AppSocket, 515 is LPD and 445 is SMB to a print server.'),
]
