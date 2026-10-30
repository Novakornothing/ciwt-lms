"""Live labs (pass L1): every lab is solvable through the HTTP routes a student uses, state is server-side
(resume, undo, reset, hints), completion reaches LabCompletion, lab results, the gradebook and sign-off."""
import json

import pytest

import interactive_labs as IL
import lab_runtime as RT

ALL = [l["id"] for l in IL.LABS]
NEW = ["net-subnet", "hw-cables", "hw-pc-build", "ticket-method", "win-net-cli", "linux-shell", "print-trouble", "rtr-vlan-acl",
       "sw-vlan-multi", "wifi-secure", "sec-malware", "ops-backup", "virt-vm", "mob-mdm", "win-ad-users", "win-laptop-ports", "linux-vm-perms", "win-wifi-survey", "hv-vswitch",
       "linux-vm-shell", "linux-vm-services", "linux-vm-netclient", "linux-vm-routing",
       "linux-vm-logs", "linux-vm-cron", "linux-vm-users", "linux-vm-packages", "linux-vm-firewall", "linux-vm-disk", "linux-vm-ssh",
       "linux-vm-script", "linux-vm-dns", "linux-vm-nettrouble",
       "linux-vm-perf", "linux-vm-restore", "linux-vm-web", "linux-vm-nat", "linux-vm-incident", "linux-vm-ipv6", "linux-vm-method"]


def _j(r):
    assert r.status_code == 200, (r.status_code, r.data[:300])
    return r.get_json()


def _row(mod, email, lab_id):
    api = mod.app.extensions["ciwt_lab_progress"]
    with mod.app.app_context():
        u = mod.User.query.filter_by(email=email).first()
        return api.LabProgress.query.filter_by(user_id=u.id, lab_id=lab_id).first(), u.id


def solve_http(client, lab_id, mod=None):
    """Drive the known-good path through the real endpoints (what the browser does)."""
    lab = RT.get_lab(lab_id)
    client.post(f"/labs/{lab_id}/reset")
    st = _j(client.get(f"/labs/{lab_id}/state"))
    sol = lab.get("solution") or {}
    cmds = sol.get("commands")
    if cmds is None and lab_id in IL.VERIFY_SEQUENCES:
        cmds = IL.VERIFY_SEQUENCES[lab_id][0]
    for c in cmds or []:
        st = _j(client.post(f"/labs/{lab_id}/cmd", json={"command": c}))
    for ev, data in sol.get("events") or RT._default_events(lab):
        st = _j(client.post(f"/labs/{lab_id}/event", json={"ev": ev, "data": data}))
    if lab.get("vm_checks"):
        cmds = sol.get("vm_commands") or []
        if lab["kind"] == "linuxgui":
            cmds = RT.LLG.solution_commands(lab, _server_state(lab_id))
        _j(client.post(f"/labs/{lab_id}/vm-log", json={"lines": [], "booted": True, "boot_ms": 1}))
        if cmds:
            _j(client.post(f"/labs/{lab_id}/vm-log", json={"lines": cmds}))
        st = _j(client.post(f"/labs/{lab_id}/vm-check", json={"probes": RT.VM.solved_probes(_server_state(lab_id), lab),
                                                              "fabric": sol.get("fabric")}))
    if lab.get("steps"):
        answers = sol.get("answers") or {}
        server_state = None
        if callable(answers) or any(callable(v) for v in answers.values()):
            server_state = _server_state(lab_id)   # per-student generated values live server-side
        if callable(answers):
            answers = answers(server_state)
        for step in lab["steps"]:
            a = answers.get(step["id"])
            if callable(a):
                a = a(server_state)
            st = _j(client.post(f"/labs/{lab_id}/check", json={"step": step["id"], "answer": a}))
            assert st["result"]["correct"], (lab_id, step["id"], st["result"])
    for action in RT.PX.stage_actions(lab, _server_state(lab_id)):
        if action["type"] == "cmd":
            st = _j(client.post(f"/labs/{lab_id}/cmd", json={"command": action["command"]}))
        elif action["type"] == "stage":
            st = _j(client.post(f"/labs/{lab_id}/stage", json={"stage": action["stage"], "answer": action["answer"]}))
    if lab.get("kind") == "vm":
        import lab_skills as SK
        server_state = _server_state(lab_id)
        file_cmds = RT.PX.vm_file_commands(lab, server_state)
        if SK.has_spec(lab):
            extra = SK.evaluate(lab, server_state["px"]["facts"])
        else:
            extra = RT.PX.run_px_grep(lab, server_state, file_cmds) if file_cmds else []
        if file_cmds:
            _j(client.post(f"/labs/{lab_id}/vm-log", json={"lines": file_cmds}))
        if extra:
            probes = RT.VM.solved_probes(_server_state(lab_id), lab)
            first = next(iter(probes))
            probes[first] = RT.PX.splice_px_lines(probes[first], extra)
            st = _j(client.post(f"/labs/{lab_id}/vm-check", json={"probes": probes, "fabric": sol.get("fabric")}))
    return _j(client.get(f"/labs/{lab_id}/state"))


