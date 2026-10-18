"""Build the DOCX + PDF course package (pass 8).

Usage: ./venv/bin/python tools/build_course_package.py /workspace/artifacts/course-package
Student/shareable documents go in <out>/<COURSE>/; answer keys, blueprints and lesson plans go in
<out>/<COURSE>/instructor-only/. Uses course templates (institution fields stay as [placeholders]).
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curriculum_v2 import documents as D  # noqa: E402

SHARED = ['syllabus', 'pacing', 'rubrics', 'glossary']
INSTRUCTOR = ['lesson-plans', 'lab-manual', 'blueprints', 'answer-key']


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def model_sha256(doc):
    """Hash of the document model (blocks), independent of DOCX/PDF timestamps."""
    return hashlib.sha256(json.dumps(doc, sort_keys=True, default=str).encode()).hexdigest()


def git_state():
    def run(*a):
        try:
            return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception:
            return ''
    return {'git_head': run('rev-parse', '--short', 'HEAD'),
            'dirty_files': [ln[3:] for ln in run('status', '--porcelain').splitlines() if ln.strip()]}


def main(out):
    made, manifest = [], []
    for code in ('ITSUP', 'NETOPS', 'CLIENT'):
        for kind in SHARED + INSTRUCTOR:
            folder = os.path.join(out, code, 'instructor-only' if kind in INSTRUCTOR else '')
            os.makedirs(folder, exist_ok=True)
            if kind == 'glossary' and code != 'ITSUP':
                continue  # one shared glossary
            doc = D.build(kind, code)
            base = os.path.join(folder, f'{code}-{kind}')
            for ext, fn in (('docx', D.to_docx), ('pdf', D.to_pdf)):
                with open(f'{base}.{ext}', 'wb') as fh:
                    fh.write(fn(doc))
                made.append(f'{base}.{ext}')
            manifest.append({'course': code, 'kind': kind, 'model_sha256': model_sha256(doc),
                             'files': [os.path.relpath(f'{base}.{e}', out) for e in ('docx', 'pdf')]})
    meta = {'built_at': datetime.datetime.now().isoformat(timespec='seconds'), **git_state(),
            'note': 'model_sha256 hashes the document model; tools/curriculum_readiness.py --package re-checks it.',
            'documents': manifest}
    with open(os.path.join(out, 'MANIFEST.json'), 'w') as fh:
        json.dump(meta, fh, indent=1)
    made.append(os.path.join(out, 'MANIFEST.json'))
    return made


if __name__ == '__main__':
    files = main(sys.argv[1] if len(sys.argv) > 1 else 'course-package')
    print('\n'.join(files))
