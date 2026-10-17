"""One entry point for every LMS lab engine (used by lab_progress.py, tests and tools).

Kinds: windows · switch · router · ticket (incl. hw bench) — interactive_labs engines;
linux — labs_linux; win11gui — labs_gui (event model); activity — labs_activity (graded steps).
All state lives in the database (lab_progress); this module is pure: (state, done) in → (result, state, done) out.
"""
import hashlib
import re
from copy import deepcopy

import interactive_labs as IL
import labs_activity as LA
import labs_gui as LG
import labs_linux as LX

KIND_GROUPS = [
    ("ticket", "Help desk & bench", "Ticket intake and the hardware bench card."),
    ("activity", "Interactive activities", "Subnetting, connectors, builds, methodology, Wi-Fi, malware, backup, VMs, mobile — drag, tap or type."),
    ("windows", "Windows command line", "cmd and PowerShell on a Windows 11 VM."),
    ("win11gui", "Windows 11 desktop", "Settings, Services, Device Manager, Network Connections and Active Directory."),
    ("linux", "Linux shell", "bash on a support server."),
    ("switch", "Switch (IOS)", "VLANs, access ports, trunks, port security."),
    ("router", "Router (IOS)", "Interfaces, routes, inter-VLAN routing and ACLs."),
]
KIND_LABEL = {k: t for k, t, _ in KIND_GROUPS}
IOS_SUBMODES = ("config-if", "config-vlan", "config-subif")
UNKNOWN_MARKERS = ("invalid input", "not recognized", "command not found", "unknown command", "type help")


def get_lab(lab_id):
    return IL.get_lab(lab_id)


def list_labs():
    out = []
    for lab in IL.LABS:
        out.append({"id": lab["id"], "title": lab["title"], "kind": lab["kind"], "kind_label": KIND_LABEL.get(lab["kind"], lab["kind"]),
                    "blurb": lab.get("blurb") or "", "builds_on": lab.get("builds_on") or [],
                    "objectives": len(lab["objectives"]), "minutes": lab.get("minutes") or 10 + 3 * len(lab["objectives"]),
                    "course_objectives": lab.get("course_objectives") or []})
    return out


def _seed(lab_id, uid, reseed):
    return int(hashlib.sha1(f"{lab_id}:{uid}:{reseed}".encode()).hexdigest()[:8], 16)


def fresh_state(lab_id, uid=0, reseed=0):
    lab = get_lab(lab_id)
    if not lab:
        return None
    st = deepcopy(lab["initial_state"])
    if lab["kind"] == "linux" and "fs" not in st:
        st.update(LX.linux_state())
    if lab["kind"] == "win11gui" and not st.get("gui"):
        st["gui"] = LG.gui_state()
    st["seed"] = _seed(lab_id, uid, reseed)
    st["objectives"] = [o["id"] for o in lab["objectives"]]
    if lab.get("steps"):
        LA.ensure_generated(lab["steps"], st)
    return st


def prompt(lab, state):
    if lab["kind"] == "linux":
        return LX.prompt(state)
    if lab["kind"] in ("activity", "win11gui"):
        return ""
    return IL.prompt_for(lab, state)


def _ids(lab):
    return [o["id"] for o in lab["objectives"]]


def _clean(lab, done):
    ids = _ids(lab)
    seen = []
    for d in done or []:
        if d in ids and d not in seen:
            seen.append(d)
    return seen


def score(lab, done):
    ids = _ids(lab)
    if not ids:
        return 0.0
    return round(100.0 * len([i for i in ids if i in (done or [])]) / len(ids), 1)


def is_complete(lab, done):
    return set(_ids(lab)) <= set(done or [])


def view(lab, state, done):
    done = done or []
    out = {
        "prompt": prompt(lab, state), "kind": lab["kind"],
        "objectives": [{"id": o["id"], "text": o["text"], "done": o["id"] in done} for o in lab["objectives"]],
        "score": score(lab, done),
        "next": next((o["id"] for o in lab["objectives"] if o["id"] not in done), None),
    }
    if lab["kind"] == "win11gui":
        g = deepcopy(state.get("gui") or {})
        g.pop("seen", None)
        out["gui"] = g
        out["facts"] = {k: state.get(k) for k in ("hostname", "ipv4", "mask", "gateway", "dns", "edition", "version", "build", "user", "domain")}
    if lab.get("steps"):
        out["steps"] = public_steps(lab, state)
    return out


def public_steps(lab, state):
    return [LA.public_step(s, state) for s in (lab.get("steps") or [])]


