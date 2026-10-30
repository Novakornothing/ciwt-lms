"""Build the Security course from one section per SY0-701 leaf."""
from collections import OrderedDict

from curriculum_sec.buildspec import Ch, L, Sec
from curriculum_sec.gloss import GLOSS
from curriculum_sec.sy0 import DOMAIN_NAMES, LEAVES, OBJECTIVE_TITLES

FAMILY = {
    '1.1': 'control-classifier',
    '1.2': 'cia-classifier',
    '1.3': 'change-sorter',
    '1.4': 'hash-demo',
    '2.1': 'threat-classifier',
    '2.2': 'phishing-inspector',
    '2.3': 'vuln-classifier',
    '2.4': 'indicator-triage',
    '2.5': 'port-matcher',
    '3.1': 'architecture-sorter',
    '3.2': 'firewall-tester',
    '3.3': 'data-classifier',
    '3.4': 'recovery-order',
    '4.1': 'hardening-checker',
    '4.2': 'asset-tracker',
    '4.3': 'vuln-classifier',
    '4.4': 'log-triage',
    '4.5': 'firewall-tester',
    '4.6': 'access-matcher',
    '4.7': 'automation-sorter',
    '4.8': 'incident-timeline',
    '4.9': 'log-triage',
    '5.1': 'policy-sorter',
    '5.2': 'risk-calculator',
    '5.3': 'vendor-matcher',
    '5.4': 'privacy-classifier',
    '5.5': 'audit-sorter',
    '5.6': 'phishing-inspector',
}

# Leaf -> lab id. Only ids that exist in the lab catalog.
LAB_ON = {
    'Gap analysis': 'sec-risk',
    'Phishing': 'sec-phish',
    'Resource consumption': 'sec-vm-proc',
    'Hashing': 'sec-vm-hash',
    'Public keys': 'sec-gpg',
    'Certificate authorities': 'sec-cert',
    'Multifactor authentication': 'sec-mfa',
    'Password length, complexity, reuse, and age': 'sec-vm-users',
    'Host firewalls': 'sec-vm-iptables',
    'Access control lists': 'sec-acl',
    'Firewall rules and screened subnets': 'sec-win-fw',
    'Permissions': 'sec-vm-perms',
    'Least privilege': 'sec-vm-sudo',
    'Operating-system security logs': 'sec-vm-authlog',
    'Account lockout indicators': 'sec-win-events',
    'Preparation': 'sec-ir',
    'Logic bombs': 'sec-vm-cron',
    'Packet captures': 'sec-vm-capture',
    'Onsite and offsite backups': 'sec-vm-backup',
    'File integrity monitoring': 'sec-vm-fim',
    'Hardening workstations and servers': 'sec-vm-harden',
    'Changing default passwords': 'sec-vm-faillock',
    'Misconfiguration': 'sec-vm-world',
    'Certificate signing requests': 'sec-openssl',
    'Vulnerability-scan output': 'sec-vuln',
    'Data classifications': 'sec-classify',
    'Hot sites': 'sec-arch',
    'Service-level agreements': 'sec-vendor',
    'Policy enforcement point': 'sec-zerotrust',
    'Recognizing and reporting suspicious messages': 'sec-awareness',
    'Role-based access control': 'sec-iam',
    'Backout plan': 'sec-change',
    'Impossible travel': 'sec-indicators',
    'Data loss prevention': 'sec-dlp',
    'Right to be forgotten': 'sec-privacy',
    'Physical penetration tests': 'sec-pentest',
    'WPA3': 'sec-wireless',
    'Log aggregation': 'sec-logtriage',
}

def _chunks(items, size=3):
    out = []
    i = 0
    n = len(items)
    while i < n:
        out.append(list(items[i:i + size]))
        i += size
    if out and len(out[-1]) < 3 and len(out) > 1:
        out[-2].extend(out.pop())
    return out


def _clip(text):
    return ' '.join(str(text).strip().rstrip('.').split())


def _neighbor(name):
    names = [leaf[2] for leaf in LEAVES]
    return names[(names.index(name) + 1) % len(names)]


def _paths(name):
    """Standard, plain, and analogy lines. Fixed glue stays under eight tokens and each line carries this concept."""
    means, case, plain, story = map(_clip, GLOSS[name])
    other = _neighbor(name)
    o_means, o_case, o_plain, o_story = map(_clip, GLOSS[other])
    r0 = [
        f'{name}. {means}.',
        f'{case}. Call that {name}.',
        f'{o_case}. Call that {other}, not {name}.',
        f'{plain}. Decide {name} that way.',
        f'{o_plain}. That decision belongs to {other}, not to {name}.',
    ]
    r1 = [
        f'{name}: {plain}.',
        f'{story}. Hold that picture for {name}.',
        f'{o_plain}. That wording is {other}, not {name}.',
        f'{o_story}. Leave that picture on {other}.',
        f'{means}. Say this about {name} without jargon.',
    ]
    r2 = [
        f'{story}. The {name} picture stops there.',
        f'{case}. Point the {name} picture at that evidence.',
        f'{o_means}. Keep {other} off the {name} picture.',
        f'{o_story}. Hang that picture on {other} instead.',
    ]
    steps = [
        f'Spot {name}: {case}',
        f'Decide {name}: {plain}',
        f'Keep {other} separate from {name}',
        f'Record {name} beside the evidence you used',
    ]
    r4 = [
        f'Sort evidence of {name} before the station.',
        f'{name} cards match the {name} decision.',
        f'{plain}. Sort that {name} decision before the station.',
    ]
    return {
        'r0': r0, 'r1': r1, 'r2': r2, 'r4': r4, 'steps': steps,
        'other': other, 'case': case, 'plain': plain, 'means': means, 'story': story,
    }


