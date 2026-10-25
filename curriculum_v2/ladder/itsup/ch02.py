"""Explanation ladder — ITSUP chapter 2 (Motherboards, CPU, Memory, POST, Inventory). Pending SME review.

Refinement pass 20. Option B pass 3: the depth and teach-block sections that used to be same_as now have their own
bespoke ladders (_p3c02.py).
"""
from curriculum_v2.ladder.itsup._lk import M, P, X
from curriculum_v2.ladder.itsup._p3c02 import SECS as _P2
from curriculum_v2.ladder.schema import order, reveal, same_as, sort

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 2


def _s(n, t):
    return f'Course lesson 2.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4, S5, S6 = (_s(1, 'Motherboards and Form Factors'), _s(2, 'UEFI Firmware'), _s(3, 'CPU and Cooling'),
                          _s(4, 'Memory'), _s(5, 'POST and the Bench Card'), _s(6, 'Inventory'))
_P = 'MC-L-IT2-'
MISCONCEPTIONS = M(_P, S1, {
    'BRAND-FF': ('IT-2.1', 'Treating form factor as a brand or marketing name', 'Form factor is board size and screw pattern; measure it.', ['form factor', 'atx']),
    'STANDOFF': ('IT-2.1', 'Leaving extra standoffs under the board', 'Only standoffs that match board holes; extras short the board.', ['standoff']),
    'SOCKET-FORCE': ('IT-2.1', 'Forcing a CPU or cooler that does not match the socket', 'Socket silkscreen decides; if it does not drop in flat, stop.', ['socket', 'lga']),
    'EPS-SKIP': ('IT-2.1', 'Forgetting the 4/8-pin CPU power or front-panel pins and calling the board dead', 'Check every power and header connection before blaming the board.', ['eps', 'header']),
    'FW-IS-OS': ('IT-2.2', 'Thinking firmware problems are Windows problems', 'Firmware runs before the OS; boot order and settings can fake a dead OS.', ['uefi', 'boot order']),
    'SB-BAD-DISK': ('IT-2.2', 'Declaring a USB installer bad when Secure Boot blocked it', 'Check Secure Boot; allowing it temporarily is a change with rollback.', ['secure boot']),
    'FW-MANY': ('IT-2.2', 'Changing several firmware settings at once', 'One setting, save, test, write it down.', ['firmware', 'change']),
    'FAN-HEADER': ('IT-2.1', 'Plugging the CPU cooler into a system-fan header', 'CPU cooler goes on CPU_FAN so firmware sees RPM.', ['cpu_fan', 'rpm']),
    'PASTE': ('IT-2.1', 'Using a glob of paste or none at all', 'A thin even film between cooler and heat spreader.', ['paste']),
    'RAM-STORAGE': ('IT-2.3', 'Confusing RAM (workspace) with storage (filing cabinet)', 'RAM is temporary workspace; the disk keeps files.', ['ram', 'storage']),
    'NOTCH': ('IT-2.3', 'Forcing or filing a DIMM notch to fit', 'DDR4 and DDR5 notches differ on purpose; resistance means stop.', ['ddr4', 'ddr5', 'notch']),
    'CHANNEL-ANY': ('IT-2.3', 'Putting a pair in any empty slots', 'Use the slots the manual marks as a channel, matched size and generation first.', ['dual channel']),
    'POST-SKIP': ('IT-2.3', 'Fixing the OS on a box that never left POST', 'Work power → POST → display → firmware → Windows in order.', ['post', 'beep']),
    'BRAND-STOR': ('IT-2.1', 'Naming storage by brand instead of interface', 'Name the interface: NVMe in M.2, or SATA.', ['nvme', 'sata']),
    'WIPE-FIRST': ('IT-2.4', 'Running diskpart clean before listing disks', 'list disk only; clean is not part of this block.', ['diskpart', 'list disk']),
    'SCREENSHOT': ('IT-2.4', 'Pasting pages of output instead of the lines that answer the question', 'Pull the four lines that matter.', ['systeminfo', 'ticket']),
})
FF, SO, SF, EPS, FWO, SB, FWM, FAN, PASTE, RS, NOTCH, CH, POST, BS, WIPE, SHOT = (_P + k for k in (
    'BRAND-FF', 'STANDOFF', 'SOCKET-FORCE', 'EPS-SKIP', 'FW-IS-OS', 'SB-BAD-DISK', 'FW-MANY', 'FAN-HEADER', 'PASTE', 'RAM-STORAGE',
    'NOTCH', 'CHANNEL-ANY', 'POST-SKIP', 'BRAND-STOR', 'WIPE-FIRST', 'SCREENSHOT'))
HW = ('hw-board', 'Identify the board, socket, memory and storage on the bench card, then name the POST line.')
BUILD = ('hw-pc-build', 'Assemble the parts in order and check each connection before power-on.')
ABOUT = ('gui-about', 'Read Settings → System → About and compare RAM with the DIMMs on the board.')

