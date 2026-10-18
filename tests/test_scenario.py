"""Lab scenario mode: PBQ tickets that chain a real VM stage and a simulation stage."""
import json

import lab_runtime as RT
from test_labs import _j, _row, _server_state, solve_http


def test_scenarios_chain_a_real_vm_and_a_sim():
    for s in RT.scenarios():
        kinds = {RT.get_lab(st["id"])["kind"] for st in s["stages"]}
        assert kinds == {"vm", "windows"}, s["id"]
        for st in s["stages"]:
            lab = RT.get_lab(st["id"])
            assert lab["pbq"] and lab["scenario"] == s["id"] and lab["objectives"] == RT.get_lab(st["base"])["objectives"]
    assert not any(l["id"].startswith("scn-") for l in RT.list_labs())   # reached through the ticket, not the index list


def test_hub_locks_stage_two_and_index_lists_tickets(student2):
    # student2: student1 may already have solved the stages in test_labs' every-lab run (order-independent)
    student = student2
    html = student.get("/labs").data.decode()
    assert "Lab scenarios" in html and "/labs/scenario/SCN-DNS" in html
    hub = student.get("/labs/scenario/SCN-DNS").data.decode()
    assert "Start stage 1" in hub and "Unlocks when stage 1 is resolved" in hub
    assert "/labs/scn-dns-fix" not in hub


def test_pbq_stage_hides_checks_until_resolved(student):
    student.post("/labs/scn-dns-evidence/reset")
    page = student.get("/labs/scn-dns-evidence").data.decode()
    assert "Hidden check 1" in page and "Ping app.training.local" not in page and "stage 1 of 2" in page
    st = _j(student.get("/labs/scn-dns-evidence/state"))
    assert all(o["text"].startswith("Hidden check") for o in st["objectives"])
    h = _j(student.post("/labs/scn-dns-evidence/hint"))["hint"]
    assert h["text"] and h["objective_text"] == "one of the hidden checks"
    st = solve_http(student, "scn-dns-evidence")
    assert st["complete"] and not any(o["text"].startswith("Hidden") for o in st["objectives"])   # revealed when resolved
    hub = student.get("/labs/scenario/SCN-DNS").data.decode()
    assert "Resolved" in hub and "/labs/scn-dns-fix" in hub and "hints 1" in hub


def test_vm_stage_check_reports_only_a_count_but_logs_the_detail(student):
    import app as lms
    lid = "scn-dns-fix"
    student.post(f"/labs/{lid}/reset")
    st = _server_state(lid)
    lab = RT.get_lab(lid)
    _j(student.post(f"/labs/{lid}/vm-log", json={"lines": [], "booted": True, "boot_ms": 1}))
    probes = RT.VM.probe_scripts(st, lab)
    fake = {m: f"nonce {st['nonce']}\nm {m}\nend\n" for m in probes}
    r = _j(student.post(f"/labs/{lid}/vm-check", json={"probes": fake}))
    msgs = r["result"]["messages"]
    assert len(msgs) == 1 and "checks pass" in msgs[0] and "resolv.conf" not in msgs[0]
    api = lms.app.extensions["ciwt_lab_progress"]
    row, uid = _row(lms, "student1@lms.local", lid)
    with lms.app.app_context():
        ev = api.LabEvent.query.filter_by(user_id=uid, lab_id=lid, kind="check").order_by(api.LabEvent.id.desc()).first()
        assert "resolv.conf" in (ev.detail or ""), ev.detail       # the instructor's event log keeps the real reason
