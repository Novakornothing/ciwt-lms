"""Pass 11: exam-alignment supplements appended to existing lessons (no lessons are added or removed).

Each supplement is a ``<section class="sublesson cert-supplement">`` with core content, a described diagram,
a worked example, a scenario, checks for understanding, key terms and sources, tagged Pending SME review
(the instructor-note block is stripped from student views by app.render_lesson).
"""
import importlib
import pkgutil
from html import escape

from . import content as _pkg
from .authoring import sources_line
from .exams import label

MODULES = [importlib.import_module(f'{_pkg.__name__}.{m.name}')
           for m in sorted(pkgutil.iter_modules(_pkg.__path__), key=lambda m: m.name) if m.name.startswith('s')]

SUPPLEMENTS = [s for m in MODULES for s in m.SUPPLEMENTS]
GLOSSARY = [g for m in MODULES for g in m.GLOSSARY]
ITEMS = [q for m in MODULES for q in m.ITEMS]
_TERMS = {m.__name__: m.GLOSSARY for m in MODULES}
_OWNER = {id(s): m.__name__ for m in MODULES for s in m.SUPPLEMENTS}
APPLIED = []   # [(course, chapter, lesson, id)]


def section_html(spec, with_terms=True):
    aligned = ', '.join(label(c) for c in spec['cert'])
    terms = ''
    if with_terms:
        gl = _TERMS[_OWNER[id(spec)]]
        if gl:
            terms = ('<div class="key-terms"><h4>Key terms</h4><dl>'
                     + ''.join(f'<dt>{escape(t)}</dt><dd>{escape(d)}</dd>' for t, d in gl) + '</dl></div>')
    return (f'\n<section id="{spec["id"]}" class="sublesson cert-supplement"><h3>{escape(spec["title"])}</h3>'
            f'<p class="cert-tag small">Exam alignment: {escape(aligned)} (aligned to the published CompTIA objectives; '
            f'not CompTIA-endorsed).</p>{spec["html"]}{terms}{sources_line(spec["sources"])}</section>\n')


def apply_cert(pack, course):
    from curriculum_v2.apply import _lesson, _log
    for spec in SUPPLEMENTS:
        if spec['course'] != course:
            continue
        les = _lesson(pack, spec['chapter'], spec['lesson'])
        if not les or f'id="{spec["id"]}"' in les['html']:
            continue
        les['html'] += section_html(spec)
        APPLIED.append((course, spec['chapter'], spec['lesson'], spec['id']))
        _log(course, spec['chapter'], spec['lesson'], 'cert-supplement', f'{PASS_LABEL}: {spec["title"]}')


PASS_LABEL = 'pass 11 exam-alignment supplement (pending SME review)'
