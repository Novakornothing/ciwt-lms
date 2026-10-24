"""A+ Core 2 1.4 (Windows tools) and 1.6 (Windows settings) — ITSUP 11.3 and 13.5."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_TOOLS = figure(
    'fig-c-wintools', 'Which Windows tool answers which question',
    ['Is it running?\nTask Manager', 'What happened?\nEvent Viewer', 'Is the hardware seen?\nDevice Manager', 'Disks and volumes?\nDisk Management', 'Runs on a schedule?\nTask Scheduler'],
    'Five boxes, each pairing a support question with the tool that answers it. Is a program or service running and what is it '
    'using? Task Manager (and Resource Monitor for detail). What happened, and when? Event Viewer. Does Windows see the hardware '
    'and its driver? Device Manager. What disks, partitions and volumes exist? Disk Management. Does something run at logon or '
    'on a timer? Task Scheduler and the Startup apps page.',
    'Start from the question, then pick the tool; each console is an .msc snap-in you can launch from Run.', cols=5)

HTML_TOOLS = ('\n<p>Core 2 1.4 lists the built-in Windows tools a technician must be able to use. Most are Microsoft Management Console\n(MMC) snap-ins: type the <code>.msc</code> name in Run (<kbd>Win</kbd>+<kbd>R</kbd>) or find them in <strong>Windows Tools</strong>\n(called Administrative Tools before Windows 11).</p>\n<table class="ref-table"><thead><tr><th scope="col">Tool</th><th scope="col">Launch</th><th scope="col">Use it to…</th></tr></thead><tbody>\n<tr><td>Task Manager</td><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Esc</kbd></td><td>See <strong>processes</strong> and end a hung one; check <strong>performance</strong> (CPU, memory, disk, network, GPU); enable or disable <strong>startup</strong> apps; see signed-in <strong>users</strong> (Users page); start and stop <strong>services</strong>.</td></tr>\n<tr><td>Event Viewer</td><td><code>eventvwr.msc</code></td><td>Read the System, Application and Security logs.</td></tr>\n<tr><td>Disk Management</td><td><code>diskmgmt.msc</code></td><td>Initialise disks; create, extend, shrink and format volumes; assign drive letters.</td></tr>\n<tr><td>Task Scheduler</td><td><code>taskschd.msc</code></td><td>Run a program at a time, at logon or on an event.</td></tr>\n<tr><td>Device Manager</td><td><code>devmgmt.msc</code></td><td>Update, roll back or disable drivers; find devices with a warning icon.</td></tr>\n<tr><td>Certificate Manager</td><td><code>certmgr.msc</code></td><td>View and import the current user’s certificates.</td></tr>\n<tr><td>Local Users and Groups</td><td><code>lusrmgr.msc</code></td><td>Create local accounts and set group membership (not in Windows Home).</td></tr>\n<tr><td>Performance Monitor</td><td><code>perfmon.msc</code></td><td>Record counters over time and build data-collector reports.</td></tr>\n<tr><td>Group Policy Editor</td><td><code>gpedit.msc</code></td><td>Set local policy (not in Windows Home).</td></tr>\n<tr><td>System Information</td><td><code>msinfo32</code></td><td>Hardware, firmware (BIOS/UEFI mode) and OS details in one report.</td></tr>\n<tr><td>Resource Monitor</td><td><code>resmon</code></td><td>Which process is using the disk, the network or a file handle.</td></tr>\n<tr><td>System Configuration</td><td><code>msconfig</code></td><td>Boot options such as safe boot, and a selective startup for troubleshooting.</td></tr>\n<tr><td>Disk Cleanup</td><td><code>cleanmgr</code></td><td>Remove temporary files and old update files.</td></tr>\n<tr><td>Defragment and Optimize Drives</td><td><code>dfrgui</code></td><td>Defragment hard drives; send TRIM to SSDs (Windows does not defragment SSDs as it does HDDs).</td></tr>\n<tr><td>Registry Editor</td><td><code>regedit</code></td><td>Edit the registry. Back up the key first (File → Export); a wrong change can stop Windows starting.</td></tr>\n</tbody></table>\n' + str(_FIG_TOOLS) + '\n' + str(worked('a PC that is slow for the first ten minutes', '''<ol>
<li>Task Manager → Performance shows disk at 100% just after sign-in. Processes, sorted by Disk, shows a cloud-sync client and a vendor updater.</li>
<li>Startup apps page: the vendor updater is enabled with “High” impact. Disable it there (it can still be run by hand).</li>
<li>Task Scheduler: the same updater also has a task “At log on”. Disable the task after checking with the vendor’s documentation.</li>
<li>Event Viewer → System: no disk errors, so the drive is not failing.</li>
<li>Restart and re-check Performance: disk activity settles within two minutes. Record both changes on the ticket.</li></ol>''')) + '\n' + str(scenario('the certificate the browser would not trust', '''<p>An internal web app shows a certificate warning on one PC only. Certificate Manager (<code>certmgr.msc</code>)
shows that the company’s internal root certificate is missing from that user’s Trusted Root Certification Authorities store,
because the PC was set up before it joined the domain. Re-applying the policy (<code>gpupdate /force</code>) installs it; the
technician does not tell the user to click through the warning.</p>''')) + '\n' + str(cfu(('Which Task Manager page shows other people signed in to the same PC?', 'The Users page.'),
     ('Which tool shows which process is holding a file open?', 'Resource Monitor (resmon), CPU tab → Associated Handles.'),
     ('Why are lusrmgr.msc and gpedit.msc missing on some PCs?', 'They are not included in Windows Home.'))) + '\n')

_FIG_SET = figure(
    'fig-c-winsettings', 'Settings app and Control Panel: where things live',
    ['Settings: System,\nDevices, Network', 'Settings: Accounts,\nTime, Privacy', 'Control Panel:\nPower Options', 'Control Panel:\nFile Explorer Options', 'Windows Tools'],
    'Five boxes. The Settings app holds most day-to-day settings: System (display, sound, power, storage), Bluetooth & devices, '
    'Network & internet, Personalization, Apps, Accounts, Time & language, Gaming, Accessibility, Privacy & security and Windows '
    'Update. Control Panel still holds older applets such as Power Options (power plans, lid and power-button actions, fast '
    'startup, USB selective suspend), File Explorer Options (hidden files and file name extensions), Indexing Options, Mail, '
    'Internet Options, User Accounts, Devices and Printers, Network and Sharing Center and Windows Defender Firewall. Windows Tools '
    'links to the management consoles.',
    'Learn both: the exam names Control Panel applets and Settings pages, and Windows still uses both.', cols=5)

HTML_SET = ('\n<p>Core 2 1.6 asks you to configure Windows through both the <strong>Settings</strong> app and <strong>Control Panel</strong>.</p>\n<h4>Control Panel applets</h4>\n<ul>\n<li><strong>Internet Options</strong> — proxy, security zones and trusted sites for older apps that use them.</li>\n<li><strong>Devices and Printers</strong> — default printer, printing preferences, device properties.</li>\n<li><strong>Programs and Features</strong> — uninstall or repair desktop programs; turn Windows features on or off.</li>\n<li><strong>Network and Sharing Center</strong> — network profile, adapter settings, sharing options.</li>\n<li><strong>Windows Defender Firewall</strong> — allow an app, or open Advanced settings for inbound and outbound rules.</li>\n<li><strong>Mail</strong> — Outlook (classic) profiles: create a new profile when one is corrupt.</li>\n<li><strong>Sound</strong> — default playback and recording devices.</li>\n<li><strong>User Accounts</strong> — account type, credential manager.</li>\n<li><strong>Device Manager</strong> and <strong>Windows Tools</strong> (Administrative Tools).</li>\n<li><strong>Indexing Options</strong> — which locations Windows Search indexes; rebuild the index when search misses files.</li>\n<li><strong>File Explorer Options</strong> — show hidden files and folders; turn off “Hide extensions for known file types”, so\n<code>invoice.pdf.exe</code> cannot pass for a PDF.</li>\n<li><strong>Power Options</strong> — power plans; what closing the <strong>lid</strong> or pressing the power button does;\n<strong>sleep</strong> (standby: low power, state kept in RAM) versus <strong>hibernate</strong> (state written to disk, no power\nused); <strong>fast startup</strong> (shutdown saves the kernel session to disk, so it is not a full restart — choose Restart when\ntroubleshooting); <strong>USB selective suspend</strong> (lets Windows power down idle USB devices; turn it off when a USB device\nkeeps dropping out).</li>\n<li><strong>Ease of Access</strong> — now the <strong>Accessibility</strong> page in Settings.</li>\n</ul>\n<h4>Settings app pages</h4>\n<p><strong>System</strong>, <strong>Bluetooth &amp; devices</strong>, <strong>Network &amp; internet</strong>, <strong>Personalization</strong>,\n<strong>Apps</strong> (installed apps, default apps, startup), <strong>Accounts</strong>, <strong>Time &amp; language</strong> (time zone\nand sync — a wrong clock breaks certificates and Kerberos sign-in), <strong>Gaming</strong>, <strong>Accessibility</strong>,\n<strong>Privacy &amp; security</strong> (app permissions for camera, microphone and location) and <strong>Windows Update</strong>\n(called Update and Security in Windows 10).</p>\n' + str(_FIG_SET) + '\n' + str(worked('a laptop that “dies” in the bag', '''<ol>
<li>User closes the lid and puts the laptop in a bag; an hour later it is hot and the battery is flat.</li>
<li>Control Panel → Power Options → “Choose what closing the lid does”: On battery, “When I close the lid” is set to “Do nothing”.</li>
<li>Set it to Sleep (or Hibernate for long trips) on battery and plugged in; save changes.</li>
<li>Test: close the lid, wait a minute, open it — the session resumes and the power light shows sleep.</li></ol>''')) + '\n' + str(scenario('the webcam that kept disconnecting', '''<p>A USB conference camera drops out of meetings after a few minutes of no movement. Device Manager shows no driver
errors. In Power Options → Change advanced power settings → USB settings, <strong>USB selective suspend</strong> is enabled.
Disabling it (or turning off “Allow the computer to turn off this device to save power” on the camera’s USB hub in Device
Manager) stops the drop-outs. The change is recorded so the next image includes it for meeting-room PCs.</p>''')) + '\n' + str(cfu(('A user cannot see that an email attachment ends in .exe. Which setting helps?', 'File Explorer Options: turn off “Hide extensions for known file types”.'),
     ('Why choose Restart rather than Shut down when troubleshooting with fast startup on?', 'Fast startup saves the kernel session on shutdown, so only Restart gives a full fresh start.'),
     ('Where do you set which app may use the microphone?', 'Settings → Privacy & security → Microphone.'))) + '\n')

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 11, 'lesson': 3, 'id': 'cert-win-tools', 'title': 'Windows tools: Task Manager and the management consoles',
     'cert': ['A2:1.4'], 'html': sme_note('Windows operating-system tools (Core 2 1.4).') + HTML_TOOLS, 'sources': ['ms-taskmgr', 'ms-mmc', 'ms-eventlog']},
    {'course': 'ITSUP', 'chapter': 13, 'lesson': 5, 'id': 'cert-win-settings', 'title': 'Windows settings: Control Panel applets and Settings pages',
     'cert': ['A2:1.6'], 'html': sme_note('Windows settings in Control Panel and the Settings app (Core 2 1.6).') + HTML_SET,
     'sources': ['ms-power', 'ms-explorer-opts', 'ms-display']},
]

GLOSSARY = [
    ('MMC snap-in', 'A management console (.msc file) such as Event Viewer or Disk Management, hosted by Microsoft Management Console.'),
    ('Resource Monitor', 'Windows tool (resmon) showing per-process CPU, memory, disk and network use, and open file handles.'),
    ('Fast startup', 'Windows shutdown mode that saves the kernel session to disk so the next start is quicker; Restart bypasses it.'),
    ('Hibernate', 'Power state that writes memory to disk and turns the PC off; sleep keeps the session in RAM at low power.'),
    ('USB selective suspend', 'Power setting that lets Windows suspend idle USB devices; disable it if a USB device keeps disconnecting.'),
    ('Windows Tools', 'Windows 11 Control Panel folder (formerly Administrative Tools) linking the management consoles.'),
]

ITEMS = [
    match('A2:1.4', 'IT-11.3', 1, 'Match each task to the Windows tool that does it.',
          [('Extend a volume into unallocated space', 'Disk Management'), ('Roll back a display driver', 'Device Manager'),
           ('Run a clean-up script every Friday at 18:00', 'Task Scheduler'), ('Read why a service stopped overnight', 'Event Viewer')],
          'Disk Management manages volumes, Device Manager drivers, Task Scheduler timed jobs, Event Viewer logs.',
          decoys=['Certificate Manager']),
    single('A2:1.4', 'IT-11.3', 2, 'A user cannot delete a file because “it is open in another program”, but nothing is visibly open. Which tool shows which process holds it?',
           'Resource Monitor, using Associated Handles on the CPU tab',
           ['System Information (msinfo32), using the Software Environment list', 'Disk Cleanup (cleanmgr), run against the system drive', 'Certificate Manager (certmgr.msc) for the current user'],
           'Resource Monitor can search open handles by file name and show the owning process.'),
    single('A2:1.4', 'IT-11.3', 3, 'A technician needs local policy settings on a Windows 11 Home PC, but gpedit.msc will not open. Why?',
           'Group Policy Editor is not included in Windows Home',
           ['The Group Policy service is set to Manual start', 'gpedit.msc needs an internet connection', 'The PC must first be joined to a workgroup'],
           'gpedit.msc and lusrmgr.msc are Pro, Enterprise and Education tools.'),
    multi('A2:1.4', 'IT-11.3', 4, 'Which TWO can you do from Task Manager? (Choose two.)',
          ['Disable a startup app', 'See which users are signed in'],
          ['Shrink a partition', 'Import a root certificate', 'Edit a registry value', 'Schedule a weekly task'],
          'Task Manager has Startup apps and Users pages; the others need Disk Management, certmgr, regedit or Task Scheduler.'),
    single('A2:1.6', 'IT-13.4', 1, 'A USB headset disconnects whenever it has been idle for a while. Which power setting is the likely cause?',
           'USB selective suspend',
           ['Fast startup in Power Options', 'The lid close action on battery', 'Hibernate after 3 hours of sleep'],
           'Selective suspend powers down idle USB devices.'),
    match('A2:1.6', 'IT-13.4', 2, 'Match each change to where it is made.',
          [('Show file name extensions', 'File Explorer Options'), ('Rebuild the search index', 'Indexing Options'),
           ('Create a new Outlook (classic) profile', 'Mail'), ('Allow an app through the firewall', 'Windows Defender Firewall')],
          'These are Control Panel applets named in Core 2 1.6.',
          decoys=['Internet Options']),
    single('A2:1.6', 'IT-13.4', 3, 'After a driver update a technician shuts the PC down and starts it again, but the problem persists as if nothing was reloaded. What explains this?',
           'Fast startup saved the kernel session; a Restart is needed',
           ['Hibernate is disabled, so the session cannot resume', 'Sleep keeps the driver in RAM until the battery drains', 'USB selective suspend has kept the old driver loaded'],
           'With fast startup on, Shut down is a partial hibernation; Restart does a full start.'),
    order('A2:1.6', 'IT-13.4', 4, 'Put the steps for making a laptop sleep when its lid is closed in order.',
          ['Open Control Panel → Power Options', 'Choose “Choose what closing the lid does”', 'Set “When I close the lid” to Sleep for battery and plugged in',
           'Save changes', 'Close the lid and confirm the laptop sleeps'],
          'Configure, save, then test the result.'),
]
