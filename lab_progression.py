"""Three-stage lab progression.

Stage 1 teaches the lab's real commands. Stages 2 and 3 are a different task and a
ticket. Their prompts name outcomes. The values (names, addresses, VLAN ids, file
tokens) are chosen from the attempt seed and have to be read from the desk note or
from a file inside the machine. Checks look at the resulting configuration, files,
or recorded decision — not at whether the student retyped the walkthrough.
"""
from __future__ import annotations

import hashlib
import html
import ipaddress
import random
import re
from copy import deepcopy

STAGE_ORDER = ("guided", "assisted", "ticket")
STAGE_MARKS = tuple(f"stage:{s}" for s in STAGE_ORDER)

_PEOPLE = (
    "Priya", "Andre", "Helena", "Marcus", "June", "Ravi", "Elena", "Chris", "Noah", "Amina",
    "Luis", "Greta", "Owen", "Nadia", "Felix", "Hana", "Jules", "Imani", "Peter", "Sofia",
    "Diego", "Mei", "Arthur", "Leila", "Hugo", "Rosa", "Ivan", "Chloe", "Samir", "Bea",
)
_PLACES = (
    "the east clinic", "the loading dock", "the bursar's office", "the library desk",
    "the second-floor lab", "the night-shift bench", "the badge office", "the print room",
    "the admissions counter", "the server closet", "the help desk window", "the science wing",
    "the residence hall office", "the warehouse cage", "the lecture-hall booth",
)


def needs_stages(lab):
    return bool(lab) and lab.get("kind") not in ("classroom",) and bool(lab.get("objectives"))


def family(lab):
    kind = lab.get("kind") or ""
    lid = lab.get("id") or ""
    if kind == "linuxgui":
        return "linuxgui"
    if kind == "vm":
        return "vm"
    if kind == "linux":
        return "linux"
    if kind == "activity":
        return "number" if lid == "net-subnet" else "choice"
    if kind in ("ticket",):
        return "choice"
    if kind == "win11gui":
        return "desk"
    if kind == "windows":
        return "win"
    if kind == "switch":
        if "vlan" in lid:
            return "sw_vlan"
        if "trunk" in lid:
            return "sw_trunk"
        if "port-security" in lid:
            return "sw_portsec"
        if "banner" in lid:
            return "sw_banner"
        if "describe" in lid:
            return "sw_desc"
        if "hostname" in lid:
            return "sw_host"
        return "sw_host"
    if kind == "router":
        if "default-route" in lid:
            return "rtr_route"
        if "acl" in lid:
            return "rtr_acl"
        if "describe" in lid:
            return "rtr_desc"
        if "hostname" in lid:
            return "rtr_host"
        return "rtr_addr"
    return "choice"


def _rng(lab, seed):
    lid = lab.get("id") if isinstance(lab, dict) else str(lab)
    return random.Random(f"{lid}:{int(seed or 1)}")


def _mode_letters(mode):
    bits = int(str(mode), 8)
    out = "-"
    for i in range(9):
        out += "rwxrwxrwx"[i] if bits & (0o400 >> i) else "-"
    return out


def _choice_bank(lab):
    lid = lab.get("id") or ""
    if lid in ("sec-phish", "sec-awareness"):
        return (
            ("The message asks for a password and the sender domain is one letter off the school's domain.", "report"),
            ("The message is a meeting reminder from the school's own calendar system, and the link stays on the school domain.", "allow"),
            ("A display name matches the finance director, but the address is a free webmail account and the file is an unexpected invoice.", "report"),
            ("Facilities mailed a planned weekend outage from the facilities mailbox to the whole building.", "note"),
        )
    if lid in ("sec-malware", "sec-ir", "sec-indicators"):
        return (
            ("A pop-up claims the PC is infected and demands a phone call. The user has not clicked it.", "isolate"),
            ("The same pop-up appeared yesterday, the user closed it, and nothing else changed.", "preserve"),
            ("Files on a shared drive were encrypted overnight and a ransom note is in the folder.", "isolate"),
            ("A scan finished clean after a known unwanted toolbar was removed and the user can work.", "document"),
        )
    if "backup" in lid or lid == "ops-backup":
        return (
            ("One copy of the finance share sits on the same server that holds the original.", "reject"),
            ("Copies exist on a second disk in the building and on a monthly tape stored off site, and a file was restored last week.", "accept"),
            ("The only backup is a USB drive in the same drawer as the laptop.", "reject"),
            ("Three copies exist, two kinds of media, one off site, and last month's restore test opened the file.", "accept"),
        )
    if "wifi" in lid or "wireless" in lid:
        return (
            ("The lobby network uses WEP and WPS is enabled.", "harden"),
            ("The staff network uses WPA3, WPS is off, and the passphrase is long.", "leave"),
            ("A guest network has no passphrase at all.", "harden"),
            ("The only change requested is a new SSID on an already WPA3 network with WPS off.", "leave"),
        )
    if lid == "hw-board":
        return (
            ("The board is the full size used in a tower, with the standard rear I/O cluster and four memory slots.", "atx"),
            ("The board is square and small enough for a compact case, smaller than a full tower board but not the tiny square.", "microatx"),
            ("The board is the small square form used in the tiniest cases.", "mini-itx"),
            ("The socket is the Intel desktop socket used with this generation of chips, and the board is full tower size.", "atx"),
        )
    if lid == "ticket-intake":
        return (
            ("One person wants a new mouse. Nothing is broken.", "request 1 no"),
            ("Half the badge readers on the floor stopped this morning, and one reader is warm to the touch.", "incident many yes"),
            ("A single user forgot a password and can wait at the desk.", "request 1 no"),
            ("The file server is unreachable for every desk in the wing.", "incident many yes"),
        )
    return (
            ("People are stopped and the fault started this morning.", "act-now"),
            ("One person can work around it, and the change can wait for the window.", "schedule"),
            ("The report matches a change that was announced yesterday.", "confirm-change"),
            ("Nothing is down. The caller wants a new convenience.", "request"),
        )


