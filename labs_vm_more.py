"""Round-2 real Linux VM labs (v86, tools/vm_image): logs, cron, users/sudo, packages, firewall, disk, SSH keys,
scripting, a DNS chain and a multi-VM DHCP/route fault. Same format as labs_vm.py; graded against real machine state."""
import hashlib
import random

from labs_vm import IMAGE, _m, _prelude

SYSLOG = "/etc/init.d/S01syslogd start >/dev/null 2>&1\n"


def _h(v):
    """Answers are compared as hashes so the probe sent to the browser does not contain them."""
    return hashlib.sha256((v + "\n").encode()).hexdigest()[:16]


def _ans(key, value, path="/root/SR-5120.txt"):
    return (f"[ \"$(grep -i '^{key}[[:space:]]*=' {path} | tail -1 | cut -d= -f2- | tr -d ' \\r' | tr 'A-Z' 'a-z' "
            f"| sha256sum | cut -c1-16)\" = {_h(value)} ]")


# --------------------------------------------------------------------------------------------- 1: log investigation
def _logs():
    r = random.Random(5120)
    host = "novak-web-03"

    def ln(day, t, fac, msg):
        return f"Oct {day} {t} {host} {fac} {msg}"

    def ts(h, m, s):
        return f"{h:02d}:{m:02d}:{s:02d}"
    today, old, older = [], [], []
    pid = 800
    for day, buf in ((15, older), (16, old), (17, today)):
        for h in range(0, 24, 3):
            buf.append(ln(day, ts(h, 1, 2), "cron.info", f"crond[211]: USER root pid {pid} cmd /usr/local/bin/rotate-logs"))
            pid += 7
            buf.append(ln(day, ts(h, 17, 40), "auth.info", f"sshd[{pid}]: Accepted publickey for deploy from 10.0.5.20 port {40000 + pid} ssh2: ED25519 SHA256:q2Vd1Xk"))
            buf.append(ln(day, ts(h, 18, 5), "daemon.info", "udhcpc: lease of 10.0.5.33 obtained from 10.0.5.1, lease time 3600"))
    older.append(ln(15, "02:30:01", "cron.info", "crond[211]: USER root pid 1201 cmd /usr/local/bin/backup.sh"))
    older.append(ln(15, "02:30:04", "user.err", "backup[1203]: ERROR: rsync to nas01.novak.lab::nightly failed: connection refused (code 10)"))
    older.append(ln(15, "02:30:04", "user.err", "backup[1203]: backup aborted, 0 files copied"))
    old.append(ln(16, "14:02:51", "kern.warn", "kernel: php-fpm invoked oom-killer: gfp_mask=0x140cca(GFP_HIGHUSER_MOVABLE), order=0"))
    old.append(ln(16, "14:02:51", "kern.err", "kernel: Out of memory: Killed process 2211 (php-fpm) total-vm:612448kB, anon-rss:401220kB"))
    old.append(ln(16, "14:02:53", "daemon.notice", "init: php-fpm respawned"))
    users = ["admin", "oracle", "root", "svc-backup", "ubuntu", "test"]
    t = 3 * 3600 + 12 * 60
    for i in range(37):
        u = users[i % len(users)]
        inval = "invalid user " if u in ("admin", "oracle", "ubuntu", "test") else ""
        t += r.randint(2, 9)
        today.append(ln(17, ts(t // 3600, t // 60 % 60, t % 60), "auth.info",
                        f"sshd[{3000 + i}]: Failed password for {inval}{u} from 203.0.113.77 port {50000 + r.randint(0, 9999)} ssh2"))
        if i % 9 == 4:
            today.append(ln(17, ts(t // 3600, t // 60 % 60, t % 60 + 0), "auth.info",
                            f"sshd[{3100 + i}]: Failed password for root from 198.51.100.23 port {40000 + i} ssh2"))
    for i in range(2):
        today.append(ln(17, ts(9, 40 + i, 11), "auth.info", f"sshd[{3200 + i}]: Failed password for deploy from 192.0.2.10 port 41{i}22 ssh2"))
    t += 6
    today.append(ln(17, ts(t // 3600, t // 60 % 60, t % 60), "auth.info", "sshd[3071]: Accepted password for svc-backup from 203.0.113.77 port 51544 ssh2"))
    today.append(ln(17, ts(t // 3600, t // 60 % 60 + 1, 3), "authpriv.notice",
                    "sudo: svc-backup : user NOT in sudoers ; TTY=pts/0 ; PWD=/home/svc-backup ; USER=root ; COMMAND=/bin/sh"))
    key = lambda s: s[7:15]
    return [sorted(b, key=key) for b in (today, old, older)]


_LT, _LO, _LOO = _logs()
_LOG_SETUP = _prelude("novak-web-03") + "mkdir -p /var/log\ncat > /var/log/messages <<'EOF'\n" + "\n".join(_LT) + \
    "\nEOF\ncat > /var/log/messages.0 <<'EOF'\n" + "\n".join(_LO) + "\nEOF\ncat > /var/log/messages.1 <<'EOF'\n" + \
    "\n".join(_LOO) + "\nEOF\ngzip -f /var/log/messages.1\nuseradd -m svc-backup 2>/dev/null\n" + SYSLOG
_ASK = "/root/SR-5120.txt"
LOGS = {
    "id": "linux-vm-logs",
    "title": "Real Linux VM — Security Log Triage",
    "kind": "vm",
    "blurb": "Three days of real syslog files (one rotated and compressed) on a real Linux server. Use grep, sort, uniq, "
             "wc and zcat to answer the incident questions, preserve the evidence and log your finding.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "preserve", "text": "Preserve the evidence first: copy /var/log/messages* to /root/evidence and record SHA-256 sums in /root/evidence/SHA256SUMS"},
        {"id": "attacker", "text": "attacker_ip = the address with the most failed SSH passwords in /var/log/messages"},
        {"id": "count", "text": "failed_count = how many failed passwords came from that address"},
        {"id": "breach", "text": "breached_user = the account that address finally logged in as"},
        {"id": "oom", "text": "oom_process = the process the kernel's OOM killer killed (yesterday's log)"},
        {"id": "backup", "text": "backup_target = the host the nightly backup failed to reach (the compressed log)"},
        {"id": "record", "text": "Log a line containing SR-5120 to syslog with logger and confirm it in /var/log/messages"},
    ],
    "intro": "SR-5120 (security): novak-web-03 may have been compromised. Write each answer to /root/SR-5120.txt as "
             "key=value lines (attacker_ip=…, failed_count=…, breached_user=…, oom_process=…, backup_target=…). "
             "The logs are real files: /var/log/messages (today), messages.0 (yesterday) and messages.1.gz (rotated, "
             "compressed). Copy them aside before you start — investigators must be able to show the evidence was not altered.",
    "success_msg": "Incident answered from real logs: evidence hashed, attacker, count, breached account, OOM victim and backup target found.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM and wait for #.", "Start VM."],
        "preserve": ["Copy with cp -p (keeps timestamps); sha256sum writes checkable sums.",
                     "mkdir -p /root/evidence ; cp -p /var/log/messages* /root/evidence/ ; cd /root/evidence ; sha256sum messages* > SHA256SUMS ; cd"],
        "attacker": ["grep the failures, cut out the address field, then sort | uniq -c | sort -rn.",
                     "grep 'Failed password' /var/log/messages | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn ; echo attacker_ip=… >> /root/SR-5120.txt"],
        "count": ["grep -c counts matching lines.", "grep 'Failed password' /var/log/messages | grep -c '203.0.113.77'"],
        "breach": ["Failed is not the only sshd result — look for Accepted from the same address.",
                   "grep 'Accepted' /var/log/messages | grep 203.0.113.77"],
        "oom": ["The kernel says 'Out of memory: Killed process'.", "grep -i 'out of memory' /var/log/messages.0"],
        "backup": ["grep cannot read gzip data directly; zcat decompresses to stdout.", "zcat /var/log/messages.1.gz | grep -i backup"],
        "record": ["logger -t TAG 'text' writes to syslog.", "logger -t SR-5120 'SR-5120 findings filed' ; grep SR-5120 /var/log/messages"],
    },
    "course_objectives": ["IT-9.1", "IT-10.4", "NO-5.1"],
    "minutes": 35,
    "palette": ["grep ", "grep -c ", "zcat ", "| sort | uniq -c | sort -rn", "awk '{print $(NF-3)}'", "tail -n 20 ", "less ",
                "sha256sum ", "logger -t ", "cat /root/SR-5120.txt", "clear"],
    "fallback": ["linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "web-03", "novak-web-03")], setup={"vm": _LOG_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "preserve", "sh": "[ -f /root/evidence/messages.1.gz ] && [ -f /root/evidence/messages.0 ] && cd /root/evidence && sha256sum -c SHA256SUMS",
         "show": "ls /root/evidence 2>&1 | tr '\\n' ' '", "why": "/root/evidence needs the three log files and a passing SHA256SUMS — now: {v}"},
        {"id": "attacker", "sh": _ans("attacker_ip", "203.0.113.77"), "hist": [r"grep\b.*(Failed|ailed pass)"],
         "show": f"grep -i '^attacker_ip' {_ASK} 2>&1 | tail -1", "why": "attacker_ip is missing or wrong ({v}). Count failures per source address."},
        {"id": "count", "sh": _ans("failed_count", "37"), "hist": [r"grep\s+(-[a-zA-Z]*c|.*\|\s*wc\s+-l)|\bwc\s+-l|uniq\s+-c"],
         "show": f"grep -i '^failed_count' {_ASK} 2>&1 | tail -1", "why": "failed_count is missing or wrong ({v})."},
        {"id": "breach", "sh": _ans("breached_user", "svc-backup"), "show": f"grep -i '^breached_user' {_ASK} 2>&1 | tail -1",
         "why": "breached_user is missing or wrong ({v}). Did that address ever succeed?"},
        {"id": "oom", "sh": _ans("oom_process", "php-fpm"), "show": f"grep -i '^oom_process' {_ASK} 2>&1 | tail -1",
         "why": "oom_process is missing or wrong ({v})."},
        {"id": "backup", "sh": _ans("backup_target", "nas01.novak.lab"), "hist": [r"\bzcat\b|gunzip\s+-c|gzip\s+-d?c|zgrep|zless"],
         "show": f"grep -i '^backup_target' {_ASK} 2>&1 | tail -1", "why": "backup_target is missing or wrong ({v}), or you have not read the .gz log."},
        {"id": "record", "sh": "grep -q 'SR-5120' /var/log/messages", "hist": [r"^logger\b", r"grep\b.*SR-5120|tail\b.*messages"],
         "why": "Log a line with SR-5120 using logger, then find it in /var/log/messages."},
    ],
    "solution": {"vm_commands": [
        "mkdir -p /root/evidence", "cp -p /var/log/messages* /root/evidence/",
        "cd /root/evidence && sha256sum messages* > SHA256SUMS && cd /root",
        "grep 'Failed password' /var/log/messages | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn",
        "echo attacker_ip=203.0.113.77 > /root/SR-5120.txt",
        "grep 'Failed password' /var/log/messages | grep -c 203.0.113.77", "echo failed_count=37 >> /root/SR-5120.txt",
        "grep Accepted /var/log/messages | grep 203.0.113.77", "echo breached_user=svc-backup >> /root/SR-5120.txt",
        "grep -i 'out of memory' /var/log/messages.0", "echo oom_process=php-fpm >> /root/SR-5120.txt",
        "zcat /var/log/messages.1.gz | grep -i backup", "echo backup_target=nas01.novak.lab >> /root/SR-5120.txt",
        "logger -t SR-5120 'SR-5120 findings filed'", "grep SR-5120 /var/log/messages"]},
}

# --------------------------------------------------------------------------------------------- 2: cron
_CRON_SETUP = _prelude("novak-ops-01") + SYSLOG + r"""mkdir -p /usr/local/bin /var/backups
cat > /usr/local/bin/backup.sh <<'EOF'
#!/bin/sh
# nightly config backup (SR-4630)
tar cf - /etc 2>/dev/null | gzip > /var/backups/etc-$(date +%Y%m%d).tar.gz && logger -t backup "etc backed up"
EOF
cat > /usr/local/bin/rotate-logs <<'EOF'
#!/bin/sh
find /var/log -name '*.old' -mtime +7 -exec rm -f {} \;
EOF
cat > /usr/local/bin/heartbeat <<'EOF'
#!/bin/sh
date '+%F %T heartbeat' >> /var/log/heartbeat.log
EOF
chmod 755 /usr/local/bin/backup.sh /usr/local/bin/heartbeat; chmod 644 /usr/local/bin/rotate-logs
useradd -m -s /bin/sh reports; mkdir -p /home/reports/bin
printf '#!/bin/sh\necho "daily report $(date +%%F)" >> /home/reports/daily.log\n' > /home/reports/bin/daily.sh
chmod 755 /home/reports/bin/daily.sh; chown -R reports:reports /home/reports/bin
printf '# m h dom mon dow command\n0 2 * * * backup.sh\n*/5 * * * * /usr/local/bin/rotate-logs\n' | crontab -
"""
CRON = {
    "id": "linux-vm-cron",
    "title": "Real Linux VM — Cron Troubleshooting",
    "kind": "vm",
    "blurb": "Real crond and real crontabs. Find why nightly jobs never run, fix the schedule and paths, schedule a job "
             "for another user, enable cron at boot and prove a job really ran.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "inspect", "text": "List root's crontab and check whether the cron daemon is running"},
        {"id": "running", "text": "Start the cron daemon"},
        {"id": "enabled", "text": "Enable cron at boot (link /etc/init.d/S50crond to crond)"},
        {"id": "backup", "text": "Run /usr/local/bin/backup.sh at 02:30, Monday to Friday (full path)"},
        {"id": "exec", "text": "Make /usr/local/bin/rotate-logs executable so its job can run"},
        {"id": "reports", "text": "As user reports, run /home/reports/bin/daily.sh at 07:30 on weekdays (crontab -u)"},
        {"id": "proof", "text": "Add an every-minute job for /usr/local/bin/heartbeat and show it really ran (/var/log/heartbeat.log)"},
    ],
    "intro": "SR-4630: no config backup since the server was rebuilt, and logs are piling up. The backup must run at "
             "02:30 Monday–Friday; the reports team needs their daily script at 07:30 on weekdays under their own "
             "account. This is real BusyBox crond: edit crontabs with crontab -l > file, change the file, crontab file "
             "(there is no full-screen editor in this console).",
    "success_msg": "cron is running, enabled at boot, both schedules are correct and the heartbeat job really ran.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM.", "Start VM."],
        "inspect": ["crontab -l shows the table; service crond status (or ps) shows the daemon.", "crontab -l ; service crond status"],
        "running": ["Init scripts live in /etc/init.d.", "service crond start"],
        "enabled": ["Scripts named S??name in /etc/init.d start at boot.", "ln -s crond /etc/init.d/S50crond"],
        "backup": ["Fields: minute hour day-of-month month day-of-week. cron's PATH is tiny — always use full paths.",
                   "crontab -l > /tmp/c ; sed -i 's#^0 2 \\* \\* \\* backup.sh#30 2 * * 1-5 /usr/local/bin/backup.sh#' /tmp/c ; crontab /tmp/c"],
        "exec": ["A script without the x bit fails with 'permission denied' every 5 minutes.", "chmod 755 /usr/local/bin/rotate-logs"],
        "reports": ["crontab -u USER FILE installs a table for that user.",
                    "echo '30 7 * * 1-5 /home/reports/bin/daily.sh' > /tmp/r ; crontab -u reports /tmp/r ; crontab -u reports -l"],
        "proof": ["* * * * * means every minute. Wait for the minute to turn over, then look at the log.",
                  "crontab -l > /tmp/c ; echo '* * * * * /usr/local/bin/heartbeat' >> /tmp/c ; crontab /tmp/c ; sleep 70 ; cat /var/log/heartbeat.log"],
    },
    "course_objectives": ["IT-9.1", "IT-12.3"],
    "minutes": 30,
    "palette": ["crontab -l", "crontab -l > /tmp/c", "crontab /tmp/c", "crontab -u reports ", "service crond ", "cat /tmp/c",
                "sed -i ", "chmod 755 ", "cat /var/log/cron.log", "clear"],
    "fallback": ["linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "ops-01", "novak-ops-01")], setup={"vm": _CRON_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "inspect", "hist": [r"^crontab\s+(-u\s+\w+\s+)?-l", r"(service|/etc/init\.d/)\s*crond\s+status|^ps\b|pidof\s+crond|pgrep"],
         "why": "Look before you change: crontab -l and service crond status."},
        {"id": "running", "sh": "pidof crond", "why": "crond is not running."},
        {"id": "enabled", "sh": "[ -L /etc/init.d/S50crond ] && readlink /etc/init.d/S50crond | grep -q 'crond$'",
         "show": "ls -l /etc/init.d/ | grep -i cron | tr -s ' ' | cut -d' ' -f9- | tr '\\n' ' '", "why": "No S50crond link to crond in /etc/init.d ({v})."},
        {"id": "backup", "sh": "crontab -l | grep -Eq '^30[[:space:]]+2[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+(1-5|mon-fri)[[:space:]]+/usr/local/bin/backup\\.sh'",
         "show": "crontab -l | grep backup", "why": "root's backup line is: {v} — it needs 30 2 * * 1-5 /usr/local/bin/backup.sh."},
        {"id": "exec", "sh": "[ -x /usr/local/bin/rotate-logs ]", "why": "rotate-logs is still not executable."},
        {"id": "reports", "sh": "crontab -u reports -l | grep -Eq '^30[[:space:]]+7[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+(1-5|mon-fri)[[:space:]]+/home/reports/bin/daily\\.sh'",
         "show": "crontab -u reports -l 2>&1 | grep -v '^#' | head -2", "why": "reports' crontab: {v}"},
        {"id": "proof", "sh": "crontab -l | grep -Eq '^\\*[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+/usr/local/bin/heartbeat' && [ -s /var/log/heartbeat.log ] && grep -q heartbeat /var/log/cron.log",
         "show": "tail -1 /var/log/heartbeat.log 2>&1", "hist": [r"heartbeat\.log|cron\.log"],
         "why": "The heartbeat has not run yet ({v}). Is crond running? Wait for the next minute, then read /var/log/heartbeat.log."},
    ],
    "solution": {"vm_commands": [
        "crontab -l", "service crond status", "service crond start", "ln -s crond /etc/init.d/S50crond",
        "crontab -l > /tmp/c", "sed -i 's#^0 2 \\* \\* \\* backup.sh#30 2 * * 1-5 /usr/local/bin/backup.sh#' /tmp/c",
        "echo '* * * * * /usr/local/bin/heartbeat' >> /tmp/c", "crontab /tmp/c", "chmod 755 /usr/local/bin/rotate-logs",
        "echo '30 7 * * 1-5 /home/reports/bin/daily.sh' > /tmp/r", "crontab -u reports /tmp/r", "crontab -u reports -l",
        "sleep 75", "cat /var/log/heartbeat.log", "tail -3 /var/log/cron.log"]},
}

