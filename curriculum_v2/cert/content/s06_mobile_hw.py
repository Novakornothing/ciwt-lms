"""A+ Core 1 1.2 (mobile accessories/connectivity), 1.3 (mobile network and app support) and 5.4 (mobile device issues) — ITSUP 4.1."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-bt-pair', 'Pairing a Bluetooth accessory',
    ['Turn on Bluetooth\non the phone', 'Put accessory in\npairing mode', 'Select it in the\nphone’s list', 'Confirm the code\nor PIN if asked', 'Test: sound,\ntyping, controls'],
    'Five boxes in order. Turn Bluetooth on in the phone settings; put the accessory into pairing (discoverable) mode '
    'following its manual; select the accessory when it appears in the phone’s list of devices; confirm the matching code '
    'or enter the PIN if one is requested; then test that the accessory actually works. If it fails, forget the device on '
    'the phone and repeat from the second step.',
    'If pairing fails: “forget” the device and start again from pairing mode — it is the accessory side that most often times out.', cols=5)

HTML = f'''
<h4>Accessories and connectivity (Core 1 1.2)</h4>
<ul>
<li><strong>Wired connectors:</strong> <strong>USB-C</strong> (reversible; now standard on most phones, tablets and laptops,
including iPhone from iPhone 15); <strong>Lightning</strong> (Apple’s earlier connector); <strong>micro-USB</strong> and
<strong>mini-USB</strong> on older or low-cost devices.</li>
<li><strong>Wireless:</strong> <strong>Bluetooth</strong> for headsets, speakers, keyboards and styluses;
<strong>NFC</strong> (near-field communication) for tap-to-pay and pairing at a range of a few centimetres;
<strong>hotspot / tethering</strong> to share the phone’s cellular data over Wi-Fi, USB or Bluetooth.</li>
<li><strong>Accessories:</strong> stylus, headsets, speakers, webcam, trackpad or drawing pad; a <strong>docking station</strong>
adds ports, charging and often display outputs through one cable, while a <strong>port replicator</strong> simply duplicates
the laptop’s ports.</li>
</ul>
{_FIG}
<h4>Network connectivity and application support (Core 1 1.3)</h4>
<ul>
<li><strong>Cellular (4G/LTE, 5G)</strong> and <strong>SIM / eSIM</strong> — an eSIM is a downloadable carrier profile rather
than a physical card; transferring it to a new phone is done through the carrier or the phone’s setup assistant.</li>
<li><strong>Hotspot</strong> and <strong>data caps</strong> — tethering counts against the plan; a user who runs out of data mid-month
may have left a hotspot or large sync running.</li>
<li><strong>Location services / GPS</strong> — needed by maps and some business apps; permission is set per app.</li>
<li><strong>MDM</strong> (mobile device management) enrols corporate and <strong>BYOD</strong> devices so the organisation can
push <strong>corporate applications</strong>, Wi-Fi and mail profiles, and enforce <strong>policies</strong> such as a passcode,
encryption and OS version; on BYOD the work data is usually kept in a separate managed container or profile.</li>
<li><strong>Synchronization</strong> of mail, calendar and contacts — usually from the organisation’s cloud mail service;
missing calendar items are often a sync account turned off on the phone.</li>
</ul>
<h4>Mobile hardware symptoms (Core 1 5.4)</h4>
<table class="ref-table"><thead><tr><th scope="col">Symptom</th><th scope="col">First action</th></tr></thead><tbody>
<tr><td><strong>Swollen battery</strong> (case bulging, screen lifting)</td><td>Stop using and do not charge it; do not puncture or press it; replace the battery and recycle it through a battery collection point, never household waste.</td></tr>
<tr><td>Poor battery health, short battery life</td><td>Check battery health and per-app battery usage before replacing.</td></tr>
<tr><td>Improper charging</td><td>Try a known-good cable and charger; inspect the charging port for lint or damage.</td></tr>
<tr><td>Liquid damage</td><td>Power off, do not charge, dry and refer for repair; check liquid-contact indicators.</td></tr>
<tr><td>Overheating</td><td>Remove from heat and case; check for a runaway app; stop charging until cool.</td></tr>
<tr><td>Broken screen, digitizer issues, ghost touches or cursor drift</td><td>Clean the screen and remove the protector; restart; recalibrate if the OS offers it; replace the screen/digitizer assembly if it persists.</td></tr>
<tr><td>Stylus does not work</td><td>Charge or replace its battery, re-pair it, and check it is supported by that model.</td></tr>
<tr><td>Poor or no connectivity, unable to install apps, degraded performance, malware</td><td>See Core 2 3.2–3.3 in lesson 4.2: radios and network settings, storage, OS version, and security symptoms.</td></tr>
</tbody></table>
{worked('a tablet that will not charge', '''<ol>
<li>Tablet shows no charging icon. Known-good USB-C cable and charger: still nothing.</li>
<li>Torch into the port: compacted lint. Power off, remove it carefully with a non-conductive tool.</li>
<li>Reconnect: charging resumes. Note it on the ticket and suggest a case with a port cover.</li></ol>''')}
{scenario('the bulging phone', '''<p>A user hands in a phone whose screen has lifted on one side. That is a swollen lithium-ion battery. You do not
power it on to “check”, do not charge it and do not press the screen down. You place it in a fire-safe container away from
combustibles, log it, and follow the shop’s battery-handling procedure: the battery is replaced by a trained technician and
the old one goes to battery recycling, not the bin.</p>''')}
{cfu(('Docking station or port replicator — which typically adds charging and display outputs through one cable?', 'A docking station.'),
     ('What is an eSIM?', 'A downloadable carrier profile stored in the phone, used instead of a physical SIM card.'),
     ('A phone’s screen is lifting at the edge. What do you do first?', 'Stop using and charging it — it is a swollen battery; handle and dispose of it as hazardous.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 4, 'lesson': 1, 'id': 'cert-mobile-hw',
    'title': 'Mobile accessories, connectivity, MDM and mobile hardware troubleshooting',
    'cert': ['A1:1.2', 'A1:1.3', 'A1:5.4'],
    'html': sme_note('Mobile accessories and connectivity, mobile network/app support and mobile hardware symptoms (Core 1 1.2, 1.3, 5.4).') + HTML,
    'sources': ['apple-btpair', 'nist-800124r2', 'epa-liion'],
}]

GLOSSARY = [
    ('eSIM', 'An embedded SIM: a downloadable carrier profile stored in the device instead of a physical SIM card.'),
    ('NFC', 'Near-field communication: very short-range radio used for contactless payment and quick pairing.'),
    ('Tethering', 'Sharing a phone’s cellular data connection with another device over Wi-Fi, USB or Bluetooth.'),
    ('Port replicator', 'A device that duplicates a laptop’s ports; simpler than a docking station.'),
    ('Swollen battery', 'A lithium-ion battery that has expanded from gas build-up; a fire risk that must not be charged or punctured.'),
]

ITEMS = [
    order('A1:1.2', 'IT-4.1', 1, 'Put the steps for pairing a new Bluetooth headset with a phone in order.',
          ['Turn on Bluetooth on the phone', 'Put the headset in pairing mode', 'Select the headset in the phone’s list',
           'Confirm the pairing code if asked', 'Play audio to test the headset'],
          'Enable the radio, make the accessory discoverable, select it, confirm the code, then verify.'),
    match('A1:1.2', 'IT-4.1', 2, 'Match each need to the best connectivity option.',
          [('Pay at a till by tapping the phone', 'NFC'), ('Share the phone’s 5G data with a laptop', 'Hotspot / tethering'),
           ('Wireless audio to a speaker across the room', 'Bluetooth'), ('One cable to charge and drive two monitors', 'USB-C docking station')],
          'NFC is centimetre-range tap; hotspots share cellular data; Bluetooth suits personal-area accessories; a dock adds power and displays through one cable.',
          decoys=['Micro-USB']),
    single('A1:1.2', 'IT-4.1', 3, 'A user wants one connection that gives a laptop power, Ethernet and two external displays at the desk. What should you recommend?',
           'A docking station on the laptop’s USB-C port',
           ['A port replicator with no charging support', 'A Bluetooth adapter for the monitors', 'An NFC reader at the desk'],
           'Docking stations add charging and display outputs through one cable.'),
    single('A1:1.2', 'IT-4.1', 4, 'A replacement charger will not fit a user’s 2019 iPhone, which charges through a small, flat, reversible connector that is not USB-C. Which connector does the phone use?',
           'Lightning',
           ['Micro-USB', 'Mini-USB', 'USB-B'],
           'Apple used Lightning before moving iPhone to USB-C with iPhone 15.'),
    single('A1:1.3', 'IT-4.2', 1, 'A user’s work calendar stopped appearing on her phone; mail still arrives. What should be checked first?',
           'Whether calendar sync is turned on for that account',
           ['Whether the eSIM profile has expired', 'Whether location services are enabled', 'Whether the hotspot is turned on'],
           'Mail, calendar and contacts sync are switched on per account; mail working proves the account itself is fine.'),
    multi('A1:1.3', 'IT-4.2', 2, 'Which TWO can an MDM policy typically enforce on an enrolled corporate phone? (Choose two.)',
          ['A minimum passcode requirement', 'Installation of required corporate apps'],
          ['The user’s cellular data cap', 'The carrier’s 5G coverage area', 'The phone’s battery health percentage'],
          'MDM pushes apps and configuration and enforces policies such as passcodes; it cannot change carrier coverage, plans or battery chemistry.'),
    single('A1:1.3', 'IT-4.2', 3, 'A user ran out of mobile data in the first week of the month. Usage shows most of it went to “Personal Hotspot”. What is the cause?',
           'Tethered devices used the phone’s data plan',
           ['GPS location services left running', 'An NFC payment app syncing receipts', 'A Bluetooth headset streaming audio'],
           'Hotspot traffic counts against the plan’s data cap.'),
    single('A1:1.3', 'IT-4.2', 4, 'A user is moving to a new phone and has an eSIM rather than a physical SIM. How is the line moved?',
           'Transfer the eSIM profile through the carrier or the setup assistant',
           ['Remove the SIM tray and move the card to the new phone', 'Copy the SIM from a Bluetooth backup', 'Pair the phones with NFC to clone the IMEI'],
           'An eSIM is a downloadable profile, so it is transferred or reissued, not physically moved.'),
    single('A1:5.4', 'IT-4.1', 2, 'A phone’s screen is lifting away from the frame on one side. What should the technician do first?',
           'Stop using and charging it and isolate it safely',
           ['Press the screen back in and apply adhesive', 'Charge it fully to test the battery', 'Run a battery-calibration app overnight'],
           'A lifting screen indicates a swollen battery: a fire risk. Do not charge, press or puncture it; dispose of it through battery recycling.'),
    multi('A1:5.4', 'IT-4.1', 3, 'A tablet registers touches the user did not make. Which TWO steps should come first? (Choose two.)',
          ['Clean the screen and remove the protector', 'Restart the tablet'],
          ['Replace the battery', 'Factory-reset the tablet', 'Replace the digitizer immediately'],
          'Ghost touches often come from dirt, moisture or a lifted protector; try the non-destructive steps before replacing parts.'),
]
