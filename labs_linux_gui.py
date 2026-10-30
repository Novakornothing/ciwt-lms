"""Live Linux desktop labs.

The page boots a real guest (tools/vm_gui) in v86: Fluxbox, a file manager, a text editor,
a terminal, and a settings tool, on the VGA framebuffer. Grading uses the same 9p probe as
the terminal VM labs and looks at files, accounts, iptables, and processes — not at clicks.

Per-session values live in state['gui_vars']. Stage 1 of each lab teaches fixed values.
Stages 2 and 3 only say where to read the live ticket. The probe compares the guest to
gui_vars, which are not rendered in the lab text.
"""
from __future__ import annotations

import random
from copy import deepcopy


def linux_gui_state() -> dict:
    """Kept so older callers still receive a dict. The live labs do not grade this."""
    return {"win": "desktop", "seen": [], "log": []}


def public_gui(state: dict) -> dict:
    g = deepcopy((state or {}).get("linuxgui") or linux_gui_state())
    g.pop("seen", None)
    return g


def apply(lab: dict, state: dict, done: list, ev: str, data: dict):
    return {"ok": "This lab is graded from the live desktop. Press Check my work.", "changed": False}, state, done


GUI_VM = {
    "image": "novak-gui.bin",
    "state": "novak-gui.state.gz",
    "download_mb": 48,
    "memory_mb": 192,
    "vga_mb": 8,
    "prompt_re": r"[#%$] $",
    "cmdline": "console=ttyS0,115200 tsc=reliable mitigations=off random.trust_cpu=on video=800x600",
    "machines": [{"name": "vm", "label": "Linux desktop", "hostname": "novak-lnx-01", "segs": [], "memory_mb": 192}],
}

_USERS = ["alex", "sam", "riley", "casey", "morgan"]
_PROCS = ["backup-job", "index-worker", "log-ship", "cache-warm"]
_PKGS = ["nano", "htop"]
_MODES = ["640", "600", "750", "740"]
_PORTS = ["8080", "8443", "2222", "993", "587"]
_MNTS = ["/srv/share", "/srv/archive", "/srv/files", "/srv/drop"]
_OPTS = ["defaults,nofail", "defaults,noatime", "defaults,ro,nofail"]
_SSH_USERS = ["ops", "auditor", "backup"]


def _ls_mode(mode: str) -> str:
    bits = int(mode, 8)
    out = "-"
    for i in range(9):
        out += "rwxrwxrwx"[i] if bits & (0o400 >> i) else "-"
    return out


def _net(rng):
    b = rng.randint(16, 40)
    c = rng.randint(1, 250)
    host = rng.choice([h for h in range(20, 220) if h not in (1, 10)])
    return {"ip": f"10.{b}.{c}.{host}", "prefix": "24", "gw": f"10.{b}.{c}.1", "dns": f"10.{b}.{c}.10"}


def gui_vars(seed: int) -> dict:
    rng = random.Random(int(seed))
    s2, s3 = _net(rng), _net(rng)
    while s3["ip"] == s2["ip"]:
        s3 = _net(rng)
    users = rng.sample(_USERS, 2)
    procs = rng.sample(_PROCS, 2)
    modes = rng.sample(_MODES, 2)
    mnts = rng.sample(_MNTS, 2)
    opts = rng.sample(_OPTS, 2)
    return {
        "s2_ip": s2["ip"], "s2_prefix": s2["prefix"], "s2_gw": s2["gw"], "s2_dns": s2["dns"],
        "s3_ip": s3["ip"], "s3_prefix": s3["prefix"], "s3_gw": s3["gw"], "s3_dns": s3["dns"],
        "s2_user": users[0], "s3_user": users[1],
        "s2_mode": modes[0], "s3_mode": modes[1],
        "s2_ls": _ls_mode(modes[0]), "s3_ls": _ls_mode(modes[1]),
        "s2_path": f"/root/work/{users[0]}.sh",
        "s3_path": f"/root/work/{users[1]}.sh",
        "s2_mnt": mnts[0], "s3_mnt": mnts[1],
        "s2_opts": opts[0], "s3_opts": opts[1],
        "s2_port": rng.choice(_PORTS),
        "s2_ban": f"203.0.113.{rng.randint(10, 240)}",
        "s3_ban": f"198.51.100.{rng.choice([i for i in range(10, 250) if i != 77])}",
        "s2_proc": procs[0], "s3_proc": procs[1],
        "s2_pkg": rng.choice(_PKGS),
        "s3_min": str(rng.randint(5, 55)),
        "s3_cmd": "/usr/local/bin/backup-verify.sh",
        "s2_ssh_user": rng.choice(_SSH_USERS),
        "s3_port": str(rng.randint(2200, 2299)),
        "ticket": str(rng.randint(1000, 9999)),
    }


def _fill(text: str, vars_: dict) -> str:
    for key, val in (vars_ or {}).items():
        text = text.replace("{{" + key + "}}", str(val))
    return text


