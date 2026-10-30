"""Lesson-depth packs for Security: core essay, exam focus, and distinct paths.

Packs live in curriculum_sec/bodies/. A lesson grows only when every topic in
it has a pack, so a partial batch cannot leave one idea in a lesson unwritten.
"""
import hashlib
import re

from curriculum_sec.bodies import BODIES
from curriculum_sec.gloss import GLOSS

_BANNED = (
    'cyber' + 'security', 'cyber' + ' ' + 'security', 'ciwt', 'guarantee', 'pass rate', 'pass-rate',
    'official comptia', 'endorsed',
)


def lesson_ready(headings):
    return bool(headings) and all(h in BODIES for h in headings)


def _words(text):
    return re.sub(r'\s+', ' ', text or '').strip().split()


def _sentences(text):
    text = re.sub(r'\s+', ' ', (text or '').replace('\n', ' ')).strip()
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def _paragraphs(text):
    chunks = [c.strip() for c in re.split(r'\n\s*\n', text or '') if c.strip()]
    if len(chunks) <= 1:
        sentences = _sentences(text)
        chunks, buf = [], []
        for sentence in sentences:
            buf.append(sentence)
            if len(_words(' '.join(buf))) >= 70:
                chunks.append(' '.join(buf))
                buf = []
        if buf:
            chunks.append(' '.join(buf))
    return chunks


def _check_banned(text, where):
    low = (text or '').lower()
    for bad in _BANNED:
        if bad in low:
            raise ValueError(f'{where} contains banned wording {bad!r}')


def pack(heading):
    return BODIES.get(heading)


def r0_sentences(heading):
    row = pack(heading)
    if not row:
        return []
    _check_banned(row.get('r0', ''), heading)
    return _sentences(row.get('r0', ''))


def path_sentences(heading, field):
    row = pack(heading)
    if not row:
        return None
    _check_banned(row.get(field, ''), f'{heading} {field}')
    return _sentences(row.get(field, ''))


def _cast(names):
    digest = hashlib.sha256('|'.join(names).encode()).digest()
    first = ('Mara', 'Luis', 'Priya', 'Owen', 'Helen', 'Jonah', 'Aisha', 'Chris', 'Nora', 'Evan')
    last = ('Chen', 'Ortiz', 'Shah', 'Brooks', 'Nguyen', 'Patel', 'Diaz', 'Okeke', 'Berg', 'Silva')
    person = f'{first[digest[0] % len(first)]} {last[digest[1] % len(last)]}'
    host = f'host-{digest[2]:02x}{digest[3]:02x}'
    ticket = str(4000 + int.from_bytes(digest[4:6], 'big') % 5000)
    return person, host, ticket


def core_chunks(headings):
    """Plain paragraphs for the core-content section. Each topic's body is used once."""
    if not lesson_ready(headings):
        return []
    person, host, ticket = _cast(headings)
    listed = ', '.join(headings[:-1]) + ', and ' + headings[-1] if len(headings) > 1 else headings[0]
    chunks = [
        f'{person} opens ticket {ticket} on {host}.',
        f'{ticket} is about {listed}.',
    ]
    for heading in headings:
        body = pack(heading)['body']
        _check_banned(body, heading)
        chunks.append(heading)
        chunks.extend(_paragraphs(body))
    return chunks


def exam_sentences(headings):
    if not lesson_ready(headings):
        return []
    out = []
    for heading in headings:
        text = (pack(heading).get('exam') or '').strip()
        _check_banned(text, f'{heading} exam')
        if text:
            out.extend(_sentences(text))
    return out


def core_why(headings):
    second = headings[1] if len(headings) > 1 else 'a neighboring idea'
    return (
        f'{headings[0]} matches this evidence on the ticket. {second} names a different fact.'
    )
