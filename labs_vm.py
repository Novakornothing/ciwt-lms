"""Real-environment labs: genuine Linux VMs that run entirely in the student's browser (v86, x86 → WebAssembly).

No server cost: the browser downloads the emulator (~2.4 MB) and a Buildroot Linux image (~10 MB) from this LMS once
(self-hosted under static/vendor/v86, fetched by tools/fetch_v86.sh with pinned sha256) and boots it locally.

How a lab is described (all keys are plain data except the python-only `vm_checks`):
  vm.machines   one or more VMs: name, label, hostname, segs (network segments the NIC is plugged into)
  vm.setup      {machine: sh script} sourced once in the fresh VM (hidden) to build the scenario: files, users,
                broken services, stale config. Not re-run when a saved VM is resumed.
  vm.net        optional virtual network (static/js/lab-vmnet.js): an isolating Ethernet switch plus a services host
                (ARP, ping, traceroute end-point, DHCP server, DNS server). The VMs' kernels do the rest for real.
  vm_checks     the grader. Each check is one objective:
                  {"id", "on": machine, "sh": "<shell test run inside the VM, exit 0 = pass>", "show": "<command whose
                   output is quoted in the feedback>", "why": "feedback; {v} = show output", "secs": timeout}
                  {"id", "hist": [regex, ...]}            every regex matched by some command (any order)
                  {"id", "seq": [regex_a, regex_b], "before": regex_c}
                                                          a command matching b AFTER one matching a (both before c)
                  {"id", "fabric": rule}                  evidence seen on the virtual network (DHCP ACK, DNS query)
                  {"id": "boot"}                          every machine reached a shell prompt
                sh / hist / seq / fabric can be combined on one check (all must pass).
"Check my work" fetches a probe per machine (generated from vm_checks), drops it into the VM's 9p share (/mnt), runs
it, reads /mnt/.ciwt-result back and posts it with the attempt nonce. Every command line the student sends is logged
in order to the attempt's event log ("[machine] cmd" when the lab has more than one VM).

Trust note: the VMs run on the student's device, so a determined student could forge the probe output. These labs
are formative practice; for summative use pair them with the event-log review or an instructor sign-off.
Licences: static/vendor/v86/LICENSES.md.  Image notes: docs/VM_IMAGE.md.
"""
import hashlib
import re

VM_ASSETS = {
    "libv86": "vendor/v86/libv86.js",
    "wasm": "vendor/v86/v86.wasm",
    "bios": "vendor/v86/seabios.bin",
    "vga_bios": "vendor/v86/vgabios.bin",
    "bzimage": "vendor/v86/ciwt-linux.bin",
}
# One image for every lab: tools/vm_image/build.sh (kernel 6.8.12 + netfilter/loop/ATA, BusyBox + real Alpine packages).
IMAGE = {"image": "ciwt-linux.bin", "download_mb": 13.2, "prompt_re": r"[#%$] $"}


def _prelude(host, home="/root"):
    return (f"hostname {host}; echo {host} > /etc/hostname\n"
            "export PS1='\\u@\\h:\\w\\$ '\n"
            "alias ll='ls -l'\n"
            f"cd {home}\n")


def _m(name, label, host, segs=None, mem=80, disk_mb=0):
    d = {"name": name, "label": label, "hostname": host, "segs": segs or [], "memory_mb": mem}
    if disk_mb:
        d["disk_mb"] = disk_mb     # a blank ATA disk (/dev/sda), saved with the VM
    return d


