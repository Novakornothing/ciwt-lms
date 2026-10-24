"""Small SVG helpers for the NETOPS ladder files (content branch). Everything draws in currentColor so diagrams
work in light and dark mode. Not a chapter module (the loader only reads ch*.py)."""

_SVG = 'viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" aria-label="{label}" class="ladder-svg"'


def svg(w, h, label, body):
    return f'<svg {_SVG.format(w=w, h=h, label=label)}><title>{label}</title>{body}</svg>'


def box(x, y, w, h, text, sub=''):
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>'
    t += (f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 7)}" text-anchor="middle" dominant-baseline="middle" '
          f'fill="currentColor" font-size="13" font-weight="700">{text}</text>')
    if sub:
        t += (f'<text x="{x + w / 2}" y="{y + h / 2 + 10}" text-anchor="middle" dominant-baseline="middle" fill="currentColor" '
              f'font-size="11">{sub}</text>')
    return t


def arrow(x1, y1, x2, y2, label=''):
    """Horizontal or vertical arrow from (x1, y1) to (x2, y2)."""
    ang = 0 if y1 == y2 and x2 > x1 else 180 if y1 == y2 else 90 if y2 > y1 else 270
    t = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="2"/>'
         f'<polygon points="{x2},{y2} {x2 - 7},{y2 - 5} {x2 - 7},{y2 + 5}" fill="currentColor" transform="rotate({ang} {x2} {y2})"/>')
    if label:
        t += (f'<text x="{(x1 + x2) / 2}" y="{min(y1, y2) - 6 if y1 == y2 else (y1 + y2) / 2}" text-anchor="middle" '
              f'fill="currentColor" font-size="11">{label}</text>')
    return t


def text(x, y, s, size=12, anchor='middle', bold=False):
    w = ' font-weight="700"' if bold else ''
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="currentColor" font-size="{size}"{w}>{s}</text>'
