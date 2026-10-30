"""Grade one Linux GUI lab against the real desktop snapshot. No browser.

usage: python tools/vm_gui_headless.py LAB_ID [--commands solution|none]
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab_runtime as RT  # noqa: E402
import labs_vm as V  # noqa: E402

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("lab")
ap.add_argument("--commands", default="solution")
ap.add_argument("--verbose", action="store_true")
a = ap.parse_args()
lab = RT.get_lab(a.lab)
state = RT.fresh_state(a.lab, uid=1)
cmds = RT.LLG.solution_commands(lab, state) if a.commands == "solution" else []
spec = {
    "memory_mb": lab["vm"]["memory_mb"],
    "vga_mb": lab["vm"].get("vga_mb") or 8,
    "setup": RT.LLG.setup_script(lab, state),
    "commands": cmds,
    "probe": V.probe_script(state, lab),
    "verbose": a.verbose,
}
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(spec, f)
    name = f.name
r = subprocess.run(["node", str(HERE / "vm_gui_grade.mjs"), name], capture_output=True, text=True, timeout=180)
sys.stderr.write(r.stderr[-4000:])
if r.returncode:
    print("node failed", r.returncode, file=sys.stderr)
    sys.exit(2)
out = json.loads(r.stdout.strip().splitlines()[-1])
res, state, done = V.grade(lab, state, [], {"vm": out["probe"]}, booted=True)
print(json.dumps({"done": done, "messages": res.get("messages"), "error": res.get("error"),
                  "restore_ms": out.get("restore_ms")}, indent=1))
want = [o["id"] for o in lab["objectives"]]
if a.commands == "solution":
    sys.exit(0 if sorted(done) == sorted(want) else 1)
sys.exit(0 if done == ["boot"] else 1)
