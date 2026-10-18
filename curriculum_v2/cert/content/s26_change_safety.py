"""A+ Core 2 4.2 (change management) — ITSUP 12.1; 4.4 (safety procedures) — ITSUP 1.2.  Round 2 of pass 11."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_CHG = figure(
    'fig-c-change', 'The change management path',
    ['Request form:\npurpose, scope,\ntype, window', 'Risk analysis:\nimpact, affected\nsystems, risk level', 'Plan:\nsandbox test,\nbackup, rollback', 'Approval:\nchange board\n(CAB)', 'Implement:\nresponsible staff,\npeer review', 'Close:\nend-user acceptance,\ndocument'],
    'Six boxes left to right. A change starts as a request form stating its purpose, scope, change type and proposed date, time '
    'and maintenance window, outside any change freeze. Risk analysis names the affected systems, the impact and a risk level. The '
    'plan is tested in a sandbox and includes a backup plan and a rollback plan. The change board approves it. A named responsible '
    'staff member implements it, with peer review. The change closes only after end-user acceptance, and the documented business '
    'process is updated.',
    'No approval without a tested rollback; no closure without user acceptance.', cols=3)

HTML_CHG = f'''
<p>A+ Core 2 4.2 asks you to apply change management (ITIL 4 calls this <em>change enablement</em>; NIST SP 800-128 covers it as
configuration change control).</p>
<ul>
<li><strong>Documented business processes</strong> — the written procedure the change follows and the process it may alter.</li>
<li><strong>Request form</strong> — states the <strong>purpose</strong> (why), the <strong>scope</strong> (what is and is not included), the
<strong>change type</strong>, and the <strong>date and time</strong>.</li>
<li><strong>Change types</strong> — <em>standard</em> (pre-approved, low risk, routine), <em>normal</em> (assessed and approved by the change
authority or board) and <em>emergency</em> (urgent, expedited approval, documented afterwards).</li>
<li><strong>Maintenance window</strong> — the agreed time when changes may be made; a <strong>change freeze</strong> is a period
(for example year-end) when only emergency changes are allowed.</li>
<li><strong>Risk analysis</strong> — <strong>affected systems</strong>, <strong>impact</strong> and a <strong>risk level</strong>.</li>
<li><strong>Sandbox testing</strong> — try the change in an isolated test environment first.</li>
<li><strong>Backup plan</strong> (protect the data first) and <strong>rollback plan</strong> (how to return to the last known-good state if it fails).</li>
<li><strong>Change board approvals</strong> — the change advisory board (CAB) or change authority approves normal changes.</li>
<li><strong>Responsible staff member</strong> — one named implementer and owner; <strong>peer review</strong> checks the work.</li>
<li><strong>End-user acceptance</strong> — the users confirm the change works before it is closed.</li>
</ul>
{_FIG_CHG}
{worked('a firmware update on the office firewall', '''<ol>
<li>Request: purpose (fixes a published vulnerability), scope (one firewall, no rule changes), type normal, window Saturday 06:00–08:00.</li>
<li>Risk: internet and VPN for all 40 staff are affected; risk medium.</li>
<li>Plan: test the firmware on the lab firewall (sandbox); back up the running configuration; rollback = reload the previous image and config.</li>
<li>CAB approves on Thursday. A named technician implements; a colleague peer-reviews the config backup and the steps.</li>
<li>After the update, staff at two sites confirm VPN and web access (end-user acceptance); the change record is closed.</li></ol>''')}
{scenario('the Friday-afternoon change', '''<p>A technician pushes a new Group Policy on Friday afternoon without a request or test. Printing breaks in three
offices and nobody knows what changed. Because there is no rollback plan, it takes hours to work out the old settings. The team
now requires a request form with scope and risk, testing in a sandbox OU, a rollback plan, CAB approval and a maintenance window
for every normal change, with standard changes listed and pre-approved.</p>''')}
{cfu(('What is the difference between a standard and a normal change?', 'A standard change is pre-approved and routine; a normal change is assessed and approved by the change board.'),
     ('What is a rollback plan?', 'The tested steps to return to the last known-good state if the change fails.'),
     ('When is a change closed?', 'After implementation, end-user acceptance and documentation.'))}
'''

_FIG_SAFE = figure(
    'fig-c-safety', 'Safety before, during and after the job',
    ['Before:\ndisconnect power,\nremove jewellery', 'Body:\nESD strap and mat,\ngoggles, mask', 'Handling:\nby the edges,\nantistatic bags', 'Workplace:\ncable management,\nlift with legs', 'Fire:\nright extinguisher\nclass', 'Rules:\ngovernment\nregulations'],
    'Six boxes. Before work, power off, unplug the device and remove jewellery. Wear an ESD wrist strap connected to a grounded ESD '
    'mat, with safety goggles and an air filter mask when using compressed air or handling toner. Hold components by the edges and '
    'store them in antistatic bags. Keep cables managed to avoid trip hazards and lift with your legs, keeping the load close and '
    'getting help with heavy items. Know which extinguisher to use on an electrical fire, and follow government regulations such as '
    'OSHA rules on workplace safety.',
    'Protect yourself first, then the equipment.', cols=3)

HTML_SAFE = f'''
<p>A+ Core 2 4.4 asks you to use common safety procedures.</p>
<ul>
<li><strong>Disconnect power</strong> — shut down and unplug before opening a device; never open a power supply or a monitor’s
high-voltage section (replace the unit instead).</li>
<li><strong>ESD straps and ESD mats</strong> — a wrist strap with a built-in resistor connected to a grounded mat keeps you and the parts at the
same potential (ANSI/ESD S20.20). <strong>Antistatic bags</strong> store and carry components; hold boards by the edges.</li>
<li><strong>Equipment grounding</strong> — use grounded outlets and never remove the ground pin from a plug.</li>
<li><strong>Personal protection</strong> — <strong>safety goggles</strong> when using compressed air, cutting cable or working with batteries;
an <strong>air filter mask</strong> for toner and heavy dust.</li>
<li><strong>Cable management</strong> — route cables under covers or along walls so nobody trips; keep walkways clear.</li>
<li><strong>Lifting techniques</strong> — plan the lift, bend at the knees with a straight back, keep the load close and do not twist; use a
team lift or a cart for heavy loads. The NIOSH lifting equation starts from 23 kg (51 lb) as the most anyone should lift under ideal
conditions, and less for awkward lifts.</li>
<li><strong>Fire safety</strong> — in the U.S. (NFPA 10) class A is ordinary combustibles, B flammable liquids, C energised electrical equipment,
D metals and K cooking oils. Use a CO<sub>2</sub> or clean-agent extinguisher on electrical fires, never water. Know the exits.</li>
<li><strong>Government regulations</strong> — follow workplace safety law (OSHA in the U.S.) and local rules; they override convenience.</li>
</ul>
{_FIG_SAFE}
{worked('replacing a failed laser printer fuser', '''<ol>
<li>Turn the printer off, unplug it and let the fuser cool; it runs at about 200 °C.</li>
<li>Wear an air filter mask and gloves because loose toner is inside; use a toner vacuum, not compressed air.</li>
<li>The printer weighs 30 kg: two people lift it onto the bench with bent knees and the load held close.</li>
<li>Fit the new fuser, route the power cable away from the walkway, test print, and record the job.</li></ol>''')}
{scenario('smoke from a power strip', '''<p>A user reports smoke from a power strip under a desk. The technician does not reach in. They switch off power at the
breaker if it is safe to do so, move people away, and if flames appear use a CO<sub>2</sub> (class C in the U.S.) extinguisher — never
water on live electrical equipment. Afterwards the strip is replaced, the daisy-chained strips are removed, and the incident is
reported under the site’s safety policy.</p>''')}
{cfu(('Which extinguisher type is used on an electrical fire?', 'CO2 or clean agent (class C in the U.S.); never water.'),
     ('Why should you never open a power supply?', 'Its capacitors can hold a dangerous charge even when it is unplugged.'),
     ('When should you wear an air filter mask?', 'When cleaning toner or heavy dust.'))}
'''

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 12, 'lesson': 1, 'id': 'cert-change-mgmt', 'title': 'Change management procedures',
     'cert': ['A2:4.2'], 'html': sme_note('Change management procedures (A+ Core 2 4.2).') + HTML_CHG,
     'sources': ['itil4-change', 'nist-800128']},
    {'course': 'ITSUP', 'chapter': 1, 'lesson': 2, 'id': 'cert-safety', 'title': 'Common safety procedures',
     'cert': ['A2:4.4'], 'html': sme_note('Common safety procedures (A+ Core 2 4.4).') + HTML_SAFE,
     'sources': ['esda-s2020', 'osha-lift', 'nfpa10']},
]

GLOSSARY = [
    ('Change advisory board (CAB)', 'Group that assesses and approves normal changes.'),
    ('Standard change', 'Pre-approved, low-risk, routine change.'),
    ('Emergency change', 'Urgent change with expedited approval, documented afterwards.'),
    ('Rollback plan', 'Tested steps to return to the last known-good state if a change fails.'),
    ('Change freeze', 'Period when only emergency changes are allowed.'),
    ('End-user acceptance', 'Users confirm a change works before it is closed.'),
    ('Class C fire', 'U.S. class for fires involving energised electrical equipment.'),
    ('Antistatic bag', 'Shielding bag for storing and carrying static-sensitive components.'),
]

MISCONCEPTIONS = {
    'MC-C-IT12-SKIP-ROLLBACK': {'obj': 'IT-12.1', 'label': 'Approving or implementing a change without a tested rollback plan',
                                'fix': 'Every normal change needs a tested rollback plan before approval.', 'terms': ['rollback', 'back out', 'known-good', 'change']},
    'MC-C-IT12-CHANGE-TYPE': {'obj': 'IT-12.1', 'label': 'Mixing up standard, normal and emergency changes',
                              'fix': 'Standard is pre-approved routine work; normal goes to the board; emergency is expedited.', 'terms': ['standard change', 'normal change', 'emergency change', 'cab']},
    'MC-C-IT12-CLOSE-ON-IMPLEMENT': {'obj': 'IT-12.1', 'label': 'Closing a change as soon as it is implemented, before users accept it',
                                     'fix': 'A change closes after end-user acceptance and documentation.', 'terms': ['acceptance', 'sign-off', 'close', 'document']},
    'MC-C-IT12-TEST-IN-PROD': {'obj': 'IT-12.1', 'label': 'Testing a change in production instead of a sandbox',
                               'fix': 'Test in an isolated sandbox first.', 'terms': ['sandbox', 'test', 'production']},
    'MC-C-IT1-WATER-ON-ELECTRICAL': {'obj': 'IT-1.2', 'label': 'Using water or the wrong extinguisher class on an electrical fire',
                                     'fix': 'Use CO2 or clean agent (class C in the U.S.) on electrical fires.', 'terms': ['extinguisher', 'fire', 'co2', 'class c']},
    'MC-C-IT1-OPEN-PSU': {'obj': 'IT-1.2', 'label': 'Opening a power supply or high-voltage part to repair it',
                          'fix': 'Capacitors hold charge; replace the unit, never open it.', 'terms': ['power supply', 'capacitor', 'replace', 'unplug']},
    'MC-C-IT1-PPE-MISMATCH': {'obj': 'IT-1.2', 'label': 'Choosing protection that does not match the hazard',
                              'fix': 'Goggles for compressed air and cutting; air filter mask for toner and dust; ESD strap for components.', 'terms': ['goggles', 'mask', 'toner', 'esd strap']},
    'MC-C-IT1-LIFT-BACK': {'obj': 'IT-1.2', 'label': 'Lifting with the back or alone when the load needs a team or a cart',
                           'fix': 'Bend the knees, keep the load close, do not twist; team lift heavy items.', 'terms': ['lift', 'knees', 'team lift', 'heavy']},
}

ITEMS = [
    order('A2:4.2', 'IT-12.1', 11, 'Put these change management steps in order.',
          ['Submit a request form with purpose, scope and window', 'Analyse risk and affected systems', 'Test in a sandbox and write the rollback plan',
           'Obtain change board approval', 'Implement and peer-review', 'Confirm end-user acceptance and close'],
          'Request, assess, plan and test, approve, implement, accept (ITIL 4 change enablement).'),
    single('A2:4.2', 'IT-12.1', 12, 'A firmware update fails halfway through the maintenance window. What should the technician follow?',
           'The rollback plan in the approved change', ['The sandbox test results from last week', 'The change freeze calendar',
            'The end-user acceptance form'],
           'The rollback plan returns the system to its last known-good state.',
           mc=['MC-C-IT12-SKIP-ROLLBACK', None, 'MC-C-IT12-CLOSE-ON-IMPLEMENT']),
    match('A2:4.2', 'IT-12.1', 13, 'Match each change to its type.',
          [('Replacing a user’s toner cartridge from the approved list', 'Standard change'),
           ('Upgrading the email server to a new version next month', 'Normal change'),
           ('Patching an actively exploited firewall flaw tonight', 'Emergency change')],
          'Standard = pre-approved routine; normal = board approval; emergency = expedited.', decoys=['Change freeze']),
    single('A2:4.2', 'IT-12.1', 14, 'The CAB will not approve a database upgrade. Which missing item is the most likely reason?',
           'A tested rollback plan', ['A longer maintenance window than requested', 'A list of the users who will be emailed', 'The vendor’s release announcement'],
           'Boards approve normal changes only when risk is analysed and a rollback exists.',
           mc=[None, None, None]),
    multi('A2:4.4', 'IT-1.2', 11, 'A technician will clean dust out of a desktop with compressed air. Which TWO precautions apply? (Choose two.)',
          ['Power off and unplug the PC first', 'Wear safety goggles'],
          ['Use a water extinguisher nearby', 'Open the power supply to blow it out', 'Hold the fans spinning with the air jet'],
          'Unplug first and protect your eyes; never open the PSU, and stop the fans spinning freely.',
          mc=['MC-C-IT1-WATER-ON-ELECTRICAL', 'MC-C-IT1-OPEN-PSU', None]),
    single('A2:4.4', 'IT-1.2', 12, 'A power strip under a desk catches fire. Which extinguisher should be used?',
           'CO2 or clean agent (class C in the U.S.)', ['Water (class A)', 'Wet chemical (class K)', 'Dry powder for metals (class D)'],
           'Electrical fires need a non-conductive agent; water conducts.',
           mc=['MC-C-IT1-WATER-ON-ELECTRICAL', 'MC-C-IT1-WATER-ON-ELECTRICAL', 'MC-C-IT1-WATER-ON-ELECTRICAL']),
    match('A2:4.4', 'IT-1.2', 13, 'Match each hazard to the protection.',
          [('Loose toner during a printer clean', 'Air filter mask'), ('Compressed air blowing dust', 'Safety goggles'),
           ('Static while fitting RAM', 'ESD strap and mat'), ('A 30 kg printer to move', 'Team lift')],
          'A+ Core 2 4.4 safety procedures.', decoys=['Remove the ground pin']),
    single('A2:4.4', 'IT-1.2', 14, 'A PC power supply has failed. What is the safe action?',
           'Replace the whole power supply unit', ['Open it and replace the failed capacitor', 'Open it after unplugging for a minute',
            'Bypass its fuse with a wire'],
           'Capacitors in a PSU can hold a dangerous charge; PSUs are replaced, not repaired in the field.',
           mc=['MC-C-IT1-OPEN-PSU', 'MC-C-IT1-OPEN-PSU', None]),
    single('A2:4.4', 'IT-1.2', 15, 'Which lifting technique is correct for a heavy UPS?',
           'Bend at the knees, keep it close, and get help if it is heavy', ['Bend at the waist and lift quickly to save time',
            'Twist while lifting to put it straight on the shelf', 'Hold it at arm’s length to keep it off your clothes'],
           'Lift with the legs, keep the load close, do not twist; team lift heavy items.',
           mc=['MC-C-IT1-LIFT-BACK', 'MC-C-IT1-LIFT-BACK', 'MC-C-IT1-LIFT-BACK']),
]
