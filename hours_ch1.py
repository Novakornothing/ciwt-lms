"""Chapter 1 multi-hour teach pack. Appended onto the existing lessons."""

# Contact hours, not "read this slide in 12 minutes."
MINUTES = {1: 90, 2: 90, 3: 90, 4: 75, 5: 90}
CHAPTER_MINUTES = 435


def _h(title, body):
    return f'<section class="sublesson hours"><h3>{title}</h3>\n{body}\n</section>\n'


L1 = "".join([
_h("Hour plan for 1.1", """
<p>This lesson is <strong>90 minutes of teaching</strong>, not a 15-minute briefing. Spend it like this:</p>
<table class="port-table">
<tr><th>Min</th><th>You do</th></tr>
<tr><td>0–15</td><td>Read “paid to restore an outcome.” Class says one sentence each.</td></tr>
<tr><td>15–35</td><td>Four labels: request / break-fix / incident / change. Work the table aloud.</td></tr>
<tr><td>35–55</td><td>Identity script. Two volunteers: one is a stranger, one is the real user.</td></tr>
<tr><td>55–75</td><td>Write one Ticket-B note from a raw sentence. Peer scores it.</td></tr>
<tr><td>75–90</td><td>Handoff out loud. Preview show ticket only — lab finish is 1.5.</td></tr>
</table>
"""),
_h("What you are paid to restore", """
<p>A support technician is paid to restore a <em>required outcome</em> without creating a second outage. The outcome is whatever the person or watch must do again: send the report, badge the door, print the watchbill, open the medical record, join the briefing VTC.</p>
<p>Everything else is a tool. A motherboard, an ipconfig line, a print driver, a vCenter snapshot — those matter only when they sit on the path to the outcome. If you cannot name the outcome in one sentence a lead would accept, you are not ready to touch the box.</p>
<p>Examples of good outcome sentences:</p>
<ul>
<li>“User in 214 can send mail from Outlook 16 on this PC.”</li>
<li>“All quarterdeck badges work on reader 3.”</li>
<li>“The floor printer accepts the watchbill from any staff PC on VLAN 20.”</li>
</ul>
<p>Examples of bad opening lines:</p>
<ul>
<li>“Looking into the network.”</li>
<li>“Layer 3 might be down.”</li>
<li>“User is difficult.”</li>
</ul>
"""),
_h("The four labels and what changes when you pick one", """
<table class="port-table">
<tr><th>Label</th><th>Means</th><th>What you do first</th><th>What you do not do</th></tr>
<tr><td>Service request</td><td>They never had it</td><td>Entitlement / who owns the access</td><td>Reset a password to “make the share appear”</td></tr>
<tr><td>Break/fix</td><td>It used to work</td><td>When it last worked, what changed</td><td>Treat it like a new-hire access ticket</td></tr>
<tr><td>Incident</td><td>Many users, safety, security, or a named critical service</td><td>Stop, scope, escalate per shop</td><td>Swap a reader alone while the building is locked out</td></tr>
<tr><td>Change</td><td>You will introduce something new</td><td>Shop process, rollback, window</td><td>“I just added the DNS record after 1500”</td></tr>
</table>
<p>The same raw sentence can move labels when facts arrive. “Printer down” is break/fix for one desk and an incident if it is the only printer for a watch that starts in twenty minutes. Write the label you are using <em>now</em>, and change it in the ticket when the facts change.</p>
"""),
_h("Impact is a count plus a consequence", """
<p>“High” is not impact. Impact is:</p>
<ul>
<li>How many people or watches cannot do the required outcome</li>
<li>What happens if it stays broken (turnover, medical, comms, payroll)</li>
<li>Whether safety or security is in the path</li>
</ul>
<p>Write “14 users in Bldg 3 cannot badge; mid-watch turnover in 20 minutes.” Do not write “priority high.” The next person cannot act on a feeling.</p>
"""),
_h("Desk set — classify these out loud", """
<p>Do not skip this. Say the label, the impact, and keep-or-escalate.</p>
<ol>
<li>New hire, first day, never had the budget share. Next desk works.</li>
<li>Outlook password loop since 0700. Next desk fine. User known in person.</li>
<li>Half the building cannot badge. Reader face is warm.</li>
<li>Unknown caller wants a reset right now and cannot complete the identity script.</li>
<li>User wants a production DNS record added at 1510 so a vendor demo works.</li>
<li>One floor printer jammed; two other printers on the floor work.</li>
<li>The only printer for the mid-watch watchbill is jammed and turnover is in 15 minutes.</li>
<li>User felt a shock from the strip under the monitor.</li>
</ol>
<p>Answer key the instructor uses: 1 request / 2 break-fix impact 1 / 3 incident many escalate / 4 stop identity / 5 change, not a silent repair / 6 break-fix impact 1 / 7 incident or at least impact-many for that watch / 8 incident stop escalate. Argue the edge cases. The point is the argument, not a secret code.</p>
"""),
_h("Identity before any account change", """
<p>A password reset, an unlock, a share add, a mailbox open — those are privileged. The shop identity script exists because friendly voices lie. Typical pieces (use <em>your</em> shop list, not this paragraph as policy):</p>
<ul>
<li>Person is on a listed callback number, not the number they offered</li>
<li>Employee / DOD ID / last four as the shop requires</li>
<li>Badge in hand if they are at the window</li>
<li>Supervisor on the line if the shop requires it for after-hours</li>
</ul>
<p>Write <em>how</em> you verified: “Callback to listed desk 555-0142.” Never write the old password, the new password, or the mother’s maiden name. If they cannot complete the script, the answer is no. No is a complete sentence. Document the refusal as a fact.</p>
"""),
_h("Handoff that survives 0200", """
<p>A handoff has five lines:</p>
<ol>
<li>Outcome they still cannot do</li>
<li>How many / where</li>
<li>Tests you ran and the results</li>
<li>What you already changed (one thing at a time)</li>
<li>Next person or next command</li>
</ol>
<p>Bad: “VPN broken, please fix.” Good: “Outlook 16 on PC214, error 809, LAN ping 10.20.30.50 4/4, gateway 10.20.30.1 fails, started after weekend client update, user on hotel Wi-Fi, next: messaging check account lock.”</p>
"""),
])

