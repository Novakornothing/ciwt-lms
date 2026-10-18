"""Explanation ladder — ITSUP chapter 1 (Professional Foundations & Workplace Safety). Pending SME review.

Worked example for docs/EXPLANATION_LADDER.md: lesson 1.1 is complete (every concept section is laddered, restated
with same_as, or skipped with a reason). Lessons 1.2-1.5 follow the same pattern.

Writing rules used here (see the guide): each rung explains the SAME idea as the original in a genuinely different
way (plain words / analogy / picture or trace / hands-on), adds no new course rules, and its checks ask the idea
in a new form rather than repeating the original's check.
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 1

L11 = 'Course lesson 1.1 “The Support Technician Role” (the original section), re-explained'
ITIL = 'AXELOS, ITIL 4 Foundation (2019): incident, service request and change practices'
APLUS = 'CompTIA A+ Core 1 (220-1201) and Core 2 (220-1202) exam objectives: hardware basics, operational procedures'

MISCONCEPTIONS = {
    'MC-L-IT1-RAM-KEEPS': {
        'obj': 'IT-1.1', 'label': 'Thinking memory (RAM) keeps your files after the power goes off, like storage does',
        'fix': 'RAM is short-term workspace that empties when power is gone; the disk or SSD keeps files.',
        'terms': ['memory', 'ram', 'storage', 'power'], 'source': L11 + '; ' + APLUS, 'review': 'Pending SME review'},
    'MC-L-IT1-ONE-BLOB': {
        'obj': 'IT-1.1', 'label': 'Treating “the computer is broken” as one thing instead of asking which layer failed',
        'fix': 'Split it: power, hardware start, operating system, one application, or the network path.',
        'terms': ['power', 'operating system', 'application', 'network'], 'source': L11, 'review': 'Pending SME review'},
    'MC-L-IT1-DRIVER-IS-APP': {
        'obj': 'IT-1.1', 'label': 'Confusing a driver with an application the user runs (or with the device itself)',
        'fix': 'A driver is a small program that lets the operating system talk to one specific device.',
        'terms': ['driver', 'device', 'operating system'], 'source': L11 + '; ' + APLUS, 'review': 'Pending SME review'},
    'MC-L-IT1-PART-FIRST': {
        'obj': 'IT-1.1', 'label': 'Opening a ticket with a part or technology name instead of the job the user cannot finish',
        'fix': 'The first sentence is the outcome the user needs (send the report, open the door), not a part name.',
        'terms': ['outcome', 'job', 'user'], 'source': L11, 'review': 'Pending SME review'},
    'MC-L-IT1-LOUD-IS-IMPACT': {
        'obj': 'IT-1.1', 'label': 'Judging impact by how loud, senior or upset the caller is',
        'fix': 'Impact is how many people cannot do the outcome and what happens if it stays broken.',
        'terms': ['impact', 'how many', 'consequence'], 'source': L11, 'review': 'Pending SME review'},
    'MC-L-IT1-HANDOFF-NUMBER': {
        'obj': 'IT-1.3', 'label': 'Escalating by passing on the ticket number without the facts the next person needs',
        'fix': 'Transfer understanding: who and how many, the exact symptom, when it started, each test and result, a clear ask.',
        'terms': ['escalate', 'handoff', 'tests', 'result'], 'source': L11, 'review': 'Pending SME review'},
    'MC-L-IT1-LABEL-FROZEN': {
        'obj': 'IT-1.1', 'label': 'Thinking a ticket’s label can never change once it is picked',
        'fix': 'Write the label that fits the facts now, and change it in the ticket when new facts arrive.',
        'terms': ['label', 'incident', 'break/fix'], 'source': L11 + '; ' + ITIL, 'review': 'Pending SME review'},
}

# reused course misconceptions (curriculum_v2/misconceptions.py)
REQ, SCOPE, CHG, HANDS = 'MC-IT1-REQ-AS-INC', 'MC-IT1-SCOPE-IGNORED', 'MC-IT1-CHANGE-AS-FIX', 'MC-IT1-HANDS-FIRST'
VAGUE, CLOSE, URGENT, SECRET = 'MC-IT1-VAGUE-NOTES', 'MC-IT1-CLOSE-EARLY', 'MC-IT1-URGENCY-OVER-ID', 'MC-IT1-SECRETS-IN-TICKET'
RAM, BLOB, DRV, PART = 'MC-L-IT1-RAM-KEEPS', 'MC-L-IT1-ONE-BLOB', 'MC-L-IT1-DRIVER-IS-APP', 'MC-L-IT1-PART-FIRST'
LOUD, HAND, FROZEN = 'MC-L-IT1-LOUD-IS-IMPACT', 'MC-L-IT1-HANDOFF-NUMBER', 'MC-L-IT1-LABEL-FROZEN'

SVG = 'viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" aria-label="{label}" class="ladder-svg"'


def svg(w, h, label, body):
    return f'<svg {SVG.format(w=w, h=h, label=label)}><title>{label}</title>{body}</svg>'


def box(x, y, w, h, text, sub=''):
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>'
    t += f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 6)}" text-anchor="middle" dominant-baseline="middle" fill="currentColor" font-size="14" font-weight="700">{text}</text>'
    if sub:
        t += f'<text x="{x + w / 2}" y="{y + h / 2 + 12}" text-anchor="middle" dominant-baseline="middle" fill="currentColor" font-size="12">{sub}</text>'
    return t


def arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="2"/>'
            f'<polygon points="{x2},{y2} {x2 - 7},{y2 - 5} {x2 - 7},{y2 + 5}" fill="currentColor" '
            f'transform="rotate({0 if y1 == y2 else 90} {x2} {y2})"/>')


LESSONS = {
    '1.1': {
        'start-here-if-you-have-never-done-this': skip(
            'Start here if you have never done this', 'orientation',
            'A welcome and reading instruction; it introduces the pictures that follow rather than teaching one.'),

        'what-a-computer-is-in-one-picture': section(
            'What a computer is, in one picture', 'IT-1.1',
            [check('A laptop loses power in the middle of an unsaved edit. Which part of the picture lost the edit?',
                   'Memory (RAM), the short-term workspace that empties when power is gone',
                   ['The SSD, because storage is wiped clean every time the laptop turns off',
                    'The CPU, because the brain keeps a copy of every file it has worked on'],
                   'Unsaved work lives in RAM, which empties without power. The SSD keeps saved files through a power '
                   'loss, and the CPU follows instructions; it is not where files are kept.', mc=[RAM, None])],
            plain('''<p>A computer has a few jobs, and each part does one of them.</p>
<ul><li><strong>Power</strong> comes in from the wall or the battery. No power, nothing else happens.</li>
<li><strong>The CPU</strong> is the part that follows instructions.</li>
<li><strong>Memory (RAM)</strong> is where the work you are doing right now sits. It forgets everything when the power goes off.</li>
<li><strong>Storage (a disk or SSD)</strong> keeps your files when the power is off.</li>
<li><strong>Screen, keyboard and mouse</strong> let a person talk to it.</li>
<li><strong>The network</strong> lets it talk to other computers.</li></ul>
<p>When something is wrong, ask which of these jobs is not happening. That one question is the whole idea.</p>''',
                  L11, [check('Which part keeps a saved file safe while the PC is switched off?',
                              'Storage: the disk or SSD',
                              ['Memory (RAM), because it holds what you work on', 'The CPU, because it runs the programs'],
                              'Storage is the long-term part that keeps files without power. RAM only holds current '
                              'work and empties at power-off; the CPU runs instructions and keeps no files.', mc=[RAM, None])]),
            analogy('''<p>Think of a small office.</p>
<p>The <strong>power</strong> is the building’s electricity: if it is off, nobody works. The <strong>CPU</strong> is the
clerk who follows the instructions on each form. <strong>RAM</strong> is the clerk’s desk: papers being worked on right
now are spread across it, and the cleaners clear it every night when the lights go out. <strong>Storage</strong> is the
filing cabinet: anything filed there is still there in the morning. The <strong>screen and keyboard</strong> are the
service window where customers hand in requests, and the <strong>network</strong> is the phone line to other offices.</p>
<p>If the lights are off, it does not matter how good the clerk is. If the clerk never arrives, the cabinet can be
perfect and still nothing gets done. That is why a technician asks which part of the office has stopped.</p>''',
                    L11 + ' (office analogy written for this rung)',
                    [check('In the office picture, a report left on the desk overnight is gone in the morning. What does that match?',
                           'Unsaved work in RAM is lost when the power goes off',
                           ['A failing SSD that quietly loses some saved files every night', 'A network fault on the phone line between the two offices'],
                           'The desk is RAM: it is cleared when the power goes off, so unsaved work disappears. The '
                           'filing cabinet (storage) would have kept it, and the phone line (network) is unrelated.',
                           mc=[RAM, BLOB])]),
            visual(svg(560, 190, 'Diagram: power feeds the CPU; the CPU works with RAM, storage, screen and keyboard, and the network',
                       box(10, 70, 90, 50, 'Power', 'wall / battery') + arrow(100, 95, 150, 95) + box(150, 70, 110, 50, 'CPU', 'follows steps')
                       + arrow(260, 95, 300, 95) + box(300, 10, 120, 46, 'RAM', 'empties at power off')
                       + box(300, 72, 120, 46, 'Storage', 'keeps files') + box(300, 134, 120, 46, 'Screen / keys', 'talk to people')
                       + box(440, 72, 110, 46, 'Network', 'other PCs') + arrow(420, 95, 440, 95)
                       + '<line x1="280" y1="33" x2="280" y2="157" stroke="currentColor" stroke-width="2"/>'
                       + '<line x1="280" y1="33" x2="300" y2="33" stroke="currentColor" stroke-width="2"/>'
                       + '<line x1="280" y1="157" x2="300" y2="157" stroke="currentColor" stroke-width="2"/>')
                   + '''<ol class="ladder-trace"><li>Is there power? If no light, fan or sound, stop here: that is the first job that failed.</li>
<li>Does the CPU start? A dark or beeping box with power usually means the start-up hardware.</li>
<li>Is the work in RAM or saved to storage? Unsaved work is lost at power-off; saved files are on the disk.</li>
<li>Can a person see and type? Then can it reach the network?</li></ol>''',
                   L11, [check('Following the trace, a PC shows no light, no fan and no sound. Where do you stop?',
                               'At step 1: power has not arrived',
                               ['At step 3: the files must be missing from storage', 'At step 4: the network is down'],
                               'With no light, fan or sound, power is the first job that failed, and nothing later in the '
                               'trace can be judged yet. Storage and network questions come only after the box starts.',
                               mc=[BLOB, BLOB])]),
            tryit('''<p>Sort each symptom into the part of the picture that is not doing its job. Say why out loud before you check.</p>''',
                  L11, [check('“My saved spreadsheet is still there, but the one I was typing when the battery died is gone.” Which part explains it?',
                              'RAM: it held the unsaved work and emptied at power loss',
                              ['Storage: the SSD deleted the newest file to save space', 'The network: the open file was really on another computer'],
                              'Saved work survived on storage, and only the unsaved work vanished, which is what RAM does '
                              'at power-off. Storage did its job, and nothing in the story involves the network.', mc=[RAM, BLOB])],
                  widget=sort('Which part of the picture is not doing its job?', {
                      'Power': ['No light, no fan, no sound when the button is pressed'],
                      'CPU / start-up hardware': ['Power light on, fans spin, screen stays dark and the box beeps'],
                      'RAM (workspace)': ['Unsaved typing disappears when the battery dies'],
                      'Storage': ['A saved file cannot be found after a restart'],
                      'Network': ['Everything works on the PC, but no website or shared folder opens']},
                      'Each symptom points at one job in the picture. Naming the job first tells you which chapter’s tools you need.'))),

        'what-software-is': section(
            'What software is', 'IT-1.1',
            [check('A new label printer is plugged in, but Windows cannot use it. Which kind of software is most likely missing?',
                   'The driver that lets the operating system talk to that printer',
                   ['A new operating system, because Windows cannot print', 'A new application, such as a different web browser'],
                   'A driver is the small program that teaches the operating system one device. Windows already prints '
                   'to other printers, so replacing the OS is wrong, and an application does not make a device work.',
                   mc=[BLOB, DRV])],
            plain('''<p>There are two halves to a computer. <strong>Hardware</strong> is the parts you can touch.
<strong>Software</strong> is the instructions that run on them.</p>
<ul><li>The <strong>operating system</strong> (Windows, macOS or Linux) is the main program. It starts first and runs everything else.</li>
<li>An <strong>application</strong> is a program a person uses to do a job, like Outlook or a browser.</li>
<li>A <strong>driver</strong> is a small helper program. It lets the operating system use one device, such as a printer or a network card.</li></ul>
<p>“The computer is broken” could mean the power, the start-up hardware, the operating system, one application, or the
network. Find out which one before you fix anything.</p>''',
                  L11, [check('Outlook will not open, but the browser, Word and the printer all work. What is the narrowest place to start?',
                              'One application: Outlook',
                              ['The operating system, because a program failed', 'The hardware, because something is broken'],
                              'Everything else runs, so the operating system and hardware are doing their jobs. Only one '
                              'application fails, which is the narrow, testable claim to start from.', mc=[BLOB, BLOB])]),
            analogy('''<p>Picture a theatre. The <strong>hardware</strong> is the building: stage, lights, seats. The
<strong>operating system</strong> is the stage manager who opens the building, turns on the lights and lets each show
go on. An <strong>application</strong> is one show, such as tonight’s play. A <strong>driver</strong> is the
interpreter the stage manager needs to work with one visiting specialist, like the lighting crew from another
country: without the interpreter, the crew is there but nobody can tell it what to do.</p>
<p>If one play is cancelled, you do not rebuild the theatre. If the lights will not take instructions, you look for
the interpreter. Asking “which part is failing?” keeps you from fixing the wrong thing.</p>''',
                    L11 + ' (theatre analogy written for this rung)',
                    [check('In the theatre picture, the visiting lighting crew is there but cannot be told what to do. What does that match?',
                           'A device with a missing or wrong driver',
                           ['A cancelled show, meaning one application failed', 'A closed building, meaning there is no power'],
                           'The crew (device) is present, but the interpreter (driver) is missing, so the operating '
                           'system cannot use it. A cancelled show is an application problem, and a closed building is power.',
                           mc=[DRV, BLOB])]),
            visual('''<ol class="ladder-trace"><li><strong>Firmware</strong> on the board starts first and checks the hardware.</li>
<li>It hands over to the <strong>operating system</strong>, which loads its <strong>drivers</strong>, one per device (network card, printer, display).</li>
<li>The person opens an <strong>application</strong>, which asks the operating system to print, save or connect.</li>
<li>The operating system uses the right <strong>driver</strong> to reach the device.</li></ol>
<p>Read the chain backwards when something fails: did the application ask, did the operating system have a driver, did the device answer?</p>''',
                   L11, [check('In the start-up chain, what runs before the operating system?',
                               'Firmware on the board',
                               ['The application the user opens first', 'The printer driver for the default printer'],
                               'Firmware starts first and hands over to the operating system. Drivers load as part of the '
                               'operating system, and applications only run after it is up.', mc=[DRV, None])]),
            tryit('<p>Sort each item into the right kind of software (or hardware). Then say which one you would check first if it failed.</p>',
                  L11, [check('Which item is a driver?', 'The program that lets Windows use one Wi-Fi card',
                              ['Microsoft Edge, the web browser that ships with Windows', 'The Wi-Fi card itself, the part on the motherboard'],
                              'A driver is the program between the operating system and one device. Edge is an '
                              'application, and the Wi-Fi card is hardware you can touch.', mc=[DRV, DRV])],
                  widget=sort('Hardware, operating system, application or driver?', {
                      'Hardware': ['SSD', 'Network card'],
                      'Operating system': ['Windows 11', 'macOS'],
                      'Application': ['Outlook', 'A web browser'],
                      'Driver': ['Printer driver', 'Wi-Fi card driver']},
                      'If you can touch it, it is hardware. The operating system runs everything; applications do a person’s job; drivers connect the OS to one device.'))),

        'what-a-user-actually-brings-you': section(
            'What a user actually brings you', 'IT-1.1',
            [check('A user says: “The badge reader is broken.” What should your first written sentence be about?',
                   'The job they cannot finish, such as getting into their space',
                   ['The badge reader’s model, serial number and firmware version', 'Which network layer and VLAN the badge reader is using'],
                   'Users bring a job they cannot finish, and the first sentence records that outcome. Model numbers and '
                   'network layers may matter later, but they are tools, not the problem statement.', mc=[PART, PART])],
            plain('''<p>Users do not arrive with a technical diagnosis. They arrive with something they cannot get done.</p>
<p>Examples: “My report will not send.” “My badge will not open the door.” “The printer will not print the watchbill.”</p>
<p>Write that job down first, in their words. Do not start with a part name like “NIC” or “server.” The job tells you
what “fixed” will look like.</p>''',
                  L11, [check('Which opening line follows this rule?', '“User cannot send the weekly report from Outlook.”',
                              ['“Possible NIC failure on the user’s desktop PC.”', '“Server issue, investigating with the server team.”'],
                              'The good line names the job the user cannot finish, so everyone knows what fixed means. '
                              'The other two are guesses about parts that may be wrong.', mc=[PART, PART])]),
            analogy('''<p>When you go to a mechanic, you do not say “your alternator’s diode has failed.” You say “my car will
not start in the morning.” A good mechanic writes that down, because it is what you need back: a car that starts.
The diode might be the cause, or it might be the battery or the starter. The sentence about the morning start stays
true whatever the cause turns out to be.</p>
<p>Your users are the same. Their sentence about the job they cannot do is the part of the ticket that stays true
while you test causes.</p>''', L11 + ' (mechanic analogy written for this rung)',
                    [check('Why does the mechanic write “car will not start in the morning” instead of a part name?',
                           'It is what the customer needs back, whatever the cause',
                           ['Customers usually know exactly which part has failed', 'Part names are not allowed anywhere on a repair order'],
                           'The outcome sentence is the stable goal and the test for “fixed.” Customers usually do not '
                           'know the failed part, and part names are fine later, once tested.', mc=[PART, None])]),
            visual('''<ol class="ladder-trace"><li><strong>Hear</strong> what the user says (“the printer is broken”).</li>
<li><strong>Ask</strong> what they were trying to get done (“print the watchbill before turnover”).</li>
<li><strong>Write</strong> that job as the first line of the ticket.</li>
<li><strong>Test</strong> causes later (paper, driver, network, queue), and check each one against that job.</li>
<li><strong>Close</strong> only when the job works again.</li></ol>''', L11,
                   [check('In the trace, what decides when the ticket can be closed?', 'The user’s job works again',
                           ['The part you suspected has been replaced', 'You have tested three possible causes'],
                           'The first line records the job, and the trace closes only when that job works. Replacing a '
                           'suspected part or running a set number of tests does not prove the user can work.', mc=[PART, CLOSE])]),
            tryit('<p>Rewrite each opening line so it names the job the user cannot finish. Commit to your version, then reveal one good answer.</p>',
                  L11, [check('Which rewrite of “VPN broken” follows the rule?', '“User cannot reach the shared drive from the hotel.”',
                              ['“VPN client fault suspected, reinstall planned.”', '“Network problem at the hotel, high priority.”'],
                              'The rewrite names what the user cannot do and where. The other two are a guess about a '
                              'part and a feeling about priority, which nobody can test.', mc=[PART, LOUD])],
                  widget=reveal('Rewrite: “The server is down again.”',
                                'For example: “Three users in the admin office cannot open the payroll folder since 0900.” It names the job, who and since when.'))),

        'what-a-ticket-is': section(
            'What a ticket is', 'IT-1.3',
            [check('You fixed a problem by phone but wrote nothing. Tomorrow it comes back to another technician. What does the shop know about your work?',
                   'Nothing: if it is not in the ticket, it did not happen',
                   ['Everything, because the user can repeat exactly what you did', 'Enough, because the ticket status says “resolved”'],
                   'The ticket is the shop’s written memory. Without notes the next technician starts at zero; the '
                   'user rarely knows what was tested, and a status word records no evidence.', mc=[VAGUE, CLOSE])],
            plain('''<p>A ticket is the shop’s memory, written down. People go home, sleep and change shifts. The ticket stays.</p>
<p>If something is not in the ticket, the next person cannot know it happened.</p>
<p>So write facts, not slogans. “VPN broken” is a slogan. Write who it affects, what they need, what you tested and
what each test showed, and who should act next.</p>''', L11,
                  [check('Which note is evidence rather than a slogan?', '“Ping to gateway 10.20.30.1 fails; LAN ping works.”',
                          ['“Network is bad today across the whole floor.”', '“User very upset, please fix ASAP, top priority.”'],
                          'The good note records an action and its result, which anyone can repeat. The others are an '
                          'opinion and a feeling, so the next person learns nothing they can test.', mc=[VAGUE, VAGUE])]),
            analogy('''<p>Think of a hospital patient chart. Nurses change shifts; the chart does not. A good chart says
what was given, when, and what happened next: “10:00, 500 mg paracetamol, temperature down to 37.5 by 11:00.” A chart
that says “patient seems unwell, doing stuff” is useless to the next nurse, and dangerous.</p>
<p>A ticket is the chart for a computer problem. The next technician reads it at two in the morning, with you asleep,
and has to know exactly what was done and what it showed.</p>''', L11 + ' (patient-chart analogy written for this rung)',
                    [check('In the chart analogy, what makes an entry useful to the next shift?',
                           'It says what was done and what happened next',
                           ['It says how worried the last nurse felt about the patient', 'It is short enough to read in one second at handover'],
                           'An action plus its result lets the next person continue without repeating work. Feelings '
                           'and brevity on their own give them nothing to act on.', mc=[VAGUE, VAGUE])]),
            visual('''<ol class="ladder-trace"><li><strong>Who</strong>: the person and how many are affected.</li>
<li><strong>Outcome</strong>: the job they cannot do.</li>
<li><strong>Test → result</strong>: each thing you tried, with what it showed.</li>
<li><strong>Change</strong>: anything you already altered.</li>
<li><strong>Next</strong>: the person or command that acts next.</li></ol>
<p>Five lines, in that order, turn a slogan into a ticket someone else can work.</p>''', L11,
                   [check('Which line in the trace stops the next technician repeating your tests?', 'Test → result',
                           ['Who is affected', 'Next person or command'],
                           'Recording each test with its result shows what is already known. “Who” and “Next” matter, '
                           'but they do not tell anyone which tests are done.', mc=[VAGUE, None])]),
            tryit('<p>Put these ticket lines in the order the next technician needs them.</p>',
                  L11, [check('A note says only “Fixed.” What is missing for the next shift?',
                              'What was tested and changed, and what each test showed',
                              ['Nothing; “Fixed” is enough when the user is happy', 'Only the exact time it was fixed and by whom'],
                              'Without tests and changes, nobody can tell what worked or undo it if it breaks again. A '
                              'happy user and a timestamp are not evidence of the fix.', mc=[CLOSE, VAGUE])],
                  widget=order('Order the lines of a usable ticket:', [
                      'Who is affected, and how many',
                      'The job they cannot do',
                      'Each test and its result',
                      'What you already changed',
                      'Who or what acts next'],
                      'Who → outcome → tests → changes → next. That order is how a stranger can continue your work.'))),

        'words-you-will-hear-this-week': skip(
            'Words you will hear this week', 'reference',
            'A vocabulary table; each term is taught (and laddered) in the concept section that uses it.'),

        '1-what-the-role-actually-delivers': section(
            '1. What the role actually delivers', 'IT-1.1',
            [check('A user cannot submit a form. Turning off the firewall would make it work in seconds. What does the role expect?',
                   'Restore the form without weakening security, and note it',
                   ['Turn off the firewall, because restoring service always comes first',
                    'Close the ticket, because the user can submit forms on another PC'],
                   'The role restores service while reducing risk and leaving a trail. Disabling security creates a '
                   'second problem, and another PC working does not restore this user’s job.', mc=[HANDS, CLOSE])],
            plain('''<p>On almost every contact you do four things:</p>
<ol><li><strong>Get the job working again</strong> (log in, print, send).</li>
<li><strong>Do not make things less safe</strong> to get there. No switching off security, no sharing admin passwords.</li>
<li><strong>Write it down</strong> so the next person can follow.</li>
<li><strong>Tell people</strong> what is happening and what you need.</li></ol>
<p>Users often say vague things like “the internet is down.” Your first task is to turn that into something you can
test, such as “this PC cannot open any website, but the shared drive works.”</p>''', L11,
                  [check('Which rewrite of “the internet is down” can be tested?',
                         '“This PC cannot open websites, but the shared drive works.”',
                         ['“The internet is down for everyone in the whole building.”', '“The network feels slow and keeps dropping out today.”'],
                         'A testable claim says what fails and what still works on which device. The other two repeat a '
                         'vague claim or a feeling with no test attached.', mc=[BLOB, PART])]),
            analogy('''<p>A good plumber called for a leak does four things. They stop the leak. They do not leave a gas pipe
loose to get at the water pipe. They write on the invoice what they replaced. And they tell you when the water can be
turned back on.</p>
<p>A plumber who fixes the leak but leaves the gas loose has made you less safe. One who leaves no invoice cannot be
followed by the next plumber. Support work is the same: fix, stay safe, write it down, communicate.</p>''',
                    L11 + ' (plumber analogy written for this rung)',
                    [check('In the plumber story, leaving the gas pipe loose to reach the water pipe matches which mistake?',
                           'Weakening security to restore service',
                           ['Writing too much on the invoice', 'Telling the customer when the water is back'],
                           'The loose gas pipe is a new risk created while fixing the first problem, like switching off '
                           'security. Notes and updates are two of the four duties, not mistakes.', mc=[HANDS, None])]),
            visual(svg(560, 120, 'Diagram: four duties on every contact: restore, stay safe, write it down, communicate',
                       box(5, 30, 130, 60, 'Restore', 'job works again') + box(145, 30, 130, 60, 'Stay safe', 'no new risk')
                       + box(285, 30, 130, 60, 'Write it down', 'trail for 0200') + box(425, 30, 130, 60, 'Communicate', 'status + ask'))
                   + '''<ol class="ladder-trace"><li>Ask: is the user’s job working again?</li><li>Did anything I did lower security?</li>
<li>Could a stranger follow my notes at 0200?</li><li>Do the user and my lead know the status and the next step?</li></ol>
<p>A contact is done well only when all four answers are yes.</p>''', L11,
                   [check('The job works and the notes are complete, but nobody told the user or the lead. Which duty is missing?',
                           'Communicate', ['Restore service', 'Stay safe'],
                           'The job working is “restore,” and nothing lowered security. The status update to the user '
                           'and lead is the communication duty, which was skipped.', mc=[CLOSE, None])]),
            tryit('<p>Sort each action into the duty it fulfils (or the duty it breaks).</p>',
                  L11, [check('Sharing the admin password with a user “so they can fix it next time” breaks which duty?',
                              'Stay safe: it creates a new security risk',
                              ['Write it down: it is not in the ticket', 'Restore: the problem is still there'],
                              'Handing out admin credentials lowers security for everyone, whatever the notes say. '
                              'Even if it is written down and the job works, it breaks the safety duty.', mc=[HANDS, VAGUE])],
                  widget=sort('Which duty does each action serve?', {
                      'Restore': ['User can print the watchbill again', 'Outlook sends mail after the profile fix'],
                      'Stay safe': ['Leave the firewall on and find the real cause', 'Do not share the admin password'],
                      'Write it down': ['Note each test and its result', 'Record what you changed'],
                      'Communicate': ['Tell the lead the next step', 'Tell the user what you need from them']},
                      'All four, every contact. A fix that skips one of them is not finished.'))),

        '2-three-kinds-of-work': section(
            '2. Three kinds of work', 'IT-1.1',
            [check('“I have never had access to the budget share and I need it today.” What kind of work is it?',
                   'A service request: something new is being asked for',
                   ['Break/fix, because the share does not work for them', 'An incident, because they need it today'],
                   'They never had the access, so nothing broke: it is a request that needs entitlement and approval. '
                   'Needing it today is urgency, which does not make it an incident.', mc=[REQ, LOUD])],
            plain('''<p>Every ticket gets a label. The label decides who approves, how fast you must act and who must be told.</p>
<ul><li><strong>Break/fix</strong>: it used to work and now it does not.</li>
<li><strong>Service request</strong>: they want something they never had.</li>
<li><strong>Incident</strong>: many people, an important service, or safety or security is involved.</li></ul>
<p>Pick the label before you touch a keyboard. If two labels seem right, pick the riskier one: incident beats break/fix.</p>''',
                  L11, [check('“Outlook worked yesterday; today it keeps asking for my password.” One user. Which label?',
                              'Break/fix', ['Service request', 'Incident'],
                              'It worked before and stopped, for one person, with no safety or security sign: that is '
                              'break/fix. Nothing new is requested, and one user is not an incident.', mc=[REQ, SCOPE])]),
            analogy('''<p>Think of a hotel front desk. A guest whose room key stopped working is <strong>break/fix</strong>:
it worked, now it does not, so you fix it. A guest asking for a late checkout they were not booked for is a
<strong>service request</strong>: something new, which may need a manager’s yes. A fire alarm on the third floor is an
<strong>incident</strong>: many people and safety, so you stop routine work, follow the plan and call the right people.</p>
<p>The desk clerk treats each one differently because the label changes who must approve and how fast to act.</p>''',
                    L11 + '; ' + ITIL + ' (hotel analogy written for this rung)',
                    [check('In the hotel story, what makes the fire alarm an incident rather than break/fix?',
                           'Many people and safety are involved',
                           ['The alarm used to work and now it is ringing', 'A guest asked for it'],
                           'Scale and safety make it an incident that changes everyone’s priorities. “Used to work” '
                           'describes break/fix, and a guest asking describes a request.', mc=[SCOPE, REQ])]),
            visual(svg(560, 210, 'Decision diagram: safety, security or many users means incident; never had it means service request; used to work means break/fix',
                       box(170, 5, 220, 44, 'Safety, security or many?') + box(420, 5, 130, 44, 'Incident')
                       + arrow(390, 27, 420, 27) + '<text x="405" y="18" text-anchor="middle" fill="currentColor" font-size="11">yes</text>'
                       + box(170, 80, 220, 44, 'Did they ever have it?') + arrow(280, 49, 280, 80)
                       + '<text x="292" y="68" fill="currentColor" font-size="11">no</text>'
                       + box(420, 80, 130, 44, 'Service request') + arrow(390, 102, 420, 102)
                       + '<text x="405" y="93" text-anchor="middle" fill="currentColor" font-size="11">no</text>'
                       + box(170, 155, 220, 44, 'It used to work') + arrow(280, 124, 280, 155)
                       + '<text x="292" y="143" fill="currentColor" font-size="11">yes</text>'
                       + box(420, 155, 130, 44, 'Break/fix') + arrow(390, 177, 420, 177))
                   + '<p>Ask the questions top to bottom. The first “yes” on the top box wins, which is why incident beats break/fix.</p>',
                   L11, [check('Following the diagram, “Someone sent mail as me” goes where first?',
                               'Incident: security is in the path', ['Break/fix: mail used to work', 'Service request: they want it stopped'],
                               'The first question is safety, security or many users, and mail sent as someone else is '
                               'a security sign, so it is an incident until proven otherwise. The lower boxes are never reached.',
                               mc=[SCOPE, REQ])]),
            tryit('<p>Sort each contact into its label. If two seem true, choose the higher-risk one. Then try the same sorting in the intake lab.</p>',
                  L11, [check('Which contact is an incident?', '“Half the building cannot badge in.”',
                              ['“I need Adobe installed on my new PC.”', '“My mouse stopped working this morning.”'],
                              'Many people losing access is an incident. Adobe on a new PC is a request, and one broken '
                              'mouse is break/fix for one user.', mc=[SCOPE, REQ])],
                  widget=sort('Break/fix, service request or incident?', {
                      'Break/fix': ['Outlook worked yesterday; today it loops on the password', 'My mouse stopped working this morning'],
                      'Service request': ['I need the budget share for the first time', 'Please install Adobe on my new PC'],
                      'Incident': ['Half the building cannot badge in', 'Someone sent mail as me']},
                      'Used to work → break/fix. Never had it → request. Many people, safety or security → incident.'),
                  lab={'id': 'ticket-intake', 'note': 'Use classify break-fix, classify request or classify incident on the lab ticket.'})),

        '3-impact-and-identity': section(
            '3. Impact and identity', 'IT-1.4',
            [check('A caller you cannot verify says: “I’m the director, reset my password now, we’ll sort it out later.” What do you do?',
                   'Run the identity script; if it is not completed, do not reset',
                   ['Reset it, because a director’s account is always high impact', 'Reset it now, then verify their identity once the call ends'],
                   'A reset is a privileged change, so identity comes first, whoever claims to be calling. Seniority '
                   'and urgency are not proof, and verifying afterwards means a stranger may already have the account.',
                   mc=[URGENT, URGENT])],
            plain('''<p><strong>Impact</strong> means how many people are affected and how bad it is if you wait. It is
not how loud or angry the caller is. Write down both the number and what happens.</p>
<p><strong>Identity</strong>: before you reset a password, unlock an account or open someone’s mailbox, make sure you
are talking to the right person. Use your shop’s method, such as calling back on a listed number or checking a badge.</p>
<p>If an unknown caller says “just do it,” the answer is no.</p>''', L11,
                  [check('Which is a correct impact statement?', '“14 users in Bldg 3 cannot badge in; turnover in 20 min.”',
                         ['“Priority high, caller very upset and asking for a manager.”', '“The director called personally about this, twice.”'],
                         'Impact is a count plus a consequence. The other two describe the caller’s mood and rank, which '
                         'do not tell the next person how many are blocked or what happens next.', mc=[LOUD, LOUD])]),
            analogy('''<p>A bank teller handles both ideas every day. <strong>Impact</strong>: a queue of forty people
because the cash machine is broken matters more than one loud customer, because more people are blocked. A teller
who serves whoever shouts loudest gets the order wrong.</p>
<p><strong>Identity</strong>: before handing over money from an account, the teller checks the person really owns it,
even when they are friendly and in a hurry. “I’ll show my ID tomorrow” gets a polite no. A password reset is handing
over the account, so it gets the same check.</p>''', L11 + ' (bank analogy written for this rung)',
                    [check('In the bank story, why does the teller refuse “I’ll show my ID tomorrow”?',
                           'Handing over the account unproven could give it to a stranger',
                           ['The customer was not loud enough to count as high impact', 'Banks never serve customers who are in a hurry to leave'],
                           'The check exists because a friendly, hurried voice can be anyone. Loudness is about impact, '
                           'not identity, and hurry is not a reason to refuse or to skip the check.', mc=[URGENT, LOUD])]),
            visual('''<ol class="ladder-trace"><li><strong>Count</strong>: how many people cannot do the job? Write the number.</li>
<li><strong>Consequence</strong>: what happens if it stays broken (turnover, payroll, medical, comms)?</li>
<li><strong>Privileged?</strong> Does the fix change an account (reset, unlock, share, mailbox)? If no, go on working.</li>
<li><strong>If yes, verify</strong> with the shop script (listed callback, ID, badge, supervisor).</li>
<li><strong>Script not completed?</strong> Do not make the change. Write “identity not verified; reset refused” as a fact.</li>
<li><strong>Write how you verified</strong>, never the password itself.</li></ol>''', L11,
                   [check('After a verified reset, what goes in the ticket?', '“Verified by callback to listed desk number; password reset.”',
                           ['The new password, so the next shift can help the user', 'Nothing, because password resets are routine and expected'],
                           'Write how identity was verified and what was done, never the secret. A password in the '
                           'ticket exposes the account, and writing nothing breaks the trail.', mc=[SECRET, VAGUE])]),
            tryit('<p>Put the steps of a safe account change in order, then try a reveal: decide what you would say to the caller.</p>',
                  L11, [check('A friendly caller fails the callback check but knows the user’s birthday. What now?',
                              'No reset; record that identity was not verified',
                              ['Reset, because knowing the birthday proves who they are', 'Reset, but ask them to change it later'],
                              'Only the shop’s script verifies identity, and it was not completed. A birthday is easy to '
                              'find, and resetting “for now” hands over the account anyway.', mc=[URGENT, URGENT])],
                  widget=order('Order the steps for a password reset request:', [
                      'Write down how many people are affected and what is blocked',
                      'Notice that a reset is a privileged change',
                      'Run the shop identity script (listed callback, ID, badge)',
                      'Reset only if the script was completed',
                      'Write how you verified, never the password'],
                      'Impact first, then identity before any privileged change, then a note with no secrets in it.'))),

        '4-keep-it-or-escalate': section(
            '4. Keep it or escalate', 'IT-1.3',
            [check('You escalate a VPN ticket to the network team. Which handoff lets them start working straight away?',
                   '“Client 4.2.1, error 809, gateway ping fails, since weekend update.”',
                   ['“Ticket 4471, VPN not working for this user, please take over.”', '“User needs VPN urgently for a briefing, very unhappy, call them.”'],
                   'The good handoff transfers understanding: version, error, tests with results, when it started and '
                   'where. A ticket number or a mood leaves the next person to start from zero.', mc=[HAND, LOUD])],
            plain('''<p>Sometimes you must pass a ticket on. That is called <strong>escalating</strong>.</p>
<p>Escalate when you lack the access, the tools, the permission or the skill. Escalate when safety or security needs a specialist.</p>
<p>Pass on what you know, not just the ticket number. Say who is affected and how many. Give the exact symptom.
Say when it started and what changed. List each test and its result. End with what you need the next person to do.</p>''', L11,
                  [check('When should you escalate rather than keep a ticket?', 'When you lack the access, tools, authority or skill',
                         ['When the user is impatient or asks for someone more senior', 'Whenever a ticket takes more than five minutes'],
                         'Escalation follows what the work needs that you cannot provide. Impatience and elapsed time on '
                         'their own are not reasons to hand over work you can finish.', mc=[LOUD, None])]),
            analogy('''<p>Think of a relay race. Handing over the baton is not the hard part; handing it over without
dropping it is. A runner who throws the baton at the next runner’s feet has technically passed it on, but the team has
lost time.</p>
<p>A ticket number alone is a thrown baton. A good handoff puts it in the next runner’s hand at full speed: the facts,
the tests already run and what they showed, so they do not repeat your lap.</p>''', L11 + ' (relay analogy written for this rung)',
                    [check('In the relay picture, what is a “dropped baton” in support work?',
                           'Escalating with only a ticket number, so tests get repeated',
                           ['Escalating at all, instead of finishing the ticket alone', 'Writing every test and its result into the handoff note'],
                           'The dropped baton is a handoff that loses what you learned. Escalating is correct when you '
                           'lack access or skill, and tests with results are exactly what keeps the baton in hand.',
                           mc=[HAND, VAGUE])]),
            visual('''<ol class="ladder-trace"><li>Can I finish this with my access, tools and authority? If yes, keep it.</li>
<li>Is there a safety or security sign? If yes, escalate now.</li>
<li>Before escalating, write: who and how many · exact symptom · when it started and what changed · where they are.</li>
<li>Add each test and its result, one per line.</li>
<li>End with a clear ask: what you need the next person to do.</li></ol>''', L11,
                   [check('In the trace, what must a handoff end with?', 'A clear ask for the next person',
                           ['An apology for escalating the ticket', 'The ticket number, repeated for clarity'],
                           'A clear ask tells the receiver exactly what is expected so nothing waits on guesswork. An '
                           'apology or a repeated number adds nothing they can act on.', mc=[HAND, HAND])]),
            tryit('<p>Put the handoff lines in order, then compare your version with Ticket B in the intake lab.</p>',
                  L11, [check('Ticket A says “VPN not working.” Ticket B lists the client version, error 809 and two ping results. Why can only B be worked?',
                              'B records tests and results, so work continues where you stopped',
                              ['B is longer, and longer tickets are always the better tickets', 'A is missing the user’s phone number and their office location'],
                              'B transfers what is already known, so work continues instead of restarting. Length alone '
                              'does not help, and a phone number does not tell anyone what was tested.', mc=[HAND, VAGUE])],
                  widget=order('Order a usable handoff:', [
                      'Who is affected and how many',
                      'The exact symptom or error',
                      'When it started and what changed',
                      'Each test and its result',
                      'The clear ask for the next person'],
                      'If the receiver can start without calling you, the handoff worked.'),
                  lab={'id': 'ticket-intake', 'note': 'Write a handoff note for the lab ticket and compare it with the pass bar in 1.5.'})),

        '5-closing-is-not-the-same-as-fixed': section(
            '5. Closing is not the same as fixed', 'IT-1.3',
            [check('The monitoring icon turned green, but the user still cannot submit the form they called about. Can you close?',
                   'No: closed means the workflow works and the notes are complete',
                   ['Yes, because the green icon shows the service is up and healthy', 'Yes, if the SLA resolve time is nearly up and the lead agrees'],
                   'Closing needs the required workflow verified with the user plus complete notes. A green icon is a '
                   'signal, not proof, and an SLA target is never permission to close early.', mc=[CLOSE, CLOSE])],
            plain('''<p>You may close a ticket only when two things are true: the job the user needed works again, and
your notes are complete.</p>
<p>A green light on a monitor is not enough. The user going quiet is not enough. Ask the user to try the exact thing
they called about. If it works, write that down, then close.</p>''', L11,
                  [check('Which is the best reason to close a ticket?', 'The user submitted the form while you watched; notes complete',
                         ['The user stopped replying to messages for two working days', 'The server dashboard shows all green for the whole morning'],
                         'Watching the user complete the job verifies the fix, and complete notes finish the record. '
                         'Silence and dashboards are signals that can be wrong.', mc=[CLOSE, CLOSE])]),
            analogy('''<p>A car is not fixed because the warning light went off. The mechanic test-drives it, on the same
road where the noise happened, before handing back the keys. The warning light can go dark while the brakes still
squeal.</p>
<p>Closing a ticket is handing back the keys. Do the test drive first: the user tries the exact task they called
about.</p>''', L11 + ' (test-drive analogy written for this rung)',
                    [check('What is the “test drive” before closing a ticket?', 'The user tries the exact task they called about',
                           ['You check that the warning icon on the dashboard is off', 'You restart the PC one more time to clear any leftovers'],
                           'The test drive is the real task under real conditions. An icon going off and a restart do '
                           'not show the user can now do their job.', mc=[CLOSE, None])]),
            visual('''<ol class="ladder-trace"><li>Fix applied.</li><li>Ask the user to repeat the exact task (submit the form, send the report).</li>
<li>Did it work? If no, the ticket stays open: write the result and keep going.</li>
<li>If yes, write the verification (“user submitted form 12 at 1410”).</li>
<li>Notes complete? Then close.</li></ol>''', L11,
                   [check('In the trace, the user’s task fails after your fix. What happens to the ticket?',
                           'It stays open, and you write the result',
                           ['It closes, because a fix was applied as planned', 'It closes, and you open a fresh ticket for the new failure'],
                           'The ticket follows the user’s outcome, which still fails, so it stays open with the new '
                           'result recorded. Applying a fix is not the same as fixing the problem.', mc=[CLOSE, CLOSE])]),
            tryit('<p>Sort each signal: is it enough to close, or not enough?</p>',
                  L11, [check('The user says “I think it’s fine now” without trying. What do you do?',
                              'Ask them to try the task now; close only if it works',
                              ['Close the ticket, because the user said it is fine', 'Leave it open for another week, just in case it fails'],
                              'Their guess is not a test, so verify with the real task first. Leaving tickets open forever '
                              'is the opposite mistake and hides real work.', mc=[CLOSE, None])],
                  widget=sort('Enough to close?', {
                      'Enough (with complete notes)': ['User submitted the form while you watched', 'User sent the report and confirmed it arrived'],
                      'Not enough': ['Monitoring icon is green', 'User stopped answering', 'The SLA timer is almost up']},
                      'Only the user’s real task, verified, plus complete notes closes a ticket.'))),

        '6-desk-drill-paper-first': skip(
            '6. Desk drill — paper first', 'activity',
            'A practice table students fill in for three contacts; the concepts it uses are laddered in sections 2-5.'),

        'what-this-job-actually-is': same_as(
            '1-what-the-role-actually-delivers', 'What this job actually is',
            'Restates the role (restore a required outcome) and the labels at more depth; uses the section 1 ladder.'),
        'worked-contacts': same_as(
            '2-three-kinds-of-work', 'Worked contacts', 'Worked examples of the three labels; uses the section 2 ladder.'),
        'identity-before-any-reset': same_as(
            '3-impact-and-identity', 'Identity before any reset', 'Identity before a privileged change; uses the section 3 ladder.'),
        'hour-plan-for-1-1': skip('Hour plan for 1.1', 'plan', 'The minute-by-minute teaching plan for the 90-minute lesson.'),
        'what-you-are-paid-to-restore': same_as(
            '1-what-the-role-actually-delivers', 'What you are paid to restore',
            'Restores the outcome idea with more examples; uses the section 1 ladder.'),

        'the-four-labels-and-what-changes-when-you-pick-one': section(
            'The four labels and what changes when you pick one', 'IT-1.1',
            [check('“Please add a DNS record in production after 1500 so the vendor demo works.” Which label?',
                   'Change: it goes through the shop’s change process',
                   ['Break/fix, because the vendor demo does not work yet', 'Service request, so you can add it straight away'],
                   'Adding a record alters a production system, so it is a change with process, rollback and a window. '
                   'Nothing broke, and treating it as a quick request skips the change controls.', mc=[CHG, REQ])],
            plain('''<p>There are four labels. Each one tells you what to do first:</p>
<ul><li><strong>Service request</strong> (they never had it): check who is allowed to have it.</li>
<li><strong>Break/fix</strong> (it used to work): ask when it last worked and what changed.</li>
<li><strong>Incident</strong> (many people, safety, security, or a critical service): stop, find the scope, escalate.</li>
<li><strong>Change</strong> (you will add or alter something): follow the shop’s change process, with a way to undo it.</li></ul>
<p>A label can change. “Printer down” is break/fix for one desk, but an incident if it is the only printer a watch needs in 20 minutes.
Write the label you are using now, and update it when the facts change.</p>''', L11,
                  [check('One floor printer jams, but two others on the floor work. Later you learn it is the only printer for the watch starting in 15 minutes. What happens to the label?',
                         'It moves up to incident (impact many) and you note why',
                         ['It stays break/fix, because labels never change once picked', 'It becomes a change, because you will alter the printer'],
                         'New facts raised the impact: the watch depends on that printer, so the label moves up and the '
                         'ticket says so. Labels follow facts, and fixing a jam is not a change.', mc=[FROZEN, CHG])]),
            analogy('''<p>A weather forecast is a label for tomorrow. Forecasters do not keep yesterday’s “sunny” when
radar shows a storm coming; they update it and tell people, because the label decides what everyone does (cancel the
picnic, close the harbour).</p>
<p>Ticket labels work the same way. The label is your best reading of the facts now. When a new fact arrives
(“it is the only printer for the watch”), update the label so everyone acts on the real situation.</p>''',
                    L11 + '; ' + ITIL + ' (forecast analogy written for this rung)',
                    [check('In the forecast picture, why do forecasters change “sunny” to “storm”?',
                           'New facts arrived, and the label drives what people do',
                           ['Labels should never change once they have been published', 'Storms are more interesting to report than sunshine'],
                           'A label is a reading of current facts that drives action, so it must follow new facts. '
                           'Keeping an outdated label sends people the wrong way.', mc=[FROZEN, None])]),
            visual(svg(560, 150, 'Diagram: the same printer ticket moves from break/fix to incident when a new fact arrives',
                       box(10, 45, 160, 60, 'Break/fix', 'one desk, jam') + arrow(170, 75, 220, 75)
                       + box(220, 45, 150, 60, 'New fact', 'only printer for watch') + arrow(370, 75, 410, 75)
                       + box(410, 45, 140, 60, 'Incident', 'impact many'))
                   + '''<ol class="ladder-trace"><li>Label from the facts you have (one jammed printer, other printers work → break/fix).</li>
<li>A new fact arrives (the watch can only use this printer, turnover in 15 minutes).</li>
<li>Re-label (incident or at least impact many) and write why in the ticket.</li>
<li>For a <em>change</em> (adding or altering something), the first step is always the change process, never a silent edit.</li></ol>''',
                   L11, [check('Which request must go through the change process?', 'Adding a production DNS record for a vendor demo',
                                ['Clearing a paper jam on the floor printer', 'Resetting a verified user’s password after a callback'],
                                'Adding a record alters a shared production system, which is a change with rollback and a '
                                'window. Clearing a jam restores a known-good state, and a verified reset is routine work.',
                                mc=[CHG, CHG])]),
            tryit('<p>Sort each contact into one of the four labels.</p>',
                  L11, [check('“I just added the DNS record after 1500” appears in a break/fix ticket. What went wrong?',
                              'A change was made silently, outside the change process',
                              ['Nothing, because the new record fixed the demo problem', 'The ticket should have been opened as an incident instead'],
                              'Adding a record is a change, which needs the process and a rollback plan even if it '
                              'helps. Calling it a repair hides the change from the people who must know.', mc=[CHG, SCOPE])],
                  widget=sort('Which of the four labels?', {
                      'Service request': ['New hire needs the budget share'],
                      'Break/fix': ['Outlook password loop since 0700, next desk fine'],
                      'Incident': ['Half the building cannot badge; reader is warm'],
                      'Change': ['Add a production DNS record for a vendor demo']},
                      'Never had it, used to work, many/safety/security, or you will alter something: each label has a different first step.'))),

        'impact-is-a-count-plus-a-consequence': same_as(
            '3-impact-and-identity', 'Impact is a count plus a consequence', 'The impact half of section 3; uses the section 3 ladder.'),
        'desk-set-classify-these-out-loud': skip(
            'Desk set — classify these out loud', 'activity',
            'Eight practice contacts to classify aloud; the labels are laddered in sections 2 and 4.'),
        'identity-before-any-account-change': same_as(
            '3-impact-and-identity', 'Identity before any account change', 'The identity half of section 3; uses the section 3 ladder.'),
        'handoff-that-survives-0200': same_as(
            '4-keep-it-or-escalate', 'Handoff that survives 0200', 'The five-line handoff; uses the section 4 ladder.'),
    },
}
STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '1.1': {'what-a-computer-is-in-one-picture': '6cf351a62dc2', 'what-software-is': '7eccaef03c95', 'what-a-user-actually-brings-you': '80f7ff00d4a9', 'what-a-ticket-is': '1cf538229cd9', '1-what-the-role-actually-delivers': 'fe1e118e5935', '2-three-kinds-of-work': '2aabfe03c73e', '3-impact-and-identity': '0981e922024d', '4-keep-it-or-escalate': '8ad8cdf0ad6b', '5-closing-is-not-the-same-as-fixed': '8b39ff26fadf', 'the-four-labels-and-what-changes-when-you-pick-one': '3495081978d8'},
}
