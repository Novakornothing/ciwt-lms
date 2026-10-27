"""Ubuntu 24.04 LTS GNOME Desktop GUI Workbench (`linuxgui`) & Split-Pane Terminal Simulator.

Provides interactive server-side state and event handling for 8 core Linux GUI administration tools:
  1. GNOME Settings → Network (`nm-connection-editor` / IPv4 & IPv6 / DNS / 802.1X / Interface Toggle)
  2. GNOME Disks & GParted Partition Manager (`gnome-disks` — `/dev/nvme0n1` & `/dev/sdb`, mount/unmount, `/etc/fstab` options, SMART self-test)
  3. GUFW Firewall & Systemd Services (`gufw` + `gnome-system-monitor` — UFW incoming/outgoing policies, allow/deny 22/tcp, 80/tcp, 443/tcp, start/restart `ssh`, `nginx`, `NetworkManager`, `cron`)
  4. GNOME Users & Nautilus File Permissions (`gnome-users` + `nautilus` — unlock `tech1`, toggle `sudo` administrator membership, set Owner/Group/Others `rwx` + executable bit on scripts/files)
  5. GNOME Logs & Journald Security Triage (`gnome-logs` / `journalctl` — filter `err`/`crit` events on `ssh.service`, identify brute-force IP `198.51.100.77`, block via Fail2Ban/UFW, vacuum journal logs to 100M)
  6. GNOME System Monitor & Process/Memory Triage (`gnome-system-monitor` — inspect live PID table, renice or terminate runaway `stress-ng-worker` PID 4412 at 98% CPU, tune `vm.swappiness=10`)
  7. Ubuntu App Center / Synaptic Package Manager & Scheduled Cron Tasks (`apt` + `crontab` / `systemd.timer` — refresh APT cache, install/upgrade `unattended-upgrades`, enable nightly `0 2 * * * /usr/local/bin/backup-verify.sh`)
  8. GNOME Passwords & Keys (`seahorse`) + OpenSSH Server Hardening (`sshd_config` — generate/import Ed25519 key `id_ed25519.pub`, set `PermitRootLogin no` & `PasswordAuthentication no`, validate `sshd -t` & reload `ssh.service`)
"""
from __future__ import annotations

from copy import deepcopy


