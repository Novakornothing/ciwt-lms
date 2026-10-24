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
                   ['A new operating system, because Windows cannot print', 'A newer application version, such as the latest Office build'],
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

# ---------------------------------------------------------------- content branch, round 2 (pass 19b): every element
# Lessons 1.1 (the sections the worked example skipped or restated) and 1.2-1.5, laddered by the content branch.
# Each section gets its own R1-R4 written for that section's emphasis. Pending SME review.
from curriculum_v2.ladder.netops._kit import C, lad, ol, ul
from curriculum_v2.ladder.netops._draw import text

L12 = 'Course lesson 1.2 “Workplace and ESD Safety” (the original section), re-explained'
L13 = 'Course lesson 1.3 “Ticketing, Documentation, and Change Awareness” (the original section), re-explained'
L14 = 'Course lesson 1.4 “Professional Communication and Privacy” (the original section), re-explained'
L15 = 'Course lesson 1.5 “Capstone — Safe Intake Workflow” (the original section), re-explained'
ESDS = 'ANSI/ESD S20.20 (ESD control programme); OSHA materials-handling guidance; NIOSH Revised Lifting Equation; NFPA 10 (extinguisher classes)'
_RV = 'Pending SME review'

MISCONCEPTIONS.update({
    'MC-L-IT1-NEW-IS-BEHIND': {
        'obj': 'IT-1.1', 'label': 'Believing a beginner must already know hardware words before starting support work',
        'fix': 'The course builds the pictures from zero; what matters is reading slowly and asking what each word means.',
        'terms': ['beginner', 'motherboard', 'ticket'], 'source': L11, 'review': _RV},
    'MC-L-IT1-WORD-MIX': {
        'obj': 'IT-1.1', 'label': 'Mixing up the week-one words (outcome, break/fix, request, incident, escalate, firmware, POST, ESD)',
        'fix': 'Each word names one thing: the job to restore, a label, a hand-off, or a piece of start-up or safety vocabulary.',
        'terms': ['outcome', 'escalate', 'firmware', 'post', 'esd'], 'source': L11, 'review': _RV},
    'MC-L-IT1-EMPTY-CELL': {
        'obj': 'IT-1.3', 'label': 'Thinking a drill table is fine with blank cells or vague next steps like “look into it”',
        'fix': 'Every cell is filled; the next step names a person or a command.',
        'terms': ['drill', 'next step', 'table'], 'source': L11, 'review': _RV},
    'MC-L-IT1-PLAN-IS-BRIEFING': {
        'obj': 'IT-1.1', 'label': 'Treating the 90-minute lesson as a quick briefing to skim',
        'fix': 'Each block is practice: say it, classify it, role-play identity, write a note, hand off out loud.',
        'terms': ['hour plan', 'practice'], 'source': L11, 'review': _RV},
    'MC-L-IT1-WRITE-SECRET': {
        'obj': 'IT-1.4', 'label': 'Writing the verification answer or a password in the ticket as proof of identity',
        'fix': 'Write how you verified (e.g. callback to the listed number), never the secret, old or new password.',
        'terms': ['verify', 'callback', 'password', 'ticket'], 'source': L11, 'review': _RV},
})

MISS1, SHOCK, TBI, FIFO = 'MC-C-IT1-REQ-VS-INC', 'MC-IT1-SHOCK-AS-SWAP', 'MC-IT1-TEST-BEFORE-INTAKE', 'MC-C-IT1-PRIORITY-FIFO'
NEWB, WMIX, EMPTY, PLANB, WSEC = ('MC-L-IT1-NEW-IS-BEHIND', 'MC-L-IT1-WORD-MIX', 'MC-L-IT1-EMPTY-CELL', 'MC-L-IT1-PLAN-IS-BRIEFING',
                                  'MC-L-IT1-WRITE-SECRET')

LESSONS['1.1'].update({
    'start-here-if-you-have-never-done-this': lad('Start here if you have never done this', 'IT-1.1', L11, {
        'r0': C('A student has never built a PC and the word “motherboard” is new. What does the course expect?', 'Normal; read slowly and build the pictures',
                ['They must pass a vendor exam before starting', 'They should skip ahead to the hardware chapters'],
                'The course assumes no PC building, help-desk work or exam. It asks you to read the opening block slowly so the '
                'pictures are in place before later chapters rely on them.', [NEWB, NEWB]),
        'p': '''<p>You do not need any experience to start this course.</p>
<ul><li>You have not built a PC? Fine.</li><li>You have never worked a help desk? Fine.</li>
<li>Words like <strong>motherboard</strong>, <strong>IP address</strong> or <strong>ticket</strong> sound strange? Also fine.</li></ul>
<p>What you must do is read the next few blocks slowly. They put four pictures in your head: what a computer is, what software is,
what a user brings you, and what a ticket is. Everything later is built on those four pictures.</p>''',
        'pc': C('Why does the course ask you to read the opening block slowly?', 'Later chapters build on its four pictures',
                ['It will be on the final exam word for word', 'It replaces the hands-on labs later'],
                'The opening block gives the mental pictures (computer, software, user, ticket) that every later chapter assumes. It is '
                'groundwork, not an exam script, and the labs still come later.', [NEWB, None]),
        'a': '''<p>Think of your first day learning to drive.</p>
<p>The instructor does not expect you to know how a gearbox works. She first makes sure you can name the pedals, the mirrors and the
indicator, and know what each one is for. Only then do you pull out of the car park. Someone who skips that and goes straight onto the
motorway is not braver; they are dangerous.</p>
<p>This block is the pedals and mirrors. Later chapters are the motorway. Being new is expected; skipping the basics is the only real mistake.</p>''',
        'ac': C('In the driving story, what does “skipping straight to the motorway” stand for?', 'Using later chapters without the basics',
                ['Asking the instructor what each pedal does', 'Reading the opening block a second time'],
                'The later chapters assume the four pictures from this block. Asking questions and re-reading are exactly what '
                'the course wants from a beginner.', [NEWB, NEWB]),
        'v': ['Read “What a computer is” and say the parts in your own words.',
              'Read “What software is”: firmware, operating system, drivers, apps.',
              'Read “What a user brings you”: the job they cannot finish.',
              'Read “What a ticket is”: the written record of that job and what you did.',
              'If a word still feels new, look it up in “Words you will hear this week” before moving on.'],
        'vc': C('After step 4, you still cannot say what a driver is. What does the trace suggest?', 'Re-read and check the word list first',
                ['Move on, because drivers come much later', 'Assume a driver is a type of display cable'],
                'The point of the opening block is that the pictures are clear before you go on. The word list is there for exactly '
                'that gap; guessing or skipping leaves a hole later chapters will hit.', [NEWB, 'MC-L-IT1-DRIVER-IS-APP']),
        't': '<p>Before you read on, write one sentence for each picture in your own words. Then compare with the reveal.</p>',
        'tc': C('Which of these is one of the four pictures the opening block builds?', 'What a ticket is',
                ['How to rebuild a RAID array', 'How to configure a VLAN trunk'],
                'The four pictures are the computer, software, the user’s request and the ticket. RAID and VLANs are later, '
                'more advanced topics.', [NEWB, NEWB]),
        'w': reveal('Write one sentence each: computer, software, what a user brings, ticket.',
                    'Computer: parts that compute, remember and store. Software: instructions from firmware to apps. User: a job they cannot finish. Ticket: the written record of that job and every step taken.'),
    }),
    'words-you-will-hear-this-week': lad('Words you will hear this week', 'IT-1.1', L11, {
        'r0': C('A user says “it worked yesterday, now it doesn’t.” Which word from the list fits?', 'Break/fix', ['Service request', 'Escalate'],
                'Break/fix means something that used to work has stopped. A service request is something they never had, and '
                'escalate is a hand-off, not a label.', [WMIX, WMIX]),
        'p': '''<p>Sort the eight words into four groups and they stop being a blur.</p>
<p><strong>The goal.</strong> <em>Outcome</em> is the one job the person must be able to do again, such as “print the payroll report”.</p>
<p><strong>The labels you choose.</strong> If it worked before, call it <em>break/fix</em>. If they never had it, it is a
<em>service request</em>. If many people or safety are involved, it is an <em>incident</em>.</p>
<p><strong>The move you make.</strong> <em>Escalate</em> means passing the job, with your evidence, to whoever may finish it.</p>
<p><strong>Start-up and safety.</strong> <em>Firmware/UEFI</em> wakes first and runs <em>POST</em>, a quick parts check, before Windows loads.
<em>ESD</em> is the invisible static zap your wrist strap drains away.</p>''',
        'pc': C('What does “escalate” mean in this course?', 'Hand it to whoever may finish it',
                ['Raise your voice so the user calms down', 'Mark the ticket as high priority yourself'],
                'Escalating is a hand-off to whoever is allowed to complete the work, with your evidence. It is not about volume, '
                'and priority comes from impact, not from you deciding it is urgent.', [WMIX, LOUD]),
        'a': '''<p>Think of taking your car to a garage.</p>
<p>“I need to get to work on Monday” is the <strong>outcome</strong>. “The brakes squeal, they didn’t last week” is <strong>break/fix</strong>;
“please fit a tow bar” is a <strong>service request</strong>. A recall affecting every car of that model is an <strong>incident</strong>. When
the apprentice hands the gearbox job to the master mechanic, that is <strong>escalating</strong>. The dashboard lights all flashing on when you
turn the key is the car’s own <strong>POST</strong>, run by its <strong>firmware</strong>. And the mechanic touching the metal frame before handling
a new sensor is the garage’s version of an <strong>ESD</strong> strap.</p>''',
        'ac': C('In the garage story, “please fit a tow bar” is which label?', 'Service request', ['Break/fix, since cars break', 'Incident, since it is a big job'],
                'A tow bar is something the car never had, so it is a request. Break/fix is the squealing brakes that worked '
                'before, and an incident is the model-wide recall.', [WMIX, REQ]),
        'v': ['You press the power button.',
              'The <strong>firmware (UEFI)</strong> wakes up and runs <strong>POST</strong>: are memory, CPU and drives there?',
              'POST passes; Windows starts.',
              'The user cannot print the report: the <strong>outcome</strong> is “print the report”.',
              'It printed yesterday, so the label is <strong>break/fix</strong>.',
              'You need to open the case, so you put on the <strong>ESD</strong> strap first.',
              'The board needs replacing and you are not allowed to: you <strong>escalate</strong>.'],
        'vc': C('In the trace, what runs POST?', 'The firmware (UEFI) on the board', ['Windows, after it has loaded', 'The printer driver'],
                'POST is the firmware’s hardware check before the operating system starts. Windows and drivers load only after '
                'POST has passed.', [WMIX, 'MC-L-IT1-DRIVER-IS-APP']),
        't': '<p>Sort each everyday sentence under the word it is an example of.</p>',
        'tc': C('Which word means “tiny software on the board that runs before Windows”?', 'Firmware / UEFI', ['Driver', 'Operating system'],
                'Firmware (UEFI) lives on the board and starts first. A driver is loaded by the operating system to talk to one device, '
                'and the operating system itself starts after the firmware.', ['MC-L-IT1-DRIVER-IS-APP', WMIX]),
        'w': sort('Which word is it?',
                  {'Break/fix': ['“The scanner worked this morning”'], 'Service request': ['“I need access to the HR folder”'],
                   'Incident': ['“Nobody on floor 2 can log in”'], 'ESD': ['“I felt a zap when I touched the RAM”'],
                   'Escalate': ['“Passing this to the network team with my tests”']},
                  'Notice that labels describe the situation, while escalate describes what you do.'),
    }),
    '6-desk-drill-paper-first': lad('6. Desk drill — paper first', 'IT-1.1', L11, {
        'r0': C('Contact B: “I got a shock from the metal strip under the monitor.” What does the drill table say?', 'Incident, escalate, do not swap the strip',
                ['Break/fix, swap the power strip and test', 'Service request for a new monitor'],
                'A shock is a safety stop: label it an incident and escalate. Swapping the strip yourself treats a hazard as a '
                'routine part change.', [SHOCK, REQ]),
        'p': '''<p>This drill is practice on paper before the live lab. You fill one table for three contacts.</p>
<p>For each contact, write: the <strong>outcome</strong> they need, the <strong>label</strong>, the <strong>impact</strong> (how many, who),
<strong>safety stop</strong> yes or no, <strong>keep or escalate</strong> and why, <strong>tests so far</strong> as action → result, and the
<strong>next step</strong> as a person or a command.</p>
<p>If any cell is empty, you are not ready for the lab. “Look into it” is not a next step.</p>''',
        'pc': C('Which next step would the drill accept?', '“Facilities: check the strip”',
                ['“Look into it further when there is time”', '“See what happens later in the shift”'],
                'A next step must name a person or a command. Vague phrases leave the next technician with nothing to do.', [EMPTY, EMPTY]),
        'a': '''<p>Think of a pilot’s pre-flight checklist.</p>
<p>The pilot does not take off with a box left blank because “it’s probably fine”. Every line gets a tick or a written problem: fuel,
flaps, radio, weather. If one line is a safety item (smoke in the cabin), the flight stops right there, however late it is.</p>
<p>The desk drill is your pre-flight sheet. Every cell is filled. The safety row (contact B’s shock) stops the flight. A blank cell means
you are not cleared to go to the live lab.</p>''',
        'ac': C('In the pre-flight story, what matches contact B’s shock?', 'Smoke in the cabin: stop',
                ['A late passenger: wait a few minutes', 'A blank fuel box: probably fine'],
                'A safety item ends the work and starts an escalation. Lateness is not a safety stop, and a blank box is never fine.', [SHOCK, EMPTY]),
        'v': ['<strong>A</strong> “Need Adobe on this new PC today.” Outcome: open PDFs in Adobe. Request, impact 1. Keep only with the package and approval.',
              '<strong>B</strong> “Shock from the metal strip under the monitor.” Safety stop: yes. Incident. Escalate. Do not swap the strip.',
              '<strong>C</strong> “Printer worked at 0800, jam icon now, three people in line.” Break/fix, impact 3.',
              '<strong>C, new fact</strong>: if it is the only printer for a watch, impact becomes many.',
              'For each, write tests as action → result and a next step naming a person or command.',
              'The live lab in 1.5 is closest to B: many users plus heat.'],
        'vc': C('Contact A asks for Adobe today. When may you keep it?', 'With the package and approval',
                ['Always, because the user asked politely', 'Never, since all software requests are incidents'],
                'A new title is a service request, kept only if you have the approved package and entitlement. Politeness is not '
                'approval, and requests are not incidents.', [REQ, MISS1]),
        't': '<p>Fill the drill table for contact C on paper, then open the intake lab and enter the same facts.</p>',
        'tc': C('Contact C’s printer is the only one for the mid-watch and turnover is in 15 minutes. What changes?', 'Impact becomes many',
                ['Nothing, it is still one printer', 'It becomes a service request'],
                'Impact counts the people who cannot do the outcome, so the whole watch counts. The device count does not change '
                'that, and it used to work, so it is not a request.', [SCOPE, REQ]),
        'w': reveal('Contact C, three people waiting: write label, impact, keep/escalate and next step.',
                    'Break/fix; impact 3 (raise to many if it is the only printer for a watch); keep; next step: clear the jam and print a test page, then confirm with the next user in line.'),
        'lab': ('ticket-intake', 'Enter the drill facts in the intake desk and check each field is filled.'),
    }),
})

