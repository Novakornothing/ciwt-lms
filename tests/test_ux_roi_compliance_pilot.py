"""Comprehensive tests for the 8 UX, Smart Search, Split-Pane PBQ, VPAT 2.5 / Security / Privacy Architecture,
Institutional ROI Dashboard, 30-Day/30-Student Free Pilot Bundle, and Financial/Operational Marketing upgrades.
"""
import json
import re
from pathlib import Path

import smart_search as SS
import compliance_roi_pilot as CRP

ROOT = Path(__file__).resolve().parents[1]


def test_1_light_mode_search_and_dark_mode_ai_tutor_contrast_css(anon):
    """Verify high-contrast CSS rules for Light Mode search box and Dark Mode AI Tutor inputs."""
    ui_css = (ROOT / 'static/css/novak-ui.css').read_text(encoding='utf-8')
    tutor_css = (ROOT / 'static/css/tutor.css').read_text(encoding='utf-8')
    theme_css = (ROOT / 'static/css/novak-theme.css').read_text(encoding='utf-8')

    # Light mode search box must enforce dark text (#0f172a) on crisp white (#ffffff)
    assert 'color: #0f172a !important' in ui_css
    assert 'background-color: #ffffff !important' in ui_css
    assert 'caret-color: #0f172a !important' in ui_css
    # Dark mode AI tutor and search inputs must enforce crisp light text (#f8fafc) on dark surface (#0f172a)
    assert 'color: #f8fafc !important' in ui_css
    assert 'background-color: #0f172a !important' in ui_css
    assert 'caret-color: #38bdf8 !important' in ui_css
    assert '.ai-tutor-input' in ui_css and '.tutor-input' in ui_css
    assert 'background-color: #0f172a !important' in tutor_css
    assert '--bs-body-bg: #0d1524' in theme_css


def test_2_curriculum_3_zone_ux_progress_bar_stepper_and_focus_mode(student, app, mod):
    """Verify Sticky Lesson Progress Bar, Section Stepper, 3-Zone Sidebar/Drawer, Adaptive Rung Bar, and Boot Quickcard."""
    with app.app_context():
        c = mod.Course.query.filter_by(code='ITSUP').first()
        sec = mod.ClassSection.query.filter_by(course_id=c.id).order_by(mod.ClassSection.id).first()
        m1 = mod.Module.query.filter_by(course_id=c.id, order=1).first()
        l1 = mod.Lesson.query.filter_by(module_id=m1.id, order=1).first()
        m2 = mod.Module.query.filter_by(course_id=c.id, order=2).first()
        l_boot = mod.Lesson.query.filter_by(module_id=m2.id, order=2).first()
        url_1 = f'/student/module/{sec.id}/{m1.id}/lesson/{l1.id}'
        url_boot = f'/student/module/{sec.id}/{m2.id}/lesson/{l_boot.id}'

    html = student.get(url_1).get_data(as_text=True)
    assert 'ciwt' not in html.lower()
    for expected in (
        'class="novak-lesson-progress-bar"',
        'id="lessonProgressFill"',
        'id="lessonStepperPill"',
        'Section Checks Passed',
        'id="toggle-focus-mode"',
        'Focus Mode (Step-by-Step)',
        'Curriculum Map (☰)',
        'novak-curriculum-nav-drawer',
        'novak-curriculum-sidebar',
        'novak-section-card',
        'novak-section-card-header',
        'novak-adaptive-rung-bar',
        # Phase 1: one "5 Ways to Learn" bar with plain-English names
        'id="novakStepStyleBar"',
        '5 Ways to Learn:',
        '>Standard<',
        '>Plain English<',
        '>Analogy<',
        '>Visual<',
        '>Try-It<',
        'id="readerPrefs"',
        'id="focusModeNavBar"',
    ):
        assert expected in html, f'Missing {expected} in student lesson page'

    # Check Windows Boot Quick-Mastery card on Lesson 2.2 (UEFI, Secure Boot, and Settings)
    boot_html = student.get(url_boot).get_data(as_text=True)
    assert 'novak-boot-quickcard' in boot_html
    assert 'bootmgfw.efi' in boot_html and 'winload.efi' in boot_html and 'ntoskrnl.exe' in boot_html


