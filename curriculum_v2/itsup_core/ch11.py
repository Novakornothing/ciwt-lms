"""ITSUP Chapter 11 — Software Troubleshooting (pass 9 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 11
SOURCES_USED = ['ms-recovery']

LESSONS = {
    (11, 1): {
        'objectives': [
            'Classify a software symptom as a crash, hang, error message, slowness or wrong result, and record its exact text and timing',
            'Determine whether a software fault is limited to one app, one user profile, one device or many devices before choosing a fix',
            'Read Application Error and Application Hang events and Reliability Monitor entries to date and name the failing component',
        ],
        'html': sme_note() + '''
<h3>Five shapes of software trouble</h3>
<p>Software faults come in a small number of shapes. Naming the shape tells you which evidence to collect.</p>
''' + table(['Shape', 'What the user says', 'Evidence to collect'], [
            ['Crash', '“It just closes” / “it disappears”', 'Application log: event “Application Error” (ID 1000) with the faulting module; Reliability Monitor entry'],
            ['Hang', '“Not responding”, spinning cursor', '“Application Hang” event (ID 1002); Task Manager CPU and disk for that process at the time'],
            ['Error message', '“It says …”', 'The exact text and code, a screenshot, and what the user clicked just before'],
            ['Slowness', '“It takes forever”', 'When it started, which actions are slow, Task Manager Performance tab, a comparison with a similar device'],
            ['Wrong result', '“The numbers are wrong” / “it prints blank”', 'Steps to reproduce, the input used, and the expected output'],
        ]) + '''
<h3>Scope it: app, profile, device or fleet?</h3>
<p>Scope decides the fix. If one app fails for one user on one device, a repair of that app or that user’s settings is in
proportion. If every user on one device fails, look at the device (updates, drivers, disk, security software). If the same
app fails on many devices after the same update, stop fixing devices and report a pattern (Chapter 8.4).</p>
''' + figure('f11-1', 'Scoping a software fault', ['App fails', 'Other user,\nsame PC?', 'Same user,\nother PC?', 'Many PCs,\nsame version?', 'Scope\nrecorded'],
             'Five boxes in a row. An app fails. Test it with another user on the same PC: if it works, the problem is in the first user’s '
             'profile or settings. Test the same user on another PC: if it fails there too, suspect the user’s account, licence or data. Check '
             'whether many PCs on the same app version fail: if so, it is a pattern for the app owner. The last box records the scope.',
             'Three comparisons place a software fault in a user profile, a device or the application itself.', cols=5) + worked('reading a crash event', '''
<pre><code>Log Name: Application    Source: Application Error    Event ID: 1000
Faulting application name: report.exe, version 4.2.0
Faulting module name: pdfprint.dll, version 1.8.3
Exception code: 0xc0000005</code></pre>
<p>What it tells you: the program report.exe crashed inside a module called pdfprint.dll, a plug-in rather than the main
program. Reliability Monitor shows the plug-in was updated yesterday. Theory: the plug-in update. Cheapest test: does the crash
happen only when the user prints to PDF? (Yes.) Next step: report to the application owner with the event text and the plug-in
version; offer the user the built-in “Microsoft Print to PDF” as a workaround.</p>''') + cfu(
            ('Which two Application-log events correspond to a crash and a hang?',
             'Application Error (ID 1000) for a crash and Application Hang (ID 1002) for a hang.'),
            ('An app fails only for one user, on any PC. Where do you look?',
             'At that user’s account, licence, settings or data — not the device.'),
            ('Why copy the exact error text instead of summarising it?',
             'Exact text and codes can be searched and matched across tickets and vendor documentation.')),
    },
    (11, 2): {
        'sources': ['ms-recovery'],
        'objectives': [
            'Perform a clean boot (non-Microsoft services and startup apps disabled) and re-enable items in halves to find a conflict',
            'Use Safe Mode, started from WinRE or System Configuration, and return the device to normal start-up afterwards',
            'Repair or reset an app from Settings, or run a vendor repair (for example Microsoft 365 Quick Repair), and state what each option keeps',
            'Test with a new or different user profile to separate profile corruption from app or system faults',
        ],
        'html': sme_note() + '''
<h3>Remove variables, then add them back</h3>
<p>Isolation means removing everything that might be interfering, confirming the problem has gone, and then adding things back
until it returns. The thing you added last is the cause. Windows gives you three ways to remove variables.</p>
<h4>1. Clean boot</h4>
<ol>
<li>Run <code>msconfig</code> (System Configuration) → Services tab → tick <em>Hide all Microsoft services</em> → <em>Disable all</em>.</li>
<li>Task Manager → Startup apps → disable each enabled item (note which ones you changed).</li>
<li>Restart and test. If the problem has gone, re-enable half of the items, restart and test again, and keep halving.</li>
<li>When finished, put everything back the way you found it except the culprit, and record the change.</li>
</ol>
<p>A clean boot changes start-up configuration, so it is a change: tell the user, and on managed devices check that it is
allowed. Security software is usually a Microsoft service on Windows (Defender) but may be third-party — do not leave protection
disabled.</p>
<h4>2. Safe Mode</h4>
<p>Safe Mode starts Windows with a minimal set of drivers and services. Reach it from WinRE (Troubleshoot → Advanced options →
Startup Settings → Restart, then 4 for Safe Mode or 5 for Safe Mode with Networking), or from <code>msconfig</code> → Boot → Safe
boot. If you use msconfig, untick Safe boot afterwards, or the PC will keep starting in Safe Mode. A fault that disappears in
Safe Mode points at a driver, a service or a startup program; a fault that remains points at the core OS, the hardware or the
user’s data.</p>
<h4>3. Repair or reset the app</h4>
''' + table(['Option', 'Where', 'Keeps', 'Removes'], [
            ['Repair (Store and many built-in apps)', 'Settings → Apps → Installed apps → (app) → ⋯ → Advanced options', 'App data', 'Damaged app files are fixed'],
            ['Reset (Store and many built-in apps)', 'Same page', 'Nothing app-specific', 'The app’s data and settings on this device'],
            ['Modify / Repair (desktop apps)', 'Settings → Apps → Installed apps → (app) → ⋯ → Modify, or the vendor installer', 'Depends on the vendor — Microsoft 365 Quick Repair runs offline; Online Repair reinstalls', 'Damaged program files'],
            ['Uninstall and reinstall', 'Installed apps, or the software portal', 'Cloud-stored data', 'Local app data unless the vendor keeps it'],
        ]) + '''
<h4>4. Try another profile</h4>
<p>Sign in as a test user (or a second user who has the same app). If the app works for them on the same PC, the first user’s
profile — settings, cached credentials, add-ins — is the domain. Resetting an app’s settings for that user, or rebuilding the
profile with the endpoint team, is then in proportion; reinstalling the app is not.</p>
''' + figure('f11-2', 'Halving the start-up items in a clean boot', ['All 16 items\noff: fault\ngone', 'Turn on 8:\nfault back?', 'Yes: those 8\n→ turn on 4', 'Repeat until\none item', 'Leave culprit\noff, record'],
             'Five boxes left to right. With all sixteen non-Microsoft services and startup items disabled, the fault is gone. Turn eight back on '
             'and test: if the fault returns, the culprit is among those eight, so turn four of them on next; if not, it is among the other eight. '
             'Repeat until a single item is left. Leave that item disabled, restore everything else and record the change.',
             'Halving finds one culprit among sixteen items in at most four restarts.', cols=5) + cfu(
            ('Why tick “Hide all Microsoft services” before “Disable all” in msconfig?',
             'So Windows’ own services keep running; only third-party services are disabled for the test.'),
            ('A fault disappears in Safe Mode. What does that suggest?',
             'A driver, service or startup program that Safe Mode does not load is involved.'),
            ('What is the difference between Repair and Reset for a Store app?',
             'Repair fixes the app’s files and keeps its data; Reset also clears the app’s data and settings.')),
    },
    (11, 3): {
        'objectives': [
            'Evaluate repair, in-place reinstall and rebuild options by time, data risk, confidence in the result and policy',
            'Set a time box for repair and decide from the evidence when a rebuild is the better use of time',
            'Plan a rebuild with backup, application list, licences, user data restore and verification under change control',
        ],
        'html': sme_note() + '''
<h3>Repair, reinstall or rebuild?</h3>
<p>Every software fault ends with one of three decisions. The right one is the least disruptive option that will reliably
restore the user’s outcome in reasonable time — not the one the technician prefers.</p>
''' + table(['Option', 'Choose it when', 'Avoid it when'], [
            ['Targeted repair (one app, one driver, one setting)', 'Evidence points to one component; a fix is documented', 'You cannot name the component after the time box'],
            ['In-place reinstall of Windows (Chapter 8)', 'System files or updates are damaged but apps and data are fine', 'The device is suspected of compromise'],
            ['Rebuild / reimage', 'Several unrelated faults, repeated failures, unknown changes, a confirmed compromise (after security’s go-ahead), or the standard image is the quicker route', 'No tested backup, or the user’s apps cannot be reinstalled'],
        ]) + '''
<h3>Time boxes protect the user’s day</h3>
<p>Agree a time box for repair at the plan step — for example, 45 minutes for a single app fault on a standard desktop. If the
cause is not found inside it, step back and compare: how long would a rebuild take, including restoring data and apps, and how
sure are you it will help? On a managed fleet a standard rebuild may be faster and more certain than a long repair; on a
personally configured research PC it may cost the user days.</p>
<h3>A rebuild is a change</h3>
<ol>
<li><strong>Back up and verify</strong> the user’s data (Chapter 12) — confirm that a file from the backup opens.</li>
<li><strong>List applications, versions and licences</strong>, including plug-ins, browser profiles and printers.</li>
<li><strong>Record settings</strong> the user cares about (mapped drives, signatures, dictionaries, display layout).</li>
<li><strong>Approve</strong> under change control if your organisation requires it, and agree a time with the user.</li>
<li><strong>Rebuild, restore, verify:</strong> the user signs in and does the task that failed, plus two everyday tasks.</li>
</ol>
''' + worked('the 45-minute time box', '''
<p>A finance PC’s accounting app crashes randomly. 20 minutes: Application Error events point at three different modules on three
days; sfc finds and repairs files; crashes continue. 40 minutes: clean boot does not stop them; Reliability Monitor shows several
failed updates and an unknown utility installed last month. Decision at 45 minutes: several unrelated faults and unknown changes
— rebuild with the standard finance image is quicker and more certain. Plan: verified backup, app list (accounting app with
licence key from the software portal, PDF plug-in, two printers), rebuild after 16:00 with the user’s agreement, user verifies
an end-of-day report.</p>''') + scenario('the rebuild that lost the macros', '''
<p>A technician rebuilt a PC for a lab coordinator without listing the applications. The rebuild took an hour; restoring the
coordinator’s spreadsheet macros, stored in a local add-in folder that was not backed up, took two days of re-creating work.
The rebuild was the right decision; the missing inventory step was the failure.</p>''') + cfu(
            ('Give two signs that a rebuild is a better choice than more repair.',
             'Several unrelated faults or repeated failures, unknown changes, or a confirmed compromise (with security’s approval).'),
            ('What must be true about the backup before a rebuild?',
             'It has been verified — a file from it has actually been opened.'),
            ('Why list applications and licences first?',
             'So everything the user needs can be reinstalled and activated after the rebuild.')),
    },
    (11, 4): {
        'objectives': [
            'Diagnose a slow logon by measuring where the time goes: policy processing, scripts and drive mappings, profile load, startup apps',
            'Use Task Manager (Processes, Performance, Startup apps) and Resource Monitor to identify CPU, memory and disk bottlenecks',
            'Recognise a temporary-profile sign-in and escalate it without deleting profile data',
        ],
        'html': sme_note('Slow-logon diagnosis and resource tools added in pass 9.') + '''
<h3>Where does a slow logon spend its time?</h3>
<p>“Logging in takes ten minutes” is one symptom with several stages behind it. Time each stage instead of guessing.</p>
''' + table(['Stage', 'What slows it', 'Evidence'], [
            ['Before the password prompt', 'Network not ready, updates installing, policy for the computer', 'Watch the screen messages; System log; GroupPolicy Operational log'],
            ['Applying user policy', 'Logon scripts, drive mappings to servers that no longer exist, slow links', 'GroupPolicy Operational log records processing times; <code>gpresult /h report.html</code>'],
            ['Loading the profile', 'Large roaming profiles, folder redirection to a slow server', 'User Profile Service events in the Application log; profile size'],
            ['Desktop appears, then hangs', 'Startup apps, sync clients, security scans', 'Task Manager → Startup apps (Startup impact column); Processes tab right after sign-in'],
        ]) + '''
<h3>Reading the resource tools</h3>
<ul>
<li><strong>Task Manager</strong> (Ctrl + Shift + Esc): <em>Processes</em> sorts by CPU, memory, disk or network; <em>Performance</em>
shows the trend; <em>Startup apps</em> lists what starts at sign-in and its impact.</li>
<li><strong>Resource Monitor</strong> (<code>resmon</code>): the Disk tab shows which files each process is reading and writing and
the disk’s response time; the Memory tab shows hard faults per second, which climb when Windows is paging to disk because RAM is
short.</li>
<li><strong>Patterns:</strong> CPU pinned by one process — a runaway or a scan; memory that only grows over hours — a leak in the
process that grows; disk active time near 100 % with long response times — a slow or failing disk, or too much I/O at once.
Compare with the device’s baseline or a similar healthy PC before drawing conclusions.</li>
</ul>
<h3>Temporary profiles</h3>
<p>If Windows says “We can’t sign in to your account” or the desktop looks brand new, the user may be on a
<strong>temporary profile</strong>: changes are lost at sign-out. Do not delete the profile folder or edit the registry at tier 1 —
the user’s data is still in the original profile. Record the message, ask the user not to save work locally, and escalate to the
endpoint team, who can repair the profile and recover data.</p>
''' + figure('f11-4', 'Slow-logon stages', ['Computer\npolicy +\nnetwork', 'User policy:\nscripts,\ndrive maps', 'Profile\nload', 'Startup\napps', 'Desktop\nusable'],
             'Five boxes in order: computer policy and network start-up; user policy, including logon scripts and drive mappings; profile load; '
             'startup apps; desktop usable. Each stage has its own evidence — the GroupPolicy Operational log, User Profile Service events, '
             'and Task Manager’s Startup apps — so a slow logon can be timed stage by stage.', 'Time each stage; the slowest stage names the owner of the fix.', cols=5) + worked('the 6-minute logon', '''
<p>Evidence: the welcome screen sits on “Applying user settings” for five minutes. The GroupPolicy Operational log shows user
policy processing took about 300 seconds. <code>gpresult /h</code> lists a logon script that maps drive S: to
<code>\\\\oldfs01\\shared</code>. <code>Test-NetConnection oldfs01 -Port 445</code> fails: that server was retired last month.
Cause: the script waits for an unreachable server. Fix: the policy owner removes the old mapping (a change); verify by
signing in again — 40 seconds. Record the fix in the problem record, because every user with that policy was affected.</p>''') + cfu(
            ('Which log shows how long Group Policy took at a logon?',
             'Applications and Services Logs → Microsoft → Windows → GroupPolicy → Operational.'),
            ('Memory used by one process grows steadily for hours and never falls. What do you suspect?',
             'A memory leak in that process.'),
            ('A user lands on a temporary profile. What must you not do at tier 1?',
             'Delete the profile folder or edit the registry — escalate so the original profile and its data can be recovered.')),
    },
}

GLOSSARY = [
    ('Clean boot', 'Starting Windows with non-Microsoft services and startup apps disabled to find a software conflict.'),
    ('Safe Mode', 'A Windows start-up mode with a minimal set of drivers and services, reached from WinRE Startup Settings or msconfig.'),
    ('App repair / reset', 'Settings options for many apps: Repair fixes files and keeps data; Reset also clears the app’s data and settings.'),
    ('Memory leak', 'A program that keeps taking memory without releasing it, so its use grows until the system slows.'),
    ('Resource Monitor', 'A Windows tool (resmon) showing per-process CPU, memory, disk and network activity in detail.'),
    ('Temporary profile', 'A fallback profile Windows uses when the user’s profile cannot load; changes are lost at sign-out.'),
    ('Rebuild (reimage)', 'Replacing the operating system and apps with a standard image, then restoring the user’s data and settings.'),
]

PLAN = {
    'warmup': 'Show a Task Manager screenshot with one process at 100 % disk. Pairs write two theories and the next tool they would open.',
    'guided': 'Read the Application Error event together (11.1), then run a clean boot with halving on the lab VM. Finish with the slow-logon stage table and the 6-minute logon worked example.',
    'worked_example': 'Lesson 11.1 reading a crash event; 11.3 the 45-minute time box; 11.4 the 6-minute logon.',
    'cfu': ['Which event IDs mark an application crash and a hang?',
            'Why tick “Hide all Microsoft services” in a clean boot?',
            'Give two signs a rebuild beats more repair.',
            'Where is the time spent in a slow logon, and which log shows policy time?'],
    'exit_ticket': 'Write the time-boxed plan for “Excel crashes when I open one workbook” on one PC, including the point at which you would stop and escalate.',
    'misconceptions_add': ['“Reinstall the app first.” Scope it first: if it fails only for one profile, a reinstall changes the wrong thing.',
                           '“A temporary profile can be fixed by deleting the old one.” That can destroy the user’s data; escalate.'],
    'classroom_lab': 'CL-11',
    'materials_add': 'Classroom lab CL-11 (slow PC and clean-boot isolation).',
}

ITEMS = [
    item('IT-11.1', 1, 'Which Application-log event usually records a program crash, with the faulting module?',
         'Application Error, event ID 1000', ['Kernel-Power, event ID 41', 'Service Control Manager, event ID 7036', 'User Profile Service, ID 1530'],
         'Application Error 1000 names the faulting application and module; Kernel-Power 41 is an unexpected shutdown.'),
    item('IT-11.1', 2, 'An app fails for one user on every PC they use, but works for colleagues. What is the likely scope?',
         'That user’s account, licence or data', ['The network switch on that floor', 'The app’s installation on one PC', 'The printer driver on the print server'],
         'A fault that follows one user across devices, while others are fine, sits with the user’s account, licence or data.'),
    item('IT-11.1', 3, 'The same app crashes on 40 PCs since this morning’s update. What should the technician do?',
         'Raise a pattern to the app owner with the evidence', ['Reinstall the app on each of the PCs in turn today', 'Reset every user’s Windows profile at once', 'Ask users to restart until it stops crashing'],
         'A fleet-wide pattern after a change needs a problem record and the owner, not 40 individual repairs.'),
    item('IT-11.2', 1, 'In a clean boot, why do you tick “Hide all Microsoft services” before “Disable all”?',
         'So only third-party services are switched off', ['So Windows Update installs the latest patches first', 'So the test runs faster than in Safe Mode', 'So the PC restarts directly into Safe Mode'],
         'Windows’ own services stay on; the test removes third-party services that might conflict.'),
    item('IT-11.2', 2, 'A fault disappears in Safe Mode. What does that suggest?',
         'A driver, service or startup item is involved', ['The hard drive is about to fail completely soon', 'The user’s password needs to be reset now', 'The monitor cable is loose at the PC end'],
         'Safe Mode loads minimal drivers and services; if the fault goes, something it does not load is implicated.'),
    item('IT-11.2', 3, 'You started a PC in Safe Mode using msconfig. What must you do afterwards?',
         'Untick Safe boot so it starts normally again', ['Turn off System Restore to save disk space', 'Run sfc /scannow before the next restart', 'Disable the network adapter for safety'],
         'msconfig’s Safe boot persists until cleared; otherwise every restart returns to Safe Mode.'),
    item('IT-11.3', 1, 'After 45 minutes you have found several unrelated faults and unknown installs. What is usually best?',
         'Plan a rebuild with a verified backup and app list', ['Keep repairing until each of the faults is fixed in turn', 'Disable the antivirus to rule it out fully', 'Close the ticket and ask the user to retry'],
         'Several unrelated faults and unknown changes past the time box favour a planned rebuild.'),
    item('IT-11.3', 2, 'Which step must come first in a rebuild plan?',
         'Back up the user’s data and test the backup', ['Download the newest drivers for the device model', 'Book a meeting room for the change review', 'Order a replacement drive in case it fails'],
         'Data protection comes first; a backup is only trusted once a restore has been tested.'),
    item('IT-11.3', 3, 'Repair is past its time box and no documented fix exists, so a rebuild looks quicker. When is a rebuild still the wrong next step?',
         'When there is no tested backup of the user’s data', ['When the device is already on the standard image', 'When a spare device on the standard image is ready', 'When the user agrees to a time after 16:00'],
         'A rebuild wipes the disk, so without a tested backup it risks permanent loss of the user’s data: back up and test a restore first. Being on the standard image, having a ready spare and an agreed time after 16:00 all make a rebuild easier, not worse.'),  # content round 7 (Oct 24): removed the "documented vendor fix" distractor, which was a second defensible answer. Pending SME review
    item('IT-11.4', 1, 'Logon sits on “Applying user settings” for five minutes. Which evidence helps most?',
         'GroupPolicy Operational log and gpresult /h', ['The firmware event log and the boot order list', 'The printer queue and the spooler status', 'The Wi-Fi channel and the signal strength'],
         'User-policy delays (scripts, drive maps) show in the GroupPolicy Operational log and the gpresult report.'),
    item('IT-11.4', 2, 'One process’s memory use climbs steadily for hours and never drops. What is the likely problem?',
         'A memory leak in that process', ['A failing power supply unit', 'A DNS server that is too slow', 'A screen resolution mismatch'],
         'Steady growth without release is the signature of a leak in the growing process.'),
    item('IT-11.4', 3, 'A user signs in to a brand-new-looking desktop with a “can’t sign in to your account” notice. What do you do?',
         'Record it and escalate; do not delete the profile', ['Delete the old profile folder to force a full rebuild', 'Edit the ProfileList registry key yourself', 'Tell the user to keep working and save locally'],
         'A temporary profile loses changes; the original data must be recovered by the endpoint team, not deleted.'),
]

LABS = {
    'CL-11': {
        'id': 'CL-11', 'title': 'Slow PC & Clean-Boot Isolation', 'chapters': [('ITSUP', 11), ('CLIENT', 4)],
        'review': 'Pending SME review',
        'objective': 'Find the cause of a staged slowdown with Task Manager, Resource Monitor and a clean boot, and restore the configuration afterwards.',
        'scenario': 'The instructor has added a startup item and a background service to a Windows 11 lab VM that consume CPU or disk after sign-in.',
        'prerequisites': ['Lessons 11.1–11.4', 'A lab VM with a snapshot'],
        'equipment': 'Windows 11 lab VM with a snapshot; a small “load” utility or script provided by the instructor.',
        'low_cost': 'Use the LMS labs w11-processes and w11-services, and printed Task Manager and Resource Monitor screenshots for the analysis steps.',
        'steps': [
            'Sign in and time how long until the desktop is usable; record it.',
            'Task Manager → Processes: sort by CPU and Disk; record the top process and its values. Task Manager → Startup apps: record items with High impact.',
            'Resource Monitor → Disk: record which files the top process reads or writes and the disk response time.',
            'Plan a clean boot (record every item you will disable), then perform it with msconfig and Task Manager.',
            'Restart and re-time the sign-in. Then re-enable items in halves until the slowdown returns; record each step.',
            'Restore every item except the culprit, record the final change and re-time the sign-in.',
            'Write the ticket: evidence, cause, change, verification. Revert the VM to its snapshot.',
        ],
        'expected': 'The culprit is identified by halving in no more than four restarts; all other items are restored; sign-in time is measured before and after.',
        'troubleshooting': ['If the slowdown does not go away in the clean boot, the cause is in a Microsoft service, a driver or the hardware — try Safe Mode next.',
                            'If you lose track of what you disabled, revert to the snapshot and start again with a written list.'],
        'reflection': ['Which tool pointed at the culprit first?', 'How many restarts did halving take, and why is it at most four for sixteen items?',
                       'What would you check on a real user’s PC before running a clean boot?'],
        'rubric': 'lab', 'minutes': 60, 'objectives': ['IT-11.3', 'IT-11.4'],
    },
}
