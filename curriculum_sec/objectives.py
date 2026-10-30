"""Course objectives for Security (internal code SEC).

Kept out of the global OBJECTIVES dict so existing item-bank audits stay scoped to
IT Support and Network Operations. Mastery and the explanation ladder opt in explicitly.
"""

REVIEW = 'Pending SME review'


def _rows():
    from curriculum_sec.catalog import CHAPTERS
    out = []
    for ch in CHAPTERS:
        for les in ch['lessons']:
            out.append((les['skill'], ch['order'], les['objective'], 'Apply'))
    return out


_ROWS = _rows()

SEC_OBJECTIVES = {
    oid: {'course': 'SEC', 'chapter': ch, 'text': text, 'bloom': bloom}
    for oid, ch, text, bloom in _ROWS
}


def rows_for(chapter=None):
    rows = [(k, v) for k, v in SEC_OBJECTIVES.items()]
    if chapter is not None:
        rows = [(k, v) for k, v in rows if v['chapter'] == chapter]
    return rows