# --------------------------------------------------------------------------------------------- lab 1: permissions
PERMS = {
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
             "one-line health-check script. This is a real Linux VM running in your browser — real errors, real BusyBox "
             "tools (try --help). Press Check my work at any time; the grader looks inside the VM.",
    "success_msg": "Every check passed inside the real VM — directory, contents, mode 640, owner tech1, working script, verified.",
    "initial_state": {},
    "hints": ["mkdir -p /root/support/tickets", "echo 'ticket 4512' > /root/support/tickets/notes.txt",
              "chmod 640 /root/support/tickets/notes.txt", "adduser -D tech1", "chown tech1 /root/support/tickets/notes.txt",
              "printf '#!/bin/sh\\necho disk ok\\n' > /root/support/check.sh", "chmod +x /root/support/check.sh",
              "/root/support/check.sh", "ls -l /root/support/tickets"],
    "obj_hints": {
        "boot": ["Press Start VM and wait for the prompt ending in # (5–40 s depending on the device).", "Start VM, then wait for the # prompt."],
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
    "fallback": ["linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "VM", "ciwt-vm")], setup={"vm": _prelude("ciwt-vm")}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "mkdir", "sh": "[ -d /root/support/tickets ]", "why": "/root/support/tickets does not exist yet."},
        {"id": "note", "sh": "grep -q 'ticket 4512' /root/support/tickets/notes.txt",
         "why": "notes.txt is missing or does not contain the line ticket 4512."},
        {"id": "perms", "sh": "ls -l /root/support/tickets/notes.txt | grep -q '^-rw-r----- '",
         "show": "ls -l /root/support/tickets/notes.txt | cut -c1-10",
         "why": "notes.txt mode is {v}; the ticket asks for -rw-r----- (640)."},
        {"id": "owner", "sh": "id tech1 && ls -l /root/support/tickets/notes.txt | awk '{print $3}' | grep -qx tech1",
         "show": "id tech1 >/dev/null 2>&1 && ls -l /root/support/tickets/notes.txt | awk '{print \"owned by \" $3}' || echo user tech1 does not exist yet",
         "why": "notes.txt should be owned by tech1 — now: {v}."},
        {"id": "script", "sh": "[ -x /root/support/check.sh ] && cd /root/support && ./check.sh | grep -q 'disk ok'",
         "show": "[ -x /root/support/check.sh ] && (cd /root/support && ./check.sh 2>&1 | head -2) || echo not executable or missing",
         "why": "check.sh must be executable and print disk ok — it gives: {v}"},
        {"id": "verified", "seq": [r"^chmod\b", r"^(ls\s.*-[a-zA-Z]*l|ll\b)"], "why": "No ls -l after your chmod in your command history yet."},
    ],
    "solution": {"vm_commands": ["mkdir -p /root/support/tickets", "echo 'ticket 4512' > /root/support/tickets/notes.txt",
                                 "chmod 640 /root/support/tickets/notes.txt", "adduser -D tech1",
                                 "chown tech1 /root/support/tickets/notes.txt",
                                 "printf '#!/bin/sh\\necho disk ok\\n' > /root/support/check.sh", "chmod +x /root/support/check.sh",
                                 "/root/support/check.sh", "ls -l /root/support/tickets"]},
}

# --------------------------------------------------------------------------------------------- lab 2: shell (twin of linux-shell)
_SHELL_SETUP = _prelude("ciwt-lnx-01") + r"""mkdir -p /root/support /root/Documents
cat > /root/support/backup.sh <<'EOF'
#!/bin/sh
# nightly backup of ~/support
mkdir -p /tmp/backup && cp /root/support/*.txt /root/support/*.log /tmp/backup/ && date > /tmp/backup/.ran
echo "Backup of ~/support complete: $(ls /tmp/backup | wc -l) files copied to /tmp/backup"
EOF
chmod 644 /root/support/backup.sh
printf 'Quarterly support report - internal only\nOpen tickets: 14\n' > /root/support/report.txt
chmod 644 /root/support/report.txt
printf '09:00 INFO service started\n09:05 INFO user login ok\n09:12 ERROR disk quota exceeded for /srv/share\n09:13 INFO retry scheduled\n09:20 WARN slow response 2300ms\n' > /root/support/app.log
"""
SHELL = {
    "id": "linux-vm-shell",
    "title": "Real Linux VM — shell basics: files, permissions, scripts and logs",
    "kind": "vm",
    "blurb": "The Linux shell lab on a real machine: the same ticket as the simulator, but every command really runs "
             "in a Linux VM inside your browser, and the grader inspects the VM.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM and get a shell prompt"},
        {"id": "identify", "text": "Identify yourself and the machine (whoami, hostname)"},
        {"id": "navigate", "text": "Go to ~/support and list it with permissions (cd, ls -l)"},
        {"id": "mkdir", "text": "Create a logs folder in ~/support"},
        {"id": "notes", "text": "Write a line to ~/support/logs/notes.txt (echo … > file)"},
        {"id": "execute", "text": "Make backup.sh executable for its owner and run it (it really copies files to /tmp/backup)"},
        {"id": "private", "text": "Remove read access for others on report.txt, then verify with ls -l"},
        {"id": "grep", "text": "Find the ERROR line in app.log with grep"},
    ],
    "intro": "SR-4120 on ciwt-lnx-01: the nightly backup script won't run and an internal report is world-readable. "
             "This is a real Linux VM — Windows commands like dir or ipconfig really fail here, so use ls, ip a and "
             "friends. Tab completes, ↑ recalls. Press Check my work at any time.",
    "success_msg": "Fixed on a real Linux box: the backup ran, the report is private, and the error is found.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Press Start VM and wait for root@ciwt-lnx-01:~#.", "Start VM."],
        "identify": ["Two short commands print the user name and the machine name.", "whoami   then   hostname"],
        "navigate": ["~ is your home folder. Change into support, then list with the long format.", "cd ~/support   then   ls -l"],
        "mkdir": ["mkdir makes a directory.", "mkdir ~/support/logs"],
        "notes": ["echo prints text; > redirects it into a file.", "echo \"checked backup\" > ~/support/logs/notes.txt"],
        "execute": ["Look at the x column in ls -l. u+x adds execute for the owner; ./ runs a file in this folder.",
                    "chmod u+x backup.sh   then   ./backup.sh"],
        "private": ["The last triplet in ls -l is 'others'. o-r removes their read bit.", "chmod o-r report.txt   then   ls -l"],
        "grep": ["grep prints the lines of a file that match a word (case matters).", "grep ERROR app.log"],
    },
    "course_objectives": ["IT-9.1", "IT-9.3"],
    "minutes": 25,
    "palette": ["ls -l", "cd ", "pwd", "cat ", "chmod ", "grep ", "mkdir ", "echo ", "./", "whoami", "hostname", "clear"],
    "fallback": ["linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "ciwt-lnx-01", "ciwt-lnx-01")], setup={"vm": _SHELL_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "identify", "hist": [r"^whoami\b|^id\b", r"^hostname\b|^uname\s+-n"], "why": "Run whoami and hostname."},
        {"id": "navigate", "seq": [r"^cd\s+(~/support|/root/support|support)/?$", r"^(ls\s.*-[a-zA-Z]*l|ll\b)"],
         "why": "cd into ~/support, then list it with ls -l."},
        {"id": "mkdir", "sh": "[ -d /root/support/logs ]", "why": "~/support/logs does not exist yet."},
        {"id": "notes", "sh": "[ -s /root/support/logs/notes.txt ]", "why": "~/support/logs/notes.txt is missing or empty."},
        {"id": "execute", "sh": "[ -x /root/support/backup.sh ] && [ -f /tmp/backup/.ran ]",
         "show": "ls -l /root/support/backup.sh | cut -c1-10; [ -f /tmp/backup/.ran ] && echo ran || echo 'has not run yet'",
         "why": "backup.sh needs the owner x bit and must have run ({v})."},
        {"id": "private", "sh": "ls -l /root/support/report.txt | grep -q '^-r..r.-'", "seq": [r"^chmod\b.*report", r"^(ls\s.*-[a-zA-Z]*l|ll\b)"],
         "show": "ls -l /root/support/report.txt | cut -c1-10",
         "why": "report.txt is {v} — others must have no r (and owner keeps read), then list it with ls -l."},
        {"id": "grep", "hist": [r"^grep\b.*ERROR.*app\.log|^grep\b.*app\.log.*ERROR|cat\b.*app\.log.*\|\s*grep.*ERROR"],
         "why": "Search app.log for ERROR with grep."},
    ],
    "solution": {"vm_commands": ["whoami", "hostname", "cd ~/support", "ls -l", "mkdir logs",
                                 "echo \"checked backup\" > logs/notes.txt", "chmod u+x backup.sh", "./backup.sh",
                                 "chmod o-r report.txt", "ls -l", "grep ERROR app.log"]},
}

