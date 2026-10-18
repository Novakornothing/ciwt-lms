"""Misconception tags for item-bank distractors (pass 11).

Each tag says which specific wrong idea a distractor signals. Tags were written by reading each item, its
correct answer and its explanation; a distractor is tagged only when the wrong idea it represents is clear
from the item itself. Throw-away distractors (e.g. "Change ticket for paint") are deliberately left untagged.
The labels describe the wrong belief; they add no new curriculum facts. The corrective explanation a student
sees is assembled from existing lesson sections (see mastery/content.py), never from these labels alone.

Coverage (this pass): the most-used objectives by item count across chapter checks and Tests A/B/C:
ITSUP IT-1.1-1.4, IT-5.1, IT-5.3, IT-8.4, IT-10.1, IT-10.3; NETOPS NO-1.2, NO-2.1, NO-2.3, NO-3.1, NO-5.1.

MISCONCEPTIONS[id] = {obj, label (the wrong idea, in plain words), fix (what the lesson shows instead, worded
from the item explanations), terms (words used to find the lesson section that addresses it)}
TAGS[(bank_id, distractor)] = misconception id
"""

MISCONCEPTIONS = {
    # ---- ITSUP chapter 1: the support role
    'MC-IT1-REQ-AS-INC': {'obj': 'IT-1.1', 'label': 'Treating a request for new access or a new item as an incident or break/fix',
                          'fix': 'New access is a service request, not a repair.', 'terms': ['service request', 'incident', 'request']},
    'MC-IT1-SCOPE-IGNORED': {'obj': 'IT-1.1', 'label': 'Classifying by the device involved instead of by how many people are affected',
                             'fix': 'Many users affected plus access control makes it an incident.', 'terms': ['incident', 'impact', 'many users', 'escalate']},
    'MC-IT1-CHANGE-AS-FIX': {'obj': 'IT-1.1', 'label': 'Calling a planned change (adding something new) a repair or an incident',
                             'fix': 'Repairs restore a known-good state; adding a record is a change.', 'terms': ['change', 'repair', 'known-good']},
    'MC-IT1-HANDS-FIRST': {'obj': 'IT-1.1', 'label': 'Going hands-on with hardware before classifying and escalating a hazard',
                           'fix': 'Many users plus heat: classify and escalate; do not open the panel.', 'terms': ['escalate', 'heat', 'panel', 'incident']},
    'MC-IT1-ESD-ORDER': {'obj': 'IT-1.2', 'label': 'Opening or touching parts before the PC is powered off, unplugged and you are grounded',
                         'fix': 'Power off, unplug at the wall, wait, strap on skin, then open.', 'terms': ['unplug', 'strap', 'esd', 'power off']},
    'MC-IT1-ESD-FALSE-PROTECT': {'obj': 'IT-1.2', 'label': 'Believing everyday materials (plastic bags, rubber soles) protect parts from ESD',
                                 'fix': 'A grounded wrist strap and ESD mat keep you and the part at the same potential.', 'terms': ['esd', 'wrist strap', 'mat', 'static']},
    'MC-IT1-SHOCK-AS-SWAP': {'obj': 'IT-1.2', 'label': 'Handling an electrical shock report as a routine part swap',
                             'fix': 'Heat and shock are not solo swaps: stop and escalate.', 'terms': ['shock', 'escalate', 'stop', 'safety']},
    'MC-IT1-VAGUE-NOTES': {'obj': 'IT-1.3', 'label': 'Writing ticket notes as complaints or slogans instead of action and result',
                           'fix': 'A usable note records versions, errors, tests run and what each test showed.', 'terms': ['notes', 'action', 'result', 'ticket']},
    'MC-IT1-CLOSE-EARLY': {'obj': 'IT-1.3', 'label': 'Closing a ticket on a signal (green icon, silence, timer) instead of a verified fix',
                           'fix': 'Closed means the required workflow works and the notes are complete.', 'terms': ['close', 'closed', 'verify', 'workflow']},
    'MC-IT1-TEST-BEFORE-INTAKE': {'obj': 'IT-1.3', 'label': 'Testing or escalating before asking intake questions',
                                  'fix': 'Good intake narrows scope first: who, since when, wired or wireless, what changed.', 'terms': ['intake', 'scope', 'questions', 'since']},
    'MC-IT1-URGENCY-OVER-ID': {'obj': 'IT-1.4', 'label': 'Letting urgency replace identity verification',
                               'fix': 'Urgency is not identity: verify per shop policy first.', 'terms': ['identity', 'verify', 'password reset', 'policy']},
    'MC-IT1-SECRETS-IN-TICKET': {'obj': 'IT-1.4', 'label': 'Recording passwords or opinions in the ticket',
                                 'fix': 'Tickets hold facts, times, tests and the next step; never passwords.', 'terms': ['ticket', 'password', 'facts']},
    # ---- ITSUP chapter 5: client networking
    'MC-IT5-GATEWAY-ROLE': {'obj': 'IT-5.1', 'label': 'Mixing up what the gateway, DHCP and DNS each do',
                            'fix': 'The address identifies the host, the gateway is the door off the LAN, DNS turns names into addresses.', 'terms': ['gateway', 'door', 'dns', 'address']},
    'MC-IT5-APIPA-AS-DNS': {'obj': 'IT-5.1', 'label': 'Reading an APIPA 169.254 address as a DNS problem or a healthy lease',
                            'fix': 'APIPA (169.254.x.x) means no usable DHCP lease; fix the lease or link before DNS.', 'terms': ['apipa', '169.254', 'lease', 'dhcp']},
    'MC-IT5-DNS-ASSIGNS': {'obj': 'IT-5.1', 'label': 'Thinking DNS assigns addresses or routes traffic',
                           'fix': 'DNS turns names into addresses; DHCP assigns them and routers route.', 'terms': ['dns', 'names', 'dhcp', 'route']},
    'MC-IT5-SUBNET-COUNT': {'obj': 'IT-5.1', 'label': 'Counting usable hosts without removing the network and broadcast addresses',
                            'fix': 'Usable hosts are the block size minus the network and broadcast addresses.', 'terms': ['usable', 'broadcast', 'network address', 'prefix', 'hosts']},
    'MC-IT5-BROADCAST-ASSIGNABLE': {'obj': 'IT-5.1', 'label': 'Thinking the network or broadcast address can be given to a host',
                                    'fix': 'The network and broadcast addresses cannot be assigned to a host.', 'terms': ['broadcast', 'network address', 'usable', 'range']},
    'MC-IT5-SKIP-LAYERS': {'obj': 'IT-5.3', 'label': 'Jumping to a fix at a higher layer before the lower layer is proven (e.g. flushing DNS on an APIPA box)',
                           'fix': 'Isolate in a fixed order: link, lease, IP path, then the name path. Do not skip layers.', 'terms': ['order', 'link', 'lease', 'flushdns', 'layer']},
    'MC-IT5-NAME-VS-IP': {'obj': 'IT-5.3', 'label': 'Missing that "IP works, name fails" points to the name / DNS path',
                          'fix': 'If the number works and the name does not, the next domain is the name path.', 'terms': ['name', 'dns', 'ping', 'nslookup']},
    'MC-IT5-RENEW-WITHOUT-LINK': {'obj': 'IT-5.3', 'label': 'Renewing DHCP or flushing DNS when there is no link at the switch port',
                                  'fix': 'No link light means layer 1/2 must be fixed before DHCP can work.', 'terms': ['link', 'port', 'vlan', 'layer 1', 'apipa']},
    'MC-IT5-UPSTREAM-AS-HOST': {'obj': 'IT-5.3', 'label': 'Blaming the host when LAN tests pass and failure starts beyond the gateway',
                                'fix': 'LAN reachability proves the host; failures past the gateway point upstream.', 'terms': ['gateway', 'upstream', 'traceroute', 'routing']},
    'MC-IT5-DNS-CACHE-TTL': {'obj': 'IT-5.3', 'label': 'Blaming ARP, DHCP or switches for old DNS answers instead of cached records (TTL)',
                             'fix': 'Clients and resolvers cache the old record until its TTL expires.', 'terms': ['ttl', 'cache', 'dns', 'record']},
    'MC-IT5-VLAN-AUTO': {'obj': 'IT-5.3', 'label': 'Thinking DHCP or the gateway can move a client into a different VLAN',
                         'fix': 'A client lands in whichever VLAN its switchport is in.', 'terms': ['vlan', 'switchport', 'access port']},
    'MC-IT5-FIREWALL-OFF': {'obj': 'IT-5.3', 'label': 'Turning the firewall off or reimaging as a troubleshooting step',
                            'fix': 'The pass bar is identity, IP and name tests with action and result, not disabling protections.', 'terms': ['firewall', 'triage', 'action', 'result']},
    # ---- ITSUP chapter 8: Windows in a domain
    'MC-IT8-OFFLINE-CACHE': {'obj': 'IT-8.4', 'label': 'Rebuilding the profile or the domain join when the laptop only needs to sign in once on the network',
                             'fix': 'After a reset, sign in once with the domain controller reachable (office or VPN) so cached credentials update.', 'terms': ['cached', 'offline', 'vpn', 'password reset']},
    'MC-IT8-GPO-DENIED-NETWORK': {'obj': 'IT-8.4', 'label': 'Chasing network or disk settings when gpresult says a GPO was denied',
                                  'fix': '"Denied" with the right OU means filtering, inheritance or scope.', 'terms': ['gpresult', 'filtering', 'scope', 'inheritance', 'group policy']},
    'MC-IT8-KERBEROS-SKEW': {'obj': 'IT-8.4', 'label': 'Missing that clock skew breaks Kerberos logons',
                             'fix': 'Kerberos rejects tickets when clocks differ by more than the allowed skew.', 'terms': ['kerberos', 'time', 'clock', 'skew']},
    'MC-IT8-MANUAL-MAPS': {'obj': 'IT-8.4', 'label': 'Using manual or per-PC workarounds where Group Policy should target the group',
                           'fix': 'Group Policy Preferences drive maps can be scoped to a security group.', 'terms': ['drive map', 'group policy', 'preferences', 'targeting']},
    'MC-IT8-GPO-SCOPE-ONSITE': {'obj': 'IT-8.4', 'label': 'Believing Group Policy cannot reach laptops or VPN clients at all',
                                'fix': 'When VPN clients miss a policy, its scope or filter assumes on-site conditions.', 'terms': ['vpn', 'scope', 'filter', 'group policy', 'slow link']},
    # ---- ITSUP chapter 10: security
    'MC-IT10-SHARED-ADMIN': {'obj': 'IT-10.1', 'label': 'Accepting shared or written-down admin passwords when the room or password length seems safe',
                             'fix': 'Shared admin credentials are unaccountable privilege; use named, least-privilege accounts.', 'terms': ['shared', 'admin', 'privilege', 'password']},
    'MC-IT10-PASSWORD-RECORDED': {'obj': 'IT-10.1', 'label': 'Recording user passwords in tickets, chat or notes for a hand-off',
                                  'fix': 'A user\u2019s password goes nowhere you record.', 'terms': ['password', 'ticket', 'chat']},
    'MC-IT10-BROAD-PRIVILEGE': {'obj': 'IT-10.1', 'label': 'Granting broad admin rights (or disabling UAC) where a narrow delegated right would do',
                                'fix': 'Least privilege: delegate only the needed right, with separate MFA admin accounts.', 'terms': ['least privilege', 'local admin', 'uac', 'delegate']},
    'MC-IT10-SECRET-OBSCURE': {'obj': 'IT-10.1', 'label': 'Thinking hiding or encoding an exposed secret makes it safe again',
                               'fix': 'Exposed secrets are compromised: rotate them and move them to a secret store.', 'terms': ['rotate', 'secret', 'credentials', 'repository']},
    'MC-IT10-DISABLE-PROTECTION': {'obj': 'IT-10.3', 'label': 'Treating the firewall, Defender or patching as optional or something to switch off',
                                   'fix': 'Read the firewall profile and patch state as part of hygiene; do not turn protections off.', 'terms': ['firewall', 'defender', 'update', 'patch']},
    'MC-IT10-QUICK-FORMAT': {'obj': 'IT-10.3', 'label': 'Thinking a quick format or profile deletion removes data from a drive',
                             'fix': 'A quick format leaves data recoverable; use cryptographic erase or destruction per policy.', 'terms': ['format', 'erase', 'disposal', 'destruction']},
    'MC-IT10-BITLOCKER-SUSPEND': {'obj': 'IT-10.3', 'label': 'Believing a suspended BitLocker drive is still fully protected',
                                  'fix': 'While suspended, the key is stored unprotected until protection resumes.', 'terms': ['bitlocker', 'suspend', 'recovery key', 'tpm']},
    # ---- NETOPS chapter 1: addressing
    'MC-NO1-HOSTS-NO-SUBTRACT': {'obj': 'NO-1.2', 'label': 'Counting all addresses in a block as usable hosts',
                                'fix': '2^host-bits addresses, minus the network and broadcast addresses.', 'terms': ['usable', 'host bits', 'broadcast', 'subnet']},
    'MC-NO1-WRONG-BLOCK': {'obj': 'NO-1.2', 'label': 'Using the wrong block size for the prefix when finding the broadcast address',
                           'fix': 'Find the block for the prefix (e.g. /27 = 32 addresses); the last address is the broadcast.', 'terms': ['block', 'broadcast', 'prefix', 'subnet']},
    'MC-NO1-IPV6-TYPES': {'obj': 'NO-1.2', 'label': 'Mixing up IPv6 link-local, unique-local and global addresses',
                          'fix': 'fe80::/10 is link-local: every interface has one and it is never routed.', 'terms': ['link-local', 'fe80', 'ipv6', 'global']},
    'MC-NO1-PRIVATE-RANGES': {'obj': 'NO-1.2', 'label': 'Calling APIPA or carrier-grade NAT space "private" (RFC 1918)',
                              'fix': '169.254.0.0/16 is link-local and 100.64.0.0/10 is shared CGN space; neither is RFC 1918.', 'terms': ['private', 'rfc 1918', '169.254', '100.64']},
    'MC-NO1-MASK-ONLINK': {'obj': 'NO-1.2', 'label': 'Missing that a wrong mask makes on-link hosts look remote',
                           'fix': 'With too long a mask the host sends some on-link traffic to the gateway.', 'terms': ['mask', 'on-link', 'gateway', 'prefix']},
    # ---- NETOPS chapter 2: switching and cabling
    'MC-NO2-UNKNOWN-UNICAST': {'obj': 'NO-2.1', 'label': 'Thinking a switch drops, ARPs for, or routes a frame to an unknown MAC',
                               'fix': 'Unknown unicast is flooded within the VLAN; the switch learns from the reply.', 'terms': ['flood', 'mac address table', 'unknown unicast', 'learn']},
    'MC-NO2-LOOP-MISSED': {'obj': 'NO-2.1', 'label': 'Blaming DHCP, DNS or duplex for a floor-wide slowdown after a cable joined two jacks',
                           'fix': 'Two jacks on one switch form a layer-2 loop and a broadcast storm.', 'terms': ['loop', 'broadcast storm', 'stp', 'bpdu guard']},
    'MC-NO2-STP-PURPOSE': {'obj': 'NO-2.1', 'label': 'Confusing STP blocking with load-balancing, VLAN isolation or LACP',
                           'fix': 'STP blocks a redundant port to prevent loops while keeping the path available.', 'terms': ['stp', 'blocking', 'redundant', 'loop']},
    'MC-NO2-DEVICE-LAYER': {'obj': 'NO-2.1', 'label': 'Mixing up hubs, switches and routers by the layer they work at',
                            'fix': 'A switch learns MAC addresses and forwards per port; a hub repeats to all ports; routers work at layer 3.', 'terms': ['switch', 'hub', 'router', 'layer 2']},
    'MC-NO2-COPPER-LENGTH': {'obj': 'NO-2.3', 'label': 'Using copper Ethernet beyond its 100 m channel',
                             'fix': 'Copper channels are 100 m; longer runs need fibre.', 'terms': ['100 m', 'copper', 'channel', 'fibre']},
    'MC-NO2-WRONG-TOOL': {'obj': 'NO-2.3', 'label': 'Choosing a test tool that measures something else (copper vs optical vs tracing)',
                          'fix': 'Toner and probe trace a jack, an optical power meter measures light, an OTDR finds fibre breaks.', 'terms': ['toner', 'probe', 'optical power meter', 'otdr', 'certifier']},
    'MC-NO2-FIBRE-MODE': {'obj': 'NO-2.3', 'label': 'Mixing up where single-mode and multimode fibre are used',
                          'fix': 'Single-mode carries over kilometres; multimode suits shorter in-building runs.', 'terms': ['single-mode', 'multimode', 'fibre', 'distance']},
    # ---- NETOPS chapter 3: routing
    'MC-NO3-SHORTER-PREFIX': {'obj': 'NO-3.1', 'label': 'Thinking a router picks the broader or default route instead of the longest match',
                              'fix': 'Routers choose the longest matching prefix; the default route is used only when nothing else matches.', 'terms': ['longest', 'prefix', 'match', 'default route']},
    'MC-NO3-AD-DYNAMIC-WINS': {'obj': 'NO-3.1', 'label': 'Thinking dynamic or first-learned routes beat static ones for the same prefix',
                               'fix': 'For equal prefixes the lower administrative distance wins: static (1) beats OSPF (110).', 'terms': ['administrative distance', 'static', 'ospf']},
    'MC-NO3-TRACEROUTE-STARS': {'obj': 'NO-3.1', 'label': 'Reading * * * at one traceroute hop as a broken path when later hops answer',
                                'fix': 'If later hops answer, the silent router is forwarding and only ignoring probes.', 'terms': ['traceroute', 'hop', 'probe']},
    'MC-NO3-FHRP-PURPOSE': {'obj': 'NO-3.1', 'label': 'Confusing first-hop redundancy (HSRP/VRRP) with aggregation, STP or routing protocols',
                            'fix': 'HSRP/VRRP let two routers share a virtual default-gateway address.', 'terms': ['hsrp', 'vrrp', 'gateway', 'redundancy']},
    # ---- NETOPS chapter 5: monitoring
    'MC-NO5-SYSLOG-ORDER': {'obj': 'NO-5.1', 'label': 'Reading higher syslog numbers as more severe',
                            'fix': 'Syslog runs 0 (emergency) to 7 (debug): lower numbers are more severe.', 'terms': ['syslog', 'severity']},
    'MC-NO5-CRC-AS-LOAD': {'obj': 'NO-5.1', 'label': 'Reading CRC errors as congestion or a logical fault instead of a physical one',
                           'fix': 'CRC errors mean corrupted frames: cabling, connectors, optics or interference.', 'terms': ['crc', 'errors', 'cable', 'interface']},
    'MC-NO5-BASELINE-PURPOSE': {'obj': 'NO-5.1', 'label': 'Not seeing that a baseline is the reference that makes readings meaningful',
                                'fix': 'Without a baseline, "high" has no reference.', 'terms': ['baseline', 'normal', 'abnormal']},
    'MC-NO5-SINGLE-SAMPLE': {'obj': 'NO-5.1', 'label': 'Using a single sample or unrelated counter to prove a trend such as saturation',
                             'fix': 'Saturation is proven by utilisation and drops over time.', 'terms': ['utilisation', 'drops', 'over time', 'saturation']},
}

