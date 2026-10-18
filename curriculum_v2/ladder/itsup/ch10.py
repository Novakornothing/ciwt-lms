"""Explanation ladder — ITSUP chapter 10 (Endpoint Security). Pending SME review.

Author B (labs branch, pass 19). Every concept section of lessons 10.1-10.4 is laddered, restated with same_as, or
skipped with a reason. CLIENT chapter 3 holds the same lessons and reuses this ladder (curriculum_v2/ladder/client/ch03.py).
No rung asks a student to handle live malware: try-its use the course's graded labs and simulators.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 10

L101 = 'Course lesson 10.1 “Physical and Logical Controls” (the original section), re-explained'
L102 = 'Course lesson 10.2 “Malware Response” (the original section), re-explained'
L103 = 'Course lesson 10.3 “Support Hygiene” (the original section), re-explained'
L104 = 'Course lesson 10.4 “Capstone — Phishing Follow-Up” (the original section), re-explained'
NIST63 = 'NIST SP 800-63B-4, Digital Identity Guidelines: Authentication and Authenticator Management (2025)'
CISA_MFA = 'CISA — Implementing phishing-resistant MFA (fact sheet)'
NIST53 = 'NIST SP 800-53 Rev. 5 — Physical and Environmental Protection (PE) and Access Control (AC) families; NIST SP 800-207, Zero Trust Architecture'
NIST61 = 'NIST SP 800-61 Rev. 3, Incident Response Recommendations and Considerations for Cybersecurity Risk Management (2025)'
MS_DEF = 'Microsoft Learn — Microsoft Defender Offline scan in Windows'
NIST83 = 'NIST SP 800-83 Rev. 1, Guide to Malware Incident Prevention and Handling for Desktops and Laptops'
CISA_SE = 'CISA — “Avoiding Social Engineering and Phishing Attacks” (security tip)'
MS_BL = 'Microsoft Support — “Device encryption in Windows” and “Find your BitLocker recovery key”'
NIST88 = 'NIST SP 800-88 Rev. 2, Guidelines for Media Sanitization'
MS_HARD = ('Microsoft Learn — Account lockout threshold (security policy setting); net user command reference '
           '(/active, /expires, /times); Microsoft Support — turn AutoPlay on or off')
RFC3227 = 'IETF RFC 3227, Guidelines for Evidence Collection and Archiving'

MISCONCEPTIONS = {
    'MC-L-IT10-REDIRECT-OUTSIDE-IN': {
        'obj': 'IT-10.2', 'label': 'Starting a browser-redirect investigation at the router or the website instead of on the PC',
        'fix': 'Test from the inside out: a clean browser profile, then proxy and hosts file, then a second device on the same network.',
        'terms': ['redirect', 'extension', 'proxy', 'hosts'], 'source': L102, 'review': 'Pending SME review'},
    'MC-L-IT10-PRIVATE-HIDES': {
        'obj': 'IT-10.2', 'label': 'Thinking private browsing hides activity from websites, the employer or the internet provider',
        'fix': 'InPrivate / Incognito only stops the browser keeping local history and cookies after the window closes.',
        'terms': ['private browsing', 'incognito', 'inprivate'], 'source': L102, 'review': 'Pending SME review'},
    'MC-L-IT10-ROOTKIT-SCAN': {
        'obj': 'IT-10.2', 'label': 'Thinking a normal scan reliably removes a rootkit',
        'fix': 'A rootkit hides with kernel or firmware access; the reliable fix is reinstalling the OS and restoring clean data.',
        'terms': ['rootkit', 'reinstall', 'kernel'], 'source': L102 + '; ' + NIST83, 'review': 'Pending SME review'},
    'MC-L-IT10-SSD-FORMAT': {
        'obj': 'IT-10.3', 'label': 'Thinking overwriting or formatting an SSD sanitizes it',
        'fix': 'SSDs remap writes to other cells; use the drive’s sanitize command or cryptographic erase (purge).',
        'terms': ['ssd', 'purge', 'cryptographic erase', 'sanitize'], 'source': L103 + '; ' + NIST88, 'review': 'Pending SME review'},
    'MC-L-IT10-FORWARD-PHISH': {
        'obj': 'IT-10.4', 'label': 'Forwarding a phishing email to security instead of using Report or sending it as an attachment',
        'fix': 'Report or attach the message so the original headers survive; security needs them to trace and block the sender.',
        'terms': ['report', 'headers', 'phishing'], 'source': L104, 'review': 'Pending SME review'},
    'MC-L-IT10-CALL-NUMBER-GIVEN': {
        'obj': 'IT-10.4', 'label': 'Verifying an unusual request with the contact details in the message itself',
        'fix': 'Verify out of band: use a number or channel you already hold, such as the directory or finance system.',
        'terms': ['out of band', 'bec', 'vishing', 'verify'], 'source': L104 + '; ' + CISA_SE, 'review': 'Pending SME review'},
}

# reused course misconceptions (curriculum_v2/misconceptions*.py)
SAMEF, SMS, OTP, FATIGUE = 'MC-C-IT10-MFA-SAME-FACTOR', 'MC-C-IT10-SMS-STRONG', 'MC-R5-IT10-OTP-PHISH', 'MC-R5-IT10-MFA-FATIGUE'
SHARED, BROADP, STANDING, PWREC = 'MC-IT10-SHARED-ADMIN', 'MC-IT10-BROAD-PRIVILEGE', 'MC-C-IT10-STANDING-ADMIN', 'MC-IT10-PASSWORD-RECORDED'
CPURP, TRUSTLAN = 'MC-C-IT10-CONTROL-PURPOSE', 'MC-C-IT10-TRUST-LAN'
SOLO, DISDEF, MORDER, OFFSCAN = 'MC-IT10-SOLO-RESPONDER', 'MC-IT10-DISABLE-DEFENDER', 'MC-C-IT10-MALWARE-ORDER', 'MC-R5-IT10-OFFLINE-SCAN'
SHUT, RANSOM, CLOCK, HASH = 'MC-IT10-SHUTDOWN-HARMLESS', 'MC-R6-IT10-RANSOM-ISOLATE', 'MC-R6-IT10-CLOCK-CERT', 'MC-R6-IT10-HASH-PURPOSE'
SYMHW, BROWSET, UNDER = 'MC-C-IT10-SYMPTOM-AS-HW', 'MC-C-IT10-BROWSER-SETTING', 'MC-R3-IT10-COMPROMISE-UNDERPLAYED'
QFMT, WIPEOK, RKEY, FUSB = 'MC-IT10-QUICK-FORMAT', 'MC-C-IT10-WIPE-ENOUGH', 'MC-R5-IT10-RECOVERY-KEY', 'MC-R5-IT10-FOUND-USB'
DISPROT, WRONGC = 'MC-IT10-DISABLE-PROTECTION', 'MC-R3-IT10-WRONG-CONTROL'
VOLAT, CUSTODY, EVLATER, COMPREQ = 'MC-IT10-VOLATILITY-ORDER', 'MC-R5-IT10-CUSTODY', 'MC-R3-IT10-EVIDENCE-LATER', 'MC-IT10-COMPROMISE-AS-REQUEST'
REDIR, PRIV, ROOTK = 'MC-L-IT10-REDIRECT-OUTSIDE-IN', 'MC-L-IT10-PRIVATE-HIDES', 'MC-L-IT10-ROOTKIT-SCAN'
SSD, FWD, GIVEN = 'MC-L-IT10-SSD-FORMAT', 'MC-L-IT10-FORWARD-PHISH', 'MC-L-IT10-CALL-NUMBER-GIVEN'

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
_MFA = svg(640, 190, 'Sign-in methods from weakest to strongest against phishing: password only; SMS code; authenticator app code; push with number matching; passkey or FIDO2 key and smart card, which are bound to the real site',
           ''.join(box(10 + i * 126, 140 - i * 24, 116, 40 + i * 24, a, b) for i, (a, b) in enumerate([
               ('Password', 'know · none'), ('SMS code', 'relay, SIM swap'), ('App code', 'can be relayed'),
               ('Push + number', 'moderate'), ('Passkey / FIDO2', 'bound to site')]))
           + label(320, 18, 'phishing resistance rises to the right', 12))

_LAYERS = svg(640, 200, 'Security layers from the outside in: perimeter fences, bollards and lighting; entry with guards, badges and a vestibule; inside cameras, alarms and motion sensors; equipment door and cable locks; identity with IAM, MFA and SSO; access with least privilege, ACLs and Zero Trust',
              ''.join(box(10 + i * 18, 10 + i * 30, 620 - i * 36, 28, a) for i, a in enumerate([
                  'Perimeter: fences · bollards · lighting', 'Entry: guards · badge · vestibule', 'Inside: cameras · alarms · motion sensors',
                  'Equipment: door locks · cable locks', 'Identity: IAM · MFA · SSO', 'Access: least privilege · ACLs · Zero Trust'])))

_IR = svg(640, 130, 'Support-role malware response: recognise indicators, isolate from the network, preserve the state without wiping, report to security, then remediate only as security directs',
          ''.join(box(10 + i * 126, 30, 116, 56, a, b) + (arrow(126 + i * 126, 58, 136 + i * 126, 58) if i < 4 else '')
                  for i, (a, b) in enumerate([('Recognise', 'indicators'), ('Isolate', 'cable · Wi-Fi'), ('Preserve', 'no wipe'),
                                              ('Report', 'to security'), ('Remediate', 'as directed')]))
          + label(320, 118, 'you own the first four; security owns the fifth', 11))

_REDIR = svg(640, 140, 'Where a browser redirect can come from, closest to the user first: a malicious extension, a proxy setting, the hosts file or PC DNS setting, the router or upstream DNS, the website itself; test from the inside out',
             ''.join(box(10 + i * 126, 30, 116, 50, a, b) + (arrow(126 + i * 126, 55, 136 + i * 126, 55) if i < 4 else '')
                     for i, (a, b) in enumerate([('Extension', 'new profile'), ('Proxy', 'browser / OS'), ('hosts / DNS', 'on the PC'),
                                                 ('Router DNS', '2nd device'), ('Website', 'compromised')]))
             + label(320, 110, 'test left to right — a second device on the same network splits PC from upstream', 11))

_SAN = svg(640, 170, 'Choosing a sanitization method: start from the data sensitivity; if the media stays for internal reuse, clear; if it leaves, purge with sanitize or cryptographic erase, or destroy highly sensitive media; always record and verify',
           box(10, 60, 130, 50, 'Data', 'sensitivity') + arrow(140, 85, 170, 85) + box(170, 60, 140, 50, 'Leaving the', 'organisation?')
           + arrow(310, 72, 350, 35) + arrow(310, 98, 350, 135)
           + box(350, 10, 150, 50, 'No → Clear', 'internal reuse') + box(350, 110, 150, 50, 'Yes → Purge', 'or destroy')
           + arrow(500, 35, 530, 80) + arrow(500, 135, 530, 95) + box(530, 60, 100, 50, 'Record', '+ verify'))

_HARD = svg(640, 130, 'Hardening a workstation outside in: physical cable lock and firmware password; disk encryption; accounts with no guest and a renamed admin; sign-in lockout, screen lock and MFA; software with AutoRun and unused services off',
            ''.join(box(10 + i * 126, 30, 116, 60, a, b) for i, (a, b) in enumerate([
                ('Physical', 'cable · UEFI pw'), ('Disk', 'BitLocker'), ('Accounts', 'no guest'), ('Sign-in', 'lockout · lock'),
                ('Software', 'AutoRun off')]))
            + label(320, 118, 'each layer removes one easy way in', 11))

_VOL = svg(640, 130, 'Order of volatility from RFC 3227, most volatile first: registers and cache; memory, ARP and the process table; temporary files; disk; remote logs; archive media',
           ''.join(box(10 + i * 105, 30, 98, 56, a, b) for i, (a, b) in enumerate([
               ('Registers', 'cache'), ('Memory', 'ARP · procs'), ('Temp files', ''), ('Disk', ''), ('Remote logs', ''), ('Archive', 'media')]))
           + arrow(40, 105, 600, 105) + label(320, 124, 'collect left first — power-off destroys the left half', 11))

_OOB = svg(640, 150, 'Verify out of band: an unusual request to pay, reset or share; check for urgency, secrecy or new details; contact the requester on a channel you already hold; proceed if confirmed, report if not',
           box(10, 50, 120, 50, 'Unusual', 'pay · reset · share') + arrow(130, 75, 155, 75) + box(155, 50, 130, 50, 'Urgent, secret,', 'new details?')
           + arrow(285, 75, 310, 75) + box(310, 50, 140, 50, 'Call a number', 'you already hold')
           + arrow(450, 65, 480, 35) + arrow(450, 85, 480, 115)
           + box(480, 10, 150, 45, 'Confirmed: proceed') + box(480, 95, 150, 45, 'Not: report it'))

LESSONS = {
    '10.1': {
        'start-here-security-is-part-of-the-ticket': skip(
            'Start here — security is part of the ticket', 'orientation', 'A start-here block framing the chapter’s habits.'),

        'core-content': section(
            'Core content', 'IT-10.1',
            [check('A system asks for a password and then a security question. Is that MFA?',
                   'No — a password and an answer are both things you know',
                   ['Yes — any two separate steps at sign-in count as MFA', 'Yes, but only when the answer is longer than the password'],
                   'MFA needs at least two different factor kinds: know, have, are. A password and a security answer are the '
                   'same kind used twice, so it is still a single factor however long the answer is.', mc=[SAMEF, SAMEF])],
            plain('''<p>Sign-in proves <strong>who</strong> you are. Permissions decide <strong>what</strong> you may do.</p>
<p>There are three kinds of proof: something you <em>know</em> (a password), something you <em>have</em> (a phone or
a key) and something you <em>are</em> (a fingerprint). MFA uses two different kinds.</p>
<p>Some MFA can still be tricked. A fake page can pass on a code you type. Passkeys and security keys only work on the
real site.</p>
<p>Give people only the rights their job needs. Technicians use their own named admin accounts, never a shared one.</p>
<p>Lock your screen with Windows key + L when you leave the desk.</p>''',
                  L101 + '; ' + NIST63 + '; ' + CISA_MFA,
                  [check('Which of these resists a fake sign-in page best?',
                         'A passkey, which only works on the real site',
                         ['A six-digit code sent by text message', 'A six-digit code from an authenticator app'],
                         'A passkey is bound to the real website, so a look-alike site gets nothing useful. Codes from SMS or an '
                         'app can be typed into a fake page and relayed to the real one in real time.', mc=[SMS, OTP])]),
            analogy('''<p>Think of collecting a parcel at the post office.</p>
<p>The clerk asks for your name (something you know), the delivery card (something you have) and looks at your photo
ID (something you are). Saying your name twice is not two checks. A con artist standing next to you could overhear a
reference number and say it first — that is a relayed code. But a card that only fits <em>this</em> counter’s reader
cannot be used at a fake counter down the road: that is a passkey.</p>
<p>The clerk can only open the parcel shelves for their own counter, not the safe. That is least privilege.</p>''',
                    L101 + ' (post-office analogy written for this rung)',
                    [check('At 23:40 a lecturer gets a dozen sign-in prompts she did not start, and finally taps Approve. What does it mean?',
                           'Someone is signing in with her password',
                           ['Her authenticator app needs an update', 'Her phone clock has drifted out of sync'],
                           'Unexpected prompts mean someone is signing in with her password and hoping she approves. Report it to '
                           'security at once: revoke sessions, reset from a clean device and review MFA methods.', mc=[FATIGUE, FATIGUE])]),
            visual(_MFA + '''
<ol class="ladder-trace">
<li>Repeated unexpected push prompts at night; one was approved.</li>
<li>Treat it as a security incident: report to security at once.</li>
<li>Security revokes her sessions and resets her password from a clean device.</li>
<li>Review her MFA methods and mailbox rules.</li>
<li>Enrol number matching now and a passkey next, moving her right on the chart.</li></ol>''',
                   L101 + ' (method table and real-world scenario, drawn); ' + NIST63,
                   [check('Why do technicians use their own named admin accounts, never a shared one?',
                          'So every change can be traced to a person',
                          ['Because shared accounts cannot be given admin rights', 'Because named accounts never need a password'],
                          'A named account makes each privileged action traceable; a shared admin password is unaccountable privilege. '
                          'Shared accounts can have admin rights, which is exactly the problem.', mc=[SHARED, None])]),
            tryit('''<p>Sort each sign-in method by factor kind and phishing resistance, then predict the answer before
you reveal it.</p>''',
                  L101 + '; ' + NIST63,
                  [check('Which is the better way to give a technician admin rights for one change?',
                         'Just-in-time elevation for that change',
                         ['Permanent admin rights so they are never blocked', 'The shared local admin password on a sticky note'],
                         'Just-in-time access grants rights only when needed, for a limited time, with logging. Standing admin '
                         'rights and shared passwords both leave privilege nobody is accountable for.', mc=[STANDING, SHARED])],
                  widget=sort('How phishing-resistant is each method?',
                              {'High (bound to the real site)': ['Passkey', 'FIDO2 security key', 'Smart card (PIV)'],
                               'Low or moderate (can be relayed)': ['SMS code', 'Authenticator app code', 'Push with number matching']},
                              'Only methods bound to the real site defeat a look-alike sign-in page.'))),

        'daily-controls': same_as('core-content', 'Daily controls', 'The same daily controls as a checklist.'),
        'reference-authentication-and-passwords-current-guidance': skip(
            'Reference — authentication and passwords (current guidance)', 'reference', 'A reference summary of NIST SP 800-63B-4 password rules.'),

        'physical-and-logical-security-measures': section(
            'Physical and logical security measures', 'IT-10.1',
            [check('Staff keep holding the badge door open for people carrying boxes. Which control stops this?',
                   'An access control vestibule with interlocked doors',
                   ['Brighter lighting and a new fence around the car park', 'A longer password policy for every staff account'],
                   'A vestibule has two interlocked doors; the second opens only after the first closes, which defeats '
                   'tailgating. Lighting and fences work at the perimeter, and passwords are a logical control.', mc=[CPURP, CPURP])],
            plain('''<p>Security comes in layers, from the outside in.</p>
<p><strong>Physical</strong> controls stop people reaching things. Fences and bollards keep cars back. Badge readers log
who goes in. A vestibule has two doors, and the second only opens when the first is shut. That stops tailgating. Cameras
and alarms catch what gets past.</p>
<p><strong>Logical</strong> controls work in software. MFA proves who you are. Least privilege and ACLs limit what you
reach. Zero Trust checks every request, even from inside the network.</p>
<p>No single layer is enough.</p>''',
                  L101 + '; ' + NIST53,
                  [check('What does Zero Trust mean?',
                         'Every request is verified, wherever on the network it comes from',
                         ['Nobody is allowed to sign in from outside the office at all', 'Devices on the office network are trusted automatically'],
                         'Zero Trust (NIST SP 800-207) trusts no user or device because of its network location; each request is '
                         'checked. Trusting the office network is the old model it replaces.', mc=[TRUSTLAN, TRUSTLAN])]),
            analogy('''<p>Think of a medieval castle.</p>
<p>A moat and walls keep armies at a distance (fences and bollards). The gatehouse has two portcullises, and the inner
one only rises once the outer one is down, so nobody slips in behind a cart (an access control vestibule). Watchmen on
the walls see and raise the alarm (cameras and motion sensors). The treasury has its own lock (server-room door locks).</p>
<p>And inside, the steward checks every request against the lord’s seal, even from people already within the walls —
being inside is not proof of loyalty. That is Zero Trust.</p>''',
                    L101 + ' (castle analogy written for this rung); ' + NIST53,
                    [check('In the castle story, which control is “two portcullises, the inner one rising only when the outer is down”?',
                           'An access control vestibule',
                           ['A bollard placed in front of the outer gate', 'A magnetometer at the gatehouse entrance'],
                           'Two interlocked doors are a vestibule (formerly a mantrap), which stops tailgating. A bollard stops '
                           'vehicles and a magnetometer screens people for metal.', mc=[CPURP, CPURP])]),
            visual(_LAYERS + '''
<ol class="ladder-trace">
<li>Door: badge reader plus PIN, every entry logged.</li>
<li>From the lobby: a vestibule, because staff were holding the door.</li>
<li>Inside: a camera on the door and racks, a motion sensor on the out-of-hours alarm.</li>
<li>Admins: SSO with a FIDO2 key; domain admin granted just in time through PAM.</li></ol>''',
                   L101 + ' (layers diagram and worked example “securing a new server room”, drawn)',
                   [check('Why is SMS the weakest MFA method in the lesson’s list?',
                          'Codes can be intercepted or redirected by SIM swapping',
                          ['Text messages arrive too slowly to be used at sign-in', 'Phones cannot store SMS codes for longer than a minute'],
                          'An attacker who takes over the phone number receives the code, and codes can be phished. Speed and '
                          'storage are not the weakness.', mc=[SMS, None])]),
            tryit('''<p>Sort each control into the layer where it works. Then predict before you reveal.</p>''',
                  L101 + '; ' + NIST53,
                  [check('What does a mobile digital key do?',
                         'Stores a door credential in a phone wallet',
                         ['Unlocks every laptop in the building by Bluetooth', 'Replaces the server-room door with a keypad'],
                         'A mobile digital key is an entry credential kept in a phone wallet; like a badge it is logged and can be '
                         'revoked. It does not unlock laptops or replace a door.', mc=[CPURP, None])],
                  widget=sort('Physical or logical control?',
                              {'Physical': ['Bollards', 'Access control vestibule', 'Cable lock', 'Motion sensor'],
                               'Logical': ['Least privilege', 'Zero Trust', 'ACL', 'Single sign-on']},
                              'Physical controls stop people reaching things; logical controls decide what an identity can do.'))),
    },
    '10.2': {
        'core-content': section(
            'Core content', 'IT-10.2',
            [check('You find ransomware on a shared lab PC. What do you do before anything else?',
                   'Isolate it, preserve its state and report it to security',
                   ['Reimage it at once so the ransomware cannot spread', 'Run a free cleaner from a USB stick to remove it'],
                   'Support isolates the PC from the network, leaves its state alone and reports to security. Reimaging destroys '
                   'the evidence of how it got in; cleaners are not incident response.', mc=[SOLO, RANSOM])],
            plain('''<p>Malware is an incident, not a normal fix.</p>
<p>Your job has three steps.</p>
<ol><li><strong>Isolate.</strong> Unplug the cable and turn off Wi-Fi.</li>
<li><strong>Preserve.</strong> Do not wipe it, reimage it or delete files.</li>
<li><strong>Report.</strong> Tell security what you saw and when.</li></ol>
<p>Security decides the rest. That can be a scan, a reimage or a restore.</p>
<p>Keep Defender on. Do not run random cleaners. If security asks for a scan, a Defender Offline scan restarts the PC and
scans before Windows loads. It finds malware that hides.</p>''',
                  L102 + '; ' + NIST61 + '; ' + MS_DEF,
                  [check('Why does a Defender Offline scan restart the PC?',
                         'It scans before Windows loads, so hiding malware is found',
                         ['It needs the PC to be disconnected from the internet', 'It runs faster than a full scan when Windows is off'],
                         'The offline scan runs from the recovery environment before Windows starts, catching malware that hides '
                         'from a running system. It is not about having no internet or about speed.', mc=[OFFSCAN, OFFSCAN])]),
            analogy('''<p>Think of a fire marshal arriving at a kitchen fire in a big hotel.</p>
<p>A good porter closes the kitchen doors so the smoke does not spread (isolate), does not mop up the scorch marks
(preserve), and calls the fire service with what they saw and when (report). The fire investigators then work out how
it started and whether other kitchens are at risk.</p>
<p>A porter who scrubs the kitchen clean before anyone arrives feels helpful, but has erased the clue to the faulty
fryer — and two days later six other kitchens catch fire from the same model.</p>''',
                    L102 + ' (hotel-fire analogy written for this rung, after the lesson’s “helpful reimage” scenario)',
                    [check('In the hotel story, “scrubbing the kitchen before anyone arrives” is like what?',
                           'Reimaging the PC before security has looked',
                           ['Unplugging the PC’s network cable straight away', 'Writing the times and symptoms into the ticket'],
                           'Wiping destroys the evidence security needs to find the entry point and other affected devices. '
                           'Unplugging the cable and writing the facts are the right first steps.', mc=[EVLATER, SOLO])]),
            visual(_IR + '''
<ol class="ladder-trace">
<li>10:14 pop-up “your PC is infected, call this number”; real-time protection off and greyed out.</li>
<li>10:16 network cable unplugged, Wi-Fi off. PC left on, no files deleted.</li>
<li>10:18 reported to Security, incident SEC-2210. User did not call the number or type a password.</li>
<li>Waiting for Security’s instructions; user given a loan laptop.</li></ol>''',
                   L102 + ' (response diagram and worked example ticket, drawn); ' + NIST61,
                   [check('Who decides whether to leave a suspected PC on or shut it down?',
                          'The organisation’s playbook and security team',
                          ['The user, because it is their PC and data', 'Always shut down, to stop the malware quickly'],
                          'Memory holds evidence, but ransomware may still be encrypting; the organisation’s playbook decides. '
                          'Shutting down by habit can destroy evidence security needed.', mc=[SHUT, None])]),
            tryit('''<p>Order the support-role steps, then work a real malware ticket in the lab: the seven-step removal
process, with Defender kept on throughout.</p>''',
                  L102 + '; ' + NIST61,
                  [check('A “cleaner” tool says it needs Defender switched off to run. What do you do?',
                         'Leave Defender on and do not run the tool',
                         ['Pause Defender for ten minutes while the tool runs', 'Uninstall Defender and reinstall it after the clean-up'],
                         'Defender stays on; disabling protection to let an unknown tool run is exactly what malware wants. '
                         'Remediation tools are chosen by security, not by a download.', mc=[DISDEF, DISDEF])],
                  widget=order('Put the support-role response in order.',
                               ['Recognise the indicators', 'Isolate from the network', 'Preserve the state', 'Report to security',
                                'Remediate as security directs'],
                               'Contain and preserve first; remediation decisions belong to the security team.'),
                  lab={'id': 'sec-malware', 'note': 'Work the INC ticket through the seven-step removal process with Defender on.'})),

        'malware-is-an-incident': same_as('core-content', 'Malware is an incident', 'The same contain-and-hand-off rule restated.'),
        'containment-without-heroics': same_as('core-content', 'Containment without heroics', 'The same isolate, document, hand off rule.'),
        'teach-block-phish-and-malware-as-tickets': skip(
            'Teach block — phish and malware as tickets', 'plan', 'An instructor’s teaching plan for the session.'),

        'pc-security-symptoms-and-browser-security-settings': section(
            'PC security symptoms and browser security settings', 'IT-10.2',
            [check('Every HTTPS site shows a certificate warning on one PC. What do you check first?',
                   'The PC’s clock: date, time and time zone',
                   ['The browser’s cache size and pop-up blocker', 'The office router’s firewall rules'],
                   'Certificates are valid only between two dates, so a wrong clock fails every site at once. Fix the time and '
                   'retest before suspecting interception; cache and router rules do not cause this.', mc=[CLOCK, BROWSET])],
            plain('''<p>Some signs point to malware. Fake virus alerts. Pop-ups. Searches that go to the wrong site. Updates
that keep failing. Files with a new ending and a ransom note.</p>
<p>Not every sign is malware. A warning on every website often means the PC clock is wrong. A flood of pop-up messages is
often a site the user allowed to send notifications.</p>
<p>For a redirect, start close to the user. Try a new browser profile with no extensions. Then check the proxy and the
hosts file. Then try another device on the same network.</p>
<p>Private browsing only stops the PC keeping history. Websites and the employer can still see it.</p>''',
                  L102,
                  [check('What does private browsing protect against?',
                         'The browser keeping local history and cookies',
                         ['Websites seeing what the user does on them', 'The employer’s network seeing the sites visited'],
                         'InPrivate or Incognito stops the browser storing history and cookies after the window closes. Websites, '
                         'the employer and the internet provider can still see the activity.', mc=[PRIV, PRIV])]),
            analogy('''<p>Think of a parcel that keeps arriving at the wrong house.</p>
<p>You do not start by phoning the national post office. First you check your own front door: did someone stick a new
label over your house number (a browser extension)? Then your own forwarding instructions (the proxy setting) and the
address book on your hall table (the hosts file). Then you ask a neighbour on the same street: are their parcels going
astray too? If yes, the problem is at the local sorting office (the router or upstream DNS); if no, it is at your house.</p>''',
                    L102 + ' (misdelivered-parcel analogy written for this rung)',
                    [check('In the parcel story, “asking a neighbour on the same street” matches which test?',
                           'Trying another device on the same network',
                           ['Clearing the browser cache and cookies on the PC', 'Reinstalling the browser from the vendor’s website'],
                           'A second device on the same network tells you which side of the PC the fault is on: if it is redirected '
                           'too, the cause is upstream. Clearing data or reinstalling skips that split.', mc=[REDIR, REDIR])]),
            visual(_REDIR + '''
<ol class="ladder-trace">
<li>Searches “go to a different search site”. Another PC on the same Wi-Fi is fine → cause is on this PC.</li>
<li>A new browser profile with no extensions searches normally → cause is in the user’s profile.</li>
<li>Extensions list: “PDF Converter Pro”, installed yesterday from a pop-up. Disable it → searches normal.</li>
<li>Remove it, reset the search engine and start page, run a full scan, check proxy and hosts.</li>
<li>Document the extension name; advise the user to install extensions only from the official store.</li></ol>''',
                   L102 + ' (redirect diagram and worked example “redirected searches”, drawn)',
                   [check('Every file in a shared folder now ends in .lockd and will not open. What is this?',
                          'A ransomware pattern, so isolate the PC now',
                          ['A broken Office install that needs a repair', 'A sync conflict that renaming will fix'],
                          'Many files with a new extension and no access is ransomware. Unplug the network, leave the PC on for '
                          'the incident team and report; do not rename files or run decryption tools.', mc=[RANSOM, SYMHW])]),
            tryit('''<p>Order the redirect tests from the inside out, then check one browser setting before you reveal it.</p>''',
                  L102,
                  [check('What does matching a vendor’s published SHA-256 hash with Get-FileHash show?',
                         'The file is the same one the vendor published',
                         ['The software is licensed to your organisation', 'The file is encrypted against malware'],
                         'A hash only verifies integrity: the same file gives the same hash. It does not license, register or '
                         'encrypt anything.', mc=[HASH, HASH])],
                  widget=order('Test a browser redirect from the inside out.',
                               ['New browser profile with no extensions', 'Proxy setting', 'hosts file and the PC’s DNS setting',
                                'Another device on the same network'],
                               'If the second device is redirected too, the cause is upstream of the PC.'))),

        'malware-types-and-the-tools-that-stop-them': section(
            'Malware types and the tools that stop them', 'IT-10.2',
            [check('A PC’s fans run all night at 95% CPU with no apps open, and a random-named process restarts when ended. What type is it?',
                   'A cryptominer using the PC’s processor to mine coins',
                   ['Ransomware that is encrypting the user’s files', 'Adware that shows the user pop-up advertising'],
                   'Constant high CPU or GPU with no visible task matches a cryptominer. Nothing is encrypted and there are no '
                   'pop-ups, which rules out ransomware and adware.', mc=[SYMHW, None])],
            plain('''<p>Malware types do different things.</p>
<ul><li>A <strong>virus</strong> spreads when an infected file runs.</li>
<li>A <strong>Trojan</strong> looks useful but hides a payload.</li>
<li>A <strong>rootkit</strong> hides deep in the system. You usually wipe and reinstall.</li>
<li><strong>Ransomware</strong> locks files and asks for money. Backups are the way back.</li>
<li>A <strong>keylogger</strong> records what you type.</li>
<li>A <strong>cryptominer</strong> uses the PC to make money. It is hot and slow.</li>
<li><strong>Fileless</strong> malware runs in memory. It leaves few files to scan.</li></ul>
<p>Many layers stop them: user training, email filters, firewalls, anti-malware and EDR.</p>''',
                  L102 + '; ' + NIST83,
                  [check('Why is a rootkit usually fixed by reinstalling the OS?',
                         'It hides itself with kernel or firmware access',
                         ['It deletes the antivirus program’s definition files', 'It only lives inside the browser’s saved passwords'],
                         'A rootkit uses kernel or firmware access to hide itself and other malware, so a scan from the infected '
                         'system cannot be trusted. Reinstall and restore data from a clean backup.', mc=[ROOTK, None])]),
            analogy('''<p>Think of the ways a burglar can get into a house.</p>
<p>A Trojan is a delivery driver with a fake parcel who is let in. A keylogger is a hidden microphone near the safe. A
rootkit is someone who has moved into the loft and changed the locks so you cannot see up there. A cryptominer is a
lodger running a space heater off your electricity. Ransomware locks every room and leaves a note asking for money.</p>
<p>The defences are layered too: the neighbours who report strangers (user training), the postal screening
(email gateway), the locks (firewall), the alarm (anti-malware), and a security company watching the alarm feed
round the clock (MDR).</p>''',
                    L102 + ' (burglary analogy written for this rung); ' + NIST83,
                    [check('In the burglary story, “a security company watching the alarm feed round the clock” is which tool?',
                           'MDR, a managed service team',
                           ['An email security gateway', 'A software firewall'],
                           'Managed detection and response is an external team monitoring and responding to EDR alerts. An email '
                           'gateway filters mail before delivery, and a firewall limits connections.', mc=[WRONGC, None])]),
            visual('''<ol class="ladder-trace">
<li>Symptom: a finance user’s webmail sends messages she did not write, even after a password change.</li>
<li>EDR on her PC flags a process recording keystrokes, installed from a “free PDF converter” → keylogger from a Trojan.</li>
<li>The technician isolates the PC through the EDR console, so it cannot report new passwords.</li>
<li>Passwords are reset from a <em>clean</em> device, and MFA is enabled.</li>
<li>The PC is reimaged, because the Trojan’s full reach is unknown.</li></ol>''',
                   L102 + ' (real-world scenario “the keyboard that told someone everything”, as a trace)',
                   [check('Why were her passwords reset from a clean device, not her own PC?',
                          'The keylogger would capture the new password',
                          ['Her PC’s browser cannot open the reset page', 'Password resets only work from the service desk'],
                          'A keylogger records every keystroke, so a new password typed on the infected PC would be stolen too. '
                          'Resetting from a clean device keeps it private.', mc=[UNDER, None])]),
            tryit('''<p>Sort each symptom to its malware type, then predict the defence before you reveal it.</p>''',
                  L102 + '; ' + NIST83,
                  [check('Why is fileless malware hard for traditional scanners to find?',
                         'It runs in memory and leaves few files',
                         ['It only runs on PCs that have no antivirus installed', 'It deletes itself whenever a scan begins'],
                         'Fileless malware uses built-in tools such as PowerShell or WMI and lives in memory, so there is little on '
                         'disk to scan. Behaviour-based EDR is better at spotting it.', mc=[SYMHW, None])],
                  widget=sort('Which malware type matches each sign?',
                              {'Ransomware': ['Files renamed with a new extension and a note'],
                               'Cryptominer': ['CPU at 95% all night, fans loud'],
                               'Keylogger': ['Passwords stolen again after every change'],
                               'Adware / PUP': ['New toolbar and a changed home page']},
                              'The symptom points to the type; the response is still isolate, preserve, report.'))),
    },
    '10.3': {
        'core-content': section(
            'Core content', 'IT-10.3',
            [check('A college SSD is being sold to a recycler. How should it be sanitized?',
                   'Purge it with the drive’s sanitize command',
                   ['Format it twice so that nothing can be read back', 'Delete every user profile and then empty the Recycle Bin'],
                   'Media leaving the organisation is purged; on an SSD that means the manufacturer’s sanitize function or a '
                   'cryptographic erase, because formatting and deleting leave data in remapped cells.', mc=[SSD, QFMT])],
            plain('''<p>If a laptop is lost, <strong>encryption</strong> keeps the data private. On Windows that is BitLocker
or device encryption.</p>
<p>Before a firmware update or a board repair, find the recovery key. For a personal device it is at
aka.ms/myrecoverykey. Never write the key into a ticket.</p>
<p>Updates come every month on the second Tuesday. Report devices that are not updating. Do not pause updates.</p>
<p>Found USB sticks go to security. Never plug them in.</p>
<p>When a drive leaves, wipe it the right way and keep a record. For an SSD, formatting is not enough.</p>''',
                  L103 + '; ' + MS_BL + '; ' + NIST88,
                  [check('A USB stick is found in the car park. What do you do with it?',
                         'Hand it to security without plugging it in',
                         ['Plug it into a lab PC to find its owner', 'Format it first and then keep it as a spare'],
                         'Unknown USB media is a classic way to get malware in; it goes to security, not into any PC. A lab PC or '
                         'formatting does not make it safe.', mc=[FUSB, FUSB])]),
            analogy('''<p>Think of selling an old filing cabinet.</p>
<p>Taking the folders out and leaving the labels on (a quick format) still tells the buyer what was in there. Shredding
each sheet properly (purge) or crushing the cabinet (destroy) means nothing comes back. If every sheet was written in
a code, burning the only codebook (cryptographic erase) makes all of it unreadable at once.</p>
<p>And an SSD is a cabinet that secretly keeps photocopies in a back drawer whenever you rewrite a page, so wiping the
front drawer is not enough — you need the maker’s own clear-out function. Whatever you do, keep a signed note of which
cabinet, how and when.</p>''',
                    L103 + ' (filing-cabinet analogy written for this rung); ' + NIST88,
                    [check('In the filing-cabinet story, what is “burning the only codebook”?',
                           'Cryptographic erase of the key',
                           ['A quick format of the drive', 'Clearing the user’s Recycle Bin'],
                           'Cryptographic erase destroys the encryption key, so encrypted data becomes unreadable. A quick format '
                           'and emptying the Recycle Bin leave the data recoverable.', mc=[QFMT, WIPEOK])]),
            visual(_SAN + '''
<ol class="ladder-trace">
<li>Asset tag and serial number of the drive.</li>
<li>Method: clear, purge, destroy or cryptographic erase.</li>
<li>Date and the operator’s name.</li>
<li>Verification result — the record is the evidence the data is gone.</li></ol>''',
                   L103 + ' (sanitization decision diagram and record, drawn); ' + NIST88,
                   [check('A laptop needs a motherboard repair and has BitLocker on. What do you confirm first?',
                          'Where its recovery key is stored',
                          ['That the TPM has been cleared first', 'That the key is written into the ticket'],
                          'A board or TPM change triggers BitLocker recovery, so confirm the key’s location (the Microsoft account '
                          'or the organisation’s directory). Never clear the TPM or put the key in a ticket.', mc=[RKEY, RKEY])]),
            tryit('''<p>Sort each device to the sanitization method that fits where it is going. Then reveal the record’s
contents once you have predicted them.</p>''',
                  L103 + '; ' + NIST88,
                  [check('Why do most organisations deploy updates in rings?',
                         'So a bad update reaches only a small pilot group first',
                         ['So that every PC updates at exactly the same moment', 'So users can pause updates they find inconvenient'],
                         'A pilot ring gets the update first; if it misbehaves, only a few devices are affected. Rings are not for '
                         'pausing updates for convenience.', mc=[DISPROT, None])],
                  widget=sort('Which method fits?',
                              {'Clear': ['HDD reused by the next staff member'],
                               'Purge or crypto erase': ['SSD sold to a recycler', 'Encrypted laptop leaving the college'],
                               'Destroy': ['Drive with research health data that cannot be purged']},
                              'Where the media is going and how sensitive the data is decide the method.'))),

        'hygiene': same_as('core-content', 'Hygiene', 'The same hygiene rules in two lines.'),

        'workstation-security-options-and-hardening': section(
            'Workstation security options and hardening', 'IT-10.3',
            [check('Why set an expiry date when creating a contractor’s account?',
                   'So that the account stops on its end date',
                   ['So that the password never needs changing', 'So the account gets admin rights by default'],
                   'An expiration date (net user /expires or the AD account properties) ends access on time even if nobody '
                   'remembers. It has nothing to do with password changes or admin rights.', mc=[BROADP, None])],
            plain('''<p>Hardening closes the easy ways into a PC.</p>
<ul><li>Fit a cable lock. Set a firmware (UEFI) password.</li>
<li>Encrypt the disk.</li>
<li>Turn off the guest account. Rename or disable the built-in admin.</li>
<li>Lock the account after too many wrong passwords. Lock the screen after a few minutes.</li>
<li>Give temporary accounts an end date.</li>
<li>Turn off AutoPlay and services the PC does not use.</li></ul>
<p>Users work as standard users. Admin rights are used only when needed.</p>''',
                  L103 + '; ' + MS_HARD,
                  [check('What does a BIOS/UEFI password protect against?',
                         'Firmware changes or booting from other media',
                         ['Users signing in to Windows with a weak password', 'Malware arriving as an email attachment'],
                         'A firmware password stops someone changing the boot order or firmware settings and booting from a USB '
                         'stick. Windows sign-in and email are protected by other controls.', mc=[WRONGC, WRONGC])]),
            analogy('''<p>Think of closing up a shop at night.</p>
<p>You chain the bike outside (cable lock), lock the till (disk encryption), and take the “spare key under the mat”
away (no guest account, no default admin password). The alarm locks the door after three wrong codes (account lockout).
The temporary helper’s key card stops working on their last day by itself (account expiry). And you unplug the machines
nobody uses tonight (unused services off), so there is less to go wrong.</p>
<p>No single step stops a determined thief; together they make the shop a poor target.</p>''',
                    L103 + ' (shop-closing analogy written for this rung)',
                    [check('In the shop story, “taking the spare key from under the mat” matches which step?',
                           'Disabling guest and default admin logins',
                           ['Turning on BitLocker for the system drive', 'Setting a five-minute screen-lock timeout'],
                           'Guest accounts and default admin credentials are well-known ways in, like a key under the mat. Encryption '
                           'protects data at rest and screen lock covers an unattended session.', mc=[SHARED, None])]),
            visual(_HARD + '''
<ol class="ladder-trace">
<li>Named standard accounts for each receptionist; remove the shared admin login.</li>
<li>Five-minute screen lock; logon hours matching opening times.</li>
<li>An account lockout threshold for repeated bad passwords.</li>
<li>BitLocker on, a UEFI password, a cable lock.</li>
<li>AutoPlay off, unused services off; record every setting on the asset.</li></ol>''',
                   L103 + ' (hardening layers and worked example “a shared front-desk PC”, drawn); ' + MS_HARD,
                   [check('What does turning off AutoRun / AutoPlay prevent?',
                          'Code running automatically from inserted media',
                          ['Windows Update installing patches automatically', 'Apps starting automatically when the user signs in'],
                          'AutoRun and AutoPlay act on inserted USB drives or discs; turning them off stops that media running code. '
                          'Windows Update and start-up apps are separate settings.', mc=[FUSB, None])]),
            tryit('''<p>On a real Linux VM, apply the same ideas: lock the departed user’s account (not delete it) and
give the help-desk team only the sudo rights their job needs.</p>''',
                  L103 + '; ' + MS_HARD,
                  [check('An audit finds a contractor’s account still active three months after the contract. What is the process fix?',
                         'Expiry dates and standard roles for temporary accounts',
                         ['Change the contractor’s password and leave the account active', 'Give the account to the next contractor who starts'],
                         'Disable it and review what it did, then fix the process: temporary accounts get an end date and a standard '
                         'user role when created. A new password or reuse keeps the risk.', mc=[BROADP, SHARED])],
                  widget=reveal('Before you reveal: which net user switch sets a temporary account’s end date?',
                                '<code>net user name /expires:date</code> — and <code>/times:</code> restricts the hours it can sign in.'),
                  lab={'id': 'linux-vm-users', 'note': 'Lock the leaver’s account and set least-privilege sudo; the probe checks /etc/shadow and sudoers.'})),
    },

    '10.4': {
        'core-content': section(
            'Core content', 'IT-10.4',
            [check('A user typed her college password on a phishing page. Which response fits?',
                   'Reset from a clean device, revoke sessions, check MFA and rules',
                   ['Tell her to delete the email and change her password next month', 'Scan her PC and close the ticket if nothing is found'],
                   'Entering a password means the account is compromised: reset from a clean device, revoke active sessions, '
                   'review MFA methods and check mailbox rules for forwarding, and watch further sign-ins.', mc=[COMPREQ, UNDER])],
            plain('''<p>Thank a user who reports a phish. You want them to keep doing it.</p>
<p>Then ask what they did. The next steps depend on it.</p>
<ul><li>Did nothing: report it with the Report button.</li>
<li>Clicked a link: report it and scan the PC.</li>
<li>Opened an attachment: isolate the PC.</li>
<li>Typed a password: the account is taken. Reset it from a clean PC and end all sessions. Check MFA and mailbox rules.</li></ul>
<p>If security wants evidence, collect what disappears first, like memory, before the disk. Record who held the device and
when. That is the chain of custody.</p>''',
                  L104 + '; ' + RFC3227 + '; ' + NIST61,
                  [check('Why use the Report button, not forward, for a phishing email?',
                         'It keeps the original headers that security needs',
                         ['Forwarded mail is always blocked by the gateway', 'The Report button deletes it from every mailbox'],
                         'Reporting, or sending the message as an attachment, keeps the headers security needs to trace and block '
                         'the sender. Security removes copies from other mailboxes afterwards.', mc=[FWD, None])]),
            analogy('''<p>Think of a hospital’s triage desk.</p>
<p>A patient who “touched something odd” gets a few questions first, because the treatment depends on the answer:
just looked at it (note it and send them home), touched it (check the skin), swallowed it (urgent care), or it got into
the bloodstream (full emergency response, and check for hidden effects later — like a mailbox rule the attacker added
quietly).</p>
<p>If police are involved, the nurse takes the blood sample before the bandage, because it changes fastest, and signs
the sample bag over in person. That is the order of volatility and the chain of custody.</p>''',
                    L104 + ' (hospital-triage analogy written for this rung); ' + RFC3227,
                    [check('Which is more volatile, the ARP table or the disk?',
                           'The ARP table',
                           ['The disk', 'They are equally volatile'],
                           'RFC 3227 puts memory, the ARP table and the process table near the top: they change in seconds and are '
                           'lost at power-off. The disk survives a restart, so it is collected later.', mc=[VOLAT, VOLAT])]),
            visual(_VOL + '''
<ol class="ladder-trace">
<li>09:02 user reports “Payroll update required”; clicked at 08:51 and entered her password; approved no MFA prompt.</li>
<li>09:04 reported to Security (SEC-2231) with the Report button.</li>
<li>09:06 password reset from the service-desk PC; all sessions revoked by Security.</li>
<li>Mailbox rule “fwd” forwarding outside, created 08:55 — removed by Security, screenshot on SEC-2231.</li>
<li>MFA re-enrolled with number matching; sign-ins monitored for 7 days.</li></ol>''',
                   L104 + ' (volatility diagram and the capstone ticket, drawn); ' + RFC3227,
                   [check('Why check mailbox rules even after the password is reset?',
                          'Attackers add rules that keep working afterwards',
                          ['Mailbox rules reset the password back to the old one', 'Rules have to be rebuilt after every password change'],
                          'An attacker in a mailbox often adds a rule to forward mail outside or delete replies; it keeps running after '
                          'a reset until someone removes it.', mc=[UNDER, None])]),
            tryit('''<p>On a real Linux VM flagged by the IDS, act as first responder: preserve the evidence before you
change anything, then remove the attacker’s persistence and hand over a report.</p>''',
                  L104 + '; ' + RFC3227,
                  [check('What does a chain-of-custody record show?',
                         'Who held the evidence, when, and what they did',
                         ['The full timeline of the attacker’s actions on the PC', 'The list of every asset the organisation owns'],
                         'Chain of custody is who had the item, when and what they did with it, from collection to the end of the '
                         'case. A gap can make evidence unusable; it is not a timeline or an asset list.', mc=[CUSTODY, CUSTODY])],
                  widget=order('Collect evidence in order of volatility.',
                               ['Registers and cache', 'Memory, ARP and process table', 'Temporary files', 'Disk', 'Remote logs',
                                'Archive media'],
                               'Power-off destroys the first half, which is why “don’t switch it off” is so often the instruction.'),
                  lab={'id': 'linux-vm-incident', 'note': 'Preserve evidence before any change, then remove persistence; the probe checks both.'})),

        'phish-follow-up': same_as('core-content', 'Phish follow-up', 'The same two outcomes, not opened and password typed.'),

        'social-engineering-attacks-threats-and-vulnerabilities': section(
            'Social engineering attacks, threats and vulnerabilities', 'IT-10.4',
            [check('A supplier emails new bank details and asks for payment today. How do you verify it?',
                   'Call the supplier on the number you already hold',
                   ['Reply to the email and ask them to confirm the change', 'Call the phone number printed in the email’s signature'],
                   'Verify out of band, through a channel you already trust, such as the number in the finance system. Replying '
                   'or calling the number in the message reaches the attacker.', mc=[GIVEN, GIVEN])],
            plain('''<p>Social engineering attacks the person, not the PC.</p>
<ul><li><strong>Phishing</strong> is a fake email. Spear phishing targets one person. Whaling targets bosses.</li>
<li><strong>Vishing</strong> is a phone call. <strong>Smishing</strong> is a text.</li>
<li><strong>Tailgating</strong> is following someone through a secure door.</li>
<li><strong>Shoulder surfing</strong> is watching someone type.</li></ul>
<p>Look for hurry, secrecy or changed details. Then check with the person in another way, using a number you already
have. Never use the details in the message.</p>
<p>The help desk never asks for an MFA code.</p>''',
                  L104 + '; ' + CISA_SE,
                  [check('What is the difference between spear phishing and whaling?',
                         'Whaling is spear phishing aimed at executives',
                         ['Whaling uses text messages instead of email', 'Spear phishing is sent to everyone in the company'],
                         'Spear phishing targets a named person with researched details; whaling is the same aimed at senior '
                         'executives. Smishing is SMS, and mass mail is ordinary phishing.', mc=[UNDER, None])]),
            analogy('''<p>Think of a con artist at a bank counter.</p>
<p>He wears a smart suit and says he is the branch manager’s new assistant (pretexting), says the matter is urgent and
confidential (pressure), and hands over a card with “his” phone number for confirmation. A careful cashier ignores the
card, rings the branch manager on the number in the staff directory, and learns there is no new assistant.</p>
<p>The same check beats a fake supplier email, a fake “IT support” call and a fake text: the second, trusted channel is
the one the attacker does not control.</p>''',
                    L104 + ' (bank-counter analogy written for this rung); ' + CISA_SE,
                    [check('In the bank story, why does the cashier ignore the card with “his” phone number?',
                           'The number on his card may reach the con artist',
                           ['Business cards are not allowed in the branch', 'The directory number is always faster to call'],
                           'Contact details supplied in the request are controlled by the attacker; only a channel you already hold '
                           'is trustworthy. Speed and policy on cards are not the reason.', mc=[GIVEN, None])]),
            visual(_OOB + '''
<ol class="ladder-trace">
<li>A user says “IT” just called and asked her to read out her authenticator code. She did.</li>
<li>That is vishing aimed at MFA: the attacker already had her password.</li>
<li>Treat it as a compromised account: reset, revoke sessions, re-register MFA, check sign-in logs.</li>
<li>Escalate to security; remind her the help desk never asks for MFA codes.</li></ol>''',
                   L104 + ' (verify-out-of-band diagram and real-world scenario, drawn)',
                   [check('Why do attackers put phishing links in QR codes?',
                          'Filters and users cannot easily read the link',
                          ['QR codes encrypt the link so it cannot be blocked later', 'Phones refuse to warn users about QR code links'],
                          'The link is inside an image, so email filters and people cannot easily see where it goes. QR codes do '
                          'not encrypt anything.', mc=[UNDER, None])]),
            tryit('''<p>Sort each attack to its name, then put the verify-out-of-band steps in order in your head and
reveal them.</p>''',
                  L104 + '; ' + CISA_SE,
                  [check('A rogue Wi-Fi access point uses the college’s network name to intercept traffic. What is it called?',
                         'An evil twin',
                         ['A zero-day', 'A supply chain attack'],
                         'An evil twin advertises a trusted network name. A zero-day is a flaw with no patch yet, and a supply chain '
                         'attack comes through a trusted vendor or update.', mc=[UNDER, None])],
                  widget=sort('Name the technique.',
                              {'Vishing': ['A caller asks for your MFA code'],
                               'Smishing': ['A text says your parcel needs a fee'],
                               'Tailgating': ['Someone follows you through the badge door'],
                               'Business email compromise': ['A supplier “changes bank details” by email']},
                              'All four are beaten by verifying through a channel you already trust.'))),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '10.1': {'core-content': '6c8b6368faef', 'physical-and-logical-security-measures': '069da8d01e07'},
    '10.2': {'core-content': 'f34b0569a365', 'pc-security-symptoms-and-browser-security-settings': 'ccff02def16a', 'malware-types-and-the-tools-that-stop-them': '8fc7015dbb16'},
    '10.3': {'core-content': 'd87092c81595', 'workstation-security-options-and-hardening': '8da7e0508f59'},
    '10.4': {'core-content': 'd9561ac611c0', 'social-engineering-attacks-threats-and-vulnerabilities': '2631090f5e31'},
}
