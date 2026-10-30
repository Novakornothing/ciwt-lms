"""Additional Security labs. Imported by labs_sec after its helpers exist.

Per-session labs embed @@TOK@@ in the VM setup. Stage 1 teaches with the sample
code DEMO00. The live code is only on the VM. Stage 2 and stage 3 do not contain
the solution commands.
"""
from labs_sec import _activity, _prelude, _vm
from labs_vm import IMAGE, _m

_MARK = '@@TOK@@'


def _tok_setup(host, body):
    return _prelude(host) + body.replace('TOKEN', _MARK)


# --- VM: backup copy and hash, code is on the VM ---
_BACKUP = _tok_setup('sec-bak-11', r"""
mkdir -p /root/work /root/safe
echo "payroll row TOKEN" > /root/work/pay-TOKEN.txt
echo "CODE TOKEN" > /root/TICKET
echo "Copy the pay file named in /root/TICKET into /root/safe and record its sha256." >> /root/TICKET
""")

SEC_VM_BACKUP = _vm({
    'id': 'sec-vm-backup',
    'title': 'Real Linux VM — Backup copy and hash',
    'blurb': 'Make a restorable copy of the payroll file named on this VM, and record a fingerprint.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the ticket'},
        {'id': 'copied', 'text': 'The pay file from the ticket exists under /root/safe'},
        {'id': 'hashed', 'text': '/root/safe/hash.txt matches the copy'},
    ],
    'intro': 'The file name is on this machine, in /root/TICKET. A sample name in the walkthrough will not match.',
    'success_msg': 'The safe copy matches the original and the fingerprint was recorded.',
    'course_objectives': ['SEC-18.3'],
    'minutes': 20,
    'palette': ['cat /root/TICKET', 'ls /root/work', 'cp ', 'sha256sum '],
    'hints': [
        'The ticket names the file. The walkthrough sample is not this session.',
        'Put the copy under /root/safe and keep the original.',
        'The fingerprint file should contain the checksum of the copy.',
    ],
    'obj_hints': {
        'boot': ['The scenario is a file in the home directory.', 'Read it before you copy anything.'],
        'copied': ['The safe directory is where the restorable copy belongs.', 'Use the name from the ticket, not a sample name.'],
        'hashed': ['A fingerprint is a checksum of the copy.', 'Write that checksum into hash.txt in the safe directory.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> On a practice host you might run '
                  '<code>cp /root/work/pay-DEMO00.txt /root/safe/</code> and then '
                  '<code>sha256sum /root/safe/pay-DEMO00.txt &gt; /root/safe/hash.txt</code>. '
                  'DEMO00 is a sample. It is not the code on your VM.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Read the ticket on the system. '
                  'Copy the pay file it names into the safe directory. Record a sha256 fingerprint of that copy. '
                  'Leave the original in place.</p>',
        'stage3': '<p><strong>Stage 3 — ticket BK-restore.</strong> Payroll needs a restorable copy and a fingerprint '
                  'before the maintenance window. Deliver both under the safe directory. The code for this session is on the machine.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-bak-11', 'sec-bak-11')], setup={'vm': _BACKUP}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'copied', 'sh': "tok=$(sed -n 's/^CODE //p' /root/TICKET); cmp /root/work/pay-$tok.txt /root/safe/pay-$tok.txt",
         'why': 'The safe copy is missing or does not match the original named in the ticket.'},
        {'id': 'hashed', 'sh': "tok=$(sed -n 's/^CODE //p' /root/TICKET); got=$(sha256sum /root/safe/pay-$tok.txt | awk '{print $1}'); grep -q \"$got\" /root/safe/hash.txt",
         'why': 'hash.txt does not contain the checksum of the safe copy.'},
    ],
    'solution': {'vm_commands': [
        "sed -n 's/^CODE //p' /root/TICKET",
        'cp /root/work/pay-$(sed -n \'s/^CODE //p\' /root/TICKET).txt /root/safe/',
        'sha256sum /root/safe/pay-$(sed -n \'s/^CODE //p\' /root/TICKET).txt > /root/safe/hash.txt',
    ]},
})

_TIME = _tok_setup('sec-time-12', r"""
mkdir -p /root/case /var/log
cat > /var/log/case.log <<EOF
12:01 backup ok
12:04 CASE TOKEN login failed from 203.0.113.50
12:05 disk warning
12:09 CASE TOKEN session opened
EOF
echo "CODE TOKEN" > /root/TICKET
echo "Save only the lines for this case into /root/case/timeline.txt" >> /root/TICKET
""")

SEC_VM_TIMELINE = _vm({
    'id': 'sec-vm-timeline',
    'title': 'Real Linux VM — Incident timeline extract',
    'blurb': 'Pull only the lines for this session case id into a timeline file.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the ticket'},
        {'id': 'lines', 'text': 'timeline.txt has both case lines'},
        {'id': 'clean', 'text': 'timeline.txt does not include the disk warning'},
    ],
    'intro': 'The case id is on the VM. A sample id from the walkthrough will not match the log.',
    'success_msg': 'The timeline has the case lines and leaves the unrelated warning out.',
    'course_objectives': ['SEC-26.2'],
    'minutes': 20,
    'palette': ['cat /root/TICKET', 'cat /var/log/case.log', 'grep '],
    'hints': [
        'The case id is in the ticket, not in the walkthrough sample.',
        'Keep lines that name the case. Drop the disk warning.',
        'Do not delete the original log.',
    ],
    'obj_hints': {
        'boot': ['Start by reading the ticket file.', 'The log is under /var/log.'],
        'lines': ['Both events for this case belong in the timeline.', 'Write them to the path the ticket names.'],
        'clean': ['A nearby warning is a different event.', 'It should not be in the extract.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> A practice extract uses a sample id: '
                  '<code>grep DEMO00 /var/log/case.log</code>. DEMO00 is not in this log. '
                  'Redirect a match into a new file when you have the real id.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Discover the case id from the ticket. '
                  'Save only the matching log lines into /root/case/timeline.txt. Leave the source log intact.</p>',
        'stage3': '<p><strong>Stage 3 — ticket TL-case.</strong> Counsel wants the case lines and only those lines. '
                  'Deliver the timeline in the case folder.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-time-12', 'sec-time-12')], setup={'vm': _TIME}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'lines', 'sh': "tok=$(sed -n 's/^CODE //p' /root/TICKET); grep -q \"CASE $tok login\" /root/case/timeline.txt && grep -q \"CASE $tok session\" /root/case/timeline.txt",
         'why': 'The timeline is missing a case line.'},
        {'id': 'clean', 'sh': "[ -s /root/case/timeline.txt ] && ! grep -q 'disk warning' /root/case/timeline.txt && [ -f /var/log/case.log ]",
         'why': 'The timeline includes an unrelated warning, or the source log is gone.'},
    ],
    'solution': {'vm_commands': [
        "sed -n 's/^CODE //p' /root/TICKET",
        'grep "$(sed -n \'s/^CODE //p\' /root/TICKET)" /var/log/case.log > /root/case/timeline.txt',
    ]},
})

