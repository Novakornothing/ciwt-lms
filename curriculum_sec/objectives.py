"""Course objectives for Cybersecurity (SEC).

Kept out of the global OBJECTIVES dict so existing item-bank audits stay scoped to
IT Support and Network Operations. Mastery and the explanation ladder opt in explicitly.
"""

REVIEW = 'Pending SME review'

# (id, chapter, text, bloom)
_ROWS = [
    ('SEC-1.1', 1, 'Explain how security work differs from ordinary support, networking, and operating-system tasks', 'Understand'),
    ('SEC-1.2', 1, 'Apply confidentiality, integrity, and availability to a workplace scenario', 'Apply'),
    ('SEC-1.3', 1, 'Classify controls as preventive, detective, corrective, or compensating', 'Understand'),
    ('SEC-1.4', 1, 'Describe an asset, threat, vulnerability, and impact without mixing the terms', 'Understand'),
    ('SEC-2.1', 2, 'Compare common threat actors by motive and typical target', 'Understand'),
    ('SEC-2.2', 2, 'Recognize phishing, pretexting, baiting, and quid pro quo approaches', 'Apply'),
    ('SEC-2.3', 2, 'Describe spoofing, replay, and denial-of-service ideas at a recognition level', 'Understand'),
    ('SEC-2.4', 2, 'Identify tailgating, shoulder surfing, and untrusted-media risks', 'Apply'),
    ('SEC-3.1', 3, 'Distinguish a vulnerability, an exploit, and a patch', 'Understand'),
    ('SEC-3.2', 3, 'Compare virus, worm, trojan, ransomware, and spyware behaviors', 'Understand'),
    ('SEC-3.3', 3, 'List host and account signs that justify a closer look', 'Apply'),
    ('SEC-3.4', 3, 'Choose a safe first response that avoids running unknown code', 'Apply'),
    ('SEC-4.1', 4, 'Separate hashing, encryption, and encoding', 'Understand'),
    ('SEC-4.2', 4, 'Contrast symmetric and asymmetric keys at a beginner level', 'Understand'),
    ('SEC-4.3', 4, 'Explain certificates, certificate authorities, and trust chains', 'Understand'),
    ('SEC-4.4', 4, 'Interpret common TLS certificate warnings without clicking through blindly', 'Apply'),
    ('SEC-5.1', 5, 'Select authentication factors that actually form multi-factor authentication', 'Apply'),
    ('SEC-5.2', 5, 'Apply least privilege and separation of duties to an access request', 'Apply'),
    ('SEC-5.3', 5, 'Compare user, privileged, service, and shared accounts', 'Understand'),
    ('SEC-5.4', 5, 'Explain password, key, and session hygiene', 'Apply'),
    ('SEC-6.1', 6, 'Explain default-deny firewall policy and stateful rules', 'Apply'),
    ('SEC-6.2', 6, 'Describe network segmentation and why flat networks spread trouble', 'Understand'),
    ('SEC-6.3', 6, 'Explain what a VPN protects and what it does not', 'Understand'),
    ('SEC-6.4', 6, 'Apply basic wireless hardening choices such as WPA3 and a guest network', 'Apply'),
    ('SEC-7.1', 7, 'Read Linux permission bits and explain why unexpected SUID is risky', 'Apply'),
    ('SEC-7.2', 7, 'Harden accounts, sudo, and SSH without locking out recovery', 'Apply'),
    ('SEC-7.3', 7, 'Describe Windows firewall, local policy, and disk-encryption goals', 'Understand'),
    ('SEC-7.4', 7, 'Explain baselines, patching, and configuration drift', 'Understand'),
    ('SEC-8.1', 8, 'Name where authentication and system logs live on Linux and Windows', 'Remember'),
    ('SEC-8.2', 8, 'Explain what a SIEM collects and what it does not decide by itself', 'Understand'),
    ('SEC-8.3', 8, 'Triage an alert as likely true, likely false, or needing more evidence', 'Analyze'),
    ('SEC-8.4', 8, 'Explain why a baseline of normal is required before an alert means anything', 'Understand'),
    ('SEC-9.1', 9, 'Order the basic incident-response cycle from preparation through lessons learned', 'Apply'),
    ('SEC-9.2', 9, 'Choose first containment steps that preserve evidence', 'Apply'),
    ('SEC-9.3', 9, 'Describe chain-of-custody habits for a beginner', 'Understand'),
    ('SEC-9.4', 9, 'Use hashes and targeted log extracts as basic forensic checks', 'Apply'),
    ('SEC-10.1', 10, 'Distinguish policy, standard, and procedure', 'Understand'),
    ('SEC-10.2', 10, 'Describe likelihood and impact in everyday risk language', 'Understand'),
    ('SEC-10.3', 10, 'Explain compliance as evidence of practice, not a substitute for it', 'Understand'),
    ('SEC-10.4', 10, 'Identify privacy duties and when to report rather than investigate alone', 'Apply'),
]

SEC_OBJECTIVES = {
    oid: {'course': 'SEC', 'chapter': ch, 'text': text, 'bloom': bloom}
    for oid, ch, text, bloom in _ROWS
}


def rows_for(chapter=None):
    rows = [(k, v) for k, v in SEC_OBJECTIVES.items()]
    if chapter is not None:
        rows = [(k, v) for k, v in rows if v['chapter'] == chapter]
    return rows
