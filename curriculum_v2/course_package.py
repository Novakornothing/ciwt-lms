"""College / classroom course package (pass 8).

Pure data plus small builders: syllabus, credit-hour mapping, grading, policy placeholders, pacing
(16-week semester, 8-week accelerated, 10-week quarter), instructor lesson plans, standard-format labs,
rubrics, exam blueprints, instructor answer keys, glossary and accessibility statement.

Fields in [square brackets] are for the institution to fill in. Nothing here claims accreditation,
articulation or vendor affiliation: this is original curriculum, not a vendor exam product.
"""
from gradebook import CATEGORIES, DEFAULT_SCALE, DEFAULT_WEIGHTS

from curriculum_v2.objectives import OBJECTIVES, clos_for
from curriculum_v2.objectives import objectives_for as _objectives_for


def objectives_for(code, chapter=None):
    """Lesson objectives as dicts: code, text, bloom, chapter."""
    return [dict(v, code=k) for k, v in _objectives_for(code, chapter)]

DISCLAIMER = ('Original CIWT curriculum. Not affiliated with, endorsed by, or a substitute for any vendor '
              'certification exam. Where objectives are compared with publicly published exam objective '
              'domains, that comparison is an alignment aid only.')

CREDIT_HOUR_SOURCE = ('U.S. federal definition of a credit hour, 34 CFR 600.2: one hour of classroom or direct '
                      'faculty instruction plus at least two hours of out-of-class work each week for about fifteen '
                      'weeks per semester hour (ten to twelve weeks per quarter hour), or an equivalent amount of '
                      'work for laboratory and other academic activities as established by the institution.')

COURSES = {
    'ITSUP': {
        'title': 'IT Support Fundamentals',
        'catalog_number': '[e.g., CIT 110]',
        'description': (
            'An introduction to supporting computer users and their devices in a workplace. Students practise safe '
            'handling of hardware, identify and replace PC components, configure and troubleshoot Windows, Linux and '
            'macOS clients, isolate network faults on client devices, apply endpoint security practices, and '
            'document work in tickets. Weekly hands-on labs use browser-based simulators and, where available, '
            'physical equipment or virtual machines. The course prepares students for entry-level help-desk and '
            'desktop-support roles and for further study in networking and systems administration.'),
        'prerequisites': 'None. Recommended: basic computer literacy (files, folders, web browser). [Institution: placement or co-requisite rules]',
        'credits': {'total': 4, 'lecture': 3, 'lab': 1, 'lecture_contact_per_week': 3, 'lab_contact_per_week': 2,
                    'note': 'A 3-credit variant (2 lecture + 1 lab) is possible by moving Chapter 13 reps and some '
                            'lesson reading out of class; see the pacing notes.'},
        'skills_exams': ('Skills Midterm — IT Support', 'Skills Final — IT Support'),
        'tests': ('IT Support Knowledge Test A', 'IT Support Knowledge Test B', 'IT Support Knowledge Test C'),
    },
    'NETOPS': {
        'title': 'Network Operations',
        'catalog_number': '[e.g., CIT 140]',
        'description': (
            'How enterprise networks are built, run and repaired. Students map protocols and faults to network '
            'layers, subnet IPv4 and recognise IPv6 address types, configure VLANs, trunks and routing on switch and '
            'router command lines, troubleshoot DHCP, DNS, NAT and firewall policy, interpret monitoring data, harden '
            'network devices and design segmentation. A capstone applies a structured method to multi-fault incidents.'),
        'prerequisites': 'IT Support Fundamentals or equivalent experience (client IP configuration, ping/ipconfig). [Institution: confirm]',
        'credits': {'total': 4, 'lecture': 3, 'lab': 1, 'lecture_contact_per_week': 3, 'lab_contact_per_week': 2,
                    'note': 'Chapter 9 (CLI lab track) is designed to run in the weekly lab session alongside Chapters 2–4.'},
        'skills_exams': ('Skills Midterm — Network Operations', 'Skills Final — Network Operations'),
        'tests': ('Network Operations Knowledge Test A', 'Network Operations Knowledge Test B', 'Network Operations Knowledge Test C'),
    },
    'CLIENT': {
        'title': 'Client Systems Support',
        'catalog_number': '[e.g., CIT 115]',
        'description': (
            'A focused course on supporting Windows, Linux and macOS clients: installation and configuration, repair '
            'tools, cross-platform access, endpoint security, software troubleshooting and operational procedures, '
            'with a Windows command-line and VM lab track. Built from IT Support Fundamentals Chapters 8–13.'),
        'prerequisites': 'Basic computer literacy. [Institution: confirm whether IT Support Fundamentals is required]',
        'credits': {'total': 3, 'lecture': 2, 'lab': 1, 'lecture_contact_per_week': 2, 'lab_contact_per_week': 2,
                    'note': 'Fits an 8-week term at double weekly contact hours.'},
        'skills_exams': ('Skills Midterm — Client Systems', 'Skills Final — Client Systems'),
        'tests': (),
    },
}


def credit_mapping(code):
    """Contact and out-of-class hours for a 15-week semester (plus a final-exam week)."""
    c = COURSES[code]['credits']
    weeks = 15
    lecture = c['lecture_contact_per_week'] * weeks
    lab = c['lab_contact_per_week'] * weeks
    out_of_class = c['lecture'] * 2 * weeks
    return {
        'credits': c['total'], 'lecture_credits': c['lecture'], 'lab_credits': c['lab'],
        'lecture_hours': lecture, 'lab_hours': lab, 'contact_hours': lecture + lab,
        'out_of_class_hours': out_of_class, 'weeks': weeks, 'note': c['note'],
        'basis': (f"{c['lecture']} lecture credits × 1 contact hour/week and {c['lab']} lab credit × "
                  f"{c['lab_contact_per_week']} contact hours/week over {weeks} weeks, plus about 2 hours of out-of-class "
                  'work per lecture credit per week. Lab contact hours per credit vary by institution (commonly 2–3).'),
        'source': CREDIT_HOUR_SOURCE,
    }


def clos(code):
    """Course learning outcomes as dicts with the lesson objectives that support each one."""
    src = clos_for(code) or []
    out = []
    for clo_code, text, prefixes in src:
        objs = [k for k in OBJECTIVES if any(k == p or k.startswith(p + '.') for p in prefixes)]
        out.append({'code': clo_code, 'text': text, 'objectives': objs})
    return out


# ------------------------------------------------------------------------------------------- grading
def grading(weights=None, pass_mark=80, scale=None, policy='best', late_per_day=0, late_max=0):
    """Grading policy text tied to the gradebook categories. Pass per-section settings to customise."""
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update(weights)
    labels = dict(CATEGORIES)
    rows = [{'key': k, 'label': labels[k], 'weight': w.get(k, 0), 'what': {
        'tests': 'Knowledge tests (multiple choice, scenario-based, timed). Forms A, B and C.',
        'skills': 'Skills exams (practical stations scored against the skills rubric): midterm and final.',
        'quizzes': 'Chapter checks (practice). Weight 0 by default: they give feedback and study tips without grade pressure.',
        'labs': 'Live labs (simulated terminals, desktops and activities, auto-graded; classroom labs signed off by the instructor). '
                'Weight 0 by default: formative practice unless the section gives them a weight.',  # labs branch
    }.get(k, '')} for k, _ in CATEGORIES]
    policy_text = {'best': 'the best attempt counts', 'latest': 'the most recent attempt counts',
                   'average': 'attempts are averaged', 'first': 'the first attempt counts'}.get(policy, policy)
    late = ('No automatic late penalty is configured.' if not late_per_day else
            f'Late submissions lose {late_per_day} points per day, up to {late_max} points.')
    return {
        'categories': rows, 'pass_mark': pass_mark, 'scale': list(scale or DEFAULT_SCALE),
        'attempt_policy': policy_text, 'late': late,
        'notes': [
            'Category weights, attempt policy, pass mark, letter scale and late rules are set per class section '
            'in the LMS gradebook settings; this syllabus shows the section’s current values.',
            'Lab completion is tracked in the LMS as formative practice; the skills exams assess the same stations summatively.',
            '[Institution/instructor: participation, discussion or project components, if any, and how they map to the categories]',
        ],
    }


# ------------------------------------------------------------------------------------------- policies
POLICY_FIELDS = [
    # key, label, placeholder shown until the instructor fills it in
    ('attendance', 'Attendance and participation',
     '[Institution: attendance policy, including how absences from lab sessions are made up. Labs build on each '
     'other, so missed lab time should be made up within one week using the LMS simulators.]'),
    ('late_work', 'Late work and make-up exams',
     '[Instructor: late-work rules. The LMS can apply an automatic per-day penalty with a cap and grace period.]'),
    ('academic_integrity', 'Academic integrity',
     '[Institution: academic integrity policy and reporting procedure. Knowledge tests and skills exams are '
     'individual work unless the instructor states otherwise; lab work may be collaborative but each ticket note '
     'is written by the student who submits it.]'),
    ('ai_use', 'Use of AI tools',
     '[Instructor: AI-use policy for this section, e.g., permitted for explaining concepts and checking writing; '
     'not permitted during knowledge tests or skills exams; any AI assistance in submitted work must be disclosed.]'),
    ('accessibility', 'Accessibility and accommodations',
     '[Institution: disability services office, contact details and accommodation procedure.] The LMS supports '
     'keyboard navigation, screen readers, light/dark themes, text narration of lessons and extended test time '
     'when an instructor sets it.'),
    ('safety', 'Lab safety',
     'Follow the course ESD, electrical and battery safety procedures (Chapter 1 and 4). Students do not open power '
     'supplies or service swollen batteries. [Institution: lab rules, PPE, incident reporting]'),
    ('communication', 'Communication and response times',
     '[Instructor: preferred contact method, expected response time and office hours]'),
    ('nondiscrimination', 'Non-discrimination and student support',
     '[Institution: required statements (e.g., non-discrimination, Title IX or local equivalent, basic needs, counselling)]'),
    ('grade_disputes', 'Grade questions and appeals', '[Institution: grade appeal procedure and deadlines]'),
]

