"""Command syntax cards for global search (Phase 1).

Typing a command (chmod, ipconfig, ufw, vlan, ...) in Cmd-K search shows a short syntax card and links to the
lessons and labs that practice it. Plain data; no network, no new dependencies.
"""
import re

# key: (display, platform, syntax, what it does, example)
CARDS = {
    'chmod': ('chmod', 'Linux / macOS', 'chmod [ugoa][+-=][rwx] FILE  ·  chmod 755 FILE', 'Change who can read, write, or run a file.', 'chmod 755 deploy.sh'),
    'chown': ('chown', 'Linux / macOS', 'chown USER[:GROUP] FILE', 'Change the owner (and group) of a file.', 'sudo chown alice:staff report.txt'),
    'ls': ('ls', 'Linux / macOS', 'ls [-l] [-a] [-h] [PATH]', 'List files; -l shows permissions and owners.', 'ls -la /etc'),
    'grep': ('grep', 'Linux / macOS', 'grep [-i] [-r] PATTERN [FILE]', 'Find lines that match text, including failed logins in auth.log.', 'grep Failed /var/log/auth.log'),
    'sudo': ('sudo', 'Linux / macOS', 'sudo COMMAND', 'Run one command as the administrator (root).', 'sudo apt update'),
    'ps': ('ps', 'Linux / macOS', 'ps aux', 'List running processes.', 'ps aux | grep nginx'),
    'kill': ('kill', 'Linux / macOS', 'kill [-9] PID', 'Stop a process by its ID.', 'kill 4211'),
    'df': ('df', 'Linux / macOS', 'df -h', 'Show free disk space per filesystem.', 'df -h /'),
    'systemctl': ('systemctl', 'Linux', 'systemctl status|start|stop|restart|enable SERVICE', 'Manage background services.', 'sudo systemctl restart ssh'),
    'journalctl': ('journalctl', 'Linux', 'journalctl [-u SERVICE] [-f]  ·  grep PATTERN /var/log/auth.log', 'Read system and service logs. On hosts without journald, search auth.log with grep.', 'journalctl -u ssh --since today'),
    'apt': ('apt', 'Ubuntu / Debian', 'apt update  ·  apt install PACKAGE', 'Install and update software packages.', 'sudo apt install htop'),
    'ufw': ('ufw', 'Ubuntu', 'ufw allow|deny PORT[/tcp]  ·  ufw enable  ·  ufw status', 'Turn on the host firewall and open or close ports.', 'sudo ufw allow 22/tcp'),
    'iptables': ('iptables', 'Linux', 'iptables -S  ·  iptables -A INPUT -p tcp --dport PORT -j ACCEPT|DROP', 'Low-level firewall rules. Default deny, then named allows.', 'iptables -S'),
    'sha256sum': ('sha256sum', 'Linux / macOS', 'sha256sum FILE  ·  sha256sum -c SUMS', 'Fingerprint a file, or check it against a saved hash.', 'sha256sum -c SHA256SUMS'),
    'chage': ('chage', 'Linux', 'chage -l USER  ·  chage -M DAYS USER  ·  chage -E DATE USER', 'Show or set how long a password stays valid.', 'chage -l intern'),
    'find': ('find', 'Linux / macOS', 'find PATH -perm -4000 -type f  ·  find PATH -perm -2000 -type f', 'List files, including ones with setuid or setgid bits.', 'find /usr/local -perm -4000 -type f'),
    'ip': ('ip', 'Linux', 'ip addr  ·  ip route  ·  ip link set DEV up', 'Show or change addresses, routes, and interfaces.', 'ip addr show eth0'),
    'ifconfig': ('ifconfig', 'Linux / macOS (legacy)', 'ifconfig [INTERFACE]', 'Show interface addresses (older tool; use ip on Linux).', 'ifconfig en0'),
    'ss': ('ss', 'Linux', 'ss -tulpn', 'Show listening ports and the programs using them.', 'sudo ss -tulpn'),
    'ssh': ('ssh', 'Linux / macOS / Windows', 'ssh USER@HOST [-p PORT]', 'Open a secure remote shell.', 'ssh admin@10.0.0.5'),
    'dig': ('dig', 'Linux / macOS', 'dig NAME [TYPE]', 'Look up DNS records in detail.', 'dig example.com A'),
    'ipconfig': ('ipconfig', 'Windows', 'ipconfig [/all] [/release] [/renew] [/flushdns]', 'Show or refresh this PC\u2019s IP settings.', 'ipconfig /all'),
    'ping': ('ping', 'Windows / Linux / macOS', 'ping HOST  ·  ping -c 4 HOST (Linux)', 'Test whether a host answers and how fast.', 'ping 8.8.8.8'),
    'tracert': ('tracert', 'Windows', 'tracert HOST', 'Show each router hop to a host.', 'tracert example.com'),
    'traceroute': ('traceroute', 'Linux / macOS', 'traceroute HOST', 'Show each router hop to a host.', 'traceroute example.com'),
    'nslookup': ('nslookup', 'Windows / Linux / macOS', 'nslookup NAME [SERVER]', 'Ask DNS what address a name has.', 'nslookup example.com'),
    'netstat': ('netstat', 'Windows / Linux', 'netstat -ano (Windows)  ·  netstat -tulpn (Linux)', 'Show connections and listening ports.', 'netstat -ano'),
    'arp': ('arp', 'Windows / Linux / macOS', 'arp -a', 'Show the IP-to-MAC address table.', 'arp -a'),
    'sfc': ('sfc', 'Windows', 'sfc /scannow', 'Check and repair protected Windows system files.', 'sfc /scannow'),
    'dism': ('DISM', 'Windows', 'DISM /Online /Cleanup-Image /RestoreHealth', 'Repair the Windows image, then run sfc.', 'DISM /Online /Cleanup-Image /RestoreHealth'),
    'chkdsk': ('chkdsk', 'Windows', 'chkdsk [DRIVE:] [/f] [/r]', 'Check a disk for errors and fix them.', 'chkdsk C: /f'),
    'bcdedit': ('bcdedit', 'Windows', 'bcdedit /enum', 'View or edit Windows boot entries.', 'bcdedit /enum'),
    'bootrec': ('bootrec', 'Windows RE', 'bootrec /fixmbr | /fixboot | /rebuildbcd', 'Repair Windows boot records from recovery.', 'bootrec /rebuildbcd'),
    'gpupdate': ('gpupdate', 'Windows', 'gpupdate [/force]', 'Apply Group Policy now.', 'gpupdate /force'),
    'gpresult': ('gpresult', 'Windows', 'gpresult /r', 'Show which Group Policies apply.', 'gpresult /r'),
    'diskpart': ('diskpart', 'Windows', 'diskpart  →  list disk · select disk N · clean', 'Partition and prepare disks.', 'diskpart'),
    'robocopy': ('robocopy', 'Windows', 'robocopy SRC DEST [/E] [/MIR]', 'Copy folders reliably, with retries.', 'robocopy C:\\Data D:\\Backup /E'),
    'tasklist': ('tasklist', 'Windows', 'tasklist  ·  taskkill /PID N [/F]', 'List or stop running programs.', 'taskkill /IM notepad.exe /F'),
    'icacls': ('icacls', 'Windows', 'icacls PATH [/grant USER:(R|M|F)]', 'View or change NTFS permissions.', 'icacls C:\\Share /grant Staff:(M)'),
    'net': ('net user', 'Windows', 'net user [NAME] [/add]  ·  net use Z: \\\\SERVER\\SHARE', 'Manage local users and map network drives.', 'net user'),
    'vlan': ('vlan', 'Cisco IOS', 'vlan ID  →  name NAME  ·  show vlan brief', 'Create a VLAN on a switch and check it.', 'vlan 10'),
    'switchport': ('switchport', 'Cisco IOS', 'switchport mode access|trunk  ·  switchport access vlan ID', 'Put a switch port in a VLAN or make it a trunk.', 'switchport access vlan 10'),
    'show': ('show', 'Cisco IOS', 'show vlan brief · show ip interface brief · show running-config · show interfaces trunk', 'Read the device\u2019s current state.', 'show ip interface brief'),
    'router': ('router ospf', 'Cisco IOS', 'router ospf ID  →  network NET WILDCARD area N', 'Turn on OSPF routing.', 'router ospf 1'),
    'access-list': ('access-list', 'Cisco IOS', 'access-list N permit|deny SOURCE [WILDCARD]', 'Filter traffic with an ACL.', 'access-list 10 permit 192.168.1.0 0.0.0.255'),
    'write': ('write memory', 'Cisco IOS', 'write memory  ·  copy running-config startup-config', 'Save the config so it survives a reboot.', 'copy running-config startup-config'),
}
ALIASES = {
    'taskkill': 'tasklist', 'sh': 'show', 'ospf': 'router', 'acl': 'access-list', 'wr': 'write', 'copy': 'write',
    'flushdns': 'ipconfig', 'scannow': 'sfc', 'firewall': 'ufw', 'vlans': 'vlan', 'trunk': 'switchport',
    'chmod755': 'chmod', 'permissions': 'chmod', 'netsh': 'ipconfig',
    'sha256': 'sha256sum', 'setuid': 'find', 'perm': 'find',
}

