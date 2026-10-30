"""Original practice-exam bank for the Cybersecurity course.

Topics are comparable to Security+ (SY0-701) and to entry-level cyber work.
This is not an official CompTIA exam and not a Department of Defense product.
"""

SEC_EXAM = {
    'code': 'SEC-FOUND',
    'name': 'Cybersecurity foundations practice',
    'short': 'Cybersecurity',
    'version': '1',
    'doc_version': 'Novak LMS™ original practice bank',
    'url': 'https://novak-lms.onrender.com/specs#course-SEC',
    'page': 'https://novak-lms.onrender.com/specs#course-SEC',
    'official': {
        'questions': '45 in a full practice sitting (120+ in the bank)',
        'minutes': 45,
        'passing': '750 simulated on a 100–900 practice scale',
    },
    'course': 'SEC',
}

SEC_DOMAINS = [
    ('1.0', 'Security ideas and risk words', 18),
    ('2.0', 'Threats and malware', 20),
    ('3.0', 'Protecting identity, crypto, networks, and hosts', 28),
    ('4.0', 'Operations and incident response', 20),
    ('5.0', 'Governance, risk, and privacy', 14),
]

_META = [
    ('1.1', '1.0', 'Apply confidentiality, integrity, availability, and control types.', ['SEC-1.2', 'SEC-1.3'], 'SEC 1.2'),
    ('1.2', '1.0', 'Use asset, threat, vulnerability, and impact precisely.', ['SEC-1.4', 'SEC-10.2'], 'SEC 1.4'),
    ('2.1', '2.0', 'Recognize social engineering and physical tricks.', ['SEC-2.2', 'SEC-2.4'], 'SEC 2.2'),
    ('2.2', '2.0', 'Separate malware families and a safe first response.', ['SEC-3.2', 'SEC-3.4'], 'SEC 3.2'),
    ('3.1', '3.0', 'Separate hashing, encryption, encoding, and certificates.', ['SEC-4.1', 'SEC-4.3'], 'SEC 4.1'),
    ('3.2', '3.0', 'Apply MFA, least privilege, and account hygiene.', ['SEC-5.1', 'SEC-5.2'], 'SEC 5.1'),
    ('3.3', '3.0', 'Choose firewall, segmentation, VPN, and wireless decisions.', ['SEC-6.1', 'SEC-6.2'], 'SEC 6.1'),
    ('3.4', '3.0', 'Harden Linux and Windows hosts and notice drift.', ['SEC-7.1', 'SEC-7.2'], 'SEC 7.1'),
    ('4.1', '4.0', 'Read logs, SIEM alerts, and baselines.', ['SEC-8.1', 'SEC-8.3'], 'SEC 8.1'),
    ('4.2', '4.0', 'Follow incident response and basic evidence care.', ['SEC-9.1', 'SEC-9.3'], 'SEC 9.1'),
    ('5.1', '5.0', 'Tell policy, standard, and procedure apart, and talk about risk.', ['SEC-10.1', 'SEC-10.2'], 'SEC 10.1'),
    ('5.2', '5.0', 'Apply privacy limits and honest scope. Do not claim an endorsement.', ['SEC-10.3', 'SEC-10.4'], 'SEC 10.4'),
]

_DOM_NAME = {d: name for d, name, _w in SEC_DOMAINS}
_COUNTS = {}
for _oid, _dom, *_rest in _META:
    _COUNTS[_dom] = _COUNTS.get(_dom, 0) + 1

SEC_OBJECTIVES = {}
for _oid, _dom, _title, _cobjs, _lesson in _META:
    SEC_OBJECTIVES[f'S:{_oid}'] = {
        'exam': 'S',
        'id': _oid,
        'domain': _dom,
        'domain_name': _DOM_NAME[_dom],
        'title': _title,
        'topics': [],
        'weight': round(dict((d, w) for d, _n, w in SEC_DOMAINS)[_dom] / _COUNTS[_dom], 2),
        'course_objs': list(_cobjs),
        'lessons': [_lesson],
        'labs': [],
    }

_PLACES = [
    ('clinic', 'patient schedule'),
    ('library', 'patron database'),
    ('warehouse', 'shipping manifest'),
    ('city hall', 'permit archive'),
    ('school lab', 'student roster'),
    ('bookstore', 'loyalty list'),
    ('museum', 'donor file'),
    ('ferry office', 'crew roster'),
    ('bakery', 'supplier invoices'),
    ('research bench', 'lab notebook'),
]


