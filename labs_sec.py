"""Cybersecurity labs for course SEC.

Linux stations are real v86 VMs graded on the final system state. Windows, phishing,
certificate, MFA, ACL, and GPG stations are graded activities in the same lab runner.
Stage 1 may show commands. Stages 2 and 3, and the hint text, do not.
"""
from labs_vm import IMAGE, _m, _prelude

REVIEW = 'Pending SME review'


def _coach(s1, s2, s3):
    return {'stage1': s1, 'stage2': s2, 'stage3': s3}


def _vm(lab):
    lab.setdefault('kind', 'vm')
    lab.setdefault('initial_state', {})
    lab.setdefault('fallback', ['linux-shell'])
    lab.setdefault('review', REVIEW)
    return lab


def _act(lab):
    lab.setdefault('kind', 'activity')
    lab.setdefault('initial_state', {'kind': 'activity'})
    lab.setdefault('review', REVIEW)
    return lab


def _choice(sid, objective, prompt, options, answer, explain, right):
    return {
        'id': sid, 'type': 'choice', 'objective': objective, 'prompt': prompt,
        'options': options, 'answer': answer,
        'explain': {str(k): v for k, v in explain.items()},
        'right': right,
    }


# ---------------------------------------------------------------- VM: iptables
_FW = _prelude('sec-fw-01') + r"""
mkdir -p /etc/iptables /root
iptables -F
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
cat > /root/TICKET <<'EOF'
FW-19. Default-deny this host.
Allow SSH only from 10.9.1.40.
Allow TCP 8443 from anywhere.
Keep loopback and established flows working.
Save the rules to /etc/iptables/rules-save.
EOF
"""
SEC_VM_IPTABLES = _vm({
    'id': 'sec-vm-iptables',
    'title': 'Real Linux VM — Host firewall (iptables)',
    'blurb': 'A real Linux host starts wide open. Build a default-deny INPUT policy with the allows the ticket names.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM and read /root/TICKET'},
        {'id': 'loop', 'text': 'Accept traffic on the loopback interface'},
        {'id': 'state', 'text': 'Accept established and related flows'},
        {'id': 'ssh', 'text': 'Allow TCP 22 only from 10.9.1.40'},
        {'id': 'app', 'text': 'Allow TCP 8443'},
        {'id': 'policy', 'text': 'Set the INPUT policy to DROP'},
        {'id': 'saved', 'text': 'Save the ruleset to /etc/iptables/rules-save'},
    ],
    'intro': 'Ticket FW-19 is on the VM in /root/TICKET. The tool on this image is iptables (the same idea as ufw on Ubuntu). Grade checks the live rules.',
    'success_msg': 'The host is default-deny, with loopback, established flows, a narrow SSH allow, and TCP 8443.',
    'course_objectives': ['SEC-6.1'],
    'minutes': 30,
    'palette': ['iptables -S', 'iptables -L INPUT -n -v', 'iptables -A INPUT ', 'iptables -P INPUT ', 'iptables-save'],
    'hints': [
        'Read the ticket file before you change a policy.',
        'Loopback and already-open conversations need a path or you will lock yourself out of local tools.',
        'Name the admin address on the SSH allow. A wide SSH allow is not the ticket.',
    ],
    'obj_hints': {
        'boot': ['The scenario is a file in the home directory.', 'Open the ticket file and read every allow before you append rules.'],
        'loop': ['Local services talk to themselves on a special interface.', 'Allow that interface before you change the default policy.'],
        'state': ['Return traffic belongs to a conversation you already accepted.', 'There is a match module for connection state. Allow established and related.'],
        'ssh': ['The admin workstation is a single address, not the whole internet.', 'Limit the SSH allow by source address and destination port.'],
        'app': ['The app port is allowed from anywhere. SSH is not.', 'Add a separate allow for that TCP port.'],
        'policy': ['The policy is what happens when no rule matches.', 'Change INPUT only after the allows exist.'],
        'saved': ['A reboot forgets rules that were not saved.', 'Write the current ruleset into the path the ticket names.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>iptables -S</code> prints the current rules. '
        '<code>-A INPUT</code> appends a rule. <code>-i lo</code> matches loopback. '
        '<code>-m conntrack --ctstate ESTABLISHED,RELATED</code> matches replies. '
        '<code>-p tcp -s ADDRESS --dport 22</code> names one peer and one port. '
        '<code>-j ACCEPT</code> allows the match. <code>-P INPUT DROP</code> sets the default. '
        '<code>iptables-save</code> prints a restorable ruleset; redirect it to <code>/etc/iptables/rules-save</code>.</p>',
        '<p><strong>Stage 2 — assisted.</strong> The live host still uses an accept policy. '
        'Discover the admin address, the SSH port, and the application port from the ticket file on the system. '
        'Build allows for loopback, existing conversations, that one admin host, and the application port. '
        'Change the default only after those allows exist, then store the ruleset where the ticket says.</p>',
        '<p><strong>Stage 3 — ticket FW-19.</strong> The night operator left this host accepting every inbound connection. '
        'Make it default-deny. Keep local services and replies working. '
        'SSH may come only from the admin host named in the ticket. '
        'The application port named in the ticket stays reachable. Persist the ruleset.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-fw-01', 'sec-fw-01')], setup={'vm': _FW}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'loop', 'sh': "iptables -S INPUT | grep -q -- '-i lo -j ACCEPT'", 'why': 'Loopback is not accepted yet.'},
        {'id': 'state', 'sh': "iptables -S INPUT | grep -q ESTABLISHED", 'why': 'Established flows are not accepted yet.'},
        {'id': 'ssh', 'sh': "iptables -S INPUT | grep -q -- '-s 10.9.1.40' && iptables -S INPUT | grep -- '-s 10.9.1.40' | grep -q 'dport 22'",
         'why': 'SSH is not limited to 10.9.1.40.'},
        {'id': 'app', 'sh': "iptables -S INPUT | grep -q 'dport 8443'", 'why': 'TCP 8443 is not allowed.'},
        {'id': 'policy', 'sh': "iptables -S | grep -q '^-P INPUT DROP'", 'why': 'INPUT policy is not DROP.'},
        {'id': 'saved', 'sh': "grep -q '^:INPUT DROP' /etc/iptables/rules-save && grep -q '10.9.1.40' /etc/iptables/rules-save && grep -q 8443 /etc/iptables/rules-save",
         'why': 'The saved ruleset is missing or incomplete.'},
    ],
    'solution': {'vm_commands': [
        'cat /root/TICKET',
        'iptables -A INPUT -i lo -j ACCEPT',
        'iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT',
        'iptables -A INPUT -p tcp -s 10.9.1.40 --dport 22 -j ACCEPT',
        'iptables -A INPUT -p tcp --dport 8443 -j ACCEPT',
        'iptables -P INPUT DROP',
        'iptables-save > /etc/iptables/rules-save',
        'iptables -S',
    ]},
})