# Command cards that should list Cybersecurity labs before older matches.
PREFER_LAB_PREFIX = {
    'iptables': 'sec-', 'sha256sum': 'sec-', 'chage': 'sec-', 'find': 'sec-',
    'ss': 'sec-', 'journalctl': 'sec-', 'grep': 'sec-',
}

_NEEDS_FULL = {'router', 'write', 'net'}
_WORD = re.compile(r'[a-z][a-z0-9-]*')


def card_for(query):
    """Return a command card dict if the query starts with (or is) a known command, else None."""
    q = (query or '').strip().lower()
    if not q or len(q) > 80:
        return None
    m = _WORD.match(q)
    if not m:
        return None
    key = m.group(0)
    key = key if key in CARDS else ALIASES.get(key)
    if not key:
        return None
    disp, plat, syntax, what, example = CARDS[key]
    if key in _NEEDS_FULL and m.group(0) == key and not q.startswith(disp.lower()):
        return None
    return {'key': key, 'command': disp, 'platform': plat, 'syntax': syntax, 'what': what, 'example': example,
            'search_term': disp.split()[0]}


def labs_using(command, labs):
    """Labs whose definition mentions the command (accepted commands, steps, hints)."""
    word = re.compile(r'(?<![\w-])' + re.escape(command.lower()) + r'(?![\w-])')
    out = []
    for lab in labs or []:
        try:
            blob = repr(lab).lower()
        except Exception:
            continue
        if word.search(blob):
            out.append(lab)
    return out