# --------------------------------------------------------------------------------------------- lab 3: services, processes, disk, cron, syslog
_SVC_SETUP = _prelude("ciwt-app-02") + r"""mkdir -p /usr/local/bin /root/bin /tmp/spool /var/spool/cron/crontabs /var/run
cat > /usr/local/bin/heartbeat <<'EOF'
#!/bin/sh
# writes a line to /var/log/heartbeat.log every 2 seconds
while true; do echo "$(date '+%H:%M:%S') heartbeat ok" >> /var/log/heartbeat.log; sleep 2; done
EOF
chmod 755 /usr/local/bin/heartbeat
cat > /etc/init.d/S50heartbeat <<'EOF'
#!/bin/sh
# heartbeat service for the app monitor (start | stop | restart | status)
DAEMON=/usr/local/sbin/heartbeat
PIDFILE=/var/run/heartbeat.pid
case "$1" in
  start)   printf 'Starting heartbeat: '
           start-stop-daemon -S -b -m -p $PIDFILE -x $DAEMON && echo OK || { echo FAIL; exit 1; } ;;
  stop)    printf 'Stopping heartbeat: '
           start-stop-daemon -K -p $PIDFILE && rm -f $PIDFILE && echo OK || { echo FAIL; exit 1; } ;;
  restart) "$0" stop; "$0" start ;;
  status)  if [ -f $PIDFILE ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then echo "heartbeat is running (pid $(cat $PIDFILE))"
           else echo "heartbeat is stopped"; exit 3; fi ;;
  *)       echo "Usage: $0 {start|stop|restart|status}"; exit 1 ;;
esac
EOF
chmod 644 /etc/init.d/S50heartbeat
cat > /usr/local/bin/debugdump <<'EOF'
#!/bin/sh
# left running by a vendor after a support call: dumps debug data into /tmp forever
while :; do head -c 3000 /dev/urandom | base64 >> /tmp/spool/debug.log 2>/dev/null; sleep 1; done
EOF
chmod 755 /usr/local/bin/debugdump
head -c 7000000 /dev/zero | tr '\0' '#' > /tmp/spool/debug.log
cat > /root/bin/cleanup.sh <<'EOF'
#!/bin/sh
find /tmp -name '*.tmp' -mmin +60 -delete 2>/dev/null; echo "cleanup $(date)" >> /var/log/cleanup.log
EOF
chmod 755 /root/bin/cleanup.sh
pidof syslogd >/dev/null || /etc/init.d/S01syslogd start >/dev/null 2>&1
crond -c /var/spool/cron/crontabs 2>/dev/null
( setsid /usr/local/bin/debugdump </dev/null >/dev/null 2>&1 & )
"""
SERVICES = {
    "id": "linux-vm-services",
    "title": "Real Linux VM — services, processes, a filling disk, cron and syslog",
    "kind": "vm",
    "blurb": "A real Linux server with real faults: a runaway process filling /tmp and a broken init script. "
             "Find, kill, clean up, repair the service, schedule a job and log the fix — graded inside the VM.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM and get a shell prompt"},
        {"id": "find", "text": "Find what is filling /tmp (df -h, du) and which process is doing it (ps, fuser or top)"},
        {"id": "kill", "text": "Stop the runaway debugdump process (kill)"},
        {"id": "space", "text": "Free the space: remove or empty /tmp/spool/debug.log"},
        {"id": "fix", "text": "Repair /etc/init.d/S50heartbeat: make it executable and correct its DAEMON path"},
        {"id": "running", "text": "Start the heartbeat service and confirm it with status (it writes /var/log/heartbeat.log)"},
        {"id": "cron", "text": "Schedule /root/bin/cleanup.sh to run every 15 minutes in root's crontab"},
        {"id": "log", "text": "Record the fix in syslog with logger (message containing SR-4201) and find it in /var/log/messages"},
    ],
    "intro": "SR-4201 on ciwt-app-02: the monitoring dashboard says the heartbeat service is down and /tmp is filling up. "
             "A real Linux VM is running in your browser with both faults really happening. Investigate before you change "
             "anything — your command history is part of the grade.",
    "success_msg": "Server healthy: runaway process gone, space freed, heartbeat running from a repaired init script, "
                   "cleanup scheduled and the fix logged.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Press Start VM and wait for root@ciwt-app-02:~#.", "Start VM."],
        "find": ["df -h shows which filesystem is full; du -sh /tmp/* shows what is big; ps lists processes.",
                 "df -h ; du -sh /tmp/* ; ps | grep debug   (or fuser /tmp/spool/debug.log)"],
        "kill": ["ps shows the PID in the first column. kill PID asks it to stop; killall matches by name.",
                 "killall debugdump   or   ps | grep debugdump  then  kill <PID>"],
        "space": ["Kill the writer first, or it recreates the file. Then remove it (or empty it with > file).",
                  "rm /tmp/spool/debug.log ; df -h /tmp"],
        "fix": ["Two faults: ls -l shows the x bit is missing, and cat shows DAEMON points at a file that does not exist "
                "(where is heartbeat really? which heartbeat).",
                "chmod +x /etc/init.d/S50heartbeat ; sed -i 's#/usr/local/sbin/heartbeat#/usr/local/bin/heartbeat#' /etc/init.d/S50heartbeat"],
        "running": ["Init scripts take start / stop / status.", "/etc/init.d/S50heartbeat start ; /etc/init.d/S50heartbeat status ; tail /var/log/heartbeat.log"],
        "cron": ["crontab -l lists root's jobs; crontab - installs a new table from standard input. Every 15 min is */15 in the minute field.",
                 "echo '*/15 * * * * /root/bin/cleanup.sh' | crontab - ; crontab -l"],
        "log": ["logger writes to syslog; syslogd stores it in /var/log/messages.",
                "logger -t helpdesk 'SR-4201 heartbeat restored' ; grep SR-4201 /var/log/messages"],
    },
    "course_objectives": ["IT-9.1", "NO-5.1"],
    "minutes": 35,
    "palette": ["df -h", "du -sh /tmp/*", "ps", "kill ", "killall ", "ls -l ", "cat ", "sed -i ", "chmod +x ",
                "/etc/init.d/S50heartbeat ", "crontab -l", "logger ", "tail ", "clear"],
    "fallback": ["linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "ciwt-app-02", "ciwt-app-02")], setup={"vm": _SVC_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "find", "hist": [r"^(df|du)\b", r"^(ps|top|fuser|lsof|pgrep|pidof)\b|\|\s*grep\b.*debug"],
         "why": "Investigate first: df/du for the space, then ps (or fuser/top) for the process."},
        {"id": "kill", "sh": "! ps | grep -v '\\[[d]ebugdump\\]' | grep -q '[d]ebugdump'", "show": "ps | grep '[d]ebugdump' | head -1",
         "why": "debugdump is still running: {v}"},
        {"id": "space", "sh": "[ ! -f /tmp/spool/debug.log ] || [ $(wc -c < /tmp/spool/debug.log) -lt 200000 ]",
         "show": "df -h /tmp | tail -1",
         "why": "/tmp/spool/debug.log is still large (df: {v})."},
        {"id": "fix", "sh": "[ -x /etc/init.d/S50heartbeat ] && grep -q '^DAEMON=/usr/local/bin/heartbeat' /etc/init.d/S50heartbeat",
         "show": "ls -l /etc/init.d/S50heartbeat | cut -c1-10; grep '^DAEMON=' /etc/init.d/S50heartbeat",
         "why": "The init script still needs work: {v}"},
        {"id": "running", "sh": "/etc/init.d/S50heartbeat status && [ -s /var/log/heartbeat.log ]",
         "seq": [r"S50heartbeat\s+(start|restart)", r"S50heartbeat\s+status|tail\b.*heartbeat|^ps\b"],
         "show": "/etc/init.d/S50heartbeat status 2>&1",
         "why": "Start the service, then confirm with status: {v}"},
        {"id": "cron", "sh": "crontab -l 2>/dev/null | grep -Eq '^\\*/15[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+\\*[[:space:]]+/root/bin/cleanup\\.sh'",
         "show": "crontab -l 2>&1 | grep -v '^#' | head -2",
         "why": "root's crontab needs */15 * * * * /root/bin/cleanup.sh — now: {v}"},
        {"id": "log", "sh": "grep -q 'SR-4201' /var/log/messages", "hist": [r"^logger\b", r"grep\b.*SR-4201|tail\b.*messages|cat\b.*messages"],
         "why": "Log a line containing SR-4201 with logger, then find it in /var/log/messages."},
    ],
    "solution": {"vm_commands": ["df -h", "du -sh /tmp/*", "ps | grep debug", "killall debugdump", "rm /tmp/spool/debug.log",
                                 "chmod +x /etc/init.d/S50heartbeat",
                                 "sed -i 's#/usr/local/sbin/heartbeat#/usr/local/bin/heartbeat#' /etc/init.d/S50heartbeat",
                                 "/etc/init.d/S50heartbeat start", "/etc/init.d/S50heartbeat status",
                                 "echo '*/15 * * * * /root/bin/cleanup.sh' | crontab -", "crontab -l",
                                 "logger -t helpdesk 'SR-4201 heartbeat restored'", "grep SR-4201 /var/log/messages"]},
}

