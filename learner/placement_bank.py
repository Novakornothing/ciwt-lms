"""Placement items for Skip What You Know. Three questions per chapter.

The correct text stays on the server. Options are shuffled with a fixed seed so a refresh
shows the same order for that item.
"""
import random

# (course, chapter, letter, prompt, correct, wrong1, wrong2, wrong3)
_ROWS = [
    # ITSUP
    ('ITSUP', 1, 'a', 'A user says the whole floor lost email, and the mail server is down. How do you class this contact?',
     'Incident: service is broken for many people', 'Service request: they want a new mailbox', 'Change: schedule a mailbox migration', 'Question only: no ticket is needed'),
    ('ITSUP', 1, 'b', 'You are about to open a desktop case. What do you do first for electrostatic discharge?',
     'Use an anti-static strap or mat, and unplug power', 'Spray the board with compressed glass cleaner', 'Wear wool so the charge stays on your sweater', 'Leave the power supply plugged in and switched on'),
    ('ITSUP', 1, 'c', 'Which ticket note can the next technician verify?',
     'Swapped the known-good adapter. The laptop powered on and the user confirmed it.', 'Fixed it.', 'User was confused. Closed.', 'Probably the battery. Will see.'),
    ('ITSUP', 2, 'a', 'A PC powers on, fans spin, and there is no display and a beep code. Where do you look first?',
     'POST: memory seating, GPU power, and the firmware beep guide', 'The user\'s email password', 'The default browser homepage', 'The printer queue on another floor'),
    ('ITSUP', 2, 'b', 'Secure Boot fails after a new unsigned bootloader. What is Secure Boot checking?',
     'That the bootloader is signed before firmware hands off', 'That the monitor cable is HDMI', 'That DHCP option 6 is present', 'That the case screws are torqued'),
    ('ITSUP', 2, 'c', 'Which memory symptom fits a mismatched or poorly seated DIMM?',
     'POST beeps or a reboot loop, and the board may show less RAM than installed', 'Only the mouse pointer is slow', 'Wi-Fi asks for the PSK again', 'The printer prints blank pages'),
    ('ITSUP', 3, 'a', 'A user asks for RAID so they can skip backups. What do you tell them?',
     'RAID is not a backup. A deleted or encrypted file is still gone.', 'RAID 0 keeps two full copies', 'RAID 5 stores a second copy offsite', 'Mirroring replaces the backup schedule'),
    ('ITSUP', 3, 'b', 'The PC shuts off under load and the case is hot. What do you check before replacing the motherboard?',
     'Fans, heatsink seating, dust, and the power supply under load', 'The Outlook signature', 'The VLAN on the access switch', 'The DNS TTL'),
    ('ITSUP', 3, 'c', 'A monitor works on one cable and not another, same port. What is the likely fault?',
     'The cable or its seat, not the operating system', 'Group Policy wallpaper', 'A full disk', 'An expired password'),
    ('ITSUP', 4, 'a', 'A laptop battery is swollen. What is the right handling?',
     'Stop using it, do not puncture it, and follow the battery hazard process', 'Press the swelling flat and keep using it', 'Charge it overnight to reshape the cell', 'Store it in a drawer of loose paper'),
    ('ITSUP', 4, 'b', 'A managed phone will not join Wi-Fi after an MDM policy change. What do you not do?',
     'Remove the management profile so the user can bypass the policy', 'Check the Wi-Fi profile the MDM pushed', 'Confirm the device is still enrolled', 'Record the error and the policy name'),
    ('ITSUP', 4, 'c', 'Jobs reach the queue and never print. The printer is online. What is a sensible next check?',
     'The spooler service, the right driver, and whether the device shows a jam or error', 'Reinstall the operating system', 'Replace the motherboard', 'Change the user\'s email address'),
    ('ITSUP', 5, 'a', 'A PC has 169.254.20.10 and no default gateway. What does that address mean?',
     'DHCP failed and the host assigned itself a link-local address', 'The DNS server is authoritative', 'The VLAN tag is 169', 'The disk is encrypted'),
    ('ITSUP', 5, 'b', 'Ping to an IP works. Ping to the server name fails. What do you test next?',
     'Name resolution: DNS server, suffix, and cache', 'The monitor cable', 'The RAID level', 'The BIOS date'),
    ('ITSUP', 5, 'c', 'Which SOHO wireless setting matches current practice?',
     'WPA3 or WPA2-AES, a unique passphrase, and admin access not left on the default password', 'WEP, because it is faster', 'SSID hidden and WPS left on with the PIN printed on the router', 'Open network with MAC filtering only'),
    ('ITSUP', 6, 'a', 'A snapshot was taken before a risky change. The guest is later encrypted by malware. Why is the snapshot not your backup?',
     'It still lives with the guest and can be encrypted or deleted with it', 'Snapshots are stored only on tape', 'A snapshot is a full offsite copy', 'Hypervisors refuse to snapshot disks'),
    ('ITSUP', 6, 'b', 'In IaaS, who patches the guest operating system?',
     'The customer, unless a managed service says otherwise', 'The power company', 'Always the application user', 'Nobody. IaaS images never need patches'),
    ('ITSUP', 6, 'c', 'A virtual machine has no network. The host and other guests are fine. What do you check first?',
     'The virtual NIC and which virtual switch it is attached to', 'The building badge reader', 'The laptop battery wear level', 'The printer fuser'),
    ('ITSUP', 7, 'a', 'A user says "the Internet is down." What is the first methodology step?',
     'Identify the problem: who is affected, since when, and what still works', 'Reimage the PC', 'Replace the switch stack', 'Escalate with no notes'),
    ('ITSUP', 7, 'b', 'One user cannot reach a file share. The user next to them can. Where is the fault domain?',
     'That user\'s account, PC, or path, not the whole site', 'The ISP for the region', 'The core router for every VLAN', 'The data-center generator'),
    ('ITSUP', 7, 'c', 'You changed a setting and the symptom is gone. What closes the loop?',
     'Have the user confirm the real task works, then write the action and result', 'Close the ticket with no note', 'Leave the change unwritten so it can be a surprise', 'Ask the user to stop reporting problems'),
    ('ITSUP', 8, 'a', 'Windows will not boot after a driver update, and you can reach the recovery menu. What do you try before a full reinstall?',
     'Startup Repair, System Restore, or uninstalling the driver from recovery', 'A new motherboard first', 'Formatting the data drive with no backup', 'Disabling the firewall on a different PC'),
    ('ITSUP', 8, 'b', 'Which pair is a normal Windows baseline for a managed client?',
     'A standard user for daily work, updates enabled, and the firewall on', 'Everyone is a local administrator', 'Windows Update turned off permanently', 'The guest account enabled with no password'),
    ('ITSUP', 8, 'c', 'A domain PC does not get a new wallpaper policy. What dependency do you check?',
     'That the PC can reach a domain controller and that policy has applied', 'The printer drum', 'The HDMI version of the monitor', 'The RAID stripe size'),
    ('ITSUP', 9, 'a', 'A Linux file is mode 640. Who can read it?',
     'The owner and the group. Others have no permission.', 'Only root, regardless of the bits', 'Everyone on the Internet', 'Only users named in /etc/hosts'),
    ('ITSUP', 9, 'b', 'A Mac user cannot install software because management blocks it. What is the right path?',
     'Use the approved software request. Do not disable management to sneak it in.', 'Boot to an unsigned installer and turn protection off', 'Share the local admin password in chat', 'Create a second admin and hide it'),
    ('ITSUP', 9, 'c', 'A user can open a share from Windows but a Linux mount says permission denied, and the password is correct. What might differ?',
     'The protocol, the path, or the rights on that identity, not "Linux is broken"', 'The monitor refresh rate', 'The CPU socket type', 'The toner level'),
    ('ITSUP', 10, 'a', 'A user pasted their password into a ticket. What do you do?',
     'Remove it, tell them to change it, and never store it in the note', 'Leave it so the next tech can log in as them', 'Email it to the whole team', 'Print it and tape it to the laptop'),
    ('ITSUP', 10, 'b', 'A popup says every file will be deleted unless they pay. The PC is still on the network. What is first?',
     'Disconnect it from the network, preserve what you can, and escalate', 'Pay from the department card', 'Ignore it and keep working', 'Run a full format with no ticket'),
    ('ITSUP', 10, 'c', 'Which control matches least privilege for a technician account?',
     'A separate admin account used only for admin tasks', 'One shared administrator password for the team', 'Daily work logged in as domain admin', 'Write-down of passwords in a shared spreadsheet'),
    ('ITSUP', 11, 'a', 'One application crashes for one user and works for the person at the next desk on the same PC image. How do you scope it?',
     'That user\'s profile or settings, not a site-wide outage', 'The ISP backbone', 'Every PC in the company', 'The building fire alarm'),
    ('ITSUP', 11, 'b', 'Disk space is nearly full and the PC is slow. What do you check before you rebuild Windows?',
     'What is using the space, and whether user data is safe', 'Order a new building switch', 'Change the public DNS for the company', 'Disable the user\'s mailbox'),
    ('ITSUP', 11, 'c', 'An app worked until a second app was installed. What isolation step fits?',
     'A clean boot or Safe Mode to see if the new software is the conflict', 'Replace the CPU', 'New door badges for the floor', 'Turn off DHCP for the VLAN'),
    ('ITSUP', 12, 'a', 'A technician wants to swap a switch at 10 a.m. on a finance close day, with no approval. What is missing?',
     'An approved change window and a rollback plan', 'A longer hostname', 'A new SSID for guests only', 'More desktop icons'),
    ('ITSUP', 12, 'b', 'Which statement about backup, RAID, and snapshots is right?',
     'Backup is a separate copy you can restore. RAID and snapshots are not that copy.', 'RAID 0 is the backup plan', 'A snapshot on the same disk is an offsite backup', 'If the share is up, backups are unnecessary'),
    ('ITSUP', 12, 'c', 'A runbook step says "fix the server." Why is that a weak step?',
     'The next person cannot tell what to check or what done looks like', 'It uses too many verbs', 'Runbooks must be a single word', 'Only managers may write steps'),
    ('ITSUP', 13, 'a', 'You need the PC name, IPv4 address, gateway, and DNS before you change anything. Which command set fits?',
     'hostname and ipconfig /all', 'format C:', 'diskpart clean', 'shutdown /s /t 0'),
    ('ITSUP', 13, 'b', 'IP ping works and the name does not. You already noted the DNS server. What is a reasonable next command?',
     'nslookup of the name, then ipconfig /flushdns if the cache is stale', 'cipher /w on the whole disk', 'Convert the disk to a dynamic disk', 'Disable the NIC in the firmware and leave'),
    ('ITSUP', 13, 'c', 'Why confirm the current state before you change it?',
     'So you know what you altered and can put it back', 'Because commands only work once a day', 'So the ticket can omit the result', 'Because Windows ignores the first command'),
    # NETOPS
    ('NETOPS', 1, 'a', 'A frame is dropped for a bad checksum on a switch port. Which layer are you in?',
     'Data link', 'Application', 'Session only, never the frame', 'The power supply layer'),
    ('NETOPS', 1, 'b', 'How many usable host addresses are in 10.1.1.0/26?',
     '62', '64', '30', '126'),
    ('NETOPS', 1, 'c', 'A voice call is sensitive to delay and can tolerate a lost packet. Which transport fits that habit?',
     'UDP', 'A protocol that retransmits every packet before playback', 'Only TCP port 25', 'ICMP redirects'),
    ('NETOPS', 2, 'a', 'Two access ports should share a broadcast domain but stay off the rest of the switch. What do you configure?',
     'The same VLAN on both access ports', 'A new public IP on each port', 'Port security set to shutdown the VLAN', 'A /32 on the native VLAN only'),
    ('NETOPS', 2, 'b', 'Users on a new switch cannot reach the gateway. The uplink is a trunk and the access VLAN is missing on it. What failed?',
     'The VLAN was not allowed on the trunk', 'DNS TTL was too long', 'The printer fuser', 'STP elected a laptop as root on purpose and that is fine'),
    ('NETOPS', 2, 'c', 'You need to trace which patch-panel port a desk run lands on. Which tool fits?',
     'A toner and probe', 'A protocol analyzer on a different continent', 'A torque screwdriver only', 'An optical time-domain meter on a copper run as the first tool'),
    ('NETOPS', 3, 'a', 'A router has a connected route, a static route, and OSPF for the same prefix. What decides the winner before metrics?',
     'Administrative distance. The lowest distance is preferred.', 'The longest hostname', 'Whichever route was learned last, always', 'The VLAN name'),
    ('NETOPS', 3, 'b', 'A site can ping its gateway but nothing beyond it, and the gateway has no default route. What is missing?',
     'A route to other networks, often a default route', 'A second copy of the same connected route', 'An MX record on the switch', 'Port 3389 open on every PC'),
    ('NETOPS', 3, 'c', 'Users on 2.4 GHz see overlaps and slow rates. Channels in use are 1, 2, 3, and 4. What is the design miss?',
     'Those channels overlap. Use 1, 6, and 11 in the US plan.', '2.4 GHz cannot carry Wi-Fi', 'Every AP must share one channel', 'Hide the SSID and the overlap goes away'),
    ('NETOPS', 4, 'a', 'Clients on a new subnet get no address. The DHCP server is on another subnet and no helper exists. What is missing?',
     'A DHCP relay on the router for that subnet', 'A larger monitor', 'An A record named DHCP', 'Spanning Tree turned off on every access port'),
    ('NETOPS', 4, 'b', 'Internal names resolve. External names do not. The resolver forwards outside queries. What do you check?',
     'The forwarder, its path, and whether recursion is allowed', 'The access-port VLAN of a working internal host only', 'The printer share name', 'The BIOS clock battery as the only cause'),
    ('NETOPS', 4, 'c', 'A firewall allows the first packet out and drops the return. The rule is not stateful. What is the symptom\'s cause?',
     'Return traffic is a new flow and nothing permits it', 'NAT always blocks DNS', 'TCP cannot leave a LAN', 'UDP port 53 is the firewall itself'),
    ('NETOPS', 5, 'a', 'Interface errors climb every minute, and the baseline last week was near zero. What are you looking at?',
     'A counter that moved off its baseline', 'A backup that replaced the need to look', 'A VLAN name', 'A help-desk greeting'),
    ('NETOPS', 5, 'b', 'Which management-plane choice is sound?',
     'SSH and a management VLAN, with Telnet and the default password removed', 'Telnet open to the Internet', 'SNMP v1 community public on every interface', 'One shared enable password taped to the rack'),
    ('NETOPS', 5, 'c', 'Guest Wi-Fi can reach file servers. What segmentation fix fits?',
     'Put guests in a network that cannot route to the inside servers', 'Use the same VLAN as finance', 'Disable the firewall to simplify', 'Give guests a route to every RFC1918 range'),
    ('NETOPS', 6, 'a', 'A branch is down. Local switching works. The default route points at an interface that is down. What is the fault pattern?',
     'The path off the LAN is down. Local hosts can still talk.', 'Every MAC address was erased on purpose', 'DNS is the only possible cause', 'The symptom must be a bad cable at one desk'),
    ('NETOPS', 6, 'b', 'You are in an incident and the change might make it worse. What belongs in the method?',
     'A time box, a status update, and a rollback if the change fails', 'Silence until the end of the day', 'Three unplanned reboots with no note', 'Closing the ticket while the link is still down'),
    ('NETOPS', 6, 'c', 'The link is up after a fix. What makes the record useful?',
     'What the symptom was, what you changed, and how you verified it', 'The word done', 'A photo of the ceiling', 'The enable password'),
    ('NETOPS', 9, 'a', 'You created VLAN 20 and the access port still shows VLAN 1. Which check fits?',
     'show vlan brief, then confirm the port is access and assigned to 20', 'copy run start as the only step', 'reload without saving, then hope', 'shutdown the uplink first'),
    ('NETOPS', 9, 'b', 'You addressed two router interfaces and hosts on each side still cannot cross. What do you verify?',
     'Both interfaces are up, the masks match the hosts, and a route exists', 'The printer driver on a laptop', 'That Telnet is enabled on the PCs', 'The SSID of a guest network'),
    ('NETOPS', 9, 'c', 'You changed the running config and power failed before you saved. What is lost?',
     'The running config. Startup config is what loads next.', 'The serial number', 'The IOS image, always', 'Every VLAN on every switch in the building'),
    # CLIENT (Operating Systems) — chapters 1–6 match the course modules
    ('CLIENT', 1, 'a', 'A Windows upgrade is planned for a PC that just meets the disk requirement and holds the only copy of a project. What do you do first?',
     'Back up the project, then confirm the PC meets the upgrade requirements', 'Start the upgrade and skip the backup', 'Downgrade the firmware at random', 'Enable the guest account'),
    ('CLIENT', 1, 'b', 'After setup, a lab PC should not use an admin account for daily work. Which baseline fits?',
     'A standard user, Windows Update on, and the firewall left on', 'A shared local admin with a blank password', 'Updates paused for a year', 'Remote desktop open to the Internet'),
    ('CLIENT', 1, 'c', 'Startup Repair is available and a recent driver is the suspect. Why try that before reinstalling?',
     'It may restore boot without wiping user data', 'Reinstall is always faster and keeps every app', 'Startup Repair formats the data partition', 'Drivers cannot affect boot'),
    ('CLIENT', 2, 'a', 'You need a Linux directory that the group can read and enter, and others cannot. Which mode fits a directory?',
     '750: owner all, group read and execute, others none', '777 on every file', '000 so the owner is locked out too', '644 on the directory and expect others to enter it'),
    ('CLIENT', 2, 'b', 'A managed Mac refuses an unsigned kernel extension. What is the support path?',
     'Use the approved software. Do not disable protections to force it.', 'Boot to a permissive mode and leave it', 'Share the firmware password', 'Create a hidden admin'),
    ('CLIENT', 2, 'c', 'A file copied from Windows to a Linux share keeps the wrong group. What is the useful distinction?',
     'The copy crossed systems, so ownership follows the destination rules, not the Windows ACL alone', 'Linux has no groups', 'The file name length is the cause', 'SMB cannot carry a file'),
    ('CLIENT', 3, 'a', 'A user offers their password so you can "just log in as me." What do you do?',
     'Refuse, use your own admin path if a change is approved, and tell them not to share it', 'Take the password and write it in the ticket', 'Text it to a classmate', 'Store it in a file named passwords.txt on the desktop'),
    ('CLIENT', 3, 'b', 'Ransom note, files renamed, PC still on the office LAN. First action?',
     'Isolate the PC from the network and escalate with what you saw', 'Pay the note from petty cash', 'Plug in a backup disk and open the files', 'Email the note to the whole company'),
    ('CLIENT', 3, 'c', 'Which pair is an endpoint control, not a hope?',
     'Disk encryption and timely patches', 'A sticky note that says be careful', 'Disabling the lock screen', 'One shared local admin for the class'),
    ('CLIENT', 4, 'a', 'Excel crashes for one person and opens for another on the same PC. How do you scope it?',
     'That profile or add-in, not a fleet-wide failure', 'The core router', 'The domain for every site', 'The monitor model'),
    ('CLIENT', 4, 'b', 'The disk is at 2 percent free and the PC stutters. What comes before a reinstall?',
     'Find what filled the disk and protect the user\'s files', 'Format the volume', 'Replace the CPU', 'Turn off DNS'),
    ('CLIENT', 4, 'c', 'A crash started after a new toolbar install. Which isolation fits?',
     'Clean boot or Safe Mode to see if that software is in the way', 'A new building VLAN', 'Disable Spanning Tree', 'Change the public IP of the firewall'),
    ('CLIENT', 5, 'a', 'You must install a lab app that changes a shared image during class. What is required around the work?',
     'Approval, a window, and a way to roll back', 'Doing it quietly with no note', 'A reboot of every router', 'Disabling backups so they do not interfere'),
    ('CLIENT', 5, 'b', 'A teacher says the nightly copy finished, but it copied onto the same disk the class uses. What is weak?',
     'There is no separate copy. A dead disk takes the copy with it.', 'The copy finished, so the design is fine', 'RAID 0 already solved this', 'Snapshots on that disk are an offsite archive'),
    ('CLIENT', 5, 'c', 'Which note can another technician follow next week?',
     'Reset the print spooler. The queue then printed the test page. User confirmed.', 'Printer stuff done.', 'User error.', 'See me.'),
    ('CLIENT', 6, 'a', 'Which command shows the IPv4 address, mask, gateway, and DNS on Windows?',
     'ipconfig /all', 'format C:', 'cipher /e on the user profile as a first step', 'shutdown /r /t 0'),
    ('CLIENT', 6, 'b', 'A name fails and the IP works. Which command asks DNS directly?',
     'nslookup', 'diskpart clean', 'bcdedit /delete as the first step', 'powercfg /hibernate off'),
    ('CLIENT', 6, 'c', 'You are about to flush the DNS cache. Why look at ipconfig /all first?',
     'So the note records the DNS servers you had before the change', 'Because flush only works after a format', 'Because the command will invent a new IP', 'Because Windows hides ipconfig until you flush'),
]