# ---------------------------------------------------------------- VM: permissions
_PERM = _prelude('sec-files-02') + r"""
groupadd payroll 2>/dev/null || addgroup payroll
mkdir -p /srv/secrets
printf 'emp,ssn\n' > /srv/secrets/payroll.csv
chmod 666 /srv/secrets/payroll.csv
chown root:root /srv/secrets/payroll.csv
"""
SEC_VM_PERMS = _vm({
    'id': 'sec-vm-perms',
    'title': 'Real Linux VM — Secret file permissions',
    'blurb': 'A payroll file is writable by every account. Leave it readable by the payroll group and nobody else.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and inspect the payroll file mode'},
        {'id': 'group', 'text': 'The payroll group exists and owns the file group'},
        {'id': 'mode', 'text': 'payroll.csv is mode 640 (owner read/write, group read, no access for others)'},
    ],
    'intro': 'The file /srv/secrets/payroll.csv is world-writable. The payroll group already exists or can be created. Do not delete the file.',
    'success_msg': 'The payroll file is group-readable and closed to everyone else.',
    'course_objectives': ['SEC-7.1'],
    'minutes': 20,
    'palette': ['ls -l ', 'chgrp ', 'chmod ', 'id '],
    'hints': ['List the file with a long listing before you change it.', 'The group name is the department that may read payroll.', 'Others should have no permissions at all.'],
    'obj_hints': {
        'boot': ['Look at the mode bits, not only the filename.', 'A long listing shows owner, group, and the other triple.'],
        'group': ['The department group should already be addable if it is missing.', 'The file group should be that department, not root.'],
        'mode': ['Owner keeps read and write. The group keeps read. Others keep nothing.', 'Express that as four digits if you use numeric mode.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>ls -l</code> shows type and three triples. '
        '<code>chgrp GROUP FILE</code> changes the group. '
        'Numeric mode: owner rw is 6, group r is 4, other none is 0, so 640. '
        '<code>chmod 640 FILE</code> applies it. This walkthrough uses a sample path, not the live payroll path.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Find the world-writable secret under /srv. '
        'The department group name is on the system. Give that group ownership of the group field and close the file to everyone else. '
        'Owner must still be able to edit it. Do not remove the data.</p>',
        '<p><strong>Stage 3 — ticket SEC-640.</strong> Payroll export is exposed to every local account. '
        'Correct the group and the mode. Confirm with a long listing. Leave the contents in place.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-files-02', 'sec-files-02')], setup={'vm': _PERM}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'group', 'sh': "grep -q '^payroll:' /etc/group && ls -l /srv/secrets/payroll.csv | awk '{print $4}' | grep -qx payroll",
         'why': 'The payroll group does not own the file group yet.'},
        {'id': 'mode', 'sh': "ls -l /srv/secrets/payroll.csv | grep -q '^-rw-r----- '",
         'why': 'The mode is not owner read/write, group read, nothing for others.'},
    ],
    'solution': {'vm_commands': [
        'ls -l /srv/secrets/payroll.csv',
        'chgrp payroll /srv/secrets/payroll.csv',
        'chmod 640 /srv/secrets/payroll.csv',
        'ls -l /srv/secrets/payroll.csv',
    ]},
})


# ---------------------------------------------------------------- VM: SUID
_SUID = _prelude('sec-suid-03') + r"""
mkdir -p /usr/local/bin /root/audit
if [ -x /bin/busybox ]; then cp /bin/busybox /usr/local/bin/helper; else cp /bin/sh /usr/local/bin/helper; fi
chmod 4755 /usr/local/bin/helper
if [ -x /bin/busybox ]; then cp /bin/busybox /usr/local/bin/oktool; else cp /bin/sh /usr/local/bin/oktool; fi
chmod 755 /usr/local/bin/oktool
"""
SEC_VM_SUID = _vm({
    'id': 'sec-vm-suid',
    'title': 'Real Linux VM — Unexpected SUID',
    'blurb': 'Something under /usr/local is setuid. Record it, then remove the special bit from the surprise.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM'},
        {'id': 'found', 'text': 'Record the unexpected setuid path in /root/audit/suid.txt'},
        {'id': 'cleared', 'text': 'The helper program is no longer setuid'},
    ],
    'intro': 'A baseline says the only setuid tools should be the ones the OS shipped. Look under /usr/local. Record the path before you change the bit.',
    'success_msg': 'The surprise setuid bit is gone and the path is in the audit note.',
    'course_objectives': ['SEC-7.1', 'SEC-7.4'],
    'minutes': 20,
    'palette': ['find /usr/local ', 'ls -l ', 'chmod u-s '],
    'hints': ['Setuid shows up as an s in the owner execute column, or as a special find test.', 'Write the path down before you change the mode.', 'Only the unexpected program should lose the bit.'],
    'obj_hints': {
        'boot': ['Start the VM and look under the local program directory.', 'Do not change modes until you have a note.'],
        'found': ['A find test can list files with the setuid bit.', 'Save that list in the audit file the ticket names.'],
        'cleared': ['Removing the special bit is not the same as deleting the program.', 'The program should remain, without owner-execute as setuid.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>find /usr/local -perm -4000 -type f</code> lists setuid files. '
        'Redirect that list into a note. <code>chmod u-s PATH</code> clears the setuid bit and leaves the file. '
        'Practice the idea on a scratch copy before you touch the live helper.</p>',
        '<p><strong>Stage 2 — assisted.</strong> The image has both an ordinary local tool and one that borrows owner power. '
        'Discover which path is setuid. Save that path in /root/audit/suid.txt while it is still setuid. '
        'Then clear only that special bit.</p>',
        '<p><strong>Stage 3 — ticket SEC-SUID.</strong> A vendor helper was left able to run as its owner. '
        'Record the path, then remove the special bit. Leave the program installed.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-suid-03', 'sec-suid-03')], setup={'vm': _SUID}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'found', 'sh': "grep -q '/usr/local/bin/helper' /root/audit/suid.txt",
         'why': 'The audit note does not name the setuid helper.'},
        {'id': 'cleared', 'sh': "! find /usr/local/bin/helper -perm -4000 | grep -q .",
         'why': 'The helper is still setuid.'},
    ],
    'solution': {'vm_commands': [
        'find /usr/local -perm -4000 -type f > /root/audit/suid.txt',
        'chmod u-s /usr/local/bin/helper',
        'find /usr/local -perm -4000 -type f',
    ]},
})


# ---------------------------------------------------------------- VM: users / sudo
_USERS = _prelude('sec-acct-04') + r"""
useradd -m -s /bin/sh intern
echo 'intern:Temp#2026' | chpasswd
printf 'intern ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/99-intern
chmod 440 /etc/sudoers.d/99-intern
"""
SEC_VM_USERS = _vm({
    'id': 'sec-vm-users',
    'title': 'Real Linux VM — Lock a leaver and drop sudo',
    'blurb': 'The intern left. Lock the account, keep the home directory, and remove the blanket sudo rule.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot and identify the intern account'},
        {'id': 'locked', 'text': 'The intern password is locked and the account still exists'},
        {'id': 'sudo', 'text': 'The blanket sudo drop-in is gone and sudoers still parses'},
    ],
    'intro': 'HR says intern left today. Do not delete the home directory. The sudo exception is a file under /etc/sudoers.d.',
    'success_msg': 'The leaver cannot log in, the files remain, and the blanket sudo rule is gone.',
    'course_objectives': ['SEC-5.2', 'SEC-7.2'],
    'minutes': 25,
    'palette': ['id ', 'chage -l ', 'ls /etc/sudoers.d', 'usermod ', 'rm ', 'visudo -c'],
    'hints': ['Locking a password is not the same as deleting the user.', 'Look for a drop-in that grants every command.', 'Check sudoers syntax after you remove a file.'],
    'obj_hints': {
        'boot': ['The account name is the role in the ticket, not root.', 'Confirm the account exists before you change it.'],
        'locked': ['A lock keeps the account and the home directory.', 'The shadow entry should show a locked password.'],
        'sudo': ['Blanket rights were added as a drop-in file.', 'Remove that file and confirm the sudoers parser still accepts the rest.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>id USER</code> shows an account. '
        '<code>chage -l USER</code> shows password aging when the command is installed. '
        '<code>usermod -L USER</code> locks the password (shadow packages also accept <code>passwd -l</code>). '
        '<code>userdel</code> would remove the account; do not use it when files must remain. '
        'A file in <code>/etc/sudoers.d</code> is an extra sudo rule. <code>visudo -c</code> checks syntax.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Find the leaver account and the drop-in that lets them run everything without a password. '
        'Lock the login. Keep the home directory. Remove only the blanket rule. Prove sudoers still parses.</p>',
        '<p><strong>Stage 3 — ticket HR-LOCK.</strong> The intern left at noon. '
        'Disable their login without destroying files, and remove the temporary all-commands sudo grant.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-acct-04', 'sec-acct-04')], setup={'vm': _USERS}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'locked', 'sh': "id intern >/dev/null && grep -q '^intern:!' /etc/shadow && [ -d /home/intern ]",
         'why': 'intern is not locked, or the account or home directory is gone.'},
        {'id': 'sudo', 'sh': "! [ -e /etc/sudoers.d/99-intern ] && visudo -c",
         'why': 'The blanket sudo rule is still present, or sudoers does not parse.'},
    ],
    'solution': {'vm_commands': [
        'id intern',
        'ls /etc/sudoers.d',
        'usermod -L intern',
        'rm /etc/sudoers.d/99-intern',
        'visudo -c',
    ]},
})