# --------------------------------------------------------------------------------------------- lab 4: real DHCP / DNS client troubleshooting
_NC_NET = {
    "segments": ["lan"],
    "services": {"name": "LAN services", "mac": "02:c1:77:00:00:01",
                 "ifaces": [{"seg": "lan", "ip": "10.10.0.1", "bits": 24}, {"seg": "lan", "ip": "10.10.0.53", "bits": 24},
                            {"seg": "lan", "ip": "10.10.0.80", "bits": 24}],
                 "dhcp": {"seg": "lan", "pool": ["10.10.0.100", "10.10.0.150"], "router": "10.10.0.1", "dns": "10.10.0.53",
                          "domain": "ciwt.lab", "bits": 24, "lease_s": 3600},
                 "dns": {"domain": "ciwt.lab", "records": {"intranet.ciwt.lab": "10.10.0.80", "gw.ciwt.lab": "10.10.0.1",
                                                           "dns1.ciwt.lab": "10.10.0.53"}}},
    "topology": "ws-14 (this VM, eth0) ── LAN switch ── gateway 10.10.0.1 · DHCP + DNS server 10.10.0.53 · intranet web 10.10.0.80",
}
_NC_SETUP = _prelude("ws-14") + r"""ip link set eth0 up; ip addr flush dev eth0; ip addr add 169.254.23.7/16 dev eth0
echo '10.10.0.99   intranet.ciwt.lab intranet   # old server, decommissioned 2025' >> /etc/hosts
"""
NETCLIENT = {
    "id": "linux-vm-netclient",
    "title": "Real Linux VM — lease, gateway and name resolution on a live network",
    "kind": "vm",
    "blurb": "A real Linux workstation on a virtual LAN with a real DHCP and DNS server. Diagnose an APIPA address "
             "and a stale hosts entry with ip, udhcpc, nslookup and ping — every packet really flows.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM and get a shell prompt"},
        {"id": "diagnose", "text": "Read the interface configuration (ip a) and spot the 169.254 (APIPA) address before changing anything"},
        {"id": "lease", "text": "Get a DHCP lease on eth0 (udhcpc -i eth0) — the DHCP server must see Discover/Request and send an ACK"},
        {"id": "route", "text": "Confirm the default gateway 10.10.0.1 (ip route) and that it answers ping"},
        {"id": "dns", "text": "Confirm the DNS server from the lease (/etc/resolv.conf) and resolve intranet.ciwt.lab with nslookup"},
        {"id": "hosts", "text": "Find and remove the stale /etc/hosts entry that overrides DNS for intranet.ciwt.lab"},
        {"id": "reach", "text": "ping intranet.ciwt.lab by name successfully (it must reach 10.10.0.80)"},
        {"id": "neigh", "text": "Show the neighbour (ARP) table and see the gateway's MAC address (ip neigh or arp -n)"},
    ],
    "intro": "SR-4307 from ws-14: \"intranet doesn't load, and I think the network is broken\". The workstation is a real "
             "Linux VM plugged into a virtual LAN; the DHCP and DNS servers are real protocol servers running in this "
             "page. Work the order: link → lease → IP/gateway → name → service. The Packets tab shows the traffic.",
    "success_msg": "Lease, gateway, DNS and the stale hosts entry all fixed — and you watched the real DHCP and DNS packets do it.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Press Start VM and wait for root@ws-14:~#.", "Start VM."],
        "diagnose": ["ip a (short for ip addr) lists every interface and its addresses. 169.254.x.x means DHCP never answered.",
                     "ip a"],
        "lease": ["BusyBox's DHCP client is udhcpc. Tell it which interface to configure. Watch the Packets tab: DISCOVER, OFFER, REQUEST, ACK.",
                  "udhcpc -i eth0"],
        "route": ["ip route shows the routing table; the default line is the gateway. Ping it to prove layer 3 works locally.",
                  "ip route ; ping -c 3 10.10.0.1"],
        "dns": ["The DHCP client wrote the DNS server into /etc/resolv.conf. nslookup asks it directly (it skips /etc/hosts).",
                "cat /etc/resolv.conf ; nslookup intranet.ciwt.lab"],
        "hosts": ["nslookup says 10.10.0.80, but ping goes to 10.10.0.99 — something answers before DNS. /etc/hosts is checked first.",
                  "cat /etc/hosts ; sed -i '/10.10.0.99/d' /etc/hosts"],
        "reach": ["After fixing hosts, ping by name and check the address it chose.", "ping -c 3 intranet.ciwt.lab"],
        "neigh": ["The kernel keeps IP → MAC mappings it has learned.", "ip neigh   (or arp -n)"],
    },
    "course_objectives": ["IT-5.1", "IT-5.3", "IT-13.2", "NO-4.1", "NO-4.2"],
    "minutes": 30,
    "palette": ["ip a", "ip route", "udhcpc -i eth0", "cat /etc/resolv.conf", "nslookup ", "cat /etc/hosts", "sed -i ",
                "ping -c 3 ", "ip neigh", "traceroute -n ", "clear"],
    "fallback": ["win-dhcp-renew", "win-dns-break"],
    "vm": dict(IMAGE, machines=[_m("vm", "ws-14", "ws-14", ["lan"])], setup={"vm": _NC_SETUP}, net=_NC_NET),
    "vm_checks": [
        {"id": "boot"},
        {"id": "diagnose", "seq": [r"^(ip\s+(-[a-z0-9]+\s+)*(a|addr|address)\b|ifconfig\b)", r"^udhcpc\b"],
         "why": "Read the configuration with ip a before requesting a lease."},
        {"id": "lease", "sh": "ip -4 addr show eth0 | grep -Eq 'inet 10\\.10\\.0\\.(1[0-4][0-9]|150)/24'",
         "fabric": "dhcp_ack", "show": "ip -4 addr show eth0 | grep inet | awk '{print $2}' | tr '\\n' ' '",
         "why": "eth0 has {v}— it needs a lease from the DHCP server (10.10.0.100–150)."},
        {"id": "route", "sh": "ip route | grep -q '^default via 10.10.0.1'", "hist": [r"^ip\s+(-[a-z0-9]+\s+)*r(oute)?\b|^route\b|^netstat\s+-r"],
         "fabric": "ping_gw", "show": "ip route | grep default || echo no default route",
         "why": "Check ip route (default via 10.10.0.1) and ping the gateway — now: {v}"},
        {"id": "dns", "sh": "grep -q '^nameserver 10.10.0.53' /etc/resolv.conf", "hist": [r"resolv\.conf"],
         "fabric": "dns_intranet", "show": "grep nameserver /etc/resolv.conf || echo no nameserver",
         "why": "Look at /etc/resolv.conf and resolve intranet.ciwt.lab with nslookup (the DNS server must see the query) — {v}"},
        {"id": "hosts", "sh": "! grep -Eq '^[[:space:]]*10\\.10\\.0\\.99[[:space:]]' /etc/hosts",
         "show": "grep -n intranet /etc/hosts | head -2", "why": "/etc/hosts still overrides DNS: {v}"},
        {"id": "reach", "sh": "ping -c 1 -W 2 intranet.ciwt.lab | grep -q '10\\.10\\.0\\.80'", "secs": 5,
         "hist": [r"^ping\b.*intranet"], "why": "ping intranet.ciwt.lab must reach 10.10.0.80."},
        {"id": "neigh", "hist": [r"^ip\s+(-[a-z0-9]+\s+)*n(eigh(bour)?)?\b|^arp\b"], "why": "Show the neighbour table (ip neigh)."},
    ],
    "solution": {"vm_commands": ["ip a", "udhcpc -i eth0", "ip route", "ping -c 2 10.10.0.1", "cat /etc/resolv.conf",
                                 "nslookup intranet.ciwt.lab", "ping -c 1 intranet.ciwt.lab", "cat /etc/hosts",
                                 "sed -i '/10.10.0.99/d' /etc/hosts", "ping -c 2 intranet.ciwt.lab", "ip neigh"],
                 "fabric": {"events": [{"type": "dhcp", "msg": "ACK", "ip": "10.10.0.100"},
                                       {"type": "ping", "from": "10.10.0.100", "to": "10.10.0.1"},
                                       {"type": "dns", "q": "intranet.ciwt.lab", "rcode": 0}]}},
}

