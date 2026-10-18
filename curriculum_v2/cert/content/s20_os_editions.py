"""A+ Core 2 1.1 (OS types and file systems) and 1.3 (Windows editions) — ITSUP 8.1."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-editions', 'Choosing a Windows edition by need',
    ['Home:\npersonal use', 'Pro: domain join,\nBitLocker, RDP host', 'Pro for Workstations:\nReFS, more RAM/CPUs', 'Enterprise:\nvolume licensing, extra security', 'N editions:\nno bundled media apps'],
    'Five boxes. Home suits personal use: it cannot join an Active Directory domain, host Remote Desktop, or run the Group '
    'Policy Editor, and offers device encryption rather than full BitLocker management. Pro adds domain join, BitLocker, Remote '
    'Desktop hosting and gpedit.msc. Pro for Workstations adds ReFS volume creation and support for more memory and processors. '
    'Enterprise is licensed through volume agreements and adds management and security features. N editions, sold in Europe, '
    'leave out bundled media apps, which the Media Feature Pack can add.',
    'Ask what the PC must do — join a domain, be reached by RDP, use BitLocker — then pick the lowest edition that does it.', cols=5)

HTML = f'''
<h4>Operating-system types (Core 2 1.1)</h4>
<ul>
<li><strong>Workstation OSs</strong>: Windows, Linux and macOS. <strong>ChromeOS</strong> runs on Chromebooks; it is built around the
Chrome browser and web apps, is managed through the Google Admin console in organisations, and updates itself automatically.</li>
<li><strong>Mobile OSs</strong>: <strong>iOS</strong> (iPhone), <strong>iPadOS</strong> (iPad; split from iOS in 2019 to add tablet features such as
multitasking) and <strong>Android</strong> (many manufacturers, so update timing depends on the vendor).</li>
<li><strong>End of life</strong>: when a vendor stops releasing security updates, the OS keeps working but every new vulnerability stays open.
Windows 10 reached end of support on 14 October 2025. Phones also have <strong>update limitations</strong>: each model receives
OS updates only for the period its manufacturer supports.</li>
<li><strong>Compatibility between OSs</strong>: file formats, file systems, peripherals and apps differ; check before mixing them.</li>
</ul>
<table class="ref-table"><thead><tr><th scope="col">File system</th><th scope="col">Where it is used</th><th scope="col">Points to know</th></tr></thead><tbody>
<tr><td>NTFS</td><td>Windows system and data drives</td><td>Permissions, encryption (EFS, BitLocker volumes), large files and volumes</td></tr>
<tr><td>ReFS</td><td>Windows Server storage; Windows 11 Pro for Workstations and Dev Drive</td><td>Resilient File System: built for integrity and large volumes; not used as the Windows boot volume</td></tr>
<tr><td>FAT32</td><td>Older removable media, firmware update sticks</td><td>Widely readable; 4 GB maximum file size</td></tr>
<tr><td>exFAT</td><td>Flash drives and memory cards</td><td>Large files, read and written by Windows, macOS and most Linux systems</td></tr>
<tr><td>ext4</td><td>Many Linux distributions</td><td>Journaling Linux default on Debian and Ubuntu</td></tr>
<tr><td>XFS</td><td>Red Hat Enterprise Linux and derivatives</td><td>Journaling, suited to large files and volumes; the RHEL default</td></tr>
<tr><td>APFS</td><td>macOS, iOS, iPadOS</td><td>Apple File System: snapshots, built-in encryption, optimised for SSDs</td></tr>
</tbody></table>
<h4>Windows editions (Core 2 1.3)</h4>
<ul>
<li><strong>Domain vs. workgroup</strong>: Home joins only workgroups (peer-to-peer). Pro, Pro for Workstations, Enterprise and Education can join an Active Directory domain.</li>
<li><strong>Remote Desktop</strong>: every edition can <em>connect to</em> another PC; only Pro and above can <em>be connected to</em> (host RDP).</li>
<li><strong>BitLocker</strong> and <strong>gpedit.msc</strong>: Pro and above. Home offers device encryption on supported hardware.</li>
<li><strong>RAM support limitations</strong>: Microsoft documents a maximum of 128 GB for Windows 11 Home, 2 TB for Pro and 6 TB for Pro for Workstations and Enterprise.</li>
<li><strong>Pro for Workstations</strong>: for high-end hardware — more processors and memory, ReFS volume creation and faster file sharing (SMB Direct).</li>
<li><strong>N versions</strong>: European-market editions without bundled media apps.</li>
<li><strong>Desktop styles / user interface</strong>: the same Start menu and taskbar across editions; organisations can lock the layout through policy (Pro and above).</li>
<li><strong>Upgrade paths</strong>: Home to Pro is an in-place edition upgrade with a Pro product key; Windows 11 needs TPM 2.0 and UEFI with Secure Boot capability.</li>
</ul>
{_FIG}
{worked('which edition for the new reception PC?', '''<ol>
<li>Requirements: join the office domain, let the IT team connect with Remote Desktop, and encrypt the drive with managed BitLocker recovery keys.</li>
<li>Home fails all three: no domain join, no RDP host, no BitLocker management.</li>
<li>Pro meets all three. Pro for Workstations adds nothing this PC needs (it has 16 GB RAM and one CPU).</li>
<li>Enterprise is only worth it if the organisation already has volume licensing.</li>
<li>Decision: Windows 11 Pro. Record the licence on the asset record.</li></ol>''')}
{scenario('the drive the Mac could not write to', '''<p>A photographer moves files between a Windows laptop and a Mac on a USB drive. The Mac can read it but not save
to it, and some large video files would not copy at all from Windows. The drive is NTFS (read-only on macOS by default), and an
older stick she also uses is FAT32 (4 GB file limit). Reformatting the new drive as <strong>exFAT</strong> — after copying the files
off — lets both computers read and write it and handles the large videos.</p>''')}
{cfu(('Which Windows 11 edition cannot host Remote Desktop?', 'Home — it can only connect to other PCs.'),
     ('Which file system would you choose for a flash drive shared by Windows and macOS with files over 4 GB?', 'exFAT.'),
     ('What does end of life mean for an operating system?', 'The vendor no longer releases security updates for it.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 8, 'lesson': 1, 'id': 'cert-os-editions', 'title': 'OS types, file systems and Windows editions',
    'cert': ['A2:1.1', 'A2:1.3'],
    'html': sme_note('Operating-system types, file systems and lifecycle (Core 2 1.1) and Windows editions (Core 2 1.3).') + HTML,
    'sources': ['ms-editions', 'ms-memlimits', 'apple-platsec', 'nist-800124r2'],
}]

GLOSSARY = [
    ('ReFS', 'Resilient File System: Windows file system designed for data integrity and large volumes.'),
    ('XFS', 'Journaling Linux file system; the default on Red Hat Enterprise Linux.'),
    ('APFS', 'Apple File System, used by macOS, iOS and iPadOS.'),
    ('exFAT', 'File system for flash media that supports large files and is readable by Windows, macOS and most Linux systems.'),
    ('End of life (OS)', 'The point after which a vendor stops releasing security updates for an operating system.'),
    ('N edition', 'European-market Windows edition without bundled media apps.'),
    ('Pro for Workstations', 'Windows edition for high-end hardware: more CPUs and memory, ReFS and SMB Direct.'),
]

ITEMS = [
    single('A2:1.1', 'IT-8.1', 2, 'A user needs a USB stick that both a Windows PC and a Mac can read and write, holding video files larger than 4 GB. Which file system fits?',
           'exFAT', ['FAT32', 'NTFS', 'ext4'],
           'FAT32 is limited to 4 GB files; NTFS is read-only on macOS by default; ext4 is not read by Windows or macOS without extra software.'),
    match('A2:1.1', 'IT-8.1', 3, 'Match each file system to where you would usually find it.',
          [('APFS', 'macOS startup disk'), ('XFS', 'Red Hat Enterprise Linux server'), ('NTFS', 'Windows system drive'), ('ReFS', 'Windows Server storage volume')],
          'Know the default file system of each platform named in Core 2 1.1.', decoys=['Firmware-update stick']),
    single('A2:1.1', 'IT-8.1', 4, 'A clinic still runs a PC whose operating system has reached end of life. What is the main risk?',
           'New vulnerabilities will not receive security updates',
           ['The PC will stop booting on a set date', 'Its licence will be revoked and it will lock', 'Its file system will become read-only'],
           'An end-of-life OS keeps running, but new flaws stay unpatched.'),
    single('A2:1.3', 'IT-8.1', 2, 'A small office wants IT staff to reach a new PC with Remote Desktop and join it to the domain. Which is the lowest edition that does both?',
           'Windows 11 Pro', ['Windows 11 Home', 'Windows 11 Home N', 'Windows 11 Home with device encryption'],
           'Home can connect to other PCs but cannot host RDP or join a domain.'),
    multi('A2:1.3', 'IT-8.1', 3, 'Which THREE are available in Windows 11 Pro but not in Windows 11 Home? (Choose three.)',
          ['Joining an Active Directory domain', 'Hosting Remote Desktop sessions', 'The Group Policy Editor (gpedit.msc)'],
          ['Using the Start menu and taskbar', 'Connecting to Wi-Fi networks', 'Running Windows Update'],
          'Domain join, RDP host and gpedit are Pro features; the rest are in every edition.'),
    match('A2:1.3', 'IT-8.1', 4, 'Match each requirement to the Windows edition it points to.',
          [('Creating ReFS volumes on a dual-CPU workstation', 'Pro for Workstations'), ('Personal laptop, no domain', 'Home'),
           ('European market, no bundled media apps', 'N edition'), ('Large organisation with volume licensing', 'Enterprise')],
          'Each edition targets a different need.', decoys=['Pro Education']),
]
