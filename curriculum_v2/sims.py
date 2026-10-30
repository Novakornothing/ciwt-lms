"""Try-It micro-simulations for every laddered concept section.

Each R4 maps to one configured widget. The browser renders it (static/js/sims/novak-sims.js).
Nothing here calls a network service. Configs are deterministic from the section id.
"""
import hashlib
import re

TYPES = (
    'subnet', 'osi', 'ports', 'chmod', 'raid', 'pcbuild', 'boot', 'acl', 'dora',
    'vlan', 'troubleshoot', 'cable', 'shell', 'cia', 'hash', 'phish', 'logs',
    'match', 'pairs', 'classify', 'sequence', 'trace', 'choose',
)

_TAG = re.compile(r'<[^>]+>')
_WS = re.compile(r'\s+')
_WORD = re.compile(r"\S+")

# Lesson label -> widget, only where the whole lesson is that topic.
# CLIENT reuses the ITSUP labels (8.x–13.x). Troubleshooting is not a lesson-wide default.
_ITSUP = {
    '2.1': 'pcbuild', '2.2': 'boot', '2.3': 'pcbuild', '2.4': 'pcbuild', '2.5': 'boot', '2.6': 'shell',
    '3.2': 'raid', '3.3': 'pcbuild', '3.4': 'cable',
    '5.1': 'subnet', '5.2': 'ports', '5.4': 'acl',
    '6.3': 'vlan',
    '9.1': 'shell', '9.2': 'shell',
    '10.1': 'cia', '10.2': 'cia', '10.3': 'hash', '10.4': 'phish',
    '11.4': 'logs',
    '12.3': 'hash',
    '13.1': 'shell', '13.2': 'shell', '13.3': 'shell', '13.4': 'dora', '13.5': 'shell', '13.6': 'boot',
}
_NETOPS = {
    '1.1': 'osi', '1.2': 'subnet', '1.3': 'ports',
    '2.1': 'vlan', '2.2': 'vlan', '2.3': 'cable',
    '4.1': 'dora', '4.2': 'dora', '4.3': 'acl',
    '5.1': 'logs', '5.2': 'cia', '5.3': 'acl',
    '6.1': 'logs',
    '9.1': 'shell', '9.3': 'shell', '9.5': 'cable', '9.6': 'shell',
}
_LESSON = {'ITSUP': _ITSUP, 'CLIENT': _ITSUP, 'NETOPS': _NETOPS}
_TROUBLE_LESSONS = {('ITSUP', '5.3'), ('ITSUP', '7.1'), ('ITSUP', '7.2'), ('ITSUP', '7.3'), ('ITSUP', '7.4'),
                    ('NETOPS', '6.2')}
_TROUBLE_RE = re.compile(
    r'troubleshoot|methodology|fault domain|isolation order|root cause|diagnos|identify the (problem|symptom)',
    re.I)
_LI = re.compile(r'<li[^>]*>(.*?)</li>', re.I | re.S)

# Sid fragments that pin a specialty widget even when the lesson default differs.
_SID = (
    ('phish', ('phish', 'social-engineer')),
    ('raid', ('raid',)),
    ('boot', ('uefi', 'secure-boot', 'post-order')),
    ('pcbuild', ('motherboard', 'form-factor')),
    ('cable', ('connector', 'cable-type', 'cable-types')),
    ('chmod', ('linux-inventory-cousins',)),
    ('osi', ('layer-thinking',)),
)

_METHOD = [
    'Identify the symptom and who is affected',
    'Pick one likely cause',
    'Test that cause with one change',
    'Verify the result and write it down',
]

