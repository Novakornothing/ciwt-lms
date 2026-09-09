"""CIWT Chapter 7 — Troubleshooting method.
Proprietary schoolhouse material. This chapter names the order you already used in 1–6.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER7 = {
    "title": "Chapter 7 — Troubleshooting Methodology",
    "order": 7,
    "minutes": 160,
    "overview": (
        "One process for every ticket: identify, test a theory, plan, change one thing, verify, document. "
        "You already did this in Blocks 1–5. This chapter makes the order explicit."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 40,
            "title": "7.1 Structured Process",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>List the order: identify → probable cause → test → plan → change one thing → verify → document</li>
<li>Refuse to skip identify because the user already “knows it is DNS”</li>
<li>Map this order onto Lab ticket-intake and win-full-triage</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Write the seven words. Have the room map ticket-intake (identify) and win-full-triage (test) onto them. No new CLI.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.5 intake and 5.5 triage. Same work, named.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Guessing first is how you replace a NIC on an APIPA box. The process is there so you do not skip a cheap layer.</p></div>
<div class="live-demo"><h4>Desk drill</h4>
<p>Take “the internet is down.” Identify: one user or many? Then Chapter 5 order. Do not start at flushdns.</p></div>

<section id="s1" class="sublesson"><h3>1. The order</h3>
<ol>
<li>Identify — who, what outcome, how many, safety stop</li>
<li>Probable cause — a short list, not a novel</li>
<li>Test — cheapest test that can kill a theory</li>
<li>Plan — including how you undo it</li>
<li>Change one thing</li>
<li>Verify with the user outcome, not only a green icon</li>
<li>Document — action → result</li>
</ol>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>User says “it’s DNS.” You skip ipconfig?</summary><p>No. Identify and a lease/IP test still come first.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 40,
            "title": "7.2 Fault Domains",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Name the domain before the part: safety, power, POST, display, OS, address, name, vendor/SaaS</li>
<li>Use one vs many to pick the domain</li>
<li>Stop crossing domains (do not format a disk because mail SaaS is down)</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Eight domain names on the board. Three tickets. Class points at one domain each.</p></div>
<div class="build-on"><strong>Builds on:</strong> 2.5 POST order, 3.4 display, 5.3 name vs IP, 6.2 SaaS.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>A fault domain is “which neighborhood is on fire.” You work inside that neighborhood until evidence moves you.</p></div>

<section id="s1" class="sublesson"><h3>1. Domains you already know</h3>
<table class="port-table">
<tr><th>Domain</th><th>First tests</th></tr>
<tr><td>Safety</td><td>Shock, heat, smell — stop</td></tr>
<tr><td>Power / POST</td><td>Wall, cables, beep/LED</td></tr>
<tr><td>Display</td><td>After POST OK — cable/input</td></tr>
<tr><td>OS / disk</td><td>About, list disk</td></tr>
<tr><td>Address</td><td>ipconfig, not 169.254</td></tr>
<tr><td>Name</td><td>Ping IP works, name fails</td></tr>
<tr><td>Vendor / SaaS</td><td>LAN fine, whole tenant down</td></tr>
</table>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>Whole tenant mail down, ping to 8.8.8.8 works.</summary><p>Vendor/SaaS domain. Not a local disk.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 40,
            "title": "7.3 Verification and Handoff",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Verify the outcome the user called about</li>
<li>Hand off with tests and results, not “please fix”</li>
<li>Keep guesses labeled</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Rewrite a bad handoff on the board. Then each trainee writes one handoff for the badge-heat story from 1.5.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.3 notes and 1.4 channels.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Verified means they can send the report, not that Task Manager looks calm. A handoff that omits tests sends the next person to zero.</p></div>
<div class="live-demo"><h4>Lab language</h4>
<p><strong>ticket-intake</strong> <code>note</code> is the handoff drill. Symptom, observation, next person.</p></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Good last line?</summary><p>A person or a command, not “look into it.”</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "7.4 Capstone Drills",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Run one hardware-shaped ticket and one network-shaped ticket with the same process</li>
<li>Name the fault domain before you touch a lab</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Two drills: MEM beep (stay in POST — hw-board). Name fail after IP works (win-dns-break or full triage). Anyone who opens diskpart on the mail-SaaS story fails the pass bar.</p></div>
<div class="live-demo"><h4>Labs</h4>
<ol>
<li><strong>ticket-intake</strong> — identify + note</li>
<li><strong>win-full-triage</strong> — test order on a client path</li>
</ol></div>
<div class="check-box"><h4>Pass bar</h4>
<p>You can point at the domain first. You change one thing. Your note would survive 0200.</p>
</div>'''
        },
    ],
}