_SETUPS = {
    "linux-gui-network": r"""
mkdir -p /root/Desktop
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 ticket — save a Settings profile named practice. Do not apply it live.
Address: {{s2_ip}}
Prefix: {{s2_prefix}}
Gateway: {{s2_gw}}
DNS: {{s2_dns}}
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}} — apply this address live on eth0.
Address: {{s3_ip}}
Prefix: {{s3_prefix}}
Gateway: {{s3_gw}}
DNS: {{s3_dns}}
EOF
""",
    "linux-gui-disks": r"""
mkdir -p /root/Desktop
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 — mount the extra disk image and record it in /etc/fstab.
Image: /var/lib/novak/extra.img
Mount point: {{s2_mnt}}
Options: {{s2_opts}}
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}} — mount the ticket image.
Image: /var/lib/novak/ticket.img
Mount point: {{s3_mnt}}
Options: {{s3_opts}}
EOF
""",
    "linux-gui-firewall": r"""
mkdir -p /root/Desktop
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 — allow this TCP port through the firewall.
Port: {{s2_port}}
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}} — drop every packet from this address.
Address: {{s3_ban}}
EOF
""",
    "linux-gui-users": r"""
mkdir -p /root/Desktop /root/support /root/work
id tech1 >/dev/null 2>&1 || useradd -m -s /bin/sh tech1
echo 'tech1:LabPass1' | chpasswd
passwd -l tech1
printf '%s\n' '#!/bin/sh' 'echo backup' > /root/support/backup.sh
chmod 644 /root/support/backup.sh
id {{s2_user}} >/dev/null 2>&1 || useradd -m -s /bin/sh {{s2_user}}
echo '{{s2_user}}:LabPass1' | chpasswd
passwd -l {{s2_user}}
printf '%s\n' '#!/bin/sh' 'echo work' > {{s2_path}}
chmod 644 {{s2_path}}
id {{s3_user}} >/dev/null 2>&1 || useradd -m -s /bin/sh {{s3_user}}
echo '{{s3_user}}:LabPass1' | chpasswd
passwd -l {{s3_user}}
printf '%s\n' '#!/bin/sh' 'echo work' > {{s3_path}}
chmod 644 {{s3_path}}
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 — unlock this account, grant sudo, and set the file mode.
Account: {{s2_user}}
File: {{s2_path}}
Mode: {{s2_mode}}
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}}
Account: {{s3_user}}
File: {{s3_path}}
Mode: {{s3_mode}}
EOF
""",
    "linux-gui-logs": r"""
mkdir -p /root/Desktop /var/log
{
  echo 'sshd: Failed password for root from 198.51.100.77'
  echo 'sshd: Failed password for root from 198.51.100.77'
  echo 'sshd: Failed password for root from 10.0.0.8'
  i=0; while [ $i -lt 12 ]; do echo "sshd: Failed password for root from {{s2_ban}}"; i=$((i+1)); done
  echo 'cron: job finished'
} > /var/log/messages
{
  echo 'sshd: Failed password for admin from {{s3_ban}}'
  echo 'sshd: Failed password for admin from {{s3_ban}}'
  echo 'sshd: Failed password for admin from {{s3_ban}}'
} > /var/log/secure
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 — the example address from the walkthrough is not the one to block.
Read /var/log/messages and block the address that failed the most.
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}}
New failures are in /var/log/secure. Block that source, then rotate /var/log/messages.
EOF
""",
    "linux-gui-processes": r"""
mkdir -p /root/Desktop /tmp
cp /usr/bin/hog /tmp/cpu-hog
cp /usr/bin/hog /tmp/{{s2_proc}}
cp /usr/bin/hog /tmp/{{s3_proc}}
chmod 755 /tmp/cpu-hog /tmp/{{s2_proc}} /tmp/{{s3_proc}}
/tmp/cpu-hog >/dev/null 2>&1 &
/tmp/{{s2_proc}} >/dev/null 2>&1 &
/tmp/{{s3_proc}} >/dev/null 2>&1 &
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 — stop the extra CPU burner named in this ticket. cpu-hog is the walkthrough process.
Name: {{s2_proc}}
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}}
One CPU burner is still running. Its name is not in this ticket.
Find it in Settings → Processes and stop it.
EOF
""",
    "linux-gui-packages": r"""
mkdir -p /root/Desktop /usr/local/bin
printf '%s\n' '#!/bin/sh' 'echo backup-verify ok' > /usr/local/bin/backup-verify.sh
chmod 755 /usr/local/bin/backup-verify.sh
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 — install this package from the local repository.
Package: {{s2_pkg}}
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}}
Enable an hourly cron job.
Minute: {{s3_min}}
Command: {{s3_cmd}}
EOF
""",
    "linux-gui-ssh": r"""
mkdir -p /root/Desktop
id {{s2_ssh_user}} >/dev/null 2>&1 || useradd -m -s /bin/sh {{s2_ssh_user}}
echo '{{s2_ssh_user}}:LabPass1' | chpasswd
cat > /root/Desktop/stage2-ticket.txt << EOF
Stage 2 — allow only this account to sign in over SSH.
Account: {{s2_ssh_user}}
EOF
cat > /root/Desktop/INC-{{ticket}}.txt << EOF
Stage 3 incident INC-{{ticket}}
Move sshd to this port and check the configuration.
Port: {{s3_port}}
EOF
""",
}


def setup_script(lab: dict, state: dict) -> str:
    body = _SETUPS.get(lab["id"], ":\n")
    return _fill(body, (state or {}).get("gui_vars") or {}) + "\n"