L2 = "".join([
_h("Hour plan for 1.2", """
<table class="port-table">
<tr><th>Min</th><th>You do</th></tr>
<tr><td>0–20</td><td>Stand at a training tower. Point wall cord, PSU rocker, strap jack, mat ground.</td></tr>
<tr><td>20–40</td><td>Class recites the five-step open order. Every person points. No one opens a PSU.</td></tr>
<tr><td>40–60</td><td>Shock / heat / smell stories. Label them incident. Practice the stop sentence.</td></tr>
<tr><td>60–75</td><td>Lift and path. Two-person tower. Where the cord is before you pick it up.</td></tr>
<tr><td>75–90</td><td>Map heat-on-a-reader to ticket-intake language. Do not open the reader.</td></tr>
</table>
"""),
_h("Why this chapter exists before hardware", """
<p>Chapter 2 will ask you to open a side panel. If you do not have the safety order in your hands, Chapter 2 is how people get bit and how boards die. Block 1 is not “soft skills.” It is the condition for touching metal.</p>
"""),
_h("The five-step open order, slowly", """
<ol>
<li><strong>Power off the PC</strong> from the OS if it is up, then the case switch. Closing a laptop lid is not power off.</li>
<li><strong>Unplug the cord from the wall.</strong> The PSU rocker is not the wall. Capacitors can stay charged. The wall end is the one that matters.</li>
<li><strong>Wait.</strong> You do not count to two and yank the panel. Give the supply a moment.</li>
<li><strong>Strap on bare skin</strong>, clip to the mat or chassis ground the shop uses. Over a fleece sleeve is jewelry, not a strap.</li>
<li><strong>Then</strong> open the panel. Panel first is the failure.</li>
</ol>
<p>Defeat the ground pin so a three-prong cord fits a two-prong tap: never. That is how you and the board share a surge.</p>
"""),
_h("What you never open", """
<p>The PSU is a sealed field-replaceable unit. You do not go inside it to “check a capacitor.” You replace the unit. A CRT monitor, if one still exists in a closet, is not a training toy. Batteries that are swollen are Chapter 4 — stop, do not pry in this room.</p>
"""),
_h("When safety is the ticket", """
<p>Shock from a strip. Burn smell. Outlet face hot. Reader face hot with people still using it. Those are incidents. Your sentence: “Stop. Do not use that gear. I am escalating.” Then you write it. You do not finish the RAM reseat “real quick” on a box that bit someone.</p>
<p>Map it onto Lab ticket-intake the way 1.5 will: classify incident, impact many if more than one person is in the path, escalate yes, note names heat or shock and that you did not open the panel.</p>
"""),
_h("Lift and path", """
<p>Clear the floor. Know where the wall cord is. Two people on an awkward full tower. Do not rest a chassis on a rolling chair. Monitors have edges; cases have corners. If you cannot say the path out loud, you are not ready to lift.</p>
"""),
])

