"""CIWT Chapter 5 — Client networking for support technicians.
Proprietary schoolhouse material. Teach from the screen. Labs are the Windows isolation set.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER5 = {
    "title": "Chapter 5 — Networking for Support Technicians",
    "order": 5,
    "minutes": 220,
    "overview": (
        "Address, name, and gateway as separate fault domains. Read ipconfig, prove IP vs name, "
        "then run a full client triage ticket. You are not configuring a core switch in this chapter."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 45,
            "title": "5.1 IPv4 Addressing and Private Ranges",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Read IPv4, mask, gateway, and DNS from <code>ipconfig /all</code> as ticket evidence</li>
<li>Recognize a missing lease (APIPA 169.254) versus a real address</li>
<li>Say what “private range” means on a training bench without treating it as the internet</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Project a canned ipconfig. Circle hostname, IPv4, mask, gateway, DNS. Then launch win-ipconfig. Nobody skips to ping yet.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.6 inventory. Same habit: collect identity before you change the thing.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>An address is how this PC is known on this LAN. The gateway is the door off the LAN. DNS turns names into addresses. If you mix those three up, you will “fix DNS” on a box that never got a lease.</p></div>
<div class="live-demo"><h4>Lab this lesson — win-ipconfig</h4>
<p>Run <code>hostname</code> then <code>ipconfig /all</code>. Write four lines into a note: name, IPv4, gateway, DNS. That note is evidence, not a novel.</p></div>

<section id="s1" class="sublesson"><h3>1. What you must be able to point to</h3>
<table class="port-table">
<tr><th>Field</th><th>Means</th></tr>
<tr><td>IPv4</td><td>This host on this LAN</td></tr>
<tr><td>Mask</td><td>How large that LAN is</td></tr>
<tr><td>Default gateway</td><td>First hop off the LAN</td></tr>
<tr><td>DNS servers</td><td>Who answers names</td></tr>
<tr><td>DHCP enabled</td><td>Whether the lease came from a server</td></tr>
</table>
<p>169.254.x.x means no usable lease. Do not start a DNS lecture. Renew or look at the link.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>ipconfig shows 169.254.27.8. Next idea?</summary><p>No lease. Link or DHCP, not “the website is down.”</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "5.2 Ports, Protocols, and Services",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Name common ports as ticket language: 53 DNS, 80/443 web, 25/587 mail submit, 3389 RDP</li>
<li>Do not disable the firewall to “make the app work”</li>
<li>Tie a failing app to a service name, not to “the internet”</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Five ports on the board. Each trainee maps one user sentence to a port. Firewall off is a 1.4 no.</p></div>
<div class="build-on"><strong>Builds on:</strong> 5.1 you can read an address. A port is which door on that address.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>The PC can ping and still fail mail. Ping proves a path. It does not prove the mail door is open.</p></div>

<section id="s1" class="sublesson"><h3>1. Ports you will actually say</h3>
<table class="port-table">
<tr><th>Port</th><th>Use</th></tr>
<tr><td>53</td><td>DNS</td></tr>
<tr><td>80 / 443</td><td>Web</td></tr>
<tr><td>25 / 587</td><td>Mail transfer / submit</td></tr>
<tr><td>3389</td><td>RDP — treat as sensitive</td></tr>
</table>
<p>You do not memorize every port. You memorize the ones that change your first test.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Firewall</h3>
<p>Read the profile (later Block 3 / w11-firewall). Do not turn the profile off for a game launcher. Open a request or use the approved app (1.4).</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Ping to the mail server works. Outlook still loops.</summary><p>Path is up. Name, account, or mail port/service next — not “replace the NIC.”</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 50,
            "title": "5.3 Connectivity Isolation Order",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Use a fixed order: link / lease → ping IP → ping name → DNS lookup</li>
<li>Prove a name failure separately from an IP failure</li>
<li>Write each test as action → result</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 50 minutes</h4>
<p>Order on the board. Demo win-dns-break: ping IP works, ping name fails, nslookup, flush. Trainees run both labs under this lesson.</p></div>
<div class="build-on"><strong>Builds on:</strong> 5.1 fields and 2.5 “do not skip a layer.”</div>
<div class="plain-english"><h4>In plain English</h4>
<p>If the number works and the name does not, you have a name problem. If the number does not work, stop talking about DNS.</p></div>
<div class="live-demo"><h4>Labs this lesson</h4>
<ol>
<li><strong>win-ipconfig</strong> — collect the four lines</li>
<li><strong>win-dns-break</strong> — ping IP, ping name, nslookup, flushdns</li>
</ol>
<p>Same facts also live in Settings → Ethernet (gui-ethernet) if you need the user-facing view.</p></div>

<section id="s1" class="sublesson"><h3>1. Order</h3>
<ol>
<li>Link lights / cable / Wi-Fi association</li>
<li>Lease — ipconfig, not 169.254</li>
<li>Ping gateway IP</li>
<li>Ping a known-good IP on the LAN</li>
<li>Ping the name</li>
<li>nslookup / flush only after the IP tests</li>
</ol>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Flushing DNS on an APIPA box</li>
<li>Writing “ping failed” with no target</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Ping 10.20.30.50 works. Ping app.training.local fails.</summary><p>Name path. nslookup next. Not a new NIC.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "5.4 SOHO Wireless Hardening",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Read whether the client is associated and has a lease</li>
<li>Change a default admin password and guest SSID only under shop change rules</li>
<li>Do not “hide SSID” as a security plan</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>w11-wlan if the bench has it. Otherwise treat this as a change-awareness lesson: home-router myths vs ticket facts.</p></div>
<div class="build-on"><strong>Builds on:</strong> 5.3 isolation and 1.3 change awareness.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Wireless fails the same way wired does, plus association. Hiding the name does not hide the radio. A default admin password on the AP is the real hole.</p></div>
<div class="live-demo"><h4>Lab this lesson — w11-wlan</h4>
<p>Read the WLAN interface state. Associated or not. Address or APIPA. Write those two lines. Do not change shop SSID in class.</p></div>

<section id="s1" class="sublesson"><h3>1. Client first</h3>
<p>Airplane mode, correct SSID, lease, then isolation order from 5.3. Wrong SSID looks like “the internet is down.”</p>
</section>

<section id="s2" class="sublesson"><h3>2. AP changes are changes</h3>
<p>Admin password, guest network, firmware on a shared AP: change process. Not a lunch click.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Hide SSID to secure the shop?</summary><p>No. Fix admin password, guest isolation, and who is allowed on the LAN.</p></details>
</div>'''
        },
        {
            "order": 5,
            "minutes": 55,
            "title": "5.5 Capstone — Client Network Ticket",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Run a full client triage: identity → IP → name → DNS → renew if needed</li>
<li>Write Block 1 notes with action → result pairs</li>
<li>Stop short of disabling the firewall or guessing a core-router fault</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 55 minutes</h4>
<p>Trainees run win-full-triage to completion. Peer-read the note. Anyone who skipped ping-IP and jumped to flushdns reruns.</p></div>
<div class="build-on"><strong>Builds on:</strong> 5.1–5.4 plus 1.5 intake.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>This is the ticket you will actually get: “the internet is down.” You already know that sentence is not a diagnosis.</p></div>
<div class="live-demo"><h4>Labs this lesson</h4>
<ol>
<li><strong>win-full-triage</strong> — identity, ping IP, ping name, nslookup, flush, release/renew as the lab requires</li>
<li><strong>gui-ethernet</strong> — same facts in Settings if you must show the user</li>
</ol></div>

<section id="s1" class="sublesson"><h3>Note bar</h3>
<p>Example: “CIWT-W11-07. ipconfig 10.20.30.47 gw 10.20.30.1. ping 10.20.30.50 4/4. ping app.training.local fail. nslookup NXDOMAIN. flushed cache — still fail. Escalate to DNS owner for app.training.local.”</p>
</section>

<section id="s2" class="sublesson"><h3>Pass bar</h3>
<p>Submit the triage lab. Your note would survive 0200. You did not turn the firewall off.</p>
</section>'''
        },
    ],
}