# --------------------------------------------------------------------------------------------- 3: users, groups and sudo
_USR_SETUP = _prelude("novak-srv-07") + SYSLOG + r"""useradd -m -s /bin/sh jdoe; echo 'jdoe:Summer2024!' | chpasswd
mkdir -p /srv/helpdesk; chmod 755 /srv/helpdesk; echo 'shift handover notes' > /srv/helpdesk/README
cat > /etc/sudoers.d/90-temp <<'EOF'
# temporary access for project Falcon (2024) - remove when done
jdoe ALL=(ALL) NOPASSWD: ALL
EOF
chmod 440 /etc/sudoers.d/90-temp
"""
USERS = {
    "id": "linux-vm-users",
    "title": "Real Linux VM — Users, Groups & Sudo",
    "kind": "vm",
    "blurb": "Real shadow utilities and real sudo 1.9. Onboard two technicians into a group, give the group a shared "
             "setgid folder and only the sudo rights it needs, and offboard a leaver without deleting evidence.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "group", "text": "Create the group helpdesk"},
        {"id": "users", "text": "Create users ana and ben with home directories, both members of helpdesk"},
        {"id": "firstlogin", "text": "Give ana and ben an initial password and force a change at first login (chage -d 0)"},
        {"id": "share", "text": "/srv/helpdesk: group helpdesk, mode 2770 (members only; new files inherit the group)"},
        {"id": "sudo", "text": "Drop-in /etc/sudoers.d/40-helpdesk (mode 440): %helpdesk may run only /usr/sbin/service and /usr/bin/tail; visudo -c passes"},
        {"id": "leaver", "text": "Offboard jdoe: lock the account (keep it and its home) and remove the leftover sudo drop-in 90-temp"},
        {"id": "verify", "text": "Verify what ana may run with sudo -l -U ana"},
    ],
    "intro": "HR-2291: ana and ben join the help desk today; jdoe left last Friday. Help-desk staff must restart services "
             "and read logs, nothing more. jdoe's account must be locked, not deleted (HR may need his files). Real "
             "accounts, real /etc/shadow, real sudo — a syntax error in sudoers really breaks sudo, so check with visudo -c.",
    "success_msg": "Onboarded and offboarded for real: group, users, forced password change, setgid share, a narrow sudo rule and a locked leaver.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM.", "Start VM."],
        "group": ["groupadd NAME.", "groupadd helpdesk"],
        "users": ["useradd -m creates the home directory; -G adds supplementary groups.", "useradd -m -s /bin/sh -G helpdesk ana ; useradd -m -s /bin/sh -G helpdesk ben"],
        "firstlogin": ["chpasswd reads user:password lines; chage -d 0 expires the password now.",
                       "printf 'ana:Welcome-2026\\nben:Welcome-2026\\n' | chpasswd ; chage -d 0 ana ; chage -d 0 ben"],
        "share": ["chgrp sets the group; the leading 2 in 2770 is the setgid bit.", "chgrp helpdesk /srv/helpdesk ; chmod 2770 /srv/helpdesk ; ls -ld /srv/helpdesk"],
        "sudo": ["%group in sudoers means every member. List the commands by full path, separated by commas.",
                 "echo '%helpdesk ALL=(root) /usr/sbin/service, /usr/bin/tail' > /etc/sudoers.d/40-helpdesk ; chmod 440 /etc/sudoers.d/40-helpdesk ; visudo -c"],
        "leaver": ["usermod -L (or passwd -l) locks the password; userdel would destroy evidence.", "usermod -L jdoe ; rm /etc/sudoers.d/90-temp ; sudo -l -U jdoe"],
        "verify": ["sudo -l -U USER lists that user's rights (as root).", "sudo -l -U ana"],
    },
    "course_objectives": ["IT-9.1", "IT-10.1", "IT-9.3"],
    "minutes": 35,
    "palette": ["groupadd ", "useradd -m -s /bin/sh -G helpdesk ", "id ", "chpasswd", "chage -l ", "chage -d 0 ", "chgrp ", "chmod 2770 ",
                "visudo -c", "sudo -l -U ", "usermod -L ", "ls -ld ", "clear"],
    "fallback": ["win-ad-users", "linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "srv-07", "novak-srv-07")], setup={"vm": _USR_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "group", "sh": "grep -q '^helpdesk:' /etc/group", "why": "There is no group helpdesk yet."},
        {"id": "users", "sh": "for u in ana ben; do id -nG $u | grep -qw helpdesk && [ -d /home/$u ] || exit 1; done",
         "show": "for u in ana ben; do printf '%s: ' $u; id -nG $u 2>&1 | tr '\\n' ' '; done", "why": "ana and ben must exist with homes and be in helpdesk — {v}"},
        {"id": "firstlogin", "sh": "for u in ana ben; do awk -F: -v u=$u '$1==u && $2 ~ /^\\$/ && $3==\"0\" {f=1} END {exit !f}' /etc/shadow || exit 1; done",
         "show": "awk -F: '$1==\"ana\"||$1==\"ben\" {printf \"%s pw=%s lastchg=%s; \", $1, substr($2,1,1)==\"$\"?\"set\":\"none\", $3}' /etc/shadow",
         "why": "Each needs a password set and lastchg 0 (forced change): {v}"},
        {"id": "share", "sh": "ls -ld /srv/helpdesk | grep -Eq '^drwxrws---[^ ]* +[0-9]+ +[a-z]+ +helpdesk '",
         "show": "ls -ld /srv/helpdesk | tr -s ' ' | cut -d' ' -f1,3,4", "why": "/srv/helpdesk is {v}; want drwxrws--- group helpdesk."},
        {"id": "sudo", "sh": "visudo -c && ls -l /etc/sudoers.d/40-helpdesk | grep -q '^-r--r-----' && L=$(sudo -l -U ana) && echo \"$L\" | grep -q /usr/sbin/service && echo \"$L\" | grep -q /usr/bin/tail && ! echo \"$L\" | grep -Eq '\\) (NOPASSWD: )?ALL[[:space:]]*$'",
         "show": "visudo -c 2>&1 | tail -1; sudo -l -U ana 2>&1 | tail -1", "why": "The help-desk rule is not right yet: {v}"},
        {"id": "leaver", "sh": "awk -F: '$1==\"jdoe\" && $2 ~ /^!/ {f=1} END {exit !f}' /etc/shadow && [ -d /home/jdoe ] && [ ! -e /etc/sudoers.d/90-temp ] && sudo -l -U jdoe 2>&1 | grep -q 'not allowed'",
         "show": "awk -F: '$1==\"jdoe\"{print ($2 ~ /^!/ ? \"locked\" : \"NOT locked\")}' /etc/shadow; ls /etc/sudoers.d | tr '\\n' ' '",
         "why": "jdoe: {v} — lock the account, keep /home/jdoe, remove 90-temp."},
        {"id": "verify", "hist": [r"-U\s+(ana|ben)\b|^su\b.*\b(ana|ben)\b"], "why": "Check the result as an auditor would: sudo -l -U ana."},
    ],
    "solution": {"vm_commands": [
        "groupadd helpdesk", "useradd -m -s /bin/sh -G helpdesk ana", "useradd -m -s /bin/sh -G helpdesk ben",
        "printf 'ana:Welcome-2026\\nben:Welcome-2026\\n' | chpasswd", "chage -d 0 ana", "chage -d 0 ben",
        "chgrp helpdesk /srv/helpdesk", "chmod 2770 /srv/helpdesk", "ls -ld /srv/helpdesk",
        "echo '%helpdesk ALL=(root) /usr/sbin/service, /usr/bin/tail' > /etc/sudoers.d/40-helpdesk",
        "chmod 440 /etc/sudoers.d/40-helpdesk", "visudo -c", "usermod -L jdoe", "rm /etc/sudoers.d/90-temp",
        "sudo -l -U jdoe", "sudo -l -U ana"]},
}