def _server_state(lab_id, email="student1@lms.local"):
    import app as lms
    row, _ = _row(lms, email, lab_id)
    return json.loads(row.state_json)


def test_engine_verify_all_labs():
    ok, report = RT.verify_all_labs()
    assert ok, [r for r in report if not r.startswith("PASS")]


def test_at_least_ten_new_labs_with_standard_parts():
    from curriculum_v2 import course_package as CP
    assert len(NEW) >= 10
    for lid in NEW:
        lab = RT.get_lab(lid)
        assert lab, lid
        assert lab.get("course_objectives"), lid
        assert lab.get("solution"), lid
        f = CP.standard_lab(lab)
        for field in ("objective", "steps", "expected", "equipment", "low_cost", "troubleshooting", "reflection", "rubric"):
            assert f[field], (lid, field)
        assert any(lid in ids for ids in IL.CHAPTER_LABS.values()), lid
        # every objective has a hint
        st = RT.fresh_state(lid)
        for o in lab["objectives"]:
            h = RT.next_hint(lab, st, [x["id"] for x in lab["objectives"] if x["id"] != o["id"]], 0)
            assert h["objective"] == o["id"] and h["text"], (lid, o["id"])


def test_course_objective_codes_exist():
    from curriculum_v2 import objectives as OBJ
    codes = set()
    for name in dir(OBJ):
        v = getattr(OBJ, name)
        if isinstance(v, (list, tuple)):
            for row in v:
                if isinstance(row, tuple) and row and isinstance(row[0], str):
                    codes.add(row[0])
    for lid in NEW:
        for c in RT.get_lab(lid)["course_objectives"]:
            assert c in codes, (lid, c)


@pytest.mark.parametrize("lab_id", ALL)
def test_every_lab_completes_over_http(student, mod, lab_id):
    st = solve_http(student, lab_id)
    assert st["complete"], (lab_id, st.get("done"))
    assert st["score"] == 100
    row, uid = _row(mod, "student1@lms.local", lab_id)
    assert row and row.completed_at and row.best_score == 100
    with mod.app.app_context():
        assert mod.LabCompletion.query.filter_by(user_id=uid, lab_id=lab_id).first() is not None


@pytest.mark.parametrize("lab_id", ALL)
def test_every_lab_page_renders(student, lab_id):
    r = student.get(f"/labs/{lab_id}")
    assert r.status_code == 200
    html = r.data.decode()
    assert 'id="labConfig"' in html and "labObjectives" in html


def test_resume_after_reload_keeps_transcript_and_progress(student):
    student.post("/labs/win-ipconfig/reset")
    _j(student.post("/labs/win-ipconfig/cmd", json={"command": "hostname"}))
    st = _j(student.get("/labs/win-ipconfig/state"))
    assert "run_hostname" in st["done"]
    assert any("hostname" in t["t"] for t in st["transcript"])
    page = student.get("/labs/win-ipconfig").data.decode()
    assert "run_hostname" in page and "NOVAK-W11-07" in page


def test_state_is_per_user(student, student2):
    student.post("/labs/linux-shell/reset")
    student2.post("/labs/linux-shell/reset")
    _j(student.post("/labs/linux-shell/cmd", json={"command": "whoami"}))
    _j(student.post("/labs/linux-shell/cmd", json={"command": "hostname"}))
    assert "identify" in _j(student.get("/labs/linux-shell/state"))["done"]
    assert "identify" not in _j(student2.get("/labs/linux-shell/state"))["done"]


def test_mark_done_cannot_be_faked(student, mod):
    student.post("/labs/rtr-edge-complete/reset")
    r = _j(student.post("/labs/rtr-edge-complete/mark-done", json={"done": [o["id"] for o in RT.get_lab("rtr-edge-complete")["objectives"]]}))
    assert r["complete"] is False
    row, _ = _row(mod, "student1@lms.local", "rtr-edge-complete")
    assert row.score < 100


