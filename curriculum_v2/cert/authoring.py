"""Authoring helpers for the content pass 11 (certification alignment) supplements and items.

Lesson building blocks (figure, worked example, scenario, check for understanding, SME note) are reused
from curriculum_v2.itsup_core so the new sections look and behave exactly like the pass 9/10 core content.
"""
import hashlib
import random
from html import escape

from curriculum_v2.itsup_core import PENDING, cfu, figure, scenario, worked  # noqa: F401  (re-exported)

PASS = 'pass 11 (certification alignment)'

# Primary sources cited by the pass 11 supplements.  Only documents that were checked to exist are listed;
# each entry names the publisher and the document or page title.
SOURCES = {
    'apple-app': 'Apple Support — “If an app on your iPhone or iPad stops responding, closes unexpectedly, or won’t open” (support.apple.com/119876)',
    'apple-oled': 'Apple Support — “About the Super Retina display and Super Retina XDR display on your iPhone” (image persistence and burn-in; support.apple.com/109039)',
    'android-app': 'Android Help — “Fix an installed Android app that isn’t working” (support.google.com/android/answer/2668665)',
    'nist-800124r2': 'NIST SP 800-124 Rev. 2, Guidelines for Managing the Security of Mobile Devices in the Enterprise (May 2023)',
    'cisa-phish': 'CISA — “Avoiding Social Engineering and Phishing Attacks” (security tip) and “Recognize and Report Phishing” (Secure Our World)',
    'nist-80063b4': 'NIST SP 800-63B-4, Digital Identity Guidelines: Authentication and Authenticator Management (2025)',
    'ms-smartscreen': 'Microsoft Learn — Microsoft Defender SmartScreen overview',
    'chrome-help': 'Google Chrome Help — “Clear cache & cookies”, “Browse in Incognito mode” and “Install and manage extensions”',
    'ms-execpolicy': 'Microsoft Learn — about_Execution_Policies (PowerShell)',
    'ms-psdrive': 'Microsoft Learn — New-PSDrive, Restart-Computer and Get-CimInstance cmdlet reference',
    'gnu-bash': 'GNU Bash Reference Manual (shebang/interpreter line, exit status, set -e)',
    'nist-ai6001': 'NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile (July 2024)',
    'nist-ai1001': 'NIST AI 100-1, Artificial Intelligence Risk Management Framework (AI RMF 1.0) (January 2023)',
    'nist-800145': 'NIST SP 800-145, The NIST Definition of Cloud Computing (2011)',
    'ms-avd': 'Microsoft Learn — “What is Azure Virtual Desktop?”',
    'ms-m365-licences': 'Microsoft Learn — “Assign Microsoft 365 licenses to user accounts” and Microsoft Entra Connect Sync documentation',
    'ms-onedrive-kfm': 'Microsoft Learn — “Redirect and move Windows known folders to OneDrive”',
    'aws-vpc': 'Amazon Web Services — Amazon VPC User Guide (“What is Amazon VPC?”, security groups, internet gateways, NAT gateways)',
    'rfc7348': 'IETF RFC 7348, Virtual eXtensible Local Area Network (VXLAN) (2014)',
    'nist-800207': 'NIST SP 800-207, Zero Trust Architecture (August 2020)',
    'cisco-spineleaf': 'Cisco — “Cisco Data Center Spine-and-Leaf Architecture: Design Overview” white paper',
    'rfc4987': 'IETF RFC 4987, TCP SYN Flooding Attacks and Common Mitigations (2007)',
    'rfc826': 'IETF RFC 826, An Ethernet Address Resolution Protocol (1982)',
    'cisa-dos': 'CISA — “Understanding Denial-of-Service Attacks” (security tip)',
    'ieee-8021q': 'IEEE Std 802.1Q, Bridges and Bridged Networks (VLAN tagging; native/untagged VLAN behaviour)',
    'ieee-poe': 'IEEE Std 802.3 clauses 33 and 145 (PoE 802.3af/at and 4-pair PoE 802.3bt) — power at the PSE: 15.4 W (Type 1), 30 W (Type 2), 60 W (Type 3), 90 W (Type 4)',
    'nist-80034r1': 'NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems (2010) — RTO, RPO, MTD; hot, warm and cold sites',
    'ashrae-tc99': 'ASHRAE TC 9.9 — Thermal Guidelines for Data Processing Environments (recommended equipment inlet temperature 18–27 °C)',
    'eia-310': 'EIA/ECIA-310 rack standard — 19-inch rack width; one rack unit (1U) = 1.75 in (44.45 mm)',
    'ms-bootrec': 'Microsoft Learn — “Use Bootrec.exe in the Windows RE to troubleshoot startup issues” and Windows Recovery Environment (Startup Repair)',
    'ms-eventlog': 'Microsoft Learn — “Advanced troubleshooting for Event ID 41: The system has rebooted without cleanly shutting down first” (Kernel-Power)',
    'ms-wow64': 'Microsoft Learn — WOW64 implementation details (32-bit applications on 64-bit Windows) and Windows 11 system requirements',
    'wfa-wpa3': 'Wi-Fi Alliance — Wi-Fi CERTIFIED 6 / 6E and WPA3 specifications (6 GHz operation requires WPA3 or Enhanced Open)',
    'ieee-80211': 'IEEE Std 802.11 and amendments 802.11h (DFS and TPC in 5 GHz), 802.11n/ac/ax/be (Wi-Fi 4/5/6/7)',
    'cisco-ifaces': 'Cisco IOS interface and switching command references (show interfaces counters: CRC, runts, giants; err-disabled; administratively down; show power inline; show lldp/cdp neighbors)',
    'tcpdump-man': 'tcpdump(8) and dig(1) manual pages; Nmap Reference Guide (nmap.org)',
    'rfc6143': 'IETF RFC 6143, The Remote Framebuffer Protocol (VNC)',
    'ms-rdp': 'Microsoft Learn — Remote Desktop Services: Network Level Authentication and Remote Desktop Gateway; Installation and configuration for Windows Remote Management (WinRM ports 5985/5986)',
    'cisa-rmm': 'CISA, NSA and MS-ISAC — “Protecting Against Malicious Use of Remote Monitoring and Management Software” (joint advisory, January 2023)',
    'ms-print': 'Microsoft Support — “Fix printer connection and printing problems in Windows”; Microsoft Learn — Print Spooler service',
    'ms-storage': 'Microsoft Support — “What to do about a critical warning for a storage device”; Microsoft Learn — Get-PhysicalDisk and Get-StorageReliabilityCounter',
    'ms-sfc': 'Microsoft Support — “Use the System File Checker tool to repair missing or corrupted system files” (run DISM /RestoreHealth before sfc /scannow)',
    'ms-flicker': 'Microsoft Support — “Troubleshoot screen flickering in Windows”',
    'epa-liion': 'U.S. EPA — “Used Lithium-Ion Batteries” (do not put in household trash or recycling; take to a battery or household-hazardous-waste collection)',
    'apple-btpair': 'Apple Support — “Pair a third-party Bluetooth accessory with your iPhone or iPad”; Android Help — “Connect to Bluetooth devices”',
    'ms-display': 'Microsoft Support — “How to use multiple monitors in Windows” (Win+P projection modes, scale and resolution)',
    # pass 11, second batch (A+ Core 2 domains 1 and 2)
    'ms-mmc': 'Microsoft Learn — Windows Tools and Microsoft Management Console snap-ins (eventvwr.msc, diskmgmt.msc, taskschd.msc, devmgmt.msc, certmgr.msc, lusrmgr.msc, perfmon.msc, gpedit.msc)',
    'ms-taskmgr': 'Microsoft Support — Task Manager in Windows (Processes, Performance, Startup apps, Users, Details and Services pages)',
    'ms-power': 'Microsoft Support — power settings in Windows (power mode, sleep, hibernate, lid and power-button actions, fast startup)',
    'ms-explorer-opts': 'Microsoft Support — “File Explorer in Windows” (show hidden files and file name extensions; Folder Options)',
    'ms-memlimits': 'Microsoft Learn — Memory Limits for Windows and Windows Server Releases',
    'ms-editions': 'Microsoft — Windows 11 edition comparison (Home, Pro, Pro for Workstations, Enterprise) and Windows 10 end of support, 14 October 2025',
    'apple-macos-guide': 'Apple Support — macOS User Guide (Finder, Dock, Mission Control, Spotlight, Time Machine, Force Quit, Disk Utility; support.apple.com/guide/mac-help)',
    'apple-platsec': 'Apple Platform Security guide — XProtect, FileVault, Keychain and Background Security Improvements (support.apple.com/guide/security)',
    'apple-bsi': 'Apple Support — “About Background Security Improvements for iOS, iPadOS, and macOS” (support.apple.com/102657)',
    'fhs3': 'Linux Foundation — Filesystem Hierarchy Standard 3.0 (/etc, /home, /root, /var)',
    'linux-man': 'Linux man-pages project (man7.org): passwd(5), shadow(5), fstab(5), hosts(5), resolv.conf(5), mount(8), fsck(8); GNU Coreutils manual (ls, cp, mv, rm, chmod, chown, du, df)',
    'nist-80083r1': 'NIST SP 800-83 Rev. 1, Guide to Malware Incident Prevention and Handling for Desktops and Laptops (July 2013)',
    'cisa-ransom': 'CISA, FBI, NSA and MS-ISAC — #StopRansomware Guide',
    'ms-lockout': 'Microsoft Learn — Account lockout threshold and Account lockout duration (security policy settings)',
    'ms-autoplay': 'Microsoft Support — turn AutoPlay on or off in Windows',
    'ms-netuser': 'Microsoft Learn — net user command reference (/active, /expires, /times)',
    'tcg-tpm': 'Trusted Computing Group — TPM 2.0 Library specification',
    'nist-fips1403': 'NIST FIPS 140-3, Security Requirements for Cryptographic Modules (2019)',
    'ms-hyperv-req': 'Microsoft Learn — Hyper-V system requirements (hardware virtualization extensions, SLAT)',
    'snia-ddf': 'SNIA — Common RAID Disk Data Format (DDF) specification (RAID level definitions)',
    'intel-atx3': 'Intel — ATX Version 3 Multi Rail Desktop Platform Power Supply Design Guide',
    'nist-80077r1': 'NIST SP 800-77 Rev. 1, Guide to IPsec VPNs (June 2020)',
    'nist-800113': 'NIST SP 800-113, Guide to SSL VPNs (July 2008)',
    'nist-80041r1': 'NIST SP 800-41 Rev. 1, Guidelines on Firewalls and Firewall Policy (September 2009)',
    'ieee-8021x': 'IEEE 802.1X-2020, Port-Based Network Access Control',
    'nist-80057p1': 'NIST SP 800-57 Part 1 Rev. 5, Recommendation for Key Management (May 2020)',
    # pass 11, round 2
    'tia568': 'ANSI/TIA-568 cabling standards (T568A and T568B pin-outs; 100 m channel)',
    'usbif': 'USB Implementers Forum — USB 2.0, USB 3.2, USB4 and USB Type-C specifications',
    'vesa-dp': 'VESA — DisplayPort standard',
    'hdmi-la': 'HDMI Licensing Administrator — HDMI specification overview',
    'nfpa70': 'NFPA 70, National Electrical Code — communications cable ratings (plenum CMP, riser CMR)',
    'nist-80053r5': 'NIST SP 800-53 Rev. 5 — Physical and Environmental Protection (PE) and Access Control (AC) control families',
    'fido': 'FIDO Alliance — FIDO2 / WebAuthn passkeys and security keys overview',
    'rfc6238': 'RFC 6238, TOTP: Time-Based One-Time Password Algorithm',
    'oasis-saml': 'OASIS — Security Assertion Markup Language (SAML) 2.0',
    'itil4-change': 'ITIL 4 — Change enablement practice guide (PeopleCert/AXELOS)',
    'nist-800128': 'NIST SP 800-128, Guide for Security-Focused Configuration Management of Information Systems (2011)',
    'osha-lift': 'OSHA — Materials handling and ergonomics guidance; NIOSH Revised Lifting Equation (load constant 23 kg / 51 lb)',
    'nfpa10': 'NFPA 10, Standard for Portable Fire Extinguishers (extinguisher classes)',
    'esda-s2020': 'ANSI/ESD S20.20 — ESD control program standard (EOS/ESD Association)',
    'nist-80086': 'NIST SP 800-86, Guide to Integrating Forensic Techniques into Incident Response (2006)',
    'rfc3227': 'RFC 3227, Guidelines for Evidence Collection and Archiving (order of volatility)',
    'pci-dss': 'PCI Security Standards Council — PCI DSS v4.0',
    'hhs-hipaa': 'U.S. Department of Health and Human Services — HIPAA Privacy Rule summary',
    'osi-osd': 'Open Source Initiative — The Open Source Definition and approved licenses',
    'comptia-a2-obj': 'CompTIA A+ Core 2 (220-1202) Exam Objectives document — objective 4.7 bullet list (used for the list of behaviours only)',
    'snia-dict': 'SNIA Dictionary — network-attached storage (NAS) and storage area network (SAN)',
    'rfc2474': 'RFC 2474, Definition of the Differentiated Services Field (DSCP) in the IPv4 and IPv6 Headers',
    'rfc791': 'RFC 791, Internet Protocol (time to live); RFC 8200, IPv6 (hop limit)',
    'rfc7336': 'RFC 7336, Framework for Content Distribution Network Interconnection (CDNI)',
    'tia606': 'ANSI/TIA-606 — Administration standard for telecommunications infrastructure (labelling and records)',
    'nist-80088': 'NIST SP 800-88, Guidelines for Media Sanitization',
}


