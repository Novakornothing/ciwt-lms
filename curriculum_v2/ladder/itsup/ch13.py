"""Explanation ladder — ITSUP chapter 13 (Windows command-line capstone). Pending SME review.

Every section of lessons 13.1-13.6 is laddered (refinement pass 20). CLIENT chapter 6 reuses this ladder (client/ch06.py).
"""
from curriculum_v2.ladder.itsup._lk import P, X
from curriculum_v2.ladder.schema import order, reveal, sort

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 13
_R = 'Pending SME review'


def _src(n, t):
    return f'Course lesson 13.{n} “{t}” (the original section), re-explained'


S1, S2, S3 = _src(1, 'The Lab Guest'), _src(2, 'Evidence from the Command Line'), _src(3, 'Lease Cycle')
S4, S5, S6 = _src(4, 'Name Resolution'), _src(5, 'Settings and Command Views'), _src(6, 'Before You Reboot')
PRIV, RULES, RENEW, FW = 'MC-IT13-EVIDENCE-PRIVATE', 'MC-IT13-LABS-BREAK-RULES', 'MC-IT13-RENEW-AS-REBOOT', 'MC-IT13-FIREWALL-OPTIONAL'
STATE, NETSH, BIG, CMD = 'MC-IT13-CHANGE-BEFORE-STATE', 'MC-IT13-NETSH-OTHER-DATA', 'MC-IT13-BIG-RESET-FIRST', 'MC-IT13-CMDLET-MIXUP'
VIEW, WHO, PURP, DOM = 'MC-C-IT13-STATE-VIEW', 'MC-C-IT13-WHOAMI-HOSTNAME', 'MC-R3-IT13-PURPOSE', 'MC-R3-IT13-LAB-DOMAIN'
APIPA, NAME, VER, NRS = 'MC-R5-IT13-APIPA-READ', 'MC-R5-IT13-NAME-PATH', 'MC-R5-IT13-VERIFY-RESOLVE', 'MC-R5-IT13-NETRESET-SCOPE'
PORT, REP, EXE = 'MC-R5-IT13-PORT-TEST', 'MC-R6-IT13-SCRIPT-REPEAT', 'MC-R6-IT13-EXEC-POLICY'
L_IP, L_DNS, L_DHCP, L_TRI = (('win-ipconfig', 'Read ipconfig /all on the lab guest and copy the evidence lines.'),
                              ('win-dns-break', 'Prove the IP path, fail the name, look up and flush.'),
                              ('win-dhcp-renew', 'Release and renew, then confirm the address and ping the gateway.'),
                              ('win-full-triage', 'Run the full triage: lease, gateway, IP, name, then one change.'))

MISCONCEPTIONS = {}