def solution_commands(lab: dict, state: dict) -> list:
    v = (state or {}).get("gui_vars") or {}
    lid = lab["id"]
    if lid == "linux-gui-network":
        return [
            "novak-net save guided 10.20.40.15 24 10.20.40.1 10.20.40.10",
            f"novak-net save practice {v['s2_ip']} {v['s2_prefix']} {v['s2_gw']} {v['s2_dns']}",
            f"novak-net apply {v['s3_ip']} {v['s3_prefix']} {v['s3_gw']} {v['s3_dns']}",
        ]
    if lid == "linux-gui-disks":
        return [
            "novak-disk report /var/lib/novak/data.img",
            "novak-disk mount /var/lib/novak/data.img /srv/data defaults,nofail",
            f"novak-disk mount /var/lib/novak/extra.img {v['s2_mnt']} {v['s2_opts']}",
            f"novak-disk mount /var/lib/novak/ticket.img {v['s3_mnt']} {v['s3_opts']}",
        ]
    if lid == "linux-gui-firewall":
        return [
            "novak-fw enable", "novak-fw allow 22", "novak-fw allow 443", "novak-fw ssh",
            f"novak-fw allow {v['s2_port']}", f"novak-fw ban {v['s3_ban']}",
        ]
    if lid == "linux-gui-users":
        return [
            "novak-user unlock tech1", "novak-user sudo tech1", "chmod 750 /root/support/backup.sh",
            f"novak-user unlock {v['s2_user']}", f"novak-user sudo {v['s2_user']}", f"chmod {v['s2_mode']} {v['s2_path']}",
            f"novak-user unlock {v['s3_user']}", f"novak-user sudo {v['s3_user']}", f"chmod {v['s3_mode']} {v['s3_path']}",
        ]
    if lid == "linux-gui-logs":
        return [
            "novak-fw ban 198.51.100.77", f"novak-fw ban {v['s2_ban']}", f"novak-fw ban {v['s3_ban']}",
            "novak-log rotate",
        ]
    if lid == "linux-gui-processes":
        return [
            "novak-proc stop cpu-hog", "novak-proc swappiness 10",
            f"novak-proc stop {v['s2_proc']}", f"novak-proc stop {v['s3_proc']}",
        ]
    if lid == "linux-gui-packages":
        return [
            "novak-pkg update", "novak-pkg add darkhttpd", f"novak-pkg add {v['s2_pkg']}",
            f"novak-pkg cron {v['s3_min']} {v['s3_cmd']}",
        ]
    if lid == "linux-gui-ssh":
        return [
            "novak-ssh keygen", "novak-ssh harden", f"novak-ssh allow {v['s2_ssh_user']}",
            f"novak-ssh port {v['s3_port']}", "novak-ssh check",
        ]
    return []


def _ck(oid, sh, why, show=None, secs=4):
    row = {"id": oid, "sh": sh, "why": why, "secs": secs}
    if show:
        row["show"] = show
    return row


def _sudo_sh(user):
    return f"grep '^sudo:' /etc/group | grep -Eq '[:,]{user}(,|$)'"