def sources_line(keys):
    return '<p class="ref-sources small">Sources: ' + '; '.join(escape(SOURCES[k]) for k in keys) + '.</p>'


def sme_note(detail):
    return (f'<div class="instructor-note"><h4>{PENDING}</h4><p>{detail} Added in {PASS} to close a gap in the '
            f'exam-objective alignment. Verify against local practice before grading on it; facts were checked against '
            f'the sources listed at the end of the section.</p></div>')


# ------------------------------------------------------------------------------------------- items
def _rng(bid):
    return random.Random(int(hashlib.sha1(bid.encode()).hexdigest(), 16))


def _bid(cert, n):
    ex, num = cert.split(':')
    return f'C-{ex}-{num}-{n}'


def _mc(wrong, mc):
    """Misconception tags for wrong options, aligned with ``wrong`` (None = untagged throw-away distractor).
    Stored as {distractor text: misconception id}; see curriculum_v2/cert/misconceptions.py."""
    if not mc:
        return {}
    assert len(mc) == len(wrong), (wrong, mc)
    return {w: m for w, m in zip(wrong, mc) if m}


def single(cert, obj, n, q, correct, wrong, why, extra=(), mc=None):
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3, (cert, n)
    return {'bank_id': _bid(cert, n), 'type': 'single', 'cert': [cert, *extra], 'obj': obj, 'text': q,
            'correct': correct, 'wrong': list(wrong), 'explanation': why, 'review': PENDING, 'mc': _mc(wrong, mc)}


