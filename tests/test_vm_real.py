"""Real-VM labs against real Linux: boot each lab's VMs in Node (v86), run the scenario setup, then
(a) the solution → every objective, (b) nothing → only "boot". Skipped when node or the v86 assets are missing
(tools/fetch_v86.sh) or CIWT_SKIP_REAL_VM=1. About 1 minute in total."""
import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import pytest

import labs_vm as V

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "static" / "vendor" / "v86"
ready = shutil.which("node") and all((ASSETS / f).is_file() for f in ("libv86.js", "v86.wasm", "seabios.bin", "vgabios.bin", V.IMAGE["image"]))
pytestmark = pytest.mark.skipif(not ready or os.environ.get("CIWT_SKIP_REAL_VM") == "1", reason="node or v86 assets not available")


@pytest.mark.parametrize("lab_id", [l["id"] for l in V.VM_LABS])
@pytest.mark.parametrize("mode", ["solution", "none"])
def test_real_vm_grades_real_state(lab_id, mode):
    def go():
        return subprocess.run([sys.executable, str(ROOT / "tools" / "vm_headless.py"), lab_id, "--commands", mode],
                              capture_output=True, text=True, timeout=1500, cwd=ROOT)
    r = go()
    if r.returncode == 3:   # harness waited > VM_WAIT_MS for a prompt (box under load): retry once, never on a grading failure
        first = r.stderr[-2500:]
        r = go()
        if r.returncode == 0:
            warnings.warn(f"{lab_id}/{mode}: harness timeout on the first run, passed on retry. First run: {first}")
    if r.returncode:
        pytest.fail(f"{lab_id} {mode}: exit {r.returncode}\nstdout: {r.stdout[-2500:]}\nstderr: {r.stderr[-4000:]}", pytrace=False)
