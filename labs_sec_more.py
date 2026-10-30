"""Additional Security labs. Linux stations are real v86 VMs. Decision stations are graded activities.

Stage 1 may name a command. Stages 2 and 3 do not. Session values are written into the VM ticket
for that attempt and are not printed in the coaching text.
"""
from labs_sec import REVIEW, _act, _activity, _choice, _coach, _vm
from labs_vm import IMAGE, _m, _prelude

# ---------------------------------------------------------------- VM: backup
_BACKUP = _prelude('sec-bak-11') + r"""
mkdir -p /srv/keep /root
printf 'row,secret\n' > /srv/keep/{{NAME}}
printf 'scratch\n' > /srv/keep/notes.txt
cat > /root/TICKET << 'EOF'
Ticket BK-11.
Back up only the named data file under /srv/keep.
The file name is on the first line of /root/WHICH.
Write a gzip-compressed tar archive to /root/keep.tar.gz.
Write the sha256 of that archive, one field, to /root/keep.sha256.
Leave the original file in place.
EOF
printf '%s\n' '{{NAME}}' > /root/WHICH
"""
# The ticket body is quoted so the name is only in WHICH, which the setup fills.
# WHICH is written after the quoted ticket. {{NAME}} in the printf is replaced per attempt.

SEC_VM_BACKUP = _vm({
    'id': 'sec-vm-backup',
    'title': 'Real Linux VM — Backup and checksum',
    'blurb': 'Make a compressed archive of the one file the ticket names, and record its checksum.',
    'session_vars': {'NAME': ['payroll.dat', 'roster.dat', 'donors.dat']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read /root/WHICH'},
        {'id': 'archive', 'text': 'The archive exists and contains the named file'},
        {'id': 'sum', 'text': 'keep.sha256 matches the archive'},
        {'id': 'kept', 'text': 'The original file is still in /srv/keep'},
    ],
    'intro': 'The file to back up is named in /root/WHICH. Do not archive the scratch notes.',
    'success_msg': 'The named file is archived, checksummed, and still on disk.',
    'course_objectives': ['SEC-18.1'],
    'minutes': 25,
    'palette': ['cat /root/WHICH', 'tar -cf ', 'gzip ', 'sha256sum '],
    'hints': ['Read WHICH before you archive anything.', 'The scratch file is not part of the backup.', 'The checksum file should contain the fingerprint of the archive.'],
    'obj_hints': {
        'boot': ['The scenario names the file in a small text file.', 'Open it and use that name.'],
        'archive': ['A compressed tar archive is the deliverable.', 'Only the named file belongs in it.'],
        'sum': ['Fingerprint the archive, not the original file.', 'One field in the checksum file is enough.'],
        'kept': ['A backup is a copy. The source stays.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>tar -cf</code> writes an uncompressed archive. '
        'BusyBox tar has no gzip flag, so pipe the archive into <code>gzip</code>. '
        '<code>sha256sum</code> prints a fingerprint. This walkthrough uses a sample name, sample.dat, which is not the live file.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover the live file name on the system. '
        'Archive only that file, compress the archive, and store the archive fingerprint where the ticket says. '
        'Leave the source file where it is. Do not include the scratch notes.</p>',
        '<p><strong>Stage 3 — ticket BK-11.</strong> Counsel wants one file from the keep directory, compressed, with a fingerprint of the archive. '
        'The original must still be readable afterward.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-bak-11', 'sec-bak-11')], setup={'vm': _BACKUP}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'archive', 'sh': "gzip -dc /root/keep.tar.gz | tar -t | grep -q '{{NAME}}'",
         'why': 'The archive is missing or does not contain the named file.'},
        {'id': 'sum', 'sh': "got=$(sha256sum /root/keep.tar.gz | awk '{print $1}'); want=$(awk '{print $1}' /root/keep.sha256); [ -n \"$want\" ] && [ \"$got\" = \"$want\" ]",
         'why': 'The checksum file does not match the archive.'},
        {'id': 'kept', 'sh': "[ -s /root/keep.tar.gz ] && [ -s /srv/keep/'{{NAME}}' ]",
         'why': 'The original file is missing.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/WHICH',
        'tar -cf - -C /srv/keep "{{NAME}}" | gzip -c > /root/keep.tar.gz',
        'sha256sum /root/keep.tar.gz | awk \'{print $1}\' > /root/keep.sha256',
    ]},
})

# ---------------------------------------------------------------- VM: world-writable
_WORLD = _prelude('sec-ww-12') + r"""
mkdir -p /srv/drop
printf 'secret\n' > /srv/drop/{{NAME}}
chmod 666 /srv/drop/{{NAME}}
printf 'readme\n' > /srv/drop/readme.txt
chmod 644 /srv/drop/readme.txt
printf '%s\n' '{{NAME}}' > /root/WHICH
"""
SEC_VM_WORLD = _vm({
    'id': 'sec-vm-world',
    'title': 'Real Linux VM — Close a world-writable file',
    'blurb': 'One file in the drop folder is writable by everyone. Close it. Leave the readme alone.',
    'session_vars': {'NAME': ['export.csv', 'ledger.csv', 'badge.csv']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and find the world-writable file'},
        {'id': 'mode', 'text': 'The named file is no longer writable by others'},
    ],
    'intro': 'The sensitive name is in /root/WHICH. Others must not be able to write it. Do not delete it.',
    'success_msg': 'The named file is closed to other accounts. The readme is unchanged.',
    'course_objectives': ['SEC-7.1'],
    'minutes': 20,
    'palette': ['ls -l ', 'chmod ', 'cat /root/WHICH'],
    'hints': ['A long listing shows who can write.', 'The readme is not the file you tighten.', 'Do not delete the data.'],
    'obj_hints': {
        'boot': ['List the drop folder before you change a mode.', 'The ticket file names the sensitive one.'],
        'mode': ['Others should not have write.', 'Owner can keep read and write.'],
        'readme': ['The notes file was already safe.', 'Leave its mode as you found it.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>ls -l</code> shows a <code>w</code> in the other triple when everyone can write. '
        '<code>chmod o-w FILE</code> removes that bit. Practice the idea on a sample name, not the live file.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover which drop-folder file is writable by every account. '
        'Remove other-write on that file only. Leave the readme mode as it is, and leave the bytes in place.</p>',
        '<p><strong>Stage 3 — ticket WW-12.</strong> A shared drop folder has one sensitive file the night operator left wide open. '
        'Close it. Do not "fix" the readme.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-ww-12', 'sec-ww-12')], setup={'vm': _WORLD}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'mode', 'sh': "ls -l /srv/drop/'{{NAME}}' | grep -q '^-rw-rw-r-- '",
         'why': 'The named file is still writable by others, or it is gone.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/WHICH',
        'ls -l /srv/drop',
        'chmod o-w /srv/drop/{{NAME}}',
    ]},
})

