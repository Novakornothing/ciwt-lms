"""Stage 2 and Stage 3 for the Linux shell and Linux VM labs.

Each lab keeps its own skill. Stage 2 gives the seeded values in the note.
Stage 3 states the symptom. Grading reads the resulting file, route, filter,
or crontab, not a proof-file token and not a hostname.
"""
from __future__ import annotations

import lab_skills as SK

PERM = [
    ("Long listing", "ls -l <path>"),
    ("Numeric mode", "chmod <mode> <path>"),
    ("Symbolic mode", "chmod <class><op><bits> <path>"),
    ("Owner", "chown <user> <path>"),
    ("Group", "chown :<group> <path>"),
    ("BusyBox account", "adduser -D <user>"),
]
FILE = [
    ("Show a file", "cat <path>"),
    ("Write a file", "printf <format> > <path>"),
    ("Search", "grep <pattern> <path>"),
]
NET = [
    ("Addresses", "ip address"),
    ("Routes", "ip route"),
    ("Default route", "ip route add default via <hop>"),
    ("Resolver", "nameserver <address>"),
    ("Forwarding", "sysctl net.ipv4.ip_forward"),
]
FILTER = [
    ("Append a rule", "iptables -A <chain> <match> -j <target>"),
    ("Policy", "iptables -P <chain> <target>"),
    ("Show rules", "iptables -S"),
]
CRON = [
    ("Show the table", "crontab -l"),
    ("Install a table", "crontab <file>"),
]


def _q(text):
    return str(text).replace("'", "'\\''")


def _file(lid, checker, syntax, directory, s2_name, s3_name, s2_prose, s3_prose, s2_note, s3_note,
          s2_bad, s2_good, s3_bad, s3_good, s2_owner=None, s3_owner=None, s3_group=None,
          s2_bad_owner="root", s3_bad_owner="root", s2_group=None, s3_bad_group="root"):
    def enrich(f, seed):
        n = 1000 + (seed * 17) % 8000
        f["s2_path"] = f"{directory}/{s2_name.format(n=n)}"
        f["s3_path"] = f"{directory}/{s3_name.format(n=n)}"
        f["s2_mode"] = s2_good
        f["s3_mode"] = s3_good
        f["s2_owner"] = s2_owner or ""
        f["s3_owner"] = s3_owner or ""
        f["s3_group"] = s3_group or ""
        f["skill_dir"] = directory

    def _plant(mode, owner, path_key, group=None):
        def run(f):
            path = f[path_key]
            parent = path.rsplit("/", 1)[0]
            cmds = [
                f"mkdir -p {parent}",
                f"printf '%s\\n' 'lab-data' > {path}",
                f"chmod {mode} {path}",
            ]
            if owner and owner != "root":
                cmds.append(f"chown {owner} {path}")
            elif group:
                cmds.append(f"chown root:{group} {path}")
            return cmds
        return run

    def _fix(mode, owner, path_key, group=None):
        def run(f):
            path = f[path_key]
            cmds = [f"chmod {mode} {path}"]
            if owner:
                cmds.append(f"chown {owner}{':' + group if group else ''} {path}")
            elif group:
                cmds.append(f"chown :{group} {path}")
            return cmds
        return run

    def _checks(mode, owner, path_key, group=None):
        def run(f):
            item = {"kind": "mode", "path": f[path_key], "mode": mode}
            if owner:
                item["owner"] = owner
            if group:
                item["group"] = group
            return [item]
        return run

    def note_s2(f):
        return s2_note.format(path=f["s2_path"], mode=f["s2_mode"], owner=s2_owner or "", directory=directory)

    def note_s3(f):
        return s3_note.format(path=f["s3_path"], directory=directory, mode=s3_good, owner=s3_owner or "", group=s3_group or "")

    SK.SPECS[lid] = {
        "syntax": syntax,
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": checker,
                "prose": s2_prose,
                "note": note_s2,
                "plant": _plant(s2_bad, s2_bad_owner if s2_owner else None, "s2_path", s2_group),
                "fix": _fix(s2_good, s2_owner, "s2_path", s2_group),
                "checks": _checks(s2_good, s2_owner, "s2_path", s2_group),
            },
            "ticket": {
                "checker": checker,
                "prose": s3_prose,
                "note": note_s3,
                "plant": _plant(s3_bad, s3_bad_owner if (s3_owner or s3_group) else None, "s3_path", s3_bad_group if s3_group else None),
                "fix": _fix(s3_good, s3_owner, "s3_path", s3_group),
                "checks": _checks(s3_good, s3_owner, "s3_path", s3_group),
            },
        },
    }


def _sibling(path):
    if "." in path.rsplit("/", 1)[-1]:
        stem, ext = path.rsplit(".", 1)
        return f"{stem}-night.{ext}"
    return path + "-night"


def _text(lid, checker, syntax, path_tmpl, s2_prose, s3_prose, s2_note, s3_note, s2_bad, s2_good, s3_bad, s3_good):
    def enrich(f, seed):
        n = 1000 + (seed * 19) % 8000
        f["s2_path"] = path_tmpl.format(n=n)
        f["s3_path"] = _sibling(f["s2_path"])
        f["s2_good"] = s2_good
        f["s3_good"] = s3_good

    def plant(bad, key):
        def run(f):
            path = f[key]
            parent = path.rsplit("/", 1)[0]
            return [f"mkdir -p {parent}", f"printf '%s\\n' '{_q(bad)}' > {path}"]
        return run

    def fix(good_key, path_key):
        def run(f):
            return [f"printf '%s\\n' '{_q(f[good_key])}' > {f[path_key]}"]
        return run

    def checks(good_key, path_key):
        def run(f):
            return [{"kind": "contains", "path": f[path_key], "text": f[good_key]}]
        return run

    SK.SPECS[lid] = {
        "syntax": syntax,
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": checker, "prose": s2_prose,
                "note": lambda f: s2_note.format(path=f["s2_path"], value=f["s2_good"]),
                "plant": plant(s2_bad, "s2_path"), "fix": fix("s2_good", "s2_path"),
                "checks": checks("s2_good", "s2_path"),
            },
            "ticket": {
                "checker": checker, "prose": s3_prose,
                "note": lambda f: s3_note.format(path=f["s3_path"], value=f["s3_good"]),
                "plant": plant(s3_bad, "s3_path"), "fix": fix("s3_good", "s3_path"),
                "checks": checks("s3_good", "s3_path"),
            },
        },
    }


