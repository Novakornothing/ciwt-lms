"""In-page simulations shipped without the three-stage content: the Cisco IOS-style banner commands,
Windows simulator output, and the client-side simulation panels (labeled, never graded, no stage UI)."""
from pathlib import Path

import interactive_labs as IL
import lab_runtime as RT

ROOT = Path(__file__).resolve().parents[1]


def _run(lab_id, cmds):
    st = RT.fresh_state(lab_id, uid=11)
    done = []
    out = None
    for c in cmds:
        out, st, done = RT.run_command(lab_id, st, done, c)
    return out["lines"], st, done


def test_switch_show_banner_login_and_motd():
    lines, st, _ = _run("sw-vlan-access", ["enable", "configure terminal", "banner motd #Authorized staff only#", "banner login #Closet 4#", "end",
                                          "show banner motd"])
    assert lines == ["Authorized staff only"]
    lines, st, _ = _run("sw-vlan-access", ["enable", "show banner login"])
    assert lines == ["(no login banner is configured)"]
    lines, _, _ = _run("sw-vlan-access", ["enable", "configure terminal", "banner login #Closet 4#", "end", "show running-config"])
    i = lines.index("banner login ^C")
    assert lines[i + 1] == "Closet 4" and lines[i + 2] == "^C"


def test_router_show_banner_and_version():
    lines, _, _ = _run("rtr-gateway", ["enable", "configure terminal", "banner motd #Edge R1#", "end", "show banner motd"])
    assert lines == ["Edge R1"]
    lines, _, _ = _run("rtr-gateway", ["show banner login"])
    assert "Invalid input" not in " ".join(lines)
    lines, _, _ = _run("rtr-gateway", ["enable", "show version"])
    assert any(l.startswith("Cisco IOS Software, Version ") for l in lines)
    assert any(l.startswith("Processor board ID ") for l in lines)


def test_windows_netstat_ano_has_pid_column_and_getmac_lists_ethernet():
    lines, _, _ = _run("win-ipconfig", ["netstat -ano"])
    text = "\n".join(lines)
    assert "PID" in text and "TIME_WAIT" in text
    lines, _, _ = _run("win-ipconfig", ["getmac"])
    assert any("Physical Address" in l for l in lines)


def _page(client, lab_id):
    r = client.get(f"/labs/{lab_id}")
    assert r.status_code == 200, (lab_id, r.status_code)
    return r.data.decode()


def test_windows_lab_shows_labeled_windows_simulation(student):
    html = _page(student, "win-ipconfig")
    assert 'id="winSim"' in html and "Simulation. This is not a Windows PC." in html
    assert "does not change or grade this lab" in html
    assert 'id="iosSim"' not in html


def test_cisco_lab_shows_labeled_ios_simulation_and_network_view(student):
    html = _page(student, "sw-vlan-access")
    assert 'id="iosSim"' in html and "This is not Cisco software." in html
    assert 'id="netCanvas"' in html and "<svg" in html


def test_regular_lab_is_unchanged_by_the_simulations(student):
    for lab_id in ("linux-shell", "net-subnet"):
        html = _page(student, lab_id)
        assert 'id="labSims"' not in html and "lab-sims.js" not in html, lab_id


def test_no_stage_ui_is_shipped(student):
    for lab_id in ("win-ipconfig", "sw-vlan-access", "rtr-gateway", "linux-vm-perms", "linux-vm-firewall", "gui-services", "linux-shell", "sec-acl"):
        lab = RT.get_lab(lab_id)
        assert lab is not None, lab_id
        html = _page(student, lab_id)
        for marker in ('id="labStages"', "stageTab-", "Stage 3 — Unassisted ticket", "data-open-note", "/note?stage="):
            assert marker not in html, (lab_id, marker)
    assert not (ROOT / "templates" / "_lab_stages.html").exists()
    assert not (ROOT / "lab_stage1.py").exists() and not (ROOT / "lab_stage_scenarios.py").exists()


def test_client_simulations_never_talk_to_the_server():
    js = (ROOT / "static" / "js" / "sims" / "lab-sims.js").read_text()
    for banned in ("fetch(", "XMLHttpRequest", "data-cmd-url", "data-stage-url", "sendBeacon"):
        assert banned not in js, banned
    assert "show banner login" in js and "not available in this simulation" in js


def test_every_sim_kind_lab_renders(student):
    kinds = {}
    for lab in IL.LABS:
        kinds.setdefault(lab["kind"], lab["id"])
    for kind in ("windows", "win11gui", "switch", "router", "vm"):
        if kind in kinds:
            _page(student, kinds[kind])