# --------------------------------------------------------------------------------------------- 4: packages and a service
_PKG_SETUP = _prelude("novak-web-05") + SYSLOG + r"""mkdir -p /srv/www /etc/default; ln -sf /var/lib/*-repo /var/lib/novak-repo 2>/dev/null || true; sed -i "s/-repo$/novak-repo/; s|/.*-repo|/var/lib/novak-repo|" /etc/apk/repositories
echo '<h1>Novak intranet OK</h1>' > /srv/www/index.html
printf '# webd settings\nPORT=8080\nDOCROOT=/srv/www\n' > /etc/default/webd
cat > /etc/init.d/webd <<'EOF'
#!/bin/sh
# webd - intranet web server (darkhttpd). Enable at boot: ln -s webd /etc/init.d/S50webd
DAEMON="webd"; EXE="/usr/bin/darkhttpd"; PIDFILE="/var/run/webd.pid"; PORT=80; DOCROOT=/var/www
[ -r /etc/default/webd ] && . /etc/default/webd
start() { printf 'Starting %s: ' "$DAEMON"
  [ -x "$EXE" ] || { echo "FAIL ($EXE not found - is the package installed?)"; logger -t init "$DAEMON: $EXE not found"; return 1; }
  if "$EXE" "$DOCROOT" --port "$PORT" --daemon --pidfile "$PIDFILE" --log /var/log/webd.log >/tmp/.webd 2>&1; then echo OK; logger -t init "$DAEMON started on port $PORT"
  else echo "FAIL ($(grep -v copyright /tmp/.webd | tail -1))"; logger -t init "$DAEMON failed: $(tail -1 /tmp/.webd)"; return 1; fi; }
stop() { printf 'Stopping %s: ' "$DAEMON"; start-stop-daemon -K -q -p "$PIDFILE" && { rm -f "$PIDFILE"; echo OK; } || { echo FAIL; return 1; } }
status() { if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then echo "$DAEMON is running (pid $(cat $PIDFILE))"; else echo "$DAEMON is stopped"; return 3; fi }
case "$1" in start|stop|status) "$1";; restart) stop; sleep 1; start;; *) echo "Usage: $0 {start|stop|restart|status}"; exit 1;; esac
EOF
chmod 755 /etc/init.d/webd
sed -i 's|^\([^#]\)|# disabled during migration SR-4410: \1|' /etc/apk/repositories
start-stop-daemon -S -b -x /usr/bin/socat -- TCP-LISTEN:8080,fork,reuseaddr 'SYSTEM:echo devtest-listener'
"""
PACKAGES = {
    "id": "linux-vm-packages",
    "title": "Real Linux VM — Packages & Services",
    "kind": "vm",
    "blurb": "A real Alpine package manager with a signed offline repository. The intranet web service is down: find the "
             "missing package, the disabled repository and the process squatting on the port, then fix and enable it.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "diagnose", "text": "Try the service and read its error, then search for the package (apk search / apk info)"},
        {"id": "repo", "text": "Re-enable the package repository /var/lib/novak-repo in /etc/apk/repositories and apk update"},
        {"id": "install", "text": "Install the web server package that provides /usr/bin/darkhttpd"},
        {"id": "conflict", "text": "Find what is listening on port 8080 (ss -tlnp) and stop it"},
        {"id": "running", "text": "Start webd so http://127.0.0.1:8080/ serves the intranet page"},
        {"id": "enabled", "text": "Enable webd at boot (/etc/init.d/S50webd → webd)"},
        {"id": "verify", "text": "Verify the page with curl or wget"},
    ],
    "intro": "SR-4410: after last night's migration the intranet (webd, port 8080) is down. Nothing has been "
             "reinstalled yet. Real apk 2.14, real init script, real sockets — the error messages are the real ones.",
    "success_msg": "Intranet back: repository re-enabled, darkhttpd installed from the signed repo, port squatter removed, webd running and enabled.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM.", "Start VM."],
        "diagnose": ["Start it and read the message; then ask apk about the package.", "service webd start ; apk search darkhttpd"],
        "repo": ["apk reads its repositories from /etc/apk/repositories; a # comments a line out.",
                 "cat /etc/apk/repositories ; sed -i 's|^# disabled during migration SR-4410: ||' /etc/apk/repositories ; apk update"],
        "install": ["apk add PACKAGE.", "apk add darkhttpd"],
        "conflict": ["ss -tlnp shows listening TCP sockets with the owning process.", "ss -tlnp ; kill PID (the socat process on :8080)"],
        "running": ["Start it again now the port is free.", "service webd start ; service webd status"],
        "enabled": ["S50 links in /etc/init.d start at boot.", "ln -s webd /etc/init.d/S50webd"],
        "verify": ["Fetch the page.", "curl http://127.0.0.1:8080/"],
    },
    "course_objectives": ["IT-9.1", "IT-10.3"],
    "minutes": 30,
    "palette": ["service webd ", "apk search ", "apk info ", "apk add ", "apk update", "cat /etc/apk/repositories", "ss -tlnp",
                "kill ", "tail /var/log/messages", "curl http://127.0.0.1:8080/", "clear"],
    "fallback": ["w11-services", "linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "web-05", "novak-web-05")], setup={"vm": _PKG_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "diagnose", "hist": [r"(service\s+webd|/etc/init\.d/webd)\s+(start|status|restart)", r"^apk\s+(search|info|policy|list)\b"],
         "why": "Read the service's own error first (service webd start), then ask apk (apk search darkhttpd)."},
        {"id": "repo", "sh": "grep -Eq '^[[:space:]]*/var/lib/novak-repo' /etc/apk/repositories", "hist": [r"^apk\s+(update|add)\b"],
         "show": "grep novak-repo /etc/apk/repositories", "why": "The repository line is still disabled: {v}"},
        {"id": "install", "sh": "apk info -e darkhttpd && [ -x /usr/bin/darkhttpd ]", "why": "darkhttpd is not installed."},
        {"id": "conflict", "sh": "! ss -tlnp | grep ':8080 ' | grep -q socat", "hist": [r"^(ss|netstat)\b.*-[a-z]*l"],
         "show": "ss -tlnp | grep ':8080 ' | grep -o 'users:.*' | head -1", "why": "Port 8080 is held by {v} (find it with ss -tlnp)."},
        {"id": "running", "sh": "service webd status && curl -s -m 2 http://127.0.0.1:8080/ | grep -q 'Novak intranet OK'", "secs": 5,
         "show": "service webd status 2>&1", "why": "webd: {v}"},
        {"id": "enabled", "sh": "[ -L /etc/init.d/S50webd ] && readlink /etc/init.d/S50webd | grep -q 'webd$'", "why": "No S50webd link to webd yet."},
        {"id": "verify", "hist": [r"^(curl|wget)\b.*(127\.0\.0\.1|localhost):8080"], "why": "Test it like a user: curl http://127.0.0.1:8080/"},
    ],
    "solution": {"vm_commands": [
        "service webd start", "apk search darkhttpd", "cat /etc/apk/repositories",
        "sed -i 's|^# disabled during migration SR-4410: ||' /etc/apk/repositories", "apk update", "apk add --no-progress darkhttpd",
        "service webd start", "ss -tlnp", "kill $(pidof socat)", "service webd start", "ln -s webd /etc/init.d/S50webd",
        "curl -s http://127.0.0.1:8080/"]},
}

