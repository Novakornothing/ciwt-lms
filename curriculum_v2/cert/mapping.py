"""CIWT ↔ CompTIA exam-objective alignment and coverage computation.

Two layers:
  CURATED  — hand-written: each CIWT course objective (IT-x.y / NO-x.y) → the exam objectives it serves,
             most relevant first.  This is an instructional-design judgement, pending SME review.
  topics   — each exam objective carries a keyword checklist (exams.py).  Coverage of a lesson, lab or
             item is measured by which checklist topics appear in its text.  This is a heuristic: a topic
             "hit" means the term is taught or used, not that it is taught to exam depth.

Item mapping: an item maps to the curated candidates of its course objective whose topics appear in the
item text (the best-scoring candidate, plus ties); with no hit it maps to the first candidate.  Items may
carry an explicit ``cert`` list, which wins.
"""
import html as _html
import re
from functools import lru_cache

from .exams import EXAMS, OBJECTIVES, sort_key

A1, A2, N = 'A1', 'A2', 'N'



CURATED = {
    # ITSUP — IT Support Technician Fundamentals
    'IT-1.1': ['A2:4.1', 'A2:4.2'], 'IT-1.2': ['A2:4.4', 'A2:4.5'], 'IT-1.3': ['A2:4.1'], 'IT-1.4': ['A2:4.6', 'A2:4.7', 'A2:2.5'],
    'IT-2.1': ['A1:3.5', 'A1:3.3', 'A1:3.4'], 'IT-2.2': ['A1:3.5'], 'IT-2.3': ['A1:5.1', 'A1:3.3'], 'IT-2.4': ['A1:3.5', 'A2:1.4', 'A2:4.1'],
    'IT-3.1': ['A1:3.4', 'A1:5.2'], 'IT-3.2': ['A1:3.4', 'A1:5.2', 'A2:4.3'], 'IT-3.3': ['A1:3.6', 'A1:5.1', 'A1:3.5'], 'IT-3.4': ['A1:3.1', 'A1:3.2', 'A1:5.3'],
    'IT-4.1': ['A1:1.1', 'A1:5.4', 'A1:1.2', 'A2:4.5'], 'IT-4.2': ['A1:1.3', 'A1:1.2', 'A2:2.8', 'A2:3.2', 'A2:3.3'], 'IT-4.3': ['A1:3.7', 'A1:3.8', 'A1:5.6'],
    'IT-5.1': ['A1:2.6', 'A2:1.7', 'N:1.7'], 'IT-5.2': ['A1:2.1', 'A1:2.3', 'N:1.4'], 'IT-5.3': ['A1:5.5', 'A2:1.5', 'N:5.5', 'A1:2.4', 'A1:2.8'],
    'IT-5.4': ['A1:2.2', 'A1:2.6', 'A2:2.10', 'A2:2.3', 'A1:2.5'],
    'IT-6.1': ['A1:4.1'], 'IT-6.2': ['A1:4.2', 'A2:1.11'], 'IT-6.3': ['A1:4.1'],
    'IT-7.1': ['N:5.1'], 'IT-7.2': ['N:5.1', 'A1:5.5'], 'IT-7.3': ['A2:4.7', 'A2:4.1'], 'IT-7.4': ['A2:4.1', 'A2:4.7'],
    'IT-8.1': ['A2:1.2', 'A2:1.3', 'A2:1.1'], 'IT-8.2': ['A2:1.6', 'A2:1.4', 'A2:2.2', 'A2:1.7', 'A2:1.10'], 'IT-8.3': ['A2:3.1', 'A2:1.4', 'A2:1.5'],
    'IT-8.4': ['A2:2.2', 'A2:1.7', 'A2:3.1'],
    'IT-9.1': ['A2:1.9'], 'IT-9.2': ['A2:1.8'], 'IT-9.3': ['A2:2.2', 'A2:1.7', 'A2:4.9'], 'IT-9.4': ['A2:1.1', 'A2:1.7', 'A2:4.9'],
    'IT-10.1': ['A2:2.1', 'A2:2.7', 'A2:2.2'], 'IT-10.2': ['A2:2.4', 'A2:2.5', 'A2:2.6', 'A2:3.4', 'A2:2.11'], 'IT-10.3': ['A2:2.7', 'A2:2.9', 'A2:2.2'],
    'IT-10.4': ['A2:4.6', 'A2:2.5'],
    'IT-11.1': ['A2:3.1'], 'IT-11.2': ['A2:3.1', 'A2:1.2', 'A2:4.2'], 'IT-11.3': ['A2:3.1', 'A2:1.4'], 'IT-11.4': ['A2:3.1', 'A2:1.4'],
    'IT-12.1': ['A2:4.2'], 'IT-12.2': ['A2:4.6', 'A2:4.7', 'A2:4.10'], 'IT-12.3': ['A2:4.3'], 'IT-12.4': ['A2:4.1'],
    'IT-13.1': ['A2:1.5', 'A2:4.8'], 'IT-13.2': ['A2:1.5', 'A1:5.5', 'A2:1.7', 'A2:4.8'], 'IT-13.3': ['A2:1.5', 'A2:1.4'], 'IT-13.4': ['A2:1.5', 'A2:1.6', 'A2:4.8'],
    # (pass 11 appended the last entry of IT-4.2, IT-8.2, IT-9.3, IT-5.3, IT-10.2, IT-10.4, IT-12.2, IT-13.2, NO-2.1, NO-5.2 and
    #  NO-6.3 when the exam-alignment supplements were added to those chapters; see coverage_baseline.json for before)
    # NETOPS — Network Operations
    'NO-1.1': ['N:1.1'], 'NO-1.2': ['N:1.7', 'N:1.8', 'A1:2.6'], 'NO-1.3': ['N:1.4', 'A1:2.1'],
    'NO-2.1': ['N:2.2', 'N:5.3', 'N:1.6'], 'NO-2.2': ['N:2.2', 'N:2.1', 'N:5.3'], 'NO-2.3': ['N:1.5', 'N:5.2', 'N:5.5', 'N:2.4', 'A1:3.2', 'A1:2.8'],
    'NO-3.1': ['N:2.1', 'N:5.3'], 'NO-3.2': ['N:1.3', 'N:3.5', 'N:1.6', 'N:1.8', 'A1:2.7'], 'NO-3.3': ['N:2.3', 'N:5.4', 'A1:2.2'],
    'NO-4.1': ['N:3.4', 'N:5.3'], 'NO-4.2': ['N:3.4', 'A1:2.4'], 'NO-4.3': ['N:2.1', 'N:4.3', 'N:1.2'],
    'NO-5.1': ['N:3.2', 'N:5.4'], 'NO-5.2': ['N:4.3', 'N:3.5', 'N:4.1', 'N:4.2'], 'NO-5.3': ['N:4.1', 'N:1.8', 'N:4.3', 'N:4.2'],
    'NO-6.1': ['N:5.3', 'N:5.4', 'N:5.2'], 'NO-6.2': ['N:5.1', 'N:3.1'], 'NO-6.3': ['N:3.1', 'N:5.1', 'N:3.3', 'N:2.4'],
    'NO-9.1': ['N:2.2', 'N:5.5'], 'NO-9.2': ['N:2.1', 'N:5.5', 'N:3.1'],
}

