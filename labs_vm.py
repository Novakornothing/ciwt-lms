"""Real-environment labs: a genuine Linux VM that runs entirely in the student's browser (v86, x86 → WebAssembly).

No server cost: the browser downloads the emulator (~2.4 MB) and a Buildroot Linux image (~10 MB) once and boots it
locally. Grading inspects the real VM: when the student presses "Check my work" the page drops a probe script into
the VM's 9p share (/mnt), runs it, reads the result file back and posts it with the attempt nonce; the server turns
that into objectives. Every command line the student sends to the VM is logged to the attempt's event log, so
process rules (e.g. "verified with ls -l after chmod") use the real command history.

Trust note: the VM runs on the student's device, so a determined student could forge the probe output. These labs
are formative practice; for summative use pair them with the event log review or an instructor sign-off.
Assets: tools/fetch_v86.sh (pinned versions + sha256). Licences: see static/vendor/v86/LICENSES.md.
"""
import hashlib
import re

VM_ASSETS = {
    "libv86": "vendor/v86/libv86.js",
    "wasm": "vendor/v86/v86.wasm",
    "bios": "vendor/v86/seabios.bin",
    "vga_bios": "vendor/v86/vgabios.bin",
    "bzimage": "vendor/v86/buildroot-bzImage68.bin",
}

# Probe: POSIX sh, BusyBox-only, absolute paths, no aliases (non-interactive shell). Writes key/value lines.
PROBE = r"""P=/root/support
F=$P/tickets/notes.txt
{
echo "nonce __NONCE__"
[ -d $P/tickets ] && echo "dir 1" || echo "dir 0"
grep -qs 'ticket 4512' $F && echo "note 1" || echo "note 0"
echo "mode $(ls -ld $F 2>/dev/null | cut -c1-10)"
echo "owner $(ls -ld $F 2>/dev/null | awk '{print $3}')"
id -u tech1 >/dev/null 2>&1 && echo "user 1" || echo "user 0"
[ -x $P/check.sh ] && echo "exec 1" || echo "exec 0"
R=/tmp/.ciwt-run; rm -f $R
if [ -x $P/check.sh ]; then
  (cd $P && ./check.sh </dev/null >$R 2>&1) & W=$!
  i=0; while kill -0 $W 2>/dev/null && [ $i -lt 3 ]; do sleep 1; i=$((i+1)); done; kill $W 2>/dev/null
fi
echo "run $(head -c 200 $R 2>/dev/null | tr '\n' ' ')"; rm -f $R
echo "end"
} > /mnt/.ciwt-result 2>&1
"""

VM_LINUX = {
    "id": "linux-vm-perms",
    "title": "Real Linux VM — files, ownership, permissions and a support script",
    "kind": "vm",
    "blurb": "A real Linux machine (BusyBox/Buildroot, kernel 6.8) boots inside your browser. Nothing is simulated: "
             "every command really runs. Graded by inspecting the VM.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM and get a shell prompt"},
        {"id": "mkdir", "text": "Create /root/support/tickets (mkdir -p)"},
        {"id": "note", "text": "Write the line ticket 4512 into /root/support/tickets/notes.txt"},
        {"id": "perms", "text": "Make notes.txt readable and writable by its owner, readable by the group, nothing for others (640)"},
        {"id": "owner", "text": "Create the user tech1 (adduser -D tech1) and make tech1 the owner of notes.txt (chown)"},
        {"id": "script", "text": "Create /root/support/check.sh that prints disk ok, make it executable and run it"},
        {"id": "verified", "text": "Verify your work with ls -l after changing permissions (from your command history)"},
    ],
    "intro": "SR-4188: the night shift needs a private ticket notes file owned by the new technician account and a "
             "one-line health-check script. This is a real Linux VM running in your browser — real errors, real man-less BusyBox "
             "tools (try --help). Press Check my work at any time; the grader looks inside the VM.",
    "success_msg": "Every check passed inside the real VM — directory, contents, mode 640, owner tech1, working script, verified.",
    "initial_state": {},
    "hints": ["mkdir -p /root/support/tickets", "echo 'ticket 4512' > /root/support/tickets/notes.txt",
              "chmod 640 /root/support/tickets/notes.txt", "adduser -D tech1", "chown tech1 /root/support/tickets/notes.txt",
              "printf '#!/bin/sh\\necho disk ok\\n' > /root/support/check.sh", "chmod +x /root/support/check.sh",
              "/root/support/check.sh", "ls -l /root/support/tickets"],
    "obj_hints": {
        "boot": ["Press Start VM and wait for the ~% prompt (5–40 s depending on the device).", "Start VM, then wait for ~%."],
        "mkdir": ["mkdir makes directories; -p creates missing parents too.", "mkdir -p /root/support/tickets"],
        "note": ["echo writes text; > sends it into a file (creating or replacing it).",
                 "echo 'ticket 4512' > /root/support/tickets/notes.txt"],
        "perms": ["Octal: r=4 w=2 x=1 per triplet (owner, group, others). rw-=6, r--=4, ---=0.",
                  "chmod 640 /root/support/tickets/notes.txt"],
        "owner": ["Create the account first (BusyBox: adduser -D for no password), then change the owner with chown.",
                  "adduser -D tech1  then  chown tech1 /root/support/tickets/notes.txt"],
        "script": ["A script starts with #!/bin/sh; it needs the x bit before ./check.sh will run.",
                   "printf '#!/bin/sh\\necho disk ok\\n' > /root/support/check.sh ; chmod +x /root/support/check.sh ; /root/support/check.sh"],
        "verified": ["Professionals check their change. List the file with permissions after the chmod.",
                     "ls -l /root/support/tickets"],
    },
    "course_objectives": ["IT-9.1", "IT-9.3"],
    "minutes": 30,
    "palette": ["ls -l ", "cd ", "pwd", "cat ", "mkdir -p ", "echo ", "chmod ", "chown ", "adduser -D ", "id ", "clear"],
    "vm": {"memory_mb": 64, "image": "buildroot-bzImage68.bin", "download_mb": 12.5, "prompt_re": r"[#%$] $"},
    "solution": {"probe": "nonce {nonce}\ndir 1\nnote 1\nmode -rw-r-----\nowner tech1\nuser 1\nexec 1\nrun disk ok \nend\n",
                 "vm_commands": ["mkdir -p /root/support/tickets", "echo 'ticket 4512' > /root/support/tickets/notes.txt",
                                 "chmod 640 /root/support/tickets/notes.txt", "adduser -D tech1",
                                 "chown tech1 /root/support/tickets/notes.txt",
                                 "printf '#!/bin/sh\\necho disk ok\\n' > /root/support/check.sh", "chmod +x /root/support/check.sh",
                                 "/root/support/check.sh", "ls -l /root/support/tickets"]},
}