# ---------------------------------------------------------------- VM: sudo least privilege
_SUDO = _prelude('sec-sudo-13') + r"""
id {{USER}} >/dev/null 2>&1 || useradd -m {{USER}}
printf '{{USER}} ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/wide
chmod 666 /etc/sudoers.d/wide
printf '%s\n' '{{USER}}' > /root/WHICH
"""
SEC_VM_SUDO = _vm({
    'id': 'sec-vm-sudo',
    'title': 'Real Linux VM — Least privilege sudo',
    'blurb': 'A sudoers drop-in lets one person run anything. Narrow it to listing files as root.',
    'session_vars': {'USER': ['audit', 'reader', 'clerk']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read which account is named'},
        {'id': 'narrow', 'text': 'The drop-in allows only /bin/ls'},
        {'id': 'mode', 'text': 'The drop-in is mode 440'},
    ],
    'intro': 'The account is in /root/WHICH. The drop-in is /etc/sudoers.d/wide. It is too broad.',
    'success_msg': 'That account may run only ls as root, and the file mode is 440.',
    'course_objectives': ['SEC-22.1'],
    'minutes': 25,
    'palette': ['cat /root/WHICH', 'ls -l /etc/sudoers.d', 'cat '],
    'hints': ['Read the drop-in before you replace it.', 'The allowed command is the directory listing tool, as root.', 'Mode 440 keeps others from writing the rule.'],
    'obj_hints': {
        'boot': ['The account name is a one-line file.', 'Use that name in the rule.'],
        'narrow': ['ALL is too wide.', 'Name one command.'],
        'mode': ['sudoers files are not world-writable.', '440 is the usual mode.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> A sudoers drop-in is a small file under <code>/etc/sudoers.d</code>. '
        'A line <code>USER ALL=(root) NOPASSWD: /bin/ls</code> allows one command. '
        '<code>chmod 440</code> locks the file. Practice the shape with a sample user, not the live account.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover the account. Replace the wide rule so that account may run only the directory listing command as root, without a password. '
        'Keep the file mode tight.</p>',
        '<p><strong>Stage 3 — ticket SU-13.</strong> The night operator granted a clerk every root command. '
        'Narrow the drop-in to listing files. Do not delete the account.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-sudo-13', 'sec-sudo-13')], setup={'vm': _SUDO}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'narrow', 'sh': "grep -q '^{{USER}} ALL=(root) NOPASSWD: /bin/ls$' /etc/sudoers.d/wide && ! grep -q 'ALL=(ALL)' /etc/sudoers.d/wide",
         'why': 'The drop-in is missing or still too wide.'},
        {'id': 'mode', 'sh': "ls -l /etc/sudoers.d/wide | grep -q '^-r--r----- '",
         'why': 'The drop-in mode is not 440.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/WHICH',
        'printf \'{{USER}} ALL=(root) NOPASSWD: /bin/ls\\n\' > /etc/sudoers.d/wide',
        'chmod 440 /etc/sudoers.d/wide',
    ]},
})

# ---------------------------------------------------------------- VM: capture transcript
_CAP = _prelude('sec-cap-14') + r"""
mkdir -p /root/case
cat > /root/case/capture.txt << 'EOF'
10:01 10.8.0.10 -> 10.8.0.5 TCP 443
10:02 10.8.0.40 -> 10.1.1.9 TCP 22
10:03 10.8.0.10 -> 10.8.0.5 TCP 443
EOF
# The odd flow is rewritten per attempt so a copied walkthrough has the wrong address.
python3 - << 'PY' 2>/dev/null || true
PY
printf '%s\n' '{{ADDR}}' > /root/WHICH
# Stamp the odd line using the address, replacing the placeholder row.
awk -v a="$(cat /root/WHICH)" 'NR==2 {$3=a} {print}' /root/case/capture.txt > /root/case/capture.new
mv /root/case/capture.new /root/case/capture.txt
"""
SEC_VM_CAPTURE = _vm({
    'id': 'sec-vm-capture',
    'title': 'Real Linux VM — Read a packet capture transcript',
    'blurb': 'A saved capture transcript has one odd flow. Copy only that line into the case file.',
    'session_vars': {'ADDR': ['10.9.9.9', '10.7.7.7', '10.6.6.6']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the transcript and WHICH'},
        {'id': 'hit', 'text': 'The case file contains the odd address'},
        {'id': 'clean', 'text': 'The normal 443 flows are not in the case file'},
    ],
    'intro': 'The odd address is in /root/WHICH. The transcript is /root/case/capture.txt. Write matching lines to /root/case/odd.txt.',
    'success_msg': 'The case file has the odd flow and not the ordinary web flows.',
    'course_objectives': ['SEC-26.3'],
    'minutes': 20,
    'palette': ['cat /root/WHICH', 'grep ', 'cat '],
    'hints': ['The address you care about is in WHICH.', 'Ordinary web flows are not the finding.', 'Write the matching lines into the case file named odd.txt.'],
    'obj_hints': {
        'boot': ['Read both the transcript and the address file.', 'The second column of the address is the source.'],
        'hit': ['Only lines with the odd address belong in odd.txt.'],
        'clean': ['Port 443 between the two known hosts is normal here.', 'Leave those lines out of the case file.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>grep</code> prints lines that match. '
        'Redirect with <code>&gt;</code> to save them. A sample address such as 192.0.2.1 is not in this capture.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover the odd address. '
        'Save every transcript line that contains it into /root/case/odd.txt. Leave the ordinary web lines out, and do not delete the transcript.</p>',
        '<p><strong>Stage 3 — ticket CAP-14.</strong> The sensor team saved a short transcript. '
        'Deliver only the odd flow in the case folder. Keep the source transcript.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-cap-14', 'sec-cap-14')], setup={'vm': _CAP}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'hit', 'sh': "grep -q '{{ADDR}}' /root/case/odd.txt && [ -f /root/case/capture.txt ]",
         'why': 'odd.txt is missing the odd address, or the transcript was removed.'},
        {'id': 'clean', 'sh': "[ -s /root/case/odd.txt ] && ! grep -q 'TCP 443' /root/case/odd.txt",
         'why': 'The case file is missing or includes an ordinary web flow.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/WHICH',
        'grep "$(cat /root/WHICH)" /root/case/capture.txt > /root/case/odd.txt',
    ]},
})

