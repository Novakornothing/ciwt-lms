"""CIWT Block 1 / Chapter 1 — Workplace, tickets, and safety.
Proprietary schoolhouse material. Not official Navy courseware.
Teach this from the screen: talk the page, run the desk drill, then Lab ticket-intake.
"""

_NOTE = '''<style>
.instructor-note{border-left:4px solid var(--accent,#3ec7ff);background:color-mix(in srgb,var(--accent,#3ec7ff) 10%,transparent);padding:.75rem 1rem;margin:1rem 0;border-radius:0 8px 8px 0}
.instructor-note h4{margin:0 0 .4rem;font-size:.95rem}
.check-box{border:1px solid var(--surface-4,#c9d6e8);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
.check-box h4{margin:0 0 .5rem}
.miss-box{background:var(--warning-bg,#fff4df);border-radius:10px;padding:.85rem 1rem;margin:1rem 0}
</style>
'''


CHAPTER1 = {
    "title": "Chapter 1 — Professional Foundations & Workplace Safety",
    "order": 1,
    "minutes": 240,
    "overview": (
        "Block 1 (weeks 1–2). Classify work, stop when it is unsafe, write a ticket another watch "
        "can use, then prove it in Lab ticket-intake. Do not open a chassis in this chapter."
    ),
    "lessons": [
        {
            "order": 1,
            "minutes": 50,
            "title": "1.1 The Support Technician Role",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>State what a support technician is paid to restore, in one sentence a lead would accept</li>
<li>Sort a contact into break/fix, service request, or incident and say what changes when the label changes</li>
<li>Verify identity before changing an account or sharing data</li>
<li>Hand a problem off with facts the next technician can act on without calling you back</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 50 minutes</h4>
<p>Talk sections 1–4 (20 min). Desk drill table out loud with three volunteers (15 min). Preview <code>show ticket</code> / <code>classify</code> only — do not finish the lab until 1.5. Common miss: calling everything “break/fix.”</p></div>
<div class="build-on"><strong>Where this fits:</strong> Block 1 / Chapter 1. Hardware and CLI come after. If you cannot triage and write, those tools help you break things faster.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Users do not bring you “Layer 3.” They bring you outcomes: the report will not send, the floor printer is dead, mail looks wrong. Restore the outcome without a second outage, leave a record, and tell the truth about what you know.</p></div>
<div class="live-demo"><h4>Lab on this chapter — ticket-intake</h4>
<p>The live lab sits under this lesson. You will open a raw user sentence, classify it, set impact, decide escalate or keep, write a note, and submit. Finish the desk drills below before you hunt for the “right” command.</p></div>

<section id="s1" class="sublesson"><h3>1. What the role actually delivers</h3>
<p>On almost every contact you do four things:</p>
<ol>
<li><strong>Restore service</strong> — the required workflow works again (login, print, send, VPN, open the file).</li>
<li><strong>Reduce risk</strong> — you do not turn off security “to make it work,” share admin passwords, or leave an account unlocked for convenience.</li>
<li><strong>Leave a trail</strong> — notes the next watch can trust at 0200 without you on the phone.</li>
<li><strong>Communicate</strong> — the user and your lead know status, next step, and what you need from them.</li>
</ol>
<p>“The internet is down” might be DNS, captive portal, proxy, VPN, Wi-Fi, or one blocked site. First job: turn vague words into a testable claim.</p>
<div class="analogy-box"><div class="analogy-label">Analogy · ER triage</div>
<p>Arrival order is not treatment order. One laptop offline is real work. Malware across a wing is more important because impact multiplies. Always ask: how many people, and how bad if we wait.</p></div>
</section>

<section id="s2" class="sublesson"><h3>2. Three kinds of work</h3>
<p>The label changes approvals, clocks, and who must be told.</p>
<table class="port-table">
<tr><th>Type</th><th>Meaning</th><th>What you do</th></tr>
<tr><td><strong>Break/fix</strong></td><td>Something that used to work stopped</td><td>Troubleshoot, repair, verify with the user</td></tr>
<tr><td><strong>Service request</strong></td><td>Something new is asked for</td><td>Check entitlement, get approval if required, fulfill</td></tr>
<tr><td><strong>Incident</strong></td><td>Many users, a major service, or security</td><td>Contain, coordinate, communicate; page a specialist if needed</td></tr>
</table>
<p><strong>SLA</strong> is the published response/resolve target. It is not permission to close before the user can work.</p>
<p>Classify before you touch a keyboard:</p>
<ul>
<li>“I need the budget share for the first time.” → service request</li>
<li>“Outlook worked yesterday; today it loops on password.” → break/fix</li>
<li>“Half the building cannot badge in.” → incident</li>
<li>“Someone sent mail as me.” → incident (security) until proven otherwise</li>
</ul>
<p>Lab commands: <code>classify break-fix</code>, <code>classify request</code>, or <code>classify incident</code>. If two feel true, pick the higher risk (incident beats break/fix).</p>
</section>

<section id="s3" class="sublesson"><h3>3. Impact and identity</h3>
<p>Impact is “how many and how bad,” not how loud the caller is. Write both. Lab: <code>impact 1</code> or <code>impact many</code>.</p>
<p>Before you reset a password, unlock an account, or read a mailbox, prove you have the right human. Follow local policy: badge, callback to a known number, supervisor confirm. “Just do it, we’ll sort it later” from an unknown caller is a no.</p>
</section>

<section id="s4" class="sublesson"><h3>4. Keep it or escalate</h3>
<p>Escalate when you lack access, tools, authority, or time-critical skill, or when safety/security needs a specialist. Transfer <em>understanding</em>, not just the ticket number.</p>
<p>A usable handoff has: who and how many; exact symptom; when it started and what changed; where they are; each test and its result; a clear ask.</p>
<div class="lab-panel"><div class="lab-title"><span>SCENARIO</span> Two VPN tickets</div>
<p><strong>A:</strong> “VPN not working.” No version, no error, no tests.<br>
<strong>B:</strong> Client 4.2.1, error 809, LAN ping OK, ping to gateway fails, started after weekend update, hotel Wi-Fi.<br>
Ticket B can be worked. Ticket A forces the next person to start at zero.</p></div>
</section>

<section id="s5" class="sublesson"><h3>5. Closing is not the same as fixed</h3>
<p>Closed means the required workflow works and the notes are complete. A green monitor icon is not enough if they still cannot submit the form they called about.</p>
</section>

<section id="s6" class="sublesson"><h3>6. Desk drill — paper first</h3>
<p>Fill this table for three contacts. Empty cell = not ready for the lab.</p>
<table class="port-table">
<tr><th>Field</th><th>What you write</th></tr>
<tr><td>Outcome they need</td><td>Send mail / print / badge / log in — not “fix the server”</td></tr>
<tr><td>Type</td><td>break/fix, request, or incident</td></tr>
<tr><td>Impact</td><td>1 or many, plus who</td></tr>
<tr><td>Safety stop?</td><td>Yes → stop and escalate. No → continue</td></tr>
<tr><td>Keep or escalate</td><td>One word plus why</td></tr>
<tr><td>Tests so far</td><td>Each line: action → result</td></tr>
<tr><td>Next step</td><td>A person or a command, not “look into it”</td></tr>
</table>
<p><strong>A:</strong> “Need Adobe on this new PC today.” → request, impact 1, keep only if you have package and approval.<br>
<strong>B:</strong> “I got a shock from the metal strip under the monitor.” → incident, escalate, do not swap the strip.<br>
<strong>C:</strong> “Printer worked at 0800, jam icon now, three people in line.” → break/fix unless it is the only printer for a watch (then impact many).</p>
<p>The live lab sentence is closer to B: many users plus heat. You will type that in 1.5.</p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Calling a first-time access ask “break/fix” because the user is upset</li>
<li>Writing impact as “high” with no count</li>
<li>Escalating with “VPN broken” and no test results</li>
</ul></div>
<div class="check-box"><h4>Check yourself (say the answer, then open)</h4>
<details><summary>1. New share access, never had it.</summary><p>Service request. Check entitlement. Do not reset a password to “make the share work.”</p></details>
<details><summary>2. One user, Outlook password loop since this morning.</summary><p>Break/fix, impact 1, keep unless you lack account tools.</p></details>
<details><summary>3. Half the building cannot badge.</summary><p>Incident, impact many, escalate. Do not start swapping a reader alone.</p></details>
<details><summary>4. Unknown caller wants a password reset “right now.”</summary><p>Stop. Verify identity per policy. No is a complete sentence.</p></details>
</div>'''
        },
        {
            "order": 2,
            "minutes": 45,
            "title": "1.2 Workplace and ESD Safety",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Stop work that is electrically or physically unsafe and say why in one sentence</li>
<li>Use an ESD strap and mat the way a bench actually works</li>
<li>Choose lift and path habits that keep you and the gear intact</li>
<li>Know when a safety issue is an incident, not a “quick swap”</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Stand a training tower. Point: wall cord, PSU switch, strap jack, mat ground. Trainees repeat the order: power off, unplug from the wall, wait, strap to bare skin, then open. No one opens a PSU. Lab stays ticket-intake — heat/shock language maps to classify incident.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 classification. Safety decides whether you are allowed to start the work at all.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Deadlines do not override physics. A chassis that was plugged in thirty seconds ago can still bite. Carpet and no strap can kill a DIMM and look like “bad RAM” all week.</p></div>
<div class="live-demo"><h4>Desk drill — before any hardware chapter</h4>
<p>On a powered-off training PC, point to power cord, PSU switch if present, case screws, strap jack. Say the order you will use in Chapter 2: power off, unplug from the wall, wait, strap, then open.</p></div>

<section id="s1" class="sublesson"><h3>1. Electrical reality on a training bench</h3>
<p>Treat every PSU and outlet as live until the cord is out of the wall (not just the PSU inlet) and you have waited. Do not defeat a ground pin. Do not work inside a PSU; replace the unit.</p>
<p>Liquids, metal jewelry, and open drinks on the bench are how shorts and ruined ports happen.</p>
</section>

<section id="s2" class="sublesson"><h3>2. ESD without mythology</h3>
<p>Electrostatic discharge is a spark you may not feel that still punches a hole in a chip. Carpet, dry air, and synthetic sleeves make it worse.</p>
<ol>
<li>Mat on a stable bench that is part of the shop ground plan.</li>
<li>Clip the mat to the specified ground point.</li>
<li>Strap on <em>bare skin</em>, then clip to the mat or chassis ground.</li>
<li>Only then unbag boards and memory. Keep parts in antistatic bags, not on the cardboard box.</li>
</ol>
<div class="analogy-box"><div class="analogy-label">Analogy · Fueling a small boat</div>
<p>You ground the nozzle before fuel flows. The strap is that path for the board. “I only needed ten seconds” is how you get intermittent failures nobody can reproduce.</p></div>
<p>If the strap is broken, stop and replace it. Holding the chassis is not a substitute unless shop procedure explicitly allows a momentary park — and you still bag the part when you walk away.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Body and path</h3>
<p>Bend at the knees, load close, do not twist. Second person for racks and floor UPS. Watch tiles, cables, and hatch edges before you walk with a chassis. Eye protection when cutting zip ties toward your face. No open-toe shoes on a raised floor.</p>
</section>

<section id="s4" class="sublesson"><h3>4. When safety becomes an incident</h3>
<p>Smell of burning, scorch, hot receptacle, user reporting shock: stop. Do not keep swapping PSUs to “see if it was a fluke.” Pull power if it is safe, keep people away, call facilities/electrical, write what you saw.</p>
<p>Ticket language: not break/fix “PSU maybe bad.” Incident + escalate. Lab ticket-intake uses that same pair when the prompt describes heat or shock.</p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Unplugging only at the PSU inlet and calling the chassis safe</li>
<li>Strap over a sleeve</li>
<li>Opening a reader or PSU “to see”</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Order before the side panel comes off?</summary><p>Power off → unplug from the wall → wait → strap on skin → then open.</p></details>
<details><summary>User felt a shock from a metal strip.</summary><p>Incident. Escalate. Do not swap the strip.</p></details>
<details><summary>May you service inside a PSU?</summary><p>No. Replace the unit.</p></details>
</div>'''
        },
        {
            "order": 3,
            "minutes": 45,
            "title": "1.3 Ticketing, Documentation, and Change Awareness",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Write a ticket a stranger can work from: symptom, scope, tests, result, next step</li>
<li>Separate facts from guesses in the same note</li>
<li>Recognize a change versus a repair, and say who must know</li>
<li>Use lab <code>note</code> at Ticket-B quality, then <code>submit</code></li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 45 minutes</h4>
<p>Put two notes on the board: one word vs four facts. Have the room vote which a night watch can use. Then each trainee writes one note for the quarterdeck-badge sentence. Do not accept “look into it” as a next step.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 classification and 1.2 stop-work. Notes are how the next watch inherits both.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>If it is not in the ticket, it did not happen. The person who opens this at 0200 was not on your call.</p></div>
<div class="live-demo"><h4>Lab commands this lesson unlocks</h4>
<p><code>show ticket</code> — read the raw sentence.<br>
<code>note ...</code> — working note, not “vpn broken.”<br>
<code>submit</code> — only after classify, impact, escalate, and note.</p></div>

<section id="s1" class="sublesson"><h3>1. Anatomy of a usable ticket</h3>
<ol>
<li>Who / where / how many</li>
<li>What they needed to do (the outcome)</li>
<li>Exact error text or behavior</li>
<li>When it started / last good / what changed</li>
<li>Tests you ran and the result of each</li>
<li>What you did</li>
<li>What is still true and the next action</li>
</ol>
<p>Write tests as pairs: action → result. “Pinged gateway” is incomplete. “Ping 10.20.30.1 → 4/4 replies, 1 ms” is a fact.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Facts versus guesses</h3>
<p>Fact: “Outlook shows a password prompt in a loop after the weekend patch window.” Guess: “Probably the domain controller.” Label guesses or leave them out. The next technician will treat your guess as measured truth.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Change awareness</h3>
<p>A <strong>change</strong> is an intentional alteration that can affect someone else: image a PC, add a group, firewall rule, DNS, firmware, major upgrade. A <strong>repair</strong> puts a known-good state back (reseat RAM, replace a failed disk with the same role).</p>
<p>Repairs still get notes. Changes also need the local change process. If policy says “no production DNS after 1500,” you do not “just add a record.”</p>
<div class="analogy-box"><div class="analogy-label">Analogy · Painting a passageway</div>
<p>Swapping a bulb is repair. Repainting during watch turnover is a change: time, warning, and a way back.</p></div>
</section>

<section id="s4" class="sublesson"><h3>4. Note quality bar for the lab</h3>
<p>The lab rejects a one-word note. Write outcome, one observation, and a next step:</p>
<p><code>note User cannot send mail since 0700. Outlook 16 password loop. Tried cached mode off — still loops. Escalate to messaging for account lock check.</code></p>
<p>Then <code>submit</code>. If it fails, <code>show ticket</code> and fill classify, impact, or escalate.</p>
</section>

<div class="miss-box"><h4>Common misses</h4>
<ul>
<li>Next step = “look into it”</li>
<li>Guess written as fact</li>
<li>Password pasted into the ticket</li>
</ul></div>
<div class="check-box"><h4>Check yourself</h4>
<details><summary>Is reseating RAM a change or a repair?</summary><p>Repair. Still write what you reseated and whether POST returned.</p></details>
<details><summary>Is adding a DNS record a change or a repair?</summary><p>Change. Use the local change process.</p></details>
</div>'''
        },
        {
            "order": 4,
            "minutes": 40,
            "title": "1.4 Professional Communication and Privacy",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Speak to a user in outcome language, not stack-trace language</li>
<li>Keep credentials, PII, and other people’s tickets off hallway talk and shared screens</li>
<li>Refuse unsafe requests without turning the user into an enemy</li>
<li>Know what belongs in the ticket versus what belongs on a phone to a lead</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 40 minutes</h4>
<p>Role-play two calls: angry first-time access, and “disable the firewall for a game.” The class writes one user-facing sentence and one ticket sentence. Grade the refusal on policy, not volume.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.3 notes. Same facts, aimed at a human who does not live in your tool.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>The user needs: can I work, when, and what do you need from me. Your lead needs the theory. Put each message in the right channel.</p></div>

<section id="s1" class="sublesson"><h3>1. Talk to the outcome</h3>
<p>Bad: “Your DHCP lease failed to renew so the NIC has an APIPA address.”<br>
Better: “This PC does not have a usable network address. I am renewing it. If that fails I will move you to a spare.”</p>
<p>On a long incident: who is affected, what you know, next check-in time. Silence reads as neglect.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Privacy on a real floor</h3>
<p>Do not read ticket details off a speakerphone in a passageway. Do not leave mail open on a shared screen. Do not paste passwords into the ticket. Do not use another person’s account “just to test.”</p>
<p>If you remote in, say what you can see. Close their mail and chat before you screenshot. Crop error dialogs when the rest of the screen is private.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Saying no</h3>
<p>“Add me to Finance-Share real quick” without approval is a no. “Disable the firewall so this launcher works” is a no. You can still be useful: open a request to the owner, or help them use the approved app.</p>
<p>If they escalate tone, you escalate the ticket to a lead — you do not trade policy for peace.</p>
</section>

<section id="s4" class="sublesson"><h3>4. What goes in the ticket</h3>
<p>Facts, times, tests, changes, user-visible status. Not jokes about the user. Not raw passwords. Not a rant about another shop. Judgment calls go to a lead, then a short factual line in the ticket.</p>
<p>The lab wants a clean <code>note</code>. That is the standard.</p>
</section>

<div class="check-box"><h4>Check yourself</h4>
<details><summary>User-facing line for no lease?</summary><p>This PC does not have a usable address. I am renewing it. I will update you in ten minutes.</p></details>
<details><summary>Caller wants a firewall off for a game.</summary><p>No. Offer the approved path. Open a request if they have a work need. Do not disable the profile.</p></details>
</div>'''
        },
        {
            "order": 5,
            "minutes": 60,
            "title": "1.5 Capstone — Safe Intake Workflow",
            "html": _NOTE + r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Run a complete intake: read, classify, impact, escalate, note, submit</li>
<li>Stop for safety before any “quick fix”</li>
<li>Produce a note another trainee can continue from</li>
</ul></div>
<div class="instructor-note"><h4>Instructor — 60 minutes</h4>
<p>Walk the command list once on a projector (10 min). Trainees run ticket-intake to submit (25 min). Peer-read three notes (15 min). Anyone who opened the “reader” in the story fails the pass bar even if submit succeeded.</p></div>
<div class="build-on"><strong>Builds on:</strong> 1.1–1.4. This lesson is the rehearsal. The live lab is the performance.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>You will see a raw sentence. You will not guess hardware yet. You will leave a structured intake. Chapters 2+ give you tools to test the guess.</p></div>
<div class="live-demo"><h4>Open lab ticket-intake now</h4>
<p>Expected order:</p>
<ol>
<li><code>help</code></li>
<li><code>show ticket</code></li>
<li><code>classify incident</code> (this card is many users + heat)</li>
<li><code>impact many</code></li>
<li><code>escalate yes</code></li>
<li><code>note</code> plus symptom, observation, next step</li>
<li><code>submit</code></li>
</ol>
<p>If submit fails, the desk tells you what is missing. Incomplete intakes do not leave your queue looking done.</p></div>

<section id="s1" class="sublesson"><h3>Worked example — this lab’s sentence</h3>
<p>User: “Half the quarterdeck badges stopped after lunch. The reader is warm.”</p>
<ul>
<li>classify → incident</li>
<li>impact → many</li>
<li>escalate → yes (facilities / access control, possible heat)</li>
<li>note → “About half of badge readers failed after 1200. Reader surface warm. Did not open the panel. Need facilities and duty section on scene. Users on a manual log.”</li>
</ul>
<p>Do not pop the reader open. Heat plus access control is not a solo hobby.</p>
</section>

<section id="s2" class="sublesson"><h3>Pass bar</h3>
<p>You pass Block 1 when you finish the lab without being fed the answers, your note names heat and a next person, and you did not “open the panel.” Then Chapter 2 puts hardware names on the same discipline.</p>
</section>

<div class="check-box"><h4>Before you launch</h4>
<p>Say out loud: type, impact, escalate, one sentence note. Then use the lab button under this lesson.</p>
</div>'''
        },
    ],
}
