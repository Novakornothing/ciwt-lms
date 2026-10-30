"""Tests for all 5 AI Discovery / Generative Engine Optimization (GEO) upgrades:
1. /llms.txt and /llms-full.txt with Content-Type: text/plain; charset=utf-8 and Access-Control-Allow-Origin: *
2. Updated novakornothing.com copy (landing.html) + 10-dimension architectural comparison matrix + public /specs & /compare routes
3. Rich Schema.org JSON-LD (SoftwareApplication, LearningResource, EducationalOrganization, ItemList, Course, FAQPage)
4. Expanded public FAQ with 4 comparison & technical depth questions
5. Explicit /robots.txt (Content-Signal: search=yes, ai-input=yes, ai-train=yes + AI bot rules) & /sitemap.xml
Plus strict verification of zero 'CIWT'/'ciwt' references in all public GEO artifacts and pages.
"""
import json
import re
import xml.etree.ElementTree as ET


REQUIRED_METRICS = (
    '639,146',
    '242,549',
    '396,597',
    '539',
    '115',
    '26',
    '90',
    '24',
    '1,400',
    '466',
    '463',
    '454',
    '660',
    '36',
    '405',
    '45',
    '325',
    '478-landmark',
    'OneEuro1D',
    'pbq-cli',
    'Diagnose → Fix → Verify',
)


def test_llms_txt_and_llms_full_txt(anon):
    for path, min_lines in (('/llms.txt', 100), ('/llms-full.txt', 400)):
        r = anon.get(path)
        assert r.status_code == 200, path
        assert r.headers.get('Content-Type') == 'text/plain; charset=utf-8', r.headers
        assert r.headers.get('Access-Control-Allow-Origin') == '*', r.headers
        text = r.get_data(as_text=True)
        assert 'ciwt' not in text.lower(), f'Found forbidden string in {path}'
        assert text.count('\n') >= min_lines, (path, text.count('\n'))
        assert 'How Novak LMS™ Compares to CompTIA CertMaster, Cisco Networking Academy (NetAcad), and Pearson VUE' in text
        for metric in REQUIRED_METRICS:
            assert metric in text, f'Missing metric {metric} in {path}'
        for competitor in ('CompTIA CertMaster', 'Cisco', 'NetAcad', 'Packet Tracer', 'Pearson VUE'):
            assert competitor in text, f'Missing {competitor} in {path}'


def test_landing_comparison_matrix_and_faq(app):
    """Phase 1: the hub stays short; the comparison matrix lives on /compare."""
    for host in ('novakornothing.com', 'www.novakornothing.com'):
        r = app.test_client().get('/', base_url=f'http://{host}')
        assert r.status_code == 200
        html = r.get_data(as_text=True)
        assert 'ciwt' not in html.lower()
        # Footer hub links survive the redesign (OPs is now labelled Results & ROI)
        for nav_card in ('NOVAK LMS™', 'Eye Tracking', 'Results &amp; ROI', 'Demo', 'Create Account'):
            assert f'<strong>{nav_card}</strong>' in html, nav_card
        assert 'n74-ops.jesse-novak.workers.dev' in html
        # Deep material moved off the hub, but stays one click away
        assert 'id="comparison"' not in html
        assert 'href="/specs"' in html and 'href="/roi"' in html
        for faq_q in (
            'What is Novak LMS™?',
            'Does Eye Tracking record video?',
            'Is Novak LMS™ affiliated with CompTIA?',
            'How do colleges or training commands run a pilot?',
            'Where is the privacy note?',
        ):
            assert f'<summary>{faq_q}</summary>' in html, f'Missing FAQ summary: {faq_q}'
    html = app.test_client().get('/compare').get_data(as_text=True)
    assert 'How Novak LMS™ Compares Across the Stack' in html
    for dim in (
        'Platform Unification',
        'Remediation When a Student Struggles',
        'Hands-On Lab Execution',
        'Attention &amp; Cognitive Friction Telemetry',
        'Adaptive Mastery Modeling',
        'Institution &amp; LMS Interoperability',
    ):
        assert dim in html, f'Missing dimension {dim} on /compare'


