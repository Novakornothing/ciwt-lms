"""Real-VM labs against real Linux: boot each lab's VMs in Node (v86), run the scenario setup, then
(a) the solution → every objective, (b) nothing → only "boot". Skipped when node or the v86 assets are missing
(tools/fetch_v86.sh) or CIWT_SKIP_REAL_VM=1. About 1 minute in total."""
import os
import shutil
import subprocess
import sys
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
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "vm_headless.py"), lab_id, "--commands", mode],
                       capture_output=True, text=True, timeout=1500, cwd=ROOT)
    if r.returncode:   # print in full: pytest shortens a long assertion repr, which hid which VM step timed out (pass 17)
        print(f"--- {lab_id} {mode} stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-3000:]}")
    assert r.returncode == 0, (lab_id, mode, r.stderr.strip().splitlines()[-3:] if r.stderr.strip() else r.stdout[-500:])
