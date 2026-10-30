"""Linux GUI labs: stage text hides per-session answers, and one lab is graded on a real desktop."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import lab_runtime as RT
import labs_linux_gui as G

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "static" / "vendor" / "v86"
READY = shutil.which("node") and all((ASSETS / f).is_file() for f in (
    "libv86.js", "v86.wasm", "seabios.bin", "vgabios.bin", "novak-gui.state.gz", "novak-gui.bin"))

# Values the page is allowed to teach in Stage 1. Later stages must not contain the session's own values.
SECRET = (
    "s2_ip", "s3_ip", "s2_gw", "s3_gw", "s2_dns", "s3_dns", "s2_ban", "s3_ban", "s2_port",
    "s2_user", "s3_user", "s2_mode", "s3_mode", "s2_proc", "s3_proc", "s2_pkg", "s3_min",
    "s2_ssh_user", "s3_port", "s2_mnt", "s3_mnt", "s2_opts", "s3_opts", "s2_path", "s3_path",
)


@pytest.mark.parametrize("lab_id", [l["id"] for l in G.LINUX_GUI_LABS])
def test_stage23_text_does_not_contain_session_answers(lab_id):
    lab = RT.get_lab(lab_id)
    assert [s["title"].startswith("Stage ") for s in lab["stages"]] == [True, True, True]
    assert len(lab["objectives"]) == len(lab["vm_checks"])
    for seed in (1, 2, 99):
        state = RT.fresh_state(lab_id, uid=seed)
        vars_ = state["gui_vars"]
        later = " ".join(s["html"] for s in lab["stages"][1:])
        hints = []
        for oid, tiers in (lab.get("obj_hints") or {}).items():
            if oid.startswith("s2") or oid.startswith("s3"):
                hints.extend(tiers)
        blob = later + "\n" + "\n".join(hints) + "\n" + "\n".join(lab.get("hints") or [])
        for key in SECRET:
            val = str(vars_[key])
            assert re.search(r"(?<![\w./-])" + re.escape(val) + r"(?![\w./-])", blob) is None, (lab_id, key, val)
        # the probe the server would send does contain the value, and it is not a leftover placeholder
        probe = RT.VM.probe_script(state, lab)
        assert "{{" not in probe
        assert state["nonce"] in probe


def test_solver_completes_every_gui_lab():
    for lab in G.LINUX_GUI_LABS:
        state, done, _ = RT.solve(lab["id"], uid=3)
        assert set(done) == {o["id"] for o in lab["objectives"]}, lab["id"]
        assert "gui_vars" in state


@pytest.mark.skipif(not READY or os.environ.get("CIWT_SKIP_REAL_VM") == "1", reason="node or GUI desktop assets missing")
def test_real_desktop_snapshot_grades_users_lab():
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "vm_gui_headless.py"), "linux-gui-users", "--commands", "solution"],
        capture_output=True, text=True, timeout=180, cwd=ROOT)
    if r.returncode:
        pytest.fail(f"exit {r.returncode}\nstdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2500:]}", pytrace=False)
    assert "s1_mode" in r.stdout and "s3_mode" in r.stdout
    # the snapshot path, not a cold boot
    assert "restore prompt" in r.stderr