SECTION_FIELDS = [
    # key, label, placeholder
    ('institution', 'Institution', '[Institution name]'),
    ('department', 'Department / program', '[Department or program]'),
    ('term', 'Term', '[Term and year]'),
    ('meeting_times', 'Meeting times and location', '[Days, times, room or online link]'),
    ('lab_times', 'Lab sessions', '[Lab days, times, room]'),
    ('instructor_name', 'Instructor', '[Instructor name]'),
    ('instructor_contact', 'Contact and office hours', '[Email, office, office hours]'),
    ('course_number', 'Course number and section', '[Catalog number and section]'),
    ('materials', 'Required materials', 'No textbook purchase required: course content is in the LMS. '
     '[Optional: lab kit, USB drive, headset for narration]'),
]


# ------------------------------------------------------------------------------------------- pacing
# Each week: (week, chapters/topics, lab session, assessments). Chapter numbers refer to the course's own chapters.
PACING = {
    'ITSUP': {
        16: [
            (1, 'Ch 1 Professional foundations & workplace safety (1.1–1.3)', 'ticket-intake', 'Syllabus quiz (ungraded)'),
            (2, 'Ch 1 (1.4–1.5); Ch 2 Motherboards & firmware (2.1–2.2)', 'ticket-intake; hw-board', 'Chapter 1 check'),
            (3, 'Ch 2 CPU, memory, POST, inventory (2.3–2.6)', 'hw-board', 'Chapter 2 check'),
            (4, 'Ch 3 Storage, RAID/backup, power, ports', 'w11-disk; gui-devices', 'Chapter 3 check'),
            (5, 'Ch 4 Laptops, mobile devices & printing', 'Classroom lab CL-4 (print path & laptop FRU)', 'Chapter 4 check'),
            (6, 'Ch 5 Client networking (5.1–5.3)', 'win-ipconfig; win-dns-break; win-arp; win-route', ''),
            (7, 'Ch 5 Wireless hardening & capstone (5.4–5.5)', 'w11-wlan; gui-ethernet; win-netstat', 'Chapter 5 check'),
            (8, 'Ch 6 Virtualisation & cloud', 'Classroom lab CL-6 (build and snapshot a VM)', 'Chapter 6 check'),
            (9, 'Ch 7 Troubleshooting methodology; review', 'win-full-triage; CL-7 (staged-fault drills)', 'Midterm: Knowledge Test A + Skills Midterm'),
            (10, 'Ch 8 Windows installation & configuration', 'gui-about; gui-update; CL-8 (recovery ladder)', 'Chapter 7 & 8 checks'),
            (11, 'Ch 9 Linux, macOS & cross-platform', 'Classroom lab CL-9 (Linux CLI & permissions)', 'Chapter 9 check'),
            (12, 'Ch 10 Endpoint security', 'gui-accounts; CL-10 (posture check & tabletop)', 'Chapter 10 check'),
            (13, 'Ch 11 Software troubleshooting', 'w11-processes; CL-11 (slow PC & clean boot)', 'Chapter 11 check; Knowledge Test B (practice or retake)'),
            (14, 'Ch 12 Operational procedures & integrated capstone', 'Classroom lab CL-12 (change request & recovery drill)', 'Chapter 12 check'),
            (15, 'Ch 13 Windows CLI & VM lab track (reps); review', 'CL-13 (PowerShell evidence); Ch 13 lab set', 'Chapter 13 check'),
            (16, 'Final exam week', 'Skills Final stations', 'Final: Knowledge Test C + Skills Final'),
        ],
        8: [
            (1, 'Ch 1–2', 'ticket-intake; hw-board', 'Chapter 1–2 checks'),
            (2, 'Ch 3–4', 'w11-disk; gui-devices; CL-4', 'Chapter 3–4 checks'),
            (3, 'Ch 5', 'Ch 5 lab set', 'Chapter 5 check'),
            (4, 'Ch 6–7; review', 'CL-6; win-full-triage', 'Midterm: Knowledge Test A + Skills Midterm'),
            (5, 'Ch 8–9', 'gui-about; gui-update; CL-9', 'Chapter 8–9 checks'),
            (6, 'Ch 10–11', 'gui-accounts; w11-firewall; w11-processes', 'Chapter 10–11 checks'),
            (7, 'Ch 12–13', 'CL-12; CL-13; Ch 13 lab set', 'Chapter 12–13 checks'),
            (8, 'Review and finals', 'Skills Final stations', 'Final: Knowledge Test C + Skills Final'),
        ],
        10: [
            (1, 'Ch 1', 'ticket-intake', 'Chapter 1 check'),
            (2, 'Ch 2–3', 'hw-board; w11-disk; gui-devices', 'Chapter 2–3 checks'),
            (3, 'Ch 4–5 (5.1–5.3)', 'CL-4; win-ipconfig; win-dns-break', 'Chapter 4 check'),
            (4, 'Ch 5 (5.4–5.5); Ch 6', 'w11-wlan; CL-6', 'Chapter 5–6 checks'),
            (5, 'Ch 7; review', 'win-full-triage', 'Midterm: Knowledge Test A + Skills Midterm'),
            (6, 'Ch 8', 'gui-about; gui-update; w11-services', 'Chapter 7–8 checks'),
            (7, 'Ch 9–10', 'CL-9; gui-accounts; w11-firewall', 'Chapter 9–10 checks'),
            (8, 'Ch 11–12', 'w11-processes; CL-12', 'Chapter 11–12 checks'),
            (9, 'Ch 13; review', 'CL-13; Ch 13 lab set', 'Chapter 13 check; Knowledge Test B (practice)'),
            (10, 'Finals', 'Skills Final stations', 'Final: Knowledge Test C + Skills Final'),
        ],
    },
    'NETOPS': {
        16: [
            (1, 'Ch 1 OSI/TCP-IP, encapsulation', 'win-ipconfig; CLI orientation (9.1)', ''),
            (2, 'Ch 1 IPv4/IPv6 addressing, TCP/UDP & ports', 'win-arp; win-netstat; subnetting drills', 'Chapter 1 check'),
            (3, 'Ch 2 Switching & STP', 'sw-show-ver; sw-mac-table; sw-int-status', ''),
            (4, 'Ch 2 VLANs, trunks; copper/fibre/PoE', 'sw-vlan-access; sw-trunk-basics (9.2)', 'Chapter 2 check'),
            (5, 'Ch 3 Routing', 'rtr-gateway; rtr-two-interfaces (9.3)', ''),
            (6, 'Ch 3 WAN & wireless', 'rtr-default-route; rtr-trace; inter-VLAN routing (9.4)', 'Chapter 3 check'),
            (7, 'Ch 4 DHCP & DNS', 'win-dhcp-renew; win-dns-break', ''),
            (8, 'Ch 4 NAT & firewall; review', 'Ch 9 capstone (9.5–9.6)', 'Chapter 4 & 9 checks; Skills Midterm'),
            (9, 'Midterm', 'sw-vlan-and-trunk practice', 'Knowledge Test A'),
            (10, 'Ch 5 Monitoring signals', 'sw-int-status; syslog/SNMP reading exercise', ''),
            (11, 'Ch 5 Hardening & segmentation', 'sw-port-security; sw-banner', 'Chapter 5 check'),
            (12, 'Ch 6 Pattern library', 'win-full-triage', ''),
            (13, 'Ch 6 Method under pressure', 'Incident simulation (instructor-run)', 'Knowledge Test B (practice or retake)'),
            (14, 'Ch 6 Verification & documentation', 'rtr-edge-complete', 'Chapter 6 check'),
            (15, 'Full capstone scenario; review', 'sw-vlan-and-trunk; rtr-edge-complete', ''),
            (16, 'Final exam week', 'Skills Final stations', 'Final: Knowledge Test C + Skills Final'),
        ],
        8: [
            (1, 'Ch 1', 'win-ipconfig; win-arp; CLI orientation', 'Chapter 1 check'),
            (2, 'Ch 2', 'Switch lab set; 9.2', 'Chapter 2 check'),
            (3, 'Ch 3', 'Router lab set; 9.3–9.4', 'Chapter 3 check'),
            (4, 'Ch 4; review', '9.5–9.6; win-dns-break', 'Chapter 4 & 9 checks; Midterm: Test A + Skills Midterm'),
            (5, 'Ch 5', 'sw-port-security; sw-banner', 'Chapter 5 check'),
            (6, 'Ch 6 (6.1–6.2)', 'win-full-triage; incident simulation', ''),
            (7, 'Ch 6 (6.3–6.4); review', 'rtr-edge-complete', 'Chapter 6 check'),
            (8, 'Finals', 'Skills Final stations', 'Final: Test C + Skills Final'),
        ],
        10: [
            (1, 'Ch 1', 'win-ipconfig; win-arp; CLI orientation', 'Chapter 1 check'),
            (2, 'Ch 2', 'Switch lab set; 9.2', 'Chapter 2 check'),
            (3, 'Ch 3', 'Router lab set; 9.3', 'Chapter 3 check'),
            (4, 'Ch 4 (DHCP, DNS)', '9.4; win-dhcp-renew', ''),
            (5, 'Ch 4 (NAT, firewall); review', '9.5–9.6', 'Chapter 4 & 9 checks; Midterm: Test A + Skills Midterm'),
            (6, 'Ch 5', 'sw-port-security; sw-banner; sw-int-status', 'Chapter 5 check'),
            (7, 'Ch 6 (6.1–6.2)', 'win-full-triage', ''),
            (8, 'Ch 6 (6.3–6.4)', 'rtr-edge-complete', 'Chapter 6 check'),
            (9, 'Review', 'Station practice', 'Knowledge Test B (practice)'),
            (10, 'Finals', 'Skills Final stations', 'Final: Test C + Skills Final'),
        ],
    },
    'CLIENT': {
        8: [
            (1, 'Ch 1 Windows installation & configuration', 'gui-about; gui-update', ''),
            (2, 'Ch 1 repair tools; Ch 2 Linux & macOS', 'w11-services; CL-9', 'Chapter 1 check'),
            (3, 'Ch 2 cross-platform; Ch 3 Endpoint security', 'gui-accounts; w11-firewall', 'Chapter 2 check'),
            (4, 'Ch 3; review', 'w11-inventory', 'Chapter 3 check; Skills Midterm'),
            (5, 'Ch 4 Software troubleshooting', 'w11-processes; CL-11', 'Chapter 4 check'),
            (6, 'Ch 5 Operational procedures', 'CL-12', 'Chapter 5 check'),
            (7, 'Ch 6 Windows CLI & VM lab track', 'CL-13; Ch 6 lab set', 'Chapter 6 check'),
            (8, 'Review and final', 'Skills Final stations', 'Skills Final'),
        ],
        16: None,  # same content at half the weekly contact hours: each 8-week row spans two weeks
        10: None,
    },
}