def _route(lid, s2_prose, s3_prose, addr, hop_a, hop_b):
    """addr is an on-link address already on the host. hop_a and hop_b are in that subnet."""
    def enrich(f, seed):
        f["s2_hop"] = hop_a
        f["s3_hop"] = hop_b
        f["link_addr"] = addr

    link = f"ip addr add {addr} dev eth0"
    SK.SPECS[lid] = {
        "syntax": NET,
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": "route",
                "prose": s2_prose,
                "note": lambda f: f"This host is on {f['link_addr']}. It has no usable default route. The on-link next hop is {f['s2_hop']}.",
                "plant": lambda f: [link],
                "fix": lambda f: [f"ip route add default via {f['s2_hop']}"],
                "checks": lambda f: [{"kind": "route", "hop": f["s2_hop"]}],
            },
            "ticket": {
                "checker": "route",
                "prose": s3_prose,
                "note": lambda f: "Hosts beyond this subnet time out. The default route is missing. The next hop is the first line of /root/NEXT-HOP, and it is on the connected subnet.",
                "plant": lambda f: [link, "mkdir -p /root", f"printf '%s\\n' '{f['s3_hop']}' > /root/NEXT-HOP"],
                "fix": lambda f: [f"ip route add default via {f['s3_hop']}"],
                "checks": lambda f: [{"kind": "route", "hop": f["s3_hop"]}],
            },
        },
    }


def _forward(lid, s2_prose, s3_prose):
    SK.SPECS[lid] = {
        "syntax": NET,
        "enrich": lambda f, seed: None,
        "stages": {
            "assisted": {
                "checker": "forward",
                "prose": s2_prose,
                "note": lambda f: "Packets arrive on this router and die. IPv4 forwarding is off. Turn it on.",
                "plant": lambda f: [],
                "fix": lambda f: ["sysctl -w net.ipv4.ip_forward=1"],
                "checks": lambda f: [{"kind": "forward", "value": "1"}],
            },
            "ticket": {
                "checker": "forward",
                "prose": s3_prose,
                "note": lambda f: "A host on the far LAN never answers, and this box still has forwarding disabled. Traffic is not supposed to stop here.",
                "plant": lambda f: [],
                "fix": lambda f: ["sysctl -w net.ipv4.ip_forward=1"],
                "checks": lambda f: [{"kind": "forward", "value": "1"}],
            },
        },
    }


def _rule(cmd):
    table, line, _policy = SK.canonical_iptables(cmd)
    return {"kind": "iptables", "table": table, "fragment": line}


def _iptables(lid, s2_prose, s3_prose, s2_fragment, s3_fragment, s2_note, s3_note):
    s2_cmd = s2_fragment if str(s2_fragment).startswith("iptables") else f"iptables {s2_fragment}"
    s3_cmd = s3_fragment if str(s3_fragment).startswith("iptables") else f"iptables {s3_fragment}"
    SK.SPECS[lid] = {
        "syntax": FILTER,
        "enrich": lambda f, seed: None,
        "stages": {
            "assisted": {
                "checker": "iptables",
                "prose": s2_prose,
                "note": lambda f: s2_note,
                "plant": lambda f: [],
                "fix": lambda f, c=s2_cmd: [c],
                "checks": lambda f, c=s2_cmd: [_rule(c)],
            },
            "ticket": {
                "checker": "iptables",
                "prose": s3_prose,
                "note": lambda f: s3_note,
                "plant": lambda f: [],
                "fix": lambda f, c=s3_cmd: [c],
                "checks": lambda f, c=s3_cmd: [_rule(c)],
            },
        },
    }


def _cron(lid, s2_prose, s3_prose, s2_line, s3_line):
    def enrich(f, seed):
        f["c2"] = s2_line
        f["c3"] = s3_line

    def plant(bad):
        def run(f):
            return ["mkdir -p /root", f"printf '%s\\n' '{bad}' > /root/cron.table"]
        return run

    SK.SPECS[lid] = {
        "syntax": CRON,
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": "crontab",
                "prose": s2_prose,
                "note": lambda f: f"Root's crontab is missing this job: {f['c2']}",
                "plant": plant("# empty"),
                "fix": lambda f: [f"printf '%s\\n' '{f['c2']}' > /root/cron.table", "crontab /root/cron.table"],
                "checks": lambda f: [{"kind": "crontab", "line": f["c2"]}],
            },
            "ticket": {
                "checker": "crontab",
                "prose": s3_prose,
                "note": lambda f: "The nightly job did not run. Root's crontab still has a placeholder instead of the schedule posted in /root/CRON-WANT.",
                "plant": lambda f: ["mkdir -p /root", "printf '%s\\n' '# placeholder' > /root/cron.table", f"printf '%s\\n' '{f['c3']}' > /root/CRON-WANT"],
                "fix": lambda f: [f"printf '%s\\n' '{f['c3']}' > /root/cron.table", "crontab /root/cron.table"],
                "checks": lambda f: [{"kind": "crontab", "line": f["c3"]}],
            },
        },
    }


# --- registrations ---

_file(
    "linux-shell", "mode", PERM, "/home/trainee/support", "shift-{n}.txt", "audit-{n}.txt",
    "The quarterly report you locked down is not the file the evening shift just dropped in ~/support. A second text file is mode 666, so every account can change it. The practice note names that file and the mode it should have. Leave the original report alone.",
    "Someone on the shared lab host can still read an audit note that was supposed to stay inside the account. It sits in ~/support and is not the file you just corrected. Others should lose read access. The walkthrough report is already done.",
    "File: {path}. Required mode: {mode}.",
    "An audit file in {directory} is still readable by every account. Close other-read. The practice file can stay as you left it.",
    "666", "640", "644", "640",
)

_file(
    "linux-vm-perms", "mode-owner", PERM, "/srv/handoff", "payroll-{n}.txt", "handoff-{n}.txt",
    "tech1 can read the walkthrough notes, and a new payroll export in the shared handoff directory cannot. It was created by root as mode 666. The practice note names the file. It has to be mode 640 and owned by tech1. tech1 can reach /srv/handoff. Do not loosen the original notes file.",
    "The night technician cannot save the handoff in /srv/handoff, but every other account can rewrite it. The file is the world-writable one in that shared directory. tech1 should own it, and others should not be able to change it. The payroll file from practice is already correct.",
    "File: {path}. Mode: {mode}. Owner: {owner}. The directory /srv/handoff is shared so tech1 can reach it.",
    "The handoff under {directory} is writable by everyone and owned by root. tech1 should own it, and others should not be able to change it.",
    "666", "640", "666", "640", s2_owner="tech1", s3_owner="tech1",
)

_file(
    "linux-vm-shell", "mode", PERM, "/root/support", "rotate-{n}.sh", "private-{n}.txt",
    "backup.sh already runs. A second script, named in the practice note, is still mode 644, so the kernel will not execute it. Add execute for the owner only. Do not change the backup script you already fixed.",
    "A private note under /root/support is still readable by every account on the box. It is not the script you just made executable. Remove read for others and leave the owner's write bit.",
    "Script: {path}. It must be mode {mode} so the owner can execute it.",
    "A private note in {directory} is still world-readable. Others should not be able to read it.",
    "644", "744", "644", "640",
)