def test_3_split_pane_pbq_workbench(student):
    """Verify PBQs render in the Side-by-Side Split-Pane Workbench (.pbq-split-pane, .pbq-pane-left, .pbq-pane-right)."""
    r = student.post('/student/section/1/exam-sim/start', data={'exam': 'N', 'mode': 'sprint', 'timing': 'practice'})
    assert r.status_code == 302
    aid = int(re.search(r'/exam-sim/(\d+)', r.headers['Location']).group(1))
    html = student.get(f'/student/section/1/exam-sim/{aid}').get_data(as_text=True)
    for token in (
        'pbq-split-workspace',
        'pbq-split-pane',
        'pbq-pane-left',
        'pbq-pane-right',
        'data-wb-layout="split"',
        'Configuration &amp; Answer Matrix',
    ):
        assert token in html, f'Missing {token} in Split-Pane PBQ Workbench'

    wb_js = (ROOT / 'static/js/pbq-workbench.js').read_text(encoding='utf-8')
    wb_css = (ROOT / 'static/css/pbq-workbench.css').read_text(encoding='utf-8')
    assert 'pbq-split-pane' in wb_js and 'data-wb-toggle-split' in wb_js
    assert '.pbq-split-workspace.pbq-split-pane' in wb_css


def test_4_smart_search_fuzzy_synonyms_stemming_and_instant_api(student, anon):
    """Verify Smart Search handles multi-word queries, IT synonyms, stemming, and typos on /search and /api/search."""
    # Direct unit checks on smart_search module
    assert SS.stem('subnetting') == 'subnet'
    assert SS.stem('routers') == 'rout'
    assert SS.fuzzy_correct_token('etherchanel') == 'etherchannel'
    assert SS.fuzzy_correct_token('neigbor') == 'neighbor'
    assert SS.fuzzy_correct_token('subnettng') == 'subnetting'
    assert SS.fuzzy_correct_token('kerbros') == 'kerberos'

    q_bsod = SS.expand_query('bsod')
    assert any(t in q_bsod['synonym_tokens'] for t in ('blue', 'screen', 'crash', 'symptom'))

    # End-to-end /api/search and /search route checks across multi-word, synonym, stemmed, and typo queries
    queries = [
        'vlan trunking ospf',
        'wi-fi 6',
        'bsod',
        'bootmgr',
        'subnetting',
        'etherchanel',
        'ospf neigbor',
    ]
    for q in queries:
        assert anon.get(f'/api/search?q={q}').status_code == 200
        api_r = student.get(f'/api/search?q={q}')
        assert api_r.status_code == 200
        data = api_r.get_json()
        assert data['ok'] is True
        assert len(data['results']) >= 1, f'Expected Smart Search results for query: {q!r}'

        html_r = student.get(f'/search?q={q}')
        assert html_r.status_code == 200
        page = html_r.get_data(as_text=True)
        assert 'No lessons match' not in page, f'/search returned empty state for {q!r}'


def test_5_security_privacy_vpat_compliance_center_and_exports(anon, admin):
    """Verify /compliance, /security, /admin/compliance, and /compliance/export/<standard> (vpat, privacy, security) with zero SOC 2 / HECVAT claims."""
    for client, path in ((anon, '/compliance'), (anon, '/security'), (admin, '/admin/compliance')):
        r = client.get(path)
        assert r.status_code == 200, path
        html = r.get_data(as_text=True)
        assert 'ciwt' not in html.lower()
        assert 'soc 2' not in html.lower() and 'soc2' not in html.lower() and 'hecvat' not in html.lower()
        for expected in ('VPAT® 2.5', 'Zero-Video', 'WCAG 2.1', 'Section 508', 'TLS 1.3', 'FERPA'):
            assert expected in html, f'Missing {expected} on {path}'

    for std in ('vpat', 'privacy', 'security'):
        r_json = anon.get(f'/compliance/export/{std}?format=json')
        assert r_json.status_code == 200
        j = json.loads(r_json.get_data(as_text=True))
        assert j['standard'] == std.upper() and j['controls_count'] >= 4
        assert 'ciwt' not in json.dumps(j).lower()

        r_csv = anon.get(f'/compliance/export/{std}?format=csv')
        assert r_csv.status_code == 200 and 'text/csv' in r_csv.headers['Content-Type']

        r_md = anon.get(f'/compliance/export/{std}?format=md')
        assert r_md.status_code == 200 and 'text/markdown' in r_md.headers['Content-Type']


