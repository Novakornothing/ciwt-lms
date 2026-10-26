"""Tests for interactive lesson visual architecture blueprints & technical spec reference cards."""
from pathlib import Path
import re

from curriculum_v2 import lesson_visuals as LV
from curriculum_v2.ladder import sections as LSEC


def test_zero_legacy_brand_strings_in_lesson_visuals():
    """Zero 'CIWT' strings may appear anywhere in curriculum_v2/lesson_visuals.py."""
    src_path = Path(LV.__file__).resolve()
    content = src_path.read_text(encoding="utf-8")
    assert "ciwt" not in content.lower(), "Found forbidden legacy string in lesson_visuals.py"


def test_curated_dictionary_covers_all_115_lessons():
    """All 115 lessons across ITSUP (59), NETOPS (30), and CLIENT (26) have curated blueprints."""
    counts = {"ITSUP": 0, "NETOPS": 0, "CLIENT": 0}
    for (course, _ch, _les), spec in LV.LESSON_VISUALS.items():
        counts[course] = counts.get(course, 0) + 1
        arch_title, stages, spec_rows, watch_title, watch_body = spec
        assert arch_title and len(stages) >= 4
        assert 4 <= len(spec_rows) <= 6
        assert watch_title and len(watch_body) >= 40
    assert counts == {"ITSUP": 59, "NETOPS": 30, "CLIENT": 26}
    assert sum(counts.values()) == 115


def test_apply_lesson_visuals_all_115_and_idempotent(app, mod):
    """Applying visuals updates all 115 lessons, is 100% idempotent, and preserves ladder sections."""
    with app.app_context():
        # Capture pre-visual ladder sections and r0_sha stamps for every lesson
        before_ladder = {}
        for les in mod.Lesson.query.order_by(mod.Lesson.id).all():
            before_ladder[les.id] = [
                (s["sid"], s["heading"], s["kind"], s["r0_sha"])
                for s in LSEC.sections(les.content or "")
            ]

        n1 = LV.apply_lesson_visuals(mod.db, mod.Course, mod.Module, mod.Lesson)
        assert n1 == 115

        seen_ids = set()
        seen_svgs = set()
        after_first = {}

        for c in mod.Course.query.filter(mod.Course.code.in_(("ITSUP", "NETOPS", "CLIENT"))).all():
            for m in mod.Module.query.filter_by(course_id=c.id).order_by(mod.Module.order).all():
                for les in mod.Lesson.query.filter_by(module_id=m.id).order_by(mod.Lesson.order).all():
                    html = les.content or ""
                    after_first[les.id] = html
                    expected_id = f'id="novak-visual-{c.code.lower()}-{m.order}-{les.order}"'
                    assert expected_id in html, (c.code, m.order, les.order, les.title)
                    assert html.count('<aside class="novak-visual-blueprint"') == 1

                    aside_match = re.search(
                        r'<aside class="novak-visual-blueprint"[^>]*>.*?</aside>',
                        html,
                        re.S,
                    )
                    assert aside_match, (c.code, m.order, les.order)
                    aside_html = aside_match.group(0)
                    assert '<svg viewBox="0 0 760 175"' in aside_html
                    assert '<table class="novak-spec-table"' in aside_html
                    assert '<details class="novak-field-watchout"' in aside_html
                    seen_ids.add(expected_id)

                    svg_match = re.search(r"<svg\b.*?</svg>", aside_html, re.S)
                    assert svg_match, (c.code, m.order, les.order)
                    seen_svgs.add(svg_match.group(0))

                    # Verify ladder section splitting & r0_sha are 100% untouched
                    after_secs = [
                        (s["sid"], s["heading"], s["kind"], s["r0_sha"])
                        for s in LSEC.sections(html)
                    ]
                    assert after_secs == before_ladder[les.id], (c.code, m.order, les.order)

        assert len(seen_ids) == 115
        assert len(seen_svgs) == 115

        # Second application must be 100% idempotent
        n2 = LV.apply_lesson_visuals(mod.db, mod.Course, mod.Module, mod.Lesson)
        assert n2 == 115
        for les in mod.Lesson.query.order_by(mod.Lesson.id).all():
            assert les.content == after_first[les.id]
            assert (les.content or "").count('<aside class="novak-visual-blueprint"') == 1