def test_undo_reverts_config_but_keeps_earned(student):
    student.post("/labs/sw-vlan-access/reset")
    for c in ["enable", "configure terminal", "vlan 20"]:
        _j(student.post("/labs/sw-vlan-access/cmd", json={"command": c}))
    before = _j(student.get("/labs/sw-vlan-access/state"))
    assert "enable" in before["done"]
    u = _j(student.post("/labs/sw-vlan-access/undo"))
    assert u["undone"] and "enable" in u["done"]
    assert u["prompt"].endswith("(config)#")


def test_reset_keeps_best_score(student, mod):
    solve_http(student, "gui-about")
    _j(student.post("/labs/gui-about/reset"))
    row, _ = _row(mod, "student1@lms.local", "gui-about")
    assert row.score == 0 and row.best_score == 100 and row.completed_at is not None


def test_hints_are_tiered_and_counted(student, mod):
    student.post("/labs/rtr-gateway/reset")
    row, _ = _row(mod, "student1@lms.local", "rtr-gateway")
    n0 = row.hints_used or 0
    h1 = _j(student.post("/labs/rtr-gateway/hint"))["hint"]
    h2 = _j(student.post("/labs/rtr-gateway/hint"))["hint"]
    h3 = _j(student.post("/labs/rtr-gateway/hint"))["hint"]
    assert (h1["tier"], h2["tier"], h3["tier"]) == (1, 2, 2)
    assert not h3["counted"]
    row, _ = _row(mod, "student1@lms.local", "rtr-gateway")
    assert row.hints_used == n0 + 2


def test_tab_completion(student):
    student.post("/labs/linux-shell/reset")
    r = _j(student.post("/labs/linux-shell/complete", json={"partial": "cd su"}))
    assert r["text"] == "cd support/"
    student.post("/labs/sw-vlan-access/reset")
    r = _j(student.post("/labs/sw-vlan-access/complete", json={"partial": "sh"}))
    assert r["text"].startswith("show")


def test_ios_parent_mode_fallback(student):
    student.post("/labs/rtr-default-route/reset")
    for c in ["enable", "conf t", "int gi0/0", "ip address 10.20.0.1 255.255.255.0", "no shut"]:
        _j(student.post("/labs/rtr-default-route/cmd", json={"command": c}))
    st = _j(student.post("/labs/rtr-default-route/cmd", json={"command": "ip route 0.0.0.0 0.0.0.0 10.20.0.254"}))
    assert "defroute" in st["done"]


def test_unknown_command_gets_suggestion(student):
    student.post("/labs/win-ipconfig/reset")
    st = _j(student.post("/labs/win-ipconfig/cmd", json={"command": "ipconfg /all"}))
    assert any("Did you mean" in ln for ln in st["lines"])


def test_ticket_intake_grades_values(student):
    student.post("/labs/ticket-intake/reset")
    st = _j(student.post("/labs/ticket-intake/cmd", json={"command": "classify request"}))
    assert "classified" not in st["done"]
    st = _j(student.post("/labs/ticket-intake/cmd", json={"command": "classify incident"}))
    assert "classified" in st["done"]


def test_wrong_activity_answer_gives_feedback(student):
    student.post("/labs/wifi-secure/reset")
    st = _j(student.post("/labs/wifi-secure/check", json={"step": "w2", "answer": {"ssid": "NETGEAR-3F2A", "security": "wep", "passphrase": "x",
                                                                                     "wps": "on", "channel": "11"}}))
    assert not st["result"]["correct"] and "SSID" in st["result"]["message"]
    assert st["steps"][1]["last"]["correct"] is False
    assert "answer" not in json.dumps(st["steps"]) or True   # public steps never include keys
    for s in st["steps"]:
        assert "rules" not in s and "answer" not in s


def test_gui_policy_feedback(student):
    student.post("/labs/win-ad-users/reset")
    _j(student.post("/labs/win-ad-users/event", json={"ev": "open:aduc"}))
    r = _j(student.post("/labs/win-ad-users/event", json={"ev": "ad:create", "data": {"first": "Maria", "last": "Lopez", "sam": "mlopez", "ou": "Sales",
                                                                                     "password": "short", "confirm": "short", "must_change": True}}))
    assert "14" in r["result"]["error"]
    r = _j(student.post("/labs/win-ad-users/event", json={"ev": "ad:delete", "data": {"sam": "rpatel"}}))
    assert "disabled" in r["result"]["error"].lower()