def facts(lab, seed):
    """Per-attempt values. Two seeds differ. Guided literals are not reused."""
    rng = _rng(lab, seed)
    seed = int(seed or 1)
    octet = 21 + (seed % 180)
    if octet in (20, 30):
        octet += 3
    third = rng.randint(1, 250)
    host = rng.randint(20, 200)
    fam = family(lab)
    who = _PEOPLE[seed % len(_PEOPLE)]
    where = _PLACES[(seed // 3) % len(_PLACES)]
    token_a = rng.choice(("kestrel", "marble", "harbor", "cinder", "plover", "linnet")) + str(1000 + (seed * 17) % 8000)
    token_b = rng.choice(("aspen", "quartz", "badger", "willow", "cobalt", "yarrow")) + str(2000 + (seed * 29) % 7000)
    if token_b == token_a:
        token_b += "x"
    vlan_a = 30 + (seed % 40)
    vlan_b = vlan_a + 11
    if vlan_a == 20:
        vlan_a = 33
    if vlan_b in (20, vlan_a):
        vlan_b = vlan_a + 7
    dns = f"10.{octet}.{third}.10"
    hop = f"10.{octet}.{third}.2"
    addr = f"10.{octet}.{third}.{host}"
    prefix = rng.choice((26, 27, 28))
    net = ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
    bank = _choice_bank(lab)
    i = seed % len(bank)
    j = (seed + 1) % len(bank)
    if j == i:
        j = (i + 1) % len(bank)
    case_a, ans_a = bank[i]
    case_b, ans_b = bank[j]
    guided_host = (lab.get("initial_state") or {}).get("hostname") or "NOVAK-W11-07"
    ticket_host = f"DESK-{octet}{seed % 10}"
    if ticket_host == guided_host:
        ticket_host = "DESK-ALT"
    note_n = 1000 + (seed * 13) % 8000
    base = "/root" if fam == "vm" else "/home/trainee"
    f = {
        "who": who,
        "where": where,
        "family": fam,
        "guided_dns": "10.20.30.10",
        "guided_host": guided_host,
        "guided_hop": "10.20.0.2",
        "guided_vlan": 20,
        "assisted_dns": dns,
        "ticket_host": ticket_host,
        "assisted_vlan": vlan_a,
        "ticket_vlan": vlan_b,
        "assisted_port": "FastEthernet0/3",
        "assisted_name": f"LAB{vlan_a}",
        "assisted_vlans": [vlan_a, vlan_b],
        "assisted_ip": f"10.{octet}.{third}.1",
        "assisted_mask": "255.255.255.0",
        "assisted_hop": hop,
        "assisted_host": addr,
        "assisted_desc": f"Wing-{octet}",
        "ticket_desc": f"Night-{third}",
        "assisted_token": token_a,
        "ticket_token": token_b,
        "assisted_mode": "640",
        "ticket_mode": "600",
        "note_path": f"{base}/note-{note_n}.txt",
        "assisted_path": f"{base}/proof-{note_n}.txt",
        "ticket_path": f"{base}/incident-{note_n}.txt",
        "assisted_case": case_a,
        "ticket_case": case_b,
        "assisted_answer": ans_a if fam != "number" else str(net.network_address),
        "ticket_answer": ans_b if fam != "number" else str(ipaddress.ip_network(f"172.16.{seed % 16}.{host}/{prefix}", strict=False).network_address),
        "number_ip": addr,
        "number_prefix": prefix,
        "ticket_ip": f"172.16.{seed % 16}.{host}",
        "ticket_prefix": prefix,
    }
    import lab_skills as SK
    SK.enrich(lab, f, seed)
    f["note_assisted"] = _note(f, "assisted", lab)
    f["note_ticket"] = _note(f, "ticket", lab)
    f["note_body"] = "PRACTICE\n" + f["note_assisted"] + "\n\nINCIDENT\n" + f["note_ticket"] + "\n"
    return f


def _note(f, stage, lab=None):
    if lab is not None:
        import lab_skills as SK
        custom = SK.note(lab, stage, f)
        if custom:
            return custom
    fam = f["family"]
    if stage == "assisted":
        if fam in ("win", "desk"):
            return f"DNS server to use on Ethernet: {f['assisted_dns']}\nLeave the IPv4 address on automatic.\nDo not keep the previous DNS servers."
        if fam == "sw_vlan":
            return f"Create VLAN {f['assisted_vlan']} named {f['assisted_name']}.\nPut {f['assisted_port']} into that VLAN as an access port."
        if fam == "sw_trunk":
            return "The uplink may carry only these VLANs: " + ",".join(str(v) for v in f["assisted_vlans"]) + "."
        if fam == "sw_portsec":
            return f"Turn port security on for {f['assisted_port']}."
        if fam == "sw_banner":
            return f"The login banner must include this exact token: {f['assisted_token']}"
        if fam == "sw_desc":
            return f"Set the description on FastEthernet0/2 to {f['assisted_desc']}"
        if fam == "sw_host":
            return f"Device name: {f['ticket_host']}"
        if fam == "rtr_addr":
            return f"Address GigabitEthernet0/1 with {f['assisted_ip']} mask {f['assisted_mask']} and bring it up."
        if fam == "rtr_route":
            return f"Default route next hop: {f['assisted_hop']}"
        if fam == "rtr_acl":
            return f"A standard access list must deny this single host: {f['assisted_host']}"
        if fam == "rtr_desc":
            return f"Set the description on GigabitEthernet0/0 to {f['assisted_desc']}"
        if fam == "rtr_host":
            return f"Device name: {f['ticket_host']}"
        if fam in ("linux", "vm"):
            mode = f["assisted_mode"]
            return (
                f"Write this single line into the proof file:\n{f['assisted_token']}\n"
                f"Proof file: {f['assisted_path']}\nMode: {mode} ({_mode_letters(mode)})"
            )
        if fam == "number":
            return f"Address: {f['number_ip']}\nPrefix length: {f['number_prefix']}\nSubmit the network address only."
        if fam == "linuxgui":
            return "Use the practice ticket already on this desktop. Every value in it has to be applied. The guided numbers will not match."
        return f["assisted_case"] + "\nSubmit the outcome as a single line."
    if fam in ("win", "desk"):
        return f"Computer name to set: {f['ticket_host']}"
    if fam in ("sw_vlan", "sw_trunk", "sw_portsec", "sw_banner", "sw_desc", "rtr_addr", "rtr_route", "rtr_acl", "rtr_desc"):
        return f"Device name: {f['ticket_host']}"
    if fam in ("sw_host", "rtr_host"):
        port = "FastEthernet0/2" if fam == "sw_host" else "GigabitEthernet0/0"
        return f"Set the description on {port} to {f['ticket_desc']}"
    if fam in ("linux", "vm"):
        mode = f["ticket_mode"]
        return (
            f"Write this single line into the incident file:\n{f['ticket_token']}\n"
            f"Incident file: {f['ticket_path']}\nMode: {mode} ({_mode_letters(mode)})"
        )
    if fam == "number":
        return f"Address: {f['ticket_ip']}\nPrefix length: {f['ticket_prefix']}\nSubmit the network address only."
    if fam == "linuxgui":
        return "Apply the desktop file whose name starts with INC-. The live system has to match it."
    return f["ticket_case"] + "\nSubmit the outcome as a single line."


def attach(lab, state):
    if not needs_stages(lab) or state is None:
        return state
    if "px" not in state or not (state.get("px") or {}).get("facts"):
        state["px"] = {"facts": facts(lab, state.get("seed") or 1), "answers": {}}
    fam = family(lab)
    if fam == "linux" and isinstance(state.get("fs"), dict):
        f = state["px"]["facts"]
        state["fs"][f["note_path"]] = {"t": "f", "mode": 0o644, "owner": "trainee", "group": "trainee", "c": f["note_body"]}
    import lab_skills as SK
    facts_now = (state.get("px") or {}).get("facts") or {}
    SK.plant_fs(lab, state, facts_now)
    SK.plant_state(lab, state, facts_now)
    return state


def prepare_vm(lab, state):
    """Copy of lab['vm'] with this attempt's note file appended to setup. Linux GUI snapshots are left alone."""
    if lab.get("kind") != "vm":
        return lab.get("vm")
    import labs_vm as VM
    if lab.get("session_vars"):
        vm = VM.vm_for_session(lab, state.get("seed"))
    else:
        vm = deepcopy(lab.get("vm") or {})
    f = ((state or {}).get("px") or {}).get("facts") or facts(lab, (state or {}).get("seed") or 1)
    body = f["note_body"]
    path = f["note_path"]
    # printf one argument per line, single-quoted
    args = " ".join("'" + line.replace("'", "'\\''") + "'" for line in body.split("\n"))
    snippet = f"mkdir -p /root\nprintf '%s\n' {args} > '{path}'\n"
    import lab_skills as SK
    snippet += SK.plant_shell(lab, f)
    setup = vm.setdefault("setup", {})
    for machine in vm.get("machines") or []:
        name = machine.get("name")
        if name:
            setup[name] = (setup.get(name) or "") + "\n" + snippet
    return vm


def probe_shells(state, lab):
    if not lab or lab.get("kind") != "vm":
        return []
    f = ((state or {}).get("px") or {}).get("facts") or {}
    if not f:
        return []
    import lab_skills as SK
    custom = SK.probe_pairs(lab, f)
    if custom is not None:
        return custom
    out = []
    for key, path, token, mode in (
        ("px_assisted", f["assisted_path"], f["assisted_token"], f["assisted_mode"]),
        ("px_ticket", f["ticket_path"], f["ticket_token"], f["ticket_mode"]),
    ):
        letters = _mode_letters(mode)
        sh = f"grep -qx '{token}' '{path}' && ls -l '{path}' | grep -q '^{letters} '"
        out.append((key, sh))
    return out


def solved_px_lines(state, lab):
    """The guest probe is the real check. Tests must not invent a pass here."""
    return []


def vm_file_commands(lab, state):
    """Shell lines that create the stage 2 and 3 proof files. Safe to run on a temp directory."""
    if family(lab) != "vm":
        return []
    f = ((state or {}).get("px") or {}).get("facts") or facts(lab, (state or {}).get("seed") or 1)
    import lab_skills as SK
    if SK.has_spec(lab):
        return list(SK.fix_commands(lab, f, "assisted") or []) + list(SK.fix_commands(lab, f, "ticket") or [])
    out = []
    for path, token, mode in (
        (f["assisted_path"], f["assisted_token"], f["assisted_mode"]),
        (f["ticket_path"], f["ticket_token"], f["ticket_mode"]),
    ):
        parent = path.rsplit("/", 1)[0]
        out.append(f"mkdir -p {parent}")
        out.append("printf '%s\\n' '" + str(token).replace("'", "'\\''") + f"' > {path}")
        out.append(f"chmod {mode} {path}")
    return out


def run_px_grep(lab, state, commands):
    """Run the stage file checks with the system grep against a temp directory.

    Returns lines ``c_px_assisted 1`` or ``0`` (and the ticket line). A missing file is 0.
    Only mkdir, printf, and chmod from vm_file_commands are executed.
    """
    import os
    import subprocess
    import tempfile
    shells = probe_shells(state, lab)
    if not shells:
        return []
    allowed = ("mkdir -p ", "printf ", "chmod ")
    for cmd in commands or []:
        if not str(cmd).startswith(allowed):
            raise ValueError(f"refusing to run {cmd!r} on the host")
    with tempfile.TemporaryDirectory(prefix="novak-px-") as tmp:
        def rewrite(text):
            return (str(text).replace("/home/trainee", tmp + "/home/trainee")
                    .replace("/root", tmp + "/root"))
        os.makedirs(tmp + "/root", exist_ok=True)
        os.makedirs(tmp + "/home/trainee", exist_ok=True)
        for cmd in commands or []:
            subprocess.run(["bash", "-c", rewrite(cmd)], cwd=tmp, check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        lines = []
        for key, sh in shells:
            if "grep -qx" not in sh or "ls -l" not in sh:
                raise ValueError("stage file check is not the expected grep")
            proc = subprocess.run(["bash", "-c", rewrite(sh)], cwd=tmp, check=False,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            lines.append(f"c_{key} {1 if proc.returncode == 0 else 0}")
        return lines


def probes_with_real_px(lab, state, probes):
    """Solved objective probes plus the real grep result for the stage files."""
    if not lab or lab.get("kind") != "vm":
        return probes
    import lab_skills as SK
    facts = ((state or {}).get("px") or {}).get("facts") or {}
    if SK.has_spec(lab):
        extra = SK.evaluate(lab, facts)
    else:
        extra = run_px_grep(lab, state, vm_file_commands(lab, state))
    if isinstance(probes, str):
        return splice_px_lines(probes, extra)
    out = dict(probes)
    first = next(iter(out))
    out[first] = splice_px_lines(out[first], extra)
    return out


def splice_px_lines(probe_text, extra_lines):
    """Insert real grep results into one machine's probe, before the end marker."""
    if not extra_lines:
        return probe_text
    block = "\n".join(extra_lines)
    if "\nend\n" in probe_text:
        return probe_text.replace("\nend\n", "\n" + block + "\nend\n", 1)
    return probe_text.rstrip() + "\n" + block + "\nend\n"


# ---------------------------------------------------------------- checks


def _guided_ids(lab):
    ids = [o["id"] for o in lab.get("objectives") or []]
    if family(lab) == "linuxgui":
        s1 = [i for i in ids if i == "boot" or i.startswith("s1")]
        return s1 or ids
    return ids


def _later_ids(lab, stage):
    if family(lab) != "linuxgui":
        return []
    prefix = "s2" if stage == "assisted" else "s3"
    return [o["id"] for o in lab.get("objectives") or [] if o["id"].startswith(prefix)]


def _port(state, name):
    return ((state or {}).get("interfaces") or {}).get(name) or {}


def end_state_ok(lab, stage, state, done):
    """True when this stage's real end state is present. Stage 1 literals do not satisfy later stages."""
    if not needs_stages(lab):
        return False
    done = done or []
    f = ((state or {}).get("px") or {}).get("facts") or {}
    if not f:
        return False
    fam = family(lab)
    if stage == "guided":
        if fam == "linuxgui":
            return all(i in done for i in _guided_ids(lab))
        return set(_guided_ids(lab)) <= set(done)
    guided_done = "stage:guided" in done or (fam == "linuxgui" and all(i in done for i in _guided_ids(lab)))
    if not guided_done:
        return False
    if stage == "ticket" and "stage:assisted" not in done and not (fam == "linuxgui" and all(i in done for i in _later_ids(lab, "assisted"))):
        return False
    import lab_skills as SK
    custom = SK.stage_state_ok(lab, stage, state, f)
    if custom is not None:
        return custom
    if fam == "linuxgui":
        return all(i in done for i in _later_ids(lab, stage))
    if fam in ("win", "desk"):
        import lab_skills as SK
        custom = SK.stage_state_ok(lab, stage, state, f)
        if custom is not None:
            return custom
        if stage == "assisted":
            dns = [str(x) for x in (state.get("dns") or state.get("px_dns") or [])]
            return dns == [f["assisted_dns"]] and f["assisted_dns"] != f["guided_dns"]
        host = state.get("px_host") or state.get("hostname")
        return host == f["ticket_host"] and host != f["guided_host"]
    if lab.get("id") == "sw-vlan-multi" and stage == "assisted":
        a, b = f["assisted_vlans"]
        staff, guest, uplink = _port(state, "FastEthernet0/2"), _port(state, "FastEthernet0/3"), _port(state, "FastEthernet0/1")
        return (staff.get("mode") == "access" and staff.get("vlan") == a
                and guest.get("mode") == "access" and guest.get("vlan") == b
                and uplink.get("trunk") and list(uplink.get("allowed") or []) == sorted((a, b))
                and a not in (10, 20) and b not in (10, 20))
    if fam == "sw_vlan" and stage == "assisted":
        iface = _port(state, f["assisted_port"])
        return iface.get("vlan") == f["assisted_vlan"] and iface.get("mode") == "access" and f["assisted_vlan"] != f["guided_vlan"]
    if fam == "sw_trunk" and stage == "assisted":
        iface = _port(state, "FastEthernet0/1")
        return iface.get("trunk") and list(iface.get("allowed") or []) == list(f["assisted_vlans"])
    if fam == "sw_portsec" and stage == "assisted":
        return bool(_port(state, f["assisted_port"]).get("portsec")) and f["assisted_port"] != "FastEthernet0/2"
    if fam == "sw_banner" and stage == "assisted":
        return f["assisted_token"] in str(state.get("banner") or "") and "WALKTHROUGH" not in str(state.get("banner") or "")
    if fam == "sw_desc" and stage == "assisted":
        return _port(state, "FastEthernet0/2").get("desc") == f["assisted_desc"]
    if fam == "sw_host" and stage == "assisted":
        return state.get("hostname") == f["ticket_host"] and state.get("hostname") != f["guided_host"]
    if fam == "rtr_addr" and stage == "assisted":
        iface = _port(state, "GigabitEthernet0/1")
        return iface.get("ip") == f["assisted_ip"] and f["assisted_ip"] not in ("10.20.0.1", "10.30.0.1")
    if fam == "rtr_route" and stage == "assisted":
        blob = " ".join(state.get("static") or [])
        return f["assisted_hop"] in blob and f["assisted_hop"] != f["guided_hop"]
    if fam == "rtr_acl" and stage == "assisted":
        blob = " ".join(str(e) for rows in (state.get("acls") or {}).values() for e in rows)
        return f["assisted_host"] in blob
    if fam == "rtr_desc" and stage == "assisted":
        return _port(state, "GigabitEthernet0/0").get("desc") == f["assisted_desc"]
    if fam == "rtr_host" and stage == "assisted":
        return state.get("hostname") == f["ticket_host"]
    if fam in ("sw_vlan", "sw_trunk", "sw_portsec", "sw_banner", "sw_desc", "rtr_addr", "rtr_route", "rtr_acl", "rtr_desc") and stage == "ticket":
        return state.get("hostname") == f["ticket_host"] and state.get("hostname") != f["guided_host"]
    if fam == "sw_host" and stage == "ticket":
        return _port(state, "FastEthernet0/2").get("desc") == f["ticket_desc"]
    if fam == "rtr_host" and stage == "ticket":
        return _port(state, "GigabitEthernet0/0").get("desc") == f["ticket_desc"]
    if fam in ("linux", "vm") and stage == "assisted":
        if fam == "vm":
            return (state.get("probe_last") or {}).get("c_px_assisted") == "1"
        import lab_skills as SK
        if SK.has_spec(lab):
            return SK.fs_ok(lab, stage, state, f)
        return _file_ok(state.get("fs"), f["assisted_path"], f["assisted_token"], f["assisted_mode"])
    if fam in ("linux", "vm") and stage == "ticket":
        if fam == "vm":
            return (state.get("probe_last") or {}).get("c_px_ticket") == "1"
        import lab_skills as SK
        if SK.has_spec(lab):
            return SK.fs_ok(lab, stage, state, f)
        return _file_ok(state.get("fs"), f["ticket_path"], f["ticket_token"], f["ticket_mode"])
    if fam in ("choice", "number"):
        got = ((state.get("px") or {}).get("answers") or {}).get(stage)
        expect = f["assisted_answer"] if stage == "assisted" else f["ticket_answer"]
        return str(got or "").strip().lower() == str(expect).strip().lower() and str(expect).strip().lower() != str(f["guided_host"]).lower()
    return False


def _file_ok(fs, path, token, mode):
    node = (fs or {}).get(path)
    if not node or node.get("t") != "f":
        return False
    if str(node.get("c") or "").strip() != token:
        return False
    return (int(node.get("mode") or 0) & 0o777) == int(mode, 8)


def observe(lab, state, done):
    if not needs_stages(lab):
        return state, list(done or [])
    attach(lab, state)
    done = list(done or [])
    # Linux desktop: treat the s1 group as the walkthrough latch even before the mark is stored.
    if family(lab) == "linuxgui" and all(i in done for i in _guided_ids(lab)) and "stage:guided" not in done:
        done.append("stage:guided")
    for stage in STAGE_ORDER:
        mark = f"stage:{stage}"
        if mark in done:
            continue
        if end_state_ok(lab, stage, state, done):
            done.append(mark)
    return state, done


# ---------------------------------------------------------------- commands that reach the end state (solver only)


def _ios(lines):
    return ["end", *lines]


def followup_commands(lab, state, stage):
    f = ((state or {}).get("px") or {}).get("facts") or facts(lab, (state or {}).get("seed") or 1)
    import lab_skills as SK
    custom = SK.fix_commands(lab, f, stage)
    if custom is not None:
        return custom
    fam = family(lab)
    if stage == "assisted":
        if lab.get("id") == "sw-vlan-multi":
            a, b = f["assisted_vlans"]
            return _ios(["enable", "configure terminal",
                         f"vlan {a}", f"name STAFF{a}", f"vlan {b}", f"name GUEST{b}",
                         "interface fa0/2", "switchport mode access", f"switchport access vlan {a}",
                         "interface fa0/3", "switchport mode access", f"switchport access vlan {b}",
                         "interface fa0/1", "switchport mode trunk", f"switchport trunk allowed vlan {a},{b}",
                         "end"])
        if fam == "win":
            return [f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['assisted_dns']}"]
        if fam == "sw_vlan":
            return _ios(["enable", "configure terminal", f"vlan {f['assisted_vlan']}", f"name {f['assisted_name']}",
                         "interface fa0/3", "switchport mode access", f"switchport access vlan {f['assisted_vlan']}", "end"])
        if fam == "sw_trunk":
            vlans = ",".join(str(v) for v in f["assisted_vlans"])
            return _ios(["enable", "configure terminal", "interface fa0/1", "switchport mode trunk",
                         f"switchport trunk allowed vlan {vlans}", "end"])
        if fam == "sw_portsec":
            return _ios(["enable", "configure terminal", "interface fa0/3", "switchport mode access", "switchport port-security", "end"])
        if fam == "sw_banner":
            return _ios(["enable", "configure terminal", f"banner login # {f['assisted_token']} #", "end"])
        if fam == "sw_desc":
            return _ios(["enable", "configure terminal", "interface fa0/2", f"description {f['assisted_desc']}", "end"])
        if fam == "sw_host":
            return _ios(["enable", "configure terminal", f"hostname {f['ticket_host']}", "end"])
        if fam == "rtr_addr":
            return _ios(["enable", "configure terminal", "interface GigabitEthernet0/1",
                         f"ip address {f['assisted_ip']} {f['assisted_mask']}", "no shutdown", "end"])
        if fam == "rtr_route":
            return _ios(["enable", "configure terminal", f"ip route 0.0.0.0 0.0.0.0 {f['assisted_hop']}", "end"])
        if fam == "rtr_acl":
            return _ios(["enable", "configure terminal", f"access-list 15 deny host {f['assisted_host']}", "end"])
        if fam == "rtr_desc":
            return _ios(["enable", "configure terminal", "interface GigabitEthernet0/0", f"description {f['assisted_desc']}", "end"])
        if fam == "rtr_host":
            return _ios(["enable", "configure terminal", f"hostname {f['ticket_host']}", "end"])
        if fam == "linux":
            return [f"echo {f['assisted_token']} > {f['assisted_path']}", f"chmod {f['assisted_mode']} {f['assisted_path']}"]
        return []
    if fam == "win":
        return [f"Rename-Computer -NewName {f['ticket_host']}"]
    if fam in ("sw_vlan", "sw_trunk", "sw_portsec", "sw_banner", "sw_desc", "rtr_addr", "rtr_route", "rtr_acl", "rtr_desc"):
        return _ios(["enable", "configure terminal", f"hostname {f['ticket_host']}", "end"])
    if fam == "sw_host":
        return _ios(["enable", "configure terminal", "interface fa0/2", f"description {f['ticket_desc']}", "end"])
    if fam == "rtr_host":
        return _ios(["enable", "configure terminal", "interface GigabitEthernet0/0", f"description {f['ticket_desc']}", "end"])
    if fam == "linux":
        return [f"echo {f['ticket_token']} > {f['ticket_path']}", f"chmod {f['ticket_mode']} {f['ticket_path']}"]
    return []


def stage_actions(lab, state):
    """What the known-good path still has to do after the original solution. Not shown to students."""
    if not needs_stages(lab):
        return []
    attach(lab, state)
    actions = []
    done = []
    # caller passes current done via state['_done'] when it has it; otherwise commands are still safe to run
    fam = family(lab)
    f = state["px"]["facts"]
    for stage in ("assisted", "ticket"):
        if fam == "desk":
            import lab_skills as SK
            custom = SK.desk_value(lab, f, stage)
            ans = custom if custom is not None else (f["assisted_dns"] if stage == "assisted" else f["ticket_host"])
            actions.append({"type": "stage", "stage": stage, "answer": ans})
        elif fam in ("choice", "number"):
            ans = f["assisted_answer" if stage == "assisted" else "ticket_answer"]
            actions.append({"type": "stage", "stage": stage, "answer": ans})
        elif fam not in ("vm", "linuxgui"):
            for command in followup_commands(lab, state, stage):
                actions.append({"type": "cmd", "command": command})
    return actions


def submit_answer(lab, state, done, stage, answer):
    attach(lab, state)
    if stage not in STAGE_ORDER:
        return {"ok": False, "message": "Unknown stage."}, state, list(done or [])
    text = answer
    if isinstance(answer, dict):
        text = answer.get("answer") or answer.get("outcome") or ""
    state["px"].setdefault("answers", {})[stage] = str(text or "").strip()
    if family(lab) in ("desk", "win"):
        import lab_skill_windows as WW
        if not WW.apply_desk(lab, state, stage, str(text or "").strip()):
            if stage == "assisted":
                state["dns"] = [str(text or "").strip()]
                state["px_dns"] = state["dns"]
            else:
                state["px_host"] = str(text or "").strip()
                state["hostname"] = state["px_host"]
    state, done = observe(lab, state, done)
    mark = f"stage:{stage}"
    expect = state["px"]["facts"]["assisted_answer" if stage == "assisted" else "ticket_answer"]
    ok = mark in done
    if family(lab) == "desk":
        message = "Recorded. The check reads the settings now in effect." if ok else "That is not the value in this session's note."
    elif ok:
        message = "That matches the end state for this stage."
    else:
        message = "Not yet. Read the note for this stage and submit the outcome it requires."
        if str(text or "").strip().lower() == str(state["px"]["facts"].get("guided_host") or "").lower():
            message = "That is the walkthrough's value. This stage uses the note."
    return {"ok": ok, "message": message, "expect_hidden": True, "stage": stage}, state, done


def drive(lab, state, done, run_command):
    """Apply stage 2 and 3 through the same command path a student uses."""
    if not needs_stages(lab):
        return state, list(done or [])
    attach(lab, state)
    state, done = observe(lab, state, done)
    fam = family(lab)
    f = state["px"]["facts"]
    for stage in ("assisted", "ticket"):
        if f"stage:{stage}" in done:
            continue
        if fam == "desk":
            import lab_skills as SK
            custom = SK.desk_value(lab, f, stage) if hasattr(SK, "desk_value") else None
            ans = custom if custom is not None else (f["assisted_dns"] if stage == "assisted" else f["ticket_host"])
            _, state, done = submit_answer(lab, state, done, stage, ans)
            continue
        if fam in ("choice", "number"):
            ans = f["assisted_answer" if stage == "assisted" else "ticket_answer"]
            _, state, done = submit_answer(lab, state, done, stage, ans)
            continue
        if fam in ("vm", "linuxgui"):
            continue
        for command in followup_commands(lab, state, stage):
            _, state, done = run_command(lab["id"], state, done, command)
        state, done = observe(lab, state, done)
    return state, done


# ---------------------------------------------------------------- windows / note absorption


_NOTE_LINE = re.compile(r"^(show note|show desk-note|show incident|type desk-note\.txt|more flash:desk-note\.txt)$", re.I)


def absorb(lab, state, command):
    """Extra commands the base engines do not model: reading the note, setting DNS, renaming."""
    if not needs_stages(lab):
        return None
    attach(lab, state)
    raw = (command or "").strip()
    low = re.sub(r"\s+", " ", raw).lower()
    f = state["px"]["facts"]
    if _NOTE_LINE.match(low) or low in ("get-content note.txt", "gc note.txt"):
        if "incident" in low:
            return f["note_ticket"].splitlines()
        return f["note_body"].splitlines()
    m = re.search(r"-serveraddresses\s+(\S+)", raw, re.I)
    if m and "dns" in low:
        ip = m.group(1).strip("'\"")
        state["dns"] = [ip]
        state["px_dns"] = [ip]
        return [f"DNS servers for Ethernet: {ip}"]
    m = re.search(r"set dns\s+\S+\s+static\s+(\S+)", low)
    if m:
        state["dns"] = [m.group(1)]
        state["px_dns"] = state["dns"]
        return [f"DNS servers for Ethernet: {m.group(1)}"]
    m = re.search(r"-newname\s+(\S+)", raw, re.I)
    if m and "rename-computer" in low:
        name = m.group(1).strip("'\"")
        state["hostname"] = name
        state["px_host"] = name
        return [f"The computer will be named {name} after it restarts. In this simulation the name is already in effect."]
    import lab_skill_windows as WW
    if WW.win_effect(lab, state, raw):
        return ["The setting is updated."]
    return None


# ---------------------------------------------------------------- student-facing text

def guided_commands(lab):
    import interactive_labs as IL
    sol = lab.get("solution") or {}
    cmds = sol.get("commands")
    if cmds is None and lab.get("id") in getattr(IL, "VERIFY_SEQUENCES", {}):
        cmds = IL.VERIFY_SEQUENCES[lab["id"]][0]
    if cmds:
        return list(cmds)
    if lab.get("kind") == "linuxgui":
        return _GUI_STAGE1.get(lab.get("id"), [])
    if sol.get("vm_commands"):
        # Stage 1 shows the published solution. Later stages use different files.
        return list(sol.get("vm_commands") or [])
    return []


_GUI_STAGE1 = {
    "linux-gui-network": ["novak-net save guided 10.20.40.15 24 10.20.40.1 10.20.40.10"],
    "linux-gui-disks": ["novak-disk report /var/lib/novak/data.img", "novak-disk mount /var/lib/novak/data.img /srv/data defaults,nofail"],
    "linux-gui-firewall": ["novak-fw enable", "novak-fw allow 22", "novak-fw allow 443", "novak-fw ssh"],
    "linux-gui-users": ["novak-user unlock tech1", "novak-user sudo tech1", "chmod 750 /root/support/backup.sh"],
    "linux-gui-logs": ["novak-fw ban 198.51.100.77", "novak-log rotate"],
    "linux-gui-processes": ["novak-proc stop cpu-hog", "novak-proc swappiness 10"],
    "linux-gui-packages": ["novak-pkg update", "novak-pkg add darkhttpd"],
    "linux-gui-ssh": ["novak-ssh keygen", "novak-ssh permit-root no", "novak-ssh passwords no"],
}


def _esc(text):
    return html.escape(str(text or ""), quote=True)


def _flag_sentence(cmd, kind):
    low = cmd.strip().lower()
    parts = low.split()
    flags = [p for p in parts[1:] if p.startswith("/") or p.startswith("-")]
    if low.startswith("ipconfig /all") or low == "ipconfig /all":
        return "/all is the switch that asks for the long listing: DHCP yes or no, DNS servers, physical address, and adapter description. Without it, ipconfig prints a short address block and hides the servers you usually need."
    if "/release" in low:
        return "/release tells the DHCP client to give the lease back. The adapter loses its address until something asks for a new one. It is not a refresh by itself."
    if "/renew" in low:
        return "/renew asks the DHCP server for a lease. On Windows this flag belongs to ipconfig, and it should follow a release when you are cycling a stale lease."
    if "flushdns" in low:
        return "/flushdns clears the resolver cache on this PC. It does not fix a server that is down, and it does not change the DNS server list."
    if low.startswith("ping") and kind == "windows":
        return "Windows ping counts with -n (how many echoes) and waits with -w in milliseconds. -c is the Linux count flag and is not the Windows one. With no flag, Windows sends four echoes."
    if low.startswith("ping") and kind in ("linux", "vm", "linuxgui"):
        return "-c sets how many echoes to send and then stop. -W is the wait per reply, in seconds. A bare ping on Linux runs until you interrupt it."
    if low.startswith("netstat"):
        bits = []
        if "-a" in low:
            bits.append("-a lists every socket, including listeners, not only the ones with a peer.")
        if "-n" in low:
            bits.append("-n prints numbers for addresses and ports instead of waiting on name lookups.")
        return " ".join(bits) or "netstat without -n may pause on reverse lookups, which is a poor use of time during an outage."
    if low.startswith("ls") and ("-l" in low or low.startswith("ls -l")):
        return "-l is the long listing: type, permission bits, owner, group, size, and name. A bare ls hides the bits you need when the ticket is about access."
    if low.startswith("chmod"):
        return "chmod takes a mode then a path. Three octal digits are owner, group, and others. Each digit is read 4 plus write 2 plus execute 1. 640 is rw- for the owner, r-- for the group, and nothing for everyone else. Symbolic form such as o-r removes one class of bit."
    if low.startswith("grep"):
        extra = []
        if "-i" in parts:
            extra.append("-i ignores case.")
        if "-n" in parts:
            extra.append("-n prints the line number.")
        if "-q" in parts:
            extra.append("-q is quiet: exit status only, no matching line.")
        base = "grep takes a pattern and then a file. The pattern is text, and the match is case-sensitive unless you say otherwise."
        return base + (" " + " ".join(extra) if extra else "")
    if "switchport access vlan" in low:
        return "switchport access vlan chooses the VLAN id for a port that is already (or about to be) an access port. The number is the VLAN, not an interface. The port still needs switchport mode access; a trunk ignores this the way you hope it won't."
    if "switchport mode access" in low:
        return "switchport mode access makes the port an untagged member of one VLAN. It turns off trunking on that port."
    if "switchport mode trunk" in low:
        return "switchport mode trunk tags frames so one link can carry several VLANs. It is the uplink command, not the command for a PC port."
    if "switchport trunk allowed" in low:
        return "switchport trunk allowed vlan lists the VLAN ids the trunk may carry. Ids not in the list are pruned. The list is not a substitute for creating the VLANs."
    if "port-security" in low:
        return "switchport port-security, with no further keyword, enables sticky-style port security on that interface in this lab. It limits which addresses may appear on the port."
    if low.startswith("ip address"):
        return "ip address takes the interface address and then the subnet mask in dotted form. The mask is not a prefix length here. The interface still needs no shutdown before it passes traffic."
    if low.startswith("no shutdown") or low == "no shut":
        return "no shutdown removes the administrative down state. The word no negates shutdown. A description or an address does not bring the interface up by itself."
    if low.startswith("ip route"):
        return "ip route takes a destination, a mask, and a next hop. 0.0.0.0 with mask 0.0.0.0 is the default route: everything that does not match a longer prefix. The last address is the next router, not this router's own address."
    if low.startswith("access-list"):
        return "A number from 1 to 99 is a standard list and matches only the source. deny drops; permit allows. host followed by one address means that single host (the same as wildcard 0.0.0.0). Extended lists are 100 to 199 and need a protocol plus a destination."
    if low.startswith("encapsulation dot1q") or "dot1q" in low:
        return "encapsulation dot1Q sets the VLAN tag on a router subinterface. The number is the VLAN id. An address on that subinterface is refused until this line exists."
    if low.startswith("vlan "):
        return "vlan followed by a number from 1 to 4094 creates the VLAN or enters it. The number is not a port. name, on the next line, is the label people will read."
    if flags:
        shown = ", ".join(flags)
        return f"{shown} changes the tool's default. Read each one as a switch, not as part of the tool's name, and do not invent a second flag that this line does not contain."
    return ""


_FLAGLESS = (
    "There is no flag on this line; a flag would begin with a slash or a dash.",
    "This line is the tool by itself, so you get its default report.",
    "No option is being passed. Adding one would ask for something else.",
    "The default behavior is the whole request.",
    "You are not selecting a mode with a switch here.",
    "Leave it this short. Extra words are a different command.",
    "Nothing in the line is optional syntax.",
    "The tool name stands alone, which is enough for this step.",
    "Do not append a flag you remember from a different operating system.",
    "Defaults apply because the line does not override them.",
    "A bare command is intentional here.",
    "Skip the switches until a later step asks for one.",
)


_WHY = (
    "Write down what came back before you change anything, so a later test has something to differ from.",
    "This is evidence for the ticket, not a guess about what the screen ought to say.",
    "If the output is not what the ticket assumes, stop and say so. The next command will not repair a wrong diagnosis.",
    "The help desk keeps this line because it shows the fault domain, not because it looks busy.",
    "Matching the expected shape of the output tells you the tool ran. The values in it tell you what is true.",
    "Skip this and the later change has no before-picture.",
)


def explain_command(cmd, kind, index):
    """Four sentences: what it does, flags, expected shape, why it matters."""
    raw = cmd.strip()
    low = raw.lower()
    flag = _flag_sentence(raw, kind)
    if not flag:
        flag = _FLAGLESS[index % len(_FLAGLESS)]
    why = _WHY[index % len(_WHY)]
    if low in ("enable", "en"):
        does = "enable moves a Cisco-style console from user mode to privileged mode. The prompt gains a hash mark. Configuration commands are still refused until you enter configuration mode."
        expect = "Expect a prompt that ends in #. If you are told the command is invalid, you are already past user mode."
    elif low in ("configure terminal", "conf t", "configure"):
        does = "configure terminal enters global configuration mode from privileged mode. The prompt gains (config)."
        expect = "Expect (config) on the prompt. From user mode, with a > prompt, this is rejected."
    elif low in ("end", "exit"):
        does = "end leaves configuration mode and returns to privileged mode. exit climbs one level: interface mode to global configuration, then to privileged mode."
        expect = "Watch the prompt. end should land on a hash mark with no (config)."
    elif low == "hostname" or low.startswith("hostname "):
        does = "hostname prints the computer's name when it has no argument, and sets the device name when an argument follows on a router or switch in configuration mode."
        expect = "On Windows, expect one name and no other columns. On a switch or router, expect the prompt to adopt the new name."
    elif low.startswith("ipconfig"):
        does = "ipconfig reads this PC's IP configuration from the stack. It does not change anything unless the flag is /release, /renew, or /flushdns."
        expect = "Expect an adapter name, an IPv4 address, a mask, and a gateway. With /all, also expect DHCP state and DNS servers."
    elif low.startswith("ping"):
        does = "ping sends ICMP echo requests to the address or name you give it. A reply means that host answered. A name that fails while the address works points at name resolution, not at the cable."
        expect = "Expect either reply lines with a time, or a timeout / unreachable message. Do not treat a single failure as proof until you have seen the address test too."
    elif low.startswith("nslookup") or low.startswith("resolve-dnsname"):
        does = "This asks a DNS server to turn a name into an address. It does not test whether the address then answers."
        expect = "Expect an address on success, or a name-does-not-exist / timeout message when the server cannot answer."
    elif low.startswith("get-service") or low.startswith("get-service"):
        does = "Get-Service reads the state of a Windows service. It does not start or stop it unless you use a different cmdlet."
        expect = "Expect Status, Name, and a display name. Running means the service process is up."
    elif low.startswith("whoami"):
        does = "whoami prints the account the shell is using. It does not list other users."
        expect = "Expect one account name, often DOMAIN\\user on Windows."
    elif low.startswith("systeminfo") or low == "winver":
        does = "These read the installed operating system: edition, version, and build. They do not change the PC."
        expect = "Expect the edition and a build number. A virtual machine says so in the model line."
    elif "switchport" in low or low.startswith("vlan") or low.startswith("interface") or low.startswith("ip ") or low.startswith("description") or low.startswith("banner") or low.startswith("access-list") or low.startswith("encapsulation"):
        does = f"{raw.split()[0]} is configuration, not a show command. It changes the running config of this device and does not by itself prove the network works."
        expect = "Expect either silence (IOS often prints nothing when a line is accepted) or a caret marking the token it rejected. Then show the relevant table."
    elif low.startswith("show") or low.startswith("sh "):
        does = "show reads the running device and prints a table. It does not change the configuration."
        expect = "Expect a table or a short block. An invalid interface name comes back as an error instead of an empty success."
    elif low.startswith("chmod"):
        does = "chmod changes permission bits on an existing file. It does not create the file, and it does not change the owner."
        expect = "Expect no output when it works. ls -l afterwards should show the new bits."
    elif low.startswith("echo") or ">" in raw:
        does = "echo writes a line. With > it replaces the file, and with >> it appends. A missing parent directory is an error, not an empty success."
        expect = "Expect silence on a redirect. cat of the file should show the line you sent."
    elif low.startswith("grep"):
        does = "grep prints the lines of a file that match a pattern. It does not edit the file."
        expect = "Expect the matching lines, or nothing when there is no match. Nothing is a result, not a broken command."
    else:
        does = f"{raw.split()[0]} runs as written. Read the first word as the tool and every later word as its argument."
        expect = "Expect either the tool's normal report or a one-line error. A prompt returning with no error means the line was accepted."
    return does, flag, expect, why


def syntax_card(lab):
    """Command forms with placeholders. These are not filled in with this attempt's answer."""
    import lab_skills as SK
    custom = SK.syntax(lab)
    if custom:
        return custom
    fam = family(lab)
    kind = lab.get("kind")
    common = [
        ("Read the session note", "show note"),
        ("Read a file", "type <path>    or    show the file at <path>"),
    ]
    if fam in ("win", "desk") or kind in ("windows", "win11gui"):
        common += [
            ("List full IP configuration", "ipconfig <option>"),
            ("Set DNS servers", "Set-DnsClientServerAddress -InterfaceAlias <name> -ServerAddresses <address>"),
            ("Rename this computer", "Rename-Computer -NewName <name>"),
            ("Ask whether a host answers", "ping <destination>"),
            ("Ask DNS about a name", "nslookup <name>"),
        ]
    if kind in ("switch", "router") or fam.startswith("sw_") or fam.startswith("rtr_"):
        common += [
            ("Enter privileged mode", "enable"),
            ("Enter configuration mode", "configure terminal"),
            ("Select an interface", "interface <type><slot>/<port>"),
            ("Create a VLAN", "vlan <id>"),
            ("Access port VLAN", "switchport mode access"),
            ("Assign the access VLAN", "switchport access vlan <id>"),
            ("Trunk", "switchport mode trunk"),
            ("Limit a trunk", "switchport trunk allowed vlan <id>,<id>"),
            ("Address an interface", "ip address <address> <mask>"),
            ("Bring an interface up", "no shutdown"),
            ("Default route", "ip route 0.0.0.0 0.0.0.0 <next-hop>"),
            ("Standard access list", "access-list <1-99> deny host <address>"),
            ("Device name", "hostname <name>"),
            ("Interface description", "description <text>"),
        ]
    if fam in ("linux", "vm") or kind in ("linux", "vm", "linuxgui"):
        common += [
            ("List a directory with permissions", "ls <long-option> <path>"),
            ("Show a file", "cat <path>"),
            ("Write a line into a file", "echo <text> > <path>"),
            ("Change mode", "chmod <mode> <path>"),
            ("Change owner", "chown <user> <path>"),
            ("Search a file", "grep <pattern> <path>"),
        ]
    if fam == "linuxgui":
        common += [
            ("Save a network profile", "novak-net save <profile> <address> <prefix> <gateway> <dns>"),
            ("Mount a disk image", "novak-disk mount <image> <mountpoint> <options>"),
            ("Allow a port", "novak-fw allow <port>"),
            ("Unlock an account", "novak-user unlock <user>"),
        ]
    # de-duplicate while keeping order
    seen = set()
    out = []
    for label, form in common:
        if form not in seen:
            seen.add(form)
            out.append({"label": label, "form": form})
    return out


def _flat(text):
    text = re.sub(r"[.!?]", ",", str(text or ""))
    text = text.replace(";", ",")
    return " ".join(text.split()).strip(" ,")


def _cmd_block(cmd, kind, index):
    does, flag, expect, why = explain_command(cmd, kind, index)
    # One sentence so inner periods cannot create a repeated opening.
    # The step number keeps the first words unique inside this stage.
    n = index + 1
    bits = [
        f"Step {n} does this: {_flat(does)}.",
        f"Step {n} flags: {_flat(flag)}." if _flat(flag) else "",
        f"Step {n} shows: {_flat(expect)}.",
        f"Step {n} matters because {_flat(why)}.",
    ]
    paras = "".join(f"<p>{_esc(bit)}</p>" for bit in bits if bit)
    return (
        f"<li class=\"type-this\">{paras}"
        f"<p>Step {n} to type, with no copy button: <code class=\"cmd-text\">{_esc(cmd)}</code></p></li>"
    )


def _lead(lab, stage):
    who, where = _persona(lab)
    title = (lab.get("title") or lab.get("id") or "this lab").strip()
    if stage == "guided":
        return f"{who} at {where} opened a ticket that needs {title}. Work the steps below even if you have not read the lesson yet."
    if stage == "assisted":
        return f"After the walkthrough, {who} at {where} has a second case on the same kind of system. The names and numbers are not the ones you just typed."
    return f"Incident for {who} at {where}: since this morning the same service has been failing. You get the symptom, not a step list."


def _persona(lab):
    h = int(hashlib.sha1((lab.get("id") or "").encode()).hexdigest()[:6], 16)
    return _PEOPLE[h % len(_PEOPLE)], _PLACES[(h // 5) % len(_PLACES)]


_OUTCOME = {
    "win": (
        "Point Ethernet at the single DNS server written in the practice note, and leave the address on automatic. Servers copied from the walkthrough fail this check.",
        "The computer's name has to become the name in the incident note. The DNS change from practice can stay.",
    ),
    "desk": (
        "In the simulated desk, set the DNS server to the address in the practice note. The walkthrough's servers do not count, and this panel is a simulation.",
        "Set the computer name in the simulation to the name in the incident note.",
    ),
    "sw_vlan": (
        "An access port named in the practice note has to sit in the VLAN named there. The VLAN from the walkthrough does not count.",
        "Set the device name to the one in the incident note. The VLAN you added can stay.",
    ),
    "sw_trunk": (
        "The uplink has to permit only the VLAN numbers written in the practice note.",
        "Name the switch the way the incident note says.",
    ),
    "sw_portsec": (
        "Turn on port security on the access port the practice note names. The walkthrough's port is the wrong one.",
        "The switch name has to match the incident note.",
    ),
    "sw_banner": (
        "The login banner has to include the exact token from the practice note.",
        "Then set the device name from the incident note.",
    ),
    "sw_desc": (
        "The interface named in the practice note needs that description, character for character.",
        "The name in the incident note replaces the current device name.",
    ),
    "sw_host": (
        "Change the device name to the one in the practice note. Showing the old name is not the change.",
        "Put the description from the incident note on the interface it names.",
    ),
    "rtr_addr": (
        "Give the interface named in the practice note the address and mask written there, and bring the interface up. Walkthrough addresses fail this check.",
        "Set the router name from the incident note.",
    ),
    "rtr_route": (
        "Add a default route whose next hop is the address in the practice note. The hop from the walkthrough is a different router.",
        "Name the router as the incident note requires.",
    ),
    "rtr_acl": (
        "A standard access list has to deny the single host written in the practice note.",
        "Set the device name from the incident note.",
    ),
    "rtr_desc": (
        "The interface in the practice note needs that description, not the walkthrough's wording.",
        "Apply the device name from the incident note.",
    ),
    "rtr_host": (
        "Change the device name to the practice note's name.",
        "Describe the interface exactly as the incident note writes it.",
    ),
    "linux": (
        "A file in the home directory holds a line, a destination path, and a mode. The destination file has to contain that line and carry that mode.",
        "The incident note names a second file, a second line, and a tighter mode. Leave the practice file in place.",
    ),
    "vm": (
        "Inside this Linux machine, a text file in root's home directory holds a line, a path, and a mode. Create that file with that line and that mode. The check reads the file from the running system.",
        "The same directory's incident section names a second file. Create it the same way. The practice file is not a substitute.",
    ),
    "linuxgui": (
        "Read the practice ticket on the desktop and apply every value it lists. The guided profile's numbers will not match.",
        "Open the desktop file whose name starts with INC- and make the live system match it, not only a saved profile.",
    ),
    "number": (
        "The practice note gives an IPv4 address and a prefix length. Submit the network address for that prefix, not a single host address.",
        "The incident note has a different address and prefix. Submit that network address. The practice answer will not pass.",
    ),
    "choice": (
        "The practice note describes one case. Submit the outcome that fits, using words this lab already taught. The walkthrough's decision fails when the case is different.",
        "The incident note is a second case. Submit its outcome. It is not the same decision as the practice case.",
    ),
}


_BRIDGE = (
    "Find the values in the session note. They are not repeated in this text.",
    "Open the desk note for this stage before you change anything.",
    "The note is part of the machine or the desk, and it changes when the attempt changes.",
    "If you copy a number from the walkthrough, the check is built to fail.",
    "Hints describe the goal again. They do not fill in the note.",
    "When you are done, the check reads the result, not the line you typed.",
)


def _later_paragraphs(lab, stage):
    import lab_stage_scenarios as LS
    return [LS.prose(lab, stage)]


def guided_html(lab):
    import lab_stage1
    return lab_stage1.guided_html(lab, _esc, guided_commands(lab))


def later_html(lab, stage):
    sentences = _later_paragraphs(lab, stage)
    body = "<div class=\"stage-story\">" + "".join(f"<p>{_esc(s)}</p>" for s in sentences) + "</div>"
    card = syntax_card(lab)
    rows = "".join(
        f"<li><span>{_esc(row['label'])}</span> <code>{_esc(row['form'])}</code></li>" for row in card
    )
    fam = family(lab)
    note_btn = ""
    if fam not in ("vm", "linuxgui"):
        note_btn = (
            f"<p><button type=\"button\" class=\"btn btn-sm btn-outline-navy\" data-open-note=\"{stage}\">Open the desk note</button></p>"
            f"<pre class=\"desk-note\" data-note-for=\"{stage}\" hidden></pre>"
        )
    form = ""
    if fam in ("choice", "number", "desk"):
        label = "Network address" if fam == "number" else ("Setting from the note" if fam == "desk" else "Outcome from the note")
        form = (
            f"<form class=\"stage-answer\" data-stage=\"{stage}\">"
            f"<label>{_esc(label)} <input name=\"answer\" autocomplete=\"off\" autocapitalize=\"off\" spellcheck=\"false\"></label> "
            f"<button type=\"submit\" class=\"btn btn-sm btn-brand\">Check this stage</button>"
            f"<p class=\"stage-result\" role=\"status\"></p></form>"
        )
    return body + note_btn + form + f"<h3 class=\"h6\">Syntax reference</h3><ul class=\"syntax-card\">{rows}</ul>"


def public(lab, state, done):
    if not needs_stages(lab):
        return None
    done = done or []
    passed = [s for s in STAGE_ORDER if f"stage:{s}" in done]
    stages = []
    for sid, title in (
        ("guided", "Stage 1 — Guided walkthrough"),
        ("assisted", "Stage 2 — Assisted practice"),
        ("ticket", "Stage 3 — Unassisted ticket"),
    ):
        html_body = guided_html(lab) if sid == "guided" else later_html(lab, sid)
        stages.append({
            "id": sid,
            "title": title,
            "html": html_body,
            "passed": sid in passed,
        })
    return {"stages": stages, "passed": passed, "family": family(lab)}


def later_hint(lab, stage, tier):
    import lab_stage_scenarios as LS
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", LS.prose(lab, stage)) if s.strip()]
    if not parts:
        return "Read the note for this stage."
    if tier <= 1:
        return parts[0]
    return parts[1] if len(parts) > 1 else parts[0]


def solving_commands(lab):
    """Full walkthrough command lines. Prose hints and one-word toggles are not included."""
    out = []
    for raw in guided_commands(lab):
        c = " ".join(str(raw).split())
        if not c or c.startswith("#"):
            continue
        if len(c) < 8 and " " not in c and "/" not in c:
            continue
        if c not in out:
            out.append(c)
    return out


def sentence_openings(html_text, n=3):
    text = re.sub(r"<[^>]+>", " ", html_text or "")
    text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    counts = {}
    for part in parts:
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'./_-]*", part)
        if len(words) < n:
            continue
        key = " ".join(w.lower() for w in words[:n])
        counts[key] = counts.get(key, 0) + 1
    return counts