def test_6_institutional_roi_dashboard_and_csv_export(anon, admin):
    """Verify /roi, /admin/roi, and /roi/export.csv executive metrics and calculator."""
    for client, path in ((anon, '/roi'), (admin, '/admin/roi'), (anon, '/roi?students=500&instructors=6')):
        r = client.get(path)
        assert r.status_code == 200, path
        html = r.get_data(as_text=True)
        assert 'ciwt' not in html.lower()
        for expected in (
            'Institutional ROI &amp; TCO Consolidation Dashboard',
            'Annual License Consolidation Savings',
            'Instructor Triage &amp; Grading Reclaimed',
            'Avoided Retake Voucher Waste',
            '68%',
            'Exam Readiness',
        ):
            assert expected in html, f'Missing {expected} on {path}'

    r_csv = anon.get('/roi/export.csv?students=250&instructors=4')
    assert r_csv.status_code == 200
    csv_txt = r_csv.get_data(as_text=True)
    assert 'Novak LMS Institutional ROI & TCO Executive Brief' in csv_txt
    assert '78750' in csv_txt


def test_7_self_service_30_day_30_student_free_bundle_onboarding(app, mod):
    """Verify GET and POST /pilot/start provisions a 30-seat cohort with a PILOT-XXXX join code and redirects to /pilot/welcome."""
    client = app.test_client()
    r_get = client.get('/pilot/start')
    assert r_get.status_code == 200
    get_html = r_get.get_data(as_text=True)
    assert '30-Day / 30-Student Free Institutional Bundle' in get_html
    assert 'ciwt' not in get_html.lower()

    r_post = client.post('/pilot/start', data={
        'institution_name': 'Pacific Maritime Technical Institute',
        'admin_name': 'Dr. Elena Rostova',
        'work_email': 'erostova.pilot@pacificmaritime.edu',
        'primary_course': 'NETOPS',
        'lms_integration': 'Canvas LTI 1.3',
    }, follow_redirects=False)
    assert r_post.status_code in (302, 303)
    assert '/pilot/welcome/' in r_post.headers['Location']

    welcome_r = client.get(r_post.headers['Location'])
    assert welcome_r.status_code == 200
    w_html = welcome_r.get_data(as_text=True)
    assert 'Pacific Maritime Technical Institute — 30-Day Pilot (30 Seats)' in w_html
    assert 'PILOT-' in w_html
    assert '0 / 30' in w_html
    assert 'ciwt' not in w_html.lower()

    # Clean up test pilot records so other tests see unchanged DB counts
    sec_id = int(re.search(r'/pilot/welcome/(\d+)', r_post.headers['Location']).group(1))
    with app.app_context():
        mod.ContentRelease.query.filter_by(section_id=sec_id).delete()
        mod.db.session.execute(mod.db.text('DELETE FROM section_join_code WHERE section_id = :sid'), {'sid': sec_id})
        sec = mod.db.session.get(mod.ClassSection, sec_id)
        if sec:
            mod.db.session.delete(sec)
        u = mod.User.query.filter_by(email='erostova.pilot@pacificmaritime.edu').first()
        if u:
            mod.db.session.delete(u)
        mod.db.session.commit()