_file(
    "sec-vm-perms", "mode-group", PERM, "/srv/secrets", "bonus-{n}.csv", "timesheets-{n}.csv",
    "payroll.csv from the walkthrough is already 640 and grouped to payroll. A bonus sheet in the same directory is still 664 and grouped to root. The practice note names it. Group payroll, mode 640.",
    "Timesheets in /srv/secrets are still group-owned by root and writable by anyone in the default group. The sheet is the world-writable csv that is not the bonus file. The payroll group should own the group, and others should have no access.",
    "File: {path}. Group payroll. Mode {mode}.",
    "A csv in {directory} is still readable and writable by the wrong group. The payroll group should have read, and others none.",
    "664", "640", "666", "640", s3_group="payroll", s3_bad_group="root",
)

_file(
    "sec-vm-suid", "mode", PERM, "/usr/local/bin", "helper-{n}", "cleanup-{n}",
    "You already cleared the setuid bit on the walkthrough helper. A second program in /usr/local/bin is mode 4755, so it still runs as its owner. The practice note names it. Leave it executable, and turn the setuid bit off.",
    "Something in /usr/local/bin still runs with the owner's identity no matter who starts it. It is not the helper you already fixed. Find the setuid program and clear that bit without removing execute.",
    "Program: {path}. Required mode: {mode}. The setuid bit must be off.",
    "A program in {directory} is still setuid. It should be an ordinary executable for the owner, the group, and others.",
    "4755", "755", "4755", "755",
)

_file(
    "sec-vm-world", "mode", PERM, "/srv/drop", "inbox-{n}.txt", "dropbox-{n}.txt",
    "The walkthrough file is no longer world-writable. A new inbox file in /srv/drop is mode 666. The practice note names it. Remove write for others and leave the owner able to write.",
    "Staff can still change a file in the drop directory that they do not own. It is not the inbox you just closed. Others must lose write.",
    "File: {path}. Mode {mode}. Others must not have write.",
    "A file in {directory} is still writable by every account. Remove that write bit.",
    "666", "644", "666", "644",
)

_file(
    "sec-vm-sudo", "mode", PERM + [("Sudoers drop-in", "<user> ALL=(root) NOPASSWD: <command>")],
    "/etc/sudoers.d", "limited-{n}", "desk-{n}",
    "The walkthrough drop-in already allows only ls. A second drop-in is mode 666 and would be ignored or unsafe. The practice note names the file. It must be mode 440.",
    "A sudoers drop-in in /etc/sudoers.d is writable by everyone, so it will not be trusted. It is not the limited file from practice. Make it mode 440.",
    "Drop-in: {path}. Mode {mode}.",
    "A file in {directory} is still writable by others. Sudo will not honor a drop-in that is not mode 440.",
    "666", "440", "666", "440",
)

_text(
    "linux-vm-services", "file-text", FILE + [("Service script", "<init-script> start")],
    "/etc/init.d/heartbeat-{n}.conf",
    "The heartbeat unit you repaired is fine. A second service file, named in the practice note, still points DAEMON at the old sbin path. Change that one line to the path in the note. Do not stop the heartbeat you already started.",
    "A service on this host fails at start because its DAEMON path still names a directory that does not exist. The file is under /etc/init.d and is not the one you edited in practice. The correct path is the only line in /root/DAEMON-PATH.",
    "Edit {path} so it contains this exact line: {value}",
    "A heartbeat config under /etc/init.d still names the wrong DAEMON path. The correct line is in /root/DAEMON-PATH. Put that line into the config.",
    "DAEMON=/usr/local/sbin/heartbeat", "DAEMON=/usr/local/bin/heartbeat",
    "DAEMON=/opt/old/heartbeat", "DAEMON=/opt/novak/bin/heartbeat",
)

_text(
    "linux-vm-netclient", "resolv", NET,
    "/etc/resolv.lab-{n}.conf",
    "The lease you already took pointed this client at 10.10.0.53. A second resolver file, named in the practice note, still lists a retired server. Replace that nameserver line with the address in the note. Do not release the address you already have.",
    "Names on this client fail and addresses answer. The resolver file that is not the walkthrough resolv.conf still names a server that does not hold the zone. The address that should be there is the only line in /root/RESOLVER.",
    "File {path} must contain this line: {value}",
    "Name lookups use a resolver file that still points at a retired server. Read /root/RESOLVER and make the nameserver line match it.",
    "nameserver 10.9.9.9", "nameserver 10.10.0.53",
    "nameserver 10.1.1.1", "nameserver 10.10.0.54",
)

_text(
    "linux-vm-dns", "zone", FILE + NET,
    "/etc/hosts.novak-{n}",
    "The walkthrough zone already returns the new intranet address. A second hosts file, named in the practice note, still maps intranet.novak.lab to the retired address. Put the address from the note on that name. Do not break the resolver you already pointed at 10.30.0.53.",
    "intranet.novak.lab still answers with the old address from a hosts file that is not the one you edited in practice. The address it should have now is the only line in /root/INTRANET-ADDR.",
    "The hosts file {path} must contain this exact line: {value}",
    "The intranet name still points at the retired server in a hosts file under /etc. /root/INTRANET-ADDR has the single hosts line that should be published.",
    "10.30.0.99 intranet.novak.lab", "10.30.0.80 intranet.novak.lab",
    "10.30.0.98 intranet.novak.lab", "10.30.0.81 intranet.novak.lab",
)

_text(
    "linux-vm-logs", "log-extract", FILE,
    "/root/evidence/attacker-{n}.txt",
    "You already counted the walkthrough address. A fresh auth extract is named in the practice note, and the top source is not 203.0.113.77. Write that address, and only that address, into the file the note names.",
    "The evidence file that should name tonight's top source still has the walkthrough address. The address that actually failed most often is the only line in /root/evidence/TOP. Do not leave 203.0.113.77 in the evidence file unless TOP says that.",
    "Write this address into {path}: {value}",
    "The evidence file still has the sample address. /root/evidence/TOP has the address that failed most often. Put that address in the evidence file.",
    "203.0.113.77", "198.51.100.23",
    "203.0.113.77", "198.51.100.24",
)

_text(
    "sec-vm-authlog", "log-extract", FILE,
    "/root/ir/source-{n}.txt",
    "The walkthrough source file already has 203.0.113.44. A second source file, named in the practice note, still says unknown. The address with the most failures in this attempt is in the note. Write that address and nothing else.",
    "The IR directory still has a source file that says unknown, and the account file from the walkthrough is not the one that is wrong. Tonight's top source is the only address in /root/ir/TOP.",
    "Write {value} into {path}.",
    "A source file in /root/ir still says unknown. /root/ir/TOP has the address that actually failed most often.",
    "unknown", "203.0.113.50",
    "unknown", "203.0.113.51",
)