_SUBNETS = (
    ('10.0.0.50', 16, 28),
    ('192.168.1.200', 16, 26),
    ('172.16.8.10', 12, 20),
    ('10.1.2.30', 16, 27),
    ('192.168.10.77', 16, 26),
)
_CHMOD = ('754', '640', '755', '600', '750')
_PORTS = (
    ('HTTPS', '443'), ('SSH', '22'), ('DNS', '53'), ('DHCP', '67'),
    ('HTTP', '80'), ('RDP', '3389'), ('SMTP', '25'), ('LDAP', '389'),
)
_CABLES = (
    ('rj45', 'RJ-45', 'Eight gold contacts in a clear plastic clip'),
    ('lc', 'LC', 'A small square fiber plug with a latch'),
    ('usbc', 'USB-C', 'An oval metal plug, reversible'),
    ('hdmi', 'HDMI', 'A wide flat plug with tapered corners'),
    ('db9', 'DB-9', 'A D-shaped metal shell with pin sockets'),
)
_CABLE_CHOICES = ['RJ-45', 'LC', 'USB-C', 'HDMI', 'DB-9']
_SHELLS = (
    {
        'expect': 'ipconfig',
        'hint': 'ipconfig',
        'commands': {
            'ipconfig': 'IPv4 Address. . . . . : 192.168.1.24\nSubnet Mask . . . . . : 255.255.255.0\nDefault Gateway . . . : 192.168.1.1',
            'help': 'Safe commands: help, ipconfig, ping, ls, ip route, nslookup',
        },
        'question': 'What is the default gateway?',
        'choices': ['192.168.1.1', '10.0.0.1', '169.254.1.1'],
        'answer': '192.168.1.1',
    },
    {
        'expect': 'ping',
        'hint': 'ping',
        'commands': {
            'ping': 'Reply from 192.168.1.1: time<1ms TTL=64\nPackets: Sent = 4, Received = 4, Lost = 0',
            'help': 'Safe commands: help, ipconfig, ping, ls, ip route, nslookup',
        },
        'question': 'Did the gateway answer?',
        'choices': ['Yes, four replies', 'No, all lost', 'Name not found'],
        'answer': 'Yes, four replies',
    },
    {
        'expect': 'ls',
        'hint': 'ls',
        'commands': {
            'ls': 'Documents  Downloads  notes.txt  script.sh',
            'help': 'Safe commands: help, ipconfig, ping, ls, ip route, nslookup',
        },
        'question': 'Which name is a file here?',
        'choices': ['notes.txt', 'eth0', 'C:\\Windows'],
        'answer': 'notes.txt',
    },
    {
        'expect': 'ip route',
        'hint': 'ip route',
        'commands': {
            'ip route': 'default via 10.0.0.1 dev eth0\n10.0.0.0/24 dev eth0 proto kernel',
            'help': 'Safe commands: help, ipconfig, ping, ls, ip route, nslookup',
        },
        'question': 'What is the default gateway?',
        'choices': ['10.0.0.1', '192.168.1.1', 'none'],
        'answer': '10.0.0.1',
    },
    {
        'expect': 'nslookup',
        'hint': 'nslookup',
        'commands': {
            'nslookup': 'Name: example.com\nAddress: 93.184.216.34',
            'help': 'Safe commands: help, ipconfig, ping, ls, ip route, nslookup',
        },
        'question': 'Which address did the name resolve to?',
        'choices': ['93.184.216.34', '192.168.1.1', '10.0.0.1'],
        'answer': '93.184.216.34',
    },
)
_CIA = (
    ('A laptop is stolen from an unlocked desk.', 'Confidentiality'),
    ('A ticket total was edited after the tech saved it.', 'Integrity'),
    ('The file server is up but no one can reach it.', 'Availability'),
    ('A password was pasted into a public chat.', 'Confidentiality'),
)
_PHISH = (
    {
        'from': 'billing@paypa1.example',
        'subject': 'Account closes in 10 minutes',
        'body': 'Confirm your password at secure-login.example.net or the account closes.',
        'clues': (
            ('domain', 'Sender domain is paypa1.example, not the real company', True),
            ('urgency', 'The message threatens closure in 10 minutes', True),
            ('link', 'The link host is secure-login.example.net', True),
            ('logo', 'The message includes a company logo', False),
        ),
    },
    {
        'from': 'it-desk@school.example',
        'subject': 'Please review the attached schedule',
        'body': 'The lab schedule for Thursday is attached. Reply if a room is wrong.',
        'clues': (
            ('domain', 'Sender domain matches the school', False),
            ('urgency', 'It demands a password right now', False),
            ('ask', 'It asks you to check a schedule, not a credential', False),
            ('link', 'A hidden button posts your password to an odd host', True),
        ),
    },
)
_LOGS = (
    ('l1', 'info', 'kernel', 'eth0 link up, 1 Gbps full duplex', False),
    ('l2', 'warning', 'dhcp', 'Lease renewed for 192.168.1.24', False),
    ('l3', 'error', 'auth', 'Failed sign-in for jlee from 203.0.113.10', True),
    ('l4', 'info', 'cron', 'Nightly backup finished, 0 errors', False),
    ('l5', 'warning', 'disk', 'Volume C has 18 percent free', False),
)
_ACL = (
    {
        'packet': 'TCP port 443 from 10.1.1.5',
        'rules': ('permit tcp 10.0.0.0/8 any eq 443', 'deny ip any any'),
        'answer': 'permit',
        'why': 'The first rule matches this packet, so the later deny never runs.',
    },
    {
        'packet': 'TCP port 22 from 198.51.100.9',
        'rules': ('permit tcp 10.0.0.0/8 any eq 443', 'deny ip any any'),
        'answer': 'deny',
        'why': 'Port 22 does not match the permit, so the final deny catches it.',
    },
)
_OSI_LAYERS = ('Data', 'Segment', 'Packet', 'Frame', 'Bits')
_BOOT = ('POST', 'UEFI', 'Bootloader', 'Kernel', 'Sign-in')
_DHCP = ('Discover', 'Offer', 'Request', 'Acknowledge')
_DNS = ('Client asks the resolver', 'Resolver asks a root server', 'Resolver asks the TLD',
        'Resolver asks the authority', 'Answer is cached')
