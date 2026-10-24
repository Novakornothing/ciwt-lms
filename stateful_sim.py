"""Shared stateful OS & network fallback engine (Option B, pass 1). Pending SME review.

Every simulated Windows and Cisco IOS lab answers standard diagnostic commands from the lab's *live* state, even when
the lab's own step script does not list them, and the packet-flow walk evaluates the same state hop by hop.
Read-only except `ip default-gateway` on a switch, which is recorded so later commands reflect it."""
import ipaddress
import re

WIN_HANDLED = ('test-netconnection', 'tnc ', 'whoami /priv')
IOS_SW = {'show startup-config', 'show ip route', 'show access-lists', 'show ip access-lists', 'show arp',
          'show cdp neighbors'}
IOS_RTR = {'show cdp neighbors'}
PACKETS = {'arp': 'ARP Request', 'icmp': 'ICMP Echo (Ping)', 'dns': 'DNS Query (UDP 53)', 'https': 'HTTPS (TCP 443)'}


# ------------------------------------------------------------------ helpers
def _ip(s):
    try:
        return ipaddress.ip_address(s)
    except ValueError:
        return None


def _resolve(state, target):
    t = (target or '').strip().lower()
    if _ip(t):
        return t
    nm = {k.lower(): v for k, v in (state.get('name_map') or {}).items()}
    return nm.get(t) or nm.get(t + '.training.local')


def _win_live(state):
    ip = state.get('ipv4') or ''
    return bool(ip) and not state.get('released') and not ip.startswith('169.254')


def _reach(state, ip):
    return _win_live(state) and ip in (state.get('pingable_ips') or [])


# ------------------------------------------------------------------ Windows
def windows(cmd, state):
    """Lines for a Windows command the lab engine does not cover, else None."""
    c = re.sub(r'\s+', ' ', (cmd or '').strip())
    cl = c.lower()
    if cl == 'whoami /priv':
        admin = bool(state.get('elevated'))
        rows = [('SeShutdownPrivilege', 'Shut down the system', 'Disabled'),
                ('SeChangeNotifyPrivilege', 'Bypass traverse checking', 'Enabled'),
                ('SeUndockPrivilege', 'Remove computer from docking station', 'Disabled'),
                ('SeIncreaseWorkingSetPrivilege', 'Increase a process working set', 'Disabled'),
                ('SeTimeZonePrivilege', 'Change the time zone', 'Disabled')]
        if admin:
            rows += [('SeDebugPrivilege', 'Debug programs', 'Disabled'), ('SeBackupPrivilege', 'Back up files and directories', 'Disabled')]
        out = ['', 'PRIVILEGES INFORMATION', '----------------------', '',
               f'{"Privilege Name":<30} {"Description":<38} State', f'{"=" * 30} {"=" * 38} ========']
        return out + [f'{a:<30} {b:<38} {s}' for a, b, s in rows]
    if cl.startswith(('test-netconnection', 'tnc ')) or cl == 'tnc':
        parts = c.split()[1:]
        port = None
        if '-port' in [p.lower() for p in parts]:
            i = [p.lower() for p in parts].index('-port')
            port = parts[i + 1] if i + 1 < len(parts) else None
            parts = parts[:i] + parts[i + 2:]
        parts = [p for p in parts if not p.startswith('-')]
        target = parts[0] if parts else 'internetbeacon.msedge.net'
        ip = _resolve(state, target)
        alias = 'Ethernet'
        if not ip:
            return [f'WARNING: Name resolution of {target} failed', '', f'ComputerName   : {target}',
                    f'RemoteAddress  :', f'InterfaceAlias : {alias}', f'SourceAddress  : {state.get("ipv4")}',
                    'PingSucceeded  : False']
        ok = _reach(state, ip)
        out = ['', f'ComputerName           : {target}', f'RemoteAddress          : {ip}']
        if port:
            dns = ip in (state.get('dns') or [])
            open_ = ok and ((port == '53' and dns) or port in ('80', '443', '445', '3389') and not dns
                            or str(port) in [str(p) for p in (state.get('open_ports') or {}).get(ip, [])])
            if not open_:
                out.insert(0, f'WARNING: TCP connect to ({ip} : {port}) failed')
            return out + [f'RemotePort             : {port}', f'InterfaceAlias         : {alias}',
                          f'SourceAddress          : {state.get("ipv4")}', f'TcpTestSucceeded       : {open_}']
        if not ok:
            out.insert(0, f'WARNING: Ping to {ip} failed with status: TimedOut')
        return out + [f'InterfaceAlias         : {alias}', f'SourceAddress          : {state.get("ipv4")}',
                      f'PingSucceeded          : {ok}'] + ([f'PingReplyDetails (RTT) : 1 ms'] if ok else [])
    return None