def _checks():
    boot = {"id": "boot"}
    net = [
        boot,
        _ck("s1_profile",
            "grep -qx address=10.20.40.15 /etc/novak/profiles/guided.conf && grep -qx prefix=24 /etc/novak/profiles/guided.conf && grep -qx gateway=10.20.40.1 /etc/novak/profiles/guided.conf && grep -qx dns=10.20.40.10 /etc/novak/profiles/guided.conf",
            "The guided profile does not have the Stage 1 address, prefix, gateway, and DNS yet.",
            "cat /etc/novak/profiles/guided.conf 2>/dev/null || echo 'guided profile missing'"),
        _ck("s2_profile",
            "grep -qx address={{s2_ip}} /etc/novak/profiles/practice.conf && grep -qx prefix={{s2_prefix}} /etc/novak/profiles/practice.conf && grep -qx gateway={{s2_gw}} /etc/novak/profiles/practice.conf && grep -qx dns={{s2_dns}} /etc/novak/profiles/practice.conf",
            "The practice profile does not match the Stage 2 ticket on the desktop.",
            "cat /etc/novak/profiles/practice.conf 2>/dev/null || echo 'practice profile missing'"),
        _ck("s3_live",
            "grep -qx address={{s3_ip}} /etc/novak/network.conf && ip -4 addr show eth0 | grep -q '{{s3_ip}}/{{s3_prefix}}' && ip route | grep -q 'default via {{s3_gw}}' && grep -qx 'nameserver {{s3_dns}}' /etc/resolv.conf",
            "eth0 is not using the address, prefix, gateway, and DNS from the incident ticket.",
            "ip -4 addr show eth0; ip route; cat /etc/resolv.conf 2>/dev/null"),
    ]
    disks = [
        boot,
        _ck("s1_report",
            "b=$(wc -c < /var/lib/novak/data.img); b=$(echo $b); grep -qx bytes=$b /var/lib/novak/smart-report.txt",
            "The health report does not match the size of /var/lib/novak/data.img.",
            "cat /var/lib/novak/smart-report.txt 2>/dev/null || echo 'no report'"),
        _ck("s1_mount",
            "grep -q /var/lib/novak/data.img /etc/fstab && grep -q ' /srv/data ' /etc/fstab && grep -q nofail /etc/fstab && grep -q ' /srv/data ' /proc/mounts",
            "/srv/data is not mounted from data.img with nofail in /etc/fstab.",
            "grep data.img /etc/fstab; grep ' /srv/data ' /proc/mounts || echo 'not mounted'"),
        _ck("s2_mount",
            "grep -q /var/lib/novak/extra.img /etc/fstab && grep -q ' {{s2_mnt}} ' /etc/fstab && grep -q '{{s2_opts}}' /etc/fstab && grep -q ' {{s2_mnt}} ' /proc/mounts",
            "The extra image is not mounted where the Stage 2 ticket says, with those options in /etc/fstab.",
            "grep extra.img /etc/fstab || echo 'not in fstab'"),
        _ck("s3_mount",
            "grep -q /var/lib/novak/ticket.img /etc/fstab && grep -q ' {{s3_mnt}} ' /etc/fstab && grep -q '{{s3_opts}}' /etc/fstab && grep -q ' {{s3_mnt}} ' /proc/mounts",
            "The ticket image is not mounted the way the incident file describes.",
            "grep ticket.img /etc/fstab || echo 'not in fstab'"),
    ]
    fw = [
        boot,
        _ck("s1_policy",
            "iptables-save | grep -q ':INPUT DROP' && iptables-save | grep -q ':OUTPUT ACCEPT'",
            "The firewall policy is not drop-incoming and allow-outgoing yet.",
            "iptables-save | head -8"),
        _ck("s1_allow",
            "iptables-save | grep -q -- '--dport 22 ' && iptables-save | grep -q -- '--dport 443 '",
            "TCP 22 and TCP 443 are not both allowed.",
            "iptables-save | grep dport || echo 'no port rules'"),
        _ck("s1_ssh", "pidof sshd >/dev/null", "sshd is not running.", "pidof sshd || echo 'sshd stopped'", secs=6),
        _ck("s2_port",
            "iptables-save | grep -q -- '--dport {{s2_port}} '",
            "The TCP port from the Stage 2 ticket is not allowed.",
            "iptables-save | grep dport || echo 'no port rules'"),
        _ck("s3_ban",
            "iptables-save | grep -q -- '-s {{s3_ban}}' && grep -qx '{{s3_ban}}' /etc/novak/banned.list",
            "The address from the incident ticket is not dropped.",
            "grep . /etc/novak/banned.list 2>/dev/null || echo 'ban list empty'"),
    ]
    users = [
        boot,
        _ck("s1_unlock", "passwd -S tech1 | awk '{print $2}' | grep -qx P", "tech1 is still locked.", "passwd -S tech1"),
        _ck("s1_sudo", _sudo_sh("tech1"), "tech1 is not in the sudo group.", "grep '^sudo:' /etc/group"),
        _ck("s1_mode", "ls -l /root/support/backup.sh | grep -q '^-rwxr-x--- '",
            "/root/support/backup.sh is not mode 750.", "ls -l /root/support/backup.sh"),
        _ck("s2_user",
            "passwd -S {{s2_user}} | awk '{print $2}' | grep -qx P && " + _sudo_sh("{{s2_user}}").replace("{{s2_user}}", "{{s2_user}}"),
            "The Stage 2 account is not both unlocked and in the sudo group.",
            "echo stage2"),
        _ck("s2_mode", "ls -l {{s2_path}} | grep -q '^{{s2_ls}} '",
            "The Stage 2 file does not have the mode written in the ticket.",
            "ls -l {{s2_path}}"),
        _ck("s3_user",
            "passwd -S {{s3_user}} | awk '{print $2}' | grep -qx P && " + _sudo_sh("{{s3_user}}"),
            "The incident account is not both unlocked and in the sudo group.",
            "echo stage3"),
        _ck("s3_mode", "ls -l {{s3_path}} | grep -q '^{{s3_ls}} '",
            "The incident file does not have the mode written in the ticket.",
            "ls -l {{s3_path}}"),
    ]
    # fix s2_user sh — the replace above is a no-op mess. Rebuild cleanly below.
    logs = [
        boot,
        _ck("s1_ban", "grep -qx 198.51.100.77 /etc/novak/banned.list && iptables-save | grep -q -- '-s 198.51.100.77'",
            "198.51.100.77 from the walkthrough is not blocked.", "grep . /etc/novak/banned.list 2>/dev/null || echo empty"),
        _ck("s2_ban", "grep -qx {{s2_ban}} /etc/novak/banned.list && iptables-save | grep -q -- '-s {{s2_ban}}'",
            "The address that fails most often in /var/log/messages is not blocked.",
            "grep . /etc/novak/banned.list 2>/dev/null || echo empty"),
        _ck("s3_ban", "grep -qx {{s3_ban}} /etc/novak/banned.list && iptables-save | grep -q -- '-s {{s3_ban}}'",
            "The source address in /var/log/secure is not blocked.",
            "grep . /etc/novak/banned.list 2>/dev/null || echo empty"),
        _ck("s3_rotate",
            "[ -s /var/log/messages.1 ] && [ $(wc -c < /var/log/messages) -lt $(wc -c < /var/log/messages.1) ]",
            "/var/log/messages has not been rotated (a smaller live log and a messages.1 copy).",
            "wc -c /var/log/messages /var/log/messages.1 2>/dev/null || echo 'no rotation'"),
    ]
    procs = [
        boot,
        _ck("s1_stop", "! grep -qx cpu-hog /proc/[0-9]*/comm", "cpu-hog is still running.", "ps w | grep cpu-hog | grep -v grep || echo stopped"),
        _ck("s1_swap", "grep -qx vm.swappiness=10 /etc/sysctl.d/99-workstation.conf && [ \"$(cat /proc/sys/vm/swappiness)\" = 10 ]",
            "vm.swappiness is not 10 both live and in /etc/sysctl.d/99-workstation.conf.",
            "cat /proc/sys/vm/swappiness; cat /etc/sysctl.d/99-workstation.conf 2>/dev/null"),
        _ck("s2_stop", "! grep -qx {{s2_proc}} /proc/[0-9]*/comm",
            "The process named in the Stage 2 ticket is still running.", "ps w | head -20"),
        _ck("s3_stop", "! grep -qx {{s3_proc}} /proc/[0-9]*/comm",
            "A CPU burner is still running. Find it in the process list and stop it.", "ps w | head -20"),
    ]
    pkgs = [
        boot,
        _ck("s1_update", "grep -qx OK /var/lib/novak/apk-updated",
            "The package index has not been updated.", "ls -l /var/lib/novak/apk-updated 2>/dev/null || echo 'not updated'"),
        _ck("s1_pkg", "apk info -e darkhttpd >/dev/null", "darkhttpd is not installed.", "apk info -e darkhttpd || echo missing"),
        _ck("s2_pkg", "apk info -e {{s2_pkg}} >/dev/null",
            "The package named in the Stage 2 ticket is not installed.", "apk info"),
        _ck("s3_cron", "grep -qxF '{{s3_min}} * * * * {{s3_cmd}}' /var/spool/cron/crontabs/root",
            "The hourly cron job from the incident ticket is not in root's crontab.",
            "cat /var/spool/cron/crontabs/root 2>/dev/null || echo 'no crontab'"),
    ]
    ssh = [
        boot,
        _ck("s1_key", "[ -s /root/.ssh/id_ed25519.pub ] && grep -q ssh-ed25519 /root/.ssh/authorized_keys",
            "There is no Ed25519 key in /root/.ssh, or it is not in authorized_keys.",
            "ls -l /root/.ssh 2>/dev/null || echo 'no .ssh'"),
        _ck("s1_harden", "grep -qx 'PermitRootLogin no' /etc/ssh/sshd_config && grep -qx 'PasswordAuthentication no' /etc/ssh/sshd_config",
            "sshd still allows root login or passwords.", "grep -E '^(PermitRootLogin|PasswordAuthentication) ' /etc/ssh/sshd_config"),
        _ck("s2_allow", "grep -qx 'AllowUsers {{s2_ssh_user}}' /etc/ssh/sshd_config",
            "AllowUsers does not name the account from the Stage 2 ticket.",
            "grep '^AllowUsers ' /etc/ssh/sshd_config || echo 'no AllowUsers'"),
        _ck("s3_port", "grep -qx 'Port {{s3_port}}' /etc/ssh/sshd_config",
            "sshd is not on the port from the incident ticket.",
            "grep '^Port ' /etc/ssh/sshd_config || echo 'no Port line'"),
        _ck("s3_check", "sshd -t", "sshd -t does not accept the configuration.", "sshd -t 2>&1 || true", secs=6),
    ]
    return {
        "linux-gui-network": net, "linux-gui-disks": disks, "linux-gui-firewall": fw,
        "linux-gui-users": users, "linux-gui-logs": logs, "linux-gui-processes": procs,
        "linux-gui-packages": pkgs, "linux-gui-ssh": ssh,
    }