_VLAN_PORTS = (
    {'id': '1', 'vlan': '10', 'label': 'Port 1 · VLAN 10'},
    {'id': '2', 'vlan': '10', 'label': 'Port 2 · VLAN 10'},
    {'id': '3', 'vlan': '20', 'label': 'Port 3 · VLAN 20'},
)

_REQUIRED = {
    'subnet': (['ip', 'startPrefix'], ['prefix']),
    'osi': (['layers', 'choices', 'answer'], ['answer']),
    'ports': (['pairs'], ['pairs']),
    'chmod': (['target'], ['octal']),
    'raid': (['disks', 'sizeTB', 'levels'], ['level']),
    'pcbuild': (['slots', 'parts'], ['slots']),
    'boot': (['stages', 'choices', 'answer'], ['answer']),
    'acl': (['packet', 'rules', 'answer', 'why'], ['answer']),
    'dora': (['mode', 'steps', 'start'], ['order']),
    'vlan': (['ports', 'frame', 'choices', 'answer'], ['answer']),
    'troubleshoot': (['mode'], []),
    'match': (['buckets', 'items'], ['items']),
    'pairs': (['buckets', 'items'], ['items']),
    'classify': (['buckets', 'items'], ['items']),
    'sequence': (['steps', 'start'], ['order']),
    'trace': (['steps', 'start'], ['order']),
    'choose': (['stem', 'options', 'answer'], ['answer']),
    'cable': (['shape', 'choices', 'answer'], ['answer']),
    'shell': (['expect', 'hint', 'commands', 'question', 'choices', 'answer'], ['command', 'answer']),
    'cia': (['buckets', 'items'], ['items']),
    'hash': (['start'], ['changed']),
    'phish': (['sender', 'subject', 'body', 'clues'], ['flags']),
    'logs': (['lines', 'answerId'], ['pick']),
}


def plain(text):
    return _WS.sub(' ', _TAG.sub('', text or '')).strip()


def words(text):
    return _WORD.findall(text or '')


def _rot(key, n):
    if n <= 0:
        return 0
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % n


def _pick(seq, key):
    return seq[_rot(key, len(seq))]


