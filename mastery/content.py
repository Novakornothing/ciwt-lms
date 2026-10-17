"""Find the existing content that teaches an objective, and assemble a short review from it (pass 11).

Nothing here writes curriculum: reviews are excerpts of the lesson pages (sections under an <h3>, the
worked example / scenario, the "In plain English" box, the analogy, the check-for-understanding
questions) plus glossary entries, selected by transparent rules:

* objective → lesson: chapter-check study tips name their lesson ("5.1 — …"), which counts 3 per item;
  plus word overlap between the objective and the lesson title (×2) and the lesson's own objectives panel.
* objective → sections: word overlap between the objective and each <h3> section's heading (×2) and text.

Every choice carries a ``why`` string so the review page can say where the excerpt came from.
"""
import math
import re
from collections import Counter
from html import unescape

STOP = set('''about above after again also among and another any are around because been before being between both
but by can cannot could does doing down during each either every few for from further have having here into its
itself just like made make many more most must not only other over same should since some such than that their
them then there these they this those through under until upon using very what when where which while will with
within without would your yours youre the a an of to in on or is it as at be if you use used uses their them
explain identify apply describe compare select choose common basic using perform recognise recognize
troubleshoot configure verify'''.split())
SKIP_HEADINGS = {'core content', 'pending sme review'}
_TAG = re.compile(r'<[^>]+>')
_WS = re.compile(r'\s+')
_INSTRUCTOR = re.compile(r'<div class="instructor-note">.*?</div>', re.S)
_H3 = re.compile(r'<h3\b[^>]*>(.*?)</h3>', re.S | re.I)
_LABEL = re.compile(r'^\s*(\d+\.\d+)\b')
_TIP_REFS = re.compile(r'(\d+\.\d+)')


def text_of(html):
    return _WS.sub(' ', unescape(_TAG.sub(' ', html or ''))).strip()


def tokens(text):
    out = []
    for w in re.findall(r"[a-z0-9][a-z0-9\-]+", (text or '').lower()):
        w = w.strip('-')
        if len(w) < 3 or w in STOP:
            continue
        if len(w) > 4 and w.endswith('s') and not w.endswith('ss'):
            w = w[:-1]
        out.append(w)
    return out


def overlap(a, b):
    sa, sb = set(a), set(b)
    return len(sa & sb)


def lesson_label(title):
    m = _LABEL.match(title or '')
    return m.group(1) if m else ''


def _div_blocks(html, cls):
    """Balanced <div class="… cls …"> … </div> blocks, in order."""
    out = []
    pat = re.compile(r'<div class="([^"]*)"', re.I)
    for m in pat.finditer(html or ''):
        if cls not in m.group(1).split():
            continue
        depth, i = 0, m.start()
        for t in re.finditer(r'<div\b|</div>', html[m.start():], re.I):
            depth += 1 if t.group(0).lower().startswith('<div') else -1
            if depth == 0:
                out.append(html[i:m.start() + t.end()])
                break
    # drop blocks nested inside an earlier block
    keep = []
    for b in out:
        if not any(b != k and b in k for k in keep):
            keep.append(b)
    return keep


def _remove_blocks(html, cls):
    for b in _div_blocks(html, cls):
        html = html.replace(b, '')
    return html


def clean(html):
    """Student-safe excerpt: no teaching notes, lab launchers, figures, ids or scripts (ids would collide)."""
    h = _INSTRUCTOR.sub('', html or '')
    for cls in ('instructor-note', 'lab-panel', 'live-demo'):
        h = _remove_blocks(h, cls)
    h = re.sub(r'<figure\b.*?</figure>', '', h, flags=re.S | re.I)
    h = re.sub(r'<(script|style|svg)\b.*?</\1>', '', h, flags=re.S | re.I)
    h = re.sub(r'\s(id|aria-labelledby|aria-describedby|for)="[^"]*"', '', h)
    return h.strip()


