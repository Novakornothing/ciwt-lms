"""Windows 11 GUI simulator: server-side event model.

The page sends user actions as events (``open:settings``, ``pane:about``, ``adapter:disable``,
``svc:Dhcp``, ``ad:create`` …). The server keeps the desktop state (open window, Settings page,
adapter state, the Active Directory directory), awards objectives from per-lab rules and returns the
state so a reload restores the same window and page.
"""
import re
from copy import deepcopy

DEFAULT_RULES = {
    'open_settings': 'open:settings', 'open_system': 'pane:system', 'open_about': 'pane:about',
    'open_network': 'pane:network', 'open_ethernet': 'pane:ethernet', 'open_update': 'pane:update',
    'open_accounts': 'pane:accounts', 'open_services': 'open:services', 'find_dhcp': 'svc:Dhcp',
    'find_dns': 'svc:Dnscache', 'find_defend': 'svc:WinDefend', 'open_devmgr': 'open:devmgr',
    'find_nic': 'dev:net', 'find_display': 'dev:display', 'check_updates': 'update:check',
    'open_adapters': ('any', 'pane:advanced', 'open:ncpa'),
    'toggle_lease': ('after', 'adapter:disable', 'adapter:enable'),
    'open_aduc': 'open:aduc',
}
# per-lab overrides for the original GUI labs (objective ids kept for existing progress records)
LAB_RULES = {
    'gui-renew': {'open_ethernet': ('any', 'pane:advanced', 'open:ncpa')},
}
WINDOWS = ('settings', 'services', 'devmgr', 'ncpa', 'aduc', 'start')
PANES = ('home', 'system', 'about', 'network', 'ethernet', 'advanced', 'accounts', 'update', 'wifi', 'vpn', 'display', 'sound')
SERVICES = ('Dhcp', 'Dnscache', 'WinDefend', 'Spooler', 'wuauserv')
DEVCATS = ('net', 'display', 'disk', 'kbd')
PRIV_GROUPS = ('Domain Admins', 'Enterprise Admins', 'Administrators', 'Schema Admins')


def gui_state(ad=None):
    st = {'win': None, 'pane': 'home', 'adapter': 'up', 'seen': [], 'log': [], 'updates': 'idle'}
    if ad:
        st['ad'] = deepcopy(ad)
    return st


def default_ad():
    return {
        'domain': 'training.local',
        'ous': ['Sales', 'HR', 'IT', 'Former Staff'],
        'groups': ['Sales-Staff', 'HR-Staff', 'IT-Helpdesk', 'Domain Users', 'Domain Admins'],
        'users': [
            {'sam': 'jchen', 'name': 'Jamie Chen', 'ou': 'Sales', 'enabled': True, 'locked': True, 'groups': ['Domain Users', 'Sales-Staff'],
             'must_change': False, 'pw_reset': False},
            {'sam': 'rpatel', 'name': 'Ravi Patel', 'ou': 'HR', 'enabled': True, 'locked': False, 'groups': ['Domain Users', 'HR-Staff'],
             'must_change': False, 'pw_reset': False, 'note': 'Left the company Friday (HR ticket 4471)'},
            {'sam': 'akim', 'name': 'Alex Kim', 'ou': 'IT', 'enabled': True, 'locked': False, 'groups': ['Domain Users', 'IT-Helpdesk'],
             'must_change': False, 'pw_reset': False},
        ],
    }


def _user(ad, sam):
    sam = (sam or '').strip().lower()
    return next((u for u in ad['users'] if u['sam'] == sam), None)


def _pw_issue(pw):
    pw = pw or ''
    if len(pw) < 14:
        return 'The password does not meet the domain policy: at least 14 characters (a passphrase is easiest).'
    if pw.lower() in ('password12345678', 'welcome1234567', 'changeme123456', 'p@ssw0rd123456') or pw.lower().startswith('password'):
        return 'That password is on the breached/common list the domain screens against. Choose a passphrase.'
    return None