COURSE_PACKS = (('ITSUP', 'APLUS'), ('NETOPS', 'NETPLUS'))
COURSE_PREFIX = {'ITSUP': 'IT', 'NETOPS': 'NO'}

# thresholds (documented on the coverage page and in CERT_COVERAGE.md)
CONTENT_COVERED = 0.7      # share of an objective's checklist topics present in linked lessons/labs
CONTENT_PARTIAL = 0.25
ITEMS_COVERED = 4          # mapped bank items


# ---------------------------------------------------------------- text + topic matching
_TAG = re.compile(r'<[^>]+>')
_WS = re.compile(r'\s+')


def plain(text):
    return _WS.sub(' ', _html.unescape(_TAG.sub(' ', text or ''))).strip().lower()


@lru_cache(maxsize=None)
def _rx(topic):
    label, _, rx = topic.partition('=')
    return re.compile(rx if rx else r'\b' + re.escape(label.lower()) + r'\b', re.I)


def topic_label(topic):
    return topic.partition('=')[0]


def hits(oid, text):
    """Indices of the exam objective's checklist topics present in ``text`` (already plain/lowercase)."""
    return {i for i, t in enumerate(OBJECTIVES[oid]['topics']) if _rx(t).search(text)}


def chapter_candidates(prefix, ch):
    out = []
    for cobj, xs in CURATED.items():
        if cobj.startswith(f'{prefix}-{ch}.'):
            out += [x for x in xs if x not in out]
    return out


