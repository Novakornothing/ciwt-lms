"""Explanation ladder content (pass 19): every ladder file validates against the schema and the real lessons."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


import json

import pytest


@pytest.fixture(scope='module')
def fresh_db(tmp_path_factory):
    """A brand-new DB path: the app seeds it and syncs the lesson HTML from the python sources on import, so these
    tests never need (or touch) ciwt_lms.db and work in any worktree."""
    return str(tmp_path_factory.mktemp('ladder') / 'fresh.db')


def _check(args, db):
    return subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'ladder_check.py'), '--db', db] + args,
                          cwd=ROOT, capture_output=True, text=True, timeout=600,
                          env=dict(os.environ, DATABASE_URL='sqlite:///' + db))


def test_ladder_files_validate_against_lessons(tmp_path, fresh_db):
    out = tmp_path / 'ladder.json'
    p = _check(['--json', str(out)], fresh_db)
    assert p.returncode == 0, p.stdout[-4000:] + p.stderr[-2000:]
    rep = json.loads(out.read_text())
    for course, c in rep['courses'].items():   # skips are counted and listed (target 0)
        assert 'covered_pct' in c and 'skip_reasons' in c
        assert c.get('skip', 0) == sum(1 for s in rep['skips'] if s['course'] == course)
        assert sum(c['skip_reasons'].values()) == c.get('skip', 0)


def test_max_skips_gate(fresh_db):
    p = _check(['--no-coverage'], fresh_db)
    assert p.returncode == 0
    p = _check(['--max-skips', '0'], fresh_db)
    n = sum(1 for ln in p.stdout.splitlines() if ln.startswith('TOO MANY SKIPS'))
    assert (p.returncode == 1) == bool(n), p.stdout[-1500:]


def test_worked_example_lesson_1_1_is_complete(fresh_db):
    p = _check(['--course', 'ITSUP', '--chapter', '1', '--sections'], fresh_db)
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


def test_netops_07_and_08_validate_and_cover_r1_to_r4():
    sys.path.insert(0, ROOT)
    import interactive_labs as IL
    from curriculum_v2 import ladder as L
    from curriculum_v2.ladder import schema as S
    from curriculum_v2.ladder.netops import ch07, ch08, netops_07, netops_08
    from curriculum_v2.misconceptions import MISCONCEPTIONS
    from curriculum_v2.objectives import OBJECTIVES

    labs = {lab["id"] for lab in IL.LABS}
    for mod, ch_num in ((netops_07, 7), (netops_08, 8), (ch07, 7), (ch08, 8)):
        assert mod.SCHEMA == 1 and mod.COURSE == "NETOPS" and mod.CHAPTER == ch_num
        E, W = S.validate_module(mod, OBJECTIVES, MISCONCEPTIONS, labs)
        assert E == [], (mod.__name__, E)
        assert W == [], (mod.__name__, W)
        assert len(mod.LESSONS) == 4
        for lbl, secs in mod.LESSONS.items():
            assert lbl.startswith(f"{ch_num}.")
            for sid, ent in secs.items():
                resolved = L.entry("NETOPS", lbl, sid)
                assert resolved is not None and resolved["type"] == "section"
                for r_code, r_kind in (("R1", "plain"), ("R2", "analogy"), ("R3", "visual"), ("R4", "try")):
                    assert resolved["rungs"][r_code]["kind"] == r_kind
                    chks = L.rung_checks(resolved, r_code)
                    assert len(chks) >= 1 and chks[0]["mc"]
