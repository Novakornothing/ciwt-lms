"""Certification alignment for the course package (syllabus, lesson plans, glossary, answer keys) — pass 11.

Kept separate from course_package.py so the alignment data has one source: exams.py (published objectives),
mapping.CURATED (CIWT objective -> exam objectives) and the pass-11 supplements and items.
Wording rule: "aligned to", never "endorsed by" or "approved by".
"""
from .exams import DISCLAIMER, EXAMS, OBJECTIVES, label, sort_key
from .mapping import CURATED

COURSE_EXAMS = {'ITSUP': ('A1', 'A2'), 'CLIENT': ('A2',), 'NETOPS': ('N',)}
STATEMENT = ('Lesson objectives below are aligned to the published CompTIA exam objectives listed here. The alignment '
             'is CIWT’s own mapping, made to help students prepare; it is not reviewed or endorsed by CompTIA.')


def exams_for(code):
    return [dict(EXAMS[k], key=k) for k in COURSE_EXAMS[code]]


def labels_for(obj_code, code=None):
    """Exam objective labels ('A+ Core 2 3.2') a CIWT objective is aligned to, limited to the course's exams."""
    keep = COURSE_EXAMS.get(code) if code else None
    ids = [x for x in CURATED.get(obj_code, []) if keep is None or OBJECTIVES[x]['exam'] in keep]
    return [label(x) for x in sorted(set(ids), key=sort_key)]


def syllabus_section(code):
    return {'statement': STATEMENT, 'disclaimer': DISCLAIMER,
            'exams': [{'name': e['name'], 'code': e['code'], 'doc_version': e['doc_version'], 'url': e['url']} for e in exams_for(code)]}


def _itsup_chapter(code, chapter):
    return ('ITSUP', chapter + 7) if code == 'CLIENT' else (code, chapter)


def supplements_for(code, chapter):
    from .supplements import SUPPLEMENTS
    course, ch = _itsup_chapter(code, chapter)
    return [{'title': s['title'], 'lesson': f"{ch}.{s['lesson']}", 'cert': [label(c) for c in sorted(s['cert'], key=sort_key)]}
            for s in SUPPLEMENTS if s['course'] == course and s['chapter'] == ch]


def plan_section(code, chapter, objectives):
    rows = [{'code': o['code'], 'labels': labels_for(o['code'], code)} for o in objectives]
    return {'rows': [r for r in rows if r['labels']], 'supplements': supplements_for(code, chapter)}


def glossary_terms():
    from .supplements import GLOSSARY
    return list(GLOSSARY)


def _fmt_key(q):
    t = q['type']
    if t == 'single':
        return q['correct']
    if t == 'multi':
        return '; '.join(q['correct'])
    if t == 'order':
        return ' → '.join(f'{i}. {s}' for i, s in enumerate(q['correct'], 1))
    return '; '.join(f'{p} → {c}' for p, c in zip(q['prompts'], q['correct']))


def answer_key_rows(code):
    """Instructor-only rows for the pass-11 certification items (all four item types)."""
    from .items import CERT_ITEMS
    from curriculum_v2.objectives import OBJECTIVES as CIWT
    prefix = 'NO-' if code == 'NETOPS' else 'IT-'
    keep = COURSE_EXAMS[code]
    items = [q for q in CERT_ITEMS if q['obj'].startswith(prefix) and any(OBJECTIVES[c]['exam'] in keep for c in q['cert'])
             and (code != 'CLIENT' or CIWT[q['obj']]['chapter'] >= 8)]
    items.sort(key=lambda q: (sort_key(q['cert'][0]), q['bank_id']))
    kinds = {'single': 'Single answer', 'multi': 'Multiple select', 'order': 'Ordering', 'match': 'Matching'}
    rows = []
    for n, q in enumerate(items, 1):
        stem = q['text']
        if q['type'] == 'match':
            opts = [f'Prompt: {p}' for p in q['prompts']] + [f'Choice: {o}' for o in q['options']]
        else:
            opts = [f'{chr(65 + j)}. {o}' for j, o in enumerate(q['options'])]
        rows.append({'n': n, 'id': q['bank_id'], 'type': kinds[q['type']], 'stem': stem, 'options': opts,
                     'key': _fmt_key(q), 'objective': f"{q['obj']} / " + ', '.join(label(c) for c in q['cert']),
                     'rationale': q['explanation']})
    return rows
