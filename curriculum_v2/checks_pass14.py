"""Pass 14: chapter-check items for the ITSUP objectives that had none (IT-7.4, 8.4, 9.4, 10.4, 11.4, 12.4, 13.4).

Two items per objective, appended to the end of each chapter check (pilot_slice.PILOT_CHECKS[ch][10:12]), so
existing item positions, bank ids (Q<ch>.<i>) and stored attempts are unchanged. Every item is answerable from
the lesson sections the mastery engine maps to its objective, and every fact was checked against a primary
source (listed per item in SOURCE). Wording is original. Stems do not repeat the X-IT bank items or the lesson
"check for understanding" questions. All items are tagged Pending SME review.

RAW[ch] = list of (stem, options, correct, focus, study_tip) in the pilot_slice._q format.
REVIEW[key] = (objective, rationale) — merged into curriculum_v2.item_review.REVIEW with fix = PENDING.
"""

PENDING = 'new chapter-check item (pass 14) — Pending SME review'

RAW = {
    7: [
        ('You escalate a VPN ticket to the identity team. Which part of the package tells them what you changed on the PC and whether it is still changed?',
         ['Impact and priority', 'Scope', 'The request', 'Current state'], 'Current state', 'Escalation package', '7.3.'),
        ('You hand a ticket to the network team. What should the user hear from you before you hang up?',
         ['Nothing until the network team has fixed it and closed the ticket', 'Who has it now, what is needed from them, and when the next update is',
          'Your best guess at the root cause, so that they feel reassured for now', 'To restart the PC every hour and call back if it still fails after that'],
         'Who has it now, what is needed from them, and when the next update is', 'Keeping users informed', '7.3 / 7.4.'),
    ],
    8: [
        ('A domain-level GPO and an OU-level GPO set the same option to different values. Neither is enforced and inheritance is not blocked. Which value applies?',
         ['The domain GPO, because it is higher in the tree', 'The OU GPO, because it is applied later', 'Whichever GPO was created most recently',
          'The local policy, because it lives on the PC'], 'The OU GPO, because it is applied later', 'Group Policy order', '8.2.'),
        ('Which command lists the GPOs that applied to the computer and the signed-in user, and the ones that were filtered out?',
         ['gpupdate /force', 'dsregcmd /status', 'gpresult /r', 'w32tm /query /status'], 'gpresult /r', 'Group Policy evidence', '8.2.'),
    ],
    9: [
        ('A Mac user can open files on an NTFS-formatted external drive but cannot save changes to it. What explains this?',
         ['macOS reads NTFS but cannot write to it without extra software', 'The drive is failing and the disk has switched itself to read-only', 'FileVault blocks writes to every external drive connected to a Mac',
          'NTFS drives must be repaired with First Aid in Disk Utility first'], 'macOS reads NTFS but cannot write to it without extra software', 'Cross-platform file systems', '9.4.'),
        ('A Linux share holds both Plan.docx and plan.docx. What does a Windows user browsing the share usually see?',
         ['Both files, listed side by side under their original names and sizes', 'Only one, as Windows treats names case-insensitively by default',
          'An error message, because SMB cannot share folders that live on Linux', 'Two copies of whichever file was saved most recently, under one name'],
         'Only one, as Windows treats names case-insensitively by default', 'Case sensitivity', '9.4.'),
    ],
    10: [
        ('Security asks you to leave a suspected compromised PC switched on and not to shut it down. Why?',
         ['Shutting down would start an automatic reimage of the whole system', 'Memory contents and live network connections are lost at power-off',
          'Shutting down would send the event logs to Microsoft automatically', 'Windows Update would install pending updates and restart the PC twice'],
         'Memory contents and live network connections are lost at power-off', 'Order of volatility', '10.4.'),
        ('Which sequence follows the RFC 3227 order of volatility (most volatile first)?',
         ['Disk, memory, temporary files, archival media', 'Archival media, disk, temporary files, memory', 'Temporary files, disk, memory, archival media',
          'Memory, temporary files, disk, archival media'], 'Memory, temporary files, disk, archival media', 'Order of volatility', '10.4.'),
    ],
    11: [
        ('A fault disappears when the PC is started in Safe Mode. What does that point to?',
         ['A driver, service or startup program that Safe Mode does not load', 'Failing hardware, such as the RAM or the system disk, in the PC',
          'Damage to the documents and files saved in the user’s profile', 'A fault in the core Windows kernel, which loads in every boot mode'],
         'A driver, service or startup program that Safe Mode does not load', 'Safe Mode', '11.2.'),
        ('A Store app crashes on launch. Which option fixes its files but keeps its data?',
         ['Reset, in the app’s Advanced options', 'Repair, in the app’s Advanced options', 'Network reset, in Settings', 'Uninstalling and reinstalling the app'],
         'Repair, in the app’s Advanced options', 'App repair or reset', '11.2.'),
    ],
    12: [
        ('How should the title of a knowledge-base article for a known fault be written?',
         ['As the internal problem-record number, with nothing else', 'In the technician’s own shorthand', 'In the user’s words, describing the symptom', 'As the name of the fix'],
         'In the user’s words, describing the symptom', 'KB articles', '12.4.'),
        ('A working laptop moves from the reception desk to the spares cupboard. What changes in its asset record?',
         ['Status and location (spare, in stores), with the ticket linked', 'A new asset tag is issued, because the device has a new home', 'Nothing changes until the laptop is finally disposed of', 'Its serial number is updated to match the new location'],
         'Status and location (spare, in stores), with the ticket linked', 'Asset records', '12.4.'),
    ],
    13: [
        ('A laptop shows a 169.254.x.x address after a cable move. Which is the least disruptive first step?',
         ['netsh winsock reset, then restart', 'Settings → Network & internet → Network reset', 'ipconfig /release, then ipconfig /renew', 'Reinstall the network adapter driver'],
         'ipconfig /release, then ipconfig /renew', 'Network reset ladder', '13.3.'),
        ('WMIC has been removed from current Windows 11. Which PowerShell command gives a summary of the IP address, gateway and DNS servers per adapter?',
         ['Get-NetIPConfiguration', 'Restart-NetAdapter', 'Clear-DnsClientCache', 'Get-DnsClientCache'], 'Get-NetIPConfiguration', 'PowerShell evidence', '13.2 / 13.3.'),
    ],
}

