"""ITSUP Chapter 9 — Linux, macOS & Cross-Platform Support (pass 9 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 9
SOURCES_USED = ['linux-man', 'apple-recovery']

LESSONS = {
    (9, 1): {
        'sources': ['linux-man'],
        'objectives': [
            'Navigate a Linux file system and collect support facts (user, host, addresses, routes, disk, memory) with standard commands',
            'Interpret a permission string such as -rw-r----- and set permissions with chmod in symbolic and octal form',
            'Manage a service with systemctl (status, start, restart) and read its log with journalctl',
            'Record every sudo command in the ticket as a change',
        ],
        'html': sme_note() + '''
<h3>The same inventory habit, different spelling</h3>
<p>Linux runs servers, network appliances, lab machines and many developer laptops. You do not need to be a Linux
administrator for first-line support, but you do need to collect facts safely and recognise when a fix needs someone with
more access. The commands below read the system; none of them change it.</p>
''' + table(['Question', 'Linux', 'Windows equivalent'], [
            ['Who am I, and on which host?', '<code>whoami</code>, <code>hostname</code>', '<code>whoami</code>, <code>hostname</code>'],
            ['What are my IP addresses?', '<code>ip addr</code> (short: <code>ip a</code>)', '<code>ipconfig /all</code>'],
            ['What is my default gateway?', '<code>ip route</code> (look for <code>default via</code>)', '<code>route print</code> / <code>ipconfig</code>'],
            ['Which DNS servers do I use?', '<code>resolvectl status</code> on systemd-resolved systems, or read <code>/etc/resolv.conf</code>', '<code>ipconfig /all</code>'],
            ['What is listening on which port?', '<code>ss -tulpn</code>', '<code>netstat -ano</code>'],
            ['How full are the disks?', '<code>df -h</code>; folder sizes with <code>du -sh *</code>', 'File Explorer; <code>Get-PSDrive</code>'],
            ['How much memory is free?', '<code>free -h</code>; live view <code>top</code>', 'Task Manager'],
            ['Is a service running?', '<code>systemctl status &lt;name&gt;</code>', '<code>Get-Service &lt;name&gt;</code>'],
        ]) + '''
<p>Paths start at <code>/</code> (the root). <code>pwd</code> prints where you are, <code>ls -l</code> lists files with
details, <code>cd</code> moves, <code>cat</code> and <code>less</code> show a file, and <code>grep</code> finds text in files or
in another command’s output (for example <code>journalctl -b | grep -i error</code>). File and command names are
case-sensitive: <code>Report.txt</code> and <code>report.txt</code> are two different files.</p>
<h3>Reading and changing permissions</h3>
<p>Every file has an owner, a group and permissions for three classes: the owner (u), the group (g) and everyone else (o). Each
class can read (r), write (w) and execute (x). <code>ls -l</code> shows them as a ten-character string.</p>
''' + figure('f9-1', 'Reading a Linux permission string', ['-\nfile type', 'rw-\nowner', 'r--\ngroup', '---\nothers', '= 640\n(octal)'],
             'The permission string -rw-r----- split into five parts. The first character, a dash, means a regular file (d would mean a '
             'directory). The next three, rw-, give the owner read and write. The next three, r--, give the group read only. The last three, '
             'dashes, give everyone else nothing. Adding r=4, w=2, x=1 for each class gives the octal form 640.',
             'Each class gets three bits; add r = 4, w = 2 and x = 1 to get the octal digit for that class.', cols=5) + '''
<p>Change permissions with <code>chmod</code>, either symbolically (<code>chmod o-r notes.txt</code> removes read for others;
<code>chmod u+x run.sh</code> lets the owner execute a script) or in octal (<code>chmod 640 notes.txt</code>). Change the owner
with <code>chown user:group file</code>, which needs administrative rights. On a directory, x means “may enter”, so a folder
set to 644 cannot be opened even by its owner.</p>
<h3>sudo, services and logs</h3>
<p><code>sudo</code> runs one command with administrative (root) rights and records it in the system’s logs. Treat every sudo
command as a change: write it in the ticket with its result. Services are managed with systemd on most current distributions:
<code>systemctl status ssh</code> shows state and the last log lines; <code>sudo systemctl restart ssh</code> restarts it;
<code>journalctl -u ssh -b</code> shows that service’s log since the last boot. Software is installed with the distribution’s
package manager — <code>apt</code> on Debian and Ubuntu, <code>dnf</code> on Fedora and Red Hat-family systems — never by
downloading random scripts.</p>
''' + worked('“the web app on the lab server is down”', '''
<pre><code>$ systemctl status nginx
● nginx.service - A high performance web server
     Active: failed (Result: exit-code) since Tue 09:12
$ journalctl -u nginx -b | tail -5
nginx: [emerg] open() "/etc/nginx/conf.d/site.conf" failed (13: Permission denied)
$ ls -l /etc/nginx/conf.d/site.conf
-rw------- 1 alex alex 812 Oct 14 09:05 site.conf</code></pre>
<p>Reading the evidence: the service failed at 09:12; the log says it could not open its config file; the file was edited at 09:05
by user alex and is now readable only by alex (600), so the web server cannot read it. Ticket: “nginx failed 09:12 — config
file permissions changed to 600 at 09:05 (owner alex). Escalated to the server owner to restore ownership and mode, then
restart.” You found the cause without changing anything.</p>''') + cfu(
            ('What does the permission string drwxr-x--- tell you?',
             'A directory; owner can read, write and enter; group can read and enter; others have no access (octal 750).'),
            ('Which command shows the default gateway on Linux?',
             'ip route — the line beginning “default via”.'),
            ('Why record sudo commands in the ticket?',
             'They run with root rights and change the system; another technician must be able to see and undo them.')),
    },
    (9, 2): {
        'sources': ['apple-recovery'],
        'objectives': [
            'Collect a Mac’s model, chip, serial number and macOS version before troubleshooting or ordering parts',
            'Use Activity Monitor, Disk Utility First Aid and Console to gather evidence on a slow or failing Mac',
            'Explain FileVault, Time Machine and macOS Recovery, and when each is needed',
            'Identify whether a Mac is enrolled in MDM and route policy questions to the device owner',
        ],
        'html': sme_note() + '''
<h3>Where things are on a Mac</h3>
<p>A Mac is still processor, memory, storage and network, with a different settings app. Settings live in
<strong>System Settings</strong> (called System Preferences on older versions of macOS). Collect the basics before anything else:
<em>Apple menu → About This Mac</em> shows the chip (Apple silicon such as M-series, or Intel), memory, serial number and macOS
version. Part orders and repair options depend on that model, and Apple silicon and Intel Macs start up and recover differently.</p>
''' + table(['Need', 'macOS tool', 'Windows equivalent'], [
            ['What is using the CPU, memory, energy, disk or network?', 'Activity Monitor (Applications → Utilities)', 'Task Manager'],
            ['Check and repair a disk or volume', 'Disk Utility → First Aid', '<code>chkdsk</code>'],
            ['System and app logs, crash reports', 'Console', 'Event Viewer'],
            ['Command line', 'Terminal (default shell: zsh)', 'Windows Terminal / PowerShell'],
            ['IP address and DNS', 'System Settings → Network → (service) → Details; <code>ipconfig getifaddr en0</code>; <code>scutil --dns</code>', '<code>ipconfig /all</code>'],
            ['Disk encryption', 'FileVault (System Settings → Privacy &amp; Security)', 'BitLocker / Device encryption'],
            ['Backup', 'Time Machine', 'File History / Windows Backup'],
            ['Recovery', 'macOS Recovery', 'WinRE'],
        ]) + '''
<h3>Recovery, encryption and backup</h3>
<ul>
<li><strong>macOS Recovery</strong> offers Disk Utility, reinstalling macOS, restoring from Time Machine and a Terminal. On a Mac
with Apple silicon, shut it down, then press and hold the power button until “Loading startup options” appears, choose
Options and Continue. On an Intel Mac, hold Command (⌘)-R while it starts. Recovery may ask for an administrator’s password.</li>
<li><strong>FileVault</strong> encrypts the startup disk. Its recovery key may be stored with the user’s Apple Account or, on
managed Macs, escrowed in the organisation’s MDM. As with BitLocker, find out where the key is before any recovery work.</li>
<li><strong>Time Machine</strong> keeps hourly, daily and weekly backups on an external disk or network destination. Confirm the
date of the last backup in its settings before you reinstall anything.</li>
</ul>
<h3>Managed Macs</h3>
<p>Organisation-owned Macs are usually enrolled in <strong>mobile device management (MDM)</strong>, often automatically through
Apple Business Manager or Apple School Manager. Look in System Settings → General → Device Management (or Privacy &amp; Security
→ Profiles on older versions) for the organisation’s profiles. MDM may enforce FileVault, restrict apps and install
certificates for Wi-Fi and email. Removing profiles to “fix” a problem bypasses policy and is not a help-desk decision;
<strong>Activation Lock</strong>, tied to an Apple Account, can also make a wiped Mac unusable until the right account or the
organisation releases it.</p>
''' + worked('“my Mac is really slow”', '''
<ol>
<li>About This Mac: MacBook Air, Apple M-series chip, 8 GB memory, current macOS. Managed by the college (Device Management shows
the college profile).</li>
<li>Activity Monitor → Memory tab: memory pressure graph is red; a browser with 60 tabs uses most of the memory; swap used is high.</li>
<li>Activity Monitor → CPU: nothing unusual. Disk Utility First Aid on the startup volume: no errors.</li>
<li>Cause: memory pressure from the browser workload. Fix agreed with the user: close unused tabs, enable the browser’s memory
saver; verify after a day of normal use. Record that 8 GB is tight for this workload in case a hardware request follows.</li>
</ol>''') + cfu(
            ('Where do you find a Mac’s chip, serial number and macOS version?',
             'Apple menu → About This Mac.'),
            ('How do you start an Apple silicon Mac in macOS Recovery?',
             'Shut down, press and hold the power button until startup options load, then choose Options → Continue.'),
            ('A user wants you to remove the college’s profile because it blocks an app. What do you do?',
             'Decline and route the request to the device-management owner; removing MDM profiles bypasses policy.')),
    },
    (9, 3): {
        'objectives': [
            'Distinguish an entitlement (access) problem from a technical fault by testing the same resource with another account and another device',
            'Identify the identity source (local, directory, cloud) that controls access to a resource in a mixed environment',
            'Route access requests to the resource owner with the evidence they need, without sharing or recording credentials',
        ],
        'html': sme_note() + '''
<h3>“I can’t get to it” has two very different meanings</h3>
<p>In a mixed Windows, macOS and Linux environment, the same symptom — “I can’t open the shared folder” — can be a technical
fault (the server is down, the path is wrong, the network blocks the port) or an <strong>entitlement</strong> problem (the user
has never been given access, or lost it in a role change). The fixes are owned by different people, so separate them early.</p>
''' + table(['Test', 'Result', 'Points to'], [
            ['Same user, another device', 'Also fails', 'The account or its access (entitlement), or the resource itself'],
            ['Another user with known access, same device', 'Works', 'The original user’s entitlement — not the device or network'],
            ['Same user, resource by IP or full path', 'Works', 'Name resolution or a mapped-drive or shortcut problem'],
            ['Anyone, the resource’s port', 'Port closed (for example SMB 445 or SSH 22)', 'Server, firewall or network — technical fault'],
            ['The error text', '“Access is denied” / “You do not have permission”', 'Entitlement, not connectivity'],
        ]) + '''
<h3>Who controls access?</h3>
<p>Access is decided by an <strong>identity source</strong>: a local account on one machine; a directory such as Active Directory;
or a cloud identity provider such as Microsoft Entra ID or Google Workspace. Macs and Linux machines in an organisation are
often connected to the same directory or cloud identity as the Windows PCs. Group membership in that identity source usually
grants access to shares, apps and printers — which is why the fix for an entitlement problem is a request to the resource
owner or identity team, approved by the user’s manager, not a setting on the user’s device.</p>
''' + figure('f9-3', 'Separating entitlement from technical faults', ['“Can’t open\nthe share”', 'Other user\nworks?', 'Yes: access\nrequest to\nresource owner', 'No: test path,\nname, port', 'Technical fault\n→ owning team'],
             'Five boxes. The symptom “can’t open the share” leads to the test “does another user with known access succeed from the same '
             'device?” If yes, the problem is the original user’s entitlement and becomes an access request to the resource owner. If no, test '
             'the path, name resolution and the port; a failure there is a technical fault for the owning team.',
             'One comparison with a user who has access usually tells you whether you have an access request or a fault.', cols=5) + worked('Mac user, Windows share', '''
<p>A designer on a Mac cannot open <code>smb://files.example.edu/budget</code>; a colleague on Windows opens
<code>\\\\files.example.edu\\budget</code> fine. Tests: the designer can open a different share on the same server (so the
server, name and port work); the error is “You do not have permission to access this server”; the designer joined the team last
week. Conclusion: entitlement. Ticket: service request to the share owner with the designer’s account name, the share path and
the manager’s approval. You did not ask for, record or type the designer’s password at any point.</p>''') + cfu(
            ('Another user opens the share from the same Mac. What does that rule out?',
             'The Mac, the network path and the server — the original user’s access is the likely problem.'),
            ('Name three identity sources that can control access.',
             'A local account, a directory such as Active Directory, or a cloud identity provider such as Microsoft Entra ID or Google Workspace.'),
            ('Why must a ticket never contain the user’s password?',
             'Tickets are read by many people and kept for years; a recorded password is a credential leak.')),
    },
    (9, 4): {
        'objectives': [
            'Select a file system (NTFS, APFS, ext4, exFAT, FAT32) that every system in a scenario can read and write',
            'Connect to shared folders from Windows, macOS and Linux using SMB paths and identify SSH as the common remote shell',
            'Explain cross-platform pitfalls — case sensitivity, line endings, file-size limits and permissions — and work around them',
            'Write one intake for a mixed-environment ticket that names the operating system and the outcome',
        ],
        'html': sme_note('Cross-platform file systems and sharing added in pass 9 (objective IT-9.4).') + '''
<h3>Which file system can everyone use?</h3>
''' + table(['File system', 'Native to', 'Windows', 'macOS', 'Linux', 'Notes'], [
            ['NTFS', 'Windows', 'Read/write', 'Read only (no native write)', 'Read/write with the ntfs3 or ntfs-3g driver', 'Permissions, journaling, large files'],
            ['APFS', 'macOS', 'Not readable natively', 'Read/write', 'Limited third-party support', 'Default for Mac startup disks; encryption and snapshots'],
            ['ext4', 'Linux', 'Not readable natively (WSL can mount)', 'Not readable natively', 'Read/write', 'Default on many distributions'],
            ['exFAT', 'Cross-platform', 'Read/write', 'Read/write', 'Read/write', 'Best for USB drives shared between systems; no permissions or journaling'],
            ['FAT32', 'Legacy', 'Read/write', 'Read/write', 'Read/write', 'Maximum file size 4 GB — large videos and disk images fail'],
        ]) + '''
<p>For a USB drive that moves between a Mac, a Windows PC and a Linux lab machine, exFAT is the usual answer. Warn the user that
exFAT has no journaling: always eject the drive before unplugging it, or recent writes can be lost.</p>
<h3>Sharing over the network</h3>
<ul>
<li><strong>SMB</strong> (TCP 445) is the common file-sharing protocol. Windows: <code>\\\\server\\share</code> in File Explorer.
macOS: Finder → Go → Connect to Server → <code>smb://server/share</code>. Linux: the file manager’s “Connect to server” with
<code>smb://server/share</code>, or <code>smbclient</code> / a CIFS mount on the command line.</li>
<li><strong>SSH</strong> (TCP 22) gives a remote shell and, with <code>scp</code> or <code>sftp</code>, file transfer. An OpenSSH
client is built into current Windows, macOS and Linux, so <code>ssh user@host</code> works on all three.</li>
<li><strong>Cloud storage</strong> (OneDrive, Google Drive, institutional storage) avoids most file-system issues but brings
sharing permissions and sync conflicts of its own.</li>
</ul>
<h3>Pitfalls that look like faults</h3>
''' + table(['Pitfall', 'What the user sees', 'Fix or workaround'], [
            ['Case sensitivity', 'Two files “Report.txt” and “report.txt” on a Linux share; one disappears or conflicts on Windows', 'Agree a naming convention; rename on the Linux side'],
            ['Line endings', 'A script written on Windows fails on Linux with “bad interpreter” or ^M characters', 'Save with LF line endings, or convert with the editor or dos2unix'],
            ['File-size limit', '“File too large” copying a 6 GB video to a USB stick', 'The stick is FAT32; reformat as exFAT after backing up its contents'],
            ['Permissions', 'Files copied from Linux arrive read-only or with odd owners', 'Set permissions on the destination; check share permissions, not just file modes'],
            ['Reserved names and characters', 'A file named “aux.txt” or containing “:” cannot be copied to Windows', 'Rename at the source'],
        ]) + worked('the intake for a mixed-environment ticket', '''
<p>“OS: macOS (managed MacBook Pro, Apple silicon). User: j.lee (signed in, Apple Account and college account). Outcome: cannot copy a
6.2 GB project video to the shared USB drive for the Windows editing PC. Error: ‘The item can’t be copied because it’s too large
for the volume’s format.’ Drive: 64 GB, FAT32 (Disk Utility). Request vs fault: fault caused by format. Plan: back up the drive’s
contents, reformat as exFAT with the user’s agreement, copy back, test on both machines.”</p>''') + scenario('the disappearing file', '''
<p>A research group keeps data on a Linux server shared over SMB. A Windows user reports that “results.csv keeps changing to old
numbers”. Investigation shows two files on the server, <code>results.csv</code> and <code>Results.csv</code>, written by
different scripts. Windows, which treats names case-insensitively by default, shows only one of them. The fix was a naming
rule in the scripts and a merge by the data owner — not a Windows repair.</p>''') + cfu(
            ('Which file system lets a USB drive be read and written by Windows, macOS and Linux without extra drivers?',
             'exFAT (FAT32 also works but limits files to 4 GB).'),
            ('How does a Mac user connect to a Windows share?',
             'Finder → Go → Connect to Server → smb://server/share.'),
            ('A script from a Windows PC fails on Linux with “bad interpreter”. What do you suspect?',
             'Windows (CRLF) line endings; save or convert the file with LF endings.')),
    },
}

GLOSSARY = [
    ('chmod', 'The Linux and macOS command that changes file permissions, in symbolic (u+x) or octal (640) form.'),
    ('sudo', 'Runs a single command with administrative (root) rights and logs it; every use is a change to record.'),
    ('systemctl / journalctl', 'systemd commands to manage services and read their logs on most current Linux distributions.'),
    ('macOS Recovery', 'The Mac recovery system (Disk Utility, reinstall macOS, Time Machine restore, Terminal).'),
    ('FileVault', 'macOS full-disk encryption of the startup disk; its recovery key may be held by the user’s account or the organisation’s MDM.'),
    ('Time Machine', 'The built-in macOS backup tool, keeping hourly, daily and weekly copies on an external or network disk.'),
    ('exFAT', 'A file system read and written natively by Windows, macOS and Linux; suited to removable drives; no journaling.'),
    ('SMB', 'Server Message Block (TCP 445), the common file- and printer-sharing protocol used by Windows, macOS and Linux.'),
    ('Entitlement', 'The access a user has been granted to a resource, usually through group membership in an identity source.'),
    ('Identity source', 'The system that authenticates users and holds group membership: a local account database, a directory, or a cloud identity provider.'),
]

PLAN = {
    'warmup': 'Show -rw-r----- on the board. Pairs decode it and write the octal value before anyone explains it.',
    'guided': 'Linux fact-collection worksheet (CL-9) side by side with the Windows commands; then the nginx worked example read line by line. Close with the file-system table: which format for a shared USB drive?',
    'worked_example': 'Lesson 9.1 “web app is down” (systemctl, journalctl, ls -l); 9.2 slow Mac in Activity Monitor; 9.3 Mac user and a Windows share; 9.4 mixed-environment intake.',
    'cfu': ['Decode drwxr-x--- and give its octal value.',
            'How do you start an Apple silicon Mac in macOS Recovery?',
            'Another user opens the share from the same Mac — what does that rule out?',
            'Which file system suits a USB drive shared by Windows, macOS and Linux?'],
    'exit_ticket': 'Write an intake note for: “Mac user cannot copy a 6 GB video to the USB drive used by the Windows edit PC.”',
    'misconceptions_add': ['“FAT32 works everywhere, so it is the safe choice.” It cannot hold files over 4 GB; exFAT is the usual cross-platform format.',
                           '“Removing the MDM profile is a quick fix.” It bypasses policy and may remove Wi-Fi and email access; route it to the owner.'],
    'classroom_lab': 'CL-9',
    'materials_add': 'Classroom lab CL-9 with the cross-platform extension steps (exFAT drive, smb:// connection).',
}

ITEMS = [
    item('IT-9.1', 1, 'A file shows -rw-r----- in ls -l. What can members of the file’s group do?',
         'Read the file but not change it', ['Read, change and execute the file', 'Nothing, because only the owner has rights', 'Execute it as a program but not read it'],
         'The middle triplet r-- gives the group read only; the owner has rw-, others ---.'),
    item('IT-9.1', 2, 'Which command shows why a Linux service failed, from its own log since the last boot?',
         'journalctl -u nginx -b', ['ip route show default', 'chmod 640 /var/log/syslog', 'systemctl list-timers --all'],
         'journalctl -u filters the systemd journal by unit; -b limits it to the current boot.'),
    item('IT-9.1', 3, 'Which octal mode gives the owner read/write, the group read, and others no access?',
         '640', ['755', '600', '664'],
         'Owner rw = 4+2 = 6, group r = 4, others 0: 640.'),
    item('IT-9.2', 1, 'How do you start a Mac with Apple silicon in macOS Recovery?',
         'Hold the power button until startup options appear', ['Hold Command-R as soon as you hear the startup chime', 'Press F8 repeatedly while the Apple logo is showing', 'Hold Shift and choose Restart from the Apple menu'],
         'Apple silicon Macs use the held power button and Options; Command-R applies to Intel Macs; F8 is a Windows habit.'),
    item('IT-9.2', 2, 'A MacBook’s battery is draining quickly. In Activity Monitor, which tab shows which apps have the highest energy impact?',
         'Energy', ['Disk', 'Network', 'Memory'],
         'The Energy tab lists Energy Impact per app; Disk, Network and Memory show other resources.'),
    # spot-check round 3 (Oct 18 2026, Pending SME review): "their Mac" read as a personally owned Mac, which made "the
    # device owner" the user; the stem now says the Mac is college-owned and the rationale names the owner. Key unchanged.
    item('IT-9.2', 3, 'A user asks you to remove the management profile from the college-owned Mac they use, because it blocks an app. What do you do?',
         'Decline and send the request to the device owner', ['Remove it, then reinstall it after the app is set up', 'Wipe the Mac so that the profile is cleared away', 'Turn off FileVault so the app can be installed'],
         'MDM profiles enforce organisation policy; changing them is the device owner’s decision, and here the owner is the college.'),
    item('IT-9.3', 1, 'A user cannot open a share, but a colleague opens it from the same device. What is most likely?',
         'The user lacks access to that share', ['The device’s network adapter is faulty', 'The file server is offline for everyone', 'DNS cannot resolve the server’s name'],
         'Success for another user on the same device rules out the device, network and server; entitlement remains.'),
    item('IT-9.3', 2, 'A new team member gets “You do not have permission to access this server”. How should the ticket be handled?',
         'As an access request to the resource owner', ['As a network fault for the campus switch team', 'As a hardware fault on the user’s laptop', 'As a password reset for the user account'],
         'Permission errors for a new starter are entitlement requests, approved and granted by the owner.'),
    item('IT-9.3', 3, 'What should you do with a user’s password during an access ticket?',
         'Never ask for it, type it or record it', ['Record it so tier 2 can sign in as them', 'Ask for it so you can test the share for them', 'Store it in the ticket’s private notes field'],
         'Credentials are never shared with or stored by support; test with your own permitted accounts.'),
    item('IT-9.4', 1, 'A USB drive must be read and written on Windows, macOS and Linux and hold 6 GB files. Which format fits?',
         'exFAT', ['FAT32', 'APFS', 'ext4'],
         'exFAT is read/write out of the box on current Windows, macOS and Linux (in-kernel driver since Linux 5.7) and has no 4 GB file limit; FAT32 limits files to 4 GB.'),
    item('IT-9.4', 2, 'How does a Mac user connect to the Windows share \\\\files\\budget?',
         'Finder → Go → Connect to Server → smb://files/budget', ['System Settings → Network → Add Server → files/budget', 'Terminal: ping files, then open the result list', 'Disk Utility → File → New Image → files/budget'],
         'macOS connects to SMB shares with smb:// URLs from Finder’s Connect to Server.'),
    item('IT-9.4', 3, 'A shell script written on Windows fails on Linux with “bad interpreter”. What is the most likely cause?',
         'Windows line endings in the script file', ['The Linux server’s clock is set wrongly', 'The script is stored on an exFAT USB drive', 'The user’s DNS suffix is not configured'],
         'CRLF line endings make the interpreter line invalid; save or convert the file with LF endings.'),
]