def palette(lab):
    if lab.get("palette"):
        return list(lab["palette"])
    k = lab["kind"]
    if k in ("switch", "router"):
        base = ["enable", "conf t", "interface ", "end", "show running-config", "write", "?"]
    elif k == "windows":
        base = ["ipconfig /all", "ping ", "nslookup ", "powershell", "cls", "help"]
    elif k == "linux":
        base = ["ls -l", "cd ", "cat ", "clear", "help"]
    elif k == "ticket":
        base = ["help", "show ticket" if lab["id"] != "hw-board" else "show board", "submit"]
    else:
        return []
    # add the first word(s) of the lab's own hints
    for h in lab.get("hints") or []:
        h = str(h).strip()
        if not h or "…" in h or "..." in h or len(h) > 40:
            continue
        if h not in base:
            base.insert(len(base) - 1, h)
        if len(base) >= 12:
            break
    return base


# ------------------------------------------------------------------ commands


def _is_unknown(lines):
    blob = " ".join(lines[:3]).lower()
    return any(m in blob for m in UNKNOWN_MARKERS)


def run_command(lab_id, state, done, command):
    lab = get_lab(lab_id)
    if not lab:
        return {"lines": ["Unknown lab."], "unknown": True}, state, done
    state = deepcopy(state) if state else fresh_state(lab_id)
    done = list(done or [])
    cmd = (command or "").strip()
    kind = lab["kind"]
    if kind in ("activity", "win11gui"):
        return {"lines": ["This lab has no terminal."], "unknown": True}, state, done
    if not cmd:
        return {"lines": []}, state, done
    if cmd.lower() in ("clear", "cls") or cmd == "\x0c":
        return {"lines": [], "clear": True}, state, done
    extra = []
    if kind == "linux":
        def mark(oid):
            if oid not in done:
                done.append(oid)

        def rules(st, dn, ev):
            fn = lab.get("rules")
            if fn:
                r = fn(st, dn, ev)
                if r:
                    extra.extend(r)
        lines, unknown = LX.run(cmd, state, done, mark, rules)
        lines = list(lines) + extra
        for ln in list(lines):
            m = re.search(r"(?:cd: |cannot access '|: )([^':]+?)'?: No such file or directory", ln)
            if m:
                near = LX.near_names(state, m.group(1).strip())
                if near:
                    lines.append("Did you mean: " + ", ".join(near) + " ?  (Linux names are case-sensitive; Tab completes them.)")
                break
        done = _clean(lab, done)
        return {"lines": lines, "unknown": bool(unknown)}, state, done

    expanded = cmd
    if kind in ("switch", "router") and not cmd.endswith("?") and cmd.lower() != "help":
        mode = state.get("mode") or "user"
        exp, err = IL.expand_ios_line(cmd, kind, mode=mode)
        if err and mode in IOS_SUBMODES:
            # IOS falls back to global configuration for a global command typed in a sub-mode
            exp2, err2 = IL.expand_ios_line(cmd, kind, mode="config")
            if not err2:
                state["mode"] = "config"
                state["prompt_if"] = None
                state["edit_vlan"] = None
                exp, err = exp2, None
        if not err and exp:
            expanded = exp
    result, state, done = IL.run_command(lab_id, state, done, cmd)
    lines = list(result.get("lines") or [])
    if result.get("clear"):
        return {"lines": [], "clear": True}, state, _clean(lab, done)
    auto = lab.get("auto")
    if auto:
        more = auto(state, done, expanded, lines)
        if more:
            lines += more
    done = _clean(lab, done)
    return {"lines": lines, "unknown": _is_unknown(lines)}, state, done


def complete(lab, state, partial):
    partial = partial or ""
    k = lab["kind"]
    if k == "linux":
        return LX.complete(state, partial)
    if k in ("switch", "router"):
        try:
            res = IL.complete_ios_line(partial, k, mode=state.get("mode") or "user")
        except TypeError:
            res = IL.complete_ios_line(partial, k, state.get("mode") or "user")
        if isinstance(res, dict):
            return res
        text, opts = (res if isinstance(res, tuple) else (res, []))
        return {"text": text or partial, "options": list(opts or []), "beep": not text or text == partial}
    if k == "windows":
        pool = palette(lab) + [h for h in (lab.get("hints") or []) if isinstance(h, str)] + list(getattr(IL, "_WIN_COMPLETIONS", []))
        pool += ["ipconfig", "ipconfig /all", "ipconfig /release", "ipconfig /renew", "ipconfig /flushdns", "ping", "tracert", "nslookup",
                 "netstat -an", "hostname", "whoami", "systeminfo", "tasklist", "getmac", "arp -a", "route print", "powershell", "cmd",
                 "Get-NetIPConfiguration", "Get-NetAdapter", "Get-Service", "Test-Connection", "Get-Printer", "Get-PrintJob",
                 "Remove-PrintJob", "Restart-Service", "Resolve-DnsName", "Get-Process", "Get-NetIPAddress", "Clear-DnsClientCache",
                 "netsh wlan show interfaces", "netsh interface show interface", "winver", "help", "cls"]
        low = partial.lower()
        opts = sorted({p.strip() for p in pool if p.strip().lower().startswith(low) and p.strip().lower() != low}, key=len)
        if len(opts) == 1:
            return {"text": opts[0] + ("" if opts[0].endswith(" ") else " "), "options": opts, "beep": False}
        if opts:
            common = opts[0]
            for o in opts[1:]:
                i = 0
                while i < min(len(common), len(o)) and common[i].lower() == o[i].lower():
                    i += 1
                common = common[:i]
            return {"text": common if len(common) > len(partial) else partial, "options": opts[:12], "beep": True}
        return {"text": partial, "options": [], "beep": True}
    if k == "ticket":
        pool = ["help", "show ticket", "show board", "classify ", "impact ", "escalate ", "note ", "submit", "form-factor ", "socket ",
                "memory ", "storage ", "post "]
        opts = [p for p in pool if p.startswith(partial.lower())]
        if len(opts) == 1:
            return {"text": opts[0], "options": opts, "beep": False}
        return {"text": partial, "options": opts, "beep": True}
    return {"text": partial, "options": [], "beep": True}