PACING_NOTES = {
    16: 'Fifteen instructional weeks plus a final-exam week. Typical meeting pattern: lecture/discussion 3 hours and lab 2 hours per week.',
    8: 'Accelerated: double the weekly contact time. Students should expect about twice the weekly out-of-class work.',
    10: 'Quarter term: about 1.5× the weekly contact time of a semester section.',
}


def pacing(code, weeks):
    rows = PACING.get(code, {}).get(weeks)
    if rows is None and code == 'CLIENT':
        base = PACING['CLIENT'][8]
        if weeks == 16:
            rows = [(w, t if w % 2 else t + ' (continued)', l, a if not w % 2 else '') for w, (t, l, a) in
                    ((i * 2 + j + 1, (r[1], r[2], r[3])) for i, r in enumerate(base) for j in (0, 1))]
        elif weeks == 10:
            rows = [(r[0], r[1], r[2], r[3]) for r in base[:3]] + [(4, 'Ch 3 (continued)', 'Station practice', '')] + \
                   [(r[0] + 1, r[1], r[2], r[3]) for r in base[3:7]] + [(9, 'Review', 'Station practice', ''), (10, base[7][1], base[7][2], base[7][3])]
    out = [{'week': w, 'topics': t, 'lab': l, 'assessment': a} for w, t, l, a in (rows or [])]
    return __import__('curriculum_v2.lab_additions', fromlist=['x']).augment_pacing(code, out)  # labs branch: new LMS labs


# ------------------------------------------------------------------------------------------- lesson plans
SESSION_TEMPLATE = [
    # (minutes, phase, what the instructor does) — a 150-minute lecture+lab block; scale for 75- or 50-minute meetings
    (10, 'Warm-up', 'Retrieval question or scenario on the board; students answer individually, then pair-share.'),
    (35, 'Direct instruction', 'Short segments (10–12 min) on the lesson sections listed, each followed by a one-question check.'),
    (20, 'Guided practice', 'Instructor models the task once, then students do a parallel example in pairs while the instructor circulates.'),
    (10, 'Break', ''),
    (55, 'Lab', 'Students complete the lab individually or in pairs; instructor checks evidence (screens, notes) at the checkpoints.'),
    (12, 'Check for understanding', 'Chapter check items in the LMS (ungraded) or 3–4 items read aloud with response cards; reteach any item under 70% correct.'),
    (8, 'Exit ticket', 'One written response collected on paper or in the LMS discussion; used to plan the next warm-up.'),
]

