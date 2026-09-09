"""CIWT Chapter 12 — Operational procedures and course capstone habits.
Proprietary schoolhouse material.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
</style>
'''


CHAPTER12 = {
    "title": "Chapter 12 — Operational Procedures & Capstone Habits",
    "order": 12,
    "minutes": 160,
    "overview": (
        "Change control, privacy, recovery awareness, then one integrated ticket using everything in 1–11."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 40,
            "title": "12.1 Change Control and Checklists",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Name a change vs a repair with a shop example</li>
<li>Use a short checklist before a production change</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Replay 1.3. Firmware, DNS, image, AP password = changes. Reseat RAM = repair, still documented.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.3 and 5.4 AP clicks.</div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Adding a DNS record after 1500 against policy?</summary><p>Change. Do not “just add it.”</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "12.2 Privacy and Policy",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Keep PII and passwords off hallway talk and tickets</li>
<li>Refuse unsafe access without becoming the enemy</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Replay 1.4. gui-accounts as the “whose data is this” drill.</p></div>
<div class="live-demo"><h4>Lab</h4>
<p><strong>gui-accounts</strong>.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Password in the ticket to “help the next guy”?</summary><p>No.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 40,
            "title": "12.3 Recovery Awareness",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Say backup ≠ RAID ≠ snapshot</li>
<li>Ask last-backup time before a destructive step</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>3.2 and 6.3 in one slide. No wipe lab.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Ransomware on the share. RAID 5 saves them?</summary><p>No. Restore from backup.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "12.4 Integrated Capstone",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Run identify → domain → one lab → note</li>
<li>Pick hardware, network, or SaaS without mixing them</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Give two stories. 1) MEM beep. 2) Tenant mail down. First uses hw-board memory. Second uses ticket-intake + no local reimage.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>ticket-intake</strong> and <strong>win-full-triage</strong> or <strong>hw-board</strong> — pick the domain first, then the lab.</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Peer can tell the domain from the note. Safety stops held.</p>
</div>'''
        },
    ],
}
