"""Explanation ladder — ITSUP chapter 3 (Storage, RAID, Power, Display, Capstone). Pending SME review.

Distinct concept sections are laddered; depth, reference and teach-block sections that restate a core section of the
same lesson use same_as.
"""
from curriculum_v2.ladder.itsup._lk import M, P, X
from curriculum_v2.ladder.schema import order, reveal, same_as, sort

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 3


def _s(n, t):
    return f'Course lesson 3.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4, S5 = (_s(1, 'Storage'), _s(2, 'RAID and Backup'), _s(3, 'Power Supplies'), _s(4, 'Display and Cables'),
                      _s(5, 'Unstable Workstation Capstone'))
_P = 'MC-L-IT3-'
MISCONCEPTIONS = {
    **M(_P, S1, {
        'M2-NVME': ('IT-3.1', 'Treating every M.2 stick as NVMe', 'M.2 is the slot shape; the stick may speak SATA or NVMe.', ['m.2', 'nvme']),
        'LOST-FILE': ('IT-3.1', 'Replacing a disk when the user only lost a file', 'A missing file on a healthy volume is delete, folder or backup.', ['file', 'ssd']),
        'IMAGE-BLIND': ('IT-3.1', 'Imaging before firmware and Windows both see the disk', 'Detect in firmware, then About and list disk, then image.', ['list disk', 'image']),
        'SAS-SATA': ('IT-3.1', 'Thinking a SATA controller can run SAS drives', 'SAS controllers run SATA drives, not the other way round.', ['sas']),
    }),
    **M(_P, S2, {
        'RAID-BACKUP': ('IT-3.2', 'Believing RAID is a backup', 'RAID survives disk failure only; deletes and ransomware hit every disk.', ['raid', 'backup']),
        'RAID0': ('IT-3.2', 'Thinking RAID 0 survives a disk failure', 'RAID 0 stripes with no redundancy; one failure loses the volume.', ['raid 0', 'stripe']),
        'PULL-SECOND': ('IT-3.2', 'Pulling another disk from a degraded array to test', 'A degraded array is an incident; touch nothing else and write it up.', ['degraded', 'rebuild']),
        'INIT-ARRAY': ('IT-3.2', 'Initialising or recreating a missing array', 'Check controller, cables and members; recreating can destroy data.', ['array missing']),
    }),
    **M(_P, S3, {
        'OPEN-PSU': ('IT-3.3', 'Opening a power supply to repair it', 'The PSU is a sealed FRU; capacitors hold charge. Replace it whole.', ['psu', 'fru']),
        'PSU-FIRST': ('IT-3.3', 'Buying a PSU before checking wall, switch and cables', 'Wall, switch, 24-pin, 8-pin first; a cord is cheaper than a PSU.', ['24-pin', 'eps']),
        '80PLUS': ('IT-3.3', 'Reading the 80 PLUS badge as wattage', '80 PLUS is efficiency; the wattage rating is capacity.', ['80 plus', 'wattage']),
        'VOLT-SWITCH': ('IT-3.3', 'Ignoring the input-voltage selector on older PSUs', 'Set 115/230 V correctly or the PSU can be destroyed.', ['115', '230']),
    }),
    **M(_P, S4, {
        'USBC-VIDEO': ('IT-3.4', 'Assuming every USB-C port carries video', 'Only ports wired for DisplayPort Alt Mode or Thunderbolt carry video.', ['usb-c', 'alt mode']),
        'DISPLAY-EARLY': ('IT-3.4', 'Starting display isolation before POST finished', 'Confirm POST passed; a MEM code with a dark panel is memory.', ['post', 'display']),
        'BOARD-FIRST': ('IT-3.4', 'Replacing the board before swapping cable, input and adapter', 'Cheap swaps first: input, cable, adapter, display, port.', ['adapter', 'cable']),
        'CAT-SPEED': ('IT-3.4', 'Expecting Cat 6 to carry 10 Gb/s over 100 m', 'Cat 6a is needed for 10GBASE-T at the full 100 m.', ['cat 6', 'cat 6a']),
        'OLED-BACKLIGHT': ('IT-3.4', 'Thinking OLED panels use a backlight', 'OLED pixels emit their own light; LCDs need a backlight.', ['oled', 'lcd']),
    }),
    **M(_P, S5, {
        'SHOTGUN': ('IT-3.3', 'Changing several parts at once on an unstable PC', 'One domain, one change, one result written down.', ['change', 'capstone']),
        'NOTE-VAGUE': ('IT-3.3', 'Writing a note a peer cannot act on', 'Each test, its result and the next step, in order.', ['note']),
    }),
}
M2, LOST, IMG, SAS, RB, R0, PULL, INIT, OPEN, PSUF, EFF, VOLT, USBC, EARLY, BOARD, CAT, OLED, SHOT, VAGUE = (_P + k for k in (
    'M2-NVME', 'LOST-FILE', 'IMAGE-BLIND', 'SAS-SATA', 'RAID-BACKUP', 'RAID0', 'PULL-SECOND', 'INIT-ARRAY', 'OPEN-PSU', 'PSU-FIRST',
    '80PLUS', 'VOLT-SWITCH', 'USBC-VIDEO', 'DISPLAY-EARLY', 'BOARD-FIRST', 'CAT-SPEED', 'OLED-BACKLIGHT', 'SHOTGUN', 'NOTE-VAGUE'))
DISK = ('w11-disk', 'List the disks, note handle, size and which one holds Windows. Do not run any destructive verb.')
BACK = ('ops-backup', 'Find the last good backup and prove a restore before anyone touches the array.')
BUILD = ('hw-pc-build', 'Seat the 24-pin and the CPU 8-pin, then check each power connection before power-on.')
CAB = ('hw-cables', 'Name each cable and connector, then pick the one the job needs.')
TRI = ('win-full-triage', 'Work one domain at a time and write test, result and next step for each.')