_text(
    "sec-vm-grep", "log-extract", FILE,
    "/root/case/hits-{n}.txt",
    "The walkthrough extract already has the SR-4419 lines. A second case file, named in the practice note, is empty. It should contain the one-line marker from the note and must not contain the backup warning.",
    "The case file that is still empty should hold the SR marker and must not pick up the backup warning. The marker text is the only line in /root/case/WANT.",
    "{path} must contain {value} and must not contain the backup warning.",
    "An empty hits file in /root/case is waiting for the marker stored in /root/case/WANT. Do not copy the backup warning into it.",
    "", "SR-4419 disk",
    "", "SR-4419 tape",
)

_text(
    "sec-vm-hash", "checksum", FILE + [("Check a sum", "sha256sum -c <file>")],
    "/opt/app/status-{n}.txt",
    "build.bin from the walkthrough now matches its sum. A status file named in the practice note still says MISMATCH. After you confirm the sum, that status file should contain the word OK from the note.",
    "A status file under /opt/app still says MISMATCH even though the good image is what should be recorded. /opt/app/STATUS-WANT contains the word the status file should hold.",
    "Write {value} into {path} once the sum matches.",
    "The status file still says MISMATCH. /opt/app/STATUS-WANT says what it should contain after the image is the good one.",
    "MISMATCH", "OK",
    "MISMATCH", "OK",
)

_text(
    "sec-vm-fim", "checksum", FILE,
    "/root/fim-{n}.txt",
    "The walkthrough baseline already matches. A second result file, named in the practice note, still says FAIL. It should contain the word MATCH from the note.",
    "The integrity result file still says FAIL. /root/FIM-WANT contains the word it should hold once the tool matches the baseline.",
    "Write {value} into {path}.",
    "An integrity result still says FAIL. Read /root/FIM-WANT and make the result file agree.",
    "FAIL", "MATCH",
    "FAIL", "MATCH",
)

_text(
    "linux-vm-method", "config-text", FILE,
    "/etc/default/timeclock-{n}",
    "The walkthrough service is pointed at the real folder. A second defaults file, named in the practice note, still has DOCROOT set to the old path. Put the DOCROOT line from the note into that file.",
    "The time clock page is empty because a defaults file still names a folder that was renamed. It is not the file you corrected in practice. The right DOCROOT line is the only line in /root/DOCROOT.",
    "{path} must contain {value}",
    "A timeclock defaults file still points at the old folder. /root/DOCROOT has the line it should contain.",
    "DOCROOT=/var/oldclock", "DOCROOT=/srv/timeclock",
    "DOCROOT=/var/oldclock", "DOCROOT=/srv/timeclock/public",
)

_text(
    "linux-vm-web", "config-text", FILE,
    "/etc/default/intranet-{n}",
    "The walkthrough service already listens on all addresses. A second defaults file, named in the practice note, still says ADDR=127.0.0.1, so only local clients can connect. Set the ADDR line from the note.",
    "Remote clients still cannot open the intranet because a defaults file binds the listener to loopback. It is not the file you changed in practice. /root/ADDR-WANT has the line that should be in the file.",
    "{path} must contain {value}",
    "A listener config still binds to loopback. /root/ADDR-WANT has the ADDR line it should contain.",
    "ADDR=127.0.0.1", "ADDR=0.0.0.0",
    "ADDR=127.0.0.1", "ADDR=10.30.0.12",
)

_text(
    "linux-vm-disk", "fstab", FILE + [("Boot mounts", "UUID=<uuid> <mountpoint> <type> <options>")],
    "/etc/fstab.d/appdata-{n}",
    "The walkthrough mount is already in the real fstab. A drop-in named in the practice note still lists /dev/sda1, which will move when disks enumerate differently. Replace that line with the UUID line from the note.",
    "A disk drop-in still mounts appdata by the device name, so a reboot can attach the wrong disk. It is not the line you fixed in practice. /root/FSTAB-WANT has the UUID line that should replace it.",
    "{path} must contain {value}",
    "An fstab drop-in still names /dev/sda1. /root/FSTAB-WANT has the UUID line that should be there instead.",
    "/dev/sda1 /srv/data ext4 defaults 0 2", "UUID=abc123 /srv/data ext4 defaults 0 2",
    "/dev/sdb1 /srv/data ext4 defaults 0 2", "UUID=def456 /srv/archive ext4 defaults 0 2",
)

_text(
    "linux-vm-ssh", "sshd", FILE + [("Key file mode", "chmod <mode> <path>"), ("sshd test", "sshd -t")],
    "/etc/ssh/sshd_config.d/lab-{n}.conf",
    "The walkthrough daemon already refuses passwords. A drop-in named in the practice note still says PasswordAuthentication yes. Set the line from the note. Do not turn root login back on.",
    "Password login is still allowed by a drop-in that is not the one you edited. /root/SSHD-WANT has the line that should be in that drop-in.",
    "{path} must contain {value}",
    "An sshd drop-in still allows passwords. /root/SSHD-WANT has the line it should contain.",
    "PasswordAuthentication yes", "PasswordAuthentication no",
    "PasswordAuthentication yes", "KbdInteractiveAuthentication no",
)

_text(
    "sec-vm-ssh", "sshd", FILE,
    "/etc/ssh/sshd_config.d/ops-{n}.conf",
    "The walkthrough key is in place. A drop-in named in the practice note still permits root login. It should contain the PermitRootLogin line from the note.",
    "Root can still log in with a password because a drop-in says so. It is not the ops file from practice. /root/SSHD-WANT has the line that should replace it.",
    "{path} must contain {value}",
    "A drop-in still permits root login. /root/SSHD-WANT has the line it should contain.",
    "PermitRootLogin yes", "PermitRootLogin no",
    "PermitRootLogin yes", "PermitRootLogin prohibit-password",
)

_text(
    "sec-openssl", "key-mode", PERM + [("Key", "openssl genrsa -out <path> <bits>"), ("Request", "openssl req -new -key <path> -subj <subject>")],
    "/root/pki/status-{n}.txt",
    "server.key from the walkthrough is already mode 600. A status file named in the practice note still says WORLD. It should contain the word PRIVATE from the note, which is what you record after the key is not readable by others.",
    "A status file under /root/pki still says WORLD. The key it describes should not be readable by other accounts. /root/pki/WANT says what the status file should contain.",
    "Write {value} into {path}.",
    "The key status still says WORLD. /root/pki/WANT has the word it should contain once the key is private.",
    "WORLD", "PRIVATE",
    "WORLD", "PRIVATE",
)