L3 = "".join([
_h("Hour plan for 1.3", """
<table class="port-table">
<tr><th>Min</th><th>You do</th></tr>
<tr><td>0–20</td><td>Ticket A vs Ticket B on the board. Class rewrites three A’s into B’s.</td></tr>
<tr><td>20–45</td><td>Action → result drills. Every test is a pair.</td></tr>
<tr><td>45–70</td><td>Repair vs change. Four shop examples. When the process applies.</td></tr>
<tr><td>70–90</td><td>Each trainee writes one full Ticket-B from a raw sentence. Peer scores.</td></tr>
</table>
"""),
_h("Anatomy of Ticket B", """
<p>Required lines, in language a stranger can use:</p>
<ol>
<li>Who and where (desk, building, hostname if you have it)</li>
<li>Outcome they need</li>
<li>When it last worked / what changed</li>
<li>Tests: action → result</li>
<li>What you already did</li>
<li>Next person or next command</li>
</ol>
<p>Ticket A is a slogan: “VPN broken.” Ticket B is evidence. If your note cannot survive you going to lunch, it is still Ticket A.</p>
"""),
_h("Action → result until it is boring", """
<p>Wrong: “Pinged the gateway.” Right: “Ping 10.20.30.1 — 0/4 timeout.” Wrong: “Checked Outlook.” Right: “Cached mode off — still password loop, error 809.” Wrong: “Looks fine.” Right: “ipconfig /all — 169.254.27.8, DHCP enabled, no DHCP server listed.”</p>
<p>Do ten of these on scrap paper. The lab <code>note</code> command is this habit with a smaller box.</p>
"""),
_h("Repair versus change, with shop examples", """
<table class="port-table">
<tr><th>Work</th><th>Label</th><th>Why</th></tr>
<tr><td>Reseat RAM after MEM beep</td><td>Repair</td><td>Return to a known-good seat</td></tr>
<tr><td>Replace a failed PSU with the same FRU</td><td>Repair</td><td>Still document; do not open the old unit</td></tr>
<tr><td>Add a production DNS record</td><td>Change</td><td>Something new now exists</td></tr>
<tr><td>Image a staff PC</td><td>Change</td><td>New OS state; needs backup and a window</td></tr>
<tr><td>Change AP admin password</td><td>Change</td><td>Shared infrastructure</td></tr>
<tr><td>Temporarily allow Secure Boot off to run a shop USB</td><td>Change</td><td>Must go back</td></tr>
</table>
<p>Repairs still get notes. Changes get the shop process even when they take two minutes. “I just added it” is how mail dies after 1500.</p>
"""),
_h("What never goes in the ticket", """
<p>Passwords. Full SSNs. Jokes about the user. Rants about another shop. Guesswork written as measured truth. If you must guess, label it guess.</p>
"""),
])

