"""Content round 7 (Oct 24): authoritative references for IT-7.x / IT-12.x certification items whose explanations
cited only course practice (flagged by tools/sme_priority_review.py, Priority 4). Pending SME review."""
AI = 'NIST AI 600-1, Generative AI Profile (2024); CompTIA A+ Core 2 (220-1202) objective 4.10'
METHOD = 'CompTIA troubleshooting methodology (A+ Core 1 220-1201 obj. 5.1; Network+ N10-009 obj. 5.1)'
PROF = 'CompTIA A+ Core 2 (220-1202) objective 4.7, communication and professionalism'
CHANGE = 'ITIL 4 Change Enablement practice; NIST SP 800-128 (security-focused configuration management); CompTIA A+ Core 2 objective 4.2'
FORENSIC = 'NIST SP 800-86 (forensics in incident response); NIST SP 800-61r2; IETF RFC 3227; CompTIA A+ Core 2 objective 4.6'
SOURCES = {
    'C-A2-4.10-21': AI, 'C-A2-4.10-22': AI, 'C-A2-4.10-23': AI, 'C-A2-4.10-24': AI, 'C-A2-4.10-2': AI, 'C-A2-4.10-3': AI,
    'C-A2-4.10-4': AI,
    'C-N-5.1-102': METHOD, 'C-N-5.1-103': METHOD,
    'C-A1-5.5-101': METHOD + '; IETF RFC 1035 (DNS)',
    'C-A2-4.7-101': PROF, 'C-A2-4.7-102': PROF, 'C-A2-4.7-103': PROF,
    'C-A2-4.1-106': 'CompTIA A+ Core 2 objective 4.1 (ticketing and escalation); NIST SP 800-61r2 (incident handling, escalation records)',
    'C-A2-4.3-101': 'CompTIA A+ Core 2 objective 4.3 (backup types); NIST SP 800-34 Rev. 1 (contingency planning)',
    'C-A2-4.3-102': 'CISA, Data Backup Options (3-2-1 rule); NIST SP 800-34 Rev. 1; CompTIA A+ Core 2 objective 4.3',
    'C-A2-4.1-107': 'ITIL 4 Knowledge Management practice; CompTIA A+ Core 2 objective 4.1 (knowledge base articles)',
    'C-A2-4.1-108': 'NIST SP 1800-5 (IT Asset Management); NIST SP 800-88 Rev. 1 (media sanitisation at disposal); CompTIA A+ Core 2 objective 4.1',
    'C-A2-4.2-11': CHANGE, 'C-A2-4.2-12': CHANGE, 'C-A2-4.2-13': CHANGE, 'C-A2-4.2-14': CHANGE, 'C-A2-4.2-15': CHANGE,
    'C-A2-4.2-16': CHANGE,
    'C-A2-4.6-11': FORENSIC, 'C-A2-4.6-16': FORENSIC,
    'C-A2-4.6-14': 'CompTIA A+ Core 2 objective 4.6 (regulated data: PII, PHI under HIPAA, PCI DSS v4.0, GDPR)',
    'C-A2-4.6-15': 'CompTIA A+ Core 2 objective 4.6 (licensing, EULA, personal versus corporate use)',
    'C-A2-4.6-17': 'PCI Security Standards Council, PCI DSS v4.0 (cardholder data); CompTIA A+ Core 2 objective 4.6',
}


def apply(items):
    for q in items:
        src = SOURCES.get(q.get('bank_id'))
        if src and 'Source:' not in (q.get('explanation') or ''):
            q['explanation'] = (q.get('explanation') or '').rstrip() + f' Source: {src}.'
    return items