LESSON_PLANS = {
    ('ITSUP', 1): {
        'warmup': 'A user says “my computer is broken and I need it now.” List three questions you would ask before touching anything.',
        'guided': 'Classify five sample requests as incident, service request or change, then write one ticket note together using facts, times, tests and next step.',
        'exit_ticket': 'Write the four parts of a good ticket note for: “Printer on floor 2 jams on every job since this morning.”',
        'discussion': ['When is it right to tell a user “I can’t do that”? How do you say it without losing their trust?',
                       'What could go wrong if a technician writes guesses in a ticket as if they were facts?'],
        'misconceptions': ['“An ESD strap is optional if I touch the case first.” Touching metal equalises once; a strap keeps you equalised.',
                           '“Every request is a repair.” New access is a service request; many users affected is an incident.',
                           '“Documentation is for after the fix.” Notes written during the work are what make hand-offs possible.'],
        'support': 'Provide a ticket-note sentence frame (Observed… / Tested… / Result… / Next…).',
        'extension': 'Draft a one-page intake checklist for a walk-up help desk and justify each step.',
        'materials': 'ESD strap and mat (or photos), sample tickets, LMS lab ticket-intake.',
    },
    ('ITSUP', 2): {
        'warmup': 'Show a photo of a motherboard; students label as many components as they can in two minutes.',
        'guided': 'Walk through a POST failure using the “minimum boot” order (PSU, board, CPU, one RAM module, video) on a demo board or images.',
        'exit_ticket': 'A PC beeps and shows no video after a RAM upgrade. What do you check first and why?',
        'discussion': ['Why might a workplace leave Secure Boot on even when it makes some installs harder?',
                       'How would you explain dual-channel memory to a user who bought one large module?'],
        'misconceptions': ['“More RAM always means faster.” Speed, channel population and workload matter.',
                           '“UEFI and BIOS are just names for the same thing.” UEFI adds Secure Boot, GPT boot and a richer firmware interface.',
                           '“DDR5 fits a DDR4 slot.” Notches and voltages differ; modules are not interchangeable.'],
        'support': 'Component flash cards with photos; a printed POST order card.',
        'extension': 'Compare two current motherboards’ manuals: slot population rules, lane sharing (M.2 vs SATA), and supported memory.',
        'materials': 'Demo board or high-resolution images, a spare RAM module, LMS lab hw-board.',
    },
    ('ITSUP', 3): {
        'warmup': 'Rank HDD, SATA SSD and NVMe SSD by speed and say one reason someone might still buy an HDD.',
        'guided': 'Read a disk list (diskpart list disk or Disk Management) together and identify system, data and unallocated space.',
        'exit_ticket': 'Explain in two sentences why RAID 1 is not a backup.',
        'discussion': ['A manager wants to skip backups because the server has RAID. What do you say?',
                       'Which cables and ports in this room could be confused for each other, and how would a user tell them apart?'],
        'misconceptions': ['“RAID is a backup.” RAID survives disk failure, not deletion, ransomware or site loss.',
                           '“A USB-C port means fast data and video.” The connector says nothing about the protocol, speed or power it supports.',
                           '“A bigger PSU wattage always helps.” Quality and the 12 V rail matter; oversizing does not fix a failing unit.'],
        'support': 'Port-identification sheet with photos and speeds.',
        'extension': 'Design a 3-2-1 backup plan for a five-person office with a budget and restore test schedule.',
        'materials': 'Assorted cables and adapters, a USB drive, LMS labs w11-disk and gui-devices.',
    },
    ('ITSUP', 4): {
        'warmup': 'What information do you need before ordering a replacement laptop screen?',
        'guided': 'Trace a print job from application to device (app → spooler → driver/port → network/USB → printer) and test at each step.',
        'exit_ticket': 'A laptop battery looks swollen. List the steps you take and the steps you never take.',
        'discussion': ['Why should a technician not remove a work profile from a personal phone without asking?',
                       'Which print problems are best solved at the printer panel and which on the PC?'],
        'misconceptions': ['“Any 65 W charger works on any laptop.” Under-powered adapters cause slow charging or throttling.',
                           '“Print problems are always the driver.” Queue, port, network and the device itself are all candidates.',
                           '“A swollen battery is fine if the laptop works.” It is a fire hazard: stop and follow the battery procedure.'],
        'support': 'Print-path diagram with a checkbox per hop.',
        'extension': 'Write an MDM enrolment FAQ for staff explaining what the organisation can and cannot see on a personal device.',
        'materials': 'A shared printer (or the classroom lab CL-4 handout), a laptop with service manual, sample MDM screenshots.',
    },
    ('ITSUP', 5): {
        'warmup': 'Your laptop shows 169.254.x.x. What does that tell you and what does it not tell you?',
        'guided': 'Run ipconfig /all, ping the gateway, ping an IP beyond it, then a name; record each result and the conclusion it supports.',
        'exit_ticket': 'Ping to 8.8.8.8 works but ping to a website name fails. Which fault domain is next and which command proves it?',
        'discussion': ['Why is MAC filtering a weak control for Wi-Fi security?',
                       'How would you explain to a user why the Wi-Fi “has full bars” but the Internet is slow?'],
        'misconceptions': ['“Full Wi-Fi bars means the network is fine.” Signal is only layer 1; DHCP, DNS and the uplink can still fail.',
                           '“Ping failing proves the host is down.” Firewalls often block ICMP.',
                           '“APIPA means the NIC is broken.” It means no DHCP lease was obtained.'],
        'support': 'Isolation order card: link → lease → gateway → beyond gateway → name.',
        'extension': 'Configure (or simulate) a SOHO router with WPA3, guest isolation and a changed admin password; document each setting.',
        'materials': 'LMS lab set for Chapter 5 (win-ipconfig, win-dns-break, win-arp, win-route, w11-wlan, win-netstat).',
    },
    ('ITSUP', 6): {
        'warmup': 'Name one thing you would use a virtual machine for at home or work.',
        'guided': 'Create (or walk through) a VM: allocate vCPU, RAM and disk, attach an ISO, choose a virtual network type, take a snapshot.',
        'exit_ticket': 'Explain why a snapshot is not a backup.',
        'discussion': ['For a small business, when would SaaS email be a better choice than running a mail server?',
                       'Five VMs on one host lose the network at once. What is your first theory and why?'],
        'misconceptions': ['“A snapshot is a backup.” It depends on the original disk and the same host.',
                           '“Cloud means someone else handles all security.” Shared responsibility varies by IaaS, PaaS and SaaS.',
                           '“A VM needs no licence.” Guest operating systems are licensed like physical installs.'],
        'support': 'Shared-responsibility table to annotate.',
        'extension': 'Compare NAT, bridged and host-only virtual networking with a diagram of which hosts can reach which.',
        'materials': 'A host with Hyper-V, VMware Workstation Pro or VirtualBox and a Windows 11 or Linux ISO; classroom lab CL-6.',
    },
    ('ITSUP', 7): {
        'warmup': 'A user says “the Internet is down.” Write the first three facts you need.',
        'guided': 'Run a full troubleshooting cycle on a staged fault: identify, theory, test, plan, implement, verify, document.',
        'exit_ticket': 'Why should you change only one thing at a time when troubleshooting?',
        'discussion': ['What is the difference between “fixed” and “verified”?',
                       'When is it time to escalate, and what should the escalation contain?'],
        'misconceptions': ['“The user’s diagnosis is the starting point.” It is a clue; the evidence decides.',
                           '“If the error went away, it is fixed.” Verify the outcome the user needs and document it.',
                           '“Changing several things at once saves time.” It hides the cause and can create new faults.'],
        'support': 'Troubleshooting method poster with an example for each step.',
        'extension': 'Write a short runbook for one recurring fault in the lab, including a rollback step.',
        'materials': 'LMS labs win-dns-break and win-full-triage.',
    },
    ('ITSUP', 8): {
        'warmup': 'Clean install or in-place upgrade: which keeps the user’s apps, and when would you choose the other?',
        'guided': 'Collect a Windows baseline: Settings → System → About, Windows Update status, key services, accounts.',
        'exit_ticket': 'Name two repair tools you would try before reinstalling Windows and what each one checks.',
        'discussion': ['A feature update failed overnight on 30 PCs. How do you decide between rolling back and repairing?',
                       'What should be in a standard Windows baseline for new staff laptops?'],
        'misconceptions': ['“Reinstalling is the quickest fix.” It loses settings and time; repair tools often solve it.',
                           '“Windows 10 is still fine to deploy.” Windows 10 reached end of support on 14 October 2025; only ESU-covered devices get security updates.',
                           '“Disabling a service is harmless.” Services such as DHCP Client and Windows Update are needed for normal operation.'],
        'support': 'Settings path cheat sheet (About, Update, Accounts, Services).',
        'extension': 'Check a Windows 11 PC against the hardware requirements (TPM 2.0, Secure Boot, supported CPU) and report gaps.',
        'materials': 'LMS labs gui-about, gui-update, gui-services, gui-accounts, w11-services, w11-powershell-net.',
    },
    ('ITSUP', 9): {
        'warmup': 'What does “sudo” do and why does it belong in a ticket?',
        'guided': 'Navigate a Linux shell: pwd, ls -l, cd, cat, grep; read permissions on a file and change them with chmod.',
        'exit_ticket': 'Write the command to show your IP addresses on Linux and the macOS equivalent of Settings → About.',
        'discussion': ['A Mac user cannot reach a share a Windows user next to them can. How do you decide whether it is access or the network?',
                       'Why do many organisations support more than one operating system?'],
        'misconceptions': ['“Linux has no permissions to worry about.” Ownership and mode bits control access.',
                           '“macOS does not need updates or security tools.” It needs patching and endpoint protection like any OS.',
                           '“A share that fails on one OS is a network fault.” Entitlement, protocol and credentials are more common causes.'],
        'support': 'Command translation table (Windows / Linux / macOS).',
        'extension': 'Write a small shell script that collects hostname, IP and disk usage into a text file for a ticket.',
        'materials': 'A Linux VM or WSL, optional Mac; classroom lab CL-9.',
    },
    ('ITSUP', 10): {
        'warmup': 'Which is more secure: a long passphrase or a short complex password? Why?',
        'guided': 'Review account types and Windows Security status (Defender, firewall profiles) on a lab PC; record what you find.',
        'exit_ticket': 'A user clicked a phishing link. List your first three actions.',
        'discussion': ['Why are shared admin accounts a problem even when the password is strong?',
                       'How should a help desk verify a caller’s identity before resetting a password?'],
        'misconceptions': ['“Complex passwords that change every 90 days are best practice.” Current NIST guidance (SP 800-63B-4) favours length, screening against breached lists and no forced periodic changes.',
                           '“Antivirus alone keeps a PC safe.” Patching, least privilege, MFA and user awareness all matter.',
                           '“Turning off the firewall is fine to test an app.” Use a scoped rule or approved exception instead.'],
        'support': 'Incident first-response card (contain, record, escalate).',
        'extension': 'Compare MFA methods (SMS, app, passkey/FIDO2) for phishing resistance and usability.',
        'materials': 'LMS labs gui-accounts, gui-services, w11-firewall.',
    },
    ('ITSUP', 11): {
        'warmup': 'One app crashes on one PC; the same app works on the PC next door. What does that tell you?',
        'guided': 'Isolate a software fault: reproduce, check scope, read the error text, check processes and services, try safe mode or a clean profile.',
        'exit_ticket': 'Give one reason to repair an application and one reason to rebuild the PC instead.',
        'discussion': ['How do you decide between reinstalling one app and reimaging the whole PC?',
                       'Why is the exact error message worth copying into the ticket?'],
        'misconceptions': ['“Rebooting is free.” It loses volatile evidence and can interrupt others; treat it as a change.',
                           '“A slow PC needs more RAM.” Check which process uses what first.',
                           '“If it works in safe mode, Windows is broken.” It points to a third-party driver or startup item.'],
        'support': 'Scope grid (one user/many users × one app/many apps).',
        'extension': 'Use Event Viewer to find the log entry that matches an application crash and explain it.',
        'materials': 'LMS labs w11-processes and w11-services.',
    },
    ('ITSUP', 12): {
        'warmup': 'What is the difference between a repair and a change?',
        'guided': 'Write a change request for a planned task (e.g., firmware update) with risk, backout plan, test and communication.',
        'exit_ticket': 'Before a destructive step (wipe, reimage), what must you confirm?',
        'discussion': ['How do privacy rules affect what a technician may look at on a user’s PC?',
                       'What makes a recovery plan believable to a manager?'],
        'misconceptions': ['“Change control is only for big companies.” Any change that can break service needs a plan and a backout.',
                           '“A backup that reports success can be restored.” Only a test restore proves it.',
                           '“Technicians may browse user files to troubleshoot.” Access should be the minimum needed, with consent where policy requires.'],
        'support': 'Change request template with an example.',
        'extension': 'Run a tabletop recovery drill for a lost laptop and write the after-action notes.',
        'materials': 'Change request template, classroom lab CL-12.',
    },
    ('ITSUP', 13): {
        'warmup': 'Without looking, write the commands to show IP configuration, test reachability and flush the DNS cache.',
        'guided': 'Run a timed triage on a broken-name-resolution ticket using only the command line, narrating each step.',
        'exit_ticket': 'Which Settings path matches ipconfig /all, and when would you use each?',
        'discussion': ['When is the GUI faster than the command line, and the reverse?',
                       'Why not reboot first when a PC misbehaves?'],
        'misconceptions': ['“ipconfig /release fixes everything.” It removes the lease; use it only when you intend to renew.',
                           '“Commands are risky; the GUI is safe.” Both can make changes; know which commands only read.',
                           '“netsh shows different facts from ipconfig.” It is another view of the same configuration.'],
        'support': 'Command reference card with read-only commands marked.',
        'extension': 'Write a PowerShell one-liner that outputs the adapter name, IPv4 address and DNS servers.',
        'materials': 'Chapter 13 lab set in the LMS; optional Windows 11 VM.',
    },
    # ---------------------------------------------------------------------------------------- NETOPS
    ('NETOPS', 1): {
        'warmup': 'Put these in order from the wire up: IP, Ethernet frame, TCP segment, HTTP request.',
        'guided': 'Subnet 192.168.10.0/24 into four equal subnets on the board: mask, block size, network, first/last host, broadcast.',
        'exit_ticket': 'How many usable hosts in a /27, and what is the broadcast of 10.0.0.32/27?',
        'discussion': ['Why does the industry still use IPv4 with NAT when IPv6 exists?',
                       'When is UDP the better choice even though it is “unreliable”?'],
        'misconceptions': ['“The OSI model describes how protocols are actually built.” It is a reference model for reasoning; TCP/IP has fewer layers.',
                           '“Routers change IP addresses at each hop.” They change layer-2 addresses and TTL; NAT is a separate function.',
                           '“A /24 is always 255 hosts.” It has 256 addresses and 254 usable hosts.'],
        'support': 'Subnet table (prefix, mask, block size, hosts) and a binary place-value strip.',
        'extension': 'Plan an IPv6 /48 for a site with 20 VLANs using /64 per VLAN, and document the scheme.',
        'materials': 'Whiteboard, subnetting worksheet, LMS labs win-ipconfig, win-arp, win-netstat.',
    },
    ('NETOPS', 2): {
        'warmup': 'What does a switch do with a frame for a MAC address it has never seen?',
        'guided': 'Configure an access port and a trunk in the switch lab; verify with show vlan brief and show interfaces trunk.',
        'exit_ticket': 'One VLAN fails across a trunk while others work. Name two likely causes.',
        'discussion': ['Why do access ports usually have BPDU Guard and PortFast?',
                       'When is fibre worth the cost over copper inside a building?'],
        'misconceptions': ['“VLANs are a security boundary on their own.” They separate broadcast domains; policy between them is still needed.',
                           '“STP slows the network, so turn it off.” It prevents loops that can take the network down.',
                           '“Cat6 always gives 10 Gb/s to 100 m.” 10GBASE-T on Cat6 is limited to about 55 m; Cat6A supports 100 m.'],
        'support': 'Switch CLI mode map (user, privileged, config, interface).',
        'extension': 'Configure port security with a violation mode and explain the trade-offs of each mode.',
        'materials': 'LMS switch labs (sw-vlan-access, sw-trunk-basics, sw-vlan-and-trunk, sw-mac-table); optional physical switches or Packet Tracer/GNS3.',
    },
    ('NETOPS', 3): {
        'warmup': 'A router has routes to 10.0.0.0/8 and 10.1.0.0/16. Which is used for 10.1.5.5?',
        'guided': 'Configure two router interfaces and a default route; read show ip route and explain each code.',
        'exit_ticket': 'Give the SNR for −67 dBm signal and −92 dBm noise and say whether it is good for voice.',
        'discussion': ['What evidence convinces a provider that a WAN fault is on their side?',
                       'How would you design Wi-Fi for a lecture hall with 200 devices?'],
        'misconceptions': ['“More AP power gives better Wi-Fi.” It increases co-channel interference; clients transmit at lower power anyway.',
                           '“A traceroute star means the path is broken.” Many routers rate-limit or ignore probes while forwarding traffic.',
                           '“Dynamic routing always beats static.” Administrative distance and design decide; static routes are common at edges.'],
        'support': 'Route-selection flowchart (longest prefix → administrative distance → metric).',
        'extension': 'Draw a channel plan for 5 GHz with 40 MHz channels across six APs and justify it.',
        'materials': 'LMS router labs (rtr-gateway, rtr-two-interfaces, rtr-default-route, rtr-trace); Wi-Fi analyser app optional.',
    },
    ('NETOPS', 4): {
        'warmup': 'List the four DHCP messages in order and who sends each.',
        'guided': 'Diagnose a DNS failure: ipconfig /all, ping by IP, nslookup the name, compare with a working client; then flush and retest.',
        'exit_ticket': 'Why do clients on a new VLAN get 169.254 addresses when the DHCP server is elsewhere?',
        'discussion': ['When would you use split-horizon DNS?',
                       'Why should firewall rules be ordered from specific to general?'],
        'misconceptions': ['“NAT is a firewall.” It hides addresses but does not inspect or enforce policy by itself.',
                           '“Changing a DNS record takes effect immediately.” Caches keep the old answer until the TTL expires.',
                           '“NXDOMAIN means the DNS server is down.” It is an answer: the name does not exist.'],
        'support': 'DORA sequence diagram; DNS record-type table.',
        'extension': 'Write a firewall rule set for a DMZ web server with inbound HTTPS only and outbound updates.',
        'materials': 'LMS labs win-dhcp-renew and win-dns-break.',
    },
    ('NETOPS', 5): {
        'warmup': 'Which syslog level is more urgent: 3 or 6?',
        'guided': 'Read sample interface counters and syslog lines; decide which are physical, capacity and security signals.',
        'exit_ticket': 'Name three settings that harden a switch’s management plane.',
        'discussion': ['How do you know what “normal” looks like on a network you just inherited?',
                       'What would a zero-trust design change about a flat office network?'],
        'misconceptions': ['“SNMPv2c is secure if you change the community string.” It is still sent in clear text; use SNMPv3.',
                           '“A login banner is just decoration.” It states authorised use and supports policy enforcement.',
                           '“Segmentation means one VLAN per department.” It means enforced policy between zones based on need.'],
        'support': 'Syslog severity ladder (0–7) and an SNMP version comparison.',
        'extension': 'Propose a monitoring baseline (what to poll, thresholds, alert routing) for a small campus.',
        'materials': 'LMS labs sw-port-security, sw-banner, sw-int-status; sample log extract.',
    },
    ('NETOPS', 6): {
        'warmup': 'Only one building has an outage. What does that rule in and out?',
        'guided': 'Run a timed incident with roles (lead, scribe, tester); give status updates every 10 minutes.',
        'exit_ticket': 'Write a status update for stakeholders with impact, current action and next update time.',
        'discussion': ['How do time boxes help during an outage?', 'What should change after an incident review?'],
        'misconceptions': ['“The fastest fix is to reboot the core.” It widens the outage and destroys evidence.',
                           '“Status updates slow the fix.” Short, scheduled updates reduce interruptions.',
                           '“Verified means the alert cleared.” Re-run the failing test and confirm with users.'],
        'support': 'Incident role cards and an update template.',
        'extension': 'Write a post-incident review with timeline, root cause, contributing factors and actions.',
        'materials': 'LMS labs win-full-triage, sw-vlan-and-trunk, rtr-edge-complete; incident scenario cards.',
    },
    ('NETOPS', 9): {
        'warmup': 'What is the difference between running-config and startup-config?',
        'guided': 'Configure router-on-a-stick for two VLANs and verify end-to-end with ping and show commands.',
        'exit_ticket': 'Which command saves your configuration, and what happens on reload if you forget?',
        'discussion': ['Why verify with show commands rather than trusting the configuration you typed?',
                       'How would you document a new closet drop so the next technician can support it?'],
        'misconceptions': ['“Creating a VLAN assigns ports to it.” Ports need switchport access vlan.',
                           '“An interface with an IP address is up.” It may be administratively down until no shutdown.',
                           '“The router saves changes automatically.” Changes are lost on reload until copied to startup-config.'],
        'support': 'CLI command sequence cards for each lab.',
        'extension': 'Add a second trunk and a native VLAN change; predict and verify the effects.',
        'materials': 'LMS Chapter 9 lab set; optional physical gear or Packet Tracer/GNS3.',
    },
}