# ---------------------------------------------------------------- curriculum inventory
def lessons_inventory():
    """[(course, chapter, lesson_order, title, plain_text)] from the assembled course packs."""
    import lessons as L
    out = []
    for course, attr in COURSE_PACKS:
        for ch in getattr(L, attr):
            for les in ch['lessons']:
                out.append((course, int(ch['order']), int(les.get('order') or 0), les.get('title') or '', plain(les.get('html'))))
    return out


def labs_inventory():
    """[(lab_id, title, course, chapters, plain_text)] — only labs placed in an ITSUP/NETOPS chapter."""
    import interactive_labs as IL
    where = {}
    for (course, ch), ids in IL.CHAPTER_LABS.items():
        if course in COURSE_PREFIX:
            for lid in ids:
                where.setdefault(lid, set()).add((course, ch))
    out = []
    for lid, places in where.items():
        lab = IL.LABS_BY_ID.get(lid)
        if not lab:
            continue
        txt = plain(' '.join(str(lab.get(k) or '') for k in ('title', 'blurb', 'objectives', 'intro', 'hints')))
        out.append((lid, lab.get('title') or lid, sorted(places), txt))
    return out


def bank_items():
    """Every bank item in the curriculum, as dicts with id/source/obj/text/options/correct/explanation/type/cert."""
    import pilot_slice
    import question_bank
    from curriculum_v2.exam_supplement import SUPPLEMENT
    from curriculum_v2.itsup_core import EXPANSION
    from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload
    out, seen = [], set()

    def add(q, source):
        bid = q.get('bank_id') or q.get('id')
        if not bid or bid in seen:
            return
        seen.add(bid)
        out.append({'id': bid, 'source': source, 'obj': q.get('obj'), 'text': q.get('text') or q.get('prompt') or '',
                    'options': list(q.get('options') or []), 'correct': q.get('correct'), 'explanation': q.get('explanation') or '',
                    'type': q.get('type') or 'single', 'cert': list(q.get('cert') or []), 'raw': q})
    for _t, _d, _o, items in question_bank.tests_aplus() + question_bank.tests_netplus():
        for q in items:
            add(q, 'test')
    for order in pilot_slice.PILOT_CHECKS:
        for q in pilot_slice.quiz_payload(order, ''):
            add(q, 'check')
    for order in NETOPS_CHECKS:
        for q in netops_quiz_payload(order):
            add(q, 'check')
    for q in SUPPLEMENT:
        add(q, 'supplement')
    for q in EXPANSION:
        add(q, 'expansion')
    try:
        from .items import CERT_ITEMS
    except ImportError:
        CERT_ITEMS = []
    for q in CERT_ITEMS:
        add(q, 'cert')
    return out


def item_text(it):
    raw = it['raw']
    parts = [it['text'], ' '.join(map(str, it['options'])), it['explanation']]
    for k in ('items', 'left', 'right', 'scenario'):
        if raw.get(k):
            parts.append(' '.join(map(str, raw[k])) if isinstance(raw[k], (list, tuple)) else str(raw[k]))
    return plain(' '.join(parts))


def map_item(it):
    if it['cert']:
        return [c for c in it['cert'] if c in OBJECTIVES]
    cands = CURATED.get(it['obj'] or '', [])
    if not cands:
        return []
    txt = item_text(it)
    scored = [(len(hits(c, txt)), c) for c in cands]
    best = max(s for s, _ in scored)
    if best == 0:
        return [cands[0]]
    return [c for s, c in scored if s == best][:2]


# ---------------------------------------------------------------- coverage
def _status(content_ratio, n_lessons, n_items):
    if content_ratio >= CONTENT_COVERED and n_lessons:
        content = 'covered'
    elif content_ratio >= CONTENT_PARTIAL and n_lessons:
        content = 'partial'
    else:
        content = 'gap'
    assess = 'covered' if n_items >= ITEMS_COVERED else ('partial' if n_items else 'gap')
    if content == 'covered' and assess == 'covered':
        overall = 'covered'
    elif content == 'gap':
        overall = 'gap'
    else:
        overall = 'partial'
    return content, assess, overall


