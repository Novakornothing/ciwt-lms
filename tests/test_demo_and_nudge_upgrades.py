"""Tests for the 4 high-impact upgrades:
1. Rich idempotent demo telemetry seeder (demo_telemetry.ensure_rich_demo_telemetry)
2. Helix in-lesson gaze struggle detector -> 4-rung explanation ladder nudge (triggerStruggleNudge)
3. 90-lab copy, Verified SME status (sme_status == 'verified') across all 90 labs
4. Fast Linux VM (v86) base kernel snapshot caching (baseCacheKey, vmBaseCached)
"""
from pathlib import Path
import interactive_labs as IL


ROOT = Path(__file__).resolve().parents[1]


def test_all_90_labs_have_verified_sme_status():
    assert len(IL.LABS) >= 90
    for lab in IL.LABS:
        assert lab.get('sme_status') == 'verified', lab['id']


def test_landing_and_register_advertise_90_labs(anon):
    landing = anon.get('/landing').get_data(as_text=True)
    assert '66 labs' not in landing
    # Phase 1: lab counts live on the specs page; the hub stays short.
    specs = anon.get('/specs').get_data(as_text=True)
    assert '137 labs' in specs and '41 real Linux VMs' in specs
    assert '66 labs' not in specs
    reg = anon.get('/register').get_data(as_text=True)
    assert '137 interactive labs' in reg and '66 interactive labs' not in reg


def test_helix_gaze_struggle_nudge_wiring(student, ids):
    js_ladder = (ROOT / 'static/js/ladder.js').read_text()
    js_gaze = (ROOT / 'static/js/helix/helix-gaze.js').read_text()
    assert 'triggerStruggleNudge' in js_ladder
    assert 'triggerStruggleNudge' in js_gaze
    assert 'helix:ladder-nudge-accepted' in js_ladder
    assert 'Switch to ' in js_ladder
    html = student.get(f"/student/module/{ids['section']}/{ids['module']}/lesson/{ids['lesson']}").get_data(as_text=True)
    assert 'class="ladder-helix" hidden' in html
    assert 'helix-gaze.js' in html and 'ladder.js' in html


def test_vm_lab_base_kernel_snapshot_cache_wiring(student):
    js_vm = (ROOT / 'static/js/lab-vm.js').read_text()
    assert 'base_kernel_v1:' in js_vm
    assert 'baseCacheKey' in js_vm
    assert 'usedBaseSnap' in js_vm
    assert 'Instant-booting cached snapshot' in js_vm
    html = student.get('/labs/linux-vm-perms').get_data(as_text=True)
    assert 'id="vmBaseCached"' in html
    assert 'Instant-Boot Snapshot Cached' in html


def test_comptia_tech_plus_fc0_u71_in_exam_sim_and_cert_coverage(student, instructor, app):
    from curriculum_v2.cert import exam_sim as ES
    from curriculum_v2.cert.exams import ALL_DOMAINS, ALL_EXAMS, ALL_OBJECTIVES
    assert 'T' in ALL_EXAMS and ALL_EXAMS['T']['code'] == 'FC0-U71'
    assert len(ALL_DOMAINS['T']) == 6 and sum(w for _d, _n, w in ALL_DOMAINS['T']) == 100
    assert any(k.startswith('T:') for k in ALL_OBJECTIVES)
    form = ES.build_form('T', 'full')
    assert len(form) == 45 and len({i for i, _o in form}) == 45
    assert str(form[0][0]).startswith('SIM-T-')
    html_es = student.get('/student/section/1/exam-sim').get_data(as_text=True)
    assert 'CompTIA Tech+ (FC0-U71)' in html_es and 'pass bar 650' in html_es
    html_cov = instructor.get('/staff/cert-coverage?exam=T').get_data(as_text=True)
    assert 'CompTIA Tech+ FC0-U71' in html_cov and 'Tech+ · 1.0 IT Concepts and Terminology' in html_cov


def test_site_name_default_is_novak_lms(app, anon):
    assert app.config['SITE_NAME'] == 'Novak LMS™'
    html = anon.get('/login').get_data(as_text=True)
    assert 'Novak LMS™' in html


def test_student_views_hide_pending_sme_review_and_speed_drill_lists_fc0_u71(student):
    es_home = student.get('/student/section/1/exam-sim').get_data(as_text=True)
    assert 'Pending SME review' not in es_home
    sd_page = student.get('/student/section/1/speed-drill').get_data(as_text=True)
    assert 'Pending SME review' not in sd_page
    assert '220-1201, 220-1202, N10-009, and FC0-U71' in sd_page
