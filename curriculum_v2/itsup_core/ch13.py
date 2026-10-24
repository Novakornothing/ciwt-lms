"""ITSUP Chapter 13 — Windows CLI & VM Lab Track (pass 9 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 13
SOURCES_USED = ['ms-cmd', 'ms-wmic']

LESSONS = {
    (13, 1): {
        'objectives': [
            'Prepare a lab virtual machine with a snapshot or checkpoint before any change, and revert it afterwards',
            'Collect a baseline inventory (device name, edition, version and build, network settings) before changing anything',
            'Distinguish lab-safe commands from destructive ones and explain why destructive disk commands are never run in this course',
        ],
        'html': sme_note() + '''
<h3>Why a virtual machine</h3>
<p>A <strong>virtual machine (VM)</strong> is a complete computer — firmware, disk, network adapter and operating system — that runs
as software on a host PC. Hypervisors such as Hyper-V (built into Windows Pro and Enterprise editions) and VirtualBox let you take a
<strong>snapshot</strong> (Hyper-V calls it a <strong>checkpoint</strong>): a saved state you can return to in seconds. That makes a VM the
right place to practise commands that change networking, services or settings. If you break the guest, you revert; nobody’s real PC
is harmed and the next student starts from the same clean state.</p>
<p>Treat the guest as shop property anyway. The habits you build here — inventory first, one change at a time, record action and
result — are the habits you will use on a user’s machine, where there is no snapshot.</p>
''' + figure('f13-1', 'The lab change loop', ['Snapshot', 'Inventory\n(baseline)', 'One change', 'Verify +\nrecord', 'Revert or\nkeep'],
             'Five boxes in order: take a snapshot or checkpoint; collect a baseline inventory; make one change; verify the result and record '
             'action and result; then revert to the snapshot or keep the change. A dashed arrow returns from the last box to “One change” for the next attempt.',
             'Every lab change starts from a snapshot and a recorded baseline, so the effect of each change can be seen and undone.', cols=5,
             loop=(4, 2, 'next attempt')) + '''
<h3>The baseline inventory</h3>
<p>Before you change anything, write down what is there. Three commands and one Settings page give you a baseline:</p>
''' + table(['Evidence', 'Command or path', 'What to record'], [
            ['Device name and user', '<code>hostname</code> and <code>whoami</code>', 'The exact name you will put in the ticket; the account you are signed in as'],
            ['Edition, version and build', 'Settings → System → About, or <code>winver</code>', 'For example “Windows 11 Pro, version 24H2, OS build …” — copy, do not guess'],
            ['Network settings', '<code>ipconfig /all</code>', 'Adapter name, physical (MAC) address, DHCP enabled, IPv4 address, gateway, DNS servers, lease times'],
            ['Hardware identity', '<code>Get-CimInstance Win32_BIOS</code> in PowerShell', 'Serial number and firmware version for the asset record'],
        ]) + '''
<h3>Lab-safe and destructive commands</h3>
<p>Most commands in this chapter only <em>read</em> state (<code>ipconfig</code>, <code>tasklist</code>, <code>Get-NetIPConfiguration</code>).
A few <em>change</em> state but are easy to reverse (<code>ipconfig /renew</code>, restarting an adapter). Some are destructive: the
<code>clean</code> command inside <code>diskpart</code> wipes the partition table of the selected disk, and a mistyped disk number
selects the wrong disk. Destructive disk commands are not used in this course, even on a VM — the habit of typing them “because it is only a lab”
is exactly what destroys data later.</p>
''' + worked('a lab baseline', '''
<p>Before the DNS lab, a student records: <code>hostname</code> → <code>LAB-W11-07</code>; About → Windows 11 Pro 24H2; <code>ipconfig /all</code>
→ Ethernet, DHCP enabled yes, IPv4 10.0.2.15, gateway 10.0.2.2, DNS 10.0.2.3; checkpoint “before-dns-lab” taken at 09:10. When the lab breaks name
resolution, every later reading is compared with these values, and the checkpoint restores the guest in under a minute.</p>''') + cfu(
            ('What does a snapshot or checkpoint give you that a user’s PC does not?',
             'A saved state you can return to in seconds, so a failed change can be undone completely.'),
            ('Name three items in a baseline inventory.',
             'Device name, Windows edition/version/build, and the adapter’s address, gateway and DNS servers (also the serial number).'),
            ('Why is diskpart clean never used in this course?',
             'It wipes the selected disk’s partition table; a wrong disk number destroys data, and practising it builds a dangerous habit.')),
    },
    (13, 2): {
        'objectives': [
            'Run hostname, whoami and ipconfig /all and record their output as ticket evidence',
            'Interpret ipconfig /all fields to tell a working DHCP lease from a self-assigned (169.254.x.x) address',
            'Use PowerShell CIM and NetTCPIP cmdlets in place of the removed WMIC tool to collect the same evidence',
        ],
        'html': sme_note('Core content added in pass 9. WMIC removal status checked against Microsoft Support (August 2026).') + '''
<h3>Reading ipconfig /all</h3>
<p><code>ipconfig /all</code> is the first command for almost every network ticket because it shows, for each adapter, what the PC
<em>thinks</em> its network settings are. Read it top to bottom for the adapter that should be connected:</p>
''' + table(['Field', 'What it tells you', 'Warning sign'], [
            ['Media State', 'Whether the adapter sees a link', '“Media disconnected” — cable, switch port, Wi-Fi association or a disabled VM adapter'],
            ['DHCP Enabled', 'Whether the address is automatic', '“No” on a PC that should use DHCP — someone set a static address'],
            ['IPv4 Address', 'The address in use', '169.254.x.x — Automatic Private IP Addressing (APIPA): no DHCP server answered'],
            ['Default Gateway', 'The router for other networks', 'Blank — the PC can only reach its own subnet'],
            ['DNS Servers', 'Who resolves names', 'An unexpected address (an old server, a public resolver on a managed PC)'],
            ['Lease Obtained / Expires', 'When DHCP last answered', 'Times far in the past with no renewal'],
        ]) + '''
<h3>PowerShell for the same evidence</h3>
<p>The <strong>WMIC</strong> command-line tool is deprecated and, according to Microsoft, has been removed from Windows 11 versions 24H2 and 25H2
with the August 2026 update; it is no longer offered as an optional feature. The underlying WMI/CIM data is still there — you read it with
PowerShell. Learn the replacements now:</p>
''' + table(['Old habit', 'PowerShell replacement', 'Module'], [
            ['<code>wmic bios get serialnumber</code>', '<code>Get-CimInstance Win32_BIOS | Select-Object SerialNumber</code>', 'CimCmdlets'],
            ['<code>wmic os get caption,version</code>', '<code>Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, LastBootUpTime</code>', 'CimCmdlets'],
            ['<code>ipconfig /all</code> (summary)', '<code>Get-NetIPConfiguration</code>', 'NetTCPIP'],
            ['Adapter state', '<code>Get-NetAdapter</code> (Status, LinkSpeed, MacAddress)', 'NetAdapter'],
            ['DNS servers per adapter', '<code>Get-DnsClientServerAddress</code>', 'DnsClient'],
        ]) + worked('evidence lines for a ticket', '''
<p>A student writes four evidence lines, each with the command, so another technician can repeat them:<br>
1. <code>hostname</code> → LAB-W11-07.<br>
2. <code>ipconfig /all</code> → Ethernet, Media State connected, DHCP enabled Yes, IPv4 169.254.31.8, gateway blank.<br>
3. <code>Get-NetAdapter</code> → Ethernet Up, 1 Gbps.<br>
4. Interpretation: link is up but no DHCP lease — the fault is in the DHCP path (server, relay, VLAN or VM network setting), not the cable.</p>''') + cfu(
            ('A PC shows IPv4 169.254.12.40 and no gateway. What does that tell you?',
             'APIPA: the adapter has a link but no DHCP server answered, so it assigned itself a link-local address.'),
            ('What do you use instead of wmic bios get serialnumber?',
             'Get-CimInstance Win32_BIOS | Select-Object SerialNumber in PowerShell.'),
            ('Why write the command next to each evidence line?',
             'So another technician can repeat it and see the same result; output without its command is hard to trust.')),
        'sources': ['ms-cmd', 'ms-wmic'],
    },
    (13, 3): {
        'objectives': [
            'Perform a DHCP release and renew and an adapter restart, recording the before and after state',
            'Choose the least disruptive reset — renew, adapter restart, stack reset or Settings network reset — for a given symptom',
            'Explain what a Windows network reset removes and what must be reconfigured afterwards',
        ],
        'html': sme_note() + '''
<h3>A ladder of network resets</h3>
<p>Network “fixes” range from harmless to disruptive. Climb the ladder one rung at a time and record the result of each before
moving up. A higher rung undoes more configuration and takes longer to put right.</p>
''' + table(['Rung', 'Command or path', 'What it changes', 'Use when'], [
            ['1 Renew the lease', '<code>ipconfig /release</code> then <code>ipconfig /renew</code>', 'Drops and requests the DHCP address', 'Wrong or 169.254 address after a network change'],
            ['2 Restart the adapter', '<code>Restart-NetAdapter -Name "Ethernet"</code> (admin), or disable/enable in Settings', 'Resets the link and the adapter driver state', 'Media state flaps or the adapter seems stuck'],
            ['3 Reset the stack', '<code>netsh winsock reset</code> and <code>netsh int ip reset</code> (admin), then restart', 'Returns Winsock and TCP/IP settings to defaults', 'Lease and adapter are fine but connections still fail oddly'],
            ['4 Network reset', 'Settings → Network &amp; internet → Advanced network settings → Network reset', 'Removes and reinstalls every network adapter and restores networking components to defaults; the PC restarts', 'Last resort, after the lower rungs and with the user warned'],
        ]) + '''
<p>After a full network reset you may have to reconnect to Wi-Fi networks and re-enter their passwords, and reconfigure static
addresses, VPN clients and virtual switches. On a managed PC, do not use it without checking the organisation’s procedure: it can remove
settings that were deployed centrally.</p>
''' + scenario('“The internet went away after I moved desks”', '''
<p>A user plugs a laptop into a new desk port. <code>ipconfig /all</code> shows Media State connected and IPv4 169.254.88.3. The student
runs rung 1: <code>/release</code>, <code>/renew</code> — the renew times out. Rung 2: adapter restart — same result. Instead of climbing to
rung 3, they stop and think: the link is up and other PCs on that desk row get leases, so the stack is not the problem. They try the
neighbouring wall port: a lease arrives at once. The ticket goes to the network team: “Port 2-14B: link up, no DHCP — likely wrong VLAN.”
No reset was needed; the evidence pointed outside the PC.</p>''') + cfu(
            ('Which rung would you try first for a 169.254 address after a cable move?',
             'Rung 1: release and renew the DHCP lease, then record the result.'),
            ('What must you warn a user about before a Settings network reset?',
             'Adapters are reinstalled and the PC restarts; Wi-Fi passwords, static settings and VPN may need to be set up again.'),
            ('In the desk-move scenario, why was a stack reset not tried?',
             'The evidence (link up, no lease, other ports work) pointed to the switch port or VLAN, not to the PC’s software.')),
    },
    (13, 4): {
        'objectives': [
            'Determine whether a fault is in IP connectivity or in name resolution by testing an address and a name separately',
            'Compare nslookup, Resolve-DnsName and the hosts file to locate where a wrong answer comes from',
            'Resolve a broken name-resolution ticket end to end and write the verification step',
        ],
        'html': sme_note() + '''
<h3>Address first, then name</h3>
<p>“The internet is down” often means “names do not resolve”. Separate the two: if you can reach a known address but not a name,
routing works and the fault is in name resolution. If you cannot reach the address either, look at the lease, gateway and link first.</p>
''' + figure('f13-2', 'IP versus name decision path', ['Valid lease?\nipconfig /all', 'Reach gateway?\nping gateway', 'Reach by IP?\nTest-NetConnection', 'Name resolves?\nResolve-DnsName', 'Compare DNS\nservers + hosts'],
             'Five boxes in order. First check for a valid lease with ipconfig /all; then test the gateway; then test a known server by IP address with '
             'Test-NetConnection; then test the server’s name with Resolve-DnsName; if the IP works but the name fails, compare the configured DNS servers and the hosts file.',
             'Test the lease, the gateway and an IP address before blaming DNS; when the address works but the name fails, the fault is in name resolution.', cols=5) + '''
<h3>Three places a wrong answer comes from</h3>
''' + table(['Source', 'How to see it', 'Note'], [
            ['The DNS server', '<code>nslookup name</code> or <code>Resolve-DnsName name -DnsOnly</code>', 'nslookup asks the DNS server directly; it does not read the hosts file or the local cache'],
            ['The local cache', '<code>ipconfig /displaydns</code> or <code>Get-DnsClientCache</code>', 'Clear with <code>ipconfig /flushdns</code> or <code>Clear-DnsClientCache</code>'],
            ['The hosts file', 'C:\\Windows\\System32\\drivers\\etc\\hosts', 'An entry here overrides DNS for normal lookups; <code>Resolve-DnsName -NoHostsFile</code> skips it'],
        ]) + '''
<p><code>Test-NetConnection server -Port 443</code> tests a TCP port as well as name resolution, so it can show “name resolves, port open” or
“name resolves, port blocked” — two different tickets.</p>
''' + worked('the broken intranet name', '''
<p>Symptom: <code>intranet.lab.local</code> does not load on LAB-W11-07; it works on other PCs.<br>
1. <code>ipconfig /all</code>: valid lease, gateway 10.0.2.2, DNS 10.0.2.3 — same as the baseline.<br>
2. <code>Test-NetConnection 10.0.2.50 -Port 443</code>: TcpTestSucceeded True — the server is reachable by address.<br>
3. <code>Resolve-DnsName intranet.lab.local</code> returns 10.0.9.9 (wrong); <code>Resolve-DnsName intranet.lab.local -DnsOnly</code> returns 10.0.2.50 (right).<br>
4. Only the local path differs, so the student opens the hosts file and finds a stale line pointing the name at 10.0.9.9.<br>
5. Change: remove that one line (admin editor), run <code>ipconfig /flushdns</code>.<br>
6. Verify: <code>Resolve-DnsName intranet.lab.local</code> → 10.0.2.50 and the page loads. Ticket records each step and result.</p>''') + cfu(
            ('You can reach 10.0.2.50 but not intranet.lab.local. Where is the fault?',
             'In name resolution — routing to the server works.'),
            ('Why can nslookup give the right answer while the browser gets the wrong one?',
             'nslookup asks the DNS server directly; the browser uses the Windows resolver, which also reads the cache and the hosts file.'),
            ('What is the verification step after removing a bad hosts entry?',
             'Flush the cache, resolve the name again and confirm the correct address, then load the page.')),
        'sources': ['ms-cmd'],
    },
    (13, 5): {
        'objectives': [
            'Navigate Windows 11 Settings to About, Ethernet or Wi-Fi properties, Windows Update history and Accounts',
            'Map each Settings view to the command that shows the same fact, and confirm that both agree',
            'Locate the tools that are not in Settings — Services, Event Viewer, Device Manager — by their console names',
        ],
        'html': sme_note() + '''
<h3>Two views of one state</h3>
<p>Settings and the command line read the same configuration. A user can follow Settings paths over the phone; a technician can
copy command output into a ticket. Knowing both lets you guide a user and still collect exact evidence. When they disagree, something is
changing underneath (a VPN, a policy, a second adapter) — and that disagreement is evidence too.</p>
''' + table(['Fact', 'Settings path (Windows 11)', 'Command view'], [
            ['Device name, edition, version, build', 'System → About', '<code>hostname</code>, <code>winver</code>, <code>Get-CimInstance Win32_OperatingSystem</code>'],
            ['IP assignment and DNS servers', 'Network &amp; internet → Ethernet (or Wi-Fi → the network’s properties)', '<code>ipconfig /all</code>, <code>Get-NetIPConfiguration</code>'],
            ['Wi-Fi network and signal', 'Network &amp; internet → Wi-Fi', '<code>netsh wlan show interfaces</code>'],
            ['Installed updates', 'Windows Update → Update history', '<code>Get-HotFix</code> (lists updates recorded by Windows)'],
            ['Accounts on the PC', 'Accounts → Your info, and Other users', '<code>whoami</code>, <code>Get-LocalUser</code>'],
        ]) + '''
<h3>Tools that are not in Settings</h3>
<p>Some administration still lives in Microsoft Management Console (MMC) snap-ins. Open them from Run (Win+R) or Start by name:
<code>services.msc</code> (Services), <code>eventvwr.msc</code> (Event Viewer), <code>devmgmt.msc</code> (Device Manager),
<code>compmgmt.msc</code> (Computer Management). Settings menu names move between Windows releases; console names rarely do, which makes
them reliable instructions in a knowledge-base article.</p>
''' + scenario('guiding a user over the phone', '''
<p>A remote user says “Teams says I’m offline.” The technician asks them to open Settings → Network &amp; internet. The page says
“Connected, secured” on Wi-Fi. Next, Wi-Fi → the network’s properties: IPv4 address 192.168.1.23, DNS servers 192.168.1.1. The home network
looks normal, so the technician asks for Settings → Windows Update → Update history to confirm a pending restart, which the user reports
is waiting. After the restart Teams signs in. The ticket records each path, what the user read out, and the restart as the change.</p>''') + cfu(
            ('Where in Settings do you find the Windows version and build?',
             'System → About (Windows specifications).'),
            ('Which command shows the same Wi-Fi details as Settings → Wi-Fi?',
             'netsh wlan show interfaces (SSID, signal, radio type).'),
            ('Why give console names like services.msc in a KB article?',
             'Settings menus move between releases; console names are stable and work from Run or Start.')),
    },
    (13, 6): {
        'objectives': [
            'Identify running processes and the services they host with tasklist /svc and Get-Process before ending anything',
            'Use netsh and Get-NetIPConfiguration as two views of the same lease and adapter state',
            'Decide when a restart is justified, and record it as a change with a reason',
        ],
        'html': sme_note() + '''
<h3>Look before you end</h3>
<p>A restart clears the evidence. Before ending a task or restarting a PC, record what is running. <code>tasklist /svc</code> lists each
process with its process ID (PID) and, for service hosts, the services inside it — ending one <code>svchost.exe</code> can stop several services at once.
In PowerShell, <code>Get-Process | Sort-Object CPU -Descending | Select-Object -First 5</code> shows the processes that have used the most processor time.</p>
<p>If one process must be ended, target its PID: <code>taskkill /PID 4312</code> asks it to close; <code>/F</code> forces it; <code>/T</code>
also ends its child processes. Forcing a process can lose unsaved work — ask the user to save first when you can.</p>
<h3>netsh: another view of the same lease</h3>
<p><code>netsh interface ipv4 show config</code> shows, per interface, whether DHCP is enabled, the address, gateway and DNS servers. It should agree
with <code>ipconfig /all</code> and <code>Get-NetIPConfiguration</code>. Three tools agreeing is strong evidence; one disagreeing usually means you are
looking at a different interface (a VPN or virtual adapter) than you think.</p>
''' + table(['Reason to restart', 'Reason not to restart yet'], [
            ['An update says a restart is pending', 'You have not recorded the processes, errors or network state'],
            ['A driver or stack reset requires it (for example after netsh winsock reset)', 'The fault is intermittent and you need to see it happen'],
            ['Memory or a handle leak is confirmed and the app cannot be restarted alone', 'The user has unsaved work open'],
        ]) + worked('a stuck print job without a reboot', '''
<p>The user’s print queue is frozen. Instead of restarting the PC, the student runs <code>tasklist /svc /fi "services eq Spooler"</code> and records the
spoolsv.exe PID. In <code>services.msc</code> they stop the Print Spooler service, clear the stuck job, start the service again and print a test page.
Ticket: “Evidence: queue frozen, spooler PID recorded. Change: restarted Print Spooler service only. Result: test page printed; no PC restart needed.”</p>''') + cfu(
            ('Why can ending one svchost.exe stop several things at once?',
             'One service host process can contain several services; tasklist /svc shows which.'),
            ('ipconfig and netsh disagree about the DNS server. What do you suspect first?',
             'You are reading different interfaces — for example a VPN or virtual adapter.'),
            ('Give one reason to delay a restart.',
             'Evidence has not been recorded, the user has unsaved work, or you need to see an intermittent fault happen.')),
        'sources': ['ms-cmd'],
    },
}

GLOSSARY = [
    ('Virtual machine (VM)', 'A complete computer — firmware, disk, network adapter and operating system — running as software on a host.'),
    ('Snapshot / checkpoint', 'A saved state of a virtual machine that can be restored; Hyper-V calls it a checkpoint.'),
    ('APIPA', 'Automatic Private IP Addressing: a 169.254.x.x address Windows assigns itself when no DHCP server answers.'),
    ('CIM / WMI', 'The Windows management data store for hardware and OS facts, read in PowerShell with Get-CimInstance (WMIC is removed).'),
    ('Get-NetIPConfiguration', 'PowerShell (NetTCPIP) cmdlet summarising each adapter’s address, gateway and DNS servers.'),
    ('Resolve-DnsName', 'PowerShell (DnsClient) cmdlet that resolves a name; -DnsOnly and -NoHostsFile change where it looks.'),
    ('Test-NetConnection', 'PowerShell (NetTCPIP) cmdlet that tests ping, a TCP port and name resolution in one command.'),
    ('Hosts file', 'C:\\Windows\\System32\\drivers\\etc\\hosts; local name-to-address entries that override DNS for normal lookups.'),
    ('Network reset', 'Windows Settings option that removes and reinstalls network adapters and restores networking defaults; the PC restarts.'),
    ('PID', 'Process identifier: the number Windows assigns to a running process, used by taskkill /PID.'),
]

PLAN = {
    'warmup': 'Show an ipconfig /all with a 169.254 address and no gateway. Pairs write what it proves and the first rung of the reset ladder.',
    'guided': 'Take a checkpoint and a baseline together (13.1), rebuild the WMIC habits in PowerShell (13.2), then walk the IP-versus-name path on the broken intranet name (13.4).',
    'worked_example': 'Lesson 13.1 lab baseline; 13.2 evidence lines; 13.4 the broken intranet name; 13.6 the stuck print job without a reboot.',
    'cfu': ['What does 169.254.x.x with no gateway prove?',
            'What replaces wmic bios get serialnumber?',
            'Address works, name fails — where is the fault?',
            'Name two things to record before restarting a PC.'],
    'exit_ticket': 'Write the four evidence lines and the change for “the intranet works on every PC but mine”.',
    'misconceptions_add': ['“nslookup works, so DNS is fine on this PC.” nslookup skips the hosts file and cache; the browser does not.',
                           '“Network reset is the quick fix.” It is the last rung: it reinstalls adapters and removes Wi-Fi, static and VPN settings.',
                           '“WMIC still works on my PC.” It is removed from current Windows 11; use Get-CimInstance.'],
    'classroom_lab': 'CL-13',
    'materials_add': 'Classroom lab CL-13 (PowerShell evidence and name-resolution repair); WMIC-to-PowerShell card.',
}

ITEMS = [
    item('IT-13.1', 1, 'Which PowerShell command reads the BIOS serial number now that WMIC has been removed?',
         'Get-CimInstance Win32_BIOS', ['Get-NetAdapter -Serial', 'Get-HotFix -Hardware -All', 'Get-Process -Firmware'],
         'CIM classes still hold the hardware facts WMIC used to read; Get-CimInstance Win32_BIOS returns SerialNumber.'),
    item('IT-13.1', 2, 'ipconfig /all shows IPv4 169.254.31.8 and a blank default gateway. What does this indicate?',
         'No DHCP server answered the adapter', ['The DNS server has returned a wrong name', 'The adapter has no physical link at all', 'A static address was typed in by hand'],
         'A 169.254 address is APIPA, self-assigned when DHCP fails; a missing link would show Media disconnected.'),
    item('IT-13.1', 3, 'Why should each evidence line in a ticket include the command that produced it?',
         'So another technician can repeat it', ['So the ticket meets a minimum length', 'So the user can run it on their own', 'So the output is saved in the registry'],
         'Evidence is trustworthy when it can be reproduced; the command makes the line repeatable.'),
    item('IT-13.2', 1, 'A PC reaches 10.0.2.50 by address but not intranet.lab.local by name. Where is the fault?',
         'In name resolution on that path', ['In the default gateway setting', 'In the network adapter’s driver', 'In the DHCP lease for the PC'],
         'Reaching the server by address shows the adapter, the IP settings and the path to that host work; only the name lookup fails, so the fault is in name resolution (DNS server, suffix, cache or hosts file).'),
    item('IT-13.2', 2, 'nslookup returns the right address, but the browser goes to the wrong server. What should you check next?',
         'The hosts file and the local DNS cache', ['The DHCP lease time on the router', 'The speed and duplex setting of the adapter', 'The Windows Update history page'],
         'nslookup asks the DNS server directly; the Windows resolver also uses the cache and hosts file, so a difference points there.'),
    item('IT-13.2', 3, 'After removing a stale hosts-file entry, what is the best verification step?',
         'Flush the cache and resolve the name again', ['Restart the PC and close the ticket at once', 'Run netsh winsock reset to make it stick', 'Ask the user to wait until tomorrow'],
         'Flushing removes any cached wrong answer; resolving again proves the fix before the page is retested.'),
    item('IT-13.3', 1, 'Before ending a task with taskkill, what should you record first?',
         'The process, its PID and the services it hosts', ['The user’s password so you can sign back in', 'Only the exact time at which the PC was restarted', 'The serial number of the PC’s memory modules'],
         'tasklist /svc records the PID and hosted services, so you know exactly what ending the process will stop.'),
    item('IT-13.3', 2, 'ipconfig /all and netsh show different DNS servers. What is the most likely explanation?',
         'You are reading two different interfaces', ['One of the two tools is out of date', 'The DNS server address changes every minute', 'The PC needs a full network reset'],
         'Both read the same configuration; a mismatch usually means a VPN or virtual adapter is being read by mistake.'),
    item('IT-13.3', 3, 'Which situation best justifies restarting the PC now?',
         'A pending update requires a restart', ['The fault is intermittent and not seen', 'The user has unsaved documents open', 'No evidence has been recorded yet'],
         'A pending restart is a documented reason; the others are reasons to wait and collect evidence first.'),
    item('IT-13.4', 1, 'A lease renew fails after a desk move while other ports on the row work. What should you do next?',
         'Try a known-good port and escalate the bad one', ['Run netsh int ip reset and then restart the PC', 'Perform a full Settings network reset now', 'Reinstall the network adapter driver first'],
         'Evidence points to the switch port or VLAN; changing the PC’s stack would alter the wrong thing.'),
    item('IT-13.4', 2, 'What must a user be warned about before a Windows network reset?',
         'Wi-Fi, static and VPN settings may need redoing', ['All of their personal files will be deleted', 'Windows will be upgraded to the next feature release', 'The device will leave its domain or tenant'],
         'Network reset reinstalls adapters and restores networking defaults, then restarts; files and OS version are untouched.'),
    item('IT-13.4', 3, 'Which PowerShell command tests whether TCP port 443 is open on a server?',
         'Test-NetConnection server -Port 443', ['Resolve-DnsName server -Type 443 -DnsOnly', 'Get-NetAdapter server -Port 443', 'Get-CimInstance server -Port 443'],
         'Test-NetConnection with -Port performs a TCP test and reports TcpTestSucceeded.'),
]

LABS = {
    'CL-13': {
        'id': 'CL-13', 'title': 'PowerShell & DNS Repair', 'chapters': [('ITSUP', 13), ('CLIENT', 6)],
        'review': 'Pending SME review',
        'objective': 'Collect baseline evidence with PowerShell instead of WMIC, then isolate and repair a staged name-resolution fault on a lab VM and verify the fix.',
        'scenario': 'The instructor has added a stale hosts-file entry on a Windows 11 lab VM so that one intranet name resolves to the wrong address.',
        'prerequisites': ['Lessons 13.1–13.4', 'A Windows 11 lab VM with a checkpoint or snapshot'],
        'equipment': 'Windows 11 lab VM (Hyper-V or VirtualBox) with a checkpoint; PowerShell; a lab web server or any reachable address supplied by the instructor.',
        'low_cost': 'Use the LMS labs w11-powershell-net, win-dns-break and win-full-triage, with printed ipconfig and Resolve-DnsName output for the analysis steps.',
        'steps': [
            'Take a checkpoint named before-cl13. Record hostname, whoami and the edition/version/build from System → About.',
            'Run Get-CimInstance Win32_BIOS and Get-CimInstance Win32_OperatingSystem; record serial number, caption, version and last boot time.',
            'Run ipconfig /all and Get-NetIPConfiguration; record adapter, address, gateway and DNS servers and confirm the two agree.',
            'Test the server by address with Test-NetConnection <address> -Port 443 and record TcpTestSucceeded.',
            'Resolve the intranet name with Resolve-DnsName, then with -DnsOnly; record both answers and say which path is wrong.',
            'Find and remove the single stale hosts-file line (admin editor). Run Clear-DnsClientCache.',
            'Verify: resolve the name again and load the page. Write the ticket (evidence, cause, change, verification) and revert to the checkpoint.',
        ],
        'expected': 'Evidence lines each include their command; the fault is placed in the hosts file by comparing default and -DnsOnly answers; exactly one line is changed; the fix is verified.',
        'troubleshooting': ['If both Resolve-DnsName answers are wrong, the fault is on the DNS server — escalate rather than editing hosts.',
                            'If Test-NetConnection by address fails, return to the lease and gateway before looking at names.'],
        'reflection': ['Which single comparison proved the fault was local?', 'Which WMIC command did each CIM query replace?',
                       'What would you check before editing a hosts file on a managed user PC?'],
        'rubric': 'lab', 'minutes': 60, 'objectives': ['IT-13.1', 'IT-13.2', 'IT-13.4'],
    },
}