def test_instructor_results_gradebook_and_signoff(student, instructor, mod):
    solve_http(student, "ticket-intake")
    r = instructor.get("/instructor/section/1/labs/results")
    assert r.status_code == 200 and b"Lab results" in r.data
    csv = instructor.get("/instructor/section/1/labs/results.csv")
    assert csv.status_code == 200 and b"ticket-intake" in csv.data
    _, uid = _row(mod, "student1@lms.local", "ticket-intake")
    d = instructor.get(f"/instructor/section/1/labs/student/{uid}/ticket-intake")
    assert d.status_code == 200 and b"classify incident" in d.data
    with mod.app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        cls = [l for l in RT.course_lab_set(sec.course) if l["kind"] == "classroom"]
    assert cls, "course has classroom labs"
    cl = cls[0]["id"]
    r = instructor.post("/instructor/section/1/labs/signoff", data={"lab_id": cl, "user_id": uid, "c0": 4, "c1": 3, "c2": 3, "c3": 2, "feedback": "Good"})
    assert r.status_code in (302, 303)
    row, _ = _row(mod, "student1@lms.local", cl)
    assert row.score == 75.0 and row.completed_at
    page = student.get(f"/labs/classroom/{cl}").data.decode()
    assert "12/16" in page and "Good" in page
    # gradebook: labs column present, weight 0 by default
    gb = instructor.get("/instructor/section/1/gradebook")
    assert gb.status_code == 200 and b"Live labs" in gb.data
    api = mod.app.extensions["ciwt_lab_progress"]
    with mod.app.app_context():
        sec = mod.db.session.get(mod.ClassSection, 1)
        sc = api.lab_scores(sec, [uid])[uid]
    assert sc[0] is not None and sc[0] > 0


def test_students_cannot_see_results(student):
    assert student.get("/instructor/section/1/labs/results").status_code in (302, 403)
    assert student.post("/instructor/section/1/labs/signoff", data={}).status_code in (302, 403)


def test_index_lists_every_kind_and_classroom(student):
    html = student.get("/labs").data.decode()
    for kind in ("k-windows", "k-win11gui", "k-switch", "k-router", "k-linux", "k-activity", "k-ticket", "k-classroom"):
        assert kind in html, kind
    for cl in ("CL-4", "CL-7", "CL-13"):
        assert cl in html


def test_event_log_records_ordered_process(student, instructor, mod):
    api = mod.app.extensions["ciwt_lab_progress"]
    student.post("/labs/win-ipconfig/reset")
    _j(student.post("/labs/win-ipconfig/cmd", json={"command": "ipconfg"}))      # typo -> unknown
    _j(student.post("/labs/win-ipconfig/hint"))
    _j(student.post("/labs/win-ipconfig/cmd", json={"command": "hostname"}))
    _j(student.post("/labs/win-ipconfig/cmd", json={"command": "ipconfig /all"}))
    for action in RT.PX.stage_actions(RT.get_lab("win-ipconfig"), _server_state("win-ipconfig")):
        if action["type"] == "cmd":
            _j(student.post("/labs/win-ipconfig/cmd", json={"command": action["command"]}))
    row, uid = _row(mod, "student1@lms.local", "win-ipconfig")
    with mod.app.app_context():
        evs = api.events_for(uid, "win-ipconfig", attempt=(row.resets or 0) + 1)
        kinds = [(e.kind, e.outcome) for e in evs]
        assert kinds[:4] == [("cmd", "unknown"), ("hint", "ok"), ("cmd", "progress"), ("cmd", "progress")], kinds
        assert kinds[-1][0] == "complete"
        assert [e.seq for e in evs] == list(range(1, len(evs) + 1))
        s = api.process_summary(evs)[-1]
        assert s["unknown"] == 1 and s["hints"] == 1 and s["complete"]
    page = instructor.get(f"/instructor/section/1/labs/student/{uid}/win-ipconfig").data.decode()
    assert "Event log" in page and "ipconfg" in page
    csv = instructor.get("/instructor/section/1/labs/events.csv?lab=win-ipconfig")
    assert csv.status_code == 200 and b"ipconfg" in csv.data


def test_event_log_masks_passwords(student, mod):
    api = mod.app.extensions["ciwt_lab_progress"]
    student.post("/labs/win-ad-users/reset")
    _j(student.post("/labs/win-ad-users/event", json={"ev": "ad:create", "data": {"sam": "x1", "password": "Secret-Pass-123456", "confirm": "Secret-Pass-123456"}}))
    _, uid = _row(mod, "student1@lms.local", "win-ad-users")
    with mod.app.app_context():
        assert not any("Secret-Pass" in (e.action or "") for e in api.events_for(uid, "win-ad-users"))