# ------------------------------------------------------------------ GUI events and graded steps


def apply_event(lab_id, state, done, ev, data):
    lab = get_lab(lab_id)
    state = deepcopy(state) if state else fresh_state(lab_id)
    done = list(done or [])
    if not lab or lab["kind"] != "win11gui":
        return {"error": "This lab has no desktop.", "changed": False}, state, done
    result, state, done = LG.apply(lab, state, done, ev, data if isinstance(data, dict) else {})
    return result, state, _clean(lab, done)


def _step(lab, step_id):
    return next((s for s in (lab.get("steps") or []) if s["id"] == step_id), None)


def check_step(lab_id, state, done, step_id, answer):
    lab = get_lab(lab_id)
    state = deepcopy(state) if state else fresh_state(lab_id)
    done = list(done or [])
    st = _step(lab, step_id) if lab else None
    if not st:
        return {"correct": False, "message": "Unknown step."}, state, done
    LA.ensure_generated(lab["steps"], state)
    try:
        res = LA.grade(st, answer, state)
    except Exception:
        res = {"correct": False, "message": "That answer could not be read — check every box is filled in.", "per": {}}
    state.setdefault("answers", {})[step_id] = answer
    state.setdefault("feedback", {})[step_id] = {"correct": res["correct"], "message": res.get("message", ""), "per": res.get("per", {})}
    att = state.setdefault("attempts", {})
    att[step_id] = att.get(step_id, 0) + 1
    if res["correct"] and st["objective"] not in done:
        done.append(st["objective"])
    res["attempts"] = att[step_id]
    return res, state, _clean(lab, done)


# ------------------------------------------------------------------ hints

_DERIVED = {}


def _derived_hints(lab):
    """Replay the lab's known-good command path and record which command first earns each objective."""
    if lab["id"] in _DERIVED:
        return _DERIVED[lab["id"]]
    cmds = []
    if lab.get("solution", {}).get("commands"):
        cmds = lab["solution"]["commands"]
    elif lab["id"] in IL.VERIFY_SEQUENCES:
        cmds = IL.VERIFY_SEQUENCES[lab["id"]][0]
    out = {}
    if cmds and lab["kind"] not in ("activity", "win11gui"):
        state, done, since = fresh_state(lab["id"]), [], []
        for c in cmds:
            before = set(done)
            _, state, done = run_command(lab["id"], state, done, c)
            since.append(c)
            for oid in done:
                if oid not in before and oid not in out:
                    out[oid] = list(since)
            if set(done) - before:
                since = []
    _DERIVED[lab["id"]] = out
    return out


def next_hint(lab, state, done, hints_used):
    done = done or []
    pending = [o for o in lab["objectives"] if o["id"] not in done]
    if not pending:
        return {"objective": None, "tier": 0, "counted": False, "text": "Every objective is complete."}
    o = pending[0]
    tiers = (state or {}).get("_hint_tier") or {}
    cur = int(tiers.get(o["id"], 0))
    tier = min(cur + 1, 2)
    counted = tier > cur
    oh = (lab.get("obj_hints") or {}).get(o["id"])
    step = next((s for s in (lab.get("steps") or []) if s["objective"] == o["id"]), None)
    if oh:
        text = oh[min(tier, len(oh)) - 1]
    elif step is not None:
        text = ("Re-read the scenario and the feedback under the question." if tier == 1 else
                "Use the feedback: each wrong choice explains why it is wrong. Eliminate those and check again.")
    else:
        seq = _derived_hints(lab).get(o["id"])
        if seq and lab["kind"] != "win11gui":
            text = (f"Next: {o['text']}. Start with: {seq[-1].split()[0]}" if tier == 1 else
                    "Type: " + "  →  ".join(seq))
        else:
            idx = [x["id"] for x in lab["objectives"]].index(o["id"])
            hs = lab.get("hints") or []
            text = (f"Next: {o['text']}." if tier == 1 else
                    (hs[idx] if idx < len(hs) else o["text"]))
    return {"objective": o["id"], "objective_text": o["text"], "tier": tier, "counted": counted, "text": text,
            "max": tier >= 2}


