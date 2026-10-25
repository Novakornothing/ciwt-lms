"""Linux shell simulator (bash-like) for the Linux basics and permissions lab.

A small in-memory file system with owners and permission bits. Supports the commands a support
technician uses first (navigation, files, permissions, facts, grep) with real-looking output and the
same error messages bash and coreutils print. Windows commands typed by habit get a pointer to the
Linux equivalent instead of a bare "command not found".
"""
import posixpath
import re
import shlex

HOME = '/home/trainee'


def _f(content='', mode=0o644, owner='trainee', group='trainee'):
    return {'t': 'f', 'mode': mode, 'owner': owner, 'group': group, 'c': content}


def _d(mode=0o755, owner='trainee', group='trainee'):
    return {'t': 'd', 'mode': mode, 'owner': owner, 'group': group}


def linux_state(**extra):
    fs = {
        '/': _d(owner='root', group='root'), '/home': _d(owner='root', group='root'), HOME: _d(0o750),
        '/tmp': _d(0o777, 'root', 'root'), '/etc': _d(owner='root', group='root'),
        '/etc/hostname': _f('novak-lnx-01\n', 0o644, 'root', 'root'),
        '/etc/shadow': _f('root:*:19000:0:99999:7:::\n', 0o640, 'root', 'shadow'),
        '/var': _d(owner='root', group='root'), '/var/log': _d(owner='root', group='root'),
        '/var/log/syslog': _f('Oct 17 09:01 novak-lnx-01 systemd[1]: Started OpenSSH server.\n', 0o640, 'syslog', 'adm'),
        HOME + '/support': _d(),
        HOME + '/support/backup.sh': _f('#!/bin/bash\necho "Backup of ~/support complete: 3 files copied to /tmp/backup"\n', 0o644),
        HOME + '/support/report.txt': _f('Quarterly support report - internal only\nOpen tickets: 14\n', 0o644),
        HOME + '/support/app.log': _f('09:00 INFO service started\n09:05 INFO user login ok\n09:12 ERROR disk quota exceeded for /srv/share\n'
                                     '09:13 INFO retry scheduled\n09:20 WARN slow response 2300ms\n', 0o644),
        HOME + '/.bashrc': _f('# ~/.bashrc\nalias ll="ls -l"\n'),
        HOME + '/Documents': _d(),
    }
    st = {'fs': fs, 'cwd': HOME, 'user': 'trainee', 'host': 'novak-lnx-01', 'hist': [], 'ip': '10.20.40.15'}
    st.update(extra)
    return st


def prompt(state):
    cwd = state.get('cwd', HOME)
    short = '~' + cwd[len(HOME):] if cwd.startswith(HOME) else cwd
    return f"{state.get('user', 'trainee')}@{state.get('host', 'novak-lnx-01')}:{short}$"


def _abs(state, p):
    if not p:
        return state['cwd']
    if p == '~' or p.startswith('~/'):
        p = HOME + p[1:]
    if not p.startswith('/'):
        p = posixpath.join(state['cwd'], p)
    p = posixpath.normpath(p)
    return '/' if p in ('', '//') else p


def _perm_str(node):
    m = node['mode']
    s = 'd' if node['t'] == 'd' else '-'
    for shift in (6, 3, 0):
        b = (m >> shift) & 7
        s += ('r' if b & 4 else '-') + ('w' if b & 2 else '-') + ('x' if b & 1 else '-')
    return s


def _can(state, node, bit, sudo=False):
    if sudo or state.get('user') == 'root':
        return True
    m = node['mode']
    if node['owner'] == state.get('user'):
        return bool((m >> 6) & bit)
    if node['group'] in ('trainee',):
        return bool((m >> 3) & bit)
    return bool(m & bit)


def _children(fs, d):
    pref = d.rstrip('/') + '/'
    return sorted(k[len(pref):] for k in fs if k.startswith(pref) and k != d and '/' not in k[len(pref):])