_WIPE = _tok_setup('sec-wipe-13', r"""
mkdir -p /srv/retired /root/audit
echo "secret TOKEN" > /srv/retired/key-TOKEN.bin
echo "SERIAL TOKEN" > /root/TICKET
echo "Destroy the retired key and record its serial in /root/audit/destroyed.txt" >> /root/TICKET
""")

SEC_VM_WIPE = _vm({
    'id': 'sec-vm-wipe',
    'title': 'Real Linux VM — Retire a secret file',
    'blurb': 'Remove the retired key named on this VM and record its serial.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the ticket'},
        {'id': 'gone', 'text': 'The retired key file is gone'},
        {'id': 'logged', 'text': 'destroyed.txt contains the serial from the ticket'},
    ],
    'intro': 'The serial and the file name are on the VM. Do not remove unrelated files.',
    'success_msg': 'The retired key is gone and the serial is in the audit file.',
    'course_objectives': ['SEC-20.3'],
    'minutes': 15,
    'palette': ['cat /root/TICKET', 'ls /srv/retired', 'rm '],
    'hints': [
        'The ticket names the serial and the file.',
        'Remove only that retired key.',
        'Write the serial into the audit file.',
    ],
    'obj_hints': {
        'boot': ['Read the ticket before you delete.', 'The retired files are under /srv/retired.'],
        'gone': ['The key file should no longer exist.', 'Leave the directory itself.'],
        'logged': ['The audit file must contain the serial from the ticket.', 'Create /root/audit/destroyed.txt if needed.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> A sample serial DEMO00 is not on this VM. '
                  'You would remove a file named with that serial and write the serial into an audit note. '
                  'Use the serial this machine shows you.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Find the retired key and its serial. '
                  'Remove the key. Record the serial in /root/audit/destroyed.txt.</p>',
        'stage3': '<p><strong>Stage 3 — ticket RT-key.</strong> The retired key must not remain on disk. '
                  'The audit note has to name the serial so the inventory can be closed.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-wipe-13', 'sec-wipe-13')], setup={'vm': _WIPE}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'gone', 'sh': "tok=$(sed -n 's/^SERIAL //p' /root/TICKET); [ ! -e /srv/retired/key-$tok.bin ]",
         'why': 'The retired key file is still present.'},
        {'id': 'logged', 'sh': "tok=$(sed -n 's/^SERIAL //p' /root/TICKET); grep -q \"$tok\" /root/audit/destroyed.txt",
         'why': 'The audit file does not contain the serial.'},
    ],
    'solution': {'vm_commands': [
        "sed -n 's/^SERIAL //p' /root/TICKET",
        'rm /srv/retired/key-$(sed -n \'s/^SERIAL //p\' /root/TICKET).bin',
        'sed -n \'s/^SERIAL //p\' /root/TICKET > /root/audit/destroyed.txt',
    ]},
})

_BASE = _prelude('sec-base-14') + r"""
mkdir -p /etc/sec /root
printf 'firewall=on\nssh=keyonly\n' > /etc/sec/baseline
printf 'firewall=off\nssh=keyonly\n' > /etc/sec/current
cat > /root/TICKET <<'EOF'
The host drifted from /etc/sec/baseline.
Make /etc/sec/current match the baseline.
EOF
"""

SEC_VM_BASELINE = _vm({
    'id': 'sec-vm-baseline',
    'title': 'Real Linux VM — Correct configuration drift',
    'blurb': 'A setting drifted from the baseline. Put the current file back in line.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and compare the two files'},
        {'id': 'match', 'text': '/etc/sec/current matches the baseline'},
    ],
    'intro': 'Compare /etc/sec/baseline with /etc/sec/current. Change only the drifted line.',
    'success_msg': 'The current configuration matches the baseline.',
    'course_objectives': ['SEC-19.1'],
    'minutes': 15,
    'palette': ['cat /etc/sec/baseline', 'cat /etc/sec/current', 'diff '],
    'hints': ['Read both files before you edit.', 'The baseline is the target.', 'Do not delete the baseline.'],
    'obj_hints': {
        'boot': ['The ticket names the two paths.', 'A difference is the drift.'],
        'match': ['The current file should become the same text as the baseline.', 'Leave the baseline file in place.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> <code>diff file1 file2</code> shows lines that differ. '
                  'You copy the intended line into the file that drifted. This walkthrough does not name the live values.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Find the line that does not match the baseline and correct the current file.</p>',
        'stage3': '<p><strong>Stage 3 — ticket DRIFT-1.</strong> Bring the host back to the written baseline. Do not weaken the baseline to match the drift.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-base-14', 'sec-base-14')], setup={'vm': _BASE}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'match', 'sh': 'cmp /etc/sec/baseline /etc/sec/current', 'why': 'current still differs from the baseline.'},
    ],
    'solution': {'vm_commands': [
        'diff /etc/sec/baseline /etc/sec/current',
        'cp /etc/sec/baseline /etc/sec/current',
    ]},
})

_SUDO = _prelude('sec-sudo-15') + r"""
adduser -D -H helpdesk 2>/dev/null || true
mkdir -p /etc/sudoers.d
echo 'helpdesk ALL=(ALL) ALL' > /etc/sudoers.d/helpdesk
cat > /root/TICKET <<'EOF'
helpdesk may only run /bin/ls as root.
Replace the wide sudo rule. Do not delete the account.
EOF
"""

