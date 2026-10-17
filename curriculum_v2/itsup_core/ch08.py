"""ITSUP Chapter 8 — Windows Installation & Client Configuration (pass 9 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 8
SOURCES_USED = ['ms-lifecycle', 'ms-recovery', 'ms-sfc', 'ms-qmr', 'ms-gp', 'ms-kerberos', 'ms-bitlocker']

LESSONS = {
    (8, 1): {
        'sources': ['ms-lifecycle', 'ms-recovery'],
        'objectives': [
            'Compare a clean install, an in-place upgrade or repair, Reset this PC and “Fix problems using Windows Update” by what each keeps and removes',
            'Verify a device against Windows 11 hardware requirements and its version against the servicing lifecycle before planning work',
            'Plan an installation with backup, BitLocker recovery key, drivers and licensing confirmed in advance',
            'Choose the least disruptive install or reinstall option that meets the ticket’s goal, and justify it',
        ],
        'html': sme_note() + '''
<h3>Four ways to put Windows on a disk</h3>
<p>“Reinstall Windows” can mean four different jobs, and each keeps different things. Choosing the right one is a data-risk
decision, so it belongs in the plan step of the method, with a backup and a rollback.</p>
''' + table(['Option', 'Started from', 'Keeps', 'Removes', 'Typical use'], [
            ['Fix problems using Windows Update (reinstall current version)', 'Settings → System → Recovery', 'Apps, files and settings', 'Damaged system files and components are replaced', 'Update failures and system-file corruption on Windows 11 22H2 or later; may be hidden on work- or school-managed PCs'],
            ['In-place upgrade or repair install', 'setup.exe from mounted installation media, inside Windows', 'Apps, files and settings (when “keep” is chosen)', 'The old Windows system files', 'Moving to a newer version, or repairing a system that still boots'],
            ['Reset this PC', 'Settings → System → Recovery, or WinRE', '“Keep my files” keeps personal files only', 'Apps and settings always; files too with “Remove everything”', 'A badly broken installation when repair tools have failed'],
            ['Clean install', 'Boot from USB installation media', 'Nothing on the partitions you delete or format', 'Everything on those partitions', 'New or replaced drive, a standard image, or a security incident that needs a known-good start'],
        ]) + '''
<p>Microsoft lists its recovery options from least to most disruptive, and the order is worth memorising: run a troubleshooter,
reinstall the current version through Windows Update, uninstall a recent update (or go back to the previous version within 10
days of an upgrade), restore to an earlier point, and only then reset the PC. A clean install is outside that ladder: it is a
rebuild, and it needs the user’s data to be safe somewhere else first.</p>
<h3>Before you install anything</h3>
<ul>
<li><strong>Hardware requirements.</strong> Windows 11 needs a compatible 64-bit processor, 4 GB of RAM, 64 GB of storage,
UEFI firmware with Secure Boot capability and TPM 2.0. Check the device in the PC Health Check app or the manufacturer’s
documentation; a failed check is a hardware or firmware conversation, not an installer setting.</li>
<li><strong>Lifecycle.</strong> Windows 11 receives one feature update a year. Home and Pro editions are serviced for 24 months
from each version’s release, Enterprise and Education for 36 months. A device on an out-of-service version stops receiving
security updates, so “which version?” is part of every baseline. Windows 10 reached end of support on 14 October 2025;
only devices enrolled in Extended Security Updates still receive security fixes.</li>
<li><strong>Data and keys.</strong> Confirm a tested backup (Chapter 12) and where the BitLocker recovery key is stored. Most
recovery-environment options ask for that key on an encrypted drive.</li>
<li><strong>Drivers and licensing.</strong> Download storage and network drivers for the model before you start, and confirm the
edition: a Pro licence reinstalls as Pro; installing Home on a business PC removes domain-join capability.</li>
</ul>
''' + figure('f8-1', 'Choosing the least disruptive reinstall',
             ['Does Windows\nstill start?', 'Repair in place\n(WU reinstall\nor setup.exe)', 'Still broken?\nUninstall update /\nrestore point', 'Still broken?\nReset this PC', 'Last resort:\nclean install'],
             'Five boxes in order. First: does Windows still start? If yes, repair in place using Fix problems using Windows Update or an '
             'in-place repair from setup.exe, which keep apps and files. If the fault remains, uninstall the recent update or restore an '
             'earlier point. If it still remains, Reset this PC, choosing Keep my files when possible. The last box, clean install, is used '
             'only when the earlier options fail or the drive is new or untrusted, and only after the data is backed up.',
             'Each step down the ladder keeps less of the user’s environment; move down only when the evidence says the step above failed.', cols=5) + worked('choosing an option for three tickets', '''
<table class="port-table"><thead><tr><th scope="col">Ticket</th><th scope="col">Choice</th><th scope="col">Why</th></tr></thead><tbody>
<tr><td>Feature update fails at 30 % on one laptop, error 0x80073712 (a file Windows Update needs is damaged)</td><td>DISM /RestoreHealth, then sfc; if it still fails, Fix problems using Windows Update</td><td>Microsoft documents this error as file damage; both options keep apps and files</td></tr>
<tr><td>Replaced SSD in a desktop; no OS</td><td>Clean install from USB media, then restore data from backup</td><td>Nothing to keep on the new drive</td></tr>
<tr><td>Laptop returned by a leaver, to be issued to a new starter</td><td>Reset this PC → Remove everything (or the organisation’s re-image process)</td><td>The previous user’s files and settings must not carry over</td></tr>
</tbody></table>''') + scenario('the in-place upgrade that took the user’s apps', '''
<p>A technician ran setup.exe to repair a failing PC but chose “Keep nothing” because the wizard said “keep personal files” was
unavailable. The user lost eight installed applications and their settings. The option was unavailable because the media was a
different edition (Home) from the installed Windows (Pro). With matching media, the repair would have kept everything. Lesson:
confirm edition, language and architecture before running setup, and stop if the wizard offers fewer choices than you planned.</p>''') + cfu(
            ('Which option keeps apps, files and settings while replacing damaged system files?',
             'Fix problems using Windows Update (reinstall current version), or an in-place repair with matching media.'),
            ('What does Reset this PC remove even with “Keep my files”?',
             'Installed apps and settings.'),
            ('Why check where the BitLocker recovery key is before starting?',
             'Most recovery-environment options ask for it on an encrypted drive; without it the data may be unreachable.')),
    },
    (8, 2): {
        'sources': ['ms-gp', 'ms-kerberos', 'ms-bitlocker'],
        'objectives': [
            'Record a Windows baseline: device name, edition, version and build, update state, accounts, protection and encryption status',
            'Configure accounts so daily work uses a standard account and administration uses a separate, managed admin account',
            'Explain how Group Policy settings are applied (local, site, domain, OU) and refresh and report them with gpupdate and gpresult',
            'Diagnose domain sign-in failures caused by time skew, a broken device trust or an unreachable domain controller',
        ],
        'html': sme_note() + '''
<h3>A baseline is a description you can compare against</h3>
<p>A <strong>baseline</strong> is a short, dated record of how a device is configured when it is healthy. When a ticket arrives
later, you compare the device against its baseline instead of guessing what “normal” was. Collect the same fields every time,
from both Settings and the command line, because each view catches different mistakes.</p>
''' + table(['Field', 'Settings path', 'Command'], [
            ['Device name, edition, version, OS build', 'System → About', '<code>winver</code>; <code>Get-ComputerInfo -Property OsName,OsVersion,OsBuildNumber</code>'],
            ['Update state', 'Windows Update (and Update history)', '<code>Get-HotFix</code> lists installed updates'],
            ['Signed-in account and type', 'Accounts → Your info', '<code>whoami</code>; <code>whoami /groups</code>'],
            ['Join state (domain, Microsoft Entra, workgroup)', 'Accounts → Access work or school', '<code>dsregcmd /status</code>'],
            ['Protection', 'Privacy &amp; security → Windows Security', '<code>Get-MpComputerStatus</code>'],
            ['Firewall profiles', 'Windows Security → Firewall &amp; network protection', '<code>Get-NetFirewallProfile</code> (read only)'],
            ['Encryption', 'Privacy &amp; security → Device encryption, or BitLocker in Control Panel', '<code>manage-bde -status</code> (elevated)'],
        ]) + '''
<h3>Accounts: daily work and administration are separate</h3>
<p>Users should work day to day in a standard account. Administrative work uses a separate account that is used only when
elevation is needed, so a malicious attachment opened in email does not run with admin rights. On managed fleets the local
Administrator password is unique per device and rotated automatically (Windows LAPS is built into current Windows); a
technician never shares one admin password across machines or writes it into a ticket.</p>
<h3>Group Policy in one page</h3>
<p>In an Active Directory domain, <strong>Group Policy Objects (GPOs)</strong> carry settings to computers and users. They are
applied in a fixed order — local policy, then site, then domain, then organisational unit (OU), with nested OUs last — and
where two GPOs set the same thing, the one applied later wins unless an administrator has enforced or blocked inheritance.
Domain members refresh policy in the background about every 90 minutes, plus a random offset of up to 30 minutes, and at
start-up and sign-in. Some settings (software installation, folder redirection) only apply at a restart or sign-in.</p>
''' + figure('f8-2', 'Group Policy processing order', ['Local\npolicy', 'Site\nGPOs', 'Domain\nGPOs', 'OU GPOs\n(parent → child)', 'Resulting\nsettings'],
             'Five boxes left to right: Local policy, Site GPOs, Domain GPOs, OU GPOs from parent to child OU, and Resulting settings. '
             'Settings are applied in that order, so a setting in a child OU’s GPO overrides the same setting from the domain or the local '
             'policy, unless inheritance is blocked or a GPO is enforced.', 'Later policies win: local, site, domain, then OU from the top of the tree down.', cols=5) + '''
<p>Two commands cover most support work: <code>gpupdate /force</code> reapplies all policy now (and tells you if a sign-out or
restart is needed), and <code>gpresult /r</code> lists which GPOs applied to the computer and the user, and which were filtered out.
Run them before you edit any registry key a policy controls — a policy will put the setting back at the next refresh.</p>
<h3>Why domain sign-in fails</h3>
<ul>
<li><strong>Time skew.</strong> Kerberos rejects tickets when the client and domain controller clocks differ by more than the
allowed tolerance, five minutes by default. Check the clock and <code>w32tm /query /status</code> before you reset passwords.</li>
<li><strong>Broken device trust.</strong> “The trust relationship between this workstation and the primary domain failed” means
the computer account and the device no longer agree on their shared secret, often after restoring an old image or snapshot.
Repairing it needs domain rights; record and escalate.</li>
<li><strong>No domain controller reachable.</strong> Off-site laptops sign in with cached credentials but cannot get new policy or
change passwords until they reach a domain controller (on site or over VPN). DNS must point to the domain’s DNS servers.</li>
</ul>
''' + worked('“my settings keep changing back”', '''
<p>A user sets a screen-lock timeout of 30 minutes; next morning it is back to 10. <code>gpresult /r</code> shows a GPO
called <em>Workstation-Security</em> applied from the Staff OU. Its lock timeout is 10 minutes. Cause: policy, not a fault.
Response: explain the security policy to the user; if there is a business need, raise a request with the policy owner. Do not
edit the registry — the next refresh would undo it, and changing security policy is not a help-desk decision.</p>''') + cfu(
            ('Name three baseline fields and where you read each.',
             'For example: edition/version/build (System → About or winver), update state (Windows Update), join state (dsregcmd /status).'),
            ('A domain GPO and an OU GPO set the same option differently. Which wins by default?',
             'The OU GPO, because it is applied later.'),
            ('Sign-in fails with a Kerberos error and the laptop clock is 9 minutes fast. What is the likely cause?',
             'Time skew greater than the default 5-minute Kerberos tolerance.')),
    },
    (8, 3): {
        'sources': ['ms-sfc', 'ms-recovery', 'ms-qmr', 'ms-bitlocker'],
        'objectives': [
            'Run DISM /RestoreHealth followed by sfc /scannow and interpret each result message',
            'Use Event Viewer and Reliability Monitor to date a fault and connect it to a change',
            'Navigate the Windows Recovery Environment (Startup Repair, uninstall updates, System Restore, Safe Mode, Command Prompt) and state what each option changes',
            'Select a repair tool that matches the symptom before considering a reset or rebuild',
        ],
        'html': sme_note() + '''
<h3>Evidence first: when did it start, and what changed?</h3>
<p><strong>Reliability Monitor</strong> (search “reliability”, or run <code>perfmon /rel</code>) shows a day-by-day timeline of
application crashes, Windows failures, and software and driver installs. It is often the fastest way to connect “slow since
Tuesday” to “a driver was installed on Tuesday”. <strong>Event Viewer</strong> (<code>eventvwr.msc</code>) has the detail:
the System log for drivers, services, disks and shutdowns, and the Application log for program errors. Filter by level
(Critical, Error) and by the time the user reported, and copy the event source and ID into the ticket.</p>
<h3>Repairing system files: DISM, then SFC</h3>
<p>Microsoft’s documented order is to repair the component store first and then check the system files:</p>
<ol>
<li>Open an elevated Command Prompt or Terminal and run <code>DISM.exe /Online /Cleanup-image /Restorehealth</code>. DISM uses
Windows Update as its source by default; if Windows Update itself is broken, it can use mounted installation media with
<code>/Source:</code> and <code>/LimitAccess</code>.</li>
<li>When DISM reports that the operation completed successfully, run <code>sfc /scannow</code> and leave the window open until
verification reaches 100 %.</li>
</ol>
''' + table(['sfc result', 'What it means', 'Next step'], [
            ['Windows Resource Protection did not find any integrity violations', 'Protected system files are intact', 'Look elsewhere: drivers, apps, profile, hardware'],
            ['… found corrupt files and successfully repaired them', 'Files were replaced from the store', 'Restart, re-test the user’s outcome, document'],
            ['… found corrupt files but was unable to fix some of them', 'The store could not supply good copies', 'Re-run DISM with a known-good source, then sfc again; consider a repair install'],
            ['… could not perform the requested operation', 'The scan could not run', 'Run it from Safe Mode, as Microsoft advises'],
        ]) + '''
<h3>The Windows Recovery Environment (WinRE)</h3>
<p>WinRE is a small recovery system that starts when Windows fails to boot repeatedly, or on request from Settings → System →
Recovery → Advanced startup (or by holding Shift while choosing Restart). Under <em>Troubleshoot → Advanced options</em>:</p>
''' + table(['WinRE option', 'What it changes', 'Use it when'], [
            ['Startup Repair', 'Repairs boot configuration and files automatically', 'Windows does not reach sign-in after a power loss or disk change'],
            ['Uninstall Updates', 'Removes the latest quality or feature update', 'The fault started immediately after an update'],
            ['System Restore', 'Rolls back system files, drivers and settings to a restore point; personal files are kept', 'A driver or app install broke start-up'],
            ['Startup Settings (Safe Mode)', 'Nothing permanent; starts with minimal drivers', 'You need to remove a driver or app that crashes normal start-up'],
            ['Command Prompt', 'Whatever you run', 'Guided recovery with evidence — not experimentation'],
            ['Reset this PC', 'Reinstalls Windows (see 8.1)', 'Only after the options above have failed'],
        ]) + '''
<p>On an encrypted drive, WinRE asks for the BitLocker recovery key for most options. Current Windows 11 versions also include
<strong>Quick machine recovery</strong>: after repeated boot failures, WinRE can connect to Windows Update and apply a fix that
Microsoft has published for a widespread start-up problem. It is a best-effort tool; continue with the steps above if it finds
nothing.</p>
''' + figure('f8-3', 'Matching repair tools to symptoms', ['Symptom\n+ date', 'Reliability\nMonitor /\nEvent Viewer', 'Boots? DISM\nthen SFC', 'No boot?\nWinRE options', 'Re-test +\ndocument'],
             'Five boxes left to right. Start with the symptom and the date it began. Use Reliability Monitor and Event Viewer to find '
             'what changed at that time. If Windows boots, run DISM RestoreHealth then sfc scannow. If it does not boot, use the WinRE '
             'options: Startup Repair, Uninstall Updates, System Restore or Safe Mode. Finally re-test the user’s outcome and document the '
             'cause and the fix.', 'Repair tools follow the evidence: date the fault, find the change, then choose the tool that targets it.', cols=5) + worked('blue screen after a printer driver', '''
<ol>
<li>Reliability Monitor shows “Windows failure” every day since 14 Oct, and an “Application install: printer driver package” the
same morning.</li>
<li>Event Viewer System log: BugCheck event after each crash; the dump points at a driver file from the printer package.</li>
<li>Plan: start in Safe Mode, uninstall the driver package, restart normally; rollback is reinstalling the previous driver
version saved in the ticket.</li>
<li>Result: no crash over two days of normal use; user prints with the vendor’s current driver from the print server.
Documented, and the printer team told about the faulty package.</li>
</ol>''') + cfu(
            ('Which runs first, DISM /RestoreHealth or sfc /scannow, and why?',
             'DISM first: it repairs the component store that SFC copies good files from.'),
            ('Which WinRE option keeps personal files but undoes a driver install?',
             'System Restore (to a restore point from before the install).'),
            ('Where do you look first to connect a fault to a recent change?',
             'Reliability Monitor (perfmon /rel), then the matching Event Viewer entries.')),
    },
    (8, 4): {
        'sources': ['ms-recovery', 'ms-sfc'],
        'objectives': [
            'Diagnose a failed Windows update from Update history, error codes and logs before choosing a fix',
            'Apply the least disruptive fix for a failed update and verify that the update installs and the user’s work is intact',
            'Document a failed-update incident so it can be compared across devices and escalated as a pattern',
        ],
        'html': sme_note('Capstone walkthrough and decision table added in pass 9.') + '''
<h3>The failed-update capstone</h3>
<p>The story: “PC restarted three times overnight. Windows Update says the update failed. The user can still sign in.” You have
45 minutes. The pass bar is evidence and the least disruptive fix — not a fresh install.</p>
<ol>
<li><strong>Identify.</strong> One device or many? Which update (KB number or feature version) and which error code? Settings →
Windows Update → Update history shows both. Is the user’s work affected now?</li>
<li><strong>Probable cause.</strong> Common causes: not enough free disk space; damaged update files or component store; a
driver or security tool blocking the install; a pending restart; a network or proxy problem reaching Windows Update.</li>
<li><strong>Test.</strong> Free space on C: (feature updates need several gigabytes); Reliability Monitor for the failure entries;
the Windows Update troubleshooter (Settings → System → Troubleshoot → Other troubleshooters); for many devices, whether the
update is paused or blocked by policy.</li>
<li><strong>Plan and change one thing.</strong> Free disk space; or DISM then SFC; or remove the blocking driver; retry the
update in an agreed window.</li>
<li><strong>Verify.</strong> The update shows as successfully installed, the build number in winver matches, and the user confirms
their applications work.</li>
</ol>
''' + table(['Evidence', 'Most likely domain', 'Least disruptive next step'], [
            ['Error mentions files missing or damaged (for example 0x80073712)', 'Component store', 'DISM /RestoreHealth, sfc /scannow, retry; then “Fix problems using Windows Update”'],
            ['C: has less than a few GB free', 'Storage', 'Storage Sense / Disk Cleanup, move user data; retry'],
            ['Failure began after a new driver or security tool', 'Driver / third-party software', 'Update or remove the component with its owner’s approval; retry'],
            ['Same error on 30 devices in one OU', 'Policy, network or the update itself', 'Stop single-device fixes; open a problem record; escalate to the endpoint team'],
            ['Device now fails to start', 'Boot / OS', 'WinRE → Uninstall Updates; then repair (8.3)'],
        ]) + scenario('thirty laptops, one error', '''
<p>A service-desk technician fixes a failed update on one laptop with DISM and SFC. By lunchtime 29 more tickets arrive with the
same error code. The technician stops fixing them one by one, links the tickets to one problem record, and sends the endpoint
team the common facts: same model, same storage driver version, same KB, same error. The endpoint team pauses the update ring
for that model while the vendor driver is updated. Fixing the pattern saved 29 manual repairs and avoided pushing a fix the
team could not explain.</p>''') + cfu(
            ('Where do you find the KB number and error code for a failed update?',
             'Settings → Windows Update → Update history.'),
            ('When should you stop repairing devices one at a time?',
             'When the same failure appears on many devices — open a problem record and escalate the pattern.'),
            ('Name two checks that prove the fix worked.',
             'Update history shows the update installed and winver shows the expected build; the user confirms their work.')),
    },
}

GLOSSARY = [
    ('Clean install', 'Installing Windows on partitions that are deleted or formatted first, so nothing from the old installation remains.'),
    ('Reset this PC', 'A Windows recovery option that reinstalls Windows; “Keep my files” keeps personal files but removes apps and settings.'),
    ('Windows Recovery Environment (WinRE)', 'The recovery system that offers Startup Repair, Uninstall Updates, System Restore, Safe Mode, Command Prompt and Reset this PC.'),
    ('DISM', 'Deployment Image Servicing and Management; DISM /Online /Cleanup-Image /RestoreHealth repairs the Windows component store.'),
    ('System File Checker (SFC)', 'sfc /scannow checks protected system files and replaces damaged ones from the component store.'),
    ('Reliability Monitor', 'A day-by-day timeline of crashes, failures and installs (perfmon /rel), used to connect a fault to a change.'),
    ('Group Policy Object (GPO)', 'A set of policy settings applied to computers or users in a domain, processed local → site → domain → OU.'),
    ('Servicing channel / lifecycle', 'The period a Windows version receives updates: 24 months for Home and Pro, 36 months for Enterprise and Education.'),
    ('Time skew', 'A clock difference between client and domain controller; more than 5 minutes (default) breaks Kerberos sign-in.'),
]

PLAN = {
    'warmup': 'Rank four options — reset, clean install, in-place repair, “Fix problems using Windows Update” — from least to most disruptive, and say what each keeps.',
    'guided': 'Collect a full baseline on the lab VM (Settings and CLI side by side), then run gpresult /r and Reliability Monitor and explain one entry from each.',
    'worked_example': 'Lesson 8.1 option table for three tickets; 8.2 “settings keep changing back” (Group Policy); 8.3 blue screen after a printer driver.',
    'cfu': ['What does Reset this PC remove even with “Keep my files”?',
            'Which runs first, DISM /RestoreHealth or sfc /scannow?',
            'A domain laptop’s clock is 9 minutes fast and sign-in fails. Why?'],
    'exit_ticket': 'Write the plan (change, impact, rollback, verification) for repairing a failed feature update on one laptop with error 0x80073712.',
    'misconceptions_add': ['“Editing the registry fixes a setting that keeps changing back.” If a GPO sets it, the next refresh puts it back; check gpresult first.',
                           '“Reset this PC with Keep my files keeps everything.” It keeps personal files only; apps and settings are removed.'],
    'classroom_lab': 'CL-8',
    'materials_add': 'Classroom lab CL-8 (recovery ladder in a lab VM with a snapshot).',
}

ITEMS = [
    item('IT-8.1', 1, 'A Windows 11 PC still boots but update files are damaged. Which option repairs it and keeps apps, files and settings?',
         'Reinstall the current version through Windows Update', ['Reset this PC with the Keep my files choice selected', 'A clean install from USB media after a full backup', 'Remove everything, then restore the files from OneDrive'],
         '“Fix problems using Windows Update” reinstalls the current version and keeps apps, files and settings; Reset this PC removes apps and settings.'),
    item('IT-8.1', 2, 'What does Reset this PC remove even when you choose “Keep my files”?',
         'Installed apps and their settings', ['Only the files in the Downloads folder', 'The user’s documents and pictures', 'Nothing at all apart from temporary files'],
         'Reset this PC always removes apps and settings; Keep my files preserves personal files only.'),
    item('IT-8.1', 3, 'A Windows 11 Pro version is past its 24-month servicing period. What is the main risk?',
         'It no longer gets security updates', ['It will stop booting at the next restart', 'Its Pro licence turns into a Home licence', 'Its user accounts are deleted automatically'],
         'Out-of-service versions stop receiving security updates; Home and Pro are serviced for 24 months, Enterprise and Education for 36.'),
    item('IT-8.2', 1, 'A user’s screen-lock setting returns to 10 minutes every morning. What should you check first?',
         'gpresult /r for a policy setting the timeout', ['The power supply and the battery health report', 'The DNS suffix list on the network adapter', 'Whether the display driver needs reinstalling'],
         'Settings that revert after a refresh usually come from Group Policy; gpresult shows which GPO applied.'),
    item('IT-8.2', 2, 'A domain GPO and an OU GPO set the same option to different values. Which value applies by default?',
         'The OU GPO, because it is processed later', ['The domain GPO, because it covers more users', 'The local policy, because it is on the device', 'Whichever GPO was edited most recently'],
         'Processing order is local, site, domain, OU; the last applied wins unless inheritance is blocked or a GPO is enforced.'),
    item('IT-8.2', 3, 'Why should daily work use a standard account rather than an administrator account?',
         'Malware the user runs gets only standard rights', ['Standard accounts make Windows start faster', 'Admin accounts cannot open email or browse', 'Standard accounts never need a password set'],
         'Least privilege limits what malicious code can do when the user opens it.'),
    item('IT-8.3', 1, 'In which order does Microsoft recommend running the system-file repair tools?',
         'DISM /RestoreHealth first, then sfc /scannow', ['sfc /scannow first, then chkdsk /f /r on C:', 'chkdsk first, then DISM, then Startup Repair', 'Startup Repair first, then sfc in Safe Mode'],
         'DISM repairs the component store that SFC uses as its source of good files.'),
    item('IT-8.3', 2, 'A PC crashes daily since a driver was installed on Tuesday. Which WinRE option undoes it but keeps personal files?',
         'System Restore to a point before Tuesday', ['Reset this PC with the Remove everything choice', 'Command Prompt with format C: /q', 'A clean install from a recovery drive'],
         'System Restore rolls back drivers, settings and system files to the restore point while keeping personal files.'),
    item('IT-8.3', 3, 'Which tool shows a day-by-day timeline of crashes alongside software and driver installs?',
         'Reliability Monitor (perfmon /rel)', ['Disk Management (diskmgmt.msc)', 'Device encryption in Settings', 'The Windows Update troubleshooter tool'],
         'Reliability Monitor correlates failures with installs, which helps date a fault to a change.'),
    item('IT-8.3', 4, 'sfc reports it found corrupt files but could not fix some of them. What is the best next step?',
         'Re-run DISM with a known-good source, then sfc again', ['Delete the C:\\Windows\\WinSxS folder so it is rebuilt', 'Turn off Windows Resource Protection and retry', 'Replace the system drive before trying anything else'],
         'SFC needs good copies in the component store; DISM with a good /Source repairs the store first.'),
    item('IT-8.4', 1, 'Domain sign-in fails with a Kerberos error and the laptop clock is 9 minutes fast. What is the likely cause?',
         'Clock skew beyond the default 5-minute limit', ['An expired Windows licence on the laptop itself', 'A full recycle bin on the system drive', 'A missing printer driver for the device'],
         'Kerberos rejects authentication when clocks differ by more than the tolerance, 5 minutes by default.'),
    item('IT-8.4', 2, 'You changed a GPO and need a user’s PC to apply it now. Which command do you use?',
         'gpupdate /force', ['ipconfig /renew', 'sfc /scannow', 'netsh winsock reset'],
         'gpupdate /force reapplies all policy settings immediately instead of waiting for the background refresh.'),
    item('IT-8.4', 3, 'A PC reports that the trust relationship with the domain failed after an old snapshot was restored. What should tier 1 do?',
         'Record the error and escalate to someone with domain rights', ['Delete the user’s profile and sign in with it again', 'Turn off the firewall so the domain can be reached', 'Set the device clock back to match the date of the old snapshot'],
         'The computer account secret no longer matches; repairing the trust needs domain permissions.'),
]

LABS = {
    'CL-8': {
        'id': 'CL-8', 'title': 'Windows recovery ladder in a lab VM', 'chapters': [('ITSUP', 8), ('CLIENT', 1)],
        'review': 'Pending SME review',
        'objective': 'Use evidence tools and repair options in order of disruption on a lab VM, recording what each option keeps and changes.',
        'scenario': 'The instructor has installed a deliberately unwanted app and driver package on a Windows 11 lab VM after taking a snapshot and a restore point.',
        'prerequisites': ['Lessons 8.1–8.3', 'A lab VM with a snapshot (CL-6)'],
        'equipment': 'Windows 11 lab VM (Education or Enterprise evaluation, or institution-licensed) with a virtual TPM, a snapshot, a restore point and internet access for Windows Update.',
        'low_cost': 'Instructor demonstration on one projected VM with students completing the evidence worksheet from screenshots.',
        'steps': [
            'Record the baseline: winver, Settings → System → About, Update history, dsregcmd /status, manage-bde -status.',
            'Open Reliability Monitor and Event Viewer; find and record the install event for the unwanted package (date, source, ID).',
            'Run DISM.exe /Online /Cleanup-image /Restorehealth, then sfc /scannow; record both result messages.',
            'Boot to WinRE (Settings → System → Recovery → Advanced startup). Record the options offered, then use System Restore to the instructor’s restore point.',
            'After restart, confirm the package is gone and your test file in Documents is still present.',
            'Write the ticket: evidence, the option used, what it kept and removed, verification, and why you did not reset or reinstall.',
            'Revert the VM to its snapshot at the end of the lab.',
        ],
        'expected': 'Baseline recorded; install event identified; DISM and SFC results recorded; System Restore removes the package and keeps personal files; ticket justifies the least disruptive option.',
        'troubleshooting': ['If System Restore shows no restore points, protection may be off for C: — note it and use Uninstall Updates or the snapshot instead.',
                            'If WinRE asks for a BitLocker recovery key, record where the key is stored before continuing; do not guess.'],
        'reflection': ['Which piece of evidence linked the fault to its cause fastest?',
                       'What would Reset this PC have removed that System Restore kept?',
                       'Why revert the snapshot, and how is that different from a backup?'],
        'rubric': 'lab', 'minutes': 60, 'objectives': ['IT-8.1', 'IT-8.3'],
    },
}