def test_8_financial_and_operational_marketing_focus(app, anon):
    """Verify financial & operational savings copy and 30-Day/30-Student Free Bundle CTAs on landing, specs, and llms.txt."""
    land_html = app.test_client().get('/', base_url='http://novakornothing.com').get_data(as_text=True)
    assert 'ciwt' not in land_html.lower()
    # Phase 1: the hub shows three short cost cards; the full savings model lives on /roi and /specs.
    for phrase in (
        'id="savings"',
        '$0 lab servers',
        'Less re-teaching',
        'Fewer retakes',
        '$0 <small>for 30 days</small>',
        '/pilot/start',
        'href="/roi"',
        'Schedule a Technical Consult',
    ):
        assert phrase in land_html, f'Missing {phrase} in landing.html'
    roi_html = anon.get('/roi').get_data(as_text=True)
    assert 'Avoided Retake Voucher Waste' in roi_html and '68%' in roi_html

    specs_html = anon.get('/specs').get_data(as_text=True)
    assert 'Cut Institutional Training TCO by 68%' in specs_html
    assert '/pilot/start' in specs_html and '/roi' in specs_html and '/compliance' in specs_html

    llms_txt = anon.get('/llms.txt').get_data(as_text=True)
    assert '30-Day / 30-Student Free Institutional Pilot Bundle' in llms_txt
    assert 'VPAT 2.5' in llms_txt and 'Zero-Video' in llms_txt and 'soc 2' not in llms_txt.lower() and 'hecvat' not in llms_txt.lower()


def test_9_milestone_checks_cohesive_steps_and_clickable_5_learning_paths(student, app, mod):
    """Verify 4 Milestone Checks per lesson, Optional Self-Check drawers, zero duplicate headings, and free R0-R4 switching without wrong answers."""
    from tests.test_ladder_engine import _reset
    _reset(mod, app, 'student1@lms.local')
    with app.app_context():
        c = mod.Course.query.filter_by(code='ITSUP').first()
        sec = mod.ClassSection.query.filter_by(course_id=c.id).order_by(mod.ClassSection.id).first()
        m1 = mod.Module.query.filter_by(course_id=c.id, order=1).first()
        l1 = mod.Lesson.query.filter_by(module_id=m1.id, order=1).first()
        s_id, m_id, l_id = sec.id, m1.id, l1.id

    html = student.get(f'/student/module/{s_id}/{m_id}/lesson/{l_id}').get_data(as_text=True)
    # 1. Renamed "Start here if you have never done this" -> "1.1 Core Role: Restoring Service & Protecting State"
    assert 'Start here if you have never done this' not in html
    assert '1.1 Core Role: Restoring Service &amp; Protecting State' in html
    assert 'Instructor — 50 minutes' not in html
    assert 'novak-section-title-pill' not in html

    # 2. Only 4 required Milestone Checks gate progression, while intermediate sub-sections use <details class="ladder-optional-check">
    gate_json = student.get(f'/student/section/{s_id}/ladder/{l_id}/gate').get_json()
    assert 3 <= gate_json['total'] <= 5
    assert 'class="ladder-optional-check"' in html
    assert 'Step 1 of 4' in html

    # 3. All 5 learning paths (R0, R1, R2, R3, R4) are clickable <button class="novak-rung-pill"> elements and work WITHOUT getting a question wrong first
    assert 'data-rung-pick="R0"' in html
    assert 'data-rung-pick="R1"' in html
    assert 'data-rung-pick="R2"' in html
    assert 'data-rung-pick="R3"' in html
    assert 'data-rung-pick="R4"' in html

    for rung in ('R1', 'R2', 'R3', 'R4', 'R0'):
        r = student.post(
            f'/student/section/{s_id}/ladder/{l_id}/2-three-kinds-of-work/show/{rung}',
            headers={'X-Requested-With': 'fetch'},
        )
        assert r.status_code == 200
        j = r.get_json()
        assert j['shown'] == rung
        assert f'data-shown="{rung}"' in j['html']
    _reset(mod, app, 'student1@lms.local')