REVIEW = {
    'Q7.10': ('IT-7.4', 'The escalation package has six parts: impact and priority, scope, evidence, actions → results, current state and the request. Current state is the part that says what you changed and whether it is still changed, so the owning team knows the starting point.'),
    'Q7.11': ('IT-7.4', 'When you escalate, tell the user who has the ticket now, what (if anything) is needed from them, and when they will next hear. Silence and guessed causes both damage trust; restarts are not a plan.'),
    'Q8.10': ('IT-8.4', 'GPOs are processed local, site, domain, then OU (parent to child). Where two set the same option, the one applied later — the OU GPO — wins unless a GPO is enforced or inheritance is blocked. Creation date does not matter.'),
    'Q8.11': ('IT-8.4', 'gpresult /r shows the Resultant Set of Policy summary for the computer and user, including the GPOs that applied and those filtered out. gpupdate /force reapplies policy; dsregcmd /status shows join state; w32tm shows time sync.'),
    'Q9.10': ('IT-9.4', 'macOS can read NTFS volumes but does not write to them natively; writing needs a third-party driver, or use exFAT for a drive shared between systems. Nothing in the symptom suggests failure or FileVault.'),
    'Q9.11': ('IT-9.4', 'Linux file names are case-sensitive, so two files can differ only by case. Windows treats names case-insensitively by default, so it shows only one of them. The fix is a naming rule on the Linux side, not a Windows repair.'),
    'Q10.10': ('IT-10.4', 'RFC 3227 puts memory, the process table and network state near the top of the order of volatility: they vanish at power-off, so “don’t switch it off” preserves evidence. Shutdown does not wipe or reimage a disk.'),
    'Q10.11': ('IT-10.4', 'RFC 3227 lists registers and cache; routing and ARP tables, the process table and memory; temporary file systems; disk; remote logging; physical configuration; archival media. Memory → temporary files → disk → archival media keeps that order.'),
    'Q11.10': ('IT-11.4', 'Safe Mode starts Windows with a minimal set of drivers and services. If the fault disappears there, something Safe Mode does not load — a driver, service or startup program — is involved; a fault that remains points at the core OS, hardware or user data.'),
    'Q11.11': ('IT-11.4', 'For Store and many built-in apps, Settings → Apps → Installed apps → Advanced options offers Repair (fixes the app; its data is not affected) and Reset (also deletes the app’s data on this device). Reinstalling removes local data too.'),
    'Q12.10': ('IT-12.4', 'A KB title in the user’s words matches what the next technician will search for when the same symptom is reported. Problem numbers, shorthand and fix names do not match how the fault is reported.'),
    'Q12.11': ('IT-12.4', 'An asset record tracks a device through its life: status (in use, in repair, spare, disposed) and location/owner change when it moves, with the ticket linked. The tag and serial stay the same; disposal is a different status.'),
    'Q13.10': ('IT-13.4', 'Climb the reset ladder one rung at a time: renewing the lease (rung 1) only drops and re-requests the DHCP address. A stack reset, a full network reset and a driver reinstall undo far more configuration.'),
    'Q13.11': ('IT-13.4', 'Microsoft removed the WMIC utility from Windows 11 24H2 and later (WMI itself remains). Get-NetIPConfiguration (NetTCPIP module) summarises addresses, gateway and DNS servers per adapter; the other cmdlets restart an adapter, clear the DNS cache, or list only the DNS server addresses per interface (Get-DnsClientServerAddress), not the addresses and gateway.'),
}

