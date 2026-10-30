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


def _text(lid, checker, syntax, path_tmpl, s2_prose, s3_prose, s2_note, s3_note, s2_bad, s2_good, s3_bad, s3_good):
    def enrich(f, seed):
        n = 1000 + (seed * 19) % 8000
        f["tx_path"] = path_tmpl.format(n=n)
        f["s2_good"] = s2_good
        f["s3_good"] = s3_good

    def plant(bad):
        def run(f):
            path = f["tx_path"]
            parent = path.rsplit("/", 1)[0]
            return [f"mkdir -p {parent}", f"printf '%s\\n' '{_q(bad)}' > {path}"]
        return run

    def fix(good_key):
        def run(f):
            return [f"printf '%s\\n' '{_q(f[good_key])}' > {f['tx_path']}"]
        return run

    def checks(good_key):
        def run(f):
            return [{"kind": "contains", "path": f["tx_path"], "text": f[good_key]}]
        return run

    SK.SPECS[lid] = {
        "syntax": syntax,
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": checker, "prose": s2_prose,
                "note": lambda f: s2_note.format(path=f["tx_path"], value=f["s2_good"]),
                "plant": plant(s2_bad), "fix": fix("s2_good"), "checks": checks("s2_good"),
            },
            "ticket": {
                "checker": checker, "prose": s3_prose,
                "note": lambda f: s3_note.format(path=f["tx_path"], value=f["s3_good"]),
                "plant": plant(s3_bad), "fix": fix("s3_good"), "checks": checks("s3_good"),
            },
        },
    }