# --------------------------------------------------------------------------------------------- 5: host firewall, two VMs
_PORTCHECK = r"""cat > /usr/bin/portcheck <<'EOF'
#!/bin/sh
# portcheck HOST PORT - a TCP connect test (2 s) with socat. open / closed (RST) / filtered (no answer)
[ $# -eq 2 ] || { echo "usage: portcheck HOST PORT"; exit 2; }
if socat -T1 /dev/null TCP:$1:$2,connect-timeout=2 2>/tmp/.pc; then echo "$1:$2 open"
elif grep -qi refused /tmp/.pc; then echo "$1:$2 closed (connection refused - RST)"; exit 1
else echo "$1:$2 filtered (no answer)"; exit 1; fi
EOF
chmod 755 /usr/bin/portcheck
"""
_FW_HOSTS = "printf '10.20.0.10 web-01\\n10.20.0.50 adm-ws\\n' >> /etc/hosts\n"
_FW_SRV = _prelude("web-01") + SYSLOG + _FW_HOSTS + r"""ip link set eth0 up; ip addr add 10.20.0.10/24 dev eth0
apk add -q --no-progress darkhttpd >/dev/null 2>&1; mkdir -p /srv/www /etc/iptables; echo 'web-01 public site' > /srv/www/index.html
darkhttpd /srv/www --port 80 --daemon --pidfile /var/run/web.pid >/dev/null 2>&1
service sshd start >/dev/null 2>&1
start-stop-daemon -S -b -x /usr/bin/socat -- TCP-LISTEN:2323,fork,reuseaddr 'SYSTEM:echo legacy admin console'
iptables -F; iptables -P INPUT ACCEPT
"""
_FW_WS = _prelude("adm-ws") + _FW_HOSTS + "ip link set eth0 up; ip addr add 10.20.0.50/24 dev eth0\nmkdir -p /usr/local/bin\n" + _PORTCHECK
_IPS = "iptables -S INPUT"
FIREWALL = {
    "id": "linux-vm-firewall",
    "title": "Real Linux VMs — iptables Host Firewall",
    "kind": "vm",
    "blurb": "Two real Linux machines on a virtual LAN. Lock down a web server with real netfilter rules: default deny, "
             "stateful return traffic, web for everyone, SSH only from the admin workstation — and prove it from the client.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (web-01 and adm-ws)"},
        {"id": "baseline", "text": "Baseline first: from adm-ws, portcheck web-01 port 2323 and look at web-01's listening ports and rules"},
        {"id": "state", "text": "web-01: accept loopback and ESTABLISHED,RELATED traffic"},
        {"id": "web", "text": "web-01: accept TCP 80 from anyone, and ping (ICMP echo-request)"},
        {"id": "ssh", "text": "web-01: accept TCP 22 only from adm-ws (10.20.0.50)"},
        {"id": "policy", "text": "web-01: set the INPUT policy to DROP (2323 and everything else is now blocked)"},
        {"id": "saved", "text": "web-01: save the rules to /etc/iptables/rules-save (iptables-save)"},
        {"id": "proof", "text": "adm-ws: prove it — the web page and port 22 work, port 2323 is filtered"},
    ],
    "intro": "CHG-5530: web-01 (10.20.0.10) is exposed with every port open, including a legacy admin console on 2323. "
             "Apply the approved policy: default deny inbound, web (80) and ping for everyone, SSH (22) only from the "
             "admin workstation adm-ws (10.20.0.50). These are real iptables rules in a real kernel (nf_tables backend). "
             "Your console is a serial line, so a wrong rule cannot lock you out — on a real server it could.",
    "success_msg": "Firewall verified from the client: 80 and 22 open for the admin, 2323 filtered, rules saved.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start both VMs.", "Start VMs."],
        "baseline": ["portcheck is a small socat script (cat /usr/bin/portcheck). ss -tlnp lists listeners.",
                     "on adm-ws: portcheck web-01 2323 ; on web-01: ss -tlnp ; iptables -S"],
        "state": ["Rule order matters; the first match wins. Allow replies to connections web-01 makes itself.",
                  "iptables -A INPUT -i lo -j ACCEPT ; iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"],
        "web": ["-p tcp --dport 80; ICMP type echo-request.", "iptables -A INPUT -p tcp --dport 80 -j ACCEPT ; iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT"],
        "ssh": ["-s limits a rule to a source address.", "iptables -A INPUT -p tcp -s 10.20.0.50 --dport 22 -j ACCEPT"],
        "policy": ["The policy applies when no rule matches.", "iptables -P INPUT DROP ; iptables -L INPUT -n -v"],
        "saved": ["iptables-save prints the whole ruleset in restorable form.", "iptables-save > /etc/iptables/rules-save"],
        "proof": ["Test from the client after the change. DROP shows as filtered (no answer), REJECT as closed.",
                  "on adm-ws: curl http://web-01/ ; portcheck web-01 22 ; portcheck web-01 2323"],
    },
    "course_objectives": ["NO-4.3", "NO-5.3", "IT-10.1"],
    "minutes": 40,
    "palette": ["iptables -S", "iptables -L INPUT -n -v --line-numbers", "iptables -A INPUT ", "-p tcp --dport ", "-j ACCEPT",
                "iptables -P INPUT DROP", "iptables -D INPUT ", "iptables-save", "ss -tlnp", "portcheck web-01 ", "curl http://web-01/", "clear"],
    "fallback": ["w11-firewall", "rtr-vlan-acl"],
    "vm": dict(IMAGE, machines=[_m("srv", "web-01", "web-01", ["dmz"]), _m("ws", "adm-ws", "adm-ws", ["dmz"])],
               setup={"srv": _FW_SRV, "ws": _FW_WS},
               net={"segments": ["dmz"], "topology": "adm-ws 10.20.0.50 ── DMZ switch ── web-01 10.20.0.10 (web :80, ssh :22, legacy :2323)"}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "baseline", "seq": [r"^\[ws\]\s*(portcheck|socat|curl)\b.*2323", r"^\[srv\]\s*(ss|netstat)\b|^\[srv\]\s*iptables\s+(-[a-zA-Z]*[LS])"],
         "before": r"^\[srv\]\s*iptables\b.*-P\s+INPUT\s+DROP", "why": "Before the policy change: portcheck 2323 from adm-ws, then ss -tlnp / iptables -S on web-01."},
        {"id": "state", "on": "srv", "sh": f"{_IPS} | grep -Eq -- '-i lo .*-j ACCEPT' && {_IPS} | grep -Eq -- '--(ct)?state (RELATED,ESTABLISHED|ESTABLISHED,RELATED|ESTABLISHED) -j ACCEPT'",
         "show": f"{_IPS} | grep -c -- '-A'", "why": "Need a loopback ACCEPT and an ESTABLISHED,RELATED ACCEPT rule ({v} rules now)."},
        {"id": "web", "on": "srv", "sh": f"{_IPS} | grep -- '--dport 80 ' | grep -v -- '-s ' | grep -q -- '-j ACCEPT' && {_IPS} | grep -- '-p icmp' | grep -q -- '-j ACCEPT'",
         "why": "Need ACCEPT rules for TCP 80 from anywhere and for ICMP echo-request."},
        {"id": "ssh", "on": "srv", "sh": f"{_IPS} | grep -- '--dport 22 ' | grep -q -- '-s 10.20.0.50/32 .*-j ACCEPT' && ! {_IPS} | grep -- '--dport 22 ' | grep -v -- '-s 10.20.0.50/32' | grep -q ACCEPT",
         "show": f"{_IPS} | grep -- '--dport 22' | head -2", "why": "SSH must be accepted only from 10.20.0.50: {v}"},
        {"id": "policy", "on": "srv", "sh": f"{_IPS} | grep -q -- '^-P INPUT DROP'", "show": f"{_IPS} | head -1", "why": "INPUT policy: {v}"},
        {"id": "saved", "on": "srv", "sh": "grep -q '^:INPUT DROP' /etc/iptables/rules-save && grep -q -- '--dport 22' /etc/iptables/rules-save",
         "why": "/etc/iptables/rules-save is missing or does not hold the final rules."},
        {"id": "proof", "on": "ws", "sh": "curl -s -m 3 http://10.20.0.10/ | grep -q 'public site' && portcheck 10.20.0.10 22 && ! portcheck 10.20.0.10 2323",
         "secs": 12, "show": "for p in 22 2323; do portcheck 10.20.0.10 $p; done | tr '\\n' ' '",
         "hist": [r"^\[ws\]\s*(portcheck|socat)\b.*\b2323\b"], "why": "From adm-ws: {v}"},
    ],
    "solution": {"vm_commands": [
        "[ws] portcheck web-01 2323", "[srv] ss -tlnp", "[srv] iptables -S",
        "[srv] iptables -A INPUT -i lo -j ACCEPT", "[srv] iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
        "[srv] iptables -A INPUT -p tcp --dport 80 -j ACCEPT", "[srv] iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT",
        "[srv] iptables -A INPUT -p tcp -s 10.20.0.50 --dport 22 -j ACCEPT", "[srv] iptables -P INPUT DROP",
        "[srv] iptables -L INPUT -n -v", "[srv] iptables-save > /etc/iptables/rules-save",
        "[ws] curl -s http://web-01/", "[ws] portcheck web-01 22", "[ws] portcheck web-01 2323"]},
}