def _chmod(mode, spec):
    if re.fullmatch(r'[0-7]{3,4}', spec):
        return int(spec[-3:], 8)
    out = mode
    for part in spec.split(','):
        m = re.fullmatch(r'([ugoa]*)([+\-=])([rwx]+)', part)
        if not m:
            return None
        who, op, perms = m.groups()
        who = who or 'a'
        bits = (4 if 'r' in perms else 0) | (2 if 'w' in perms else 0) | (1 if 'x' in perms else 0)
        for w in ('u', 'g', 'o'):
            if w in who or 'a' in who:
                shift = {'u': 6, 'g': 3, 'o': 0}[w]
                if op == '+':
                    out |= bits << shift
                elif op == '-':
                    out &= ~(bits << shift)
                else:
                    out = (out & ~(7 << shift)) | (bits << shift)
    return out


WIN_HINTS = {
    'ipconfig': 'On Linux use: ip addr  (or hostname -I)', 'dir': 'On Linux use: ls   (ls -l shows permissions, owner and size)', 'cls': 'On Linux use: clear  (or Ctrl-L)',
    'type': 'On Linux use: cat <file>', 'del': 'On Linux use: rm <file>', 'copy': 'On Linux use: cp <src> <dest>',
    'move': 'On Linux use: mv <src> <dest>', 'md': 'On Linux use: mkdir <dir>', 'tasklist': 'On Linux use: ps aux',
    'icacls': 'On Linux use: ls -l to read and chmod to change permissions', 'findstr': 'On Linux use: grep <pattern> <file>',
    'ifconfig': None, 'get-childitem': 'On Linux use: ls', 'systeminfo': 'On Linux use: uname -a  and  hostnamectl',
}
COMMANDS = ['pwd', 'ls', 'll', 'cd', 'mkdir', 'rmdir', 'touch', 'cat', 'echo', 'cp', 'mv', 'rm', 'chmod', 'chown', 'whoami',
            'id', 'hostname', 'ip', 'ifconfig', 'df', 'free', 'uname', 'grep', 'head', 'tail', 'history', 'clear', 'man',
            'help', 'sudo', 'ps', 'which', 'file', 'wc', 'systemctl', 'date', 'uptime']


