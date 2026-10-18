"""Explanation ladder content (pass 19): every ladder file validates against the schema and the real lessons."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_ladder_files_validate_against_lessons(tmp_path):
    out = tmp_path / 'ladder.json'
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'ladder_check.py'), '--json', str(out)],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert p.returncode == 0, p.stdout[-4000:] + p.stderr[-2000:]
    assert out.exists()


def test_worked_example_lesson_1_1_is_complete():
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'ladder_check.py'), '--course', 'ITSUP', '--chapter', '1',
                        '--sections'], cwd=ROOT, capture_output=True, text=True, timeout=300)
    rows = [ln for ln in p.stdout.splitlines() if ln.strip().startswith('ITSUP') and ' 1.1 ' in ln]
    assert len(rows) == 22 and not [r for r in rows if ' missing ' in r or ' stale ' in r], rows


def test_sections_and_ids_are_stable():
    sys.path.insert(0, ROOT)
    from curriculum_v2.ladder import sections as S
    html = ('<p>intro</p><section class="sublesson core"><h3>1. Same name</h3><p>a</p></section>'
            '<div class="instructor-note"><h4>x</h4></div><section class="sublesson depth"><h3>1. Same name</h3><p>b</p></section>'
            '<section class="other"><h3>not a lesson block</h3></section>')
    secs = S.sections(html)
    assert [s['sid'] for s in secs] == ['1-same-name', '1-same-name-2'] and [s['kind'] for s in secs] == ['core', 'depth']
    assert secs[0]['r0_sha'] != secs[1]['r0_sha'] and S.lesson_label('1.1 The Support Technician Role') == '1.1'


def test_schema_rejects_paraphrase_unsafe_html_and_untagged_checks():
    sys.path.insert(0, ROOT)
    from types import SimpleNamespace
    from curriculum_v2.ladder import schema as S
    c = S.check('q?', 'key', ['w1', 'w2'], 'one two three four five six seven eight nine ten', mc=None)
    txt = '<p>' + ' '.join(f'word{i}' for i in range(60)) + '</p>'
    sec = S.section('H', 'IT-1.1', [c], S.plain(txt, 's', [c]), S.analogy(txt, 's', [c]),
                    S.visual('<p><script>x</script></p>', 's', [c]), S.tryit('<p>x</p>', 's', [c]))
    mod = SimpleNamespace(__name__='t', SCHEMA=1, COURSE='ITSUP', CHAPTER=1, LESSONS={'1.1': {'h': sec}})
    E, W = S.validate_module(mod, {'IT-1.1': {}}, {})
    joined = '\n'.join(E)
    for needle in ('too similar', 'scripts', 'tag at least one', 'needs a widget', 'repeats another check', 'numbered <ol>'):
        assert needle in joined, (needle, joined)