# ---------------------------------------------------------------- VM: SSH
_SSH = _prelude('sec-ssh-05') + r"""
[ -f /etc/ssh/ssh_host_ed25519_key ] || ssh-keygen -q -t ed25519 -N '' -f /etc/ssh/ssh_host_ed25519_key
useradd -m -s /bin/sh ops
echo 'ops:Ops#Temp1' | chpasswd
grep -q '^PasswordAuthentication ' /etc/ssh/sshd_config || echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
grep -q '^PermitRootLogin ' /etc/ssh/sshd_config || echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
"""
SEC_VM_SSH = _vm({
    'id': 'sec-vm-ssh',
    'title': 'Real Linux VM — SSH key, then close passwords',
    'blurb': 'Install an ed25519 key for ops, then turn off password login and direct root login. Do not close passwords first.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM'},
        {'id': 'key', 'text': 'ops has an ed25519 public key in authorized_keys'},
        {'id': 'mode', 'text': '.ssh is 700 and authorized_keys is 600, owned by ops'},
        {'id': 'config', 'text': 'PasswordAuthentication no and PermitRootLogin no, and sshd -t succeeds'},
    ],
    'intro': 'ops can still sign in with a password, and root login is allowed. Put a key in place and prove the config is valid before you rely on it.',
    'success_msg': 'Key login is installed with safe modes, and password and root login are closed in a config sshd accepts.',
    'course_objectives': ['SEC-5.4', 'SEC-7.2'],
    'minutes': 30,
    'palette': ['ssh-keygen -t ed25519 ', 'ls -ld ', 'chmod ', 'chown ', 'sshd -t'],
    'hints': ['Create the key for the ops account, not only for root.', 'Directory and file modes matter or sshd will ignore the key.', 'Ask sshd to test the config before you walk away.'],
    'obj_hints': {
        'boot': ['The account that needs the key is a normal user.', 'Confirm that user exists.'],
        'key': ['The public half ends up in that user authorized keys file.', 'The algorithm for this ticket is ed25519.'],
        'mode': ['The directory should be private to the user. The key file should not be group-readable.', 'Ownership should be the user, not root, if the user must use it.'],
        'config': ['Change the two yes values in the daemon config.', 'Run the config test. Do not leave a typo that prevents the daemon from starting.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>ssh-keygen -t ed25519 -N \'\' -f PATH</code> makes a key with an empty passphrase for this lab. '
        'The <code>.ssh</code> directory needs mode 700 and <code>authorized_keys</code> mode 600. '
        '<code>chown -R USER USER</code> gives the files to that user. '
        'In <code>sshd_config</code>, set password authentication and root login to no. <code>sshd -t</code> checks syntax.</p>',
        '<p><strong>Stage 2 — assisted.</strong> The ops account exists and can still use a password. '
        'Create a key pair for that account, install the public half so the daemon will accept it, and fix ownership and modes. '
        'Only then close password login and direct root login. Prove the daemon config still parses.</p>',
        '<p><strong>Stage 3 — ticket SSH-KEY.</strong> Password login and root login are still open. '
        'Move ops to key login with safe file modes, then close both password login and root login without breaking the config.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-ssh-05', 'sec-ssh-05')], setup={'vm': _SSH}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'key', 'sh': "grep -q '^ssh-ed25519 ' /home/ops/.ssh/authorized_keys",
         'why': 'authorized_keys does not contain an ed25519 key.'},
        {'id': 'mode', 'sh': "ls -ld /home/ops/.ssh | grep -q '^drwx------ .* ops ' && ls -l /home/ops/.ssh/authorized_keys | grep -q '^-rw------- .* ops '",
         'why': '.ssh or authorized_keys has the wrong mode or owner.'},
        {'id': 'config', 'sh': "grep -q '^PasswordAuthentication no' /etc/ssh/sshd_config && grep -q '^PermitRootLogin no' /etc/ssh/sshd_config && sshd -t",
         'why': 'Password or root login is still allowed, or sshd -t fails.'},
    ],
    'solution': {'vm_commands': [
        'mkdir -p /home/ops/.ssh',
        "ssh-keygen -t ed25519 -N '' -f /home/ops/.ssh/id_ed25519",
        'cat /home/ops/.ssh/id_ed25519.pub > /home/ops/.ssh/authorized_keys',
        'chmod 700 /home/ops/.ssh',
        'chmod 600 /home/ops/.ssh/authorized_keys',
        'chown -R ops:ops /home/ops/.ssh',
        "sed -i 's/^PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config",
        "sed -i 's/^PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config",
        'sshd -t',
    ]},
})


