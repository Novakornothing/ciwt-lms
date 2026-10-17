"""ITSUP Chapter 7 — Troubleshooting Methodology (pass 9 core content, pending SME review)."""
from . import cfu, figure, item, scenario, sme_note, table, worked

CHAPTER = 7
SOURCES_USED = []

LESSONS = {
    (7, 1): {
        'objectives': [
            'Apply the seven-step method (identify, probable cause, test, plan, change one thing, verify, document) to a ticket',
            'Write a probable-cause list of no more than three theories, each with the cheapest test that could disprove it',
            'Justify a test order by cost, risk and how much of the problem each test rules out',
            'Record each test as an action → result pair that another technician could repeat',
        ],
        'html': sme_note() + '''
<h3>Why a method beats experience alone</h3>
<p>Experienced technicians are fast because they follow a method so often that it looks like instinct. Beginners who skip the
method tend to do one of two things: they change several things at once and cannot say which one worked, or they start with the
most expensive fix (reimage, replace the part) because it feels decisive. A written method protects you from both. It also
protects the user: every step you take on their device should be one you can explain and undo.</p>
<p>The method has seven steps. The names matter less than the order and the evidence each step produces.</p>
''' + table(['Step', 'Question it answers', 'What you write down', 'Common mistake'], [
            ['1 Identify', 'What outcome is missing, for whom, since when, and how many are affected?', 'Symptom in the user’s words, exact error text, scope, start time, recent changes', 'Accepting the user’s diagnosis (“it’s the Wi-Fi”) as the problem'],
            ['2 Probable cause', 'What are the two or three most likely explanations?', 'A short ranked list of theories', 'Listing ten causes and testing none'],
            ['3 Test', 'Which cheap test can disprove the top theory?', 'Action → result (“ping 10.1.1.1 — 4/4 replies”)', 'Running a test that cannot change your mind'],
            ['4 Plan', 'What will I change, what could break, and how do I undo it?', 'The change, its impact, the rollback step, any approval needed', 'No rollback, or making a change that needs approval without it'],
            ['5 Change one thing', 'Did that single change restore the outcome?', 'Exactly what changed and when', 'Changing the driver, the cable and the setting together'],
            ['6 Verify', 'Can the user do the thing they could not do before?', 'The user’s confirmation and the test that now passes', 'Closing on “the error went away” without the user'],
            ['7 Document', 'Could someone else understand and repeat this in six months?', 'Cause, fix, verification, prevention', 'Writing “fixed” and nothing else'],
        ]) + figure('f7-1', 'Seven-step troubleshooting cycle',
                    ['1 Identify', '2 Probable\ncause', '3 Test', '4 Plan +\nrollback', '5 Change\none thing', '6 Verify with\nthe user', '7 Document'],
                    'Seven boxes in order: Identify, Probable cause, Test, Plan with rollback, Change one thing, Verify with the user, '
                    'Document. An arrow leads from each box to the next. A return arrow runs from Test back to Probable cause, labelled '
                    '“theory disproved: next theory”, showing that a failed test sends you back to your list rather than forward to a change.',
                    'The method is a loop between theory and test until a test confirms a cause; only then do you plan and change anything.',
                    cols=4, loop=(2, 1, 'theory disproved → next theory')) + '''
<h3>Choosing the cheapest test that can kill a theory</h3>
<p>A good test is cheap (seconds, not hours), safe (it changes nothing, or changes something you can undo) and decisive
(either result tells you something). “Ping the default gateway” is a good test for “the PC has no network path”: a reply
proves layers 1–3 to the gateway, and no reply points at the link, the lease or the address. “Reinstall the network driver”
is a poor first test: it takes time, it changes the system and a success does not tell you what was wrong.</p>
<p>When a path has many parts, test in the middle first. If a user cannot open an internal web app, a test from their PC to the
app server by IP address splits the path in half: success means the network path works and the problem is name resolution
or the application; failure means the problem is between the PC and the server. This is <strong>divide and conquer</strong>
(also called half-splitting), and it usually beats working from one end.</p>
''' + worked('“Outlook won’t send”', '''
<ol>
<li><strong>Identify.</strong> One user, since 08:30. Mail arrives but messages stay in the Outbox. Webmail sends fine.
Nothing changed on the PC that the user knows of. Error text: “Your message could not be sent. The server is not responding.”</li>
<li><strong>Probable cause.</strong> (a) The Outlook profile or cached credentials are stale. (b) A local security tool is
blocking the client. (c) The mail service is down. Webmail working makes (c) unlikely, so it goes last.</li>
<li><strong>Test.</strong> Cheapest test for (a): sign out of Office and back in, then press Send/Receive. Result: same error.
Theory (a) is weakened, not proven wrong, so you note it and move on. Test for (b): check the security tool’s recent
events. Result: an entry at 08:27 blocking OUTLOOK.EXE outbound after a definitions update.</li>
<li><strong>Plan.</strong> Report the block to the security team, who own the tool; do not disable protection yourself. Rollback is
not needed for a report, but you note the time and event ID.</li>
<li><strong>Change one thing.</strong> The security team releases the rule for this client.</li>
<li><strong>Verify.</strong> The user sends a test message to a colleague, who confirms receipt. The Outbox is empty.</li>
<li><strong>Document.</strong> “Cause: endpoint protection rule (event 08:27) blocked Outlook outbound after definitions
update. Fix: rule released by Security (ticket SEC-1042). Verified: user sent and colleague received at 09:12.
Prevention: Security reviewing rule for other users.”</li>
</ol>
<p>Notice that the technician did not reinstall Office, did not rebuild the profile and did not turn off protection. The
cheap test pointed to an owner, and the owner made the change.</p>''') + scenario('the printer that was “fixed” three times', '''
<p>A front-desk printer was “fixed” three times in a week: each technician restarted it, saw a test page print and closed the
ticket. Each time the problem came back by the afternoon. The fourth technician identified the outcome properly: the
<em>user’s</em> jobs from the booking system failed, while test pages always worked. A test from the booking PC showed jobs
reaching the queue and then stalling. The probable cause was a driver mismatch on the print server after an update, not
the printer. Updating the queue’s driver (with approval and a rollback note) fixed it, and the user verified a real booking
receipt. Lesson: a test page proves the printer, not the user’s outcome.</p>''') + cfu(
            ('Why is “restart it and see” a weak first test even when it often works?',
             'It changes the system, destroys evidence (logs, error state) and, if it works, does not tell you the cause, so the fault is likely to return.'),
            ('A user cannot reach one internal site by name. Which single test splits the problem in half?',
             'Reach the same site by IP address (or test the port with Test-NetConnection). Success points to name resolution or the app; failure points to the path.'),
            ('What must a plan include before you change anything?',
             'What will change, what it could affect, how to undo it, and whether it needs approval.')),
    },
    (7, 2): {
        'objectives': [
            'Classify a symptom into a fault domain (power, hardware, boot/OS, account/profile, local network, name resolution, service, permissions)',
            'Determine scope by asking whether one user, one device, one application, one site or everyone is affected',
            'Choose the first proof test and the owning team for each fault domain',
        ],
        'html': sme_note() + '''
<h3>Fault domains: where could this break?</h3>
<p>A <strong>fault domain</strong> is the part of the system that could explain a symptom and that one team or one test can
prove or rule out. Naming the domain before choosing a tool stops you from running network commands on a PC that will not
power on, or editing DNS when the user’s password has expired. Most help-desk tickets fall into one of eight domains.</p>
''' + table(['Domain', 'Typical symptoms', 'First proof test', 'Usual owner'], [
            ['Power and safety', 'No lights, burning smell, swollen battery, tripped breaker', 'Known-good outlet and cable; stop on any safety hazard', 'Desk-side support; facilities for building power'],
            ['Hardware / POST', 'Beeps, no video, fans only, repeated reboot before Windows', 'Minimum-boot isolation (Chapter 2)', 'Desk-side support or vendor warranty'],
            ['Boot / OS', 'Boot loop, recovery screen, BitLocker recovery prompt, slow start', 'Does it reach the sign-in screen? Safe Mode? WinRE?', 'Desk-side or endpoint team'],
            ['Account / profile', 'Wrong password, locked out, temporary profile, missing desktop', 'Same user on another PC; another user on this PC', 'Service desk (identity) or endpoint team'],
            ['Local network', 'No network icon, APIPA 169.254.x.x, “No Internet”', 'ipconfig /all, ping gateway (Chapter 5 order)', 'Service desk, then network team'],
            ['Name resolution', 'Works by IP, fails by name; wrong site loads', 'nslookup / Resolve-DnsName against the configured DNS server', 'Network or server team'],
            ['Service / SaaS', 'Many users, one app; status page shows an incident', 'Provider status page; another network; another user', 'Application owner or provider'],
            ['Permissions / entitlement', '“Access denied”, folder visible but empty, licence error', 'Group membership and licence assignment', 'Identity or application owner'],
        ]) + '''
<h3>Scope comes before tools</h3>
<p>Scope is the fastest way to narrow the domain. Ask, or test, in this order: Is it only this user? Only this device? Only
this application? Only this location? Everyone? A single test often answers two questions at once: if the same user signs in
on a colleague’s PC and the problem follows them, the device is ruled out and the account or profile is ruled in.</p>
''' + figure('f7-2', 'Scoping questions narrow the fault domain',
             ['Symptom\nreported', 'Same user,\nother device?', 'Other user,\nsame device?', 'Same app,\nother users?', 'Domain\nnamed'],
             'Five boxes left to right. Symptom reported leads to the question “same user on another device?” — if the problem follows the '
             'user, suspect the account or profile. Next, “another user on the same device?” — if everyone fails on this device, suspect '
             'the device, its OS or its network connection. Next, “same app for other users?” — if many users fail, suspect the service or '
             'the provider. The last box, Domain named, means you can now choose a tool and an owner.',
             'Three scoping tests usually name the fault domain before any configuration is changed.', cols=5) + worked('“Teams won’t load”', '''
<p>A user reports that Teams shows a spinning circle. You ask two scope questions and run one test:</p>
<ul>
<li>Does Teams work in a browser on the same PC? <em>Yes.</em> So the network path and the account both work; the problem is the
desktop app on this device.</li>
<li>Do colleagues have the problem? <em>No.</em> Not a service outage.</li>
</ul>
<p>Domain: application on one device. First proof test: sign out of the app and clear its cache as the vendor documents, or run
the app’s repair. You did not touch DNS, the network adapter or the user’s password, because the scope already ruled those
out.</p>''') + scenario('Monday morning, a whole floor cannot print', '''
<p>At 08:05 twelve tickets arrive from the second floor: nobody can print. The first technician starts reinstalling drivers on
one PC. A second technician scopes first: all twelve users print to the same queue; users on other floors print fine; the
second-floor printer shows a static IP that now conflicts with a new device added over the weekend (the switch logs show a
duplicate address). Domain: local network, at the printer. Owner: network team for the address reservation. One fix, one
verification on three users’ PCs, one parent ticket with eleven linked children.</p>''') + cfu(
            ('A user is placed in a temporary profile on every PC they sign in to. Which domain?',
             'Account / profile — it follows the user across devices, so the device and network are ruled out.'),
            ('Many users at one site lose a SaaS app; users at home can still use it. What does that suggest?',
             'The site’s Internet path, proxy or DNS rather than the SaaS provider, because the service works from another network.'),
            ('Why record which team owns the domain?',
             'So the fix is made by the people with authority and tools to make it, and the ticket reaches them with the evidence attached.')),
    },
    (7, 3): {
        'objectives': [
            'Verify a fix by repeating the original failing test and confirming the user’s outcome with the user',
            'Apply a preventive measure or record why none applies',
            'Write closure notes that state cause, fix, verification and prevention',
            'Assemble an escalation package (impact, scope, evidence, actions → results, current state, request) and send status updates on a stated schedule',
        ],
        'html': sme_note() + '''
<h3>“Fixed” is a claim; “verified” is evidence</h3>
<p>A fix is verified when the outcome the user lost is back and the user agrees. Re-run the exact test that failed (the same
page, the same print job, the same sign-in) and ask the user to do the task while you watch or while they describe it. A
green icon, an empty error log or a successful test page is supporting evidence, not verification.</p>
<p>After verification, ask whether the problem can recur. A <strong>preventive measure</strong> might be correcting an address
reservation, adding a monitoring alert, updating a knowledge-base article or raising a problem record so the root cause is
investigated across many incidents. If none applies, say so in the notes.</p>
<h3>Closure notes another technician can use</h3>
''' + table(['Weak note', 'Strong note'], [
            ['“Fixed printer.”', '“Cause: duplicate IP 10.2.0.40 after new camera installed 12 Oct. Fix: network team moved camera to .41 (NET-311). Verified: user printed booking receipt 09:40. Prevention: printer IP now reserved in DHCP and labelled.”'],
            ['“Reset PW, ok now.”', '“Identity verified (callback to number on file). Account was locked after 10 failed attempts from an old phone mail profile. Unlocked, user removed the old profile. Verified: sign-in on laptop and phone at 14:05.”'],
            ['“Escalated to network.”', '“Escalated to Network (P2): VLAN 20 users on floor 3 get APIPA since 07:50; floor 2 unaffected; switch port Gi1/0/24 shows err-disabled. Tried: reseat uplink (no change). Need: port check.”'],
        ]) + '''
<h3>Escalating without starting over</h3>
<p>Escalation is not failure; it is handing work to the people who own the fix. A good escalation lets the next tier start at
step 3, not step 1. Use the same structure every time:</p>
<ol>
<li><strong>Impact and priority</strong> — who cannot do what, how many people, any deadline or safety concern.</li>
<li><strong>Scope</strong> — what works and what does not (the comparisons you made).</li>
<li><strong>Evidence</strong> — exact error text, times, screenshots, command output.</li>
<li><strong>Actions → results</strong> — everything you tried, including what did not help.</li>
<li><strong>Current state</strong> — anything you changed and whether it is still changed.</li>
<li><strong>Request</strong> — what you need from them.</li>
</ol>
<p>Tell the user what happens next and when they will hear from someone. A status update at an agreed interval (for example,
every 30 minutes during a high-impact incident) is better than silence, even when the update is “no change yet”.</p>
''' + figure('f7-3', 'Escalation path with evidence', ['Service desk\n(tier 1)', 'Escalation\npackage', 'Owning team\n(tier 2/3)', 'Fix +\nverify', 'Closure\nnotes'],
             'Five boxes in a row: Service desk tier 1 creates an Escalation package, which goes to the Owning team at tier 2 or 3. The '
             'owning team applies the fix and verification, then closure notes are written. The package carries impact, scope, evidence, '
             'actions with results, the current state and the request, so the owning team does not repeat the first-tier tests.',
             'Escalation moves the ticket and its evidence together; the user hears status updates throughout.', cols=5) + worked('rewriting an escalation', '''
<p>Original: “User can’t get on VPN, tried everything, please help.”</p>
<p>Rewritten: “P3 — one user (remote, home broadband) cannot connect to VPN since 07:30; colleagues connect normally. Error:
‘The remote connection was not made because the attempted VPN tunnels failed.’ Tried: restarted client (no change); home
Internet works (speed test 80 Mb/s); PC clock correct; same failure on mobile hotspot. Nothing changed on the PC. Request:
check the user’s VPN certificate or group assignment.” The second version rules out the home network and points the
identity team at the most likely cause.</p>''') + cfu(
            ('What is the difference between verification and a successful test page?',
             'Verification is the user’s own outcome restored and confirmed; a test page only proves one part of the path.'),
            ('List the six parts of an escalation package.',
             'Impact and priority, scope, evidence, actions → results, current state, request.'),
            ('When is a problem record useful?',
             'When the same cause produces repeated incidents and needs investigation beyond the current ticket.')),
    },
    (7, 4): {
        'objectives': [
            'Resolve a staged fault within a time box using the seven-step method and record every test',
            'Decide when to stop and escalate, and justify the decision from the evidence',
            'Communicate expectations and status to a user in plain language',
        ],
        'html': sme_note('Capstone drills, time boxes and communication guidance added in pass 9.') + '''
<h3>How the drills work</h3>
<p>Each drill gives you a ticket, a lab VM or desk scenario and a time box. You are graded on the method, not on guessing the
answer quickly: identify, a short theory list, cheap tests recorded as action → result, one change with a rollback, user
verification and closure notes. Stop and escalate if the time box expires or the evidence points to a domain you do not own.</p>
''' + table(['Drill', 'Ticket text', 'Time box', 'Expected path'], [
            ['A', '“Internet is down” (one user)', '15 min', 'Scope: one PC. ipconfig shows 169.254.x.x → lease failure. Check link and adapter state; renew lease; if still failing, escalate to network with the port and MAC.'],
            ['B', '“The shared drive is gone”', '15 min', 'Same user on another PC also fails → account. Group membership removed during a role change → identity team, with the change ticket number.'],
            ['C', '“My PC is slow since the update”', '20 min', 'Task Manager shows sustained disk 100 % from one process; Reliability Monitor shows a failed driver install; follow Chapter 11 isolation; no reinstall before evidence.'],
            ['D', '“Website says not secure”', '10 min', 'One site, many users → certificate expired on the server. Not a PC fault; escalate to the site owner with the certificate dates.'],
        ]) + '''
<h3>Knowing when to stop</h3>
<p>Escalate when any of these is true: the fix needs access or approval you do not have; the evidence points to a domain
another team owns; the time box has expired without a confirmed cause; the impact has grown (more users, safety, data loss
risk). Escalating early with good evidence is better practice than a late escalation after several untested changes.</p>
<h3>Talking to the user</h3>
<p>Set expectations at the start (“I’ll run a few quick checks — about ten minutes — and I’ll tell you what I find”), avoid
jargon, and never blame. If you need to escalate, tell the user who has the ticket now, what they need from the user, and
when the next update will come.</p>
''' + scenario('the drill that went wrong', '''
<p>In a practice round a student saw “Internet is down”, ran <code>netsh winsock reset</code> and <code>ipconfig /flushdns</code>,
rebooted, and the fault remained. The rubric marked the attempt as Developing: no identify notes, no scope, two changes with
no test in between, and the real cause (a disabled adapter) was visible in the first <code>ipconfig</code> output. The same
student, with the method, solved the next drill in six minutes.</p>''') + cfu(
            ('Drill B: the problem follows the user to another PC. What do you stop doing?',
             'Stop testing the original PC’s hardware, OS and network; the account or its permissions are now the domain.'),
            ('Give two reasons to escalate before the time box ends.',
             'You need access or approval you do not have, or the evidence points to a domain another team owns (also: impact has grown).'),
            ('What should you tell a user when you escalate?',
             'Who has the ticket now, what (if anything) is needed from them, and when they will next hear.')),
    },
}