SEC_VM_SUDO = _vm({
    'id': 'sec-vm-sudo',
    'title': 'Real Linux VM — Least privilege sudo',
    'blurb': 'The helpdesk account can do anything as root. Narrow it to one command.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the sudo rule'},
        {'id': 'narrow', 'text': 'helpdesk sudo is limited to /bin/ls'},
    ],
    'intro': 'The rule is in /etc/sudoers.d/helpdesk. The ticket says which command may remain.',
    'success_msg': 'helpdesk can run only the command the ticket allows.',
    'course_objectives': ['SEC-24.6'],
    'minutes': 20,
    'palette': ['cat /etc/sudoers.d/helpdesk', 'ls /bin/ls'],
    'hints': ['Read the current rule before you replace it.', 'The account should remain.', 'Name the one allowed command.'],
    'obj_hints': {
        'boot': ['The drop-in file is under sudoers.d.', 'A rule that says ALL is wider than the ticket.'],
        'narrow': ['The allowed command is the one the ticket names.', 'Do not leave a second wide rule.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> A sudoers drop-in can name one command instead of ALL. '
                  'A sample line for a different account would not satisfy this ticket. Read the live file.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Replace the wide rule so the helpdesk account may run only the command in the ticket.</p>',
        'stage3': '<p><strong>Stage 3 — ticket SUDO-ls.</strong> Daily support must not be full root. Leave the account. Narrow the rule.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-sudo-15', 'sec-sudo-15')], setup={'vm': _SUDO}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'narrow', 'sh': "grep -q '^helpdesk .* /bin/ls$' /etc/sudoers.d/helpdesk && ! grep -q 'ALL=(ALL) ALL' /etc/sudoers.d/helpdesk",
         'why': 'The sudo rule is still wider than /bin/ls.'},
    ],
    'solution': {'vm_commands': [
        'cat /etc/sudoers.d/helpdesk',
        "printf '%s\\n' 'helpdesk ALL=(ALL) /bin/ls' > /etc/sudoers.d/helpdesk",
    ]},
})

_BANNER = _prelude('sec-ban-16') + r"""
echo 'Welcome' > /etc/issue
cat > /root/TICKET <<'EOF'
Set /etc/issue to exactly: Authorized use only. Activity is logged.
EOF
"""

SEC_VM_BANNER = _vm({
    'id': 'sec-vm-banner',
    'title': 'Real Linux VM — Sign-in banner',
    'blurb': 'Replace the friendly banner with the authorized-use line from the ticket.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the current banner'},
        {'id': 'text', 'text': '/etc/issue matches the ticket sentence'},
    ],
    'intro': 'The required sentence is in /root/TICKET. /etc/issue is what a console shows before login.',
    'success_msg': 'The banner matches the authorized-use sentence.',
    'course_objectives': ['SEC-19.2'],
    'minutes': 10,
    'palette': ['cat /etc/issue', 'cat /root/TICKET'],
    'hints': ['Read the ticket for the exact sentence.', 'Write it to the banner file.', 'Do not leave the old welcome line.'],
    'obj_hints': {
        'boot': ['The banner file is /etc/issue.', 'The ticket has the required words.'],
        'text': ['The file should contain the authorized-use sentence.', 'An extra welcome line is not the ticket.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> A banner is a text file shown before login. '
                  'You replace its contents with the sentence the organization requires. Copy it from the ticket, not from memory.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Put the ticket sentence into /etc/issue.</p>',
        'stage3': '<p><strong>Stage 3 — ticket BAN-1.</strong> The console must warn that use is authorized and logged.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-ban-16', 'sec-ban-16')], setup={'vm': _BANNER}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'text', 'sh': "grep -qx 'Authorized use only. Activity is logged.' /etc/issue",
         'why': 'The banner is not the required sentence.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/TICKET',
        "printf '%s\\n' 'Authorized use only. Activity is logged.' > /etc/issue",
    ]},
})

_SHADOW = _prelude('sec-sh-17') + r"""
chmod 644 /etc/shadow 2>/dev/null || true
cat > /root/TICKET <<'EOF'
/etc/shadow is readable by everyone. Close it so only root can read it.
EOF
"""

SEC_VM_SHADOW = _vm({
    'id': 'sec-vm-shadow',
    'title': 'Real Linux VM — Protect the password file',
    'blurb': 'The shadow file is world-readable. Close it.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and inspect /etc/shadow mode'},
        {'id': 'mode', 'text': '/etc/shadow is not readable by group or others'},
    ],
    'intro': 'Password hashes live in /etc/shadow. Others should not be able to read it.',
    'success_msg': 'Only root can read the shadow file.',
    'course_objectives': ['SEC-24.5'],
    'minutes': 10,
    'palette': ['ls -l /etc/shadow', 'chmod '],
    'hints': ['Look at the mode before you change it.', 'Others should have no access.', 'Do not delete the file.'],
    'obj_hints': {
        'boot': ['A long listing shows who can read the file.', 'World-readable hashes are the problem.'],
        'mode': ['Remove group and other read.', 'Root should still be able to read it.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> <code>ls -l</code> shows the mode. '
                  'Numeric mode 600 means owner read and write, nothing for anyone else. Apply that idea to the shadow file, not to a sample path.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Close /etc/shadow so group and others cannot read it.</p>',
        'stage3': '<p><strong>Stage 3 — ticket SH-600.</strong> Password hashes must not be world-readable. Leave the file in place.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-sh-17', 'sec-sh-17')], setup={'vm': _SHADOW}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'mode', 'sh': "perms=$(stat -c %a /etc/shadow 2>/dev/null || ls -l /etc/shadow | awk '{print $1}'); ls -l /etc/shadow | grep -q '^-rw------- '",
         'why': 'Group or others can still read /etc/shadow.'},
    ],
    'solution': {'vm_commands': [
        'ls -l /etc/shadow',
        'chmod 600 /etc/shadow',
    ]},
})

_PATH = _prelude('sec-path-18') + r"""
mkdir -p /tmp/scratch
chmod 777 /tmp/scratch
cat > /root/TICKET <<'EOF'
/tmp/scratch is writable by everyone. Make it owner-only (mode 700).
EOF
"""

