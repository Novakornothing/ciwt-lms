"""Content round 4 (Oct 18 2026): misconception tags for the pass-15 certification gap items
(curriculum_v2/cert/content/i05_gaps_p15.py) and the last two untagged chapter-check items.

Measured before this round with tools/misconception_coverage.py and a served-item check (exact option text, not the
key, same objective, ``tag_for`` returns it): the 55 single-answer pass-15 items already carried 155 tags on their
165 distractors, all 155 verified against the served items, but their 47 ``MC-C-*`` misconceptions had no ``source``
and no ``status``, so the mix-up correction page did not show that they are unreviewed. The two choose-N and two
ordering items are not scored per distractor by the engine and stay untagged, as on every other bank.

This round:

* ``P15_ANNOTATIONS``: ``status: 'Pending SME review'`` and a ``source`` for each of the 47 pass-15 misconceptions,
  taken from the primary sources pass 15 recorded for the items that carry the tag (``i05_gaps_p15.SOURCE``).
* Five more tags on pass-15 distractors whose wrong idea the item explanation names (155 -> 160 of 165).
* Q13.6 and NQ5.5, left untagged in round 3, now carry one tag each: Q13.6's "Hyper-V delete-all" option is the
  change-before-reading-state idea its rationale names; NQ5.5's "removes the need for SNMP" option is a real wrong
  idea, and its rationale was extended in curriculum_v2/rationales_round4.py to explain it.
* Three new ``MC-R4-*`` misconceptions, each with a primary source and Pending SME review.

Left untagged on purpose (throw-away distractors, no wrong idea the explanation names): C-N-5.1-103 "Fix the printer
first, because it is quickest"; C-A2-2.2-101 "sfc /scannow" and "ipconfig /renew"; C-A2-2.2-102 "A local account on
each PC" and "BitLocker on the file server"; and Q13.6 / NQ5.5's other distractors. Same rules as round 3. Written
by Grok Bot."""

STATUS = 'Pending SME review'


def _m(obj, label, fix, terms, source):
    return {'obj': obj, 'label': label, 'fix': fix, 'terms': terms, 'source': source, 'status': STATUS}


MISCONCEPTIONS = {
    'MC-R4-IT12-321-COUNTS': _m('IT-12.3', 'Reading the 3-2-1 rule as counts of backup jobs, people or tests instead of copies, media and off-site',
                                '3-2-1 means three copies of the data, on two different media, with one copy off-site.',
                                ['3-2-1', 'copies', 'off-site', 'media', 'backup'],
                                'CISA, "Back Up Business Data" (3-2-1 rule); CompTIA A+ 220-1202 objective 4.3'),
    'MC-R4-NO4-DHCP-RESOLVES': _m('NO-4.2', 'Thinking the DHCP server answers name lookups',
                                  'DHCP hands out the address and the list of DNS servers (option 6); names are answered from the resolver cache, then by the configured DNS server.',
                                  ['dhcp', 'dns server', 'resolver', 'cache', 'option 6'],
                                  'IETF RFC 2132 §3.8 (option 6, domain name servers); Microsoft Learn, DNS client resolver cache'),
    'MC-R4-NO5-LOG-VS-SNMP': _m('NO-5.2', 'Thinking central syslog replaces SNMP monitoring',
                                'Syslog carries event messages from devices; SNMP answers polls for counters and status and sends traps. They are used together.',
                                ['syslog', 'snmp', 'ntp', 'trap', 'log'],
                                'IETF RFC 5424 (syslog protocol); RFC 3411 (SNMP architecture); RFC 5905 (NTPv4)'),
}

_T = [
    # pass-15 certification gap items
    ('C-A2-4.1-105', 'Order another 8 GB module for the PC right away', 'MC-C-IT2-RECONCILE-SKIP'),
    ('C-A1-2.6-101', 'An administrator set a static address on it', 'MC-C-IT5-APIPA'),
    ('C-N-5.1-103', 'Escalate all three to the network team at once', 'MC-C-IT7-BUNDLE'),
    ('C-A2-4.3-102', 'Three backups a day, two admins, one restore test', 'MC-R4-IT12-321-COUNTS'),
    ('C-N-3.4-105', 'The DHCP server for its scope', 'MC-R4-NO4-DHCP-RESOLVES'),
    # chapter checks left untagged in round 3
    ('Q13.6', 'Hyper-V delete-all, snapshots, vSwitch, uplinks', 'MC-IT13-CHANGE-BEFORE-STATE'),
    ('NQ5.5', 'It removes the need for SNMP', 'MC-R4-NO5-LOG-VS-SNMP'),
]
TAGS = {(b, d): mc for b, d, mc in _T}


def p15_annotations():
    """{mc id: {'source', 'status'}} for the pass-15 misconceptions: the distinct primary sources recorded for the
    pass-15 items that carry each tag (after this round's tags), in item order."""
    from curriculum_v2.cert.content import i05_gaps_p15 as P
    srcs = {}
    for q in P.ITEMS:
        tags = dict(q.get('mc') or {})
        tags.update({d: mc for (b, d), mc in TAGS.items() if b == q['bank_id']})
        for mc in tags.values():
            if mc in P.MISCONCEPTIONS:
                lst = srcs.setdefault(mc, [])
                if P.SOURCE[q['bank_id']] not in lst:
                    lst.append(P.SOURCE[q['bank_id']])
    return {mc: {'source': '; '.join(srcs.get(mc) or []), 'status': STATUS} for mc in P.MISCONCEPTIONS}
