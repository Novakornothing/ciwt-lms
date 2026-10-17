"""Course-package additions for the labs added on the ``labs`` branch (pass L1).

Kept separate from course_package.py so curriculum edits there merge cleanly. course_package applies these with two
one-line hooks: KIND_EQUIPMENT.update(EXTRA_KIND_EQUIPMENT) and pacing() → augment_pacing().
Pure data + functions; must not import course_package (it is imported by it).
"""
import re

EXTRA_KIND_EQUIPMENT = {
    'vm': {
        'equipment': 'A real Linux VM that boots inside the browser (v86 emulator + Buildroot Linux; ~12.5 MB download once, '
                     'then cached). Desktop or laptop recommended; recent phones work (see the lab page for timings).',
        'real': 'Any Linux machine or VM: the commands are identical (BusyBox; on Ubuntu use sudo adduser instead of adduser -D).',
        'low_cost': 'The in-browser VM is the low-cost option: nothing to install. Offline: Ubuntu in VirtualBox, WSL or a Raspberry Pi.',
        'reflection': ['Which of your commands changed the system, and how did you prove each change?',
                       'What did the real error messages tell you that a simulator might not?',
                       'Explain 640 in words: owner, group, others.'],
        'troubleshooting': ['adduser complains about /home: BusyBox still creates the account — check with id tech1.',
                            'Permission denied running ./check.sh means the x bit is missing (chmod +x).',
                            'If the VM is slow on a phone, close other tabs; Restart VM gives a clean machine.'],
    },
    'linux': {
        'equipment': 'LMS Linux shell simulator (bash-style; any modern browser, phone or desktop).',
        'real': 'A Linux VM or server (Ubuntu/Debian) with a standard user account and sudo for the steps that need it.',
        'low_cost': 'Ubuntu in VirtualBox or Hyper-V, Windows Subsystem for Linux (WSL), or a Raspberry Pi. '
                    'Paper alternative: printed ls -l output to annotate.',
        'reflection': ['Which command changed the system, and which only read it?',
                       'Read one ls -l permission string aloud: owner, group, others.',
                       'Which Windows command did you reach for first, and what is the Linux equivalent?'],
        'troubleshooting': ['Linux is case-sensitive: App.log and app.log are different files.',
                            'Permission denied usually means a missing r, w or x bit — check with ls -l before using sudo.',
                            'Press Tab to complete file names; pwd shows where you are.'],
    },
    'activity': {
        'equipment': 'LMS interactive activity (browser; drag and drop, tap or keyboard — works on phones).',
        'real': 'The matching classroom hardware, router admin page or hypervisor where the activity names one.',
        'low_cost': 'Printed activity cards (the lab manual lists every item) and a pencil.',
        'reflection': ['Which answer did you change after feedback, and what made you change it?',
                       'Where would you meet this decision on the job?',
                       'What would you check on real equipment before trusting your answer?'],
        'troubleshooting': ['Feedback names the first item that is wrong — fix that one and check again.',
                            'On a phone, tap an item and then tap where it goes; the move buttons reorder lists.'],
    },
}


def _new_chapter_labs():
    import interactive_labs  # noqa: F401  (installs the new labs)
    import labs_catalog_new
    return labs_catalog_new.NEW_CHAPTER_LABS


def _chapters_in(text):
    """'Ch 1 (1.4–1.5); Ch 2 …' → [1, 2];  'Ch 1–2' → [1, 2]."""
    out = []
    for a, b in re.findall(r'Ch\.?\s*(\d+)(?:\s*[–-]\s*(\d+))?', text or ''):
        lo, hi = int(a), int(b or a)
        out += [c for c in range(lo, hi + 1) if c not in out]
    return out


def augment_pacing(code, rows):
    """Append the new LMS labs to the last pacing week that teaches each chapter (originals unchanged)."""
    try:
        chapter_labs = _new_chapter_labs()
    except Exception:
        return rows
    last = {}
    for i, r in enumerate(rows):
        for ch in _chapters_in(r.get('topics')):
            last[ch] = i
    for ch, i in sorted(last.items()):
        ids = chapter_labs.get((code, ch)) or []
        cell = rows[i].get('lab') or ''
        add = [x for x in ids if x not in cell]
        if add:
            rows[i]['lab'] = (cell + '; ' if cell else '') + '; '.join(add)
    return rows
