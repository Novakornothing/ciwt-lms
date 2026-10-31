"""Per-lab Stage 2 and Stage 3 skills.

A lab in SPECS is graded on that skill's end state. Stage 2 names the seeded
values in the desk note. Stage 3 describes the symptom. The fix commands are
for the solver only. They are not the syntax card.
"""
from __future__ import annotations

import hashlib
import ipaddress
import os
import re
import shlex
import subprocess
import tempfile

SPECS: dict = {}


def spec(lab):
    if not lab:
        return None
    return SPECS.get(lab.get("id"))


def has_spec(lab):
    return spec(lab) is not None


def checker(lab, stage):
    row = spec(lab)
    if not row:
        return None
    return row["stages"][stage]["checker"]


def prose(lab, stage):
    row = spec(lab)
    if not row:
        return None
    return row["stages"][stage]["prose"]


def note(lab, stage, facts):
    row = spec(lab)
    if not row:
        return None
    return row["stages"][stage]["note"](facts)


def syntax(lab):
    row = spec(lab)
    if not row:
        return None
    return [{"label": a, "form": b} for a, b in row["syntax"]]


def enrich(lab, facts, seed):
    row = spec(lab)
    if not row:
        return facts
    row["enrich"](facts, int(seed or 1))
    return facts


def plant_fs(lab, state, facts):
    row = spec(lab)
    if not row or not isinstance(state.get("fs"), dict) or not facts:
        return
    world = _World()
    for stage in ("assisted", "ticket"):
        for cmd in row["stages"][stage]["plant"](facts):
            world.apply(cmd)
    user = state.get("user") or "root"
    for path, node in world.files.items():
        parent = path.rsplit("/", 1)[0]
        if parent and parent not in state["fs"]:
            state["fs"][parent] = {"t": "d", "mode": 0o755, "owner": "root", "group": "root"}
        if path in state["fs"]:
            continue
        owner = node.get("owner") or "root"
        if user != "root" and owner == "root":
            owner = user
        state["fs"][path] = {
            "t": "f",
            "mode": node.get("mode", 0o644),
            "owner": owner,
            "group": node.get("group") or "root",
            "c": node.get("content", ""),
        }


def plant_shell(lab, facts):
    row = spec(lab)
    if not row:
        return ""
    lines = []
    for stage in ("assisted", "ticket"):
        lines.extend(row["stages"][stage].get("plant")(facts) or [])
    return "\n".join(lines) + ("\n" if lines else "")


def fix_commands(lab, facts, stage):
    row = spec(lab)
    if not row:
        return None
    return list(row["stages"][stage]["fix"](facts))


def probe_pairs(lab, facts):
    row = spec(lab)
    if not row:
        return None
    out = []
    for stage, key in (("assisted", "px_assisted"), ("ticket", "px_ticket")):
        out.append((key, _shell(row["stages"][stage]["checks"](facts))))
    return out


def fs_ok(lab, stage, state, facts):
    row = spec(lab)
    if not row:
        return False
    fs = (state or {}).get("fs") or {}
    return _model_ok(_fs_world(fs), row["stages"][stage]["checks"](facts))


def evaluate(lab, facts):
    """Run each stage's plant, then its fix, and return probe lines from the result.

    File checks run with chmod, grep, and ls in a temp directory. Checks that
    need a routing table, packet filter, or crontab are applied to an in-memory
    model of those tables. That model is a checker unit test: it does not boot
    the guest and it does not mark a check passed unless the fix produced the
    required state.
    """
    row = spec(lab)
    if not row:
        return []
    lines = []
    for stage, key in (("assisted", "px_assisted"), ("ticket", "px_ticket")):
        stage_row = row["stages"][stage]
        checks = stage_row["checks"](facts)
        ok = _run_stage(stage_row["plant"](facts), stage_row["fix"](facts), checks)
        lines.append(f"c_{key} {1 if ok else 0}")
    return lines


def stage_fails_until_fixed(lab, facts, stage):
    """True when the planted fault fails and the fix commands make it pass."""
    row = spec(lab)["stages"][stage]
    checks = row["checks"](facts)
    planted = _run_stage(row["plant"](facts), [], checks)
    fixed = _run_stage(row["plant"](facts), row["fix"](facts), checks)
    return (not planted) and fixed