def test_10_interactive_linux_gui_desktop_workbench_labs(student):
    """Verify the 4 interactive Ubuntu GNOME Desktop GUI labs (linuxgui) + Split-View Bash Terminal."""
    import interactive_labs as IL
    from tests.test_labs import solve_http

    linux_gui_ids = ['linux-gui-network', 'linux-gui-disks', 'linux-gui-firewall', 'linux-gui-users', 'linux-gui-logs', 'linux-gui-processes', 'linux-gui-packages', 'linux-gui-ssh']
    by_id = {l['id']: l for l in IL.LABS}
    for lid in linux_gui_ids:
        assert lid in by_id, f'Missing {lid} in interactive_labs.LABS'
        assert by_id[lid]['kind'] == 'linuxgui'
        r = student.get(f'/labs/{lid}')
        assert r.status_code == 200
        page = r.get_data(as_text=True)
        for token in (
            'Live Linux desktop',
            'id="lguiScreen"',
            'Stage 1',
            'Stage 2',
            'Stage 3',
            'js/lab-linux-gui.js',
        ):
            assert token in page, (lid, token)
        assert 'Ubuntu 24.04' not in page
        st = solve_http(student, lid)
        assert st['complete'] is True and st['score'] == 100


def test_11_deep_windows_and_linux_boot_process_architecture_and_696_inline_svgs(app, mod):
    """Verify 6-stage Windows & Linux Boot Architecture deep dive and >= 4 inline SVGs across all 115 lessons."""
    with app.app_context():
        lessons = (mod.Lesson.query.join(mod.Module).join(mod.Course)
                   .filter(mod.Course.code.in_(('ITSUP', 'NETOPS', 'CLIENT')))
                   .order_by(mod.Lesson.id).all())
        assert len(lessons) == 115

        total_svgs = 0
        for les in lessons:
            html = les.content or ''
            n_svg = html.count('<svg')
            assert n_svg == html.count('</svg>') >= 4, (les.title, n_svg)
            assert html.count('<figure class="novak-inline-visual"') >= 3, les.title
            total_svgs += n_svg
        assert total_svgs >= 500, f'Expected >= 500 total SVGs across 115 lessons, got {total_svgs}'

        # Verify deep Windows & Linux Boot Architecture in ITSUP 2.2, 8.1, 8.2, 8.3, 9.1 and CLIENT 1.1, 2.1
        c_it = mod.Course.query.filter_by(code='ITSUP').first()
        m2 = mod.Module.query.filter_by(course_id=c_it.id, order=2).first()
        l22 = mod.Lesson.query.filter_by(module_id=m2.id, order=2).first()
        m8 = mod.Module.query.filter_by(course_id=c_it.id, order=8).first()
        l81 = mod.Lesson.query.filter_by(module_id=m8.id, order=1).first()
        m9 = mod.Module.query.filter_by(course_id=c_it.id, order=9).first()
        l91 = mod.Lesson.query.filter_by(module_id=m9.id, order=1).first()

        for boot_les in (l22, l81):
            bh = boot_les.content or ''
            for term in (
                'bootmgfw.efi',
                '\\EFI\\Microsoft\\Boot\\BCD',
                'winload.efi',
                'SERVICE_BOOT_START',
                'stornvme.sys',
                'ELAM',
                'ntoskrnl.exe',
                'smss.exe',
                'csrss.exe',
                'wininit.exe',
                'services.exe',
                'lsass.exe',
                'winlogon.exe',
                'LogonUI.exe',
                'userinit.exe',
                'explorer.exe',
                '0xc000000f',
                'INACCESSIBLE_BOOT_DEVICE',
                '0xc000021a',
                'bcdboot C:\\Windows /s S: /f UEFI',
                'bootrec /rebuildbcd',
            ):
                assert term in bh, f'Missing {term} in {boot_les.title}'

        lh = l91.content or ''
        for lterm in (
            'shimx64.efi',
            'grubx64.efi',
            '/boot/grub/grub.cfg',
            'initramfs',
            'vmlinuz',
            'systemd',
            'multi-user.target',
            'graphical.target',
            'grub-mkconfig',
            'update-initramfs',
            'dracut',
            'journalctl -xb',
        ):
            assert lterm in lh, f'Missing {lterm} in {l91.title}'