_T = [
    # IT-1.1
    ('Q1.0', 'Incident', 'MC-IT1-REQ-AS-INC'), ('Q1.0', 'Break/fix', 'MC-IT1-REQ-AS-INC'),
    ('Q1.1', 'Break/fix for one reader', 'MC-IT1-SCOPE-IGNORED'), ('Q1.1', 'Service request for new badges', 'MC-IT1-SCOPE-IGNORED'),
    ('Q1.6', 'A repair', 'MC-IT1-CHANGE-AS-FIX'), ('Q1.6', 'An incident', 'MC-IT1-CHANGE-AS-FIX'),
    ('Q1.8', 'Open the reader panel first', 'MC-IT1-HANDS-FIRST'), ('Q1.8', 'classify request, impact 1, escalate no', 'MC-IT1-SCOPE-IGNORED'),
    ('Q1.8', 'classify break-fix, impact 1, escalate no', 'MC-IT1-SCOPE-IGNORED'),
    # IT-1.2
    ('Q1.4', 'Strap over a sleeve, then pull the RAM', 'MC-IT1-ESD-ORDER'), ('Q1.4', 'Open the case first, then unplug it', 'MC-IT1-ESD-ORDER'),
    ('Q1.5', 'Swap the strip as break/fix', 'MC-IT1-SHOCK-AS-SWAP'), ('Q1.5', 'Open the PSU to look', 'MC-IT1-SHOCK-AS-SWAP'),
    ('Q1.5', 'Ignore it if the PC still boots', 'MC-IT1-SHOCK-AS-SWAP'),
    ('A1.37', 'Storing modules in a plastic bag', 'MC-IT1-ESD-FALSE-PROTECT'), ('A1.37', 'Rubber-soled shoes', 'MC-IT1-ESD-FALSE-PROTECT'),
    # IT-1.3
    ('Q1.3', 'VPN is broken again, user says it worked last week and wants it fixed fast', 'MC-IT1-VAGUE-NOTES'),
    ('Q1.3', 'User cannot connect, tried rebooting, please look into it when you have time', 'MC-IT1-VAGUE-NOTES'),
    ('Q1.3', 'Hotel Wi-Fi is bad, told the user to find a better network and call back later', 'MC-IT1-VAGUE-NOTES'),
    ('Q1.9', 'The monitoring icon turned green', 'MC-IT1-CLOSE-EARLY'), ('Q1.9', 'The user stopped responding', 'MC-IT1-CLOSE-EARLY'),
    ('Q1.9', 'The SLA timer expired', 'MC-IT1-CLOSE-EARLY'),
    ('A1.38', 'Run a speed test and close the ticket', 'MC-IT1-TEST-BEFORE-INTAKE'), ('A1.38', 'Restart the PC first and see if it helps', 'MC-IT1-TEST-BEFORE-INTAKE'),
    ('A1.38', 'Escalate to the network team at once', 'MC-IT1-TEST-BEFORE-INTAKE'),
    # IT-1.4
    ('Q1.2', 'Reset it and sort identity later', 'MC-IT1-URGENCY-OVER-ID'),
    ('Q1.7', 'The user\u2019s password, so the next technician can test', 'MC-IT1-SECRETS-IN-TICKET'), ('Q1.7', 'Your opinion of the user', 'MC-IT1-SECRETS-IN-TICKET'),
    # IT-5.1
    ('Q5.0', 'Replaces DNS', 'MC-IT5-GATEWAY-ROLE'), ('Q5.0', 'Assigns MAC addresses', 'MC-IT5-GATEWAY-ROLE'),
    ('Q5.1', 'The DNS server is down', 'MC-IT5-APIPA-AS-DNS'), ('Q5.1', 'A healthy DHCP lease', 'MC-IT5-APIPA-AS-DNS'), ('Q5.1', 'DNS is working', 'MC-IT5-APIPA-AS-DNS'),
    ('Q5.2', 'Assigns IP addresses', 'MC-IT5-DNS-ASSIGNS'), ('Q5.2', 'Routes packets between networks', 'MC-IT5-DNS-ASSIGNS'),
    ('A3.2', '4', 'MC-IT5-SUBNET-COUNT'),
    # IT-5.3
    ('Q5.3', 'Restart the DHCP server', 'MC-IT5-NAME-VS-IP'), ('Q5.3', 'Replace the NIC', 'MC-IT5-NAME-VS-IP'),
    ('Q5.4', 'Yes, always first', 'MC-IT5-SKIP-LAYERS'), ('Q5.4', 'Yes instead of ipconfig', 'MC-IT5-SKIP-LAYERS'),
    ('Q5.9', 'Firewall off, then retest the app', 'MC-IT5-FIREWALL-OFF'), ('Q5.9', 'Reimage first, then test the network', 'MC-IT5-FIREWALL-OFF'),
    ('A1.12', 'The host\u2019s DNS settings', 'MC-IT5-UPSTREAM-AS-HOST'), ('A1.12', 'The host\u2019s NIC driver', 'MC-IT5-UPSTREAM-AS-HOST'),
    ('A1.15', 'Stale ARP entries on the router', 'MC-IT5-DNS-CACHE-TTL'), ('A1.15', 'Client DHCP leases', 'MC-IT5-DNS-CACHE-TTL'),
    ('A1.15', 'The switches learning the new address', 'MC-IT5-DNS-CACHE-TTL'),
    ('A1.18', 'Flush the DNS cache on the PC', 'MC-IT5-RENEW-WITHOUT-LINK'), ('A1.18', 'Release and renew the DHCP lease', 'MC-IT5-RENEW-WITHOUT-LINK'),
    ('A1.18', 'Restart the DHCP server for the scope', 'MC-IT5-RENEW-WITHOUT-LINK'),
    ('A2.9', 'DHCP moves it to VLAN 40 automatically', 'MC-IT5-VLAN-AUTO'), ('A2.9', 'It reaches VLAN 40 through the default gateway', 'MC-IT5-VLAN-AUTO'),
    # IT-8.4
    ('A1.24', 'Rejoin the laptop to the domain', 'MC-IT8-OFFLINE-CACHE'), ('A1.24', 'Delete and recreate the user profile', 'MC-IT8-OFFLINE-CACHE'),
    ('A1.26', 'DNS suffix order and IP configuration', 'MC-IT8-GPO-DENIED-NETWORK'), ('A1.26', 'BitLocker status and TPM ownership', 'MC-IT8-GPO-DENIED-NETWORK'),
    ('A1.26', 'Local firewall profile and update status', 'MC-IT8-GPO-DENIED-NETWORK'),
    ('A1.28', 'Expired DNS records on the client', 'MC-IT8-KERBEROS-SKEW'), ('A1.28', 'A corrupt local user profile', 'MC-IT8-KERBEROS-SKEW'),
    ('A1.29', 'Asking users to run net use', 'MC-IT8-MANUAL-MAPS'), ('A1.29', 'A hosts-file entry on each PC', 'MC-IT8-MANUAL-MAPS'),
    ('A2.10', 'Group Policy cannot apply to laptops', 'MC-IT8-GPO-SCOPE-ONSITE'), ('A2.10', 'VPN clients cannot use SMB at all', 'MC-IT8-GPO-SCOPE-ONSITE'),
    # IT-10.1
    ('Q10.1', 'Yes, in a locked room', 'MC-IT10-SHARED-ADMIN'), ('Q10.1', 'Yes, if the password is long', 'MC-IT10-SHARED-ADMIN'),
    ('Q10.1', 'Yes, it is required for shared PCs', 'MC-IT10-SHARED-ADMIN'),
    ('Q10.5', 'In the ticket notes', 'MC-IT10-PASSWORD-RECORDED'), ('Q10.5', 'In team chat for the hand-off', 'MC-IT10-PASSWORD-RECORDED'),
    ('Q10.5', 'On a sticky note for the next shift', 'MC-IT10-PASSWORD-RECORDED'),
    ('A1.31', 'One shared help-desk admin account', 'MC-IT10-SHARED-ADMIN'), ('A1.31', 'Local admin rights for all staff', 'MC-IT10-BROAD-PRIVILEGE'),
    ('A1.41', 'Disable UAC for that user', 'MC-IT10-BROAD-PRIVILEGE'), ('A1.41', 'Share the help-desk admin password', 'MC-IT10-SHARED-ADMIN'),
    ('A2.12', 'The user\u2019s own admin account', 'MC-IT10-BROAD-PRIVILEGE'), ('A2.12', 'A Domain Admin account for reliability', 'MC-IT10-BROAD-PRIVILEGE'),
    ('A1.45', 'Encode the password in Base64', 'MC-IT10-SECRET-OBSCURE'), ('A1.45', 'Make the repository private and keep them', 'MC-IT10-SECRET-OBSCURE'),
    ('A1.45', 'Delete the file in the latest commit only', 'MC-IT10-SECRET-OBSCURE'),
    # IT-10.3
    ('Q10.0', 'Turn it off for games', 'MC-IT10-DISABLE-PROTECTION'), ('Q10.0', 'Only after malware', 'MC-IT10-DISABLE-PROTECTION'),
    ('Q10.6', 'Optional trivia', 'MC-IT10-DISABLE-PROTECTION'), ('Q10.6', 'A reason to disable Defender', 'MC-IT10-DISABLE-PROTECTION'),
    ('A1.39', 'A quick format', 'MC-IT10-QUICK-FORMAT'), ('A1.39', 'Deleting the user profiles', 'MC-IT10-QUICK-FORMAT'),
    ('A1.39', 'Reset this PC with \u201cKeep my files\u201d', 'MC-IT10-QUICK-FORMAT'),
    ('A1.33', 'None \u2014 the drive stays fully protected', 'MC-IT10-BITLOCKER-SUSPEND'),
    # NO-1.2
    ('NQ1.2', '64', 'MC-NO1-HOSTS-NO-SUBTRACT'), ('NQ1.3', '172.16.5.127', 'MC-NO1-WRONG-BLOCK'), ('NQ1.3', '172.16.5.96', 'MC-NO1-WRONG-BLOCK'),
    ('NQ1.4', 'Unique local', 'MC-NO1-IPV6-TYPES'), ('NQ1.4', 'Global unicast', 'MC-NO1-IPV6-TYPES'),
    ('N2.9', '16', 'MC-NO1-HOSTS-NO-SUBTRACT'), ('N1.29', '169.254.0.0/16', 'MC-NO1-PRIVATE-RANGES'), ('N1.29', '100.64.0.0/10', 'MC-NO1-PRIVATE-RANGES'),
    ('N2.12', 'DNS rejects hosts with the wrong mask', 'MC-NO1-MASK-ONLINK'), ('N2.12', 'ARP does not work with a /24 mask', 'MC-NO1-MASK-ONLINK'),
    # NO-2.1
    ('NQ2.0', 'Drops the frame', 'MC-NO2-UNKNOWN-UNICAST'), ('NQ2.0', 'Asks the router with ARP', 'MC-NO2-UNKNOWN-UNICAST'),
    ('NQ2.0', 'Sends it to the default gateway', 'MC-NO2-UNKNOWN-UNICAST'),
    ('NQ2.1', 'A DHCP scope running out', 'MC-NO2-LOOP-MISSED'), ('NQ2.1', 'A DNS server failure', 'MC-NO2-LOOP-MISSED'),
    ('NQ2.1', 'A duplex mismatch on one port', 'MC-NO2-LOOP-MISSED'),
    ('N1.3', 'Load-balance across both links', 'MC-NO2-STP-PURPOSE'), ('N1.3', 'Isolate VLANs from each other', 'MC-NO2-STP-PURPOSE'),
    ('N3.3', 'Block redundant links to prevent loops', 'MC-NO2-STP-PURPOSE'),
    ('N1.5', 'Hub (repeater)', 'MC-NO2-DEVICE-LAYER'), ('N1.5', 'Router', 'MC-NO2-DEVICE-LAYER'),
    # NO-2.3
    ('NQ2.5', '185 m', 'MC-NO2-COPPER-LENGTH'), ('NQ2.5', '300 m', 'MC-NO2-COPPER-LENGTH'),
    ('NQ2.6', 'Cat6A copper', 'MC-NO2-COPPER-LENGTH'), ('NQ2.6', 'Cat5e with a repeater', 'MC-NO2-COPPER-LENGTH'),
    ('NQ2.7', 'Optical power meter', 'MC-NO2-WRONG-TOOL'), ('NQ2.7', 'Loopback plug', 'MC-NO2-WRONG-TOOL'),
    ('N1.12', 'Copper cable certifier', 'MC-NO2-WRONG-TOOL'), ('N1.12', 'Tone generator and probe', 'MC-NO2-WRONG-TOOL'),
    ('N3.7', 'Measure crosstalk on copper', 'MC-NO2-WRONG-TOOL'), ('N3.7', 'Trace a wall jack to its port', 'MC-NO2-WRONG-TOOL'),
    ('N2.5', 'Connections to desktop PCs', 'MC-NO2-FIBRE-MODE'), ('N2.5', 'Short patch cords inside a rack', 'MC-NO2-FIBRE-MODE'),
    # NO-3.1
    ('NQ3.0', '10.0.0.0/8', 'MC-NO3-SHORTER-PREFIX'), ('NQ3.0', 'The default route', 'MC-NO3-SHORTER-PREFIX'),
    ('NQ3.1', 'The OSPF route (dynamic wins)', 'MC-NO3-AD-DYNAMIC-WINS'), ('NQ3.1', 'Whichever was learned first', 'MC-NO3-AD-DYNAMIC-WINS'),
    ('NQ3.2', 'Only the local subnet', 'MC-NO3-SHORTER-PREFIX'),
    ('N1.24', 'The path is broken at that hop', 'MC-NO3-TRACEROUTE-STARS'), ('N1.24', 'The destination host is down', 'MC-NO3-TRACEROUTE-STARS'),
    ('N1.23', 'Link aggregation', 'MC-NO3-FHRP-PURPOSE'), ('N1.23', 'Layer-2 loop prevention', 'MC-NO3-FHRP-PURPOSE'),
    ('N1.23', 'Dynamic route exchange', 'MC-NO3-FHRP-PURPOSE'),
    # NO-5.1
    ('NQ5.0', '5 (notice)', 'MC-NO5-SYSLOG-ORDER'),
    ('NQ5.1', 'The link is saturated by traffic', 'MC-NO5-CRC-AS-LOAD'), ('NQ5.1', 'A routing loop upstream', 'MC-NO5-CRC-AS-LOAD'),
    ('NQ5.1', 'A DNS failure on the network', 'MC-NO5-CRC-AS-LOAD'),
    ('NQ5.2', 'So the switch runs faster', 'MC-NO5-BASELINE-PURPOSE'),
    ('N3.2', 'A single ping time to the far end', 'MC-NO5-SINGLE-SAMPLE'), ('N3.2', 'The router\u2019s uptime counter', 'MC-NO5-SINGLE-SAMPLE'),
]
TAGS = {(b, d): mc for b, d, mc in _T if mc}