def _ad_event(st, ev, data):
    ad = st['ad']
    d = data or {}
    if ev == 'ad:create':
        first, last = (d.get('first') or '').strip(), (d.get('last') or '').strip()
        sam = re.sub(r'[^a-z0-9._-]', '', (d.get('sam') or '').strip().lower())
        ou = d.get('ou') or ''
        if not first or not last or not sam:
            return {'error': 'First name, last name and user logon name are required.'}
        if ou not in ad['ous']:
            return {'error': 'Choose the organizational unit (OU) the user belongs in.'}
        if _user(ad, sam):
            return {'error': f'The user logon name {sam} is already in use. Pick a unique name.'}
        issue = _pw_issue(d.get('password'))
        if issue:
            return {'error': issue}
        if d.get('password') != d.get('confirm'):
            return {'error': 'The passwords do not match.'}
        ad['users'].append({'sam': sam, 'name': f'{first} {last}', 'ou': ou, 'enabled': True, 'locked': False,
                            'groups': ['Domain Users'], 'must_change': bool(d.get('must_change')), 'pw_reset': False})
        msg = f'{first} {last} created in {ou}.'
        if not d.get('must_change'):
            msg += ' Note: "User must change password at next logon" was not ticked — the help desk now knows this password.'
        return {'ok': msg}
    u = _user(ad, d.get('sam'))
    if not u:
        return {'error': 'Select a user first.'}
    if ev == 'ad:addgroup':
        g = d.get('group') or ''
        if g not in ad['groups']:
            return {'error': 'Choose a group from the list.'}
        if g in PRIV_GROUPS:
            return {'error': f'Blocked by the lab policy: {g} is a privileged group. New staff get least privilege — use the department group.',
                    'policy': True}
        if g not in u['groups']:
            u['groups'].append(g)
        return {'ok': f"{u['name']} added to {g}."}
    if ev == 'ad:removegroup':
        g = d.get('group') or ''
        if g in u['groups'] and g != 'Domain Users':
            u['groups'].remove(g)
        return {'ok': f"{u['name']} removed from {g}."}
    if ev == 'ad:unlock':
        if not u['locked']:
            return {'ok': f"{u['name']} was not locked out."}
        u['locked'] = False
        return {'ok': f"{u['name']}'s account is unlocked."}
    if ev == 'ad:reset':
        issue = _pw_issue(d.get('password'))
        if issue:
            return {'error': issue}
        if d.get('password') != d.get('confirm'):
            return {'error': 'The passwords do not match.'}
        u['pw_reset'] = True
        u['must_change'] = bool(d.get('must_change'))
        if d.get('unlock'):
            u['locked'] = False
        msg = f"Password for {u['name']} was reset."
        if not u['must_change']:
            msg += ' Tick "User must change password at next logon" so only the user knows the new password.'
        return {'ok': msg}
    if ev == 'ad:disable':
        u['enabled'] = False
        return {'ok': f"Object {u['name']} has been disabled."}
    if ev == 'ad:enable':
        u['enabled'] = True
        return {'ok': f"Object {u['name']} has been enabled."}
    if ev == 'ad:move':
        if d.get('ou') in ad['ous']:
            u['ou'] = d['ou']
            return {'ok': f"{u['name']} moved to {d['ou']}."}
        return {'error': 'Choose an OU.'}
    if ev == 'ad:delete':
        return {'error': 'Lab policy: departed staff accounts are disabled and kept for 30 days (mail, file ownership, audit). Do not delete.',
                'policy': True}
    return {'error': 'Unknown action.'}


def apply(lab, state, done, ev, data):
    st = state.setdefault('gui', gui_state())
    result = {}
    ev = (ev or '').strip()
    kind, _, arg = ev.partition(':')
    if kind == 'open' and arg in WINDOWS:
        st['win'] = arg
        if arg == 'settings' and st.get('pane') not in PANES:
            st['pane'] = 'home'
    elif kind == 'close':
        st['win'] = None
    elif kind == 'pane' and arg in PANES:
        st['win'] = 'settings'
        st['pane'] = arg
    elif kind == 'adapter' and arg in ('disable', 'enable'):
        st['adapter'] = 'down' if arg == 'disable' else 'up'
        result['ok'] = 'Ethernet disabled — the address is released.' if arg == 'disable' else 'Ethernet enabled — new DHCP lease obtained (10.20.30.47).'
    elif kind == 'svc' and arg in SERVICES:
        st['svc'] = arg
    elif kind == 'dev' and arg in DEVCATS:
        st.setdefault('dev_open', [])
        if arg not in st['dev_open']:
            st['dev_open'].append(arg)
    elif ev == 'update:check':
        st['updates'] = 'checked'
        result['ok'] = "You're up to date. Last checked: today."
    elif kind == 'ad' and 'ad' in st:
        result = _ad_event(st, ev, data)
    elif kind == 'search':
        pass
    else:
        return {'error': 'unknown event', 'changed': False}, state, done
    if 'error' not in result:
        st['seen'].append(ev)
        st['seen'] = st['seen'][-80:]
    st['log'] = (st.get('log') or [])[-29:] + [ev]
    _award(lab, state, done, ev, data)
    result['changed'] = True
    return result, state, done


def _award(lab, state, done, ev, data):
    st = state['gui']
    rules = dict(DEFAULT_RULES)
    rules.update(LAB_RULES.get(lab['id']) or {})
    rules.update(lab.get('gui_rules') or {})
    seen = st.get('seen') or []
    for o in lab['objectives']:
        oid = o['id']
        if oid in done:
            continue
        rule = rules.get(oid)
        if rule is None:
            continue
        ok = False
        if callable(rule):
            try:
                ok = bool(rule(st, ev, data))
            except Exception:
                ok = False
        elif isinstance(rule, tuple) and rule[0] == 'any':
            ok = any(r in seen for r in rule[1:])
        elif isinstance(rule, tuple) and rule[0] == 'after':
            a, b = rule[1], rule[2]
            ok = a in seen and b in seen and (len(seen) - 1 - seen[::-1].index(b)) > seen.index(a)
        else:
            ok = rule in seen
        if ok:
            done.append(oid)
