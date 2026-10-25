"""Pure helpers for the skills portfolio: certification domain readiness, lab process badges, OpenBadges-style export."""
from curriculum_v2.cert.exams import DOMAINS
from curriculum_v2.cert.mapping import CURATED

EXAMS = {'A1': 'CompTIA A+ Core 1', 'A2': 'CompTIA A+ Core 2', 'N': 'CompTIA Network+'}
BADGE_IDS = ('diagnosed_first', 'verified_before_submit', 'efficient')
READY, DEVELOPING = 0.85, 0.6


def level(p):
    return 'Ready' if p >= READY else 'Developing' if p >= DEVELOPING else 'Not yet'


def cert_readiness(states):
    """states: {course objective id: estimate dict with 'p'}. Returns [{exam, name, domains: [...]}] for exams with evidence."""
    out = []
    for ex, name in EXAMS.items():
        doms = []
        for d, dname, weight in DOMAINS[ex]:
            ps = [st['p'] for obj, st in states.items()
                  for t in CURATED.get(obj, []) if t.startswith(f'{ex}:{d.split(".")[0]}.')]
            if ps:
                p = sum(ps) / len(ps)
                doms.append({'domain': d, 'name': dname, 'weight': weight, 'p': round(p, 2), 'pct': round(100 * p), 'level': level(p),
                             'objectives': len(ps)})
        if doms:
            out.append({'exam': ex, 'name': name, 'domains': doms,
                        'pct': round(sum(x['pct'] * x['weight'] for x in doms) / max(1, sum(x['weight'] for x in doms)))})
    return out


def lab_badges(analysis):
    """Process-quality strengths from mastery.lab_diagnosis.analyze()."""
    return [{'id': p['id'], 'label': p['label']} for p in (analysis or {}).get('strengths', []) if p.get('id') in BADGE_IDS or p.get('strength')]


def openbadges(pf, issuer_url, verify_url):
    """OpenBadges 2.0-shaped JSON (unsigned, hosted verification). One assertion per mastered competency and completed lab."""
    issuer = {'type': 'Profile', 'id': issuer_url, 'name': 'Novak LMS™'}
    rec = {'type': 'name', 'hashed': False, 'identity': pf['student']['name']}
    asr = []
    for c in pf['competencies']:
        asr.append({'@context': 'https://w3id.org/openbadges/v2', 'type': 'Assertion', 'recipient': rec,
                    'issuedOn': c.get('when') or pf['generated'], 'verification': {'type': 'hosted', 'url': verify_url},
                    'badge': {'type': 'BadgeClass', 'name': f"{c['id']}: {c['text']}", 'criteria': {'narrative': 'Mastery estimate ≥ 0.85 with medium or high confidence in the Novak LMS™ adaptive engine.'},
                              'issuer': issuer, 'tags': [c['course']]}})
    for lab in pf['labs']:
        asr.append({'@context': 'https://w3id.org/openbadges/v2', 'type': 'Assertion', 'recipient': rec,
                    'issuedOn': lab.get('completed') or pf['generated'], 'verification': {'type': 'hosted', 'url': verify_url},
                    'badge': {'type': 'BadgeClass', 'name': f"Lab: {lab['title']}", 'issuer': issuer,
                              'criteria': {'narrative': f"Completed with score {lab['score']}%. Process: " + (', '.join(b['label'] for b in lab['badges']) or 'recorded')},
                              'tags': [lab['kind']]}})
    for x in pf.get('exam_sittings', []):
        if not x['ready']:
            continue
        asr.append({'@context': 'https://w3id.org/openbadges/v2', 'type': 'Assertion', 'recipient': rec,
                    'issuedOn': x['date'] or pf['generated'], 'verification': {'type': 'hosted', 'url': verify_url},
                    'badge': {'type': 'BadgeClass', 'name': f"VOUCHER READY: {x['name']} ({x['code']}) simulator",
                              'issuer': issuer, 'tags': [x['code'], 'exam-simulator'],
                              'criteria': {'narrative': f"Simulated scaled score {x['score']}/900 against a pass bar of {x['bar']} "
                                                        f"({x['mode']}) with every domain at 60% or better. Simulation only; "
                                                        'not an official CompTIA result.'}}})
    return {'portfolio': {k: pf.get(k) for k in ('student', 'generated', 'courses', 'certifications', 'exam_sittings')}, 'assertions': asr,
            'note': 'Unsigned export. Verify at the hosted URL while the student keeps the portfolio shareable.'}
