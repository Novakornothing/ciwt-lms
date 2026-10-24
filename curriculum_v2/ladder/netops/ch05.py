"""Explanation ladder — NETOPS chapter 5 (Monitoring, Management and Security). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Facts follow the lesson and the primary sources named in each rung.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 5

L = 'Course lesson {} (the original section), re-explained'
MON = 'RFC 5424 (syslog severities); RFC 3411–3418 and RFC 3414 (SNMPv3 USM); RFC 7011 (IPFIX); RFC 3954 (NetFlow v9); RFC 5905 (NTP)'
MGMT = 'RFC 4253 (SSH transport); RFC 8907 (TACACS+); RFC 2865 (RADIUS); NIST SP 800-123 and vendor hardening guides (e.g. Cisco IOS hardening guide)'
VPN = 'NIST SP 800-77 Rev. 1 (IPsec VPNs); NIST SP 800-113 (SSL VPNs); CompTIA Network+ N10-009 objective 3.5'
SEG = 'NIST SP 800-207 (zero trust); NIST SP 800-41 Rev. 1 (firewall policy); IEEE Std 802.1X-2020 (port-based access control)'
ATK = 'RFC 4987 (SYN flooding); RFC 826 (ARP); IEEE Std 802.1Q (native VLAN); CISA “Understanding Denial-of-Service Attacks”; CompTIA Network+ N10-009 objectives 4.1 and 4.2'
DEF = 'IEEE Std 802.1X-2020; NIST SP 800-41 Rev. 1; NIST SP 800-57 Part 1 Rev. 5 (key management); CompTIA Network+ N10-009 objective 4.3'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO5-TRAP-VS-POLL': {
        'obj': 'NO-5.1', 'label': 'Mixing up SNMP polling (manager asks, UDP 161) with traps/informs (device sends, UDP 162)',
        'fix': 'Polling is the NMS reading counters on a schedule; traps and informs are alerts the device pushes.',
        'terms': ['snmp', 'trap', 'poll', '161', '162'], 'source': L.format('5.1') + '; RFC 3416', 'review': R},
    'MC-L-NO5-NO-NTP': {
        'obj': 'NO-5.1', 'label': 'Correlating logs from several devices without a common time source',
        'fix': 'Point every device at the same NTP sources, or timestamps cannot be lined up across devices.',
        'terms': ['ntp', 'timestamp', 'correlate'], 'source': L.format('5.1') + '; RFC 5905', 'review': R},
    'MC-L-NO5-AAA-PROTOCOLS': {
        'obj': 'NO-5.2', 'label': 'Mixing up TACACS+ (device admin, per-command authorisation, TCP 49) and RADIUS (network access)',
        'fix': 'TACACS+ separates AAA and can authorise individual commands; RADIUS is typical for 802.1X and VPN access.',
        'terms': ['tacacs+', 'radius', 'aaa', 'authorisation'], 'source': L.format('5.2') + '; RFC 8907; RFC 2865', 'review': R},
    'MC-L-NO5-NO-LOCAL-ACCOUNT': {
        'obj': 'NO-5.2', 'label': 'Removing every local admin account once AAA is in place',
        'fix': 'Keep one vaulted local emergency account for when the AAA servers or the path to them are down.',
        'terms': ['local account', 'aaa', 'emergency'], 'source': L.format('5.2'), 'review': R},
    'MC-L-NO5-VPN-TYPES': {
        'obj': 'NO-5.2', 'label': 'Mixing up site-to-site, client-to-site and clientless VPNs, or split and full tunnels',
        'fix': 'Pick the VPN type by who connects; pick split or full tunnel by how much traffic the company must inspect.',
        'terms': ['site-to-site', 'client-to-site', 'clientless', 'split tunnel', 'full tunnel'], 'source': L.format('5.2') + '; ' + VPN, 'review': R},
    'MC-L-NO5-INBAND-ONLY': {
        'obj': 'NO-5.2', 'label': 'Relying only on in-band management, so a bad change locks everyone out',
        'fix': 'Out-of-band access (console server, management network, cellular) works when production is down.',
        'terms': ['out-of-band', 'in-band', 'console', 'jump host'], 'source': L.format('5.2') + '; ' + VPN, 'review': R},
    'MC-L-NO5-INSIDE-TRUSTED': {
        'obj': 'NO-5.3', 'label': 'Granting access because a device is “inside” the network',
        'fix': 'Zero trust verifies identity and device health for each request and allows only what is needed.',
        'terms': ['zero trust', 'least privilege', 'inside'], 'source': L.format('5.3') + '; NIST SP 800-207', 'review': R},
    'MC-L-NO5-ATTACK-CONTROL': {
        'obj': 'NO-5.3', 'label': 'Pairing a layer-2 attack with the wrong switch control',
        'fix': 'MAC flooding → port security; rogue DHCP → DHCP snooping; ARP poisoning → DAI; VLAN hopping → no DTP, unused native VLAN.',
        'terms': ['port security', 'dhcp snooping', 'dynamic arp inspection', 'vlan hopping'], 'source': L.format('5.3') + '; ' + ATK, 'review': R},
    'MC-L-NO5-MAC-FILTER-STRONG': {
        'obj': 'NO-5.3', 'label': 'Thinking MAC filtering is a strong control on its own',
        'fix': 'MAC addresses are easy to spoof; use 802.1X/NAC and treat MAC filtering as a minor extra at most.',
        'terms': ['mac filtering', 'spoof', '802.1x'], 'source': L.format('5.3') + '; IEEE 802.1X-2020', 'review': R},
    'MC-L-NO5-URL-VS-CONTENT': {
        'obj': 'NO-5.3', 'label': 'Mixing up URL filtering (site or category) with content filtering (what is fetched)',
        'fix': 'URL filtering decides by address or category; content filtering inspects file types or malware in what is fetched.',
        'terms': ['url filtering', 'content filtering'], 'source': L.format('5.3'), 'review': R},
}

SYS, CRC, BASE, SAMP, FLOW, LOCAL, JIT = ('MC-NO5-SYSLOG-ORDER', 'MC-NO5-CRC-AS-LOAD', 'MC-NO5-BASELINE-PURPOSE', 'MC-NO5-SINGLE-SAMPLE',
                                          'MC-R3-NO5-FLOW', 'MC-R3-NO5-LOCAL-LOGS', 'MC-R3-NO5-JITTER')
TRAP, NTP = 'MC-L-NO5-TRAP-VS-POLL', 'MC-L-NO5-NO-NTP'
SNMPV, WEAK, AAA, LOCALA, VPNT, OOB = ('MC-NO5-SNMP-VERSIONS', 'MC-NO5-WEAK-MGMT', 'MC-L-NO5-AAA-PROTOCOLS', 'MC-L-NO5-NO-LOCAL-ACCOUNT',
                                       'MC-L-NO5-VPN-TYPES', 'MC-L-NO5-INBAND-ONLY')
SSIDS, PRIN, SEC, INSIDE, ATC, MACF, URLC = ('MC-NO5-SSID-AS-SEGMENT', 'MC-NO5-PRINCIPLE-MIXUP', 'MC-C-NO5-SEC-CONCEPT', 'MC-L-NO5-INSIDE-TRUSTED',
                                             'MC-L-NO5-ATTACK-CONTROL', 'MC-L-NO5-MAC-FILTER-STRONG', 'MC-L-NO5-URL-VS-CONTENT')

_TXT = {
    'incident-application': ('Incident application', 'activity', 'A practice drill (write a ticket timeline and a status sentence); it applies the lesson rather than explaining a concept.'),
    'standard-of-work': ('Standard of work', 'reference', 'A two-line list of work-habit reminders (record negative results; no untracked parallel changes) repeated in every lesson.'),
    'practice-standard-for-this-lesson': ('Practice standard for this lesson', 'activity', 'A self-study instruction to build a 5–9 step checklist; it is an exercise, not an explanation.'),
    'beyond-the-quiz': ('Beyond the quiz', 'activity', 'A study-skills prompt (write your own scenario, explain to a non-technical user); an exercise, not a concept.'),
}


def _filler(summary):
    out = {'core-concepts': same_as('core-content', 'Core concepts', summary)}
    out.update({k: skip(*v) for k, v in _TXT.items()})
    return out


LESSONS = {
    '5.1': {
        'core-content': section(
            'Core content', 'NO-5.1',
            [check('An interface shows rising CRC errors but low utilisation. What do you suspect first?',
                   'The physical layer: cable, optic or duplex', ['Congestion from too much traffic on the link',
                    'A routing loop somewhere upstream of the switch'],
                   'CRC errors mean frames arrived damaged, which points at cabling, optics or a duplex mismatch. Low utilisation '
                   'rules out congestion, and routing loops do not corrupt frames.', mc=[CRC, CRC])],
            plain('''<p>Monitoring tells you what “normal” looks like, so you can spot what is not.</p>
<ul><li><strong>SNMP polling</strong>: the monitoring server asks each device for counters, on a schedule.</li>
<li><strong>SNMP traps</strong>: the device sends an alert by itself.</li>
<li><strong>Syslog</strong>: event messages. Lower numbers are worse: 0 is Emergency, 7 is Debug.</li>
<li><strong>Flow data</strong>: who talked to whom, and how much.</li></ul>
<p>Watch errors (CRC means a physical fault), drops, and use over time, not one reading.</p>
<p>A <strong>baseline</strong> is a record of normal. Without one, a number means little.</p>
<p>Use SNMPv3, and give every device the same time source (NTP).</p>''',
                  L.format('5.1') + '; ' + MON,
                  [check('Is syslog severity 2 more or less severe than 5?', 'More severe (2 is Critical)', ['Less severe (5 is Critical)', 'The same, the number is just a category'],
                         'Syslog levels run from 0 (Emergency) to 7 (Debug), so a lower number is more severe: 2 is Critical and 5 is '
                         'Notice. The numbers are an ordered scale, not unordered categories.', mc=[SYS, SYS])]),
            analogy('''<p>Think of a hospital ward.</p>
<p>A nurse doing rounds every hour, reading each patient’s temperature and pulse, is <strong>SNMP polling</strong>. A patient pressing the call
button is a <strong>trap</strong>. The ward diary of everything that happened, each entry marked from “life-threatening” down to “routine”, is
<strong>syslog</strong>. The visitor log showing who came to see whom and for how long is <strong>flow data</strong>.</p>
<p>A temperature of 37.5 °C only means something if you know the patient’s normal: the <strong>baseline</strong>. A single high reading is not a
trend. And if every clock on the ward shows a different time, nobody can work out what happened first: that is why every device uses
<strong>NTP</strong>.</p>''',
                    L.format('5.1') + ' (hospital analogy written for this rung); ' + MON,
                    [check('In the hospital story, a patient presses the call button. Which SNMP mechanism is that?', 'A trap or inform from the device',
                           ['A scheduled poll from the monitoring server', 'A flow record of who talked to whom'],
                           'Traps and informs are pushed by the device when something happens (UDP 162). Polling is the manager asking '
                           'on a schedule, and flows record conversations.', mc=[TRAP, FLOW])]),
            visual('''<ol class="ladder-trace"><li>Complaint: “the WAN is slow every afternoon”.</li>
<li>Pull <strong>utilisation over weeks</strong> from SNMP polling, not one sample: is 14:00–16:00 higher than the baseline?</li>
<li>Check <strong>output drops</strong> at the same times: sustained high use plus drops means congestion.</li>
<li>Check <strong>CRC/input errors</strong>: rising errors with low use points to the physical layer instead.</li>
<li>Use <strong>flow data</strong> to see who is using the link then (e.g. a backup job).</li>
<li>Check <strong>jitter</strong> for voice complaints even if average latency looks fine.</li>
<li>Line up syslog from switch, firewall and server by timestamp: works only if all use NTP.</li></ol>''',
                   L.format('5.1') + '; ' + MON,
                   [check('From the trace, a colleague says “the WAN was at 70% once this afternoon, so it is saturated”. Why is that weak?',
                          'One sample with no baseline proves nothing', ['70% is always a sign of saturation',
                           'Utilisation can only be measured with flow data'],
                          'A single reading without normal values for comparison is not evidence of a trend; look for sustained use and '
                          'drops. SNMP counters do measure utilisation.', mc=[SAMP, BASE])]),
            tryit('<p>Sort each signal by the question it answers, then read device logs in the lab VM.</p>', L.format('5.1') + '; ' + MON,
                  [check('Voice calls are choppy, yet average latency is only 20 ms. Which measure should you look at?', 'Jitter',
                         ['Average latency over a week', 'The device uptime counter'],
                         'Jitter is variation in delay, and it breaks voice even when the average is low. The average hides that '
                         'variation, and uptime says nothing about delay.', mc=[JIT, SAMP])],
                  widget=sort('Which signal answers it?',
                              {'SNMP polling': ['Interface use every 5 minutes', 'Error counters over a month'],
                               'Syslog': ['When the link went down', 'Who changed the config'],
                               'Flow data': ['Which host used the bandwidth', 'Which ports a server talks on']},
                              'Notice that each tool answers a different question.'),
                  lab={'id': 'linux-vm-logs', 'note': 'Read the system log, find events by severity and line them up by time.'})),
        **_filler('A short summary (polling, logs, baselines) of the core section.'),
    },
    '5.2': {
        'core-content': section(
            'Core content', 'NO-5.2',
            [check('Why is Telnet unacceptable for device management?', 'It sends logins and commands in cleartext',
                   ['It cannot run on modern switches and routers', 'It is slower than SSH on busy management networks'],
                   'Telnet carries usernames, passwords and commands unencrypted, so anyone on the path can read them. SSH v2 '
                   'encrypts the session; speed and support are not the reason.', mc=[WEAK, WEAK])],
            plain('''<p>Protect the way you manage network devices.</p>
<ul><li>Use <strong>SSH</strong>, not Telnet. Use <strong>HTTPS</strong>, not HTTP. Use <strong>SNMPv3</strong>, not v1/v2c. Use <strong>SCP/SFTP</strong>, not TFTP.</li>
<li>Give each admin their own login through <strong>TACACS+</strong> or <strong>RADIUS</strong>. Keep one local emergency account locked away.</li>
<li>Only let the management network reach the device.</li>
<li>Change default passwords. Turn off unused services and ports. Keep firmware patched.</li>
<li>Save and back up the config after each approved change.</li></ul>''',
                  L.format('5.2') + '; ' + MGMT,
                  [check('Which AAA protocol can authorise individual CLI commands?', 'TACACS+', ['RADIUS', 'Kerberos'],
                         'TACACS+ separates authentication, authorisation and accounting and can authorise each command. RADIUS is '
                         'mainly for network access, and SNMPv3 is a monitoring protocol.', mc=[AAA, SNMPV])]),
            analogy('''<p>Think of the keys to a bank vault.</p>
<p>Shouting the vault code across the lobby is <strong>Telnet</strong>; whispering it through a sealed tube is <strong>SSH</strong>. One shared key
for every employee means you never know who opened the vault and cannot take a key back when someone leaves: that is a <strong>shared
admin login</strong>. Personal badges checked by a central office, which also logs every door opened, is <strong>AAA</strong> with TACACS+.</p>
<p>The vault door only opens from the staff corridor, not the street: the <strong>management ACL</strong>. And one emergency key sits sealed in
the manager’s safe in case the badge office is offline: the <strong>local emergency account</strong>.</p>''',
                    L.format('5.2') + ' (bank-vault analogy written for this rung); ' + MGMT,
                    [check('In the vault story, why keep a sealed emergency key if everyone uses badges?', 'For when the AAA servers cannot be reached',
                           ['So staff can skip the badge check when busy', 'Because badges cannot log who opened the vault'],
                           'A vaulted local account gives access when the AAA servers or the path to them are down. It is not a '
                           'shortcut, and AAA accounting does record who did what.', mc=[LOCALA, AAA])]),
            visual('''<ol class="ladder-trace"><li><strong>Before connecting</strong>: change default usernames and passwords.</li>
<li><strong>Access</strong>: enable SSH v2 and HTTPS; disable Telnet and the HTTP server.</li>
<li><strong>Who</strong>: individual accounts through TACACS+ or RADIUS; one vaulted local emergency account.</li>
<li><strong>From where</strong>: an ACL on the VTY lines allowing only the management subnet; a management VLAN or out-of-band network.</li>
<li><strong>Monitoring</strong>: SNMPv3 authPriv, logging to the central server, NTP.</li>
<li><strong>Hygiene</strong>: unused ports disabled, supported firmware, login banner.</li>
<li><strong>After every change</strong>: save the running config and back it up off the device.</li></ol>''',
                   L.format('5.2') + '; ' + MGMT,
                   [check('Following the checklist, what replaces SNMPv2c community strings?', 'SNMPv3 with authPriv',
                          ['SNMPv1 with a longer community string', 'Telnet with a strong password'],
                          'SNMPv3 authPriv adds user authentication and encryption. v1 and v2c send communities in cleartext however '
                          'long they are, and Telnet is cleartext too.', mc=[SNMPV, SNMPV])]),
            tryit('<p>Sort each setting into “replace it” or “keep it”, then harden the lab device’s management access.</p>', L.format('5.2') + '; ' + MGMT,
                  [check('Where should SSH to a core switch be allowed from?', 'The management subnet only', ['Any internal subnet', 'Anywhere, because SSH is encrypted'],
                         'Encryption protects the session, but an ACL limits who can even try to log in. Allowing every internal subnet '
                         'or the world widens the attack surface.', mc=[WEAK, WEAK])],
                  widget=sort('Replace or keep?',
                              {'Replace': ['Telnet on TCP 23', 'SNMPv2c “public” community', 'TFTP for config backups'],
                               'Keep': ['SSH v2 from the management VLAN', 'One vaulted local emergency account', 'Logging to a central server with NTP']},
                              'Notice that every “replace” item sends something in cleartext.'),
                  lab={'id': 'linux-vm-ssh', 'note': 'Connect with SSH, check the key fingerprint, and confirm Telnet is not offered.'})),
        **_filler('A short summary (secure management protocols and AAA) of the core section.'),
        'vpn-types-and-network-management-access': section(
            'VPN types and network management access', 'NO-5.2',
            [check('Which VPN type needs no client installed on the user’s device?', 'A clientless (browser TLS) VPN',
                   ['A client-to-site IPsec VPN', 'A site-to-site VPN between firewalls'],
                   'A clientless VPN gives selected web apps through a TLS portal in the browser. Client-to-site needs a VPN client, '
                   'and site-to-site joins two gateways, not a user device.', mc=[VPNT, VPNT])],
            plain('''<p>Pick the VPN by who needs to connect.</p>
<ul><li><strong>Site-to-site</strong>: joins two offices through their firewalls. Users notice nothing.</li>
<li><strong>Client-to-site</strong>: a VPN app on each laptop.</li>
<li><strong>Clientless</strong>: a web portal for a few apps. Nothing to install.</li>
<li><strong>Split tunnel</strong>: only company traffic uses the VPN. <strong>Full tunnel</strong>: everything does, so the company can filter it.</li></ul>
<p>To manage devices, use SSH, HTTPS or an API, through a hardened <strong>jump host</strong>.</p>
<p>Keep an <strong>out-of-band</strong> path (console server or cellular link) for when the main network is down.</p>''',
                  L.format('5.2') + '; ' + VPN,
                  [check('What is the difference between a split tunnel and a full tunnel?', 'Split sends only company traffic through the VPN',
                         ['Split encrypts traffic; full tunnel does not', 'Full tunnel works only for site-to-site VPNs'],
                         'In split mode internet traffic goes direct and only company-bound traffic uses the tunnel; full mode sends '
                         'everything through it. Both encrypt what they carry.', mc=[VPNT, VPNT])]),
            analogy('''<p>Think of ways to get into a company campus.</p>
<p>A private covered bridge between two buildings is a <strong>site-to-site</strong> VPN: people walk across without noticing. A staff
member with a personal key card for the side door is <strong>client-to-site</strong>. A visitor who only needs the café is let in at the front
desk to that one place: <strong>clientless</strong>.</p>
<p>A staff member who drives everything through the main gate so security can check it is using a <strong>full tunnel</strong>; one who only
brings work papers through the gate and does personal errands elsewhere is a <strong>split tunnel</strong>.</p>
<p>The fire escape that still works when the lifts fail is <strong>out-of-band</strong> management.</p>''',
                    L.format('5.2') + ' (campus-access analogy written for this rung); ' + VPN,
                    [check('In the campus story, what is the fire escape that works when the lifts fail?', 'Out-of-band management',
                           ['A split tunnel for personal traffic', 'A clientless portal for visitors'],
                           'Out-of-band uses a separate path (console server, management network, cellular) so devices can be fixed '
                           'when production is down. Split tunnels and portals both ride the production network.', mc=[OOB, VPNT])]),
            visual(svg(560, 120, 'VPN types: site-to-site gateway to gateway, client-to-site laptop to gateway, clientless browser portal; split versus full tunnel',
                       box(5, 15, 175, 46, 'Site-to-site', 'gateway ↔ gateway') + box(192, 15, 175, 46, 'Client-to-site', 'laptop app ↔ gateway')
                       + box(380, 15, 175, 46, 'Clientless', 'browser TLS portal') + box(60, 72, 210, 40, 'Split: company traffic only')
                       + box(290, 72, 210, 40, 'Full: all traffic via VPN'))
                   + '''<ol class="ladder-trace"><li>Branch needs head-office printers and files all day: site-to-site IPsec between firewalls.</li>
<li>Field staff in hotels: client-to-site VPN with MFA.</li>
<li>Contractors need only the ticketing web app: clientless portal.</li>
<li>Policy requires web filtering on company laptops everywhere: full tunnel.</li>
<li>Branch switches managed by SSH from the jump host; console server on a cellular link for out-of-band.</li></ol>''',
                   L.format('5.2') + '; ' + VPN,
                   [check('Why does the trace choose a full tunnel for the field staff?', 'Policy requires company web filtering everywhere',
                          ['Full tunnels use less head-office bandwidth', 'Split tunnels cannot carry company traffic'],
                          'A full tunnel sends all traffic through company controls, which the filtering policy needs. It uses more '
                          'head-office bandwidth, not less, and split tunnels do carry company traffic.', mc=[VPNT, VPNT])]),
            tryit('<p>Match each access need to a VPN type or management method.</p>', L.format('5.2') + '; ' + VPN,
                  [check('A config change blocks the management VLAN and every SSH session drops. What would have avoided the site visit?',
                         'An out-of-band console server', ['A second SSH session left open', 'Moving management to Telnet'],
                         'Out-of-band access uses a separate path, so it survives a production or management-VLAN mistake. A second SSH '
                         'session rides the same broken path, and Telnet is in-band and insecure.', mc=[OOB, WEAK])],
                  widget=sort('Which method?',
                              {'VPN type': ['Branch to head office all day: site-to-site', 'Contractor needs one web app: clientless'],
                               'Management path': ['Admins connect via a hardened jump host', 'Console server on cellular for outages'],
                               'Tunnel mode': ['Company must filter all laptop traffic: full', 'Only company traffic via VPN: split']},
                              'Notice that type, path and mode are separate choices.'))),
    },
    '5.3': {
        'core-content': section(
            'Core content', 'NO-5.3',
            [check('Which zone should a visitor’s phone land in, and what should it reach?', 'Guest: internet only, with client isolation',
                   ['Users: the same access as staff laptops', 'Servers: so it can use the printer directly'],
                   'Visitors go to the guest zone with internet only and isolation from each other. Putting them with staff or '
                   'servers gives an untrusted device internal reach.', mc=[SSIDS, PRIN])],
            plain('''<p>Split the network into <strong>zones</strong> and only allow what each needs.</p>
<ul><li><strong>Users</strong> reach servers on business ports. <strong>Guests</strong> reach the internet only.</li>
<li><strong>IoT</strong> devices reach only their controllers. <strong>Management</strong> is reachable only from admin PCs.</li>
<li>The <strong>DMZ</strong> holds public services.</li></ul>
<p>Enforce it with VLANs and ACLs, firewalls between zones, and 802.1X to put each device in the right place.</p>
<p><strong>Zero trust</strong>: do not trust a device because it is inside. Check every request.</p>
<p>Zones also limit the damage: ransomware or a loop stays in one segment.</p>''',
                  L.format('5.3') + '; ' + SEG,
                  [check('What does 802.1X add to VLAN segmentation?', 'It authenticates the device, then can assign its VLAN',
                         ['It encrypts all traffic between VLANs', 'It replaces the need for firewalls between zones'],
                         '802.1X checks the user or device at the port or Wi-Fi before access and can place it in a VLAN. It does not '
                         'encrypt routed traffic, and zone firewalls are still needed.', mc=[SEC, SEC])]),
            analogy('''<p>Think of a ship with watertight compartments.</p>
<p>If the hull is breached in one compartment, the doors close and the ship stays afloat. A ship with one big open hold sinks from one hole.
A <strong>flat network</strong> is that open hold: one infected laptop can reach every server. <strong>Zones</strong> are the compartments, and the
doors between them are <strong>firewalls and ACLs</strong>, each with a log of who tried to pass.</p>
<p>Passengers stay on passenger decks (<strong>guest</strong>), crew in crew areas (<strong>users</strong>), and only engineers enter the engine room
(<strong>management</strong>). On a <strong>zero-trust</strong> ship, even crew show their pass at every door.</p>''',
                    L.format('5.3') + ' (ship analogy written for this rung); ' + SEG,
                    [check('In the ship story, what is the main benefit of compartments besides security?', 'A fault such as a loop stays in one segment',
                           ['Every compartment can share one broadcast domain', 'Crew no longer need passes at any door'],
                           'Segmentation shrinks broadcast domains and contains faults like loops and storms. One shared broadcast domain '
                           'is the flat design, and zero trust adds checks rather than removing them.', mc=[INSIDE, PRIN])]),
            visual('''<ol class="ladder-trace"><li>List the zones: users, servers, guest, IoT/OT, management, DMZ.</li>
<li>For each pair, write the flows that are needed (e.g. users → servers on TCP 443 and 445).</li>
<li>Put each zone in its own VLAN and subnet.</li>
<li>Apply ACLs on the layer-3 gateway, or a stateful firewall for important boundaries; deny everything else and log it.</li>
<li>Use 802.1X/NAC to place devices into the right VLAN automatically.</li>
<li>Inside a zone, use microsegmentation (per-workload policy) for east-west control.</li></ol>''',
                   L.format('5.3') + '; ' + SEG,
                   [check('From the trace, which zone may reach device management interfaces?', 'Administrator workstations or jump hosts',
                          ['Any staff laptop in the users zone', 'The DMZ, so web servers can be managed'],
                          'Management is the most sensitive zone, reachable only from admin workstations or jump hosts. Letting every '
                          'user or the DMZ in defeats the point of the zone.', mc=[PRIN, INSIDE])]),
            tryit('<p>Place each device in its zone, then write one VLAN ACL in the lab.</p>', L.format('5.3') + '; ' + SEG,
                  [check('A building camera needs to reach only its video recorder. Which zone and rule fit?', 'IoT zone, allowed only to its controller',
                         ['Users zone, with full internet access', 'Management zone, beside the jump hosts'],
                         'IoT devices go in their own zone and reach only their controllers, with no general internet unless required. '
                         'The users and management zones are far more trusted.', mc=[PRIN, PRIN])],
                  widget=sort('Which zone?',
                              {'Guest': ['Visitor’s phone', 'Conference-room laptop of a supplier'],
                               'IoT / OT': ['Door-entry controller', 'Security camera'],
                               'DMZ': ['Public website', 'Inbound mail relay']},
                              'Notice that none of these belong on the staff user VLAN.'),
                  lab={'id': 'rtr-vlan-acl', 'note': 'Write an ACL that lets one VLAN reach a server port and blocks the rest.'})),
        **_filler('A short summary (zones, least privilege and enforcement) of the core section.'),
        'network-attacks-their-impact-and-basic-security-concepts': section(
            'Network attacks, their impact and basic security concepts', 'NO-5.3',
            [check('Several PCs get gateway 192.168.50.1 from DHCP server 192.168.50.1, not the corporate server. What is happening?',
                   'A rogue DHCP server is answering', ['The corporate DHCP scope is full', 'DNS poisoning on the resolver'],
                   'An unexpected server handing out a wrong gateway is rogue DHCP; find its port and enable DHCP snooping. A full '
                   'scope gives APIPA, and DNS poisoning changes name answers, not the gateway.', mc=[ATC, ATC])],
            plain('''<p>Know the common attacks and what stops each one.</p>
<ul><li><strong>DoS/DDoS</strong>: floods a service until it fails. Stopped by filtering and rate limits.</li>
<li><strong>MAC flooding</strong>: fills the switch table. Stopped by <strong>port security</strong>.</li>
<li><strong>Rogue DHCP</strong>: gives out a bad gateway. Stopped by <strong>DHCP snooping</strong>.</li>
<li><strong>ARP poisoning</strong>: steals the gateway’s address. Stopped by <strong>dynamic ARP inspection</strong>.</li>
<li><strong>VLAN hopping</strong>: reaches another VLAN. Stopped by turning off trunk negotiation and using an unused native VLAN.</li>
<li><strong>Evil twin</strong>: a fake Wi-Fi with a real name.</li></ul>
<p>The goals are <strong>CIA</strong>: confidentiality, integrity, availability.</p>''',
                  L.format('5.3') + '; ' + ATK,
                  [check('Which switch feature limits the number of MAC addresses on a port?', 'Port security', ['DHCP snooping', 'Dynamic ARP inspection'],
                         'Port security caps MAC addresses per port, which defeats MAC flooding. DHCP snooping stops rogue DHCP, and '
                         'DAI checks ARP against snooping bindings.', mc=[ATC, ATC])]),
            analogy('''<p>Think of tricks played on a school office.</p>
<p>A crowd of fake visitors fills the sign-in book so the receptionist gives up and lets everyone wander: <strong>MAC flooding</strong>. Someone
stands at the gate handing out fake maps with the wrong exit: <strong>rogue DHCP</strong>. Someone tells the post room “I’m the head teacher now,
send her letters to me”: <strong>ARP poisoning</strong>. A fake school sign on a building next door: an <strong>evil twin</strong>.</p>
<p>The fixes are office rules: a limit of two visitors per pass (<strong>port security</strong>), only the real office may hand out maps
(<strong>DHCP snooping</strong>), and the post room checks names against the official register (<strong>dynamic ARP inspection</strong>, which uses
the snooping table).</p>''',
                    L.format('5.3') + ' (school-office analogy written for this rung); ' + ATK,
                    [check('In the school story, the post room checks names against the official register. Which register is that on a switch?',
                           'The DHCP snooping binding table', ['The MAC address table built by learning', 'The routing table on the gateway'],
                           'Dynamic ARP inspection checks ARP replies against the IP-to-MAC bindings that DHCP snooping recorded. The MAC '
                           'table and routing table are not used to validate ARP.', mc=[ATC, ATC])]),
            visual(svg(560, 130, 'Layer-2 attacks paired with controls: MAC flooding to port security, rogue DHCP to DHCP snooping, ARP poisoning to dynamic ARP inspection, VLAN hopping to no DTP and unused native VLAN',
                       box(5, 10, 130, 50, 'MAC flooding', '→ port security') + box(145, 10, 130, 50, 'Rogue DHCP', '→ DHCP snooping')
                       + box(285, 10, 130, 50, 'ARP poisoning', '→ dynamic ARP insp.') + box(425, 10, 130, 50, 'VLAN hopping', '→ no DTP, unused native')
                       + arrow(275, 35, 285, 35) + text(280, 90, 'DAI relies on the DHCP snooping bindings') + text(280, 110, 'encryption (TLS, IPsec) protects data if an on-path attack succeeds'))
                   + '''<ol class="ladder-trace"><li>PCs on one floor have gateway 192.168.50.1; the right one is 10.20.30.1.</li>
<li><code>ipconfig /all</code> shows DHCP server 192.168.50.1: not the corporate server.</li>
<li>The MAC table locates the source port: a consumer router under a desk.</li>
<li>Shut the port and remove the device.</li>
<li>Prevent it: DHCP snooping (uplinks trusted only) plus dynamic ARP inspection on the VLAN.</li>
<li>Release and renew affected PCs; verify the gateway; document.</li></ol>''',
                   L.format('5.3') + '; ' + ATK,
                   [check('An employee on café Wi-Fi gets a certificate warning for the company portal and sees two networks with the same name. What should she do?',
                          'Not click through; disconnect and use the VPN or a hotspot', ['Accept the warning, because café Wi-Fi often has them',
                           'Switch to the other café network and try again'],
                          'This matches an evil twin on-path attack, and the warning is the defence working. Clicking through or picking '
                          'the other same-named network risks credentials.', mc=[SEC, SEC])]),
            tryit('<p>Match each attack to the control that stops it.</p>', L.format('5.3') + '; ' + ATK,
                  [check('Which CIA goal does redundancy mainly serve?', 'Availability', ['Confidentiality', 'Integrity'],
                         'Redundant links and devices keep services available. Encryption serves confidentiality, and hashing and '
                         'signatures serve integrity.', mc=[SEC, SEC])],
                  widget=sort('Which control?',
                              {'Port security': ['Thousands of fake source MACs on one port', 'More than two devices on a desk port'],
                               'DHCP snooping': ['A home router handing out leases', 'Offers arriving on an access port'],
                               'Dynamic ARP inspection': ['Forged ARP replies for the gateway', 'ARP that does not match the bindings']},
                              'Notice that DAI depends on DHCP snooping being on.'),
                  lab={'id': 'sw-port-security', 'note': 'Limit a port to a set number of MAC addresses and watch a violation.'})),
        'network-security-features-and-defences': section(
            'Network security features and defences', 'NO-5.3',
            [check('Why is MAC filtering weak on its own?', 'MAC addresses are easy to spoof', ['It only works on fibre networks', 'It blocks every phone by default'],
                   'Any device can copy an allowed MAC address, as the visitor in the lesson did. MAC filtering works on any medium '
                   'and blocks only what is not listed.', mc=[MACF, MACF])],
            plain('''<p>Layer your defences from the port outwards.</p>
<ul><li><strong>Port</strong>: turn off unused ports. Use port security.</li>
<li><strong>Joining</strong>: 802.1X checks who the device is. NAC checks it is healthy.</li>
<li><strong>Traffic</strong>: ACLs and firewall zones. Public servers go in a screened subnet (DMZ).</li>
<li><strong>Content</strong>: URL filtering blocks sites. Content filtering checks what is downloaded.</li>
<li><strong>Basics</strong>: change default passwords. Rotate keys and Wi-Fi passwords.</li></ul>
<p>MAC filtering alone is weak, because MAC addresses can be copied.</p>''',
                  L.format('5.3') + '; ' + DEF,
                  [check('What is the difference between URL filtering and content filtering?', 'URL filtering decides by site; content filtering inspects what is fetched',
                         ['URL filtering inspects downloaded files for malware; content filtering only blocks domains',
                          'They are the same feature sold under two different names'],
                         'URL filtering allows or blocks by address or category, while content filtering looks at file types or malware '
                         'in what comes back. They are distinct controls.', mc=[URLC, URLC])]),
            analogy('''<p>Think of security at an airport.</p>
<p>Locked staff doors nobody uses are <strong>disabled ports</strong>. Passport control checks who you are (<strong>802.1X</strong>) and the health
desk checks you are fit to fly (<strong>NAC</strong>). Signs and gates decide which areas you can enter (<strong>ACLs and zones</strong>), with a
public arrivals hall kept apart (<strong>DMZ</strong>). The departures board blocks some destinations (<strong>URL filtering</strong>) and the bag
scanner looks inside your luggage (<strong>content filtering</strong>).</p>
<p>A list of “allowed suitcase colours” is <strong>MAC filtering</strong>: anyone can buy a suitcase in the right colour.</p>''',
                    L.format('5.3') + ' (airport analogy written for this rung); ' + DEF,
                    [check('In the airport story, what is the bag scanner?', 'Content filtering', ['URL filtering', 'Packet filtering'],
                           'The scanner inspects what is carried, which is content filtering. The departures board blocks destinations '
                           '(URL filtering), and suitcase colours stand for MAC filtering.', mc=[URLC, MACF])]),
            visual('''<ol class="ladder-trace"><li>A public meeting-room wall port connects straight to the staff VLAN.</li>
<li>Enable 802.1X: company laptops authenticate with certificates; anything else lands in the guest VLAN.</li>
<li>Add port security: at most two MACs (phone and PC), violations logged.</li>
<li>Guest VLAN ACL: internet only, no internal subnets.</li>
<li>Disable the room’s unused ports.</li>
<li>Record the change.</li></ol>''',
                   L.format('5.3') + '; ' + DEF,
                   [check('In the trace, what happens to a visitor’s laptop plugged into the hardened port?', 'It fails 802.1X and is put in the guest VLAN',
                          ['It joins the staff VLAN because the port is up', 'It is blocked until IT adds its MAC to a list'],
                          'Devices without a company certificate fail 802.1X and are placed in the guest VLAN with internet only. The '
                          'staff VLAN is no longer the default, and MAC lists are not the control here.', mc=[MACF, MACF])]),
            tryit('<p>Sort each defence by the layer it protects, then secure the lab Wi-Fi.</p>', L.format('5.3') + '; ' + DEF,
                  [check('A company’s one Wi-Fi key is known to former staff. What is the lasting fix?', 'WPA3-Enterprise with 802.1X, and key rotation',
                         ['Add MAC filtering on top of the same shared key', 'Hide the SSID so former staff cannot find it'],
                         'Per-user 802.1X credentials can be revoked when people leave, and remaining keys get rotated. MAC filtering '
                         'and hidden SSIDs are easily bypassed.', mc=[MACF, MACF])],
                  widget=sort('Which layer?',
                              {'Port / joining': ['Disable unused ports', '802.1X with certificates', 'NAC posture check'],
                               'Traffic': ['ACL between guest and staff', 'Screened subnet for the web server'],
                               'Content': ['Block gambling sites by category', 'Block .exe downloads']},
                              'Notice that each layer limits something different: who joins, what they reach, what they fetch.'),
                  lab={'id': 'wifi-secure', 'note': 'Move a Wi-Fi network from a shared key to an enterprise or WPA3 setting and verify.'})),
    },
    '5.4': {
        'the-scenario': skip('The scenario', 'activity', 'The capstone ticket the student works; it sets up practice, not a concept.'),
        'your-turn-scaffolded-checklist': skip('Your turn — scaffolded checklist', 'activity', 'The checklist the student fills in during the capstone drill.'),
        'common-beginner-mistakes': skip('Common beginner mistakes', 'reference', 'Short list of capstone pitfalls; the ideas behind them are laddered in 5.1–5.3.'),
        'check-your-understanding': skip('Check your understanding', 'activity', 'A self-check prompt for the capstone; it is practice, not an explanation.'),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '5.1': {'core-content': '0ec1b43a4f58', 'incident-application': '1640f834119d', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': 'b8af31b825c4', 'beyond-the-quiz': '734feba9004e'},
    '5.2': {'core-content': '49aabebca015', 'incident-application': 'c710db1a9151', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '9b0d8a7bc06f', 'beyond-the-quiz': '5b15790a7233', 'vpn-types-and-network-management-access': '99c507502633'},
    '5.3': {'core-content': '2ef8b7c5d57f', 'incident-application': '4fc9722b1784', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': 'f8693789f9bd', 'beyond-the-quiz': 'ed15c48deff3', 'network-attacks-their-impact-and-basic-security-concepts': '7cbe528f8fa5', 'network-security-features-and-defences': '3fddd73915bf'},
    '5.4': {'the-scenario': 'df0644a93ed0', 'your-turn-scaffolded-checklist': 'c012ac6b0861', 'common-beginner-mistakes': '49a618d1ee12', 'check-your-understanding': 'cdda2cb3f068'},
}

# ---- pass 21: former skips laddered from lesson data (Pending SME review) ----
from curriculum_v2.ladder.netops import _gen as _G  # noqa: E402

_DATA = {
    '5.1': dict(
        title='Monitoring Signals', an='security cameras', ab='you need a sense of normal',
        case='Users report slowness every afternoon; the monitoring dashboard is green.',
        steps=[('14:00', 'Check interface utilisation graph', 'uplink at 95% from 13:30'),
               ('14:03', 'Check error counters', 'flat'),
               ('14:06', 'Check syslog for the period', 'backup job started 13:30'),
               ('14:09', 'Compare with last week baseline', 'backup moved from 02:00')],
        esc='all users afternoons; uplink 95% from 13:30; backup job rescheduled; backup owner needed.',
        status='The afternoon slowness is caused by a backup running during the day. We have asked its owner to move it; next update at 15:00.',
        neg='“Error counters flat” rules out a faulty link.',
        par='raising QoS, changing alert thresholds and moving the backup all at once.',
        good=['Uplink 95% from 13:30', 'Errors flat, 14:03'], bad=['Dashboard green so fine', 'Changed thresholds and QoS'],
        plist=[('Check utilisation', 'normal for time of day', 'unusual peak'),
               ('Check errors', 'flat', 'rising errors'),
               ('Read syslog', 'nothing new', 'event found'),
               ('Compare baseline', 'matches', 'differs'),
               ('Note owner', 'none needed', 'escalate to owner')],
        up='a baseline of what normal looks like.', down='your ability to tell a fault from a busy day.',
        user='A scheduled job is using the network in the afternoon; we have asked for it to run at night.',
        mist=['Trusting a green dashboard', 'Changing thresholds to hide alerts'],
        escw='the job or system belongs to another team.',
        scen=('Slow every afternoon.', ['Busy uplink', 'Errors on link', 'Server load'],
              'compare utilisation and errors against the baseline', 'graphs, times and owners.'),
        lab=('linux-vm-logs', 'Read the logs for the period and find the event.')),
    '5.2': dict(
        title='Management Plane Hardening', an='a utility room lock', ab='controls are not in the public hall',
        case='An audit finds a switch answering Telnet from the user VLAN.',
        steps=[('10:00', 'Confirm Telnet answers', 'port 23 open from user VLAN'),
               ('10:03', 'Check SSH is enabled', 'SSH v2 works'),
               ('10:06', 'Check management ACL', 'none applied'),
               ('10:09', 'Open a change for Telnet off plus ACL', 'change raised')],
        esc='one switch; Telnet open from users; no management ACL; change needed via network owner.',
        status='An audit found an insecure management setting on one switch. A planned change will close it; no user impact expected.',
        neg='“SSH v2 works, 10:03” means you can turn Telnet off safely.',
        par='disabling Telnet, adding an ACL and changing passwords live without a change.',
        good=['Port 23 open from 10.10.x', 'SSH v2 confirmed'], bad=['Turned off Telnet live', 'Did several fixes, no record'],
        plist=[('Check management protocols', 'SSH only', 'Telnet or HTTP open'),
               ('Check ACL', 'admin subnet only', 'no ACL'),
               ('Check accounts', 'named, strong auth', 'shared or default'),
               ('Check firmware', 'patched', 'outdated'),
               ('Raise change', 'approved', 'escalate')],
        up='SSH, management ACLs and named accounts.', down='the security of every device managed that way.',
        user='One device can be managed in an insecure way; we are fixing it in a planned change.',
        mist=['Leaving Telnet on for convenience', 'Fixing live without a change'],
        escw='the device is production and needs an approved change.',
        scen=('Audit finds Telnet open.', ['No ACL', 'Telnet enabled', 'Default accounts'],
              'scan management ports from the user VLAN', 'ports open and ACL state.'),
        lab=('linux-vm-ssh', 'Connect over SSH and check how the device is managed.')),
    '5.3': dict(
        title='Segmentation', an='fire doors', ab='they slow the spread',
        case='A lab PC infected with malware was able to scan the finance server.',
        steps=[('16:00', 'Isolate the lab PC', 'unplugged, ticket raised'),
               ('16:05', 'Check lab VLAN to finance ACL', 'permit any'),
               ('16:10', 'Check design document', 'lab should reach internet only'),
               ('16:15', 'Raise ACL change', 'change raised')],
        esc='lab PC isolated; lab VLAN can reach finance; design says it should not; security and network owners needed.',
        status='A lab computer was isolated after a security alert. We are tightening the network separation; finance is unaffected so far.',
        neg='“Finance VLAN cannot reach lab, 16:06” narrows the gap to one direction.',
        par='reimaging the PC, changing ACLs and resetting passwords at once.',
        good=['ACL lab→finance permit any', 'Lab PC isolated 16:00'], bad=['Fixed the finance ACL quietly', 'Did everything at once'],
        plist=[('Isolate the host', 'off the network', 'still connected'),
               ('Map paths', 'drawn', 'path unknown'),
               ('Read ACLs', 'match design', 'permit any found'),
               ('List gaps', 'with owner', 'no owner'),
               ('Raise changes', 'approved', 'escalate')],
        up='ACLs between VLANs that match the design.', down='containment when any one host is compromised.',
        user='We isolated one lab computer and are tightening the walls between networks.',
        mist=['Leaving networks flat', 'Silent fixes during a review'],
        escw='the change crosses another team’s network.',
        scen=('Lab PC reached finance.', ['ACL permit any', 'Wrong VLAN', 'Shared firewall rule'],
              'read the ACL between the two VLANs', 'paths, ACL lines and owners.'),
        lab=('rtr-vlan-acl', 'Read the ACL between VLANs and compare with the design.')),
}
_CAP = dict(
    title='segmentation review', short='Paper review of a diagram', an='a building inspection', ab='list the gaps before knocking down walls',
    scen='a paper review: list gaps on a simple diagram with a user VLAN, a server VLAN and a firewall.',
    why='It trains you to draw the path, list gaps and give each a severity and owner, without touching production.',
    steps=['Draw the path', 'Mark each control', 'List gaps', 'Rate severity', 'Name the owner'],
    layer=['map', 'controls', 'findings', 'risk', 'escalation'],
    items=['Path drawn', 'Gaps listed', 'Severity + owner'],
    mist=[('Silent “fixes” on production during a review exercise', 'Write findings and raise changes'), ('Listing gaps with no owner', 'Name an owner for each gap')],
    lab=('rtr-vlan-acl', 'Read the ACLs and list the gaps.'))
_G.apply(LESSONS, MISCONCEPTIONS, CHAPTER, _DATA, _CAP, 'NO-5.3')