_text(
    "linux-vm-users", "group-file", PERM,
    "/etc/labgroup-{n}",
    "helpdesk from the walkthrough already exists. A group file named in the practice note is empty. It should contain the single group line from the note, the same shape as /etc/group.",
    "A group file under /etc is empty, so the desk tools do not see the new group. It is not the helpdesk line you already created. /root/GROUP-WANT has the line that file should hold.",
    "{path} must contain {value}",
    "An empty group file is still empty. /root/GROUP-WANT has the line it should contain.",
    "", "opsdesk:x:2400:ana,ben",
    "", "nightdesk:x:2401:cara,ben",
)

_text(
    "sec-vm-users", "shadow", PERM,
    "/etc/shadow.d/intern-{n}",
    "The walkthrough intern is locked. A shadow snippet named in the practice note still has an unlocked password field. Replace it with the locked line from the note. Do not delete the account.",
    "An intern shadow snippet still has a usable password hash. It is not the account you locked in the walkthrough. /root/SHADOW-WANT has the locked line that should replace it.",
    "{path} must contain {value}",
    "A shadow snippet still allows a password. /root/SHADOW-WANT has the locked line it should contain.",
    "intern:$6$hash:19000:0:99999:7:::", "intern:!:19000:0:99999:7:::",
    "intern2:$6$hash:19000:0:99999:7:::", "intern2:!:19000:0:99999:7:::",
)

_text(
    "sec-vm-faillock", "shadow-age", PERM + [("Password age", "chage -m <min> -M <max> <user>")],
    "/etc/shadow.d/age-{n}",
    "The walkthrough account already has a maximum age. A shadow snippet named in the practice note still has minimum 0 and maximum 99999. Replace it with the aged line from the note.",
    "A shadow snippet still allows a password to be changed immediately and to live forever. /root/AGE-WANT has the line with a 14 day minimum and a 90 day maximum.",
    "{path} must contain {value}",
    "Password aging is still unset in a shadow snippet. /root/AGE-WANT has the line it should contain.",
    "contractor:$6$hash:19000:0:99999:7:::", "contractor:$6$hash:19000:14:90:7:::",
    "vendor:$6$hash:19000:0:99999:7:::", "vendor:$6$hash:19000:14:90:7:::",
)

_text(
    "linux-vm-script", "script", PERM + FILE,
    "/usr/local/bin/status-{n}.sh",
    "app-backup.sh already exits 2 when the arguments are missing. A second script, named in the practice note, has no shebang and is not the backup script. It should be the one-line script in the note.",
    "A script under /usr/local/bin still has no shebang, so the kernel will not run it as a shell script. It is not app-backup.sh. /root/SCRIPT-WANT has the line the file should contain.",
    "{path} must contain {value}",
    "A script is still missing its shebang. /root/SCRIPT-WANT has the line it should start with.",
    "echo nope", "#!/bin/sh",
    "echo nope", "#!/usr/bin/env sh",
)

_text(
    "linux-vm-packages", "repo", FILE,
    "/etc/apk/repositories-{n}",
    "The walkthrough repo line is already active. A second repositories file, named in the practice note, still has the repo commented out. The file should contain the uncommented line from the note.",
    "A repositories file still has the local repo commented out, so the package index will not include it. /root/REPO-WANT has the line that should be present.",
    "{path} must contain {value}",
    "The local repository is still commented out in a repositories file. /root/REPO-WANT has the line that should be there.",
    "repo none", "/var/lib/novak-repo",
    "# /var/lib/novak-repo", "/var/lib/novak-night",
)

_text(
    "linux-vm-restore", "restore", FILE,
    "/srv/share/finance/status-{n}.txt",
    "budget-2027 from the walkthrough is restored. A status file named in the practice note still says MISSING. It should contain the word RESTORED from the note, which you write only after the restored tree is the one that passed the sum.",
    "A finance status file still says MISSING. The good backup is the one that passed its sum, not the newer one that failed. /root/RESTORE-WANT has the word the status file should contain.",
    "Write {value} into {path} after the good tree is in place.",
    "The restore status still says MISSING. /root/RESTORE-WANT has the word it should contain.",
    "MISSING", "RESTORED",
    "MISSING", "RESTORED",
)

_text(
    "linux-vm-incident", "account-file", FILE,
    "/etc/passwd.d/extra-{n}",
    "The walkthrough backdoor account is gone. A passwd snippet named in the practice note still has a second UID 0 account. Remove that line so the snippet does not contain it. The note tells you the account name.",
    "A passwd snippet still lists an extra UID 0 account. It is not the one you removed in the walkthrough. /root/UID0-NAME names the account that must not remain.",
    "The file {path} must still contain the real root line and must no longer contain the extra UID 0 account.",
    "A different passwd snippet still lists an extra UID 0 account. Remove that account line and leave the root line.",
    "backdoor:x:0:0:backdoor:/root:/bin/sh", "root:x:0:0:root:/root:/bin/sh",
    "ghost:x:0:0:ghost:/root:/bin/sh", "root:x:0:0:root:/root:/bin/sh",
)

_text(
    "sec-vm-proc", "absent-marker", FILE,
    "/var/tmp/.cache/status-{n}.txt",
    "The walkthrough beacon is gone. A status file named in the practice note still says RUNNING. After the beacon program is not running and its file is gone, that status file should contain the word STOPPED from the note.",
    "A status file under the cache directory still says RUNNING. The beacon program should not be on disk. /root/PROC-WANT has the word the status file should contain.",
    "Write {value} into {path}.",
    "The beacon status still says RUNNING. /root/PROC-WANT has the word it should contain once the program is gone.",
    "RUNNING", "STOPPED",
    "RUNNING", "STOPPED",
)

_text(
    "sec-vm-harden", "absent-marker", FILE,
    "/root/harden-{n}.txt",
    "The walkthrough extra process is stopped. A status file named in the practice note still says LISTENING. It should contain the word CLOSED from the note.",
    "A harden status file still says LISTENING. /root/HARDEN-WANT has the word it should contain after that process is gone.",
    "Write {value} into {path}.",
    "Something still claims to be listening in the status file. /root/HARDEN-WANT has the word that file should contain.",
    "LISTENING", "CLOSED",
    "LISTENING", "CLOSED",
)

_text(
    "sec-vm-backup", "checksum", FILE,
    "/root/keep-status-{n}.txt",
    "The walkthrough archive matches its sum. A status file named in the practice note still says BAD. It should contain the word GOOD from the note, which you write after the archive sum matches.",
    "A keep status file still says BAD. /root/KEEP-WANT has the word it should contain once the archive sum matches and the original file is still in place.",
    "Write {value} into {path}.",
    "The archive status still says BAD. /root/KEEP-WANT has the word it should contain.",
    "BAD", "GOOD",
    "BAD", "GOOD",
)

