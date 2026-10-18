"""Split a lesson into its concept sections (explanation ladder, schema v1).

A concept section is one ``<section class="sublesson ...">`` block of the lesson HTML. Every lesson in ITSUP, NETOPS
and CLIENT is built from these blocks (pass 19 census: 0 headings outside one). The section id (``sid``) is a slug of
the block's first <h3> heading, with -2, -3 ... for repeats inside the same lesson, so it survives reordering and
edits elsewhere in the lesson. ``r0_sha`` fingerprints the block's student-visible text, so the validator can say
when the original changed after its rungs were written.

Instructor-only notes (<div class="instructor-note">) are removed first, exactly as students see the lesson.
"""
import hashlib
import re
from html import unescape

SECTION_RE = re.compile(r'<section\b(?P<attrs>[^>]*)>(?P<body>.*?)</section>', re.S)
CLASS_RE = re.compile(r'class="(?P<cls>[^"]*)"')
H3_RE = re.compile(r'<h3\b[^>]*>(?P<h>.*?)</h3>', re.S | re.I)
INSTRUCTOR_RE = re.compile(r'<div class="instructor-note">.*?</div>', re.S)
TAG_RE = re.compile(r'<[^>]+>')
WS_RE = re.compile(r'\s+')
LABEL_RE = re.compile(r'^\s*(\d+\.\d+)\b')


def text_of(html):
    return WS_RE.sub(' ', unescape(TAG_RE.sub(' ', html or ''))).strip()


def slug(text):
    s = re.sub(r'[^a-z0-9]+', '-', unescape(text).lower().replace('’', '').replace("'", '')).strip('-')
    return s[:60].rstrip('-') or 'section'


def lesson_label(title):
    """'1.1 The Support Technician Role' -> '1.1' (the key used by ladder files)."""
    m = LABEL_RE.match(title or '')
    return m.group(1) if m else ''


def student_html(html):
    return INSTRUCTOR_RE.sub('', html or '')


def sections(html):
    """Concept sections of a lesson, in page order:
    [{sid, heading, kind (sublesson class, e.g. core/depth/ground), start, end, html, r0_sha}]
    start/end are offsets into student_html(html)."""
    src = student_html(html)
    out, seen = [], {}
    for m in SECTION_RE.finditer(src):
        cm = CLASS_RE.search(m.group('attrs'))
        classes = (cm.group('cls') if cm else '').split()
        if 'sublesson' not in classes:
            continue
        hm = H3_RE.search(m.group('body'))
        heading = text_of(hm.group('h')) if hm else ''
        base = slug(heading)
        seen[base] = seen.get(base, 0) + 1
        sid = base if seen[base] == 1 else f'{base}-{seen[base]}'
        kind = next((c for c in classes if c != 'sublesson'), 'core')
        out.append({'sid': sid, 'heading': heading, 'kind': kind, 'start': m.start(), 'end': m.end(),
                    'html': m.group(0), 'r0_sha': r0_sha(m.group(0))})
    return out


def r0_sha(section_html):
    return hashlib.sha256(text_of(section_html).encode()).hexdigest()[:12]
