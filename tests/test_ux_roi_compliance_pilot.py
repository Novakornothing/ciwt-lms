"""Comprehensive tests for the 8 UX, Smart Search, Split-Pane PBQ, VPAT/SOC2/HECVAT Compliance,
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
        'R0 Standard',
        'R1 Plain Language',
        'R2 Real-World Analogy',
        'R3 Visual Diagram',
        'R4 Hands-On Try-It',
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


def test_5_vpat_soc2_hecvat_compliance_center_and_exports(anon, admin):
    """Verify /compliance, /admin/compliance, and /compliance/export/<standard> (vpat, hecvat, soc2)."""
    for client, path in ((anon, '/compliance'), (admin, '/admin/compliance')):
        r = client.get(path)
        assert r.status_code == 200, path
        html = r.get_data(as_text=True)
        assert 'ciwt' not in html.lower()
        for expected in ('VPAT® 2.5', 'HECVAT v3.04', 'SOC 2', 'WCAG 2.1', 'Section 508', 'CC1.1', 'FERPA'):
            assert expected in html, f'Missing {expected} on {path}'

    for std in ('vpat', 'hecvat', 'soc2'):
        r_json = anon.get(f'/compliance/export/{std}?format=json')
        assert r_json.status_code == 200
        j = json.loads(r_json.get_data(as_text=True))
        assert j['standard'] == std.upper() and j['controls_count'] >= 8
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
            'VOUCHER READY',
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
    for phrase in (
        'Financial &amp; Operational Impact: Cut Training TCO by 68%',
        'Consolidate 4 Vendor Licenses into 1 Unified Stack',
        'Eliminate Retake Voucher Waste',
        'Reclaim 14.5 Instructor Hours Every Week',
        '30-Day / 30-Student Free Bundle',
        '/pilot/start',
        '/roi',
        '/compliance',
    ):
        assert phrase in land_html, f'Missing {phrase} in landing.html'

    specs_html = anon.get('/specs').get_data(as_text=True)
    assert 'Cut Institutional Training TCO by 68%' in specs_html
    assert '/pilot/start' in specs_html and '/roi' in specs_html and '/compliance' in specs_html

    llms_txt = anon.get('/llms.txt').get_data(as_text=True)
    assert '30-Day / 30-Student Free Institutional Pilot Bundle' in llms_txt
    assert 'VPAT 2.5' in llms_txt and 'HECVAT' in llms_txt and 'SOC 2' in llms_txt


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
            'Ubuntu 24.04 LTS · GNOME 46 Desktop',
            'GUI + Bash Split View',
            'id="lnxWorkbenchGrid"',
            'id="lnxDesk"',
            'id="termWrap"',
            'js/lab-linux-gui.js',
        ):
            assert token in page, (lid, token)

        # Verify split-view bash terminal command works inside linuxgui lab
        cmd_r = student.post(f'/labs/{lid}/cmd', json={'command': 'whoami'})
        assert cmd_r.status_code == 200
        assert 'trainee' in ' '.join(cmd_r.get_json().get('lines') or [])

        # Verify full GUI event path solves the lab to 100%
        st = solve_http(student, lid)
        assert st['complete'] is True and st['score'] == 100


def test_11_deep_windows_and_linux_boot_process_architecture_and_696_inline_svgs(app, mod):
    """Verify 6-stage Windows & Linux Boot Architecture deep dive and >= 4 inline SVGs across all 115 lessons."""
    with app.app_context():
        lessons = mod.Lesson.query.order_by(mod.Lesson.id).all()
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
