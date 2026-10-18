"""Misconception tags for pass-11 certification items (round 2), in the schema used by the adaptive engine on
the ``refinement`` branch (curriculum_v2/misconceptions.py, read by mastery/):

    MISCONCEPTIONS[id] = {obj, label (the wrong idea, in plain words), fix (what the lesson shows instead),
                          terms (words used to find the lesson section that addresses it)}
    TAGS[(bank_id, distractor)] = misconception id

``obj`` is the CIWT objective of the items the tag is used on (the engine only honours a tag whose ``obj``
equals the item's ``obj``).  Tags are written per wrong option with the ``mc=`` argument of the single/multi
builders; a distractor is tagged only when the wrong idea it signals is clear from the item and its
explanation.  Throw-away distractors stay untagged, as on refinement.  Order and match items carry no tags
(the engine scores single-answer choices).  Ids use the ``MC-C-`` prefix so they cannot collide with
refinement's ``MC-IT``/``MC-NO`` ids.

After the merge, refinement's module can take these in with::

    from curriculum_v2.cert import misconceptions as _cert_mc
    MISCONCEPTIONS.update(_cert_mc.MISCONCEPTIONS); TAGS.update(_cert_mc.TAGS)
    _NORM.update({(b, _norm(d)): mc for (b, d), mc in _cert_mc.TAGS.items()})
"""
import importlib
import pkgutil

from . import content as _pkg
from .items import CERT_ITEMS

_MODS = [importlib.import_module(f'{_pkg.__name__}.{m.name}')
         for m in sorted(pkgutil.iter_modules(_pkg.__path__), key=lambda m: m.name) if m.name.startswith(('s', 'i'))]

MISCONCEPTIONS = {}
for _m in _MODS:
    for _k, _v in getattr(_m, 'MISCONCEPTIONS', {}).items():
        assert _k.startswith('MC-C-') and _k not in MISCONCEPTIONS, _k
        MISCONCEPTIONS[_k] = _v

TAGS = {(q['bank_id'], d): mc for q in CERT_ITEMS for d, mc in (q.get('mc') or {}).items()}


def _norm(s):
    return ' '.join((s or '').replace('\u2019', "'").lower().split())


_NORM = {(b, _norm(d)): mc for (b, d), mc in TAGS.items()}


def tag_for(item, answer):
    """Same contract as refinement's curriculum_v2.misconceptions.tag_for."""
    if not item or answer is None or answer == item.get('correct'):
        return None
    mc = _NORM.get((item.get('bank_id'), _norm(answer)))
    if mc and MISCONCEPTIONS[mc]['obj'] == item.get('obj'):
        return mc
    return None


def coverage():
    return sorted({m['obj'] for m in MISCONCEPTIONS.values()}), len(TAGS), len(MISCONCEPTIONS)