_text(
    "sec-vm-capture", "log-extract", FILE,
    "/root/case/odd-{n}.txt",
    "The walkthrough case file already has the odd address. A second file, named in the practice note, is empty. It should contain the address from the note and not a normal 443 flow.",
    "An empty odd-address file is sitting in the case directory. /root/case/ODD-WANT has the address it should contain. Do not copy the ordinary 443 lines.",
    "Write {value} into {path}.",
    "The odd-address file is empty. /root/case/ODD-WANT has the address that belongs in it.",
    "", "198.51.100.77",
    "", "198.51.100.78",
)

_text(
    "sec-vm-timeline", "log-extract", FILE,
    "/root/case/order-{n}.txt",
    "The walkthrough timeline is in order. A second file, named in the practice note, lists the later failure first. Replace it with the single line from the note, which has the earlier failure first.",
    "A timeline file still leads with the later failure. /root/case/ORDER-WANT has the line that puts the earlier failure first.",
    "{path} must contain {value}",
    "The timeline file still has the later failure first. /root/case/ORDER-WANT has the line it should contain.",
    "12:10 failed login", "12:02 failed login",
    "12:10 failed login", "12:02 failed login before 12:10",
)

_text(
    "sec-vm-cron", "crontab-text", CRON,
    "/root/cron.clean-{n}",
    "The walkthrough crontab no longer has the hidden sync job. A table file named in the practice note still contains that job and is missing the logrotate line. The note has the line the file should contain.",
    "A crontab file still schedules the hidden sync and never runs logrotate. /root/CRON-WANT has the only line that file should contain.",
    "{path} must contain {value}",
    "A crontab file still has the hidden job. /root/CRON-WANT has the line it should contain instead.",
    "* * * * * /var/tmp/.font/sync.sh", "15 3 * * * /usr/local/bin/logrotate-local",
    "* * * * * /var/tmp/.font/sync.sh", "30 4 * * * /usr/local/bin/logrotate-night",
)

_cron(
    "linux-vm-cron",
    "crond is already running from the walkthrough. Root's crontab does not yet contain the weekday cleanup named in the practice note. Install that one line. Leave the 02:30 backup job if it is already there, but the check for this stage is the cleanup line.",
    "The cleanup did not run this morning. Root's crontab still has a comment where the job should be. The schedule that should be installed is the only line in /root/CRON-WANT.",
    "20 1 * * 1-5 /usr/local/bin/cleanup.sh",
    "45 4 * * 1-5 /usr/local/bin/cleanup-night.sh",
)

_route(
    "linux-vm-routing",
    "Forwarding between the walkthrough LANs already works. This PC is on 10.1.0.0/24 and has no default route, so anything off its own subnet dies here. Install the on-link next hop from the note. Do not remove the connected address.",
    "The PC can ping its own subnet and nothing past it. The default route is missing. Read /root/NEXT-HOP and install that on-link hop.",
    "10.1.0.10/24", "10.1.0.4", "10.1.0.5",
)

_route(
    "linux-vm-nettrouble",
    "The walkthrough path reaches the far host. This client is on 10.2.0.0/24 and has no default route, which is why its pings never leave the subnet. The practice note has an on-link next hop. Install it.",
    "Pings past the local subnet die on this client. The routing table has no default. The hop in /root/NEXT-HOP is on 10.2.0.0/24. Install that route.",
    "10.2.0.40/24", "10.2.0.4", "10.2.0.5",
)

_route(
    "scn-lan2-fix",
    "LAN 2's PC is on 10.2.0.0/24 and has no default route, so it cannot reach the ERP host. The practice note has an on-link next hop. Install it.",
    "The CFO's side of LAN 2 still cannot reach the ERP host. This client has no default route. /root/NEXT-HOP has an on-link hop on 10.2.0.0/24.",
    "10.2.0.40/24", "10.2.0.6", "10.2.0.7",
)

_iptables(
    "linux-vm-nat",
    "The walkthrough edge masquerades 10.5.0.0/24. A second LAN, named in the practice note, is still sent out with its private source, so the far host cannot answer. Append a POSTROUTING masquerade for that source. Do not delete the rule you already added.",
    "A new inside subnet still leaves the edge with a private source address, and the far host never answers. The source that should be masqueraded is in /root/NAT-NET. Append that POSTROUTING masquerade. Leave the walkthrough rule in place.",
    "iptables -t nat -A POSTROUTING -s 10.9.0.0/24 -o eth0 -j MASQUERADE",
    "iptables -t nat -A POSTROUTING -s 10.9.8.0/24 -o eth0 -j MASQUERADE",
    "Append a POSTROUTING masquerade for 10.9.0.0/24 out eth0.",
    "The new inside LAN is still not masqueraded. /root/NAT-NET names 10.9.8.0/24. Masquerade that source out eth0.",
)

_text(
    "linux-vm-ipv6", "ra-config", NET,
    "/etc/dnsmasq.d/ra-{n}.conf",
    "Router advertisements for the walkthrough prefix already work. A second dnsmasq snippet, named in the practice note, still has RA commented out. It should contain the enable-ra line from the note.",
    "Hosts on the second segment never learn a prefix. A dnsmasq snippet still has RA commented out. /root/RA-WANT has the line that snippet should contain.",
    "{path} must contain {value}",
    "A dnsmasq snippet still has router advertisements commented out. /root/RA-WANT has the line it should contain.",
    "ra disabled", "enable-ra",
    "# enable-ra", "dhcp-range=10.40.0.50,10.40.0.80",
)

_iptables(
    "linux-vm-firewall",
    "The walkthrough host already accepts TCP 22 from 10.20.0.50. A new admin workstation needs SSH and its address is in the practice note. Append an INPUT rule that accepts TCP 22 from that address only. Do not set the policy to ACCEPT.",
    "SSH from the new admin host is still dropped. The address that must be allowed is in /root/ADMIN-IP. Accept TCP 22 from that host on INPUT. Do not open SSH to the world.",
    "iptables -A INPUT -p tcp -s 10.20.0.60 --dport 22 -j ACCEPT",
    "iptables -A INPUT -p tcp -s 10.20.0.61 --dport 22 -j ACCEPT",
    "Append an INPUT accept for TCP 22 from 10.20.0.60.",
    "SSH from the admin host is dropped. /root/ADMIN-IP will hold 10.20.0.61. Accept TCP 22 from that address.",
)

