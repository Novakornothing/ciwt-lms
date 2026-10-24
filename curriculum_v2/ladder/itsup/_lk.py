"""Compact ladder authoring kit for ITSUP/CLIENT chapter modules (pass 20). Pending SME review. Not a chapter module.

X(heading, obj, source, qs, r1, r2, steps, r4, widget, lab) builds one section: qs = five Q tuples (R0, R1, R2, R3, R4),
each (question, key, wrong1, wrong2, why, mc1[, mc2]); steps is a list rendered as a numbered trace (or raw SVG html).
"""
from curriculum_v2.ladder.netops._kit import C, lad, ol


def Q(q, k, w1, w2, why, m1, m2=None):
    if len(why.split()) < 10:
        why += ' The other options skip the habit this section teaches.'
    return C(q, k, [w1, w2], why, [m1, m2])


def V(v):
    if isinstance(v, str):
        return v
    return ol(v) + ('<p>Work the numbered steps top to bottom. If a step fails or surprises you, stop there and write what you saw '
                    'before you go on.</p>')


def X(h, obj, src, qs, p, a, v, t, w, lab):
    return lad(h, obj, src, {'r0': Q(*qs[0]), 'p': p, 'pc': Q(*qs[1]), 'a': a, 'ac': Q(*qs[2]), 'v': V(v), 'vc': Q(*qs[3]),
                             't': t, 'tc': Q(*qs[4]), 'w': w, 'lab': lab})


def P(*paras):
    return ''.join(f'<p>{x}</p>' for x in paras)