# ---------------------------------------------------------------- VM: auth log
_AUTH = _prelude('sec-log-06') + r"""
mkdir -p /var/log /root/ir
cat > /var/log/auth.log <<'EOF'
Mar  4 02:11:01 sec-log-06 sshd[1101]: Failed password for backup from 198.51.100.8 port 41022 ssh2
Mar  4 02:14:11 sec-log-06 sshd[1108]: Failed password for finance from 203.0.113.44 port 51102 ssh2
Mar  4 02:14:14 sec-log-06 sshd[1109]: Failed password for finance from 203.0.113.44 port 51108 ssh2
Mar  4 02:14:18 sec-log-06 sshd[1110]: Failed password for finance from 203.0.113.44 port 51112 ssh2
Mar  4 02:14:22 sec-log-06 sshd[1111]: Failed password for finance from 203.0.113.44 port 51120 ssh2
Mar  4 02:20:01 sec-log-06 sshd[1200]: Accepted publickey for ops from 10.9.1.40 port 51222 ssh2
Mar  4 03:01:09 sec-log-06 sudo: ops : TTY=pts/0 ; USER=root ; COMMAND=/bin/ls
EOF
"""
SEC_VM_AUTH = _vm({
    'id': 'sec-vm-authlog',
    'title': 'Real Linux VM — Failed login investigation',
    'blurb': 'Read auth.log. Record the source address and the account that failed most often.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM'},
        {'id': 'source', 'text': '/root/ir/source.txt contains the address with the most failures'},
        {'id': 'account', 'text': '/root/ir/account.txt contains the account name on those failures'},
    ],
    'intro': 'Security asked who is being guessed, and from where. The log is /var/log/auth.log. One successful login is not the pattern.',
    'success_msg': 'You named the noisy source and the account it targeted.',
    'course_objectives': ['SEC-8.1', 'SEC-8.3'],
    'minutes': 20,
    'palette': ['ls /var/log', 'grep ', 'journalctl ', 'wc '],
    'hints': ['Failed lines and accepted lines are different stories.', 'Count repeats instead of stopping at the first line.', 'Write the two answers into the two files under /root/ir.'],
    'obj_hints': {
        'boot': ['The log is a text file under /var/log.', 'Read it before you write the answer files.'],
        'source': ['The noisy address appears on more than one failure.', 'Put only that address in the source file.'],
        'account': ['The account name sits on those same failure lines.', 'Put only that account in the account file.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>grep Failed /var/log/auth.log</code> shows failures. '
        'On a systemd host the same events are in <code>journalctl</code>. '
        'A successful line says Accepted. Count which address and which account repeat. '
        'This walkthrough uses a sample address, 198.51.100.9, that is not the live answer.</p>',
        '<p><strong>Stage 2 — assisted.</strong> The live log mixes a single failure, a burst of failures, and one success. '
        'Decide which address failed most often and which account those lines name. '
        'Write the address to /root/ir/source.txt and the account to /root/ir/account.txt. One token each, nothing else required.</p>',
        '<p><strong>Stage 3 — ticket AUTH-BURST.</strong> Overnight failures need a one-line identification: '
        'the source that failed most, and the account it kept trying. File them in /root/ir as the ticket names. Do not lock any account.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-log-06', 'sec-log-06')], setup={'vm': _AUTH}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'source', 'sh': "grep -q '203.0.113.44' /root/ir/source.txt", 'why': 'source.txt does not name the noisiest address.'},
        {'id': 'account', 'sh': "grep -q 'finance' /root/ir/account.txt", 'why': 'account.txt does not name the targeted account.'},
    ],
    'solution': {'vm_commands': [
        'grep Failed /var/log/auth.log',
        'mkdir -p /root/ir',
        "printf '203.0.113.44\\n' > /root/ir/source.txt",
        "printf 'finance\\n' > /root/ir/account.txt",
    ]},
})


# ---------------------------------------------------------------- VM: cron
_CRON = _prelude('sec-cron-07') + r"""
mkdir -p /var/spool/cron/crontabs /var/tmp/.font /usr/local/bin
printf '#!/bin/sh\necho tick\n' > /var/tmp/.font/sync.sh
chmod 755 /var/tmp/.font/sync.sh
printf '#!/bin/sh\necho rotate\n' > /usr/local/bin/logrotate-local
chmod 755 /usr/local/bin/logrotate-local
cat > /var/spool/cron/crontabs/root <<'EOF'
*/10 * * * * /var/tmp/.font/sync.sh
EOF
chmod 600 /var/spool/cron/crontabs/root
"""
SEC_VM_CRON = _vm({
    'id': 'sec-vm-cron',
    'title': 'Real Linux VM — Suspicious scheduled job',
    'blurb': 'Root has a nightly rotate job and a hidden job. Remove the hidden job and the program it runs. Keep the nightly job.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM'},
        {'id': 'kept', 'text': 'The nightly logrotate-local job is still scheduled'},
        {'id': 'gone', 'text': 'The hidden sync job is not scheduled and its program is gone'},
    ],
    'intro': 'A baseline says root runs one nightly rotate. Anything else in the crontab, especially under a dot directory, is suspect.',
    'success_msg': 'The nightly job remains. The hidden job and its program are gone.',
    'course_objectives': ['SEC-9.2'],
    'minutes': 25,
    'palette': ['crontab -l', 'ls -la /var/tmp', 'rm '],
    'hints': ['List the scheduled jobs before you replace the table.', 'Keep the job that matches the baseline name.', 'Remove the program the surprise job points at, not only the schedule line.'],
    'obj_hints': {
        'boot': ['Scheduled jobs for root are listed by the crontab tool.', 'Read them before you edit.'],
        'kept': ['The nightly rotate name is the one the baseline expects.', 'That line must still be scheduled when you finish.'],
        'gone': ['The surprise line points at a hidden program.', 'Unschedule it and delete that program.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>crontab -l</code> lists root jobs. '
        'You can send a filtered table back with a pipe into <code>crontab -</code>. '
        '<code>rm</code> deletes a program. Never wipe the whole table if one line is still required.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Root’s table has a job that does not belong, and the nightly rotate is missing. '
        'The baseline name is a local rotate program under /usr/local/bin. Schedule that nightly job, remove the hidden job, and delete the hidden program.</p>',
        '<p><strong>Stage 3 — ticket CRON-HIDE.</strong> Root’s schedule does not match the baseline. '
        'Put the nightly rotate back, remove the extra job, and delete the program that extra job called.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-cron-07', 'sec-cron-07')], setup={'vm': _CRON}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'kept', 'sh': "crontab -l | grep -q logrotate-local", 'why': 'The nightly rotate job is missing.'},
        {'id': 'gone', 'sh': "! crontab -l | grep -q sync.sh && ! [ -e /var/tmp/.font/sync.sh ]",
         'why': 'The hidden job or its program is still present.'},
    ],
    'solution': {'vm_commands': [
        'crontab -l',
        "printf '%s\\n' '15 3 * * * /usr/local/bin/logrotate-local' | crontab -",
        'rm -f /var/tmp/.font/sync.sh',
        'crontab -l',
    ]},
})


# ---------------------------------------------------------------- VM: process
_PROC = _prelude('sec-proc-08') + r"""
mkdir -p /var/tmp/.cache
cat > /var/tmp/.cache/beacon <<'EOF'
#!/bin/sh
while true; do sleep 60; done
EOF
chmod 755 /var/tmp/.cache/beacon
( setsid /var/tmp/.cache/beacon </dev/null >/dev/null 2>&1 & )
"""
SEC_VM_PROC = _vm({
    'id': 'sec-vm-proc',
    'title': 'Real Linux VM — Suspicious process',
    'blurb': 'A hidden program is running from a cache directory. Record is optional; stop it and remove the program.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM'},
        {'id': 'stopped', 'text': 'The hidden beacon process is not running'},
        {'id': 'removed', 'text': 'The beacon program file is gone'},
    ],
    'intro': 'A normal system does not run long-lived programs from /var/tmp/.cache. Find it, stop it, and remove the file so it cannot be started again by hand.',
    'success_msg': 'The beacon is stopped and the program file is gone.',
    'course_objectives': ['SEC-3.3', 'SEC-3.4'],
    'minutes': 20,
    'palette': ['ps w', 'ss -tulpn', 'ls -la /var/tmp', 'kill ', 'rm '],
    'hints': ['A long process listing shows the path, not only the short name.', 'Stop the running copy and also delete the file.', 'Do not delete unrelated programs in /usr/bin.'],
    'obj_hints': {
        'boot': ['Look at running programs and at hidden directories under temporary space.', 'The path will look out of place.'],
        'stopped': ['Stopping a process is not the same as deleting its file.', 'The long listing should no longer show that path running.'],
        'removed': ['If the file remains, someone can start it again.', 'Remove that file after you know it is the one you saw running.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>ps w</code> shows arguments. '
        '<code>ss -tulpn</code> lists listening sockets when you are hunting a port instead of a path. '
        '<code>kill PID</code> stops a process. <code>rm</code> removes a file. '
        'Identify the path before you signal anything. A sample name like debugdump is not the live program.</p>',
        '<p><strong>Stage 2 — assisted.</strong> Something is looping under a hidden cache directory. '
        'Find the path from the process list, stop that process, and remove the program file. Leave ordinary system programs alone.</p>',
        '<p><strong>Stage 3 — ticket PROC-CACHE.</strong> A host is busy with a program that should not exist. '
        'Stop it and remove the file so a person cannot start that copy again.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-proc-08', 'sec-proc-08')], setup={'vm': _PROC}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'stopped', 'sh': "! ps w | grep -v grep | grep -q /var/tmp/.cache/beacon",
         'why': 'The beacon process is still running.'},
        {'id': 'removed', 'sh': "! [ -e /var/tmp/.cache/beacon ]", 'why': 'The beacon program file is still on disk.'},
    ],
    'solution': {'vm_commands': [
        'ps w',
        "kill $(ps w | grep /var/tmp/.cache/beacon | grep -v grep | awk '{print $1}')",
        'rm -f /var/tmp/.cache/beacon',
        'ps w',
    ]},
})