GLOSSARY = [
    ('Fault domain', 'The part of a system (power, hardware, OS, account, network, name resolution, service, permissions) that could explain a symptom and that one test or team can prove or rule out.'),
    ('Divide and conquer (half-splitting)', 'Testing at the midpoint of a path first so each result rules out half of the remaining possibilities.'),
    ('Escalation package', 'The information handed to the next support tier: impact, scope, evidence, actions and results, current state and the request.'),
    ('Problem record', 'A record used to find and remove the underlying cause of one or more incidents.'),
    ('Time box', 'A fixed amount of time allowed for an activity before you stop and decide whether to escalate.'),
    ('Verification', 'Evidence that the user’s lost outcome is restored, confirmed by repeating the failing test with the user.'),
]

PLAN = {
    'warmup': 'Show the ticket “Outlook won’t send.” In pairs, write two theories and the cheapest test that would disprove each.',
    'guided': 'Walk the “Outlook won’t send” worked example step by step; students fill the seven-step worksheet. Then scope “Teams won’t load” with three questions before any tool is chosen.',
    'worked_example': 'Lesson 7.1 “Outlook won’t send” and lesson 7.3 “rewriting an escalation”.',
    'cfu': ['Which single test splits “can’t open the intranet by name” in half?',
            'A problem follows the user to another PC. Which fault domain is now most likely?',
            'Name the six parts of an escalation package.'],
    'exit_ticket': 'Rewrite the note “Escalated to network” as a full escalation package for the floor-3 APIPA scenario.',
    'misconceptions_add': ['“Escalating means I failed.” Escalation hands the fix to the owner; a good package is a skill that is graded.'],
    'classroom_lab': 'CL-7',
    'materials_add': 'Classroom lab CL-7 drill cards (A–D) and the ticket rubric.',
}

