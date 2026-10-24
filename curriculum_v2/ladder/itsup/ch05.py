"""Explanation ladder — ITSUP chapter 5 (Addressing, Ports, Isolation, SOHO Wireless, Triage). Pending SME review.

Distinct concept sections are laddered; core, reference and teach-block sections that restate a core section of the
same lesson use same_as.
"""
from curriculum_v2.ladder.itsup._lk import M, P, X
from curriculum_v2.ladder.schema import order, reveal, same_as, sort

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 5


def _s(n, t):
    return f'Course lesson 5.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4, S5 = (_s(1, 'Addresses'), _s(2, 'Ports and Firewall'), _s(3, 'Isolation Order'), _s(4, 'SOHO Wireless'),
                      _s(5, 'Full Triage Capstone'))
_P = 'MC-L-IT5-'
MISCONCEPTIONS = {
    **M(_P, S1, {
        'APIPA-DNS': ('IT-5.1', 'Chasing DNS on a 169.254 (APIPA) address', 'APIPA means no lease: fix link and DHCP first.', ['169.254', 'apipa']),
        'GW-ROLE': ('IT-5.1', 'Not knowing the gateway is the first hop off the LAN', 'If the gateway does not answer, you are not leaving the LAN.', ['gateway']),
        'APIPA-PRIVATE': ('IT-5.1', 'Calling 169.254 a private range the shop uses', 'Private: 10/8, 172.16/12, 192.168/16. 169.254 is APIPA.', ['private', '10.0.0.0']),
    }),
    **M(_P, S2, {
        'PING-PORT': ('IT-5.2', 'Thinking a ping reply proves the app’s port is open', 'Ping is ICMP with no port; test the port itself.', ['ping', 'port']),
        'FW-OFF': ('IT-5.2', 'Turning the firewall profile off to make an app work', 'Read the profile; request a rule or use the approved app.', ['firewall', 'profile']),
        'PORT-MIX': ('IT-5.2', 'Mixing up common port numbers', '53 DNS, 80/443 web, 25/587 mail, 3389 RDP, 445 SMB.', ['443', '3389']),
    }),
    **M(_P, S3, {
        'SKIP-LAYER': ('IT-5.3', 'Flushing DNS or testing names before the IP tests', 'Link, lease, gateway, remote IP, name, port — stop at the first failure.', ['flushdns', 'nslookup']),
        'PING-READ': ('IT-5.3', 'Misreading which layer a failed ping points to', 'Gateway fail = LAN; remote fail = upstream; name fail = DNS.', ['ping', 'gateway']),
        'HUB-SWITCH': ('IT-5.3', 'Confusing switches, routers and access points', 'Switch: within LAN by MAC; router: between networks; AP: Wi-Fi onto LAN.', ['switch', 'router']),
    }),
    **M(_P, S4, {
        'HIDE-SSID': ('IT-5.4', 'Thinking a hidden SSID or MAC filter secures Wi-Fi', 'Change admin password, WPA3, WPS off, guest isolation, firmware.', ['ssid', 'mac filter']),
        'AP-CLICK': ('IT-5.4', 'Changing a shared AP setting without the change process', 'Shared AP changes are changes: record what and how to undo.', ['ap', 'change']),
        'WRONG-SSID': ('IT-5.4', 'Calling it an outage when the client is on the wrong SSID', 'Client first: airplane mode, SSID, lease.', ['ssid', 'client']),
    }),
    **M(_P, S5, {
        'TRIAGE-SKIP': ('IT-5.3', 'Skipping the IP tests and jumping to a fix in the triage lab', 'Identity, IP tests, name tests, action → result, firewall on.', ['triage', 'note']),
    }),
}
APD, GW, APR, PP, FW, PM, SL, PR, HW, HS, APC, WS, TS = (_P + k for k in (
    'APIPA-DNS', 'GW-ROLE', 'APIPA-PRIVATE', 'PING-PORT', 'FW-OFF', 'PORT-MIX', 'SKIP-LAYER', 'PING-READ', 'HUB-SWITCH', 'HIDE-SSID',
    'AP-CLICK', 'WRONG-SSID', 'TRIAGE-SKIP'))
IPC = ('win-ipconfig', 'Run ipconfig /all and mark address, mask, gateway, DNS and DHCP.')
NET = ('w11-powershell-net', 'Use Test-NetConnection to test the service port, not just ping.')
DNSB = ('win-dns-break', 'Work the order: lease, gateway, IP, then name. Stop at the first failure.')
WIFI = ('wifi-secure', 'Apply the SOHO baseline and write what you changed and how to undo it.')
TRI = ('win-full-triage', 'Identity, IP tests, name tests, then action → result. Firewall stays on.')