def _shuf(items, key):
    out = list(items)
    digest = hashlib.sha256(('shuf:' + key).encode()).digest()
    for i in range(len(out) - 1, 0, -1):
        j = digest[i % len(digest)] % (i + 1)
        out[i], out[j] = out[j], out[i]
    if out == list(items) and len(out) > 1:
        out = list(reversed(out))
    return out


def _instr(text):
    text = plain(text)
    if not text or len(words(text)) > 25:
        raise ValueError(f'instruction must be 1–25 words: {text!r}')
    return text


def _finish(kind, instruction, params, goal):
    return {'type': kind, 'instruction': _instr(instruction), 'params': params, 'goal': goal}


def _steps_from_r3(entry):
    html = ((entry.get('rungs') or {}).get('R3') or {}).get('html') or ''
    steps = [plain(x) for x in _LI.findall(html)]
    steps = [s for s in steps if s]
    return steps if len(steps) >= 3 else None


def _is_trouble(entry, widget):
    if (entry.get('course'), entry.get('label')) in _TROUBLE_LESSONS and (widget or {}).get('type') == 'order':
        return True
    blob = ' '.join([
        entry.get('heading') or '',
        entry.get('sid') or '',
        (widget or {}).get('prompt') or '',
    ])
    return bool(_TROUBLE_RE.search(blob)) and (widget or {}).get('type') == 'order'


def _sec_kind(entry):
    """Security sections use the same widgets as the other courses, spread so one type does not dominate."""
    blob = f"{entry.get('heading') or ''} {entry.get('sid') or ''}".lower()
    rules = (
        ('phish', ('phish', 'vishing', 'smishing', 'pretext', 'baiting')),
        ('hash', ('hash', 'checksum', 'digest')),
        ('logs', ('logs', 'syslog', 'siem')),
        ('acl', ('firewall', 'iptables')),
        ('ports', ('ports', 'well-known')),
        ('cia', ('confidentiality', 'availability')),
    )
    for kind, words in rules:
        if any(word in blob for word in words):
            return kind
    cycle = ('classify', 'match', 'pairs', 'sequence', 'choose', 'shell',
             'cia', 'hash', 'phish', 'logs', 'acl', 'ports', 'trace')
    n = int(hashlib.sha256(('sec-widget:' + (entry.get('sid') or '')).encode()).hexdigest()[:8], 16)
    return cycle[n % len(cycle)]


def _kind_for(entry):
    course, label, sid = entry['course'], entry['label'], entry.get('sid') or ''
    if course == 'SEC':
        return _sec_kind(entry)
    sid_l = sid.lower()
    for kind, bits in _SID:
        if any(b in sid_l for b in bits):
            return kind
    mapped = _LESSON.get(course, {}).get(label)
    if mapped:
        return mapped
    widget = ((entry.get('rungs') or {}).get('R4') or {}).get('widget') or {}
    if _is_trouble(entry, widget):
        return 'troubleshoot'
    if widget.get('type') == 'order':
        steps = _steps_of(widget) or []
        return 'trace' if len(steps) >= 5 else 'sequence'
    if widget.get('type') == 'sort':
        names = [plain(b) for b in (widget.get('buckets') or {}) if plain(b)]
        if len(names) >= 3:
            return 'classify'
        key = f'{course}|{label}|{sid}'
        return 'pairs' if _rot(key, 2) else 'match'
    return 'choose'


def _steps_of(widget):
    if not widget or widget.get('type') != 'order':
        return None
    steps = [plain(s) for s in (widget.get('steps') or [])]
    steps = [s for s in steps if s]
    return steps if len(steps) >= 3 else None


def _sort_of(widget):
    if not widget or widget.get('type') != 'sort':
        return None
    buckets = widget.get('buckets') or {}
    items = []
    for bucket, values in buckets.items():
        b = plain(bucket)
        if not b:
            continue
        for value in values:
            text = plain(value)
            if text:
                items.append({'text': text, 'bucket': b})
    names = []
    for bucket in buckets:
        b = plain(bucket)
        if b and b not in names:
            names.append(b)
    if len(names) < 2 or len(items) < 4:
        return None
    for i, item in enumerate(items):
        item['id'] = f'i{i}'
    return names, items


