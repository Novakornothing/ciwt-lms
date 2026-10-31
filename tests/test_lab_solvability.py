"""Every later stage can be passed from information the simulator actually shows.

The scripted student may use the note, files the stage plants, and commands or
clicks the environment implements. A stage that names a command the simulator
rejects, or a file that was never planted, fails here. Each stage also has to
start unsolved, and Stage 3 must still be unsolved after only the Stage 2 fix.
"""
import hashlib
import json
import re
from copy import deepcopy

import lab_progression as PX
import lab_runtime as RT
import lab_skills as SK

LABS = [RT.get_lab(row["id"]) for row in RT.list_labs()]
SEEDS = range(1, 9)

_COMMANDS = (
    "show banner login",
    "show banner motd",
    "show version",
    "show mac address-table",
    "show running-config",
    "Get-Content ticket.txt",
    "ipconfig /all",
    "netstat -ano",
    "tasklist",
    "getmac",
    "ipconfig",
    "arp -a",
)
_MASKS = {"0.0.0.0", "255.255.255.0", "255.255.255.255", "255.0.0.0", "127.0.0.1"}


def _files(commands):
    world = SK._World()
    for cmd in commands or []:
        try:
            world.apply(cmd)
        except ValueError:
            continue
    return {path: node.get("content", "") for path, node in world.files.items()}


def _mentioned(text):
    low = text.lower()
    cmds = [cmd for cmd in _COMMANDS if cmd.lower() in low]
    if "ticket.txt" in low and "Get-Content ticket.txt" not in cmds:
        cmds.append("Get-Content ticket.txt")
    if re.search(r"\bshow banner\b", low) and "show banner login" not in low and "show banner motd" not in low:
        cmds.append("show banner")
    paths = []
    for p in re.findall(r"(/[A-Za-z0-9_./-]+)", text):
        p = p.rstrip(".")
        if p.startswith("/root/"):
            paths.append(p)
    return cmds, paths


def _run(lab, state, done, cmd):
    try:
        res, state, done = RT.run_command(lab["id"], deepcopy_state(state), list(done), cmd)
    except Exception as exc:
        raise AssertionError((lab["id"], cmd, type(exc).__name__, exc)) from exc
    lines = res.get("lines") or []
    return "\n".join(str(line) for line in lines), bool(res.get("unknown"))


def deepcopy_state(state):
    return deepcopy(state)


def _environment(lab, state, done, text, plant_cmds):
    files = _files(plant_cmds)
    cmds, paths = _mentioned(text)
    chunks = []
    for cmd in cmds:
        out, unknown = _run(lab, state, done, cmd)
        assert not unknown and "Invalid input" not in out and "not recognized" not in out, (
            lab["id"], cmd, out[:240],
        )
        chunks.append(out)
    for path in paths:
        hit = files.get(path)
        if hit is None:
            nested = [body for name, body in files.items() if name.startswith(path.rstrip("/") + "/")]
            assert nested or path in files or any(name == path for name in files), (
                lab["id"], "missing planted path", path, sorted(files),
            )
            chunks.extend(nested)
        else:
            chunks.append(hit)
    chunks.extend(files.values())
    return "\n".join(chunks), files


def _tokens(fix_cmds, checks):
    blob = "\n".join(str(cmd) for cmd in fix_cmds or [])
    found = set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", blob)) - _MASKS
    found.update(re.findall(r"(?i)\bvlan\s+(\d+)", blob))
    for match in re.finditer(r"-Name\s+(\S+)|-NewName\s+(\S+)|interface \"([^\"]+)\"", blob):
        found.add(next(g for g in match.groups() if g))
    for check in checks or []:
        text = check.get("text") or ""
        if text and ":x:" not in text:
            found.add(text)
        if check.get("hop"):
            found.add(check["hop"])
        if check.get("digest"):
            found.add(check["digest"])
    return {tok for tok in found if tok and tok not in ("1",)}


def _gui_source():
    from pathlib import Path
    return Path(__file__).resolve().parents[1].joinpath("static/js/lab-gui.js").read_text()


def _apply_stage(lab, state, done, stage):
    fam = PX.family(lab)
    facts = state["px"]["facts"]
    events = SK.stage_events(lab, facts, stage)
    if events:
        import labs_gui as LG
        for item in events:
            _, state, done = LG.apply(lab, state, done, item["ev"], item.get("data") or {})
        return PX.observe(lab, state, done)
    if fam in ("choice", "number"):
        answer = facts["assisted_answer" if stage == "assisted" else "ticket_answer"]
        _, state, done = PX.submit_answer(lab, state, done, stage, answer)
        return state, done
    for cmd in PX.followup_commands(lab, state, stage):
        try:
            _, state, done = RT.run_command(lab["id"], state, done, cmd)
        except Exception as exc:
            raise AssertionError((lab["id"], stage, cmd, type(exc).__name__, exc)) from exc
    return PX.observe(lab, state, done)


