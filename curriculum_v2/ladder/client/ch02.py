"""Explanation ladder — CLIENT chapter 2 (Linux, macOS & Cross-Platform Support). Pending SME review.

CLIENT chapter 2 is built from the same lessons as ITSUP chapter 9 (labels 9.1-9.4; identical section ids and
original-section hashes), so this module reuses the ladder authored in curriculum_v2/ladder/itsup/ch09.py by the
same author. The new misconceptions get CLIENT ids (MC-L-CL2-*, same wording and sources), because ids defined in
another ladder module do not resolve.
"""
import copy

from curriculum_v2.ladder.itsup import ch09 as _SRC

SCHEMA = 1
COURSE = 'CLIENT'
CHAPTER = 2
_FROM, _TO = 'MC-L-IT9-', 'MC-L-CL2-'


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
