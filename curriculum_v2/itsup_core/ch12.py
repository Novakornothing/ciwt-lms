"""ITSUP Chapter 12 — Operational Procedures & Capstone Habits (pass 9 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 12
SOURCES_USED = ['cisa-backup']

LESSONS = {
    (12, 1): {
        'objectives': [
            'Classify a change as standard, normal or emergency and identify the approval each needs',
            'Write a change request with scope, risk and impact, test plan, implementation steps, backout plan, schedule and communication',
            'Use a checklist during implementation and complete a post-implementation review',
        ],
        'html': sme_note() + '''
<h3>Why change control exists</h3>
<p>Most outages are caused by changes — an update, a new rule, a replaced cable, a “quick” setting. Change management does not
stop changes; it makes them predictable: someone has thought about what could break, the people affected know when, and there
is a tested way back. Support technicians make changes every day, so knowing which ones need approval is part of the job.</p>
''' + table(['Change type', 'Meaning', 'Approval', 'Example'], [
            ['Standard', 'Low-risk, repeatable, with a documented procedure that has been approved in advance', 'Pre-approved; log it', 'Replacing a keyboard; adding a user to a printer group from the request catalogue'],
            ['Normal', 'Anything else that is planned', 'Assessed and approved before it is done — by a manager or a change advisory board (CAB) depending on risk', 'Moving a shared printer to a new address; changing a Group Policy setting'],
            ['Emergency', 'Needed now to restore service or close a serious security risk', 'Expedited approval by a named authority; full review afterwards', 'Blocking a malicious sender domain during a phishing outbreak'],
        ]) + '''
<h3>What a change request contains</h3>
<ol>
<li><strong>Purpose and scope</strong> — what changes, on which systems, for whom.</li>
<li><strong>Risk and impact</strong> — what could go wrong, how many users notice during and after.</li>
<li><strong>Test plan</strong> — where it was tried first (lab VM, pilot group) and how success is measured.</li>
<li><strong>Implementation steps</strong> — numbered, specific, in order.</li>
<li><strong>Backout (rollback) plan</strong> — the steps to undo it, and the point at which you will use them.</li>
<li><strong>Schedule</strong> — the maintenance window, chosen to minimise impact.</li>
<li><strong>Communication</strong> — who is told, when and how; who to call if something goes wrong.</li>
<li><strong>Approvals</strong> — who approved it and when.</li>
</ol>
''' + figure('f12-1', 'Change lifecycle', ['Request', 'Assess risk\n+ impact', 'Approve', 'Implement\nwith checklist', 'Verify or\nback out', 'Review +\nclose'],
             'Six boxes in order: Request; Assess risk and impact; Approve; Implement with a checklist during the maintenance window; '
             'Verify the result or back out using the rollback plan; Review and close, recording what happened and any lessons.',
             'Every normal change passes through assessment and approval before implementation, and ends with verification and review.', cols=3) + worked('a change request for moving a printer', '''
<p><strong>Purpose:</strong> move the second-floor printer from 10.2.0.40 to reserved address 10.2.0.60 to remove an address
conflict. <strong>Scope:</strong> one printer, one print-server queue, 34 users. <strong>Risk:</strong> printing fails if the queue
port is not updated; low impact outside the window. <strong>Test:</strong> new port created on a test queue and a page printed.
<strong>Steps:</strong> 1 reserve .60 in DHCP; 2 set the printer to DHCP and restart it; 3 confirm .60 on its status page; 4 update the
queue port; 5 print from two user PCs. <strong>Backout:</strong> set the printer back to static .40 and restore the old port (5
minutes) if step 5 fails. <strong>Window:</strong> Tuesday 07:30–08:00. <strong>Communication:</strong> email to floor 2 the day
before; ticket number on the printer. <strong>Approval:</strong> team lead, Monday.</p>''') + cfu(
            ('Is adding a user to a printer group from the request catalogue a normal change?',
             'No — it is a standard change: pre-approved, low risk, with a documented procedure.'),
            ('What is a backout plan, and when do you decide to use it?',
             'The tested steps to undo the change; the trigger point (for example, “if step 5 fails”) is written in the plan.'),
            ('Who reviews an emergency change?',
             'It is approved quickly by a named authority and then fully reviewed after the event.')),
    },
    (12, 2): {
        'objectives': [
            'Identify personal and regulated data (student records, health, payment card data) and apply the minimum-access rule during support',
            'Apply acceptable-use, licensing and BYOD policies when a user asks for something the policy does not allow',
            'Respond professionally when you encounter sensitive or inappropriate content during support, following the reporting procedure',
        ],
        'html': sme_note() + '''
<h3>Personal and regulated data</h3>
<p><strong>Personally identifiable information (PII)</strong> is information that identifies a person: name with student ID,
home address, date of birth, ID numbers, photos. Some data is also protected by law or contract — for example, in the United
States, FERPA protects student education records and HIPAA protects health information held by covered organisations; in the
EU and UK, GDPR covers personal data generally; card payment data falls under the PCI DSS industry standard. Your institution’s
policy tells you which apply and how; when in doubt, ask the data owner or the privacy office.</p>
<p>The rule for support work is <strong>minimum access</strong>: open only what the task needs, for as long as it needs, and record
only what the next technician needs. A ticket that says “cannot open grade spreadsheet” is better than a ticket with a
screenshot of the grades.</p>
''' + table(['Situation', 'Do', 'Do not'], [
            ['Remote session on a PC showing student records', 'Ask the user to close or minimise it; work only in the app with the fault', 'Screenshot it for the ticket'],
            ['User sends a spreadsheet of personal data “so you can see the error”', 'Ask for the exact error text or a test file instead; delete the copy securely if you received it', 'Store it in the ticket or your downloads'],
            ['Request to look up a colleague’s details', 'Decline: access is for job need only', 'Look it up “just this once”'],
            ['Laptop with health data reported lost', 'Report immediately as a security incident; record encryption status', 'Wait to see if it turns up'],
        ]) + '''
<h3>Acceptable use, licensing and BYOD</h3>
<ul>
<li><strong>Acceptable-use policy (AUP)</strong> — what users may and may not do with institutional systems. When a request breaks
it (installing a game on a lab PC, sharing an account), say so politely, point to the policy and offer the legitimate route.</li>
<li><strong>Licensing</strong> — software is used under licence terms: per user, per device, per concurrent seat, site or subscription.
Installing a copy without a licence, or a personal licence on an institutional machine, can breach the terms. Use the software
portal or request process.</li>
<li><strong>Bring your own device (BYOD)</strong> — personal phones and laptops may access some services under conditions (MDM
enrolment, app protection, minimum OS version). Support helps with access to institutional services; it does not repair or
take responsibility for personal devices beyond what the policy says.</li>
</ul>
<h3>When you see something you should not have</h3>
<p>Technicians sometimes encounter content that suggests a policy breach, a crime or a risk to someone’s safety. Do not
investigate, copy or discuss it. Stop the work if appropriate, record only the facts (time, device, what you saw, who you told),
and report through the procedure your institution names (manager, security, safeguarding or HR). Professional conduct also
means not discussing users’ data or problems with others, even when the story is interesting.</p>
''' + scenario('the helpful screenshot', '''
<p>To show a formatting bug, a technician attached a screenshot of a gradebook to a ticket that 40 support staff could read. The
screenshot contained 30 students’ names and grades. It was a privacy incident: the ticket attachment had to be removed, the privacy
office informed, and the team trained. A cropped screenshot of the column headers — or the exact error text — would have shown
the bug without any personal data.</p>''') + cfu(
            ('What is the minimum-access rule?',
             'Open only what the task needs, for as long as it needs, and record only what the next technician needs.'),
            ('A user asks you to install a personal copy of software on a lab PC. What do you do?',
             'Decline under the licensing/acceptable-use policy and direct them to the software request process.'),
            ('You find content that may indicate a crime. Name two things you must not do.',
             'Investigate or copy it, or discuss it with others; record facts and report through the named procedure.')),
    },
    (12, 3): {
        'sources': ['cisa-backup'],
        'objectives': [
            'Apply the 3-2-1 backup rule and explain why RAID, snapshots and file sync are not backups on their own',
            'Compare full, incremental and differential backups by backup time, storage and what a restore needs',
            'Evaluate a backup plan against its recovery point objective (RPO) and recovery time objective (RTO)',
            'Verify a backup by restoring a file and recording the result',
        ],
        'html': sme_note() + '''
<h3>The 3-2-1 rule</h3>
<p>CISA’s guidance for organisations is the <strong>3-2-1 rule</strong>: keep three copies of important data (the original and two
backups), on two different kinds of storage, with one copy off-site. Back up automatically and regularly, protect backups (an
offline or immutable copy cannot be encrypted by ransomware that reaches the network) and test restores.</p>
''' + table(['Not a backup on its own', 'Why'], [
            ['RAID', 'It keeps a disk failure from stopping the system; deletions, corruption and ransomware are written to every disk at once'],
            ['VM snapshot', 'It lives on the same storage as the VM and is meant for short-term rollback; lose the storage and you lose both'],
            ['File sync (OneDrive, Google Drive, Dropbox)', 'Deletions and encrypted files sync too; version history and recycle bins help but have limits and are not a separate copy you control'],
        ]) + '''
<h3>Full, incremental and differential</h3>
''' + table(['Type', 'Copies', 'Backup time and space', 'To restore you need'], [
            ['Full', 'Everything selected', 'Longest; most space', 'The one full backup'],
            ['Incremental', 'Changes since the last backup of any type', 'Shortest; least space', 'The last full backup plus every incremental since'],
            ['Differential', 'Changes since the last full backup', 'Grows each day until the next full', 'The last full backup plus the latest differential'],
        ]) + figure('f12-3', 'Restoring from a full + incremental chain', ['Sunday\nfull', 'Mon\nincremental', 'Tue\nincremental', 'Wed\nincremental', 'Restore\nWednesday'],
                    'Five boxes in a row: a full backup on Sunday, then incremental backups on Monday, Tuesday and Wednesday, then a restore of '
                    'Wednesday’s state. Restoring Wednesday needs the Sunday full backup and all three incrementals in order; losing Tuesday’s '
                    'incremental breaks the chain. With differential backups the same restore would need only Sunday’s full and Wednesday’s '
                    'differential.', 'An incremental chain is only as strong as its weakest link; differentials trade larger backups for simpler restores.', cols=5) + '''
<h3>RPO and RTO</h3>
<p>The <strong>recovery point objective (RPO)</strong> is how much data, measured in time, the business can afford to lose — a
nightly backup gives an RPO of up to 24 hours. The <strong>recovery time objective (RTO)</strong> is how long the service can be
unavailable while you restore it. The data owner sets both; the backup plan has to meet them. A plan that backs up nightly cannot
meet a one-hour RPO, however reliable it is.</p>
<h3>A backup you have not restored is a hope</h3>
<p>Verify backups by restoring something: pick a file, restore it to a different location, open it, compare its date and size, and
record the test. Organisations also test full restores and keep enough history to roll back past an infection that went unnoticed
for days. On a single PC, Windows Backup, File History or a Mac’s Time Machine can be tested the same way.</p>
''' + worked('judging a backup plan', '''
<p>A department’s shared drive has a nightly full backup to a NAS in the same room; no other copy. Requirements from the data owner:
RPO 4 hours, RTO 1 day. Assessment: the RPO is not met (up to 24 hours of loss); the 3-2-1 rule is not met (one backup, same site,
same building risk); restores have never been tested. Recommendation: add snapshots or backups every 4 hours, an off-site or cloud
copy with immutability, and a monthly restore test recorded in the change log.</p>''') + cfu(
            ('Why is RAID 1 not a backup?',
             'A deletion, corruption or ransomware encryption is written to both disks at once.'),
            ('Which restore needs the most backup sets: incremental or differential?',
             'Incremental — the last full plus every incremental since.'),
            ('Backups run nightly. Can they meet a 1-hour RPO?',
             'No — up to 24 hours of data could be lost.')),
    },
    (12, 4): {
        'objectives': [
            'Write a knowledge-base article with symptom, cause, resolution, scope and keywords that a first-line technician can follow',
            'Update an asset record (tag, serial, owner, location, status, warranty) after a repair, move or disposal',
            'Apply change control, privacy, backup and documentation together in one end-to-end ticket',
        ],
        'html': sme_note('Documentation standards and integrated capstone added in pass 9 (objective IT-12.4).') + '''
<h3>Documentation that saves the next technician</h3>
<p>Good documentation turns one person’s fix into the team’s knowledge. Three kinds matter most for support:</p>
''' + table(['Document', 'Purpose', 'Must contain'], [
            ['Knowledge-base (KB) article', 'Lets anyone fix a known problem the same way', 'Title in the user’s words, symptom and error text, applies to (OS, app, version), cause, step-by-step resolution, how to verify, when to escalate, keywords, owner and review date'],
            ['Runbook / standard procedure', 'Describes a routine task done the same way every time', 'Purpose, prerequisites and permissions, numbered steps, expected results, rollback, who to contact'],
            ['Asset record', 'Tracks each device through its life', 'Asset tag, serial number, model, owner or location, status (in use, in repair, spare, disposed), purchase and warranty dates, linked tickets and changes'],
        ]) + worked('a KB article from a resolved ticket', '''
<p><strong>Title:</strong> “Login takes several minutes; stuck on ‘Applying user settings’”.
<strong>Applies to:</strong> Windows 11 domain PCs, Staff OU. <strong>Symptom:</strong> sign-in pauses for 4–6 minutes at
“Applying user settings”. <strong>Cause:</strong> a logon script maps a drive to a retired server. <strong>Resolution (tier 1):</strong>
1 confirm with gpresult /h that the Staff logon script runs; 2 test the mapped server with Test-NetConnection … -Port 445; 3 if it
fails, link the ticket to problem PRB-118 and tell the user a fix is in progress — do not edit the script. <strong>Verify:</strong>
sign-in under 1 minute after the policy owner’s change. <strong>Escalate:</strong> to the endpoint team if the server responds and
the delay persists. <strong>Keywords:</strong> slow logon, drive map, S: drive. <strong>Owner / review:</strong> Endpoint team,
every 6 months.</p>''') + '''
<h3>Integrated capstone</h3>
<p>The capstone ticket: “Replace the reception PC. It is slow and out of warranty. The new PC must print to the front-desk printer
and keep the receptionist’s files.” Score yourself against all four habits:</p>
<ol>
<li><strong>Change control:</strong> a normal change request — scope, risk, test, steps, backout (keep the old PC for a week),
window (before opening), communication, approval.</li>
<li><strong>Privacy:</strong> the old PC holds visitor logs; its drive is sanitised under the disposal procedure (Chapter 10) and the
sanitisation record is attached.</li>
<li><strong>Backup and restore:</strong> the receptionist’s files are backed up and a restore is tested on the new PC before the
old one is retired.</li>
<li><strong>Documentation:</strong> both asset records updated (new: in use, owner Reception; old: disposed, with the sanitisation
reference); a KB article updated if the printer setup had a trick.</li>
</ol>
''' + figure('f12-4', 'Capstone: replacing a reception PC', ['Change\nrequest', 'Back up +\ntest restore', 'Swap +\nverify', 'Sanitise\nold drive', 'Update assets\n+ KB'],
             'Five boxes in order: raise a change request; back up the receptionist’s files and test a restore; swap the PC and verify printing '
             'and files with the user; sanitise the old drive and attach the record; update both asset records and any knowledge-base article.',
             'Each habit from the chapter appears once in a single replacement job.', cols=5) + cfu(
            ('Name four fields of a good KB article.',
             'Any four of: title in user’s words, symptom/error text, applies to, cause, resolution steps, verification, escalation, keywords, owner and review date.'),
            ('What changes in the old PC’s asset record at the end of the capstone?',
             'Status becomes disposed, with the date and the sanitisation record reference.'),
            ('Why keep the old PC for a week in the backout plan?',
             'So the user can be switched back quickly if something on the new PC is missing or broken.')),
    },
}

GLOSSARY = [
    ('Standard change', 'A low-risk, repeatable change with a pre-approved procedure; logged but not individually approved.'),
    ('Emergency change', 'A change needed immediately to restore service or remove a serious risk; approved quickly and reviewed afterwards.'),
    ('Change advisory board (CAB)', 'The group that assesses and approves higher-risk normal changes.'),
    ('PII', 'Personally identifiable information: data that identifies a person, alone or combined with other data.'),
    ('Acceptable-use policy (AUP)', 'The rules for how users may use an organisation’s systems and data.'),
    ('BYOD', 'Bring your own device: using personal devices for work or study under the organisation’s conditions.'),
    ('3-2-1 backup rule', 'Three copies of data on two kinds of storage with one copy off-site (CISA guidance).'),
    ('Incremental backup', 'A backup of changes since the last backup of any type; restores need the full backup and every incremental since.'),
    ('Differential backup', 'A backup of changes since the last full backup; restores need the full backup and the latest differential.'),
    ('RPO / RTO', 'Recovery point objective (how much data, in time, may be lost) and recovery time objective (how long restoration may take).'),
    ('Knowledge-base (KB) article', 'A documented, reviewed procedure for a known problem, written so any technician can follow it.'),
    ('Asset record', 'The inventory entry tracking a device’s tag, serial, owner, location, status and warranty through its life.'),
]

PLAN = {
    'warmup': 'Sort ten cards (keyboard swap, GPO edit, blocking a phishing domain, printer move …) into standard, normal and emergency changes.',
    'guided': 'Write the printer-move change request together from the worked example, then judge the department backup plan against its RPO and RTO.',
    'worked_example': 'Lesson 12.1 printer-move change request; 12.3 judging a backup plan; 12.4 a KB article from a resolved ticket.',
    'cfu': ['Standard, normal or emergency: adding a user to a printer group from the catalogue?',
            'Why is RAID not a backup?',
            'Which restore needs more backup sets, incremental or differential?',
            'Name four fields of a good KB article.'],
    'exit_ticket': 'Write the asset-record updates and the privacy step for retiring the old reception PC.',
    'misconceptions_add': ['“OneDrive is my backup.” Sync copies deletions and encrypted files; version history helps but is not a separate copy you control.',
                           '“A screenshot is the clearest evidence.” It often contains personal data; use the error text or a cropped image.'],
    'classroom_lab': 'CL-12',
    'materials_add': 'KB article template and asset-record worksheet for the capstone.',
}

ITEMS = [
    item('IT-12.1', 1, 'Adding a user to a printer group through the request catalogue’s documented procedure is which kind of change?',
         'A standard change', ['An emergency change', 'A normal change for the CAB', 'A problem record'],
         'Low-risk, repeatable, pre-approved procedures are standard changes; they are logged, not individually approved.'),
    item('IT-12.1', 2, 'What is the purpose of a backout plan in a change request?',
         'To undo the change if it fails, at a stated trigger', ['To list everyone who will be told about the change and when', 'To explain why the change is needed at all', 'To record who approved the change and when'],
         'The backout plan gives tested steps to reverse the change and the condition for using them.'),
    item('IT-12.1', 3, 'A phishing outbreak needs a sender domain blocked within minutes. How is the change handled?',
         'As an emergency change, reviewed after the event', ['As a standard change with no record kept at all', 'As a normal change at next month’s CAB meeting', 'As a service request from the first victim'],
         'Emergency changes get expedited approval by a named authority and a full review afterwards.'),
    item('IT-12.2', 1, 'A user emails you a spreadsheet of student data “so you can see the error”. What should you do?',
         'Ask for the error text and securely delete the copy', ['Attach it to the ticket so the next technician can see it', 'Forward it to the vendor’s support address', 'Keep it in your downloads until the fix is done'],
         'Minimum access: avoid holding personal data; ask for the error text or a test file instead.'),
    item('IT-12.2', 2, 'A user asks you to install their personal copy of a paid app on a lab PC. What is the right response?',
         'Decline and point them to the software request process', ['Install it, since the user already owns a licence for it', 'Install it but remove it again at the end of term', 'Install a free trial so no licence is needed'],
         'Personal licences usually do not cover institutional devices; the request process handles licensed installs.'),
    item('IT-12.2', 3, 'During repair you see files suggesting a possible crime. What should you do?',
         'Stop, record the facts and report through the procedure', ['Open the files to confirm what they are before reporting', 'Copy the files to a USB stick as evidence', 'Discuss it with colleagues to get their views'],
         'Do not investigate, copy or discuss; record facts and report through the named channel.'),
    item('IT-12.3', 1, 'Why is a RAID 1 mirror not a backup?',
         'Deletions and corruption are written to both disks', ['It needs twice as much power as a single disk does', 'It only works with hard drives, not with SSDs', 'It cannot be used on a computer with a TPM'],
         'RAID protects against a disk failure, not against deletion, corruption or ransomware.'),
    item('IT-12.3', 2, 'You keep a Sunday full backup and daily incrementals. What do you need to restore Wednesday’s data?',
         'Sunday’s full and the Mon, Tue and Wed incrementals', ['Only Wednesday’s incremental backup set on its own', 'Sunday’s full and only Wednesday’s incremental', 'Only the most recent full backup set'],
         'Incrementals depend on every previous link back to the full backup.'),
    item('IT-12.3', 3, 'Backups run once a night. The data owner requires an RPO of one hour. What is true?',
         'The plan cannot meet the RPO', ['The plan meets the RPO easily', 'RPO only applies to databases', 'The RTO decides this, not RPO'],
         'A nightly schedule can lose up to 24 hours of data, far more than a one-hour RPO allows.'),
    item('IT-12.4', 1, 'Which item belongs in a knowledge-base article for a known fault?',
         'The steps to verify that the fix worked', ['The user’s password at the time of the fault', 'Screenshots that show the user’s personal files', 'The names of everyone who reported the fault'],
         'A KB article includes verification and escalation steps; secrets and personal data never belong in it.'),
    item('IT-12.4', 2, 'A laptop is sanitised and recycled. How should its asset record change?',
         'Status disposed, with date and sanitisation reference', ['Delete the record so that the asset list stays short', 'Keep it marked “in use” until the warranty ends', 'Move it to the new owner listed on the invoice'],
         'Asset records track a device through disposal; the sanitisation reference is the evidence.'),
    item('IT-12.4', 3, 'What makes a runbook usable by another technician?',
         'Numbered steps with prerequisites, results and rollback', ['A summary paragraph written from memory later on', 'A link to the vendor’s marketing web page', 'The author’s initials and the date it was first written'],
         'Runbooks need specific, ordered steps with prerequisites, expected results and a way back.'),
]