ITEMS = [
    item('IT-7.1', 1, 'You have three theories for a fault. Which test should you normally run first?',
         'The quick, safe test that could rule out the top theory', ['The test that changes the most settings at once', 'The slowest test, since it is the most thorough of them', 'A full reinstall, because it removes every theory in one go'],
         'Cheap, safe, decisive tests come first; a reinstall changes the system and does not reveal the cause.'),
    item('IT-7.1', 2, 'A technician updates a driver, swaps the cable and resets the adapter, and the fault clears. What is the main problem?',
         'Nobody can tell which change fixed the fault', ['The driver should always be updated as the last step', 'Cables should never be swapped by tier-1 staff', 'Adapter resets need a reboot to verify'],
         'Changing one thing at a time is what links the fix to the cause.'),
    item('IT-7.1', 3, 'Which ticket entry best records a test?',
         '“ping 10.1.1.1 from PC-22: 4 of 4 replies, 2 ms”', ['“Checked the network and it all looked fine to me”', '“Ran some tests, all good, moving on to DNS”', '“Network OK per user, so the ping test was skipped”'],
         'An action → result pair with the target and outcome can be repeated by someone else.'),
    item('IT-7.2', 1, 'A user gets a temporary profile on every PC they sign in to. Which fault domain is most likely?',
         'The user account or its roaming profile', ['The network adapter on the first PC they used', 'The DNS server for the building subnet', 'The power supply in the user’s desk PC'],
         'A symptom that follows the user across devices rules out the device and points to the account or profile.'),
    item('IT-7.2', 2, 'An app fails for many users at one site but works for staff at home. What should you suspect first?',
         'The site’s Internet path, proxy or DNS', ['Each user’s local application cache files', 'A fault in every user’s home router', 'The users’ keyboard and mouse drivers'],
         'Working from another network shows the service is up; the shared site path is the common factor.'),
    item('IT-7.2', 3, 'A site works by IP address but not by name. Which domain and first test fit best?',
         'Name resolution; query the configured DNS server', ['Power; try the PC on a known-good wall outlet', 'Hardware; reseat both of the memory modules', 'Account; reset the user’s password'],
         'Reachability by IP proves the path; failure by name points to DNS, tested with nslookup or Resolve-DnsName.'),
    item('IT-7.3', 1, 'Which evidence best verifies that a printing fault is fixed?',
         'The user prints the job that failed and confirms it', ['The printer prints its own test page again', 'The print spooler service shows as Running', 'No new errors appear in the event log for an hour'],
         'Verification repeats the failing outcome with the user; the other items are supporting evidence only.'),
    item('IT-7.3', 2, 'After fixing a duplicate-IP fault on a printer, which step is the preventive measure?',
         'Reserve the printer’s address in DHCP and label it', ['Restart the printer at the start of every working day', 'Ask users to report it again if it happens', 'Close the ticket once one job prints out'],
         'Prevention removes the cause of recurrence; restarts and waiting for reports do not.'),
    item('IT-7.3', 3, 'Which closure note is most useful to the next technician?',
         'Cause, fix, how it was verified and any prevention', ['Only the time spent and the user’s full name and desk', 'A thank-you message copied from the user', 'The word “fixed” and the closing date'],
         'Cause, fix, verification and prevention let someone else understand and repeat the work.'),
    item('IT-7.4', 1, 'Which escalation lets the next tier start without repeating your work?',
         'Impact, scope, evidence, actions tried and the request', ['“User still cannot connect, we tried everything here”', '“Urgent — please call the user back today”', '“Same as last week’s ticket, see that one”'],
         'A structured package carries the evidence forward so tier 2 can begin at the test step.'),
    item('IT-7.4', 2, 'When should you escalate before your time box ends?',
         'When the fix needs access or approval you lack', ['When the user asks how long the work will take you', 'When the first test result surprises you', 'When another ticket arrives in your queue'],
         'Lack of authority or a domain owned by another team are reasons to escalate early.'),
    item('IT-7.4', 3, 'During a high-impact outage, what should users hear while the owning team works?',
         'Status updates at an agreed interval, even if no change', ['Nothing until the fix has been confirmed by the owning team', 'A guess at the root cause to keep them calm', 'Instructions to restart their PCs every hour'],
         'Regular, honest updates manage expectations; guesses and silence both erode trust.'),
]