_iptables(
    "sec-vm-iptables",
    "The walkthrough policy is already DROP, with SSH from 10.9.1.40. The practice note names a second source that must reach TCP 8443. Append that one accept. Do not change the policy to ACCEPT.",
    "A monitoring host cannot reach TCP 8443, and nothing else should gain that port. The source that needs it is in /root/MON-IP. Append an INPUT accept for TCP 8443 from that host.",
    "iptables -A INPUT -p tcp -s 10.9.1.70 --dport 8443 -j ACCEPT",
    "iptables -A INPUT -p tcp -s 10.9.1.71 --dport 8443 -j ACCEPT",
    "Append an INPUT accept for TCP 8443 from 10.9.1.70.",
    "TCP 8443 from the monitor is dropped. /root/MON-IP names 10.9.1.71. Accept that source only.",
)

_text(
    "scn-dns-fix", "zone", NET,
    "/etc/hosts.floor-{n}",
    "The floor cannot open the intranet by name. A hosts file named in the practice note still publishes the retired address. Put the address from the note on intranet.novak.lab in that file.",
    "The intranet name still returns the retired address from a hosts file you have not fixed. /root/INTRANET-ADDR has the address that name should have.",
    "The hosts file {path} must contain this exact line: {value}",
    "The intranet name is still wrong in a different hosts file. /root/INTRANET-ADDR has the single hosts line to publish.",
    "10.30.0.99 intranet.novak.lab", "10.30.0.80 intranet.novak.lab",
    "10.30.0.98 intranet.novak.lab", "10.30.0.82 intranet.novak.lab",
)

_text(
    "linux-vm-perf", "sysctl-text", [("Sysctl", "sysctl <key>=<value>"), ("Show memory", "free")],
    "/etc/sysctl.d/99-swap-{n}.conf",
    "You already found what was burning CPU. This host still swaps because a sysctl file, named in the practice note, sets vm.swappiness to 60. The note has the line it should contain instead.",
    "The host is swapping under ordinary load. A sysctl drop-in still sets swappiness to 60. /root/SWAP-WANT has the line that file should contain.",
    "{path} must contain {value}",
    "Swappiness is still 60 in a sysctl drop-in. /root/SWAP-WANT has the line it should contain.",
    "vm.swappiness=60", "vm.swappiness=10",
    "vm.swappiness=80", "vm.swappiness=1",
)


def _also(lid, stage, extra):
    row = SK.SPECS[lid]["stages"][stage]
    original = row["plant"]
    row["plant"] = lambda f, original=original, extra=extra: list(original(f)) + list(extra(f))


_also("linux-vm-logs", "ticket", lambda f: ["mkdir -p /root/evidence", f"printf '%s\\n' '{f['s3_good']}' > /root/evidence/TOP"])
_also("linux-vm-nat", "ticket", lambda f: ["mkdir -p /root", "printf '%s\\n' '10.9.8.0/24' > /root/NAT-NET"])
_also("linux-vm-firewall", "ticket", lambda f: ["mkdir -p /root", "printf '%s\\n' '10.20.0.61' > /root/ADMIN-IP"])
_also("sec-vm-iptables", "ticket", lambda f: ["mkdir -p /root", "printf '%s\\n' '10.9.1.71' > /root/MON-IP"])


def _absent_pair(lid, checker, p2, p3, s2_prose, s3_prose, s2_note, s3_note):
    def enrich(f, seed):
        n = 1400 + (seed * 13) % 5000
        f["s2_path"] = p2.format(n=n)
        f["s3_path"] = p3.format(n=n)

    def plant(key):
        def run(f):
            path = f[key]
            parent = path.rsplit("/", 1)[0]
            return [f"mkdir -p {parent}", f"printf '%s\\n' 'still-running' > {path}", f"chmod 755 {path}"]
        return run

    def fix(key):
        def run(f):
            return [f"rm -f {f[key]}"]
        return run

    def checks(key):
        def run(f):
            return [{"kind": "absent", "path": f[key]}]
        return run

    SK.SPECS[lid] = {
        "syntax": [("Remove a file", "rm -f <path>"), ("See processes", "ps")],
        "enrich": enrich,
        "stages": {
            "assisted": {"checker": checker, "prose": s2_prose, "note": lambda f: s2_note.format(path=f["s2_path"]),
                         "plant": plant("s2_path"), "fix": fix("s2_path"), "checks": checks("s2_path")},
            "ticket": {"checker": checker, "prose": s3_prose, "note": lambda f: s3_note.format(path=f["s3_path"]),
                       "plant": plant("s3_path"), "fix": fix("s3_path"), "checks": checks("s3_path")},
        },
    }


_absent_pair(
    "sec-vm-proc", "process-gone",
    "/var/tmp/.cache/beacon-{n}", "/var/tmp/.font/agent-{n}",
    "The walkthrough beacon is gone. A second program is still on disk under the cache directory. The practice note names it. Remove that file. Stopping a status word is not the check.",
    "A different program is still on disk under /var/tmp/.font. It is not the beacon you just removed. Delete that file so the process cannot be started again.",
    "Remove {path}. The process file itself has to be gone.",
    "Remove {path}. The agent file has to be gone.",
)
_absent_pair(
    "sec-vm-harden", "process-gone",
    "/usr/local/sbin/extra-{n}", "/var/tmp/listener-{n}",
    "The walkthrough extra process is stopped. Another executable is still in /usr/local/sbin. The practice note names it. Remove the file.",
    "A listener binary is still under /var/tmp. It is not the program you just removed. Delete it.",
    "Remove {path}.",
    "Remove {path}.",
)

_file(
    "sec-openssl", "key-mode", PERM, "/root/pki", "server-{n}.key", "client-{n}.key",
    "server.key from the walkthrough is already private. A second key, named in the practice note, is mode 644, so every account can read it. Make it mode 600.",
    "A client key in /root/pki is still readable by other accounts. It is not the server key you just closed. Make that key mode 600.",
    "Key: {path}. Required mode: {mode}. Others must not be able to read it.",
    "The other key in {directory} is still world-readable. It should be mode 600.",
    "644", "600", "644", "600",
)

