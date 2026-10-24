"""Explanation ladder — ITSUP chapter 9 (Linux, macOS & Cross-Platform Support). Pending SME review.

Author B (labs branch, pass 19). Every concept section of lessons 9.1-9.4 is laddered (Option B pass 2 replaced every same_as with a bespoke ladder, _p2cNN.py), or
skipped with a reason. CLIENT chapter 2 holds the same lessons and reuses this ladder (curriculum_v2/ladder/client/ch02.py).
Where a real Linux VM lab exercises the idea, the try-it rung links to it.
"""
from curriculum_v2.ladder.itsup._p2c09 import SECS as _P2
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, section, skip, sort,
                                         tryit, visual)

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 9

L91 = 'Course lesson 9.1 “Linux CLI Essentials” (the original section), re-explained'
L92 = 'Course lesson 9.2 “macOS Support Patterns” (the original section), re-explained'
L93 = 'Course lesson 9.3 “Cross-Platform Access” (the original section), re-explained'
L94 = 'Course lesson 9.4 “Capstone — Mixed Environment” (the original section), re-explained'
MAN = ('Linux man-pages project (man7.org): chmod(1), ls(1), sudo(8), passwd(5), shadow(5), fstab(5), hosts(5); '
       'systemd documentation (systemctl, journalctl)')
APPLE = ('Apple Support — “How to start up from macOS Recovery”; Mac User Guide (Activity Monitor, Disk Utility, '
         'FileVault, Time Machine, Force Quit)')
APPLE_SEC = 'Apple Platform Security guide — XProtect, FileVault and Keychain'
MS_RDP = ('Microsoft Learn — Remote Desktop Services: Network Level Authentication and Remote Desktop Gateway; '
          'Windows Remote Management (WinRM ports 5985/5986)')
CISA_RMM = 'CISA, NSA and MS-ISAC — “Protecting Against Malicious Use of Remote Monitoring and Management Software” (January 2023)'
RFC6143 = 'IETF RFC 6143, The Remote Framebuffer Protocol (VNC)'
MS_SMB = 'Microsoft Learn — SMB protocol overview (TCP 445); OpenSSH for Windows (ssh, scp, sftp clients)'

MISCONCEPTIONS = {
    'MC-L-IT9-PERM-TRIPLET': {
        'obj': 'IT-9.1', 'label': 'Reading a permission string from the wrong end, or adding the octal digits across the whole string',
        'fix': 'After the type character come three triplets — owner, group, others — and each triplet gets its own digit (r4 + w2 + x1).',
        'terms': ['rwx', 'octal', 'owner', 'group', 'others'], 'source': L91 + '; ' + MAN, 'review': 'Pending SME review'},
    'MC-L-IT9-DIR-X': {
        'obj': 'IT-9.1', 'label': 'Thinking read permission alone lets you open a directory',
        'fix': 'On a directory, x means “may enter”; without it even the owner cannot cd into it or reach its files.',
        'terms': ['directory', 'execute', 'enter'], 'source': L91 + '; ' + MAN, 'review': 'Pending SME review'},
    'MC-L-IT9-PASSWD-HOLDS-PW': {
        'obj': 'IT-9.1', 'label': 'Thinking /etc/passwd holds the password hashes',
        'fix': '/etc/passwd is world-readable account information; the hashes are in /etc/shadow, which ordinary users cannot read.',
        'terms': ['/etc/passwd', '/etc/shadow', 'hash'], 'source': L91 + '; ' + MAN, 'review': 'Pending SME review'},
    'MC-L-IT9-DMG-TRASH-ALL': {
        'obj': 'IT-9.2', 'label': 'Thinking dragging any Mac app to the Trash always removes everything it installed',
        'fix': 'A .dmg app is one bundle, but a .pkg can install helpers and extensions elsewhere; use the vendor’s uninstaller.',
        'terms': ['.pkg', '.dmg', 'uninstall', 'helper'], 'source': L92 + '; ' + APPLE, 'review': 'Pending SME review'},
    'MC-L-IT9-EXFAT-JOURNAL': {
        'obj': 'IT-9.4', 'label': 'Thinking an exFAT drive is as safe to unplug without ejecting as a journaled disk',
        'fix': 'exFAT has no journaling, so recent writes can be lost if the drive is pulled without ejecting.',
        'terms': ['exfat', 'journaling', 'eject'], 'source': L94, 'review': 'Pending SME review'},
    'MC-L-IT9-MEM-AS-DISK': {
        'obj': 'IT-9.2', 'label': 'Reading red memory pressure and heavy swap on a Mac as a disk or network fault',
        'fix': 'Red memory pressure with high swap means the workload needs more memory than is free; reduce the load or plan more RAM.',
        'terms': ['memory pressure', 'swap', 'activity monitor'], 'source': L92 + '; ' + APPLE, 'review': 'Pending SME review'},
}

# reused course misconceptions (curriculum_v2/misconceptions.py)
WINHAB, SUDONOTE, WIPEMAC = 'MC-IT9-WINDOWS-HABITS', 'MC-IT9-SUDO-NO-NOTE', 'MC-IT9-WIPE-MAC'
ACCFAULT, PWBYOS, NTFSRO = 'MC-IT9-ACCESS-AS-FAULT', 'MC-IT9-PASSWORD-BY-OS', 'MC-IT9-NTFS-READONLY-AS-FAULT'
CASE, REMOTE, BROAD = 'MC-IT9-CASE-BLIND', 'MC-C-IT9-REMOTE-TOOL', 'MC-R3-IT9-BROAD-PRIV'
PERMS, MACREC = 'MC-R5-IT9-PERMS', 'MC-R5-IT9-MAC-RECOVERY'
MDMSIDE, FSCHOICE, CRLF = 'MC-R5-IT9-MDM-SIDESTEP', 'MC-R5-IT9-FS-CHOICE', 'MC-R5-IT9-LINE-ENDINGS'
RDPEXP, TOOLMATCH, DMG = 'MC-R6-IT9-RDP-EXPOSURE', 'MC-R6-IT9-MAC-TOOL-MATCH', 'MC-R6-IT9-DMG-INSTALL'
TRIPLET, DIRX, PASSWD = 'MC-L-IT9-PERM-TRIPLET', 'MC-L-IT9-DIR-X', 'MC-L-IT9-PASSWD-HOLDS-PW'
PKG, EXJ = 'MC-L-IT9-DMG-TRASH-ALL', 'MC-L-IT9-EXFAT-JOURNAL'

SVG = 'viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" aria-label="{label}" class="ladder-svg"'


def svg(w, h, label, body):
    return f'<svg {SVG.format(w=w, h=h, label=label)}><title>{label}</title>{body}</svg>'


