"""A+ Core 2 1.8 (macOS) and 1.9 (Linux) — ITSUP 9.2 and 9.1."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_MAC = figure(
    'fig-c-macos', 'Where a macOS support task starts',
    ['Install / remove:\n.dmg .pkg .app', 'System Settings\n(Apple Account, MDM)', 'Protect: FileVault,\nTime Machine', 'Find and switch:\nSpotlight, Mission Control', 'Fix: Disk Utility,\nForce Quit, Terminal'],
    'Five boxes. Install software from the App Store, from a .dmg disk image (drag the .app into Applications) or a .pkg '
    'installer; remove it by dragging the app to the Trash (the Bin in UK English) or with the vendor’s uninstaller. System Settings holds the Apple Account, '
    'device-management profiles and Software Update. Protect data with FileVault encryption and Time Machine backups. Find files '
    'with Spotlight and switch between desktops with Mission Control. Repair with Disk Utility First Aid, Force Quit for a hung app, '
    'and Terminal for command-line work.',
    'Most macOS tickets start in one of five places: installing, settings, protection, finding things, or repair.', cols=5)

HTML_MAC = ('\n<p>Core 2 1.8 covers the features and tools of macOS a support technician uses.</p>\n<h4>Installing and removing apps</h4>\n<ul>\n<li><strong>App Store</strong> — signed apps, updated through the store.</li>\n<li><strong>.dmg</strong> — a disk image: open it, drag the <strong>.app</strong> bundle into <code>/Applications</code>, then eject the image.</li>\n<li><strong>.pkg</strong> — an installer package that can place files in several locations (drivers, helpers).</li>\n<li><strong>Uninstallation</strong> — drag the app from Applications to the Trash; apps installed by a .pkg may need the vendor’s uninstaller to remove helpers.</li>\n</ul>\n<p><strong>System folders:</strong> <code>/Applications</code> (apps for all users), <code>/Users</code> (home folders),\n<code>/Library</code> (shared support files and preferences) and <code>/System</code> (the protected operating system).</p>\n<h4>Settings, accounts and updates</h4>\n<ul>\n<li><strong>System Settings</strong> (System Preferences before macOS 13 Ventura) — Apple Account (Apple ID), network, displays, privacy and security.</li>\n<li><strong>Corporate restrictions</strong> — an organisation’s device-management (MDM) profile can enforce passcodes, restrict settings and install apps.</li>\n<li><strong>Updates</strong> — General → Software Update. Apple’s exam-era term <strong>Rapid Security Responses (RSR)</strong> delivered urgent\nfixes between updates; from macOS 26.1 these are called <strong>Background Security Improvements</strong> and are managed in Privacy &amp; Security.</li>\n<li><strong>Antivirus</strong> — macOS includes <strong>XProtect</strong>, which detects and removes known malware using signatures Apple updates in the background; organisations may add a managed anti-malware or EDR agent.</li>\n</ul>\n<h4>Protecting data</h4>\n<ul>\n<li><strong>Time Machine</strong> — automatic backups to an external disk or network volume; restore single files or the whole Mac.</li>\n<li><strong>FileVault</strong> — full-disk encryption; keep the recovery key in a safe place (or escrowed by MDM).</li>\n<li><strong>Keychain</strong> — stores passwords, certificates and keys (Keychain Access; the Passwords app in newer versions); <strong>iCloud</strong> can sync it.</li>\n</ul>\n<h4>Getting around</h4>\n<p><strong>Finder</strong> (file manager), the <strong>Dock</strong> (launch and switch apps), <strong>Spotlight</strong>\n(<kbd>⌘</kbd>+<kbd>Space</kbd>, search everything), <strong>Mission Control</strong> and <strong>multiple desktops</strong>\n(Spaces), trackpad <strong>gestures</strong>, and <strong>Continuity</strong> features between Apple devices (Handoff,\nAirDrop, Universal Clipboard).</p>\n<h4>Repair tools</h4>\n<p><strong>Disk Utility</strong> (First Aid checks and repairs a volume; erase and format), <strong>Force Quit</strong>\n(<kbd>⌥</kbd>+<kbd>⌘</kbd>+<kbd>Esc</kbd>), <strong>Terminal</strong> (zsh shell), and Activity Monitor (the Task Manager equivalent).</p>\n' + str(_FIG_MAC) + '\n' + str(worked('an app that will not uninstall cleanly', '''<ol>
<li>A VPN client was removed by dragging it to the Trash, but its menu-bar item still appears after restart.</li>
<li>It was installed from a .pkg, which also installed a helper and a network extension outside /Applications.</li>
<li>Download the vendor’s uninstaller (or run the uninstall script the vendor documents) and run it with administrator rights.</li>
<li>System Settings → General → Login Items &amp; Extensions: confirm nothing from the vendor remains. Restart and check again.</li></ol>''')) + '\n' + str(scenario('the Mac that would not take the update', '''<p>A designer’s Mac says it is up to date, but the security team reports it is missing a fix. Software Update’s
automatic options have been turned off, and the Mac also has an MDM profile from a previous employer. The technician removes the
old profile with the user’s permission, enrols the Mac in the company’s MDM, turns automatic security updates back on and installs
the pending update. FileVault and Time Machine are checked before the update, so the user’s work is protected.</p>''')) + '\n' + str(cfu(('How do you install an app delivered as a .dmg?', 'Open the image, drag the .app into Applications, then eject the image.'),
     ('Which macOS feature encrypts the whole startup disk?', 'FileVault.'),
     ('What is the macOS shortcut for Force Quit?', 'Option-Command-Escape.'))) + '\n')

_FIG_LNX = figure(
    'fig-c-linux', 'A Linux client from boot to shell',
    ['Firmware', 'Bootloader\n(GRUB)', 'Kernel', 'systemd\n(services)', 'Login and shell\n(bash)'],
    'Five boxes in a chain. The firmware starts the bootloader, usually GRUB, which loads the Linux kernel. The kernel starts '
    'systemd, the init system, which mounts the file systems listed in /etc/fstab and starts services. The user then signs in '
    'and works in a shell such as bash. Account details live in /etc/passwd and password hashes in /etc/shadow.',
    'Know the chain: a problem before the kernel is a bootloader issue; after it, check systemd services and /etc/fstab.', cols=5)

HTML_LNX = ('\n<p>Core 2 1.9 lists the Linux commands and files a desktop technician should recognise.</p>\n<table class="ref-table"><thead><tr><th scope="col">Task</th><th scope="col">Commands</th></tr></thead><tbody>\n<tr><td>Files and folders</td><td><code>ls</code> (list), <code>pwd</code> (current folder), <code>cd</code>, <code>mv</code> (move or rename), <code>cp</code> (copy), <code>rm</code> (remove — there is no recycle bin), <code>cat</code> (show a file), <code>nano</code> (simple text editor)</td></tr>\n<tr><td>Permissions and ownership</td><td><code>chmod</code> (change permissions, e.g. <code>chmod 750 script.sh</code>), <code>chown</code> (change owner)</td></tr>\n<tr><td>Search</td><td><code>grep</code> (text in files), <code>find</code> (files by name, size or age)</td></tr>\n<tr><td>Disks</td><td><code>df</code> (free space per file system), <code>du</code> (space used by a folder), <code>mount</code>, <code>fsck</code> (check and repair an <em>unmounted</em> file system)</td></tr>\n<tr><td>Administration</td><td><code>sudo</code> (run one command as root, logged), <code>su</code> (switch user, often to root); package managers <code>apt</code> (Debian, Ubuntu) and <code>dnf</code> (Fedora, Red Hat)</td></tr>\n<tr><td>Processes</td><td><code>ps</code> (snapshot of processes), <code>top</code> (live view)</td></tr>\n<tr><td>Network</td><td><code>ip a</code> / <code>ip route</code>, <code>ping</code>, <code>curl</code> (fetch a URL), <code>dig</code> (DNS query), <code>traceroute</code></td></tr>\n<tr><td>Help</td><td><code>man</code> (manual page for a command)</td></tr>\n</tbody></table>\n<h4>Important files</h4>\n<ul>\n<li><code>/etc/passwd</code> — user accounts (name, ID, home folder, shell); readable by everyone, so it holds no passwords.</li>\n<li><code>/etc/shadow</code> — password hashes and ageing; readable only by root.</li>\n<li><code>/etc/hosts</code> — local name-to-address entries, checked before DNS by default.</li>\n<li><code>/etc/fstab</code> — file systems to mount at boot. A mistake here can stop the system booting normally.</li>\n<li><code>/etc/resolv.conf</code> — DNS servers the resolver uses (often managed by a service such as systemd-resolved).</li>\n</ul>\n<p><strong>OS components:</strong> the <strong>kernel</strong> (manages hardware, memory and processes), the\n<strong>bootloader</strong> (GRUB), and <strong>systemd</strong> (starts and supervises services: <code>systemctl status ssh</code>).\nThe <strong>root account</strong> has full control; daily work uses a normal account and <code>sudo</code> when needed.</p>\n' + str(_FIG_LNX) + '\n' + str(worked('“disk full” on a Linux workstation', '''<ol>
<li><code>df -h</code> shows <code>/</code> at 100%.</li>
<li><code>sudo du -sh /var/* | sort -h</code> shows <code>/var/log</code> using most of it.</li>
<li><code>ls -lh /var/log</code> finds one very large log; <code>sudo tail /var/log/…</code> shows an application logging the same error every second.</li>
<li>Fix the application’s error, then rotate or truncate the log with the distribution’s tools rather than deleting files at random with <code>rm</code>.</li>
<li><code>df -h</code> again to confirm the free space, and note the cause on the ticket.</li></ol>''')) + '\n' + str(scenario('the workstation that booted to an emergency shell', '''<p>After a technician added a network share to <code>/etc/fstab</code>, a Linux workstation boots to an emergency
shell. The new line has a typing error in the server name, and the share is not marked as optional, so the boot waits on it and
fails. From the emergency shell the technician remounts the root file system read-write, comments out the line with
<code>nano</code>, and reboots. The corrected entry is tested with <code>sudo mount -a</code> <em>before</em> the next reboot.</p>''')) + '\n' + str(cfu(('Which file holds password hashes on Linux, and who can read it?', '/etc/shadow; only root.'),
     ('What is the difference between sudo and su?', 'sudo runs one command with elevated rights and logs it; su switches to another user (often root) for a whole shell.'),
     ('Why run fsck only on an unmounted file system?', 'Repairing a mounted, changing file system can corrupt it.'))) + '\n')

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 9, 'lesson': 2, 'id': 'cert-macos', 'title': 'macOS features and tools',
     'cert': ['A2:1.8'], 'html': sme_note('macOS features and tools (Core 2 1.8).') + HTML_MAC, 'sources': ['apple-macos-guide', 'apple-platsec', 'apple-bsi']},
    {'course': 'ITSUP', 'chapter': 9, 'lesson': 1, 'id': 'cert-linux', 'title': 'Linux commands, key files and OS components',
     'cert': ['A2:1.9'], 'html': sme_note('Linux client commands, configuration files and components (Core 2 1.9).') + HTML_LNX, 'sources': ['linux-man', 'fhs3', 'gnu-bash']},
]

GLOSSARY = [
    ('.dmg', 'macOS disk image used to distribute apps; the .app inside is dragged to Applications.'),
    ('.pkg', 'macOS installer package that can place files in several system locations.'),
    ('FileVault', 'macOS full-disk encryption.'),
    ('Time Machine', 'macOS built-in backup to an external or network disk.'),
    ('XProtect', 'macOS built-in signature-based malware detection and removal.'),
    ('Mission Control', 'macOS overview of open windows and desktops (Spaces).'),
    ('/etc/shadow', 'Linux file holding password hashes; readable only by root.'),
    ('/etc/fstab', 'Linux file listing the file systems to mount at boot.'),
    ('GRUB', 'Common Linux bootloader, which loads the kernel.'),
    ('systemd', 'Linux init system and service manager (systemctl).'),
]

ITEMS = [
    single('A2:1.8', 'IT-9.2', 1, 'A user downloads an app as a .dmg file. What is the usual way to install it?',
           'Open the image and drag the .app into Applications',
           ['Rename the .dmg to .pkg and double-click it', 'Copy the .dmg file into /System/Library', 'Open Terminal and run the .dmg with sudo'],
           'A .dmg is a disk image; the app bundle inside is copied to /Applications.'),
    match('A2:1.8', 'IT-9.2', 2, 'Match each macOS need to the built-in feature.',
          [('Encrypt the whole startup disk', 'FileVault'), ('Hourly backups to an external drive', 'Time Machine'),
           ('Search for a file by name from anywhere', 'Spotlight'), ('Close an app that has stopped responding', 'Force Quit')],
          'Know the macOS tools named in Core 2 1.8.', decoys=['Continuity']),
    single('A2:1.8', 'IT-9.2', 3, 'On a Mac, where are company-enforced restrictions such as passcode rules and blocked settings usually coming from?',
           'A device-management (MDM) profile installed on the Mac',
           ['The Keychain entries saved for the user’s Apple Account', 'A Time Machine backup restored from another Mac', 'The Dock layout chosen during the first setup'],
           'Organisations enforce settings through MDM configuration profiles.'),
    multi('A2:1.8', 'IT-9.2', 4, 'Which TWO are macOS features that help protect a user’s data? (Choose two.)',
          ['FileVault', 'Time Machine'],
          ['Mission Control', 'Spotlight', 'The Dock', 'Gestures'],
          'FileVault encrypts; Time Machine backs up. The others are navigation features.'),
    single('A2:1.9', 'IT-9.1', 1, 'Which Linux file stores password hashes and is readable only by root?',
           '/etc/shadow', ['/etc/passwd', '/etc/hosts', '/etc/fstab'],
           '/etc/passwd holds account details for everyone to read; hashes moved to /etc/shadow.'),
    match('A2:1.9', 'IT-9.1', 2, 'Match each Linux task to the command.',
          [('Show free space on each file system', 'df'), ('Show how much space a folder uses', 'du'),
           ('Search files for a text string', 'grep'), ('Change who owns a file', 'chown')],
          'df = disk free, du = disk usage, grep searches text, chown changes owner.', decoys=['fsck']),
    single('A2:1.9', 'IT-9.1', 3, 'A Linux workstation drops to an emergency shell after a new line was added to /etc/fstab. What is the most likely cause?',
           'The new fstab entry is wrong and the boot is waiting on it',
           ['The GRUB bootloader has been removed from the disk', 'The /etc/shadow file has lost the root password hash', 'The kernel cannot find the /etc/hosts file'],
           'fstab mounts happen at boot; a bad, non-optional entry stops a normal boot.'),
    order('A2:1.9', 'IT-9.1', 4, 'Put the Linux boot sequence in order.',
          ['Firmware starts the bootloader', 'GRUB loads the kernel', 'The kernel starts systemd', 'systemd mounts file systems and starts services', 'The user signs in to a shell'],
          'Firmware → bootloader → kernel → init (systemd) → login.'),
]