# ---------------------------------------------------------------- VM: hash
_HASH = _prelude('sec-hash-09') + r"""
mkdir -p /opt/app /tmp/sum
printf 'release-7\n' > /opt/app/build.bin.good
cp /opt/app/build.bin.good /tmp/sum/build.bin
( cd /tmp/sum && sha256sum build.bin ) > /opt/app/SHA256SUMS
printf 'release-7\nTAMPER\n' > /opt/app/build.bin
rm -rf /tmp/sum
"""
SEC_VM_HASH = _vm({
    'id': 'sec-vm-hash',
    'title': 'Real Linux VM — Check a file with sha256sum',
    'blurb': 'A release file no longer matches its sums file. Restore the known-good copy and prove the fingerprint matches.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM'},
        {'id': 'match', 'text': 'sha256sum -c succeeds for /opt/app/build.bin'},
    ],
    'intro': 'Publishers ship a fingerprint so you can see tampering. The good bytes are beside the live file. The sums file expects the name build.bin.',
    'success_msg': 'The live file matches the published fingerprint.',
    'course_objectives': ['SEC-4.1', 'SEC-9.4'],
    'minutes': 20,
    'palette': ['sha256sum ', 'ls -l /opt/app', 'cp '],
    'hints': ['A sums check fails when the bytes differ, even if the name is right.', 'A known-good copy is in the same directory with a different name.', 'Check from the directory that matches the name inside the sums file.'],
    'obj_hints': {
        'boot': ['Look in /opt/app before you copy anything.', 'See which names are the live file, the good copy, and the sums file.'],
        'match': ['The checker compares bytes to the fingerprint and cares about the filename in the sums file.', 'Replace the live bytes with the known-good bytes, then run the checker.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>sha256sum FILE</code> prints a fingerprint. '
        '<code>sha256sum -c SUMS</code> checks every name listed in the sums file, from the current directory. '
        'A mismatch means the bytes changed. Restoring means copying the known-good bytes over the live name, then checking again.</p>',
        '<p><strong>Stage 2 — assisted.</strong> The sums file and a good copy are both on the system. '
        'The live file fails the check. Put the good bytes under the name the sums file expects and show a clean check. Do not edit the sums file to match the tampered bytes.</p>',
        '<p><strong>Stage 3 — ticket HASH-REL.</strong> Release engineering says the build artifact was modified. '
        'Restore it from the known-good copy and prove the fingerprint matches. Leave the sums file unchanged.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-hash-09', 'sec-hash-09')], setup={'vm': _HASH}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'match', 'sh': 'cd /opt/app && sha256sum -c SHA256SUMS', 'why': 'build.bin still does not match SHA256SUMS.'},
    ],
    'solution': {'vm_commands': [
        'ls -l /opt/app',
        'cd /opt/app && sha256sum -c SHA256SUMS',
        'cp /opt/app/build.bin.good /opt/app/build.bin',
        'cd /opt/app && sha256sum -c SHA256SUMS',
    ]},
})


# ---------------------------------------------------------------- VM: grep forensics
_GREP = _prelude('sec-grep-10') + r"""
mkdir -p /var/log /root/case
cat > /var/log/app.log <<'EOF'
09:01 INFO service start
09:14 ERROR SR-4419 disk denied for acct payroll
09:15 INFO health ok
09:22 ERROR SR-4419 repeated from 203.0.113.44
09:30 WARN backup slow
09:41 INFO SR-2201 unrelated rotate
EOF
"""
SEC_VM_GREP = _vm({
    'id': 'sec-vm-grep',
    'title': 'Real Linux VM — Log extract',
    'blurb': 'Copy only the lines for incident SR-4419 into the case file. Leave the original log in place.',
    'objectives': [
        {'id': 'boot', 'text': 'Boot the VM'},
        {'id': 'hits', 'text': '/root/case/hits.txt contains the SR-4419 lines'},
        {'id': 'clean', 'text': 'The extract does not include the unrelated backup warning'},
    ],
    'intro': 'The case folder is /root/case. The log is /var/log/app.log. Incident SR-4419 is the only identifier you should extract.',
    'success_msg': 'The case file has the incident lines and not the unrelated warning.',
    'course_objectives': ['SEC-8.4', 'SEC-9.4'],
    'minutes': 15,
    'palette': ['ls /var/log', 'grep ', 'wc -l '],
    'hints': ['Match the incident identifier, not every ERROR.', 'Write the matches into the case file.', 'The original log should still be there afterward.'],
    'obj_hints': {
        'boot': ['Find the application log and the case directory.', 'Read a few lines so you see the shape.'],
        'hits': ['Only lines that name this incident belong in the extract.', 'Create the case file from those lines.'],
        'clean': ['A nearby warning is a different event.', 'It should not be in the extract.'],
    },
    'coaching': _coach(
        '<p><strong>Stage 1 — guided.</strong> <code>grep PATTERN FILE</code> prints matching lines. '
        'Redirect with <code>&gt;</code> to save them. A pattern that is too wide pulls in other incidents. '
        'Practice on a sample identifier such as SR-0000, which is not in this log.</p>',
        '<p><strong>Stage 2 — assisted.</strong> The incident identifier is SR-4419. '
        'Save every log line that names it into /root/case/hits.txt. Leave unrelated warnings out, and do not delete the original log.</p>',
        '<p><strong>Stage 3 — ticket SR-4419.</strong> Counsel asked for the lines and only the lines. '
        'Deliver the extract in the case folder. Keep the source log intact.</p>',
    ),
    'vm': dict(IMAGE, machines=[_m('vm', 'sec-grep-10', 'sec-grep-10')], setup={'vm': _GREP}),
    'vm_checks': [
        {'id': 'boot'},
        {'id': 'hits', 'sh': "grep -q SR-4419 /root/case/hits.txt && [ -f /var/log/app.log ]",
         'why': 'hits.txt is missing the incident lines, or the original log was removed.'},
        {'id': 'clean', 'sh': "[ -s /root/case/hits.txt ] && ! grep -q 'backup slow' /root/case/hits.txt",
         'why': 'The extract is missing or includes an unrelated warning.'},
    ],
    'solution': {'vm_commands': [
        'grep SR-4419 /var/log/app.log',
        'mkdir -p /root/case',
        'grep SR-4419 /var/log/app.log > /root/case/hits.txt',
    ]},
})


SEC_VM_LABS = [
    SEC_VM_IPTABLES, SEC_VM_PERMS, SEC_VM_SUID, SEC_VM_USERS, SEC_VM_SSH,
    SEC_VM_AUTH, SEC_VM_CRON, SEC_VM_PROC, SEC_VM_HASH, SEC_VM_GREP,
]


