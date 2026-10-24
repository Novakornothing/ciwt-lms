"""Explanation ladder — ITSUP chapter 12 (Operational Procedures & Capstone Habits). Pending SME review.

Author B (labs branch, pass 19). Every section of lessons 12.1-12.4 is laddered, including the start-here, depth and
teach blocks. CLIENT chapter 5 holds the same lessons and reuses this ladder (curriculum_v2/ladder/client/ch05.py).
"""
from curriculum_v2.ladder.schema import (analogy, check, order, plain, reveal, same_as, section, skip, sort,
                                         tryit, visual)

SCHEMA = 1
COURSE = 'ITSUP'
CHAPTER = 12

L121 = 'Course lesson 12.1 “Change Control and Checklists” (the original section), re-explained'
L122 = 'Course lesson 12.2 “Privacy and Policy” (the original section), re-explained'
L123 = 'Course lesson 12.3 “Recovery Awareness” (the original section), re-explained'
L124 = 'Course lesson 12.4 “Integrated Capstone” (the original section), re-explained'
ITIL = 'ITIL 4 — Change enablement practice guide (PeopleCert/AXELOS); NIST SP 800-128, Security-Focused Configuration Management'
PRIV = 'U.S. Department of Education — FERPA; HHS — HIPAA Privacy Rule summary; PCI Security Standards Council — PCI DSS v4.0'
NISTAI = 'NIST AI 600-1, Generative Artificial Intelligence Profile (July 2024); NIST AI 100-1, AI RMF 1.0 (January 2023)'
FORENS = 'NIST SP 800-86, Guide to Integrating Forensic Techniques into Incident Response; IETF RFC 3227'
OSI = 'Open Source Initiative — The Open Source Definition and approved licenses'
CISA_BK = 'CISA — “Back Up Business Data” (3-2-1 rule, test restores)'

MISCONCEPTIONS = {
    'MC-L-IT12-CUSTODY-HANDOVER': {
        'obj': 'IT-12.2', 'label': 'Treating found evidence as something to copy, reuse or tidy rather than preserve and hand over',
        'fix': 'Stop, report and preserve: evidence is imaged through a write blocker, hashed, and signed for at every hand-over '
               '(chain of custody) so its integrity can be proven.',
        'terms': ['chain of custody', 'evidence', 'write blocker', 'hash'], 'source': L122 + '; ' + FORENS, 'review': 'Pending SME review'},
    'MC-L-IT12-EVIDENCE-TERMS': {
        'obj': 'IT-12.2', 'label': 'Mixing up chain of custody, order of volatility and data retention',
        'fix': 'Chain of custody records who held the evidence and when; order of volatility decides what to collect first; '
               'retention is how long records are kept.',
        'terms': ['chain of custody', 'order of volatility', 'retention'], 'source': L122 + '; ' + FORENS, 'review': 'Pending SME review'},
    'MC-L-IT12-QUICK-NOT-CHANGE': {
        'obj': 'IT-12.1', 'label': 'Thinking a change that takes two minutes does not need the change process',
        'fix': 'Duration does not decide it: firmware, DNS, an image or an AP password is a change however quick it is.',
        'terms': ['change', 'quick', 'policy'], 'source': L121 + '; ' + ITIL, 'review': 'Pending SME review'},
    'MC-L-IT12-UNDO-AFTER': {
        'obj': 'IT-12.1', 'label': 'Working out how to undo a change only after it has gone wrong',
        'fix': 'Write the undo steps and their trigger in the ticket before you apply the change; without them there is no plan.',
        'terms': ['rollback', 'backout', 'undo'], 'source': L121, 'review': 'Pending SME review'},
    'MC-L-IT12-AI-TRUST': {
        'obj': 'IT-12.2', 'label': 'Running or forwarding AI-generated commands or facts without checking them',
        'fix': 'Treat AI output as a draft: AI can produce confident, false output (hallucination); verify against vendor documentation.',
        'terms': ['ai', 'hallucination', 'verify'], 'source': L122 + '; ' + NISTAI, 'review': 'Pending SME review'},
    'MC-L-IT12-PUBLIC-AI-DATA': {
        'obj': 'IT-12.2', 'label': 'Pasting personal or customer data into a public AI tool that policy has not approved',
        'fix': 'Check the tool is approved and the data is allowed in it; public tools may retain prompts under the provider’s terms.',
        'terms': ['public ai', 'personal data', 'policy'], 'source': L122 + '; ' + NISTAI, 'review': 'Pending SME review'},
    'MC-L-IT12-DOMAIN-LATER': {
        'obj': 'IT-12.4', 'label': 'Leaving the fault domain out of the first line of a ticket note',
        'fix': 'Name the domain first (hardware/POST, SaaS, network…) so the next technician opens the right lab or runbook.',
        'terms': ['domain', 'ticket note', 'first line'], 'source': L124, 'review': 'Pending SME review'},
}

