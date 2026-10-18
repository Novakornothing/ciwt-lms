"""A+ Core 2 2.1 (physical and logical security measures) — ITSUP 10.1.  Round 2 of pass 11."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-physsec', 'Layers of physical and logical security',
    ['Perimeter:\nfences, bollards,\nlighting', 'Entry:\nguards, badge reader,\nvestibule', 'Inside:\ncameras, alarms,\nmotion sensors', 'Equipment:\ndoor and cable locks', 'Identity:\nIAM, MFA, SSO', 'Access:\nleast privilege,\nACLs, Zero Trust'],
    'Six boxes from the outside in. Fences, bollards and lighting slow and deter people and vehicles at the perimeter. At the '
    'entrance, guards, badge readers, key fobs, smart cards or a mobile digital key control who enters, and an access control '
    'vestibule stops tailgating; magnetometers screen for metal objects. Inside, video surveillance, alarm systems and motion sensors '
    'detect and record. Equipment is protected by door locks on server rooms and cable locks on devices. Logically, identity and '
    'access management with multifactor authentication and single sign-on proves who the user is, and least privilege, ACLs and '
    'Zero Trust limit what they can reach.',
    'Each layer deters, delays, detects or limits; no single layer is enough.', cols=3)

HTML = f'''
<p>A+ Core 2 2.1 summarises physical and logical security measures and what each is for (NIST SP 800-53 Rev. 5,
Physical and Environmental Protection and Access Control families).</p>
<h4>Physical security</h4>
<ul>
<li><strong>Bollards</strong> — short posts that stop vehicles reaching doors or glass. <strong>Fences</strong> and <strong>lighting</strong>
deter and expose intruders.</li>
<li><strong>Access control vestibule</strong> (formerly “mantrap”) — two interlocked doors; the second opens only after the first closes,
which defeats tailgating and piggybacking.</li>
<li><strong>Badge reader</strong>, <strong>key fob</strong>, <strong>smart card</strong> and <strong>mobile digital key</strong> (a credential in a phone wallet)
— electronic entry that is logged and can be revoked.</li>
<li><strong>Security guards</strong> — judge and respond; can check identity and escort visitors. <strong>Magnetometers</strong> (metal detectors) screen people.</li>
<li><strong>Video surveillance</strong> records and deters; <strong>alarm systems</strong> and <strong>motion sensors</strong> detect entry out of hours.</li>
<li><strong>Door locks</strong> on server rooms and wiring closets; <strong>equipment locks</strong> (cable locks on laptops, locking racks and cases).</li>
<li><strong>Biometrics</strong> — fingerprint, facial or other body features; often one factor of MFA.</li>
</ul>
<h4>Logical security</h4>
<ul>
<li><strong>Least privilege</strong> — only the rights needed for the job. <strong>Zero Trust</strong> — no user or device is trusted because of
its network location; every request is verified (NIST SP 800-207). <strong>ACLs</strong> — lists that permit or deny access to files or traffic.</li>
<li><strong>MFA</strong> — two or more different factor types (something you know, have, are). Methods: <strong>hardware token</strong> or FIDO2
security key (phishing-resistant), <strong>authenticator application</strong>, <strong>TOTP/OTP</strong> codes (RFC 6238), push
notification, <strong>SMS or voice call</strong> and email codes (weakest: open to SIM swapping and interception; NIST SP 800-63B).</li>
<li><strong>SSO</strong> — one sign-in gives access to many applications; <strong>SAML</strong> is a common standard for passing that sign-in
from an identity provider to the application.</li>
<li><strong>Just-in-time access / PAM</strong> — privileged access management grants admin rights only when needed, for a limited time,
with logging; no standing admin rights.</li>
<li><strong>IAM</strong> (identity and access management) and <strong>directory services</strong> such as Active Directory hold accounts and groups.
<strong>MDM</strong> enforces device policy on phones and laptops. <strong>DLP</strong> (data loss prevention) detects and blocks sensitive data leaving.</li>
</ul>
{_FIG}
{worked('securing a new server room', '''<ol>
<li>Door: badge reader with a PIN (two factors) and a log of every entry; keys only for facilities, kept in a lock box.</li>
<li>Entrance from the lobby: an access control vestibule, because staff were holding the door for others.</li>
<li>Inside: a camera on the door and racks, and a motion sensor tied to the alarm system out of hours.</li>
<li>Admins sign in through SSO with a FIDO2 security key; domain admin rights are granted just-in-time through PAM for each change.</li></ol>''')}
{scenario('the friendly tailgater', '''<p>A visitor in a hi-vis vest follows an employee through the badge door carrying boxes; nobody stops him and a laptop goes
missing. The review finds that the badge door works, but people hold it open to be polite. The site adds a vestibule at the main
entrance, a guard at reception who signs in and escorts visitors, cable locks on hot-desk laptops, and a short awareness session:
holding the door is how tailgating works.</p>''')}
{cfu(('What does an access control vestibule prevent?', 'Tailgating and piggybacking: the second door opens only after the first closes.'),
     ('Why is SMS the weakest MFA method?', 'Codes can be intercepted or redirected by SIM swapping.'),
     ('What is just-in-time access?', 'Privileged rights granted only when needed, for a limited time, through PAM.'))}
'''

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 10, 'lesson': 1, 'id': 'cert-phys-logical-sec', 'title': 'Physical and logical security measures',
     'cert': ['A2:2.1'], 'html': sme_note('Physical and logical security measures (A+ Core 2 2.1).') + HTML,
     'sources': ['nist-80053r5', 'nist-800207', 'nist-80063b4', 'rfc6238', 'oasis-saml', 'fido']},
]

GLOSSARY = [
    ('Access control vestibule', 'Two interlocked doors that stop tailgating; formerly called a mantrap.'),
    ('Bollard', 'Short, sturdy post that stops vehicles reaching a building.'),
    ('Mobile digital key', 'Door or vehicle credential stored in a phone wallet.'),
    ('Magnetometer', 'Metal detector used to screen people at an entrance.'),
    ('Just-in-time access', 'Privileged rights granted only when needed and for a limited time.'),
    ('SAML', 'Security Assertion Markup Language: standard for passing a sign-in from an identity provider to an application.'),
    ('DLP', 'Data loss prevention: tools that detect and block sensitive data leaving the organisation.'),
]

MISCONCEPTIONS = {
    'MC-C-IT10-CONTROL-PURPOSE': {'obj': 'IT-10.1', 'label': 'Picking a physical control that addresses a different threat (e.g. cameras for tailgating, bollards for people)',
                                  'fix': 'A vestibule stops tailgating, bollards stop vehicles, cameras detect and record.', 'terms': ['vestibule', 'tailgating', 'bollard', 'camera']},
    'MC-C-IT10-MFA-SAME-FACTOR': {'obj': 'IT-10.1', 'label': 'Counting two things of the same type (two passwords, password plus PIN) as MFA',
                                  'fix': 'MFA needs different factor types: know, have, are.', 'terms': ['mfa', 'factor', 'pin', 'token']},
    'MC-C-IT10-SMS-STRONG': {'obj': 'IT-10.1', 'label': 'Believing SMS or voice codes are the strongest MFA option',
                             'fix': 'SMS codes can be intercepted or SIM-swapped; FIDO2 keys resist phishing.', 'terms': ['sms', 'fido', 'security key', 'phishing']},
    'MC-C-IT10-TRUST-LAN': {'obj': 'IT-10.1', 'label': 'Trusting a user or device because it is on the internal network',
                            'fix': 'Zero Trust verifies every request regardless of network location.', 'terms': ['zero trust', 'verify', 'location']},
    'MC-C-IT10-STANDING-ADMIN': {'obj': 'IT-10.1', 'label': 'Giving permanent admin rights where just-in-time access would do',
                                 'fix': 'PAM grants privileged rights only when needed, for a limited time, with logging.', 'terms': ['just-in-time', 'pam', 'privileged', 'least privilege']},
}

ITEMS = [
    single('A2:2.1', 'IT-10.1', 11, 'Staff keep holding the badge door open for people behind them. Which control stops this most directly?',
           'An access control vestibule', ['More video surveillance cameras', 'Bollards outside the entrance', 'Brighter car park lighting'],
           'A vestibule lets one person through at a time; cameras only record, bollards stop vehicles.',
           mc=['MC-C-IT10-CONTROL-PURPOSE', 'MC-C-IT10-CONTROL-PURPOSE', 'MC-C-IT10-CONTROL-PURPOSE']),
    match('A2:2.1', 'IT-10.1', 12, 'Match each physical control to its main purpose.',
          [('Bollards', 'Stop vehicles reaching the building'), ('Motion sensor', 'Detect movement out of hours'),
           ('Cable lock', 'Stop a laptop being carried away'), ('Magnetometer', 'Screen people for metal objects'),
           ('Access control vestibule', 'Stop tailgating at an entrance')],
          'A+ Core 2 2.1 physical security measures.', decoys=['Encrypt data at rest']),
    single('A2:2.1', 'IT-10.1', 13, 'Which sign-in combination is true multifactor authentication?',
           'A password and a code from an authenticator app', ['A password and a security question', 'A password and a PIN',
            'Two different passwords'],
           'MFA combines different factor types: a password (know) and an app on the phone (have).',
           mc=['MC-C-IT10-MFA-SAME-FACTOR', 'MC-C-IT10-MFA-SAME-FACTOR', 'MC-C-IT10-MFA-SAME-FACTOR']),
    single('A2:2.1', 'IT-10.1', 14, 'Administrators should hold domain admin rights only while doing an approved task, with every use logged. What provides this?',
           'Just-in-time access through privileged access management (PAM)',
           ['Permanent domain admin membership for each administrator', 'A single shared admin account in a password vault',
            'Single sign-on for all administrators'],
           'PAM grants time-limited privileged access on request and logs it.',
           mc=['MC-C-IT10-STANDING-ADMIN', 'MC-C-IT10-STANDING-ADMIN', None]),
    multi('A2:2.1', 'IT-10.1', 15, 'Which TWO MFA methods resist phishing and SIM swapping best? (Choose two.)',
          ['A FIDO2 hardware security key', 'A passkey (FIDO2 / WebAuthn credential)'],
          ['A code sent by SMS', 'A one-time code read out in a voice call', 'An emailed sign-in code'],
          'FIDO2 keys and passkeys are bound to the real site; SMS, voice and email codes can be phished or redirected (NIST SP 800-63B).',
          mc=['MC-C-IT10-SMS-STRONG', 'MC-C-IT10-SMS-STRONG', None]),
]