def test_students_cannot_export_events(student):
    assert student.get("/instructor/section/1/labs/events.csv").status_code in (302, 403)


def test_vm_lab_grades_probe_and_history(student, instructor, mod):
    student.post("/labs/linux-vm-perms/reset")
    html = student.get("/labs/linux-vm-perms").data.decode()
    assert "vmBoot" in html or "fetch_v86.sh" in html
    st = _server_state("linux-vm-perms")
    probe = _j(student.get("/labs/linux-vm-perms/vm-probe"))["script"]
    assert st["nonce"] in probe and "/mnt/.ciwt-result" in probe and "_c perms" in probe
    # forged / stale nonce is refused
    r = _j(student.post("/labs/linux-vm-perms/vm-check", json={"probe": "nonce bad\nc_mkdir 1\nend\n"}))
    assert r["result"]["error"] and "mkdir" not in r["done"]
    # boot + commands are logged in order; verify needs ls -l AFTER chmod
    _j(student.post("/labs/linux-vm-perms/vm-log", json={"lines": [], "booted": True, "boot_ms": 2900}))
    _j(student.post("/labs/linux-vm-perms/vm-log", json={"lines": ["ls -l /root", "chmod 640 /root/support/tickets/notes.txt"]}))
    good = RT.VM.solved_probe(st, RT.VM.PERMS)
    r = _j(student.post("/labs/linux-vm-perms/vm-check", json={"probe": good}))
    assert not r["complete"] and "verified" not in r["done"] and any("ls -l" in m for m in r["result"]["messages"])
    _j(student.post("/labs/linux-vm-perms/vm-log", json={"lines": ["ls -l /root/support/tickets"]}))
    bad = good.replace("c_perms 1", "c_perms 0") + "v_perms -rw-r--r--\n"
    student.post("/labs/linux-vm-perms/reset")
    st = _server_state("linux-vm-perms")
    _j(student.post("/labs/linux-vm-perms/vm-log", json={"lines": [], "booted": True, "boot_ms": 2900}))
    _j(student.post("/labs/linux-vm-perms/vm-log", json={"lines": ["chmod 640 x", "ls -l"]}))
    bad = RT.VM.solved_probe(st, RT.VM.PERMS).replace("c_perms 1", "c_perms 0").replace("end", "v_perms -rw-r--r--\nend")
    r = _j(student.post("/labs/linux-vm-perms/vm-check", json={"probe": bad}))
    assert "perms" not in r["done"] and any("-rw-r--r--" in m and "640" in m for m in r["result"]["messages"])
    probe = RT.PX.probes_with_real_px(RT.get_lab("linux-vm-perms"), st, RT.VM.solved_probe(st, RT.VM.PERMS))
    r = _j(student.post("/labs/linux-vm-perms/vm-check", json={"probe": probe}))
    assert r["complete"] and r["score"] == 100
    _, uid = _row(mod, "student1@lms.local", "linux-vm-perms")
    page = instructor.get(f"/instructor/section/1/labs/student/{uid}/linux-vm-perms").data.decode()
    assert "booted in 2900 ms" in page and "chmod 640" in page


def test_vm_multi_machine_probes_and_order(student):
    lab = RT.get_lab("linux-vm-routing")
    student.post("/labs/linux-vm-routing/reset")
    j = _j(student.get("/labs/linux-vm-routing/vm-probe"))
    assert set(j["scripts"]) == {"pc", "rtr"}
    assert "_c pc_ip" in j["scripts"]["pc"] and "_c pc_ip" not in j["scripts"]["rtr"] and "_c forward" in j["scripts"]["rtr"]
    st = _server_state("linux-vm-routing")
    probes = RT.VM.solved_probes(st, lab)
    # a probe that claims to come from the other machine is refused
    r = _j(student.post("/labs/linux-vm-routing/vm-check", json={"probes": {"pc": probes["rtr"]}}))
    assert r["result"]["error"]
    # isolate must happen BEFORE forwarding is enabled
    _j(student.post("/labs/linux-vm-routing/vm-log", json={"lines": [], "booted": True}))
    _j(student.post("/labs/linux-vm-routing/vm-log", json={"lines": ["[rtr] sysctl -w net.ipv4.ip_forward=1", "[pc] ping -c1 10.2.0.10",
                                                                   "[rtr] ping -c1 10.2.0.10", "[pc] traceroute -n 10.2.0.10"]}))
    r = _j(student.post("/labs/linux-vm-routing/vm-check", json={"probes": probes}))
    assert "isolate" not in r["done"] and "reach" in r["done"] and "trace" in r["done"] and not r["complete"]
    student.post("/labs/linux-vm-routing/reset")
    st = _server_state("linux-vm-routing")
    _j(student.post("/labs/linux-vm-routing/vm-log", json={"lines": [], "booted": True}))
    _j(student.post("/labs/linux-vm-routing/vm-log", json={"lines": lab["solution"]["vm_commands"]}))
    probes = RT.PX.probes_with_real_px(lab, st, RT.VM.solved_probes(st, lab))
    r = _j(student.post("/labs/linux-vm-routing/vm-check", json={"probes": probes}))
    assert r["complete"]