LESSONS['1.1'].update({
    'what-this-job-actually-is': lad('What this job actually is', 'IT-1.1', L11, {
        'r0': C('A user asks for a second monitor they have never had. Which label fits?', 'Service request',
                ['Break/fix, because a screen is hardware', 'Incident, because they asked urgently'],
                'They never had it, so it is a request. Break/fix is for things that stopped working, and urgency in the voice '
                'does not make an incident.', [REQ, LOUD]),
        'p': '''<p>Your job is not “fix computers”. Your job is to give someone back one thing they need to do.</p>
<p>So every contact gets three answers before you touch anything:</p>
<ol><li><strong>What must they be able to do again?</strong> That is the outcome.</li>
<li><strong>What kind of job is it?</strong> Request (never had it), break/fix (it stopped), or incident (many people, safety, security).</li>
<li><strong>How big is it?</strong> A number of people plus what happens to them, for example “14 people cannot badge in, shift change in 20 minutes”.</li></ol>
<p>The label decides who may do the work. The impact decides how fast.</p>''',
        'pc': C('Which statement describes impact the way this course wants it?', '“14 cannot badge; turnover in 20 min”',
                ['“It is a really big problem for them”', '“The user sounds very upset on the phone”'],
                'Impact is a count of people plus the consequence. Feelings and adjectives cannot be compared between tickets.', [LOUD, LOUD]),
        'a': '''<p>Picture an emergency-room triage nurse.</p>
<p>She does not start by asking which machine to use. She asks: what can this person not do (breathe, walk, see)? Is this a scheduled
check-up, a sudden injury, or a bus crash with twenty people? How many are hurt and how badly?</p>
<p>The scheduled check-up is your <strong>request</strong>. The sudden sprained ankle is your <strong>break/fix</strong>. The bus crash is
your <strong>incident</strong>: it goes to the trauma team, not the first nurse with a free hand. Help desk work is triage first, treatment second.</p>''',
        'ac': C('In the triage story, the bus crash with twenty people matches which label?', 'Incident',
                ['Break/fix, since each injury is separate', 'Service request, since care is needed'],
                'Many people affected at once is an incident that goes to the team allowed to handle it, not a string of single repairs.', [SCOPE, REQ]),
        'v': svg(560, 170, 'Three questions before any action: outcome, label, impact',
                 box(10, 40, 160, 70, 'Outcome', 'what must work again') + arrow(170, 75, 200, 75) +
                 box(200, 40, 160, 70, 'Label', 'request / break-fix / incident') + arrow(360, 75, 390, 75) +
                 box(390, 40, 160, 70, 'Impact', 'count + consequence') +
                 '<text x="280" y="150" text-anchor="middle" font-size="12">label → who may work it · impact → how fast</text>') +
             '<p>Read left to right: name the outcome, choose the label, then count people and consequence before any tool comes out.</p>',
        'vc': C('According to the diagram, what does the label decide?', 'Who may do the work',
                ['How many people are affected by it', 'What the user’s outcome sentence is'],
                'The label routes the work to whoever is allowed to do it; the impact decides speed, and the outcome comes first.', [SCOPE, None]),
        't': '<p>Label each contact by asking “did they ever have it?” and “how many people?”.</p>',
        'tc': C('“Outlook worked at 0700, now it loops at sign-in, just me.” Which label?', 'Break/fix, impact 1',
                ['Service request for a new Outlook install', 'Incident, because email is important'],
                'It used to work and one person is affected, so it is break/fix with impact 1. Email being important does not '
                'make one person’s problem an incident.', [REQ, LOUD]),
        'w': sort('Label each contact.',
                  {'Request': ['New user needs a shared-folder map', 'Second monitor for a new desk'],
                   'Break/fix': ['Scanner worked yesterday, now blank', 'Outlook loops at sign-in, one user'],
                   'Incident': ['Quarterdeck badge readers warm, many users', 'Shock from a power strip']},
                  'Ask “never had it, stopped working, or many/safety?” every time.'),
        'lab': ('ticket-intake', 'Classify the next three contacts in the intake desk using these three questions.'),
    }),
    'worked-contacts': lad('Worked contacts', 'IT-1.1', L11, {
        'r0': C('Contact D calls, cannot pass identity checks, and wants an urgent reset. What do you do?', 'Stop; no change without identity',
                ['Reset it, since the caller sounds urgent', 'Reset it, then verify afterwards'],
                'An account change without verified identity is how attackers get in. Urgency is a common pressure tactic, and '
                'checking afterwards is too late.', [URGENT, URGENT]),
        'p': '''<p>Here are four calls worked the same way, so you can copy the pattern.</p>
<ul><li><strong>A</strong>: “Please add me to the budget folder.” They never had it: <strong>request</strong>, impact 1. Needs the owner’s approval.</li>
<li><strong>B</strong>: “Outlook has looped since 0700, only me.” Worked before: <strong>break/fix</strong>, impact 1. You keep it.</li>
<li><strong>C</strong>: “The quarterdeck badge readers are warm and nobody can badge.” Many people plus heat: <strong>incident</strong>.
Escalate, keep people off the reader.</li>
<li><strong>D</strong>: an unknown caller who fails the identity questions. <strong>Stop.</strong> No account change.</li></ul>''',
        'pc': C('Why does contact A need more than your own decision?', 'Folder access needs the owner’s approval',
                ['The folder is too large to copy quickly', 'Requests are always escalated as incidents'],
                'Access to data is a request that the data owner approves. Size is irrelevant, and a request is not an incident.', [REQ, MISS1]),
        'a': '''<p>Think of a hotel front desk on a busy night.</p>
<p>Guest A asks for a late checkout: a <em>request</em>, and the manager may need to say yes. Guest B’s key card stopped working:
<em>break/fix</em>, the clerk re-encodes it. Guest C reports smoke in the corridor: an <em>incident</em>; the clerk calls the fire team
and keeps people out, rather than going to look with a bucket. Caller D says “I’m in room 312, give me a new key” but cannot show ID:
the clerk says no, however angry the caller gets.</p>''',
        'ac': C('Which hotel guest matches contact C, the warm badge readers?', 'The smoke in the corridor',
                ['The late checkout', 'The key card that stopped'],
                'Smoke is a safety problem affecting many people, like warm readers on a busy quarterdeck. Late checkout is a request, '
                'and the dead key card is a single break/fix.', [REQ, SCOPE]),
        'v': ['Ask: did it ever work? A no (request). B yes. C yes. D: account change.',
              'Ask: how many and what happens? A 1. B 1, cannot email. C many, cannot enter, and heat.',
              'Ask: safety or identity stop? C heat: yes. D identity: yes.',
              'Decide: A request to owner. B keep and test. C incident, escalate. D refuse and document.',
              'Write: outcome, label, impact, tests as action → result, next owner.'],
        'vc': C('At step 3, which two contacts stop the normal flow?', 'C (heat) and D (identity)',
                ['A and B, because they came first', 'B and C, because both used to work'],
                'Safety and identity are the two stops. Order of arrival and “it used to work” do not stop anything.', [FIFO, SCOPE]),
        't': '<p>Match each worked contact to what you do next.</p>',
        'tc': C('What is the next step for contact B, Outlook looping since 0700?', 'Keep it and test, writing action → result',
                ['Escalate to email engineering at once', 'Close it as a duplicate of contact C'],
                'B is a single-user break/fix you are allowed to work. Escalate only once your tests show it is beyond you, and B '
                'has nothing to do with the badge readers.', [HANDS, CLOSE]),
        'w': order('Put the decision steps in order for any contact.',
                   ['Find the outcome', 'Choose the label', 'Count the impact', 'Check for a safety or identity stop',
                    'Keep or escalate, and write it down'],
                   'Labels and impact come before any keyboard or screwdriver.'),
    }),
    'identity-before-any-reset': lad('Identity before any reset', 'IT-1.4', L11, {
        'r0': C('What should the ticket say after a verified password reset?', '“Verified via callback to listed desk”',
                ['The employee number and last four the user gave', 'The new temporary password, so the user can find it'],
                'The ticket records how identity was proved, never the secret answers or the password. Those would let anyone '
                'reading the ticket impersonate the user.', [WSEC, SECRET]),
        'p': '''<p>A reset hands someone the account. So first prove who they are.</p>
<p>Use the shop script. Ask for the employee number and the last four of a listed ID. Call back the number already on file, not the one
they give now. Or check the badge in person. Or get the manager to confirm.</p>
<p>Then write how you checked: “Verified via callback to listed desk 555-0142.” Never write the password. Never write the answers.</p>''',
        'pc': C('Why call back the number on file instead of the number the caller gives?', 'An attacker controls the number they give',
                ['The number on file is usually cheaper to call', 'Callbacks are faster than asking questions'],
                'A caller pretending to be someone can give you their own phone. Only the number already listed belongs to the real user.', [URGENT, None]),
        'a': '''<p>Think of a bank teller asked to hand over cash.</p>
<p>A stranger says “I’m Maria Lopez, I’ve lost my card, give me £500.” The teller does not take her word for it, even if she cries or
says her boss is waiting. The teller checks ID against the account, or rings the phone number already on Maria’s record. In the ledger
the teller writes “ID checked, passport”, not Maria’s PIN.</p>
<p>A password reset hands over the account just like the cash. Same checks, same ledger rule.</p>''',
        'ac': C('In the bank story, what does the teller write in the ledger?', 'How ID was checked',
                ['Maria’s PIN, for the record', 'Her answer to the security question'],
                'The record shows the method of proof. Writing the PIN or answer would put the secret where others can read it.', [WSEC, SECRET]),
        'v': ['Caller: “I’m locked out, reset me now.”',
              'You: ask for employee number and last four of the listed ID.',
              'Answers match? Call back the listed desk number, 555-0142.',
              'The real user answers and confirms the request.',
              'Reset; the user sets their own password.',
              'Ticket: “Verified via callback to listed desk 555-0142. Reset done. User signed in.”'],
        'vc': C('In the trace, what goes in the final ticket line?', 'The method of proof and the result',
                ['The new password the user chose', 'The last four digits the caller gave'],
                'The note records how you verified and what happened. Passwords and answers never go in a ticket.', [SECRET, WSEC]),
        't': '<p>Practise the identity script out loud with a partner, then write the one-line ticket note.</p>',
        'tc': C('The caller fails the questions but says “my director will be furious.” What now?', 'Refuse politely and document it',
                ['Reset it, since the director outranks you', 'Reset it but mark it as urgent in the ticket'],
                'Failing identity means no change, whatever the pressure. Writing down the refusal protects the user and you.', [URGENT, URGENT]),
        'w': reveal('Write the ticket line for a reset verified by calling back 555-0142.',
                    'Verified via callback to listed desk 555-0142. Password reset; user set a new password and signed in. (No password or answers recorded.)'),
        'lab': ('ticket-intake', 'Work the identity contact in the intake desk and record only the method of verification.'),
    }),
})

LESSONS['1.1'].update({
    'hour-plan-for-1-1': lad('Hour plan for 1.1', 'IT-1.1', L11, {
        'r0': C('In the 1.1 hour plan, what happens from minute 35 to 55?', 'Identity-script role play',
                ['A lecture on motherboard parts', 'Free time to start the live lab'],
                'Minutes 35–55 are the identity script role play. Hardware comes in chapter 2, and the live lab comes in 1.5.', [PLANB, PLANB]),
        'p': '''<p>Lesson 1.1 is 90 minutes of doing, not listening. Here is what each block trains.</p>
<ul><li><strong>0–15</strong>: say the outcome out loud for sample contacts.</li>
<li><strong>15–35</strong>: put each contact under one of four labels.</li>
<li><strong>35–55</strong>: role-play the identity script with a partner.</li>
<li><strong>55–75</strong>: write a “Ticket B” note; a peer scores it.</li>
<li><strong>75–90</strong>: give a handoff aloud, as if the next shift takes over.</li></ul>
<p>By the end you have done every step of a contact at least once.</p>''',
        'pc': C('Why is the Ticket-B note scored by a peer rather than by you?', 'A reader shows if the note works for someone else',
                ['Peers mark faster than the instructor does', 'Your own score does not count toward the grade'],
                'A ticket note is written for the next person. Having someone else read it tests exactly that.', [VAGUE, None]),
        'a': '''<p>Think of a football training session.</p>
<p>The coach does not spend 90 minutes on a whiteboard. Warm-up (say the outcome), passing drills (labels), one-on-one defence (identity
role play with a partner trying to trick you), shooting with a teammate keeping score (peer-scored note), then a short practice match
where you hand the ball on (handoff aloud). Each drill is one skill you will need in the real match: the live lab in 1.5.</p>''',
        'ac': C('In the training story, “one-on-one defence with a partner trying to trick you” matches which block?', 'The identity role play',
                ['The outcome warm-up block', 'The handoff practice match block'],
                'In the identity role play your partner plays a caller who may try pressure or tricks, like an attacker in a defence drill.', [PLANB, PLANB]),
        'v': svg(560, 120, 'Ninety-minute plan for lesson 1.1 in five blocks',
                 box(5, 30, 100, 60, '0–15', 'outcome') + box(115, 30, 100, 60, '15–35', 'labels') +
                 box(225, 30, 100, 60, '35–55', 'identity') + box(335, 30, 100, 60, '55–75', 'Ticket B note') +
                 box(445, 30, 110, 60, '75–90', 'handoff aloud')) +
             '<p>The blocks follow one contact from first words to handover: name it, label it, check identity, write it, hand it on.</p>',
        'vc': C('Which block comes straight before the handoff aloud?', 'Writing the peer-scored Ticket B note',
                ['Role-playing the identity script', 'Saying the outcome for sample contacts'],
                'The order follows a real contact: outcome, label, identity, note, then handoff. The note is written before you hand off.', [PLANB, PLANB]),
        't': '<p>Put the five blocks in the order the lesson runs them.</p>',
        'tc': C('What do you have by the end of the 90 minutes?', 'Practised each step of a contact once',
                ['A finished live-lab score for 1.5', 'A memorised list of hardware parts'],
                'The hour plan rehearses every step of a contact. The scored live lab is in 1.5, and hardware comes later.', [PLANB, PLANB]),
        'w': order('Order the 1.1 blocks.', ['Say the outcome', 'Label the contact', 'Identity role play', 'Write the Ticket B note',
                                            'Hand off aloud'], 'Same order as a real contact.'),
    }),
    'what-you-are-paid-to-restore': lad('What you are paid to restore', 'IT-1.1', L11, {
        'r0': C('Which is a good outcome sentence?', '“User in 214 can send mail from Outlook 16 on this PC”',
                ['“Looking into the network for the user in room 214”', '“Fixing the computer problem in room 214 today”'],
                'A good outcome names who, what they can do, and where, so anyone can test it. “Looking into” and “fixing the '
                'problem” cannot be checked.', [VAGUE, VAGUE]),
        'p': '''<p>You are paid to give back a thing the person can do, not to “work on the network”.</p>
<p>So write the outcome as a test someone else could run: <strong>who</strong>, <strong>can do what</strong>, <strong>on which device</strong>.</p>
<p>Good: “User in 214 can send mail from Outlook 16 on this PC.” Bad: “Looking into the network.”</p>
<p>When the user does the outcome in front of you, you are done. Until then, you are not, however many things you changed.</p>''',
        'pc': C('When is the job finished?', 'When the user does the outcome',
                ['When you have changed a setting that looks likely to help', 'When you have spent the planned time on it'],
                'Finished means the outcome works and the user confirms. A change is not a fix until the outcome is tested.', [CHG, CLOSE]),
        'a': '''<p>Think of a plumber called for a leak.</p>
<p>The homeowner does not pay for “worked on pipes for two hours”. She pays for “the kitchen tap runs and nothing drips under the sink”.
A good plumber turns the tap on in front of her, opens the cupboard, and they both look. A bad plumber says “I replaced a washer, should
be fine” and drives off, and the floor is wet by dinner.</p>
<p>Your outcome sentence is the tap test. Write it first, then do it together at the end.</p>''',
        'ac': C('What does the bad plumber’s “I replaced a washer, should be fine” match?', 'Treating a change as a fix',
                ['A good outcome sentence', 'A successful user test'],
                'Replacing a part is a change. Without running the outcome (the tap test), nobody knows if it worked.', [CHG, CHG]),
        'v': ['Contact: “Email’s broken.”',
              'Ask: what must you be able to do? “Send the shift report from Outlook on this PC.”',
              'Write it: “User in 214 can send mail from Outlook 16 on PC214.”',
              'Work and test, writing action → result.',
              'User sends a test mail while you watch: it arrives.',
              'Close with the outcome sentence and “verified by user”.'],
        'vc': C('What does step 2 turn “email’s broken” into?', 'A specific thing the user must do',
                ['A guess about which server failed', 'A label for the ticket priority'],
                'Asking what they must do turns a vague complaint into a testable outcome. Server guesses and priority come later.', [VAGUE, LOUD]),
        't': '<p>Rewrite each vague goal as an outcome a stranger could test.</p>',
        'tc': C('Which rewrite of “printer issue” is a testable outcome?', '“Front-desk PC prints to HP-2 again”',
                ['“Printer issue being investigated”', '“Something is wrong with printing”'],
                'It names the device, the printer and the action, so anyone can check it. The others describe nothing testable.', [VAGUE, VAGUE]),
        'w': reveal('Rewrite “Wi-Fi is bad” as an outcome.', 'Example: “Laptop LT-08 in conference room B joins CorpWiFi and loads the intranet.”'),
    }),
    'impact-is-a-count-plus-a-consequence': lad('Impact is a count plus a consequence', 'IT-1.1', L11, {
        'r0': C('Which impact statement meets the bar?', '“14 in Bldg 3 cannot badge; turnover in 20 min”',
                ['“Huge problem, users are very angry”', '“High impact for many users, please treat as urgent”'],
                'Impact is a number of people plus what happens to them and when. Adjectives and “urgent” cannot be compared or checked.', [LOUD, LOUD]),
        'p': '''<p>Impact has two parts, and you need both.</p>
<p><strong>The count</strong>: how many people cannot do the outcome, and where. <strong>The consequence</strong>: what that stops, and by when.</p>
<p>“Fourteen users in Bldg 3 cannot badge, mid-watch turnover in 20 minutes” has both. A dispatcher can compare it with every other ticket.</p>
<p>“Really bad” has neither. A loud caller is not a big impact, and a quiet one is not a small impact.</p>''',
        'pc': C('A calm caller says the whole lab of 30 cannot log in before an exam at 0900. Impact?', '30 users, exam blocked at 0900',
                ['Low, because the caller is calm about it', 'One, because only one person phoned in'],
                'Impact counts the affected people and the consequence, not the caller’s tone or the number of calls.', [LOUD, SCOPE]),
        'a': '''<p>Think of a fire dispatcher.</p>
<p>A caller screaming about a smoking toaster and a calm caller saying “the apartment block next door is on fire, about forty people live
there” are not ranked by volume. The dispatcher writes: how many people, what is at risk, how soon. Forty people and a burning
building win, even though the voice was calm.</p>
<p>Your impact line is that dispatch note. It lets the queue sort itself fairly.</p>''',
        'ac': C('Why does the calm caller in the story get the faster response?', 'More people and a bigger consequence',
                ['They phoned the service desk first', 'They stayed calm and used polite language'],
                'Priority follows count plus consequence. Order of calls and manners do not change who is at risk.', [FIFO, LOUD]),
        'v': svg(560, 150, 'Impact equals count plus consequence',
                 box(20, 40, 150, 60, 'Count', '14 users, Bldg 3') + text(195, 75, '+', 20, 'middle', True) +
                 box(220, 40, 150, 60, 'Consequence', 'turnover in 20 min') + arrow(370, 70, 400, 70) +
                 box(400, 40, 140, 60, 'Impact line', 'comparable')) +
             '<p>Only when both boxes are filled can a dispatcher compare this ticket with others in the queue.</p>',
        'vc': C('What is missing from “Bldg 3 badges down”?', 'The count and the consequence',
                ['Nothing, the building already tells you', 'The caller’s name and extension number'],
                'It names a place but not how many people or what stops. The caller’s details are useful but are not impact.', [SCOPE, None]),
        't': '<p>Add a count and a consequence to each weak impact line.</p>',
        'tc': C('Which line is a complete impact statement?', '“3 at front desk cannot print; patients waiting”',
                ['“Front desk printer down, urgent!!”', '“Front desk printer broken; please come quickly”'],
                'It has a count (3), where (front desk), and a consequence (patients waiting). The others are adjectives.', [LOUD, LOUD]),
        'w': reveal('Fix: “Wi-Fi down in the training room, big problem.”',
                    'Example: “22 trainees in Room 4 cannot join Wi-Fi; class assessment at 1000 cannot start.”'),
    }),
})


# ---------------------------------------------------------------- refinement pass 20: the rest of chapter 1
# 1.1 desk set / identity / handoff (now laddered in their own right) and every section of 1.2-1.5. Pending SME review.
SAFE, OPSU, LIFT, ESDO, ESDF = 'MC-IT1-SHOCK-AS-SWAP', 'MC-C-IT1-OPEN-PSU', 'MC-C-IT1-LIFT-BACK', 'MC-IT1-ESD-ORDER', 'MC-IT1-ESD-FALSE-PROTECT'
HANDS, PPE, WATER = 'MC-IT1-HANDS-FIRST', 'MC-C-IT1-PPE-MISMATCH', 'MC-C-IT1-WATER-ON-ELECTRICAL'
VAGUE, VNOTE, CHG, CHGU, SEC = 'MC-IT1-VAGUE-NOTES', 'MC-C-IT1-VAGUE-NOTE', 'MC-IT1-CHANGE-AS-FIX', 'MC-C-IT1-CHANGE-UNRECORDED', 'MC-IT1-SECRETS-IN-TICKET'
ARGUE, JARG, PRIV, URG = 'MC-C-IT1-ARGUE', 'MC-C-IT1-JARGON', 'MC-C-IT1-PRIVACY-LOOK', 'MC-IT1-URGENCY-OVER-ID'
REQ, SCOPE2 = 'MC-IT1-REQ-AS-INC', 'MC-IT1-SCOPE-IGNORED'
LAB = ('ticket-intake', 'Run the Block 1 intake card: show ticket, classify, impact, escalate, note, submit.')


def Q(q, k, w1, w2, why, m1, m2=None):
    if len(why.split()) < 10:
        why += ' The other options skip the habit this section teaches.'
    return C(q, k, [w1, w2], why, [m1, m2])


def V(v):
    """Numbered trace plus the one habit every walk-through shares."""
    return ol(v) + ('<p>Work the numbered steps top to bottom. If a step fails or surprises you, stop there and write what you saw '
                    'before you go on.</p>')


def X(h, obj, src, qs, p, a, v, t, w=None, lab=LAB):
    """Compact section: qs = five Q tuples for R0, R1, R2, R3, R4."""
    return lad(h, obj, src, {'r0': Q(*qs[0]), 'p': P1.get(h, p), 'pc': Q(*qs[1]), 'a': a, 'ac': Q(*qs[2]), 'v': V(v), 'vc': Q(*qs[3]),
                             't': t, 'tc': Q(*qs[4]), 'w': w, 'lab': lab})


