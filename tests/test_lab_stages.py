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
            html = re.sub(r"<code[^>]*>.*?</code>", " ", stage["html"], flags=re.S)
            counts = PX.sentence_openings(html)
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
    st["dns"] = [st["px"]["facts"]["w_ip"]]
    st, done = PX.observe(win, st, done)
    assert "stage:assisted" in done

    linux = RT.get_lab("linux-shell")
    lx = RT.fresh_state(linux["id"], uid=8)
    f = lx["px"]["facts"]
    assert not PX.end_state_ok(linux, "assisted", lx, [o["id"] for o in linux["objectives"]] + ["stage:guided"])
    lx["fs"][f["s2_path"]]["mode"] = int(f["s2_mode"], 8)
    assert PX.end_state_ok(linux, "assisted", lx, [o["id"] for o in linux["objectives"]] + ["stage:guided"])
    lx["fs"][f["s2_path"]]["mode"] = 0o666
    assert not PX.end_state_ok(linux, "assisted", lx, [o["id"] for o in linux["objectives"]] + ["stage:guided"])


def _story(html):
    m = re.search(r'<div class="stage-story">(.*?)</div>', html or "", flags=re.S)
    text = m.group(1) if m else ""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _shingles(text, n=5):
    words = _words(text)
    if len(words) < n:
        return set()
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def test_stage_two_and_three_do_not_share_sentences_or_shingles():
    """Different labs must not reuse an 8-word sentence or more than 40% of 5-word shingles."""
    pubs = {lab["id"]: PX.public(lab, {"seed": 1}, []) for lab in LABS}
    for stage in ("assisted", "ticket"):
        texts = {lid: _story(pub["stages"][{"guided": 0, "assisted": 1, "ticket": 2}[stage]]["html"]) for lid, pub in pubs.items()}
        seen = {}
        for lid, text in texts.items():
            for sentence in _sentences(text):
                if len(_words(sentence)) < 8:
                    continue
                seen.setdefault(sentence.lower(), []).append(lid)
        shared = {s: labs for s, labs in seen.items() if len(labs) > 1}
        assert not shared, (stage, list(shared.items())[:3])
        ids = list(texts)
        bags = {lid: _shingles(texts[lid]) for lid in ids}
        worst = (0.0, "", "")
        for i, left in enumerate(ids):
            for right in ids[i + 1:]:
                a, b = bags[left], bags[right]
                if not a and not b:
                    score = 0.0
                else:
                    score = len(a & b) / len(a | b)
                if score > worst[0]:
                    worst = (score, left, right)
                assert score <= 0.40, (stage, left, right, round(score, 3))


_TRIVIAL = {"hostname", "computer-name", "proof-token", "token-file"}


def _stage_sentences(html):
    text = re.sub(r'<ul class="syntax-card">.*?</ul>', " ", html or "", flags=re.S)
    text = re.sub(r"<button[^>]*>.*?</button>", " ", text, flags=re.S)
    text = re.sub(r"<form[^>]*>.*?</form>", " ", text, flags=re.S)
    text = re.sub(r"<h3[^>]*>.*?</h3>", " ", text, flags=re.S)
    text = re.sub(r"<code[^>]*>.*?</code>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(_words(s)) >= 8]


def test_stage3_checker_is_the_labs_skill():
    import lab_skills as SK
    for lab in LABS:
        kind = SK.checker(lab, "ticket")
        if kind is None and lab.get("kind") == "linuxgui":
            continue
        assert kind and kind not in _TRIVIAL, (lab["id"], kind)


def test_stage_text_does_not_turn_dots_into_commas():
    for lab in LABS:
        pub = PX.public(lab, {"seed": 1}, [])
        for stage in pub["stages"]:
            html = stage["html"]
            assert not re.search(r"\d,\d,\d,\d", html), (lab["id"], stage["id"])
            assert "notes,txt" not in html and "backup,sh" not in html, lab["id"]


def test_no_stage_sentence_is_shared_by_more_than_five_labs():
    from collections import defaultdict
    seen = defaultdict(set)
    for lab in LABS:
        pub = PX.public(lab, {"seed": 1}, [])
        for stage in pub["stages"]:
            for sentence in _stage_sentences(stage["html"]):
                seen[sentence.lower()].add(lab["id"])
    shared = {s: labs for s, labs in seen.items() if len(labs) > 5}
    assert not shared, list(shared.items())[:3]


def test_syntax_card_does_not_contain_the_seeded_answer_command():
    import lab_skills as SK
    for lab in LABS:
        if not SK.has_spec(lab):
            continue
        facts = PX.facts(lab, 3)
        card = " ".join(row["form"] for row in PX.syntax_card(lab))
        for stage in ("assisted", "ticket"):
            for cmd in SK.fix_commands(lab, facts, stage) or []:
                if not re.search(r"\d", str(cmd)):
                    continue
                assert str(cmd) not in card, (lab["id"], cmd)


def test_vm_file_check_runs_real_grep_and_solved_probe_does_not_fake_it():
    import lab_skills as SK
    lab = RT.get_lab("linux-vm-perms")
    state = RT.fresh_state(lab["id"], uid=3)
    script = RT.VM.probe_script(state, lab)
    path = state["px"]["facts"]["s2_path"]
    assert path in script and "px_assisted" in script and "ls -l" in script
    assert "c_px_assisted" not in RT.VM.solved_probe(state, lab)
    assert "proof-" not in script
    facts = state["px"]["facts"]
    assert SK.stage_fails_until_fixed(lab, facts, "assisted")
    assert SK.stage_fails_until_fixed(lab, facts, "ticket")
    made = SK.evaluate(lab, facts)
    assert made == ["c_px_assisted 1", "c_px_ticket 1"]
