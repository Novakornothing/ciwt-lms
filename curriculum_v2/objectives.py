"""Course learning outcomes (CLOs) and assessed chapter objectives (pass 8).

Chapter objectives are the unit every quiz/test item, lab and rubric maps to. Lesson-level "terminal
objectives" in the lesson pages remain as enabling objectives under these. Bloom levels use the revised
taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create).

CIWT objectives are original. Where an institution wants to show alignment to a published certification
exam objective list, record it as *alignment* in the syllabus; do not copy vendor exam text or items.
"""

CLOS = {
    'ITSUP': [
        ('CLO1', 'Apply workplace safety, ESD and professional communication practices when handling users and equipment.', ['IT-1', 'IT-4.1', 'IT-12']),
        ('CLO2', 'Identify, install and troubleshoot PC, mobile, storage, power and display hardware using a fixed isolation order.', ['IT-2', 'IT-3', 'IT-4']),
        ('CLO3', 'Configure and troubleshoot client networking (IPv4/IPv6, DHCP, DNS, ports, SOHO wireless) using command-line and graphical tools.', ['IT-5', 'IT-13']),
        ('CLO4', 'Install, configure, maintain and recover Windows clients, and perform basic support on Linux and macOS.', ['IT-8', 'IT-9', 'IT-11']),
        ('CLO5', 'Apply endpoint security controls and respond to common security events within support-role limits.', ['IT-10']),
        ('CLO6', 'Use a structured troubleshooting methodology and produce documentation, tickets and change records another technician can act on.', ['IT-6', 'IT-7', 'IT-12']),
    ],
    'NETOPS': [
        ('CLO1', 'Explain network models, IPv4/IPv6 addressing and transport protocols, and calculate subnets.', ['NO-1']),
        ('CLO2', 'Configure and verify switching, VLANs, trunks and physical-layer media.', ['NO-2', 'NO-9']),
        ('CLO3', 'Explain and verify routing, WAN and wireless LAN operation.', ['NO-3', 'NO-9']),
        ('CLO4', 'Troubleshoot core network services: DHCP, DNS, NAT and firewall policy.', ['NO-4']),
        ('CLO5', 'Apply monitoring, management-plane hardening and segmentation practices.', ['NO-5']),
        ('CLO6', 'Diagnose multi-layer network faults with a structured method and document the outcome.', ['NO-6']),
    ],
}