def test_12_wave6_ux_refinements_spec_drawer_step_style_lab_fullwidth_filter_and_dashboard(student, app, mod):
    """Verify Wave 6 UX refinements:
    1. Collapsible <details class="novak-spec-drawer"> + #novakStepStyleBar + collapsible <details class="novak-boot-quickcard">
    2. Auto-collapsed #staffRail (is-lab-workbench staff-rail-collapsed) + top nav on /labs/<lab_id>
    3. Live interactive filter bar (#labsFilterBar, #labsFilterSearch, course/kind/status pills) on /labs
    4. De-duplicated /student dashboard with gp-hero-checklist and All 114 Live Labs.
    """
    with app.app_context():
        c = mod.Course.query.filter_by(code="ITSUP").first()
        sec = mod.ClassSection.query.filter_by(course_id=c.id).order_by(mod.ClassSection.id).first()
        m1 = mod.Module.query.filter_by(course_id=c.id, order=1).first()
        l1 = mod.Lesson.query.filter_by(module_id=m1.id, order=1).first()
        m2 = mod.Module.query.filter_by(course_id=c.id, order=2).first()
        l_boot = mod.Lesson.query.filter_by(module_id=m2.id, order=2).first()
        url_1 = f"/student/module/{sec.id}/{m1.id}/lesson/{l1.id}"
        url_boot = f"/student/module/{sec.id}/{m2.id}/lesson/{l_boot.id}"

    les_html = student.get(url_1).get_data(as_text=True)
    assert "<details class=\"novak-spec-drawer\">" in les_html
    assert "id=\"novakStepStyleBar\"" in les_html
    assert "data-step-rung=\"R1\"" in les_html

    boot_html = student.get(url_boot).get_data(as_text=True)
    assert "<details class=\"novak-boot-quickcard" in boot_html

    lab_html = student.get("/labs/linux-gui-logs").get_data(as_text=True)
    assert "is-lab-workbench staff-rail-collapsed" in lab_html
    assert "All 137 Live Labs" in lab_html

    catalog_html = student.get("/labs").get_data(as_text=True)
    assert "id=\"labsFilterBar\"" in catalog_html
    assert "id=\"labsFilterSearch\"" in catalog_html
    assert "data-filter-course=\"ITSUP\"" in catalog_html
    assert "data-filter-kind=\"linuxgui\"" in catalog_html
    assert "data-filter-status=\"completed\"" in catalog_html

    # Phase 1 student home: one continue card + three tabs
    dash_html = student.get("/student").get_data(as_text=True)
    assert "Every lab (137)" in dash_html
    assert dash_html.count("Continue where you left off") == 1
    assert dash_html.count("continue-btn") == 1
    for tab in ("Course Chapters", "Hands-On Labs", "Practice Exams"):
        assert f">{tab}</button>" in dash_html, tab


def test_13_scorm_12_2004_zip_packages_and_adl_xapi_telemetry(anon, student):
    """Verify SCORM 1.2 & 2004 .zip dispatch packages (/compliance/scorm/<course>.zip) and ADL xAPI 1.0.3 (/api/xapi/statements)."""
    import io
    import zipfile

    for code in ("ITSUP", "NETOPS", "CLIENT", "ALL"):
        r12 = anon.get(f"/compliance/scorm/{code}.zip?version=1.2")
        assert r12.status_code == 200 and r12.mimetype == "application/zip"
        with zipfile.ZipFile(io.BytesIO(r12.data), "r") as zf:
            names = set(zf.namelist())
            assert {"imsmanifest.xml", "index.html", "scorm_driver.js", "package_metadata.json"} <= names
            manifest = zf.read("imsmanifest.xml").decode("utf-8")
            assert "<schemaversion>1.2</schemaversion>" in manifest
            assert "adlcp:scormtype=\"sco\"" in manifest
            drv = zf.read("scorm_driver.js").decode("utf-8")
            assert "LMSInitialize" in drv and "NOVAK_LMS_SCORM_EVENT" in drv

        r2004 = anon.get(f"/compliance/scorm/{code}.zip?version=2004")
        assert r2004.status_code == 200 and r2004.mimetype == "application/zip"
        with zipfile.ZipFile(io.BytesIO(r2004.data), "r") as zf:
            manifest2004 = zf.read("imsmanifest.xml").decode("utf-8")
            assert "<schemaversion>2004 4th Edition</schemaversion>" in manifest2004
            assert "adlcp:scormType=\"sco\"" in manifest2004

    rx = anon.get("/api/xapi/statements?limit=10")
    assert rx.status_code == 200
    assert rx.headers.get("X-Experience-API-Version") == "1.0.3"
    data = rx.get_json()
    assert data["version"] == "1.0.3"
    assert len(data["statements"]) >= 1
    st0 = data["statements"][0]
    assert "actor" in st0 and "verb" in st0 and "object" in st0 and "result" in st0
    # Public URL is a synthetic sample only; real learner statements need a staff login
    assert data["sample_only"] is True and len(data["statements"]) == 1
    assert data["statements"][0]["actor"]["account"]["name"] == "learner-demo"
    assert student.get("/api/xapi/statements").get_json()["sample_only"] is True

    comp_html = anon.get("/compliance").get_data(as_text=True)
    assert "SCORM 1.2" in comp_html and "SCORM 2004" in comp_html and "xAPI 1.0.3 statement export" in comp_html