def _order_cfg(kind, steps, key, instruction):
    return _finish(kind, instruction,
                   {'mode': 'order', 'steps': steps, 'start': _shuf(steps, key)} if kind == 'troubleshoot'
                   else {'steps': steps, 'start': _shuf(steps, key)},
                   {'order': steps})


def _troubleshoot(entry, widget, key):
    steps = _steps_of(widget) or _steps_from_r3(entry) or list(_METHOD)
    return _order_cfg('troubleshoot', steps, key, 'Put the troubleshooting steps in order, then check.')


def _grouped(kind, names, items, instruction):
    return _finish(kind, instruction,
                   {'buckets': names, 'items': items},
                   {'items': {it['id']: it['bucket'] for it in items}})


def _classifier(kind, key, default_items, default_buckets, instruction):
    items = [{'id': f'c{i}', 'text': text, 'bucket': bucket} for i, (text, bucket) in enumerate(default_items)]
    return _finish(kind, instruction,
                   {'buckets': list(default_buckets), 'items': _shuf(items, key)},
                   {'items': {it['id']: it['bucket'] for it in items}})


def _choose(entry, key):
    checks = ((entry.get('rungs') or {}).get('R4') or {}).get('checks') or entry.get('checks') or []
    if not checks:
        steps = list(_METHOD)
        return _order_cfg('sequence', steps, key, 'Put these steps in the order this concept uses, then check.')
    chk = checks[0]
    options = [chk['correct']] + list(chk.get('wrong') or [])
    stem = plain(chk.get('q') or '') or 'Which line matches this concept?'
    return _finish('choose', 'Pick the line that matches this concept, then check.',
                   {'stem': stem[:240], 'options': _shuf(options, key), 'answer': chk['correct']},
                   {'answer': chk['correct']})


