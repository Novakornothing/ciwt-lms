"""Option B pass 2 authoring kit: bespoke R1-R4 ladders for the ITSUP ch3-10 sections that used to be same_as.
Pending SME review. Not a chapter module (the loader only imports ch*.py).

B(label, sid, heading, obj, src, qs, r1, r2, r3, r4, widget, lab) builds one section through the _lk.X kit:
  qs  five check tuples (R0, R1, R2, R3, R4): (question, key, wrong1, wrong2, why, mc1, mc2) — both distractors tagged;
      the key may never be the uniquely longest option (test-wise cue), enforced here at import time.
  r1  (sentences, takeaway): short plain sentences and a concrete takeaway line.
  r2  (story, [(everyday thing, technical part)], where it breaks): analogy with an explicit map and its limit.
  r3  (kind, title, items[, fail]) then caption: 'flow' = boxes left to right (fail = index of the box where it stops),
      'two' = two labelled columns; rendered as an inline, labelled SVG plus a caption.
  r4  try-it text; widget = order/sort/reveal from the schema; lab = (lab id, note) or None.
"""
from html import escape

from curriculum_v2.ladder.itsup._lk import X
from curriculum_v2.ladder.itsup._p2_stamps import STAMPS

REVIEW = 'Pending SME review'
VIOLATIONS = []     # balance problems found at import time (tests assert this stays empty)


def _wrap(text, n=22):
    words, lines, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines[:3]


def _text(x, y, s, n=22, size=12):
    lines = _wrap(s, n)
    y0 = y - (len(lines) - 1) * (size + 2) / 2
    return ''.join(f'<text x="{x}" y="{y0 + i * (size + 2):.0f}" text-anchor="middle" font-size="{size}" '
                   f'fill="currentColor">{escape(l)}</text>' for i, l in enumerate(lines))


def flow(title, steps, fail=None):
    n = len(steps)
    bw, gap = 118, 22
    w = n * bw + (n - 1) * gap + 20
    h = 150
    body = [f'<text x="{w / 2:.0f}" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="currentColor">{escape(title)}</text>']
    for i, s in enumerate(steps):
        x = 10 + i * (bw + gap)
        bad = fail is not None and i == fail
        after = fail is not None and i > fail
        dash = ' stroke-dasharray="5 4"' if after else ''
        stroke = '#b42318' if bad else 'currentColor'
        body.append(f'<rect x="{x}" y="40" width="{bw}" height="72" rx="8" fill="none" stroke="{stroke}" stroke-width="2"{dash}/>')
        body.append(_text(x + bw / 2, 78, s, 18))
        if bad:
            body.append(f'<text x="{x + bw / 2}" y="132" text-anchor="middle" font-size="12" fill="#b42318">stops here</text>')
        if i < n - 1:
            ax = x + bw
            body.append(f'<line x1="{ax + 2}" y1="76" x2="{ax + gap - 4}" y2="76" stroke="currentColor" stroke-width="2"/>'
                        f'<polygon points="{ax + gap - 4},71 {ax + gap},76 {ax + gap - 4},81" fill="currentColor"/>')
    return w, h, ''.join(body)


def two(title, cols):
    (la, ia), (lb, ib) = cols
    rows = max(len(ia), len(ib))
    w, h = 560, 70 + rows * 46
    body = [f'<text x="280" y="18" text-anchor="middle" font-size="13" font-weight="bold" fill="currentColor">{escape(title)}</text>',
            f'<text x="140" y="44" text-anchor="middle" font-size="13" font-weight="bold" fill="currentColor">{escape(la)}</text>',
            f'<text x="420" y="44" text-anchor="middle" font-size="13" font-weight="bold" fill="currentColor">{escape(lb)}</text>',
            '<line x1="280" y1="30" x2="280" y2="%d" stroke="currentColor" stroke-width="1"/>' % (h - 6)]
    for col, items in ((0, ia), (1, ib)):
        for j, s in enumerate(items):
            x, y = 20 + col * 280, 56 + j * 46
            body.append(f'<rect x="{x}" y="{y}" width="240" height="38" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>')
            body.append(_text(x + 120, y + 23, s, 36, 11))
    return w, h, ''.join(body)


def svg(kind, title, items, fail=None):
    w, h, body = flow(title, items, fail) if kind == 'flow' else two(title, items)
    lab = escape(title, quote=True)
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{lab}" class="ladder-svg">'
            f'<title>{lab}</title>{body}</svg>')


def r1_html(sentences, takeaway):
    return ''.join(f'<p>{s}</p>' for s in sentences) + f'<p><strong>Takeaway:</strong> {takeaway}</p>'


def r2_html(story, amap, breaks):
    m = ''.join(f'<li><strong>{a}</strong> → {b}</li>' for a, b in amap)
    return (f'<p>{story}</p><p><strong>Analogy map</strong></p><ul class="analogy-map">{m}</ul>'
            f'<p><strong>Where the analogy breaks:</strong> {breaks}</p>')


def r3_html(spec):
    kind, title, items = spec[:3]
    fail = spec[3] if len(spec) > 4 else None
    caption = spec[-1]
    return svg(kind, title, items, fail) + f'<p>{caption}</p>'


def _balanced(where, q):
    key, w1, w2 = q[1], q[2], q[3]
    if len(key) > max(len(w1), len(w2)):
        VIOLATIONS.append(f'{where}: key is the longest option: {key!r} ({len(key)} vs {len(w1)}/{len(w2)})')
    if not (q[5] and q[6]):
        VIOLATIONS.append(f'{where}: tag both distractors')


def B(label, sid, heading, obj, src, qs, r1, r2, r3, caption, r4, widget, lab):
    assert len(qs) == 5, (label, sid)
    for i, q in enumerate(qs):
        _balanced(f'ITSUP {label} {sid} check {i}', q)
    ent = X(heading, obj, src, qs, r1_html(*r1), r2_html(*r2), r3_html(tuple(r3) + (caption,)), f'<p>{r4}</p>', widget, lab)
    ent['r0_sha'] = STAMPS[f'{label}|{sid}']
    ent['note'] = 'Option B pass 2: bespoke ladder (was same_as).'
    return ent