L4 = "".join([
_h("Hour plan for 1.4", """
<table class="port-table">
<tr><th>Min</th><th>You do</th></tr>
<tr><td>0–20</td><td>Two-audience drill: say the user sentence, then write the ticket sentence.</td></tr>
<tr><td>20–40</td><td>Refuse an unsafe reset. Partner plays the loud caller.</td></tr>
<tr><td>40–60</td><td>Privacy: what is PII here, what is a hostname, what is a secret.</td></tr>
<tr><td>60–75</td><td>Write one refusal note that is factual, not a fight.</td></tr>
</table>
"""),
_h("User channel versus ticket channel", """
<p>User: “You can send mail again. I need you to stay on this PC until we confirm the report goes. I will check back at 1400.” Ticket: versions, error codes, pings, times. Lead phone: “I think this is an account lock, not a NIC. Can messaging take it?” If you dump DHCP into the user channel they stop listening. If you dump feelings into the ticket the next watch cannot work.</p>
"""),
_h("Refuse without becoming the enemy", """
<p>Script: “I cannot reset that from this call. Here is the approved path: [window / portal / supervisor]. If you are the user, come to the window with your badge.” Then write: “Declined reset. Caller could not complete identity script. Directed to window.” That is not a war. That is the job.</p>
"""),
_h("Privacy on a real bench", """
<p>Screens face away from the passageway. Privacy screen if the shop issues one. Do not read medical or personnel records out loud for color. Do not leave a box unlocked while you get coffee. Do not put a password on a sticky note “for the next guy.” The next guy is how accounts walk away.</p>
"""),
])

L5 = "".join([
_h("Hour plan for 1.5", """
<table class="port-table">
<tr><th>Min</th><th>You do</th></tr>
<tr><td>0–15</td><td>Read the live card together. Name heat and many users before anyone types.</td></tr>
<tr><td>15–45</td><td>Every trainee runs ticket-intake to submit. Instructor watches classify and impact.</td></tr>
<tr><td>45–70</td><td>Failed submits: say why. Run it again clean.</td></tr>
<tr><td>70–90</td><td>Chapter 1 check (10 items). Misses go back to the matching section, not a new tool.</td></tr>
</table>
"""),
_h("The card, line by line", """
<p>The lab sentence is: after lunch, half the quarterdeck badges failed, the reader face is warm. That is not a broken cable on one PC. That is many users plus heat on an access-control device.</p>
<p>Commands the lab wants, in order:</p>
<ol>
<li><code>show ticket</code> — read before you type</li>
<li><code>classify incident</code> — not break-fix, not request</li>
<li><code>impact many</code> — not impact 1</li>
<li><code>escalate yes</code> — facilities / access control / safety, not you with a screwdriver</li>
<li><code>note</code> — warm reader, did not open the panel, next person named</li>
<li><code>submit</code></li>
</ol>
<p>Fails: classify break-fix, impact 1, escalate no, note that opens the reader, empty note, password in the note.</p>
"""),
_h("After the lab", """
<p>If submit passed and the chapter check is weak on identity, you are not done. The lab is one card. The job is every card. Re-read 1.1 identity and write one more refusal note before you go to Chapter 2.</p>
"""),
])

PACK = {1: L1, 2: L2, 3: L3, 4: L4, 5: L5}


def apply_hours_ch1(pack):
    for ch in pack:
        if not isinstance(ch, dict) or ch.get("order") != 1:
            continue
        ch["minutes"] = CHAPTER_MINUTES
        for les in ch.get("lessons") or []:
            o = les.get("order")
            if o in MINUTES:
                les["minutes"] = MINUTES[o]
            extra = PACK.get(o)
            if extra:
                les["html"] = (les.get("html") or "") + extra
    return pack