# ---------------------------------------------------------------- VM: timeline
_TIME = _prelude('sec-time-15') + r"""
mkdir -p /root/case
cat > /var/log/app.log << 'EOF'
08:01 backup ok
09:14 login failed user ada
09:16 login failed user ada
11:02 backup ok
EOF
printf '%s\n' '{{USER}}' > /root/WHICH
# Rewrite the failed user to the session value.
sed -i "s/ada/$(cat /root/WHICH)/" /var/log/app.log
"""
SEC_VM_TIMELINE = _vm({
    'id': 'sec-vm-timeline',
    'title': 'Real Linux VM — Incident timeline',
    'blurb': 'Pull the failed logins for the named account into a timeline file, in the order they appear.',
    'session_vars': {'USER': ['ada', 'ben', 'chio']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the account name'},
        {'id': 'lines', 'text': 'The timeline has both failures and no backup lines'},
        {'id': 'order', 'text': 'The earlier failure is first'},
    ],
    'intro': 'The account is in /root/WHICH. The log is /var/log/app.log. Write /root/case/timeline.txt.',
    'success_msg': 'The timeline has the two failures in order and nothing else.',
    'course_objectives': ['SEC-25.1'],
    'minutes': 20,
    'palette': ['cat /root/WHICH', 'grep ', 'cat '],
    'hints': ['Match the account from WHICH.', 'Backup lines are a different event.', 'Keep the log order.'],
    'obj_hints': {
        'boot': ['The account is one word in WHICH.'],
        'lines': ['Failed logins only.', 'Do not include the backup lines.'],
        'order': ['Do not sort the lines yourself if the log is already in order.', 'The earlier time comes first.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>grep</code> keeps matching lines in the order they appear. '
        'Redirect into the case file. A sample account name such as sam is not the live account.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover the account. '
        'Save the failed login lines for that account, in log order, to /root/case/timeline.txt. Leave backup lines out.</p>',
        '<p><strong>Stage 3 — ticket TL-15.</strong> Counsel wants a timeline of the failed logins and only those lines. '
        'Keep the source log.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-time-15', 'sec-time-15')], setup={'vm': _TIME}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'lines', 'sh': "grep -q '{{USER}}' /root/case/timeline.txt && ! grep -q backup /root/case/timeline.txt && [ $(grep -c failed /root/case/timeline.txt) -eq 2 ]",
         'why': 'The timeline is missing a failure or it includes a backup line.'},
        {'id': 'order', 'sh': "grep -q '{{USER}}' /root/case/timeline.txt && awk 'NR==1{a=$1} NR==2{b=$1} END{exit !(a<b)}' /root/case/timeline.txt",
         'why': 'The failures are out of order.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/WHICH',
        'grep "$(cat /root/WHICH)" /var/log/app.log | grep failed > /root/case/timeline.txt',
    ]},
})

# ---------------------------------------------------------------- VM: file integrity
_FIM = _prelude('sec-fim-16') + r"""
mkdir -p /srv/bin /root
printf '#!/bin/sh\necho ok\n' > /srv/bin/{{NAME}}
chmod 755 /srv/bin/{{NAME}}
sha256sum /srv/bin/{{NAME}} > /root/baseline.txt
printf '#!/bin/sh\necho tampered\n' > /srv/bin/{{NAME}}
printf '%s\n' '{{NAME}}' > /root/WHICH
"""
SEC_VM_FIM = _vm({
    'id': 'sec-vm-fim',
    'title': 'Real Linux VM — File integrity',
    'blurb': 'A baseline hash no longer matches the tool. Restore the tool so the baseline matches again.',
    'session_vars': {'NAME': ['health.sh', 'probe.sh', 'check.sh']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and compare the tool to the baseline'},
        {'id': 'match', 'text': 'sha256sum -c /root/baseline.txt succeeds'},
    ],
    'intro': 'The baseline is /root/baseline.txt. The tool name is in /root/WHICH. The bytes were changed after the baseline.',
    'success_msg': 'The tool matches the baseline again.',
    'course_objectives': ['SEC-21.1'],
    'minutes': 20,
    'palette': ['sha256sum -c ', 'cat /root/WHICH', 'cat '],
    'hints': ['The baseline tells you the expected fingerprint.', 'The current file does not match.', 'Put the original program text back. The baseline expects a script that prints ok.'],
    'obj_hints': {
        'boot': ['Check the baseline before you edit.', 'The mismatch is the finding.'],
        'match': ['The checker should exit clean.', 'Do not edit the baseline to fit the tampered file.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>sha256sum -c FILE</code> checks a saved fingerprint. '
        'A mismatch means the bytes changed. Restoring means putting the known-good bytes back, not editing the baseline. '
        'A sample script that prints ok is the shape of the known-good file.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover the tool name. '
        'The baseline no longer matches. Restore the known-good script so the check passes. Do not change the baseline file.</p>',
        '<p><strong>Stage 3 — ticket FIM-16.</strong> Integrity monitoring flagged one tool. '
        'Make the baseline match again by repairing the tool, not by weakening the baseline.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-fim-16', 'sec-fim-16')], setup={'vm': _FIM}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'match', 'sh': 'sha256sum -c /root/baseline.txt',
         'why': 'The file still does not match the baseline.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/WHICH',
        'sha256sum -c /root/baseline.txt',
        'printf \'#!/bin/sh\\necho ok\\n\' > /srv/bin/{{NAME}}',
        'sha256sum -c /root/baseline.txt',
    ]},
})

