"""Course objectives for Security (internal code SEC).

Kept out of the global OBJECTIVES dict so existing item-bank audits stay scoped to
IT Support and Network Operations. Mastery and the explanation ladder opt in explicitly.
"""
from curriculum_sec.assemble import course_objectives

REVIEW = 'Pending SME review'

SEC_OBJECTIVES = course_objectives()


def rows_for(chapter=None):
    rows = [(k, v) for k, v in SEC_OBJECTIVES.items()]
    if chapter is not None:
        rows = [(k, v) for k, v in rows if v['chapter'] == chapter]
    return rows
