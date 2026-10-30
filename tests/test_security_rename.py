"""The SEC course is shown as 'Security' everywhere; marketing pages carry the SY0-701 line and no banned wording."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINE = ('Security: aligned to the CompTIA Security+ (SY0-701) exam objectives. 28 chapters, 153 lessons, '
        '43 hands-on labs, and a full-length 90-question practice exam.')
MARKETING = ['templates/landing.html', 'templates/specs.html', 'static/llms.txt', 'static/llms-full.txt']
# NIST document titles ("Cybersecurity Framework", SP 800-61 r3) are citations, not the course name.
NIST_OK = re.compile(r'(NIST[^\n]{0,120}Cybersecurity|Cybersecurity Framework|Considerations for Cybersecurity Risk)')


def test_marketing_line_and_banned_wording():
    for rel in MARKETING:
        text = (ROOT / rel).read_text(encoding='utf-8')
        assert LINE in text, rel
        low = text.lower()
        for bad in ('official comptia', 'endorse', 'pass rate', 'pass-rate', 'guarantee', 'cybersecurity'):
            assert bad not in low, (rel, bad)


def test_no_visible_cybersecurity_label_in_templates_or_course_data():
    hits = []
    for path in list((ROOT / 'templates').rglob('*.html')) + list((ROOT / 'curriculum_sec').rglob('*.py')) + \
            [ROOT / 'learner' / 'tickets.py', ROOT / 'learner' / 'deck_data.py', ROOT / 'learner' / 'placement_bank.py']:
        for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if re.search(r'cyber\s*security', line, re.I) and not NIST_OK.search(line) and 'sec_row.name' not in line:
                hits.append(f'{path.relative_to(ROOT)}:{i}')
    assert not hits, hits


def test_course_title_and_demo_codes(client=None):
    import app as lms
    with lms.app.app_context():
        c = lms.Course.query.filter_by(code='SEC').first()
        assert c and c.title == 'Security'
        for s in lms.ClassSection.query.filter_by(course_id=c.id).all():
            assert 'cyber' not in (s.name or '').lower()
    src = (ROOT / 'app.py').read_text(encoding='utf-8')
    assert "('CYBER-DEMO', 'SECURITY-DEMO')" in src
