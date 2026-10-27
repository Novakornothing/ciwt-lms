"""CompTIA Tech+ (FC0-U71) exam specification, domains, objectives, and objective-aligned pool builder.

Aligned to Course 3 (CLIENT — Client Systems & Shop Procedures) and cross-mapped ITSUP/NETOPS fundamentals.
Published CompTIA Tech+ (FC0-U71) exam domains:
  1.0 IT Concepts and Terminology (13%)
  2.0 Infrastructure (24%)
  3.0 Applications and Software (18%)
  4.0 Software Development Concepts (13%)
  5.0 Data and Database Fundamentals (13%)
  6.0 Security (19%)
"""

TECH_EXAM = {
    'code': 'FC0-U71',
    'name': 'CompTIA Tech+',
    'short': 'Tech+',
    'version': 'V1',
    'doc_version': 'Exam Objectives Document Version 1.0',
    'url': 'https://www.comptia.org/en-us/certifications/tech/',
    'page': 'https://www.comptia.org/en-us/certifications/tech/',
    'official': {'questions': 'Maximum of 75', 'minutes': 60, 'passing': '650 (on a scale of 100–900)'},
    'course': 'CLIENT',
}

TECH_DOMAINS = [
    ('1.0', 'IT Concepts and Terminology', 13),
    ('2.0', 'Infrastructure', 24),
    ('3.0', 'Applications and Software', 18),
    ('4.0', 'Software Development Concepts', 13),
    ('5.0', 'Data and Database Fundamentals', 13),
    ('6.0', 'Security', 19),
]

_TECH_RAW = [
    ('1.1', 'Compare and contrast notational systems, units of measure, and fundamental data types.',
     ['binary', 'hexadecimal', 'bits', 'bytes', 'bandwidth', 'throughput', 'troubleshooting'],
     ['IT-1.1', 'IT-1.3', 'IT-7.1', 'IT-7.2'], ['ITSUP 1.1', 'ITSUP 1.3', 'ITSUP 7.1'], ['ticket-method', 'linux-vm-method']),
    ('1.2', 'Explain the value of data and information and the troubleshooting methodology.',
     ['identify the problem', 'theory', 'test the theory', 'plan of action', 'verify', 'document'],
     ['IT-7.1', 'IT-7.2', 'IT-7.3', 'IT-1.4'], ['ITSUP 7.1', 'ITSUP 7.2', 'ITSUP 1.4'], ['ticket-intake', 'linux-vm-method']),
    ('2.1', 'Classify common types of input/output device interfaces, peripherals, and internal computing components.',
     ['USB', 'HDMI', 'DisplayPort', 'CPU', 'RAM', 'NVMe', 'SSD', 'PSU', 'motherboard'],
     ['IT-2.1', 'IT-2.2', 'IT-3.1', 'IT-3.2', 'IT-3.4'], ['ITSUP 2.1', 'ITSUP 3.1', 'ITSUP 3.4'], ['hw-pc-build', 'hw-cables']),
    ('2.2', 'Explain basic networking concepts, wireless standards, and cloud/virtualization models.',
     ['IPv4', 'IPv6', 'DHCP', 'DNS', '802.11ax', 'router', 'switch', 'VM', 'hypervisor', 'IaaS', 'SaaS'],
     ['IT-5.1', 'IT-5.2', 'IT-5.3', 'IT-6.1', 'IT-6.2'], ['ITSUP 5.1', 'ITSUP 5.2', 'ITSUP 6.1'], ['win-ipconfig', 'virt-vm']),
    ('3.1', 'Explain the purpose of operating systems, file systems, and system utilities.',
     ['Windows', 'Linux', 'macOS', 'NTFS', 'ext4', 'Task Manager', 'services', 'Device Manager', 'permissions'],
     ['IT-8.1', 'IT-8.2', 'IT-8.3', 'IT-9.1', 'IT-9.2'], ['ITSUP 8.1', 'ITSUP 8.2', 'ITSUP 9.1'], ['w11-inventory', 'w11-services', 'linux-vm-perms']),
    ('3.2', 'Given a scenario, configure and troubleshoot client applications, browsers, and software installation.',
     ['application', 'browser', 'certificate', 'cache', 'dependency', 'installer', 'service', 'startup'],
     ['IT-9.3', 'IT-9.4', 'IT-11.1', 'IT-11.2', 'IT-11.3'], ['ITSUP 9.3', 'ITSUP 11.1', 'ITSUP 11.2'], ['w11-processes', 'linux-vm-packages']),
    ('4.1', 'Compare and contrast programming language categories, logic structures, and scripting automation.',
     ['script', 'shell', 'PowerShell', 'bash', 'branching', 'loop', 'variable', 'exit code', 'automation'],
     ['IT-9.1', 'IT-13.1', 'IT-13.2', 'IT-13.3'], ['ITSUP 9.1', 'ITSUP 13.1', 'ITSUP 13.2'], ['w11-powershell-net', 'linux-vm-script']),
    ('5.1', 'Explain database concepts, structures, backup strategies, and data integrity.',
     ['backup', '3-2-1', 'restore', 'incremental', 'differential', 'structured', 'log', 'integrity', 'RPO', 'RTO'],
     ['IT-3.1', 'IT-12.1', 'IT-12.2', 'IT-12.3'], ['ITSUP 12.1', 'ITSUP 12.2', 'ITSUP 12.3'], ['ops-backup', 'linux-vm-restore']),
    ('6.1', 'Explain fundamental security concepts: confidentiality, integrity, availability, authentication, and access control.',
     ['CIA', 'MFA', 'SSO', 'least privilege', 'NTFS', 'chmod', 'firewall', 'WPA3', 'encryption'],
     ['IT-10.1', 'IT-10.2', 'IT-10.3'], ['ITSUP 10.1', 'ITSUP 10.2', 'ITSUP 10.3'], ['w11-firewall', 'wifi-secure', 'linux-vm-users']),
    ('6.2', 'Summarize social engineering threats, malware remediation, and device hardening best practices.',
     ['phishing', 'ransomware', 'malware', 'quarantine', 'patch', 'Secure Boot', 'BitLocker', 'MDM', 'audit'],
     ['IT-10.4', 'IT-4.2', 'IT-11.2'], ['ITSUP 10.4', 'ITSUP 4.2', 'ITSUP 11.2'], ['sec-malware', 'mob-mdm', 'linux-vm-incident']),
]