SEC_VM_PATH = _vm({
    'id': 'sec-vm-path',
    'title': 'Real Linux VM — Close a world-writable directory',
    'blurb': 'A scratch directory is writable by every account. Close it.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and inspect /tmp/scratch'},
        {'id': 'mode', 'text': '/tmp/scratch is mode 700'},
    ],
    'intro': 'World-writable directories are a place for planted programs. The ticket names the directory.',
    'success_msg': 'Only the owner can use the scratch directory.',
    'course_objectives': ['SEC-14.4'],
    'minutes': 10,
    'palette': ['ls -ld /tmp/scratch', 'chmod '],
    'hints': ['Look at the directory mode, not a file inside it.', 'Owner-only is the ticket.', 'Do not delete the directory.'],
    'obj_hints': {
        'boot': ['A long listing of the directory shows the write bits.', 'Everyone can write today.'],
        'mode': ['700 is owner read, write, and enter. Nothing for group or others.', 'Apply it to the directory the ticket names.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> <code>ls -ld</code> shows a directory. '
                  'Mode 700 closes it to everyone but the owner. The live path is in the ticket, not in this sentence.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Close the world-writable scratch directory so only the owner can use it.</p>',
        'stage3': '<p><strong>Stage 3 — ticket DIR-700.</strong> A shared writable directory is an easy place to drop a program. Close it.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-path-18', 'sec-path-18')], setup={'vm': _PATH}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'mode', 'sh': "ls -ld /tmp/scratch | grep -q '^d[r-][w-][x-]------ '",
         'why': 'The directory is still accessible to group or others.'},
    ],
    'solution': {'vm_commands': [
        'ls -ld /tmp/scratch',
        'chmod 700 /tmp/scratch',
    ]},
})

_LISTEN = _prelude('sec-listen-19') + r"""
mkdir -p /root/audit
cat > /root/listeners.txt <<'EOF'
tcp 0 0 0.0.0.0:22 users:(("sshd",pid=1,fd=3))
tcp 0 0 0.0.0.0:8089 users:(("debug",pid=9,fd=4))
EOF
cat > /root/TICKET <<'EOF'
A debug service is listening on 8089. Record that port, and only that surprise port, in /root/audit/unexpected.txt.
Do not record port 22.
EOF
"""

SEC_VM_LISTEN = _vm({
    'id': 'sec-vm-listener',
    'title': 'Real Linux VM — Unexpected listener',
    'blurb': 'A capture of listening sockets includes a surprise port. Record only that port.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the listener list'},
        {'id': 'port', 'text': 'unexpected.txt contains 8089 and not 22'},
    ],
    'intro': 'The listener list is /root/listeners.txt. SSH on 22 is expected. The ticket says what to record.',
    'success_msg': 'The surprise port is recorded and the expected SSH port is not in the finding.',
    'course_objectives': ['SEC-19.5'],
    'minutes': 15,
    'palette': ['cat /root/listeners.txt', 'cat /root/TICKET'],
    'hints': ['Expected remote administration is not the finding.', 'Record the surprise port.', 'Do not include the SSH port in the finding file.'],
    'obj_hints': {
        'boot': ['Read the listener list and the ticket.', 'One port is the service you meant to run.'],
        'port': ['The finding file should name the unexpected port.', 'Leave the expected port out of that file.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> A listener line includes an address and a port. '
                  'You keep the port that the ticket calls a surprise. Writing every port into the finding hides the signal.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Write the unexpected port into /root/audit/unexpected.txt. Leave SSH out of that file.</p>',
        'stage3': '<p><strong>Stage 3 — ticket PORT-8089.</strong> Report the debug listener. Do not file the expected administration port as the incident.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-listen-19', 'sec-listen-19')], setup={'vm': _LISTEN}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'port', 'sh': "grep -q 8089 /root/audit/unexpected.txt && ! grep -q 22 /root/audit/unexpected.txt",
         'why': 'The finding is missing 8089 or it includes port 22.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/listeners.txt',
        "printf '%s\\n' 8089 > /root/audit/unexpected.txt",
    ]},
})

_GROUP = _prelude('sec-grp-20') + r"""
grep -q '^auditor:' /etc/passwd || echo 'auditor:x:201:201:auditor:/:/bin/false' >> /etc/passwd
grep -q '^review:' /etc/group || echo 'review:x:200:' >> /etc/group
cat > /root/TICKET <<'EOF'
GROUP review
USER auditor
Add the user to the group named in the ticket.
EOF
"""

SEC_VM_GROUP = _vm({
    'id': 'sec-vm-group',
    'title': 'Real Linux VM — Add a user to a review group',
    'blurb': 'Put the auditor in the review group named on this VM. Do not grant extra admin rights.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the ticket'},
        {'id': 'member', 'text': 'The user is a member of the named group'},
    ],
    'intro': 'Group and user names are in /root/TICKET.',
    'success_msg': 'The auditor is in the review group.',
    'course_objectives': ['SEC-24.2'],
    'minutes': 15,
    'palette': ['cat /root/TICKET', 'grep review /etc/group'],
    'hints': ['Read the user and the group from the ticket.', 'Membership is the goal, not a new admin account.', 'Do not delete the user.'],
    'obj_hints': {
        'boot': ['The ticket has two names.', 'Confirm the group exists.'],
        'member': ['The user should appear on that group line.', 'A wide sudo rule is not the request.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> Group membership is recorded in the group database. '
                  'A sample user DEMO is not the account on this VM. Read the ticket, then add that user to that group.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Add the user named in the ticket to the group named in the ticket.</p>',
        'stage3': '<p><strong>Stage 3 — ticket GRP-review.</strong> The auditor needs the review group and nothing broader.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-grp-20', 'sec-grp-20')], setup={'vm': _GROUP}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'member', 'sh': "grep -q '^review:.*auditor' /etc/group",
         'why': 'auditor is not in the review group.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/TICKET',
        "sed -i 's/^review:\\([^:]*\\):\\([^:]*\\):$/review:\\1:\\2:auditor/' /etc/group",
    ]},
})

_UMASK = _prelude('sec-umask-21') + r"""
mkdir -p /root/work
umask 000
touch /root/work/note.txt
chmod 666 /root/work/note.txt
cat > /root/TICKET <<'EOF'
/root/work/note.txt is world-writable. Make it owner read-write only (mode 600).
EOF
"""

SEC_VM_UMASK = _vm({
    'id': 'sec-vm-umask',
    'title': 'Real Linux VM — Fix a world-writable note',
    'blurb': 'A note was created wide open. Close it to the owner.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and inspect the note'},
        {'id': 'mode', 'text': 'note.txt is mode 600'},
    ],
    'intro': 'The file is /root/work/note.txt. Do not delete the text.',
    'success_msg': 'Only the owner can read and write the note.',
    'course_objectives': ['SEC-14.4'],
    'minutes': 10,
    'palette': ['ls -l /root/work/note.txt', 'chmod '],
    'hints': ['Look at the mode.', 'Owner read and write, nothing else.', 'Leave the file in place.'],
    'obj_hints': {
        'boot': ['A long listing shows the extra write bits.', 'The path is in the ticket.'],
        'mode': ['600 is owner read and write.', 'Group and others should have no permissions.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> A new file inherits the umask. '
                  'If the result is world-writable, you correct that file. Mode 600 is owner-only read and write.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Close the note so only the owner can read and write it.</p>',
        'stage3': '<p><strong>Stage 3 — ticket NOTE-600.</strong> The note must not be writable by every account.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-umask-21', 'sec-umask-21')], setup={'vm': _UMASK}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'mode', 'sh': "ls -l /root/work/note.txt | grep -q '^-rw------- '",
         'why': 'The note is still accessible to group or others.'},
    ],
    'solution': {'vm_commands': [
        'ls -l /root/work/note.txt',
        'chmod 600 /root/work/note.txt',
    ]},
})