@lru_cache(maxsize=1)
def compute():
    """Full alignment: {'objectives': {oid: {...}}, 'items': {item_id: [oids]}, 'summary': {exam: {...}}}."""
    lessons = lessons_inventory()
    labs = labs_inventory()
    items = bank_items()
    res = {oid: {'lessons': [], 'labs': [], 'items': [], 'topic_hits': set()} for oid in OBJECTIVES}
    for course, ch, lo, title, txt in lessons:
        cands = set(chapter_candidates(COURSE_PREFIX[course], ch))
        for oid in OBJECTIVES:
            h = hits(oid, txt)
            if not h:
                continue
            n = len(OBJECTIVES[oid]['topics'])
            if (oid in cands and len(h) >= min(2, n)) or len(h) >= max(3, round(0.3 * n)):
                res[oid]['lessons'].append({'course': course, 'chapter': ch, 'lesson': lo, 'title': title, 'hits': len(h)})
                res[oid]['topic_hits'] |= h
    for lid, title, places, txt in labs:
        cands = set()
        for course, ch in places:
            cands |= set(chapter_candidates(COURSE_PREFIX[course], ch))
        for oid in OBJECTIVES:
            h = hits(oid, txt)
            if h and (oid in cands or len(h) >= 3):
                res[oid]['labs'].append({'id': lid, 'title': title, 'places': places})
                res[oid]['topic_hits'] |= h
    item_map = {}
    for it in items:
        oids = map_item(it)
        item_map[it['id']] = oids
        for oid in oids:
            res[oid]['items'].append({'id': it['id'], 'source': it['source'], 'type': it['type'], 'obj': it['obj']})
    out = {}
    for oid, r in res.items():
        o = OBJECTIVES[oid]
        n = len(o['topics'])
        ratio = len(r['topic_hits']) / n if n else 0.0
        content, assess, overall = _status(ratio, len(r['lessons']), len(r['items']))
        r['lessons'].sort(key=lambda x: -x['hits'])
        out[oid] = {
            'exam': o['exam'], 'id': o['id'], 'domain': o['domain'], 'title': o['title'], 'weight': o['weight'],
            'topics_total': n, 'topics_hit': sorted(r['topic_hits']),
            'topics_missing': [topic_label(t) for i, t in enumerate(o['topics']) if i not in r['topic_hits']],
            'content_ratio': round(ratio, 3), 'lessons': r['lessons'], 'labs': r['labs'], 'items': r['items'],
            'content': content, 'assessment': assess, 'status': overall,
        }
    summary = {}
    for ex in EXAMS:
        rows = [v for v in out.values() if v['exam'] == ex]
        s = {k: sum(1 for v in rows if v['status'] == k) for k in ('covered', 'partial', 'gap')}
        s['total'] = len(rows)
        s['weighted_covered'] = min(100.0, round(sum(v['weight'] for v in rows if v['status'] == 'covered'), 1))
        s['weighted_partial'] = round(sum(v['weight'] for v in rows if v['status'] == 'partial'), 1)
        s['items'] = sum(len(v['items']) for v in rows)
        s['topic_ratio'] = round(sum(len(v['topics_hit']) for v in rows) / sum(v['topics_total'] for v in rows), 3)
        summary[ex] = s
    return {'objectives': dict(sorted(out.items(), key=lambda kv: sort_key(kv[0]))), 'items': item_map, 'summary': summary}


def snapshot():
    """JSON-serialisable mapping data (committed as alignment.json)."""
    c = compute()
    return {
        'note': 'Aligned to (not endorsed by) CompTIA exam objectives. Heuristic topic matching; pending SME review.',
        'exams': {k: {kk: v[kk] for kk in ('code', 'name', 'version', 'doc_version', 'url')} for k, v in EXAMS.items()},
        'summary': c['summary'],
        'curated': CURATED,
        'objectives': {oid: {k: v[k] for k in ('title', 'weight', 'content_ratio', 'content', 'assessment', 'status', 'topics_missing')}
                       | {'lessons': [f"{x['course']} {x['chapter']}.{x['lesson']}" for x in v['lessons']],
                          'labs': [x['id'] for x in v['labs']], 'items': [x['id'] for x in v['items']]}
                       for oid, v in c['objectives'].items()},
        'item_map': c['items'],
    }