def _chapter_meta(code, chapter):
    import lessons as _lessons
    pack = {'ITSUP': _lessons.APLUS, 'NETOPS': _lessons.NETPLUS, 'CLIENT': _lessons.CLIENT}[code]
    for ch in pack:
        if ch['order'] == chapter:
            return ch
    return None


def plan_key(code, chapter):
    """CLIENT chapters reuse the ITSUP plans for chapters 8–13."""
    return ('ITSUP', chapter + 7) if code == 'CLIENT' else (code, chapter)


def lesson_plan(code, chapter):
    import interactive_labs
    meta = _chapter_meta(code, chapter)
    base = LESSON_PLANS.get(plan_key(code, chapter))
    if not meta or not base:
        return None
    labs_key = ('ITSUP', chapter + 7) if code == 'CLIENT' else (code, chapter)
    lab_ids = interactive_labs.CHAPTER_LABS.get(labs_key, [])
    by_id = {l['id']: l for l in interactive_labs.LABS}
    classroom = [cl for cl in CLASSROOM_LABS.values() if (code, chapter) in cl['chapters'] or labs_key in cl['chapters']]
    objs = objectives_for(code, chapter)
    plan = None  # noqa: F841
    # Plan time is the LMS lesson time (pass 13: NETOPS chapter totals in lessons.py included extra time the
    # lesson-plan text described as "LMS content"; the per-lesson minutes are what the LMS shows).
    lesson_minutes = sum(l.get('minutes') or 0 for l in meta['lessons']) or meta.get('minutes')
    sessions = max(1, round((lesson_minutes or 180) / 150))
    plan = {
        'course': code, 'chapter': chapter, 'title': meta['title'], 'minutes': lesson_minutes,
        'sessions': sessions,
        'objectives': objs,
        'lessons': [l['title'] for l in meta['lessons']],
        'timing': [{'minutes': m, 'phase': p, 'how': h} for m, p, h in SESSION_TEMPLATE],
        'labs': [{'id': i, 'title': by_id[i]['title']} for i in lab_ids if i in by_id][:6],
        'more_labs': max(0, len(lab_ids) - 6),
        'classroom_labs': [{'id': cl['id'], 'title': cl['title']} for cl in classroom],
        'check': f'Chapter {chapter} check (LMS, ungraded)',
        **base,
    }
    return _with_pass9(plan, code, chapter)


def _with_pass9(plan, code, chapter):
    """Merge the pass-9/10 lesson-plan updates for ITSUP chapters 3–13 (and CLIENT 1–6)."""
    from curriculum_v2.itsup_core import PENDING, PLAN_UPDATES, is_pending
    itsup_ch = chapter + 7 if code == 'CLIENT' else chapter
    upd = PLAN_UPDATES.get(itsup_ch) if code in ('ITSUP', 'CLIENT') else None
    plan['review'] = PENDING if is_pending(code, chapter) else ''
    plan.setdefault('worked_example', '')
    plan.setdefault('cfu', [])
    if not upd:
        return plan
    for k in ('warmup', 'guided', 'exit_ticket', 'worked_example', 'cfu'):
        if upd.get(k):
            plan[k] = upd[k]
    plan['misconceptions'] = list(plan['misconceptions']) + list(upd.get('misconceptions_add', []))
    if upd.get('materials_add'):
        plan['materials'] = plan['materials'].rstrip('.') + '. ' + upd['materials_add']
    return plan


# ------------------------------------------------------------------------------------------- labs
KIND_EQUIPMENT = {
    'windows': {
        'equipment': 'LMS Windows 11 command-line simulator (any modern browser; no install).',
        'real': 'A Windows 11 PC or VM with network access and a standard (non-admin) account plus an admin account for the steps that need it.',
        'low_cost': 'Windows 11 VM on Hyper-V, VMware Workstation Pro (free for personal and commercial use since Nov 2024) or VirtualBox 7+, '
                    'using institution licensing or a Microsoft evaluation image where available. Paper alternative: printed command output to annotate.',
        'reflection': ['Which output line was the key evidence, and what did it rule out?',
                       'Which command only reads information, and which one changed the system?',
                       'What would you write in the ticket after this lab?'],
        'troubleshooting': ['Type the command exactly as shown; Windows commands are not case-sensitive but spaces and switches matter.',
                            'If output looks different from the expected result, compare adapter names and addresses with the lab scenario.'],
    },
    'win11gui': {
        'equipment': 'LMS Windows 11 Settings simulator (browser).',
        'real': 'A Windows 11 PC or VM (Settings app).',
        'low_cost': 'Windows 11 VM (see above) or annotated screenshots of each Settings page.',
        'reflection': ['Which command-line lab shows the same facts as this Settings page?',
                       'Which settings here would you never change without a ticket and approval?',
                       'How would you guide a user to this page over the phone?'],
        'troubleshooting': ['Use the search box in Settings if a page is not where you expect it.',
                            'Some pages differ slightly between Windows 11 releases; match the page title, not the exact position.'],
    },
    'switch': {
        'equipment': 'LMS switch command-line simulator (Cisco IOS-style syntax).',
        'real': 'A managed layer-2 switch with console access, two PCs and patch cables.',
        'low_cost': 'Cisco Packet Tracer (free with a Networking Academy account) or GNS3 (free; needs device images); '
                    'used managed switches; or the paper topology worksheet.',
        'reflection': ['Which show command proved your configuration worked?',
                       'What would happen to connected users if you made this change on a production switch during the day?',
                       'What did you save, and how would you prove it survives a reload?'],
        'troubleshooting': ['Check the prompt to see which mode you are in (>, #, (config)#, (config-if)#).',
                            'Use ? for context help and Tab to complete commands.',
                            'If a command is rejected, check you are in the right mode and spelled the interface correctly.'],
    },
    'router': {
        'equipment': 'LMS router command-line simulator (Cisco IOS-style syntax).',
        'real': 'A router (or layer-3 switch) with two interfaces, console access and two PCs.',
        'low_cost': 'Cisco Packet Tracer or GNS3 (see above), or the paper topology worksheet.',
        'reflection': ['Which routing table entry carries traffic for the test you ran?',
                       'What evidence would show the problem is beyond your router?',
                       'What did you document so the next technician understands this configuration?'],
        'troubleshooting': ['An interface shows administratively down until you enter no shutdown.',
                            'Check addresses and masks on both ends of a link with show ip interface brief.',
                            'Save with copy running-config startup-config before you finish.'],
    },
    'ticket': {
        'equipment': 'LMS scenario desk (browser).',
        'real': 'A live help-desk queue or a printed set of scenario cards.',
        'low_cost': 'Printed scenario cards and a paper ticket template.',
        'reflection': ['What did you classify the request as, and what evidence decided it?',
                       'What did you deliberately not do, and why?',
                       'Could a peer pick up your ticket and continue without calling you?'],
        'troubleshooting': ['Re-read the scenario for scope (how many users) and safety cues before choosing an action.'],
    },
}