# R1 re-tellings for sections whose first draft stayed too close to the original wording (plain-language, new words).
P1 = {
    '3. Body and path': '<p>Your back and feet get hurt more often than your fingers in this job. Squat down instead of folding over, hug the box to your '
        'chest, and turn with your feet rather than your waist. Heavy cabinets and big battery boxes always need a helper. Look at the floor before carrying '
        'anything, protect your eyes when snipping plastic ties, and wear proper closed shoes.</p>',
    'Why the wall unplug matters': '<p>Think of three habits. One: the little switch on the back only tells the box to stop. The plug in the socket is what really cuts the power. Parts inside can stay charged for a while, so pull the plug and pause. Two: the wrist band only works touching skin. '
        'Three: if anything is bulging, smells burnt or gave someone a jolt, step back. Call for help instead of repairing.</p>',
    'Lift, path, and the bench': '<p>Before you carry a computer anywhere, plan the trip. Look at the floor for cables and bags. Decide if you need a helper. Know which plug is the power one. Put the computer down only on the solid work table, never a seat on wheels. Keep empty packaging on the ground so the table stays clear.</p>',
    'When safety is the ticket': '<p>Sometimes there is nothing to repair yet, because the danger itself is the problem. Maybe someone got a jolt, something smells scorched, or a device is too hot to touch. Tell everyone to stop using it. Then call for help. In the lab, pick incident. Choose many if several people are affected. Say yes to escalate, and mention the heat in your note.</p>',
    'Lift and path': '<p>Quick rule for moving gear: describe your route before you pick it up. If you cannot, put it down and plan. Check the floor. Find and pull the power plug. Grab a helper for big awkward cases. Set things on the solid table, never a chair that rolls. Corners and screen edges '
        'bite shins and fingers.</p>',
    '1. Anatomy of a usable ticket': '<p>A helpful ticket answers the questions the next person would ask you if they could. Who is stuck, and where? What '
        'were they trying to get done? What exactly did the screen say? When did it go wrong, and did anything change just before? What did you try, and '
        'what happened each time? What are you leaving for them to do next?</p>',
    '2. Facts versus guesses': '<p>Split what you saw from what you suspect. Seeing a login box pop up again and again after updates is something you '
        'observed. Thinking a server somewhere is the cause is a hunch. Hunches are fine in your head, but in writing they must be marked as hunches, '
        'because a reader cannot tell the difference and will believe whatever is written.</p>',
    '3. Change awareness': '<p>Ask yourself one question: am I putting things back the way they were, or am I adding something new? Putting back, like '
        'pushing a loose memory stick into place, is fixing. Adding, like a new network rule, a fresh install or a new name lookup entry, is changing, and '
        'changing needs permission, timing and a plan to undo it. Both get written down.</p>',
    '4. Note quality bar for the lab': '<p>The lab is strict about notes. A single word such as “fixed” bounces. Tell it three things in a few short '
        'sentences: who cannot do what, one thing you noticed or tested, and who or what comes next. If the lab still refuses, open the card again and '
        'check that you chose a label, a size of impact and whether to pass it on.</p>',
    'Anatomy of Ticket B': '<p>Picture a stranger reading your notes tomorrow with no way to call you. They need to find the computer, know what the '
        'person was trying to do, know when it last behaved, see every check with its outcome, see what you already tried, and know where to go next. '
        'If any of that is missing, your note is still the weak kind.</p>',
    'Action → result until it is boring': '<p>Every check you write needs two halves: what you did and what came back. Half a line, like “checked the '
        'mail program,” tells the reader nothing. A full line gives the setting you switched and what still happened, or the exact address the computer '
        'showed. Practise on paper until writing both halves happens without thinking.</p>',
    '1. Talk to the outcome': '<p>People want to know what this means for them, not how the network works. Skip the acronyms. Tell them what is not '
        'working, what you are doing about it, and your backup plan. During a long outage, keep checking in at times you promised, because hearing nothing '
        'makes people think nobody cares.</p>',
    '2. Privacy on a real floor': '<p>Treat everything you see on someone’s computer as private. Keep phone calls about tickets out of busy hallways. Close personal windows before you share or capture a screen. Crop pictures down to the error. Keep secrets out of writing. Only ever test with your own login. When connected remotely, tell the person what is visible to you.</p>',
    '3. Saying no': '<p>Part of the job is turning down requests that break the rules. Examples: folder access with no sign-off, or switching off protection so a game runs. Saying no is not the end of helping. Point them to the person who can approve it, or to a safer option. If they get angry, pass it to your supervisor rather than giving in.</p>',
    '4. What goes in the ticket': '<p>Picture an auditor, your boss and the customer all reading your note. Keep it to what happened, when, what you '
        'checked, what you altered and what the person can now do. Leave out secrets, insults and complaints about colleagues. Tricky decisions go to a '
        'supervisor first; afterwards add one plain line about what was decided.</p>',
    'Hour plan for 1.4': '<p>This lesson is rehearsal. You practise switching between plain speech for people and precise writing for records. You '
        'practise holding the line politely while a classmate acts pushy. You practise spotting which details are personal, which are ordinary, and which '
        'are secret. You finish by writing down a refusal calmly.</p>',
    'User channel versus ticket channel': '<p>You talk in three places, and each wants a different kind of sentence. To the person: what works again, what '
        'you need from them, when you will be back. In the record: exact versions, codes and test numbers. To your supervisor: a short question asking for a '
        'decision. Mixing them up confuses people or loses information.</p>',
    'Refuse without becoming the enemy': '<p>Turning down a request can stay friendly. Have a ready sentence that says you cannot do it this way, then gives '
        'the proper route, such as visiting the service window with ID. Afterwards, write one calm line saying what was asked, why it was declined and '
        'where the person was sent. No blame, no drama.</p>',
    'Worked example — this lab’s sentence': '<p>Let us walk through the practice card. Lots of door badges stopped working and the box on the wall feels '
        'warm. Lots of people plus heat equals a serious, shared problem, so it is an incident affecting many, and you hand it to building and door-security '
        'staff. Your note says what you saw, that you kept the box shut, and who should come.</p>',
    'Pass bar': '<p>To finish this block you have to do the practice card yourself without being told the answers. Your written note needs to mention the '
        'warmth and say who should take over, and you must keep the device closed. Do that, and the next chapter adds names of computer parts to the same '
        'careful habits.</p>',
    'How the live lab is scored': '<p>The lab checks each decision you type. Look at the card first. Call it an incident. Say many people are hit. Choose to pass it on. Write a note that mentions heat but keeps the box closed. Then hand it in. Calling it a simple repair, '
        'saying only one person, or prying it open marks you down.</p>',
    'Hour plan for 1.5': '<p>In this final session the class reads the practice card together and spots the key clues before typing. Then each person '
        'works through the lab while the teacher watches the big decisions. Anyone whose attempt bounces explains why and tries again. A ten-question '
        'quiz ends the chapter, and wrong answers point back to the lesson part to reread.</p>',
    'The card, line by line': '<p>Read the practice card carefully: lots of door badges stopped and the wall box is warm. This is not one faulty cable '
        'at one desk. Go step by step: open the card, call it an incident, say many, pass it to the building and security teams, write that it is warm, '
        'that you kept it shut and who comes next, then submit. Secrets or blank notes fail.</p>',
    'After the lab': '<p>Getting the practice card right does not mean you are finished. If the end-of-chapter quiz showed you were shaky on checking who '
        'a caller really is, go back and reread that part, then practise writing one polite “no” note. Real work throws many different situations at you, '
        'not just this one.</p>',
}

LESSONS['1.1'].update({
    'desk-set-classify-these-out-loud': X('Desk set — classify these out loud', 'IT-1.1', L11, [
        ('A new hire cannot open the budget share on day one; the next desk can. Which label fits?', 'Request', 'Incident', 'Change',
         'Nothing broke: the person never had access, so it is a request for something new, not a failure of something that worked.', REQ, CHG),
        ('What three things do you say out loud for every desk-set line?', 'Label, impact, keep-or-escalate', 'Label, hostname, password', 'Name, mood, estimated fix time',
         'The drill trains the three intake decisions: what kind of work, how many and what stops, and whether you keep it.', HANDS, SEC),
        ('In the referee story, why does arguing the close calls matter more than the answer key?', 'The reasoning is the skill', 'Matching the secret key exactly', 'Referees never agree',
         'The key is a starting point; the point of the drill is defending a label with impact facts, like a referee explaining a call.', FIFO, REQ),
        ('Half the building cannot badge and the reader is warm. What comes out of step 3 of the trace?', 'Incident, many, escalate', 'Break-fix, impact 1, keep', 'Request, impact 1, keep',
         'Many people plus heat on a device is an incident with a big impact and a safety reason to escalate.', SAFE, SCOPE2),
        ('A user wants a production DNS record added at 1510 for a demo. What is it?', 'A change, not a repair', 'A quick break/fix to do now', 'An incident to keep',
         'Adding something new to shared infrastructure is a change and goes through the shop process, even when it takes two minutes.', CHG, CHGU),
    ],
        '<p>This block is practice, not reading. The instructor reads eight short situations. For each one you say three things out loud: '
        'the <strong>label</strong> (request, break/fix, incident or change), the <strong>impact</strong> (how many people and what stops), and '
        '<strong>keep or escalate</strong>. Some lines are easy, like a new hire who never had access. Some are edge cases, like the only printer for a '
        'watchbill jamming fifteen minutes before turnover. The answer key exists, but the goal is to argue your choice with facts.</p>',
        '<p>Think of a football referee in training. The coach plays clips: a foul, a dive, a clumsy tackle that is almost a foul. '
        'The trainee must blow the whistle, name the call and explain it in one breath. Nobody grades the trainee only on matching the head referee; '
        'they grade the explanation. Two good referees can disagree on a borderline clip, but both must point to what they saw. '
        'Your desk set is that clip reel: name the call, then say what you saw that made it that call.</p>',
        ['Hear the line once; do not touch anything yet.', 'Ask: did this ever work? If no, it leans request.',
         'Count people and name what stops: one desk, one floor, half a building.', 'Check for heat, shock or identity trouble: those force stop or escalate.',
         'Say label, impact, keep-or-escalate in one sentence, then defend it if challenged.'],
        '<p>Sort each desk-set line into its label, then say the impact and keep-or-escalate out loud.</p>',
        sort('Sort the desk-set lines', {'Request': ['New hire never had the budget share'],
                                         'Break/fix': ['Outlook password loop on one desk', 'One floor printer jammed, two others work'],
                                         'Incident': ['Half the building cannot badge, reader warm', 'User felt a shock from the strip'],
                                         'Change': ['Production DNS record for a 1510 demo']},
             'Requests are new things, break/fix restores one thing, incidents hit many or safety, changes add something new to shared systems.')),
    'identity-before-any-account-change': X('Identity before any account change', 'IT-1.1', L11, [
        ('A friendly caller wants a reset but cannot finish the identity script. What happens?', 'No reset; document the refusal', 'Reset it, they sound genuine', 'Reset it and note “sounded OK”',
         'Friendly voices lie; the script is the gate. If it is not completed, the answer is no, and the refusal is written as a fact.', URG, WSEC),
        ('Which number do you call back to verify a caller?', 'The listed number on file', 'The number they just gave', 'Any number that answers',
         'A callback only proves identity when it goes to a number the shop already holds; a number the caller offers proves nothing.', URG, None),
        ('In the bank-vault story, what does the second key stand for?', 'The identity script step', 'How urgent the caller sounds', 'The new password',
         'Two keys mean no single friendly person can open the vault; the script is the second key that must turn before any account change.', URG, WSEC),
        ('After verifying, what do you write in the ticket?', 'How you verified it', 'The answer they gave', 'The new password',
         'Write the method, such as “callback to listed desk 555-0142”; never the secret answer, the old password or the new one.', WSEC, SEC),
        ('Which of these is a privileged action that needs the identity script first?', 'Adding someone to a share', 'Reading a public notice', 'Giving the desk phone number',
         'Resets, unlocks, share adds and mailbox opens change who can reach data, so each one waits for identity first.', URG, None),
    ],
        '<p>Some jobs change who can get into what: a password reset, an account unlock, adding someone to a shared folder, opening a mailbox. '
        'These are <strong>privileged</strong> actions. Before any of them you run the shop identity script: call back on the listed number, check the ID '
        'the shop requires, see the badge if they are at the window. Then write <em>how</em> you verified, never the secret itself. '
        'If the caller cannot finish the script, you say no and write that down.</p>',
        '<p>Picture a bank vault that needs two keys turned at the same time by two different people. A charming customer at the counter can smile, '
        'name the manager, even cry; the vault still does not open with one key. The rule is not an insult to the customer. It exists because the most '
        'convincing people are often the ones the rule is there to stop. Your identity script is the second key. Until it turns, the account stays shut, '
        'however nice the voice sounds.</p>',
        ['Caller asks for a reset, unlock, share or mailbox.', 'Run the script: listed callback, ID, badge or supervisor as the shop requires.',
         'Script complete? Do the change, write “verified by callback to listed desk …”.',
         'Script not complete? Say “I cannot do that from this call” and give the approved path.', 'Write the refusal as a fact; never write the secret.'],
        '<p>Put the identity steps in order, then write one verification line and one refusal line without any secret in them.</p>',
        order('Order an account change', ['Hear the request', 'Run the identity script', 'Decide: complete or not', 'Act or refuse', 'Write how you verified'],
              'Identity always comes before the change, and the note records the method, not the secret.')),
    'handoff-that-survives-0200': X('Handoff that survives 0200', 'IT-1.1', L11, [
        ('Which handoff lets the night shift continue without calling you?', 'Outcome, scope, tests, changes, next', '“VPN still broken, user unhappy, please fix”', '“Tried a few things, still failing for user”',
         'Five lines carry the work: what they cannot do, how many and where, tests with results, what you changed, and the next step.', 'MC-L-IT1-HANDOFF-NUMBER', VAGUE),
        ('Why must the handoff list what you already changed?', 'So nobody undoes or repeats it', 'To prove how hard you worked all shift', 'It is optional detail',
         'The next technician needs to know the current state; unknown changes lead to repeated work or to undoing a fix by accident.', CHGU, None),
        ('In the relay story, what does a dropped baton stand for?', 'A vague handoff', 'A slow runner', 'A closed ticket',
         'The race is lost at the exchange, not on the straight; a handoff with no tests or next step drops the work between shifts.', VAGUE, 'MC-IT1-CLOSE-EARLY'),
        ('Line 3 of the trace says “gateway 10.20.30.1 fails.” What kind of line is that?', 'A test with its result', 'A guess about the cause', 'A user complaint',
         'It pairs an action with what happened, which is evidence the next person can trust and build on.', VNOTE, None),
        ('What should the last handoff line contain?', 'The next person or command', 'A thank-you note to the user for waiting', 'The caller’s password',
         'The handoff ends by naming who or what comes next, so the work keeps moving at 0200.', 'MC-L-IT1-HANDOFF-NUMBER', SEC),
    ],
        '<p>When your shift ends, someone else picks up your open tickets, maybe at two in the morning. A good handoff has five lines: the outcome the user '
        'still cannot do, how many people and where, each test you ran with its result, what you already changed, and the next person or command. '
        '“VPN broken, please fix” gives them nothing. A handoff with version, error, pings and timing lets them carry on without phoning you.</p>',
        '<p>Think of a relay race. The runners can be fast, but races are won and lost in the twenty-metre box where the baton passes. '
        'A good runner looks back, calls “stick!”, and puts the baton firmly in the next hand. A sloppy one waves it vaguely and hopes. '
        'Your ticket at the end of a shift is that baton. If the next technician has to stop, turn round and call you to ask what you tried, '
        'the baton hit the track.</p>',
        ['Outcome: “Cannot send mail from Outlook 16 on PC214.”', 'Scope: one user, Building 2.', 'Tests: “LAN ping 10.20.30.50 4/4; gateway 10.20.30.1 fails.”',
         'Changes: “Weekend client update; nothing changed by me.”', 'Next: “Messaging team to check account lock.”'],
        '<p>Rewrite this weak handoff into the five lines.</p>',
        reveal('Rewrite: “Printer issue, see user.”',
               'Outcome: 3 front-desk staff cannot print. Scope: front desk, Bldg 1. Tests: queue cleared → still stuck; test page → error 79. '
               'Changes: none. Next: vendor call for fuser error.')),
})