# ------------------------------------------------------------------ Cisco IOS
def _sw_gateway(state):
    return state.get('default_gateway')


def ios(kind, cmd, state, done):
    """Lines for an IOS command the lab engine does not cover, else None. May record `ip default-gateway`."""
    cl = re.sub(r'\s+', ' ', (cmd or '').strip().lower())
    if cl.startswith('do '):
        cl = cl[3:]
    mode = state.get('mode') or 'user'
    if kind == 'switch' and mode == 'config' and cl.startswith('ip default-gateway '):
        state['default_gateway'] = cl.split()[-1]
        return None                        # the engine still prints its own (empty) reply
    if mode == 'user' and cl.startswith('show ') and cl not in ('show version', 'show ip interface brief', 'show vlan brief',
                                                             'show interfaces status', 'show cdp neighbors', 'show arp'):
        return None
    host = state.get('hostname') or ('SW1' if kind == 'switch' else 'R1')
    if kind == 'switch':
        if cl == 'show startup-config':
            if not state.get('startup'):
                return ['startup-config is not present']
            return ['Using 1520 out of 65536 bytes', '!'] + list(state.get('startup_cfg') or [f'hostname {host}']) + ['end']
        if cl == 'show ip route':
            gw = _sw_gateway(state)
            return [f'Default gateway is {gw}' if gw else 'Default gateway is not set', '',
                    'Host               Gateway           Last Use    Total Uses  Interface',
                    'ICMP redirect cache is empty']
        if cl in ('show access-lists', 'show ip access-lists'):
            return []
        if cl == 'show arp':
            mgmt = state.get('mgmt_ip')
            gw = _sw_gateway(state)
            out = ['Protocol  Address          Age (min)  Hardware Addr   Type   Interface']
            if mgmt:
                out.append(f'Internet  {mgmt:<16} -          0019.e8a4.1c01  ARPA   Vlan1')
            if gw:
                out.append(f'Internet  {gw:<16} 0          0019.e8a4.9901  ARPA   Vlan1')
            return out
        if cl == 'show cdp neighbors':
            up = next((p for p, c in (state.get('interfaces') or {}).items() if c.get('mode') == 'trunk' or c.get('trunk')), None)
            out = ['Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge',
                   '                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone', '',
                   'Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID']
            if up:
                out.append(f'R1               {_short(up):<17} 152        R S I       ISR4331   Gig 0/1')
            return out
        if cl.startswith('traceroute '):
            t = cl.split()[1]
            gw = _sw_gateway(state)
            out = ['Type escape sequence to abort.', f'Tracing the route to {t}', '']
            return out + ([f'  1 {gw} 1 msec 1 msec 1 msec', f'  2 {t} 2 msec 1 msec 2 msec'] if gw
                          else ['  1  *  *  *', '% No default gateway: set ip default-gateway on the switch first.'])
    if kind == 'router' and cl == 'show cdp neighbors':
        out = ['Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge',
               '                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone', '',
               'Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID']
        for name, cfg in (state.get('interfaces') or {}).items():
            if '.' not in name and cfg.get('up'):
                out.append(f'SW-ACCESS-01     {_short(name):<17} 163        S I         WS-C2960  Fas 0/1')
                break
        return out
    return None


def _short(ifname):
    return ifname.replace('GigabitEthernet', 'Gig ').replace('FastEthernet', 'Fas ')


