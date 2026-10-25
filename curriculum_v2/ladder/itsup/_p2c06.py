"""Option B pass 2 — ITSUP chapter 6 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

_P = 'MC-L-IT6-'
HOWN, FIVE, HVT, SAASR, IAAS, CDEF, SNAPB, SNAPK, VSW, GUESS = (_P + k for k in (
    'HOST-OWN', 'FIVE-NICS', 'HV-TYPE', 'SAAS-REIMAGE', 'IAAS-OS', 'CLOUD-DEF', 'SNAP-BACKUP', 'SNAP-KEEP', 'VSWITCH', 'GUESS-FACT'))
VM = ('virt-vm', 'Inventory the guest, then decide whether the next question belongs to the host owner.')
ABOUT = ('gui-about', 'Read About in the guest and name the machine before anything else.')
VSWL = ('hv-vswitch', 'Check the VM’s switch type and adapter, then run the Chapter 5 order inside the guest.')


def _s(n, t):
    return f'Course lesson 6.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4 = _s(1, 'Virtualization'), _s(2, 'Cloud Models'), _s(3, 'Snapshots and Virtual Networks'), _s(4, 'Slow VM Capstone')
SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


_add('6.1', 'core-content', 'Core content', 'IT-6.1', S1, [
    ('Which hypervisor type runs directly on the hardware?', 'Type 1', 'Type 2', 'Type 0 (no hypervisor)',
     'Type 1 (bare-metal) runs on the hardware; type 2 runs as an app on a desktop OS.', HVT, HVT),
    ('Task Manager shows “Virtual machine: Yes”. What does it mean?', 'You are inside a guest', 'Hyper-V is turned off', 'The CPU lacks VT-x support',
     'That line appears when Windows itself runs as a guest VM.', HVT, HOWN),
    ('In the apartment story, what is the building owner?', 'The host', 'A guest VM', 'The vNIC',
     'The building holds every flat, like the host holds every guest.', HOWN, VSW),
    ('In the picture, which product is type 2?', 'VirtualBox', 'VMware ESXi', 'Microsoft Hyper-V',
     'VirtualBox runs as an app on a desktop OS; ESXi and Hyper-V are type 1.', HVT, HVT),
    ('Hyper-V will not install on a PC. Which check first?', 'Windows edition', 'Monitor size', 'The keyboard layout',
     'Hyper-V needs Pro, Enterprise or Education, plus virtualization enabled in firmware.', HVT, HVT),
],
    (['A hypervisor lets one computer run several virtual computers.', 'The real computer is the host.', 'Each virtual one is a guest.',
      'Type 1 runs straight on the hardware.', 'Type 2 runs as an app on Windows or macOS.', 'Hyper-V is type 1, even on a desktop.',
      'Task Manager tells you if you are inside a guest.'],
     'Name the host and the guest, and check Task Manager and the Windows edition before anything else.'),
    ('An apartment block is one building with many flats. Each flat has its own door, kitchen and fuse box, but all of them share the '
     'building’s water main and lift. Some blocks are purpose-built for flats; others are a house with a lodger’s room added on.',
     [('The building', 'Host computer'), ('Each flat', 'Guest virtual machine'), ('Building manager', 'Hypervisor'),
      ('Purpose-built block', 'Type 1 (bare-metal)'), ('House with a lodger room', 'Type 2 (hosted)')],
     'Flats have real walls; guests only feel separate. A busy host can slow every guest at once, which walls would never do.'),
    ('two', 'Two kinds of hypervisor', (('Type 1 (bare-metal)', ['Runs on the hardware', 'Hyper-V, ESXi, KVM', 'Server rooms, Win 11 Pro']),
                                        ('Type 2 (hosted)', ['Runs as an app', 'VirtualBox, Workstation', 'A tech’s lab laptop']))),
     'Read each column top to bottom. Hyper-V sits in the left column even on a desktop, because it loads before Windows.',
    'Sort each product and clue, then read About in the guest lab to name the machine.',
    sort('Type 1 or type 2?', {'Type 1': ['VMware ESXi', 'Microsoft Hyper-V', 'KVM'], 'Type 2': ['Oracle VirtualBox', 'VMware Workstation']},
         'Hyper-V is type 1 even on a Windows 11 Pro desktop.'), ABOUT)

_add('6.1', 'host-versus-guest', 'Host versus guest', 'IT-6.1', S1, [
    ('Five guests fail together. Who do you call?', 'The host owner', 'Five NIC suppliers', 'Each guest’s user in turn',
     'Many guests failing together points at the shared host, not each guest.', FIVE, HOWN),
    ('What do you inventory first?', 'The guest', 'The host datastore', 'The cluster switches',
     'Start with what you can see and own: the guest.', HOWN, HOWN),
    ('In the bus story, what is the bus?', 'The host', 'The guest', 'The ticket',
     'If the bus breaks down, every passenger is late, as every guest suffers when the host fails.', FIVE, FIVE),
    ('In the picture, which arrow points at the host owner?', 'Five guests fail at once', 'One guest has APIPA', 'One user forgot a password',
     'Simultaneous failure across guests points at the shared host.', FIVE, FIVE),
    ('The bench PC is NOVAK-W11-07. What may it be?', 'A guest VM', 'The physical host', 'A network switch',
     'The Windows you type in on the bench may already be a guest.', HOWN, HOWN),
],
    (['The Windows you use in class may be a guest.', 'The host is the machine that holds its files.', 'If the host’s disk fills up, every guest looks sick.',
      'Check the guest first.', 'If the guest looks healthy, look at the pattern.', 'Five guests failing together means the host.', 'Call the host owner, not five NIC suppliers.'],
     'Check the guest first; if many guests fail together, hand the question to the host owner.'),
    ('Passengers on a bus are all late when the bus breaks down. You would not send each passenger to a doctor. You call the bus '
     'company. If only one passenger is late, you ask that passenger what happened.',
     [('The bus', 'Host computer or cluster'), ('Each passenger', 'Guest VM'), ('Bus company', 'Host owner'),
      ('One late passenger', 'One failing guest: inventory it')],
     'Passengers can step off the bus; guests cannot leave a host on their own, and moving them is the host owner’s job.'),
    ('flow', 'Guest first, then the pattern', ['Inventory the guest', 'Guest healthy?', 'Others failing too?', 'Ask host owner']),
     'If the guest is unhealthy on its own, fix it inside. If many guests fail at once, the last box is the right next step.',
    'Sort each situation, then inventory a guest in the VM lab.',
    sort('Guest or host?', {'Work inside the guest': ['One guest has 169.254', 'One guest’s disk is full'],
                            'Ask the host owner': ['Five guests slow at 10:02', 'Every guest lost network together']}, 'Patterns point upward.'), VM)

_add('6.1', 'teach-block-you-may-already-be-a-guest', 'Teach block — you may already be a guest', 'IT-6.1', S1, [
    ('What do trainees read first?', 'About and inventory', 'The host’s logs', 'The cluster vendor manual',
     'Start inside: read About and inventory the guest.', HOWN, HOWN),
    ('What plan must the class not make?', 'Five NIC swaps', 'A host question', 'A guest inventory',
     'Five guests dying together is a host story, not five hardware jobs.', FIVE, FIVE),
    ('In the play story, who owns the theatre?', 'The host owner', 'The lead actor', 'The audience',
     'Actors are guests on the stage; the theatre owner fixes the building.', HOWN, HOWN),
    ('In the flow, what comes after “name the guest”?', 'Ask who owns the host', 'Order five NICs', 'Reimage the guest straight away',
     'After naming the guest, ask whose host it is.', FIVE, HOWN),
    ('Why name the guest first?', 'So the owner knows which VM', 'To use up class time', 'To change its name to something new',
     'A name lets the host owner find the exact VM.', GUESS, HOWN),
],
    (['Open About on the class PC.', 'Read its name.', 'It may be a virtual machine.', 'Write that down.', 'Then ask a question.',
      'If five of these died together, who would you call?', 'The answer is the host owner.', 'Not five network card swaps.'],
     'Name the guest, then ask who owns the host.'),
    ('Actors on a stage play their parts, but the theatre owns the lights and the roof. If every actor goes dark at once, nobody blames '
     'the actors. Someone calls the theatre manager.',
     [('Actor', 'Guest VM'), ('Stage and lights', 'Host hardware'), ('Theatre manager', 'Host owner'), ('Everyone goes dark', 'Five guests fail together')],
     'Actors know they are on a stage; a guest VM can look exactly like a real PC, so you must check About to know.'),
    ('flow', 'Teach block steps', ['Read About', 'Inventory', 'Name the guest', 'Who owns the host?']),
     'Every trainee walks these four boxes on their own bench PC. The class does not plan any hardware swap during this block.',
    'Order the steps, then read About in the lab and write the guest name.',
    order('Am I a guest?', ['Open About', 'Inventory the machine', 'Write the guest name', 'Ask who owns the host'],
          'The question about the host is the point of the block.'), ABOUT)

_add('6.2', 'core-content', 'Core content', 'IT-6.2', S2, [
    ('Who patches the guest OS in IaaS?', 'You do', 'The provider', 'Nobody needs to',
     'In IaaS you still own the guest OS and its patching.', IAAS, IAAS),
    ('A server in a cupboard reached over the internet. Cloud?', 'No, not by NIST’s rules', 'Yes, it is online', 'Yes, if it has a website',
     'Cloud needs self-service, pooling, elasticity and metering, not just internet access.', CDEF, CDEF),
    ('In the restaurant story, what is SaaS?', 'Eating in', 'Cooking at home', 'Renting a kitchen',
     'Eating in, the restaurant runs everything except your order and payment.', SAASR, IAAS),
    ('In the responsibility picture, what is always yours?', 'Data and accounts', 'The data centre', 'The platform operating system',
     'Data, endpoints and identities stay yours in every model.', IAAS, SAASR),
    ('Many users across sites fail; the provider lists an incident. Next?', 'Record the ID, tell users', 'Reimage each laptop', 'Reset every user’s password',
     'It is the provider’s fix; record the incident and stop changing PCs.', SAASR, SAASR),
],
    (['Cloud means more than “on the internet”.', 'It is self-service, shared, stretchy and metered.', 'There are three service models.',
      'In IaaS you run the guest OS.', 'In PaaS you run only your app.', 'In SaaS you run only accounts and data.', 'Your data and accounts are always yours.'],
     'Know which layer you own, and check the provider’s status before touching PCs.'),
    ('Dinner can happen three ways. You can rent a kitchen and cook everything yourself. You can buy a meal kit and just assemble it. '
     'Or you can eat at a restaurant. In every case, you choose what to order and you pay the bill.',
     [('Rented kitchen', 'IaaS: you run the guest OS'), ('Meal kit', 'PaaS: you run your app'), ('Restaurant', 'SaaS: you run accounts and data'),
      ('Your order and the bill', 'Your data and identities')],
     'A restaurant closes in the evening; cloud outages come without warning, so check the provider’s status page every time.'),
    ('two', 'Who owns which layer?', (('You', ['Data and accounts (always)', 'Guest OS (IaaS)', 'Your code (PaaS)']),
                                      ('Provider', ['Hardware and data centre', 'Platform OS (PaaS, SaaS)', 'The application (SaaS)']))),
     'The left column never empties, whatever the model. Work there; ask the provider about anything in the right column.',
    'Sort each task to its owner in IaaS, then compare with SaaS.',
    sort('IaaS: who does it?', {'You': ['Patch the guest OS', 'Manage user accounts', 'Protect your data'],
                                'Provider': ['Replace a failed host disk', 'Run the data centre']}, 'Your data is always yours.'), VM)

_add('6.2', 'what-you-may-touch', 'What you may touch', 'IT-6.2', S2, [
    ('Outlook 365 is down for the whole tenant. Reimage?', 'No, it is the provider’s', 'Yes, start with one PC', 'Yes, reimage them all tonight',
     'A tenant-wide SaaS problem is not fixed on a laptop.', SAASR, SAASR),
    ('In PaaS, what do you own?', 'The app path', 'The platform OS', 'The data-centre network',
     'In PaaS you own your application path, not the platform OS.', IAAS, IAAS),
    ('In the rental story, what can you change in a hotel room?', 'Your own luggage', 'The hotel’s wiring', 'The lift motor',
     'You own what you brought in, like accounts and clients in SaaS.', SAASR, SAASR),
    ('In the picture, what goes in every cloud ticket?', 'Tenant name and scope', 'The user’s home address', 'Their manager’s mobile',
     'Write the tenant name and whether other users fail.', SAASR, CDEF),
    ('In IaaS, a guest has no network. Which chapters apply inside?', 'Chapters 2–5', 'Chapter 10 only', 'None, call the provider',
     'You own the guest OS in IaaS, so normal client chapters apply.', IAAS, IAAS),
],
    (['In SaaS you look after the account, the licence and the app on the PC.', 'You do not reimage for a tenant-wide outage.',
      'In IaaS you still run the guest OS.', 'Use chapters 2 to 5 inside it.', 'In PaaS you run your app only.',
      'Always write the tenant name.', 'Write whether other users fail too.'],
     'Touch only your layer, and write the tenant and the scope on the ticket.'),
    ('In a hotel you may move your luggage, change the thermostat and call reception. You may not rewire the room. If every room loses '
     'power, the problem is the hotel’s, and unpacking your suitcase again will not help.',
     [('Your luggage', 'Account, licence and client'), ('Room wiring', 'Provider platform'), ('Every room loses power', 'Tenant-wide outage'),
      ('Unpacking again', 'Reimaging a laptop')],
     'A hotel shows a notice in the lobby; providers publish status pages and admin-centre health, which you must check yourself.'),
    ('two', 'What you may touch', (('SaaS', ['Account, licence, client']), ('IaaS', ['Guest OS: chapters 2–5']))),
     'PaaS sits between them: your app path only. Every ticket in any column records the tenant name and whether other users fail.',
    'Reveal the answer after you decide what you may touch.',
    reveal('Three users at two sites cannot open Outlook 365; the admin centre lists an Exchange incident. What do you do and not do?',
           'Record the incident ID and tenant, tell users, and stop. Do not reimage, reset passwords or reinstall Office.'), VM)

_add('6.3', 'snapshots-and-virtual-cables', 'Snapshots and virtual cables', 'IT-6.3', S3, [
    ('Is a snapshot a backup?', 'No, it sits beside the disks', 'Yes, a full off-site copy', 'Yes, once it is a week old or more',
     'A snapshot lives next to the live disks; it is not a separate copy elsewhere.', SNAPB, SNAPB),
    ('What do week-old snapshot chains do?', 'Fill the datastore', 'Speed up every guest', 'Protect against fire',
     'Long chains grow and slow every guest on that datastore.', SNAPK, SNAPK),
    ('In the bookmark story, what is the bookmark?', 'A snapshot', 'A backup copy', 'A virtual NIC',
     'A bookmark marks a page in the same book; it is not a copy of the book.', SNAPB, SNAPB),
    ('In the flow, the guest has APIPA and the host network is up. Next?', 'Ask about vNIC/port group', 'Reinstall the guest', 'Flush DNS inside the guest OS',
     'With a healthy host network, ask the host owner about the vNIC, port group or uplink.', VSW, VSW),
    ('Where do you isolate first?', 'Inside the guest', 'On the host', 'At the physical uplink',
     'Run ipconfig inside the guest first; you own that part.', HOWN, VSW),
],
    (['A snapshot is a bookmark.', 'It sits next to the live disks.', 'It is not a copy in another building.', 'Old snapshots pile up.',
      'They fill the storage and slow everyone.', 'A virtual network card can be unplugged in the hypervisor.', 'Check ipconfig in the guest first.',
      'Then ask the host owner about the virtual cable.'],
     'Treat snapshots as short-lived bookmarks, and ask the host owner about virtual cables after the guest checks.'),
    ('A bookmark marks a page in your book. If the book burns, the bookmark burns too. Leaving a hundred bookmarks in makes the book fat '
     'and slow to open. And a lamp that looks plugged in may be switched off at the wall in another room.',
     [('Bookmark', 'Snapshot'), ('The book', 'Live virtual disks'), ('Hundred bookmarks', 'Old snapshot chain'),
      ('Lamp switched off in another room', 'vNIC disconnected in the hypervisor')],
     'Removing a bookmark is harmless; merging or deleting a snapshot changes disks and belongs to the host owner.'),
    ('flow', 'Guest has no network', ['ipconfig in guest', 'No adapter or APIPA', 'Host network up?', 'Ask host owner: vNIC, port group']),
     'Start inside the guest. Only the last box crosses to the host, and it is a question, not a change you make.',
    'Sort each statement, then check the switch type and adapter in the virtual switch lab.',
    sort('True or false?', {'True': ['A snapshot sits beside the live disks', 'A vNIC can be disconnected in the hypervisor'],
                            'False': ['A snapshot is an off-site backup', 'Old snapshot chains speed up guests']}, 'Snapshots are bookmarks.'), VSWL)

_add('6.4', 'core-content', 'Core content', 'IT-6.3', S4, [
    ('What comes first in the slow-VM note?', 'Guest facts with values', 'The host owner’s guess', 'A list of every fix you tried',
     'Guest facts with real values come first; host ideas are labelled guesses.', GUESS, GUESS),
    ('Why is “checkpoint chain on host” labelled a guess?', 'You cannot see the host', 'It sounds more polite', 'Guesses read faster in notes',
     'From inside the guest you cannot confirm it; the host owner must check.', GUESS, GUESS),
    ('In the tenant story, what is the landlord?', 'The host owner', 'The guest user', 'The help desk',
     'The landlord owns the building systems, like the host owner owns the host.', HOWN, HOWN),
    ('In the evidence table, which column do you collect?', 'Guest', 'Host', 'Provider',
     'You collect guest evidence and ask the host or provider for theirs.', GUESS, HOWN),
    ('Which action is allowed for you?', 'Read guest Task Manager', 'Merge host checkpoints', 'Reimage the guest to speed it',
     'Reading guest facts is yours; checkpoints and reimaging are not.', SNAPB, HOWN),
],
    (['A slow VM needs the same habits as a slow PC.', 'Collect facts inside the guest.', 'Give each fact a number.', 'RAM use, CPU use, free disk.',
      'Then ipconfig and a ping.', 'Write host ideas as guesses.', 'Ask the host owner to confirm them.', 'Do not touch checkpoints you do not own.'],
     'Guest facts with values first, host ideas labelled as guesses, and nothing changed outside your layer.'),
    ('A tenant reports a cold flat. They write the thermostat reading, which rooms are cold and since when. They might suspect the '
     'building boiler, but they write “maybe the boiler” and let the landlord check. They do not open the boiler room.',
     [('Thermostat reading', 'Guest RAM, CPU and disk values'), ('Which rooms and since when', 'Symptom and start time'),
      ('“Maybe the boiler”', 'Host guess, labelled'), ('Landlord', 'Host owner'), ('Boiler room', 'Host checkpoints and datastore')],
     'A tenant can feel the cold; a guest cannot see host load at all, so your guess may be wrong in either direction.'),
    ('two', 'Collect versus ask', (('Guest (you collect)', ['Name, OS, VM: Yes', 'RAM, CPU, free disk', 'ipconfig, ping, errors']),
                                    ('Host (you ask)', ['Which host or cluster', 'Datastore space', 'Checkpoint chain']))),
     'Fill the left column with values. Turn the right column into questions for the owner. Nothing in the right column is a change you make.',
    'Order the note, then inventory the guest in the VM lab and write one ask for the host owner.',
    order('Slow VM note', ['Identity: name, OS, VM: Yes', 'Guest values: RAM, CPU, disk', 'Network: ipconfig and ping', 'Guess labelled as guess',
                           'Ask to the host owner'], 'Facts first, guesses labelled, asks last.'), VM)
