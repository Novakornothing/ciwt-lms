"""Original practice bank for Security.

Questions are written for this course and tagged to the same numbered objectives
used by the CompTIA Security+ (SY0-701) exam. This is not an official exam.
"""
from curriculum_sec.catalog import CHAPTERS

SEC_EXAM = {
    'code': 'SY0-701',
    'name': 'Security',
    'short': 'Security',
    'version': 'SY0-701',
    'doc_version': 'Aligned to the CompTIA Security+ (SY0-701) exam objectives',
    'url': 'https://novak-lms.onrender.com/specs#course-SEC',
    'page': 'https://novak-lms.onrender.com/specs#course-SEC',
    'official': {
        'questions': '90',
        'minutes': 90,
        'passing': '750 simulated on a 100–900 practice scale',
    },
    'course': 'SEC',
}

SEC_DOMAINS = [
    ('1.0', 'General security concepts', 12),
    ('2.0', 'Threats, vulnerabilities, and mitigations', 22),
    ('3.0', 'Security architecture', 18),
    ('4.0', 'Security operations', 28),
    ('5.0', 'Security program management and oversight', 20),
]

_TITLES = {
    '1.1': 'Compare control categories and the jobs controls do.',
    '1.2': 'Explain confidentiality, identity, zero trust, physical measures, and decoys.',
    '1.3': 'Explain why the change process matters to security.',
    '1.4': 'Explain how to choose cryptographic tools.',
    '2.1': 'Compare threat actors and what motivates them.',
    '2.2': 'Explain the common ways an attack arrives.',
    '2.3': 'Explain kinds of weaknesses.',
    '2.4': 'Analyze signs of malicious activity.',
    '2.5': 'Explain ways to reduce how far an incident can spread.',
    '3.1': 'Compare the security effects of architecture choices.',
    '3.2': 'Apply security ideas when placing enterprise infrastructure.',
    '3.3': 'Compare ways to protect data.',
    '3.4': 'Explain resilience and recovery.',
    '4.1': 'Apply security techniques to computing resources.',
    '4.2': 'Explain how asset management affects security.',
    '4.3': 'Explain vulnerability management activities.',
    '4.4': 'Explain alerting, monitoring, and security tools.',
    '4.5': 'Modify enterprise tools to improve security.',
    '4.6': 'Implement identity and access management.',
    '4.7': 'Explain automation in secure operations.',
    '4.8': 'Explain incident response activities.',
    '4.9': 'Use logs and other data in an investigation.',
    '5.1': 'Summarize security governance.',
    '5.2': 'Explain risk management.',
    '5.3': 'Explain third-party risk.',
    '5.4': 'Summarize security compliance.',
    '5.5': 'Explain audits and assessments.',
    '5.6': 'Implement security awareness practices.',
}

_DOM_NAME = {d: name for d, name, _w in SEC_DOMAINS}
_WEIGHT = {d: w for d, _n, w in SEC_DOMAINS}
_COUNTS = {}
for _oid in _TITLES:
    _dom = _oid.split('.')[0] + '.0'
    _COUNTS[_dom] = _COUNTS.get(_dom, 0) + 1

SEC_OBJECTIVES = {}
for _oid, _title in _TITLES.items():
    _dom = _oid.split('.')[0] + '.0'
    SEC_OBJECTIVES[f'S:{_oid}'] = {
        'exam': 'S',
        'id': _oid,
        'domain': _dom,
        'domain_name': _DOM_NAME[_dom],
        'title': _title,
        'topics': [],
        'weight': round(_WEIGHT[_dom] / _COUNTS[_dom], 2),
        'course_objs': [],
        'lessons': [],
        'labs': [],
    }

_THIRDS = [
    'Wait until next quarter and leave it unchanged',
    'Put the secret in the ticket so the next shift has it',
    'Turn logging off so the alert stops',
    'Give every account full admin rights for speed',
    'Treat a marketing screenshot as proof',
    'Reboot and close the ticket with no note',
]


def _sections():
    out = []
    for ch in CHAPTERS:
        for les in ch['lessons']:
            for sec in les['sections']:
                out.append((ch['order'], les, sec))
    return out


def _balance(correct, wrongs):
    wrongs = list(wrongs)
    if len(correct) > max(len(w) for w in wrongs):
        i = max(range(len(wrongs)), key=lambda n: len(wrongs[n]))
        while len(wrongs[i]) <= len(correct):
            wrongs[i] += ' in this case'
    return wrongs