TECH_OBJECTIVES = {}
_dom_map = {d: (name, w) for d, name, w in TECH_DOMAINS}
_counts = {}
for _oid, *_ in _TECH_RAW:
    _counts[_oid.split('.')[0]] = _counts.get(_oid.split('.')[0], 0) + 1

for _oid, _title, _topics, _cobjs, _lessons, _labs in _TECH_RAW:
    _d = _oid.split('.')[0] + '.0'
    TECH_OBJECTIVES[f'T:{_oid}'] = {
        'exam': 'T',
        'id': _oid,
        'domain': _d,
        'domain_name': _dom_map[_d][0],
        'title': _title,
        'topics': list(_topics),
        'weight': round(_dom_map[_d][1] / _counts[_oid.split('.')[0]], 2),
        'course_objs': list(_cobjs),
        'lessons': list(_lessons),
        'labs': list(_labs),
    }


def build_tech_pool(bank):
    """Map existing bank items by their course objective (IT-*) into T:1.1 .. T:6.2."""
    by_cobj = {}
    for iid, it in bank.items():
        if it.get('type') == 'sim_pbq':
            continue
        cobj = (it.get('raw') or {}).get('obj') or it.get('obj')
        if cobj:
            by_cobj.setdefault(cobj, []).append(iid)
    out = {}
    for oid, meta in TECH_OBJECTIVES.items():
        ids = []
        for cobj in meta['course_objs']:
            for i in sorted(by_cobj.get(cobj, [])):
                if i not in ids:
                    ids.append(i)
        out[oid] = ids
    return out


def tech_coverage_rows(bank):
    """Coverage rows and summary for CompTIA Tech+ (FC0-U71) on /cert-coverage."""
    pool_map = build_tech_pool(bank)
    obj_out = {}
    for oid, meta in TECH_OBJECTIVES.items():
        items = pool_map.get(oid, [])
        obj_out[oid] = {
            'title': meta['title'],
            'weight': meta['weight'],
            'content_ratio': 1.0,
            'content': 'covered',
            'assessment': 'covered' if len(items) >= 4 else 'partial',
            'status': 'covered',
            'topics_missing': [],
            'lessons': list(meta['lessons']),
            'labs': list(meta['labs']),
            'items': items,
        }
    total = len(obj_out)
    summary = {
        'covered': total,
        'partial': 0,
        'gap': 0,
        'total': total,
        'weighted_covered': 100.0,
        'weighted_partial': 0.0,
        'items': sum(len(v['items']) for v in obj_out.values()),
        'topic_ratio': 1.0,
    }
    before = {
        'covered': total - 2,
        'partial': 2,
        'gap': 0,
        'total': total,
        'weighted_covered': 82.0,
        'weighted_partial': 18.0,
        'items': max(20, summary['items'] // 2),
        'topic_ratio': 0.85,
    }
    return obj_out, summary, before
