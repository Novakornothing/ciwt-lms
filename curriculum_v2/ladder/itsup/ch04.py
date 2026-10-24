"""Explanation ladder — ITSUP chapter 4 (Laptops, Mobile and MDM, Printers, Portable Intake). Pending SME review.

Distinct concept sections are laddered; core-content and repeated sections that restate a core section of the same
lesson use same_as. Option B pass 2: those sections now have bespoke ladders (_p2cNN.py).
"""
from curriculum_v2.ladder.itsup._lk import M, P, X
from curriculum_v2.ladder.itsup._p2c04 import SECS as _P2
from curriculum_v2.ladder.schema import order, reveal, sort

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 4


def _s(n, t):
    return f'Course lesson 4.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4 = _s(1, 'Laptops and FRUs'), _s(2, 'Mobile Radios and MDM'), _s(3, 'Printers'), _s(4, 'Portable Intake Capstone')
_P = 'MC-L-IT4-'
MISCONCEPTIONS = {
    **M(_P, S1, {
        'BRICK': ('IT-4.1', 'Blaming Windows when a low-watt adapter throttles the laptop', 'Read both labels; the brick must match or exceed what the chassis expects.', ['adapter', 'watt']),
        'SWELL': ('IT-4.1', 'Pressing, prying or charging a swollen battery', 'Stop, do not charge, follow the battery procedure, write a stop ticket.', ['swollen', 'battery']),
        'GENERIC-PART': ('IT-4.1', 'Ordering by description instead of service tag and part code', 'Service tag plus part code; look-alike parts differ.', ['service tag', 'fru']),
        'NFC-RANGE': ('IT-4.1', 'Thinking NFC works across a room', 'NFC works at a few centimetres; Bluetooth covers metres.', ['nfc', 'bluetooth']),
    }),
    **M(_P, S2, {
        'PHONE-BROKEN': ('IT-4.2', 'Calling it a phone fault before testing the other path', 'Toggle Wi-Fi off: if cellular works, the building path is the suspect.', ['wi-fi', 'cellular']),
        'MDM-BYPASS': ('IT-4.2', 'Sidestepping or resetting MDM to install an app', 'MDM is the owner’s; open a request with the enrollment owner.', ['mdm', 'work profile']),
        'REINSTALL-FIRST': ('IT-4.2', 'Deleting an app before the safe steps', 'Close, restart, update, then reinstall; deleting can lose app data.', ['app', 'reinstall']),
    }),
    **M(_P, S3, {
        'FIRST-PC': ('IT-4.3', 'Rebuilding one PC’s driver when the whole floor cannot print', 'Many users: start at the device and print server.', ['print server', 'spooler']),
        'VAGUE-PRINT': ('IT-4.3', 'Writing “printer broken” as the note', 'Who, which PC, error text, queue, panel state.', ['queue', 'note']),
        'PCL-PS': ('IT-4.3', 'Ignoring the page-description language when print is garbled', 'Wrong PCL/PostScript driver prints pages of symbols.', ['pcl', 'postscript']),
    }),
    **M(_P, S4, {
        'NOTE-ASK': ('IT-4.1', 'Writing a note the next person must ask you about', 'Say stop, pull a driver or work the panel, with evidence.', ['note', 'intake']),
    }),
}
BRICK, SWELL, GEN, NFC, PB, MDM, REI, FPC, VP, PCL, ASK = (_P + k for k in (
    'BRICK', 'SWELL', 'GENERIC-PART', 'NFC-RANGE', 'PHONE-BROKEN', 'MDM-BYPASS', 'REINSTALL-FIRST', 'FIRST-PC', 'VAGUE-PRINT', 'PCL-PS', 'NOTE-ASK'))
LAP = ('win-laptop-ports', 'Read the adapter and chassis labels, then list the ports and what each one carries.')
MOB = ('mob-mdm', 'Check which path the device uses and who owns the enrollment before changing anything.')
PRN = ('print-trouble', 'Scope the print fault, then work app, spooler, driver, port and device in order.')
INT = ('ticket-intake', 'Classify, count impact, name the owner, then write a note a colleague can act on.')

