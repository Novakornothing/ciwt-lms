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
    assert len(IL.LABS) == 90
    for lab in IL.LABS:
        assert lab.get('sme_status') == 'verified', lab['id']


def test_landing_and_register_advertise_90_labs(anon):
    landing = anon.get('/landing').get_data(as_text=True)
    assert '90 labs' in landing and '24 real Linux VMs' in landing
    assert '66 labs' not in landing
    reg = anon.get('/register').get_data(as_text=True)
    assert '90 interactive labs' in reg and '66 interactive labs' not in reg


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