# --------------------------------------------------------------------------------------------- 6: disk, partitions, mounts, fstab
_Q3 = "region,q3\nnorth,41200\nsouth,38950\n"
_DISK_SETUP = _prelude("novak-file-02") + r"""mkdir -p /srv/data/reports /mnt/olddata
printf 'region,q3\nnorth,41200\nsouth,38950\n' > /srv/data/reports/q3.csv; echo 'app data v2' > /srv/data/README
echo 'UUID=0c5e1f2a-7d3b-4e5f-9a1b-2c3d4e5f6a7b /mnt/olddata ext4 defaults 0 2   # old data disk (removed)' >> /etc/fstab
"""
_FDISK = "printf 'n\\np\\n1\\n\\n+32M\\nn\\np\\n2\\n\\n\\nt\\n2\\n82\\nw\\n' | fdisk /dev/sda"
DISK = {
    "id": "linux-vm-disk",
    "title": "Real Linux VM — Disk, Swap & fstab",
    "kind": "vm",
    "blurb": "A real blank 48 MB ATA disk is attached to a real Linux server. Partition it, format it, move the "
             "application data onto it, mount it persistently by UUID, add swap and repair a stale fstab entry.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "identify", "text": "Identify the new disk (lsblk or fdisk -l)"},
        {"id": "partition", "text": "Partition /dev/sda: sda1 of 32 MB (Linux) and sda2 with the rest (type 82, Linux swap)"},
        {"id": "format", "text": "Format sda1 as ext4 with the label appdata"},
        {"id": "migrate", "text": "Move /srv/data onto sda1 without losing files (copy, then mount sda1 on /srv/data)"},
        {"id": "fstab", "text": "Mount it at boot: an fstab line for /srv/data by UUID (not /dev/sda1)"},
        {"id": "swap", "text": "Make sda2 swap, turn it on and add it to fstab"},
        {"id": "clean", "text": "Remove the stale /mnt/olddata entry so findmnt --verify and mount -a are clean"},
    ],
    "intro": "SR-4777: novak-file-02 is running out of space. A new 48 MB disk has been attached. Put the application data "
             "(/srv/data) on its own ext4 partition and add some swap. Device names can change between boots, so mount "
             "by UUID. Someone left an entry for a removed disk in /etc/fstab. A real kernel, a real disk, real "
             "fdisk/mkfs/mount — a mistake here really loses data, so copy before you mount over a directory.",
    "success_msg": "New disk in service: partitioned, ext4 'appdata' holding /srv/data by UUID, swap on, fstab verified clean.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM.", "Start VM."],
        "identify": ["lsblk lists block devices; the new one has no partitions yet.", "lsblk ; fdisk -l /dev/sda"],
        "partition": ["fdisk: n (new) p (primary) number, first sector (Enter), size (+32M); t changes the type; w writes.",
                      "fdisk /dev/sda then n p 1 Enter +32M, n p 2 Enter Enter, t 2 82, w — or pipe the answers: " + _FDISK],
        "format": ["mkfs.ext4 -L LABEL DEVICE.", "mkfs.ext4 -L appdata /dev/sda1 ; blkid /dev/sda1"],
        "migrate": ["Mounting over a directory hides what was in it. Mount the new filesystem somewhere temporary, copy, then remount.",
                    "mkdir /mnt/new ; mount /dev/sda1 /mnt/new ; cp -a /srv/data/. /mnt/new/ ; umount /mnt/new ; mount /dev/sda1 /srv/data ; ls -R /srv/data"],
        "fstab": ["blkid -s UUID -o value /dev/sda1 prints only the UUID.",
                  "echo \"UUID=$(blkid -s UUID -o value /dev/sda1) /srv/data ext4 defaults 0 2\" >> /etc/fstab"],
        "swap": ["mkswap, swapon, then an fstab line with type swap.",
                 "mkswap /dev/sda2 ; swapon /dev/sda2 ; echo \"UUID=$(blkid -s UUID -o value /dev/sda2) none swap sw 0 0\" >> /etc/fstab ; cat /proc/swaps"],
        "clean": ["findmnt --verify checks every fstab line; delete the one for the missing disk.",
                  "sed -i '/olddata/d' /etc/fstab ; findmnt --verify ; mount -a"],
    },
    "course_objectives": ["IT-9.1", "IT-3.1", "IT-9.4"],
    "minutes": 35,
    "palette": ["lsblk", "lsblk -f", "fdisk -l /dev/sda", "fdisk /dev/sda", "mkfs.ext4 -L ", "blkid", "mount ", "umount ", "cp -a ",
                "cat /etc/fstab", "findmnt --verify", "mount -a", "mkswap ", "swapon ", "df -h", "clear"],
    "fallback": ["w11-disk"],
    "vm": dict(IMAGE, machines=[_m("vm", "file-02", "novak-file-02", disk_mb=48)], setup={"vm": _DISK_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "identify", "hist": [r"^lsblk\b|^fdisk\s+-l|^blkid\b|cat\s+/proc/partitions"], "why": "Identify the new disk first (lsblk)."},
        {"id": "partition", "sh": "[ -e /sys/block/sda/sda1 ] && [ -e /sys/block/sda/sda2 ] && [ $(cat /sys/block/sda/sda1/size) -ge 60000 ] && [ $(cat /sys/block/sda/sda1/size) -le 70000 ] && fdisk -l /dev/sda | grep '^/dev/sda2' | grep -qi swap",
         "show": "lsblk -rno NAME,SIZE /dev/sda | tr '\\n' ' '", "why": "Partitions now: {v}(want sda1 32M, sda2 the rest, type 82)."},
        {"id": "format", "sh": "[ \"$(blkid -s TYPE -o value /dev/sda1)\" = ext4 ] && [ \"$(blkid -s LABEL -o value /dev/sda1)\" = appdata ]",
         "show": "blkid /dev/sda1 2>&1 || echo no filesystem", "why": "sda1: {v}"},
        {"id": "migrate", "sh": f"[ \"$(findmnt -n -o SOURCE /srv/data)\" = /dev/sda1 ] && [ \"$(sha256sum < /srv/data/reports/q3.csv | cut -c1-16)\" = {hashlib.sha256(_Q3.encode()).hexdigest()[:16]} ] && [ -f /srv/data/README ]",
         "show": "findmnt -n -o SOURCE /srv/data || echo /srv/data is not a mount point; ls /srv/data 2>&1 | tr '\\n' ' '",
         "why": "/srv/data must be sda1 with reports/q3.csv and README intact: {v}"},
        {"id": "fstab", "sh": "U=$(blkid -s UUID -o value /dev/sda1) && [ -n \"$U\" ] && grep -Eq \"^UUID=\\\"?$U\\\"?[[:space:]]+/srv/data[[:space:]]+ext4\" /etc/fstab",
         "show": "grep /srv/data /etc/fstab || echo no /srv/data line", "why": "fstab: {v} — use UUID=… /srv/data ext4."},
        {"id": "swap", "sh": "grep -q '^/dev/sda2' /proc/swaps && awk '$3==\"swap\"' /etc/fstab | grep -q .",
         "show": "tail -n +2 /proc/swaps | cut -c1-30; awk '$3==\"swap\"' /etc/fstab", "why": "Swap: {v}"},
        {"id": "clean", "sh": "! grep -q olddata /etc/fstab && findmnt --verify && mount -a", "hist": [r"findmnt\s+--verify|^mount\s+-a"],
         "show": "findmnt --verify 2>&1 | tail -2", "why": "fstab is not clean yet: {v}"},
    ],
    "solution": {"vm_commands": [
        "lsblk", _FDISK, "lsblk /dev/sda", "mkfs.ext4 -q -L appdata /dev/sda1", "mkdir -p /mnt/new", "mount /dev/sda1 /mnt/new",
        "cp -a /srv/data/. /mnt/new/", "umount /mnt/new", "mount /dev/sda1 /srv/data", "ls -R /srv/data",
        "echo \"UUID=$(blkid -s UUID -o value /dev/sda1) /srv/data ext4 defaults 0 2\" >> /etc/fstab",
        "mkswap /dev/sda2", "swapon /dev/sda2", "echo \"UUID=$(blkid -s UUID -o value /dev/sda2) none swap sw 0 0\" >> /etc/fstab",
        "sed -i '/olddata/d' /etc/fstab", "findmnt --verify", "mount -a", "df -h /srv/data"]},
}

# --------------------------------------------------------------------------------------------- 7: SSH keys between two VMs
_REL = "release 1.4\n" + "".join(f"{i}\n" for i in range(1, 2001))
_SSH_HOSTS = "printf '10.40.0.10 app-01\\n10.40.0.21 dev-ws\\n' >> /etc/hosts\n"
_SSH_SRV = _prelude("app-01") + SYSLOG + _SSH_HOSTS + r"""ip link set eth0 up; ip addr add 10.40.0.10/24 dev eth0
useradd -m -s /bin/sh deploy; echo 'deploy:Deploy#2026' | chpasswd
sed -i 's/^PermitRootLogin .*/PermitRootLogin noo/' /etc/ssh/sshd_config
"""
# r5: OpenSSH 9.7 negotiates the post-quantum hybrid sntrup761x25519-sha512 by default. In the in-browser VM that
# key exchange alone costs ~20 s of client CPU per connection on a 4x-throttled (mid-range phone) page — measured
# 25.6 s per ssh vs 6.5 s with curve25519-sha256 — so every ssh/scp/ssh-copy-id and the grading probe crawled and the
# probe's 15/20 s watchdogs expired. dev-ws's client config pins curve25519-sha256 (the student is told why in the intro).
_KEX = "curve25519-sha256"
_SSH_WS = _prelude("dev-ws") + _SSH_HOSTS + r"""ip link set eth0 up; ip addr add 10.40.0.21/24 dev eth0
{ echo 'release 1.4'; seq 1 2000; } > /root/release-1.4.txt
printf '\n# Novak lab: classic X25519 key exchange - the post-quantum default (sntrup761x25519) is too slow in an in-browser VM\nHost *\n    KexAlgorithms %s\n' """ + _KEX + r""" >> /etc/ssh/ssh_config
"""
# the probe pins the KEX itself too (in case the student edits ssh_config); watchdogs stay generous for slow phones —
# they only matter when a connection hangs, a refused/denied login returns at once
_BATCH = f"-o BatchMode=yes -o ConnectTimeout=30 -o KexAlgorithms={_KEX}"
SSH = {
    "id": "linux-vm-ssh",
    "title": "Real Linux VMs — SSH Key Hardening",
    "kind": "vm",
    "blurb": "Real OpenSSH 9.7 on two real Linux VMs. Repair a broken sshd config, set up ed25519 key login for a deploy "
             "account, verify the host key, harden the server and copy a release with scp.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (dev-ws and app-01)"},
        {"id": "sshd", "text": "app-01: find why sshd will not start (sshd -t), fix the config and start it"},
        {"id": "key", "text": "dev-ws: generate an ed25519 key pair for root (no passphrase for this lab)"},
        {"id": "trust", "text": "dev-ws: connect once and accept app-01's host key (known_hosts)"},
        {"id": "installed", "text": "Install the public key for deploy@app-01 (ssh-copy-id) — .ssh 700, authorized_keys 600, owned by deploy"},
        {"id": "keylogin", "text": "dev-ws: ssh deploy@app-01 logs in with the key, no password"},
        {"id": "harden", "text": "app-01: PasswordAuthentication no and PermitRootLogin no, sshd restarted"},
        {"id": "refused", "text": "dev-ws: show a password login is now refused, and the key still works"},
        {"id": "copy", "text": "dev-ws: scp /root/release-1.4.txt to deploy's home on app-01"},
    ],
    "intro": "CHG-6120: the deploy pipeline on dev-ws must reach app-01 without stored passwords. The temporary deploy "
             "password is Deploy#2026 (you need it once, for ssh-copy-id). After key login works, password logins must "
             "be turned off. Two real VMs, real OpenSSH — the password prompt hides what you type and is never logged. "
             "Type exit to leave a remote session before you press Check my work. Note: dev-ws's /etc/ssh/ssh_config pins "
             "KexAlgorithms curve25519-sha256 because OpenSSH 9.x's default post-quantum hybrid key exchange "
             "(sntrup761x25519) takes ~20 s per login in an in-browser VM on a phone; real servers keep the default.",
    "success_msg": "Key-only SSH for real: sshd fixed, ed25519 key installed with correct permissions, passwords refused, release copied.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start both VMs.", "Start VMs."],
        "sshd": ["sshd -t tests the config and prints the bad line.", "on app-01: sshd -t ; sed -i 's/^PermitRootLogin noo/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config ; service sshd start"],
        "key": ["ssh-keygen -t ed25519; -N '' sets an empty passphrase, -f the file.", "on dev-ws: ssh-keygen -t ed25519 -N '' -f /root/.ssh/id_ed25519"],
        "trust": ["The first connection asks you to confirm the host key fingerprint — answer yes.", "on dev-ws: ssh-copy-id deploy@app-01 (answer yes, then the password)"],
        "installed": ["ssh-copy-id appends your public key to ~deploy/.ssh/authorized_keys with safe permissions.", "on dev-ws: ssh-copy-id deploy@app-01"],
        "keylogin": ["BatchMode=yes fails instead of asking for a password, so it proves the key works.", "on dev-ws: ssh -o BatchMode=yes deploy@app-01 hostname"],
        "harden": ["Edit /etc/ssh/sshd_config, test with sshd -t, restart.",
                   "on app-01: sed -i 's/^PasswordAuthentication .*/PasswordAuthentication no/; s/^PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config ; sshd -t ; service sshd restart"],
        "refused": ["Force password-only auth from the client and expect Permission denied (publickey).",
                    "on dev-ws: ssh -o PubkeyAuthentication=no -o BatchMode=yes deploy@app-01 ; ssh -o BatchMode=yes deploy@app-01 true"],
        "copy": ["scp SOURCE USER@HOST:PATH.", "on dev-ws: scp /root/release-1.4.txt deploy@app-01:"],
    },
    "course_objectives": ["NO-5.2", "IT-10.1", "IT-9.4"],
    "minutes": 40,
    "palette": ["sshd -t", "service sshd ", "ssh-keygen -t ed25519 -N '' -f /root/.ssh/id_ed25519", "ssh-copy-id deploy@app-01",
                "ssh -o BatchMode=yes deploy@app-01 ", "ssh -o PubkeyAuthentication=no deploy@app-01", "scp ", "ls -la ", "exit", "clear"],
    "fallback": ["linux-shell"],
    "vm": dict(IMAGE, machines=[_m("ws", "dev-ws", "dev-ws", ["lan"]), _m("srv", "app-01", "app-01", ["lan"])],
               setup={"ws": _SSH_WS, "srv": _SSH_SRV},
               net={"segments": ["lan"], "topology": "dev-ws 10.40.0.21 ── LAN switch ── app-01 10.40.0.10 (sshd)"}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "sshd", "on": "srv", "sh": "sshd -t && pidof sshd", "hist": [r"^\[srv\]\s*sshd\s+-t"],
         "show": "sshd -t 2>&1 | head -1; pidof sshd >/dev/null && echo running || echo not running", "why": "sshd on app-01: {v}"},
        {"id": "key", "on": "ws", "sh": "[ -f /root/.ssh/id_ed25519 ] && grep -q '^ssh-ed25519 ' /root/.ssh/id_ed25519.pub",
         "why": "No ed25519 key pair in /root/.ssh on dev-ws yet."},
        {"id": "trust", "on": "ws", "sh": "ssh-keygen -F app-01 >/dev/null || ssh-keygen -F 10.40.0.10 >/dev/null", "why": "app-01's host key is not in known_hosts yet."},
        {"id": "installed", "on": "srv", "sh": "grep -q '^ssh-ed25519 .* root@dev-ws' /home/deploy/.ssh/authorized_keys && ls -ld /home/deploy/.ssh | grep -q '^drwx------ .* deploy ' && ls -l /home/deploy/.ssh/authorized_keys | grep -Eq '^-rw-------.* deploy '",
         "show": "ls -ld /home/deploy/.ssh /home/deploy/.ssh/authorized_keys 2>&1 | tr -s ' ' | cut -d' ' -f1,3,9 | tr '\\n' ' '",
         "why": "deploy's key setup: {v} (want .ssh 700 and authorized_keys 600 owned by deploy, with dev-ws's key)."},
        {"id": "keylogin", "on": "ws", "sh": f"ssh {_BATCH} deploy@app-01 true", "secs": 60, "why": "Key login as deploy@app-01 does not work yet (or took over a minute on this device)."},
        {"id": "harden", "on": "srv", "sh": "sshd -T | grep -qx 'passwordauthentication no' && sshd -T | grep -qx 'permitrootlogin no' && pidof sshd",
         "show": "sshd -T 2>&1 | grep -E '^(passwordauthentication|permitrootlogin)' | tr '\\n' ' '", "why": "app-01 sshd: {v}"},
        {"id": "refused", "on": "ws", "sh": f"ssh {_BATCH} -o PubkeyAuthentication=no deploy@app-01 true 2>&1 | grep -q 'denied (publickey)' && ssh {_BATCH} deploy@app-01 true",
         "secs": 90, "hist": [r"^\[ws\]\s*ssh\b.*(PubkeyAuthentication=no|PreferredAuthentications=(password|keyboard))"],
         "show": f"ssh {_BATCH} -o PubkeyAuthentication=no deploy@app-01 true 2>&1 | tail -1",
         "why": "A password-only attempt should get 'Permission denied (publickey)': {v}. Did you restart sshd?"},
        {"id": "copy", "on": "srv", "sh": f"[ \"$(sha256sum < /home/deploy/release-1.4.txt | cut -c1-16)\" = {hashlib.sha256(_REL.encode()).hexdigest()[:16]} ] && ls -l /home/deploy/release-1.4.txt | grep -q ' deploy '",
         "hist": [r"^\[ws\]\s*scp\b"], "why": "/home/deploy/release-1.4.txt is missing or different on app-01."},
    ],
    "solution": {"vm_commands": [
        "[srv] service sshd start", "[srv] sshd -t", "[srv] sed -i 's/^PermitRootLogin noo/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config",
        "[srv] sshd -t", "[srv] service sshd start",
        "[ws] mkdir -p -m 700 /root/.ssh", "[ws] ssh-keygen -q -t ed25519 -N '' -f /root/.ssh/id_ed25519",
        "[ws] ssh-copy-id deploy@app-01", "[ws] yes", "[ws] Deploy#2026",
        "[ws] ssh -o BatchMode=yes deploy@app-01 hostname",
        "[srv] sed -i 's/^PasswordAuthentication .*/PasswordAuthentication no/; s/^PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config",
        "[srv] sshd -t", "[srv] service sshd restart",
        "[ws] ssh -o BatchMode=yes -o PubkeyAuthentication=no deploy@app-01 true", "[ws] ssh -o BatchMode=yes deploy@app-01 true",
        "[ws] scp /root/release-1.4.txt deploy@app-01:"]},
}

