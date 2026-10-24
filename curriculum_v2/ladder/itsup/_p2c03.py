"""Option B pass 2 — ITSUP chapter 3 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

_P = 'MC-L-IT3-'
M2, LOST, IMG, SAS, RB, R0, PULL, INIT, OPEN, PSUF, EFF, VOLT, USBC, EARLY, BOARD, CAT, OLED, SHOT, VAGUE = (_P + k for k in (
    'M2-NVME', 'LOST-FILE', 'IMAGE-BLIND', 'SAS-SATA', 'RAID-BACKUP', 'RAID0', 'PULL-SECOND', 'INIT-ARRAY', 'OPEN-PSU', 'PSU-FIRST',
    '80PLUS', 'VOLT-SWITCH', 'USBC-VIDEO', 'DISPLAY-EARLY', 'BOARD-FIRST', 'CAT-SPEED', 'OLED-BACKLIGHT', 'SHOTGUN', 'NOTE-VAGUE'))
DISK = ('w11-disk', 'List the disks, note handle, size and which one holds Windows. Do not run any destructive verb.')
BACK = ('ops-backup', 'Find the last good backup and prove a restore before anyone touches the array.')
BUILD = ('hw-pc-build', 'Seat the 24-pin and the CPU 8-pin, then check each power connection before power-on.')
CAB = ('hw-cables', 'Name each cable and connector, then pick the one the job needs.')
TRI = ('win-full-triage', 'Work one domain at a time and write test, result and next step for each.')


def _s(n, t):
    return f'Course lesson 3.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4, S5 = (_s(1, 'Storage'), _s(2, 'RAID and Backup'), _s(3, 'Power Supplies'), _s(4, 'Display and Cables'),
                      _s(5, 'Unstable Workstation Capstone'))

SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


# ------------------------------------------------------------------ 3.1
_add('3.1', 'hdd-ssd-nvme-without-the-brochure', 'HDD, SSD, NVMe without the brochure', 'IT-3.1', S1, [
    ('Which drive kind can make a clicking noise when it fails?', 'A hard disk (HDD)', 'An NVMe stick in an M.2 slot', 'A SATA SSD in a 2.5-inch case',
     'Only a hard disk has a moving head and platter, so only it can click; flash drives fail silently.', M2, M2),
    ('What three things do you name when you order a drive?', 'Shape, protocol and length', 'Brand, colour and warranty years', 'Capacity only, the rest is automatic',
     'The slot shape, the protocol it speaks and the stick length decide whether the part fits and works.', M2, M2),
    ('In the post-box story, what does the letterbox slot stand for?', 'The M.2 slot shape', 'The NVMe language on the drive', 'The data stored on the drive',
     'The slot shape is the letterbox: it says what fits, not how the mail inside is written.', M2, M2),
    ('In the comparison picture, which drive has no moving parts and uses PCIe?', 'NVMe SSD', 'Hard disk drive', 'Floppy disk drive',
     'NVMe drives are flash chips that talk over PCIe lanes; the hard disk is the one that spins.', M2, M2),
    ('A stick fits the M.2 slot but the label says SATA. Is it NVMe?', 'No, it speaks SATA', 'Yes, every M.2 stick is NVMe', 'Yes, if it is 80 mm long',
     'Fitting the slot proves the shape only; the label tells you the protocol, here SATA.', M2, M2),
],
    (['A hard disk spins a metal platter.', 'A small arm reads it, so it can click when it fails.',
      'An SSD keeps data on chips.', 'It has no moving parts at all.', 'NVMe is a fast way for some SSDs to talk to the board.',
      'M.2 is just the shape of a slot.', 'Some M.2 sticks speak NVMe, and some speak SATA.'],
     'When you order a drive, write the slot shape, the protocol and the length, for example “M.2 2280 NVMe”.'),
    ('Think of a post box on a wall. The slot decides what size of envelope fits. The letter inside can be written in English or French. '
     'A letter that fits the slot is not automatically in the language the reader speaks. An old parcel locker with a spinning carousel is '
     'slower and has parts that wear, but it holds a lot for little money.',
     [('Letterbox slot size', 'M.2 form factor and stick length'), ('Language of the letter', 'Protocol: SATA or NVMe'),
      ('Spinning parcel carousel', 'Hard disk with platter and head'), ('Reader who only knows French', 'A slot wired for NVMe only')],
     'A wrong-language letter still gets delivered; a wrong-protocol drive may simply not be seen at all. Also, drive speed has no real '
     'equivalent in a post box, so judge speed from the protocol, not the story.'),
    ('two', 'Three drive kinds side by side', (('Moving parts', ['HDD: spinning platter and head', 'Can click or report not ready']),
                                               ('Flash chips', ['SATA SSD: SATA cable or M.2 SATA', 'NVMe SSD: M.2 stick over PCIe']))),
     'The left column moves and wears. The right column is silent flash. Both flash drives can sit in M.2, so the slot alone does not say which one you have.',
    'Sort each description under the drive it belongs to. Then say aloud the three words you would put on a parts order.',
    sort('Which drive is it?', {'HDD': ['Spinning platter', 'May click when failing'], 'SATA SSD': ['Uses SATA link speed', 'Can be 2.5-inch'],
                                'NVMe SSD': ['Talks over PCIe lanes', 'Short M.2 stick, fastest']}, 'Shape alone never tells you the protocol.'), DISK)

_add('3.1', 'core-content', 'Core content', 'IT-3.1', S1, [
    ('Which of these is a form factor, not a protocol?', 'M.2 2280', 'NVMe over PCIe lanes', 'SATA at 6 Gb/s',
     'M.2 2280 names a shape and length; NVMe and SATA name how the drive talks to the board.', M2, M2),
    ('What should you record before imaging a drive that may be failing?', 'Its health readings', 'The user’s favourite folder', 'The colour of the drive label',
     'Health first: S.M.A.R.T. or Drive health values tell you whether to copy data before anything else.', IMG, LOST),
    ('In the moving-house story, which question matches “media”?', 'What the boxes are made of', 'Which door the boxes go through', 'How many removal vans you hire',
     'Media is what holds the data, like the box material; the door is the interface and the van size is the form factor.', M2, M2),
    ('In the flow, what comes straight after reading drive health?', 'Copy data if it is failing', 'Order the cheapest drive online', 'Run diskpart clean on it',
     'A failing disk is copied first; ordering and destructive steps come later or never.', IMG, IMG),
    ('A desktop has SATA ports and no M.2 slot. Fastest sensible upgrade?', 'A 2.5-inch SATA SSD', 'An NVMe stick taped inside the case', 'A second spinning hard disk',
     'A SATA SSD uses the existing SATA data and power cables; NVMe needs an M.2 slot or an adapter card.', M2, M2),
],
    (['Every drive choice answers three questions.', 'First, what shape is it?', 'Second, how does it talk to the board?',
      'Third, what holds the data inside?', 'Before you touch a drive, read its health.', 'Get-PhysicalDisk shows health in PowerShell.',
      'If the drive is failing, copy the data first.'],
     'Write shape, protocol and health on the ticket before you order or image anything.'),
    ('Moving house asks three separate questions. How big is each box? Which door will it go through? Is the box cardboard or a '
     'plastic crate? Mixing the questions causes trouble. A crate that fits the door can still be too weak for books. Before you lift a '
     'box that looks damp, you check it, because a soggy box can split and lose everything inside.',
     [('Box size', 'Form factor: 3.5, 2.5 inch or M.2 length'), ('The door it goes through', 'Interface: SATA or NVMe over PCIe'),
      ('Cardboard or plastic crate', 'Media: platter (HDD) or flash (SSD)'), ('Checking a damp box first', 'Reading drive health before imaging')],
     'Boxes do not report their own condition, but drives do through S.M.A.R.T. and the NVMe health log. Use the readings, not a look and a guess.'),
    ('flow', 'Picking or replacing a drive', ['Form factor and length', 'Interface: SATA or NVMe', 'Media: HDD or SSD', 'Read drive health', 'Copy, then order like-for-like']),
     'Read left to right. The first three boxes describe the part. The fourth protects the data. Only the last box spends money.',
    'Put the steps for a “no bootable device” laptop in a safe order, then try the disk lab and read the health fields.',
    order('Replacing a laptop drive', ['Check whether firmware lists any disk', 'Read the parts list for the service tag',
                                       'Note shape, length and protocol', 'Order the like-for-like drive', 'Restore data from backup'],
          'The parts list, not the look of the stick, decides what to order.'), DISK)

_add('3.1', 'm-2-is-the-slot-nvme-is-the-protocol', 'M.2 is the slot, NVMe is the protocol', 'IT-3.1', S1, [
    ('A colleague calls every short stick “NVMe”. What is the risk?', 'The wrong part arrives', 'The drive will run too fast', 'Windows will not need drivers',
     'An M.2 stick can speak SATA, so ordering by the nickname can bring a part the slot will not use.', M2, M2),
    ('Which tool shows disk numbers and sizes without changing anything?', 'diskpart list disk', 'diskpart clean all', 'format C: /q /y',
     'list disk only reads; clean and format destroy data and are out of scope.', IMG, IMG),
    ('In the plug story, what is the language spoken on the line?', 'The protocol', 'The socket shape', 'The cable colour',
     'The socket shape is the slot; what is spoken over it is the protocol, SATA or NVMe.', M2, M2),
    ('In the picture, which failure is silent?', 'A flash drive dying', 'A hard disk head clicking', 'A fan grinding loudly',
     'NAND flash usually dies silently; the hard disk is the one that clicks or reports not ready.', LOST, LOST),
    ('Two disks of the same size appear. How do you tell which is which?', 'Note each handle in list disk', 'Guess from the order they boot', 'Pick the one that feels warmer',
     'list disk numbers each disk; write the handle and size before any later step.', IMG, IMG),
],
    (['M.2 is a slot shape.', 'NVMe is a way of talking.', 'A stick can fit the slot and still speak SATA.',
      'So “M.2” alone is not an order.', 'Hard disks fail with clicks or “not ready” errors.', 'Flash drives often just stop.',
      'To tell disks apart, run list disk.', 'It shows a number and a size for each disk.', 'It changes nothing.'],
     'Name the slot and the protocol separately, and identify disks with list disk only.'),
    ('A wall socket and the conversation on a phone line are two different things. The socket shape says which plug fits. The language '
     'spoken down the line decides if the other side understands. Two phones can use the same socket and speak different languages. '
     'A switchboard operator reads each line number before connecting a call.',
     [('Socket shape', 'M.2 slot and key'), ('Language on the line', 'SATA or NVMe protocol'),
      ('Operator reading line numbers', 'list disk showing handles and sizes'), ('A line that goes dead with no warning', 'Flash drive that fails silently')],
     'A phone line can carry any language at any time, but a slot is wired for set protocols by the board maker. Check the manual, not the socket.'),
    ('two', 'Same slot, different protocol', (('M.2 SATA stick', ['Fits M.2 slot (often B+M key)', 'Talks SATA, about 550 MB/s']),
                                               ('M.2 NVMe stick', ['Fits M.2 slot (usually M key)', 'Talks PCIe, several GB/s']))),
     'Both columns fit the same slot shape. Only the label and the board manual tell you which protocol the slot accepts.',
    'Reveal the answer after you decide how you would identify an unknown stick without opening a box of spares.',
    reveal('A laptop shows two 512 GB disks. How do you prove which one holds Windows before anything else?',
           'Run list disk and note each handle and size, check Disk Management for the C: volume, and write that handle on the ticket.'), DISK)

_add('3.1', 'when-the-disk-is-the-ticket', 'When the disk is the ticket', 'IT-3.1', S1, [
    ('Disk Management shows a disk as Unknown. Which story is this?', 'A disk or partition story', 'Only a lost-file story', 'A printer queue story again',
     'Unknown, inaccessible boot device and no OS are disk or partition faults, not lost files.', LOST, LOST),
    ('A user cannot find a file but the PC boots. What do you check first?', 'Recycle bin and folders', 'Order a replacement SSD', 'Reimage the whole laptop',
     'A healthy volume with a missing file points to delete, wrong folder or backup.', LOST, LOST),
    ('In the car story, what matches a missing file?', 'Keys left in a coat', 'An engine that will not start', 'A flat tyre on the road',
     'Losing the keys does not mean the car is broken; a missing file does not mean the disk failed.', LOST, LOST),
    ('In the picture, what must be written before imaging is discussed?', 'Handle, size and OS disk', 'User’s phone model and case', 'The monitor serial number',
     'Handle, size and whether it is the OS disk let the next person image the right drive.', IMG, IMG),
    ('Which ticket belongs in the disk column?', 'Inaccessible boot device', 'Report saved to Downloads', 'File renamed by mistake',
     'Inaccessible boot device is a storage fault; the others are lost-file stories on a healthy disk.', LOST, LOST),
],
    (['Some tickets really are about the disk.', 'Windows will not start.', 'Or the screen says “inaccessible boot device”.',
      'Or Disk Management shows a disk as Unknown.', 'Other tickets only sound like disk problems.', 'A user cannot find a file, but the PC works fine.',
      'That is not a disk fault.', 'For real disk tickets, write the disk number and size first.'],
     'Decide disk story or file story, and for a disk story write the handle, size and “OS disk: yes or no”.'),
    ('A car that will not start is a mechanic’s job. A driver who cannot find the car keys is not. Both people say “I can’t drive”, but '
     'only one needs a tow truck. Before the tow truck comes, the mechanic writes the number plate and which car it is, so the right '
     'one is towed.',
     [('Car will not start', 'Inaccessible boot device or OS missing'), ('Lost car keys', 'Missing file on a healthy disk'),
      ('Number plate written down', 'Disk handle and size on the ticket'), ('Tow truck', 'Imaging or replacing the disk')],
     'A lost file can still be a real loss if there is no backup, so file stories still need care. They just do not need hardware.'),
    ('two', 'Disk story or file story?', (('Disk story', ['OS will not start', 'Inaccessible boot device', 'Disk shows Unknown']),
                                         ('File story', ['File missing, PC works', 'Saved to another folder', 'Deleted, check backup']))),
     'Only the left column leads to imaging or a part. In both columns, the first line of the ticket says which story you are in.',
    'Sort each ticket line into the right story, then write the three facts you would record for each disk story.',
    sort('Disk or file?', {'Disk story': ['Inaccessible boot device', 'Disk Management: Unknown'],
                           'File story': ['Report missing from Desktop', 'Spreadsheet saved to Downloads']}, 'Only one column needs the disk handle.'), DISK)

_add('3.1', 'teach-block-words-that-order-parts', 'Teach block — words that order parts', 'IT-3.1', S1, [
    ('Which order line will bring the right drive?', 'M.2 2280 NVMe, 512 GB', 'An M.2, as fast as possible', 'Small SSD, any brand will do',
     'Shape with length, protocol and size together describe a part that fits and works.', M2, M2),
    ('Which diskpart verb is allowed in this block?', 'list disk', 'clean', 'convert gpt',
     'Only list disk is allowed; it reads and changes nothing.', IMG, IMG),
    ('In the shoe-shop story, what is the shoe length?', 'The 2280 length code', 'The protocol, NVMe or SATA', 'The drive’s storage capacity',
     'Length must match the standoff, just like shoe size; 2280 means 80 mm long.', M2, M2),
    ('In the picture, what follows “M.2” in a good order?', 'Length and protocol', 'Only the brand name', 'The price and colour',
     'M.2 is only the slot; length and protocol finish the description.', M2, M2),
    ('A hard disk reports “not ready” and clicks. Flash or spinning failure?', 'Spinning disk failure', 'Flash failure, it is silent', 'A cable colour mismatch',
     'Clicks and not-ready errors are spinning-disk symptoms; flash usually dies silently.', LOST, LOST),
],
    (['Ordering a part is a sentence with three words.', 'Say the slot shape: M.2.', 'Say the length: 2280.', 'Say the protocol: NVMe or SATA.',
      '“An M.2” alone is how the wrong stick arrives.', 'Know the failure stories too.', 'Spinning disks click.', 'Flash drives go quiet.',
      'And only list disk is allowed here.'],
     'A good order reads like “M.2 2280 NVMe, 512 GB” and nothing in this block erases a disk.'),
    ('Buying shoes, you say the style, the size and the width. “Trainers, please” gets you any trainer, maybe the wrong size. A shop '
     'assistant who hears “running shoe, size 9, wide” brings one box that fits. The same assistant would never cut a shoe to make it fit.',
     [('Shoe style', 'M.2 slot shape'), ('Shoe size', 'Length code such as 2280'), ('Shoe width', 'Protocol: SATA or NVMe'),
      ('Never cutting the shoe', 'No destructive diskpart verbs')],
     'Shoes stretch a little; drives do not. A drive in the wrong protocol does not half-work, it often is not seen at all.'),
    ('flow', 'Words that order a part', ['Slot: M.2', 'Length: 2280', 'Protocol: NVMe', 'Size: 512 GB', 'Order sent']),
     'Each box adds one fact. Skip any box and the part may not fit or may not be seen. The order goes out only at the end.',
    'Put the words of a parts order in the order you would say them, then compare with a partner’s order line.',
    order('Build the order line', ['Slot shape: M.2', 'Length: 2280', 'Protocol: NVMe', 'Capacity: 512 GB'],
          'Every word answers a different question about fit or function.'), DISK)

# ------------------------------------------------------------------ 3.2
_add('3.2', 'core-content', 'Core content', 'IT-3.2', S2, [
    ('Four 4 TB disks in RAID 5 give how much usable space?', '12 TB', '16 TB', '8 TB',
     'RAID 5 gives (n − 1) × size: three of the four disks hold data, so 12 TB.', R0, R0),
    ('A user deletes a folder on a RAID 1 share. Does the mirror help?', 'No, restore from backup', 'Yes, pull one disk to recover', 'Yes, the mirror undoes deletes',
     'The delete is written to both disks at once; only a separate backup brings it back.', RB, PULL),
    ('In the photocopy story, what is the second copy in another building?', 'An off-site backup', 'A RAID 1 mirror disk', 'A RAID 0 stripe set',
     'The mirror sits in the same box and copies every change; off-site backup is separate.', RB, R0),
    ('In the two-row picture, what answers a ransomware attack?', 'Restore from backup', 'Rebuild the RAID array', 'Add a hot spare disk',
     'Ransomware changes data on every disk; only a separate, tested backup undoes it.', RB, RB),
    ('Which backup type needs the last full plus every one since, in order?', 'Incremental', 'Differential', 'Full only',
     'Incremental saves changes since the last backup of any type, so the whole chain is needed.', RB, RB),
],
    (['RAID joins disks into one volume.', 'It keeps working when a disk dies.', 'That is all it protects.', 'A delete hits every disk at once.',
      'So does ransomware.', 'A backup is a separate copy.', 'You have restored from it at least once.', 'Keep three copies, on two kinds of storage, one off site.'],
     'RAID answers a dead disk; only a tested, separate backup answers deletion, corruption or ransomware.'),
    ('An office keeps important letters in two filing cabinets that always copy each other. If one cabinet falls over, the other still '
     'has every letter. But if someone shreds a letter, the matching copy is shredded too. A photocopy locked in another building is the '
     'only thing that survives the shredder or a fire.',
     [('Two cabinets copying each other', 'RAID 1 mirror'), ('Cabinet falling over', 'One disk failing'),
      ('Shredding a letter', 'User delete or ransomware'), ('Photocopy in another building', 'Off-site backup (3-2-1 rule)')],
     'Cabinets do not slow down when one falls, but a degraded RAID 5 does, and it is at risk until the rebuild ends.'),
    ('two', 'Disk failure versus data loss', (('Disk fails', ['RAID keeps the volume online', 'Replace disk, rebuild', 'Data was never lost']),
                                             ('Data deleted or encrypted', ['RAID copies the damage', 'Every disk now wrong', 'Restore from backup']))),
     'The left column is what RAID was built for. The right column is why backups exist. A ticket must say which column it is in.',
    'Sort each event under the thing that saves you, then work out the RAID 6 capacity of six 2 TB disks.',
    sort('RAID or backup?', {'RAID saves you': ['One disk dies in RAID 1', 'One disk dies in RAID 5'],
                             'Only backup saves you': ['User deletes a folder', 'Ransomware encrypts the share', 'Office fire']},
         'RAID only ever answers a dead disk.'), BACK)

_add('3.2', 'raid-is-not-backup', 'RAID is not backup', 'IT-3.2', S2, [
    ('One disk dies in a RAID 0 volume. What happens?', 'The whole volume is lost', 'It keeps running, just slower', 'The mirror takes over at once',
     'RAID 0 stripes with no redundancy; losing one disk loses all data on the volume.', R0, R0),
    ('What is the minimum number of disks for RAID 5?', 'Three', 'Four', 'Seven',
     'RAID 5 needs at least three disks because one disk’s worth of space holds parity.', R0, R0),
    ('In the notebook story, why is carbon paper not a backup?', 'It copies the mistakes', 'It is far too expensive', 'It only works on Mondays',
     'Carbon paper writes every scribble onto both sheets, as RAID writes every delete to every disk.', RB, RB),
    ('In the picture, which RAID level has no protection column at all?', 'RAID 0', 'RAID 1', 'RAID 5',
     'RAID 0 is striping only: speed with no surviving disk.', R0, R0),
    ('The only copy of the data is on the same array. Do you have a backup?', 'No backup exists', 'Yes, RAID is a backup', 'Yes, if it is RAID 5',
     'A backup is a second copy you can restore; the same array is not separate.', RB, RB),
],
    (['RAID 0 splits data across disks for speed.', 'If one disk dies, everything is gone.', 'RAID 1 keeps two matching disks.',
      'RAID 5 needs three disks.', 'It survives one dead disk.', 'None of them undo a delete.', 'None of them stop ransomware.',
      'A backup is a separate copy you can restore.'],
     'If the only copy lives on the same array, write “no backup” on the ticket.'),
    ('Writing with carbon paper gives you two pages at once. If one page blows away, you still have the other. But a spelling mistake '
     'appears on both pages. Spilled coffee soaks both. A photocopy in a drawer at home is the copy that survives the coffee.',
     [('Two pages at once', 'RAID 1 mirroring'), ('One page blowing away', 'One disk failing'),
      ('Mistake on both pages', 'Delete or ransomware on every disk'), ('Photocopy at home', 'Separate backup copy')],
     'Carbon paper never splits one page across two sheets, but RAID 0 does, which is why one lost disk loses all of it.'),
    ('two', 'What each RAID level survives', (('Survives a dead disk', ['RAID 1: one disk of the pair', 'RAID 5: any one disk']),
                                              ('Survives nothing', ['RAID 0: one failure loses all', 'Any level vs delete or ransomware']))),
     'Even the left column only covers hardware. Nothing on this chart undoes a mistake. That is the job of a backup.',
    'Reveal the answer after you decide what the user loses in each case.',
    reveal('Three cases: RAID 0 loses a disk; RAID 1 loses a disk; a user deletes a file on RAID 5. What is lost in each?',
           'RAID 0: the whole volume. RAID 1: nothing yet, replace the disk. RAID 5 delete: the file, unless a separate backup exists.'), BACK)

_add('3.2', 'rebuild-tax', 'Rebuild tax', 'IT-3.2', S2, [
    ('Why is a degraded RAID 5 array slow?', 'It serves users and rebuilds', 'The disks are getting colder', 'The backup job paused it',
     'A degraded array does two jobs at once: normal input/output and rebuilding the missing data.', PULL, RB),
    ('A second disk dies during a RAID 5 rebuild. Result?', 'The volume is lost', 'The array keeps running', 'Only one folder is lost',
     'RAID 5 survives one failure; a second failure before the rebuild finishes loses the volume.', PULL, R0),
    ('In the bridge story, what is the lane closure?', 'The degraded array', 'A brand-new hot spare', 'A completed backup',
     'One lane closed is one disk gone: traffic still moves but slower and with no spare lane.', PULL, RB),
    ('In the timeline, when is the risk highest?', 'Until the rebuild ends', 'After the rebuild ends', 'Before any disk failed',
     'Between the first failure and the end of the rebuild the array has no redundancy.', PULL, PULL),
    ('The NAS emails “degraded” at 16:30 Friday. First action?', 'Confirm the latest backup', 'Pull a second disk to test', 'Recreate the array fresh',
     'Treat it as an incident: confirm a readable backup before touching any bay.', PULL, INIT),
],
    (['A RAID 5 array with a dead disk is called degraded.', 'It still serves files.', 'At the same time it rebuilds the missing data.',
      'That makes it slow.', 'It also has no spare protection.', 'If a second disk dies now, the volume is gone.', 'So the backup matters most right now.'],
     'Degraded means slow and at risk; check the backup before you touch any disk.'),
    ('A four-lane bridge loses one lane to repairs. Cars still cross, but queues build up while crews work. If a second lane closes '
     'before the repair is done, the bridge shuts. Smart drivers know another route before that happens.',
     [('One lane closed', 'One disk failed, array degraded'), ('Repair crews working', 'The rebuild running'),
      ('Queues of cars', 'Slow file access for users'), ('Another route ready', 'A tested backup')],
     'A bridge lane reopens the moment work stops; a RAID rebuild must finish fully, often for hours, before protection returns.'),
    ('flow', 'A RAID 5 rebuild timeline', ['Disk fails', 'Degraded: slow, at risk', 'Backup confirmed', 'Replace the failed bay', 'Rebuild finishes'], 1),
     'The red box is the danger window. The array is still up, but nothing protects it. Confirm the backup before swapping anything.',
    'Put the Friday degraded-array response in order, then try the backup lab and prove one restore.',
    order('Degraded array response', ['Treat it as an incident', 'Confirm the last backup opens', 'Note the failed bay and model',
                                      'Replace that bay only', 'Warn users while it rebuilds'], 'No other disk is touched while the array is degraded.'), BACK)

_add('3.2', 'teach-block-raid-stories', 'Teach block — RAID stories', 'IT-3.2', S2, [
    ('A user deleted a file on a RAID 1 share. Which fix?', 'Restore from backup', 'Rebuild the mirror', 'Swap the second disk',
     'The delete reached both disks; only a backup restore returns the file.', RB, PULL),
    ('One disk in RAID 1 died. What is true?', 'Volume up; replace the disk', 'All data is gone now', 'The mirror is now a full backup',
     'A mirror survives one failure; replace the disk, but it is still not a backup.', R0, RB),
    ('In the umbrella story, what is the umbrella?', 'RAID parity', 'A backup copy', 'A time machine',
     'An umbrella stops rain, like parity stops a disk failure; it cannot undo yesterday.', RB, RB),
    ('In the picture, which ticket loses data unless a backup exists?', 'RAID 0 volume gone', 'RAID 1 disk died', 'RAID 5 still rebuilding',
     'RAID 0 has no redundancy, so a failed disk means the data is gone without a backup.', R0, R0),
    ('Which sentence should nobody leave the class believing?', 'Parity is a time machine', 'Backups need a test restore', 'RAID 0 has no redundancy',
     'Parity rebuilds a missing disk; it cannot bring back changed or deleted data.', RB, RB),
],
    (['Here are three tickets.', 'First, a user deleted a file.', 'You fix that from backup.', 'Second, one disk in a mirror died.',
      'The share is still up.', 'Replace the disk.', 'Third, a RAID 0 volume is gone.', 'The data is gone too, unless there is a backup.'],
     'Every RAID story ends with the same question: where is the separate backup?'),
    ('An umbrella keeps you dry when it rains. It does not dry the shirt you spilled tea on this morning. A spare shirt in your bag does. '
     'RAID is the umbrella. A backup is the spare shirt.',
     [('Umbrella', 'RAID redundancy or parity'), ('Rain', 'A disk failing'), ('Tea spilled earlier', 'A deleted or encrypted file'),
      ('Spare shirt in the bag', 'Separate tested backup')],
     'An umbrella works for everyone under it, but RAID 0 is an umbrella with a hole: it gives speed and no cover at all.'),
    ('two', 'Three RAID tickets', (('Ticket', ['File deleted on RAID 1', 'One RAID 1 disk died', 'RAID 0 volume gone']),
                                   ('Fix', ['Restore from backup', 'Replace disk, still back up', 'Gone unless backed up']))),
     'Read across each row. Only one row is fixed by the array itself. The other two depend on a backup.',
    'Sort each RAID ticket by what saves the data, then explain one row to a classmate.',
    sort('What saves the data?', {'The array itself': ['One disk died in a RAID 1 mirror', 'One disk died in RAID 6'],
                                  'Only a backup': ['File deleted on RAID 1', 'RAID 0 volume gone']}, 'Parity is never a time machine.'), BACK)

# ------------------------------------------------------------------ 3.3
_add('3.3', 'core-content', 'Core content', 'IT-3.3', S3, [
    ('What does the 80 PLUS badge describe?', 'Efficiency', 'Maximum wattage', 'Cable length',
     '80 PLUS is about how little power is wasted as heat; the wattage label is capacity.', EFF, EFF),
    ('A PC turns off only during games. Which PSU cause fits?', 'Too small for the load', 'Wrong cable colour used', 'A dirty keyboard tray',
     'An undersized PSU often fails under load, not at idle.', EFF, PSUF),
    ('In the kitchen story, what is the fuse box with a battery?', 'A UPS', 'A surge protector', 'The 24-pin cable',
     'A UPS keeps power on from a battery; a surge protector only clamps spikes.', EFF, PSUF),
    ('In the connector map, what feeds the CPU voltage regulators?', '8-pin EPS', '24-pin ATX', 'SATA power',
     'The 8-pin (4+4) EPS connector feeds the CPU; without it, fans spin but many boards will not POST.', PSUF, PSUF),
    ('Why does this course never open a PSU?', 'Capacitors keep a charge', 'It voids the user’s licence', 'The screws are too small',
     'A PSU is a sealed FRU; its capacitors can hold a dangerous charge after unplugging.', OPEN, OPEN),
],
    (['The power supply turns wall power into steady power for parts.', 'It is sealed.', 'You swap it whole and never open it.',
      'The 24-pin plug feeds the board.', 'The 8-pin plug feeds the CPU.', 'Size a new one with room to spare.', 'The 80 PLUS badge means efficiency, not watts.',
      'A surge protector stops spikes.', 'A UPS keeps power on from a battery.'],
     'Match the connectors, leave headroom on watts, and never open the PSU.'),
    ('A house has one main fuse box that splits power to the oven, the lights and the fridge. Each appliance has its own plug. A bigger '
     'oven needs a box that can supply more. A whole-house battery keeps the fridge cold in a power cut; a surge strip only protects '
     'against a lightning spike.',
     [('Main fuse box', 'Power supply unit'), ('Oven, lights, fridge plugs', '24-pin, 8-pin EPS, PCIe and SATA connectors'),
      ('Bigger oven', 'New graphics card that needs more watts'), ('Whole-house battery', 'UPS'), ('Surge strip', 'Surge protector')],
     'You can open a fuse box with care; you never open a PSU. Its capacitors can stay charged after it is unplugged.'),
    ('two', 'Connectors and mains protection', (('Inside the PC', ['24-pin ATX: motherboard', '8-pin EPS: CPU', 'PCIe / 12V-2x6: graphics']),
                                               ('At the wall', ['Surge protector: clamps spikes', 'UPS: battery during outages']))),
     'The left column is about which plug feeds which part. The right column protects against mains problems. Neither column is fixed by opening the PSU.',
    'Sort each fact to the right column, then seat the 24-pin and 8-pin connectors in the build lab.',
    sort('Inside the PC or at the wall?', {'Inside the PC': ['24-pin feeds the board', '8-pin feeds the CPU', 'PCIe feeds the graphics card'],
                                           'At the wall': ['Surge protector clamps spikes', 'UPS runs on battery']}, '80 PLUS is efficiency, not size.'), BUILD)

_add('3.3', 'power-isolation', 'Power isolation', 'IT-3.3', S3, [
    ('No fans and no LEDs. What do you check first?', 'The wall outlet', 'The PSU’s capacitors', 'The graphics driver',
     'Start at the wall and move inward: outlet, switch, 24-pin, 8-pin.', PSUF, OPEN),
    ('Which test is cheaper than a new PSU?', 'A known-good power cord', 'A brand-new motherboard', 'A fresh Windows install',
     'Swapping a cord costs nothing and rules out the cable before buying a PSU.', PSUF, PSUF),
    ('In the lamp story, what matches the CPU 8-pin?', 'The bulb’s own socket', 'The wall socket', 'The fuse box in the hall',
     'Power can reach the lamp base but still miss the bulb, like a board with no 8-pin.', PSUF, PSUF),
    ('In the flow, what comes right after the PSU switch?', 'The 24-pin plug', 'Opening the PSU', 'Replacing the CPU',
     'Wall, switch, 24-pin, 8-pin: each step is one connection further in.', PSUF, OPEN),
    ('You smell burning while swapping a cord. What now?', 'Stop: it is an incident', 'Finish the swap quickly', 'Open the PSU to look',
     'A hot receptacle or burning smell is an incident with the same stop rule as Chapter 1.2.', OPEN, OPEN),
],
    (['The PC shows no fan and no light.', 'Start at the wall socket.', 'Then check the switch on the PSU.', 'Then check the 24-pin plug on the board.',
      'Then check the 8-pin plug for the CPU.', 'Try a cord you know works.', 'It is cheaper than a new PSU.', 'Never open the PSU.', 'If you smell burning, stop.'],
     'Work from the wall inward, one connection at a time, and stop on heat or smell.'),
    ('A desk lamp will not light. You check that the plug is in the wall, the lamp switch is on, and the bulb is screwed in. You do not '
     'take the lamp’s transformer apart. If the socket feels hot or smells, you step away and report it.',
     [('Wall socket', 'Wall outlet'), ('Lamp switch', 'PSU rear switch'), ('Lamp base wiring', '24-pin ATX plug'),
      ('Bulb socket', 'CPU 8-pin EPS plug'), ('Hot smelling socket', 'Safety incident: stop')],
     'A lamp has one path; a PC has two board plugs. Fans can spin with the 24-pin while the missing 8-pin still stops POST.'),
    ('flow', 'Power isolation from the wall in', ['Wall outlet', 'PSU switch', '24-pin ATX', 'CPU 8-pin', 'Known-good cord', 'Replace PSU whole']),
     'Each box is one more connection inward. The last box is a sealed swap, never a repair inside the PSU.',
    'Put the power checks in order, then seat both board plugs in the build lab.',
    order('Dead PC, no fans', ['Check the wall outlet', 'Check the PSU switch', 'Reseat the 24-pin', 'Reseat the CPU 8-pin', 'Try a known-good cord'],
          'Cheap, outside checks always come before buying a part.'), BUILD)

# ------------------------------------------------------------------ 3.4
_add('3.4', 'core-content', 'Core content', 'IT-3.4', S4, [
    ('Does every USB-C port carry video?', 'No, only wired ports do', 'Yes, all USB-C ports do', 'Yes, with any charge cable',
     'Video needs DisplayPort Alt Mode or Thunderbolt on that port, and a cable that supports it.', USBC, USBC),
    ('A projector worked, now the laptop panel is black. First try?', 'Win+P, PC screen only', 'Replace the laptop panel', 'Reinstall the graphics driver',
     'The laptop was probably left in Second screen only; Win+P fixes it in seconds.', BOARD, BOARD),
    ('In the doorway story, what is the oval door?', 'The USB-C connector', 'DisplayPort Alt Mode', 'The graphics driver',
     'The door shape is the connector; what is allowed through depends on the room behind it.', USBC, USBC),
    ('In the flow, what comes straight after power and input?', 'Cable and adapter', 'Graphics driver', 'Known-good display',
     'Swap the cable and adapter next: cheap and likely before a new display or port.', BOARD, BOARD),
    ('A dock charges the laptop but no monitors light. Likely cause?', 'Port without video', 'Monitor needs a firmware update', 'Dock is too far away',
     'The dock may be on a data-and-charge port; the marked Thunderbolt or DP port carries video.', USBC, USBC),
],
    (['USB-C is the shape of a plug.', 'It does not promise what the plug can do.', 'Some ports carry video.', 'Some only carry data and power.',
      'Look for the DisplayPort or Thunderbolt symbol.', 'For a dark screen after POST, start cheap.', 'Check power and the input first.',
      'Then swap the cable.', 'Leave drivers to the end.'],
     'Check the port symbol for video, and work display faults from input and cable toward the graphics card.'),
    ('Every room in a building can have the same oval doorway. One room leads to a cinema. Another is a broom cupboard. The door shape '
     'does not tell you which. A sign on the door does. If the film will not show, you first check the projector is on and the right '
     'channel is chosen, before calling a builder.',
     [('Oval doorway', 'USB-C connector'), ('Sign on the door', 'DisplayPort or Thunderbolt symbol'),
      ('Cinema behind the door', 'Port wired for video'), ('Projector on, right channel', 'Display power and input selected')],
     'Doors do not need special cables, but USB-C does: a charge-only or USB 2.0 cable can block video even on the right port.'),
    ('flow', 'Display isolation after a good POST', ['Power and input', 'Cable and adapter', 'Known-good display', 'Other port or graphics', 'Driver and settings']),
     'Move right only when a box passes. Most tickets end in the first two boxes. Driver work is last.',
    'Put the display checks in order, then name each connector in the cable lab and say which ones carry video.',
    order('Dark monitor after POST', ['Display power and input', 'Swap cable and adapter', 'Try a known-good display', 'Try another output port',
                                      'Check driver and Win+P'], 'Cheap and likely first, graphics hardware last.'), CAB)

_add('3.4', 'display-path-after-post-ok', 'Display path after POST OK', 'IT-3.4', S4, [
    ('When does the display order start?', 'After POST says it is booting', 'Before the power button press', 'During memory beep codes',
     'Only when firmware is trying to boot; earlier dark screens are POST stories.', EARLY, EARLY),
    ('MEM beeps and a dark panel. What is it?', 'A POST memory fault', 'A loose HDMI cable', 'A wrong monitor input',
     'Memory beeps are POST; the display order does not apply yet.', EARLY, BOARD),
    ('In the theatre story, what is the curtain rising?', 'POST finishing', 'The GPU being reseated', 'The cable being swapped',
     'You only judge the stage lights once the curtain is up, as display checks start after POST.', EARLY, EARLY),
    ('In the flow, what is the last step?', 'GPU seating', 'Brightness setting', 'Input selection',
     'Cable, input, brightness, then reseat the graphics card last.', BOARD, BOARD),
    ('POST is OK and the panel is dark. Which first?', 'Check the cable', 'Reseat the GPU', 'Replace the board',
     'Cable and input are cheapest and most likely; hardware comes last.', BOARD, BOARD),
],
    (['First, the PC must pass POST.', 'POST is the self-test at power-on.', 'If it beeps for memory, that is not a display fault.',
      'Once POST is OK, check the cable.', 'Then the input: HDMI or DisplayPort.', 'Then the brightness.', 'Last, reseat the graphics card.'],
     'Start display checks only after POST, and go cable, input, brightness, GPU.'),
    ('In a theatre, you cannot judge the stage lights while the curtain is still down. Once it rises, you check the spotlight plug, then '
     'which switch is chosen, then the dimmer, and only then call the electrician to look at the lamp itself.',
     [('Curtain still down', 'POST not finished, memory beeps'), ('Spotlight plug', 'Display cable'), ('Switch chosen', 'Input: HDMI or DisplayPort'),
      ('Dimmer', 'Brightness'), ('Electrician on the lamp', 'Reseating the graphics card')],
     'A theatre curtain is visible; POST is not always. Listen for beeps or read the board LEDs to know whether it finished.'),
    ('flow', 'Display path once POST is OK', ['POST OK', 'Cable', 'Input HDMI/DP', 'Brightness', 'GPU seating']),
     'The first box is a gate. If POST fails, stop and use the Chapter 2.5 codes instead. Otherwise move right one box at a time.',
    'Sort each symptom into the right path, then say the display order out loud.',
    sort('Which path?', {'POST problem first': ['MEM beep code', 'Board LED stuck on DRAM'],
                         'Display path': ['Fans run, Windows chime, panel dark', 'Wrong input selected']}, 'Display checks wait for POST.'), CAB)

# ------------------------------------------------------------------ 3.5
_add('3.5', 'core-content', 'Core content', 'IT-3.3', S5, [
    ('Why change only one part at a time on an unstable PC?', 'To know what fixed it', 'To use up spare parts', 'To keep the user busy',
     'One change, one result: several changes hide the real cause and may add faults.', SHOT, SHOT),
    ('The OS disk warns during the reboot hunt. What comes first?', 'Protect the user’s data', 'Swap the PSU anyway', 'Reinstall Windows right now',
     'A failing disk can lose data every hour; back it up before other changes.', SHOT, VAGUE),
    ('In the recipe story, why change one ingredient per bake?', 'To see what changed it', 'To finish baking sooner', 'To use the whole cupboard',
     'One change per test shows which ingredient made the difference.', SHOT, SHOT),
    ('In the domain flow, which comes first?', 'Safety', 'Display', 'Storage',
     'Safety is always checked first: smell, heat, swelling or shock stop the job.', SHOT, SHOT),
    ('Which line belongs in a good capstone note?', 'Kernel-Power 41 at each reboot', 'PC acting weird, so I fixed it now', 'Tried lots of stuff',
     'A note gives each test with its result so a colleague can follow it.', VAGUE, VAGUE),
],
    (['An unstable PC tempts you to change everything.', 'Do not.', 'Check one area at a time.', 'Start with safety.', 'Then POST, inventory and storage.',
      'Then power, heat and display.', 'Change one thing.', 'Write what you saw.', 'A colleague should be able to follow your note.'],
     'One domain, one change, one written result, starting with safety.'),
    ('A baker’s cake keeps sinking. Changing the flour, the oven and the recipe in one go might fix it, but nobody learns why. Changing '
     'only the oven temperature, baking once, and writing the result tells the next baker exactly what worked.',
     [('Sinking cake', 'Intermittent reboots'), ('Flour, oven, recipe', 'RAM, PSU, Windows image'), ('One change per bake', 'One change per test'),
      ('Notebook by the oven', 'Capstone note: test, result, next')],
     'A cake failure is cheap; a failing disk can lose data. Unlike baking, protect the data before any test.'),
    ('flow', 'Unstable workstation: one domain at a time', ['Safety', 'POST', 'Inventory', 'Storage', 'Power and heat', 'Display']),
     'Each box is a domain with its own evidence. Finish one before moving right, and write its result on the note.',
    'Order the capstone domains, then work the triage lab with one change at a time.',
    order('Capstone domains', ['Safety', 'POST', 'Inventory', 'Storage and backup', 'Power and heat', 'Display'],
          'Safety and data come before any part swap.'), TRI)

_add('3.5', 'unstable-workstation-capstone', 'Unstable workstation capstone', 'IT-3.3', S5, [
    ('You reseat RAM, swap the PSU and reimage in one hour. What is lost?', 'Which change worked', 'The user’s password', 'The service tag',
     'Several changes together hide which one fixed the fault.', SHOT, SHOT),
    ('What should the capstone note read like?', 'Ticket B from 1.3', 'A short text message', 'A shopping list',
     'Ticket B lists each test with its result and the next step.', VAGUE, VAGUE),
    ('In the light-switch story, why flip one switch at a time?', 'To find the right one', 'To save on the electricity', 'To test the bulbs',
     'One switch at a time shows which one controls the light.', SHOT, SHOT),
    ('In the loop picture, what follows “change one thing”?', 'Write the result', 'Change another thing', 'Close the ticket',
     'Every change is followed by a written result before the next change.', VAGUE, SHOT),
    ('Which plan follows the capstone rule?', 'Reseat RAM, test, write', 'Swap three parts, then test', 'Reimage, then decide',
     'One change, one test, one written result.', SHOT, SHOT),
],
    (['Pick one area of the PC.', 'Change one thing.', 'Test it.', 'Write the result.', 'Then decide the next step.',
      'If you change three things at once, you lose the answer.', 'Your note should look like Ticket B from lesson 1.3.'],
     'Change one thing, write the result, then choose the next step.'),
    ('A room has five light switches and one light that flickers. Flip all five and you will never know which one matters. Flip one, '
     'watch, write it down. Then the next. By the end you have a list anyone can repeat.',
     [('Five light switches', 'RAM, PSU, disk, image, cables'), ('Flicking one switch', 'One change'), ('Watching the light', 'Testing the result'),
      ('Writing it down', 'The capstone note')],
     'Switches flip back for free; some PC changes, like a reimage, cannot be undone. Choose cheap, reversible changes first.'),
    ('flow', 'The capstone loop', ['Pick one domain', 'Change one thing', 'Test', 'Write the result', 'Next step']),
     'The loop repeats until the fault is found. Never skip the written result, because the next loop depends on it.',
    'Order the loop, then run the triage lab and write one loop as a ticket line.',
    order('One loop of the capstone', ['Pick one domain', 'Change one thing', 'Test it', 'Write the result', 'Choose the next step'],
          'The note is part of the loop, not an afterthought.'), TRI)
