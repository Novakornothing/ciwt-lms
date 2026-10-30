"""Per-topic teaching packs for the Security course.

Each gN.py file exports BODIES: topic name -> {body, r0, r1, r2, r4, exam}.
Missing files leave those topics on the short lesson until the pack lands.
"""
import importlib.util
from pathlib import Path

BODIES = {}
_ROOT = Path(__file__).parent
for _path in sorted(_ROOT.glob('g*.py')):
    _spec = importlib.util.spec_from_file_location(f'curriculum_sec.bodies.{_path.stem}', _path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    BODIES.update(getattr(_mod, 'BODIES', {}))