# ------------------------------------------------------------------ classroom labs, rubric, course sets


def _cp():
    from curriculum_v2 import course_package as CP
    return CP


def classroom_lab(cl_id):
    cl = _cp().CLASSROOM_LABS.get(cl_id or "")
    if not cl:
        return None
    out = dict(cl)
    out.setdefault("id", cl_id)
    out["kind"] = "classroom"
    out["objectives"] = [{"id": "signed_off", "text": "Instructor sign-off against the lab rubric"}]
    return out


def lab_rubric():
    return _cp().RUBRICS["lab"]


def course_lab_set(course):
    """Interactive labs used in this course's chapters plus its classroom labs (in chapter order)."""
    code = (getattr(course, "code", None) or "")
    seen, out = set(), []
    for (c, ch), ids in sorted(IL.CHAPTER_LABS.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        if c != code:
            continue
        for i in ids:
            lab = get_lab(i)
            if lab and i not in seen:
                seen.add(i)
                out.append({"id": i, "title": lab["title"], "kind": lab["kind"], "chapter": ch})
    for cid, cl in _cp().CLASSROOM_LABS.items():
        chs = [ch for c, ch in cl.get("chapters") or [] if c == code]
        if code == "CLIENT":
            chs += [ch - 7 for c, ch in cl.get("chapters") or [] if c == "ITSUP" and 8 <= ch <= 13]
        if chs and cid not in seen:
            seen.add(cid)
            out.append({"id": cid, "title": cl["title"], "kind": "classroom", "chapter": min(chs)})
    out.sort(key=lambda l: (l["chapter"], l["kind"] == "classroom"))
    return out


# ------------------------------------------------------------------ verification


def solve(lab_id, uid=0):
    """Run the lab's known-good path through the same functions the web routes use. Returns (state, done, log)."""
    lab = get_lab(lab_id)
    state, done, log = fresh_state(lab_id, uid), [], []
    sol = lab.get("solution") or {}
    cmds = sol.get("commands")
    if cmds is None and lab["id"] in IL.VERIFY_SEQUENCES:
        cmds = IL.VERIFY_SEQUENCES[lab["id"]][0]
    for c in cmds or []:
        res, state, done = run_command(lab_id, state, done, c)
        log.append((c, res))
    for ev, data in sol.get("events") or _default_events(lab):
        res, state, done = apply_event(lab_id, state, done, ev, data)
        log.append((ev, res))
    answers = sol.get("answers") or {}
    if callable(answers):
        answers = answers(state)
    for st in lab.get("steps") or []:
        a = answers.get(st["id"])
        if callable(a):
            a = a(state)
        res, state, done = check_step(lab_id, state, done, st["id"], a)
        log.append((st["id"], res))
    return state, done, log


GUI_SOLUTIONS = {
    "gui-about": ["open:settings", "pane:system", "pane:about"],
    "gui-ethernet": ["open:settings", "pane:network", "pane:ethernet"],
    "gui-renew": ["open:settings", "pane:network", "pane:advanced", "adapter:disable", "adapter:enable"],
    "gui-services": ["open:services", "svc:Dhcp", "svc:Dnscache", "svc:WinDefend"],
    "gui-update": ["open:settings", "pane:update", "update:check"],
    "gui-accounts": ["open:settings", "pane:accounts"],
    "gui-devices": ["open:devmgr", "dev:net", "dev:display"],
}


def _default_events(lab):
    if lab["kind"] != "win11gui":
        return []
    return [(e, {}) for e in GUI_SOLUTIONS.get(lab["id"], [])]


def verify_all_labs():
    ok, report = IL.verify_all_labs()
    for lab in IL.LABS:
        try:
            state, done, _ = solve(lab["id"], uid=1)
        except Exception as e:  # pragma: no cover - reported
            ok = False
            report.append(f"FAIL {lab['id']} (runtime path): {type(e).__name__}: {e}")
            continue
        missing = [i for i in _ids(lab) if i not in done]
        if missing:
            ok = False
            report.append(f"FAIL {lab['id']} (runtime path): missing={missing}")
        else:
            report.append(f"PASS {lab['id']} (runtime path, {lab['kind']})")
    return ok, report


if __name__ == "__main__":
    passed, lines = verify_all_labs()
    for ln in lines:
        if not ln.startswith("PASS") or "runtime" in ln:
            print(ln)
    raise SystemExit(0 if passed else 1)