# --------------------------------------------------------------------------------------------- 8: shell scripting automation
_SCRIPT_STARTER = r"""#!/bin/sh
# app-backup.sh SOURCE_DIR DEST_DIR - archive SOURCE_DIR into DEST_DIR, keep the newest 3 archives
# TODO 1: fewer than 2 arguments -> print "usage: app-backup.sh SOURCE_DIR DEST_DIR" to stderr, exit 2
# TODO 2: SOURCE_DIR is not a directory -> error to stderr, logger -t app-backup "FAILED: ...", exit 1
# TODO 3: create DEST_DIR if needed; write DEST_DIR/<name of SOURCE_DIR>-YYYYmmdd-HHMMSS.tar.gz (BusyBox tar has no -z: tar cf - ... | gzip > FILE)
# TODO 4: delete all but the newest 3 archives of that name
# TODO 5: logger -t app-backup "backup ok: <archive>" and exit 0
echo "app-backup.sh: not implemented yet" >&2
exit 1
"""
_SCR_SETUP = _prelude("novak-ops-04") + SYSLOG + "mkdir -p /usr/local/bin /srv/app/conf /backup\necho 'db=10.0.0.5' > /srv/app/conf/app.ini; echo v3.2 > /srv/app/VERSION\n" + \
    "cat > /usr/local/bin/app-backup.sh <<'EOF'\n" + _SCRIPT_STARTER + "EOF\nchmod 644 /usr/local/bin/app-backup.sh\n"
_S = "/usr/local/bin/app-backup.sh"
_SCRIPT_LINES = [
    "#!/bin/sh", "# app-backup.sh SOURCE_DIR DEST_DIR - archive SOURCE_DIR into DEST_DIR, keep the newest 3",
    '[ $# -ge 2 ] || { echo "usage: app-backup.sh SOURCE_DIR DEST_DIR" >&2; exit 2; }',
    'SRC=$1; DEST=$2; N=$(basename "$SRC")',
    '[ -d "$SRC" ] || { echo "error: $SRC is not a directory" >&2; logger -t app-backup "FAILED: $SRC missing"; exit 1; }',
    'mkdir -p "$DEST" || exit 1', 'A="$DEST/$N-$(date +%Y%m%d-%H%M%S).tar.gz"',
    'tar cf - -C "$(dirname "$SRC")" "$N" | gzip > "$A" || { logger -t app-backup "FAILED: tar $SRC"; exit 1; }',
    'ls -1t "$DEST"/"$N"-*.tar.gz | tail -n +4 | xargs -r rm -f', 'logger -t app-backup "backup ok: $A"']


def _printf(lines, op):
    return "printf '%s\\n' " + " ".join("'" + ln + "'" for ln in lines) + f" {op} {_S}"


_ROT = ("rm -rf /tmp/pr && mkdir -p /tmp/pr/src/sub /tmp/pr/dst && echo x > /tmp/pr/src/sub/f.txt && "
        "for d in 01 02 03 04; do touch -d \"2024-01-$d 00:00:00\" /tmp/pr/dst/src-202401$d-000000.tar.gz; done && "
        f"{_S} /tmp/pr/src /tmp/pr/dst && [ $(ls /tmp/pr/dst | wc -l) -eq 3 ] && ls /tmp/pr/dst | grep -q 20240104 && "
        "ls /tmp/pr/dst | grep -q 20240103 && ! ls /tmp/pr/dst | grep -q 20240102")
SCRIPT = {
    "id": "linux-vm-script",
    "title": "Real Linux VM — Backup Automation",
    "kind": "vm",
    "blurb": "Write a real POSIX shell script and schedule it. The grader runs your script against test folders inside "
             "the VM — wrong arguments, a missing source, a real archive and rotation — and checks the exit codes.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "exec", "text": "/usr/local/bin/app-backup.sh starts with #!/bin/sh and is executable"},
        {"id": "usage", "text": "With fewer than two arguments it prints a usage line and exits 2"},
        {"id": "missing", "text": "With a missing source folder it exits 1 and creates no archive"},
        {"id": "archive", "text": "It writes DEST/NAME-YYYYmmdd-HHMMSS.tar.gz containing the source folder and exits 0"},
        {"id": "rotate", "text": "It keeps only the newest 3 archives of that name"},
        {"id": "logged", "text": "Each successful run logs 'backup ok' to syslog with the tag app-backup"},
        {"id": "schedule", "text": "Schedule it nightly at 01:15 for /srv/app → /backup in root's crontab, and run it once for real"},
    ],
    "intro": "AUTO-118: replace the manual nightly copy of /srv/app with a script. A starter with TODO comments is at "
             "/usr/local/bin/app-backup.sh (cat it). Write the file with printf or cat > file <<'EOF' … EOF — this "
             "console has no full-screen editor. The grader really runs your script with test folders, so behaviour "
             "matters, not wording.",
    "success_msg": "Your script behaves: usage and missing-source exit codes, real archives, rotation to 3, syslog lines, scheduled.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM.", "Start VM."],
        "exec": ["The first line must be #!/bin/sh; chmod +x adds the execute bit.", f"head -1 {_S} ; chmod 755 {_S}"],
        "usage": ["$# is the number of arguments; >&2 writes to stderr; exit 2.",
                  "[ $# -ge 2 ] || { echo \"usage: app-backup.sh SOURCE_DIR DEST_DIR\" >&2; exit 2; }"],
        "missing": ["[ -d \"$SRC\" ] tests for a directory.", "[ -d \"$SRC\" ] || { echo \"error: $SRC missing\" >&2; exit 1; }"],
        "archive": ["date +%Y%m%d-%H%M%S gives the timestamp. BusyBox tar has no -z here, so pipe: tar cf - -C PARENT NAME | gzip > ARCHIVE.",
                    "A=\"$DEST/$(basename \"$SRC\")-$(date +%Y%m%d-%H%M%S).tar.gz\" ; tar cf - -C \"$(dirname \"$SRC\")\" \"$(basename \"$SRC\")\" | gzip > \"$A\""],
        "rotate": ["List newest first (ls -1t), skip the first 3 (tail -n +4), delete the rest.",
                   "ls -1t \"$DEST\"/\"$N\"-*.tar.gz | tail -n +4 | xargs -r rm -f"],
        "logged": ["logger -t TAG MESSAGE.", "logger -t app-backup \"backup ok: $A\""],
        "schedule": ["minute hour * * * command.", f"echo '15 1 * * * {_S} /srv/app /backup' | crontab - ; {_S} /srv/app /backup ; ls /backup"],
    },
    "course_objectives": ["IT-9.1", "IT-12.3", "IT-12.4"],
    "minutes": 45,
    "palette": [f"cat {_S}", f"chmod 755 {_S}", "printf '%s\\n' ", f"{_S} /srv/app /backup", "echo $?", "ls -l /backup",
                "gzip -dc FILE | tar tf -", "crontab -l", "grep app-backup /var/log/messages", "clear"],
    "fallback": ["linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "ops-04", "novak-ops-04")], setup={"vm": _SCR_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "exec", "sh": f"[ -x {_S} ] && head -1 {_S} | grep -q '^#!/bin/sh'", "show": f"ls -l {_S} | cut -c1-10; head -1 {_S}",
         "why": "The script is {v} — needs #!/bin/sh and the x bit."},
        {"id": "usage", "sh": f"! grep -q 'not implemented yet' {_S} && {_S} >/tmp/.o 2>&1; [ $? -eq 2 ] && grep -qi usage /tmp/.o", "secs": 5,
         "show": f"{_S} >/tmp/.o 2>&1; echo \"exit=$? $(head -1 /tmp/.o)\"", "why": "Run with no arguments it gave: {v}"},
        {"id": "missing", "sh": f"! grep -q 'not implemented yet' {_S} && rm -rf /tmp/pm; {_S} /nonexistent/x /tmp/pm >/dev/null 2>&1; [ $? -eq 1 ] && [ -z \"$(ls /tmp/pm 2>/dev/null)\" ]", "secs": 5,
         "show": f"{_S} /nonexistent/x /tmp/pm >/dev/null 2>&1; echo exit=$?", "why": "With a missing source: {v} (want exit=1, no archive)."},
        {"id": "archive", "sh": f"rm -rf /tmp/pa && mkdir -p /tmp/pa/src/sub && echo x > /tmp/pa/src/sub/f.txt && {_S} /tmp/pa/src /tmp/pa/dst && "
                                "F=$(ls /tmp/pa/dst/src-[0-9]*-[0-9]*.tar.gz) && [ $(echo \"$F\" | wc -l) -eq 1 ] && "
                                "echo \"$F\" | grep -Eq 'src-[0-9]{8}-[0-9]{6}\\.tar\\.gz$' && gzip -dc $F | tar tf - | grep -q 'sub/f\\.txt$'", "secs": 8,
         "show": f"rm -rf /tmp/pa2; mkdir -p /tmp/pa2/src; {_S} /tmp/pa2/src /tmp/pa2/dst >/dev/null 2>&1; echo exit=$?; ls /tmp/pa2/dst 2>&1",
         "why": "A test run gave: {v}"},
        {"id": "rotate", "sh": _ROT, "secs": 8, "show": "ls /tmp/pr/dst 2>&1 | tr '\\n' ' '",
         "why": "After 4 old archives plus one new run, the folder held: {v}(want the newest 3)."},
        {"id": "logged", "sh": "grep -q 'app-backup.*backup ok' /var/log/messages", "why": "No 'backup ok' line from app-backup in /var/log/messages."},
        {"id": "schedule", "sh": f"crontab -l | grep -Eq '^15[[:space:]]+1[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+{_S}[[:space:]]+/srv/app[[:space:]]+/backup' && ls /backup/app-*.tar.gz",
         "show": "crontab -l 2>&1 | grep -v '^#' | head -1; ls /backup | head -2", "why": "Crontab/backups: {v}"},
    ],
    "solution": {"vm_commands": [
        f"cat {_S}", _printf(_SCRIPT_LINES[:5], ">"), _printf(_SCRIPT_LINES[5:], ">>"), f"chmod 755 {_S}",
        f"{_S}; echo $?", f"{_S} /nope /backup; echo $?", f"{_S} /srv/app /backup", "ls -l /backup",
        f"echo '15 1 * * * {_S} /srv/app /backup' | crontab -", "crontab -l", "grep app-backup /var/log/messages"]},
}