SOURCE = {
    'Q7.10': 'Course lesson 7.3 (escalation package); local practice — SME to confirm.',
    'Q7.11': 'Course lessons 7.3/7.4; local practice — SME to confirm.',
    'Q8.10': 'Microsoft Learn, Group Policy processing (order local, site, domain, OU; later wins unless enforced/blocked).',
    'Q8.11': 'Microsoft Learn, gpresult command reference (/r displays RSoP summary data).',
    'Q9.10': 'Apple Support, file system formats available in Disk Utility (macOS reads but cannot write NTFS).',
    'Q9.11': 'Microsoft Learn, case sensitivity in Windows (case-insensitive by default; per-directory option); Linux ext4 is case-sensitive.',
    'Q10.10': 'IETF RFC 3227, Guidelines for Evidence Collection and Archiving, section 2.1 (order of volatility).',
    'Q10.11': 'IETF RFC 3227, section 2.1.',
    'Q11.10': 'Microsoft Support, Start your PC in safe mode in Windows (minimal set of files and drivers).',
    'Q11.11': 'Microsoft Support, Repair apps and programs in Windows (Repair keeps data; Reset deletes app data).',
    'Q12.10': 'Course lesson 12.4 (KB fields); KCS practice of capturing the requester’s context — SME to confirm.',
    'Q12.11': 'Course lesson 12.4 (asset record fields and statuses); local practice — SME to confirm.',
    'Q13.10': 'Microsoft Learn, ipconfig command reference (/release, /renew); course lesson 13.3 reset ladder.',
    'Q13.11': 'Microsoft Support, WMIC removal from Windows (Aug 2026); Microsoft Learn, Get-NetIPConfiguration (NetTCPIP).',
}

STEMS = {f'Q{ch}.{10 + i}': ' '.join(r[0].split()[:6]) for ch, rows in RAW.items() for i, r in enumerate(rows)}


def extend(checks, make):
    """Append the new items to PILOT_CHECKS (idempotent)."""
    for ch, rows in RAW.items():
        bank = checks.setdefault(ch, [])
        have = {q['q'] for q in bank}
        for stem, options, correct, focus, tip in rows:
            assert correct in options and len(options) == 4 and len(set(options)) == 4, stem
            if stem not in have:
                bank.append(make(stem, list(options), correct, focus, tip))


# ---------------------------------------------------------------- misconception tags (pass-11 rules)
# A distractor is tagged only when the wrong idea it stands for is clear from the item, its key and its rationale.
# Labels describe the wrong belief and add no new curriculum facts. Pending SME review.
def _m(obj, label, fix, terms):
    return {'obj': obj, 'label': label, 'fix': fix, 'terms': terms}


