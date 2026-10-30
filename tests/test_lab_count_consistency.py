"""Every public lab-count claim matches the real lab catalog (all four courses)."""
import re
from pathlib import Path

import lab_runtime as RT

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ['templates/landing.html', 'templates/specs.html', 'templates/index.html', 'templates/login.html',
          'templates/_lab_header.html', 'templates/student_dashboard.html', 'templates/compliance.html',
          'templates/pilot_start.html', 'templates/consult.html', 'templates/gaps.html', 'templates/search.html',
          'static/llms.txt', 'static/llms-full.txt']


def test_lab_catalog_size_and_courses():
    labs = RT.list_labs()
    assert len(labs) == 137
    assert all(lab['courses'] for lab in labs)
    assert {c for lab in labs for c in lab['courses']} == {'ITSUP', 'NETOPS', 'CLIENT', 'SEC'}


def test_public_lab_counts_match_catalog():
    labs = RT.list_labs()
    n = str(len(labs))
    non_vm = str(sum(1 for lab in labs if lab['kind'] != 'vm'))  # '32 Linux VMs + 82 stateful ... labs'
    pat = re.compile(r'(?<![\d,.$#-])(\d{2,3})\+?`?\s+(?:[A-Za-z&/()-]+\s+){0,4}[Ll]abs?\b')
    for rel in PUBLIC:
        text = (ROOT / rel).read_text(encoding='utf-8')
        for m in pat.finditer(text):
            if int(m.group(1)) < 50:  # per-kind or per-course figures (e.g. '20 hands-on labs', 'Windows 11 GUI labs')
                continue
            assert m.group(1) in (n, non_vm), f'{rel}: {m.group(0)!r}'
