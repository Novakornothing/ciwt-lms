"""Option B pass 2 — ITSUP chapter 9 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

WINH, SUDO, WIPE, SWOL = 'MC-IT9-WINDOWS-HABITS', 'MC-IT9-SUDO-NO-NOTE', 'MC-IT9-WIPE-MAC', 'MC-IT9-SWOLLEN-MAC'
ACCF, PWOS, BROAD, ABOUTV = 'MC-IT9-ACCESS-AS-FAULT', 'MC-IT9-PASSWORD-BY-OS', 'MC-R3-IT9-BROAD-PRIV', 'MC-R3-IT9-ABOUT-VIEW'
NTFSRO = 'MC-IT9-NTFS-READONLY-AS-FAULT'
LSH = ('linux-vm-shell', 'Find your way around a real Linux shell with read-only commands first.')
LABOUT = ('gui-about', 'Read the identity facts first, the same way you would on a Mac’s About This Mac.')
LINT = ('ticket-intake', 'Classify request versus break/fix and name the owner before acting.')


def _s(n, t):
    return f'Course lesson 9.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4 = _s(1, 'Linux Basics'), _s(2, 'macOS Basics'), _s(3, 'Shares and Remote Access'), _s(4, 'Mixed Environment Capstone')
SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


_add('9.1', '1-map-to-what-you-already-type', '1. Map to what you already type', 'IT-9.1', S1, [
    ('Which Linux command is the cousin of ipconfig /all?', 'ip a', 'lsblk', 'pwd',
     'ip a lists interfaces and addresses, like ipconfig /all.', WINH, WINH),
    ('lsblk is the cousin of which Windows step?', 'list disk', 'format C:', 'diskpart clean',
     'lsblk lists block devices, like list disk; neither wipes anything.', WINH, WINH),
    ('In the phrasebook story, what is the phrasebook?', 'The command map', 'The Linux kernel', 'A destructive verb list',
     'A phrasebook maps words you know to the local language, like the command map.', WINH, WINH),
    ('In the picture, hostname / whoami maps to…', 'hostnamectl / whoami', 'mkfs / fdisk -l', 'rm -rf / run with sudo',
     'Identity commands map to identity commands, never to destructive ones.', WINH, SUDO),
    ('Does lsblk mean you may now wipe a disk?', 'No, still not wipe', 'Yes, it prepares wiping', 'Yes, with sudo it is fine',
     'lsblk only reads, just like list disk; wiping stays out of scope.', WINH, BROAD),
],
    (['Linux has its own names for things you already do.', 'hostname and whoami become hostnamectl and whoami.', 'ipconfig /all becomes ip a.',
      'list disk becomes lsblk.', 'These commands only read.', 'None of them wipe anything.', 'Learn the map before you touch a real box.'],
     'Map each Windows reading habit to its Linux cousin, and keep it read-only.'),
    ('On holiday you carry a phrasebook. “Where is the station?” has a local version that means the same thing. You still would not '
     'shout an unknown phrase at a police officer just to see what happens.',
     [('Phrasebook', 'Windows-to-Linux command map'), ('Familiar question', 'ipconfig /all, list disk'), ('Local phrase', 'ip a, lsblk'),
      ('Unknown phrase shouted', 'A destructive command typed blindly')],
     'Phrases are harmless to try; some Linux commands are not, so only use mapped, read-only ones until you know more.'),
    ('two', 'Windows habit and Linux cousin', (('Windows', ['hostname / whoami', 'ipconfig /all', 'list disk']),
                                                ('Linux', ['hostnamectl / whoami', 'ip a', 'lsblk (still not wipe)']))),
     'Read across each row. Every pair is read-only. The chart gives you nothing that changes a disk or a setting.',
    'Sort each command to its Windows twin, then run the read-only commands in the Linux shell lab.',
    sort('Windows twin', {'ipconfig /all': ['ip a'], 'list disk': ['lsblk'], 'hostname / whoami': ['hostnamectl', 'whoami']},
         'Same habit, different spelling.'), LSH)

_add('9.1', 'linux-inventory-cousins', 'Linux inventory cousins', 'IT-9.1', S1, [
    ('Which is an inventory command?', 'lsblk', 'mkfs', 'rm -rf',
     'lsblk lists block devices; mkfs and rm change or destroy data.', WINH, WINH),
    ('What is sudo?', 'A change needing a ticket', 'A harmless shortcut', 'A way to skip writing notes',
     'sudo runs as administrator; it is a change that needs a record.', SUDO, SUDO),
    ('In the new-kitchen story, what is opening every cupboard?', 'Inventory commands', 'Running sudo', 'Formatting a whole disk',
     'Looking before touching, like pwd, ls and ip a.', WINH, WINH),
    ('In the picture, which command is NOT a first command?', 'mkfs', 'pwd', 'ls -la',
     'mkfs makes a filesystem and destroys data; never a first step.', WINH, WINH),
    ('Why learn the map without a Linux terminal here?', 'So a real box is not scary', 'To pass a typing test', 'To skip the Windows chapters',
     'Knowing the map stops panic and destructive guesses later.', WINH, WINH),
],
    (['On Linux, start by looking.', 'whoami and hostnamectl say who and where you are.', 'pwd shows your folder.', 'ls lists files.', 'ip a shows addresses.',
      'lsblk shows disks.', 'sudo makes a change, so it needs a ticket.', 'mkfs wipes a disk, so it is never first.'],
     'Look with read-only commands first; sudo needs a record and mkfs is never first.'),
    ('In a friend’s new kitchen, you open cupboards to see where things are before you cook. You do not knock out a wall. If you need '
     'to move the fridge, you ask first and say so.',
     [('Opening cupboards', 'pwd, ls, ip a, lsblk'), ('Asking before moving the fridge', 'sudo with a ticket'), ('Knocking out a wall', 'mkfs or rm -rf'),
      ('Friend’s kitchen', 'A Linux box you do not own')],
     'Cupboards do not change when opened, and neither do read-only commands; but in Linux one wrong flag can turn a read into a delete.'),
    ('two', 'Look first, change with a ticket', (('Read-only', ['whoami / hostnamectl', 'pwd, ls', 'ip a, lsblk']),
                                                   ('Change', ['sudo: ticket needed', 'mkfs: never first']))),
     'Spend your first minutes in the left column. Anything in the right column is a change that someone must approve and record.',
    'Sort each command, then try only the read-only ones in the Linux shell lab.',
    sort('Read or change?', {'Read-only': ['whoami', 'pwd', 'ls', 'ip a', 'lsblk'], 'Change': ['sudo apt upgrade', 'mkfs.ext4 /dev/sdb1']},
         'Same 2.6 habit, different spelling.'), LSH)

_add('9.2', 'a-mac-is-still-a-portable', 'A Mac is still a portable', 'IT-9.2', S2, [
    ('About This Mac is the cousin of which lab?', 'gui-about', 'gui-update', 'hw-cables',
     'About This Mac gives identity facts, like gui-about.', ABOUTV, ABOUTV),
    ('A MacBook battery is swollen. Which lesson applies?', 'The 4.1 battery stop', 'A macOS reinstall', 'A firmware (SMC) reset',
     'A swollen pack is a safety stop, as in 4.1.', SWOL, SWOL),
    ('In the company-car story, who owns the tracker?', 'The company', 'The driver', 'The local garage',
     'FileVault and MDM belong to the shop, like a tracker in a company car.', WIPE, WIPE),
    ('In the picture, mail fails on a managed Mac. What is NOT an option?', 'Hallway wipe', 'Radio check', 'Tenant check',
     'Check radio, tenant and enrollment; a hallway wipe is never an option.', WIPE, WIPE),
    ('FileVault is…', 'Shop property', 'A user’s own toy', 'A virus to remove',
     'FileVault and MDM are shop-controlled; do not remove them.', WIPE, WIPE),
],
    (['A Mac laptop is still a laptop.', 'About This Mac shows its identity.', 'FileVault and MDM belong to the shop.', 'A swollen battery is still a safety stop.',
      'If mail fails, check the radio first.', 'Then the tenant.', 'Then the enrollment.', 'Never wipe it in the hallway.'],
     'Treat a Mac like any managed portable: identity first, safety stop, and no hallway wipes.'),
    ('A company car is still a car, even if it is a different brand. You check the logbook, stop if the battery smokes, and leave the '
     'company tracker alone. If the radio fails, you check the station before calling it broken.',
     [('Different brand of car', 'Mac instead of a PC laptop'), ('Logbook', 'About This Mac'), ('Company tracker', 'FileVault and MDM'),
      ('Smoking battery', 'Swollen pack: 4.1 safety stop'), ('Radio station check', 'Radio vs tenant vs enrollment')],
     'A car tracker is visible; MDM and FileVault are invisible, so ask before assuming a Mac is personal.'),
    ('two', 'Same portable rules on a Mac', (('Check', ['About This Mac', 'Radio, tenant, enrollment']), ('Never', ['Hallway wipe', 'Press a swollen pack']))),
     'The left column is your first work. The right column is never on the list, whatever the brand of laptop.',
    'Sort each action, then read identity facts in the About lab as you would on a Mac.',
    sort('Do or never?', {'Do': ['Read About This Mac', 'Test radio vs tenant'], 'Never': ['Wipe it in the hallway', 'Charge a swollen pack']},
         'Brand does not change the rules.'), LABOUT)

_add('9.3', 'shares-and-accounts', 'Shares and accounts', 'IT-9.3', S3, [
    ('A user never had access to a share. What is it?', 'A request', 'A NIC fault', 'A dead switch',
     'Access never granted is an entitlement request, not a fault.', ACCF, ACCF),
    ('Where does the user’s password go?', 'Nowhere in the ticket', 'In the ticket notes', 'In the ticket title line',
     'Passwords never go in a ticket on any platform.', PWOS, PWOS),
    ('In the club story, who decides membership?', 'The club secretary', 'The doorman', 'The car-park attendant',
     'The directory owner decides entitlement, like a secretary decides membership.', ACCF, ACCF),
    ('In the flow, entitlement is the block. Next?', 'Escalate to owner', 'Replace the NIC', 'Reset the office router',
     'Escalate to the directory owner when entitlement blocks access.', ACCF, ACCF),
    ('Which line belongs in the ticket?', 'Requested access to HR share', 'Password is Summer2024!', 'NIC replaced, still no access',
     'Record the request, never the password, and do not invent a hardware fault.', PWOS, ACCF),
],
    (['Some users never had access to a share.', 'That is not a broken network.', 'It is a request.', 'Someone must grant it.',
      'Send it to the directory owner.', 'Keep the password out of the ticket.', 'Always.'],
     'Never-had-access means a request to the directory owner, and no passwords in tickets.'),
    ('A new member is turned away at a club door because their name is not on the list. The doorman cannot add it, and nothing is '
     'wrong with the door. The club secretary adds names. Nobody writes the member’s PIN on the guest list.',
     [('Name not on the list', 'Entitlement missing'), ('Door', 'Network card and path'), ('Club secretary', 'Directory owner'),
      ('PIN on the guest list', 'Password in the ticket')],
     'A doorman can see the list; a technician may not see group membership, so the request must still go to the owner.'),
    ('flow', 'Never had the share', ['Never had access?', 'Request, not fault', 'No password in ticket', 'Escalate to directory owner']),
     'The path never touches hardware. The only action is a well-written request to the person who controls entitlement.',
    'Reveal the answer after you write the ticket line.',
    reveal('A new hire cannot open \\\\fs01\\HR. Colleagues can. The user offers their password. What do you write?',
           '“Never had access to \\\\fs01\\HR: entitlement request. Escalated to directory owner. Password not recorded.”'), LINT)

_add('9.4', 'mixed-environment-note', 'Mixed environment note', 'IT-9.4', S4, [
    ('What three things does the note name first?', 'OS, user, request type', 'Brand, colour and price', 'Desk, chair and floor',
     'Name the OS, who is signed in, and request versus break/fix.', ACCF, WINH),
    ('Windows next door opens the share. Is the Mac NIC dead?', 'Not proven', 'Yes, clearly', 'Yes, replace it',
     'A Windows PC working does not prove anything about the Mac’s NIC.', NTFSRO, ACCF),
    ('In the twins story, why does one twin’s health not prove the other’s?', 'They are separate people', 'They share one heart', 'They live in the same house',
     'Two machines on one desk are separate; one working proves nothing about the other.', NTFSRO, NTFSRO),
    ('In the picture, what comes after naming the OS?', 'Who is signed in', 'Replace the NIC', 'Wipe the Mac first',
     'OS, then user, then request or break/fix.', WIPE, WINH),
    ('Is this a request or break/fix?', 'Decide before acting', 'It does not matter', 'Always treat as break/fix',
     'Classifying first decides the owner and next step.', ACCF, ACCF),
],
    (['Offices often mix Windows, Mac and Linux.', 'Name the operating system first.', 'Name who is signed in.', 'Say if it is a request or a fault.',
      'A Windows PC opening a share proves nothing about the Mac.', 'Test the Mac itself.'],
     'Name the OS, the user and the ticket type, and test the machine in front of you.'),
    ('Twins can look alike, but one twin’s clean bill of health says nothing about the other. The doctor examines each one and writes '
     'their own name on their own chart.',
     [('Twin A is healthy', 'Windows PC opens the share'), ('Twin B', 'The Mac with the problem'), ('Own chart with own name', 'Note naming OS and user'),
      ('Examining each twin', 'Testing the Mac itself')],
     'Twins share genes; two PCs share the network, so a shared path can still matter. Test it from the Mac, not from Windows.'),
    ('flow', 'Mixed environment note', ['Name the OS', 'Who is signed in', 'Request or break/fix', 'Test this machine']),
     'Every ticket in a mixed office starts with these four boxes. The neighbour’s PC is never a box on this chart.',
    'Order the note, then classify a mixed-environment ticket in the intake lab.',
    order('Mixed note', ['Name the OS', 'Name the signed-in user', 'Request or break/fix', 'Test the affected machine'],
          'The next desk proves nothing about this one.'), LINT)
