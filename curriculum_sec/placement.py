"""Placement items for Security, three per chapter.

Skip What You Know is on the learner-features branch. These rows match
learner/placement_bank.py: (course, chapter, letter, prompt, correct, wrong, wrong, wrong).
Append them when that module is wired. Objective tags are the lesson skill ids.
"""
from curriculum_sec.catalog import CHAPTERS

_EXTRA = [
    'Ignore it until next quarter',
    'Put the secret in the ticket',
    'Turn logging off',
]


def rows():
    out = []
    for ch in CHAPTERS:
        picked = ch['lessons'][:3]
        letters = 'abc'
        for les, letter in zip(picked, letters):
            sec = les['sections'][0]
            wrongs = [sec['bad'][0], sec['bad'][1], _EXTRA[0]]
            if sec['key'] in wrongs:
                wrongs[2] = _EXTRA[1]
            out.append((
                'SEC', ch['order'], letter,
                sec['note'].rstrip('.') + '. What is the right call?',
                sec['key'], wrongs[0], wrongs[1], wrongs[2],
                les['skill'],
            ))
    return out


ROWS = rows()
