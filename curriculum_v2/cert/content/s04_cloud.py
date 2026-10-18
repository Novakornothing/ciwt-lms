"""A+ Core 1 4.1/4.2 (virtualization and cloud concepts) and Core 2 1.11 (cloud productivity tools) — ITSUP 6.2."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-cloud', 'NIST cloud model: characteristics, service models and deployment models',
    ['5 characteristics:\nself-service, network,', 'pooling, elasticity,\nmeasured service', 'Service models:\nIaaS · PaaS · SaaS',
     'Deployment: private,\ncommunity, public, hybrid'],
    'Four boxes. NIST SP 800-145 defines cloud computing by five essential characteristics — on-demand self-service, broad '
    'network access, resource pooling, rapid elasticity and measured service — then three service models (infrastructure, '
    'platform and software as a service) and four deployment models (private, community, public and hybrid). A service '
    'is described by one service model and one deployment model, for example SaaS delivered from a public cloud.',
    'Any cloud service = the five characteristics + one service model + one deployment model (NIST SP 800-145).', cols=4)

HTML = f'''
<h4>Virtualization use cases (Core 1 4.1)</h4>
<p>Lesson 6.1 covered hypervisors: a <strong>type 1</strong> (bare-metal) hypervisor runs directly on the hardware; a
<strong>type 2</strong> (hosted) hypervisor runs as an application on a desktop OS. The exam also asks <em>why</em> you
virtualise: a <strong>sandbox</strong> to open a suspicious file safely; <strong>test and development</strong> environments
that can be reset from a snapshot; <strong>legacy software or OS</strong> support (an old line-of-business app in an old OS,
isolated from the network); and <strong>cross-platform</strong> work (a Windows VM on a Mac). <strong>Requirements</strong>
follow from that: CPU virtualization extensions enabled in UEFI, enough RAM and storage for host <em>plus</em> guests, and
network mode chosen deliberately.</p>
<p><strong>Containers</strong> package an application with its libraries but share the host’s kernel, so they start in
seconds and are small; a VM carries a whole guest OS. <strong>Application virtualization</strong> streams or isolates a
single app rather than a desktop. <strong>VDI (virtual desktop infrastructure)</strong> runs whole desktops on servers in
the data centre or cloud — Azure Virtual Desktop is one example — and users reach them from any device; the desktop, and
the data, never leave the data centre.</p>
{_FIG}
<h4>Cloud concepts (Core 1 4.2)</h4>
<ul>
<li><strong>Deployment models:</strong> <strong>public cloud</strong> (provider’s infrastructure, shared by many customers);
<strong>private cloud</strong> (one organisation’s exclusive use, on or off premises); <strong>community cloud</strong>
(shared by organisations with common requirements, such as a group of hospitals); <strong>hybrid cloud</strong> (two or more
of these, connected so data and apps can move between them).</li>
<li><strong>Service models:</strong> <strong>IaaS</strong> (you manage the OS and up — virtual machines, networks);
<strong>PaaS</strong> (you manage the application and data — the provider runs the platform); <strong>SaaS</strong> (you
manage users and data only — email, office suites).</li>
<li><strong>Characteristics:</strong> <strong>multitenancy</strong> (many customers on shared infrastructure, logically
isolated); <strong>shared vs. dedicated resources</strong> (dedicated hosts cost more but satisfy some compliance
rules); <strong>metered utilization</strong> (pay for what you use — including data leaving the cloud, “egress”);
<strong>rapid elasticity</strong> (capacity grows and shrinks with demand); <strong>availability</strong> (stated in the
provider’s service-level agreement); and <strong>file synchronization</strong> between devices and cloud storage.</li>
</ul>
<h4>Cloud productivity tools (Core 2 1.11)</h4>
<p>Most support desks now administer a SaaS suite such as Microsoft 365 or Google Workspace. The recurring tasks:</p>
<ul>
<li><strong>Licensing assignment</strong> — a user gets a mailbox, OneDrive and Office apps only when a licence that includes
them is assigned in the admin centre. A new starter with “no mailbox” usually has no licence yet.</li>
<li><strong>Email systems</strong> — mailbox, shared mailboxes and distribution groups are cloud objects; the client
(Outlook, phone mail app, browser) just connects to them.</li>
<li><strong>Storage and sync settings</strong> — sync clients such as OneDrive can redirect the Windows known folders
(Desktop, Documents, Pictures) so they are backed up to the cloud; check sync status before reimaging a PC.</li>
<li><strong>Collaboration tools</strong> — chat, videoconferencing, shared documents and spreadsheets with co-authoring;
permissions on the shared file decide who can edit.</li>
<li><strong>Identity synchronization</strong> — organisations with on-premises Active Directory sync accounts to the cloud
directory (Microsoft Entra Connect Sync runs a sync cycle every 30 minutes by default), so a password or group change
made on premises can take a sync cycle to appear in the cloud.</li>
</ul>
{worked('the new starter with no email', '''<ol>
<li>Ticket: “new starter can sign in to Teams on the web but Outlook says no mailbox”.</li>
<li>Admin centre → user → Licences: none assigned. Sign-in works because the account exists; the mailbox needs a licence that includes Exchange Online.</li>
<li>Assign the licence the role requires (per the onboarding checklist), wait for provisioning, and retest in Outlook on the web first.</li>
<li>Document; feed back to HR onboarding so licences are assigned before the start date.</li></ol>''')}
{scenario('the laptop rebuild', '''<p>A user’s laptop must be reimaged. Before wiping, you confirm in the OneDrive client that Desktop and
Documents are redirected and show “up to date”, and you check for files outside those folders. After the rebuild,
the user signs in, OneDrive restores the known folders, and nothing is copied by hand. If sync had shown errors, you would
fix them — or back up locally — <em>before</em> wiping.</p>''')}
{cfu(('A container and a VM both run an app in isolation. What is the key difference?', 'A container shares the host kernel; a VM runs its own complete guest OS.'),
     ('Which service model leaves you responsible only for users and data?', 'SaaS.'),
     ('A password changed on premises still fails in the cloud ten minutes later. What is the likely reason?', 'Identity sync has not run yet — the change appears after the next sync cycle.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 6, 'lesson': 2, 'id': 'cert-cloud',
    'title': 'Virtualization use cases, cloud models and cloud productivity administration',
    'cert': ['A1:4.1', 'A1:4.2', 'A2:1.11'],
    'html': sme_note('Virtualization use cases, NIST cloud models and cloud productivity administration (Core 1 4.1/4.2, Core 2 1.11).') + HTML,
    'sources': ['nist-800145', 'ms-avd', 'ms-m365-licences', 'ms-onedrive-kfm'],
}]

GLOSSARY = [
    ('Community cloud', 'Cloud infrastructure shared by organisations with common requirements (NIST SP 800-145).'),
    ('Multitenancy', 'Many customers share the same cloud infrastructure while their data and configuration stay logically isolated.'),
    ('Metered utilization', 'Paying for cloud resources by measured use (compute time, storage, data egress).'),
    ('VDI', 'Virtual desktop infrastructure: complete desktops run on central servers and are accessed remotely.'),
    ('Container', 'Packaged application and libraries that share the host OS kernel; lighter than a virtual machine.'),
    ('Identity synchronization', 'Copying user accounts and attributes from an on-premises directory to a cloud directory on a schedule.'),
]

ITEMS = [
    single('A1:4.1', 'IT-6.1', 1, 'An analyst must open a suspicious attachment safely and then discard everything it changed. Which approach fits best?',
           'A sandboxed VM reverted to a snapshot afterwards',
           ['A container that shares the analyst’s host kernel', 'A second user account on the analyst’s laptop', 'A type 2 hypervisor with a bridged network adapter'],
           'A sandbox VM isolates the file; reverting the snapshot discards every change. Sharing a kernel or bridging to the LAN weakens isolation.'),
    multi('A1:4.1', 'IT-6.1', 2, 'Which TWO statements about containers are correct? (Choose two.)',
          ['They share the host operating system’s kernel', 'They package an application with its libraries'],
          ['They each include a full guest operating system', 'They need a type 1 hypervisor to run', 'They cannot run on a cloud platform'],
          'Containers share the host kernel and bundle the app’s dependencies; that is why they are smaller than VMs.'),
    single('A1:4.1', 'IT-6.3', 3, 'Staff need the same managed Windows desktop from home PCs, tablets and thin clients, with no company data stored on those devices. What fits best?',
           'Virtual desktop infrastructure (VDI)',
           ['A type 2 hypervisor on each home PC', 'Application containers on the tablets', 'A local VM copied to each device weekly'],
           'VDI runs the desktop centrally; endpoints only display it, so data stays in the data centre.'),
    match('A1:4.2', 'IT-6.2', 1, 'Match each description to the cloud deployment model.',
          [('A group of regional hospitals shares one compliant platform', 'Community cloud'),
           ('One company runs a cloud platform for its own exclusive use', 'Private cloud'),
           ('Thousands of unrelated customers share a provider’s platform', 'Public cloud'),
           ('On-premises systems linked to a provider for overflow capacity', 'Hybrid cloud')],
          'NIST SP 800-145 deployment models: community, private, public and hybrid.',
          decoys=['Multitenant SaaS']),
    single('A1:4.2', 'IT-6.2', 2, 'A web shop’s cloud servers scale out automatically for a sale and back in afterwards, and the bill reflects the extra hours. Which TWO characteristics does this show?',
           'Rapid elasticity and metered (measured) service',
           ['Multitenancy and a dedicated host', 'Broad network access and a private cloud', 'Resource pooling and a community cloud'],
           'Scaling with demand is elasticity; paying for the hours used is measured service.'),
    single('A2:1.11', 'IT-6.2', 1, 'A new starter can sign in to the cloud portal but has no mailbox. What should the technician check first?',
           'Whether a licence that includes email is assigned',
           ['Whether the user’s password has expired', 'Whether the Outlook profile is corrupted', 'Whether the PC is joined to the domain'],
           'The account exists (sign-in works); the mailbox is provisioned only when an appropriate licence is assigned.'),
    single('A2:1.11', 'IT-6.2', 2, 'An on-premises AD password reset is not yet working for cloud sign-in a few minutes later. Everything else is normal. What is the most likely reason?',
           'The next identity synchronization cycle has not run',
           ['The cloud tenant has run out of licences', 'The user’s mailbox is over its quota', 'OneDrive Known Folder Move is turned off'],
           'Directory sync runs on a schedule (Entra Connect Sync: every 30 minutes by default).'),
    order('A2:1.11', 'IT-6.2', 3, 'Put the steps for reimaging a laptop whose user relies on OneDrive known-folder sync in a safe order.',
          ['Confirm Desktop and Documents show as synced', 'Check for files outside the synced folders', 'Reimage the laptop',
           'Have the user sign in to OneDrive', 'Verify the known folders have restored'],
          'Confirm sync and back up anything outside it before the destructive step; verify after the restore.'),
]
