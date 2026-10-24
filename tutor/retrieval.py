"""Curriculum-grounded retrieval for the AI tutor (Priority 3). Pure Python, deterministic, no network.

Documents are lesson sections, explanation-ladder rungs (plain / analogy / visual / try-it), glossary entries and lab
guides. Ranking is Okapi BM25 over lower-cased word tokens with light suffix stripping. Graded material (quiz, test and
ladder-check answer keys) is never indexed, so the tutor cannot leak an answer key even by accident.
"""
import math
import re
from collections import Counter

STOP = set('''a an and are as at be been but by can could do does did for from how i if in into is it its me my
not of on or so than that the their them then there these they this to was we what when where which who why will
with would you your about should shall may might must i'm im explain tell show help please just really get got make
does doing done also any some more most much very want need know'''.split())
RUNG_KIND = {'R1': 'plain', 'R2': 'analogy', 'R3': 'visual', 'R4': 'try-it'}
_TAG = re.compile(r'<[^>]+>')
_TOK = re.compile(r"[a-z0-9][a-z0-9.+/-]*[a-z0-9+]|[a-z0-9]")
_SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9“"(])')


def plain(html):
    return re.sub(r'\s+', ' ', _TAG.sub(' ', html or '')).replace('&amp;', '&').replace('&nbsp;', ' ').strip()


def stem(w):
    for suf in ('ing', 'ies', 'es', 's', 'ed'):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[:-len(suf)] + ('y' if suf == 'ies' else '')
    return w


def tokens(text):
    return [stem(t) for t in _TOK.findall((text or '').lower()) if t not in STOP]


class Index:
    """BM25 index. docs: dicts with at least 'text' and 'course' (None = every course)."""

    def __init__(self, docs, k1=1.4, b=0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.tf = [Counter(tokens(d['title'] + ' ' + d['title'] + ' ' + d['text'])) for d in docs]
        self.len = [sum(t.values()) for t in self.tf]
        self.avg = (sum(self.len) / len(self.len)) if docs else 1
        df = Counter()
        for t in self.tf:
            df.update(t.keys())
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def search(self, query, course=None, k=6):
        q = [w for w in tokens(query) if w in self.idf]
        out = []
        for i, d in enumerate(self.docs):
            if course and d.get('course') not in (None, course):
                continue
            tf, s = self.tf[i], 0.0
            for w in q:
                f = tf.get(w)
                if f:
                    s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            if s > 0:
                out.append((s, i))
        out.sort(key=lambda x: (-x[0], x[1]))
        return [(s, self.docs[i]) for s, i in out[:k]]

    def coverage(self, query, doc):
        """Share of the question's content words (that the course knows at all) found in one document."""
        q = set(tokens(query))
        if not q:
            return 0.0
        have = set(tokens(doc['title'] + ' ' + doc['text']))
        return len(q & have) / len(q)


def best_sentences(query, text, n=2):
    q = set(tokens(query))
    sents = [s.strip() for s in _SENT.split(text) if 25 <= len(s.strip()) <= 400]
    scored = sorted(((len(q & set(tokens(s))), -i, s) for i, s in enumerate(sents)), reverse=True)
    picked = [x for x in scored[:n] if x[0] > 0]
    return [s for _, _, s in sorted(picked, key=lambda x: -x[1])]


def build_docs(lessons, ladder, glossary, labs):
    """lessons: [(course, label, lesson_title, module_id, lesson_id, sid, heading, html)];
    ladder: {(course, label, sid): entry}; glossary: [(term, definition)]; labs: [(course, lab_dict)]."""
    docs = []
    for course, label, ltitle, mid, lid, sid, heading, html in lessons:
        docs.append({'type': 'lesson', 'course': course, 'label': label, 'lesson': ltitle, 'module_id': mid, 'lesson_id': lid,
                     'sid': sid, 'title': heading, 'text': plain(html)})
    for (course, label, sid), e in ladder.items():
        if e.get('type') != 'section':
            continue
        for r, rung in (e.get('rungs') or {}).items():
            docs.append({'type': 'rung', 'course': course, 'label': label, 'sid': sid, 'rung': r,
                         'kind': RUNG_KIND.get(r, rung.get('kind')), 'title': e.get('heading', sid), 'text': plain(rung.get('html'))})
    for term, definition in glossary:
        docs.append({'type': 'glossary', 'course': None, 'term': term, 'title': term, 'text': definition})
    for course, lab in labs:
        objs = lab.get('objectives') or []
        txt = ' '.join([lab.get('blurb', ''), lab.get('intro', '')] + [o.get('text', '') for o in objs if isinstance(o, dict)])
        docs.append({'type': 'lab', 'course': course, 'lab_id': lab['id'], 'title': lab.get('title', lab['id']), 'text': plain(txt)})
    return docs
