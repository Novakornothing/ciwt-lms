"""Help Desk Queue: deterministic tickets and grading.

The caller is a decision tree. Each question has one reply. Nothing calls an external API.
Score is 100 points: triage 25, steps 40, time 15, closing note 20.
"""
PRIORITIES = ('low', 'medium', 'high', 'critical')
_BANNED = ('idk', 'whatever', 'not my problem', 'dumb', 'stupid user')
_RESULT = ('resolved', 'fixed', 'restored', 'working', 'confirmed', 'verified', 'replaced', 'completed')


def hd(tid, course, title, caller, priority, opening, qa, steps, required, keywords, lab=None, area='', target=480):
    tree = {'start': {'reply': '', 'asks': []}}
    for qid, ask, reply, fqid, fask, freply in qa:
        tree['start']['asks'].append({'id': qid, 'text': ask, 'next': qid})
        follow = []
        if fqid:
            follow.append({'id': fqid, 'text': fask, 'next': fqid})
            tree[fqid] = {'reply': freply, 'asks': []}
        tree[qid] = {'reply': reply, 'asks': follow}
    return {
        'id': tid, 'course': course, 'title': title, 'caller': caller, 'priority': priority,
        'opening': opening, 'tree': tree, 'area': area or course,
        'steps': [{'id': a, 'text': b, 'good': c} for a, b, c in steps],
        'required': list(required), 'keywords': list(keywords),
        'lab_id': lab, 'target_sec': int(target),
    }


def _find(ticket, node_id, qid):
    for ask in ticket['tree'].get(node_id, {}).get('asks', []):
        if ask['id'] == qid:
            return ask
    return None


def replay(ticket, asked):
    """Walk the tree. Same questions always produce the same replies."""
    node_id = 'start'
    lines = [{'who': 'them', 'name': ticket['caller'], 'text': ticket['opening']}]
    for qid in asked or []:
        ask = _find(ticket, node_id, qid)
        if not ask:
            break
        lines.append({'who': 'you', 'text': ask['text']})
        node_id = ask['next']
        lines.append({'who': 'them', 'name': ticket['caller'], 'text': ticket['tree'][node_id]['reply']})
    return lines, node_id


def questions_at(ticket, node_id):
    return list(ticket['tree'].get(node_id, {}).get('asks', []))


def public_steps(ticket):
    return [{'id': s['id'], 'text': s['text']} for s in ticket['steps']]


def _index(priority):
    try:
        return PRIORITIES.index(priority)
    except ValueError:
        return -1


def _ordered(chosen, required):
    i = 0
    for step in chosen:
        if i < len(required) and step == required[i]:
            i += 1
    return i == len(required)


def grade(ticket, *, priority, steps, note, seconds):
    """Deterministic score. ``steps`` is the order the student chose."""
    pri = (priority or '').strip().lower()
    want = ticket['priority']
    if pri == want:
        triage, triage_note = 25, 'Priority matches.'
    elif _index(pri) >= 0 and abs(_index(pri) - _index(want)) == 1:
        triage, triage_note = 10, 'Priority is one step off.'
    else:
        triage, triage_note = 0, 'Priority does not match the impact.'

    good = {s['id'] for s in ticket['steps'] if s['good']}
    bad = {s['id'] for s in ticket['steps'] if not s['good']}
    chosen = [s for s in (steps or []) if s in good or s in bad]
    required = ticket['required']
    hit = sum(1 for r in required if r in chosen)
    base = 35 * hit / len(required) if required else 0
    penalty = min(16, 8 * sum(1 for s in chosen if s in bad))
    bonus = 5 if hit == len(required) and _ordered(chosen, required) else 0
    steps_pts = int(round(max(0, min(40, base - penalty + bonus))))
    steps_note = f'{hit} of {len(required)} required steps.'
    if any(s in bad for s in chosen):
        steps_note += ' A step that does not fit this ticket was included.'

    target = ticket['target_sec']
    seconds = max(0, int(seconds or 0))
    if seconds <= target:
        time_pts = 15
    elif seconds >= target * 2:
        time_pts = 0
    else:
        time_pts = int(round(15 * (target * 2 - seconds) / target))
    time_note = f'{max(1, round(seconds / 60))} min on a {max(1, round(target / 60))} min target.'

    text = (note or '').strip()
    low = text.lower()
    professional = len(text) >= 40 and not any(b in low for b in _BANNED)
    found = sum(1 for k in ticket['keywords'] if k.lower() in low)
    result = any(w in low for w in _RESULT)
    close = (8 if professional else 0) + (8 if found >= 2 else 4 if found == 1 else 0) + (4 if result else 0)
    close = min(20, close)
    bits = []
    if not professional:
        bits.append('Write a full sentence another technician can follow.')
    if found < 2:
        bits.append('Name what you found.')
    if not result:
        bits.append('Say whether the user is working again.')
    close_note = 'Closing note meets the rubric.' if not bits else ' '.join(bits)

    total = triage + steps_pts + time_pts + close
    return {
        'total': total,
        'triage': triage, 'triage_note': triage_note,
        'steps': steps_pts, 'steps_note': steps_note,
        'time': time_pts, 'time_note': time_note,
        'closing': close, 'closing_note': close_note,
        'priority_key': want,
    }


def _qa(a, b):
    return (a, b)


