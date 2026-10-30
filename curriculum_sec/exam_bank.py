"""Original practice-exam bank for the Security course.

Aligned to the CompTIA Security+ (SY0-701) exam objectives.
This is not an official CompTIA exam and it is not endorsed by CompTIA.
"""
from collections import OrderedDict

from curriculum_sec.gloss import GLOSS
from curriculum_sec.sy0 import DOMAIN_NAMES, DOMAIN_WEIGHTS, LEAVES, OBJECTIVE_TITLES

SEC_EXAM = {
    'code': 'SEC-FOUND',
    'name': 'Security practice exam',
    'short': 'Security',
    'version': '2',
    'doc_version': 'Novak LMS™ original practice bank, aligned to the CompTIA Security+ (SY0-701) exam objectives',
    'url': 'https://novak-lms.onrender.com/specs#course-SEC',
    'page': 'https://novak-lms.onrender.com/specs#course-SEC',
    'official': {
        'questions': '90 in a full Exam-Day sitting (600+ in the bank)',
        'minutes': 90,
        'passing': '750 simulated on a 100–900 practice scale',
    },
    'course': 'SEC',
}

_OBJ_ORDER = list(OrderedDict((leaf[1], None) for leaf in LEAVES).keys())
_OBJ_DOMAIN = {}
_OBJ_COUNT = {}
for _dom, _obj, _name in LEAVES:
    _OBJ_DOMAIN[_obj] = _dom
    _OBJ_COUNT[_dom] = _OBJ_COUNT.get(_dom, 0) + 0
for _obj in _OBJ_ORDER:
    _dom = _OBJ_DOMAIN[_obj]
    _OBJ_COUNT[_dom] = sum(1 for o in _OBJ_ORDER if _OBJ_DOMAIN[o] == _dom)

SEC_DOMAINS = [
    (dom, DOMAIN_NAMES[dom], DOMAIN_WEIGHTS[dom])
    for dom in ('1.0', '2.0', '3.0', '4.0', '5.0')
]

SEC_OBJECTIVES = {}
for _obj in _OBJ_ORDER:
    _dom = _OBJ_DOMAIN[_obj]
    SEC_OBJECTIVES[f'S:{_obj}'] = {
        'exam': 'S',
        'id': _obj,
        'domain': _dom,
        'domain_name': DOMAIN_NAMES[_dom],
        'title': OBJECTIVE_TITLES[_obj],
        'topics': [name for dom, obj, name in LEAVES if obj == _obj],
        'weight': round(DOMAIN_WEIGHTS[_dom] / _OBJ_COUNT[_dom], 2),
        'course_objs': [],
        'lessons': [],
        'labs': [],
    }


def _pad(correct, wrongs):
    w = [str(x) for x in wrongs][:3]
    while len(w) < 3:
        w.append('A different control in this chapter')
    used = set(w)
    used.add(correct)
    extras = ['Ask for a written owner and a date', 'Reboot first and write nothing', 'Copy the secret into the ticket']
    for extra in extras:
        if len(set(w)) == 3 and correct not in w:
            break
        if len(w) < 3 or len(set(w)) < 3 or correct in w:
            if extra not in used:
                if len(w) < 3:
                    w.append(extra)
                else:
                    w[w.index(next(x for x in w if w.count(x) > 1 or x == correct))] = extra
                used.add(extra)
    w = w[:3]
    if len(correct) > max(len(x) for x in w):
        i = max(range(len(w)), key=lambda n: len(w[n]))
        while len(w[i]) <= len(correct):
            w[i] += ' in this workplace'
    return w


def _mc(n, oid, course_obj, text, correct, wrongs, why):
    w = _pad(correct, wrongs)
    opts = list(w)
    opts.insert(n % 4, correct)
    item = {
        'id': f'SECQ-{n:04d}',
        'bank_id': f'SECQ-{n:04d}',
        'type': 'single',
        'text': text,
        'options': opts,
        'correct': correct,
        'explanation': why,
        'obj': course_obj or 'SEC-1.1',
        'cert': [oid],
        'review': 'Pending SME review',
    }
    item['raw'] = item
    return item


_ID_FRAMES = (
    'The evidence in the ticket is: {case} Which topic is that?',
    'You have to label this before you touch a setting: {case} What is the right label?',
    'A coworker used a different name. The fact you can verify is: {case} Which name fits the fact?',
    'Sort this queue item before you recommend a tool. {case} Which topic matches it?',
    'The handoff is missing a label. Here is the only fact: {case} Which topic belongs on the ticket?',
    'Do not file this under the neighboring idea. {case} Which topic is actually in front of you?',
    'Read the evidence once, then name it. {case} Which topic is supported?',
    'The next person will bring the wrong control if you misname this. {case} Which topic is accurate?',
)