def sections(html):
    """Split a lesson into <h3> sections: [{'heading', 'html', 'text', 'order'}]."""
    h = html or ''
    marks = list(_H3.finditer(h))
    out = []
    for i, m in enumerate(marks):
        head = text_of(m.group(1))
        end = marks[i + 1].start() if i + 1 < len(marks) else len(h)
        body = h[m.end():end]
        if head.lower() in SKIP_HEADINGS:
            continue
        txt = text_of(body)
        if len(txt) < 120:
            continue
        out.append({'heading': head, 'html': body, 'text': txt, 'order': i})
    return out


def lesson_objectives_text(html):
    b = _div_blocks(html, 'lo-panel')
    return text_of(b[0]) if b else ''


def tip_votes(items):
    """{obj: Counter(lesson label)} from chapter-check study tips ('5.1 — …', '1.1 / 1.4 — …')."""
    votes = {}
    for it in items or []:
        obj, tip = it.get('obj'), (it.get('study_tip') or '')
        if not obj or not tip:
            continue
        head = tip.split('—')[0]
        refs = _TIP_REFS.findall(head)
        if not refs:
            continue
        c = votes.setdefault(obj, Counter())
        c[refs[0]] += 1
    return votes


def map_objective(obj, obj_text, chapter, lessons, votes=None):
    """Best lesson for an objective among ``lessons`` (dicts: id, label, title, html) of its chapter.
    Returns {'lesson': dict, 'score': float, 'why': str} or None."""
    ot = tokens(obj_text)
    best = None
    v = (votes or {}).get(obj) or Counter()
    for les in lessons:
        tip = v.get(les['label'], 0)
        t_title = overlap(ot, tokens(les['title']))
        t_lo = overlap(ot, tokens(lesson_objectives_text(les['html'])))
        score = 3 * tip + 2 * t_title + 1.0 * t_lo
        why = []
        if tip:
            why.append(f"{tip} chapter-check item{'s' if tip > 1 else ''} on this objective point to lesson {les['label']}")
        if t_title or t_lo:
            why.append('the objective’s wording matches the lesson title or its objectives')
        cand = (score, -les.get('order', 0), les, why)
        if best is None or cand[:2] > best[:2]:
            best = cand
    if not best:
        return None
    score, _o, les, why = best
    if score <= 0:
        why = ['no lesson matched by wording, so the first lesson of the chapter is used']
    return {'lesson': les, 'score': score, 'why': '; '.join(why)}


def pick_sections(obj_text, secs, n=2, exclude=()):
    ot = tokens(obj_text)
    scored = []
    for s in secs:
        if s['heading'] in exclude:
            continue
        sh = overlap(ot, tokens(s['heading']))
        st = overlap(ot, tokens(s['text']))
        score = 2 * sh + st / math.sqrt(1 + len(s['text']) / 1500.0)
        scored.append((score, -s['order'], s))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [s for sc, _o, s in scored[:n] if sc > 0] or [s for _sc, _o, s in scored[:1]]


def glossary_for(text, glossary, limit=4, marked=()):
    """Glossary entries whose term appears in ``text`` (whole word, case-insensitive)."""
    low = ' ' + (text or '').lower() + ' '
    out = []
    for term, definition in glossary or []:
        base = re.sub(r'\s*\(.*?\)\s*', ' ', term).strip().lower()
        if len(base) < 3:
            continue
        if re.search(r'(?<![a-z0-9])' + re.escape(base) + r'(?![a-z0-9])', low):
            out.append({'term': term, 'definition': definition, 'pending': term in marked})
    out.sort(key=lambda g: -len(g['term']))
    return out[:limit]


