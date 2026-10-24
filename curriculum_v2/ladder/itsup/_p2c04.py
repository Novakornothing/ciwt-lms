"""Option B pass 2 — ITSUP chapter 4 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

_P = 'MC-L-IT4-'
BRICK, SWELL, GEN, NFC, PHONE, MDM, REINST, FIRSTPC, VPRINT, PCL, ASK = (_P + k for k in (
    'BRICK', 'SWELL', 'GENERIC-PART', 'NFC-RANGE', 'PHONE-BROKEN', 'MDM-BYPASS', 'REINSTALL-FIRST', 'FIRST-PC', 'VAGUE-PRINT', 'PCL-PS',
    'NOTE-ASK'))
RESETNET, SIDESTEP, PSCOPE, PORDER = 'MC-IT4-RESET-FOR-NETWORK', 'MC-IT4-SIDESTEP-MDM', 'MC-IT4-WRONG-SCOPE-PRINT', 'MC-IT4-PRINT-ORDER'
FFACT, SKIPISO, FRUPAPER = 'MC-C-IT4-FORM-FACTOR', 'MC-C-IT4-SKIP-ISOLATE', 'MC-R3-IT4-FRU-PAPERWORK'
LAP = ('win-laptop-ports', 'Read the adapter and chassis labels, then list the ports and what each one carries.')
MOB = ('mob-mdm', 'Check which path the device uses and who owns the enrollment before changing anything.')
PRN = ('print-trouble', 'Scope the print fault, then work app, spooler, driver, port and device in order.')
INT = ('ticket-intake', 'Classify, count impact, name the owner, then write a note a colleague can act on.')


def _s(n, t):
    return f'Course lesson 4.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4 = (_s(1, 'Laptops'), _s(2, 'Mobile Devices'), _s(3, 'Printers'), _s(4, 'Portable Devices Capstone'))
SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


_add('4.1', 'start-here-a-laptop-is-still-a-computer', 'Start here — a laptop is still a computer', 'IT-4.1', S1, [
    ('Which laptop symptom is a safety ticket, not a repair?', 'A swelling battery', 'A sticky keyboard key', 'A slow Wi-Fi connection',
     'A swollen lithium-ion battery can burn; it is a stop-and-report safety ticket.', SWELL, SWELL),
    ('How do you order a laptop screen?', 'By service tag and part code', 'As “a 15-inch screen”', 'By the colour of the outer case',
     'The same model ships with different panels; the service tag parts list names the exact one.', GEN, GEN),
    ('In the camper-van story, what is the van’s own fridge battery?', 'The laptop battery', 'The wall socket at home', 'The phone’s SIM card',
     'A camper van carries its own power like a laptop carries its battery.', SWELL, SWELL),
    ('In the picture, which part is extra on phones and tablets?', 'Radios and work profile', 'A CPU and some memory', 'A screen and internal storage',
     'Phones share the same core parts; radios and MDM work profiles are the additions.', MDM, MDM),
    ('A 45 W brick on a laptop built for 65 W. Likely symptom?', 'Slow, not charging under load', 'Laptop runs faster than usual', 'The screen turns black and white',
     'An underpowered brick can keep it alive idle but lets the battery drain under load.', BRICK, BRICK),
],
    (['A laptop has the same parts as a tower PC.', 'It has power, a brain, memory, storage and a screen.', 'But some things are different.',
      'The battery can swell.', 'A swollen battery is a safety problem.', 'The charger must have enough watts.', 'Parts are ordered by service tag.',
      'Phones add radios and sometimes a work profile.'],
     'Treat a laptop as a PC, but stop for swollen batteries and order parts by service tag.'),
    ('A camper van is still a car. It has an engine, wheels and lights. But it also carries its own fridge battery and a small kitchen. '
     'If that battery bulges, you do not drive on. You also buy parts for “this van, this year”, not “a van”.',
     [('Engine, wheels, lights', 'CPU, storage, screen'), ('Fridge battery', 'Laptop lithium-ion battery'), ('Bulging battery', 'Swollen pack: safety stop'),
      ('Parts for this van, this year', 'Parts by service tag'), ('Satellite radio', 'Phone Wi-Fi and cellular radios')],
     'A van battery is easy to reach; a laptop battery is often glued inside and must never be pressed or pried.'),
    ('two', 'Tower parts, plus what portables add', (('Same as a tower', ['Power, CPU, memory', 'Storage and screen']),
                                                    ('What portables add', ['Battery that can swell', 'Brick wattage must match', 'Radios and MDM profile']))),
     'Start from what you know about a tower. The right column lists the new risks. Each one changes what you are allowed to do.',
    'Sort each fact into the right column, then read the adapter and chassis labels in the laptop lab.',
    sort('Same or new?', {'Same as a tower': ['Has storage and memory', 'Has a CPU'],
                          'New on portables': ['Battery can swell', 'Charger wattage matters', 'Parts named by service tag']},
         'The new column is where beginners get hurt or order the wrong part.'), LAP)

_add('4.1', 'core-content', 'Core content', 'IT-4.1', S1, [
    ('What decides whether a laptop part is a FRU?', 'The model’s service manual', 'How the laptop looks inside', 'Whether it has screws',
     'Which parts are field-replaceable depends on the model; the service manual and parts list decide.', GEN, FFACT),
    ('First step before opening a laptop?', 'Confirm the data is backed up', 'Remove all the bottom screws', 'Press on the battery to test it',
     'Back up or confirm sync, record the tag and BitLocker status, then shut down fully.', SWELL, GEN),
    ('In the hotel story, what is the room-key number?', 'The service tag', 'The wattage', 'The battery size',
     'The service tag identifies the exact build, like a room number identifies one room.', GEN, FRUPAPER),
    ('In the flow, what comes right after “shut down fully”?', 'Unplug charger and dock', 'Order a new keyboard', 'Remove the screen assembly',
     'After a full shutdown, remove external power before opening anything.', SWELL, GEN),
    ('powercfg /batteryreport shows full charge far below design. Meaning?', 'Battery wear', 'A faulty Wi-Fi card', 'A broken charger port',
     'Full charge capacity well below design capacity is normal wear, not a fault.', BRICK, BRICK),
],
    (['A FRU is a part a technician can swap on site.', 'Which parts count depends on the model.', 'Read the service manual first.',
      'Order by the service tag, not by looks.', 'Before you open it, back up the data.', 'Shut it down fully.', 'Unplug the charger.',
      'Disconnect the battery as the manual says.', 'Never press a swollen battery.'],
     'Look up the exact model, back up, power down fully, then open it as the manual says.'),
    ('A hotel has many rooms that look alike. The room number tells staff exactly which minibar and which bed to replace. Before '
     'cleaners move furniture, they check the guest has left and the lights are off. A smoking minibar means evacuating, not fixing.',
     [('Room number', 'Service tag'), ('Room’s inventory list', 'Parts list and service manual'), ('Guest has left, lights off', 'Data backed up, full shutdown, unplugged'),
      ('Smoking minibar', 'Swollen or hot battery: safety incident')],
     'Rooms rarely change between years; laptop builds do. The same model name can hide different panels and batteries.'),
    ('flow', 'Opening a laptop safely', ['Back up data', 'Record tag and BitLocker', 'Shut down fully', 'Unplug charger, dock', 'Disconnect battery', 'Swap the FRU']),
     'Each box makes the next one safe. The battery is disconnected before any other part is touched.',
    'Order the power-down steps, then read the chassis and adapter labels in the lab.',
    order('Before opening the laptop', ['Back up or confirm sync', 'Record service tag and BitLocker status', 'Shut down fully, not sleep',
                                        'Unplug charger and dock', 'Disconnect the battery per the manual'], 'Data and power first, screws last.'), LAP)

_add('4.2', 'core-content', 'Core content', 'IT-4.2', S2, [
    ('Mail fails on building Wi-Fi but works on cellular. Suspect?', 'The building Wi-Fi path', 'The phone’s hardware', 'The mail account itself',
     'The account works over cellular, so the Wi-Fi path (portal, proxy, filter) is the suspect.', PHONE, PHONE),
    ('What does the APN setting do?', 'Reaches carrier data', 'Sets the screen lock', 'Encrypts the storage',
     'The Access Point Name tells the phone how to reach the carrier’s data network.', PHONE, RESETNET),
    ('In the delivery story, what is the second road?', 'Cellular data', 'The MDM profile', 'The phone’s internal battery',
     'Two roads to the same town: if one is blocked, try the other to see if the parcel is the problem.', PHONE, PHONE),
    ('In the table picture, a 169.254 Wi-Fi address points at…', 'DHCP or association', 'The mail app itself', 'The carrier’s data network',
     'A 169.254 address means no lease; the app is not the problem yet.', PHONE, REINST),
    ('A user wants to factory-reset to fix one path. Your answer?', 'Test the other path first', 'Reset it, it is quicker', 'Remove the work profile first',
     'One failing path is not a phone fault; resets and profile removal are not first steps.', RESETNET, SIDESTEP),
],
    (['A phone has more than one way out.', 'There is Wi-Fi.', 'There is cellular data.', 'Some apps also use a VPN tunnel.',
      '“Mail does not work” is only a symptom.', 'Turn Wi-Fi off and try cellular.', 'If mail works now, the building path is the suspect.',
      'Do not reset the phone for that.'],
     'Find which path fails by testing the other one before you change anything on the phone.'),
    ('A delivery van can reach a town by the main road or the back road. If parcels stop arriving, the driver tries the back road. If '
     'parcels get through, the van is fine and the main road is blocked. Nobody scraps the van.',
     [('Main road', 'Building Wi-Fi'), ('Back road', 'Cellular data'), ('Toll tunnel for work parcels', 'VPN or per-app tunnel'),
      ('Scrapping the van', 'Factory reset'), ('Depot that owns the van', 'MDM owner of the managed phone')],
     'Roads do not check identity, but work apps do: a compliance or MFA block fails on every path, so check the account banner too.'),
    ('two', 'Which path is failing?', (('Test', ['Wi-Fi off, cellular on', 'Wi-Fi details: IP, router, DNS', 'VPN status']),
                                       ('If it fails', ['Account or device issue', '169.254: DHCP, not the app', 'Ask VPN owner with error']))),
     'Read each row across. Every test has a different owner if it fails. None of the rows says “reset the phone”.',
    'Order the checks for “mail broken on my phone”, then use the mobile lab to see which path the device uses.',
    order('Mobile mail ticket', ['Toggle Wi-Fi off and try cellular', 'Read the Wi-Fi details', 'Check VPN status', 'Read the account banner',
                                 'Escalate to the right owner'], 'Find the failing path before you touch settings.'), MOB)

_add('4.2', 'radios-and-mdm', 'Radios and MDM', 'IT-4.2', S2, [
    ('Mail works on cellular, fails on building Wi-Fi. What works?', 'The phone’s radio', 'The building path', 'Nothing at all',
     'The radio and account work on cellular; the building path is what fails.', PHONE, PHONE),
    ('May you factory-reset a managed phone to “clear it”?', 'No, MDM is shop property', 'Yes, if the user asks', 'Yes, it is the fastest fix',
     'The work profile belongs to the shop; resets and bypasses need its owner.', SIDESTEP, RESETNET),
    ('In the company-car story, who owns the tracker?', 'The company', 'The driver', 'The local garage',
     'A company car’s tracker belongs to the company, as the MDM profile belongs to the shop.', MDM, MDM),
    ('In the picture, which question links gui-accounts to MDM?', 'Whose account is it?', 'How old is the phone?', 'What colour is the case?',
     'Both ask whose account or profile you are touching before any change.', MDM, MDM),
    ('A user asks you to remove MDM to install an app. Response?', 'Refer it to the owner', 'Remove it in the hallway', 'Reset to factory state',
     'Sidestepping MDM is a change you do not get to make; the owner decides.', SIDESTEP, RESETNET),
],
    (['If mail works on cellular, the radio is fine.', 'The building path is the problem.', 'A managed phone has a work profile.',
      'That profile belongs to the shop.', 'Do not reset the phone to clear it.', 'Do not remove the profile to add an app.', 'Ask whose account you are touching.'],
     'Test the path, and leave the work profile to the people who own it.'),
    ('A company car has a tracker and fuel card fitted by the company. If the radio cannot find a station in a tunnel, the radio is fine; '
     'the tunnel blocks it. The driver may not rip out the tracker to fit a new stereo. That needs the fleet manager.',
     [('Car radio in a tunnel', 'Phone on building Wi-Fi that blocks mail'), ('Tracker and fuel card', 'MDM work profile'),
      ('Fleet manager', 'MDM owner'), ('Ripping out the tracker', 'Factory reset or profile removal')],
     'Removing a tracker is obvious; wiping a phone can look harmless but deletes company data and access in one tap.'),
    ('flow', 'Managed phone, mail failing', ['Try cellular', 'Path identified', 'Whose account?', 'MDM owner decides', 'Change by owner']),
     'The flow never passes through “reset” or “remove profile”. The owner box is where any device change is approved.',
    'Sort each action into allowed or not allowed for a hallway visit, then check the enrollment owner in the mobile lab.',
    sort('Hallway or owner?', {'You may do it': ['Toggle Wi-Fi to test cellular', 'Read the Company Portal message'],
                               'Owner decides': ['Remove the work profile', 'Factory-reset the phone', 'Install an app outside MDM']},
         'Testing paths is yours; the profile is not.'), MOB)

_add('4.3', 'core-content', 'Core content', 'IT-4.3', S3, [
    ('One user, one app cannot print. Where do you start?', 'The app’s print dialog', 'The print server', 'The printer’s fuser unit',
     'Scope points at the app: one app on one PC means start at the first box.', PSCOPE, FIRSTPC),
    ('Every PC on the floor cannot print. Where do you look?', 'The printer or print server', 'One PC’s printer driver', 'The first user’s application',
     'Many PCs failing points at the shared end: device, server or network path.', FIRSTPC, PSCOPE),
    ('In the water-pipe story, what is the tap?', 'The printer', 'The application', 'The spooler',
     'The tap is where water comes out, like the printer where the page comes out.', PORDER, PORDER),
    ('In the path picture, what sits between the spooler and the port?', 'The driver', 'The application', 'The paper tray',
     'App, spooler and queue, driver, port, device: the driver translates for the printer.', PORDER, PORDER),
    ('Another desk prints fine to the same printer. What is it?', 'Your control', 'The fault', 'A second outage',
     'A working desk is the control that proves the printer and server path are fine.', PSCOPE, FIRSTPC),
],
    (['A print job travels a path.', 'It starts in the app.', 'Then the spooler and queue.', 'Then the driver.', 'Then the port, USB or network.',
      'Then the printer.', 'Ask how many users fail.', 'One app on one PC: start at the app.', 'Every PC: start at the printer end.'],
     'Let the scope tell you which end of the print path to start from.'),
    ('Water flows from a reservoir through pipes to a tap. If one kitchen tap is dry, you check that tap and its pipe. If every house on '
     'the street is dry, you look at the main pipe and the reservoir. A neighbour with running water is your proof.',
     [('Kitchen tap', 'One app or one PC'), ('House pipes', 'Spooler, queue and driver'), ('Street main', 'Network port or print server'),
      ('Reservoir', 'The printer itself'), ('Neighbour with water', 'Control PC that prints')],
     'Water flows from the reservoir outward, but print jobs flow from the app toward the printer. The scope rule still holds.'),
    ('flow', 'The print path', ['Application', 'Spooler and queue', 'Driver', 'Port: USB or network', 'Printer panel']),
     'Read left to right for the job. Read the scope to decide where to start. The next desk that prints is your control.',
    'Sort each ticket by where you would start, then work the print lab from that end.',
    sort('Where do you start?', {'App end': ['One user, only Excel fails', 'One app prints blank pages'],
                                 'PC middle': ['One PC, every app fails', 'Queue on one PC is stuck'],
                                 'Printer end': ['Whole floor cannot print', 'Panel shows a paper jam']}, 'Scope picks the starting box.'), PRN)

_add('4.3', 'print-path', 'Print path', 'IT-4.3', S3, [
    ('The panel says paper jam. What do you check first?', 'The device', 'The driver', 'The spooler',
     'A jam or paper-out message on the panel means the device comes first.', PORDER, FIRSTPC),
    ('The whole floor is queued. Should you rebuild the first PC’s driver?', 'No, check panel and server', 'Yes, start with that PC', 'Yes, on every PC on the floor',
     'Many users failing points at the device and the print server, not one driver.', FIRSTPC, FIRSTPC),
    ('In the relay-race story, what is the baton?', 'The print job', 'The printer driver', 'The paper tray',
     'The job is passed hand to hand along the path like a baton.', PORDER, PORDER),
    ('In the picture, one PC fails in every app. Which boxes?', 'Spooler and driver', 'The app only', 'The printer panel and tray',
     'One PC with every app failing points at that PC’s spooler and driver.', PSCOPE, PORDER),
    ('Which is a good ticket note?', 'Floor 2: panel OK, queue stuck on server', 'Printer broken, please fix it soon', 'Tried lots of stuff and it is still broken',
     'Name the link in the path and its state, not “printer broken”.', VPRINT, VPRINT),
],
    (['A print job makes five stops on its way to paper.', 'Ask who is affected before you pick a stop.', 'If only Word fails for Sam, look at Word.',
      'If Sam’s whole PC fails, look at its queue and printer software.', 'Ask a neighbour to print as a test.', 'If twenty people fail, walk to the machine.',
      'Read its screen for jams or empty trays.', 'Leave everyone’s PC alone in that case.'],
     'Match the scope to a part of the path, and start there.'),
    ('In a relay race, runners pass a baton. If the baton falls at the third handover, you watch the third runner, not the first. If '
     'every team drops at the finish line, the finish line is the problem.',
     [('Baton', 'Print job'), ('Runners in order', 'App, spooler, driver, port, device'), ('Third handover', 'Driver to port'),
      ('Every team fails at the end', 'Whole floor: device or print server')],
     'Runners can see where the baton fell; print jobs leave little trace, so you use scope and the control desk to find the spot.'),
    ('flow', 'Scope picks the starting box', ['One app: application', 'One PC: spooler, driver', 'Next desk prints: control', 'Floor: panel, server']),
     'Each box pairs a scope with where to start. The control desk is the fastest test you have.',
    'Reveal the answer after choosing where to start.',
    reveal('Twelve users on floor 2 cannot print; the next floor prints fine to its own printer. Where do you start, and what do you leave alone?',
           'Start at the floor 2 printer panel and the print server queue. Leave each PC’s driver alone.'), PRN)

_add('4.4', 'core-content', 'Core content', 'IT-4.1', S4, [
    ('“Case bulging, warm when off.” How do you classify it?', 'Safety stop', 'Routine repair', 'Software issue',
     'A swollen, warm battery is a safety stop: isolate, tag, do not charge.', SWELL, SWELL),
    ('“Nobody on floor 2 can print.” Who owns the change?', 'Print server or network owner', 'The first user who rang', 'The laptop vendor’s phone helpdesk',
     'A shared device with many users belongs to its server or network owner.', FIRSTPC, ASK),
    ('In the hospital story, what is triage?', 'Classify and impact', 'Writing the bill', 'Booking a taxi home',
     'Triage sorts by urgency and impact, like the intake structure for tickets.', ASK, ASK),
    ('In the intake flow, what is last?', 'The note', 'Classify', 'Impact',
     'Classify, impact, escalate, then write a note a colleague can act on.', ASK, ASK),
    ('A phone fails compliance. What does a passing note include?', 'Compliance message and approver', 'That the user seemed very upset', 'Only the words “fixed it”',
     'Name the message, the remote action if any and who approved it.', ASK, SIDESTEP),
],
    (['Every portable ticket uses the same steps.', 'Classify it.', 'Count the impact.', 'Name who owns the change.', 'Write a note.',
      'A bulging battery is a safety stop.', 'A phone failing compliance needs the MDM owner.', 'A floor that cannot print needs the server owner.',
      'The note must let a colleague continue without asking you.'],
     'Classify, count impact, name the owner, and write a note nobody has to ask about.'),
    ('In a hospital, a nurse sorts arrivals by urgency, counts how many are hurt, calls the right doctor and writes a chart. The next '
     'shift reads the chart and carries on. Nobody has to phone the nurse at home.',
     [('Sorting by urgency', 'Classify the ticket'), ('Counting the hurt', 'Impact: one user or many'), ('Calling the right doctor', 'Escalate to the owner'),
      ('Chart for the next shift', 'Ticket note')],
     'A patient can explain symptoms; a swollen battery cannot. The safety stop must come from you, not from the user’s worry.'),
    ('flow', 'Portable ticket intake', ['Classify', 'Impact', 'Owner', 'Note']),
     'All three capstone tickets pass through these four boxes in the same order. Only the owner box changes between them: battery depot, MDM owner, or the print server and network owner.',
    'Sort the three tickets by owner, then run the intake lab and write one passing note.',
    sort('Who owns the change?', {'Battery procedure / depot': ['Bulging case, warm when off'], 'MDM owner': ['Phone fails compliance after update'],
                                  'Print server or network owner': ['Floor 2 cannot print', 'Printer reservation missing']},
         'Classify first; the owner follows from the class.'), INT)
