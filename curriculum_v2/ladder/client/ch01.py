"""Explanation ladder — CLIENT chapter 1 (Windows Installation & Client Configuration). Pending SME review.

CLIENT chapter 1 is built from the same lessons as ITSUP chapter 8 (labels 8.1-8.4; identical section ids and
r0 fingerprints, confirmed with tools/ladder_check.py --scaffold), so it uses the same rungs and checks, authored in
curriculum_v2/ladder/itsup/ch08.py by the same author. The new misconceptions get CLIENT ids (MC-L-CL1-*, same wording
and fixes), so each course's tags resolve in its own file and no id is defined twice. If the CLIENT lessons ever
diverge from ITSUP's, the checker marks the changed sections stale here and they need their own rungs.
"""
import copy

from curriculum_v2.ladder.itsup import ch08 as _SRC

SCHEMA = 1
COURSE = 'CLIENT'
CHAPTER = 1
_FROM, _TO = 'MC-L-IT8-', 'MC-L-CL1-'


def _retag(obj):
    if isinstance(obj, dict):
        return {(_retag(k) if isinstance(k, str) else k): _retag(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_retag(v) for v in obj]
    if isinstance(obj, str) and obj.startswith(_FROM):
        return _TO + obj[len(_FROM):]
    return obj


MISCONCEPTIONS = {_TO + k[len(_FROM):]: copy.deepcopy(v) for k, v in _SRC.MISCONCEPTIONS.items()}
LESSONS = _retag(copy.deepcopy(_SRC.LESSONS))
STAMPS = copy.deepcopy(_SRC.STAMPS)
