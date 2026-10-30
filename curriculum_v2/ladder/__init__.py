"""Explanation ladder (pass 19): per-section alternative explanations, loaded from one module per chapter.

Layout (one file per chapter so parallel authors never edit the same file):

  curriculum_v2/ladder/itsup/ch01.py ... ch13.py
  curriculum_v2/ladder/netops/ch01.py ... (plus netops_07.py, netops_08.py)
  curriculum_v2/ladder/client/ch01.py ...

Each module defines SCHEMA = 1, COURSE, CHAPTER (the chapter's order in its course), LESSONS = {lesson label:
{sid: entry}}, STAMPS = {lesson label: {sid: r0_sha}} (from tools/ladder_check.py --stamp) and optionally
MISCONCEPTIONS (new MC-L-* ids). Modules are discovered automatically; nothing else
has to be edited to add a chapter. See schema.py for the entry helpers and docs/EXPLANATION_LADDER.md.
"""
import importlib
import pkgutil

from . import schema as S

COURSE_PACKAGES = {'ITSUP': 'itsup', 'NETOPS': 'netops', 'CLIENT': 'client', 'SEC': 'sec'}
_EXTENDED_CHAPTERS = {('NETOPS', 7), ('NETOPS', 8)}
_CACHE = {}


def modules(include_extended=False):
    """All ladder modules, sorted by course and chapter."""
    key = 'mods_all' if include_extended else 'mods'
    if key not in _CACHE:
        out = []
        for course, pkg in COURSE_PACKAGES.items():
            p = importlib.import_module(f'{__name__}.{pkg}')
            for info in sorted(pkgutil.iter_modules(p.__path__), key=lambda i: i.name):
                if info.name.startswith('ch'):
                    mod = importlib.import_module(f'{p.__name__}.{info.name}')
                    if not include_extended and (getattr(mod, 'COURSE', None), getattr(mod, 'CHAPTER', None)) in _EXTENDED_CHAPTERS:
                        continue
                    out.append(mod)
        _CACHE[key] = out
    return _CACHE[key]


def extended_modules():
    """Extended pilot ladder modules (e.g. NETOPS Chapters 7 and 8: netops_07 / netops_08)."""
    return [m for m in modules(include_extended=True)
            if (getattr(m, 'COURSE', None), getattr(m, 'CHAPTER', None)) in _EXTENDED_CHAPTERS]


def _build():
    if 'ladder' in _CACHE:
        return
    ladder, all_lad, mcs, where, dup = {}, {}, {}, {}, []
    for mod in modules(include_extended=True):
        is_ext = (getattr(mod, 'COURSE', None), getattr(mod, 'CHAPTER', None)) in _EXTENDED_CHAPTERS
        for mid, m in (getattr(mod, 'MISCONCEPTIONS', {}) or {}).items():
            if mid in mcs:
                dup.append(f'misconception {mid} defined in {where[mid]} and {mod.__name__}')
            mcs[mid] = m
            where[mid] = mod.__name__
        stamps = getattr(mod, 'STAMPS', {}) or {}
        for label, secs in (getattr(mod, 'LESSONS', {}) or {}).items():
            for sid, ent in secs.items():
                k = (mod.COURSE, label, sid)
                if ent.get('type') == 'section' and not ent.get('r0_sha') and (stamps.get(label) or {}).get(sid):
                    ent = dict(ent, r0_sha=stamps[label][sid])
                if k in all_lad:
                    dup.append(f'{k} defined in {where[k]} and {mod.__name__}')
                rec = dict(ent, course=mod.COURSE, label=label, sid=sid, module=mod.__name__)
                if is_ext:
                    all_lad[k] = rec
                else:
                    ladder[k] = rec
                where[k] = mod.__name__
    _CACHE.update(ladder=ladder, ext_ladder=all_lad, mcs=mcs, dup=dup)


def ladder():
    _build()
    return _CACHE['ladder']


def all_ladder():
    """Full ladder dict including extended NETOPS Chapters 7 and 8 modules."""
    _build()
    return {**_CACHE['ext_ladder'], **_CACHE['ladder']}


def misconceptions():
    _build()
    return _CACHE['mcs']


def duplicates():
    _build()
    return _CACHE['dup']


def extended_ladder():
    """Extended ladder entries (e.g. NETOPS Chapters 7 and 8: netops_07 / netops_08)."""
    _build()
    return _CACHE['ext_ladder']


def entry(course, label, sid):
    """The ladder for one section, with same_as resolved; None when the section has none (or is a skip)."""
    _build()
    base = _CACHE['ladder']
    ext = extended_ladder()
    e = base.get((course, label, sid)) or ext.get((course, label, sid))
    if e and e.get('type') == 'same_as':
        t = (course, label, e['target'])
        e = base.get(t) or ext.get(t)
    return e if e and e.get('type') == 'section' else None


def rung_checks(ent, rung):
    """Checks for R0..R4 of a section, finalised: stable id, shuffled options, misconception tags."""
    src = ent['checks'] if rung == 'R0' else ent['rungs'][rung]['checks']
    out = []
    for i, c in enumerate(src):
        out.append({'id': S.check_id(ent['course'], ent['label'], ent['sid'], rung, i), 'q': c['q'],
                    'options': S.options(c), 'correct': c['correct'], 'why': c['why'], 'mc': c.get('mc') or {},
                    'obj': ent['obj'], 'review': c.get('review')})
    return out


def reset_cache():
    _CACHE.clear()
