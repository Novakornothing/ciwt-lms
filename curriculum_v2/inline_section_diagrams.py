"""Inline Technical SVG Diagrams & Schematics for all 115 Novak LMS™ lessons.

Generates 3 distinct, topic-specific inline `<figure class="novak-inline-visual">` SVG schematics
per lesson from the lesson's curated specification data so every lesson across ITSUP, NETOPS,
and CLIENT has at least 4–7 visible inline SVG diagrams directly inside the reading flow:
  1. Component & Protocol Specification Bus Schematic (`viewBox="0 0 740 185"`)
  2. Multi-Stage Signal & State-Transition Sequence Map (`viewBox="0 0 740 190"`)
  3. Fault-Isolation & Field Triage Decision Tree (`viewBox="0 0 740 185"`)

Safe for Explanation Ladder (`curriculum_v2/ladder/sections.py`):
- Never emits `<section class="sublesson...">` or `<h3>`.
- Placed cleanly between `</section>` blocks so `LSEC.sections()` and `r0_sha` hashes are 100% preserved.
"""
from __future__ import annotations

import re
from html import escape

_INLINE_FIG_RE = re.compile(
    r'\n*<figure\s+class="novak-inline-visual"[^>]*>.*?</figure>\n*',
    re.DOTALL | re.IGNORECASE,
)