MISCONCEPTIONS = {
    'MC-IT7-PACKAGE-PARTS': _m('IT-7.4', 'Mixing up the parts of an escalation package (impact, scope, request) with the current state of the device',
                               'Current state says what you changed and whether it is still changed; impact, scope and the request are separate parts.',
                               ['current state', 'escalation', 'package', 'request']),
    'MC-IT7-SILENT-ESCALATION': _m('IT-7.4', 'Thinking the user needs no update, or a guessed cause, once the ticket is escalated',
                                   'Tell the user who has the ticket now, what is needed from them and when they will next hear.',
                                   ['status update', 'escalate', 'user', 'next update']),
    'MC-IT8-GPO-HIGHER-WINS': _m('IT-8.4', 'Believing the higher-level (domain) or newest GPO wins over an OU GPO',
                                 'GPOs apply local, site, domain, then OU; the later one (the OU GPO) wins unless enforced or blocked.',
                                 ['group policy', 'gpo', 'ou', 'order']),
    'MC-IT8-WRONG-GP-TOOL': _m('IT-8.4', 'Using gpupdate, dsregcmd or w32tm to list which GPOs applied',
                               'gpresult /r lists the applied and filtered GPOs; gpupdate reapplies them.', ['gpresult', 'gpupdate', 'applied', 'filtered']),
    'MC-IT9-NTFS-READONLY-AS-FAULT': _m('IT-9.4', 'Reading macOS’s native NTFS read-only behaviour as a failing or locked drive',
                                        'macOS reads NTFS but does not write it natively; use exFAT for shared drives.', ['ntfs', 'macos', 'read only', 'exfat']),
    'MC-IT9-CASE-BLIND': _m('IT-9.4', 'Expecting Windows to show two files whose names differ only by case, or blaming SMB',
                            'Linux names are case-sensitive; Windows is case-insensitive by default and shows only one.', ['case', 'linux', 'windows', 'share']),
    'MC-IT10-SHUTDOWN-HARMLESS': _m('IT-10.4', 'Not seeing that power-off destroys volatile evidence (memory, connections)',
                                    'Memory and network state vanish at power-off, so they are collected first and the PC stays on.',
                                    ['volatility', 'memory', 'power-off', 'evidence']),
    'MC-IT10-VOLATILITY-ORDER': _m('IT-10.4', 'Collecting disk or archive evidence before memory and temporary files',
                                   'RFC 3227 order: memory before temporary files, then disk, then archival media.', ['rfc 3227', 'order of volatility', 'disk', 'memory']),
    'MC-IT11-SAFEMODE-MEANING': _m('IT-11.4', 'Reading a fault that disappears in Safe Mode as hardware, data or core-OS damage',
                                   'Safe Mode loads a minimal set of drivers and services; if the fault goes, something it skips is involved.',
                                   ['safe mode', 'driver', 'service', 'startup']),
    'MC-IT11-RESET-KEEPS-DATA': _m('IT-11.4', 'Believing Reset or a reinstall keeps the app’s data',
                                   'Repair fixes the app and keeps its data; Reset and reinstalling remove local app data.', ['repair', 'reset', 'app data', 'advanced options']),
    'MC-IT12-KB-TECH-TITLE': _m('IT-12.4', 'Titling a KB article by internal number, shorthand or the fix instead of the symptom in the user’s words',
                                'Write the title in the user’s words so the next technician finds it from the report.', ['kb', 'title', 'symptom', 'user’s words']),
    'MC-IT12-ASSET-STATIC': _m('IT-12.4', 'Thinking an asset record only changes at disposal, or that the tag or serial changes on a move',
                               'Status and location change through the device’s life; the tag and serial stay the same.', ['asset record', 'status', 'location', 'serial']),
    'MC-IT13-BIG-RESET-FIRST': _m('IT-13.4', 'Starting with a stack reset, full network reset or driver reinstall instead of the lowest rung',
                                  'Climb the ladder: renew the lease first, then restart the adapter, and only then reset more.',
                                  ['release', 'renew', 'network reset', 'ladder']),
    'MC-IT13-CMDLET-MIXUP': _m('IT-13.4', 'Choosing a cmdlet that restarts an adapter or shows/clears the DNS cache to read IP configuration',
                               'Get-NetIPConfiguration summarises addresses, gateway and DNS servers per adapter.',
                               ['get-netipconfiguration', 'powershell', 'wmic', 'dns']),
}