def _solve_vm(lab, spec, seed):
    state = RT.fresh_state(lab["id"], uid=seed)
    facts = state["px"]["facts"]
    both_plants = []
    for stage in ("assisted", "ticket"):
        row = spec["stages"][stage]
        plants = list((row.get("plant") or (lambda f: []))(facts) or [])
        both_plants.extend(plants)
        note = row["note"](facts)
        prose = row["prose"] if isinstance(row["prose"], str) else ""
        env, files = _environment(lab, state, [], f"{note}\n{prose}", plants)
        if stage == "ticket":
            env_low = env.lower()
            for tok in _tokens(row["fix"](facts), row["checks"](facts)):
                assert tok.lower() in env_low, (lab["id"], seed, stage, tok)
        for check in row["checks"](facts):
            if check.get("kind") != "sha256":
                continue
            matched = [path for path, body in files.items()
                       if hashlib.sha256(body.encode()).hexdigest() == check["digest"]]
            assert any(path != check["path"] for path in matched), (lab["id"], stage)
        checks = row["checks"](facts)
        assert not SK._run_stage(plants, [], checks), (lab["id"], seed, stage, "already passing")
    assisted = spec["stages"]["assisted"]
    ticket = spec["stages"]["ticket"]
    assert not SK._run_stage(both_plants, assisted["fix"](facts), ticket["checks"](facts)), (
        lab["id"], seed, "stage 3 passed after only stage 2",
    )
    assert SK._run_stage(assisted["plant"](facts), assisted["fix"](facts), assisted["checks"](facts)), (
        lab["id"], seed, "stage 2 fix did not pass",
    )
    assert SK._run_stage(both_plants, list(assisted["fix"](facts)) + list(ticket["fix"](facts)), ticket["checks"](facts)), (
        lab["id"], seed, "stage 3 fix did not pass",
    )


def test_stages_are_solvable_from_the_environment():
    gui_js = _gui_source()
    solved = 0
    for lab in LABS:
        if lab.get("kind") == "linuxgui" or not SK.has_spec(lab):
            continue
        spec = SK.spec(lab)
        if lab.get("kind") == "vm":
            for seed in SEEDS:
                _solve_vm(lab, spec, seed)
                solved += 1
            continue
        for seed in SEEDS:
            state = RT.fresh_state(lab["id"], uid=seed)
            done = [obj["id"] for obj in lab.get("objectives") or []]
            state, done = PX.observe(lab, state, done)
            assert "stage:assisted" not in done, (lab["id"], seed, "stage 2 already passed")
            assert "stage:ticket" not in done, (lab["id"], seed, "stage 3 already passed")
            facts = state["px"]["facts"]
            if PX.family(lab) in ("choice", "number"):
                assert facts["assisted_answer"] != facts["ticket_answer"], (lab["id"], seed)
            for stage in ("assisted", "ticket"):
                row = spec["stages"][stage]
                note = row["note"](facts)
                prose = row["prose"] if isinstance(row["prose"], str) else ""
                plant_fn = row.get("plant")
                plants = list(plant_fn(facts) or []) if plant_fn else []
                env, files = _environment(lab, state, done, f"{note}\n{prose}", plants)
                if stage == "ticket" and PX.family(lab) not in ("choice", "number"):
                    env_low = env.lower()
                    for tok in _tokens(row["fix"](facts), row["checks"](facts)):
                        assert tok.lower() in env_low, (lab["id"], seed, stage, tok)
                if "169.254" in note:
                    assert "169.254" in env, (lab["id"], seed, stage)
                for check in row["checks"](facts):
                    if check.get("kind") != "sha256":
                        continue
                    matched = [path for path, body in files.items()
                               if hashlib.sha256(body.encode()).hexdigest() == check["digest"]]
                    assert any(path != check["path"] for path in matched), (lab["id"], stage, matched)
                events = SK.stage_events(lab, facts, stage) or []
                for item in events:
                    ev = item["ev"]
                    present = (
                        ev in gui_js
                        or (ev.startswith("open:") and "send('open:" in gui_js)
                        or (ev.startswith("dev:") and "send('dev:" in gui_js)
                        or (ev.startswith("pane:") and "send('pane:" in gui_js)
                        or (ev.startswith("svc:") and ("send('svc:" in gui_js or "svc:start" in gui_js))
                        or (ev.startswith("adapter:") and "adapter:" in gui_js)
                    )
                    assert present, (lab["id"], ev)
                    for value in (item.get("data") or {}).values():
                        if not isinstance(value, str):
                            continue
                        visible = value in env or value in note or value in gui_js or value in json.dumps(state.get("gui") or {})
                        assert visible, (lab["id"], stage, value)
            state, done = _apply_stage(lab, state, done, "assisted")
            assert "stage:assisted" in done, (lab["id"], seed, "stage 2 fix did not pass")
            assert "stage:ticket" not in done, (lab["id"], seed, "stage 3 passed after only stage 2")
            state, done = _apply_stage(lab, state, done, "ticket")
            assert "stage:ticket" in done, (lab["id"], seed, "stage 3 fix did not pass")
            solved += 1
    assert solved == sum(1 for lab in LABS if lab.get("kind") != "linuxgui" and SK.has_spec(lab)) * len(SEEDS)
