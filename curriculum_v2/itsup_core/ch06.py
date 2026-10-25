"""ITSUP Chapter 6 — Virtualization & Cloud Concepts (pass 10 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 6
SOURCES_USED = ['nist-800125', 'ms-hyperv', 'nist-800145', 'ms-shared', 'ms-servicehealth']

_NOTE = 'Core content added in pass 10.'

LESSONS = {
    (6, 1): {
        'objectives': [
            'Distinguish type 1 and type 2 hypervisors and say which one a given setup uses',
            'Determine whether a Windows PC is a virtual machine guest, and whether a host has virtualization enabled',
            'Identify the hardware and edition requirements for running Hyper-V on Windows 11',
            'Compare a virtual machine with a container by what each one shares with the host',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Host, guest and the layer between</h3>
<p>A <strong>hypervisor</strong> lets one physical computer (the <strong>host</strong>) run several <strong>virtual machines</strong>
(guests), each with its own virtual CPU, memory, disks and network adapters. NIST SP 800-125 describes two kinds:</p>
''' + table(['Type', 'Runs on', 'Examples', 'Where you meet it'], [
            ['Type 1 (bare-metal)', 'Directly on the hardware', 'Hyper-V, VMware ESXi, KVM', 'Server rooms and data centres; also Hyper-V on a Windows 11 Pro PC'],
            ['Type 2 (hosted)', 'As an application on a desktop OS', 'VMware Workstation, Oracle VirtualBox', 'A technician’s laptop running a lab VM'],
        ]) + '''
<p>Hyper-V surprises people: once the feature is turned on, the hypervisor loads first and the Windows you log in to becomes its
privileged “root” partition. It is a type 1 hypervisor even on a desktop. That is also why some type 2 products behave differently
on a PC where Hyper-V (or a feature that uses it, such as Windows Sandbox or WSL 2) is enabled.</p>
<h3>Is this PC a guest? Is this host ready?</h3>
''' + table(['Question', 'Where to look', 'What you see'], [
            ['Am I inside a VM?', 'Task Manager → Performance → CPU', '“Virtual machine: Yes” (and no Virtualization line)'],
            ['Am I inside a VM?', 'System Information (msinfo32) or systeminfo', 'System model such as “Virtual Machine” and a hypervisor vendor as manufacturer'],
            ['Can this host run VMs?', 'Task Manager → Performance → CPU', '“Virtualization: Enabled” — if Disabled, it is off in firmware (UEFI) settings'],
            ['Is Hyper-V available?', 'Windows edition', 'Windows 11 Pro, Enterprise or Education; not Home'],
        ]) + '''
<p>Hyper-V needs a 64-bit processor with hardware virtualization (Intel VT-x or AMD-V) and second-level address translation (SLAT),
virtualization enabled in firmware, and at least 4 GB of RAM. In a ticket, the edition and the “Virtualization” line answer most
“Hyper-V won’t install” questions before anyone touches the BIOS.</p>
<h3>VMs and containers</h3>
<p>A VM carries a complete operating system with its own kernel; a <strong>container</strong> packages an application and its
libraries and shares the host’s kernel. Containers start in seconds and use less memory; VMs isolate more strongly and can run a different
operating system from the host. Desktop support mostly meets containers as “the developer’s Docker won’t start”, which usually leads
back to the same virtualization checks.</p>
''' + worked('“Hyper-V is missing”', '''
<p>Ticket: “I can’t turn on Hyper-V for the training VM.” Settings → System → About shows Windows 11 Home. Task Manager shows
“Virtualization: Enabled”. The hardware is ready; the edition is not. Note: “Win 11 Home — Hyper-V not available on Home. CPU virtualization
enabled. Options for the owner: upgrade edition (licence request) or use the shop’s approved type 2 hypervisor. No firmware changes made.”</p>''') + cfu(
            ('Is Hyper-V on a Windows 11 Pro laptop type 1 or type 2?',
             'Type 1: the hypervisor runs below Windows, which becomes the root partition.'),
            ('Task Manager shows “Virtualization: Disabled”. Where is it turned on?',
             'In the firmware (UEFI/BIOS) settings — under shop change rules, since it is a firmware change.'),
            ('What does a container share with its host that a VM does not?',
             'The operating system kernel.')),
        'sources': ['nist-800125', 'ms-hyperv'],
    },
    (6, 2): {
        'objectives': [
            'Compare SaaS, PaaS and IaaS by what the customer manages and what the provider manages',
            'Explain the NIST essential characteristics and deployment models of cloud computing',
            'Determine whether a fault is a provider outage using scope and the provider’s service health page',
            'Route a cloud ticket to the right owner without exposing tenant credentials',
        ],
        'html': sme_note(_NOTE) + '''
<h3>What makes something “cloud”</h3>
<p>NIST SP 800-145 defines cloud computing by five <strong>essential characteristics</strong>: on-demand self-service, broad network
access, resource pooling, rapid elasticity and measured service. It names three <strong>service models</strong> and four
<strong>deployment models</strong> (private, community, public and hybrid). A server in a cupboard that someone reaches over the internet is
not cloud by this definition; a self-service, metered, pooled service is.</p>
<h3>Shared responsibility</h3>
''' + table(['Layer', 'On-premises', 'IaaS', 'PaaS', 'SaaS'], [
            ['Data, accounts and identities', 'You', 'You', 'You', 'You'],
            ['Devices (endpoints)', 'You', 'You', 'You', 'You'],
            ['Application', 'You', 'You', 'You (your code)', 'Provider'],
            ['Operating system', 'You', 'You (guest OS)', 'Provider', 'Provider'],
            ['Virtualization, hardware, network, data centre', 'You', 'Provider', 'Provider', 'Provider'],
        ]) + '''
<p>Microsoft’s shared-responsibility guidance makes the point that matters most for support: whatever the model, <strong>your
data, your endpoints and your accounts and identities remain yours</strong>. A SaaS provider will not recover a mailbox someone deleted
past the retention period, and cannot stop a user giving their password to a phishing page.</p>
<h3>Is it them or us?</h3>
<p>For a SaaS problem, scope and the provider’s status decide the route. In Microsoft 365, administrators check
<strong>Service health</strong> in the Microsoft 365 admin center, which lists active incidents and advisories per service; other
providers publish a status page. If many users across sites fail the same way and the provider lists an incident, the fix is the
provider’s: record the incident ID, tell users, and stop changing PCs. If one user fails and the service is healthy, work the user’s
account, licence and client.</p>
''' + figure('f6-2', 'SaaS ticket: provider or local?', ['One user or\nmany?', 'Service health:\nincident?', 'Provider\nincident:\nrecord + inform', 'Account,\nlicence,\nclient', 'Network path\n(Chapter 5)'],
             'Five boxes. First ask whether one user or many are affected. Then check the provider’s service health. If the provider lists an incident '
             'that matches, record its ID and inform users rather than changing devices. If only one user is affected and the service is healthy, check '
             'that user’s account, licence and app; if a whole site fails while service health is clean, check the site’s network path with the Chapter 5 order.',
             'Scope plus the provider’s service health decide whether you fix something or follow an incident.', cols=5) + scenario('the yellow icon', '''
<p>At 08:40 the help desk receives twelve calls: Outlook will not connect, at three different sites. One technician has already started
recreating a user’s mail profile. The team lead checks Service health: Exchange Online shows an incident, “users may be unable to connect
using Outlook desktop”. The profile work stops. The lead posts the incident ID to the team, sends users a short notice suggesting Outlook on
the web if the incident says it is unaffected, and links each ticket to the incident. When Microsoft marks it resolved, the team confirms with
two of the users and closes the tickets. No PC was changed.</p>''') + cfu(
            ('In IaaS, who patches the guest operating system?',
             'The customer: in IaaS you manage the guest OS and everything above it.'),
            ('Name the five NIST essential characteristics.',
             'On-demand self-service, broad network access, resource pooling, rapid elasticity, measured service.'),
            ('Many users at several sites cannot open SaaS mail. What do you check before touching a PC?',
             'The provider’s service health/status page for an active incident.')),
        'sources': ['nist-800145', 'ms-shared', 'ms-servicehealth'],
    },
    (6, 3): {
        'objectives': [
            'Explain how Hyper-V virtual switch types (external, internal, private, Default Switch) decide what a VM can reach',
            'Compare standard and production checkpoints and explain why a checkpoint is not a backup',
            'Troubleshoot a guest with no network or a paused state and route host issues to the host owner',
            'Diagnose a slow or stopped VM by separating guest evidence from host evidence',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Virtual switches</h3>
<p>A VM’s network adapter plugs into a <strong>virtual switch</strong> on the host. In Hyper-V the switch type decides what the VM can
reach:</p>
''' + table(['Switch type', 'VM can reach', 'Typical symptom when it is the wrong choice'], [
            ['External', 'The physical network through a host adapter', 'Works like a normal PC on the LAN; gets a lease from the LAN’s DHCP'],
            ['Internal', 'Other VMs and the host only', '“No internet” in the guest, but the host is reachable'],
            ['Private', 'Other VMs on the same switch only', 'Cannot reach the host or the LAN at all'],
            ['Default Switch', 'The network through NAT on the host (created automatically on Windows 10/11)', 'Works, but other LAN devices cannot connect in to the VM'],
        ]) + '''
<p>Inside the guest, use the Chapter 5 order: a guest with 169.254 on an internal or private switch has no DHCP server to ask — that is
the design, not a broken guest. A guest whose virtual adapter is disconnected in the VM’s settings shows a disconnected cable, exactly like
an unplugged patch lead.</p>
<h3>Checkpoints (snapshots)</h3>
<p>A <strong>checkpoint</strong> records a VM’s state so you can return to it. Hyper-V offers two kinds:</p>
''' + table(['Checkpoint', 'Captures', 'Use for'], [
            ['Standard', 'Disk and memory state, including running applications', 'Lab work and testing where returning to the exact running state helps'],
            ['Production (the default)', 'A disk state made consistent inside the guest (VSS on Windows); no memory state', 'Servers and anything with databases or services'],
        ]) + '''
<p>Each checkpoint starts a new differencing disk (<code>.avhdx</code>) that records changes from that point; deleting the checkpoint in
Hyper-V Manager merges it back. Two habits follow. A <strong>checkpoint is not a backup</strong>: it lives on the same storage as the VM and
depends on it, so a failed disk or ransomware on the host takes both. And <strong>checkpoints are temporary</strong>: a long chain grows
without limit and slows the VM. Never delete <code>.avhdx</code> files by hand — that breaks the chain; remove checkpoints through the
hypervisor, and only for VMs you own.</p>
''' + figure('f6-3', 'Checkpoint chain on the host disk', ['Base disk\n(.vhdx)', 'Checkpoint 1\n(.avhdx)', 'Checkpoint 2\n(.avhdx)', 'Running VM\nwrites here', 'Host disk\nfills up'],
             'Five boxes in a row. The base virtual disk is followed by one differencing disk per checkpoint; the running VM writes only to the newest one. '
             'Every file sits on the same host disk, so the chain keeps growing, and a failure of that disk loses the VM and every checkpoint together.',
             'A checkpoint is a chain of files on the same disk as the VM, which is why it is neither permanent nor a backup.', cols=5) + '''
<h3>When the host is the problem</h3>
<p>If the host volume holding a VM’s disks runs critically low on space, Hyper-V pauses the VM and shows it as <strong>Paused-Critical</strong>
rather than let the disk fill. Restarting the guest does nothing; the host owner must free space (often by merging old checkpoints) before
resuming it. In the same way, five guests that lose the network together point at the shared virtual switch or the host’s uplink, not at five
guest NICs.</p>
''' + worked('slow since Tuesday', '''
<p>Ticket: “NOVAK-W11-07 has been slow since Tuesday.” Inside the guest: 8 GB RAM visible, 35 % used, disk 40 % free, no runaway process.
The guest looks healthy. The VM’s settings (read-only view the shop allows) list four checkpoints, the oldest from Tuesday’s update. Note:
“Guest: RAM 35 %, disk 40 % free, no high CPU. Guess (unconfirmed): checkpoint chain of 4 since Tue on host. Asked host owner to review and merge
checkpoints. No checkpoints deleted.”</p>''') + cfu(
            ('A guest on an internal switch has 169.254 and “no internet”. Is the guest broken?',
             'No. An internal switch reaches only the host and other VMs and normally has no DHCP; the switch choice is the cause.'),
            ('Why is a checkpoint not a backup?',
             'It depends on the VM’s own disks on the same storage; lose that storage and you lose the VM and its checkpoints.'),
            ('A VM shows Paused-Critical. Who fixes it?',
             'The host owner: the host volume holding the VM’s disks is nearly full and needs space before the VM can resume.')),
        'sources': ['ms-hyperv'],
    },
    (6, 4): {
        'objectives': [
            'Collect guest-side evidence before raising a host or cloud question',
            'Write a note that separates confirmed guest facts from labelled guesses about the host',
            'Route the ticket to the host, hypervisor or cloud-provider owner with that evidence',
        ],
        'html': sme_note(_NOTE) + '''
<h3>Capstone: a slow or unreachable VM</h3>
<p>The same Chapter 1 standard applies inside a virtual machine: name the outcome, collect evidence, change one thing you own, and write
action → result. What is new is the boundary. The guest is yours to inventory; the host, the virtual switch, the checkpoints and the cloud
tenant usually belong to someone else.</p>
''' + table(['Evidence', 'Guest (you collect)', 'Host or provider (you ask)'], [
            ['Identity', 'Computer name, OS, “Virtual machine: Yes”', 'Which host or cluster, which VM name'],
            ['Resources', 'RAM and CPU use in Task Manager; free disk', 'Host RAM/CPU pressure; datastore free space'],
            ['Network', 'ipconfig, ping gateway, nslookup', 'Switch type, adapter connected, host uplink'],
            ['State', 'Event Viewer errors in the guest', 'Checkpoint chain, Paused-Critical, backup jobs'],
            ['Cloud', 'Error text, time, tenant name', 'Service health incident, subscription limits'],
        ]) + worked('guest facts, then the ask', '''
<p>“NOVAK-W11-07 (VM). Guest: 8 GB, RAM 35 %, CPU &lt; 10 % idle, C: 40 % free; ipconfig 10.20.30.47 gw OK. Slow opening files since Tue.
<em>Guess:</em> checkpoint chain on host (4 checkpoints seen, oldest Tue). Ask to host owner: review/merge checkpoints, check datastore space.
Nothing changed in the guest; no checkpoints touched.”</p>''') + '''
<h3>Pass bar</h3>
<ul>
<li>Guest facts come first and each one has a value, not an adjective.</li>
<li>Anything about the host is labelled <em>guess</em> until the owner confirms it.</li>
<li>Nobody deleted, reverted or merged a checkpoint they do not own; nobody reimaged a guest because the host was full.</li>
</ul>
''' + cfu(
            ('Why is “checkpoint chain on host” labelled a guess in the note?',
             'The technician cannot confirm it from inside the guest; the host owner must check before anyone acts on it.'),
            ('Five guests on one host lose the network at once. What goes in the ask?',
             'The shared virtual switch and the host’s uplink, with each guest’s ipconfig and ping results as evidence.')),
        'sources': ['ms-hyperv', 'ms-servicehealth'],
    },
}

GLOSSARY = [
    ('Type 1 hypervisor', 'A hypervisor that runs directly on the hardware (bare-metal), such as Hyper-V, ESXi or KVM.'),
    ('Type 2 hypervisor', 'A hypervisor that runs as an application on a desktop operating system, such as VMware Workstation or VirtualBox.'),
    ('Root partition', 'In Hyper-V, the privileged Windows instance that manages the hypervisor and the guest VMs.'),
    ('SLAT', 'Second-level address translation (Intel EPT, AMD RVI): processor support Hyper-V requires for efficient VM memory.'),
    ('Container', 'A packaged application with its libraries that shares the host’s kernel, unlike a VM with its own OS.'),
    ('Resource pooling', 'A NIST cloud characteristic: the provider serves many customers from shared, dynamically assigned resources.'),
    ('Rapid elasticity', 'A NIST cloud characteristic: capacity can grow and shrink quickly, often automatically, with demand.'),
    ('Shared responsibility', 'The split of security and operations duties between a cloud provider and the customer, which varies by service model.'),
    ('Service health', 'The Microsoft 365 admin center page listing active incidents and advisories for each cloud service.'),
    ('External virtual switch', 'A Hyper-V switch bound to a physical adapter, giving VMs access to the physical network.'),
    ('Default Switch', 'The Hyper-V switch Windows creates automatically, giving VMs outbound access through NAT on the host.'),
    ('Production checkpoint', 'A Hyper-V checkpoint made consistent inside the guest (VSS) without memory state; the default type.'),
    ('Differencing disk', 'A virtual disk file (.avhdx in Hyper-V) that records changes relative to a parent disk; checkpoints create them.'),
    ('Paused-Critical', 'A Hyper-V VM state set when the host volume holding the VM’s disks is critically low on space.'),
]

PLAN = {
    'warmup': 'Ask: “Is the Windows you are typing in right now a computer?” Open Task Manager → CPU and look for “Virtual machine: Yes”.',
    'guided': 'Fill the type 1/type 2 table and run the guest checks (6.1); build the shared-responsibility table on the board (6.2); match four switch types to four symptoms and draw a checkpoint chain (6.3).',
    'worked_example': 'Lesson 6.1 “Hyper-V is missing”; 6.3 slow since Tuesday; 6.4 guest facts, then the ask.',
    'cfu': ['Hyper-V on Windows 11 Pro: type 1 or 2?',
            'IaaS: who patches the guest OS?',
            'Guest on an internal switch has 169.254: broken?',
            'Why is a checkpoint not a backup?'],
    'exit_ticket': 'Write the guest-facts line and the labelled host guess for a VM that is slow after a weekend of updates.',
    'misconceptions_add': ['“Checkpoints are backups.” They depend on the VM’s own storage and grow until merged.',
                           '“SaaS means the provider protects our data.” Data, accounts and endpoints stay with the customer.',
                           '“The VM has no internet, so reinstall the guest.” Check the switch type and adapter first.'],
    'classroom_lab': '',
    'materials_add': 'A bench VM (or screenshots) showing Task Manager in a guest and on a host; a printed checkpoint tree; a sample Service health incident page.',
}

ITEMS = [
    item('IT-6.1', 1, 'Hyper-V is enabled on a Windows 11 Pro laptop. Which type of hypervisor is it?',
         'Type 1, running beneath Windows', ['Type 2, running as a Windows app', 'A container runtime on Windows', 'A cloud PaaS service from Microsoft'],
         'Hyper-V loads first and Windows becomes its root partition, so it is type 1 even on a desktop.'),
    item('IT-6.1', 2, 'Task Manager shows “Virtualization: Disabled” on a host PC. Where is it turned on?',
         'In the UEFI firmware settings', ['In Windows Update settings', 'In Device Manager’s CPU entry', 'In the Hyper-V Manager console'],
         'Hardware virtualization (VT-x/AMD-V) is enabled in firmware, as a controlled change.'),
    item('IT-6.1', 3, 'What does a container share with its host that a virtual machine does not?',
         'The host’s operating system kernel', ['The host’s physical network cables', 'The host’s user accounts and passwords', 'The host’s firmware boot settings'],
         'Containers share the host kernel; each VM runs its own complete operating system.'),
    item('IT-6.2', 1, 'In IaaS, who is responsible for patching the guest operating system?',
         'The cloud customer', ['The cloud provider', 'The internet provider', 'The hardware maker'],
         'In IaaS the provider runs the hardware and virtualization; the guest OS and above belong to the customer.'),
    item('IT-6.2', 2, 'Users at three sites cannot connect to SaaS mail. What should be checked first?',
         'The provider’s service health page', ['Each user’s local Outlook profile', 'The DNS cache on every user’s PC', 'The firmware version on each laptop'],
         'Many users across sites suggests a provider incident; service health confirms it before anyone changes PCs.'),
    item('IT-6.2', 3, 'Which of these is one of the NIST essential characteristics of cloud computing?',
         'Measured service', ['Fixed capacity', 'Single tenancy', 'Manual provisioning'],
         'NIST lists on-demand self-service, broad network access, resource pooling, rapid elasticity and measured service.'),
    item('IT-6.3', 1, 'A VM on a Hyper-V internal switch has a 169.254 address. What is the most likely cause?',
         'The switch has no DHCP or LAN access', ['The guest’s network driver is corrupted', 'The guest OS needs a full reinstall', 'The DNS server’s record is missing'],
         'An internal switch reaches only the host and other VMs; with no DHCP there, the guest falls back to APIPA.'),
    item('IT-6.3', 2, 'Why is a VM checkpoint not a substitute for a backup?',
         'It depends on the VM’s own storage', ['It cannot be reverted after a day', 'It only saves the VM’s settings', 'It is deleted whenever the VM restarts'],
         'Checkpoints are differencing disks on the same storage as the VM; losing that storage loses both.'),
    item('IT-6.3', 3, 'A VM shows Paused-Critical in Hyper-V Manager. What is the most likely cause?',
         'The host volume is almost out of space', ['The guest’s Windows licence has expired', 'The user locked the guest’s screen', 'The guest’s DNS settings are wrong'],
         'Hyper-V pauses a VM when the volume holding its disks is critically low on space; the host owner must free space.'),
]