def _activity(lid, title, blurb, skill, prompts):
    """prompts: list of (prompt, options, answer_index, explain dict, right)."""
    objectives = []
    steps = []
    answers = {}
    hints = []
    obj_hints = {}
    for i, (prompt, options, ans, explain, right) in enumerate(prompts, start=1):
        oid = f'q{i}'
        objectives.append({'id': oid, 'text': prompt[:110]})
        steps.append(_choice(f's{i}', oid, prompt, options, ans, explain, right))
        answers[f's{i}'] = ans
        hints.append('Use the scenario text. Eliminate the choice that skips a record or expands access.')
        obj_hints[oid] = [
            'Name the goal in the question before you look at the choices.',
            'Reject the choice that is faster but skips identity, evidence, or least privilege.',
        ]
    return _act({
        'id': lid,
        'title': title,
        'blurb': blurb,
        'objectives': objectives,
        'intro': blurb,
        'success_msg': 'Your decisions match the control the lesson describes.',
        'course_objectives': [skill],
        'minutes': 15,
        'hints': hints,
        'obj_hints': obj_hints,
        'steps': steps,
        'coaching': _coach(
            '<p><strong>Stage 1 — guided.</strong> Each question names a goal. '
            'Read every choice. The safe choice is the one that keeps evidence, limits access, or matches the factor or control type. '
            'A faster choice that skips a record is the one to reject.</p>',
            '<p><strong>Stage 2 — assisted.</strong> The prompts use a fresh workplace story. '
            'Decide from the story. Do not look for a command to paste. If two choices sound strict, pick the one that still lets the real work happen.</p>',
            '<p><strong>Stage 3 — ticket.</strong> You are the on-call person. Answer from policy and evidence. '
            'There is no command line on this station. Submit each decision when you can defend it in one sentence.</p>',
        ),
        'solution': {'answers': answers},
    })


SEC_GPG = _activity(
    'sec-gpg', 'GPG decisions — encrypt and decrypt',
    'GnuPG is not in the browser Linux image, so this station grades the decisions: who holds which key, and which action hides or reveals a file.',
    'SEC-4.2',
    [
        ('You must send payroll.csv so only the finance lead can read it. What do you use?',
         ['Encrypt to the finance lead public key', 'Encode the file as Base64', 'Hash the file and send the hash instead', 'Email your private key with the file'],
         0, {1: 'Encoding is reversible with no secret.', 2: 'A hash does not carry the file.', 3: 'The private key must stay with you.'},
         'Encrypting to their public key means only their private key opens it.'),
        ('Which key do you publish?',
         ['The public key', 'The private key', 'Both keys in one zip', 'The passphrase only'],
         0, {1: 'The private key stays secret.', 2: 'Publishing the private key defeats the pair.', 3: 'A passphrase is not the public key.'},
         'The public key is the one you can share.'),
        ('A teammate asks you to decrypt a file that was locked to you. What unlocks it?',
         ['Your private key, and its passphrase if you set one', 'Your public key', 'A fresh hash of the file', 'Base64 decode'],
         0, {1: 'The public key locks messages to you. It does not open them.', 2: 'A hash is not a key.', 3: 'Decoding is not decryption.'},
         'Only the matching private key opens what was encrypted to your public key.'),
        ('Where should the private key file sit?',
         ['Unreadable to other users, with a passphrase', 'Mode 666 in a shared directory', 'Pasted into the ticket', 'Next to the ciphertext in the same email'],
         0, {1: 'Other users could copy it.', 2: 'Tickets are widely readable.', 3: 'The key must not travel with the locked file.'},
         'Protect the private key file the way you protect any other secret.'),
    ],
)

SEC_WIN_FW = _activity(
    'sec-win-fw', 'Windows firewall — which allow is safe',
    'A simulated Windows host. Choose firewall decisions. Nothing is changed on a real PC.',
    'SEC-7.3',
    [
        ('Remote Desktop must work for two admin laptops and nobody else. Which inbound rule matches?',
         ['Allow TCP 3389 only from the admin subnet', 'Allow TCP 3389 from any address', 'Turn the firewall off', 'Allow every inbound TCP port from the admin subnet'],
         0, {1: 'Any address is not the two laptops.', 2: 'Off is not an allow you can name.', 3: 'The whole subnet does not need every port.'},
         'Name the port and the source.'),
        ('A vendor asks you to disable the firewall for the afternoon and leave it. What do you do?',
         ['Keep it on and add the one port they named, with an expiry', 'Disable it and write nothing', 'Disable it and email the whole company the admin password', 'Allow all inbound permanently'],
         0, {1: 'A silent disable becomes drift.', 2: 'That shares a secret.', 3: 'Permanent any-inbound is not a test.'},
         'A named allow with an end date beats a disabled firewall.'),
        ('The default inbound stance you want on a workstation is:',
         ['Block, with explicit allows', 'Allow, with a few blocks', 'Block outbound internet entirely, including updates', 'No firewall because the network firewall exists'],
         0, {1: 'A default allow misses new ports.', 2: 'Blocking updates hurts patching.', 3: 'The host still needs its own rule set.'},
         'Default deny inbound is the workstation stance.'),
        ('Where do you confirm the rule after you add it?',
         ['The firewall rule list, including scope and port', 'A screenshot of the desktop', 'The user said it feels faster', 'Event Viewer application errors only'],
         0, {1: 'A picture of the desktop does not show scope.', 2: 'Feeling is not a rule.', 3: 'Application errors are a different log.'},
         'Read the rule back: port, direction, and source.'),
    ],
)

SEC_WIN_POL = _activity(
    'sec-win-policy', 'Local security policy — account rules',
    'Choose local policy settings for a standalone Windows lab PC. This is a decision station, not a domain controller.',
    'SEC-7.3',
    [
        ('Which password policy matches least privilege and hygiene?',
         ['Long minimum length, and refuse reuse of recent passwords', 'Blank passwords allowed for speed', 'Maximum length of 6 characters', 'One shared password for every local account'],
         0, {1: 'Blank passwords are not a policy.', 2: 'A short maximum forces weak secrets.', 3: 'Sharing erases attribution.'},
         'Length and no reuse beat a shared or blank secret.'),
        ('Ten bad passwords in a minute should:',
         ['Lock the account for a short window', 'Disable the audit log', 'Turn off the firewall', 'Email the password to the user'],
         0, {1: 'You need the failures recorded.', 2: 'The firewall is unrelated.', 3: 'Never send the password.'},
         'A short lockout slows guessing without deleting the account.'),
        ('Which audit setting helps a later investigation?',
         ['Record success and failure logons', 'Record nothing to save disk', 'Clear the Security log every hour', 'Audit only print jobs'],
         0, {1: 'No record means no triage.', 2: 'Clearing the log destroys evidence.', 3: 'Print jobs do not show who signed in.'},
         'Logon success and failure are the events you will need.'),
        ('A user asks you to disable the consent prompt so installs are one click. You:',
         ['Leave the prompt on and use a separate admin account when an install is approved', 'Disable it for everyone', 'Give every user a permanent admin token', 'Share the local administrator password'],
         0, {1: 'The prompt is a control.', 2: 'Standing admin is not least privilege.', 3: 'A shared admin password is a shared account.'},
         'Keep the prompt. Elevate only for the approved install.'),
    ],
)