LESSONS.setdefault('1.2', {}).update({
    'electricity-you-need-as-a-technician-not-as-an-engineer': X('Electricity you need as a technician, not as an engineer', 'IT-1.2', L12, [
        ('What does the PC power supply do?', 'Turns wall power into low voltages', 'Stores static charge for the motherboard', 'Grounds your wrist strap',
         'The supply converts dangerous wall power into the lower voltages that the board and drives use; it is not a static store or ground.', OPSU, ESDF),
        ('A user says the strip under the monitor shocked them. What is it?', 'An incident, not a quick swap', 'A break/fix job: swap the PSU now', 'A request for a new strip',
         'A shock means a live hazard that can hurt someone else; you stop, keep people away and escalate instead of swapping parts.', SAFE, REQ),
        ('In the kitchen story, why does the cook leave the gas line to a fitter?', 'Some hazards are beyond the role', 'Cooks are too busy with other orders', 'Gas lines are cheap',
         'Knowing which hazards you handle and which you hand off is the safety skill; a technician replaces the unit and never works inside the supply.', OPSU, None),
        ('Step 3 of the trace puts the strap on. Where does it go?', 'On bare skin', 'Over a hoodie sleeve', 'Around the PSU cable',
         'The strap must touch skin to drain your body charge into the shared ground; fabric in between makes it decoration.', ESDF, ESDO),
        ('Which item do you never open in this course?', 'The power supply', 'The side panel', 'The antistatic bag',
         'The supply holds charge even after unplugging; it is a sealed replaceable unit, while panels and bags are opened safely in order.', OPSU, None),
    ],
        '<p>You do not need to be an electrician, but you must respect two kinds of electricity. The first is <strong>wall power</strong>: the supply inside the '
        'PC turns it into small voltages for the parts, and it can kill. So you unplug at the wall before opening a panel and you never open the supply. '
        'The second is <strong>static</strong> from your own body, a tiny spark that can ruin a chip without you feeling it. The wrist strap drains it, but only '
        'when it touches your skin.</p>',
        '<p>Think of a cook in a busy kitchen. The cook handles hot pans, sharp knives and the oven door every day, with habits that keep fingers safe. '
        'But when the gas line hisses or smells wrong, the cook does not grab a spanner and start fiddling; they shut the valve, clear the kitchen and call '
        'the gas fitter. A technician is the cook: comfortable with the case, the parts and the strap, but the power supply internals and a live, shocking '
        'outlet belong to the fitter.</p>',
        ['Shut down and unplug at the wall, not just the rocker.', 'Wait a moment for stored charge.', 'Strap on bare skin, clipped to the shared ground.',
         'Open the side panel; never the supply.', 'Any shock, heat or burn smell: stop and escalate as an incident.'],
        '<p>Sort each job into what a technician does and what is someone else’s.</p>',
        sort('Technician job or hand off?', {'Technician does it': ['Unplug at the wall', 'Wear the strap on skin', 'Replace a failed PSU unit'],
                                             'Stop and escalate': ['Open the PSU to check a capacitor', 'Keep using a strip that shocked a user']},
             'You replace sealed units and follow the open order; live hazards go to facilities or electrical.')),
    '1-electrical-reality-on-a-training-bench': X('1. Electrical reality on a training bench', 'IT-1.2', L12, [
        ('When is a PSU safe to treat as not live?', 'Cord out of the wall and waited', 'When the rocker switch on the back is off', 'Screen is dark',
         'The rocker and a dark screen do not remove stored or incoming power; only the wall cord out plus a wait does.', ESDO, None),
        ('Why is a three-to-two prong adapter that drops the ground pin forbidden?', 'It removes the safety path', 'It makes the PC slower', 'It voids the warranty only',
         'The ground pin carries fault current away from you and the parts; defeating it lets a fault travel through people.', 'MC-C-IT1-POWER-DEVICE', None),
        ('In the pool-lifeguard story, what is the open drink on the bench?', 'A short waiting to happen', 'A harmless habit if you are careful', 'A cooling aid',
         'Liquids and metal near open electronics cause shorts and dead ports, the same way glass by a pool causes injuries.', PPE, None),
        ('Step 2 of the trace says remove jewelry. Why?', 'Metal can bridge contacts', 'It can scratch the case paint', 'It blocks the strap',
         'Rings and watches conduct; they can short a board or a battery terminal, which is why they come off before work.', PPE, ESDF),
        ('A PSU is dead. What do you do with it?', 'Replace the whole unit', 'Open it and resolder the joint', 'Bypass its fuse',
         'Supplies are sealed field-replaceable units; work inside them is out of scope and dangerous because of stored charge.', OPSU, None),
    ],
        '<p>On the training bench, act as if every power supply and outlet is live. It only stops being live when the cord is out of the wall and you have '
        'waited. Never break off or bypass the ground pin. Never work inside a power supply; swap the whole unit. Keep drinks, liquids and metal jewelry off '
        'the bench, because that is how shorts and ruined ports happen.</p>',
        '<p>A lifeguard at a public pool has a short list of rules that look fussy: no running, no glass, no diving in the shallow end. Most days nothing '
        'happens, which is exactly the point. The rules are there for the one afternoon when a glass shatters on wet tiles. The bench rules are the same: '
        'no drinks by open boards, no rings near terminals, no ground pins snapped off. Ninety-nine days they feel unnecessary; the hundredth day they '
        'save a board or a hand.</p>',
        ['Clear drinks and liquids off the bench.', 'Remove rings, watches and metal bracelets.', 'Unplug from the wall and wait.',
         'Check the ground pin is intact on every cord.', 'Swap failed supplies whole; do not open them.'],
        '<p>Order the bench set-up before you touch a tower.</p>',
        order('Bench set-up', ['Clear liquids', 'Remove jewelry', 'Unplug at the wall', 'Wait', 'Check the ground pin'],
              'The bench is made safe first, then the device is made dead, then you check the safety path.')),
    '2-esd-without-mythology': X('2. ESD without mythology', 'IT-1.2', L12, [
        ('Can ESD damage a chip even if you feel nothing?', 'Yes, below what you can feel', 'No, you always feel a damaging one', 'Only in wet weather',
         'Damaging discharges are often far below the level a person notices, and dry air makes them more likely, not less.', ESDF, None),
        ('Which order is right before unbagging memory?', 'Mat grounded, strap on, then unbag', 'Unbag, then clip on the wrist strap', 'Strap clipped to the box, then unbag',
         'Ground the mat, put the strap on skin and clip it, and only then take parts out of their antistatic bags.', ESDO, ESDF),
        ('In the boat-fuelling story, why ground the nozzle first?', 'So charge drains before fuel flows', 'To keep the fuel cool while pumping', 'To measure the fuel',
         'Grounding first gives static a safe path before the risky moment, just as the strap does for a board before you touch it.', ESDO, None),
        ('Your strap is broken mid-job. What does the trace say?', 'Stop and replace it', 'Hold the chassis and carry on', 'Work faster',
         'A broken strap means no path; holding the chassis is not a substitute unless the shop procedure explicitly allows it.', ESDF, ESDO),
        ('Where do loose parts go when you walk away?', 'Back in antistatic bags', 'On top of the cardboard shipping box', 'On the carpet',
         'Bags keep parts at a safe potential; cardboard and carpet build or hold charge.', ESDF, None),
    ],
        '<p>Electrostatic discharge, or ESD, is a little spark from your body. You may not feel it, but it can still punch a hole in a chip. Carpet, dry air '
        'and synthetic sleeves make it worse. The fix is a routine: mat on a steady bench, mat clipped to the shop ground point, strap on bare skin and '
        'clipped to the mat or chassis, and only then take boards and memory out of their bags. If the strap breaks, stop and replace it.</p>',
        '<p>When you fill a small boat with fuel, you touch the nozzle to the tank before the fuel flows, so any static drains away first. Nobody skips it '
        'because “it’s only ten litres”; the one spark that matters does not care how quick the job is. The wrist strap is that nozzle contact for a '
        'motherboard. “I only needed ten seconds” is how a board ends up with a fault that comes and goes and nobody can reproduce.</p>',
        ['Mat on a stable bench.', 'Clip the mat to the shop ground point.', 'Strap on bare skin, clipped to mat or chassis.',
         'Unbag the board or memory and hold it by the edges.', 'Bag parts again before you walk away.'],
        '<p>Order the ESD routine, then open the lab and practise saying it before each part.</p>',
        order('ESD routine', ['Place the mat', 'Ground the mat', 'Strap on skin', 'Unbag the part', 'Rebag before leaving'],
              'Ground first, then you, then the part; bag it again when you leave.')),
    '3-body-and-path': X('3. Body and path', 'IT-1.2', L12, [
        ('How do you lift a tower off the floor?', 'Bend knees, load close, no twist', 'Bend at the waist and lift it quickly', 'Twist to save steps',
         'Knees bent, load close and no twisting keeps the strain off your back; speed and twisting cause injuries.', LIFT, None),
        ('When do you get a second person?', 'Racks, floor UPS, awkward towers', 'Never; a second person slows the job', 'Only for monitors',
         'Heavy or awkward loads like racks and floor UPS units need a team lift or a cart.', LIFT, None),
        ('In the furniture-mover story, why walk the route first?', 'To find trip hazards before carrying', 'To time how long the job will take', 'To meet the neighbours',
         'You cannot look down at tiles and cables while carrying a chassis, so you check the path before you lift.', LIFT, None),
        ('Cutting zip ties toward your face calls for what?', 'Eye protection', 'Gloves only, nothing else', 'An ESD wrist strap',
         'Snipped ties fly toward the eyes; the protection must match the hazard, so goggles, not just gloves.', PPE, ESDF),
        ('Which shoes are wrong on a raised floor?', 'Open-toe shoes', 'Work boots', 'Closed trainers',
         'Raised floors have tile edges and lifted panels; open toes leave feet exposed when a tile or chassis drops.', PPE, None),
    ],
        '<p>Your body is part of the job. Lift with your knees bent, keep the load close to you and do not twist. Get a second person for racks and floor '
        'UPS units. Look for loose tiles, cables and hatch edges before you walk with a chassis. Wear eye protection when cutting zip ties toward your face, '
        'and wear closed shoes on a raised floor.</p>',
        '<p>Professional furniture movers walk the route before they pick up the sofa: which doors open which way, where the rug curls, where the stairs turn. '
        'Once the sofa is in their arms they cannot see their feet, so the thinking happens first. They also never carry the heavy piece alone just to look '
        'tough. A technician carrying a tower across a server room full of floor tiles and cables is doing the same job on a smaller scale.</p>',
        ['Walk the path: tiles, cables, hatch edges.', 'Decide: one person or two?', 'Feet apart, knees bent, load close.', 'Lift and walk without twisting.',
         'Set it on the bench, not a rolling chair.'],
        '<p>Sort each habit into safe or unsafe.</p>',
        sort('Safe or unsafe?', {'Safe': ['Second person for a floor UPS', 'Goggles when cutting ties', 'Checking tiles first'],
                                 'Unsafe': ['Twisting while carrying', 'Open-toe shoes on a raised floor']},
             'Safe habits plan the lift and match the protection to the hazard.')),
    '4-when-safety-becomes-an-incident': X('4. When safety becomes an incident', 'IT-1.2', L12, [
        ('You smell burning from a PC. First move?', 'Stop and pull power if safe', 'Swap the PSU to test whether it was a fluke', 'Keep working carefully',
         'Burning, scorch, heat or shock means stop; swapping parts “to see if it was a fluke” keeps the hazard alive.', SAFE, HANDS),
        ('What label goes on a hot receptacle ticket?', 'Incident, escalate', 'Break/fix, PSU maybe bad', 'Request, new outlet',
         'A safety hazard is an incident that is escalated to facilities or electrical, not a routine part swap.', SAFE, REQ),
        ('In the smoke-alarm story, why not keep cooking?', 'The alarm means stop first', 'Alarms are usually wrong, so check first', 'Cooking fixes it',
         'Warning signs mean you stop the activity and make people safe before investigating, just like heat or shock on IT gear.', SAFE, None),
        ('What does step 4 of the trace record?', 'What you saw', 'Your guess at the part', 'The user’s password',
         'The note records the observation, such as scorch marks or a hot outlet, so facilities know exactly what they face.', VNOTE, SEC),
        ('Which lab card should get incident + escalate?', 'A warm reader many people use', 'One jammed printer on a busy floor', 'A new hire’s share access',
         'Heat on a device used by many people is a safety incident; the others are break/fix or request.', REQ, SCOPE2),
    ],
        '<p>Some signs mean the job is no longer a repair. A burning smell, scorch marks, a hot wall socket or a user who felt a shock: you stop. You do not keep '
        'swapping power supplies to see whether it was a fluke. Pull power if that is safe, keep people away, call facilities or electrical, and write down '
        'what you saw. In the ticket this is an incident that you escalate, not “PSU maybe bad.”</p>',
        '<p>When the smoke alarm goes off in your kitchen, you do not finish stirring the sauce to see whether it was a false alarm. You turn off the hob, '
        'open the window, get people out of the way and only then look for the cause. A burning smell from a tower or a user who got a shock is the smoke '
        'alarm of the IT world. The repair can wait; the people cannot.</p>',
        ['Notice: smell, scorch, heat or shock.', 'Stop all work on that gear.', 'Pull power if safe; keep people away.', 'Write what you saw and when.',
         'Ticket: incident, escalate to facilities or electrical.'],
        '<p>Order the response to a hot receptacle, then run the lab card that describes heat.</p>',
        order('Hot receptacle response', ['Notice the heat', 'Stop work', 'Pull power if safe', 'Keep people away', 'Escalate with notes'],
              'People first, then power, then the record and the right team.')),
})