_INTEG = _tok_setup('sec-int-22', r"""
mkdir -p /root/release /root/audit
echo "build TOKEN" > /root/release/app-TOKEN.bin
sha256sum /root/release/app-TOKEN.bin | awk '{print $1}' > /root/release/GOOD
echo "CODE TOKEN" > /root/TICKET
# tamper after the good hash was recorded
echo "tampered" >> /root/release/app-TOKEN.bin
echo "Compare the release file to GOOD and write MISMATCH into /root/audit/result.txt if it changed." >> /root/TICKET
""")

SEC_VM_INTEGRITY = _vm({
    'id': 'sec-vm-integrity',
    'title': 'Real Linux VM — Detect a changed release file',
    'blurb': 'A published fingerprint no longer matches the file. Record the mismatch.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and read the ticket'},
        {'id': 'result', 'text': '/root/audit/result.txt contains MISMATCH'},
    ],
    'intro': 'GOOD holds the fingerprint from before the file changed. The file name includes this session code.',
    'success_msg': 'You recorded that the release file no longer matches the published fingerprint.',
    'course_objectives': ['SEC-6.3'],
    'minutes': 20,
    'palette': ['cat /root/TICKET', 'sha256sum ', 'cat /root/release/GOOD'],
    'hints': [
        'The code in the ticket is part of the file name.',
        'Compare a fresh checksum to the saved fingerprint.',
        'Write MISMATCH when they differ. Do not overwrite GOOD.',
    ],
    'obj_hints': {
        'boot': ['Read the ticket and list the release directory.', 'GOOD is the published fingerprint.'],
        'result': ['The audit result should say MISMATCH.', 'Do not change the GOOD file to hide the difference.'],
    },
    'coaching': {
        'stage1': '<p><strong>Stage 1 — guided.</strong> A checksum of a file either matches a saved fingerprint or it does not. '
                  'The sample name app-DEMO00.bin is not this session. Compute the live file and compare.</p>',
        'stage2': '<p><strong>Stage 2 — assisted.</strong> Find the release file for this session. '
                  'If its checksum differs from GOOD, write MISMATCH into /root/audit/result.txt.</p>',
        'stage3': '<p><strong>Stage 3 — ticket HASH-drift.</strong> The release bytes changed after publication. Record the mismatch. Leave GOOD as the reference.</p>',
    },
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-int-22', 'sec-int-22')], setup={'vm': _INTEG}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'result', 'sh': "grep -q MISMATCH /root/audit/result.txt && test -f /root/release/GOOD",
         'why': 'MISMATCH was not recorded, or the reference fingerprint was removed.'},
    ],
    'solution': {'vm_commands': [
        "sed -n 's/^CODE //p' /root/TICKET",
        'sha256sum /root/release/app-$(sed -n \'s/^CODE //p\' /root/TICKET).bin',
        "printf '%s\\n' MISMATCH > /root/audit/result.txt",
    ]},
})

MORE_VM = [
    SEC_VM_BACKUP, SEC_VM_TIMELINE, SEC_VM_WIPE, SEC_VM_BASELINE, SEC_VM_SUDO, SEC_VM_BANNER,
    SEC_VM_SHADOW, SEC_VM_PATH, SEC_VM_LISTEN, SEC_VM_GROUP, SEC_VM_UMASK, SEC_VM_INTEGRITY,
]


def _A(lid, title, blurb, skill, prompts):
    return _activity(lid, title, blurb, skill, prompts)