# ------------------------------------------------------------------ packet flow
def _hop(n, label, ok, detail):
    return {'n': n, 'label': label, 'ok': ok, 'detail': detail}


def _win_hops(state, ptype):
    hops = []
    ip, gw, dns = state.get('ipv4'), state.get('gateway'), (state.get('dns') or [None])[0]
    if not _win_live(state):
        why = 'adapter released' if state.get('released') else f'APIPA {ip} — no DHCP lease' if (ip or '').startswith('169.254') else 'no IPv4 address'
        return [_hop(1, 'L2 frame from the client', False, f'Dropped at Hop 1: {why}')]
    hops.append(_hop(1, 'L2 frame from the client', True, f'{ip}/{state.get("mask")} on the access VLAN'))
    gw_ok = bool(gw) and gw in (state.get('pingable_ips') or [])
    hops.append(_hop(2, 'Default gateway (ARP + L3 lookup)', gw_ok,
                     f'Gateway {gw} answers ARP' if gw_ok else f'Dropped at Hop 2: default gateway {gw or "(none)"} does not answer'))
    if not gw_ok or ptype == 'arp':
        return hops
    hops.append(_hop(3, 'Edge router ACL / NAT', True, 'No ACL denies this flow; NAT translates to the public address'))
    if ptype in ('dns', 'https'):
        svc = state.get('services') or {}
        ok = bool(dns) and dns in (state.get('pingable_ips') or []) and svc.get('Dnscache', 'Running') == 'Running'
        hops.append(_hop(4, f'DNS server {dns}', ok, f'{dns} answers UDP 53' if ok else f'Timed out at DNS {dns}'))
        if not ok or ptype == 'dns':
            return hops
        hops.append(_hop(5, 'Target server (TCP 443)', True, 'TLS handshake completes'))
        return hops
    tgt = next((x for x in (state.get('pingable_ips') or []) if x not in (ip, gw, '127.0.0.1')), gw)
    hops.append(_hop(4, f'Target reply ({tgt})', True, 'Echo reply received'))
    return hops


def _sw_hops(state, ptype):
    ifs = state.get('interfaces') or {}
    vlans = {int(k) for k in (state.get('vlans') or {1: 'default'})}
    access = [(p, c) for p, c in ifs.items() if c.get('mode') != 'trunk' and not c.get('trunk')]
    trunk = next(((p, c) for p, c in ifs.items() if c.get('mode') == 'trunk' or c.get('trunk')), None)
    p, c = (access[-1] if access else ('Fa0/2', {'vlan': 1, 'up': True}))
    v = int(c.get('vlan') or 1)
    if not c.get('up', True):
        return [_hop(1, 'L2 frame & VLAN tag', False, f'Dropped at Hop 1: {p} is down (shutdown?)')]
    if v not in vlans:
        return [_hop(1, 'L2 frame & VLAN tag', False, f'Dropped at Hop 1: VLAN {v} does not exist on the switch')]
    hops = [_hop(1, 'L2 frame & VLAN tag', True, f'{p} access VLAN {v}')]
    if not trunk:
        hops.append(_hop(2, 'Uplink trunk to the gateway', False, 'Dropped at Hop 2: no trunk uplink (switchport mode trunk)'))
        return hops
    tp, tc = trunk
    al = tc.get('allowed')
    if al and v not in al:
        hops.append(_hop(2, 'Uplink trunk to the gateway', False, f'Dropped at Hop 2: VLAN {v} not allowed on trunk {tp}'))
        return hops
    hops.append(_hop(2, 'Uplink trunk to the gateway', True, f'{tp} carries VLAN {v} (802.1Q)'))
    if ptype == 'arp':
        return hops
    hops.append(_hop(3, 'Edge router ACL / NAT', True, 'Inter-VLAN routing on the router'))
    hops.append(_hop(4, 'Target reply', True, 'Reply returns on the same VLAN'))
    return hops