def linux_gui_state() -> dict:
    return {
        "win": "network",          # network | disks | firewall | users | files | logs | processes | packages | ssh
        "split_terminal": True,    # show GUI + Bash Terminal split view by default
        "seen": [],
        "log": [],
        "net": {
            "iface": "eth0",
            "connected": True,
            "method": "dhcp",      # dhcp | manual
            "ipv4": "10.20.40.120",
            "prefix": "24",
            "gateway": "10.20.40.1",
            "dns": "10.20.40.10",
            "ipv6_mode": "auto",
            "eight021x": False,
            "applied": False,
        },
        "disks": {
            "selected_disk": "/dev/nvme0n1",
            "selected_part": "/dev/sdb1",
            "smart_checked": False,
            "smart_status": "PASSED (34°C · 0 Reallocated Sectors · 99% Life Remaining)",
            "sdb1_mounted": False,
            "sdb1_mountpoint": "/srv/data",
            "sdb1_fstype": "ext4",
            "fstab_opts": "defaults,nofail",
            "fstab_saved": False,
        },
        "firewall": {
            "ufw_enabled": False,
            "default_incoming": "deny",
            "default_outgoing": "allow",
            "rules": [
                {"port": "22/tcp", "service": "OpenSSH", "action": "ALLOW IN", "enabled": False},
                {"port": "80/tcp", "service": "HTTP Web", "action": "ALLOW IN", "enabled": False},
                {"port": "443/tcp", "service": "HTTPS TLS", "action": "ALLOW IN", "enabled": False},
                {"port": "23/tcp", "service": "Telnet (Legacy)", "action": "DENY IN", "enabled": True},
            ],
            "services": {
                "ssh": {"unit": "ssh.service", "desc": "OpenBSD Secure Shell server", "state": "inactive (dead)", "enabled": True},
                "nginx": {"unit": "nginx.service", "desc": "A high performance web server and reverse proxy", "state": "active (running)", "enabled": True},
                "NetworkManager": {"unit": "NetworkManager.service", "desc": "Network Manager daemon", "state": "active (running)", "enabled": True},
                "cron": {"unit": "cron.service", "desc": "Regular background program processing daemon", "state": "active (running)", "enabled": True},
            },
        },
        "users": {
            "selected_user": "tech1",
            "accounts": {
                "trainee": {"uid": 1000, "full_name": "Support Trainee", "locked": False, "sudo": True, "groups": ["trainee", "sudo", "adm"]},
                "tech1": {"uid": 1001, "full_name": "Jordan Vance (Tier-1 Tech)", "locked": True, "sudo": False, "groups": ["tech1"]},
                "svc_backup": {"uid": 1002, "full_name": "Nightly Backup Account", "locked": False, "sudo": False, "groups": ["backup"]},
            },
            "files": {
                "/home/trainee/support/backup.sh": {
                    "owner": "trainee",
                    "group": "trainee",
                    "mode": "644",
                    "exec_bit": False,
                },
                "/home/trainee/support/report.txt": {
                    "owner": "trainee",
                    "group": "trainee",
                    "mode": "640",
                    "exec_bit": False,
                },
            },
        },
        "logs": {
            "unit_filter": "all",
            "severity_filter": "all",
            "filtered_ssh": False,
            "banned_ip": None,
            "journal_usage_mb": 640,
            "vacuumed": False,
        },
        "processes": {
            "runaway_pid": 4412,
            "runaway_name": "stress-ng-worker",
            "runaway_cpu": 98.4,
            "runaway_nice": 0,
            "runaway_state": "R (running)",
            "killed": False,
            "swappiness": 60,
            "swappiness_tuned": False,
        },
        "packages": {
            "apt_updated": False,
            "last_update": "42 days ago (stale cache)",
            "unattended_installed": False,
            "cron_schedule": "0 2 * * * /usr/local/bin/backup-verify.sh",
            "cron_enabled": False,
        },
        "ssh": {
            "ed25519_generated": False,
            "ed25519_fp": "SHA256:9xK4mP8vR2nL7qW3cT6yB1zF5jH0dG8sA4eU2iO6pY (trainee@novak-lnx-01)",
            "permit_root_login": "yes",
            "password_auth": "yes",
            "hardened": False,
            "sshd_reloaded": False,
        },
    }


def public_gui(state: dict) -> dict:
    g = deepcopy((state or {}).get("linuxgui") or linux_gui_state())
    g.pop("seen", None)
    return g


DEFAULT_GUI_RULES = {
    "open_network": "open:network",
    "configure_ipv4": "net:save_manual",
    "apply_connection": "net:apply",
    "open_disks": "open:disks",
    "check_smart": "disks:smart",
    "mount_sdb1": "disks:mount_sdb1",
    "open_firewall": "open:firewall",
    "enable_ufw": "fw:enable",
    "allow_ssh_https": "fw:allow_ssh_https",
    "restart_ssh": "svc:restart:ssh",
    "open_users": "open:users",
    "unlock_tech1": "users:unlock:tech1",
    "grant_sudo": "users:sudo:tech1",
    "set_nautilus_perms": "files:chmod:backup.sh:750",
    "open_logs": "open:logs",
    "filter_ssh_logs": "logs:filter_ssh",
    "ban_attacker_ip": "logs:ban:198.51.100.77",
    "vacuum_journal": "logs:vacuum",
    "open_processes": "open:processes",
    "terminate_runaway": "proc:kill:4412",
    "tune_swappiness": "proc:swappiness:10",
    "open_packages": "open:packages",
    "apt_update_cache": "pkg:apt_update",
    "install_unattended": "pkg:install:unattended-upgrades",
    "enable_backup_cron": "pkg:cron_enable",
    "open_ssh_keys": "open:ssh",
    "generate_ed25519": "ssh:keygen",
    "harden_sshd_config": "ssh:harden",
    "reload_sshd_service": "ssh:reload",
}


