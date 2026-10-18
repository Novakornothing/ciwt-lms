"""A+ Core 2 3.1 (Windows OS issues) — ITSUP 11.1; Core 2 1.10 (installing applications to requirements) — ITSUP 8.2."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-noos', '“No operating system found”: check in this order',
    ['Is the drive\ndetected in UEFI?', 'Boot order /\nboot entry right?', 'UEFI vs legacy\n(CSM) mode match?', 'WinRE: Startup\nRepair', 'bootrec /rebuildbcd\n(then restore)'],
    'Five boxes in order. First check that the firmware detects the system drive at all — if not, it is a cable, '
    'connection or drive fault. Then check the boot order and that the Windows Boot Manager entry is first. Then check that '
    'the firmware boot mode matches how the disk was installed: UEFI for GPT disks, legacy CSM for MBR. Then boot the Windows '
    'Recovery Environment and run Startup Repair. Only then use bootrec commands such as bootrec /rebuildbcd, and if the '
    'disk itself is failing, restore from backup.',
    'Most “no OS” tickets are firmware settings or a removable drive left in — check before repairing boot files.', cols=5)

HTML_31 = f'''
<p>Lessons 11.1–11.4 cover the main Windows symptom patterns (BSOD, slow performance, crashes, slow profile loads and
time drift). Core 2 3.1 adds several symptoms that each have a quick first check.</p>
<table class="ref-table"><thead><tr><th scope="col">Symptom</th><th scope="col">First checks</th></tr></thead><tbody>
<tr><td><strong>No OS found</strong> / “no bootable device”</td><td>A USB stick or disc left in first in the boot order; the drive is not detected in firmware; the boot mode (UEFI vs legacy CSM) changed; then Startup Repair and bootrec in WinRE.</td></tr>
<tr><td><strong>Frequent shutdowns</strong></td><td>Event Viewer System log: Event ID 41 (Kernel-Power) means Windows did not shut down cleanly — often power or heat, not software. Check temperatures, fans and dust, the PSU, and the power plan.</td></tr>
<tr><td><strong>Services not starting</strong></td><td><code>services.msc</code>: start type, the log-on account (an expired service-account password is common) and dependencies; System log events from the Service Control Manager.</td></tr>
<tr><td><strong>USB controller resource warnings</strong></td><td>“Not enough USB controller resources”: too many devices or hubs on one controller. Move devices to ports on a different controller (for example rear ports) or remove an unpowered hub.</td></tr>
<tr><td><strong>System instability</strong> (random freezes, restarts, errors)</td><td>Recent driver or update (roll back); hardware tests — memory diagnostic, drive health, temperatures; <code>sfc /scannow</code> after <code>DISM /RestoreHealth</code> for system-file corruption.</td></tr>
<tr><td><strong>Low memory warnings</strong></td><td>Task Manager: which process grows over time (a memory leak) versus genuinely too little RAM for the workload.</td></tr>
</tbody></table>
{_FIG}
{worked('a PC that switches itself off', '''<ol>
<li>Users report a PC that “just turns off” two or three times a day. No BSOD is shown.</li>
<li>Event Viewer → System: Event ID 41 (Kernel-Power) at each time, with no BugCheck code — power was lost, not a crash.</li>
<li>Hardware monitor: CPU reaches 100 °C under load; the heatsink fins are packed with dust.</li>
<li>Clean the cooler and case filters (power off, unplugged, ESD precautions); temperatures under load drop to 70 °C.</li>
<li>Monitor for a week; no further shutdowns. Document the cause and add the site to the cleaning schedule.</li></ol>''')}
{cfu(('A PC says “No operating system found” the morning after a USB installer was used. What do you check first?', 'Remove the USB stick or fix the boot order — the PC may be trying to boot from it.'),
     ('What does Event ID 41 (Kernel-Power) tell you?', 'Windows restarted without a clean shutdown — often power or overheating.'),
     ('A service will not start after a password change policy. What is a likely cause?', 'The service’s log-on account password expired or changed.'))}
'''

HTML_110 = f'''
<p>Before installing an application, check its <strong>system requirements</strong> against the PC — Core 2 1.10 lists
them explicitly:</p>
<ul>
<li><strong>32-bit vs. 64-bit</strong> — 64-bit Windows runs most 32-bit applications (through WOW64), but a 64-bit application
cannot run on 32-bit Windows, and 32-bit drivers cannot load on 64-bit Windows.</li>
<li><strong>Graphics</strong> — whether a <strong>dedicated</strong> (discrete) graphics card is required or <strong>integrated</strong>
graphics are enough, and the <strong>VRAM</strong> required (CAD, video and games often specify it).</li>
<li><strong>RAM</strong>, <strong>CPU</strong> (generation, core count, instruction-set support) and <strong>storage</strong> (free space for the
install and its data).</li>
<li><strong>External hardware tokens</strong> — some licensed software needs a USB licence dongle or a security key present.</li>
<li><strong>Application-to-OS compatibility</strong> — supported Windows versions and editions; check the vendor’s list.</li>
</ul>
<p><strong>Distribution methods:</strong> physical media vs. a <strong>mountable ISO</strong> file (double-click in Windows to mount
it as a drive), a <strong>downloadable package</strong> (<code>.exe</code>, <code>.msi</code>, or a package manager), or
<strong>image deployment</strong> (the app is built into the organisation’s standard image).</p>
<p><strong>Impact considerations:</strong> the <strong>device</strong> (performance, conflicts, security software), the
<strong>network</strong> (bandwidth for installs and updates, firewall rules the app needs), <strong>operation</strong> (support
load, training, licensing) and the <strong>business</strong> (cost, compliance, downtime during rollout).</p>
{worked('the CAD install that will not start', '''<ol>
<li>Engineering wants a CAD package on a new hire’s laptop. Vendor requirements: 64-bit Windows 11, 16 GB RAM, dedicated GPU with 4 GB VRAM.</li>
<li>Laptop: 64-bit Windows 11, 16 GB RAM, but integrated graphics only (System Information / Task Manager → GPU).</li>
<li>The install would succeed but performance would fail the requirement. Raise it with the manager: approve a laptop with a dedicated GPU, or a VDI/workstation option.</li>
<li>Record the decision on the ticket — requirements were checked <em>before</em> installation.</li></ol>''')}
{cfu(('Can a 64-bit application run on 32-bit Windows?', 'No — 64-bit Windows can run most 32-bit apps, not the reverse.'),
     ('How do you use an application delivered as an ISO file without burning a disc?', 'Mount the ISO (double-click in Windows) and run the installer from the virtual drive.'),
     ('Name the four impact areas Core 2 1.10 lists for a new application.', 'Device, network, operation and business.'))}
'''

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 11, 'lesson': 1, 'id': 'cert-win-issues', 'title': 'More Windows symptoms: no OS found, shutdowns, services, USB resources',
     'cert': ['A2:3.1'], 'html': sme_note('Additional Windows OS symptoms from Core 2 3.1.') + HTML_31, 'sources': ['ms-bootrec', 'ms-eventlog', 'ms-sfc']},
    {'course': 'ITSUP', 'chapter': 8, 'lesson': 2, 'id': 'cert-app-reqs', 'title': 'Installing applications to requirements',
     'cert': ['A2:1.10'], 'html': sme_note('Application system requirements, distribution methods and impact (Core 2 1.10).') + HTML_110, 'sources': ['ms-wow64']},
]

GLOSSARY = [
    ('Event ID 41 (Kernel-Power)', 'Windows log entry recorded when the system restarted without a clean shutdown.'),
    ('bootrec', 'Windows RE command that repairs the master boot record, boot sector and boot configuration data.'),
    ('WOW64', 'The Windows subsystem that runs 32-bit applications on 64-bit Windows.'),
    ('VRAM', 'Video RAM: memory dedicated to the graphics processor.'),
    ('Mountable ISO', 'A disc image file that Windows can attach as a virtual drive.'),
]

ITEMS = [
    order('A2:3.1', 'IT-11.1', 1, 'A desktop shows “No operating system found”. Put the checks in a sensible order.',
          ['Remove USB media and check the boot order', 'Confirm the drive is detected in UEFI', 'Check UEFI vs legacy boot mode', 'Run Startup Repair from WinRE', 'Rebuild the BCD with bootrec'],
          'Cheapest and least invasive first: removable media and boot order, detection, boot mode, then repair tools.'),
    single('A2:3.1', 'IT-11.1', 2, 'A PC turns off without warning several times a day. The System log shows Event ID 41 (Kernel-Power) with no bug-check code. What is the most likely cause?',
           'Overheating or a power-supply problem',
           ['A corrupted user profile', 'An expired service-account password', 'A DNS misconfiguration'],
           'Event 41 without a bug check means power was lost — commonly heat or the PSU, not a software crash.'),
    single('A2:3.1', 'IT-11.1', 3, 'A user plugs a fourth webcam into a USB hub and Windows reports “Not enough USB controller resources”. What should the technician try first?',
           'Move some devices to ports on a different controller',
           ['Reinstall Windows', 'Update the monitor driver', 'Disable USB selective suspend in the BIOS'],
           'The controller has run out of endpoints; spreading devices across controllers fixes it.'),
    multi('A2:3.1', 'IT-11.1', 4, 'A line-of-business service will not start after the domain’s password policy changed. Which TWO checks are most relevant? (Choose two.)',
          ['The service’s log-on account and its password', 'Service Control Manager errors in the System log'],
          ['The display scaling setting', 'The Wi-Fi channel in use', 'The printer’s default tray'],
          'Services that run as an account fail when its password changes; the System log records why.'),
    single('A2:1.10', 'IT-8.2', 1, 'A vendor’s installer refuses to run on an older PC with “This app can’t run on your PC”. The PC runs 32-bit Windows 10. What is the cause?',
           'The application is 64-bit only',
           ['The PC has integrated graphics', 'The installer needs a USB dongle', 'The PC is not joined to a domain'],
           '64-bit applications cannot run on 32-bit Windows.'),
    match('A2:1.10', 'IT-8.2', 2, 'Match each requirement check to the application that most needs it.',
          [('Dedicated GPU with 8 GB VRAM', 'Video-editing suite'), ('USB licence dongle present', 'Licensed engineering software with a hardware token'),
           ('Supported OS edition list', 'Line-of-business app certified for specific Windows versions'), ('Free disk space for a large data set', 'Mapping app with offline maps')],
          'Each Core 2 1.10 requirement maps to the kind of application that typically states it.',
          decoys=['Browser extension']),
    single('A2:1.10', 'IT-8.2', 3, 'Software is supplied as a single .iso file. How can a technician install it on Windows 11 without burning a disc?',
           'Mount the ISO and run the installer from it',
           ['Rename the file to .exe and run it', 'Copy the file into System32', 'Open the ISO in Notepad'],
           'Windows can mount an ISO as a virtual drive.'),
    multi('A2:1.10', 'IT-8.2', 4, 'Before a company-wide rollout of a new app, which TWO are network impact considerations? (Choose two.)',
          ['Bandwidth used when 500 PCs download it', 'Firewall rules the app needs to reach its server'],
          ['The training time for staff', 'The licence cost per seat', 'The VRAM on each PC'],
          'Download load and required firewall rules are network impacts; training and cost are operation and business impacts; VRAM is a device requirement.'),
]