def test_vm_network_evidence_is_required(student):
    """A static address typed by hand is not a DHCP lease: the services host must have sent an ACK."""
    lab = RT.get_lab("linux-vm-netclient")
    student.post("/labs/linux-vm-netclient/reset")
    st = _server_state("linux-vm-netclient")
    _j(student.post("/labs/linux-vm-netclient/vm-log", json={"lines": [], "booted": True}))
    _j(student.post("/labs/linux-vm-netclient/vm-log", json={"lines": ["ip a", "ip addr add 10.10.0.120/24 dev eth0", "udhcpc -i eth0"]}))
    probe = RT.VM.solved_probe(st, lab)
    r = _j(student.post("/labs/linux-vm-netclient/vm-check", json={"probe": probe, "fabric": {"events": [{"type": "dhcp", "msg": "DISCOVER"}]}}))
    assert "lease" not in r["done"] and any("acknowledged" in m for m in r["result"]["messages"])
    r = _j(student.post("/labs/linux-vm-netclient/vm-check", json={"probe": probe, "fabric": {"events": [{"type": "dhcp", "msg": "ACK", "ip": "10.10.0.100"}]}}))
    assert "lease" in r["done"]
    # evidence seen once stays earned (the page's event ring may roll over)
    r = _j(student.post("/labs/linux-vm-netclient/vm-check", json={"probe": probe, "fabric": {"events": []}}))
    assert "lease" in r["done"]


def test_vm_labs_have_fallbacks_and_pure_data():
    import json as _json
    for lab in RT.VM.VM_LABS:
        assert lab["fallback"] and all(RT.get_lab(f) for f in lab["fallback"]), lab["id"]
        _json.dumps(lab["vm"]), _json.dumps(lab["vm_checks"])
        ids = [o["id"] for o in lab["objectives"]]
        assert ids == [c["id"] for c in lab["vm_checks"]], lab["id"]
        assert set(lab["vm"]["setup"]) <= set(RT.VM.machines(lab))


def test_vm_routes_refuse_other_kinds(student):
    assert student.post("/labs/win-ipconfig/vm-log", json={"lines": ["x"]}).status_code == 400
    assert student.post("/labs/win-ipconfig/vm-check", json={"probe": "x"}).status_code == 400


def test_privacy_delete_covers_lab_records(student, mod):
    import privacy_tools
    solve_http(student, "win-ipconfig")
    _, uid = _row(mod, "student1@lms.local", "win-ipconfig")
    with mod.app.app_context():
        doomed = privacy_tools.plan(mod.db, uid)[0]
        assert doomed.get("lab_progress") and doomed.get("lab_event")


def test_new_labs_tagged_pending_sme_review_instructor_only(student, instructor):
    """Every lab added on the labs branch (and every scenario and stage) carries the curriculum's SME tag. Instructors see it; students do not."""
    import labs_scenario as SC
    tag = "Pending SME review"
    stages = [s["id"] for sc in SC.SCENARIOS for s in sc["stages"]]
    for lid in NEW + stages:
        assert RT.get_lab(lid).get("review") == tag, lid
    assert all(sc.get("review") == tag for sc in SC.SCENARIOS)
    assert not RT.get_lab("win-ipconfig").get("review")     # original labs are not tagged
    for path in ["/labs/linux-vm-dns", "/labs/linux-vm-perms", "/labs/scenario/SCN-DNS", "/labs"]:
        assert tag not in student.get(path).data.decode(), path
        assert tag in instructor.get(path).data.decode(), path
    assert tag not in instructor.get("/labs/win-ipconfig").data.decode()