# --------------------------------------------------------------------------------------------- lab 5: real routing between two networks
_RT_NET = {
    "segments": ["lan1", "lan2"],
    "services": {"name": "fileserver", "mac": "02:c1:77:00:02:0a",
                 "ifaces": [{"seg": "lan2", "ip": "10.2.0.10", "bits": 24, "gw": "10.2.0.1"}]},
    "topology": "pc-a (eth0, LAN 1 10.1.0.0/24) ── rtr-1 (eth0 on both LANs: 10.1.0.1 and 10.2.0.1) ── fileserver 10.2.0.10 (LAN 2 10.2.0.0/24)",
}
ROUTING = {
    "id": "linux-vm-routing",
    "title": "Real Linux VMs — route between two networks (two machines, one router)",
    "kind": "vm",
    "blurb": "Two real Linux VMs on a virtual network: address a PC and a Linux router, turn on IP forwarding and set "
             "the default gateway until the PC reaches a server on the other subnet. Real ARP, TTLs and traceroute.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (pc-a and rtr-1)"},
        {"id": "pc_ip", "text": "pc-a: give eth0 the address 10.1.0.10/24"},
        {"id": "rtr_ip", "text": "rtr-1: give eth0 both gateway addresses, 10.1.0.1/24 (LAN 1) and 10.2.0.1/24 (LAN 2)"},
        {"id": "gw", "text": "pc-a: add the default route via 10.1.0.1"},
        {"id": "isolate", "text": "Before enabling forwarding, prove where it fails: ping 10.2.0.10 from pc-a (fails), then from rtr-1 (works)"},
        {"id": "forward", "text": "rtr-1: enable IPv4 forwarding (net.ipv4.ip_forward=1)"},
        {"id": "reach", "text": "pc-a: ping the fileserver 10.2.0.10 successfully (through the router)"},
        {"id": "trace", "text": "pc-a: traceroute to 10.2.0.10 and see the router as hop 1"},
    ],
    "intro": "NET-118: the new lab subnet (LAN 2, 10.2.0.0/24, with the fileserver at 10.2.0.10) must be reachable from "
             "LAN 1. You have two real Linux VMs — pc-a on LAN 1 and rtr-1, a Linux router plugged into both LANs — and "
             "an isolating switch between them. Use the tabs to switch machines; the Packets tab shows real frames, TTLs "
             "and ARP. Nothing is configured yet.",
    "success_msg": "Routed for real: pc-a reaches 10.2.0.10 through rtr-1 (TTL 63, router as hop 1).",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VMs; both consoles reach a # prompt.", "Start VMs."],
        "pc_ip": ["ip addr add ADDRESS/PREFIX dev INTERFACE.", "on pc-a: ip addr add 10.1.0.10/24 dev eth0"],
        "rtr_ip": ["A Linux interface can hold several addresses. The router needs one in each subnet.",
                   "on rtr-1: ip addr add 10.1.0.1/24 dev eth0 ; ip addr add 10.2.0.1/24 dev eth0"],
        "gw": ["Traffic for other subnets goes to the default gateway.", "on pc-a: ip route add default via 10.1.0.1"],
        "isolate": ["Divide and conquer: if the router reaches the server but the PC cannot, look at the router's forwarding (or the PC's gateway).",
                    "on pc-a: ping -c 1 -W 1 10.2.0.10 (fails) ; on rtr-1: ping -c 1 10.2.0.10 (works) — before sysctl"],
        "forward": ["Linux hosts drop packets that are not for them unless forwarding is on.", "on rtr-1: sysctl -w net.ipv4.ip_forward=1"],
        "reach": ["Ping from pc-a. Watch the Packets tab: the request crosses the router with TTL 63.", "on pc-a: ping -c 3 10.2.0.10"],
        "trace": ["traceroute lists each router on the path.", "on pc-a: traceroute -n 10.2.0.10"],
    },
    "course_objectives": ["NO-9.2", "IT-5.1", "IT-5.3"],
    "minutes": 35,
    "palette": ["ip a", "ip addr add ", "ip route", "ip route add default via ", "sysctl -w net.ipv4.ip_forward=1",
                "ping -c 3 ", "traceroute -n ", "ip neigh", "clear"],
    "fallback": ["rtr-two-interfaces", "rtr-default-route"],
    "vm": dict(IMAGE, machines=[_m("pc", "pc-a", "pc-a", ["lan1"]), _m("rtr", "rtr-1", "rtr-1", ["lan1", "lan2"])],
               setup={"pc": _prelude("pc-a") + "ip link set eth0 up\n",
                      "rtr": _prelude("rtr-1") + "sysctl -qw net.ipv4.ip_forward=0 net.ipv4.conf.all.send_redirects=0 "
                                                 "net.ipv4.conf.default.send_redirects=0 net.ipv4.conf.eth0.send_redirects=0\nip link set eth0 up\n"},
               net=_RT_NET),
    "vm_checks": [
        {"id": "boot"},
        {"id": "pc_ip", "on": "pc", "sh": "ip -4 addr show eth0 | grep -q 'inet 10\\.1\\.0\\.10/24'",
         "show": "ip -4 addr show eth0 | grep inet | awk '{print $2}' | tr '\\n' ' '", "why": "pc-a eth0 has: {v}(needs 10.1.0.10/24)."},
        {"id": "rtr_ip", "on": "rtr", "sh": "ip -4 addr show eth0 | grep -q 'inet 10\\.1\\.0\\.1/24' && ip -4 addr show eth0 | grep -q 'inet 10\\.2\\.0\\.1/24'",
         "show": "ip -4 addr show eth0 | grep inet | awk '{print $2}' | tr '\\n' ' '", "why": "rtr-1 eth0 has: {v}(needs 10.1.0.1/24 and 10.2.0.1/24)."},
        {"id": "gw", "on": "pc", "sh": "ip route | grep -q '^default via 10\\.1\\.0\\.1'", "show": "ip route | grep default || echo none",
         "why": "pc-a default route: {v}."},
        {"id": "isolate", "seq": [r"^\[pc\]\s*ping\b.*10\.2\.0\.10", r"^\[rtr\]\s*ping\b.*10\.2\.0\.10"],
         "before": r"^\[rtr\]\s*(sysctl\b.*ip_forward\s*=\s*1|echo\s+1\s*>\s*/proc/sys/net/ipv4/ip_forward)",
         "why": "Before turning on forwarding, ping 10.2.0.10 from pc-a (fails) and then from rtr-1 (works)."},
        {"id": "forward", "on": "rtr", "sh": "[ \"$(cat /proc/sys/net/ipv4/ip_forward)\" = 1 ]", "show": "cat /proc/sys/net/ipv4/ip_forward",
         "why": "rtr-1 net.ipv4.ip_forward is {v}."},
        {"id": "reach", "on": "pc", "sh": "ping -c 1 -W 2 10.2.0.10 | grep -q 'ttl=63'", "secs": 5,
         "why": "pc-a cannot reach 10.2.0.10 through the router yet."},
        {"id": "trace", "hist": [r"^\[pc\]\s*traceroute\b.*10\.2\.0\.10"], "why": "Run traceroute 10.2.0.10 on pc-a."},
    ],
    "solution": {"vm_commands": ["[pc] ip addr add 10.1.0.10/24 dev eth0",
                                 "[rtr] ip addr add 10.1.0.1/24 dev eth0", "[rtr] ip addr add 10.2.0.1/24 dev eth0",
                                 "[pc] ip route add default via 10.1.0.1", "[pc] ping -c 1 -W 1 10.2.0.10",
                                 "[rtr] ping -c 1 10.2.0.10", "[rtr] sysctl -w net.ipv4.ip_forward=1",
                                 "[pc] ping -c 2 10.2.0.10", "[pc] traceroute -n -w 1 -q 1 10.2.0.10"]},
}