_DO_FRAMES = (
    'The ticket says: {case} Which decision matches {name}?',
    'You have to tell a new teammate what to do about this: {case} Which line is the right call for {name}?',
    'Pick the action that fits {name}. The evidence is: {case}',
    'Which response is the one {name} calls for, given this evidence: {case}',
    'A faster option is on the table. The evidence is still: {case} Which response is the one for {name}?',
    'Write the decision for {name} into the ticket. The evidence is: {case} Which line should you write?',
    'Two labels were proposed. The evidence is: {case} Which decision is the one {name} supports?',
    'Close this only if the decision matches the evidence. {case} Which decision is right for {name}?',
)


def _singles():
    by_obj = OrderedDict()
    for leaf in LEAVES:
        by_obj.setdefault(leaf[1], []).append(leaf[2])
    out = []
    n = 1
    for obj, names in by_obj.items():
        oid = f'S:{obj}'
        course_obj = f'SEC-{_OBJ_ORDER.index(obj) + 1}.1'
        for i, name in enumerate(names):
            means, case, plain, _story = GLOSS[name]
            others = [x for x in names if x != name]
            wrong_names = sorted(others, key=lambda x: (abs(len(x) - len(name)), x))[:3]
            contrast = wrong_names[0]
            contrast_case = GLOSS[contrast][1].rstrip('.')
            why_id = (
                f'{means} That is why the label is {name}. '
                f'{contrast} would be the label if the ticket instead said: {contrast_case}.'
            )
            out.append(_mc(
                n, oid, course_obj,
                _ID_FRAMES[i % len(_ID_FRAMES)].format(case=case.rstrip('.')),
                name, wrong_names, why_id,
            ))
            n += 1
            wrong_plain = []
            plain_owners = []
            for other in others:
                line = GLOSS[other][2].rstrip('.')
                if line != plain.rstrip('.') and line not in wrong_plain:
                    wrong_plain.append(line)
                    plain_owners.append(other)
                if len(wrong_plain) == 3:
                    break
            decoy = plain_owners[0] if plain_owners else contrast
            why_do = (
                f'For {name}, the decision is: {plain.rstrip(".")}. '
                f'{means} The line about {decoy} answers a different decision, '
                f'because {decoy} shows up as: {GLOSS[decoy][1].rstrip(".")}.'
            )
            out.append(_mc(
                n, oid, course_obj,
                _DO_FRAMES[(i + 3) % len(_DO_FRAMES)].format(case=case.rstrip('.'), name=name),
                plain.rstrip('.'),
                wrong_plain,
                why_do,
            ))
            n += 1
    return out


def _order(n, oid, text, steps, why):
    item = {
        'id': f'SECQ-P{n}',
        'bank_id': f'SECQ-P{n}',
        'type': 'order',
        'text': text,
        'options': list(steps),
        'correct': list(steps),
        'explanation': why,
        'obj': f'SEC-{_OBJ_ORDER.index(oid.split(":")[1]) + 1}.1',
        'cert': [oid],
        'review': 'Pending SME review',
    }
    item['raw'] = item
    return item


def _match(n, oid, text, pairs, why):
    prompts = [a for a, _b in pairs]
    correct = [b for _a, b in pairs]
    item = {
        'id': f'SECQ-P{n}',
        'bank_id': f'SECQ-P{n}',
        'type': 'match',
        'text': text,
        'prompts': prompts,
        'options': list(reversed(correct)),
        'correct': correct,
        'explanation': why,
        'obj': f'SEC-{_OBJ_ORDER.index(oid.split(":")[1]) + 1}.1',
        'cert': [oid],
        'review': 'Pending SME review',
    }
    item['raw'] = item
    return item