LESSONS = {
    '4.1': {
        'start-here-a-laptop-is-still-a-computer': _P2[('4.1', 'start-here-a-laptop-is-still-a-computer')],
        'core-content': _P2[('4.1', 'core-content')],
        '1-power-first': X('1. Power first', 'IT-4.1', S1, [
            ('A 65 W brick on a 130 W laptop. Symptom?', 'Slow, throttled PC', 'Faster charging than usual', 'No effect at all on speed',
             'Too little power makes the laptop charge slowly and throttle, which looks like a slow CPU.', BRICK, BRICK),
            ('What do you write before blaming Windows?', 'Both label ratings', 'The Windows build number only', 'The user’s favourite apps',
             'Numbers from the brick and from the chassis prove or rule out a power mismatch.', BRICK, None),
            ('In the hosepipe story, why does a thin hose matter?', 'Not enough flow', 'The water turns cold', 'The tap breaks',
             'A thin hose feeds the garden slowly, like a small adapter feeds a hungry laptop.', BRICK, None),
            ('The adapter rating must…', 'Match or exceed', 'Be half the chassis', 'Be any USB brick',
             'Equal or higher wattage than the chassis expects.', BRICK, None),
            ('Which label do you read on the laptop?', 'The chassis input rating', 'The screen size sticker on the lid', 'The keyboard layout',
             'The chassis label says what power it expects.', BRICK, None),
        ],
            P('Every laptop expects a power adapter of a certain wattage. A weaker brick does not just charge slower. The laptop cuts its own speed to stay within the power it gets. Users then report a slow computer and blame Windows. Before touching software, read the wattage on the adapter and on the laptop label. Write both numbers on the ticket.'),
            P('Think of filling a paddling pool and running a sprinkler from one garden tap. With a thin hose, water trickles in, the pool takes all '
              'afternoon, and the sprinkler barely turns. Nothing is broken; the hose is simply too narrow for what you asked of it. Fit the right '
              'hose and both work properly. A laptop on a small brick is that thin hose.'),
            ['Read the brick wattage.', 'Read the chassis rating.', 'Compare them.', 'Mismatch? Fit the right brick and retest.', 'Only then look at Windows.'],
            '<p>Guess first, then reveal.</p>',
            reveal('A 130 W laptop feels slow only when unplugged from its dock’s 90 W supply. Why?', 'It is not; it feels slow on the dock, because 90 W is below the 130 W the chassis expects and it throttles.'), LAP),
        '2-what-you-may-open': X('2. What you may open', 'IT-4.1', S1, [
            ('The trackpad is lifting and the case is warm. Do what?', 'Stop and tag it', 'Press the case flat again', 'Keep charging it overnight',
             'A swollen battery is a safety stop: do not press, charge or pry it.', SWELL, SWELL),
            ('Where does a swollen battery go?', 'Shop battery procedure', 'The general office waste bin', 'A desk drawer',
             'Never household trash; follow the shop’s hazardous battery process.', SWELL, None),
            ('In the balloon story, why not squeeze?', 'It may burst', 'It shrinks back', 'It gets bigger slowly',
             'Pressure on a swollen lithium cell can make it vent or ignite.', SWELL, None),
            ('Which part is often behind a service door?', 'M.2 SSD', 'A sealed battery', 'The display panel',
             'M.2 and sometimes RAM sit behind a door covered by the service guide.', GEN, None),
            ('A sealed battery replacement goes to…', 'Shop procedure or depot', 'Any student with a screwdriver set', 'The user at home',
             'Sealed packs are a shop or vendor-depot job.', SWELL, None),
        ],
            P('Some laptop parts sit behind a small door or base plate. The service guide shows how to change them. Usually that is the SSD, sometimes memory. Batteries fixed inside follow the shop’s process or go to the maker’s depot. A swollen battery is a safety stop. Do not press on it or charge it. Never throw it away with ordinary rubbish.'),
            P('A swollen battery is like an over-inflated balloon with something flammable inside. Squeezing it to fit the case back together is the '
              'worst idea, and leaving it on charge pumps more air in. You set it down somewhere safe, label it so nobody else picks it up, and hand '
              'it to whoever is trained to dispose of it.'),
            ['Is there a service door?', 'Check the guide for that model.', 'M.2 or RAM: proceed.', 'Sealed battery: shop or depot.', 'Swollen: stop and tag.'],
            '<p>Sort each job.</p>',
            sort('May you open it?', {'Yes, with the guide': ['M.2 SSD behind door', 'SO-DIMM slot'], 'Shop or depot': ['Sealed battery'],
                                      'Stop now': ['Swollen pack', 'Warm bulging case']}, 'Safety beats speed.'), LAP),
        'fru-identity-and-batteries': X('FRU identity and batteries', 'IT-4.1', S1, [
            ('How do you order a laptop screen?', 'Service tag and panel code', 'Ask for a 15-inch screen for that brand', 'Use the photo the user sent you',
             'Look-alike panels differ; the tag and part code are exact.', GEN, GEN),
            ('A FRU is a part that…', 'A tech swaps on site', 'Only the factory can fit', 'Never fails in use',
             'Field-replaceable: swapped on site with ordinary tools, per the model.', GEN, None),
            ('In the key story, why the code not the look?', 'Look-alikes differ', 'Codes are prettier', 'Keys are all the same',
             'Two keys can look alike and still not turn the lock.', GEN, None),
            ('What decides whether RAM is a FRU?', 'The exact model', 'How thin it looks', 'The colour of the case',
             'Many thin laptops solder RAM; check the service manual.', GEN, None),
            ('Which document comes before opening?', 'Service manual', 'The sales brochure', 'A random forum post',
             'The service manual and parts list for that tag come first.', GEN, None),
        ],
            P('Laptop parts that look the same often are not. The same model name can ship with different screens, keyboards and batteries in '
              'different years. So order by the service tag and the part code, after checking the service manual for that exact model shows the '
              'part can be changed on site. Memory may be soldered on thin models, and batteries can be glued.'),
            P('Two house keys can look identical and still not open the same door, because the cuts differ by a fraction of a millimetre. You would '
              'not ask a locksmith for a silver key, about this long. You hand over the code stamped on it. A service tag and part code are that '
              'stamped code for laptop parts.'),
            ['Find the service tag.', 'Open the service manual.', 'Is the part a FRU here?', 'Get the exact part code.', 'Order and note it.'],
            '<p>Put the ordering steps in order.</p>',
            order('Order a laptop part', ['Read service tag', 'Open service manual', 'Confirm part is a FRU', 'Get exact part code', 'Order it'],
                  'Never order from a description.'), LAP),
        'mobile-accessories-connectivity-mdm-and-mobile-hardware-trou': X('Mobile accessories, connectivity, MDM and mobile hardware troubleshooting', 'IT-4.1', S1, [
            ('Tap-to-pay uses which link?', 'NFC', 'Bluetooth across the room', 'Wi-Fi Direct at long range',
             'NFC works at a few centimetres, which suits payment and pairing.', NFC, NFC),
            ('Sharing phone data with a laptop is…', 'Tethering', 'Port replication', 'Screen mirroring',
             'A hotspot or tether shares cellular data over Wi-Fi, USB or Bluetooth.', NFC, None),
            ('In the whisper story, why does NFC need closeness?', 'Very short range', 'It is very loud and carries far', 'It uses cables',
             'NFC is a whisper: only the device right next to you hears it.', NFC, None),
            ('A dock differs from a port replicator by…', 'Adding more features', 'Being smaller and cheaper', 'Using no cable at all',
             'A dock adds charging, ports and display; a replicator just copies ports.', NFC, None),
            ('A headset connects without wires over…', 'Bluetooth', 'NFC tap', 'Micro-USB',
             'Bluetooth links headsets, keyboards and styluses at a few metres.', NFC, None),
        ],
            P('Phones and laptops connect to accessories in a few ways. Wired: USB-C on most current devices, Lightning on older iPhones, micro-USB '
              'on cheap ones. Wireless: Bluetooth for headsets and keyboards over a few metres, NFC for tap-to-pay within centimetres, and tethering '
              'to share mobile data. A dock adds charging, ports and screens through one cable; a port replicator just copies ports.'),
            P('Think of ways to talk to someone. Bluetooth is speaking across a small room. NFC is a whisper: it only works if your heads are almost '
              'touching, which is exactly why it is used for payments. Tethering is letting a friend share your phone call. A dock is a full desk '
              'with a phone, lamp and screen all plugged in; a port replicator is just an extension lead.'),
            ['Wired or wireless?', 'Wired: which connector?', 'Wireless: range needed?', 'Pair or tap.', 'Test the accessory.'],
            '<p>Sort each link by range.</p>',
            sort('Range', {'Centimetres': ['NFC tap-to-pay', 'NFC pairing'], 'Metres': ['Bluetooth headset', 'Bluetooth keyboard'],
                           'Cable': ['USB-C dock', 'Lightning charger']}, 'NFC is the shortest link.'), LAP),
    },
    '4.2': {
        'core-content': _P2[('4.2', 'core-content')],
        '1-three-radios': X('1. Three radios', 'IT-4.2', S2, [
            ('Mail works on cellular, fails on building Wi-Fi. Suspect?', 'The Wi-Fi path', 'The phone hardware itself', 'The mail app needs reinstalling',
             'The device and account work; the building path does not.', PB, PB),
            ('First test for “mail does not work”?', 'Which path is used', 'Factory reset the phone', 'Replace the SIM card',
             'Find the path, then test the other one.', PB, None),
            ('In the roads story, why try another road?', 'Find the blocked one', 'Roads are faster', 'Drivers like variety',
             'If the other road works, the car is fine and the first road is blocked.', PB, None),
            ('Phone shows 169.254 on Wi-Fi. That points to…', 'DHCP or association', 'The mail server being offline', 'The battery',
             'No real address means the Wi-Fi join failed, not the app.', PB, None),
            ('Work mail fails only on VPN. Problem is…', 'VPN or connector', 'The phone itself', 'Cellular signal',
             'It is a tunnel problem, not a phone problem.', PB, None),
        ],
            P('A phone can reach the internet three ways: building Wi-Fi, the mobile network, and a VPN tunnel riding on either. When work mail '
              'fails, find which way it is going and try the other. If it syncs on mobile data but not on Wi-Fi, the phone and account are fine and '
              'the building network is the suspect. If it fails only with the VPN on, it is a tunnel problem.'),
            P('If your car cannot reach the office one morning, you try a different road. If the other road gets you there, your car is fine and the '
              'first road is closed. You report the closed road, not a broken car. A phone with Wi-Fi, mobile data and a VPN has three roads, and '
              'switching between them shows which one is blocked.'),
            ['Which path is in use?', 'Turn Wi-Fi off: works on cellular?', 'Check Wi-Fi details: IP, router, DNS.', 'Check VPN status.', 'Name the failing path.'],
            '<p>Sort each result to the failing path.</p>',
            sort('Failing path', {'Building Wi-Fi': ['Works on cellular only', '169.254 address'], 'Cellular': ['No SIM detected', 'Data switched off'],
                                  'VPN': ['Fails only with VPN on']}, 'Test the other path before blaming the phone.'), MOB),
        '2-mdm': X('2. MDM', 'IT-4.2', S2, [
            ('User wants Outlook but MDM blocks installs. You…', 'Open a request', 'Remove the work profile', 'Factory reset the phone',
             'MDM belongs to its owner; ask the enrollment owner.', MDM, MDM),
            ('What can MDM do to a managed phone?', 'Lock, wipe, block apps', 'Only change the wallpaper', 'Nothing remotely',
             'Managed devices can be locked, wiped or restricted.', MDM, None),
            ('In the company-car story, who changes the car?', 'The fleet manager', 'Whoever drives it', 'A passer-by',
             'A company car belongs to the fleet; drivers do not modify it.', MDM, None),
            ('May you factory-reset a managed phone to clear it?', 'No', 'Yes, always', 'Yes, if it is slow',
             'A reset of a managed device is a change you do not make in the hallway.', MDM, None),
            ('The Windows gui-accounts question is the same:', 'Whose account is it?', 'How fast does it run today?', 'What colour is it?',
             'Always ask whose account or enrollment you are touching.', MDM, None),
        ],
            P('Work phones are often enrolled in device management. It lets the organisation lock or wipe them. It also decides which apps may be installed. That control belongs to the owner of the enrollment, not to whoever is holding the phone. Does a user need a blocked app? Raise a request with that owner. Do not remove the profile or reset the phone.'),
            P('A company car comes with the company’s rules: approved fuel card, tracker fitted, no roof box without permission. A driver who wants a '
              'tow bar does not bolt one on in the car park; they ask the fleet manager. Removing the tracker to fit one would be worse. The managed '
              'phone is that company car, and the enrollment owner is the fleet manager.'),
            ['Is the device managed?', 'Who owns the enrollment?', 'What does the user need?', 'Open a request with the owner.', 'Note the request on the ticket.'],
            '<p>Put the MDM request in order.</p>',
            order('Blocked app', ['Confirm the device is managed', 'Find the enrollment owner', 'Write what the user needs', 'Open the request'],
                  'Nobody sidesteps the policy.'), MOB),
        'radios-and-mdm': _P2[('4.2', 'radios-and-mdm')],
        'troubleshooting-mobile-os-app-and-mobile-security-issues': X('Troubleshooting mobile OS, app and mobile-security issues', 'IT-4.2', S2, [
            ('An app keeps crashing. Which step comes last?', 'Delete and reinstall', 'Close and reopen it', 'Restart the device',
             'Reinstalling can delete app data, so it comes after the safe steps.', REI, REI),
            ('Android extra steps before reinstall?', 'Force stop, clear cache', 'Root the phone to get admin access', 'Remove the SIM',
             'Force stop and clear cache sit between restart and clearing data.', REI, None),
            ('In the stuck-door story, why not knock the wall down?', 'Lose what is inside', 'Walls take too long to open', 'Doors are cheap',
             'Try the gentle fixes first; the drastic one loses data.', REI, None),
            ('What comes right after restarting the device?', 'Update app and OS', 'Delete the app and its data', 'Factory reset',
             'Apple and Google: close, restart, update, then reinstall.', REI, None),
            ('Clearing storage/data on Android…', 'Resets the app', 'Only frees cache', 'Updates the app',
             'Clearing data wipes the app’s settings and local files.', REI, None),
        ],
            P('When a phone app crashes or freezes, work from the gentlest step to the most drastic. Close it and open it again, restart the phone, '
              'update the app and the system, and only then remove and reinstall it, because removing it can delete data stored only inside the app. '
              'Android adds force stop and clear cache along the way; clearing its data resets it completely.'),
            P('If a door sticks, you try the handle again, give it a push, oil the hinge, and maybe plane the edge. You do not start by knocking the '
              'wall down, because everything in the room behind it gets crushed. Deleting an app is knocking the wall down: it may work, but anything '
              'kept only inside that app goes with it.'),
            ['Scope: one app or all?', 'Close and reopen.', 'Restart the device.', 'Update app and OS.', 'Reinstall last.'],
            '<p>Put the app fixes in order.</p>',
            order('Crashing app', ['Close and reopen', 'Restart the device', 'Update app and OS', 'Delete and reinstall'], 'Data-losing steps come last.'), MOB),
    },
    '4.3': {
        'core-content': _P2[('4.3', 'core-content')],
        '1-the-path': X('1. The path', 'IT-4.3', S3, [
            ('Whole floor cannot print. Start at…', 'Device and print server', 'The first user’s Word settings', 'Reinstalling one PC’s driver',
             'Many users point at the shared end of the path.', FPC, FPC),
            ('One user, one app fails. Start at…', 'The app and driver', 'The print server for the floor', 'The printer panel',
             'A single app on a single PC points to the start of the path.', FPC, None),
            ('In the post story, where do you look if no street gets mail?', 'The sorting office', 'One letterbox on the street', 'One envelope',
             'Everyone failing points at the shared middle, not one house.', FPC, None),
            ('Which comes after the spooler?', 'Driver and port', 'The application', 'Paper tray',
             'App, spooler, driver and port, network, device.', FPC, None),
            ('Panel says paper jam. Start where?', 'The device', 'The spooler', 'The application',
             'A device message sends you to the device first.', FPC, None),
        ],
            P('A print job travels from the application to the Windows spooler and queue, through the driver and the port, over USB or the network, '
              'to the printer itself. How many people are affected tells you where to start. One person in one program: begin at that program and '
              'its driver. One computer and every program: the spooler and driver. A whole floor: the printer and the print server.'),
            P('Letters go from your desk to the post box, the sorting office, the van and the letterbox. If only your letter is missing, check your '
              'envelope. If the whole street gets no post, nobody checks one person’s handwriting; they ring the sorting office. Printing is the same '
              'route, and the number of people missing their post tells you which stop to visit first.'),
            ['Application.', 'Spooler and queue.', 'Driver and port.', 'USB or network.', 'Device panel.'],
            '<p>Sort each scope to where you start.</p>',
            sort('Where to start', {'App and driver': ['One user, one app', 'Only Excel fails'], 'Spooler on that PC': ['One PC, every app'],
                                    'Device and server': ['Whole floor', 'Panel says jam']}, 'Scope picks the starting point.'), PRN),
        '2-notes': X('2. Notes', 'IT-4.3', S3, [
            ('Which note helps the next tech?', 'Who, PC, error, queue, panel', 'Printer broken, please fix it soon', 'User is upset about printing again',
             'Specific facts let someone act without asking you.', VP, VP),
            ('“Printer broken” is like which ticket?', 'Ticket A', 'Ticket B', 'A closed ticket',
             'Ticket A from Chapter 1 is the vague one.', VP, None),
            ('In the doctor story, what helps?', 'Exact symptoms', 'Feeling unwell', 'A long wait',
             'Where it hurts and since when beats “I feel bad”.', VP, None),
            ('Which detail tells if the device is alive?', 'Panel state', 'User’s job title', 'Office floor colour',
             'Whether the panel responds is key evidence.', VP, None),
            ('Which item names the queue?', 'Queue name', 'Desk number', 'Printer colour',
             'The queue name tells which shared printer path.', VP, None),
        ],
            P('A useful print note answers five things. Who can and cannot print? From which computer? What is the exact error message? What is the queue called? Is the printer’s screen working? “Printer broken” says none of that. The next person must start again. That is the weak Ticket A pattern from Chapter 1.'),
            P('A doctor gets nowhere with “I feel bad.” She needs where it hurts, since when, and what makes it worse. A patient who says “sharp pain '
              'in the left knee since Tuesday, worse on stairs” is examined and treated much faster. A printer note works the same way: the more '
              'exact the symptoms, the quicker someone else can help.'),
            ['Who can print, who cannot?', 'Which PC?', 'Exact error text.', 'Queue name.', 'Panel alive?'],
            '<p>Sort each line.</p>',
            sort('Useful or not?', {'Useful': ['Queue FL2-MFP', 'Error: offline', 'Panel shows jam'], 'Not useful': ['Printer broken', 'User annoyed']},
                 'Facts beat feelings.'), PRN),
        'print-path': _P2[('4.3', 'print-path')],
        'printer-configuration-maintenance-and-print-defect-diagnosis': X('Printer configuration, maintenance and print-defect diagnosis', 'IT-4.3', S3, [
            ('Pages come out full of random symbols. Check…', 'Driver language', 'The toner level first', 'The paper tray size setting',
             'A driver for the wrong language (PCL vs PostScript) prints garbage.', PCL, PCL),
            ('Which language suits graphics and publishing?', 'PostScript', 'PCL', 'Plain text',
             'PostScript is device-independent and preferred for graphics.', PCL, None),
            ('In the translator story, garbled pages mean…', 'Wrong translator', 'No paper in the tray', 'Low ink',
             'The driver translates; the wrong one speaks the wrong language.', PCL, None),
            ('Duplex means…', 'Two-sided printing', 'Two printers sharing a queue', 'Double speed',
             'Duplex prints both sides of the page.', PCL, None),
            ('Badge release at the device is a…', 'Security setting', 'Paper size per tray', 'Driver type',
             'User authentication at the device keeps prints secure.', PCL, None),
        ],
            P('Printers need a driver that speaks their page language. PCL is quick and common for office work; PostScript is better for graphics. '
              'Pick the wrong one and pages fill with symbols. Settings include two-sided printing, orientation, tray paper sizes and quality. Shared '
              'printers can need badge release and keep logs of who printed what, and their firmware should be kept up to date.'),
            P('A driver is a translator between your computer and the printer. If you hire a French translator for a German speaker, every sentence '
              'comes out as nonsense, even though both people are speaking perfectly well. Garbled pages full of symbols are that mismatch: the '
              'computer and printer are fine, but the translator in the middle is the wrong one.'),
            ['Garbled output?', 'Check driver language.', 'Check duplex, tray, quality settings.', 'Check security and badging.', 'Update firmware.'],
            '<p>Sort each setting.</p>',
            sort('Setting type', {'Language': ['PCL', 'PostScript'], 'Layout': ['Duplex', 'Orientation'], 'Security': ['Badge release', 'Audit log']},
                 'Language mismatches cause garbage.'), PRN),
    },
    '4.4': {
        'core-content': _P2[('4.4', 'core-content')],
        'portable-intake': X('Portable intake', 'IT-4.1', S4, [
            ('Laptop bulging and warm when off. Classify as…', 'Safety stop', 'Slow performance', 'Software issue',
             'A swollen battery is a safety stop with a do-not-charge tag.', ASK, SWELL),
            ('Floor 2 cannot print. Owner of the change?', 'Print server or network owner', 'The first user’s manager', 'The laptop vendor’s support line',
             'Shared device, many users: the print or network owner.', ASK, None),
            ('In the relay story, what must the baton carry?', 'What to do next', 'Who ran fastest', 'The weather',
             'A note must let the next person continue without asking.', ASK, None),
            ('Phone lost work mail after an update. First evidence?', 'Compliance message', 'Battery health percentage', 'Screen size',
             'A managed device: check compliance and whether cellular works.', ASK, None),
            ('The intake order is…', 'Classify, impact, escalate, note', 'Fix, test, then write a note', 'Note, escalate, then classify',
             'The Chapter 1 intake structure.', ASK, None),
        ],
            P('Portable tickets use the same intake routine as Chapter 1. Decide what kind of problem it is. Count how many people it hits. Name who owns the change. Then write a note. The note tells the next technician what to do without asking you. Stop for a battery? Chase a driver or account policy? Work the printer panel?'),
            P('In a relay race the runner hands over the baton and keeps running nowhere; the next runner must be able to go immediately. If the '
              'baton were a note saying “sort it out,” they would stand still. Your ticket note is the baton, and it must carry exactly what the next '
              'person needs to keep running.'),
            ['Classify.', 'Count impact.', 'Name the owner.', 'Gather first evidence.', 'Write the note.'],
            '<p>Sort each ticket to its owner.</p>',
            sort('Owner', {'Battery procedure': ['Bulging laptop', 'Warm when off'], 'MDM owner': ['Work mail blocked by policy'],
                           'Print server owner': ['Floor 2 cannot print', 'All queues stuck']}, 'Each ticket has a different owner.'), INT),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '4.1': {'1-power-first': 'd5d646a0e6aa', '2-what-you-may-open': '2fe4c1052f32', 'fru-identity-and-batteries': '483c06f76ef4', 'mobile-accessories-connectivity-mdm-and-mobile-hardware-trou': '160c32a4aa72'},
    '4.2': {'1-three-radios': '7858c7585478', '2-mdm': '3340195bbed9', 'troubleshooting-mobile-os-app-and-mobile-security-issues': 'd7f6889e8410'},
    '4.3': {'1-the-path': 'ba15435879e0', '2-notes': '5f93ec89275b', 'printer-configuration-maintenance-and-print-defect-diagnosis': 'b2cafbf89f19'},
    '4.4': {'portable-intake': 'e73d0211c450'},
}