LESSONS['1.2'].update({
    'why-the-wall-unplug-matters': X('Why the wall unplug matters', 'IT-1.2', L12, [
        ('Is switching the PSU rocker off the same as unplugging at the wall?', 'No; unplug at the wall', 'Yes, it cuts all power', 'Yes, after ten seconds',
         'Supplies can hold charge in capacitors and the cord still brings power to the inlet; the wall end is what matters.', ESDO, None),
        ('A strap worn over a fleece sleeve is…', 'Jewelry, not protection', 'Fine in winter when it is cold', 'Better insulated',
         'The strap must touch skin to drain charge; fabric breaks the path so it protects nothing.', ESDF, None),
        ('In the garden-hose story, what does water left in the hose stand for?', 'Charge stored after switch-off', 'Static building up on the mat', 'The ground pin',
         'Turning the tap off does not empty the hose, just as the rocker does not drain capacitors; you disconnect and wait.', ESDO, None),
        ('A capacitor looks swollen. What does the trace say?', 'Stop, escalate, do not open', 'Open the PSU and check the capacitor', 'Press it flat',
         'Swollen capacitors, burn smells and shocks are incidents; this course never opens a supply.', OPSU, SAFE),
        ('Why does a burn smell share a label with a building-wide badge failure?', 'Both are incidents: safety first', 'Both are requests for new equipment', 'Both are cosmetic',
         'Both put people at risk or stop many people, so they are incidents handled with stop, protect and escalate.', SAFE, REQ),
    ],
        '<p>The switch on the back of the power supply is not the wall. Even with it off, the supply can keep stored charge in its capacitors. So you unplug the '
        'cord from the wall, wait, and then open the case. The ESD strap goes on bare skin and clips to the same ground as the mat or chassis. You never open '
        'the supply in this course. A swollen capacitor, burn smell or shock from a power strip is an incident: stop, keep people away, escalate.</p>',
        '<p>Turn off an outside tap and the hose still sprays when you squeeze the nozzle: water is trapped inside. Only when you unscrew the hose from the '
        'tap and let it drain is it empty. A power supply is the hose. The rocker switch is the nozzle; the wall plug is the tap connection; the capacitors '
        'are the water still inside. You disconnect at the source and give it a moment before you put your hands in.</p>',
        ['Rocker off.', 'Pull the cord out of the wall socket.', 'Wait for stored charge.', 'Strap on skin, clipped to the shared ground.',
         'Open the panel. Swollen part or burn smell: stop and escalate.'],
        '<p>Decide what you would say to a classmate who only flipped the rocker.</p>',
        reveal('Your classmate flipped the rocker and reached in. What do you say?',
               '“Stop. The rocker is not the wall. Pull the cord out of the wall, wait, strap on skin, then open the panel.”')),
    'lift-path-and-the-bench': X('Lift, path, and the bench', 'IT-1.2', L12, [
        ('Before you pick up a tower, what must you be able to name?', 'Where the wall cord is', 'The CPU model and speed', 'The user’s manager',
         'If the cord is still connected or trailing, lifting can pull gear or trip someone; knowing where it is shows you checked.', LIFT, None),
        ('Where do you rest an open chassis?', 'On the bench', 'On a rolling chair', 'On the floor among boxes',
         'The bench is stable and grounded for open work; a rolling chair can move and drop the chassis.', LIFT, None),
        ('In the airport-trolley story, why park the trolley before unloading?', 'Moving bases drop loads', 'Trolleys are slow to push loaded', 'To save space',
         'A base that rolls shifts the load at the worst moment, which is why a chassis never rests on a rolling chair.', LIFT, None),
        ('The trace asks “one person or two?” for a full tower. When is it two?', 'When it is awkward to carry', 'Never for towers; they have handles', 'Only if a manager says',
         'Awkward size or weight means a team lift, regardless of how strong you feel.', LIFT, None),
        ('Which item belongs on the floor, not the bench?', 'Empty boxes', 'The open chassis', 'The ESD mat',
         'The bench is for open work; boxes go on the floor so the work surface stays clear and stable.', LIFT, None),
    ],
        '<p>Towers and monitors have sharp edges and cords that catch boots. Clear the path before you pick anything up. Use two people for a full tower if it '
        'is awkward. Never rest a chassis on a chair with wheels. The bench is for open work and the floor is for boxes. If you cannot say where the wall cord '
        'is before you lift, you are not ready to lift.</p>',
        '<p>At an airport you would not stack suitcases onto a trolley that is still rolling down a slope. You park it, push it against something, then load '
        'and unload. A chair with wheels is a trolley with no brake. Put a heavy chassis on it, lean in with a screwdriver, and it slides away just when your '
        'hands are inside. The bench is the parked trolley: still, flat and meant for the weight.</p>',
        ['Find the wall cord and unplug it.', 'Clear the floor path.', 'Decide one person or two.', 'Lift with knees, load close.',
         'Place on the bench; boxes on the floor.'],
        '<p>Sort where each thing belongs.</p>',
        sort('Bench or floor?', {'Bench': ['Open chassis', 'ESD mat', 'Bagged memory'], 'Floor': ['Empty boxes', 'Packing foam']},
             'The bench holds the work; the floor holds packaging.')),
    'hour-plan-for-1-2': X('Hour plan for 1.2', 'IT-1.2', L12, [
        ('What happens in the first block of the 1.2 hour plan?', 'Point to cord, rocker, strap, mat ground', 'Open a PSU together as a class demo', 'Write tickets',
         'The opening block builds hand knowledge of where each safety point is, before anyone talks about procedures.', PLANB, OPSU),
        ('In the 20–40 block, what does every person do?', 'Recite and point the open order', 'Watch a safety video quietly', 'Open a PSU',
         'Everyone says and points the five-step order out loud so it becomes a habit; nobody opens a supply.', PLANB, OPSU),
        ('In the fire-drill story, why walk to the exit instead of reading the map?', 'Doing builds the habit', 'Maps are often wrong', 'It is quicker',
         'Practising with your body makes the order automatic under stress, which is the point of each hour-plan block.', PLANB, None),
        ('Which block practises the stop sentence?', 'Shock, heat and smell stories', 'Lift and path, two-person tower', 'Pointing at the tower',
         'The 40–60 block tells shock, heat and smell stories, labels them incident and practises saying stop.', SAFE, PLANB),
        ('The last block maps heat on a reader to ticket-intake. What must you not do?', 'Open the reader', 'Name the heat', 'Escalate to facilities',
         'The note names the heat and says the panel was not opened; opening a hot access-control device is out of scope.', HANDS, None),
    ],
        '<p>The 90-minute plan for 1.2 is hands-on. First you stand at a tower and point to the wall cord, the PSU switch, the strap jack and the mat ground. '
        'Then the class says the five-step open order out loud while everyone points. Next come stories about shocks, heat and smells, each labelled as an '
        'incident with the stop sentence. Then lifting and path practice. Finally you turn heat on a badge reader into ticket-intake language without opening it.</p>',
        '<p>A school fire drill does not hand out a map and ask pupils to memorise it. Everyone stands up, walks the corridor, uses the stairs and lines up '
        'at the meeting point. The first time is slow and silly; by the third, nobody needs to think. When the real alarm sounds, the feet already know the '
        'way. The 1.2 hour plan is a fire drill for your hands: point, recite, rehearse the sentence, lift for real, so the safe order comes without thinking.</p>',
        ['0–20: point to cord, rocker, strap jack, mat ground.', '20–40: recite the five-step open order while pointing.',
         '40–60: shock, heat and smell stories; say the stop sentence.', '60–75: lift and path with a two-person tower.',
         '75–90: write heat-on-a-reader as ticket-intake, panel closed.'],
        '<p>Order the five blocks of the hour plan.</p>',
        order('Hour plan 1.2', ['Point to safety points', 'Recite the open order', 'Stop-sentence stories', 'Lift and path, two-person tower', 'Map heat to ticket-intake'],
              'Hands first, then order, then hazards, then body, then the ticket.')),
    'why-this-chapter-exists-before-hardware': X('Why this chapter exists before hardware', 'IT-1.2', L12, [
        ('Why does safety come before Chapter 2 hardware?', 'Chapter 2 opens side panels', 'Safety is easier to teach first', 'It is a soft skill',
         'Opening a panel without the safety order is how people get hurt and boards die, so the order comes first.', HANDS, None),
        ('What does the course call Block 1?', 'The condition for touching metal', 'Optional soft skills for later', 'An exam warm-up',
         'Block 1 is the permission to work on hardware, not a soft extra you can skip.', PLANB, None),
        ('In the driving-licence story, what is the theory test?', 'The safety order before hardware', 'The hardware chapter that follows', 'The final exam',
         'You learn the rules before you drive on the road; you learn the safety order before you open a case.', NEWB, None),
        ('In the trace, what has to be “in your hands” before step 3?', 'The safety order', 'A new PSU', 'A ticket number',
         'The hands-on safety order must be a habit before you open panels in Chapter 2.', HANDS, None),
        ('Which is a sign you are not ready for Chapter 2?', 'You cannot say the open order', 'You know the strap jack', 'You can name the wall cord',
         'If you cannot say and point the five-step order, you will skip a step when a real panel is in front of you.', ESDO, None),
    ],
        '<p>Chapter 2 will ask you to take off a side panel and touch the parts inside. If the safety order is not already a habit in your hands, that is '
        'exactly when people get shocked and boards get ruined. So Block 1 is not a soft extra. It is the condition you must meet before you touch metal. '
        'Learn it here so that Chapter 2 is about parts, not about accidents.</p>',
        '<p>Before you drive a car alone you pass a theory test and spend hours with an instructor on quiet roads. Nobody calls that the “soft” part of '
        'driving; it is what makes the rest legal and survivable. Chapter 1 is your theory test and quiet-road practice. Chapter 2 is the first time on a '
        'real road with a real engine under the bonnet. Skip the first and the second becomes dangerous.</p>',
        ['Learn the safety order in Chapter 1.', 'Practise it until your hands do it.', 'Open a side panel in Chapter 2.', 'Touch parts only after the order.'],
        '<p>Write one sentence you would say to a classmate who wants to skip straight to Chapter 2.</p>',
        reveal('Your classmate says “Safety is soft stuff, let’s skip to hardware.” Reply?',
               '“Chapter 2 opens panels. Without the safety order in your hands, that is how people get shocked and boards die.”')),
    'the-five-step-open-order-slowly': X('The five-step open order, slowly', 'IT-1.2', L12, [
        ('Which step comes right after unplugging from the wall?', 'Wait', 'Open the panel', 'Unbag the RAM',
         'Stored charge needs a moment to drain, so you wait before strapping on and opening.', ESDO, None),
        ('Is closing a laptop lid the same as powering it off?', 'No; shut it down properly', 'Yes, it cuts all power to the board', 'Yes, after a minute',
         'A closed lid usually means sleep, and the battery still powers the board, so you shut down properly.', ESDO, None),
        ('In the surgery story, why scrub in before the first cut?', 'The order prevents harm', 'To look professional to patients', 'It is optional',
         'Surgeons follow a strict order because skipping one step causes harm; the open order works the same way.', ESDO, None),
        ('Which step in the trace is the classic failure?', 'Opening the panel first', 'Waiting too long after unplugging', 'Strapping on skin',
         'Panel first means every protection afterwards is too late; the order exists to prevent that.', ESDO, HANDS),
        ('Can you snap off a ground pin to fit a two-prong socket?', 'Never', 'Yes, if careful', 'Only for testing',
         'The ground pin is the safety path; removing it means you and the board share any surge.', 'MC-C-IT1-POWER-DEVICE', None),
    ],
        '<p>There are five steps and their order matters. One: shut down from the operating system, then the case switch; closing a laptop lid is not off. '
        'Two: unplug the cord from the wall, because the PSU switch is not the wall. Three: wait so stored charge can drain. Four: strap on bare skin and clip '
        'to the shop’s ground. Five: only then open the panel. Opening the panel first is the classic failure. Never remove a ground pin to fit a socket.</p>',
        '<p>A surgeon does not pick up the scalpel and then remember to wash. The order is fixed: scrub, gown, gloves, check the patient, then cut. '
        'Each step protects the next one, and doing them out of order makes the earlier ones pointless. Your open order is a surgeon’s routine for a PC. '
        'Shut down, unplug, wait, strap, open. Do step five first and steps one to four can no longer help you.</p>',
        ['Shut down from the OS, then the case switch.', 'Unplug the cord at the wall.', 'Wait for stored charge.', 'Strap on bare skin, clip to ground.',
         'Open the panel.'],
        '<p>Put the five steps in order and say each one out loud as you drag it.</p>',
        order('Five-step open order', ['Shut down', 'Unplug at the wall', 'Wait', 'Strap on skin', 'Open the panel'],
              'Each step only works if the one before it is done.')),
    'what-you-never-open': X('What you never open', 'IT-1.2', L12, [
        ('What do you do when a PSU fails?', 'Replace the sealed unit', 'Open it to check a capacitor', 'Tape it shut',
         'Power supplies are field-replaceable units; going inside risks stored charge and is out of scope.', OPSU, None),
        ('An old CRT monitor in a closet is…', 'Not a training toy', 'Safe once unplugged', 'Good for practice',
         'CRTs hold very high voltages long after unplugging, so they are never opened for practice.', OPSU, None),
        ('In the sealed-jar story, why not pry the lid of a swollen jar?', 'Pressure inside can burst', 'Jars are expensive to replace', 'It wastes food',
         'A swollen battery is like a bulging jar under pressure; prying it can cause fire or burns.', OPSU, PPE),
        ('In the trace, a swollen battery sends you where?', 'Stop; it is Chapter 4', 'Pry it out now', 'Puncture to release gas',
         'Swollen batteries are handled in Chapter 4 with proper procedure; in this room you stop and do not pry.', OPSU, None),
        ('Which of these may you open in this course?', 'The PC side panel', 'The PSU housing', 'A CRT monitor shell',
         'Side panels are opened with the safe order; PSUs and CRTs are sealed high-voltage items you replace or leave alone.', OPSU, None),
    ],
        '<p>Some things stay closed. The power supply is a sealed unit you replace. You never go inside to “check a capacitor.” An old CRT monitor in a closet is not a toy for practice. It can hold a dangerous charge. A swollen battery belongs to Chapter 4: stop and do not pry it in this room.</p>',
        '<p>If a jar of preserves in the cupboard has a bulging lid, you do not stab it with a knife to see what happens. The bulge means pressure inside, '
        'and opening it carelessly can spray you. You bin it the safe way. A swollen battery, a CRT and a power supply are bulging jars: the danger is '
        'inside and invisible. Your job is to recognise them and call for the right handling, not to satisfy curiosity.</p>',
        ['Spot the item: PSU, CRT or swollen battery.', 'Do not open, pry or puncture.', 'PSU: replace the whole unit.', 'CRT or battery: stop and follow the shop procedure.'],
        '<p>Sort what you open and what you never open.</p>',
        sort('Open or never open?', {'Open with the safe order': ['PC side panel', 'Antistatic bag'],
                                     'Never open': ['Power supply', 'CRT monitor', 'Swollen battery']},
             'Sealed and high-energy items stay closed; you replace them or escalate.')),
    'when-safety-is-the-ticket': X('When safety is the ticket', 'IT-1.2', L12, [
        ('A reader face is hot and people still use it. What do you say?', '“Stop. I am escalating.”', '“I’ll reseat it quickly.”', '“Probably fine.”',
         'Heat on gear people use is an incident; the stop sentence protects people before anything else.', SAFE, HANDS),
        ('Should you finish a RAM reseat on a box that shocked someone?', 'No; stop and escalate', 'Yes, it is quick and nearly done', 'Yes, wearing gloves',
         'A device that shocked someone is a hazard; finishing other work on it puts you next.', SAFE, PPE),
        ('In the lifeguard-whistle story, what does the whistle stand for?', 'The stop sentence', 'The ticket number', 'The repair',
         'The whistle stops activity first so people are safe, like the stop sentence before you write the ticket.', SAFE, None),
        ('Step 4 of the trace is the note. What must it say?', 'Heat or shock, panel not opened', 'Your guess of the failed PSU model', 'A joke to calm things',
         'The note names the hazard and states you did not open the panel, so the escalation team knows the state.', VNOTE, None),
        ('When is impact “many” on a safety ticket?', 'More than one person in the path', 'Only if ten or more people are there', 'Never for safety',
         'If more than one person could be hurt or blocked, impact is many.', SCOPE2, None),
    ],
        '<p>Sometimes the safety problem is the whole ticket: a shock from a power strip, a burning smell, a hot outlet, a hot reader face while people are still '
        'using it. These are incidents. Your words are “Stop. Do not use that gear. I am escalating.” Then you write it up. You do not finish a quick RAM '
        'reseat on a box that hurt someone. In ticket-intake: incident, impact many if more than one person is in the path, escalate yes, note naming heat or shock.</p>',
        '<p>At a swimming pool, when the lifeguard sees something wrong, the first thing is a long whistle blast and “Everybody out!”. The lifeguard does not '
        'first write a report or try a clever rescue in a crowded pool. People get clear, then the problem is dealt with, then the paperwork. Your stop sentence '
        'is the whistle. It comes before the screwdriver, before the diagnosis and before the ticket text.</p>',
        ['Notice the hazard: shock, burn smell, heat.', 'Say: “Stop. Do not use that gear. I am escalating.”', 'Keep people away; pull power if safe.',
         'Note: incident, impact, escalate yes, heat or shock named, panel not opened.'],
        '<p>Run the lab card and fill all four ticket fields for the warm reader.</p>',
        order('Safety ticket', ['Say the stop sentence', 'Keep people clear', 'Classify incident', 'Escalate yes', 'Write the note'],
              'Words and safety first, then the ticket fields.')),
    'lift-and-path': X('Lift and path', 'IT-1.2', L12, [
        ('If you cannot say the path out loud, you should…', 'Not lift yet', 'Lift quickly', 'Ask the user to lift',
         'Saying the path proves you have planned it; without that you are lifting blind.', LIFT, None),
        ('What is wrong with resting a chassis on a rolling chair?', 'It can roll away', 'It scratches the chair', 'Nothing',
         'Wheels move under load; the chassis can fall just when your hands are inside.', LIFT, None),
        ('In the stage-crew story, why call “clear” before moving scenery?', 'Everyone knows the path', 'To sound official to the audience', 'To start music',
         'Calling the path out loud makes sure it is clear and known before the heavy piece moves.', LIFT, None),
        ('Trace step 1 is “clear the floor.” What does that remove?', 'Trip hazards', 'Static charge', 'The ticket',
         'Cables, boxes and loose tiles cause trips when you cannot see your feet.', LIFT, ESDF),
        ('When is a two-person lift needed?', 'An awkward full tower', 'Any boxed keyboard', 'A boxed 24-inch monitor',
         'Awkward or heavy loads need a team so nobody twists or drops it.', LIFT, None),
    ],
        '<p>This is the short version for the hour. Clear the floor first. Know where the wall cord is. Use two people for an awkward full tower. Never rest '
        'a chassis on a chair with wheels. Monitors have edges and cases have corners. If you cannot say your path out loud, you are not ready to lift.</p>',
        '<p>Backstage in a theatre, the crew moving a heavy flat calls out “Clear! Moving stage left!” before anyone takes a step. Everyone knows where the '
        'piece is going and who is carrying which end. Nobody shoves scenery through a dark wing hoping the path is empty. Saying your lift path out loud is '
        'your “clear” call. It forces you to look, and it tells anyone nearby where a heavy, sharp-cornered object is about to travel.</p>',
        ['Clear the floor.', 'Locate and unplug the wall cord.', 'Say the path out loud.', 'One or two people?', 'Lift and set on the bench.'],
        '<p>Practise saying a path out loud for the tower in front of you.</p>',
        reveal('Say the lift path for a tower from under a desk to the bench.',
               '“Cord unplugged at the wall. Floor clear past the bin. Two of us, I take the front. Set it on the bench by the mat.”')),
    'common-safety-procedures': X('Common safety procedures', 'IT-1.2', ESDS, [
        ('Which extinguisher do you use on an electrical fire?', 'CO2 or clean agent', 'Water', 'Foam for cooking oil',
         'Class C fires involve energised equipment; water conducts, so CO2 or clean agent is used.', WATER, None),
        ('What PPE fits toner clean-up and heavy dust?', 'An air filter mask', 'An ESD wrist strap', 'Ear plugs',
         'Protection must match the hazard; fine particles need a mask, not static or noise protection.', PPE, ESDF),
        ('In the hiking-kit story, why pack different gear for rain and sun?', 'Protection matches the hazard', 'A full bag looks well prepared', 'Rules say so',
         'Each hazard needs its own protection, just like goggles, masks and straps each guard against different risks.', PPE, None),
        ('Per the trace, what does the NIOSH lifting equation start from?', '23 kg (51 lb) ideal', '50 kg for anyone', 'No limit with gloves',
         'NIOSH starts from 23 kg under ideal conditions and lowers it for awkward lifts.', LIFT, None),
        ('Which is correct grounding practice?', 'Use grounded outlets, keep the pin', 'Remove the ground pin so it fits', 'Use any extension',
         'Equipment grounding depends on grounded outlets and intact ground pins.', 'MC-C-IT1-POWER-DEVICE', None),
    ],
        '<p>The A+ Core 2 objective 4.4 lists common safety procedures. Shut down and unplug before opening; never open a supply or monitor high-voltage part. '
        'Use an ESD strap with a resistor connected to a grounded mat, and keep parts in antistatic bags. Use grounded outlets and keep ground pins. Wear '
        'goggles with compressed air or cutting, a mask for toner and dust. Keep cables off walkways. Lift with your knees, keep loads close, team-lift heavy items. '
        'Use CO2 or clean agent on electrical fires, never water, and follow workplace safety law.</p>',
        '<p>When you pack for a hike you do not bring one item for every danger. Rain needs a jacket, sun needs a hat and cream, a steep slope needs boots '
        'with grip, and a long day needs water. Bring only the jacket and you will still get sunburnt. Safety in IT works the same way: the strap is for '
        'static, the goggles for flying debris, the mask for dust, the CO2 extinguisher for an electrical fire. Matching the protection to the hazard is the skill.</p>',
        ['Hazard: electrical → disconnect power, never open PSU.', 'Hazard: static → strap with resistor, grounded mat, bags.',
         'Hazard: debris or dust → goggles or mask.', 'Hazard: heavy load → knees, close, team lift or cart.', 'Hazard: electrical fire → CO2 or clean agent.'],
        '<p>Match each hazard with its protection.</p>',
        sort('Hazard to protection', {'ESD strap and mat': ['Handling memory'], 'Goggles': ['Compressed air cleaning', 'Cutting cable ties'],
                                      'Mask': ['Toner spill'], 'CO2 extinguisher': ['Burning power strip']},
             'Every control matches one hazard; none covers them all.')),
})