LABS = {
    'CL-7': {
        'id': 'CL-7', 'title': 'Structured troubleshooting drills on staged faults', 'chapters': [('ITSUP', 7)],
        'review': 'Pending SME review',
        'objective': 'Resolve staged faults with the seven-step method inside a time box, and escalate with a complete package when the fault is outside your domain.',
        'scenario': 'Four drill cards (A–D, lesson 7.4) each describe a user ticket. The instructor stages each fault on a lab VM or desk station before the session.',
        'prerequisites': ['Chapter 5 connectivity order', 'Lessons 7.1–7.3'],
        'equipment': 'One Windows 11 lab VM per pair (LMS win-full-triage works for drill A), printed drill cards, the seven-step worksheet and a timer.',
        'low_cost': 'Run drills A and D as tabletop exercises using printed command output; B and C as role-plays with an instructor acting as the user.',
        'steps': [
            'Read the drill card aloud to your partner, who plays the user. Ask identify questions and record the answers (outcome, scope, start time, changes, exact error).',
            'Write no more than three probable causes, each with the cheapest test that could disprove it.',
            'Run the tests in order and record each as action → result. Stop when a test confirms a cause.',
            'Write the plan, including rollback and whether approval is needed. Get the instructor’s approval for any change.',
            'Make one change, then repeat the original failing test.',
            'Verify with the “user” and write closure notes (cause, fix, verification, prevention).',
            'If the time box expires or the fault is outside your domain, write an escalation package instead and tell the “user” what happens next.',
            'Swap roles and repeat with the next drill card.',
        ],
        'expected': 'For each drill: identify notes, a theory list, tests recorded as action → result, one change with rollback, user verification and closure notes — or a complete escalation package (drill B and D faults belong to other teams).',
        'troubleshooting': ['If you have run three tests without narrowing the domain, go back to scope: one user, one device, one app, one site?',
                            'If a change did not help, undo it before trying the next one, and record both.'],
        'reflection': ['Which test in your drill ruled out the most possibilities, and why?',
                       'Where did you nearly skip a step, and what would that have cost?',
                       'Rewrite your weakest ticket note so another technician could act on it.'],
        'rubric': 'ticket', 'minutes': 60, 'objectives': ['IT-7.1', 'IT-7.2', 'IT-7.3', 'IT-7.4'],
    },
}