MORE_ACT = [
    _A('sec-vuln', 'Vulnerability report — what to fix first',
       'Order the work by exposure, not by the scariness of the score alone.', 'SEC-21.3', [
        ('A high score on an isolated lab PC, and a medium score on the internet-facing VPN that attackers are using this week. What goes first?',
         ['The VPN, because it is exposed and being used', 'The lab PC, because the score is higher', 'Neither, until the annual window', 'Whichever is alphabetically first'],
         0, {1: 'The score is an input. Exposure and active use change the order.', 2: 'Waiting leaves the open door in place.', 3: 'The alphabet is not a risk method.'},
         'Patch the reachable flaw that is being used before a higher score on a machine nobody can reach.'),
        ('The scanner flags a library you do not run. What is the honest status?',
         ['Not applicable, after you confirm the code is absent', 'Emergency, because the score is high', 'Ignore every future scan', 'Disable the scanner'],
         0, {1: 'A high score on code you do not run is not your incident.', 2: 'Future scans still matter.', 3: 'The tool is how you see the next real one.'},
         'Confirm applicability. A score without the code path is not your priority.'),
        ('You patched the host. What closes the finding?',
         ['A rescan or a version check that shows the path is gone, plus a health check', 'The change window ended', 'The installer printed success and you closed the laptop', 'A reply that says done'],
         0, {1: 'The window ending is a clock, not a proof.', 2: 'Success text is not a retest.', 3: 'A one-word reply is not validation.'},
         'Prove the weakness is gone and the service still works.'),
        ('You cannot patch a device for 90 days. What is a real response?',
         ['Segment it and record a dated exception', 'Buy insurance and call that the fix', 'Silence, which counts as acceptance', 'Publish the exploit to motivate the vendor'],
         0, {1: 'Insurance may pay later. It does not close the port.', 2: 'Silence is not a decision.', 3: 'Publishing an exploit is not your mitigation.'},
         'Isolate what you cannot patch, and write the exception with an end date.'),
    ]),
    _A('sec-siem', 'SIEM triage',
       'Decide what the alert is, and what it is not.', 'SEC-22.4', [
        ('Failed logins on the VPN and a new mailbox forwarding rule appear in the same minutes for one user. What do you treat this as?',
         ['One incident worth containing, not two unrelated notes', 'Noise, because users mistype passwords', 'Proof the SIEM is broken', 'A reason to disable the VPN alert'],
         0, {1: 'A single failure can be a typo. The forwarding rule changes the story.', 2: 'Correlation is the point of the tool.', 3: 'Disabling the alert hides the next one.'},
         'Two facts about the same account in the same minutes are one investigation.'),
        ('The archive disk is full and new logs are dropping. What is the incident?',
         ['Collection has stopped, so you are blind', 'Nothing, because the old logs are still there', 'A reason to delete the SIEM', 'Proof no attacks are happening'],
         0, {1: 'Old logs do not show what happens next.', 2: 'You need the tool. You need it to have space.', 3: 'Silence from a full disk is not safety.'},
         'Alert on the archive. A full disk is a detection failure.'),
        ('An alert fires every Monday because a backup runs. What is tuning?',
         ['Adjust the rule so the backup is expected and a noon login by that account still fires', 'Delete the rule', 'Page the on-call every Monday forever', 'Turn off the backup'],
         0, {1: 'Deleting the rule also deletes the real signal.', 2: 'Paging a known job trains people to ignore pages.', 3: 'The backup is not the problem.'},
         'Teach the rule what normal looks like. Keep the surprising case.'),
        ('The dashboard is green and a short capture shows a beacon. What do you trust?',
         ['The capture for that question, and you keep it as evidence', 'The green dashboard, and you delete the capture', 'A screenshot of the dashboard as the only record', 'Nothing, so you capture the whole company for a month'],
         0, {1: 'A view can hide what it does not graph.', 2: 'A screenshot is not the events.', 3: 'Capture narrowly. A month of everything is a new data store.'},
         'A dashboard is a view. The packets you saved are the evidence for this question.'),
    ]),
    _A('sec-bec', 'Payment-change email',
       'A vendor bank account changes the day before a large payment.', 'SEC-10.2', [
        ('How do you confirm the new bank account?',
         ['Call the vendor on a number you already had, not the number in the email', 'Reply to the email and ask if it is real', 'Pay, because the invoice number is correct', 'Use the phone number in the signature of the email'],
         0, {1: 'The attacker reads that mailbox.', 2: 'A real invoice number can ride along with a fake account.', 3: 'The signature number belongs to the sender of this mail.'},
         'Out of band means a channel the message did not provide.'),
        ('SPF fails and DMARC is set to none. What happens to a forged message?',
         ['Receivers may still deliver it, because none does not ask them to reject', 'Every receiver drops it automatically', 'The message is encrypted so it is fine', 'DMARC none means the domain is safe'],
         0, {1: 'None means report, not reject.', 2: 'SPF is not encryption.', 3: 'None is the monitoring setting, not protection.'},
         'Until you enforce DMARC, a failed check can still land in the inbox.'),
        ('The mailbox that sends your invoices starts a burst of lures. What helps?',
         ['Outbound filtering and disabling that account', 'Inbound filtering only', 'A new logo on the email', 'Turning off SPF'],
         0, {1: 'Inbound filters do not see mail that already left.', 2: 'A logo is not a control.', 3: 'SPF is how others know your real servers.'},
         'Watch mail leaving, not only mail arriving.'),
        ('A look-alike domain is one character off. What do you tell the user?',
         ['Read the name character by character and use a bookmark', 'If the logo matches, it is us', 'The lock icon proves the brand', 'Close enough is the same site'],
         0, {1: 'Logos are cheap to copy.', 2: 'A lock means a certificate, not your company.', 3: 'One character is a different place.'},
         'The address is the check. The paint is not.'),
    ]),
    _A('sec-backup-dec', 'Backup decisions',
       'Choose a copy you could actually restore.', 'SEC-18.3', [
        ('Nightly backups sit on a disk in the same rack, unencrypted. What is missing?',
         ['An offsite encrypted copy, with the key stored apart from that disk', 'A second copy on the same disk', 'A longer hostname', 'RAID on that disk, which replaces backup'],
         0, {1: 'The same disk dies in the same fire.', 2: 'A name does not restore data.', 3: 'RAID is not a backup.'},
         'Somewhere else, encrypted, and the key survives too.'),
        ('Replication to a second array is running. Ransomware encrypts the files. What else do you need?',
         ['A copy the same account cannot keep overwriting', 'Nothing. Replication is a backup', 'A snapshot on the same array only', 'To turn replication off forever'],
         0, {1: 'Replication copies the damage.', 2: 'A snapshot beside the original shares the failure.', 3: 'Replication is useful. It is not the only copy.'},
         'You need a copy that is not continuously writable by the attacker.'),
        ('The business can lose one hour and must return in four. Backups are nightly. What is true?',
         ['The design does not meet the recovery point. Change the copies or the promise', 'Nightly copies meet a one-hour promise', 'The numbers are optional', 'A green backup job proves the timing'],
         0, {1: 'A daily copy can lose a day of work.', 2: 'The promise is a requirement.', 3: 'A green job means the copy was written, not that the timing matches.'},
         'Frequency has to match how much work you can lose.'),
        ('What proves a backup?',
         ['A restore of a real file by someone other than the only expert', 'A green check on the job', 'The vendor dashboard', 'The fact that the job ran last night'],
         0, {1: 'The job succeeding is not a restore.', 2: 'A dashboard is a claim.', 3: 'A run is not a proof you can read the data.'},
         'Restore it. Have a second person do it.'),
    ]),
    _A('sec-classify', 'Data labels',
       'Name the data and the state before you pick a tool.', 'SEC-17.2', [
        ('A salary file is mailed to a personal address. The site is up and the file was not edited. What failed?',
         ['Confidentiality, in transit and then at rest outside', 'Integrity only', 'Availability only', 'Nothing, because the password was strong'],
         0, {1: 'The contents were not the problem. Who received them is.', 2: 'The service stayed up.', 3: 'A password does not unsend a file.'},
         'Name the promise and the state. The file left.'),
        ('Full-disk encryption is on, and the user is logged in and copies a report into chat. What did disk encryption not cover?',
         ['Data in use, and the copy in transit after that', 'The powered-off disk', 'The need for a password at boot', 'Nothing. Disk encryption covers chat'],
         0, {1: 'The powered-off disk is what full-disk encryption is for.', 2: 'Boot protection can still be working.', 3: 'A logged-on session can read the files.'},
         'Rest, transit, and use are three states.'),
        ('Support staff should see only the last four digits. The export still has the full number. What is true?',
         ['The screen mask is not the control until the export is masked too', 'The user interface is enough', 'Masking deletes the stored number', 'Tokenization shows the full number on the receipt'],
         0, {1: 'A mask the export ignores is theater.', 2: 'Masking hides display. It does not always delete the store.', 3: 'A token stands in for the number. The receipt should not show all of it.'},
         'Apply the reduction everywhere the value appears.'),
        ('Who may decide that marketing can have the patient list?',
         ['The data owner, not the server administrator by default', 'Whoever can open the file', 'The cloud vendor', 'The person who asked first'],
         0, {1: 'Access is not ownership.', 2: 'The vendor processes. They do not own the decision.', 3: 'Asking is not approval.'},
         'The owner decides. The custodian carries it out.'),
    ]),
    _A('sec-zt-choice', 'Zero trust decisions',
       'Location is not a yes.', 'SEC-3.4', [
        ('A user on the office wireless wants payroll. The rule also requires a managed device. The device is personal. What happens?',
         ['Deny or step up. The network location is not enough', 'Allow, because they are in the building', 'Allow, because the password was correct this morning', 'Disable the wireless'],
         0, {1: 'Inside is not a trust zone by itself.', 2: 'This morning is not this request.', 3: 'The wireless can stay. This request should not.'},
         'Policy checks identity and context, not only the building.'),
        ('The enforcement point cannot reach the decision service. What should it do for a new payroll connection?',
         ['Fail closed and block', 'Fail open so work continues with no decision', 'Allow for an hour and log nothing', 'Ask the user to choose'],
         0, {1: 'Fail open lets traffic through with no decision.', 2: 'An unlogged allow is worse.', 3: 'The user does not make the policy decision.'},
         'If you cannot decide, do not open a sensitive path.'),
        ('An analyst needs logs for four hours. What matches least privilege here?',
         ['The log role until a time, not standing domain admin', 'Domain admin, because it is faster', 'A shared admin password', 'No account, and they use someone else session'],
         0, {1: 'Standing admin outlives the task.', 2: 'A shared password hides who acted.', 3: 'Borrowing a session destroys accounting.'},
         'The smallest allow for the shortest time.'),
        ('A diagram says zero trust and shows only a firewall. What do you ask?',
         ['Where the decision is made, and what happens if that service is down', 'Which logo is newer', 'Nothing. A firewall is the whole model', 'Whether the firewall is red'],
         0, {1: 'A logo is not a decision point.', 2: 'A firewall can enforce. It is not the whole model.', 3: 'Color is not architecture.'},
         'Point at the decision and the enforcement.'),
    ]),
    _A('sec-privacy', 'Privacy request',
       'A person asks for their data and for deletion.', 'SEC-28.4', [
        ('What do you do first?',
         ['Verify who they are, then find the copies, including vendors', 'Email them a raw database dump', 'Delete everything including a legal hold', 'Ignore it because IT is busy'],
         0, {1: 'A dump is a new disclosure.', 2: 'A hold can pause deletion.', 3: 'The request is a duty, not a favor.'},
         'Prove identity, find every copy, follow the rule that applies.'),
        ('Backups still contain the person after the app delete. What is true?',
         ['Retention includes the backups, or you have not deleted the data', 'The app delete finished the job', 'Backups are exempt from every rule', 'The vendor copy does not count'],
         0, {1: 'A leftover backup is still the data.', 2: 'Backups are a copy.', 3: 'A processor copy is still your problem to track.'},
         'Copies count. Name them in the inventory.'),
        ('Who decides why the data was collected?',
         ['The controller', 'The processor who stores it', 'The person who runs the server, automatically', 'Anyone with a login'],
         0, {1: 'A processor handles data for the controller.', 2: 'Operating a server is custody, not the decision.', 3: 'A login is not ownership.'},
         'The controller decides the purpose. The processor handles it.'),
        ('A legal hold is in place and the person asks for deletion. What do you do?',
         ['Follow counsel. A hold can pause the shredder', 'Delete immediately to be helpful', 'Delete and tell nobody', 'Post the request on a public page'],
         0, {1: 'Helpful deletion can destroy evidence.', 2: 'Silent deletion is worse.', 3: 'The request is not public content.'},
         'Privacy rights and legal holds are both real. Counsel sorts the conflict.'),
    ]),
    _A('sec-passwords', 'Password and factor choices',
       'Pick a factor that is actually a second kind.', 'SEC-24.5', [
        ('Which pair is multi-factor?',
         ['A passphrase and a hardware security key', 'Two passwords', 'A password and a hint that is the same password', 'A longer password only'],
         0, {1: 'Two secrets are one kind.', 2: 'A hint is not a second factor.', 3: 'Length is not a second kind.'},
         'Different kinds: know, have, are, or a place you can defend.'),
        ('A policy forces a change every 30 days and people use Spring1 then Spring2. What is the better rule?',
         ['Long unique passphrases, a breach check, and a change when it is exposed', 'Shorter passwords changed weekly', 'One shared password that is complex', 'Write the password on a ticket so nobody forgets'],
         0, {1: 'Faster rotation makes the pattern worse.', 2: 'Shared secrets are one leak for everyone.', 3: 'Tickets are widely readable.'},
         'Length and uniqueness beat a rotation that creates a pattern.'),
        ('An admin approves a push prompt on a fake site. What would have resisted that?',
         ['A security key that checks the site name', 'SMS, which cannot be redirected', 'A shorter session only', 'A password written on paper'],
         0, {1: 'SMS can be stolen in the moment or by a SIM swap.', 2: 'A short session helps after the fact. It does not bind the site.', 3: 'Paper is something you know, written down.'},
         'Phishing-resistant keys refuse the wrong site name.'),
        ('Where should a privileged password live?',
         ['In a vault that checks it out and rotates it, not in the ticket', 'In the ticket for the next shift', 'In a chat channel', 'In a spreadsheet on a share'],
         0, {1: 'The ticket is readable by many people.', 2: 'Chat history keeps secrets.', 3: 'A share is a shared password.'},
         'Checkout and rotate. Do not paste the secret.'),
    ]),
    _A('sec-ports', 'Ports and protocols',
       'Allow the service you mean, and know the number.', 'SEC-23.2', [
        ('A vendor wants FTP so a transfer will work. What do you require instead?',
         ['SFTP or HTTPS, and only that port from their addresses', 'All ports, because one transfer failed', 'Telnet, because it is simple', 'FTP with the password in the ticket'],
         0, {1: 'Opening everything hides the next mistake.', 2: 'Telnet is clear text.', 3: 'The ticket must not hold the password.'},
         'Pick an encrypted protocol and one port.'),
        ('Which line is the DNS path you expect for a normal lookup?',
         ['UDP 53 to the resolver you run', 'TCP 23 to the resolver', 'UDP 161 to the resolver', 'TCP 3389 to the resolver'],
         0, {1: '23 is Telnet.', 2: '161 is SNMP.', 3: '3389 is remote desktop.'},
         'Name service lookups use DNS, typically UDP 53.'),
        ('A firewall allows any source to any port above the deny rules. What is the effect?',
         ['The later denies never run for that traffic', 'The denies still win because they are more specific in spirit', 'Nothing. Order does not matter', 'The firewall ignores the first match'],
         0, {1: 'Spirit is not how the list is evaluated.', 2: 'Order is the policy.', 3: 'First match wins on a typical firewall.'},
         'Read the list from the top. An any-any allow makes the rest decoration.'),
        ('Remote administration of a router should be:',
         ['Encrypted and limited to a management network', 'Telnet from the internet', 'A default password, because it is documented', 'Open to every staff laptop on every network'],
         0, {1: 'Telnet is clear text.', 2: 'Documented defaults are still defaults.', 3: 'Every laptop is a large surface.'},
         'Management is a small, encrypted path.'),
    ]),
    _A('sec-fp', 'False positive or false negative',
       'Tune without going deaf.', 'SEC-21.3', [
        ('The scanner flags a patched library because a banner string is old. What do you do?',
         ['Confirm the patch, then tune that check', 'Declare an emergency and rebuild the data center', 'Turn the scanner off', 'Ignore all future highs'],
         0, {1: 'The score is not the confirmation.', 2: 'You still need the scanner.', 3: 'One bad banner is not a reason to ignore real highs.'},
         'Confirm, then tune. Do not go deaf.'),
        ('A control blocks a real business file every Monday and would also block a known malware sample. How do you tune?',
         ['Adjust it so the business file passes and the sample still blocks, and record the change', 'Delete the rule', 'Click allow forever for the whole company', 'Disable the control on Mondays'],
         0, {1: 'Deleting the rule drops the real detection.', 2: 'A permanent allow for everyone is the hole.', 3: 'Monday is when you need the control if that is when the file moves.'},
         'Keep the true case working. Write down the exception.'),
        ('Which miss is worse if you must choose what to fear?',
         ['A false negative on an internet-facing login', 'A false positive that you then confirm', 'A report that is too long', 'A scanner that asks for credentials'],
         0, {1: 'A false positive you confirm costs time. A miss on the front door costs the account.', 2: 'Length is annoying.', 3: 'Credentials are how an authenticated scan sees more.'},
         'The quiet miss on an exposed system is the dangerous one.'),
        ('Someone wants to delete a noisy rule the night of an incident. What do you require?',
         ['A ticket and a test that the real pattern still fires', 'A side chat and no record', 'Deletion first so the queue is quiet', 'Turning off logging'],
         0, {1: 'A side chat becomes the permanent state.', 2: 'Quiet is not the goal during an incident.', 3: 'Logs are how you know.'},
         'Weaken a rule only with a record and a test.'),
    ]),
    _A('sec-ir-choice', 'Incident choices',
       'Contain, keep evidence, then recover clean.', 'SEC-25.4', [
        ('Files are encrypting and the laptop is on the wireless. What is first?',
         ['Get it off the network and keep the disk', 'Reimage immediately', 'Pay the note from a local card', 'Reboot to see if it stops'],
         0, {1: 'Reimaging first destroys the story and may miss other hosts.', 2: 'Paying is not the help-desk action.', 3: 'A reboot can destroy volatile detail and does not stop a share copy.'},
         'Stop the spread. Do not wipe yet.'),
        ('Who may disconnect a production host at 2 a.m.?',
         ['The person the plan names, who then writes the time', 'Nobody, until a morning committee', 'Whoever is angriest', 'Only the vendor, by contract, with no local action'],
         0, {1: 'Waiting for morning lets the spread continue.', 2: 'Anger is not authority.', 3: 'The plan should not require a vendor to unplug your host.'},
         'Pre-agreed authority, then a note.'),
        ('You restore a snapshot taken after the backdoor was installed. What did you do?',
         ['Brought the cause back', 'Finished eradication', 'Met the recovery point', 'Completed lessons learned'],
         0, {1: 'The cause is still there.', 2: 'The point in time includes the attacker.', 3: 'A lesson is a later change, not this restore.'},
         'Restore from before the cause, then watch.'),
        ('What belongs in the status note?',
         ['What you know, what you did, and when the next update is', 'A guessed country and a villain name', 'Nothing until the incident is over', 'The list of employee passwords you reset'],
         0, {1: 'Speculation becomes the story people repeat.', 2: 'Silence invites a second click.', 3: 'Passwords do not go in the note.'},
         'Facts and the next update. No secrets and no guesses.'),
    ]),
    _A('sec-audit', 'Audit evidence',
       'A claim needs a sample.', 'SEC-28.5', [
        ('Managers attest that every laptop is encrypted. A sample finds three that are not. What is the finding?',
         ['The attestation was wrong and the process has a gap', 'Nothing, because most laptops passed', 'The sample method is the problem, so ignore the three', 'Encryption is optional'],
         0, {1: 'Most is not the claim they signed.', 2: 'The three are the point of the sample.', 3: 'The standard is not optional.'},
         'A signature without a matching sample is a finding.'),
        ('An external report disagrees with your wording and the shared admin password is real. What closes it?',
         ['A dated change that removes the shared password', 'A rebuttal of the sentence and no change', 'Hiding the report', 'Renaming the account'],
         0, {1: 'Wording is not the risk.', 2: 'Hiding the report makes the next audit worse.', 3: 'A new name on the same shared secret changes nothing.'},
         'Track the finding to a real change.'),
        ('A penetration test starts scanning the plant, which the rules put off limits. What do you do?',
         ['Stop the test', 'Let it continue because they are skilled', 'Call it passive reconnaissance', 'Ask them to scan harder'],
         0, {1: 'Skill is not scope.', 2: 'A scan touches systems. It is not passive.', 3: 'More scope is the opposite of the rules.'},
         'Active work outside the rules stops.'),
        ('A self-assessment cannot say fail. What is it?',
         ['Not an assessment', 'A strong audit', 'Better than an external exam', 'Proof the controls work'],
         0, {1: 'An assessment that cannot fail cannot find a gap.', 2: 'External exams still have value. They are not the reason to hide.', 3: 'Proof would include a fail when one exists.'},
         'Allow a real fail, then write the fix.'),
    ]),
]