LESSONS.setdefault('1.3', {}).update({
    'why-writing-is-part-of-the-repair': X('Why writing is part of the repair', 'IT-1.3', L13, [
        ('You fixed the PC but wrote nothing. What happens next?', 'The next person repeats or undoes it', 'Nothing; it is fixed for good', 'The user writes the ticket up for you',
         'Without notes the shop has no memory, so the next technician starts over or makes it worse.', VAGUE, 'MC-IT1-CLOSE-EARLY'),
        ('How does a 24-hour shop keep working across shifts?', 'Through the written record', 'Through one expert on call', 'Through memory and luck',
         'Shifts change; only the ticket carries what was done from one person to the next.', VAGUE, None),
        ('In the hospital-chart story, what does the chart stand for?', 'The ticket', 'The repair tool', 'The user',
         'Nurses change shifts but the chart tells the next one what was given and when, exactly like a ticket.', VAGUE, None),
        ('In the trace, what comes right after the fix?', 'Write what you did', 'Close and walk away', 'Start the next job',
         'The write-up is part of finishing; the job is not done until it is recorded.', 'MC-IT1-CLOSE-EARLY', None),
        ('Which statement matches the section?', 'Documentation is part of the job', 'Notes are an extra if time allows at the end', 'Only big jobs need notes',
         'Writing is not extra; it is how the shop exists across days and people.', VAGUE, None),
    ],
        '<p>Fixing the computer is only half the job. If you walk away without writing anything, the shop has no memory of what happened. The next person who '
        'sees that PC repeats your work, or undoes it by accident. Writing is not an extra chore at the end. It is how a shop that runs day and night keeps '
        'working when the people change.</p>',
        '<p>In a hospital, nurses change shifts every twelve hours, but the patient stays. The chart at the end of the bed says what medicine was given, '
        'when, and how the patient reacted. A nurse who gives a dose and does not write it down puts the patient in danger, because the next nurse may give it '
        'again. A ticket is the chart for a computer or a user. The fix without the note is a dose nobody knows about.</p>',
        ['Diagnose the problem.', 'Do the fix.', 'Write what you did and what you saw.', 'The next shift reads it and continues.'],
        '<p>Write one line you would add to a ticket after reseating RAM.</p>',
        reveal('You reseated RAM and the PC now boots. One ticket line?', '“Reseated DIMM in slot A2 after MEM beep → POST passes, Windows loads. Monitoring.”')),
    '1-anatomy-of-a-usable-ticket': X('1. Anatomy of a usable ticket', 'IT-1.3', L13, [
        ('Which test line is a usable fact?', '“Ping 10.20.30.1 → 4/4, 1 ms”', '“Pinged the gateway and it was fine”', '“Network looked OK”',
         'A test is only useful with its result; action plus result lets the next person trust it.', VNOTE, VAGUE),
        ('Which item belongs in a usable ticket?', 'When it started and what changed', 'Your honest opinion of the user’s skill', 'The user’s password',
         'Start time and recent changes point to causes; opinions and secrets never belong.', SEC, None),
        ('In the recipe story, why list quantities, not “some flour”?', 'Someone else must repeat it', 'It looks tidy on the page', 'Cooks like numbers',
         'A recipe works only if a stranger can follow it; ticket lines need the same precision.', VNOTE, None),
        ('Trace step 5 is tests. How are they written?', 'Action → result pairs', 'One summary word', 'Only the failing ones',
         'Each test is an action with its result, including passes, so nobody repeats it.', VNOTE, VAGUE),
        ('Which field tells the next person what to do?', 'What is still true and the next action', 'Who / where the user sits in the building', 'Exact error text',
         'The final field leaves a clear next step so the work continues.', VAGUE, None),
    ],
        '<p>A usable ticket answers these questions: who, where and how many people; what they needed to do; the exact error message or behaviour; when it '
        'started, when it last worked and what changed; each test you ran and its result; what you did; and what is still true plus the next action. '
        'Write tests as pairs: what you did, then what happened. “Pinged gateway” is not enough. “Ping 10.20.30.1, 4 of 4 replies, 1 ms” is a fact.</p>',
        '<p>A good recipe never says “add some flour and bake until done.” It says 250 g flour, 180 °C, 25 minutes, until a skewer comes out clean. Someone '
        'who has never met the cook can follow it and get the same cake. A ticket is a recipe for whoever picks up the job next. Every line should be precise '
        'enough that a stranger, at another desk, at another hour, can repeat or continue your work without guessing.</p>',
        ['Who / where / how many.', 'Outcome they need.', 'Exact error text or behaviour.', 'Started / last good / what changed.',
         'Tests: action → result.', 'What you did.', 'Still true + next action.'],
        '<p>Order the fields of a usable ticket.</p>',
        order('Ticket fields', ['Who and where, with building', 'Outcome', 'Exact error', 'When and what changed', 'Tests with results', 'What you did', 'Next action'],
              'Context first, evidence in the middle, next action last.')),
    '2-facts-versus-guesses': X('2. Facts versus guesses', 'IT-1.3', L13, [
        ('Which line is a fact?', '“Password loop since the patch window”', '“Probably the domain controller is down again”', '“Must be a bad NIC”',
         'A fact describes what you saw; the others are guesses about a cause.', VNOTE, None),
        ('What do you do with a guess in a ticket?', 'Label it as a guess or omit it', 'Write it as a confirmed finding', 'Put it in capitals',
         'The next technician treats unlabelled guesses as measured truth.', VNOTE, VAGUE),
        ('In the weather-forecast story, why say “60% chance”?', 'It marks uncertainty', 'It sounds clever', 'Rules require numbers',
         'Labelling uncertainty lets people decide well; a guess written as a fact misleads.', VNOTE, None),
        ('In the trace, what happens if a guess is unlabelled?', 'The next tech trusts it as fact', 'Nothing changes; people re-test everything', 'The ticket closes',
         'Unlabelled guesses steer the next person down the wrong path.', VNOTE, None),
        ('How should you write a hunch about the DC?', '“Guess: DC auth issue (untested)”', '“Cause: DC auth failure”', '“Root cause: DC authentication down”',
         'Marking it as a guess and untested keeps facts and ideas apart.', VNOTE, None),
    ],
        '<p>A fact is something you saw or measured, such as “Outlook shows a password prompt in a loop after the weekend patch window.” A guess is what you '
        'think might be causing it, such as “probably the domain controller.” Mark guesses clearly as guesses, or leave them out. The next technician will '
        'treat anything in the ticket as tested truth.</p>',
        '<p>A weather forecaster does not say “it will rain tomorrow” when the models disagree. They say “60 percent chance of showers.” People plan around '
        'that honesty: some take an umbrella, some risk it. If the forecaster stated every hunch as certain, nobody could trust any forecast. Your ticket is a '
        'forecast for the next technician. Facts are the measurements; guesses must carry their “60 percent” label.</p>',
        ['Observe: what does the screen or user show?', 'Write it as a fact with time.', 'Have a hunch? Mark it “guess, untested.”', 'Test the hunch.',
         'Turn it into a fact or drop it.'],
        '<p>Sort each line into fact or guess.</p>',
        sort('Fact or guess?', {'Fact': ['Error 809 at 0915', 'Ping gateway 0/4', 'Loop started after patch'],
                                'Guess': ['Probably the DC', 'Maybe a bad cable']},
             'Facts are observations with detail; guesses are possible causes.')),
    '3-change-awareness': X('3. Change awareness', 'IT-1.3', L13, [
        ('Adding a firewall rule is a…', 'Change', 'Repair', 'Request only',
         'It introduces something new that can affect others, so it is a change and follows the change process.', CHG, CHGU),
        ('Policy says no production DNS after 1500. A user asks at 1510. You…', 'Use the change process', 'Just add the record since it is quick', 'Add it and note later',
         'Policy and the change process apply even for quick changes; “just adding” is how outages start.', CHGU, CHG),
        ('In the painting story, why is repainting a change?', 'It needs timing, warning and a way back', 'It changes how the room looks', 'It costs more than a quick clean-up',
         'Changes affect others and need planning and rollback, unlike swapping a bulb back to normal.', CHG, None),
        ('In the trace, reseating RAM is labelled…', 'Repair', 'Change', 'Incident',
         'Reseating returns a known-good state, so it is a repair, though it still gets notes.', CHG, None),
        ('Do repairs need notes?', 'Yes, always', 'No, only changes', 'Only if they fail',
         'Repairs still get notes; changes also need the change process.', VAGUE, None),
    ],
        '<p>A <strong>change</strong> is a planned alteration that can affect someone else: imaging a PC, adding a group, a firewall rule, a DNS record, '
        'firmware, a major upgrade. A <strong>repair</strong> puts a known-good state back, like reseating RAM or replacing a failed disk with the same kind. '
        'Repairs still get notes. Changes also go through the local change process. If policy says no production DNS after 1500, you do not “just add a record.”</p>',
        '<p>On a ship, swapping a burnt-out bulb in a passageway is a repair: it returns things to how they were. Repainting that passageway during watch '
        'turnover is a change: people need warning, it has to happen at a sensible time, and if the paint is wrong you need a way back. Nobody repaints a '
        'busy corridor on a whim because it “only takes a minute.” IT changes are repaintings; repairs are bulbs.</p>',
        ['Ask: am I restoring a known-good state?', 'Yes → repair; write notes.', 'No, something new → change.', 'Check policy and window.',
         'Use the change process, with a way back.'],
        '<p>Sort each job into repair or change.</p>',
        sort('Repair or change?', {'Repair': ['Reseat RAM', 'Replace failed disk with same role'],
                                   'Change': ['Add a firewall rule', 'Image a PC', 'Add a DNS record']},
             'Repairs restore; changes introduce.')),
    '4-note-quality-bar-for-the-lab': X('4. Note quality bar for the lab', 'IT-1.3', L13, [
        ('Will the lab accept the note “fixed”?', 'No; one-word notes fail', 'Yes, it is short', 'Yes, if you submit fast',
         'The lab requires an outcome, an observation and a next step.', VAGUE, None),
        ('What three parts does a lab note need?', 'Outcome, observation, next step', 'Name, date and how the user feels', 'Error, password, guess',
         'Outcome, one observation and a next step make a note someone can act on.', VAGUE, SEC),
        ('In the postcard story, why write more than “Hi”?', 'The reader needs real news', 'Postcards have lots of space to fill', 'Stamps cost money',
         'A note must carry information; a one-word note is a postcard that only says hi.', VAGUE, None),
        ('In the trace, submit fails. What next?', 'Show ticket, fill missing fields', 'Submit again unchanged until it passes', 'Delete the note',
         'Failed submits mean a field is missing; show the ticket and fill classify, impact or escalate.', VAGUE, None),
        ('Which note passes the bar?', '“Cannot send since 0700; loop; escalate”', '“Outlook broken; user upset”', '“Restarted Outlook; works; closed ticket”',
         'It has the outcome, an observation and a next step; the others do not.', VAGUE, None),
    ],
        '<p>The lab will not accept a one-word note. Your note must have three parts: the outcome, one thing you observed, and a next step. For example: '
        '“User cannot send mail since 0700. Outlook 16 password loop. Tried cached mode off, still loops. Escalate to messaging for account lock check.” '
        'Then submit. If submit fails, show the ticket and fill in classify, impact or escalate.</p>',
        '<p>Imagine getting a postcard from a friend on holiday that says only “Hi.” You know they are alive, but nothing else: where they are, how it is '
        'going, when they come back. A good postcard says where, what happened, and what is next. The lab’s note box is a postcard to the next technician. '
        '“Fixed” is “Hi.” Three short sentences give them the news they need.</p>',
        ['Write the outcome: who cannot do what.', 'Add one observation: error or test result.', 'Add the next step: person or command.', 'Submit.',
         'If it fails: show ticket, fill missing fields.'],
        '<p>Open the lab and write a three-part note before you submit.</p>',
        order('Lab note', ['Outcome', 'Observation', 'Next step', 'Submit'], 'All three parts come before submit.')),
    'ticket-b-versus-ticket-a': X('Ticket B versus Ticket A', 'IT-1.3', L13, [
        ('Why is “VPN broken” a weak ticket?', 'The next watch learns nothing', 'It is too long for the ticket field', 'It names the cause',
         'It has no version, error, tests or timing, so nobody can continue.', VAGUE, None),
        ('What makes a test line complete?', 'Action and its result', 'Just the action you took', 'Just a feeling',
         'A test without a result is a slogan.', VNOTE, None),
        ('In the treasure-map story, what makes map B useful?', 'Landmarks and distances', 'Nice colours and a neat border', 'A big X only',
         'Detail lets a stranger follow the route, like Ticket B’s evidence.', VAGUE, None),
        ('In the trace, adding a DNS record is a…', 'Change', 'Repair', 'Test',
         'It introduces something new, so it uses the change process.', CHG, CHGU),
        ('Which line belongs in Ticket B?', '“Error 809; gateway ping fails”', '“VPN broken for user”', '“VPN fails; user will retry later”',
         'Ticket B lists errors and test results.', VAGUE, None),
    ],
        '<p>Ticket A says “VPN broken.” The next shift learns nothing. Ticket B says: client version, error 809, local network ping works, gateway ping fails, '
        'started after the weekend update, user is on hotel Wi-Fi. With Ticket B, someone can continue at 2 a.m. without calling you. Every test is an action '
        'plus result. A repair puts back a known-good state; a change introduces something new and uses the shop process.</p>',
        '<p>Two pirates leave treasure maps. Map A has a big X and the word “beach.” Map B says: from the broken mast, forty paces north, past the twin palms, '
        'dig under the flat rock. Only map B can be followed by someone who was not there. Your tickets are maps for whoever comes next. Ticket A is the big X; '
        'Ticket B gives landmarks, distances and what you already dug up.</p>',
        ['Start with Ticket A: “VPN broken.”', 'Add version and error code.', 'Add tests: LAN ping OK, gateway ping fails.', 'Add timing: after weekend update.',
         'Add context: hotel Wi-Fi. Now it is Ticket B.'],
        '<p>Rewrite a Ticket A into a Ticket B.</p>',
        reveal('Rewrite Ticket A: “Email not working.”', '“Outlook 16 on PC118, send fails with 0x800CCC0F since 0800; OWA works; ping mail01 4/4; next: messaging check SMTP auth.”')),
    'hour-plan-for-1-3': X('Hour plan for 1.3', 'IT-1.3', L13, [
        ('What opens the 1.3 hour plan?', 'Rewriting Ticket A’s into B’s', 'A lecture on DNS record types', 'Opening a PC',
         'The plan starts by turning slogans into evidence on the board.', PLANB, None),
        ('What is drilled in the 20–45 block?', 'Action → result pairs', 'Typing speed and accuracy', 'Ticket colours',
         'Every test becomes a pair until the habit is automatic.', VNOTE, PLANB),
        ('In the music-scales story, why repeat scales?', 'Repetition builds habit', 'Scales are fun to play', 'Teachers insist',
         'Repeating the pattern makes it automatic, like action → result drills.', PLANB, None),
        ('What does the trace end with?', 'One full Ticket B, peer scored', 'A short quiz on DNS and DHCP', 'A peer chat about tickets',
         'Each trainee writes one complete Ticket B and peers score it.', PLANB, None),
        ('Which block covers when the change process applies?', 'Repair vs change', 'Ticket A vs Ticket B', 'Peer scoring',
         'The 45–70 block uses four shop examples to decide repair or change.', CHG, None),
    ],
        '<p>The 1.3 lesson runs in four blocks. First 20 minutes: Ticket A versus Ticket B on the board, and the class rewrites three weak tickets into strong '
        'ones. Next 25 minutes: action and result drills, where every test is written as a pair. Then 25 minutes on repair versus change with four shop '
        'examples. The last 20 minutes: each trainee writes one full Ticket B from a raw sentence and a partner scores it.</p>',
        '<p>A piano student does not learn by reading about scales. They play them, slowly, every day, until the fingers move on their own. Then they play a '
        'real piece and the scales are already inside it. The 1.3 hour plan is scale practice for tickets: rewrite weak ones, drill action-result pairs, sort '
        'repairs from changes, then perform a full Ticket B in front of a peer.</p>',
        ['0–20: Ticket A vs B; rewrite three.', '20–45: action → result drills.', '45–70: repair vs change, four examples.', '70–90: write one Ticket B; peer scores.'],
        '<p>Order the four blocks.</p>',
        order('Hour plan 1.3', ['Ticket A vs Ticket B', 'Action → result drills', 'Repair vs change', 'Write and peer-score Ticket B'],
              'From examples to drills to judgment to a full performance.')),
    'anatomy-of-ticket-b': X('Anatomy of Ticket B', 'IT-1.3', L13, [
        ('Which line is required in Ticket B?', 'Who and where, with hostname', 'Your shift and lunch plans', 'The user’s password',
         'Location and hostname tell a stranger where the problem is.', SEC, None),
        ('What test for a note works best?', 'Could it survive you going to lunch?', 'Is it short enough to read fast?', 'Does it use jargon?',
         'If someone else could continue while you are away, the note is Ticket B.', VAGUE, None),
        ('In the baton-board story, what does the board hold?', 'The handover facts', 'The score and the time left', 'The rules',
         'A handover board holds the facts the next team needs, like Ticket B lines.', VAGUE, None),
        ('In the trace, what comes after tests?', 'What you already did', 'Who and where, with building', 'The outcome',
         'After evidence you record your actions, then the next person or command.', VAGUE, None),
        ('What is Ticket A described as?', 'A slogan', 'Evidence', 'A change record',
         '“VPN broken” is a slogan; Ticket B is evidence.', VAGUE, None),
    ],
        '<p>Ticket B has required lines written so a stranger can use them: who and where (desk, building, hostname if known); the outcome they need; when it '
        'last worked and what changed; tests as action and result; what you already did; and the next person or next command. Ticket A is a slogan. Ticket B '
        'is evidence. If your note cannot survive you going to lunch, it is still Ticket A.</p>',
        '<p>Factory teams at shift change use a whiteboard by the line: which machine, what is wrong, what was tried, what to do next. The outgoing lead fills '
        'it in so the incoming lead can start without a phone call. If the board says only “line 3 bad,” the new team wastes the first hour. Ticket B is that '
        'whiteboard filled in properly, so your lunch break does not stop the work.</p>',
        ['Who and where.', 'Outcome needed.', 'Last worked / what changed.', 'Tests: action → result.', 'What you did.', 'Next person or command.'],
        '<p>Sort lines into Ticket A or Ticket B.</p>',
        sort('Ticket A or B?', {'Ticket B': ['PC214, Bldg 2', 'Gateway ping 0/4', 'Next: messaging team'], 'Ticket A': ['VPN broken', 'Looks bad']},
             'Ticket B lines carry specifics; Ticket A lines are slogans.')),
    'action-result-until-it-is-boring': X('Action → result until it is boring', 'IT-1.3', L13, [
        ('Rewrite “Checked Outlook.” Which is right?', '“Cached mode off → still loops”', '“Outlook checked, looks fine”', '“Looked at Outlook”',
         'The right line names the action and what happened.', VNOTE, None),
        ('Which ipconfig line is a proper result?', '“169.254.27.8, no DHCP server”', '“IP address looks weird”', '“Ran ipconfig, IP address is wrong”',
         'It records the exact address and what it means, not a feeling.', VNOTE, None),
        ('In the lab-notebook story, why write every reading?', 'Others must check it', 'To fill pages', 'Teachers count pages',
         'Scientists log action and reading so others can verify; tickets need the same.', VNOTE, None),
        ('The trace says do ten. Why?', 'Until the habit is automatic', 'To fill the lab period', 'Ten is the weekly ticket quota',
         'Repetition until boring makes action → result the default.', PLANB, None),
        ('Which is wrong?', '“Looks fine.”', '“Ping 10.20.30.1 — 0/4 timeout.”', '“Cached mode off — still loops.”',
         '“Looks fine” has no action or measured result.', VNOTE, None),
    ],
        '<p>Practise writing every test as an action and its result until it is boring. Wrong: “Pinged the gateway.” Right: “Ping 10.20.30.1, 0 of 4, timeout.” '
        'Wrong: “Checked Outlook.” Right: “Cached mode off, still password loop, error 809.” Wrong: “Looks fine.” Right: “ipconfig /all shows 169.254.27.8, '
        'DHCP enabled, no DHCP server listed.” Do ten of these on scrap paper. The lab note is the same habit in a smaller box.</p>',
        '<p>In a school science lab, you do not write “heated the water, it got hot.” You write “heated 200 ml for 3 minutes, temperature 72 °C.” Anyone can '
        'check your work, repeat it and compare. Scientists keep notebooks this way because memory lies and vague words hide mistakes. Your ticket is a lab '
        'notebook. The action is the experiment, the result is the reading, and both go on the same line.</p>',
        ['Write the action: command or step.', 'Add an arrow.', 'Write the exact result: numbers, codes, messages.', 'Repeat ten times on scrap paper.'],
        '<p>Fix three wrong lines into action → result pairs.</p>',
        reveal('Fix: “Rebooted, better.”', '“Restarted PC118 at 1020 → login 40 s (was 4 min); Outlook opens; send test → delivered.”')),
    'repair-versus-change-with-shop-examples': X('Repair versus change, with shop examples', 'IT-1.3', L13, [
        ('Imaging a staff PC is a…', 'Change', 'Repair', 'Request only',
         'It creates a new OS state needing backup and a window, so it is a change.', CHG, None),
        ('Replacing a failed PSU with the same FRU is a…', 'Repair', 'Change', 'Incident',
         'It returns a known-good state; you still document it and do not open the old unit.', CHG, OPSU),
        ('In the house story, why is a new wall different from a new bulb?', 'It alters shared structure', 'It costs more money to do', 'It is louder',
         'Changing structure affects others and needs approval, unlike restoring a part.', CHG, None),
        ('In the trace, turning Secure Boot off temporarily is…', 'A change that must go back', 'A repair that stays', 'A setting not worth noting',
         'It alters security state and must be reverted, so it is a change.', CHG, CHGU),
        ('Changing an AP admin password is a change because…', 'It is shared infrastructure', 'It is quick and easy to do', 'It fixes a security issue',
         'Shared infrastructure changes affect others and need the process.', CHGU, None),
    ],
        '<p>Here are shop examples. Reseating RAM after a memory beep is a repair: it returns a known-good seat. Replacing a failed power supply with the same '
        'part is a repair; still document it and do not open the old one. Adding a production DNS record is a change, because something new exists. Imaging a '
        'staff PC, changing the Wi-Fi admin password, and turning Secure Boot off for a USB are all changes. Changes use the shop process, even for two minutes.</p>',
        '<p>In a rented flat, replacing a dead light bulb with the same kind is something you just do. Knocking through a wall to make the kitchen bigger is '
        'not, even if you are quick with a hammer: the landlord, neighbours and building rules all care. IT works the same. Restoring a part is the bulb. '
        'Adding a DNS record, imaging a PC or changing a shared password is the wall.</p>',
        ['Reseat RAM → repair.', 'Same-FRU PSU swap → repair.', 'Production DNS record → change.', 'Image a staff PC → change.',
         'AP password or Secure Boot off → change.'],
        '<p>Sort each shop job into repair or change.</p>',
        sort('Repair or change?', {'Repair': ['Reseat RAM after MEM beep', 'Same-FRU PSU swap'],
                                   'Change': ['Image a staff PC', 'Change AP admin password', 'Secure Boot off for USB']},
             'Restoring is repair; anything new or shared is change.')),
    'what-never-goes-in-the-ticket': X('What never goes in the ticket', 'IT-1.3', L13, [
        ('Which item must never go in a ticket?', 'A password', 'An error code', 'A test result',
         'Passwords are secrets; tickets are widely read and stored.', SEC, None),
        ('You have a hunch about the cause. In the ticket you…', 'Label it as a guess', 'State it as fact', 'Leave out all ideas forever',
         'Guesses may go in only when clearly labelled.', VNOTE, None),
        ('In the public-noticeboard story, why not pin your bank PIN?', 'Anyone can read it', 'The board is small', 'It falls off',
         'Tickets are read by many people, like a noticeboard.', SEC, None),
        ('The trace lists items to remove. Which?', 'Jokes about the user', 'Times of each test', 'Hostname',
         'Jokes and rants are unprofessional and may be read by the user.', ARGUE, None),
        ('Full SSNs in a ticket are…', 'Never allowed', 'Fine if internal', 'Fine if masked later',
         'Sensitive personal data does not belong in tickets.', SEC, PRIV),
    ],
        '<p>Some things never go in a ticket: passwords, full social security numbers, jokes about the user, rants about another shop, and guesses written as if '
        'they were measured. If you must write a guess, label it as a guess. Tickets are read by many people, sometimes including the user.</p>',
        '<p>Think of the noticeboard in a shared office kitchen. Anyone walking past can read it: colleagues, cleaners, visitors. You would not pin your bank PIN '
        'there, or a nasty joke about a colleague, or a complaint about another team. A ticket system is that noticeboard. Lots of people read it, now and years '
        'later. Write only what you would be happy for the user, your lead and an auditor to read.</p>',
        ['Draft the note.', 'Remove passwords and full IDs.', 'Remove jokes and rants.', 'Label any guess.', 'Save.'],
        '<p>Sort what goes in and what stays out.</p>',
        sort('In or out?', {'In the ticket': ['Error 809 at 0915', 'Ping result'], 'Never': ['User’s password', 'Joke about the user', 'Full SSN']},
             'Facts in; secrets and opinions out.')),
})