# ---------------------------------------------------------------- VM: harden a listener
_HARD = _prelude('sec-hard-17') + r"""
# A decoy listener is recorded as a pid file the student must stop by killing that pid.
mkdir -p /root
sleep 1000 &
echo $! > /root/extra.pid
printf '%s\n' '{{PORT}}' > /root/WHICH
# Record the port as a note. The live task is to stop the extra sleep.
"""
SEC_VM_HARDEN = _vm({
    'id': 'sec-vm-harden',
    'title': 'Real Linux VM — Stop an extra process',
    'blurb': 'An extra long-running process was left behind. Stop it. The pid is in a file. Do not stop your shell.',
    'session_vars': {'PORT': ['8088', '9099', '7077']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the pid file'},
        {'id': 'gone', 'text': 'That pid is no longer running'},
    ],
    'intro': 'The ticket note /root/WHICH is the port the operator meant to document. The process to stop is the pid in /root/extra.pid.',
    'success_msg': 'The extra process is gone.',
    'course_objectives': ['SEC-16.1'],
    'minutes': 15,
    'palette': ['cat /root/extra.pid', 'ps ', 'kill '],
    'hints': ['The pid file names the extra process.', 'Do not kill pid 1.', 'Confirm the pid is gone afterward.'],
    'obj_hints': {
        'boot': ['Read the pid file before you signal anything.'],
        'gone': ['A signal stops the process.', 'Check that the pid is no longer in the process list.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>ps</code> lists processes. '
        '<code>kill PID</code> asks that one process to exit. Never signal pid 1. A sample pid such as 99999 is not the live pid.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover the pid on the system. '
        'Stop that process and confirm it is gone. Leave the shell you are typing in running.</p>',
        '<p><strong>Stage 3 — ticket HD-17.</strong> Hardening leftover: one extra process is still running from a test. '
        'Stop it. Do not reboot.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-hard-17', 'sec-hard-17')], setup={'vm': _HARD}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'gone', 'sh': 'pid=$(cat /root/extra.pid); ! kill -0 "$pid" 2>/dev/null',
         'why': 'The extra process is still running.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/extra.pid',
        'kill "$(cat /root/extra.pid)"',
    ]},
})

# ---------------------------------------------------------------- VM: password aging
_AGE = _prelude('sec-age-18') + r"""
id {{USER}} >/dev/null 2>&1 || useradd -m {{USER}}
printf '%s\n' '{{USER}}' > /root/WHICH
"""
SEC_VM_AGE = _vm({
    'id': 'sec-vm-faillock',
    'title': 'Real Linux VM — Password aging',
    'blurb': 'Set the named account so the password must be at least 14 days old before a change, and it expires after 90 days.',
    'session_vars': {'USER': ['nina', 'omar', 'priya']},
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the account name'},
        {'id': 'min', 'text': 'Minimum password age is 14 days'},
        {'id': 'max', 'text': 'Maximum password age is 90 days'},
    ],
    'intro': 'The account is in /root/WHICH. Use the aging tool. Do not delete the account.',
    'success_msg': 'The account has a 14-day minimum and a 90-day maximum password age.',
    'course_objectives': ['SEC-22.1'],
    'minutes': 20,
    'palette': ['cat /root/WHICH', 'chage -l ', 'chage '],
    'hints': ['Read the account name first.', 'Minimum age and maximum age are different fields.', 'Do not lock the account.'],
    'obj_hints': {
        'boot': ['WHICH has the account.'],
        'min': ['The shortest wait before a change is 14 days.'],
        'max': ['The password must be changed by 90 days.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>chage -l USER</code> shows aging. '
        '<code>chage -m 14 -M 90 USER</code> sets the minimum and the maximum. '
        'Practice the flags on a sample name such as sam, which is not the live account.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Discover the account. '
        'Set the minimum age to 14 days and the maximum age to 90 days. Do not delete the account or lock the password.</p>',
        '<p><strong>Stage 3 — ticket AGE-18.</strong> The account policy for this person is a 14-day minimum and a 90-day maximum. '
        'Apply it and confirm by listing the aging fields.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-age-18', 'sec-age-18')], setup={'vm': _AGE}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'min', 'sh': "chage -l {{USER}} | awk -F: '/Minimum/{gsub(/ /,\"\",$2); if($2==\"14\") ok=1} END{exit !ok}'",
         'why': 'Minimum age is not 14.'},
        {'id': 'max', 'sh': "chage -l {{USER}} | awk -F: '/Maximum/{gsub(/ /,\"\",$2); if($2==\"90\") ok=1} END{exit !ok}'",
         'why': 'Maximum age is not 90.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/WHICH',
        'chage -m 14 -M 90 {{USER}}',
        'chage -l {{USER}}',
    ]},
})


def _ticket_step():
    def _eq(field):
        def check(got, vals, answer):
            from labs_activity import norm
            return norm(got) == norm(vals.get(field) or ''), 'Read the value in the prompt.'
        return check
    return {
        'id': 's0', 'type': 'fields', 'objective': 'read', 'gen': 'ticket',
        'title': 'Read the ticket',
        'prompt': 'Ticket {case} is about host {host}. Type both values before you decide.',
        'fields': [
            {'name': 'case', 'label': 'Case number', 'check': _eq('case')},
            {'name': 'host', 'label': 'Host', 'check': _eq('host')},
        ],
        'right': 'You read the case and the host from this attempt.',
    }


def _read_back(state):
    vals = (state.get('gen') or {}).get('s0') or {}
    return {'case': vals.get('case') or '', 'host': vals.get('host') or ''}


def _decide(lid, title, blurb, skill, prompts):
    lab = _activity(lid, title, blurb, skill, prompts)
    lab['steps'] = [_ticket_step()] + lab['steps']
    lab['objectives'] = [{'id': 'read', 'text': 'Read the case number and host for this attempt'}] + lab['objectives']
    lab['solution']['answers']['s0'] = _read_back
    return lab