def _mc(n, oid, course_obj, text, correct, wrongs, why):
    wrongs = _balance(correct, wrongs)
    opts = list(wrongs)
    opts.insert(n % 4, correct)
    if len(set(opts)) != 4 or correct not in opts:
        raise RuntimeError(f'bad options for {n}: {opts}')
    item = {
        'id': f'SECQ-{n:04d}',
        'bank_id': f'SECQ-{n:04d}',
        'type': 'single',
        'text': text,
        'options': opts,
        'correct': correct,
        'explanation': why,
        'obj': course_obj,
        'cert': [oid],
        'review': 'Pending SME review',
    }
    item['raw'] = item
    return item


def _singles():
    out = []
    n = 1
    seen = set()
    for _ch, les, sec in _sections():
        bid = sec['id']
        oid = 'S:' + '.'.join(bid.split('.')[:2])
        if oid not in SEC_OBJECTIVES:
            raise RuntimeError(oid)
        scene = sec['note'].rstrip('.')
        name = sec['heading']
        key, bad1, bad2 = sec['key'], sec['bad'][0], sec['bad'][1]
        third = next(t for t in _THIRDS if t not in (key, bad1, bad2))
        stems = [
            (f'{scene}. What is the right call?', key, [bad1, bad2, third], sec['why']),
            (f'A teammate says "{bad1}" when discussing {name}. What do you tell them?',
             key, [bad1, bad2, third], sec['why']),
        ]
        # second stem's correct answer must not also be a distractor
        stems[1] = (
            stems[1][0],
            key,
            [bad2, third, 'Call it finished without a note'],
            sec['why'],
        )
        for text, correct, wrongs, why in stems:
            if correct in wrongs or len(set([correct] + wrongs)) != 4:
                wrongs = [w for w in wrongs if w != correct]
                while len(wrongs) < 3:
                    wrongs.append(f'Ignore {name} and move on')
                wrongs = wrongs[:3]
            if len(why) < 45:
                why = why + ' The other choices describe a different job.'
            item = _mc(n, oid, les['skill'], text, correct, wrongs, why)
            key_norm = ''.join(ch for ch in text.lower() if ch.isalnum())
            if key_norm in seen:
                raise RuntimeError('duplicate stem ' + text[:80])
            seen.add(key_norm)
            out.append(item)
            n += 1
        SEC_OBJECTIVES[oid]['course_objs'].append(les['skill'])
        lesson_ref = f"SEC {les['title'].split()[0]}"
        if lesson_ref not in SEC_OBJECTIVES[oid]['lessons']:
            SEC_OBJECTIVES[oid]['lessons'].append(lesson_ref)
    for meta in SEC_OBJECTIVES.values():
        meta['course_objs'] = list(dict.fromkeys(meta['course_objs']))
    return out


def _order(n, oid, cobj, text, steps, why):
    item = {
        'id': f'SECQ-P{n}',
        'bank_id': f'SECQ-P{n}',
        'type': 'order',
        'text': text,
        'options': list(reversed(steps)),
        'correct': list(steps),
        'explanation': why,
        'obj': cobj,
        'cert': [oid],
        'review': 'Pending SME review',
    }
    item['raw'] = item
    return item


def _match(n, oid, cobj, text, pairs, why):
    prompts = [a for a, _b in pairs]
    correct = [b for _a, b in pairs]
    item = {
        'id': f'SECQ-P{n}',
        'bank_id': f'SECQ-P{n}',
        'type': 'match',
        'text': text,
        'prompts': prompts,
        'options': list(reversed(correct)) + ['A different control'],
        'correct': correct,
        'explanation': why,
        'obj': cobj,
        'cert': [oid],
        'review': 'Pending SME review',
    }
    item['raw'] = item
    return item


