"""Explanation ladder — ITSUP chapter 8 (Windows Installation & Client Configuration). Pending SME review.

Author B (labs branch, pass 19). Every concept section of lessons 8.1-8.4 is laddered, restated with same_as, or
skipped with a reason. CLIENT chapter 1 holds the same lessons and reuses this ladder (curriculum_v2/ladder/client/ch01.py).
Facts are checked against Microsoft's documentation as named in each rung's source.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 8

L81 = 'Course lesson 8.1 “Clean vs In-Place” (the original section), re-explained'
L82 = 'Course lesson 8.2 “Baseline Configuration” (the original section), re-explained'
L83 = 'Course lesson 8.3 “Repair Tools” (the original section), re-explained'
L84 = 'Course lesson 8.4 “Capstone — Failed Update” (the original section), re-explained'
MS_RECOVERY = 'Microsoft Support — “Recovery options in Windows” and “Fix issues by reinstalling the current version of Windows”'
MS_SFC = ('Microsoft Support — “Use the System File Checker tool to repair missing or corrupted system files” '
          '(DISM /Online /Cleanup-Image /RestoreHealth before sfc /scannow)')
MS_EDITIONS = 'Microsoft — Windows 11 edition comparison (Home, Pro, Pro for Workstations, Enterprise)'
MS_FS = ('Microsoft Learn — exFAT file system specification and FAT32 limits (largest file 4 GB); the macOS NTFS '
         'read-only behaviour is from the lesson’s real-world scenario')
MS_GP = ('Microsoft Learn — Group Policy processing (local, site, domain, OU order; later wins unless enforced or '
         'blocked); gpupdate and gpresult command reference')
MS_WOW64 = 'Microsoft Learn — WOW64 implementation details (32-bit applications on 64-bit Windows)'
MS_SERVICES = 'Microsoft Learn — Windows services overview (services run in the background without a signed-in user)'
ITIL = 'AXELOS, ITIL 4 Foundation (2019): incident and problem management'
APLUS2 = 'CompTIA A+ Core 2 (220-1202) exam objectives 1.1, 1.3 and 1.10 (OS types and file systems, Windows editions, application requirements)'

MISCONCEPTIONS = {
    'MC-L-IT8-RESET-KEEPS-APPS': {
        'obj': 'IT-8.1', 'label': 'Thinking Reset this PC with “Keep my files” also keeps the installed apps and settings',
        'fix': '“Keep my files” keeps personal files only; apps and settings are removed and must be reinstalled.',
        'terms': ['reset this pc', 'keep my files', 'apps'], 'source': L81 + '; ' + MS_RECOVERY, 'review': 'Pending SME review'},
    'MC-L-IT8-FAT32-ANY-SIZE': {
        'obj': 'IT-8.1', 'label': 'Choosing FAT32 or NTFS for a drive shared with a Mac that must hold files over 4 GB',
        'fix': 'FAT32 cannot hold a file over 4 GB, and macOS cannot write NTFS by default; exFAT does both.',
        'terms': ['fat32', 'exfat', 'ntfs', '4 gb'], 'source': L81 + '; ' + MS_FS, 'review': 'Pending SME review'},
    'MC-L-IT8-32-RUNS-64': {
        'obj': 'IT-8.2', 'label': 'Thinking a 64-bit application can run on 32-bit Windows (the reverse of WOW64)',
        'fix': '64-bit Windows runs most 32-bit apps through WOW64; 32-bit Windows cannot run a 64-bit app.',
        'terms': ['32-bit', '64-bit', 'wow64'], 'source': L82 + '; ' + MS_WOW64, 'review': 'Pending SME review'},
    'MC-L-IT8-SFC-FIRST': {
        'obj': 'IT-8.3', 'label': 'Running sfc /scannow before DISM has repaired the component store it copies from',
        'fix': 'Run DISM /RestoreHealth first so the store is good, then sfc /scannow replaces damaged files from it.',
        'terms': ['dism', 'sfc', 'component store'], 'source': L83 + '; ' + MS_SFC, 'review': 'Pending SME review'},
    'MC-L-IT8-ONE-BY-ONE': {
        'obj': 'IT-8.3', 'label': 'Repairing the same failed update device by device when many devices show the same error',
        'fix': 'Many devices with one error is a pattern: link the tickets to a problem record and escalate the common facts.',
        'terms': ['pattern', 'problem record', 'many devices'], 'source': L84 + '; ' + ITIL, 'review': 'Pending SME review'},
}

# reused course misconceptions (curriculum_v2/misconceptions.py)
INSTALL, CLEANVS, UPDIGN = 'MC-IT8-INSTALL-FIRST', 'MC-IT8-CLEAN-VS-INPLACE', 'MC-IT8-UPDATE-IGNORED'
DHCPSVC, REBOOT, HIGHER = 'MC-IT8-DHCP-SERVICE-SYMPTOM', 'MC-IT8-REBOOT-CLEARS', 'MC-IT8-GPO-HIGHER-WINS'
SKEW, EDITION, APPREQ = 'MC-IT8-KERBEROS-SKEW', 'MC-C-IT8-EDITION-FEATURE', 'MC-C-IT8-APP-REQ'
REPAIRTOOL, DESTRUCT, RESETSCOPE = 'MC-C-IT8-REPAIR-TOOL', 'MC-R3-IT8-DESTRUCTIVE-FIRST', 'MC-R5-IT8-RESET-SCOPE'
REVERT, GPORDER, TIMELINE, ISO = 'MC-R5-IT8-REVERT-AS-LOCAL', 'MC-R5-IT8-GPO-ORDER', 'MC-R5-IT8-TIMELINE-TOOL', 'MC-R6-IT8-ISO-MOUNT'
KEEPAPPS, FAT32, BIT64, SFCFIRST, ONEBYONE = ('MC-L-IT8-RESET-KEEPS-APPS', 'MC-L-IT8-FAT32-ANY-SIZE', 'MC-L-IT8-32-RUNS-64',
                                              'MC-L-IT8-SFC-FIRST', 'MC-L-IT8-ONE-BY-ONE')

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
_KEEP = svg(640, 200, 'What each way of reinstalling Windows keeps: repair through Windows Update keeps apps, files and settings; an in-place repair with matching media keeps them too; Reset with Keep my files keeps files only; a clean install keeps nothing',
            label(130, 20, 'keeps →', 12) + label(330, 20, 'apps', 12) + label(430, 20, 'settings', 12) + label(540, 20, 'files', 12)
            + box(10, 32, 240, 34, 'Repair via Windows Update') + label(330, 54, '✓', 16) + label(430, 54, '✓', 16) + label(540, 54, '✓', 16)
            + box(10, 74, 240, 34, 'In-place repair (setup.exe)') + label(330, 96, '✓', 16) + label(430, 96, '✓', 16) + label(540, 96, '✓', 16)
            + box(10, 116, 240, 34, 'Reset — Keep my files') + label(330, 138, '✗', 16) + label(430, 138, '✗', 16) + label(540, 138, '✓', 16)
            + box(10, 158, 240, 34, 'Clean install') + label(330, 180, '✗', 16) + label(430, 180, '✗', 16) + label(540, 180, '✗', 16))

_EDITION = svg(640, 170, 'Choosing by need: list what the PC must do, then pick the lowest edition that does all of it; for a shared drive, list the computers and file sizes, then pick the file system all of them can write',
               box(10, 20, 180, 54, 'What must it do?', 'domain, RDP host, BitLocker') + arrow(190, 47, 230, 47)
               + box(230, 20, 180, 54, 'Home can’t → Pro', 'lowest edition that fits') + arrow(410, 47, 450, 47)
               + box(450, 20, 180, 54, 'Record on asset', 'licence + edition')
               + box(10, 100, 180, 54, 'Who shares the drive?', 'Windows + Mac, 6 GB video') + arrow(190, 127, 230, 127)
               + box(230, 100, 180, 54, 'FAT32 ✗  NTFS ✗', 'size limit / Mac read-only') + arrow(410, 127, 450, 127)
               + box(450, 100, 180, 54, 'exFAT', 'both read and write'))

_GPO = svg(640, 150, 'Group Policy order: local, then site, then domain, then OU from parent to child; each later layer overwrites the same setting from an earlier one, so the OU policy wins by default',
           box(10, 30, 110, 50, 'Local') + arrow(120, 55, 150, 55) + box(150, 30, 110, 50, 'Site') + arrow(260, 55, 290, 55)
           + box(290, 30, 110, 50, 'Domain') + arrow(400, 55, 430, 55) + box(430, 30, 200, 50, 'OU → child OU', 'applied last')
           + label(320, 108, 'same setting in two layers → the one applied LATER wins', 12)
           + label(320, 130, 'exceptions an admin can set: Enforced (keeps a higher GPO) or Block inheritance', 11))

_APP = svg(640, 130, 'Before installing an app: read the vendor requirements, compare them with this PC, choose how it is delivered, review the impact, then install and record the check',
           box(10, 30, 110, 54, 'Requirements', '32/64, GPU, RAM') + arrow(120, 57, 140, 57) + box(140, 30, 110, 54, 'Compare', 'with this PC')
           + arrow(250, 57, 270, 57) + box(270, 30, 110, 54, 'Delivery', 'media, ISO, .msi') + arrow(380, 57, 400, 57)
           + box(400, 30, 110, 54, 'Impact', 'device, network') + arrow(510, 57, 530, 57) + box(530, 30, 100, 54, 'Install', '+ record')
           + label(320, 112, 'a requirement that fails is a decision for the manager, not a surprise after install', 11))

_REPAIR = svg(640, 190, 'Repair follows evidence: date the fault in Reliability Monitor and Event Viewer; if Windows boots run DISM then SFC; if it does not boot use the recovery environment options; then re-test and document',
              box(10, 70, 120, 50, 'Symptom + date') + arrow(130, 95, 160, 95) + box(160, 70, 150, 50, 'What changed?', 'perfmon /rel, Events')
              + arrow(310, 95, 340, 95)
              + box(340, 15, 170, 50, 'Boots → DISM', 'then sfc /scannow') + box(340, 125, 170, 50, 'No boot → WinRE', 'repair, uninstall, restore')
              + arrow(510, 40, 540, 40) + arrow(510, 150, 540, 150) + box(540, 70, 90, 50, 'Re-test') + label(585, 140, '+ document', 11))

_SVC = svg(640, 140, 'A stopped DHCP Client service explains a missing lease: the network card is fine, but the background job that asks for an address is not running',
           box(10, 40, 140, 54, 'Network card', 'cable OK, link up') + arrow(150, 67, 190, 67)
           + box(190, 40, 160, 54, 'DHCP Client service', 'STOPPED') + arrow(350, 67, 390, 67)
           + box(390, 40, 110, 54, 'No request', 'sent') + arrow(500, 67, 530, 67) + box(530, 40, 100, 54, '169.254.x.x')
           + label(320, 122, 'check the service list before blaming the cable, the card or the DHCP server', 12))

_PATTERN = svg(640, 160, 'One failed update is a device ticket; the same error on many devices is a pattern for a problem record and the endpoint team',
               box(10, 20, 190, 54, '1 device, 1 error', 'device ticket') + arrow(200, 47, 240, 47)
               + box(240, 20, 390, 54, 'evidence → least disruptive fix', 'free space · DISM + SFC · remove blocker · WinRE')
               + box(10, 96, 190, 54, '30 devices, same error', 'a pattern') + arrow(200, 123, 240, 123)
               + box(240, 96, 390, 54, 'stop single fixes → problem record', 'escalate common facts: model, driver, KB, error'))

LESSONS = {
    '8.1': {
        'start-here-windows-as-the-shops-default-client': skip(
            'Start here — Windows as the shop’s default client', 'orientation',
            'A start-here block that frames the chapter; the reinstall choice is laddered in the core section.'),

        'core-content': section(
            'Core content', 'IT-8.1',
            [check('A laptop still boots, but a feature update keeps failing with a damaged-file error. Which option keeps the user’s apps and files?',
                   'Reinstall the current version via Windows Update',
                   ['Reset this PC with “Keep my files” selected', 'A clean install from a USB stick after a full backup of the data'],
                   'Reinstalling the current version through Windows Update replaces system files and keeps apps, files and '
                   'settings. Reset with “Keep my files” removes the apps, and a clean install removes everything.',
                   mc=[KEEPAPPS, INSTALL])],
            plain('''<p>“Reinstall Windows” can mean four jobs. Each one keeps a different amount.</p>
<ul><li><strong>Repair through Windows Update</strong>: keeps apps, files and settings. It swaps damaged system files.</li>
<li><strong>In-place repair</strong> (setup.exe with matching media): also keeps apps, files and settings.</li>
<li><strong>Reset this PC</strong>: “Keep my files” keeps only files. Apps and settings go.</li>
<li><strong>Clean install</strong>: keeps nothing on the disk you wipe.</li></ul>
<p>Start with the one that keeps the most. Move down only if it fails. Check the backup and the BitLocker key first.
Check that the PC meets the Windows 11 needs, like TPM 2.0 and Secure Boot.</p>''',
                  L81 + '; ' + MS_RECOVERY,
                  [check('Reset this PC with “Keep my files” finishes. What will the user notice is gone?',
                         'Their installed apps and settings',
                         ['Their documents and photos in the user folders', 'Nothing at all, because Reset only repairs files'],
                         '“Keep my files” keeps personal files and removes apps and settings, so apps must be reinstalled. '
                         'Documents stay, and Reset is more than a file repair.', mc=[KEEPAPPS, CLEANVS])]),
            analogy('''<p>Think of fixing up a flat you live in.</p>
<p><strong>Repair through Windows Update</strong> is a handyman replacing cracked tiles and a dripping tap while all your
furniture and belongings stay put. An <strong>in-place repair</strong> is a bigger refit of the kitchen and bathroom —
still with your things in place, as long as the builder uses the same plan as the flat (matching edition and language).
<strong>Reset this PC, Keep my files</strong> is being moved out, the flat stripped of fittings and furniture, and only
your boxes of personal things carried back in. A <strong>clean install</strong> is knocking the flat back to bare walls
— anything not stored somewhere else first is gone.</p>
<p>You pick the smallest job that will fix the problem, and you check the spare key (the BitLocker key) before work starts.</p>''',
                    L81 + ' (flat-repair analogy written for this rung); ' + MS_RECOVERY,
                    [check('In the flat story, the builder uses a plan for a different flat, so your things cannot stay. What is the Windows match?',
                           'Setup media of a different edition from the installed one',
                           ['A user who has not backed up their personal files', 'A laptop that has run out of free disk space on C:'],
                           'In the lesson, Home media on a Pro PC removed the keep-everything choice. Matching edition, language and '
                           'architecture is what lets an in-place repair keep apps and files.', mc=[CLEANVS, None])]),
            visual(_KEEP + '''
<ol class="ladder-trace">
<li>Does Windows still start? Yes → repair in place first (Windows Update reinstall, or setup.exe with matching media).</li>
<li>Still broken → uninstall the recent update, or restore to an earlier point.</li>
<li>Still broken → Reset this PC, with “Keep my files” when possible.</li>
<li>Last → clean install, only for a new or untrusted drive, after the data is backed up.</li></ol>''',
                   L81 + ' (keep/remove table and least-disruptive ladder, redrawn); ' + MS_RECOVERY,
                   [check('Which ticket in the lesson is the right one for a clean install?',
                          'A replaced SSD with no operating system on it',
                          ['A laptop whose feature update fails at 30 percent', 'A PC with a damaged system file that still boots'],
                          'A new drive has nothing to keep, so a clean install loses nothing. A failing update or damaged file on '
                          'a PC that boots calls for a repair that keeps apps and files.', mc=[INSTALL, DESTRUCT])]),
            tryit('''<p>Put the recovery options in the order Microsoft lists them, from least to most disruptive. Then
predict which option fits the leaver’s laptop before you reveal it.</p>''',
                  L81 + '; ' + MS_RECOVERY,
                  [check('A leaver’s laptop is going to a new starter. Which option fits?',
                         'Reset this PC with “Remove everything”',
                         ['Reset this PC with “Keep my files”', 'Repair the current version through Windows Update'],
                         'The previous user’s files and settings must not carry over, so “Remove everything” (or the '
                         'organisation’s re-image) fits. The other two keep the old user’s data.', mc=[RESETSCOPE, None])],
                  widget=order('Order Microsoft’s recovery options from least to most disruptive.',
                               ['Run a troubleshooter', 'Reinstall the current version through Windows Update',
                                'Uninstall a recent update or go back to the previous version',
                                'Restore to an earlier restore point', 'Reset this PC'],
                               'Each step keeps less of the user’s setup; a clean install sits outside this ladder as a rebuild.'))),

        '1-choose-with-evidence': same_as('core-content', '1. Choose with evidence', 'The same in-place-or-clean choice in three lines.'),
        'clean-versus-in-place': same_as('core-content', 'Clean versus in-place', 'The same comparison of clean and in-place installs.'),
        'teach-block-install-is-a-change': skip('Teach block — install is a change', 'plan', 'An instructor teaching block; the idea is laddered in the core section.'),
        'reference-windows-11-requirements-and-servicing-checked-oct': skip(
            'Reference — Windows 11 requirements and servicing (checked Oct 2026)', 'reference',
            'Lookup tables of requirements and servicing dates, checked against Microsoft each term.'),

        'os-types-file-systems-and-windows-editions': section(
            'OS types, file systems and Windows editions', 'IT-8.1',
            [check('The new reception PC must join the domain and be reached by IT over Remote Desktop. Which is the lowest edition that does both?',
                   'Windows 11 Pro',
                   ['Windows 11 Home', 'Windows 11 Pro for Workstations, for safety'],
                   'Home cannot join an Active Directory domain or host Remote Desktop; Pro does both. Pro for Workstations '
                   'adds features this PC does not need.', mc=[EDITION, None]),
             check('A flash drive must move 6 GB videos between Windows and a Mac, written on both. Which file system?',
                   'exFAT',
                   ['FAT32', 'NTFS'],
                   'exFAT handles files over 4 GB and both systems can read and write it. FAT32 stops at 4 GB per file, and '
                   'NTFS is read-only on a Mac by default.', mc=[FAT32, FAT32])],
            plain('''<p>Pick by what the computer has to do.</p>
<p><strong>Windows editions.</strong> Home is for home use. It cannot join a work domain. It cannot be reached by Remote
Desktop. It has no full BitLocker tools. Pro can do all three. Pick the lowest edition that does every job on the list.</p>
<p><strong>File systems.</strong> NTFS is for Windows disks. FAT32 works almost anywhere, but one file cannot be over 4 GB.
exFAT is for flash drives. Windows and Macs can both read and write it, and it takes big files.</p>
<p><strong>End of life</strong> means no more security fixes. The system still runs, but new holes stay open.</p>''',
                  L81 + '; ' + MS_EDITIONS + '; ' + MS_FS,
                  [check('What does “end of life” mean for an operating system?',
                         'The vendor stops sending security updates for it',
                         ['The computer will no longer start up', 'The licence stops working and must be renewed'],
                         'At end of life the OS keeps running, but no new security fixes arrive, so new holes stay open. It does '
                         'not stop booting or cancel the licence.', mc=['MC-R5-IT8-END-OF-SERVICE', None])]),
            analogy('''<p>Choosing an edition is like choosing a vehicle for a job.</p>
<p>A small car (Home) is fine for one person’s errands. If the job is deliveries for a company — a fleet badge at the
depot gate (domain join), a dispatcher who can take over the controls remotely (Remote Desktop host) and a locked cargo
box with a company key (BitLocker management) — you need the van (Pro). A heavy truck (Pro for Workstations) only pays
off when the load needs it.</p>
<p>A file system is the box you pack things in. FAT32 is a box with a size limit: no single item over 4 GB fits. NTFS is
a box a Mac can open and look into but cannot repack. exFAT is a box both can open, fill and close, with room for big
items.</p>''',
                    L81 + ' (vehicle and packing-box analogy written for this rung); ' + MS_EDITIONS,
                    [check('In the packing-box picture, which file system is “a box a Mac can open but not repack”?',
                           'NTFS',
                           ['exFAT', 'FAT32'],
                           'NTFS is read-only on macOS by default, so the Mac can read but not write. exFAT is read and written by '
                           'both, and FAT32 is writable on both but has the 4 GB item limit.', mc=[FAT32, None])]),
            visual(_EDITION + '''
<ol class="ladder-trace">
<li>Write the needs: join the domain, host Remote Desktop for IT, managed BitLocker keys.</li>
<li>Home fails all three → Pro meets all three.</li>
<li>Pro for Workstations adds nothing this 16 GB, one-CPU PC needs; Enterprise only with volume licensing.</li>
<li>Decision: Windows 11 Pro; record the licence on the asset record.</li></ol>''',
                   L81 + ' (worked example “which edition for the new reception PC?”, drawn)',
                   [check('Which of these needs can Windows 11 Home meet?',
                          'Connecting out to another PC with Remote Desktop',
                          ['Being reached by Remote Desktop from the IT team’s own PCs', 'Joining the Active Directory domain'],
                          'Every edition can connect out to another PC; only Pro and above can be the Remote Desktop host or '
                          'join a domain.', mc=[EDITION, EDITION])]),
            tryit('''<p>Sort the features by edition, then open Settings → System → About in the GUI lab and read which
edition the PC is running before deciding what it can do.</p>''',
                  L81 + '; ' + MS_EDITIONS,
                  [check('A user on Windows 11 Home asks for BitLocker managed by IT. What is the honest first answer?',
                         'Home has device encryption only; managed BitLocker needs Pro',
                         ['Turn on BitLocker in Control Panel, which every edition includes', 'Install the BitLocker app from the Microsoft Store'],
                         'Home offers device encryption on supported hardware, but BitLocker management is a Pro-and-above '
                         'feature, so an edition upgrade is needed. There is no Home BitLocker panel or Store app.', mc=[EDITION, None])],
                  widget=sort('Which edition do you need for each job?',
                              {'Any edition (Home is fine)': ['Connect out with Remote Desktop', 'Join a workgroup at home'],
                               'Pro or above': ['Join an Active Directory domain', 'Host Remote Desktop', 'Manage BitLocker',
                                                'Use gpedit.msc']},
                              'Read the edition in Settings → About first; the edition decides what is possible.'),
                  lab={'id': 'gui-about', 'note': 'Read the edition, version and build in Settings → About.'})),
    },

    '8.2': {
        'core-content': section(
            'Core content', 'IT-8.2',
            [check('A user’s 30-minute screen-lock setting is back to 10 minutes every morning. What should you check before touching the registry?',
                   'gpresult /r, to see which GPO sets it',
                   ['The display driver version in Device Manager', 'Disk health, since settings may not be saving'],
                   'A setting that reverts on every refresh is usually Group Policy, and gpresult shows which GPO applied it. '
                   'Drivers and disks would not reset one setting on a schedule.', mc=[REVERT, None]),
             check('A domain GPO and an OU GPO set the same option differently, with nothing enforced. Which applies?',
                   'The OU GPO, because it is applied later',
                   ['The domain GPO, because it covers more computers', 'Whichever GPO an admin edited most recently'],
                   'Policies apply local, site, domain, then OU, and the later one wins unless an admin enforced a GPO or '
                   'blocked inheritance. Scope size and edit date do not decide it.', mc=[GPORDER, HIGHER])],
            plain('''<p>A <strong>baseline</strong> is a short note of how a PC looks when it is healthy. It has a date. Later,
when something breaks, you compare the PC to that note. Then you are not guessing what “normal” was.</p>
<p>Write the same things each time: the name, edition and build; updates; who is signed in; how it is joined; the
firewall; encryption. Read them in Settings and with commands. Each view catches different mistakes.</p>
<p>On a work network, <strong>Group Policy</strong> sets many settings. It applies in order: local, site, domain, then the
OU. The last one wins. So if a setting keeps changing back, look at the policy first. Do not fight it in the registry.</p>''',
                  L82 + '; ' + MS_GP,
                  [check('Why is a baseline dated?',
                         'So you know what was normal at that time to compare with now',
                         ['So the licence can be renewed on the right day each year', 'So Windows Update knows when it is due to install the next patch'],
                         'A baseline is a snapshot of healthy settings at one time; the date tells you what you are comparing '
                         'against. It has nothing to do with licence renewal or the update schedule.', mc=[REVERT, None])]),
            analogy('''<p>Think of rules at a school.</p>
<p>The country sets some rules, the region adds its own, the school adds more, and each class teacher has a few for their
room. When two levels disagree, the one closest to the classroom is applied last and is the one pupils follow — unless the
country marks a rule “cannot be overridden”. A pupil who changes the clock in the classroom finds it changed back the next
morning, because the rule is reapplied.</p>
<p>Group Policy is the same: local, site, domain, then organisational unit, with the OU last. And a <strong>baseline</strong>
is like the class register on the first day of term — a dated record you check against when something seems off.</p>''',
                    L82 + ' (school-rules analogy written for this rung); ' + MS_GP,
                    [check('In the school story, what matches a rule the country marks “cannot be overridden”?',
                           'A GPO an administrator has set to Enforced',
                           ['The local policy on the user’s own PC', 'The OU GPO, since it is applied last'],
                           'Enforced keeps a higher-level GPO’s setting even though the OU applies later. Without it, the OU GPO '
                           'would win; local policy is applied first and loses.', mc=[GPORDER, None])]),
            visual(_GPO + '''
<ol class="ladder-trace">
<li>Symptom: the lock timeout goes back to 10 minutes each morning.</li>
<li>Run <code>gpresult /r</code> → GPO “Workstation-Security” from the Staff OU applied.</li>
<li>Its lock timeout is 10 minutes → cause: policy, not a fault.</li>
<li>Explain the policy to the user; a business need becomes a request to the policy owner.</li>
<li>No registry edit: the next refresh (about every 90 minutes plus up to 30) would undo it.</li></ol>''',
                   L82 + ' (worked example “my settings keep changing back”, drawn); ' + MS_GP,
                   [check('You edit the registry to undo a policy setting. What will happen?',
                          'The next policy refresh puts the setting back',
                          ['The setting stays until the PC is reimaged', 'The GPO is removed from the OU automatically'],
                          'Domain members reapply policy in the background about every 90 minutes and at start-up, so the policy '
                          'value returns. A registry edit does not change or remove the GPO.', mc=[REVERT, None])]),
            tryit('''<p>Collect a baseline on the simulated endpoint: name, edition and build, update state, the signed-in
account and the adapter. Before you run each command, say which baseline field it fills.</p>''',
                  L82,
                  [check('Which command shows whether the PC is joined to a domain or to Microsoft Entra?',
                         'dsregcmd /status',
                         ['gpupdate /force', 'manage-bde -status'],
                         'dsregcmd /status reports the join state. gpupdate reapplies policy and manage-bde reports BitLocker '
                         'encryption; neither shows how the device is joined.', mc=['MC-C-IT8-GPO-TOOLS', None])],
                  widget=sort('Which view fills each baseline field?',
                              {'Settings': ['System → About for edition and build', 'Accounts → Access work or school'],
                               'Command line': ['winver or Get-ComputerInfo', 'whoami /groups', 'dsregcmd /status']},
                              'Both views describe the same PC; collecting both catches mistakes either one alone would miss.'),
                  lab={'id': 'w11-inventory', 'note': 'Inventory the endpoint and write the baseline fields as you go.'})),

        'baseline-is-a-description': same_as('core-content', 'Baseline is a description', 'The same baseline idea in two lines.'),
        'what-pending-update-does-to-a-ticket': same_as(
            'core-content', 'What pending update does to a ticket',
            'Update state is one of the baseline fields laddered in the core section; this restates how it reads in a ticket.'),

        'installing-applications-to-requirements': section(
            'Installing applications to requirements', 'IT-8.2',
            [check('A CAD package needs a dedicated GPU with 4 GB of VRAM; the laptop has integrated graphics only. What do you do?',
                   'Raise it with the manager before installing',
                   ['Install it anyway, as the installer will not block it', 'Add more RAM, since that replaces the VRAM'],
                   'The requirement fails, so it is a decision for the manager (another laptop or a workstation option), '
                   'recorded on the ticket. Installing anyway hides the failure, and system RAM does not add a dedicated GPU.',
                   mc=[APPREQ, None])],
            plain('''<p>Before you install an app, read what it needs. Then look at the PC.</p>
<ul><li><strong>32-bit or 64-bit.</strong> 64-bit Windows runs most 32-bit apps. 32-bit Windows cannot run a 64-bit app.</li>
<li><strong>Graphics.</strong> Some apps need a separate graphics card and its own memory.</li>
<li><strong>RAM, CPU and disk space.</strong></li>
<li><strong>A USB licence key</strong>, if the app needs one.</li>
<li><strong>Which Windows versions</strong> the maker supports.</li></ul>
<p>An ISO file is a disc in a file. Double-click it and Windows shows it as a drive. Think about the effect on the PC, the
network, support and the business. Write the check on the ticket.</p>''',
                  L82 + '; ' + MS_WOW64 + '; ' + APLUS2,
                  [check('Can a 64-bit application run on 32-bit Windows?',
                         'No; only the reverse works',
                         ['Yes, through the WOW64 layer', 'Yes, if you run it as administrator'],
                         'WOW64 lets 64-bit Windows run most 32-bit apps; it does not work the other way. Running as '
                         'administrator does not change the processor mode the OS runs in.', mc=[BIT64, BIT64])]),
            analogy('''<p>Installing an app is like moving a piano into a flat.</p>
<p>Before the van arrives you check the stairs and the door width (the CPU and 32- or 64-bit), the floor strength
(RAM and storage), and whether the room has the right socket for the lamp that goes with it (a dedicated graphics card).
Some pianos only open with a special key that came separately (a USB licence key) — if it stayed at the old address, the
piano is in but no one can play it.</p>
<p>A good removal firm writes down what it measured before lifting anything, and tells you early if the piano will not
fit, so you can choose another room.</p>''',
                    L82 + ' (piano-move analogy written for this rung)',
                    [check('In the piano story, “the special key stayed at the old address” matches which ticket in the lesson?',
                           'A licensed app says “No licence found” on the new laptop',
                           ['A CAD app that runs slowly on a laptop with integrated graphics', 'A 64-bit app will not start on 32-bit Windows'],
                           'The surveyor’s USB hardware licence key was still in the old PC; moving it fixed the error. The other '
                           'two are graphics and architecture requirements, not tokens.', mc=[APPREQ, None])]),
            visual(_APP + '''
<ol class="ladder-trace">
<li>Vendor says: 64-bit Windows 11, 16 GB RAM, dedicated GPU with 4 GB VRAM.</li>
<li>Laptop: 64-bit Windows 11 ✓, 16 GB RAM ✓, integrated graphics only ✗ (Task Manager → GPU).</li>
<li>The install would succeed, but the performance requirement fails.</li>
<li>Raise it: a laptop with a dedicated GPU, or a workstation or VDI option.</li>
<li>Record the decision on the ticket.</li></ol>''',
                   L82 + ' (worked example “the CAD install that will not start”, drawn)',
                   [check('An application arrives as an .iso file. How do you install it without burning a disc?',
                          'Mount the ISO and run the installer from the new drive',
                          ['Rename the .iso to .exe and double-click it', 'Copy the .iso into Program Files and restart the PC to install it'],
                          'An ISO is a disc image: Windows mounts it as a virtual drive on double-click. Renaming it or copying it '
                          'into Program Files treats it as a program, which it is not.', mc=[ISO, ISO])]),
            tryit('''<p>Predict the answer, then reveal it. Then sort the requirements into the ones you can read on the PC
and the ones you must get from the vendor.</p>''',
                  L82 + '; ' + APLUS2,
                  [check('Which is one of the four impact areas the lesson lists for a new application?',
                         'The network: bandwidth and firewall rules',
                         ['The user’s preferred desktop wallpaper', 'The colour scheme of the installer window'],
                         'The lesson names device, network, operation and business as the impact areas. Wallpaper and installer '
                         'colours have no impact on the rollout.', mc=[APPREQ, None])],
                  widget=reveal('The laptop runs 32-bit Windows and the app is 64-bit only. What happens when the user runs the installer?',
                                'It will not run: 32-bit Windows cannot run a 64-bit application. The fix is 64-bit Windows (often a '
                                'reinstall on suitable hardware) or a 32-bit build of the app, decided before installing.'))),
    },

    '8.3': {
        'core-content': section(
            'Core content', 'IT-8.3',
            [check('Windows boots but system files are damaged. Which order does Microsoft document?',
                   'DISM /RestoreHealth first, then sfc /scannow',
                   ['sfc /scannow first, then DISM /RestoreHealth', 'chkdsk first, then reset the PC if errors remain'],
                   'DISM repairs the component store that SFC copies good files from, so it goes first. Running SFC first can '
                   'fail for lack of good copies, and chkdsk or a reset is not the documented repair.', mc=[SFCFIRST, DESTRUCT])],
            plain('''<p>First find out when it started and what changed.</p>
<p><strong>Reliability Monitor</strong> shows each day. It lists crashes and new installs. It is often the quickest way to
see “slow since Tuesday” next to “a driver was added on Tuesday”. <strong>Event Viewer</strong> has the detail. Copy the
event source and ID into the ticket.</p>
<p>If Windows starts, repair its files in two steps. Run DISM first. It fixes the store of good copies. Then run SFC. It
swaps bad system files for good ones from that store.</p>
<p>If Windows will not start, use the recovery screens. You can repair start-up, remove the last update, or go back to a
restore point. Keep a reset for last.</p>''',
                  L83 + '; ' + MS_SFC + '; ' + MS_RECOVERY,
                  [check('Where do you look first to tie “slow since Tuesday” to a change?',
                         'Reliability Monitor (perfmon /rel)',
                         ['Disk Management, to check the partitions', 'BitLocker settings, to check the encryption'],
                         'Reliability Monitor puts crashes and installs on one timeline by day. Disk Management and BitLocker show '
                         'storage and encryption, not when something changed.', mc=[TIMELINE, None])]),
            analogy('''<p>Think of a library that keeps a master copy of every book in a locked room.</p>
<p>When readers report torn pages, a librarian swaps the damaged copies for clean ones from the master room — that is
<strong>SFC</strong>. But if the master room itself has damp, the swaps just hand out more damaged pages. So first the
conservator repairs the master room — that is <strong>DISM</strong>, fixing the component store. Then the swaps work.</p>
<p>Before any of that, the head librarian checks the visitor log to see what changed the day the complaints started — that
is <strong>Reliability Monitor</strong> and <strong>Event Viewer</strong>. And if the library will not open at all, there is a
back door for staff — the <strong>recovery environment</strong>.</p>''',
                    L83 + ' (library analogy written for this rung); ' + MS_SFC,
                    [check('In the library story, why does the conservator fix the master room before the swaps?',
                           'Swaps from a damaged store hand out more damaged copies',
                           ['The conservator is paid more than the librarian', 'Readers must leave the library before any swaps can be started'],
                           'SFC copies files from the component store; if the store is damaged it cannot supply good copies, so DISM '
                           'repairs the store first. Pay and readers leaving are not part of the reason.', mc=[SFCFIRST, None])]),
            visual(_REPAIR + '''
<ol class="ladder-trace">
<li>Reliability Monitor: “Windows failure” every day since 14 Oct, and a printer driver install that morning.</li>
<li>Event Viewer, System log: a BugCheck after each crash; the dump points at a file from the printer package.</li>
<li>Plan: Safe Mode, uninstall the driver package, restart normally; rollback is the previous driver saved in the ticket.</li>
<li>Result: no crash over two days; the user prints with the current driver from the print server.</li>
<li>Document it and tell the printer team about the faulty package.</li></ol>''',
                   L83 + ' (worked example “blue screen after a printer driver”, drawn)',
                   [check('A driver install broke start-up. Which recovery option undoes it and keeps personal files?',
                          'System Restore to a point before the install',
                          ['Reset this PC with “Remove everything”, then reinstall the apps', 'A clean install from USB media'],
                          'System Restore rolls back system files, drivers and settings to a restore point and keeps personal '
                          'files. A reset or clean install removes far more than the driver.', mc=[DESTRUCT, REPAIRTOOL])]),
            tryit('''<p>Put the repair steps in order for a PC that still boots, then sort the recovery options by what they
change.</p>''',
                  L83 + '; ' + MS_SFC,
                  [check('sfc reports “found corrupt files but was unable to fix some of them”. What is the next step?',
                         'Run DISM again with a known-good source, then SFC',
                         ['Ignore it, as SFC fixed most of the files', 'Delete the damaged files by hand from System32 and run SFC again'],
                         'The store could not supply good copies, so DISM needs a known-good source (such as mounted media) before '
                         'SFC can finish. Ignoring it leaves damage; deleting system files by hand makes it worse.', mc=[SFCFIRST, DESTRUCT])],
                  widget=order('Order the repair for a PC that boots but has damaged system files.',
                               ['Note the symptom and the date it began', 'Find what changed in Reliability Monitor',
                                'Run DISM /Online /Cleanup-Image /RestoreHealth', 'Run sfc /scannow to 100%',
                                'Restart and re-test the user’s outcome'],
                               'Evidence first, then the store, then the files, then the user’s own test.'))),

        'services-are-background-jobs': section(
            'Services are background jobs', 'IT-8.2',
            [check('A PC shows 169.254.x.x and the cable and switch port are fine. Which service do you check?',
                   'DHCP Client',
                   ['Print Spooler', 'Windows Search'],
                   'The DHCP Client service asks the server for an address; if it is stopped, no lease arrives and Windows '
                   'falls back to 169.254.x.x. The spooler and search services have nothing to do with addressing.', mc=[DHCPSVC, None])],
            plain('''<p>A service is a program that runs in the background. It runs even when no one is signed in.</p>
<p>Some of them do jobs you rely on. The <strong>DHCP Client</strong> asks for an address. The <strong>DNS Client</strong>
looks up names. <strong>Defender</strong> watches for malware.</p>
<p>If one stops, things break in odd ways. With DHCP Client stopped, the PC gets no address. Then ipconfig looks wrong
for no clear reason.</p>
<p>List the services and processes before you reboot. A reboot is a change. After it you cannot see what was running.</p>''',
                  L83 + ' (services depth block); ' + MS_SERVICES,
                  [check('Why list processes and services before rebooting?',
                         'A reboot changes the state and wipes the evidence',
                         ['A reboot always fixes a stopped service anyway', 'Windows blocks reboots until the list is saved'],
                         'After a restart you can no longer see what was running or stopped at the time of the fault. A reboot '
                         'does not always fix it, and Windows does not require the list.', mc=[REBOOT, None])]),
            analogy('''<p>Think of the staff in a hotel who work while guests sleep.</p>
<p>Guests never see the night porter, the laundry or the boiler engineer, but if one of them stops, the morning goes wrong
in strange ways: cold showers, no towels, a locked door. You would not rebuild the bathroom for a cold shower — you would
check whether the boiler engineer turned up.</p>
<p>Windows services are that night staff. The DHCP Client is the porter who collects the room key (the address) from
reception; if he does not show up, the guest is left with a temporary key that opens nothing useful (169.254.x.x).</p>''',
                    L83 + ' (hotel-staff analogy written for this rung)',
                    [check('In the hotel story, the boiler engineer did not turn up. What is the Windows match?',
                           'A background service that should be running is stopped',
                           ['A user account that has been locked out overnight', 'A network cable that was unplugged from the PC'],
                           'The night staff are background services; one not running causes odd symptoms elsewhere. A locked account '
                           'or a loose cable is a different domain.', mc=[DHCPSVC, None])]),
            visual(_SVC + '''
<ol class="ladder-trace">
<li>Symptom: ipconfig shows 169.254.x.x; the link light is on.</li>
<li>Open the services list (services.msc or <code>Get-Service</code>) before changing anything.</li>
<li>DHCP Client shows Stopped → that explains the missing lease.</li>
<li>Start it (with approval if policy needs it), renew the lease, re-test.</li>
<li>Note the service state before and after in the ticket.</li></ol>''',
                   L83 + ' (services depth block, drawn as a chain)',
                   [check('In the chain picture, what is the first thing to check after the link light?',
                          'The DHCP Client service state',
                          ['A new network card from the spares cupboard', 'The DHCP server’s address pool'],
                          'With a working link, the next link in the chain is the local service that sends the request. Swapping the '
                          'card or blaming the server skips a cheap local check.', mc=[DHCPSVC, None])]),
            tryit('''<p>Check service health in the Windows lab: find which required service is not running before you
change anything, and record its state.</p>''',
                  L83,
                  [check('Which of these is a background service, not a program the user opens?',
                         'DNS Client',
                         ['Microsoft Word', 'File Explorer'],
                         'DNS Client runs in the background whether or not anyone is signed in, and resolves names. Word and File '
                         'Explorer are programs the user starts.', mc=[DHCPSVC, None])],
                  widget=reveal('Before you look: which service would explain “ping by IP works, but every name fails”?',
                                'The DNS Client service (or the DNS server it points to). The DHCP Client is not the suspect, because '
                                'the PC has an address and reaches IPs.'),
                  lab={'id': 'w11-services', 'note': 'Find the stopped service and record its state before and after.'})),
    },

    '8.4': {
        'core-content': section(
            'Core content', 'IT-8.3',
            [check('The same update error appears on 30 laptops of one model. What do you do?',
                   'Stop single fixes; open a problem record and escalate',
                   ['Run DISM and SFC on each laptop as its ticket arrives in the queue', 'Reset each laptop with “Keep my files” selected'],
                   'Many devices with one error is a pattern; linking the tickets to a problem record lets the endpoint team '
                   'fix the cause once. Repairing or resetting each device repeats the work.', mc=[ONEBYONE, DESTRUCT])],
            plain('''<p>The story: a PC restarted three times overnight. Windows Update says the update failed. The user can
still sign in. You have 45 minutes.</p>
<p>First, read the update history. It shows the update’s KB number and the error code. Then check the usual causes.
Is the C: drive nearly full? Are update files damaged? Did a new driver or security tool block it?</p>
<p>Fix the one thing the evidence points at. Then retry the update. You are done when the update shows as installed, the
build is right, and the user says their apps work.</p>
<p>If many PCs show the same error, stop fixing them one by one. Report the pattern.</p>''',
                  L84 + '; ' + MS_RECOVERY,
                  [check('Where do you find the KB number and error code of a failed update?',
                         'Settings → Windows Update → Update history',
                         ['Device Manager, under the display adapter', 'Task Manager, on the Startup tab'],
                         'Update history lists each update with its KB number and result code. Device Manager and Task Manager do '
                         'not record update results.', mc=[UPDIGN, None])]),
            analogy('''<p>Think of a parcel that will not deliver.</p>
<p>The tracking page (Update history) tells you which parcel and why: “address damaged”, “no room in the letterbox”,
“refused at the door”. Each reason has its own fix — correct the label (DISM and SFC), empty the letterbox (free disk
space), or ask the building’s guard to let it through (a driver or security tool, with its owner’s approval). You do
not tear down the house because one parcel failed.</p>
<p>If a whole street reports the same failed parcel, it is not one door’s problem. The courier depot (the endpoint team)
needs one report with the shared facts, not thirty separate complaints.</p>''',
                    L84 + ' (parcel-delivery analogy written for this rung)',
                    [check('In the parcel story, “no room in the letterbox” matches which evidence?',
                           'C: has only a few gigabytes free',
                           ['The error code says files are damaged', 'A new security tool was installed last week'],
                           'A full letterbox is low free space on C:, fixed with Storage Sense or Disk Cleanup before a retry. '
                           'Damaged files and a blocking tool are different reasons with different fixes.', mc=[UPDIGN, None])]),
            visual(_PATTERN + '''
<ol class="ladder-trace">
<li>Identify: one device or many? Which KB and which error (Update history)?</li>
<li>Test the usual causes: free space on C:, damaged files, a new driver or security tool, a pending restart, network or proxy.</li>
<li>Change one thing: free space, or DISM then SFC, or remove the blocker with its owner; retry in an agreed window.</li>
<li>Verify: Update history shows installed, <code>winver</code> shows the expected build, the user’s apps work.</li>
<li>Same error on many devices → problem record and escalate the pattern.</li></ol>''',
                   L84 + ' (capstone table and “thirty laptops, one error”, drawn); ' + ITIL,
                   [check('After the retry, which pair proves the update fix?',
                          'Update history shows installed; winver shows the right build',
                          ['The PC restarts without a message and the fans are quiet', 'Event Viewer shows no new errors in the hour after the restart'],
                          'The lesson’s verification is the update recorded as installed, the right build number and the user’s '
                          'apps working. A quiet restart or a clean hour of logs is only supporting evidence.', mc=[UPDIGN, None])]),
            tryit('''<p>Sort each piece of evidence to the fault domain it points at, then look at the update history in
the Windows Update GUI lab.</p>''',
                  L84,
                  [check('The failed update has stopped the PC from starting at all. What comes first?',
                         'WinRE → Uninstall Updates',
                         ['A clean install from USB media', 'Disk Cleanup to free more space'],
                         'For a device that no longer starts after an update, the recovery environment can remove that update '
                         'first. A clean install is a last resort, and Disk Cleanup needs Windows running.', mc=[DESTRUCT, None])],
                  widget=sort('Which domain does each piece of evidence point at?',
                              {'Component store': ['Error says files are missing or damaged'],
                               'Storage': ['C: has less than a few GB free'],
                               'Driver or third-party software': ['Failure began after a new driver was installed'],
                               'Policy, network or the update itself': ['Same error on 30 devices in one OU']},
                              'The evidence names the domain; the domain names the least disruptive next step.'),
                  lab={'id': 'gui-update', 'note': 'Read Windows Update and its history; note the KB number and result.'})),

        'failed-update-capstone': same_as('core-content', 'Failed update capstone', 'The same capstone as a checklist.'),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '8.1': {'core-content': '437cb63af39e', 'os-types-file-systems-and-windows-editions': '3a1d8f4f0e3a'},
    '8.2': {'core-content': '17bce7af2b16', 'installing-applications-to-requirements': '4a6c8b8eef52'},
    '8.3': {'core-content': 'c30f458bbff0', 'services-are-background-jobs': '11b475916cd7'},
    '8.4': {'core-content': '0ce7b8cf7d0d'},
}

# ---------------------------------------------------------------- refinement pass 20: former skips, now laddered
from curriculum_v2.ladder.itsup._lk import P as _P, X as _X  # noqa: E402

_LUP = ('gui-update', 'Read the update state and history before deciding on any repair or install.')
LESSONS['8.1'].update({
    'start-here-windows-as-the-shops-default-client': _X('Start here — Windows as the shop’s default client', 'IT-8.1', L81, [
        ('A PC never gets past POST. Does it need setup.exe?', 'No; it is a hardware fault', 'Yes; reinstall Windows', 'Yes; run an in-place upgrade',
         'If the box never leaves POST, Windows has not even started, so installing it cannot help.', INSTALL, INSTALL),
        ('What comes before any Windows install or repair?', 'Inventory: name, edition, disks', 'Formatting the system drive', 'Ordering a new licence key',
         'Install and repair are changes, so you record what the box is first.', INSTALL, CLEANVS),
        ('In the house-renovation story, why survey first?', 'You must know what is there', 'Surveys look professional', 'Builders like paperwork',
         'You record the current state before changing it, like an inventory.', INSTALL, None),
        ('In the trace, what is update status?', 'Part of describing the box', 'Trivia to skip', 'Only for servers',
         'Update state is part of the inventory, not an afterthought.', UPDIGN, UPDIGN),
        ('Install and repair of Windows are…', 'Changes', 'Quick fixes', 'Requests from users',
         'They alter the system state and follow the change habits.', INSTALL, None),
    ],
        _P('Most office desks in this course run Windows. Installing or repairing Windows counts as a change, so first write down the computer’s '
           'name, Windows edition and disks. A computer that never gets past the power-on test does not need the Windows installer, because Windows '
           'never even started. Which updates are installed is part of describing the computer, not a minor detail.'),
        _P('Before builders renovate a house, a surveyor walks through: which walls hold the roof up, where the pipes and wires run, how old the '
           'boiler is. Nobody knocks down a wall first and checks later. And if the problem is a cracked foundation, new wallpaper will not help. '
           'Inventory is the survey; reinstalling Windows is the renovation; a box stuck in POST is the cracked foundation.'),
        ['Does it pass POST? If not, stay in hardware.', 'Record name, edition, disks.', 'Record update state.', 'Only then plan install or repair.'],
        '<p>Order the checks before touching Windows.</p>',
        order('Before install or repair', ['Check POST', 'Record name and edition', 'Record disks', 'Record update state', 'Plan the change'],
              'Inventory before change.'), _LUP),
    'teach-block-install-is-a-change': _X('Teach block — install is a change', 'IT-8.1', L81, [
        ('What sits in the middle of the in-place versus clean board?', 'Data risk', 'Installation speed', 'Screen resolution',
         'The choice hinges on what happens to user data.', CLEANVS, CLEANVS),
        ('Is a MEM beep a reason to run setup.exe?', 'No; it is hardware', 'Yes; it fixes drivers', 'Yes; after a reboot',
         'A memory beep is a POST hardware fault, not an OS problem.', INSTALL, INSTALL),
        ('In the moving-house story, why pack valuables first?', 'They are hardest to replace', 'They are light to carry', 'Movers ask for them',
         'Data risk drives the choice, like protecting valuables before a move.', CLEANVS, None),
        ('Trace step 1 is…', 'Inventory', 'Clean install', 'Delete partitions',
         'Inventory always comes first.', INSTALL, None),
        ('Is a clean install done in class?', 'No', 'Yes, once each', 'Yes, on the host PC',
         'No clean installs in class; the board discussion is the practice.', DESTRUCT, None),
    ],
        _P('In this teaching block: take an inventory first. A memory beep is a hardware fault and setup.exe will not fix it. On the board, '
           'compare an in-place upgrade with a clean install, with the risk to user data written in the middle. Nobody does a clean install in class.'),
        _P('When you move house, you do not throw everything in a skip and buy new. You decide what comes with you, starting with the things you '
           'cannot replace: photos, documents, the family ring. An in-place upgrade is moving with your belongings; a clean install is starting '
           'over in an empty flat. Data is the family ring, so it sits in the middle of the decision.'),
        ['Inventory first.', 'MEM beep? Hardware, not setup.exe.', 'Compare in-place and clean.', 'Write data risk in the middle.', 'No clean install in class.'],
        '<p>Sort the facts into in-place or clean.</p>',
        sort('In-place or clean?', {'In-place': ['Keeps apps and files', 'Less data risk'], 'Clean': ['Wipes the drive', 'Needs a verified backup first']},
             'Data risk is the deciding line.'), _LUP),
    'reference-windows-11-requirements-and-servicing-checked-oct': _X('Reference — Windows 11 requirements and servicing (checked Oct 2026)', 'IT-8.1', L81, [
        ('Which security chip does Windows 11 require?', 'TPM 2.0', 'TPM 1.2 or none', 'A smart-card reader',
         'Windows 11 needs TPM 2.0, plus UEFI and Secure Boot capability.', APPREQ, None),
        ('How long is a Home/Pro feature update serviced?', '24 months', '36 months', '10 years',
         'Home/Pro get 24 months; Enterprise/Education get 36.', EDITION, None),
        ('In the car-MOT story, why check before promising?', 'Not every car passes', 'Tests are free', 'Mechanics like forms',
         'Check a PC with PC Health Check before promising an upgrade.', APPREQ, None),
        ('Which tool checks a PC before promising an upgrade?', 'PC Health Check', 'Disk Cleanup', 'Task Manager',
         'PC Health Check (or your management tool) verifies the requirements.', APPREQ, None),
        ('When did Windows 10 reach end of support?', '14 October 2025', '1 January 2030', 'It never will',
         'Windows 10 ended support on 14 October 2025; only enrolled devices get extended security updates.', UPDIGN, None),
    ],
        _P('Windows 11 needs a 64-bit processor from Microsoft’s list with at least two cores, 4 GB of memory, 64 GB of storage, UEFI with Secure '
           'Boot, a TPM 2.0 chip and DirectX 12 graphics. Check a PC with PC Health Check before promising an upgrade. Each yearly feature update '
           'gets 24 months of updates on Home and Pro, 36 on Enterprise and Education. Windows 10 support ended on 14 October 2025.'),
        _P('Before you promise someone their old car will be fine for a long road trip, you take it for its safety inspection. Some cars pass, '
           'some need parts, some are simply too old. Telling the owner “it’ll be fine” without checking is how they end up stranded. PC Health '
           'Check is the inspection for Windows 11, and the servicing dates are the expiry on the inspection certificate.'),
        ['Run PC Health Check.', 'Confirm CPU on the supported list, 4 GB RAM, 64 GB disk.', 'Confirm UEFI, Secure Boot, TPM 2.0.',
         'Check the version and its end-of-servicing date.', 'Only then promise the upgrade.'],
        '<p>Decide whether this PC can upgrade.</p>',
        reveal('PC: 8 GB RAM, 256 GB SSD, TPM 1.2, legacy BIOS. Upgrade?', 'Not yet: Windows 11 needs TPM 2.0 and UEFI with Secure Boot. Check firmware options or plan a replacement.'), _LUP),
})

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '8.1': {'start-here-windows-as-the-shops-default-client': '25c9270119ab', 'core-content': '437cb63af39e', 'teach-block-install-is-a-change': 'c12433064c59', 'reference-windows-11-requirements-and-servicing-checked-oct': '855b2e5390bf', 'os-types-file-systems-and-windows-editions': '3a1d8f4f0e3a'},
    '8.2': {'core-content': '17bce7af2b16', 'installing-applications-to-requirements': '4a6c8b8eef52'},
    '8.3': {'core-content': 'c30f458bbff0', 'services-are-background-jobs': '11b475916cd7'},
    '8.4': {'core-content': '0ce7b8cf7d0d'},
}