LESSONS = {
    '2.1': {
        'start-here-the-parts-inside-the-box': X('Start here — the parts inside the box', 'IT-2.1', S1, [
            ('Which part is the “floor” everything plugs into?', 'Motherboard', 'Power supply unit', 'Storage drive bay',
             'The motherboard connects CPU, memory, storage and power into one system.', RS, None),
            ('What does RAM do?', 'Short-term workspace', 'Keeps files after power-off', 'Feeds power to the board',
             'RAM is temporary workspace; storage keeps files and the PSU supplies power.', RS, RS),
            ('In the kitchen story, what is the countertop?', 'RAM', 'The fridge and pantry', 'The oven itself',
             'Countertop is where you work now (RAM); the pantry stores things (disk).', RS, None),
            ('In the walk-round trace, what does the CPU need?', 'A socket and a cooler', 'A SATA data cable', 'An antistatic bag only',
             'The CPU sits in a socket and must have a cooler.', FAN, None),
            ('Which part keeps your files when the PC is off?', 'SSD or HDD', 'RAM sticks in DIMMs', 'The CPU cache',
             'Storage keeps data; RAM loses it at power-off.', RS, None),
        ],
            P('Before opening a case, picture what is inside. The motherboard is the large board everything plugs into. The CPU is the brain; it '
              'sits in a socket and needs a cooler. RAM sticks give short-term working space. An SSD or hard drive keeps files. The power supply '
              'feeds the board. The case holds it all and moves air through it.'),
            P('Think of a kitchen. The motherboard is the kitchen itself, with plumbing and sockets that connect everything. The CPU is the cook. '
              'RAM is the countertop: the bigger it is, the more the cook can work on at once, but it is wiped clean at the end of the day. Storage '
              'is the pantry and fridge, where food stays overnight. The power supply is the gas and electricity coming into the house.'),
            ['Find the motherboard: the big board.', 'Find the CPU socket and cooler.', 'Find the RAM slots.', 'Find the SSD or HDD.', 'Find the PSU in the corner.'],
            '<p>Sort each part by what it does.</p>',
            sort('Part to job', {'Thinks': ['CPU'], 'Works now': ['RAM'], 'Keeps files': ['SSD', 'HDD'], 'Feeds power': ['PSU']},
                 'Every part has one main job.'), BUILD),
        'what-form-factor-means-if-you-have-never-heard-it': _P2[('2.1', 'what-form-factor-means-if-you-have-never-heard-it')],
        '1-form-factor-is-the-hole-pattern': X('1. Form factor is the hole pattern', 'IT-2.1', S1, [
            ('A board is 9.6 × 9.6 in. Which form factor?', 'microATX', 'Full ATX', 'Mini-ITX',
             'ATX is 12 × 9.6 in, Mini-ITX about 6.7 in square; 9.6 × 9.6 is microATX.', FF, FF),
            ('Form factor is mainly about…', 'Size and screw holes', 'The brand on the box', 'How fast the CPU is',
             'Form factor sets size and mounting pattern, which decides which case fits.', FF, FF),
            ('In the picture-frame story, why measure first?', 'The frame must match the holes', 'Frames come in lots of colours', 'Glass breaks easily',
             'A board, like a picture, only fits a frame with matching size and fixings.', FF, None),
            ('What goes wrong with an extra standoff under an empty spot?', 'It shorts the board', 'It cools the back of the board', 'Nothing at all',
             'Metal standoffs where there is no hole touch the back of the board and can short it.', SO, SO),
            ('Which is smallest?', 'Mini-ITX', 'microATX board', 'Full ATX board',
             'Mini-ITX is the smallest of the three, with fewest slots.', FF, None),
        ],
            P('Form factor tells you how big the motherboard is and where its screw holes are, so it tells you which case it fits. ATX is the big '
              'standard (12 × 9.6 in). microATX is smaller (9.6 × 9.6 in), like this course card. Mini-ITX is tiny (about 6.7 in square). Never leave '
              'a metal standoff where the board has no hole: it can short the back.'),
            P('Buying a picture frame, you measure the photo first. A frame that is “nearly” the right size is the wrong frame: the photo slides '
              'around or will not go in. And if a nail sits behind the photo where there is no hook, it pokes a hole. Motherboards are the photos, '
              'cases are the frames, and standoffs are the nails. Measure, match the holes, and only put supports where the board expects them.'),
            ['Measure the board or read the card.', '12 × 9.6 → ATX; 9.6 × 9.6 → microATX; ~6.7 square → Mini-ITX.', 'Match standoffs to board holes only.',
             'Check the case supports that form factor.'],
            '<p>Sort each board size into its form factor.</p>',
            sort('Form factor', {'ATX': ['12 × 9.6 in'], 'microATX': ['9.6 × 9.6 in', 'This course card'], 'Mini-ITX': ['About 6.7 in square']},
                 'Size and holes decide the name.'), HW),
        '2-chipset-and-sockets-names': X('2. Chipset and sockets (names)', 'IT-2.1', S1, [
            ('On an LGA socket, where are the pins?', 'In the socket', 'On the CPU underside', 'On the cooler base',
             'LGA has pads on the CPU and pins in the socket; AM4 is the reverse.', SF, SF),
            ('What does the chipset do?', 'Directs traffic between parts', 'Stores the operating system files', 'Cools the CPU directly',
             'The chipset links CPU, RAM, storage and USB.', SF, None),
            ('In the airport story, what is the control tower?', 'The chipset', 'The CPU socket', 'The power supply',
             'The tower directs traffic between runways, like the chipset between parts.', SF, None),
            ('To identify the board, what do you search?', 'The model printed on it', 'The colour of the board', 'The case brand name',
             'Read the model string on the board and search that.', FF, FF),
            ('AMD AM5 is which kind of socket?', 'LGA, like Intel', 'PGA, pins on the CPU', 'A slot for cards',
             'AM5 (LGA1718) has pins in the socket, like Intel.', SF, None),
        ],
            P('The socket is where the CPU sits. Intel boards and AMD AM5 use LGA: flat pads on the CPU, pins in the socket. AMD AM4 has the pins on '
              'the CPU. The chipset is the traffic controller between CPU, memory, storage and USB. To know exactly which board you have, read the '
              'model printed between the RAM slots and search that.'),
            P('An airport has runways, gates, baggage halls and a control tower. The control tower does not fly planes, but nothing moves without '
              'it directing traffic. That is the chipset. The socket is a gate shaped for one type of plane: an aircraft that does not match the '
              'gate cannot dock, however hard you push. And the airport’s name is on the sign, not guessed from the colour of the terminal.'),
            ['Read the board model between the RAM slots.', 'Read the socket silkscreen (LGA1700, AM4, AM5).', 'LGA: pins in socket; AM4: pins on CPU.',
             'Search the exact model for the support list.'],
            '<p>Sort each socket by where its pins are.</p>',
            sort('Where are the pins?', {'In the socket (LGA)': ['Intel LGA1700', 'Intel LGA1851', 'AMD AM5'], 'On the CPU': ['AMD AM4']},
                 'The socket type decides how you handle the chip.'), HW),
        '3-connectors-you-must-point-to': X('3. Connectors you must point to', 'IT-2.1', S1, [
            ('PC turns on then instantly off, no POST. Which connector?', '4/8-pin EPS by the CPU', 'The SATA data cable to the drive', 'The front USB header',
             'Missing CPU power (EPS) gives no POST or instant off.', EPS, EPS),
            ('Which connector is main board power?', '24-pin ATX', '8-pin EPS', 'SATA power',
             'The 24-pin ATX feeds the motherboard; EPS feeds the CPU.', EPS, None),
            ('In the house-wiring story, why does one loose fuse matter?', 'One missing feed stops it all', 'Fuses are only there for decoration', 'Only lights need fuses',
             'A single missing connector can make a whole PC look dead.', EPS, None),
            ('Power button does nothing but everything else is fine. Check?', 'Front-panel header pins', 'The RAM channel layout on the board', 'The M.2 notch',
             'Wrong front-panel pins make a working PC look dead.', EPS, None),
            ('What holds an M.2 stick in place?', 'A screw at the end', 'A SATA latch and clip', 'A 24-pin clip',
             'M.2 sits in a short slot and is held by a screw at its end.', BS, None),
        ],
            P('Learn to point at these. The 24-pin ATX plug powers the board. The 4 or 8-pin EPS plug sits near the CPU. Without it, there is no POST or the PC turns off at once. The RAM slots are colour-paired for channels. The M.2 slot takes a short stick with a screw at the end. SATA is an L-shaped data plug with separate power. On the front-panel header, wrong pins make a good PC seem dead.'),
            P('In a house, the lights, the oven and the boiler each need their own feed from the fuse board. If the oven circuit is off, the cooker '
              'is dead even though the lights work, and an electrician checks the fuse before replacing the oven. PC connectors are those circuits. '
              'Missing CPU power or a front-panel plug on the wrong pins makes a perfectly good machine look broken.'),
            ['24-pin ATX on the board edge.', '4/8-pin EPS near the CPU.', 'RAM slots, colour-paired.', 'M.2 slot with end screw.', 'SATA data plus PSU power.',
             'Front-panel header pins.'],
            '<p>Match each symptom to the connector to check.</p>',
            sort('Symptom to connector', {'8-pin EPS': ['Instant off, no POST'], 'Front-panel header': ['Power button does nothing'],
                                          'SATA power': ['Drive not detected, data cable fine'], '24-pin ATX': ['No fans, no LEDs at all']},
                 'Check the connection before blaming the part.'), BUILD),
        'what-a-motherboard-is-for': _P2[('2.1', 'what-a-motherboard-is-for')],
        'teach-block-boards-and-boxes': _P2[('2.1', 'teach-block-boards-and-boxes')],
    },
    '2.2': {
        'firmware-before-windows-from-zero': X('Firmware before Windows — from zero', 'IT-2.2', S2, [
            ('What runs first when you press power?', 'UEFI/BIOS firmware', 'Windows login screen', 'The web browser',
             'Firmware runs POST and then starts a bootloader, which starts the OS.', FWO, FWO),
            ('What is POST?', 'Firmware checking CPU, RAM, disk', 'A Windows update check after login', 'A network login',
             'POST is the power-on self-test done by firmware before any OS.', FWO, None),
            ('In the theatre story, who checks the stage before the show?', 'The stage manager (firmware)', 'The lead actor on stage (Windows)', 'The audience',
             'Firmware checks the stage before the OS performs.', FWO, None),
            ('In the boot trace, what comes after POST?', 'Bootloader', 'Desktop apps', 'Shutdown',
             'POST, then bootloader, then the operating system.', FWO, None),
            ('No beep and no logo means you may be…', 'Still in power or POST', 'Inside Windows already', 'Online and updating',
             'Without a logo, the problem is before Windows.', POST, FWO),
        ],
            P('Pressing the power button does not start Windows directly. A small program stored on the motherboard, UEFI (often still called BIOS), '
              'runs first. It checks that a CPU, memory and disk are there; that check is POST. Then it starts a bootloader, which starts Windows. If '
              'you see no logo at all, the problem is still in power or POST, not Windows.'),
            P('Before a theatre show, the stage manager walks the stage: lights working, props in place, curtains moving. Only then does the lead '
              'actor walk on. If the curtain never opens, nobody blames the actor’s acting. Firmware is the stage manager, POST is the walk-round, and '
              'Windows is the actor. No logo means the curtain never opened.'),
            ['Press power.', 'Firmware runs POST: CPU, memory, disk?', 'Firmware starts the bootloader.', 'Bootloader starts Windows.'],
            '<p>Order the start-up chain.</p>',
            order('Start-up chain', ['Power on', 'Firmware POST', 'Bootloader', 'Operating system'], 'Firmware always comes before Windows.'), HW),
        '1-uefi-versus-the-bios-screen': X('1. UEFI versus “the BIOS screen”', 'IT-2.2', S2, [
            ('Modern boards run what?', 'UEFI', 'Only legacy BIOS', 'Windows directly',
             'People still say BIOS, but modern boards run UEFI.', FWO, FWO),
            ('Windows is up. Supported way into firmware?', 'Settings → Recovery → Advanced → UEFI', 'Pull the power cord out during boot', 'Press keys at random',
             'The supported path is through Recovery advanced start-up.', FWM, None),
            ('In the old-and-new-phone story, what changed?', 'Same job, more features', 'A totally different job', 'Nothing at all',
             'UEFI does the BIOS job with larger disks, mouse support and Secure Boot.', FWO, None),
            ('Trace step 3 restarts into what?', 'UEFI Firmware Settings', 'Safe Mode with networking', 'A new Windows install',
             'The Recovery path restarts straight into firmware settings.', FWO, None),
            ('Why not yank power to force the BIOS on a production box?', 'It risks data and damage', 'It is too slow to work reliably', 'BIOS ignores it',
             'Forced power-off can corrupt data; use the supported path.', FWM, None),
        ],
            P('People still say “BIOS,” but modern computers use UEFI. It does the same job and adds support for big disks, a mouse and Secure Boot. '
              'If Windows is running, reach it through Settings → System → Recovery → Advanced start-up → UEFI Firmware Settings. Do not pull the power '
              'on a working computer just to get into the setup screen.'),
            P('Your old phone made calls; your new smartphone also makes calls, but adds a touchscreen, apps and fingerprint unlock. People still say '
              '“phone” for both. UEFI is the smartphone version of BIOS: same core job, more features. And just as you would not pull the battery out '
              'of a phone to reach its settings, you use the proper menu path to reach firmware.'),
            ['Open Settings → System → Recovery.', 'Advanced start-up → Restart now.', 'Troubleshoot → Advanced options.', 'UEFI Firmware Settings → Restart.'],
            '<p>Order the supported path into firmware.</p>',
            order('Into UEFI', ['Settings Recovery', 'Advanced start-up', 'Troubleshoot', 'UEFI Firmware Settings'], 'Use the supported path.'), HW),
        '2-secure-boot': X('2. Secure Boot', 'IT-2.2', S2, [
            ('What does Secure Boot allow to start?', 'Only signed bootloaders', 'Any USB stick that is plugged in', 'Only Windows updates',
             'Firmware starts only a signed bootloader, which blocks some bootkits.', SB, SB),
            ('A shop USB installer will not boot. Check first?', 'Secure Boot setting', 'Buy a new USB stick', 'Replace the motherboard',
             'Secure Boot may be blocking an unsigned installer; check before declaring the disk bad.', SB, SB),
            ('In the guest-list story, who gets in?', 'Only names on the list', 'Anyone who knocks loudly', 'Only staff members',
             'Secure Boot admits only signed loaders, like a door with a list.', SB, None),
            ('Allowing an unsigned USB temporarily is…', 'A change with rollback', 'Not worth recording in the ticket', 'A permanent fix',
             'Turning Secure Boot off is a change that must be reverted.', FWM, SB),
            ('What threat does Secure Boot help block?', 'Some bootkits', 'Phishing emails', 'Paper jams',
             'It stops unsigned boot-time malware from starting.', SB, None),
        ],
            P('With Secure Boot on, the firmware will start only a bootloader that carries a trusted signature. That stops some boot-time malware. '
              'It also stops an unsigned USB installer. If a shop disk will not boot, check Secure Boot before deciding the disk is faulty, and if you '
              'turn it off to run the tool, record it and turn it back on.'),
            P('At an exclusive party, the bouncer has a guest list. If your name is not on it, you do not get in, however good your outfit. That '
              'keeps gatecrashers out. It also keeps out your friend who forgot to RSVP. Secure Boot is the bouncer for start-up code. Malware is the '
              'gatecrasher; an unsigned shop USB is the friend. Letting the friend in once is fine, as long as you put the rope back afterwards.'),
            ['USB will not boot.', 'Check Secure Boot in UEFI.', 'If needed, allow temporarily and record it.', 'Run the tool.', 'Turn Secure Boot back on.'],
            '<p>Write the ticket line for a temporary Secure Boot change.</p>',
            reveal('Ticket line?', '“1020 Secure Boot off to boot shop diagnostic USB; 1045 diagnostics done; Secure Boot on, Windows boots normally.”'), HW),
        '3-settings-that-fake-hardware-failure': X('3. Settings that fake hardware failure', 'IT-2.2', S2, [
            ('“No OS found” but the NVMe is healthy. Likely cause?', 'Wrong boot order', 'A dead CPU fan bearing', 'Faulty RAM slot',
             'Boot order pointing at the wrong device fakes a missing OS.', FWO, POST),
            ('Random POST failures after enabling XMP suggest…', 'Memory profile too fast', 'A broken monitor cable or port', 'A failed network card',
             'An XMP profile the stick cannot run causes random POST failures.', FWO, None),
            ('In the stage-lighting story, why check the switchboard first?', 'A setting can mimic a dead bulb', 'Bulbs never fail in theatres at all', 'Switchboards are new',
             'A wrong setting can look exactly like failed hardware.', FWO, None),
            ('How do you change firmware settings?', 'One at a time, test, record', 'All at once to save time at the bench', 'Reset everything first',
             'One change, save, test, write it down.', FWM, FWM),
            ('Internal video off and no GPU fitted gives…', 'No display', 'Faster booting', 'A louder fan',
             'With no video path enabled, the screen stays blank.', FWO, None),
        ],
            P('Some firmware settings make healthy hardware look broken. A wrong boot order says “no operating system” when the drive is fine. Legacy '
              'or CSM mode can block a UEFI-only disk. A memory XMP profile the RAM cannot handle causes random POST failures. Turning off built-in '
              'video with no graphics card leaves a blank screen. Change one setting, save, test and write it down.'),
            P('In a theatre, a lighting technician sees a dark stage and assumes the bulbs have blown. Before climbing the rig, a wiser colleague '
              'checks the lighting desk and finds the fader pulled down. Firmware settings are the faders. Boot order, CSM, XMP and video settings can '
              'all make good hardware look dead, so check the desk before climbing the ladder with a new bulb.'),
            ['“No OS”? Check boot order.', 'UEFI disk? Check CSM/Legacy is off.', 'Random POST? Check XMP.', 'Blank screen? Check internal video setting.',
             'One change, save, test, record.'],
            '<p>Match each symptom to the setting.</p>',
            sort('Symptom to setting', {'Boot order': ['“No OS found”, disk healthy'], 'XMP profile': ['Random POST failures'],
                                        'Internal video': ['Blank screen, no GPU'], 'CSM/Legacy': ['UEFI disk will not boot']},
                 'Settings can fake failures.'), HW),
        'firmware-is-not-windows': _P2[('2.2', 'firmware-is-not-windows')],
    },
    '2.3': {
        '1-socket-first': X('1. Socket first', 'IT-2.1', S3, [
            ('The CPU does not drop in flat. What do you do?', 'Stop and realign', 'Press down firmly', 'Close the lever anyway',
             'If it does not sit flat it is misaligned; pressing bends pins.', SF, SF),
            ('On an AM4 CPU, where are the pins?', 'On the chip', 'In the socket', 'On the cooler',
             'AM4 has pins on the CPU; never set it on a screw.', SF, None),
            ('In the jigsaw story, why not force a piece?', 'Forcing breaks it', 'It is faster that way', 'Pieces bend back',
             'A piece that fits drops in; forcing damages it, like a CPU.', SF, None),
            ('Trace step 2 opens what fully?', 'The load lever', 'The case side panel', 'The PSU switch',
             'Open the lever fully before seating the CPU.', SF, None),
            ('LGA CPU: what must you not touch?', 'The pads on the chip', 'The box label', 'The heat spreader top',
             'Do not scrape LGA pads; protect socket pins.', SF, None),
        ],
            P('Read the socket name on the board and on the CPU box before you start. LGA chips have flat pads; do not scrape them. AM4 chips have '
              'pins; never rest one on a screw. AM5 is LGA like Intel, so protect the pins in the socket. Open the lever all the way, place the chip, '
              'close it. If it does not drop in flat, it is not lined up; do not press.'),
            P('A jigsaw piece that belongs in a spot drops in with no effort. If you have to push, it is the wrong piece or turned the wrong way, and '
              'pushing just bends the tabs. A CPU is a very expensive jigsaw piece with hundreds of tiny tabs. The triangle marking shows the right '
              'way round; if it does not sit flat by itself, lift it and look again.'),
            ['Match socket and CPU names.', 'Open the load lever fully.', 'Align the triangle mark.', 'Lower the CPU; it must sit flat.', 'Close the lever.'],
            '<p>Order the CPU seating steps.</p>',
            order('Seat the CPU', ['Match socket', 'Open lever', 'Align mark', 'Lower flat', 'Close lever'], 'Never press a CPU in.'), BUILD),
        '2-cooler-is-part-of-the-cpu': X('2. Cooler is part of the CPU', 'IT-2.1', S3, [
            ('PC shuts down after 10 minutes; firmware shows 0 RPM. Likely?', 'Fan on SYS_FAN header', 'Windows needs updating', 'Bad SATA cable',
             'A cooler on the wrong header shows 0 RPM and can trigger protection.', FAN, FAN),
            ('How much thermal paste?', 'A thin, even film', 'A large glob in the centre', 'None at all',
             'Thin and even transfers heat; a glob or nothing does not.', PASTE, PASTE),
            ('In the car-radiator story, what happens without coolant?', 'The engine overheats', 'It runs faster and smoother', 'Nothing changes',
             'A CPU without proper cooling throttles or shuts down.', FAN, None),
            ('Trace step 3 plugs the fan where?', 'CPU_FAN', 'SYS_FAN', 'USB header',
             'CPU_FAN lets firmware read RPM and protect the chip.', FAN, None),
            ('No cooler at all leads to…', 'Throttling or shutdown', 'Better performance under load', 'Quieter running',
             'Without a cooler the CPU overheats.', FAN, None),
        ],
            P('A CPU without a working cooler will slow itself down or shut off. Check the backplate and a thin, even layer of paste. Plug the fan or pump into CPU_FAN so firmware can see its speed. A “good” CPU that turns off after ten minutes often has its fan on the wrong header. Firmware then reads zero RPM.'),
            P('A car engine has a radiator and coolant. Run it with the hose disconnected and it overheats and cuts out, even though the engine '
              'itself is fine. Mechanics check the cooling system before replacing an engine. The CPU cooler is the radiator, the paste is the coolant '
              'seal, and CPU_FAN is the temperature gauge on the dashboard. Zero on the gauge means check the wiring first.'),
            ['Fit the backplate.', 'Apply a thin, even film of paste.', 'Seat the cooler flat.', 'Plug the fan into CPU_FAN.', 'Check RPM in firmware.'],
            '<p>Diagnose this case.</p>',
            reveal('New build shuts down at 10 min; firmware CPU fan 0 RPM, fan spins. Cause?', 'Fan cable on SYS_FAN, not CPU_FAN. Move it, confirm RPM in firmware, retest.'), BUILD),
        '3-performance-without-myth': X('3. Performance without myth', 'IT-2.1', S3, [
            ('Firmware does not list the CPU. What is it?', 'A support-list problem', 'Just a slow chip from the factory', 'A Windows setting',
             'If firmware cannot identify the CPU, check the board’s support list and firmware version.', SF, FWO),
            ('What three checks does this course use?', 'Part, firmware sees it, RPM', 'Benchmarks, overclock, RGB lighting', 'Price, brand, colour',
             'Identify, confirm firmware detection, confirm cooler speed.', FAN, SF),
            ('In the guest-badge story, what does a missing badge mean?', 'Not on the list yet', 'The guest is slow', 'Badges are optional',
             'An unlisted CPU needs support, not a speed fix.', SF, None),
            ('In the trace, after identifying the part you…', 'Confirm firmware sees it', 'Install some games to test speed', 'Order a faster CPU',
             'Detection in firmware comes before anything else.', FWO, None),
            ('Cooler RPM matters because…', 'Overheating slows the CPU', 'RPM sets the CPU clock speed directly', 'It changes the socket',
             'Without cooling the CPU throttles, which looks like poor performance.', FAN, None),
        ],
            P('In this course, judging CPU performance is simple. Know which part it is. Check that firmware lists it. Check that the cooler fan spins at a sensible speed. If firmware does not show the CPU, the board may not support it yet. That is a support-list or firmware-version problem, not a slow chip.'),
            P('At a conference, a speaker with no badge is stopped at the door. It is not that they are a poor speaker; their name simply is not on '
              'the list yet. Someone must update the list. A CPU that firmware does not recognise is that speaker. Talk of slow chips is a myth here: '
              'check the support list and firmware version, then check the cooling.'),
            ['Identify the CPU model.', 'Does firmware list it?', 'If not: check support list and firmware version.', 'Check cooler RPM.'],
            '<p>Sort each finding into its cause.</p>',
            sort('Finding to cause', {'Support list / firmware': ['CPU not listed in firmware'], 'Cooling': ['0 RPM, shuts down hot', 'Throttles under load', 'Paste missing']},
                 'Check identity, detection and cooling.'), HW),
        'cpu-cooler-header': _P2[('2.3', 'cpu-cooler-header')],
        'motherboards-cpu-architectures-firmware-security-and-add-on': X('Motherboards, CPU architectures, firmware security and add-on cards', 'IT-2.1', S3, [
            ('Which CPU architecture do most phones and some laptops use?', 'ARM', 'x86 only', 'PowerPC only',
             'ARM dominates phones and appears in some laptops; x64 is Intel/AMD.', SF, None),
            ('Which board is 244 × 244 mm?', 'microATX', 'ATX (305 × 244)', 'mini-ITX (170 × 170)',
             'microATX is 244 mm square.', FF, FF),
            ('In the house-extension story, what is an add-on card?', 'An extension on the house', 'A new foundation under the house', 'Paint on the walls',
             'Add-on cards extend the board’s abilities through expansion slots.', SF, None),
            ('Which firmware feature checks signed bootloaders?', 'Secure Boot', 'XMP profile', 'Wake-on-LAN',
             'Secure Boot verifies signatures; XMP and Wake-on-LAN do other jobs.', SB, None),
            ('64-bit x86 is also called…', 'x64 or x86-64', 'ARM64 only, never Intel', 'IA-16',
             'x64 and x86-64 name 64-bit Intel/AMD architecture.', SF, None),
        ],
            P('A+ Core 1 objective 3.5 covers motherboards, CPUs and add-on cards. Know the form factors in millimetres: ATX 305 × 244, microATX '
              '244 × 244, mini-ITX 170 × 170. Know CPU architectures: x86/x64 from Intel and AMD, and ARM in phones and many newer laptops. Know '
              'firmware security such as Secure Boot and TPM, and that expansion cards add features through slots like PCIe.'),
            P('A house has a size and plot (form factor), a type of construction such as brick or timber (CPU architecture), locks and an alarm '
              '(firmware security), and you can build extensions like a conservatory or garage (add-on cards). A buyer asks about all four. The '
              'exam asks the same about a PC: what size, what kind of brain, how it is secured, and how it can be extended.'),
            ['Form factor: ATX, microATX, mini-ITX in mm.', 'Architecture: x64 or ARM.', 'Firmware security: Secure Boot, TPM.', 'Add-on cards: PCIe slots.'],
            '<p>Sort each item into its category.</p>',
            sort('Category', {'Form factor': ['microATX', 'mini-ITX'], 'Architecture': ['ARM', 'x64'], 'Firmware security': ['Secure Boot']},
                 'Four categories the exam expects.'), HW),
    },
    '2.4': {
        'memory-from-zero': X('Memory from zero', 'IT-2.3', S4, [
            ('RAM is best described as…', 'A workspace', 'A filing cabinet', 'A power source',
             'RAM is temporary workspace; the disk is the filing cabinet.', RS, RS),
            ('RAM missing or unseated usually gives…', 'Beeps and no Windows', 'Slower internet browsing only', 'A louder fan only',
             'Without usable RAM the system cannot start, so you get beeps and no OS.', POST, None),
            ('In the desk story, what is the desk surface?', 'RAM', 'The drawers', 'The lamp',
             'The desk surface is temporary workspace like RAM; drawers store like a disk.', RS, None),
            ('In the trace, can DDR4 go in a DDR5 slot?', 'No; the notch differs', 'Yes, with firm pressure on both ends', 'Yes if filed',
             'Generations have different notches; never force or file.', NOTCH, NOTCH),
            ('Which is the filing cabinet in this analogy?', 'The disk', 'The RAM sticks', 'The CPU cache',
             'Storage keeps files; RAM is workspace.', RS, None),
        ],
            P('RAM is where the computer works on things right now. It is not where files are kept; that is the disk. If RAM is missing or loose, '
              'the computer often cannot start at all, so you hear beeps and Windows never appears. DDR4 and DDR5 are different generations with the '
              'notch in a different place, so they cannot be swapped. Never file a notch.'),
            P('Picture an office desk. The drawers hold all your folders (the disk). The desk surface is where you spread out the papers you are using '
              'now (RAM). A bigger desk lets you work on more at once, but at the end of the day you clear it. Take the desk away entirely and you '
              'cannot work at all, even though every folder is safe in the drawers.'),
            ['RAM = workspace; disk = storage.', 'No RAM → beeps, no Windows.', 'Check generation: DDR4 or DDR5.', 'Match the notch; never force.'],
            '<p>Sort each statement into RAM or storage.</p>',
            sort('RAM or storage?', {'RAM': ['Cleared at power-off', 'Workspace for running apps'], 'Storage': ['Keeps files overnight', 'SSD or HDD']},
                 'Workspace versus filing cabinet.'), HW),
        '1-generation-and-notch': X('1. Generation and notch', 'IT-2.3', S4, [
            ('A DIMM resists going in. What does that tell you?', 'It may be the wrong generation', 'Push harder until it finally clicks in', 'File the notch down',
             'Resistance is information; the notch prevents mixing generations.', NOTCH, NOTCH),
            ('How do DDR4 and DDR5 differ visibly?', 'The notch position', 'The colour of the PCB', 'The label brand',
             'The notch is offset differently on purpose.', NOTCH, None),
            ('In the key-and-lock story, why does a wrong key stick?', 'It is cut for another lock', 'The lock is rusty inside', 'Keys bend easily',
             'A notch is like a key cut; the wrong one will not turn.', NOTCH, None),
            ('In the trace, the slot fights you. Next step?', 'Stop and check', 'Use more force', 'Try a hammer',
             'Stop, compare generation, then retry correctly.', NOTCH, None),
            ('From two feet away DDR4 and DDR5 look…', 'Very similar', 'Totally different', 'Different colours',
             'They look alike; check the notch and label.', NOTCH, None),
        ],
            P('DDR4 and DDR5 memory sticks look almost the same from a distance. The difference is the notch, a small gap in the gold edge, which '
              'sits in a different spot on each. If the slot resists, that resistance is telling you something: stop and check the generation.'),
            P('Two house keys can look nearly identical on a keyring, but only one turns your front-door lock. If a key sticks halfway, you do not '
              'force it with pliers; you check you have the right key. The notch on a memory stick is the key cut. The slot is the lock. When it '
              'sticks, look at the key.'),
            ['Read the module label: DDR4 or DDR5.', 'Read the board’s supported memory.', 'Line up the notch.', 'If it resists, stop.'],
            '<p>Decide what to do.</p>',
            reveal('A new stick will not seat in the board; label says DDR4, board is DDR5. Next?', 'Stop. Wrong generation. Return it and fit a DDR5 module matching the board’s list.'), HW),
        '2-channels': X('2. Channels', 'IT-2.3', S4, [
            ('Two matched sticks go where for dual channel?', 'The paired slots the manual marks', 'Any two empty slots that are free', 'Slots 1 and 2 always',
             'Use the slots the board marks as a channel, often 2 and 4.', CH, CH),
            ('What do you match first?', 'Size and generation', 'Colour of the heatsink', 'Brand of the box',
             'Match size and generation first; speed second.', CH, None),
            ('In the two-lane road story, why use both lanes?', 'More traffic flows', 'Lanes look nicer', 'It is required by law',
             'Dual channel lets memory traffic flow on two paths.', CH, None),
            ('Four unmatched kits POST then blue-screen. Cause?', 'Mismatched memory', 'A bad DNS server', 'A loose monitor cable',
             'Unmatched kits can POST and still be unstable.', CH, None),
            ('Does one stick work?', 'Yes, single channel', 'No, never without a pair', 'Only on Mini-ITX',
             'One stick works, just without dual channel.', CH, None),
        ],
            P('Put two matching sticks in the paired slots the board manual shows, often slots 2 and 4, and they run in dual channel. One stick works '
              'fine too. Mixing four sticks from different kits can pass POST and then crash. Match size and generation first, then speed.'),
            P('A road with two lanes moves twice the traffic of a single lane, but only if both lanes go the same way and have the same speed limit. '
              'Mix a motorway lane with a dirt track and the fast cars get stuck. Dual-channel memory is that two-lane road. The board paints which '
              'slots are the lanes, and matched sticks keep traffic flowing.'),
            ['Read the manual’s slot pairs.', 'Match size and generation.', 'Install in the marked pair.', 'Check About shows the full RAM.'],
            '<p>Place two sticks correctly.</p>',
            order('Dual channel', ['Read the manual', 'Match the sticks', 'Use the marked pair', 'Confirm RAM in About'], 'Manual first, then slots.'), ABOUT),
        '3-when-ram-looks-like-a-dead-board': X('3. When RAM looks like a dead board', 'IT-2.3', S4, [
            ('No video after “just adding memory.” First step?', 'Reseat both sticks', 'Replace the motherboard', 'Reinstall Windows',
             'Reseat, then test one known-good stick in A2.', POST, POST),
            ('Which slot for the single known-good stick test?', 'A2', 'The last slot', 'Any slot',
             'This course uses A2 for the single-stick test.', CH, None),
            ('In the jammed-drawer story, why check the runners first?', 'Simple causes first', 'Drawers are expensive', 'Runners are hidden',
             'Reseat memory before condemning the board.', POST, None),
            ('In the trace, firmware is cleared only when…', 'Shop procedure says so', 'Every time memory is changed', 'Never under any case',
             'Clearing firmware is a change done only under procedure.', FWM, None),
            ('What do you do with each test?', 'Write it down', 'Keep it in your head', 'Tell nobody',
             'Record action → result for each test.', SHOT, None),
        ],
            P('If the screen stays black after someone added memory, the board is usually fine. Reseat both sticks. Then try one stick you know is '
              'good in slot A2. Only clear the firmware settings if your shop procedure says so. Write down every test and its result.'),
            P('When a kitchen drawer suddenly jams after you put something new in it, you do not rip out the cabinet. You take the new thing out, '
              'check the runners and try again. Memory that “kills” a board is usually a jammed drawer: not seated, or the wrong slot. Reseat, test '
              'one known-good stick, and keep a note of what you tried.'),
            ['Power off, unplug, strap on.', 'Reseat both sticks.', 'Test one known-good stick in A2.', 'Clear firmware only per procedure.', 'Record each result.'],
            '<p>Order the tests.</p>',
            order('RAM isolation', ['Reseat both', 'One known-good in A2', 'Clear firmware if procedure', 'Record results'], 'Cheapest test first.'), HW),
        'memory-generation-and-channels': _P2[('2.4', 'memory-generation-and-channels')],
        'reference-memory-generations-and-form-factors': X('Reference — memory generations and form factors', 'IT-2.3', S4, [
            ('Desktop DDR4 and DDR5 modules both have how many pins?', '288', '260', '204',
             'Both are 288-pin DIMMs, with the notch in a different place.', NOTCH, None),
            ('Where is DDR5 power regulated?', 'On the module (PMIC)', 'On the PSU rail only', 'In the CPU cooler',
             'DDR5 moves power regulation onto the module.', NOTCH, None),
            ('In the shoe-size story, why do sizes matter?', 'Each fits one kind of foot', 'Sizes are only for fashion', 'All shoes fit',
             'DIMM and SO-DIMM sizes fit desktop or laptop slots respectively.', NOTCH, None),
            ('Laptop DDR5 module type?', '262-pin SO-DIMM', '288-pin desktop DIMM', '240-pin DIMM',
             'Laptop DDR5 is a 262-pin SO-DIMM; some use CAMM2 or soldered memory.', NOTCH, None),
            ('DDR5 nominal voltage?', '1.1 V', '1.5 V', '3.3 V',
             'DDR5 is 1.1 V; DDR4 is 1.2 V.', NOTCH, None),
        ],
            P('Quick facts. Desktop DDR4 and DDR5 are both 288-pin DIMMs, but the notch sits in a different place. Laptop DDR4 is a 260-pin SO-DIMM; '
              'laptop DDR5 is a 262-pin SO-DIMM, and some new laptops use CAMM2 or soldered memory. DDR4 runs at 1.2 V with power controlled on the '
              'board; DDR5 at 1.1 V with a power chip on the module, and two sub-channels per stick.'),
            P('Shoes come in sizes and types: a boot, a trainer, a child’s shoe. A size 9 boot and a size 9 trainer are the same length but not the '
              'same shoe. Memory is the same. Desktop and laptop sticks are different shapes, and DDR4 and DDR5 are different types even at the same '
              'length. The reference table is the shoe-size chart that tells you which fits.'),
            ['Desktop: 288-pin DIMM (DDR4 or DDR5).', 'Laptop DDR4: 260-pin SO-DIMM.', 'Laptop DDR5: 262-pin SO-DIMM or CAMM2/soldered.', 'Voltage: DDR4 1.2 V, DDR5 1.1 V.'],
            '<p>Sort each fact by generation.</p>',
            sort('DDR4 or DDR5?', {'DDR4': ['1.2 V', '260-pin SO-DIMM'], 'DDR5': ['1.1 V', 'PMIC on module', '262-pin SO-DIMM']},
                 'Read the chart, not the colour.'), HW),
    },
    '2.5': {
        '1-order-of-work': X('1. Order of work', 'IT-2.3', S5, [
            ('Which comes first in the order of work?', 'Power at wall and PSU', 'Windows settings and updates', 'Firmware boot order',
             'Start with power, then LEDs, beeps, display, firmware, Windows.', POST, POST),
            ('Fixing Windows on a box that never left POST is…', 'Skipping steps', 'A good shortcut', 'Required first',
             'Skipping steps wastes time on the wrong layer.', POST, None),
            ('In the climbing-stairs story, why not skip to the top?', 'Each step supports the next', 'Stairs are slow to climb', 'Lifts are broken',
             'Each layer depends on the one below.', POST, None),
            ('After a beep or debug code, what is next?', 'Display', 'Windows', 'Power',
             'Order: power, LED/fan, beep, display, firmware, Windows.', POST, None),
            ('Fans twitch but no beep. Which stage?', 'POST', 'Windows', 'Display only',
             'Power is present; the fault is at POST.', POST, None),
        ],
            P('Start at the bottom and climb. Is electricity reaching the computer? Does anything light up or spin when the button is pressed? '
              'Does it beep or show a code? Is there a picture? Does the setup screen look right? Only then think about Windows. Jumping ahead means '
              'repairing software on a machine that never got as far as loading it.'),
            P('A staircase only works one step at a time. Try to jump from the bottom to the fifth step and you fall. Troubleshooting a dead PC is '
              'the staircase: power, signs of life, beeps, picture, firmware, Windows. Every step stands on the one below, so you climb in order and '
              'stop where the first step fails.'),
            ['Power at wall and PSU switch.', 'LED or fan twitch?', 'Beep or debug code.', 'Display.', 'Firmware.', 'Windows.'],
            '<p>Order the six stages.</p>',
            order('Order of work', ['Power', 'LED / fan', 'Beep / code', 'Display', 'Firmware', 'Windows'], 'Stop at the first stage that fails.'), HW),
        '2-beeps-on-this-courses-bench-card': X('2. Beeps on this course’s bench card', 'IT-2.3', S5, [
            ('Long beeps or “MEM” on this card mean?', 'Memory', 'Display path', 'Power supply',
             'On this course card, long beeps / MEM point to memory.', POST, POST),
            ('Do all vendors share one beep codebook?', 'No', 'Yes, always', 'Only for Intel',
             'Codes differ by vendor; use the card for this lab.', POST, None),
            ('In the Morse-code story, why carry the right chart?', 'Codes differ by sender', 'Charts look more official', 'Morse is easy',
             'Beep codes depend on the vendor; read the right chart.', POST, None),
            ('One short beep means what here?', 'POST OK; check display', 'Memory test failed', 'PSU not delivering power',
             'One short beep is POST OK; look at display and cables next.', POST, None),
            ('No beep and no fan suggests…', 'Power or board', 'A RAM fault only', 'A DNS fault',
             'Nothing at all means power or board.', POST, None),
        ],
            P('Each manufacturer has its own beep codes, so use this course’s card for the lab. One short beep: POST passed, check the display. '
              'Repeated short beeps: display path. Long beeps or “MEM”: memory. No beep and no fan: power or board. The seeded card in the lab gives '
              'long beeps and MEM, so the answer is post memory.'),
            P('Morse code operators on different ships used different private codebooks. Hearing “three long, one short” meant nothing without the '
              'right book. Beep codes are the same: a long beep on one brand means memory, on another something else. This bench card is your '
              'codebook for the lab, and you read it before you decide.'),
            ['Listen to the pattern.', 'Find it on this course card.', '1 short → post ok.', 'Repeating short → post display.', 'Long / MEM → post memory.', 'Nothing → post power.'],
            '<p>Match each beep to its code.</p>',
            sort('Beep to code', {'post ok': ['One short beep'], 'post display': ['Repeating short beeps'], 'post memory': ['Long beeps', 'MEM LED'],
                                  'post power': ['No beep, no fan']},
                 'Use this course’s card.'), HW),
        '3-storage-word-for-the-card': X('3. Storage word for the card', 'IT-2.1', S5, [
            ('An M.2 stick in the short slot is named?', 'storage nvme', 'storage sata', 'storage samsung',
             'Name the interface, not the brand: M.2 NVMe is storage nvme.', BS, BS),
            ('A 2.5 in drive in a SATA tray is?', 'storage sata', 'storage nvme', 'storage usb',
             'The SATA interface gives storage sata.', BS, None),
            ('In the road-type story, what do you name?', 'The road, not the car', 'The car’s make and model', 'The driver’s name',
             'You name the interface (road), not the brand (car).', BS, None),
            ('In the trace, what decides the word?', 'The interface', 'The capacity', 'The colour',
             'Interface decides: NVMe or SATA.', BS, None),
            ('Why not write the brand?', 'The card asks for interface', 'Brands change often', 'Brands are too long to type',
             'The lab wants the interface word.', BS, None),
        ],
            P('For the bench card, name the storage by how it connects, not who made it. An M.2 stick in the short slot is “storage nvme.” A 2.5-inch '
              'drive in a SATA tray is “storage sata.” The brand and capacity can go in the note. The card wants the connection word.'),
            P('If someone asks how you got to work, “a Ford” is not the answer they want; “the motorway” or “the back roads” is. The road decides '
              'how fast and how you get there. Storage interfaces are roads: NVMe is the motorway straight to the CPU, SATA the older A-road. The '
              'brand on the drive is just the car.'),
            ['Look at the drive.', 'M.2 in the short slot → storage nvme.', '2.5 in in a SATA tray → storage sata.', 'Write the interface word.'],
            '<p>Sort each drive into its word.</p>',
            sort('Storage word', {'storage nvme': ['M.2 stick with end screw', 'Short slot on the board'], 'storage sata': ['2.5 in drive in tray', 'L-shaped data cable']},
                 'Interface, not brand.'), HW),
        'post-order': _P2[('2.5', 'post-order')],
        'teach-block-three-neighborhoods': _P2[('2.5', 'teach-block-three-neighborhoods')],
    },
    '2.6': {
        '1-about-is-the-polite-inventory': X('1. About is the polite inventory', 'IT-2.4', S6, [
            ('Where is the polite inventory with the user watching?', 'Settings → System → About', 'diskpart list disk', 'The registry editor (regedit)',
             'About shows name, edition, processor and RAM without risk.', WIPE, None),
            ('About RAM disagrees with the DIMM count. Next?', 'Check seating and firmware', 'Reimage the PC first', 'Order a replacement DIMM',
             'A mismatch is a seating or firmware problem; go back to 2.4.', POST, WIPE),
            ('In the hotel-check-in story, why read the booking first?', 'Confirm facts before acting', 'It is the polite thing', 'Guests expect a short wait',
             'About confirms facts before you change anything.', WIPE, None),
            ('Trace step 3 compares About RAM with…', 'The sticks on the board', 'The monitor resolution', 'The Wi-Fi adapter list',
             'Reconcile OS-reported RAM with installed DIMMs.', POST, None),
            ('Which facts does About show?', 'Name, edition, CPU, RAM', 'Saved passwords, keys', 'Browser history',
             'About lists device name, edition, processor and RAM.', SHOT, None),
        ],
            P('Settings → System → About is the inventory you can do while the user watches. It shows the device name, Windows edition, processor '
              'and how much RAM Windows sees. Does that RAM figure disagree with the sticks on the board? Then it is a seating or firmware problem. Go back to lesson 2.4. Do not reimage yet.'),
            P('At a hotel desk the receptionist first reads your booking aloud: name, dates, room type. If the booking says one night and you '
              'expected three, you sort that out before handing over a key. About is the booking read-back. If the RAM it reports does not match what '
              'is physically fitted, that is the mismatch to resolve before anything else.'),
            ['Open Settings → System → About.', 'Note device name and edition.', 'Note processor and RAM.', 'Compare RAM with the DIMMs fitted.'],
            '<p>Open About and record the four facts.</p>',
            order('About inventory', ['Open About', 'Device name', 'Edition', 'Processor and RAM', 'Compare with DIMMs'], 'Read, then reconcile.'), ABOUT),
        '2-cli-identity': X('2. CLI identity', 'IT-2.4', S6, [
            ('Which command shows the account you are using?', 'whoami', 'hostname', 'systeminfo',
             'whoami shows the signed-in account; hostname shows the PC name.', SHOT, None),
            ('What goes in the ticket from systeminfo?', 'The few lines that answer it', 'Twenty pages of output', 'A screenshot of all of it',
             'Pull the four lines that answer the question.', SHOT, SHOT),
            ('In the ID-card story, why check name and photo?', 'They show who and what', 'Cards look official', 'It is a rule at every desk',
             'hostname and whoami answer which PC and which account.', SHOT, None),
            ('In the trace, how do you page systeminfo?', 'Pipe to more', 'Print it all', 'Email it',
             'systeminfo | more lets you read it page by page.', SHOT, None),
            ('hostname shows…', 'The name on the wire', 'The signed-in user account', 'The Windows build',
             'hostname gives the computer’s network name.', SHOT, None),
        ],
            P('Three commands tell you who and what. hostname gives the computer’s network name. whoami gives the account you are really using. '
              'systeminfo gives the edition, build, install date and updates; pipe it to more to read it page by page. Copy only the lines that '
              'answer the question into the ticket.'),
            P('A security guard checking an ID card looks at two things: the name and the photo. They do not read the small print on the back to '
              'confirm who you are. hostname is the machine’s name; whoami is the person holding the card. systeminfo is the small print, useful '
              'when needed, but only the relevant lines go in your report.'),
            ['hostname: name on the wire.', 'whoami: account in use.', 'systeminfo | more: edition, build, hotfixes.', 'Copy the lines that answer the question.'],
            '<p>Match each command to what it shows.</p>',
            sort('Command to fact', {'hostname': ['NOVAK-W11-07'], 'whoami': ['ciwt\\student'], 'systeminfo': ['Windows 11 Education 25H2', 'Install date']},
                 'Each command answers one question.'), ('win-hostname', 'Run hostname, whoami and systeminfo and note the key lines.')),
        '3-list-disk-before-any-wipe': X('3. List disk before any wipe', 'IT-2.4', S6, [
            ('Which diskpart command is allowed in Block 2?', 'list disk', 'clean', 'convert gpt',
             'Only list disk; clean and convert are not Block 2 commands.', WIPE, WIPE),
            ('What do size and GPT/MBR tell you?', 'Which disk handle is which', 'The CPU speed and cores', 'The RAM channel layout',
             'They identify the disk before anyone touches it.', WIPE, None),
            ('In the surgery-marker story, why mark the limb first?', 'To avoid the wrong one', 'It looks more neat', 'It saves surgery time',
             'list disk marks which disk is which before any action.', WIPE, None),
            ('In the trace, after listing you…', 'Exit', 'Clean Disk 0', 'Convert to MBR',
             'If the lab only asks to list, you list and exit.', WIPE, None),
            ('Why never clean in this course?', 'It wipes the disk', 'It is too slow', 'It needs internet',
             'clean destroys partitions and data.', WIPE, None),
        ],
            P('Open diskpart and type list disk. The size of each disk and whether it is GPT or MBR tell you which disk is which before anything '
              'is touched. clean and convert are not part of this block. If the lab asks you to list, you list and then exit.'),
            P('Before an operation, surgeons draw an arrow on the correct leg with a marker pen, and the whole team checks it. It sounds obvious, yet '
              'it stops the worst mistake in medicine. list disk is your marker pen: it names Disk 0 and Disk 1 by size and layout so nobody wipes '
              'the wrong one. In this course you only mark; you never operate.'),
            ['Open diskpart.', 'list disk.', 'Note size and GPT/MBR for each.', 'exit.'],
            '<p>Order the safe diskpart steps.</p>',
            order('Safe diskpart', ['Open diskpart', 'list disk', 'Note size and layout', 'exit'], 'List only; never clean.'), ('win-hostname', 'Inventory the guest; list disks only.')),
        '4-note-that-ties-block-1-to-block-2': X('4. Note that ties Block 1 to Block 2', 'IT-2.4', S6, [
            ('Which line belongs in the inventory note?', '“RAM 16 GB matches two DDR5”', '“PC looks fine, RAM OK”', '“Wiped Disk 1 to check speed”',
             'The note reconciles OS RAM with installed sticks.', SHOT, WIPE),
            ('What does the note say about wiping?', 'No wipe', 'Wiped both disks', 'Wipe next week',
             'This block never wipes; it states “no wipe.”', WIPE, WIPE),
            ('In the handover story, why list stock and next steps?', 'The next shift continues', 'Lists look tidy', 'Managers want more detail',
             'The note lets the next person act without guessing.', SHOT, None),
            ('What is the next step in the example?', 'Image Disk 0 after backup', 'Clean Disk 1 right now', 'Replace both DIMMs',
             'Next: image only Disk 0 after backup confirmation.', WIPE, None),
            ('The note ties Block 1 to Block 2 by…', 'Ticket habits plus hardware facts', 'Using more technical words', 'Adding photos of the open case',
             'Block 1 ticket discipline meets Block 2 inventory facts.', SHOT, None),
        ],
            P('Your note should read like a short report a stranger could act on. Say which computer and which Windows it runs. Say whether the '
              'memory Windows reports matches the sticks you can see. List the disks and which one holds the system. State plainly that nothing was '
              'erased, and finish with what should happen next.'),
            P('At the end of a shift in a warehouse, the supervisor leaves a note: what is in stock, what does not match the books, what was not '
              'touched, and what the next shift should do. The incoming team can start straight away. Your inventory note is that handover: what '
              'the PC is, whether hardware and OS agree, what you did not do, and the next step.'),
            ['Name and edition/build.', 'RAM the OS sees vs sticks fitted.', 'list disk handles.', '“No wipe.”', 'Next step.'],
            '<p>Write the four-line inventory.</p>',
            reveal('Four-line inventory for a PC with 8 GB in About but two 8 GB sticks?', '“PC118, Win 11 Pro 25H2. About 8 GB vs 2×8 GB DDR5 fitted → reseat/firmware check. Disk 0 512 GB GPT OS. No wipe; next: reseat DIMMs.”'), ABOUT),
        'inventory-before-you-change-the-box': _P2[('2.6', 'inventory-before-you-change-the-box')],
        'teach-block-inventory-is-a-document': _P2[('2.6', 'teach-block-inventory-is-a-document')],
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '2.1': {'start-here-the-parts-inside-the-box': '7256e5862d9a', '1-form-factor-is-the-hole-pattern': '88cb51e74595', '2-chipset-and-sockets-names': '32bad90140df', '3-connectors-you-must-point-to': '2af22e748c63'},
    '2.2': {'firmware-before-windows-from-zero': 'bf9793aac863', '1-uefi-versus-the-bios-screen': '0315aee9b2f9', '2-secure-boot': '1166b0be5e06', '3-settings-that-fake-hardware-failure': 'ac1c211db22c'},
    '2.3': {'1-socket-first': '2b891df69ced', '2-cooler-is-part-of-the-cpu': 'be00ea086b5c', '3-performance-without-myth': '8e69b4b38069', 'motherboards-cpu-architectures-firmware-security-and-add-on': '787c5b340deb'},
    '2.4': {'memory-from-zero': 'cea0518df322', '1-generation-and-notch': 'd0baab4795f8', '2-channels': '8af2b34a90fa', '3-when-ram-looks-like-a-dead-board': 'e085b94c446f', 'reference-memory-generations-and-form-factors': '38e3b5447a8c'},
    '2.5': {'1-order-of-work': 'd05f5a889a04', '2-beeps-on-this-courses-bench-card': 'c3a7dc3b928c', '3-storage-word-for-the-card': '344242507680'},
    '2.6': {'1-about-is-the-polite-inventory': 'c87fe724ba68', '2-cli-identity': 'c437f34ad2ce', '3-list-disk-before-any-wipe': '2fafb787adeb', '4-note-that-ties-block-1-to-block-2': '216e02483853'},
}