VM_LABS = [PERMS, SHELL, SERVICES, NETCLIENT, ROUTING]
from labs_vm_more import MORE_LABS, MORE_FABRIC, MORE_FABRIC_WHY  # noqa: E402  (round 2: ten more real labs)
VM_LABS += MORE_LABS
VM_BY_ID = {l["id"]: l for l in VM_LABS}
VM_LINUX = PERMS  # backwards name


# --------------------------------------------------------------------------------------------- engine
def nonce(seed):
    return hashlib.sha1(f"vm:{seed}".encode()).hexdigest()[:12]


def machines(lab):
    return [m["name"] for m in lab["vm"]["machines"]]


def fresh(lab, seed):
    return {"nonce": nonce(seed), "vm_cmds": [], "checks": 0, "probe_last": None}


def _shq(s):
    return "'" + str(s).replace("'", "'\\''") + "'"


_HELPERS = r"""_c(){ ( eval "$2" ) </dev/null >/dev/null 2>&1 & W=$!; i=0; L=$(( ${3:-3} * 10 ))
while kill -0 $W 2>/dev/null && [ $i -lt $L ]; do usleep 100000; i=$((i+1)); done
if kill -0 $W 2>/dev/null; then kill $W 2>/dev/null; echo "c_$1 0"; elif wait $W; then echo "c_$1 1"; else echo "c_$1 0"; fi; }
_v(){ echo "v_$1 $( ( eval "$2" ) </dev/null 2>&1 | head -c 200 | tr '\n\t' '  ')"; }
"""