KIND_EQUIPMENT.update(__import__('curriculum_v2.lab_additions', fromlist=['x']).EXTRA_KIND_EQUIPMENT)  # labs branch: linux, activity


def standard_lab(lab, course=None, chapter=None):
    """Return one LMS lab in the standard classroom format."""
    import interactive_labs
    kind = KIND_EQUIPMENT.get(lab.get('kind'), KIND_EQUIPMENT['windows'])
    by_id = {l['id']: l for l in interactive_labs.LABS}
    pre = [by_id[b]['title'] for b in (lab.get('builds_on') or []) if b in by_id]
    hints = list(lab.get('hints') or [])
    steps = [o['text'] for o in (lab.get('objectives') or [])]
    return {
        'id': lab['id'], 'title': lab['title'], 'kind': lab.get('kind'),
        'objective': (lab.get('blurb') or '').strip() or (lab.get('intro') or ''),
        'scenario': lab.get('intro') or '',
        'prerequisites': pre or ['None beyond the chapter reading'],
        'equipment': kind['equipment'], 'real_equipment': kind['real'], 'low_cost': kind['low_cost'],
        'steps': steps,
        'commands': hints,
        'expected': lab.get('success_msg') or 'All checkpoints complete.',
        'troubleshooting': kind['troubleshooting'],
        'reflection': kind['reflection'],
        'rubric': 'lab',
        'minutes': 15 + 5 * len(steps),
    }


CLASSROOM_LABS = {
    'CL-4': {
        'id': 'CL-4', 'title': 'Print path and laptop FRU identification', 'chapters': [('ITSUP', 4)],
        'objective': 'Trace a print job hop by hop and identify the information needed to order a laptop field-replaceable unit.',
        'prerequisites': ['Chapter 4 lessons 4.1 and 4.3'],
        'equipment': 'One shared printer on the classroom network and a Windows PC; one laptop with its service manual.',
        'low_cost': 'Windows “Microsoft Print to PDF” as the device plus the printed print-path worksheet; laptop service manual PDF from the vendor site.',
        'steps': [
            'Print a test page from Notepad. Record whether it arrives.',
            'Pause the printer queue, print again and observe the job in the queue. Resume it.',
            'Open Printer properties and record the driver name and port (USB, TCP/IP address or WSD).',
            'Ping the printer’s IP address (network printers) and record the result.',
            'Print a configuration page from the printer panel and compare its IP address with the port.',
            'On the laptop, record the service tag/serial, model and the panel or battery part number from the service manual.',
            'Write a ticket note that a peer could use to order the right part or continue the print investigation.',
        ],
        'expected': 'A completed worksheet with each hop marked working or failing and a ticket note naming the exact FRU part number.',
        'troubleshooting': ['If the queue shows an error, note the exact text before clearing it.',
                            'If the port IP differs from the configuration page, the printer’s address changed (DHCP); record it rather than editing anything.'],
        'reflection': ['Which hop would you test first if only one user cannot print? If everyone cannot?',
                       'Why is “15-inch Dell screen” not enough to order a replacement?',
                       'What safety steps apply before opening a laptop?'],
        'rubric': 'lab', 'minutes': 50, 'objectives': ['IT-4.1', 'IT-4.3'],
    },
    'CL-6': {
        'id': 'CL-6', 'title': 'VM Build, Snapshot & Networking', 'chapters': [('ITSUP', 6)],
        'objective': 'Create a VM with appropriate resources, take and revert a snapshot, and compare virtual network modes.',
        'prerequisites': ['Chapter 6 lessons 6.1 and 6.3'],
        'equipment': 'A host PC with virtualisation enabled in firmware (8 GB RAM or more), Hyper-V, VMware Workstation Pro or VirtualBox 7+, and a Linux or Windows 11 ISO.',
        'low_cost': 'A lightweight Linux ISO (needs about 2 GB RAM and 20 GB disk) instead of Windows 11; or pair students on one host.',
        'steps': [
            'Create a VM: name it, set vCPU and RAM, create a virtual disk and attach the ISO. For Windows 11 guests use at least 4 GB RAM, 2 vCPU, 64 GB disk, UEFI with Secure Boot and a virtual TPM.',
            'Install the guest OS (or boot the live image) and record the guest’s IP address.',
            'Take a snapshot named “baseline”.',
            'Make a visible change (create a file or change the wallpaper), then revert to “baseline” and confirm the change is gone.',
            'Switch the VM network between NAT and bridged (or Default Switch and External) and record the guest IP and whether another classroom PC can reach it.',
            'Delete only your own snapshot when finished, and record what you did in a ticket note.',
        ],
        'expected': 'The guest runs, the snapshot revert removes the change, and the student can explain which network mode exposed the VM to the classroom LAN.',
        'troubleshooting': ['If the VM will not start, check virtualisation (Intel VT-x / AMD-V) is enabled in firmware.',
                            'Windows 11 setup fails without TPM/Secure Boot: enable the virtual TPM and Secure Boot in the VM settings.',
                            'Bridged mode may be blocked on some campus networks; use NAT and note the restriction.'],
        'reflection': ['Why is a snapshot not a backup?', 'Which network mode would you use for a test server that must not be reachable from the LAN?',
                       'What happens to a host if five VMs each get half its RAM?'],
        'rubric': 'lab', 'minutes': 60, 'objectives': ['IT-6.1', 'IT-6.3'],
    },
    'CL-9': {
        'id': 'CL-9', 'title': 'Linux command line and permissions', 'chapters': [('ITSUP', 9), ('CLIENT', 2)],
        'objective': 'Navigate a Linux file system, read and change permissions, and collect support facts from the shell.',
        'prerequisites': ['Chapter 9 lesson 9.1'],
        'equipment': 'A Linux VM, a Linux PC or WSL on Windows 11.',
        'low_cost': 'A free browser-based Linux terminal provided by the institution, or the printed command worksheet.',
        'steps': [
            'Run whoami, hostname and ip addr; record the user, host name and IPv4 address.',
            'Run pwd, ls -l and cd to move into /tmp; create a file with echo "test" > notes.txt.',
            'Read the permission string from ls -l notes.txt and explain each part (owner, group, other).',
            'Remove read permission for others with chmod o-r notes.txt and confirm with ls -l.',
            'Use grep to find a word in the file and df -h to check free disk space.',
            'Run one command with sudo (e.g., sudo apt update or sudo dnf check-update) only if the instructor allows it, and record it as a change.',
            'Write a ticket note listing the facts collected and any change made.',
        ],
        'expected': 'Correct facts recorded; permission string explained; the chmod change visible in ls -l; sudo use documented.',
        'troubleshooting': ['“Permission denied” means the current user lacks rights: check the owner and mode before using sudo.',
                            'If ip is not found, try ifconfig (older systems) or hostname -I.'],
        'reflection': ['Why should every sudo command appear in a ticket?', 'What is the Windows equivalent of ip addr and of chmod?',
                       'How would you explain file permissions to a Mac user?'],
        'rubric': 'lab', 'minutes': 50, 'objectives': ['IT-9.1', 'IT-9.3'],
    },
    'CL-12': {
        'id': 'CL-12', 'title': 'Change request and recovery drill', 'chapters': [('ITSUP', 12), ('CLIENT', 5)],
        'objective': 'Write a change request with risk and backout, then run a tabletop recovery drill and record the outcome.',
        'prerequisites': ['Chapter 12 lessons 12.1 and 12.3'],
        'equipment': 'Change request template and the recovery scenario card (provided by the instructor).',
        'low_cost': 'Paper only.',
        'steps': [
            'Read the scenario: a firmware update is needed on 20 staff laptops.',
            'Complete the change request: description, reason, risk, affected users, schedule, test plan, backout plan, communication.',
            'Peer review: swap requests and mark anything missing using the change-request checklist.',
            'Recovery drill: a laptop is lost. In groups, list the steps (report, remote lock/wipe per policy, account reset, restore to a replacement) and who does each.',
            'Write a short after-action note: what went well, what was unclear, one improvement.',
        ],
        'expected': 'A complete change request that passes peer review and an after-action note with at least one concrete improvement.',
        'troubleshooting': ['If the backout plan is “reinstall”, ask whether a less disruptive rollback exists.'],
        'reflection': ['What makes a backout plan believable?', 'Which recovery step depends on a backup having been tested?',
                       'What privacy rules limit what you may do with a recovered device?'],
        'rubric': 'lab', 'minutes': 50, 'objectives': ['IT-12.1', 'IT-12.3'],
    },
}


# ------------------------------------------------------------------------------------------- rubrics
from curriculum_v2.itsup_core import LABS_ADD as _LABS_ADD  # noqa: E402  (pass 9 classroom labs)

CLASSROOM_LABS.update(_LABS_ADD)

LEVELS = ['Exemplary (4)', 'Proficient (3)', 'Developing (2)', 'Beginning (1)']