def apply(lab: dict, state: dict, done: list, ev: str, data: dict):
    st = state.setdefault("linuxgui", linux_gui_state())
    for k, v in linux_gui_state().items():
        if k not in st:
            st[k] = deepcopy(v)
    result = {}
    ev = (ev or "").strip()
    data = data if isinstance(data, dict) else {}

    if ev.startswith("open:"):
        win = ev.split(":", 1)[1]
        if win in ("network", "disks", "firewall", "users", "files", "logs", "processes", "packages", "ssh"):
            st["win"] = win
            result["ok"] = f"Opened GNOME {win.capitalize()} utility."
        else:
            return {"error": "Unknown GNOME application window.", "changed": False}, state, done
    elif ev == "toggle:split":
        st["split_terminal"] = not bool(st.get("split_terminal", True))
        result["ok"] = "Split-View Bash Terminal " + ("shown." if st["split_terminal"] else "hidden.")
    elif ev == "net:save_manual":
        ipv4 = (data.get("ipv4") or "10.20.40.15").strip()
        prefix = str(data.get("prefix") or "24").strip().lstrip("/")
        gw = (data.get("gateway") or "10.20.40.1").strip()
        dns = (data.get("dns") or "10.20.40.10, 1.1.1.1").strip()
        method = (data.get("method") or "manual").strip().lower()
        st["net"]["method"] = method
        st["net"]["ipv4"] = ipv4
        st["net"]["prefix"] = prefix
        st["net"]["gateway"] = gw
        st["net"]["dns"] = dns
        state["ip"] = ipv4
        result["ok"] = f"Saved eth0 IPv4 profile ({method.upper()}: {ipv4}/{prefix}, GW {gw}, DNS {dns})."
    elif ev == "net:apply":
        st["net"]["connected"] = True
        st["net"]["applied"] = True
        result["ok"] = f"NetworkManager applied connection profile eth0 ({st['net']['ipv4']}/{st['net']['prefix']})."
    elif ev == "net:toggle":
        st["net"]["connected"] = not st["net"]["connected"]
        result["ok"] = "Interface eth0 " + ("connected." if st["net"]["connected"] else "disconnected.")
    elif ev == "disks:select":
        disk = data.get("disk") or "/dev/nvme0n1"
        st["disks"]["selected_disk"] = disk
        result["ok"] = f"Selected block device {disk} in GNOME Disks."
    elif ev == "disks:smart":
        st["disks"]["smart_checked"] = True
        result["ok"] = "SMART Self-Test completed on /dev/nvme0n1: Disk is OK (34°C, 0 bad sectors)."
    elif ev == "disks:mount_sdb1":
        mp = (data.get("mountpoint") or "/srv/data").strip()
        opts = (data.get("fstab_opts") or "defaults,noatime,nofail").strip()
        st["disks"]["sdb1_mountpoint"] = mp
        st["disks"]["fstab_opts"] = opts
        st["disks"]["fstab_saved"] = True
        st["disks"]["sdb1_mounted"] = True
        result["ok"] = f"Mounted /dev/sdb1 (ext4) at {mp} and updated /etc/fstab ({opts})."
    elif ev == "disks:unmount_sdb1":
        st["disks"]["sdb1_mounted"] = False
        result["ok"] = "Unmounted /dev/sdb1 cleanly."
    elif ev == "fw:enable":
        st["firewall"]["ufw_enabled"] = True
        result["ok"] = "UFW Firewall enabled (Default policy: Deny Incoming, Allow Outgoing)."
    elif ev == "fw:toggle":
        st["firewall"]["ufw_enabled"] = not st["firewall"]["ufw_enabled"]
        if st["firewall"]["ufw_enabled"]:
            ev = "fw:enable"
        result["ok"] = "UFW Firewall is now " + ("ENABLED." if st["firewall"]["ufw_enabled"] else "DISABLED.")
    elif ev.startswith("fw:rule:"):
        port = ev.split(":", 2)[2]
        for r in st["firewall"]["rules"]:
            if r["port"] == port:
                r["enabled"] = not r["enabled"]
                result["ok"] = f"UFW rule {r['port']} ({r['service']}): {'ENABLED' if r['enabled'] else 'DISABLED'}."
                break
        enabled_ports = {r["port"] for r in st["firewall"]["rules"] if r["enabled"]}
        if {"22/tcp", "443/tcp"} <= enabled_ports:
            st["seen"].append("fw:allow_ssh_https")
    elif ev == "fw:allow_ssh_https":
        for r in st["firewall"]["rules"]:
            if r["port"] in ("22/tcp", "443/tcp"):
                r["enabled"] = True
        result["ok"] = "Added UFW ALLOW rules for 22/tcp (OpenSSH) and 443/tcp (HTTPS)."
    elif ev.startswith("svc:restart:"):
        svc = ev.split(":", 2)[2]
        if svc in st["firewall"]["services"]:
            st["firewall"]["services"][svc]["state"] = "active (running)"
            result["ok"] = f"systemd restarted {svc}.service — state is now active (running)."
    elif ev.startswith("users:unlock:"):
        uname = ev.split(":", 2)[2]
        acc = st["users"]["accounts"].get(uname)
        if acc:
            acc["locked"] = False
            result["ok"] = f"Unlocked user account '{uname}' via GNOME Users."
    elif ev.startswith("users:sudo:"):
        uname = ev.split(":", 2)[2]
        acc = st["users"]["accounts"].get(uname)
        if acc:
            acc["sudo"] = True
            if "sudo" not in acc["groups"]:
                acc["groups"].append("sudo")
            result["ok"] = f"Granted Administrator (sudo) group membership to '{uname}'."
    elif ev.startswith("files:chmod:"):
        parts = ev.split(":")
        fname = parts[2] if len(parts) > 2 else "backup.sh"
        mode = parts[3] if len(parts) > 3 else "750"
        path = "/home/trainee/support/" + fname
        fobj = st["users"]["files"].setdefault(path, {"owner": "trainee", "group": "trainee", "mode": "644", "exec_bit": False})
        fobj["mode"] = mode
        fobj["exec_bit"] = mode in ("750", "755", "700", "775")
        if "fs" in state and path in state["fs"]:
            state["fs"][path]["mode"] = int(mode, 8)
        result["ok"] = f"Nautilus Permissions updated on {path}: octal {mode} (executable={fobj['exec_bit']})."
    elif ev == "logs:filter_ssh":
        st["logs"]["unit_filter"] = "ssh.service"
        st["logs"]["severity_filter"] = "err"
        st["logs"]["filtered_ssh"] = True
        result["ok"] = "Filtered GNOME Logs (journalctl -u ssh.service -p err): 48 failed root logins from 198.51.100.77."
    elif ev.startswith("logs:ban:"):
        ip = ev.split(":", 2)[2] or "198.51.100.77"
        st["logs"]["banned_ip"] = ip
        result["ok"] = f"Fail2Ban / UFW blocked brute-force source IP {ip} (ufw insert 1 deny from {ip})."
    elif ev == "logs:vacuum":
        st["logs"]["journal_usage_mb"] = 92
        st["logs"]["vacuumed"] = True
        result["ok"] = "Rotated and vacuumed systemd-journald archive (journalctl --vacuum-size=100M → 92 MB used)."
    elif ev.startswith("proc:renice:"):
        st["processes"]["runaway_nice"] = 15
        result["ok"] = "Adjusted PID 4412 (stress-ng-worker) scheduling priority to nice +15."
    elif ev.startswith("proc:kill:"):
        st["processes"]["killed"] = True
        st["processes"]["runaway_cpu"] = 0.0
        st["processes"]["runaway_state"] = "terminated (SIGTERM)"
        result["ok"] = "Terminated runaway process stress-ng-worker (PID 4412) — CPU load dropped from 98.4% to 4.2%."
    elif ev.startswith("proc:swappiness:"):
        val = int(ev.split(":", 2)[2] or 10)
        st["processes"]["swappiness"] = val
        st["processes"]["swappiness_tuned"] = True
        result["ok"] = f"Applied sysctl vm.swappiness={val} in /etc/sysctl.d/99-workstation.conf."
    elif ev == "pkg:apt_update":
        st["packages"]["apt_updated"] = True
        st["packages"]["last_update"] = "Just now (ubuntu noble-security InRelease synced)"
        result["ok"] = "Refreshed APT package lists (apt update — 14 security updates available)."
    elif ev.startswith("pkg:install:"):
        pkg = ev.split(":", 2)[2] or "unattended-upgrades"
        st["packages"]["unattended_installed"] = True
        result["ok"] = f"Installed and enabled {pkg} (automatic security patching active)."
    elif ev == "pkg:cron_enable":
        sched = (data.get("schedule") or "0 2 * * * /usr/local/bin/backup-verify.sh").strip()
        st["packages"]["cron_schedule"] = sched
        st["packages"]["cron_enabled"] = True
        result["ok"] = f"Saved and enabled nightly cron job ({sched}) in /etc/crontab."
    elif ev == "ssh:keygen":
        st["ssh"]["ed25519_generated"] = True
        result["ok"] = "Generated Ed25519 SSH keypair (~/.ssh/id_ed25519.pub) and authorized key in GNOME Passwords & Keys."
    elif ev == "ssh:harden":
        st["ssh"]["permit_root_login"] = "no"
        st["ssh"]["password_auth"] = "no"
        st["ssh"]["hardened"] = True
        result["ok"] = "Updated /etc/ssh/sshd_config: PermitRootLogin no, PasswordAuthentication no, PubkeyAuthentication yes."
    elif ev == "ssh:reload":
        st["ssh"]["sshd_reloaded"] = True
        st["firewall"]["services"]["ssh"]["state"] = "active (running)"
        result["ok"] = "Validated sshd -t syntax and reloaded ssh.service with hardened key-only policy."
    else:
        return {"error": f"Unknown Linux GUI event: {ev}", "changed": False}, state, done

    if "error" not in result:
        st["seen"].append(ev)
        st["seen"] = st["seen"][-80:]
    st["log"] = (st.get("log") or [])[-29:] + [ev]
    _award(lab, state, done)
    result["changed"] = True
    return result, state, done