# pass 13: every remaining chapter-check objective (ITSUP 2.1–13.3, NETOPS 1.1–9.2), same rules
from curriculum_v2 import misconceptions_pass13 as _p13  # noqa: E402
MISCONCEPTIONS.update(_p13.MISCONCEPTIONS)
TAGS.update(_p13.TAGS)

# pass 14: the new chapter-check items for IT-7.4 … IT-13.4 (curriculum_v2/checks_pass14.py), same rules
from curriculum_v2 import checks_pass14 as _p14  # noqa: E402
MISCONCEPTIONS.update(_p14.MISCONCEPTIONS)
TAGS.update(_p14.TAGS)

# pass 12 (content round 2): certification-item tags (MC-C-* ids, same schema) so the engine sees them
from curriculum_v2.cert import misconceptions as _cert_mc  # noqa: E402
MISCONCEPTIONS.update(_cert_mc.MISCONCEPTIONS)
TAGS.update(_cert_mc.TAGS)

# content round 3: Tests A/B/C and the remaining untagged chapter-check items (curriculum_v2/misconceptions_round3.py), same
# rules; every new entry carries a primary `source` and status 'Pending SME review'
from curriculum_v2 import misconceptions_round3 as _r3  # noqa: E402
MISCONCEPTIONS.update(_r3.MISCONCEPTIONS)
TAGS.update(_r3.TAGS)

