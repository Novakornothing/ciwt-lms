"""CIWT Chapter 6 — Virtualization and cloud for support techs.
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


CHAPTER6 = {
    "title": "Chapter 6 — Virtualization & Cloud Concepts",
    "order": 6,
    "minutes": 160,
    "overview": (
        "Host versus guest, what a snapshot is for, and which cloud model you are actually calling. "
        "You will not stand up a datacenter in this chapter. You will stop treating a VM like a mystery PC."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 40,
            "title": "6.1 Hypervisors and VMs",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Say host vs guest in one sentence</li>
<li>Know that this training PC may already be a guest (CIWT-W11-07)</li>
<li>Do not snapshot or delete a VM that is not yours</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Point at the bench: the Windows you type in is the guest. The hypervisor (if present) is someone else’s job unless shop policy says otherwise. Demo gui-about + w11-inventory — device name and RAM the guest sees.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.6 inventory. Same facts, new meaning: this box may not be the metal.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>A VM is a PC made of files. It feels like hardware. The host is the machine (or cluster) that holds those files. If the host is sick, every guest on it looks sick.</p></div>
<div class="live-demo"><h4>Labs this lesson</h4>
<p><strong>gui-about</strong> and <strong>w11-inventory</strong> — read name, edition, RAM the guest reports. Write “guest identity” in the note. You are not opening Hyper-V Manager in this course unless the shop image has it and the instructor says so.</p></div>

<section id="s1" class="sublesson"><h3>1. Two machines in one ticket</h3>
<p>User: “My VM is slow.” Ask: is the guest out of RAM/disk, or is the host oversubscribed? Inventory the guest first (Chapter 2.6). If the guest looks fine and the whole farm is slow, escalate to the host owner. Do not “optimize” a host you do not own.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Type 1 vs type 2 — only what you need</h3>
<p>Type 1 sits on the metal (shop hypervisors). Type 2 sits on a desktop OS (a laptop running one lab VM). For tickets: who owns the host, and may you touch it?</p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Reimaging the guest when the host datastore is full</li>
<li>Treating “VM” as a brand instead of a role</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Five guests on one host all “lose the network.” First thought?</summary><p>Host or shared virtual switch / uplink — not five separate NICs to replace.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "6.2 Cloud Service Models",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Tell IaaS, PaaS, and SaaS apart by what you are allowed to touch</li>
<li>Know when a “cloud outage” is a vendor ticket, not a local reimage</li>
<li>Do not paste tenant admin passwords into a ticket</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Three rows on the board: mail SaaS, a shop VM in someone else’s datacenter (IaaS), a database platform (PaaS). Each trainee names who resets what.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 who owns the work and 4.2 MDM — same idea, bigger vendor.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>SaaS: you use the app (mail in a browser). IaaS: you still own the guest OS. PaaS: you own the app, not the OS. If you treat SaaS like a local PC you will reimage a laptop that is not the problem.</p></div>

<section id="s1" class="sublesson"><h3>1. What you can touch</h3>
<table class="port-table">
<tr><th>Model</th><th>You usually touch</th><th>You do not</th></tr>
<tr><td>SaaS</td><td>Account, license, client</td><td>Vendor servers</td></tr>
<tr><td>IaaS</td><td>Guest OS, like Chapter 2–5</td><td>The vendor’s metal unless they say so</td></tr>
<tr><td>PaaS</td><td>App settings / deploy path</td><td>The platform OS</td></tr>
</table>
</section>

<section id="s2" class="sublesson"><h3>2. Ticket habit</h3>
<p>Write the tenant or subscription name, the error text, and whether other users in the tenant fail. Escalate to the owner of that tenant. Do not guess a DNS “fix” on a working LAN because Outlook 365 is yellow.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Whole tenant cannot open mail; your ipconfig is fine.</summary><p>SaaS / vendor path. Do not reimage the first laptop.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 40,
            "title": "6.3 Virtual Networking and Snapshots",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Treat a snapshot as a change with a rollback story — not a backup</li>
<li>Know a guest can be on a virtual switch that is not the jack in the wall</li>
<li>Do not leave snapshots forever</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Snapshot ≠ backup (same punch as RAID ≠ backup). Virtual NIC can be disconnected in the hypervisor while the guest “has a NIC.” No live snapshot lab — judgment + Chapter 5 isolation inside the guest.</p></div>
<div class="build-on"><strong>Builds on:</strong> 3.2 RAID is not backup, and 5.3 isolation inside the guest.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>A snapshot is a bookmark so you can try something and go back. It is not a second copy in another building. A virtual cable can be unplugged in software while the physical drop is fine.</p></div>
<div class="live-demo"><h4>If the guest has “no network”</h4>
<p>Run the Chapter 5 order <em>inside</em> the guest first (<strong>win-ipconfig</strong>). If the guest shows no adapter or APIPA and the host network is up, the next person is the hypervisor owner — disconnected vNIC, wrong port group, or host uplink.</p></div>

<section id="s1" class="sublesson"><h3>1. Snapshots</h3>
<p>Take one before a change you can name. Revert only with a ticket. Delete or consolidate when the change is done. A chain of week-old snapshots fills the datastore and makes every guest slow.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Snapshot instead of backup before ransomware?</summary><p>No. Snapshot lives next to the live disks. Backup is a second copy you can restore.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "6.4 Capstone — Slow VM",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Inventory the guest before you blame the host</li>
<li>Write a note that separates guest facts from host guesses</li>
<li>Escalate the host only with evidence</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Story: “CIWT-W11-07 is slow since the snapshot Tuesday.” Trainees run inventory, write guest facts, then say what they would ask the host owner. No one deletes a snapshot in class.</p></div>
<div class="build-on"><strong>Builds on:</strong> 6.1–6.3 plus 2.6 and 1.3.</div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>w11-inventory</strong> and <strong>gui-about</strong>. Note: name, RAM the guest sees, disk list if you already know 2.6. Guess line labeled guess: “snapshot chain on host?”</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Peer can tell guest facts from host ask. You did not delete a snapshot you do not own.</p>
</div>'''
        },
    ],
}