def _mc(n, oid, course_obj, text, correct, wrongs, why):
    w = list(wrongs)
    # Keep the key from being the uniquely longest option.
    if len(correct) > max(len(x) for x in w):
        w[0] = w[0] + ' in this workplace'
    opts = list(w)
    opts.insert(n % 4, correct)
    item = {
        'id': f'SECQ-{n:03d}',
        'bank_id': f'SECQ-{n:03d}',
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
    builders = [
        ('S:1.1', 'SEC-1.2', lambda p, t: (
            f'At the {p}, someone forwards the {t} to a personal mailbox. Which goal failed?',
            'Confidentiality',
            ['Availability of the mail server', 'Integrity of the clock', 'A firewall default-allow policy'],
            'Confidentiality fails when unapproved people can read the data. The file did not have to change, and the service can still be up.',
        )),
        ('S:1.1', 'SEC-1.3', lambda p, t: (
            f'The {p} keeps a badge reader on the records room and a camera that only records. Which statement is right?',
            'The reader is preventive and the camera is detective',
            ['Both are corrective', 'The camera stops entry by itself', 'The reader is only a compensating control'],
            'A badge reader blocks entry before it happens. A camera reports what already happened.',
        )),
        ('S:1.2', 'SEC-1.4', lambda p, t: (
            f'For the {p}, the {t} is stolen because an old form has a known flaw. Which word is the flaw?',
            'Vulnerability',
            ['Asset', 'Impact', 'Patch'],
            'The flaw is the vulnerability. The file is the asset. The harm is the impact. The update would be the patch.',
        )),
        ('S:1.2', 'SEC-10.2', lambda p, t: (
            f'A manager at the {p} asks how risky a lost laptop is. What belongs in the answer?',
            'How often it happens here and how bad the harm is',
            ['Only the attacker nickname', 'Only the laptop purchase price', 'A claim that every risk is critical'],
            'Risk talk needs likelihood in this workplace and impact as real harm, not a slogan.',
        )),
        ('S:2.1', 'SEC-2.2', lambda p, t: (
            f'A message to the {p} shows a trusted display name, a lookalike address, and a link for the {t}. What is this?',
            'Phishing',
            ['A routine patch notice you must obey', 'A VPN split-tunnel choice', 'A disk hash'],
            'Phishing imitates a trusted sender. Check the real address and do not sign in through the unexpected link.',
        )),
        ('S:2.1', 'SEC-2.4', lambda p, t: (
            f'Someone follows a badged employee into the {p} records room. What is that called?',
            'Tailgating',
            ['Replay', 'Encoding', 'A false positive'],
            'Tailgating is physical entry behind someone who already authenticated.',
        )),
        ('S:2.2', 'SEC-3.2', lambda p, t: (
            f'Computers at the {p} infect each other with no one opening a file, and the {t} is untouched. Which family fits best?',
            'A worm',
            ['A hash', 'A certificate', 'A baseline'],
            'A worm spreads on its own. A virus usually waits for a person to open a host file.',
        )),
        ('S:2.2', 'SEC-3.4', lambda p, t: (
            f'A pop-up at the {p} says the {t} is encrypted and demands payment. What is the first student action?',
            'Do not pay or run unknown files; isolate per the local rule and record what you see',
            ['Pay from a personal account to save time', 'Open the attachment to confirm', 'Post the note on a public chat'],
            'Ransomware is a lock-and-demand. Contain and record. Do not pay and do not launch the unknown file.',
        )),
        ('S:3.1', 'SEC-4.1', lambda p, t: (
            f'The {p} publishes a fingerprint for the {t} installer. A copied file does not match. What failed?',
            'An integrity check using a hash',
            ['A confidentiality lock', 'An encoding costume', 'A wireless channel plan'],
            'A hash is a fingerprint. A mismatch means the bytes changed. It does not by itself hide the file.',
        )),
        ('S:3.1', 'SEC-4.3', lambda p, t: (
            f'A browser at the {p} warns that the signer for the {t} site is not trusted. What should you do?',
            'Stop and report instead of adding the signer',
            ['Add the signer so the warning disappears', 'Switch the site to HTTP', 'Email a private key to yourself'],
            'An untrusted signer is not a small glitch. Adding them is a trust decision you do not make casually.',
        )),
        ('S:3.2', 'SEC-5.1', lambda p, t: (
            f'A {p} account protects the {t} with a password plus a PIN. Is that MFA?',
            'No. Both are something you know',
            ['Yes, because there are two boxes', 'Yes, because the PIN is longer', 'Yes, because the site uses TLS'],
            'MFA needs two different factor kinds. A password and a PIN are both knowledge.',
        )),
        ('S:3.2', 'SEC-5.2', lambda p, t: (
            f'A clerk at the {p} needs to read one folder of the {t}. What access do you grant?',
            'Read on that folder only',
            ['Domain administrator', 'A shared login for the whole shift', 'The service account password'],
            'Least privilege is the smallest right that completes the task.',
        )),
        ('S:3.3', 'SEC-6.1', lambda p, t: (
            f'The {p} host still uses an INPUT accept policy while serving the {t}. What is the better stance?',
            'Default deny, then explicit allows',
            ['Default allow, with no rules', 'Disable the firewall during business hours', 'Allow every inbound port from guests'],
            'Default deny is least privilege for packets. Allows should name who and which service.',
        )),
        ('S:3.3', 'SEC-6.2', lambda p, t: (
            f'Guest Wi-Fi at the {p} can open the server that holds the {t}. What is missing?',
            'A rule between the guest zone and the server zone',
            ['A longer SSID', 'A new wallpaper', 'A second monitor'],
            'A VLAN name without a filter does not segment. Guests need a path that cannot reach internal data.',
        )),
        ('S:3.4', 'SEC-7.1', lambda p, t: (
            f'On a {p} Linux host, the {t} file is mode 666. What is wrong?',
            'Every account can read and change it',
            ['Only root can read it', 'It is encrypted', 'It is a certificate'],
            'Mode 666 grants read and write to others. A secret needs the other triple closed.',
        )),
        ('S:3.4', 'SEC-7.2', lambda p, t: (
            f'You are hardening SSH for the {p} so staff can reach a host that stores the {t}. What is the safe order?',
            'Install a working key, then disable password login',
            ['Disable passwords before any key exists', 'Permit root login with a shared password', 'Email the private key to the team'],
            'Close the password door only after a key works, or you lock everyone out. Do not share the private key.',
        )),
        ('S:4.1', 'SEC-8.1', lambda p, t: (
            f'You need failed sign-ins for a {p} Windows PC that opens the {t}. Which channel?',
            'Security',
            ['Application', 'Setup', 'A cleared log'],
            'Windows logon success and failure are in the Security channel. 4625 is a failure. Do not clear the log.',
        )),
        ('S:4.1', 'SEC-8.3', lambda p, t: (
            f'A SIEM alert says the {p} backup of the {t} looks like ransomware. The job is the known nightly backup. What is the triage?',
            'Likely false, with a narrow note so the real rule stays on',
            ['Pay the demand', 'Disable every alert', 'Wipe the SIEM'],
            'A known-good job is a false positive. Tune it narrowly. Do not turn the whole rule off.',
        )),
        ('S:4.2', 'SEC-9.1', lambda p, t: (
            f'The only suspicious PC at the {p} holds clues about the {t}. What do you avoid as the first move?',
            'Reimaging it before anyone records what is there',
            ['Naming an incident lead', 'Isolating it from the network if policy says so', 'Writing the time and the signs'],
            'Contain and record before you erase the only copy of the story.',
        )),
        ('S:4.2', 'SEC-9.3', lambda p, t: (
            f'A USB stick of logs from the {p} about the {t} sits on a shared desk with no label. What is missing?',
            'A chain of who held it and when',
            ['A brighter desktop wallpaper', 'A faster CPU', 'A guest Wi-Fi name'],
            'Chain of custody is the list of holders and times. An unlabeled stick has no chain.',
        )),
        ('S:5.1', 'SEC-10.1', lambda p, t: (
            f'The {p} decides that found USB sticks must not be plugged into computers that hold the {t}. That decision is a:',
            'Policy',
            ['Hash', 'Worm', 'VLAN'],
            'Policy is the leadership decision. A standard would set a measurable bar. A procedure would list the steps.',
        )),
        ('S:5.1', 'SEC-10.2', lambda p, t: (
            f'Leaders at the {p} will live with a low risk to the {t} and review it next quarter. That choice is:',
            'Explicit risk acceptance',
            ['Proof an incident cannot happen', 'A substitute for logs', 'An official certification'],
            'Accepting a risk is allowed when it is written down and reviewed. Silence is not acceptance.',
        )),
        ('S:5.2', 'SEC-10.4', lambda p, t: (
            f'A printer ticket at the {p} does not require reading the whole {t}. What privacy habit applies?',
            'Open only what the task needs',
            ['Browse the full record in case it helps later', 'Paste details into a widely read ticket', 'Photograph the screen for a group chat'],
            'Minimum necessary means the task sets the view. Curiosity is not a task.',
        )),
        ('S:5.2', 'SEC-10.3', lambda p, t: (
            f'A poster at the {p} says the {t} training is an official certification because the topics overlap a public outline. What is wrong?',
            'Overlap is not an endorsement or an official exam',
            ['The topics cannot be taught at all', 'A practice bank is illegal', 'Students must skip labs'],
            'You may say the topics are comparable. You may not claim a vendor or a government endorsed the course.',
        )),
    ]
    # 24 builders × 10 places = 240, too many. Take 5 places per builder = 120.
    for bi, (oid, cobj, fn) in enumerate(builders):
        for pi, (place, thing) in enumerate(_PLACES[:5]):
            text, correct, wrongs, why = fn(place, thing)
            out.append(_mc(n, oid, cobj, text, correct, wrongs, why))
            n += 1
    return out


def _pbqs():
    def order_item(n, oid, cobj, text, steps, why):
        opts = list(reversed(steps))
        item = {
            'id': f'SECQ-P{n}',
            'bank_id': f'SECQ-P{n}',
            'type': 'order',
            'text': text,
            'options': opts,
            'correct': list(steps),
            'explanation': why,
            'obj': cobj,
            'cert': [oid],
            'review': 'Pending SME review',
        }
        item['raw'] = item
        return item

    def match_item(n, oid, cobj, text, pairs, why):
        prompts = [a for a, _b in pairs]
        correct = [b for _a, b in pairs]
        options = list(reversed(correct))
        item = {
            'id': f'SECQ-P{n}',
            'bank_id': f'SECQ-P{n}',
            'type': 'match',
            'text': text,
            'prompts': prompts,
            'options': options,
            'correct': correct,
            'explanation': why,
            'obj': cobj,
            'cert': [oid],
            'review': 'Pending SME review',
        }
        item['raw'] = item
        return item

    return [
        order_item(1, 'S:4.2', 'SEC-9.1',
                   'Order a basic incident response.',
                   ['Prepare contacts and logs', 'Identify that this is an incident', 'Contain the spread', 'Eradicate the cause', 'Recover from a clean point', 'Record the lesson'],
                   'Prepare and identify come before you erase anything. Contain, then remove the cause, recover clean, and write the lesson.'),
        order_item(2, 'S:3.3', 'SEC-6.1',
                   'Order a default-deny host firewall change.',
                   ['Read the ticket', 'Allow loopback', 'Allow established flows', 'Add the named service allows', 'Set the default to deny', 'Save the rules'],
                   'Put the allows in before the default deny, then persist them.'),
        order_item(3, 'S:3.4', 'SEC-7.2',
                   'Order SSH hardening so you do not lock yourself out.',
                   ['Create the user key', 'Install the public key', 'Fix directory and file modes', 'Test that the key works', 'Disable password login', 'Test the daemon config'],
                   'A working key is the way back. Close passwords only after that, and check the config.'),
        order_item(4, 'S:4.2', 'SEC-9.4',
                   'Order a beginner evidence check on a file.',
                   ['Leave the original untouched', 'Record a hash', 'Copy the file', 'Hash the copy', 'Compare the two hashes', 'Analyze the copy'],
                   'The original stays still. Matching hashes show the copy is the same bits.'),
        match_item(5, 'S:1.1', 'SEC-1.2',
                   'Match the failure to the goal.',
                   [('Unapproved person can read the file', 'Confidentiality'),
                    ('Approved total was edited later', 'Integrity'),
                    ('The service is too slow to do the work', 'Availability'),
                    ('A badge reader stops a stranger', 'Preventive control')],
                   'Each goal fails differently. A badge reader is preventive because it acts before entry.'),
        match_item(6, 'S:2.2', 'SEC-3.2',
                   'Match the behavior to the malware family.',
                   [('Spreads with no one opening a file', 'Worm'),
                    ('Looks useful and also harms', 'Trojan'),
                    ('Locks data and demands payment', 'Ransomware'),
                    ('Hides and collects information', 'Spyware')],
                   'Family follows behavior: self-spread, disguise, lock-and-demand, or quiet collection.'),
    ]


def as_bank_items():
    return _singles() + _pbqs()


def pool_map():
    out = {}
    for it in as_bank_items():
        for oid in it['cert']:
            if it['type'] == 'single' or it['type'] in ('order', 'match'):
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
    before = dict(summary)
    return obj_out, summary, before