LESSONS = {
    '5.1': {
        'start-here-what-a-network-is': X('Start here — what a network is', 'IT-5.1', S1, [
            ('What is a network, at its simplest?', 'Devices sharing a path', 'A single computer with a fast processor', 'Any website you can open in a browser',
             'More than one device sharing a path so they can exchange data.', GW, None),
            ('In Chapter 5, what must you read?', 'What one PC believes', 'The whole building wiring plan', 'The ISP’s routing tables',
             'You read one client’s view of the path, not design the plant.', GW, None),
            ('In the street story, what are cables and switches?', 'The roads', 'The houses on the street', 'The letters being posted',
             'Switches and cables carry traffic like roads between houses.', GW, None),
            ('At home, the shared path is usually…', 'Router plus Wi-Fi', 'A server rack with switches', 'A satellite dish only',
             'A small router with Wi-Fi is the typical home path.', GW, None),
            ('At work, who owns switches and access points?', 'The shop', 'Each user', 'The PC vendor',
             'Work network gear belongs to the shop and its owners.', GW, None),
        ],
            P('Two or more devices that can send each other data over a shared route form a network. At home that route is usually one small router '
              'with Wi-Fi built in. At work it is switches, routers, cabling and access points that the shop owns. In this chapter you are not '
              'building that route; you are reading what a single computer thinks about it.'),
            P('Picture a village. The houses are computers, the lanes and junctions between them are cables and switches, and the road out to the '
              'town is the router. A postman only needs to know the house numbers and which junction leads out of the village. You are the postman '
              'here, reading one house’s idea of its own address and the way out, not redrawing the village map.'),
            ['Identify the device.', 'Is it wired or Wi-Fi?', 'Read its address.', 'Read its way out (gateway).', 'Read who answers names (DNS).'],
            '<p>Sort each item.</p>',
            sort('Home or work?', {'Home': ['Small router with Wi-Fi', 'One box does everything'], 'Work': ['Managed switches', 'Access points owned by the shop']},
                 'The idea is the same; the owner differs.'), IPC),
        'address-door-name-said-slowly': same_as('1-what-you-must-be-able-to-point-to', 'Address, door, name — said slowly', 'The same four fields in plain words.'),
        'core-content': same_as('1-what-you-must-be-able-to-point-to', 'Core content', 'Prefix length and mask in depth.'),
        '1-what-you-must-be-able-to-point-to': X('1. What you must be able to point to', 'IT-5.1', S1, [
            ('ipconfig shows 169.254.10.4. What do you do?', 'Renew or check link', 'Flush the DNS cache and retry', 'Teach the user how DNS works',
             'APIPA means no lease; DNS is the wrong lecture here.', APD, APD),
            ('The default gateway is…', 'The first hop off the LAN', 'The server that answers names', 'The PC’s own address',
             'The gateway is the door off this street.', GW, GW),
            ('In the house story, what is DNS?', 'The phone book', 'The front door', 'The street name',
             'DNS turns typed names into numbers, like a phone book.', APD, None),
            ('/26 gives how many usable hosts?', '62', '64 usable addresses', '126 usable addresses',
             '64 addresses minus network and broadcast = 62.', GW, None),
            ('Which field says how large the LAN is?', 'Mask', 'The DNS server only', 'Hostname',
             'The mask (prefix length) sets the network size.', GW, None),
        ],
            P('On any client ticket you should be able to point at five lines in ipconfig /all. The IPv4 address is this computer on this network. '
              'The mask says how big that network is. The default gateway is the way off it. The DNS servers turn names into numbers. DHCP enabled '
              'says whether the address was handed out. A 169.254 address means nothing was handed out: renew it or check the cable.'),
            P('Think of a house. Its number is the IP address. The mask is the name of the street, saying which houses are neighbours. The gateway is '
              'the junction at the end of the street; if you cannot reach it, you never leave. DNS is the phone book that turns a friend’s name into '
              'a house number. A house with a made-up number painted on the gate (169.254) was never given a real one.'),
            ['Find IPv4.', 'Find mask.', 'Find gateway.', 'Find DNS servers.', 'Check DHCP and look for 169.254.'],
            '<p>Sort each field to its meaning.</p>',
            sort('Field meanings', {'Who am I': ['IPv4 address'], 'How big': ['Subnet mask', '/24 prefix'], 'Way out': ['Default gateway'],
                                    'Names': ['DNS servers']}, 'Four lines answer most first questions.'), IPC),
        'address-door-name': same_as('1-what-you-must-be-able-to-point-to', 'Address, door, name', 'The four fields again, with APIPA.'),
        'private-ranges-you-will-see': X('Private ranges you will see', 'IT-5.1', S1, [
            ('Which is a private range?', '172.16.0.0/12', '169.254.0.0/16 link-local', '8.8.8.0/24 public DNS',
             '10/8, 172.16/12 and 192.168/16 are private; 169.254 is APIPA.', APR, APR),
            ('A staff laptop shows a public address it should not. Ticket type?', 'Address plan', 'Replace the NIC', 'Reinstall Windows',
             'A wrong public address is an addressing problem, not hardware.', APR, None),
            ('In the internal-phone story, what are private ranges?', 'Extension numbers', 'Outside lines to the street', 'Mobile numbers',
             'Private addresses work inside, like extensions; NAT reaches out.', APR, None),
            ('Is 169.254 a range the shop assigns?', 'No, it is APIPA', 'Yes, for servers', 'Yes, for printers',
             'APIPA is self-assigned when no lease arrived.', APR, None),
            ('Which private range is the largest?', '10.0.0.0/8', '192.168.0.0/16', '172.16.0.0/12',
             'A /8 is far larger than /12 or /16.', APR, None),
        ],
            P('Three blocks of addresses are kept for use inside organisations and homes. One is everything starting 10. One is 172.16 to 172.31. One is everything starting 192.168. Addresses starting 169.254 are not private ranges. They mean the computer gave itself a number because no server answered. A staff laptop showing a public address where it should be behind NAT is an addressing problem.'),
            P('An office phone system gives every desk a short extension number. Those numbers only work inside the building; to ring out, calls go '
              'through the switchboard. Private ranges are extensions, and NAT is the switchboard. A phone with no extension at all, just a scribbled '
              'number someone made up, is the 169.254 case: it cannot ring anyone properly.'),
            ['Read the address.', 'Starts 10, 172.16–31 or 192.168? Private.', 'Starts 169.254? No lease.', 'Anything else on a staff laptop? Address plan.', 'Write it.'],
            '<p>Sort each address.</p>',
            sort('Address type', {'Private': ['10.20.30.47', '192.168.1.20', '172.20.5.9'], 'APIPA': ['169.254.10.4'], 'Public': ['8.8.8.8']},
                 '169.254 is never a planned range.'), IPC),
        'teach-block-four-lines-on-the-board': same_as('1-what-you-must-be-able-to-point-to', 'Teach block — four lines on the board', 'Mark the four fields, then APIPA.'),
    },
    '5.2': {
        'what-a-port-is-if-you-have-never-heard-it': X('What a port is if you have never heard it', 'IT-5.2', S2, [
            ('Ping to the mail server works, Outlook fails. Why?', 'Different door', 'The network card is dead', 'The PC has no IP address',
             'Ping proves ICMP only; mail uses its own port.', PP, PP),
            ('A port is…', 'A numbered door', 'A cable socket on the wall', 'The PC’s IP address',
             'The IP is the building; the port is a numbered door on it.', PP, None),
            ('In the building story, what does ping do?', 'Knocks on the building', 'Opens the mail door to check', 'Checks every door',
             'Ping asks whether the address answers, not whether a service door is open.', PP, None),
            ('Which tool tests a port?', 'Test-NetConnection -Port', 'ping on its own, many times', 'ipconfig /all',
             'Test the port itself, not the address.', PP, None),
            ('Ping uses which protocol?', 'ICMP', 'TCP 443', 'UDP 53',
             'Ping is ICMP and has no port.', PP, None),
        ],
            P('An IP address gets traffic to the right computer; a port number picks which program on that computer receives it. Web uses 80 or 443, '
              'DNS 53, Remote Desktop 3389. Ping uses neither: it only asks whether the address is there. So a ping reply from the mail server does not '
              'prove its mail service is open, which is why Outlook can fail while ping succeeds.'),
            P('A large office building has one street address but many numbered doors: deliveries, staff entrance, the post room. Ringing the main '
              'bell proves the building is there; it does not prove the post room door is unlocked. Ping rings the main bell. To know whether mail '
              'can be delivered, you walk round and try the post-room door, which is what a port test does.'),
            ['Ping the address: building there?', 'Name the service.', 'Find its port.', 'Test that port.', 'Write which door is closed.'],
            '<p>Guess first, then reveal.</p>',
            reveal('Ping to the file server works, but the shared drive is gone. What do you test?', 'TCP 445 (SMB) with Test-NetConnection fileserver -Port 445.'), NET),
        'core-content': same_as('what-a-port-is-if-you-have-never-heard-it', 'Core content', 'Ports as service promises, with tests.'),
        '1-ports-you-will-actually-say': X('1. Ports you will actually say', 'IT-5.2', S2, [
            ('Remote Desktop uses…', '3389', '443, the HTTPS port', '53, the DNS port',
             'RDP is 3389 and should be treated as sensitive.', PM, PM),
            ('Mail submission from clients uses…', '587', '25 between servers only', '110 for POP3',
             '587 is client submission; 25 is server-to-server relay.', PM, None),
            ('In the speed-dial story, why learn only some?', 'They change the test', 'Others are illegal to use here', 'Others are slow',
             'Memorise the ports that change your first test.', PM, None),
            ('DNS uses port…', '53', '80', '3389',
             'DNS answers on 53, UDP and TCP.', PM, None),
            ('Web uses…', '80 / 443', '25 / 587', '137–139',
             'HTTP 80 and HTTPS 443.', PM, None),
        ],
            P('You do not need every port number, only the few that change what you test first. 53 is name lookups. 80 and 443 are web pages. 25 '
              'carries mail between servers and 587 is where mail programs send from. 3389 is Remote Desktop, which is sensitive and often blocked. '
              'Knowing these lets you test the right door when a user reports one thing broken.'),
            P('Most people keep a handful of speed-dial numbers: home, work, the doctor. They do not memorise the whole phone book, because those few '
              'cover almost every call they make. Ports are the same. A short list you know by heart gets you through most tickets, and the full '
              'reference table is there for the rare call you need to look up.'),
            ['Hear the complaint.', 'Name the service.', 'Recall its port.', 'Test that port.', 'Write the result.'],
            '<p>Sort each port.</p>',
            sort('Port to service', {'Names': ['53'], 'Web': ['80', '443'], 'Mail': ['25', '587'], 'Remote': ['3389']}, 'A short list covers most tickets.'), NET),
        '2-firewall': X('2. Firewall', 'IT-5.2', S2, [
            ('A game launcher is blocked. You…', 'Request a rule', 'Turn the firewall profile off', 'Disable Defender for a day',
             'Read the profile, then request or use the approved app.', FW, FW),
            ('First firewall step?', 'Read the profile', 'Turn it off', 'Reinstall Windows',
             'Know whether the network is Domain, Private or Public first.', FW, None),
            ('In the front-door story, why not remove the lock?', 'Anyone gets in', 'Locks are heavy', 'Keys get lost',
             'Turning the profile off opens every door, not just one.', FW, None),
            ('Disabling the firewall to test is…', 'A hole, not a test', 'Standard practice in every shop', 'Required first',
             'In this course it is never a test.', FW, None),
            ('Where is approved software found?', 'The approved app source (1.4)', 'The vendor’s download page', 'A trusted USB stick from home',
             'Use the approved source from lesson 1.4.', FW, None),
        ],
            P('When something is blocked, first look at which firewall profile is active. Never switch the profile off to make a game launcher or any '
              'other program work. Either use the approved version of the software from lesson 1.4, or raise a request for a rule. Switching the '
              'firewall off does not test anything; it removes protection from every service on the machine.'),
            P('If a delivery driver cannot get in, you do not take the lock off the front door for the day. You open the door for that one '
              'delivery, or arrange a drop box. Removing the lock lets anyone walk in, long after the parcel arrived. Turning the firewall off is '
              'removing the lock; a firewall rule is opening for one delivery.'),
            ['Read the active profile.', 'Is the app approved?', 'Approved: use the approved source.', 'Not approved: open a request.', 'Firewall stays on.'],
            '<p>Sort each action.</p>',
            sort('Allowed?', {'Allowed': ['Read the profile', 'Open a rule request', 'Use the approved app'], 'Not allowed': ['Turn the profile off', 'Disable to test']},
                 'The firewall stays on.'), ('w11-firewall', 'Read the firewall profile and rules; change nothing without a request.')),
        'ports-are-doors-on-a-host': same_as('what-a-port-is-if-you-have-never-heard-it', 'Ports are doors on a host', 'Ping versus the service door.'),
        'reference-port-numbers-technicians-use': X('Reference — port numbers technicians use', 'IT-5.2', S2, [
            ('Which port carries SMB file sharing?', '445', '3389, the Remote Desktop port', '389, the LDAP directory port',
             'SMB uses TCP 445; RDP is 3389 and LDAP 389.', PM, PM),
            ('IMAP over TLS uses…', '993', '110 for plain POP3', '25 for server relay',
             'IMAP is 143 and IMAP over TLS 993; POP3 is 110/995.', PM, None),
            ('In the apartment story, why use a high source port?', 'Temporary return door', 'It is faster', 'It is required by DNS',
             'Clients pick a temporary high port so replies find their way back.', PP, None),
            ('Which pair is cleartext and best avoided?', 'Telnet 23 and FTP 21', 'SSH 22 and HTTPS 443', 'LDAPS 636 and IMAPS 993',
             'Telnet and FTP send passwords in clear; prefer SSH and SFTP.', PM, None),
            ('Ping works but the app does not. What next?', 'Test the port', 'Replace the NIC', 'Reinstall the OS',
             'A firewall rule or stopped service shows up exactly like this; test the port itself.', PP, None),
        ],
            P('The reference table lists the ports a technician meets. 20/21 FTP and 23 Telnet send passwords in clear, so prefer 22 for SSH and '
              'SFTP. 25 relays mail between servers, 587 takes mail from clients, 110/995 are POP3 and 143/993 IMAP. 53 is DNS, 67/68 DHCP, 123 '
              'NTP, 161/162 SNMP, 389/636 LDAP, 443 HTTPS, 445 SMB and 3389 Remote Desktop. Ports below 1024 are well-known; clients reply from a '
              'temporary high port.'),
            P('Think of a large apartment block. Well-known ports are the numbered service doors on the ground floor: the post room, the laundry, '
              'the bike store. When a resident sends something out, they give a temporary flat number for the reply, used once and then forgotten. '
              'If the post room door is locked, ringing the main bell still works, which is why ping can succeed while the service itself fails.'),
            ['Name the service the user cannot reach.', 'Look up its port and protocol.', 'Prefer the encrypted variant.',
             'Test that port with Test-NetConnection.', 'Write port, result and owner.'],
            '<p>Sort each port to its service.</p>',
            sort('Port to service', {'Mail': ['25', '587', '993'], 'Files': ['445'], 'Remote admin': ['22', '3389'], 'Directory': ['389', '636']},
                 'Learn the encrypted variants alongside the clear ones.'), NET),
    },
    '5.3': {
        'core-content': same_as('1-order', 'Core content', 'The isolation order and why it is fixed.'),
        '1-order': X('1. Order', 'IT-5.3', S3, [
            ('The PC has 169.254. You flush DNS. Problem?', 'Skipped a layer', 'Nothing, that is correct', 'You should reinstall instead',
             'No lease yet; name tests mean nothing until the IP tests pass.', SL, SL),
            ('Which comes right after the lease?', 'Ping gateway', 'nslookup the name', 'Flush the DNS cache',
             'Link, lease, gateway, remote IP, name, port.', SL, None),
            ('In the ladder story, why each rung in turn?', 'Each holds the next', 'Rungs are numbered for safety', 'Climbing is slow',
             'Each test depends on the one before.', SL, None),
            ('When do you stop?', 'At the first failure', 'After every test', 'When the user leaves',
             'The first failure is the layer to work on.', SL, None),
            ('nslookup belongs…', 'After the IP tests', 'Before the link check', 'Instead of ipconfig',
             'Names only after IP reachability is proven.', SL, None),
        ],
            P('Connectivity checks go in a fixed order, because each one relies on the last. First the link light or Wi-Fi join. Then a real address from ipconfig. Then a reply from the gateway. Then a reply from a known remote address. Then the name lookup. Last, the service port. Stop at the first one '
              'that fails; that is the layer to fix. Flushing names on a computer with no real address skips layers.'),
            P('Climbing a ladder, you put your foot on each rung in turn. Skipping three rungs to reach the top usually ends with a fall, and you '
              'learn nothing about which rung was broken. Network tests are rungs: if the second one is missing, testing the fifth tells you '
              'nothing useful, and the broken rung is still there.'),
            ['Link.', 'Lease.', 'Ping gateway.', 'Ping remote IP.', 'Resolve name, then test port.'],
            '<p>Put the isolation steps in order.</p>',
            order('Isolation order', ['Link', 'Lease', 'Ping gateway', 'Ping remote IP', 'Resolve name', 'Test port'], 'Stop at the first failure.'), DNSB),
        'isolation-order': same_as('1-order', 'Isolation order', 'The same order with identity first.'),
        'what-each-failed-ping-means': X('What each failed ping means', 'IT-5.3', S3, [
            ('Gateway ping works, 8.8.8.8 fails. Where?', 'Upstream or NAT', 'The local DNS server', 'The PC’s own network card',
             'The LAN is fine; the problem is beyond the gateway.', PR, PR),
            ('App IP pings, its name fails. Which layer?', 'DNS', 'The cable', 'DHCP',
             'IP works, name does not: a name problem.', PR, None),
            ('In the road-trip story, where is the closure?', 'Past the last town reached', 'In your own driveway at home', 'At the start',
             'The failure sits just past the last stop that answered.', PR, None),
            ('Gateway fails and the address is good. Suspect?', 'LAN or gateway', 'The DNS server only', 'The app',
             'Good lease but no gateway: local LAN or the gateway.', PR, None),
            ('Gateway fails plus APIPA means…', 'Lease or link', 'Upstream NAT at the ISP', 'DNS',
             'No lease explains the dead gateway.', PR, None),
        ],
            P('Each failed ping points somewhere specific. No reply from the gateway with a 169.254 address: the link or the lease. No reply from the '
              'gateway with a good address: the local network or the gateway itself. Gateway answers but an outside address does not: the problem is '
              'upstream or in NAT. The app’s address answers but its name does not: it is a DNS problem.'),
            P('On a road trip, if you reach the next town but not the city, the road is closed somewhere between them, not in your driveway. If you '
              'cannot leave your own street, the problem is local. And if you can drive to the address but cannot find it by name, your map is '
              'wrong, not the road. Each failed ping tells you which stretch to look at.'),
            ['Gateway fails + APIPA: lease/link.', 'Gateway fails + good IP: LAN.', 'Gateway OK, remote fails: upstream.', 'IP OK, name fails: DNS.', 'Write the layer.'],
            '<p>Sort each result to its layer.</p>',
            sort('Failing layer', {'Lease or link': ['Gateway fails, 169.254'], 'Local LAN': ['Gateway fails, good IP'], 'Upstream': ['8.8.8.8 fails, gateway OK'],
                                   'DNS': ['Name fails, IP works', 'NXDOMAIN from server']}, 'Each failure names a layer.'), DNSB),
        'teach-block-isolation-table-until-boring': same_as('what-each-failed-ping-means', 'Teach block — isolation table until boring', 'Drill the four failed-ping stories.'),
        'networking-hardware-and-networking-tools': X('Networking hardware and networking tools', 'IT-5.3', S3, [
            ('Which device forwards frames inside the LAN by MAC?', 'Switch', 'Router between networks', 'Cable modem on coax',
             'Switches forward by MAC within the LAN; routers move between networks.', HW, HW),
            ('Where does fibre from the provider end?', 'ONT', 'Patch panel', 'Access point',
             'The optical network terminal terminates fibre.', HW, None),
            ('In the town story, what is the router?', 'The bridge to the next town', 'The town’s local post office', 'The main street in town',
             'The router connects networks like a bridge connects towns.', HW, None),
            ('A managed switch adds…', 'VLANs and monitoring', 'Wi-Fi radios on every port', 'DOCSIS',
             'Managed switches add VLANs, port security and remote management.', HW, None),
            ('Bridges Wi-Fi clients onto the wired LAN:', 'Access point', 'Edge router', 'Network switch',
             'An AP joins wireless clients to the wired network.', HW, None),
        ],
            P('Learn what each box does. A cable modem, DSL modem or fibre ONT ends the provider’s line. A router passes traffic between networks and, '
              'in small offices, also does NAT, DHCP, firewall and Wi-Fi. A switch passes frames around inside the LAN using MAC addresses; managed ones '
              'add VLANs and monitoring. An access point puts Wi-Fi users on the wired network. A patch panel ends the building’s cable runs.'),
            P('Picture a town. The modem is where the motorway from the outside world arrives. The router is the bridge that joins your town to others. '
              'Switches are the roundabouts inside town, sending each car down the right street by its house number. An access point is a ferry that '
              'brings people from the island onto the roads. A patch panel is the neat junction box where every street’s wires meet.'),
            ['Provider line: modem or ONT.', 'Between networks: router.', 'Inside LAN: switch.', 'Wireless onto LAN: AP.', 'Cable runs end: patch panel.'],
            '<p>Sort each device.</p>',
            sort('Device role', {'Provider edge': ['Cable modem', 'ONT'], 'Between networks': ['Router'], 'Inside the LAN': ['Switch', 'Patch panel'],
                                 'Wireless': ['Access point']}, 'Each box has one main job.'), DNSB),
    },
    '5.4': {
        'core-content': same_as('reference-wi-fi-generations-and-soho-security-baseline', 'Core content', 'The SOHO baseline in order of impact.'),
        '1-client-first': X('1. Client first', 'IT-5.4', S4, [
            ('“The internet is down” on one laptop. Check first?', 'Airplane mode and SSID', 'Reboot the office router', 'Call the internet provider',
             'Wrong SSID or airplane mode looks like an outage.', WS, WS),
            ('After SSID and lease, what next?', 'The 5.3 order', 'Reset the AP', 'Change Wi-Fi password',
             'Then the isolation order from 5.3.', WS, None),
            ('In the radio story, why check the station?', 'Wrong station', 'The radio itself is broken', 'Weather',
             'Silence on the wrong station is not a broadcast outage.', WS, None),
            ('Laptop joined “Guest” not “Staff”. Result?', 'Looks like an outage', 'Faster internet for that user', 'No difference',
             'Wrong SSID often lacks access to internal services.', WS, None),
            ('Which comes first?', 'Airplane mode off', 'Ping the gateway address first', 'nslookup',
             'Client radio settings come before the network tests.', WS, None),
        ],
            P('When one laptop says the internet is down, start with the laptop. Is airplane mode off? Is it joined to the right network name, not the '
              'guest network or a neighbour’s? Did it get a real address? Only then run the isolation order from lesson 5.3. A laptop on the wrong '
              'network looks exactly like an outage to the user.'),
            P('If the radio is silent, you check it is switched on and tuned to the right station before ringing the broadcaster. Tuned one notch '
              'off, you hear static and assume the station is off air. A laptop on the wrong network name is tuned to the wrong station: everything '
              'works, just not what the user expected.'),
            ['Airplane mode off?', 'Correct SSID?', 'Real lease?', 'Then 5.3 order.', 'Write each result.'],
            '<p>Put the client checks in order.</p>',
            order('Client first', ['Airplane mode off', 'Correct SSID', 'Real lease', 'Isolation order'], 'The laptop before the network.'), ('w11-wlan', 'Check the Wi-Fi profile, SSID and lease on the client.')),
        '2-ap-changes-are-changes': X('2. AP changes are changes', 'IT-5.4', S4, [
            ('Changing a shared AP’s password at lunch is…', 'An unrecorded change', 'A normal quick fix to do', 'Required every week anyway',
             'Shared AP settings go through the change process.', APC, APC),
            ('What must you write after an AP change?', 'What and how to undo', 'Only the date and time of it', 'Nothing',
             'Record the setting and the rollback.', APC, None),
            ('In the shared-kitchen story, why tell people?', 'Others depend on it', 'Kitchens are small', 'Rules are fun',
             'Everyone using the AP is affected.', APC, None),
            ('Which is an AP change?', 'Guest network setting', 'Ping the gateway address first', 'Read ipconfig',
             'Admin password, guest network and firmware are changes.', APC, None),
            ('Firmware updates on a shared AP need…', 'Change process', 'No notice to anyone', 'A user vote',
             'Firmware is a change like any other.', APC, None),
        ],
            P('An access point that many people share is not yours to tweak casually. Its admin password, guest network and firmware all affect '
              'everyone who connects. Changing any of them goes through the change process. Say what you set, when, and how to put it back. Then nobody wonders why their devices dropped off.'),
            P('In a shared office kitchen, you do not quietly reset the fridge temperature or move the microwave because it suits you. Everyone uses '
              'it, and if things go wrong, they need to know what changed and how to put it back. A shared access point is that kitchen: change it '
              'openly, write it up, and leave a way to undo it.'),
            ['Is the AP shared?', 'Open a change.', 'Make the change.', 'Write what you set.', 'Write how to undo it.'],
            '<p>Sort each item.</p>',
            sort('Change or not?', {'Change process': ['Admin password', 'Guest network', 'Firmware update'], 'Read-only': ['View status page', 'Read client list']},
                 'Reading is free; changing is a change.'), WIFI),
        'soho-wireless': same_as('2-ap-changes-are-changes', 'SOHO wireless', 'Shared AP changes and the hidden-SSID myth.'),
        'reference-wi-fi-generations-and-soho-security-baseline': X('Reference — Wi-Fi generations and SOHO security baseline', 'IT-5.4', S4, [
            ('Which helps security most on a small router?', 'Change admin password', 'Hide the network name SSID', 'Turn on MAC filtering for all',
             'Default admin credentials are the biggest hole; hiding SSID does little.', HS, HS),
            ('Wi-Fi 6E adds which band?', '6 GHz', '900 MHz', '60 GHz',
             'Wi-Fi 6E is 802.11ax extended into 6 GHz.', HS, None),
            ('In the house-lock story, what is hiding the SSID?', 'Removing the house number', 'Changing the front-door lock', 'Fitting a burglar alarm',
             'The house is still there; it just has no number.', HS, None),
            ('Should WPS stay on?', 'No', 'Yes, always', 'Only on 6 GHz',
             'The WPS PIN method can be brute-forced.', HS, None),
            ('Which encryption should you avoid?', 'WEP or TKIP', 'WPA3-Personal', 'WPA2/WPA3 mixed',
             'Never WEP or WPA with TKIP.', HS, None),
        ],
            P('Securing a small router follows a short list. Change the default admin password, switch off management from the internet, use WPA3 '
              '(or WPA2/WPA3 mixed for older devices), never WEP or TKIP, turn WPS off, put visitors on an isolated guest network, and keep firmware '
              'updated. Hiding the network name and filtering MAC addresses are not on the list. Newer generations add bands: 6E and 7 use 6 GHz.'),
            P('Securing a house means changing the locks the builder left, not taking the number off the gate. A burglar can still see the house. '
              'Likewise a hidden network still broadcasts, and MAC addresses can be copied. Change the default key, fit a proper lock, give visitors a '
              'separate annex, and keep the locks maintained: that is the real list.'),
            ['Change admin password.', 'Remote admin off.', 'WPA3 on.', 'WPS off.', 'Guest network and firmware updates.'],
            '<p>Sort each measure.</p>',
            sort('Real security?', {'On the baseline': ['Change admin password', 'WPA3', 'WPS off', 'Guest isolation'], 'Not on it': ['Hide SSID', 'MAC filtering']},
                 'Hiding is not locking.'), WIFI),
    },
    '5.5': {
        'core-content': same_as('note-bar', 'Core content', 'One line per test, ending at the failing layer.'),
        'note-bar': X('Note bar', 'IT-5.3', S5, [
            ('Which note line names the failing layer?', 'nslookup NXDOMAIN', 'User says internet down', 'Rebooted, seems fine now',
             'The failing test, with the server that answered, is the key line.', TS, TS),
            ('The note ends with…', 'Escalate to the owner', 'A smiley face and a thank-you', 'The user’s phone',
             'Changes to shared DNS belong to its owner.', TS, None),
            ('In the lab-report story, what matters?', 'Each test and result', 'Neat handwriting on the cover', 'Long words',
             'A reviewer checks each test and what it showed.', TS, None),
            ('ping 10.20.30.50 4/4 proves…', 'The server answers', 'DNS works', 'The port is open',
             'The IP is reachable; names are a separate test.', TS, None),
            ('Who changes a DNS zone?', 'Its owner', 'The first tech', 'The user',
             'Shared equipment changes belong to their owners.', TS, None),
        ],
            P('A passing network note has one short line per test. Name the device. Give the ipconfig result. Give the gateway ping and the remote IP ping. Give the name lookup and the server that answered. Say what you tried and what happened. It stops at the layer that failed and names who owns the fix, '
              'such as the DNS owner. “The internet is down” is the complaint, never the diagnosis.'),
            P('A science lab report lists each experiment and what it showed, so anyone can repeat it and reach the same answer. “It didn’t work” '
              'earns no marks. The network note is a lab report: each test, each result, the conclusion, and who should act on it. Anyone reading it should be able to rerun your steps.'),
            ['Identity.', 'Lease.', 'Gateway and remote IP.', 'Name test.', 'Action, result, owner.'],
            '<p>Sort each note line.</p>',
            sort('Note quality', {'Evidence': ['ping gw 4/4', 'nslookup NXDOMAIN from 10.20.30.10', 'ipconfig 10.20.30.47/24'],
                                  'Not evidence': ['Internet is down', 'Seems OK now']}, 'Facts with sources pass.'), TRI),
        'pass-bar': same_as('full-triage-lab', 'Pass bar', 'Submit the triage lab with the firewall on.'),
        'full-triage-lab': X('Full triage lab', 'IT-5.3', S5, [
            ('You skip ping-IP and flush DNS; the box works. Pass?', 'No', 'Yes, it works now', 'Yes, if you were quick',
             'The habit is the order; skipping it fails even if the box recovers.', TS, TS),
            ('What does the lab want in the note?', 'Action → result', 'Only the final state', 'A screenshot',
             'Identity, IP tests, name tests, action and result.', TS, None),
            ('In the driving-test story, why fail despite arriving?', 'Skipped the checks', 'Drove too slowly', 'Parked badly',
             'Arriving safely does not excuse skipping mirrors.', TS, None),
            ('The firewall during the lab…', 'Stays on', 'Goes off', 'Is uninstalled',
             'Firewall stays on throughout.', FW, None),
            ('Which comes first in the lab?', 'Identity', 'flushdns', 'Reboot',
             'Identity, then IP tests, then names.', TS, None),
        ],
            P('The full triage lab checks the method, not just the outcome. You record the computer’s identity, run the IP tests, then the name tests, '
              'and write each action with its result. Jump straight to flushing the DNS cache and you fail, even if the computer then works. The '
              'firewall stays on for the whole lab.'),
            P('A driving test is not passed by reaching the end of the route. If you skipped every mirror check and still arrived, the examiner fails '
              'you, because next time the skipped check is the one that matters. The triage lab is that examiner: arriving at a working computer by '
              'luck does not count.'),
            ['Identity.', 'IP tests.', 'Name tests.', 'Action and result.', 'Firewall still on.'],
            '<p>Put the lab steps in order.</p>',
            order('Full triage', ['Record identity', 'Run IP tests', 'Run name tests', 'Write action and result'], 'The order is the grade.'), TRI),
        'teach-block-full-triage-as-a-period': same_as('full-triage-lab', 'Teach block — full triage as a period', 'Every trainee completes the lab with a note.'),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '5.1': {'start-here-what-a-network-is': '368d593c9638', '1-what-you-must-be-able-to-point-to': '3106e130ebac', 'private-ranges-you-will-see': '49d8eadeab42'},
    '5.2': {'what-a-port-is-if-you-have-never-heard-it': '6e1922533272', '1-ports-you-will-actually-say': '0f17ff210612', '2-firewall': '5cc1012db1f5', 'reference-port-numbers-technicians-use': 'e877126ecdc8'},
    '5.3': {'1-order': 'f2d4197428ee', 'what-each-failed-ping-means': '4af263203d52', 'networking-hardware-and-networking-tools': '4a95f469079a'},
    '5.4': {'1-client-first': 'd58919f7a781', '2-ap-changes-are-changes': '222a98236469', 'reference-wi-fi-generations-and-soho-security-baseline': '294ea9f270b7'},
    '5.5': {'note-bar': 'ada78b75b5c9', 'full-triage-lab': 'fec3c7f966a8'},
}

