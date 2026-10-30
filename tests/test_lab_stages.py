"""Every lab is a three-stage progression with discovery, not a copy of the walkthrough."""
import re

import lab_progression as PX
import lab_runtime as RT

LABS = [RT.get_lab(row["id"]) for row in RT.list_labs()]


def _narrative(html):
    text = re.sub(r'<ul class="syntax-card">.*?</ul>', " ", html or "", flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def test_every_lab_has_three_stages():
    assert len(LABS) == 137
    for lab in LABS:
        pub = PX.public(lab, {"seed": 1}, [])
        assert [s["id"] for s in pub["stages"]] == ["guided", "assisted", "ticket"], lab["id"]
        guided = pub["stages"][0]["html"]
        assert "cmd-text" in guided or lab["kind"] in ("activity", "win11gui", "ticket")
        assert "syntax-card" in pub["stages"][1]["html"]
        assert "syntax-card" in pub["stages"][2]["html"]
        assert "copy-btn" not in guided and "<button" not in guided.split("type-this")[0]


def test_later_stages_do_not_contain_walkthrough_commands():
    for lab in LABS:
        forbidden = [c.lower() for c in PX.solving_commands(lab)]
        pub = PX.public(lab, {"seed": 4}, [])
        for stage in pub["stages"]:
            if stage["id"] == "guided":
                continue
            text = _narrative(stage["html"]).lower()
            for cmd in forbidden:
                assert cmd not in text, (lab["id"], stage["id"], cmd)
            for tier in (1, 2):
                hint = PX.later_hint(lab, stage["id"], tier).lower()
                for cmd in forbidden:
                    assert cmd not in hint, (lab["id"], stage["id"], cmd)


def test_sentence_openings_are_not_repeated_filler():
    for lab in LABS:
        pub = PX.public(lab, {"seed": 1}, [])
        for stage in pub["stages"]:
            counts = PX.sentence_openings(stage["html"])
            over = {k: v for k, v in counts.items() if v > 2}
            assert not over, (lab["id"], stage["id"], over)


def test_two_seeds_change_the_values():
    for lab in LABS:
        a = PX.facts(lab, 1)
        b = PX.facts(lab, 2)
        interesting = ("assisted_dns", "ticket_host", "assisted_vlan", "assisted_token", "assisted_answer", "note_path")
        assert any(a[k] != b[k] for k in interesting), lab["id"]
        assert a["assisted_dns"] != a["guided_dns"]
        assert a["assisted_vlan"] != a["guided_vlan"]


def test_checkers_read_end_state_and_reject_walkthrough_values():
    lab = RT.get_lab("sw-vlan-access")
    state = RT.fresh_state(lab["id"], uid=1)
    done = [o["id"] for o in lab["objectives"]]
    state["vlans"][20] = "TRAINING"
    state["interfaces"]["FastEthernet0/2"]["vlan"] = 20
    state["interfaces"]["FastEthernet0/2"]["mode"] = "access"
    state, done = PX.observe(lab, state, done)
    assert "stage:guided" in done and "stage:assisted" not in done
    facts = state["px"]["facts"]
    state["vlans"][facts["assisted_vlan"]] = facts["assisted_name"]
    state["interfaces"]["FastEthernet0/3"]["vlan"] = facts["assisted_vlan"]
    state["interfaces"]["FastEthernet0/3"]["mode"] = "access"
    state, done = PX.observe(lab, state, done)
    assert "stage:assisted" in done and "stage:ticket" not in done

    win = RT.get_lab("win-ipconfig")
    st = RT.fresh_state(win["id"], uid=5)
    done = [o["id"] for o in win["objectives"]]
    st, done = PX.observe(win, st, done)
    assert "stage:guided" in done and "stage:assisted" not in done
    st["dns"] = [st["px"]["facts"]["guided_dns"]]
    st, done = PX.observe(win, st, done)
    assert "stage:assisted" not in done
    st["dns"] = [st["px"]["facts"]["assisted_dns"]]
    st, done = PX.observe(win, st, done)
    assert "stage:assisted" in done

    linux = RT.get_lab("linux-shell")
    lx = RT.fresh_state(linux["id"], uid=8)
    f = lx["px"]["facts"]
    assert not PX._file_ok(lx["fs"], f["assisted_path"], f["assisted_token"], f["assisted_mode"])
    lx["fs"][f["assisted_path"]] = {"t": "f", "mode": int(f["assisted_mode"], 8), "c": f["assisted_token"] + "\n"}
    assert PX._file_ok(lx["fs"], f["assisted_path"], f["assisted_token"], f["assisted_mode"])
    lx["fs"][f["assisted_path"]]["c"] = "ticket 4512\n"
    assert not PX._file_ok(lx["fs"], f["assisted_path"], f["assisted_token"], f["assisted_mode"])


def test_vm_probe_checks_the_file_not_the_walkthrough_line():
    lab = RT.get_lab("linux-vm-perms")
    state = RT.fresh_state(lab["id"], uid=3)
    script = RT.VM.probe_script(state, lab)
    token = state["px"]["facts"]["assisted_token"]
    assert token in script and "px_assisted" in script and "grep -qx" in script
    assert token != "ticket 4512"
    solved = RT.VM.solved_probe(state, lab)
    assert "c_px_assisted 1" in solved and "c_px_ticket 1" in solved