def run(cmd, state, done, mark, rules):
    """Run one line. ``rules(state, done, event)`` lets the lab award objectives."""
    raw = cmd.strip()
    out = []
    state.setdefault('hist', []).append(raw)
    state['hist'] = state['hist'][-50:]
    # redirection: echo "x" > file / >> file
    redirect = None
    m = re.match(r'^(.*?)(>>|>)\s*(\S+)\s*$', raw)
    if m and not raw.startswith('grep'):
        raw, redirect = m.group(1).strip(), (m.group(2), m.group(3))
    try:
        parts = shlex.split(raw)
    except ValueError:
        return ['bash: syntax error: unmatched quote'], True
    if not parts:
        return [], False
    sudo = False
    if parts[0] == 'sudo':
        sudo = True
        parts = parts[1:]
        if not parts:
            return ['usage: sudo <command>'], True
        out.append('[sudo] password for trainee: (accepted for the lab)')
        rules(state, done, ('sudo', parts[0]))
    name, args = parts[0], parts[1:]
    if name == 'll':
        name, args = 'ls', ['-l'] + args
    flags = ''.join(a[1:] for a in args if a.startswith('-') and len(a) > 1)
    paths = [a for a in args if not a.startswith('-')]
    fs = state['fs']
    unknown = False

    def missing(cmdname, p):
        return f"{cmdname}: cannot access '{p}': No such file or directory"

    if name in ('help', 'man'):
        out += ['Linux lab shell — supported commands:',
                '  where am I / what is here : pwd  ls [-l] [-a] [path]  cd <dir>  cd ..  cd ~',
                '  files                     : touch f  mkdir [-p] d  cat f  echo "text" > f  echo "more" >> f  cp  mv  rm [-r]',
                '  permissions               : ls -l f   chmod u+x f   chmod o-r f   chmod 640 f   sudo chown user f',
                '  facts                     : whoami  id  hostname  ip addr  df -h  free -h  uname -a  ps aux',
                '  search                    : grep [-i] [-n] pattern file   head/tail file   wc -l file',
                '  run a script              : ./script.sh  (needs execute permission)',
                'Tab completes commands and paths. Up/Down recall history. Ctrl-C cancels a line, Ctrl-L clears.']
    elif name == 'pwd':
        out.append(state['cwd'])
        rules(state, done, ('pwd', state['cwd']))
    elif name == 'whoami':
        out.append('root' if sudo else state['user'])
        rules(state, done, ('whoami',))
    elif name == 'id':
        out.append('uid=1000(trainee) gid=1000(trainee) groups=1000(trainee),27(sudo)')
        rules(state, done, ('whoami',))
    elif name == 'hostname':
        out.append(state['ip'] if '-I' in args else state['host'])
        rules(state, done, ('hostname',))
    elif name == 'uname':
        out.append('Linux novak-lnx-01 6.8.0-45-generic #45-Ubuntu SMP x86_64 GNU/Linux' if 'a' in flags else 'Linux')
    elif name in ('ip', 'ifconfig'):
        if name == 'ip' and (not args or args[0] not in ('a', 'addr', 'address', 'r', 'route')):
            out.append('Usage: ip addr   |   ip route')
        elif name == 'ip' and args[0] in ('r', 'route'):
            out += ['default via 10.20.40.1 dev ens33 proto dhcp metric 100', '10.20.40.0/24 dev ens33 proto kernel scope link src 10.20.40.15']
        else:
            out += ['1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536', '    inet 127.0.0.1/8 scope host lo',
                    '2: ens33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500', '    link/ether 00:0c:29:4f:8e:35 brd ff:ff:ff:ff:ff:ff',
                    f"    inet {state['ip']}/24 brd 10.20.40.255 scope global dynamic ens33"]
            rules(state, done, ('ipaddr',))
    elif name == 'df':
        out += ['Filesystem      Size  Used Avail Use% Mounted on', '/dev/sda2        40G   31G  7.1G  82% /',
                'tmpfs           1.9G     0  1.9G   0% /dev/shm'] if 'h' in flags else ['Filesystem 1K-blocks Used Available Use% Mounted on',
                                                                                   '/dev/sda2 41152736 32505856 7445248 82% /']
        rules(state, done, ('df',))
    elif name == 'free':
        out += ['               total        used        free      shared  buff/cache   available',
                'Mem:           3.8Gi       1.9Gi       410Mi        24Mi       1.5Gi       1.6Gi', 'Swap:          2.0Gi       0.1Gi       1.9Gi']
    elif name == 'uptime':
        out.append(' 10:14:02 up 3 days,  2:11,  1 user,  load average: 0.21, 0.18, 0.12')
    elif name == 'date':
        out.append('Sat Oct 17 10:14:02 UTC 2026')
    elif name == 'ps':
        out += ['USER         PID %CPU %MEM COMMAND', 'root           1  0.0  0.3 /sbin/init', 'root         812  0.0  0.2 /usr/sbin/sshd -D',
                'trainee     1440  0.0  0.1 -bash']
    elif name == 'systemctl':
        svc = (paths[1] if len(paths) > 1 else 'ssh')
        out += [f'● {svc}.service - {svc}', '     Loaded: loaded', '     Active: active (running) since Wed 2026-10-14 08:03:11 UTC']
    elif name == 'which':
        for p in paths:
            out.append(f'/usr/bin/{p}' if p in COMMANDS else f'{p} not found')
    elif name == 'history':
        out += [f'{i + 1:>5}  {h}' for i, h in enumerate(state['hist'])]
    elif name == 'cd':
        target = _abs(state, paths[0] if paths else '~')
        if paths and paths[0] == '-':
            target = state.get('oldpwd', state['cwd'])
        node = fs.get(target)
        if node is None:
            out.append(f"bash: cd: {paths[0]}: No such file or directory")
        elif node['t'] != 'd':
            out.append(f"bash: cd: {paths[0]}: Not a directory")
        elif not _can(state, node, 1, sudo):
            out.append(f"bash: cd: {paths[0]}: Permission denied")
        else:
            state['oldpwd'], state['cwd'] = state['cwd'], target
            rules(state, done, ('cd', target))
    elif name == 'ls':
        targets = paths or ['.']
        long_ = 'l' in flags
        all_ = 'a' in flags
        for p in targets:
            ap = _abs(state, p)
            node = fs.get(ap)
            if node is None:
                out.append(missing('ls', p))
                continue
            if node['t'] == 'd' and not _can(state, node, 4, sudo):
                out.append(f"ls: cannot open directory '{p}': Permission denied")
                continue
            names = _children(fs, ap) if node['t'] == 'd' else [posixpath.basename(ap)]
            if not all_:
                names = [n for n in names if not n.startswith('.')]
            if len(targets) > 1:
                out.append(f'{p}:')
            if long_:
                if node['t'] == 'd':
                    out.append(f'total {len(names) * 4}')
                for n in names:
                    full = ap if node['t'] != 'd' else posixpath.join(ap, n)
                    nd = fs[full]
                    size = len(nd.get('c', '')) if nd['t'] == 'f' else 4096
                    out.append(f"{_perm_str(nd)} 1 {nd['owner']:<7} {nd['group']:<7} {size:>5} Oct 17 09:30 {n}{'/' if nd['t'] == 'd' else ''}")
                rules(state, done, ('ls-l', ap, names))
            else:
                out.append('  '.join(n + ('/' if fs[posixpath.join(ap, n) if node['t'] == 'd' else ap]['t'] == 'd' else '') for n in names) or '')
                rules(state, done, ('ls', ap))
    elif name == 'mkdir':
        if not paths:
            out.append('mkdir: missing operand')
        for p in paths:
            ap = _abs(state, p)
            parent = posixpath.dirname(ap)
            if ap in fs:
                out.append(f"mkdir: cannot create directory '{p}': File exists")
            elif parent not in fs:
                if 'p' in flags:
                    cur = ''
                    for seg in ap.strip('/').split('/'):
                        cur += '/' + seg
                        fs.setdefault(cur, _d())
                    rules(state, done, ('mkdir', ap))
                else:
                    out.append(f"mkdir: cannot create directory '{p}': No such file or directory")
            elif not _can(state, fs[parent], 2, sudo):
                out.append(f"mkdir: cannot create directory '{p}': Permission denied")
            else:
                fs[ap] = _d(owner='root' if sudo else 'trainee', group='root' if sudo else 'trainee')
                rules(state, done, ('mkdir', ap))
    elif name == 'rmdir':
        for p in paths:
            ap = _abs(state, p)
            if ap not in fs:
                out.append(f"rmdir: failed to remove '{p}': No such file or directory")
            elif _children(fs, ap):
                out.append(f"rmdir: failed to remove '{p}': Directory not empty")
            else:
                del fs[ap]
    elif name == 'touch':
        if not paths:
            out.append('touch: missing file operand')
        for p in paths:
            ap = _abs(state, p)
            parent = posixpath.dirname(ap)
            if parent not in fs:
                out.append(f"touch: cannot touch '{p}': No such file or directory")
            elif ap not in fs:
                if not _can(state, fs[parent], 2, sudo):
                    out.append(f"touch: cannot touch '{p}': Permission denied")
                else:
                    fs[ap] = _f('')
                    rules(state, done, ('create', ap))
    elif name == 'echo':
        text = ' '.join(args)
        if redirect:
            op, target = redirect
            ap = _abs(state, target)
            parent = posixpath.dirname(ap)
            if parent not in fs:
                out.append(f"bash: {target}: No such file or directory")
            elif ap in fs and fs[ap]['t'] == 'd':
                out.append(f"bash: {target}: Is a directory")
            elif ap in fs and not _can(state, fs[ap], 2, sudo):
                out.append(f"bash: {target}: Permission denied")
            elif ap not in fs and not _can(state, fs[parent], 2, sudo):
                out.append(f"bash: {target}: Permission denied")
            else:
                node = fs.setdefault(ap, _f(''))
                node['c'] = (node['c'] if op == '>>' else '') + text + '\n'
                rules(state, done, ('write', ap, node['c']))
        else:
            out.append(text)
    elif name in ('cat', 'head', 'tail', 'wc', 'file'):
        if not paths:
            out.append(f'{name}: missing file operand')
        for p in paths:
            if name in ('head', 'tail') and p.isdigit():
                continue
            ap = _abs(state, p)
            node = fs.get(ap)
            if node is None:
                out.append(f"{name}: {p}: No such file or directory")
            elif node['t'] == 'd':
                out.append(f"{name}: {p}: Is a directory")
            elif not _can(state, node, 4, sudo):
                out.append(f"{name}: {p}: Permission denied")
            else:
                lines = node['c'].rstrip('\n').split('\n') if node['c'] else []
                if name == 'cat':
                    out += lines
                    rules(state, done, ('cat', ap))
                elif name == 'head':
                    out += lines[:10]
                elif name == 'tail':
                    out += lines[-10:]
                elif name == 'wc':
                    out.append(f"{len(lines)} {p}" if 'l' in flags else f" {len(lines)} {len(node['c'].split())} {len(node['c'])} {p}")
                else:
                    out.append(f"{p}: {'Bourne-Again shell script, ASCII text executable' if node['c'].startswith('#!') else 'ASCII text'}")
    elif name == 'grep':
        if len(paths) < 2:
            out.append('Usage: grep [OPTION]... PATTERNS [FILE]...')
        else:
            pat, files = paths[0], paths[1:]
            for p in files:
                ap = _abs(state, p)
                node = fs.get(ap)
                if node is None:
                    out.append(f"grep: {p}: No such file or directory")
                    continue
                if not _can(state, node, 4, sudo):
                    out.append(f"grep: {p}: Permission denied")
                    continue
                hits = []
                for i, ln in enumerate(node['c'].split('\n')):
                    if (pat.lower() in ln.lower()) if 'i' in flags else (pat in ln):
                        hits.append((f'{i + 1}:' if 'n' in flags else '') + ln)
                out += hits
                rules(state, done, ('grep', ap, pat, hits))
    elif name in ('cp', 'mv'):
        if len(paths) < 2:
            out.append(f'{name}: missing destination file operand')
        else:
            src, dst = _abs(state, paths[0]), _abs(state, paths[1])
            if src not in fs:
                out.append(f"{name}: cannot stat '{paths[0]}': No such file or directory")
            else:
                if dst in fs and fs[dst]['t'] == 'd':
                    dst = posixpath.join(dst, posixpath.basename(src))
                if posixpath.dirname(dst) not in fs:
                    out.append(f"{name}: cannot create regular file '{paths[1]}': No such file or directory")
                elif fs[src]['t'] == 'd' and name == 'cp' and 'r' not in flags.lower():
                    out.append(f"cp: -r not specified; omitting directory '{paths[0]}'")
                else:
                    moved = {k: dict(v) for k, v in fs.items() if k == src or k.startswith(src + '/')}
                    for k, v in moved.items():
                        fs[dst + k[len(src):]] = v
                    if name == 'mv':
                        for k in moved:
                            del fs[k]
                    rules(state, done, (name, src, dst))
    elif name == 'rm':
        if not paths:
            out.append('rm: missing operand')
        for p in paths:
            ap = _abs(state, p)
            if ap not in fs:
                out.append(f"rm: cannot remove '{p}': No such file or directory")
            elif fs[ap]['t'] == 'd' and 'r' not in flags.lower():
                out.append(f"rm: cannot remove '{p}': Is a directory")
            elif ap in (HOME, '/', HOME + '/support'):
                out.append(f"rm: refusing to remove '{p}' in this lab (it holds the files the ticket is about)")
            else:
                for k in [k for k in fs if k == ap or k.startswith(ap + '/')]:
                    del fs[k]
                rules(state, done, ('rm', ap))
    elif name == 'chmod':
        if len(paths) < 2:
            out.append('chmod: missing operand' if not paths else f"chmod: missing operand after '{paths[0]}'")
        else:
            spec = paths[0]
            for p in paths[1:]:
                ap = _abs(state, p)
                node = fs.get(ap)
                if node is None:
                    out.append(f"chmod: cannot access '{p}': No such file or directory")
                elif node['owner'] != state['user'] and not sudo:
                    out.append(f"chmod: changing permissions of '{p}': Operation not permitted")
                else:
                    new = _chmod(node['mode'], spec)
                    if new is None:
                        out.append(f"chmod: invalid mode: '{spec}'")
                        out.append("Try: chmod u+x file   chmod o-r file   chmod 640 file")
                    else:
                        node['mode'] = new
                        rules(state, done, ('chmod', ap, new))
    elif name == 'chown':
        if len(paths) < 2:
            out.append('chown: missing operand')
        elif not sudo:
            out.append(f"chown: changing ownership of '{paths[1]}': Operation not permitted")
            out.append('(Changing the owner needs root: sudo chown user:group file)')
        else:
            owner = paths[0]
            for p in paths[1:]:
                ap = _abs(state, p)
                if ap not in fs:
                    out.append(f"chown: cannot access '{p}': No such file or directory")
                else:
                    u, _, g = owner.partition(':')
                    fs[ap]['owner'] = u or fs[ap]['owner']
                    if g:
                        fs[ap]['group'] = g
                    rules(state, done, ('chown', ap))
    elif name.startswith('./') or name.startswith('/') or name.startswith('~/'):
        ap = _abs(state, name)
        node = fs.get(ap)
        if node is None:
            out.append(f"bash: {name}: No such file or directory")
        elif node['t'] == 'd':
            out.append(f"bash: {name}: Is a directory")
        elif not _can(state, node, 1, sudo):
            out.append(f"bash: {name}: Permission denied")
            out.append("(The file is not executable for you. Check with ls -l; owner execute is the 3rd character.)")
            rules(state, done, ('exec-denied', ap))
        else:
            for ln in node['c'].split('\n'):
                mm = re.match(r'^echo "(.*)"$', ln.strip())
                if mm:
                    out.append(mm.group(1))
            rules(state, done, ('exec', ap))
    elif name in ('bash', 'sh') and paths:
        ap = _abs(state, paths[0])
        if ap in fs:
            out.append('(Running a script through bash works without execute permission, but the ticket asks you to make it executable: chmod u+x)')
        else:
            out.append(f"bash: {paths[0]}: No such file or directory")
    else:
        unknown = True
        hint = WIN_HINTS.get(name.lower())
        out.append(f"{name}: command not found")
        if hint:
            out.append(hint)
        else:
            close = [c for c in COMMANDS if c.startswith(name[:2])] if len(name) >= 2 else []
            if close:
                out.append('Did you mean: ' + ', '.join(close[:4]) + '?  Type help for the list.')
            else:
                out.append('Type help for the commands this lab supports.')
    return out, unknown


