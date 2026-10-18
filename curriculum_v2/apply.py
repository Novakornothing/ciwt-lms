"""Apply the pass-8 curriculum layer to the assembled course packs (called at the end of lessons.py)."""
import re
from html import escape

from .itsup_reference import OBJECTIVE_REWRITES, REFERENCE, SOURCES
from .netops_core import CAPSTONE_OBJECTIVES, NETOPS_CORE
from .itsup_core import ITSUP_CORE, SOURCE_KEYS as _CORE_SOURCES, sources_line as _core_sources

CHANGES = []          # [{'course','chapter','lesson','kind','detail'}] — read by the audit and tests


def _log(course, ch, les, kind, detail):
    CHANGES.append({'course': course, 'chapter': ch, 'lesson': les, 'kind': kind, 'detail': detail})


def _lesson(pack, ch_order, les_order):
    for ch in pack:
        if ch.get('order') == ch_order:
            for les in ch['lessons']:
                if int(les.get('order') or 0) == les_order:
                    return les
    return None


def _objective_panel(objs, heading='Lesson objectives'):
    lis = ''.join(f'<li>{o}</li>' for o in objs)
    return (f'<div class="lo-panel"><h4>{heading}</h4><p class="lo-lead">By the end of this lesson you will be able to:</p>'
            f'<ul>{lis}</ul></div>')


_LO = re.compile(r'<div class="lo-panel">.*?</div>', re.S)
_PLAIN = re.compile(r'(<div class="plain-english"><h4>In plain English</h4>)(.*?)(</div>)', re.S)


def apply_itsup(pack, course='ITSUP'):
    for (ch, les_o), rewrites in OBJECTIVE_REWRITES.items():
        les = _lesson(pack, ch, les_o)
        if not les:
            continue
        for old, new in rewrites.items():
            if old in les['html']:
                les['html'] = les['html'].replace(old, new)
                _log(course, ch, les_o, 'objective', f'“{old}” → “{new}”')
    for (ch, les_o), (heading, body, srcs) in REFERENCE.items():
        les = _lesson(pack, ch, les_o)
        if not les or 'class="sublesson reference-depth"' in les['html']:
            continue
        src = ''
        if srcs:
            src = '<p class="ref-sources small">Sources: ' + '; '.join(escape(SOURCES[s]) for s in srcs) + '.</p>'
        les['html'] += (f'\n<section id="reference" class="sublesson reference-depth"><h3>{heading}</h3>{body}{src}</section>')
        _log(course, ch, les_o, 'reference', heading)
    apply_itsup_core(pack, course)
    from .cert.supplements import apply_cert   # pass 11: exam-alignment supplements
    apply_cert(pack, course)


def apply_itsup_core(pack, course='ITSUP'):
    """Passes 9–10: chapters 3–13 core content and measurable lesson objectives (pending SME review)."""
    last = {}
    for (ch, les_o) in ITSUP_CORE:
        last[ch] = max(last.get(ch, 0), les_o)
    for (ch, les_o), spec in ITSUP_CORE.items():
        les = _lesson(pack, ch, les_o)
        if not les or 'class="sublesson core-content"' in les['html']:
            continue
        h = les['html']
        h, n = _LO.subn(lambda _m: _objective_panel(spec['objectives']), h, count=1)
        if not n:
            h = _objective_panel(spec['objectives']) + h
        body = spec['html']
        if spec.get('sources'):
            body += _core_sources(spec['sources'])
        core = f'\n<section id="core" class="sublesson core-content"><h3>Core content</h3>{body}</section>\n'
        m = _PLAIN.search(h)
        h = h[:m.end()] + core + h[m.end():] if m else core + h
        les['html'] = h
        _log(course, ch, les_o, 'core-content', f'pass 9: objectives ({len(spec["objectives"])}) and core content (pending SME review)')


def apply_netops(pack, course='NETOPS'):
    for (ch, les_o), spec in NETOPS_CORE.items():
        les = _lesson(pack, ch, les_o)
        if not les or 'class="sublesson core-content"' in les['html']:
            continue
        h = les['html']
        h, n = _LO.subn(lambda _m: _objective_panel(spec['objectives']), h, count=1)
        if not n:
            h = _objective_panel(spec['objectives']) + h
        h = _PLAIN.sub(lambda m: m.group(1) + f'<p>{spec["plain"]}</p>' + m.group(3), h, count=1)
        core = f'\n<section id="core" class="sublesson core-content"><h3>Core content</h3>{spec["html"]}</section>\n'
        m = _PLAIN.search(h)
        h = h[:m.end()] + core + h[m.end():] if m else core + h
        les['html'] = h
        _log(course, ch, les_o, 'core-content', f'objectives ({len(spec["objectives"])}), plain-English summary and core content')
    for ch, objs in CAPSTONE_OBJECTIVES.items():
        les = _lesson(pack, ch, 4)
        if not les or 'lo-lead' in les['html']:
            continue
        les['html'] = _LO.sub(lambda _m: _objective_panel(objs + ['Explain what you did, and why, in plain language']), les['html'], count=1)
        _log(course, ch, 4, 'objective', 'capstone objectives made specific')
    from .cert.supplements import apply_cert   # pass 11: exam-alignment supplements
    apply_cert(pack, course)