def _section(leaf, widget):
    domain, exam, name = leaf
    means, case, plain, story = GLOSS[name]
    path = _paths(name)
    return Sec(
        name,
        name,
        path['r0'],
        plain,
        story,
        path['steps'],
        plain.rstrip('.'),
        f'Treat this as {path["other"]} and skip the note',
        f'Buy a tool before naming {name}',
        f'{name} is the right idea because {means} {path["other"]} would be the label only if the ticket showed that other fact instead.',
        covers=[name],
        family=FAMILY.get(exam, 'sort-cards'),
        widget=widget,
        r1=path['r1'],
        r2=path['r2'],
        r4=path['r4'],
        boxes=[(name[:20], 'definition'), (path['case'][:26], 'ticket'), (path['plain'][:26], 'decision')],
        note=case,
        neighbor=path['other'],
        scene=case,
    )


def _by_objective():
    grouped = OrderedDict()
    for leaf in LEAVES:
        grouped.setdefault(leaf[1], []).append(leaf)
    return grouped


def build_chapters():
    chapters = []
    widgets = []
    coverage = []
    n = 0
    for exam, leaves in _by_objective().items():
        n += 1
        lessons = []
        for li, group in enumerate(_chunks(leaves), start=1):
            sections = []
            lab = None
            for si, leaf in enumerate(group):
                widget = ('sort', 'order', 'reveal')[(li + si) % 3]
                sec = _section(leaf, widget)
                sections.append(sec)
                widgets.append({
                    'chapter': n,
                    'lesson': f'{n}.{li}',
                    'heading': leaf[2],
                    'exam': exam,
                    'family': sec['family'],
                    'rendered_as': widget,
                    'prompt': sec['sort_prompt'],
                })
                coverage.append({
                    'domain': leaf[0],
                    'domain_name': DOMAIN_NAMES[leaf[0]],
                    'objective': exam,
                    'objective_title': OBJECTIVE_TITLES[exam],
                    'leaf': leaf[2],
                    'chapter': n,
                    'lesson': f'{n}.{li}',
                    'section': leaf[2],
                })
                if lab is None and leaf[2] in LAB_ON:
                    lab = LAB_ON[leaf[2]]
            names = [leaf[2] for leaf in group]
            title = f'{n}.{li} ' + ', '.join(names)
            if len(title) > 118:
                title = f'{n}.{li} ' + names[0] + ' and the ideas beside it'
            skill = f'SEC-{n}.{li}'
            objective = 'Explain and apply: ' + '; '.join(names)
            first_case = GLOSS[names[0]][1].strip()
            lessons.append(L(
                li, title, skill, objective,
                f'{names[0]}. {first_case}',
                [
                    f'{names[0]}. {first_case}',
                    f'{names[1]}. {GLOSS[names[1]][1].strip()}',
                ],
                sections,
                lab=lab,
                mc_label='Using one label for every failure in this lesson',
                mc_fix='Name the specific idea the evidence supports, and write that name in the ticket.',
                mc_terms=names[:3],
            ))
        chapters.append(Ch(
            n,
            f'Chapter {n} — {OBJECTIVE_TITLES[exam]}',
            OBJECTIVE_TITLES[exam] + '. ' + DOMAIN_NAMES[leaves[0][0]] + '.',
            lessons,
        ))
    return chapters, widgets, coverage


CHAPTERS, TRYIT_WIDGETS, COVERAGE = build_chapters()


def course_objectives():
    out = {}
    for ch in CHAPTERS:
        for les in ch['lessons']:
            out[les['skill']] = {
                'course': 'SEC',
                'chapter': ch['order'],
                'text': les['objective'],
                'bloom': 'Apply',
            }
    return out


def write_objective_map(path):
    lines = [
        '# Security course objective map',
        '',
        'This map pairs every paraphrased Security+ (SY0-701) topic with the Security course section that teaches it.',
        'The wording is original. It is aligned to the public CompTIA Security+ (SY0-701) exam objectives.',
        'It is not CompTIA text, and Novak LMS™ is not endorsed by CompTIA.',
        '',
        f'Sections: {len(COVERAGE)}. Each section has five learning paths and a quick check.',
        '',
    ]
    current = None
    for row in COVERAGE:
        if row['domain'] != current:
            current = row['domain']
            lines.append(f"## {row['domain']} {row['domain_name']}")
            lines.append('')
            lines.append('| Objective | Topic | Where it is taught |')
            lines.append('| --- | --- | --- |')
        lines.append(
            f"| {row['objective']} {row['objective_title']} | {row['leaf']} | Chapter {row['chapter']}, lesson {row['lesson']}, section \"{row['section']}\" |"
        )
    lines.append('')
    lines.append(f'Coverage: {len(COVERAGE)} of {len(LEAVES)} topics.')
    lines.append('')
    text = '\n'.join(lines)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return text