def multi(cert, obj, n, q, correct, wrong, why, extra=(), mc=None):
    """Choose-N. ``correct`` 2–3 options, ``wrong`` the rest (5–6 options in total)."""
    assert 2 <= len(correct) <= 3 and 5 <= len(correct) + len(wrong) <= 6 and not set(correct) & set(wrong), (cert, n)
    bid = _bid(cert, n)
    opts = list(correct) + list(wrong)
    _rng(bid).shuffle(opts)
    return {'bank_id': bid, 'type': 'multi', 'cert': [cert, *extra], 'obj': obj, 'text': q, 'options': opts,
            'correct': sorted(correct, key=opts.index), 'choose': len(correct), 'explanation': why, 'review': PENDING,
            'mc': _mc(wrong, mc)}


def order(cert, obj, n, q, steps, why, extra=()):
    """Put the steps in order.  ``steps`` is the key order; ``options`` is a shuffled presentation that is never
    the key order."""
    assert 4 <= len(steps) <= 6 and len(set(steps)) == len(steps), (cert, n)
    bid = _bid(cert, n)
    opts = list(steps)
    r = _rng(bid)
    while opts == list(steps):
        r.shuffle(opts)
    return {'bank_id': bid, 'type': 'order', 'cert': [cert, *extra], 'obj': obj, 'text': q, 'options': opts,
            'correct': list(steps), 'explanation': why, 'review': PENDING}