SEC_OPENSSL = _decide(
    'sec-openssl', 'Certificate decisions — keys and requests',
    'The browser Linux image has no openssl binary, so this station grades the decisions. Stage 1 names the commands. Later stages do not.',
    'SEC-7.1',
    [
        ('You need a certificate for mail.example.edu. What do you send to the authority?',
         ['A signing request, and you keep the private key', 'The private key', 'Only a hash of the hostname', 'A self-signed certificate for a different name'],
         0, {1: 'The private key stays on the server.', 2: 'A hash is not a request.', 3: 'The name has to be the name you serve.'},
         'Send the request. Keep the private key.'),
        ('Which command family creates the key pair on the server before the request?',
         ['The key-generation command, on the server that will use the key', 'Email the private key to the authority first', 'Download a private key from a website', 'Reuse last year\'s private key from a chat log'],
         0, {1: 'The authority never needs the private key.', 2: 'A downloaded private key is not yours.', 3: 'A key from a chat is already exposed.'},
         'Generate the key where it will live.'),
        ('The returned certificate name does not match the site. You:',
         ['Stop and ask for a certificate with the right name', 'Click through and add a permanent exception', 'Turn off TLS', 'Replace the site name with the certificate name without telling anyone'],
         0, {1: 'A permanent exception hides the next mismatch.', 2: 'Clear text is not the fix.', 3: 'Renaming the service to fit a bad certificate hides the mistake.'},
         'The name must match. Do not click through.'),
        ('A wildcard certificate is:',
         ['Broader than a single name, so a leaked key hurts more names', 'Safer than a single name because it is shorter', 'A private key', 'A hash'],
         0, {1: 'Broader is not safer.', 2: 'It is not the private key.', 3: 'It is not a fingerprint.'},
         'A wildcard covers many names. Treat the key with extra care.'),
    ],
)
SEC_OPENSSL['coaching'] = _coach(
    '<p><strong>Stage 1 — guided.</strong> On a machine that has the tool, <code>openssl genrsa</code> creates a private key, '
    '<code>openssl req -new</code> builds a signing request from that key, and you send only the request. '
    '<code>openssl x509 -req</code> is what an authority uses to sign. <code>openssl verify</code> checks a chain. '
    'The private key stays on the server. This station has no openssl binary, so you will be graded on the decisions.</p>',
    '<p><strong>Stage 2 — assisted.</strong> Each prompt is a certificate decision. '
    'Keep the secret half at home. Match the name. Treat a broad name as a broader blast radius.</p>',
    '<p><strong>Stage 3 — ticket CERT-7.</strong> You are the person who requests the certificate. '
    'Choose the action you can defend. There is no command line on this station.</p>',
)

SEC_VULN = _decide(
    'sec-vuln', 'Read a vulnerability scan',
    'Sort scan lines. No exploit is run.',
    'SEC-19.1',
    [
        ('A critical finding on a host that is powered off in a closet, and a medium finding on the public website. What do you schedule first?',
         ['The public website', 'The closet host, because the score is higher', 'Neither, until next year', 'Both, by buying a new firewall brand first'],
         0, {1: 'A high score on an unreachable host is not first.', 2: 'Waiting a year leaves the public site exposed.', 3: 'A purchase is not the finding.'},
         'Exposure and impact outrank a raw score on a dead host.'),
        ('The scanner flags a library you already patched, because the banner string never changed. This is:',
         ['A likely false positive to confirm', 'Proof the patch failed', 'A zero-day by definition', 'A reason to turn the scanner off'],
         0, {1: 'A stale banner is not proof.', 2: 'A zero-day is an unpatched unknown, not a stale banner.', 3: 'Turning the scanner off hides the next real finding.'},
         'Confirm the banner lie before you reopen the change.'),
        ('You cannot patch a lab instrument this month. The honest record is:',
         ['A dated exception plus a fence that limits who can reach it', 'Silence', 'Mark it fixed', 'Delete the asset from the inventory so the scan is clean'],
         0, {1: 'Silence is not an exception.', 2: 'Marking it fixed is false.', 3: 'Hiding the asset is not remediation.'},
         'Write the exception and reduce the exposure.'),
        ('After the patch window you:',
         ['Rescan and attach the result', 'Close the ticket because the change was approved', 'Assume the banner update is enough with no check', 'Turn off logging'],
         0, {1: 'Approval is not verification.', 2: 'Hope is not a rescan.', 3: 'Logging is how you would see a miss.'},
         'Verify. Then close.'),
    ],
)

SEC_CLASSIFY = _decide(
    'sec-classify', 'Classify the data',
    'Pick the handling. No files are copied.',
    'SEC-17.1',
    [
        ('A spreadsheet of card numbers is:',
         ['Financial information that does not go to a personal mailbox', 'Public, because the shop is public', 'A honeytoken by default', 'Safe to paste into a ticket'],
         0, {1: 'A public shop does not make card numbers public.', 2: 'It is real data, not a decoy.', 3: 'Tickets are widely readable.'},
         'Card numbers are financial data. Keep them in the approved system.'),
        ('A file marked restricted sits on a world-readable share. The problem is:',
         ['The handling does not match the label', 'The label is decorative and can be ignored', 'Labels replace permissions', 'World-readable is the definition of restricted'],
         0, {1: 'A label the handling ignores is a finding.', 2: 'The label does not replace the permission.', 3: 'World-readable is the opposite of restricted.'},
         'Make the handling match the label, or fix the label if it was wrong.'),
        ('Data open on a lobby screen is:',
         ['Data in use, even if the disk is encrypted', 'Protected because the disk is encrypted', 'Data at rest', 'Impossible to shoulder-surf'],
         0, {1: 'Disk encryption does not cover an open screen.', 2: 'At rest means stored, not displayed.', 3: 'A lobby screen is easy to read over a shoulder.'},
         'In use is its own state.'),
        ('A token stored in the register, with the real card number only in the vault, is:',
         ['Tokenization', 'A hash of the whole disk', 'Steganography', 'A wildcard certificate'],
         0, {1: 'A disk hash does not replace the card number in the till.', 2: 'Nothing is hidden inside a picture.', 3: 'A certificate is a different object.'},
         'The stand-in is a token. The secret stays in the vault.'),
    ],
)

SEC_ARCH = _decide(
    'sec-arch', 'Recovery sites',
    'Choose the site that matches the promise. No failover is performed.',
    'SEC-18.1',
    [
        ('You need to be back in minutes and you can pay for a live copy. Which site?',
         ['Hot', 'Cold', 'An empty room with power', 'No site, because backups are enough for a minutes-long promise'],
         0, {1: 'Cold is space, not a live copy.', 2: 'An empty room is cold.', 3: 'A backup you still have to restore will not hit a minutes-long promise.'},
         'Hot means the spare is already live.'),
        ('Gear is racked and last night\'s backup must be restored. That is:',
         ['Warm', 'Hot', 'Air-gapped', 'A generator'],
         0, {1: 'Hot would already have the data.', 2: 'An air gap is a network choice.', 3: 'A generator makes power, not a site.'},
         'Warm needs a catch-up.'),
        ('Two copies in the same building protect you from:',
         ['A single server failure, not a building fire', 'A regional flood', 'A provider going away', 'A lost password'],
         0, {1: 'A flood of the region takes both if they share the building.', 2: 'A second provider is a different design.', 3: 'Copies do not remember a password.'},
         'Distance is what survives a building-level disaster.'),
        ('A backup you have never restored is:',
         ['A hope, until a restore test passes', 'Proof of recovery', 'A hot site', 'Encryption'],
         0, {1: 'An untested copy is not proof.', 2: 'A backup is not a hot site.', 3: 'Encryption is whether a thief can read it.'},
         'Restore something on a schedule.'),
    ],
)