# --------------------------------------------------------------------------------------------- 9: DNS troubleshooting chain
_DNS_NET = {
    "segments": ["lan"],
    "services": {"name": "isp-resolver", "mac": "02:c1:77:00:03:01", "ifaces": [{"seg": "lan", "ip": "10.30.0.1", "bits": 24}],
                 "dns": {"records": {"www.example.com": "192.0.2.80", "updates.vendor.example": "198.51.100.44"}}},
    "topology": "ws-22 10.30.0.22 ── LAN ── dns-01 10.30.0.53 (dnsmasq, novak.lab) ── upstream resolver 10.30.0.1 (internet names)",
}
_DNS_HOSTS = "printf '10.30.0.53 dns-01.novak.lab dns-01\\n' >> /etc/hosts\n"
_DNS_SRV = _prelude("dns-01") + SYSLOG + _DNS_HOSTS + r"""ip link set eth0 up; ip addr add 10.30.0.53/24 dev eth0; ip route add default via 10.30.0.1
cat > /etc/dnsmasq.conf <<'EOF'
# dns-01: internal resolver for novak.lab (dnsmasq 2.90). Test: dnsmasq --test ; apply: service dnsmasq restart
listen-address=127.0.0.1
bind-interfaces
no-resolv
domain=novak.lab
local=/novak.lab/
addn-hosts=/etc/hosts.novak
user=dnsmasq
log-queries
EOF
cat > /etc/hosts.novak <<'EOF'
10.30.0.53  dns-01.novak.lab
10.30.0.99  intranet.novak.lab
10.30.0.25  mail.novak.lab
EOF
service dnsmasq start >/dev/null 2>&1
"""
_DNS_WS = _prelude("ws-22") + r"""ip link set eth0 up; ip addr add 10.30.0.22/24 dev eth0; ip route add default via 10.30.0.1
printf 'search corp.example\nnameserver 10.30.0.254\n' > /etc/resolv.conf
"""
_DR = "drill -Q"
DNS = {
    "id": "linux-vm-dns",
    "title": "Real Linux VMs — DNS Resolver Repair",
    "kind": "vm",
    "blurb": "A real client and a real dnsmasq resolver, with an upstream resolver on the virtual LAN. Follow a name from "
             "the client's resolv.conf to the server's listen address, its zone data and its forwarder until every name resolves.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (ws-22 and dns-01)"},
        {"id": "diagnose", "text": "ws-22: read /etc/resolv.conf and query intranet.novak.lab with drill or nslookup"},
        {"id": "client", "text": "ws-22: use the resolver 10.30.0.53 and the search domain novak.lab"},
        {"id": "listen", "text": "dns-01: answer queries from the LAN, not just from itself (listen address)"},
        {"id": "record", "text": "intranet.novak.lab must resolve to the new server 10.30.0.80"},
        {"id": "mx", "text": "Add mail for novak.lab: an MX record pointing at mail.novak.lab, and wiki.novak.lab as a CNAME of intranet"},
        {"id": "forward", "text": "dns-01: forward other names to the upstream resolver 10.30.0.1 (www.example.com must resolve on ws-22)"},
        {"id": "verify", "text": "ws-22: verify with both drill and nslookup after the fix"},
    ],
    "intro": "SR-5307: on ws-22 nothing resolves — not internal names, not the internet. dns-01 runs dnsmasq for novak.lab; "
             "the intranet moved to 10.30.0.80 last week and mail was never added. The upstream resolver is 10.30.0.1. "
             "Two real VMs, real dnsmasq and real drill/nslookup: the dig-like tool here is drill (same flags for "
             "the basics: drill NAME @SERVER, drill MX NAME). Changes to dnsmasq need a restart.",
    "success_msg": "Name resolution fixed end to end: client resolver, LAN listen address, corrected A record, MX + CNAME, and forwarding.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start both VMs.", "Start VMs."],
        "diagnose": ["The resolver the client asks is in /etc/resolv.conf.", "on ws-22: cat /etc/resolv.conf ; drill intranet.novak.lab"],
        "client": ["Two lines: search DOMAIN and nameserver ADDRESS.", "on ws-22: printf 'search novak.lab\\nnameserver 10.30.0.53\\n' > /etc/resolv.conf"],
        "listen": ["ss -ulnp shows what dnsmasq listens on; listen-address takes a comma-separated list.",
                   "on dns-01: sed -i 's/^listen-address=.*/listen-address=127.0.0.1,10.30.0.53/' /etc/dnsmasq.conf ; service dnsmasq restart"],
        "record": ["The novak.lab names come from addn-hosts=/etc/hosts.novak.", "on dns-01: sed -i 's/^10.30.0.99 /10.30.0.80 /' /etc/hosts.novak ; service dnsmasq restart"],
        "mx": ["dnsmasq: mx-host=DOMAIN,HOST,PREF and cname=ALIAS,TARGET.",
               "on dns-01: printf 'mx-host=novak.lab,mail.novak.lab,10\\ncname=wiki.novak.lab,intranet.novak.lab\\n' >> /etc/dnsmasq.conf ; dnsmasq --test ; service dnsmasq restart"],
        "forward": ["no-resolv means dnsmasq ignores resolv.conf; give it server=ADDRESS.",
                    "on dns-01: echo 'server=10.30.0.1' >> /etc/dnsmasq.conf ; service dnsmasq restart ; on ws-22: drill www.example.com"],
        "verify": ["Both tools ask the same resolver; nslookup also shows which server answered.", "on ws-22: drill intranet.novak.lab ; nslookup wiki.novak.lab"],
    },
    "course_objectives": ["NO-4.2", "IT-13.2", "IT-5.3"],
    "minutes": 40,
    "palette": ["cat /etc/resolv.conf", "drill ", "drill MX novak.lab", "nslookup ", "@10.30.0.53", "cat /etc/dnsmasq.conf", "dnsmasq --test",
                "service dnsmasq restart", "ss -ulnp", "cat /etc/hosts.novak", "sed -i ", "clear"],
    "fallback": ["win-dns-break", "win-nslookup-ok"],
    "vm": dict(IMAGE, machines=[_m("ws", "ws-22", "ws-22", ["lan"]), _m("dns", "dns-01", "dns-01", ["lan"])],
               setup={"ws": _DNS_WS, "dns": _DNS_SRV}, net=_DNS_NET),
    "vm_checks": [
        {"id": "boot"},
        {"id": "diagnose", "hist": [r"^\[ws\]\s*cat\s+/etc/resolv\.conf", r"^\[ws\]\s*(drill|nslookup|host|dig)\b.*intranet"],
         "why": "Start at the client: cat /etc/resolv.conf, then drill intranet.novak.lab on ws-22."},
        {"id": "client", "on": "ws", "sh": "grep -Eq '^nameserver[[:space:]]+10\\.30\\.0\\.53' /etc/resolv.conf && grep -Eq '^(search|domain)[[:space:]]+novak\\.lab' /etc/resolv.conf && ! grep -q 10.30.0.254 /etc/resolv.conf",
         "show": "grep -v '^#' /etc/resolv.conf | tr '\\n' ' '", "why": "ws-22 resolv.conf: {v}"},
        {"id": "listen", "on": "ws", "sh": f"{_DR} dns-01.novak.lab @10.30.0.53 | grep -q 10.30.0.53", "secs": 6,
         "show": "drill dns-01.novak.lab @10.30.0.53 2>&1 | grep -iE 'error|rcode' | head -1", "why": "dns-01 does not answer LAN queries yet ({v})."},
        {"id": "record", "on": "ws", "sh": f"[ \"$({_DR} intranet.novak.lab @10.30.0.53)\" = 10.30.0.80 ]", "secs": 6,
         "show": f"{_DR} intranet.novak.lab @10.30.0.53 2>&1 | head -1", "why": "intranet.novak.lab answers {v}; it moved to 10.30.0.80."},
        {"id": "mx", "on": "ws", "sh": f"drill MX novak.lab @10.30.0.53 | grep -Eq 'MX[[:space:]]+10[[:space:]]+mail\\.novak\\.lab' && drill wiki.novak.lab @10.30.0.53 | grep -Eq 'CNAME[[:space:]]+intranet\\.novak\\.lab'",
         "secs": 8, "show": "drill MX novak.lab @10.30.0.53 2>&1 | grep -E 'IN[[:space:]]+MX' | head -1", "why": "MX/CNAME not served yet ({v})."},
        {"id": "forward", "on": "ws", "sh": f"[ \"$({_DR} www.example.com)\" = 192.0.2.80 ]", "secs": 8, "fabric": "dns_fwd",
         "show": f"{_DR} www.example.com 2>&1 | head -1", "why": "www.example.com from ws-22: {v}"},
        {"id": "verify", "hist": [r"^\[ws\]\s*drill\b", r"^\[ws\]\s*nslookup\b"],
         "before": None, "why": "Check with both tools on ws-22: drill and nslookup."},
    ],
    "solution": {"vm_commands": [
        "[ws] cat /etc/resolv.conf", "[ws] drill intranet.novak.lab",
        "[ws] printf 'search novak.lab\\nnameserver 10.30.0.53\\n' > /etc/resolv.conf", "[ws] drill intranet.novak.lab",
        "[dns] ss -ulnp", "[dns] sed -i 's/^listen-address=.*/listen-address=127.0.0.1,10.30.0.53/' /etc/dnsmasq.conf",
        "[dns] sed -i 's/^10.30.0.99 /10.30.0.80 /' /etc/hosts.novak",
        "[dns] printf 'mx-host=novak.lab,mail.novak.lab,10\\ncname=wiki.novak.lab,intranet.novak.lab\\nserver=10.30.0.1\\n' >> /etc/dnsmasq.conf",
        "[dns] dnsmasq --test", "[dns] service dnsmasq restart",
        "[ws] drill intranet.novak.lab", "[ws] drill MX novak.lab", "[ws] nslookup wiki.novak.lab", "[ws] drill www.example.com"]},
}
DNS["vm_checks"][-1].pop("before")

