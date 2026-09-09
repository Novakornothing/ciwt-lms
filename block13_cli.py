"""CIWT Chapter 13 — Windows CLI / GUI lab track.
Proprietary schoolhouse material. This chapter is the live-lab gym for skills already taught.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
</style>
'''


CHAPTER13 = {
    "title": "Chapter 13 — Windows CLI & VM Lab Track",
    "order": 13,
    "minutes": 200,
    "overview": (
        "Reps. Every command here was taught in Chapters 2, 5, and 8. Pass bar is submit on the labs, "
        "not a new theory chapter."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 30,
            "title": "13.1 Lab VM Setup and Safety",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Inventory the lab VM before you change it</li>
<li>Treat this guest as shop property</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 30 minutes</h4>
<p>gui-about + w11-inventory. No clean.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>w11-inventory</strong>, <strong>gui-about</strong>.</p></div>'''
        },
        {
            "order": 2,
            "minutes": 35,
            "title": "13.2 Command Prompt Foundations",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Collect hostname and ipconfig /all as ticket evidence</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 35 minutes</h4>
<p>Replay 5.1. Four lines in the note.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>win-ipconfig</strong>, <strong>gui-ethernet</strong>, <strong>w11-powershell-net</strong>.</p></div>'''
        },
        {
            "order": 3,
            "minutes": 35,
            "title": "13.3 Network Reset and Adapter Labs",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Release/renew a lease and recycle the adapter from Settings</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 35 minutes</h4>
<p>win-dhcp-renew + gui-renew. Not a reboot substitute for thinking.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>win-dhcp-renew</strong>, <strong>gui-renew</strong>.</p></div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "13.4 Capstone — Broken Name Resolution Ticket",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Prove IP vs name and finish full triage</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Same pass bar as 5.5. No firewall off.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>win-dns-break</strong>, <strong>win-full-triage</strong>.</p></div>'''
        },
        {
            "order": 5,
            "minutes": 30,
            "title": "13.5 Windows 11 Settings paths that match the live labs",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Find About, Ethernet, Update, Accounts, Services in Settings</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 30 minutes</h4>
<p>GUI gym. Click the labs in order.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>gui-about</strong>, <strong>gui-ethernet</strong>, <strong>gui-renew</strong>, <strong>gui-services</strong>, <strong>gui-update</strong>, <strong>gui-accounts</strong>.</p></div>'''
        },
        {
            "order": 6,
            "minutes": 30,
            "title": "13.6 Processes, netsh, and when not to reboot",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>List processes before a reboot</li>
<li>Read netsh facts as another view of the same lease</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 30 minutes</h4>
<p>Replay 8.3. Reboot is a change.</p></div>
<div class="live-demo"><h4>Labs</h4>
<p><strong>w11-processes</strong>, <strong>w11-netsh</strong>.</p></div>
<div class="check-box"><h4>Pass bar</h4>
<p>Chapter 13 is done when the mapped labs submit and the notes still look like Block 1.</p>
</div>'''
        },
    ],
}