def _fix_user_checks(rows):
    """The sudo test is built with the placeholder still inside the shell."""
    out = []
    for row in rows:
        if row["id"] == "s2_user":
            row = _ck("s2_user",
                      "passwd -S {{s2_user}} | awk '{print $2}' | grep -qx P && grep '^sudo:' /etc/group | grep -Eq '[:,]{{s2_user}}(,|$)'",
                      row["why"], "passwd -S {{s2_user}}; grep '^sudo:' /etc/group")
        elif row["id"] == "s3_user":
            row = _ck("s3_user",
                      "passwd -S {{s3_user}} | awk '{print $2}' | grep -qx P && grep '^sudo:' /etc/group | grep -Eq '[:,]{{s3_user}}(,|$)'",
                      row["why"], "passwd -S {{s3_user}}; grep '^sudo:' /etc/group")
        out.append(row)
    return out


_CHECKS = _checks()
_CHECKS["linux-gui-users"] = _fix_user_checks(_CHECKS["linux-gui-users"])


def _lab(lid, title, blurb, intro, success, objectives, hints, obj_hints, stages, minutes=25, codes=None):
    return {
        "id": lid,
        "title": title,
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": minutes,
        "course_objectives": codes or ["IT-9.1"],
        "blurb": blurb,
        "intro": intro,
        "success_msg": success,
        "initial_state": {"hostname": "novak-lnx-01", "user": "root"},
        "objectives": objectives,
        "hints": hints,
        "obj_hints": obj_hints,
        "stages": stages,
        "vm": dict(GUI_VM),
        "vm_checks": _CHECKS[lid],
        "solution": {"vm_commands": []},
    }


def _o(oid, text):
    return {"id": oid, "text": text}


_RIGHT = "Right-click the desktop and open the tool named in the step. Click the desktop first if the keyboard is not typing there."