# --------------------------------------------------------------------------------------------- 10: multi-VM DHCP + route fault
_NT_NET = {
    "segments": ["lan1", "lan2"],
    "services": {"name": "core-1", "mac": "02:c1:77:00:04:01", "ifaces": [{"seg": "lan1", "ip": "10.1.0.1", "bits": 24, "gw": "10.1.0.2"}],
                 "remote": [{"ip": "198.51.100.10"}]},
    "topology": "pc-7 (LAN 2, DHCP) ── rtr-2 (10.2.0.1 · 10.1.0.2, dnsmasq DHCP) ── core-1 10.1.0.1 ── ERP server 198.51.100.10",
}
_NT_RTR = _prelude("rtr-2") + SYSLOG + r"""sysctl -qw net.ipv4.ip_forward=1 net.ipv4.conf.all.send_redirects=0 net.ipv4.conf.default.send_redirects=0 net.ipv4.conf.eth0.send_redirects=0
ip link set eth0 up; ip addr add 10.1.0.2/24 dev eth0; ip addr add 10.2.0.1/24 dev eth0; ip route add default via 10.1.0.254
cat > /etc/dnsmasq.conf <<'EOF'
# rtr-2: DHCP for LAN 2 (10.2.0.0/24) - change CHG-3317 (edited Friday 17:40)
port=0
interface=eth0
dhcp-authoritative
dhcp-rnage=10.2.0.100,10.2.0.150,12h
dhcp-option=option:router,10.2.0.254
dhcp-option=option:dns-server,10.1.0.1
log-dhcp
EOF
service dnsmasq start >/dev/null 2>&1
"""
_NT_PC = _prelude("pc-7") + "ip link set eth0 up\n"
NETTROUBLE = {
    "id": "linux-vm-nettrouble",
    "title": "Real Linux VMs — Multi-Hop Net Triage",
    "kind": "vm",
    "blurb": "A PC with no address, a Linux router running a real DHCP server and a core router one hop beyond. Three "
             "faults on two machines: find each one from the symptoms, fix it and verify the path hop by hop.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (pc-7 and rtr-2)"},
        {"id": "symptom", "text": "pc-7: try to get a lease (udhcpc) and record the symptom; rtr-2: check the DHCP server config"},
        {"id": "dhcp", "text": "rtr-2: the DHCP server runs with a valid pool 10.2.0.100–10.2.0.150"},
        {"id": "gwopt", "text": "rtr-2: DHCP hands out the right default gateway (this router, 10.2.0.1)"},
        {"id": "lease", "text": "pc-7: holds a lease in the pool with default route via 10.2.0.1"},
        {"id": "isolate", "text": "Isolate before changing the route: from rtr-2 look at the routing table or ping the ERP server"},
        {"id": "route", "text": "rtr-2: default route via the core router 10.1.0.1"},
        {"id": "reach", "text": "pc-7: ping the ERP server 198.51.100.10 (two routers away: TTL 62)"},
        {"id": "trace", "text": "pc-7: traceroute shows rtr-2, core-1 and the server"},
    ],
    "intro": "NET-2207 (P2): after Friday's change nobody on LAN 2 can reach the ERP server 198.51.100.10. Users report "
             "'no network'. You have the PC (pc-7) and the LAN 2 router (rtr-2), which also runs DHCP (dnsmasq). The core "
             "router is 10.1.0.1. Work it like a ticket: symptom, scope, one fix at a time, verify. All real: kernel "
             "routing, a real DHCP server and client; the Packets tab shows every frame.",
    "success_msg": "Fixed and verified hop by hop: DHCP config repaired, correct gateway option, router default route — pc-7 reaches the ERP server.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start both VMs.", "Start VMs."],
        "symptom": ["udhcpc retries and gives up when no server answers. On the router, dnsmasq --test checks the config.",
                    "on pc-7: udhcpc -i eth0 -n -t 3 ; on rtr-2: dnsmasq --test ; service dnsmasq status ; cat /etc/dnsmasq.conf"],
        "dhcp": ["'bad option at line N' — read that line very carefully.", "on rtr-2: sed -i 's/^dhcp-rnage/dhcp-range/' /etc/dnsmasq.conf ; dnsmasq --test ; service dnsmasq restart"],
        "gwopt": ["option:router is what DHCP clients install as their default gateway.",
                  "on rtr-2: sed -i 's/option:router,10.2.0.254/option:router,10.2.0.1/' /etc/dnsmasq.conf ; service dnsmasq restart"],
        "lease": ["Renew on the PC after the server is fixed.", "on pc-7: udhcpc -i eth0 -n ; ip a ; ip route"],
        "isolate": ["Divide the path: if the PC reaches its gateway but not beyond, look at the router.", "on rtr-2: ip route ; ping -c 1 -W 1 198.51.100.10"],
        "route": ["10.1.0.254 does not exist (try ip neigh).", "on rtr-2: ip route replace default via 10.1.0.1"],
        "reach": ["Each router decrements the TTL by one.", "on pc-7: ping -c 3 198.51.100.10"],
        "trace": ["traceroute lists each hop.", "on pc-7: traceroute -n 198.51.100.10"],
    },
    "course_objectives": ["NO-4.1", "NO-6.1", "NO-6.3", "NO-1.1"],
    "minutes": 45,
    "palette": ["udhcpc -i eth0 -n", "ip a", "ip route", "ip neigh", "dnsmasq --test", "cat /etc/dnsmasq.conf", "service dnsmasq ",
                "sed -i ", "ip route replace default via ", "ping -c 3 ", "traceroute -n ", "tail /var/log/messages", "clear"],
    "fallback": ["win-dhcp-renew", "rtr-default-route", "rtr-trace"],
    "vm": dict(IMAGE, machines=[_m("pc", "pc-7", "pc-7", ["lan2"]), _m("rtr", "rtr-2", "rtr-2", ["lan1", "lan2"])],
               setup={"pc": _NT_PC, "rtr": _NT_RTR}, net=_NT_NET),
    "vm_checks": [
        {"id": "boot"},
        {"id": "symptom", "hist": [r"^\[pc\]\s*udhcpc\b", r"^\[rtr\]\s*(dnsmasq\s+--test|cat\s+/etc/dnsmasq\.conf|service\s+dnsmasq\s+(status|start|restart)|grep\b.*dnsmasq)"],
         "why": "Record the symptom on pc-7 (udhcpc), then check the DHCP server on rtr-2 (dnsmasq --test)."},
        {"id": "dhcp", "on": "rtr", "sh": "dnsmasq --test && grep -Eq '^dhcp-range=10\\.2\\.0\\.100,10\\.2\\.0\\.150' /etc/dnsmasq.conf && pidof dnsmasq",
         "show": "dnsmasq --test 2>&1 | tail -1; pidof dnsmasq >/dev/null && echo running || echo not running", "why": "DHCP server on rtr-2: {v}"},
        {"id": "gwopt", "on": "rtr", "sh": "grep -Eq '^dhcp-option=(option:router|3),10\\.2\\.0\\.1$' /etc/dnsmasq.conf",
         "show": "grep -E 'option:router|^dhcp-option=3' /etc/dnsmasq.conf", "why": "Router option: {v}"},
        {"id": "lease", "on": "pc", "sh": "ip -4 addr show eth0 | grep -Eq 'inet 10\\.2\\.0\\.(1[0-4][0-9]|150)/24' && ip route | grep -q '^default via 10\\.2\\.0\\.1 '",
         "show": "ip -4 addr show eth0 | grep inet | awk '{print $2}'; ip route | grep default", "why": "pc-7 has: {v}"},
        {"id": "isolate", "seq": [r"^\[pc\]\s*(ping|traceroute)\b.*198\.51\.100\.10|^\[pc\]\s*ip\s+r(oute)?\s*$", r"^\[rtr\]\s*ip\s+r(oute)?(\s+(show|list))?\s*$|^\[rtr\]\s*(ping|traceroute)\b.*198\.51\.100\.10"],
         "before": r"^\[rtr\]\s*ip\s+r(oute)?\s+(replace|change|add|del)\b.*default",
         "why": "Before changing rtr-2's route: test from pc-7 (ping 198.51.100.10), then look at rtr-2 (ip route)."},
        {"id": "route", "on": "rtr", "sh": "ip route | grep -q '^default via 10\\.1\\.0\\.1 ' && ! ip route | grep -q 10.1.0.254",
         "show": "ip route | grep default", "why": "rtr-2 default route: {v}"},
        {"id": "reach", "on": "pc", "sh": "ping -c 1 -W 2 198.51.100.10 | grep -q 'ttl=62'", "secs": 5, "why": "pc-7 cannot reach 198.51.100.10 yet."},
        {"id": "trace", "hist": [r"^\[pc\]\s*traceroute\b.*198\.51\.100\.10"], "fabric": "trace_core", "why": "Run traceroute 198.51.100.10 on pc-7."},
    ],
    "solution": {"vm_commands": [
        "[pc] udhcpc -i eth0 -n -t 2 -T 1", "[rtr] service dnsmasq status", "[rtr] dnsmasq --test", "[rtr] cat /etc/dnsmasq.conf",
        "[rtr] sed -i 's/^dhcp-rnage/dhcp-range/; s/option:router,10.2.0.254/option:router,10.2.0.1/' /etc/dnsmasq.conf",
        "[rtr] dnsmasq --test", "[rtr] service dnsmasq restart", "[pc] udhcpc -i eth0 -n -t 5", "[pc] ip route",
        "[pc] ping -c 1 -W 1 198.51.100.10", "[rtr] ip route", "[rtr] ip route replace default via 10.1.0.1",
        "[pc] ping -c 2 198.51.100.10", "[pc] traceroute -n -w 1 -q 1 198.51.100.10"]},
}

MORE_LABS = [LOGS, CRON, USERS, PACKAGES, FIREWALL, DISK, SSH, SCRIPT, DNS, NETTROUBLE]
MORE_FABRIC = {
    "dns_fwd": lambda ev: any(e.get("type") == "dns" and e.get("from") == "10.30.0.53" and str(e.get("q") or "").rstrip(".") == "www.example.com"
                              and e.get("rcode") in (0, None) for e in ev),
    "trace_core": lambda ev: any(e.get("type") == "ttl" and e.get("at") == "10.1.0.1" and str(e.get("from") or "").startswith("10.2.0.") for e in ev),
}
MORE_FABRIC_WHY = {"dns_fwd": "the upstream resolver has not received a forwarded query for www.example.com from dns-01",
                   "trace_core": "no traceroute probe from LAN 2 has expired at core-1 yet"}

# the network evidence a correct run produces (engine self-check replays it; the real run is in tools/vm_headless.py)
DNS["solution"]["fabric"] = {"events": [{"type": "dns", "from": "10.30.0.53", "q": "www.example.com", "rcode": 0, "answer": "192.0.2.80"}]}
NETTROUBLE["solution"]["fabric"] = {"events": [{"type": "ttl", "from": "10.2.0.100", "to": "198.51.100.10", "at": "10.1.0.1"}]}