RUBRICS = {
    'lab': {
        'title': 'Lab rubric', 'scale': LEVELS, 'points': 16,
        'use': 'Formative scoring of LMS and classroom labs. Proficient (3) on every criterion meets the course standard.',
        'criteria': [
            ('Procedure and safety', ['Follows every step in order, applies all safety and policy rules unprompted',
                                       'Follows the steps with minor reordering; safety rules followed',
                                       'Skips or reorders steps in ways that affect results; needs safety reminders',
                                       'Does not follow the procedure, or a safety rule is broken (stop and reteach)']),
            ('Results and evidence', ['All expected results reached and evidence captured exactly (output, screenshots, values)',
                                       'Expected results reached; evidence mostly complete',
                                       'Some results reached; evidence incomplete or not matched to steps',
                                       'Results not reached or no evidence']),
            ('Troubleshooting reasoning', ['Explains what each result rules in or out and chooses the next test logically',
                                            'Explains most results and next steps',
                                            'Describes results but not what they mean',
                                            'Guesses or changes things without a reason']),
            ('Documentation', ['Ticket note is factual, complete and another technician could continue from it',
                               'Ticket note is factual with small gaps',
                               'Ticket note missing tests, results or next step',
                               'No note, or the note contains guesses as facts or a password']),
        ],
    },
    'skills': {
        'title': 'Skills exam station rubric', 'scale': ['Meets (2)', 'Partly meets (1)', 'Not met (0)'], 'points': 10,
        'use': 'Summative scoring of each station in the Skills Midterm and Skills Final. A station passes at 8/10 '
               '(the 80% pass mark) with no critical errors.',
        'criteria': [
            ('Outcome', ['The required end state is reached and verified', 'Reached but not verified', 'Not reached']),
            ('Method', ['Steps in a logical order with the right tools', 'Correct tools, some wasted or out-of-order steps', 'Trial and error']),
            ('Verification', ['Re-tests the original symptom and confirms the outcome', 'Partial verification', 'None']),
            ('Documentation', ['Accurate note: facts, tests, result, next step', 'Note with gaps', 'No note']),
            ('Policy and safety', ['No unsafe or unauthorised actions', 'A minor policy slip, self-corrected', 'Critical error (see below)']),
        ],
        'critical_errors': ['Unsafe hardware handling (e.g., opening a PSU, ignoring a swollen battery)',
                            'Destructive command without approval (e.g., disk clean, reimage)',
                            'Disabling security controls (firewall, Defender) without an approved exception',
                            'Recording or disclosing a password'],
    },
    'ticket': {
        'title': 'Ticket note rubric', 'scale': LEVELS, 'points': 12,
        'use': 'Any written ticket or escalation note.',
        'criteria': [
            ('Facts', ['Who, what, when, scope and exact error text', 'Most facts present', 'Vague facts', 'Opinions instead of facts']),
            ('Tests and results', ['Each test with its result, in order', 'Most tests and results', 'Tests without results', 'None']),
            ('Next step / hand-off', ['Clear next step and owner', 'Next step without owner', 'Unclear next step', 'None']),
        ],
    },
    'discussion': {
        'title': 'Discussion rubric', 'scale': LEVELS, 'points': 12,
        'use': 'Discussion prompts in lesson plans (in class or in the LMS).',
        'criteria': [
            ('Accuracy', ['Technically correct and precise', 'Correct with small gaps', 'Partly correct', 'Incorrect']),
            ('Reasoning and evidence', ['Supports claims with course concepts or examples', 'Some support', 'Assertions only', 'None']),
            ('Engagement', ['Builds on or respectfully challenges peers', 'Responds to peers', 'Minimal response', 'No engagement']),
        ],
    },
}


# ------------------------------------------------------------------------------------------- assessments
# Objectives assessed by skills-exam stations rather than multiple choice (CLI lab tracks).
PRACTICAL_CHAPTERS = {'ITSUP': (13,), 'NETOPS': (9,), 'CLIENT': (13,)}
MIDTERM_CHAPTERS = {'ITSUP': range(1, 8), 'NETOPS': (1, 2, 3, 4, 9), 'CLIENT': range(1, 4)}


def _course_items(code):
    import question_bank
    forms = question_bank.tests_aplus() if code in ('ITSUP', 'CLIENT') else question_bank.tests_netplus()
    return forms


def _pool(code):
    seen = {}
    for _t, _d, _o, items in _course_items(code):
        for q in items:
            seen.setdefault(q.get('bank_id'), q)
    prefix = {'ITSUP': 'IT-', 'NETOPS': 'NO-', 'CLIENT': 'IT-'}[code]
    from curriculum_v2.exam_supplement import SUPPLEMENT
    from curriculum_v2.itsup_core import EXPANSION
    return [q for q in list(seen.values()) + SUPPLEMENT + EXPANSION if (q.get('obj') or '').startswith(prefix)]


def _chapter_of(obj):
    o = OBJECTIVES.get(obj)
    return o['chapter'] if o else None


def blueprint(code, exam, n_items=50):
    """Test specification: items per objective for the midterm (first-half chapters) or the cumulative final."""
    pool = _pool(code)
    if code == 'CLIENT':
        chapters = [c + 7 for c in (MIDTERM_CHAPTERS['CLIENT'] if exam == 'midterm' else range(1, 7))]
    else:
        chapters = list(MIDTERM_CHAPTERS[code]) if exam == 'midterm' else sorted(
            {v['chapter'] for v in OBJECTIVES.values() if v['course'] == code})
    prefix = {'ITSUP': 'IT', 'NETOPS': 'NO', 'CLIENT': 'IT'}[code]
    objs = [k for k, v in OBJECTIVES.items() if k.startswith(prefix + '-') and v['chapter'] in chapters]
    avail = {k: [q['bank_id'] for q in pool if q['obj'] == k] for k in objs}
    total_avail = sum(len(v) for v in avail.values()) or 1
    rows = []
    for k in objs:
        share = len(avail[k]) / total_avail
        rows.append({'objective': k, 'text': OBJECTIVES[k]['text'], 'bloom': OBJECTIVES[k]['bloom'],
                     'chapter': OBJECTIVES[k]['chapter'], 'available': len(avail[k]),
                     'recommended': min(len(avail[k]), max(1 if avail[k] else 0, round(share * n_items))),
                     'items': avail[k],
                     'practical': OBJECTIVES[k]['chapter'] in PRACTICAL_CHAPTERS.get(code, ())})
    # top up / trim to n_items without exceeding what is available
    def total():
        return sum(r['recommended'] for r in rows)
    for r in sorted(rows, key=lambda r: -r['available']):
        while total() < n_items and r['recommended'] < r['available']:
            r['recommended'] += 1
    for r in sorted(rows, key=lambda r: -r['recommended']):
        while total() > n_items and r['recommended'] > 1:
            r['recommended'] -= 1
    bloom = {}
    for r in rows:
        bloom[r['bloom']] = bloom.get(r['bloom'], 0) + r['recommended']
    gaps = [r['objective'] for r in rows if not r['available'] and not r['practical']]
    practical = [r['objective'] for r in rows if r['practical']]
    return {'course': code, 'exam': exam, 'chapters': chapters, 'n_items': total(), 'rows': rows,
            'bloom': bloom, 'gaps': gaps, 'practical': practical,
            'note': ('Knowledge Tests A–C in the LMS are cumulative forms drawn from the whole bank. Use this specification '
                     'to build a chapter-limited midterm from the listed item IDs, or deliver Test A as a cumulative '
                     'diagnostic midterm.') if exam == 'midterm' else
                    'The cumulative final follows this specification; Knowledge Test C is the default LMS final form.'}


def form_coverage(code):
    """How each LMS knowledge-test form spreads its items across chapters."""
    out = []
    for title, _d, _o, items in _course_items(code):
        by = {}
        for q in items:
            ch = _chapter_of(q.get('obj'))
            by[ch] = by.get(ch, 0) + 1
        out.append({'title': title, 'n': len(items), 'by_chapter': dict(sorted((k, v) for k, v in by.items() if k))})
    return out


LETTERS = 'ABCD'


def _key_rows(items):
    rows = []
    for i, q in enumerate(items, 1):
        opts = q['options']
        rows.append({'n': i, 'id': q.get('bank_id', ''), 'stem': q['text'],
                     'options': [f'{LETTERS[j]}. {o}' for j, o in enumerate(opts)],
                     'key': LETTERS[opts.index(q['correct'])], 'answer': q['correct'],
                     'objective': q.get('obj', ''), 'rationale': ('[Pending SME review] ' if 'Pending SME review' in (q.get('review') or '') else '')
                     + (q.get('explanation') or q.get('study_tip') or '')})
    return rows


def answer_keys(code):
    """Instructor-only answer keys: knowledge-test forms and chapter checks, with rationales."""
    import pilot_slice
    from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload
    keys = []
    if code != 'CLIENT':
        for title, _d, _o, items in _course_items(code):
            keys.append({'title': title, 'kind': 'Knowledge test', 'rows': _key_rows(items)})
    from curriculum_v2.exam_supplement import SUPPLEMENT
    prefix = 'NO-' if code == 'NETOPS' else 'IT-'
    sup = [q for q in SUPPLEMENT if q['obj'].startswith(prefix)
           and (code != 'CLIENT' or (OBJECTIVES[q['obj']]['chapter'] >= 8))]
    if sup:
        keys.append({'title': 'Supplementary exam items', 'kind': 'Exam supplement', 'rows': _key_rows(sup)})
    from curriculum_v2.itsup_core import EXPANSION, PENDING
    if code in ('ITSUP', 'CLIENT'):
        lo = 8 if code == 'CLIENT' else 1
        exp = sorted((q for q in EXPANSION if OBJECTIVES[q['obj']]['chapter'] >= lo),
                     key=lambda q: (OBJECTIVES[q['obj']]['chapter'], q['bank_id']))
        if exp:
            keys.append({'title': f'Chapter item bank, passes 9–10 — {PENDING}', 'kind': 'Exam item bank',
                         'review': PENDING, 'rows': _key_rows(exp)})
    if code == 'NETOPS':
        for order in NETOPS_CHECKS:
            keys.append({'title': f'Chapter {order} check', 'kind': 'Chapter check', 'rows': _key_rows(netops_quiz_payload(order))})
    else:
        orders = range(8, 14) if code == 'CLIENT' else sorted(pilot_slice.PILOT_CHECKS)
        for order in orders:
            label = order - 7 if code == 'CLIENT' else order
            keys.append({'title': f'Chapter {label} check', 'kind': 'Chapter check',
                         'rows': _key_rows(pilot_slice.quiz_payload(order, ''))})
    return keys


def skills_stations(code):
    import interactive_labs
    from skills_exams import exams_for, stations_of
    by_id = {l['id']: l for l in interactive_labs.LABS}
    out = []
    for title, desc, order, payload, minutes, passing in exams_for(code):
        stations = []
        for st in stations_of(payload):
            lab = by_id.get(st.get('lab_id'))
            stations.append({'lab_id': st.get('lab_id'), 'lab': lab['title'] if lab else st.get('lab_id'),
                             'area': st.get('area', ''),
                             'evidence': [o['text'] for o in (lab or {}).get('objectives', [])]})
        out.append({'title': title, 'minutes': minutes, 'passing': passing, 'description': desc, 'stations': stations,
                    'rubric': 'skills'})
    return out