def build_review(obj, obj_text, lesson, variant='review', chapter_lessons=(), glossary=(), marked=()):
    """Assemble review blocks from existing content. variant: 'review' or 'alt' (alternate explanation)."""
    html = lesson['html'] if lesson else ''
    secs = sections(html)
    blocks = []
    first = pick_sections(obj_text, secs, n=2)
    if variant == 'alt':
        plain = _div_blocks(html, 'plain-english')
        analogy = _div_blocks(html, 'analogy-box')
        example = _div_blocks(html, 'worked-example') or _div_blocks(html, 'scenario-box')
        if not example:
            for other in chapter_lessons:
                example = _div_blocks(other['html'], 'worked-example') or _div_blocks(other['html'], 'scenario-box')
                if example:
                    break
        for kind, label, items in (('plain', 'In plain English', plain[:1]), ('analogy', 'An analogy', analogy[:1]),
                                   ('example', 'Worked through step by step', example[:1])):
            for b in items:
                blocks.append({'kind': kind, 'label': label, 'html': clean(b)})
        other_secs = pick_sections(obj_text, secs, n=1, exclude={s['heading'] for s in first[:1]})
        for s in other_secs:
            blocks.append({'kind': 'section', 'label': s['heading'], 'html': clean(s['html'])})
    else:
        for s in first:
            blocks.append({'kind': 'section', 'label': s['heading'], 'html': clean(s['html'])})
        example = _div_blocks(html, 'worked-example')
        if example and not any(example[0] in s['html'] for s in first):
            blocks.append({'kind': 'example', 'label': 'Worked example', 'html': clean(example[0])})
    cfu = [b for b in _div_blocks(html, 'check-box')][:1]
    for b in cfu:
        if not any(b in x['html'] for x in blocks):
            blocks.append({'kind': 'cfu', 'label': 'Check yourself', 'html': clean(b)})
    text = obj_text + ' ' + ' '.join(text_of(b['html']) for b in blocks)
    return {'obj': obj, 'variant': variant, 'blocks': [b for b in blocks if b['html']],
            'glossary': glossary_for(text, glossary, marked=marked),
            'lesson': lesson}


def _term_score(terms, text):
    low = ' ' + (text or '').lower() + ' '
    score = 0.0
    for t in terms or []:
        n = len(re.findall(r'(?<![a-z0-9])' + re.escape(t.lower()) + r'(?![a-z0-9])', low))
        score += min(n, 4) * (1.5 if ' ' in t else 1.0)
    return score


def build_correction(obj, obj_text, mc, lesson, chapter_lessons=(), glossary=(), marked=()):
    """Corrective explanation for one misconception: the lesson sections (mapped lesson first, then the rest of
    the chapter) that best address the misconception's terms. Framing text comes from the template."""
    cands = []
    seen = set()
    for les in ([lesson] if lesson else []) + [x for x in chapter_lessons if not lesson or x['id'] != lesson['id']]:
        if les['id'] in seen:
            continue
        seen.add(les['id'])
        for s in sections(les['html']):
            sc = _term_score(mc.get('terms'), s['heading'] + ' ' + s['text']) + 0.5 * overlap(tokens(obj_text), tokens(s['heading']))
            if sc > 0:
                cands.append((sc + (0.5 if lesson and les['id'] == lesson['id'] else 0), -s['order'], les, s))
    cands.sort(key=lambda x: (x[0], x[1]), reverse=True)
    blocks = []
    for sc, _o, les, s in cands[:2]:
        blocks.append({'kind': 'section', 'label': s['heading'], 'html': clean(s['html']), 'lesson': les['label']})
    if not blocks and lesson:
        for s in pick_sections(obj_text, sections(lesson['html']), n=1):
            blocks.append({'kind': 'section', 'label': s['heading'], 'html': clean(s['html']), 'lesson': lesson['label']})
    text = ' '.join(mc.get('terms') or []) + ' ' + ' '.join(text_of(b['html']) for b in blocks)
    return {'obj': obj, 'variant': 'mc', 'blocks': [b for b in blocks if b['html']],
            'glossary': glossary_for(text, glossary, marked=marked), 'lesson': lesson}
