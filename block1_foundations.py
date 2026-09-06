"""CIWT Block 1 / Chapter 1 — Workplace, tickets, and safety.
Original CIWT schoolhouse material. Not official Navy courseware.
Written so a brand-new trainee can classify work, write a ticket, and run Lab ticket-intake.
"""

CHAPTER1 = {
    "title": "Chapter 1 — Professional Foundations & Workplace Safety",
    "order": 1,
    "minutes": 180,
    "overview": (
        "You learn how support work is structured before you touch hardware or CLI. "
        "Classify tickets, work safely, write notes another watch can use, then prove it in the intake lab."
    ),
    "lessons": [
        {
            "order": 1,
            "title": "1.1 The Support Technician Role",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>State what a support technician is paid to restore on a normal watch, in one sentence a chief would accept</li>
<li>Sort a contact into break/fix, service request, or incident and say what process changes when the label changes</li>
<li>Verify identity before changing an account or sharing data</li>
<li>Hand a problem off with facts the next technician can act on without calling you back</li>
</ul></div>
<div class="build-on"><strong>Where this fits:</strong> Block 1 / Chapter 1. Hardware, Windows, and networking come after this. If you cannot triage and write, those tools just help you break things faster.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Users do not bring you “Layer 3.” They bring you outcomes: the report will not send, the floor printer is dead, mail looks wrong. Your job is to restore the outcome without creating a second outage, leave a record, and tell the truth about what you know.</p>
<p>Memorizing clicks fails the first time the screen is different. Structure does not: what kind of work this is, who is hurt, what you already tried, and whether you should keep it or pass it.</p></div>
<div class="live-demo"><h4>What you will do in the lab</h4>
<p>Lab <strong>ticket-intake</strong> sits under this chapter. You will open a raw user sentence, classify it, set impact, decide escalate or keep, write a note, and submit. Every command in that lab is taught in this lesson. Do not start the lab until you can do the desk drills below out loud.</p></div>

<section id="s1" class="sublesson"><h3>1. What the role actually delivers</h3>
<p>On almost every contact you do four things:</p>
<ol>
<li><strong>Restore service</strong> — the user’s required workflow works again (login, print, send, VPN, open the file).</li>
<li><strong>Reduce risk</strong> — you do not turn off security “to make it work,” share admin passwords, or leave an account unlocked for convenience.</li>
<li><strong>Leave a trail</strong> — notes the next watch can trust at 0200 without you on the phone.</li>
<li><strong>Communicate</strong> — the user and your lead know status, next step, and what you need from them.</li>
</ol>
<p>You sit between human language and system behavior. “The internet is down” might be DNS, captive portal, proxy, VPN, Wi-Fi association, or one blocked site. Your first job is to turn vague words into a testable claim.</p>
<div class="analogy-box"><div class="analogy-label">Analogy · ER triage</div>
<p>Arrival order is not treatment order. A stable sprained ankle waits if someone is bleeding. One laptop offline is real work. Malware spreading across a wing is more important because impact multiplies. Always ask: how many people, and how bad if we wait.</p></div>
</section>

<section id="s2" class="sublesson"><h3>2. Three kinds of work</h3>
<p>The label is not paperwork trivia. It changes approvals, clocks, and who must be told.</p>
<table class="port-table">
<tr><th>Type</th><th>Meaning</th><th>What you do</th></tr>
<tr><td><strong>Break/fix</strong></td><td>Something that used to work stopped</td><td>Troubleshoot, repair, verify with the user</td></tr>
<tr><td><strong>Service request</strong></td><td>Something new is asked for</td><td>Check entitlement, get approval if required, fulfill</td></tr>
<tr><td><strong>Incident</strong></td><td>Many users, a major service, or security</td><td>Contain, coordinate, communicate; page a specialist if needed</td></tr>
</table>
<p><strong>SLA</strong> is the published response/resolve target. It is not permission to close a ticket before the user can work.</p>
<p><strong>Classify these before you touch a keyboard:</strong></p>
<ul>
<li>“I need the budget share for the first time.” → service request</li>
<li>“Outlook worked yesterday; today it loops on password.” → break/fix</li>
<li>“Half the building cannot badge in.” → incident</li>
<li>“Someone sent mail as me.” → incident (security) until proven otherwise</li>
</ul>
<p>In the lab the command is <code>classify break-fix</code>, <code>classify request</code>, or <code>classify incident</code>. Pick one. If two feel true, pick the higher risk (incident beats break/fix).</p>
</section>

<section id="s3" class="sublesson"><h3>3. Impact and identity</h3>
<p>Impact is “how many and how bad,” not how loud the caller is. One executive offline is high visibility. Twenty users on a floor with no badge is high impact. Write both.</p>
<p>In the lab: <code>impact 1</code> or <code>impact many</code>.</p>
<p>Before you reset a password, unlock an account, or read a mailbox, prove you have the right human. Social engineering works when you skip that check because the voice sounds urgent. Follow local policy: badge, callback to a known number, supervisor confirm. “Just do it, we’ll sort it later” from an unknown caller is a no.</p>
</section>

<section id="s4" class="sublesson"><h3>4. Keep it or escalate</h3>
<p>Escalate when you lack access, tools, authority, or time-critical skill, or when safety/security needs a specialist. Escalation is professional when it transfers <em>understanding</em>, not just the ticket number.</p>
<p>A usable handoff has:</p>
<ul>
<li>Who is affected and how many</li>
<li>Exact symptom and error text</li>
<li>When it started and what changed</li>
<li>Where they are (desk, VPN, hotel, ship)</li>
<li>Steps already tried and the <em>result of each step</em></li>
<li>A clear ask (“need group X on account Y”)</li>
</ul>
<div class="lab-panel"><div class="lab-title"><span>SCENARIO</span> Two VPN tickets</div>
<p><strong>Ticket A:</strong> “VPN not working.” No version, no error, no tests.<br>
<strong>Ticket B:</strong> Client 4.2.1, error 809, LAN ping OK, ping to gateway fails, started after weekend update, hotel Wi-Fi.<br>
Ticket B can be worked. Ticket A forces the next person to start at zero. In the lab, <code>escalate yes</code> or <code>escalate no</code>, then <code>note</code> with Ticket-B quality facts.</p></div>
</section>

<section id="s5" class="sublesson"><h3>5. Closing is not the same as fixed</h3>
<p>Closed means the required workflow works and the notes are complete. A green monitor icon is not enough if they still cannot submit the form they called about. Verify with the user when you can. If you cannot reach them, say what you verified and what they must confirm.</p>
<p>Desk drill (say it out loud): classify the four examples above, pick impact, say keep or escalate, then write one four-line note. Then open <strong>ticket-intake</strong>.</p>
</section>

<section id="s6" class="sublesson"><h3>6. Watch walk-through (paper first)</h3>
<p>Fill this table for three contacts before you open the lab. Empty cell = not ready to submit.</p>
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
<p>The live lab sentence is closer to B: many users plus heat. classify incident, impact many, escalate yes, note, submit.</p>
</section>'''
        },
        {
            "order": 2,
            "title": "1.2 Workplace and ESD Safety",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Stop work that is electrically or physically unsafe and say why in one sentence</li>
<li>Use an ESD strap and mat the way a bench actually works, not as a slogan</li>
<li>Choose PPE and lift/path habits that keep you and the gear intact</li>
<li>Know when a safety issue becomes an incident, not a “quick swap”</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 — you already know to classify work. Safety decides whether you are allowed to start the work at all.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>Deadlines do not override physics. A chassis that was plugged in thirty seconds ago can still bite. A carpeted shop with no strap can kill a $200 DIMM and look like “bad RAM” for the rest of the week.</p></div>
<div class="live-demo"><h4>Desk drill before any hardware chapter</h4>
<p>Stand a powered-off training PC. Point to power cord, PSU switch if present, case screws, strap jack. Say the order you will use in Chapter 2: power off, unplug, wait, strap, then open. If you cannot point and say it, you are not ready to pull a stick of RAM later.</p></div>

<section id="s1" class="sublesson"><h3>1. Electrical reality on a training bench</h3>
<p>Treat every PSU and wall outlet as live until you have removed the cord from the wall (not just from the PSU inlet) and waited. Some supplies store charge. Do not defeat a ground pin. Do not work inside a PSU; replace the unit.</p>
<p>Liquids, metal jewelry, and open drinks on the bench are not “being careful later.” They are how shorts and ruined ports happen.</p>
</section>

<section id="s2" class="sublesson"><h3>2. ESD without mythology</h3>
<p>Electrostatic discharge is a tiny spark you may not feel that still punches a hole in a chip. Carpet, dry air, and synthetic sleeves make it worse.</p>
<ol>
<li>Put the mat on a stable bench, not a painted metal cart that is not part of the ground plan.</li>
<li>Clip the mat to a known ground (bench ground point or the equipment ground your shop specified).</li>
<li>Put the strap on <em>bare skin</em>, then clip the strap to the mat or the chassis ground point.</li>
<li>Only then unbag boards and memory. Keep parts in antistatic bags, not on the cardboard box.</li>
</ol>
<div class="analogy-box"><div class="analogy-label">Analogy · Fueling a small boat</div>
<p>You ground the nozzle before fuel flows so a spark has a path that is not the tank. The strap is that path for the board. Skipping it because “I only needed ten seconds” is how you get intermittent failures nobody can reproduce.</p></div>
<p>A wrist strap is not optional theater. If the strap is broken, stop and replace it. Do not “just hold the chassis” as a substitute unless your shop procedure explicitly allows a momentary park of the board on the grounded chassis — and even then, bag it when you walk away.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Body and path</h3>
<p>Servers and UPSs are heavy. Bend at the knees, keep the load close, do not twist. Get a second person for racks and floor-standing UPS. Watch floor tiles, cables, and hatch edges before you walk with a chassis in your hands.</p>
<p>Eye protection when cutting zip ties toward your face. Hearing protection in a generator or IDF that actually needs it. No open-toe shoes on a raised floor.</p>
</section>

<section id="s4" class="sublesson"><h3>4. When safety becomes an incident</h3>
<p>Smell of burning, scorch marks, a receptacle that is hot to the touch, a user reporting shock: stop. Do not keep swapping PSUs to “see if it was a fluke.” That is an incident. Pull power if it is safe to do so, keep people away, call the person who owns facilities/electrical, write what you saw.</p>
<p>In ticket language this is not break/fix “PSU maybe bad.” It is incident + escalate. You will use those same commands in <strong>ticket-intake</strong> when the prompt describes a hot outlet or a shock.</p>
</section>'''
        },
        {
            "order": 3,
            "title": "1.3 Ticketing, Documentation, and Change Awareness",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Write a ticket a stranger can work from: symptom, scope, tests, result, next step</li>
<li>Separate facts from guesses in the same note</li>
<li>Recognize a change (something you intend to alter) versus a repair, and say who must know</li>
<li>Use the lab <code>note</code> command at Ticket-B quality, then <code>submit</code></li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 1.1 classification and 1.2 stop-work. Notes are how the next watch inherits both.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>If it is not in the ticket, it did not happen. Memory is not a record. The person who opens this at 0200 was not on your call.</p></div>
<div class="live-demo"><h4>Lab commands this lesson unlocks</h4>
<p><code>show ticket</code> — read the raw user sentence and any system fields.<br>
<code>note ...</code> — write the working note (several words, not “vpn broken”).<br>
<code>submit</code> — close the intake only after classify, impact, escalate, and note are done.</p></div>

<section id="s1" class="sublesson"><h3>1. Anatomy of a usable ticket</h3>
<p>Minimum fields you should be able to fill without looking at a template:</p>
<ol>
<li><strong>Who / where / how many</strong></li>
<li><strong>What they needed to do</strong> (the outcome), not the guessed root cause</li>
<li><strong>Exact error text or behavior</strong></li>
<li><strong>When it started / last time it worked / what changed</strong></li>
<li><strong>Tests you ran and the result of each</strong> (ping gateway OK, ping name FAIL)</li>
<li><strong>What you did</strong> (changed X, restarted Y)</li>
<li><strong>What is still true</strong> and the next action</li>
</ol>
<p>Write tests as pairs: action → result. “Pinged gateway” is incomplete. “Ping 10.20.30.1 → 4/4 replies, 1 ms” is a fact.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Facts versus guesses</h3>
<p>Fact: “Outlook shows password prompt in a loop after the weekend patch window.” Guess: “Probably the domain controller.” Put guesses in a separate line labeled guess, or do not put them in. The next technician will treat your guess as measured truth and waste an hour.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Change awareness</h3>
<p>A <strong>change</strong> is an intentional alteration that can affect someone else: image a PC, add a group, firewall rule, DNS record, firmware, major app upgrade. A <strong>repair</strong> puts a known-good state back (reseat RAM, replace a failed disk with the same role).</p>
<p>Repairs still get notes. Changes also need the local change process — even a short one — because the outage you cause at 0900 is now your incident. If policy says “no production DNS after 1500,” you do not “just add a record.”</p>
<div class="analogy-box"><div class="analogy-label">Analogy · Painting a passageway</div>
<p>Swapping a burned-out bulb is repair. Repainting the passageway during watch turnover is a change: you need a time, a warning, and a way back if the paint is wrong. Tickets are how the rest of the ship knows which one you did.</p></div>
</section>

<section id="s4" class="sublesson"><h3>4. Note quality bar for the lab</h3>
<p>The lab rejects a one-word note. Write at least the outcome, one test or observation, and a next step. Example that should pass:</p>
<p><code>note User cannot send mail since 0700. Outlook 16 password loop. Tried cached mode off — still loops. Escalate to messaging for account lock check.</code></p>
<p>Then <code>submit</code>. If submit fails, <code>show ticket</code> and fill the missing piece (classify, impact, or escalate).</p>
</section>'''
        },
        {
            "order": 4,
            "title": "1.4 Professional Communication and Privacy",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Speak to a user in outcome language, not stack-trace language</li>
<li>Keep credentials, PII, and other people’s tickets off hallway talk and shared screens</li>
<li>Refuse unsafe requests without turning the user into an enemy</li>
<li>Know what belongs in the ticket versus what belongs on a phone to a lead</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 1.3 notes. Communication is the same facts, aimed at a human who does not live in your tool.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>The user needs to know: can I work, when, and what do you need from me. They do not need your theory about the mail connector. Your lead needs the theory. Put each message in the right channel.</p></div>

<section id="s1" class="sublesson"><h3>1. Talk to the outcome</h3>
<p>Bad: “Your DHCP lease failed to renew so the NIC has an APIPA address.”<br>
Better: “This PC does not have a usable network address. I am renewing it. If that fails I will move you to a spare while I keep working.”</p>
<p>Status cadence on a long incident: who is affected, what you know, next check-in time. Silence reads as neglect.</p>
</section>

<section id="s2" class="sublesson"><h3>2. Privacy on a real floor</h3>
<p>Do not read ticket details off a speakerphone in a passageway. Do not leave a screen shared with a mailbox open. Do not paste passwords into the ticket. Do not use another person’s account “just to test.” Those are how small shops get big problems.</p>
<p>Screen-share risk: if you remote in, say what you can see. Close their mail and chat before you record or screenshot for a ticket. Crop error dialogs when the rest of the screen is a privacy problem.</p>
</section>

<section id="s3" class="sublesson"><h3>3. Saying no</h3>
<p>“Can you add me to Finance-Share real quick?” without approval is a no. “Can you disable the firewall so this game launcher works?” is a no. You can still be useful: “I can open a request to the owner of that share” or “I can help you use the approved app.”</p>
<p>If they escalate tone, you escalate the ticket to a lead — you do not trade policy for peace.</p>
</section>

<section id="s4" class="sublesson"><h3>4. What goes in the ticket</h3>
<p>Facts, times, tests, changes, user-visible status. Not jokes about the user. Not raw passwords. Not a rant about another shop. If you need a judgment call (“this looks like someone fishing for a reset”), call the lead, then write a short factual line.</p>
<p>You will not type social language into the lab. You will type a clean <code>note</code>. That is the standard.</p>
</section>'''
        },
        {
            "order": 5,
            "title": "1.5 Capstone — Safe Intake Workflow",
            "html": r'''<div class="lo-panel"><h4>Terminal objectives</h4>
<ul>
<li>Run a complete intake: read, classify, impact, escalate decision, note, submit</li>
<li>Stop for safety before any “quick fix”</li>
<li>Produce a note another trainee can continue from</li>
</ul></div>
<div class="build-on"><strong>Builds on:</strong> 1.1–1.4. This lesson is the rehearsal. The live lab is the performance.</div>
<div class="plain-english"><h4>In plain English</h4>
<p>You will see a raw sentence. You will not guess hardware yet. You will leave a structured intake. That is Block 1. Chapters 2+ give you tools to test the guess.</p></div>
<div class="live-demo"><h4>Open lab ticket-intake now</h4>
<p>Commands, in order you should expect to use:</p>
<ol>
<li><code>help</code> — list legal commands</li>
<li><code>show ticket</code> — read the user sentence</li>
<li><code>classify break-fix</code> or <code>request</code> or <code>incident</code></li>
<li><code>impact 1</code> or <code>impact many</code></li>
<li><code>escalate yes</code> or <code>escalate no</code></li>
<li><code>note</code> plus a real sentence (symptom, one observation, next step)</li>
<li><code>submit</code></li>
</ol>
<p>If submit fails, the desk tells you what is missing. That is intentional. Incomplete intakes do not leave your queue looking done.</p></div>

<section id="s1" class="sublesson"><h3>Worked example</h3>
<p>User: “Half the quarterdeck badges stopped after lunch. The reader is warm.”</p>
<ul>
<li>classify → incident (many users + possible electrical)</li>
<li>impact → many</li>
<li>escalate → yes (facilities / security gear, possible heat)</li>
<li>note → “About 50% of badge readers failed after 1200. Reader surface warm. Did not open the panel. Need facilities and duty section on scene. Users using manual log.”</li>
</ul>
<p>Do not pop the reader open to “see if a cable is loose” after 1.2. Heat plus access control is not a solo hobby.</p>
</section>

<section id="s2" class="sublesson"><h3>Pass bar</h3>
<p>You pass this chapter when you can finish the lab without being told the answers, and when a peer can take your note and know what to do next. Then Chapter 2 starts putting hardware names on the same discipline.</p>
</section>'''
        },
    ],
}