def _item(course, chapter, letter, prompt, correct, w1, w2, w3):
    iid = f'{course}-{chapter}-{letter}'
    options = [correct, w1, w2, w3]
    random.Random(iid).shuffle(options)
    return {
        'id': iid,
        'course': course,
        'chapter': int(chapter),
        'prompt': prompt,
        'correct': correct,
        'options': options,
    }


def _security_rows():
    """Three placement questions per Security chapter, from the lesson text."""
    from curriculum_sec.assemble import CHAPTERS
    from curriculum_sec.gloss import GLOSS
    rows = []
    letters = 'abc'
    for ch in CHAPTERS:
        plains = []
        for les in ch['lessons']:
            for name in les.get('mc_terms') or []:
                if name in GLOSS:
                    plains.append((name, GLOSS[name][2].rstrip('.')))
        if len(plains) < 3:
            continue
        wrongs = [p for _n, p in plains]
        for i, (name, plain) in enumerate(plains[:3]):
            pool = [w for w in wrongs if w != plain]
            while len(pool) < 3:
                pool.append('That description belongs to a different idea in this course')
            rows.append(('SEC', ch['order'], letters[i],
                         f'Which line matches {name}?', plain, pool[0], pool[1], pool[2]))
    return rows


def all_items():
    return [_item(*row) for row in list(_ROWS) + _security_rows()]


def items_for(course_code, chapters=None):
    chapters = set(chapters) if chapters is not None else None
    out = []
    for it in all_items():
        if it['course'] != course_code:
            continue
        if chapters is not None and it['chapter'] not in chapters:
            continue
        out.append(it)
    return out


def by_id(course_code):
    return {it['id']: it for it in items_for(course_code)}