def test_public_specs_and_compare_routes(anon):
    for path in ('/specs', '/compare'):
        r = anon.get(path)
        assert r.status_code == 200, path
        html = r.get_data(as_text=True)
        # Strip asset bundle hash or check visible/raw HTML for ciwt
        assert 'ciwt' not in html.lower(), f'Found forbidden string in {path}'
        for m in REQUIRED_METRICS:
            assert m in html, f'Missing {m} in {path}'
        assert 'How Novak LMS™ Compares Across the Stack' in html
        assert 'course-ITSUP' in html and 'course-NETOPS' in html and 'course-CLIENT' in html
        assert '13.6 Processes, netsh, and when not to reboot' in html
        assert '9.6 Hostname and write memory' in html


def test_schema_org_json_ld_on_landing_login_and_specs(app, anon):
    pages = [
        app.test_client().get('/', base_url='http://novakornothing.com').get_data(as_text=True),
        anon.get('/login').get_data(as_text=True),
        anon.get('/specs').get_data(as_text=True),
        anon.get('/').get_data(as_text=True),
    ]
    for html in pages:
        matches = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, flags=re.S)
        assert len(matches) >= 1, 'Missing application/ld+json script block'
        data = json.loads(matches[0])
        assert 'ciwt' not in json.dumps(data).lower()
        assert data.get('@context') == 'https://schema.org'
        graph = data.get('@graph') or []
        types = set()
        for node in graph:
            t = node.get('@type')
            if isinstance(t, list):
                types.update(t)
            elif t:
                types.add(t)
        for req_type in ('SoftwareApplication', 'LearningResource', 'EducationalOrganization', 'ItemList', 'FAQPage'):
            assert req_type in types, f'Missing Schema.org @type {req_type}'
        item_list = next(n for n in graph if n.get('@type') == 'ItemList')
        assert item_list['numberOfItems'] == 3
        courses = [el['item'] for el in item_list['itemListElement']]
        assert [c['courseCode'] for c in courses] == ['ITSUP', 'NETOPS', 'CLIENT']
        faq_page = next(n for n in graph if n.get('@type') == 'FAQPage')
        faq_qs = {q['name'] for q in faq_page['mainEntity']}
        assert len(faq_qs) >= 3
        if html is pages[0]:
            assert 'Is Novak LMS™ affiliated with CompTIA?' in faq_qs
            assert 'Does Eye Tracking record video?' in faq_qs


def test_robots_txt_and_sitemap_xml(anon):
    r_rob = anon.get('/robots.txt')
    assert r_rob.status_code == 200
    assert r_rob.headers.get('Content-Type') == 'text/plain; charset=utf-8'
    assert r_rob.headers.get('Access-Control-Allow-Origin') == '*'
    rob_txt = r_rob.get_data(as_text=True)
    assert 'ciwt' not in rob_txt.lower()
    assert 'Content-Signal: search=yes, ai-input=yes, ai-train=yes' in rob_txt
    for bot in ('GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-Web', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended', 'GrokBot'):
        assert f'User-agent: {bot}' in rob_txt
    assert 'Sitemap: https://novakornothing.com/sitemap.xml' in rob_txt
    assert 'Sitemap: https://novak-lms.onrender.com/sitemap.xml' in rob_txt

    r_map = anon.get('/sitemap.xml')
    assert r_map.status_code == 200
    assert 'xml' in r_map.headers.get('Content-Type', '')
    assert r_map.headers.get('Access-Control-Allow-Origin') == '*'
    xml_txt = r_map.get_data(as_text=True)
    assert 'ciwt' not in xml_txt.lower()
    root = ET.fromstring(xml_txt)
    locs = {el.text for el in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    for expected_url in (
        'https://novakornothing.com/',
        'https://novakornothing.com/specs',
        'https://novakornothing.com/compare',
        'https://novakornothing.com/llms.txt',
        'https://novakornothing.com/llms-full.txt',
        'https://novak-lms.onrender.com/',
        'https://novak-lms.onrender.com/specs',
        'https://novak-lms.onrender.com/compare',
        'https://novak-lms.onrender.com/llms.txt',
        'https://novak-lms.onrender.com/llms-full.txt',
    ):
        assert expected_url in locs, f'Missing {expected_url} in sitemap.xml'
