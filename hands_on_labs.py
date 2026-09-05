"""CIWT proprietary hands-on lab chapters — Windows CLI, VM practice, and switch/router CLI labs.
Original instructional scenarios for IST training. Not vendor exam dumps.
"""

def _cli_box(title, lines):
    body = "\n".join(f"<div class='cli-line'><code>{line}</code></div>" for line in lines)
    return (
        f"<div class='lab-panel' style='background:#0b1524;color:#e8f0ff;border-color:#3ec7ff'>"
        f"<div class='lab-title' style='color:#f0c14b'><span>CLI</span> {title}</div>"
        f"{body}</div>"
    )


# Shared CSS snippet for lessons
_LAB_CSS = """
<style>
.cli-line{font-family:ui-monospace,Consolas,monospace;font-size:.85rem;padding:.15rem 0;color:#c5e4ff}
.lab-goal{background:rgba(62,199,255,.08);border-left:4px solid #3ec7ff;padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.vm-setup{background:rgba(201,162,39,.1);border-left:4px solid #c9a227;padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
</style>
"""

WINDOWS_CLI_CHAPTERS = [
  {
    "title": "Chapter 13 — Windows CLI & VM Lab Track",
    "order": 13,
    "minutes": 400,
    "overview": "Hands-on command prompt and virtual machine labs for support technicians. Practice on isolated lab VMs only—never production.",
    "lessons": [
      {
        "title": "13.1 Lab VM Setup and Safety",
        "order": 1,
        "minutes": 90,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Describe why lab work uses isolated VMs instead of production PCs</li>
<li>List minimum VM settings for a Windows client lab (CPU, RAM, disk, network mode)</li>
<li>Explain Host-Only vs NAT vs Bridged networking for lab safety</li>
<li>Create a pre-lab checklist that protects the host and the network</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> Chapter 1 safety and documentation. Lab power is still real power—habits transfer.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>A <strong>virtual machine (VM)</strong> is a computer simulated in software on your host PC. You can break networking, install tools, and snapshot restore without destroying a physical classroom machine. Bridged mode can put a lab VM on the real network—use Host-Only or NAT unless an instructor directs otherwise.</p></div>
<div class="vm-setup"><strong>Recommended starter lab</strong>
<ul>
<li>Hypervisor: Hyper-V, VMware Workstation Player, or VirtualBox (per site standard)</li>
<li>Guest: Windows 10/11 evaluation or site lab image</li>
<li>RAM: 4 GB+ guest if host allows; 2 virtual CPUs</li>
<li>Network: NAT for internet updates; Host-Only for isolated peer labs</li>
<li>Snapshot: take one clean snapshot before every major experiment</li>
</ul></div>
<section class="sublesson"><h3>Safety rules for VM labs</h3>
<ol>
<li>Never practice malware samples on production or home networks without isolation.</li>
<li>Do not store real user passwords or production data inside lab VMs.</li>
<li>Document host resources so the classroom PC remains usable.</li>
<li>Revert to snapshot when the guest is in an unknown state.</li>
</ol>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Build your lab pad</div>
<ol>
<li>Create a VM named <code>CIWT-WIN-LAB</code>.</li>
<li>Set network to NAT; confirm the guest gets an IP.</li>
<li>Take snapshot <code>clean-base</code>.</li>
<li>Write a five-line ticket-style note describing what you built.</li>
</ol></div>
</section>
"""
      },
      {
        "title": "13.2 Command Prompt Foundations",
        "order": 2,
        "minutes": 100,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Open Command Prompt or Terminal and navigate the file system</li>
<li>Use <code>ipconfig</code>, <code>ping</code>, <code>tracert</code>, and <code>nslookup</code> to gather evidence</li>
<li>Interpret common outputs without guessing</li>
<li>Record commands and results in ticket notes</li>
</ul></div>
<div class="plain-english"><h4>In plain English</h4>
<p>The command line is a precise way to ask the OS questions. GUIs hide detail; CLI output is copy/paste evidence for tickets and escalations.</p></div>
<div class="lab-goal"><strong>Lab goal:</strong> From a Windows VM, prove whether name resolution, local stack, and remote reachability work—and write the proof down.</div>
""" + _cli_box("Identity and interface", [
    "hostname",
    "ipconfig /all",
    "ipconfig /displaydns",
]) + _cli_box("Reachability tests", [
    "ping 127.0.0.1",
    "ping <default-gateway>",
    "ping 8.8.8.8",
    "ping intranet.example.local",
    "tracert intranet.example.local",
    "nslookup intranet.example.local",
]) + """
<section class="sublesson"><h3>How to read results</h3>
<ul>
<li><strong>127.0.0.1 fails</strong> — local TCP/IP stack or firewall pathology (rare but serious).</li>
<li><strong>Gateway fails, 8.8.8.8 fails</strong> — local link, cable/Wi-Fi, or host IP config.</li>
<li><strong>IP works, name fails</strong> — DNS path problem.</li>
<li><strong>Name works off-site, fails on-site</strong> — internal DNS or split-horizon issues.</li>
</ul>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Evidence pack</div>
<ol>
<li>Run the command set above on your lab VM.</li>
<li>Paste outputs into a mock ticket (sanitize any real hostnames if needed).</li>
<li>State in one sentence: “Fault domain is ___ because ___.”</li>
</ol></div>
</section>
"""
      },
      {
        "title": "13.3 Network Reset and Adapter Labs",
        "order": 3,
        "minutes": 90,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Release/renew DHCP addresses safely</li>
<li>Flush DNS cache when stale records are suspected</li>
<li>Use <code>netsh</code> only with a rollback plan on lab systems</li>
<li>Document before/after addressing</li>
</ul></div>
""" + _cli_box("DHCP and DNS cache", [
    "ipconfig /all",
    "ipconfig /release",
    "ipconfig /renew",
    "ipconfig /flushdns",
    "ipconfig /registerdns",
]) + """
<section class="sublesson"><h3>Discipline</h3>
<p>On production, coordinate before releasing addresses on servers. On lab VMs, practice the sequence and always capture <code>ipconfig /all</code> before and after.</p>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Renew path</div>
<ol>
<li>Note current IPv4, DHCP server, and DNS servers.</li>
<li>Release and renew; compare results.</li>
<li>Flush DNS; resolve an internal name again with <code>nslookup</code>.</li>
</ol></div>
</section>
"""
      },
      {
        "title": "13.4 Capstone — Broken Name Resolution Ticket",
        "order": 4,
        "minutes": 80,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Run an ordered CLI isolation for “intranet works by IP, not by name”</li>
<li>Produce a complete evidence package</li>
<li>State next action: client DNS fix, server DNS, or escalate</li>
</ul></div>
<div class="lab-goal"><strong>Scenario:</strong> User can open <code>http://10.10.10.50</code> but not <code>http://app.training.local</code>.</div>
<section class="sublesson"><h3>Live demonstration order</h3>
<ol>
<li>Confirm symptom and scope (one PC vs many).</li>
<li><code>ping 10.10.10.50</code> — expect success if IP path works.</li>
<li><code>nslookup app.training.local</code> — capture which DNS server answered and the result.</li>
<li><code>ipconfig /all</code> — verify DNS server list matches site standard.</li>
<li>Try alternate DNS only on <em>lab</em> with approval pattern; document.</li>
<li>Verify browser workflow, not only ping.</li>
</ol>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Write the ticket</div>
<p>Include commands, outputs, root-cause hypothesis, fix, and verification.</p></div>
</section>
"""
      },
      {
        "title": "13.5 Windows 11 Settings paths that match the live labs",
        "order": 5,
        "minutes": 70,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Open Settings with Win+I and find System → About</li>
<li>Read IPv4, gateway, and DNS from Network &amp; internet → Ethernet</li>
<li>Recycle a DHCP lease from ncpa.cpl (Disable / Enable), not a fake Renew button</li>
<li>Open services.msc and name DHCP Client, DNS Client, and Defender</li>
</ul></div>
<div class="plain-english"><h4>In plain English</h4>
<p>Command Prompt is faster for tickets. Settings is what the user already has open. A technician who can only use one of those two views will stall. The live GUI labs on this site follow the same labels you will see on a Windows 11 Education PC.</p></div>
<section class="sublesson"><h3>Memorize these four paths</h3>
<ol>
<li><strong>Who is this PC?</strong> Win+I → System → About. Copy device name, edition, version, OS build.</li>
<li><strong>What is the address?</strong> Win+I → Network &amp; internet → Ethernet. IP assignment, IPv4, gateway, DNS.</li>
<li><strong>Lease looks stale.</strong> Network &amp; internet → Advanced network settings → More adapter options → right-click Ethernet → Disable → Enable. That is ncpa.cpl.</li>
<li><strong>Service health.</strong> Start → type Services → DHCP Client / DNS Client / Microsoft Defender Antivirus Service should be Running.</li>
</ol>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> GUI then CLI</div>
<p>Run the Windows 11 GUI About lab, then immediately run <code>hostname</code> and <code>systeminfo</code> in the CLI lab. The names must match. That is how you prove the two views are the same computer.</p></div>
</section>
"""
      },
      {
        "title": "13.6 Processes, netsh, and when not to reboot",
        "order": 6,
        "minutes": 55,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>List processes with tasklist and Get-Process</li>
<li>Read the same IPv4 block with netsh interface ip show config</li>
<li>Explain why a reboot is a last step, not a first step</li>
</ul></div>
<div class="plain-english"><h4>In plain English</h4>
<p>Rebooting clears evidence. <code>tasklist</code> tells you whether Defender, Explorer, or a hung installer is sitting on the CPU. <code>netsh</code> is the older interface tool; some checklists still require it. Learn both so a senior tech's script does not look like a foreign language.</p></div>
<section class="sublesson"><h3>Order on a slow PC</h3>
<ol>
<li>Ask how long it has been slow and what changed.</li>
<li><code>tasklist</code> or <code>Get-Process</code> — look for a process eating memory.</li>
<li><code>ipconfig /all</code> then <code>netsh interface ip show config</code> if the ticket says netsh.</li>
<li>Only then consider a restart, and say what you expect it to fix.</li>
</ol></div>
"""
      },
    ],
  }
]