LESSONS = {
    '13.1': {
        'start-here-the-lab-guest-is-a-real-pc-for-this-course': X('Start here — the lab guest is a real PC for this course', 'IT-13.1', S1, [
            ('What do you do first on the Windows lab guest?', 'Take an inventory of it', 'Run diskpart clean to start fresh', 'Install a new browser and tools',
             'The lab guest is treated as a real PC: you inventory it before changing anything, and destructive commands are off limits.', RULES, STATE),
            ('What is this chapter mostly for?', 'Repetitions of Chapters 5 and 8', 'A whole new theory of networking', 'Optional reading for fast students',
             'Chapter 13 is practice of skills already taught, done on a real Windows guest so they become habits.', PURP, PURP),
            ('In the flight-simulator story, why treat the simulator seriously?', 'Habits carry over to the real plane', 'Simulators cost a lot of money to run', 'Instructors grade the seat belt',
             'What you practise in the simulator is what your hands do in the real cockpit, so sloppy sim habits become real mistakes.', RULES, None),
            ('Trace step 2 says write commands so a stranger can repeat them. Why?', 'The ticket must be repeatable by anyone', 'Strangers grade the lab reports at night', 'Short notes save disk space',
             'Exact command spelling lets another technician repeat the work and get the same evidence.', PRIV, None),
            ('Which command is never run on the lab guest?', 'diskpart clean', 'ipconfig /all', 'hostname',
             'diskpart clean wipes a disk; inventory commands like ipconfig and hostname only read state.', RULES, None),
        ],
            P('In this chapter you type real commands on a Windows computer that runs inside the lab. Treat it like a computer that belongs to '
              'someone. Start by writing down what it is and how it is set up. Never wipe its disk. Spell every command exactly, so another person '
              'could repeat your steps. Nothing here is new theory: it is practice of Chapters 5 and 8.'),
            P('Trainee pilots spend hours in a flight simulator. Crashing it hurts nobody, yet instructors still insist on every checklist, every '
              'radio call, every glance at the instruments. The reason is simple: whatever the trainee does in the simulator, their hands will do '
              'in the real aircraft. The lab guest is your simulator. If you skip the inventory or type careless commands here, that is what you '
              'will do on a user’s PC, where there is no reset button.'),
            ['Open the lab guest and note its name.', 'Run inventory commands and copy the exact output.', 'Make no destructive change.',
             'Practise the Chapter 5 and 8 commands as written.'],
            '<p>Sort the commands into safe inventory or never on the guest.</p>',
            sort('Inventory or never?', {'Inventory first': ['hostname', 'ipconfig /all', 'whoami'], 'Never on the guest': ['diskpart clean', 'format C:']},
                 'Inventory commands read state; destructive ones are never part of this lab.'), L_IP),
        'core-content': X('Core content', 'IT-13.1', S1, [
            ('What is a snapshot (Hyper-V checkpoint)?', 'A saved VM state you can return to', 'A screenshot of the VM desktop as a file', 'A backup of the host PC only',
             'A snapshot captures the whole virtual machine state so you can revert in seconds after a bad change.', STATE, None),
            ('Why practise network changes on a VM?', 'You can revert and harm nobody', 'VMs never have network faults', 'VMs run commands faster than PCs',
             'Breaking a guest is cheap because you revert; nobody’s real PC is affected and the next student starts clean.', RULES, None),
            ('In the save-game story, what is the save point?', 'The snapshot before the change', 'The final score shown at the very end', 'The game controller',
             'A save point lets you try something risky and go back, exactly like a snapshot before a change.', STATE, None),
            ('In the change loop, what comes right after the baseline inventory?', 'Make one change', 'Revert the snapshot', 'Close the ticket',
             'The loop is snapshot, inventory, one change, verify and record, then revert or keep.', STATE, BIG),
            ('Which habit carries over to a real PC with no snapshot?', 'Inventory first, one change at a time', 'Revert whenever something breaks, skip notes', 'Skip notes because you can undo',
             'Real PCs have no revert button, so the inventory-first, one-change habit is what protects users.', STATE, RULES),
        ],
            P('A virtual machine is a whole computer running as software on another computer. Tools like Hyper-V and VirtualBox can save its '
              'state at a moment in time, called a snapshot or checkpoint. If a change goes wrong, you jump back to that moment. That makes it the '
              'safe place to practise. Still, follow the loop: save, inventory, change one thing, check and record, then go back or keep.'),
            P('In a video game you save before the boss fight. If it goes badly you reload and try again with a different plan, and nothing in '
              'the rest of the game is lost. But a good player still learns from each attempt rather than mashing buttons. The snapshot is your '
              'save point. The inventory, one change and recorded result are the learning. On a user’s real PC there is no reload, so the learning '
              'habit is what you keep.'),
            ['Take a snapshot or checkpoint.', 'Collect a baseline inventory.', 'Make one change.', 'Verify and record action → result.',
             'Revert to the snapshot, or keep the change.'],
            '<p>Put the lab change loop in order.</p>',
            order('Lab change loop', ['Snapshot', 'Baseline inventory', 'One change', 'Verify and record', 'Revert or keep'],
                  'Save first, look second, change one thing, prove it, then decide.'), ('virt-vm', 'Take a checkpoint, change one setting, verify, revert.')),
        'this-guest-is-shop-property': X('This guest is shop property', 'IT-13.1', S1, [
            ('How should you treat CIWT-W11-07?', 'Like a shared bench PC', 'Like a throwaway sandbox', 'Like your personal laptop',
             'Others use the same guest, so you inventory first and never run destructive commands.', RULES, RULES),
            ('What comes before any change to the lab VM?', 'An inventory', 'A disk clean', 'A reboot',
             'Inventory shows the starting state so you can prove what you changed.', STATE, STATE),
            ('In the library-book story, why not write in the margins?', 'The next reader needs it clean', 'Pencils are not allowed inside', 'Books are cheap to replace',
             'Shared property is left as you found it, just like the lab guest.', RULES, None),
            ('Trace step 3 forbids which action?', 'diskpart clean', 'hostname', 'ipconfig /all',
             'Cleaning a disk destroys the guest for everyone else.', RULES, None),
            ('Why does treating the guest as shop property matter later?', 'It builds habits for user PCs', 'It speeds up the lab scoring', 'It makes snapshots unnecessary',
             'The respect you show the guest becomes how you handle real users’ machines.', RULES, None),
        ],
            P('The lab computer is not yours to break. Other students and instructors use it too. Before you change anything, write down how it '
              'is set up. Never wipe its disk. Think of CIWT-W11-07 as a repair-bench PC that a colleague will sit at after you, and leave it in a '
              'state they can work with.'),
            P('A library book passes through hundreds of hands. The good reader returns it without notes in the margins, folded corners or coffee '
              'rings, because the next person deserves the same book. Nobody checks every page, so it relies on habit. The lab guest is a library '
              'book. Taking an inventory first, avoiding destructive commands and leaving it tidy is the habit you will need on users’ PCs, '
              'where far more is at stake than a stained page.'),
            ['Sign in to CIWT-W11-07.', 'Run the inventory and save it.', 'Never run diskpart clean or format.', 'Change one thing at a time and note it.'],
            '<p>Write your two-line inventory note for the guest.</p>',
            reveal('What two lines open every lab note?', '“CIWT-W11-07, Windows 11 Pro, user lab\\student” then “ipconfig /all: Ethernet 10.20.30.41, gw 10.20.30.1, DNS 10.20.30.5.”'), L_IP),
    },
    '13.2': {
        'core-content': X('Core content', 'IT-13.1', S2, [
            ('ipconfig /all shows 169.254.12.7. What does that mean?', 'No DHCP server answered', 'The network cable is unplugged', 'DNS is broken',
             'A 169.254 address is APIPA: the PC asked for an address and nobody answered. Link may be fine.', APIPA, APIPA),
            ('Default Gateway is blank. What can the PC reach?', 'Only its own subnet', 'Everything on the internet', 'Only DNS servers',
             'Without a gateway the PC cannot route to other networks.', NAME, None),
            ('In the passport story, why read every field?', 'Each field answers a different question', 'Officers like long, slow checks at the desk', 'The photo is enough',
             'Each line of ipconfig /all answers one question: link, address source, address, gateway, DNS, lease.', APIPA, None),
            ('Which PowerShell cmdlet shows the same IP facts?', 'Get-NetIPConfiguration', 'Restart-NetAdapter -Name Ethernet', 'Clear-DnsClientCache',
             'Get-NetIPConfiguration only reads; the others change state.', CMD, VIEW),
            ('Media State says “Media disconnected.” What do you check?', 'Cable, port, Wi-Fi or VM adapter', 'The DNS server list and suffix', 'The DHCP lease time',
             'Disconnected media is a link problem, before any address question.', APIPA, None),
        ],
            P('Almost every network ticket starts with ipconfig /all. It tells you what the computer believes about each network card. Read the '
              'card that should be connected from top to bottom: is there a link, is the address automatic, what address is it, is there a router, '
              'who answers names, and when did the address arrive? A 169.254 address means nobody handed one out. PowerShell gives the same facts '
              'with Get-NetIPConfiguration.'),
            P('A border officer checking a passport does not glance at the photo and wave you through. They look at the name, the date of birth, '
              'the expiry date, the issuing country and the stamps, because each field can reveal a different problem. ipconfig /all is the '
              'network passport of a PC. Media state, DHCP, address, gateway, DNS and lease times each answer a separate question, and a problem can '
              'hide in any one of them.'),
            ['Media State: link or “disconnected”?', 'DHCP Enabled: should it be Yes?', 'IPv4: 169.254 means no DHCP answer.',
             'Default Gateway: blank means own subnet only.', 'DNS Servers: expected addresses?', 'Lease times: recent?'],
            '<p>Match each warning sign to what it means.</p>',
            sort('Warning signs', {'No DHCP answer': ['169.254.x.x address'], 'Link problem': ['Media disconnected'],
                                   'Cannot leave subnet': ['Blank default gateway'], 'Name problem likely': ['Unexpected DNS server']},
                 'Each field points to a different layer.'), L_IP),
        'evidence-lines': X('Evidence lines', 'IT-13.1', S2, [
            ('Which outputs go into the ticket as evidence?', 'hostname and ipconfig /all', 'A screenshot of the desktop', 'Your memory of the screen',
             'Exact command output is evidence a stranger can trust and compare.', PRIV, PRIV),
            ('Get-NetIPConfiguration compared with ipconfig /all is…', 'The same facts, different spelling', 'A completely different set of data', 'Only for servers',
             'Both read the same configuration; one is PowerShell, one is classic.', NETSH, CMD),
            ('In the receipt story, why keep the receipt?', 'It proves what happened', 'Receipts look tidy in a wallet', 'Shops require them',
             'Command output is the receipt for your diagnosis.', PRIV, None),
            ('Trace step 3 pastes output where?', 'Into the ticket', 'Into a private file', 'Nowhere',
             'Keeping output out of the ticket hides the evidence from the next person.', PRIV, None),
            ('Which identity command shows the signed-in user?', 'whoami', 'hostname', 'ipconfig',
             'whoami shows the account; hostname shows the computer name.', WHO, WHO),
        ],
            P('Two outputs always go in the ticket: hostname, which names the computer, and ipconfig /all, which shows its network settings. If '
              'you prefer PowerShell, Get-NetIPConfiguration gives the same information in a different layout. Paste the real text, not a summary '
              'from memory, so the next person sees exactly what you saw.'),
            P('When you return something to a shop, the receipt settles every argument: what you bought, when, and for how much. Without it, it is '
              'your word against theirs. Command output is the receipt for a diagnosis. “The network looked fine” is your word. The pasted lines of '
              'hostname and ipconfig /all are the receipt, and anyone can read them later and agree on what the PC actually said.'),
            ['Run hostname.', 'Run ipconfig /all (or Get-NetIPConfiguration).', 'Paste both outputs into the ticket.', 'Add one line saying what they show.'],
            '<p>Write the evidence block you would paste for a PC with an APIPA address.</p>',
            reveal('Evidence block for an APIPA PC?', '“hostname: CIWT-W11-07. ipconfig /all: Ethernet up, DHCP Yes, IPv4 169.254.12.7, gateway blank → no DHCP answer.”'), L_IP),
        'scripting-basics-file-types-use-cases-and-risks': X('Scripting basics: file types, use cases and risks', 'IT-13.2', S2, [
            ('Which extension is a PowerShell script?', '.ps1', '.bat', '.vbs',
             '.ps1 is PowerShell; .bat is batch for cmd.exe; .vbs is deprecated VBScript.', EXE, None),
            ('Why do support teams script repeated jobs?', 'So the job is done the same way every time', 'So nobody has to understand the job at all', 'Because scripts never fail',
             'Scripts make repeated work consistent and fast across many PCs.', REP, REP),
            ('In the recipe-card story, what is the danger of a stranger’s card?', 'It may contain harmful steps', 'It uses metric units instead of cups', 'It is too short',
             'Running an unknown script can do harm, just like following an untrusted recipe.', EXE, None),
            ('A .ps1 will not run on a managed PC. What is a likely reason?', 'The execution policy blocks it', 'The firewall blocks all text files', 'The extension is wrong for PowerShell',
             'PowerShell’s execution policy decides which scripts may run.', EXE, EXE),
            ('What must a .sh script have to run directly on Linux?', 'An interpreter line and execute permission', 'A .exe extension added to the file name', 'Administrator rights in Windows',
             'The #! line names the interpreter and the file must be executable.', EXE, None),
        ],
            P('A script is a text file full of commands that run one after another. Teams write scripts for jobs they repeat, like restarting PCs '
              'in a maintenance window or mapping drives, so the job is identical every time. Know the common types: .bat, .ps1, .vbs, .sh, .js '
              'and .py. Scripts carry risk too: a bad or untrusted script can break many machines at once, so test them and run only approved ones.'),
            P('A recipe card lets anyone bake the same cake without thinking: follow the steps and it comes out right every time. That is why '
              'kitchens use them. But a card handed to you by a stranger might say “add a cup of salt,” and following it blindly ruins every cake '
              'in the batch. Scripts are recipe cards for computers: brilliant for consistency, dangerous when untested or untrusted, and they can '
              'spoil a hundred PCs as fast as they fix them.'),
            ['Identify the type: .bat, .ps1, .vbs, .sh, .js, .py.', 'Check the source: approved and reviewed?', 'Test on one lab machine.',
             'Run in the maintenance window.', 'Verify and record the result.'],
            '<p>Sort each file into its interpreter.</p>',
            sort('Script types', {'Windows': ['.bat', '.ps1', '.vbs'], 'Linux / macOS': ['.sh'], 'Cross-platform': ['.py', '.js']},
                 'The extension tells you which interpreter runs it.'), ('linux-vm-script', 'Write a small shell script, make it executable and run it.')),
    },
    '13.3': {
        'core-content': X('Core content', 'IT-13.4', S3, [
            ('Which is the lowest rung of the network-reset ladder?', 'Release and renew the lease', 'A full network reset in Settings', 'netsh winsock reset',
             'You start with the least disruptive fix and record the result before moving up.', BIG, BIG),
            ('What does a full Network reset in Settings do?', 'Reinstalls adapters and restores defaults', 'Only renews the DHCP lease on Ethernet', 'Clears the browser cache',
             'It removes and reinstalls every adapter, so Wi-Fi passwords and static settings may need re-entering.', NRS, NRS),
            ('In the doctor story, why start with rest and fluids?', 'Least harm first', 'Surgery is boring', 'Doctors are cautious by law',
             'Like medicine, you escalate treatment only when the gentler one fails.', BIG, None),
            ('Rung 2 restarts the adapter. Which cmdlet does that?', 'Restart-NetAdapter -Name Ethernet', 'Disable-NetAdapter -Name Ethernet', 'Get-NetAdapter -Name Ethernet',
             'Restart-NetAdapter resets the link; Get- only reads and Resolve-DnsName looks up names.', CMD, CMD),
            ('What must you do after each rung?', 'Record the result', 'Jump to the top rung', 'Reboot twice',
             'Recording each result tells you whether to stop or climb.', BIG, None),
        ],
            P('Network fixes range from gentle to drastic. Gentle: ask for a fresh address. Next: restart the network card. Stronger: reset the '
              'network stack with netsh. Most drastic: the Network reset button in Settings, which reinstalls every network card and makes the PC '
              'restart. Go one step at a time and write down what happened before trying a stronger one, because each step up undoes more.'),
            P('A good doctor treating a cough does not start with surgery. First rest and fluids, then a mild medicine, then stronger drugs, and '
              'only then a specialist and an operation. Each step has more side effects and takes longer to recover from, so the doctor checks the '
              'result before going further. Network fixes are the same: renewing the lease is rest and fluids, the Settings network reset is surgery.'),
            ['Rung 1: ipconfig /release then /renew.', 'Rung 2: Restart-NetAdapter (admin).', 'Rung 3: netsh winsock reset and netsh int ip reset, restart.',
             'Rung 4: Settings → Network reset, user warned.', 'Record the result after every rung.'],
            '<p>Put the reset rungs in order from gentlest to most drastic.</p>',
            order('Reset ladder', ['Renew lease', 'Restart adapter', 'Reset stack with netsh', 'Settings network reset'],
                  'Each rung undoes more, so climb only when the one below fails.'), L_DHCP),
        'lease-cycle': X('Lease cycle', 'IT-13.2', S3, [
            ('When is release/renew the right tool?', 'For a lease problem', 'As a general reboot reflex', 'For a printer jam',
             'Release and renew tests and fixes the DHCP lease, not every fault.', RENEW, RENEW),
            ('After renewing, what do you confirm?', 'New address and gateway ping', 'Only that the command ran without error', 'The desktop wallpaper',
             'Confirm a valid address appeared and the gateway answers.', VER, None),
            ('In the library-card story, why renew the card?', 'It expired, not the library', 'The library moved to a new building', 'Cards look nicer new',
             'Renewal fixes an expired lease, not other problems.', RENEW, None),
            ('Trace step 3 pings what?', 'The default gateway', 'A random website on the internet', 'The PC itself only',
             'Pinging the gateway proves the new lease actually works on the network.', VER, None),
            ('Renew fails and you still get 169.254. Next?', 'Check link and DHCP server', 'Renew ten more times in a row', 'Full network reset now',
             'Repeating renew is guessing; check the link and the DHCP server path.', RENEW, BIG),
        ],
            P('Releasing and renewing hands back the computer’s address and asks for a new one. Use it when the address is the problem, for '
              'example a 169.254 address or a wrong range after moving networks. It is not a general “turn it off and on” fix. Afterwards, check '
              'the new address and ping the router to prove it works.'),
            P('If your library card expires, renewing it at the desk gets you borrowing again in a minute. But if the book you want is missing '
              'from the shelf, renewing your card ten times will not make it appear. Release and renew is the card renewal: perfect for an expired '
              'or wrong lease, pointless for a problem somewhere else. And after renewing, you check that you really can borrow, by pinging the gateway.'),
            ['ipconfig /release.', 'ipconfig /renew.', 'ipconfig /all: new valid address?', 'ping the default gateway.', 'Record action → result.'],
            '<p>Run the renew lab and record each result.</p>',
            order('Lease cycle', ['Release', 'Renew', 'Read the new address', 'Ping the gateway', 'Record'], 'Renew, then prove it works.'), L_DHCP),
    },
    '13.4': {
        'core-content': X('Core content', 'IT-13.2', S4, [
            ('You can reach 8.8.8.8 but not www.example.com. Where is the fault?', 'Name resolution', 'The default gateway', 'The network cable',
             'Reaching an address proves routing works, so the failure is in turning names into addresses.', NAME, NAME),
            ('Which cmdlet tests a server name?', 'Resolve-DnsName', 'Restart-NetAdapter -Name Ethernet', 'Get-NetAdapter',
             'Resolve-DnsName looks up the name; the others manage or read the adapter.', CMD, CMD),
            ('In the phone-book story, what does a wrong phone book stand for?', 'A bad DNS server or hosts entry', 'A broken phone line in the street', 'A flat battery',
             'You can still dial numbers; only looking up names is broken.', NAME, None),
            ('In the decision path, what comes before testing by IP?', 'Reach the gateway', 'Resolve the name', 'Compare hosts file',
             'Lease, gateway, IP, then name: each step rules out a layer.', NAME, None),
            ('IP works, name fails. What do you compare?', 'DNS servers and the hosts file', 'The cable and the switch port lights', 'The DHCP lease times',
             'Name failures come from the resolver settings or a hosts entry.', NAME, NAME),
        ],
            P('When users say “the internet is down,” often only names are failing. Separate the two. If you can reach a known address but not a '
              'name, the path works and name lookup is broken. If you cannot reach the address either, check the lease, router and link first. '
              'Use ipconfig /all, ping the gateway, Test-NetConnection to an address, then Resolve-DnsName.'),
            P('Imagine your phone’s contacts app is broken but the phone itself works. You cannot call “Mum” by name, yet if you type her number '
              'directly, it rings. Nobody would replace the phone line. DNS is the contacts app of the network. If typing the address works but the '
              'name does not, the lines are fine and the lookup is broken: a wrong DNS server, or a bad entry in the hosts file.'),
            ['Valid lease? ipconfig /all.', 'Reach gateway? ping it.', 'Reach a server by IP? Test-NetConnection.', 'Name resolves? Resolve-DnsName.',
             'IP works, name fails → compare DNS servers and hosts file.'],
            '<p>Order the IP-versus-name decision path.</p>',
            order('IP versus name', ['Check lease', 'Ping gateway', 'Test by IP', 'Resolve the name', 'Compare DNS and hosts'],
                  'Each test only makes sense once the layer below works.'), L_DNS),
        'broken-name-resolution': X('Broken name resolution', 'IT-13.2', S4, [
            ('What is the order for this fault?', 'Prove IP, fail name, nslookup, flush', 'Flush first, then think about the cause', 'Reset the stack, then test',
             'Evidence first: show the IP path works and the name fails, then look up and only then flush.', NAME, BIG),
            ('Should the firewall be off during this lab?', 'No; firewall stays on', 'Yes; it blocks DNS replies in the lab', 'Yes; to save time',
             'The pass bar requires the firewall on; turning it off hides the real fault and is unsafe.', FW, FW),
            ('In the detective story, why gather clues before arresting?', 'Evidence before action', 'Arrests take a long time', 'Clues are optional',
             'Proving the fault first stops you fixing the wrong thing.', NAME, None),
            ('After flushing, what do you do?', 'Resolve the name again to verify', 'Close the ticket straight away as fixed', 'Reset the network stack',
             'Verification proves the flush worked.', VER, VER),
            ('Which pass bar does this lab share?', 'The same as 5.5', 'A new, easier one', 'No pass bar at all',
             'It repeats the Chapter 5.5 standard.', PURP, None),
        ],
            P('For a name problem, follow the same order every time. First show that reaching an address works. Then show that the name fails. '
              'Then look it up with nslookup to see which server answers. Only then flush the DNS cache, and test the name again. Keep the firewall '
              'on the whole time. The pass bar is the same as lesson 5.5.'),
            P('A detective does not arrest the first person they see. They collect fingerprints, check alibis, and only then make an arrest, and '
              'afterwards they make sure the case holds up in court. Flushing DNS is the arrest. Proving the IP path works and the name fails is the '
              'evidence, nslookup is checking the alibi, and resolving the name again afterwards is the court case that proves you got it right.'),
            ['Test-NetConnection to a known IP: works.', 'Resolve-DnsName the server name: fails.', 'nslookup: which server answers?',
             'ipconfig /flushdns.', 'Resolve the name again; firewall still on.'],
            '<p>Run the DNS-break lab in this order.</p>',
            order('Name fault order', ['Prove IP', 'Fail name', 'nslookup', 'Flush', 'Verify'], 'Evidence, look-up, one change, verify.'), L_DNS),
        'teach-block-name-resolution-gym': X('Teach block — name resolution gym', 'IT-13.2', S4, [
            ('Which labs fill the gym period?', 'win-dns-break and win-full-triage', 'A hardware memory reseat lab and quiz', 'A Settings-only quiz',
             'The gym is name resolution reps; other domains belong elsewhere.', DOM, DOM),
            ('What is this teach block?', 'Practice reps, not new theory', 'A lecture on the history of DNS', 'A free period',
             'It repeats skills until they are automatic.', PURP, PURP),
            ('In the gym story, why repeat the same lift?', 'Repetition builds strength', 'Gyms have very few machines', 'Coaches enjoy counting',
             'Reps turn a known move into a reliable habit.', PURP, None),
            ('In the trace, how long do you give it?', 'A full period', 'Five minutes at the end', 'Only if time is left',
             'The block deserves a full period of practice.', PURP, None),
            ('Which pass bar applies?', 'The same as 5.5', 'Any score passes', 'No checks at all',
             'Gym reps use the 5.5 standard.', PURP, None),
        ],
            P('This block is a full class period of practice on two labs: win-dns-break and win-full-triage. There is no new theory. Students '
              'repeat the name-resolution process until it is automatic, and they are held to the same pass bar as lesson 5.5. Give it the full '
              'time, because skills that are not practised fade.'),
            P('Nobody gets strong by reading about squats. You go to the gym and do the same lift, set after set, week after week, until the '
              'movement is smooth and the weight feels lighter. The coach does not invent a new exercise each session; they add reps. This teach '
              'block is the gym. win-dns-break and win-full-triage are the lifts, and the reps are what make the process stick.'),
            ['Open win-dns-break; run it to the 5.5 bar.', 'Open win-full-triage; run it to the 5.5 bar.', 'Repeat any failed run cleanly.',
             'Use the full period.'],
            '<p>Run both gym labs and record each attempt.</p>',
            sort('In the gym or not?', {'Gym lab': ['win-dns-break', 'win-full-triage'], 'Another domain': ['Memory reseat', 'Printer driver']},
                 'Gym time is name-resolution reps.'), L_TRI),
    },
    '13.5': {
        'core-content': X('Core content', 'IT-13.3', S5, [
            ('Settings and the command line disagree. What does it mean?', 'Something is changing underneath', 'One of them is always wrong, ignore it', 'Windows needs reinstalling',
             'A VPN, policy or second adapter can cause the views to differ; the disagreement is evidence.', VIEW, NETSH),
            ('Which command shows the Wi-Fi network and signal?', 'netsh wlan show interfaces', 'netsh wlan show profiles', 'ipconfig /all',
             'netsh wlan show interfaces reads Wi-Fi state; the others show updates or version.', CMD, CMD),
            ('In the map-and-satnav story, why use both?', 'Each confirms the other', 'Maps are always outdated', 'Satnav is illegal',
             'Two views of the same state let you guide a user and still collect exact evidence.', VIEW, None),
            ('Where do you find Services, Event Viewer, Device Manager?', 'MMC snap-ins via Run', 'Settings → System → About', 'Windows Update',
             'Some tools still live in MMC snap-ins such as services.msc and eventvwr.msc.', VIEW, None),
            ('Which pair reads accounts on the PC?', 'whoami and Get-LocalUser', 'hostname and systeminfo', 'net share and net use',
             'whoami shows you; Get-LocalUser lists local accounts.', WHO, WHO),
        ],
            P('Windows shows the same settings in two places: the Settings app and the command line. Over the phone you can guide a user through '
              'Settings, while you copy exact command output into the ticket. Knowing both helps. If they disagree, something like a VPN, a policy '
              'or a second network card is changing things, and that is a clue. Some tools still live in MMC snap-ins like services.msc.'),
            P('On a road trip you might use a paper map and a satnav together. The map is easy to point at with a passenger; the satnav gives the '
              'exact distance. Usually they agree. If they suddenly disagree, it is worth stopping: maybe a road has closed or you took a turn you '
              'did not notice. Settings is the map you share with the user; commands are the satnav for the ticket. A disagreement is a road closure.'),
            ['Device facts: System → About and hostname / winver.', 'IP and DNS: Network & internet and ipconfig /all.', 'Wi-Fi: Settings Wi-Fi and netsh wlan show interfaces.',
             'Updates: Update history and Get-HotFix.', 'Accounts: Your info and whoami / Get-LocalUser.'],
            '<p>Match each fact to its command view.</p>',
            sort('Command views', {'Device name / version': ['hostname', 'winver'], 'IP and DNS': ['ipconfig /all'], 'Updates': ['Get-HotFix'],
                                   'Accounts': ['Get-LocalUser']},
                 'Every Settings page has a command twin.'), L_IP),
        'settings-gym': X('Settings gym', 'IT-13.3', S5, [
            ('Which five paths does the gym drill?', 'About, Ethernet, Update, Accounts, Services', 'Paint, Calculator, Notepad, Edge, Store', 'BIOS, POST, RAID, PXE, UEFI',
             'These are the paths you guide users to most often.', VIEW, DOM),
            ('What is the goal of the gym?', 'Find each path without a forum screenshot', 'Memorise every registry key by heart', 'Change every setting once',
             'You should navigate confidently on your own.', VIEW, STATE),
            ('In the taxi-driver story, why learn streets by heart?', 'To guide without a map', 'Taxis have no satnav fitted', 'Exams require it',
             'Knowing the paths lets you guide users smoothly over the phone.', VIEW, None),
            ('In the trace, Services is opened how?', 'services.msc', 'Settings → System → About', 'Windows Update',
             'Services is an MMC snap-in, not a Settings page.', VIEW, None),
            ('Should you change settings while practising the paths?', 'No; just find and read', 'Yes; change each one', 'Yes; reset all to default',
             'The gym is about navigation and reading state, not changing it.', STATE, VIEW),
        ],
            P('Practise finding five places until you can do it from memory: About, Ethernet, Windows Update, Accounts and Services. You should '
              'not need to search online for screenshots. Look and read, but do not change anything; the point is fast, confident navigation that '
              'you can talk a user through on the phone.'),
            P('London taxi drivers spend years learning “The Knowledge,” every street by heart, so they can drive without looking at a map and '
              'answer any passenger instantly. They are fast because they never have to stop and search. Your Settings gym is a small version: five '
              'routes learned so well that you can guide a nervous user on the phone, step by step, without hunting for a forum screenshot.'),
            ['Settings → System → About.', 'Settings → Network & internet → Ethernet.', 'Settings → Windows Update.', 'Settings → Accounts.', 'Run → services.msc.'],
            '<p>Order the five gym stops as you would walk a user through them.</p>',
            order('Settings gym', ['About', 'Ethernet', 'Windows Update', 'Accounts', 'Services'], 'Five paths you can reach from memory.'), L_IP),
        'windows-settings-control-panel-applets-and-settings-pages': X('Windows settings: Control Panel applets and Settings pages', 'IT-13.3', S5, [
            ('Where do you create a new Outlook (classic) profile?', 'Control Panel → Mail', 'Settings → System → About', 'Device Manager',
             'The Mail applet manages classic Outlook profiles.', VIEW, None),
            ('Why turn off “Hide extensions for known file types”?', 'So invoice.pdf.exe is visible', 'To speed up File Explorer windows', 'To save disk space',
             'Showing extensions reveals disguised executables.', VIEW, None),
            ('In the old-house story, why keep the old fuse box?', 'Some controls still live there', 'Fuse boxes look nice and old-fashioned', 'It is cheaper',
             'Control Panel still holds applets that Settings has not replaced.', VIEW, None),
            ('Search misses files. Which applet helps?', 'Indexing Options', 'Sound', 'Internet Options',
             'Indexing Options chooses locations and rebuilds the index.', VIEW, None),
            ('Allow an app through the firewall from where?', 'Windows Defender Firewall applet', 'Programs and Features list', 'User Account Control settings',
             'The firewall applet allows apps and opens advanced rules.', FW, None),
        ],
            P('A+ Core 2 objective 1.6 expects you to use both the Settings app and Control Panel. Control Panel still holds useful applets: '
              'Internet Options, Devices and Printers, Programs and Features, Network and Sharing Center, Windows Defender Firewall, Mail, Sound, '
              'User Accounts, Indexing Options and File Explorer Options. Know which job each one does.'),
            P('In an old house that has been partly renovated, the new kitchen has smart switches, but the fuse box, the water stopcock and the '
              'boiler controls are still in the cellar. A good plumber knows both the shiny new panel and the old cellar. Windows is that house. '
              'Settings is the renovated kitchen; Control Panel is the cellar where Mail profiles, Indexing Options and firewall rules still live.'),
            ['Corrupt Outlook profile → Mail.', 'Search misses files → Indexing Options.', 'Disguised file → File Explorer Options, show extensions.',
             'App blocked → Windows Defender Firewall.', 'Uninstall or repair → Programs and Features.'],
            '<p>Match each job to its applet.</p>',
            sort('Applets', {'Mail': ['New Outlook profile'], 'Indexing Options': ['Rebuild search index'], 'File Explorer Options': ['Show file extensions'],
                             'Programs and Features': ['Repair a desktop program']},
                 'Each applet owns one family of jobs.'), L_IP),
    },
    '13.6': {
        'core-content': X('Core content', 'IT-13.3', S6, [
            ('Why record processes before a restart?', 'A restart clears the evidence', 'Restarts are always harmful to Windows', 'It speeds up the reboot',
             'Once the PC restarts, the running state and errors are gone.', STATE, STATE),
            ('What does taskkill /PID 4312 /F do?', 'Forces that process to end', 'Lists services in that process', 'Restarts the whole PC',
             '/F forces the end; unsaved work can be lost, so ask the user to save first.', VIEW, None),
            ('In the crime-scene photo story, why photograph first?', 'Moving things destroys evidence', 'Photos are cheap to take now', 'Police like albums',
             'Record the state before you change it, like a scene photo.', STATE, None),
            ('netsh interface ipv4 show config disagrees with ipconfig. Likely cause?', 'You are reading a different interface', 'netsh reads a cached, older copy of the data', 'The PC needs a restart to sync',
             'netsh shows the same lease; a mismatch usually means a VPN or virtual adapter.', NETSH, NETSH),
            ('Why can ending one svchost.exe be risky?', 'It may host several services', 'It is a virus by default on most PCs', 'It deletes user files',
             'tasklist /svc shows several services inside one svchost process.', VIEW, None),
        ],
            P('Restarting a PC wipes out what was happening. Before you end a task or reboot, write down what is running. tasklist /svc shows each '
              'process and the services inside it. Get-Process sorted by CPU shows the busiest. If you must end something, target its PID with '
              'taskkill and ask the user to save first. netsh interface ipv4 show config should match ipconfig /all; if not, check which interface.'),
            P('At a crime scene, the first officer does not tidy up. They photograph everything exactly as it is, because once a glass is moved or '
              'a door is closed, that clue is gone forever. A restart is tidying up the scene. tasklist, Get-Process and netsh are your camera. '
              'Take the photos first; then, if you must, end one process by its PID or reboot, and write down why.'),
            ['tasklist /svc: record processes and services.', 'Get-Process | sort CPU: top five.', 'netsh interface ipv4 show config: matches ipconfig?',
             'Ask the user to save; taskkill /PID if needed.', 'Restart only with a named reason.'],
            '<p>Order your steps before a restart.</p>',
            order('Before restart', ['Record processes', 'Check top CPU', 'Compare netsh with ipconfig', 'Ask user to save', 'Restart with a reason'],
                  'Evidence first, then the change.'), L_TRI),
        'before-you-reboot': X('Before you reboot', 'IT-13.3', S6, [
            ('What is a reboot, according to this section?', 'A change you can name', 'A harmless reflex to try first', 'Not worth recording',
             'A reboot changes state and clears evidence, so it is recorded with a reason.', STATE, STATE),
            ('netsh shows what, compared with ipconfig?', 'The same lease, another view', 'A different network entirely', 'Only Wi-Fi passwords',
             'netsh is another view of the same lease data.', NETSH, NETSH),
            ('In the game-reset story, why note the score before resetting?', 'Otherwise it is lost', 'Scores are decorative', 'Resets are illegal',
             'Recording state before a reset keeps evidence.', STATE, None),
            ('Trace step 1 is…', 'List processes', 'Reboot', 'Close the ticket',
             'Listing processes captures the evidence first.', STATE, None),
            ('Which ticket line names the reboot well?', '“Rebooted 1410: pending update”', '“Rebooted, all good now, closing”', '“Turned it off and on”',
             'A named reason and time make the reboot a recorded change.', STATE, None),
        ],
            P('Three short rules. List the processes first, so you have evidence. Remember that netsh only shows the same address details as '
              'ipconfig, from another angle. And treat a reboot as a change: write down when you did it and why, the same as any other change.'),
            P('Before resetting a pinball machine you might jot down your score and which lights were on, because after the reset it all goes '
              'dark and nobody will believe you. A PC reboot is that reset. The process list is the score, netsh is a second photo of the same board, '
              'and the reboot itself is a named move in your ticket: time, reason, result.'),
            ['List processes (tasklist /svc).', 'Compare netsh with ipconfig.', 'Write the reboot reason and time.', 'Reboot, then verify.'],
            '<p>Write the ticket line for a reboot.</p>',
            reveal('Ticket line for a reboot after an update?', '“1410 tasklist saved; netsh and ipconfig agree. Rebooted for pending KB update. After: Outlook opens, mail sends.”'), L_TRI),
    },
}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '13.1': {'start-here-the-lab-guest-is-a-real-pc-for-this-course': '4371f2c27ea3', 'core-content': 'fe52e8648481', 'this-guest-is-shop-property': '51dd02644fca'},
    '13.2': {'core-content': '809c8aa153f2', 'evidence-lines': 'cb6c3cad173a', 'scripting-basics-file-types-use-cases-and-risks': '025f5dd1c602'},
    '13.3': {'core-content': '15f5c952deb9', 'lease-cycle': '812cee6f318c'},
    '13.4': {'core-content': 'cf34c92a5acf', 'broken-name-resolution': '51d5add7e6f1', 'teach-block-name-resolution-gym': 'abd85495aba5'},
    '13.5': {'core-content': 'd0ff25e6db5d', 'settings-gym': '962af21f09bf', 'windows-settings-control-panel-applets-and-settings-pages': '36d16458d712'},
    '13.6': {'core-content': '1d81c9e9ca93', 'before-you-reboot': '492bb3ee6eab'},
}