def _trunc(text: str, max_len: int = 34) -> str:
    s = (text or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def _course_display(code):
    from .lesson_visuals import course_display
    return course_display(code)


def render_inline_spec_schematic_svg(
    code: str, ch_i: int, les_i: int, arch_title: str, spec_rows: list
) -> str:
    """Figure 1: 4-Node Component & CLI Technical Specification Schematic."""
    fig_id = f"novak-inline-fig-{code.lower()}-{ch_i}-{les_i}-spec"
    rows = (spec_rows or [])[:4]
    accents = ["#38bdf8", "#a78bfa", "#34d399", "#fbbf24"]
    cards = []
    for idx, (param, spec, cli, _symptom) in enumerate(rows):
        x = 16 + idx * 179
        y = 42
        w, h = 168, 122
        c = accents[idx % len(accents)]
        cards.append(
            f'<g transform="translate({x},{y})">'
            f'<rect width="{w}" height="{h}" rx="8" fill="#0f172a" stroke="{c}" stroke-width="1.5"/>'
            f'<rect x="8" y="8" width="{w - 16}" height="19" rx="4" fill="{c}" fill-opacity="0.16"/>'
            f'<text x="{w // 2}" y="21" text-anchor="middle" fill="{c}" font-family="ui-monospace,Consolas,monospace" font-size="9.2" font-weight="700">{escape(_trunc(param, 22))}</text>'
            f'<text x="10" y="45" fill="#f8fafc" font-family="system-ui,-apple-system,sans-serif" font-size="9.5" font-weight="600">{escape(_trunc(spec, 26))}</text>'
            f'<text x="10" y="61" fill="#cbd5e1" font-family="system-ui,-apple-system,sans-serif" font-size="8.8">{escape(_trunc(spec[25:] if len(spec) > 25 else "Standard operational spec", 28))}</text>'
            f'<line x1="10" y1="74" x2="{w - 10}" y2="74" stroke="{c}" stroke-opacity="0.3" stroke-width="1"/>'
            f'<text x="10" y="90" fill="#94a3b8" font-family="ui-monospace,Consolas,monospace" font-size="8.2">CLI / STD:</text>'
            f'<text x="10" y="106" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="8.8" font-weight="700">{escape(_trunc(cli, 24))}</text>'
            f'</g>'
        )
        if idx < len(rows) - 1:
            lx = x + w + 1
            cards.append(
                f'<line x1="{lx}" y1="{y + h // 2}" x2="{lx + 9}" y2="{y + h // 2}" stroke="#38bdf8" stroke-width="1.8" stroke-dasharray="3,2"/>'
            )

    svg = (
        f'<svg viewBox="0 0 740 185" width="100%" role="img" '
        f'aria-label="{escape(arch_title)} — Technical Specification Schematic" '
        f'class="novak-inline-svg" style="display:block;height:auto;max-width:100%;background:#0b1120;border:1px solid rgba(56,189,248,0.28);border-radius:10px">'
        f'<rect x="0" y="0" width="740" height="28" rx="10" fill="#1e293b"/>'
        f'<text x="16" y="18" fill="#e2e8f0" font-family="system-ui,-apple-system,sans-serif" font-size="11" font-weight="700">'
        f'TECHNICAL SCHEMATIC 1 · {escape(_course_display(code))} {ch_i}.{les_i} — {escape(_trunc(arch_title, 48))} (Parameters &amp; CLI)</text>'
        f'<text x="724" y="18" text-anchor="end" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="9" font-weight="600">SPEC MATRIX</text>'
        + "".join(cards)
        + f'<text x="16" y="177" fill="#94a3b8" font-family="ui-monospace,Consolas,monospace" font-size="8.5">'
        f'Key Interfaces: {escape(" | ".join(_trunc(r[0], 18) for r in rows))}</text>'
        f'</svg>'
    )
    return (
        f'\n<figure class="novak-inline-visual" id="{fig_id}" data-step-visual="1" '
        f'style="margin:1.1rem 0;padding:0.85rem 1rem;border:1px solid rgba(56,189,248,0.25);border-radius:12px;background:rgba(15,23,42,0.03)">'
        f'{svg}'
        f'<figcaption class="small text-muted mt-2" style="font-size:0.82rem">'
        f'<strong>Figure {ch_i}.{les_i}A — Hardware/Protocol Parameter &amp; CLI Reference Map:</strong> '
        f'Core standards and verification commands for {escape(arch_title)}.</figcaption>'
        f'</figure>\n'
    )


def render_inline_sequence_flow_svg(
    code: str, ch_i: int, les_i: int, arch_title: str, stages: list, spec_rows: list
) -> str:
    """Figure 2: Multi-Stage Packet / Signal / Execution Timeline Ladder Diagram."""
    fig_id = f"novak-inline-fig-{code.lower()}-{ch_i}-{les_i}-seq"
    st_list = (stages or [])[:5]
    lanes = []
    accents = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f472b6"]
    for idx, (st_title, st_sub, st_badge) in enumerate(st_list):
        cx = 78 + idx * 146
        c = accents[idx % len(accents)]
        lanes.append(
            f'<g>'
            f'<rect x="{cx - 58}" y="36" width="116" height="34" rx="6" fill="#0f172a" stroke="{c}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="50" text-anchor="middle" fill="{c}" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">{escape(_trunc(st_badge, 14))}</text>'
            f'<text x="{cx}" y="63" text-anchor="middle" fill="#f8fafc" font-family="system-ui,-apple-system,sans-serif" font-size="9.5" font-weight="700">{escape(_trunc(st_title, 16))}</text>'
            f'<line x1="{cx}" y1="70" x2="{cx}" y2="165" stroke="{c}" stroke-opacity="0.4" stroke-width="1.5" stroke-dasharray="4,3"/>'
            f'</g>'
        )
        if idx < len(st_list) - 1:
            nx = 78 + (idx + 1) * 146
            ry = 86 + idx * 19
            cli_hint = spec_rows[idx][2] if idx < len(spec_rows or []) else st_sub
            lanes.append(
                f'<g>'
                f'<line x1="{cx + 4}" y1="{ry}" x2="{nx - 6}" y2="{ry}" stroke="{c}" stroke-width="2"/>'
                f'<polygon points="{nx - 6},{ry - 3.5} {nx},{ry} {nx - 6},{ry + 3.5}" fill="{c}"/>'
                f'<rect x="{(cx + nx) // 2 - 54}" y="{ry - 13}" width="108" height="12" rx="3" fill="#0b1120"/>'
                f'<text x="{(cx + nx) // 2}" y="{ry - 4}" text-anchor="middle" fill="#e2e8f0" font-family="ui-monospace,Consolas,monospace" font-size="8">{escape(_trunc(cli_hint, 20))}</text>'
                f'</g>'
            )

    svg = (
        f'<svg viewBox="0 0 740 190" width="100%" role="img" '
        f'aria-label="{escape(arch_title)} — Signal &amp; Execution Sequence Timeline" '
        f'class="novak-inline-svg" style="display:block;height:auto;max-width:100%;background:#0b1120;border:1px solid rgba(129,140,248,0.28);border-radius:10px">'
        f'<rect x="0" y="0" width="740" height="28" rx="10" fill="#1e1b4b"/>'
        f'<text x="16" y="18" fill="#e2e8f0" font-family="system-ui,-apple-system,sans-serif" font-size="11" font-weight="700">'
        f'SEQUENCE TIMELINE 2 · {escape(_course_display(code))} {ch_i}.{les_i} — Step-by-Step Signal &amp; State Handshake</text>'
        f'<text x="724" y="18" text-anchor="end" fill="#818cf8" font-family="ui-monospace,Consolas,monospace" font-size="9" font-weight="600">STATE LADDER</text>'
        + "".join(lanes)
        + f'<text x="16" y="181" fill="#94a3b8" font-family="ui-monospace,Consolas,monospace" font-size="8.5">'
        f'Execution Order: Verify each stage output before advancing to the next state transition.</text>'
        f'</svg>'
    )
    return (
        f'\n<figure class="novak-inline-visual" id="{fig_id}" data-step-visual="2" '
        f'style="margin:1.1rem 0;padding:0.85rem 1rem;border:1px solid rgba(129,140,248,0.25);border-radius:12px;background:rgba(15,23,42,0.03)">'
        f'{svg}'
        f'<figcaption class="small text-muted mt-2" style="font-size:0.82rem">'
        f'<strong>Figure {ch_i}.{les_i}B — End-to-End State &amp; Handshake Sequence:</strong> '
        f'Chronological stage transitions and verification checkpoints across the {escape(arch_title)} pipeline.</figcaption>'
        f'</figure>\n'
    )


def render_inline_triage_tree_svg(
    code: str, ch_i: int, les_i: int, arch_title: str, spec_rows: list, watch_title: str
) -> str:
    """Figure 3: Fault-Isolation & Symptom-to-Action Troubleshooting Tree."""
    fig_id = f"novak-inline-fig-{code.lower()}-{ch_i}-{les_i}-triage"
    rows = (spec_rows or [])[:3]
    branches = []
    colors = ["#f87171", "#fbbf24", "#34d399"]
    for idx, (param, _spec, cli, symptom) in enumerate(rows):
        y = 44 + idx * 42
        c = colors[idx % len(colors)]
        branches.append(
            f'<g>'
            f'<line x1="168" y1="98" x2="210" y2="{y + 15}" stroke="{c}" stroke-width="1.6"/>'
            f'<rect x="210" y="{y}" width="235" height="32" rx="6" fill="#0f172a" stroke="{c}" stroke-width="1.4"/>'
            f'<text x="220" y="{y + 13}" fill="{c}" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">SYMPTOM {idx + 1}: {escape(_trunc(param, 18))}</text>'
            f'<text x="220" y="{y + 25}" fill="#e2e8f0" font-family="system-ui,-apple-system,sans-serif" font-size="8.8">{escape(_trunc(symptom, 34))}</text>'
            f'<line x1="445" y1="{y + 16}" x2="478" y2="{y + 16}" stroke="#38bdf8" stroke-width="1.6"/>'
            f'<rect x="478" y="{y}" width="244" height="32" rx="6" fill="#0f172a" stroke="#38bdf8" stroke-width="1.3"/>'
            f'<text x="488" y="{y + 13}" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">PROBE / FIX: {escape(_trunc(cli, 20))}</text>'
            f'<text x="488" y="{y + 25}" fill="#cbd5e1" font-family="system-ui,-apple-system,sans-serif" font-size="8.5">Isolate single variable &amp; verify state</text>'
            f'</g>'
        )

    svg = (
        f'<svg viewBox="0 0 740 185" width="100%" role="img" '
        f'aria-label="{escape(arch_title)} — Fault Isolation Decision Tree" '
        f'class="novak-inline-svg" style="display:block;height:auto;max-width:100%;background:#0b1120;border:1px solid rgba(52,211,153,0.28);border-radius:10px">'
        f'<rect x="0" y="0" width="740" height="28" rx="10" fill="#064e3b"/>'
        f'<text x="16" y="18" fill="#e2e8f0" font-family="system-ui,-apple-system,sans-serif" font-size="11" font-weight="700">'
        f'FAULT-ISOLATION TREE 3 · {escape(_course_display(code))} {ch_i}.{les_i} — {escape(_trunc(watch_title, 48))}</text>'
        f'<text x="724" y="18" text-anchor="end" fill="#34d399" font-family="ui-monospace,Consolas,monospace" font-size="9" font-weight="600">DECISION TREE</text>'
        f'<rect x="16" y="72" width="152" height="52" rx="8" fill="#0f172a" stroke="#fbbf24" stroke-width="1.8"/>'
        f'<text x="92" y="92" text-anchor="middle" fill="#fbbf24" font-family="ui-monospace,Consolas,monospace" font-size="9" font-weight="700">FAULT DOMAIN</text>'
        f'<text x="92" y="108" text-anchor="middle" fill="#f8fafc" font-family="system-ui,-apple-system,sans-serif" font-size="9.5" font-weight="700">{escape(_trunc(arch_title, 20))}</text>'
        + "".join(branches)
        + f'</svg>'
    )
    return (
        f'\n<figure class="novak-inline-visual" id="{fig_id}" data-step-visual="3" '
        f'style="margin:1.1rem 0;padding:0.85rem 1rem;border:1px solid rgba(52,211,153,0.25);border-radius:12px;background:rgba(15,23,42,0.03)">'
        f'{svg}'
        f'<figcaption class="small text-muted mt-2" style="font-size:0.82rem">'
        f'<strong>Figure {ch_i}.{les_i}C — Diagnostic Fault-Isolation Tree:</strong> '
        f'Symptom-to-probe mapping and watchout prevention ({escape(_trunc(watch_title, 65))}).</figcaption>'
        f'</figure>\n'
    )


def strip_inline_section_diagrams(html: str) -> str:
    """Remove any existing `<figure class="novak-inline-visual"...>...</figure>` blocks."""
    if not html:
        return ""
    return _INLINE_FIG_RE.sub("\n", html)


def inject_inline_diagrams_into_lesson(
    html: str,
    code: str,
    ch_i: int,
    les_i: int,
    arch_title: str,
    stages: list,
    spec_rows: list,
    watch_title: str,
) -> str:
    """Idempotently place 3 inline `<figure class="novak-inline-visual">` diagrams between `</section>` blocks."""
    cleaned = strip_inline_section_diagrams(html)
    fig1 = render_inline_spec_schematic_svg(code, ch_i, les_i, arch_title, spec_rows)
    fig2 = render_inline_sequence_flow_svg(code, ch_i, les_i, arch_title, stages, spec_rows)
    fig3 = render_inline_triage_tree_svg(code, ch_i, les_i, arch_title, spec_rows, watch_title)

    # Find all `</section>` closing tags so we never insert inside a `<section>`
    close_positions = [m.end() for m in re.finditer(r"</section>", cleaned, flags=re.I)]
    if len(close_positions) >= 6:
        idx1 = close_positions[1]
        idx2 = close_positions[len(close_positions) // 2]
        idx3 = close_positions[min(len(close_positions) - 2, (len(close_positions) * 3) // 4)]
        # Insert from back to front so offsets stay valid
        out = (
            cleaned[:idx1]
            + "\n"
            + fig1.strip()
            + "\n"
            + cleaned[idx1:idx2]
            + "\n"
            + fig2.strip()
            + "\n"
            + cleaned[idx2:idx3]
            + "\n"
            + fig3.strip()
            + "\n"
            + cleaned[idx3:]
        )
        return out
    return cleaned + "\n" + fig1.strip() + "\n" + fig2.strip() + "\n" + fig3.strip() + "\n"