LESSONS.setdefault('1.4', {}).update({
    '1-talk-to-the-outcome': X('1. Talk to the outcome', 'IT-1.4', L14, [
        ('Which sentence suits the user best?', '“No usable address; renewing it now”', '“Your DHCP lease failed, NIC has APIPA”', '“It’s a layer-3 issue, hang on a sec”',
         'Users need the outcome and next step in plain words, not protocol names.', JARG, JARG),
        ('On a long incident, what do users need from you?', 'Who, what is known, next check-in', 'Silence until it is completely fixed', 'A full technical log every five minutes',
         'Silence reads as neglect; a short update with a check-in time keeps trust.', 'MC-L-NO21-STATUS' if False else ARGUE, JARG),
        ('In the pilot-announcement story, why say “twenty minutes delay”?', 'Passengers need impact and time', 'Pilots enjoy talking a lot', 'Engine details reassure everyone',
         'People need to know what it means for them and when, not the mechanics.', JARG, None),
        ('Trace step 3 is the fallback. What is it here?', 'Move them to a spare PC', 'Explain APIPA in more detail', 'Close the ticket and leave',
         'Offering a fallback keeps the user working if the first fix fails.', 'MC-IT1-CLOSE-EARLY', JARG),
        ('Which update is best during an outage?', '“Mail is down; next update 1400”', '“Working on it, will tell you sometime”', '“Exchange DAG failover in progress now”',
         'It says what is affected and when you will update next, in plain words.', JARG, JARG),
    ],
        '<p>Talk to users about what they can and cannot do, not about the technology. Bad: “Your DHCP lease failed to renew so the NIC has an APIPA address.” '
        'Better: “This PC does not have a usable network address. I am renewing it. If that fails I will move you to a spare.” On a long incident, tell people '
        'who is affected, what you know and when you will check in next. Silence feels like neglect.</p>',
        '<p>When a plane is delayed, the pilot does not announce “we have a hydraulic pressure fault in the number two system.” They say “we have a small '
        'technical issue, engineers are on it, we expect about twenty minutes, I will update you in ten.” Passengers relax because they know what it means for '
        'them and when they will hear more. Talking to the outcome is your cabin announcement: impact, plan, next update.</p>',
        ['Say what they cannot do right now.', 'Say what you are doing in plain words.', 'Offer a fallback if it fails.', 'Give the next check-in time.'],
        '<p>Rewrite a jargon sentence for a user.</p>',
        reveal('Rewrite for a user: “Your profile’s NTUSER.DAT is corrupt.”', '“Your Windows settings file is damaged. I will set up a fresh one; your files stay. About 20 minutes.”')),
    '2-privacy-on-a-real-floor': X('2. Privacy on a real floor', 'IT-1.4', L14, [
        ('Can you use someone else’s account “just to test”?', 'No, never', 'Yes, if it is quick and you log out', 'Yes, if the user is on leave',
         'Using another person’s account breaks accountability and privacy.', PRIV, URG),
        ('Before screenshotting a remote session, you…', 'Close their mail and chat', 'Capture everything for context', 'Ask a colleague to take it',
         'Private content stays private; crop or close before capturing.', PRIV, PRIV),
        ('In the doctor’s-waiting-room story, why not read charts aloud?', 'Others can hear private details', 'It slows the queue down a bit', 'Patients prefer reading',
         'Private information shared in public spaces is a breach.', PRIV, None),
        ('Trace step 1 when remoting in is…', 'Say what you can see', 'Silently browse their files', 'Open their email first',
         'Telling the user what is visible keeps trust and privacy.', PRIV, PRIV),
        ('Where should ticket details not be read aloud?', 'On speakerphone in a passageway', 'In a private office with the user', 'In the written ticket system',
         'Public spaces leak private details.', PRIV, None),
    ],
        '<p>Privacy matters on a busy floor. Do not read ticket details over a speakerphone in a corridor. Do not leave someone’s email open on a shared screen. '
        'Never paste passwords into a ticket. Never use another person’s account “just to test.” When you remote in, tell the user what you can see. Close '
        'their mail and chat before taking a screenshot, and crop error messages if the rest of the screen is private.</p>',
        '<p>In a doctor’s waiting room, the receptionist does not shout “Mr Jones, about your rash!” across the room. Charts are kept face down, and private '
        'conversations happen behind a door. Everyone understands that health details are private. A user’s screen, mail and chat deserve the same care. '
        'You are the receptionist with access to everyone’s chart; your job is to see only what you need and keep it from everyone else.</p>',
        ['Remote in and say what you can see.', 'Close mail and chat before capturing.', 'Crop to the error dialog.', 'Never use their account to test.',
         'Keep speakerphone details out of corridors.'],
        '<p>Sort each action into private-safe or a breach.</p>',
        sort('Safe or breach?', {'Safe': ['Cropping an error dialog', 'Saying what you can see'],
                                 'Breach': ['Testing with another person’s account', 'Leaving mail open on a shared screen']},
             'Safe actions limit what is seen; breaches expose it.')),
    '3-saying-no': X('3. Saying no', 'IT-1.4', L14, [
        ('“Add me to Finance-Share real quick” without approval. You say…', 'No; I’ll open a request to the owner', 'Sure, I’ll add you now and note it', 'OK, but only for today',
         'Access needs the owner’s approval; you stay useful by opening the request.', URG, CHGU),
        ('A user wants the firewall off so a launcher works. You…', 'Refuse and help with an approved app', 'Disable it for an hour then re-enable', 'Turn it off if they sign',
         'Disabling security is a no; you can help them use the approved path.', URG, URG),
        ('In the bouncer story, why does the bouncer stay polite?', 'Firm and calm keeps control', 'Bouncers are paid to smile', 'The guest is always right',
         'A refusal is firm on the rule and calm in tone.', ARGUE, ARGUE),
        ('In the trace, the caller raises their tone. Next step?', 'Escalate the ticket to a lead', 'Give in to calm them down quickly', 'Hang up immediately',
         'You escalate the ticket, not trade policy for peace.', ARGUE, URG),
        ('Saying no still means…', 'Offering the approved path', 'Ending the conversation politely', 'Ignoring the request',
         'You remain useful by pointing to the right process.', ARGUE, None),
    ],
        '<p>Sometimes the right answer is no. “Add me to Finance-Share real quick” without approval is a no. “Disable the firewall so this launcher works” is a '
        'no. You can still help: open a request to the owner of the share, or help them use the approved app. If the user gets angry, you escalate the ticket '
        'to a lead. You do not trade policy for peace.</p>',
        '<p>A good nightclub bouncer turns people away every night without a fight. They do not shout or argue; they say “Not tonight, mate, you need ID,” '
        'point to the rule and stay calm. If someone kicks off, they call the manager rather than bending the rule to make the noise stop. Your refusals work '
        'the same way: calm voice, clear rule, helpful alternative, and a lead if it heats up.</p>',
        ['Hear the request.', 'Check: allowed without approval?', 'If not: say no calmly.', 'Offer the approved path.', 'Tone rises: escalate to a lead.'],
        '<p>Write one refusal with an alternative.</p>',
        reveal('Refuse: “Just give me admin rights for this install.”', '“I can’t grant admin from here. I can install the approved version for you now, or open a request to your manager.”')),
    '4-what-goes-in-the-ticket': X('4. What goes in the ticket', 'IT-1.4', L14, [
        ('Which belongs in the ticket?', 'Facts, times, tests, changes', 'Opinions about the user’s attitude', 'The user’s password',
         'Tickets hold facts and status, never jokes or secrets.', ARGUE, SEC),
        ('Where do judgment calls go first?', 'To a lead, then a short line', 'Straight into a long rant', 'Nowhere; keep them to yourself',
         'Leads make the judgment; the ticket gets a factual line.', ARGUE, None),
        ('In the court-record story, why is the record plain?', 'Others rely on it later', 'Stenographers dislike emotion', 'Paper is expensive',
         'Records are for future readers, so they stay factual.', VAGUE, None),
        ('In the trace, what does the last step check?', 'It reads as a clean note', 'It is as long as possible', 'It includes your opinion',
         'The lab and the shop want a clean, factual note.', VAGUE, None),
        ('A rant about another shop belongs…', 'Nowhere in the ticket', 'In the notes section', 'In capitals at the top',
         'Rants are unprofessional and unhelpful to the next reader.', ARGUE, None),
    ],
        '<p>The ticket holds facts, times, tests, changes and what the user can see. It does not hold jokes about the user, raw passwords or a rant about another '
        'team. If something needs a judgment call, take it to a lead first, then write a short factual line about the decision. The lab wants a clean note, and '
        'that is the standard everywhere.</p>',
        '<p>A court stenographer records exactly what was said and when, without commentary. Years later a judge, a lawyer or a journalist may read that record '
        'and rely on it. If the stenographer had added “witness seemed shifty, lol,” the record would be worthless. Your ticket is a court record for the '
        'repair: plain, timed and factual, because someone you have never met will rely on it.</p>',
        ['Write facts and times.', 'Add tests and changes.', 'Add user-visible status.', 'Judgment call? Ask a lead, then one factual line.',
         'Re-read: clean and factual?'],
        '<p>Sort lines into in-the-ticket or not.</p>',
        sort('Ticket or not?', {'In the ticket': ['Changed DNS at 1410', 'User can print again'], 'Not in the ticket': ['“User is clueless”', 'Rant about the network team']},
             'Facts and status go in; opinions stay out.')),
    'two-audiences': X('Two audiences', 'IT-1.4', L14, [
        ('What does the user need from you?', 'Outcome, time, what you need', 'DHCP and APIPA details in full', 'A copy of the technical ticket',
         'Users need plain outcome and next steps, not protocol detail.', JARG, JARG),
        ('What happens when channels mix?', 'Someone pastes a password in chat', 'Work gets faster for everyone', 'Nothing important changes',
         'Mixing channels leads to secrets landing in the wrong place.', SEC, None),
        ('In the restaurant story, why does the waiter not read the kitchen ticket aloud?', 'Diners and cooks need different words', 'Kitchen tickets are secret recipes', 'Waiters cannot read well',
         'Each audience gets the information in its own form.', JARG, None),
        ('In the trace, the lead gets…', 'A judgment call, short', 'A full novel of every step', 'The user’s password',
         'The lead needs a decision request, not every detail.', JARG, SEC),
        ('Which refusal sentence is complete?', '“I cannot reset that; here is the path”', '“No, that is not our job.”', '“Maybe later, if you call back tomorrow”',
         'It refuses and offers the approved route.', ARGUE, URG),
    ],
        '<p>You talk to different people in different ways. The user needs the outcome, the time and what you need from them; not DHCP or APIPA. The ticket '
        'needs facts. The lead on the phone needs a short judgment call, not a long story. If these channels get mixed, someone ends up pasting a password into '
        'chat “so the next guy can log in.” Refuse unsafe requests calmly and write the refusal as a fact.</p>',
        '<p>In a restaurant, the waiter tells the diner “your steak will be about ten minutes.” On the kitchen ticket the same order reads “T4 ribeye MR no '
        'butter.” The head chef might be asked “can we swap the side for table four?” Same meal, three audiences, three languages. If the waiter read the kitchen '
        'ticket aloud to the diner, nobody would understand. Your user, ticket and lead each need their own version.</p>',
        ['User: outcome, time, what you need from them.', 'Ticket: facts, codes, tests, times.', 'Lead: one judgment question.', 'Keep secrets out of every channel.'],
        '<p>Write the same update for the user and for the ticket.</p>',
        reveal('Mail send fails from an account lock. User line and ticket line?', 'User: “You can’t send mail yet; the messaging team is unlocking your account, update by 1400.” Ticket: “Send fails 0x800CCC0F; account locked per AD; escalated to messaging 1320.”')),
    'hour-plan-for-1-4': X('Hour plan for 1.4', 'IT-1.4', L14, [
        ('What is the first drill in 1.4?', 'Say the user line, write the ticket line', 'Open a PC case and reseat the RAM sticks', 'Read the policy manual first',
         'The two-audience drill comes first to separate the channels.', PLANB, None),
        ('In the 20–40 block, the partner plays…', 'The loud caller', 'The lead technician', 'The help-desk manager',
         'Practising refusal against a loud caller builds calm under pressure.', ARGUE, PLANB),
        ('In the rehearsal story, why practise with a heckler?', 'Real calls get loud too', 'Hecklers are fun to have', 'It makes the play longer',
         'Rehearsing pressure makes the real thing easier.', PLANB, None),
        ('In the trace, the privacy block sorts…', 'PII, hostnames and secrets', 'Fonts and colours on screen', 'Printer models by brand',
         'Knowing which data is private versus routine is the privacy skill.', PRIV, None),
        ('The plan ends with…', 'A factual refusal note', 'A long lecture on privacy law', 'A group lunch break',
         'The last block writes a refusal note that is factual, not a fight.', ARGUE, None),
    ],
        '<p>The 1.4 lesson has four blocks. First: the two-audience drill, where you say the user sentence and then write the ticket sentence. Second: refuse an '
        'unsafe reset while a partner plays a loud caller. Third: privacy, deciding what is personal information, what is just a hostname and what is a secret. '
        'Fourth: write one refusal note that is factual, not a fight.</p>',
        '<p>Actors rehearse a scene many times, and a good director sometimes adds a heckler in the audience so the cast learns to stay in character under '
        'pressure. By opening night, a cough or a shout does not throw them. The 1.4 hour plan rehearses the moments that throw new technicians: switching '
        'language between user and ticket, a caller who gets loud, and spotting private data.</p>',
        ['0–20: say user line, write ticket line.', '20–40: refuse a reset to a loud caller.', '40–60: sort PII, hostname, secret.', '60–75: write a factual refusal note.'],
        '<p>Order the 1.4 blocks.</p>',
        order('Hour plan 1.4', ['Two-audience drill', 'Refuse a loud caller', 'Privacy sort', 'Factual refusal note'],
              'Language, pressure, privacy, then the written record.')),
    'user-channel-versus-ticket-channel': X('User channel versus ticket channel', 'IT-1.4', L14, [
        ('Which line belongs in the user channel?', '“You can send mail; I’ll check at 1400”', '“Error 0x800CCC0F, ping 4/4 to mail01”', '“DHCP scope 10.20.30.0/24 renewed”',
         'Users get outcome and timing in plain words.', JARG, JARG),
        ('What happens if feelings go in the ticket?', 'The next watch cannot work from it', 'The ticket becomes more helpful', 'The user feels much better',
         'Tickets must be factual so the next person can act.', VAGUE, None),
        ('In the TV-news story, why does the anchor not read raw data?', 'Viewers need the meaning', 'Data is always wrong', 'Anchors cannot read numbers',
         'Each channel gets the form its audience can use.', JARG, None),
        ('In the trace, what goes to the lead?', 'A one-line judgment question', 'A full copy of the user chat', 'The full packet capture',
         'Leads need a concise decision request.', JARG, None),
        ('If you dump DHCP details on the user, they…', 'Stop listening', 'Learn networking quickly', 'Thank you for detail',
         'Jargon loses the user’s attention.', JARG, None),
    ],
        '<p>Each channel has its own style. User: “You can send mail again. Please stay on this PC until we confirm the report goes. I will check back at 1400.” '
        'Ticket: versions, error codes, pings, times. Lead phone: “I think this is an account lock, not a network card. Can messaging take it?” Put DHCP in the '
        'user channel and they stop listening. Put feelings in the ticket and the next shift cannot work.</p>',
        '<p>A TV news anchor reports an election as “the results are close; we expect a final count by midnight.” Behind the scenes, analysts look at spreadsheets '
        'of precinct numbers, and producers argue in short sentences about which story leads. The same facts, three channels. Nobody would put the spreadsheet on '
        'screen raw. Your user hears the anchor version, the ticket gets the spreadsheet, the lead gets the producer’s question.</p>',
        ['User: outcome and next time.', 'Ticket: versions, codes, pings, times.', 'Lead: one judgment question.', 'Check: nothing mixed between them.'],
        '<p>Sort each line into its channel.</p>',
        sort('Which channel?', {'User': ['I’ll check back at 1400'], 'Ticket': ['Error 809; gateway ping 0/4', 'Outlook 16.0.1'],
                                'Lead': ['Account lock, can messaging take it?']},
             'Plain outcome to users, facts to tickets, decisions to leads.')),
    'refuse-without-becoming-the-enemy': X('Refuse without becoming the enemy', 'IT-1.4', L14, [
        ('Which refusal follows the script?', '“I can’t reset that; here’s the approved path”', '“Stop wasting my time, I won’t do it”', '“Fine, just this once, don’t tell anyone”',
         'The script refuses calmly and points to the approved route.', ARGUE, URG),
        ('What do you write after refusing?', '“Declined reset; identity not completed”', '“Caller was rude and a liar, refused”', 'Nothing; refusals are not recorded',
         'The refusal is documented as a fact, not a fight.', ARGUE, VAGUE),
        ('In the referee story, why does the ref explain calmly?', 'The decision stands, without a fight', 'Referees like long talks with players', 'Players vote on calls',
         'Calm explanation keeps authority without conflict.', ARGUE, None),
        ('In the trace, where is the caller directed?', 'The window with a badge', 'A colleague’s personal phone', 'A public chat channel',
         'The approved path is the window, portal or supervisor.', URG, None),
        ('Is refusing an unsafe reset a failure of service?', 'No; it is the job', 'Yes; users must always get help', 'Yes; it hurts metrics',
         'Protecting accounts is part of good service.', ARGUE, URG),
    ],
        '<p>When you must refuse, use a script: “I cannot reset that from this call. Here is the approved path: the window, the portal or your supervisor. If you '
        'are the user, come to the window with your badge.” Then write: “Declined reset. Caller could not complete identity script. Directed to window.” That is '
        'not a war. That is the job.</p>',
        '<p>A good referee who gives a free kick does not argue with the angry player. They point to the spot, say what the foul was, and let play continue. The '
        'decision stands, but nobody turns it into a personal fight. Your refusal script is the referee’s point to the spot: the rule is clear, the next step is '
        'clear, and your tone stays neutral. Afterwards you write it down like a match report.</p>',
        ['Hear the request.', 'Identity script not completed.', 'Say the refusal sentence calmly.', 'Give the approved path.', 'Write the factual refusal note.'],
        '<p>Order the refusal steps.</p>',
        order('Refusal', ['Hear the request', 'Check identity', 'Say the refusal', 'Give the approved path', 'Write the note'],
              'Calm words and a clear path, then the factual note.')),
    'privacy-on-a-real-bench': X('Privacy on a real bench', 'IT-1.4', L14, [
        ('Which way should bench screens face?', 'Away from the passageway', 'Toward the door for visibility', 'Toward the waiting area',
         'Screens facing away keep private data from passers-by.', PRIV, None),
        ('You step away for coffee. The PC…', 'Gets locked first', 'Stays open for speed', 'Gets a note with the password',
         'Unlocked machines are an open door.', PRIV, SEC),
        ('In the hotel-housekeeper story, why not read guests’ letters?', 'Access is for the job only', 'Letters are boring to read', 'Managers might notice',
         'Access to a space does not mean permission to read private things.', PRIV, None),
        ('In the trace, a sticky-note password “for the next guy” leads to…', 'Accounts walking away', 'Faster handoffs for all', 'A tidy desk',
         'Written passwords are how accounts get stolen.', SEC, None),
        ('Reading personnel records aloud “for colour” is…', 'A privacy breach', 'Harmless banter', 'Good for team spirit',
         'Private records are never shared for entertainment.', PRIV, None),
    ],
        '<p>On the repair bench, keep screens facing away from the corridor. Use a privacy screen if the shop gives you one. Never read medical or personnel records '
        'out loud for fun. Lock the machine before you get coffee. Never leave a password on a sticky note “for the next guy.” The next guy is how accounts get stolen.</p>',
        '<p>A hotel housekeeper goes into every room, every day. They see suitcases, letters, laptops and medicine on the bedside table. A good housekeeper cleans '
        'and leaves everything unread and untouched, and always locks the door behind them. Having the key is part of the job; snooping is not. You are the '
        'housekeeper for users’ computers. Access comes with the work; privacy is the condition of keeping it.</p>',
        ['Turn screens away from the corridor.', 'Fit a privacy screen if issued.', 'Lock before you step away.', 'No passwords on sticky notes.',
         'Keep records unread unless needed.'],
        '<p>Sort bench habits into safe or breach.</p>',
        sort('Bench privacy', {'Safe': ['Lock before coffee', 'Screen faces away'], 'Breach': ['Password sticky note', 'Reading HR file aloud']},
             'Safe habits limit exposure; breaches create it.')),
    'communication-and-professionalism': X('Communication and professionalism', 'IT-1.4', L14, [
        ('A customer is upset. Which behaviour fits A+ 4.7?', 'Listen, restate, avoid arguing', 'Defend yourself and correct them', 'Minimise it as a small problem',
         'Active listening and restating calm the situation; arguing and minimising escalate it.', ARGUE, ARGUE),
        ('You will be late. What do you do?', 'Contact them before the time', 'Arrive late and apologise then', 'Skip the visit entirely',
         'Professionals contact the customer before the agreed time.', ARGUE, None),
        ('In the tailor story, why ask open questions?', 'To understand what is wanted', 'To fill the silence while measuring', 'To sell more cloth',
         'Open questions reveal the real need, just as in troubleshooting.', 'MC-C-IT1-CLOSED-Q', None),
        ('In the trace, the final step is…', 'Follow up on satisfaction', 'Post about it on social media', 'Close and never call back',
         'Following up confirms the outcome and is part of professionalism.', 'MC-IT1-CLOSE-EARLY', PRIV),
        ('Which is a distraction to avoid?', 'Personal texting on a call', 'Taking notes while listening', 'Restating the issue',
         'Personal calls and texting signal disrespect.', ARGUE, None),
    ],
        '<p>A+ Core 2 objective 4.7 covers professional behaviour. Dress to suit the site. Use plain language, not jargon. Stay positive and confident. Listen '
        'actively, take notes and do not interrupt. Respect cultural differences. Be on time, or call before you are late. Avoid personal calls and texting. With '
        'a difficult customer, do not argue or minimise; ask open questions and restate the issue. Set expectations, keep people updated, document, and follow up. '
        'Never look at or share confidential material.</p>',
        '<p>A good tailor fitting a suit does not start cutting while the customer is still talking. They listen, ask “what will you wear it for?”, repeat back '
        '“so, a summer wedding, slim fit,” agree a date for the fitting and ring the day before if it will be late. When the suit is ready, they check it fits. '
        'IT professionalism is the tailor’s routine: listen, clarify, promise realistically, deliver, follow up.</p>',
        ['Arrive on time, dressed for the site.', 'Listen; take notes; do not interrupt.', 'Ask open questions; restate the issue.', 'Set expectations and update.',
         'Document and follow up.'],
        '<p>Order a professional contact from start to finish.</p>',
        order('Professional contact', ['Arrive on time', 'Listen and take notes', 'Restate the issue', 'Set expectations', 'Follow up'],
              'Listening and clarifying come before promising and delivering.')),
})

