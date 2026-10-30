"""Phase 1: plain-English names, course renames, hub budget, 60-second tour, student/instructor/admin tabs,
Cmd-K command cards, reader preferences."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_TITLES = {'ITSUP': 'IT Support', 'NETOPS': 'Basic Networking', 'CLIENT': 'Operating Systems'}


def test_course_titles_renamed_and_codes_kept(app, mod):
    with app.app_context():
        got = {c.code: c.title for c in mod.Course.query.filter(mod.Course.code.in_(NEW_TITLES)).all()}
        assert got == NEW_TITLES
        names = [s.name for s in mod.ClassSection.query.all()]
    assert not any('Shop Procedures' in n or 'Client Systems' in n for n in names)


def test_new_titles_show_for_every_role(student, instructor, admin):
    assert 'IT Support' in student.get('/student').get_data(as_text=True)
    ih = instructor.get('/instructor').get_data(as_text=True)
    ah = admin.get('/admin').get_data(as_text=True)
    for h in (ih, ah):
        assert 'Shop Procedures' not in h
    assert any(t in ih for t in NEW_TITLES.values())


def test_no_old_jargon_in_main_pages(student, instructor, admin, anon):
    pages = [anon.get('/landing'), student.get('/student'), instructor.get('/instructor'), admin.get('/admin'),
             anon.get('/demo/tour')]
    for r in pages:
        h = r.get_data(as_text=True)
        for old in ('VOUCHER READY', 'Who Needs Me', 'Exam-Day Simulator', 'PBQ Workbench', 'Rung ', 'BKT',
                    'Shop Procedures', 'CIWT'):
            assert old not in h, (r.request.path, old)


def test_demo_tour_page_and_data(anon):
    r = anon.get('/demo/tour')
    assert r.status_code == 200
    h = r.get_data(as_text=True)
    for s in ('id="tour"', 'id="coursePick"', 'data-way=', 'id="camOn"', 'id="labForm"', 'data-view=',
              'id="tourCreate"', 'id="tourEnter"', 'js/demo_tour.js'):
        assert s in h, s
    data = json.loads(re.search(r'<script type="application/json" id="tourData">(.*?)</script>', h, re.S).group(1))
    assert [c['code'] for c in data['courses']] == ['ITSUP', 'NETOPS', 'CLIENT', 'SEC']
    assert [c['title'] for c in data['courses']] == list(NEW_TITLES.values()) + ['Cybersecurity']
    assert set(data['content']) == set(NEW_TITLES) | {'SEC'}
    assert 'SEC' not in ' '.join(c['title'] for c in data['courses'])


def test_landing_budget_links_and_brand(anon):
    h = anon.get('/landing').get_data(as_text=True)
    assert 'Every Mind Learns Differently.<br>Now the Course Does Too.' in h
    assert h.count('class="btn-gold"') == 1
    for href in ('/terms', '/security', '/privacy', '/specs', '/roi', '/consult', '/demo/tour', '/register'):
        assert f'href="{href}"' in h, href
    low = h.lower()
    assert 'soc 2' not in low and 'hecvat' not in low and 'not built yet' not in low
    assert '© 2026 Novak LMS™' in h


def test_student_lesson_reader_has_one_ways_bar_and_prefs(student, app, mod):
    with app.app_context():
        c = mod.Course.query.filter_by(code='ITSUP').first()
        sec = mod.ClassSection.query.filter_by(course_id=c.id).order_by(mod.ClassSection.id).first()
        m1 = mod.Module.query.filter_by(course_id=c.id, order=1).first()
        l1 = mod.Lesson.query.filter_by(module_id=m1.id, order=1).first()
    h = student.get(f'/student/module/{sec.id}/{m1.id}/lesson/{l1.id}').get_data(as_text=True)
    assert h.count('id="novakStepStyleBar"') == 1 and '5 Ways to Learn:' in h
    for k in ('fs', 'lh', 'contrast', 'dys', 'reset'):
        assert f'data-rp="{k}"' in h, k
    js = (ROOT / 'static/js/novak-ui.js').read_text()
    assert 'localStorage' in js and 'reader-dys' in js
    # Right rail on desktop / bottom sheet on mobile; the old header no longer sticks
    for s in ('id="lessonRail"', 'id="lessonRailToggle"', 'id="lessonRailSteps"', 'id="lessonRailLab"',
              'id="lessonSheetBtn"', 'id="lessonTopLine"'):
        assert s in h, s
    assert h.count('data-rail-rung=') == 5
    assert "novak.lessonRail.v1" in js and 'novak:lesson-step' in js
    css = (ROOT / 'static/css/novak-ui.css').read_text()
    assert '.novak-lesson-progress-bar { position: static !important;' in css


def test_cmdk_command_card(student):
    j = student.get('/api/search?q=chmod').get_json()
    card = j.get('command_card')
    assert card and card['command'].startswith('chmod') and card.get('syntax')
    j2 = student.get('/api/search?q=').get_json()
    assert j2.get('command_card') is None
    import command_cards as CC
    assert CC.card_for('show vlan brief') is not None
    assert CC.card_for('zzzz-not-a-command') is None


def test_instructor_tabs_roster_and_csv(instructor, student):
    h = instructor.get('/instructor').get_data(as_text=True)
    for s in ('id="classPassRate"', 'Students Needing Help', 'id="rosterTable"', 'id="rosterFilter"',
              '/instructor/roster.csv', 'Labs &amp; Assignments', 'Students &amp; Grades'):
        assert s in h, s
    r = instructor.get('/instructor/roster.csv')
    assert r.status_code == 200 and r.mimetype == 'text/csv'
    assert r.get_data(as_text=True).splitlines()[0].startswith('student,email,course,class,progress_percent')
    assert student.get('/instructor/roster.csv').status_code in (302, 403)


def test_admin_overview_cards_exports_and_tools(admin, instructor):
    h = admin.get('/admin').get_data(as_text=True)
    for s in ('admin-kpi-4', 'Active seats', 'Instructors', 'Exam Readiness', 'Estimated lab savings',
              'Users &amp; Sections', 'Exports'):
        assert s in h, s
    e = admin.get('/admin/exports').get_data(as_text=True)
    assert 'SCORM' in e and 'xAPI' in e and 'CSV' in e
    assert admin.get('/admin/tools').status_code == 200
    assert admin.get('/api/xapi/statements').get_json()['sample_only'] is False
    assert instructor.get('/admin/exports').status_code in (302, 403)


VERIFIED_PUBLIC_CLAIMS = (
    'cmi5 support verified with the adl catapult test suite',
    'xapi 1.0.3 learning record store',
    'passes the adl lrs conformance suite',
)
UNVERIFIED_PUBLIC_CLAIMS = (
    'cmi5 compliant', 'cmi5 conformant', 'cmi5 certified', 'cmi5)', '9274',
)


def _without_verified_claims(body):
    text = body.lower()
    for phrase in VERIFIED_PUBLIC_CLAIMS:
        text = text.replace(phrase, ' ')
    return text


def test_no_unbacked_cmi5_or_ieee_claims(anon):
    """Verified suite wording is allowed. Unverified conformance wording is not."""
    pages = ('/landing', '/compliance', '/security', '/specs', '/compare', '/gaps', '/consult', '/llms.txt', '/llms-full.txt')
    for path in pages:
        body = anon.get(path).get_data(as_text=True)
        scrubbed = _without_verified_claims(body)
        for bad in UNVERIFIED_PUBLIC_CLAIMS:
            assert bad not in scrubbed, (path, bad)
    for path in ('/specs', '/compliance', '/compare', '/llms.txt', '/llms-full.txt'):
        lowered = anon.get(path).get_data(as_text=True).lower()
        for phrase in VERIFIED_PUBLIC_CLAIMS:
            assert phrase in lowered, (path, phrase)


PUBLIC_PAGES = ('/', '/landing', '/login', '/register', '/compliance', '/security', '/specs', '/compare', '/consult',
                '/terms', '/privacy', '/roi', '/gaps', '/pricing', '/demo/tour', '/llms.txt', '/llms-full.txt',
                '/robots.txt', '/sitemap.xml', '/api/xapi/statements')
UNVERIFIED_MILITARY = ('Navy ILE', 'JKO', 'CIN:', 'A-150-')


def test_no_unverified_navy_dod_claims_on_public_pages(app, anon):
    for host in (None, 'novakornothing.com'):
        c = app.test_client() if host else anon
        for path in PUBLIC_PAGES:
            r = c.get(path, base_url=f'http://{host}') if host else c.get(path)
            assert r.status_code in (200, 302), (host, path, r.status_code)
            body = r.get_data(as_text=True)
            for bad in UNVERIFIED_MILITARY:
                assert bad not in body, (host, path, bad)


def test_scorm_packages_have_no_navy_metadata(anon):
    import io
    import zipfile
    for ver in ('1.2', '2004'):
        r = anon.get(f'/compliance/scorm/ITSUP.zip?version={ver}')
        assert r.status_code == 200
        with zipfile.ZipFile(io.BytesIO(r.data)) as zf:
            for name in zf.namelist():
                text = zf.read(name).decode('utf-8', 'ignore')
                for bad in UNVERIFIED_MILITARY + ('ile_cin', 'Navy', 'DoD'):
                    assert bad not in text, (ver, name, bad)


_CODE_RE = re.compile(r'\b(ITSUP|NETOPS|CLIENT|SEC)\b(?!-[A-Z]+-\d)')  # SEC-LAB-03 style control ids are not course labels
_OLD_TITLE_RE = re.compile(r'IT Support Technician Fundamentals|Network Operations Fundamentals|Client Systems|'
                           r'Shop Procedures|client systems|network operations (training|learning)|CLIENT-101')


def _visible_strings(html):
    """Text a user can see or a crawler shows: titles, meta content, JSON-LD strings, attributes, body text."""
    out = re.findall(r'<title>(.*?)</title>', html, re.S) + re.findall(r'<meta[^>]+content="([^"]*)"', html)

    def walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and key not in ('courseCode', '@id', 'url', 'identifier'):
            out.append(o)
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        walk(json.loads(block))
    body = re.sub(r'(?is)<(script|style|template)\b.*?</\1>', ' ', html)
    body = re.sub(r'(?s)<!--.*?-->', ' ', body)
    out += re.findall(r'\b(?:title|aria-label|placeholder|alt)="([^"]*)"', body)
    out += re.sub(r'<[^>]+>', '\n', body).split('\n')
    return [' '.join(s.split()) for s in out if s.strip()]


def _bad_course_names(strings):
    return [s[:120] for s in strings if _CODE_RE.search(s) or _OLD_TITLE_RE.search(s)]


def test_no_course_codes_or_old_titles_visible(app, anon, student, instructor, admin):
    pages = {
        anon: ['/', '/landing', '/specs', '/compare', '/login', '/demo', '/demo/tour', '/compliance', '/security',
               '/roi', '/consult', '/gaps', '/terms'],
        student: ['/student', '/labs'],
        instructor: ['/instructor'],
        admin: ['/admin', '/admin/classes', '/admin/exports'],
    }
    for client, urls in pages.items():
        for u in urls:
            r = client.get(u, follow_redirects=True)
            assert r.status_code == 200, u
            assert _bad_course_names(_visible_strings(r.get_data(as_text=True))) == [], u
    for role in ('student', 'instructor', 'admin'):
        c = app.test_client()
        r = c.get(f'/demo/enter/{role}', follow_redirects=True)
        assert r.status_code == 200, role
        assert _bad_course_names(_visible_strings(r.get_data(as_text=True))) == [], role
    for name in ('llms.txt', 'llms-full.txt'):
        text = (ROOT / 'static' / name).read_text()
        assert 'across IT Support, Basic Networking, and Operating Systems' in text
        assert _bad_course_names(text.splitlines()) == [], name
    landing = anon.get('/landing').get_data(as_text=True)
    assert 'learning management system for IT Support, Basic Networking, and Operating Systems' in landing


def test_lesson_visuals_and_exports_use_course_names():
    import io
    import zipfile
    from curriculum_v2.lesson_visuals import inject_lesson_visual
    html = inject_lesson_visual('<section><h2>A</h2><p>x</p></section>' * 6, 'NETOPS', 1, 1, 'OSI model')
    assert _bad_course_names(_visible_strings(html)) == []
    assert 'Basic Networking' in html
    import scorm_xapi
    for code in ('ITSUP', 'NETOPS', 'CLIENT', 'SEC', 'ALL'):
        res = scorm_xapi.build_scorm_package_zip(code, '1.2')
        data = next(x for x in (res if isinstance(res, tuple) else (res,)) if isinstance(x, (bytes, bytearray)) or hasattr(x, 'getvalue'))
        data = data.getvalue() if hasattr(data, 'getvalue') else data
        manifest = zipfile.ZipFile(io.BytesIO(data)).read('imsmanifest.xml').decode()
        titles = re.findall(r'<title>(.*?)</title>', manifest, re.S)
        assert titles and _bad_course_names(titles) == [], code


def test_learning_path_switch_keeps_reader_in_place():
    """The 5 Ways switcher swaps every section; it must not focus-jump and must re-pin the section in view.
    (Browser check: /tmp/p1/jump_check.py, which asserts the in-view section moves < 40px.)"""
    ui = (ROOT / 'static/js/novak-ui.js').read_text()
    lad = (ROOT / 'static/js/ladder.js').read_text()
    assert "box.setAttribute('data-swap-quiet', '1')" in ui and 'keepReaderInPlace();' in ui
    assert 'function restoreAnchor()' in ui and 'ResizeObserver' in ui and 'keeper.pending' in ui
    assert "box.hasAttribute('data-swap-quiet')) moveFocus = false" in lad
    assert 'if (!desk.matches) openSheet(false);' in ui


def test_eye_tracking_pill_uses_plain_name():
    js = (ROOT / 'static/js/helix/helix-gaze.js').read_text()
    assert '<span class="hx-pill-text">Eye Tracking</span>' in js
    assert not re.search(r"""['"][^'"\n]*(?<![\w.])Helix\b(?![\w(])[^'"\n]*['"]""", js)


def test_student_home_lists_every_course_side_by_side(student):
    h = student.get('/student').get_data(as_text=True)
    assert 'Other classes' not in h
    n = h.count('class="home-course')
    if n:
        assert h.count('aria-current="true"') >= 1
        assert re.search(r'<nav class="home-courses[^"]*" aria-label="My courses">', h)


def test_cybersecurity_pages_show_names_not_codes(student):
    from app import _obj_label, _course_label
    assert _obj_label('SEC-7.1') == 'CYB-7.1' and _obj_label('IT-9.1') == 'IT-9.1'
    assert _course_label('SEC') == 'Cybersecurity'
    for u in ('/labs/sec-vm-suid', '/labs/sec-phish', '/labs'):
        r = student.get(u, follow_redirects=True)
        assert r.status_code == 200, u
        bad = [s for s in _bad_course_names(_visible_strings(r.get_data(as_text=True)))
               if not re.search(r'ticket SEC-\w+', s)]
        assert bad == [], (u, bad)
    from curriculum_sec import render
    assert 'coach a classmate on <strong>SEC' not in (ROOT / 'curriculum_sec/render.py').read_text()
