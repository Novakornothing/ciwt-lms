"""Option B pass 2 — ITSUP chapter 5 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

_P = 'MC-L-IT5-'
APDNS, GW, APPRIV, PINGP, FWOFF, PMIX, SKIP, PREAD, HUB, HIDE, APCL, WSSID, TSKIP = (_P + k for k in (
    'APIPA-DNS', 'GW-ROLE', 'APIPA-PRIVATE', 'PING-PORT', 'FW-OFF', 'PORT-MIX', 'SKIP-LAYER', 'PING-READ', 'HUB-SWITCH', 'HIDE-SSID',
    'AP-CLICK', 'WRONG-SSID', 'TRIAGE-SKIP'))
SUBN, GWSUB, MASK, TCPUDP, NAMEIP = 'MC-IT5-SUBNET-COUNT', 'MC-C-IT5-GATEWAY', 'MC-R3-IT5-MASK-SIZE', 'MC-C-IT5-TCP-UDP', 'MC-IT5-NAME-VS-IP'
IPC = ('win-ipconfig', 'Run ipconfig /all and mark address, mask, gateway, DNS and DHCP.')
NET = ('w11-powershell-net', 'Use Test-NetConnection to test the service port, not just ping.')
DNSB = ('win-dns-break', 'Work the order: lease, gateway, IP, then name. Stop at the first failure.')
WIFI = ('wifi-secure', 'Apply the SOHO baseline and write what you changed and how to undo it.')
TRI = ('win-full-triage', 'Identity, IP tests, name tests, then action → result. Firewall stays on.')


def _s(n, t):
    return f'Course lesson 5.{n} “{t}” (the original section), re-explained'


S1, S2, S3, S4, S5 = (_s(1, 'IP Addressing'), _s(2, 'Ports and Protocols'), _s(3, 'Client Connectivity'), _s(4, 'SOHO Wireless'),
                      _s(5, 'Internet Is Down Capstone'))
SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


# ------------------------------------------------------------------ 5.1
_add('5.1', 'address-door-name-said-slowly', 'Address, door, name — said slowly', 'IT-5.1', S1, [
    ('Which field is the first door off this street?', 'Default gateway', 'Subnet mask', 'The DNS server list',
     'The gateway is the first hop off the local network; the mask only marks the street.', GW, GW),
    ('The number works but the name fails. Which problem?', 'A name problem', 'A dead internet link', 'A broken network card',
     'If an IP address works and a name does not, the phone book (DNS) is the suspect.', NAMEIP, APDNS),
    ('In the street story, what is the phone book?', 'DNS', 'The gateway', 'The house number',
     'DNS turns names people type into numbers, like a phone book.', APDNS, GW),
    ('In the picture, which address means “nobody gave me a lease”?', '169.254.x.x', '10.20.30.47', '192.168.1.20',
     'APIPA 169.254 addresses are self-assigned when DHCP did not answer.', APPRIV, APPRIV),
    ('A PC shows 169.254.10.5. Which lecture is off-limits?', 'DNS', 'Link and DHCP', 'Cables and lights',
     'On APIPA, fix the link and DHCP first; DNS cannot help a box with no real lease.', APDNS, APDNS),
],
    (['Your PC has a number on the network.', 'That is its IP address.', 'The mask says which part is the street.', 'The rest is the house.',
      'The gateway is the door off the street.', 'DNS turns names into numbers.', 'A 169.254 number means nobody gave the PC an address.',
      'Then fix the cable and DHCP first.'],
     'Read address, mask, gateway and DNS in that order, and treat 169.254 as “no lease”.'),
    ('A house has a number. The street name tells the postman which houses are neighbours. To leave the street, you walk through the '
     'one gate at the end. To find a friend’s house you look up their name in a phone book. If nobody gave your house a number, you '
     'chalk one on the door yourself, and no post can find you.',
     [('House number', 'IP address'), ('Street name', 'Subnet mask (network part)'), ('Gate at the end of the street', 'Default gateway'),
      ('Phone book', 'DNS'), ('Chalked-on number', 'APIPA 169.254 address')],
     'A street is fixed on a map, but a subnet is set by the mask, so one wrong mask can make a neighbour look like a stranger.'),
    ('flow', 'Four lines, then APIPA', ['IP address', 'Subnet mask', 'Default gateway', 'DNS server', '169.254? Fix link and DHCP']),
     'Read the four fields in order. The last box is the check that decides whether DNS is even worth discussing.',
    'Sort each ipconfig line into what it tells you, then mark the four fields in the ipconfig lab.',
    sort('What does it tell you?', {'Who and where I am': ['IPv4 Address 10.20.30.47', 'Subnet Mask 255.255.255.0'],
                                    'How I leave and find names': ['Default Gateway 10.20.30.1', 'DNS Servers 10.20.30.10'],
                                    'Nobody gave me a lease': ['Autoconfiguration IPv4 169.254.7.9']}, 'APIPA stops the lesson at DHCP.'), IPC)

_add('5.1', 'core-content', 'Core content', 'IT-5.1', S1, [
    ('How many usable hosts does a /26 give?', '62', '64', '30',
     'A /26 holds 64 addresses; subtract the network and broadcast to get 62 usable hosts.', SUBN, MASK),
    ('Which mask matches /27?', '255.255.255.224', '255.255.255.192', '255.255.255.240',
     '/27 leaves 5 host bits: 32 addresses, mask .224.', MASK, MASK),
    ('In the pizza story, what does a longer prefix do?', 'Cuts smaller slices', 'Makes the pizza bigger', 'Adds more toppings on top',
     'Each extra prefix bit halves the network, like cutting each slice in two.', MASK, MASK),
    ('In the block picture, .77 with /26 is in which block?', 'The block from .64', 'The block from .0', 'The block from .128',
     '/26 blocks start at .0, .64, .128 and .192; 77 falls in the .64 block.', GWSUB, MASK),
    ('192.168.10.77/26 with gateway .1. What is wrong?', 'Gateway is off-subnet', 'Nothing, it is fine', 'The DNS server is missing',
     'Hosts in the .64 block are .65–.126; the gateway .1 is in another subnet.', GWSUB, GW),
],
    (['An IPv4 address has 32 bits.', 'The prefix says how many name the network.', '/24 means 24 network bits.', 'The mask says the same thing in four numbers.',
      'Each extra bit halves the network.', 'A /26 has 64 addresses.', 'Two are reserved, so 62 hosts can use it.', 'The gateway must sit in the same block.'],
     'Find the block size, then check that the address and the gateway land in the same block.'),
    ('A pizza is the whole address space. Cut it in half and you have two /25 slices. Cut each again for four /26 slices, and so on. '
     'Every slice keeps its first and last bite for the box edges. Two people can only share food directly if they hold the same slice.',
     [('Whole pizza', '/24 network, 256 addresses'), ('Each cut', 'One more prefix bit'), ('Edge bites kept back', 'Network and broadcast addresses'),
      ('Same slice', 'Same subnet: gateway must be here')],
     'A pizza can be cut unevenly; subnets cannot. Every block at one prefix is the same size and starts on a multiple of it.'),
    ('flow', 'Is the gateway on my subnet?', ['Prefix /26', 'Block size 64', 'Blocks .0 .64 .128 .192', '.77 is in .64 block', 'Gateway .1: other block'], 4),
     'The red box shows where this example fails. The fix is the mask or the gateway, compared with a working PC on the same VLAN.',
    'Order the subnet steps, then check a real address, mask and gateway in the ipconfig lab.',
    order('Gateway check by hand', ['Read the prefix or mask', 'Work out the block size', 'List the block starts', 'Find the address’s block',
                                    'Check the gateway is in it'], 'Same block means the gateway is reachable directly.'), IPC)

_add('5.1', 'address-door-name', 'Address, door, name', 'IT-5.1', S1, [
    ('Which command is the first evidence line on a client ticket?', 'ipconfig /all', 'nslookup on a name', 'tracert to the web',
     'ipconfig /all shows hostname, IPv4, mask, gateway, DNS and whether DHCP is on.', APDNS, SKIP),
    ('What does 169.254.x.x mean?', 'No usable DHCP lease', 'A private office range', 'A healthy DNS answer',
     'APIPA means the PC gave itself an address because no DHCP server answered.', APPRIV, APDNS),
    ('In the ID-card story, what is the photo ID number?', 'The IPv4 address', 'The DNS server', 'The gateway router',
     'The ID number says who this host is on the LAN.', GW, APDNS),
    ('In the checklist picture, which line is checked last?', 'DHCP enabled', 'Host name', 'IPv4 address',
     'The ipconfig read goes hostname, IPv4, mask, gateway, DNS, then DHCP enabled.', SKIP, SKIP),
    ('On an APIPA box, what do you skip?', 'A DNS lecture', 'Checking the link', 'Checking DHCP status',
     'With no lease, DNS cannot help; work the link and DHCP first.', APDNS, APDNS),
],
    (['Run ipconfig /all first.', 'Read the host name.', 'Read the IPv4 address.', 'Read the mask.', 'Read the gateway.', 'Read the DNS servers.',
      'Check if DHCP is on.', 'If the address starts 169.254, there is no lease.', 'Then skip DNS and fix the link and DHCP.'],
     'ipconfig /all is your first evidence, and 169.254 sends you to link and DHCP.'),
    ('An office ID card shows your name, your staff number, your department, the exit you use and the help-desk number for finding '
     'colleagues. A temporary card you wrote yourself opens no doors.',
     [('Name on the card', 'Hostname'), ('Staff number', 'IPv4 address'), ('Department', 'Subnet mask'), ('Your exit', 'Default gateway'),
      ('Help-desk directory number', 'DNS server'), ('Self-written card', 'APIPA 169.254 address')],
     'A card is issued once; a DHCP lease expires and renews, so the same PC can show a different address next week.'),
    ('flow', 'Reading ipconfig /all', ['Hostname', 'IPv4', 'Mask', 'Gateway', 'DNS', 'DHCP on?']),
     'Read each box left to right and write it on the ticket. If IPv4 shows 169.254, stop at the second box and work link and DHCP.',
    'Reveal the answer after you decide what the first ticket line should say.',
    reveal('ipconfig /all shows 169.254.33.8, no gateway, DNS fec0::1, DHCP enabled: Yes. What is your first ticket line?',
           '“APIPA 169.254.33.8, no gateway: no DHCP lease. Checking link and DHCP next; DNS not relevant yet.”'), IPC)

_add('5.1', 'teach-block-four-lines-on-the-board', 'Teach block — four lines on the board', 'IT-5.1', S1, [
    ('Which four lines go on the board first?', 'Address, mask, gateway, DNS', 'Cable, switch, router, cloud', 'Ping, tracert, nslookup, arp',
     'The block starts with the four ipconfig fields, then APIPA.', GW, SKIP),
    ('What is marked after the four lines?', 'APIPA', 'Port numbers', 'Wi-Fi bands',
     'Once the four fields are known, trainees mark APIPA in the dump.', APPRIV, APPRIV),
    ('In the recipe-card story, what is APIPA?', 'An empty card', 'The oven setting', 'The shopping list',
     'An empty card means nobody gave the recipe; APIPA means nobody gave a lease.', APPRIV, APDNS),
    ('In the picture, which lecture is crossed out on APIPA?', 'DNS', 'Link', 'DHCP',
     'DNS is the forbidden lecture on an APIPA box; link and DHCP come first.', APDNS, APDNS),
    ('When does the class move on?', 'When all can mark the four', 'After ten minutes exactly', 'When one trainee finally gets it',
     'Stay until every trainee can mark the four lines in a real dump.', SKIP, SKIP),
],
    (['Write four words on the board.', 'Address.', 'Mask.', 'Gateway.', 'DNS.', 'Every trainee points to each one in an ipconfig dump.',
      'Then they find APIPA.', 'Then they say which talk is banned on APIPA.', 'The answer is DNS.'],
     'Nobody moves on until they can mark all four lines and spot APIPA.'),
    ('A cooking class starts with four labels on a recipe card: ingredients, amounts, oven and time. Students point to each on a real '
     'card. Then the teacher hands out a blank card and asks: can you bake from this? No, so nobody discusses icing yet.',
     [('Four labels on the card', 'Address, mask, gateway, DNS'), ('Real recipe card', 'ipconfig /all dump'), ('Blank card', 'APIPA, no lease'),
      ('Discussing icing', 'A DNS lecture on APIPA')],
     'A blank recipe card is obvious, but a 169.254 address looks like a normal address; trainees must learn the first two numbers.'),
    ('flow', 'Teach block order', ['Address', 'Mask', 'Gateway', 'DNS', 'Mark APIPA', 'Name the banned lecture']),
     'The class only moves to the next box when every trainee can do the current one. Speed is not the goal here.',
    'Order the teach block, then let each trainee mark a dump in the ipconfig lab.',
    order('Teach block sequence', ['Address', 'Mask', 'Gateway', 'DNS', 'Mark APIPA', 'Say: no DNS lecture on APIPA'],
          'Repeat until boring; it pays off on every network ticket.'), IPC)

# ------------------------------------------------------------------ 5.2
_add('5.2', 'core-content', 'Core content', 'IT-5.2', S2, [
    ('What does a successful ping prove?', 'The host answers ping', 'Port 443 is open', 'The web app works fine',
     'Ping uses ICMP and has no port; it proves only that the host replies to ping.', PINGP, PINGP),
    ('Which test checks that TCP 445 answers?', 'Test-NetConnection -Port 445', 'ping fileserver -t -l 500', 'ipconfig /flushdns and /renew',
     'Test-NetConnection with -Port shows TcpTestSucceeded for that port.', PINGP, PMIX),
    ('In the office-block story, what is the room number?', 'The port', 'The IP address', 'The transport',
     'The building address gets you to the host; the room number picks the service.', PMIX, TCPUDP),
    ('In the DORA picture, what comes after Offer?', 'Request', 'Discover', 'Acknowledge',
     'Discover, Offer, Request, Acknowledge: the client requests the offer it received.', PMIX, PMIX),
    ('Websites fail but Teams chat works. Which test?', 'Test port 443 and proxy', 'Replace the network card', 'Ping the DNS server',
     'Web uses HTTPS on TCP 443; test that port and the proxy settings.', PINGP, PINGP),
],
    (['An address gets data to the right computer.', 'A port picks the service on it.', 'TCP or UDP says how it travels.', 'Ping has no port.',
      'A reply proves only that ping works.', 'To test a service, test its port.', 'Use Test-NetConnection with -Port.', 'DHCP uses a four-step DORA exchange.'],
     'Name the service, test its port, and never let a ping reply stand in for a service test.'),
    ('An office block has one street address and many rooms. The post room on the ground floor answers the bell even when the accounts '
     'office on floor 3 is locked. Ringing the doorbell proves the building is there, not that accounts is open.',
     [('Street address', 'IP address'), ('Room number', 'Port number'), ('Doorbell', 'Ping (ICMP)'), ('Accounts on floor 3', 'A service such as SMB on 445'),
      ('Signed delivery vs dropped leaflet', 'TCP vs UDP')],
     'Buildings rarely move rooms, but services can listen on other ports, and a firewall can lock one room while the bell still rings.'),
    ('flow', 'DHCP lease exchange (DORA)', ['Discover (broadcast)', 'Offer', 'Request', 'Acknowledge', 'Lease in ipconfig']),
     'If ipconfig shows 169.254, the exchange stopped before Acknowledge. Port tests make no sense until a lease exists.',
    'Sort each complaint to its service port, then test one port in the PowerShell network lab.',
    sort('Which port?', {'TCP 443': ['Websites do not load'], 'TCP 445': ['Shared drive is gone'], 'TCP/UDP 3389': ['Cannot remote into desktop'],
                         'UDP/TCP 53': ['Names do not resolve']}, 'The port changes your first test.'), NET)

_add('5.2', 'ports-are-doors-on-a-host', 'Ports are doors on a host', 'IT-5.2', S2, [
    ('Which port is DNS?', '53', '25', '443',
     'DNS uses port 53; 25 is mail and 443 is secure web.', PMIX, PMIX),
    ('Outlook loops but ping to the mail server works. Dead NIC?', 'No, test the mail port', 'Yes, replace the card', 'Yes, ping proves it is dead',
     'Ping proves ICMP only; the mail service door may be closed while the NIC is fine.', PINGP, PINGP),
    ('In the shop story, what is the shop door?', 'A port', 'The street', 'The shop owner',
     'Each service door on the host is a port; the street is the address.', PMIX, PINGP),
    ('In the picture, which port is RDP?', '3389', '587', '8080',
     'Remote Desktop uses 3389; 587 is mail submission and 80 is web.', PMIX, PMIX),
    ('Which change does the port number cause?', 'It changes the first test', 'It changes the user name', 'It changes the cable type',
     'Knowing the port tells you which door to test first.', PMIX, PINGP),
],
    (['A host has many doors.', 'Each door is a port.', 'Port 53 is DNS.', 'Ports 80 and 443 are web.', 'Ports 25 and 587 are mail.',
      'Port 3389 is Remote Desktop.', 'A ping only knocks on the wall.', 'It does not open any door.'],
     'Pick the door for the service, then test that door.'),
    ('A shopping centre has one address but many shop doors. The bakery can be shut while the chemist is open. Knocking on the centre’s '
     'outer wall tells you the building exists, not which shops are trading.',
     [('Shopping centre address', 'Host IP address'), ('Bakery door', 'Port 80 or 443 (web)'), ('Post office counter', 'Port 25 or 587 (mail)'),
      ('Knocking on the wall', 'Ping')],
     'Shop doors have signs; ports do not. You must know the numbers or look them up before you test.'),
    ('two', 'Doors on one host', (('Service', ['DNS', 'Web', 'Mail', 'Remote Desktop']), ('Port', ['53', '80 / 443', '25 / 587', '3389']))),
     'Read across each row to match service and port. A ping test does not appear anywhere on this chart, because ping has no port.',
    'Sort each port to its service, then use Test-NetConnection -Port in the lab.',
    sort('Port to service', {'Web': ['80', '443'], 'Mail': ['25', '587'], 'DNS': ['53'], 'RDP': ['3389']}, 'Ping never tests these doors.'), NET)

# ------------------------------------------------------------------ 5.3
_add('5.3', 'core-content', 'Core content', 'IT-5.3', S3, [
    ('Ping to the gateway fails with a valid lease. Which layer?', 'The local LAN path', 'The DNS server', 'The web service itself',
     'With a real lease, a failed gateway ping points at the local network path.', PREAD, SKIP),
    ('Why stop at the first failing step?', 'Later steps are untested', 'Later steps all broke', 'It saves a lot of typing time',
     'Every step depends on the one before; after a failure the rest are untested, not broken.', SKIP, PREAD),
    ('In the ladder story, why climb rung by rung?', 'Each rung holds the next', 'The top rung is the safest', 'Rungs are numbered for fun',
     'You cannot stand on rung four if rung two is missing, as with network layers.', SKIP, SKIP),
    ('In the isolation flow, what comes after “ping remote IP”?', 'Resolve the name', 'Ping the gateway', 'Check the link',
     'Link, lease, gateway, remote IP, name, then the service port.', SKIP, SKIP),
    ('IP works, the name fails. Which tool next?', 'nslookup', 'ipconfig /renew', 'Replace the cable',
     'Name resolution is next; nslookup tests it directly.', NAMEIP, SKIP),
],
    (['Network tests depend on each other.', 'Check the cable or Wi-Fi first.', 'Then check for a real address.', 'Then ping the gateway.',
      'Then ping a remote address.', 'Then look up the name.', 'Then test the service port.', 'Stop at the first failure.', 'That is the layer to fix.'],
     'Go in order and stop at the first failing step; everything after it is untested.'),
    ('Climbing a ladder, you test each rung before you put weight on it. If rung two is cracked, you do not argue about rung five. You '
     'fix rung two. Rung five might be fine; you just cannot reach it yet.',
     [('Bottom rung', 'Link: cable or Wi-Fi'), ('Second rung', 'Lease: real address, not 169.254'), ('Middle rungs', 'Ping gateway, ping remote IP'),
      ('Upper rungs', 'Name lookup, then service port'), ('Cracked rung', 'First failing test')],
     'A ladder is physical and obvious; network layers are invisible, so you only know a rung is cracked by running its test.'),
    ('flow', 'Client connectivity isolation order', ['Link', 'Lease', 'Ping gateway', 'Ping remote IP', 'Resolve name', 'Service port']),
     'Move right only when a box passes. The first box that fails is your layer. Boxes to its right are untested, not broken.',
    'Order the six tests, then work the DNS-break lab and stop at the first failing box.',
    order('Isolation order', ['Link', 'Lease (ipconfig)', 'Ping gateway', 'Ping a remote IP', 'Resolve the name', 'Test the service port'],
          'Testing a name before you have a lease tells you nothing.'), DNSB)

_add('5.3', 'isolation-order', 'Isolation order', 'IT-5.3', S3, [
    ('What comes first in the isolation order?', 'Identity', 'nslookup', 'ipconfig /renew',
     'Identity first: which device, which user, which path.', SKIP, SKIP),
    ('Is flushing DNS on an APIPA box a good step?', 'No, it skips a layer', 'Yes, it often helps', 'Yes, always do it first',
     'APIPA means no lease; DNS is several layers above the failure.', APDNS, SKIP),
    ('In the morning-routine story, what is “check you are awake”?', 'Identity', 'Ping a name', 'Flush and renew',
     'You confirm who and where before anything else, like being awake before dressing.', SKIP, SKIP),
    ('In the flow, what is the last step?', 'Flush or renew', 'Ping the gateway', 'Read link lights',
     'Flush or renew comes only after every test before it.', SKIP, SKIP),
    ('Turning off the firewall “to test” is…', 'A hole, not a test', 'A quick valid test', 'The first step of triage',
     'Disabling the firewall changes security without isolating anything.', FWOFF, FWOFF),
],
    (['Start by naming the device and user.', 'Look at link lights or Ethernet status.', 'Run ipconfig.', 'Ping the gateway address.',
      'Ping a name.', 'Run nslookup.', 'Only then flush or renew.', 'Never turn off the firewall to test.'],
     'Follow the order from identity to nslookup, and keep the firewall on.'),
    ('Getting ready for work, you wake up, check the light switch works, find your keys, open the front door and then check the bus '
     'times. Nobody checks bus times while still asleep. Taking the front door off its hinges is not a way to see if it opens.',
     [('Waking up', 'Identity: which device and user'), ('Light switch', 'Link lights'), ('Keys', 'ipconfig: real address'),
      ('Front door', 'Ping the gateway'), ('Bus times', 'Name lookup'), ('Removing the door', 'Turning the firewall off')],
     'Morning steps can be rushed; network steps cannot, because a skipped test gives a false answer later.'),
    ('flow', 'Isolation order with identity first', ['Identity', 'Link lights', 'ipconfig', 'Ping gateway', 'Ping name', 'nslookup', 'Flush or renew']),
     'The last box is the only one that changes anything. Every box before it is a test. The firewall is not on this chart at all.',
    'Order the steps, then work the DNS-break lab without turning off the firewall.',
    order('Isolation order', ['Identity', 'Link lights', 'ipconfig', 'Ping gateway IP', 'Ping a name', 'nslookup', 'Flush or renew'],
          'Changes come only after the tests.'), DNSB)

_add('5.3', 'teach-block-isolation-table-until-boring', 'Teach block — isolation table until boring', 'IT-5.3', S3, [
    ('What does the class point at for each failed ping?', 'The fault domain', 'The user to blame', 'The fastest fix',
     'Each failed-ping story maps to a domain; that is the drill.', PREAD, PREAD),
    ('Someone flushes DNS on APIPA. What happens?', 'They repeat the table', 'They pass anyway', 'They teach the rest of the class',
     'Flushing DNS on APIPA skips layers; the trainee repeats the isolation table.', APDNS, SKIP),
    ('In the times-table story, why repeat until boring?', 'So it becomes automatic', 'To fill up the lesson', 'Because tests require it',
     'Drilling until boring makes the order automatic under pressure.', PREAD, PREAD),
    ('In the picture, gateway ping fails with a lease. Domain?', 'Local LAN', 'DNS name', 'The website',
     'A real lease with a failed gateway ping points at the local network.', PREAD, PREAD),
    ('Which labs follow the table drill?', 'win-ipconfig, win-dns-break', 'hw-cables and hw-board', 'gui-update and gui-about only',
     'The drill is followed by the ipconfig and DNS-break labs.', PREAD, SKIP),
],
    (['The teacher tells four stories of a failed ping.', 'The class points at the area at fault.', 'They repeat this until it is boring.',
      'Then they run two labs.', 'One is win-ipconfig.', 'One is win-dns-break.', 'Anyone who flushes DNS on APIPA does the table again.'],
     'Drill the four failed-ping stories until pointing at the domain is automatic.'),
    ('Children chant times tables until the answers come without thinking. Later, under exam pressure, 7 × 8 just appears. A network '
     'trainee should feel the same about failed pings: the domain comes to mind before panic does.',
     [('Times table chant', 'Isolation table drill'), ('7 × 8 = 56', 'Gateway ping fails → local LAN'), ('Exam pressure', 'A live outage call'),
      ('Re-learning a table', 'Repeating the drill after flushing on APIPA')],
     'Times tables have one answer; failed pings need context, such as whether there is a lease, before the domain is clear.'),
    ('two', 'Four failed-ping stories', (('Symptom', ['169.254, no gateway', 'Lease OK, gateway ping fails', 'Remote IP fails, gateway OK', 'IP works, name fails']),
                                          ('Domain', ['Link or DHCP', 'Local LAN path', 'Beyond the gateway', 'DNS / name']))),
     'Point at the right column for each row until it is automatic. Then run the two labs.',
    'Sort each failed-ping story into its domain, then run the DNS-break lab.',
    sort('Which domain?', {'Link or DHCP': ['169.254 address, no gateway'], 'Local LAN': ['Lease OK, gateway ping fails'],
                           'Beyond the gateway': ['Gateway OK, remote IP fails'], 'Name': ['IP works, name fails']}, 'Repeat until boring.'), DNSB)

# ------------------------------------------------------------------ 5.4
_add('5.4', 'core-content', 'Core content', 'IT-5.4', S4, [
    ('What is the single biggest hole on small routers?', 'Default admin password', 'Hidden SSID setting', 'The 5 GHz band channel choice',
     'The default admin password is the first baseline item to change.', HIDE, APCL),
    ('Which Wi-Fi security should a mixed old/new office use?', 'WPA2/WPA3 transition', 'WEP for older devices', 'Open with MAC filtering',
     'Transition mode lets WPA3 clients use SAE while older ones use WPA2-AES.', HIDE, HIDE),
    ('In the house story, what is changing the front-door lock?', 'Changing the admin password', 'Hiding the house number', 'Painting the door a new colour',
     'The default lock is the biggest risk, like the default admin password.', HIDE, HIDE),
    ('In the baseline picture, what is near the top?', 'Remote admin off', 'Hide the SSID', 'MAC filtering on',
     'Admin credentials and remote admin come first; hiding and MAC filtering are not on the list.', HIDE, HIDE),
    ('Which 2.4 GHz channels do not overlap in North America?', '1, 6 and 11', '1, 2 and 3', '4, 8 and 12',
     'Only 1, 6 and 11 avoid overlap in the 2.4 GHz band in North America.', HIDE, WSSID),
],
    (['Secure a small router in order of impact.', 'First, change the admin password.', 'Turn off remote admin.', 'Use WPA3, or WPA2/WPA3 mixed mode.',
      'Never use WEP.', 'Turn off WPS.', 'Give guests their own network.', 'Keep the firmware updated.', 'Hiding the network name does not help.'],
     'Fix the admin password first and work down the list; hiding the SSID is not security.'),
    ('Moving into a house, you change the front-door lock first, because the builder still has a key. Then you lock the back gate, give '
     'visitors the garden room instead of the house, and keep the alarm serviced. Taking the house number off the gate does not stop a burglar.',
     [('Front-door lock', 'Admin password'), ('Builder’s spare key', 'Default credentials'), ('Back gate', 'Remote (WAN) admin'),
      ('Garden room for visitors', 'Guest network with isolation'), ('Removing the house number', 'Hiding the SSID')],
     'A house number really is hidden when removed; an SSID still appears in client probes, so hiding it gives no real cover.'),
    ('flow', 'SOHO baseline, highest impact first', ['Admin password', 'Remote admin off', 'WPA3 / WPA2 mix', 'WPS off', 'Guest network', 'Firmware updated']),
     'Work left to right. Each box closes a real hole. Hiding the SSID and MAC filtering are deliberately missing.',
    'Order the baseline, then apply it in the Wi-Fi lab and write how to undo each change.',
    order('SOHO baseline', ['Change the admin password', 'Disable remote admin', 'Set WPA3 or transition mode', 'Turn WPS off',
                            'Create a guest network', 'Update firmware'], 'Highest impact first.'), WIFI)

_add('5.4', 'soho-wireless', 'SOHO wireless', 'IT-5.4', S4, [
    ('Does hiding the SSID hide the radio?', 'No, it still transmits', 'Yes, fully invisible', 'Yes, to all phones nearby',
     'The radio still transmits and clients still probe; hiding the name is not security.', HIDE, HIDE),
    ('Changing a shared AP password is…', 'A change to record', 'A quick silent fix', 'A user’s own choice to make',
     'It affects everyone; write what you set and how to undo it.', APCL, APCL),
    ('In the curtain story, what are the curtains?', 'A hidden SSID', 'The admin password', 'Guest isolation',
     'Closed curtains do not lock the door, like a hidden SSID does not secure the network.', HIDE, HIDE),
    ('In the picture, which item is a real control?', 'Guest isolation', 'Hidden network name', 'Hidden router lights',
     'Guest isolation keeps visitors off the LAN; hiding names is not a control.', HIDE, HIDE),
    ('What must the change note include?', 'What was set and the undo', 'Only that it was done', 'The old password written in full',
     'Record the new setting and how to revert; never the password itself.', APCL, APCL),
],
    (['Hiding the network name does not hide the radio.', 'Fix the real things instead.', 'Set a strong admin password.', 'Keep guests apart from the office.',
      'Decide who may join the LAN.', 'A shared access point affects everyone.', 'Changing its password is a change.', 'Write what you set and how to undo it.'],
     'Use real controls, and treat every shared AP setting as a recorded change.'),
    ('Closing the curtains hides who is inside, but the house is still there and the door is unlocked. A real lock, a guest room for '
     'visitors and a list of who has keys keep people out. If you change the lock on a shared flat, you tell your flatmates and keep the old key until it works.',
     [('Closed curtains', 'Hidden SSID'), ('Real lock', 'Admin password and WPA3'), ('Guest room', 'Guest network with isolation'),
      ('Telling flatmates', 'Change record for a shared AP'), ('Keeping the old key', 'Documented undo step')],
     'Curtains do hide some detail; a hidden SSID hides almost nothing, because devices still call out the name.'),
    ('two', 'Real control or cosmetic?', (('Real controls', ['Strong admin password', 'Guest isolation', 'Who may join the LAN']),
                                          ('Cosmetic', ['Hidden SSID', 'MAC filter alone']))),
     'Spend time on the left column. Any change there on a shared AP needs a written note and an undo step.',
    'Sort each setting, then apply one real control in the Wi-Fi lab and write the change note.',
    sort('Real or cosmetic?', {'Real control': ['Change admin password', 'Enable guest isolation', 'Restrict who joins the LAN'],
                               'Cosmetic': ['Hide the SSID', 'Rely on MAC filtering']}, 'Record every shared AP change.'), WIFI)

# ------------------------------------------------------------------ 5.5
_add('5.5', 'core-content', 'Core content', 'IT-5.3', S5, [
    ('Is “the internet is down” a diagnosis?', 'No, it is a symptom', 'Yes, it is complete', 'Yes, if users agree',
     'The sentence is a symptom; the tests decide the failing layer.', TSKIP, TSKIP),
    ('Who changes a DNS zone?', 'The DNS owner', 'The first technician', 'The affected user',
     'Shared equipment belongs to its owner; your evidence lets them act.', TSKIP, FWOFF),
    ('In the doctor story, what is the chart?', 'The ticket note', 'The firewall rule', 'The DNS server list',
     'The chart records each test and result, like the note.', TSKIP, TSKIP),
    ('In the note picture, which line names the failing layer?', 'nslookup: NXDOMAIN', 'Ping gateway 4/4', 'Lease 10.20.30.47/24',
     'NXDOMAIN from the DNS server is the first failing result in the example.', TSKIP, TSKIP),
    ('Which item should NOT be in the note?', 'Firewall off to test', 'Ping gateway 4/4', 'Escalated to DNS owner',
     'Turning the firewall off changes security and tests nothing.', FWOFF, FWOFF),
],
    (['“The internet is down” is what users say.', 'It is never the answer.', 'Work the test order.', 'Write one line per test.',
      'Stop at the layer that fails.', 'Shared kit belongs to its owner.', 'Give them your evidence.', 'Do not reboot or turn things off to see.'],
     'One line per test, stop at the failing layer, and hand shared fixes to their owners.'),
    ('A patient says “I feel ill”. The doctor checks temperature, pulse and blood pressure, writing each one on the chart. The chart '
     'shows which reading was wrong. A specialist reads the chart and acts. Nobody removes an organ “to see”.',
     [('“I feel ill”', '“The internet is down”'), ('Each reading', 'Each test line: lease, gateway, IP, name'), ('Wrong reading', 'First failing layer'),
      ('Specialist', 'Owner of DNS, DHCP or the router'), ('Removing an organ to see', 'Disabling the firewall or resetting settings')],
     'A doctor can examine the whole body; you can only test from the client, so anything beyond is evidence for the owner.'),
    ('flow', 'The internet-is-down note', ['Identity', 'Lease', 'Gateway 4/4', 'Remote IP 4/4', 'Name: NXDOMAIN', 'Escalate to owner'], 4),
     'The red box is the first failing layer in the worked note. Everything after it is a hand-off, not another change.',
    'Order the note lines, then complete the full triage lab with the firewall on.',
    order('Capstone note lines', ['Identity and path', 'Lease from ipconfig', 'Ping gateway', 'Ping remote IP', 'nslookup result', 'Action and owner'],
          'Each line is a test with a result.'), TRI)

_add('5.5', 'pass-bar', 'Pass bar', 'IT-5.3', S5, [
    ('What must you submit to pass?', 'The triage lab and note', 'A screenshot of ping', 'A verbal summary only, no note',
     'The pass bar is the triage lab with a note that would survive 0200.', TSKIP, TSKIP),
    ('What does “survive 0200” mean?', 'Someone can act on it alone', 'It was written at night', 'It is very long and detailed',
     'A night-shift colleague can act on it without calling you.', TSKIP, TSKIP),
    ('In the relay story, what is the handover note?', 'The triage note', 'The firewall rule', 'The ping count',
     'The incoming runner needs everything on the note to keep going.', TSKIP, TSKIP),
    ('In the checklist picture, what must stay on?', 'The firewall', 'The DHCP scope', 'The guest Wi-Fi',
     'The firewall stays on; turning it off fails the bar.', FWOFF, FWOFF),
    ('A trainee turned the firewall off but found the fault. Pass?', 'No, it fails the bar', 'Yes, the fault was found', 'Yes, if turned back on',
     'The bar requires the firewall to stay on throughout.', FWOFF, FWOFF),
],
    (['To pass, three things must be true.', 'You submitted the triage lab.', 'Your note makes sense to someone at 2 a.m.',
      'That person can act without calling you.', 'You never turned the firewall off.', 'Finding the fault is not enough on its own.'],
     'Submit the lab, write a note a night-shift colleague can act on, and keep the firewall on.'),
    ('A night nurse takes over from the day nurse with only the handover sheet. If it says what was tested, what was found and what is '
     'next, the night goes smoothly. If the day nurse switched off an alarm to get a quiet reading, the sheet fails, whatever else it says.',
     [('Handover sheet', 'Triage note'), ('Night nurse', 'Colleague at 0200'), ('Tests and findings', 'Action → result lines'),
      ('Alarm switched off', 'Firewall turned off')],
     'A nurse can phone the day nurse in an emergency; at 0200 you will be asleep, so the note must stand alone.'),
    ('flow', 'Pass bar checklist', ['Lab submitted', 'Note survives 0200', 'Firewall stayed on', 'Pass']),
     'All three boxes before “Pass” must be true. Missing any one of them means the attempt does not pass, even if the fault was found.',
    'Reveal the answer after you judge the attempt.',
    reveal('A note reads “Lease OK, gw 4/4, name NXDOMAIN, escalated to DNS owner. Firewall disabled briefly.” Does it pass?',
           'No. The evidence is good, but the firewall was turned off, which fails the bar.'), TRI)

_add('5.5', 'teach-block-full-triage-as-a-period', 'Teach block — full triage as a period', 'IT-5.3', S5, [
    ('How long is the full-triage block?', 'A full period', 'A five-minute demo', 'A short homework task',
     'This block is a full period, not a quick demo.', TSKIP, TSKIP),
    ('What must every trainee’s note contain?', 'Action → result lines', 'A list of guesses', 'Only the final fix applied',
     'Each line pairs an action with its result.', TSKIP, TSKIP),
    ('In the driving-test story, what is the full drive?', 'The whole triage lab', 'A single ping test', 'Reading the textbook',
     'A full drive tests everything, like completing the full triage lab.', TSKIP, TSKIP),
    ('In the period plan, what comes after the lab?', 'The capstone check', 'Firewall turned off', 'A brand-new lab task',
     'The capstone check follows the completed lab.', TSKIP, FWOFF),
    ('Which rule holds during the period?', 'Firewall stays on', 'Firewall is optional', 'Firewall off to save time',
     'The firewall stays on for every trainee.', FWOFF, FWOFF),
],
    (['This block takes a whole lesson.', 'It is not a quick demo.', 'Every trainee runs the full triage lab.', 'Each one writes a note.',
      'Each line shows an action and its result.', 'The firewall stays on.', 'The capstone check comes after.'],
     'Give the full period to the triage lab, and check every note for action → result.'),
    ('A driving test is a full drive, not a quick turn around the car park. Every learner drives the whole route, the examiner writes '
     'what happened at each junction, and seatbelts stay on. The pass decision comes at the end.',
     [('Full route', 'The whole win-full-triage lab'), ('Examiner’s notes per junction', 'Action → result lines'), ('Seatbelt on', 'Firewall stays on'),
      ('Pass decision at the end', 'Capstone check')],
     'A driving test has one examiner per learner; in class, one instructor checks many notes, so the format must be easy to scan.'),
    ('flow', 'Full triage period', ['Brief the case', 'Every trainee runs the lab', 'Write action → result', 'Firewall checked on', 'Capstone check']),
     'The period moves through these boxes for every trainee. Nobody skips to the check without a complete note.',
    'Order the period, then run the full triage lab yourself as if you were a trainee.',
    order('Period plan', ['Brief the case', 'Run win-full-triage', 'Write action → result', 'Confirm firewall on', 'Capstone check'],
          'It is a full period because the note takes time.'), TRI)