_T = [
    ('Q7.10', 'Impact and priority', 'MC-IT7-PACKAGE-PARTS'), ('Q7.10', 'Scope', 'MC-IT7-PACKAGE-PARTS'), ('Q7.10', 'The request', 'MC-IT7-PACKAGE-PARTS'),
    ('Q7.11', 'Nothing until the network team has fixed it and closed the ticket', 'MC-IT7-SILENT-ESCALATION'),
    ('Q7.11', 'Your best guess at the root cause, so that they feel reassured for now', 'MC-IT7-SILENT-ESCALATION'),
    ('Q8.10', 'The domain GPO, because it is higher in the tree', 'MC-IT8-GPO-HIGHER-WINS'),
    ('Q8.10', 'Whichever GPO was created most recently', 'MC-IT8-GPO-HIGHER-WINS'),
    ('Q8.10', 'The local policy, because it lives on the PC', 'MC-IT8-GPO-HIGHER-WINS'),
    ('Q8.11', 'gpupdate /force', 'MC-IT8-WRONG-GP-TOOL'), ('Q8.11', 'dsregcmd /status', 'MC-IT8-WRONG-GP-TOOL'), ('Q8.11', 'w32tm /query /status', 'MC-IT8-WRONG-GP-TOOL'),
    ('Q9.10', 'The drive is failing and the disk has switched itself to read-only', 'MC-IT9-NTFS-READONLY-AS-FAULT'),
    ('Q9.10', 'NTFS drives must be repaired with First Aid in Disk Utility first', 'MC-IT9-NTFS-READONLY-AS-FAULT'),
    ('Q9.11', 'Both files, listed side by side under their original names and sizes', 'MC-IT9-CASE-BLIND'),
    ('Q9.11', 'An error message, because SMB cannot share folders that live on Linux', 'MC-IT9-CASE-BLIND'),
    ('Q10.10', 'Shutting down would start an automatic reimage of the whole system', 'MC-IT10-SHUTDOWN-HARMLESS'),
    ('Q10.10', 'Windows Update would install pending updates and restart the PC twice', 'MC-IT10-SHUTDOWN-HARMLESS'),
    ('Q10.11', 'Disk, memory, temporary files, archival media', 'MC-IT10-VOLATILITY-ORDER'),
    ('Q10.11', 'Archival media, disk, temporary files, memory', 'MC-IT10-VOLATILITY-ORDER'),
    ('Q10.11', 'Temporary files, disk, memory, archival media', 'MC-IT10-VOLATILITY-ORDER'),
    ('Q11.10', 'Failing hardware, such as the RAM or the system disk, in the PC', 'MC-IT11-SAFEMODE-MEANING'),
    ('Q11.10', 'Damage to the documents and files saved in the user’s profile', 'MC-IT11-SAFEMODE-MEANING'),
    ('Q11.10', 'A fault in the core Windows kernel, which loads in every boot mode', 'MC-IT11-SAFEMODE-MEANING'),
    ('Q11.11', 'Reset, in the app’s Advanced options', 'MC-IT11-RESET-KEEPS-DATA'),
    ('Q11.11', 'Uninstalling and reinstalling the app', 'MC-IT11-RESET-KEEPS-DATA'),
    ('Q12.10', 'As the internal problem-record number, with nothing else', 'MC-IT12-KB-TECH-TITLE'),
    ('Q12.10', 'In the technician’s own shorthand', 'MC-IT12-KB-TECH-TITLE'), ('Q12.10', 'As the name of the fix', 'MC-IT12-KB-TECH-TITLE'),
    ('Q12.11', 'A new asset tag is issued, because the device has a new home', 'MC-IT12-ASSET-STATIC'),
    ('Q12.11', 'Nothing changes until the laptop is finally disposed of', 'MC-IT12-ASSET-STATIC'),
    ('Q12.11', 'Its serial number is updated to match the new location', 'MC-IT12-ASSET-STATIC'),
    ('Q13.10', 'netsh winsock reset, then restart', 'MC-IT13-BIG-RESET-FIRST'),
    ('Q13.10', 'Settings → Network & internet → Network reset', 'MC-IT13-BIG-RESET-FIRST'),
    ('Q13.10', 'Reinstall the network adapter driver', 'MC-IT13-BIG-RESET-FIRST'),
    ('Q13.11', 'Restart-NetAdapter', 'MC-IT13-CMDLET-MIXUP'), ('Q13.11', 'Clear-DnsClientCache', 'MC-IT13-CMDLET-MIXUP'),
    ('Q13.11', 'Get-DnsClientCache', 'MC-IT13-CMDLET-MIXUP'),
]
TAGS = {(b, d): mc for b, d, mc in _T}