LESSONS = {
    '3.1': {
        'start-here-files-live-on-storage': X('Start here — files live on storage', 'IT-3.1', S1, [
            ('Where do files stay when the PC is switched off?', 'On storage', 'In RAM, until the next morning', 'Inside the CPU cache memory',
             'Storage keeps data with no power; RAM and cache are wiped at shutdown.', LOST, None),
            ('A user cannot find yesterday’s report but the PC boots fine. First thought?', 'Deleted or moved', 'The SSD is dying and must be replaced', 'The RAM is faulty and needs reseating',
             'A healthy disk with a missing file points to delete, wrong folder or backup, not hardware.', LOST, LOST),
            ('In the library story, what is the shelf?', 'Storage', 'The reading desk where you work', 'The librarian who fetches things',
             'The shelf keeps books overnight, like storage keeps files; the desk is RAM.', LOST, None),
            ('In the trace, what do you check before ordering a disk?', 'Whether the disk is the problem', 'Which brand of disk is on sale this week', 'Whether the user likes faster computers',
             'The trace separates disk faults from lost-file stories before spending money.', LOST, None),
            ('Windows will not start and firmware shows no disk. Which story?', 'Disk story', 'Lost-file story only', 'Printer driver story',
             'No disk in firmware means the OS cannot load; that is a storage fault.', LOST, None),
        ],
            P('Every document, photo and even Windows itself is a file. Files sit on a drive when the computer is off. Memory forgets everything at shutdown. So if the Windows drive is missing or broken, the machine cannot start. A good processor does not help. But “I lost a document” usually means it was deleted or saved elsewhere. It rarely means the drive failed.'),
            P('Picture a library. The shelves hold every book overnight; that is storage. The reading desk is where you spread books out while '
              'you work, and it is cleared at closing time; that is RAM. If the shelves collapse, nobody can borrow anything. But if one reader '
              'cannot find a book, you first check whether it was returned to the wrong shelf or thrown away, not rebuild the shelving.'),
            ['Does the PC reach Windows?', 'If not: does firmware list the disk?', 'If Windows runs: is this a missing file on a healthy disk?',
             'Check recycle bin, other folders and backup.', 'Only a disk fault leads to a disk order.'],
            '<p>Sort each ticket into the right story.</p>',
            sort('Which story?', {'Disk story': ['No boot device found', 'Disk shows Unknown', 'Drive clicks'],
                                  'Lost-file story': ['Report missing from Desktop', 'Saved to wrong folder']}, 'Only one column needs hardware.'), DISK),
        'hdd-ssd-nvme-without-the-brochure': same_as('1-three-common-drives', 'HDD, SSD, NVMe without the brochure', 'The same three drive kinds in plain words.'),
        'core-content': same_as('1-three-common-drives', 'Core content', 'Form factor, interface and media: the same drive comparison in depth.'),
        '1-three-common-drives': X('1. Three common drives', 'IT-3.1', S1, [
            ('Which drive has moving parts?', 'HDD', 'A SATA SSD in a laptop tray', 'An NVMe stick in an M.2 slot',
             'Only the hard disk spins platters and moves a head; SSDs are chips.', M2, None),
            ('M.2 names…', 'The slot shape', 'The fastest protocol a drive can use', 'A brand of solid-state drive',
             'M.2 is a connector and card shape; NVMe or SATA is the protocol it speaks.', M2, M2),
            ('In the road story, what is NVMe?', 'The lane rules', 'The shape of the car park entrance', 'The colour painted on the car',
             'The slot is the entrance shape; NVMe is how traffic moves on the road behind it.', M2, None),
            ('In the trace, what proves the protocol?', 'Label and Device Manager', 'The marketing name on the retail box', 'How short the stick looks',
             'Read the label and what Windows reports, not the box art.', M2, None),
            ('A 2.5-inch SATA SSD uses which cables?', 'SATA data and power', 'No cables, it screws into M.2', 'A PCIe power lead from the PSU',
             'A SATA SSD uses the same data and power cables as a SATA hard disk.', M2, None),
        ],
            P('Three kinds of drive turn up on tickets. A hard disk spins a platter and is cheap per terabyte but slow at small random jobs. A SATA '
              'solid-state drive has no moving parts and feels quick, but it still talks over the older SATA link. An NVMe drive is a small stick '
              'that talks over PCIe and is the fastest of the three. M.2 is only the shape of the slot, so check what the stick speaks.'),
            P('Think of a car park entrance and the road behind it. M.2 is the shape of the gate: lots of vehicles fit through it. NVMe and SATA are '
              'the road rules once you are through, and NVMe is the motorway. A car that fits the gate is not automatically allowed on the motorway. '
              'A hard disk is a lorry with a crane on it: it carries a lot cheaply, but it is slow to turn and it has parts that wear out.'),
            ['Look at the drive: platter case, 2.5-inch box or stick?', 'If a stick, read the label for NVMe or SATA.', 'Check the key notch and length (2280 etc.).',
             'Confirm in Device Manager what Windows sees.', 'Write kind, interface and size on the ticket.'],
            '<p>Sort each fact to the drive it describes.</p>',
            sort('Drive facts', {'HDD': ['Spinning platter', 'Can click when failing'], 'SATA SSD': ['Same cables as an HDD', 'Capped near 600 MB/s'],
                                 'NVMe': ['Talks over PCIe', 'Several GB/s']}, 'Shape alone never tells you the protocol.'), DISK),
        '2-detect-before-you-image': X('2. Detect before you image', 'IT-3.1', S1, [
            ('Firmware does not list the new stick. What now?', 'Stop and reseat', 'Image it anyway from the USB stick', 'Run diskpart clean on Disk 0 to reset it',
             'If firmware cannot see it, imaging will hit the wrong disk or fail. Reseat, check notch and slot.', IMG, IMG),
            ('What order proves a disk is seen?', 'Firmware, About, list disk', 'list disk, then image, then firmware', 'Image first and check afterwards',
             'Each layer confirms the one before before anything destructive happens.', IMG, IMG),
            ('In the parcel story, why check the address first?', 'Wrong house otherwise', 'Parcels are heavier than they look', 'Couriers prefer short postcodes',
             'Imaging the wrong disk handle is like delivering to the wrong house: costly and hard to undo.', IMG, None),
            ('Some boards share lanes between an M.2 slot and SATA ports. What may help?', 'The other M.2 slot', 'Buying a bigger power supply unit', 'Turning Secure Boot fully off',
             'Shared lanes can disable one slot; the other slot may work.', IMG, None),
            ('Which step comes last?', 'Imaging', 'Checking the firmware disk list', 'Reading list disk handles',
             'Imaging comes only after every detection step agrees.', IMG, None),
        ],
            P('Before you put an image on a drive, prove three times that the computer can see it. Check the setup screen first. Then check Windows About or Disk Management. Then run list disk and read its numbered handles. If the setup screen does not show the new stick, stop. Push it back in, look at the notch and try the other slot. Writing to a drive you have not confirmed is how the wrong one gets erased.'),
            P('A courier checks the house number, the street and the postcode before leaving a parcel. If any one does not match, the van does not '
              'unload; the driver rings the office. Imaging is a delivery that cannot be taken back. Firmware, Windows and list disk are the three '
              'parts of the address. When they all agree on which drive is which, you deliver. When one is missing, you call it in.'),
            ['Firmware lists the drive.', 'About or Disk Management shows it.', 'list disk shows its handle and size.', 'Write the handle on the ticket.', 'Only now image.'],
            '<p>Put the detection steps in order.</p>',
            order('Before imaging', ['Firmware sees the disk', 'Windows sees the disk', 'list disk handle written down', 'Image the disk'],
                  'Nothing destructive happens until all three agree.'), DISK),
        'm-2-is-the-slot-nvme-is-the-protocol': same_as('1-three-common-drives', 'M.2 is the slot, NVMe is the protocol', 'Slot versus protocol again, with list disk.'),
        'when-the-disk-is-the-ticket': same_as('start-here-files-live-on-storage', 'When the disk is the ticket', 'Disk stories versus lost-file stories.'),
        'teach-block-words-that-order-parts': same_as('1-three-common-drives', 'Teach block — words that order parts', 'Ordering by slot, protocol and length.'),
        'reference-storage-interfaces-and-real-world-speeds': X('Reference — storage interfaces and real-world speeds', 'IT-3.1', S1, [
            ('Roughly what is the practical ceiling of SATA III?', '≈ 550–600 MB/s', 'About 7 GB/s on a fast board', 'About 14 GB/s with a heatsink',
             'SATA III signals at 6 Gb/s, which works out to roughly 550–600 MB/s of real data.', M2, M2),
            ('A PCIe 4.0 ×4 NVMe drive tops out near…', '7 GB/s', '600 MB/s, the same as SATA', '480 Mb/s, like USB 2.0',
             'Each PCIe generation doubles the per-lane rate; 4.0 ×4 gives about 7 GB/s.', M2, None),
            ('In the motorway story, what does PCIe 5.0 add?', 'More speed per lane', 'A different car park gate', 'Wider parking bays only',
             'Newer PCIe generations double the speed of each lane; the slot shape stays M.2.', M2, None),
            ('An M-key-only stick is usually…', 'NVMe', 'A SATA drive in M.2 form', 'An mSATA card',
             'B+M keyed sticks are usually SATA; M-key-only sticks are usually NVMe. The board manual decides.', M2, None),
            ('What keeps an SSD fast over time?', 'TRIM', 'A 7,200 rpm spindle', 'Defragmenting weekly',
             'SSDs rely on TRIM; spindle speed only applies to hard disks.', M2, None),
        ],
            P('The table puts numbers on the drive types. SATA III, used by hard disks and 2.5-inch SSDs, manages about 550 to 600 MB/s in practice. '
              'NVMe drives on four PCIe lanes are far quicker: around 3.5 GB/s on PCIe 3.0, 7 GB/s on 4.0 and 14 GB/s on 5.0, which often needs a '
              'heatsink. Hard disks spin at 5,400 or 7,200 rpm; SSDs are rated for total writes (TBW) and use TRIM to stay quick.'),
            P('Picture roads leaving the same car park gate. The gate is M.2. Behind it, SATA is a single-lane country road with a speed limit. '
              'NVMe uses four motorway lanes, and every new PCIe generation raises the speed limit on each lane, so a 5.0 motorway is twice as fast '
              'as 4.0. Cars that go that fast get hot, which is why the newest drives often wear a heatsink like a radiator grille.'),
            ['Read the stick: B+M key (usually SATA) or M key (usually NVMe)?', 'Check the board manual for what the slot supports.',
             'Find the PCIe generation of the slot.', 'Expect ≈600 MB/s (SATA), 3.5, 7 or 14 GB/s (NVMe 3.0/4.0/5.0).', 'Note heatsink needs for PCIe 5.0.'],
            '<p>Sort each interface to its rough real-world ceiling.</p>',
            sort('Real-world speed', {'Under 1 GB/s': ['SATA III SSD', 'M.2 SATA stick'], '3.5–7 GB/s': ['NVMe PCIe 3.0 ×4', 'NVMe PCIe 4.0 ×4'],
                                      'About 14 GB/s': ['NVMe PCIe 5.0 ×4']}, 'The slot shape never sets the speed; the protocol and PCIe generation do.'), DISK),
        'storage-devices-interfaces-form-factors-raid-and-removable-m': X('Storage devices: interfaces, form factors, RAID and removable media', 'IT-3.1', S1, [
            ('Can a SATA controller run a SAS drive?', 'No', 'Yes, they use the same connector', 'Only with an NVMe adapter fitted',
             'A SAS controller can run SATA drives, but a SATA controller cannot run SAS drives.', SAS, SAS),
            ('Which optical disc holds about 25 GB on one layer?', 'Blu-ray', 'A single-layer DVD disc', 'A standard audio CD',
             'CD is about 700 MB, DVD 4.7 GB, single-layer Blu-ray 25 GB.', SAS, None),
            ('In the shoe story, why does SAS fit SATA but not back?', 'One way only', 'All shoes are the same size anyway', 'Shoes stretch with time',
             'The bigger SAS socket accepts SATA drives; the reverse is blocked on purpose.', SAS, None),
            ('Which drive speed suits an older enterprise server?', '15,000 rpm', '5,400 rpm laptop drive speed', '7,200 rpm desktop drive speed',
             '10k and 15k rpm drives were common in older enterprise servers.', SAS, None),
            ('mSATA was replaced by…', 'M.2', 'The SAS connector on servers', 'USB flash drives',
             'mSATA is an older small form factor; M.2 took its place.', M2, None),
        ],
            P('The exam wants you to compare drives. Hard disks spin at 5,400 or 7,200 rpm in ordinary PCs and 10,000 or 15,000 in older servers. '
              'Server drives often use SAS; a SAS controller will also run SATA drives, but a plain SATA controller cannot run SAS. Small SSDs come '
              'as 2.5-inch, M.2, the older mSATA or add-in cards. Removable media includes USB sticks, SD cards and optical discs.'),
            P('Think of shoes and feet. A SAS controller is a roomy boot that a SATA foot slips into easily. A SATA controller is a narrow slipper, '
              'and the larger SAS foot simply will not go in, which is deliberate. Discs are like different sized notebooks: a CD is a thin pad of '
              'about 700 MB, a DVD a thicker one of 4.7 GB, and a Blu-ray a fat binder of 25 GB on a single layer.'),
            ['Server or desktop?', 'Pick interface: SAS, SATA or NVMe.', 'Check controller supports it.', 'Pick form factor for the bay or slot.', 'Removable? Pick USB, SD or disc by size.'],
            '<p>Guess first, then reveal.</p>',
            reveal('A server has a SAS controller and you only have SATA drives. Will they work?', 'Yes. SAS controllers accept SATA drives; only the reverse fails.'), DISK),
    },
    '3.2': {
        'backup-versus-raid-from-zero': X('Backup versus RAID from zero', 'IT-3.2', S2, [
            ('A user deleted a folder on a RAID 1 server. What brings it back?', 'A backup', 'The mirror disk in the same array', 'Rebuilding the RAID from parity',
             'The delete was copied to both mirrors at once; only a separate copy restores it.', RB, RB),
            ('What is a backup?', 'A restorable second copy', 'Two disks glued together for speed', 'Any folder synced to the same disk',
             'A backup is a separate copy you can restore, ideally kept off the same box.', RB, RB),
            ('In the photocopy story, why is a mirror not a backup?', 'Mistakes copy too', 'Mirrors are slower than copies', 'Paper fades over time',
             'A mirror writes every change, including mistakes, to both sides at once.', RB, None),
            ('Ransomware encrypts a RAID 5 volume. What helps?', 'Offline backup', 'Replacing the parity disk', 'Adding a hot spare drive',
             'Encryption hits every member; only a copy the malware cannot reach helps.', RB, None),
            ('Which rule does CISA give small shops?', '3-2-1', 'RAID 5 everywhere', 'Sync to OneDrive only',
             'Three copies, two media types, one off site, plus offline copies for ransomware.', RB, None),
        ],
            P('Two ideas get confused all the time. RAID joins several disks so the system keeps running, or runs faster, when one disk dies. A '
              'backup is a separate copy you have actually restored from, kept away from the original. If someone deletes a folder or ransomware '
              'scrambles it, RAID copies that damage to every disk instantly. Only the separate copy can bring the work back.'),
            P('Imagine writing a diary with carbon paper under each page, so two copies appear at once. If one copy gets coffee on it, you still '
              'have the other: that is a mirror. But if you tear a page out or scribble over it, the carbon copy is torn or scribbled too. A '
              'photocopy kept in a drawer at a friend’s house is different: whatever happens to your diary, last week’s copy is still safe.'),
            ['What happened: disk failure, delete, or encryption?', 'Disk failure: RAID may keep you running.', 'Delete or encryption: RAID copied it.',
             'Find the separate backup.', 'Restore and record the backup age.'],
            '<p>Sort each event by what saves you.</p>',
            sort('What saves you?', {'RAID (redundancy)': ['One disk in a mirror dies', 'One disk in RAID 5 fails'],
                                     'Backup only': ['User deletes a folder', 'Ransomware encrypts the share', 'Office fire']}, 'RAID only covers a dead disk.'), BACK),
        'core-content': same_as('1-levels-you-must-not-mix-up', 'Core content', 'RAID levels with capacity numbers and the 3-2-1 backup rule.'),
        '1-levels-you-must-not-mix-up': X('1. Levels you must not mix up', 'IT-3.2', S2, [
            ('One disk dies in RAID 0. Result?', 'Volume lost', 'Still up; replace and rebuild', 'Still up but slower for a while',
             'RAID 0 has no redundancy; one failure loses the whole stripe.', R0, R0),
            ('Four 4 TB disks in RAID 5 give…', '12 TB', '16 TB of usable space', '8 TB of usable space',
             'RAID 5 gives (n − 1) × s: three disks’ worth, so 12 TB.', R0, None),
            ('In the relay story, what is parity?', 'A recipe to rebuild', 'A spare runner on the bench', 'A faster pair of shoes',
             'Parity lets the missing piece be recalculated from the others.', R0, None),
            ('Minimum disks for RAID 6?', 'Four', 'Two disks are enough', 'Three disks are enough',
             'RAID 6 keeps two disks’ worth of parity and needs at least four drives.', R0, None),
            ('Which level mirrors pairs then stripes them?', 'RAID 10', 'RAID 5 with a single parity', 'RAID 0 with no redundancy',
             'RAID 10 is a stripe of mirrors and needs at least four disks.', R0, None),
        ],
            P('Learn the common RAID levels by what happens when one drive fails. Level 0 spreads data across drives for speed, so losing any drive '
              'loses everything. Level 1 keeps an identical copy, so the system stays up. Level 5 spreads data plus a parity block and survives one '
              'failure but is slow and fragile while it rebuilds. Level 6 survives two. Level 10 pairs mirrors and stripes them.'),
            P('Think of a relay team carrying a long message cut into pieces. In level 0 each runner holds one piece and nothing else; if one trips, '
              'the message is gone. In level 1 two runners carry identical copies. In level 5 each runner also carries a small recipe that lets the '
              'team rebuild any single missing piece, but rebuilding takes everyone’s effort, and if a second runner falls meanwhile, the race is lost.'),
            ['Count disks.', 'Name the level.', 'Work out usable space.', 'Say how many failures it survives.', 'Write it on the ticket.'],
            '<p>Sort each level by what one failed disk does.</p>',
            sort('One disk dies', {'Volume lost': ['RAID 0'], 'Still running': ['RAID 1', 'RAID 5', 'RAID 6', 'RAID 10']},
                 'Only the stripe with no redundancy dies outright.'), BACK),
        '2-ticket-habit': X('2. Ticket habit', 'IT-3.2', S2, [
            ('An array is degraded and users are working. What is it?', 'An incident', 'A quiet lunchtime disk swap', 'Nothing until it fails fully',
             'A degraded array has a clock running; treat it as an incident.', PULL, PULL),
            ('Which belongs on the ticket?', 'Array, slot, last backup', 'The colour of the drive caddies', 'Only the date of purchase',
             'Which array, which slot, whether mounted, and last backup time.', PULL, None),
            ('In the bridge story, why not test another plank?', 'It may collapse', 'Planks are expensive to buy', 'Testing takes too long',
             'Pulling a second disk from a degraded array can destroy it.', PULL, None),
            ('May you pull a second disk “to test”?', 'No', 'Yes, if users are offline', 'Yes, if it is the parity disk',
             'A second missing member can lose the volume.', PULL, None),
            ('A disk dies in RAID 5. While it rebuilds, performance…', 'Drops', 'Rises as data spreads', 'Stays exactly the same',
             'The array serves users and rebuilds at once, so it slows and is at risk.', PULL, None),
        ],
            P('When a RAID array loses a drive but stays online, people keep working, so it can look harmless. It is not: one more failure and the '
              'data is gone. Write down which array, which bay, whether the volume is still mounted, and when the last good backup ran. Never pull '
              'another drive just to see what happens, and remember the array is slow and fragile until it finishes rebuilding.'),
            P('A rope bridge has lost one plank. People can still cross carefully, so traffic continues, but now every remaining plank carries more '
              'weight. That is the moment to fence it off, note which plank is gone and send for a replacement, not to yank a neighbouring plank to '
              'see if it is loose too. Replacing the plank takes time, and during that time the bridge is weaker than usual.'),
            ['Note array name and failed slot.', 'Is the volume still mounted?', 'When was the last backup?', 'Open an incident.', 'Replace only the failed disk.'],
            '<p>Put the degraded-array response in order.</p>',
            order('Degraded array', ['Record array and slot', 'Confirm backup age', 'Open the incident', 'Replace failed disk', 'Watch the rebuild'],
                  'Nothing else is pulled while it rebuilds.'), BACK),
        'raid-is-not-backup': same_as('backup-versus-raid-from-zero', 'RAID is not backup', 'RAID survives a dead disk, not a delete.'),
        'rebuild-tax': same_as('2-ticket-habit', 'Rebuild tax', 'Why a degraded RAID 5 is slow and at risk.'),
        'teach-block-raid-stories': same_as('backup-versus-raid-from-zero', 'Teach block — RAID stories', 'Three tickets that separate RAID from backup.'),
        'storage-and-raid-symptoms': X('Storage and RAID symptoms', 'IT-3.2', S2, [
            ('A hard disk starts clicking. First step?', 'Back up now', 'Run a long defrag to fix it', 'Keep using it to see if it stops',
             'Clicking is mechanical failure in progress; every hour risks the data.', INIT, None),
            ('The RAID controller reports the array missing. Avoid…', 'Recreating the array', 'Checking cables to each member', 'Checking the controller in firmware',
             'Initialising or recreating an array can destroy the data on it.', INIT, INIT),
            ('In the smoke-alarm story, what is S.M.A.R.T.?', 'An early warning', 'The fire itself starting', 'A sprinkler that fixes it',
             'S.M.A.R.T. warns before failure; back up and replace.', INIT, None),
            ('In the triage chain, what comes second?', 'Protect the data', 'Replace the controller card', 'Initialise the array',
             'Back up before touching cables, modes or arrays.', INIT, None),
            ('An amber light on a drive bay usually means…', 'Failed member', 'Drive is idle and sleeping', 'Drive is brand new',
             'Amber or flashing usually marks the failed disk; check the vendor legend.', INIT, None),
        ],
            P('Common storage warnings each have a safe first move. Grinding or clicking means the mechanics are failing, so copy the data off before '
              'anything else. Slow reads can be a full disk, a weak cable or a rebuild. A health warning from the drive means back up and replace. '
              'If the array disappears, look at the controller, cables and members, and never initialise or rebuild it from scratch.'),
            P('A smoke alarm is not the fire; it is a warning while there is still time to leave with your valuables. A S.M.A.R.T. alert or a new '
              'clicking noise is that alarm. You do not stand in the kitchen working out which pan caused it: you get the important things out '
              'first, then investigate. Recreating a missing array is like knocking walls down to find the alarm: you destroy what you meant to save.'),
            ['Symptom noticed.', 'Back up the data.', 'Check cables and firmware detection.', 'Check controller mode and array status without initialising.', 'Replace the failed part.'],
            '<p>Put the storage triage in order.</p>',
            order('Storage triage', ['Notice the symptom', 'Back up the data', 'Check cables and detection', 'Check controller and array status', 'Replace the failed part'],
                  'Data first, parts last.'), BACK),
    },
    '3.3': {
        'core-content': same_as('choosing-and-installing-a-power-supply', 'Core content', 'Connectors, sizing and mains protection in depth.'),
        '1-sealed-unit': X('1. Sealed unit', 'IT-3.3', S3, [
            ('Why do we never open a PSU?', 'Stored charge', 'The screws are too small', 'It voids the case warranty',
             'Capacitors can hold dangerous charge after unplugging; the PSU is replaced whole.', OPEN, OPEN),
            ('What is the PSU, in shop words?', 'A sealed FRU', 'A repairable sub-board', 'Part of the motherboard',
             'Field-replaceable unit: test from outside, swap the whole thing.', OPEN, None),
            ('In the fuse-box story, what do you call?', 'Replace the unit', 'Open it with a screwdriver', 'Tap it to reset',
             'You swap sealed boxes; you do not repair inside them.', OPEN, None),
            ('The replacement must be…', 'Equal rating, same connectors', 'Any PSU on the shelf that fits', 'The cheapest one available',
             'Equal or greater rating and the same connectors.', OPEN, PSUF),
            ('First step before removing the PSU?', 'Unplug and wait', 'Remove the board screws', 'Pull the 24-pin while running',
             'Unplug from the wall and wait before touching cables.', OPEN, None),
        ],
            P('The power supply turns wall current into the low voltages the parts use. Its capacitors can stay charged after you unplug it. So '
              'in this course it is a sealed part: you never open it. Unplug at the wall, wait, then unplug the cables from the board. Fit a tested unit with at least the same wattage and plugs. Recycle the old one the way the shop says.'),
            P('Think of the sealed meter box on the side of a house. If it fails you do not prise the lid off with a screwdriver: the power company '
              'swaps the whole box for one that works. A desktop power supply is the same kind of box. It goes in whole and comes out whole, and '
              'nothing about the job needs a peek inside, because what is inside can hurt you even after the plug is out.'),
            ['Unplug at the wall.', 'Wait.', 'Disconnect board and drive cables.', 'Fit a known-good PSU of equal or greater rating.', 'Recycle the old unit.'],
            '<p>Put the swap in order.</p>',
            order('PSU swap', ['Unplug at the wall', 'Wait', 'Disconnect cables', 'Fit known-good PSU', 'Recycle old unit'],
                  'The lid never comes off.'), BUILD),
        '2-symptoms-that-look-like-a-dead-board': X('2. Symptoms that look like a dead board', 'IT-3.3', S3, [
            ('No fan, no LED. Check first?', 'The wall socket', 'Order a new motherboard', 'Reinstall the operating system',
             'Start at the wall, then the PSU switch, 24-pin and CPU 8-pin.', PSUF, PSUF),
            ('PC switches off only in games. Likely?', 'Undersized PSU', 'A loose monitor cable', 'A full recycle bin',
             'Instant off under load points to a weak or overloaded PSU.', PSUF, None),
            ('In the torch story, what do you test first?', 'The batteries', 'The bulb’s brand', 'The torch colour',
             'Cheapest likely cause first: power at the source.', PSUF, None),
            ('Burn smell while swapping. What is it?', 'An incident: stop', 'Normal for new parts', 'Dust; keep going',
             'Smell or a hot outlet is the Chapter 1.2 stop rule.', OPEN, None),
            ('Which is cheaper to test than a new PSU?', 'A known-good cord', 'A new graphics card', 'A fresh Windows install',
             'Swap the cord before buying a supply.', PSUF, None),
        ],
            P('A computer that shows no light and no fan movement looks like a broken board, but power is usually the cause. Check the socket, the '
              'switch on the back of the supply, the large 24-pin plug and the CPU 8-pin plug, in that order. A machine that turns off only when '
              'working hard points to a supply that is too small or failing. A burning smell or hot socket is not a repair: stop and report.'),
            P('A torch that will not light makes people blame the bulb. A sensible person checks the batteries are in, the right way round, and the '
              'switch actually clicks before buying a new torch. Then, if it dies only when on full beam, the batteries are tired, not the bulb. And '
              'if the torch is hot and smells, you put it down and walk away rather than shaking it.'),
            ['Wall socket.', 'PSU switch.', '24-pin seated.', 'CPU 8-pin seated.', 'Then suspect the PSU.'],
            '<p>Sort each symptom to its likely cause.</p>',
            sort('Symptom to cause', {'Power path': ['No fan, no LED', 'Dead after a move'], 'PSU capacity': ['Off under load', 'Off in games only'],
                                      'Stop now': ['Burn smell', 'Hot outlet']}, 'Some symptoms are not repairs at all.'), BUILD),
        'power-isolation': same_as('2-symptoms-that-look-like-a-dead-board', 'Power isolation', 'Wall, switch, 24-pin, 8-pin, then PSU.'),
        'choosing-and-installing-a-power-supply': X('Choosing and installing a power supply', 'IT-3.3', S3, [
            ('What does an 80 PLUS badge tell you?', 'Efficiency', 'Maximum wattage the unit gives', 'How many cables it has',
             '80 PLUS certifies efficiency at set loads, not capacity.', EFF, EFF),
            ('An old PSU set to 115 V is plugged into 230 V. Risk?', 'Destroyed PSU', 'It runs slightly slower', 'Nothing; it adapts automatically',
             'Only auto-ranging units adapt; a wrong selector can destroy the supply.', VOLT, VOLT),
            ('In the menu story, why add headroom?', 'Avoid running hot', 'Cheaper to buy big', 'Bigger looks better',
             'A PSU near its limit runs hot and less efficiently.', EFF, None),
            ('Which rail feeds most of a modern CPU and GPU?', '+12 V', '+5 V', '+3.3 V',
             'Modern CPUs and graphics cards draw mostly from 12 V.', EFF, None),
            ('A server has two hot-swappable PSUs. They are…', 'Redundant', 'Modular cables', 'Auto-ranging only',
             'Redundant supplies can each run the server alone and be swapped live.', EFF, None),
        ],
            P('To pick a power supply, first check it accepts your mains voltage. Most are auto-ranging; old ones have a switch. Next check the plugs: 24-pin, CPU EPS, PCIe for graphics and SATA power. Then check the wattage covers the parts with room to spare. The 80 PLUS badge '
              'only rates efficiency. Modular units let you fit just the cables you use, and servers may run two redundant supplies.'),
            P('Choosing a supply is like booking a caterer. You check they work in your country, bring the right dishes for every guest, and can '
              'feed more people than you invited in case extras turn up. A gold star for a tidy kitchen tells you how little food they waste, not '
              'how many they can serve. A big event hires two caterers, each able to feed everyone if the other drops out.'),
            ['Check input voltage or selector.', 'List connectors needed.', 'Add CPU and GPU watts plus allowance.', 'Choose a rating with headroom.', 'Fit and seat every plug.'],
            '<p>Sort each term to what it means.</p>',
            sort('PSU terms', {'Capacity': ['Wattage rating', 'Headroom'], 'Efficiency': ['80 PLUS Bronze', '80 PLUS Titanium'],
                               'Build': ['Modular cables', 'Redundant pair']}, 'Efficiency and capacity are different questions.'), BUILD),
    },
    '3.4': {
        'core-content': same_as('2-connectors', 'Core content', 'USB-C capabilities and the display isolation order in depth.'),
        '1-isolation-order': X('1. Isolation order', 'IT-3.4', S4, [
            ('The board shows MEM and the screen is dark. Start display checks?', 'No, memory first', 'Yes, swap the monitor now', 'Yes, reinstall the GPU driver',
             'POST has not finished; a dark panel during MEM is still a memory problem.', EARLY, EARLY),
            ('After POST passes, what is checked first?', 'Cable and input', 'The graphics card seating', 'The motherboard itself',
             'Cheap checks first: right input, known-good cable.', BOARD, BOARD),
            ('In the TV story, what do you press first?', 'The input button', 'Call an engineer to visit', 'Buy a new aerial',
             'Wrong input is the commonest blank screen.', BOARD, None),
            ('Which comes after a known-good display?', 'Onboard vs discrete', 'Replace the motherboard', 'Check the cable',
             'Then try another output or the onboard graphics.', BOARD, None),
            ('What is last in the order?', 'Board or GPU', 'Known-good cable', 'Correct input',
             'Expensive parts come only after the cheap swaps.', BOARD, None),
        ],
            P('Only start on the screen once the computer has finished its start-up check. If the board still shows a memory code, the dark screen '
              'is a memory problem. After a clean start, check the monitor is on the right input with a cable you trust, then try another monitor, '
              'then switch between the onboard and the add-in graphics. Only after all that do you suspect the graphics card or the board.'),
            P('When the television shows nothing, nobody sensible calls an engineer straight away. You check it is on, press the input button to '
              'pick the right source, and wiggle the lead. Then you try the box on a different TV. Only if every TV stays blank do you suspect the '
              'box itself. And if the box is still flashing its own error light, the TV was never the problem.'),
            ['POST finished?', 'Right input, known-good cable.', 'Known-good display.', 'Onboard versus discrete graphics.', 'Then board or GPU.'],
            '<p>Put the display checks in order.</p>',
            order('Display isolation', ['POST finished', 'Input and cable', 'Known-good display', 'Other output', 'Board or GPU'],
                  'Cheap and likely before expensive and rare.'), CAB),
        '2-connectors': X('2. Connectors', 'IT-3.4', S4, [
            ('A monitor stays dark on a laptop USB-C port. Possible cause?', 'Port lacks video', 'USB-C never carries video', 'The laptop needs a new board',
             'Only ports wired for DisplayPort Alt Mode or Thunderbolt carry video.', USBC, USBC),
            ('Which carry video and audio?', 'HDMI and DisplayPort', 'SATA and Molex', 'RJ45 and RJ11 jacks',
             'HDMI and DisplayPort carry both picture and sound.', USBC, None),
            ('In the tap story, why does the cable matter?', 'It limits the flow', 'Cables are only decoration', 'Every cable is identical',
             'A charge-only or USB 2.0 cable blocks video even on a good port.', USBC, None),
            ('What do you swap before a laptop board?', 'The adapter', 'The keyboard', 'The battery',
             'Adapters fail often and are cheap to swap.', BOARD, None),
            ('How do you know a USB-C port carries video?', 'Icon or spec sheet', 'All oval ports do', 'The colour of the plug',
             'Look for the DisplayPort or Thunderbolt symbol, or check the specifications.', USBC, None),
        ],
            P('HDMI and DisplayPort always carry picture and sound. The oval USB-C plug is only a shape: a given port might do data, charging, video '
              'or all three, depending on how the maker wired it and which cable you use. Look for a DisplayPort or lightning-bolt icon, or check the '
              'specifications. Adapters and cheap cables fail often, so swap them before you blame the laptop.'),
            P('All the taps in a house can look the same, but one is cold water only, one is hot and cold, and one is just a garden hose outlet. '
              'Fitting the same nozzle does not make the garden tap give hot water. A USB-C port is the same. And a cracked hose in between can '
              'stop the flow even when the tap is fine, which is why the cable and adapter get checked first.'),
            ['Which port? Look for the icon.', 'Is the cable rated for video?', 'Swap the adapter.', 'Try HDMI or DisplayPort directly.', 'Then suspect the laptop.'],
            '<p>Guess first, then reveal.</p>',
            reveal('A dock works on one laptop but not another with the same oval port. Why?', 'The second laptop’s USB-C port is not wired for video (no Alt Mode or Thunderbolt).'), CAB),
        'display-path-after-post-ok': same_as('1-isolation-order', 'Display path after POST OK', 'The same display order after POST.'),
        'reference-usb-thunderbolt-and-display-links-current-names': X('Reference — USB, Thunderbolt and display links (current names)', 'IT-3.4', S4, [
            ('“USB 3.2 Gen 2” is sold to customers as…', 'USB 10Gbps', 'USB 40Gbps on a USB4 port', 'Hi-Speed USB at 480 Mb/s',
             'USB-IF’s customer name states the speed: USB 3.2 Gen 2 is USB 10Gbps.', USBC, USBC),
            ('Thunderbolt 5 is built on…', 'USB4 Version 2.0', 'USB 2.0 Hi-Speed signalling', 'HDMI 2.1 signalling',
             'Thunderbolt 5 uses USB4 Version 2.0: 80 Gb/s, up to 120 Gb/s for displays.', USBC, None),
            ('In the chain story, what sets the maximum resolution?', 'The slowest link', 'The newest device', 'The longest cable',
             'Port, adapter, cable and monitor input: the weakest one sets the limit.', BOARD, None),
            ('Up to how much power can USB PD 3.1 EPR deliver?', '240 W', '60 W with any cable', '15 W only',
             'Extended Power Range reaches 240 W with a 240 W-rated cable.', USBC, None),
            ('DisplayPort 2.1 (UHBR20) carries up to…', '80 Gb/s', '48 Gb/s, the HDMI 2.1 limit', '10 Gb/s',
             'DP 2.1 UHBR20 is 80 Gb/s; HDMI 2.1 tops out at 48 Gb/s.', USBC, None),
        ],
            P('USB names now state speed: USB 5Gbps, 10Gbps, 20Gbps, 40Gbps (USB4) and 80Gbps (USB4 Version 2.0). Thunderbolt 4 runs at 40 Gb/s and '
              'Thunderbolt 5 at 80 Gb/s, with up to 120 Gb/s for screens. USB-C is only the plug: one port may offer all of that, plus DisplayPort '
              'video and up to 240 W of charging, or only some of it. HDMI 2.1 carries up to 48 Gb/s and DisplayPort 2.1 up to 80 Gb/s.'),
            P('Think of a chain of hoses from a tap to a sprinkler. A wide tap does not help if one section of hose in the middle is thin: the '
              'thinnest piece decides how much water arrives. A laptop port, an adapter, a cable and a monitor input are those hose sections. The '
              'resolution and refresh you get are set by whichever piece is slowest, which is why a cheap adapter can cap an expensive monitor.'),
            ['Read the port icon and the laptop spec sheet.', 'Check the cable rating (speed and watts).', 'Check any adapter or dock.',
             'Check the monitor input version.', 'The slowest link sets the result.'],
            '<p>Sort each name to its speed.</p>',
            sort('Name to speed', {'5–10 Gb/s': ['USB 5Gbps', 'USB 10Gbps'], '40 Gb/s': ['USB4 (40Gbps)', 'Thunderbolt 4'],
                                   '80 Gb/s': ['USB4 Version 2.0', 'Thunderbolt 5']}, 'USB-C is the plug; the name tells the speed.'), CAB),
        'display-technologies-and-display-video-and-projector-trouble': X('Display technologies and display, video and projector troubleshooting', 'IT-3.4', S4, [
            ('Which panel needs no backlight?', 'OLED', 'IPS LCD panel', 'Mini-LED LCD panel',
             'OLED pixels emit their own light; every LCD, including Mini-LED, needs a backlight.', OLED, OLED),
            ('Which panel type gives wide angles and accurate colour?', 'IPS', 'TN, the fast type', 'VA, the contrast type',
             'IPS trades some speed for angles and colour.', OLED, None),
            ('In the window story, what is the backlight?', 'The sun behind', 'The curtain itself', 'The window frame',
             'An LCD filters light from behind; OLED is like each pane glowing on its own.', OLED, None),
            ('Touch fails but the picture is fine. Which part?', 'Digitizer', 'Backlight inverter', 'Graphics card',
             'The digitizer layer can fail independently of the image.', OLED, None),
            ('An LCD looks blurry. Check…', 'Native resolution', 'Refresh rate only', 'Colour gamut',
             'LCDs are sharpest at their native resolution.', OLED, None),
        ],
            P('Flat screens come in two families. LCDs need light from behind; TN panels are fast but weak at angles, IPS gives good colour and '
              'angles, VA gives deep contrast, and Mini-LED is an LCD with many small dimming zones. OLED pixels make their own light, so blacks are '
              'true black, but static images can leave marks. Touch is a separate layer that can fail alone. LCDs look sharpest at native resolution.'),
            P('Think of stained glass. An LCD is a window that only shows its picture when the sun shines through from behind; block the sun and the '
              'picture vanishes even though the glass is fine. An OLED is a window where every pane is its own little lamp. The touch layer is like '
              'a sheet of cling film on the glass: it can tear without the picture underneath changing at all.'),
            ['Is the source sending to the right output?', 'Cable and connectors sound?', 'Panel lit (backlight) or dark?', 'Touch working separately?', 'Resolution native?'],
            '<p>Sort each display fact.</p>',
            sort('Display types', {'LCD': ['Needs a backlight', 'TN, IPS or VA', 'Mini-LED zones'], 'OLED': ['Pixels emit light', 'True black', 'Burn-in risk']},
                 'Mini-LED is still an LCD.'), CAB),
        'cable-types-and-connectors': X('Cable types and connectors', 'IT-3.4', S4, [
            ('10 Gb/s over a full 100 m run needs…', 'Cat 6a', 'Cat 6, which also does it', 'Cat 5e, which is plenty',
             'Cat 6 only reaches 10 Gb/s on short runs; Cat 6a does the full 100 m.', CAT, CAT),
            ('T568A on one end, T568B on the other makes…', 'A crossover', 'A straight-through patch', 'A rollover console cable',
             'Same standard both ends is straight-through; mixed is crossover.', CAT, None),
            ('In the smoke story, why plenum cable?', 'Less toxic smoke', 'It is cheaper to buy', 'It carries more speed',
             'Plenum jackets burn with less smoke in air-handling spaces.', CAT, None),
            ('A cable modem uses…', 'RG-6 with F-type', 'Cat 8 with RJ45', 'Multimode fibre',
             'Coax RG-6 with a screw-on F connector.', CAT, None),
            ('Shielded twisted pair must be…', 'Grounded', 'Painted', 'Plenum only',
             'STP shielding only helps when grounded.', CAT, None),
        ],
            P('Network copper is graded by category. Cat 5e handles 1 Gb/s, Cat 6 reaches 10 Gb/s only on short runs, Cat 6a does 10 Gb/s at the full '
              '100 m, and Cat 8 serves short data-centre links. Shielded cable suits electrically noisy places and must be grounded. Matching wiring '
              'standards on both ends makes a straight cable; mixing them makes a crossover. Ceilings that carry air need plenum-rated jackets.'),
            P('Think of water pipes. A thin old pipe brings enough water for one tap; a wider pipe feeds a shower but only over a short distance; '
              'the widest pipe keeps full pressure the whole way down the street. Pipes that run through the air vents of a building must be made of '
              'material that will not fill the rooms with poisonous smoke if there is a fire.'),
            ['Speed needed?', 'Distance?', 'Pick the category.', 'Noisy area? Shielded and grounded.', 'Air-handling space? Plenum jacket.'],
            '<p>Sort each cable to its job.</p>',
            sort('Cable to job', {'Office LAN': ['Cat 6a run', 'UTP patch'], 'Noisy floor': ['Grounded STP'], 'Cable modem': ['RG-6 coax'],
                                  'Above ceiling': ['Plenum jacket']}, 'Speed, distance and location all matter.'), CAB),
    },
    '3.5': {
        'core-content': same_as('worked-order', 'Core content', 'One domain at a time, with the full worked note.'),
        'worked-order': X('Worked order', 'IT-3.3', S5, [
            ('An unstable PC: what comes first?', 'Safety', 'Reimage Windows', 'Order a new PSU',
             'Smell, heat, swelling or shock reports stop everything.', SHOT, SHOT),
            ('POST shows MEM. Next?', 'Memory first', 'Image the disk', 'Swap the monitor',
             'Do not image or chase display while POST points at memory.', SHOT, None),
            ('In the detective story, why one suspect at a time?', 'Know who did it', 'Saves paperwork', 'Suspects get bored',
             'Changing one thing at a time tells you which change fixed it.', SHOT, None),
            ('POST OK, panel dark. Which order?', 'The 3.4 display order', 'Reseat every RAM stick', 'Replace the PSU',
             'A good POST with no picture goes to the display isolation order.', SHOT, None),
            ('What goes in the note after each test?', 'Result and next step', 'Only the final fix', 'The time of lunch',
             'Test, result, next step, every time.', VAGUE, None),
        ],
            P('An unreliable computer tempts you to swap memory, the power supply and Windows all at once. If it then works, nobody knows which change '
              'fixed it. Work in order instead: safety first, then the start-up check, then what Windows can see, then storage, power and heat, then '
              'the screen. Change one thing, record the result, and decide the next step before touching anything else.'),
            P('A detective with three suspects does not arrest all of them and call the case closed. She questions one, checks the alibi, writes it '
              'down, and only then moves to the next. If she locked everyone up at once, the real culprit would never be known and two innocent '
              'people would pay. Swapping three parts in an hour is the same mistake with money and data instead of people.'),
            ['Safety: smell, heat, shock?', 'POST clean?', 'Windows sees all parts?', 'Disk, power, heat under load?', 'Display only if PC keeps running.'],
            '<p>Put the capstone domains in order.</p>',
            order('Capstone order', ['Safety', 'POST', 'Inventory', 'Storage', 'Power and heat'], 'One domain at a time.'), TRI),
        'pass-bar': X('Pass bar', 'IT-3.3', S5, [
            ('What makes a capstone note pass?', 'A peer can act on it', 'It is very long', 'It lists every part number',
             'A colleague must know whether to reseat, swap or stop.', VAGUE, VAGUE),
            ('Which action fails the capstone?', 'Cleaning a disk', 'Reseating RAM', 'Swapping a cable',
             'Destructive disk commands and opening a PSU are out of bounds.', VAGUE, None),
            ('In the recipe story, what makes it usable?', 'Steps someone can follow', 'A photo of the dish', 'A list of ingredients',
             'A note, like a recipe, must let someone else repeat it.', VAGUE, None),
            ('Reseat RAM, swap PSU, reimage in one hour. Problem?', 'Unknown fix', 'Too slow', 'Nothing wrong',
             'Three changes at once hide which one worked.', SHOT, None),
            ('The note should read like…', 'Ticket B from 1.3', 'A sales brochure', 'A chat message',
             'The capstone note follows the Ticket B shape.', VAGUE, None),
        ],
            P('The capstone asks one question. Could another technician read your note and know exactly what to do next? That might be reseat memory, swap a cable, or stop and call facilities. You must not have wiped a disk or opened a power supply. Did you change several things in one go? Then the note cannot say what worked. It fails even if the computer now behaves.'),
            P('A recipe passes if a stranger can cook the dish from it. “Add stuff and bake until done” fails, however good your own cake was. A '
              'recipe that says how much flour, what temperature and how long, and what to check before taking it out, passes. Your note is the '
              'recipe for this ticket: each step, what happened, and what to try next.'),
            ['One domain chosen.', 'One change made.', 'Result written.', 'Next step written.', 'No destructive actions.'],
            '<p>Sort each note line.</p>',
            sort('Pass or fail?', {'Passes': ['Reseated DIMM A2, 3 cold boots OK', 'Next: load test 10 min'],
                                   'Fails': ['Fixed it', 'Swapped RAM, PSU and reimaged']}, 'Specific and single beats vague and many.'), TRI),
        'unstable-workstation-capstone': same_as('pass-bar', 'Unstable workstation capstone', 'One domain, one change, one written result.'),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '3.1': {'start-here-files-live-on-storage': 'd6190754eef1', '1-three-common-drives': '8926fd53517f', '2-detect-before-you-image': '7ad3452f5760', 'reference-storage-interfaces-and-real-world-speeds': '42c556ffd97f', 'storage-devices-interfaces-form-factors-raid-and-removable-m': '2920ec52200f'},
    '3.2': {'backup-versus-raid-from-zero': 'e2afcd557c51', '1-levels-you-must-not-mix-up': '7d9ff8162cf3', '2-ticket-habit': 'd288aff74874', 'storage-and-raid-symptoms': '8c96f7d6a3e1'},
    '3.3': {'1-sealed-unit': 'ebbf8cae0fcd', '2-symptoms-that-look-like-a-dead-board': '53bd3d7cdefc', 'choosing-and-installing-a-power-supply': 'f8b24cfc5910'},
    '3.4': {'1-isolation-order': '6084fa0bebbf', '2-connectors': '94f425612149', 'reference-usb-thunderbolt-and-display-links-current-names': 'd263a6edc9a1', 'display-technologies-and-display-video-and-projector-trouble': '5ecec34ee03c', 'cable-types-and-connectors': '486bff68ed2f'},
    '3.5': {'worked-order': '19f9fb478a0a', 'pass-bar': '494d40203198'},
}

