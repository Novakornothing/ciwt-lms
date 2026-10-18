"""Run a real-VM lab headless in Node (v86) and grade it with the real grader — no browser.

usage: python tools/vm_headless.py LAB_ID [--commands solution|none|FILE] [--verbose]
Needs node and the self-hosted assets (tools/fetch_v86.sh); uses static/vendor/v86 and static/js/lab-vmnet.js.
Exit 0 when the expected outcome holds (solution → complete; none → nothing but boot).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import labs_vm as V  # noqa: E402

HERE = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("lab")
ap.add_argument("--commands", default="solution")
ap.add_argument("--verbose", action="store_true")
a = ap.parse_args()
lab = V.VM_BY_ID[a.lab]
state = V.fresh(lab, 1)
cmds = lab["solution"]["vm_commands"] if a.commands == "solution" else ([] if a.commands == "none" else
                                                                         Path(a.commands).read_text().splitlines())
spec = {"vm": lab["vm"], "commands": cmds, "probes": V.probe_scripts(state, lab), "verbose": a.verbose}
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(spec, f)
r = subprocess.run(["node", str(HERE / "vm_headless.mjs"), f.name], capture_output=True, text=True, timeout=600)
sys.stderr.write(r.stderr[-6000:])
if r.returncode:
    sys.exit(f"node failed: {r.returncode}")
out = json.loads(r.stdout.strip().splitlines()[-1])
V.record_commands(state, cmds)
res, state, done = V.grade(lab, state, [], out["probes"], booted=True, fabric={"events": out["events"]})
print(json.dumps({"done": done, "messages": res["messages"], "error": res.get("error"), "probe": state["probe_last"]}, indent=1))
want = [o["id"] for o in lab["objectives"]]
if a.commands == "solution":
    sys.exit(0 if sorted(done) == sorted(want) else 1)
if a.commands == "none":
    sys.exit(0 if done == ["boot"] else 1)