def _build(entry):
    course, label, sid = entry['course'], entry['label'], entry['sid']
    key = f'{course}|{label}|{sid}'
    r4 = (entry.get('rungs') or {}).get('R4') or {}
    widget = r4.get('widget') or {}
    kind = _kind_for(entry)

    if kind == 'troubleshoot':
        return _troubleshoot(entry, widget, key)
    if kind == 'subnet':
        ip, start, prefix = _pick(_SUBNETS, key)
        return _finish('subnet', f'Set the prefix to /{prefix}, then read the network address.',
                       {'ip': ip, 'startPrefix': start}, {'prefix': prefix})
    if kind == 'osi':
        return _finish('osi', 'Step through encapsulation, then name the layer that adds the IP header.',
                       {'layers': list(_OSI_LAYERS), 'choices': ['Transport', 'Network', 'Data Link'],
                        'answer': 'Network'},
                       {'answer': 'Network'})
    if kind == 'ports':
        offset = _rot(key, 4)
        pairs = [_PORTS[(offset + i) % len(_PORTS)] for i in range(4)]
        return _finish('ports', 'Match each service to its well-known port, then check.',
                       {'pairs': [{'service': a, 'port': b} for a, b in pairs]},
                       {'pairs': {a: b for a, b in pairs}})
    if kind == 'chmod':
        target = _pick(_CHMOD, key)
        return _finish('chmod', f'Set the permission boxes to {target}, then check.',
                       {'target': target}, {'octal': target})
    if kind == 'raid':
        disks = 3 + _rot(key, 3)
        return _finish('raid', 'Choose the RAID level that survives one failure and keeps more than half the capacity.',
                       {'disks': disks, 'sizeTB': 2, 'levels': ['0', '1', '5', '6', '10']},
                       {'level': '5'})
    if kind == 'pcbuild':
        slots = ['CPU', 'RAM', 'Storage', 'PSU']
        return _finish('pcbuild', 'Seat the CPU, memory, storage, and power supply on the board.',
                       {'slots': slots, 'parts': slots + ['GPU']},
                       {'slots': slots})
    if kind == 'boot':
        return _finish('boot', 'Step through startup, then pick the stage that loads the kernel.',
                       {'stages': list(_BOOT), 'choices': ['POST', 'UEFI', 'Kernel'], 'answer': 'Kernel'},
                       {'answer': 'Kernel'})
    if kind == 'acl':
        spec = _pick(_ACL, key)
        return _finish('acl', 'Walk the packet down the list and say whether it is permitted.',
                       {'packet': spec['packet'], 'rules': list(spec['rules']), 'answer': spec['answer'],
                        'why': spec['why']},
                       {'answer': spec['answer']})
    if kind == 'dora':
        mode = 'dns' if label in ('4.2', '13.4') else 'dhcp'
        steps = list(_DNS if mode == 'dns' else _DHCP)
        text = 'Arrange the DNS lookup steps, then check.' if mode == 'dns' else 'Arrange the DHCP messages into DORA order, then check.'
        return _finish('dora', text, {'mode': mode, 'steps': steps, 'start': _shuf(steps, key)}, {'order': steps})
    if kind == 'vlan':
        return _finish('vlan', 'Choose which port forwards this frame, then check.',
                       {'ports': [dict(p) for p in _VLAN_PORTS],
                        'frame': 'VLAN 10 frame, destination MAC is on port 2',
                        'choices': ['Port 2', 'Port 3', 'Flood every port'], 'answer': 'Port 2'},
                       {'answer': 'Port 2'})
    if kind == 'cable':
        shape, name, caption = _pick(_CABLES, key)
        return _finish('cable', 'Name the connector drawn here, then check.',
                       {'shape': shape, 'caption': caption, 'choices': list(_CABLE_CHOICES), 'answer': name},
                       {'answer': name})
    if kind == 'shell':
        spec = dict(_pick(_SHELLS, key))
        return _finish('shell', 'Run the safe command, read the output, then answer the check.',
                       spec, {'command': spec['expect'], 'answer': spec['answer']})
    if kind == 'cia':
        return _classifier('cia', key, _CIA,
                           ('Confidentiality', 'Integrity', 'Availability'),
                           'Classify each case as confidentiality, integrity, or availability.')
    if kind in ('match', 'pairs', 'classify'):
        grouped = _sort_of(widget)
        if not grouped:
            return _choose(entry, key)
        names, items = grouped
        text = ('Sort one card at a time into the right pile, then check.' if kind == 'pairs'
                else 'Match each term to the group it belongs in, then check.' if kind == 'match'
                else 'Sort each item into the matching group, then check.')
        return _grouped(kind, names, items, text)
    if kind in ('sequence', 'trace', 'troubleshoot'):
        steps = _steps_of(widget) or _steps_from_r3(entry)
        if steps and kind == 'trace' and len(steps) < 5:
            kind = 'sequence'
        if steps and kind == 'sequence' and len(steps) >= 5:
            kind = 'trace'
        if not steps:
            return _choose(entry, key)
        if kind == 'troubleshoot':
            return _order_cfg('troubleshoot', steps, key, 'Put the troubleshooting steps in order, then check.')
        if kind == 'trace':
            return _order_cfg('trace', steps, key, 'Tap the steps in the order this concept uses, then check.')
        return _order_cfg('sequence', steps, key, 'Put these steps in the order this concept uses, then check.')
    if kind == 'hash':
        return _finish('hash', 'Change one character and confirm the teaching hash changes.',
                       {'start': 'backup-report'}, {'changed': True})
    if kind == 'phish':
        spec = _pick(_PHISH, key)
        clues = [{'id': i, 'text': t, 'real': real} for i, t, real in spec['clues']]
        return _finish('phish', 'Flag only the real phishing clues, then check.',
                       {'sender': spec['from'], 'subject': spec['subject'], 'body': spec['body'], 'clues': clues},
                       {'flags': [c['id'] for c in clues if c['real']]})
    if kind == 'logs':
        lines = [{'id': i, 'sev': sev, 'src': src, 'text': text} for i, sev, src, text, _hit in _LOGS]
        answer = next(i for i, sev, src, text, hit in _LOGS if hit)
        return _finish('logs', 'Filter the lines and select the failed sign-in.',
                       {'lines': lines, 'answerId': answer}, {'pick': answer})
    if kind == 'choose':
        return _choose(entry, key)
    return _choose(entry, key)