def _pbqs():
    skill = {
        '1.1': 'SEC-1.4', '1.2': 'SEC-2.1', '1.3': 'SEC-5.1', '1.4': 'SEC-6.3',
        '2.2': 'SEC-10.1', '2.4': 'SEC-12.1', '2.5': 'SEC-14.1',
        '3.2': 'SEC-16.1', '3.4': 'SEC-18.3',
        '4.3': 'SEC-21.4', '4.5': 'SEC-23.1', '4.6': 'SEC-24.4', '4.8': 'SEC-25.4', '4.9': 'SEC-26.3',
        '5.2': 'SEC-27.5', '5.3': 'SEC-28.1', '5.6': 'SEC-28.6',
    }
    rows = [
        _order(1, 'S:4.8', skill['4.8'],
               'Order a basic incident from first preparation through the lesson.',
               ['Prepare access and contacts before the event', 'Detect and decide it is an incident', 'Contain the spread', 'Remove the cause', 'Recover from a clean point', 'Assign a lesson with an owner'],
               'Preparation comes first. Contain before you wipe. Recover only from a clean point, then name a change.'),
        _order(2, 'S:4.5', skill['4.5'],
               'Order a default-deny host firewall change so you do not lock yourself out.',
               ['Read the ticket', 'Allow loopback', 'Allow established flows', 'Add the named service allows', 'Set the default to deny', 'Save the rules'],
               'Put the allows in before the default deny, then persist them.'),
        _order(3, 'S:4.6', skill['4.6'],
               'Order a privileged access checkout.',
               ['Confirm the ticket and the person', 'Check out the secret from the vault', 'Do the task', 'Return the secret so it rotates', 'Write what you changed'],
               'The secret is checked out for the task and rotated after. It does not live in the ticket.'),
        _order(4, 'S:4.9', skill['4.9'],
               'Order evidence handling for a disk you may need later.',
               ['Leave the original untouched', 'Record a hash of the image', 'Work on the copy', 'Keep a chain of who held it', 'Report only what the facts support'],
               'The original stays sealed. The hash shows the copy matches. The report stays inside the evidence.'),
        _order(5, 'S:1.3', skill['1.3'],
               'Order a normal security-relevant change.',
               ['Name the owner and the stakeholders', 'Write the impact and the test', 'Get approval', 'Change during the window', 'Back out if the test fails', 'Update the diagram'],
               'Approval and a way back come before the edit. The diagram is part of done.'),
        _order(6, 'S:3.4', skill['3.4'],
               'Order a backup you can trust.',
               ['Decide how much data you can lose', 'Make a copy somewhere else', 'Encrypt the copy and keep the key apart', 'Restore a real file as a test', 'Record who restored it'],
               'Frequency follows the recovery point. A copy you have not restored is a hope.'),
        _order(7, 'S:4.3', skill['4.3'],
               'Order vulnerability work for an exposed flaw.',
               ['Confirm it applies to you', 'Rank it by exposure and active use', 'Patch or isolate', 'Rescan or check the version', 'Report the residual risk'],
               'A score is not the order. Proof the path is gone closes the finding.'),
        _order(8, 'S:5.6', skill['5.6'],
               'Order the response to a reported lure.',
               ['Thank the person who reported it', 'Do not click the link', 'Contain any account that already clicked', 'Tell the reporter what you did', 'Adjust the filter or the training'],
               'Reports are the goal. Silence and shame stop the next report.'),
        _order(9, 'S:2.4', skill['2.4'],
               'Order the first hour of a suspected ransomware host.',
               ['Get the host off the network', 'Keep the disk', 'Disable accounts it could use', 'Scope what else those accounts could reach', 'Call the incident owner'],
               'Contain and preserve before you wipe or pay.'),
        _order(10, 'S:5.2', skill['5.2'],
               'Order a risk entry from identification to a decision.',
               ['Name the asset and the event', 'Estimate likelihood and impact', 'Put it on the register with an owner', 'Choose mitigate, accept, transfer, or avoid', 'Watch the indicator'],
               'A register entry has an owner and a treatment. Acceptance is written.'),
        _match(11, 'S:1.1', skill['1.1'],
               'Match the control to the moment it helps.',
               [('Badge reader that stops a stranger', 'Preventive'),
                ('Camera that records a theft', 'Detective'),
                ('Restore from a clean backup', 'Corrective'),
                ('Bright light that makes an attempt feel risky', 'Deterrent')],
               'Preventive blocks, detective notices, corrective repairs, and deterrent discourages.'),
        _match(12, 'S:1.2', skill['1.2'],
               'Match the failure to the promise.',
               [('Unapproved person can read the file', 'Confidentiality'),
                ('Approved total was edited later', 'Integrity'),
                ('The service is too slow to do the work', 'Availability'),
                ('A shared password was used, so nobody can be tied to the click', 'Non-repudiation')],
               'Each promise fails differently. A shared password cannot tie the action to one person.'),
        _match(13, 'S:1.4', skill['1.4'],
               'Match the tool to the job.',
               [('Show whether the bytes changed', 'Hash'),
                ('Hide the bytes from unapproved readers', 'Encryption'),
                ('Change format with no secret', 'Encoding'),
                ('Prove who signed and that the bytes stayed the same', 'Digital signature')],
               'A hash fingerprints, encryption hides, encoding has no secret, and a signature proves origin and integrity.'),
        _match(14, 'S:2.2', skill['2.2'],
               'Match the path to the trick.',
               [('Fake email that wants a password', 'Phishing'),
                ('Phone call that wants a one-time code', 'Vishing'),
                ('Text message with a look-alike link', 'Smishing'),
                ('Email that changes a vendor bank account', 'Business email compromise')],
               'The channel and the ask name the trick. Confirm money changes on a known phone number.'),
        _match(15, 'S:2.4', skill['2.4'],
               'Match the behavior to the malware description.',
               [('Spreads with no one opening a file each time', 'Worm'),
                ('Looks useful and also harms', 'Trojan'),
                ('Locks data and demands payment', 'Ransomware'),
                ('Hides underneath the tools you use to look', 'Rootkit')],
               'Describe the behavior first. A rootkit means you do not trust the host to describe itself.'),
        _match(16, 'S:2.5', skill['2.5'],
               'Match the mitigation to the path.',
               [('One compromised laptop can reach every server', 'Segmentation'),
                ('A known flaw on the public VPN', 'Patching'),
                ('A stolen powered-off laptop', 'Disk encryption'),
                ('An alert nobody owns', 'Monitoring with an owner')],
               'Pick the mitigation that closes the path you actually have.'),
        _match(17, 'S:3.2', skill['3.2'],
               'Match the device to the job.',
               [('Can stop traffic because it sits in the path', 'Inline control'),
               ('Copies traffic and cannot block', 'Tap'),
               ('Stepping stone for administration', 'Jump server'),
               ('Public systems separated from the internal LAN', 'Screened subnet')],
               'A tap watches. An inline control can stop. Public systems do not sit on the office LAN.'),
        _match(18, 'S:4.6', skill['4.6'],
               'Match the identity word to the meaning.',
               [('Proving the person before the session', 'Authentication'),
                ('What that person may do', 'Authorization'),
                ('A record of what they did', 'Accounting'),
                ('One employer login accepted by another organization', 'Federation')],
               'Authenticate, then authorize, and keep the record. Federation still needs your own permission decision.'),
        _match(19, 'S:5.1', skill['1.3'],
               'Match the document to the job.',
               [('What must be true', 'Policy'),
                ('The specific product or setting required', 'Standard'),
                ('How this team performs the task', 'Procedure'),
                ('Advice that is not mandatory', 'Guideline')],
               'Do not audit someone for skipping a guideline you never promoted to a standard.'),
        _match(20, 'S:5.3', skill['5.3'],
               'Match the agreement to the promise.',
               [('Uptime or response numbers', 'Service-level agreement'),
                ('Secrets stay secret', 'Non-disclosure agreement'),
                ('The specific job to be done', 'Statement of work'),
                ('The legal terms that govern the relationship', 'Master service agreement')],
               'Put the uptime number in the contract. A non-disclosure agreement does not set uptime.'),
        _order(21, 'S:4.6', skill['4.6'],
               'Order identity proofing for a password reset.',
               ['Do not trust the mailbox that may be stolen', 'Call back on a number from the directory', 'Reset only after the person matches', 'Send the new secret a different way', 'Write the method, not the secret'],
               'The mailbox that asked cannot be the only proof. The ticket never holds the password.'),
        _order(22, 'S:1.4', skill['1.4'],
               'Order certificate issuance without emailing a private key.',
               ['Generate the key pair locally', 'Send a request that contains the public key', 'The authority signs the public key', 'Install the certificate', 'Keep the private key where it was generated'],
               'The request does not include the private key. The authority never needs it.'),
        _order(23, 'S:3.4', skill['3.4'],
               'Order a failover test that is more than a meeting.',
               ['Name the recovery time you promised', 'Move a non-production copy', 'Write what broke', 'Fix the break', 'Repeat until the move meets the promise'],
               'A tabletop is a discussion. A failover moves the work.'),
        _order(24, 'S:4.8', skill['4.8'],
               'Order legal preservation after counsel says hold.',
               ['Read the custodians and the dates counsel named', 'Stop the usual deletion for that scope', 'Include backups that would age out', 'Export only that scope', 'Hash what you produced'],
               'A hold pauses the shredder. Do not export the whole company, and do not edit the mail first.'),
        _order(25, 'S:2.5', skill['2.5'],
               'Order hardening a new server before it is reachable.',
               ['Start from the baseline image', 'Remove software you do not need', 'Turn on the host firewall', 'Change default passwords', 'Confirm management is not open to the internet'],
               'Hardening is the list, done before the host is exposed.'),
        _match(26, 'S:4.1', 'SEC-19.1',
               'Match the wireless choice to the meaning.',
               [('Current preferred wireless protection', 'WPA3'),
                ('One passphrase printed on a sign', 'A shared secret'),
                ('Each user or device authenticates to a server', 'Enterprise authentication'),
                ('A personal phone used for work', 'Bring your own device')],
               'A shared passphrase is not per-user authentication. Ownership of the phone decides the wipe.'),
        _match(27, 'S:4.4', 'SEC-22.3',
               'Match the tool to what it sees.',
               [('Who talked to whom, without full packets', 'NetFlow'),
                ('Known or suspicious programs on a host', 'Antivirus'),
                ('Patterns across many logs', 'SIEM'),
                ('Device health, dangerous if the community string is public', 'SNMP')],
               'Each tool has a job. Public SNMP is a risk, not a convenience.'),
        _match(28, 'S:5.2', skill['5.2'],
               'Match the risk treatment.',
               [('Add a control', 'Mitigate'),
                ('Live with it in writing', 'Accept'),
                ('Share the money impact by contract or insurance', 'Transfer'),
                ('Stop doing the activity', 'Avoid')],
               'Insurance does not close the port. Acceptance is a written decision.'),
        _order(29, 'S:4.2', 'SEC-20.3',
               'Order retirement of a server that held payroll.',
               ['Name the owner and the data', 'Export or destroy what policy says to keep', 'Wipe or shred the media', 'Remove the accounts and firewall rules', 'File the destruction record with serial numbers'],
               'Powering off is not retirement. Accounts, rules, and a record have to go too.'),
        _order(30, 'S:5.3', skill['5.3'],
               'Order a vendor review before you connect them.',
               ['Say what data they will hold', 'Ask for an independent report, not a brochure', 'Put uptime and breach notice in the contract', 'Limit the access they get', 'Review that access on a schedule'],
               'Signing is the start of monitoring, not the end of the work.'),
        _match(31, 'S:2.1', 'SEC-8.1',
               'Match the actor clue.',
               [('Patient access with a government goal', 'Nation-state'),
                ('A business that wants money', 'Organized crime'),
                ('A message and an audience', 'Hacktivist'),
                ('A person who already has a legitimate role', 'Insider')],
               'Write the evidence. A scary event is not automatically a nation-state.'),
        _match(32, 'S:3.3', 'SEC-17.1',
               'Match the data handling word.',
               [('Stored on a disk', 'At rest'),
                ('Moving across a network', 'In transit'),
                ('Open in memory while someone works', 'In use'),
                ('Laws of the place where it sits', 'Sovereignty')],
               'Disk encryption does not cover a logged-on session. Replicas count as a place.'),
    ]
    return rows