def probe_script(state, lab=None, machine=None):
    """The probe for one machine: POSIX sh, BusyBox-only, runs each shell check with a watchdog."""
    lab = lab or PERMS
    names = machines(lab)
    machine = machine or names[0]
    lines = ["{", f"echo \"nonce {state.get('nonce') or ''}\"", f"echo \"m {machine}\""]
    for c in lab["vm_checks"]:
        if not c.get("sh") or (c.get("on") or names[0]) != machine:
            continue
        lines.append(f"_c {c['id']} {_shq(c['sh'])} {int(c.get('secs') or 3)}")
        if c.get("show"):
            lines.append(f"_v {c['id']} {_shq(c['show'])}")
    lines += ["echo end", "} > /mnt/.ciwt-result 2>&1"]
    return _HELPERS + "\n".join(lines) + "\n"


def probe_scripts(state, lab):
    return {m: probe_script(state, lab, m) for m in machines(lab)}


def parse_probe(text):
    out = {}
    for ln in (text or "").splitlines():
        k, _, v = ln.strip().partition(" ")
        if k:
            out[k] = v.strip()
    return out


def record_commands(state, lines):
    """Append the student's VM command lines (already in order; "[machine] cmd" for multi-VM labs)."""
    cmds = state.setdefault("vm_cmds", [])
    for ln in lines or []:
        ln = str(ln).replace("\r", "")[:500]
        if ln.strip():
            cmds.append(ln)
    del cmds[:-600]