VM_LABS = [VM_LINUX]
VM_BY_ID = {l["id"]: l for l in VM_LABS}


def nonce(seed):
    return hashlib.sha1(f"vm:{seed}".encode()).hexdigest()[:12]


def fresh(lab, seed):
    return {"nonce": nonce(seed), "vm_cmds": [], "checks": 0, "probe_last": None}


def probe_script(state):
    return PROBE.replace("__NONCE__", state.get("nonce") or "")


def parse_probe(text):
    out = {}
    for ln in (text or "").splitlines():
        k, _, v = ln.strip().partition(" ")
        if k:
            out[k] = v.strip()
    return out


_VERIFY_RE = re.compile(r"^\s*(ls|ll)\b.*(-[a-z]*l|\bll\b)")


def record_commands(state, lines):
    """Append the student's VM command lines (already in order)."""
    cmds = state.setdefault("vm_cmds", [])
    for ln in lines or []:
        ln = str(ln).replace("\r", "")[:500]
        if ln.strip():
            cmds.append(ln)
    del cmds[:-500]


def _verified(cmds):
    seen_chmod = False
    for c in cmds:
        c2 = c.strip()
        if re.match(r"^chmod\b", c2):
            seen_chmod = True
        elif seen_chmod and (_VERIFY_RE.match(c2) or c2.startswith("stat ")):
            return True
    return False


def grade(lab, state, done, probe_text, booted=True):
    """Objectives from the real VM probe + the real command history. Returns (result, state, done)."""
    p = parse_probe(probe_text)
    state["checks"] = (state.get("checks") or 0) + 1
    res = {"checks": {}, "messages": []}
    if probe_text and p.get("nonce") != state.get("nonce"):
        res["error"] = "The check result did not come from this attempt's VM (nonce mismatch). Press Check my work again."
        return res, state, done
    state["probe_last"] = {k: p.get(k) for k in ("dir", "note", "mode", "owner", "user", "exec", "run")}
    got = {
        "boot": bool(booted and (probe_text or state.get("vm_cmds"))),
        "mkdir": p.get("dir") == "1",
        "note": p.get("note") == "1",
        "perms": p.get("mode") == "-rw-r-----",
        "owner": p.get("user") == "1" and p.get("owner") == "tech1",
        "script": p.get("exec") == "1" and "disk ok" in (p.get("run") or ""),
        "verified": _verified(state.get("vm_cmds") or []),
    }
    why = {
        "mkdir": "/root/support/tickets does not exist yet.",
        "note": "notes.txt is missing or does not contain the line ticket 4512.",
        "perms": f"notes.txt mode is {p.get('mode') or 'missing'}; the ticket asks for -rw-r----- (640).",
        "owner": ("user tech1 does not exist yet." if p.get("user") != "1" else f"notes.txt is owned by {p.get('owner') or '?'}, not tech1."),
        "script": ("check.sh is not executable (chmod +x)." if p.get("exec") != "1" else
                   f"check.sh runs but printed: {(p.get('run') or '').strip()[:80] or '(nothing)'}"),
        "verified": "No ls -l after your chmod in your command history yet.",
    }
    for oid, ok in got.items():
        res["checks"][oid] = ok
        if ok and oid not in done:
            done.append(oid)
        elif not ok and oid in why:
            res["messages"].append(why[oid])
    return res, state, done


def solved_probe(state):
    return VM_LINUX["solution"]["probe"].format(nonce=state.get("nonce"))
