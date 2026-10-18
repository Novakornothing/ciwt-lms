"""Pass 14: no ITSUP chapter-check item is left with a rationale that is only a section reference."""
import re

import pilot_slice as PS
from curriculum_v2 import item_review as IR
from curriculum_v2.rationales_pass14 import RATIONALE


def _rest(e):
    return re.sub(r'^[\d\s./]+(overview)?\.?\s*(—|-)?\s*', '', (e or '').strip())


def test_no_chapter_check_rationale_is_only_a_section_reference():
    terse = [q['bank_id'] for ch in sorted(PS.PILOT_CHECKS) for q in PS.quiz_payload(ch, '')
             if len(_rest(q['explanation']).split()) < 4]
    assert terse == []


def test_new_rationales_were_applied_keep_the_pointer_and_name_the_key_idea():
    assert set(IR.RATIONALE_UPDATED) == set(RATIONALE)            # only filled where no rationale existed
    by = {q['bank_id']: q for ch in sorted(PS.PILOT_CHECKS) for q in PS.quiz_payload(ch, '')}
    for k, why in RATIONALE.items():
        q = by[k]
        assert q['explanation'] == why and len(why) > 100
        assert re.search(r'See \d+(\.\d+)?( overview)?[ ./\d]*\.$', why), k   # original section pointer kept