SEC_VENDOR = _decide(
    'sec-vendor', 'Vendor agreements',
    'Pick the paper that matches the promise.',
    'SEC-27.1',
    [
        ('You need a measurable uptime promise. Which paper?',
         ['A service-level agreement', 'A non-disclosure agreement', 'A honeypot', 'A baseline image'],
         0, {1: 'A non-disclosure promise is about secrecy, not uptime.', 2: 'A honeypot is a decoy system.', 3: 'An image is a build, not a contract.'},
         'Uptime belongs in the service-level agreement.'),
        ('A non-disclosure agreement:',
         ['Limits sharing. It does not prove the vendor\'s controls', 'Replaces an audit', 'Is a penetration test', 'Sets the firewall rules'],
         0, {1: 'Secrecy is not an audit.', 2: 'It is not a test.', 3: 'It does not configure devices.'},
         'Read it as a secrecy promise, then still check the controls.'),
        ('Before customer data moves, you:',
         ['Compare security needs, not only price', 'Pick the cheapest and review next year', 'Skip the contract because the demo was friendly', 'Email the data to three vendors to see who answers'],
         0, {1: 'Cheapest without the control is how data gets stuck.', 2: 'A demo is not a control.', 3: 'A bake-off that emails real data is a disclosure.'},
         'Score the controls before the data moves.'),
        ('Rules of engagement for a test should name:',
         ['What is allowed, what is forbidden, and who to call', 'Only the price', 'The tester\'s home address on a public page', 'That any system may be destroyed'],
         0, {1: 'Price is a different document.', 2: 'Do not publish personal data.', 3: 'Destruction is not an implied right.'},
         'Scope and a phone number belong on the first page.'),
    ],
)

SEC_ZT = _decide(
    'sec-zerotrust', 'Zero trust decisions',
    'Decide what the gate should do. No network is changed.',
    'SEC-3.1',
    [
        ('A laptop is on the office wifi, so every internal app trusts it. That is:',
         ['An implicit trust zone', 'A policy enforcement point', 'A hash', 'A hot site'],
         0, {1: 'The enforcement point is the gate that can say no.', 2: 'A hash is a fingerprint.', 3: 'A hot site is a recovery copy.'},
         'Inside means safe is the assumption zero trust refuses.'),
        ('The component that weighs the signals and returns allow or deny is:',
         ['The policy engine', 'The camera', 'The generator', 'The backup tape'],
         0, {1: 'A camera records.', 2: 'A generator makes power.', 3: 'A tape stores bytes.'},
         'The engine decides. Something else enforces.'),
        ('The gate that actually drops the session is:',
         ['The policy enforcement point', 'The policy document in a wiki', 'The heat map', 'The risk register'],
         0, {1: 'A wiki page does not drop packets.', 2: 'A heat map shows wifi.', 3: 'A register lists risks.'},
         'Enforcement is the door that moves.'),
        ('Adaptive identity means:',
         ['A riskier sign-in gets a harder check', 'Every sign-in is identical', 'Passwords are removed with no replacement', 'The office network is trusted'],
         0, {1: 'Identical checks ignore risk.', 2: 'Removing a factor with nothing else is not adaptive.', 3: 'Trusting the office is the old assumption.'},
         'The check gets harder when the signals look worse.'),
    ],
)

SEC_AWARE = _decide(
    'sec-awareness', 'Report a suspicious message',
    'Choose the human response. Do not build a phish.',
    'SEC-28.1',
    [
        ('A payroll lookalike arrives. You:',
         ['Report it and do not click', 'Click to verify the site', 'Forward it to the whole clinic', 'Reply with your password to confirm'],
         0, {1: 'Clicking is the payload.', 2: 'Forwarding spreads the bait.', 3: 'A password in a reply is a gift.'},
         'Report. Do not poke it.'),
        ('A caller says they are the CEO and need a code from your phone. You:',
         ['Refuse and call back using the directory number', 'Read the code because they sound senior', 'Disable your own factor', 'Text the code to the number they give you'],
         0, {1: 'Seniority is not identity.', 2: 'Disabling the factor is the attacker\'s goal.', 3: 'Their number is the untrusted channel.'},
         'Callback on a number you already had.'),
        ('An annual video nobody remembers is:',
         ['Not a program, until the behavior is practiced and measured', 'Proof of awareness', 'A penetration test', 'A firewall'],
         0, {1: 'A forgotten video is not evidence of a habit.', 2: 'It is not a test of systems.', 3: 'It does not filter traffic.'},
         'Repeat the habit and measure the reports.'),
        ('A found USB stick is:',
         ['Turned in, not mounted on a work computer', 'Opened on your laptop so you can find the owner', 'Copied to the file share', 'Booted from'],
         0, {1: 'Mounting it is how bait runs.', 2: 'The share would spread it.', 3: 'Booting from it is worse.'},
         'Found media stays out of work computers.'),
    ],
)

SEC_IAM = _decide(
    'sec-iam', 'Access models',
    'Pick the model the story describes.',
    'SEC-22.1',
    [
        ('Rights are attached to the job, and people move in and out of the job. That is:',
         ['Role-based access', 'A shared password', 'A honeytoken', 'Full-disk encryption'],
         0, {1: 'A shared password has no job boundary.', 2: 'A honeytoken is a decoy secret.', 3: 'Disk encryption is a different control.'},
         'The role carries the rights.'),
        ('The owner of a file can grant access to a teammate. That is:',
         ['Discretionary access', 'Mandatory access, which the owner cannot relax', 'A firewall', 'A generator'],
         0, {1: 'Mandatory labels do not yield to the owner.', 2: 'A firewall filters packets.', 3: 'A generator makes power.'},
         'Discretionary means the owner decides.'),
        ('Admin rights for two hours, then gone, is:',
         ['Just-in-time privilege', 'A permanent admin group', 'A default password', 'Shadow IT'],
         0, {1: 'Permanent admin is the opposite.', 2: 'A default password is a published secret.', 3: 'Shadow IT is an unapproved system.'},
         'Short-lived privilege is the point.'),
        ('A password plus a PIN is:',
         ['Still one factor kind', 'Multi-factor authentication', 'A certificate chain', 'A hot site'],
         0, {1: 'Both are something you know.', 2: 'A certificate is not two secrets.', 3: 'A hot site is recovery.'},
         'Mix kinds, or you do not have multi-factor authentication.'),
    ],
)