# id -> (chapter, text, bloom)
_IT = [
    ('IT-1.1', 1, 'Classify a support contact as an incident, service request or change and assign impact', 'Apply'),
    ('IT-1.2', 1, 'Apply ESD and electrical-safety procedures before opening equipment, and stop work on safety hazards', 'Apply'),
    ('IT-1.3', 1, 'Write ticket notes as action → result pairs that another technician can verify', 'Create'),
    ('IT-1.4', 1, 'Protect user identity, credentials and privacy during support interactions', 'Apply'),
    ('IT-2.1', 2, 'Identify motherboard form factors, sockets, memory and storage interfaces from physical evidence', 'Remember'),
    ('IT-2.2', 2, 'Explain how UEFI settings (boot order, Secure Boot, memory profiles) affect boot and stability', 'Understand'),
    ('IT-2.3', 2, 'Troubleshoot POST failures and memory configuration using an ordered isolation process', 'Analyze'),
    ('IT-2.4', 2, 'Inventory a running system and reconcile it with the installed hardware', 'Apply'),
    ('IT-3.1', 3, 'Compare HDD, SATA SSD and NVMe storage and select storage for a scenario', 'Understand'),
    ('IT-3.2', 3, 'Explain RAID levels and why RAID is not a backup', 'Understand'),
    ('IT-3.3', 3, 'Troubleshoot power supply, cooling and expansion-card power problems', 'Analyze'),
    ('IT-3.4', 3, 'Isolate display, port and cable faults (USB-C, DisplayPort, HDMI)', 'Analyze'),
    ('IT-4.1', 4, 'Service laptop field-replaceable units safely, including swollen-battery handling', 'Apply'),
    ('IT-4.2', 4, 'Troubleshoot mobile connectivity and managed (MDM) device issues without bypassing policy', 'Analyze'),
    ('IT-4.3', 4, 'Troubleshoot printing along the print path from application to device', 'Analyze'),
    ('IT-5.1', 5, 'Interpret IPv4/IPv6 configuration (address, mask/prefix, gateway, DNS, APIPA) and calculate subnet sizes', 'Apply'),
    ('IT-5.2', 5, 'Relate common ports and protocols to the services and tests they imply', 'Remember'),
    ('IT-5.3', 5, 'Isolate client connectivity faults in a fixed order: link, lease, IP, name, service', 'Analyze'),
    ('IT-5.4', 5, 'Configure SOHO wireless and router security to current practice', 'Apply'),
    ('IT-6.1', 6, 'Explain hypervisors, virtual machines, snapshots and virtual networking', 'Understand'),
    ('IT-6.2', 6, 'Compare cloud service models (SaaS, PaaS, IaaS) and the shared-responsibility split', 'Understand'),
    ('IT-6.3', 6, 'Troubleshoot guest and host virtualization issues and route them to the right owner', 'Analyze'),
    ('IT-7.1', 7, 'Apply a structured troubleshooting methodology from identification to documentation', 'Apply'),
    ('IT-7.2', 7, 'Determine the fault domain of a symptom before choosing a tool', 'Analyze'),
    ('IT-7.3', 7, 'Verify full functionality with the user and hand off with complete notes', 'Evaluate'),
    ('IT-7.4', 7, 'Escalate with a complete evidence package and keep users informed on a stated schedule', 'Apply'),  # pass 9
    ('IT-8.1', 8, 'Plan a Windows installation, upgrade or reset that meets hardware and lifecycle requirements', 'Apply'),
    ('IT-8.2', 8, 'Configure and baseline Windows 11 (accounts, updates, services, firewall) through Settings and CLI', 'Apply'),
    ('IT-8.3', 8, 'Use Windows repair tools (SFC, DISM, recovery environment, Event Viewer) before rebuilding', 'Apply'),
    ('IT-8.4', 8, 'Manage Windows in a domain: Group Policy, profiles and authentication dependencies', 'Analyze'),
    ('IT-9.1', 9, 'Perform basic Linux administration from the command line (navigation, permissions, services, networking)', 'Apply'),
    ('IT-9.2', 9, 'Support macOS and managed Apple devices using equivalent tools and policies', 'Apply'),
    ('IT-9.3', 9, 'Distinguish access and entitlement problems from technical faults in mixed environments', 'Analyze'),
    ('IT-9.4', 9, 'Move and share files between Windows, macOS and Linux using compatible file systems and protocols', 'Apply'),  # pass 9
    ('IT-10.1', 10, 'Apply authentication and least-privilege controls (MFA, separate admin accounts, password policy)', 'Apply'),
    ('IT-10.2', 10, 'Respond to malware and phishing reports within the support role: contain, record, escalate', 'Apply'),
    ('IT-10.3', 10, 'Apply endpoint protections: encryption, removable-media control, patching, secure disposal', 'Apply'),
    ('IT-10.4', 10, 'Preserve evidence and logs and protect integrity during incident handling', 'Understand'),
    ('IT-11.1', 11, 'Recognise software failure patterns and scope them (one app, one PC, many users)', 'Analyze'),
    ('IT-11.2', 11, 'Choose between repair, in-place and rebuild with backup and change control', 'Evaluate'),
    ('IT-11.3', 11, 'Diagnose OS and resource problems (processes, memory, storage latency) with system tools', 'Analyze'),
    ('IT-12.1', 12, 'Follow change management: approvals, windows, rollback and documentation', 'Apply'),
    ('IT-12.2', 12, 'Apply privacy, acceptable-use and professional-conduct policies', 'Apply'),
    ('IT-12.3', 12, 'Plan and verify backup and recovery, distinguishing backup, RAID and snapshots', 'Evaluate'),
    ('IT-13.1', 13, 'Collect system and network evidence from the Windows command line and PowerShell', 'Apply'),
    ('IT-13.2', 13, 'Resolve a client name-resolution or lease fault end to end in a lab VM', 'Apply'),
    ('IT-13.3', 13, 'Use process, netsh and Settings views to confirm a state before changing it', 'Apply'),
]
_NO = [
    ('NO-1.1', 1, 'Map protocols, devices and symptoms to OSI/TCP-IP layers and explain encapsulation', 'Understand'),
    ('NO-1.2', 1, 'Calculate IPv4 subnets and identify special IPv4 and IPv6 address types', 'Apply'),
    ('NO-1.3', 1, 'Compare TCP and UDP and associate services with ports', 'Understand'),
    ('NO-2.1', 2, 'Explain switch forwarding, loops and Spanning Tree protections', 'Understand'),
    ('NO-2.2', 2, 'Configure and troubleshoot VLANs, trunks and inter-VLAN routing', 'Apply'),
    ('NO-2.3', 2, 'Select copper, fibre and PoE options and the right physical-layer test tool', 'Evaluate'),
    ('NO-3.1', 3, 'Explain route selection and routing sources (connected, static, OSPF, BGP, default)', 'Understand'),
    ('NO-3.2', 3, 'Compare WAN access and site-to-site options and gather evidence for a provider fault', 'Analyze'),
    ('NO-3.3', 3, 'Design and troubleshoot WLAN channels, coverage and security', 'Analyze'),
    ('NO-4.1', 4, 'Troubleshoot DHCP across subnets (scope, relay, rogue servers)', 'Analyze'),
    ('NO-4.2', 4, 'Troubleshoot DNS resolution, record types and caching', 'Analyze'),
    ('NO-4.3', 4, 'Evaluate NAT and firewall rules, states and zones', 'Evaluate'),
    ('NO-5.1', 5, 'Interpret monitoring data: SNMP, syslog, flows, counters and baselines', 'Analyze'),
    ('NO-5.2', 5, 'Harden the management plane of network devices', 'Apply'),
    ('NO-5.3', 5, 'Design segmentation and apply least privilege / zero trust between zones', 'Create'),
    ('NO-6.1', 6, 'Diagnose faults from symptom patterns and scope', 'Analyze'),
    ('NO-6.2', 6, 'Run an incident with a structured method, time boxes, status updates and rollback', 'Apply'),
    ('NO-6.3', 6, 'Verify fixes and maintain network documentation', 'Evaluate'),
    ('NO-9.1', 9, 'Configure switch VLANs, access ports and trunks from the CLI and verify with show commands', 'Apply'),
    ('NO-9.2', 9, 'Configure router interfaces, connected/default routes and inter-VLAN routing, and save the configuration', 'Apply'),
]