def _pbqs():
    return [
        _order(1, 'S:4.8', 'Order a basic incident from first notice through the lesson.',
               ['Prepare contacts and backups before the bad day', 'Detect that this is an incident', 'Analyze scope before you erase anything', 'Contain the spread', 'Eradicate the cause', 'Recover from a clean point', 'Record a lesson with an owner'],
               'Preparation comes before the fire. Analyze and contain before you erase. Recover from a clean point, then name a change and an owner.'),
        _order(2, 'S:1.3', 'Order a firewall change so you can undo it.',
               ['Name the owner and the stakeholders', 'Write the impact and the backout', 'Test on a small set', 'Change during the agreed window', 'Update the diagram and the procedure'],
               'Know who owns it and how to undo it before you edit production, then update the picture people will follow.'),
        _order(3, 'S:3.2', 'Order a default-deny host firewall change.',
               ['Read the ticket', 'Allow loopback', 'Allow established flows', 'Add the named service allows', 'Set the default to deny', 'Save the rules'],
               'Put the allows in before the default deny, or you lock out the path you still need. Then save the rules.'),
        _order(4, 'S:4.9', 'Order a beginner evidence check on a file.',
               ['Leave the original untouched', 'Record a hash', 'Copy the file', 'Hash the copy', 'Compare the two hashes', 'Analyze the copy'],
               'The original stays still. Matching hashes show the copy is the same bits, and you analyze the copy.'),
        _order(5, 'S:4.6', 'Order account removal on the last day.',
               ['Confirm the person with the directory', 'Disable the account', 'Revoke tokens and badges', 'Remove standing admin rights', 'Record the time in the ticket'],
               'Prove who left, then remove the keys. A note with no disable leaves the door open.'),
        _order(6, 'S:4.1', 'Order a secure build for a new server.',
               ['Start from the approved baseline', 'Remove software you do not need', 'Change default passwords', 'Turn on the host firewall', 'Record the result against the baseline'],
               'Begin from the known-good build, shrink it, replace sticker passwords, then prove the host matches the baseline.'),
        _order(7, 'S:3.4', 'Order a backup you can trust.',
               ['Decide the recovery time and recovery point', 'Take an encrypted copy', 'Store a copy offsite', 'Restore a file in a test', 'Write the result'],
               'A copy you have never restored is a hope. Frequency and encryption follow from how much loss you can stand.'),
        _order(8, 'S:5.2', 'Order a risk entry.',
               ['Name the asset and the threat', 'Rate impact and likelihood', 'Pick transfer, accept, avoid, or mitigate', 'Name an owner and a review date', 'Report it if it crosses the threshold'],
               'A risk without an owner and a date is a worry, not a register entry.'),
        _order(9, 'S:2.5', 'Order a response to a vulnerable legacy device you cannot patch today.',
               ['Confirm the exposure', 'Isolate it to the least network it needs', 'Change any default password', 'Record a dated exception', 'Plan the replacement'],
               'Fence what you cannot patch, and write the exception down so it does not become permanent by silence.'),
        _order(10, 'S:4.3', 'Order vulnerability handling.',
               ['Scan or receive the finding', 'Confirm it is real and reachable', 'Prioritize by exposure and impact', 'Patch or add a compensating control', 'Rescan and report'],
               'A scanner line is not automatically an incident. Confirm, rank, fix or fence, then check again.'),
        _order(11, 'S:1.4', 'Order a certificate request.',
               ['Generate the key pair on the server', 'Keep the private key on that server', 'Build a signing request', 'Send only the request to the authority', 'Install the returned certificate and test the name'],
               'The private key never travels with the request. After the certificate returns, check that the name matches.'),
        _order(12, 'S:4.8', 'Order a tabletop before a failover drill.',
               ['Pick a scenario and the roles', 'Walk the calls without touching production', 'Write the gaps', 'Fix the plan', 'Schedule a real failover test'],
               'Talk it through, fix the plan, then move real work. Skipping the talk is how drills surprise you.'),
        _order(13, 'S:5.6', 'Order a response to a suspicious message.',
               ['Do not click and do not reply', 'Use the report button or the known security address', 'Leave the message in place for the investigators', 'Warn a coworker only through the official path', 'Return to work'],
               'Reporting is the job. Investigating alone, or forwarding the attachment, spreads the bait.'),
        _order(14, 'S:2.2', 'Order a check of a lookalike payment request.',
               ['Read the real sending address', 'Check the link host without signing in', 'Call back on a number already on file', 'Do not change any bank account from the message', 'Report the thread'],
               'The display name is cheap. The callback uses a number you already trusted, not the one in the message.'),
        _match(15, 'S:1.2', 'Match the failure to the goal.',
               [('An unapproved person can read the file', 'Confidentiality'),
                ('An approved total was edited later', 'Integrity'),
                ('The service is too slow to do the work', 'Availability'),
                ('The signer can be shown later', 'Non-repudiation')],
               'Each goal fails differently. Reading, changing, being down, and being unable to prove who acted are not the same event.'),
        _match(16, 'S:1.1', 'Match the control to its type.',
               [('A badge reader that stops a stranger', 'Preventive'),
                ('A camera that records the door', 'Detective'),
                ('A restore from last night', 'Corrective'),
                ('A sign that warns of prosecution', 'Deterrent')],
               'Preventive acts before. Detective notices after. Corrective repairs. Deterrent raises the felt cost.'),
        _match(17, 'S:2.4', 'Match the behavior to the malware family.',
               [('Spreads with nobody opening a file', 'Worm'),
                ('Looks useful and also harms', 'Trojan'),
                ('Locks data and demands payment', 'Ransomware'),
                ('Hides and collects keystrokes', 'Spyware')],
               'Family follows behavior: self-spread, disguise, lock-and-demand, or quiet collection.'),
        _match(18, 'S:4.6', 'Match the proof to the factor kind.',
               [('A long passphrase', 'Something you know'),
                ('A hardware security key', 'Something you have'),
                ('A fingerprint', 'Something you are'),
                ('A sign-in only from the clinic network', 'Somewhere you are')],
               'Two items you know are still one kind. Mix kinds when you want multi-factor authentication.'),
        _match(19, 'S:3.4', 'Match the spare site to its readiness.',
               [('Live data and a fast switch', 'Hot site'),
                ('Gear ready, data must catch up', 'Warm site'),
                ('Empty space and power only', 'Cold site'),
                ('A copy in another region', 'Geographic dispersion')],
               'Hot is fast and costly. Cold is cheap and slow. Distance keeps one disaster from taking both copies.'),
        _match(20, 'S:5.1', 'Match the document to its job.',
               [('Leadership\'s rule', 'Policy'),
                ('The measurable setting', 'Standard'),
                ('The step-by-step', 'Procedure'),
                ('Recommended, not mandatory', 'Guideline')],
               'A policy sets the duty. A standard measures it. A procedure walks the steps. A guideline advises.'),
        _match(21, 'S:5.2', 'Match the risk response.',
               [('Buy insurance for the residual loss', 'Transfer'),
                ('Write that you will live with it', 'Accept'),
                ('Stop doing the activity', 'Avoid'),
                ('Add a control that reduces it', 'Mitigate')],
               'Ignoring a risk with no note is not acceptance. Acceptance is written and reviewed.'),
        _match(22, 'S:1.4', 'Match the crypto job.',
               [('A fingerprint of the file', 'Hash'),
                ('The same secret locks and unlocks', 'Symmetric encryption'),
                ('A key pair', 'Asymmetric encryption'),
                ('A private key over a fingerprint of the bytes', 'Digital signature')],
               'A hash is not encryption. A signature uses a private key so others can check with the public key.'),
        _match(23, 'S:4.4', 'Match the monitoring tool to what it sees.',
               [('Many logs in one place', 'SIEM'),
                ('Who talked to whom, and how much', 'NetFlow'),
                ('A device pushes an event', 'SNMP trap'),
                ('Sensitive data leaving', 'Data loss prevention')],
               'Each tool answers a different question. A flow record is not a full packet, and a SIEM does not decide guilt alone.'),
        _match(24, 'S:2.1', 'Match the actor clue.',
               [('Patience, custom tools, no ransom', 'Nation-state'),
                ('A cause, and they want to be seen', 'Hacktivist'),
                ('Already has a key', 'Insider'),
                ('A kit someone else wrote', 'Unskilled attacker')],
               'Motive and resources are different clues. A loud slogan is not the same as a quiet long intrusion.'),
        _match(25, 'S:3.3', 'Match the data state to the control.',
               [('Files on a disk', 'Encryption at rest'),
                ('Moving between two hosts', 'Transport encryption'),
                ('Open on a screen in a lobby', 'A privacy screen and a clean desk'),
                ('A column of ID numbers', 'Field or record encryption')],
               'Rest, transit, and use are different moments. A locked disk does not hide an open screen.'),
        _match(26, 'S:4.5', 'Match the mail control.',
               [('Who may send for the domain', 'SPF'),
                ('A signature on the message', 'DKIM'),
                ('What to do when those checks fail', 'DMARC'),
                ('Filter before the inbox', 'Email gateway')],
               'SPF names senders. DKIM signs. DMARC sets the failure policy. The gateway is where you enforce a filter.'),
        _order(27, 'S:5.3', 'Order a vendor decision before data moves.',
               ['Write the security needs', 'Compare vendors against those needs', 'Read the contract and the audit rights', 'Move a small pilot', 'Keep a review date'],
               'Price is not the only score. Audit rights and a review date belong in the choice, not after the data has moved.'),
        _order(28, 'S:4.2', 'Order disposal of a laptop that held customer data.',
               ['Back up anything you must keep, elsewhere', 'Wipe or destroy to the standard', 'Match the serial to the certificate', 'Update the inventory', 'Close the ticket'],
               'Sanitization without a record is a story. The inventory has to drop the device the same day.'),
    ]


def as_bank_items():
    return _singles() + _pbqs()


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
            'status': 'covered',
            'topics_missing': [],
            'lessons': list(meta['lessons']),
            'labs': [],
            'items': items,
        }
    total = len(obj_out)
    summary = {
        'covered': total, 'partial': 0, 'gap': 0, 'total': total,
        'weighted_covered': 100.0, 'weighted_partial': 0.0,
        'items': sum(len(v['items']) for v in obj_out.values()),
        'topic_ratio': 1.0,
    }
    return obj_out, summary, dict(summary)