def _rtr_hops(state, ptype):
    ifs = {k: v for k, v in (state.get('interfaces') or {}).items()}
    lan = [(k, v) for k, v in ifs.items() if v.get('ip')]
    if not lan or not any(v.get('up') for _k, v in lan):
        down = next(iter(ifs), 'Gi0/0')
        return [_hop(1, 'L2 frame to the router LAN port', False, f'Dropped at Hop 1: {down} has no address or is shutdown')]
    hops = [_hop(1, 'L2 frame to the router LAN port', True, ', '.join(f'{k} {v["ip"]}' for k, v in lan if v.get('up')))]
    if ptype == 'arp':
        return hops
    static = [r.lower() for r in state.get('static') or []]
    has_default = any(r.startswith('route 0.0.0.0 0.0.0.0') or r.startswith('ip route 0.0.0.0 0.0.0.0') for r in static)
    up_count = sum(1 for _k, v in lan if v.get('up'))
    if up_count < 2 and not has_default:
        hops.append(_hop(2, 'Gateway L3 lookup', False, 'Dropped at Hop 2: no route to the destination (no second interface or default route)'))
        return hops
    hops.append(_hop(2, 'Gateway L3 lookup', True, 'Default route' if has_default else 'Directly connected route'))
    denied = [(k, v) for k, v in ifs.items() for d in ('in', 'out') if v.get('acl_' + d)
              and any(e.get('action') == 'deny' for e in (state.get('acls') or {}).get(v['acl_' + d], []))
              and not any(e.get('action') == 'permit' for e in (state.get('acls') or {}).get(v['acl_' + d], []))]
    if denied:
        hops.append(_hop(3, 'ACL / NAT evaluation', False, f'Dropped at Hop 3: ACL {denied[0][1].get("acl_in") or denied[0][1].get("acl_out")} on {denied[0][0]} has no permit (implicit deny)'))
        return hops
    hops.append(_hop(3, 'ACL / NAT evaluation', True, 'Permitted'))
    hops.append(_hop(4, 'Target reply', True, 'Reply routed back'))
    return hops


def packet_flow(lab, state, done, ptype='icmp'):
    ptype = ptype if ptype in PACKETS else 'icmp'
    kind = lab.get('kind')
    state = state or {}
    if kind == 'switch':
        hops = _sw_hops(state, ptype)
    elif kind == 'router':
        hops = _rtr_hops(state, ptype)
    elif kind in ('windows', 'win11gui'):
        hops = _win_hops(state, ptype)
    else:
        need = {o['id'] for o in lab.get('objectives') or []}
        fixed = need <= set(done or [])
        hops = [_hop(1, 'L2 frame & VLAN', True, 'Client on its access VLAN'),
                _hop(2, 'Default gateway', fixed, 'Gateway answers' if fixed else 'Stopped at Hop 2: finish the lab fix, then trace again')]
        if fixed:
            hops += [_hop(3, 'ACL / NAT', True, 'Permitted'), _hop(4, 'Target reply', True, 'Reply received')]
    ok = all(h['ok'] for h in hops)
    bad = next((h for h in hops if not h['ok']), None)
    return {'packet': PACKETS[ptype], 'type': ptype, 'hops': hops, 'ok': ok,
            'summary': ('✓ Delivered end-to-end' if ok else '✗ ' + bad['detail']),
            'topology': ['Client PC', 'Access switch (VLAN)', 'Edge router (gateway / NAT / ACL)', 'DNS / target server']}


NETWORK_KINDS = ('switch', 'router', 'windows', 'win11gui')
NETWORK_IDS = ('net-subnet',)


def has_packet_flow(lab):
    lid = lab.get('id', '')
    return (lab.get('kind') in NETWORK_KINDS and not lid.startswith(('w11-disk', 'w11-processes', 'gui-about', 'gui-update', 'gui-accounts', 'gui-devices', 'win-ad-users', 'print-trouble'))) \
        or lid in NETWORK_IDS or lid.startswith(('scn-dns-', 'scn-lan2-'))


HW_IDS = ('hw-board', 'hw-pc-build', 'hw-cables')