def _route(lid, s2_prose, s3_prose):
    def enrich(f, seed):
        f["s2_hop"] = f"10.{20 + (seed % 50)}.{seed % 200}.1"
        f["s3_hop"] = f"10.{30 + (seed % 40)}.{(seed * 3) % 200}.1"
        if f["s3_hop"] == f["s2_hop"]:
            f["s3_hop"] = "10.44.44.1"

    SK.SPECS[lid] = {
        "syntax": NET,
        "enrich": enrich,
        "stages": {
            "assisted": {
                "checker": "route",
                "prose": s2_prose,
                "note": lambda f: f"This host has no usable default route. The next hop to install is {f['s2_hop']}.",
                "plant": lambda f: [],
                "fix": lambda f: [f"ip route add default via {f['s2_hop']}"],
                "checks": lambda f: [{"kind": "route", "hop": f["s2_hop"]}],
            },
            "ticket": {
                "checker": "route",
                "prose": s3_prose,
                "note": lambda f: "Hosts beyond this subnet time out. The default route is missing. The next hop is written on the first line of /root/NEXT-HOP.",
                "plant": lambda f: ["mkdir -p /root", f"printf '%s\\n' '{f['s3_hop']}' > /root/NEXT-HOP"],
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


def _iptables(lid, s2_prose, s3_prose, s2_fragment, s3_fragment, s2_note, s3_note):
    SK.SPECS[lid] = {
        "syntax": FILTER,
        "enrich": lambda f, seed: f.update(frag2=s2_fragment, frag3=s3_fragment),
        "stages": {
            "assisted": {
                "checker": "iptables",
                "prose": s2_prose,
                "note": lambda f: s2_note,
                "plant": lambda f: [],
                "fix": lambda f: [s2_fragment if s2_fragment.startswith("iptables") else f"iptables {s2_fragment}"],
                "checks": lambda f: [{"kind": "iptables", "fragment": s2_fragment if s2_fragment.startswith("iptables") else s2_fragment}],
            },
            "ticket": {
                "checker": "iptables",
                "prose": s3_prose,
                "note": lambda f: s3_note,
                "plant": lambda f: [],
                "fix": lambda f: [s3_fragment if s3_fragment.startswith("iptables") else f"iptables {s3_fragment}"],
                "checks": lambda f: [{"kind": "iptables", "fragment": s3_fragment}],
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
    "linux-vm-perms", "mode-owner", PERM, "/root/support", "payroll-{n}.txt", "handoff-{n}.txt",
    "tech1 can read the walkthrough notes, and a new payroll export cannot. It was created by root as mode 666. The practice note names the file. It has to be mode 640 and owned by tech1. Do not loosen the original notes file.",
    "The night technician cannot save the handoff, but every other account can rewrite it. The file is the one under /root/support that is still world-writable. tech1 should own it, and others should not be able to change it. The payroll file from practice is already correct.",
    "File: {path}. Mode: {mode}. Owner: {owner}.",
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
    "DAEMON=/usr/local/sbin/heartbeat", "DAEMON=/usr/local/bin/heartbeat",
)

_text(
    "linux-vm-netclient", "resolv", NET,
    "/etc/resolv.lab-{n}.conf",
    "The lease you already took pointed this client at 10.10.0.53. A second resolver file, named in the practice note, still lists a retired server. Replace that nameserver line with the address in the note. Do not release the address you already have.",
    "Names on this client fail and addresses answer. The resolver file that is not the walkthrough resolv.conf still names a server that does not hold the zone. The address that should be there is the only line in /root/RESOLVER.",
    "File {path} must contain this line: {value}",
    "Name lookups use a resolver file that still points at a retired server. Read /root/RESOLVER and make the nameserver line match it.",
    "nameserver 10.9.9.9", "nameserver 10.10.0.53",
    "nameserver 10.1.1.1", "nameserver 10.10.0.53",
)

_text(
    "linux-vm-dns", "zone", FILE + NET,
    "/etc/hosts.novak-{n}",
    "The walkthrough zone already returns the new intranet address. A second hosts file, named in the practice note, still maps intranet.novak.lab to the retired address. Put the address from the note on that name. Do not break the resolver you already pointed at 10.30.0.53.",
    "intranet.novak.lab still answers with the old address from a hosts file that is not the one you edited in practice. The address it should have now is the only line in /root/INTRANET-ADDR.",
    "In {path}, intranet.novak.lab must resolve to {value}",
    "The intranet name still points at the retired server in a hosts file under /etc. /root/INTRANET-ADDR has the address that should be published.",
    "10.30.0.99 intranet.novak.lab", "10.30.0.80 intranet.novak.lab",
    "10.30.0.99 intranet.novak.lab", "10.30.0.80 intranet.novak.lab",
)

_text(
    "linux-vm-logs", "log-extract", FILE,
    "/root/evidence/attacker-{n}.txt",
    "You already counted the walkthrough address. A fresh auth extract is named in the practice note, and the top source is not 203.0.113.77. Write that address, and only that address, into the file the note names.",
    "The evidence file that should name tonight's top source still has the walkthrough address. The address that actually failed most often is the only line in /root/evidence/TOP. Do not leave 203.0.113.77 in the evidence file unless TOP says that.",
    "Write this address into {path}: {value}",
    "The evidence file still has the sample address. /root/evidence/TOP has the address that failed most often. Put that address in the evidence file.",
    "203.0.113.77", "198.51.100.23",
    "203.0.113.77", "198.51.100.23",
)

_text(
    "sec-vm-authlog", "log-extract", FILE,
    "/root/ir/source-{n}.txt",
    "The walkthrough source file already has 203.0.113.44. A second source file, named in the practice note, still says unknown. The address with the most failures in this attempt is in the note. Write that address and nothing else.",
    "The IR directory still has a source file that says unknown, and the account file from the walkthrough is not the one that is wrong. Tonight's top source is the only address in /root/ir/TOP.",
    "Write {value} into {path}.",
    "A source file in /root/ir still says unknown. /root/ir/TOP has the address that actually failed most often.",
    "unknown", "203.0.113.50",
    "unknown", "203.0.113.50",
)

_text(
    "sec-vm-grep", "log-extract", FILE,
    "/root/case/hits-{n}.txt",
    "The walkthrough extract already has the SR-4419 lines. A second case file, named in the practice note, is empty. It should contain the one-line marker from the note and must not contain the backup warning.",
    "The case file that is still empty should hold the SR marker and must not pick up the backup warning. The marker text is the only line in /root/case/WANT.",
    "{path} must contain {value} and must not contain the backup warning.",
    "An empty hits file in /root/case is waiting for the marker stored in /root/case/WANT. Do not copy the backup warning into it.",
    "", "SR-4419 disk",
    "", "SR-4419 disk",
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
    "DOCROOT=/var/oldclock", "DOCROOT=/srv/timeclock",
)

_text(
    "linux-vm-web", "config-text", FILE,
    "/etc/default/intranet-{n}",
    "The walkthrough service already listens on all addresses. A second defaults file, named in the practice note, still says ADDR=127.0.0.1, so only local clients can connect. Set the ADDR line from the note.",
    "Remote clients still cannot open the intranet because a defaults file binds the listener to loopback. It is not the file you changed in practice. /root/ADDR-WANT has the line that should be in the file.",
    "{path} must contain {value}",
    "A listener config still binds to loopback. /root/ADDR-WANT has the ADDR line it should contain.",
    "ADDR=127.0.0.1", "ADDR=0.0.0.0",
    "ADDR=127.0.0.1", "ADDR=0.0.0.0",
)

_text(
    "linux-vm-disk", "fstab", FILE + [("Boot mounts", "UUID=<uuid> <mountpoint> <type> <options>")],
    "/etc/fstab.d/appdata-{n}",
    "The walkthrough mount is already in the real fstab. A drop-in named in the practice note still lists /dev/sda1, which will move when disks enumerate differently. Replace that line with the UUID line from the note.",
    "A disk drop-in still mounts appdata by the device name, so a reboot can attach the wrong disk. It is not the line you fixed in practice. /root/FSTAB-WANT has the UUID line that should replace it.",
    "{path} must contain {value}",
    "An fstab drop-in still names /dev/sda1. /root/FSTAB-WANT has the UUID line that should be there instead.",
    "/dev/sda1 /srv/data ext4 defaults 0 2", "UUID=abc123 /srv/data ext4 defaults 0 2",
    "/dev/sda1 /srv/data ext4 defaults 0 2", "UUID=abc123 /srv/data ext4 defaults 0 2",
)

_text(
    "linux-vm-ssh", "sshd", FILE + [("Key file mode", "chmod <mode> <path>"), ("sshd test", "sshd -t")],
    "/etc/ssh/sshd_config.d/lab-{n}.conf",
    "The walkthrough daemon already refuses passwords. A drop-in named in the practice note still says PasswordAuthentication yes. Set the line from the note. Do not turn root login back on.",
    "Password login is still allowed by a drop-in that is not the one you edited. /root/SSHD-WANT has the line that should be in that drop-in.",
    "{path} must contain {value}",
    "An sshd drop-in still allows passwords. /root/SSHD-WANT has the line it should contain.",
    "PasswordAuthentication yes", "PasswordAuthentication no",
    "PasswordAuthentication yes", "PasswordAuthentication no",
)

_text(
    "sec-vm-ssh", "sshd", FILE,
    "/etc/ssh/sshd_config.d/ops-{n}.conf",
    "The walkthrough key is in place. A drop-in named in the practice note still permits root login. It should contain the PermitRootLogin line from the note.",
    "Root can still log in with a password because a drop-in says so. It is not the ops file from practice. /root/SSHD-WANT has the line that should replace it.",
    "{path} must contain {value}",
    "A drop-in still permits root login. /root/SSHD-WANT has the line it should contain.",
    "PermitRootLogin yes", "PermitRootLogin no",
    "PermitRootLogin yes", "PermitRootLogin no",
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
    "", "opsdesk:x:2400:ana,ben",
)

_text(
    "sec-vm-users", "shadow", PERM,
    "/etc/shadow.d/intern-{n}",
    "The walkthrough intern is locked. A shadow snippet named in the practice note still has an unlocked password field. Replace it with the locked line from the note. Do not delete the account.",
    "An intern shadow snippet still has a usable password hash. It is not the account you locked in the walkthrough. /root/SHADOW-WANT has the locked line that should replace it.",
    "{path} must contain {value}",
    "A shadow snippet still allows a password. /root/SHADOW-WANT has the locked line it should contain.",
    "intern:$6$hash:19000:0:99999:7:::", "intern:!:19000:0:99999:7:::",
    "intern:$6$hash:19000:0:99999:7:::", "intern:!:19000:0:99999:7:::",
)

_text(
    "sec-vm-faillock", "shadow-age", PERM + [("Password age", "chage -m <min> -M <max> <user>")],
    "/etc/shadow.d/age-{n}",
    "The walkthrough account already has a maximum age. A shadow snippet named in the practice note still has minimum 0 and maximum 99999. Replace it with the aged line from the note.",
    "A shadow snippet still allows a password to be changed immediately and to live forever. /root/AGE-WANT has the line with a 14 day minimum and a 90 day maximum.",
    "{path} must contain {value}",
    "Password aging is still unset in a shadow snippet. /root/AGE-WANT has the line it should contain.",
    "contractor:$6$hash:19000:0:99999:7:::", "contractor:$6$hash:19000:14:90:7:::",
    "contractor:$6$hash:19000:0:99999:7:::", "contractor:$6$hash:19000:14:90:7:::",
)

_text(
    "linux-vm-script", "script", PERM + FILE,
    "/usr/local/bin/status-{n}.sh",
    "app-backup.sh already exits 2 when the arguments are missing. A second script, named in the practice note, has no shebang and is not the backup script. It should be the one-line script in the note.",
    "A script under /usr/local/bin still has no shebang, so the kernel will not run it as a shell script. It is not app-backup.sh. /root/SCRIPT-WANT has the line the file should contain.",
    "{path} must contain {value}",
    "A script is still missing its shebang. /root/SCRIPT-WANT has the line it should start with.",
    "echo nope", "#!/bin/sh",
    "echo nope", "#!/bin/sh",
)

_text(
    "linux-vm-packages", "repo", FILE,
    "/etc/apk/repositories-{n}",
    "The walkthrough repo line is already active. A second repositories file, named in the practice note, still has the repo commented out. The file should contain the uncommented line from the note.",
    "A repositories file still has the local repo commented out, so the package index will not include it. /root/REPO-WANT has the line that should be present.",
    "{path} must contain {value}",
    "The local repository is still commented out in a repositories file. /root/REPO-WANT has the line that should be there.",
    "repo none", "/var/lib/novak-repo",
    "repo none", "/var/lib/novak-repo",
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
    "{path} must not contain the account named in the note. Write the single word gone as {value} once that account line is gone, into this same file, replacing its contents.",
    "An extra UID 0 account is still listed. /root/UID0-NAME names it. The snippet should end up containing only the word gone.",
    "backdoor:x:0:0:backdoor:/root:/bin/sh", "gone",
    "backdoor:x:0:0:backdoor:/root:/bin/sh", "gone",
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
    "", "198.51.100.77",
)

_text(
    "sec-vm-timeline", "log-extract", FILE,
    "/root/case/order-{n}.txt",
    "The walkthrough timeline is in order. A second file, named in the practice note, lists the later failure first. Replace it with the single line from the note, which has the earlier failure first.",
    "A timeline file still leads with the later failure. /root/case/ORDER-WANT has the line that puts the earlier failure first.",
    "{path} must contain {value}",
    "The timeline file still has the later failure first. /root/case/ORDER-WANT has the line it should contain.",
    "12:10 failed login", "12:02 failed login",
    "12:10 failed login", "12:02 failed login",
)

_text(
    "sec-vm-cron", "crontab-text", CRON,
    "/root/cron.clean-{n}",
    "The walkthrough crontab no longer has the hidden sync job. A table file named in the practice note still contains that job and is missing the logrotate line. The note has the line the file should contain.",
    "A crontab file still schedules the hidden sync and never runs logrotate. /root/CRON-WANT has the only line that file should contain.",
    "{path} must contain {value}",
    "A crontab file still has the hidden job. /root/CRON-WANT has the line it should contain instead.",
    "* * * * * /var/tmp/.font/sync.sh", "15 3 * * * /usr/local/bin/logrotate-local",
    "* * * * * /var/tmp/.font/sync.sh", "15 3 * * * /usr/local/bin/logrotate-local",
)

_cron(
    "linux-vm-cron",
    "crond is already running from the walkthrough. Root's crontab does not yet contain the weekday cleanup named in the practice note. Install that one line. Leave the 02:30 backup job if it is already there, but the check for this stage is the cleanup line.",
    "The cleanup did not run this morning. Root's crontab still has a comment where the job should be. The schedule that should be installed is the only line in /root/CRON-WANT.",
    "20 1 * * 1-5 /usr/local/bin/cleanup.sh",
    "20 1 * * 1-5 /usr/local/bin/cleanup.sh",
)

_route(
    "linux-vm-routing",
    "Forwarding between the walkthrough LANs already works. This host, the one named in the practice note, has no default route, so anything off its own subnet dies here. Install the next hop from the note. Do not remove the connected routes you already added.",
    "A PC on the near LAN can ping its router and nothing past it. The default route is missing. The next hop is not the walkthrough address. Read /root/NEXT-HOP and install that route.",
)

_route(
    "linux-vm-nettrouble",
    "The multi-hop path from the walkthrough reaches the far host. This attempt's client has no default route at all, which is why its pings never leave the subnet. The practice note has the next hop. Install it.",
    "Pings to the far host die on this client and the routing table has no default. The hop you should use is in /root/NEXT-HOP, not the address from the walkthrough.",
)

_route(
    "scn-lan2-fix",
    "LAN 2's PCs get nowhere past the router because this client has no default route. The practice note has the next hop that should be installed. This is not the proof file from another lab.",
    "The CFO's side of LAN 2 still cannot reach the ERP host. This router-facing client has no default route. /root/NEXT-HOP has the hop.",
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
    "ra disabled", "enable-ra",
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
    "{path} must map the intranet name to {value}",
    "The intranet name is still wrong in a hosts file. /root/INTRANET-ADDR has the address to publish.",
    "10.30.0.99 intranet.novak.lab", "10.30.0.80 intranet.novak.lab",
    "10.30.0.99 intranet.novak.lab", "10.30.0.80 intranet.novak.lab",
)

_text(
    "linux-vm-perf", "sysctl-text", [("Sysctl", "sysctl <key>=<value>"), ("Show memory", "free")],
    "/etc/sysctl.d/99-swap-{n}.conf",
    "You already found what was burning CPU. This host still swaps because a sysctl file, named in the practice note, sets vm.swappiness to 60. The note has the line it should contain instead.",
    "The host is swapping under ordinary load. A sysctl drop-in still sets swappiness to 60. /root/SWAP-WANT has the line that file should contain.",
    "{path} must contain {value}",
    "Swappiness is still 60 in a sysctl drop-in. /root/SWAP-WANT has the line it should contain.",
    "vm.swappiness=60", "vm.swappiness=10",
    "vm.swappiness=60", "vm.swappiness=10",
)


def _also(lid, stage, extra):
    row = SK.SPECS[lid]["stages"][stage]
    original = row["plant"]
    row["plant"] = lambda f, original=original, extra=extra: list(original(f)) + list(extra(f))


_also("linux-vm-logs", "ticket", lambda f: ["mkdir -p /root/evidence", f"printf '%s\\n' '{f['s3_good']}' > /root/evidence/TOP"])
_also("linux-vm-nat", "ticket", lambda f: ["mkdir -p /root", "printf '%s\\n' '10.9.8.0/24' > /root/NAT-NET"])
_also("linux-vm-firewall", "ticket", lambda f: ["mkdir -p /root", "printf '%s\\n' '10.20.0.61' > /root/ADMIN-IP"])
_also("sec-vm-iptables", "ticket", lambda f: ["mkdir -p /root", "printf '%s\\n' '10.9.1.71' > /root/MON-IP"])
