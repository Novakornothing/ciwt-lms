"""Build the DOCX + PDF course package (pass 8).

Usage: ./venv/bin/python tools/build_course_package.py /workspace/artifacts/course-package
Student/shareable documents go in <out>/<COURSE>/; answer keys, blueprints and lesson plans go in
<out>/<COURSE>/instructor-only/. Uses course templates (institution fields stay as [placeholders]).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curriculum_v2 import documents as D  # noqa: E402

SHARED = ['syllabus', 'pacing', 'rubrics', 'glossary']
INSTRUCTOR = ['lesson-plans', 'lab-manual', 'blueprints', 'answer-key']


def main(out):
    made = []
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
    return made


if __name__ == '__main__':
    files = main(sys.argv[1] if len(sys.argv) > 1 else 'course-package')
    print('\n'.join(files))