def match(cert, obj, n, q, pairs, why, decoys=(), extra=()):
    """Match each prompt (left) to one choice (right).  ``pairs`` = [(left, right)]; right values may repeat only
    if listed once in the choice list.  ``decoys`` are extra choices that match nothing."""
    assert 3 <= len(pairs) <= 6, (cert, n)
    bid = _bid(cert, n)
    choices = sorted({r for _l, r in pairs} | set(decoys))
    _rng(bid).shuffle(choices)
    return {'bank_id': bid, 'type': 'match', 'cert': [cert, *extra], 'obj': obj, 'text': q,
            'prompts': [l for l, _r in pairs], 'options': choices, 'correct': [r for _l, r in pairs],
            'explanation': why, 'review': PENDING}


def finalise(items):
    """Single-answer items: place the key so positions are balanced across the set, in a hashed (non-visible)
    sequence — the same approach as curriculum_v2.itsup_core._finalise."""
    singles = [i for i, q in enumerate(items) if q['type'] == 'single']
    order_ = sorted(singles, key=lambda i: hashlib.sha1(items[i]['bank_id'].encode()).hexdigest())
    out = [dict(q) for q in items]
    for rank, i in enumerate(order_):
        q = out[i]
        opts = list(q.pop('wrong'))
        opts.insert(rank % 4, q['correct'])
        q['options'] = opts
    return out