L15S = L15
LESSONS.setdefault('1.5', {}).update({
    'worked-example-this-labs-sentence': X('Worked example — this lab’s sentence', 'IT-1.3', L15S, [
        ('Half the quarterdeck badges failed and the reader is warm. Classify?', 'Incident', 'Break/fix on one reader', 'Request for new badges',
         'Many users plus heat on access control is an incident.', REQ, SCOPE2),
        ('What impact do you enter?', 'Many', 'One, since it is one reader', 'None until someone complains',
         'Half the badges failing affects many people.', SCOPE2, SCOPE2),
        ('In the gas-leak story, why not fix the pipe yourself?', 'Heat and safety need specialists', 'Pipes are cheap and easy to replace', 'Plumbers are always slow',
         'Heat on access control is a safety issue, not a solo repair.', HANDS, None),
        ('In the trace, the note must say…', 'Reader warm; panel not opened', 'Opened reader to check fuse', 'Probably a bad card batch',
         'The note names heat and confirms you did not open the panel.', HANDS, VNOTE),
        ('Who do you escalate to?', 'Facilities and access control', 'Nobody; reboot it yourself', 'The user’s line manager only',
         'Heat plus access control needs facilities and duty staff.', HANDS, None),
    ],
        '<p>Here is the lab worked through. The user says: “Half the quarterdeck badges stopped after lunch. The reader is warm.” Classify: incident. Impact: many. '
        'Escalate: yes, to facilities and access control, because of possible heat. Note: “About half of badge readers failed after 1200. Reader surface warm. Did '
        'not open the panel. Need facilities and duty section on scene. Users on a manual log.” Do not open the reader.</p>',
        '<p>If you smell gas in a block of flats, you do not get a spanner and start tightening pipes. You open windows, get people out, and call the gas board, '
        'telling them exactly what you smelled and where. A warm badge reader that has stopped working for half the building is that smell of gas. Your job is '
        'to recognise it, protect people, call the specialists and leave a clear note, not to become the repair.</p>',
        ['show ticket — read the card.', 'classify incident.', 'impact many.', 'escalate yes — facilities / access control.',
         'note — warm reader, panel not opened, manual log.', 'submit.'],
        '<p>Run the lab and enter each command in order.</p>',
        order('Lab commands', ['show ticket', 'classify incident', 'impact many', 'escalate yes', 'note', 'submit'], 'Read, decide, record, submit.')),
    'pass-bar': X('Pass bar', 'IT-1.3', L15S, [
        ('Which is part of passing Block 1?', 'Note names heat and a next person', 'Finishing fastest in the class', 'Opening the panel to check',
         'The note must name heat and a next person, without opening the panel.', HANDS, VAGUE),
        ('Can you pass if the answers were fed to you?', 'No', 'Yes, if you submit', 'Yes, with a long note',
         'You must finish the lab without being fed answers.', PLANB, None),
        ('In the driving-test story, why does the examiner stay quiet?', 'You must decide alone', 'Examiners are shy', 'Talking is not allowed in cars',
         'A pass means you did it yourself.', PLANB, None),
        ('After passing, what comes next per the trace?', 'Chapter 2 hardware names', 'Repeat Block 1 again from the start', 'Skip to Chapter 10',
         'Chapter 2 applies the same discipline to hardware.', NEWB, None),
        ('Which note fails the bar?', '“Opened reader, fixed fuse”', '“Reader warm; facilities called”', '“Panel not opened; duty notified”',
         'Opening the panel fails the bar.', HANDS, None),
    ],
        '<p>You pass Block 1 when you finish the lab on your own, without being given the answers. Your note must mention the heat and name a next person, and you '
        'must not open the panel. Then Chapter 2 puts hardware names on the same careful habits.</p>',
        '<p>On a driving test, the examiner gives directions but never tells you when to check your mirrors or how to handle a roundabout. They watch to see '
        'whether you do it yourself. If they had to grab the wheel, you fail, however smoothly the rest went. The Block 1 pass bar is your driving test: the lab '
        'is the route, and you must make every safe decision without being steered.</p>',
        ['Run the lab without hints.', 'Note names heat.', 'Note names a next person.', 'Panel stays closed.', 'Move on to Chapter 2.'],
        '<p>Check your own note against the pass bar.</p>',
        reveal('Does “Reader warm, many badges down” pass?', 'Not yet: add a next person (facilities / duty section) and that the panel was not opened.')),
    'how-the-live-lab-is-scored': X('How the live lab is scored', 'IT-1.3', L15S, [
        ('Which classify value fails the lab?', 'break-fix', 'incident', 'incident (typed after show ticket)',
         'The card describes many users and heat, so break-fix is the wrong label.', REQ, None),
        ('Which impact value passes?', 'many', '1, because it is one reader', '0, because no one is hurt',
         'Half the badges down is many people.', SCOPE2, SCOPE2),
        ('In the exam-marking story, why does a wrong step lose marks?', 'The method is marked', 'Examiners are strict', 'Ink colour matters',
         'The lab scores each decision, not only the final submit.', PLANB, None),
        ('In the trace, which note fails?', 'One that opens the reader', 'One that names heat', 'One that names facilities',
         'Opening the reader in the note fails.', HANDS, None),
        ('Which command comes first?', 'show ticket', 'submit', 'classify incident',
         'You read the card before typing decisions.', 'MC-IT1-TEST-BEFORE-INTAKE', None),
    ],
        '<p>The live lab card is: half the badges stopped after lunch and a reader is warm. The lab accepts these commands in order: show ticket, classify incident, '
        'impact many, escalate yes, a note that names heat and does not open the panel, then submit. Classify break-fix or impact 1 fails. A note that opens the '
        'reader fails. That is the same judgment you will use on a real quarterdeck.</p>',
        '<p>In a maths exam, the right final number with no working earns little, and wrong working loses marks even if you stumble on the answer. Examiners '
        'mark the method. The intake lab is marked the same way: each command is a step in your working. Read the card, classify, judge impact, escalate, write '
        'the note. A wrong label or a note that opens the reader is a wrong line of working.</p>',
        ['show ticket', 'classify incident', 'impact many', 'escalate yes', 'note: heat, panel closed', 'submit'],
        '<p>Sort each entry into pass or fail.</p>',
        sort('Pass or fail?', {'Pass': ['classify incident', 'impact many', 'escalate yes'], 'Fail': ['classify break-fix', 'impact 1', 'note: opened reader']},
             'The card needs incident, many, escalate, and a closed panel.')),
    'hour-plan-for-1-5': X('Hour plan for 1.5', 'IT-1.3', L15S, [
        ('What happens before anyone types?', 'Name heat and many users', 'Submit a guess quickly', 'Open the reader together',
         'The class names the key facts before typing commands.', 'MC-IT1-TEST-BEFORE-INTAKE', HANDS),
        ('What does the instructor watch in 15–45?', 'Classify and impact', 'Typing speed only', 'Font choice in notes',
         'Classify and impact are the key judgment points.', PLANB, None),
        ('In the flight-sim story, why repeat a failed landing?', 'To fix the reason and redo clean', 'Simulator time is free to use', 'To log more landings',
         'Failed submits are explained, then rerun clean.', PLANB, None),
        ('In the trace, where do chapter-check misses go?', 'Back to the matching section', 'To a new tool or a new lab', 'Nowhere; move on',
         'Misses send you back to the section that teaches it.', PLANB, None),
        ('How many items is the Chapter 1 check?', '10', '100', '1',
         'The plan ends with a 10-item chapter check.', PLANB, None),
    ],
        '<p>The 1.5 lesson: first 15 minutes, read the live card together and name the heat and the many users before anyone types. Next 30 minutes: everyone runs '
        'ticket-intake through to submit while the instructor watches classify and impact. Next 25 minutes: explain failed submits and run them again cleanly. '
        'Last 20 minutes: the Chapter 1 check of ten items; misses go back to the matching section.</p>',
        '<p>Trainee pilots practise landings in a simulator. When one goes wrong, the instructor freezes it, asks what happened, and the trainee flies it again '
        'until it is clean. Nobody moves on to a new aircraft because one landing failed; they fix the reason. The 1.5 hour plan does the same: read the card, fly '
        'the lab, explain the failure, fly it clean, then a short check that sends you back to the right lesson if needed.</p>',
        ['0–15: read the card; name heat and many.', '15–45: everyone runs ticket-intake.', '45–70: explain failed submits; rerun clean.',
         '70–90: 10-item Chapter 1 check; misses go back to sections.'],
        '<p>Order the 1.5 blocks.</p>',
        order('Hour plan 1.5', ['Read the card', 'Run ticket-intake', 'Explain and rerun failures', 'Chapter 1 check'], 'Read, do, fix, check.')),
    'the-card-line-by-line': X('The card, line by line', 'IT-1.3', L15S, [
        ('Why is this card not break-fix?', 'Many users plus heat on access control', 'Because it happened after lunch', 'Because the reader is old hardware',
         'One broken cable is break-fix; many users plus heat is an incident.', REQ, SCOPE2),
        ('Which note fails?', 'Password in the note', 'Warm reader, panel closed', 'Facilities named as next',
         'Secrets in notes fail, as do empty notes or opening the reader.', SEC, None),
        ('In the crime-scene story, why not touch the evidence?', 'Specialists need it as found', 'It is dirty and unsafe to handle', 'It might be lost',
         'You leave the warm reader for facilities, like a scene for investigators.', HANDS, None),
        ('In the trace, escalate yes goes to…', 'Facilities / access control / safety', 'You, with a screwdriver', 'The user’s line manager, by email',
         'Escalate to the teams that own heat and access control.', HANDS, None),
        ('Which command reads before you type?', 'show ticket', 'submit', 'escalate yes',
         'show ticket reads the card first.', 'MC-IT1-TEST-BEFORE-INTAKE', None),
    ],
        '<p>The lab says: after lunch, half the quarterdeck badges failed and the reader face is warm. That is not one broken cable; it is many users plus heat on '
        'an access-control device. Commands in order: show ticket (read first), classify incident, impact many, escalate yes to facilities, access control and safety, '
        'a note saying the reader is warm, the panel was not opened and naming the next person, then submit. Fails: break-fix, impact 1, escalate no, opening the '
        'reader, an empty note or a password in the note.</p>',
        '<p>A police officer first at a crime scene does not start picking up objects to look for clues. They tape off the area, note what they see, keep people '
        'back and call the detectives. Touching things ruins the evidence and can be dangerous. The warm reader is your scene. You read it, record it, keep '
        'people clear and hand it to facilities and access control as you found it.</p>',
        ['show ticket — read first.', 'classify incident — not break-fix.', 'impact many — not 1.', 'escalate yes — facilities, access control, safety.',
         'note — warm, panel closed, next person.', 'submit.'],
        '<p>Run the card in the lab, line by line.</p>',
        sort('Line by line: right or fail?', {'Right': ['show ticket first', 'impact many', 'note names next person'],
                                              'Fail': ['escalate no', 'password in note']},
             'Right lines read, judge and record; fail lines skip escalation or leak secrets.')),
    'after-the-lab': X('After the lab', 'IT-1.3', L15S, [
        ('Submit passed but identity was weak on the check. Are you done?', 'No; re-read 1.1 identity', 'Yes, the lab passed', 'Yes, identity is optional',
         'One lab card is not the whole job; fix the weak area first.', URG, PLANB),
        ('What extra task closes the gap?', 'Write one more refusal note', 'Retake the lab ten more times', 'Skip to Chapter 3',
         'A refusal note practises identity and documentation together.', URG, PLANB),
        ('In the football story, why train a weak foot?', 'Matches use both feet', 'Coaches like running drills', 'It is easier',
         'Real work uses every skill, not only the one the lab tested.', PLANB, None),
        ('In the trace, after re-reading identity you…', 'Write a refusal note', 'Delete the ticket and start over', 'Open a PSU',
         'The written refusal proves the identity habit.', URG, None),
        ('“The lab is one card; the job is…”', 'every card', 'just this card', 'only the hard cards',
         'Real work brings every kind of card, so every skill matters.', PLANB, None),
    ],
        '<p>Passing submit is not the end if your chapter check shows you are weak on identity. The lab is one card; the job is every card. Re-read the identity '
        'part of 1.1 and write one more refusal note before you go to Chapter 2.</p>',
        '<p>A footballer who scores with their right foot in training still practises with the left. In a real match the ball does not always come to the '
        'strong side. The lab tested one situation and you passed it. The chapter check showed where your other foot is weak. Before Chapter 2, you train that '
        'foot: re-read identity, write a refusal note, and only then move on.</p>',
        ['Look at your chapter check.', 'Weak on identity? Re-read 1.1 identity.', 'Write one refusal note.', 'Then start Chapter 2.'],
        '<p>Write one refusal note now.</p>',
        reveal('Write a refusal note for a caller who failed callback.', '“Declined password reset 1015. Caller could not be reached on listed callback number. Directed to window with badge.”')),
})


STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '1.1': {'start-here-if-you-have-never-done-this': '76dabd98c636', 'what-a-computer-is-in-one-picture': '6cf351a62dc2', 'what-software-is': '7eccaef03c95', 'what-a-user-actually-brings-you': '80f7ff00d4a9', 'what-a-ticket-is': '1cf538229cd9', 'words-you-will-hear-this-week': '03f86bf50af7', '1-what-the-role-actually-delivers': 'fe1e118e5935', '2-three-kinds-of-work': '2aabfe03c73e', '3-impact-and-identity': '0981e922024d', '4-keep-it-or-escalate': '8ad8cdf0ad6b', '5-closing-is-not-the-same-as-fixed': '8b39ff26fadf', '6-desk-drill-paper-first': '525f78e4d727', 'what-this-job-actually-is': 'ee56d60a49f5', 'worked-contacts': '8f6db023a4a1', 'identity-before-any-reset': 'f4213a9ce29c', 'hour-plan-for-1-1': '5d97c85fb6b3', 'what-you-are-paid-to-restore': '3b490012a4fe', 'the-four-labels-and-what-changes-when-you-pick-one': '3495081978d8', 'impact-is-a-count-plus-a-consequence': '93b2049e94f4', 'desk-set-classify-these-out-loud': '099a2959a4af', 'identity-before-any-account-change': 'dedd87b29023', 'handoff-that-survives-0200': '18d0c931c78e'},
    '1.2': {'electricity-you-need-as-a-technician-not-as-an-engineer': 'eb6b1f7d9e0a', '1-electrical-reality-on-a-training-bench': 'd25c08019803', '2-esd-without-mythology': '45ec0b4f79c7', '3-body-and-path': '12d5060a39b3', '4-when-safety-becomes-an-incident': 'f4380764365b', 'why-the-wall-unplug-matters': '5aace49092a2', 'lift-path-and-the-bench': '547a56d41f4e', 'hour-plan-for-1-2': '25920248aa4b', 'why-this-chapter-exists-before-hardware': 'b316150d1227', 'the-five-step-open-order-slowly': '6a90aa1a2ab4', 'what-you-never-open': 'b5677c35e830', 'when-safety-is-the-ticket': '8eb68a306e0b', 'lift-and-path': '1a288edc16c0', 'common-safety-procedures': 'b0a97e3e58c1'},
    '1.3': {'why-writing-is-part-of-the-repair': 'f5b8e1b57aab', '1-anatomy-of-a-usable-ticket': '288a3bfea50f', '2-facts-versus-guesses': 'a8be7428dc4e', '3-change-awareness': 'cd644700eebd', '4-note-quality-bar-for-the-lab': 'eefd7b2963ee', 'ticket-b-versus-ticket-a': '59fdcdbf105b', 'hour-plan-for-1-3': 'b5160f974ad9', 'anatomy-of-ticket-b': 'f5200b1193df', 'action-result-until-it-is-boring': '64cc8c93ebb1', 'repair-versus-change-with-shop-examples': 'e2a65d2f5033', 'what-never-goes-in-the-ticket': 'f00858f3a525'},
    '1.4': {'1-talk-to-the-outcome': 'ef16bfce8581', '2-privacy-on-a-real-floor': '65595f5eb2ff', '3-saying-no': 'a99bffe12d2e', '4-what-goes-in-the-ticket': '391fa34220d9', 'two-audiences': '4fa3ca2bdb35', 'hour-plan-for-1-4': '9e1d52296c66', 'user-channel-versus-ticket-channel': '4b1c009e9f42', 'refuse-without-becoming-the-enemy': '175752d06d85', 'privacy-on-a-real-bench': '2759aba0126d', 'communication-and-professionalism': '0b0059e29704'},
    '1.5': {'worked-example-this-labs-sentence': '1c2d04e5a429', 'pass-bar': 'fba2cc44979e', 'how-the-live-lab-is-scored': '96d19d480034', 'hour-plan-for-1-5': 'f891163a1fba', 'the-card-line-by-line': '391aea2e8fc7', 'after-the-lab': '9c5572c242aa'},
}