def complete(state, partial):
    """Complete the command (first word) or a path (later words)."""
    raw = partial or ''
    if ' ' not in raw.strip() and not raw.endswith(' '):
        opts = [c for c in COMMANDS if c.startswith(raw.strip())]
        if len(opts) == 1:
            return {'text': opts[0] + ' ', 'options': opts, 'beep': False}
        return {'text': raw, 'options': opts, 'beep': len(opts) != 1}
    head, _, last = raw.rpartition(' ')
    d, _, pref = last.rpartition('/')
    base = _abs(state, d if d or last.startswith('/') else '.') if d or last.startswith('/') else state['cwd']
    if last.startswith('/') and not d:
        base = '/'
    fs = state['fs']
    if base not in fs:
        return {'text': raw, 'options': [], 'beep': True}
    names = [n for n in _children(fs, base) if n.startswith(pref) and (pref.startswith('.') or not n.startswith('.'))]
    names = [n + ('/' if fs[posixpath.join(base, n)]['t'] == 'd' else '') for n in names]
    if len(names) == 1:
        new_last = (d + '/' if d or last.startswith('/') else '') + names[0]
        return {'text': head + ' ' + new_last + ('' if names[0].endswith('/') else ' '), 'options': names, 'beep': False}
    if len(names) > 1:
        common = names[0]
        for n in names[1:]:
            i = 0
            while i < min(len(common), len(n)) and common[i] == n[i]:
                i += 1
            common = common[:i]
        new_last = (d + '/' if d or last.startswith('/') else '') + common
        return {'text': head + ' ' + new_last, 'options': names, 'beep': True}
    return {'text': raw, 'options': [], 'beep': True}


def near_names(state, missing):
    """Names close to a path that was not found (case differences, prefixes) — for 'Did you mean' help."""
    ap = _abs(state, missing)
    parent, _, base = ap.rpartition('/')
    parent = parent or '/'
    fs = state['fs']
    if parent not in fs or not base:
        return []
    kids = _children(fs, parent)
    lo = base.lower()
    out = [k for k in kids if k.lower() == lo and k != base]
    out += [k for k in kids if k.lower().startswith(lo) and k not in out and k != base]
    return out[:3]