def _write_fs(fs, node, facts):
    path = node["path"](facts) if callable(node["path"]) else node["path"]
    parent = path.rsplit("/", 1)[0]
    if parent and parent not in fs:
        fs[parent] = {"t": "d", "mode": 0o755, "owner": "root", "group": "root"}
    fs[path] = {
        "t": "f",
        "mode": int(str(node["mode"](facts) if callable(node["mode"]) else node["mode"]), 8),
        "owner": node.get("owner", "root"),
        "group": node.get("group", "root"),
        "c": (node["content"](facts) if callable(node["content"]) else node.get("content") or "") ,
    }


def _fs_world(fs):
    world = _World()
    for path, node in fs.items():
        if node.get("t") == "f":
            world.files[path] = {
                "mode": node.get("mode", 0),
                "owner": node.get("owner", "root"),
                "content": node.get("c", ""),
            }
    return world


def canonical_iptables(cmd):
    """Turn an iptables command into the line `iptables -S` actually prints.

    `iptables -A INPUT -p tcp -s 10.20.0.60 --dport 22 -j ACCEPT` becomes
    `-A INPUT -s 10.20.0.60/32 -p tcp -m tcp --dport 22 -j ACCEPT`.
    NAT commands are reported by `iptables -t nat -S`, not `iptables -S`.
    """
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        tokens = cmd.split()
    if not tokens or tokens[0] != "iptables":
        return "filter", None, None
    rest = tokens[1:]
    table = "filter"
    if rest and rest[0] == "-t" and len(rest) > 1:
        table = rest[1]
        rest = rest[2:]
    if not rest:
        return table, None, None
    if rest[0] == "-P" and len(rest) >= 3:
        return table, None, (rest[1], rest[2])
    if rest[0] not in ("-A", "-I") or len(rest) < 2:
        return table, None, None
    chain = rest[1]
    opts = rest[2:]
    src = dst = inn = out = proto = dport = jump = None
    extra = []
    i = 0
    while i < len(opts):
        tok = opts[i]
        nxt = opts[i + 1] if i + 1 < len(opts) else ""
        if tok in ("-s", "-d", "-i", "-o", "-p", "-j", "--dport", "-m") and nxt:
            if tok == "-s":
                src = nxt if "/" in nxt else nxt + "/32"
            elif tok == "-d":
                dst = nxt if "/" in nxt else nxt + "/32"
            elif tok == "-i":
                inn = nxt
            elif tok == "-o":
                out = nxt
            elif tok == "-p":
                proto = nxt
            elif tok == "-j":
                jump = nxt
            elif tok == "--dport":
                dport = nxt
            i += 2
            continue
        if tok.startswith("--dport="):
            dport = tok.split("=", 1)[1]
        elif tok not in ("-m",):
            extra.append(tok)
        i += 1
    parts = ["-A", chain]
    if src:
        parts += ["-s", src]
    if dst:
        parts += ["-d", dst]
    if inn:
        parts += ["-i", inn]
    if out:
        parts += ["-o", out]
    if proto:
        parts += ["-p", proto]
        if proto == "tcp" and dport:
            parts += ["-m", "tcp"]
    if dport:
        parts += ["--dport", dport]
    parts += extra
    if jump:
        parts += ["-j", jump]
    return table, " ".join(parts), None