SEC_WIN_EVT = _activity(
    'sec-win-events', 'Event Viewer — triage a logon alert',
    'Read a described Windows Security event and sort it. No live Windows machine is required.',
    'SEC-8.3',
    [
        ('Event 4625 repeats for one account from one external address. First bucket?',
         ['Needs containment review: repeated failures against one account', 'Ignore because 4625 means success', 'Wipe the domain controller', 'Treat it as a printer jam'],
         0, {1: '4625 is a failure. 4624 is a success.', 2: 'Wiping is not triage.', 3: 'This is a logon event.'},
         'Repeated 4625 from one address is a guessing pattern, not a success.'),
        ('A single 4624 for a user at their normal office hour is:',
         ['Likely normal if it matches the baseline', 'Always ransomware', 'Proof the firewall is off', 'A reason to delete the account'],
         0, {1: 'One success at a normal hour is not ransomware by itself.', 2: 'A logon event does not describe the firewall.', 3: 'Do not delete an account for a normal logon.'},
         'Compare success events to the baseline before you escalate.'),
        ('You want the logon channel. You open:',
         ['Security', 'Application', 'Setup', 'Forwarded Events only, with local Security cleared'],
         0, {1: 'Application holds program errors.', 2: 'Setup is installation history.', 3: 'Do not clear Security.'},
         'Logons are in the Security channel.'),
        ('The queue is large. You:',
         ['Write a one-line reason for each bucket you close', 'Close all as false with no note', 'Disable the Security log', 'Export every event to a public chat'],
         0, {1: 'A silent close is not triage.', 2: 'Disabling the log hides the next event.', 3: 'Public chat is not a case file.'},
         'A bucket without a sentence is not a decision.'),
    ],
)

SEC_ACL = _activity(
    'sec-acl', 'Firewall ACL — which packet passes',
    'A small rule list is in each question. Decide what the packet does. This grader checks your decision, not a device CLI.',
    'SEC-6.2',
    [
        ('Rules, top to bottom: allow TCP 443 from anywhere; deny all. A packet is TCP 443 from a guest. Result?',
         ['Allowed by the first rule', 'Denied because guests are never allowed', 'Allowed because deny all is first', 'Dropped because 443 is encrypted'],
         0, {1: 'The first rule does not mention guests.', 2: 'Deny all is last.', 3: 'Encryption is not the rule.'},
         'First match wins. TCP 443 hits the allow.'),
        ('Same list. A packet is TCP 22 from a guest. Result?',
         ['Denied by the final deny', 'Allowed because guests are on the network', 'Allowed because SSH is secure', 'Allowed by the 443 rule'],
         0, {1: 'Being on the network is not a rule.', 2: 'Secure is not an allow.', 3: 'Port 22 is not port 443.'},
         'Nothing allows 22, so the final deny matches.'),
        ('You want finance servers unreachable from the guest zone. What do you add?',
         ['A deny from the guest zone to the finance zone, placed so it matches', 'A note in a wiki and no rule', 'An allow from guests to all servers', 'A VLAN rename with no filter'],
         0, {1: 'A wiki note does not filter packets.', 2: 'That allow is the opposite.', 3: 'A name without a filter does not segment.'},
         'Segmentation is a rule between zones, not a label.'),
        ('An emergency allow has no owner and no end date. It is:',
         ['Drift until someone approves it or removes it', 'Automatically part of the baseline', 'Proof the network is segmented', 'A substitute for logs'],
         0, {1: 'Unapproved changes are not the baseline.', 2: 'One allow does not prove segmentation.', 3: 'An allow does not record who connected.'},
         'Emergency allows need an owner and a review, or they are drift.'),
    ],
)

SEC_PHISH = _activity(
    'sec-phish', 'Phishing email — what do you do',
    'Analyze a described message. Do not build or send anything. The safe action is the point.',
    'SEC-2.2',
    [
        ('The display name is Payroll. The address is payroll@pay-roll-example.com. The link host is not your company. You:',
         ['Report it and do not enter credentials', 'Sign in because the display name matches', 'Forward your password to the sender to confirm', 'Click to see where it goes, using your admin account'],
         0, {1: 'The display name is spoofable.', 2: 'Never send a password.', 3: 'An admin click is worse.'},
         'Check the real address and the link host. Report. Do not authenticate.'),
        ('A caller says they are the new CFO and need a password read aloud. You:',
         ['Refuse, and call back using the number in the directory', 'Read the password because they sound senior', 'Disable MFA so they can get in', 'Email the password to the address they give you'],
         0, {1: 'Seniority is not identity.', 2: 'Disabling MFA is not help.', 3: 'Their channel is the one you do not trust.'},
         'Verify on a channel you already trust.'),
        ('A USB stick labeled salaries is in the parking lot. You:',
         ['Leave it and tell the instructor or security', 'Plug it into your work computer to find the owner', 'Plug it into a friend computer', 'Open the files and then report'],
         0, {1: 'Plugging it in is how bait runs.', 2: 'A friend computer is still a computer.', 3: 'Opening it is too late.'},
         'Found media is untrusted. Do not mount it on a daily-use computer.'),
        ('Which detail is the strongest phish tell in a short message?',
         ['Urgency plus a link whose host is not the real service', 'A signature block', 'The word please', 'A morning timestamp'],
         0, {1: 'Signatures are easy to copy.', 2: 'Politeness is not evidence.', 3: 'Time of day is weak alone.'},
         'Pressure plus a mismatched host is the pattern to report.'),
    ],
)

SEC_MFA = _activity(
    'sec-mfa', 'MFA — which pair counts',
    'Decide which combinations are actually multi-factor. No codes are sent.',
    'SEC-5.1',
    [
        ('Which pair is MFA?',
         ['Password and a prompt on a phone you have', 'Password and a PIN', 'Two different passwords', 'A fingerprint used twice'],
         0, {1: 'Both are something you know.', 2: 'Both are something you know.', 3: 'The same factor twice is still one kind.'},
         'A password (know) plus a phone (have) is two kinds.'),
        ('Backup codes stored in the same chat as the password are:',
         ['A weak recovery path', 'Stronger than the phone prompt', 'Required by every standard', 'A form of encryption'],
         0, {1: 'They are not stronger if they sit with the password.', 2: 'They are a recovery secret, not a universal requirement.', 3: 'Storage location is not encryption.'},
         'Recovery that sits next to the first factor is not a second factor.'),
        ('A user lost the phone that receives prompts. You:',
         ['Revoke that factor and enroll a new one after you verify them out of band', 'Disable MFA permanently', 'Tell them to share a coworker phone prompt', 'Email the password to the lost phone number'],
         0, {1: 'Permanent disable is not the recovery design.', 2: 'A shared prompt is a shared factor.', 3: 'The lost phone is not a trusted channel.'},
         'Verify, then replace the factor. Do not turn MFA off as the fix.'),
        ('Which statement is accurate?',
         ['Two items you know are still one factor kind', 'Any two fields on a form are MFA', 'A longer password is automatically MFA', 'MFA means the account cannot be phished'],
         0, {1: 'Two fields can be the same kind.', 2: 'Length is not a second kind.', 3: 'MFA raises the bar. It is not magic.'},
         'Factor kind matters more than the number of boxes on the form.'),
    ],
)