CHTYPE, CHREP, OVERRUN, BACKOUT = 'MC-C-IT12-CHANGE-TYPE', 'MC-IT12-CHANGE-AS-REPAIR', 'MC-R3-IT12-OVERRUN', 'MC-R5-IT12-BACKOUT'
INVSELF, LICSCOPE, PWOK, UNSAFE = 'MC-C-IT12-INVESTIGATE-SELF', 'MC-C-IT12-LICENCE-SCOPE', 'MC-IT12-PASSWORD-OK-IF', 'MC-IT12-UNSAFE-ALTERNATIVE'
ACCNEED, HOLDPD = 'MC-R5-IT12-ACCESS-NEED', 'MC-R5-IT12-HOLD-PERSONAL-DATA'
SAMEPROT, ASKLATE, UNTESTED, OVERSIZE = 'MC-IT12-ALL-SAME-PROTECTION', 'MC-IT12-BACKUP-ASK-LATE', 'MC-R3-IT12-BACKUP-UNTESTED', 'MC-R3-IT12-OVERSIZED-RESTORE'
BTYPES, C321, RPO = 'MC-C-IT12-BACKUP-TYPES', 'MC-R4-IT12-321-COUNTS', 'MC-R5-IT12-RPO'
ASSETD, KBC, RUNBK = 'MC-R5-IT12-ASSET-DISPOSAL', 'MC-R5-IT12-KB-CONTENT', 'MC-R5-IT12-RUNBOOK'
CUSTODY, VOLAT = 'MC-L-IT12-CUSTODY-HANDOVER', 'MC-L-IT12-EVIDENCE-TERMS'
QUICK, UNDO, AITRUST, AIDATA, DOMAIN = ('MC-L-IT12-QUICK-NOT-CHANGE', 'MC-L-IT12-UNDO-AFTER', 'MC-L-IT12-AI-TRUST',
                                        'MC-L-IT12-PUBLIC-AI-DATA', 'MC-L-IT12-DOMAIN-LATER')

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
def _row(labels, y=30, h=56, note=''):
    n = len(labels); w = (620 - (n - 1) * 10) // n
    out = ''.join(box(10 + i * (w + 10), y, w, h, a, b) + (arrow(10 + i * (w + 10) + w, y + h // 2, 20 + i * (w + 10) + w, y + h // 2) if i < n - 1 else '')
                  for i, (a, b) in enumerate(labels))
    return out + (label(320, y + h + 26, note, 11) if note else '')

_LIFE = svg(640, 130, 'Change lifecycle: request, assess risk and impact, approve, implement with a checklist in the window, verify or back out, review and close',
            _row([('Request', ''), ('Assess', 'risk · impact'), ('Approve', ''), ('Implement', 'checklist'), ('Verify', 'or back out'), ('Review', '+ close')],
                 note='the backout trigger is written before “Implement”'))
_CMP = svg(640, 130, 'Change management path for the exam: request form, risk analysis, plan with sandbox test, backup and rollback, change board approval, implementation with peer review, closure after end-user acceptance',
           _row([('Request form', 'purpose · scope'), ('Risk', 'systems · level'), ('Plan', 'sandbox · rollback'), ('CAB', 'approves'),
                 ('Implement', 'peer review'), ('Close', 'user accepts')], note='no approval without a rollback; no closure without acceptance'))
_AI = svg(640, 130, 'Checks before using an AI tool on a work task: is the tool approved, is the data allowed in it, use it and treat the output as a draft, verify facts, sources and bias, record or disclose the use',
          _row([('Tool approved?', 'policy'), ('Data allowed?', 'in this tool'), ('Use it', 'as a draft'), ('Verify', 'facts · bias'), ('Disclose', 'if required')],
               note='policy and data checks come before the prompt'))
_FIND = svg(640, 130, 'When you find prohibited content or signs of an incident: stop, report to management, preserve with a forensic copy through a write blocker, record the chain of custody',
            _row([('Stop', 'no browse · no delete'), ('Report', 'to management'), ('Preserve', 'write blocker · hash'), ('Record', 'chain of custody')],
                 note='the technician who found it is a witness, not the investigator'))
_CHAIN = svg(640, 150, 'Restoring Wednesday from a full plus incremental chain needs Sunday’s full and the Monday, Tuesday and Wednesday incrementals; with differentials it needs only Sunday’s full and Wednesday’s differential',
             _row([('Sun', 'full'), ('Mon', 'incremental'), ('Tue', 'incremental'), ('Wed', 'incremental'), ('Restore', 'Wednesday')],
                  note='incremental: full + all three · differential: full + Wednesday only'))
_SWAP = svg(640, 130, 'Capstone for replacing a reception PC: change request, back up and test a restore, swap and verify with the user, sanitise the old drive, update both asset records and the knowledge base',
            _row([('Change', 'request'), ('Back up', '+ test restore'), ('Swap', '+ verify'), ('Sanitise', 'old drive'), ('Update', 'assets + KB')],
                 note='each habit from the chapter appears once'))

LESSONS = {
    '12.1': {
        'start-here-the-shop-is-a-system': section(
            'Start here — the shop is a system', 'IT-12.1',
            [check('A technician adds a DNS record after 15:00, against policy, because “it only takes a second”. Is it a change?',
                   'Yes — speed does not make it exempt',
                   ['No — anything under a minute is a quick fix', 'No, as long as nobody notices it went in'],
                   'The policy decides what is a change, not how long it takes. A DNS record after the cut-off is a change and '
                   'needs the process, however quick.', mc=[QUICK, QUICK])],
            plain('''<p>A shop runs on a few systems that keep people and data safe.</p>
<p>Change control. Privacy. Backup. Tickets.</p>
<p>Three facts to hold on to:</p>
<ul><li>RAID is not a backup.</li><li>A snapshot is not an off-site backup.</li>
<li>A quick change is still a change. Adding a DNS record after 15:00, when policy says no, is a change even if it
takes a second.</li></ul>''',
                  L121,
                  [check('Why is RAID not a backup?',
                         'A deletion is written to every disk at once',
                         ['RAID disks are always slower than backups', 'RAID only works on servers, not on desktops'],
                         'RAID keeps a disk failure from stopping the system, but deletions, corruption and ransomware are mirrored '
                         'to every disk immediately. It is not a separate copy.', mc=[SAMEPROT, None])]),
            analogy('''<p>Think of an airport.</p>
<p>Planes leave safely every few minutes not because pilots are brilliant but because the airport is a system: every
change to a flight plan is filed (change control), passengers’ details are kept private (privacy), there is a spare
plane at another airport (an off-site backup), and every fault is logged (tickets). A second engine on the same plane
(RAID) helps if one fails, but it is no use if the whole plane is lost. And a pilot who “just quickly” changes runway
without telling the tower is the cause of the accident report.</p>''',
                    L121 + ' (airport analogy written for this rung)',
                    [check('In the airport story, “a second engine on the same plane” is like which storage feature?',
                           'RAID — protection from one disk failing',
                           ['An off-site backup kept in another city', 'A ticket logging the fault for the next shift'],
                           'RAID keeps the system running when a disk fails, like a second engine, but a lost plane (deleted or '
                           'encrypted data) loses both. An off-site backup is the spare plane elsewhere.', mc=[SAMEPROT, None])]),
            visual('''<ol class="ladder-trace">
<li>Change control → a DNS record after 15:00 needs a request, even if it takes a second.</li>
<li>Privacy → no PII or passwords in tickets or hallway talk.</li>
<li>Backup → RAID ≠ backup; snapshot ≠ off-site copy.</li>
<li>Tickets → the record that lets the next person carry on.</li></ol>''',
                   L121 + ' (the four shop systems, as a list with one example each)',
                   [check('A VM snapshot sits on the same storage as the VM. Why is it not an off-site backup?',
                          'Lose the storage and you lose both',
                          ['Snapshots are deleted every night automatically', 'Snapshots can only be restored by the vendor'],
                          'A snapshot is a short-term rollback on the same storage; if that storage fails or is encrypted, the VM and '
                          'its snapshot go together. An off-site copy survives that.', mc=[SAMEPROT, None])]),
            tryit('''<p>Sort each item to say whether it is a real backup on its own, then reveal the rule.</p>''',
                  L121,
                  [check('Which of these counts as a change under policy?',
                         'Updating a switch’s firmware',
                         ['Reading a PC’s IP address', 'Opening Event Viewer to look'],
                         'Firmware, DNS, an image or an AP password are changes whatever the time they take. Reading settings and '
                         'logs changes nothing.', mc=[QUICK, CHREP])],
                  widget=sort('A backup on its own, or not?',
                              {'Not a backup on its own': ['RAID 1 mirror', 'VM snapshot on the same storage', 'OneDrive sync'],
                               'Backup': ['Nightly copy to an off-site, immutable store']},
                              'Only a separate copy you control, ideally off-site, survives deletion and ransomware.'))),

        'core-content': section(
            'Core content', 'IT-12.1',
            [check('Is adding a user to a printer group from the request catalogue a normal change?',
                   'No — it is a standard, pre-approved change',
                   ['Yes — every change needs the change board first', 'No — it is an emergency change to log afterwards'],
                   'A standard change is low-risk, repeatable and pre-approved with a documented procedure; you just log it. '
                   'Normal changes are assessed and approved; emergencies restore service now.', mc=[CHTYPE, CHTYPE])],
            plain('''<p>Most outages come from changes. Change control makes changes safe and predictable.</p>
<p>There are three types.</p>
<ul><li><strong>Standard</strong> — low risk, done often, already approved. Just log it.</li>
<li><strong>Normal</strong> — planned, and approved before you do it.</li>
<li><strong>Emergency</strong> — needed now to fix an outage or a serious risk. Approved fast, reviewed after.</li></ul>
<p>A change request says what changes, the risk, how it was tested, the steps, how to undo it, when, and who is told.</p>''',
                  L121 + '; ' + ITIL,
                  [check('Who reviews an emergency change, and when?',
                         'A named authority approves fast; full review follows',
                         ['Nobody — emergencies skip the change process', 'The change board, before the work starts as normal'],
                         'An emergency change gets expedited approval by a named authority and a full review afterwards. It is not '
                         'exempt, and waiting for a normal CAB would defeat the point.', mc=[CHTYPE, CHTYPE])]),
            analogy('''<p>Think of a city’s road works.</p>
<p>Filling a pothole from the standard list needs no meeting (a standard change). Closing a main road for a weekend
needs a permit, a diversion plan and notices to residents a week before (a normal change with a backout and
communication). A burst water main gets dug up now, with the paperwork done afterwards (an emergency change). And the
diversion signs are the backout plan: what everyone does if the road is not ready by Monday.</p>''',
                    L121 + ' (road-works analogy written for this rung)',
                    [check('In the road-works story, a burst water main dug up now matches which change type?',
                           'Emergency',
                           ['Standard change', 'Normal'],
                           'An emergency change restores service or closes a serious risk now, with expedited approval and a full review '
                           'afterwards. Standard is pre-approved routine; normal is planned and approved first.', mc=[CHTYPE, CHTYPE])]),
            visual(_LIFE + '''
<ol class="ladder-trace">
<li>Purpose: move the floor-2 printer from 10.2.0.40 to reserved .60 to end an address conflict.</li>
<li>Scope: one printer, one queue, 34 users. Risk: printing fails if the port is not updated.</li>
<li>Test: new port on a test queue, a page printed.</li>
<li>Steps 1–5, ending “print from two user PCs”. Backout: static .40 and the old port if step 5 fails.</li>
<li>Window Tuesday 07:30–08:00; email the floor the day before; team lead approved Monday.</li></ol>''',
                   L121 + ' (lifecycle diagram and worked example “moving a printer”, drawn); ' + ITIL,
                   [check('In the printer change, when is the backout used?',
                          'If step 5, the print test, fails',
                          ['Only if the team lead asks for it later', 'Whenever a user phones during the window'],
                          'The trigger is written in the plan: if printing from two PCs fails at step 5, set the printer back to .40 '
                          'and restore the old port. It is decided in advance, not on request.', mc=[BACKOUT, UNDO])]),
            tryit('''<p>Sort each change to its type, then order the lifecycle in your head and reveal it.</p>''',
                  L121 + '; ' + ITIL,
                  [check('Which part of a change request says how to undo it?',
                         'The backout (rollback) plan',
                         ['The communication plan for users', 'The approval record'],
                         'The backout plan holds the undo steps and the point at which you use them. Communication says who is told; '
                         'approval says who agreed.', mc=[BACKOUT, BACKOUT])],
                  widget=sort('Which change type?',
                              {'Standard change': ['Replacing a keyboard', 'Adding a user to a printer group from the catalogue'],
                               'Normal': ['Changing a Group Policy setting', 'Moving a shared printer to a new address'],
                               'Emergency': ['Blocking a malicious sender during a phishing outbreak']},
                              'Pre-approved and routine, planned and approved, or needed now.'))),

        'change-control': section(
            'Change control', 'IT-12.1',
            [check('A technician reseats a RAM module to fix a fault. Change or repair?',
                   'A repair, and it is still documented',
                   ['A change that needs the change board first', 'Neither, so nothing needs to be written down'],
                   'Reseating RAM restores the device to its known state, so it is a repair rather than a change, but it still '
                   'goes in the ticket. Firmware, DNS, an image or an AP password would be changes.', mc=[CHREP, CHREP])],
            plain('''<p>Some things are always <strong>changes</strong>: new firmware, a DNS record, a new image, a new Wi-Fi
password.</p>
<p>Some things are <strong>repairs</strong>: putting the RAM back in its slot. A repair puts things back how they were.
You still write it down.</p>
<p>Time does not matter. A change that takes two minutes is still a change if it skips the process.</p>''',
                  L121,
                  [check('Changing a Wi-Fi access point’s password takes one minute. Does it go through change control?',
                         'Yes — it changes what every device depends on',
                         ['No — a one-minute change is too short to need a record', 'No — passwords are a matter for the user'],
                         'An AP password change affects every device that connects; it is a change however fast it is. The minute it '
                         'takes is irrelevant.', mc=[QUICK, None])]),
            analogy('''<p>Think of a restaurant kitchen.</p>
<p>Wiping down a counter or tightening a loose oven knob puts the kitchen back the way it should be — a repair, noted in
the daily log. Changing the menu, the supplier or the oven temperature setting for every dish is a change, and the head
chef has to know before it happens, even if it takes thirty seconds. A cook who quietly turns every oven up “just a
little” ruins the evening service.</p>''',
                    L121 + ' (kitchen analogy written for this rung)',
                    [check('In the kitchen story, “tightening a loose oven knob” is like which support action?',
                           'Reseating a RAM module',
                           ['Updating a switch’s firmware', 'Adding a new DNS record'],
                           'Both put the equipment back to its known state — a repair, still logged. Firmware and DNS change how the '
                           'system behaves, so they are changes.', mc=[CHREP, None])]),
            visual('''<ol class="ladder-trace">
<li>Does it change how the system behaves for others (firmware, DNS, image, AP password)? → <strong>change</strong>.</li>
<li>Does it only restore the known state (reseat RAM, replace a cable like-for-like)? → <strong>repair</strong>.</li>
<li>Either way → write it in the ticket.</li>
<li>Short duration → no effect on the answer.</li></ol>''',
                   L121 + ' (change-or-repair test, as a numbered trace written for this rung)',
                   [check('What decides whether a task is a change?',
                          'Whether it alters how the system behaves',
                          ['Whether it takes more than five minutes', 'Whether the user is watching at the time'],
                          'A change alters configuration others depend on; a repair restores the known state. Duration and who is '
                          'watching do not enter into it.', mc=[QUICK, CHREP])]),
            tryit('''<p>Sort each task into change or repair, then reveal the rule that ties them together.</p>''',
                  L121,
                  [check('A repair has been done. What still has to happen?',
                         'It is recorded in the ticket',
                         ['It is approved by the CAB afterwards', 'It is undone at the end of the day'],
                         'Repairs do not need change approval, but they are documented so the next technician knows what was done. '
                         'They are not reversed or sent to the board.', mc=[CHREP, None])],
                  widget=sort('Change or repair?',
                              {'Change': ['Firmware update', 'New DNS record', 'New AP password', 'Deploy a new image'],
                               'Repair (still documented)': ['Reseat a RAM module', 'Replace a cable like-for-like']},
                              'A two-minute change that skips the process is still a change.'))),

        'rollback-is-part-of-the-plan': section(
            'Rollback is part of the plan', 'IT-12.1',
            [check('When should the undo steps be written in the ticket?',
                   'Before you click apply',
                   ['After the change, if it goes wrong', 'Only when the change board asks'],
                   'If you cannot say how to undo a change, you do not have a plan. Writing the undo first means you have '
                   'thought about it while calm, not during an outage.', mc=[UNDO, UNDO])],
            plain('''<p>A plan has two halves. How to do it. And how to undo it.</p>
<p>If you cannot say how you would undo the change, you do not have a plan yet.</p>
<p>Write the undo steps in the ticket <em>before</em> you click apply. Say when you would use them, for example “if the
test print fails”.</p>''',
                  L121,
                  [check('Which of these is a complete undo note?',
                         'If the test print fails, set .40 and restore the old port',
                         ['We will think of something if it goes wrong', 'Ask the team lead what to do afterwards if printing stops'],
                         'A real undo note names the trigger (the test print fails) and the exact steps. “Think of something” or '
                         '“ask later” is no plan at all.', mc=[UNDO, BACKOUT])]),
            analogy('''<p>Think of a climber on a cliff.</p>
<p>Before moving up to the next hold, a good climber checks the rope is clipped in below — the way back down is fixed
before the risky move, not after the slip. A climber who plans to “find a way down if it goes wrong” is not climbing
safely; they are hoping. The rope is the undo written in the ticket, and the clip is done before you click apply.</p>''',
                    L121 + ' (climbing analogy written for this rung)',
                    [check('In the climbing story, “clipping the rope before the next move” is like what?',
                           'Writing the undo before applying the change',
                           ['Asking the user to watch the change happen on their screen', 'Closing the ticket as soon as it works'],
                           'The safety line is fixed before the risky step, just as the undo is written before apply. Closing quickly '
                           'or having the user watch does not give you a way back.', mc=[UNDO, None])]),
            visual('''<ol class="ladder-trace">
<li>Write the change steps.</li>
<li>Write the undo steps.</li>
<li>Write the trigger: “use the undo if …”.</li>
<li>Only now click apply.</li>
<li>Test; if the trigger is hit, run the undo — no improvising.</li></ol>''',
                   L121 + ' (the do-and-undo order, as a numbered trace)',
                   [check('The trigger in the plan is hit during the change. What do you do?',
                          'Run the written undo steps',
                          ['Try a few more fixes before deciding', 'Leave it and tell the user in the morning'],
                          'The trigger was agreed in advance so the decision is easy under pressure: run the undo. Improvising or '
                          'leaving a broken service turns a change into an outage.', mc=[OVERRUN, UNDO])]),
            tryit('''<p>Put the steps in the right order, then reveal what “no plan” looks like.</p>''',
                  L121,
                  [check('A colleague says “I’ll work out the rollback if I need one”. What is missing?',
                         'A plan — the undo must be written first',
                         ['Nothing, rollbacks are rarely needed anyway', 'Only the user’s signature on the ticket'],
                         'Without written undo steps there is no plan. That most changes succeed is no reason to skip the way back.',
                         mc=[UNDO, None])],
                  widget=order('Order the work for any change.',
                               ['Write the change steps', 'Write the undo steps and trigger', 'Click apply', 'Test against the trigger'],
                               'The undo exists before the change does.'))),

        'change-management-procedures': section(
            'Change management procedures', 'IT-12.1',
            [check('When is a change closed?',
                   'After users accept it and it is documented',
                   ['As soon as the technician has finished the work', 'When the change board approves the request form'],
                   'Closure comes after implementation, end-user acceptance and documentation. Approval happens before the work; '
                   'finishing the work is not the same as the users confirming it works.', mc=[OVERRUN, CHTYPE])],
            plain('''<p>For the exam, a change follows a path.</p>
<ol><li>A <strong>request form</strong>: why, what, which type, and when.</li>
<li>A <strong>risk check</strong>: which systems, how bad, what level.</li>
<li>A <strong>plan</strong>: test it in a sandbox first. Back up the data. Write the rollback.</li>
<li><strong>Approval</strong> by the change board (CAB).</li>
<li>One <strong>named person</strong> does it. A colleague checks the work.</li>
<li>The <strong>users</strong> confirm it works. Then close it.</li></ol>
<p>A change freeze is a time when only emergency changes are allowed.</p>''',
                  L121 + '; ' + ITIL,
                  [check('What is a change freeze?',
                         'A period when only emergency changes are allowed',
                         ['A change that has been rolled back and locked', 'The moment when the CAB stops a change mid-way'],
                         'A change freeze (for example at year-end) allows only emergency changes. It is not a rollback or a CAB '
                         'decision about one change.', mc=[CHTYPE, None])]),
            analogy('''<p>Think of a hospital operation.</p>
<p>The consent form states the procedure and why (the request form). The surgeon and anaesthetist assess the risks
(risk analysis). A practice run on a model and blood on standby (sandbox test and backup), with a plan to close up safely
if something goes wrong (rollback). The board signs off on unusual surgery (CAB). One named surgeon operates while a
second checks the count (peer review). The patient is not discharged until they can walk (end-user acceptance).</p>''',
                    L121 + ' (operating-theatre analogy written for this rung)',
                    [check('In the hospital story, “not discharged until the patient can walk” matches which step?',
                           'End-user acceptance before closing',
                           ['The CAB approval of the plan', 'The sandbox test before the change'],
                           'The change closes only when users confirm it works, as discharge waits for the patient to walk. CAB '
                           'approval and sandbox testing come earlier.', mc=[OVERRUN, None])]),
            visual(_CMP + '''
<ol class="ladder-trace">
<li>Request: fix a published firewall vulnerability; one firewall, no rule changes; normal; Saturday 06:00–08:00.</li>
<li>Risk: internet and VPN for all 40 staff; medium.</li>
<li>Plan: firmware tested on the lab firewall; config backed up; rollback = previous image and config.</li>
<li>CAB approves Thursday; a named technician implements, a colleague peer-reviews.</li>
<li>Staff at two sites confirm VPN and web → change closed.</li></ol>''',
                   L121 + ' (change path and worked example “firmware update on the office firewall”, drawn); ' + ITIL,
                   [check('In the firewall example, what was the sandbox?',
                          'The lab firewall where the firmware was tried',
                          ['The Saturday-morning maintenance window', 'The backup copy of the running configuration'],
                          'A sandbox is an isolated test environment — here, the lab firewall. The window is when the change happens, '
                          'and the config backup is part of the rollback.', mc=[BACKOUT, None])]),
            tryit('''<p>Order the change path, then reveal what went wrong in the Friday-afternoon story.</p>''',
                  L121 + '; ' + ITIL,
                  [check('A Group Policy pushed on Friday afternoon with no request or test breaks printing in three offices. What was missing?',
                         'A request, a sandbox test and a rollback plan',
                         ['Only a larger number of technicians on duty', 'A faster network link between the offices'],
                         'With no request, test or rollback, nobody knew what changed and it took hours to rebuild the old settings. '
                         'The team now requires the full path for every normal change.', mc=[UNDO, None])],
                  widget=order('Order the change management path.',
                               ['Request form', 'Risk analysis', 'Plan: sandbox, backup, rollback', 'CAB approval',
                                'Implement with peer review', 'End-user acceptance and close'],
                               'No approval without a rollback; no closure without user acceptance.'))),
    },
    '12.2': {
        'core-content': section(
            'Core content', 'IT-12.2',
            [check('To show a formatting bug, would you attach a screenshot of a gradebook to the ticket?',
                   'No — crop to the headers or copy the error text',
                   ['Yes, as long as the ticket is marked as internal', 'Yes, because support staff are trusted with grades'],
                   'A ticket read by 40 staff is not a place for 30 students’ grades. A cropped screenshot of the column headers '
                   'or the exact error shows the bug without any personal data.', mc=[HOLDPD, ACCNEED])],
            plain('''<p>Some data is about people. Names with ID numbers, home addresses, birth dates, photos. This is
<strong>PII</strong>. Some of it is also protected by law, such as student records or health data.</p>
<p>The rule is <strong>minimum access</strong>. Open only what the job needs. Keep it open only as long as needed.
Write down only what the next technician needs.</p>
<p>If a user sends you a file full of personal data, ask for the error text instead. Delete the copy safely.</p>
<p>Never look someone up “just this once”. Report a lost laptop with health data at once.</p>''',
                  L122 + '; ' + PRIV,
                  [check('A colleague asks you to look up another staff member’s home address. What do you do?',
                         'Decline: access is for job need only',
                         ['Look it up once, since they asked politely', 'Send it, but ask them not to share it further'],
                         'Access to personal data is for the task in hand, not for favours. Politeness or a promise not to share does '
                         'not create a job need.', mc=[ACCNEED, ACCNEED])]),
            analogy('''<p>Think of a hotel housekeeper.</p>
<p>They have a key to every room, but they go in only to clean, only while cleaning, and they do not read the guest’s
letters on the desk. If a guest leaves a passport on the bed, the housekeeper tidies around it and does not photograph
it for the manager. A housekeeper who tells the bar staff what they saw in room 214 has broken the hotel’s trust,
however interesting the story. That is minimum access and professional conduct.</p>''',
                    L122 + ' (housekeeper analogy written for this rung)',
                    [check('In the hotel story, “tidying around the passport, not photographing it” is like what in support?',
                           'Working only in the faulty app, not saving records',
                           ['Screenshotting the student records for the ticket', 'Copying the user’s files to check the error'],
                           'Minimum access means you work only where the fault is and record only what the next technician needs. '
                           'Screenshots and copies of personal data create a privacy risk.', mc=[HOLDPD, None])]),
            visual('''<ol class="ladder-trace">
<li>Remote session shows student records → ask the user to minimise them; work only in the faulty app.</li>
<li>User emails a spreadsheet of personal data → ask for the error text or a test file; delete the copy securely.</li>
<li>Request for a colleague’s details → decline; job need only.</li>
<li>Laptop with health data lost → report now as a security incident; note its encryption status.</li>
<li>Request to install a personal copy on a lab PC → decline under licensing and point to the software portal.</li></ol>''',
                   L122 + ' (the do / do-not table, as a numbered trace)',
                   [check('A laptop with health data is reported lost. What do you do?',
                          'Report it as a security incident now',
                          ['Wait a few days in case it turns up', 'Remotely wipe it and close the ticket'],
                          'A lost device with regulated data is an incident to report immediately, recording whether it was '
                          'encrypted. Waiting delays the response; wiping on your own skips the process.', mc=[ACCNEED, INVSELF])]),
            tryit('''<p>Sort each situation into what you do and what you never do, then reveal the minimum-access rule.</p>''',
                  L122 + '; ' + PRIV,
                  [check('You notice content on a PC that may show a crime. Name what you must not do.',
                         'Investigate, copy or discuss it',
                         ['Stop the work and note the facts', 'Report it through the named procedure'],
                         'Do not investigate, copy or talk about it. Stop if appropriate, record only the facts and report through '
                         'the manager, security, safeguarding or HR as your institution names.', mc=[INVSELF, INVSELF])],
                  widget=sort('Do, or never do?',
                              {'Do': ['Ask the user to minimise records', 'Ask for the exact error text', 'Report a lost laptop now'],
                               'Never do': ['Screenshot a gradebook for the ticket', 'Look up a colleague “just this once”']},
                              'Open only what the task needs, for as long as it needs, and record only what the next technician needs.'))),

        'privacy': section(
            'Privacy', 'IT-12.2',
            [check('A user asks you to email them their colleague’s password “to save time”. How do you refuse well?',
                   'Decline and offer the approved reset process',
                   ['Ignore the request and close the ticket without a reply', 'Send it by text message rather than email'],
                   'Refusing unsafe access means saying no and offering the approved path — here, a verified reset for the account '
                   'owner. Ignoring it or offering another unsafe shortcut both fail the user.', mc=[UNSAFE, PWOK])],
            plain('''<p>Two short rules.</p>
<p>Keep PII and passwords out of tickets. Keep them out of hallway talk too.</p>
<p>When you have to say no to something unsafe, do not just say no. Offer the approved, safe way to get the job done.</p>''',
                  L122,
                  [check('Why offer an approved path when you refuse a request?',
                         'So the user can still get the job done safely',
                         ['So the refusal sounds less rude to them', 'So the ticket can be closed more quickly'],
                         'A bare “no” pushes people to find their own unsafe workaround; the approved path keeps them working and '
                         'safe. Politeness and speed are side effects.', mc=[UNSAFE, None])]),
            analogy('''<p>Think of a pharmacist.</p>
<p>When a customer asks for a prescription medicine without a prescription, the pharmacist does not just say “no” and
turn away — the customer might go somewhere worse. They say “I can’t sell that without a prescription, but here is
how to get one today, and this over-the-counter option may help meanwhile.” They also never discuss one customer’s
medicines with the next person in the queue.</p>''',
                    L122 + ' (pharmacist analogy written for this rung)',
                    [check('In the pharmacist story, “here is how to get a prescription today” is like what?',
                           'Offering the approved path when refusing',
                           ['Selling the medicine just this once', 'Telling the next customer about it'],
                           'The pharmacist refuses the unsafe request and points to the legitimate route, which is exactly what the '
                           'privacy rule asks of a technician.', mc=[UNSAFE, None])]),
            visual('''<ol class="ladder-trace">
<li>Request: “Put my password in the ticket so the night shift can log in as me.”</li>
<li>Refuse: passwords never go in tickets, even with consent.</li>
<li>Offer: the night shift uses their own accounts; access is granted to the right group.</li>
<li>Record: the request and the approved route — no password.</li></ol>''',
                   L122 + ' (refuse-and-redirect, as a worked trace written for this rung)',
                   [check('The user says it is fine to put their password in the ticket because they consent. Is it?',
                          'No — consent does not make it safe',
                          ['Yes, because the user has agreed to it', 'Yes, if the ticket is marked private'],
                          'Tickets are read widely and kept for years; a password in one is a leak whatever the user agrees to. '
                          'Marking it private does not change that.', mc=[PWOK, PWOK])]),
            tryit('''<p>For each unsafe request, decide the refusal and the approved path, then reveal one answer.</p>''',
                  L122,
                  [check('Where may a user’s password be written?',
                         'Nowhere — not in tickets, chat or notes',
                         ['In a private ticket note only you can see', 'In a chat message deleted after an hour'],
                         'A password is never recorded by support anywhere; private notes and deleted chats are still copies. Use '
                         'verified resets and named accounts instead.', mc=[PWOK, PWOK])],
                  widget=reveal('A teacher asks you to unlock a student’s account by telling her the student’s password. Your reply?',
                                '“I can’t share passwords, but the student can reset it with ID at the desk, or I can start a verified reset now.”'))),

        'ai-tools-at-work-policy-limitations-and-private-vs-public': section(
            'AI tools at work: policy, limitations, and private vs. public', 'IT-12.2',
            [check('An AI assistant suggests a PowerShell command with a parameter you have never seen. What do you do first?',
                   'Look the cmdlet up in Microsoft Learn',
                   ['Run it on the user’s PC to see what happens', 'Ask the same AI tool whether it is correct'],
                   'AI can produce confident output that is false — a hallucination. Check the cmdlet against the vendor’s '
                   'documentation before running anything; asking the same tool again is not verification.', mc=[AITRUST, AITRUST])],
            plain('''<p>AI tools now appear in many apps. Three things to know.</p>
<p><strong>Policy.</strong> Your workplace says which AI tools you may use. It says what data may go in. It may say you
must tell people when you used AI.</p>
<p><strong>Limits.</strong> AI can sound sure and still be wrong. It can make up commands that do not exist. It can be out of
date. It can be biased. Check everything it says.</p>
<p><strong>Public or private.</strong> A public tool may keep what you type. A private tool is set up for your workplace.
Never put personal data into a public tool.</p>''',
                  L122 + '; ' + NISTAI,
                  [check('Why might a public AI tool be wrong for a customer spreadsheet?',
                         'It may keep prompts and is not approved for that data',
                         ['Public tools cannot open spreadsheet files at all', 'Customer data makes the AI answer too slowly'],
                         'Depending on the provider’s terms, prompts may be retained or used for training, and the organisation has '
                         'not approved the tool for personal data. Use the approved enterprise assistant.', mc=[AIDATA, AIDATA])]),
            analogy('''<p>Think of a very confident new intern.</p>
<p>They answer every question instantly and sound sure of themselves, but sometimes they make things up — a policy
that does not exist, a phone number that is wrong. You would not send their draft to a customer without checking it,
and you would not hand them the confidential customer files if they were a temp from an agency you have no contract
with. A private AI is an intern under your company’s contract; a public one is a stranger in a café.</p>''',
                    L122 + ' (confident-intern analogy written for this rung); ' + NISTAI,
                    [check('In the intern story, “making up a policy that does not exist” is which AI limitation?',
                           'A hallucination',
                           ['A bias', 'A licence breach'],
                           'Fluent, confident but false output is a hallucination (NIST AI 600-1 calls it confabulation). Bias is a '
                           'skew from training data, and a licence breach is a legal issue.', mc=[AITRUST, None])]),
            visual(_AI + '''
<ol class="ladder-trace">
<li>A sales user wants to paste a customer spreadsheet into a public chatbot.</li>
<li>Tool approved? No. Data allowed? No — personal data.</li>
<li>Point her to the approved enterprise assistant, which keeps data in the company’s tenant.</li>
<li>Remind her to check the summary before sending it on.</li></ol>''',
                   L122 + ' (AI-checks diagram and real-world scenario “the customer list”, drawn)',
                   [check('Which check comes before typing anything into an AI tool?',
                          'Whether the tool and the data are approved',
                          ['Whether the answer will be quick enough', 'Whether the output needs a nice format'],
                          'Policy and data checks come before the prompt: is this tool approved, and may this data go into it? Speed '
                          'and formatting do not protect anyone.', mc=[AIDATA, None])]),
            tryit('''<p>Order the checks before an AI-assisted task, then reveal what to note on the ticket.</p>''',
                  L122 + '; ' + NISTAI,
                  [check('Presenting AI-written code as your own original work can breach what?',
                         'Academic, employment or licensing rules',
                         ['Only the AI provider’s pricing plan and usage limits', 'Nothing, if the code works correctly'],
                         'Plagiarism is part of an AI policy: passing AI output off as your own, or reproducing copyrighted output, '
                         'can breach academic, employment or licensing rules even when it works.', mc=[AITRUST, None])],
                  widget=order('Order the checks before using AI on a work task.',
                               ['Is the tool approved?', 'Is the data allowed in it?', 'Use it; treat output as a draft',
                                'Verify facts, sources and bias', 'Record or disclose the use if required'],
                               'Policy and data first; verification before anyone relies on the answer.'))),

        'incident-handling-licensing-and-regulated-data': section(
            'Incident handling, licensing and regulated data', 'IT-12.2',
            [check('A licence says “free for personal, non-commercial use”. Can the department install it on 40 work PCs?',
                   'No — business use needs a commercial licence',
                   ['Yes, because the software costs nothing at all', 'Yes, if each install is removed at the end of term'],
                   'The EULA does not cover business use, so 40 installs breach it. The fix is to remove them and buy the right '
                   'licence, and to install only from the approved catalogue.', mc=[LICSCOPE, LICSCOPE])],
            plain('''<p>Three topics in one section.</p>
<p><strong>Incidents.</strong> If you find illegal content, stop. Do not look further, copy or delete. Tell your
manager. A trained person copies the drive. Every hand-over is written down (chain of custody).</p>
<p><strong>Licences.</strong> Every install needs a valid licence. “Free for personal use” does not mean free at work. A
perpetual licence is paid once. A subscription stops when payments stop.</p>
<p><strong>Regulated data.</strong> Card data (PCI DSS), health data (HIPAA) and ID numbers have extra rules. Keep records
only as long as required, then dispose of them safely.</p>''',
                  L122 + '; ' + FORENS + '; ' + PRIV,
                  [check('What is the difference between a perpetual and a subscription licence?',
                         'Perpetual is paid once; subscription per period',
                         ['Perpetual expires yearly; subscription never does', 'They are the same thing with different names'],
                         'A perpetual licence lets you use that version indefinitely after one payment; a subscription’s right to use '
                         'ends when payment stops.', mc=[LICSCOPE, None])]),
            analogy('''<p>Think of a plumber who opens a wall and finds something that looks like stolen goods.</p>
<p>They do not rummage through it, take photos for their friends or throw it away. They step back, call their boss, and
the boss calls the police. Officers bag and label it and sign for it at every hand-over. The plumber writes down what
they saw and when — they are a witness, not a detective.</p>
<p>And the plumber’s own tools are licensed for trade use: a “home use only” drill on a building site breaks the
warranty terms, just as a personal licence does at work.</p>''',
                    L122 + ' (plumber-finds-goods analogy written for this rung)',
                    [check('In the plumber story, “signing for it at every hand-over” is which procedure?',
                           'Chain of custody',
                           ['Order of volatility', 'Data retention'],
                           'Chain of custody records who held the evidence, when and why, from collection onward. Order of volatility '
                           'is about what to collect first; retention is how long records are kept.', mc=[VOLAT, VOLAT])]),
            visual(_FIND + '''
<ol class="ladder-trace">
<li>Recovering files, a technician sees images that appear to be prohibited content.</li>
<li>Stop: close nothing further, copy nothing, delete nothing.</li>
<li>Tell the manager straight away; the manager follows policy and contacts law enforcement.</li>
<li>The laptop is bagged, labelled and signed for on a chain-of-custody form.</li>
<li>The technician writes what they saw, when, and every action — and discusses it with nobody.</li></ol>''',
                   L122 + ' (stop-report-preserve-record diagram and worked example, drawn); ' + FORENS,
                   [check('Why is a drive imaged through a write blocker with a hash recorded?',
                          'So the copy is proven identical and unaltered',
                          ['So the drive can be reused straight away', 'So the image file takes up less space'],
                          'A write blocker stops any writes to the original, and matching hashes of the original and the copy show '
                          'nothing changed. It is about integrity, not reuse or size.', mc=[CUSTODY, None])]),
            tryit('''<p>On a real Linux VM flagged for a compromise, preserve the evidence before you change anything —
the probe checks that you did.</p>''',
                  L122 + '; ' + FORENS,
                  [check('Which licence type lets you use, change and share software, with conditions such as keeping notices?',
                         'An open-source licence such as GPL or MIT',
                         ['A “free for personal use” home licence', 'A perpetual licence for one fixed version'],
                         'OSI-approved open-source licences allow use, change and sharing, with conditions. A personal-use licence '
                         'forbids business use; a perpetual licence is about payment, not sharing.', mc=[LICSCOPE, LICSCOPE])],
                  widget=order('Order the response when you find prohibited content.',
                               ['Stop — no browsing, copying or deleting', 'Report to management', 'Preserve with a forensic copy',
                                'Record the chain of custody'],
                               'The technician who found it is a witness, not the investigator.'),
                  lab={'id': 'linux-vm-incident', 'note': 'Preserve evidence before any change, then remove persistence and report.'})),
    },
    '12.3': {
        'core-content': section(
            'Core content', 'IT-12.3',
            [check('Backups run nightly. Can they meet a one-hour RPO?',
                   'No — up to 24 hours of data could be lost',
                   ['Yes, as long as each backup completes', 'Yes, if the restore takes under an hour'],
                   'RPO is how much data, in time, the business can afford to lose; a nightly backup can lose a day. How reliable '
                   'it is, or how fast the restore (RTO), does not change that.', mc=[RPO, RPO])],
            plain('''<p>Keep <strong>3</strong> copies of important data, on <strong>2</strong> kinds of storage, with
<strong>1</strong> copy off-site. That is the 3-2-1 rule.</p>
<p>RAID, snapshots and file sync are not backups on their own. A deletion or ransomware reaches them too.</p>
<p>A <strong>full</strong> backup copies everything. An <strong>incremental</strong> copies changes since the last backup. A
<strong>differential</strong> copies changes since the last full one.</p>
<p><strong>RPO</strong> is how much data you can lose. <strong>RTO</strong> is how long you can be down.</p>
<p>A backup you have never restored is only a hope. Test it.</p>''',
                  L123 + '; ' + CISA_BK,
                  [check('What do the numbers in the 3-2-1 rule count?',
                         'Copies, kinds of storage, and off-site copies',
                         ['Backup jobs, staff members, and restore tests', 'Days kept, weeks kept, and months kept'],
                         'Three copies of the data, on two kinds of media, one of them off-site. It does not count jobs, people, '
                         'tests or retention periods.', mc=[C321, C321])]),
            analogy('''<p>Think of keeping copies of your house deeds.</p>
<p>The original is at home, a photocopy is in a folder at home, and a third copy is with your solicitor across town —
three copies, two kinds of place, one away from home. A fire takes the first two but not the third. Keeping two
photocopies in the same drawer (RAID) does not help in a fire.</p>
<p>A full backup is copying the whole folder; an incremental copies only the pages changed since yesterday’s copy; a
differential copies everything changed since the last full copy. And you only know the solicitor’s copy is readable
when you have asked to see it.</p>''',
                    L123 + ' (house-deeds analogy written for this rung); ' + CISA_BK,
                    [check('Which restore needs the most backup sets: incremental or differential?',
                           'Incremental — the full plus every incremental since',
                           ['Differential — the full plus every differential', 'Both need exactly the same number of sets'],
                           'An incremental restore needs the last full and every incremental after it, in order; a differential '
                           'needs only the last full and the latest differential.', mc=[BTYPES, BTYPES])]),
            visual(_CHAIN + '''
<ol class="ladder-trace">
<li>Shared drive: nightly full backup to a NAS in the same room; no other copy.</li>
<li>Data owner: RPO 4 hours, RTO 1 day.</li>
<li>RPO not met (up to 24 h loss). 3-2-1 not met (one copy, same site). Restores never tested.</li>
<li>Recommend: backups every 4 hours, an off-site immutable copy, a monthly restore test in the change log.</li></ol>''',
                   L123 + ' (incremental-chain diagram and worked example “judging a backup plan”, drawn); ' + CISA_BK,
                   [check('Tuesday’s incremental is lost. Can you restore Wednesday’s state from Sunday’s full and Wednesday’s incremental?',
                          'No — the chain breaks without Tuesday',
                          ['Yes, Wednesday’s incremental holds all changes', 'Yes, as long as Monday’s incremental is present'],
                          'Each incremental holds only the changes since the previous backup, so a missing link breaks the chain. A '
                          'differential would have held everything since Sunday.', mc=[BTYPES, BTYPES])]),
            tryit('''<p>Judge a real file server’s backups in the lab: types, restore sets, 3-2-1 and RPO/RTO, showing
your working.</p>''',
                  L123 + '; ' + CISA_BK,
                  [check('How do you verify a backup works?',
                         'Restore a file elsewhere, open it, and record it',
                         ['Check that the last backup job said “Success”', 'Confirm that the backup drive is still reachable'],
                         'Only a real restore proves the backup: restore a file to another location, open it, compare date and size, '
                         'and record the test. Job reports and reachability prove nothing.', mc=[UNTESTED, UNTESTED])],
                  widget=sort('A backup on its own, or not?',
                              {'Not on its own': ['RAID 5 array', 'VM snapshot on the same storage', 'Dropbox sync'],
                               'Backup': ['Immutable off-site copy', 'Tested nightly copy to a second site']},
                              'Only a separate copy you control survives deletion and ransomware.'),
                  lab={'id': 'ops-backup', 'note': 'SR-4188: show whether the file server’s backups would actually save them.'})),

        'recovery-words': section(
            'Recovery words', 'IT-12.3',
            [check('Ransomware has encrypted a file share on a RAID 5 array. How is the data recovered?',
                   'Restore from a clean backup',
                   ['Rebuild the RAID 5 array from parity', 'Run chkdsk on the share’s volume'],
                   'RAID wrote the encrypted files to every disk, so parity holds encrypted data too. The fix is a restore from a '
                   'backup taken before the infection; chkdsk repairs file systems, not encryption.', mc=[SAMEPROT, OVERSIZE])],
            plain('''<p>Three words that sound alike but are not: backup, RAID, snapshot.</p>
<ul><li>A <strong>backup</strong> is a separate copy you can restore.</li>
<li><strong>RAID</strong> keeps working if one disk dies. It copies mistakes too.</li>
<li>A <strong>snapshot</strong> is a quick rollback point on the same storage.</li></ul>
<p>Before any step that could destroy data, ask: “When was the last backup?”</p>
<p>Ransomware on a share is fixed by a restore. RAID 5 cannot undo it.</p>''',
                  L123,
                  [check('When should you ask about the last backup?',
                         'Before any destructive step',
                         ['After the step, if data is missing', 'Only at the yearly audit'],
                         'The last-backup question comes before a wipe, a reimage or a format, while there is still time to take one. '
                         'Asking afterwards is too late.', mc=[ASKLATE, ASKLATE])]),
            analogy('''<p>Think of three ways to protect a manuscript.</p>
<p>A carbon copy made as you type (RAID) gives you a second page instantly, but if you spill ink on the original, the
carbon gets the same smudge. A bookmark you can return to (a snapshot) helps you undo the last hour, but it lives in the
same book; burn the book and the bookmark burns with it. A photocopy stored at a friend’s house (a backup) is the only one
that survives the fire. Before you tear out any pages, you check when the last photocopy was made.</p>''',
                    L123 + ' (manuscript analogy written for this rung)',
                    [check('In the manuscript story, “a carbon copy that gets the same smudge” is which technology?',
                           'RAID',
                           ['A snapshot', 'An off-site backup'],
                           'RAID mirrors or stripes every write, including mistakes and encryption, across the disks. A snapshot is a '
                           'rollback point; an off-site backup is the separate copy.', mc=[SAMEPROT, SAMEPROT])]),
            visual('''<ol class="ladder-trace">
<li>Disk failed in a RAID 1 mirror → RAID did its job; replace the disk and let it rebuild.</li>
<li>User deleted a folder an hour ago → snapshot or backup restore; RAID cannot help.</li>
<li>Ransomware encrypted the share → isolate, then restore from a clean, ideally offline, backup.</li>
<li>Before any of these destructive steps → ask “when was the last backup?”</li></ol>''',
                   L123 + ' (the three words applied to three tickets, as a worked trace)',
                   [check('A disk fails in a RAID 1 mirror and the server keeps running. What has protected it?',
                          'RAID, against a single disk failure',
                          ['The backup, by restoring the lost disk', 'A snapshot, by rolling the disk back'],
                          'Surviving a disk failure is exactly what RAID is for. It is not a backup restore or a snapshot rollback.',
                          mc=[SAMEPROT, None])]),
            tryit('''<p>On a real Linux VM, restore a deleted folder from verified backups — checking checksums, the right
version and the permissions.</p>''',
                  L123,
                  [check('A user deleted one folder this afternoon. Which recovery is in proportion?',
                         'Restore that folder from the latest good backup',
                         ['Rebuild the whole RAID array from parity data', 'Bare-metal restore of the entire server'],
                         'One deleted folder needs one targeted restore. A RAID rebuild cannot bring back a deletion, and a bare-metal '
                         'restore would roll back everyone else’s work.', mc=[OVERSIZE, OVERSIZE])],
                  widget=sort('What protects against what?',
                              {'RAID': ['One disk fails'], 'Snapshot': ['Roll back a VM after a bad update'],
                               'Backup': ['Ransomware on the share', 'Folder deleted yesterday']},
                              'Backup ≠ RAID ≠ snapshot.'),
                  lab={'id': 'linux-vm-restore', 'note': 'SR-6230: restore budget-2027 from verified backups with checksums and permissions.'})),
    },

    '12.4': {
        'core-content': section(
            'Core content', 'IT-12.4',
            [check('What changes in the old PC’s asset record at the end of the replacement capstone?',
                   'Status becomes disposed, with the sanitisation reference',
                   ['The record is deleted, because the PC no longer exists', 'Nothing changes until the next yearly asset audit'],
                   'Asset records track a device through disposal: status “disposed”, the date and the sanitisation record '
                   'reference. Deleting the record loses the evidence that the data was destroyed.', mc=[ASSETD, ASSETD])],
            plain('''<p>Good notes turn one person’s fix into the whole team’s knowledge. Three kinds matter.</p>
<ul><li>A <strong>KB article</strong> lets anyone fix a known problem the same way. Its title uses the user’s words.</li>
<li>A <strong>runbook</strong> lists the steps for a routine task, done the same way every time.</li>
<li>An <strong>asset record</strong> follows each device from purchase to disposal.</li></ul>
<p>The capstone joins the whole chapter. Replacing a reception PC needs a change request, a tested backup, a safe wipe
of the old drive, and updated asset records.</p>''',
                  L124,
                  [check('Which of these belongs in a KB article?',
                         'The symptom text, cause, steps, and how to verify',
                         ['The user’s password so the fix can be repeated', 'The names of everyone who had the problem'],
                         'A KB article holds the symptom and error text, what it applies to, cause, resolution, verification, '
                         'escalation, keywords, owner and review date — never secrets or personal data.', mc=[KBC, KBC])]),
            analogy('''<p>Think of a family recipe book.</p>
<p>A recipe card (a KB article) is titled the way people ask for it — “Grandma’s Sunday stew”, not “Recipe 14” — lists
the ingredients and steps, says how you know it is done, and says when to ask for help. The weekly routine for cleaning
the oven (a runbook) is the same steps every week. And the list of every pan in the kitchen, when it was bought and when
it was thrown out (the asset register) stops the same pan being “found” twice.</p>''',
                    L124 + ' (recipe-book analogy written for this rung)',
                    [check('In the recipe story, why is the card titled “Grandma’s Sunday stew”, not “Recipe 14”?',
                           'A KB title uses the user’s own words',
                           ['Short numbers are harder for the system to store', 'Titles must always include a person’s name'],
                           'Users and technicians search in the words they use for the problem, so a KB title in the user’s words gets '
                           'found. It is not about storage or naming people.', mc=[KBC, None])]),
            visual(_SWAP + '''
<ol class="ladder-trace">
<li>Change: a normal request — scope, risk, test, steps, backout (keep the old PC a week), window before opening, approval.</li>
<li>Backup: the receptionist’s files backed up and a restore tested on the new PC.</li>
<li>Privacy: the old drive holds visitor logs → sanitised under the disposal procedure; record attached.</li>
<li>Documentation: new asset “in use, Reception”; old asset “disposed” with the sanitisation reference; KB updated if the printer needed a trick.</li></ol>''',
                   L124 + ' (capstone diagram and the scored habits, drawn)',
                   [check('Why does the backout plan keep the old PC for a week?',
                          'So the user can switch back if something is missing',
                          ['So the old PC can be sold for a better price', 'So its warranty can be extended by the vendor'],
                          'Keeping the old PC means the user can return to it quickly if a file or setting is missing on the new one. '
                          'It is a rollback, not a sale or warranty step.', mc=[BACKOUT, None])]),
            tryit('''<p>Order the capstone steps, then sort each field to the document it belongs to.</p>''',
                  L124,
                  [check('What makes a runbook usable by another technician?',
                         'Prerequisites, numbered steps, expected results and rollback',
                         ['A summary paragraph, the author’s name and the review date', 'A list of every ticket the author closed with it'],
                         'Runbooks need purpose, prerequisites and permissions, numbered steps, expected results, rollback and a '
                         'contact. A summary or authorship details do not let someone else run it.', mc=[RUNBK, RUNBK])],
                  widget=sort('Which document holds it?',
                              {'KB article': ['Symptom and error text', 'How to verify the fix'],
                               'Runbook': ['Numbered routine steps with rollback'],
                               'Asset record': ['Serial number and warranty date', 'Status: disposed']},
                              'Each document answers a different question for the next technician.'))),

        'integrated-ticket': section(
            'Integrated ticket', 'IT-12.4',
            [check('A PC gives a memory beep code at power-on. What goes in the first line of the note?',
                   'Domain: hardware / POST',
                   ['Domain: Microsoft 365 / SaaS', 'Domain: DNS and the network'],
                   'A memory beep happens during POST, before Windows loads, so the domain is hardware. Naming it first stops the '
                   'next technician opening a network or SaaS lab.', mc=[DOMAIN, DOMAIN])],
            plain('''<p>Name the fault domain in the <em>first line</em> of the ticket note.</p>
<ul><li>A memory beep at power-on → <strong>hardware / POST</strong>.</li>
<li>Company email is down for everyone, but <code>ipconfig</code> looks good → <strong>SaaS</strong> (the cloud
service).</li></ul>
<p>Then a colleague knows where to start and does not open the wrong lab or runbook.</p>''',
                  L124,
                  [check('Mail is down for the whole tenant but ipconfig shows a good address and gateway. Which domain?',
                         'SaaS — the cloud mail service',
                         ['Hardware — the PC’s network card', 'The user’s local Windows profile'],
                         'A good local configuration and a tenant-wide outage point at the cloud service. The network card and the '
                         'profile are already ruled out by the evidence.', mc=[DOMAIN, None])]),
            analogy('''<p>Think of a hospital referral letter.</p>
<p>The first line says “cardiology” or “orthopaedics” so the letter goes to the right department straight away. A
letter that starts with three paragraphs of history and names the department at the bottom gets sent to the wrong ward
first. A ticket note is a referral letter: the first line — “Domain: hardware / POST” — sends the next technician to the
right bench, the right lab and the right runbook.</p>''',
                    L124 + ' (referral-letter analogy written for this rung)',
                    [check('In the referral story, what does “cardiology” on the first line correspond to?',
                           'The fault domain named first',
                           ['The user’s full name and phone', 'The closing time of the ticket'],
                           'The department on the first line routes the letter, just as the domain on the first line routes the '
                           'ticket. Contact details and timestamps belong in the ticket too, but they do not route it.', mc=[DOMAIN, None])]),
            visual('''<ol class="ladder-trace">
<li>Line 1: <strong>Domain: hardware / POST.</strong></li>
<li>Symptom: three short beeps at power-on, no display.</li>
<li>Evidence: the board manual lists the code as a memory error.</li>
<li>Next: reseat or swap the DIMM on the bench (a repair, documented).</li></ol>''',
                   L124 + ' (a domain-first note, as a worked example written for this rung)',
                   [check('Why does the domain come before the symptom in the note?',
                          'So a peer opens the right lab first',
                          ['Because symptoms are written last by policy', 'So the ticket title is shorter to read'],
                          'Putting the domain first sends the next person straight to the right bench, lab or runbook. The order is '
                          'about routing, not tidiness or rules.', mc=[DOMAIN, None])]),
            tryit('''<p>Practise turning a messy user sentence into an intake another shift can use, domain first.</p>''',
                  L124,
                  [check('Which first line is best for “Outlook says cannot connect, nobody in the company can get mail”?',
                         'Domain: SaaS — tenant mail outage',
                         ['User reports a problem with their computer', 'Outlook broken, please fix as soon as possible'],
                         'The domain and scope up front route it to the service owner. The other two hide the domain and invite a '
                         'PC-level repair that would not help.', mc=[DOMAIN, None])],
                  widget=sort('Which domain goes on line one?',
                              {'Hardware / POST': ['Memory beep code at power-on', 'No display, fans spin, beeps'],
                               'SaaS / cloud service': ['Tenant mail down, ipconfig good', 'Teams down for every user']},
                              'Name the domain first so a peer does not open the wrong lab.'),
                  lab={'id': 'ticket-intake', 'note': 'Turn one messy sentence into an intake another shift can use.'})),

        'teach-block-two-stories-two-domains': section(
            'Teach block — two stories, two domains', 'IT-12.4',
            [check('In the drill, what counts as the miss?',
                   'Opening the wrong lab for the story',
                   ['Taking more than five minutes to finish', 'Writing the note before running a test'],
                   'The drill gives two stories — a memory beep and a tenant mail outage — and the class picks the lab before opening '
                   'it. Picking the wrong lab is the miss, because it shows the domain was not named.', mc=[DOMAIN, DOMAIN])],
            plain('''<p>This is a class drill with two short stories.</p>
<ol><li>A PC beeps with a memory code at power-on.</li><li>Company mail is down for everyone.</li></ol>
<p>Before you open any lab, say which domain each story is in. The first is hardware. The second is a cloud service (SaaS).</p>
<p>The only way to fail is to open the wrong lab. That shows you did not name the domain first.</p>''',
                  L124,
                  [check('Why must the class pick the lab before opening it?',
                         'Picking first forces them to name the domain',
                         ['Labs can only be opened once per class', 'The instructor needs time to set them up'],
                         'Choosing the lab first makes each student commit to a domain, which is the skill being practised. It is '
                         'not about lab limits or set-up time.', mc=[DOMAIN, None])]),
            analogy('''<p>Think of a quiz where you must pick the right toolbox before you see the job.</p>
<p>One card says “the car will not start and the dashboard is dark”; the other says “the whole street has no
electricity”. Grabbing the car toolbox for the second card is the miss — no spanner fixes a power cut. The drill trains
you to read the story, say the domain, and only then reach for the tools.</p>''',
                    L124 + ' (toolbox-quiz analogy written for this rung)',
                    [check('In the toolbox story, the street-wide power cut matches which ticket story?',
                           'Tenant mail down for everyone',
                           ['Memory beep at power-on on one desk PC', 'A single PC that is slow'],
                           'An outage for everyone points to a shared service — SaaS — just as a street-wide power cut points to the '
                           'supplier. The memory beep is one machine’s hardware.', mc=[DOMAIN, None])]),
            visual('''<ol class="ladder-trace">
<li>Story 1: memory beep → say “hardware / POST” → open the hardware bench lab.</li>
<li>Story 2: tenant mail down, ipconfig good → say “SaaS” → open the service-status runbook, not a network lab.</li>
<li>Score: both labs right = pass; any wrong lab = the miss.</li></ol>''',
                   L124 + ' (the drill’s two stories, as a scored trace)',
                   [check('A student opens a DNS lab for the tenant mail story. Why is that the miss?',
                          'Good ipconfig and a tenant-wide outage point to SaaS',
                          ['DNS labs only apply to the hardware story', 'The student should have rebooted the user’s PC first'],
                          'The evidence already shows the client network works and everyone is affected, so the domain is the cloud '
                          'service. A DNS lab chases a domain the evidence ruled out.', mc=[DOMAIN, None])]),
            tryit('''<p>Pick the domain for each story before you reveal the answer — that is the drill.</p>''',
                  L124,
                  [check('Which domain fits “three short beeps, no display, fans spinning”?',
                         'Hardware / POST',
                         ['SaaS / cloud service', 'DNS'],
                         'Beeps and no display at power-on happen before the OS or network matter, so the fault is in the hardware '
                         'during POST.', mc=[DOMAIN, None])],
                  widget=reveal('Story: “Nobody can open SharePoint; my ipconfig is fine.” Which lab do you open?',
                                '<strong>SaaS</strong> — check the service status and the tenant first; a client network lab would be the miss.'))),
    },
}

STAMPS = {}

STAMPS = {   # r0_sha of the original when these rungs were written (tools/ladder_check.py --stamp)
    '12.1': {'start-here-the-shop-is-a-system': 'd3ccd1c26ac3', 'core-content': 'de75b65f5338', 'change-control': '8f65055d8c46', 'rollback-is-part-of-the-plan': '72ce64f1294d', 'change-management-procedures': '50bcf49efca0'},
    '12.2': {'core-content': '97196072b037', 'privacy': 'f4a534996782', 'ai-tools-at-work-policy-limitations-and-private-vs-public': 'c070e9ce170a', 'incident-handling-licensing-and-regulated-data': 'e72ee5e5e330'},
    '12.3': {'core-content': 'b9c91ab2331b', 'recovery-words': '5c7cd1875b96'},
    '12.4': {'core-content': '130e0c606c59', 'integrated-ticket': '6c82d5a3b9e4', 'teach-block-two-stories-two-domains': 'a38095d9a668'},
}