def _digest(lid, path_tmpl, s2_bad, s2_good, s3_bad, s3_good, s2_prose, s3_prose, s2_note, s3_note, clue):
    """Grade the sha256 of the file, which is what sha256sum prints, not a status word."""
    import hashlib

    def dig(text):
        return hashlib.sha256((text + "\n").encode()).hexdigest()

    def enrich(f, seed):
        n = 1100 + (seed * 23) % 7000
        f["s2_path"] = path_tmpl.format(n=n)
        f["s3_path"] = _sibling(f["s2_path"])
        f["s2_good"] = s2_good
        f["s3_good"] = s3_good
        f["s2_digest"] = dig(s2_good)
        f["s3_digest"] = dig(s3_good)

    def plant(bad, key):
        def run(f):
            path = f[key]
            parent = path.rsplit("/", 1)[0]
            return [f"mkdir -p {parent}", f"printf '%s\\n' '{_q(bad)}' > {path}"]
        return run

    def fix(good_key, path_key):
        def run(f):
            return [f"printf '%s\\n' '{_q(f[good_key])}' > {f[path_key]}"]
        return run

    def checks(digest_key, path_key):
        def run(f):
            return [{"kind": "sha256", "path": f[path_key], "digest": f[digest_key]}]
        return run

    SK.SPECS[lid] = {
        "syntax": FILE + [("Check a sum", "sha256sum <file>")],
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": "checksum", "prose": s2_prose,
                "note": lambda f: s2_note.format(path=f["s2_path"], value=f["s2_digest"]),
                "plant": plant(s2_bad, "s2_path"), "fix": fix("s2_good", "s2_path"),
                "checks": checks("s2_digest", "s2_path"),
            },
            "ticket": {
                "checker": "checksum", "prose": s3_prose,
                "note": lambda f: s3_note.format(path=f["s3_path"]),
                "plant": plant(s3_bad, "s3_path"), "fix": fix("s3_good", "s3_path"),
                "checks": checks("s3_digest", "s3_path"),
            },
        },
    }
    _also(lid, "ticket", lambda f, clue=clue: [
        f"mkdir -p {clue.rsplit('/', 1)[0]}",
        f"printf '%s\\n' '{f['s3_digest']}' > {clue}",
    ])


_digest(
    "sec-vm-hash", "/opt/app/build-{n}.bin",
    "TAMPERED-BUILD", "GOOD-BUILD-v1", "TAMPERED-PLUGIN", "GOOD-PLUGIN-v2",
    "The walkthrough image now matches its sum. A second file, named in the practice note, still hashes to the tampered build. Replace it with the payload whose sha256 is in the note.",
    "A plugin image under /opt/app still hashes to the tampered bytes. It is not the file you repaired. sha256sum of that file has to match the digest in /root/HASH-WANT.",
    "File {path} must sha256 to {value}.",
    "The plugin image still does not match its sum. /root/HASH-WANT has the digest. The path is {path}.",
    "/root/HASH-WANT",
)
_digest(
    "sec-vm-fim", "/srv/bin/tool-{n}",
    "echo tampered", "echo ok-a", "echo tampered-b", "echo ok-b",
    "The walkthrough baseline matches. A second tool, named in the practice note, does not. Replace it so its sha256 is the digest in the note.",
    "Another tool under /srv/bin does not match its baseline. /root/FIM-WANT has the sha256 that file must have.",
    "File {path} must sha256 to {value}.",
    "A tool still does not match its baseline. /root/FIM-WANT has the digest. The path is {path}.",
    "/root/FIM-WANT",
)
_digest(
    "sec-vm-backup", "/root/keep/archive-{n}.bin",
    "BAD-ARCHIVE", "GOOD-ARCHIVE-v1", "BAD-NIGHT", "GOOD-ARCHIVE-v2",
    "The walkthrough archive matches its sum. A second archive, named in the practice note, does not. Replace the bytes so sha256sum matches the digest in the note.",
    "The night archive does not match the sum that was recorded when it was written. /root/SHA-WANT has that digest. The archive file is not the one you already repaired.",
    "File {path} must sha256 to {value}.",
    "The night archive still fails its sum. /root/SHA-WANT has the digest. The path is {path}.",
    "/root/SHA-WANT",
)


def _drop_account(lid, stage, bad):
    key = "s2_path" if stage == "assisted" else "s3_path"
    row = SK.SPECS[lid]["stages"][stage]
    original = row["checks"]

    def checks(f, original=original, bad=bad, key=key):
        return list(original(f)) + [{"kind": "not_contains", "path": f[key], "text": bad}]

    row["checks"] = checks


_drop_account("linux-vm-incident", "assisted", "backdoor:x:0:0:backdoor:/root:/bin/sh")
_drop_account("linux-vm-incident", "ticket", "ghost:x:0:0:ghost:/root:/bin/sh")


def _clue(lid, path):
    _also(lid, "ticket", lambda f, path=path: [
        f"mkdir -p {path.rsplit('/', 1)[0]}",
        f"printf '%s\\n' '{_q(f['s3_good'])}' > {path}",
    ])


for _lid, _path in (
    ("linux-vm-services", "/root/DAEMON-PATH"),
    ("linux-vm-netclient", "/root/RESOLVER"),
    ("linux-vm-dns", "/root/INTRANET-ADDR"),
    ("linux-vm-logs", "/root/evidence/TOP"),
    ("sec-vm-authlog", "/root/ir/TOP"),
    ("sec-vm-grep", "/root/case/WANT"),
    ("linux-vm-method", "/root/DOCROOT"),
    ("linux-vm-web", "/root/ADDR-WANT"),
    ("linux-vm-disk", "/root/FSTAB-WANT"),
    ("linux-vm-ssh", "/root/SSHD-WANT"),
    ("sec-vm-ssh", "/root/SSHD-WANT"),
    ("linux-vm-users", "/root/GROUP-WANT"),
    ("sec-vm-users", "/root/SHADOW-WANT"),
    ("sec-vm-faillock", "/root/AGE-WANT"),
    ("linux-vm-script", "/root/SCRIPT-WANT"),
    ("linux-vm-packages", "/root/REPO-WANT"),
    ("linux-vm-ipv6", "/root/RA-WANT"),
    ("scn-dns-fix", "/root/INTRANET-ADDR"),
    ("linux-vm-perf", "/root/SWAP-WANT"),
    ("sec-vm-cron", "/root/CRON-WANT"),
    ("sec-vm-capture", "/root/case/ODD-WANT"),
    ("sec-vm-timeline", "/root/case/ORDER-WANT"),
    ("linux-vm-restore", "/root/RESTORE-WANT"),
    ("linux-vm-incident", "/root/UID0-NAME"),
):
    _clue(_lid, _path)

# The incident clue names the extra account, not the root line the file must keep.
_also("linux-vm-incident", "ticket", lambda f: ["mkdir -p /root", "printf '%s\\n' 'ghost' > /root/UID0-NAME"])
_text(
    "linux-vm-restore", "restore", FILE,
    "/srv/share/finance/budget-{n}.csv",
    "The walkthrough restore is in place. A budget file named in the practice note still has the broken copy. Replace it with the restored row from the note.",
    "The HR rota file is still the broken copy. It is not the budget file. /root/RESTORE-WANT has the row that file should contain.",
    "{path} must contain {value}",
    "The rota file still has the broken copy. /root/RESTORE-WANT has the restored row.",
    "broken-budget", "quarter,amount",
    "broken-rota", "Mon,front-desk",
)
