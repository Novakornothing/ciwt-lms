"""CIWT Chapter 10 — Endpoint security for support.
Proprietary schoolhouse material. Attention/Helix is not assessment. This chapter is policy + ticket.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER10 = {
    "title": "Chapter 10 — Endpoint Security",
    "order": 10,
    "minutes": 160,
    "overview": (
        "Physical and account controls, malware as an incident, hygiene that does not disable Defender. "
        "You isolate and escalate. You do not become the incident-response team in this chapter."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 40,
            "title": "10.1 Physical and Logical Controls",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Name badge, screen lock, and least privilege as daily controls</li>
<li>Read who is signed in before you change an account</li>
<li>Read firewall profile — do not turn it off</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>gui-accounts + w11-firewall. Screen lock and unknown USB are policy, not a lab command.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.4 privacy and 8.3 firewall stays on.</div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>gui-accounts</strong> — who is signed in.<br>
<strong>w11-firewall</strong> — read profile only.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Shared admin password on a monitor?</summary><p>No. Unaccountable privilege. 1.4 still applies.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "10.2 Malware Response",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Treat active malware or “mail sent as me” as incident</li>
<li>Contain: isolate the host per shop process, do not power-cycle as your only move</li>
<li>Write facts, not a novel about the user’s habits</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Classify incident. Do not run random “cleaners.” ticket-intake for the note. Escalate to the IR owner.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 incident label and 7.2 fault domains.</div>
<div class="live-demo"><h4>Lab</h4>
<p><strong>ticket-intake</strong> — if the sentence is many users or security, you already know classify incident.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Disable Defender so the “cleaner” can run?</summary><p>No. That is how you help the malware.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 40,
            "title": "10.3 Support Hygiene",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Confirm Defender / security service is Running</li>
<li>Do not paste passwords into tickets or chat</li>
<li>Patch state is part of hygiene — read Update, do not skip it</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>gui-services / Defender + gui-update. Same baseline as 8.2–8.3 with a security reason attached.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>gui-services</strong> and <strong>gui-update</strong>.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Where does a password go?</summary><p>Not the ticket. Not the projector. Reset through the approved tool.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "10.4 Capstone — Phishing Follow-Up",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>User reports a phish they did not open: record, do not shame, confirm no credentials entered</li>
<li>If they entered a password: incident + approved reset path, not a hallway lecture only</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Two stories. A: not opened. B: password typed. ticket-intake for B-quality notes. No live malware.</p></div>
<div class="live-demo"><h4>Lab</h4>
<p><strong>ticket-intake</strong> plus <strong>gui-accounts</strong> if you must show whose account you would reset.</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Note is factual. No password in the ticket. Defender left on.</p>
</div>'''
        },
    ],
}