# ------------------------------------------------------------------------------------------- glossary
GLOSSARY = [
    ('802.1Q', 'The IEEE standard for VLAN tagging on trunk links.'),
    ('802.1X', 'Port-based network access control: a device or user must authenticate (usually via RADIUS) before the port or Wi-Fi grants access.'),
    ('AAA', 'Authentication, authorisation and accounting: who you are, what you may do, and a record of what you did.'),
    ('Administrative distance', 'A router’s preference between routing sources for the same prefix; lower is preferred.'),
    ('APIPA', 'Automatic Private IP Addressing (169.254.0.0/16), self-assigned when no DHCP lease is obtained.'),
    ('ARP', 'Address Resolution Protocol: finds the MAC address for an IPv4 address on the local link.'),
    ('Backout (rollback) plan', 'The tested steps to undo a change if it fails.'),
    ('Baseline', 'A record of normal configuration or performance used to spot abnormal readings.'),
    ('BitLocker', 'Windows full-volume encryption, usually protected by the TPM.'),
    ('Broadcast domain', 'The set of devices that receive each other’s layer-2 broadcasts; a VLAN is one broadcast domain.'),
    ('Change request', 'A documented proposal for a change, with risk, schedule, test and backout plan, approved before work starts.'),
    ('CIDR / prefix length', 'Notation such as /24 giving the number of network bits in an address.'),
    ('DDR5', 'Current desktop/laptop memory generation (JEDEC); not slot-compatible with DDR4.'),
    ('DHCP', 'Dynamic Host Configuration Protocol: leases addresses and options (gateway, DNS) to clients via Discover, Offer, Request, Acknowledge.'),
    ('DHCP relay', 'A router feature (helper address) that forwards DHCP broadcasts to a server on another subnet.'),
    ('DMZ', 'A network zone for Internet-facing services, separated from internal networks by policy.'),
    ('DNS', 'Domain Name System: resolves names to addresses and other records.'),
    ('Encapsulation', 'Wrapping data with each layer’s header (segment → packet → frame) on the way down the stack.'),
    ('ESD', 'Electrostatic discharge: static electricity that can damage components; controlled with straps, mats and handling.'),
    ('Escalation', 'Passing a ticket to a higher tier or another team with the evidence gathered so far.'),
    ('Fault domain', 'A part of the system (hardware, OS, network path, name resolution, account, service) where a fault can be isolated.'),
    ('Field-replaceable unit (FRU)', 'A part designed to be replaced on site, ordered by exact part number.'),
    ('Firewall', 'A device or software that permits or denies traffic by rules; stateful firewalls track connections.'),
    ('Incident', 'An unplanned interruption or reduction in service quality.'),
    ('In-place upgrade', 'Reinstalling or upgrading Windows while keeping apps, settings and files.'),
    ('IPsec', 'A suite of protocols that authenticates and encrypts IP traffic, used for site-to-site and remote-access VPNs.'),
    ('IPv6 link-local', 'An fe80::/10 address present on every IPv6 interface; valid only on the local link.'),
    ('Least privilege', 'Giving users and systems only the access needed for their task.'),
    ('Longest prefix match', 'Routers forward using the most specific matching route.'),
    ('MDM', 'Mobile device management: organisation-controlled enrolment and policy on phones, tablets and laptops.'),
    ('MFA', 'Multi-factor authentication: two or more of something you know, have or are.'),
    ('NAT / PAT', 'Network (port) address translation: rewrites addresses (and ports) so many inside hosts share public addresses.'),
    ('Native VLAN', 'The VLAN carried untagged on an 802.1Q trunk.'),
    ('NVMe', 'A storage protocol for SSDs over PCIe, much faster than SATA.'),
    ('OSI model', 'A seven-layer reference model for reasoning about network functions.'),
    ('Passkey', 'A phishing-resistant FIDO credential stored on a device or password manager, used instead of a password.'),
    ('PoE', 'Power over Ethernet: delivers power to phones, APs and cameras over twisted-pair cabling.'),
    ('POST', 'Power-on self-test run by firmware before the operating system loads.'),
    ('RAID', 'Combining disks for performance and/or availability; not a backup.'),
    ('RSSI / SNR', 'Received signal strength (dBm) and signal-to-noise ratio (dB) for wireless links.'),
    ('Secure Boot', 'UEFI feature that starts only signed boot loaders.'),
    ('Service request', 'A request for something new (access, software, equipment) rather than a repair.'),
    ('Snapshot', 'A point-in-time state of a VM used to revert changes; depends on the original disk and is not a backup.'),
    ('SNMP', 'Simple Network Management Protocol for polling and traps (UDP 161/162); SNMPv3 adds authentication and encryption.'),
    ('Spanning Tree Protocol (STP)', 'Prevents layer-2 loops by blocking redundant paths until needed.'),
    ('Subnet mask', 'The bits of an IPv4 address that identify the network.'),
    ('Syslog', 'A standard for sending device log messages to a central server; severities 0 (emergency) to 7 (debug).'),
    ('TCP / UDP', 'Transport protocols: TCP is connection-oriented and reliable; UDP is connectionless with lower overhead.'),
    ('Ticket', 'The record of a support request: facts, tests, results, actions and next step.'),
    ('TPM', 'Trusted Platform Module: hardware security chip used for keys (e.g., BitLocker); TPM 2.0 is required for Windows 11.'),
    ('Trunk', 'A switch link that carries several VLANs with tags.'),
    ('TTL / hop limit', 'A counter in each IP packet decremented by every router; the packet is dropped at zero.'),
    ('UEFI', 'Unified Extensible Firmware Interface, the modern replacement for legacy BIOS.'),
    ('USB4 / Thunderbolt', 'High-speed USB-C based interfaces; the connector shape does not indicate speed or features.'),
    ('Virtual machine (VM)', 'A guest computer made of files, running on a hypervisor host.'),
    ('VLAN', 'A virtual LAN: a logical broadcast domain on a switch.'),
    ('VPN', 'Virtual private network: an encrypted tunnel across an untrusted network.'),
    ('Wi-Fi 6/6E/7', 'IEEE 802.11ax (6 and 6E, the latter adding 6 GHz) and 802.11be (7).'),
    ('WPA3', 'Current Wi-Fi security standard; Personal uses SAE, Enterprise uses 802.1X.'),
    ('Zero trust', 'A security model that verifies every request and applies least privilege regardless of network location.'),
]

# Pass 9–10 terms (chapters 3–13), marked in the glossary document as pending SME review.
from curriculum_v2.itsup_core import GLOSSARY_ADD as _GLOSSARY_ADD  # noqa: E402

_existing = {t.lower() for t, _d in GLOSSARY}
GLOSSARY_NEW = {t for t, _d in _GLOSSARY_ADD if t.lower() not in _existing}
GLOSSARY = sorted(GLOSSARY + [(t, d) for t, d in _GLOSSARY_ADD if t in GLOSSARY_NEW], key=lambda td: td[0].lower())


ACCESSIBILITY = {
    'statement': (
        'This course is designed to be usable with keyboards, screen readers and magnification. The LMS pages are '
        'checked with automated accessibility testing (axe-core) in light and dark themes; automated checks do not '
        'find every barrier, so report any problem to the instructor. [Institution: accessibility office contact]'),
    'features': [
        'Lesson text is HTML with headings and tables marked up for screen readers; there are no images in lesson bodies that need alt text.',
        'Narration is generated from the on-page lesson text, so the page itself is the transcript. There is no pre-recorded audio or video that needs captions.',
        'Light and dark themes; text resizes with browser zoom; all labs work with the keyboard.',
        'Instructors can extend test time limits for individual students.',
        'Course documents are available as PDF and editable DOCX for conversion to other formats.',
    ],
    'reading_level': ('Estimated Flesch–Kincaid grade level of lesson text is about 7–9 for IT Support and about 9–11 for '
                      'Network Operations (automated estimate; technical terms raise the score).'),
    'instructor_checklist': [
        'Provide printed or large-print copies of command references on request.',
        'For physical labs, offer a seated workstation and a simulator alternative for students who cannot handle equipment.',
        'Read aloud any on-screen instructions during timed skills stations when an accommodation requires it.',
        'Check any images, videos or slides you add for alt text and captions.',
    ],
}


# ------------------------------------------------------------------------------------------- syllabus
def syllabus(code, section=None, gb=None):
    """Assemble the syllabus for a course. ``section`` holds the instructor's per-section fields
    (SECTION_FIELDS + POLICY_FIELDS keys); ``gb`` is a gradebook settings object or dict."""
    import json as _json
    c = COURSES[code]
    section = section or {}
    gbd = {}
    if gb is not None:
        get = (gb.get if isinstance(gb, dict) else lambda k, d=None: getattr(gb, k, d))
        scale = get('letter_scale')
        try:
            scale = [tuple(x) if not isinstance(x, dict) else (x['min'], x['label']) for x in _json.loads(scale)] if isinstance(scale, str) else scale
        except (ValueError, TypeError, KeyError):
            scale = None
        gbd = dict(weights={'tests': get('weight_tests', 70), 'skills': get('weight_skills', 30), 'quizzes': get('weight_quizzes', 0), 'labs': get('weight_labs', 0)},
                   pass_mark=get('pass_mark', 80) or 80, scale=scale, policy=get('policy', 'best') or 'best',
                   late_per_day=get('late_per_day', 0) or 0, late_max=get('late_max', 0) or 0)
    fields = [{'key': k, 'label': lab, 'value': (section.get(k) or '').strip(), 'placeholder': ph} for k, lab, ph in SECTION_FIELDS]
    policies = [{'key': k, 'label': lab, 'value': (section.get(k) or '').strip(), 'placeholder': ph} for k, lab, ph in POLICY_FIELDS]
    import lessons as _lessons
    pack = {'ITSUP': _lessons.APLUS, 'NETOPS': _lessons.NETPLUS, 'CLIENT': _lessons.CLIENT}[code]
    weeks = int(section.get('pacing_weeks') or (8 if code == 'CLIENT' else 16))
    return {
        'code': code, 'title': c['title'], 'catalog_number': c['catalog_number'], 'description': c['description'],
        'prerequisites': c['prerequisites'], 'credits': credit_mapping(code), 'clos': clos(code),
        'chapters': [{'order': ch['order'], 'title': ch['title'], 'minutes': ch.get('minutes'),
                      'objectives': objectives_for(code, ch['order'])} for ch in pack],
        'grading': grading(**gbd), 'fields': fields, 'policies': policies,
        'pacing_weeks': weeks, 'pacing': pacing(code, weeks), 'pacing_note': PACING_NOTES.get(weeks, ''),
        'skills_exams': skills_stations(code), 'disclaimer': DISCLAIMER, 'accessibility': ACCESSIBILITY,
    }