_SPLIT = re.compile(r"\s*(?:;|&&|\|\||\n)\s*")
_TAG = re.compile(r"^\[(\w[\w-]*)\]\s*")


def _parts(cmds, first):
    """Each command line split at ; && || into simple commands, tagged with its machine."""
    out = []
    for c in cmds:
        m = _TAG.match(c)
        mach, body = (m.group(1), c[m.end():]) if m else (first, c)
        for p in _SPLIT.split(body.strip()):
            p = re.sub(r"^sudo\s+", "", p.strip())
            if p:
                out.append((mach, p))
    return out


def _match(rx, mach, cmd):
    if rx.startswith("^\\["):
        return re.search(rx, f"[{mach}] {cmd}") is not None
    return re.search(rx, cmd) is not None


def _hist_ok(check, parts):
    for rx in check.get("hist") or []:
        if not any(_match(rx, m, c) for m, c in parts):
            return False
    seq = check.get("seq")
    if seq:
        before = check.get("before")
        stop = next((i for i, (m, c) in enumerate(parts) if before and _match(before, m, c)), len(parts))
        ia = next((i for i, (m, c) in enumerate(parts) if _match(seq[0], m, c)), None)
        if ia is None or ia >= stop:
            return False
        if not any(_match(seq[1], m, c) for m, c in parts[ia + 1:stop]):
            return False
    return True


def _events(fabric):
    ev = (fabric or {}).get("events") if isinstance(fabric, dict) else None
    return [e for e in (ev or []) if isinstance(e, dict)][:300]


FABRIC_RULES = {
    "dhcp_ack": lambda ev: any(e.get("type") == "dhcp" and e.get("msg") == "ACK" for e in ev),
    "ping_gw": lambda ev: any(e.get("type") == "ping" and e.get("to") == "10.10.0.1" for e in ev),
    "dns_intranet": lambda ev: any(e.get("type") == "dns" and str(e.get("q") or "").rstrip(".") in ("intranet.ciwt.lab", "intranet")
                                   and e.get("rcode") in (0, None) for e in ev),
}
FABRIC_WHY = {"dhcp_ack": "the DHCP server has not acknowledged a lease yet",
              "ping_gw": "the gateway has not seen a ping from you yet",
              "dns_intranet": "the DNS server has not been asked for intranet.ciwt.lab yet"}


FABRIC_RULES.update(MORE_FABRIC)
FABRIC_WHY.update(MORE_FABRIC_WHY)


def _fabric_ok(rule, ev, state):
    seen = (state.setdefault("fabric_seen", []))
    if rule in seen:
        return True
    if FABRIC_RULES[rule](ev):
        seen.append(rule)
        return True
    return False


def grade(lab, state, done, probes, booted=True, fabric=None):
    """Objectives from the real VM probe(s), the real command history and the virtual network's evidence.
    probes: {machine: probe text} (a plain string means the first machine). Returns (result, state, done)."""
    lab = lab or PERMS
    names = machines(lab)
    if isinstance(probes, str):
        probes = {names[0]: probes} if probes else {}
    probes = {k: v for k, v in (probes or {}).items() if k in names and isinstance(v, str)}
    state["checks"] = (state.get("checks") or 0) + 1
    res = {"checks": {}, "messages": []}
    parsed = {}
    for m, text in probes.items():
        p = parse_probe(text)
        if p.get("nonce") != state.get("nonce") or p.get("m", m) != m:
            res["error"] = "The check result did not come from this attempt's VM (nonce mismatch). Press Check my work again."
            return res, state, done
        parsed[m] = p
    vals = {}
    for m, p in parsed.items():
        vals.update({k: v for k, v in p.items() if k.startswith(("c_", "v_"))})
    state["probe_last"] = {k: vals[k] for k in sorted(vals)}
    ev = _events(fabric)
    parts = _parts(state.get("vm_cmds") or [], names[0])
    for c in lab["vm_checks"]:
        oid = c["id"]
        fab_missing = False
        if oid == "boot":
            ok = bool(booted and (probes or state.get("vm_cmds")))
        else:
            ok = True
            if c.get("sh"):
                ok = (c.get("on") or names[0]) in parsed and vals.get("c_" + oid) == "1"
            if ok and (c.get("hist") or c.get("seq")):
                ok = _hist_ok(c, parts)
            if ok and c.get("fabric"):
                ok = _fabric_ok(c["fabric"], ev, state)
                fab_missing = not ok
        res["checks"][oid] = ok
        if ok and oid not in done:
            done.append(oid)
        elif not ok and oid != "boot" and oid not in done:
            v = re.sub(r"^/mnt/\.ciwt-probe: (eval: )?(line \d+: )?", "", vals.get("v_" + oid, "").strip())
            msg = (c.get("why") or "").replace("{v}", v or "?")
            if fab_missing:
                msg += f" ({FABRIC_WHY[c['fabric']]})"
            res["messages"].append(msg)
    return res, state, done


def solved_probe(state, lab=None, machine=None):
    """A passing probe for tests and solve(): every shell check returns 1."""
    lab = lab or PERMS
    names = machines(lab)
    machine = machine or names[0]
    out = [f"nonce {state.get('nonce')}", f"m {machine}"]
    for c in lab["vm_checks"]:
        if c.get("sh") and (c.get("on") or names[0]) == machine:
            out.append(f"c_{c['id']} 1")
    return "\n".join(out + ["end"]) + "\n"


def solved_probes(state, lab):
    return {m: solved_probe(state, lab, m) for m in machines(lab)}