def box(x, y, w, h, text, sub=''):
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>'
    t += (f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 7)}" text-anchor="middle" dominant-baseline="middle" '
          f'fill="currentColor" font-size="13" font-weight="700">{text}</text>')
    if sub:
        t += (f'<text x="{x + w / 2}" y="{y + h / 2 + 10}" text-anchor="middle" dominant-baseline="middle" '
              f'fill="currentColor" font-size="11">{sub}</text>')
    return t


def arrow(x1, y1, x2, y2):
    """Horizontal (y1 == y2) or vertical-down arrow."""
    rot = 0 if y1 == y2 else 90
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="2"/>'
            f'<polygon points="{x2},{y2} {x2 - 7},{y2 - 5} {x2 - 7},{y2 + 5}" fill="currentColor" transform="rotate({rot} {x2} {y2})"/>')


def label(x, y, text, size=11, anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="currentColor" font-size="{size}">{text}</text>'


# ---------------------------------------------------------------- diagrams
_PERM = svg(640, 170, 'The permission string -rw-r----- split into the file type and three triplets: owner rw- is 6, group r-- is 4, others --- is 0, so the octal mode is 640',
            box(10, 20, 70, 50, '-', 'type') + box(95, 20, 150, 50, 'r w -', 'owner (u)') + box(260, 20, 150, 50, 'r - -', 'group (g)')
            + box(425, 20, 150, 50, '- - -', 'others (o)')
            + label(170, 92, '4 + 2 + 0 = 6', 12) + label(335, 92, '4 + 0 + 0 = 4', 12) + label(500, 92, '0 + 0 + 0 = 0', 12)
            + label(320, 122, 'one digit per triplet → chmod 640', 13)
            + label(320, 150, 'r = 4 · w = 2 · x = 1   (on a directory, x = may enter)', 11))

_BOOT = svg(640, 150, 'A Linux client from power-on to a shell: firmware, the GRUB bootloader, the kernel, systemd mounting /etc/fstab and starting services, then the login shell',
            box(10, 30, 100, 50, 'Firmware') + arrow(110, 55, 135, 55) + box(135, 30, 110, 50, 'GRUB', 'bootloader')
            + arrow(245, 55, 270, 55) + box(270, 30, 100, 50, 'Kernel') + arrow(370, 55, 395, 55)
            + box(395, 30, 120, 50, 'systemd', 'fstab · services') + arrow(515, 55, 540, 55) + box(540, 30, 90, 50, 'Shell')
            + label(190, 108, 'stops here → bootloader problem', 11) + label(455, 108, 'stops here → check fstab, services', 11)
            + label(320, 138, 'accounts: /etc/passwd (anyone reads) · hashes: /etc/shadow (not ordinary users)', 11))

_MAC = svg(640, 170, 'Windows tools and their macOS counterparts: Task Manager and Activity Monitor, chkdsk and Disk Utility First Aid, Event Viewer and Console, BitLocker and FileVault, File History and Time Machine, WinRE and macOS Recovery',
           label(160, 18, 'Windows', 13) + label(480, 18, 'macOS', 13)
           + ''.join(box(10, 26 + i * 28, 300, 24, a) + box(330, 26 + i * 28, 300, 24, b) for i, (a, b) in enumerate([
               ('Task Manager', 'Activity Monitor'), ('chkdsk', 'Disk Utility → First Aid'), ('Event Viewer', 'Console'),
               ('BitLocker', 'FileVault'), ('File History', 'Time Machine')])))

_INSTALL = svg(640, 150, 'Two ways Mac apps arrive: a .dmg holds one app bundle you drag to Applications and later drag to the Trash; a .pkg installer can place helpers and extensions in several places, so it needs the vendor’s uninstaller',
               box(10, 20, 150, 50, '.dmg image') + arrow(160, 45, 200, 45) + box(200, 20, 200, 50, 'drag .app → Applications')
               + arrow(400, 45, 440, 45) + box(440, 20, 190, 50, 'remove: drag to Trash')
               + box(10, 90, 150, 50, '.pkg installer') + arrow(160, 115, 200, 115) + box(200, 90, 200, 50, 'files in several places', 'helpers, extensions')
               + arrow(400, 115, 440, 115) + box(440, 90, 190, 50, 'remove: vendor uninstaller'))

_ENT = svg(640, 170, 'Access or fault: compare with a user who has access on the same device; if they succeed it is the original user’s entitlement, an access request; if they fail, test path, name and port for a technical fault',
           box(10, 60, 140, 50, '“Can’t open it”') + arrow(150, 85, 190, 85) + box(190, 60, 170, 50, 'User WITH access,', 'same device?')
           + arrow(360, 72, 400, 40) + arrow(360, 98, 400, 130)
           + box(400, 15, 230, 50, 'Works → entitlement', 'request to resource owner') + box(400, 105, 230, 50, 'Fails → technical fault', 'path · name · port')
           + label(320, 162, 'no password is asked for, typed or recorded at any step', 11))

_REMOTE = svg(640, 170, 'Matching the remote tool to the job: see a user’s screen with the approved screen-sharing tool and consent; one command on many Windows servers with WinRM; a Linux server shell with SSH keys; all through the VPN or gateway, never a port opened to the internet',
              box(10, 15, 230, 40, 'See the user’s screen') + arrow(240, 35, 280, 35) + box(280, 15, 350, 40, 'approved screen share + consent')
              + box(10, 65, 230, 40, 'Same command, 30 servers') + arrow(240, 85, 280, 85) + box(280, 65, 350, 40, 'WinRM / PowerShell remoting')
              + box(10, 115, 230, 40, 'Linux server config') + arrow(240, 135, 280, 135) + box(280, 115, 350, 40, 'SSH with a key, via jump host')
              + label(320, 166, 'everything through the VPN or gateway — never RDP 3389 open to the internet', 11))

_FS = svg(640, 190, 'Which systems can read and write each file system natively: exFAT and FAT32 all three (FAT32 limited to 4 GB files); NTFS Windows read-write, macOS read only, Linux with a driver; APFS macOS only; ext4 Linux only',
          label(150, 18, 'file system', 12) + label(330, 18, 'Windows', 12) + label(440, 18, 'macOS', 12) + label(550, 18, 'Linux', 12)
          + ''.join(box(70, 26 + i * 32, 160, 26, n) + label(330, 44 + i * 32, w, 12) + label(440, 44 + i * 32, m, 12)
                    + label(550, 44 + i * 32, l, 12) for i, (n, w, m, l) in enumerate([
                        ('exFAT', 'rw', 'rw', 'rw'), ('FAT32 (≤ 4 GB file)', 'rw', 'rw', 'rw'), ('NTFS', 'rw', 'read only', 'rw (driver)'),
                        ('APFS', '—', 'rw', 'limited'), ('ext4', '— (WSL)', '—', 'rw')])))

LESSONS = {
    '9.1': {
        'start-here-other-operating-systems-exist': skip(
            'Start here — other operating systems exist', 'orientation',
            'A start-here block framing the chapter; the Linux habits are laddered in the core section.'),

        'core-content': section(
            'Core content', 'IT-9.1',
            [check('ls -l shows drwxr-x--- for a folder. What can the group do?',
                   'List it and enter it, but not change it',
                   ['Read, change and delete everything inside it', 'Nothing, because only the owner has rights here'],
                   'The second triplet is the group: r-x means read the listing and enter (x on a directory), with no write. '
                   'rwx is the owner’s triplet, and the last triplet (---) is others with no access.', mc=[TRIPLET, PERMS])],
            plain('''<p>On a Linux box you do not know, read first. Change nothing yet.</p>
<p>Many commands only read. <code>whoami</code>, <code>ip a</code>, <code>ip route</code>, <code>df -h</code> and
<code>systemctl status</code> tell you who, where and what is running.</p>
<p>Every file has an <strong>owner</strong>, a <strong>group</strong> and <strong>everyone else</strong>. Each one can
read (r), write (w) or run (x). <code>ls -l</code> shows this as nine letters after the first one.</p>
<p>For a folder, x means you may go in.</p>
<p><code>sudo</code> runs one command as the admin. That is a change. Write it in the ticket with what happened.</p>''',
                  L91 + '; ' + MAN,
                  [check('Why does a sudo command go in the ticket?',
                         'It ran with root rights and changed the system',
                         ['Because sudo always asks for the user’s password first', 'Because sudo commands are removed from the log afterwards'],
                         'sudo runs the command with administrative rights, so it is a change another technician must be able to '
                         'see and undo. It is logged by the system, and the password prompt is not the reason.', mc=[SUDONOTE, None])]),
            analogy('''<p>Think of a shared office building.</p>
<p>Each room has a door sign with three lines: what the <strong>room’s owner</strong> may do, what <strong>the
team</strong> may do, and what <strong>visitors</strong> may do. “Read” is looking through the glass, “write” is
moving the furniture, and for a room “execute” is being allowed through the door at all. A room marked “look, but no
entry” for the team means they can see the desks but cannot walk in to use them.</p>
<p>The building manager’s master key is <code>sudo</code>: it opens anything, which is exactly why each use is
written in the logbook. A new visitor reads the floor plan (<code>ls</code>, <code>ip a</code>, <code>df -h</code>)
before touching anything.</p>''',
                    L91 + ' (office-building analogy written for this rung)',
                    [check('In the building story, “allowed through the door” matches which permission on a directory?',
                           'x (execute)',
                           ['r (read the names)', 'w (write and delete)'],
                           'On a directory, x means may enter: without it you cannot cd into the folder even if you can read its '
                           'name list. r shows the names and w changes the contents.', mc=[DIRX, TRIPLET])]),
            visual(_PERM + '''
<ol class="ladder-trace">
<li><code>systemctl status nginx</code> → failed at 09:12.</li>
<li><code>journalctl -u nginx -b</code> → “open() site.conf failed (13: Permission denied)”.</li>
<li><code>ls -l site.conf</code> → <code>-rw------- alex alex</code>, edited 09:05: only alex can read it (600).</li>
<li>Cause found without changing anything; escalate to the server owner to restore owner and mode.</li></ol>''',
                   L91 + ' (permission diagram and worked example “the web app on the lab server is down”, redrawn); ' + MAN,
                   [check('A file shows -rwxr-xr--. What is its octal mode?',
                          '754',
                          ['775', '457'],
                          'Owner rwx = 4+2+1 = 7, group r-x = 4+0+1 = 5, others r-- = 4, so 754. 775 gives others too much, and '
                          '457 reads the triplets backwards.', mc=[TRIPLET, TRIPLET])]),
            tryit('''<p>Predict, then check on a real Linux machine in your browser: the permissions lab grades the real
file modes and owners it finds in the VM.</p>''',
                  L91 + '; ' + MAN,
                  [check('A folder is set to 644. Why can even its owner not open it with cd?',
                         'It has no x bit, so nobody may enter it',
                         ['644 is a read-only mode for files that blocks all access', 'The owner needs sudo to open any folder they own'],
                         'Directories need x to be entered; 644 gives r and w but no x. A correct folder mode for the owner would '
                         'include x, such as 755 or 750.', mc=[DIRX, BROAD])],
                  widget=reveal('Before you look: which command shows the default gateway on Linux, and which line do you read?',
                                '<code>ip route</code> — the line that starts “default via”. It only reads, so it is safe on a box you do not know.'),
                  lab={'id': 'linux-vm-perms', 'note': 'Set and read real file modes and owners in the VM; the probe checks the result.'})),

        '1-map-to-what-you-already-type': _P2[('9.1', '1-map-to-what-you-already-type')],
        'linux-inventory-cousins': _P2[('9.1', 'linux-inventory-cousins')],
        'reference-linux-commands-a-support-technician-uses': skip(
            'Reference — Linux commands a support technician uses', 'reference', 'A lookup table of commands and their Windows cousins.'),

        'linux-commands-key-files-and-os-components': section(
            'Linux commands, key files and OS components', 'IT-9.1',
            [check('Which file holds the password hashes on a Linux system?',
                   '/etc/shadow',
                   ['/etc/passwd', '/etc/hosts'],
                   '/etc/shadow holds the hashes and ordinary users cannot read it. /etc/passwd holds account details and is '
                   'readable by everyone, which is why it holds no passwords; /etc/hosts maps names to addresses.', mc=[PASSWD, None])],
            plain('''<p>A few files run a Linux box.</p>
<ul><li><code>/etc/passwd</code> lists the users. Anyone can read it, so no passwords are in it.</li>
<li><code>/etc/shadow</code> holds the password hashes. Ordinary users cannot read it.</li>
<li><code>/etc/hosts</code> maps names to addresses. It is checked before DNS.</li>
<li><code>/etc/fstab</code> lists the disks to mount at start-up. One typing mistake here can stop the boot.</li></ul>
<p>Start-up goes in a chain. The firmware starts GRUB. GRUB loads the kernel. The kernel starts systemd. systemd mounts
the disks and starts services. Then you log in.</p>
<p>If it stops before the kernel, look at GRUB. If it stops after, look at fstab and services.</p>''',
                  L91 + '; ' + MAN,
                  [check('A workstation drops to an emergency shell right after someone added a share to /etc/fstab. Where do you look?',
                         'The new fstab line',
                         ['The GRUB bootloader settings', 'The user’s home folder permissions'],
                         'The boot got past the kernel and stopped while systemd mounted file systems, and the only change was the '
                         'fstab line. GRUB problems stop before the kernel; home folder modes do not stop a boot.', mc=[WINHAB, None])]),
            analogy('''<p>Think of a theatre opening for the evening.</p>
<p>The caretaker unlocks the building (firmware), the stage manager reads the running order and calls the show
(GRUB), the director takes charge of the stage (the kernel), and the crew chief brings in the sets listed on the
props sheet and starts the lights and sound (systemd mounting <code>/etc/fstab</code> and starting services). Only then
are the doors opened to the audience (the login shell).</p>
<p>If the props sheet lists a set that is not in the store, the crew chief waits for it and the doors never open — a bad
fstab line. The cast list on the noticeboard (<code>/etc/passwd</code>) is public; the keys to the dressing rooms
(<code>/etc/shadow</code>) are locked in the office.</p>''',
                    L91 + ' (theatre analogy written for this rung)',
                    [check('In the theatre story, “the cast list on the public noticeboard” matches which file?',
                           '/etc/passwd',
                           ['/etc/shadow', '/etc/fstab'],
                           '/etc/passwd is readable by everyone and lists accounts, like a public cast list. /etc/shadow (locked '
                           'keys) holds the hashes, and /etc/fstab is the props sheet of disks to mount.', mc=[PASSWD, None])]),
            visual(_BOOT + '''
<ol class="ladder-trace">
<li>Symptom: the workstation boots to an emergency shell.</li>
<li>It got past GRUB and the kernel, so the fault is at the systemd stage.</li>
<li>Recent change: a network share was added to <code>/etc/fstab</code> with a typo in the server name, and not marked optional.</li>
<li>From the emergency shell: remount root read-write, comment out the line with <code>nano</code>, reboot.</li>
<li>Test the corrected line with <code>sudo mount -a</code> before the next reboot.</li></ol>''',
                   L91 + ' (boot chain and real-world scenario “the workstation that booted to an emergency shell”, drawn); ' + MAN,
                   [check('Why should fsck be run only on an unmounted file system?',
                          'Repairing one that is in use can corrupt it',
                          ['fsck only works if the network is disconnected first', 'A mounted file system is already repaired by systemd'],
                          'fsck changes the file system structures; if the system is writing to it at the same time, the repair '
                          'can make things worse. It has no network requirement, and systemd does not repair it.', mc=[WINHAB, None])]),
            tryit('''<p>Order the boot chain, then add a real data disk in the VM: partition, format, mount by UUID and an
<code>/etc/fstab</code> line that <code>findmnt --verify</code> must accept.</p>''',
                  L91 + '; ' + MAN,
                  [check('What is the difference between sudo and su?',
                         'sudo elevates one logged command; su switches user for a session',
                         ['They are the same program installed under two different names', 'su is safer, because it records every command a user types in it'],
                         'sudo elevates a single command and records it; su switches user, often to root, for a whole session. '
                         'Using sudo for the one command that needs it limits what runs as root.', mc=[BROAD, None])],
                  widget=order('Put the Linux start-up chain in order.',
                               ['Firmware', 'GRUB bootloader', 'Linux kernel', 'systemd mounts fstab and starts services', 'Login shell'],
                               'Where it stops tells you where to look: before the kernel is the bootloader, after it is fstab and services.'),
                  lab={'id': 'linux-vm-disk', 'note': 'Add a disk and an fstab entry by UUID; findmnt --verify must pass.'})),
    },

    '9.2': {
        'core-content': section(
            'Core content', 'IT-9.2',
            [check('How do you start a Mac with Apple silicon in macOS Recovery?',
                   'Shut down, then hold the power button until startup options load',
                   ['Hold Command-R while it starts up, exactly as on every Mac model', 'Press F8 repeatedly while the Apple logo is on the screen'],
                   'On Apple silicon you hold the power button from shut down until “Loading startup options”, then choose '
                   'Options. Command-R is the Intel Mac method, and F8 is an old Windows key.', mc=[MACREC, MACREC])],
            plain('''<p>A Mac is still a chip, memory, a disk and a network. The settings app is different.</p>
<p>Start with <strong>About This Mac</strong>. It shows the chip, the memory, the serial number and the macOS version.
Apple silicon Macs and Intel Macs start up and recover in different ways.</p>
<p>Each Windows tool has a Mac partner. Activity Monitor is like Task Manager. Disk Utility First Aid is like chkdsk.
Console is like Event Viewer. FileVault is like BitLocker. Time Machine is the backup.</p>
<p>Before any repair, find the FileVault key and the date of the last Time Machine backup. A college Mac is managed by
MDM. Do not remove its profiles to “fix” something.</p>''',
                  L92 + '; ' + APPLE,
                  [check('Which Mac tool matches Windows Task Manager?',
                         'Activity Monitor',
                         ['System Information', 'Console'],
                         'Activity Monitor shows what is using CPU, memory, energy, disk and network, like Task Manager. System '
                         'Information lists hardware and software, and Console shows logs like Event Viewer.', mc=[TOOLMATCH, TOOLMATCH])]),
            analogy('''<p>Moving from Windows to a Mac is like driving a car from another country.</p>
<p>The engine, brakes and fuel are the same idea, but the controls are in different places: the indicator is on the
other stalk, the handbook calls the boot a trunk. You find the familiar job under its new name — Activity Monitor for
Task Manager, Console for Event Viewer, FileVault for BitLocker.</p>
<p>And if the car is a company car, it carries the fleet’s tracker and rules (MDM). You do not unbolt the tracker
because it beeps; you call the fleet manager. Before any big repair, you check where the spare key is (the FileVault
recovery key) and that the boot is empty (the last Time Machine backup).</p>''',
                    L92 + ' (foreign-car analogy written for this rung)',
                    [check('In the company-car story, “unbolting the tracker because it beeps” matches what?',
                           'Removing the college’s MDM profile to fix an app',
                           ['Running Disk Utility First Aid on the startup disk', 'Closing browser tabs to free up memory'],
                           'Removing MDM profiles bypasses the organisation’s policy and is not a help-desk decision; route it to '
                           'the device-management owner. First Aid and closing tabs are normal fixes.', mc=[MDMSIDE, None])]),
            visual(_MAC + '''
<ol class="ladder-trace">
<li>“My Mac is really slow.” About This Mac: MacBook Air, M-series, 8 GB, current macOS; Device Management shows the college profile.</li>
<li>Activity Monitor → Memory: pressure graph red, a browser with 60 tabs, high swap.</li>
<li>Activity Monitor → CPU: nothing unusual. Disk Utility First Aid: no errors.</li>
<li>Cause: memory pressure from the browser. Fix agreed with the user: close tabs, turn on the browser’s memory saver.</li>
<li>Verify after a day; note that 8 GB is tight for this workload.</li></ol>''',
                   L92 + ' (tool table and worked example “my Mac is really slow”, drawn); ' + APPLE,
                   [check('Activity Monitor’s memory pressure graph is red and swap use is high. What does that point to?',
                          'The workload needs more memory than is free',
                          ['The startup disk has a failing sector', 'The Wi-Fi network is congested at the moment'],
                          'Red memory pressure and heavy swap mean the Mac is short of memory for what is running. A disk fault '
                          'would show in First Aid, and Wi-Fi congestion is a network symptom.', mc=['MC-L-IT9-MEM-AS-DISK', None])]),
            tryit('''<p>Sort each job to its Mac tool. Then predict where you would read the chip, serial number and
macOS version before you reveal it.</p>''',
                  L92 + '; ' + APPLE,
                  [check('A user asks you to remove the college’s profile because it blocks an app. What do you do?',
                         'Decline and route it to the device-management owner',
                         ['Remove it, then reinstall it once the app is installed', 'Erase the Mac and set it up as a personal device'],
                         'MDM profiles are the organisation’s policy; removing them, even briefly, bypasses it. Erasing a managed '
                         'Mac can also trigger Activation Lock and loses data.', mc=[MDMSIDE, WIPEMAC])],
                  widget=sort('Which macOS tool does each job?',
                              {'Activity Monitor': ['See what is using memory', 'Find the app draining energy'],
                               'Disk Utility': ['Run First Aid on a volume', 'Erase and format a drive'],
                               'Console': ['Read crash reports', 'Read system logs']},
                              'Same jobs as Windows, different names: Task Manager, chkdsk and Event Viewer.'))),

        'a-mac-is-still-a-portable': _P2[('9.2', 'a-mac-is-still-a-portable')],

        'macos-features-and-tools': section(
            'macOS features and tools', 'IT-9.2',
            [check('A VPN client was dragged to the Trash, but its menu-bar item is back after a restart. Why?',
                   'It came as a .pkg that put helpers elsewhere',
                   ['The Trash must be emptied twice before apps are removed', 'macOS reinstalls deleted apps from the App Store'],
                   'A .pkg installer can place helpers and network extensions outside Applications, so dragging the app '
                   'leaves them; the vendor’s uninstaller removes them. The Trash and the App Store are not the cause.', mc=[PKG, None])],
            plain('''<p>Mac apps come in a few ways.</p>
<ul><li>The <strong>App Store</strong>.</li>
<li>A <strong>.dmg</strong> file. Open it. Drag the app into Applications. Eject it.</li>
<li>A <strong>.pkg</strong> installer. It can put files in many places.</li></ul>
<p>To remove a .dmg app, drag it to the Trash. A .pkg app may need the maker’s uninstaller.</p>
<p>Protect data first. <strong>FileVault</strong> locks the whole disk. <strong>Time Machine</strong> backs it up.
<strong>XProtect</strong> is the built-in malware check.</p>
<p>A frozen app? Press Option-Command-Esc to Force Quit.</p>''',
                  L92 + '; ' + APPLE + '; ' + APPLE_SEC,
                  [check('How do you install an app that arrives as a .dmg?',
                         'Open it, drag the app to Applications, eject',
                         ['Rename the .dmg to .app and double-click it', 'Copy the .dmg into the System folder and restart'],
                         'A .dmg is a disk image that holds the app bundle; you drag the .app into Applications and eject the '
                         'image. Renaming it or copying it into System treats it as a program.', mc=[DMG, DMG])]),
            analogy('''<p>Think of how furniture arrives.</p>
<p>A <strong>.dmg</strong> is a flat box with one assembled chair inside: you lift the chair into the room
(Applications) and recycle the box (eject the image). To get rid of it, you carry the chair out (drag it to the
Trash).</p>
<p>A <strong>.pkg</strong> is a fitted kitchen: the installer puts cupboards in the kitchen, a pipe under the floor and a
switch in the hall. Carrying out one cupboard leaves the pipe and the switch behind — you need the fitter’s removal
service (the vendor’s uninstaller).</p>
<p>FileVault is the lock on the front door, and Time Machine is the photo inventory you take before any work.</p>''',
                    L92 + ' (furniture-delivery analogy written for this rung); ' + APPLE,
                    [check('In the furniture story, which Mac feature is “the lock on the front door”?',
                           'FileVault',
                           ['Time Machine', 'XProtect'],
                           'FileVault encrypts the whole startup disk, like a lock on the whole house. Time Machine is the backup, '
                           'and XProtect is the built-in malware detection.', mc=[TOOLMATCH, None])]),
            visual(_INSTALL + '''
<ol class="ladder-trace">
<li>The VPN client was dragged to the Trash; its menu-bar item came back after restart.</li>
<li>It was installed from a <code>.pkg</code>, which added a helper and a network extension outside Applications.</li>
<li>Run the vendor’s uninstaller with administrator rights.</li>
<li>System Settings → General → Login Items &amp; Extensions: nothing from the vendor remains.</li>
<li>Restart and check again.</li></ol>''',
                   L92 + ' (worked example “an app that will not uninstall cleanly”, drawn)',
                   [check('Which shortcut force-quits a frozen Mac app?',
                          'Option-Command-Esc',
                          ['Control-Alt-Delete', 'Command-Shift-Q'],
                          'Option-Command-Escape opens Force Quit on a Mac. Control-Alt-Delete is the Windows security screen, and '
                          'Command-Shift-Q logs the user out.', mc=[WINHAB, None])]),
            tryit('''<p>Sort each install type to the way it is removed, then predict the answer before you reveal it.</p>''',
                  L92,
                  [check('A Mac “up to date” misses a security fix, and it still has a previous employer’s MDM profile. What did the lesson do first?',
                         'Protect the data first, then fix enrolment and updates',
                         ['Erase the Mac and reinstall macOS from Recovery straight away', 'Turn off XProtect so that the missing update can install'],
                         'The technician protected the user’s work first, then removed the old profile with the user’s permission, '
                         'enrolled the Mac and turned automatic updates back on. Erasing or disabling protection is not the fix.', mc=[WIPEMAC, None])],
                  widget=sort('How is each one removed?',
                              {'Drag to the Trash': ['App from a .dmg', 'App Store app'],
                               'Vendor uninstaller': ['VPN client from a .pkg', 'Driver with a helper from a .pkg']},
                              'A .pkg can scatter files; the vendor’s uninstaller knows where they went.'))),
    },

    '9.3': {
        'core-content': section(
            'Core content', 'IT-9.3',
            [check('A colleague with known access opens the share from the same Mac. What does that rule out?',
                   'The Mac, the network path and the server',
                   ['The original user’s group membership', 'Nothing yet, until the share is rebuilt'],
                   'If someone with access succeeds from the same device, the device, path and server work; what is left is '
                   'the original user’s entitlement, an access request. Group membership is the remaining suspect.', mc=[ACCFAULT, None])],
            plain('''<p>“I can’t get to it” can mean two things.</p>
<p>It can be a <strong>fault</strong>. The server is down, the path is wrong, or a port is blocked.</p>
<p>Or it can be <strong>access</strong>. The user was never given it, or lost it when their job changed.</p>
<p>Different people fix each one, so tell them apart early. Ask someone who has access to try on the same computer. If it
works for them, the computer is fine. It is an access request for the owner of the folder, with the manager’s OK.</p>
<p>“Access is denied” usually means access, not the network. Never ask for or write down the user’s password.</p>''',
                  L93,
                  [check('The error says “You do not have permission to access this server”. Which is more likely?',
                         'An entitlement problem',
                         ['A failing network card on the user’s PC', 'A DNS server that is not answering queries'],
                         'Permission errors mean the server was reached and refused this user, so the network path and names '
                         'work. The fix is an access request, not a hardware or DNS change.', mc=[ACCFAULT, None])]),
            analogy('''<p>Think of a staff card at an office door.</p>
<p>The door will not open for a new starter. Is the door broken, or is the card not on the list? You ask a colleague to
tap their card at the same door. If it opens for them, the door, the reader and the power are fine — the new starter is
simply not on the list yet, and the person who owns the list (with the manager’s approval) adds them.</p>
<p>If it does not open for anyone, it is a broken door: call facilities. Either way, nobody hands their card or PIN to
the receptionist to “try it”.</p>''',
                    L93 + ' (door-card analogy written for this rung)',
                    [check('In the door-card story, why does nobody hand their PIN to the receptionist?',
                           'A shared secret leaks, like a password in a ticket',
                           ['The receptionist is not trained to use the reader', 'The PIN changes every time the door is opened'],
                           'Tickets are read by many people and kept for years, so a recorded password is a credential leak, just '
                           'like a shared PIN. The receptionist’s skills are not the reason.', mc=[PWBYOS, None])]),
            visual(_ENT + '''
<ol class="ladder-trace">
<li>A designer on a Mac cannot open <code>smb://files.example.edu/budget</code>; a Windows colleague can.</li>
<li>The designer opens a different share on the same server → server, name and port work.</li>
<li>The error is “You do not have permission to access this server”; the designer joined last week.</li>
<li>Conclusion: entitlement. Service request to the share owner with the account name, path and the manager’s approval.</li></ol>''',
                   L93 + ' (decision diagram and worked example “Mac user, Windows share”, drawn)',
                   [check('Which test result points to a technical fault rather than access?',
                          'Port 445 on the file server is closed',
                          ['The error says “Access is denied” for this user', 'A colleague opens it from the same Mac'],
                          'A closed SMB port is a server, firewall or network fault for the owning team. “Access is denied” and a '
                          'colleague succeeding both point to the user’s entitlement.', mc=[ACCFAULT, None])]),
            tryit('''<p>Sort the ticket evidence into access or fault. Then onboard a user into the right group in the
directory lab — group membership is what usually grants access.</p>''',
                  L93,
                  [check('Which of these is an identity source that can control access?',
                         'Microsoft Entra ID',
                         ['The user’s desktop wallpaper settings', 'The PC’s screen resolution'],
                         'Access is decided by an identity source: a local account, a directory such as Active Directory, or a '
                         'cloud identity provider such as Entra ID or Google Workspace. Display settings do not grant access.', mc=[ACCFAULT, None])],
                  widget=sort('Access request or technical fault?',
                              {'Access (entitlement)': ['“Access is denied” for one user', 'Colleague succeeds on the same PC',
                                                        'User changed role last week'],
                               'Technical fault': ['Port 445 closed for everyone', 'Server down for every user']},
                              'One comparison with a user who has access usually decides it.'),
                  lab={'id': 'win-ad-users', 'note': 'Add a new starter to the right group; group membership grants the share.'})),

        'shares-and-accounts': _P2[('9.3', 'shares-and-accounts')],

        'remote-access-technologies-and-their-security': section(
            'Remote access technologies and their security', 'IT-9.3',
            [check('You must run the same PowerShell command on 30 Windows servers. Which method fits?',
                   'WinRM (PowerShell remoting)',
                   ['Thirty separate RDP sessions, one per server', 'VNC screen sharing to each server in turn'],
                   'PowerShell remoting over WinRM runs one command on many servers from the admin workstation. RDP and VNC '
                   'give one desktop at a time and suit a person watching a screen.', mc=[REMOTE, REMOTE])],
            plain('''<p>Pick the remote tool by the job.</p>
<ul><li><strong>RDP</strong> gives a whole Windows desktop. Never open it straight to the internet. Use the VPN or a
gateway.</li>
<li><strong>SSH</strong> gives a safe command line on Linux, Macs and network kit. Use keys.</li>
<li><strong>WinRM</strong> runs PowerShell on many Windows servers at once.</li>
<li><strong>VNC</strong> shares a screen on any system. It is often weakly protected, so tunnel it.</li>
<li><strong>RMM</strong> manages many devices. If attackers get in, they reach all of them.</li></ul>
<p>Before you see a user’s screen, check who they are, check the ticket, and ask their consent. Use only approved tools.</p>''',
                  L93 + '; ' + MS_RDP + '; ' + CISA_RMM,
                  [check('Why should RDP not be published straight to the internet?',
                         'It is a top attack target; use a VPN or gateway',
                         ['RDP only ever works on the local network anyway', 'RDP traffic is never encrypted in any version'],
                         'Internet-facing RDP is a common attack target; a VPN or Remote Desktop Gateway with NLA and MFA reduces '
                         'that. RDP can work across networks and is encrypted, so those are not the reasons.', mc=[RDPEXP, RDPEXP])]),
            analogy('''<p>Think of the ways to work on a house when you are not there.</p>
<p>Being let in by the owner while they watch is screen sharing with consent. A tradesperson’s own key to a single room
is SSH with a key. A building manager who sends the same instruction to thirty flats at once is WinRM. A master key to
every flat in the block is RMM — enormously useful, and the first thing a burglar wants.</p>
<p>A front door left open to the street is RDP published to the internet. And someone who phones out of the blue,
saying they are from “the building company” and asking to be let in, is a scam until proven otherwise.</p>''',
                    L93 + ' (house-access analogy written for this rung); ' + CISA_RMM,
                    [check('A user says “Microsoft support” phoned and asked her to install a screen-sharing app. What is it?',
                           'A tech-support scam to treat as an incident',
                           ['A routine Microsoft call that needs no action', 'A normal update check that IT asked Microsoft to run'],
                           'Microsoft does not make unsolicited support calls; the lesson treats it as a scam: disconnect if a '
                           'session happened, remove the app, scan, reset passwords from a clean device and report it.', mc=[REMOTE, None])]),
            visual(_REMOTE + '''
<ol class="ladder-trace">
<li>Verify who the user is and that there is a ticket.</li>
<li>Get the user’s consent before viewing or controlling the screen.</li>
<li>Connect with an approved tool, through the VPN or remote-desktop gateway.</li>
<li>Work while the user can watch.</li>
<li>End the session, confirm it is closed, and record it on the ticket.</li></ol>''',
                   L93 + ' (worked example “choosing the tool” and the safe-session diagram, drawn)',
                   [check('Why is VNC usually tunnelled over SSH or a VPN?',
                          'Its authentication and encryption are often weak',
                          ['VNC only runs on Linux and needs SSH to start', 'VNC cannot show more than one monitor otherwise'],
                          'Plain VNC often has weak authentication and may send traffic unencrypted, so a tunnel protects it. VNC is '
                          'cross-platform and does not need SSH to run.', mc=[REMOTE, None])]),
            tryit('''<p>Match each job to its tool, then use SSH for real: set up key login between two Linux VMs and turn
password login off.</p>''',
                  L93,
                  [check('Which security setting does the lesson recommend for SSH?',
                         'Key login, with password and root login off',
                         ['Password login on a well-known default port', 'Root login allowed so admins work faster'],
                         'Key-based authentication with password and direct root login disabled makes SSH much harder to attack. '
                         'Passwords and root logins are what attackers try first.', mc=[BROAD, None])],
                  widget=sort('Which tool fits each job?',
                              {'Screen sharing with consent': ['See a home user’s app error'],
                               'WinRM': ['Restart a service on 30 Windows servers'],
                               'SSH': ['Check a Linux web server’s config', 'Copy a file to a Linux server with scp']},
                              'The job chooses the tool; the VPN or gateway is the way in for all of them.'),
                  lab={'id': 'linux-vm-ssh', 'note': 'Set up key login between two VMs, then turn password login off.'})),
    },

    '9.4': {
        'core-content': section(
            'Core content', 'IT-9.4',
            [check('A USB drive must move between a Mac, a Windows PC and a Linux lab machine with no extra drivers. Which file system?',
                   'exFAT',
                   ['NTFS', 'Btrfs'],
                   'exFAT is read and written natively by all three. NTFS is read-only on macOS without extra software, and '
                   'APFS is not readable natively on Windows.', mc=[FSCHOICE, NTFSRO]),
             check('A script from a Windows PC fails on Linux with “bad interpreter”. What do you suspect?',
                   'Windows line endings',
                   ['A failing disk on the Linux server', 'A firewall blocking the script’s port'],
                   'Windows saves CRLF line endings, and the Linux shell reads the stray carriage return as part of the '
                   'interpreter name. Saving with LF fixes it; the disk and firewall are not involved.', mc=[CRLF, None])],
            plain('''<p>Different systems store files in different ways.</p>
<ul><li><strong>NTFS</strong> is Windows. A Mac can read it but not write to it.</li>
<li><strong>APFS</strong> is the Mac. Windows cannot read it.</li>
<li><strong>ext4</strong> is Linux.</li>
<li><strong>exFAT</strong> works on all three. Eject it before you unplug it.</li>
<li><strong>FAT32</strong> works on all three too, but no file can be over 4 GB.</li></ul>
<p>Over the network, use SMB shares or SSH. Some things look like faults but are not. Linux sees “Report.txt” and
“report.txt” as two files; Windows shows one. Windows line endings break Linux scripts.</p>''',
                  L94 + '; ' + MS_SMB,
                  [check('Why warn the user to eject an exFAT drive before unplugging it?',
                         'exFAT has no journaling, so recent writes can be lost',
                         ['exFAT drives erase themselves if unplugged too fast', 'Ejecting converts the drive to NTFS for safety'],
                         'Without a journal, an interrupted write can leave files incomplete. Unplugging does not erase the drive, '
                         'and ejecting does not change the file system.', mc=[EXJ, None])]),
            analogy('''<p>File systems are like the shelving systems in different libraries.</p>
<p>The Windows library (NTFS) uses a catalogue a visiting Mac librarian can read but is not allowed to write in. The Mac
library (APFS) and the Linux library (ext4) use catalogues the Windows librarian cannot read at all. A shared lending
box that every library accepts is exFAT — though it has no logbook, so if you snatch it away mid-entry the last few
books may not be recorded (eject first). FAT32 is an older shared box with small slots: no single book over 4 GB fits.</p>
<p>And one library files “Report” and “report” on two different shelves, while another treats them as the same book —
which is how one file seems to vanish on a Windows PC.</p>''',
                    L94 + ' (library-shelving analogy written for this rung)',
                    [check('In the library story, why does one of two files seem to vanish on Windows?',
                           'Linux names are case-sensitive; Windows’ are not',
                           ['Windows deletes one of the two files each time it syncs', 'The SMB share hides any file whose name has a capital'],
                           'Linux file names are case-sensitive and Windows, by default, is not, so Windows shows only one. It is a '
                           'naming problem, not deletion by Windows or a fault in SMB.', mc=[CASE, CASE])]),
            visual(_FS + '''
<ol class="ladder-trace">
<li>Intake: managed MacBook Pro; user j.lee; cannot copy a 6.2 GB video to the shared USB drive.</li>
<li>Error: “too large for the volume’s format”; Disk Utility shows the drive is FAT32.</li>
<li>Request or fault? A fault caused by the format.</li>
<li>Plan: back up the drive, reformat as exFAT with the user’s agreement, copy back.</li>
<li>Test on both machines.</li></ol>''',
                   L94 + ' (file-system table and worked example, drawn)',
                   [check('How does a Mac user connect to a Windows share?',
                          'Finder → Go → Connect to Server → smb://server/share',
                          ['Disk Utility → First Aid → Mount Network Volume', 'System Settings → General → Device Management'],
                          'Finder’s Connect to Server takes an smb:// address. Disk Utility repairs local volumes and Device '
                          'Management shows MDM profiles; neither connects a share.', mc=[TOOLMATCH, None])]),
            tryit('''<p>Sort each symptom to its real cause, then move a file between two Linux machines over SSH with
<code>scp</code> in the VM lab.</p>''',
                  L94 + '; ' + MS_SMB,
                  [check('Copying a 6 GB video to a USB stick fails with “file too large”. What is the likely cause?',
                         'The stick is FAT32',
                         ['The stick is exFAT and too small', 'The video file is damaged on the PC'],
                         'FAT32 cannot store a single file over 4 GB, whatever the free space. exFAT handles large files, and a '
                         'damaged file would give a different error.', mc=[FSCHOICE, None])],
                  widget=sort('What is really behind each symptom?',
                              {'Case sensitivity': ['One of two files seems to vanish on Windows'],
                               'Line endings': ['Script fails with “bad interpreter” on Linux'],
                               'File-size limit': ['6 GB video will not copy to a USB stick'],
                               'NTFS on a Mac': ['Mac reads the drive but cannot save to it']},
                              'Each looks like a fault, but each has a cause you can explain to the user without a repair.'),
                  lab={'id': 'linux-vm-ssh', 'note': 'Copy release-1.4.txt between the two VMs with scp after key login works.'})),

        'mixed-environment-note': _P2[('9.4', 'mixed-environment-note')],
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '9.1': {'core-content': 'b0995cdfae4c', 'linux-commands-key-files-and-os-components': '8cefe5923cad'},
    '9.2': {'core-content': '5eaa3877a9f5', 'macos-features-and-tools': '3a91624fe026'},
    '9.3': {'core-content': '10de5ce2b3cb', 'remote-access-technologies-and-their-security': '78e2e3ba0ddf'},
    '9.4': {'core-content': '20bf3596008c'},
}

# ---------------------------------------------------------------- refinement pass 20: former skips, now laddered
from curriculum_v2.ladder.itsup._lk import P as _P, X as _X  # noqa: E402

_LSH = ('linux-vm-shell', 'Find your way around a real Linux shell with read-only commands first.')
LESSONS['9.1'].update({
    'start-here-other-operating-systems-exist': _X('Start here — other operating systems exist', 'IT-9.1', L91, [
        ('Linux and macOS are still made of what?', 'Brain, memory, disk, network', 'Completely different hardware', 'Only cloud services',
         'Every OS runs on the same building blocks; only the commands are spelled differently.', WINHAB, None),
        ('Which Linux command is the cousin of ipconfig?', 'ip a', 'mkfs', 'rm -rf',
         'ip a shows addresses; mkfs and rm -rf are destructive.', WINHAB, WINHAB),
        ('In the foreign-car story, why is the driver still fine?', 'The controls work the same way', 'Foreign cars drive themselves', 'Rules are identical',
         'Different labels, same parts, just like a new OS.', WINHAB, None),
        ('Which is never a first move on Linux?', 'mkfs', 'ip a', 'pwd',
         'mkfs creates a filesystem and wipes data; it is never a first move.', WINHAB, None),
        ('A managed Mac misbehaves. What do you not do?', 'Wipe it in the hallway', 'Write a ticket with evidence', 'Ask the MDM owner',
         'Managed Macs are not wiped casually; evidence and escalation first.', WIPEMAC, None),
    ],
        _P('Linux and macOS computers have the same parts as Windows ones: a processor, memory, a disk and a network card. The commands just have '
           'different names. ip a on Linux does roughly what ipconfig does on Windows. This chapter will not make you a Linux administrator, but '
           'you will know not to run mkfs first or wipe a managed Mac on the spot.'),
        _P('Rent a car abroad and the indicator stalk may be on the other side, the dashboard labels are in another language, and the gear stick '
           'feels odd. Yet you still know where the brake is and how to steer, because every car has the same basic parts. A new operating system '
           'is that hire car. Find the familiar controls first, and do not start pulling levers you do not recognise.'),
        ['Remember: brain, memory, disk, network.', 'Find the cousin command: ip a for ipconfig.', 'Read before you change.', 'Never mkfs or wipe as a first move.'],
        '<p>Match each Linux command to its Windows cousin.</p>',
        sort('Cousins', {'ipconfig': ['ip a'], 'whoami': ['whoami'], 'dir': ['ls -l'], 'Never a first move': ['mkfs', 'rm -rf /']},
             'Read-only cousins first; destructive commands never first.'), _LSH),
    'reference-linux-commands-a-support-technician-uses': _X('Reference — Linux commands a support technician uses', 'IT-9.1', L91, [
        ('Which command lists listening ports on Linux?', 'ss -tulpn', 'df -h', 'chmod +x',
         'ss -tulpn shows listening sockets, the cousin of netstat -ano.', WINHAB, None),
        ('“Permission denied” on a script you can read usually means…', 'It lacks the execute bit', 'The disk is full or read-only', 'You lack read permission',
         'Add the execute bit with chmod +x, or run it through its interpreter.', PERMS, None),
        ('In the phrasebook story, why carry a two-column list?', 'To map words you already know', 'To learn the whole language', 'For decoration',
         'The table maps Windows habits to Linux commands.', WINHAB, None),
        ('Which command reads a service’s log?', 'journalctl -u name', 'ls -l /var/log', 'systemctl stop name',
         'journalctl -u shows a unit’s log, like Event Viewer.', WINHAB, None),
        ('Which runs one command as administrator?', 'sudo command', 'chmod 777 everything', 'su forever',
         'sudo elevates one command; broad permissions are not a substitute.', BROAD, SUDONOTE),
    ],
        _P('This is a lookup table. Where am I: pwd, whoami, hostname. Files: ls -l, cat, less, tail -f. Permissions: chmod, chown. Admin: sudo. '
           'Network: ip a, ip route, dig, resolvectl status, ss -tulpn. Services and logs: systemctl status and journalctl -u. Disk and memory: '
           'df -h, free -h, top. Software: apt or dnf. A script you can read but not run usually needs chmod +x.'),
        _P('A traveller with a pocket phrasebook does not learn the whole language. They look up “where is the station” and “how much is this,” '
           'the phrases they already use at home, and find the local version. This reference is your phrasebook: each row starts with something you '
           'already do on Windows and gives you the Linux words for it.'),
        ['Where am I: pwd, whoami, hostname.', 'Network: ip a, ip route, dig.', 'Ports: ss -tulpn.', 'Services: systemctl status, journalctl -u.',
         'Admin for one command: sudo.'],
        '<p>Run the read-only rows in the Linux lab.</p>',
        sort('Task to command', {'Addresses': ['ip a'], 'Ports': ['ss -tulpn'], 'Logs': ['journalctl -u sshd'], 'Disk space': ['df -h']},
             'Each task has one cousin command.'), _LSH),
})

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '9.1': {'start-here-other-operating-systems-exist': 'abdd8a97788b', 'core-content': 'b0995cdfae4c', 'reference-linux-commands-a-support-technician-uses': '1b622ba67df4', 'linux-commands-key-files-and-os-components': '8cefe5923cad'},
    '9.2': {'core-content': '5eaa3877a9f5', 'macos-features-and-tools': '3a91624fe026'},
    '9.3': {'core-content': '10de5ce2b3cb', 'remote-access-technologies-and-their-security': '78e2e3ba0ddf'},
    '9.4': {'core-content': '20bf3596008c'},
}