OBJECTIVES = {}
for _id, _ch, _t, _b in _IT:
    OBJECTIVES[_id] = {'course': 'ITSUP', 'chapter': _ch, 'text': _t, 'bloom': _b}
for _id, _ch, _t, _b in _NO:
    OBJECTIVES[_id] = {'course': 'NETOPS', 'chapter': _ch, 'text': _t, 'bloom': _b}

# CLIENT chapters 1–6 are ITSUP chapters 8–13.
CLIENT_CHAPTER_TO_ITSUP = {n: n + 7 for n in range(1, 7)}


def objectives_for(course_code, chapter=None):
    code = 'ITSUP' if course_code == 'CLIENT' else course_code
    rows = [(k, v) for k, v in OBJECTIVES.items() if v['course'] == code]
    if course_code == 'CLIENT':
        rows = [(k, v) for k, v in rows if v['chapter'] >= 8]
        if chapter is not None:
            chapter = CLIENT_CHAPTER_TO_ITSUP.get(chapter, -1)
    if chapter is not None:
        rows = [(k, v) for k, v in rows if v['chapter'] == chapter]
    return rows


def clos_for(course_code):
    if course_code == 'CLIENT':
        return [
            ('CLO1', 'Install, configure, maintain and recover Windows clients, and support Linux and macOS users.', ['IT-8', 'IT-9']),
            ('CLO2', 'Apply endpoint security controls and respond to security events within support-role limits.', ['IT-10']),
            ('CLO3', 'Diagnose software and OS faults and choose repair, in-place or rebuild with change control.', ['IT-11']),
            ('CLO4', 'Follow operational procedures: change management, privacy and backup/recovery.', ['IT-12']),
            ('CLO5', 'Collect evidence and resolve client faults from the Windows command line in a lab VM.', ['IT-13']),
        ]
    return CLOS.get(course_code, [])
