"""Explanation ladder — NETOPS chapter 6 (Troubleshooting, Incidents and Documentation). Pending SME review.

Author: content branch (pass 19). R1 plain, R2 analogy, R3 visual/trace, R4 try-it per concept section, each with a
check that asks the idea in a new form. Facts follow the lesson and the primary sources named in each rung.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)
from curriculum_v2.ladder.netops._draw import arrow, box, svg, text

SCHEMA = 1
COURSE = 'NETOPS'
CHAPTER = 6

L = 'Course lesson {} (the original section), re-explained'
TS = 'CompTIA Network+ N10-009 troubleshooting methodology (objective 5.1) and objectives 5.2–5.5; RFC 1191 (path MTU discovery); RFC 4821 (packetization-layer PMTUD)'
IFC = 'Cisco IOS interface and switching command references (show interfaces counters, err-disabled, show power inline, show lldp/cdp neighbors); IEEE Std 802.3 (auto-negotiation, minimum frame 64 bytes); IEEE Std 802.1AB (LLDP)'
INC = 'CompTIA Network+ N10-009 objective 5.1 (troubleshooting methodology); ITIL 4 incident and change enablement practices; Google SRE book, “Postmortem Culture”'
DOC = 'ANSI/TIA-606 (labelling and records); NIST SP 800-128 (configuration management); NIST SP 800-88 (media sanitisation); CompTIA Network+ N10-009 objective 3.1'
DR = 'NIST SP 800-34 Rev. 1 (RPO, RTO, hot/warm/cold sites); ASHRAE TC 9.9 thermal guidelines (18–27 °C inlet); EIA/ECIA-310 (19-inch rack, 1U = 1.75 in); CompTIA Network+ N10-009 objectives 2.4 and 3.3'
R = 'Pending SME review'

MISCONCEPTIONS = {
    'MC-L-NO6-PATTERN-MIX': {
        'obj': 'NO-6.1', 'label': 'Matching a symptom to the wrong fault pattern (e.g. MTU black hole read as DNS, loop read as DHCP)',
        'fix': 'Use the discriminating test for each pattern: DF-bit ping for MTU, nslookup for DNS, STP logs for loops, ipconfig server for rogue DHCP.',
        'terms': ['mtu', 'pattern', 'symptom', 'discriminating test'], 'source': L.format('6.1') + '; ' + TS, 'review': R},
    'MC-L-NO6-IF-STATE': {
        'obj': 'NO-6.1', 'label': 'Mixing up administratively down, err-disabled and suspended interface states, or runts and giants',
        'fix': 'Admin down: shut in config. Err-disabled: the switch shut it after a violation. Runts: <64 bytes (duplex). Giants: > MTU.',
        'terms': ['administratively down', 'err-disabled', 'runts', 'giants', 'suspended'], 'source': L.format('6.1') + '; ' + IFC, 'review': R},
    'MC-L-NO6-ESCALATE-FAIL': {
        'obj': 'NO-6.2', 'label': 'Treating escalation as failure and holding on past the time box',
        'fix': 'When the time box ends, escalate with what you tested and the results; escalation is an evidence hand-off.',
        'terms': ['time box', 'escalate', 'evidence'], 'source': L.format('6.2'), 'review': R},
    'MC-L-NO6-SILENT-CHANGE': {
        'obj': 'NO-6.2', 'label': 'Thinking small or emergency changes do not need a change record',
        'fix': 'Every change gets a note: what, why, risk and rollback; emergency changes are still changes.',
        'terms': ['change control', 'emergency change', 'rollback'], 'source': L.format('6.3'), 'review': R},
    'MC-L-NO6-RPO-RTO': {
        'obj': 'NO-6.3', 'label': 'Swapping RPO (acceptable data loss) and RTO (acceptable downtime), or the site types',
        'fix': 'RPO looks back from the disaster (how much data can be lost); RTO looks forward (how long it may be down).',
        'terms': ['rpo', 'rto', 'warm site', 'cold site', 'hot site'], 'source': L.format('6.3') + '; NIST SP 800-34', 'review': R},
    'MC-L-NO6-UPS-PDU': {
        'obj': 'NO-6.3', 'label': 'Confusing a UPS (battery backup) with a PDU (power distribution), or ignoring rack airflow',
        'fix': 'A UPS bridges outages; a PDU spreads power to the rack. Match device airflow to the hot/cold aisle.',
        'terms': ['ups', 'pdu', 'airflow', 'hot aisle'], 'source': L.format('6.3') + '; ' + DR, 'review': R},
    'MC-L-NO6-EOL-EOS': {
        'obj': 'NO-6.3', 'label': 'Mixing up end of life (no longer sold) with end of support (no more fixes), or golden config with backups',
        'fix': 'EOL: no longer sold. EOS: no more patches. Golden config: the approved baseline new devices start from.',
        'terms': ['eol', 'eos', 'golden configuration', 'ipam'], 'source': L.format('6.3') + '; ' + DOC, 'review': R},
}

SCOPE, PAT, IFS = 'MC-NO6-SCOPE-IGNORED', 'MC-L-NO6-PATTERN-MIX', 'MC-L-NO6-IF-STATE'
SHOT, PROM, ORDR, ROLL, ESC, ESCF, SILENT = ('MC-NO6-SHOTGUN', 'MC-NO6-STATUS-PROMISE', 'MC-C-NO6-METHOD-ORDER', 'MC-C-NO6-NO-ROLLBACK',
                                             'MC-C-NO6-ESCALATION', 'MC-L-NO6-ESCALATE-FAIL', 'MC-L-NO6-SILENT-CHANGE')
ALERT, DOCS, DIAG, RPO, UPS, EOL = ('MC-NO6-ALERT-CLEARED', 'MC-NO6-DOCS-OPTIONAL', 'MC-C-NO6-DIAGRAM-TYPE', 'MC-L-NO6-RPO-RTO',
                                    'MC-L-NO6-UPS-PDU', 'MC-L-NO6-EOL-EOS')

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
    '6.1': {
        'core-content': section(
            'Core content', 'NO-6.1',
            [check('Users reach file shares fine, but every large download over the VPN stalls. Which pattern is it?',
                   'An MTU / path-MTU black hole', ['A DNS failure for the file server name', 'A duplicate IP address on the VPN gateway'],
                   'Small packets pass while large ones stall, which is the MTU signature, often over VPNs; test with a DF-bit '
                   'ping of growing size. DNS or a duplicate IP would break small traffic too.', mc=[PAT, PAT])],
            plain('''<p>Most network faults follow a few patterns. Match the symptom, then run the one test that tells causes apart.</p>
<ul><li>169.254 on one PC: link or VLAN. On many new PCs in one VLAN: scope or relay.</li>
<li>IP works, names fail: DNS.</li>
<li>Small packets fine, big transfers stall: MTU.</li>
<li>Rising CRC errors: cable or duplex.</li>
<li>Whole switch slow after a cabling change: a loop.</li>
<li>Wrong gateway from DHCP: a rogue server.</li>
<li>Two devices dropping in turn: a duplicate IP.</li></ul>
<p>First ask <strong>how far it reaches</strong>: one user, one VLAN, one site, or everyone.</p>''',
                  L.format('6.1') + '; ' + TS,
                  [check('Why ask about scope before running any test?', 'It narrows the fault domain to a few causes',
                         ['It is required before opening any ticket', 'It tells you which user to blame for the fault'],
                         'Knowing whether one user, one VLAN, one site or everyone is affected removes most of the pattern table, '
                         'so the first test can discriminate. It is about evidence, not paperwork or blame.', mc=[SCOPE, SCOPE])]),
            analogy('''<p>Think of a plumber called to a house with no water.</p>
<p>Her first question is “just this tap, this floor, the whole house, or the whole street?” One tap points at that tap’s valve; the whole
street points at the water main. That is <strong>scope</strong>. Then she uses one test that splits the likely causes: turning on the
outside tap tells her straight away whether the house supply is fine.</p>
<p>She also knows patterns: hot water fine but cold weak is a different fault from no pressure anywhere. A network technician’s patterns are
the same idea: small packets fine but big ones stuck (MTU), IP fine but names stuck (DNS), everything slow after new cabling (a loop).</p>''',
                    L.format('6.1') + ' (plumber analogy written for this rung)',
                    [check('In the plumber story, the whole street has no water. Where does that point on a network?', 'A shared service or upstream link',
                           ['The one PC’s cable and switchport', 'The user’s browser cache and cookies'],
                           'Everyone affected points at something shared: DNS, identity, the WAN or a SaaS provider. One device’s cable '
                           'or browser would only affect that user.', mc=[SCOPE, SCOPE])]),
            visual('''<ol class="ladder-trace"><li>Ask scope: one user? one VLAN? one site? everyone?</li>
<li>Match the symptom to a row: e.g. “half the VLAN suddenly has the wrong gateway”.</li>
<li>Pick the discriminating test for that row: read the DHCP server field in <code>ipconfig /all</code>.</li>
<li>Result: the server is 192.168.50.1, not the corporate one: rogue DHCP confirmed.</li>
<li>If the test had shown the corporate server, drop that theory and pick the next row.</li>
<li>Record the test and result in the ticket either way.</li></ol>''',
                   L.format('6.1') + '; ' + TS,
                   [check('Following the trace, two devices drop off the network in turn every few minutes. Which test fits that pattern?',
                          'Look for an ARP address conflict', ['Ping with the don’t-fragment bit set', 'Read STP topology-change logs'],
                          'Devices dropping in turn suggests a duplicate IP, which shows as an ARP or address-conflict event. DF-bit pings '
                          'test MTU, and STP logs test for loops.', mc=[PAT, PAT])]),
            tryit('<p>Sort each symptom into its fault pattern, then run the full triage lab.</p>', L.format('6.1') + '; ' + TS,
                  [check('APs and phones reboot whenever more are plugged into one switch. What is the likely pattern?', 'PoE budget exceeded',
                         ['Wi-Fi channel contention', 'A DHCP scope that is full'],
                         'Devices losing power as more are added is the PoE budget running out; compare usage with the budget. Channel '
                         'contention slows Wi-Fi, and a full scope stops leases, not power.', mc=[PAT, PAT])],
                  widget=sort('Which pattern?',
                              {'MTU black hole': ['Web pages load, big VPN copies stall', 'Ping works, large file transfer hangs'],
                               'Layer-2 loop': ['Whole switch slow after a new patch lead', 'Switch CPU 100% with storms'],
                               'Rogue DHCP': ['Half the VLAN has the wrong gateway', 'Unknown DHCP server in ipconfig']},
                              'Notice that each pattern has its own test.'),
                  lab={'id': 'win-full-triage', 'note': 'Work a fault from scope to discriminating test on the Windows client.'})),
        **_filler('A short summary (match symptoms to patterns and test) of the core section.'),
        'interface-states-error-counters-and-the-troubleshooting-tool': section(
            'Interface states, error counters and the troubleshooting toolkit', 'NO-6.1',
            [check('A port shows err-disabled. What does that mean?', 'The switch shut it after a violation',
                   ['Someone typed shutdown on the port', 'Its LACP settings do not match the bundle'],
                   'Err-disabled is the switch protecting itself, for example after port security or BPDU Guard. Administratively '
                   'down means someone shut it, and suspended is an LACP member mismatch.', mc=[IFS, IFS])],
            plain('''<p>Read <code>show interfaces</code> before you touch a cable.</p>
<ul><li><strong>Status</strong>: up/up is fine. <strong>Administratively down</strong>: someone shut it. <strong>Err-disabled</strong>: the switch shut it after a problem.</li>
<li><strong>Speed and duplex</strong> must match at both ends.</li>
<li><strong>CRC errors</strong>: damaged frames, so cable or interference. <strong>Runts</strong>: tiny frames, often a duplex mismatch. <strong>Giants</strong>: frames too big for the MTU.</li>
<li>For fibre, check the light level. For PoE, check the power budget.</li></ul>
<p>Tools: Wireshark, ping, traceroute, nslookup, netstat, arp, LLDP/CDP to find the neighbour port, Nmap only with permission.</p>''',
                  L.format('6.1') + '; ' + IFC,
                  [check('Which tool shows the neighbouring switch’s name and port?', 'LLDP or CDP neighbours', ['nslookup against the switch name', 'netstat on the connected PC'],
                         'LLDP and CDP advertise each device’s identity and port to its neighbour. nslookup queries DNS, and netstat '
                         'lists local connections and listening ports.', mc=[IFS, IFS])]),
            analogy('''<p>Think of reading a car’s dashboard before opening the bonnet.</p>
<p>The ignition light tells you whether the engine is on at all: the <strong>status line</strong>. “Key turned off” is administratively down; “the
engine cut out to protect itself” is err-disabled. Then the gauges: a rough idle and backfires are <strong>runts</strong> from two systems fighting
(a duplex mismatch); a warning that something is too big for the garage door is a <strong>giant</strong>; a flickering fuel gauge from a loose
wire is <strong>CRC errors</strong>.</p>
<p>A good mechanic also checks whether the fault moves with the part: if the noise follows the tyre to another wheel, it is the tyre.</p>''',
                    L.format('6.1') + ' (car-dashboard analogy written for this rung); ' + IFC,
                    [check('CRC errors follow the user’s PC to a different switch port, then stop when the patch cable is replaced. What did moving the PC show?',
                           'The fault moved with the cable', ['The original switch port was faulty all along',
                            'The PC network card needed a driver update'],
                           'Errors that move with the PC rule out the switch port and point to its cable or NIC; replacing the cable '
                           'fixing it confirms the cable.', mc=[IFS, IFS])]),
            visual(svg(560, 110, 'Reading an interface in order: status line, then speed and duplex, then error counters, then optics or PoE',
                       box(5, 25, 125, 56, 'Status', 'up/up? admin down?') + box(145, 25, 125, 56, 'Speed/duplex', 'match both ends?')
                       + box(285, 25, 125, 56, 'Counters', 'CRC, runts, giants') + box(425, 25, 130, 56, 'Optics / PoE', 'light, budget')
                       + arrow(130, 53, 145, 53) + arrow(270, 53, 285, 53) + arrow(410, 53, 425, 53))
                   + '''<ol class="ladder-trace"><li>One user’s copies crawl; neighbours are fine.</li>
<li>Status: up/up. Speed/duplex: switch hard-set to 100 Mb/s full.</li>
<li>Counters: runts and CRC errors rising.</li>
<li>Reason: the PC auto-negotiates, gets no reply from a hard-set port, and falls back to half duplex: mismatch.</li>
<li>Fix: set the port to auto, re-patch with a tested cable; link comes up 1000/full.</li>
<li>Clear counters, check again the next day, document.</li></ol>''',
                   L.format('6.1') + '; ' + IFC,
                   [check('In the trace, why did the PC end up at half duplex?', 'The hard-set port sent no auto-negotiation',
                          ['The cable was too long for gigabit', 'The PC was set to half duplex by its user'],
                          'An auto-negotiating device facing a hard-set port detects the speed but must assume half duplex, creating the '
                          'mismatch. Cable length and user settings were not the cause.', mc=[IFS, IFS])]),
            tryit('<p>Read interface status on the lab switch and name each state or counter.</p>', L.format('6.1') + '; ' + IFC,
                  [check('Which counter rises when frames exceed the configured MTU?', 'Giants', ['Runts', 'CRC errors'],
                         'Giants are frames larger than the MTU, fixed by making MTU or jumbo settings consistent. Runts are under 64 '
                         'bytes, and CRC errors are corrupted frames.', mc=[IFS, IFS])],
                  widget=sort('What does it mean?',
                              {'Configuration': ['Administratively down', 'Suspended LACP member'],
                               'Protection': ['Err-disabled after BPDU Guard', 'Err-disabled after port security'],
                               'Physical / duplex': ['Rising CRC errors', 'Runts with late collisions']},
                              'Notice that only the protection states need you to find a cause first.'),
                  lab={'id': 'sw-int-status', 'note': 'Read show interfaces status and name each port’s state.'})),
    },
    '6.2': {
        'core-content': section(
            'Core content', 'NO-6.2',
            [check('A rule change at 09:35 preceded a 09:40 outage. What should be tested first?', 'The 09:35 change, and rolling it back',
                   ['The ISP circuit, because outages are usually upstream', 'Every firewall rule, one by one from the top'],
                   'A recent change is the most likely cause, and rolling it back is often the fastest way to restore service. '
                   'Starting elsewhere ignores the strongest clue.', mc=[ROLL, ORDR])],
            plain('''<p>Use the same seven steps every time.</p>
<ol><li><strong>Identify</strong> the problem: symptoms, scope, recent changes.</li>
<li><strong>Theory</strong>: start with simple and recent.</li>
<li><strong>Test</strong> it. Wrong? New theory, or escalate.</li>
<li><strong>Plan</strong> the fix, with a way back.</li>
<li><strong>Implement</strong> one change at a time.</li>
<li><strong>Verify</strong> from the user’s side.</li>
<li><strong>Document</strong> it.</li></ol>
<p>Give each theory a time limit. When it runs out, <strong>escalate</strong> with your evidence.</p>
<p>Status updates say what is broken, since when, what you know, what is next, and when the next update comes.</p>''',
                  L.format('6.2') + '; ' + INC,
                  [check('Your first theory is disproved. What are your two options?', 'Form and test a new theory, or escalate',
                         ['Make several changes at once to save time', 'Close the ticket as cannot reproduce'],
                         'The method says to form a new theory or escalate with evidence. Several untracked changes turn one incident '
                         'into two, and closing the ticket abandons the user.', mc=[SHOT, ESCF])]),
            analogy('''<p>Think of a doctor in an emergency room.</p>
<p>She takes the history first (<strong>identify</strong>), suspects the common and recent cause first (“you started a new medicine
yesterday?”: <strong>theory</strong>), orders one test that rules it in or out (<strong>test</strong>), plans treatment with a backup
(<strong>plan</strong>, rollback), gives one drug at a time so she knows which worked (<strong>implement</strong>), checks the patient actually
feels better (<strong>verify</strong>), and writes it all in the notes (<strong>document</strong>).</p>
<p>If she is stuck after the time she allowed, she calls a specialist and hands over her notes. That is escalation, not failure. And she tells
the family what is happening and when she will update them next, without promising a time she cannot keep.</p>''',
                    L.format('6.2') + ' (emergency-room analogy written for this rung); ' + INC,
                    [check('In the ER story, why does the doctor give one drug at a time?', 'So she knows which change had the effect',
                           ['Because two drugs always cost too much', 'So the patient can choose the one they like'],
                           'One change at a time ties each result to one cause, the same as implementing network changes one by one. '
                           'Changing several at once hides what fixed or broke it.', mc=[SHOT, SHOT])]),
            visual('''<ol class="ladder-trace"><li><strong>09:40</strong> North site cannot reach the internet. Scope: one site. Recent change: firewall rule at 09:35.</li>
<li><strong>Theory</strong>: the 09:35 rule blocks outbound. Time box: 15 minutes.</li>
<li><strong>Test</strong>: firewall log shows outbound denies by the new rule. Theory confirmed.</li>
<li><strong>Status</strong> (09:55): “North site has no internet since 09:40; the ISP circuit is up; our 09:35 firewall change is dropping traffic; rolling it back now; next update 10:15.”</li>
<li><strong>Plan and implement</strong>: roll back to the last known good rule set.</li>
<li><strong>Verify</strong>: a user at the north site opens the sites that failed.</li>
<li><strong>Document</strong>: cause, actions, outcome and lessons.</li></ol>''',
                   L.format('6.2') + '; ' + INC,
                   [check('Which part of the 09:55 status update stops users chasing you for news?', 'The time of the next update',
                          ['The firewall vendor’s name', 'A promise that it will be fixed by 10:00'],
                          'Saying when the next update comes sets expectations without over-promising. A fix-time promise may be broken, '
                          'and the vendor’s name does not help users.', mc=[PROM, PROM])]),
            tryit('<p>Put the seven steps in order, then work a ticket with the method in the lab.</p>', L.format('6.2') + '; ' + INC,
                  [check('Your 15-minute time box for a priority-1 theory has run out and you feel close. What do you do?',
                         'Escalate now with what you tested', ['Keep going until you find the cause', 'Quietly try three more changes first'],
                         'The time box exists so a P1 gets more help on schedule; escalation hands over evidence. Carrying on or making '
                         'untracked changes extends the outage.', mc=[ESCF, ESC])],
                  widget=order('Order the method', ['Identify the problem', 'Establish a theory', 'Test the theory', 'Plan the fix with rollback',
                                                    'Implement one change', 'Verify from the user’s side', 'Document'],
                               'Verification and documentation are steps, not extras.'),
                  lab={'id': 'ticket-method', 'note': 'Work a ticket through the seven steps and write the status update.'})),
        **_filler('A short summary (structured method, time boxes and status) of the core section.'),
    },
    '6.3': {
        'core-content': section(
            'Core content', 'NO-6.3',
            [check('After changing a trunk’s allowed-VLAN list, which documents need updating?', 'Config backup, change record, logical diagram',
                   ['Only the physical cable map of the wiring closet', 'Nothing, because the change was small and quick'],
                   'An allowed-VLAN change alters configuration and layer-2 topology, so the backup, change record and logical '
                   'diagram change. No cable moved, and small changes still get recorded.', mc=[DOCS, DIAG])],
            plain('''<p>A fix is not done until you have proved it and written it down.</p>
<ul><li><strong>Verify</strong>: ask the user to do the task that failed. Run the same test before and after.</li>
<li>Watch for a while. A counter that keeps rising means the fix did not hold.</li>
<li><strong>Document</strong>: update the diagrams, IP records, config backup and change record when things change.</li>
<li>Write a knowledge-base article titled by the symptom.</li>
<li>After a big incident, hold a <strong>blameless review</strong>: what happened and how the process allowed it.</li></ul>''',
                  L.format('6.3') + '; ' + DOC,
                  [check('Why attach before-and-after evidence to a ticket?', 'It proves what changed so others can trust it',
                         ['It is only needed when a manager asks for it', 'It replaces asking the user to test'],
                         'The same test before and after shows the fix worked and lets the next technician trust the conclusion. It '
                         'does not replace user verification, and it is always worth doing.', mc=[ALERT, DOCS])]),
            analogy('''<p>Think of a car service.</p>
<p>A good garage does not say “fixed” after tightening something. They take the car for a drive with you, the way you drive it
(<strong>verify from the user’s side</strong>). They give you before-and-after readings (<strong>evidence</strong>). They update the service
book (<strong>documentation</strong>), so the next mechanic knows what was done.</p>
<p>If a brake failed badly, they hold a review: was a part mislabelled, was the checklist unclear? They do not just blame the apprentice,
because people only report mistakes honestly when they are not punished for it. That is a <strong>blameless review</strong>.</p>''',
                    L.format('6.3') + ' (car-service analogy written for this rung); ' + INC,
                    [check('In the garage story, what makes the review “blameless”?', 'It studies the process, not the person',
                           ['Nobody is allowed to say what went wrong', 'The apprentice is named in the report'],
                           'A blameless review examines system and process conditions so people report honestly. It still names what '
                           'went wrong; it just does not target individuals.', mc=[DOCS, DOCS])]),
            visual('''<ol class="ladder-trace"><li>Before: capture the failing test (e.g. traceroute, interface counters, DHCP lease).</li>
<li>Make the approved change.</li>
<li>After: run the same test, and ask the user to do the original task.</li>
<li>Watch: clear counters and check again later; rising errors mean it did not hold.</li>
<li>Update: config backup (and diff), change record, diagram, IPAM, as each applies.</li>
<li>Write the KB: title by symptom, then environment, cause, fix, verification, when to escalate.</li></ol>''',
                   L.format('6.3') + '; ' + DOC,
                   [check('The monitoring alert has cleared after your fix. What does the trace say to do before closing?',
                          'Have the user repeat the task and keep watching', ['Close it at once, since the cleared alert proves it',
                           'Reboot the device to make sure the fix sticks'],
                          'An alert clearing is not proof from the user’s side, and intermittent faults need time to show. Rebooting '
                          'adds a new change instead of verifying.', mc=[ALERT, ALERT])]),
            tryit('<p>Sort each change into the document it updates.</p>', L.format('6.3') + '; ' + DOC,
                  [check('Which document changes when a patch panel port is moved to a different switch port?', 'The physical (layer 1) diagram or cable map',
                         ['The logical diagram of subnets and routing', 'Only the knowledge-base article'],
                         'Moving a cable changes layer-1 records. Subnets and routing are unchanged, so the logical diagram stays, and '
                         'a KB article is not a record of the physical plant.', mc=[DIAG, DIAG])],
                  widget=sort('Which document?',
                              {'Physical diagram / cable map': ['Patch lead moved to another port', 'Switch moved to another rack'],
                               'Logical diagram': ['New VLAN added to a trunk', 'New firewall zone created'],
                               'IPAM': ['New DHCP reservation for a printer', 'Static IP given to a new server']},
                              'Notice that config backups and change records apply to every row.'),
                  lab={'id': 'sw-describe', 'note': 'Add interface descriptions so the switch documents its own links.'})),
        **_filler('A short summary (verify from the user’s side and keep documentation true) of the core section.'),
        'operational-discipline': section(
            'Operational discipline', 'NO-6.2',
            [check('What should an escalation contain, according to the lesson?', 'Impact, urgency, steps taken and evidence',
                   ['“Please fix ASAP” and the user’s name', 'Just the ticket number, so the next tier starts fresh'],
                   'An escalation hands over impact, urgency, what you tried, evidence such as errors and timestamps, and access '
                   'details. A bare request or ticket number makes the next tier repeat your work.', mc=[ESC, ESC])],
            plain('''<p>Small habits stop outages.</p>
<ul><li>Write down <strong>every change</strong>: what, why, the risk, and how to undo it. Even small ones.</li>
<li>When you escalate, give <strong>impact, urgency, what you tried, and evidence</strong> with times. Not just “please fix”.</li>
<li>Protect users’ <strong>privacy</strong>.</li>
<li>Know where <strong>backups</strong> are, and who may approve a restore that overwrites data.</li></ul>''',
                  L.format('6.3') + '; ' + INC,
                  [check('A one-line ACL edit fixes a ticket. Does it need a change note?', 'Yes: what, why, risk and rollback',
                         ['No, one-line edits are too small to matter', 'Only if the edit later causes an outage'],
                         'Silent changes create outages because nobody knows what changed. Every change, even a small or emergency one, '
                         'gets a note so it can be traced and undone.', mc=[SILENT, SILENT])]),
            analogy('''<p>Think of a shared kitchen in a restaurant.</p>
<p>A cook who quietly changes the recipe, without telling anyone, ruins the next shift’s dishes: that is a <strong>silent change</strong>. The rule
is a note on the board: what changed, why, and how to go back.</p>
<p>When a cook hands a problem to the head chef, “the sauce is wrong, fix it” helps nobody. “Table 6, allergy, I tried less salt, here is the
tasting note from 19:10” does: that is a good <strong>escalation</strong>. And only the manager may throw out the whole batch: knowing <strong>who can
authorise destructive recovery</strong>.</p>''',
                    L.format('6.3') + ' (kitchen analogy written for this rung); ' + INC,
                    [check('In the kitchen story, which handover is a good escalation?', '“Table 6, allergy, tried less salt, tasting note at 19:10”',
                           ['“The sauce is wrong, please fix it quickly”', '“Something is off in the kitchen tonight, have a look”'],
                           'A good escalation gives impact, what was tried and timed evidence. Vague requests make the next person start '
                           'from zero.', mc=[ESC, ESC])]),
            visual('''<ol class="ladder-trace"><li><strong>Before a change</strong>: write what, why, risk and rollback.</li>
<li><strong>During</strong>: one change at a time, noted with the time.</li>
<li><strong>Stuck</strong>: escalate with impact, urgency, steps taken, evidence and timestamps, and access details.</li>
<li><strong>Data at risk</strong>: find where backups live, and get approval from whoever owns destructive recovery.</li>
<li><strong>After</strong>: close the change record with the outcome.</li></ol>''',
                   L.format('6.3') + '; ' + INC,
                   [check('Following the trace, a restore would overwrite a team’s shared folder. What comes first?', 'Approval from the data’s owner',
                          ['Run the restore now to save time', 'Ask the user who reported it to approve'],
                          'Destructive recovery needs the right authority before it runs. Restoring at once risks losing newer data, and '
                          'the reporting user may not own the data.', mc=[SILENT, SILENT])]),
            tryit('<p>Rewrite a weak escalation into a strong one, then compare with the model answer.</p>', L.format('6.3'),
                  [check('Which detail turns “VPN broken, please fix” into a useful escalation?', 'Since 08:10, 40 users, two sites tested, logs',
                         ['A note that the user is very frustrated today', 'The request marked urgent in capital letters'],
                         'Time, scope, tests and evidence let the next tier act at once. Frustration and capital letters show urgency '
                         'but give nothing to work with.', mc=[ESC, ESC])],
                  widget=reveal('Weak: “Printer broken, please fix.” Write a strong version.',
                                '“3rd-floor printer (PRN-03) unreachable since 09:20 for 12 users; link light on; ping to 10.20.40.20 fails; neighbour PC fine; switchport Gi1/0/14 shows err-disabled. Need switch access to investigate.”'))),
        'physical-installations-and-disaster-recovery': section(
            'Physical installations and disaster recovery', 'NO-6.3',
            [check('What is the difference between RPO and RTO?', 'RPO is acceptable data loss; RTO is acceptable downtime',
                   ['RPO is acceptable downtime; RTO is acceptable data loss', 'They are the same target, measured by two teams'],
                   'RPO looks back from the disaster to the last good copy; RTO looks forward to when service must be back. Swapping '
                   'them leads to the wrong backup or site design.', mc=[RPO, RPO])],
            plain('''<p>Where equipment lives matters.</p>
<ul><li>The <strong>MDF</strong> is the main wiring room. An <strong>IDF</strong> is a closet for one floor.</li>
<li>Racks are 19 inches wide. One rack unit (1U) is 1.75 inches.</li>
<li>Match device airflow to the hot and cold aisles. Keep inlet air about 18–27 °C.</li>
<li>A <strong>UPS</strong> keeps power on in a cut. A <strong>PDU</strong> shares power across a rack.</li></ul>
<p>For disasters: <strong>RPO</strong> is how much data you can lose. <strong>RTO</strong> is how long you can be down.</p>
<p>A <strong>hot</strong> site is ready now, a <strong>warm</strong> site needs data restored, a <strong>cold</strong> site is an empty room.</p>''',
                  L.format('6.3') + '; ' + DR,
                  [check('What does a PDU do that a UPS does not?', 'Spreads power to each device in a rack', ['Keeps devices running in a power cut', 'Cools the rack in hot weather'],
                         'A PDU distributes power within a rack. Keeping devices running through an outage is the UPS’s job, and neither '
                         'of them cools equipment.', mc=[UPS, UPS])]),
            analogy('''<p>Think of saving a long essay.</p>
<p>If your laptop dies, <strong>RPO</strong> is how much writing you can stand to lose: autosave every 15 minutes means at most 15 minutes. <strong>RTO</strong>
is how soon you need to be typing again. A friend’s laptop that is already on with your files synced is a <strong>hot site</strong>. A spare laptop
in a cupboard you must load your files onto is <strong>warm</strong>. An empty desk where you must first buy a laptop is <strong>cold</strong>.</p>
<p>A power bank keeps the laptop alive through a short cut (<strong>UPS</strong>); a power strip feeds the laptop, lamp and phone (<strong>PDU</strong>).</p>''',
                    L.format('6.3') + ' (essay analogy written for this rung); ' + DR,
                    [check('In the essay story, autosave runs every 15 minutes. Which target does that set?', 'The RPO: at most 15 minutes of work lost',
                           ['The RTO: back to typing within 15 minutes', 'The MTBF: a failure every 15 minutes'],
                           'How often copies are taken limits data loss, which is RPO. RTO is about time to resume, and MTBF is the '
                           'average time between failures.', mc=[RPO, RPO])]),
            visual('''<ol class="ladder-trace"><li>Business owner sets <strong>RPO 15 minutes</strong>, <strong>RTO 1 hour</strong> for the order system.</li>
<li>Nightly backups give a 24-hour RPO: not enough. Add database replication to a second site.</li>
<li>A cold site could take days: fails the RTO.</li>
<li>A warm site with replicated data and pre-built servers can meet one hour.</li>
<li>Prove it: planned failover twice a year, plus a tabletop exercise.</li>
<li>Closet check: IDF switch rebooting in summer, no ventilation, UPS at 92%: fix airflow, request ventilation, shed load, document.</li></ol>''',
                   L.format('6.3') + '; ' + DR,
                   [check('In the trace, why does a cold site fail the order system’s needs?', 'Equipping it takes days, beyond the RTO',
                          ['Its data is replicated far too often', 'It costs more to run than a hot site does'],
                          'A cold site has space but no ready hardware, so recovery takes far longer than an hour. It holds no replicated '
                          'data, and it is the cheapest option.', mc=[RPO, RPO])]),
            tryit('<p>Sort each fact into physical installation or disaster recovery.</p>', L.format('6.3') + '; ' + DR,
                  [check('Which site type has hardware and network ready but needs current data restored?', 'A warm site', ['A hot site', 'A cold site'],
                         'A warm site has equipment and connectivity, but data must be restored. A hot site is fully current, and a cold '
                         'site has neither hardware nor data.', mc=[RPO, RPO])],
                  widget=sort('Physical or recovery?',
                              {'Physical installation': ['Rack 19 in wide, 1U = 1.75 in', 'Hot-aisle/cold-aisle airflow', 'PDU in each rack'],
                               'Disaster recovery': ['RPO 15 minutes', 'Warm site with pre-built servers', 'Twice-yearly failover test']},
                              'Notice that UPS load belongs to both.'))),
        'network-documentation-and-life-cycle-processes': section(
            'Network documentation and life-cycle processes', 'NO-6.3',
            [check('What is the difference between EOL and EOS?', 'EOL: no longer sold. EOS: no more fixes',
                   ['EOL: no more fixes. EOS: no longer sold', 'They both mean the device must be removed today'],
                   'End of life means the vendor stops selling it; end of support means no more patches, which is the security '
                   'deadline. Neither forces removal on the day.', mc=[EOL, EOL])],
            plain('''<p>Good records save the next person hours.</p>
<ul><li><strong>Physical diagrams</strong> show devices and cables. <strong>Logical diagrams</strong> show subnets, VLANs and routing.</li>
<li><strong>Rack diagrams</strong> and <strong>cable maps</strong> show what is where.</li>
<li><strong>Asset inventory</strong>: hardware, licences, warranty.</li>
<li><strong>IPAM</strong> tracks every address so none are used twice.</li>
<li><strong>SLA</strong>: what a provider promises.</li>
<li><strong>Golden config</strong>: the approved starting config.</li></ul>
<p>Plan for <strong>end of support</strong>. When you retire a device, wipe it and update every record.</p>''',
                  L.format('6.3') + '; ' + DOC,
                  [check('What does a logical diagram show that a physical diagram does not?', 'Subnets, VLANs, routing and flows',
                         ['Rack positions of each device', 'The length and route of each cable'],
                         'Logical diagrams show layer-2 and layer-3 structure; physical diagrams, rack elevations and cable maps show '
                         'where devices and cables really are.', mc=[DIAG, DIAG])]),
            analogy('''<p>Think of a city’s records office.</p>
<p>The street map with every building and pipe is the <strong>physical diagram</strong>. The bus-route map that ignores exact streets but shows
which areas connect is the <strong>logical diagram</strong>. The land registry, which stops two people claiming the same plot, is <strong>IPAM</strong>.
The list of every council vehicle and its warranty is the <strong>asset inventory</strong>.</p>
<p>When a bus model is no longer made it is <strong>end of life</strong>; when the maker stops supplying parts it is <strong>end of support</strong>,
and that is when you must plan its replacement. New buses are fitted out from the same approved design: the <strong>golden configuration</strong>.</p>''',
                    L.format('6.3') + ' (records-office analogy written for this rung); ' + DOC,
                    [check('In the records-office story, which record stops two people claiming the same plot?', 'IPAM', ['The asset inventory', 'The service-level agreement'],
                           'IPAM tracks subnets, scopes, reservations and statics so no address is assigned twice. The inventory lists '
                           'equipment, and an SLA records a provider’s promises.', mc=[EOL, EOL])]),
            visual('''<ol class="ladder-trace"><li>The inventory shows an access switch reaches <strong>end of support</strong> next quarter: no more security fixes.</li>
<li>Raise a change request with scope, window and rollback.</li>
<li>Configure the new switch from the <strong>golden config</strong>.</li>
<li>Cut over using the <strong>cable map</strong>, so every lead returns to the same port; update the rack diagram.</li>
<li>Decommission the old switch: wipe its config, remove it from IPAM and the inventory, dispose of it per policy.</li></ol>''',
                   L.format('6.3') + '; ' + DOC,
                   [check('A printer was given a static IP that “looked free” and knocked the finance server off. Which record would have prevented it?',
                          'Current IPAM records', ['A newer rack diagram of the server room',
                           'The printer vendor’s warranty record'],
                          'IPAM tracks every assignment so a “free-looking” address is checked before use. Rack diagrams and warranty '
                          'records do not show address use.', mc=[EOL, DIAG])]),
            tryit('<p>Sort each item into the document set it belongs to.</p>', L.format('6.3') + '; ' + DOC,
                  [check('What is a golden configuration?', 'The approved baseline new devices start from',
                         ['The most recent running config of any device', 'A backup copy kept on the same device'],
                         'A golden config is the approved standard that new devices use and running devices are compared to for drift. '
                         'A latest running config or a local backup is not a reviewed standard.', mc=[EOL, EOL])],
                  widget=sort('Which record?',
                              {'Diagrams': ['Rack elevation', 'Layer 2 VLAN diagram', 'Cable map with labels'],
                               'Inventory / life cycle': ['Warranty end date', 'EOS date for a switch model', 'Decommission record'],
                               'Configuration': ['Golden config', 'Nightly config backup and diff']},
                              'Notice that each record answers a different question for the next technician.'))),
    },
    '6.4': {
        'the-scenario': skip('The scenario', 'activity', 'The capstone ticket the student works; it sets up practice, not a concept.'),
        'your-turn-scaffolded-checklist': skip('Your turn — scaffolded checklist', 'activity', 'The checklist the student fills in during the capstone drill.'),
        'common-beginner-mistakes': skip('Common beginner mistakes', 'reference', 'Short list of capstone pitfalls; the ideas behind them are laddered in 6.1–6.3.'),
        'check-your-understanding': skip('Check your understanding', 'activity', 'A self-check prompt for the capstone; it is practice, not an explanation.'),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '6.1': {'core-content': '56c2bfaa0326', 'incident-application': '0fddf18cfcdc', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '4ff7b89ae0d0', 'beyond-the-quiz': '1b4e309de944', 'interface-states-error-counters-and-the-troubleshooting-tool': '15b73215b424'},
    '6.2': {'core-content': '39b469842b28', 'incident-application': 'b0e8b90f5a1d', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '72741925e0f6', 'beyond-the-quiz': '81143799eaf8'},
    '6.3': {'core-content': '71841c4d9fab', 'incident-application': '67ab36d89708', 'standard-of-work': 'c8a9116f574c', 'practice-standard-for-this-lesson': '455e0be0b7fc', 'operational-discipline': '10e5248b1384', 'beyond-the-quiz': '507643a13c2e', 'physical-installations-and-disaster-recovery': 'f4f0d86507e4', 'network-documentation-and-life-cycle-processes': 'fe43eaea0def'},
    '6.4': {'the-scenario': '90d8edd5216e', 'your-turn-scaffolded-checklist': 'c77eb8957738', 'common-beginner-mistakes': '4fe854d22832', 'check-your-understanding': 'cdda2cb3f068'},
}

# ---- pass 21: former skips laddered from lesson data (Pending SME review) ----
from curriculum_v2.ladder.netops import _gen as _G  # noqa: E402

_DATA = {
    '6.1': dict(
        title='Pattern Library', an='triage cards', ab='match the pattern to the tests',
        case='One PC is slow on the network only for large file copies; small web pages are fine.',
        steps=[('11:00', 'Check interface speed and duplex', '100 Mb half duplex'),
               ('11:03', 'Check switch port', '1 Gb full duplex fixed'),
               ('11:06', 'Check late collisions on the port', 'rising'),
               ('11:09', 'Set both ends to auto', 'pending change approval')],
        esc='one PC; duplex mismatch; late collisions rising; port fixed full; switch change needed.',
        status='One computer is slow for big copies because of a link setting mismatch. A switch change is scheduled; next update at 11:30.',
        neg='“Small pages load fine” points away from DNS.',
        par='replacing the NIC and changing the port settings together.',
        good=['PC 100/half, switch 1000/full', 'Late collisions rising'], bad=['Swapped NIC, seems OK', 'Changed both ends and cable'],
        plist=[('Name the pattern', 'matched', 'unknown pattern'),
               ('Run its first test', 'expected result', 'unexpected'),
               ('Run its second test', 'confirms', 'rules it out'),
               ('Pick the fix owner', 'named', 'escalate'),
               ('Verify', 'symptom gone', 'try next pattern')],
        up='a library of known fault signatures.', down='speed of response on common tickets.',
        user='Your computer and the network box disagree on how to talk; we are making them agree.',
        mist=['Ignoring the pattern and testing at random', 'Forcing one pattern onto every ticket'],
        escw='the pattern points to a device you do not own.',
        scen=('Slow only for big copies.', ['Duplex mismatch', 'Bad cable', 'Server disk'],
              'compare speed and duplex on both ends', 'both settings and counters.'),
        lab=('sw-int-status', 'Read interface status, speed and duplex.')),
    '6.2': dict(
        title='Method Under Pressure', an='a calm pilot', ab='checklists in turbulence',
        case='During a payroll deadline, the finance share is unreachable and a manager demands an instant fix.',
        steps=[('16:00', 'Scope who is affected', 'all finance users'),
               ('16:03', 'Ping the file server', 'replies'),
               ('16:05', 'Test TCP 445', 'times out'),
               ('16:08', 'Check recent changes', 'firewall update at 15:45')],
        esc='finance users; server up; SMB 445 blocked since 15:45 firewall update; firewall owner and manager informed.',
        status='Finance cannot reach the shared drive since 15:45. We know which change caused it and are rolling it back; next update at 16:30.',
        neg='“Server replies to ping” rules out a down server.',
        par='rebooting the server and changing the firewall during the deadline.',
        good=['TCP 445 times out, 16:05', 'Firewall change at 15:45'], bad=['Rebooted server under pressure', 'Tried fixes, unsure which'],
        plist=[('State impact', 'who and what', 'unknown scope'),
               ('Form a theory', 'one likely cause', 'many guesses'),
               ('Test it', 'confirms or rules out', 'inconclusive'),
               ('Communicate', 'status sent', 'nobody informed'),
               ('Fix, verify, document', 'user confirms', 'escalate')],
        up='a method you follow even when rushed.', down='the quality of every decision under pressure.',
        user='We know the shared drive is down and why; we are undoing the change now and will update you at 4:30.',
        mist=['Skipping steps because the manager is shouting', 'Promising a fix time'],
        escw='the fix needs approval you do not hold.',
        scen=('Share down at a deadline.', ['Firewall change', 'Server down', 'DNS'],
              'ping the server then test port 445', 'tests, times and change found.'),
        lab=('ticket-method', 'Work the method step by step on the ticket.')),
    '6.3': dict(
        title='Verification and Documentation', an='a court record', ab='evidence is required',
        case='A VLAN fix is applied and the network team says it is done, but no user has tested.',
        steps=[('12:00', 'Ask the user to test the app', 'works'),
               ('12:03', 'Check the user’s IP', 'correct VLAN'),
               ('12:05', 'Write root cause', 'port in wrong VLAN'),
               ('12:08', 'List ruled-out causes', 'cable, DHCP, DNS')],
        esc='not needed; fix verified by the user; ticket closed with cause and ruled-outs.',
        status='The fault is fixed and the user has confirmed it works. The ticket records the cause and what was ruled out.',
        neg='“DHCP lease normal” is a ruled-out cause worth writing.',
        par='closing the ticket and also making an extra tidy-up change.',
        good=['User confirmed app works 12:00', 'Ruled out: cable, DHCP, DNS'], bad=['Fixed the app, closing ticket', 'Switch lights green, so done'],
        plist=[('User verifies', 'works for them', 'still failing'),
               ('Check the evidence', 'matches fix', 'mismatch'),
               ('Write root cause', 'specific', 'vague'),
               ('List ruled-outs', 'listed', 'missing'),
               ('Close with timeline', 'complete', 'gaps')],
        up='evidence from tests and the user.', down='trust in the ticket history and future fixes.',
        user='Please try the app now and tell me if it works; I will close the ticket once you confirm.',
        mist=['Closing on green lights', 'No ruled-out list'],
        escw='the user still reports the fault.',
        scen=('Fix applied, untested.', ['Fix worked', 'Fix partial', 'Wrong fault'],
              'ask the affected user to test the exact task', 'user confirmation, cause, ruled-outs.'),
        lab=('win-full-triage', 'Verify the fix and write action → result.')),
}
_CAP = dict(
    title='weekend firewall change', short='Half the users lose the web app', an='an emergency team', ab='one coordinator, clear roles',
    scen='after a weekend firewall change, half the users cannot reach the main web app on Monday, and you coordinate the checks.',
    why='It trains you to correlate the change, test, get approval and verify with users.',
    steps=['Scope affected users', 'Correlate with the change', 'Test the app port', 'Get approval to roll back', 'Verify with users'],
    layer=['scope', 'change', 'transport', 'approval', 'verification'],
    items=['Scope', 'Change correlation', 'Tests', 'Approval for action', 'User verification', 'Timeline notes'],
    mist=[('Forward-fix without evidence', 'Test before changing'), ('No user verification after green lights', 'Ask users to confirm')],
    lab=('ticket-method', 'Coordinate the checks and keep the timeline.'))
_G.apply(LESSONS, MISCONCEPTIONS, CHAPTER, _DATA, _CAP, 'NO-6.2')
