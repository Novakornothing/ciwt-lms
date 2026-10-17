"""ITSUP Chapter 10 — Endpoint Security (pass 9 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 10
SOURCES_USED = ['nist-80063b4', 'cisa-mfa', 'ms-bitlocker', 'ms-defender', 'nist-80061r3', 'rfc3227', 'nist-80088r2']

LESSONS = {
    (10, 1): {
        'sources': ['nist-80063b4', 'cisa-mfa'],
        'objectives': [
            'Compare authentication factors and rank MFA methods by phishing resistance (passkeys and security keys above app push, codes and SMS)',
            'Apply least privilege: separate admin accounts, standard daily accounts and just-enough access',
            'Identify physical controls (screen lock, cable locks, badge access, privacy screens, clean desk) that a support technician enforces or reports',
            'Respond to an MFA-fatigue report by treating unexpected prompts as a possible compromise',
        ],
        'html': sme_note() + '''
<h3>Something you know, have or are</h3>
<p><strong>Authentication</strong> proves who someone is; <strong>authorisation</strong> decides what they may do. Factors come
in three kinds: something you know (a password or PIN), something you have (a phone, a security key, a smart card) and something
you are (a fingerprint or face, used to unlock a device-bound credential). <strong>Multi-factor authentication (MFA)</strong>
combines at least two different kinds. Two passwords are still one factor.</p>
<p>Not all MFA resists phishing equally. A fake sign-in page can relay a typed code or trick a user into approving a push
prompt. <strong>Phishing-resistant</strong> methods bind the sign-in to the real website so a look-alike site gets nothing
useful: FIDO2/WebAuthn security keys, passkeys and smart-card (PKI) credentials. CISA recommends phishing-resistant MFA, and
NIST SP 800-63B-4 sets out authenticator requirements and password rules (length over complexity, screening against breached
passwords, no forced periodic changes without cause — see the reference section in this chapter).</p>
''' + table(['Method', 'Factor kinds', 'Phishing resistance', 'Support notes'], [
            ['Password only', 'Know', 'None', 'Still common for low-risk systems; never enough for admin or remote access'],
            ['SMS or voice code', 'Know + have', 'Low — codes can be relayed; SIM-swap risk', 'Better than nothing; plan to replace'],
            ['Authenticator app code (TOTP)', 'Know + have', 'Low–moderate — codes can be relayed', 'Works offline; re-enrol when a phone is replaced'],
            ['App push with number matching', 'Know + have', 'Moderate — resists blind approval, not a real-time relay', 'Number matching blocks most “prompt bombing”'],
            ['Passkey / FIDO2 security key', 'Have + are or know (device unlock)', 'High — bound to the real site', 'Register at least two; keep a recovery process'],
            ['Smart card / PIV', 'Have + know', 'High', 'Common in government and some campuses'],
        ]) + '''
<h3>Least privilege in daily support</h3>
<ul>
<li>Users work in standard accounts; elevation uses a separate admin account or a just-in-time approval process.</li>
<li>Technicians use their own named admin accounts, never a shared one, so every change is traceable.</li>
<li>Access is granted to groups for a role, and removed when the role changes (Chapter 9’s entitlement problems are the
other side of this).</li>
</ul>
<h3>Physical controls are part of security</h3>
<p>Screen lock after inactivity (and Windows key + L when leaving the desk), cable locks for shared spaces, badge-controlled
rooms for network and server equipment, privacy screens where the public can see displays, and a clean-desk habit for
printed records. A technician who props open a server-room door or leaves a signed-in console has bypassed every password
policy in the building.</p>
''' + scenario('“my phone keeps asking me to approve sign-ins”', '''
<p>At 23:40 a lecturer receives a dozen MFA push prompts she did not start, and finally taps Approve to make them stop. In the
morning she mentions it at the help desk “in case it matters”. It does: repeated unexpected prompts mean someone has her
password. The technician treats it as a security incident — reports to the security team at once, who revoke her sessions,
reset the password from a clean device, review her MFA methods and mailbox rules — and the lecturer is enrolled in number
matching and then a passkey.</p>''') + cfu(
            ('Why is a password plus a security question not MFA?',
             'Both are “something you know” — one factor kind used twice.'),
            ('Which MFA methods are phishing-resistant?',
             'FIDO2/WebAuthn security keys and passkeys, and smart-card (PKI) credentials.'),
            ('A user approved a prompt they did not start. What does that mean?',
             'Their password is probably known to an attacker; treat it as an incident and report it immediately.')),
    },
    (10, 2): {
        'sources': ['ms-defender', 'nist-80061r3'],
        'objectives': [
            'Recognise common indicators of malware (unexpected pop-ups, disabled protection, new startup items, unusual traffic, encrypted files)',
            'Contain a suspected infection within the support role: isolate from the network, preserve the state, report to security',
            'Run Microsoft Defender full and offline scans and record the results in Protection history',
            'Explain why reimaging and credential resets follow, not precede, the security team’s decision',
        ],
        'html': sme_note() + '''
<h3>Signs that something is wrong</h3>
<ul>
<li>Protection turned off, or settings greyed out with “managed by your organisation” on a device that is not managed.</li>
<li>New browser extensions, toolbars or a changed home page; pop-ups demanding payment or a phone call to “support”.</li>
<li>Unknown programs in startup (Task Manager → Startup apps) or unknown scheduled tasks.</li>
<li>Files renamed with a new extension and a ransom note — <strong>ransomware</strong>.</li>
<li>Unusual network activity, accounts locked out repeatedly, or colleagues receiving email the user did not send.</li>
</ul>
<h3>Your role: contain, preserve, report</h3>
<p>Incident response is a team activity. NIST SP 800-61 Revision 3 organises it under the Cybersecurity Framework functions
Detect, Respond and Recover, supported by preparation. For a support technician that means following the organisation’s
playbook, which usually looks like this:</p>
''' + figure('f10-2', 'Support-role response to suspected malware', ['Recognise\nindicators', 'Isolate from\nnetwork', 'Preserve:\ndo not wipe\nor delete', 'Report to\nsecurity', 'Remediate as\ndirected'],
             'Five boxes in order: Recognise indicators; Isolate the device from the network (unplug the cable, turn off Wi-Fi, or use the '
             'security tool’s isolate function); Preserve the state — do not wipe, reimage or delete files, and avoid shutting down unless the '
             'playbook says so; Report to the security team with times and what you saw; then Remediate only as the security team directs — '
             'scans, reimage, password resets and restore from backup.', 'Contain and preserve first; remediation decisions belong to the security team.', cols=5) + '''
<p><strong>Isolate</strong> means disconnecting the device from the network so the malware cannot spread or send data — unplug
the cable, turn off Wi-Fi, or use the endpoint tool’s “isolate device” action if your organisation provides one.
<strong>Preserve</strong> means not wiping, reimaging or deleting files before security has decided what evidence it needs; the
playbook says whether to leave the device on (memory holds evidence) or shut it down (ransomware still encrypting).</p>
<h3>Scanning with Microsoft Defender</h3>
<p>When security asks you to scan: Windows Security → Virus &amp; threat protection → Scan options. A <strong>full scan</strong>
checks all files and running programs. A <strong>Microsoft Defender Offline scan</strong> restarts the PC into the recovery
environment and scans before Windows loads, which catches malware that hides from a running system; save work first, because it
restarts immediately. Results appear in Protection history. If the offline scan never runs, the recovery environment may be
disabled (<code>reagentc /info</code> shows its state).</p>
''' + worked('the ticket for a suspected infection', '''
<p>“10:14 user reported pop-up claiming ‘your PC is infected, call this number’; Windows Security shows real-time protection off and
cannot be turned on. 10:16 unplugged network cable (Wi-Fi off). Device left powered on, user signed out of nothing, no files deleted.
10:18 reported to Security (phone + SEC queue), incident SEC-2210. User did not call the number and did not enter any password.
Waiting for Security’s instructions; user given loan laptop.”</p>''') + scenario('the helpful reimage', '''
<p>A technician found ransomware on a shared lab PC, reimaged it within the hour and closed the ticket. Two days later the same
ransomware appeared on six other PCs. Because the first PC had been wiped, the security team had no way to find how it got in
— a reused password on a remote-access tool. Containment and a report would have taken ten minutes and probably prevented the
spread.</p>''') + cfu(
            ('What are the three support-role actions before any remediation?',
             'Isolate from the network, preserve the state (no wipe or deletion), report to security.'),
            ('When is a Defender Offline scan useful?',
             'When malware may hide from the running Windows; the offline scan runs before Windows loads.'),
            ('Why not reimage straight away?',
             'It destroys the evidence security needs to find the entry point and other affected devices.')),
    },
    (10, 3): {
        'sources': ['ms-bitlocker', 'nist-80088r2'],
        'objectives': [
            'Verify device encryption and locate where the BitLocker recovery key is stored',
            'Apply patching and removable-media controls and explain the risk each one reduces',
            'Select a sanitization approach (clear, purge, destroy; cryptographic erase) for media leaving the organisation and record it',
            'Apply support hygiene in a remote session: verify identity, use a named account, record no secrets and close the session',
        ],
        'html': sme_note() + '''
<h3>Encryption at rest</h3>
<p>If a laptop is lost, encryption is what keeps the data private. On Windows that is <strong>BitLocker</strong> or its
consumer form, <strong>device encryption</strong>. On many current Windows 11 devices, device encryption turns on automatically
when the user signs in with a Microsoft account or a work or school account, and the recovery key is backed up to that account
first. Check it in Settings → Privacy &amp; security → Device encryption, or with <code>manage-bde -status</code>. Before any
firmware update, TPM change or motherboard repair, confirm where the recovery key is — a personal device’s key can be found
by the account owner at <code>aka.ms/myrecoverykey</code>; an organisation’s keys are usually in its directory or device
management. Never write a recovery key into a ticket.</p>
<h3>Patching and removable media</h3>
<ul>
<li><strong>Patching.</strong> Microsoft releases monthly security updates on the second Tuesday of the month; browsers and many
apps update on their own schedules. Most organisations deploy in rings (a pilot group first, then everyone) so a bad update
reaches a few devices, not all. Your job is to report devices that are not updating, not to pause updates for convenience.</li>
<li><strong>Removable media.</strong> USB drives carry malware in and data out. Organisations may block them, allow only
encrypted drives (BitLocker To Go) or allow read-only. Unknown USB drives found in car parks or lecture halls go to security,
not into a PC “to find the owner”.</li>
</ul>
<h3>When media leaves: sanitization</h3>
<p>NIST SP 800-88 Revision 2 (September 2025) treats sanitization as a programme: decide by the sensitivity of the data and
where the media is going, use a method the media supports, verify it, and record it. The method families are:</p>
''' + table(['Method', 'What it does', 'Typical use'], [
            ['Clear', 'Overwrites user-addressable storage with standard commands; protects against simple recovery tools', 'Reuse inside the organisation'],
            ['Purge', 'Uses the device’s own sanitize or secure-erase commands (or degaussing for magnetic media) so laboratory recovery is infeasible', 'Media leaving the organisation for resale or recycling'],
            ['Destroy', 'Shredding, disintegration, incineration', 'Highly sensitive data or media that cannot be purged'],
            ['Cryptographic erase', 'Destroys the encryption key so encrypted data becomes unreadable', 'Self-encrypting drives and encrypted volumes, as part of purge'],
        ]) + '''
<p>For SSDs, overwriting files or formatting is not reliable, because the drive maps writes to different cells; use the
manufacturer’s sanitize function or cryptographic erase, as the organisation’s procedure specifies. Record the asset tag,
serial number, method, date, operator and verification for every device — that record is the evidence the data is gone.</p>
''' + figure('f10-3', 'Choosing a sanitization method', ['Data\nsensitivity', 'Leaving the\norganisation?', 'No: clear\n(reuse)', 'Yes: purge\n(or crypto erase)', 'Record +\nverify'],
             'Five boxes. Start with the sensitivity of the data. Then ask whether the media is leaving the organisation. If it stays for '
             'internal reuse, clear is often enough. If it leaves, purge it with the device’s sanitize command or a cryptographic erase, or '
             'destroy it when it is highly sensitive or cannot be purged. Every path ends with recording and verifying the sanitization.',
             'The destination and the data decide the method; every device gets a sanitization record.', cols=5) + worked('support hygiene during a remote session', '''
<ol>
<li>Verify the caller’s identity with the approved method before connecting.</li>
<li>Connect with your own named account; ask before taking control and tell the user what you are doing.</li>
<li>Do not view or copy unrelated files; close personal windows before screen-sharing.</li>
<li>Elevate only when needed, with your admin account, never by asking for the user’s password.</li>
<li>End the session, confirm the remote tool has disconnected, and write the ticket — without passwords, recovery keys or
personal data.</li>
</ol>''') + cfu(
            ('Where can a user find the BitLocker recovery key for a personal Windows 11 device with a Microsoft account?',
             'At aka.ms/myrecoverykey, signed in with that Microsoft account.'),
            ('Why is formatting an SSD not enough before it is sold?',
             'Writes are remapped inside the drive, so data can survive; use sanitize/secure erase or cryptographic erase (purge).'),
            ('What goes in a sanitization record?',
             'Asset tag, serial number, method, date, operator and verification.')),
    },
    (10, 4): {
        'sources': ['rfc3227', 'nist-80061r3'],
        'objectives': [
            'Triage a phishing report: submit the message with its headers and determine whether the user clicked, opened or entered credentials',
            'Respond to entered credentials: reset from a clean device, revoke sessions, review MFA methods and mailbox forwarding rules — with or through the security team',
            'Preserve evidence in order of volatility and maintain a chain-of-custody record when asked',
        ],
        'html': sme_note('Phishing follow-up, order of volatility and chain of custody added in pass 9.') + '''
<h3>A phishing report is a gift</h3>
<p>Thank the user — reporting is the behaviour you want. Then find out quickly what happened, because the next steps depend on
it: did they only receive it, click a link, open an attachment, or type a password or MFA code?</p>
''' + table(['What the user did', 'Risk', 'Response (with or through security)'], [
            ['Received it, did nothing', 'Low for this user; others may have it', 'Report with the built-in “Report” button or as an attachment (keeps the headers); security removes it from other mailboxes'],
            ['Clicked a link, entered nothing', 'Possible drive-by or tracking', 'Report; scan the device; note the time and URL from the message (do not visit it)'],
            ['Opened an attachment', 'Malware likely', 'Isolate the device and follow lesson 10.2'],
            ['Entered a password or approved MFA', 'Account compromise', 'Reset the password from a clean device, revoke active sessions, review MFA methods, check mailbox rules for forwarding or deletion, watch for further sign-ins'],
        ]) + '''
<p>Attackers who get into a mailbox often add a rule that forwards mail outside or deletes replies so the user does not notice.
That is why mailbox rules and MFA methods are checked even after the password is changed.</p>
<h3>Evidence: order of volatility and chain of custody</h3>
<p>If security asks you to help preserve evidence, collect the most volatile first, because it disappears soonest. RFC 3227
gives the order: CPU registers and cache; routing and ARP tables, the process table and memory; temporary file systems; disk;
remote logging and monitoring data; physical configuration and network topology; archival media. In practice this is why
“don’t switch it off” is often the instruction — memory and network connections vanish at power-off.</p>
''' + figure('f10-4', 'Order of volatility (most volatile first)', ['Registers,\ncache', 'Memory, ARP,\nprocess table', 'Temporary\nfiles', 'Disk', 'Remote logs,\nmonitoring', 'Archive\nmedia'],
             'Six boxes from most to least volatile, following RFC 3227: CPU registers and cache; memory, routing and ARP tables and the '
             'process table; temporary file systems; disk; remote logging and monitoring data; and archival media. Evidence on the left '
             'disappears first, so it is collected first.', 'Collect evidence that vanishes soonest first; power-off destroys the left half of the chain.', cols=3) + '''
<p><strong>Chain of custody</strong> is the record of who had an item of evidence, when, and what they did with it, from collection
to the end of the case. Label the device (asset tag, serial), record the time and condition, sign it over in person, and store it
securely. A gap in the chain can make evidence unusable in a disciplinary or legal process.</p>
''' + worked('the capstone ticket', '''
<p>“09:02 user reported email ‘Payroll update required’ (from: payroll-update@ an outside domain). User clicked the link at 08:51 and
entered college password; did not approve any MFA prompt. 09:04 reported to Security (SEC-2231) using Report button. 09:06 with
Security on the phone: password reset from the service-desk PC, all sessions revoked by Security. Mailbox rules: one new rule ‘fwd’
forwarding to an outside address created 08:55 — removed by Security, screenshot attached to SEC-2231. User re-enrolled MFA with
number matching. User advised; Security monitoring sign-ins for 7 days.”</p>''') + cfu(
            ('Why report a phishing email as an attachment or with the Report button rather than forwarding it?',
             'Both keep the original headers, which security needs to trace and block the sender.'),
            ('A user entered their password on a phishing page. Name four follow-up actions.',
             'Reset from a clean device, revoke sessions, review MFA methods, check mailbox rules (and monitor sign-ins).'),
            ('Which is more volatile, the ARP table or the disk?',
             'The ARP table — it changes in seconds and is lost at power-off.')),
    },
}

GLOSSARY = [
    ('Phishing-resistant MFA', 'Authentication bound to the genuine site or service (FIDO2 security keys, passkeys, smart cards), so a look-alike site cannot reuse it.'),
    ('Passkey', 'A FIDO2/WebAuthn credential stored on a device or security key and unlocked with a PIN or biometric; it cannot be typed into a fake site.'),
    ('MFA fatigue (prompt bombing)', 'Repeated push prompts sent by an attacker who knows the password, hoping the user approves one.'),
    ('Ransomware', 'Malware that encrypts or steals data and demands payment.'),
    ('Isolation (containment)', 'Disconnecting a suspect device from the network so malware cannot spread or exfiltrate data.'),
    ('Microsoft Defender Offline scan', 'A Defender scan that runs from the recovery environment before Windows loads.'),
    ('Media sanitization', 'Making data on media infeasible to recover: clear, purge or destroy, with a record (NIST SP 800-88 Rev. 2).'),
    ('Cryptographic erase', 'Sanitizing encrypted media by destroying its encryption keys.'),
    ('Order of volatility', 'Collecting evidence from the most short-lived (registers, memory) to the most durable (archives), per RFC 3227.'),
    ('Chain of custody', 'The documented record of who handled evidence, when and how, from collection to disposal.'),
]

PLAN = {
    'warmup': 'Show five sign-in methods (password, SMS, app code, number-matched push, passkey). Students rank them by phishing resistance and justify the top choice.',
    'guided': 'Role-play the malware playbook: one student is the user with a scareware pop-up, one the technician (isolate, preserve, report), one the security analyst. Then decode the sanitization table for three devices leaving the college.',
    'worked_example': 'Lesson 10.2 suspected-infection ticket; 10.3 remote-session hygiene; 10.4 phishing capstone ticket with mailbox-rule finding.',
    'cfu': ['Which MFA methods are phishing-resistant, and why?',
            'Name the three support-role actions before remediation of suspected malware.',
            'Why is formatting not enough for an SSD that will be sold?',
            'Which is collected first, memory or disk, and why?'],
    'exit_ticket': 'A user typed their password into a fake payroll page 10 minutes ago. List, in order, what you and the security team do.',
    'misconceptions_add': ['“Reimaging fast is the safest response.” It destroys evidence; contain, preserve and report first.',
                           '“Any MFA stops phishing.” Codes and push approvals can be relayed or fatigued; passkeys and security keys resist it.'],
    'classroom_lab': 'CL-10',
    'materials_add': 'Classroom lab CL-10 (endpoint security posture check) and the incident tabletop cards.',
}

ITEMS = [
    item('IT-10.1', 1, 'Which sign-in method resists phishing best?',
         'A passkey or FIDO2 security key', ['A six-digit code sent by text message', 'A code from an authenticator app', 'A password plus a security question'],
         'Passkeys and FIDO2 keys are bound to the genuine site; codes can be relayed and two “know” factors are one factor kind.'),
    item('IT-10.1', 2, 'A user received many MFA push prompts overnight and approved one. What should you assume?',
         'Their password is known to an attacker', ['The authenticator app needs an update', 'The phone’s clock has drifted overnight', 'The prompts were from a routine sync job'],
         'Unexpected prompts mean someone is signing in with the password; approving one may have let them in.'),
    item('IT-10.1', 3, 'Why should technicians use their own named admin accounts?',
         'So every privileged change is traceable to a person', ['So they never need to use MFA when signing in to servers', 'So their accounts never expire or lock out', 'So users can borrow them when they need rights'],
         'Named accounts give accountability; shared admin accounts hide who made a change.'),
    item('IT-10.2', 1, 'You suspect malware on a PC. What do you do first, within the support role?',
         'Disconnect it from the network and report it', ['Reimage it so the user can work again today', 'Delete the suspicious files you can find', 'Restart it to see whether the problem clears up'],
         'Contain and preserve, then report; wiping, deleting or restarting can destroy evidence.'),
    item('IT-10.2', 2, 'When is a Microsoft Defender Offline scan most useful?',
         'When malware may be hiding from the running Windows', ['When the PC has no internet connection at all', 'When the user wants a faster scan than a quick one', 'When the antivirus licence has recently expired'],
         'The offline scan runs from the recovery environment before Windows loads, catching malware that hides while Windows runs.'),
    item('IT-10.2', 3, 'Why should a technician not reimage a ransomware-infected PC before security reviews it?',
         'The evidence of how it got in would be lost', ['Reimaging spreads the ransomware to backups', 'The licence key is erased by reimaging', 'Reimaging takes longer than paying the ransom'],
         'Security needs the device’s state to find the entry point and other affected systems.'),
    item('IT-10.3', 1, 'Before replacing a laptop’s motherboard, what must you confirm about BitLocker?',
         'Where the recovery key is stored', ['That BitLocker is turned off for good', 'That the TPM is cleared beforehand', 'That the user writes the key in the ticket'],
         'A board or TPM change triggers recovery; you need the key, which must never be written into a ticket.'),
    item('IT-10.3', 2, 'An SSD with student records will be sold. Which approach fits NIST SP 800-88 Rev. 2?',
         'Purge it with sanitize or crypto erase, then record it', ['Quick-format it twice and then reinstall Windows on it', 'Delete the files and empty the Recycle Bin', 'Copy new files over it until the drive is full'],
         'Media leaving the organisation needs purge (device sanitize or cryptographic erase) and a sanitization record.'),
    item('IT-10.3', 3, 'A USB stick is found in a lecture-hall car park. What is the right action?',
         'Hand it to security without plugging it in', ['Plug it into a lab PC to find out who the owner is', 'Format it and add it to the loan pool', 'Open it in a VM to look for a name file'],
         'Unknown USB media is a classic malware delivery method; security handles it.'),
    item('IT-10.4', 1, 'A user typed their password into a phishing page. Which step is part of the follow-up?',
         'Check the mailbox for new forwarding rules', ['Ask the user to change their desk phone PIN', 'Reinstall the user’s web browser at once', 'Clear the user’s browser history and cache'],
         'Attackers often add forwarding or deletion rules; these are checked along with sessions and MFA methods.'),
    item('IT-10.4', 2, 'Under RFC 3227, which evidence should be collected first?',
         'Memory and the process table', ['The contents of the system disk', 'Archived backup tapes', 'Remote syslog records'],
         'Collect from most to least volatile; memory and process data disappear at power-off.'),
    item('IT-10.4', 3, 'What does a chain-of-custody record show?',
         'Who held the evidence, when, and what they did', ['The order in which malware spread across devices', 'The list of passwords reset after an incident', 'The vendor and model of each affected device'],
         'Chain of custody documents every handover so evidence remains trustworthy.'),
]

LABS = {
    'CL-10': {
        'id': 'CL-10', 'title': 'Endpoint security posture check and incident tabletop', 'chapters': [('ITSUP', 10), ('CLIENT', 3)],
        'review': 'Pending SME review',
        'objective': 'Verify the security posture of a Windows 11 lab VM and run a malware and phishing tabletop within the support role.',
        'prerequisites': ['Lessons 10.1–10.4'],
        'equipment': 'Windows 11 lab VM (encryption may be simulated where the VM lacks a virtual TPM), Windows Security app, printed tabletop cards.',
        'low_cost': 'Posture check from instructor screenshots; tabletop on paper only.',
        'steps': [
            'Record protection state with Get-MpComputerStatus (real-time protection, signature date) and Windows Security.',
            'Record encryption status with manage-bde -status (elevated) or Settings → Privacy & security → Device encryption; note where the recovery key would be stored — do not display it.',
            'Record account type (whoami /groups): is the daily account a standard user?',
            'Check Windows Update history for the latest monthly security update.',
            'Tabletop 1 (scareware pop-up): write the isolate–preserve–report ticket in the order of lesson 10.2.',
            'Tabletop 2 (password entered on phishing page): list the follow-up actions and who performs each.',
            'Tabletop 3 (laptop leaving the college): choose a sanitization method and fill in a sanitization record.',
        ],
        'expected': 'Posture recorded with evidence; tabletop tickets follow the playbook order; no secret (password, recovery key) appears in any note.',
        'troubleshooting': ['If manage-bde reports “access denied”, the console is not elevated.',
                            'If real-time protection is off on the VM, record it as a finding — do not change it unless the instructor asks.'],
        'reflection': ['Which posture finding would you raise first, and why?',
                       'In tabletop 1, what evidence would a reimage have destroyed?',
                       'Why is the sanitization record as important as the sanitization?'],
        'rubric': 'ticket', 'minutes': 60, 'objectives': ['IT-10.1', 'IT-10.2', 'IT-10.3', 'IT-10.4'],
    },
}
