"""Pass 11 bank items: supplement-module items plus depth items for objectives that had fewer than four.

Item types: ``single`` (one key), ``multi`` (choose N), ``order`` (put steps in sequence) and ``match``
(match each prompt to a choice).  Keys stay server-side: see practice.public_item().
"""
import importlib
import pkgutil

from . import content as _pkg
from .authoring import finalise

_MODS = [importlib.import_module(f'{_pkg.__name__}.{m.name}')
         for m in sorted(pkgutil.iter_modules(_pkg.__path__), key=lambda m: m.name) if m.name.startswith(('s', 'i'))]
from .sources_round7 import apply as _cite
CERT_ITEMS = _cite(finalise([q for m in _MODS for q in m.ITEMS]))
BY_ID = {q['bank_id']: q for q in CERT_ITEMS}