class _World:
    def __init__(self):
        self.files = {}
        self.routes = []
        self.rules = {"filter": [], "nat": []}
        self.iptables = []
        self.policy = {}
        self.forward = "0"
        self.crontab = []
        self.links = []

    def apply(self, cmd):
        raw = str(cmd).strip()
        if raw.startswith("sudo "):
            raw = raw[5:].strip()
        if not raw or raw.startswith("#"):
            return
        if raw.startswith("mkdir "):
            return
        m = re.match(r"^printf '%s\\n' '(.*)' > (\S+)$", raw)
        if m:
            self.files[m.group(2)] = {"mode": 0o644, "owner": "root", "group": "root", "content": m.group(1).replace("\\n", "\n") + "\n"}
            return
        m = re.match(r"^echo (\S+) > (\S+)$", raw)
        if m:
            self.files[m.group(2)] = {"mode": 0o644, "owner": "root", "content": m.group(1) + "\n"}
            return
        m = re.match(r"^chmod (\S+) (\S+)$", raw)
        if m:
            node = self.files.setdefault(m.group(2), {"mode": 0o644, "owner": "root", "content": ""})
            from labs_linux import _chmod
            new = _chmod(node["mode"], m.group(1))
            if new is None:
                raise ValueError(f"bad mode in {raw}")
            node["mode"] = new
            return
        m = re.match(r"^chown (\S+) (\S+)$", raw)
        if m:
            node = self.files.setdefault(m.group(2), {"mode": 0o644, "owner": "root", "group": "root", "content": ""})
            who = m.group(1)
            user, sep, group = who.partition(":")
            if user:
                node["owner"] = user
            if sep and group:
                node["group"] = group
            return
        m = re.match(r"^rm -f (\S+)$", raw)
        if m:
            self.files.pop(m.group(1), None)
            return
        m = re.match(r"^ip addr add (\S+)/(\d+) dev \S+$", raw)
        if m:
            self.links.append(ipaddress.ip_network(f"{m.group(1)}/{m.group(2)}", strict=False))
            return
        m = re.match(r"^ip route add default via (\S+)$", raw)
        if m:
            hop = ipaddress.ip_address(m.group(1))
            if any(hop in net for net in self.links):
                self.routes.append(m.group(1))
            return
        m = re.match(r"^sysctl -w net\.ipv4\.ip_forward=(\d+)$", raw)
        if m:
            self.forward = m.group(1)
            return
        if raw.startswith("iptables "):
            table, line, policy = canonical_iptables(raw)
            if line:
                self.rules.setdefault(table, []).append(line)
                self.iptables.append(line)
            if policy:
                self.policy[policy[0]] = policy[1]
                self.rules.setdefault(table, []).append(f"-P {policy[0]} {policy[1]}")
            return
        m = re.match(r"^crontab (\S+)$", raw)
        if m:
            text = self.files.get(m.group(1), {}).get("content", "")
            self.crontab = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
            return
        raise ValueError(f"stage harness cannot apply {raw}")


def _model_ok(world, checks):
    for check in checks:
        kind = check["kind"]
        if kind == "mode":
            node = world.files.get(check["path"])
            if not node or f"{node['mode']:04o}"[-3:] != str(check["mode"])[-3:]:
                return False
            if check.get("owner") and node.get("owner") != check["owner"]:
                return False
            if check.get("group") and node.get("group") != check["group"]:
                return False
        elif kind == "absent":
            if check["path"] in world.files:
                return False
        elif kind == "contains":
            node = world.files.get(check["path"])
            if not node or check["text"] not in node.get("content", ""):
                return False
        elif kind == "not_contains":
            node = world.files.get(check["path"])
            if node and check["text"] in node.get("content", ""):
                return False
        elif kind == "route":
            if check["hop"] not in world.routes:
                return False
        elif kind == "forward":
            if world.forward != str(check["value"]):
                return False
        elif kind == "iptables":
            table = check.get("table") or "filter"
            blob = "\n".join(world.rules.get(table, []))
            if check["fragment"] not in blob:
                return False
        elif kind == "policy":
            if world.policy.get(check["chain"]) != check["policy"]:
                return False
        elif kind == "crontab":
            if check["line"] not in world.crontab:
                return False
        elif kind == "sha256":
            node = world.files.get(check["path"])
            if not node:
                return False
            digest = hashlib.sha256(node.get("content", "").encode()).hexdigest()
            if digest != check["digest"]:
                return False
        else:
            raise ValueError(kind)
    return True


def _letters(mode):
    n = int(str(mode), 8)
    letters = "-"
    for shift in (6, 3, 0):
        bit = (n >> shift) & 7
        letters += ("r" if bit & 4 else "-") + ("w" if bit & 2 else "-") + ("x" if bit & 1 else "-")
    return letters