_CACHE = {}


def sim_for(entry):
    """Widget config for one ladder section, or None when the entry is not a concept section."""
    if not entry or entry.get('type') != 'section':
        return None
    key = (entry.get('course'), entry.get('label'), entry.get('sid'))
    if key not in _CACHE:
        _CACHE[key] = _build(entry)
    return _CACHE[key]


def mapped_sections():
    """Every concept section on the main ladder, with its widget config."""
    from curriculum_v2 import ladder as LD
    out = {}
    for key, entry in LD.ladder().items():
        if entry.get('type') != 'section':
            continue
        out[key] = sim_for(entry)
    return out


def coverage():
    """(by_course Counter-like dict, by_type dict)."""
    by_course, by_type = {}, {}
    for (course, _label, _sid), cfg in mapped_sections().items():
        by_course[course] = by_course.get(course, 0) + 1
        by_type[cfg['type']] = by_type.get(cfg['type'], 0) + 1
    return by_course, by_type


def validate_config(cfg, where=''):
    """Return a list of problems. Empty means the config can render."""
    errs = []
    prefix = f'{where}: ' if where else ''
    if not isinstance(cfg, dict):
        return [prefix + 'config is not an object']
    kind = cfg.get('type')
    if kind not in TYPES:
        errs.append(prefix + f'unknown widget type {kind!r}')
        return errs
    instr = cfg.get('instruction') or ''
    n = len(words(instr))
    if not 1 <= n <= 25:
        errs.append(prefix + f'instruction has {n} words')
    low = instr.lower()
    for bad in ('ciwt', 'not built yet', 'soc 2', 'soc2', 'hecvat'):
        if bad in low:
            errs.append(prefix + f'instruction contains {bad!r}')
    params, goal = cfg.get('params') or {}, cfg.get('goal') or {}
    if not isinstance(params, dict) or not isinstance(goal, dict):
        errs.append(prefix + 'params and goal must be objects')
        return errs
    need_p, need_g = _REQUIRED[kind]
    for field in need_p:
        if field not in params:
            errs.append(prefix + f'params.{field} missing')
    for field in need_g:
        if field not in goal:
            errs.append(prefix + f'goal.{field} missing')
    if kind == 'troubleshoot':
        mode = params.get('mode')
        if mode == 'order':
            if len(params.get('steps') or []) < 3 or params.get('start') == params.get('steps'):
                errs.append(prefix + 'order sim needs 3+ steps shown out of order')
            if goal.get('order') != params.get('steps'):
                errs.append(prefix + 'order goal must match the steps')
        elif mode == 'sort':
            items = params.get('items') or []
            if len(params.get('buckets') or []) < 2 or len(items) < 4:
                errs.append(prefix + 'sort sim needs 2 groups and 4 items')
        else:
            errs.append(prefix + f'unknown troubleshoot mode {mode!r}')
    if kind == 'subnet' and params.get('startPrefix') == goal.get('prefix'):
        errs.append(prefix + 'subnet slider must not start on the answer')
    if kind in ('dora', 'sequence', 'trace') and params.get('start') == goal.get('order'):
        errs.append(prefix + 'sequence must not start in the solved order')
    if kind == 'choose' and params.get('answer') not in (params.get('options') or []):
        errs.append(prefix + 'choose answer must be one of the options')
    if kind in ('match', 'pairs', 'classify'):
        items = params.get('items') or []
        if len(params.get('buckets') or []) < 2 or len(items) < 4:
            errs.append(prefix + 'group sim needs 2 groups and 4 items')
    if kind == 'shell':
        expect = params.get('expect')
        if expect not in (params.get('commands') or {}):
            errs.append(prefix + 'shell expect command has no simulated output')
    if kind == 'phish':
        flags = set(goal.get('flags') or [])
        real = {c['id'] for c in params.get('clues') or [] if c.get('real')}
        if flags != real or not flags:
            errs.append(prefix + 'phish goal must be exactly the real clues')
    return errs
