"""Explanation ladder — ITSUP chapter 6 (Virtual Machines, Cloud Models, Snapshots and vSwitches, Slow VM). Pending SME review.

Distinct concept sections are laddered; core, teach-block and repeated sections that restate a core section of the
same lesson use same_as.
"""
from curriculum_v2.ladder.itsup._lk import M, P, X
from curriculum_v2.ladder.schema import order, reveal, same_as, sort

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 6


def _s(n, t):
    return f'Course lesson 6.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4 = _s(1, 'Virtual Machines'), _s(2, 'Cloud Models'), _s(3, 'Snapshots and Virtual Switches'), _s(4, 'Slow VM Capstone')
_P = 'MC-L-IT6-'
MISCONCEPTIONS = {
    **M(_P, S1, {
        'HOST-OWN': ('IT-6.1', 'Tuning or fixing a host you do not own', 'Inventory the guest; escalate host problems to the host owner.', ['host', 'guest']),
        'FIVE-NICS': ('IT-6.1', 'Planning hardware swaps in each guest when many guests fail together', 'Many guests failing together points at the host.', ['guest', 'nic']),
        'HV-TYPE': ('IT-6.1', 'Mixing up type 1 and type 2 hypervisors', 'Type 1 on the metal; type 2 as an app on a desktop OS.', ['type 1', 'type 2']),
    }),
    **M(_P, S2, {
        'SAAS-REIMAGE': ('IT-6.2', 'Reimaging a laptop for a tenant-wide SaaS problem', 'If the whole tenant fails, escalate to the tenant owner.', ['saas', 'tenant']),
        'IAAS-OS': ('IT-6.2', 'Thinking the provider patches the guest OS in IaaS', 'In IaaS you own the guest OS.', ['iaas', 'guest os']),
        'CLOUD-DEF': ('IT-6.2', 'Calling any internet-reachable server “cloud”', 'NIST: self-service, broad access, pooling, elasticity, measured.', ['cloud', 'nist']),
    }),
    **M(_P, S3, {
        'SNAP-BACKUP': ('IT-6.3', 'Treating a snapshot as a backup', 'A snapshot sits beside the live disks; it is not an off-site copy.', ['snapshot', 'backup']),
        'SNAP-KEEP': ('IT-6.3', 'Leaving snapshot chains for weeks', 'Delete or consolidate when the change is done.', ['snapshot', 'datastore']),
        'VSWITCH': ('IT-6.3', 'Chasing DNS when the VM is on the wrong virtual switch', 'Internal/private switches have no LAN DHCP; check switch type.', ['virtual switch', 'internal']),
    }),
    **M(_P, S4, {
        'GUESS-FACT': ('IT-6.3', 'Writing a host guess as if it were a fact', 'Guest facts first; label host ideas as guesses.', ['note', 'guess']),
    }),
}
HO, FN, HT, SR, IO, CD, SB, SK, VS, GF = (_P + k for k in (
    'HOST-OWN', 'FIVE-NICS', 'HV-TYPE', 'SAAS-REIMAGE', 'IAAS-OS', 'CLOUD-DEF', 'SNAP-BACKUP', 'SNAP-KEEP', 'VSWITCH', 'GUESS-FACT'))
VM = ('virt-vm', 'Inventory the guest, then decide whether the next question belongs to the host owner.')
ABOUT = ('gui-about', 'Read About in the guest and name the machine before anything else.')
VSW = ('hv-vswitch', 'Check the VM’s switch type and adapter, then run the Chapter 5 order inside the guest.')