TICKETS = [
    hd('hd-it-01', 'ITSUP', 'Laptop will not power on', 'Priya N.', 'high',
       'My laptop is plugged in and it will not turn on. The light on the charger brick is dark.',
       [('brick', 'Is the charger light on at the wall?', 'No. The brick stays dark. A different laptop charges in that outlet.',
         'other', 'Have you tried another charger?', 'I do not have another one here.'),
        ('when', 'When did this start?', 'It died when I moved desks this morning. It was fine yesterday.',
         'drop', 'Did the brick or the laptop get dropped?', 'The brick hit the floor. The laptop did not.')],
       [('swap', 'Swap in a known-good AC adapter and see if the laptop powers on', True),
        ('reimage', 'Reimage Windows before testing power', False),
        ('confirm', 'Have Priya confirm the laptop stays on and write the adapter result', True),
        ('bios', 'Clear the BIOS password', False)],
       ['swap', 'confirm'], ['adapter', 'powers'], lab=None, area='Power'),
    hd('hd-it-02', 'ITSUP', 'No picture on the monitor', 'Luis R.', 'medium',
       'The PC fans spin but the monitor stays black. It worked yesterday.',
       [('cable', 'Does the same monitor work with another cable?', 'I tried a second cable and still nothing. The monitor menu does come up.',
         'source', 'Which input is the monitor set to?', 'It says HDMI, and the cable is in HDMI.'),
        ('pc', 'Does this PC show a picture on a different monitor?', 'Yes. On the spare monitor I see the login screen.',
         'port', 'Same port on the PC?', 'Yes, the same port.')],
       [('input', 'Confirm the monitor input and reseat the cable at both ends', True),
        ('panel', 'Replace the monitor after a known-good display also fails on this PC', True),
        ('raid', 'Rebuild the RAID array', False),
        ('format', 'Format the disk', False)],
       ['input', 'panel'], ['monitor', 'cable'], area='Display'),
    hd('hd-it-03', 'ITSUP', 'Beeps and no display', 'Sam O.', 'high',
       'I added RAM last night. Now the PC beeps and never shows a picture.',
       [('beep', 'How many beeps, and did you reseat the new stick?', 'Three beeps. I pushed the stick in until it clicked, I think.',
         'slot', 'Is it in the slot the board manual lists first?', 'I used the slot farthest from the CPU.'),
        ('old', 'Does it boot with only the original memory installed?', 'I have not tried taking the new stick out.',
         'match', 'Is the new stick the same type as the old one?', 'The label is different. It was on sale.')],
       [('one', 'Boot with one known-good stick in the primary slot', True),
        ('seat', 'Reseat memory and confirm the board posts', True),
        ('os', 'Reinstall Windows while it is still beeping', False),
        ('dns', 'Change the DNS server', False)],
       ['one', 'seat'], ['memory', 'post'], area='Hardware'),
    hd('hd-it-04', 'ITSUP', 'PC is slow and the disk is full', 'Ava K.', 'medium',
       'My computer crawls. A message says low disk space. I have a presentation at 2.',
       [('free', 'About how full is the disk?', 'It says 1 GB free of 256 GB.',
         'what', 'Did you install anything large this week?', 'A video project folder, and the recycle bin is huge.'),
        ('who', 'Is it only your PC, or is the whole lab slow?', 'Just mine. The person next to me is fine.',
         'data', 'Is the presentation saved only on this PC?', 'Yes. I have not copied it anywhere.')],
       [('space', 'Find what filled the disk and clear safe space after the file is copied off', True),
        ('backup', 'Copy the presentation off the PC before you delete anything', True),
        ('reimage', 'Reimage first and hope the file is in email', False),
        ('ram', 'Replace the CPU', False)],
       ['backup', 'space'], ['disk', 'copied'], lab='w11-disk', area='Storage'),
    hd('hd-it-05', 'ITSUP', 'Print jobs sit in the queue', 'Noah P.', 'medium',
       'I print and nothing comes out. The jobs sit there. The printer looks awake.',
       [('where', 'Is it one PC or every PC that uses this printer?', 'Only my PC. My coworker printed a page.',
         'err', 'Any error on the printer screen?', 'It says ready.'),
        ('app', 'Does a test page from Windows fail the same way?', 'The test page also sits in the queue.',
         'spool', 'Have you restarted anything yet?', 'I restarted Word. Not the computer.')],
       [('spooler', 'Restart the print spooler and send one test page', True),
        ('driver', 'Confirm the queue points at the right printer and the driver is not erroring', True),
        ('mobo', 'Replace the motherboard', False),
        ('wifi', 'Forget the Wi-Fi network', False)],
       ['spooler', 'driver'], ['spooler', 'test page'], lab='print-trouble', area='Printing'),
    hd('hd-it-06', 'ITSUP', 'Laptop cannot join Wi-Fi', 'Mina S.', 'medium',
       'My laptop will not join the office Wi-Fi. My phone on the same desk joins fine.',
       [('which', 'Which network name are you choosing?', 'I pick Office-Staff. It asks for a password and then says cannot connect.',
         'psk', 'Are you using the staff passphrase, not the guest one?', 'I was using the guest password. I did not know there were two.'),
        ('others', 'Do other laptops at this desk join Office-Staff?', 'Yes. Just mine fails.',
         'saved', 'Is an old password saved for that name?', 'It might be. I used to be on guest.')],
       [('forget', 'Forget the saved network and join Office-Staff with the current passphrase', True),
        ('check', 'Confirm the laptop gets an address and can open an inside page', True),
        ('reimage', 'Reimage before trying the passphrase', False),
        ('open', 'Set the router to an open network', False)],
       ['forget', 'check'], ['wi-fi', 'address'], lab='win-wifi-survey', area='Wireless'),
    hd('hd-it-07', 'ITSUP', 'Suspicious email asking for a password', 'Jon E.', 'high',
       'I got an email that looks like IT. It says my mailbox will close unless I sign in at a link. I almost clicked.',
       [('click', 'Did you enter the password?', 'No. I stopped. The link is still unopened.',
         'look', 'Does the sender address match our real domain?', 'It is it-support.example-mail.test, not our domain.'),
        ('others', 'Have coworkers reported the same message?', 'Two people in chat said they got it too.',
         'attach', 'Any attachment?', 'No attachment. Just the link.')],
       [('report', 'Have Jon report the message and do not enter credentials', True),
        ('note', 'Record the sender and that no password was entered, then escalate the campaign', True),
        ('click', 'Click the link to see where it goes', False),
        ('pay', 'Reply with the password so the sender will stop', False)],
       ['report', 'note'], ['phish', 'password'], lab='sec-malware', area='Security'),
    hd('hd-it-08', 'ITSUP', 'Account locked after vacation', 'Rae T.', 'medium',
       'I am back from leave and my account says locked. I need email before the 9 a.m. standup.',
       [('tries', 'Did you try a guessed password this morning?', 'A few times. I was not sure of the new one from the reset email.',
         'other', 'Can you sign in on your phone?', 'The phone mail app also says locked.'),
        ('shared', 'Does anyone else use this account?', 'No. It is only me.',
         'cap', 'Any message about a cap or a trip?', 'No. Just locked.')],
       [('unlock', 'Unlock the account through the approved path and have Rae set a new password', True),
        ('verify', 'Confirm Rae can open mail, and tell them not to share the password', True),
        ('disable', 'Disable the lockout policy for the domain', False),
        ('sharedpw', 'Set the password to the team shared one', False)],
       ['unlock', 'verify'], ['unlocked', 'password'], lab='win-ad-users', area='Accounts'),
    hd('hd-it-09', 'ITSUP', 'VPN drops every few minutes', 'Chris L.', 'medium',
       'My VPN connects, then drops. It started on the hotel Wi-Fi. At my desk yesterday it was fine.',
       [('where', 'Are you on hotel Wi-Fi right now?', 'Yes. The hotel page makes me sign in again every so often.',
         'desk', 'Did it stay up at your desk?', 'Yes, all day.'),
        ('one', 'Is it only your laptop?', 'My teammate in the office is fine. I am the only one traveling.',
         'time', 'How long does it stay up?', 'About three minutes.')],
       [('path', 'Note that the drop follows the hotel network, not the office', True),
        ('workaround', 'Offer a phone hotspot test and document the result', True),
        ('firewall', 'Disable the company firewall for everyone', False),
        ('reimage', 'Reimage the laptop in the hotel lobby', False)],
       ['path', 'workaround'], ['hotel', 'vpn'], area='Network'),
    hd('hd-it-10', 'ITSUP', 'Blue screen after last night\'s update', 'Elena V.', 'high',
       'The PC installed updates and now it blue-screens before the login. I have a draft on the desktop.',
       [('code', 'Do you see a stop code?', 'It flashes DRIVER something, then reboots.',
         'when', 'Did this start only after the update?', 'Yes. It was fine at 6 p.m.'),
        ('data', 'Is the draft only on this PC?', 'Yes. Please do not wipe it.',
         'safe', 'Can you get to the recovery screen?', 'Yes, it offers startup repair.')],
       [('repair', 'Try Startup Repair or uninstall the latest update before any wipe', True),
        ('files', 'Confirm the draft is still there before you close the ticket', True),
        ('clean', 'Clean the disk with diskpart as the first step', False),
        ('ignore', 'Tell Elena to keep rebooting until it stops', False)],
       ['repair', 'files'], ['update', 'boot'], area='Windows'),
    hd('hd-it-11', 'ITSUP', 'Cannot open the team share', 'Omar F.', 'medium',
       'I can sign in to Windows but the Finance share says access denied. I could open it last week.',
       [('who', 'Can a teammate with the same role open it from their PC?', 'Yes. And from my PC their account works. Mine does not.',
         'group', 'Were you moved to a new team?', 'I moved from Finance to Sales on Friday.'),
        ('name', 'Are you opening the same path as before?', 'Yes. \\\\files\\finance.',
         'err', 'What is the exact error?', 'Access is denied.')],
       [('group', 'Check group membership against the share, and request the right access', True),
        ('prove', 'Confirm Omar can open a file he should still have, and record the group change', True),
        ('everyone', 'Grant Everyone full control', False),
        ('format', 'Format the file server', False)],
       ['group', 'prove'], ['access', 'group'], area='Files'),
    hd('hd-it-12', 'ITSUP', 'Nightly backup reported failed', 'Dev P.', 'medium',
       'The backup email says failed. People are working. I do not know if we have a copy.',
       [('which', 'Which job failed, and what did the log say?', 'The nightly file-server job. The log says destination disk full.',
         'last', 'When did a job last succeed?', 'Two nights ago.'),
        ('need', 'Is anyone restoring right now?', 'No. I just do not want to find out we have no copy.',
         'where', 'Is the destination a different disk than the live data?', 'It is a second disk in the same server.')],
       [('space', 'Free space on the backup disk or point the job at a disk with room', True),
        ('test', 'Run a small restore test and record that it worked', True),
        ('stop', 'Turn the backup job off', False),
        ('raid', 'Convert the live volume to RAID 0 and call it a backup', False)],
       ['space', 'test'], ['backup', 'restore'], lab='ops-backup', area='Backup'),
    hd('hd-it-13', 'ITSUP', 'New hire cannot sign in', 'Holly G.', 'low',
       'The new hire starts at noon. The account was requested last week. The login says the username is wrong.',
       [('name', 'What username are they typing?', 'First name only. The welcome mail says h.garcia.',
         'mail', 'Do they have that welcome mail?', 'Yes, on their phone.'),
        ('pc', 'Is the PC on the network?', 'Yes. I can sign in with my account on it.',
         'cap', 'Caps lock?', 'No.')],
       [('name', 'Have them sign in as h.garcia and set a password they choose', True),
        ('check', 'Confirm they reach the desktop and mail', True),
        ('admin', 'Make the new hire a domain admin so login is easier', False),
        ('share', 'Tell them your password to use today', False)],
       ['name', 'check'], ['username', 'signed in'], lab='win-ad-users', area='Accounts'),
    hd('hd-it-14', 'ITSUP', 'USB headset not showing up', 'Ben C.', 'low',
       'I plugged in a headset and the PC does not see it. The call is in an hour. Speakers still work.',
       [('port', 'Have you tried another USB port?', 'The front ports do nothing. I have not tried the back.',
         'light', 'Any light on the headset?', 'No light.'),
        ('other', 'Does the headset work on another PC?', 'I have not tried. I can use the laptop next to me.',
         'need', 'Do the speakers cover the call if we need a workaround?', 'Yes, if I can be heard. The mic is the problem.')],
       [('port', 'Try a rear USB port and a second PC to separate the port from the headset', True),
        ('note', 'Record which port works, or give Ben the speaker workaround and a replacement if the headset is dead', True),
        ('os', 'Reinstall Windows', False),
        ('switch', 'Reload the core switch', False)],
       ['port', 'note'], ['usb', 'headset'], lab='gui-devices', area='Peripherals'),
    hd('hd-it-15', 'ITSUP', 'BitLocker asking for a key', 'Nina W.', 'high',
       'After a firmware update the laptop asks for a BitLocker recovery key. I do not have it. Class starts in 20 minutes.',
       [('screen', 'Is it the blue recovery key screen, before Windows?', 'Yes. It wants the key. I cannot get to the desktop.',
         'change', 'What changed?', 'The tech bench updated the firmware at lunch.'),
        ('copy', 'Is there a copy of the work anywhere else?', 'The project is also on the class share. This laptop is my notes.',
         'key', 'Were you given a key when encryption was turned on?', 'I do not remember one.')],
       [('key', 'Recover the key from the approved store and enter it. Do not clear the disk.', True),
        ('confirm', 'Confirm Nina reaches the desktop and the notes are intact', True),
        ('clean', 'Clean the disk because the key is annoying', False),
        ('off', 'Turn BitLocker off for every laptop', False)],
       ['key', 'confirm'], ['recovery key', 'desktop'], area='Encryption'),
    hd('hd-it-16', 'ITSUP', 'Second monitor flickers', 'Ibrahim Y.', 'low',
       'My second monitor flickers when I move a window onto it. The laptop screen is fine.',
       [('cable', 'Does a different cable stop the flicker?', 'I only have this one HDMI cable. It is loose at the dock.',
         'dock', 'Is the dock in the chain?', 'Yes. Laptop to dock to monitor.'),
        ('rate', 'Does it flicker at the desktop with no extra apps?', 'Yes, even on the empty desktop.',
         'one', 'Only this desk?', 'Yes.')],
       [('seat', 'Reseat the dock cable and try a known-good cable', True),
        ('verify', 'Have Ibrahim move a window and confirm the flicker is gone', True),
        ('reimage', 'Reimage before touching the cable', False),
        ('dns', 'Flush DNS', False)],
       ['seat', 'verify'], ['cable', 'flicker'], area='Display'),

    hd('hd-no-01', 'NETOPS', 'User cannot reach the gateway', 'Pat K.', 'high',
       'A new desk cannot ping its gateway. The desk next to it, same closet, can.',
       [('vlan', 'What VLAN is the working desk on?', 'VLAN 20. I have not checked the new port.',
         'port', 'Is the new port an access port?', 'It might still be the default VLAN.'),
        ('gw', 'What address is the gateway?', '10.20.0.1. The PC has 10.20.0.50 if I set it by hand. Ping fails.',
         'link', 'Is the link light on?', 'Yes, the light is on.')],
       [('access', 'Put the port in VLAN 20 as an access port and verify', True),
        ('show', 'Confirm with show vlan brief that the port is in 20', True),
        ('nat', 'Add a NAT overload rule', False),
        ('wipe', 'Erase startup-config', False)],
       ['access', 'show'], ['vlan', 'gateway'], lab='sw-vlan-access', area='Switching'),
    hd('hd-no-02', 'NETOPS', 'Trunk drops a new VLAN', 'Riley S.', 'high',
       'VLAN 40 works on the access switch if I put two ports in it, but those users cannot reach the router.',
       [('allow', 'Is VLAN 40 allowed on the uplink trunk?', 'I am not sure. The trunk was built last year for 10 and 20.',
         'native', 'What is the native VLAN?', 'Native is 1 on this switch. I think the other end is 1 too.'),
        ('router', 'Does the router have an interface for VLAN 40?', 'Yes. 10.40.0.1. It works for a port on the core.',
         'tag', 'Are the users untagged on 40?', 'Yes, access ports.')],
       [('allow', 'Allow VLAN 40 on the trunk and verify the tag matches on both ends', True),
        ('ping', 'Ping the gateway from a VLAN 40 host and record it', True),
        ('flat', 'Put every port in VLAN 1', False),
        ('stp', 'Disable Spanning Tree on all switches', False)],
       ['allow', 'ping'], ['trunk', 'vlan 40'], lab='sw-trunk-basics', area='Switching'),
    hd('hd-no-03', 'NETOPS', 'No DHCP on the new subnet', 'Casey M.', 'high',
       'PCs on the new subnet stay at 169.254 addresses. The DHCP server is on the server VLAN and works there.',
       [('helper', 'Is there a relay or helper on the new subnet\'s gateway?', 'I do not think so. The gateway is a new router interface.',
         'scope', 'Does a scope exist for this range?', 'Yes. The scope is active and empty.'),
        ('server', 'Can the server VLAN reach the new gateway?', 'Yes. I can ping the gateway from the DHCP server.',
         'rogue', 'Any other device answering DHCP?', 'Not that I have seen.')],
       [('relay', 'Add a DHCP relay on the gateway toward the server', True),
        ('lease', 'Confirm a client gets a lease in the new scope', True),
        ('static', 'Tell every user to pick a random address', False),
        ('off', 'Turn off DHCP on the server', False)],
       ['relay', 'lease'], ['relay', 'lease'], lab='win-dhcp-renew', area='DHCP'),
    hd('hd-no-04', 'NETOPS', 'External names do not resolve', 'Jordan A.', 'high',
       'Inside names work. Anything on the Internet fails by name. Ping to 1.1.1.1 works from a client.',
       [('forward', 'Where do outside queries go?', 'Our DNS forwards to two resolvers. I have not tested those resolvers.',
         'path', 'Can the DNS server itself ping those resolvers?', 'I will have to check. Clients can ping 1.1.1.1.'),
        ('cache', 'Did this start after a firewall change?', 'Yes, an hour ago. We tightened outbound rules.',
         'inside', 'Do internal zones still load?', 'Yes.')],
       [('path', 'Confirm the DNS server can reach its forwarders on UDP and TCP 53', True),
        ('rule', 'Allow that path on the firewall and retest an external name', True),
        ('delete', 'Delete the internal zones', False),
        ('hosts', 'Put the whole Internet in the hosts file', False)],
       ['path', 'rule'], ['dns', 'forward'], lab='win-dns-break', area='DNS'),
    hd('hd-no-05', 'NETOPS', 'Branch cannot reach anything off the LAN', 'Samir D.', 'high',
       'Every PC in the branch can ping the router. Nothing past the router answers. This started after a reload.',
       [('route', 'Does the router have a default route?', 'show ip route shows only connected networks.',
         'save', 'Was the default route saved before the reload?', 'We added it yesterday and I am not sure we saved.'),
        ('wan', 'Is the WAN interface up?', 'Yes. It has the provider address and a ping to the provider gateway works from the router.',
         'nat', 'Was NAT also new?', 'NAT was already there and looks the same.')],
       [('default', 'Add the default route and save the configuration', True),
        ('verify', 'Ping past the provider from a client and confirm the route survives a review of startup-config', True),
        ('vlan1', 'Move all users to VLAN 1', False),
        ('telnet', 'Enable Telnet on the WAN', False)],
       ['default', 'verify'], ['default route', 'saved'], lab='rtr-default-route', area='Routing'),
    hd('hd-no-06', 'NETOPS', 'ACL blocks the app server', 'Lee H.', 'high',
       'After a new access list, users can ping the app server but the app on TCP 8443 times out.',
       [('order', 'Where is the permit for 8443, and is there a deny above it?', 'The list permits ip any any at the bottom. I do not see 8443. Ping is ICMP so it hits a permit icmp line.',
         'way', 'Is the list inbound on the user VLAN?', 'Yes, inbound on the user gateway.'),
        ('before', 'Did 8443 work before this list?', 'Yes, this morning.',
         'server', 'Is the service listening?', 'From the server itself, yes.')],
       [('permit', 'Permit TCP to the server on 8443 above the implicit deny and retest', True),
        ('hit', 'Confirm the application loads from a user PC', True),
        ('any', 'Permit ip any any at the top and leave it', False),
        ('off', 'Remove every ACL on the router', False)],
       ['permit', 'hit'], ['8443', 'acl'], lab='rtr-vlan-acl', area='Firewall'),
    hd('hd-no-07', 'NETOPS', 'Building network melts down', 'Alex J.', 'critical',
       'Everything on the floor is crawling. Link lights are solid. It started after someone plugged a desk switch into two jacks.',
       [('loop', 'Two jacks, one small switch?', 'Yes. They wanted more ports and used both wall jacks.',
         'storm', 'Are the uplink lights maxed out?', 'The closet uplink is pegged. It was quiet an hour ago.'),
        ('scope', 'Is it one floor or the whole campus?', 'One floor. Other buildings are fine.',
         'stp', 'Is Spanning Tree on for those ports?', 'I think bpduguard is off on the access ports.')],
       [('unplug', 'Unplug the looped desk switch', True),
        ('guard', 'Turn on BPDU guard or equivalent on access ports and confirm the storm stops', True),
        ('rebootall', 'Reload every core router at once', False),
        ('wifi', 'Hide the guest SSID', False)],
       ['unplug', 'guard'], ['loop', 'storm'], area='Switching', target=360),
    hd('hd-no-08', 'NETOPS', 'Wi-Fi is slow in one hallway', 'Morgan P.', 'medium',
       'The hallway by the lab is slow on Wi-Fi. The other wing is fine. A survey last year used channels 1, 6, and 11.',
       [('channel', 'What channel is the hallway AP on now?', 'Someone set it to channel 3 last week during a demo.',
         'overlap', 'What are the neighbors on?', 'The next AP is on channel 1, and this one overlaps it.'),
        ('wired', 'Is the wire on that AP fine?', 'A laptop on the same switch port is fast.',
         'count', 'How many people are in the hall?', 'A class of 20, same as usual.')],
       [('channel', 'Move the AP back to a non-overlapping channel and retest', True),
        ('check', 'Confirm a client in the hall gets a normal rate', True),
        ('power', 'Set the AP to maximum power and the same channel as its neighbor', False),
        ('nat', 'Disable NAT', False)],
       ['channel', 'check'], ['channel', 'wi-fi'], area='Wireless'),
    hd('hd-no-09', 'NETOPS', 'SNMP poller shows the switch as down', 'Taylor B.', 'low',
       'The monitor says the access switch is down. Users on that switch are working.',
       [('reach', 'Can you ping the switch from the poller?', 'Yes. Ping works. The poller uses community public.',
         'acl', 'Did the management ACL change?', 'We removed the old community yesterday and did not update the poller.'),
        ('which', 'Is it only this switch?', 'Only switches we touched yesterday.',
         'ver', 'Which SNMP version?', 'The poller is still on v2c with public.')],
       [('community', 'Point the poller at the new community or SNMPv3 user', True),
        ('green', 'Confirm the poller marks the switch up', True),
        ('public', 'Set the community back to public on the Internet interface', False),
        ('off', 'Turn monitoring off', False)],
       ['community', 'green'], ['snmp', 'poller'], area='Monitoring'),
    hd('hd-no-10', 'NETOPS', 'Interface is down/down', 'Reese C.', 'high',
       'A closet uplink shows down/down after a ceiling tile job. Users past that closet have no network.',
       [('light', 'Any light on either end?', 'No light on the closet side. The core side is down too.',
         'work', 'Were they pulling cable in that ceiling?', 'Yes. They said a line got tugged.'),
        ('alt', 'Is there a second uplink?', 'No. This closet has one run.',
         'config', 'Did anyone shut the port on purpose?', 'show says it is not administratively down.')],
       [('plant', 'Test the physical run and reseat or replace the damaged pair', True),
        ('up', 'Confirm the interface is up/up and users past the closet pass traffic', True),
        ('vlan', 'Change the native VLAN until the light returns', False),
        ('write', 'Erase the core config', False)],
       ['plant', 'up'], ['down/down', 'cable'], lab='sw-int-status', area='Physical'),
    hd('hd-no-11', 'NETOPS', 'Duplicate IP address', 'Drew F.', 'medium',
       'A PC warns that another device has its address. It drops off the network every few minutes.',
       [('how', 'Is the address from DHCP or typed in?', 'Typed in. A contractor set it to 10.20.0.10 last month.',
         'server', 'Is 10.20.0.10 also in the DHCP scope?', 'Yes. The scope starts at .10.'),
        ('who', 'Who else is on .10 right now?', 'The badge printer. It has been .10 for years.',
         'mac', 'Can you see two MACs for .10?', 'The ARP table flips between two MACs.')],
       [('free', 'Give the PC a DHCP address or a reservation outside the conflict', True),
        ('exclude', 'Exclude the printer address from the scope and confirm the warning stops', True),
        ('both', 'Leave both devices on .10', False),
        ('shutdown', 'Shut every access port', False)],
       ['free', 'exclude'], ['duplicate', 'address'], area='Addressing'),
    hd('hd-no-12', 'NETOPS', 'OSPF neighbor is down', 'Kendall R.', 'high',
       'The branch router used to show an OSPF neighbor. After an interface address change it is gone. Traffic that used that path fails.',
       [('hello', 'Do both sides use the same area and hello timers?', 'Area matches. I have not checked hello. The new mask is /30 and the other side is still /29.',
         'mask', 'So the masks do not match?', 'Right. I changed only this side.'),
        ('up', 'Is the interface up?', 'Yes, up/up, and I can ping the old address but not the new peer address.',
         'acl', 'Any ACL on the interface?', 'No.')],
       [('mask', 'Match the masks and addressing so the two routers share a subnet', True),
        ('neigh', 'Confirm the neighbor is full and routes return', True),
        ('static', 'Turn off OSPF everywhere', False),
        ('nat', 'NAT the neighbor address to itself', False)],
       ['mask', 'neigh'], ['ospf', 'neighbor'], area='Routing'),
    hd('hd-no-13', 'NETOPS', 'Port security shut the port', 'Jamie L.', 'medium',
       'A desk died after someone plugged in a small switch. The port LED is amber and the PC has no link after they removed the switch.',
       [('err', 'What does the switch log say for that port?', 'Port security violation, and the port is err-disabled.',
         'max', 'How many MACs are allowed?', 'One. The PC plus the little switch was two.'),
        ('need', 'Do they still need the extra switch?', 'No. They only need the PC.',
         'other', 'Do other desks on that switch work?', 'Yes.')],
       [('recover', 'Shut and no-shut the port, or clear the err-disable, after the extra switch is gone', True),
        ('policy', 'Leave a one-MAC limit if that is the standard, and confirm the PC is online', True),
        ('off', 'Turn port security off on every port', False),
        ('vlan', 'Move the port to the guest VLAN as the fix', False)],
       ['recover', 'policy'], ['err-disable', 'port'], lab='sw-port-security', area='Switching'),
    hd('hd-no-14', 'NETOPS', 'Inside hosts have no Internet after NAT change', 'Parker G.', 'high',
       'We edited the NAT rule. Inside hosts still ping the router. They cannot ping past it. The router itself can ping the Internet.',
       [('nat', 'Is the new NAT matching the inside subnet?', 'The ACL in the NAT rule still names the old subnet. We renumbered yesterday.',
         'route', 'Does the router have a default route?', 'Yes. The router\'s own ping works.'),
        ('pat', 'Is it overload on the WAN interface?', 'Yes, overload. The translation table is empty when a user pings.',
         'state', 'Any deny on the inside interface?', 'No ACL there.')],
       [('acl', 'Update the NAT match so the new inside subnet is translated', True),
        ('table', 'Confirm the translation table fills and a user ping succeeds', True),
        ('open', 'Permit every port from the Internet to the inside', False),
        ('off', 'Remove the default route', False)],
       ['acl', 'table'], ['nat', 'translation'], lab='linux-vm-nat', area='NAT'),

    hd('cl-01', 'CLIENT', 'Windows stops at a spinning wheel', 'Maya D.', 'high',
       'The classroom PC spins forever after the logo. It started after a driver update. The student\'s essay is on the desktop.',
       [('safe', 'Can you reach Startup Settings?', 'Yes, if I interrupt boot. Safe Mode is in the list.',
         'when', 'Did a driver install just before this?', 'A display driver, last period.'),
        ('copy', 'Is the essay only on this PC?', 'Yes. Please do not reset the PC yet.',
         'others', 'Do the other PCs in the row boot?', 'Yes.')],
       [('safe', 'Boot Safe Mode and remove the display driver before any reset', True),
        ('file', 'Confirm the essay is still on the desktop after a normal boot', True),
        ('reset', 'Reset the PC and delete files as the first step', False),
        ('bios', 'Turn on Secure Boot and walk away', False)],
       ['safe', 'file'], ['safe mode', 'boot'], area='Windows'),
    hd('cl-02', 'CLIENT', 'System file check requested', 'Owen B.', 'medium',
       'An app says Windows files are damaged. The PC still boots. I do not want to reinstall if I can avoid it.',
       [('boot', 'Does the PC boot and sign in?', 'Yes. The app is the only complaint.',
         'which', 'Which app?', 'A class installer. It ran sfc once and I closed it.'),
        ('data', 'Is there local work to protect first?', 'Yes, a folder on the desktop.',
         'admin', 'Do you have an admin sign-in for this PC?', 'The lab tech account, yes.')],
       [('copy', 'Copy the desktop folder aside, then run sfc /scannow', True),
        ('result', 'Read the SFC result and only then decide if a deeper repair is needed', True),
        ('format', 'Format the disk because SFC sounds serious', False),
        ('share', 'Email the admin password to the class', False)],
       ['copy', 'result'], ['sfc', 'files'], area='Windows'),
    hd('cl-03', 'CLIENT', 'Linux lab says permission denied', 'Sofia M.', 'medium',
       'I cannot run the script the teacher posted. The shell says permission denied. The file is in my home directory.',
       [('ls', 'What does ls -l show for the file?', 'It is -rw-r--r-- and I own it.',
         'bit', 'So the execute bit is off?', 'I guess so. I have not used chmod.'),
        ('which', 'Are you typing ./script.sh?', 'I typed script.sh with no dot slash. It also says not found that way.',
         'shebang', 'Does the first line name an interpreter?', 'It starts with #!/bin/bash.')],
       [('chmod', 'Add execute for the owner and run it as ./script.sh', True),
        ('works', 'Confirm the script runs and the student knows why the bit mattered', True),
        ('777', 'chmod 777 the whole home directory', False),
        ('root', 'Give the student the root password', False)],
       ['chmod', 'works'], ['chmod', 'execute'], lab='linux-shell', area='Linux'),
    hd('cl-04', 'CLIENT', 'Mac asks for a keychain password', 'Eli N.', 'low',
       'After a password change the Mac keeps asking for the old keychain password. Mail will not stay open.',
       [('which', 'Is it the login keychain?', 'Yes. It asks every time I open Mail.',
         'old', 'Do you still know the old password?', 'Yes.'),
        ('mdm', 'Is the Mac managed by the school?', 'Yes, but the password change was the school portal.',
         'work', 'Can you work in the browser for now?', 'Browser mail works.')],
       [('update', 'Update the login keychain with the old password so it matches the new account password', True),
        ('mail', 'Confirm Mail stays open', True),
        ('newuser', 'Make a second admin and abandon the account', False),
        ('off', 'Turn off FileVault for the lab', False)],
       ['update', 'mail'], ['keychain', 'mail'], area='macOS'),
    hd('cl-05', 'CLIENT', 'Files renamed and a ransom note', 'Hannah J.', 'critical',
       'The lab PC shows a note demanding payment. Documents have new extensions. It is still on the network.',
       [('pay', 'Has anyone paid or opened more files?', 'No. I unplugged nothing yet.',
         'share', 'Is this PC connected to the class share?', 'Yes, the share was open.'),
        ('others', 'Do other PCs show the note?', 'Not yet. I am afraid to click around.',
         'usb', 'Any unknown USB stick?', 'There was one in the front port. I did not put it there.')],
       [('isolate', 'Unplug the network and the unknown USB. Do not pay.', True),
        ('escalate', 'Record what you saw and escalate. Do not delete the note yet.', True),
        ('pay', 'Pay the note from the department card', False),
        ('plug', 'Plug the backup drive in and open the files', False)],
       ['isolate', 'escalate'], ['isolated', 'ransom'], lab='sec-malware', area='Security', target=360),
    hd('cl-06', 'CLIENT', 'One app crashes for one student', 'Leo A.', 'medium',
       'The browser crashes for me on this PC. The next student logs in and the browser is fine.',
       [('profile', 'Same Windows account or two accounts?', 'Two accounts. Mine crashes. Theirs does not. Same PC.',
         'addon', 'Any extra toolbar on your account?', 'I installed one yesterday.'),
        ('otherapp', 'Do other apps crash?', 'No. Just the browser.',
         'time', 'Since when?', 'Since the toolbar.')],
       [('profile', 'Remove the toolbar from that profile or test a fresh profile', True),
        ('ok', 'Confirm the browser stays open on Leo\'s account', True),
        ('reimage', 'Reimage the PC for a toolbar', False),
        ('all', 'Uninstall the browser for every account', False)],
       ['profile', 'ok'], ['profile', 'browser'], area='Software'),
    hd('cl-07', 'CLIENT', 'Lab policy did not apply', 'Grace T.', 'medium',
       'The new lab wallpaper policy is on the other row of PCs and not on this one. We are in the same OU, I think.',
       [('refresh', 'Did you run gpupdate on this PC?', 'No. I only rebooted the ones that worked.',
         'dc', 'Can this PC ping a domain controller?', 'I have not checked. The network icon looks normal.'),
        ('user', 'Are you signed in with a domain account?', 'Yes, the lab student account.',
         'time', 'When was the policy linked?', 'This morning.')],
       [('gp', 'Confirm the PC reaches a domain controller and run gpupdate /force', True),
        ('see', 'Confirm the wallpaper applied and note the OU if it did not', True),
        ('local', 'Set a local policy that fights the domain', False),
        ('admin', 'Add the student account to Domain Admins', False)],
       ['gp', 'see'], ['policy', 'applied'], area='Windows'),
    hd('cl-08', 'CLIENT', 'Disk almost full, PC stuttering', 'Will S.', 'high',
       'The PC says 500 MB free and it freezes when I save. My video project is on the desktop.',
       [('what', 'Do you know what grew?', 'A render folder, and old downloads.',
         'only', 'Is the project only here?', 'Yes.'),
        ('share', 'Is there space on the class share?', 'Yes. I can copy there.',
         'ssd', 'Is this the only drive?', 'One drive.')],
       [('copy', 'Copy the project to the class share before deleting anything', True),
        ('free', 'Clear downloads or the render cache and confirm free space and a save', True),
        ('format', 'Format the drive', False),
        ('ram', 'Remove a RAM stick', False)],
       ['copy', 'free'], ['copied', 'free space'], lab='linux-vm-disk', area='Storage'),
    hd('cl-09', 'CLIENT', 'Sign-in fails after the clock was wrong', 'Ivy P.', 'medium',
       'Domain sign-in failed all morning. The PC clock was set to 2019. We set the clock and I want to be sure that was the cause.',
       [('skew', 'How far off was the clock?', 'Years. It is correct now.',
         'now', 'Can you sign in now?', 'Yes, after the clock change.'),
        ('others', 'Did PCs with the right time fail too?', 'No. Only this one.',
         'source', 'Is the time set by the domain?', 'It was set by hand. The domain time works on the others.')],
       [('time', 'Point the PC at the domain time source so it does not drift again', True),
        ('login', 'Confirm sign-in still works and note the clock as the cause', True),
        ('disable', 'Disable Kerberos on the domain', False),
        ('reimage', 'Reimage because the clock was wrong', False)],
       ['time', 'login'], ['clock', 'sign-in'], area='Accounts'),
    hd('cl-10', 'CLIENT', 'Profile loads a temporary desktop', 'Nate Q.', 'medium',
       'Windows says I am signed in with a temporary profile. My desktop icons are gone. This is the lab PC I always use.',
       [('msg', 'Does it say temporary profile?', 'Yes, a balloon in the corner.',
         'files', 'If you sign out and back in, do the icons return?', 'I tried once. Still temporary.'),
        ('other', 'Does a different account on this PC look normal?', 'The teacher account looks normal.',
         'disk', 'Is the disk full?', 'No. Lots of free space.')],
       [('profile', 'Repair or recreate the profile after the files under the real profile folder are copied aside', True),
        ('back', 'Confirm Nate sees the usual desktop and files', True),
        ('delete', 'Delete the profile folder with no copy', False),
        ('all', 'Delete every profile on the PC', False)],
       ['profile', 'back'], ['profile', 'desktop'], area='Windows'),
    hd('cl-11', 'CLIENT', 'App blocked by the firewall', 'Cora H.', 'medium',
       'A class app cannot reach its server. The browser can. The app says connection timed out. It worked before a firewall prompt I clicked No on.',
       [('prompt', 'The prompt was Windows Firewall?', 'Yes. I clicked cancel. I was not sure.',
         'server', 'Does the browser reach the same server?', 'The browser opens the server status page. The app uses a different port.'),
        ('others', 'Do other PCs still run the app?', 'Yes.',
         'name', 'What is the app name?', 'LabTracker. It uses TCP 4510.')],
       [('allow', 'Allow LabTracker on the firewall for the domain profile only', True),
        ('open', 'Confirm the app connects and note the port', True),
        ('off', 'Turn the firewall off for all profiles', False),
        ('any', 'Allow every inbound port', False)],
       ['allow', 'open'], ['firewall', 'connects'], lab='w11-firewall', area='Windows'),
    hd('cl-12', 'CLIENT', 'Nightly lab script did not run', 'Bea F.', 'low',
       'The cleanup script that should run at 7 p.m. did not run. The lab PCs are still full of yesterday\'s files.',
       [('cron', 'Is it a scheduled task or cron?', 'Cron on the lab server. crontab -l for the lab user shows 19:00.',
         'log', 'Any log line at 19:00?', 'Nothing in the log. The script works if I run it by hand.'),
        ('path', 'Does the cron line use a full path?', 'It says cleanup.sh with no path.',
         'perm', 'Can the lab user read the script?', 'Yes, and it is executable when I am in that directory.')],
       [('path', 'Call the script by full path in cron and capture output to a log', True),
        ('ran', 'Confirm a manual cron-style run works and note the next 7 p.m. check', True),
        ('root', 'Put the lab password in the crontab', False),
        ('off', 'Delete cron', False)],
       ['path', 'ran'], ['cron', 'path'], lab='linux-vm-cron', area='Linux'),
]

assert len(TICKETS) >= 40
assert len({t['id'] for t in TICKETS}) == len(TICKETS)
_BY = {t['id']: t for t in TICKETS}


def all_tickets():
    return list(TICKETS)


def tickets_for(course_code):
    return [t for t in TICKETS if t['course'] == course_code]


def get_ticket(ticket_id):
    return _BY.get(ticket_id)