def _award(lab: dict, state: dict, done: list):
    st = state.get("linuxgui") or {}
    rules = dict(DEFAULT_GUI_RULES)
    rules.update(lab.get("gui_rules") or {})
    seen = st.get("seen") or []
    for o in lab.get("objectives") or []:
        oid = o["id"]
        if oid in done:
            continue
        rule = rules.get(oid)
        if not rule:
            continue
        if isinstance(rule, tuple) and rule[0] == "any":
            ok = any(r in seen for r in rule[1:])
        else:
            ok = rule in seen
        if ok:
            done.append(oid)


LINUX_GUI_LABS = [
    {
        "id": "linux-gui-network",
        "title": "Ubuntu GNOME GUI — NetworkManager & Static IPv4/DNS",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-5.1"],
        "blurb": "Configure static IPv4/CIDR, default gateway, and DNS servers in GNOME Settings → Network (nm-connection-editor) alongside the bash terminal.",
        "intro": "Ticket INC-9104: Support workstation novak-lnx-01 needs a static IPv4 address (10.20.40.15/24, gateway 10.20.40.1, DNS 10.20.40.10) configured in GNOME Network Settings and applied to eth0.",
        "success_msg": "You configured static IPv4/CIDR, gateway, and DNS in GNOME NetworkManager and verified the active eth0 profile.",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_network", "text": "Open GNOME Settings → Network (Wired eth0 properties)"},
            {"id": "configure_ipv4", "text": "Switch IPv4 Method to Manual and save 10.20.40.15/24, gateway 10.20.40.1, DNS 10.20.40.10"},
            {"id": "apply_connection", "text": "Apply the NetworkManager profile to cycle eth0 with the new IPv4 configuration"},
        ],
        "hints": [
            "Click GNOME Settings (Network) on the left Ubuntu Dock or top bar",
            "Select Manual IPv4, enter 10.20.40.15 / 24, Gateway 10.20.40.1, DNS 10.20.40.10, and click Save IPv4 Profile",
            "Click Apply & Reconnect eth0",
        ],
        "solution": {
            "events": [
                ("open:network", {}),
                ("net:save_manual", {"method": "manual", "ipv4": "10.20.40.15", "prefix": "24", "gateway": "10.20.40.1", "dns": "10.20.40.10"}),
                ("net:apply", {}),
            ]
        },
    },
    {
        "id": "linux-gui-disks",
        "title": "Ubuntu GNOME GUI — GNOME Disks, SMART & /etc/fstab Mounts",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-3.1"],
        "blurb": "Inspect NVMe/SATA drives in GNOME Disks, run a SMART health assessment, and mount /dev/sdb1 persistently at /srv/data.",
        "intro": "Ticket SR-9208: Verify NVMe SMART health on /dev/nvme0n1 and mount the secondary ext4 partition /dev/sdb1 at /srv/data with persistent /etc/fstab mount options.",
        "success_msg": "You verified NVMe SMART health and mounted /dev/sdb1 at /srv/data with persistent /etc/fstab options in GNOME Disks.",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_disks", "text": "Open GNOME Disks (gnome-disks) from the Ubuntu Dock"},
            {"id": "check_smart", "text": "Run SMART Data & Self-Tests on /dev/nvme0n1 to confirm disk health"},
            {"id": "mount_sdb1", "text": "Mount /dev/sdb1 (ext4) at /srv/data with persistent /etc/fstab options"},
        ],
        "hints": [
            "Click GNOME Disks on the left Ubuntu Dock",
            "Click Run SMART Self-Test on /dev/nvme0n1",
            "Click Mount /dev/sdb1 at /srv/data (Save to /etc/fstab)",
        ],
        "solution": {
            "events": [
                ("open:disks", {}),
                ("disks:smart", {}),
                ("disks:mount_sdb1", {"mountpoint": "/srv/data", "fstab_opts": "defaults,noatime,nofail"}),
            ]
        },
    },
    {
        "id": "linux-gui-firewall",
        "title": "Ubuntu GNOME GUI — GUFW Firewall & Systemd Daemon Control",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-10.1"],
        "blurb": "Enable UFW host firewall in GUFW, allow OpenSSH (22/tcp) and HTTPS (443/tcp), and start ssh.service in System Monitor.",
        "intro": "Ticket INC-9315: Harden workstation novak-lnx-01 by enabling the UFW firewall (Deny Incoming, Allow Outgoing), permitting 22/tcp (SSH) and 443/tcp (HTTPS), and starting ssh.service.",
        "success_msg": "UFW is enabled with least-privilege rules for 22/tcp and 443/tcp, and ssh.service is active (running).",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_firewall", "text": "Open GUFW Firewall & Systemd Services from the Ubuntu Dock"},
            {"id": "enable_ufw", "text": "Enable the UFW Firewall (Incoming: Deny, Outgoing: Allow)"},
            {"id": "allow_ssh_https", "text": "Enable ALLOW IN rules for 22/tcp (OpenSSH) and 443/tcp (HTTPS)"},
            {"id": "restart_ssh", "text": "Start / Restart ssh.service in the Systemd Services panel"},
        ],
        "hints": [
            "Click Firewall & Services on the Ubuntu Dock",
            "Toggle UFW Status to Enabled",
            "Click Allow 22/tcp (SSH) & 443/tcp (HTTPS)",
            "Click Start / Restart next to ssh.service",
        ],
        "solution": {
            "events": [
                ("open:firewall", {}),
                ("fw:enable", {}),
                ("fw:allow_ssh_https", {}),
                ("svc:restart:ssh", {}),
            ]
        },
    },
    {
        "id": "linux-gui-users",
        "title": "Ubuntu GNOME GUI — Users, Sudo Privileges & Nautilus Permissions",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-9.3"],
        "blurb": "Unlock technician account tech1, grant sudo (Administrator) access in GNOME Users, and set 750 executable permissions in Nautilus Files.",
        "intro": "Ticket SR-9402: Onboard Tier-1 technician Jordan Vance (tech1) by unlocking their account and enabling Administrator (sudo) privileges in GNOME Users, then open Nautilus Files to mark /home/trainee/support/backup.sh executable (750).",
        "success_msg": "Account tech1 is unlocked with sudo privileges, and backup.sh has mode 750 (rwxr-x---) in Nautilus.",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_users", "text": "Open GNOME Users & Accounts from the Ubuntu Dock"},
            {"id": "unlock_tech1", "text": "Unlock the locked technician account tech1"},
            {"id": "grant_sudo", "text": "Enable Administrator (sudo group) access for tech1"},
            {"id": "set_nautilus_perms", "text": "In Nautilus File Permissions, set /home/trainee/support/backup.sh to 750 (executable)"},
        ],
        "hints": [
            "Click GNOME Users on the Ubuntu Dock",
            "Click Unlock Account for tech1, then click Grant Administrator (sudo)",
            "Switch to Nautilus Files & Permissions and click Apply 750 (rwxr-x--- + Executable) on backup.sh",
        ],
        "solution": {
            "events": [
                ("open:users", {}),
                ("users:unlock:tech1", {}),
                ("users:sudo:tech1", {}),
                ("files:chmod:backup.sh:750", {}),
            ]
        },
    },
    {
        "id": "linux-gui-logs",
        "title": "Ubuntu GNOME GUI — GNOME Logs (journalctl) & Brute-Force Triage",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-10.4", "NO-5.1"],
        "blurb": "Filter systemd-journald security logs in GNOME Logs (gnome-logs), isolate an SSH brute-force attacker IP (198.51.100.77), block it via Fail2Ban/UFW, and vacuum journal storage.",
        "intro": "Ticket SEC-9510: Workstation novak-lnx-01 alerted on repeated authentication failures and /var/log/journal disk growth. Use GNOME Logs + Bash to filter ssh.service errors, block attacker IP 198.51.100.77, and vacuum journal logs to 100 MB.",
        "success_msg": "You filtered ssh.service error logs, blocked brute-force source 198.51.100.77, and vacuumed persistent journald logs.",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_logs", "text": "Open GNOME Logs (gnome-logs / journalctl viewer) from the Ubuntu Dock"},
            {"id": "filter_ssh_logs", "text": "Filter journal events to ssh.service (Priority: Error/Critical) to identify the brute-force IP"},
            {"id": "ban_attacker_ip", "text": "Block brute-force attacker IP 198.51.100.77 in Fail2Ban / UFW Quarantine"},
            {"id": "vacuum_journal", "text": "Vacuum persistent systemd-journald logs to 100 MB (journalctl --vacuum-size=100M)"},
        ],
        "hints": [
            "Click GNOME Logs on the left Ubuntu Dock",
            "Click Filter ssh.service Errors (journalctl -u ssh -p err)",
            "Click Block 198.51.100.77 (Fail2Ban / UFW Deny)",
            "Click Vacuum Journal to 100 MB",
        ],
        "solution": {
            "events": [
                ("open:logs", {}),
                ("logs:filter_ssh", {}),
                ("logs:ban:198.51.100.77", {}),
                ("logs:vacuum", {}),
            ]
        },
    },
    {
        "id": "linux-gui-processes",
        "title": "Ubuntu GNOME GUI — System Monitor, Runaway PID & Memory Triage",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-11.3"],
        "blurb": "Inspect live CPU and memory consumption in GNOME System Monitor, terminate a runaway worker process (PID 4412 at 98% CPU), and tune vm.swappiness=10.",
        "intro": "Ticket INC-9604: Support workstation novak-lnx-01 is sluggish with fan noise at 100%. Open GNOME System Monitor to identify the runaway process (stress-ng-worker, PID 4412), terminate it cleanly, and tune kernel vm.swappiness=10.",
        "success_msg": "You identified and terminated runaway PID 4412 in GNOME System Monitor and tuned kernel vm.swappiness=10.",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_processes", "text": "Open GNOME System Monitor (Processes & Resources) from the Ubuntu Dock"},
            {"id": "terminate_runaway", "text": "Identify and terminate runaway process stress-ng-worker (PID 4412 consuming 98.4% CPU)"},
            {"id": "tune_swappiness", "text": "Apply kernel memory tuning (vm.swappiness=10) to prevent premature swap thrashing"},
        ],
        "hints": [
            "Click GNOME System Monitor on the left Ubuntu Dock",
            "Click Terminate PID 4412 (stress-ng-worker)",
            "Click Apply vm.swappiness=10",
        ],
        "solution": {
            "events": [
                ("open:processes", {}),
                ("proc:kill:4412", {}),
                ("proc:swappiness:10", {}),
            ]
        },
    },
    {
        "id": "linux-gui-packages",
        "title": "Ubuntu GNOME GUI — Package Manager (APT) & Scheduled Cron Backups",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-10.3", "IT-12.3"],
        "blurb": "Refresh stale APT package repositories in Ubuntu Software & Updates, install unattended-upgrades, and enable the nightly 02:00 cron backup verification job.",
        "intro": "Ticket SR-9712: Workstation novak-lnx-01 has a 42-day-old APT metadata cache and missing nightly backup verification. Refresh APT repositories, install unattended-upgrades, and enable the 02:00 cron schedule.",
        "success_msg": "APT repositories are synced, unattended-upgrades is active, and the 02:00 nightly backup cron job is enabled.",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_packages", "text": "Open Ubuntu Software & Cron Scheduler from the Ubuntu Dock"},
            {"id": "apt_update_cache", "text": "Refresh APT repository metadata cache (apt update)"},
            {"id": "install_unattended", "text": "Install and enable unattended-upgrades for automated security patching"},
            {"id": "enable_backup_cron", "text": "Enable the nightly cron job (0 2 * * * /usr/local/bin/backup-verify.sh)"},
        ],
        "hints": [
            "Click Ubuntu Software & Cron on the left Ubuntu Dock",
            "Click Refresh APT Cache (apt update)",
            "Click Install unattended-upgrades",
            "Click Enable Nightly Cron Job (0 2 * * *)",
        ],
        "solution": {
            "events": [
                ("open:packages", {}),
                ("pkg:apt_update", {}),
                ("pkg:install:unattended-upgrades", {}),
                ("pkg:cron_enable", {}),
            ]
        },
    },
    {
        "id": "linux-gui-ssh",
        "title": "Ubuntu GNOME GUI — Passwords & Keys (Seahorse) & OpenSSH Hardening",
        "kind": "linuxgui",
        "sme_status": "verified",
        "minutes": 20,
        "course_objectives": ["IT-9.1", "IT-10.1", "NO-5.2"],
        "blurb": "Generate an Ed25519 SSH keypair in GNOME Passwords & Keys (seahorse), disable root and password login in sshd_config, and reload ssh.service.",
        "intro": "Ticket SEC-9820: Replace cleartext SSH password logins on novak-lnx-01 with Ed25519 public-key authentication, enforce PermitRootLogin no and PasswordAuthentication no, and reload ssh.service.",
        "success_msg": "You generated an Ed25519 keypair, hardened /etc/ssh/sshd_config (PermitRootLogin no, PasswordAuthentication no), and reloaded ssh.service.",
        "initial_state": {"hostname": "novak-lnx-01", "user": "trainee"},
        "objectives": [
            {"id": "open_ssh_keys", "text": "Open GNOME Passwords & Keys (Seahorse & OpenSSH Hardening) from the Ubuntu Dock"},
            {"id": "generate_ed25519", "text": "Generate an Ed25519 SSH keypair (~/.ssh/id_ed25519.pub) and add it to authorized_keys"},
            {"id": "harden_sshd_config", "text": "Set PermitRootLogin no and PasswordAuthentication no in OpenSSH Server policy"},
            {"id": "reload_sshd_service", "text": "Validate sshd -t syntax and reload ssh.service"},
        ],
        "hints": [
            "Click Passwords & SSH Keys on the left Ubuntu Dock",
            "Click Generate Ed25519 Keypair",
            "Click Apply Hardened sshd_config (PermitRootLogin no & PasswordAuthentication no)",
            "Click Validate & Reload ssh.service",
        ],
        "solution": {
            "events": [
                ("open:ssh", {}),
                ("ssh:keygen", {}),
                ("ssh:harden", {}),
                ("ssh:reload", {}),
            ]
        },
    },
]