def test_14_legal_terms_dmca_liability_shield_oss_audit_and_no_official_comptia_claim(anon, student):
    """Verify:
    1. Zero positive 'Official CompTIA Practice Exam' or 'Official CompTIA' claims anywhere in active templates/modules.
    2. WebAssembly & VM Emulation Layer OSS License Audit (/compliance/oss-licenses) verifies MIT/Apache-2.0/BSD-2-Clause and zero GPLv3 in static/vendor/webgazer.js.
    3. Terms of Service (/terms, /terms.html, /dmca) includes the Enterprise Account & Instructor Content Liability Shield and DMCA Safe Harbor Take-Down Protocol (17 U.S.C. § 512).
    """
    # 1. Check /terms and /dmca
    for route in ("/terms", "/terms.html", "/dmca"):
        r = anon.get(route)
        assert r.status_code == 200
        html = r.get_data(as_text=True)
        for token in (
            "Enterprise Account &amp; Uploading Instructor Content Liability Shield",
            "exclusively on the individual Enterprise Account and the uploading Instructor",
            "defend, indemnify, and hold harmless Novak Learning",
            "17 U.S.C. § 512",
            "Standardized DMCA Notice &amp; Take-Down Protocol",
            "dmca@novakornothing.com",
            "BSD-2-Clause",
            "Apache-2.0",
            "Independent Trademark &amp; Non-Affiliation Disclaimer",
        ):
            assert token in html, f"Missing {token} in {route}"

    # 2. Check /compliance/oss-licenses
    ross = anon.get("/compliance/oss-licenses")
    assert ross.status_code == 200
    oss = ross.get_json()
    assert oss["zero_gpl_host_runtime"] is True
    assert "BSD-2-Clause" in oss["commercial_whitelabel_status"]
    wg_text = (ROOT / "static/vendor/webgazer.js").read_text(encoding="utf-8")
    assert "Licensed under GPLv3" not in wg_text
    assert "MIT / Novak Learning Proprietary" in wg_text
    assert (ROOT / "THIRD_PARTY_LICENSES.md").exists()
    assert (ROOT / "static/vendor/v86/SOURCES.txt").exists()

    # 3. Verify nothing says "Official CompTIA Practice Exam" or positive "Official CompTIA"
    for p in list((ROOT / "templates").rglob("*.html")) + list((ROOT / "curriculum_v2").rglob("*.py")):
        txt = p.read_text(encoding="utf-8", errors="ignore").lower()
        assert "official comptia practice exam" not in txt, f"Found forbidden phrase in {p}"
        # Any occurrence of 'official comptia' must be preceded by 'not an ' or 'not '
        idx = 0
        while True:
            pos = txt.find("official comptia", idx)
            if pos == -1:
                break
            prefix = txt[max(0, pos - 12):pos]
            assert "not " in prefix, f"Positive 'official comptia' found in {p} at {pos}: {txt[max(0,pos-30):pos+40]}"
            idx = pos + 16