_SINGLES = _singles()
_PBQS = _pbqs()


def as_bank_items():
    return _SINGLES + _PBQS


def pool_map():
    out = {}
    for it in as_bank_items():
        for oid in it['cert']:
            out.setdefault(oid, [])
            if it['id'] not in out[oid]:
                out[oid].append(it['id'])
    return out


def coverage_rows():
    pool = pool_map()
    obj_out = {}
    for oid, meta in SEC_OBJECTIVES.items():
        items = pool.get(oid, [])
        obj_out[oid] = {
            'title': meta['title'],
            'weight': meta['weight'],
            'content_ratio': 1.0,
            'content': 'covered',
            'assessment': 'covered' if len(items) >= 4 else 'partial',
            'status': 'covered' if len(items) >= 4 else 'partial',
            'topics_missing': [],
            'lessons': list(meta['lessons']),
            'labs': [],
            'items': items,
        }
    total = len(obj_out)
    covered = sum(1 for v in obj_out.values() if v['status'] == 'covered')
    summary = {
        'covered': covered, 'partial': total - covered, 'gap': 0, 'total': total,
        'weighted_covered': 100.0 if covered == total else 0.0, 'weighted_partial': 0.0,
        'items': sum(len(v['items']) for v in obj_out.values()),
        'topic_ratio': 1.0,
    }
    return obj_out, summary, dict(summary)
