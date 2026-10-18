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
    'ms-flicker': 'Microsoft Support — “Troubleshoot screen flickering in Windows”',
    'epa-liion': 'U.S. EPA — “Used Lithium-Ion Batteries” (do not put in household trash or recycling; take to a battery or household-hazardous-waste collection)',
    'apple-btpair': 'Apple Support — “Pair a third-party Bluetooth accessory with your iPhone or iPad”; Android Help — “Connect to Bluetooth devices”',
    'ms-display': 'Microsoft Support — “How to use multiple monitors in Windows” (Win+P projection modes, scale and resolution)',
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


def single(cert, obj, n, q, correct, wrong, why, extra=()):
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3, (cert, n)
    return {'bank_id': _bid(cert, n), 'type': 'single', 'cert': [cert, *extra], 'obj': obj, 'text': q,
            'correct': correct, 'wrong': list(wrong), 'explanation': why, 'review': PENDING}


def multi(cert, obj, n, q, correct, wrong, why, extra=()):
    """Choose-N. ``correct`` 2–3 options, ``wrong`` the rest (5–6 options in total)."""
    assert 2 <= len(correct) <= 3 and 5 <= len(correct) + len(wrong) <= 6 and not set(correct) & set(wrong), (cert, n)
    bid = _bid(cert, n)
    opts = list(correct) + list(wrong)
    _rng(bid).shuffle(opts)
    return {'bank_id': bid, 'type': 'multi', 'cert': [cert, *extra], 'obj': obj, 'text': q, 'options': opts,
            'correct': sorted(correct, key=opts.index), 'choose': len(correct), 'explanation': why, 'review': PENDING}


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
