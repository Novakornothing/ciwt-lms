"""Option B pass 3 — ITSUP chapter 2 bespoke ladders for the last ten same_as sections. Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import P3
from curriculum_v2.ladder.schema import order, reveal, sort

_P = 'MC-L-IT2-'
BFF, STO, SOCK, EPS, FWOS, SBD, FWM, FAN, PASTE, RAMS, NOTCH, CHAN, POSTS, BSTOR, WIPE, SHOT = (_P + k for k in (
    'BRAND-FF', 'STANDOFF', 'SOCKET-FORCE', 'EPS-SKIP', 'FW-IS-OS', 'SB-BAD-DISK', 'FW-MANY', 'FAN-HEADER', 'PASTE',
    'RAM-STORAGE', 'NOTCH', 'CHANNEL-ANY', 'POST-SKIP', 'BRAND-STOR', 'WIPE-FIRST', 'SCREENSHOT'))
HW = ('hw-board', 'Identify the board, socket, memory and storage on the bench card, then name the POST line.')
BUILD = ('hw-pc-build', 'Assemble the parts in order and check each connection before power-on.')
ABOUT = ('gui-about', 'Read Settings → System → About and compare RAM with the DIMMs on the board.')
SECS = {}


def _s(n, t):
    return f'Course lesson 2.{n} “{t}” (the original section), re-explained'


def _add(label, sid, src, *a):
    SECS[(label, sid)] = P3('ITSUP', label, sid, src, *a)


S1, S2, S3, S4, S5, S6 = (_s(1, 'Motherboards'), _s(2, 'Firmware'), _s(3, 'CPU and cooling'), _s(4, 'Memory'),
                          _s(5, 'POST and isolation'), _s(6, 'Inventory'))

# ------------------------------------------------------------------ 2.1
_add('2.1', 'what-form-factor-means-if-you-have-never-heard-it', S1, [
    ('A listing says “ATX-style mini board”. What decides if it fits the case?', 'Its measured size and holes', 'The brand in the title',
     'The word “mini” in the listing', 'Form factor is a size and mounting-hole standard you measure, not a marketing word.', BFF, BFF),
    ('Which is the smallest of the three common desktop boards?', 'Mini-ITX', 'microATX', 'ATX',
     'Mini-ITX is smaller than microATX, which is smaller than full ATX.', BFF, BFF),
    ('In the shoe story, what plays the part of the shoe size?', 'The form factor', 'The shoe brand', 'The shop that sold it',
     'Shoe size, like form factor, is a measured standard; the brand does not change whether it fits.', BFF, BSTOR),
    ('The chart shows 9.6 × 9.6 in. Which form factor is that?', 'microATX', 'Full ATX', 'Mini-ITX',
     'The course card board measures 9.6 × 9.6 in, which is microATX.', BFF, BFF),
    ('Holes do not line up with the case standoffs. What is true?', 'It is the wrong board', 'Add extra standoffs', 'It is almost the right one',
     'If the holes do not line up, the board is the wrong form factor; extra standoffs can short the board.', STO, BFF),
], ([
    'Form factor means the size of a motherboard.',
    'It also means where the screw holes are.',
    'Size and holes decide which case the board fits.',
    'ATX is the big common desktop board.',
    'microATX is smaller. Our course card is 9.6 by 9.6 inches.',
    'Mini-ITX is the smallest of the three.',
    'A shop title may say anything. Trust a ruler instead.',
], 'Measure the board and match the holes; the name on the box is not the form factor.'), (
    'Think about buying shoes online. The brand and the colour are on the photo, but what matters is the size. A size 9 '
    'fits a size 9 foot, whatever the brand. A board is the same: the case only cares about the outline and the holes.',
    [('Shoe size', 'form factor (ATX, microATX, Mini-ITX)'), ('Brand on the box', 'name in the shop title'),
     ('Your foot', 'the case and its standoffs'), ('Trying the shoe on', 'lining up holes before you screw down')],
    'Shoes stretch a little. A board never does: a hole that is a few millimetres off means the wrong board.'),
    ('flow', 'Three common board sizes, large to small', ['ATX: most slots', 'microATX: 9.6 × 9.6 in', 'Mini-ITX: fewest slots']),
    'Read the chart left to right. Each step down in size loses expansion slots and memory slots but fits a smaller case. '
    'The course card sits in the middle box.',
    'Open the bench card and find the board size printed on it. Say the form factor out loud before you look at any other part.',
    sort('Sort each fact into what it tells you.', {'Form factor': ['9.6 × 9.6 in', 'Mounting hole pattern'],
                                                    'Not form factor': ['Brand name', 'Colour of the heatsinks']},
         'Only size and hole pattern decide the fit.'), HW)

_add('2.1', 'what-a-motherboard-is-for', S1, [
    ('What does a motherboard do for the other parts?', 'Lets them work as one system', 'Stores all of the user’s files', 'Runs the apps for Windows',
     'The board is the backplane that connects CPU, memory, storage and cards; storage keeps files.', RAMS, BFF),
    ('A CPU will not drop into the socket. What should you do?', 'Check orientation and socket', 'Press harder on it until it sits', 'Bend a pin back',
     'If the chip will not drop in, orientation or socket type is wrong; force destroys the CPU and socket.', SOCK, SOCK),
    ('In the city story, the roads stand for what?', 'The board’s traces and slots', 'The CPU’s cores and its cache', 'The case fans',
     'The roads are the paths on the board that let the parts reach each other.', RAMS, FAN),
    ('In the picture, which part decides the CPU family?', 'Socket and chipset', 'The form factor size', 'The case colour',
     'Socket and chipset decide which CPU family fits; form factor decides which case fits.', BFF, SOCK),
    ('Last step before you latch the CPU?', 'Seat it with no force', 'Push down hard on the chip', 'Add paste in the socket',
     'Seat the chip flat with no force, then latch. Paste goes on top of the heat spreader, never in the socket.', SOCK, PASTE),
], ([
    'A motherboard joins all the parts of a PC.',
    'The CPU, memory, storage and cards plug into it.',
    'The socket and chipset decide which CPU fits.',
    'Bigger boards have more slots. Smaller boards fit smaller cases.',
    'A CPU should drop into the socket with no force.',
    'If it does not drop in, stop. Check the arrow and the socket name.',
    'A bent pin can ruin the CPU and the board.',
], 'The board connects everything; seat the CPU gently, then latch.'), (
    'A motherboard is like a town’s road network. Houses, shops and the town hall only work together because roads join '
    'them. The town hall needs a plot of the right shape, and you cannot squeeze a bigger building onto a small plot.',
    [('Roads', 'traces and slots on the board'), ('Town hall', 'the CPU'), ('Plot shape', 'socket type'),
     ('Town size', 'form factor and number of slots')],
    'A building can be adapted on site. A CPU cannot: a wrong socket means a different part, never a firmer push.'),
    ('two', 'What each feature of the board decides', (('Feature', ['Form factor', 'Socket and chipset', 'Slot count']),
                                                        ('Decides', ['Which case fits', 'Which CPU family fits', 'How many cards and DIMMs'])))
    , 'The left column is the board feature and the right column is the choice it controls. A mistake in the middle row is '
    'the one that breaks parts.',
    'On the build bench, place the CPU by lining up the arrow with the socket mark. Note whether it dropped in without any force.',
    order('Put the CPU install steps in order.', ['Match arrow to socket mark', 'Lower the chip, no force', 'Close the latch',
                                                  'Note “seated, latched” in the ticket'], 'Seat first, latch second, write it down.'), BUILD)

_add('2.1', 'teach-block-boards-and-boxes', S1, [
    ('A ticket asks for “an ATX board for a small office PC”. What is missing?', 'The measured size and socket', 'The board’s colour and brand',
     'A faster brand name', 'The ticket should record measured size and socket so the right board arrives.', BFF, BSTOR),
    ('What do you give up by going Mini-ITX?', 'Slots and RAM count', 'The CPU socket itself', 'The ability to boot',
     'Mini-ITX trades expansion slots, DIMM count and GPU clearance for a small case.', BFF, BFF),
    ('In the furniture story, what is the doorway?', 'The case size', 'The CPU socket', 'The seller',
     'The doorway is the case: a too-big sofa (board) cannot pass, whatever the brand.', BFF, SOCK),
    ('The chart compares two boards. Which gains a small case?', 'Mini-ITX', 'Full ATX', 'Both equally',
     'Mini-ITX is the small-case option; ATX keeps the slots.', BFF, BFF),
    ('Cooler does not match the socket. Teacher’s rule?', 'Do not make it work', 'Drill new holes', 'Hold it on with cable ties',
     'Socket silkscreen is law: a mismatched cooler is the wrong part, not a puzzle.', SOCK, SOCK),
], ([
    'This block is for the teacher.',
    'Spend one full period on form factor.',
    'Students measure the board or read the card.',
    'The card says 9.6 by 9.6 inches. That is microATX.',
    'They list what Mini-ITX loses: slots, RAM, card space.',
    'They list what it gains: a small case.',
    'Then they read the socket name on the board.',
], 'Students should write size and socket on every parts ticket.'), (
    'Picture ordering a sofa for a small flat. The shop says “family size”. It arrives and will not fit through the door. '
    'The order should have said the width in centimetres and the door width. A board order is the same.',
    [('Sofa width', 'board size in inches'), ('Door', 'the case'), ('“Family size”', 'vague words like ATX-style'),
     ('Tape measure', 'ruler on the board')],
    'A sofa can be turned on its side. A board cannot be rotated to fit; the holes are fixed.'),
    ('two', 'microATX versus Mini-ITX', (('microATX', ['More slots', 'Four DIMMs often', 'Room for a big GPU']),
                                         ('Mini-ITX', ['One slot', 'Two DIMMs', 'Small case']))),
    'Each column lists what a student should say. The trade is simple: smaller case, fewer places to plug things in.',
    'With a ruler or the bench card, write a one-line parts ticket: measured size, form factor and socket. No brand names.',
    reveal('A student writes “ATX board, small office”. Rewrite it.', 'microATX, 9.6 × 9.6 in, socket LGA1700.'), HW)

# ------------------------------------------------------------------ 2.2
_add('2.2', 'firmware-is-not-windows', S2, [
    ('A PC shows “no boot device”. Which is the first suspect?', 'Firmware boot order', 'A corrupt Windows file', 'The monitor cable',
     'Before Windows starts, firmware picks the boot device; wrong boot order looks like a dead Windows.', FWOS, FWOS),
    ('A shop USB installer will not start. Why might that be?', 'Secure Boot blocks it', 'The USB stick is dead', 'Windows refused it',
     'Secure Boot only starts signed bootloaders; the stick is often fine.', SBD, FWOS),
    ('In the theatre story, who is the stage manager?', 'UEFI firmware', 'The Windows desktop', 'The audience',
     'Firmware checks the stage (POST) and calls the first act (bootloader) before the show (Windows).', FWOS, FWOS),
    ('In the flow, what runs right after POST?', 'The bootloader', 'Windows apps and services', 'A second POST',
     'POST checks hardware, then firmware starts a bootloader, which starts the OS.', FWOS, FWOS),
    ('How many firmware settings do you change per test?', 'One, then reboot', 'Six from a forum', 'All the defaults',
     'One change, save, watch the boot, write action → result. Many changes hide the cause.', FWM, FWM),
], ([
    'UEFI is firmware. It runs before Windows.',
    'First it checks the hardware. That check is POST.',
    'Then it starts a bootloader from a disk.',
    'A wrong boot order can look like a dead Windows.',
    'Secure Boot only starts signed bootloaders.',
    'That can block a shop USB stick.',
    'Change one setting at a time. Write what happened.',
], 'Firmware comes first; change one setting, reboot, record the result.'), (
    'A theatre show has a stage manager who checks lights and props, then calls the first actor. If the manager calls the '
    'wrong actor, the play looks broken, but the script is fine. Secure Boot is the manager checking each actor’s badge.',
    [('Stage manager', 'UEFI firmware'), ('Checking lights and props', 'POST'), ('First actor', 'bootloader'),
     ('Badge check', 'Secure Boot signature check')],
    'A stage manager can improvise. Firmware does exactly what its settings say, so a single wrong setting fails every time.'),
    ('flow', 'Power on to Windows', ['Power on', 'POST checks', 'Boot order', 'Secure Boot check', 'Bootloader', 'Windows'], 2),
    'The red box shows where a wrong boot order stops the chain. Everything after it never runs, so Windows is not the place '
    'to start fixing.',
    'Write a one-line change record: the firmware setting you would change, its old value, its new value and how to undo it.',
    order('Order a safe firmware change.', ['Note current value', 'Change one setting', 'Save and reboot', 'Write action → result'],
          'One change, one result line.'), HW)

# ------------------------------------------------------------------ 2.3
_add('2.3', 'cpu-cooler-header', S3, [
    ('Firmware shows 0 RPM for the CPU fan after a build. Likely cause?', 'Wrong fan header', 'A dead brand-new CPU', 'Too much RAM',
     'Zero RPM right after a build is often the cable on a system-fan header, not a dead fan.', FAN, RAMS),
    ('How much thermal paste goes on the heat spreader?', 'A thin, even film', 'A large glob in the middle', 'None at all',
     'Paste fills tiny gaps; a glob insulates and none leaves air gaps.', PASTE, PASTE),
    ('In the kettle story, the paste is like what?', 'Full contact with the hob', 'The kettle’s handle', 'The kitchen fan over the cooker',
     'Paste makes full contact between hot metal and cooler, like a flat kettle on a hob.', PASTE, FAN),
    ('In the chart, where does the cooler cable go?', 'CPU_FAN header', 'SYS_FAN header', 'USB header',
     'The cooler fan plugs into CPU_FAN so firmware can watch it and protect the chip.', FAN, FAN),
    ('What sets airflow in a case?', 'Intake and exhaust fans', 'The side panel airflow sticker', 'The CPU brand',
     'Air moves from intake fans to exhaust fans; stickers do nothing.', FAN, BFF),
], ([
    'The cooler must sit flat on the CPU.',
    'Use a thin film of paste. Not a glob. Not bare metal.',
    'The fan cable goes on the CPU_FAN header.',
    'Firmware watches that header to protect the chip.',
    'Zero RPM after a build is often the wrong header.',
    'Case airflow is intake fans and exhaust fans.',
], 'Flat cooler, thin paste, CPU_FAN header, then check RPM in firmware.'), (
    'Think of a kettle on an electric hob. A flat kettle touching the whole ring heats fast. A warped one with gaps heats '
    'slowly. The CPU and cooler are the same: paste fills the tiny gaps so heat moves across.',
    [('Hob ring', 'CPU heat spreader'), ('Kettle base', 'cooler plate'), ('Flat full contact', 'thin film of paste'),
     ('Smoke alarm wired to the right room', 'fan on the CPU_FAN header')],
    'A kettle that is too cool just boils slowly. A CPU that is too hot throttles or shuts down to protect itself.'),
    ('flow', 'Cooler install check', ['Thin paste film', 'Cooler flat', 'Cable on CPU_FAN', 'Firmware shows RPM']),
    'Each box must pass before the next. If the last box shows zero RPM, go back one box and check the header first.',
    'On the build bench, find the CPU_FAN header label. Write its name and the RPM you expect to see in firmware.',
    reveal('Firmware shows CPU fan 0 RPM, fan spins. First check?', 'Move the cable to the CPU_FAN header and recheck.'), BUILD)

# ------------------------------------------------------------------ 2.4
_add('2.4', 'memory-generation-and-channels', S4, [
    ('A DDR4 stick will not fit a DDR5 slot. What should you do?', 'Get a DDR5 stick', 'File the notch', 'Press until it clicks in',
     'The notch is placed differently on purpose; filing or forcing ruins the board.', NOTCH, NOTCH),
    ('Two sticks for dual-channel go where?', 'Slots the manual marks', 'Any two empty slots', 'The two nearest the CPU',
     'Dual-channel needs the slot pair the manual names, often slots 2 and 4.', CHAN, CHAN),
    ('In the key story, the notch is like what?', 'The key’s cut pattern', 'The key ring that holds it', 'The door colour',
     'A notch, like a key cut, only fits the matching lock (slot generation).', NOTCH, RAMS),
    ('In the chart, which slots make the usual pair?', 'Slots 2 and 4', 'Slots 1 and 2', 'Slots 3 and 4',
     'Most manuals paint slots 2 and 4 (A2/B2) as the first pair.', CHAN, CHAN),
    ('About shows less RAM than you installed. Next step?', 'Reseat, check firmware', 'Reimage Windows from USB', 'Buy bigger RAM',
     'Missing RAM is seating or firmware first; the OS image is not the cause.', POSTS, RAMS),
], ([
    'DDR4 and DDR5 do not swap.',
    'The notch is in a different place on purpose.',
    'Never file a notch. That can kill the board.',
    'For dual-channel, use the slots the manual marks.',
    'That is often slot 2 and slot 4.',
    'If Windows shows less RAM, reseat the sticks.',
    'Check firmware before you reinstall anything.',
], 'Match the generation, follow the manual’s slot pair, and reseat before you reimage.'), (
    'Memory sticks are like keys. A house key and a car key may look alike, but the cuts differ so the wrong one will not '
    'turn. Two people carrying shopping through two doors at once is dual-channel: each door must be one the plan names.',
    [('Key cut', 'DIMM notch'), ('Lock', 'DDR4 or DDR5 slot'), ('Two doors used together', 'dual-channel pair'),
     ('Floor plan', 'motherboard manual')],
    'You can copy a key. You cannot reshape a DIMM: the notch protects the board from the wrong voltage.'),
    ('two', 'Four slots, one pair', (('Use for a pair', ['Slot 2 (A2)', 'Slot 4 (B2)']), ('Leave empty', ['Slot 1 (A1)', 'Slot 3 (B1)']))),
    'This chart is the usual layout. Always confirm in the manual for your board, because some boards paint a different pair.',
    'Open the About page lab. Compare the RAM Windows reports with the DIMMs on the bench card and write both numbers.',
    sort('Sort each action.', {'Do': ['Match DDR generation', 'Use the manual’s slot pair'], 'Never': ['File the notch',
                                                                                                  'Reimage for missing RAM']},
         'Fit and seating come before software.'), ABOUT)

# ------------------------------------------------------------------ 2.5
_add('2.5', 'post-order', S5, [
    ('Memory LED, long beeps, no video. Which area?', 'Memory (POST)', 'The display cable', 'The power supply',
     'A memory LED and beeps mean POST found a memory fault; video comes later.', POSTS, POSTS),
    ('When does display isolation begin?', 'After POST passes', 'Before power checks', 'At the same time',
     'Display work only makes sense once POST has passed.', POSTS, POSTS),
    ('In the airport story, what is the security check?', 'POST', 'The display', 'Windows',
     'POST is the check point everyone passes before boarding (display and OS).', POSTS, FWOS),
    ('In the flow, which box stops a no-twitch, no-LED PC?', 'Power', 'POST', 'Display',
     'No fan twitch and no LED means power: nothing has reached POST.', POSTS, POSTS),
    ('Bench card POST line for hw-board?', 'POST memory', 'POST display', 'POST storage',
     'The course card answer is POST memory; type what the card says.', POSTS, BSTOR),
], ([
    'POST is firmware testing hardware.',
    'It happens before Windows exists.',
    'A memory LED and beeps point to memory.',
    'Check display only after POST is OK.',
    'Check power when nothing twitches and no LED lights.',
    'Do not swap a GPU for loose RAM.',
    'The bench card says POST memory.',
], 'Pick the right neighbourhood first: power, POST or display.'), (
    'Boarding a plane has three gates in order: the entrance, security and the boarding gate. If security stops you, there '
    'is no point checking your seat number. A PC boot has the same order: power, then POST, then display.',
    [('Airport entrance', 'power (fans, LEDs)'), ('Security check', 'POST'), ('Boarding gate', 'display'),
     ('Security alarm', 'memory LED and beeps')],
    'At an airport a guard tells you why. A PC only gives LEDs and beeps, so you must read the manual’s code list.'),
    ('flow', 'Boot isolation order', ['Power: twitch, LED?', 'POST: beeps, codes?', 'Display: picture?'], 1),
    'In this picture the red box is POST. A memory code stops the chain there, so the display box is not reached yet.',
    'Run the hw-board lab and type the POST line from the bench card. Then name the box in the chart where it stops.',
    order('Put the isolation checks in order.', ['Power', 'POST', 'Display'], 'Never jump to display before POST is OK.'), HW)

_add('2.5', 'teach-block-three-neighborhoods', S5, [
    ('Where does every hardware ticket start this week?', 'Pointing at one box', 'Swapping a part', 'Reinstalling Windows',
     'Students point at power, POST or display first; that choice drives the tests.', POSTS, FWOS),
    ('Which box means “no twitch, no LED”?', 'Power', 'POST', 'Display',
     'With no movement and no light, power has not reached the board.', POSTS, POSTS),
    ('In the hospital story, triage is like what?', 'Picking the box', 'Doing surgery', 'Discharging the user',
     'Triage sorts the case before treatment, like picking power, POST or display.', POSTS, POSTS),
    ('In the chart, which box needs POST already OK?', 'Display', 'Power box', 'POST box',
     'Display is only reachable once POST has passed.', POSTS, POSTS),
    ('What does mixing the boxes cause?', 'Replacing the wrong part', 'Faster tickets for the team', 'Better notes',
     'Mixing boxes leads to swaps like a GPU for unseated RAM.', POSTS, POSTS),
], ([
    'This block is for the teacher.',
    'Draw three boxes on the board. Keep them up all week.',
    'Power: no twitch, no LED.',
    'POST: beeps, LEDs or codes.',
    'Display: POST already OK, but no picture.',
    'Each ticket starts by pointing at one box.',
    'Students run hw-board to submit.',
], 'Make students choose power, POST or display before touching anything.'), (
    'In a hospital, triage comes first. A nurse sorts patients into breathing, bleeding and broken bones before any '
    'treatment. Teaching the three boxes is triage for hardware: sort, then treat.',
    [('Triage nurse', 'the student pointing at a box'), ('Breathing', 'power'), ('Bleeding', 'POST'), ('Broken bone', 'display')],
    'Patients can say where it hurts. A PC cannot, so the student must read the signs: twitch, LED, beep, picture.'),
    ('two', 'Signs and the box they point to', (('Sign', ['No twitch, no LED', 'Beeps or LED code', 'POST OK, no picture']),
                                                ('Box', ['Power', 'POST', 'Display']))),
    'Each row pairs one sign with one box. A teacher can point at this chart whenever a student reaches for a spare part.',
    'Give a student the sign “memory LED and three beeps”. Ask them to point to a box and say the first check.',
    sort('Sort each sign into a box.', {'Power': ['No fan twitch'], 'POST': ['Memory LED on', 'Long beeps'],
                                        'Display': ['Beep OK, black screen']}, 'One sign, one box.'), HW)

# ------------------------------------------------------------------ 2.6
_add('2.6', 'inventory-before-you-change-the-box', S6, [
    ('Which four facts go in the inventory?', 'Name, build, RAM, disks', 'Brand, colour and price', 'Wallpaper, apps, user',
     'Name, edition/build, RAM the OS sees and the disk list are the inventory lines.', SHOT, BSTOR),
    ('Which diskpart command is allowed in this course?', 'list disk', 'clean all', 'format',
     'Only list disk; clean wipes a disk and is never run here.', WIPE, WIPE),
    ('In the moving story, the inventory is like what?', 'The box labels', 'The removal van', 'The new house',
     'Labels say what is in each box so the next person does not guess.', SHOT, WIPE),
    ('In the chart, About and the chassis disagree. Which box?', 'Seating or firmware', 'Reimage the PC first', 'Order new disks',
     'A mismatch is a hardware seating or firmware issue, not an image issue.', POSTS, WIPE),
    ('What goes into the ticket?', 'The four answer lines', 'Pages of full screenshots', 'Nothing until done',
     'Write the lines that answer the question so the next technician can trust them.', SHOT, SHOT),
], ([
    'Write an inventory before you change a PC.',
    'Note the name, edition and build.',
    'Note the RAM that Windows sees.',
    'Note the disk list from list disk.',
    'Never run clean in this course.',
    'If About and the box disagree, check seating and firmware.',
    'Put the inventory in the ticket.',
], 'Four inventory lines first, so nobody guesses which disk is the OS disk.'), (
    'Before moving house you label every box: kitchen, books, bathroom. The movers then know what each box holds and '
    'nothing important ends up in the bin. A PC inventory labels the machine before anyone changes it.',
    [('Box labels', 'inventory lines'), ('Kitchen box', 'the OS disk handle'), ('Movers', 'the next technician'),
     ('Bin', 'diskpart clean')],
    'A wrong label on a box costs a search. A wrong disk handle with clean costs the user’s data, which is why clean is banned.'),
    ('flow', 'Inventory before change', ['Name and build', 'RAM seen', 'list disk', 'Compare with chassis', 'Write ticket']),
    'Follow the boxes left to right. If the compare box shows a mismatch, the next step is seating or firmware, not imaging.',
    'Open the About page lab. Copy the name, edition, build and RAM into a four-line inventory note.',
    order('Order the inventory steps.', ['Read name and build', 'Read RAM seen', 'Run list disk', 'Write the four lines'],
          'Read, list, write. No clean.'), ABOUT)

_add('2.6', 'teach-block-inventory-is-a-document', S6, [
    ('What do students hand in for this block?', 'A four-line inventory', 'A freshly reimaged PC', 'A cleaned disk',
     'The deliverable is a written four-line inventory; imaging and clean are out of scope.', WIPE, WIPE),
    ('Where must the inventory appear?', 'Paper and the ticket', 'Only in their head', 'Only on the desktop PC',
     'An inventory is a document: it goes on paper and in the ticket.', SHOT, SHOT),
    ('In the library story, the catalogue card is like what?', 'The inventory note', 'The book itself', 'The reader’s library card',
     'A catalogue card describes the book so others find it; the inventory describes the PC.', SHOT, BSTOR),
    ('In the chart, which actions are banned?', 'Imaging and clean', 'Reading the About page', 'list disk',
     'Reading About and list disk are allowed; imaging and clean are not.', WIPE, WIPE),
    ('About and chassis disagree. What does the class discuss?', 'Seating and firmware', 'Running setup.exe again', 'A new image',
     'The class stops and talks seating and firmware, not setup.', POSTS, FWOS),
], ([
    'This block is for the teacher.',
    'Each student writes a four-line inventory.',
    'They write it on paper and in the ticket.',
    'Lines: name, edition or build, RAM seen, disk list.',
    'They do not image. They do not clean.',
    'If About and the chassis disagree, stop the class.',
    'Talk about seating and firmware, not setup.',
], 'The inventory is a document students can hand in and others can trust.'), (
    'A library keeps a catalogue card for every book: title, author, shelf. A new librarian can find any book without '
    'opening every shelf. The four-line inventory is the PC’s catalogue card for the next technician.',
    [('Catalogue card', 'four-line inventory'), ('Shelf number', 'disk handle'), ('New librarian', 'next technician'),
     ('Throwing out a book', 'running clean')],
    'Library cards rarely change. A PC inventory goes stale after any change, so it is written again before the next one.'),
    ('two', 'In this block', (('Students do', ['Read About', 'Run list disk', 'Write four lines']),
                              ('Students never', ['Image the PC', 'Run clean', 'Run setup.exe']))),
    'The left column is the whole task. The right column is off limits, even when a student finishes early.',
    'Write your own four-line inventory for the lab PC and paste it into a practice ticket note.',
    reveal('A student’s About shows 8 GB; the bench has two 8 GB sticks. What next?', 'Stop: reseat RAM and check firmware.'), ABOUT)