LESSONS = {
    '6.1': {
        'start-here-virtual-machines': X('Start here — virtual machines', 'IT-6.1', S1, [
            ('What is a virtual machine?', 'A computer made of files', 'A very small physical laptop', 'A remote desktop shortcut only',
             'A VM is a computer built from files on another computer, the host.', HO, None),
            ('The host runs out of disk. What do guests do?', 'All look sick', 'Only one guest slows', 'Nothing changes for them',
             'Every guest depends on the host, so all of them suffer.', FN, FN),
            ('In the flats story, what is the host?', 'The building', 'One flat on the top floor', 'The tenants’ furniture',
             'Flats share the building’s plumbing, like guests share the host.', HO, None),
            ('What do you inventory first?', 'The guest', 'The host datastore', 'The cluster network',
             'You start with what you own: the guest.', HO, None),
            ('May you delete a snapshot you do not own?', 'No', 'Yes, to free space', 'Yes, if it is old',
             'Snapshots belong to whoever took them.', HO, None),
        ],
            P('A virtual machine is a whole computer made of files that run on another, physical computer called the host. The Windows you work in on '
              'the training bench may already be one. When the host fills its disk or loses its network, every virtual machine on it looks broken. '
              'Still, begin by inventorying the guest you are in, and never delete a snapshot that is not yours.'),
            P('Picture a block of flats. Each flat has its own front door, rooms and furniture, like a guest. But they all share one building, its '
              'water main and its wiring, like the host. If the water main bursts, every flat has no water at once. You would not replumb five '
              'kitchens; you would call the building manager.'),
            ['Read About in the guest.', 'Is it a VM?', 'Inventory the guest.', 'Did many guests fail together?', 'Yes: call the host owner.'],
            '<p>Sort each item.</p>',
            sort('Guest or host?', {'Guest': ['Computer name', 'RAM the guest sees', 'ipconfig in the VM'], 'Host': ['Datastore space', 'Physical NIC', 'Cluster']},
                 'Start with what you own.'), ABOUT),
        'core-content': same_as('2-type-1-vs-type-2-only-what-you-need', 'Core content', 'Hypervisor types and Hyper-V in depth.'),
        '1-two-machines-in-one-ticket': X('1. Two machines in one ticket', 'IT-6.1', S1, [
            ('“My VM is slow” and the guest looks fine. Next?', 'Ask the host owner', 'Tune the host settings yourself', 'Reinstall the guest operating system',
             'A healthy guest points at host pressure, which someone else owns.', HO, HO),
            ('Five guests fail together. Plan?', 'Escalate to host owner', 'Swap five NICs, one per guest', 'Reimage each guest',
             'A shared failure points at the shared host.', FN, FN),
            ('In the train story, why not fix each seat?', 'The engine is shared', 'Seats are cheap to replace', 'Trains are long',
             'When every carriage stops, look at the engine.', FN, None),
            ('What does guest inventory use?', 'Chapter 2.6 steps', 'Host console access', 'A new snapshot',
             'About, systeminfo and list disk inside the guest.', HO, None),
            ('Which question splits the ticket?', 'Guest or host?', 'Which colour is the case?', 'Which user?',
             'Out of RAM/disk in the guest, or host oversubscribed?', HO, None),
        ],
            P('A slow virtual machine ticket involves two computers: the guest the user sees and the host it runs on. Check the guest first using '
              'the inventory steps from Chapter 2.6: memory, disk, what Windows reports. If the guest looks healthy, or several guests suffer together, '
              'the host is the suspect, and that belongs to the host owner. Do not try to tune a host you do not own.'),
            P('When every carriage of a train stops at once, nobody checks each seat for a fault; the problem is the engine pulling them all. If only '
              'one passenger is uncomfortable, look at that seat. A virtual machine ticket works the same way: one sick guest, look inside it; many '
              'sick guests together, ask whoever runs the engine.'),
            ['Inventory the guest.', 'Guest short of RAM or disk?', 'Fix what you own.', 'Guest fine or many fail?', 'Escalate to the host owner.'],
            '<p>Sort each finding.</p>',
            sort('Who acts?', {'You (guest)': ['Guest disk 98% full', 'Guest RAM maxed'], 'Host owner': ['Five guests slow together', 'Datastore full', 'Host NIC down']},
                 'Shared symptoms point at the shared host.'), VM),
        '2-type-1-vs-type-2-only-what-you-need': X('2. Type 1 vs type 2 — only what you need', 'IT-6.1', S1, [
            ('VirtualBox on a laptop is which type?', 'Type 2', 'Type 1, bare-metal', 'Neither of the two types',
             'Type 2 runs as an application on a desktop OS.', HT, HT),
            ('VMware ESXi runs…', 'On the hardware', 'Inside Windows as an app', 'Only in the cloud',
             'Type 1 sits directly on the metal.', HT, None),
            ('In the house story, what is type 2?', 'A tent in the garden', 'The house foundation', 'The roof',
             'It sits on top of something else, like a tent on a lawn.', HT, None),
            ('Hyper-V on Windows 11 Pro is…', 'Type 1', 'Type 2', 'Not a hypervisor',
             'Hyper-V loads first; Windows becomes its root partition.', HT, None),
            ('For tickets, the key question is…', 'Who owns the host?', 'Which one is faster to boot?', 'Which is newer?',
             'Ownership decides whether you may touch it.', HO, None),
        ],
            P('Hypervisors come in two kinds. Type 1 runs directly on the hardware, as shop servers do with ESXi, KVM or Hyper-V. Type 2 runs as a '
              'program on an ordinary desktop, like VirtualBox on a laptop with one lab machine. Hyper-V counts as type 1 even on a Windows desktop. '
              'For tickets the type matters less than one question: who owns the host, and are you allowed to touch it?'),
            P('A house built on its own foundation stands straight on the ground: that is type 1. A tent pitched in the garden sits on top of '
              'something that was already there: that is type 2. Both give shelter. Either way, before you start moving walls or pegs, you check '
              'whose property it is.'),
            ['On the metal or in an app?', 'Name the type.', 'Find the host owner.', 'May you touch it?', 'Write it on the ticket.'],
            '<p>Sort each product.</p>',
            sort('Hypervisor type', {'Type 1': ['VMware ESXi', 'KVM', 'Hyper-V'], 'Type 2': ['VirtualBox', 'VMware Workstation']}, 'Hyper-V is type 1 even on a desktop.'), VM),
        'host-versus-guest': same_as('1-two-machines-in-one-ticket', 'Host versus guest', 'Guest first; many failing guests point at the host.'),
        'teach-block-you-may-already-be-a-guest': same_as('1-two-machines-in-one-ticket', 'Teach block — you may already be a guest', 'Name the guest, then ask who owns the host.'),
    },
    '6.2': {
        'core-content': same_as('1-what-you-can-touch', 'Core content', 'Cloud definition and the shared-responsibility table.'),
        '1-what-you-can-touch': X('1. What you can touch', 'IT-6.2', S2, [
            ('In IaaS, who patches the guest OS?', 'You', 'The cloud provider always does', 'Nobody needs to patch it',
             'IaaS hands you the guest OS; Chapters 2–5 apply inside it.', IO, IO),
            ('In SaaS you usually touch…', 'Account, licence, client', 'The vendor servers and storage', 'The platform OS',
             'SaaS: you manage users and clients, not servers.', SR, None),
            ('In the restaurant story, what is SaaS?', 'Eating out', 'Renting a kitchen', 'Growing food',
             'SaaS: the meal is ready; you only order.', SR, None),
            ('In PaaS you own…', 'The app path', 'The platform OS', 'The data centre',
             'PaaS: your code and settings, not the OS beneath.', IO, None),
            ('Which is cloud by NIST?', 'Self-service, metered', 'Any server reachable online', 'A cupboard server',
             'Self-service, pooled, elastic, measured, broad access.', CD, None),
        ],
            P('Cloud services split the work between you and the provider. With software as a service you manage accounts, licences and the client app; '
              'the vendor runs the rest. With infrastructure as a service you run the guest operating system yourself, using everything from Chapters 2 '
              'to 5. With platform as a service you own your app and its settings, not the system underneath.'),
            P('Think of food. Software as a service is eating at a restaurant: you choose from the menu and pay. Platform as a service is renting a '
              'kitchen with ovens supplied: you cook your own dish. Infrastructure as a service is renting an empty building with gas and water: you '
              'fit the kitchen and run it. Each step gives you more to look after.'),
            ['Name the model.', 'SaaS: account, licence, client.', 'PaaS: app settings, deploy path.', 'IaaS: guest OS.', 'Everything else: provider.'],
            '<p>Sort who looks after each item in IaaS.</p>',
            sort('IaaS responsibility', {'You': ['Guest OS patches', 'Accounts', 'Your data'], 'Provider': ['Physical hosts', 'Data centre', 'Hypervisor']},
                 'IaaS gives you the guest OS.'), VM),
        '2-ticket-habit': X('2. Ticket habit', 'IT-6.2', S2, [
            ('Outlook 365 is yellow for the whole tenant. You…', 'Escalate to tenant owner', 'Reimage the user’s laptop', 'Change DNS on a working LAN',
             'A tenant-wide problem is not fixed on one laptop.', SR, SR),
            ('Which belongs on the ticket?', 'Tenant name and error', 'The laptop colour and model', 'Favourite browser',
             'Tenant or subscription name, error text, who else fails.', SR, None),
            ('In the power-cut story, why not rewire your flat?', 'The whole street is off', 'Wires are cheap to replace', 'You are bored',
             'If everyone is affected, the fault is upstream.', SR, None),
            ('Ask whether others in the tenant…', 'Also fail', 'Like the app', 'Use Macs',
             'Scope decides whether it is one user or the tenant.', SR, None),
            ('Guessing a DNS fix on a working LAN is…', 'Wrong', 'Standard', 'Required',
             'Do not change a working LAN because a SaaS icon is yellow.', SR, None),
        ],
            P('For a cloud service ticket, write the tenant or subscription name, the exact error text, and whether other users in the same tenant are '
              'also failing. If they are, escalate to the tenant owner. Do not invent a DNS change on a network that works fine just because the '
              'Outlook icon has turned yellow.'),
            P('If every house on the street loses power, you do not rewire your own flat. You check whether the neighbours are dark too and then ring '
              'the electricity company with your address. A tenant-wide cloud problem is that street-wide power cut: note who else is affected and '
              'report it to the owner.'),
            ['Tenant name.', 'Error text.', 'Do others fail?', 'Yes: tenant owner.', 'No: user account or client.'],
            '<p>Put the cloud ticket steps in order.</p>',
            order('Cloud ticket', ['Write tenant name', 'Copy error text', 'Check other users', 'Escalate to owner'], 'Scope before any change.'), VM),
        'what-you-may-touch': same_as('1-what-you-can-touch', 'What you may touch', 'SaaS, IaaS and PaaS boundaries again.'),
        'virtualization-use-cases-cloud-models-and-cloud-productivity': X('Virtualization use cases, cloud models and cloud productivity administration', 'IT-6.2', S2, [
            ('Opening a suspicious file safely uses a…', 'Sandbox VM', 'Shared network drive', 'Second user account on the PC',
             'A sandbox VM isolates the file from the real machine.', CD, None),
            ('What must be enabled in UEFI to run VMs?', 'Virtualization extensions', 'Secure Boot switched fully off', 'Legacy BIOS',
             'CPU virtualization extensions must be on.', CD, None),
            ('In the test-kitchen story, why snapshots?', 'Reset after a mess', 'Cook every dish much faster', 'Save money',
             'Test environments can be reset to a known state.', SB, None),
            ('A Windows VM on a Mac is for…', 'Cross-platform work', 'A faster Mac boot time', 'Backups',
             'Run software for another OS.', CD, None),
            ('An old app on an old OS in an isolated VM is…', 'Legacy support', 'Sandbox testing', 'Cloud migration',
             'Legacy software kept running safely.', CD, None),
        ],
            P('People run virtual machines for a few clear reasons. A sandbox lets you open a doubtful file safely. Test and development setups can be reset from a snapshot. An old business program can stay alive on an old system, away from the network. You can run another platform’s software, such as Windows on a Mac. To run them, switch on the processor’s virtualization feature in firmware. You also need enough RAM.'),
            P('A test kitchen lets cooks try risky recipes without ruining the restaurant. Make a mess and it is wiped back to clean. An old family '
              'recipe that needs an ancient oven gets its own corner where it cannot disturb anything. A virtual machine is that test kitchen: '
              'separate, resettable, and safe to experiment in.'),
            ['Why virtualize?', 'Sandbox, test, legacy or cross-platform?', 'Check UEFI extensions on.', 'Enough RAM and disk?', 'Create the VM.'],
            '<p>Sort each use case.</p>',
            sort('Use case', {'Sandbox': ['Open a suspicious file'], 'Test/dev': ['Reset from snapshot', 'Try an update first'], 'Legacy': ['Old app on old OS'],
                              'Cross-platform': ['Windows VM on a Mac']}, 'Each reason has its own setup.'), VM),
    },
    '6.3': {
        'core-content': X('Core content', 'IT-6.3', S3, [
            ('Guest says “no internet” but reaches the host. Switch type?', 'Internal', 'External to the LAN', 'Default Switch with NAT',
             'Internal switches reach the host and other VMs only.', VS, VS),
            ('Guest gets 169.254 on a private switch. Why?', 'No DHCP there', 'DNS is broken', 'The NIC is faulty',
             'Private switches have no DHCP server; the APIPA is expected.', VS, None),
            ('In the office-phone story, what is a private switch?', 'Room-only intercom', 'An outside line', 'A shared mobile phone',
             'It only connects VMs on that switch.', VS, None),
            ('Which switch lets a VM act like a normal LAN PC?', 'External', 'Private', 'Internal',
             'External bridges to the physical network.', VS, None),
            ('Default Switch on Windows 11 uses…', 'NAT on the host', 'A bridged LAN port', 'A VLAN trunk',
             'It works outward, but LAN devices cannot connect in.', VS, None),
        ],
            P('A virtual machine’s network card plugs into a virtual switch on the host, and the switch type decides what it can reach. External joins '
              'the real network and gets a normal lease. Internal reaches only the host and other VMs. Private reaches only VMs on that switch. The '
              'Default Switch goes out through NAT. Inside the guest, a 169.254 address on an internal or private switch is expected.'),
            P('Think of phones in an office. An external switch is an outside line: you can call anyone. An internal switch is the office extension '
              'system: you reach colleagues and reception but not the outside world. A private switch is an intercom between two rooms only. NAT is '
              'a switchboard that lets you ring out, but nobody outside can ring you directly.'),
            ['Check the VM’s switch type.', 'Is the adapter connected?', 'Run ipconfig in the guest.', 'Ping gateway, then name.', 'Hand host questions to the owner.'],
            '<p>Sort each symptom to the switch.</p>',
            sort('Switch type', {'External': ['Normal LAN lease'], 'Internal': ['Reaches host, no internet'], 'Private': ['Only other VMs', 'APIPA, no DHCP'],
                                 'Default Switch': ['Out via NAT, not reachable in']}, 'Switch type explains many “network” faults.'), VSW),
        '1-snapshots': X('1. Snapshots', 'IT-6.3', S3, [
            ('Is a snapshot a backup?', 'No', 'Yes, a full off-site copy', 'Yes, if it is a week old',
             'A snapshot sits next to the live disks on the same storage.', SB, SB),
            ('Week-old snapshot chains cause…', 'Slow guests, full datastore', 'Faster guests and more space', 'Nothing at all',
             'Chains grow and slow every guest on the datastore.', SK, SK),
            ('In the bookmark story, what is a snapshot?', 'A bookmark', 'A photocopy', 'A new book',
             'It marks a point beside the live pages, not a copy elsewhere.', SB, None),
            ('When do you take one?', 'Before a named change', 'Every hour on the hour', 'Never',
             'Take one before a change you can name.', SK, None),
            ('Reverting needs…', 'A ticket', 'Nothing', 'A reboot only',
             'Revert only with a ticket.', SK, None),
        ],
            P('Take a snapshot just before a change you can name. Revert to it only with a ticket. Delete or merge it once the change is done. A '
              'snapshot lives right next to the running disks, so it is not a copy kept somewhere safe. Old snapshot chains keep growing, fill the '
              'shared storage and make every virtual machine on it slower.'),
            P('A snapshot is a bookmark in a book you are still writing. It lets you flip back to page 40 if the next chapter goes badly. But it is '
              'not a photocopy kept in another house: if the book burns, the bookmark burns too. And a book stuffed with dozens of old bookmarks '
              'gets fat and awkward to use.'),
            ['Name the change.', 'Take the snapshot.', 'Make the change.', 'Revert only with a ticket.', 'Delete or consolidate.'],
            '<p>Put the snapshot steps in order.</p>',
            order('Snapshot life', ['Name the change', 'Take snapshot', 'Make the change', 'Delete or consolidate'], 'Snapshots are short-lived.'), VSW),
        'snapshots-and-virtual-cables': same_as('1-snapshots', 'Snapshots and virtual cables', 'Snapshots as bookmarks, plus vNIC checks.'),
    },
    '6.4': {
        'core-content': same_as('slow-vm-note', 'Core content', 'Guest evidence versus host questions in a full table.'),
        'slow-vm-note': X('Slow VM note', 'IT-6.3', S4, [
            ('What goes first in a slow VM note?', 'Guest facts', 'A guess about the host', 'The fix you plan to try',
             'Name and RAM the guest sees come first.', GF, GF),
            ('“Snapshot chain on host?” should be…', 'Labelled a guess', 'Written as a confirmed fact', 'Left out',
             'Host ideas you cannot see are guesses.', GF, None),
            ('In the weather story, why label a forecast?', 'It is not certain', 'It may be long', 'It is from a model',
             'Facts and guesses must be told apart.', GF, None),
            ('May you delete a host snapshot?', 'Not if not yours', 'Yes, any time', 'Yes, if it is old',
             'You do not delete snapshots you do not own.', SK, None),
            ('Host RAM pressure is evidence you…', 'Ask for', 'Collect yourself', 'Ignore',
             'Host evidence comes from the host owner.', HO, None),
        ],
            P('A slow virtual machine note starts with what you saw in the guest. Give its name, the memory it sees, disk space and errors. Anything about the host goes in marked as a guess. A long snapshot chain is one example. The host owner checks it. You never delete a '
              'snapshot that belongs to someone else.'),
            P('A weather report says what the thermometer reads now, and separately says “rain likely tomorrow.” Nobody confuses the two, because the '
              'forecast is labelled. Your note works the same way: measured guest facts, then clearly marked guesses about the host for the person who '
              'can actually check them and confirm or rule them out.'),
            ['Guest name and OS.', 'RAM and disk the guest sees.', 'Guest network tests.', 'Host ideas labelled as guesses.', 'Escalate to host owner.'],
            '<p>Sort each line.</p>',
            sort('Fact or guess?', {'Guest fact': ['RAM seen 8 GB', 'Disk C: 3% free', 'Name CIWT-W11-07'], 'Labelled guess': ['Snapshot chain on host?', 'Datastore full?']},
                 'Facts first, guesses labelled.'), VM),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '6.1': {'start-here-virtual-machines': '5ddf19b7d1a9', '1-two-machines-in-one-ticket': 'c2eca8a77a6c', '2-type-1-vs-type-2-only-what-you-need': 'b0e9769fb0f4'},
    '6.2': {'1-what-you-can-touch': 'ab9acd2132b7', '2-ticket-habit': '092d386ad58f', 'virtualization-use-cases-cloud-models-and-cloud-productivity': 'cc3b7bf5124b'},
    '6.3': {'core-content': '0ed10268d4ed', '1-snapshots': 'e6a3c8cd11dd'},
    '6.4': {'slow-vm-note': 'daf2e1722281'},
}