SEC_CHANGE = _decide(
    'sec-change', 'Change control',
    'Pick the missing piece of the change.',
    'SEC-5.1',
    [
        ('The new rule is about to be typed, and nobody saved the previous rules. You are missing:',
         ['A backout plan', 'A honeypot', 'A heat map', 'A generator'],
         0, {1: 'A decoy is not an undo path.', 2: 'A wifi map does not restore a ruleset.', 3: 'Power does not undo a bad rule.'},
         'Know how to get back before you change production.'),
        ('Payroll was not told the file server will reboot during Friday close. You missed:',
         ['Stakeholders', 'A hash', 'A salt', 'An air gap'],
         0, {1: 'A fingerprint does not warn a team.', 2: 'A salt is a password ingredient.', 3: 'An air gap is a network with no path.'},
         'Tell the people whose work will stop.'),
        ('The change worked, and the wall diagram still shows the old network. You still need:',
         ['An updated diagram', 'A longer password', 'A new vendor', 'A logic bomb'],
         0, {1: 'Password length is unrelated.', 2: 'A vendor is not the picture.', 3: 'A logic bomb is an attack.'},
         'The picture has to match the wires.'),
        ('Someone uses the window to attempt a database rewrite that was not in the ticket. That is:',
         ['A restricted activity', 'The point of a maintenance window', 'A baseline', 'Non-repudiation'],
         0, {1: 'The window is not a free pass.', 2: 'A baseline is the approved build.', 3: 'Non-repudiation is about proof of who acted.'},
         'Stay inside the ticket.'),
    ],
)

SEC_INDICATORS = _decide(
    'sec-indicators', 'Sort the signal',
    'Decide what the signal most strongly suggests. Do not accuse a person in the ticket.',
    'SEC-10.1',
    [
        ('One account signs in from two continents an hour apart. The best label is:',
         ['Impossible travel', 'A normal lunch break', 'A patch', 'A cold site'],
         0, {1: 'A lunch break does not cross an ocean.', 2: 'A patch is a fix.', 3: 'A cold site is a recovery room.'},
         'Nobody travels that fast. Investigate the account.'),
        ('Dozens of accounts show one failure each, same common password, same hour. That pattern is:',
         ['Password spraying', 'One user who forgot a password', 'A backup', 'A site survey'],
         0, {1: 'One forgetful user does not touch dozens of accounts.', 2: 'A backup does not fail logins.', 3: 'A survey measures wifi.'},
         'One guess, many doors.'),
        ('The authentication log has a two-hour hole on the night of the incident. You treat the hole as:',
         ['A finding, not as proof that nothing happened', 'Proof the night was quiet', 'A reason to delete the rest of the log', 'Expected, so you close the ticket'],
         0, {1: 'A gap is not a quiet night.', 2: 'Deleting more log makes it worse.', 3: 'Expected gaps are documented. This one is on the incident night.'},
         'Missing logs are evidence.'),
        ('A leak site names your clinic. You:',
         ['Verify whether the sample is real, then follow the incident path', 'Ignore it because the internet lies', 'Pay immediately', 'Post the sample in a public chat to ask'],
         0, {1: 'Ignoring skips verification.', 2: 'Paying is not the first student action.', 3: 'A public chat spreads the data.'},
         'A public claim is a lead. Check it. Do not spread the sample.'),
    ],
)

SEC_DLP = _decide(
    'sec-dlp', 'Data leaving the building',
    'Choose the control that matches the exit.',
    'SEC-20.1',
    [
        ('Card numbers are leaving by email. The control aimed at that exit is:',
         ['Data loss prevention', 'A generator', 'A bollard', 'A heat map'],
         0, {1: 'A generator makes power.', 2: 'A bollard stops a car.', 3: 'A heat map shows wifi.'},
         'DLP watches for sensitive data on the way out.'),
        ('You want who talked to whom without storing every packet. You ask for:',
         ['Flow records', 'A full packet capture of a year', 'A password dump', 'A wildcard certificate'],
         0, {1: 'A year of packets is heavy and full of secrets.', 2: 'A password dump is an incident, not a tool.', 3: 'A certificate does not summarize conversations.'},
         'Flow records are the summary.'),
        ('A file server sends logs only to its own disk. A later wipe would erase the story. You want:',
         ['Log aggregation to another system', 'Fewer logs', 'A shorter retention of zero days', 'To turn the audit log off'],
         0, {1: 'Fewer logs hide the event.', 2: 'Zero retention is amnesia.', 3: 'Turning it off is the attacker\'s preference.'},
         'Copy the logs somewhere the wiped host cannot reach.'),
        ('An alert that pages nobody is:',
         ['A log line with extra steps', 'A finished incident response', 'A policy', 'A hot site'],
         0, {1: 'Response needs a person.', 2: 'A policy is a rule.', 3: 'A hot site is a spare environment.'},
         'Name who answers.'),
    ],
)

SEC_PRIVACY = _decide(
    'sec-privacy', 'Privacy duties',
    'Pick the duty. Do not invent a legal conclusion beyond the story.',
    'SEC-27.1',
    [
        ('The person the record is about is:',
         ['The data subject', 'The processor by default', 'A honeytoken', 'The load balancer'],
         0, {1: 'A processor handles data for someone else.', 2: 'A honeytoken is a decoy.', 3: 'A load balancer shares traffic.'},
         'The subject is the person in the data.'),
        ('A deletion request arrives during a legal hold. You:',
         ['Check the hold before anything is wiped', 'Delete every copy immediately, including the hold set', 'Ignore the request forever', 'Post the record publicly so the person can see it'],
         0, {1: 'The hold exists so those copies stay.', 2: 'Forever-ignore is not the process.', 3: 'Publishing is a new disclosure.'},
         'The hold and the request both get a decision. Do not wipe blindly.'),
        ('The clinic decides why records exist. The mail host only handles mail under the contract. The host is:',
         ['A processor', 'The data owner of the clinical purpose', 'A regulator', 'A penetration tester'],
         0, {1: 'The clinic decides the purpose.', 2: 'A regulator examines.', 3: 'A tester is a scoped engagement.'},
         'The controller decides. The processor handles.'),
        ('Keeping everything forever is:',
         ['Not the safe default. Retention has an end.', 'Required by every rule', 'The same as encryption', 'A backup test'],
         0, {1: 'Many rules tell you to delete.', 2: 'Retention is not encryption.', 3: 'A restore test proves a copy, it does not set a keep-forever rule.'},
         'Know the date the data should go.'),
    ],
)