# content round 4: pass-15 cert gap items get a source + Pending SME review status on their misconceptions, five more
# tags, and the last two untagged chapter checks (Q13.6, NQ5.5) are tagged (curriculum_v2/misconceptions_round4.py)
from curriculum_v2 import misconceptions_round4 as _r4  # noqa: E402
MISCONCEPTIONS.update(_r4.MISCONCEPTIONS)
TAGS.update(_r4.TAGS)
for _k, _ann in _r4.p15_annotations().items():
    MISCONCEPTIONS[_k] = dict(MISCONCEPTIONS[_k], **{f: v for f, v in _ann.items() if v and not MISCONCEPTIONS[_k].get(f)})

# content round 5: the X-IT expansion bank and the exam supplement (161 items, 0 tagged before) get tags on the
# distractors whose wrong idea the item explanation names; 66 new MC-R5-* entries, each with a primary `source` and
# status 'Pending SME review' (curriculum_v2/misconceptions_round5.py)
from curriculum_v2 import misconceptions_round5 as _r5  # noqa: E402
MISCONCEPTIONS.update(_r5.MISCONCEPTIONS)
TAGS.update(_r5.TAGS)

# pass 15: option-length parity rewrote some distractors (curriculum_v2/parity_pass15.py). The rewritten text keeps
# the same wrong idea, so its tag moves to the new text (tags must point at distractors that are actually shown).
from curriculum_v2 import parity_pass15 as _par15  # noqa: E402
for _b, _rw in _par15.REWRITE.items():
    for _old, _new in _rw.items():
        if (_b, _old) in TAGS:
            TAGS[(_b, _new)] = TAGS.pop((_b, _old))


def _norm(s):
    return ' '.join((s or '').replace('\u2019', "'").lower().split())


_NORM = {(b, _norm(d)): mc for (b, d), mc in TAGS.items()}


def tag_for(item, answer):
    """The misconception id signalled by choosing ``answer`` on ``item`` (dict with bank_id, obj), or None."""
    if not item or answer is None or answer == item.get('correct'):
        return None
    mc = _NORM.get((item.get('bank_id'), _norm(answer)))
    if mc and MISCONCEPTIONS[mc]['obj'] == item.get('obj'):
        return mc
    return None


def coverage():
    """(objectives covered, tags, misconceptions) for the notes and tests."""
    return sorted({m['obj'] for m in MISCONCEPTIONS.values()}), len(TAGS), len(MISCONCEPTIONS)
