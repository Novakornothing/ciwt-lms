"""CIWT Chapter 4 — Laptops, mobile accounts, print path.
Proprietary schoolhouse material. Teach from the screen.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER4 = {
    "title": "Chapter 4 — Mobile Devices & Printing",
    "order": 4,
    "minutes": 180,
    "overview": (
        "Portable hardware, accounts on a phone you do not own, and a print path you isolate "
        "before you replace a printer. Same Block 1 ticket habits. No open-chassis work on a live laptop."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 45,
            "title": "4.1 Laptop FRUs and Service Habits",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Name common laptop FRUs: battery, SSD/M.2, RAM if socketed, screen/inverter path, AC adapter</li>
<li>Power off, disconnect AC, remove the external battery if the model allows, then wait — before screws</li>
<li>Match parts to the service tag, not to “a 15-inch Dell”</li>
<li>Stop if the chassis is swollen, hot, or the user reported a shock</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Show one training laptop and the service manual page if you have it. Point: AC brick rating, battery release, M.2 under a door vs glued chassis. No one pries a sealed battery in class.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.2 safety and 3.1 storage. A laptop is the same map in a smaller box with fewer user-replaceable parts.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>FRU means the part your shop will swap. Many modern laptops glue the battery and hide the disk. If the manual says “internal battery, not field replaceable,” you do not make it field replaceable with a spudger and hope.</p></div>
<div class="live-demo"><h4>Desk drill</h4>
<p>On the training laptop: unplug AC, hold power 10 seconds, then say whether this model has an external battery. If you cannot find the service tag, you are not ordering parts yet.</p></div>

<section id="s1" class="sublesson"><h3>1. Power first</h3>
<p>AC adapter rating must match or exceed the brick the chassis expects. A 65 W brick on a 130 W chassis will charge slowly or throttle and look like “slow CPU.” Write the numbers off both labels before you blame Windows.</p>
</section>

<section id="s2" class="sublesson"><h3>2. What you may open</h3>
<p>Door or bottom plate with a service guide: M.2, sometimes RAM. Sealed battery: shop procedure or vendor depot. Swollen battery: stop, do not sit on it, do not toss it in household trash.</p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Ordering “the 15-inch screen” without the panel code</li>
<li>Prying a swollen pack</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>User says the laptop is hot and the trackpad is raised.</summary><p>Suspected swollen battery. Incident-level stop. Do not keep using it. Follow shop battery procedure.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "4.2 Mobile Networking and Accounts",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Separate Wi-Fi, cellular, and VPN failures on a phone or tablet</li>
<li>Treat a work profile / MDM account as shop property, not the user’s personal Apple/Google login</li>
<li>Read the signed-in Windows account on a shared bench PC before you change it</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Demo gui-accounts on the Windows bench. Say out loud: this is the PC account, not the phone MDM. Do not factory-reset a managed phone in class.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 identity and 2.6 inventory. Same rule: know whose account you are touching.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>“The phone cannot get mail” might be Wi-Fi, cellular data, VPN, or the work profile wiped itself. Resetting the whole phone because mail is late is how you wipe someone else’s photos and violate policy.</p></div>
<div class="live-demo"><h4>Lab this lesson — gui-accounts</h4>
<p>Open Settings → Accounts. Read who is signed in. That is the habit you take to a phone: which profile is failing, work or personal.</p></div>

<section id="s1" class="sublesson"><h3>1. Three radios</h3>
<p>Wi-Fi: association + DHCP + DNS, same isolation as Chapter 5. Cellular: airplane mode off, data enabled, SIM/eSIM present. VPN: if work mail only fails on VPN, that is a VPN or connector problem, not “the phone.”</p>
</section>

<section id="s2" class="sublesson"><h3>2. MDM</h3>
<p>Managed devices can be locked, wiped, or blocked from installing apps. You do not sidestep MDM to “just install Outlook.” Open a request to the owner of that enrollment.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Mail works on cellular, fails on building Wi-Fi.</summary><p>Not a broken phone radio. Isolate the WLAN / captive portal / proxy. Do not factory reset.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 45,
            "title": "4.3 Print Path Troubleshooting",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Walk the print path: app → spooler → queue / driver → network or USB → device</li>
<li>Decide if one user, one PC, or the whole floor is down</li>
<li>Do not replace a printer because one workstation has a stale driver</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Draw the path on the board. Three tickets: one user, one PC, whole floor. Class names the first test for each. No live printer required.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 impact (one vs many) and 3.4 “cheap layer first.”</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Printing is a chain. Breaks at different links look the same to the user (“it won’t print”). Your job is to find the link, not to wheel in a new device on the first call.</p></div>
<div class="live-demo"><h4>Desk drill</h4>
<p>For each story, say first test:<br>
A. One user, same PC prints from Word, not from the browser.<br>
B. One PC, every app fails, next desk prints fine.<br>
C. Whole floor queued, printer panel says paper out — or offline on the server.</p></div>

<section id="s1" class="sublesson"><h3>1. The path</h3>
<ol>
<li>Application</li>
<li>Spooler / local queue</li>
<li>Driver and port</li>
<li>USB or network path</li>
<li>Device panel (paper, toner, offline, jam)</li>
</ol>
<p>One user / one app → start at the app and driver. Whole floor → start at the device and the print server, not at Office settings.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Notes</h3>
<p>Write: who can print, from which PC, error text, queue name, and whether the panel is alive. “Printer broken” is Ticket A from Chapter 1.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Three people in line, jam icon on the panel.</summary><p>Device. Clear the path or swap trays. Do not rebuild a driver on the first PC in line.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 50,
            "title": "4.4 Capstone — Portable Intake",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Take a laptop or print ticket using Block 1 structure</li>
<li>Stop for swollen battery / shock / hot brick</li>
<li>Leave a note that says which FRU or which print-path link you will touch next</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 50 minutes</h4>
<p>Two stories on paper. 1) Swollen pack. 2) Floor printer offline. Trainees write classify / impact / escalate / note. Optional: ticket-intake if they try to force a hardware command onto a badge-heat story — remind them that lab is Block 1 language.</p></div>
<div class="build-on"><strong>Builds on:</strong> 4.1–4.3 plus 1.5 intake.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Portable gear fails in hallways. You still classify, you still write, you still stop for safety.</p></div>
<div class="live-demo"><h4>Worked notes</h4>
<p><strong>Swollen pack:</strong> incident or at least stop-work. Impact 1 unless it is in a bag on a plane of devices. Escalate to the battery procedure owner. Note: trackpad raised, do not charge, quarantined.</p>
<p><strong>Floor printer:</strong> break/fix unless it is the only device for a watch (impact many). Check panel first. Note: queue name, panel state, who can still print.</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Peer can tell from your note whether to order a panel, pull a driver, or stop for a battery. You did not pry a sealed pack.</p>
</div>'''
        },
    ],
}