def _shell(checks):
    parts = []
    for check in checks:
        kind = check["kind"]
        path = check.get("path", "")
        if kind == "mode":
            letters = _letters(check["mode"])
            parts.append(f"ls -l '{path}' | grep -q '^{letters} '")
            if check.get("owner"):
                parts.append(f"ls -l '{path}' | awk '{{print $3}}' | grep -qx '{check['owner']}'")
            if check.get("group"):
                parts.append(f"ls -l '{path}' | awk '{{print $4}}' | grep -qx '{check['group']}'")
        elif kind == "absent":
            parts.append(f"[ ! -e '{path}' ]")
        elif kind == "contains":
            parts.append(f"grep -F -q -- '{check['text']}' '{path}'")
        elif kind == "not_contains":
            parts.append(f"! grep -F -q -- '{check['text']}' '{path}'")
        elif kind == "route":
            parts.append(f"ip route | grep -q '^default via {check['hop']}'")
        elif kind == "forward":
            parts.append(f"[ \"$(cat /proc/sys/net/ipv4/ip_forward)\" = '{check['value']}' ]")
        elif kind == "iptables":
            table = check.get("table") or "filter"
            tool = "iptables -t nat -S" if table == "nat" else "iptables -S"
            parts.append(f"{tool} | grep -F -q -- '{check['fragment']}'")
        elif kind == "policy":
            parts.append(f"iptables -S | grep -q '^-P {check['chain']} {check['policy']}'")
        elif kind == "crontab":
            parts.append(f"crontab -l | grep -qxF -- '{check['line']}'")
        elif kind == "sha256":
            parts.append(f"sha256sum '{path}' | grep -q '^{check['digest']} '")
        else:
            raise ValueError(kind)
    return " && ".join(parts)


_FILE_KINDS = {"mode", "absent", "contains", "not_contains", "sha256"}


def _run_stage(plant, fix, checks):
    kinds = {c["kind"] for c in checks}
    if kinds <= _FILE_KINDS and not any(c.get("owner") or c.get("group") for c in checks):
        return _run_real(plant, fix, checks)
    world = _World()
    for cmd in list(plant) + list(fix):
        world.apply(cmd)
    return _model_ok(world, checks)


def _rewrite(text, tmp):
    for src, dst in (
        ("/root", tmp + "/root"),
        ("/home/trainee", tmp + "/home/trainee"),
        ("/etc", tmp + "/etc"),
        ("/srv", tmp + "/srv"),
        ("/var", tmp + "/var"),
        ("/opt", tmp + "/opt"),
        ("/usr", tmp + "/usr"),
    ):
        text = text.replace(src, dst)
    return text


def plant_state(lab, state, facts):
    row = spec(lab)
    fn = (row or {}).get("plant_state")
    if fn and facts:
        fn(state, facts)


def stage_events(lab, facts, stage):
    """GUI actions that grade a desktop stage. None when the stage is not click-graded."""
    row = spec(lab)
    evs = (row or {}).get("events") or {}
    fn = evs.get(stage) if isinstance(evs, dict) else None
    if not fn:
        return None
    return list(fn(facts))


def after_guided(lab, state):
    """Re-plant stage 2 and 3 faults once the walkthrough has just finished."""
    row = spec(lab)
    fn = (row or {}).get("after_guided")
    px = (state or {}).setdefault("px", {})
    if not fn or px.get("spoiled"):
        return
    px["spoiled"] = True
    fn(state, px.get("facts") or {})


def desk_value(lab, facts, stage):
    row = spec(lab)
    if not row or not row.get("ok"):
        return None
    if stage_events(lab, facts, stage) is not None:
        return None
    cmds = row["stages"][stage]["fix"](facts)
    if not cmds:
        return None
    return cmds[0]


def stage_state_ok(lab, stage, state, facts):
    row = spec(lab)
    fn = (row or {}).get("ok")
    if not fn:
        return None
    return bool(fn(state, facts, stage))


import lab_skill_linux  # noqa: E402,F401  — registers SPECS
import lab_skill_windows  # noqa: E402,F401
import lab_skill_ios  # noqa: E402,F401
import lab_skill_choice  # noqa: E402,F401


def _run_real(plant, fix, checks):
    shell = _shell(checks)
    with tempfile.TemporaryDirectory(prefix="novak-skill-") as tmp:
        for folder in ("root", "home/trainee", "etc", "srv", "var", "opt", "usr"):
            os.makedirs(tmp + "/" + folder, exist_ok=True)
        env_cmds = []
        for cmd in list(plant) + list(fix):
            if cmd.startswith("sudo "):
                cmd = cmd[5:]
            if not cmd.startswith(("mkdir ", "printf ", "echo ", "chmod ", "rm ")):
                raise ValueError(f"real fixture refused {cmd}")
            env_cmds.append(cmd)
        for cmd in env_cmds:
            subprocess.run(["bash", "-c", _rewrite(cmd, tmp)], cwd=tmp, check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        proc = subprocess.run(["bash", "-c", _rewrite(shell, tmp)], cwd=tmp, check=False,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return proc.returncode == 0