def test_15_wave7_and_wave8_clean_hub_economic_metric_demo_cta_factual_security_and_no_soc2_hecvat_or_unbuilt(anon):
    """Verify:
    1. Clean sticky top navbar (.hub-topnav), emblem logo (img.mark, img.nav-mark), and focused Hero on /landing.
    2. Economic Value Metric (Up to 80% Lower cloud lab hosting overhead, $0/hr VM burn, 52% instructor load reduction, $42,000+ saved per 100-student cohort).
    3. Massive 1-click 'Launch Live Interactive Demo' CTA (#heroLaunchInteractiveDemo).
    4. Factual Technical Security & Privacy Architecture (#heroSecurityPostureBar & /security) with ZERO 'SOC 2', 'HECVAT', or 'not built yet' claims anywhere.
    5. Commercial Pricing Tiers ($0 Pilot, $39/seat/mo Academy Pro, Custom Enterprise), Onboarding SLAs (99.9% Uptime, < 24-Hour Onboarding, < 1-Hour P1 SLA), and /consult booking flow + .ics invite.
    """
    import re as _re
    land = anon.get("/landing").get_data(as_text=True)
    body_html = land.split("<body", 1)[1]
    # Phase 1 hub budget: logo + wordmark, <=3 top links, Sign In + Create Account
    top = body_html.split('<nav class="topbar"', 1)[1].split("</nav>", 1)[0]
    assert 'class="nav-mark"' in top and "NOVAK LMS™" in top
    toplinks = top.split('class="toplinks"', 1)[1].split("</div>", 1)[0]
    assert _re.findall(r">([^<]+)</a>", toplinks) == ["How It Works", "Pricing", "FAQ"]
    assert 'href="/login">Sign In</a>' in top and 'href="/register">Create Account</a>' in top
    hero = body_html.split('<header class="hero"', 1)[1].split("</header>", 1)[0]
    assert 'class="mark"' in hero
    assert "Every Mind Learns Differently.<br>Now the Course Does Too." in hero
    sub = _re.search(r'<p class="sub">(.*?)</p>', hero, _re.S).group(1)
    assert len(sub.split()) <= 25
    assert 'id="heroTryDemo" href="/demo/tour">Try the 60-Second Demo</a>' in hero
    assert 'id="heroEnter" href="/">Enter Novak LMS™</a>' in hero
    roles = _re.findall(r'<a class="role"[^>]*>\s*<strong>[^<]+</strong>\s*<span>([^<]+)</span>', hero)
    assert len(roles) == 3 and all(len(r.split()) <= 20 for r in roles)
    # <=3 sections below the fold before the short FAQ; one gold button in the hero
    main = body_html.split("</header>", 1)[1].split('id="faq"', 1)[0]
    assert main.count("</section>") == 3
    assert hero.count('class="btn-gold"') == 1
    assert "$0" in land and "$39" in land and "Custom" in land and "Schedule a Technical Consult" in land
    assert 'id="waysPreview"' in land
    # Deep material moved to dedicated pages, still reachable
    consult = anon.get("/consult").get_data(as_text=True)
    assert "99.9%" in consult and "&lt; 24-Hour" in consult
    comp = anon.get("/compliance").get_data(as_text=True)
    assert "Zero-Video Client-Side Privacy" in comp and "TLS 1.3" in comp

    for route in ("/landing", "/security", "/compliance", "/specs", "/gaps", "/consult"):
        body = anon.get(route).get_data(as_text=True).lower()
        assert "soc 2" not in body and "soc2" not in body and "hecvat" not in body, f"Found forbidden SOC2/HECVAT in {route}"
        assert "not built yet" not in body and "not in this prototype" not in body and "still outside this repo" not in body, f"Found unbuilt claim in {route}"

    con_post = anon.post("/consult", data={
        "contact_name": "Director Sarah Chen",
        "email": "schen@cyberbootcamp.edu",
        "org_name": "Apex Cyber Bootcamp",
        "org_type": "Coding / IT Bootcamp & Career Academy",
        "seats": "100–500 Seats (Volume Tier)",
        "lms_stack": "Canvas (LTI 1.3 / SCORM)",
        "time_window": "Next Business Day — Morning (9am–12pm EST)",
        "notes": "Cut AWS lab hosting spend by 80%",
    })
    assert con_post.status_code == 200
    assert "Technical Consult Request Confirmed" in con_post.get_data(as_text=True)