SEC_CERT = _activity(
    'sec-cert', 'Certificate warning — what failed',
    'Name the TLS problem. Do not click through.',
    'SEC-4.4',
    [
        ('You asked for mail.example.edu. The certificate name is www.example.edu. The warning is:',
         ['Name mismatch', 'A hash failure', 'Proof the site is offline', 'Proof the password is short'],
         0, {1: 'This is a name, not a file hash.', 2: 'The warning appeared, so you reached a certificate.', 3: 'Passwords are unrelated.'},
         'The name you asked for is not the name on the certificate.'),
        ('Every site warns, and the laptop date is years off. Check:',
         ['The device clock, then the certificate dates', 'Nothing, and add a permanent exception', 'The wireless channel', 'The disk size'],
         0, {1: 'A permanent exception hides a real mismatch later.', 2: 'Channel does not set certificate dates.', 3: 'Disk size is unrelated.'},
         'A wrong clock makes valid dates look wrong. Fix the clock before you blame every site.'),
        ('The signer is not in the trust store and nobody on your team expected a private signer. You:',
         ['Stop and report. Do not add the signer.', 'Add the signer so the warning goes away', 'Email the private key to yourself', 'Switch the site to HTTP and continue'],
         0, {1: 'Adding a signer is a trust decision.', 2: 'You do not email private keys.', 3: 'HTTP removes the check instead of fixing it.'},
         'An unexpected signer is not your signer. Stop.'),
        ('A certificate binds:',
         ['A name to a public key, signed by someone you trust', 'A password to a user', 'A file hash to a backup', 'A private key to the whole internet'],
         0, {1: 'That is an account secret, not a certificate.', 2: 'A hash is not a certificate.', 3: 'The private key is not what you publish.'},
         'Name, public key, and a trusted signature. That is the certificate.'),
    ],
)

SEC_IR = _activity(
    'sec-ir', 'Incident response — order and first moves',
    'Choose the response habit. This station does not attack anything.',
    'SEC-9.1',
    [
        ('What comes before you reimage the only suspicious host?',
         ['Identify, contain, and record what you have', 'Reimage so the queue is clear', 'Pay the note', 'Post the disk image publicly'],
         0, {1: 'Reimaging first destroys the story.', 2: 'Paying is not the student action.', 3: 'Public posting spreads data.'},
         'Know what you have and stop the spread before you erase the machine.'),
        ('A suspicious scheduled job is still in the table. You:',
         ['Copy the line and the path, then remove it', 'Delete it and forget the text', 'Run it once to see the output', 'Email the script to a personal account'],
         0, {1: 'The text is the evidence.', 2: 'Running it gives it a chance.', 3: 'Personal mail is not a case file.'},
         'Record, then remove. Do not run it.'),
        ('Which recovery is actually clean?',
         ['Restore from a copy that does not contain the backdoor, then watch', 'Restore the backup taken after the backdoor was installed', 'Turn the host on and hope', 'Disable logging so alerts stop'],
         0, {1: 'That backup still has the cause.', 2: 'Hope is not eradication.', 3: 'Disabling logs hides the return.'},
         'The restore point has to be from before the cause, and you still watch.'),
        ('After the service is back, the lesson learned needs:',
         ['An owner and a change you will actually make', 'A closed ticket with no note', 'A public blame post', 'A new firewall brand and nothing else'],
         0, {1: 'No note means the same event repeats.', 2: 'Blame is not a control.', 3: 'A purchase without a change is not a lesson.'},
         'Name the change and the person who will make it.'),
    ],
)

SEC_RISK = _activity(
    'sec-risk', 'Risk language — likelihood and impact',
    'Sort workplace risks without calling everything critical. No scoring formula is required.',
    'SEC-1.4',
    [
        ('The customer list is:',
         ['An asset', 'A threat', 'A patch', 'A certificate'],
         0, {1: 'A threat is what might cause harm.', 2: 'A patch is a fix.', 3: 'A certificate binds a name to a key.'},
         'The list is the valued thing.'),
        ('An unpatched library on a server you actually run is:',
         ['A vulnerability', 'The impact', 'A policy', 'A VPN'],
         0, {1: 'Impact is the harm if it is used.', 2: 'Policy is a decision.', 3: 'A VPN is a path.'},
         'The flaw is the vulnerability. Harm is separate.'),
        ('A lost laptop with no disk encryption, full of personal data, is mostly about:',
         ['High impact if the disk is readable', 'Low impact because laptops are cheap', 'A wireless channel problem only', 'Proof that MFA failed'],
         0, {1: 'The hardware price is not the data harm.', 2: 'The disk, not the radio, is the issue.', 3: 'MFA is not what protects a powered-off disk.'},
         'Impact is the personal data on a readable disk.'),
        ('Accepting a risk means:',
         ['Writing down that you will live with it, and reviewing that choice', 'Ignoring it with no note', 'Buying a product so the form looks finished', 'Marking every item critical'],
         0, {1: 'Silence is not acceptance.', 2: 'A purchase is not a decision record.', 3: 'If everything is critical, nothing is ordered.'},
         'Acceptance is explicit and reviewed.'),
    ],
)

SEC_ACTIVITY_LABS = [
    SEC_GPG, SEC_WIN_FW, SEC_WIN_POL, SEC_WIN_EVT, SEC_ACL, SEC_PHISH, SEC_MFA, SEC_CERT, SEC_IR, SEC_RISK,
]

SEC_CHAPTER_LABS = {
    ('SEC', 1): ['sec-risk'],
    ('SEC', 2): ['sec-phish'],
    ('SEC', 3): ['sec-vm-proc'],
    ('SEC', 4): ['sec-vm-hash', 'sec-gpg', 'sec-cert'],
    ('SEC', 5): ['sec-mfa', 'sec-vm-users', 'sec-vm-ssh'],
    ('SEC', 6): ['sec-vm-iptables', 'sec-acl', 'sec-win-fw'],
    ('SEC', 7): ['sec-vm-perms', 'sec-vm-suid', 'sec-vm-users', 'sec-vm-ssh', 'sec-win-policy'],
    ('SEC', 8): ['sec-vm-authlog', 'sec-win-events', 'sec-vm-grep'],
    ('SEC', 9): ['sec-ir', 'sec-vm-cron', 'sec-vm-proc', 'sec-vm-hash', 'sec-vm-grep'],
    ('SEC', 10): ['sec-risk'],
}

SEC_LESSON_LABS = {
    ('SEC', 1, 4): ['sec-risk'],
    ('SEC', 2, 2): ['sec-phish'],
    ('SEC', 3, 3): ['sec-vm-proc'],
    ('SEC', 3, 4): ['sec-vm-proc'],
    ('SEC', 4, 1): ['sec-vm-hash'],
    ('SEC', 4, 2): ['sec-gpg'],
    ('SEC', 4, 3): ['sec-cert'],
    ('SEC', 4, 4): ['sec-cert'],
    ('SEC', 5, 1): ['sec-mfa'],
    ('SEC', 5, 2): ['sec-vm-users'],
    ('SEC', 5, 4): ['sec-vm-ssh'],
    ('SEC', 6, 1): ['sec-vm-iptables'],
    ('SEC', 6, 2): ['sec-acl'],
    ('SEC', 6, 4): ['sec-win-fw'],
    ('SEC', 7, 1): ['sec-vm-perms'],
    ('SEC', 7, 2): ['sec-vm-ssh'],
    ('SEC', 7, 3): ['sec-win-policy'],
    ('SEC', 7, 4): ['sec-vm-suid'],
    ('SEC', 8, 1): ['sec-vm-authlog'],
    ('SEC', 8, 3): ['sec-win-events'],
    ('SEC', 8, 4): ['sec-vm-grep'],
    ('SEC', 9, 1): ['sec-ir'],
    ('SEC', 9, 2): ['sec-vm-cron'],
    ('SEC', 9, 4): ['sec-vm-hash'],
    ('SEC', 10, 2): ['sec-risk'],
}

SEC_LAB_ALIGN = {lab['id']: lab['blurb'] for lab in SEC_VM_LABS + SEC_ACTIVITY_LABS}