LINUX_GUI_LABS = [
    _lab(
        "linux-gui-network",
        "Linux desktop — static IPv4, gateway, and DNS",
        "Set a static address, prefix, gateway, and DNS on a live Linux desktop, including values you have to read from the machine.",
        "The workstation needs a static IPv4 setup. Stage 1 walks through a known address. Stages 2 and 3 use tickets that exist only on this desktop.",
        "The guided profile, the practice profile, and the live eth0 address all match their tickets.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_profile", "Save a profile named guided with 10.20.40.15/24, gateway 10.20.40.1, DNS 10.20.40.10"),
         _o("s2_profile", "Save a profile named practice that matches the Stage 2 ticket on the desktop"),
         _o("s3_live", "Apply the incident ticket so eth0, the default route, and DNS match it")],
        ["Open Settings from the desktop menu.", "Read the ticket file before you type a Stage 2 or Stage 3 address."],
        {"boot": ["Wait until the desktop picture appears.", "If it stays on the progress line, reload the page."],
         "s1_profile": ["Settings → Network. Profile name guided. Address 10.20.40.15, prefix 24, gateway 10.20.40.1, DNS 10.20.40.10, then Save profile.",
                        "novak-net save guided 10.20.40.15 24 10.20.40.1 10.20.40.10"],
         "s2_profile": ["Open /root/Desktop/stage2-ticket.txt in the editor. The profile name is practice.",
                        "Use every address field from that file. Do not reuse the Stage 1 numbers."],
         "s3_live": ["The incident file on the desktop starts with INC-.",
                     "Apply live, not only Save profile. Check with the terminal: ip -4 addr show eth0"]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<p>Right-click the desktop and choose <strong>Settings</strong>. Open the <strong>Network</strong> tab.</p><ol><li>Profile: <code>guided</code></li><li>Address <code>10.20.40.15</code>, prefix <code>24</code>, gateway <code>10.20.40.1</code>, DNS <code>10.20.40.10</code></li><li>Click <strong>Save profile</strong>. This stores <code>/etc/novak/profiles/guided.conf</code> and does not have to be the live address yet.</li></ol><p>The same tool from a terminal is <code>novak-net save guided 10.20.40.15 24 10.20.40.1 10.20.40.10</code>.</p>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Open <code>/root/Desktop/stage2-ticket.txt</code> in the editor. Save a profile named <code>practice</code> using the address, prefix, gateway, and DNS written in that file. The Stage 1 numbers will not match.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>A file on the desktop starts with <code>INC-</code>. Apply that address live on eth0 (address, prefix, gateway, and DNS). Confirm in the terminal with <code>ip -4 addr</code> and <code>ip route</code>.</p>"},
        ],
        codes=["IT-9.1", "IT-5.1"],
    ),
    _lab(
        "linux-gui-disks",
        "Linux desktop — disk health and persistent mounts",
        "Read a disk image's size, then mount images and record them in /etc/fstab.",
        "Three disk images are already on this machine. Stage 1 is a known mount. The other two are described only in ticket files.",
        "The health report matches the image, and all three mounts are in /etc/fstab and mounted.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_report", "Save a health report for /var/lib/novak/data.img"),
         _o("s1_mount", "Mount data.img at /srv/data with options defaults,nofail"),
         _o("s2_mount", "Mount the extra image the way the Stage 2 ticket describes"),
         _o("s3_mount", "Mount the ticket image the way the incident file describes")],
        ["Settings → Disks writes the report and the fstab line.", "The mount has to show up in the terminal, not only in the form."],
        {"boot": ["Wait for the desktop.", "Right-click the background if you do not see a menu."],
         "s1_report": ["Settings → Disks. Image /var/lib/novak/data.img. Click Save health report.",
                       "The report is /var/lib/novak/smart-report.txt and must match the file's real size."],
         "s1_mount": ["Mount point /srv/data and options defaults,nofail, then Mount and save fstab.",
                      "novak-disk mount /var/lib/novak/data.img /srv/data defaults,nofail"],
         "s2_mount": ["Read /root/Desktop/stage2-ticket.txt for the mount point and options.",
                      "Use the extra image named in that file, not data.img."],
         "s3_mount": ["Open the desktop file whose name starts with INC-.",
                      "Mount that image at the path and with the options written there."]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<p>Right-click and open <strong>Settings → Disks</strong>.</p><ol><li>Image <code>/var/lib/novak/data.img</code>. Click <strong>Save health report</strong>. It records the image's real size.</li><li>Mount point <code>/srv/data</code>, options <code>defaults,nofail</code>. Click <strong>Mount and save fstab</strong>.</li></ol><p>Check with <code>findmnt /srv/data</code> or <code>mount | grep /srv/data</code>.</p>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Read <code>/root/Desktop/stage2-ticket.txt</code>. Mount the image it names, at the mount point it names, with the options it names.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>Open the <code>INC-</code> file on the desktop and mount that image the way the ticket says. Both the mount and the <code>/etc/fstab</code> line have to be there.</p>"},
        ],
        codes=["IT-9.1", "IT-3.1"],
    ),
    _lab(
        "linux-gui-firewall",
        "Linux desktop — host firewall and SSH",
        "Turn on a default-drop firewall, allow the services you mean to allow, and start sshd.",
        "Lock down incoming traffic, then open the ports and block the address the tickets name.",
        "Incoming traffic is dropped by default, the required ports are allowed, sshd is running, and the incident address is banned.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_policy", "Set the firewall to drop incoming traffic and allow outgoing traffic"),
         _o("s1_allow", "Allow TCP 22 and TCP 443"),
         _o("s1_ssh", "Start sshd"),
         _o("s2_port", "Allow the TCP port named in the Stage 2 ticket"),
         _o("s3_ban", "Drop traffic from the address named in the incident ticket")],
        ["Settings → Firewall changes real iptables rules.", "You can read the result with iptables-save."],
        {"boot": ["Wait for the desktop.", "The serial console is not the desktop."],
         "s1_policy": ["Settings → Firewall → Enable drop-incoming policy.", "That sets INPUT DROP and OUTPUT ACCEPT."],
         "s1_allow": ["Allow TCP port 22, then TCP port 443.", "Both rules have to be present together."],
         "s1_ssh": ["Click Start SSH on the Firewall tab.", "pidof sshd should print a process id."],
         "s2_port": ["The port is in /root/Desktop/stage2-ticket.txt.", "Allow that TCP port. Do not remove 22 or 443."],
         "s3_ban": ["The address to drop is in the INC- file, not in this hint.", "Ban that address. Earlier bans should stay."]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<p>Open <strong>Settings → Firewall</strong>.</p><ol><li>Click <strong>Enable drop-incoming policy</strong>.</li><li>Allow TCP port <code>22</code>, then <code>443</code>.</li><li>Click <strong>Start SSH</strong>.</li></ol><p>Check with <code>iptables-save</code> and <code>pidof sshd</code>.</p>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Read <code>/root/Desktop/stage2-ticket.txt</code> and allow the TCP port it names. Leave the Stage 1 rules in place.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>Open the <code>INC-</code> file and drop traffic from the address it names.</p>"},
        ],
        codes=["IT-9.1", "IT-10.1"],
    ),
    _lab(
        "linux-gui-users",
        "Linux desktop — accounts, sudo, and file permissions",
        "Unlock accounts, grant sudo, and set file modes from the file manager.",
        "tech1 is locked and a script is not executable. Two more accounts are described only in the tickets.",
        "tech1 and both ticket accounts are unlocked with sudo, and each script has the mode the ticket asked for.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_unlock", "Unlock the tech1 account"),
         _o("s1_sudo", "Add tech1 to the sudo group"),
         _o("s1_mode", "Set /root/support/backup.sh to mode 750"),
         _o("s2_user", "Unlock the Stage 2 account and add it to sudo"),
         _o("s2_mode", "Set the Stage 2 file to the mode in the ticket"),
         _o("s3_user", "Unlock the incident account and add it to sudo"),
         _o("s3_mode", "Set the incident file to the mode in the ticket")],
        ["Users are under Settings. File modes are under Files → Permissions.", "Owner, group, and others are three groups of read, write, and execute."],
        {"boot": ["Wait for the desktop.", "Right-click for Files, Editor, Terminal, and Settings."],
         "s1_unlock": ["Settings → Users. Username tech1. Click Unlock account.", "The account was locked on purpose."],
         "s1_sudo": ["With tech1 still in the username box, click Grant sudo.", "That adds the sudo group."],
         "s1_mode": ["Open Files, go to /root/support, select backup.sh, and open Permissions.",
                     "Owner read/write/execute, group read/execute, others nothing. That is mode 750."],
         "s2_user": ["The account name is in /root/Desktop/stage2-ticket.txt.", "Unlock it and grant sudo. Do not lock tech1 again."],
         "s2_mode": ["The same ticket names a file and a mode.", "Set that mode in Files → Permissions. The mode number is only in the ticket."],
         "s3_user": ["The incident file starts with INC- and names another account.", "Unlock that account and grant sudo."],
         "s3_mode": ["The incident file names a file and a mode.", "Set that mode. Do not copy the Stage 1 mode unless the ticket says the same number."]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<ol><li>Settings → <strong>Users</strong>. Username <code>tech1</code>. Click <strong>Unlock account</strong>, then <strong>Grant sudo</strong>.</li><li>Right-click the desktop and open <strong>Files</strong>. Go to <code>/root/support</code>, select <code>backup.sh</code>, and click <strong>Permissions</strong>.</li><li>Turn on owner read, write, and execute; group read and execute; leave others off. That is mode <code>750</code>. Click <strong>Apply</strong>.</li></ol>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Read <code>/root/Desktop/stage2-ticket.txt</code>. Unlock that account, grant sudo, and set the file it names to the mode it names.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>Open the <code>INC-</code> file on the desktop and do the same for the account, file, and mode written there.</p>"},
        ],
        codes=["IT-9.1", "IT-9.3"],
    ),
    _lab(
        "linux-gui-logs",
        "Linux desktop — log triage and blocking a source",
        "Find failed-login sources in the logs, block them, and rotate the message log.",
        "The message log has a known example and a noisier source. A second log has a new source.",
        "Each source address is banned, and the message log has been rotated.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_ban", "Block 198.51.100.77, the example address in the walkthrough"),
         _o("s2_ban", "Block the address that accounts for the most failures in /var/log/messages"),
         _o("s3_ban", "Block the source address in /var/log/secure"),
         _o("s3_rotate", "Rotate /var/log/messages so the live file is smaller than the copy")],
        ["Settings → Logs shows the files and can ban an address.", "Count failures yourself. The walkthrough address is not the busiest one."],
        {"boot": ["Wait for the desktop.", "Then open Settings → Logs and click Refresh."],
         "s1_ban": ["The walkthrough address is 198.51.100.77. Type it in Ban IP and click Ban.", "It should appear in the ban list."],
         "s2_ban": ["Refresh the log view and read /var/log/messages.", "Block the address that appears more often than 198.51.100.77. The hint will not repeat that address."],
         "s3_ban": ["The incident file tells you which log to open. It does not repeat the address here.", "Block the source you find in that log."],
         "s3_rotate": ["On the Logs tab, click Rotate.", "That keeps a copy and empties the live message log."]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<p>Open <strong>Settings → Logs</strong> and click <strong>Refresh</strong>. <code>/var/log/messages</code> contains failed sshd passwords, including the example address <code>198.51.100.77</code>. Type that address under Ban IP and click <strong>Ban</strong>.</p>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Read <code>/root/Desktop/stage2-ticket.txt</code>, then the message log. Block the address that failed the most. It is not the example from Stage 1.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>Open the <code>INC-</code> file. It names a log. Block the source you find there, then rotate <code>/var/log/messages</code>.</p>"},
        ],
        codes=["IT-9.1", "IT-10.4"],
    ),
    _lab(
        "linux-gui-processes",
        "Linux desktop — runaway processes and swappiness",
        "Stop CPU burners and set vm.swappiness.",
        "Three tight loops are running. One name is given. You have to find the last one.",
        "All three burners are gone and vm.swappiness is 10, including the saved sysctl file.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_stop", "Stop the process named cpu-hog"),
         _o("s1_swap", "Set vm.swappiness to 10 and save it"),
         _o("s2_stop", "Stop the process named in the Stage 2 ticket"),
         _o("s3_stop", "Stop the remaining CPU burner")],
        ["Settings → Processes lists what is running.", "Swappiness is a number you type. 60 is the starting value."],
        {"boot": ["Wait for the desktop.", "Open Settings → Processes and click Refresh."],
         "s1_stop": ["Select or type cpu-hog and click Stop.", "Refresh and confirm it is gone."],
         "s1_swap": ["Type 10 in Swappiness and click Apply swappiness.", "That writes /etc/sysctl.d/99-workstation.conf and sets the live value."],
         "s2_stop": ["The name is in /root/Desktop/stage2-ticket.txt.", "Stop that process. Do not stop unrelated system processes."],
         "s3_stop": ["The incident file tells you a burner is left and does not name it.", "Refresh the process list and stop the one that is not a normal system task."]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<p>Open <strong>Settings → Processes</strong> and click <strong>Refresh</strong>.</p><ol><li>Stop the process named <code>cpu-hog</code>.</li><li>Set swappiness to <code>10</code> and click <strong>Apply swappiness</strong>.</li></ol><p>Check with <code>cat /proc/sys/vm/swappiness</code>.</p>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Read <code>/root/Desktop/stage2-ticket.txt</code> and stop the process it names.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>Open the <code>INC-</code> file. One CPU burner is still running. Identify it from the process list and stop it. The ticket does not contain the name.</p>"},
        ],
        codes=["IT-9.1", "IT-11.3"],
    ),
    _lab(
        "linux-gui-packages",
        "Linux desktop — packages and cron",
        "Update the local package index, install packages, and schedule a job.",
        "The machine has a small offline package repository. The second package and the cron minute come from tickets.",
        "The index was updated, both packages are installed, and root's crontab has the incident job.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_update", "Update the package index"),
         _o("s1_pkg", "Install darkhttpd"),
         _o("s2_pkg", "Install the package named in the Stage 2 ticket"),
         _o("s3_cron", "Enable the hourly cron job described in the incident ticket")],
        ["Settings → Packages talks to apk and cron.", "Update the index before you install."],
        {"boot": ["Wait for the desktop.", "Open Settings → Packages."],
         "s1_update": ["Click Update package index.", "That has to succeed before an install."],
         "s1_pkg": ["Package name darkhttpd, then Install.", "It comes from the local repository on this machine."],
         "s2_pkg": ["The package name is in /root/Desktop/stage2-ticket.txt.", "Install that package. It is not darkhttpd."],
         "s3_cron": ["The incident file has a minute and a command.", "Put those in Minute and Command, then Enable hourly cron. The hint does not include the minute."]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<p>Open <strong>Settings → Packages</strong>.</p><ol><li>Click <strong>Update package index</strong>.</li><li>Package <code>darkhttpd</code>, then <strong>Install</strong>.</li></ol><p>This uses <code>apk</code> and the repository already configured on the machine.</p>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Read <code>/root/Desktop/stage2-ticket.txt</code> and install the package it names.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>Open the <code>INC-</code> file. Enable an hourly cron job using the minute and the command written there.</p>"},
        ],
        codes=["IT-9.1", "IT-10.3"],
    ),
    _lab(
        "linux-gui-ssh",
        "Linux desktop — SSH keys and sshd",
        "Create an Ed25519 key, turn off root and password logins, and apply the ticket's account and port.",
        "sshd still allows passwords. The account and the port you must set are on the desktop, not in this page.",
        "The key is installed, root and password logins are off, AllowUsers and Port match the tickets, and sshd -t accepts the file.",
        [_o("boot", "The Linux desktop is running"),
         _o("s1_key", "Generate an Ed25519 key and authorize it for root"),
         _o("s1_harden", "Set PermitRootLogin no and PasswordAuthentication no"),
         _o("s2_allow", "Allow only the account named in the Stage 2 ticket"),
         _o("s3_port", "Set sshd to the port named in the incident ticket"),
         _o("s3_check", "sshd accepts the configuration (sshd -t)")],
        ["Settings → SSH edits /etc/ssh/sshd_config.", "Check the file before you finish. sshd -t must succeed."],
        {"boot": ["Wait for the desktop.", "Open Settings → SSH."],
         "s1_key": ["Click Generate Ed25519 key.", "That writes /root/.ssh/id_ed25519 and adds the public key to authorized_keys."],
         "s1_harden": ["Click Root login off, passwords off.", "That sets PermitRootLogin no and PasswordAuthentication no."],
         "s2_allow": ["The account is in /root/Desktop/stage2-ticket.txt.", "Type that account under Allow user and click Allow."],
         "s3_port": ["The port is in the INC- file.", "Set that port. The hint does not include the number."],
         "s3_check": ["Click Check config.", "sshd -t has to exit cleanly. Fix the file if it reports an error."]},
        [
            {"title": "Stage 1 — Guided walkthrough", "html": "<p>Open <strong>Settings → SSH</strong>.</p><ol><li>Click <strong>Generate Ed25519 key</strong>.</li><li>Click <strong>Root login off, passwords off</strong>.</li></ol><p>You can read <code>/etc/ssh/sshd_config</code> in the editor afterward.</p>"},
            {"title": "Stage 2 — Assisted practice", "html": "<p>Read <code>/root/Desktop/stage2-ticket.txt</code> and allow only the account it names.</p>"},
            {"title": "Stage 3 — Ticket", "html": "<p>Open the <code>INC-</code> file, set sshd to the port it names, and check the configuration.</p>"},
        ],
        codes=["IT-9.1", "IT-10.1"],
    ),
]
