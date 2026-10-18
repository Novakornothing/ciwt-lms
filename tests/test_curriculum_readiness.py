"""Pass 13: the curriculum readiness audit (tools/curriculum_readiness.py) passes on the seeded test DB, and the
spot-check sample is reproducible. CURRICULUM_READINESS.md summarises the full run."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))


def test_readiness_audit_passes(app):
    import curriculum_readiness as CR
    R = CR.run()
    failed = [c for c in R['checks'] if not c['ok']]
    assert not failed, failed
    areas = {c['area'] for c in R['checks']}
    assert {'lessons', 'objectives', 'keys', 'items', 'documents'} <= areas
    assert R['summary']['total'] >= 24


def test_package_manifest_detects_drift(tmp_path, monkeypatch):
    import json
    import curriculum_readiness as CR
    folder = tmp_path / 'pkg'
    (folder / 'ITSUP').mkdir(parents=True)
    (folder / 'ITSUP' / 'ITSUP-glossary.docx').write_bytes(b'x')
    (folder / 'ITSUP' / 'ITSUP-glossary.pdf').write_bytes(b'x')
    good = CR.doc_hash('glossary', 'ITSUP')
    entry = {'course': 'ITSUP', 'kind': 'glossary', 'files': ['ITSUP/ITSUP-glossary.docx', 'ITSUP/ITSUP-glossary.pdf']}
    (folder / 'MANIFEST.json').write_text(json.dumps({'documents': [dict(entry, model_sha256=good)]}))
    assert CR.package_manifest(str(folder))['ok']
    (folder / 'MANIFEST.json').write_text(json.dumps({'documents': [dict(entry, model_sha256='0' * 64)]}))
    assert not CR.package_manifest(str(folder))['ok']


def test_spot_check_sample_is_seeded_and_original_only():
    import spot_check_sample as S
    a, b = S.sample(13), S.sample(13)
    assert a == b and len(a) == 40
    assert not any(str(q['bank_id']).startswith('C-') for q in a)
    assert all(q['correct'] in q['options'] for q in a)


def test_a_brand_new_install_syncs_chapter_checks_on_first_boot(tmp_path):
    """Pass 13 bug: init_db() returned right after seeding, so a new database served the generic seed checks
    (no objective tags, so the adaptive engine had nothing to work with) until the first restart."""
    import subprocess
    code = ("import app as M, json\n"
            "with M.app.app_context():\n"
            "    c = M.Course.query.filter_by(code='ITSUP').first()\n"
            "    q = M.Quiz.query.join(M.Module).filter(M.Module.course_id == c.id, M.Module.order == 1).first()\n"
            "    it = json.loads(q.questions)[0]\n"
            "    print('RESULT', it.get('bank_id'), it.get('obj'))\n")
    env = dict(os.environ, DATABASE_URL='sqlite:///' + str(tmp_path / 'brand-new.db'))
    out = subprocess.run([sys.executable, '-c', code], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    line = [ln for ln in out.stdout.splitlines() if ln.startswith('RESULT')]
    assert line, out.stdout + out.stderr
    _, bank_id, obj = line[0].split()
    assert bank_id.startswith('Q1.') and obj.startswith('IT-1.')
