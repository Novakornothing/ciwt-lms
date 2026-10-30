"""Try-It simulations: every concept section has a valid widget, and the reader renders it."""
import subprocess
from pathlib import Path

from curriculum_v2.sims import TYPES, coverage, mapped_sections, validate_config

ROOT = Path(__file__).resolve().parents[1]


def test_every_concept_section_has_a_valid_widget():
    from curriculum_v2 import ladder as LD
    rows = mapped_sections()
    assert len(rows) >= 155
    by_course, by_type = coverage()
    assert by_course['ITSUP'] >= 1 and by_course['NETOPS'] >= 1 and by_course['CLIENT'] >= 1
    sec_n = sum(1 for k, e in LD.ladder().items() if k[0] == 'SEC' and e.get('type') == 'section')
    assert by_course.get('SEC') == sec_n and sec_n >= 300
    total = sum(by_course.values())
    assert set(by_type) == set(TYPES)
    biggest = max(by_type.values())
    assert biggest / total <= 0.20, (biggest, total, by_type)
    problems = []
    for key, cfg in rows.items():
        problems.extend(validate_config(cfg, f'{key[0]} {key[1]} {key[2]}'))
    assert problems == []
    # A support-role section is not forced onto the troubleshooting sorter.
    sample = next(cfg for (c, lab, sid), cfg in rows.items() if c == 'ITSUP' and lab == '1.1')
    assert sample['type'] != 'troubleshoot'
    sec_types = {cfg['type'] for (c, _lab, _sid), cfg in rows.items() if c == 'SEC'}
    assert {'cia', 'hash', 'phish', 'logs', 'acl', 'ports'} <= sec_types


def test_widget_logic_passes_for_every_type():
    script = ROOT / 'static' / 'js' / 'sims' / 'check.js'
    proc = subprocess.run(['node', str(script)], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert 'ok 23 widget types' in proc.stdout


def _itsup_lesson(mod, label='1.1'):
    course = mod.Course.query.filter_by(code='ITSUP').first()
    section = mod.ClassSection.query.filter_by(course_id=course.id).order_by(mod.ClassSection.id).first()
    lesson = None
    for m in mod.Module.query.filter_by(course_id=course.id).all():
        for les in mod.Lesson.query.filter_by(module_id=m.id).all():
            if (les.title or '').startswith(label + ' '):
                lesson = les
    return section, lesson


def test_r4_html_renders_the_mapped_widget(student, app, mod):
    from curriculum_v2 import ladder as LD
    with app.app_context():
        section, lesson = _itsup_lesson(mod)
        label = '1.1'
        sid = next(s for (c, lab, s), e in LD.ladder().items()
                   if c == 'ITSUP' and lab == label and e.get('type') == 'section')
        cfg = mapped_sections()[('ITSUP', label, sid)]
    r = student.post(
        f'/student/section/{section.id}/ladder/{lesson.id}/{sid}/show/R4',
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 200, r.status_code
    html = r.get_json()['html']
    assert f'data-novak-sim="{cfg["type"]}"' in html
    assert 'data-sim-check' in html and 'data-sim-reset' in html
    assert cfg['instruction'] in html
    assert 'novak-sim-spec' in html
    blob = html.split('novak-sim-spec', 1)[1]
    assert f'"type": "{cfg["type"]}"' in blob or f'"type":"{cfg["type"]}"' in blob
    # The simulation replaces the dashed order/sort card. It is not a nested card.
    assert 'ladder-widget' not in html
    assert 'class="card' not in html.split('novak-sim', 1)[1][:800]


def test_sim_check_records_one_mastery_observation(student, app, mod):
    from curriculum_v2 import ladder as LD
    with app.app_context():
        section, lesson = _itsup_lesson(mod)
        sid, ent = next((s, e) for (c, lab, s), e in LD.ladder().items()
                        if c == 'ITSUP' and lab == '1.1' and e.get('type') == 'section')
        user = mod.User.query.filter_by(email='student1@lms.local').first()
        checks = mod.mastery_api.models.MasteryCheck
        before_checks = checks.query.filter_by(user_id=user.id).count()
        before_quiz = mod.QuizAttempt.query.filter_by(user_id=user.id).count()
    url = f'/student/section/{section.id}/ladder/{lesson.id}/{sid}/event'
    first = student.post(url, data={'kind': 'sim_check', 'correct': '0', 'answer': 'not yet'},
                         headers={'Accept': 'application/json'})
    assert first.status_code == 200 and first.get_json()['mastery'] is True
    second = student.post(url, data={'kind': 'sim_check', 'correct': '1', 'answer': 'matched'},
                          headers={'Accept': 'application/json'})
    assert second.status_code == 200 and second.get_json()['correct'] is True
    with app.app_context():
        user = mod.User.query.filter_by(email='student1@lms.local').first()
        rows = checks.query.filter_by(user_id=user.id, kind='inline', target=ent['obj']).all()
        sim_rows = [r for r in rows if (r.variant or '').startswith('sim:')]
        assert len(sim_rows) == 1
        assert sim_rows[0].correct == 1
        assert checks.query.filter_by(user_id=user.id).count() == before_checks + 1
        assert mod.QuizAttempt.query.filter_by(user_id=user.id).count() == before_quiz
        events = mod.mastery_api.ladder.models.LadderEvent.query.filter_by(
            user_id=user.id, sid=sid, kind='sim_check').count()
        assert events == 2


def test_switcher_still_pins_the_reader():
    ui = (ROOT / 'static/js/novak-ui.js').read_text()
    lad = (ROOT / 'static/js/ladder.js').read_text()
    assert "box.setAttribute('data-swap-quiet', '1')" in ui and 'keepReaderInPlace();' in ui
    assert 'Swap the section in view first' in ui
    assert "box.hasAttribute('data-swap-quiet')) moveFocus = false" in lad
    assert 'mountSims(box)' in lad
    assert 'scrollIntoView' not in (ROOT / 'static/js/sims/novak-sims.js').read_text()


def test_sim_check_posts_without_reference_error():
    """Check sends its evidence with the global fetch; the factory has no `root` in scope."""
    from pathlib import Path
    js = (Path(__file__).resolve().parents[1] / 'static/js/sims/novak-sims.js').read_text(encoding='utf-8')
    body = js.split('function mount(node)', 1)[1].split('function mountAll', 1)[0]
    assert 'root.' not in body
    assert "typeof fetch === 'function'" in body


def test_path_switch_holds_reader_ignoring_swap_animation():
    """The 5 Ways to Learn switch pins the in-view section by layout top (no translateY from the entry animation)."""
    from pathlib import Path
    js = (Path(__file__).resolve().parents[1] / 'static/js/novak-ui.js').read_text(encoding='utf-8')
    assert 'function layoutTop(el)' in js
    assert 'var d = layoutTop(el) - keeper.top;' in js
    assert 'Math.abs(d) >= 0.5' in js
