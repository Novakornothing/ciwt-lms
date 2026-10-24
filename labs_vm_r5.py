"""Round-5 real Linux VM lab: the troubleshooting methodology on a real server (ITSUP chapter 7, which had only the
simulated ticket-method activity). The machine really is broken; the grade is mostly about *how* the student works:
identify (ticket, change log, service status, syslog) → fault domain → a written theory → test it → back up → fix →
verify full functionality (including reboot persistence) → document. Same format and grader as labs_vm.py; tagged
*Pending SME review* by interactive_labs._install_new_labs."""
from labs_vm import IMAGE, _m, _prelude
from labs_vm_more import SYSLOG
from labs_vm_r4 import _ans

_ASK = "/root/SR-7301.txt"
# a command that changes the timeclock settings (copying it *to* a backup does not count)
_EDIT = (r"\bsed\b.*\s-i\S*\s.*/etc/default/timeclock(\s|;|$)|^\s*(vi|ed|nano)\s+/etc/default/timeclock(\s|;|$)"
         r"|(>|>>)\s*/etc/default/timeclock(\s|;|$)|^\s*(cp|mv)\b.*\s/etc/default/timeclock\s*(;|$)")
_SETUP = _prelude("clock-01") + SYSLOG + r"""apk add -q --no-progress darkhttpd >/dev/null 2>&1
mkdir -p /srv/timeclock /etc/default /var/backups
cat > /srv/timeclock/index.html <<'EOF'
<h1>Front desk time clock</h1><form><label>Badge <input name=badge></label> <button>Clock in</button> <button>Clock out</button></form>
EOF
chmod 644 /srv/timeclock/index.html
cat > /var/backups/timeclock.2026-10-16 <<'EOF'
# time clock web service settings (read by /etc/init.d/timeclock)
PORT=8080
DOCROOT=/srv/timeclock
EOF
cat > /etc/default/timeclock <<'EOF'
# time clock web service settings (read by /etc/init.d/timeclock)
# CHG-7290 tidy-up 17 Oct: renamed folders to the new naming standard
PORT=8080
DOCROOT=/srv/time-clock
EOF
cat > /etc/init.d/timeclock <<'EOF'
#!/bin/sh
# timeclock - darkhttpd serving the front-desk time clock page. Settings: /etc/default/timeclock
PIDFILE=/run/timeclock/timeclock.pid; PORT=8080; DOCROOT=/srv/timeclock
[ -r /etc/default/timeclock ] && . /etc/default/timeclock
start() { printf 'Starting timeclock: '; mkdir -p /run/timeclock; chown nobody:nobody /run/timeclock
  if [ ! -d "$DOCROOT" ]; then echo "FAIL (document root $DOCROOT not found)"; logger -t timeclock "start failed: document root $DOCROOT not found"; return 1; fi
  if darkhttpd "$DOCROOT" --port "$PORT" --uid nobody --gid nobody --daemon --pidfile "$PIDFILE" --log /var/log/timeclock.log >/tmp/.timeclock 2>&1
  then echo "OK (port $PORT)"; logger -t timeclock "started on port $PORT from $DOCROOT"; else echo "FAIL ($(tail -1 /tmp/.timeclock))"; return 1; fi; }
stop() { printf 'Stopping timeclock: '; start-stop-daemon -K -q -p "$PIDFILE" && { rm -f "$PIDFILE"; echo OK; } || { echo "FAIL (not running)"; return 1; }; }
status() { if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then echo "timeclock is running (pid $(cat $PIDFILE))"; else echo "timeclock is stopped"; return 3; fi; }
case "$1" in start|stop|status) "$1";; restart) stop >/dev/null 2>&1; sleep 1; start;; *) echo "Usage: $0 {start|stop|restart|status}"; exit 1;; esac
EOF
chmod 755 /etc/init.d/timeclock
cat > /var/log/changes.log <<'EOF'
2026-10-14 09:12 CHG-7244 jlee   patched OpenSSH (apk upgrade openssh) - verified ssh login
2026-10-17 16:40 CHG-7290 contractor (facilities) tidy-up: folders renamed to the new naming standard (time-clock), removed unused S50 boot links
2026-10-17 16:52 CHG-7290 contractor rebooted clock-01 - "all fine"
EOF
cat > /root/SR-7301.ticket <<'EOF'
SR-7301  priority 2  opened 18 Oct 07:05 by M. Ortiz (front desk)
"The time clock page on the front-desk kiosk says it cannot connect, so nobody can clock in. It worked on Friday."
Kiosk uses: http://clock-01:8080/
EOF
echo '127.0.0.1 clock-01' >> /etc/hosts
logger -t ntpd "time skew 0.42 s corrected"
/etc/init.d/timeclock start >/dev/null 2>&1
logger -t kiosk "front-desk kiosk: connection refused to clock-01:8080"
"""
_CODE = "curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/"
_LINK = "l=$(readlink /etc/init.d/S50timeclock 2>/dev/null); [ \"$l\" = timeclock ] || [ \"$l\" = /etc/init.d/timeclock ]"
METHOD = {
    "id": "linux-vm-method",
    "title": "Real Linux VM — Time-Clock Service Repair",
    "kind": "vm",
    "blurb": "A real Linux server whose time-clock web service died after a contractor's tidy-up. Work the full "
             "troubleshooting method: identify (ticket, change log, status, logs), find the fault domain, write and test "
             "a theory, back up, fix, verify it would survive a reboot, and document — the order is graded.",
    "objectives": [
        {"id": "boot", "text": "Boot the VM"},
        {"id": "identify", "text": "Identify the problem before you change anything: read the ticket (/root/SR-7301.ticket) or the change log (/var/log/changes.log), check the service (service timeclock status) and read the system log"},
        {"id": "domain", "text": "Find the fault domain: what listens on port 8080 (ss -tln), does the server reach itself (curl http://127.0.0.1:8080/)? Record domain=network or domain=service in /root/SR-7301.txt"},
        {"id": "theory", "text": "Establish a theory and write it down before any change: a theory= line in /root/SR-7301.txt"},
        {"id": "test", "text": "Test the theory without changing anything: compare the configured DOCROOT with what is on disk (ls /srv, or diff the pre-change copy in /var/backups)"},
        {"id": "backup", "text": "Plan with a rollback: copy /etc/default/timeclock to /etc/default/timeclock.bak before you edit it"},
        {"id": "fix", "text": "Implement the fix: correct the setting in /etc/default/timeclock and restart the timeclock service"},
        {"id": "verify", "text": "Verify full functionality: after the restart the page loads (HTTP 200, the Clock in form), and the service will also start after a reboot"},
        {"id": "document", "text": "Document it: cause=<the setting that was wrong>, fix= and verified= lines in /root/SR-7301.txt, and log \"SR-7301 resolved\" to syslog with logger"},
    ],
    "intro": "SR-7301 from the front desk: \"the time clock page says it cannot connect, nobody can clock in\". clock-01 is a "
             "real Linux VM running the time clock web service (darkhttpd on port 8080, started by /etc/init.d/timeclock "
             "with settings in /etc/default/timeclock). This lab grades the method as much as the fix: your command "
             "history is part of the grade, so gather information and write a theory before you change anything, test "
             "the theory, keep a rollback copy, verify the way the user works, and document. Tools: cat, tail, grep, "
             "ss -tln, curl, ls, diff, cp, sed -i, service, ln -s, logger.",
    "success_msg": "SR-7301 resolved by the method: evidence first, a written and tested theory, a backed-up one-line fix, "
                   "full verification including the boot link, and the ticket documented.",
    "initial_state": {},
    "obj_hints": {
        "boot": ["Start the VM and wait for root@clock-01:~#.", "Start VM."],
        "identify": ["Step 1 of the method: gather information. What did the user report? What changed recently? What does the "
                     "service and its log say?", "cat /root/SR-7301.ticket ; cat /var/log/changes.log ; service timeclock status ; "
                                                 "tail -20 /var/log/messages"],
        "domain": ["\"Cannot connect\" can be the network or the service. If nothing listens on the port and even the server "
                   "cannot reach itself, the network is not the problem.",
                   "ss -tln ; curl -s http://127.0.0.1:8080/ ; echo domain=service >> /root/SR-7301.txt"],
        "theory": ["Step 2: state the most likely cause from your evidence (the log says why the start failed; the change log "
                   "says what changed). Write it before you touch the config.",
                   "echo 'theory=CHG-7290 renamed the folder; DOCROOT points at a path that does not exist' >> /root/SR-7301.txt"],
        "test": ["Step 3: confirm the theory without changing anything. Does the folder in DOCROOT exist? What did the file "
                 "say before the change?", "cat /etc/default/timeclock ; ls -ld /srv/* ; diff /var/backups/timeclock.2026-10-16 /etc/default/timeclock"],
        "backup": ["Step 4: plan the change and its rollback. A copy of the current file is the rollback.",
                   "cp /etc/default/timeclock /etc/default/timeclock.bak"],
        "fix": ["Step 5: one change — put DOCROOT back to the folder that really exists — then restart the service and read its "
                "message.", "sed -i 's|^DOCROOT=.*|DOCROOT=/srv/timeclock|' /etc/default/timeclock ; service timeclock restart"],
        "verify": ["Step 6: verify like the user (the kiosk loads http://clock-01:8080/), and think about the next reboot: the "
                   "change log says the tidy-up removed boot links. Scripts start at boot through /etc/init.d/S50* links.",
                   "ln -s timeclock /etc/init.d/S50timeclock ; curl -s -o /dev/null -w '%{http_code}\\n' http://clock-01:8080/ ; "
                   "curl -s http://clock-01:8080/ | grep -o 'Clock in'"],
        "document": ["Step 7: document the cause, the fix and how you verified it, so the next technician can follow it.",
                     "printf 'cause=DOCROOT\\nfix=DOCROOT back to /srv/timeclock, restored S50 link\\nverified=HTTP 200 from clock-01:8080\\n' "
                     ">> /root/SR-7301.txt ; logger SR-7301 resolved"],
    },
    "course_objectives": ["IT-7.1", "IT-7.2", "IT-7.3"],
    "minutes": 30,
    "palette": ["cat /root/SR-7301.ticket", "cat /var/log/changes.log", "service timeclock status", "tail -20 /var/log/messages",
                "ss -tln", "curl -s http://127.0.0.1:8080/", "cat /etc/default/timeclock", "ls -ld /srv/*", "diff ",
                "cp /etc/default/timeclock /etc/default/timeclock.bak", "sed -i ", "service timeclock restart",
                "ls -l /etc/init.d", "ln -s ", "cat /root/SR-7301.txt", "logger ", "clear"],
    "fallback": ["ticket-method", "linux-shell"],
    "vm": dict(IMAGE, machines=[_m("vm", "clock-01", "clock-01")], setup={"vm": _SETUP}),
    "vm_checks": [
        {"id": "boot"},
        {"id": "identify",
         "seq": [r"^(cat|less|more|head|tail|grep)\b.*(SR-7301\.ticket|changes\.log)", r"(service\s+timeclock|/etc/init\.d/timeclock)\s+(status|start|restart)"],
         "before": _EDIT, "hist": [r"^(cat|tail|head|grep|less|more)\b.*(/var/log/messages|timeclock\.log)|^logread\b"],
         "why": "Before you edit the settings: read the ticket or the change log, then the service status (service timeclock status) — and read /var/log/messages."},
        {"id": "domain", "sh": _ans("domain", "service", _ASK),
         "seq": [r"^(ss|netstat)\b.*-[a-z]*l", r"^(curl|wget)\b.*(127\.0\.0\.1|localhost|clock-01)(:8080)?"], "before": _EDIT,
         "show": f"grep -i '^domain' {_ASK} 2>&1 | tail -1",
         "why": "Before the fix, run ss -tln and then curl the server from itself; record the fault domain in /root/SR-7301.txt (now: {v})."},
        {"id": "theory", "sh": f"grep -Eq '^theory=.{{8,}}' {_ASK}",
         "seq": [r"^(cat|less|more|head|tail|grep)\b.*(SR-7301\.ticket|changes\.log|messages)", r"theory\s*="], "before": _EDIT,
         "why": "Write a theory= line (at least a few words) into /root/SR-7301.txt after reading the evidence and before you edit /etc/default/timeclock."},
        {"id": "test", "seq": [r"theory\s*=", r"^(ls\b.*/srv|diff\b.*timeclock|cat\b.*/var/backups/timeclock|grep\b.*DOCROOT|test\s+-d|\[\s+-d)"],
         "before": _EDIT,
         "why": "After writing the theory and before the edit, test it: ls the folders in /srv (or diff the copy in /var/backups)."},
        {"id": "backup", "sh": "grep -qx 'DOCROOT=/srv/time-clock' /etc/default/timeclock.bak && grep -qx 'PORT=8080' /etc/default/timeclock.bak",
         "why": "/etc/default/timeclock.bak is missing or is not a copy of the settings as you found them."},
        {"id": "fix", "sh": "( . /etc/default/timeclock; [ \"$DOCROOT\" = /srv/timeclock ] && [ \"$PORT\" = 8080 ] ) && service timeclock status >/dev/null && ss -tln | grep -q ':8080 '",
         "show": "grep '^DOCROOT' /etc/default/timeclock; service timeclock status", "secs": 6,
         "why": "timeclock must run on port 8080 from the corrected settings: {v}"},
        {"id": "verify", "sh": f"[ \"$({_CODE})\" = 200 ] && curl -s -m 3 http://127.0.0.1:8080/ | grep -q 'Clock in' && {_LINK}",
         "seq": [r"(service\s+timeclock|/etc/init\.d/(S50)?timeclock)\s+(restart|start)", r"^(curl|wget)\b.*(127\.0\.0\.1|localhost|clock-01)"],
         "show": f"echo http=$({_CODE}) bootlink=$(readlink /etc/init.d/S50timeclock 2>/dev/null || echo missing)", "secs": 8,
         "why": "After the restart, load the page (curl) — and make sure it starts at boot: {v}"},
        {"id": "document", "sh": _ans("cause", "docroot", _ASK) + f" && grep -Eq '^fix=.{{6,}}' {_ASK} && grep -Eq '^verified=.{{4,}}' {_ASK} "
                                                                  "&& grep -q 'SR-7301' /var/log/messages",
         "hist": [r"^logger\b"], "show": f"grep -Ei '^(cause|fix|verified)' {_ASK} 2>&1 | tr '\\n' ' '",
         "why": "/root/SR-7301.txt needs cause= (the setting), fix= and verified= lines, and logger must put SR-7301 in syslog (now: {v})."},
    ],
    "solution": {"vm_commands": [
        "cat /root/SR-7301.ticket", "cat /var/log/changes.log", "service timeclock status", "tail -20 /var/log/messages",
        "ss -tln", "curl -s -m 3 http://127.0.0.1:8080/", "echo domain=service >> /root/SR-7301.txt",
        "echo 'theory=CHG-7290 renamed the folder so DOCROOT points at a path that does not exist' >> /root/SR-7301.txt",
        "cat /etc/default/timeclock", "ls -ld /srv/*", "diff /var/backups/timeclock.2026-10-16 /etc/default/timeclock",
        "cp /etc/default/timeclock /etc/default/timeclock.bak",
        "sed -i 's|^DOCROOT=.*|DOCROOT=/srv/timeclock|' /etc/default/timeclock", "service timeclock restart",
        "ln -s timeclock /etc/init.d/S50timeclock",
        "curl -s -o /dev/null -w '%{http_code}\\n' http://clock-01:8080/", "curl -s http://clock-01:8080/ | grep -o 'Clock in'",
        "printf 'cause=DOCROOT\\nfix=DOCROOT back to /srv/timeclock, restored the S50 boot link\\nverified=HTTP 200 and the Clock in form from clock-01:8080\\n' >> /root/SR-7301.txt",
        "logger SR-7301 resolved", "cat /root/SR-7301.txt"]},
}

R5_LABS = [METHOD]