NETWORK_LAB_CHAPTERS = [
  {
    "title": "Chapter 9 — Switch & Router CLI Lab Track",
    "order": 9,
    "minutes": 480,
    "overview": "Beginner switch and router command-line labs for CIWT networking. Practice on simulators or isolated lab gear only. Commands are educational patterns used across many platforms.",
    "lessons": [
      {
        "title": "9.1 Lab Topology and CLI Access",
        "order": 1,
        "minutes": 90,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Describe a simple lab topology: two PCs, one switch, one router</li>
<li>Connect a console session and enter user/privileged modes safely</li>
<li>Set a hostname and document the device role</li>
<li>Explain why lab configs must not be copied blindly into production</li>
</ul></div>
<div class="plain-english"><h4>In plain English</h4>
<p>Switches forward frames inside a LAN. Routers forward packets between networks. You configure both with a text CLI. In training we use simulators (or isolated racks) so mistakes teach instead of outage.</p></div>
<div class="vm-setup"><strong>Lab pad options</strong>
<ul>
<li>Cisco Packet Tracer / similar academic simulator (if licensed by your site)</li>
<li>GNS3/EVE-NG with approved images</li>
<li>Physical lab with console cable and isolated VLAN</li>
</ul></div>
""" + _cli_box("First contact (generic IOS-style)", [
    "enable",
    "configure terminal",
    "hostname SW-ACCESS-01",
    "end",
    "show running-config",
]) + """
<section class="sublesson"><h3>Modes</h3>
<p>User mode is limited. Privileged mode (<code>enable</code>) can show deeper status. Configuration mode changes the device—always know how to abandon or save deliberately.</p>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Name and show</div>
<ol>
<li>Set hostname on switch and router to match a diagram.</li>
<li>Capture <code>show running-config</code> (or equivalent) into lab notes.</li>
<li>Draw the topology: PC-A — SW — RTR — PC-B.</li>
</ol></div>
</section>
"""
      },
      {
        "title": "9.2 Switch: VLANs and Access Ports",
        "order": 2,
        "minutes": 110,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Explain why VLANs separate broadcast domains inside one physical switch</li>
<li>Create a VLAN and assign an access port</li>
<li>Verify with show commands</li>
<li>Document VLAN ID, port, and expected user segment</li>
</ul></div>
""" + _cli_box("VLAN and access port (educational pattern)", [
    "configure terminal",
    "vlan 20",
    "name TRAINING-USERS",
    "exit",
    "interface FastEthernet0/2",
    "switchport mode access",
    "switchport access vlan 20",
    "no shutdown",
    "end",
    "show vlan brief",
    "show interfaces status",
]) + """
<section class="sublesson"><h3>Verification mindset</h3>
<p>Configuration without verification is hope. Confirm the port is up, VLAN membership is correct, and the PC received an address in the expected subnet (from the router or DHCP for that VLAN).</p>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Two VLANs</div>
<ol>
<li>Create VLAN 20 (users) and VLAN 30 (printers).</li>
<li>Place PC-A on VLAN 20 and a printer port on VLAN 30.</li>
<li>Show that they do not share a broadcast domain until routing exists.</li>
</ol></div>
</section>
"""
      },
      {
        "title": "9.3 Router: Interfaces and Connected Routes",
        "order": 3,
        "minutes": 110,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Address a router interface and bring it up</li>
<li>Explain connected routes in the routing table</li>
<li>Ping from router to PC and from PC to gateway</li>
<li>Troubleshoot “no route” vs “interface down”</li>
</ul></div>
""" + _cli_box("Router interface (educational pattern)", [
    "configure terminal",
    "interface GigabitEthernet0/0",
    "description LAN-TRAINING",
    "ip address 10.20.0.1 255.255.255.0",
    "no shutdown",
    "end",
    "show ip interface brief",
    "show ip route",
    "ping 10.20.0.10",
]) + """
<section class="sublesson"><h3>Reading the table</h3>
<p>A connected route appears when the interface is up with an address. If the PC cannot ping the gateway, check cable/VLAN/port, PC address/mask, and router interface status before chasing “the internet.”</p>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Gateway proof</div>
<ol>
<li>Set PC-A to 10.20.0.10/24 gateway 10.20.0.1.</li>
<li>Ping gateway; ping from router to PC.</li>
<li>Document both directions (asymmetric failures teach).</li>
</ol></div>
</section>
"""
      },
      {
        "title": "9.4 Inter-VLAN Routing Lab",
        "order": 4,
        "minutes": 100,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Explain why different VLANs need a router (or L3 switch) to communicate</li>
<li>Configure router-on-a-stick subinterfaces <em>or</em> L3 switched SVIs per lab gear</li>
<li>Verify cross-VLAN pings</li>
<li>Write a failure isolation order</li>
</ul></div>
""" + _cli_box("Router-on-a-stick pattern (educational)", [
    "interface GigabitEthernet0/1.20",
    "encapsulation dot1Q 20",
    "ip address 10.20.0.1 255.255.255.0",
    "interface GigabitEthernet0/1.30",
    "encapsulation dot1Q 30",
    "ip address 10.30.0.1 255.255.255.0",
    "end",
    "show ip route",
]) + """
<section class="sublesson"><h3>Isolation order</h3>
<ol>
<li>Same VLAN ping works?</li>
<li>Each PC can ping its own gateway?</li>
<li>Router has both networks in the table?</li>
<li>Trunk allows both VLANs if using trunk links?</li>
</ol>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Users to printers</div>
<p>Make VLAN 20 reach VLAN 30. Capture successful pings and one intentional misconfig you fixed (wrong VLAN on port, wrong mask, subinterface down).</p></div>
</section>
"""
      },
      {
        "title": "9.5 Capstone — New Closet Drop",
        "order": 5,
        "minutes": 90,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Apply switch access port + VLAN + gateway verification as one workflow</li>
<li>Produce a complete lab ticket with CLI evidence</li>
<li>List what you would escalate to network engineering</li>
</ul></div>
<div class="lab-goal"><strong>Scenario:</strong> A new wall drop must land on VLAN 20 with DHCP from the training scope. PC gets no address.</div>
<section class="sublesson"><h3>Ordered checks</h3>
<ol>
<li>Link lights / <code>show interfaces status</code></li>
<li>Access VLAN on the switch port</li>
<li>Trunk to the router if required</li>
<li>Router subinterface/SVI up with correct subnet</li>
<li>DHCP pool/relay (if used) and PC settings</li>
</ol>
<div class="lab-panel"><div class="lab-title"><span>LAB</span> Deliver the evidence pack</div>
<p>Commands, outputs, root cause, fix, verification ping and “user can open intranet.”</p></div>
</section>
"""
      },
      {
        "title": "9.6 Hostname and write memory — make it survive a reload",
        "order": 6,
        "minutes": 40,
        "html": _LAB_CSS + """
<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Set a hostname that matches the closet label</li>
<li>Save with write memory or copy running-config startup-config</li>
<li>Explain why an unsaved config disappears after a power blip</li>
</ul></div>
<div class="plain-english"><h4>In plain English</h4>
<p>Running-config is what the box is doing now. Startup-config is what it will do after a reload. If you VLAN a port and walk away without saving, the next breaker trip undoes your work and the ticket reopens.</p></div>
""" + _cli_box("Save path", ["enable", "configure terminal", "hostname SW-ACCESS-01", "end", "write memory"]) + """
<section class="sublesson"><h3>Check</h3>
<p>After save, <code>show running-config</code> and <code>show startup-config</code> should both show the new hostname. Use the live lab “Hostname and save” on switch and router.</p></section>
"""
      },
    ],
  }
]