SEC_PENTEST = _decide(
    'sec-pentest', 'Audit and test scope',
    'Choose the test that answers the question. Do not attack anything from this station.',
    'SEC-28.1',
    [
        ('You want to know what a stranger can do, with little inside information. Ask for:',
         ['An unknown-environment test', 'A known-environment test only', 'A password dump from production', 'A generator test'],
         0, {1: 'A known-environment test answers a different question.', 2: 'A dump is not a scoped test.', 3: 'A generator test is about power.'},
         'Unknown means the tester starts like an outsider.'),
        ('You want to know whether the on-call team notices. Add:',
         ['A defensive side to the exercise', 'Only a longer report', 'A public blog during the test', 'A wipe of the logs first'],
         0, {1: 'A longer report does not train detection.', 2: 'Publishing mid-test is not the scope.', 3: 'Wiping logs destroys the thing you want to measure.'},
         'Someone has to be scored on noticing.'),
        ('A physical test:',
         ['Tries doors and tailgating, inside the written safety rules', 'Means any locked room may be smashed', 'Replaces the need for permission', 'Is the same as a vulnerability scan'],
         0, {1: 'Smashing is not the default.', 2: 'Permission is still required.', 3: 'A scan does not walk into a lobby.'},
         'Physical, scoped, and safe.'),
        ('An internal audit finding is:',
         ['Still a finding', 'Optional because your own team wrote it', 'A fine', 'A certificate'],
         0, {1: 'Internal does not mean ignorable.', 2: 'A fine is a regulator\'s penalty.', 3: 'A certificate is a different artifact.'},
         'Track it like any other finding.'),
    ],
)

SEC_WIRELESS = _decide(
    'sec-wireless', 'Wireless choices',
    'Pick the wireless decision.',
    'SEC-16.1',
    [
        ('The staff network should use:',
         ['WPA3, with a fallback path fenced if a device cannot speak it', 'An open network, because the building has a lock', 'A shared passphrase taped to the lobby', 'WEP, because it is simple'],
         0, {1: 'A door lock does not protect the radio.', 2: 'A taped passphrase is a published secret.', 3: 'WEP is retired.'},
         'Current protection, and fence the devices that cannot do it.'),
        ('Each person signs in with their own account, and access dies when the account is disabled. That needs:',
         ['RADIUS, not a shared passphrase', 'A heat map only', 'A bollard', 'A cold site'],
         0, {1: 'A heat map shows coverage. It does not authenticate.', 2: 'A bollard stops a car.', 3: 'A cold site is a recovery room.'},
         'Per-person sign-in is RADIUS or an equivalent.'),
        ('You place access points by:',
         ['A survey and a heat map, not by guessing from the hallway', 'Putting them all in the wiring closet', 'Maximizing spill into the parking lot', 'Skipping the survey to save an hour'],
         0, {1: 'A closet full of radios does not cover the floor.', 2: 'Spill into the lot is exposure.', 3: 'A guess misses dead zones.'},
         'Measure, then place.'),
        ('A second network appears with your name, and laptops join it from the lobby. That is:',
         ['A wireless evil-twin style attack', 'A successful site survey', 'Load balancing', 'Salting'],
         0, {1: 'A survey is something you run on purpose.', 2: 'Load balancing shares servers.', 3: 'Salting is a password ingredient.'},
         'A lookalike radio is an attack. Do not join it.'),
    ],
)

SEC_LOGS = _decide(
    'sec-logtriage', 'Choose the log',
    'Pick the record that answers the question.',
    'SEC-26.1',
    [
        ('You want denied connections. Look in:',
         ['Firewall logs', 'A heat map', 'A certificate signing request', 'A generator test log only'],
         0, {1: 'A heat map is wifi coverage.', 2: 'A signing request is a certificate step.', 3: 'A generator log is about power.'},
         'Allows and denies are firewall log questions.'),
        ('You want the app\'s own export at 03:00. Look in:',
         ['Application logs', 'Only the building badge log', 'A bollard inspection', 'A password policy poster'],
         0, {1: 'The badge log shows doors, not app exports.', 2: 'A bollard is a post.', 3: 'A poster is not a log.'},
         'The application writes its own diary.'),
        ('You want who signed in to the operating system. Look in:',
         ['The operating-system security log', 'The print queue', 'The heat map', 'The vendor brochure'],
         0, {1: 'Print jobs are not sign-ins.', 2: 'A heat map is coverage.', 3: 'A brochure is marketing.'},
         'Authentication lives in the security log.'),
        ('A green dashboard over a collector that stopped yesterday is:',
         ['Not proof the night was quiet', 'Proof of health', 'A penetration test', 'Encryption'],
         0, {1: 'Green can mean the picture is not being fed.', 2: 'A test is an engagement.', 3: 'Encryption is a different control.'},
         'Check that the summary is still receiving logs.'),
    ],
)

MORE_VM = [
    SEC_VM_BACKUP, SEC_VM_WORLD, SEC_VM_SUDO, SEC_VM_CAPTURE, SEC_VM_TIMELINE,
    SEC_VM_FIM, SEC_VM_HARDEN, SEC_VM_AGE,
]
MORE_ACTIVITY = [
    SEC_OPENSSL, SEC_VULN, SEC_CLASSIFY, SEC_ARCH, SEC_VENDOR, SEC_ZT, SEC_AWARE,
    SEC_IAM, SEC_CHANGE, SEC_INDICATORS, SEC_DLP, SEC_PRIVACY, SEC_PENTEST,
    SEC_WIRELESS, SEC_LOGS,
]
