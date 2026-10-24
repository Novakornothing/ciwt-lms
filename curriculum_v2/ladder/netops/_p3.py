"""Option B pass 3 NETOPS kit: wires the bespoke ladders (_p3nN.py) into a chapter, replacing the old templated
practice/capstone blocks from _gen and the core-concepts / network-operations-depth same_as entries. Pending SME review.
Not a chapter module (the loader only imports ch*.py)."""
from functools import partial

from curriculum_v2.ladder.itsup._p2 import P3
from curriculum_v2.ladder.netops._kit import ops_mcs

N = partial(P3, 'NETOPS')


def src(label, title):
    return f'Course lesson {label} “{title}” (the original section), re-explained'


def mc(label):
    """Per-lesson process misconception ids: mc('2.2')('NEG') -> 'MC-L-NO22-NEG'."""
    code = 'NO' + label.replace('.', '')
    return lambda k: f'MC-L-{code}-{k}'


def wire(lessons, mcs_out, secs, cap_obj):
    """Register the per-lesson process misconceptions and put every bespoke section in place."""
    for label, entries in lessons.items():
        mine = {sid: e for (lb, sid), e in secs.items() if lb == label}
        if not mine:
            continue
        code = 'NO' + label.replace('.', '')
        obj = cap_obj if label.endswith('.4') else f'NO-{label}'
        mcs_out.update(ops_mcs(code, obj, f'Course lesson {label} (the original section), re-explained'))
        for sid, e in mine.items():
            assert sid in entries, (label, sid)
            entries[sid] = e
        left = [sid for sid, e in entries.items() if e.get('type') in ('skip', 'same_as')]
        assert not left, (label, left)
