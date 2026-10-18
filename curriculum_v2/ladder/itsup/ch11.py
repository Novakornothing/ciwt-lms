"""Explanation ladder — ITSUP chapter 11 (Software Troubleshooting). Pending SME review.

Author B (labs branch, pass 19). Every concept section of lessons 11.1-11.4 is laddered, restated with same_as, or
skipped with a reason. CLIENT chapter 4 holds the same lessons and reuses this ladder (curriculum_v2/ladder/client/ch04.py).
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 11

L111 = 'Course lesson 11.1 “Symptom Patterns” (the original section), re-explained'
L112 = 'Course lesson 11.2 “Isolation Techniques” (the original section), re-explained'
L113 = 'Course lesson 11.3 “Repair vs Rebuild” (the original section), re-explained'
L114 = 'Course lesson 11.4 “Capstone — Slow Logon” (the original section), re-explained'
MS_EV = ('Microsoft Learn — Event Viewer and Reliability Monitor; “Advanced troubleshooting for Event ID 41: The system has '
         'rebooted without cleanly shutting down first” (Kernel-Power)')
MS_BOOT = 'Microsoft Learn — “Use Bootrec.exe in the Windows RE to troubleshoot startup issues”; Windows Recovery Environment (Startup Repair)'
MS_CLEAN = ('Microsoft Support — “How to perform a clean boot in Windows”; “Start your PC in safe mode in Windows”; '
            '“Repair apps and programs in Windows”')
MS_TOOLS = ('Microsoft Support — Task Manager in Windows; Microsoft Learn — Windows Tools and Microsoft Management Console '
            'snap-ins; Resource Monitor')
MS_GP = 'Microsoft Learn — Group Policy Operational log and gpresult; User Profile Service events'

MISCONCEPTIONS = {
    'MC-L-IT11-KP41-AS-CRASH': {
        'obj': 'IT-11.3', 'label': 'Reading Event ID 41 (Kernel-Power) with no bug-check code as a software crash',
        'fix': 'Event 41 means Windows restarted without a clean shutdown; with no BugCheck it usually points at power or heat.',
        'terms': ['event 41', 'kernel-power', 'shutdown'], 'source': L111 + '; ' + MS_EV, 'review': 'Pending SME review'},
    'MC-L-IT11-BOOTREC-FIRST': {
        'obj': 'IT-11.3', 'label': 'Rebuilding boot files before checking the drive is detected, the boot order and the boot mode',
        'fix': 'Most “no OS found” tickets are a USB stick left in, the boot order or UEFI/legacy mode; check those before bootrec.',
        'terms': ['no operating system', 'bootrec', 'boot order', 'uefi'], 'source': L111 + '; ' + MS_BOOT, 'review': 'Pending SME review'},
    'MC-L-IT11-RESET-KEEPS-DATA': {
        'obj': 'IT-11.4', 'label': 'Thinking Reset keeps a Store app’s data, like Repair does',
        'fix': 'Repair fixes the app’s files and keeps its data; Reset also clears the app’s data and settings on this device.',
        'terms': ['repair', 'reset', 'store app'], 'source': L112 + '; ' + MS_CLEAN, 'review': 'Pending SME review'},
    'MC-L-IT11-ONE-AT-A-TIME': {
        'obj': 'IT-11.4', 'label': 'Re-enabling clean-boot items one at a time instead of halving',
        'fix': 'Turn half back on and test, then half of the guilty half; sixteen items take at most four restarts.',
        'terms': ['clean boot', 'halving', 'msconfig'], 'source': L112, 'review': 'Pending SME review'},
    'MC-L-IT11-SAFEBOOT-LEFT': {
        'obj': 'IT-11.4', 'label': 'Leaving msconfig’s Safe boot ticked after testing',
        'fix': 'Safe boot set in msconfig persists; untick it afterwards or the PC keeps starting in Safe Mode.',
        'terms': ['msconfig', 'safe boot'], 'source': L112 + '; ' + MS_CLEAN, 'review': 'Pending SME review'},
    'MC-L-IT11-LOGON-GUESS': {
        'obj': 'IT-11.3', 'label': 'Guessing the cause of a slow logon instead of timing each stage',
        'fix': 'Time computer policy, user policy, profile load and startup apps; the slowest stage names the owner of the fix.',
        'terms': ['slow logon', 'group policy', 'profile'], 'source': L114 + '; ' + MS_GP, 'review': 'Pending SME review'},
}

SCOPE, PATTERN, FOLLOWS, EVID = 'MC-IT11-SCOPE-INFLATED', 'MC-R5-IT11-PATTERN-AS-SINGLE', 'MC-R5-IT11-FOLLOWS', 'MC-R5-IT11-EVENT-ID'
PARA, CLAIM, DNSAPP = 'MC-IT11-PARAPHRASE-ERROR', 'MC-R3-IT11-ACT-ON-CLAIM', 'MC-IT11-DNS-AS-APP'
RBFIRST, RBNOGATE, RBGATE, RBORDER = 'MC-IT11-REBUILD-FIRST', 'MC-IT11-REBUILD-NO-GATE', 'MC-C-IT11-REBUILD-GATE', 'MC-R5-IT11-REBUILD-ORDER'
ENDLESS, REBOOT, SAFEREAD = 'MC-R5-IT11-ENDLESS-REPAIR', 'MC-IT11-REBOOT-HARMLESS', 'MC-R5-IT11-SAFEMODE-READ'
BOTTLE, LOCKED, EDITION = 'MC-R3-IT11-BOTTLENECK-READ', 'MC-R3-IT11-FORCE-LOCKED', 'MC-R6-IT11-EDITION-TOOLS'
TEMPP, TEMPDEL = 'MC-R3-IT11-TEMP-PROFILE', 'MC-R5-IT11-TEMP-PROFILE-DELETE'
KP41, BOOTREC, RESETK = 'MC-L-IT11-KP41-AS-CRASH', 'MC-L-IT11-BOOTREC-FIRST', 'MC-L-IT11-RESET-KEEPS-DATA'
ONEAT, SAFELEFT, GUESS = 'MC-L-IT11-ONE-AT-A-TIME', 'MC-L-IT11-SAFEBOOT-LEFT', 'MC-L-IT11-LOGON-GUESS'

SVG = 'viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px" role="img" aria-label="{label}" class="ladder-svg"'


def svg(w, h, label, body):
    return f'<svg {SVG.format(w=w, h=h, label=label)}><title>{label}</title>{body}</svg>'


def box(x, y, w, h, text, sub=''):
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>'
    t += (f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 7)}" text-anchor="middle" dominant-baseline="middle" '
          f'fill="currentColor" font-size="13" font-weight="700">{text}</text>')
    if sub:
        t += (f'<text x="{x + w / 2}" y="{y + h / 2 + 10}" text-anchor="middle" dominant-baseline="middle" '
              f'fill="currentColor" font-size="11">{sub}</text>')
    return t


def arrow(x1, y1, x2, y2):
    """Horizontal (y1 == y2) or vertical-down arrow."""
    rot = 0 if y1 == y2 else 90
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="2"/>'
            f'<polygon points="{x2},{y2} {x2 - 7},{y2 - 5} {x2 - 7},{y2 + 5}" fill="currentColor" transform="rotate({rot} {x2} {y2})"/>')


def label(x, y, text, size=11, anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="currentColor" font-size="{size}">{text}</text>'


# ---------------------------------------------------------------- diagrams
_SCOPE = svg(640, 150, 'Scoping a software fault with three comparisons: another user on the same PC, the same user on another PC, many PCs on the same version; the answers place the fault in a profile, an account, the device or the application',
             box(10, 40, 100, 50, 'App fails') + arrow(110, 65, 135, 65) + box(135, 40, 150, 50, 'Other user,', 'same PC?')
             + arrow(285, 65, 310, 65) + box(310, 40, 150, 50, 'Same user,', 'other PC?') + arrow(460, 65, 485, 65)
             + box(485, 40, 145, 50, 'Many PCs,', 'same version?')
             + label(210, 118, 'works → profile', 11) + label(385, 118, 'fails → account, data', 11) + label(557, 118, 'yes → pattern', 11)
             + label(320, 142, 'write the scope down before any repair', 11))

_NOOS = svg(640, 130, '“No operating system found” checks in order: is the drive detected in firmware; boot order and Windows Boot Manager first; UEFI or legacy mode matches the disk; WinRE Startup Repair; only then bootrec',
            ''.join(box(10 + i * 126, 30, 116, 56, a, b) + (arrow(126 + i * 126, 58, 136 + i * 126, 58) if i < 4 else '')
                    for i, (a, b) in enumerate([('Drive seen', 'in UEFI?'), ('Boot order', 'USB left in?'), ('UEFI / CSM', 'mode match?'),
                                                ('WinRE', 'Startup Repair'), ('bootrec', 'then restore')]))
            + label(320, 116, 'cheap firmware checks first; boot-file repair last', 11))

_HALVE = svg(640, 150, 'Halving sixteen clean-boot items: all off and the fault is gone; turn eight on; if the fault returns the culprit is among those eight, turn four on next; repeat until one item remains, at most four restarts',
             ''.join(box(10 + i * 126, 30, 116, 56, a, b) + (arrow(126 + i * 126, 58, 136 + i * 126, 58) if i < 4 else '')
                     for i, (a, b) in enumerate([('16 off', 'fault gone'), ('8 on', 'fault back?'), ('4 on', 'of the 8'), ('2, then 1', ''),
                                                 ('Culprit off', 'record it')]))
             + label(320, 118, '16 → 8 → 4 → 2 → 1: four restarts, not sixteen', 12))

_DECIDE = svg(640, 170, 'Repair, reinstall or rebuild: a named component gets a targeted repair; damaged system files with healthy apps and data get an in-place reinstall; several unrelated faults, unknown changes or a confirmed compromise get a rebuild after a verified backup',
              box(10, 60, 150, 50, 'Evidence after', 'the time box') + arrow(160, 85, 200, 30) + arrow(160, 85, 200, 85) + arrow(160, 85, 200, 140)
              + box(200, 8, 430, 44, 'One named component → targeted repair')
              + box(200, 63, 430, 44, 'System files damaged, apps fine → in-place reinstall')
              + box(200, 118, 430, 44, 'Many faults, unknown changes → rebuild (backup first)'))

_TOOLS = svg(640, 170, 'Pick the Windows tool by the question: is it running, Task Manager; what happened, Event Viewer; is the hardware seen, Device Manager; which disks and volumes, Disk Management; what runs on a schedule, Task Scheduler',
             ''.join(box(10, 8 + i * 32, 300, 28, a) + arrow(310, 22 + i * 32, 330, 22 + i * 32) + box(330, 8 + i * 32, 300, 28, b)
                     for i, (a, b) in enumerate([('Is it running? What is it using?', 'Task Manager / resmon'),
                                                 ('What happened, and when?', 'Event Viewer'), ('Is the hardware seen?', 'Device Manager'),
                                                 ('Which disks and volumes?', 'Disk Management'), ('What runs on a schedule?', 'Task Scheduler')])))

_LOGON = svg(640, 140, 'Slow-logon stages in order: computer policy and network; user policy with scripts and drive maps; profile load; startup apps; desktop usable; each has its own evidence',
             ''.join(box(10 + i * 126, 30, 116, 56, a, b) + (arrow(126 + i * 126, 58, 136 + i * 126, 58) if i < 4 else '')
                     for i, (a, b) in enumerate([('Computer', 'policy · network'), ('User policy', 'scripts · maps'), ('Profile load', 'size · redirect'),
                                                 ('Startup apps', 'impact column'), ('Desktop', 'usable')]))
             + label(320, 112, 'GroupPolicy Operational log · User Profile Service events · Task Manager', 11)
             + label(320, 132, 'time each stage; the slowest names the owner of the fix', 11))

LESSONS = {
    '11.1': {
        'start-here-software-problems-have-a-scope': section(
            'Start here — software problems have a scope', 'IT-11.1',
            [check('A user says “my computer is broken” because Excel will not open. What is the first question?',
                   'Does it fail only in Excel, or in other apps too?',
                   ['Shall I book a reimage for this afternoon?', 'When did you last buy a new computer for the desk?'],
                   'One app failing on one profile is not a dead computer. Narrowing app, profile, PC or fleet first decides '
                   'whether the fix is a repair, a network check or a rebuild.', mc=[SCOPE, RBFIRST])],
            plain('''<p>“My computer is broken” rarely means the whole computer.</p>
<p>Ask four short questions:</p>
<ol><li>Is it only this app?</li><li>Is it only this Windows sign-in?</li><li>Is it only this PC?</li><li>Is it every PC?</li></ol>
<p>The answer tells you what kind of fix fits. One app means a repair. Every PC means look at the network or the
server. Only a broken PC with a backup is a rebuild.</p>
<p>Wiping a PC without a backup is how shops lose people’s files.</p>''',
                  L111,
                  [check('Why ask the scope questions before choosing a fix?',
                         'The scope decides which fix is in proportion',
                         ['The user expects a long list of questions first', 'Windows logs the answers for the asset record'],
                         'A one-app fault deserves a repair; a fleet-wide one is a pattern for the network or app owner; a rebuild '
                         'needs a backup. Asking first stops an oversized fix.', mc=[SCOPE, None])]),
            analogy('''<p>Think of a plumber called because “the house has no water”.</p>
<p>A good plumber asks: is it one tap, one bathroom, the whole house, or the whole street? One tap is a washer. One
bathroom is a valve. The whole street is the water company, and digging up this house’s pipes would waste a day.
Nobody replaces the boiler (rebuilds the PC) before turning on a different tap — and nobody rips out the bathroom
before moving the owner’s things out of it (the backup).</p>''',
                    L111 + ' (plumber analogy written for this rung)',
                    [check('In the plumber story, “the whole street has no water” matches which software scope?',
                           'Every PC fails, so look at the network or server',
                           ['One app fails, so repair that one app and its settings', 'One profile fails, so rebuild the PC from the image'],
                           'When every PC fails the same way, the cause sits upstream: a server, a licence or the network path. '
                           'Repairing single PCs would be digging up one house’s pipes.', mc=[PATTERN, SCOPE])]),
            visual('''<ol class="ladder-trace">
<li>“Outlook won’t open.” Other apps open fine → not the whole PC.</li>
<li>A colleague signs in on the same PC and Outlook opens → not the PC: this user’s profile.</li>
<li>Scope written in the ticket: one app, one profile, one PC.</li>
<li>Fix in proportion: repair that user’s Outlook profile settings. No reimage.</li></ol>''',
                   L111 + ' (the four scope questions, as a worked trace written for this rung)',
                   [check('In the trace, why was a reimage never on the table?',
                          'Outlook worked for a colleague on the same PC',
                          ['Reimaging needs a manager’s phone call first', 'The PC was too new to be reimaged under warranty'],
                          'A colleague succeeding on the same PC puts the fault in the user’s profile, so a profile-level repair is '
                          'in proportion. Reimaging would erase a healthy device to fix one profile.', mc=[FOLLOWS, RBFIRST])]),
            tryit('''<p>Sort each finding to the scope it proves, then reveal the fix that fits before you look.</p>''',
                  L111,
                  [check('Which finding means you should stop fixing devices one by one?',
                         'Many PCs fail on the same app version',
                         ['One PC fails for every user who signs in', 'One user fails on the only PC they use'],
                         'The same app failing on many devices after the same update is a pattern: report it to the app owner. One '
                         'PC failing for everyone is a device fault; one user is a profile or account question.', mc=[PATTERN, None])],
                  widget=sort('What does each finding prove?',
                              {'One profile': ['Works for a colleague on the same PC'],
                               'One device': ['Fails for every user on this PC only', 'Blank prints from this PC for everyone'],
                               'Fleet pattern': ['Fails on 30 PCs since the same update', 'Same error on every finance PC']},
                              'Name the scope out loud before anyone says “reimage”.'))),

        'core-content': section(
            'Core content', 'IT-11.1',
            [check('A user says “it just closes”. Which event do you look for in the Application log?',
                   'Application Error, event ID 1000',
                   ['Application Hang, event ID 1002', 'Kernel-Power, event ID 41 in the System log'],
                   'A crash is logged as Application Error (ID 1000) with the faulting module; a hang is Application Hang (ID '
                   '1002). Kernel-Power 41 is an unclean restart of the whole system.', mc=[EVID, KP41])],
            plain('''<p>Software trouble comes in five shapes.</p>
<ul><li><strong>Crash</strong> — it just closes. Look for event 1000.</li>
<li><strong>Hang</strong> — “not responding”. Look for event 1002.</li>
<li><strong>Error message</strong> — copy the exact words and code.</li>
<li><strong>Slow</strong> — note when it started and what is slow.</li>
<li><strong>Wrong result</strong> — write the steps to make it happen again.</li></ul>
<p>Then find the scope: one app, one user, one PC, or many PCs.</p>
<p>Copy error text exactly. You can search for exact words. A summary like “some error” helps nobody.</p>''',
                  L111 + '; ' + MS_EV,
                  [check('Why copy the exact error text instead of summarising it?',
                         'Exact text and codes can be searched and matched',
                         ['Summaries are not allowed by the ticket system', 'The user will be offended by a paraphrase'],
                         'Exact wording and codes match vendor documentation and earlier tickets; “it gave some error” matches '
                         'nothing. Policy and politeness are not the reason.', mc=[PARA, PARA])]),
            analogy('''<p>Think of a doctor sorting patients by the shape of their complaint.</p>
<p>“I fainted” (a crash), “I froze and could not move” (a hang), “the test says code 0x5” (an error message), “I get
tired by noon” (slowness), and “my scales read 10 kg too heavy” (a wrong result) each send the doctor to a different
test. Naming the shape first saves running every test on everyone.</p>
<p>The doctor also asks whether the whole family is ill (many PCs), which changes it from one patient to a public
health report.</p>''',
                    L111 + ' (doctor-triage analogy written for this rung)',
                    [check('In the doctor story, “my scales read 10 kg too heavy” is which shape of software trouble?',
                           'A wrong result from the app',
                           ['A crash that closes the app', 'A hang with a spinning cursor'],
                           'The program runs but its output is wrong, so you collect the steps to reproduce, the input and the '
                           'expected output. A crash closes the app and a hang stops it responding.', mc=[PARA, None])]),
            visual(_SCOPE + '''
<ol class="ladder-trace">
<li>Event 1000: <code>report.exe</code> 4.2.0 crashed in module <code>pdfprint.dll</code> 1.8.3, code 0xc0000005.</li>
<li>The faulting module is a plug-in, not the main program.</li>
<li>Reliability Monitor: the plug-in was updated yesterday. Theory: the plug-in update.</li>
<li>Cheapest test: does it crash only when printing to PDF? Yes.</li>
<li>Report to the app owner with the event text and versions; workaround: Microsoft Print to PDF.</li></ol>''',
                   L111 + ' (scope diagram and worked example “reading a crash event”, drawn); ' + MS_EV,
                   [check('An app fails for one user on every PC they use. Where do you look?',
                          'Their account, licence, settings or data',
                          ['The first PC’s drivers and Windows updates', 'The network switch on that user’s floor'],
                          'A fault that follows the user across devices lives with the user: account, licence, roaming settings or '
                          'data. A device fault would stay on one PC.', mc=[FOLLOWS, FOLLOWS])]),
            tryit('''<p>Sort each user complaint to its shape, then reveal which evidence you would collect first.</p>''',
                  L111,
                  [check('A crash event names a faulting module that is a plug-in updated yesterday. What is the cheapest test?',
                         'Check whether it crashes only when that plug-in is used',
                         ['Reinstall Windows to clear every plug-in at once', 'Replace the PC’s memory and run the app again'],
                         'Testing the one action that uses the plug-in confirms the theory in a minute. A reinstall or a memory swap '
                         'is a large change with no evidence behind it.', mc=[CLAIM, RBFIRST])],
                  widget=sort('Which shape is each complaint?',
                              {'Crash': ['“It just disappears”'], 'Hang': ['“Not responding”, spinning cursor'],
                               'Error message': ['“It says 0x80070005”'], 'Slowness': ['“Saving takes two minutes”'],
                               'Wrong result': ['“It prints blank pages”']},
                              'The shape tells you which evidence to collect.'))),

        'scope-first': section(
            'Scope first', 'IT-11.1',
            [check('One app crashes for one user. Is a clean image in proportion?',
                   'No — repair that app or profile first',
                   ['Yes — a clean image fixes every kind of fault', 'Yes, as long as the user agrees on the phone'],
                   'A one-app crash is a small, named fault; a clean image wipes a healthy system to fix it. Repair the app or '
                   'the user’s settings, and record the exact error text.', mc=[RBFIRST, RBNOGATE])],
            plain('''<p>This box is the short rule to remember.</p>
<p>Check four sizes in order: one app, one profile, one PC, many PCs. Stop at the first one that fits.</p>
<p>Write the exact error text in the ticket.</p>
<p>And keep the fix the same size as the problem. One app crashing is a small problem. Wiping the PC is a big fix. Do not
use a big fix on a small problem.</p>''',
                  L111,
                  [check('What two things does the “scope first” rule ask you to write down?',
                         'The scope found and the exact error text',
                         ['The user’s password and the PC’s serial number', 'The time of the reboot and the next update'],
                         'The scope (app, profile, PC or many PCs) and the exact error text are the evidence the next person needs. '
                         'Passwords never go in a ticket.', mc=[PARA, None])]),
            analogy('''<p>Think of a tailor with a torn sleeve to mend.</p>
<p>The tailor checks the size of the tear before choosing the needle: a loose button needs a stitch, a torn sleeve
needs a patch, and only a coat that is falling apart is remade. Remaking the whole coat for a loose button is a waste of
the customer’s week. The tailor also writes on the ticket exactly where the tear is — “left cuff, 2 cm” — not “some
damage”.</p>''',
                    L111 + ' (tailor analogy written for this rung)',
                    [check('In the tailor story, what is “remaking the whole coat for a loose button”?',
                           'A clean image for a one-app crash',
                           ['Repairing one app’s settings for one user', 'Copying the exact error text into the ticket'],
                           'A clean image is the biggest fix there is; using it on a one-app fault costs the user their day for no '
                           'gain. Repairing settings and copying the error are the proportionate steps.', mc=[RBFIRST, None])]),
            visual('''<ol class="ladder-trace">
<li>One app? Yes, only the CAD viewer fails → stop widening; scope = one app.</li>
<li>Error copied exactly: “License server unavailable (-15,10032)”.</li>
<li>Fix size: one app, so a licence-setting check, not a reimage.</li></ol>''',
                   L111 + ' (the four-size ladder applied as a trace written for this rung)',
                   [check('Why is the exact text “(-15,10032)” more useful than “licence error”?',
                          'Exact codes can be searched in vendor documentation',
                          ['Codes in brackets are always from the network', 'Exact text makes the ticket shorter to read'],
                          'Exact codes can be searched and matched to the vendor’s documentation and earlier tickets. A summary '
                          'throws that evidence away.', mc=[PARA, DNSAPP])]),
            tryit('''<p>Put the four scope sizes in order, smallest first, and stop at the first that fits.</p>''',
                  L111,
                  [check('Which fix is the same size as “one app crashes for one user”?',
                         'Repair that app or that user’s settings',
                         ['Reimage the PC from the standard image', 'Replace the PC with a new one from stock'],
                         'A targeted repair matches a one-app, one-user fault. Reimaging or replacing hardware is a fix for a much '
                         'larger, proven problem.', mc=[RBFIRST, None])],
                  widget=order('Check the scope from smallest to largest.',
                               ['One app', 'One profile', 'One PC', 'Many PCs'],
                               'Stop at the first size that fits; that size chooses the fix.'))),

        'teach-block-scope-before-repair': section(
            'Teach block — scope before repair', 'IT-11.1',
            [check('In the class drill, what must a student do before saying “reimage”?',
                   'Name the scope out loud for that ticket',
                   ['Get the instructor’s signature on the ticket', 'Run a full antivirus scan on the PC'],
                   'The drill’s rule is that nobody proposes a reimage until they have named the scope — one app, one profile, '
                   'one PC or many PCs — because the scope decides the fix.', mc=[RBFIRST, None])],
            plain('''<p>This is a class drill.</p>
<p>You get three real tickets. For each one, say the scope out loud: one app, one profile, one PC, or many PCs.</p>
<p>Nobody may say “reimage” until they have said the scope first.</p>
<p>Why? Saying it out loud makes you think before you act. Most of the time, once the scope is named, a reimage is
clearly too big.</p>''',
                  L111,
                  [check('What usually happens once the scope has been named?',
                         'A reimage is clearly too big for it',
                         ['The ticket can be closed straight away', 'The user can fix it themselves at home'],
                         'Naming the scope usually shows the fault is one app or one profile, so a targeted repair fits and a '
                         'reimage would be out of proportion.', mc=[SCOPE, None])]),
            analogy('''<p>Think of a driving instructor’s rule: say “mirror, signal” out loud before every turn.</p>
<p>Saying it feels slow at first, but it stops the habit of turning without looking. In the scope drill, saying “one
profile” out loud before touching anything does the same job: it stops the habit of reaching for the biggest fix
because it feels decisive. After a few weeks the words become automatic and the bad turns stop.</p>''',
                    L111 + ' (driving-instructor analogy written for this rung)',
                    [check('In the driving story, the spoken “mirror, signal” matches which part of the drill?',
                           'Saying the scope before proposing any fix',
                           ['Reimaging any PC that looks slow during class', 'Reading the ticket silently and then fixing it'],
                           'The spoken scope is the check before the action, like “mirror, signal” before a turn. It builds the habit '
                           'of thinking first.', mc=[RBFIRST, None])]),
            visual('''<ol class="ladder-trace">
<li>Ticket A: “Teams crashes on start for me only” → scope said: <em>one profile</em> → reset Teams for that user.</li>
<li>Ticket B: “Every login on PC-114 is slow” → scope said: <em>one PC</em> → look at that device.</li>
<li>Ticket C: “Payroll app errors on all finance PCs since Monday” → scope said: <em>many PCs</em> → report a pattern.</li>
<li>Nobody said “reimage” in any of the three.</li></ol>''',
                   L111 + ' (the drill’s three-ticket round, as a worked trace written for this rung)',
                   [check('Ticket C fails on every finance PC since Monday. What does the student say and do?',
                          'Many PCs — report a pattern to the app owner',
                          ['One PC — reimage each finance PC in turn', 'One profile — reset each user’s app settings'],
                          'The same failure across many PCs since one date is a pattern; fixing devices one by one wastes time and '
                          'misses the cause.', mc=[PATTERN, PATTERN])]),
            tryit('''<p>Try the drill yourself: read each ticket line, say the scope, then reveal the answer.</p>''',
                  L111,
                  [check('“Excel crashes for Sam on any PC he uses.” Which scope do you say?',
                         'One user, following him across PCs',
                         ['One PC, because Excel lives on the PC', 'Many PCs, because it fails on several'],
                         'The fault follows the user, not the device, so it lives in his account, licence or data. It is not a fleet '
                         'pattern, because other users are fine.', mc=[FOLLOWS, PATTERN])],
                  widget=reveal('Say the scope: “Only the front-desk PC prints blank pages, for every receptionist.”',
                                '<strong>One PC.</strong> Every user fails on that device only, so look at its driver, queue and updates.'))),

        'more-windows-symptoms-no-os-found-shutdowns-services-usb-res': section(
            'More Windows symptoms: no OS found, shutdowns, services, USB resources', 'IT-11.3',
            [check('A PC says “No operating system found” the morning after a USB installer was used. What do you check first?',
                   'Remove the USB stick, or fix the boot order',
                   ['Run bootrec /rebuildbcd from the recovery tools', 'Replace the system drive, because it has failed'],
                   'The PC is probably trying to boot from the USB stick left in first. Check removable media, firmware detection '
                   'and boot order before repairing boot files or replacing hardware.', mc=[BOOTREC, BOOTREC])],
            plain('''<p>Some Windows symptoms have a quick first check.</p>
<ul><li><strong>No OS found.</strong> Take out any USB stick. Check the boot order. Only later repair boot files.</li>
<li><strong>Turns itself off.</strong> Look for event 41 (Kernel-Power). It often means heat or power, not software.</li>
<li><strong>A service will not start.</strong> Check its log-on account. An old password is common.</li>
<li><strong>“Not enough USB controller resources.”</strong> Too many devices on one controller. Move some to other ports.</li>
<li><strong>Random freezes.</strong> Roll back a new driver. Test memory, disk and heat.</li></ul>''',
                  L111 + '; ' + MS_BOOT + '; ' + MS_EV,
                  [check('A PC switches off with Event 41 and no bug-check code. What does that suggest?',
                         'Power was lost — often heat or the power supply',
                         ['An app crashed and closed the user’s documents', 'A Windows update installed itself and restarted'],
                         'Kernel-Power 41 with no BugCheck means Windows restarted without a clean shutdown; check temperatures, '
                         'dust, the PSU and the power plan. An update restart is a clean shutdown.', mc=[KP41, KP41])]),
            analogy('''<p>Think of a car that will not start.</p>
<p>Before you take the engine apart, you check the obvious: is it in park (a USB stick first in the boot order)? Is the
key the right one for this car (UEFI versus legacy mode)? Only then do you open the bonnet (Startup Repair and bootrec).</p>
<p>A car that keeps cutting out on hills is overheating, not badly driven — like Event 41 with a dusty heatsink. And a
car whose new key fob was never paired (a service still holding an old password) will not start however healthy the
engine is.</p>''',
                    L111 + ' (car analogy written for this rung)',
                    [check('In the car story, “a key fob that was never paired” matches which Windows symptom?',
                           'A service holding an old log-on password',
                           ['A USB stick left first in the boot order', 'A heatsink packed with dust'],
                           'The service’s account password changed under policy but the service still holds the old one, so it '
                           'cannot log on. Update it on the Log On tab or use a managed service account.', mc=[REBOOT, None])]),
            visual(_NOOS + '''
<ol class="ladder-trace">
<li>A PC “just turns off” two or three times a day; no blue screen.</li>
<li>System log: Event 41 (Kernel-Power) at each time, no BugCheck → power was lost, not a crash.</li>
<li>Hardware monitor: CPU at 100 °C under load; heatsink fins packed with dust.</li>
<li>Power off, unplug, ESD precautions; clean the cooler and filters → 70 °C under load.</li>
<li>No shutdowns in a week; add the site to the cleaning schedule.</li></ol>''',
                   L111 + ' (no-OS check order and worked example “a PC that switches itself off”, drawn); ' + MS_EV,
                   [check('Windows says “Not enough USB controller resources”. What is the first fix?',
                          'Move devices to ports on another controller',
                          ['Reinstall Windows to reset every USB driver', 'Replace the keyboard and mouse with new ones'],
                          'Too many devices or hubs share one controller; moving some to rear ports (a different controller) or '
                          'removing an unpowered hub frees resources.', mc=[RBFIRST, None])]),
            tryit('''<p>Order the “no OS found” checks, then reveal where you would read a service’s log-on failure.</p>''',
                  L111 + '; ' + MS_BOOT,
                  [check('Which order does Microsoft give for repairing system files?',
                         'DISM /RestoreHealth, then sfc /scannow',
                         ['sfc /scannow, then format the system drive', 'chkdsk /f, then reinstall every application'],
                         'DISM repairs the component store that sfc uses as its source, so it runs first; then sfc repairs the '
                         'system files. Formatting or reinstalling apps is not a file repair.', mc=[RBFIRST, None])],
                  widget=order('Put the “No operating system found” checks in order.',
                               ['Is the drive detected in UEFI?', 'Boot order and USB sticks', 'UEFI or legacy mode matches the disk',
                                'WinRE Startup Repair', 'bootrec, then restore if the disk is failing'],
                               'Most “no OS” tickets are settled by the first two checks.'),
                  lab={'id': 'w11-services', 'note': 'Check a service’s start type, state and dependencies before changing it.'})),
    },
    '11.2': {
        'core-content': section(
            'Core content', 'IT-11.4',
            [check('Why tick “Hide all Microsoft services” before “Disable all” in msconfig?',
                   'So only third-party services are switched off',
                   ['So Windows can install updates during the test', 'So the PC will start straight into Safe Mode'],
                   'Hiding Microsoft services keeps Windows’ own services running; the clean boot then removes only third-party '
                   'services and startup items, which are the usual suspects.', mc=[SAFEREAD, SAFELEFT])],
            plain('''<p>To find what is getting in the way, take everything away. Then add it back bit by bit.</p>
<ol><li><strong>Clean boot.</strong> In msconfig, hide Microsoft services and disable the rest. Turn off startup apps.
Restart. If the fault is gone, turn half back on and test again.</li>
<li><strong>Safe Mode.</strong> Windows starts with very little. If the fault goes away, a driver or startup program is to
blame.</li>
<li><strong>Repair or Reset the app.</strong> Repair keeps its data. Reset wipes its data.</li>
<li><strong>Another profile.</strong> If it works for another user, the problem is in the first user’s profile.</li></ol>
<p>Afterwards, put things back the way you found them.</p>''',
                  L112 + '; ' + MS_CLEAN,
                  [check('What is the difference between Repair and Reset for a Store app?',
                         'Repair keeps the app’s data; Reset clears it',
                         ['Reset keeps the app’s data; Repair clears it', 'They are the same, so either one is fine to use'],
                         'Repair fixes damaged app files and keeps data; Reset also removes the app’s data and settings on this '
                         'device. Warn the user before a Reset.', mc=[RESETK, RESETK])]),
            analogy('''<p>Think of finding which guest at a dinner party keeps setting off the smoke alarm.</p>
<p>You send everyone outside (a clean boot): the alarm stops. Then you let half back in. If it goes off, the culprit is
in that half; if not, the other half. Halve again, and in four rounds you find one guest among sixteen — far quicker than
one at a time.</p>
<p>Safe Mode is cooking with only the host in the kitchen: if the alarm stays silent, it was a guest, not the oven. And
when you are done, everyone except the culprit goes back to the table.</p>''',
                    L112 + ' (dinner-party analogy written for this rung)',
                    [check('In the dinner-party story, “cooking with only the host in the kitchen” matches what?',
                           'Starting Windows up in Safe Mode first',
                           ['Resetting the app and clearing its data', 'Signing in with a second user profile'],
                           'Safe Mode loads a minimal set of drivers and services; a fault that disappears there points at a driver, '
                           'service or startup program rather than core Windows.', mc=[SAFEREAD, None])]),
            visual(_HALVE + '''
<ol class="ladder-trace">
<li>All 16 non-Microsoft items off → fault gone.</li>
<li>Items 1–8 on → fault back. Culprit in 1–8.</li>
<li>Items 1–4 on (5–8 off) → fault gone. Culprit in 5–8.</li>
<li>5–6 on → fault back; then 5 alone → fault back. Culprit: item 5.</li>
<li>Leave item 5 off, restore the other 15, record the change.</li></ol>''',
                   L112 + ' (halving diagram, as a worked trace written for this rung)',
                   [check('A fault disappears in Safe Mode. What does that suggest?',
                          'A driver, service or startup program is involved',
                          ['The hard drive is failing and needs replacing', 'The network cable to the PC is damaged'],
                          'Safe Mode leaves out non-essential drivers, services and startup programs, so one of those is likely. A '
                          'fault that stays in Safe Mode points at the core OS, hardware or user data.', mc=[SAFEREAD, SAFEREAD])]),
            tryit('''<p>Order the halving steps, then reveal what to undo afterwards before you look.</p>''',
                  L112 + '; ' + MS_CLEAN,
                  [check('You used msconfig → Boot → Safe boot to test. What must you do afterwards?',
                         'Go back into msconfig and untick Safe boot',
                         ['Nothing — Windows clears it at the next start', 'Run sfc /scannow to switch Safe Mode off'],
                         'The msconfig Safe boot setting persists; if it stays ticked, the PC keeps starting in Safe Mode. Windows '
                         'does not clear it on its own.', mc=[SAFELEFT, SAFELEFT])],
                  widget=order('Halve sixteen clean-boot items to find the culprit.',
                               ['Turn all 16 off and confirm the fault is gone', 'Turn 8 back on and test',
                                'Turn on half of the guilty group', 'Repeat until one item is left', 'Leave it off, restore the rest, record it'],
                               'Sixteen items take at most four restarts when you halve.'))),

        'controls': section(
            'Controls', 'IT-11.1',
            [check('An app says “cannot connect”. Ping to the server’s IP works, but ping to its name fails. Where is the fault?',
                   'Name resolution (DNS)',
                   ['The app’s program files', 'The PC’s network cable'],
                   'If the IP answers, the cable and routing work; a failing name means DNS. Repairing Office or the app would '
                   'not touch that domain — run the Chapter 5 network checks first.', mc=[DNSAPP, DNSAPP])],
            plain('''<p>A <strong>control</strong> is a comparison that tells you where the fault is.</p>
<p>Try three things: another app, another profile, another PC.</p>
<p>If the app says “no network”, check the network first (Chapter 5). Do not repair Office for a network fault.</p>
<p>A quick test: ping the server’s address, then ping its name. If the address works and the name does not, the problem
is DNS. It is not the app.</p>''',
                  L112,
                  [check('Why run the Chapter 5 network checks before an Office repair when the symptom is “no network in the app”?',
                         'A network fault cannot be fixed by repairing the app',
                         ['Office repairs need the network to be down first', 'Chapter 5 checks are faster to write in the ticket'],
                         'If the network or name resolution is the domain, repairing the app changes nothing. Prove the network '
                         'works before blaming the software.', mc=[DNSAPP, None])]),
            analogy('''<p>Think of a radio that has gone silent.</p>
<p>Before opening it up, you try a different station (another app), a different room (another profile), and a
different radio (another PC). If every radio in the house is silent on that station, the transmitter is off, not your
set. And if you can hear the station when you type its frequency but not when you press the preset button, the preset
list is wrong — the radio is fine. That preset list is DNS.</p>''',
                    L112 + ' (radio analogy written for this rung)',
                    [check('In the radio story, “the frequency works but the preset button does not” matches what?',
                           'Ping by IP works, ping by name fails',
                           ['The app crashes as soon as it starts up', 'Every PC in the building loses its network'],
                           'Reaching the server by address but not by name is a name-resolution fault, like a wrong preset. An app '
                           'crash or a building-wide outage are different domains.', mc=[DNSAPP, None])]),
            visual('''<ol class="ladder-trace">
<li>“The finance app says cannot connect.” Another app on the same PC browses fine.</li>
<li><code>ping 10.20.0.15</code> → replies. Cable and routing work.</li>
<li><code>ping fin-app01</code> → “could not find host”. Name resolution fails.</li>
<li>Domain: DNS, not the app. Hand to the network checks; no Office or app repair.</li></ol>''',
                   L112 + ' (the ping-by-IP-then-name control, as a worked trace written for this rung)',
                   [check('In the trace, what did the successful ping to 10.20.0.15 rule out?',
                          'The cable and the routing to the server',
                          ['Every DNS problem on the client', 'The app’s licence and its settings'],
                          'A reply by IP proves the physical link and routing to the server work. It says nothing about DNS, which '
                          'the failed name ping then exposed.', mc=[DNSAPP, None])]),
            tryit('''<p>Sort each control result to the domain it points at, then reveal the next test.</p>''',
                  L112,
                  [check('The app fails in every profile on this PC but works at the next desk. Which domain?',
                         'This machine',
                         ['The user’s profile', 'The server'],
                         'Failing for everyone on one PC while working on another puts the fault on the machine. A profile fault '
                         'would work for other users; a server fault would fail at the next desk too.', mc=[FOLLOWS, None])],
                  widget=sort('Where does each control result point?',
                              {'DNS': ['Ping by IP works, by name fails', 'nslookup finds no record for the server'],
                               'Profile': ['Works for another user on this PC'],
                               'Machine': ['Fails for all users here, works next desk', 'Every user on PC-12 fails']},
                              'Each comparison removes one domain.'))),

        'profile-versus-machine': section(
            'Profile versus machine', 'IT-11.1',
            [check('An app fails on every PC in the office for every user. Which domain is left?',
                   'The server, the licence or the network path',
                   ['One user’s profile settings on their own PC', 'This one machine’s drivers and its disk'],
                   'When it fails everywhere for everyone, nothing on any single PC or profile explains it; the shared parts — the '
                   'server, the licence or the network path — are left.', mc=[PATTERN, SCOPE])],
            plain('''<p>Three results, three answers.</p>
<ul><li>Works for another user on this PC → the <strong>profile</strong>.</li>
<li>Fails for every user on this PC, but works at the next desk → the <strong>machine</strong>.</li>
<li>Fails on every PC → the <strong>server</strong>, the <strong>licence</strong> or the <strong>network path</strong>.</li></ul>
<p>Each result points to who fixes it. A profile is fixed for one user. A machine is fixed at that desk. A server problem goes
to the team that owns it.</p>''',
                  L112,
                  [check('The app works when a colleague signs in on the same PC. Which domain?',
                         'The first user’s own profile',
                         ['The PC’s hardware and drivers', 'The shared licence server'],
                         'If another user succeeds on the same hardware, the PC and server are fine; the first user’s profile — '
                         'settings, cached credentials, add-ins — is the domain.', mc=[FOLLOWS, None])]),
            analogy('''<p>Think of a hotel where a guest cannot get the shower to run hot.</p>
<p>If the next guest in the same room has a hot shower, it was how the first guest set the dial (the profile). If nobody in
that room gets hot water but the room next door is fine, it is that room’s boiler (the machine). If no room in the hotel
has hot water, it is the main supply (the server, licence or network path). The answer also tells you whether to call
housekeeping, a plumber or the utility company.</p>''',
                    L112 + ' (hotel-shower analogy written for this rung)',
                    [check('In the hotel story, “no room in the hotel has hot water” matches which domain?',
                           'Server, licence or network path',
                           ['One guest’s profile settings', 'That one room’s machine'],
                           'Failing everywhere puts the cause in the shared supply, so it goes to the team that owns the server, '
                           'the licence or the path.', mc=[PATTERN, None])]),
            visual('''<ol class="ladder-trace">
<li>Test 1: a colleague signs in on the same PC → works? If yes: <strong>profile</strong>. Stop.</li>
<li>Test 2: same user at the next desk → works? If yes: <strong>machine</strong>. Stop.</li>
<li>Both fail, and other PCs fail too → <strong>server, licence or network path</strong>.</li></ol>''',
                   L112 + ' (the profile-versus-machine decision, as a numbered trace)',
                   [check('Why stop at test 1 when a colleague succeeds on the same PC?',
                          'It already proves the fault is in the profile',
                          ['Policy allows only one test per ticket', 'The colleague’s profile is now broken as well'],
                          'A success on the same PC removes the machine and server from suspicion, so the profile is the answer. '
                          'More tests would add no information.', mc=[FOLLOWS, None])]),
            tryit('''<p>Sort each result to its domain, then reveal who owns the fix.</p>''',
                  L112,
                  [check('Who should fix a fault that fails on every PC for every user?',
                         'The team that owns the server or licence',
                         ['The technician at the first desk that reported it', 'Each user, by resetting their own profile'],
                         'A fleet-wide failure is the shared service’s problem; repairing desks or profiles one by one does not '
                         'touch it.', mc=[PATTERN, None])],
                  widget=sort('Which domain?',
                              {'Profile': ['Works for another user on this PC', 'A test user on this PC is fine'],
                               'Machine': ['Fails for all here, works next desk'],
                               'Server / licence / path': ['Fails on every PC for everyone', 'Same error at three sites']},
                              'The domain decides who fixes it.'))),
    },

    '11.3': {
        'core-content': section(
            'Core content', 'IT-11.2',
            [check('At the end of a 45-minute time box you have found several unrelated faults and unknown changes. What now?',
                   'Plan a rebuild with a verified backup',
                   ['Keep repairing each fault until all of them are gone', 'Close the ticket and ask the user to restart daily'],
                   'Several unrelated faults and unknown changes favour a rebuild, which is quicker and more certain — after a '
                   'verified backup, an app list and approval. Endless repair costs the user their day.', mc=[ENDLESS, ENDLESS])],
            plain('''<p>Every software fault ends in one of three fixes.</p>
<ul><li><strong>Repair</strong> one thing, when you can name the broken part.</li>
<li><strong>Reinstall Windows in place</strong>, when system files are broken but apps and files are fine.</li>
<li><strong>Rebuild</strong>, when there are many faults, unknown changes or a hack.</li></ul>
<p>Pick the smallest fix that will really work.</p>
<p>Agree a time limit for repair, such as 45 minutes. If you have not found the cause by then, compare with a rebuild.</p>
<p>A rebuild is a change. Back up first and check the backup opens. List the apps and licences. Get approval.</p>''',
                  L113,
                  [check('What must be true about the backup before a rebuild?',
                         'A file from it has actually been opened',
                         ['It was started at some point this week', 'It is on the same disk as the user’s data'],
                         'A backup is only proven when a file from it opens. “Started this week” proves nothing, and a backup on '
                         'the same disk is lost with it.', mc=[RBNOGATE, RBORDER])]),
            analogy('''<p>Think of a mechanic with a car that keeps breaking.</p>
<p>One worn brake pad is a repair. An engine that needs new seals but a fine body is a rebuild of the engine only (an
in-place reinstall). A car with five unrelated faults and a mystery modification by the last owner is often cheaper to
replace with a standard one from the fleet (a rebuild).</p>
<p>The mechanic agrees a time limit with the owner at the start. And before scrapping a car, they empty the glovebox
and write down the radio presets — the lab coordinator’s macros were in the glovebox.</p>''',
                    L113 + ' (mechanic analogy written for this rung, after the lesson’s “rebuild that lost the macros”)',
                    [check('In the mechanic story, “emptying the glovebox” before scrapping matches which rebuild step?',
                           'Listing the apps, add-ins and settings first',
                           ['Agreeing the time limit with the car’s owner', 'Ordering a standard car from the fleet manager'],
                           'The rebuild that lost the macros failed at the inventory step: local add-ins were not listed or backed up. '
                           'The decision was right; the missing list was the failure.', mc=[RBORDER, None])]),
            visual(_DECIDE + '''
<ol class="ladder-trace">
<li>20 min: crash events name three different modules on three days; sfc repairs files; crashes continue.</li>
<li>40 min: clean boot does not stop them; several failed updates and an unknown utility.</li>
<li>45 min decision: many unrelated faults, unknown changes → rebuild.</li>
<li>Plan: verified backup, app list with licence keys, rebuild after 16:00 with the user’s agreement.</li>
<li>Verify: the user runs an end-of-day report.</li></ol>''',
                   L113 + ' (decision diagram and worked example “the 45-minute time box”, drawn)',
                   [check('System files are damaged but the user’s apps and data are fine. Which option fits?',
                          'An in-place reinstall of Windows',
                          ['A full rebuild from the standard image', 'Replacing the PC with a new one from stock'],
                          'An in-place reinstall repairs Windows while keeping apps and data. A rebuild or replacement is for many '
                          'faults, unknown changes or a compromise.', mc=[RBFIRST, None])]),
            tryit('''<p>Put the rebuild steps in order, then reveal what proves the rebuild worked.</p>''',
                  L113,
                  [check('Why list applications and licences before a rebuild?',
                         'So everything can be reinstalled and activated',
                         ['So the old licences can be sold on afterwards', 'So the rebuild finishes faster than planned'],
                         'Without the list, apps, plug-ins and licence keys the user needs are missed and the rebuild costs days. '
                         'It is not about resale or speed.', mc=[RBORDER, None])],
                  widget=order('Order the rebuild as a change.',
                               ['Back up and open a file from the backup', 'List apps, versions, licences and settings',
                                'Approve and agree a time with the user', 'Rebuild and restore', 'User signs in and repeats the failing task'],
                               'Data first, inventory second; the user’s own test is the verification.'))),

        'repair-before-rebuild': section(
            'Repair before rebuild', 'IT-11.2',
            [check('Which three things must be in place before a rebuild?',
                   'A backup, a change ticket and a listed disk',
                   ['A reboot, a new password and a spare PC', 'The user’s verbal OK and a USB installer'],
                   'The lesson’s gate is a verified backup, a change ticket and the disk listed (so you erase the right one). A '
                   'verbal OK and an installer are not a gate.', mc=[RBNOGATE, RBGATE])],
            plain('''<p>Try the smaller fix first. Repair, or reinstall Windows in place.</p>
<p>A rebuild comes last. Before it, three things must be true:</p>
<ol><li>The backup is done and checked.</li><li>There is a change ticket.</li><li>You have listed the disks, so you wipe the right one.</li></ol>
<p>One app crashing never earns a wipe.</p>''',
                  L113,
                  [check('Why list the disks before a rebuild?',
                         'So the right disk is the one erased',
                         ['So the rebuild uses less disk space', 'So the backup runs faster that night'],
                         'Listing disks first (for example in Disk Management or diskpart list disk) makes sure the system disk, '
                         'not the data disk, is the one wiped.', mc=[RBNOGATE, None])]),
            analogy('''<p>Think of a demolition crew.</p>
<p>Before any wall comes down, three things happen: the tenants’ belongings are moved out and checked off (the
verified backup), the council permit is pinned to the fence (the change ticket), and the surveyor marks exactly which
building is coming down (listing the disk). A crew that knocks down the wrong house next door because nobody checked
the address has a very bad day. Most cracked plaster is patched, not demolished.</p>''',
                    L113 + ' (demolition analogy written for this rung)',
                    [check('In the demolition story, “the surveyor marks exactly which building” matches which gate?',
                           'Listing the disk before erasing',
                           ['Getting the change ticket approved', 'Checking the backup opens'],
                           'Listing disks makes sure the one erased is the right one, like marking the building. The permit is the '
                           'change ticket and the moved belongings are the backup.', mc=[RBNOGATE, None])]),
            visual('''<ol class="ladder-trace">
<li>Repair or in-place reinstall tried? If it worked, stop.</li>
<li>Backup: a file opened from it ✔.</li>
<li>Change ticket approved ✔.</li>
<li>Disks listed: Disk 0 = 512 GB system, Disk 1 = 2 TB data — wipe Disk 0 only ✔.</li>
<li>All three ticked → rebuild may start.</li></ol>''',
                   L113 + ' (the rebuild gate, as a worked checklist written for this rung)',
                   [check('The backup has not been tested, but the user is in a hurry. Can the rebuild start?',
                          'No — open a file from the backup first',
                          ['Yes, as long as the user agrees out loud', 'Yes, because most backups work anyway'],
                          'An untested backup is not a backup; the gate must be complete. Speed or a verbal OK does not replace a '
                          'file actually opened from it.', mc=[RBNOGATE, RBNOGATE])]),
            tryit('''<p>Tick the gate yourself: reveal the answer once you have decided whether this rebuild may start.</p>''',
                  L113,
                  [check('A single app crashes daily. Does that earn a rebuild?',
                         'No — repair or reinstall that app first',
                         ['Yes, a rebuild is always the quickest fix', 'Yes, if the PC is more than two years old'],
                         'One crashing app is a named component: a targeted repair or reinstall of that app is in proportion. Age '
                         'and speed do not justify a wipe.', mc=[RBFIRST, None])],
                  widget=reveal('Backup verified ✔, change ticket ✔, disks not yet listed. May the rebuild start?',
                                '<strong>Not yet.</strong> List the disks first so the right one is erased; then all three gates are met.'))),

        'windows-tools-task-manager-and-the-management-consoles': section(
            'Windows tools: Task Manager and the management consoles', 'IT-11.3',
            [check('Which tool shows which process is holding a file open?',
                   'Resource Monitor, run as resmon',
                   ['Disk Management (diskmgmt.msc)', 'Certificate Manager (certmgr.msc)'],
                   'Resource Monitor’s CPU tab → Associated Handles shows which process has a file open. Disk Management handles '
                   'volumes, and Certificate Manager holds certificates.', mc=[LOCKED, None])],
            plain('''<p>Windows has a tool for each kind of question.</p>
<ul><li>Is it running? What is it using? <strong>Task Manager</strong> (Ctrl+Shift+Esc).</li>
<li>What happened, and when? <strong>Event Viewer</strong>.</li>
<li>Is the hardware seen? <strong>Device Manager</strong>.</li>
<li>Which disks are there? <strong>Disk Management</strong>.</li>
<li>Does something run on a timer? <strong>Task Scheduler</strong>.</li></ul>
<p>Most open from Win+R with a name ending in .msc. Some, like gpedit.msc, are not in Windows Home.</p>''',
                  L113 + '; ' + MS_TOOLS,
                  [check('Why is gpedit.msc missing on a user’s PC?',
                         'It is not included in Windows Home',
                         ['A Windows service has stopped running', 'The PC is not connected to the network'],
                         'Local Group Policy Editor and Local Users and Groups are not part of Windows Home. A stopped service or '
                         'the network does not remove them.', mc=[EDITION, EDITION])]),
            analogy('''<p>Think of a hospital’s departments.</p>
<p>You go to the monitor by the bed to see what is happening now (Task Manager), to the patient’s notes to see what
happened overnight (Event Viewer), to radiology to check the bones are there and connected (Device Manager), to the
records office for the filing layout (Disk Management), and to the medication schedule for what is given at set times
(Task Scheduler). Asking radiology about last night’s fever wastes everyone’s time.</p>''',
                    L113 + ' (hospital-departments analogy written for this rung)',
                    [check('In the hospital story, “the patient’s notes for what happened overnight” is which tool?',
                           'Event Viewer',
                           ['Task Manager', 'Device Manager'],
                           'Event Viewer holds the System, Application and Security logs — the record of what happened and when. Task '
                           'Manager shows the present, and Device Manager the hardware.', mc=[EDITION, None])]),
            visual(_TOOLS + '''
<ol class="ladder-trace">
<li>Slow for the first ten minutes: Task Manager → Performance, disk at 100% after sign-in.</li>
<li>Processes by Disk: a cloud-sync client and a vendor updater.</li>
<li>Startup apps: updater enabled, “High” impact → disable it there.</li>
<li>Task Scheduler: the same updater runs “At log on” → disable that task too.</li>
<li>Event Viewer → System: no disk errors. Restart: disk settles within two minutes.</li></ol>''',
                   L113 + ' (tool-by-question diagram and worked example “slow for the first ten minutes”, drawn); ' + MS_TOOLS,
                   [check('In the trace, why check Task Scheduler after disabling the startup item?',
                          'The updater also started from a logon task',
                          ['Task Scheduler restores disabled startup items', 'Disk errors are recorded only in Task Scheduler'],
                          'A program can start from both the Startup apps list and a scheduled task “At log on”; disabling only one '
                          'leaves it running. Disk errors are in Event Viewer.', mc=[BOTTLE, None])]),
            tryit('''<p>Sort each question to the tool that answers it, then find a device with a warning icon in the
Device Manager simulator.</p>''',
                  L113 + '; ' + MS_TOOLS,
                  [check('Which Task Manager page shows other people signed in to the same PC?',
                         'The Users page',
                         ['The Startup apps page', 'The Performance page'],
                         'The Users page lists signed-in users and what each is using. Startup apps lists what runs at sign-in, and '
                         'Performance shows CPU, memory, disk and network trends.', mc=[EDITION, None])],
                  widget=sort('Which tool answers it?',
                              {'Task Manager': ['Which process is using the CPU now?'], 'Event Viewer': ['Why did it restart at 03:12?'],
                               'Device Manager': ['Is the webcam driver loaded?'], 'Disk Management': ['Is the new disk initialised?'],
                               'Task Scheduler': ['What runs every night at 02:00?']},
                              'Start from the question, then pick the console.'),
                  lab={'id': 'gui-devices', 'note': 'Find the device with a warning icon and read its status, as in devmgmt.msc.'})),
    },

    '11.4': {
        'core-content': section(
            'Core content', 'IT-11.3',
            [check('The welcome screen sits on “Applying user settings” for five minutes. Which log do you open?',
                   'The GroupPolicy Operational log',
                   ['The Security log, for failed sign-ins', 'The Setup log, for installed updates'],
                   'User policy is the stage that is slow, and the GroupPolicy Operational log records how long processing took. '
                   'gpresult /h then shows the scripts and drive mappings that ran.', mc=[GUESS, GUESS])],
            plain('''<p>A slow logon has stages. Time each stage. Do not guess.</p>
<ol><li>Computer policy and network.</li><li>User policy: scripts and drive maps.</li><li>Loading the profile.</li>
<li>Startup apps.</li><li>The desktop is ready.</li></ol>
<p>Each stage leaves its own evidence. The slowest stage tells you who fixes it.</p>
<p>Memory that grows for hours and never falls is a leak.</p>
<p>If the desktop looks brand new, the user may be on a temporary profile. Do not delete the profile folder. Escalate.</p>''',
                  L114 + '; ' + MS_GP,
                  [check('A user’s desktop looks brand new and says “We can’t sign in to your account”. What must you not do?',
                         'Delete the profile folder or edit the registry',
                         ['Write down the exact message in the ticket', 'Ask the user not to save work on the PC'],
                         'The user is on a temporary profile and their data is still in the original one. Recording the message and '
                         'warning them are right; deleting or editing is for the endpoint team.', mc=[TEMPDEL, TEMPP])]),
            analogy('''<p>Think of a parcel that takes six days to arrive.</p>
<p>Instead of blaming “the post”, you read the tracking: collected Monday, one day at the depot, four days waiting at a
sorting office for a van that never came, one day out for delivery. The four days name the problem, and the sorting office
is who fixes it. A slow logon has its own tracking: the GroupPolicy log, User Profile Service events and the Startup apps
list. The longest wait names the owner.</p>''',
                    L114 + ' (parcel-tracking analogy written for this rung)',
                    [check('In the parcel story, “four days waiting for a van that never came” is like what at logon?',
                           'A logon script waiting for a retired server',
                           ['A large profile copying files from a fast server', 'A startup app with a “Low” impact rating'],
                           'A logon script that maps a drive to a server that no longer exists waits for a timeout, like the van that '
                           'never comes. That one stage is where the time goes.', mc=[GUESS, None])]),
            visual(_LOGON + '''
<ol class="ladder-trace">
<li>“Applying user settings” for five minutes.</li>
<li>GroupPolicy Operational log: user policy took about 300 seconds.</li>
<li><code>gpresult /h</code>: a logon script maps S: to <code>\\\\oldfs01\\shared</code>.</li>
<li><code>Test-NetConnection oldfs01 -Port 445</code> fails: retired last month.</li>
<li>Policy owner removes the mapping (a change); next sign-in takes 40 seconds; record it in the problem record.</li></ol>''',
                   L114 + ' (logon-stage diagram and worked example “the 6-minute logon”, drawn); ' + MS_GP,
                   [check('Why record this fix in the problem record, not only the ticket?',
                          'Every user with that policy was affected',
                          ['Problem records are shorter to write up', 'The ticket system cannot store gpresult output'],
                          'The cause sat in a shared policy, so every user who received it had the slow logon; the problem record '
                          'links them and stops repeat tickets.', mc=[PATTERN, None])]),
            tryit('''<p>Order the logon stages, then work out what is running at sign-in on the Windows 11 VM.</p>''',
                  L114 + '; ' + MS_GP,
                  [check('One process’s memory grows steadily for hours and never falls. What do you suspect?',
                         'A memory leak inside that one running process',
                         ['Not enough RAM for the user’s normal workload', 'A failing disk slowing everything down'],
                         'Memory that only grows in one process is a leak. Too little RAM shows as high use from normal work, and a '
                         'slow disk shows as long response times in Resource Monitor.', mc=[BOTTLE, BOTTLE])],
                  widget=order('Order the slow-logon stages.',
                               ['Computer policy and network', 'User policy: scripts and drive maps', 'Profile load', 'Startup apps',
                                'Desktop usable'],
                               'Time each stage; the slowest one names the owner of the fix.'),
                  lab={'id': 'w11-processes', 'note': 'List what is running at sign-in before forming one theory.'})),

        'slow-logon': section(
            'Slow logon', 'IT-11.3',
            [check('Is rebooting the PC over and over a way to identify a slow logon’s cause?',
                   'No — it changes things without proving anything',
                   ['Yes — each reboot clears one cause at a time', 'Yes, if you reboot at least three times in a row'],
                   'A reboot loop is not identification: it destroys the state you need and tests nothing. Gather inventory, '
                   'updates, services and processes, then test one theory.', mc=[REBOOT, REBOOT])],
            plain('''<p>This box gives the order of work for a slow logon.</p>
<ol><li>Check what the PC is.</li><li>Check updates.</li><li>Check services.</li><li>Check what is running.</li></ol>
<p>Then pick <em>one</em> idea and test it. Is it the profile, a network home folder, the disk, or Group Policy?</p>
<p>Rebooting again and again is not a test. It only changes things.</p>''',
                  L114,
                  [check('After collecting evidence, how many theories do you test at once?',
                         'Just one theory at a time',
                         ['All four at the same time', 'None — reimage instead'],
                         'Testing one theory at a time means the result tells you something. Changing several things at once '
                         'leaves you unsure which one helped.', mc=[GUESS, RBFIRST])]),
            analogy('''<p>Think of a detective with four suspects.</p>
<p>She first collects the facts — who was where, what time, what was taken — before naming anyone. Then she tests one
suspect’s alibi at a time. Arresting everybody and letting them go one by one tells her nothing, and tidying the crime
scene over and over (a reboot loop) destroys the clues. The four suspects at logon are the profile, a network home
folder, the disk and Group Policy.</p>''',
                    L114 + ' (detective analogy written for this rung)',
                    [check('In the detective story, “tidying the crime scene over and over” matches what?',
                           'Rebooting the PC repeatedly',
                           ['Reading the GroupPolicy log', 'Checking which updates are pending'],
                           'Each reboot clears the running state you need, like tidying away clues. Reading logs and checking updates '
                           'are evidence gathering.', mc=[REBOOT, None])]),
            visual('''<ol class="ladder-trace">
<li>Inventory: model, Windows build, user, domain-joined ✔.</li>
<li>Updates: none pending ✔. Services: all running ✔.</li>
<li>Processes at sign-in: nothing unusual ✔.</li>
<li>One theory: the network home folder on a slow server. Test: sign in with home-folder redirection off for a test user.</li>
<li>Logon drops from 4 minutes to 35 seconds → theory confirmed.</li></ol>''',
                   L114 + ' (the order of work, as a worked trace written for this rung)',
                   [check('In the trace, what proved the home-folder theory?',
                          'Logon was fast with redirection off for a test user',
                          ['All the services were running at the time of sign-in', 'No updates were pending on the PC that day'],
                          'Changing one thing and seeing the logon drop to 35 seconds proves the theory. Running services and no '
                          'pending updates only ruled other ideas out.', mc=[GUESS, None])]),
            tryit('''<p>Put the order of work in sequence, then reveal what you would test first.</p>''',
                  L114,
                  [check('Which of these is one of the four slow-logon theories the lesson names?',
                         'A network home folder',
                         ['A dusty keyboard', 'A low screen brightness'],
                         'The lesson names profile, network home folder, disk and Group Policy as the candidates. Keyboard dust and '
                         'brightness do not affect sign-in time.', mc=[GUESS, None])],
                  widget=order('Order the work on a slow logon.',
                               ['Inventory the PC', 'Check updates', 'Check services', 'Check processes', 'Test one theory'],
                               'Evidence first, then a single theory.'))),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '11.1': {'start-here-software-problems-have-a-scope': '431cd65a24b7', 'core-content': '2bcdb1d3aa28', 'scope-first': 'cb50a83f75ef', 'teach-block-scope-before-repair': '7d7f23d2205a', 'more-windows-symptoms-no-os-found-shutdowns-services-usb-res': '317e273e1555'},
    '11.2': {'core-content': '4de76126594f', 'controls': '8826db2a46ad', 'profile-versus-machine': '4af84b2c2497'},
    '11.3': {'core-content': '1a81c1d3a2e1', 'repair-before-rebuild': 'ca3c5e70ba98', 'windows-tools-task-manager-and-the-management-consoles': 'ffeded8ab88c'},
    '11.4': {'core-content': 'a08191d1ff54', 'slow-logon': '4e08dc47fbf9'},
}
