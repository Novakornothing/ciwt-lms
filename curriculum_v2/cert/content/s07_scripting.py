"""A+ Core 2 4.8 — scripting basics (ITSUP 13.2)."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-script', 'Safe path for a support script',
    ['Write or obtain\n(trusted source)', 'Read it: what\ndoes it change?', 'Test on a lab VM\nor one pilot PC', 'Approve via\nchange control', 'Deploy, log,\nverify results'],
    'Five boxes in order. Write the script yourself or obtain it from a trusted source; read it line by line to see '
    'what it changes; test it on a lab virtual machine or a single pilot PC; get it approved through change control; then '
    'deploy it with logging and verify the results. A script run on many PCs repeats any mistake on every one of them.',
    'A script multiplies whatever it does — including mistakes — so test and approval come before deployment.', cols=5)

HTML = ('\n<p>A script is a text file of commands that an interpreter runs in order. Support teams script the jobs they do\noften, so the job is done the same way every time. Core 2 4.8 expects you to recognise the common file types, know what\nscripts are used for, and understand the risks.</p>\n<table class="ref-table"><thead><tr><th scope="col">Extension</th><th scope="col">Language / interpreter</th><th scope="col">Typical use</th></tr></thead><tbody>\n<tr><td><code>.bat</code></td><td>Windows batch file (cmd.exe)</td><td>Simple legacy logon and maintenance tasks</td></tr>\n<tr><td><code>.ps1</code></td><td>PowerShell script</td><td>Modern Windows administration; subject to the PowerShell <em>execution policy</em></td></tr>\n<tr><td><code>.vbs</code></td><td>VBScript (Windows Script Host)</td><td>Legacy Windows scripts; Microsoft has deprecated VBScript</td></tr>\n<tr><td><code>.sh</code></td><td>Shell script (bash or another shell)</td><td>Linux and macOS tasks; first line names the interpreter (<code>#!/bin/bash</code>), and the file must be executable</td></tr>\n<tr><td><code>.js</code></td><td>JavaScript</td><td>Web pages, Node.js tools, and (legacy) Windows Script Host</td></tr>\n<tr><td><code>.py</code></td><td>Python</td><td>Cross-platform automation and data handling</td></tr>\n</tbody></table>\n<h4>Use cases</h4>\n<ul>\n<li><strong>Basic automation</strong> of repeated tasks, on one PC or many.</li>\n<li><strong>Restarting machines</strong> — for example PowerShell <code>Restart-Computer</code> in a maintenance window.</li>\n<li><strong>Remapping network drives</strong> — <code>net use H: \\\\fs01\\home /persistent:yes</code> or PowerShell <code>New-PSDrive -Persist</code>.</li>\n<li><strong>Installing applications</strong> — a package manager such as <code>winget install</code>, or an <code>.msi</code> with <code>msiexec /i … /qn</code>.</li>\n<li><strong>Automated backups</strong> — a scheduled <code>robocopy</code> job, or <code>rsync</code> on Linux.</li>\n<li><strong>Gathering information</strong> — inventory with <code>Get-CimInstance Win32_OperatingSystem</code> or <code>systeminfo</code>.</li>\n<li><strong>Initiating updates</strong> — triggering an update scan or package upgrade instead of waiting for the schedule.</li>\n</ul>\n' + str(_FIG) + '\n<h4>Risks (“other considerations”)</h4>\n<p>The exam names three: <strong>unintentionally introducing malware</strong> (a script copied from a forum can download\nand run anything), <strong>inadvertently changing system settings</strong> (a wrong path or a missing condition repeats on\nevery PC it runs on), and <strong>browser or system crashes due to mishandling of resources</strong> (a loop that never ends,\nor a script that fills a disk or memory). PowerShell’s execution policy is a safety feature that helps stop scripts running\nunintentionally — Microsoft is explicit that it is not a security boundary — so the real controls are reading the script,\nrunning it from a trusted location, testing it, and putting it through change control.</p>\n' + str(worked('remapping a drive after a file-server move', '''<p>The H: drive moved from <code>\\\\fs01\\home</code> to <code>\\\\fs02\\home</code>. A two-line batch file does it:</p>
<pre><code>net use H: /delete /y
net use H: \\\\fs02\\home\\%USERNAME% /persistent:yes</code></pre>
<p>You run it on your own test account first, confirm H: opens the right folder, then submit it through change control
to run at logon for the affected group. The ticket records the script, the test result and the approval.</p>''')) + '\n' + str(scenario('the forum script', '''<p>A colleague finds a PowerShell “one-liner to speed up Windows” on a forum and wants to push it to every
PC. Reading it, you see it downloads a second script from a URL and runs it. You cannot know what that second script
will do tomorrow. You decline, explain the risk of introducing malware, and suggest raising the performance problem as a
change with a reviewed, in-house script tested on a pilot group.</p>''')) + '\n' + str(cfu(('Which extension is a PowerShell script, and what setting can stop it running?', '.ps1; the PowerShell execution policy.'),
     ('Name the three script risks Core 2 4.8 lists.', 'Unintentionally introducing malware; inadvertently changing system settings; crashes from mishandling resources.'),
     ('What does the first line #!/bin/bash in a .sh file do?', 'It tells the system which interpreter runs the script.'))) + '\n')

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 13, 'lesson': 2, 'id': 'cert-scripting',
    'title': 'Scripting basics: file types, use cases and risks',
    'cert': ['A2:4.8'],
    'html': sme_note('Scripting file types, use cases and risks (Core 2 4.8).') + HTML,
    'sources': ['ms-execpolicy', 'ms-psdrive', 'gnu-bash'],
}]

GLOSSARY = [
    ('Script', 'A text file of commands that an interpreter runs in sequence.'),
    ('Execution policy', 'PowerShell setting that controls when scripts may run; a safety feature, not a security boundary.'),
    ('Shebang', 'The first line of a Unix script (for example #!/bin/bash) naming the interpreter to run it.'),
]

ITEMS = [
    match('A2:4.8', 'IT-13.2', 1, 'Match each script file extension to its language.',
          [('.ps1', 'PowerShell'), ('.sh', 'Unix shell (bash)'), ('.vbs', 'VBScript'), ('.py', 'Python'), ('.bat', 'Windows batch (cmd)')],
          'Recognise the six Core 2 4.8 file types by extension.',
          decoys=['JavaScript']),
    multi('A2:4.8', 'IT-13.2', 2, 'Which THREE risks does the A+ objective list for running scripts? (Choose three.)',
          ['Unintentionally introducing malware', 'Inadvertently changing system settings', 'Crashes from mishandling resources'],
          ['Voiding the PC’s hardware warranty', 'Exceeding the software licence count', 'Lowering the display refresh rate'],
          'The objective’s three considerations are malware, unintended setting changes and resource-handling crashes.'),
    single('A2:4.8', 'IT-13.2', 3, 'A technician must map the same network drive for 200 users at logon. Which approach fits best?',
           'A tested logon script deployed to the user group',
           ['Visit every PC and map the drive by hand', 'Email users the UNC path and ask them to map it', 'Add the drive letter to each PC’s BIOS'],
           'Repeated, identical tasks across many users are the classic scripting use case — after testing and approval.'),
    order('A2:4.8', 'IT-13.2', 4, 'Put the steps for deploying a new maintenance script in a safe order.',
          ['Read the script and note what it changes', 'Test it on a lab VM or one pilot PC', 'Get approval through change control',
           'Deploy it with logging enabled', 'Verify the results on the target PCs'],
          'Review, test, approve, deploy with logging, verify.'),
    single('A2:4.8', 'IT-13.2', 5, 'A PowerShell script will not run on a Windows 11 PC, with a message that running scripts is disabled. What is the cause?',
           'The PowerShell execution policy',
           ['The script uses the .bat extension', 'Windows Defender Firewall', 'The user’s NTFS share permissions'],
           'On Windows client computers the default execution policy is Restricted, which prevents scripts from running.'),
]
